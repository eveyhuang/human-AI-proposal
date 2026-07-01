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
| `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`      | Prepared Section-1 / abstract-only proposal embeddings. This is the required proposal representation for all proposal-to-literature comparisons, including novelty distances, literature-space UMAP projection, BERTopic-region coverage, MeSH-neighbor coverage, and literature-neighbor recency | `compare_proposals_rephrased.ipynb`                                                         |
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

- **Representation rule**: any comparison against literature embeddings must use Section-1 / abstract-only proposal embeddings from `proposal_embeddings_section1_only.pkl`. Do not use full-proposal embeddings (`X_prop`) for proposal-to-literature distances, literature-space UMAPs, literature-neighbor tables, MeSH-neighbor coverage, publication-year recency, or BERTopic-region coverage.
- The existing Step 7 novelty visualization in `compare_proposals_rephrased.ipynb` should load `lit_umap_reducer.pkl` and `lit_umap2d.npy`, then project Section-1 / abstract-only proposal embeddings inside the comparison notebook.
- Analysis 3.5 in `compare_proposals_rephrased.ipynb` should load the same literature reducer and project Section-1 / abstract-only proposal embeddings (`proposal_embeddings_section1_only.pkl`) inside the comparison notebook, so literature-space maps use the same proposal representation as proposal-to-literature novelty distances.
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

1. `high_temperature` (**planned next**)

- LLMs use the same minimal idea/proposal prompt pipeline as the baseline condition.
- The only intended generation change is higher sampling temperature: `GENERATION_TEMPERATURE = 0.8` in the rendered proposal-generation notebook.
- Use this condition to test whether increasing model sampling temperature increases diversity and literature-relative novelty of AI-generated ideas/proposals.

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
- Primary comparison: each new condition (`high_temperature`, `how_to_think`, `persona`) vs `baseline(minimal)-rephrased`, then Human vs each condition.

## Completed Analyses and Results

> **Update (July 1, 2026):** compact proposal results below have been refreshed from the rendered `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb` outputs; NCEMS rows reflect the executed baseline/minimal review notebook audit.

> **Representation update (July 2, 2026):** proposal-to-literature analyses have been standardized to use Section-1 / abstract-only proposal embeddings. Literature-relative novelty, literature-space outlier, BERTopic-region coverage, MeSH-neighbor, and literature-neighbor recency numbers below reflect the last audited rendered outputs and should be refreshed by rerunning Part III after this code change.


### Compact Results Table

Stars indicate corrected/primary significance for the model-vs-Human contrast: `*** p<.001`, `** p<.01`, `* p<.05`; blank means not significant. Unless noted, `Δ` is AI model minus Human, so negative values mean Human is higher.

| Analysis | Human reference | Claude vs Human | Gemini vs Human | GPT-5.2 vs Human | Primary test |
| --- | --- | --- | --- | --- | --- |
| Proposal diversity 2.1 pairwise / Remote-Clique family | mean pairwise `0.4429` | `0.0337`; Δ `-0.3670` `***`; δ `-1.000` | `0.1505`; Δ `-0.2838` `***`; δ `-0.826` | `0.3148`; Δ `-0.1546` `**`; δ `-0.478` | MW Holm |
| Proposal diversity 2.2a centroid LOO | centroid LOO `0.2665` | `0.0178`; Δ `-0.2451` `***`; δ `-1.000` | `0.0802`; Δ `-0.1862` `***`; δ `-0.826` | `0.1787`; Δ `-0.0848` `**`; δ `-0.478` | MW Holm |
| Proposal diversity 2.2b global centroid | global-centroid dist `0.2926` | `0.0400`; H-AI `0.2526` `***`; δ `0.887` | `0.0869`; H-AI `0.2057` `***`; δ `0.705` | `0.1704`; H-AI `0.1222` `**`; δ `0.580` | MW Holm |
| Proposal diversity 2.2c MST dispersion | MST `0.1126` | `0.0241`; Δ `-0.0885` `***` | `0.0643`; Δ `-0.0482` `**` | `0.0733`; Δ `-0.0393` `*` | Permutation Holm |
| Proposal diversity 2.2d sparseness | sparseness `0.3721` | `0.0267`; Δ `-0.3454` `***`; δ `-0.915` | `0.0870`; Δ `-0.2810` `***`; δ `-0.765` | `0.2052`; Δ `-0.1656` `***`; δ `-0.595` | MW Holm |
| Proposal diversity 2.3 1-NN / Chamfer | Chamfer `0.0822` | `0.0237`; Δ `-0.0505` `***`; δ `-0.813` | `0.0432`; Δ `-0.0413` `***`; δ `-0.713` | `0.0463`; Δ `-0.0331` `**`; δ `-0.507` | MW Holm |
| Proposal diversity 2.5 grid entropy | normalized entropy `0.4145` | `0.7494`; Δ `+0.3349` `**` | `0.2268`; Δ `-0.1876` | `0.2861`; Δ `-0.1284` | Permutation Holm |
| Proposal novelty ElementNovel-0 | mean `0.0989` | `0.0658`; Δ `-0.0332` `**`; δ `-0.580` | `0.0717`; Δ `-0.0272` `**`; δ `-0.565` | `0.0792`; Δ `-0.0198` `*`; δ `-0.353` | MW Holm |
| Proposal novelty ElementNovel-10 | mean `0.2003` | `0.1620`; Δ `-0.0383` `**`; δ `-0.561` | `0.1700`; Δ `-0.0302` `*`; δ `-0.429` | `0.1828`; Δ `-0.0175`; δ `-0.070` | MW Holm |
| Proposal novelty MeanKNN-10 | mean `0.1109` | `0.0746`; Δ `-0.0363` `**`; δ `-0.573` | `0.0828`; Δ `-0.0281` `*`; δ `-0.482` | `0.0914`; Δ `-0.0195`; δ `-0.202` | MW Holm |
| Proposal novelty normalized `novelty_z` | mean `1.0508` | `0.4966`; Δ `-0.5541` `*`; δ `-0.444` | `0.6700`; Δ `-0.3808`; δ `-0.388` | `0.7937`; Δ `-0.2571`; δ `0.025` | MW Holm |
| Proposal literature-space outliers mean-10NN | Human `5/23` (`21.7%`) | `0/23` (`0.0%`) | `2/23` (`8.7%`) | `3/23` (`13.0%`) | Fisher Holm; no model significant |
| Pairwise-distance bimodality 2.1b | dip `0.142`; best GMM `k=3` | dip `0.014`; `p=0.991`; best `k=1` | dip `0.071`; `p<.001`; best `k=3` | dip `0.167`; `p<.001`; best `k=3` | Dip test + BIC |
| Topic distribution + Ward/GMM clusters | topics T1/T2 `15/14`; Ward A/B `11/12`; GMM clusters `5/11/7` | topics `14/13`; Ward A/B `0/23` `**`; GMM `12/0/11` | topics `7/20`; Ward A/B `2/21` `*`; GMM `3/2/18` | topics `16/13`; Ward A/B `6/17`; GMM `2/6/15` | Topic 4-group perm `p=0.0240`; Ward Fisher Holm; GMM NMI `p=0.0033`, ARI `p=0.0014` |
| LDA topic vs Ward cluster correspondence | ARI `-0.0068`; NMI `0.0006`; lexical topics and embedding clusters are complementary | not model-specific | not model-specific | not model-specific | ARI/NMI descriptive |
| Literature BERTopic region coverage | group entropy `1.1583`; effective regions `3.1845`; dominant frac `0.5217` | entropy `0.0155` `*`; effective `1.0156`; dominant `0.9978` | entropy `0.3790`; effective `1.4608`; dominant `0.9130`; Holm trend `q=0.0793` | entropy `0.8587`; effective `2.3600`; dominant `0.7370` | MW Holm on proposal-level region entropy / max-region weight |
| Literature MeSH coverage | mean unique MeSH `79.57`; union `750` | mean `62.39`; union `197` | mean `57.52`; union `339`; Holm trend `q=0.0748` | mean `68.30`; union `450` | MW Holm; no model significant |
| Within-region literature year 3.8 | medians `2021.5` or `2023.5` by region | no Human contrast significant | no Human contrast significant | stratum-1 median `2024.5` vs Human `2023.5`, ns | MW Holm |
| Style-only source classifier | AUROC `0.561 ± 0.166`; balanced accuracy `0.584 ± 0.117`; permutation `p=0.2977` | not model-specific; no style-adjusted residualization cells rendered | not model-specific; no style-adjusted residualization cells rendered | not model-specific; no style-adjusted residualization cells rendered | 5-fold CV + AUROC permutation |
| NCEMS R1 review diversity | Human review diversity > AI-all; Y2 all metrics `***`; Y1 4/9 metrics `*` | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | per-model within-review diversity not estimable; each model has one review/proposal | Paired Wilcoxon FDR |
| NCEMS R1 Human-AI review similarity, Y1 cosine | Human-Human baseline | Human-AI vs Human-Human δ `-0.042` | Human-AI vs Human-Human δ `0.083` | Human-AI vs Human-Human δ `-0.236` | MW FDR; all model contrasts ns (`q=0.8852`) |
| NCEMS R1 Y1/Y2 within-cohort review similarity | Human-Y1 `0.9583`; Human-Y2 `0.9524` | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | AI model-specific not estimated in four-group Y1/Y2 table | AI-all: Y2 Human vs AI `***`; Y1 trend ns |
| NCEMS R1 Y2 score reliability | Human-Human ICC2k overall `0.4949`; Human-vs-AI ICC2k `0.7805` `*` | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | reliability estimated as AI-all, not model-specific | Spearman/ICC |
| NCEMS quality reviews, raw evaluator pool | Human-all mean `3.5855` | mean `4.0087`; H-AI Δ `-0.4232` `***` | mean `3.8319`; H-AI Δ `-0.2464` `*` | mean `4.3174`; H-AI Δ `-0.7319` `***` | Robust permutation q |
| NCEMS quality reviews, cross-eval only | Human-all mean `3.5855` | mean `4.0739`; δ `-0.652` `***` | mean `3.6761`; δ `0.070` | mean `4.4739`; δ `-0.992` `***` | MW FDR |
| NCEMS R3 self-preference | compares each evaluator's self vs other AI proposals | self `3.8783`, other `3.8870`; δ `-0.053` | self `4.1435`, other `4.5304`; δ `-0.732` `***` | self `4.0043`, other `3.8065`; δ `0.933` `***` | MW FDR |
| Novelty-framework reviews, cross-eval rerun | Human reference from novelty-review notebook | Claude ~ Human; `q=0.8428` | Human > Gemini; δ `0.7788` `***` | GPT > Human; δ `-0.4631` `*` | MW FDR |
| Metric-score relationship (executed baseline-minimal outputs) | semantic-distance metrics are mostly negative with NCEMS and often positive with novelty criteria | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | model-specific score/metric validation not estimated in compact table | Spearman |


## Data Visualization Guide

This guide summarizes the visual conventions used in the audited `baseline(minimal)-rephrased/compare_proposals_rephrased.ipynb` notebook and should be treated as the default style for future condition notebooks unless an analysis requires a specific exception.

### Color Scheme and Metadata Encoding

- Use the shared group palette consistently: Human `#DC143C`, Claude `#4A90E2`, Gemini `#7B68EE`, GPT-5.2 `#3CB371`.
- Use `#808080` only as a fallback for unknown groups. Use a distinct muted aggregate color for combined All-AI views when needed, currently `#B56576`.
- Proposal-level Human funding status should override the generic Human color when individual Human points are plotted: funded Human proposals use dark red `#8B0000`; nonfunded or unknown-funding Human proposals use light coral `#F08080`.
- Top-ranked proposals should be marked with a black outline/ring, using `is_top5_ranked` when available. This applies to both boxplot jitter points and UMAP/scatter proposal markers.
- Outlier overlays should use outline rings rather than replacing the base point color. Proposal-space or within-cluster outliers use magenta outlines; literature-space comparison overlays may use an additional cyan outline when two outlier definitions are shown together.
- Literature-background points in literature-space UMAPs should remain small and semi-transparent so proposal markers and BERTopic region labels remain visually dominant.

### Standard Boxplot Grammar

Use the standardized boxplot helper pattern for all group-comparison distributions.

- Box: standard median line, IQR box, whiskers, and outlier points. Fill each box with the group color at 70% opacity and use black outlines/median lines.
- Jittered scatter: overlay individual observations with random horizontal jitter of approximately `±0.15` units, point size around `20`, and 50% opacity. Use the same group color unless proposal metadata specify funded/nonfunded Human coloring. Add a black ring for top-ranked proposals.
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
- Proposal markers should follow the metadata encoding above: AI groups use the group palette; funded Human uses dark red; nonfunded/unknown Human uses light coral; top-ranked proposals have black outlines.
- Per-cluster UMAP zooms should retain the same marker semantics and use panel titles with cluster names, total `n`, and compact discriminative topic labels when available.
- Literature-region UMAPs should color the fixed literature background by BERTopic embedding-region labels, not LDA lexical topics. LDA-colored maps are supplementary diagnostics only.
- UMAP legends should explicitly explain black outlines, funding colors, outlier rings, and any literature-region colors that are needed to interpret the panel.

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

Purpose: compare Human and AI research proposals after all proposal texts have been rephrased into a standardized neutral academic style. This audit reflects the notebook outputs saved in the `.ipynb` through the final JSON merge cell. The older style-adjusted residualization analyses are not present in the audited notebook and should not be treated as executed results.

Global settings:

- Condition label for results in this section: `baseline-minimal-rephrased`.
- Proposal input: `data/prepared/rephrased/minimal/all_proposals.json`.
- NCEMS review input: `data/prepared/rephrased/minimal/ncems_criteria_all_reviews.csv`.
- Tables: `results/tables/rephrased/minimal`.
- Figures: `results/figures/rephrased/minimal`.
- Full-proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Abstract/Section-1 embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.

#### `## Condition Configuration`

Baseline-minimal-rephrased rendered result:

- `CONDITION = 'minimal'`.
- `REUSE_CACHED_PROPOSAL_EMBEDDINGS = True`.
- `REUSE_CACHED_MAIN_IDEA_EMBEDDINGS = True`.
- `REUSE_CACHED_LITERATURE_EMBEDDINGS = True`.
- The configuration cell has no printed notebook output.

#### `# Setup and Imports`

Baseline-minimal-rephrased rendered result:

- Working directory: `baseline(minimal)-rephrased`.
- Project root: `/Users/eveyhuang/Documents/NICO/human-AI-proposal`.
- PyTorch `2.9.1`; CUDA unavailable.

##### `## Helper Functions`

Baseline-minimal-rephrased rendered result:

- Helper functions loaded, including proposal-level mean pairwise diversity, bootstrap 95% CIs, and Holm multiple-testing adjustment.

##### `## Load Prepared Proposal Data`

Baseline-minimal-rephrased rendered result:

- Loaded proposals from `data/prepared/rephrased/minimal/all_proposals.json`.
- AI proposals: `69`; Human proposals: `23`.
- AI model counts: GPT-5.2 `23`, Gemini `23`, Claude `23`.

##### `## Load Prepared NCEMS Reviews`

Baseline-minimal-rephrased rendered result:

- Loaded `361` NCEMS review rows.
- Unique reviewed proposals: `92`.
- Proposal-level aggregated review rows: `95`.

##### `## Prepare Proposal Texts`

Baseline-minimal-rephrased rendered result:

- Used `standardized_text` with template headers stripped.
- Average cleaned length: AI `1807` characters, Human `1803` characters.

##### `## Load Prepared Full-Proposal Embeddings`

Baseline-minimal-rephrased rendered result:

- Loaded full-proposal embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- AI embeddings shape: `(69, 1024)`.
- Human embeddings shape: `(23, 1024)`.
- Saved `results/tables/rephrased/minimal/proposal_metadata.csv` with `92` rows.

##### `## Shared Distance-Matrix Precomputation`

Baseline-minimal-rephrased rendered result:

- Saved shared caches to `results/tables/rephrased/minimal/cached`.
- `X_prop` shape: `(92, 1024)`; `D_pp` shape: `(92, 92)`.
- Groups: Human `23`, Claude `23`, GPT-5.2 `23`, Gemini `23`, All AI `69`.
- Review ranking coverage: `96.7%`; top-5 outlined proposals: `21.7%`; Human funding coverage: `87.0%`.
- Outputs: `proposal_meta.csv`, `proposal_distance_matrix.npy`, `proposal_pca2d.npy`.

#### `# PART I: THEMATIC AND CLUSTER ANALYSIS`

##### `## Analysis 1.1: Topic Modeling (LDA - Exploratory)`

Baseline-minimal-rephrased rendered result:

- Prepared `92` topic-model texts: Human `23`, AI `69`.
- Document-term matrix: `(92, 192)`; dropped `8` domain unigrams while keeping bigrams.
- Topic-count selection tested `k=2..8`; selected `n_topics=2` by the conservative CV criterion.
- Final LDA: perplexity `228.80`, log-likelihood `-3520.48`.
- Topic labels:
  - Topic 1: `functional data, integrating structural, emergent properties, multi scale` (`46` dominant documents).
  - Topic 2: `protein interaction, decoding emergent, single cell, synthesizing emergent` (`46` dominant documents).
- Stability validation across 10 aligned runs:
  - Topic 1: `60.0% +/- 14.1%` top-10 overlap, cosine `0.813 +/- 0.042`.
  - Topic 2: `47.8% +/- 19.3%` top-10 overlap, cosine `0.784 +/- 0.051`.
- Topic-count sensitivity found Human/AI association significant for `k=3..8`, but not for selected `k=2` (`chi2=0.9275`, `p=0.3355`).
- Outputs: `lda_topic_k_selection.csv`, `lda_topic_contrastive_labels.csv`.

##### `## Analysis 1.2: Topic Distribution and Coverage Per Model`

Baseline-minimal-rephrased rendered result:

- Soft topic participation threshold: `>0.20`.
- Participation counts:
  - Human: Topic_1 `15` (`65%`), Topic_2 `14` (`61%`).
  - Claude: Topic_1 `14` (`61%`), Topic_2 `13` (`57%`).
  - Gemini: Topic_1 `7` (`30%`), Topic_2 `20` (`87%`).
  - GPT-5.2: Topic_1 `16` (`70%`), Topic_2 `13` (`57%`).
- Four-group chi-square `6.1008`, permutation `p=0.0240` (significant).
- Per-topic Fisher tests vs Human: `0/6` significant after Holm correction. Gemini had the strongest unadjusted shifts, Topic_1 `p=0.0377`, `q=0.2261`; Topic_2 `p=0.0909`, `q=0.4547`.
- Topic entropy:
  - Human `H=0.6897`, normalized `0.9950`, covered `2/2`, dominant `Topic_1`.
  - Claude `H=0.6904`, normalized `0.9960`, covered `2/2`, dominant `Topic_1`.
  - Gemini `H=0.6142`, normalized `0.8861`, covered `2/2`, dominant `Topic_2`.
  - GPT-5.2 `H=0.6813`, normalized `0.9829`, covered `2/2`, dominant `Topic_1`.
- Outputs: `topic_distribution_per_model.csv`, `topic_distribution_per_model_tests.csv`, `topic_entropy_per_model.csv`.
- Figure: `topic_distribution_comparison.png`.

##### `## Analysis 1.3: Embedding Cluster Structure and UMAP (Primary Cluster Labels)`

Baseline-minimal-rephrased rendered result:

- Ward agglomerative k-selection:
  - `k=2`: silhouette `0.9055`, Calinski-Harabasz `277.8` (selected).
  - `k=3`: silhouette `0.8127`, Calinski-Harabasz `153.2`.
  - `k=4`: silhouette `0.7681`, Calinski-Harabasz `108.1`.
  - `k=5`: silhouette `0.7698`, Calinski-Harabasz `85.5`.
- Best k: `2`; cluster sizes `[19, 73]`.
- Ward cluster labels:
  - Cluster_A: `19` documents, `mass spectrometry, proteomics imaging, synthesizing emergent`.
  - Cluster_B: `73` documents, `data understand, decoding emergent, integrating structural, multi scale`.
- Optional proposal BERTopic sensitivity produced `2` non-outlier topics with `0.0%` outlier fraction, matching the two Ward regions.
- Cluster membership by group:
  - Human: Cluster_A `11`, Cluster_B `12`.
  - Claude: Cluster_A `0`, Cluster_B `23`.
  - Gemini: Cluster_A `2`, Cluster_B `21`.
  - GPT-5.2: Cluster_A `6`, Cluster_B `17`.
- Fisher tests vs Human:
  - Claude differs for both clusters, `q=0.001216`.
  - Gemini differs for both clusters, `q=0.029426`.
  - GPT-5.2 does not differ after Holm correction, `q=0.442802`.
- Per-group silhouette/dominant-cluster fraction: Human `0.8371`/`52%`, Claude `NaN`/`100%`, Gemini `0.9291`/`91%`, GPT-5.2 `0.9156`/`74%`.
- Cached `proposal_umap2d.npy`.
- Outputs: `ward_cluster_bertopic_style_labels.csv`, `proposal_bertopic_assignments.csv`, `proposal_bertopic_topic_labels.csv`, `diversity_cluster_k_selection.csv`, `diversity_cluster_membership_by_group.csv`.
- Figures: `proposal_ward_clusters_labeled_umap.png`, `proposal_bertopic_topics_labeled_umap.png`, `cluster_membership_umap_per_group.png`.

##### `## Analysis 1.4: Cluster Segregation - GMM Convergent Validity and Per-Model Composition`

Baseline-minimal-rephrased rendered result:

- GMM k-selection over `k=3..8` selected `k=3` by BIC and silhouette.
- GMM cluster sizes: `[22, 19, 51]`.
- Cluster composition:
  - Cluster 0: total `22`, Human `5`, AI `17`, `22.7%` Human, Mixed.
  - Cluster 1: total `19`, Human `11`, AI `8`, `57.9%` Human, Mixed.
  - Cluster 2: total `51`, Human `7`, AI `44`, `13.7%` Human, AI-dominated.
- Segregation metrics:
  - NMI `0.0923`, permutation `p=0.0033`.
  - ARI `0.1411`, permutation `p=0.0014`.
  - Within-human mean distance `0.4429`, within-AI `0.1826`, between Human-AI `0.3880`.
  - Between/within ratio `1.2406`, permutation `p=0.0017`.
- Per-model GMM composition:
  - Human: GMM-0 `5` (`22%`), GMM-1 `11` (`48%`), GMM-2 `7` (`30%`).
  - Claude: GMM-0 `12` (`52%`), GMM-1 `0` (`0%`), GMM-2 `11` (`48%`).
  - Gemini: GMM-0 `3` (`13%`), GMM-1 `2` (`9%`), GMM-2 `18` (`78%`).
  - GPT-5.2: GMM-0 `2` (`9%`), GMM-1 `6` (`26%`), GMM-2 `15` (`65%`).
- GMM k=3 vs Ward k=2 agreement: ARI `0.4976`, NMI `0.6772`; notebook interpretation: high agreement, same latent clusters.
- Outputs: `cluster_gmm_composition_per_model.csv`, `cluster_gmm_vs_ward_agreement.csv`.
- Figures: `cluster_k_selection.png`, `cluster_analysis_visualization.png`, `cluster_composition_per_model.png`.

##### `## Analysis 1.5: LDA Topic-Cluster Correspondence`

Baseline-minimal-rephrased rendered result:

- LDA topics vs Ward clusters: ARI `-0.0068`, NMI `0.0006`.
- Notebook interpretation: low agreement; report LDA lexical structure and embedding-space clusters as complementary axes.
- Contingency table:
  - Topic_1 (`functional data...`): Cluster_A `10`, Cluster_B `36`.
  - Topic_2 (`protein interaction...`): Cluster_A `9`, Cluster_B `37`.
- Decision rule outcome: report both as complementary.
- Outputs: `topic_cluster_contingency.csv`, `topic_cluster_assignment_labels.csv`, `topic_cluster_agreement.csv`.
- Figure: `topic_cluster_correspondence.png`.

##### `### PART I Summary`

Baseline-minimal-rephrased rendered result:

- LDA selected `2` topics; results are exploratory with small-sample/stability limitations.
- Per-model topic distribution differs overall (`perm-p=0.0240`), though per-topic model-vs-Human Fisher tests are not significant after Holm correction.
- Ward clustering finds `2` high-silhouette embedding clusters; Claude is entirely in Cluster_B, Gemini is mostly Cluster_B, and GPT-5.2 spans both clusters more than Claude/Gemini.
- GMM segregation metrics show significant Human/AI semantic-region separation.
- LDA topics and Ward clusters have near-zero agreement, so they should be treated as complementary lexical vs embedding-space structure.

#### `# PART II: DIVERSITY`

##### `## Analysis 2.1: Within-Group Pairwise Diversity (Remote-Clique + proposal-level mean pairwise distance)`

Baseline-minimal-rephrased rendered result:

- Group summary:
  - Human: Remote-Clique `0.4237`, proposal mean-pairwise `0.4429`.
  - Claude: `0.0322`, proposal mean-pairwise `0.0337`.
  - GPT-5.2: `0.3011`, proposal mean-pairwise `0.3148`.
  - Gemini: `0.1439`, proposal mean-pairwise `0.1505`.
  - All AI: `0.1799`, proposal mean-pairwise `0.1826`.
- Pairwise-distance distributions:
  - Human mean `0.4429`, median `0.6984`, SD `0.3182`.
  - Claude mean `0.0337`, median `0.0337`, SD `0.0069`.
  - GPT-5.2 mean `0.3148`, median `0.0447`, SD `0.3301`.
  - Gemini mean `0.1505`, median `0.0348`, SD `0.2613`.
- Inference table was saved as `diversity_pairwise_tests.csv`.
- Outputs: `diversity_remote_clique_group_summary.csv`, `diversity_pairwise_proposal_level.csv`, `diversity_pairwise_tests.csv`.
- Figures: `pairwise_diversity_by_model.png`, `pairwise_diversity_boxplot.png`.

##### `## Analysis 2.1b: Pairwise Distance Bimodality Test`

Baseline-minimal-rephrased rendered result:

- Hartigan dip and GMM BIC:
  - Human: dip `0.1420`, `p=0.00000`, best GMM k `3`.
  - Claude: dip `0.0141`, `p=0.99126`, best GMM k `1`.
  - Gemini: dip `0.0706`, `p=0.00000`, best GMM k `3`.
  - GPT-5.2: dip `0.1673`, `p=0.00000`, best GMM k `3`.
- Interpretation: Claude is unimodal/tightly clustered; Human, Gemini, and GPT-5.2 show multimodal pairwise-distance structure.
- Outputs: `diversity_pairwise_bimodality_tests.csv`, `diversity_pairwise_gmm_summary.csv`.
- Figure: `pairwise_diversity_bimodality_gmm.png`.

##### `## Analysis 2.1c: Cross-Group Topic Space Alignment`

Baseline-minimal-rephrased rendered result:

- Nearest-Human distances:
  - Claude AI-to-Human `0.0325 +/- 0.0057`; Human-to-Claude `0.3595 +/- 0.3420`.
  - Gemini AI-to-Human `0.0419 +/- 0.0341`; Human-to-Gemini `0.0973 +/- 0.0714`.
  - GPT-5.2 AI-to-Human `0.0487 +/- 0.0266`; Human-to-GPT-5.2 `0.0776 +/- 0.0571`.
- AI-to-nearest-Human MW tests after Holm:
  - Claude vs Gemini `q=0.8778`.
  - Claude vs GPT-5.2 `q=0.0795`.
  - Gemini vs GPT-5.2 `q=0.1433`.
- Outputs: `diversity_cross_group_nearest_human.csv`, `diversity_cross_group_alignment_tests.csv`.
- Figure: `cross_group_topic_alignment.png`.

##### `## Analysis 2.1d: Within-Cluster and Between-Cluster Diversity`

Baseline-minimal-rephrased rendered result:

- Within-cluster mean pairwise diversity:
  - Human Cluster_A `n=11`, mean `0.1924`; Human Cluster_B `n=12`, mean `0.0542`.
  - Claude Cluster_A `n=0`; Claude Cluster_B `n=23`, mean `0.0337`.
  - Gemini Cluster_A `n=2`, mean `0.2466`; Gemini Cluster_B `n=21`, mean `0.0334`.
  - GPT-5.2 Cluster_A `n=6`, mean `0.1303`; GPT-5.2 Cluster_B `n=17`, mean `0.0356`.
- Between-cluster gap:
  - Human `0.7417`, Gemini `0.7334`, GPT-5.2 `0.7141`; Claude has no between-cluster gap because all Claude proposals are in Cluster_B.
- Within-cluster tests vs Human:
  - Cluster_A Gemini vs Human `q=0.3929`; GPT-5.2 vs Human `q=0.0002226`.
  - Cluster_B Claude vs Human `q=2.90e-25`; Gemini vs Human `q=1.12e-25`; GPT-5.2 vs Human `q=6.57e-20`.
- Outputs: `diversity_within_cluster_by_group.csv`, `diversity_between_cluster_gap.csv`.
- Figure: `diversity_cluster_aware_comparison.png`.

##### `## Analysis 2.2: Centroid Dispersion Metric (mean radius + Span-90)`

##### `### 2.2a Within-group Centroid Dispersion`

Baseline-minimal-rephrased rendered result:

- Centroid LOO means and Span-90:
  - Human `0.2665`, Span-90 `0.3137`.
  - Claude `0.0178`, Span-90 `0.0214`.
  - GPT-5.2 `0.1787`, Span-90 `0.4673`.
  - Gemini `0.0802`, Span-90 `0.0275`.
  - All AI `0.0968`, Span-90 `0.5841`.
- Human comparison summary:
  - All AI vs Human: mean difference `-0.1720`, delta `-0.7681`, MW Holm `1.18e-08`, permutation Holm `0.0009999`.
  - Claude vs Human: mean difference `-0.2451`, delta `-1.0000`, MW Holm `6.91e-11`, permutation Holm `0.000400`.
  - GPT-5.2 vs Human: mean difference `-0.0848`, delta `-0.4783`, MW Holm `0.00131`, permutation Holm `0.1005`.
  - Gemini vs Human: mean difference `-0.1862`, delta `-0.8261`, MW Holm `5.51e-08`, permutation Holm `0.000400`.
- Outputs: `centroid_distances.csv`, `diversity_span90_group_summary.csv`, `diversity_centroid_pairwise_tests.csv`.
- Figure: `centroid_dispersion_by_model.png`.

##### `### 2.2b: Between-Group Centroid Dispersion`

Baseline-minimal-rephrased rendered result:

- Global-centroid mean distance: Human `0.2926`, Claude `0.0400`, GPT-5.2 `0.1704`, Gemini `0.0869`, All AI `0.0991`.
- Key Human comparisons:
  - Human vs Claude: mean difference `0.2526`, delta `0.8866`, MW Holm `2.46e-06`, permutation Holm `0.0009999`.
  - Human vs GPT-5.2: mean difference `0.1222`, delta `0.5803`, MW Holm `0.00543`, permutation Holm `0.3215`.
  - Human vs Gemini: mean difference `0.2057`, delta `0.7051`, MW Holm `0.000351`, permutation Holm `0.0104`.
  - Human vs All AI: mean difference `0.1935`, delta `0.7240`, MW Holm `2.27e-06`, permutation Holm `0.0009999`.
- Outputs: `between_group_global_centroid_distances.csv`, `between_group_global_centroid_group_summary.csv`, `between_group_global_centroid_pairwise_tests.csv`.
- Figure: `between_group_global_centroid_dispersion.png`.

##### `## Analysis 2.2c: MST Dispersion`

Baseline-minimal-rephrased rendered result:

- MST dispersion: Human `0.1126`, Claude `0.0241`, GPT-5.2 `0.0733`, Gemini `0.0643`, All AI `0.0427`.
- Permutation tests vs Human after Holm:
  - Claude difference `-0.0885`, `q=0.000400`.
  - All AI difference `-0.0699`, `q=0.000400`.
  - Gemini difference `-0.0482`, `q=0.00720`.
  - GPT-5.2 difference `-0.0393`, `q=0.0109`.
- Outputs: `diversity_mst_group_summary.csv`, `diversity_mst_pairwise_permutation.csv`.
- Figure: `diversity_mst_dispersion.png`.

##### `## Analysis 2.2d: Sparseness (Medoid-Based Dispersion)`

Baseline-minimal-rephrased rendered result:

- Sparseness: Human `0.3721`, Claude `0.0267`, GPT-5.2 `0.2052`, Gemini `0.0870`, All AI `0.1098`.
- Pairwise tests vs Human after Holm:
  - Claude mean difference `-0.3454`, delta `-0.9149`, MW Holm `2.98e-09`, permutation Holm `0.000400`.
  - All AI mean difference `-0.2640`, delta `-0.7580`, MW Holm `1.88e-08`, permutation Holm `0.000600`.
  - Gemini mean difference `-0.2810`, delta `-0.7647`, MW Holm `5.42e-07`, permutation Holm `0.000400`.
  - GPT-5.2 mean difference `-0.1656`, delta `-0.5945`, MW Holm `6.42e-05`, permutation Holm `0.0409`.
- Outputs: `diversity_medoid_distances.csv`, `diversity_sparseness_group_summary.csv`, `diversity_sparseness_pairwise_tests.csv`.
- Figure: `diversity_sparseness_medoid.png`.

##### `## Analysis 2.3: Nearest-Neighbor Isolation and Outlier Detection (Chamfer / NN)`

Baseline-minimal-rephrased rendered result:

- Chamfer/mean NN distance: Human `0.0822`, Claude `0.0237`, GPT-5.2 `0.0463`, Gemini `0.0432`, All AI `0.0337`.
- NN tests vs Human:
  - All AI mean difference `-0.0416`, delta `-0.6774`, MW Holm `5.13e-06`, permutation Holm `0.000400`.
  - Claude mean difference `-0.0505`, delta `-0.8129`, MW Holm `7.31e-06`, permutation Holm `0.000400`.
  - GPT-5.2 mean difference `-0.0331`, delta `-0.5066`, MW Holm `0.00335`, permutation Holm `0.0169`.
  - Gemini mean difference `-0.0413`, delta `-0.7127`, MW Holm `7.24e-05`, permutation Holm `0.00780`.
- Within-cluster NN outlier counts were computed:
  - Global outliers `10`; within-cluster outliers `10`.
  - Human: global `7/23`, within-cluster `9/23`.
  - Claude: global `0/23`, within-cluster `1/23`.
  - GPT-5.2: global `2/23`, within-cluster `0/23`.
  - Gemini: global `1/23`, within-cluster `0/23`.
- Global NN outlier threshold: `0.0984`; total global outliers `10/92`.
- Nearest-neighbor source composition:
  - Human: nearest Human `7/23`.
  - Claude: nearest Human `1/23`, same group `19/23`, other AI `3/23`.
  - GPT-5.2: nearest Human `7/23`, same group `11/23`, other AI `5/23`.
  - Gemini: nearest Human `1/23`, same group `13/23`, other AI `9/23`.
  - All AI: nearest Human `9/69`, same group `60/69`.
- Outputs: `nn_distances.csv`, `mean_knn_distances_k5.csv`, `diversity_chamfer_group_summary.csv`, `nearest_neighbor_source_composition.csv`, `diversity_nn_pairwise_tests.csv`.
- Figure: `nearest_neighbor_by_model.png`.

##### `## 2.4 Visualize proposals in Embedding Space V`

Baseline-minimal-rephrased rendered result:

- Loaded cached UMAP from `results/tables/rephrased/minimal/cached/proposal_umap2d.npy`, shape `(92, 2)`.
- Saved `embedding_space_umap_2d.png`.
- The currently rendered notebook did not save a t-SNE output cell for this section, although `embedding_space_tsne.png` exists on disk from prior/generated outputs.

##### `### Analysis 2.4b: Per-Cluster Zoom - UMAP Detail View`

Baseline-minimal-rephrased rendered result:

- Added per-cluster UMAP detail view.
- Figure: `embedding_space_umap_per_cluster_zoom.png`.

##### `## Analysis 2.5: Grid Entropy of Proposal Occupancy`

Baseline-minimal-rephrased rendered result:

- PCA-grid entropy (`5 x 5`):
  - Human entropy `1.3341`, normalized `0.4145`.
  - Claude entropy `2.4122`, normalized `0.7494`.
  - GPT-5.2 entropy `0.9208`, normalized `0.2861`.
  - Gemini entropy `0.7302`, normalized `0.2268`.
  - All AI entropy `1.0686`, normalized `0.3320`.
- Permutation tests vs Human after Holm:
  - Claude difference `0.3349`, `q=0.00840`.
  - Gemini difference `-0.1876`, `q=0.2832`.
  - GPT-5.2 difference `-0.1284`, `q=0.4578`.
  - All AI difference `-0.0825`, `q=0.4734`.
- Outputs: `diversity_entropy_group_summary.csv`, `diversity_entropy_pairwise_permutation.csv`.
- Figure: `diversity_entropy_group_summary.png`.

#### `# PART III: NOVELTY`

##### `## Step 1: Load Prepared Literature Corpus`

Baseline-minimal-rephrased rendered result:

- Loaded `39538` PubMed articles from `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.
- Search queries: `1`.
- Prepared `39538` literature texts with average length `1584` characters.
- Query: `(("emergent properties" OR emergence) AND ("molecular biosciences" OR "cellular biosciences" OR "molecular biology" OR "cell biology"))`.
- Figure: `literature_corpus_overview.png`.

##### `## Step 2: Embed Literature Corpus`

Baseline-minimal-rephrased rendered result:

- Loaded cached literature embeddings from `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Literature embeddings: `39538`.
- Loaded abstract-only proposal embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Abstract-only proposal embeddings: Human `(23, 1024)`, AI `(69, 1024)`.
- Representation rule for all later literature comparisons: stack these Section-1 embeddings as Human rows followed by AI rows to align with `proposal_meta`; use this matrix as `X_prop_lit`.

##### `## Shared Novelty Precomputation (CAREFUL, computationally expensive)`

Baseline-minimal-rephrased rendered result:

- Loaded literature kNN cache for `39538` papers from `results/tables/rephrased/minimal/cached/lit_knn_distances_50.npy`.
- Proposal-to-literature distance matrix `D_pl` shape: `(92, 39538)`.
- Updated implementation: `D_pl` must be computed from Section-1 / abstract-only proposal embeddings (`X_prop_lit @ X_lit.T`), not from full-proposal embeddings (`X_prop @ X_lit.T`).
- Computed reusable literature kNN baselines up to `k=50`.

##### `## Step 2.5: Element Novelty Percentiles`

Baseline-minimal-rephrased rendered result:

- Saved `novelty_element_percentiles.csv` and `novelty_element_percentiles_pairwise_tests.csv`.
- ElementNovel model-vs-Human highlights:
  - `element_novel_0`: Claude difference `-0.0332`, `q=0.00233`; Gemini `-0.0272`, `q=0.00233`; GPT-5.2 `-0.0198`, `q=0.0410`.
  - `element_novel_1`: Claude `-0.0375`, `q=0.00155`; Gemini `-0.0299`, `q=0.0121`; GPT-5.2 not significant, `q=0.7417`.
  - `element_novel_5`: Claude `-0.0376`, `q=0.00273`; Gemini `-0.0300`, `q=0.0230`; GPT-5.2 not significant, `q=0.6925`.
  - `element_novel_10`: Claude `-0.0383`, `q=0.00344`; Gemini `-0.0302`, `q=0.0261`; GPT-5.2 not significant, `q=0.6925`.
- Figure: `novelty_analysis_element_percentiles.png`.

##### `## Step 3: Raw Novelty Scores (Mean k-NN to Literature)`

Baseline-minimal-rephrased rendered result:

- Saved `novelty_mean_knn_scores.csv`, `novelty_mean_knn_pairwise_tests.csv`, `novelty_local_density_normalized.csv`, and `novelty_local_density_pairwise_tests.csv`.
- MeanKNN model-vs-Human highlights:
  - `mean_knn_5`: Claude difference `-0.0357`, `q=0.00319`; Gemini `-0.0285`, `q=0.00390`; GPT-5.2 not significant, `q=0.0950`.
  - `mean_knn_10`: Claude `-0.0363`, `q=0.00273`; Gemini `-0.0281`, `q=0.0105`; GPT-5.2 not significant, `q=0.2443`.
  - `mean_knn_20`: Claude `-0.0371`, `q=0.00112`; Gemini `-0.0280`, `q=0.0191`; GPT-5.2 not significant, `q=0.3677`.
  - `mean_knn_50`: Claude `-0.0377`, `q=0.000944`; Gemini `-0.0284`, `q=0.0333`; GPT-5.2 not significant, `q=0.5241`.
- Normalized novelty:
  - `novelty_ratio`: no model-vs-Human contrast significant after Holm correction.
  - `novelty_z`: Claude lower than Human, difference `-0.5541`, MW Holm `0.0305`, permutation Holm `0.00210`; Gemini is borderline by MW Holm `0.0501` and not significant by permutation Holm; GPT-5.2 not significant.
- Figures: `novelty_analysis_mean_knn.png`, `novelty_analysis_local_density.png`.

##### `## Step 5: Statistical Tests for Novelty Metrics`

Baseline-minimal-rephrased rendered result:

- Saved combined `novelty_all_pairwise_tests.csv`.
- Printed combined ElementNovel, MeanKNN, and normalized-novelty tables. The saved combined table reflects the same model-vs-Human contrasts summarized in Steps 2.5 and 3.

##### `## Step 6: Visualize Novelty Results`

Baseline-minimal-rephrased rendered result:

- Saved novelty visualization figures:
  - `novelty_analysis_element_percentiles.png`
  - `novelty_analysis_mean_knn.png`
  - `novelty_analysis_local_density.png`

##### `## Step 7: Visualize Proposals in Literature Embedding Space`

Baseline-minimal-rephrased rendered result:

- The current notebook cell for the UMAP literature-space view has no saved output in the `.ipynb`.
- The cell code targets `results/figures/rephrased/minimal/proposals_in_literature_space_umap.png`, and that file exists on disk.
- Updated implementation: the view loads the fixed literature UMAP (`lit_umap2d.npy` + `lit_umap_reducer.pkl`) and projects Section-1 / abstract-only proposal embeddings into that map. It should not use full-proposal embeddings or a stale generic `proposals_2d_umap` object.
- The current notebook text says the view fits UMAP on literature only and projects proposals into that space; it does not render the previously documented t-SNE or publication-year literature-space figures in the saved output.
- Refresh status: rerun this cell after rerunning the shared novelty precomputation to regenerate the figure under the Section-1-only representation rule.

##### `### Step 7B: Literature-Space Outliers and High-Novelty Flags`

Baseline-minimal-rephrased rendered result:

- Saved `literature_space_outliers_mean_knn_k10.csv`, `literature_space_outliers_element0.csv`, `literature_space_outliers_z.csv`, and `literature_space_outlier_prevalence_tests.csv`.
- Updated implementation: outlier flags and the outlier-comparison UMAP are based on the same Section-1 / abstract-only proposal-to-literature distances and projection used in Step 7.
- Mean-10NN and ElementNovel-0 outliers:
  - Human `5/23` (`21.7%`).
  - Claude `0/23`, Holm Fisher `p=0.1473`.
  - Gemini `2/23`, Holm `p=0.8280`.
  - GPT-5.2 `3/23`, Holm `p=0.8280`.
- `novelty_z` outliers:
  - Human `6/23` (`26.1%`).
  - Claude `0/23`, Holm `p=0.0647`.
  - Gemini `2/23`, Holm `p=0.4855`.
  - GPT-5.2 `2/23`, Holm `p=0.4855`.
- Figure: `proposals_in_literature_space_umap_outliers_comparison_k10.png`.

##### `## Additional Analysis: Nearest Neighbors in Literature for Every Proposal`

Baseline-minimal-rephrased rendered result:

- Saved `nearest_literature_neighbors_top3.csv`.
- Top mean-10NN proposals included Human `MaiTool - LLM-powered bioinformatics tools for microbiome analysis` (`0.2082`) and Human `Searching the crosslinking mass spectrometry universe for new protein-protein interactions` (`0.1964`).
- Lowest mean-10NN proposals included Claude `Decoding Emergent mRNA Fate Decisions...` (`0.0674`) and Human `Multimodel single-cell frameworks...` (`0.0681`).
- Top ElementNovel-0 proposals included Human `MaiTool...` (`0.1995`), Gemini `Synthesizing the Emergent Assembly of Bacterial Microcompartments` (`0.1782`), and Human `Searching the crosslinking...` (`0.1684`).

##### `## Analysis 3.5: Literature-Anchored UMAP with Embedding-Native Topic Regions`

Baseline-minimal-rephrased rendered result:

- Loaded BERTopic display-label strategy from prepare-data artifacts: `contrastive_phrase_v4`.
- Updated implementation: proposal markers are Section-1 / abstract-only proposal embeddings projected into the fixed literature UMAP. This map should use the same proposal representation as Step 7 and the novelty-distance matrix.
- Saved primary combined literature-region UMAP: `literature_umap_with_bertopic_regions.png`.
- Saved split zoom: `literature_umap_with_bertopic_regions_split_zoom.png`.
- Proposal x split for zoom panes: `6.447`; left pane `n=19`, right pane `n=73`.
- Saved per-author-group panels: `literature_umap_bertopic_by_author_group.png`.
- Analysis completed successfully.

##### `## Analysis 3.6: Literature Embedding-Region Coverage per Author Group`

Baseline-minimal-rephrased rendered result:

- Group-level BERTopic region coverage:
  - Human: breadth `3`, entropy `1.1583`, effective region count `3.1845`, dominant region fraction `0.5217`, unassigned neighbor fraction `0.0`.
  - Claude: breadth `1`, entropy `0.0155`, effective region count `1.0156`, dominant region fraction `0.9978`, unassigned `0.0`.
  - Gemini: breadth `2`, entropy `0.3790`, effective region count `1.4608`, dominant region fraction `0.9130`, unassigned `0.0`.
  - GPT-5.2: breadth `3`, entropy `0.8587`, effective region count `2.3600`, dominant region fraction `0.7370`, unassigned `0.0`.
- MW tests vs Human after Holm:
  - Claude max-region weight higher than Human, `q=0.0150`; Claude region entropy lower, `q=0.0150`.
  - Gemini max-region weight and entropy differ only before Holm, both Holm `q=0.0793`.
  - GPT-5.2 does not differ from Human on max-region weight or entropy after Holm correction.
  - Unassigned neighbor fractions are all `0.0`; tests `q=1.0`.
- Supplementary LDA lexical topic coverage saved to `lit_topic_coverage_*.csv`.
- Outputs: `bertopic_region_coverage_per_group.csv`, `bertopic_region_coverage_per_proposal.csv`, `bertopic_region_coverage_tests.csv`, `lit_topic_coverage_per_group.csv`, `lit_topic_coverage_per_proposal.csv`, `lit_topic_coverage_tests.csv`.
- Figures: `bertopic_region_coverage_stacked_bar.png`, `lit_topic_coverage_stacked_bar.png`.

##### `## Analysis 3.7: MeSH Term Coverage per Author Group`

Baseline-minimal-rephrased rendered result:

- Group MeSH summary:
  - Human: mean unique MeSH `79.57`, median `71.0`, SD `32.42`, group union `750`.
  - Claude: mean `62.39`, median `63.0`, SD `7.89`, group union `197`.
  - Gemini: mean `57.52`, median `53.0`, SD `20.00`, group union `339`.
  - GPT-5.2: mean `68.30`, median `61.0`, SD `29.07`, group union `450`.
- MW tests vs Human after Holm:
  - Claude `q=0.4126`.
  - Gemini `q=0.0748`.
  - GPT-5.2 `q=0.4126`.
- Outputs: `mesh_coverage_per_proposal.csv`, `mesh_coverage_group_summary.csv`, `mesh_coverage_tests.csv`.
- Figure: `mesh_coverage_by_group.png`.

##### `## Analysis 3.8: Publication Year Recency of Nearest Literature (Within Embedding Region)`

Baseline-minimal-rephrased rendered result:

- Within-region MW tests:
  - Stratum `0`, GPT-5.2 vs Human: median year `2021.0` vs `2021.5`, `p=0.1734`, Holm `q=0.5203`.
  - Stratum `1`, Claude vs Human: `2023.5` vs `2023.5`, `p=0.6466`, Holm `q=1.0`.
  - Stratum `1`, Gemini vs Human: `2023.5` vs `2023.5`, `p=0.9547`, Holm `q=1.0`.
  - Stratum `1`, GPT-5.2 vs Human: `2024.5` vs `2023.5`, `p=0.0907`, Holm `q=0.3626`.
- No within-region recency contrast is significant after Holm correction.
- Outputs: `lit_neighbor_year_per_proposal.csv`, `lit_neighbor_year_within_region_tests.csv`, `lit_neighbor_year_region_group_summary.csv`.
- Figure: `lit_neighbor_year_by_group_within_bertopic_region.png`.

##### `## Unified Proposal-Level Metric Export`

Baseline-minimal-rephrased rendered result:

- Master dataframe rows after merges: `92` (expected `92`).
- Merged BERTopic literature-region metrics into `proposal_metrics_master_df`.
- Saved `proposal_metrics_master.csv`.
- `proposal_metrics_master.csv` has `92` rows and `41` columns, including diversity, novelty, outlier, and BERTopic-region metrics.

##### `# PART IV Style Baseline`

##### `### Exract stylistic features`

Baseline-minimal-rephrased rendered result:

- Built style feature table: `92` documents x `18` features.
- Group means:
  - AI average sentence length `18.341`, stopword rate `0.296`, hedge rate `0.0`, FK grade `17.932`.
  - Human average sentence length `18.378`, stopword rate `0.293`, hedge rate `0.0`, FK grade `17.642`.
- Saved `style_features.csv` with `92` rows x `21` columns.

##### `#### Visualization: Style feature distributions by group (Human vs each AI model)`

Baseline-minimal-rephrased rendered result:

- Saved `style_features_by_model_boxplots.png`.
- Summary table was printed by group; the largest visible mean difference was type-token ratio, with Human mean `0.637` vs Claude `0.669`, Gemini `0.672`, GPT-5.2 `0.671`.

##### `### Analysis 2.3.5: Style-only baseline (can style predict source?)`

Baseline-minimal-rephrased rendered result:

- Style-only Human-vs-AI classifier used 18 style features.
- CV AUROC `0.561 +/- 0.166`.
- CV balanced accuracy `0.584 +/- 0.117`.
- Permutation test: observed AUROC `0.561`, null mean `0.504 +/- 0.098`, `p=0.2977`.
- Notebook interpretation: style-only separation is weak; downstream separation is less likely to be purely stylistic.
- Top positive AI-like coefficients: `type_token_ratio` `0.7949`, `comma_per_1k_chars` `0.4151`, `stopword_rate` `0.3746`, `fk_grade_level` `0.2876`.
- Top Human-like coefficients: `n_sents` `-0.5360`, `hedge_rate` `-0.3689`, `flesch_reading_ease` `-0.2968`, `n_words` `-0.2302`.

##### `#### Visualization: Style-only baseline results (CV + permutation test)`

Baseline-minimal-rephrased rendered result:

- Saved `style_only_baseline_viz.png`.

##### Non-rendered style-adjusted analyses previously listed

Baseline-minimal-rephrased rendered result:

- The audited notebook does not contain rendered cells for the previously listed style residualization, style-adjusted centroid dispersion, style-adjusted NN residual embeddings, or style-adjusted 2D UMAP analyses.
- Corresponding figures are not present in `results/figures/rephrased/minimal`: `centroid_dispersion_style_adjusted.png`, `nearest_neighbor_by_model_style_adjusted.png`, and `embedding_space_2d_style_adjusted.png`.
- Those old result claims should not be treated as outputs of the current `compare_proposals_rephrased.ipynb` run.

##### `# Save All Proposals to a Single JSON`

Baseline-minimal-rephrased rendered result:

- Input JSON: `data/prepared/rephrased/minimal/all_proposals.json`.
- Output JSON: `results/tables/rephrased/minimal/all_proposals.json`.
- Master rows: `92`; output records: `92`; records missing a master row: `0`.
- Missing values in diversity family: `0`.
- Missing values in novelty family: `0`.
- Outlier flag alignment with top-10% rule: `1.000` for `is_lit_outlier_mean10`, `is_lit_outlier_element0`, and `is_lit_outlier_z`.

##### Baseline-minimal-rephrased Results Summary

- Human proposals are more semantically spread than AI proposals across pairwise diversity, centroid dispersion, global-centroid distance, MST dispersion, sparseness, and nearest-neighbor isolation.
- Claude is the most concentrated AI model: all Claude proposals fall in Ward Cluster_B, Claude has unimodal pairwise distances, and Claude has sharply lower BERTopic literature-region entropy than Human.
- Gemini is also concentrated relative to Human in embedding clusters and literature-region coverage, though some effects become non-significant after Holm correction.
- GPT-5.2 is closer to Human than Claude/Gemini on several structure and literature-region metrics, but still lower than Human on multiple diversity metrics.
- Topic distribution differs across the four author groups in the current rendered run, but per-topic model-vs-Human Fisher tests are not significant after Holm correction.
- LDA topics and Ward embedding clusters are complementary, not redundant (ARI `-0.0068`, NMI `0.0006`).
- Human proposals are more novel relative to literature than Claude and Gemini on ElementNovel and MeanKNN metrics; GPT-5.2 is often not significant after correction beyond ElementNovel-0.
- Literature-space outlier prevalence is descriptively higher for Human proposals but not significant after Holm correction.
- Style-only classification is weak and non-significant in the current rendered notebook.

##### Diversity Metric Definitions Aligned to Table-3 Naming

Current implementation status for future notebook edits:

1. **Remote-Clique** (`implemented partially`)

- Current Analysis 2.1 computes upper-triangle pairwise cosine distances for descriptions and proposal-level mean distance-to-others for inference.
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

- Project embeddings to 2D, partition into a `5 x 5` grid, compute occupancy frequencies, and report Shannon entropy plus a normalized entropy.
- Keep this distinct from the existing LDA topic entropy in Analysis 1.3.

### Compare_proposals_all_ai.ipynb

#### Notebook Scope and Global Settings

Notebook path: `baseline(minimal)-rephrased/compare_proposals_all_ai.ipynb`.

Purpose: compare Human proposals against the full pooled AI proposal set (Claude + Gemini + GPT-5.2 combined, n=69) using the same analysis families as `compare_proposals_rephrased.ipynb`. All primary comparisons are binary (Human vs All-AI). Per-model breakdowns are produced only as supplementary tables and are never primary figures. The notebook addresses the N-imbalance problem (23 human vs 69 AI proposals) through a bootstrap subsampling strategy that is generated once at the start and reused across all N-sensitive diversity analyses.

Global settings:

- Condition label: `baseline-minimal-rephrased`.
- `CONDITION = 'minimal'`.
- `N_BOOT = 1000` (number of bootstrap subsamples for N-sensitive metrics).
- `BOOT_SEED = 42`.
- `N_HUMAN = 23`; `N_AI_POOL = 69`; `N_SUBSAMPLE = 23` (subsample size matches human N).
- Proposal input: `data/prepared/rephrased/minimal/all_proposals.json`.
- Tables output root: `results/tables/rephrased/minimal/all_ai/`.
- Figures output root: `results/figures/rephrased/minimal/all_ai/`.
- Full-proposal embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`.
- Abstract/Section-1 embedding cache: `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`.
- Literature embedding cache: `data/embeddings/literature/relevant_literature_embeddings.pkl`.
- Literature kNN cache (precomputed in `compare_proposals_rephrased.ipynb`): `results/tables/rephrased/minimal/cached/lit_knn_distances_50.npy`.
- Shared proposal distance matrix (precomputed): `results/tables/rephrased/minimal/cached/proposal_distance_matrix.npy`.
- Shared proposal PCA 2D coords (precomputed): `results/tables/rephrased/minimal/cached/proposal_pca2d.npy`.
- Shared proposal UMAP 2D coords (precomputed): `results/tables/rephrased/minimal/cached/proposal_umap2d.npy`.
- Shared proposal metadata: `results/tables/rephrased/minimal/proposal_metadata.csv`.
- BERTopic model: `data/embeddings/literature/lit_bertopic_model.pkl`.
- Literature BERTopic assignments: `data/prepared/rephrased/minimal/lit_bertopic_assignments.csv`.
- Literature UMAP reducer: `data/embeddings/literature/lit_umap_reducer.pkl`.
- Literature 2D UMAP: `data/embeddings/literature/lit_umap2d.npy`.
- Literature articles: `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.

Embedding-use boundary:

- Use full-proposal embeddings (`X_prop`) for proposal-vs-proposal structure: clustering, proposal-space UMAP, pairwise diversity, centroid/global-centroid dispersion, nearest-neighbor isolation, MST, sparseness, and style/semantic source checks.
- Use Section-1 / abstract-only proposal embeddings (`X_prop_lit`) for every proposal-to-literature analysis: ElementNovel, MeanKNN, normalized novelty, literature-space outlier flags, literature-space UMAPs, BERTopic-region coverage, nearest-literature-neighbor MeSH coverage, and literature-neighbor publication-year recency.

Display colors:

- `Human`: same color as in `compare_proposals_rephrased.ipynb`.
- `All AI`: a single distinct color (e.g., `#E07B39`, a muted orange) used for all pooled-AI points and bars.
- Per-model supplementary figures may reuse the existing per-model palette from `compare_proposals_rephrased.ipynb`.

#### N-Sensitivity Classification and Subsampling Policy

This notebook applies a fixed policy to every analysis, determined by whether the metric's expected value changes as a function of group size N when the underlying distribution is held constant.

**N-sensitive metrics — use bootstrap subsampling for effect size estimates:**
- Mean pairwise distance (partially N-sensitive due to model mixing across 3 AI systems).
- MST dispersion (mean MST edge length decreases monotonically with N).
- Nearest-neighbor / Chamfer distance (min-NN distance decreases monotonically with N).
- Centroid dispersion / global-centroid distance (moderately N-sensitive; centroid precision improves with N).
- Sparseness / medoid-based dispersion (moderately N-sensitive).
- Grid entropy (more proposals fill more cells, pushing entropy upward).
- Group-level union MeSH count (monotone in N by definition; do not compare group-union for 23 vs 69 directly).
- BERTopic group-level breadth / region count (monotone in N; use per-proposal MW tests as primary instead).

**N-insensitive metrics — use Mann-Whitney or permutation test on full groups (23 vs 69) directly:**
- Per-proposal novelty metrics: ElementNovel, MeanKNN, novelty_z (proposal-level, compared via MW).
- Per-proposal MeSH count (proposal-level MW).
- Per-proposal BERTopic region weight / entropy (proposal-level MW).
- Cluster membership proportions (Fisher or chi-square; conditions on group sizes).
- LDA topic participation proportions (chi-square; conditions on group sizes).
- Style features (proposal-level MW).
- Pairwise-similarity tests for categorical outcomes (Fisher, chi-square).

**Significance testing policy for N-sensitive metrics:**
- Use permutation tests on the full 23-vs-69 assignment as the source of p-values. Permutation tests correctly account for group sizes in their null distribution and remain valid with unequal N.
- Use the bootstrap-subsampled estimate (mean over 1000 subsamples of n=23 from the 69 AI pool) as the reported effect size and for the human-vs-AI mean difference.
- Report both the full n=69 AI metric value (in supplementary) and the subsampled n=23 mean ± 95% CI (in the main table).

#### `## Condition Configuration`

Step-by-step:

1. Set `CONDITION = 'minimal'`.
2. Set `N_BOOT = 1000`, `BOOT_SEED = 42`, `N_SUBSAMPLE = 23`.
3. Set `REUSE_CACHED_EMBEDDINGS = True` (load all embedding and distance caches from `compare_proposals_rephrased.ipynb` precomputation; do not recompute).
4. Define output directories `TABLES_DIR = results/tables/rephrased/minimal/all_ai/` and `FIGURES_DIR = results/figures/rephrased/minimal/all_ai/`. Create both if they do not exist.

#### `# Setup and Imports`

Step-by-step:

1. Import standard libraries: `numpy`, `pandas`, `scipy`, `sklearn`, `matplotlib`, `seaborn`, `networkx`, `statsmodels`.
2. Locate project root.
3. Define all input/output paths as constants using `pathlib.Path`.
4. Create output directories.

##### `## Helper Functions`

Copy or import the following helpers from `compare_proposals_rephrased.ipynb`. Do not rewrite from scratch; use identical implementations so results are numerically consistent:

- `cliffs_delta(x, y)`.
- `bootstrap_cliffs_delta_ci(x, y, n_boot, random_state)`.
- `add_mean_ci_to_boxplot(ax, data_list, positions, ...)`.
- `fmt_p(p)` (significance formatter).
- `proposal_mean_pairwise_distance(idx_array, D)` (mean upper-triangle pairwise distance for a group index array and precomputed distance matrix).
- `mst_dispersion(idx_array, D)` (mean MST edge length for a group).
- `sparseness_medoid(idx_array, D)` (mean distance from medoid).
- `chamfer_nn_distance(idx_array, D)` (mean nearest-neighbor distance within a group, excluding self).
- `grid_entropy(coords_2d, grid_size=5)` (Shannon entropy of grid occupancy for a set of 2D points).
- Bootstrap CI helper: `boot_ci(values, alpha=0.05)` returning `(lower, upper)` from a 1D array of bootstrap replicates.
- Holm correction wrapper (or use `statsmodels.stats.multitest.multipletests(..., method='holm')`).

Add one new helper not in the original notebook:

- `bootstrap_group_metric(metric_fn, ai_indices, D_or_coords, n_boot, n_subsample, seed)`: draws `n_boot` subsamples of size `n_subsample` without replacement from `ai_indices`, applies `metric_fn` to each subsample, returns the array of `n_boot` metric values. `metric_fn` signature: `fn(idx_array, D_or_coords) -> float`.

##### `## Load Prepared Proposal Data`

Step-by-step:

1. Load `data/prepared/rephrased/minimal/all_proposals.json` into a list of proposal dicts.
2. Build `proposal_meta` DataFrame from the loaded list (columns: `proposal_uid`, `title`, `group_model`, `group_binary`).
3. Assert counts: `n_human == 23`, `n_ai == 69`, `n_total == 92`.
4. Build index arrays:
   - `human_idx = np.where(proposal_meta['group_binary'] == 'Human')[0]` (shape `(23,)`).
   - `ai_idx = np.where(proposal_meta['group_binary'] == 'AI')[0]` (shape `(69,)`).
   - Per-model index arrays for supplementary heterogeneity test: `claude_idx`, `gemini_idx`, `gpt_idx` (each shape `(23,)`).
5. Print group counts to confirm.

##### `## Load Shared Precomputed Caches`

Step-by-step:

1. Load `results/tables/rephrased/minimal/cached/proposal_distance_matrix.npy` as `D_pp` (shape `(92, 92)`). This is the full inter-proposal cosine-distance matrix used in all diversity calculations.
2. Load `results/tables/rephrased/minimal/cached/proposal_pca2d.npy` as `X_pca2d` (shape `(92, 2)`).
3. Load `results/tables/rephrased/minimal/cached/proposal_umap2d.npy` as `X_umap2d` (shape `(92, 2)`).
4. Load full-proposal embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_human_ai_rephrased.pkl`. Extract `X_prop` (shape `(92, 1024)`), L2-normalized.
5. Load literature kNN distances from `results/tables/rephrased/minimal/cached/lit_knn_distances_50.npy` (shape `(92, 50)`). Also load `results/tables/rephrased/minimal/cached/lit_knn_indices_50.npy` (shape `(92, 50)`) if needed for MeSH analyses.
6. Load abstract-only embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl` (used for novelty step 2).
7. Load literature articles from `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.
8. Load literature BERTopic assignments from `data/prepared/rephrased/minimal/lit_bertopic_assignments.csv`.

Do not recompute any of these. If a cache file does not exist, raise a `FileNotFoundError` with a message directing the user to run `compare_proposals_rephrased.ipynb` first.

##### `## Generate Bootstrap Subsamples (One-Time, Stored for All Analyses)`

**This is the central subsampling cell. It must execute before any N-sensitive analysis. All subsequent N-sensitive analyses reuse `boot_ai_idx_samples`; they do not generate their own samples.**

Step-by-step:

1. Initialize `rng = np.random.default_rng(BOOT_SEED)`.
2. Generate `boot_ai_idx_samples`: a Python list of `N_BOOT` arrays, each of shape `(N_SUBSAMPLE,)`, drawn without replacement from `ai_idx`.
   ```python
   boot_ai_idx_samples = [
       rng.choice(ai_idx, size=N_SUBSAMPLE, replace=False)
       for _ in range(N_BOOT)
   ]
   ```
3. Print confirmation: `f"Generated {N_BOOT} bootstrap subsamples of size {N_SUBSAMPLE} from {len(ai_idx)} AI proposals."`.
4. Save `boot_ai_idx_samples` as a numpy array to `results/tables/rephrased/minimal/all_ai/bootstrap_ai_idx_samples.npy` (shape `(N_BOOT, N_SUBSAMPLE)`) for reproducibility.
5. Compute and print model-composition variance across bootstrap samples: for each of the 1000 subsamples, count how many proposals come from Claude, Gemini, and GPT-5.2. Report mean ± SD of each model count across the 1000 subsamples. Expected: mean ~7.67 from each model, SD captures the sampling variability. This is a diagnostic that confirms random subsampling does not systematically exclude any model.

#### `# PREFLIGHT: AI Model Heterogeneity Tests`

**Purpose:** Before all primary analyses, test whether the three AI models form a statistically homogeneous group on every primary outcome variable. This justifies (or flags concerns about) the pooling approach. Results go to a supplementary table only; they do not appear as primary figures. If Kruskal-Wallis is significant for a metric, the pooled estimate is reported with an explicit note in the methods that within-AI heterogeneity exists.

Step-by-step:

1. Define the set of outcomes to test: all per-proposal numeric metrics available at this point in the notebook, including proposal-level pairwise distance (each proposal's mean distance to others in its group), centroid distance (distance from each proposal to its group centroid), NN distance (distance to nearest neighbor within the group), and any per-proposal novelty metrics loaded from the shared cache if pre-computed. Additional metrics (MeSH count, novelty scores, BERTopic region entropy) are added as they are computed in later cells, and those cells append their Kruskal-Wallis result to the same running heterogeneity table.

2. For each metric with per-proposal values available for Claude (`n=23`), Gemini (`n=23`), GPT-5.2 (`n=23`):
   - Run `scipy.stats.kruskal(*[claude_vals, gemini_vals, gpt_vals])`.
   - Record: `metric`, `H_stat`, `p_value`, `n_claude`, `n_gemini`, `n_gpt`.

3. Apply Holm correction across all K-W tests: `multipletests(p_values, method='holm')`.

4. Save `results/tables/rephrased/minimal/all_ai/supplementary_ai_heterogeneity_kruskal_wallis.csv` with columns: `metric`, `H_stat`, `p_kw`, `p_holm`, `significant_after_holm`.

5. Print summary: how many metrics show significant between-model heterogeneity after Holm correction. Print the sentence that will appear in the paper methods: `"We tested between-model heterogeneity across the three AI systems (Kruskal-Wallis) for all primary outcome variables. X of Y outcomes showed significant between-model heterogeneity after Holm correction (see Supplementary Table S_). We treat the pooled estimate as the average effect across these three frontier AI systems and report per-model breakdowns in Supplementary Table S_."`.

#### `# PART I: THEMATIC AND CLUSTER ANALYSIS`

All Ward cluster labels, BERTopic topic assignments, UMAP coordinates, and GMM labels are loaded from the precomputed caches produced by `compare_proposals_rephrased.ipynb`. No clustering is refit in this notebook.

##### `## Analysis 1.1: Topic Modeling (LDA — Exploratory)`

**Changes from per-model notebook:** The LDA model is already fitted on all 92 documents and does not change. The only change is that the downstream test is a 2-group chi-square (Human vs All-AI) instead of a 4-group test.

Step-by-step:

1. Load `results/tables/rephrased/minimal/lda_topic_contrastive_labels.csv` and the per-proposal dominant-topic assignment from `results/tables/rephrased/minimal/topic_cluster_assignment_labels.csv`.
2. Build a contingency table: rows = `[Human, All_AI]`, columns = `[Topic_1, Topic_2]`.
3. Run `scipy.stats.chi2_contingency` on the 2×2 table and a permutation test (10,000 permutations, permute binary group label, recompute chi2 statistic).
4. Report: chi2 statistic, df=1, p-value (chi-square), permutation p-value.
5. Save `results/tables/rephrased/minimal/all_ai/lda_topic_distribution_human_vs_allai.csv` with columns: `group`, `n_topic1`, `n_topic2`, `pct_topic1`, `pct_topic2`, `chi2`, `p_chi2`, `p_permutation`.
6. Add supplementary table: per-model topic distribution (reuse `topic_distribution_per_model.csv` from the main notebook output directory; do not recompute).

No figure required for this analysis; it is reported as a table only.

##### `## Analysis 1.2: Topic Distribution and Coverage (Binary)`

Step-by-step:

1. For topic soft-participation (threshold `>0.20`): compute counts for Human and All-AI combined.
2. Run 2-group Fisher exact test for each topic (Human vs All-AI).
3. Compute topic entropy for Human (already in `topic_entropy_per_model.csv`) and for All-AI combined (pool all 69 soft-probability vectors, compute group-level distribution).
4. Save `results/tables/rephrased/minimal/all_ai/topic_distribution_human_vs_allai_participation.csv`.
5. No figure required; supplementary table only.

##### `## Analysis 1.3: Cluster Membership (Binary Fisher Test)`

Step-by-step:

1. Load Ward cluster assignments from `results/tables/rephrased/minimal/ward_cluster_bertopic_style_labels.csv`.
2. Build 2×2 contingency: rows = `[Human, All_AI]`, columns = `[Cluster_A, Cluster_B]`.
3. Run Fisher exact test (two-sided). Report odds ratio and 95% CI.
4. Compute per-group cluster composition proportions.
5. Save `results/tables/rephrased/minimal/all_ai/cluster_membership_human_vs_allai.csv` with columns: `group`, `n_cluster_a`, `n_cluster_b`, `pct_cluster_a`, `pct_cluster_b`, `fisher_OR`, `fisher_p`.
6. **Supplementary table:** load `results/tables/rephrased/minimal/diversity_cluster_membership_by_group.csv` (per-model cluster breakdown from main notebook); copy to `results/tables/rephrased/minimal/all_ai/supplementary_cluster_membership_by_model.csv`.

Figure 1.3: One 2-panel figure.
- Panel A: Stacked bar showing Human vs All-AI cluster composition (% Cluster_A and Cluster_B).
- Panel B: UMAP scatter of all 92 proposals, colored by group (Human = group color, All-AI = All-AI color), with Ward cluster boundaries annotated. Load UMAP coords from `X_umap2d`.
- Save `results/figures/rephrased/minimal/all_ai/cluster_membership_human_vs_allai.png`.

##### `## Analysis 1.4: GMM Segregation (Human vs AI Binary)`

**No changes needed.** GMM segregation metrics (NMI, ARI, between/within distance ratio) are natively binary (Human vs AI label). They are not N-sensitive because they measure label-vs-cluster agreement on a fixed embedding space.

Step-by-step:

1. Load GMM cluster assignments from `results/tables/rephrased/minimal/cluster_gmm_composition_per_model.csv` and recompute binary GMM label alignment using `human_idx` and `ai_idx`.
2. Compute NMI and ARI between binary Human/AI label and GMM cluster label for all 92 proposals.
3. Run permutation test (10,000 permutations of the binary group label) for NMI and ARI.
4. Report within-human mean distance, within-AI mean distance, between-Human-AI mean distance, and between/within ratio. Run permutation test for the ratio.
5. Save `results/tables/rephrased/minimal/all_ai/gmm_segregation_human_vs_allai.csv`.

No new figure required; report values in the results table.

##### `## Analysis 1.5: LDA Topic–Cluster Correspondence`

No changes. This analysis is not group-dependent. Load results from `results/tables/rephrased/minimal/topic_cluster_agreement.csv` and copy to `results/tables/rephrased/minimal/all_ai/topic_cluster_agreement.csv` for the all-AI notebook's output directory.

#### `# PART II: DIVERSITY`

**Critical design rule for all Part II analyses:** Every diversity metric that is N-sensitive (see the N-Sensitivity Classification above) must produce three reported values:
1. `human_metric`: the metric computed on the 23 human proposals. No subsampling needed for the human side.
2. `ai_full_metric`: the metric computed on the full 69 AI proposals. Reported in the supplementary table only. Answers "how much space does the collective AI output occupy?"
3. `ai_boot_mean` ± `ai_boot_ci`: the mean ± 95% CI of the metric computed across the 1000 bootstrap subsamples of n=23 from the 69 AI proposals. This is the **primary comparison value**. Answers "how diverse is a typical AI proposal set of the same size as the human set?"

The primary figure for every N-sensitive diversity metric shows human_metric vs ai_boot_mean ± CI. The main results table reports `ai_boot_mean` and its CI as the AI estimate. `ai_full_metric` appears in a footnote or supplementary column.

For significance testing of N-sensitive metrics: run the permutation test on the full 23-vs-69 assignment (permute group labels, recompute the metric difference). The permutation test is valid with unequal N because it correctly models the null distribution for the actual group sizes.

##### `## Analysis 2.1: Within-Group Pairwise Diversity`

N-sensitivity: **partial** (mean pairwise distance is asymptotically N-robust for i.i.d. data, but the pooled AI group is not i.i.d. due to model mixing). Apply bootstrap subsampling as a correction.

Step-by-step:

1. Compute `human_pairwise = proposal_mean_pairwise_distance(human_idx, D_pp)`.
2. Compute `ai_full_pairwise = proposal_mean_pairwise_distance(ai_idx, D_pp)`.
3. Compute `boot_pairwise_vals = bootstrap_group_metric(proposal_mean_pairwise_distance, ai_idx, D_pp, N_BOOT, N_SUBSAMPLE, BOOT_SEED)` using `boot_ai_idx_samples`. Report `ai_boot_mean = np.mean(boot_pairwise_vals)` and `ai_boot_ci = boot_ci(boot_pairwise_vals)`.
4. Permutation test: pool `human_idx` and `ai_idx`, permute binary label 10,000 times, recompute the difference in mean pairwise distance between the two groups.
5. Also compute per-model supplementary values: `claude_pairwise`, `gemini_pairwise`, `gpt_pairwise` (these are already in `diversity_remote_clique_group_summary.csv` from the main notebook; load rather than recompute).
6. **Within-model average** (required for PNAS methods comparison): compute `within_model_avg_pairwise = np.mean([claude_pairwise, gemini_pairwise, gpt_pairwise])`. Report this in the supplementary table alongside `ai_full_pairwise` and `ai_boot_mean`.
7. Save `results/tables/rephrased/minimal/all_ai/diversity_pairwise_human_vs_allai.csv` with columns: `group`, `human_metric`, `ai_full_metric`, `ai_boot_mean`, `ai_boot_ci_lo`, `ai_boot_ci_hi`, `within_model_avg`, `perm_p`.
8. Save per-proposal pairwise values for each proposal (mean distance to all others in its group) for MW test: compute proposal-level mean pairwise distances for human and AI proposals. Run `mannwhitneyu(ai_proposal_pairwise, human_proposal_pairwise, alternative='two-sided')`. Compute Cliff's delta and bootstrap 95% CI. Save `results/tables/rephrased/minimal/all_ai/diversity_pairwise_proposal_level_human_vs_allai.csv`.

Figure 2.1: Two-panel figure.
- Panel A: Side-by-side boxplot with jitter + mean diamond (same style as `pairwise_diversity_boxplot.png` from main notebook but only two groups). Show Human vs All-AI using proposal-level pairwise distances. Add bootstrap-corrected mean ± CI as a separate diamond marker in a distinct style (e.g., hollow diamond) above the standard mean diamond to visually distinguish the full-group mean from the N-corrected mean.
- Panel B: Forest plot showing Cliff's delta for All-AI vs Human with 95% bootstrap CI and MW p-value (Holm if multiple tests exist; otherwise unadjusted).
- Save `results/figures/rephrased/minimal/all_ai/pairwise_diversity_human_vs_allai.png`.

##### `## Analysis 2.1b: Pairwise Distance Bimodality — RESTRUCTURED`

**This analysis is restructured from the per-model notebook because pooled AI bimodality is partially artifactual.**

Step-by-step:

1. Compute the full pairwise distance distribution for the pooled 69 AI proposals (upper triangle of `D_pp[ai_idx,:][:,ai_idx]`).
2. Decompose this distribution into two labeled components:
   - Within-model pairs: pairs where both proposals are from the same model.
   - Between-model pairs: pairs where proposals are from different models.
   Use `claude_idx`, `gemini_idx`, `gpt_idx` to assign each pair a label.
3. Run the Hartigan dip test separately on:
   - Within-model pairs (H0: this distribution is unimodal).
   - Between-model pairs.
   - Full pooled AI distribution.
4. Run the dip test on the human pairwise distance distribution for comparison.
5. Save `results/tables/rephrased/minimal/all_ai/diversity_pairwise_bimodality_decomposed.csv` with columns: `group`, `n_pairs`, `dip_stat`, `p_dip`, `interpretation`.
6. Figure: Three-panel KDE plot showing (a) Human pairwise distances, (b) pooled AI pairwise distances with within-model and between-model sub-distributions overlaid as stacked fills, (c) within-model-only AI pairwise distances. This makes the artifactual contribution of model mixing visible.
7. Save `results/figures/rephrased/minimal/all_ai/pairwise_diversity_bimodality_decomposed.png`.
8. In the results text, explicitly state: "The bimodality observed in the pooled AI pairwise distance distribution reflects the mixture of within-model pairs (tight clusters) and between-model pairs (larger separations); only the within-model distribution is directly comparable to the human distribution."

##### `## Analysis 2.1c: Cross-Group Topic Space Alignment`

N-sensitivity: **not sensitive** (per-AI-proposal distance to its nearest human neighbor is a proposal-level metric). Use MW directly.

Step-by-step:

1. For each AI proposal `i` in `ai_idx`, find its nearest human neighbor: `min(D_pp[i, human_idx])`. Store as `ai_to_nearest_human` (length 69).
2. For each human proposal `j` in `human_idx`, find its nearest AI neighbor: `min(D_pp[j, ai_idx])`. Store as `human_to_nearest_ai` (length 23).
3. Run MW test: `ai_to_nearest_human` vs `human_to_nearest_ai`. Report mean ± SD for each direction, U statistic, p-value, Cliff's delta, 95% CI.
4. Save `results/tables/rephrased/minimal/all_ai/diversity_cross_group_alignment_human_vs_allai.csv`.
5. No new figure required; report as table.

##### `## Analysis 2.1d: Within-Cluster Diversity`

N-sensitivity: **not sensitive within clusters** (cluster membership controls for the embedding-space confound and naturally stratifies proposals into comparable groups).

Step-by-step:

1. Load Ward cluster assignments from `ward_cluster_bertopic_style_labels.csv`.
2. For each cluster (`Cluster_A`, `Cluster_B`):
   - Compute within-cluster mean pairwise distance for human proposals in that cluster.
   - Compute within-cluster mean pairwise distance for AI proposals in that cluster.
   - Run MW test (AI vs Human within cluster). Report U, p-value, Cliff's delta.
3. Note: If a cluster has fewer than 3 proposals in either group, skip the MW test and report `n_too_small`.
4. Save `results/tables/rephrased/minimal/all_ai/diversity_within_cluster_human_vs_allai.csv`.

##### `## Analysis 2.2a: Centroid Dispersion (LOO and Global)`

N-sensitivity: **yes, moderate**. Apply bootstrap subsampling.

Step-by-step:

1. Compute `human_centroid_loo`: for each human proposal, compute its distance to the LOO centroid of the other 22 human proposals. Report mean across proposals.
2. Compute `ai_full_centroid_loo` on the full 69 AI proposals.
3. Compute `boot_centroid_vals` by applying the LOO-centroid metric to each of the 1000 bootstrap subsamples. Report `ai_boot_mean` and `ai_boot_ci`.
4. Compute Span-90 for human and for each bootstrap subsample. Report mean Span-90 across bootstrap iterations.
5. Permutation test on full 23-vs-69 assignment.
6. Report Cliff's delta using proposal-level LOO-centroid distances (per-proposal metric) and MW test (valid with unequal N for proposal-level values).
7. Save `results/tables/rephrased/minimal/all_ai/diversity_centroid_human_vs_allai.csv` with columns: `human_loo_mean`, `ai_full_loo_mean`, `ai_boot_loo_mean`, `ai_boot_loo_ci_lo`, `ai_boot_loo_ci_hi`, `human_span90`, `ai_boot_span90_mean`, `mw_p`, `cliffs_delta`, `perm_p`.

Figure 2.2a: Two-panel figure.
- Panel A: Boxplot of per-proposal LOO-centroid distances for Human vs All-AI (n=69, full), with the bootstrap-corrected mean ± CI shown as a separate annotation.
- Panel B: Forest plot of Cliff's delta + 95% CI, MW p-value.
- Save `results/figures/rephrased/minimal/all_ai/centroid_dispersion_human_vs_allai.png`.

##### `## Analysis 2.2b: Between-Group Global-Centroid Distance`

N-sensitivity: **yes, moderate**. Apply bootstrap subsampling for the AI global-centroid distances.

Step-by-step:

1. Compute global centroid of all 92 proposals: `global_centroid = X_prop.mean(axis=0)`.
2. Per-proposal distance to global centroid: `global_dist = np.array([np.linalg.norm(X_prop[i] - global_centroid) for i in range(92)])`.
3. Human global-centroid distances: `global_dist[human_idx]`. AI full: `global_dist[ai_idx]`.
4. Bootstrap: for each subsample in `boot_ai_idx_samples`, compute mean of `global_dist[subsample]`. Report `ai_boot_mean_global` and `ai_boot_ci_global`.
5. MW test on full per-proposal global distances (human vs AI, 23 vs 69). Cliff's delta.
6. Permutation test.
7. Save `results/tables/rephrased/minimal/all_ai/diversity_global_centroid_human_vs_allai.csv`.

##### `## Analysis 2.2c: MST Dispersion`

N-sensitivity: **yes, strong**. MST edge length decreases monotonically with N. Bootstrap subsampling is required for the primary comparison.

Step-by-step:

1. Compute `human_mst = mst_dispersion(human_idx, D_pp)`.
2. Compute `ai_full_mst = mst_dispersion(ai_idx, D_pp)`.
3. Compute `boot_mst_vals = [mst_dispersion(s, D_pp) for s in boot_ai_idx_samples]`. Report `ai_boot_mst_mean = np.mean(boot_mst_vals)` and `ai_boot_mst_ci = boot_ci(boot_mst_vals)`.
4. Permutation test on full assignment: pool `human_idx` and `ai_idx`, permute the binary label, recompute `human_mst - ai_mst` difference, repeat 10,000 times.
5. The primary reported comparison is `human_mst` vs `ai_boot_mst_mean ± ai_boot_mst_ci`. The full `ai_full_mst` is reported in the supplementary column.
6. Save `results/tables/rephrased/minimal/all_ai/diversity_mst_human_vs_allai.csv`.

Figure 2.2c: Single panel showing Human MST value as a horizontal line with 95% bootstrap CI band (computed by bootstrapping human as well for symmetry), and AI bootstrap distribution as a violin or histogram. Alternatively, show as a two-bar chart with error bars from bootstrap CIs. Save `results/figures/rephrased/minimal/all_ai/diversity_mst_human_vs_allai.png`.

##### `## Analysis 2.2d: Sparseness (Medoid-Based Dispersion)`

N-sensitivity: **yes, moderate**. Apply bootstrap subsampling.

Step-by-step:

1. Compute `human_sparseness = sparseness_medoid(human_idx, D_pp)`.
2. Compute `ai_full_sparseness = sparseness_medoid(ai_idx, D_pp)`.
3. Compute `boot_sparseness_vals` using `boot_ai_idx_samples`. Report `ai_boot_mean` and `ai_boot_ci`.
4. Per-proposal distance to group medoid (proposal-level metric): compute for human and AI proposals. Run MW test. Cliff's delta.
5. Permutation test on full assignment.
6. Save `results/tables/rephrased/minimal/all_ai/diversity_sparseness_human_vs_allai.csv`.

##### `## Analysis 2.3: Nearest-Neighbor Isolation (Chamfer / NN Distance)`

N-sensitivity: **yes, strong**. NN distance decreases monotonically with N. Bootstrap subsampling is required.

Step-by-step:

1. Compute per-proposal within-group NN distance for each human proposal (distance to nearest other human). `human_nn_per_proposal` (length 23).
2. Compute per-proposal within-group NN distance for each AI proposal (distance to nearest other AI within the full 69-pool). `ai_full_nn_per_proposal` (length 69).
3. For bootstrap: for each subsample `s` in `boot_ai_idx_samples`, compute each proposal's within-subsample NN distance. Record the **mean across the 23 proposals** in that subsample. `boot_chamfer_vals` (length 1000). Report `ai_boot_chamfer_mean` and `ai_boot_chamfer_ci`.
4. MW test: `ai_full_nn_per_proposal` vs `human_nn_per_proposal`. Cliff's delta and 95% CI.
5. Permutation test on full assignment.
6. Nearest-neighbor source composition for All-AI (supplementary only): for each AI proposal, determine whether its global nearest neighbor (across all 92 proposals, not just within-group) is Human, same-model AI, or other-model AI. Load from `results/tables/rephrased/minimal/nearest_neighbor_source_composition.csv`; aggregate to Human vs All-AI framing.
7. Save `results/tables/rephrased/minimal/all_ai/diversity_chamfer_human_vs_allai.csv` with both full-n=69 and boot-corrected estimates.
8. Save `results/tables/rephrased/minimal/all_ai/nearest_neighbor_source_composition_human_vs_allai.csv`.

Figure 2.3: Same panel style as Analysis 2.1 (boxplot + jitter + mean diamond). Show Human vs All-AI proposal-level NN distances. Annotate with bootstrap-corrected Chamfer distance mean ± CI. Save `results/figures/rephrased/minimal/all_ai/nearest_neighbor_human_vs_allai.png`.

##### `## Analysis 2.4: UMAP Embedding Space Visualization`

N-sensitivity: **not applicable** (visualization only; uses fixed UMAP coords from cache).

Step-by-step:

1. Load `X_umap2d` from cache.
2. Color each point as Human or All-AI.
3. Add Ward cluster boundary annotations (convex hull or ellipse per cluster).
4. Save `results/figures/rephrased/minimal/all_ai/embedding_space_umap_human_vs_allai.png`.
5. Optional per-cluster zoom: same as Analysis 2.4b in main notebook but colored by binary group.
6. Save `results/figures/rephrased/minimal/all_ai/embedding_space_umap_per_cluster_zoom_human_vs_allai.png`.

##### `## Analysis 2.5: Grid Entropy of Proposal Occupancy`

N-sensitivity: **yes, strong**. More proposals fill more grid cells. Bootstrap subsampling is required.

Step-by-step:

1. Load `X_pca2d` from cache. Use PCA 2D for grid computation (same as main notebook).
2. Compute `human_entropy = grid_entropy(X_pca2d[human_idx], grid_size=5)` and `human_normalized_entropy`.
3. Compute `ai_full_entropy = grid_entropy(X_pca2d[ai_idx], grid_size=5)`.
4. Compute `boot_entropy_vals`: for each subsample `s` in `boot_ai_idx_samples`, compute `grid_entropy(X_pca2d[s], grid_size=5)`. Report `ai_boot_entropy_mean` and `ai_boot_entropy_ci`.
5. Permutation test on full assignment.
6. The primary comparison is `human_entropy` vs `ai_boot_entropy_mean ± ai_boot_entropy_ci`. Report `ai_full_entropy` in supplementary.
7. Save `results/tables/rephrased/minimal/all_ai/diversity_grid_entropy_human_vs_allai.csv`.
8. Figure: Bar chart of human entropy vs AI bootstrap-mean entropy with error bars. Save `results/figures/rephrased/minimal/all_ai/diversity_entropy_human_vs_allai.png`.

##### `## Part II Summary Table`

After all Part II analyses, compile a unified diversity summary table:

Columns: `metric`, `human_value`, `ai_full_n69_value`, `ai_boot_n23_mean`, `ai_boot_n23_ci_lo`, `ai_boot_n23_ci_hi`, `within_model_avg` (where applicable), `perm_p`, `mw_p`, `cliffs_delta`, `cliffs_delta_ci_lo`, `cliffs_delta_ci_hi`.

Save `results/tables/rephrased/minimal/all_ai/diversity_summary_human_vs_allai.csv`.

This table is the primary Table for Part II results in the paper.

#### `# PART III: NOVELTY`

All novelty metrics are proposal-level values compared with Mann-Whitney. They are **not N-sensitive** for validity purposes (MW is valid with 23 vs 69). Cliff's delta and bootstrap 95% CIs are reported alongside all MW tests. No bootstrap subsampling is needed for novelty analyses.

##### `## Steps 1–2: Load Literature Corpus and Embeddings`

Step-by-step:

1. Load literature articles from `data/prepared/rephrased/minimal/literature_corpus_prepared.json`.
2. Load literature kNN distances from `results/tables/rephrased/minimal/cached/lit_knn_distances_50.npy` (shape `(92, 50)`). No recomputation.
3. Load abstract-only proposal embeddings for novelty section from `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`. Extract human and AI abstract embeddings.
4. Stack Human then AI Section-1 embeddings to match `proposal_meta`, L2-normalize as `X_prop_lit`, and use `X_prop_lit` for all proposal-to-literature distances and projections. Do not substitute full-proposal `X_prop` in Part III.

##### `## Analysis 3.2.5 / Step 2.5: Element Novelty Percentiles`

Step-by-step:

1. Load `results/tables/rephrased/minimal/novelty_element_percentiles.csv`. This contains per-proposal ElementNovel scores at various k thresholds.
2. Split into `human_novel` (rows where `group_binary == 'Human'`) and `ai_novel` (rows where `group_binary == 'AI'`, n=69).
3. For each ElementNovel column (`element_novel_0`, `element_novel_1`, `element_novel_5`, `element_novel_10`):
   - Run `mannwhitneyu(ai_vals, human_vals, alternative='two-sided')`.
   - Compute Cliff's delta and bootstrap 95% CI.
4. Apply Holm correction across the 4 tests.
5. Save `results/tables/rephrased/minimal/all_ai/novelty_element_percentiles_human_vs_allai.csv`.
6. Add Kruskal-Wallis heterogeneity test results (Claude vs Gemini vs GPT on each ElementNovel metric) to the running heterogeneity table (`supplementary_ai_heterogeneity_kruskal_wallis.csv`).

##### `## Step 3: Raw Novelty Scores (Mean kNN to Literature)`

Step-by-step:

1. Load `results/tables/rephrased/minimal/novelty_mean_knn_scores.csv`. Contains per-proposal `mean_knn_5`, `mean_knn_10`, `mean_knn_20`, `mean_knn_50`.
2. For each kNN metric: MW test (human n=23 vs AI n=69), Cliff's delta, bootstrap CI.
3. Apply Holm correction across the 4 kNN metrics.
4. Load `results/tables/rephrased/minimal/novelty_local_density_normalized.csv`. Contains `novelty_ratio` and `novelty_z`.
5. MW tests for `novelty_ratio` and `novelty_z`. Holm correction.
6. Save `results/tables/rephrased/minimal/all_ai/novelty_meanknn_human_vs_allai.csv` and `results/tables/rephrased/minimal/all_ai/novelty_normalized_human_vs_allai.csv`.
7. Add K-W heterogeneity tests for all novelty metrics to the running heterogeneity table.

Figure 3: Three-panel figure (ElementNovel-0, MeanKNN-10, novelty_z) using boxplot + jitter + mean diamond style (same as main notebook). Two groups only: Human and All-AI. Save `results/figures/rephrased/minimal/all_ai/novelty_human_vs_allai.png`.

##### `## Step 7B: Literature-Space Outliers`

Step-by-step:

1. Load `results/tables/rephrased/minimal/literature_space_outliers_mean_knn_k10.csv` and `literature_space_outliers_element0.csv` and `literature_space_outliers_z.csv`.
2. For each outlier definition, build a 2×2 contingency table: rows = `[Human, All_AI]`, columns = `[outlier, not_outlier]`.
3. Run Fisher exact test (two-sided). Apply Holm correction across the 3 outlier definitions.
4. Report: Human outlier count/fraction, AI outlier count/fraction, Fisher OR, p-value, Holm q.
5. Save `results/tables/rephrased/minimal/all_ai/literature_space_outliers_human_vs_allai.csv`.

##### `## Analysis 3.5: Literature-Anchored UMAP`

Step-by-step:

1. Load `data/embeddings/literature/lit_umap_reducer.pkl` and `data/embeddings/literature/lit_umap2d.npy`.
2. Load abstract/Section-1 proposal embeddings from `data/embeddings/rephrased/minimal/proposal_embeddings_section1_only.pkl`, stack Human then AI rows to match `proposal_meta`, L2-normalize, and project all 92 proposals into the literature UMAP space using `lit_umap_reducer.transform(X_prop_lit)`.
3. Load `data/prepared/rephrased/minimal/lit_bertopic_assignments.csv` for region labels.
4. Plot: all 39538 literature articles in gray; Human proposals in human color; All-AI proposals in all-AI color. Annotate BERTopic region labels.
5. Save `results/figures/rephrased/minimal/all_ai/literature_umap_human_vs_allai.png`.
6. Also save a per-group panel version (two panels side-by-side: human proposals, AI proposals) for direct visual comparison. Save `results/figures/rephrased/minimal/all_ai/literature_umap_human_vs_allai_split.png`.

##### `## Analysis 3.6: Literature Embedding-Region Coverage`

N-sensitivity: **mixed**.
- Per-proposal region entropy and max-region weight are proposal-level metrics → MW test, no subsampling needed.
- Group-level breadth (number of distinct regions covered by the group) is N-sensitive → **use bootstrap subsampling for group-breadth comparison**.
- Group-level region entropy (entropy of the group-level region distribution) is N-sensitive → **use bootstrap subsampling**.

Step-by-step:

1. Load `results/tables/rephrased/minimal/bertopic_region_coverage_per_proposal.csv`. Contains per-proposal `dominant_region`, `max_region_weight`, `region_entropy`, `effective_region_count`.
2. Primary proposal-level tests (MW, no subsampling):
   - `max_region_weight`: MW (AI vs Human). Cliff's delta. Holm with other region metrics.
   - `region_entropy`: MW (AI vs Human). Cliff's delta.
   - `effective_region_count`: MW (AI vs Human). Cliff's delta.
3. Group-level breadth test (with bootstrap):
   - For human: `human_breadth = len(set(proposal_meta.loc[human_idx, 'dominant_region']))`.
   - For full AI: `ai_full_breadth = len(set(proposal_meta.loc[ai_idx, 'dominant_region']))`.
   - For bootstrap: for each subsample `s` in `boot_ai_idx_samples`, compute `breadth_s = len(set(proposal_meta.loc[s, 'dominant_region']))`. Report `ai_boot_breadth_mean` and `ai_boot_breadth_ci`. Note: breadth values are integers, so CI is over a discrete distribution.
   - **Do not compare `ai_full_breadth` to `human_breadth` as the primary test.** Report it in supplementary only.
4. Group-level region-distribution entropy (with bootstrap):
   - Compute the distribution of proposals across BERTopic regions for all 69 AI proposals, compute Shannon entropy.
   - For bootstrap: for each subsample, compute region-distribution entropy. Report mean ± CI.
5. Add K-W heterogeneity tests for `max_region_weight` and `region_entropy` to the running heterogeneity table.
6. Save `results/tables/rephrased/minimal/all_ai/bertopic_region_coverage_human_vs_allai.csv` and `results/tables/rephrased/minimal/all_ai/bertopic_region_breadth_human_vs_allai.csv`.

Figure 3.6: Stacked bar chart showing Human and All-AI region composition (proportion of proposals in each BERTopic region), plus a forest plot of MW effect sizes for proposal-level region metrics. Save `results/figures/rephrased/minimal/all_ai/bertopic_region_coverage_human_vs_allai.png`.

##### `## Analysis 3.7: MeSH Term Coverage`

N-sensitivity: **mixed**.
- Per-proposal unique MeSH count is proposal-level → MW test, no subsampling needed.
- Group-level union MeSH count is N-sensitive (monotone in N) → **use bootstrap subsampling; do not compare group-union MeSH for n=23 vs n=69 directly**.

Step-by-step:

1. Load or recompute per-proposal unique MeSH counts (using `K_MESH = 20` nearest literature neighbors, same as main notebook). Load `results/tables/rephrased/minimal/mesh_coverage_per_proposal.csv` if it exists and contains the per-proposal `unique_mesh_count`.
2. Primary test (no subsampling): MW test on `unique_mesh_count` for human (n=23) vs AI (n=69). Cliff's delta and bootstrap 95% CI.
3. Group-level union MeSH (with bootstrap):
   - `human_union_mesh = len(union of all MeSH sets for human proposals)`.
   - `ai_full_union_mesh = len(union of all MeSH sets for all 69 AI proposals)`.
   - For bootstrap: for each subsample `s` in `boot_ai_idx_samples`, compute `union_mesh_s`. Report `ai_boot_union_mesh_mean` and `ai_boot_union_mesh_ci`.
   - **The primary union-MeSH comparison is human vs `ai_boot_union_mesh_mean ± CI`.** Report `ai_full_union_mesh` in a supplementary column with the note that it reflects n=69 vs n=23.
4. Add K-W heterogeneity test for `unique_mesh_count` to the running heterogeneity table.
5. Save `results/tables/rephrased/minimal/all_ai/mesh_coverage_human_vs_allai.csv` with columns: `human_mean_unique_mesh`, `human_union_mesh`, `ai_full_mean_unique_mesh`, `ai_full_union_mesh`, `ai_boot_mean_unique_mesh`, `ai_boot_union_mesh_mean`, `ai_boot_union_mesh_ci_lo`, `ai_boot_union_mesh_ci_hi`, `mw_p`, `mw_p_holm`, `cliffs_delta`, `cliffs_delta_ci_lo`, `cliffs_delta_ci_hi`.

Figure 3.7: Two-panel figure.
- Panel A: Boxplot of per-proposal unique MeSH count for Human vs All-AI (n=69 shown, bootstrap-corrected mean annotated).
- Panel B: Bar chart of group-union MeSH count: one bar for Human (n=23), one bar for All-AI bootstrap mean (n=23 equivalent) with 95% CI error bar, and a supplementary marker or footnote showing the n=69 full-pool value.
- Save `results/figures/rephrased/minimal/all_ai/mesh_coverage_human_vs_allai.png`.

##### `## Analysis 3.8: Publication Year Recency`

No changes from main notebook logic. Load `results/tables/rephrased/minimal/lit_neighbor_year_per_proposal.csv` and run MW tests for Human vs All-AI within each BERTopic stratum. No subsampling needed (per-proposal metric). Save `results/tables/rephrased/minimal/all_ai/lit_neighbor_year_human_vs_allai.csv`.

#### `# PART IV: STYLE`

All style analyses use per-proposal features compared with MW. No subsampling needed.

Step-by-step:

1. Load `results/tables/rephrased/minimal/style_features.csv` (already computed in main notebook).
2. For each of the 18 style features: MW test (human n=23 vs AI n=69), Cliff's delta.
3. Apply Holm correction across the 18 features.
4. Save `results/tables/rephrased/minimal/all_ai/style_features_human_vs_allai.csv`.
5. Re-run style-only Human-vs-AI classifier (LogisticRegression with L2 penalty, 5-fold stratified CV) using binary Human/AI label. Report AUROC, balanced accuracy, and permutation p-value.
6. **Note on class imbalance:** with 23 human vs 69 AI, the classifier is imbalanced. Use `class_weight='balanced'` in LogisticRegression and `StratifiedKFold` for CV. Report both macro-average and per-class precision/recall.
7. Save `results/tables/rephrased/minimal/all_ai/style_only_classifier_human_vs_allai.csv`.
8. Figure: two-panel figure — (a) per-feature effect sizes with Cliff's delta forest plot, (b) CV AUROC distribution across folds. Save `results/figures/rephrased/minimal/all_ai/style_human_vs_allai.png`.

#### `## Finalize Heterogeneity Table`

After all analyses have appended their Kruskal-Wallis results to the running heterogeneity table:

1. Apply Holm correction across all K-W tests in the table.
2. Save the final `results/tables/rephrased/minimal/all_ai/supplementary_ai_heterogeneity_kruskal_wallis.csv`.
3. Print the summary sentence for the methods section.

#### `## Unified Summary Export`

Step-by-step:

1. Compile the unified diversity + novelty summary table from all Part II and Part III outputs.
2. Save `results/tables/rephrased/minimal/all_ai/proposal_metrics_summary_human_vs_allai.csv` with one row per metric, containing human value, full AI value, bootstrap-corrected AI value (where applicable), CI bounds, permutation p-value, MW p-value, Holm-corrected q, Cliff's delta, and delta CI.
3. This table is intended to be the single source for the main paper results table comparing Human vs All-AI.

#### Output File Inventory

Tables (`results/tables/rephrased/minimal/all_ai/`):

- `bootstrap_ai_idx_samples.npy`
- `supplementary_ai_heterogeneity_kruskal_wallis.csv`
- `lda_topic_distribution_human_vs_allai.csv`
- `topic_distribution_human_vs_allai_participation.csv`
- `cluster_membership_human_vs_allai.csv`
- `supplementary_cluster_membership_by_model.csv`
- `gmm_segregation_human_vs_allai.csv`
- `topic_cluster_agreement.csv`
- `diversity_pairwise_human_vs_allai.csv`
- `diversity_pairwise_proposal_level_human_vs_allai.csv`
- `diversity_pairwise_bimodality_decomposed.csv`
- `diversity_cross_group_alignment_human_vs_allai.csv`
- `diversity_within_cluster_human_vs_allai.csv`
- `diversity_centroid_human_vs_allai.csv`
- `diversity_global_centroid_human_vs_allai.csv`
- `diversity_mst_human_vs_allai.csv`
- `diversity_sparseness_human_vs_allai.csv`
- `diversity_chamfer_human_vs_allai.csv`
- `nearest_neighbor_source_composition_human_vs_allai.csv`
- `diversity_grid_entropy_human_vs_allai.csv`
- `diversity_summary_human_vs_allai.csv`
- `novelty_element_percentiles_human_vs_allai.csv`
- `novelty_meanknn_human_vs_allai.csv`
- `novelty_normalized_human_vs_allai.csv`
- `literature_space_outliers_human_vs_allai.csv`
- `bertopic_region_coverage_human_vs_allai.csv`
- `bertopic_region_breadth_human_vs_allai.csv`
- `mesh_coverage_human_vs_allai.csv`
- `lit_neighbor_year_human_vs_allai.csv`
- `style_features_human_vs_allai.csv`
- `style_only_classifier_human_vs_allai.csv`
- `proposal_metrics_summary_human_vs_allai.csv`

Figures (`results/figures/rephrased/minimal/all_ai/`):

- `cluster_membership_human_vs_allai.png`
- `embedding_space_umap_human_vs_allai.png`
- `embedding_space_umap_per_cluster_zoom_human_vs_allai.png`
- `pairwise_diversity_human_vs_allai.png`
- `pairwise_diversity_bimodality_decomposed.png`
- `centroid_dispersion_human_vs_allai.png`
- `diversity_mst_human_vs_allai.png`
- `nearest_neighbor_human_vs_allai.png`
- `diversity_entropy_human_vs_allai.png`
- `novelty_human_vs_allai.png`
- `literature_umap_human_vs_allai.png`
- `literature_umap_human_vs_allai_split.png`
- `bertopic_region_coverage_human_vs_allai.png`
- `mesh_coverage_human_vs_allai.png`
- `style_human_vs_allai.png`

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

Baseline-minimal result:

- Prepared proposals loaded: `92`.
- Prepared AI review-score mean rows loaded: `92`.
- Prepared Human-Y2 score mean rows loaded: `11`.

#### `## 0. Load Prepared Review Score Tables (No Re-Aggregation)`

Step-by-step:

1. Load `data/prepared/rephrased/minimal/review_scores_wide.csv`.
2. Load `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`.
3. Validate that prepared score-table columns required for downstream analyses are present.

Baseline-minimal result:

- Loaded proposals from `data/prepared/rephrased/minimal/all_proposals.json`.
- Loaded AI review score means from `data/prepared/rephrased/minimal/review_scores_wide.csv` (`92` rows).
- Loaded Human-Y2 score means from `data/prepared/rephrased/minimal/human_y2_scores_wide.csv` (`11` rows).
- Prepared score tables validated successfully.

#### `## 1. Load Data and Build Unified DataFrame`

Step-by-step:

1. Flatten prepared proposal records into a proposal-level dataframe.
2. Merge prepared AI score means by normalized title key.
3. Merge prepared Human-Y2 score means by normalized title key.
4. Prefer unified proposal metrics from `results/tables/rephrased/minimal/proposal_metrics_master.csv` when present.
5. Keep proposal metadata, score columns, semantic metrics, and outlier flags in one merged table.

Baseline-minimal result:

- Unified proposal metrics merged from `results/tables/rephrased/minimal/proposal_metrics_master.csv`.
- Analysis dataframe shape: `(92, 59)`.
- Groups present: `Human`, `claude-opus-4-5`, `gemini-3-pro-preview`, `gpt-5.2`.

#### `## 1b. Define Metric Families and Score Groups`

Step-by-step:

1. Build semantic metric families from the available diversity and novelty metrics.
2. Detect whether any legacy semantic metrics remain available.
3. Detect available style metrics.
4. Define NCEMS score columns, novelty-framework score columns, and outlier flags.
5. Choose the literature-distance metric fallback used in downstream summaries.

Baseline-minimal result:

- Semantic metrics total: `24`.
- New diversity metrics: `14`.
- New novelty metrics: `10`.
- Legacy semantic metrics present: `0`.
- Style metrics present: `0`.
- NCEMS score columns present: `8`.
- Novelty score columns present: `7`.
- Outlier flags present: `3/8`.
- Literature distance metric used: `mean_knn_10`.

#### `## 1c. Score Distribution by Group`

Step-by-step:

1. Summarize proposal-level NCEMS overall means by group.
2. Summarize proposal-level novelty-framework overall means by group.

Baseline-minimal result:

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

Baseline-minimal result:

- Strong negative associations with `relevance_to_emergent_phenomena` dominated the printed matrix:
  - `remote_clique_group`, `chamfer_group`, `mst_dispersion_group`, and `sparseness_group`: `r=-0.722`
  - `mean_5nn_dist_global`: `r=-0.574`
  - `global_centroid_dist`: `r=-0.552`
- `novelty_and_significance` was also generally negative for semantic-distance metrics:
  - `nn_dist_global`: `r=-0.498`
  - `mean_5nn_dist_global`: `r=-0.485`
  - `global_centroid_dist`: `r=-0.457`
- Some metrics were positively associated with feasibility/data-oriented NCEMS criteria:
  - `span90_group` vs `data_identification`: `r=0.566`
  - `span90_group` vs `rigor_of_approach`: `r=0.504`
  - `span90_group` vs `open_science_commitment`: `r=0.472`

Figure:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_ncems.png`

#### `## 2b. Correlation: Semantic Metrics vs Novelty Review Scores`

Step-by-step:

1. Compute Spearman correlations between all available semantic metrics and novelty-framework score criteria.
2. Build an annotated heatmap marking `p < 0.05`.
3. Print the full semantic-vs-novelty correlation matrix.

Baseline-minimal result:

- Positive associations were common for novelty-oriented criteria:
  - `mean_pairwise_dist` vs `new_question_topic_or_framing`: `r=0.481`
  - `mean_pairwise_dist` vs `new_theory_concept_method_dataset_or_design`: `r=0.536`
  - `centroid_dist_loo` vs `new_theory_concept_method_dataset_or_design`: `r=0.506`
- `span90_group` showed the strongest repeated positive pattern in the printed matrix:
  - `new_question_topic_or_framing`: `r=0.511`
  - `new_theory_concept_method_dataset_or_design`: `r=0.536`
  - `unusual_combination_of_existing_ideas`: `r=0.510`
  - `beyond_state_of_the_art`: `r=0.532`
- Literature-relative novelty metrics were positively associated with novelty-theory criteria:
  - `element_novel_1` vs `new_theory_concept_method_dataset_or_design`: `r=0.411`
  - `element_novel_5` vs `new_theory_concept_method_dataset_or_design`: `r=0.407`
  - `mean_knn_50` vs `new_theory_concept_method_dataset_or_design`: `r=0.391`
- Grid-entropy metrics were negative for several novelty criteria in the printed matrix, for example `grid_entropy_group` vs `unusual_combination_of_existing_ideas`: `r=-0.308`.

Figure:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_novelty.png`

#### `## 2c. Human-Y2 Reviews vs Semantic Metrics`

Step-by-step:

1. Restrict to Human Y2 proposals only.
2. Keep only semantic metrics with within-Y2 proposal variation.
3. Compute Spearman correlations between per-proposal semantic metrics and Human-Y2 quantitative score means.
4. Render semantic and style heatmaps.
5. Print the top semantic-vs-Human-Y2 correlation table that was produced before notebook execution stopped.

Baseline-minimal result:

- Human-Y2 prepared score table used: `data/prepared/rephrased/minimal/human_y2_scores_wide.csv`.
- Y2 human proposals used for Human-Y2 metric-score analysis: `11`.
- Human-Y2 analysis dataframe shape: `(11, 59)`.
- Metrics with per-proposal variation: `17 / 24`.
- Dropped group-level constant metrics:
  - `remote_clique_group`
  - `chamfer_group`
  - `mst_dispersion_group`
  - `span90_group`
  - `sparseness_group`
  - `grid_entropy_group`
  - `grid_entropy_group_norm`
- Top printed semantic-vs-Human-Y2 correlations:
  - `nn_dist_global` vs `data_identification_human_y2`: `r=-0.8074`, `p=0.0027`
  - `nn_dist_global` vs `synthesis_focus_human_y2`: `r=-0.8074`, `p=0.0027`
  - `mean_knn_5` vs `data_identification_human_y2`: `r=-0.7707`, `p=0.0055`
  - `mean_knn_5` vs `synthesis_focus_human_y2`: `r=-0.7707`, `p=0.0055`
  - `mean_5nn_dist_global` vs `data_identification_human_y2`: `r=-0.7615`, `p=0.0065`
  - `element_novel_0` vs `data_identification_human_y2`: `r=-0.7615`, `p=0.0065`
  - `element_novel_0` vs `synthesis_focus_human_y2`: `r=-0.7615`, `p=0.0065`
  - `mean_pairwise_dist` vs `scope_and_timeline_human_y2`: `r=0.6713`, `p=0.0237`
  - `centroid_dist_raw` vs `scope_and_timeline_human_y2`: `r=0.6713`, `p=0.0237`
  - `centroid_dist_loo` vs `scope_and_timeline_human_y2`: `r=0.6713`, `p=0.0237`

Figures:

- `results/figures/rephrased/minimal/metric-score/corr_semantic_human_y2.png`
- `results/figures/rephrased/minimal/metric-score/corr_style_human_y2.png`

#### `## 3-7. Remaining Part V Sections`

Baseline-minimal output status from the audited executed notebook:

- `## 3. Strongest Correlations Summary`: no saved baseline-minimal output captured for the NCEMS/novelty summary cells in this notebook run.
- `## 4. Outlier Validation`: no saved baseline-minimal output captured in this notebook run.
- `## 5. Scatter Plots`: no saved baseline-minimal output captured in this notebook run.
- `## 6. Group-Level Analysis: Human vs AI`: no saved baseline-minimal output captured in this notebook run.
- `## 7. Summary Statistics Table` and export cells: no saved baseline-minimal output captured in this notebook run.

Interpretation from the executed baseline-minimal outputs only:

- In the captured correlation outputs, semantic-distance/remoteness metrics were generally negative against NCEMS relevance-type criteria and positive against several novelty-oriented criteria.
- In the captured Human-Y2 block, the strongest associations were concentrated on `data_identification_human_y2`, `synthesis_focus_human_y2`, and `scope_and_timeline_human_y2`.
- Style-based Part V interpretation is not available in this run because no style metrics were present in the merged baseline-minimal dataframe.

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
