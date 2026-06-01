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


| Analysis                                                                 | Main effect                                                                   | Significance (primary)                                                              | Effect size / key statistic                                                           | Status                          |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------- |
| Proposal Diversity 1.1 Pairwise (**Remote-Clique family**)               | Human > All AI diversity                                                      | MW Holm `p=1.18e-08`; permutation Holm `p=0.000400`                                 | `δ=-0.7681` (large); mean diff `AI-Human=-0.2685`                                    | Done                            |
| Proposal Diversity 1.2a Centroid dispersion                              | Human > All AI within-group centroid dispersion                               | MW Holm `p=1.18e-08`; permutation Holm `p=0.000400`                                 | `δ=-0.7681` (large); mean diff `-0.1720`                                             | Done                            |
| Proposal Diversity 1.2b Global-centroid dispersion                       | Human farther from global centroid than All AI                                | MW Holm `p=2.27e-06`; permutation Holm `p=0.0009999`                                | `δ=0.7240` (large); Human mean `0.2926`, All AI `0.0991`                             | Done                            |
| Proposal Diversity 1.2c MST dispersion                                   | Human > All AI MST dispersion                                                 | Permutation Holm `p=0.000400`                                                       | MST Human `0.1126`, All AI `0.0427`; diff `-0.0699`                                 | Done                            |
| Proposal Diversity 1.2d Sparseness                                       | Human > All AI medoid-based sparseness                                        | MW Holm `p=1.88e-08`; permutation Holm `p=0.000400`                                 | `δ=-0.7580` (large); mean diff `-0.2640`                                             | Done                            |
| Proposal Diversity 1.3 1-NN isolation (**Chamfer / NN**)                 | Human more isolated than All AI                                               | MW Holm `p=5.13e-06`; permutation Holm `p=0.000400`                                 | `δ=-0.6774` (large); Human Chamfer `0.0822`, All AI `0.0337`                         | Done                            |
| Proposal Diversity 1.5 Grid entropy                                      | All AI ~ Human; Claude > Human                                                | All AI vs Human Holm `p=0.4734`; Claude vs Human Holm `p=0.00840`                   | Normalized entropy: Human `0.4145`, All AI `0.3320`, Claude `0.7494`                 | Done                            |
| Proposal Novelty ElementNovel 0/1/5/10                                   | Human > All AI literature-relative novelty                                    | ElementNovel-0 MW Holm `p=0.00142`; ElementNovel-10 MW Holm `p=0.0347`              | ElementNovel-0 `δ=-0.4997`; ElementNovel-10 `δ=-0.3535`                              | Done                            |
| Proposal Novelty MeanKNN 5/10/20/50                                      | Human > All AI raw literature-distance novelty                                | MeanKNN-10 MW Holm `p=0.00827`; permutation Holm `p=0.000900`                       | MeanKNN-10 `δ=-0.4190`; mean diff `-0.0279`                                          | Done                            |
| Proposal Novelty normalized local density                                | Mixed; `novelty_z` supports Human > All AI by permutation, not MW             | `novelty_z` permutation Holm `p=0.0132`; MW Holm `p=0.1096`                         | `novelty_z` `δ=-0.2691` (small)                                                      | Done                            |
| Proposal Novelty Step 7B literature-space outliers                       | Human outlier prevalence higher descriptively; model tests ns after Holm      | Mean-10NN outlier Fisher Holm: Claude `p=0.1473`, Gemini/GPT `p=0.8280`             | Human `5/23`; Claude `0/23`, Gemini `2/23`, GPT `3/23`                               | Done                            |
| Topic + cluster structure (2.3.2-2.3.4)                                  | Topics not significantly different; clusters still segregate by source        | Topic permutation `p=0.5990`; NMI `p=0.0021`; ARI `p=0.0016`; B/W ratio `p=0.0017`  | NMI `0.0923`; ARI `0.1411`; B/W ratio `1.2406`; entropy two-sided `p=0.8760`          | Done                            |
| Style sensitivity (2.3.5-2.3.6)                                          | Style-only source prediction weak; centroid separation robust; NN style-sensitive | Style-only permutation `p=0.2977`; centroid permutation `p=0.0002`; style-adjusted NN MW `p=0.1582` | Style AUROC `0.561 +/- 0.166`; centroid AI coef `-0.174962`; NN `δ=0.1979` (ns)       | Done                            |
| NCEMS R1 review diversity                                                | Human reviews more diverse than AI reviews                                    | Y2 all 9 metrics Wilcoxon FDR `q=0.000977`; Y1 4/9 metrics `q=0.047241`             | Y2 mean-pairwise diff `0.0188`, `δ=1.0`; Y1 span90 diff `0.0054`                     | Done                            |
| NCEMS R1 review similarity                                               | Human-AI similarity ~ Human-Human in Y1; AI-AI more internally similar        | Human-AI vs Human-Human Wilcoxon `p=0.9097`; AI-AI vs Human-AI Wilcoxon `p=0.0161`  | AI-AI vs Human-AI cosine `δ=0.7361` (large)                                          | Done                            |
| NCEMS R1 Y1/Y2 within-cohort similarity                                  | AI reviews more internally similar than Human reviews, especially Y2          | Y2 Human vs AI Wilcoxon `p=0.000977`; MW `q=0.000489`                               | Means: Human-Y2 `0.9524`, AI-Y2 `0.9712`; `δ=-1.0`                                  | Done                            |
| NCEMS R1 Y2 score reliability                                            | AI-AI reliability > Human-Human; Human mean and AI mean agree meaningfully    | Human-vs-AI overall Spearman `p=0.0189`; Open Science `p=0.000672`                  | Overall ICC2k: Human-Human `0.4949`, AI-AI `0.7447`, Human-vs-AI `0.7805`            | Done                            |
| NCEMS quality reviews (raw evaluator pool)                               | Claude, Gemini, and GPT-5.2 score above Human-all                             | Claude `q=5.25e-04`; Gemini `q=0.0187`; GPT `q=1.31e-07`                            | Robust mean diffs Human-AI: Claude `-0.4232`, Gemini `-0.2464`, GPT `-0.7319`        | Done                            |
| NCEMS quality reviews (cross-eval rerun)                                 | GPT-5.2 and Claude > Human-all; Gemini ~ Human-all                            | GPT vs Human `q=1.70e-08`; Claude vs Human `q=2.25e-04`; Gemini `q=0.6816`          | GPT `δ=-0.9924`; Claude `δ=-0.6522`; Gemini `δ=0.0699`                               | Done                            |
| NCEMS R3 self-preference                                                 | Gemini self-penalizes; GPT self-favors; Claude negligible overall             | Gemini `q=7.75e-07`; GPT `q=3.30e-12`; Claude `q=0.7173`                            | Mean self-other: Gemini `-0.3869`; GPT `+0.1978`; Claude `-0.0087`                  | Done                            |
| Novelty-framework reviews (cross-eval rerun)                             | Mixed: GPT > Human, Human > Gemini, Claude ~ Human                            | GPT vs Human `q=0.010924`; Human vs Gemini `q=1.79e-05`; Human vs Claude `q=0.8428` | Human-GPT `δ=-0.4631`; Human-Gemini `δ=0.7788`                                        | Done                            |
| Metric-score + outlier validation                                        | Semantic remoteness penalized on NCEMS but can help novelty-specific criteria | Outlier NCEMS relevance `p<0.001`; novelty criterion (`new_theory...`) `p=0.0273`   | `r=-0.6496` (semantic vs NCEMS relevance); `r=0.5093` (centroid vs novelty criterion) | Done                            |


## Notebooks and analyses

## Compare_proposals_rephrased.ipynb


#### Notebook Scope and Global Settings

Notebook title: `# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)`.

Purpose: compare Human and AI research proposals after all proposal texts have been rephrased by `gemini-2.0-flash` into a standardized neutral academic style. The notebook states that the analyses mirror `compare_proposals_baseline.ipynb`, but all inputs are the rephrased proposal artifacts.

Global condition and paths:

- `condition = 'rephrased/minimal'`.
- Proposal inputs are loaded from prepared artifacts in `data/prepared/rephrased/minimal/`, primarily `all_proposals.json`.
- AI source directory: `data/ai-proposals/rephrased/minimal`.
- Human source directory: `data/human-proposals/rephrased/minimal`.
- Tables are written to `results/tables/rephrased/minimal`.
- Figures are written to `results/figures/rephrased/minimal`.
- Full proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Section-1/abstract embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Main-idea embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_main_idea_only.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.

Embedding model and text setting:

- Model: `michiyasunaga/BioLinkBERT-large`.
- Device: CUDA if available, otherwise CPU.
- Embedding function uses the tokenizer/model from Hugging Face, batches at `batch_size=8`, truncates/pads to `max_length=512`, and uses the final hidden state's `[CLS]` vector (`outputs.last_hidden_state[:, 0, :]`).
- Prepared full-proposal embeddings are loaded from cache when present. If the cache is missing, the notebook generates fallback embeddings and saves them to the same cache path.
- Text field: `standardized_text` from the rephrased record is used as `full_text` after stripping the five standardized section headers:
  - `SCIENTIFIC BACKGROUND AND RESEARCH QUESTION`
  - `METHODOLOGY AND ANALYTICAL APPROACH`
  - `DATA SOURCES AND SYNTHESIS PLAN`
  - `FEASIBILITY AND TIMELINE`
  - `OPEN SCIENCE AND TEAM COMPOSITION`

Shared inferential helpers:

- Distance metric for embedding analyses: cosine distance.
- `run_group_comparison(group1, group2)` returns Mann-Whitney U, Cliff's delta, permutation p-value, observed mean difference, observed median difference, and bootstrap CI.
- Default inferential settings are `n_permutations=10000`, `n_boot=5000`, `random_state=42`.
- Cliff's delta interpretation thresholds are: negligible `<0.147`, small `<0.33`, medium `<0.474`, large `>=0.474`.
- Multiple-testing correction uses Holm adjustment for Mann-Whitney and permutation p-values.
- Comparison orientation is generally `AI group - Human`; positive mean difference / positive delta means the AI group is higher than Human on that metric.

#### `# Setup and Imports`

Cells import NumPy, pandas, plotting libraries, Plotly, PyTorch, BioLinkBERT tokenizer/model utilities, cosine similarity/distance helpers, SciPy tests, and `umap-learn`. They find the project root by locating `src/` and `data/`, define the condition-specific directories above, and create all output/cache directories.

#### `## Helper Functions`

Defines:

- Color map for `Human`, `claude-opus-4-5`, `gemini-3-pro-preview`, and `gpt-5.2`.
- `retrieve_embeddings(path_to_embeddings)` for pickle loading.
- `cliffs_delta()` and `interpret_cliffs_delta()`.
- `permutation_test()` for two-sided difference in means with `10000` default permutations.
- `bootstrap_mean_diff_ci()` with `5000` default bootstrap samples.
- `run_group_comparison()` combining Mann-Whitney, Cliff's delta, permutation, and bootstrap CI.
- `apply_multiple_testing()` using `statsmodels.stats.multitest.multipletests(..., method='holm')`.
- `proposal_mean_pairwise_distances()`, which computes each proposal's mean cosine distance to all other proposals in the same group and is used for pairwise-diversity inference to avoid treating all pairwise distances as independent observations.

#### `## Load Prepared Proposal Data`

Loads `data/prepared/rephrased/minimal/all_proposals.json` if present, otherwise falls back to `results/tables/rephrased/minimal/all_proposals.json`. Each record is split into `ai_df` or `human_df` based on `is_ai`. The notebook stores title, model, cohort, source file, `standardized_text`, `abstract_text`, `main_idea`, and group labels. Expected group structure in the completed run is `23` Human proposals and `69` AI proposals, with `23` each for Claude, Gemini, and GPT-5.2.

#### `## Prepare Proposal Texts`

For both AI and Human proposals:

- Takes `standardized_text`.
- Removes standardized section-heading lines with regex.
- Stores the cleaned prose as `full_text`.
- Sets `group` to `AI` or `Human`.
- Reports average character length for the cleaned AI and Human proposal texts.

#### `## Load Prepared Full-Proposal Embeddings`

Sets `model_name = 'michiyasunaga/BioLinkBERT-large'`. The model is only loaded if a required cache is missing. The notebook loads `ai_embeddings`, `human_embeddings`, `ai_metadata`, and `human_metadata` from the full-proposal embedding cache, or computes fallback BioLinkBERT `[CLS]` embeddings from `full_text`. It also exports `proposal_metadata.csv` with proposal title and group/model labels.

#### `# PART I: DIVERSITY`

All Part I analyses use full rephrased proposal embeddings unless otherwise stated. Groups are always Human, each individual AI model, and All AI combined.

##### `## Analysis 1.1: Within-Group Pairwise Diversity`

What data:

- Full-proposal BioLinkBERT embeddings for Human proposals, each AI model's proposals, and all AI proposals pooled.

Step-by-step:

1. Compute within-group cosine distance matrices.
2. Extract only upper-triangle pairwise distances for descriptive summaries (`np.triu_indices(n, k=1)`).
3. For each group, print `N`, number of pairs, mean, median, and standard deviation.
4. Compute proposal-level pairwise diversity: for each proposal, take its mean cosine distance to all other proposals in the same group.
5. Use proposal-level pairwise means for primary inference, not raw pairwise upper-triangle distances, because pairwise distances are dependent.
6. Compare `All AI` and each AI model against Human with `run_group_comparison(..., n_permutations=10000, n_boot=5000, random_state=42)`.
7. Apply Holm correction to Mann-Whitney and permutation p-values.
8. Visualize pairwise distributions, effect sizes, bootstrap Cliff's delta CIs, ridge/violin/box plots, jittered points, mean diamonds, SD bars, and summary panels.

Primary estimand:

- Mean difference in proposal-level within-group pairwise diversity: `AI - Human`.

Export/status:

- Figures include `pairwise_diversity_by_model.png`.
- Existing compact result: Human > All AI on proposal-level pairwise diversity; All AI vs Human Holm-adjusted MW `p=1.20e-07`, Cliff's delta `δ=-0.7681`.

Table-3 metric mapping:

- This is the implemented Remote-Clique-family analysis, but the current implemented descriptive pairwise mean uses upper-triangle distances and the inferential estimand uses one proposal-level mean distance-to-others per proposal. If exact `N^2` Remote-Clique reporting is needed later, add it explicitly rather than assuming this cell already exports that exact formula.

##### `## Analysis 1.2: Centroid Dispersion Metric`

What data:

- Full-proposal BioLinkBERT embeddings for Human, each AI model, and All AI combined.

Step-by-step:

1. For each group, compute the group centroid as the mean embedding.
2. Compute cosine distance from each proposal embedding to its own group centroid.
3. Print group-level `N`, mean, median, standard deviation, and variance of centroid distances.
4. Save per-proposal centroid distances to `centroid_distances.csv` with columns including `title`, `group`, and `centroid_dist`.
5. Compare `All AI` and each AI model against Human using the shared Mann-Whitney, Cliff's delta, permutation, and bootstrap framework.
6. Apply Holm correction to Mann-Whitney and permutation p-values.
7. Visualize centroid-distance distributions with violin plots, individual proposal scatters, and group mean lines.

Primary estimand:

- Mean difference in distance to own-group centroid: `AI - Human`.

Export/status:

- Table: `results/tables/rephrased/minimal/centroid_distances.csv`.
- Figure: `centroid_dispersion_by_model.png`.
- Existing compact result: Human > All AI centroid dispersion; All AI vs Human Holm-adjusted MW `p=1.20e-07`, Cliff's delta `δ=-0.7681`.

Table-3 metric mapping:

- This is a centroid-radius / Span-related analysis, but it reports mean distance to centroid. It is not yet the planned percentile Span metric. To match Table-3 Span exactly, add `Span_90 = percentile_90(distance_to_centroid)` and report it alongside the current mean radius.

##### `## Analysis 1.2b: Between-Group Centroid Dispersion`

What data:

- Full-proposal embeddings for all Human and AI proposals.
- Group labels: Human, each AI model, and All AI (combined).

Step-by-step:

1. Build one global centroid from all embeddings stacked together (Human + AI).
2. For each proposal, compute cosine distance to that global centroid.
3. Split proposal-level distances by group: Human, each AI model, and All AI combined.
4. Print per-group summary statistics (`N`, mean, median, std, variance).
5. Run pairwise inferential comparisons between group distributions using the same pipeline as other sections (MW, Cliff's delta, permutation p, bootstrap CI, Holm correction).
6. Save per-proposal distances, per-group summaries, and pairwise test results.
7. Visualize group distance distributions and mean group dispersion.

Primary estimand:

- Difference in mean distance-to-global-centroid between groups (proposal-level), with corrected inferential statistics.

Export/status:

- Tables include:
  - `between_group_global_centroid_distances.csv`
  - `between_group_global_centroid_group_summary.csv`
  - `between_group_global_centroid_pairwise_tests.csv`
- Figure: `between_group_global_centroid_dispersion.png`.
- Compact table marks this as added, with run pending in that earlier summary.

##### `## Analysis 1.3: Nearest-Neighbor Outlier Detection (Between Group)`

What data:

- Full-proposal BioLinkBERT embeddings for all Human and AI proposals combined.

Step-by-step:

1. Use the stacked All embeddings (Human + AI) created from 1.2b
2. Build labels aligned to embedding order, preferring `ai_metadata`; fall back to `ai_df['model']` only if metadata is unavailable.
3. Compute all-by-all cosine distances and set the diagonal to infinity.
4. For each proposal, compute global 1-nearest-neighbor distance as the minimum distance to any other proposal.
5. Split 1-NN distances into Human, All AI, and per-model arrays.
6. Print per-group `N`, mean, median, minimum, and maximum NN distance.
7. Define NN outliers as proposals with 1-NN distance greater than the 90th percentile across all proposals.
8. Count outliers for Human, All AI, and each AI model.
9. Save per-proposal NN distance and outlier flag to `nn_distances.csv`, including the global threshold.
10. For each proposal, identify the nearest neighbor's group and summarize whether nearest neighbors come from the same source, Human, the same AI model, or another AI model.
11. Compare `All AI` and each AI model against Human using the shared inference framework and Holm correction.
12. Print outlier titles/authors for unadjusted NN outliers.
13. Visualize NN distance distributions, outlier prevalence, and nearest-neighbor source composition.

Primary estimand:

- Mean difference in global 1-NN distance: `AI - Human`.

Export/status:

- Table: `results/tables/rephrased/minimal/nn_distances.csv`.
- Figure: `nearest_neighbor_by_model.png`.
- Existing compact result: Human > All AI 1-NN isolation; All AI vs Human Holm-adjusted MW `p=5.13e-06`, Cliff's delta `δ=-0.6774`; Human outlier prevalence `30.4%` vs All AI `4.3%`.

Table-3 metric mapping:

- This is the implemented Chamfer/nearest-neighbor-family analysis for `k=1`: group mean of `min_{j != i} d(x_i, x_j)`.

##### `### Visualize proposals in Embedding Space V`

What data:

- Full-proposal embeddings and unadjusted NN outlier flags.

Step-by-step:

1. Reduce the combined full-proposal embedding matrix to 2D with UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
2. Plot AI points by model, Human points on top, and mark outliers with a magenta ring.
3. Add group centroids as `X` markers.
4. Run a diagnostic comparing actual high-dimensional NN outliers to apparent remoteness in UMAP space; the notebook computes distance from the UMAP plot center and uses an 80th-percentile UMAP remoteness threshold for this descriptive check.
5. Create an alternative t-SNE projection using `n_components=2`, `perplexity=30`, `init='pca'`, and `random_state=42`.

Interpretation rule:

- These plots are descriptive only. The notebook explicitly checks that apparent 2D remoteness is not the same thing as high-dimensional NN outlier status.

##### `## Analysis 1.3-B: Mean k-NN Outlier Detection (k=5)`

What data:

- Full-proposal embeddings for all Human and AI proposals combined.

Step-by-step:

1. Set `k_mean_nn = 5`.
2. Compute all-by-all cosine distances with diagonal set to infinity.
3. For each proposal, find its five nearest neighbors and compute the mean of those five distances.
4. Define mean-kNN outliers as proposals with mean-5NN distance greater than the 90th percentile.
5. Compare overlap between original 1-NN outliers and mean-5NN outliers when the original variables are in scope.
6. Save per-proposal mean-5NN distances and outlier flags to `mean_knn_distances_k5.csv`.
7. Visualize mean-5NN outliers in UMAP (`n_neighbors=15`, `min_dist=0.1`, `metric='cosine'`, `random_state=42`) and t-SNE (`perplexity=30`, `random_state=42`) projections.

Purpose:

- Robustness check for local isolation, reducing sensitivity to a single nearest neighbor.

#### `# PART II: NOVELTY`

All Part II analyses compare proposal embeddings against the literature embedding corpus.

##### `## Step 1: Load Literature Corpus`

What data:

- Literature corpus metadata and abstracts from the prepared literature artifact associated with `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Completed run summary reports `n=39538` literature abstracts with dates from `2010-01-01` to `2026-05-25`.


Figure:

- `literature_corpus_overview.png`.

##### `## Step 2: Embed Literature Corpus`

Step-by-step:

1. Use the same BioLinkBERT-Large model as the proposal embeddings.
2. Embed literature abstracts with truncation to 512 tokens.
3. Load cached literature embeddings if present; otherwise compute and save them.
4. Report literature embedding matrix shape.

Model setting:

- Same `michiyasunaga/BioLinkBERT-large`, `[CLS]`, `max_length=512` pipeline used for proposals.

##### `## Step 3: Compute Novelty Scores`

The code cell immediately after Step 2 computes the raw novelty scores.

Step-by-step:

1. Set `k = 10`.
2. For each proposal embedding, compute cosine distances to all literature embeddings.
3. Find the 10 nearest literature abstracts.
4. Define raw novelty as mean cosine distance to the 10 nearest literature neighbors.
5. Compute raw novelty separately for Human, All AI, and each AI model.
6. Store nearest-neighbor indices for later normalization and nearest-literature export.

Primary metric:

- `raw_novelty = mean distance to k=10 nearest literature abstracts`; higher means farther from existing literature.

##### `## Step 5: Statistical Tests for Novelty`

Step-by-step:

1. Use raw novelty scores from the k=10 proposal-to-literature analysis.
2. Compare `All AI` and each AI model against Human with `run_group_comparison(..., n_permutations=10000, n_boot=5000, random_state=42)`.
3. Apply Holm correction to Mann-Whitney and permutation p-values.
4. Print effect direction, Cliff's delta interpretation, mean difference, bootstrap CI, and corrected p-values.

Primary estimand:

- Mean difference in raw novelty score: `AI - Human`.

Existing compact result:

- Human raw novelty mean `0.1303`; All AI `0.0999`; Claude `0.0898`; Gemini `0.1000`; GPT-5.2 `0.1098`.
- Claude vs Human remains significant after Holm (`p=0.0197`), while All AI vs Human is not significant after Holm (`p=0.1069`).

##### `## Step 6: Visualize Novelty Results`

Step-by-step:

1. Build effect-size annotations from Step 5 results.
2. Visualize novelty score distributions by group.
3. Annotate each AI group against Human with Cliff's delta, effect-size class, and Holm-adjusted p-value.

Figure:

- `novelty_analysis.png`.

##### `## Step 7: Visualize Proposals in Literature Embedding Space`

Step-by-step:

1. Combine literature embeddings and proposal embeddings into a shared projection input.
2. Create a t-SNE projection with `n_components=2`, `perplexity=30`, `init='pca'`, `random_state=42`.
3. Create a UMAP projection with `n_neighbors=20`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
4. Plot literature points and proposal points by source/model in the shared 2D literature space.
5. Plot a publication-year-colored literature view to inspect whether proposal positions align with temporal regions of the corpus.

Interpretation rule:

- These projections are descriptive; high-dimensional proposal-to-literature distances remain the primary novelty/outlier metric.

##### `### Step 7B: Recompute Literature-Space Outliers (proposal -> literature, mean k-NN)`

Step-by-step:

1. Set `k_lit_out = 10`.
2. Compute each proposal's mean cosine distance to its 10 nearest literature embeddings.
3. Define literature-space outliers as proposals above the 90th percentile of mean-10NN proposal-to-literature distance.
4. Save per-proposal outlier flags and distances to `literature_space_outliers_mean_knn_k10.csv`.
5. Save group summaries to `literature_space_outlier_summary_k10.csv`.
6. Compare mean-10NN literature distance for All AI and each AI model against Human using the shared inference framework.
7. Save inferential stats to `literature_space_mean_knn_stats_k10.csv`.
8. Test outlier prevalence using Fisher exact tests, with multiple-testing correction, and save to `literature_space_outlier_prevalence_tests_k10.csv`.
9. Visualize group distributions, the 90th-percentile threshold, outlier prevalence, and overlays comparing proposal-space outliers with literature-space outliers.

Primary metric:

- `mean_lit_nn_dist_k10`: mean distance from proposal to 10 nearest literature abstracts.

Existing compact result:

- Literature-space outlier prevalence: Human `26.1%` vs All AI `5.8%`; All AI vs Human Fisher Holm `p=0.0562`.

##### `## Additional Analysis: Nearest Neighbors in Literature for Every Proposal`

Step-by-step:

1. Set `N_LIT_NEIGHBORS = 3`.
2. For each Human and AI proposal, retrieve the three nearest literature abstracts using the proposal-to-literature distance matrix.
3. Store nearest literature metadata and distances for inspection.
4. Save or display nearest-literature records per proposal.

Purpose:

- Qualitative audit of what literature items anchor each proposal's raw novelty score.

##### Unnumbered export cell: `novelty_scores_from_literature.csv`

Step-by-step:

1. Build one row per proposal with `title`, `group`, and `raw_novelty`.
2. Compute top-10% threshold for raw novelty.
3. Add `is_most_novel_raw`.
4. Save `results/tables/rephrased/minimal/novelty_scores_from_literature.csv`.
5. Print the top 10% most novel proposals.

Sanity check:

- Later JSON export maps `metrics.is_literature_outlier` from Step 7B, preferring the k=10 table.

#### `# PART III: THEMATIC AND CLUSTER ANALYSIS`

##### `## Analysis 3.1: Topic Modeling (LDA - Exploratory)`

What data:

- Normalized content text (`title + abstract`) rather than full formatted proposal text, to reduce formatting/template confounding.

Step-by-step:

1. Build a unigram probe with `CountVectorizer(stop_words='english', ngram_range=(1, 1), min_df=2, max_df=1.0, max_features=5000)` to identify domain unigrams.
2. Build the main document-term matrix with `CountVectorizer(max_features=2000, min_df=2, max_df=0.7, stop_words='english', ngram_range=(1, 2))`.
3. Drop selected domain unigram stopwords while preserving bigrams.
4. Fit LDA with `n_topics = 3` using `LatentDirichletAllocation(n_components=3, doc_topic_prior=0.5, topic_word_prior=0.5, random_state=42)`.
5. Compute document-topic probabilities, dominant topic, and dominant-topic probability.
6. Print top words per topic and model perplexity.
7. Run topic stability validation with 10 random seeds, aligning topics and summarizing word overlap/cosine similarity.
8. Run topic-count sensitivity for `k = 4..8`, reporting perplexity and source distribution diagnostics.

Note:

- One summary print statement still says `n=5 topics`, but the actual code sets `n_topics = 3`.

##### `## Analysis 3.2: Topic Distribution Comparison`

Step-by-step:

1. Use soft topic participation, where a proposal participates in a topic if its topic probability is greater than `0.20`.
2. Build Human vs AI soft participation counts for each topic.
3. Compute an overall soft chi-square statistic.
4. Run a label-permutation test with `n_permutations = 10000`.
5. Run per-topic Fisher exact tests and apply FDR correction.
6. Run subsample validation by repeatedly subsampling AI to `n=23` to match the Human sample size; repeat `1000` times in the printed validation cell and `500` times for figure error bars.
7. Visualize topic distribution as a heatmap and bar plot.

Primary estimand:

- Whether Human and AI proposals have different soft topic-participation distributions.

Existing compact result:

- Rendered baseline result: soft-topic permutation chi-square `p=0.5990`; no per-topic Fisher test was significant after FDR.

##### `## Analysis 3.3: Topic Coverage and Entropy`

Step-by-step:

1. Use the same soft topic threshold `0.20`.
2. Compute topic coverage: number of topics with at least one proposal above 20% topic probability.
3. Compute exclusive topics: topics where one group has at least `min_count=2` proposals above threshold and the other group has zero.
4. Use permutation tests (`n_perm = 10000`) for exclusivity counts.
5. Compute topic entropy from each group's soft topic distribution.
6. Compare AI and Human entropy, including subsampling AI to Human-sized samples where applicable.

Primary estimands:

- Coverage parity, exclusive-topic counts, and entropy of topic participation.

Existing compact result:

- Human `3/3` and AI `3/3` topic coverage; no exclusive topics; entropy Human `0.5470` vs AI `1.5990`.

##### `## Analysis 3.4: Cluster Composition/Segregation Analysis`

What data:

- Full-proposal BioLinkBERT embeddings.

Step-by-step:

1. Load or reuse Human and AI embeddings.
2. Fit Gaussian mixture models over candidate `k_values = [3, 4, 5, 6, 7, 8]`.
3. For each k, compute silhouette score, Davies-Bouldin score, and BIC.
4. Select `best_k` using BIC as the primary criterion.
5. Fit final `GaussianMixture(n_components=best_k, covariance_type='full', random_state=42)`.
6. Assign clusters and print cluster sizes.
7. Summarize cluster composition by Human/AI source.
8. Classify cluster dominance using Human baseline prevalence: Human-dominated if `pct_human > 60`, AI-dominated if `pct_human < 15`, otherwise Mixed.
9. Compute segregation metrics:
  - Normalized Mutual Information (NMI) between cluster label and Human/AI source.
  - Adjusted Rand Index (ARI) between cluster label and Human/AI source.
  - Between-source vs within-source cosine-distance ratio.
10. For NMI, ARI, and distance ratio, run permutation tests with `n_perm_seg = 10000`.
11. Visualize clusters with UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
12. Print a comprehensive Part III summary.

Existing compact result:

- Rendered baseline result: NMI `0.0923` (`p=0.0021`), ARI `0.1411` (`p=0.0016`), between/within ratio `1.2406` (`p=0.0017`).

##### `### PART III Summary`

Step-by-step:

1. Print the topic-modeling setup and identified topics.
2. Print the overall topic-distribution permutation result and per-topic FDR-corrected Fisher results.
3. Print topic coverage, exclusive-topic diagnostics, and entropy results.
4. Print cluster-analysis setup and segregation results.
5. Summarize Part III as a combined thematic/cluster evidence block.

#### `# PART IV Style Baseline`

Purpose stated in notebook: before interpreting embedding distances, clustering segregation, or topic separation as conceptual differences, quantify how much purely stylistic signal can separate Human vs AI.

##### `### Exract stylistic features`

What data:

- Full rephrased proposal text (`full_text`), Human rows first and AI rows second.

Step-by-step:

1. Tokenize words with a lightweight regex.
2. Split sentences with punctuation/newline rules.
3. Count syllables heuristically.
4. Compute Flesch Reading Ease and Flesch-Kincaid grade.
5. Extract style features including:
  - `n_words`, `n_chars`, `n_sents`
  - average word length
  - average sentence length in words
  - type-token ratio
  - stopword rate
  - hedge rate based on a fixed hedge-word/phrase set
  - readability measures
  - punctuation rates per 1k characters for commas, semicolons, colons, dashes, parentheses, quotes, newlines, and bullets
  - header-line counts and related formatting features
6. Build `style_df` with `group` and `is_ai`.
7. Save `style_features.csv` with titles prepended.
8. Visualize style feature distributions by Human and each AI model.

Export:

- `results/tables/rephrased/minimal/style_features.csv`.

##### `#### Visualization: Style feature distributions by group (Human vs each AI model)`

Step-by-step:

1. Reconstruct per-model labels aligned to `style_df` order: Human rows first, then AI rows in `ai_df['model']` order.
2. Plot compact interpretable style features across Human and each AI model.
3. Use boxplots with median/IQR, whiskers, mean diamonds, and standard-deviation bars.
4. Print mean, median, and standard deviation summaries by group.

##### `### Analysis 2.3.5: Style-only baseline (can style predict source?)`

Step-by-step:

1. Use all style columns except `group` and `is_ai` as predictors.
2. Predict `is_ai`.
3. Pipeline: median imputation, `StandardScaler`, `LogisticRegression(max_iter=5000, class_weight='balanced', solver='liblinear', random_state=42)`.
4. Cross-validation: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`.
5. Score with AUROC and balanced accuracy.
6. Run permutation test with `n_permutations=1000`, AUROC scoring, `n_jobs=-1`, `random_state=42`.
7. Fit the same pipeline on all data for coefficient interpretation.
8. Print top 15 standardized coefficients by absolute value, plus top AI-like and Human-like features.
9. Visualize CV fold scores and permutation null distribution.

Existing compact result:

- Rendered baseline result: style-only classifier AUROC `0.561 ± 0.166`, balanced accuracy `0.584 ± 0.117`, permutation `p=0.2977`.

##### `#### Visualization: Style-only baseline results (CV + permutation test)`

Step-by-step:

1. Plot fold-level AUROC and balanced-accuracy distributions from 5-fold cross-validation.
2. Plot the AUROC permutation-test null distribution from 1000 label shuffles.
3. Mark chance AUROC `0.5` and the observed AUROC.
4. Save the figure to `style_only_baseline_viz.png`.

##### `### Analysis 2.3.6A: Style-controlled sensitivity via residualization`

Step-by-step:

1. Load full-proposal embeddings if not already in memory.
2. Stack Human and AI embeddings.
3. Build source indicator `group` where Human is `0` and AI is `1`.
4. Use all style features except `group` and `is_ai` as covariates in this broad residualization cell.
5. Standardize covariates.
6. Define embedding-derived outcomes:
  - distance to overall centroid
  - distance to own Human/AI group centroid
7. Fit ordinary least squares models with intercept, source indicator, and style covariates.
8. Extract the source coefficient after controlling for style.
9. Use permutation tests with `n_perm=5000`, `seed=42` for source coefficients.

Primary purpose:

- Check whether Human/AI embedding-distance outcomes remain source-associated after linear style adjustment.

Existing compact result:

- Centroid-level difference remains robust after style controls; AI coefficient `-0.174962`, permutation `p=0.0002`.

##### `### Style-adjusted centroid dispersion (All Groups vs Human)`

Step-by-step:

1. Align labels as Human first, then AI model labels.
2. Compute raw distance-to-own-group-centroid for Human and each AI model.
3. Residualize centroid-distance outcome on a compact style covariate set:
  - `avg_word_len`
  - `type_token_ratio`
  - `avg_sent_len_words`
  - `flesch_reading_ease`
  - `dash_per_1k_chars`
4. Shift residuals back to the original outcome mean.
5. Compare style-adjusted centroid distances for All AI and each AI model against Human.
6. Use Mann-Whitney, Cliff's delta, and a custom two-sided permutation test with `n_perm=10000`, `seed=42`.
7. Visualize unadjusted vs style-adjusted centroid dispersion.

Primary estimand:

- Mean difference in style-adjusted distance to own-group centroid: `AI - Human`.

##### `### Style-adjust nearest-neighbor (NN) distances by residualizing embeddings`

Step-by-step:

1. Stack Human and AI full-proposal embeddings.
2. Align per-row model/source labels using metadata when possible.
3. Use compact style covariates:
  - `avg_word_len`
  - `type_token_ratio`
  - `avg_sent_len_words`
  - `flesch_reading_ease`
  - `dash_per_1k_chars`
4. Standardize covariates.
5. Residualize the embedding matrix dimension-wise using OLS.
6. Renormalize residual embeddings.
7. Recompute all-by-all cosine distances on residual embeddings.
8. Compute style-adjusted global 1-NN distance for every proposal.
9. Define style-adjusted NN outliers as the top 10% by style-adjusted NN distance.
10. Compare All AI and each AI model against Human using Mann-Whitney, Cliff's delta, and permutation tests.
11. Visualize style-adjusted NN distance distributions and outlier counts.

Primary estimand:

- Mean difference in style-adjusted 1-NN distance: `AI - Human`.

Existing compact result:

- Style-adjusted NN differences become non-significant for All AI vs Human; MW `p=0.1582`, permutation `p=0.2777`.

##### `### Visualization: Style-adjusted NN analysis in 2D (UMAP on residual embeddings)`

Step-by-step:

1. Recompute compact style covariates.
2. Compare mean absolute correlation between style covariates and the first 10 PCA scores before and after residualization.
3. Project residual embeddings to 2D with UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
4. Plot Human, per-model AI, group centroids, and style-adjusted NN outliers.

Purpose:

- Visual audit that style residualization weakened linear style association with embeddings and changed/retained outlier structure.

##### `#### Outlier proposals (style-adjusted NN)`

Step-by-step:

1. Find proposal indices flagged by `outliers_adj`.
2. Retrieve style-adjusted NN distance from `nn_distances_adj` or recompute from residual embeddings if necessary.
3. Use metadata-aligned titles and model/source labels.
4. Print sorted outlier table, threshold, total outliers, and outliers by source/model.

#### `# Save All Proposals to a Single JSON`

Step-by-step:

1. Load metric tables:
  - `centroid_distances.csv`
  - `nn_distances.csv`
  - `novelty_scores_from_literature.csv`
  - `style_features.csv`
  - `review_scores_wide.csv`
2. Load literature-space outlier table, preferring `literature_space_outliers_mean_knn_k10.csv` and falling back to k=5 only for backward compatibility.
3. Build title-normalized lookup dictionaries.
4. Add in-memory proposal-level pairwise diversity metrics when available.
5. Merge original proposal metadata, rephrased text, diversity metrics, novelty metrics, style metrics, literature outlier flags, and review scores into records.
6. Save combined records to `results/tables/rephrased/minimal/all_proposals.json`.
7. Print metrics coverage and a sanity check that `metrics.is_literature_outlier` matches the raw top-10% novelty flag when both are available.

Purpose:

- Produce a single proposal-level JSON artifact for downstream metric-score validation and cross-notebook integration.

#### Baseline(minimal)-rephrased Rendered Notebook Cell-by-Cell Audit

This subsection is the source-of-truth plan for the rendered notebook at `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb`. Numeric results come from the notebook's persisted cell outputs, with exported tables used to confirm table/figure paths.

Actual run settings and data:

- Notebook path: `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb`.
- Prepared proposals: `data/prepared/rephrased/minimal/all_proposals.json`.
- Output proposal JSON: `results/tables/rephrased/minimal/all_proposals.json`.
- Proposal count in exported metric tables: `92` total, with `23` Human, `23` Claude, `23` Gemini, and `23` GPT-5.2 proposals.
- Main table directory: `results/tables/rephrased/minimal`.
- Main figure directory: `results/figures/rephrased/minimal`.
- Full-proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Abstract/Section-1 embedding cache for literature comparisons: `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.

##### `# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)`

Purpose:

1. Compare semantic diversity and isolation of Human vs AI proposals after style-controlled rephrasing.
2. Compare proposal novelty against an external literature corpus.
3. Compare Human/AI thematic structure and cluster segregation.
4. Quantify residual style signal and run style-adjusted robustness checks.
5. Merge proposal, diversity, novelty, style, and review-score metrics into a single JSON.

##### `# Setup and Imports`

Step-by-step:

1. Import plotting, embedding, statistical, NLP, dimensionality reduction, and utility libraries.
2. Set seaborn/matplotlib styles.
3. Locate project root and define condition-specific prepared-data, embedding, table, and figure paths.
4. Create output directories.

##### `## Helper Functions`

Step-by-step:

1. Define group colors.
2. Load pickle embeddings.
3. Compute Cliff's delta and delta magnitude.
4. Run two-sided permutation tests for mean differences with default `10000` permutations.
5. Bootstrap mean-difference confidence intervals with default `5000` resamples.
6. Combine Mann-Whitney U, Cliff's delta, permutation p-value, observed mean/median differences, and bootstrap CI in `run_group_comparison`.
7. Apply Holm correction to Mann-Whitney and permutation p-values.
8. Compute proposal-level mean pairwise distances so inferential tests use one value per proposal rather than dependent raw pairwise distances.

##### `## Load Prepared Proposal Data`

Step-by-step:

1. Load prepared proposal records from `data/prepared/rephrased/minimal/all_proposals.json`, with fallback to `results/tables/rephrased/minimal/all_proposals.json`.
2. Split records into Human and AI dataframes using `is_ai`.
3. Preserve title, model, cohort, source file, standardized text, abstract text, main idea, and group labels.

Actual result:

- Exported metric artifacts contain `23` Human proposals and `69` AI proposals.
- AI proposals are balanced: `23` Claude, `23` Gemini, `23` GPT-5.2.

##### `## Load Prepared NCEMS Reviews`

Step-by-step:

1. Load `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
2. Harmonize title/proposal keys for proposal-level merge.
3. Prepare review ranking, funding, and proposal-level score fields for later metadata joins.

Downstream use:

- The shared precomputation cell merges proposal-level review ranking/funding into `proposal_meta`.
- The final JSON merge also reads `data/prepared/rephrased/minimal/review_scores_wide.csv`.

##### `## Prepare Proposal Texts`

Step-by-step:

1. Use each record's `standardized_text`.
2. Remove standardized rephrasing section headers.
3. Save stripped text as `full_text`.
4. Attach `group = Human` or `AI`.
5. Keep AI model labels for per-model analyses.

##### `## Load Prepared Full-Proposal Embeddings`

Step-by-step:

1. Set embedding model to `michiyasunaga/BioLinkBERT-large`.
2. Load cached full-proposal embeddings when available.
3. If missing, compute fallback BioLinkBERT `[CLS]` embeddings from `full_text` with truncation to `512` tokens.
4. Load/retain `ai_embeddings`, `human_embeddings`, `ai_metadata`, and `human_metadata`.
5. Save proposal metadata.

Table:

- `results/tables/rephrased/minimal/proposal_metadata.csv`

##### `## Shared Distance-Matrix Precomputation`

Step-by-step:

1. Build canonical proposal metadata in embedding order.
2. Merge review ranking/funding fields.
3. Normalize and stack all full-proposal embeddings.
4. Precompute the proposal-proposal cosine distance matrix.
5. Save cached proposal metadata, distance matrix, and deterministic PCA-2D reference coordinates.

Tables:

- `results/tables/rephrased/minimal/cached/proposal_meta.csv`
- `results/tables/rephrased/minimal/cached/proposal_distance_matrix.npy`
- `results/tables/rephrased/minimal/cached/proposal_pca2d.npy`

##### `# PART I: DIVERSITY`

All diversity analyses use full rephrased proposal embeddings and compare Human, each AI model, and All AI.

##### `## Analysis 1.1: Within-Group Pairwise Diversity (Remote-Clique + proposal-level mean pairwise distance)`

Step-by-step:

1. For each group, compute within-group cosine distances.
2. Compute the Remote-Clique-family group summary from all within-group distances.
3. Compute each proposal's mean distance to other proposals in the same group.
4. Use proposal-level mean pairwise distance for inference.
5. Compare All AI and each AI model against Human with Mann-Whitney U, Cliff's delta, permutation p-values, bootstrap CIs, and Holm correction.
6. Plot pairwise distributions, effect sizes, ridge/violin/box distributions, and summary panels.

Actual result:

- Human upper-triangle mean pairwise distance: `0.4429`.
- All AI upper-triangle mean pairwise distance: `0.1826`.
- Claude: `0.0337`; Gemini: `0.1505`; GPT-5.2: `0.3148`.
- All AI vs Human proposal-level test: mean difference `-0.2685`, Cliff's delta `-0.7681` large, Holm MW `p=1.18e-08`, Holm permutation `p=0.000400`.
- Claude, Gemini, and GPT-5.2 were each less diverse than Human; all three model-vs-Human contrasts had large negative Cliff's deltas.

Tables:

- `results/tables/rephrased/minimal/diversity_remote_clique_group_summary.csv`
- `results/tables/rephrased/minimal/diversity_pairwise_proposal_level.csv`
- `results/tables/rephrased/minimal/diversity_pairwise_tests.csv`

Figures:

- `results/figures/rephrased/minimal/pairwise_diversity_by_model.png`
- `results/figures/rephrased/minimal/pairwise_diversity_boxplot.png`

##### `## Analysis 1.2: Centroid Dispersion Metric (mean radius + Span-90)`

##### `### 1.2a Within-group Centroid Dispersion`

Step-by-step:

1. Compute each group's centroid.
2. Compute each proposal's cosine distance to its own group centroid.
3. Also compute leave-one-out centroid distances for proposal-level inference.
4. Compare All AI and each AI model against Human with the shared inference pipeline.
5. Plot centroid-distance distributions.

Actual result:

- All AI vs Human leave-one-out centroid dispersion: mean difference `-0.1720`, Cliff's delta `-0.7681` large, Holm MW `p=1.18e-08`, Holm permutation `p=0.000400`.
- Claude vs Human: mean difference `-0.2451`, delta `-1.0`, Holm MW `p=6.91e-11`.
- Gemini vs Human: mean difference `-0.1862`, delta `-0.8261`, Holm MW `p=5.51e-08`.
- GPT-5.2 vs Human: mean difference `-0.0848`, delta `-0.4783`, Holm MW `p=0.00131`; permutation Holm `p=0.10049`.

Tables:

- `results/tables/rephrased/minimal/centroid_distances.csv`
- `results/tables/rephrased/minimal/diversity_centroid_pairwise_tests.csv`
- `results/tables/rephrased/minimal/diversity_span90_group_summary.csv`

Figure:

- `results/figures/rephrased/minimal/centroid_dispersion_by_model.png`

##### `### 1.2b: Between-Group Centroid Dispersion`

Step-by-step:

1. Compute one global centroid from all Human and AI proposal embeddings.
2. Compute each proposal's distance to that global centroid.
3. Summarize distances by Human, each AI model, and All AI.
4. Run all pairwise group comparisons with Mann-Whitney, Cliff's delta, permutation p-values, bootstrap CIs, and Holm correction.
5. Plot global-centroid distance distributions and summaries.

Actual result:

- Human mean distance to global centroid: `0.2926`.
- All AI mean distance: `0.0991`.
- Claude mean: `0.0400`; Gemini mean: `0.0869`; GPT-5.2 mean: `0.1704`.
- Human vs All AI: Cliff's delta `0.7240` large, Holm MW `p=2.27e-06`, Holm permutation `p=0.0009999`.
- Human vs Claude and Human vs Gemini were significant after Holm correction; Human vs GPT-5.2 was significant by MW Holm but not permutation Holm.

Tables:

- `results/tables/rephrased/minimal/between_group_global_centroid_distances.csv`
- `results/tables/rephrased/minimal/between_group_global_centroid_group_summary.csv`
- `results/tables/rephrased/minimal/between_group_global_centroid_pairwise_tests.csv`

Figure:

- `results/figures/rephrased/minimal/between_group_global_centroid_dispersion.png`

##### `## Analysis 1.2c: MST Dispersion`

Step-by-step:

1. For each group, build the complete cosine-distance graph over proposal embeddings.
2. Compute the minimum spanning tree.
3. Report mean MST edge length as group-level dispersion.
4. Compare AI groups against Human with permutation tests and Holm correction.
5. Plot MST dispersion results.

Actual result:

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

Actual result:

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

Actual result:

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

Actual result:

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

Actual result:

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

Actual MeanKNN result:

- All AI was lower than Human at all tested k values.
- `mean_knn_5`: All AI vs Human mean difference `-0.0282`, delta `-0.4631` medium, MW Holm `p=0.00374`, permutation Holm `p=0.000900`.
- `mean_knn_10`: All AI vs Human mean difference `-0.0279`, delta `-0.4190` medium, MW Holm `p=0.00827`, permutation Holm `p=0.000900`.
- `mean_knn_20`: All AI vs Human mean difference `-0.0282`, delta `-0.4064` medium, MW Holm `p=0.0111`.
- `mean_knn_50`: All AI vs Human mean difference `-0.0285`, delta `-0.3825` medium, MW Holm `p=0.0189`.
- Claude and Gemini were consistently lower than Human; GPT-5.2 was not significant after Holm correction.

Actual normalized-novelty result:

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

Actual result:

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

Actual result:

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

Actual rendered result:

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

Actual rendered result:

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

Actual rendered result:

- Best k by BIC and silhouette: `3`.
- Cluster sizes: `[22, 19, 51]`; two clusters were Mixed and one was AI-dominated.
- NMI `0.0923`, permutation `p=0.0021`.
- ARI `0.1411`, permutation `p=0.0016`.
- Between/within distance ratio `1.2406`, permutation `p=0.0017`.

Figures:

- `results/figures/rephrased/minimal/cluster_k_selection.png`
- `results/figures/rephrased/minimal/cluster_analysis_visualization.png`

##### `# PART IV Style Baseline`

##### `### Exract stylistic features`

Step-by-step:

1. Extract style features from full rephrased proposal text.
2. Features include text length, sentence length, word length, type-token ratio, stopword rate, hedge rate, readability, punctuation rates, newline/bullet/header features, and group labels.
3. Save style features with titles.
4. Plot Human-vs-model style distributions.

Actual result:

- `style_features.csv` contains `92` proposal rows.

Table:

- `results/tables/rephrased/minimal/style_features.csv`

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

Actual rendered result:

- Style-only AUROC `0.561 +/- 0.166`.
- Balanced accuracy `0.584 +/- 0.117`.
- Permutation test observed AUROC `0.561`, null mean `0.504 +/- 0.098`, `p=0.2977`.
- The rendered notebook interprets this as weak style-only separation.

Figure:

- `results/figures/rephrased/minimal/style_only_baseline_viz.png`

##### `### Analysis 2.3.6A: Style-controlled sensitivity via residualization`

Step-by-step:

1. Stack Human and AI embeddings.
2. Build Human/AI source indicator.
3. Use style covariates to residualize embedding-distance outcomes.
4. Test whether source remains associated with distance to centroid after linear style control.
5. Use permutation tests with `n_perm=5000`, `seed=42`.

Actual rendered result:

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

Actual rendered result:

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

Actual result:

- The final merged proposal JSON exists at `results/tables/rephrased/minimal/all_proposals.json`.
- The metric master table has no missingness in the main diversity/novelty metric families according to the export design.

##### Actual Results Summary

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

Purpose: compare Human and AI reviews in the NCEMS criteria evaluation pipeline using reviews generated on rephrased proposals. The notebook mirrors the older `compare_reviews.ipynb` workflow but reads the prepared rephrased review artifact.

Global condition and paths:

- `condition = 'minimal'`.
- Primary prepared input: `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
- Figure output directory: `results/figures/quality/minimal/ncems_criteria`.
- Table output directory: `results/tables/quality/minimal/ncems_criteria`.
- Review embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl`.
- Matched Y1 cache, when needed: `review_embeddings_minimal_matched_y1.pkl` in the same embedding directory.

Criteria evaluated:

- `Relevance_to_Emergent_Phenomena`
- `Novelty_and_Significance`
- `Rigor_of_Approach`
- `Scope_and_Timeline`
- `Synthesis_Focus`
- `Data_Identification`
- `Open_Science_Commitment`

Score fields:

- `QUALITY_METRICS = ['overall_score'] + CRITERIA_ORDER`.
- Human rubric fields are mapped onto NCEMS criteria with `HUMAN_COL_MAP`:
  - `scientific_merit_and_innovation_score` maps to `Relevance_to_Emergent_Phenomena`, `Novelty_and_Significance`, and `Rigor_of_Approach`.
  - `feasibility_score` maps to `Scope_and_Timeline`.
  - `data_sources_and_limitations_score` maps to `Synthesis_Focus` and `Data_Identification`.
  - `open_science_compliance_score` maps to `Open_Science_Commitment`.

Shared statistical settings:

- Pairwise group tests use two-sided Mann-Whitney U plus Cliff's delta.
- Cliff's delta thresholds: negligible `<0.147`, small `<0.33`, medium `<0.474`, large `>=0.474`.
- Multiple testing uses Benjamini-Hochberg FDR, usually within each metric family.
- Robust quality checks use `2000` bootstrap resamples for 95% mean-difference CIs and `5000` label permutations with `seed=42`.
- Reliability uses ICC(2,1), ICC(2,k), and Spearman rank correlations.

#### `## 0) Environment setup (run once if needed)`

The notebook includes an optional commented install cell for `numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`, `openpyxl`, `textblob`, `transformers`, `torch`, `scikit-learn`, `statsmodels`, and `krippendorff`.

#### `## 1) Imports, paths, and constants`

Step-by-step:

1. Import JSON/path utilities, NumPy/pandas, seaborn/matplotlib, SciPy tests, cosine similarity, TextBlob, PyTorch, and BioLinkBERT tokenizer/model utilities.
2. Find the project root by locating `src/` and `data/`.
3. Set `condition='minimal'`.
4. Require the prepared review table at `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`; fail early if it is missing.
5. Create figure/table directories and review embedding cache directory.
6. Define the color map for Human, Claude, Gemini, and GPT-5.2.
7. Define NCEMS criteria, display-name mappings, Human-to-NCEMS rubric mappings, and four shared Human rubric categories.

#### `## 2) Utility functions`

Defines:

- `normalize_title()`: lowercases, removes non-alphanumeric characters, and collapses whitespace.
- `token_set_jaccard()` and `hybrid_similarity()`: hybrid title matching score using `0.7 * SequenceMatcher + 0.3 * token_set_jaccard`.
- `cliffs_delta()` and `interpret_cliffs_delta()`.
- `benjamini_hochberg()` and `add_bh_fdr()`.
- `mannwhitney_summary()`: returns `n_group1`, `n_group2`, U statistic, raw p-value, Cliff's delta, and delta magnitude.
- TextBlob sentiment helpers:
  - `sentiment_label()`: positive if polarity `>0.1`, negative if `<-0.1`, otherwise neutral.
  - `sentiment_alignment()`: `1 - abs(p1 - p2) / 2`.
  - `categorical_agreement()`: agree, partial, or disagree for sentiment labels.
- `bootstrap_mean_diff_ci()` with `n_boot=2000`, `ci=0.95`, `seed=42`.
- `permutation_p_value_mean_diff()` with `n_perm=5000`, `seed=42`.
- `icc2_1_2k()` for complete item-by-rater matrices.
- `build_one_to_one_title_mapping()`:
  1. exact-match normalized titles first;
  2. fuzzy-match remaining titles with `fuzzy_threshold=0.70`;
  3. enforce one-to-one matching;
  4. return mapping table, diagnostics, unmatched Human IDs, and unmatched AI IDs.

#### `## 3) Load prepared AI reviews`

What data:

- Reads `ncems_criteria_all_reviews.csv`.
- Keeps rows where `review_source == 'ai'`.

Step-by-step:

1. Load the prepared all-review table.
2. Create `ai_df`.
3. Convert `overall_score` and every NCEMS criterion to numeric.
4. Print AI review row count, author groups, and evaluator groups.

Expected author/evaluator semantics:

- `author` identifies proposal source (`human-y1`, `human-y2`, Claude, Gemini, GPT-5.2).
- `evaluator` identifies the AI model that produced the review.

#### `## 4) Load prepared human Y1 expert reviews`

What data:

- Same prepared all-review table.
- Keeps rows where `review_source == 'human'` and `author == 'human-y1'`.

Step-by-step:

1. Create `human_df`.
2. Convert `overall_score` and criteria to numeric.
3. Print Human Y1 review row count and unique proposal count.

Purpose:

- Human Y1 expert reviews are the initial human-human baseline for the similarity-proxy workflow.

#### `## 5) Proposal matching diagnostics (exact + fuzzy fallback)`

What data:

- Human Y1 proposal titles from `human_df`.
- AI reviews of Human Y1 proposals from `ai_df[author == 'human-y1']`.

Step-by-step:

1. Build Human proposal table with `human_proposal_id`, original title, and normalized title.
2. Build AI proposal table with `ai_proposal_id`, original title, and normalized title.
3. Run `build_one_to_one_title_mapping(..., fuzzy_threshold=0.70)`.
4. Sort mapping by Human proposal ID.
5. Assign stable matched keys `Y1_01`, `Y1_02`, ...
6. Print diagnostics: number of Human proposals, AI proposals, matches, exact matches, fuzzy matches, and unmatched IDs.

Purpose:

- Fixes the earlier issue where title-exact matching dropped proposals; this mapping is the single source of truth for Y1 review-pair comparisons.

#### `## 6) Build matched review sets, embeddings, and pair table (single source of truth)`

What data:

- Matched Human Y1 reviews.
- Matched AI reviews of Human Y1 proposals.
- Review text from `review_text`.

Embedding model and setting:

- Model: `michiyasunaga/BioLinkBERT-large`.
- Device: CUDA if available, otherwise CPU.
- Embedding function uses mean pooling over token embeddings with the attention mask, not `[CLS]`.
- Embeddings are L2-normalized.
- Batch size: `8`.
- Max token length: `512`.

Step-by-step:

1. Merge `human_df` and `ai_y1` with the Y1 title mapping to get aligned Human and AI review rows.
2. Ensure every row has a `review_uid`.
3. Prefer prepared all-review embedding cache if it contains `embeddings` and `metadata` keyed by `review_uid`.
4. Otherwise accept a legacy matched cache only if model name, review UIDs, and review texts match exactly.
5. Otherwise use or write the matched-Y1 cache `review_embeddings_minimal_matched_y1.pkl`.
6. If no valid cache exists, compute embeddings with BioLinkBERT mean pooling.
7. Attach embeddings to the aligned Human and AI review rows.
8. Compute TextBlob polarity and sentiment labels for every aligned review.
9. For each matched proposal:
  - create all Human-AI review pairs;
  - create all AI-AI review pairs;
  - create all Human-Human review pairs.
10. For every pair, compute:
  - cosine similarity between review embeddings;
  - sentiment alignment;
  - categorical sentiment agreement (`disagree`, `partial`, `agree`);
  - numeric categorical agreement (`0`, `1`, `2`).
11. Store pair metadata such as pair type, proposal key, match method, reviewer/evaluator IDs, AI model, and AI model pair.
12. Build `pair_df` and print matched proposal count plus pair counts by type/model.

#### `## 7) Pair count checks (expected vs observed)`

Step-by-step:

1. Count Human reviews per matched proposal.
2. Count AI reviews per matched proposal in total and by evaluator model.
3. Compute expected Human-AI pairs as `n_human_reviews * n_ai_reviews_total` per proposal.
4. Compute expected Human-Human pairs as `nC2(n_human_reviews)` per proposal.
5. Compute expected AI-AI pairs as `nC2(n_ai_reviews_total)` per proposal.
6. Compare expected totals to observed `pair_df['pair_type'].value_counts()`.

Purpose:

- Confirms that the pair table is complete and that later proposal-level aggregation is based on the intended pair universe.

#### `## 8) Similarity proxy stats (proposal-level, model-aware, FDR-corrected)`

What data:

- `pair_df` from Section 6.

Similarity metrics:

- `cosine_similarity`
- `sentiment_alignment`
- `categorical_agreement_num`

Step-by-step:

1. Aggregate pair-level metrics to proposal-level means for:
  - `human-human`
  - `human-ai`
  - `ai-ai`
2. For each metric, compare:
  - `human-ai` vs `human-human`
  - `ai-ai` vs `human-human`
  - `ai-ai` vs `human-ai`
3. Use paired Wilcoxon signed-rank tests as the primary test by merging on `proposal_key`.
4. Also compute Mann-Whitney U and Cliff's delta as a secondary sensitivity check.
5. Apply BH-FDR to Mann-Whitney p-values within each metric family.
6. For model-aware Human-AI analyses:
  - aggregate `human-ai` pairs by `proposal_key` and `ai_model`;
  - compare each `human-ai::<model>` group to `human-human`.
7. For AI-AI model-pair analyses:
  - aggregate `ai-ai` pairs by `proposal_key` and `ai_model_pair`;
  - compare each `ai-ai::<model-pair>` group to `human-human`.
8. Display overall, Human-AI-by-model, and AI-AI-by-model-pair test tables.

Primary inference rule:

- Trust `wilcoxon_p_value` for paired proposal-level comparisons. Mann-Whitney and Cliff's delta are retained for robustness and effect-size reporting.

#### `### Interpretation: Similarity Proxy Statistics`

The notebook explicitly states:

- Wilcoxon is primary because the same matched proposals appear across pair types.
- Mann-Whitney is a sensitivity check only.
- Cliff's delta sign means group 1 tends to be higher or lower than group 2.
- AI-AI similarity can be high without implying human alignment; it may indicate model-reviewer convergence.

##### `#### Primary test — Paired Wilcoxon signed-rank (`wilcoxon_stat`, `wilcoxon_p_value`)`

Use this as the primary p-value for proposal-matched pair-type comparisons. It tests whether the median signed proposal-level difference is zero.

##### `#### Secondary test — Mann-Whitney U (`u_stat`, `p_value`, `q_value`) — sensitivity check only`

Use this as a robustness check because the notebook notes that the independence assumption is violated for matched proposal-level comparisons.

##### `#### Effect size — Cliff's delta (`cliffs_delta`, `delta_magnitude`)`

Report sign and magnitude with the relevant primary or sensitivity p-value. Positive delta means group 1 tends to be higher than group 2.

##### `#### Example interpretations:`

The notebook gives examples distinguishing Human-AI review alignment from AI-AI reviewer convergence; high AI-AI similarity is not automatically evidence of human-like review behavior.

#### `## 8b) Similarity proxy visualization (proposal-level)`

Step-by-step:

1. Build a wide proposal-level table with one row per proposal and columns for each pair type by metric.
2. Create a paired slope plot for `human-human`, `human-ai`, and `ai-ai`; each line is one proposal.
3. Add group mean markers to the slope plots.
4. Create model-specific Human-AI box/strip plots.
5. Create AI-AI model-pair box/strip plots.

Figures:

- `quality_similarity_proxy_paired_slopes.png`
- `quality_similarity_human_ai_by_model_proposal_level.png`
- `quality_similarity_ai_ai_by_model_pair_proposal_level.png`

#### `### Interpretation: Similarity Plots`

Use Human-Human as the inter-expert baseline. Interpret Human-AI overlap with Human-Human as proxy alignment, and interpret AI-AI tightness as model consistency rather than necessarily human-like reviewing.

#### `# R2: How are AI proposals' quality compare to humans (evaluated by AI)`

This block asks whether AI-authored proposals score differently from Human-authored proposals when evaluated by the AI reviewers under the NCEMS criteria.

#### `## 10) Proposal-quality analysis dataset (proposal-level means, no duplicated human-all rows)`

What data:

- AI-produced NCEMS reviews in `ai_df`, including AI reviews of Human and AI-authored proposals.

Step-by-step:

1. Define `QUALITY_METRICS = ['overall_score'] + CRITERIA_ORDER`.
2. Group `ai_df` by `author`, `proposal_id`, and `proposal_uid`.
3. Average all quality metrics across evaluators within each proposal.
4. Keep true base groups:
  - `human-y1`
  - `human-y2`
  - `claude-opus-4-5`
  - `gemini-3-pro-preview`
  - `gpt-5.2`
5. Define `human-all` analytically in helper functions as the union of `human-y1` and `human-y2`; do not duplicate rows in the source proposal-level data.
6. Summarize overall-score `n`, mean, median, and standard deviation for:
  - `human-y1`
  - `human-y2`
  - `human-all`
  - Claude
  - Gemini
  - GPT-5.2

Existing compact result:

- Raw evaluator-pool overall means: Human-all `3.5855`, Claude `4.0087`, Gemini `3.8319`, GPT-5.2 `4.3174`.

#### `### Interpretation: Proposal-Level Summary Dataset`

Use group sizes and dispersion to contextualize the pairwise tests. Unequal sample sizes affect power; variance can weaken significance despite mean gaps.

#### `### Interpretation: Quality Distribution Plots`

The notebook then visualizes:

1. Overall-score histograms with bins from `1` to `5.5` in increments of `0.25`.
2. Overall-score boxplots plus strip plots.
3. Radar chart of mean criterion scores for Human-all, Claude, Gemini, and GPT-5.2.

Figures:

- `quality_overall_histograms_proposal_level.png`
- `quality_overall_boxplot_proposal_level.png`
- `quality_radar_criteria_proposal_level.png`

#### `## 11) Pairwise quality tests (MW + Cliff's delta + FDR) on proposal-level means`

Step-by-step:

1. Define AI groups: Claude, Gemini, GPT-5.2.
2. For each quality metric, compare Human Y1 vs Human Y2 using Mann-Whitney U and Cliff's delta.
3. Apply BH-FDR within each metric family for Human-cohort tests.
4. For each quality metric and each AI group, compare `human-all` vs the AI group.
5. Apply BH-FDR within each metric family for Human-all vs AI tests.
6. Build a full pairwise table across all base groups, excluding synthetic `human-all`.
7. Apply BH-FDR within metric family for the full pairwise table.
8. Display Human-cohort tests and Human-all-vs-AI tests sorted by metric and q-value.

Primary estimand:

- Proposal-level quality-score difference between Human-all and each AI-authored proposal group.

Existing compact result:

- Significant overall contrasts vs Human-all in the raw evaluator pool:
  - Claude `q=5.25e-04`
  - Gemini `q=0.0187`
  - GPT-5.2 `q=1.31e-07`

#### `### Interpretation: Pairwise Quality Tests`

Prioritize `q_value` over raw `p_value`; report Cliff's delta and delta magnitude as practical effect size. The sign of Cliff's delta follows `group1` vs `group2`.

#### `## 11b) Effect size & significance visualization`

Step-by-step:

1. Combine Human-all-vs-AI tests with Human Y1-vs-Y2 tests.
2. Create an effect-size heatmap:
  - rows are `overall_score` plus all criteria;
  - columns are Human vs Claude, Human vs Gemini, Human vs GPT, and Y1 vs Y2;
  - color is Cliff's delta;
  - gray means `q >= 0.05`;
  - each cell prints delta and significance stars.
3. Create a Human-vs-AI dot plot:
  - x-axis is Cliff's delta for `human-all minus AI model`;
  - y-axis is metric;
  - color is AI model;
  - hollow points are non-significant;
  - point size scales with `-log10(q_value)`.

Figures:

- `quality_effect_size_heatmap.png`
- `quality_effect_size_dotplot.png`

#### `## 12) Non-parametric sensitivity check (OPTIONAL)`

##### `### Robust inference for key comparisons (bootstrap CI + permutation p)`

Step-by-step:

1. For every quality metric and every Human-all-vs-AI model comparison, compute mean difference `human-all minus model`.
2. Bootstrap a 95% CI for the mean difference using `n_boot=2000`, `seed=42`.
3. Run a two-sided label-permutation test for the mean difference using `n_perm=5000`, `seed=42`.
4. Apply BH-FDR to permutation p-values within metric family, writing `permutation_q_value`.

Interpretation:

- Robust evidence requires the bootstrap CI to exclude `0` and permutation `q_value < 0.05`.

#### `### Interpretation: Robust Inference`

The sign of `mean_diff` is `human-all minus model`. Disagreement between Mann-Whitney and robust checks marks a finding as fragile/exploratory.

#### `# R3: Is there any self-preference bias in AI evaluators?`

This block asks whether AI evaluator models rate their own generated proposals differently than proposals generated by other AI models.

#### `## 13) Evaluator differences (non-duplicated data only)`

Step-by-step:

1. Use non-duplicated `ai_df`, not synthetic `human-all`.
2. Group by evaluator model and summarize `overall_score` count, mean, median, and standard deviation.
3. Visualize raw overall-score distributions by evaluator model.
4. Run Kruskal-Wallis across evaluator models.

Figure:

- `quality_overall_by_evaluator_clean.png`.

Existing compact result:

- Evaluator effects were strong; Kruskal-Wallis `p=5.20e-22`.

#### `### Interpretation: Evaluator Descriptives`

Large evaluator mean/median gaps indicate potential judge leniency or severity, which must be considered before interpreting author-group quality differences.

#### `### Interpretation: Evaluator Difference Test`

Kruskal-Wallis `p_value < 0.05` means at least one evaluator distribution differs; this motivates the later self-preference and fixed-effects analyses.

#### `## 14) AI self-preference tests (overall + criterion-level + proposal controls)`

What data:

- Restrict to AI-authored proposals and AI evaluators:
  - authors: Claude, Gemini, GPT-5.2;
  - evaluators: Claude, Gemini, GPT-5.2.

Overall self-preference step-by-step:

1. Group by `evaluator`, `author`, and `proposal_id`.
2. Average `QUALITY_METRICS` at proposal level.
3. Define `is_self = (author == evaluator)`.
4. For each evaluator model, compare scores on its own proposals (`is_self`) against scores on other AI models' proposals.
5. Use Mann-Whitney U, Cliff's delta, and BH-FDR.
6. Record `mean_self` and `mean_other`.

Criterion-level self-preference step-by-step:

1. Melt the proposal-level table over `QUALITY_METRICS`.
2. For each evaluator and metric, compare self vs other scores.
3. Use Mann-Whitney U, Cliff's delta, and BH-FDR within each evaluator.
4. Record metric-level `mean_self` and `mean_other`.

Existing compact interpretation:

- Self-preference direction is model-dependent: Claude self-deprecates, GPT self-inflates, and Gemini is closer to neutral.

#### `### Interpretation: Overall Self-Preference`

`q_value < 0.05` plus `mean_self > mean_other` indicates self-favoring bias; the reverse indicates self-penalization or preference for other models' proposals.

#### `### Interpretation: Criterion-Level Self-Preference`

Use criterion-level `q_value` and Cliff's delta to identify whether bias is concentrated in specific rubric dimensions.

#### `## 14b) Self-preference visualization`

Step-by-step:

1. Create a three-panel box/strip plot of overall score, one panel per evaluator, comparing `Self` vs `Other`.
2. Add red mean lines and annotate significance plus Cliff's delta.
3. Create a criterion-level heatmap:
  - rows are `overall_score` plus criteria;
  - columns are evaluator models;
  - cell value is `mean_self - mean_other`;
  - gray means FDR non-significant (`q >= 0.05`).

Figures:

- `self_pref_strip_overall.png`
- `self_pref_criterion_heatmap.png`

#### `#### Do these models rate their own proosals better? How to remove that bias?`

The notebook explains why a fixed-effects regression is needed: non-parametric self-vs-other comparisons do not rule out the possibility that a model's own proposals are genuinely higher quality. Proposal fixed effects absorb proposal-specific quality so the self-preference term captures evaluator behavior rather than proposal quality.

Regression formula:

- `score ~ is_self_num * C(metric) + C(evaluator) + C(author) + C(proposal_uid)`

Model details:

- `C(proposal_uid)` controls proposal-specific quality/difficulty.
- `C(evaluator)` controls evaluator severity/leniency.
- `C(author)` controls author/source differences.
- `is_self_num * C(metric)` allows self-preference to vary by criterion.
- Fit with `statsmodels` OLS and HC3 robust standard errors.

#### `## 14c) Fixed-effects regression: forest plot`

Step-by-step:

1. Extract the fitted fixed-effects regression parameters and covariance matrix.
2. For each metric, compute net self-preference coefficient:
  - reference metric `Data_Identification`: `beta = is_self_num`;
  - other metrics: `beta = is_self_num + is_self_num:C(metric)[T.metric]`.
3. Combine uncertainty from main and interaction terms:
  - `var(beta_c) = var(main) + var(interaction_c) + 2 * cov(main, interaction_c)`.
4. Compute 95% confidence intervals using a normal critical value.
5. Plot per-criterion self-preference coefficients:
  - red for significant self-favoring;
  - blue for significant other-favoring;
  - gray for non-significant.
6. Plot evaluator severity offsets from `C(evaluator)` in a side panel, with Claude as the reference evaluator.

Figure:

- `self_pref_regression_forest.png`.

#### `## 19) Export tables`

Exports:

- `quality_matching_map_exact_fuzzy.csv`
- `quality_similarity_pairs.csv`
- `quality_similarity_mw_cliffs_overall.csv`
- `quality_similarity_mw_cliffs_human_ai_by_model.csv`
- `quality_similarity_mw_cliffs_ai_ai_by_model_pair.csv`
- `quality_summary_overall_by_author_group.csv`
- `quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv`
- `quality_robust_bootstrap_permutation_key_comparisons.csv`
- `quality_evaluator_overall_stats_clean.csv`
- `quality_self_preference_tests_overall.csv`
- `quality_self_preference_tests_by_metric.csv`

Note:

- In the executed baseline notebook, proxy validity/rank agreement/ICC exports are commented out and are not actual outputs for this run.

#### `## 20) R2 Re-Run Without Self-Evaluator Scores on AI-Authored Proposals`

Bias-control rule:

- For AI-authored proposals, drop the review where `evaluator == author`.
- For Human-authored proposals, keep all three AI evaluators.
- AI-authored proposal scores are then averaged over the two cross-evaluators only.

Step-by-step:

1. Define reusable function `run_r2_10_12_pipeline(reviews_df, run_tag, run_label)`.
2. Inside the function, repeat Sections 10-12:
  - proposal-level score aggregation;
  - overall summaries;
  - histogram, boxplot, and radar figures;
  - Human Y1 vs Y2 tests;
  - Human-all vs AI tests;
  - full pairwise base-group table;
  - effect-size heatmap and dot plot;
  - bootstrap/permutation robust checks.
3. Save all scenario-specific outputs with `run_tag` suffixes.
4. Build `ai_df_cross_eval_only` by removing self-evaluations for AI-authored proposals.
5. Print the number of removed rows and remaining evaluator counts.
6. Run the pipeline with `run_tag='cross_eval_only'` and label `R2 Bias-Control: AI self-score removed`.

Scenario-specific outputs:

- `quality_summary_overall_by_author_group_cross_eval_only.csv`
- `quality_human_cohort_mw_cliffs_cross_eval_only.csv`
- `quality_vs_ai_mw_cliffs_cross_eval_only.csv`
- `quality_pairwise_mw_cliffs_all_metrics_cross_eval_only.csv`
- `quality_robust_bootstrap_permutation_cross_eval_only.csv`
- `quality_overall_histograms_proposal_level_cross_eval_only.png`
- `quality_overall_boxplot_proposal_level_cross_eval_only.png`
- `quality_radar_criteria_proposal_level_cross_eval_only.png`
- `quality_effectsize_heatmap_cross_eval_only.png`
- `quality_effectsize_dotplot_cross_eval_only.png`

Existing compact result after self-evaluation removal:

- Human-all vs Claude remains significant (`q=2.25e-04`).
- Human-all vs Gemini becomes non-significant (`q=0.6816`).
- Human-all vs GPT-5.2 remains strongly significant (`q=1.70e-08`).

#### `## 21) Y1 + Y2 Rephrased Review Similarity (Human-Human vs AI-AI)`

Purpose:

- Extend the embedding-similarity workflow to both Human Y1 and Human Y2 rephrased reviews.

Step-by-step:

1. Define `load_rephrased_human_reviews(path, author_label)`:
  - read the rephrased Human review CSV;
  - require `rephrased_review`, with legacy fallback to `rephrased_reviews`;
  - create evaluator IDs from `reviewer_id`;
  - normalize titles;
  - convert Human rubric columns to numeric;
  - set `overall_score` from `overall_rating_score`, falling back to mean Human rubric score when missing;
  - map Human rubric columns onto NCEMS criteria using `HUMAN_COL_MAP`;
  - set `review_text` from `rephrased_review`;
  - create `proposal_uid`.
2. Define `build_cohort_similarity(human_reviews_df, ai_reviews_df, cohort_tag, fuzzy_threshold=0.70)`:
  - build one-to-one Human-AI proposal title mapping for that cohort;
  - align Human and AI review rows to mapping;
  - ensure review UIDs;
  - load prepared embeddings by `review_uid` when possible, otherwise compute locally with BioLinkBERT;
  - attach embeddings;
  - create Human-Human and AI-AI pairwise cosine-similarity records within each proposal.
3. Build Y1 and Y2 cohort objects:
  - `human_y1_reviews`
  - `human_y2_reviews`
  - `ai_y1_reviews`
  - `ai_y2_reviews`
4. Print review counts and unique proposal counts for each cohort/source.

Outputs prepared in memory:

- cohort-specific mappings;
- aligned Human and AI review tables;
- pairwise cosine-similarity tables for Y1 and Y2.

#### `### 21a) Combined Y1/Y2 Pairwise Similarity Graph + Significance Tests`

Step-by-step:

1. For each cohort/source pair, aggregate pairwise cosine similarity to proposal-level means:
  - `human-y1`
  - `ai-y1`
  - `human-y2`
  - `ai-y2`
2. Concatenate the four groups into `sim_4group`.
3. Plot a four-group boxplot/stripplot of proposal-level mean pairwise cosine similarity.
4. Run Kruskal-Wallis across the four groups.
5. Run all pairwise Mann-Whitney + Cliff's delta comparisons across the four groups.
6. Apply BH-FDR across pairwise p-values.
7. For each cohort, run paired Human-vs-AI Wilcoxon tests by matching proposal keys.
8. Also report Mann-Whitney and Cliff's delta for within-cohort Human-vs-AI comparisons.

Figure:

- `quality_review_similarity_y1y2_four_groups.png`.

Tables created later:

- `quality_review_similarity_y1y2_four_groups_values.csv`
- `quality_review_similarity_y1y2_four_group_tests.csv`
- `quality_review_similarity_within_cohort_paired_tests.csv`

#### `## 22) Y2 Quantitative Score Reliability (Human, AI, and Human-vs-AI)`

What data:

- Y2 aligned Human reviews and AI reviews from Section 21.
- Metrics: `overall_score` plus all NCEMS criteria.

Step-by-step:

1. For each metric, build a Human Y2 proposal-by-reviewer score matrix.
2. Compute Human-Human Y2:
  - ICC(2,1);
  - ICC(2,k);
  - mean pairwise Spearman across reviewer pairs.
3. Build an AI Y2 proposal-by-evaluator score matrix.
4. Compute AI-AI Y2 ICC and mean pairwise Spearman.
5. Compute Human-vs-AI Y2 agreement:
  - mean Human score per proposal;
  - mean AI score per proposal;
  - Spearman correlation and p-value;
  - ICC(2,1) and ICC(2,k) treating Human mean and AI mean as two raters.
6. Store all rows in `y2_reliability_df`.
7. Visualize ICC(2,k) as a metric-by-comparison heatmap.
8. Plot Human-vs-AI overall-score agreement with a regression line and proposal labels.

Figures:

- `quality_review_reliability_y2_heatmap.png`
- `quality_review_reliability_y2_human_vs_ai_scatter.png`

#### `## 23) Export Y2 + Y1Y2 Added Outputs`

Exports:

- `quality_matching_map_y1_rephrased_reviews.csv`
- `quality_matching_map_y2_rephrased_reviews.csv`
- `quality_similarity_pairs_y1_rephrased_reviews.csv`
- `quality_similarity_pairs_y2_rephrased_reviews.csv`
- `quality_review_similarity_y1y2_four_groups_values.csv`
- `quality_review_similarity_y1y2_four_group_tests.csv`
- `quality_review_similarity_within_cohort_paired_tests.csv`
- `quality_y2_reliability_human_ai.csv`

Figures printed as saved:

- `quality_review_similarity_y1y2_four_groups.png`
- `quality_review_reliability_y2_heatmap.png`
- `quality_review_reliability_y2_human_vs_ai_scatter.png`

#### Baseline(minimal)-rephrased Rendered Notebook Cell-by-Cell Audit

This subsection is the source-of-truth plan for the rendered notebook at `baseline(minimal)-rephrased/compare_reviews_ncems_criteria.ipynb`. It supersedes the generic/template notes above where filenames, headings, or export behavior differ.

Actual run settings:

- `CONDITION = 'minimal'`.
- `REUSE_REVIEW_EMBEDDINGS = True`.
- Prepared review input: `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
- Review embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl`.
- Strength embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_strengths_embeddings_minimal.pkl`.
- Weakness embedding cache: `data/embeddings/reviews/minimal/ncems_criteria/review_weakness_embeddings_minimal.pkl`.
- Figure directory: `results/figures/quality/minimal/ncems_criteria`.
- Table directory: `results/tables/quality/minimal/ncems_criteria`.

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

Actual result:

- AI review rows: `276`.
- Authors: `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`, `human-y1`, `human-y2`.
- Evaluators: `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`.

##### `## 4) Load prepared human expert reviews (Y1 + Y2)`

What data:

- Same prepared review table, filtered to `review_source == 'human'`.

Actual result:

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

Actual result:

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

Actual result:

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

Actual result:

- Expected and observed totals matched exactly: Human-AI `141`, Human-Human `70`, AI-AI `36`.

##### `# R1: How does the diversity of human reviews compare to those by AI?`

The executed notebook adds a full review-diversity analysis before the similarity proxy analyses. The main estimand is proposal-conditioned within-cohort diversity: Human reviewer variation compared with AI reviewer variation for the same proposal set.

##### `## 8c) Build matched review sets for Y1 and Y2 (single source of truth)`

What data:

- Prepared merged review dataframe.
- Human-Y1 and Human-Y2 expert reviews.
- AI reviews of Human-Y1 and Human-Y2 proposals.
- Prepared review embeddings keyed by `review_uid`.

Actual matched cohort result:

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

Actual result:

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

Actual result:

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

Actual result:

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

Actual result:

- Human-AI vs Human-Human cosine similarity: Wilcoxon `p=0.909668`, Mann-Whitney `q=0.750832`, Cliff's delta `-0.083333` negligible.
- AI-AI vs Human-Human cosine similarity: Wilcoxon `p=0.063965`, Mann-Whitney `q=0.029060`, Cliff's delta `0.569444` large.
- AI-AI vs Human-AI cosine similarity: Wilcoxon `p=0.016113`, Mann-Whitney `q=0.007310`, Cliff's delta `0.736111` large.
- Human-AI by model: no model differed significantly from Human-Human after FDR on cosine similarity.
- AI-AI model pairs: Claude/Gemini cosine similarity was significant by Mann-Whitney FDR (`q=0.042414`, large delta); categorical agreement was significant for all three model pairs (`q=0.016011`).

Tables:

- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_overall.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_human_ai_by_model.csv`
- `results/tables/quality/minimal/ncems_criteria/quality_similarity_mw_cliffs_ai_ai_by_model_pair.csv`

##### `## 8b) Similarity proxy visualization (proposal-level)`

Step-by-step:

1. Plot proposal-level paired slopes for Human-Human, Human-AI, and AI-AI similarity.
2. Plot Human-AI similarity by AI model.
3. Plot AI-AI similarity by model pair.

Figures:

- `results/figures/quality/minimal/ncems_criteria/quality_similarity_proxy_paired_slopes.png`
- `results/figures/quality/minimal/ncems_criteria/quality_similarity_human_ai_by_model_proposal_level.png`
- `results/figures/quality/minimal/ncems_criteria/quality_similarity_ai_ai_by_model_pair_proposal_level.png`

##### `### 8e) Rephrased review similarity analyses (Y1, Y2, combined)`

What data:

- Y1 and Y2 aligned Human-Human and AI-AI review pairs.

Step-by-step:

1. Aggregate within-cohort pairwise cosine similarity to proposal-level means for `human-y1`, `ai-y1`, `human-y2`, and `ai-y2`.
2. Plot the four groups in one distribution figure.
3. Run Kruskal-Wallis across the four groups.
4. Run all pairwise Mann-Whitney + Cliff's delta comparisons and BH-FDR.
5. Run within-cohort paired Human-vs-AI Wilcoxon tests by proposal.

Actual result:

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

Actual result:

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

Actual exported R1 tables:

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

Actual result:

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

##### `## 11) Pairwise quality tests (MW + Cliff's delta + FDR) on proposal-level means`

Step-by-step:

1. Compare Human-Y1 vs Human-Y2 for each quality metric.
2. Compare Human-all vs each AI author group for each quality metric.
3. Run full base-group pairwise comparisons excluding synthetic `human-all`.
4. Use Mann-Whitney U, Cliff's delta, and BH-FDR within metric families.

Actual overall-score result in the raw evaluator pool:

- Human-all vs Claude: significant, `q=5.25e-04`.
- Human-all vs Gemini: significant, `q=0.0187`.
- Human-all vs GPT-5.2: significant, `q=1.31e-07`.

Table:

- `results/tables/quality/minimal/ncems_criteria/quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv`

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

Actual overall-score result:

- Human-all minus Claude: mean difference `-0.423188`, CI `[-0.627609, -0.231848]`, permutation `q=0.000300`.
- Human-all minus Gemini: mean difference `-0.246377`, CI `[-0.443478, -0.063768]`, permutation `q=0.015197`.
- Human-all minus GPT-5.2: mean difference `-0.731884`, CI `[-0.927572, -0.552138]`, permutation `q=0.000300`.

Table:

- `results/tables/quality/minimal/ncems_criteria/quality_robust_bootstrap_permutation_key_comparisons.csv`

##### `# R3: Is there any self-preference bias in AI evaluators?`

##### `## 13) Evaluator differences (non-duplicated data only)`

What data:

- Non-duplicated AI-review rows; no synthetic `human-all`.

Actual result:

- Gemini evaluator: `n=92`, mean overall `4.301087`.
- Claude evaluator: `n=92`, mean overall `3.783696`.
- GPT-5.2 evaluator: `n=92`, mean overall `3.722826`.
- Kruskal-Wallis statistic `98.015853`, `p=5.20149e-22`.

Figure:

- `results/figures/quality/minimal/ncems_criteria/quality_overall_by_evaluator_clean.png`

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

Actual overall self-preference result:

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

##### `## 19) Export tables`

Actual exported R2/R3 tables:

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

Actual non-exports:

- `quality_proxy_validity_metrics.csv`, `quality_proxy_rank_agreement.csv`, and `quality_proxy_icc.csv` are commented out in the executed baseline export cell and should not be treated as outputs for this notebook run.

##### `## 20) R2 Re-Run Without Self-Evaluator Scores on AI-Authored Proposals`

Bias-control rule:

- Remove AI-authored proposal reviews where `evaluator == author`.
- Keep all AI reviews of Human-authored proposals.
- Average AI-authored proposal scores over the two remaining cross-evaluators.

Actual result:

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

##### Actual Results Summary

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
