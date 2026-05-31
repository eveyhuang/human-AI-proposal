
# Codex Patch Plan for `compare_proposals_rephrased.ipynb`

This document is a **literal notebook patch plan** for revising `compare_proposals_rephrased.ipynb` in place. It preserves the current notebook spine and conventions. It also adds the missing literature-aligned diversity and novelty metrics while minimizing recomputation by caching reusable matrices once.

---

## 0. Patch goals

Codex should revise the notebook so that it:

1. Preserves the current:
   - embedding model: `michiyasunaga/BioLinkBERT-large`
   - cosine-distance embedding analysis
   - proposal-level inferential workflow
   - export structure under `results/tables/rephrased/minimal/` and `results/figures/rephrased/minimal/`

2. Adds literature-aligned metrics:
   - **Diversity:** exact Remote-Clique, exact Chamfer, MST Dispersion, Span-90, Sparseness, grid entropy
   - **Novelty:** ElementNovel_0/1/5/10 and MeanKNN_5/10/20/50

3. Computes reusable matrices only once:
   - proposal-proposal cosine distance matrix
   - proposal-literature cosine distance matrix
   - literature self-kNN cache up to `k=50`

4. Updates the export layer so the notebook produces one canonical:
   - `proposal_metrics_master.csv`
   - refreshed `all_proposals.json`

---

## 1. Exact notebook surgery plan

### 1.1 Keep these notebook sections and helpers

Keep the current sections:

- `# Setup and Imports`
- `## Helper Functions`
- `## Load Prepared Proposal Data`
- `## Prepare Proposal Texts`
- `## Load Prepared Full-Proposal Embeddings`
- `# PART I: DIVERSITY`
- `# PART II: NOVELTY`
- `# PART III: THEMATIC AND CLUSTER ANALYSIS`
- `# PART IV Style Baseline`
- `# Save All Proposals to a Single JSON`

Keep the current helper framework and file/path conventions already documented in the notebook plan.

### 1.2 Add new helper functions inside `## Helper Functions`

Codex should **append** the following new helper functions to the existing helper section rather than creating a separate utility file.

#### A. Matrix / group utilities
- `build_group_indices(proposal_meta)`
- `get_group_submatrix(D, idx)`
- `sort_distance_rows(D)`
- `safe_percentile(arr, q)`

#### B. Proposal-level diversity metrics
- `proposal_mean_pairwise_from_submatrix(Dg)`
- `proposal_min_pairwise_from_submatrix(Dg)`
- `proposal_mean_knn_from_submatrix(Dg, k=5)`
- `proposal_centroid_distances(Xg, leave_one_out=False)`
- `proposal_global_centroid_distances(X_all, idx_group)`
- `proposal_medoid_distances(Dg)`

#### C. Group-level diversity metrics
- `group_remote_clique(Dg)`
- `group_chamfer(Dg)`
- `group_mst_dispersion(Dg)`
- `group_span_percentile(Xg, q=90)`
- `group_medoid_index(Dg)`
- `group_sparseness(Dg)`
- `group_grid_entropy(coords_2d, idx_group, bins=5, normalize=True)`

#### D. Novelty metrics
- `compute_element_novel_percentiles(D_pl, q_list=[0,1,5,10])`
- `compute_mean_knn_novelty(D_pl_sorted_dist, ks=[5,10,20,50])`
- `compute_local_density_normalized_novelty(mean_knn_10, proposal_top10_lit_idx, lit_mean_knn_10)`

#### E. Group-level permutation/bootstrap helpers
- `bootstrap_group_metric(X_or_D, metric_fn, n_boot=5000, random_state=42, metric_type="distance")`
- `permutation_test_group_metric(X_prop, labels, idx_a, idx_b, metric_fn, n_perm=10000, random_state=42, use_distance_submat=False)`

#### F. Outlier helpers
- `flag_top_percentile(values, pct=90, strict=True)`
- `fisher_group_prevalence_tests(flag_series, group_series, reference_group="Human")`

---

## 2. Insert one new precompute block after proposal embeddings load

### 2.1 Insert new markdown cell
Insert this markdown cell immediately after `## Load Prepared Full-Proposal Embeddings`:

```markdown
## Shared Distance-Matrix Precomputation

This block computes and caches the reusable proposal-space and literature-space distance objects used throughout Part I and Part II. All later sections should reuse these objects rather than recomputing distances.
```

### 2.2 Insert new code cell
Insert one code cell right after that markdown block.

#### Cell responsibilities
1. Build canonical proposal metadata order
2. Build normalized stacked proposal matrix `X_prop`
3. Build group index dictionary
4. Compute proposal-proposal similarity and distance
5. Precompute proposal PCA 2D coordinates for entropy and deterministic plotting
6. Build reusable `group_cache`

#### Expected code shape
```python
# Canonical proposal metadata in embedding order
proposal_meta = pd.DataFrame({
    "title": [...],
    "group_model": [...],
    "group_binary": [...],
    "is_ai": [...],
    "source_file": [...],
})

proposal_meta["proposal_uid"] = [f"P_{i:03d}" for i in range(len(proposal_meta))]

# X_prop in exact row order of proposal_meta
X_prop = np.vstack([human_embeddings, ai_embeddings]).astype(np.float32)

# L2 normalize once
X_prop = X_prop / np.linalg.norm(X_prop, axis=1, keepdims=True)

GROUPS = build_group_indices(proposal_meta)

# proposal-proposal cosine distance
S_pp = X_prop @ X_prop.T
D_pp = 1.0 - S_pp
np.fill_diagonal(D_pp, 0.0)

D_pp_infdiag = D_pp.copy()
np.fill_diagonal(D_pp_infdiag, np.inf)

# deterministic 2D reference
pca_2d = PCA(n_components=2, random_state=42).fit_transform(X_prop)

group_cache = {}
for g, idx in GROUPS.items():
    Dg = D_pp[np.ix_(idx, idx)]
    Xg = X_prop[idx]
    group_cache[g] = {"idx": idx, "D": Dg, "X": Xg, "n": len(idx)}
```

#### Add save-to-cache behavior
Codex should optionally persist:
- `proposal_distance_matrix.npy`
- `proposal_pca2d.npy`
- `proposal_meta.csv`

under a subdirectory like:
- `results/tables/rephrased/minimal/cached/`

---

## 3. PART I patch plan

# PART I: DIVERSITY

Codex should **keep** the current section headings where possible, but revise the internal code and outputs as follows.

---

## 3.1 Patch `## Analysis 1.1: Within-Group Pairwise Diversity`

### Replace current internal logic with a two-level output:
1. exact **Remote-Clique**
2. proposal-level **mean pairwise distance**

### Keep the section heading, but rename it to:
```markdown
## Analysis 1.1: Within-Group Pairwise Diversity (Remote-Clique + proposal-level mean pairwise distance)
```

### Code requirements
For each group in `GROUPS`:

#### Group-level exact metric
\[
RC(G) = \frac{1}{N^2} \sum_{i=1}^{N}\sum_{j=1}^{N} d(x_i, x_j)
\]

#### Proposal-level metric
\[
MPD_i = \frac{1}{N-1}\sum_{j \ne i} d(x_i, x_j)
\]

### Cell outputs
Create:
- `pairwise_group_summary_df`
- `pairwise_proposal_df`
- `pairwise_tests_df`

#### `pairwise_group_summary_df` columns
- `group`
- `n`
- `remote_clique`
- `upper_tri_mean`
- `upper_tri_median`
- `upper_tri_sd`
- `proposal_mean_pairwise_mean`
- `proposal_mean_pairwise_median`
- `proposal_mean_pairwise_sd`
- `proposal_mean_pairwise_iqr`

#### `pairwise_proposal_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `mean_pairwise_dist`

### Inference
Run `run_group_comparison()` on `mean_pairwise_dist` for:
- Claude vs Human
- Gemini vs Human
- GPT vs Human
- AllAI vs Human

Apply Holm correction to:
- MW p-values
- permutation p-values

### Exports
Write:
- `diversity_remote_clique_group_summary.csv`
- `diversity_pairwise_proposal_level.csv`
- `diversity_pairwise_tests.csv`

### Keep / update plots
Reuse the current pairwise-distribution plotting cell but update captions/labels to note:
- proposal-level mean pairwise distance is the inferential variable
- Remote-Clique is the exact collective metric

---

## 3.2 Patch `## Analysis 1.2: Centroid Dispersion Metric`

### Keep section heading but rename to:
```markdown
## Analysis 1.2: Centroid Dispersion Metric (mean radius + Span-90)
```

### Replace internal code so it computes both:
1. raw centroid distance
2. leave-one-out centroid distance
3. Span-90

#### Raw centroid distance
\[
d_i^{raw} = d(x_i, c_G)
\]

#### Leave-one-out centroid distance
\[
d_i^{LOO} = d(x_i, c_{G,-i})
\]

#### Span-90
\[
Span_{90}(G) = P_{90}(d(x_i, c_G))
\]

### Cell outputs
Create:
- `centroid_proposal_df`
- `span90_group_summary_df`
- `centroid_tests_df`

#### `centroid_proposal_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `centroid_dist_raw`
- `centroid_dist_loo`

#### `span90_group_summary_df` columns
- `group`
- `n`
- `centroid_mean_raw`
- `centroid_median_raw`
- `centroid_sd_raw`
- `centroid_var_raw`
- `centroid_mean_loo`
- `centroid_median_loo`
- `centroid_sd_loo`
- `span_90`

### Inference
Use `centroid_dist_loo` as the primary proposal-level inferential variable.

### Keep export compatibility
Keep writing:
- `centroid_distances.csv`

But update it so it includes both:
- `centroid_dist_raw`
- `centroid_dist_loo`

Also export:
- `diversity_span90_group_summary.csv`
- `diversity_centroid_pairwise_tests.csv`

### Plotting
Update the existing centroid plot so it can show:
- proposal-level distribution using `centroid_dist_loo`
- group-level Span-90 as annotation or companion summary table

---

## 3.3 Keep and patch `## Analysis 1.2b: Between-Group Centroid Dispersion`


### Section heading remains:
```markdown
## Analysis 1.2b: Between-Group Centroid Dispersion
```

### Code requirements
Compute one global centroid:
\[
c_{global} = \frac{1}{N} \sum_{i=1}^{N} x_i
\]

For every proposal:
\[
global\_centroid\_dist_i = d(x_i, c_{global})
\]

### Outputs
Create:
- `between_group_global_centroid_df`
- `between_group_global_centroid_summary_df`
- `between_group_global_centroid_tests_df`

#### `between_group_global_centroid_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `global_centroid_dist`

### Inference
Use proposal-level `global_centroid_dist`.

### Exports
Keep the same filenames already planned:
- `between_group_global_centroid_distances.csv`
- `between_group_global_centroid_group_summary.csv`
- `between_group_global_centroid_pairwise_tests.csv`

### Plot
Keep your current between-group centroid dispersion figure.

---

## 3.4 Insert new section after 1.3-B:
```markdown
## Analysis 1.2c: MST Dispersion
```

### Code requirements
For each within-group distance matrix `Dg`, compute MST Dispersion:

\[
MSTDisp(G)=\frac{1}{N-1}\sum_{e \in MST(G)} w_e
\]

### Outputs
Create:
- `mst_group_summary_df`
- `mst_pairwise_perm_df`

#### `mst_group_summary_df` columns
- `group`
- `n`
- `mst_dispersion`
- `mst_boot_mean`
- `mst_boot_ci_low`
- `mst_boot_ci_high`

### Inference
Because MST is collective:
- bootstrap within each group
- permutation tests for Human vs each AI group

### Comparisons
- Claude vs Human
- Gemini vs Human
- GPT vs Human
- AllAI vs Human

### Exports
- `diversity_mst_group_summary.csv`
- `diversity_mst_pairwise_permutation.csv`

---

## 3.5 Insert new section after 1.2c:
```markdown
## Analysis 1.2d: Sparseness (Medoid-Based Dispersion)
```

### Code requirements
For each group:
1. find medoid:
\[
m = \arg\min_j \sum_i d(x_i, x_j)
\]

2. compute proposal-level medoid distance:
\[
medoid\_dist_i = d(x_i, m)
\]

3. compute exact Sparseness:
\[
Sparseness(G)=\frac{1}{N}\sum_i d(x_i, m)
\]

### Outputs
Create:
- `medoid_proposal_df`
- `sparseness_group_summary_df`
- `sparseness_tests_df`

#### `medoid_proposal_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `medoid_dist`

### Inference
Use proposal-level `medoid_dist`.

### Exports
- `diversity_medoid_distances.csv`
- `diversity_sparseness_group_summary.csv`
- `diversity_sparseness_pairwise_tests.csv`

---

## 3.6 Patch `## Analysis 1.3: Nearest-Neighbor Outlier Detection (Between Group)`

### Rename section to:
```markdown
## Analysis 1.3: Nearest-Neighbor Isolation and Outlier Detection (Chamfer / NN)
```

### Keep all first-class outputs:
- global 1-NN distances
- pooled 90th percentile outliers
- nearest-neighbor source composition
- outlier titles
- Human vs AI inferential tests

### Add exact within-group Chamfer summary
For each group submatrix `Dg`:

\[
Chamfer(G) = \frac{1}{N}\sum_{i=1}^{N} \min_{j \ne i} d(x_i, x_j)
\]

### Proposal-level global NN metric
For full `D_pp_infdiag`:
- `nn_dist_global`
- `nn_index_global`
- `nn_group_global`

### Outputs
Create:
- `nn_proposal_df`
- `chamfer_group_summary_df`
- `nn_tests_df`
- `nn_source_composition_df`

#### `nn_proposal_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `nn_dist_global`
- `nn_neighbor_proposal_uid`
- `nn_neighbor_group_model`
- `is_nn_outlier`

### Threshold
\[
nn\_outlier\_threshold = P_{90}(nn\_dist\_global)
\]

### Inference
Use `nn_dist_global` as the proposal-level inferential variable.

### Exports
Keep:
- `nn_distances.csv`

Add:
- `diversity_chamfer_group_summary.csv`
- `nearest_neighbor_source_composition.csv`
- `diversity_nn_pairwise_tests.csv`

### Visualization
Keep the UMAP outlier ring visualization, but do not recompute distances inside that block.

---

## 3.7 REMOVE `## Analysis 1.3-B: Mean k-NN Outlier Detection (k=5)`

Remove this whole section

---



## 3.8 Insert new section after 1.3:
```markdown
## Analysis 1.4: Grid Entropy of Proposal Occupancy
```

### Code requirements
Use fixed PCA coordinates already computed once.

For each group:
- compute 5×5 occupancy grid
- compute entropy
- compute normalized entropy

\[
H = -\sum_b p_b \log p_b
\]

### Outputs
Create:
- `entropy_group_summary_df`

#### Columns
- `group`
- `n`
- `grid_entropy`
- `grid_entropy_normalized`
- `bins`
- `projection_method`

### Export
- `diversity_entropy_group_summary.csv`

### Note
Keep this distinct from LDA topic entropy in Part III.

---

## 3.9 Diversity figure cleanup patch

Codex should modify the diversity plotting blocks so they:

### Keep in main notebook
- pairwise-diversity figure
- centroid-dispersion figure
- between-group global-centroid figure
- NN isolation figure
- one UMAP proposal scatter
- one PCA proposal scatter

### Move to optional / appendix cells
- duplicate t-SNE versions
- repeated outlier overlays that do not add new information

---

## 4. PART II patch plan

# PART II: NOVELTY

---

## 4.1 Patch literature loading / embedding section by adding a new shared precompute block

Immediately after literature embeddings are loaded, insert:

```markdown
## Shared Novelty Precomputation

This block computes reusable proposal-to-literature distance objects and literature local-density baselines used by all later novelty analyses.
```

### Insert one code cell under that markdown
Responsibilities:
1. L2 normalize `X_lit`
2. compute `D_pl`
3. compute sorted rowwise proposal→literature distances and indices
4. compute literature self-kNN cache summaries at k = 5, 10, 20, 50

#### Expected code shape
```python
X_lit = X_lit / np.linalg.norm(X_lit, axis=1, keepdims=True)

S_pl = X_prop @ X_lit.T
D_pl = 1.0 - S_pl

D_pl_sorted_idx = np.argsort(D_pl, axis=1)
D_pl_sorted_dist = np.take_along_axis(D_pl, D_pl_sorted_idx, axis=1)

# literature self-kNN cache already loaded or computed
lit_mean_knn_5 = lit_knn_distances_50[:, :5].mean(axis=1)
lit_mean_knn_10 = lit_knn_distances_50[:, :10].mean(axis=1)
lit_mean_knn_20 = lit_knn_distances_50[:, :20].mean(axis=1)
lit_mean_knn_50 = lit_knn_distances_50[:, :50].mean(axis=1)
```

---

## 4.2 Insert new section before the current STEP 3 COMPUTE NOVELTY SCORE section:
```markdown
## Step 2.5: Element Novelty Percentiles
```

### Code requirements
For each proposal:
- `element_novel_0 = D_pl_sorted_dist[:, 0]`
- `element_novel_1 = np.percentile(D_pl, 1, axis=1)`
- `element_novel_5 = np.percentile(D_pl, 5, axis=1)`
- `element_novel_10 = np.percentile(D_pl, 10, axis=1)`

### Outputs
Create:
- `element_novelty_df`
- `element_novelty_tests_df`

#### `element_novelty_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `element_novel_0`
- `element_novel_1`
- `element_novel_5`
- `element_novel_10`

### Inference
Run proposal-level group comparisons for each element novelty metric.

### Exports
- `novelty_element_percentiles.csv`
- `novelty_element_percentiles_pairwise_tests.csv`

---

## 4.3 Patch the current raw novelty block into a full Mean-kNN block

Replace the current  `STEP 3 COMPUTING NOVELTY SCORES` block with a new section:

```markdown
## Step 3: Raw Novelty Scores (Mean k-NN to Literature)
```

### Code requirements
For each proposal compute:
- `mean_knn_5`
- `mean_knn_10`
- `mean_knn_20`
- `mean_knn_50`

from the already-sorted `D_pl_sorted_dist`.

### Outputs
Create:
- `mean_knn_novelty_df`
- `mean_knn_novelty_tests_df`

#### `mean_knn_novelty_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `mean_knn_5`
- `mean_knn_10`
- `mean_knn_20`
- `mean_knn_50`

### Inference
Use:
- `mean_knn_10` as primary continuity metric
- other k values as robustness

### Exports
- `novelty_mean_knn_scores.csv`
- `novelty_mean_knn_pairwise_tests.csv`

---



---

## 4.5 Patch `## Step 5: Statistical Tests for Novelty`

This section should no longer only test raw `k=10` mean novelty. It should become a combined statistical-report section for:

1. ElementNovel family
2. MeanKNN family
3. normalized novelty family

### New section title
```markdown
## Step 5: Statistical Tests for Novelty Metrics
```

### Outputs
Create one long-format table:
- `novelty_all_pairwise_tests_df`

#### Required columns
- `metric_family`
- `metric_name`
- `comparison`
- `group1`
- `group2`
- `n_group1`
- `n_group2`
- `u_stat`
- `p_value`
- `q_value_holm`
- `cliffs_delta`
- `delta_magnitude`
- `perm_p_value`
- `perm_q_value_holm`
- `mean_diff`
- `median_diff`
- `boot_ci_low`
- `boot_ci_high`

### Export
- `novelty_all_pairwise_tests.csv`

---

## 4.6 Patch `## Step 6: Visualize Novelty Results`

Revise into a three-panel novelty figure section.

### Panel A
ElementNovel distributions:
- 0, 1, 5, 10 percentiles

### Panel B
MeanKNN k-sensitivity:
- k = 5, 10, 20, 50

### Panel C
Normalized novelty:
- `novelty_z`
- `novelty_ratio`

### Exports
- `novelty_analysis_element_percentiles.png`
- `novelty_analysis_mean_knn.png`
- `novelty_analysis_local_density.png`

---

## 4.7 Patch `### Step 7B: Recompute Literature-Space Outliers`

Keep this section as a first-class analysis and expand it.

### New section title
```markdown
### Step 7B: Literature-Space Outliers and High-Novelty Flags
```

### Code requirements
Create three primary binary flags:

1. `is_lit_outlier_mean10`
   - top 10% of `mean_knn_10`

2. `is_lit_outlier_element0`
   - top 10% of `element_novel_0`

3. `is_lit_outlier_z`
   - top 10% of `novelty_z` among non-missing rows

### Outputs
Create:
- `lit_outlier_flags_df`
- `lit_outlier_prevalence_tests_df`

#### `lit_outlier_flags_df` columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `mean_knn_10`
- `element_novel_0`
- `novelty_z`
- `is_lit_outlier_mean10`
- `is_lit_outlier_element0`
- `is_lit_outlier_z`

### Tests
For each flag:
- counts by group
- percentages by group
- Fisher exact tests Human vs each AI group
- Holm correction within flag family

### Keep exports
Keep:
- `literature_space_outliers_mean_knn_k10.csv`

Add:
- `literature_space_outliers_element0.csv`
- `literature_space_outliers_z.csv`
- `literature_space_outlier_prevalence_tests.csv`

---

## 4.8 Keep and patch `## Additional Analysis: Nearest Neighbors in Literature for Every Proposal`

Keep this as a first-class section.

### Section title can remain, but update internal code
Do **not** recompute proposal-to-literature distances. Pull from `D_pl_sorted_idx` and `D_pl_sorted_dist`.

### Outputs
Create:
- `nearest_literature_neighbors_df`

#### Columns
- `proposal_uid`
- `proposal_title`
- `proposal_group_model`
- `neighbor_rank`
- `lit_doc_id`
- `lit_title`
- `lit_year`
- `lit_distance`
- `lit_query_category`
- `lit_abstract_preview`

### Export
- `nearest_literature_neighbors_top3.csv`

### Print tables
Print:
- top 10 proposals with largest `mean_knn_10`
- top 10 proposals with smallest `mean_knn_10`
- top 10 proposals with largest `element_novel_0`

---

## 4.9 Patch the `novelty_scores_from_literature.csv` export cell

Replace this with a unified novelty export that merges:
- ElementNovel metrics
- MeanKNN metrics
- normalized novelty metrics
- literature-space outlier flags

### New main export
- `novelty_scores_from_literature.csv`

### Required columns
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `element_novel_0`
- `element_novel_1`
- `element_novel_5`
- `element_novel_10`
- `mean_knn_5`
- `mean_knn_10`
- `mean_knn_20`
- `mean_knn_50`
- `novelty_ratio`
- `novelty_z`
- `is_lit_outlier_mean10`
- `is_lit_outlier_element0`
- `is_lit_outlier_z`

---



## 5. Build master metric table at end of Part II

Insert a new markdown cell before `# PART III`:

```markdown
## Unified Proposal-Level Metric Export
```

### Insert one code cell under it

This cell should merge all Part I and Part II outputs into one canonical dataframe:

`proposal_metrics_master_df`

### Required columns

#### Metadata
- `proposal_uid`
- `title`
- `group_model`
- `group_binary`
- `is_ai`

#### Diversity proposal-level
- `mean_pairwise_dist`
- `centroid_dist_raw`
- `centroid_dist_loo`
- `global_centroid_dist`
- `nn_dist_global`
- `mean_5nn_dist_global`
- `medoid_dist`

#### Diversity group-level
- `remote_clique_group`
- `chamfer_group`
- `mst_dispersion_group`
- `span90_group`
- `sparseness_group`
- `grid_entropy_group`
- `grid_entropy_group_norm`

#### Diversity flags
- `is_nn_outlier`
- `is_mean5nn_outlier`

#### Novelty continuous
- `element_novel_0`
- `element_novel_1`
- `element_novel_5`
- `element_novel_10`
- `mean_knn_5`
- `mean_knn_10`
- `mean_knn_20`
- `mean_knn_50`
- `novelty_ratio`
- `novelty_z`

#### Novelty flags
- `is_lit_outlier_mean10`
- `is_lit_outlier_element0`
- `is_lit_outlier_z`

### Export
Write:
- `proposal_metrics_master.csv`

---

## 6. Patch the final JSON merge section

Inside `# Save All Proposals to a Single JSON`, update the merge logic so it loads:

- `proposal_metrics_master.csv`
- `style_features.csv`
- `review_scores_wide.csv`

and uses `proposal_uid` plus normalized title as the preferred merge keys.

### Keep backward-compatible sanity checks
Keep the current coverage printouts and metric coverage diagnostics.

### Add new sanity checks
Print:
- whether every proposal has a row in `proposal_metrics_master.csv`
- counts of missing values by metric family
- whether literature outlier flags align with source novelty columns

---

## 7. Export checklist Codex should guarantee

At the end of notebook execution, the following should exist:

### Diversity tables
- `diversity_remote_clique_group_summary.csv`
- `diversity_pairwise_proposal_level.csv`
- `diversity_pairwise_tests.csv`
- `centroid_distances.csv`
- `diversity_span90_group_summary.csv`
- `diversity_centroid_pairwise_tests.csv`
- `between_group_global_centroid_distances.csv`
- `between_group_global_centroid_group_summary.csv`
- `between_group_global_centroid_pairwise_tests.csv`
- `nn_distances.csv`
- `diversity_chamfer_group_summary.csv`
- `nearest_neighbor_source_composition.csv`
- `diversity_nn_pairwise_tests.csv`
- `mean_knn_distances_k5.csv`
- `diversity_mst_group_summary.csv`
- `diversity_mst_pairwise_permutation.csv`
- `diversity_medoid_distances.csv`
- `diversity_sparseness_group_summary.csv`
- `diversity_sparseness_pairwise_tests.csv`
- `diversity_entropy_group_summary.csv`

### Novelty tables
- `novelty_element_percentiles.csv`
- `novelty_element_percentiles_pairwise_tests.csv`
- `novelty_mean_knn_scores.csv`
- `novelty_mean_knn_pairwise_tests.csv`
- `novelty_local_density_normalized.csv`
- `novelty_local_density_pairwise_tests.csv`
- `novelty_all_pairwise_tests.csv`
- `literature_space_outliers_mean_knn_k10.csv`
- `literature_space_outliers_element0.csv`
- `literature_space_outliers_z.csv`
- `literature_space_outlier_prevalence_tests.csv`
- `nearest_literature_neighbors_top3.csv`
- `novelty_scores_from_literature.csv`

### Unified export
- `proposal_metrics_master.csv`

---

## 8. Minimal pseudocode block Codex can follow

```python
# 1. Build proposal_meta and X_prop
# 2. Normalize X_prop
# 3. Compute D_pp once
# 4. Build GROUPS and group_cache
# 5. PART I metrics from D_pp / group_cache
# 6. Load / normalize X_lit
# 7. Compute D_pl once
# 8. Build sorted D_pl rows and literature self-kNN summaries
# 9. PART II metrics from D_pl
# 10. Merge all metrics into proposal_metrics_master_df
# 11. Export CSVs
# 12. Update all_proposals.json
```

---

## 9. Final instruction block to paste into Codex

```text
Patch compare_proposals_rephrased.ipynb in place using the attached plan.

Requirements:
- Keep the notebook structure and current helper/testing conventions.
- Keep proposal-space and literature-space outlier analyses as first-class outputs.
- Keep the nearest-neighbor literature audit as a first-class output.
- Add these metrics:
  - Diversity: exact Remote-Clique, exact Chamfer, MST Dispersion, Span-90, Sparseness, grid entropy
  - Novelty: ElementNovel_0/1/5/10 and MeanKNN_5/10/20/50
- Compute reusable matrices only once:
  - proposal-proposal cosine distance matrix
  - proposal-literature cosine distance matrix
  - literature self-kNN cache up to k=50
- Reuse cached objects in all later sections.
- Export all CSVs listed in the plan, plus proposal_metrics_master.csv.
- Update all_proposals.json so it cleanly merges the new metric outputs.
- Do not remove the current local-density normalized novelty section.
- Do not demote outlier analyses or nearest-neighbor literature audit.
- Reduce duplicated visualization/recomputation where possible.
```
