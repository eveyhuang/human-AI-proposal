## Overview

This document is now an **execution-status analysis plan** based on the completed notebooks in:

- `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb`
- `baseline(minimal)-rephrased/compare_reviews_ncems_criteria.ipynb`
- `notebooks/templates/rephrased/compare_reviews_novelty.ipynb`
- `notebooks/templates/rephrased/metric_score_relationship.ipynb`

Primary question: how Human vs AI proposals differ on diversity, novelty, thematic structure, and review outcomes.

## Data Used (Actual)

- Proposal set: `n=92` total.
- Group sizes: Human `23`, Claude `23`, Gemini `23`, GPT-5.2 `23`, All AI `69`.
- Literature corpus for novelty: `n=39538` abstracts. Date from `2010-01-01` to `2026-05-25`
- Review datasets parsed for metric-score integration: `276` NCEMS reviews + `276` novelty-framework reviews.
- Human Y2 quantitative review scores for metric-score linkage:
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased.csv`

## Prepared Data Inventory (`prepare_data_for_analysis.ipynb`)

The table below is the single-source-of-truth inventory of artifacts prepared in
`notebooks/templates/rephrased/prepare_data_for_analysis.ipynb`, what each artifact contains,
and where it is consumed downstream.


| Prepared artifact                                                              | What it is                                                                                                                            | Used in notebooks                                                                           |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `data/prepared/rephrased/minimal/all_proposals.json`                 | Prepared proposal records (AI + Human Y1/Y2), standardized text fields, normalized titles, metadata scaffold                          | `compare_proposals_rephrased.ipynb`, `metric_score_relationship.ipynb`                      |
| `data/prepared/rephrased/minimal/all_proposals.csv`                  | Flat proposal table companion to prepared proposal JSON                                                                               | QA/reference in proposal and metric workflows                                               |
| `results/tables/rephrased/minimal/all_proposals.json`                          | Analysis-compatible proposal JSON copy updated by downstream metric/style merges                                                      | `compare_proposals_rephrased.ipynb` (final merge target), `metric_score_relationship.ipynb` |
| `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`     | Merged NCEMS review table (AI + Human Y1 + Human Y2) with harmonized reviewer-level schema, including original + rephrased review text fields (`review_text`, `rephrased_review`, `original_review_text`, `strengths`, `weakness`), unified NCEMS criteria score columns (`Relevance_to_Emergent_Phenomena` to `Open_Science_Commitment`), proposal-level score aggregates (`average_score_human`, `average_score_AI`), `ranking_AI_reviews` (rank by `average_score_AI` within author for AI / within cohort for humans), human proposal `ranking` from `human-proposals-y1/y2.json`, and `funding` (`1` accepted, `0` rejected, `NA` for AI proposals) | `compare_reviews_ncems_criteria.ipynb`, `metric_score_relationship.ipynb`                   |
| `data/prepared/rephrased/minimal/novelty_all_reviews.csv`            | Merged novelty-framework review table (prepared schema)                                                                               | `compare_reviews_novelty.ipynb`                                                             |
| `data/prepared/rephrased/minimal/review_scores_wide.csv`                      | Proposal-level AI review score means (NCEMS + novelty criteria)                                                                       | `compare_proposals_rephrased.ipynb` (final merge), `metric_score_relationship.ipynb`        |
| `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`           | Proposal-level Human-Y2 quantitative score means mapped to NCEMS-equivalent score columns                                             | `metric_score_relationship.ipynb`                                                           |
| `data/prepared/rephrased/minimal/literature_corpus_prepared.json`    | Prepared literature corpus payload for novelty analyses (articles + search metadata), moved out of proposal notebook raw-loading path | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl` | Prepared full-proposal embeddings (AI/Human) + metadata                                                                               | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`      | Prepared abstract-only proposal embeddings for literature novelty comparisons                                                         | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/literature/relevant_literature_embeddings.pkl`                | Prepared literature embeddings used for proposal-to-literature distance calculations                                                  | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl` | Prepared NCEMS review embeddings with metadata + `review_uid` alignment                                                               | `compare_reviews_ncems_criteria.ipynb`                                                      |
| `data/embeddings/reviews/minimal/novelty/review_embeddings_minimal.pkl`        | Prepared novelty review embeddings with metadata + `review_uid` alignment                                                             | `compare_reviews_novelty.ipynb` (future-ready; current core analysis is score-table based)  |


## Experiment Conditions

This study now has three generation conditions:

1. `baseline(minimal)-rephrased` (**completed**)

- LLMs generate ideas/proposals under the minimal prompt pipeline with rephrasing.
- This condition is the current reference condition and all completed results in this plan come from it.

1. `how_to_think` (**planned next**)

- LLMs first use an LLM-suggested “how to think” process, then generate ideas/proposals using that process.

1. `persona` (**planned next**)

- LLMs generate ideas/proposals while adopting human-scientist author personas.
- Inputs include titles/abstracts of recent papers by the target author(s) during idea generation.

### Cross-condition comparison plan

- For both **ideas** and **full proposals**, run the same analysis families already used in baseline:
- Diversity analyses.
- Novelty analyses.
- Score-comparison analyses.
- Primary comparison: each new condition (`how_to_think`, `persona`) vs `baseline(minimal)-rephrased`, then Human vs each condition.

## Completed Analyses and Results

> **Update (June 1, 2026):** compact proposal results below have been refreshed from the rendered `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb` outputs; NCEMS rows reflect the executed baseline/minimal review notebook audit.


### Compact Results Table

Stars indicate corrected/primary significance for the model-vs-Human contrast: `*** p<.001`, `** p<.01`, `* p<.05`; blank means not significant. Unless noted, `Δ` is AI model minus Human, so negative values mean Human is higher.

| Analysis | Human reference | Claude vs Human | Gemini vs Human | GPT-5.2 vs Human | Primary test |
| --- | --- | --- | --- | --- | --- |
| Proposal diversity 1.1 pairwise / Remote-Clique family | mean pairwise `0.4429` | `0.0337`; Δ `-0.3670` `***`; δ `-1.000` | `0.1505`; Δ `-0.2838` `***`; δ `-0.826` | `0.3148`; Δ `-0.1546` `**`; δ `-0.478` | MW Holm |
| Proposal diversity 1.2a centroid LOO | centroid LOO `0.2665` | `0.0178`; Δ `-0.2451` `***`; δ `-1.000` | `0.0802`; Δ `-0.1862` `***`; δ `-0.826` | `0.1787`; Δ `-0.0848` `**`; δ `-0.478` | MW Holm |
| Proposal diversity 1.2b global centroid | global-centroid dist `0.2926` | `0.0400`; H-AI `0.2526` `***`; δ `0.887` | `0.0869`; H-AI `0.2057` `***`; δ `0.705` | `0.1704`; H-AI `0.1222` `**`; δ `0.580` | MW Holm |
| Proposal diversity 1.2c MST dispersion | MST `0.1126` | `0.0241`; Δ `-0.0885` `***` | `0.0643`; Δ `-0.0482` `**` | `0.0733`; Δ `-0.0393` `*` | Permutation Holm |
| Proposal diversity 1.2d sparseness | sparseness `0.3721` | `0.0267`; Δ `-0.3454` `***`; δ `-0.915` | `0.0870`; Δ `-0.2810` `***`; δ `-0.765` | `0.2052`; Δ `-0.1656` `***`; δ `-0.595` | MW Holm |
| Proposal diversity 1.3 1-NN / Chamfer | Chamfer `0.0822` | `0.0237`; Δ `-0.0505` `***`; δ `-0.813` | `0.0432`; Δ `-0.0413` `***`; δ `-0.713` | `0.0463`; Δ `-0.0331` `**`; δ `-0.507` | MW Holm |
| Proposal diversity 1.5 grid entropy | normalized entropy `0.4145` | `0.7494`; Δ `+0.3349` `**` | `0.2268`; Δ `-0.1876` | `0.2861`; Δ `-0.1284` | Permutation Holm |
| Proposal novelty ElementNovel-0 | mean `0.0989` | `0.0658`; Δ `-0.0332` `**`; δ `-0.580` | `0.0717`; Δ `-0.0272` `**`; δ `-0.565` | `0.0792`; Δ `-0.0198` `*`; δ `-0.353` | MW Holm |
| Proposal novelty ElementNovel-10 | mean `0.2003` | `0.1620`; Δ `-0.0383` `**`; δ `-0.561` | `0.1700`; Δ `-0.0302` `*`; δ `-0.429` | `0.1828`; Δ `-0.0175`; δ `-0.070` | MW Holm |
| Proposal novelty MeanKNN-10 | mean `0.1109` | `0.0746`; Δ `-0.0363` `**`; δ `-0.573` | `0.0828`; Δ `-0.0281` `*`; δ `-0.482` | `0.0914`; Δ `-0.0195`; δ `-0.202` | MW Holm |
| Proposal novelty normalized `novelty_z` | mean `1.0508` | `0.4966`; Δ `-0.5541` `*`; δ `-0.444` | `0.6700`; Δ `-0.3808`; δ `-0.388` | `0.7937`; Δ `-0.2571`; δ `0.025` | MW Holm |
| Proposal literature-space outliers mean-10NN | Human `5/23` (`21.7%`) | `0/23` (`0.0%`) | `2/23` (`8.7%`) | `3/23` (`13.0%`) | Fisher Holm; no model significant |
| Topic distribution + cluster segregation | topics: no Human/AI difference; clusters segregate | topic distribution not model-specific; cluster source segregation significant | topic distribution not model-specific; cluster source segregation significant | topic distribution not model-specific; cluster source segregation significant | Topic perm `p=0.5990`; NMI `**`; ARI `**`; B/W ratio `**` |
| Style sensitivity | style-only classifier weak; centroid separation robust | centroid style-adjusted Δ `-0.2027` `***`; style-NN Δ `+0.0320` | centroid style-adjusted Δ `-0.1345` `***`; style-NN Δ `+0.0746` | centroid style-adjusted Δ `-0.0478` `**`; style-NN Δ `+0.0282` | Centroid MW/permutation; style-NN ns |
| NCEMS R1 review diversity | Human review diversity > AI-all; Y2 all metrics `***`; Y1 4/9 metrics `*` | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | Paired Wilcoxon FDR |
| NCEMS R1 Human-AI review similarity, Y1 cosine | Human-Human baseline | Human-AI vs Human-Human δ `-0.042` | Human-AI vs Human-Human δ `0.083` | Human-AI vs Human-Human δ `-0.236` | MW FDR; all model contrasts ns (`q=0.8852`) |
| NCEMS R1 Y1/Y2 within-cohort review similarity | Human-Y1 `0.9583`; Human-Y2 `0.9524` | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | AI-all: Y2 Human vs AI `***`; Y1 trend ns |
| NCEMS R1 Y2 score reliability | Human-Human ICC2k overall `0.4949`; Human-vs-AI ICC2k `0.7805` `*` | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | Spearman/ICC |
| NCEMS quality reviews, raw evaluator pool | Human-all mean `3.5855` | mean `4.0087`; H-AI Δ `-0.4232` `***` | mean `3.8319`; H-AI Δ `-0.2464` `*` | mean `4.3174`; H-AI Δ `-0.7319` `***` | Robust permutation q |
| NCEMS quality reviews, cross-eval only | Human-all mean `3.5855` | mean `4.0739`; δ `-0.652` `***` | mean `3.6761`; δ `0.070` | mean `4.4739`; δ `-0.992` `***` | MW FDR |
| NCEMS R3 self-preference | compares each evaluator's self vs other AI proposals | self `3.8783`, other `3.8870`; δ `-0.053` | self `4.1435`, other `4.5304`; δ `-0.732` `***` | self `4.0043`, other `3.8065`; δ `0.933` `***` | MW FDR |
| Novelty-framework reviews, cross-eval rerun | Human reference from novelty-review notebook | Claude ~ Human; `q=0.8428` | Human > Gemini; δ `0.7788` `***` | GPT > Human; δ `-0.4631` `*` | MW FDR |
| Metric-score + outlier validation | semantic remoteness penalized on NCEMS but can help novelty-specific criteria | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | Outlier NCEMS relevance `***`; novelty criterion `*` |


## Notebooks and analyses

## Compare_proposals_rephrased.ipynb

#### Notebook Scope and Global Settings

Notebook title: `# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)`.

Ground-truth audited notebook: `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb`.

Purpose: compare Human and AI research proposals after all proposal texts have been rephrased into a standardized neutral academic style. The notebook analyzes proposal diversity, literature-relative novelty, thematic/cluster structure, style signal, style-adjusted embedding robustness, and final metric export.

#### `## Condition Configuration`

Step-by-step:

1. Run after the rephrasing section in `gen_proposals.ipynb`.
2. Set the rephrased proposal condition to analyze.
3. Configure whether cached proposal, main-idea, and literature embeddings should be reused.

Global settings:

- Condition label for results in this section: `baseline-minimal-rephrased`.
- Proposal input: `data/prepared/rephrased/minimal/all_proposals.json`.
- NCEMS review input for metadata/score merge: `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
- Review-score merge input: `data/prepared/rephrased/minimal/review_scores_wide.csv`.
- Tables: `results/tables/rephrased/minimal`.
- Figures: `results/figures/rephrased/minimal`.
- Full-proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Abstract/Section-1 embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.

Embedding and statistics:

- Full-proposal and abstract embeddings use `michiyasunaga/BioLinkBERT-large`, 1024-dimensional vectors, cached when available.
- Fallback embedding code uses `[CLS]` vectors with `max_length=512`.
- Full-proposal embedding analyses use cosine distance.
- Group comparisons use Mann-Whitney U, Cliff's delta, permutation tests, bootstrap CIs, and Holm correction unless a section states a different test.
- Cliff's delta thresholds: negligible `<0.147`, small `<0.33`, medium `<0.474`, large `>=0.474`.

#### `# Setup and Imports`

Step-by-step:

1. Import plotting, embedding, statistical, NLP, dimensionality-reduction, and utility libraries.
2. Locate the project root by finding `src/` and `data/`.
3. Define condition-specific prepared-data, embedding, table, and figure paths.
4. Create output/cache directories.

Baseline-minimal-rephrased result:

- Working directory: `baseline(minimal)-rephrased`.
- Project root: `/Users/eveyhuang/Documents/NICO/human-AI-proposal`.
- PyTorch `2.9.1`; CUDA unavailable.

#### `## Helper Functions`

Step-by-step:

1. Define group colors for Human, Claude, Gemini, and GPT-5.2.
2. Load cached pickle embeddings.
3. Compute Cliff's delta and qualitative effect-size labels.
4. Run two-sided permutation tests and bootstrap CIs for mean differences.
5. Combine Mann-Whitney U, Cliff's delta, permutation p-value, observed mean/median differences, and bootstrap CI in `run_group_comparison`.
6. Apply Holm multiple-testing correction.
7. Compute proposal-level mean pairwise distance-to-others so inference uses one value per proposal rather than dependent raw pairwise distances.

#### `## Load Prepared Proposal Data`

Step-by-step:

1. Load prepared proposal records from `data/prepared/rephrased/minimal/all_proposals.json`, with fallback to `results/tables/rephrased/minimal/all_proposals.json`.
2. Split records into Human and AI dataframes using `is_ai`.
3. Preserve title, model, cohort, source file, standardized text, abstract text, main idea, and group labels.

Baseline-minimal-rephrased result:

- AI proposals: `69`.
- Human proposals: `23`.
- AI model counts: GPT-5.2 `23`, Gemini `23`, Claude `23`.

#### `## Load Prepared NCEMS Reviews`

Step-by-step:

1. Load `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
2. Harmonize title/proposal keys for proposal-level merge.
3. Aggregate proposal-level review metadata, ranking, funding, and score fields for downstream joins.

Baseline-minimal-rephrased result:

- NCEMS review rows: `361`.
- Unique reviewed proposals: `92`.
- Proposal-level aggregated review rows: `95`.
- Review ranking coverage in shared proposal metadata: `96.7%`.
- Human funding coverage: `87.0%`.

#### `## Prepare Proposal Texts`

Step-by-step:

1. Use `standardized_text` for every proposal.
2. Strip standardized section headers:
   - `SCIENTIFIC BACKGROUND AND RESEARCH QUESTION`
   - `METHODOLOGY AND ANALYTICAL APPROACH`
   - `DATA SOURCES AND SYNTHESIS PLAN`
   - `FEASIBILITY AND TIMELINE`
   - `OPEN SCIENCE AND TEAM COMPOSITION`
3. Store cleaned prose as `full_text`.
4. Attach Human/AI group and AI model labels.

Baseline-minimal-rephrased result:

- AI average cleaned proposal length: `1807` characters.
- Human average cleaned proposal length: `1803` characters.

#### `## Load Prepared Full-Proposal Embeddings`

Step-by-step:

1. Set model name to `michiyasunaga/BioLinkBERT-large`.
2. Load cached full-proposal embeddings if present.
3. If missing, lazily load the model and compute fallback embeddings.
4. Load/retain `ai_embeddings`, `human_embeddings`, `ai_metadata`, and `human_metadata`.
5. Save proposal metadata.

Baseline-minimal-rephrased result:

- Loaded full-proposal embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- AI embeddings shape: `(69, 1024)`.
- Human embeddings shape: `(23, 1024)`.
- Table: `results/tables/rephrased/minimal/proposal_metadata.csv` (`92` rows).

#### `## Shared Distance-Matrix Precomputation`

Step-by-step:

1. Build canonical proposal metadata in embedding order.
2. Merge review ranking and funding metadata.
3. L2-normalize and stack all full-proposal embeddings.
4. Compute the proposal-proposal cosine distance matrix.
5. Save cached metadata, distance matrix, and deterministic PCA-2D coordinates.

Baseline-minimal-rephrased result:

- `X_prop` shape: `(92, 1024)`.
- `D_pp` shape: `(92, 92)`.
- Tables:
  - `results/tables/rephrased/minimal/cached/proposal_meta.csv`
  - `results/tables/rephrased/minimal/cached/proposal_distance_matrix.npy`
  - `results/tables/rephrased/minimal/cached/proposal_pca2d.npy`

#### `# PART I: DIVERSITY`

All Part I analyses use full rephrased proposal embeddings. Groups are Human, each individual AI model, and All AI combined.

##### `## Analysis 1.1: Within-Group Pairwise Diversity (Remote-Clique + proposal-level mean pairwise distance)`

Step-by-step:

1. Compute within-group cosine distance matrices.
2. Summarize within-group upper-triangle distances and Remote-Clique-family group scores.
3. Compute proposal-level mean pairwise distance-to-others.
4. Use proposal-level mean distances for primary inference.
5. Compare All AI and each model against Human with Mann-Whitney U, Cliff's delta, permutation p-values, bootstrap CIs, and Holm correction.
6. Generate pairwise-distance distribution and effect-size figures.

Baseline-minimal-rephrased result:

- Human: upper-triangle mean `0.4429`; proposal mean-pairwise mean `0.4429`.
- Claude: `0.0337`; model-vs-Human Δ `-0.3670`, δ `-1.000`, MW Holm `p=6.91e-11`.
- Gemini: `0.1505`; Δ `-0.2838`, δ `-0.8261`, MW Holm `p=5.51e-08`.
- GPT-5.2: `0.3148`; Δ `-0.1546`, δ `-0.4783`, MW Holm `p=0.00131`.
- All AI: `0.1826`; Δ `-0.2685`, δ `-0.7681`, MW Holm `p=1.18e-08`, permutation Holm `p=0.000400`.
- Tables:
  - `results/tables/rephrased/minimal/diversity_remote_clique_group_summary.csv`
  - `results/tables/rephrased/minimal/diversity_pairwise_proposal_level.csv`
  - `results/tables/rephrased/minimal/diversity_pairwise_tests.csv`
- Figures:
  - `results/figures/rephrased/minimal/pairwise_diversity_by_model.png`
  - `results/figures/rephrased/minimal/pairwise_diversity_boxplot.png`

##### `## Analysis 1.2: Centroid Dispersion Metric (mean radius + Span-90)`

##### `### 1.2a Within-group Centroid Dispersion`

Step-by-step:

1. Compute each group's centroid.
2. Compute raw and leave-one-out distance from each proposal to its own group centroid.
3. Compute group-level `span_90`.
4. Compare All AI and each model against Human using leave-one-out centroid distance.
5. Plot centroid-distance distributions.

Baseline-minimal-rephrased result:

- Human centroid LOO mean `0.2665`; `span_90=0.3137`.
- Claude centroid LOO mean `0.0178`; Δ `-0.2451`, δ `-1.000`, MW Holm `p=6.91e-11`.
- Gemini mean `0.0802`; Δ `-0.1862`, δ `-0.8261`, MW Holm `p=5.51e-08`.
- GPT-5.2 mean `0.1787`; Δ `-0.0848`, δ `-0.4783`, MW Holm `p=0.00131`.
- All AI mean `0.0968`; Δ `-0.1720`, δ `-0.7681`, MW Holm `p=1.18e-08`, permutation Holm `p=0.000400`.
- Tables:
  - `results/tables/rephrased/minimal/centroid_distances.csv`
  - `results/tables/rephrased/minimal/diversity_centroid_pairwise_tests.csv`
  - `results/tables/rephrased/minimal/diversity_span90_group_summary.csv`
- Figure: `results/figures/rephrased/minimal/centroid_dispersion_by_model.png`

##### `### 1.2b: Between-Group Centroid Dispersion`

Step-by-step:

1. Compute one global centroid from all proposal embeddings.
2. Compute each proposal's cosine distance to that global centroid.
3. Summarize by Human, each AI model, and All AI.
4. Run all pairwise group comparisons with Mann-Whitney U, Cliff's delta, permutation p-values, bootstrap CIs, and Holm correction.
5. Plot global-centroid distance distributions.

Baseline-minimal-rephrased result:

- Human mean global-centroid distance `0.2926`.
- Claude mean `0.0400`; Human-minus-Claude `0.2526`, δ `0.8866`, MW Holm `p=2.46e-06`.
- Gemini mean `0.0869`; Human-minus-Gemini `0.2057`, δ `0.7051`, MW Holm `p=0.000351`.
- GPT-5.2 mean `0.1704`; Human-minus-GPT `0.1222`, δ `0.5803`, MW Holm `p=0.00543`; permutation Holm not significant (`p=0.3215`).
- All AI mean `0.0991`; Human-minus-All-AI `0.1935`, δ `0.7240`, MW Holm `p=2.27e-06`, permutation Holm `p=0.0009999`.
- Tables:
  - `results/tables/rephrased/minimal/between_group_global_centroid_distances.csv`
  - `results/tables/rephrased/minimal/between_group_global_centroid_group_summary.csv`
  - `results/tables/rephrased/minimal/between_group_global_centroid_pairwise_tests.csv`
- Figure: `results/figures/rephrased/minimal/between_group_global_centroid_dispersion.png`

##### `## Analysis 1.2c: MST Dispersion`

Step-by-step:

1. Build each group's complete cosine-distance graph.
2. Compute the minimum spanning tree.
3. Report mean MST edge length.
4. Compare AI groups against Human with permutation tests and Holm correction.
5. Plot MST dispersion.

Baseline-minimal-rephrased result:

- Human MST dispersion: `0.1126`.
- All AI MST dispersion: `0.0427`.
- Claude: `0.0241`; Gemini: `0.0643`; GPT-5.2: `0.0733`.
- All AI vs Human: difference `-0.0699`, Holm permutation `p=0.000400`.
- Claude, Gemini, and GPT-5.2 were each lower than Human after Holm correction.

Tables:

- `results/tables/rephrased/minimal/diversity_mst_group_summary.csv`
- `results/tables/rephrased/minimal/diversity_mst_pairwise_permutation.csv`

Figure:

- `results/figures/rephrased/minimal/diversity_mst_dispersion.png`

##### `## Analysis 1.2d: Sparseness (Medoid-Based Dispersion)`

Step-by-step:

1. For each group, find the medoid minimizing total within-group distance.
2. Compute mean proposal distance to the medoid as sparseness.
3. Compare All AI and each AI model against Human with the shared inference pipeline.
4. Plot medoid/sparseness distributions.

Baseline-minimal-rephrased result:

- Human sparseness: `0.3721`.
- All AI sparseness: `0.1098`.
- Claude: `0.0267`; Gemini: `0.0870`; GPT-5.2: `0.2052`.
- All AI vs Human: mean difference `-0.2640`, Cliff's delta `-0.7580` large, Holm MW `p=1.88e-08`, Holm permutation `p=0.000400`.
- Claude, Gemini, and GPT-5.2 were each lower than Human with large negative deltas.

Tables:

- `results/tables/rephrased/minimal/diversity_medoid_distances.csv`
- `results/tables/rephrased/minimal/diversity_sparseness_group_summary.csv`
- `results/tables/rephrased/minimal/diversity_sparseness_pairwise_tests.csv`

Figure:

- `results/figures/rephrased/minimal/diversity_sparseness_medoid.png`

##### `## Analysis 1.3: Nearest-Neighbor Isolation and Outlier Detection (Chamfer / NN)`

Step-by-step:

1. Compute all-by-all proposal cosine distances and set self-distances to infinity.
2. Compute each proposal's global 1-nearest-neighbor distance.
3. Compute the Chamfer/NN group summary.
4. Flag unadjusted NN outliers above the 90th percentile.
5. Compare All AI and each AI model against Human using the shared inference pipeline.
6. Summarize nearest-neighbor source composition.
7. Save both global 1-NN and mean-5NN robustness outputs.
8. Plot nearest-neighbor distributions, outlier counts, and source-composition panels.

Baseline-minimal-rephrased result:

- Human Chamfer/mean NN distance: `0.0822`.
- All AI Chamfer/mean NN distance: `0.0337`.
- Claude: `0.0237`; Gemini: `0.0432`; GPT-5.2: `0.0463`.
- All AI vs Human 1-NN: mean difference `-0.0416`, Cliff's delta `-0.6774` large, Holm MW `p=5.13e-06`, Holm permutation `p=0.000400`.
- Claude, Gemini, and GPT-5.2 were each more locally clustered than Human after Holm correction.

Tables:

- `results/tables/rephrased/minimal/nn_distances.csv`
- `results/tables/rephrased/minimal/mean_knn_distances_k5.csv`
- `results/tables/rephrased/minimal/diversity_chamfer_group_summary.csv`
- `results/tables/rephrased/minimal/diversity_nn_pairwise_tests.csv`
- `results/tables/rephrased/minimal/nearest_neighbor_source_composition.csv`

Figure:

- `results/figures/rephrased/minimal/nearest_neighbor_by_model.png`

##### `## 1.4 Visualize proposals in Embedding Space V`

Step-by-step:

1. Project full-proposal embeddings to UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
2. Plot AI points by model, Human points with funding-aware shading, group centroids, and NN outlier rings.
3. Run diagnostics explaining why visually clustered points can still be high-dimensional outliers.
4. Build a complementary t-SNE projection with `perplexity=30`, `init='pca'`, `random_state=42`.

Figures:

- `results/figures/rephrased/minimal/embedding_space_umap_2d.png`
- `results/figures/rephrased/minimal/embedding_space_tsne.png`

##### `## Analysis 1.5: Grid Entropy of Proposal Occupancy`

Step-by-step:

1. Use the deterministic PCA-2D projection.
2. Partition space into a `5 x 5` grid.
3. Compute Shannon entropy and normalized entropy from occupied grid-cell frequencies.
4. Compare AI groups against Human with permutation tests and Holm correction.
5. Plot group entropy summaries.

Baseline-minimal-rephrased result:

- Human normalized grid entropy: `0.4145`.
- All AI normalized grid entropy: `0.3320`, not significant vs Human after Holm correction (`p=0.4734`).
- Claude normalized grid entropy: `0.7494`, higher than Human, Holm permutation `p=0.00840`.
- Gemini normalized grid entropy: `0.2268`, not significant after Holm correction.
- GPT-5.2 normalized grid entropy: `0.2861`, not significant after Holm correction.

Tables:

- `results/tables/rephrased/minimal/diversity_entropy_group_summary.csv`
- `results/tables/rephrased/minimal/diversity_entropy_pairwise_permutation.csv`

Figure:

- `results/figures/rephrased/minimal/diversity_entropy_group_summary.png`

##### `# PART II: NOVELTY`

##### `## Step 1: Load Prepared Literature Corpus`

Step-by-step:

1. Load `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.
2. Extract literature abstracts and query metadata.
3. Plot articles per query and publication-year distribution.

Figure:

- `results/figures/rephrased/minimal/literature_corpus_overview.png`

##### `## Step 2: Embed Literature Corpus`

Step-by-step:

1. Use BioLinkBERT-large with `max_length=512`.
2. Load cached literature embeddings from `data/embeddings/literature/relevant_literature_embeddings.pkl` or compute them.
3. Load abstract/Section-1 proposal embeddings for proposal-to-literature comparisons.

##### `## Shared Novelty Precomputation (CAREFUL, computationally expensive)`

Step-by-step:

1. Normalize proposal and literature embedding matrices.
2. Precompute proposal-to-literature cosine distances.
3. Cache literature self-kNN distances up to `k=50`.
4. Reuse this distance matrix for ElementNovel, MeanKNN, normalized novelty, outlier flags, and nearest-literature-neighbor exports.

##### `## Step 2.5: Element Novelty Percentiles`

Step-by-step:

1. Compute ElementNovel percentile metrics at `k=0`, `1`, `5`, and `10` using local literature neighborhoods.
2. Save per-proposal ElementNovel scores.
3. Compare All AI and each AI model against Human using the shared inference pipeline and Holm correction.

Baseline-minimal-rephrased result:

- All AI was lower than Human for every ElementNovel metric.
- `element_novel_0`: All AI vs Human mean difference `-0.0267`, delta `-0.4997` large, MW Holm `p=0.00142`, permutation Holm `p=0.000900`.
- `element_novel_1`: All AI vs Human mean difference `-0.0283`, delta `-0.3774` medium, MW Holm `p=0.0181`.
- `element_novel_5`: All AI vs Human mean difference `-0.0283`, delta `-0.3598` medium, MW Holm `p=0.0305`.
- `element_novel_10`: All AI vs Human mean difference `-0.0287`, delta `-0.3535` medium, MW Holm `p=0.0347`.
- Claude and Gemini were consistently lower than Human after correction; GPT-5.2 was lower mainly for `element_novel_0` by MW Holm and was not robust by permutation Holm.

Tables:

- `results/tables/rephrased/minimal/novelty_element_percentiles.csv`
- `results/tables/rephrased/minimal/novelty_element_percentiles_pairwise_tests.csv`

Figure:

- `results/figures/rephrased/minimal/novelty_analysis_element_percentiles.png`

##### `## Step 3: Raw Novelty Scores (Mean k-NN to Literature)`

Step-by-step:

1. Compute each proposal's mean cosine distance to its nearest literature abstracts for `k=5`, `10`, `20`, and `50`.
2. Save per-proposal MeanKNN scores.
3. Compute normalized local-density novelty metrics:
   - `novelty_ratio`
   - `novelty_z`
4. Compare All AI and each AI model against Human for MeanKNN and normalized novelty metrics.

Baseline-minimal-rephrased MeanKNN result:

- All AI was lower than Human at all tested k values.
- `mean_knn_5`: All AI vs Human mean difference `-0.0282`, delta `-0.4631` medium, MW Holm `p=0.00374`, permutation Holm `p=0.000900`.
- `mean_knn_10`: All AI vs Human mean difference `-0.0279`, delta `-0.4190` medium, MW Holm `p=0.00827`, permutation Holm `p=0.000900`.
- `mean_knn_20`: All AI vs Human mean difference `-0.0282`, delta `-0.4064` medium, MW Holm `p=0.0111`.
- `mean_knn_50`: All AI vs Human mean difference `-0.0285`, delta `-0.3825` medium, MW Holm `p=0.0189`.
- Claude and Gemini were consistently lower than Human; GPT-5.2 was not significant after Holm correction.

Baseline-minimal-rephrased normalized-novelty result:

- `novelty_ratio`: All AI vs Human was not significant after Holm correction.
- `novelty_z`: All AI vs Human had permutation Holm `p=0.0132`, but MW Holm `p=0.1096`; Claude was lower than Human by both MW Holm (`p=0.0406`) and permutation Holm (`p=0.00280`).

Tables:

- `results/tables/rephrased/minimal/novelty_mean_knn_scores.csv`
- `results/tables/rephrased/minimal/novelty_mean_knn_pairwise_tests.csv`
- `results/tables/rephrased/minimal/novelty_local_density_normalized.csv`
- `results/tables/rephrased/minimal/novelty_local_density_pairwise_tests.csv`

Figures:

- `results/figures/rephrased/minimal/novelty_analysis_mean_knn.png`
- `results/figures/rephrased/minimal/novelty_analysis_local_density.png`

##### `## Step 5: Statistical Tests for Novelty Metrics`

Step-by-step:

1. Combine novelty pairwise test outputs across ElementNovel, MeanKNN, and normalized local-density metrics.
2. Display and export the unified test table.

Table:

- `results/tables/rephrased/minimal/novelty_all_pairwise_tests.csv`

##### `## Step 6: Visualize Novelty Results`

Step-by-step:

1. Plot ElementNovel percentiles.
2. Plot MeanKNN k-sensitivity.
3. Plot normalized local-density novelty.

Figures:

- `results/figures/rephrased/minimal/novelty_analysis_element_percentiles.png`
- `results/figures/rephrased/minimal/novelty_analysis_mean_knn.png`
- `results/figures/rephrased/minimal/novelty_analysis_local_density.png`

##### `## Step 7: Visualize Proposals in Literature Embedding Space`

Step-by-step:

1. Build metadata aligned to abstract-embedding order.
2. Join review/style fields from proposal metadata when available.
3. Project literature abstracts and proposal abstracts into 2D with t-SNE and UMAP.
4. Plot literature points and Human/AI proposal points.
5. Produce a publication-year-colored literature view.

Figures:

- `results/figures/rephrased/minimal/proposals_in_literature_space_tsne.png`
- `results/figures/rephrased/minimal/proposals_in_literature_space_umap.png`
- `results/figures/rephrased/minimal/proposals_in_literature_space_by_year.png`

##### `### Step 7B: Literature-Space Outliers and High-Novelty Flags`

Step-by-step:

1. Compute proposal-to-literature mean-10NN distances.
2. Flag proposals above the 90th percentile as literature-space outliers.
3. Also flag high ElementNovel-0 and high `novelty_z` proposals.
4. Test outlier prevalence against Human with Fisher exact tests and Holm correction.
5. Plot proposal-space vs literature-space outlier overlays.

Baseline-minimal-rephrased result:

- Human literature-space outlier rate for mean-10NN: `5/23 = 21.7%`.
- Claude mean-10NN outlier rate: `0/23 = 0%`, Holm Fisher `p=0.1473`.
- Gemini mean-10NN outlier rate: `2/23 = 8.7%`, Holm `p=0.8280`.
- GPT-5.2 mean-10NN outlier rate: `3/23 = 13.0%`, Holm `p=0.8280`.
- For `novelty_z` outliers, Human had `6/23 = 26.1%`; all AI model comparisons were not significant after Holm correction, though Claude vs Human had unadjusted `p=0.0216` and Holm `p=0.0647`.

Tables:

- `results/tables/rephrased/minimal/literature_space_outliers_mean_knn_k10.csv`
- `results/tables/rephrased/minimal/literature_space_outliers_element0.csv`
- `results/tables/rephrased/minimal/literature_space_outliers_z.csv`
- `results/tables/rephrased/minimal/literature_space_outlier_prevalence_tests.csv`

Figures:

- `results/figures/rephrased/minimal/proposals_in_literature_space_umap_outliers_comparison_k10.png`
- `results/figures/rephrased/minimal/proposals_in_literature_space_tsne_outliers_comparison_k10.png`

##### `## Additional Analysis: Nearest Neighbors in Literature for Every Proposal`

Step-by-step:

1. Retrieve the three nearest literature abstracts for each proposal.
2. Store proposal title, group/model, literature metadata, and distances.
3. Use this as a qualitative audit of what anchors the novelty score.

Table:

- `results/tables/rephrased/minimal/nearest_literature_neighbors_top3.csv`

##### `## Unified Proposal-Level Metric Export`

Step-by-step:

1. Merge proposal-level diversity metrics.
2. Merge group-level diversity metrics mapped down to each proposal.
3. Merge novelty continuous metrics and outlier flags.
4. Save a single proposal-level metrics table.

Baseline-minimal-rephrased result:

- `proposal_metrics_master.csv` has `92` rows and `34` columns.
- Included metric families: pairwise diversity, centroid/NN/medoid/global-centroid metrics, group Remote-Clique/Chamfer/MST/Span90/Sparseness/Grid Entropy, ElementNovel, MeanKNN, normalized novelty, and literature outlier flags.

Table:

- `results/tables/rephrased/minimal/proposal_metrics_master.csv`

##### `# PART III: THEMATIC AND CLUSTER ANALYSIS`

##### `## Analysis 3.1: Topic Modeling (LDA - Exploratory)`

Step-by-step:

1. Build normalized content text from title plus abstract.
2. Probe common unigrams and construct domain stopwords.
3. Build a `CountVectorizer` matrix with `max_features=2000`, `min_df=2`, `max_df=0.7`, English stopwords, and unigrams/bigrams.
4. Drop selected domain unigrams but keep bigrams.
5. Fit LDA with `n_topics = 3`, `doc_topic_prior=0.5`, `topic_word_prior=0.5`, `max_iter=100`, batch learning, and `random_state=42`.
6. Print topic words, perplexity, and log-likelihood.
7. Run 10 aligned stability runs.
8. Run topic-count sensitivity for `k=4..8`.

Note:

- The code and output identify three topics, but one print statement says `n_topics=5`; the actual variable is `n_topics = 3`.
- No separate topic table artifact is currently exported.

##### `## Analysis 3.2: Topic Distribution Comparison`

Step-by-step:

1. Use soft topic participation where a proposal counts for a topic if its probability is greater than `0.20`.
2. Build Human vs AI participation counts by topic.
3. Run an overall soft-topic chi-square permutation test with `10000` permutations.
4. Run per-topic Fisher exact tests with FDR correction.
5. Subsample AI to `n=23` for `1000` validation iterations.
6. Plot topic-distribution heatmap and subsampled bar plot.

Baseline-minimal-rephrased rendered result:

- Soft participation counts: Topic_1 Human `13`, AI `27`; Topic_2 Human `9`, AI `26`; Topic_3 Human `9`, AI `29`.
- Overall soft-topic chi-square statistic `0.8361`, permutation `p=0.5990`; no significant Human/AI topic-distribution difference.
- Per-topic Fisher tests found no FDR-significant topic over/under-representation (`q=0.4666`, `1.0000`, `1.0000`).
- AI subsample validation showed weak topic differences: Topic_1 significant in `27/1000` subsamples, Topic_2 and Topic_3 in `0/1000`.

Figure:

- `results/figures/rephrased/minimal/topic_distribution_comparison.png`

##### `## Analysis 3.3: Topic Coverage and Entropy`

Step-by-step:

1. Use soft topic threshold `0.20`.
2. Compute topic coverage.
3. Compute exclusive topics requiring at least `2` proposals in one group and zero in the other.
4. Run `10000` permutation tests for exclusive-topic counts.
5. Compute Shannon entropy on mean soft topic distributions.
6. Subsample AI to Human-sized samples for entropy comparisons.

Baseline-minimal-rephrased rendered result:

- Human and AI both covered `3/3` topics.
- No exclusive topics.
- Topic entropy: Human `H=1.6135`, normalized `1.0180`; AI `H=1.5987`, normalized `1.0087`.
- AI subsampled entropy: `H=1.6012 +/- 0.0282`; Human minus AI-subsample mean difference `0.0123`, two-sided `p=0.8760`.

##### `## Analysis 3.4: Cluster Composition/Segregation Analysis`

Step-by-step:

1. Fit Gaussian mixture models for candidate `k = 3..8`.
2. Use BIC as the primary selection criterion; also compute silhouette and Davies-Bouldin.
3. Fit final full-covariance GMM with `random_state=42`.
4. Summarize cluster composition by Human vs AI.
5. Compute NMI, ARI, and between/within cosine-distance ratio.
6. Run `10000` permutation tests for segregation metrics.
7. Plot k-selection and cluster diagnostics in embedding space.

Baseline-minimal-rephrased rendered result:

- Best k by BIC and silhouette: `3`.
- Cluster sizes: `[22, 19, 51]`; two clusters were Mixed and one was AI-dominated.
- NMI `0.0923`, permutation `p=0.0021`.
- ARI `0.1411`, permutation `p=0.0016`.
- Between/within distance ratio `1.2406`, permutation `p=0.0017`.

Figures:

- `results/figures/rephrased/minimal/cluster_k_selection.png`
- `results/figures/rephrased/minimal/cluster_analysis_visualization.png`

##### `### PART III Summary`

Baseline-minimal-rephrased rendered result:

- Topic distribution and topic entropy did not show a significant Human/AI difference in the rendered baseline run.
- GMM cluster/segregation analyses did show significant Human/AI semantic-region separation by NMI, ARI, and between/within distance ratio.

##### `# PART IV Style Baseline`

##### `### Exract stylistic features`

Step-by-step:

1. Extract style features from full rephrased proposal text.
2. Features include text length, sentence length, word length, type-token ratio, stopword rate, hedge rate, readability, punctuation rates, newline/bullet/header features, and group labels.
3. Save style features with titles.
4. Plot Human-vs-model style distributions.

Baseline-minimal-rephrased result:

- `style_features.csv` contains `92` proposal rows.

Table:

- `results/tables/rephrased/minimal/style_features.csv`

##### `#### Visualization: Style feature distributions by group (Human vs each AI model)`

Step-by-step:

1. Plot each extracted style feature by Human and individual AI model.
2. Use boxplots with medians/IQRs, mean diamonds, and +/- 1 SD error bars.
3. Use the plot to inspect skew, outliers, and group-level spread in style features.

Figure:

- `results/figures/rephrased/minimal/style_features_by_model_boxplots.png`

##### `### Analysis 2.3.5: Style-only baseline (can style predict source?)`

Step-by-step:

1. Predict Human vs AI using style features only.
2. Use median imputation, `StandardScaler`, and `LogisticRegression(max_iter=5000, class_weight='balanced', solver='liblinear', random_state=42)`.
3. Evaluate with 5-fold stratified CV.
4. Run a 1000-permutation AUROC test.
5. Fit the model on all rows to inspect standardized coefficients.
6. Plot fold scores and permutation null.

Baseline-minimal-rephrased rendered result:

- Style-only AUROC `0.561 +/- 0.166`.
- Balanced accuracy `0.584 +/- 0.117`.
- Permutation test observed AUROC `0.561`, null mean `0.504 +/- 0.098`, `p=0.2977`.
- The rendered notebook interprets this as weak style-only separation.

##### `#### Visualization: Style-only baseline results (CV + permutation test)`

Step-by-step:

1. Plot fold-level AUROC and balanced-accuracy scores from cross-validation.
2. Plot the permutation-test null distribution for AUROC.
3. Mark the observed AUROC to show that style-only classification is not beyond chance in this rendered baseline run.

Figure:

- `results/figures/rephrased/minimal/style_only_baseline_viz.png`

##### `### Analysis 2.3.6A: Style-controlled sensitivity via residualization`

Step-by-step:

1. Stack Human and AI embeddings.
2. Build Human/AI source indicator.
3. Use style covariates to residualize embedding-distance outcomes.
4. Test whether source remains associated with distance to centroid after linear style control.
5. Use permutation tests with `n_perm=5000`, `seed=42`.

Baseline-minimal-rephrased rendered result:

- Centroid-level source difference remained robust after style controls; AI coefficient `-0.174962`, permutation `p=0.0002`.
- Own-group centroid outcome was also robust: AI coefficient `-0.151039`, permutation `p=0.0002`.

##### `### Style-adjusted centroid dispersion (All Groups vs Human)`

Step-by-step:

1. Compute raw distance to own group centroid for Human and each AI model.
2. Residualize the centroid-distance outcome on compact style covariates: `avg_word_len`, `type_token_ratio`, `avg_sent_len_words`, `flesch_reading_ease`, and `dash_per_1k_chars`.
3. Shift residuals back to the original outcome mean.
4. Compare style-adjusted centroid distances for All AI and each AI model against Human.
5. Plot before/after centroid dispersion.

Figure:

- `results/figures/rephrased/minimal/centroid_dispersion_style_adjusted.png`

##### `### Style-adjust nearest-neighbor (NN) distances by residualizing embeddings`

Step-by-step:

1. Residualize the full embedding matrix dimension-wise on the same compact style covariates.
2. Renormalize residual embeddings.
3. Recompute all-by-all cosine distances.
4. Compute style-adjusted global 1-NN distances.
5. Flag top-10% style-adjusted NN outliers.
6. Compare All AI and each AI model against Human.

Baseline-minimal-rephrased rendered result:

- Style-adjusted NN differences became non-significant for All AI vs Human; MW `p=0.1582`, permutation `p=0.2777`.
- All AI mean style-adjusted NN distance was `0.2808` vs Human `0.2359`; Cliff's delta `0.1979` (small).
- Style-adjusted outliers: Human `2/23`, Claude `2/23`, Gemini `4/23`, GPT-5.2 `2/23`, All AI `8/69`.

Figure:

- `results/figures/rephrased/minimal/nearest_neighbor_by_model_style_adjusted.png`

##### `### Visualization: Style-adjusted NN analysis in 2D (UMAP on residual embeddings)`

Step-by-step:

1. Compare mean absolute correlations between compact style covariates and the first 10 PCA scores before and after residualization.
2. Project residual embeddings to 2D with UMAP using `n_neighbors=15`, `min_dist=0.1`, `metric='cosine'`, and `random_state=42`.
3. Plot Human, each AI model, centroids, and style-adjusted NN outliers.

Figure:

- `results/figures/rephrased/minimal/embedding_space_2d_style_adjusted.png`

##### `#### Outlier proposals (style-adjusted NN)`

Step-by-step:

1. Find proposals flagged by `outliers_adj`.
2. Retrieve metadata-aligned title, Human/AI source, model, and style-adjusted NN distance.
3. Print threshold, total outliers, source/model counts, and sorted outlier table.

##### `# Save All Proposals to a Single JSON`

Step-by-step:

1. Load `proposal_metrics_master.csv`.
2. Load `style_features.csv`.
3. Load `data/prepared/rephrased/minimal/review_scores_wide.csv` if available.
4. Match existing proposal records by `proposal_uid` and normalized title.
5. Attach metrics, style features, and review scores to each proposal record.
6. Save merged records to `results/tables/rephrased/minimal/all_proposals.json`.
7. Print sanity checks for row counts, missing master rows, family-wise missingness, and outlier-flag alignment.

Baseline-minimal-rephrased result:

- The final merged proposal JSON exists at `results/tables/rephrased/minimal/all_proposals.json`.
- The metric master table has no missingness in the main diversity/novelty metric families according to the export design.

##### Baseline-minimal-rephrased Results Summary

- Human proposals are more semantically spread than AI proposals across pairwise diversity, centroid dispersion, global-centroid distance, MST dispersion, sparseness, and nearest-neighbor isolation.
- Claude proposals are especially clustered in full-proposal embedding space; GPT-5.2 is closer to Human than Claude/Gemini on some metrics but still lower than Human on several diversity tests.
- Grid entropy is the main diversity exception: Claude has higher PCA-grid occupancy entropy than Human, while All AI is not significantly different from Human after Holm correction.
- Human proposals are more novel relative to literature than All AI on ElementNovel and MeanKNN metrics; Claude and Gemini show the strongest deficits, while GPT-5.2 is often not significant after correction.
- Literature-space outlier prevalence is higher for Human proposals descriptively, but model-vs-Human Fisher tests are not significant after Holm correction.
- Topic modeling did not find a significant Human/AI soft-topic distribution difference in the rendered baseline run, and topic entropy was also similar.
- Cluster analyses still indicate Human/AI semantic-region segregation, with significant NMI, ARI, and between/within distance-ratio permutation tests.
- Style-only classification was weak/non-significant after leakage-safe CV, so full-proposal style alone does not strongly predict source in this rendered run.
- Centroid differences persist after style controls, while NN isolation weakens after style-adjusted embedding residualization.

#### Diversity Metric Definitions Aligned to Table-3 Naming

Current implementation status for future notebook edits:

1. **Remote-Clique** (`implemented partially`)

- Current Analysis 1.1 computes upper-triangle pairwise cosine distances for descriptions and proposal-level mean distance-to-others for inference.
- To report the exact Table-3 Remote-Clique value, add `RC = (1 / N^2) * sum_i sum_j d(x_i, x_j)` explicitly and export it by group.

1. **Chamfer Distance** (`implemented for k=1`)

- Current Analysis 1.3 implements the nearest-neighbor version: `CD = (1 / N) * sum_i min_{j != i} d(x_i, x_j)`.
- Analysis 1.3-B adds a mean-5NN robustness variant, not the canonical k=1 Chamfer value.

1. **MST Dispersion** (`implemented`)

- Build a minimum spanning tree over each group's complete cosine-distance graph.
- Report mean MST edge length: `(1 / (N - 1)) * sum_{(i,j) in MST} d(x_i, x_j)`.

1. **Span** (`implemented as Span-90 group summary`)

- Current Analysis 1.2 reports mean distance to centroid and exports `diversity_span90_group_summary.csv` for percentile span.

1. **Sparseness** (`implemented`)

- Compute the group medoid `m = argmin_j sum_i d(x_i, x_j)`.
- Report `Sparseness = (1 / N) * sum_i d(x_i, m)`.

1. **Entropy (grid-based embedding occupancy)** (`implemented`)

- Project embeddings to 2D, partition into a `5 x 5` grid, compute occupancy frequencies, and report Shannon entropy plus a normalized entropy.
- Keep this distinct from the existing LDA topic entropy in Analysis 3.3.

## Compare_reviews_ncems_criteria.ipynb

#### Notebook Scope and Global Settings

Notebook title: `# PART IV QUALITY — Compare Human and AI Reviews (Style-Controlled / Rephrased)`.

Ground-truth audited notebook: `baseline(minimal)-rephrased/compare_reviews_ncems_criteria.ipynb`.

Purpose: compare Human and AI reviews in the NCEMS criteria evaluation pipeline using reviews generated on style-controlled/rephrased proposals. The rendered notebook is organized around R1 review diversity/similarity/reliability, R2 AI-evaluated proposal quality, R3 evaluator/self-preference bias, and a bias-control R2 rerun that removes AI self-evaluations.

Global settings:

- Condition label for results in this section: `baseline-minimal-rephrased`.
- `CONDITION = 'minimal'`.
- `REUSE_REVIEW_EMBEDDINGS = True`.
- Prepared review input: `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
- Review embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl`.
- Strength embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_strengths_embeddings_minimal.pkl`.
- Weakness embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_weakness_embeddings_minimal.pkl`.
- Figures: `results/figures/quality/minimal/ncems_criteria`.
- Tables: `results/tables/quality/minimal/ncems_criteria`.

Criteria evaluated:

- `Relevance_to_Emergent_Phenomena`
- `Novelty_and_Significance`
- `Rigor_of_Approach`
- `Scope_and_Timeline`
- `Synthesis_Focus`
- `Data_Identification`
- `Open_Science_Commitment`

Embedding and statistics:

- Review embeddings use `michiyasunaga/BioLinkBERT-large`, mean pooling over token embeddings with attention masks, L2 normalization, batch size `8`, and max length `512`.
- Similarity uses cosine similarity; diversity uses cosine distance.
- Pairwise score tests use Mann-Whitney U and Cliff's delta with BH-FDR correction.
- Matched proposal-level similarity/diversity tests prioritize paired Wilcoxon signed-rank tests; Mann-Whitney and Cliff's delta are sensitivity/effect-size outputs.
- Robust R2 checks use `2000` bootstrap resamples and `5000` label permutations with `seed=42`.
- Reliability reports ICC(2,1), ICC(2,k), Krippendorff's alpha where available, and Spearman rank correlations.

##### `## Condition Configuration`

Step-by-step:

1. Set the run condition to `minimal`.
2. Reuse prepared review embeddings rather than recomputing them.
3. Route all downstream table, figure, and embedding paths through the condition-specific `minimal/ncems_criteria` directories.

##### `# PART IV QUALITY — Compare Human and AI Reviews (Style-Controlled / Rephrased)`

The executed notebook compares NCEMS-quality review behavior for Human and AI reviews on style-controlled/rephrased proposals. It covers three families of analyses:

1. R1: review diversity, embedding-space structure, Human-AI similarity, and Y2 reliability.
2. R2: AI-authored proposal quality compared with Human-authored proposal quality under AI evaluation.
3. R3: evaluator effects and AI self-preference bias, followed by an R2 rerun that removes AI self-evaluations.

##### `## 0) Environment setup (run once if needed)`

The cell is a commented dependency install cell. It does not execute any analysis.

##### `## 1) Imports, paths, and constants`

Step-by-step:

1. Import file/path utilities, numerical/statistical libraries, plotting libraries, embedding/model utilities, `statsmodels`, `networkx`, and `krippendorff`.
2. Locate the project root by walking upward until `src` and `data` exist.
3. Define condition-specific input, output, figure, table, and embedding paths.
4. Create table, figure, and embedding directories if needed.
5. Define display colors for Human, Claude, Gemini, and GPT-5.2.
6. Define NCEMS criteria order and display labels.
7. Define the Human-to-NCEMS rubric mapping.
8. Define reusable metric lists, including `QUALITY_METRICS = ['overall_score'] + CRITERIA_ORDER`.

##### `## 2) Utility functions`

Step-by-step:

1. Normalize titles and compute hybrid title similarity with exact/fuzzy support.
2. Compute Cliff's delta, qualitative Cliff's delta magnitude, Mann-Whitney summaries, Benjamini-Hochberg FDR, bootstrap CIs, permutation p-values, and ICC(2,1)/ICC(2,k).
3. Compute TextBlob polarity, sentiment labels, sentiment alignment, and categorical sentiment agreement.
4. Build one-to-one Human/AI title mappings using exact normalized-title matches first, then fuzzy matches at threshold `0.70`.
5. Support embedding reuse or computation with BioLinkBERT mean pooling, attention masks, L2 normalization, batch size `8`, and max length `512`.

##### `## 3) Load prepared AI reviews`

What data:

- `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`, filtered to `review_source == 'ai'`.

Baseline-minimal-rephrased result:

- AI review rows: `276`.
- Authors: `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`, `human-y1`, `human-y2`.
- Evaluators: `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`.

##### `## 4) Load prepared human expert reviews (Y1 + Y2)`

What data:

- Same prepared review table, filtered to `review_source == 'human'`.

Baseline-minimal-rephrased result:

- Human reviews total: `85`.
- Human Y1: `47` reviews across `12` proposals.
- Human Y2: `38` reviews across `11` proposals.

##### `## 5) Proposal matching diagnostics (exact + fuzzy fallback)`

What data:

- Human Y1 reviews and AI reviews of Human-Y1 proposals.

Step-by-step:

1. Build Human and AI title tables.
2. Normalize titles.
3. Run exact normalized-title matching first.
4. Fuzzy-match remaining titles with threshold `0.70`.
5. Enforce one-to-one matches.
6. Assign stable matched keys `Y1_01` through `Y1_12`.

Baseline-minimal-rephrased result:

- Human proposals: `12`.
- AI proposals: `12`.
- Matched: `12`.
- Exact matches: `9`.
- Fuzzy matches: `3`.
- Unmatched Human proposals: `0`.
- Unmatched AI proposals: `0`.

##### `## 6) Build matched review sets, embeddings, and pair table (single source of truth)`

What data:

- Matched Human-Y1 reviews.
- Matched AI reviews of Human-Y1 proposals.
- Review text from the prepared review table.
- Prepared embeddings from `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl`.

Step-by-step:

1. Align Human-Y1 and AI-on-Human-Y1 reviews by the Section 5 mapping.
2. Ensure every row has a stable `review_uid`.
3. Load prepared review embeddings by `review_uid`.
4. Attach embeddings to aligned Human and AI review rows.
5. Compute TextBlob polarity and sentiment labels.
6. Within each matched proposal, enumerate Human-AI, Human-Human, and AI-AI review pairs.
7. For every pair, compute embedding cosine similarity, sentiment alignment, categorical sentiment agreement, and numeric agreement.
8. Retain proposal key, match method, reviewer IDs, AI model, and AI model-pair metadata.

Baseline-minimal-rephrased result:

- Matched proposals: `12`.
- Human-AI pairs: `141`.
- Human-Human pairs: `70`.
- AI-AI pairs: `36`.
- Human-AI pairs by AI model: `47` for each of Claude, Gemini, and GPT-5.2.
- AI-AI model-pair counts: `12` for each of Claude/Gemini, Claude/GPT-5.2, and Gemini/GPT-5.2.

##### `## 7) Pair count checks (expected vs observed)`

Step-by-step:

1. Count reviews per matched proposal.
2. Compute expected Human-AI, Human-Human, and AI-AI pair counts.
3. Compare expected counts with observed `pair_df` counts.

Baseline-minimal-rephrased result:

- Expected and observed totals matched exactly: Human-AI `141`, Human-Human `70`, AI-AI `36`.

##### `# R1: How does the diversity of human reviews compare to those by AI?`

The executed notebook adds a full review-diversity analysis before the similarity proxy analyses. The main estimand is proposal-conditioned within-cohort diversity: Human reviewer variation compared with AI reviewer variation for the same proposal set.

##### `## 8c) Build matched review sets for Y1 and Y2 (single source of truth)`

What data:

- Prepared merged review dataframe.
- Human-Y1 and Human-Y2 expert reviews.
- AI reviews of Human-Y1 and Human-Y2 proposals.
- Prepared review embeddings keyed by `review_uid`.

Baseline-minimal-rephrased matched cohort result:

- Human Y1: `47` reviews across `12` proposals.
- AI Y1: `36` reviews across `12` proposals.
- Human Y2: `38` reviews across `11` proposals.
- AI Y2: `33` reviews across `11` proposals.
- Y1 mapping: `12` matched, `9` exact, `3` fuzzy.
- Y2 mapping: `11` matched, `11` exact, `0` fuzzy.
- Y1 pair counts for diversity: Human-Human `70`, AI-AI `36`.
- Y2 pair counts for diversity: Human-Human `49`, AI-AI `33`.

##### `## R1-Q1) Can humans create more diverse reviews than AI?`

##### `### 8d) Review diversity metrics (proposal-conditioned; Y1 and Y2)`

What data:

- Aligned Human and AI review embeddings for Y1 and Y2.
- Cosine distance is used as the diversity distance metric.

Step-by-step:

1. For each proposal and source group, collect all review embeddings.
2. Compute within-group diversity metrics:
   - `mean_pairwise`: mean pairwise cosine distance.
   - `nn`: mean nearest-neighbor distance.
   - `centroid_loo`: leave-one-out centroid distance.
   - `global_centroid_dist`: distance to group-balanced Human/AI global centroid.
   - `medoid_dist`: distance to within-group medoid.
   - `remote_clique`: off-diagonal pairwise mean, equivalent to the Remote-Clique family metric for this review set.
   - `span90`: 90th percentile distance to centroid.
   - `mst_dispersion`: mean edge length of a minimum-spanning tree over review embeddings.
   - `sparseness`: mean distance to centroid.
3. Build Y1 and Y2 wide proposal-level tables.
4. Compare Human vs AI within each matched proposal set using paired Wilcoxon signed-rank tests.
5. Also compute Mann-Whitney U and Cliff's delta as secondary effect-size/sensitivity outputs.
6. Apply BH-FDR to Wilcoxon and Mann-Whitney p-values.
7. Attempt per-model Human-vs-AI effects; in this run the per-model table is empty because each model contributes only one review per proposal, so within-model diversity requires at least two reviews.

Baseline-minimal-rephrased result:

- Y1 wide diversity table shape: `(12, 49)`.
- Y2 wide diversity table shape: `(11, 49)`.
- Human-vs-AI test rows: `18` metric/cohort rows.
- Y1 significant after Wilcoxon FDR: `span90` (`q=0.047241`), `global_centroid_dist` (`q=0.047241`), `medoid_dist` (`q=0.047241`), and `sparseness` (`q=0.047241`), all Human greater than AI with large Cliff's deltas.
- Y1 `mean_pairwise`/`remote_clique` trended Human greater than AI but did not pass Wilcoxon FDR (`q=0.095947`).
- Y2 all nine diversity metrics were significant by Wilcoxon FDR (`q=0.000977`), all Human greater than AI, with large Cliff's deltas.

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y1_proposal_level.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y2_proposal_level.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y1_long.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y2_long.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_within_cohort_human_vs_ai_tests.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_human_vs_ai_by_model.csv` exists but has no usable per-model rows in this run.

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_y1_paired_slopes.png`
- `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_y2_paired_slopes.png`
- `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_human_vs_ai_all.png`
- `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_effects_dotplot.png`
- `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_by_model.png` may be stale/diagnostic because the notebook reported no per-model effect data for this run.

##### `### 8d-ii) Granular diversity: Strengths vs Weaknesses`

What data:

- Strength-specific review embeddings from `review_strengths_embeddings_minimal.pkl`.
- Weakness-specific review embeddings from `review_weakness_embeddings_minimal.pkl`.
- Same Y1/Y2 matched proposal cohorts.

Step-by-step:

1. Build field-specific embedding cohorts for `strengths` and `weakness`.
2. Recompute the same proposal-conditioned diversity metrics for each field.
3. Compare Human vs AI within Y1 and Y2 using paired Wilcoxon tests and Cliff's delta.
4. Plot field-level effect sizes and distributions.
5. Project strengths/weakness embeddings into a shared UMAP space.

Baseline-minimal-rephrased result:

- Strengths: Human reviews were more diverse than AI reviews on all tested metrics in both Y1 and Y2; all reported Cliff's deltas were large.
- Y1 strengths examples: `mean_pairwise` difference `0.0212`, Wilcoxon `p=0.0010`; `span90` difference `0.0127`, `p=0.0005`.
- Y2 strengths examples: `mean_pairwise` difference `0.0175`, `p=0.0098`; `nn` difference `0.0111`, `p=0.0068`.
- Weaknesses: Y1 Human reviews were more diverse than AI reviews on all tested metrics, with Wilcoxon p-values between about `0.0015` and `0.0342` and large deltas.
- Weaknesses in Y2 were weaker and mostly non-significant; for example `mean_pairwise` difference `0.0230`, `p=0.4131`, small Cliff's delta.

Figures:

- `results/figures/quality/minimal/ncems_criteria/review_diversity_strengths_vs_weakness_effect.png`
- `results/figures/quality/minimal/ncems_criteria/review_diversity_strengths_vs_weakness_boxplot.png`
- `results/figures/quality/minimal/ncems_criteria/review_embedding_space_strengths_weakness_umap.png`

##### `### 8e) Review Embedding Space`

What data:

- All aligned Y1 and Y2 Human/AI review embeddings used in R1.

Step-by-step:

1. Concatenate aligned review embeddings across Y1 and Y2.
2. Project embeddings with UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, and `random_state=42`.
3. Plot points by source/model and cohort.

Baseline-minimal-rephrased result:

- Total reviews projected: `154`.
- Y1 reviews projected: `83`.
- Y2 reviews projected: `71`.

Figure:

- `results/figures/quality/minimal/ncems_criteria/reviews_embedding_space_umap.png`

##### `## R1-Q2) How similar are AI reviews to human reviews?`

##### `## 8) Similarity proxy stats (proposal-level, model-aware, FDR-corrected)`

What data:

- Y1 `pair_df` from Sections 6-7.
- Proposal-level means for `cosine_similarity`, `sentiment_alignment`, and `categorical_agreement_num`.

Step-by-step:

1. Aggregate pair-level Human-Human, Human-AI, and AI-AI similarities to proposal-level means.
2. Run paired Wilcoxon tests for pair-type contrasts matched by proposal.
3. Run Mann-Whitney U and Cliff's delta as secondary sensitivity/effect-size summaries.
4. Apply BH-FDR to Mann-Whitney p-values.
5. Repeat Human-AI comparisons separately for each AI model.
6. Repeat AI-AI comparisons separately for each AI model pair.

Baseline-minimal-rephrased result:

- Human-AI vs Human-Human cosine similarity: Wilcoxon `p=0.909668`, Mann-Whitney `q=0.750832`, Cliff's delta `-0.083333` negligible.
- AI-AI vs Human-Human cosine similarity: Wilcoxon `p=0.063965`, Mann-Whitney `q=0.029060`, Cliff's delta `0.569444` large.
- AI-AI vs Human-AI cosine similarity: Wilcoxon `p=0.016113`, Mann-Whitney `q=0.007310`, Cliff's delta `0.736111` large.
- Human-AI by model: no model differed significantly from Human-Human after FDR on cosine similarity.
- AI-AI model pairs: Claude/Gemini cosine similarity was significant by Mann-Whitney FDR (`q=0.042414`, large delta); categorical agreement was significant for all three model pairs (`q=0.016011`).

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_overall.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_human_ai_by_model.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_ai_ai_by_model_pair.csv`

##### `### Interpretation: Similarity Proxy Statistics`

- Use paired Wilcoxon as the primary proposal-matched test. Treat Mann-Whitney and Cliff's delta as sensitivity/effect-size summaries because proposal-level rows are matched.
- High AI-AI similarity is interpreted as model-reviewer convergence or consistency, not automatically as Human alignment.

##### `#### Primary test — Paired Wilcoxon signed-rank (`wilcoxon_stat`, `wilcoxon_p_value`)`

- Tests whether the median proposal-level signed difference between paired comparison groups is zero.

##### `#### Secondary test — Mann-Whitney U (`u_stat`, `p_value`, `q_value`) — sensitivity check only`

- Retained for robustness and FDR-adjusted comparisons, but secondary to Wilcoxon for matched proposal-level contrasts.

##### `#### Effect size — Cliff's delta (`cliffs_delta`, `delta_magnitude`)`

- Reports direction and practical magnitude; positive means group 1 tends to be higher than group 2.

##### `#### Example interpretations:`

- Human-AI similarity near Human-Human supports proxy alignment; AI-AI similarity above both Human-Human and Human-AI supports reviewer convergence among AI models.

##### `## 8b) Similarity proxy visualization (proposal-level)`

Step-by-step:

1. Plot proposal-level paired slopes for Human-Human, Human-AI, and AI-AI similarity.
2. Plot Human-AI similarity by AI model.
3. Plot AI-AI similarity by model pair.

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_similarity_proxy_paired_slopes.png`
- `results/figures/quality/minimal/ncems_criteria/quality_similarity_human_ai_by_model_proposal_level.png`
- `results/figures/quality/minimal/ncems_criteria/quality_similarity_ai_ai_by_model_pair_proposal_level.png`

##### `### Interpretation: Similarity Plots`

- Use Human-Human as the inter-expert baseline, Human-AI overlap as proxy alignment, and AI-AI tightness as model consistency rather than necessarily human-like reviewing.

##### `### 8e) Rephrased review similarity analyses (Y1, Y2, combined)`

What data:

- Y1 and Y2 aligned Human-Human and AI-AI review pairs.

Step-by-step:

1. Aggregate within-cohort pairwise cosine similarity to proposal-level means for `human-y1`, `ai-y1`, `human-y2`, and `ai-y2`.
2. Plot the four groups in one distribution figure.
3. Run Kruskal-Wallis across the four groups.
4. Run all pairwise Mann-Whitney + Cliff's delta comparisons and BH-FDR.
5. Run within-cohort paired Human-vs-AI Wilcoxon tests by proposal.

Baseline-minimal-rephrased result:

- Mean pairwise cosine similarity: Human-Y1 `0.958279`, AI-Y1 `0.965502`, Human-Y2 `0.952415`, AI-Y2 `0.971167`.
- Human-Y1 vs AI-Y1: Mann-Whitney `p=0.019373`, `q=0.029060`, large negative Human-minus-AI delta; paired Wilcoxon `p=0.063965`.
- Human-Y2 vs AI-Y2: Mann-Whitney `p=0.000082`, `q=0.000489`, Cliff's delta `-1.0`; paired Wilcoxon `p=0.000977`.
- AI-Y1 vs AI-Y2: Mann-Whitney `p=0.028898`, `q=0.034678`.
- Human-Y1 vs Human-Y2 was not significant after FDR (`q=0.148086`).

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_y1y2_four_groups_values.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_y1y2_four_group_tests.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_within_cohort_paired_tests.csv`

Figure:

- `results/figures/quality/minimal/ncems_criteria/quality_review_similarity_y1y2_four_groups.png`

##### `### 8f) Inter-rater reliability (scores) for Y2 and Human-vs-AI agreement`

What data:

- Y2 aligned Human and AI quantitative NCEMS score matrices.
- Metrics: `overall_score` plus all NCEMS criteria.

Step-by-step:

1. Build Human-Y2 proposal-by-reviewer matrices.
2. Build AI-Y2 proposal-by-evaluator matrices.
3. Compute ICC(2,1), ICC(2,k), Krippendorff's alpha with interval distance, and mean pairwise Spearman for Human-Human and AI-AI matrices.
4. Compute Human-vs-AI agreement by comparing per-proposal mean Human scores with per-proposal mean AI scores.
5. Plot a reliability heatmap.
6. Plot Human-vs-AI overall-score agreement with proposal labels.

Baseline-minimal-rephrased result:

- Overall score Human-Human-Y2: `ICC2k=0.494949`, alpha `0.162021`, mean Spearman `0.227696`.
- Overall score AI-AI-Y2: `ICC2k=0.744734`, alpha `0.394553`, mean Spearman `0.890884`.
- Overall score Human-vs-AI-Y2: `ICC2k=0.780513`, alpha `0.634416`, Spearman `0.689672`, `p=0.018864`.
- Human-vs-AI agreement was also high for Open Science (`ICC2k=0.856134`, Spearman `0.860614`, `p=0.000672`) and Data Identification (`ICC2k=0.797508`, Spearman `0.723568`, `p=0.011836`).

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_human.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_ai.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_human_vs_ai.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_y2_reliability_human_ai.csv`

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_review_reliability_y2_heatmap.png`
- `results/figures/quality/minimal/ncems_criteria/quality_review_reliability_y2_human_vs_ai_scatter.png`

##### `## 8g) R1 exports (diversity + similarity + reliability)`

Baseline-minimal-rephrased exported R1 tables:

- `results/tables/quality/minimal/ncems_criteria/quality_matching_map_y1_rephrased_reviews.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_matching_map_y2_rephrased_reviews.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_pairs_y1_rephrased_reviews.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_pairs_y2_rephrased_reviews.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_y1y2_four_groups_values.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_y1y2_four_group_tests.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_similarity_within_cohort_paired_tests.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_human.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_ai.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_reliability_y2_human_vs_ai.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y1_proposal_level.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y2_proposal_level.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y1_long.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_y2_long.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_within_cohort_human_vs_ai_tests.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_review_diversity_human_vs_ai_by_model.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_y2_reliability_human_ai.csv`

##### `# R2: How are AI proposals' quality compare to humans (evaluated by AI)`

##### `## 10) Proposal-quality analysis dataset (proposal-level means, no duplicated human-all rows)`

What data:

- AI-generated reviews of Human-authored and AI-authored proposals.
- Scores are averaged to proposal-level means by proposal author.
- `human-all` is analytic only; the source proposal table keeps `human-y1` and `human-y2` separate.

Baseline-minimal-rephrased result:

- Human-Y1: `n=12`, mean overall `3.441667`.
- Human-Y2: `n=11`, mean overall `3.742424`.
- Human-all: `n=23`, mean overall `3.585507`.
- Claude-authored proposals: `n=23`, mean overall `4.008696`.
- Gemini-authored proposals: `n=23`, mean overall `3.831884`.
- GPT-5.2-authored proposals: `n=23`, mean overall `4.317391`.

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_overall_histograms_proposal_level.png`
- `results/figures/quality/minimal/ncems_criteria/quality_overall_boxplot_proposal_level.png`
- `results/figures/quality/minimal/ncems_criteria/quality_radar_criteria_proposal_level.png`

##### `### Interpretation: Proposal-Level Summary Dataset`

- Use group sizes, means, medians, and dispersion to contextualize later pairwise tests; unequal group sizes and variance affect power.

##### `### Interpretation: Quality Distribution Plots`

- The histogram, boxplot/strip plot, and radar chart are descriptive views of overall score and criterion-level score patterns before formal tests.

##### `## 11) Pairwise quality tests (MW + Cliff's delta + FDR) on proposal-level means`

Step-by-step:

1. Compare Human-Y1 vs Human-Y2 for each quality metric.
2. Compare Human-all vs each AI author group for each quality metric.
3. Run full base-group pairwise comparisons excluding synthetic `human-all`.
4. Use Mann-Whitney U, Cliff's delta, and BH-FDR within metric families.

Baseline-minimal-rephrased overall-score result in the raw evaluator pool:

- Human-all vs Claude: significant, `q=5.25e-04`.
- Human-all vs Gemini: significant, `q=0.0187`.
- Human-all vs GPT-5.2: significant, `q=1.31e-07`.

Table:

- `results/tables/quality/minimal/ncems_criteria/quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv`

##### `### Interpretation: Pairwise Quality Tests`

- Prioritize `q_value` over raw `p_value`; use Cliff's delta sign and magnitude to describe the practical direction of Human-all vs AI author-group differences.

##### `## 11b) Effect size & significance visualization`

Step-by-step:

1. Combine Human-all-vs-AI tests with Human-Y1-vs-Human-Y2 tests.
2. Plot a metric-by-comparison Cliff's delta heatmap, graying out non-significant cells.
3. Plot a Human-vs-AI effect-size dot plot where x is Cliff's delta and point size reflects FDR significance.

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_effect_size_heatmap.png`
- `results/figures/quality/minimal/ncems_criteria/quality_effect_size_dotplot.png`

##### `## 12) Non-parametric sensitivity check (OPTIONAL)`

##### `### Robust inference for key comparisons (bootstrap CI + permutation p)`

Step-by-step:

1. For each Human-all-vs-AI quality comparison, compute mean difference as `human-all minus AI`.
2. Bootstrap `2000` resamples for a 95% CI.
3. Run `5000` two-sided label permutations.
4. Apply BH-FDR to permutation p-values.

Baseline-minimal-rephrased overall-score result:

- Human-all minus Claude: mean difference `-0.423188`, CI `[-0.627609, -0.231848]`, permutation `q=0.000300`.
- Human-all minus Gemini: mean difference `-0.246377`, CI `[-0.443478, -0.063768]`, permutation `q=0.015197`.
- Human-all minus GPT-5.2: mean difference `-0.731884`, CI `[-0.927572, -0.552138]`, permutation `q=0.000300`.

Table:

- `results/tables/quality/minimal/ncems_criteria/quality_robust_bootstrap_permutation_key_comparisons.csv`

##### `### Interpretation: Robust Inference`

- Robust evidence requires the bootstrap CI to exclude `0` and the permutation-adjusted `q_value` to be significant; disagreement with Mann-Whitney marks a result as fragile or exploratory.

##### `# R3: Is there any self-preference bias in AI evaluators?`

##### `## 13) Evaluator differences (non-duplicated data only)`

What data:

- Non-duplicated AI-review rows; no synthetic `human-all`.

Baseline-minimal-rephrased result:

- Gemini evaluator: `n=92`, mean overall `4.301087`.
- Claude evaluator: `n=92`, mean overall `3.783696`.
- GPT-5.2 evaluator: `n=92`, mean overall `3.722826`.
- Kruskal-Wallis statistic `98.015853`, `p=5.20149e-22`.

Figure:

- `results/figures/quality/minimal/ncems_criteria/quality_overall_by_evaluator_clean.png`

##### `### Interpretation: Evaluator Descriptives`

- Large evaluator mean/median gaps indicate severity or leniency differences that can confound author-group quality comparisons.

##### `### Interpretation: Evaluator Difference Test`

- A significant Kruskal-Wallis test motivates self-preference and fixed-effect analyses because at least one evaluator distribution differs.

##### `## 14) AI self-preference tests (overall + criterion-level + proposal controls)`

What data:

- AI-authored proposals evaluated by AI models.
- `is_self = author == evaluator`.

Step-by-step:

1. Aggregate scores by evaluator, proposal author, and proposal.
2. Compare each evaluator's scores on its own proposals against scores on other AI models' proposals.
3. Repeat for overall score and each NCEMS criterion.
4. Use Mann-Whitney U, Cliff's delta, and BH-FDR.
5. Fit the fixed-effect regression `score ~ is_self_num * C(metric) + C(evaluator) + C(author) + C(proposal_uid)` with HC3 robust standard errors.

Baseline-minimal-rephrased overall self-preference result:

- Claude: mean self `3.878261`, mean other `3.886957`, `q=0.717336`, negligible delta.
- Gemini: mean self `4.143478`, mean other `4.530435`, `q=7.749241e-07`, large negative delta; Gemini penalized its own proposals relative to others.
- GPT-5.2: mean self `4.004348`, mean other `3.806522`, `q=3.300906e-12`, large positive delta; GPT favored its own proposals.

Criterion-level highlights:

- Claude: significant positive self effects on Rigor and Scope, significant negative self effect on Open Science.
- Gemini: significant self-penalty on overall score, Rigor, Scope, and Data Identification.
- GPT-5.2: significant positive self effects on overall score, Rigor, and Data Identification.
- Fixed effects showed strong evaluator severity/leniency structure: Gemini evaluator coefficient about `+0.4777`, GPT evaluator coefficient about `-0.0576`, and GPT author coefficient about `+0.355`.

Figures:

- `results/figures/quality/minimal/ncems_criteria/self_pref_strip_overall.png`
- `results/figures/quality/minimal/ncems_criteria/self_pref_criterion_heatmap.png`
- `results/figures/quality/minimal/ncems_criteria/self_pref_regression_forest.png`

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_self_preference_tests_overall.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_self_preference_tests_by_metric.csv`

##### `### Interpretation: Overall Self-Preference`

- `q_value < 0.05` with `mean_self > mean_other` indicates self-favoring bias; the reverse indicates self-penalization or preference for other models' proposals.

##### `### Interpretation: Criterion-Level Self-Preference`

- Criterion-level tests identify whether self-preference is concentrated in specific rubric dimensions rather than the overall score alone.

##### `## 14b) Self-preference visualization`

Step-by-step:

1. Plot overall score by `Self` vs `Other` for each evaluator model.
2. Plot a criterion-level heatmap of `mean_self - mean_other`, graying out non-significant cells.

##### `#### Do these models rate their own proosals better? How to remove that bias?`

- The notebook motivates fixed-effects regression because raw self-vs-other tests cannot separate evaluator bias from real proposal-quality differences.

##### `## 14c) Fixed-effects regression: forest plot`

Step-by-step:

1. Fit `score ~ is_self_num * C(metric) + C(evaluator) + C(author) + C(proposal_uid)` with HC3 robust standard errors.
2. Extract metric-specific net self-preference coefficients and uncertainty.
3. Plot self-favoring, other-favoring, and non-significant fixed-effect coefficients, plus evaluator severity offsets.

##### `## 19) Export tables`

Baseline-minimal-rephrased exported R2/R3 tables:

- `results/tables/quality/minimal/ncems_criteria/quality_matching_map_exact_fuzzy.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_pairs.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_overall.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_human_ai_by_model.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_ai_ai_by_model_pair.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_summary_overall_by_author_group.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_robust_bootstrap_permutation_key_comparisons.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_evaluator_overall_stats_clean.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_self_preference_tests_overall.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_self_preference_tests_by_metric.csv`

Baseline-minimal-rephrased non-exports:

- `quality_proxy_validity_metrics.csv`, `quality_proxy_rank_agreement.csv`, and `quality_proxy_icc.csv` are commented out in the executed baseline export cell and should not be treated as outputs for this notebook run.

##### `## 20) R2 Re-Run Without Self-Evaluator Scores on AI-Authored Proposals`

Bias-control rule:

- Remove AI-authored proposal reviews where `evaluator == author`.
- Keep all AI reviews of Human-authored proposals.
- Average AI-authored proposal scores over the two remaining cross-evaluators.

Baseline-minimal-rephrased result:

- Removed self-evaluation rows: `69`.
- Remaining rows: `207`.
- Each AI-authored proposal retained two evaluators.
- Human-all mean overall remained `3.585507`.
- Claude-authored mean overall became `4.073913`.
- Gemini-authored mean overall became `3.676087`.
- GPT-5.2-authored mean overall became `4.473913`.
- Human-all vs Claude remained significant: `q=2.252824e-04`, Cliff's delta `-0.652174`.
- Human-all vs Gemini became non-significant: `q=0.681584`, Cliff's delta `0.069943`.
- Human-all vs GPT-5.2 remained strongly significant: `q=1.702623e-08`, Cliff's delta `-0.992439`.
- Robust overall Human-all minus Claude: `-0.488406`, CI `[-0.698587, -0.290562]`, permutation `q=0.000300`.
- Robust overall Human-all minus Gemini: `-0.090580`, CI `[-0.288406, 0.092772]`, permutation `q=0.348930`.
- Robust overall Human-all minus GPT-5.2: `-0.888406`, CI `[-1.085525, -0.706522]`, permutation `q=0.000300`.

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_summary_overall_by_author_group_cross_eval_only.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_human_cohort_mw_cliffs_cross_eval_only.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_vs_ai_mw_cliffs_cross_eval_only.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_pairwise_mw_cliffs_all_metrics_cross_eval_only.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_robust_bootstrap_permutation_cross_eval_only.csv`

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_overall_histograms_proposal_level_cross_eval_only.png`
- `results/figures/quality/minimal/ncems_criteria/quality_overall_boxplot_proposal_level_cross_eval_only.png`
- `results/figures/quality/minimal/ncems_criteria/quality_radar_criteria_proposal_level_cross_eval_only.png`
- `results/figures/quality/minimal/ncems_criteria/quality_effectsize_heatmap_cross_eval_only.png`
- `results/figures/quality/minimal/ncems_criteria/quality_effectsize_dotplot_cross_eval_only.png`

##### Baseline-minimal-rephrased Results Summary

- Human expert reviews were consistently more embedding-diverse than AI reviews, especially in Y2 where every whole-review diversity metric passed Wilcoxon FDR.
- Human-AI review cosine similarity was not distinguishable from Human-Human similarity in the Y1 proxy analysis, but AI-AI reviews were more similar to each other than Human-AI pairs.
- Across Y1/Y2 within-cohort similarity, AI reviews were more internally similar than Human reviews, especially in Y2.
- Y2 AI-AI quantitative score reliability exceeded Human-Human reliability, while Human mean scores and AI mean scores showed meaningful agreement on overall score and several criteria.
- In raw R2 quality comparisons, all three AI author groups scored above Human-all; after removing AI self-evaluations, Claude and GPT-5.2 remained above Human-all while Gemini no longer differed significantly.
- R3 showed strong evaluator effects and model-specific self-preference behavior: Gemini self-penalized, GPT-5.2 self-favored, and Claude was mixed/negligible overall.

### Compare_reviews_novelty.ipynb

#### 5) Novelty-framework review analyses

Analyses completed:

- Proposal-quality comparisons under novelty criteria.
- Evaluator strictness/self-preference analyses.
- Bias-control rerun with self-evaluations removed.

Criteria evaluated:

- `new_question_topic_or_framing`
- `new_theory_concept_method_dataset_or_design`
- `unusual_combination_of_existing_ideas`
- `beyond_state_of_the_art`
- `credible_high_risk_high_gain`
- `unique_knowledge_generation`

Key findings:

- Raw evaluator pool overall means: Human-all `3.7645`, Claude `3.4029`, Gemini `3.6565`, GPT-5.2 `3.9935`.
- Human-all > Claude (`q=0.001252`), Human-all vs Gemini non-significant (`q=0.2799`), GPT-5.2 > Human-all (`q=0.010149`).
- Evaluator differences were very strong (Kruskal-Wallis `p=1.51e-33`) with model-dependent self-preference.
- After removing self-evaluations:
- Human-all vs Claude non-significant (`q=0.8428`).
- Human-all > Gemini (`q=1.79e-05`).
- GPT-5.2 > Human-all (`q=0.010924`).

Interpretation:

- Framework choice materially changes who appears “better”; novelty-quality conclusions are not invariant across evaluation setups.

### metric_score_relationship.ipynb

#### 6) Metric-score relationship and outlier validation (Part V)

Analyses completed:

- Proposal-level data integration (legacy run: `92 x 52`), now expanded to support unified metric exports.
- Spearman metric-score correlation analysis.
- Outlier score-comparison tests.
- Added Human-Y2 metric-score analysis block in:
  - `notebooks/templates/rephrased/metric_score_relationship.ipynb`
- Expanded semantic metric ingestion to include the new diversity + novelty families from
`proposal_metrics_master.csv` when present (with backward-compatible fallback to legacy metrics).
- Expanded AI-score and Human-Y2-score correlation analyses to use the full available semantic metric set
(new diversity metrics, new novelty metrics, and legacy semantic metrics when available).

Key findings:

- Strong negative associations between semantic-distance metrics and NCEMS-type scores were observed (example: `mi_pairwise_mean_dist` vs `relevance_to_emergent_phenomena`, `r=-0.6496`).
- Positive associations appeared with novelty-oriented criteria (example: `centroid_dist` vs `new_theory_concept_method_dataset_or_design`, `r=0.5093`).
- Outlier proposals tended to score lower on key NCEMS dimensions, but could score higher on at least one novelty criterion (`new_theory...`, `p=0.0273`).

Interpretation:

- Embedding “novelty/remoteness” aligns differently with conservative quality criteria vs novelty-emphasizing criteria, indicating a clear evaluation-tradeoff structure.

## Updated Overall Story

- Human proposals are consistently more semantically spread and isolated than AI proposals in baseline raw-space diversity metrics.
- Novelty results are nuanced: raw literature distance favors Human over some AI groups, while effects vary by model and test correction.
- Human and AI proposals occupy different semantic/topic regions, and this separation remains visible even after several robustness checks.
- Style contributes to separation, but does not fully explain all effects; centroid-level differences remain after style control while NN outlier differences weaken.
- Review outcomes are highly dependent on rubric and evaluator effects. Some AI groups score higher under NCEMS, while novelty-framework conclusions are mixed and sensitive to self-evaluation removal.
- Overall, the study supports a **tradeoff narrative** rather than a simple “AI better vs Human better” claim: semantic remoteness, rubric design, and evaluator bias jointly shape conclusions.

## UPDATE LOGS

### 2026-05-30 update: Expanded semantic metrics + Human-Y2 quantitative integration

What was updated in `metric_score_relationship.ipynb`:

- Added unified semantic-metric loading that prefers:
  - `results/tables/rephrased/minimal/proposal_metrics_master.csv`
  and falls back to metrics already present in `all_proposals.json`.
- Refactored score inputs to use prepared score artifacts directly (no in-notebook re-aggregation/writeback):
  - `data/prepared/rephrased/minimal/review_scores_wide.csv` (AI review-score means)
  - `data/prepared/rephrased/minimal/human_y2_scores_wide.csv` (Human-Y2 quantitative means)
- Expanded semantic metric families used in correlation analyses:
  - Diversity family: pairwise/centroid/global-centroid/NN/mean-5NN/medoid plus group-level
  Remote-Clique, Chamfer, MST, Span-90, Sparseness, and grid-entropy metrics.
  - Novelty family: `element_novel_{0,1,5,10}`, `mean_knn_{5,10,20,50}`, `novelty_ratio`, `novelty_z`.
  - Legacy semantic metrics are still included when present for backward compatibility.
- Updated Human-Y2 quantitative score linkage to use prepared NCEMS review table rows for
`author == human-y2`, then aggregate to proposal-level means before correlation testing.
- Ensured expanded semantic metric set is used for:
  - AI review-score relationships (NCEMS and novelty score families).
  - Human-Y2 quantitative review-score relationships.
  - AI-vs-Human-Y2 correlation difference analysis on matched Y2 human proposals.

New/updated exports (Part V):

- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_ai_scores_on_y2_human_proposals.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_diff_semantic_ai_minus_humany2_on_y2.csv`

Status note:

- Notebook logic is now updated to the expanded metric families and Human-Y2 quantitative linkage.
- Final numeric outputs should be treated as pending refresh until the notebook is re-executed end-to-end.

Related preparation/reuse updates:

- `prepare_data_for_analysis.ipynb` now saves:
  - `data/prepared/rephrased/minimal/review_scores_wide.csv`
  - `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`
  from the merged prepared review tables.
- `compare_reviews_ncems_criteria.ipynb` cohort-parallel Y1/Y2 review-similarity build now reuses the prepared merged review dataframe (`ncems_criteria_all_reviews.csv`) directly rather than reloading/reformatting raw review files.
- `compare_reviews_novelty.ipynb` now explicitly uses only the prepared merged novelty table:
  - `data/prepared/rephrased/minimal/novelty_all_reviews.csv`
  with schema checks, and does not re-load/re-merge raw novelty review JSONs inside the analysis notebook.

### 2026-05-26 update: Human-Y2 metric-score relationship expansion

What was added (mirroring existing metric-vs-AI analyses):

- Human-Y2 score ingestion via glob from rephrased directory:
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased*.csv`
- Proposal-level aggregation of Human-Y2 quantitative rubric scores.
- Mapping from Human-Y2 rubric fields to NCEMS-equivalent score fields for direct comparability.
- Spearman correlation analyses and heatmaps for:
  - Semantic metrics vs Human-Y2 scores.
  - Style metrics vs Human-Y2 scores.
- Top-correlation summaries and top-pair scatter visualizations for Human-Y2 scores.
- Direct Y2 comparison plots:
  - Correlations with AI-derived NCEMS scores vs correlations with Human-Y2 scores on the same Y2 human proposals.
  - Difference heatmap (`AI - Human-Y2`) for semantic metric-score correlations.

New exported tables from this added block:

- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_diff_ai_minus_humany2_on_y2.csv`

Status note:

- The notebook analysis section has been added and wired for Human-Y2, with outputs defined above.
- Numeric results from this newly added Human-Y2 block should be treated as pending until full notebook execution is completed in an environment with all plotting dependencies installed.

### Review Rephrasing + Notebook Path Updates (2026-05-25)

Completed and now used as the default input pipeline:

1. **Review rephrasing pipeline implemented**

- Script: `src/rephrase_reviews.py`.
- Rephrasing is now a **single-step extraction** (one API call per review), not multi-step summarize/fill.
- Extracted fields per review:
  - `rephrased_review`
  - `strengths`
  - `weakness`

1. **Stable rephrased review outputs (no timestamped run outputs)**

- Human Y1: `data/reviews/human_reviews/rephrased/human_reviews_human-y1_rephrased.csv`
- Human Y2: `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased.csv`
- AI NCEMS: `data/reviews/ai_reviews/minimal/ncems_criteria/rephrased/ncems_reviews_rephrased.json`

1. `**compare_reviews_ncems_criteria.ipynb` updated**

- Notebook path: `baseline(minimal)-rephrased/compare_reviews_ncems_criteria.ipynb`.
- AI reviews now load from the **rephrased directory** with condition-based glob:
  - `data/reviews/ai_reviews/<condition>/ncems_criteria/rephrased/ncems_reviews_rephrased*.json`
- Human reviews now load from the **rephrased directory** with glob:
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y1_rephrased*.csv`
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased*.csv`
- Review text field now uses `rephrased_review` (with compatibility fallback only if legacy naming appears).

1. **Y2 review analyses now incorporated in the notebook**

- Added notebook sections:
  - `21) Y1 + Y2 Rephrased Review Similarity (Human-Human vs AI-AI)`
  - `22) Y2 Quantitative Score Reliability (Human, AI, and Human-vs-AI)`
  - `23) Export Y2 + Y1Y2 Added Outputs`
- Added analyses include:
  - Cohort-parallel embedding similarity for `Y1` and `Y2` (using rephrased review text).
  - Proposal-level pairwise similarity for `human-human` and `ai-ai` within each cohort.
  - One direct comparison graph with four groups in a single panel:
    - `human-y1`, `ai-y1`, `human-y2`, `ai-y2`.
  - Significance testing for four-group comparison:
    - Kruskal-Wallis global test.
    - Pairwise Mann-Whitney + Cliff’s delta + BH-FDR.
    - Within-cohort paired human-vs-AI Wilcoxon tests for `Y1` and `Y2`.
  - Y2 quantitative reliability analysis:
    - Human-human reliability.
    - AI-AI reliability.
    - Human-vs-AI reliability at proposal-level means.
    - ICC(2,1), ICC(2,k), and rank-correlation summaries with heatmap/scatter visualizations.

## Analyses From Original Plan Not Yet Done (Moved Here)

### A) Generation-condition analyses not yet executed end-to-end

- Generate and analyze full proposal sets for the non-baseline conditions:
- AI with background literature condition (with fixed retrieval protocol and controlled N).
- AI with human-scientist prior-paper/persona condition.
- Side-by-side statistical comparison of these additional conditions against baseline and Human.

### B) Novelty robustness items not yet completed

- Full preplanned k-sensitivity for novelty inference across `k={5,10,20,50}` with complete inferential tables for each k (beyond current k=10 primary pipeline and targeted diagnostics).

### C) External human-review validation not yet completed

- Blinded external expert evaluation of top Human and AI proposals (planned in Part IV, item (3)).

### D) Part V planned modeling not yet completed

- Criterion-wise predictive modeling with cross-validated Ridge regressions and permutation-based R² significance (style-only vs semantic-only vs combined feature sets).
- Full planned “human vs AI outlier reward” interaction modeling (group × NN distance slope tests) as originally specified.

## Next Priority Execution Order

1. Complete non-baseline generation conditions and run the same analysis stack for direct condition-level comparison.
2. Run external blinded expert review to validate AI-review-based findings.
3. Finish Part V predictive models and outlier interaction tests to close the validation loop.
4. Pre-register final confirmatory analyses and freeze reporting tables/figures for manuscript drafting.
