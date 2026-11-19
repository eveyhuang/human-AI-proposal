"""Tests for lossless activity separation and safe NOVO review rebuilding."""

import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "rebuild_novo_reviews", Path(__file__).resolve().parents[1] / "src" / "rebuild_novo_reviews.py"
)
rebuild = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rebuild)


def row(review_id, reviewer="person-1", kind="Assessment", status="Complete", score="1.0"):
    return {
        "proposal_id": "proposal-1", "review_id": review_id,
        "reviewer_id": reviewer, "reviewer_full_name": "Reviewer",
        "activity_type": kind, "activity_status": status,
        "assessment_score": score, "assessor_comment": "Identical text\nwith a newline.",
        "conflict_of_interest": "",
    }


class ReviewRebuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.inputs = self.root / "proposals"
        self.inputs.mkdir()
        self.input_path = self.inputs / "call.json"
        self.document = {"call": {"call_id": "call-1"}, "proposals": [{
            "_id": "proposal-1", "Application source record id": "proposal-1",
            "proposal_text": "Preserve this scientific text.", "mean_score": "2.5",
            "reviews": [{"review_id": "old-flat-record"}],
        }]}
        self.input_path.write_text(json.dumps(self.document))
        self.original = self.input_path.read_bytes()
        self.csv_path = self.root / "reviews.csv"
        self.rows = [
            row("a1", status="Historic", score="2.0"),
            row("a2"),
            row("a3", reviewer="person-2"),
            row("r1", kind="Recommendation"),
            row("i1", kind="Interview recommendation"),
            row("r2", reviewer="person-3", kind="Recommendation"),
        ]
        self.save_csv(self.rows)

    def save_csv(self, rows):
        with self.csv_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_grouping_preserves_versions_people_and_every_source_field(self):
        result, counts = rebuild.rebuild_document(self.document, rebuild.load_reviews(self.csv_path))
        p = result["proposals"][0]
        self.assertEqual(len(p["reviews"]), 2)
        self.assertEqual([r["review_id"] for r in p["reviews"][0]["assessments"]], ["a1", "a2"])
        self.assertEqual(len(p["recommendation"]), 2)
        self.assertEqual([r["activity_type"] for r in p["recommendation"][0]["recommendations"]],
                         ["Recommendation", "Interview recommendation"])
        recovered = []
        for group in p["reviews"]:
            recovered.extend(group["assessments"])
        for group in p["recommendation"]:
            for record in group["recommendations"]:
                self.assertNotIn("assessor_comment", record)
                restored = dict(record)
                restored["assessor_comment"] = restored.pop("comment")
                recovered.append(restored)
        self.assertEqual({r["review_id"]: r for r in recovered},
                         {r["review_id"]: r for r in self.rows})
        self.assertEqual(p["mean_score"], "2.5")
        self.assertEqual(p["proposal_text"], self.document["proposals"][0]["proposal_text"])
        self.assertEqual(self.document["proposals"][0]["reviews"], [{"review_id": "old-flat-record"}])
        self.assertEqual(counts["source_records_attached"], 6)
        self.assertEqual(counts["assessment_groups_with_multiple_versions"], 1)

    def test_dry_run_does_not_change_or_create_files(self):
        before = sorted(str(p) for p in self.root.rglob("*"))
        report = rebuild.run(self.inputs, self.csv_path)
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["Assessment"], 3)
        self.assertEqual(self.input_path.read_bytes(), self.original)
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))

    def test_output_copies_leave_originals_intact_and_have_audit(self):
        out = self.root / "output"
        report = rebuild.run(self.inputs, self.csv_path, output_dir=out)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(self.input_path.read_bytes(), self.original)
        self.assertTrue((out / "_audit" / "review_rebuild_audit.json").exists())
        self.assertEqual(rebuild.run(out, self.csv_path)["files_needing_update"], 0)
        with self.assertRaises(ValueError):
            rebuild.run(self.inputs, self.csv_path, output_dir=out)

    def test_in_place_backup_and_idempotence(self):
        report = rebuild.run(self.inputs, self.csv_path, write=True)
        backup = Path(report["backup_dir"])
        self.assertEqual((backup / "call.json").read_bytes(), self.original)
        self.assertEqual(rebuild.run(self.inputs, self.csv_path)["files_needing_update"], 0)

    def test_invalid_source_fails_before_writing(self):
        for rows in [self.rows + [self.rows[0]], [row("x", kind="Unknown")], [row("x", reviewer="")]]:
            with self.subTest(rows=rows):
                self.save_csv(rows)
                out = self.root / "never-created"
                with self.assertRaises(ValueError):
                    rebuild.run(self.inputs, self.csv_path, output_dir=out)
                self.assertFalse(out.exists())
                self.assertEqual(self.input_path.read_bytes(), self.original)

    def test_duplicate_proposals_fail_before_writing(self):
        (self.inputs / "another.json").write_bytes(self.original)
        with self.assertRaises(ValueError):
            rebuild.run(self.inputs, self.csv_path, write=True)
        self.assertFalse((self.root / "review-rebuild-backups").exists())


if __name__ == "__main__":
    unittest.main()
