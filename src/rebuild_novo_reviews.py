#!/usr/bin/env python3
"""Rebuild NOVO review fields from the original review export.

Default: validate every call JSON and print a dry-run summary (no writes).

    python3 src/rebuild_novo_reviews.py
    python3 src/rebuild_novo_reviews.py --output-dir /path/to/new/call-files
    python3 src/rebuild_novo_reviews.py --write

Each proposal receives two collections, independently grouped by reviewer_id:

    reviews: [{reviewer_id, reviewer_full_name, assessments: [source rows]}]
    recommendation: [{reviewer_id, reviewer_full_name,
                      recommendations: [source rows]}]

Only Assessment rows retain the field "assessor_comment". Recommendation and
Interview recommendation rows rename that field to "comment", preserving the
original activity_type. All other CSV fields and all versions remain intact,
including original names at record level if a reviewer's name varies. CSV values
remain strings. Source order is retained, but is not interpreted as chronology.

Recommendation-only reviewers occur only in "recommendation". A person with both
roles appears once in each collection and can be linked using reviewer_id.
No versions are selected, deduplicated, or treated as independent reviewers.
Existing flat reviews are replaced, not appended to. Repeated runs are idempotent.

Other proposal/call fields, including mean_score and within_call_pct, are left
unchanged. Those existing aggregates are NOT assessment-only scores; recompute
analysis scores only after defining which assessment version/stage to use.

--write backs up every changed input before replacing files atomically. The
audit report records source hash, counts, and backup location. --output-dir
writes copies into a new directory and leaves the originals untouched.
"""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import csv
import os
import shutil
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "NOVO-data"
ACTIVITIES = {"Assessment", "Recommendation", "Interview recommendation"}
REQUIRED_COLUMNS = {
    "proposal_id", "review_id", "reviewer_id", "reviewer_full_name",
    "activity_type", "activity_status", "assessment_score", "assessor_comment",
}


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def load_reviews(path):
    """Validate the source before any output is written. Do not guess IDs/types."""
    indexed = defaultdict(list)
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed CSV row at line {line}")
            for key in ("proposal_id", "review_id", "reviewer_id"):
                if not row[key].strip():
                    raise ValueError(f"Blank {key} at CSV line {line}")
            if row["activity_type"] not in ACTIVITIES:
                raise ValueError(f"Unknown activity_type at CSV line {line}: "
                                 f"{row['activity_type']!r}")
            if row["review_id"] in seen:
                raise ValueError(f"Duplicate source review_id at CSV line {line}")
            seen.add(row["review_id"])
            indexed[row["proposal_id"]].append(row)
    return indexed


def group_records(rows, assessment):
    groups = {}
    field = "assessments" if assessment else "recommendations"
    for row in rows:
        if (row["activity_type"] == "Assessment") != assessment:
            continue
        reviewer = row["reviewer_id"]
        if reviewer not in groups:
            groups[reviewer] = {
                "reviewer_id": reviewer,
                "reviewer_full_name": row["reviewer_full_name"],
                field: [],
            }
        record = dict(row)
        if not assessment:
            record["comment"] = record.pop("assessor_comment")
        groups[reviewer][field].append(record)
    return list(groups.values())


def rebuild_document(document, indexed):
    """Return an updated document and counts without changing the argument."""
    if not isinstance(document, dict) or not isinstance(document.get("proposals"), list):
        raise ValueError("Expected a call object containing a proposals list")
    result = dict(document)
    result["proposals"] = []
    counts = Counter()
    for proposal in document["proposals"]:
        pid = str(proposal.get("_id", ""))
        if not pid:
            raise ValueError("Proposal missing _id")
        source_id = proposal.get("Application source record id")
        if source_id not in (None, "") and str(source_id) != pid:
            raise ValueError(f"Conflicting proposal identifiers for {pid}")
        rows = indexed.get(pid, [])
        updated = dict(proposal)
        updated["reviews"] = group_records(rows, assessment=True)
        updated["recommendation"] = group_records(rows, assessment=False)
        result["proposals"].append(updated)
        counts["proposals"] += 1
        counts["source_records_attached"] += len(rows)
        counts["assessment_reviewer_groups"] += len(updated["reviews"])
        counts["recommendation_reviewer_groups"] += len(updated["recommendation"])
        counts["proposals_without_assessments"] += not bool(updated["reviews"])
        counts["proposals_without_source_records"] += not bool(rows)
        counts["assessment_groups_with_multiple_versions"] += sum(
            len(group["assessments"]) > 1 for group in updated["reviews"]
        )
        for row in rows:
            counts[row["activity_type"]] += 1
    return result, counts


def encode(document):
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path, payload):
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        if path.exists():
            shutil.copymode(path, temporary)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run(proposals_dir, reviews_csv, *, write=False, output_dir=None):
    proposals_dir, reviews_csv = proposals_dir.resolve(), reviews_csv.resolve()
    if write and output_dir is not None:
        raise ValueError("Choose --write or --output-dir, not both")
    if output_dir is not None:
        output_dir = output_dir.resolve()
        if output_dir.exists():
            raise ValueError("--output-dir must be a new directory")
        if output_dir.is_relative_to(proposals_dir):
            raise ValueError("--output-dir must be outside the source proposals directory")
    files = sorted(proposals_dir.glob("*.json"))
    if not files:
        raise ValueError(f"No call JSON files found in {proposals_dir}")
    source_hash = sha256(reviews_csv.read_bytes())
    indexed = load_reviews(reviews_csv)
    seen_proposals = set()
    totals = Counter()
    plan = []
    # Preflight the entire input before creating directories or modifying files.
    for path in files:
        raw = path.read_bytes()
        document = json.loads(raw)
        rebuilt, counts = rebuild_document(document, indexed)
        for proposal in document["proposals"]:
            pid = str(proposal["_id"])
            if pid in seen_proposals:
                raise ValueError(f"Proposal {pid} occurs more than once in input files")
            seen_proposals.add(pid)
        totals.update(counts)
        plan.append({"file": path.name, "input_sha256": sha256(raw),
                     "changed": document != rebuilt})
    if sha256(reviews_csv.read_bytes()) != source_hash:
        raise RuntimeError("Source CSV changed during validation; rerun")
    report = {
        "mode": "in_place" if write else "copies" if output_dir else "dry_run",
        "proposals_dir": str(proposals_dir), "reviews_csv": str(reviews_csv),
        "reviews_csv_sha256": source_hash,
        "call_files": len(files), "files_needing_update": sum(p["changed"] for p in plan),
        **dict(totals),
        "source_records_outside_input_proposals": sum(
            len(rows) for pid, rows in indexed.items() if pid not in seen_proposals
        ),
        "score_policy": "Source scores preserved per version; proposal aggregates unchanged.",
        "version_policy": "All Assessment versions retained, grouped by stable reviewer_id.",
    }
    if not write and output_dir is None:
        return report

    # Verify originals again; a backup precedes every in-place mutation.
    for item in plan:
        if sha256((proposals_dir / item["file"]).read_bytes()) != item["input_sha256"]:
            raise RuntimeError(f"Input changed during validation: {item['file']}")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if write:
        audit_dir = proposals_dir.parent / "review-rebuild-backups" / run_id
        audit_dir.mkdir(parents=True, exist_ok=False)
        for item in plan:
            if item["changed"]:
                shutil.copy2(proposals_dir / item["file"], audit_dir / item["file"])
        report["backup_dir"] = str(audit_dir)
        destination = proposals_dir
    else:
        output_dir.mkdir(parents=True, exist_ok=False)
        destination = output_dir
        audit_dir = output_dir / "_audit"
        audit_dir.mkdir()
        report["output_dir"] = str(output_dir)
    report["files"] = plan
    report["completed_files"] = []
    audit_path = audit_dir / "review_rebuild_audit.json"
    report["status"] = "in_progress"
    atomic_write(audit_path, encode(report))
    try:
        for item in plan:
            if write and not item["changed"]:
                continue
            source = proposals_dir / item["file"]
            raw = source.read_bytes()
            if sha256(raw) != item["input_sha256"]:
                raise RuntimeError(f"Input changed before write: {source.name}")
            rebuilt, _ = rebuild_document(json.loads(raw), indexed)
            payload = encode(rebuilt)
            if sha256(source.read_bytes()) != item["input_sha256"]:
                raise RuntimeError(f"Input changed while rebuilding: {source.name}")
            atomic_write(destination / source.name, payload)
            item["output_sha256"] = sha256(payload)
            report["completed_files"].append(source.name)
        report["status"] = "complete"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        atomic_write(audit_path, encode(report))
    return {k: v for k, v in report.items() if k not in {"files", "completed_files"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--proposals-dir", type=Path, default=DATA_ROOT / "proposals")
    parser.add_argument("--reviews-csv", type=Path,
                        default=DATA_ROOT / "original" / "reviews_extended.csv")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Update originals with backups")
    mode.add_argument("--output-dir", type=Path, help="Write copies to a new directory")
    args = parser.parse_args()
    try:
        report = run(args.proposals_dir, args.reviews_csv,
                     write=args.write, output_dir=args.output_dir)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
