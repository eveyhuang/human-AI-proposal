# Human-AI Proposal Analysis

This repo compares human-written and AI-generated research proposals under several prompting conditions, then runs the same downstream analyses for each condition.

The main entrypoint is [src/run_condition.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/run_condition.py:1). It does **not** execute the pipeline. It only renders the condition-specific notebooks into the right folder so you can run them yourself in order.

## Quick Start

Render the full notebook pipeline for one condition:

```bash
python src/run_condition.py --condition minimal
python src/run_condition.py --condition how_to_think
python src/run_condition.py --condition persona
```

Render only some steps:

```bash
python src/run_condition.py --condition persona --steps 1,2
python src/run_condition.py --condition persona --from-step 3 --to-step 6
```

Control whether step 1 is set to generate fresh ideas or reuse existing ones:

```bash
python src/run_condition.py --condition persona --generate-new-ideas
python src/run_condition.py --condition persona --reuse-existing-ideas
```

After rendering, open the notebooks in the condition folder and run them manually in order.

## Conditions

Configured conditions live in [configs/pipeline_conditions.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal/configs/pipeline_conditions.json:1):

- `minimal`
- `how_to_think`
- `persona`

Rendered notebook folders:

- `minimal` -> [baseline(minimal)-rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal/baseline(minimal)-rephrased)
- `how_to_think` -> [C1-how_to_think](/Users/eveyhuang/Documents/NICO/human-AI-proposal/C1-how_to_think)
- `persona` -> [C2-persona](/Users/eveyhuang/Documents/NICO/human-AI-proposal/C2-persona)

## Notebook Pipeline

`run_condition.py` renders these 6 notebooks:

1. `gen_proposals.ipynb`
   This now includes proposal generation and the rephrasing step at the end.
2. `compare_proposals_rephrased.ipynb`
   This consumes the rephrased AI and human proposal files and writes proposal-analysis outputs such as `all_proposals.json` and `proposal_lit_neighbors.json`.
3. `generate_reviews.ipynb`
   This runs NCEMS review generation, novelty review generation, and builds `review_scores_wide.csv`.
4. `compare_reviews_ncems_criteria.ipynb`
5. `compare_reviews_novelty.ipynb`
6. `metric_score_relationship.ipynb`

Recommended execution order inside a condition folder is the same `1 -> 6`.

## Folder Structure

### Templates you should edit

These are the canonical notebooks. If you want a change to apply to all conditions, edit these:

- [notebooks/templates/gen_proposals.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/gen_proposals.ipynb)
- [notebooks/templates/generate_reviews.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/generate_reviews.ipynb)
- [notebooks/templates/rephrased/compare_proposals_rephrased.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_proposals_rephrased.ipynb)
- [notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb)
- [notebooks/templates/rephrased/compare_reviews_novelty.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_reviews_novelty.ipynb)
- [notebooks/templates/rephrased/metric_score_relationship.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/metric_score_relationship.ipynb)

Do not hand-edit only the rendered copies in `baseline(minimal)-rephrased/`, `C1-how_to_think/`, or `C2-persona/` if you want the change to persist across rerenders.

### Main code

- Runner: [src/run_condition.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/run_condition.py:1)
- Notebook renderer: [src/notebook_pipeline.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/notebook_pipeline.py:1)
- Pipeline config loader: [src/pipeline_config.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/pipeline_config.py:1)
- Prompt templates: [src/prompt_templates.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/prompt_templates.py:1)
- Rephrasing script: [src/rephrase_proposals.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/rephrase_proposals.py:1)
- NCEMS review script: [src/generate_reviews_ncems_criteria.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/generate_reviews_ncems_criteria.py:1)
- Novelty review script: [src/generate_reviews_novelty.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/generate_reviews_novelty.py:1)
- Review-score export: [src/build_review_scores_wide.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/build_review_scores_wide.py:1)
- Persona cards builder: [src/build_persona_cards.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/build_persona_cards.py:1)

### Data and output locations

- Human source proposals: [data/human-proposals](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/human-proposals)
- AI proposals by condition: [data/ai-proposals](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/ai-proposals)
- Rephrased AI proposals: [data/ai-proposals/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/ai-proposals/rephrased)
- Rephrased human proposals: [data/human-proposals/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/human-proposals/rephrased)
- AI review outputs: [data/reviews/ai_reviews](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/reviews/ai_reviews)
- Proposal-analysis tables: [results/tables/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/tables/rephrased)
- Figures: [results/figures](/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/figures)
- Analysis plan: [docs/plans/analysis_plan.md](/Users/eveyhuang/Documents/NICO/human-AI-proposal/docs/plans/analysis_plan.md:1)

### Persona-specific inputs

- Author publication corpus: [data/literature/human-scientists-corpus.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/literature/human-scientists-corpus.json:1)
- Persona cards: [data/literature/persona_cards.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/literature/persona_cards.json)

`persona` step 1 expects `persona_cards.json` to already exist.

## What Each Notebook Expects

1. `gen_proposals.ipynb`
   Reads or generates ideas under `data/ai-proposals/<condition>/`, writes complete proposal CSVs there, then writes rephrased outputs to:
   `data/ai-proposals/rephrased/<condition>/` and `data/human-proposals/rephrased/<condition>/`.

2. `compare_proposals_rephrased.ipynb`
   Reads the rephrased files and writes outputs under:
   `results/tables/rephrased/<condition>/` and `results/figures/rephrased/<condition>/`.
   One important output is `proposal_lit_neighbors.json`, which step 3 needs.

3. `generate_reviews.ipynb`
   Reads rephrased proposals and `proposal_lit_neighbors.json`, then writes:
   `data/reviews/ai_reviews/<condition>/ncems_criteria/`
   `data/reviews/ai_reviews/<condition>/novelty/`
   `results/tables/rephrased/<condition>/review_scores_wide.csv`

4. `compare_reviews_ncems_criteria.ipynb`
   Reads the latest NCEMS review JSON for the condition.

5. `compare_reviews_novelty.ipynb`
   Reads the latest novelty review JSON for the condition.

6. `metric_score_relationship.ipynb`
   Reads `results/tables/rephrased/<condition>/all_proposals.json` plus the latest review JSONs.

## Typical Workflows

Render everything for a condition:

```bash
python src/run_condition.py --condition persona
```

Render only proposal generation and proposal analysis:

```bash
python src/run_condition.py --condition how_to_think --steps 1,2
```

Render only the review-side notebooks after changing review analysis:

```bash
python src/run_condition.py --condition minimal --steps 3,4,5,6
```

Rerender a single notebook after editing its template:

```bash
python src/run_condition.py --condition persona --steps 6
```

## Notes

- The rendered notebooks are path-aware and try to locate the repo root automatically, so they can be run from the condition folder or from a repo-root Jupyter session.
- `run_condition.py` overwrites the rendered notebook copies for the selected steps.
- If you change an analysis and want that change reflected across all conditions, update the template notebook and rerender each condition.
