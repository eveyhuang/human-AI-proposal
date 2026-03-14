# Design: Style-Controlled Rephrasing Pipeline

**Date:** 2026-03-12
**Status:** Approved

## Problem

Style-only features (AUROC = 1.0) perfectly separate human vs. AI proposals, making it impossible to attribute downstream diversity/novelty/quality differences to scientific content. The existing style-residualization in Analysis 2.3.6 is insufficient because embeddings already encode style strongly. A more robust approach: rephrase all proposals into a single neutral academic style, then rerun all analyses on the neutralized text.

## Goal

Rephrase every proposal (AI and human) field-by-field into a standardized neutral academic writing style using `gemini-2.0-flash`, then:
1. Rerun all proposal comparison analyses (diversity, novelty, thematic/cluster, style baseline)
2. Re-generate AI reviews on rephrased proposals
3. Rerun review comparison analyses

This produces a fully parallel "style-controlled" comparison folder to sit alongside the baseline results.

## Data Sources

| Source | Count | Fields to rephrase |
|--------|-------|--------------------|
| `data/ai-proposals/baseline/ai_proposals_baseline_complete_*.csv` | 69 rows (23 × 3 models) | `title`, `abstract`, `background_and_significance`, `research_questions_and_hypotheses`, `methods_and_approach`, `expected_outcomes_and_impact`, `budget_and_resources` |
| `data/human-proposals/human-proposals-y1.json` | 12 proposals | `proposal_title`, `abstract`, `full_draft` |
| `data/human-proposals/human-proposals-y2.json` | 11 proposals | `proposal_title`, `abstract`, `full_draft` |

## Rephrasing Design

**Model:** `gemini-2.0-flash` (via Google Generative AI SDK, same client as existing `ai_models_interface.py`)

**Strategy:** Rephrase each field separately to:
- Standardize sentence structure (subject-verb-object, ~20-25 word average sentence length)
- Normalize hedging language (use consistent set: "may", "suggests", "is expected to")
- Remove AI-specific patterns (e.g., excessive bullet formatting, "I will", "we propose to")
- Remove human-specific patterns (informal phrasing, inconsistent capitalization)
- Preserve all scientific content: hypotheses, methods, data sources, expected outcomes
- Target a uniform academic register (similar to Nature Methods writing style)

**Field handling:**
- `title` / `proposal_title`: Rephrase to standard title case, noun-phrase format, no verbs
- `abstract`: Standardize to 4 sentences: background, gap, approach, expected contribution
- All other fields: Standardize paragraph structure (topic sentence + supporting detail)
- `full_draft` (human proposals): Rephrase section by section, preserving section headers

## Output Files

```
data/ai-proposals/rephrased/
  ai_proposals_rephrased_<timestamp>.csv    # same columns as baseline CSV

data/human-proposals/rephrased/
  human_proposals_rephrased_y1_<timestamp>.json   # same structure as original
  human_proposals_rephrased_y2_<timestamp>.json
```

## Scripts (`src/`)

| Script | Purpose |
|--------|---------|
| `rephrase_proposals.py` | Rephrase all AI and human proposals field-by-field using gemini-2.0-flash |
| `generate_reviews_rephrased.py` | Re-generate AI reviews (GPT, Gemini, Claude) for rephrased proposals |

## Notebooks (`style-controlled comparison/`)

| Notebook | Mirrors | Key differences |
|----------|---------|-----------------|
| `compare_proposals_rephrased.ipynb` | `compare_proposals_baseline.ipynb` | Load from `data/*/rephrased/`, save embeddings to `data/embeddings/rephrased/` |
| `compare_reviews_rephrased.ipynb` | `compare_reviews.ipynb` | Load rephrased proposals + reviews from rephrased review JSON |

## Implementation Plan Summary

1. Write `src/rephrase_proposals.py`
2. Write `src/generate_reviews_rephrased.py`
3. Create `style-controlled comparison/compare_proposals_rephrased.ipynb`
4. Create `style-controlled comparison/compare_reviews_rephrased.ipynb`
