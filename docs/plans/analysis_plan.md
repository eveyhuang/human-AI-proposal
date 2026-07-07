## Overview

This document is an **execution-status analysis plan** based on the completed notebooks in:

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
| `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl` | Prepared full-proposal embeddings (AI/Human) + metadata. Use for proposal-vs-proposal analyses only: proposal clustering, proposal-space UMAPs, diversity, centroid, NN, medoid, and sparseness metrics | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/rephrased/minimal/proposal_embeddings_rephrased_abstract.pkl` | Prepared Section-1 / abstract-only proposal embeddings. This is the required proposal representation for all proposal-to-literature comparisons, including novelty distances, literature-space UMAP projection, BERTopic-region coverage, MeSH-neighbor coverage, and literature-neighbor recency | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/literature/relevant_literature_embeddings.pkl`                | Prepared literature abstract embeddings used for proposal-to-literature distance calculations. Compare only against Section-1 / abstract-only proposal embeddings, not full-proposal embeddings | `compare_proposals_rephrased.ipynb`                                                         |
| `data/embeddings/reviews/minimal/ncems_criteria/review_embeddings_minimal.pkl` | Prepared NCEMS review embeddings with metadata + `review_uid` alignment                                                               | `compare_reviews_ncems_criteria.ipynb`                                                      |
| `data/embeddings/reviews/minimal/novelty/review_embeddings_minimal.pkl`        | Prepared novelty review embeddings with metadata + `review_uid` alignment                                                             | `compare_reviews_novelty.ipynb` (future-ready; current core analysis is score-table based)  |
|   `data/embeddings/literature/lit_lda_model.pkl`                         |     Supplementary lexical LDA model (K topics) fitted on literature abstracts; used as a lexical robustness/comparison layer, not as the primary UMAP region definition      | `compare_proposals_rephrased.ipynb` (supplementary lexical analyses; Analyses 3.6b, 3.8 sensitivity)                                     |
|   `data/prepared/rephrased/minimal/lit_topic_assignments.csv`             |     Per-article supplementary LDA dominant topic index + soft topic probabilities for all 39538 literature articles                               | `compare_proposals_rephrased.ipynb` (supplementary lexical analyses; Analyses 3.6b, 3.8 sensitivity)                                     |
|   `data/embeddings/literature/lit_bertopic_model.pkl`              |   BERTopic model fitted on existing BioLinkBERT-large literature embeddings; defines embedding-native literature topic/region labels via UMAP + clustering + c-TF-IDF topic representations | `prepare_data_for_analysis.ipynb` (new Section 12), `compare_proposals_rephrased.ipynb` (Analyses 3.5, 3.6, 3.8) |
|   `data/prepared/rephrased/minimal/lit_bertopic_assignments.csv`   |   Per-literature-article embedding-native region label (`bertopic_topic`), optional probability/confidence, outlier flag, and human-readable c-TF-IDF label/top terms | `compare_proposals_rephrased.ipynb` (Analyses 3.5, 3.6, 3.8) |
|   `data/prepared/rephrased/minimal/lit_bertopic_topic_info.csv`    |   Per-BERTopic-region metadata: topic id, article count, top c-TF-IDF words, representative documents/titles, and display label for UMAP annotation | `compare_proposals_rephrased.ipynb` (Analysis 3.5) |
|   `data/embeddings/literature/lit_umap_reducer.pkl`                       |   UMAP reducer fitted on all 39538 literature embeddings (1024d); used to project Section-1 / abstract-only proposal embeddings into the literature landscape via `transform()`, not refit | `compare_proposals_rephrased.ipynb` (Step 7, Analysis 3.5)                                          |
|   `data/embeddings/literature/lit_umap2d.npy`                             |   2D UMAP coordinates for all 39538 literature articles (shape 39538×2)                                                          | `compare_proposals_rephrased.ipynb` (Analysis 3.5)                                          |
|   `results/figures/rephrased/minimal/literature_umap_bertopic_regions_prepare.png` |   Literature-only diagnostic UMAP: all literature articles colored by embedding-native BERTopic region with region labels annotated; no proposal overlay | `prepare_data_for_analysis.ipynb` (Section 13 diagnostic visualization) |


###   New `prepare_data_for_analysis.ipynb` Sections

  The following three sections must be added to `prepare_data_for_analysis.ipynb` after the existing `## 9. Review Embeddings` section and before `## 10. Artifact Summary`. All outputs are cached (skip-if-exists logic) and are loaded by `compare_proposals_rephrased.ipynb` without re-fitting.

####   `## 11. Literature Topic Modeling (LDA)` [UPDATE: supplementary lexical topic model]

  **Role in the analysis**: LDA is retained as a supplementary lexical topic model because it captures word co-occurrence themes, not necessarily the semantic neighborhoods visible in the BioLinkBERT/UMAP geometry. LDA topic labels should not be used as the primary coloring or region definition for the literature UMAP. They are used for lexical robustness checks, LDA-vs-embedding-topic agreement diagnostics, and optional supplementary tables.

Step-by-step:

1.   Load literature abstracts from `lit_payload['texts']` (already in memory after Section 8). Filter to articles with non-empty abstracts (`has_abstract = abstract.strip() != ''`; approximately 39172/39538 articles).
2.   Fit `CountVectorizer(max_features=3000, min_df=3, max_df=0.7, stop_words='english', ngram_range=(1,2))` on the non-empty abstract texts. Use the same domain stopword strategy as Analysis 1.1 in the proposal notebook.
3.   Fit LDA with `n_topics=K` (start with K=10; run sensitivity for K=8,12,15 and select by perplexity on a held-out 10% split). Use `doc_topic_prior=0.1, topic_word_prior=0.1, max_iter=50, batch_size=128, random_state=42`. Print top-15 words per topic for human interpretability check.
4.   Assign each article its dominant topic (`argmax` of document-topic distribution) and save full soft probabilities. For the ~366 articles with empty abstracts, assign topic label `−1` (no topic).
5.   Save `lit_lda_model.pkl` to `data/embeddings/literature/` (for potential `transform()` on new documents) and `lit_topic_assignments.csv` to `data/prepared/rephrased/minimal/` with columns: `pmid`, `dominant_topic`, `topic_prob_0..K-1`.

Saved artifacts:

-   `data/embeddings/literature/lit_lda_model.pkl`
-   `data/prepared/rephrased/minimal/lit_topic_assignments.csv`

####   `## 12. Literature Embedding Topic Regions (BERTopic)`

  **Motivation**: The literature UMAP is built from BioLinkBERT-large embeddings, while LDA topics are built from bag-of-words count features. If LDA labels do not align with visible UMAP islands, the plot becomes hard to interpret and can mislead readers about which "topic regions" proposals occupy. This section therefore defines literature regions using an embedding-native topic model: BERTopic fitted on the existing BioLinkBERT-large literature embeddings. Text is used afterward only to generate human-readable c-TF-IDF labels for each embedding cluster.

  **Dependency note**: Add `bertopic` and `umap-learn` to the project environment. Use the already-computed literature embeddings; do not let BERTopic recompute default sentence-transformer embeddings.

  Step-by-step:

1.   Load literature titles + abstracts from `lit_payload['texts']` / `articles` and existing BioLinkBERT-large literature embeddings from `data/embeddings/literature/relevant_literature_embeddings.pkl`. L2-normalize embeddings exactly as in the literature-distance pipeline.
2.   Fit BERTopic on the literature corpus only: `topics, probs = topic_model.fit_transform(lit_texts, X_lit)`. The documents are titles + abstracts; embeddings are the precomputed BioLinkBERT-large vectors. Proposals are not included in the BERTopic fit, so they cannot reshape the reference field map.
3.   Configure BERTopic to use an embedding-space clustering pipeline appropriate for ~39k biomedical abstracts. Starting configuration:
   - `UMAP(n_neighbors=30, n_components=5, min_dist=0.0, metric='cosine', random_state=42, low_memory=True)` for BERTopic's internal dimensionality reduction.
   -   `MiniBatchKMeans(n_clusters=12, random_state=42, batch_size=2048, n_init=20)` as BERTopic's clustering model. HDBSCAN produced only two broad density masses in the 39k-article BioLinkBERT space; a fixed-granularity clusterer is better for the intended 10-15 interpretable literature-map regions.
   -   `CountVectorizer(stop_words='english', ngram_range=(1,2), min_df=1, max_df=1.0, max_features=10000)` for c-TF-IDF topic labels; use permissive df thresholds because BERTopic applies this vectorizer to topic-level aggregate documents after clustering, where strict `min_df`/`max_df` settings can fail if the number of discovered topics is small. Use the same domain stopword strategy developed for proposal LDA where helpful.
4.   Generate human-readable topic/region labels from BERTopic topic representations, but do **not** use the raw top 4 c-TF-IDF terms directly when they overlap heavily across regions. Build display labels with `contrastive_phrase_v4`: vectorize literature titles + abstracts with unigrams, bigrams, and trigrams; score candidate phrases by region-vs-rest enrichment; prefer multi-word phrases; penalize terms that appear across many regions rather than banning them outright; avoid generic singleton biomedical terms such as `cell`, `cells`, `cancer`, `emerging`, `study`, `review`, and `potential`; and use MMR-style token-overlap penalties so each label is not internally redundant. Multi-word phrases containing a generic word can still be used when the full phrase is region-specific, e.g. `therapeutic potential`. Save both the raw c-TF-IDF label (`display_label_raw_ctfidf`) and the contrastive phrase label (`display_label`) so the visualization emphasizes differences between nearby regions while preserving the original topic representation for auditability. Treat BERTopic topic `-1` as "embedding outlier / unassigned region".
5.   Save a per-article assignment table aligned to the literature embedding order with columns: `article_idx`, `pmid`, `bertopic_topic`, `bertopic_is_outlier`, `bertopic_prob` when available, `bertopic_label`, `bertopic_top_terms`, `bertopic_contrastive_terms`, and `bertopic_label_strategy`.
6.   Save the fitted BERTopic model and topic-info table for reuse. Do not recompute if all three output artifacts already exist.
7.   Run sensitivity diagnostics before using labels in the paper: vary `n_clusters` (e.g., 10, 12, 15) and report region sizes, c-TF-IDF label interpretability, and qualitative stability of proposal-region assignments. The primary setting is `n_clusters=12`, but the final interpretation should not depend on one fragile granularity setting.
8.   Compare BERTopic embedding-region labels against LDA labels using ARI/NMI and a contingency heatmap. Low agreement is not a failure; it supports reporting LDA as lexical structure and BERTopic as embedding-region structure.

  Saved artifacts:

-   `data/embeddings/literature/lit_bertopic_model.pkl`
-   `data/prepared/rephrased/minimal/lit_bertopic_assignments.csv`
-   `data/prepared/rephrased/minimal/lit_bertopic_topic_info.csv`
-   `results/tables/rephrased/minimal/lit_lda_bertopic_agreement.csv`
-   `results/figures/rephrased/minimal/lit_lda_bertopic_contingency.png`

####   `## 13. Literature-Space UMAP (Literature Only)`

**Note**: Fitting UMAP on 39538 × 1024d embeddings is the most expensive step in the entire pipeline (~10–30 minutes on CPU). This must be cached with a skip-if-exists check on both output files. Do NOT refit if outputs already exist.

  **Role in the analysis**: This section fits/caches the fixed 2D literature map on literature embeddings only. The UMAP coordinates provide the visual map; BERTopic labels from Section 12 provide the primary region colors/labels on that map. It does **not** load, project, map, or save proposal coordinates. Proposal projection into this saved literature reducer happens only in `compare_proposals_rephrased.ipynb`.

Step-by-step:

1.   Load `X_lit` from `lit_payload['embeddings']` (already in memory from Section 8) and L2-normalize. Do not load proposal embeddings in this prepare-data section.
2.   Check if `data/embeddings/literature/lit_umap_reducer.pkl` and `data/embeddings/literature/lit_umap2d.npy` both exist. If so, load and skip fitting entirely.
3.   If fitting: run `umap.UMAP(n_neighbors=20, min_dist=0.1, n_components=2, metric='cosine', random_state=42, low_memory=True)` on `X_lit`. Use `n_neighbors=20` to match the existing Step 7 UMAP parameters so Step 7 can swap in the cached coordinates without visual discontinuity. Use `low_memory=True` to handle the 39538-sample case.
4.   Save the fitted reducer as `data/embeddings/literature/lit_umap_reducer.pkl` and the 2D literature coordinates as `data/embeddings/literature/lit_umap2d.npy`.
5.   Add a literature-only diagnostic visualization cell: load `lit_umap2d.npy`, `lit_bertopic_assignments.csv`, and `lit_bertopic_topic_info.csv`; color literature articles by `bertopic_topic`; annotate each non-outlier BERTopic region with its c-TF-IDF display label; save the figure to `results/figures/rephrased/minimal/literature_umap_bertopic_regions_prepare.png`. This diagnostic intentionally does **not** overlay proposals.

  Proposal projection boundary:

- **Representation rule**: any comparison against literature embeddings must use Section-1 / abstract-only proposal embeddings from `proposal_embeddings_rephrased_abstract.pkl`. Do not use full-proposal embeddings (`X_prop`) for proposal-to-literature distances, literature-space UMAPs, literature-neighbor tables, MeSH-neighbor coverage, publication-year recency, or BERTopic-region coverage.
- The existing Step 7 novelty visualization in `compare_proposals_rephrased.ipynb` should load `lit_umap_reducer.pkl` and `lit_umap2d.npy`, then project Section-1 / abstract-only proposal embeddings inside the comparison notebook.
- Analysis 3.5 in `compare_proposals_rephrased.ipynb` should load the same literature reducer and project Section-1 / abstract-only proposal embeddings (`proposal_embeddings_rephrased_abstract.pkl`) inside the comparison notebook, so literature-space maps use the same proposal representation as proposal-to-literature novelty distances.
- `prepare_data_for_analysis.ipynb` should not create `proposal_abstract_coords_in_lit_umap.npy` or `proposal_full_coords_in_lit_umap.npy`.

Saved artifacts:

-   `data/embeddings/literature/lit_umap_reducer.pkl`
-   `data/embeddings/literature/lit_umap2d.npy`
-   `results/figures/rephrased/minimal/literature_umap_bertopic_regions_prepare.png`


## Experiment Conditions

This study now has four generation conditions:

1. `baseline(minimal)-rephrased` (**completed**)

- LLMs generate ideas/proposals under the minimal prompt pipeline with rephrasing.
- This condition is the current reference condition and all completed results in this plan come from it.

1. C0: `one_at_a_time` + high temperature (**planned next**)

- LLMs use the same minimal idea/proposal prompt pipeline as the baseline condition, except that it generates one idea at a time from each model instead of all 23 at once.
- use temperature = 0.9 for each model


1. C1:`persona` + high temperature (**planned next**)

- LLMs generate ideas/proposals one at a time, while adopting human-scientist author personas. use temperature = 0.9 for each model
- Inputs include titles/abstracts of recent papers by the target author(s) during idea generation.

### Cross-condition comparison plan

- For both **ideas** and **full proposals**, run the same analysis families already used in baseline:
- Diversity analyses.
- Novelty analyses.
- Score-comparison analyses.
- Primary comparison: each new condition (`high_temperature`, `how_to_think`, `persona`) vs `baseline(minimal)-rephrased`, then Human vs each condition.

## Completed Analyses and Results

> **Update (July 1, 2026):** compact proposal results below have been refreshed from the rendered `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb` outputs; NCEMS rows reflect the executed baseline/minimal review notebook audit.

> **Representation update (July 2, 2026):** proposal-to-literature analyses have been standardized to use Section-1 / abstract-only proposal embeddings. Literature-relative novelty, literature-space outlier, BERTopic-region coverage, MeSH-neighbor, and literature-neighbor recency numbers below reflect the last audited rendered outputs and should be refreshed by rerunning Part III after this code change.


### Compact Results Table

Stars indicate corrected/primary significance for the model-vs-Human contrast: `*** p<.001`, `** p<.01`, `* p<.05`; blank means not significant. Unless noted, `Δ` is AI model minus Human, so negative values mean Human is higher. **[CRITICAL CHANGE] For the matrix-derived diversity rows (2.1, 2.2a–2.2d, 2.3) the stars now reflect the group-level permutation (label-shuffle) test, Holm-corrected across the model contrasts — not Mann–Whitney. See the inference note directly below.**
For the `All AI vs Human` column, pooled values come from the dedicated audited `compare_proposals_all_ai.ipynb` binary notebook; some literature-relative rows therefore use slightly different Human-side summaries than the four-group notebook.

> **[CRITICAL CHANGE] Primary inference for within-group diversity metrics: permutation, not Mann–Whitney.**
>
> Every proposal-level *within-group diversity* metric — mean pairwise distance (2.1), LOO-centroid distance (2.2a), global-centroid distance (2.2b), MST edge weight (2.2c), medoid sparseness (2.2d), and nearest-neighbor / Chamfer distance (2.3) — is a function of a single shared within-group pairwise-distance matrix. The 23 per-proposal values inside a group are therefore **statistically dependent**: each is computed from the same set of proposals and shares terms with the others. Mann–Whitney + Holm assumes independent observations; applied to these coupled quantities it treats correlated numbers as i.i.d. and returns anti-conservative p-values (e.g. `MW p=3.5e-09` in 2.1) that **overstate the evidence**. The effect is real and survives the correct test — this is a *reporting* fix, not a finding that disappears.
>
> The valid inference is the **group-level label-permutation test** (shuffle Human/AI labels, recompute the group statistic, build the null distribution). It is already computed for every diversity metric and permutes at the exchangeable unit — the proposal label — so it is unaffected by the within-matrix dependence.
>
> **Rule — apply in every step below and in every future condition notebook:**
> 1. Report the **permutation p-value (Holm-corrected across the model contrasts) as PRIMARY** for every matrix-derived diversity metric, and set significance stars from it.
> 2. **Drop the Mann–Whitney / Holm p-values** from these metrics, or keep them only in a clearly labelled footnote: *"MW/Holm shown for reference only — not valid inference for a matrix-derived metric."* Never let a MW p-value carry a significance star or headline a diversity result.
> 3. **2.2c (MST) and 2.5 (grid entropy) are already permutation-primary** and are the template for the rest.
> 4. **Exemption — do NOT change Part III/IV.** Literature-relative novelty (ElementNovel, MeanKNN, `novelty_z`), MeSH coverage, literature-neighbor year, and style features measure each proposal against a **fixed external reference** (the 39,538-abstract corpus / a style model), so their per-proposal values **are** independent and Mann–Whitney/Holm stays valid. Literature-space outlier prevalence (Fisher) and review diversity (paired Wilcoxon across independent proposals) are likewise valid and unchanged.
> 5. **How to avoid this going forward:** any statistic that is a function of a shared distance/adjacency matrix among the compared items must be tested by permutation/randomization at the exchangeable unit. Never feed matrix-derived per-item values into a rank-sum test as if they were independent samples.

| Analysis | Human reference | Claude vs Human | Gemini vs Human | GPT-5.2 vs Human | All AI vs Human | Primary test |
| --- | --- | --- | --- | --- | --- | --- |
| **[CRITICAL CHANGE]** Proposal diversity 2.1 pairwise / Remote-Clique family | mean pairwise `0.3411` | `0.1523`; Δ `-0.1895`; perm `q=0.0004` `***`; δ `-0.826` | `0.0978`; Δ `-0.2291`; perm `q=0.0004` `***`; δ `-0.913` | `0.1997`; Δ `-0.1535`; perm `q=0.0018` `**`; δ `-0.739` | AI boot `0.1524` vs Human `0.3411`; δ `-0.826`; perm `p=0.0001` `***` | Permutation (label-shuffle) Holm |
| **[CRITICAL CHANGE]** Proposal diversity 2.2a centroid LOO | centroid LOO `0.1953` | `0.0813`; Δ `-0.1149`; perm `q=0.0464` `*`; δ `-0.826` | `0.0515`; Δ `-0.1434`; perm `q=0.0064` `**`; δ `-0.913` | `0.1084`; Δ `-0.0880`; perm `q=0.0945` ns | AI boot `0.0821` vs Human `0.1953`; δ `-0.826`; perm `p=0.0089` `**` | Permutation (label-shuffle) Holm |
| **[CRITICAL CHANGE]** Proposal diversity 2.2b global centroid | global-centroid dist `0.1913` | `0.0784`; H-AI `0.1128`; perm `q=0.3760` ns; δ `0.682` | `0.0542`; H-AI `0.1370`; perm `q=0.0855` ns; δ `0.766` | `0.1031`; H-AI `0.0882`; perm `q=0.9575` ns; δ `0.641` | AI boot `0.0793` vs Human `0.1913`; δ `-0.696`; perm `p=0.0078` `**` | Permutation (label-shuffle) Holm |
| Proposal diversity 2.2c MST dispersion | MST `0.1004` | `0.0623`; Δ `-0.0381` `*` | `0.0584`; Δ `-0.0420` `*` | `0.0667`; Δ `-0.0337` `*` | AI boot `0.0613` vs Human `0.1004`; perm `***` | Permutation Holm |
| **[CRITICAL CHANGE]** Proposal diversity 2.2d sparseness | sparseness `0.2218` | `0.0906`; Δ `-0.1292`; perm `q=0.0486` `*`; δ `-0.693` | `0.0597`; Δ `-0.1621`; perm `q=0.0064` `**`; δ `-0.822` | `0.1194`; Δ `-0.1010`; perm `q=0.0907` ns | AI boot `0.0926` vs Human `0.2218`; δ `-0.699`; perm `p=0.0098` `**` | Permutation (label-shuffle) Holm |
| **[CRITICAL CHANGE]** Proposal diversity 2.3 1-NN / Chamfer | Chamfer `0.0751` | `0.0386`; Δ `-0.0338`; perm `q=0.0186` `*`; δ `-0.826` | `0.0566`; Δ `-0.0358`; perm `q=0.0186` `*`; δ `-0.826` | `0.0409`; Δ `-0.0286`; perm `q=0.0352` `*`; δ `-0.696` | AI boot `0.0432` vs Human `0.0751`; δ `-0.869`; perm `p=0.0002` `***` | Permutation (label-shuffle) Holm |
| Proposal diversity 2.5 grid entropy | normalized entropy `0.3304` | `0.2802`; Δ `-0.0502`; ns | `0.2297`; Δ `-0.1007`; ns | `0.2790`; Δ `-0.0514`; ns | AI boot `0.3640` vs Human `0.3304`; perm `p=0.771` | Permutation Holm |
| Proposal novelty ElementNovel-0 | mean `0.0993` | `0.0871`; Δ `-0.0122`; Holm ns | `0.0923`; Δ `-0.0070`; ns | `0.0818`; Δ `-0.0175`; MW Holm ns; perm trend `q=0.112` | AI `0.0871` vs Human `0.0993`; Holm `q=0.275`; ns | MW Holm |
| Proposal novelty ElementNovel-10 | mean `0.2171` | `0.1965`; Δ `-0.0206`; ns | `0.1985`; Δ `-0.0186`; ns | `0.1839`; Δ `-0.0332`; MW ns; perm trend `q=0.0528` | AI `0.1930` vs Human `0.2171`; Holm `q=0.126`; ns | MW Holm |
| Proposal novelty MeanKNN-10 | mean `0.1151` | `0.1009`; Δ `-0.0143`; ns | `0.1045`; Δ `-0.0107`; ns | `0.0918`; Δ `-0.0233`; MW ns; perm `q=0.0363` | AI `0.0990` vs Human `0.1151`; Holm `q=0.798`; ns | MW Holm |
| Proposal novelty normalized `novelty_z` | mean `0.7323` | `0.5313`; Δ `-0.2011`; ns | `0.6950`; Δ `-0.0374`; ns | `0.4146`; Δ `-0.3178`; MW ns; perm trend `q=0.0969` | AI `0.5469` vs Human `0.7323`; Holm `q=0.798`; ns | MW Holm |
| Proposal literature-space outliers mean-10NN | Human `7/23` (`30.4%`) | `1/23` (`4.3%`), Holm `q=0.094` | `2/23` (`8.7%`), `q=0.135` | `0/23`, `q=0.0275` `*` | Human `7/23` (`30.4%`) vs AI `3/69` (`4.3%`); Holm `q=0.00585`; element0 `q=0.0281`; z ns | Fisher Holm |
| Pairwise-distance bimodality 2.1b | dip `0.1628`; best GMM `k=3` | dip `0.0710`; `p<.001`; best `k=3` | dip `0.0408`; `p=0.0042`; best `k=2` | dip `0.1040`; `p<.001`; best `k=3` | human dip `0.1628`; AI dip `0.0671`; within/between-model dips both `<.001` | Dip test + BIC |
| Topic distribution + Ward/GMM clusters | topics T1/T2 `15/14`; Ward A/B `6/17`; GMM `9/6/8` | topics `14/13`; Ward A/B `2/21`; GMM `3/2/18` | topics `7/20`; Ward A/B `1/22`; GMM `2/1/20` | topics `16/13`; Ward A/B `3/20`; GMM `16/3/4` | topics ns (`p=0.327`); Ward OR `3.706`, `p=0.0665`; GMM ratio `1.062`, `p=0.0305`, NMI `0.577`, ARI `0.326` | Topic 4-group perm `p=0.0250`; Ward Fisher Holm; GMM ARI `p=0.0123`, ratio `p=0.0346` |
| LDA topic vs Ward cluster correspondence | ARI `-0.0050`; NMI `0.0000`; lexical topics and embedding clusters are complementary | not model-specific | not model-specific | not model-specific | inherited cached ARI/NMI; same correspondence result | ARI/NMI descriptive |
| Literature BERTopic region coverage | group entropy `1.2807`; effective regions `3.5991`; dominant frac `0.4804` | entropy `1.0942`; effective `2.9867`; Holm ns | entropy `0.9029`; effective `2.4668`; Holm ns | entropy `0.8833`; effective `2.4189`; Holm ns | group entropy `1.0038`; effective `2.7286`; breadth boot `3.521 [2,4]`; proposal-level raw p≈`0.039`, Holm ns `q=0.193` | MW Holm on proposal-level region entropy / max-region weight |
| Literature MeSH coverage | mean unique MeSH `80.00`; union `825` | mean `90.30`; union `834`; Holm ns | mean `84.26`; union `706`; Holm ns | mean `80.70`; union `623`; Holm ns | mean `85.09` vs Human `80.0`; union boot `750.5 [625,860]`; MW `p=0.825` | MW Holm; no model significant |
| Within-region literature year 3.8 | stratum medians `2021.75` / `2022.00` | no Human contrast significant | no Human contrast significant | no Human contrast significant | strata 0/1 medians ns; Holm `q=0.203` and `q=0.766` | MW Holm |
| Style-only source classifier | AUROC `0.521 ± 0.227`; balanced accuracy `0.531 ± 0.133`; permutation `p=0.4496` | not model-specific; no style-adjusted residualization cells rendered | not model-specific; no style-adjusted residualization cells rendered | not model-specific; no style-adjusted residualization cells rendered | AUROC `0.518 ± 0.229`; perm `p=0.421`; `1/18` style features Holm sig | 5-fold CV + AUROC permutation |
| NCEMS R1 review diversity | Human review diversity > AI-all; Y2 all metrics `***`; Y1 4/9 metrics `*` | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | `—` | Paired Wilcoxon FDR |
| NCEMS R1 Human-AI review similarity, Y1 cosine | Human-Human baseline | Human-AI vs Human-Human δ `-0.042` | Human-AI vs Human-Human δ `0.083` | Human-AI vs Human-Human δ `-0.236` | `—` | MW FDR; all model contrasts ns (`q=0.8852`) |
| NCEMS R1 Y1/Y2 within-cohort review similarity | Human-Y1 `0.9583`; Human-Y2 `0.9524` | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | `—` | AI-all: Y2 Human vs AI `***`; Y1 trend ns |
| NCEMS R1 Y2 score reliability | Human-Human ICC2k overall `0.4949`; Human-vs-AI ICC2k `0.7805` `*` | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | `—` | Spearman/ICC |
| NCEMS quality reviews, raw evaluator pool | Human-all mean `3.5855` | mean `4.0087`; H-AI Δ `-0.4232` `***` | mean `3.8319`; H-AI Δ `-0.2464` `*` | mean `4.3174`; H-AI Δ `-0.7319` `***` | `—` | Robust permutation q |
| NCEMS quality reviews, cross-eval only | Human-all mean `3.5855` | mean `4.0739`; δ `-0.652` `***` | mean `3.6761`; δ `0.070` | mean `4.4739`; δ `-0.992` `***` | `—` | MW FDR |
| NCEMS R3 self-preference | compares each evaluator's self vs other AI proposals | self `3.8783`, other `3.8870`; δ `-0.053` | self `4.1435`, other `4.5304`; δ `-0.732` `***` | self `4.0043`, other `3.8065`; δ `0.933` `***` | `—` | MW FDR |
| Novelty-framework reviews, cross-eval rerun | Human reference from novelty-review notebook | Claude ~ Human; `q=0.8428` | Human > Gemini; δ `0.7788` `***` | GPT > Human; δ `-0.4631` `*` | `—` | MW FDR |
| Metric-score relationship (executed baseline-minimal outputs) | semantic-distance/group-dispersion metrics are strongly negative with NCEMS relevance (`r=-0.722`) and overall NCEMS score for `chamfer_group` (`r=-0.546`), but moderately positive with selected novelty-framework criteria (`r~0.33-0.38`) | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | Human-Y2 metric-score block now shows only trend-level correlations (`p>=0.0526`) | Spearman / MW outlier tests |


## Data Visualization Guide

This guide summarizes the visual conventions used in the audited `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb` notebook and should be treated as the default style for future condition notebooks unless an analysis requires a specific exception.

### Color Scheme and Metadata Encoding

- Use the shared group palette consistently: Human `#DC143C`, Claude `#4A90E2`, Gemini `#7B68EE`, GPT-5.2 `#3CB371`.
- Use `#808080` only as a fallback for unknown groups. Combined All-AI views use Claude blue `#4A90E2` for stronger contrast from the Human red palette.
- Proposal-level Human funding status should be encoded as an outline/ring rather than a second red fill: funded Human proposals use a magenta ring `#FF00FF` around the base Human-colored point. Nonfunded or unknown-funding Human proposals keep the ordinary Human point fill with no funding ring.
- Top-ranked proposals should be marked with a black outline/ring, using `is_top5_ranked` when available. This applies to both boxplot jitter points and UMAP/scatter proposal markers. If a point is both funded Human and top-ranked, show both encodings as nested rings, with the funded magenta ring inside the top-ranked black ring.
- When deriving `is_top5_ranked` from review ranks, select the five smallest rows with `nsmallest(5)` or an equivalent stable top-k operation rather than filtering on `rank <= 5`; averaged tie ranks can skip values and otherwise yield fewer than five highlighted proposals.
- In pooled All-AI analyses, `ranking_AI_reviews_global` is global only within the pooled AI proposal set (`1-69`) and is `NA` for Human proposals. Human top-ranked markers should come from the Human ranking field used by the rephrased notebook, not from a mixed Human+AI rank.
- Outlier overlays should use outline rings rather than replacing the base point color. Proposal-space or within-cluster outliers use magenta outlines; literature-space comparison overlays may use an additional cyan outline when two outlier definitions are shown together.
- Literature-background points in literature-space UMAPs should remain small and semi-transparent so proposal markers and BERTopic region labels remain visually dominant.
- Whenever used, legends should explicitly explain black top-ranked outlines, magenta funded-Human rings, outlier rings, and any literature-region colors that are needed to interpret the panel.

### Standard Boxplot Grammar

Use the standardized boxplot helper pattern for all group-comparison distributions.

- Box: standard median line, IQR box, whiskers, and outlier points. Fill each box with the group color at 70% opacity and use black outlines/median lines.
- Jittered scatter: overlay individual observations with random horizontal jitter of approximately `±0.15` units, point size around `20`, and 50% opacity. Use the same group color for the point fill. When proposal metadata are available, add a magenta ring for funded Human proposals and a black ring for top-ranked proposals.
- Mean + 95% CI: plot the bootstrapped mean as a filled diamond marker of roughly `50` points, with vertical error bars for the 95% bootstrap confidence interval. Draw this above jitter points.
- Proposal-level panels should preserve `proposal_uid` or equivalent metadata columns through reshaping/melting so funding and top-rank encodings survive into the plotting layer.
- Non-proposal observations, such as pairwise distances or CV folds, should still use the standardized box/point/mean-CI grammar but should not force proposal-level funding or ranking metadata onto datapoints that do not represent a single proposal.
- Grouped metric panels, such as novelty metrics across multiple `k` values, should use dodged standardized boxplots with a group legend and the same metadata legend when proposal-level rows are available.

### Violin, Ridge, and Histogram Views

- Violin plots should be used sparingly as descriptive distribution-shape diagnostics, not as the primary group-comparison figure when inferential interpretation is expected. For proposal metric comparisons, prefer the standardized boxplot grammar above.
- If a violin plot is used, it should follow the same group palette, show median/quartile or mean annotations clearly, and avoid duplicating an adjacent standardized boxplot unless the shape view adds information.
- Ridge plots are appropriate for dense pairwise-distance distributions where the full shape and skew are important. Use group-colored density fills, with solid median and dashed mean lines in the same group color.
- Histograms should use consistent binning across groups, transparent fills, and log-scale counts when long tails obscure most of the distribution. They should be labeled as descriptive full-range views.

### UMAP and Embedding-Space Projections

- Reuse cached UMAP coordinates whenever available. Proposal-space UMAPs should load `results/tables/rephrased/minimal/cached/proposal_umap2d.npy`; literature-space UMAPs should use the fixed literature reducer and coordinates from `data/embeddings/literature/lit_umap_reducer.pkl` and `data/embeddings/literature/lit_umap2d.npy`.
- Literature-space UMAPs and BERTopic-region overlays must project Section-1 / abstract-only proposal embeddings, not full-proposal embeddings. This keeps proposal markers comparable to the literature abstract embeddings and to the proposal-to-literature novelty metrics.
- Do not refit UMAP inside a visualization cell if a cache exists. If recomputation is unavoidable, use the documented parameters and save the cache for downstream panels.
- Axis labels should identify the coordinate system: `UMAP-1` / `UMAP-2` for proposal-space maps, and `Literature UMAP Dim 1` / `Literature UMAP Dim 2` for literature-anchored maps.
- Proposal markers should follow the metadata encoding above: AI groups use the group palette; Human uses the Human palette color; funded Human proposals add a magenta ring; top-ranked proposals from both Human and AI have black outlines.
- Per-cluster UMAP zooms should retain the same marker semantics and use panel titles with cluster names, total `n`, and compact discriminative topic labels when available.
- Literature-region UMAPs should color the fixed literature background by BERTopic embedding-region labels, not LDA lexical topics. LDA-colored maps are supplementary diagnostics only.
- UMAP legends should explicitly explain black top-ranked outlines, magenta funded-Human rings, outlier rings, and any literature-region colors that are needed to interpret the panel.

### Effect-Size and Significance Panels

- Pair distribution panels with statistical comparisons should be paired with an effect-size panel when space allows.
- Cliff's delta panels should use a vertical zero reference line, horizontal CIs, and group-colored markers for the model-vs-Human contrast.
- Label effect-size axes with the direction of the comparison, e.g. `Cliff's δ (bootstrap 95% CI)` or `AI − Human`. If positive/negative direction changes by metric, state that in the axis label or caption.
- Significance stars should reflect corrected p-values where correction is part of the analysis. Use the compact table convention: `*** p<.001`, `** p<.01`, `* p<.05`.

### Labels, Legends, and Export Standards

- Titles should name the analysis object and, when useful, include a second line describing key encodings such as `diamond/error bar = mean bootstrap 95% CI`.
- Axis labels should use metric units or definitions rather than variable names. Examples: `Pairwise cosine distance`, `Distance to group centroid`, `Cosine distance to global centroid`, `Nearest-Neighbor Distance`, `Unique MeSH descriptors`.
- Include sample sizes in tick labels, panel titles, legends, or adjacent tables when group size differences could affect interpretation.
- Use legends only when they decode colors, markers, line styles, or rings. Place legends outside or below crowded panels when they would obscure data.
- Use light grids for quantitative y-axes (`alpha` around `0.2-0.3`) and avoid heavy gridlines on embedding maps.
- Save figures under the appropriate condition-specific `results/figures/...` directory with descriptive filenames, `dpi` at least `200` for notebook diagnostics and `300` for manuscript-style figures, and `bbox_inches='tight'`.


## Notebooks and analyses

### Compare_proposals_rephrased.ipynb

#### Notebook Scope and Global Settings

Ground-truth audited notebook: `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb`.

Purpose: compare Human and AI research proposals after proposal texts have been rephrased into a standardized neutral academic style. This audit reflects the rendered notebook outputs saved in the `.ipynb` after the July 2026 rephrase refresh. Older result claims from the prior rephrase model should not be reused.

Global settings:

- Condition label: `baseline-minimal-rephrased`.
- Proposal input: `data/prepared/rephrased/minimal/all_proposals.json`.
- Tables: `results/tables/rephrased/minimal`.
- Figures: `results/figures/rephrased/minimal`.
- Full-proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Section-1 / abstract-only embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_rephrased_abstract.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Literature-space projection cache for proposals: `data/embeddings/literature/proposals_section1_lit_umap2d.npy`.

#### `# Setup and Imports`

Baseline-minimal-rephrased rendered result:

- Working directory: `baseline(minimal)-rephrased`.
- Project root: `/Users/eveyhuang/Documents/NICO/human-AI-proposal`.
- PyTorch `2.9.1`; CUDA unavailable.
- Helper functions loaded, including proposal-level mean pairwise diversity, bootstrap 95% CIs, and Holm multiple-testing adjustment.

##### `## Load Prepared Proposal Data and Metadata`

Baseline-minimal-rephrased rendered result:

- Loaded proposals from `data/prepared/rephrased/minimal/all_proposals.json`.
- AI proposals: `69`; Human proposals: `23`.
- AI model counts: GPT-5.2 `23`, Gemini `23`, Claude `23`.
- Metadata coverage: proposals `92`, panel ranking `23`, AI-review ranking `92`, funding `23`.
- Text scope: `standardized_text` with template headers stripped.
- Average cleaned length: AI `1859` characters, Human `1845` characters.

##### `## Load Prepared Full-Proposal Embeddings and Shared Caches`

Baseline-minimal-rephrased rendered result:

- Loaded full-proposal embeddings from `proposal_embeddings_human_ai_rephrased.pkl`.
- AI embeddings shape: `(69, 1024)`; Human embeddings shape: `(23, 1024)`.
- Saved `proposal_metadata.csv` with `92` rows.
- Saved shared caches to `results/tables/rephrased/minimal/cached`.
- `X_prop` shape: `(92, 1024)`; `D_pp` shape: `(92, 92)`.
- Groups: Human `23`, Claude `23`, GPT-5.2 `23`, Gemini `23`, All AI `69`.
- Review ranking coverage: `100.0%`; top-5 outlined proposals: `21.7%`; Human funding coverage: `100.0%`.

#### `# PART I: THEMATIC AND CLUSTER ANALYSIS`

##### `## Analysis 1.1: Topic Modeling (LDA - Exploratory)`

Baseline-minimal-rephrased rendered result:

- Topic-model text: normalized content text (`title + abstract`) to reduce formatting/template confounding.
- Prepared `92` topic-model texts: Human `23`, AI `69`.
- Document-term matrix: `(92, 192)`; dropped `8` domain unigrams while keeping bigrams.
- Topic-count selection tested `k=2..8`; selected `n_topics=2` by the conservative held-out perplexity rule.
- Final LDA: perplexity `228.80`, log-likelihood `-3520.48`.
- Topic labels:
  - Topic_1: `functional data, integrating structural, emergent properties, multi scale` (`46` dominant documents).
  - Topic_2: `protein interaction, decoding emergent, single cell, synthesizing emergent` (`46` dominant documents).
- Stability validation across 10 aligned runs:
  - Topic_1: `60.0% +/- 14.1%` top-10 overlap, cosine `0.813 +/- 0.042`.
  - Topic_2: `47.8% +/- 19.3%` top-10 overlap, cosine `0.784 +/- 0.051`.
- Topic-count sensitivity: selected `k=2` is not associated with Human/AI grouping (`chi2=0.9275`, `p=0.3355`), while larger exploratory `k=3..8` values show significant chi-square tests.
- Outputs: `lda_topic_k_selection.csv`, `lda_topic_contrastive_labels.csv`.

##### `## Analysis 1.2: Topic Distribution and Coverage Per Model`

Baseline-minimal-rephrased rendered result:

- Soft topic participation threshold: `>0.20`.
- Participation counts:
  - Human: Topic_1 `15` (`65%`), Topic_2 `14` (`61%`).
  - Claude: Topic_1 `14` (`61%`), Topic_2 `13` (`57%`).
  - Gemini: Topic_1 `7` (`30%`), Topic_2 `20` (`87%`).
  - GPT-5.2: Topic_1 `16` (`70%`), Topic_2 `13` (`57%`).
- Four-group chi-square `6.1008`, permutation `p=0.0250`.
- Per-topic Fisher tests vs Human: `0/6` significant after Holm correction.
- Strongest unadjusted shifts: Gemini Topic_1 `p=0.0377`, Holm `q=0.2261`; Gemini Topic_2 `p=0.0909`, Holm `q=0.4547`.
- Topic entropy:
  - Human `H=0.6897`, normalized `0.9950`, covered `2/2`, dominant `Topic_1`.
  - Claude `H=0.6904`, normalized `0.9960`, covered `2/2`, dominant `Topic_1`.
  - Gemini `H=0.6142`, normalized `0.8861`, covered `2/2`, dominant `Topic_2`.
  - GPT-5.2 `H=0.6813`, normalized `0.9829`, covered `2/2`, dominant `Topic_1`.
- Outputs: `topic_distribution_per_model.csv`, `topic_distribution_per_model_tests.csv`, `topic_entropy_per_model.csv`.
- Figure: `topic_distribution_comparison.png`.

##### `## Analysis 1.3: Embedding Cluster Structure - Ward Agglomerative + UMAP Cache`

Baseline-minimal-rephrased rendered result:

- Ward k-selection:
  - `k=2`: silhouette `0.9102`, Calinski-Harabasz `199.9` (selected).
  - `k=3`: silhouette `0.8625`, Calinski-Harabasz `112.5`.
  - `k=4`: silhouette `0.8331`, Calinski-Harabasz `79.5`.
  - `k=5`: silhouette `0.1428`, Calinski-Harabasz `62.9`.
- Best k: `2`; cluster sizes `[12, 80]`.
- Ward cluster labels:
  - Cluster_A: `12` documents, `mass spectrometry, 3d genome function, adaptation mitochondrial reticular, analysis bacterial organelles`.
  - Cluster_B: `80` documents, `data understand, decoding emergent, integrating structural, multi scale`.
- Optional proposal BERTopic sensitivity produced `2` non-outlier topics; outlier fraction `0.0%`.
- Cluster membership by group:
  - Human: Cluster_A `6`, Cluster_B `17`.
  - Claude: Cluster_A `2`, Cluster_B `21`.
  - Gemini: Cluster_A `1`, Cluster_B `22`.
  - GPT-5.2: Cluster_A `3`, Cluster_B `20`.
- Fisher tests vs Human: no model-vs-Human cluster contrast survives Holm correction; Claude `q=0.9709`, Gemini `q=0.5755`, GPT-5.2 `q=0.9709`.
- Per-group silhouette / dominant-cluster fraction: Human `0.8558` / `74%`, Claude `0.9315` / `91%`, Gemini `0.9100` / `96%`, GPT-5.2 `0.9250` / `87%`.
- Cached `proposal_umap2d.npy`.
- Outputs: `ward_cluster_bertopic_style_labels.csv`, `proposal_bertopic_assignments.csv`, `proposal_bertopic_topic_labels.csv`, `diversity_cluster_k_selection.csv`, `diversity_cluster_membership_by_group.csv`.
- Figures: `proposal_ward_clusters_labeled_umap.png`, `proposal_bertopic_topics_labeled_umap.png`, `cluster_membership_umap_per_group.png`.

##### `## Analysis 1.4: GMM Cluster Segregation and Per-Model Composition`

Baseline-minimal-rephrased rendered result:

- GMM k-selection selected `k=3` by BIC.
- GMM cluster sizes: `[30, 12, 50]`; all three clusters are mixed under the notebook's dominance thresholds.
- Segregation metrics:
  - NMI `0.0443`, permutation `p=0.0574` (not significant).
  - ARI `0.0856`, permutation `p=0.0123`.
  - Within-Human mean distance `0.3411 +/- 0.3262`.
  - Within-AI mean distance `0.1510 +/- 0.2515`.
  - Between Human-AI mean distance `0.2613 +/- 0.3111`.
  - Between/within ratio `1.0622`, permutation `p=0.0346`.
- Per-model GMM composition:
  - Human: GMM-0 `9` (`39%`), GMM-1 `6` (`26%`), GMM-2 `8` (`35%`).
  - Claude: GMM-0 `3` (`13%`), GMM-1 `2` (`9%`), GMM-2 `18` (`78%`).
  - Gemini: GMM-0 `2` (`9%`), GMM-1 `1` (`4%`), GMM-2 `20` (`87%`).
  - GPT-5.2: GMM-0 `16` (`70%`), GMM-1 `3` (`13%`), GMM-2 `4` (`17%`).
- GMM k=3 vs Ward k=2 agreement: ARI `0.3455`, NMI `0.5738`.
- Outputs: `cluster_gmm_composition_per_model.csv`, `cluster_gmm_vs_ward_agreement.csv`.
- Figures: `cluster_k_selection.png`, `cluster_analysis_visualization.png`, `cluster_composition_per_model.png`.

##### `## Analysis 1.5: LDA Topic-Cluster Correspondence`

Baseline-minimal-rephrased rendered result:

- LDA topics vs Ward clusters: ARI `-0.0050`, NMI `0.0000`.
- Contingency table: Topic_1 has Cluster_A `6`, Cluster_B `40`; Topic_2 has Cluster_A `6`, Cluster_B `40`.
- Interpretation: LDA lexical topics and Ward embedding clusters are complementary, not redundant.
- Outputs: `topic_cluster_contingency.csv`, `topic_cluster_assignment_labels.csv`, `topic_cluster_agreement.csv`.
- Figure: `topic_cluster_correspondence.png`.

##### `### PART I Summary`

Baseline-minimal-rephrased rendered result:

- Topics differ overall across author groups (`perm-p=0.0250`), but per-topic model-vs-Human tests are not significant after Holm correction.
- Ward clustering finds two high-silhouette regions, but model-vs-Human cluster-membership Fisher tests are not significant after Holm correction in the current rerun.
- GMM shows weak but significant Human/AI separation by ARI and between/within distance ratio; NMI is a trend.
- LDA topics and Ward clusters have near-zero agreement.

#### `# PART II: DIVERSITY`

##### `## Analysis 2.1: Within-Group Pairwise Diversity`

Baseline-minimal-rephrased rendered result:

- Group summary:
  - Human: Remote-Clique `0.3263`, proposal mean-pairwise `0.3411`.
  - Claude: Remote-Clique `0.1456`, proposal mean-pairwise `0.1523`.
  - GPT-5.2: Remote-Clique `0.1910`, proposal mean-pairwise `0.1997`.
  - Gemini: Remote-Clique `0.0936`, proposal mean-pairwise `0.0978`.
  - All AI: Remote-Clique `0.1488`, proposal mean-pairwise `0.1510`.
- **[CRITICAL CHANGE] Primary test = group-level permutation (label-shuffle), Holm-corrected. `mean_pairwise_dist` is derived from the shared within-group distance matrix, so the MW/Holm p-values are invalid (non-independent inputs) and are retained below for reference only — do not report them as evidence.** Model-vs-Human tests:
  - Claude: mean difference `-0.1895`, Cliff's delta `-0.826`, **permutation Holm `q=0.0004` `***`** (MW/Holm `5.51e-08`, ref only).
  - Gemini: mean difference `-0.2291`, delta `-0.913`, **permutation Holm `q=0.0004` `***`** (MW/Holm `2.45e-09`, ref only).
  - GPT-5.2: mean difference `-0.1535`, delta `-0.739`, **permutation Holm `q=0.0018` `**`** (MW/Holm `6.67e-07`, ref only).
  - All AI: mean difference `-0.1907`, delta `-0.826`, **permutation Holm `q=0.0004` `***`** (MW/Holm `9.75e-10`, ref only).
- Outputs: `diversity_remote_clique_group_summary.csv`, `diversity_pairwise_proposal_level.csv`, `diversity_pairwise_tests.csv`.
- Figures: `pairwise_diversity_by_model.png`, `pairwise_diversity_boxplot.png`.

##### `## Analysis 2.1b: Pairwise Distance Bimodality Test + GMM`

Baseline-minimal-rephrased rendered result:

- Hartigan dip and GMM BIC:
  - Human: dip `0.1628`, `p=0.0000`, best GMM k `3`.
  - Claude: dip `0.0710`, `p=0.0000`, best GMM k `3`.
  - Gemini: dip `0.0408`, `p=0.0042`, best GMM k `2`.
  - GPT-5.2: dip `0.1040`, `p=0.0000`, best GMM k `3`.
- Outputs: `diversity_pairwise_bimodality_tests.csv`, `diversity_pairwise_gmm_summary.csv`.
- Figure: `pairwise_diversity_bimodality_gmm.png`.

##### `## Analysis 2.1c: Cross-Group Topic Space Alignment`

Baseline-minimal-rephrased rendered result:

- AI-to-nearest-Human / Human-to-nearest-AI distances:
  - Claude: `0.0418 +/- 0.0305` / `0.0775 +/- 0.0740`.
  - Gemini: `0.0422 +/- 0.0286` / `0.0881 +/- 0.0844`.
  - GPT-5.2: `0.0475 +/- 0.0351` / `0.0733 +/- 0.0654`.
- **[CRITICAL CHANGE] AI-to-nearest-Human distances are matrix-derived (nearest-neighbor distances over the shared cross-group distance matrix), so MW/Holm is not valid inference here. Compute a label-permutation test on the group-level statistic and report that as primary; the MW/Holm q-values below are reference-only and must not carry significance claims.** AI-to-nearest-Human tests:
  - Claude vs Gemini `q=0.0305` (MW, ref only).
  - Claude vs GPT-5.2 `q=0.2080` (MW, ref only).
  - Gemini vs GPT-5.2 `q=0.8605` (MW, ref only).
- Outputs: `diversity_cross_group_nearest_human.csv`, `diversity_cross_group_alignment_tests.csv`.
- Figure: `cross_group_topic_alignment.png`.

##### `## Analysis 2.1d: Within-Cluster and Between-Cluster Diversity`

Baseline-minimal-rephrased rendered result:

- Within-cluster mean pairwise diversity:
  - Human Cluster_A `n=6`, mean `0.2416`; Human Cluster_B `n=17`, mean `0.0577`.
  - Claude Cluster_A `n=2`, mean `0.1764`; Claude Cluster_B `n=21`, mean `0.0375`.
  - Gemini Cluster_A `n=1`, mean `0.0000`; Gemini Cluster_B `n=22`, mean `0.0363`.
  - GPT-5.2 Cluster_A `n=3`, mean `0.1544`; GPT-5.2 Cluster_B `n=20`, mean `0.0383`.
- Between-cluster gaps: Human `0.7337`, Claude `0.7252`, Gemini `0.7445`, GPT-5.2 `0.7131`.
- **[CRITICAL CHANGE] Within-cluster MPD is matrix-derived and heavily coupled (every value comes from one cluster's pairwise matrix). The Cluster_B q-values below (e.g. `1.58e-46`) are an artifact of treating dependent distances as i.i.d. and grossly overstate evidence — do not report them. Replace with a cluster-conditional label-permutation test and report that as primary; the MW/Holm q-values are reference-only.** Within-cluster tests vs Human:
  - Cluster_A: Claude `q=0.6250`; GPT-5.2 `q=0.0784`; Gemini not tested (`n=1`). (MW, ref only.)
  - Cluster_B: Claude `q=6.59e-39`; Gemini `q=1.58e-46`; GPT-5.2 `q=1.88e-38`. (MW, ref only — not valid inference.)
- Outputs: `diversity_within_cluster_by_group.csv`, `diversity_between_cluster_gap.csv`.
- Figure: `diversity_cluster_aware_comparison.png`.

##### `### 2.2a: Within-Group Centroid Dispersion`

Baseline-minimal-rephrased rendered result:

- Centroid LOO means and Span-90:
  - Human `0.1953`, Span-90 `0.5129`.
  - Claude `0.0813`, Span-90 `0.0315`.
  - GPT-5.2 `0.1084`, Span-90 `0.4607`.
  - Gemini `0.0515`, Span-90 `0.0236`.
  - All AI `0.0793`, Span-90 `0.0326`.
- **[CRITICAL CHANGE] Primary test = group-level permutation (label-shuffle), Holm-corrected. LOO-centroid distance is matrix-derived, so the MW/Holm values are reference-only and must not be reported as evidence.** Human comparisons:
  - Claude: mean difference `-0.1149`, delta `-0.826`, **permutation Holm `q=0.0464` `*`** (MW/Holm `5.51e-08`, ref only).
  - Gemini: mean difference `-0.1434`, delta `-0.913`, **permutation Holm `q=0.0064` `**`** (MW/Holm `2.45e-09`, ref only).
  - GPT-5.2: mean difference `-0.0880`, delta `-0.739`, **permutation Holm `q=0.0945` ns** (MW/Holm `6.67e-07`, ref only).
  - All AI: mean difference `-0.1154`, delta `-0.826`, **permutation Holm `q=0.0168` `*`** (MW/Holm `9.75e-10`, ref only).
- Outputs: `centroid_distances.csv`, `diversity_span90_group_summary.csv`, `diversity_centroid_pairwise_tests.csv`.
- Figure: `centroid_dispersion_by_model.png`.

##### `### 2.2b: Between-Group Global-Centroid Distance`

Baseline-minimal-rephrased rendered result:

- Global-centroid mean distance: Human `0.1913`, Claude `0.0784`, GPT-5.2 `0.1031`, Gemini `0.0542`, All AI `0.0786`.
- **[CRITICAL CHANGE] Primary test = group-level permutation (label-shuffle), Holm-corrected. Global-centroid distance is matrix-derived, so MW/Holm is reference-only. Under the valid permutation test NO per-model global-centroid contrast is significant — the MW `***`/`**` stars were an artifact of the independence violation. (The pooled All-AI contrast in the binary notebook does survive at perm `p=0.0078`; see the binary Analysis 2.2b.)** Human comparisons:
  - Human vs Claude: mean difference `0.1128`, delta `0.682`, **permutation Holm `q=0.3760` ns** (MW/Holm `0.000614`, ref only).
  - Human vs Gemini: mean difference `0.1370`, delta `0.766`, **permutation Holm `q=0.0855` ns** (MW/Holm `0.000082`, ref only).
  - Human vs GPT-5.2: mean difference `0.0882`, delta `0.641`, **permutation Holm `q=0.9575` ns** (MW/Holm `0.001435`, ref only).
  - Human vs All AI: mean difference `0.1127`, delta `0.696`, **permutation Holm `q=0.0830` ns** (MW/Holm `0.000006`, ref only).
- Outputs: `between_group_global_centroid_distances.csv`, `between_group_global_centroid_group_summary.csv`, `between_group_global_centroid_pairwise_tests.csv`.
- Figure: `between_group_global_centroid_dispersion.png`.

##### `## Analysis 2.2c: MST Dispersion`

Baseline-minimal-rephrased rendered result:

- MST dispersion: Human `0.1004`, Claude `0.0623`, GPT-5.2 `0.0667`, Gemini `0.0584`, All AI `0.0419`.
- Permutation tests vs Human after Holm:
  - Claude difference `-0.0381`, `q=0.0333`.
  - Gemini difference `-0.0420`, `q=0.0333`.
  - GPT-5.2 difference `-0.0337`, `q=0.0333`.
  - All AI difference `-0.0584`, `q=0.0028`.
- Outputs: `diversity_mst_group_summary.csv`, `diversity_mst_pairwise_permutation.csv`.
- Figure: `diversity_mst_dispersion.png`.

##### `## Analysis 2.2d: Sparseness (Medoid-Based Dispersion)`

Baseline-minimal-rephrased rendered result:

- Sparseness: Human `0.2218`, Claude `0.0906`, GPT-5.2 `0.1194`, Gemini `0.0597`, All AI `0.0923`.
- **[CRITICAL CHANGE] Primary test = group-level permutation (label-shuffle), Holm-corrected. Medoid sparseness is matrix-derived, so the MW/Holm values are reference-only.** Pairwise tests vs Human:
  - Claude: mean difference `-0.1292`, delta `-0.693`, **permutation Holm `q=0.0486` `*`** (MW/Holm `6.36e-06`, ref only).
  - Gemini: mean difference `-0.1621`, delta `-0.822`, **permutation Holm `q=0.0064` `**`** (MW/Holm `1.27e-07`, ref only).
  - GPT-5.2: mean difference `-0.1010`, delta `-0.647`, **permutation Holm `q=0.0907` ns** (MW/Holm `1.34e-05`, ref only).
  - All AI: mean difference `-0.1307`, delta `-0.721`, **permutation Holm `q=0.0144` `*`** (MW/Holm `1.27e-07`, ref only).
- Outputs: `diversity_medoid_distances.csv`, `diversity_sparseness_group_summary.csv`, `diversity_sparseness_pairwise_tests.csv`.
- Figure: `diversity_sparseness_medoid.png`.

##### `## Analysis 2.3: Nearest-Neighbor Isolation and Outlier Detection (Chamfer / NN)`

Baseline-minimal-rephrased rendered result:

- Chamfer/mean NN distance: Human `0.0751`, Claude `0.0386`, GPT-5.2 `0.0409`, Gemini `0.0566`, All AI `0.0330`.
- **[CRITICAL CHANGE] Primary test = group-level permutation (label-shuffle), Holm-corrected. Nearest-neighbor / Chamfer distance is matrix-derived, so the MW/Holm values are reference-only.** NN tests vs Human:
  - Claude: mean difference `-0.0338`, delta `-0.826`, **permutation Holm `q=0.0186` `*`** (MW/Holm `5.01e-06`, ref only).
  - Gemini: mean difference `-0.0358`, delta `-0.826`, **permutation Holm `q=0.0186` `*`** (MW/Holm `5.01e-06`, ref only).
  - GPT-5.2: mean difference `-0.0286`, delta `-0.696`, **permutation Holm `q=0.0352` `*`** (MW/Holm `5.54e-05`, ref only).
  - All AI: mean difference `-0.0328`, delta `-0.783`, **permutation Holm `q=0.0020` `**`** (MW/Holm `8.81e-08`, ref only).
- Unadjusted NN outliers: threshold `0.0883`, total `10/92`; Human `6`, GPT-5.2 `2`, Gemini `1`, Claude `1`.
- Nearest-neighbor source composition: Human nearest Human `6/23`; Claude nearest Human `0/23`, same group `11/23`, other AI `12/23`; GPT-5.2 nearest Human `1/23`, same group `12/23`, other AI `10/23`; Gemini nearest Human `0/23`, same group `13/23`, other AI `10/23`; All AI nearest Human `1/69`, same group `68/69`.
- Outputs: `nn_distances.csv`, `mean_knn_distances_k5.csv`, `diversity_chamfer_group_summary.csv`, `nearest_neighbor_source_composition.csv`, `diversity_nn_pairwise_tests.csv`.
- Figures: `nearest_neighbor_by_model.png`, `embedding_space_umap_reviewaware.png`.

##### `## Analysis 2.4: UMAP Embedding-Space Visualization`

Baseline-minimal-rephrased rendered result:

- Loaded cached UMAP from `results/tables/rephrased/minimal/cached/proposal_umap2d.npy`, shape `(92, 2)`.
- Saved `embedding_space_umap_2d.png`.
- Saved review-aware UMAP `embedding_space_umap_reviewaware.png`.
- Saved per-cluster detail view `embedding_space_umap_per_cluster_zoom.png`.

##### `## Analysis 2.5: Grid Entropy of Proposal Occupancy`

Baseline-minimal-rephrased rendered result:

- PCA-grid entropy (`5 x 5`), normalized:
  - Human `0.3304`.
  - Claude `0.2802`.
  - GPT-5.2 `0.2790`.
  - Gemini `0.2297`.
  - All AI `0.2950`.
- Permutation tests vs Human after Holm: all non-significant; Claude `q=1.0`, Gemini `q=1.0`, GPT-5.2 `q=1.0`, All AI `q=1.0`.
- Outputs: `diversity_entropy_group_summary.csv`, `diversity_entropy_pairwise_permutation.csv`.
- Figure: `diversity_entropy_group_summary.png`.

#### `# PART III: NOVELTY AND LITERATURE-ANCHORED ANALYSES`

##### `## Literature Corpus and Shared Novelty Precomputation`

Baseline-minimal-rephrased rendered result:

- Loaded `39538` PubMed articles from `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.
- Loaded cached literature embeddings from `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Loaded abstract-only proposal embeddings from `proposal_embeddings_rephrased_abstract.pkl`.
- Literature-space analyses use Section-1 / abstract-only proposal embeddings, not full-proposal embeddings.
- Loaded literature kNN cache `lit_knn_distances_50.npy`.
- Proposal-to-literature distance matrix `D_pl`: `(92, 39538)`.

##### `## Step 2.5: Element Novelty Percentiles`

Baseline-minimal-rephrased rendered result:

- Group means:
  - Human: ElementNovel-0 `0.0993`, ElementNovel-10 `0.2171`.
  - Claude: ElementNovel-0 `0.0871`, ElementNovel-10 `0.1965`.
  - Gemini: ElementNovel-0 `0.0923`, ElementNovel-10 `0.1985`.
  - GPT-5.2: ElementNovel-0 `0.0818`, ElementNovel-10 `0.1839`.
- MW Holm tests: no ElementNovel model-vs-Human comparison survives MW Holm correction.
- Permutation Holm tests flag GPT-5.2 for ElementNovel-1 (`q=0.0330`) and ElementNovel-5 (`q=0.0414`); ElementNovel-10 is a trend (`q=0.0528`).
- Outputs: `novelty_element_percentiles.csv`, `novelty_element_percentiles_pairwise_tests.csv`.
- Figure: `novelty_analysis_element_percentiles.png`.

##### `## Step 3: Mean kNN Novelty Scores and Local Density`

Baseline-minimal-rephrased rendered result:

- MeanKNN-10 group means: Human `0.1151`, Claude `0.1009`, Gemini `0.1045`, GPT-5.2 `0.0918`.
- MW Holm tests: no MeanKNN model-vs-Human comparison survives MW Holm correction.
- Permutation Holm tests flag GPT-5.2 for MeanKNN-5 (`q=0.0426`), MeanKNN-10 (`q=0.0363`), MeanKNN-20 (`q=0.0348`), and MeanKNN-50 (`q=0.0339`).
- Normalized novelty:
  - `novelty_ratio`: no model-vs-Human contrast significant after Holm correction.
  - `novelty_z`: no MW Holm significance; GPT-5.2 has permutation trend `q=0.0969`.
- Outputs: `novelty_mean_knn_scores.csv`, `novelty_mean_knn_pairwise_tests.csv`, `novelty_local_density_normalized.csv`, `novelty_local_density_pairwise_tests.csv`, `novelty_all_pairwise_tests.csv`.
- Figures: `novelty_analysis_mean_knn.png`, `novelty_analysis_local_density.png`.

##### `## Step 7: Literature-Space UMAP and Step 7B Outliers`

Baseline-minimal-rephrased rendered result:

- Literature-space UMAP loaded fixed literature coordinates `lit_umap2d.npy` with shape `(39538, 2)` and cached proposal projection `proposals_section1_lit_umap2d.npy` with shape `(92, 2)`.
- Saved `proposals_in_literature_space_umap.png`.
- Literature-space outlier prevalence tests:
  - Mean-10NN outliers: Human `7/23` (`30.4%`), Claude `1/23` (`4.3%`, Holm `q=0.0940`), Gemini `2/23` (`8.7%`, `q=0.1346`), GPT-5.2 `0/23` (`q=0.0275`).
  - ElementNovel-0 outliers: Human `6/23` (`26.1%`), Claude `2/23`, Gemini `2/23`, GPT-5.2 `0/23`; none significant after Holm (`q>=0.0647`).
  - `novelty_z` outliers: Human `5/23` (`21.7%`), Claude `2/23`, Gemini `3/23`, GPT-5.2 `0/23`; none significant after Holm (`q>=0.1473`).
- Saved `proposals_in_literature_space_umap_outliers_comparison_k10.png`.
- Outputs: `literature_space_outliers_mean_knn_k10.csv`, `literature_space_outliers_element0.csv`, `literature_space_outliers_z.csv`, `literature_space_outlier_prevalence_tests.csv`, `nearest_literature_neighbors_top3.csv`, `novelty_scores_from_literature.csv`.

##### `## Analysis 3.5: Literature-Anchored UMAP - BERTopic Embedding Regions`

Baseline-minimal-rephrased rendered result:

- Reused cached Section-1 proposal projection: `data/embeddings/literature/proposals_section1_lit_umap2d.npy`.
- BERTopic display-label strategy: `contrastive_phrase_v4`.
- Saved primary combined literature-region UMAP: `literature_umap_with_bertopic_regions.png`.
- Saved split zoom: `literature_umap_with_bertopic_regions_split_zoom.png`.
- Proposal x split for zoom panes: `6.325`; left pane `n=36`, right pane `n=56`.
- Saved per-author-group panels: `literature_umap_bertopic_by_author_group.png`.

##### `## Analysis 3.6: Literature Embedding-Region Coverage per Author Group`

Baseline-minimal-rephrased rendered result:

- Group-level BERTopic region coverage:
  - Human: breadth `4`, entropy `1.2807`, effective regions `3.5991`, dominant fraction `0.4804`.
  - Claude: breadth `4`, entropy `1.0942`, effective regions `2.9867`, dominant fraction `0.5652`.
  - Gemini: breadth `2`, entropy `0.9029`, effective regions `2.4668`, dominant fraction `0.6522`.
  - GPT-5.2: breadth `3`, entropy `0.8833`, effective regions `2.4189`, dominant fraction `0.6717`.
- MW tests vs Human after Holm: no BERTopic proposal-level region metric is significant; max-region-weight strongest raw tests are Gemini `p=0.0396`, Holm `q=0.3561`, and GPT-5.2 `p=0.0923`, Holm `q=0.5851`.
- Unassigned neighbor fractions are all `0.0`.
- Outputs: `bertopic_region_coverage_per_group.csv`, `bertopic_region_coverage_per_proposal.csv`, `bertopic_region_coverage_tests.csv`, `lit_topic_coverage_per_group.csv`, `lit_topic_coverage_per_proposal.csv`, `lit_topic_coverage_tests.csv`.
- Figure: `bertopic_region_coverage_stacked_bar.png`.

##### `## Analysis 3.7: MeSH Term Coverage per Author Group`

Baseline-minimal-rephrased rendered result:

- Group MeSH summary:
  - Human: mean unique MeSH `80.00`, median `76.0`, SD `21.02`, group union `825`.
  - Claude: mean `90.30`, median `82.0`, SD `25.64`, group union `834`.
  - Gemini: mean `84.26`, median `75.0`, SD `29.07`, group union `706`.
  - GPT-5.2: mean `80.70`, median `68.0`, SD `26.86`, group union `623`.
- MW tests vs Human after Holm: Claude `q=0.9359`, Gemini `q=1.0`, GPT-5.2 `q=1.0`; no significant MeSH coverage differences.
- Outputs: `mesh_coverage_per_proposal.csv`, `mesh_coverage_group_summary.csv`, `mesh_coverage_tests.csv`.
- Figure: `mesh_coverage_by_group.png`.

##### `## Analysis 3.8: Publication Year Recency of Nearest Literature`

Baseline-minimal-rephrased rendered result:

- Within-BERTopic-region MW tests:
  - Stratum `0`: Claude median `2020.75` vs Human `2021.75`, Holm `q=1.0`; Gemini `2021.50` vs `2021.75`, `q=0.6141`; GPT-5.2 `2021.50` vs `2021.75`, `q=1.0`.
  - Stratum `1`: Claude median `2021.00` vs Human `2022.00`, `q=1.0`; Gemini `2023.00` vs `2022.00`, `q=1.0`; GPT-5.2 `2022.50` vs `2022.00`, `q=1.0`.
- No within-region publication-year contrast is significant after Holm correction.
- Outputs: `lit_neighbor_year_per_proposal.csv`, `lit_neighbor_year_within_region_tests.csv`, `lit_neighbor_year_region_group_summary.csv`.
- Figure: `lit_neighbor_year_by_group_within_bertopic_region.png`.

##### `## Unified Proposal-Level Metric Export`

Baseline-minimal-rephrased rendered result:

- Master dataframe rows after merges: `92` (expected `92`).
- Merged BERTopic literature-region metrics into `proposal_metrics_master_df`.
- Saved `proposal_metrics_master.csv` with `92` rows.

#### `# PART IV: Style Baseline`

##### `### Extract stylistic features`

Baseline-minimal-rephrased rendered result:

- Built style feature table: `92` documents x `18` features.
- Group means:
  - AI average sentence length `19.736`, stopword rate `0.339`, hedge rate `0.000`, FK grade `16.983`.
  - Human average sentence length `19.642`, stopword rate `0.342`, hedge rate `0.001`, FK grade `16.749`.
- Saved `style_features.csv` with `92` rows x `21` columns.
- Saved `style_features_by_model_boxplots.png`.

##### `### Style-Only Baseline: Can Style Predict Source?`

Baseline-minimal-rephrased rendered result:

- Style-only Human-vs-AI classifier used `18` style features.
- CV AUROC `0.521 +/- 0.227`.
- CV balanced accuracy `0.531 +/- 0.133`.
- Permutation test: observed AUROC `0.521`, null mean `0.504 +/- 0.096`, `p=0.4496`.
- Top standardized coefficients by absolute value: `hedge_rate` `-0.9277`, `newline_per_1k_chars` `0.5140`, `type_token_ratio` `0.4882`, `n_sents` `-0.4749`, `comma_per_1k_chars` `0.3929`.
- Interpretation: style-only separation is weak and non-significant.
- Figure: `style_only_baseline_viz.png`.

##### Non-rendered style-adjusted analyses previously listed

Baseline-minimal-rephrased rendered result:

- The audited notebook does not contain rendered cells for style residualization, style-adjusted centroid dispersion, style-adjusted NN residual embeddings, or style-adjusted 2D UMAP analyses.
- Corresponding figures are not present in `results/figures/rephrased/minimal`: `centroid_dispersion_style_adjusted.png`, `nearest_neighbor_by_model_style_adjusted.png`, and `embedding_space_2d_style_adjusted.png`.

##### `# Save All Proposals to a Single JSON`

Baseline-minimal-rephrased rendered result:

- Input JSON: `data/prepared/rephrased/minimal/all_proposals.json`.
- Output JSON: `results/tables/rephrased/minimal/all_proposals.json`.
- Master rows: `92`; output records: `92`; records missing a master row: `0`.
- Missing values in diversity family: `0`; missing values in novelty family: `0`.
- Outlier flag alignment with top-10% rule: `1.000` for `is_lit_outlier_mean10`, `is_lit_outlier_element0`, and `is_lit_outlier_z`.

##### Baseline-minimal-rephrased Results Summary

- Human proposals remain more semantically spread than AI proposals across pairwise diversity, centroid dispersion, MST dispersion, sparseness, and nearest-neighbor isolation.
- Ward cluster membership is less sharply model-separated than the older rerun: no model-vs-Human Ward Fisher contrast survives Holm correction.
- GMM still shows weak Human/AI separation by ARI and between/within ratio, but NMI is not significant.
- Topic distribution differs overall across author groups, driven mainly by Gemini's topic mix, but no per-topic model-vs-Human contrast survives Holm correction.
- Literature novelty effects are now concentrated mainly in GPT-5.2 under permutation tests; no ElementNovel or MeanKNN model-vs-Human contrast survives MW Holm correction.
- Literature-space outlier prevalence remains higher for Human, with GPT-5.2 having `0/23` mean-10NN outliers vs Human `7/23` after Holm correction.
- BERTopic literature-region coverage, MeSH coverage, and literature-neighbor publication year do not show Holm-significant model-vs-Human differences in the current four-group notebook.
- Style-only classification remains weak and non-significant.

##### Diversity Metric Definitions Aligned to Table-3 Naming

Current implementation status for future notebook edits:

1. **Remote-Clique** (`implemented partially`)

- Current Analysis 2.1 computes upper-triangle pairwise cosine distances and proposal-level mean distance-to-others for inference.
- To report the exact Table-3 Remote-Clique value, add `RC = (1 / N^2) * sum_i sum_j d(x_i, x_j)` explicitly and export it by group.

1. **Chamfer Distance** (`implemented for k=1`)

- Current Analysis 2.3 implements the nearest-neighbor version: `CD = (1 / N) * sum_i min_{j != i} d(x_i, x_j)`.
- Analysis 2.3-B adds a mean-5NN robustness variant, not the canonical k=1 Chamfer value.

1. **MST Dispersion** (`implemented`)

- Build a minimum spanning tree over each group's complete cosine-distance graph.
- Report mean MST edge length: `(1 / (N - 1)) * sum_{(i,j) in MST} d(x_i, x_j)`.

1. **Span** (`implemented as Span-90 group summary`)

- Current Analysis 2.2 reports mean distance to centroid and exports `diversity_span90_group_summary.csv` for percentile span.

1. **Sparseness** (`implemented`)

- Compute the group medoid `m = argmin_j sum_i d(x_i, x_j)`.
- Report `Sparseness = (1 / N) * sum_i d(x_i, m)`.

1. **Entropy (grid-based embedding occupancy)** (`implemented`)

- Project embeddings to 2D, partition into a `5 x 5` grid, compute occupancy frequencies, and report Shannon entropy plus normalized entropy.
- Keep this distinct from LDA topic entropy in Analysis 1.2.

### Compare_proposals_all_ai.ipynb

#### Notebook Scope and Global Settings

Notebook path: `baseline(minimal)-rephrased/compare_proposals_all_ai.ipynb`.

Purpose: compare Human proposals against the pooled AI proposal set (Claude + Gemini + GPT-5.2 combined, `n=69`) under the rephrased/style-controlled condition. This audit reflects the rendered notebook outputs saved in the `.ipynb`; primary contrasts are binary (`Human` vs `All AI`), and the notebook uses one bootstrap subsampling scheme (`1000` draws of `n=23`) for N-sensitive diversity and breadth metrics.

Global settings:

- Condition label: `baseline-minimal-rephrased`.
- Proposal input: `data/prepared/rephrased/minimal/all_proposals.json`.
- Tables output root: `results/tables/rephrased/minimal/all_ai/`.
- Figures output root: `results/figures/rephrased/minimal/all_ai/`.
- Proposal-space analyses use full-proposal embeddings. Proposal-to-literature analyses use Section-1 / abstract-only proposal embeddings from `proposal_embeddings_rephrased_abstract.pkl`.

#### `## Condition Configuration`

Baseline-minimal-rephrased rendered result:

- Binary comparison setup: Human `23` vs pooled AI `69`.
- Bootstrap policy for N-sensitive metrics: `1000` subsamples of size `23`, seed `42`.
- `is_top5_ranked` was reset to Human top-5 plus the five smallest pooled AI-only global ranks.

#### `## Load Shared Precomputed Caches`

Baseline-minimal-rephrased rendered result:

- Proposal distance matrix `D_pp`: `(92, 92)`.
- Proposal PCA coordinates `X_pca2d`: `(92, 2)`.
- Proposal UMAP coordinates `X_umap2d`: `(92, 2)`.
- Literature self-kNN distances `lit_knn_distances_50`: `(39538, 50)`.
- Full proposal embeddings `X_prop`: `(92, 1024)`.
- Literature embeddings `X_lit`: `(39538, 1024)`.
- Section-1 / abstract-only proposal embeddings `X_prop_nov`: `(92, 1024)`.
- Proposal-to-literature nearest-neighbor cache: sorted indices `(92, 39538)`, sorted top distances `(92, 50)`.
- Metadata loaded as `proposal_meta: (92, 14)` with group counts Human `23`, All AI `69` (`23` Claude, `23` Gemini, `23` GPT-5.2).

#### `## Generate Bootstrap Subsamples (One-Time - Reused by All N-Sensitive Analyses)`

Baseline-minimal-rephrased rendered result:

- Saved bootstrap subsamples: `1000 x 23`.
- Mean model composition per subsample:
  - Claude `7.72 +/- 1.90`.
  - Gemini `7.64 +/- 1.91`.
  - GPT-5.2 `7.64 +/- 1.90`.

#### `# PREFLIGHT: AI Model Heterogeneity Tests`

Baseline-minimal-rephrased rendered result:

- `0/14` audited outcomes showed significant Claude/Gemini/GPT-5.2 heterogeneity after Holm correction.
- All final Holm-adjusted p-values are `1.0` in `supplementary_ai_heterogeneity_kruskal_wallis.csv`.
- The largest raw Kruskal-Wallis effects were still non-significant after correction, including `mean_knn_20` (`H=3.1216`, raw `p=0.2100`) and `element_novel_0` (`H=2.8394`, raw `p=0.2418`).

#### `# PART I: THEMATIC AND CLUSTER ANALYSIS`

##### `## Analysis 1.1: LDA Topic Distribution (Human vs All-AI)`

Baseline-minimal-rephrased rendered result:

- Dominant-topic counts:
  - Human: Topic_1 `14` (`60.9%`), Topic_2 `9` (`39.1%`).
  - All AI: Topic_1 `32` (`46.4%`), Topic_2 `37` (`53.6%`).
- Chi-square `0.9275`, `df=1`, asymptotic `p=0.3355`.
- Permutation `p=0.3271`.
- Binary Human-vs-All-AI LDA topic distribution is not significant.
- Output: `lda_topic_distribution_human_vs_allai.csv`.

##### `## Analysis 1.2: Topic Participation (Human vs All-AI)`

Baseline-minimal-rephrased rendered result:

- Topic participation Fisher tests:
  - Topic_1: Human-in `14`, AI-in `32`, Fisher `p=0.3357`, Holm `q=0.6713`.
  - Topic_2: Human-in `9`, AI-in `37`, Fisher `p=0.3357`, Holm `q=0.6713`.
- No binary topic-participation contrast survives Holm correction.
- Output: `topic_participation_human_vs_allai.csv`.

##### `## Analysis 1.3: Ward Cluster Membership (Human vs All-AI)`

Baseline-minimal-rephrased rendered result:

- Cluster counts:
  - Cluster_A: Human `6`, All AI `6`.
  - Cluster_B: Human `17`, All AI `63`.
- Ward cluster Fisher exact: odds ratio `3.706`, `p=0.0665`.
- This is a trend toward Human over-representation in Cluster_A, but not significant at `p<0.05`.
- Figure: `cluster_membership_human_vs_allai.png`.
- Outputs: `cluster_membership_human_vs_allai.csv`, `supplementary_cluster_membership_by_model.csv`.

##### `## Analysis 1.4: GMM Segregation (Human vs AI)`

Baseline-minimal-rephrased rendered result:

- Within-Human mean distance `0.3411`.
- Within-AI mean distance `0.1510`.
- Between-group mean distance `0.2613`.
- Between/within ratio `1.0622`, permutation `p=0.0305`.
- Binary Human-vs-AI cluster agreement: NMI `0.5772`, ARI `0.3259`.
- Output: `gmm_segregation_human_vs_allai.csv`.

##### `## Analysis 1.5: LDA Topic-Cluster Correspondence`

Baseline-minimal-rephrased rendered result:

- The all-AI notebook reuses the cached topic-cluster correspondence from `compare_proposals_rephrased.ipynb`.
- Current inherited correspondence result remains near zero: ARI `-0.0068`, NMI `0.0006`, supporting the interpretation that lexical LDA topics and embedding Ward clusters capture complementary structure.

#### `# PART II: DIVERSITY`

##### `## Analysis 2.1: Within-Group Pairwise Diversity`

Baseline-minimal-rephrased rendered result:

- Human mean pairwise distance `0.3411`.
- AI full-pool mean pairwise distance `0.1510` (`n=69`).
- AI bootstrap mean pairwise distance `0.1524`, `95% CI [0.0393, 0.2512]` (`n=23`-equivalent).
- Within-model average `0.1499`.
- **[CRITICAL CHANGE] Primary = permutation `p=0.0001` `***` (matrix-derived metric). The MW `p=3.50e-09` is reference-only and must not be reported as evidence — this is exactly the invalid headline p-value flagged in review.** Cliff's delta `-0.826` `[-0.942, -0.681]`.
- Figure: `pairwise_diversity_human_vs_allai.png`.
- Output: `diversity_pairwise_human_vs_allai.csv`.

##### `## Analysis 2.1b: Pairwise Distance Bimodality (Decomposed)`

Baseline-minimal-rephrased rendered result:

- Hartigan dip tests:
  - Human `0.1628`, `p=0.0000`.
  - All-AI pooled `0.0671`, `p=0.0000`.
  - AI within-model pairs `0.0692`, `p=0.0000`.
  - AI between-model pairs `0.0665`, `p=0.0000`.
- All pairwise-distance distributions are non-unimodal in the rendered notebook.
- Figure: `pairwise_diversity_bimodality_decomposed.png`.
- Output: `diversity_pairwise_bimodality_decomposed.csv`.

##### `## Analysis 2.1c: Cross-Group Topic Space Alignment`

Baseline-minimal-rephrased rendered result:

- AI-to-nearest-Human mean distance `0.0439`.
- Human-to-nearest-AI mean distance `0.0707`.
- **[CRITICAL CHANGE] Matrix-derived cross-group distance — replace MW with a label-permutation test as primary; MW `p=0.1333` is reference-only (result is null either way).** Cliff's delta `-0.210` `[-0.509, 0.086]`.
- The nearest-cross-group asymmetry is not significant in the current rendered output.
- Figure: `cross_group_topic_alignment_human_vs_allai.png`.
- Output: `diversity_cross_group_alignment_human_vs_allai.csv`.

##### `## Analysis 2.1d: Within-Cluster Diversity`

Baseline-minimal-rephrased rendered result:

- Within-cluster MPD:
  - Cluster_A: Human `n=6`, MPD `0.2416`; All AI `n=6`, MPD `0.1493`.
  - Cluster_B: Human `n=17`, MPD `0.0577`; All AI `n=63`, MPD `0.0402`.
- **[CRITICAL CHANGE] Within-cluster MPD is matrix-derived and heavily coupled; the MW/Holm p-values below (especially Cluster_B `4.23e-10`) are an i.i.d.-violation artifact and must not be reported. Use a cluster-conditional label-permutation test as primary; MW/Holm reference-only.** Within-cluster tests:
  - Cluster_A: Cliff's delta `-1.000` (MW `p=0.00216`, Holm `q=0.00216`, ref only).
  - Cluster_B: Cliff's delta `-0.993` (MW `p=4.23e-10`, Holm `q=8.46e-10`, ref only).
- Between-cluster gaps are similar by group: Human `0.7337`, All AI `0.7235`.
- Outputs: `diversity_within_cluster_human_vs_allai.csv`, `diversity_within_cluster_tests_human_vs_allai.csv`, `diversity_between_cluster_gap_human_vs_allai.csv`.

##### `## Analysis 2.2a: Centroid Dispersion (LOO)`

Baseline-minimal-rephrased rendered result:

- Human LOO centroid distance `0.1953`.
- AI full-pool `0.0793`.
- AI bootstrap mean `0.0821`, `95% CI [0.0207, 0.1388]`.
- **[CRITICAL CHANGE] Primary = permutation `p=0.0089` `**` (matrix-derived metric); MW `p<0.0001` reference-only.** Cliff's delta `-0.826`.
- Figure: `centroid_dispersion_human_vs_allai.png`.
- Output: `diversity_centroid_human_vs_allai.csv`.

##### `## Analysis 2.2b: Global-Centroid Distance`

Baseline-minimal-rephrased rendered result:

- Human global-centroid mean `0.1913`.
- AI full-pool mean `0.0786`.
- AI bootstrap mean `0.0793`, `95% CI [0.0276, 0.1310]`.
- **[CRITICAL CHANGE] Primary = permutation `p=0.0078` `**` (matrix-derived metric); MW `p<0.0001` reference-only. Report this pooled All-AI result — the four-group per-model global-centroid contrasts do NOT survive the permutation test, so per-model MW stars must not be reported.** Cliff's delta `-0.696`.
- Figure: `global_centroid_dispersion_human_vs_allai.png`.
- Output: `diversity_global_centroid_human_vs_allai.csv`.

##### `## Analysis 2.2c: MST Dispersion`

Baseline-minimal-rephrased rendered result:

- Human MST mean edge `0.1004`.
- AI full-pool MST mean edge `0.0419`.
- AI bootstrap mean `0.0613`, `95% CI [0.0276, 0.0737]`.
- Observed difference `-0.0584`, permutation `p=0.0010`.
- Figure: `diversity_mst_human_vs_allai.png`.
- Output: `diversity_mst_human_vs_allai.csv`.

##### `## Analysis 2.2d: Sparseness (Medoid-Based Dispersion)`

Baseline-minimal-rephrased rendered result:

- Human sparseness `0.2218`.
- AI full-pool sparseness `0.0923`.
- AI bootstrap mean `0.0926`, `95% CI [0.0313, 0.1533]`.
- **[CRITICAL CHANGE] Primary = permutation `p=0.0098` `**` (matrix-derived metric); MW `p<0.0001` reference-only.** Cliff's delta `-0.699`.
- Figure: `diversity_sparseness_human_vs_allai.png`.
- Output: `diversity_sparseness_human_vs_allai.csv`.

##### `## Analysis 2.3: Nearest-Neighbor Isolation (Chamfer)`

Baseline-minimal-rephrased rendered result:

- Human Chamfer `0.0751`.
- AI full-pool Chamfer `0.0330`.
- AI bootstrap mean `0.0432`, `95% CI [0.0269, 0.0589]`.
- **[CRITICAL CHANGE] Primary = permutation `p=0.0002` `***` (matrix-derived metric); MW `p<0.0001` reference-only.** Cliff's delta `-0.869`.
- AI nearest-neighbor source composition: Claude `25`, Gemini `22`, GPT `21`, Human `1`.
- Figure: `nearest_neighbor_human_vs_allai.png`.
- Outputs: `diversity_chamfer_human_vs_allai.csv`, `nearest_neighbor_source_composition_human_vs_allai.csv`.

##### `## Analysis 2.4: UMAP Embedding Space Visualization`

Baseline-minimal-rephrased rendered result:

- Saved pooled binary proposal-space views:
  - `embedding_space_umap_human_vs_allai.png`.
  - `embedding_space_umap_per_cluster_zoom_human_vs_allai.png`.
- Figure styling follows the shared visualization guide: model/group colors, dark red funded Human markers, and black outlines for top-5 ranked proposals.

##### `## Analysis 2.5: Grid Entropy`

Baseline-minimal-rephrased rendered result:

- Human normalized entropy `0.3304`.
- AI full-pool entropy `0.2950`.
- AI bootstrap mean `0.3640`, `95% CI [0.2148, 0.8289]`.
- Permutation `p=0.7710`; not significant.
- Figure: `diversity_entropy_human_vs_allai.png`.
- Output: `diversity_entropy_human_vs_allai.csv`.

##### `## Part II Diversity Summary Table`

Baseline-minimal-rephrased rendered result:

- **[CRITICAL CHANGE] This permutation-primary summary table (perm p per metric, no MW) is the canonical diversity result to cite in the manuscript. All metrics except Grid Entropy (perm `0.7710`, null) are significant by the valid permutation test.** Summary table rows:
  - Mean Pairwise Distance: Human `0.3411`, AI boot `0.1524`, perm `0.0001`, Cliff's delta `-0.826`.
  - LOO Centroid Distance: Human `0.1953`, AI boot `0.0821`, perm `0.0089`, Cliff's delta `-0.826`.
  - Global Centroid Distance: Human `0.1913`, AI boot `0.0793`, perm `0.0078`, Cliff's delta `-0.696`.
  - MST Mean Edge Weight: Human `0.1004`, AI boot `0.0613`, perm `0.0010`.
  - Sparseness: Human `0.2218`, AI boot `0.0926`, perm `0.0098`, Cliff's delta `-0.699`.
  - Chamfer: Human `0.0751`, AI boot `0.0432`, perm `0.0002`, Cliff's delta `-0.869`.
  - Grid Entropy: Human `0.3304`, AI boot `0.3640`, perm `0.7710`.
- Output: `diversity_summary_human_vs_allai.csv`.

#### `# PART III: NOVELTY`

##### `## Analysis 3.2.5: Element Novelty Percentiles`

Baseline-minimal-rephrased rendered result:

- Human vs All-AI means and Holm-corrected MW results:
  - `element_novel_0`: Human `0.0993`, AI `0.0871`, raw `p=0.2752`, Holm `q=0.2752`, Cliff's delta `-0.153`.
  - `element_novel_1`: Human `0.1687`, AI `0.1469`, raw `p=0.0298`, Holm `q=0.1191`, Cliff's delta `-0.304`.
  - `element_novel_5`: Human `0.1994`, AI `0.1757`, raw `p=0.0364`, Holm `q=0.1191`, Cliff's delta `-0.293`.
  - `element_novel_10`: Human `0.2171`, AI `0.1930`, raw `p=0.0632`, Holm `q=0.1265`, Cliff's delta `-0.260`.
- No ElementNovel metric survives Holm correction in the current all-AI rendered output.
- Output: `novelty_element_percentiles_human_vs_allai.csv`.

##### `## Step 3: Mean kNN Novelty Scores and Local Density`

Baseline-minimal-rephrased rendered result:

- MeanKNN metrics do not survive Holm correction:
  - `mean_knn_5`: Human `0.1094`, AI `0.0945`, raw `p=0.1820`, Holm `q=0.7977`, delta `-0.187`.
  - `mean_knn_10`: Human `0.1151`, AI `0.0990`, raw `p=0.1820`, Holm `q=0.7977`, delta `-0.187`.
  - `mean_knn_20`: Human `0.1211`, AI `0.1041`, raw `p=0.1595`, Holm `q=0.7977`, delta `-0.197`.
  - `mean_knn_50`: Human `0.1299`, AI `0.1117`, raw `p=0.1146`, Holm `q=0.6874`, delta `-0.221`.
- Normalized novelty:
  - `novelty_ratio`: Human `1.2373`, AI `1.2125`, raw/Holm `p=0.8077`, delta `-0.035`.
  - `novelty_z`: Human `0.7323`, AI `0.5469`, raw `p=0.2873`, Holm `q=0.7977`, delta `-0.149`.
- Figure: `novelty_human_vs_allai.png`.
- Output: `novelty_knn_density_human_vs_allai.csv`.

##### `## Step 7B: Literature-Space Outliers`

Baseline-minimal-rephrased rendered result:

- Literature-space outlier prevalence:
  - `is_lit_outlier_mean10`: Human `7/23` (`30.4%`), All AI `3/69` (`4.3%`), Fisher `p=0.00195`, Holm `q=0.00585`.
  - `is_lit_outlier_element0`: Human `6/23` (`26.1%`), All AI `4/69` (`5.8%`), Fisher `p=0.0141`, Holm `q=0.0281`.
  - `is_lit_outlier_z`: Human `5/23` (`21.7%`), All AI `5/69` (`7.2%`), Fisher `p=0.1137`, Holm `q=0.1137`.
- Human proposals are more likely than the pooled AI set to occupy mean-10NN and element0 literature-space outlier positions.
- Output: `literature_space_outliers_human_vs_allai.csv`.

##### `## Analysis 3.5: Literature-Anchored UMAP - BERTopic Embedding Regions`

Baseline-minimal-rephrased rendered result:

- Reused prepare-data literature UMAP/BERTopic artifacts; no refit.
- Loaded cached Section-1 proposal projection: `data/embeddings/literature/proposals_section1_lit_umap2d.npy`.
- BERTopic display-label strategy: `contrastive_phrase_v4`.
- Saved pooled binary literature-space figures:
  - `literature_umap_human_vs_allai.png`.
  - `literature_umap_bertopic_by_group_human_vs_allai.png`.

##### `## Analysis 3.6: BERTopic Region Coverage`

Baseline-minimal-rephrased rendered result:

- Group-level BERTopic region coverage:
  - Human: breadth `4`, Shannon entropy `1.2807`, effective regions `3.5991`, dominant-region fraction `0.4804`.
  - All AI: breadth `3`, Shannon entropy `1.0038`, effective regions `2.7286`, dominant-region fraction `0.6297`.
  - Bootstrap AI breadth: mean `3.521`, `95% CI [2.0, 4.0]`.
- Proposal-level region metrics:
  - `max_region_weight`: Human `0.9000`, AI `0.9355`, raw `p=0.0401`, Holm `q=0.1934`, delta `0.251`.
  - `region_entropy`: Human `0.2587`, AI `0.1469`, raw `p=0.0387`, Holm `q=0.1934`, delta `-0.253`.
  - `effective_region_count`: Human `1.3690`, AI `1.1968`, raw `p=0.0387`, Holm `q=0.1934`, delta `-0.253`.
  - `n_regions_gt5pct`: Human `1.3478`, AI `1.2319`, raw `p=0.4353`, Holm `q=0.8707`.
  - `unassigned_neighbor_frac`: both `0.0`, Holm `q=1.0`.
- Interpretation: pooled AI neighborhoods are somewhat more concentrated, but proposal-level BERTopic metrics do not survive the family-level Holm correction in the saved coverage table.
- Figure: `bertopic_region_coverage_human_vs_allai.png`.
- Outputs: `bertopic_region_coverage_human_vs_allai.csv`, `bertopic_region_coverage_group_human_vs_allai.csv`, `bertopic_region_coverage_per_proposal_human_vs_allai.csv`.

##### `## Analysis 3.7: MeSH Term Coverage`

Baseline-minimal-rephrased rendered result:

- Built MeSH sets from `20` nearest literature neighbors; mean per-proposal MeSH count was `83.8`.
- Per-proposal unique MeSH count:
  - Human mean `80.0`.
  - AI mean `85.09`.
  - MW `p=0.8251`, Cliff's delta `0.0315`.
- Group-level breadth:
  - Human union MeSH `825`.
  - AI full-pool union MeSH `1255`.
  - AI bootstrap union mean `750.5`, `95% CI [625.0, 860.0]`.
- Figure: `mesh_coverage_human_vs_allai.png`.
- Output: `mesh_coverage_human_vs_allai.csv`.

##### `## Analysis 3.8: Publication Year Recency`

Baseline-minimal-rephrased rendered result:

- Within-BERTopic-region literature-neighbor year contrasts:
  - Stratum `0` (`related morbidity, stage diagnosis, combination strategies, clinical intervention`): All AI median `2021.5`, Human median `2021.75`, raw `p=0.1017`, Holm `q=0.2035`, Cliff's delta `-0.403`.
  - Stratum `1` (`details use execution, myosin motors, nascent chain, origin life`): All AI median `2022.0`, Human median `2022.0`, raw `p=0.7659`, Holm `q=0.7659`, Cliff's delta `0.060`.
- No pooled Human-vs-All-AI publication-year contrast is significant after within-region correction.
- Figure: `lit_neighbor_year_by_group_within_bertopic_region_human_vs_allai.png`.
- Output: `lit_neighbor_year_human_vs_allai.csv`.

#### `# PART IV: STYLE`

Baseline-minimal-rephrased rendered result:

- `1/18` style features is significant after Holm correction.
- Significant Holm-corrected feature:
  - `hedge_rate`: Human `0.001200`, AI `0.000114`, MW `p=0.000600`, Holm `q=0.010797`, Cliff's delta `-0.235`.
- Raw but not Holm-significant features include `type_token_ratio` (Human `0.5904`, AI `0.6079`, raw `p=0.0275`, Holm `q=0.4396`) and `dash_per_1k_chars` (raw `p=0.00656`, Holm `q=0.1116`).
- Style-only Human-vs-AI classifier: AUROC `0.518 +/- 0.229`, permutation `p=0.4212`, `18` features.
- Figure: `style_human_vs_allai.png`.
- Outputs: `style_features_human_vs_allai.csv`, `style_only_classifier_human_vs_allai.csv`.

#### `## Finalize AI Heterogeneity Supplementary Table`

Baseline-minimal-rephrased rendered result:

- Final heterogeneity audit remains `0/14` significant outcomes after Holm correction.
- Output: `supplementary_ai_heterogeneity_kruskal_wallis.csv`.

#### `## Unified Summary Export`

Baseline-minimal-rephrased rendered result:

- Final summary table contains `41` rows across `6` domains.
- Raw significant row counts by domain in `proposal_metrics_summary_human_vs_allai.csv`:
  - BERTopic `3`.
  - Diversity `6`.
  - MeSH `0`.
  - Novelty-Element `2`.
  - Novelty-KNN `0`.
  - Style `3`.
- Important correction nuance: these summary-domain counts are based on the row-level `sig` labels in the unified export. The family-specific tables show that ElementNovel, MeanKNN, and BERTopic proposal-level metrics do not survive their Holm corrections in the current all-AI audit; the robust binary findings are proposal-space diversity and two literature-space outlier definitions.
- All outputs saved under `results/tables/rephrased/minimal/all_ai/`.
- All figures saved under `results/figures/rephrased/minimal/all_ai/`.
- Notebook completed successfully.

### Compare_reviews_ncems_criteria.ipynb

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
- Pairwise score tests use Mann-Whitney   and Cliff's delta with BH-FDR correction.
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
5. Also compute Mann-Whitney   and Cliff's delta as secondary effect-size/sensitivity outputs.
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
3. Run Mann-Whitney   and Cliff's delta as secondary sensitivity/effect-size summaries.
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

##### `#### Secondary test — Mann-Whitney   (`u_stat`, `p_value`, `q_value`) — sensitivity check only`

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
4. Use Mann-Whitney  , Cliff's delta, and BH-FDR within metric families.

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

-   significant Kruskal-Wallis test motivates self-preference and fixed-effect analyses because at least one evaluator distribution differs.

##### `## 14) AI self-preference tests (overall + criterion-level + proposal controls)`

What data:

- AI-authored proposals evaluated by AI models.
- `is_self = author == evaluator`.

Step-by-step:

1. Aggregate scores by evaluator, proposal author, and proposal.
2. Compare each evaluator's scores on its own proposals against scores on other AI models' proposals.
3. Repeat for overall score and each NCEMS criterion.
4. Use Mann-Whitney  , Cliff's delta, and BH-FDR.
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

Notebook title: `# Review Score Prediction and Outlier Validation`.

Ground-truth audited notebook: `baseline(minimal)-rephrased/metric_score_relationship.ipynb`.

Purpose: link proposal-level semantic metrics from the baseline-minimal rephrased proposal analysis to prepared AI review score means and prepared Human-Y2 score means, then test how metric-score relationships differ across NCEMS criteria, novelty criteria, and Human-Y2 quantitative scores.

#### `## Condition Configuration`

Step-by-step:

1. Set `CONDITION = 'minimal'`.
2. Load prepared proposal records as the base table.
3. Merge prepared AI review score means, prepared Human-Y2 score means, and unified proposal metrics from `proposal_metrics_master.csv`.
4. Reuse the merged proposal-level dataframe for NCEMS, novelty, and Human-Y2 correlation analyses.

Baseline-minimal rendered result:

- Prepared proposals loaded: `92` from `data/prepared/rephrased/minimal/all_proposals.json`.
- Prepared AI review-score mean rows loaded: `92` from `data/prepared/rephrased/minimal/review_scores_wide.csv`.
- Prepared Human-Y2 score mean rows loaded: `11` from `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`.
- Prepared score tables validated successfully.

#### `## 1. Load Data and Build Unified DataFrame`

Baseline-minimal rendered result:

- Unified proposal metrics merged from `results/tables/rephrased/minimal/proposal_metrics_master.csv`.
- Analysis dataframe shape: `(92, 66)`.
- Groups present: `Human`, `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`.
- Final merged dataframe exported to `results/tables/rephrased/minimal/metric-score/metric_score_df.csv` with `92` rows and `66` columns.

#### `## 1b. Define Metric Families and Score Groups`

Baseline-minimal rendered result:

- Semantic metrics total: `24`.
- New diversity metrics: `14`.
- New novelty metrics: `10`.
- Legacy semantic metrics present: `0`.
- Style metrics present: `0`.
- NCEMS score columns present: `8`.
- Novelty score columns present: `7`.
- Outlier flags present in the merged dataframe: `is_nn_outlier`, `is_mean5nn_outlier`, `is_lit_outlier_mean10`, `is_lit_outlier_element0`, `is_lit_outlier_z`.
- Literature distance metric used: `mean_knn_10`.

Available new diversity metrics:

- `mean_pairwise_dist`, `centroid_dist_raw`, `centroid_dist_loo`, `global_centroid_dist`, `nn_dist_global`, `mean_5nn_dist_global`, `medoid_dist`, `remote_clique_group`, `chamfer_group`, `mst_dispersion_group`, `span90_group`, `sparseness_group`, `grid_entropy_group`, `grid_entropy_group_norm`.

Available new novelty metrics:

- `element_novel_0`, `element_novel_1`, `element_novel_5`, `element_novel_10`, `mean_knn_5`, `mean_knn_10`, `mean_knn_20`, `mean_knn_50`, `novelty_ratio`, `novelty_z`.

#### `## 1c. Score Distribution by Group`

Baseline-minimal rendered result:

- NCEMS `review_score_mean` by group:
  - Human: mean `3.586`, SD `0.465`
  - Claude: mean `4.009`, SD `0.135`
  - Gemini: mean `3.832`, SD `0.069`
  - GPT-5.2: mean `4.317`, SD `0.055`
- Novelty-framework `novelty_score_mean` by group:
  - Human: mean `3.764`, SD `0.266`
  - Claude: mean `3.403`, SD `0.352`
  - Gemini: mean `3.657`, SD `0.301`
  - GPT-5.2: mean `3.993`, SD `0.237`

#### `## 2a. Correlation: Semantic Metrics vs NCEMS Review Scores`

Step-by-step:

1. Compute Spearman correlations between all available semantic metrics and NCEMS score criteria.
2. Build an annotated heatmap marking `p < 0.05`.
3. Print the full semantic-vs-NCEMS correlation matrix.
4. Save correlation and p-value tables under `results/tables/rephrased/minimal/metric-score/`.

Baseline-minimal rendered result:

- Strong negative associations with `relevance_to_emergent_phenomena` dominated the current output:
  - `grid_entropy_group`, `grid_entropy_group_norm`, `sparseness_group`, `span90_group`, `remote_clique_group`, `mst_dispersion_group`, and `chamfer_group`: `r=-0.7220`, `p<0.001`.
  - `nn_dist_global`: `r=-0.5973`, `p<0.001`.
  - `mean_5nn_dist_global`: `r=-0.5958`, `p<0.001`.
  - `mean_pairwise_dist`, `centroid_dist_raw`, and `centroid_dist_loo`: `r=-0.5945`, `p<0.001`.
  - `medoid_dist`: `r=-0.5929`, `p<0.001`.
  - `global_centroid_dist`: `r=-0.5656`, `p<0.001`.
- Overall NCEMS score was also lower for more group-level dispersion under `chamfer_group`: `review_score_mean r=-0.5458`, `p<0.001`.
- The clearest positive NCEMS association was with `data_identification` for the group-dispersion metrics `sparseness_group`, `span90_group`, `remote_clique_group`, and `mst_dispersion_group`: `r=0.5065`, `p<0.001`.
- This replaces the older audited values that reported stronger positive `span90_group` associations with `data_identification`, `rigor_of_approach`, and `open_science_commitment`.

Figure:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_ncems.png`

Tables:

- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_all_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_semantic_all_scores.csv`

#### `## 2b. Correlation: Semantic Metrics vs Novelty Review Scores`

Step-by-step:

1. Compute Spearman correlations between all available semantic metrics and novelty-framework score criteria.
2. Build an annotated heatmap marking `p < 0.05`.
3. Print the full semantic-vs-novelty correlation matrix.

Baseline-minimal rendered result:

- Positive novelty-framework associations are present, but they are moderate rather than the stronger earlier audited values.
- Top positive associations:
  - `sparseness_group`, `span90_group`, `remote_clique_group`, and `mst_dispersion_group` vs `new_theory_concept_method_dataset_or_design`: `r=0.3779`, `p=0.0002`.
  - `mean_pairwise_dist` vs `new_theory_concept_method_dataset_or_design`: `r=0.3646`, `p=0.0004`.
  - `sparseness_group`, `span90_group`, `remote_clique_group`, and `mst_dispersion_group` vs `unique_knowledge_generation`: `r=0.3646`, `p=0.0004`.
  - The same group-dispersion metrics vs `new_question_topic_or_framing`: `r=0.3433`, `p=0.0008`.
  - `centroid_dist_loo` vs `new_theory_concept_method_dataset_or_design`: `r=0.3351`, `p=0.0011`.
  - `centroid_dist_raw` vs `new_theory_concept_method_dataset_or_design`: `r=0.3321`, `p=0.0012`.
- Negative novelty-framework associations were smaller in magnitude:
  - `novelty_z` vs `unique_knowledge_generation`: `r=-0.2987`, `p=0.0038`.
  - `grid_entropy_group` and `grid_entropy_group_norm` vs `unusual_combination_of_existing_ideas`: `r=-0.2605`, `p=0.0121`.
  - `grid_entropy_group` and `grid_entropy_group_norm` vs `credible_high_risk_high_gain`: `r=-0.2561`, `p=0.0138`.
- This replaces the older section that reported `mean_pairwise_dist` / `span90_group` novelty-framework correlations around `r=0.48-0.54`; those are not the current rendered outputs.

Figure:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_novelty.png`

#### `## 2c. Human-Y2 Reviews vs Semantic Metrics`

Step-by-step:

1. Restrict to Human Y2 proposals only.
2. Keep only semantic metrics with within-Y2 proposal variation.
3. Compute Spearman correlations between per-proposal semantic metrics and Human-Y2 quantitative score means.
4. Render semantic and style heatmaps.
5. Compare AI-score correlations on the same Y2 human proposals against Human-Y2 correlations.

Baseline-minimal rendered result:

- Human-Y2 prepared score table used: `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`.
- Y2 human proposals used for Human-Y2 metric-score analysis: `11`.
- Human-Y2 analysis dataframe shape: `(11, 66)`.
- Metrics with per-proposal variation: `17 / 24`.
- Dropped group-level constant metrics: `remote_clique_group`, `chamfer_group`, `mst_dispersion_group`, `span90_group`, `sparseness_group`, `grid_entropy_group`, `grid_entropy_group_norm`.
- Top semantic-vs-Human-Y2 correlations are now trend-level only under the notebook's printed p-values:
  - `novelty_z` vs `open_science_commitment_human_y2`: `r=-0.5968`, `p=0.0526`.
  - `element_novel_0` vs `rigor_of_approach_human_y2`: `r=0.5807`, `p=0.0610`.
  - `element_novel_0` vs `novelty_and_significance_human_y2`: `r=0.5807`, `p=0.0610`.
  - `element_novel_0` vs `relevance_to_emergent_phenomena_human_y2`: `r=0.5807`, `p=0.0610`.
  - `mean_knn_5` vs `relevance_to_emergent_phenomena_human_y2`, `novelty_and_significance_human_y2`, and `rigor_of_approach_human_y2`: `r=0.5623`, `p=0.0718`.
- Style-vs-Human-Y2 table is empty because no style metrics are available in the merged dataframe.
- On the same 11 Y2 human proposals, AI score correlations showed the strongest relationship for `mean_knn_5` vs AI-scored `synthesis_focus`: `r=0.7683`; the AI-minus-Human-Y2 difference table was largest for `mean_knn_5` vs `synthesis_focus`: `diff=0.6032`.
- This replaces the older audited Human-Y2 block that reported significant `nn_dist_global` / `mean_knn_5` negative correlations around `r=-0.81` and `r=-0.77`; those values are not present in the current notebook outputs.

Figures:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_human_y2.png`
- `results/figures/rephrased/minimal/metric-score/corr_style_human_y2.png`
- `results/figures/rephrased/minimal/metric-score/corr_semantic_ai_vs_humany2_on_y2.png`

Tables:

- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_semantic_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_pval_style_human_y2_scores.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_semantic_ai_scores_on_y2_human_proposals.csv`
- `results/tables/rephrased/minimal/metric-score/spearman_corr_diff_semantic_ai_minus_humany2_on_y2.csv`

#### `## 3. Strongest Correlations Summary`

Baseline-minimal rendered result:

- Top NCEMS metric-score pairs were the same `relevance_to_emergent_phenomena` negative block, led by `grid_entropy_group`, `grid_entropy_group_norm`, `sparseness_group`, `span90_group`, `mst_dispersion_group`, `chamfer_group`, and `remote_clique_group` at `r=-0.7220`, `p<0.001`.
- Top novelty-framework metric-score pairs were group-dispersion metrics vs `new_theory_concept_method_dataset_or_design` at `r=0.3779`, followed by group-dispersion metrics vs `unique_knowledge_generation` at `r=0.3646` and vs `new_question_topic_or_framing` at `r=0.3433`.

#### `## 4. Outlier Validation: Do Semantically Unique Proposals Score Higher?`

Baseline-minimal rendered result:

- Missing legacy flag columns were skipped: `is_outlier`, `is_most_novel_raw`, `is_most_novel_z`, `is_most_novel_ratio`, `is_literature_outlier`.
- Available literature outlier flags each marked `10` proposals and left `82` unflagged proposals.
- NCEMS review scores were generally lower, not higher, for flagged literature outliers:
  - `is_lit_outlier_mean10`: `relevance_to_emergent_phenomena` flagged mean `3.8000` vs not flagged `4.7967`, `diff=-0.9967`, `p=0.0002`; `review_score_mean` `3.6700` vs `3.9683`, `diff=-0.2983`, `p=0.0104`.
  - `is_lit_outlier_element0`: `relevance_to_emergent_phenomena` `diff=-0.8846`, `p=0.0025`; `review_score_mean` `diff=-0.2946`, `p=0.0118`.
  - `is_lit_outlier_z`: `review_score_mean` `diff=-0.4404`, `p=0.0016`; `data_identification` `diff=-0.4724`, `p=0.0098`; `open_science_commitment` `diff=-0.7317`, `p=0.0258`.
- Novelty-framework review scores did not show broad outlier advantages:
  - `is_lit_outlier_mean10`: no novelty-framework criterion reached `p<0.05`; `unusual_combination_of_existing_ideas` was near-threshold with `diff=-0.2033`, `p=0.0504`.
  - `is_lit_outlier_element0`: `unique_knowledge_generation` was lower for flagged proposals, `diff=-0.2179`, `p=0.0344`.
  - `is_lit_outlier_z`: `unique_knowledge_generation` was lower for flagged proposals, `diff=-0.2366`, `p=0.0374`.

Figure:

- `results/figures/rephrased/minimal/metric-score/outlier_boxplots.png`

#### `## 5. Scatter Plots: Best Metric-Score Pairs`

Baseline-minimal rendered result:

- The top six metric-score scatter panels used the dominant NCEMS correlations, all `relevance_to_emergent_phenomena` vs group-level dispersion/entropy metrics at `r=-0.7220`.
- Human-Y2 scatter panels were also rendered from the current Human-Y2 trend-level top pairs.

Figures:

- `results/figures/rephrased/minimal/metric-score/top_scatter_metric_score.png`
- `results/figures/rephrased/minimal/metric-score/top_scatter_metric_score_human_y2.png`

#### `## 6. Group-Level Analysis: Human vs AI`

Baseline-minimal rendered result:

- Mean score heatmap by group was rendered and saved.
- Current group means:
  - NCEMS `review_score_mean`: Human `3.586`, Claude `4.009`, Gemini `3.832`, GPT-5.2 `4.317`.
  - NCEMS `novelty_and_significance`: Human `4.101`, Claude `4.333`, Gemini `4.333`, GPT-5.2 `4.362`.
  - Novelty-framework `new_question_topic_or_framing`: Human `3.855`, Claude `3.348`, Gemini `3.594`, GPT-5.2 `3.942`.
  - Novelty-framework `credible_high_risk_high_gain`: Human `3.536`, Claude `3.283`, Gemini `3.652`, GPT-5.2 `3.725`.
  - Novelty-framework `novelty_score_mean`: Human `3.764`, Claude `3.403`, Gemini `3.657`, GPT-5.2 `3.993`.
- AI-vs-Human correlation heatmaps were rendered for NCEMS and novelty-framework scores.

Figures:

- `results/figures/rephrased/minimal/metric-score/group_score_heatmap.png`
- `results/figures/rephrased/minimal/metric-score/corr_ai_vs_human_ncems.png`
- `results/figures/rephrased/minimal/metric-score/corr_ai_vs_human_novelty.png`
- `results/figures/rephrased/minimal/metric-score/corr_diff_ai_human_novelty.png`

#### `## 7. Summary Statistics Table`

Baseline-minimal rendered result:

- The notebook exported the merged metric-score dataframe and all available Spearman correlation tables.
- Final output set is present under `results/tables/rephrased/minimal/metric-score/` and `results/figures/rephrased/minimal/metric-score/`.

Interpretation from the executed baseline-minimal outputs:

- Current metric-score results no longer support the older claim that novelty-framework correlations reach roughly `r=0.5`; the current strongest novelty-framework correlations are moderate, topping out at `r=0.3779`.
- NCEMS relevance remains strongly inversely associated with semantic dispersion/remoteness metrics, suggesting that proposals farther from the common proposal/literature structure are scored as less relevant by NCEMS reviewers.
- Literature-outlier flags do not validate as "higher-scoring novelty" signals in this run; flagged proposals usually score lower on NCEMS and do not gain broad novelty-framework advantages.
- Human-Y2 validation is now weaker and small-sample-limited: the current top Human-Y2 correlations are trend-level (`p>=0.0526`) rather than significant.
- Style-based metric-score interpretation is unavailable in this run because the merged metric-score dataframe contains no style metrics.

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

###  ) Generation-condition analyses not yet executed end-to-end

- Generate and analyze full proposal sets for the non-baseline conditions:
- AI with background literature condition (with fixed retrieval protocol and controlled N).
- AI with human-scientist prior-paper/persona condition.
- Side-by-side statistical comparison of these additional conditions against baseline and Human.

### B) Novelty robustness items not yet completed

- Full preplanned k-sensitivity for novelty inference across `k={5,10,20,50}` with complete inferential tables for each k (beyond current k=10 primary pipeline and targeted diagnostics).

### C) External human-review validation not yet completed

- Blinded external expert evaluation of top Human and AI proposals (planned in Part IV, item (3)).

###  ) Part V planned modeling not yet completed

- Criterion-wise predictive modeling with cross-validated Ridge regressions and permutation-based R² significance (style-only vs semantic-only vs combined feature sets).
- Full planned “human vs AI outlier reward” interaction modeling (group × NN distance slope tests) as originally specified.

## Next Priority Execution Order

1. Complete non-baseline generation conditions and run the same analysis stack for direct condition-level comparison.
2. Run external blinded expert review to validate AI-review-based findings.
3. Finish Part V predictive models and outlier interaction tests to close the validation loop.
4. Pre-register final confirmatory analyses and freeze reporting tables/figures for manuscript drafting.
