"""
create_rephrased_notebooks.py

Generates two style-controlled analysis notebooks by patching the baseline
notebooks to point at rephrased data instead of baseline data.

Tasks 6 & 7 of the implementation plan.
"""

import copy
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "style-controlled comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def join_source(source):
    """Return the cell source as a single string regardless of list vs str."""
    if isinstance(source, list):
        return "".join(source)
    return source


def set_source(source_str):
    """Store the patched source as a single-element list (Jupyter standard)."""
    return [source_str]


def clear_outputs(nb):
    """Clear all cell outputs and execution_counts in-place."""
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None


def save_notebook(nb, path):
    """Save notebook with indent=1 to match Jupyter's default."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Task 6 — compare_proposals_rephrased.ipynb
# ---------------------------------------------------------------------------

PROPOSALS_TITLE = [
    "# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)\n",
    "\n",
    "This notebook mirrors `compare_proposals_baseline.ipynb` but uses proposals rephrased by "
    "`gemini-2.0-flash` into a standardized neutral academic style, removing stylistic "
    "fingerprints before analysis.\n",
    "\n",
    "**Data sources:**\n",
    "- `data/ai-proposals/rephrased/ai_proposals_rephrased_*.csv`\n",
    "- `data/human-proposals/rephrased/human_proposals_rephrased_y*.json`\n",
    "\n",
    "All analyses (diversity, novelty, thematic, style baseline) are identical to the baseline notebook.",
]


def create_proposals_notebook():
    src_path = PROJECT_ROOT / "compare_proposals_baseline.ipynb"
    with open(src_path, encoding="utf-8") as f:
        nb = json.load(f)

    nb = copy.deepcopy(nb)
    modified_cells = []

    # --- Cell 0: title ---
    nb["cells"][0]["source"] = PROPOSALS_TITLE
    modified_cells.append((0, "title"))

    # --- Patch remaining cells ---
    for i, cell in enumerate(nb["cells"]):
        if i == 0:
            continue

        src = join_source(cell["source"])
        original = src

        # Data loading cell: ai-proposals path and glob pattern
        if "data/ai-proposals/baseline" in src or "ai_proposals_baseline_complete_" in src:
            src = src.replace(
                "Path('data/ai-proposals/baseline')",
                "Path('data/ai-proposals/rephrased')",
            )
            src = src.replace(
                'Path("data/ai-proposals/baseline")',
                'Path("data/ai-proposals/rephrased")',
            )
            src = src.replace(
                "'ai_proposals_baseline_complete_*.csv'",
                "'ai_proposals_rephrased_*.csv'",
            )
            src = src.replace(
                '"ai_proposals_baseline_complete_*.csv"',
                '"ai_proposals_rephrased_*.csv"',
            )

        # Human proposals path variable
        if "human_proposals_path = Path('data/human-proposals')" in src:
            src = src.replace(
                "human_proposals_path = Path('data/human-proposals')",
                "human_proposals_path = Path('data/human-proposals/rephrased')",
            )
        if 'human_proposals_path = Path("data/human-proposals")' in src:
            src = src.replace(
                'human_proposals_path = Path("data/human-proposals")',
                'human_proposals_path = Path("data/human-proposals/rephrased")',
            )

        # embeddings_dir variable
        if "embeddings_dir = Path('data/embeddings')" in src:
            src = src.replace(
                "embeddings_dir = Path('data/embeddings')",
                "embeddings_dir = Path('data/embeddings/rephrased')",
            )
        if 'embeddings_dir = Path("data/embeddings")' in src:
            src = src.replace(
                'embeddings_dir = Path("data/embeddings")',
                'embeddings_dir = Path("data/embeddings/rephrased")',
            )

        # Hardcoded 'data/embeddings' strings (path glob calls etc.)
        # But do NOT double-replace already-patched 'data/embeddings/rephrased'
        # Strategy: replace bare 'data/embeddings' that is NOT already followed by '/rephrased'
        import re as _re
        src = _re.sub(
            r"'data/embeddings'(?!/rephrased')",
            "'data/embeddings/rephrased'",
            src,
        )
        src = _re.sub(
            r'"data/embeddings"(?!/rephrased")',
            '"data/embeddings/rephrased"',
            src,
        )

        if src != original:
            cell["source"] = set_source(src)
            modified_cells.append((i, "data paths"))

    clear_outputs(nb)

    out_path = OUT_DIR / "compare_proposals_rephrased.ipynb"
    save_notebook(nb, out_path)

    print(f"\nProposals notebook — modified cells: {modified_cells}")
    return modified_cells


# ---------------------------------------------------------------------------
# Task 7 — compare_reviews_rephrased.ipynb
# ---------------------------------------------------------------------------

REVIEWS_TITLE = [
    "# PART IV QUALITY — Compare Human and AI Reviews (Style-Controlled / Rephrased)\n",
    "\n",
    "This notebook mirrors `compare_reviews.ipynb` but uses AI reviews generated on rephrased proposals.\n",
    "\n",
    "**Review data:** `data/reviews/ai_reviews/ai_reviews_rephrased_*.json`\n",
    "**Proposal data:** `data/*/rephrased/`",
]

OLD_REVIEW_PATH_OBJ = "Path('data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json')"
NEW_REVIEW_PATH_OBJ = "sorted(Path('data/reviews/ai_reviews').glob('ai_reviews_rephrased_*.json'))[-1]"

OLD_REVIEW_PATH_STR = "'data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json'"
NEW_REVIEW_PATH_STR = "str(sorted(Path('data/reviews/ai_reviews').glob('ai_reviews_rephrased_*.json'))[-1])"


def create_reviews_notebook():
    src_path = PROJECT_ROOT / "compare_reviews.ipynb"
    with open(src_path, encoding="utf-8") as f:
        nb = json.load(f)

    nb = copy.deepcopy(nb)
    modified_cells = []

    # --- Cell 0: title ---
    nb["cells"][0]["source"] = REVIEWS_TITLE
    modified_cells.append((0, "title"))

    # --- Patch remaining cells ---
    for i, cell in enumerate(nb["cells"]):
        if i == 0:
            continue

        src = join_source(cell["source"])
        original = src

        # Replace Path(...) form first (more specific)
        if OLD_REVIEW_PATH_OBJ in src:
            src = src.replace(OLD_REVIEW_PATH_OBJ, NEW_REVIEW_PATH_OBJ)

        # Replace bare string form
        if OLD_REVIEW_PATH_STR in src:
            src = src.replace(OLD_REVIEW_PATH_STR, NEW_REVIEW_PATH_STR)

        if src != original:
            cell["source"] = set_source(src)
            modified_cells.append((i, "review file path"))

    clear_outputs(nb)

    out_path = OUT_DIR / "compare_reviews_rephrased.ipynb"
    save_notebook(nb, out_path)

    print(f"\nReviews notebook — modified cells: {modified_cells}")
    return modified_cells


if __name__ == "__main__":
    print("=" * 60)
    print("Creating compare_proposals_rephrased.ipynb …")
    print("=" * 60)
    create_proposals_notebook()

    print()
    print("=" * 60)
    print("Creating compare_reviews_rephrased.ipynb …")
    print("=" * 60)
    create_reviews_notebook()

    print("\nDone.")
