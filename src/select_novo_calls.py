"""Select NOVO calls using assessment reviewers and report instrument counts.

Run after rebuilding reviews: python3 src/select_novo_calls.py
Only call_selection.csv is updated; source call/proposal JSON files are read-only.
All assessment versions are checked for blank comments. Matching nonblank
comments across distinct reviewers cause exclusion; repeated versions belonging
to one reviewer do not. Recommendation records are not used.
"""

import csv
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "data" / "NOVO-data"
HEADERS = [
    "call_id", "Instrument type", "call_grant_year", "number_of_proposals",
    "has_proposals_with_less_than_2_reviews",
    "has_proposals_with_no_assessor_comments",
    "has_proposals_with_blank_assessor_comments",
    "has_proposals_with_duplicate_assessor_comments", "include",
]


def normalize(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("Assessment comments must be strings or null")
    return " ".join(unicodedata.normalize("NFC", value).split())


def proposal_flags(proposal):
    reviewers = {}
    for group in proposal["reviews"]:
        reviewer_id = group["reviewer_id"]
        if not reviewer_id or reviewer_id in reviewers:
            raise ValueError(f"Missing or duplicate reviewer group: {proposal['_id']}")
        assessments = group["assessments"]
        if not assessments:
            raise ValueError(f"Empty assessment group: {proposal['_id']}")
        for row in assessments:
            if row["activity_type"] != "Assessment" or row["reviewer_id"] != reviewer_id:
                raise ValueError(f"Invalid assessment membership: {proposal['_id']}")
        reviewers[reviewer_id] = [normalize(a["assessor_comment"]) for a in assessments]
    comments = [c for values in reviewers.values() for c in values]
    owners = defaultdict(set)
    for reviewer_id, values in reviewers.items():
        for comment in values:
            if comment:
                owners[comment].add(reviewer_id)
    return (
        len(reviewers) < 2,
        not any(comments),
        not comments or any(not c for c in comments),
        any(len(ids) > 1 for ids in owners.values()),
    )


def run(base=BASE):
    rows = []
    distribution = Counter()
    type_calls = defaultdict(set)
    call_ids, proposal_ids = set(), set()
    mixed_calls = 0
    files = sorted((base / "proposals").glob("*.json"))
    files += sorted((base / "included-round1").glob("*.json"))
    files += sorted((base / "included-research_projects").glob("*.json"))
    if not files:
        raise ValueError("No call files found")
    for path in files:
        document = json.loads(path.read_text(encoding="utf-8"))
        call = document["call"]
        cid = call["call_id"]
        if cid in call_ids:
            raise ValueError(f"Call occurs in multiple files: {cid}")
        call_ids.add(cid)
        proposals = document["proposals"]
        types = list(dict.fromkeys(p["Instrument type"] for p in proposals))
        flags = [False] * 4
        for proposal in proposals:
            pid = proposal["_id"]
            if pid in proposal_ids or proposal["call_id"] != cid:
                raise ValueError(f"Duplicate or mismatched proposal: {pid}")
            proposal_ids.add(pid)
            flags = [a or b for a, b in zip(flags, proposal_flags(proposal))]
        include = len(proposals) >= 10 and not any(flags)
        rows.append(dict(zip(HEADERS, [
            cid, "; ".join(types), call["call_grant_year"], len(proposals),
            *flags, include,
        ])))
        if include:
            mixed_calls += len(types) > 1
            for proposal in proposals:
                kind = proposal["Instrument type"] or "Missing instrument type"
                distribution[kind] += 1
                type_calls[kind].add(cid)
    destination = base / "call_selection.csv"
    temporary = destination.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    with temporary.open(encoding="utf-8", newline="") as handle:
        saved = list(csv.DictReader(handle))
    assert saved == [{k: str(v) for k, v in row.items()} for row in rows]
    temporary.replace(destination)
    eligible = [r for r in rows if r["include"]]
    total = sum(r["number_of_proposals"] for r in eligible)
    assert total == sum(distribution.values())
    return {
        "calls_checked": len(rows), "proposals_checked": len(proposal_ids),
        "included_calls": len(eligible), "included_proposals": total,
        "mixed_type_included_calls": mixed_calls,
        "distribution": [
            {"instrument_type": kind, "calls": len(type_calls[kind]),
             "proposals": count, "proposal_percent": round(100 * count / total, 1)}
            for kind, count in distribution.most_common()
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
