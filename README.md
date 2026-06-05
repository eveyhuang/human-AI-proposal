# Human-AI Proposal Analysis

This repo compares human-written and AI-generated research proposals under several prompting conditions, then runs the same downstream analyses for each condition.

The main entrypoint is [src/run_condition.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/run_condition.py:1). It does **not** execute the pipeline. It only renders the condition-specific notebooks into the right folder so you can run them yourself in order.

## Quick Start

Render the full notebook pipeline for one condition:

```bash
python src/run_condition.py --condition minimal
python src/run_condition.py --condition high_temperature
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

Configured conditions live in [configs/pipeline_conditions.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/configs/pipeline_conditions.json:1):

- `minimal`
- `high_temperature`
- `how_to_think`
- `persona`

Rendered notebook folders:

- `minimal` -> [baseline(minimal)-rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/baseline(minimal)-rephrased)
- `high_temperature` -> [C3-high_temperature](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/C3-high_temperature)
- `how_to_think` -> [C1-how_to_think](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/C1-how_to_think)
- `persona` -> [C2-persona](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/C2-persona)

`high_temperature` uses the same minimal idea and proposal prompts as `minimal`, but renders step 1 with `GENERATION_TEMPERATURE = 0.8` for AI idea and proposal generation. The generated CSV rows include `generation_temperature` so the sampling setting can be audited later.

## Notebook Pipeline

`run_condition.py` renders these 7 notebooks:

1. `gen_proposals.ipynb`
   This now includes proposal generation and the rephrasing step at the end.
2. `compare_proposals_rephrased.ipynb`
   This consumes the rephrased AI and human proposal files and writes proposal-analysis outputs such as `all_proposals.json` and `proposal_lit_neighbors.json`.
3. `generate_reviews.ipynb`
   This runs NCEMS review generation, novelty review generation, and builds `review_scores_wide.csv`.
4. `prepare_data_for_analysis.ipynb`
   This prepares reusable datasets and embedding artifacts consumed by downstream analysis notebooks.
5. `compare_reviews_ncems_criteria.ipynb`
6. `compare_reviews_novelty.ipynb`
7. `metric_score_relationship.ipynb`

Recommended execution order inside a condition folder is the same `1 -> 7`.

## Folder Structure

### Templates you should edit

These are the canonical notebooks. If you want a change to apply to all conditions, edit these:

- [notebooks/templates/gen_proposals.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/gen_proposals.ipynb)
- [notebooks/templates/generate_reviews.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/generate_reviews.ipynb)
- [notebooks/templates/rephrased/compare_proposals_rephrased.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/rephrased/compare_proposals_rephrased.ipynb)
- [notebooks/templates/rephrased/prepare_data_for_analysis.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/rephrased/prepare_data_for_analysis.ipynb)
- [notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb)
- [notebooks/templates/rephrased/compare_reviews_novelty.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/rephrased/compare_reviews_novelty.ipynb)
- [notebooks/templates/rephrased/metric_score_relationship.ipynb](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/notebooks/templates/rephrased/metric_score_relationship.ipynb)

Do not hand-edit only the rendered copies in `baseline(minimal)-rephrased/`, `C1-how_to_think/`, or `C2-persona/` if you want the change to persist across rerenders.

### Main code

- Runner: [src/run_condition.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/run_condition.py:1)
- Notebook renderer: [src/notebook_pipeline.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/notebook_pipeline.py:1)
- Pipeline config loader: [src/pipeline_config.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/pipeline_config.py:1)
- Prompt templates: [src/prompt_templates.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/prompt_templates.py:1)
- Rephrasing script: [src/rephrase_proposals.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/rephrase_proposals.py:1)
- NCEMS review script: [src/generate_reviews_ncems_criteria.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/generate_reviews_ncems_criteria.py:1)
- Novelty review script: [src/generate_reviews_novelty.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/generate_reviews_novelty.py:1)
- Review-score export: [src/build_review_scores_wide.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/build_review_scores_wide.py:1)
- Persona cards builder: [src/build_persona_cards.py](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/src/build_persona_cards.py:1)

### Data and output locations

- Human source proposals: [data/human-proposals](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/human-proposals)
- AI proposals by condition: [data/ai-proposals](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/ai-proposals)
- Rephrased AI proposals: [data/ai-proposals/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/ai-proposals/rephrased)
- Rephrased human proposals: [data/human-proposals/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/human-proposals/rephrased)
- AI review outputs: [data/reviews/ai_reviews](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/reviews/ai_reviews)
- Proposal-analysis tables: [results/tables/rephrased](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/results/tables/rephrased)
- Figures: [results/figures](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/results/figures)
- Analysis plan: [docs/plans/analysis_plan.md](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/docs/plans/analysis_plan.md:1)

### Persona-specific inputs

- Author publication corpus: [data/literature/human-scientists-corpus.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/literature/human-scientists-corpus.json:1)
- Persona cards: [data/literature/persona_cards.json](/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison/data/literature/persona_cards.json)

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

4. `prepare_data_for_analysis.ipynb`
   Reads outputs from proposal and review generation steps and writes normalized prepared datasets under `data/prepared/rephrased/<condition>/`.

5. `compare_reviews_ncems_criteria.ipynb`
   Reads the latest NCEMS review JSON for the condition.

6. `compare_reviews_novelty.ipynb`
   Reads the latest novelty review JSON for the condition.

7. `metric_score_relationship.ipynb`
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

Render only the review-side and downstream analysis notebooks:

```bash
python src/run_condition.py --condition minimal --steps 3,4,5,6,7
```

Rerender a single notebook after editing its template:

```bash
python src/run_condition.py --condition persona --steps 6
```

## Notes

- The rendered notebooks are path-aware and try to locate the repo root automatically, so they can be run from the condition folder or from a repo-root Jupyter session.
- `run_condition.py` overwrites the rendered notebook copies for the selected steps.
- If you change an analysis and want that change reflected across all conditions, update the template notebook and rerender each condition.
