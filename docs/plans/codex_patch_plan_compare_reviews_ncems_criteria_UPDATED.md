# Codex Patch Plan for `compare_reviews_ncems_criteria.ipynb` (Updated to Current `analysis_plan.md`)

This patch plan is revised to match the current state where **Human Y2 reviews are now available** and should be treated as first-class inputs, not a late extension.

Core structural requirements:
- Load **Human Y1 and Human Y2** reviews together at the same stage (where human reviews are loaded).
- Keep one shared matched/embedding pipeline for both cohorts.
- Place all review-text analyses under R1, before R2.
- Split R1 into two explicit sub-questions:
  - **R1-Q1: Can humans create more diverse reviews than AI?** (all diversity metrics)
  - **R1-Q2: How similar are AI reviews to human reviews?** (all similarity metrics + inter-rater reliability metrics)
- Keep R2 focused on proposal-quality score comparisons.

---

## 0. Patch goals

Codex should revise `compare_reviews_ncems_criteria.ipynb` so that it:

1. Keeps existing data-prep and quality-comparison logic where possible, but updates structure so Y2 is not handled as a late add-on.
2. Loads Human Y1 and Human Y2 reviews together in the human-review loading stage.
3. Adds/organizes one unified R1 block before R2:
   - `# R1: How does the diversity of human reviews compare to those by AI?`
4. Splits R1 into two sub-questions and moves analyses accordingly:
   - diversity metrics under R1-Q1
   - similarity metrics and inter-rater reliability metrics under R1-Q2
5. Uses proposal-conditioned diversity metrics aligned to the proposal notebook family.
6. Stays computationally efficient (no giant global review-by-review matrix).

---

## 1. Alignment to current notebook and `analysis_plan.md`

### 1.1 Loading structure must be cohort-complete up front

The notebook structure should treat review loading as:
- `## 3` AI reviews
- `## 4` Human reviews (**Y1 + Y2 together**)
- `## 5` proposal matching/mapping
- `## 6` matched review sets + embeddings (single source of truth)

Y2 should not first appear only in late sections.

### 1.2 R1/R2 boundary

- All review diversity, review similarity, and review reliability analyses belong in R1.
- `# R2: How are AI proposals' quality compare to humans (evaluated by AI)` should begin only after R1 completes.

### 1.3 Inferential philosophy

For proposal-matched comparisons in R1:
- Primary: paired Wilcoxon.
- Secondary sensitivity: Mann-Whitney + Cliff's delta.
- Multiple-testing correction: BH-FDR or Holm (consistent per table).

---

## 2. High-level design

Primary R1-Q1 question:

> For the same proposal, are Human reviews more semantically diverse than AI reviews?

Primary R1-Q2 question:

> For the same proposal/cohort, how similar are AI reviews to human reviews, and how reliable are Human and AI numeric scoring patterns?

Analysis unit:
- `proposal_key x cohort x source_family`

`source_family`:
- `human`
- `ai_all`
- `claude`
- `gemini`
- `gpt`

This avoids confounding proposal content with reviewer variation.

---

## 3. Required structure in `analysis_plan.md`

Under `## Compare_reviews_ncems_criteria.ipynb`, reflect this structure:

```markdown
# R1: How does the diversity of human reviews compare to those by AI?
## 8c) Build matched review sets for Y1 and Y2 (single source of truth)

## R1-Q1) Can humans create more diverse reviews than AI?
### 8d) Review diversity metrics (proposal-conditioned; Y1 and Y2)
#### 8d.1) Proposal-level paired tests for review diversity
#### 8d.2) Review diversity visualizations

## R1-Q2) How similar are AI reviews to human reviews?
### 8e) Rephrased review similarity analyses (Y1, Y2, combined)
#### 8e.1) Within-proposal Human-Human vs AI-AI pairwise similarity
#### 8e.2) Combined Y1/Y2 four-group similarity comparison (human-y1, ai-y1, human-y2, ai-y2)
#### 8e.3) Significance tests for four-group and paired within-cohort contrasts
### 8f) Inter-rater reliability (scores) for Y2 and Human-vs-AI agreement

## 8g) R1 exports (diversity + similarity + reliability)

# R2: How are AI proposals' quality compare to humans (evaluated by AI)
```

Any previous late Y2 similarity/diversity/reliability sections (e.g., old `21-23` flow) should be retired or folded into the R1 structure above.

---

## 4. Helper functions to maintain/add in `## 2) Utility functions`

### 4.1 Review-set helpers
- `build_review_set_df(aligned_human_df, aligned_ai_df, cohort_tag)`
- `collect_review_embeddings_by_proposal(review_set_df, proposal_key_col='proposal_key')`

### 4.2 Distance helpers
- `cosine_distance_matrix(X)`
- `safe_upper_triangle(D)`
- `safe_percentile(arr, q)`

### 4.3 Proposal-conditioned diversity helpers
- `proposal_mean_pairwise_from_submatrix(Dg)`
- `proposal_min_pairwise_from_submatrix(Dg)`
- `proposal_centroid_distances(Xg, leave_one_out=True)`
- `proposal_medoid_distances(Dg)`

### 4.4 Exact collective metrics
- `group_remote_clique(Dg)`
- `group_chamfer(Dg)`
- `group_mst_dispersion(Dg)`
- `group_span_percentile(Xg, q=90)`
- `group_medoid_index(Dg)`
- `group_sparseness(Dg)`

### 4.5 Between-group centroid metric
- `proposal_global_centroid_distances_two_sets(X_a, X_b)`

### 4.6 Statistical helpers
- `paired_wilcoxon_safe(x, y)`
- `mw_cliffs_summary(x, y)`
- `add_bh_or_holm(df, p_col, method='fdr_bh')`

---

## 5. R1 data build (replace late-extension pattern)

Immediately after current similarity-prep flow (and before R2), create:

`## 8c) Build matched review sets for Y1 and Y2 (single source of truth)`

### Inputs
- Rephrased Human reviews: Y1 and Y2 loaded together.
- Rephrased AI NCEMS reviews (condition-aware glob).
- Proposal mapping table for matched Human/AI proposal keys.

### Objects to build
- `review_set_df_y1`
- `review_set_df_y2`
- optional combined `review_set_df_all` for shared plotting/tests

Required columns:
- `proposal_key`, `proposal_uid`, `proposal_title`, `cohort`, `source_family`, `review_uid`, `reviewer_or_evaluator`, `embedding`

---

## 6. R1-Q1 diversity analyses (Y1 + Y2)

Create:

`## R1-Q1) Can humans create more diverse reviews than AI?`

`### 8d) Review diversity metrics (proposal-conditioned; Y1 and Y2)`

For each proposal and source-family block with `n >= 2`, compute:
- mean pairwise distance
- nearest-neighbor / Chamfer
- centroid dispersion (LOO form)
- between-group global-centroid dispersion (Human vs AI block)
- medoid distance / Sparseness
- exact Remote-Clique
- exact Span-90
- exact MST Dispersion

And include:
- cohort-parallel human-vs-AI paired diversity tests
- model-aware diversity comparisons (Human vs Claude/Gemini/GPT)
- diversity-focused visualizations

---

## 7. R1-Q2 similarity + reliability analyses (Y1 + Y2)

Create:

`## R1-Q2) How similar are AI reviews to human reviews?`

`### 8e) Rephrased review similarity analyses (Y1, Y2, combined)`

Include:
- within-proposal Human-Human vs AI-AI similarity for Y1
- same for Y2
- one combined four-group similarity visualization (`human-y1`, `ai-y1`, `human-y2`, `ai-y2`)
- four-group and within-cohort significance testing

Then add:

`### 8f) Inter-rater reliability (scores) for Y2 and Human-vs-AI agreement`

Include:
- Human-human quantitative score reliability
- AI-AI quantitative score reliability
- Human-vs-AI reliability/agreement at proposal-level means
- ICC summaries and rank-correlation summaries with visualizations

---

## 8. R1 tests and visualizations

### 8.1 Tests
R1-Q1 (diversity):
- For each cohort and diversity metric: Human vs AI-all (primary paired Wilcoxon)
- Human vs Claude/Gemini/GPT (paired when valid)
- sensitivity: MW + Cliff's delta

R1-Q2 (similarity + reliability):
- four-group similarity differences (global + pairwise corrected tests)
- within-cohort paired Human-vs-AI similarity tests
- reliability significance/uncertainty summaries where applicable

### 8.2 Visualizations
- Diversity: paired slopes, by-model box/strip, effect dotplot
- Similarity: combined four-group distribution plot
- Reliability: heatmap and human-vs-AI agreement scatter(s)

---

## 9. R1 export block

Create one consolidated R1 export section:

`## 8g) R1 exports (diversity + similarity + reliability)`

Tables:
- `quality_review_similarity_y1_pairwise.csv`
- `quality_review_similarity_y2_pairwise.csv`
- `quality_review_similarity_y1y2_four_group_tests.csv`
- `quality_review_similarity_within_cohort_paired_tests.csv`
- `quality_review_diversity_y1_proposal_level.csv`
- `quality_review_diversity_y2_proposal_level.csv`
- `quality_review_diversity_y1_long.csv`
- `quality_review_diversity_y2_long.csv`
- `quality_review_diversity_within_cohort_human_vs_ai_tests.csv`
- `quality_review_diversity_human_vs_ai_by_model.csv`
- `quality_review_reliability_y2_human.csv`
- `quality_review_reliability_y2_ai.csv`
- `quality_review_reliability_y2_human_vs_ai.csv`

Figures:
- `quality_review_similarity_y1y2_four_groups.png`
- `quality_review_diversity_y1_paired_slopes.png`
- `quality_review_diversity_y2_paired_slopes.png`
- `quality_review_diversity_by_model.png`
- `quality_review_diversity_effects_dotplot.png`
- `quality_review_reliability_y2_heatmap.png`
- `quality_review_reliability_y2_human_vs_ai_scatter.png`

---

## 10. Computational-efficiency rules

1. Do not build one giant review x review matrix across all proposals.
2. Compute distance matrices only within proposal-conditioned sets.
3. Reuse aligned embedded review rows from the shared build stage (Y1 and Y2 together).
4. Store embeddings once (`review_uid -> embedding`) and avoid repeated copies.
5. Do not add unstable micro-sample metrics as core outputs.

---

## 11. Minimal pseudocode

```python
# 1) Load AI reviews + Human Y1/Y2 reviews together
# 2) Build matched/proposal-aligned review rows once for Y1 and Y2
# 3) Embed (or load cached embeddings) once; attach by review_uid
# 4) Enter R1 before R2
# 5) R1-Q1: build diversity metrics for Y1 and Y2 + paired/model-aware tests
# 6) R1-Q2: run similarity analyses (Y1, Y2, combined) + significance tests
# 7) R1-Q2: run inter-rater reliability analyses (Y2 scores, human/AI/human-vs-AI)
# 8) Export all R1 diversity/similarity/reliability tables and figures
# 9) Continue to R2 quality-score analyses
```

---

## 12. Final instruction block to paste into Codex

```text
Patch compare_reviews_ncems_criteria.ipynb in place using this updated plan.

Requirements:
- Treat Y2 as first-class input: load Human Y1 and Human Y2 reviews together in the human-review loading stage.
- Keep one shared matched/embedding pipeline for both cohorts.
- Put all review analyses under R1 before R2.
- Split R1 into two sub-questions:
  - R1-Q1: Can humans create more diverse reviews than AI? (all diversity metrics)
  - R1-Q2: How similar are AI reviews to human reviews? (all similarity + inter-rater reliability metrics)
- Use heading:
  # R1: How does the diversity of human reviews compare to those by AI?
- Keep R2 focused on proposal-quality score comparisons.
- Reuse aligned embedded review rows; do not build one giant global review-by-review matrix.
- Compute proposal-conditioned diversity metrics aligned to proposal notebook families.
- Provide one combined four-group similarity graph:
  human-y1, ai-y1, human-y2, ai-y2
- Run significance tests for group differences and within-cohort paired Human-vs-AI comparisons.
- Export all R1 diversity/similarity/reliability outputs listed in this plan.
- Keep `analysis_plan.md` consistent with this structure.
```
