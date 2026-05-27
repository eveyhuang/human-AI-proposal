## Overview

This document is now an **execution-status analysis plan** based on the completed notebooks in:
- `notebooks/templates/rephrased/compare_proposals_rephrased.ipynb`
- `notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb`
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



## Experiment Conditions

This study now has three generation conditions:

1. `baseline(minimal)-rephrased` (**completed**)
- LLMs generate ideas/proposals under the minimal prompt pipeline with rephrasing.
- This condition is the current reference condition and all completed results in this plan come from it.

2. `how_to_think` (**planned next**)
- LLMs first use an LLM-suggested “how to think” process, then generate ideas/proposals using that process.

3. `persona` (**planned next**)
- LLMs generate ideas/proposals while adopting human-scientist author personas.
- Inputs include titles/abstracts of recent papers by the target author(s) during idea generation.

### Cross-condition comparison plan

- For both **ideas** and **full proposals**, run the same analysis families already used in baseline:
- Diversity analyses.
- Novelty analyses.
- Score-comparison analyses.
- Primary comparison: each new condition (`how_to_think`, `persona`) vs `baseline(minimal)-rephrased`, then Human vs each condition.

## Completed Analyses and Results

### Compact Results Table

| Analysis | Main effect | Significance (primary) | Effect size / key statistic | Status |
|---|---|---|---|---|
| Diversity 1.1 Pairwise (**Remote-Clique**) | Human > All AI diversity | MW Holm `p=1.20e-07` (All AI vs Human) | `δ=-0.7681` (large) | Done |
| Diversity 1.2 Centroid dispersion (**Span-related, mean radius**) | Human > All AI dispersion | MW Holm `p=1.20e-07` | `δ=-0.7681` (large) | Done |
| Diversity 1.2b Between-group centroid dispersion (centroid-to-centroid) | Quantifies separation among Human, per-model AI, and All-AI centroids | Descriptive output (pairwise matrix + ranking) | Pairwise centroid cosine distances; mean distance-to-other-centroids | Added to notebook (run pending) |
| Diversity 1.3 1-NN isolation (**Chamfer / NN**) | Human more isolated than All AI | MW Holm `p=5.13e-06` | `δ=-0.6774`; outliers `30.4%` vs `4.3%` | Done |
| Novelty Step 5 Raw (k=10) | Human higher raw novelty than most AI groups | Claude vs Human MW Holm `p=0.0197`; All AI Holm `p=0.1069` | Claude `δ=-0.4858`; All AI `δ=-0.2943` | Done |
| Novelty Step 4b Local-density normalized | Broad AI-vs-Human difference disappears after normalization | All AI vs Human MW `p=0.9138` | `δ=0.0158` (negligible) | Done |
| Novelty Step 7B Literature-space outliers (mean-10NN) | Human outlier prevalence higher than All AI | Fisher Holm `p=0.0562` (All AI vs Human) | Rate diff `-20.3` pp; OR `0.1744` | Done |
| Topic + cluster structure (2.3.2-2.3.4) | Human/AI semantic regions differ | Soft-topic permutation chi-square `p=0.0001`; NMI `p=0.0026`; ARI `p=0.0013` | NMI `0.0887`; ARI `0.1254`; B/W ratio `1.2406` | Done |
| Style sensitivity (2.3.5-2.3.6) | Centroid separation robust; NN isolation style-sensitive | Centroid permutation `p=0.0002`; style-adjusted NN MW `p=0.1582` | AI coef `-0.174962`; NN `δ=0.1979` (ns) | Done |
| NCEMS quality reviews (cross-eval rerun) | GPT-5.2 and Claude > Human-all; Gemini ~ Human-all | GPT vs Human `q=1.70e-08`; Claude vs Human `q=2.25e-04`; Gemini `q=0.6816` | GPT `δ=-0.9924`; Claude `δ=-0.6522` | Done |
| Novelty-framework reviews (cross-eval rerun) | Mixed: GPT > Human, Human > Gemini, Claude ~ Human | GPT vs Human `q=0.010924`; Human vs Gemini `q=1.79e-05`; Human vs Claude `q=0.8428` | Human-GPT `δ=-0.4631`; Human-Gemini `δ=0.7788` | Done |
| Metric-score + outlier validation | Semantic remoteness penalized on NCEMS but can help novelty-specific criteria | Outlier NCEMS relevance `p<0.001`; novelty criterion (`new_theory...`) `p=0.0273` | `r=-0.6496` (semantic vs NCEMS relevance); `r=0.5093` (centroid vs novelty criterion) | Done |


## Notebooks and analyses

### Compare_proposals_rephrased.ipynb
#### Notebook Scope and Global Settings

Notebook title: `# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)`.

Purpose: compare Human and AI research proposals after all proposal texts have been rephrased by `gemini-2.0-flash` into a standardized neutral academic style. The notebook states that the analyses mirror `compare_proposals_baseline.ipynb`, but all inputs are the rephrased proposal artifacts.

Global condition and paths:
- `condition = 'rephrased/minimal'`.
- Proposal inputs are loaded from prepared artifacts in `results/tables/rephrased/minimal/prepared/`, primarily `all_proposals.json`.
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

Loads `results/tables/rephrased/minimal/prepared/all_proposals.json` if present, otherwise falls back to `results/tables/rephrased/minimal/all_proposals.json`. Each record is split into `ai_df` or `human_df` based on `is_ai`. The notebook stores title, model, cohort, source file, `standardized_text`, `abstract_text`, `main_idea`, and group labels. Expected group structure in the completed run is `23` Human proposals and `69` AI proposals, with `23` each for Claude, Gemini, and GPT-5.2.

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
- Centroids already computed for Human, each AI model, and All AI combined.

Step-by-step:
1. Build a centroid dictionary in stable order: Human, each AI model, All AI combined.
2. Stack centroids into a matrix.
3. Compute a full pairwise cosine-distance matrix among group centroids.
4. Print the pairwise centroid-distance matrix.
5. Convert upper-triangle centroid pairs to long format and rank pair separations from largest to smallest.
6. For each group, compute mean and median distance from that group's centroid to all other group centroids.
7. Save pairwise and per-group centroid-dispersion tables.

Primary estimand:
- Descriptive between-group separation among group centroids; no inferential test is run in this cell.

Export/status:
- Tables include `between_group_centroid_pairwise_distances.csv` and `between_group_centroid_dispersion.csv`.
- Compact table marks this as added, with run pending in that earlier summary.

##### `## Analysis 1.3: Nearest-Neighbor Outlier Detection (Between Group)`

What data:
- Full-proposal BioLinkBERT embeddings for all Human and AI proposals combined.

Step-by-step:
1. Stack Human embeddings first and AI embeddings second.
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

##### `# PART I-B: Diversity of Main Ideas`

What data:
- `main_idea` text from the prepared rephrased proposal records, separately for Human and AI proposals.
- Main-idea embeddings are loaded from `proposal_embeddings_main_idea_only.pkl` or computed with the same BioLinkBERT model if cache is unavailable.

##### `## Analysis 1-B.1: Within-Group Pairwise Diversity of Main Ideas`

Step-by-step:
1. Compute upper-triangle within-group cosine distances for main-idea embeddings for Human, each AI model, and All AI combined.
2. Compute proposal-level mean distance-to-others for main ideas.
3. Print descriptive pairwise summaries by group.
4. Compare AI groups against Human using `run_group_comparison(..., n_permutations=10000, n_boot=5000, random_state=42)`.
5. Visualize main-idea pairwise diversity and save the figure.

Primary estimand:
- Mean difference in proposal-level pairwise diversity of extracted main ideas: `AI - Human`.

##### `## Analysis 1-B.2: Centroid Dispersion of Main Ideas`

Step-by-step:
1. Compute each group's main-idea centroid.
2. Compute cosine distance from every main-idea embedding to its group centroid.
3. Print mean, median, and SD by group.
4. Compare AI groups against Human with the shared inference framework.

Primary estimand:
- Mean difference in distance from main idea to own-group main-idea centroid.

##### `## Analysis 1-B.3: Nearest-Neighbor Distances for Main Ideas`

Step-by-step:
1. Stack Human and AI main-idea embeddings.
2. Compute global all-by-all cosine distances with diagonal set to infinity.
3. Compute each main idea's 1-NN distance.
4. Define main-idea outliers as distances above the 90th percentile.
5. Print group means, medians, and outlier counts.
6. Compare AI groups against Human using the shared inference framework.
7. Visualize NN distances and outlier threshold.

Primary estimand:
- Mean difference in main-idea 1-NN distance: `AI - Human`.

##### `## Analysis 1-B.4: Main-Idea Embedding Space (UMAP)`

Step-by-step:
1. Reduce main-idea embeddings with UMAP using `n_neighbors=15`, `min_dist=0.1`, `n_components=2`, `metric='cosine'`, `random_state=42`.
2. Plot Human and per-model AI main ideas, group centroids, and main-idea NN outliers.
3. Save the UMAP figure.

##### `## Analysis 1-B.5: Unique, Non-Overlapping Idea Concepts`

Step-by-step:
1. Set `OVERLAP_THRESHOLD = 0.8` cosine similarity.
2. Build within-group similarity graphs where an edge means two main ideas exceed the threshold.
3. Compute connected components, component sizes, pairwise overlap counts, and percentage of overlapping pairs within Human, each AI model, and All AI.
4. Compute cross-source Human-AI similarity matrix.
5. Count Human ideas with at least one AI counterpart above threshold and AI ideas with at least one Human counterpart above threshold.
6. Repeat cross-overlap diagnostics by individual AI model.
7. Visualize unique concept counts, component structure, overlap-pair percentages, and cross-source overlap rates.

Purpose:
- Diagnose whether diversity differences are due to duplicate/near-duplicate main ideas within a source or overlap between sources.

#### `# PART II: NOVELTY`

All Part II analyses compare proposal embeddings against the literature embedding corpus.

##### `## Step 1: Load Literature Corpus`

What data:
- Literature corpus metadata and abstracts from the prepared literature artifact associated with `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Completed run summary reports `n=39538` literature abstracts with dates from `2010-01-01` to `2026-05-25`.

Step-by-step:
1. Load the literature corpus and search-query metadata.
2. Print article count and number of search queries.
3. Visualize articles per search query and publication-year distribution.
4. Print search terms/queries used per category.

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

##### Unnumbered code cell: `COMPUTING NOVELTY SCORES`

Although the markdown headers jump from Step 2 to Step 4b, the code cell immediately after Step 2 computes the raw novelty scores.

Step-by-step:
1. Set `k = 10`.
2. For each proposal embedding, compute cosine distances to all literature embeddings.
3. Find the 10 nearest literature abstracts.
4. Define raw novelty as mean cosine distance to the 10 nearest literature neighbors.
5. Compute raw novelty separately for Human, All AI, and each AI model.
6. Store nearest-neighbor indices for later normalization and nearest-literature export.

Primary metric:
- `raw_novelty = mean distance to k=10 nearest literature abstracts`; higher means farther from existing literature.

##### `## Step 4b: Literature-Normalized Novelty Scores (Local Density)`

What data:
- Raw proposal-to-literature novelty scores and nearest literature-neighbor indices from the previous code cell.
- Literature-to-literature local density estimates.

Step-by-step:
1. Set `k = 10`, matching raw novelty.
2. Compute each literature article's within-literature kNN distance baseline.
3. For each proposal, use its nearest literature neighbors to estimate local literature density.
4. Compute local-density normalized novelty as:
   - `novelty_z`: raw novelty standardized relative to local neighbor density.
   - `novelty_ratio`: raw novelty divided by local density.
5. Compute Human, All AI, and per-model normalized scores.
6. Run Mann-Whitney, Cliff's delta, permutation, bootstrap CI, and Holm correction for z-score novelty comparisons against Human.
7. Visualize raw novelty, z-score novelty, and ratio novelty side by side, with reference lines for `z=0` and `ratio=1`.

Primary normalized estimand:
- Mean difference in local-density normalized novelty z-score: `AI - Human`.

Existing compact result:
- Broad AI-vs-Human difference disappears after normalization; All AI vs Human MW `p=0.9138`, Cliff's delta `δ=0.0158`.

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

##### `### Step 7C: Projection Reliability (Seed Sweep + PCA Reference)`

Step-by-step:
1. Use high-dimensional mean-10NN proposal-to-literature outlier flags as the reference.
2. Run t-SNE and UMAP seed sweeps over projection random seeds.
3. For each projection, compute trustworthiness at `k=5` and `k=10`.
4. Recompute 2D proposal-to-literature local distances and 2D outlier flags.
5. Measure overlap between high-dimensional and 2D outliers using Jaccard and related diagnostics.
6. Add PCA with `n_components=2`, `random_state=42` as a deterministic reference.
7. Save projection reliability diagnostics and summary figures.

Interpretation rule:
- Use high-dimensional novelty/outlier metrics for inference. Projection outlier locations are visual diagnostics only.

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
1. Build one row per proposal with `title`, `group`, `raw_novelty`, `novelty_z`, and `novelty_ratio`.
2. Compute top-10% thresholds separately for raw novelty, z novelty, and ratio novelty.
3. Add `is_most_novel_raw`, `is_most_novel_z`, and `is_most_novel_ratio`.
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
- Soft-topic permutation chi-square `p=0.0001`; Topic_2 Human-up and Topic_3 AI-up after FDR in the completed run.

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
- NMI `0.0887` (`p=0.0026`), ARI `0.1254` (`p=0.0013`), between/within ratio `1.2406` (`p=0.0022`).

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
- Style-only classifier AUROC `0.684 ± 0.102`, permutation `p=0.0230`.

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
- Style-adjusted NN differences become non-significant for All AI vs Human; MW `p=0.1582`, permutation `p=0.2716`.

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
4. Add in-memory proposal-level pairwise diversity and main-idea metrics when available.
5. Merge original proposal metadata, rephrased text, diversity metrics, novelty metrics, style metrics, literature outlier flags, and review scores into records.
6. Save combined records to `results/tables/rephrased/minimal/all_proposals.json`.
7. Print metrics coverage and a sanity check that `metrics.is_literature_outlier` matches the raw top-10% novelty flag when both are available.

Purpose:
- Produce a single proposal-level JSON artifact for downstream metric-score validation and cross-notebook integration.

#### Diversity Metric Definitions Aligned to Table-3 Naming

Current implementation status for future notebook edits:

1. **Remote-Clique** (`implemented partially`)
- Current Analysis 1.1 computes upper-triangle pairwise cosine distances for descriptions and proposal-level mean distance-to-others for inference.
- To report the exact Table-3 Remote-Clique value, add `RC = (1 / N^2) * sum_i sum_j d(x_i, x_j)` explicitly and export it by group.

2. **Chamfer Distance** (`implemented for k=1`)
- Current Analysis 1.3 implements the nearest-neighbor version: `CD = (1 / N) * sum_i min_{j != i} d(x_i, x_j)`.
- Analysis 1.3-B adds a mean-5NN robustness variant, not the canonical k=1 Chamfer value.

3. **MST Dispersion** (`to add`)
- Build a minimum spanning tree over each group's complete cosine-distance graph.
- Report mean MST edge length: `(1 / (N - 1)) * sum_{(i,j) in MST} d(x_i, x_j)`.

4. **Span** (`partial -> to add full`)
- Current Analysis 1.2 reports mean distance to centroid.
- Add percentile span, especially `Span_90 = percentile_90({d(x_i, centroid)})`, for direct Table-3 alignment.

5. **Sparseness** (`to add`)
- Compute the group medoid `m = argmin_j sum_i d(x_i, x_j)`.
- Report `Sparseness = (1 / N) * sum_i d(x_i, m)`.

6. **Entropy (grid-based embedding occupancy)** (`to add`)
- Project embeddings to 2D, partition into a `5 x 5` grid, compute occupancy frequencies, and report Shannon entropy plus a normalized entropy.
- Keep this distinct from the existing LDA topic entropy in Analysis 3.3.


### Compare_reviews_ncems_criteria.ipynb
#### Notebook Scope and Global Settings

Notebook title: `# PART IV QUALITY — Compare Human and AI Reviews (Style-Controlled / Rephrased)`.

Purpose: compare Human and AI reviews in the NCEMS criteria evaluation pipeline using reviews generated on rephrased proposals. The notebook mirrors the older `compare_reviews.ipynb` workflow but reads the prepared rephrased review artifact.

Global condition and paths:
- `condition = 'minimal'`.
- Primary prepared input: `results/tables/rephrased/minimal/prepared/ncems_criteria_all_reviews.csv`.
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
4. Require the prepared review table at `results/tables/rephrased/minimal/prepared/ncems_criteria_all_reviews.csv`; fail early if it is missing.
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
- `quality_proxy_validity_metrics.csv`
- `quality_proxy_rank_agreement.csv`
- `quality_proxy_icc.csv`

Note:
- The notebook exports proxy validity/rank agreement/ICC tables if those objects exist in the runtime; they are included in the export cell even though the visible markdown spine focuses on Sections 8-14.

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
- `quality_similarity_four_group_y1_y2.png`.

Tables created later:
- `quality_similarity_four_group_y1_y2_values.csv`
- `quality_similarity_four_group_y1_y2_pairwise_tests.csv`
- `quality_similarity_within_cohort_human_vs_ai_tests.csv`

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
- `quality_y2_reliability_icc_heatmap.png`
- `quality_y2_human_vs_ai_overall_scatter.png`

#### `## 23) Export Y2 + Y1Y2 Added Outputs`

Exports:
- `quality_matching_map_y1_rephrased_reviews.csv`
- `quality_matching_map_y2_rephrased_reviews.csv`
- `quality_similarity_pairs_y1_rephrased_reviews.csv`
- `quality_similarity_pairs_y2_rephrased_reviews.csv`
- `quality_similarity_four_group_y1_y2_values.csv`
- `quality_similarity_four_group_y1_y2_pairwise_tests.csv`
- `quality_similarity_within_cohort_human_vs_ai_tests.csv`
- `quality_y2_reliability_human_ai.csv`

Figures printed as saved:
- `quality_similarity_four_group_y1_y2.png`
- `quality_y2_reliability_icc_heatmap.png`
- `quality_y2_human_vs_ai_overall_scatter.png`

#### Compact Results Already Reflected Elsewhere

- NCEMS quality conclusions are substantial but partially sensitive to evaluator composition and self-preference structure.
- Raw evaluator pool: GPT-5.2 and Claude score above Human-all; Gemini is closer but still significant in the raw pool.
- After removing AI self-evaluations, Gemini no longer differs significantly from Human-all, while Claude and GPT-5.2 remain above Human-all.


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
- Proposal-level data integration (`92 x 52`).
- Spearman metric-score correlation analysis.
- Outlier score-comparison tests.
- Added Human-Y2 metric-score analysis block in:
  - `notebooks/templates/rephrased/metric_score_relationship.ipynb`

Key findings:
- Strong negative associations between semantic-distance metrics and NCEMS-type scores were observed (example: `mi_pairwise_mean_dist` vs `relevance_to_emergent_phenomena`, `r=-0.6496`).
- Positive associations appeared with novelty-oriented criteria (example: `centroid_dist` vs `new_theory_concept_method_dataset_or_design`, `r=0.5093`).
- Outlier proposals tended to score lower on key NCEMS dimensions, but could score higher on at least one novelty criterion (`new_theory...`, `p=0.0273`).

Interpretation:
- Embedding “novelty/remoteness” aligns differently with conservative quality criteria vs novelty-emphasizing criteria, indicating a clear evaluation-tradeoff structure.

## Updated Overall Story

- Human proposals are consistently more semantically spread and isolated than AI proposals in baseline raw-space diversity metrics.
- Novelty results are nuanced: raw literature distance favors Human over some AI groups, but density-normalized novelty removes broad significance.
- Human and AI proposals occupy different semantic/topic regions, and this separation remains visible even after several robustness checks.
- Style contributes to separation, but does not fully explain all effects; centroid-level differences remain after style control while NN outlier differences weaken.
- Review outcomes are highly dependent on rubric and evaluator effects. Some AI groups score higher under NCEMS, while novelty-framework conclusions are mixed and sensitive to self-evaluation removal.
- Overall, the study supports a **tradeoff narrative** rather than a simple “AI better vs Human better” claim: semantic remoteness, rubric design, and evaluator bias jointly shape conclusions.

## UPDATE LOGS
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

2. **Stable rephrased review outputs (no timestamped run outputs)**
- Human Y1: `data/reviews/human_reviews/rephrased/human_reviews_human-y1_rephrased.csv`
- Human Y2: `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased.csv`
- AI NCEMS: `data/reviews/ai_reviews/minimal/ncems_criteria/rephrased/ncems_reviews_rephrased.json`

3. **`compare_reviews_ncems_criteria.ipynb` updated**
- Notebook path: `notebooks/templates/rephrased/compare_reviews_ncems_criteria.ipynb`.
- AI reviews now load from the **rephrased directory** with condition-based glob:
  - `data/reviews/ai_reviews/<condition>/ncems_criteria/rephrased/ncems_reviews_rephrased*.json`
- Human reviews now load from the **rephrased directory** with glob:
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y1_rephrased*.csv`
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased*.csv`
- Review text field now uses `rephrased_review` (with compatibility fallback only if legacy naming appears).

4. **Y2 review analyses now incorporated in the notebook**
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
