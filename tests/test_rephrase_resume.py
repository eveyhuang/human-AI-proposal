import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rephrase_pipeline import (
    _carry_over_successful_rows,
    _proposal_rephrase_prompt_compatible,
    _proposal_rephrase_prompt_matches,
    _review_rephrase_prompt_compatible,
    _review_rephrase_prompt_matches,
)

V2 = "review_neutralization_v2"


def _partial_review_frame(n_success=244, n_pending=100, n_failed=1):
    """Mimic an interrupted per-row resume file: some rows processed, some untouched."""
    rows = []
    for i in range(n_success):
        rows.append({"review_uid": f"ok-{i}", "review_rephrase_status": "success",
                     "review_rephrase_prompt_version": V2, "rephrased_review": "x"})
    for i in range(n_failed):
        rows.append({"review_uid": f"fail-{i}", "review_rephrase_status": "failed",
                     "review_rephrase_prompt_version": V2, "rephrased_review": ""})
    for i in range(n_pending):
        # untouched rows: status + prompt version left blank by the initializer
        rows.append({"review_uid": f"todo-{i}", "review_rephrase_status": "",
                     "review_rephrase_prompt_version": "", "rephrased_review": ""})
    return pd.DataFrame(rows)


class ReviewResumeGateTests(unittest.TestCase):
    def test_strict_match_rejects_partial_file(self):
        # Documents the root cause: the strict gate refuses any unfinished run.
        partial = _partial_review_frame()
        self.assertFalse(_review_rephrase_prompt_matches(partial, V2))

    def test_compatible_gate_accepts_partial_file(self):
        partial = _partial_review_frame()
        self.assertTrue(_review_rephrase_prompt_compatible(partial, V2))

    def test_compatible_gate_rejects_stale_prompt_version(self):
        # A processed row from a different prompt version must NOT be resumed.
        partial = _partial_review_frame(n_success=3, n_pending=2, n_failed=0)
        partial.loc[0, "review_rephrase_prompt_version"] = "review_neutralization_v1"
        self.assertFalse(_review_rephrase_prompt_compatible(partial, V2))

    def test_compatible_gate_rejects_fully_blank_file(self):
        partial = _partial_review_frame(n_success=0, n_pending=5, n_failed=0)
        self.assertFalse(_review_rephrase_prompt_compatible(partial, V2))

    def test_partial_resume_carries_over_successful_rows(self):
        partial = _partial_review_frame()  # 244 success, 1 failed, 100 pending
        # Fresh out_df spanning every review_uid, all status blank (as in the real code path).
        out_df = pd.DataFrame({"review_uid": partial["review_uid"].tolist()})
        columns = ["review_rephrase_status", "review_rephrase_prompt_version", "rephrased_review"]
        for col in columns:
            out_df[col] = ""

        resume_df = partial if _review_rephrase_prompt_compatible(partial, V2) else None
        _carry_over_successful_rows(
            out_df, resume_df,
            key_col="review_uid", status_col="review_rephrase_status", columns=columns,
        )
        carried = int(out_df["review_rephrase_status"].eq("success").sum())
        self.assertEqual(carried, 244)
        self.assertEqual(len(out_df) - carried, 101)  # 100 pending + 1 failed re-sent


class ProposalResumeGateTests(unittest.TestCase):
    def test_compatible_gate_accepts_partial_file(self):
        partial = pd.DataFrame({
            "proposal_uid": ["a", "b", "c"],
            "proposal_rephrase_status": ["success", "success", ""],
            "proposal_rephrase_prompt_version": ["prop_v1", "prop_v1", ""],
        })
        self.assertFalse(_proposal_rephrase_prompt_matches(partial, "prop_v1"))
        self.assertTrue(_proposal_rephrase_prompt_compatible(partial, "prop_v1"))


if __name__ == "__main__":
    unittest.main()
