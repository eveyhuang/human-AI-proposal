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
- Literature corpus for novelty: `n=1030` abstracts.
- Review datasets parsed for metric-score integration: `276` NCEMS reviews + `276` novelty-framework reviews.
- Human Y2 quantitative review scores for metric-score linkage:
  - `data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased.csv`

## Review Rephrasing + Notebook Path Updates (2026-05-25)

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

### 1) Diversity in embedding space (Part 2-I)

Analyses completed:
- Within-group pairwise diversity (**Remote-Clique** family).
- Centroid dispersion (mean distance to centroid; **related to Span** but not percentile-based Span yet).
- Between-group centroid dispersion (new Analysis 1.2b): pairwise centroid distance matrix, separation ranking, and per-group mean distance to other group centroids.
- Global nearest-neighbor (1-NN) isolation and outlier detection (top 10% rule; **Chamfer/NN family**).
- Embedding visualizations (UMAP/t-SNE, descriptive).
- Main-idea sub-analyses (pairwise/centroid/NN + overlap diagnostics).

Key findings:
- Human proposals were more diverse than All AI on pairwise distance (Human mean `0.4429` vs All AI `0.1826`; MW `p=3.99e-08`, Holm `p=1.20e-07`, `δ=-0.7681`).
- Human proposals were more dispersed from centroid (Human `0.2413` vs All AI `0.0945`; MW `p=3.99e-08`, Holm `p=1.20e-07`, `δ=-0.7681`).
- Human proposals were more isolated by 1-NN (Human `0.0739` vs All AI `0.0323`; MW `p=1.28e-06`, Holm `p=5.13e-06`, `δ=-0.6774`).
- Global 1-NN outlier prevalence was higher in Human (`30.4%`) than All AI (`4.3%`).
- Main-idea analyses generally pointed in the same direction, but permutation support was mixed in some pairwise/centroid comparisons.

Interpretation:
- In the baseline minimal condition, Human proposals occupy a broader and more isolated semantic space than AI proposals in raw embedding analyses.

#### Diversity metric definitions aligned to Table-3 naming (for all conditions)

Use cosine distance `d(x_i, x_j)` on embeddings. Compute each metric within each group (Human, Claude, Gemini, GPT-5.2, All AI), then compare groups with the same inferential framework already used (MW, Cliff's delta, permutation, multiple-testing correction).

1. **Remote-Clique** (`implemented`)
- Definition (match screenshot): `RC = (1 / N^2) * sum_{i=1..N} sum_{j=1..N} d(x_i, x_j)`.
- Note: current pairwise analysis already overlaps this family; we will additionally export exact `N^2` Remote-Clique values for direct comparability.

2. **Chamfer Distance** (`implemented`)
- Definition (match screenshot): `CD = (1 / N) * sum_{i=1..N} min_{j != i} d(x_i, x_j)`.
- This is the group mean of nearest-neighbor distances (k=1), already used in Analysis 1.3.

3. **MST Dispersion** (`to add`)
- Definition (match screenshot): build the minimum spanning tree (MST) on the complete weighted graph of group embeddings with edge weights `d(x_i, x_j)`.
- Metric: `MST_dispersion = (1 / |E_MST|) * sum_{(i,j) in E_MST} d(x_i, x_j)`, where `|E_MST| = N-1`.

4. **Span** (`partial -> to add full`)
- Screenshot definition is percentile-to-centroid radius.
- Centroid: `c = (1 / N) * sum_i x_i`.
- Metric to add: `Span_p = percentile_p( { d(x_i, c) } )`.
- Primary reported value: **Span_90** (p=90), matching the screenshot's robustness choice.
- Current centroid-dispersion analysis uses **mean** distance to centroid; keep it and add Span_90 as the Table-3 aligned metric.

5. **Sparseness** (`to add`)
- Medoid definition: `m = argmin_{x_j} sum_{i=1..N} d(x_i, x_j)`.
- Metric (match screenshot intent): `Sparseness = (1 / N) * sum_{i=1..N} d(x_i, m)`.

6. **Entropy (grid-based embedding occupancy)** (`to add`)
- Follow screenshot approach on a 2D projection:
- Project points to 2D embedding space, partition into a `5 x 5` grid, and compute bin frequencies `f_b = n_b / N`.
- Metric: Shannon-Wiener entropy `H = - sum_b f_b * log(f_b)` over non-zero bins.
- Report normalized entropy `H / log(B_nonzero)` as a secondary scale-free version.
- Important: this is **embedding-space occupancy entropy**, distinct from the existing **topic entropy** analysis.

#### Rollout for new conditions (`how_to_think`, `persona`)

- Compute all six metrics above for both **ideas** and **full proposals** in each condition.
- Compare each new condition vs `baseline(minimal)-rephrased`, then Human vs each condition.
- Preserve current significance pipeline (MW + permutation + effect size + correction), and add robust CI summaries for newly added metrics.

### 2) Novelty against literature (Part 2-II)

Analyses completed:
- Raw novelty: mean distance to literature 10-NN.
- Local-density normalized novelty (`z` and ratio).
- Raw novelty inferential tests.
- Literature-space projections (descriptive).
- Recomputed literature-space outliers using mean-10NN (aligned to novelty definition).
- Projection reliability diagnostics.
- JSON export + flag sanity check.

Key findings:
- Raw novelty means: Human `0.1303`; All AI `0.0999`; Claude `0.0898`; Gemini `0.1000`; GPT-5.2 `0.1098`.
- Raw novelty tests vs Human:
- All AI MW `p=0.0356` but Holm `p=0.1069`.
- Claude MW `p=0.0049`, Holm `p=0.0197`, `δ=-0.4858`.
- Gemini MW `p=0.0650`, Holm `p=0.1300`.
- GPT-5.2 MW `p=0.6604`.
- After local-density normalization (z-scores), AI-vs-Human differences were not significant (All AI MW `p=0.9138`, `δ=0.0158`; all model contrasts non-significant after Holm).
- Literature-space outliers (mean-10NN top 10%): Human `26.1%` vs All AI `5.8%`; Fisher tests were suggestive but Holm-adjusted p-values were above `0.05` (All AI Holm `p=0.0562`).
- Projection reliability: trustworthiness high for t-SNE/UMAP, but outlier overlap between high-D and 2D was poor in seed sweeps (Jaccard `0.0`), so 2D outliers should not be treated as ground truth.
- Sanity check in combined export: `metrics.is_literature_outlier` exactly matched `metrics.is_most_novel_raw` (`10/10` overlap).

Interpretation:
- Novelty conclusions depend on framing. Raw distance suggests Human/Claude separation, but local-density normalization weakens broad Human-vs-AI novelty claims.

### 3) Topic, clustering, and style controls (Part 2-III)

Analyses completed:
- Exploratory topic modeling.
- Topic distribution comparison with permutation + per-topic tests.
- Topic coverage/exclusivity/entropy.
- Cluster segregation (NMI/ARI/between-within ratio permutation tests).
- Style-only baseline classifier.
- Style-controlled sensitivity (embedding residualization).

Key findings:
- Overall soft-topic distribution differed (permutation chi-square `p=0.0001`), with asymmetric topics (Topic_2 Human-up, Topic_3 AI-up after FDR).
- Coverage parity: Human `3/3`, AI `3/3`; exclusivity none.
- Entropy difference: Human `H=0.5470` vs AI `H=1.5990` (subsample comparison significant).
- Cluster segregation significant: NMI `0.0887` (`p=0.0026`), ARI `0.1254` (`p=0.0013`), between/within ratio `1.2406` (`p=0.0022`).
- Style-only classifier was above chance but moderate (AUROC `0.684 ± 0.102`, permutation `p=0.0230`).
- After style adjustment, centroid differences remained robust (AI coefficient `-0.174962`, permutation `p=0.0002`), but style-adjusted NN differences became non-significant (All AI vs Human MW `p=0.1582`, permutation `p=0.2716`).

Interpretation:
- Human/AI semantic separation is present, but some local isolation/outlier conclusions are sensitive to stylistic covariates.

### 4) NCEMS-criteria review analyses (Part IV)

Analyses completed:
- Review-similarity proxy analysis.
- Proposal-quality comparisons by criterion and overall.
- Evaluator strictness/self-preference analyses.
- Bias-control rerun with self-evaluations removed.

Criteria evaluated:
- `Relevance_to_Emergent_Phenomena`
- `Novelty_and_Significance`
- `Rigor_of_Approach`
- `Scope_and_Timeline`
- `Synthesis_Focus`
- `Data_Identification`
- `Open_Science_Commitment`

Key findings:
- Raw evaluator pool overall means: Human-all `3.5855`, Claude `4.0087`, Gemini `3.8319`, GPT-5.2 `4.3174`.
- Significant overall contrasts vs Human-all: Claude (`q=5.25e-04`), Gemini (`q=0.0187`), GPT-5.2 (`q=1.31e-07`).
- Evaluator effects were strong (Kruskal-Wallis `p=5.20e-22`) with model-dependent self-preference direction.
- After removing self-evaluations:
- Human-all vs Claude remained significant (`q=2.25e-04`).
- Human-all vs Gemini became non-significant (`q=0.6816`).
- Human-all vs GPT-5.2 remained strongly significant (`q=1.70e-08`).

Interpretation:
- NCEMS-quality conclusions are substantial but partially sensitive to evaluator composition and self-preference structure.

### 5) Novelty-framework review analyses

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

### 6) Metric-score relationship and outlier validation (Part V)

Analyses completed:
- Proposal-level data integration (`92 x 52`).
- Spearman metric-score correlation analysis.
- Outlier score-comparison tests.
- Added Human-Y2 metric-score analysis block in:
  - `notebooks/templates/rephrased/metric_score_relationship.ipynb`

#### 2026-05-26 update: Human-Y2 metric-score relationship expansion

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
