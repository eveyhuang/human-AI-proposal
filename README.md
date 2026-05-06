# Human-AI Proposal Analysis

This repo compares human-written and AI-generated research proposals under multiple generation conditions, then runs a shared downstream analysis pipeline on each condition.

The main entrypoint is [`src/run_condition.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/run_condition.py:1).

## Quick Start

Run a full condition:

```bash
python src/run_condition.py --condition how_to_think
python src/run_condition.py --condition persona
```

Run only part of the pipeline:

```bash
python src/run_condition.py --condition how_to_think --from-step 1 --to-step 2
python src/run_condition.py --condition how_to_think --steps 3,4,5,6,7,8,9
python src/run_condition.py --condition persona --steps 1,2,7,9
```

Useful flags:

```bash
python src/run_condition.py --condition how_to_think --force
python src/run_condition.py --condition how_to_think --render-only
python src/run_condition.py --condition persona --generate-new-ideas
python src/run_condition.py --condition persona --reuse-existing-ideas
```

## Conditions

Current configured conditions are defined in [`configs/pipeline_conditions.json`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/configs/pipeline_conditions.json:1):

- `minimal`
- `how_to_think`
- `persona`

Each condition has:

- an AI proposal generation directory under `data/ai-proposals/<condition>/`
- a rephrased output directory under `data/ai-proposals/rephrased/<condition>/`
- a human rephrased directory under `data/human-proposals/rephrased/<condition>/`
- an executed notebook directory where rendered notebooks are saved for inspection

Executed notebook folders:

- `minimal` -> [`baseline(minimal)-rephrased`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/baseline(minimal)-rephrased)
- `how_to_think` -> [`C1-how_to_think`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/C1-how_to_think)
- `persona` -> [`C2-persona`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/C2-persona)

## Pipeline Steps

`run_condition.py` uses these step numbers:

1. Generate proposals notebook
2. Rephrase proposals
3. Compare proposals rephrased notebook
4. Generate NCEMS reviews
5. Generate novelty reviews
6. Build `review_scores_wide.csv`
7. Compare NCEMS reviews notebook
8. Compare novelty reviews notebook
9. Metric-score relationship notebook

Default dependency order:

1. Step 1 creates AI proposals.
2. Step 2 rephrases AI and human proposals.
3. Step 3 computes proposal-level analyses and writes artifacts such as literature neighbors.
4. Step 5 depends on step 3 because novelty reviews need proposal literature neighbors.
5. Step 6 builds `review_scores_wide.csv` from the review outputs.
6. Steps 7-9 use the review and proposal analysis outputs.

## Where To Look

### Main code

- Runner: [`src/run_condition.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/run_condition.py:1)
- Notebook rendering/execution: [`src/notebook_pipeline.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/notebook_pipeline.py:1)
- Pipeline config loader: [`src/pipeline_config.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/pipeline_config.py:1)
- Rephrase script: [`src/rephrase_proposals.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/rephrase_proposals.py:1)
- NCEMS review generation: [`src/generate_reviews_ncems_criteria.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/generate_reviews_ncems_criteria.py:1)
- Novelty review generation: [`src/generate_reviews_novelty.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/generate_reviews_novelty.py:1)
- Review score export: [`src/build_review_scores_wide.py`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/src/build_review_scores_wide.py:1)

### Canonical notebook templates

These are the source notebooks you should edit if you want changes to apply across all conditions:

- Generation template: [`notebooks/templates/gen_proposals.ipynb`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/gen_proposals.ipynb)
- Rephrased proposal analysis: [`notebooks/templates/rephrased/compare_proposals_rephrased.ipynb`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_proposals_rephrased.ipynb)
- NCEMS review analysis: [`notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb)
- Novelty review analysis: [`notebooks/templates/rephrased/compare_reviews_novelty.ipynb`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/compare_reviews_novelty.ipynb)
- Metric/score relationship: [`notebooks/templates/rephrased/metric_score_relationship.ipynb`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/notebooks/templates/rephrased/metric_score_relationship.ipynb)

Do not hand-edit only the executed notebooks in `C1-how_to_think/`, `C2-persona/`, or `baseline(minimal)-rephrased/` if you want the change to stay consistent across reruns. Edit the template, then rerun the condition.

### Data and results

- Human source proposals: [`data/human-proposals`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/human-proposals)
- AI proposals by condition: [`data/ai-proposals`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/ai-proposals)
- Rephrased proposals: [`data/ai-proposals/rephrased`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/ai-proposals/rephrased) and [`data/human-proposals/rephrased`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/human-proposals/rephrased)
- AI review outputs: [`data/reviews/ai_reviews`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/reviews/ai_reviews)
- Figures: [`results/figures`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/figures)
- Tables: [`results/tables`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/tables)
- Analysis plan: [`docs/plans/analysis_plan.md`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/docs/plans/analysis_plan.md:1)

## Common Workflows

### 1. Run a brand-new condition end to end

```bash
python src/run_condition.py --condition how_to_think
```

### 2. Generate proposals and rephrase first, inspect later

```bash
python src/run_condition.py --condition persona --steps 1,2
```

### 3. Re-run just downstream analysis notebooks after editing a template

```bash
python src/run_condition.py --condition how_to_think --steps 3,7,8,9 --force
```

### 4. Render notebooks without executing them

```bash
python src/run_condition.py --condition persona --steps 3,7,8,9 --render-only
```

## How The Notebook System Works

- Templates live in `notebooks/templates/`.
- `run_condition.py` renders them with the right condition-specific paths.
- Rendered notebooks are saved into the condition folder like `C1-how_to_think/`.
- Those rendered notebooks are the ones you inspect after a run.

This gives you:

- one canonical source notebook per analysis
- one executed notebook per condition
- consistent reruns across conditions

## Environment Notes

Use the same Python environment you normally use to run the project notebooks. The pipeline renders notebooks itself, but execution still depends on the scientific Python stack used by the notebooks.

If something fails, the first places to check are:

- the rendered notebook in the condition folder
- the latest files under `data/ai-proposals/<condition>/`
- the latest files under `data/ai-proposals/rephrased/<condition>/`
- the latest files under `results/tables/rephrased/<condition>/`

## For New Collaborators

If you are new to the repo, start here:

1. Read [`docs/plans/analysis_plan.md`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/docs/plans/analysis_plan.md:1).
2. Look at [`configs/pipeline_conditions.json`](/Users/eveyhuang/Documents/NICO/human-AI-proposal/configs/pipeline_conditions.json:1).
3. Run `python src/run_condition.py --condition minimal --steps 3 --render-only` to see how a notebook is rendered.
4. Edit notebook templates in `notebooks/templates/`, not the executed copies.
