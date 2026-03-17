## Overview

The goal of this study is to understand whether AI models (GPT, Gemini, Claude) can match or exceed teams of the best human scientists in biomedical domains in terms of the ability to generate novel, diverse, and high quality research ideas.

<!-- REVIEW: CRITICAL — Framing as "match or exceed" implies an apples-to-apples comparison, but the conditions are fundamentally different. Human proposals were written under real funding stakes with domain expertise, lab capabilities, and collaborative context. AI proposals are generated in zero-stakes, zero-context conditions. Consider reframing as "AI ideation capability assessment" or explicitly foregrounding this asymmetry. See Critique §1a. -->

Target publication venues:
- Nature machine intelligence
- Q: Any suggestions on other venus that will likely publish this study given the biomedical domain, AI, but small sample size?

<!-- REVIEW: See Critique §7 for venue-specific advice. Nature Machine Intelligence is feasible but will require addressing all critical issues below. Also consider: PNAS, Research Policy, Patterns (Cell Press), Quantitative Science Studies (MIT Press). -->

## Data
1. Call for proposals provided by the funding organizaiton. It outlines the requirements and areas of research that the funding organization (NCEMS) wants to fund. The call for proposal and information about NCEMS are in `data/call_and_info.json`
2. Proposals written by teams of human scientists from year 1 of submission and year 2 of submisson. these are two seperate cohorts of scientists, but the calls for the two years are the same. full proposals and names of authors are in `data/human-proposals`
<!-- REVIEW: Y1 (n=12) and Y2 (n=11) are different cohorts responding to potentially different calls. Can they be pooled? Test for cohort effects first (e.g., compare embedding distributions of Y1 vs Y2). If significantly different, analyze separately or include cohort as a covariate. See Critique §1b. -->

3. Human proposals from year 1 submissions have received detailed and qualitative reviews based on a set of criteria provided by NCEMS (`data/evaluation_criteria.json`) and the reviews are in `data/reviews/human_reviews/human_reviews_human-y1.xlsx`. We will receive human expert reviews for Y2 soon (end of february)



#  PART 1: Use AI models to generate proposals

### [DONE] Baseline condition:  AI generate proposals with only  the call for proposal and information about NCEMS. Each AI model receives the same prompt 
- First use generate_ideas_baseline prompt in `src/prompt_templates.py`,  instruct AI models (GPT, Gemini, Claude as specified in `src/ai_models_interface.py`) to each generate 23 research ideas (same as total amount of human proposals). In the prompt, includes the call for proposal and information about NCEMS from `data/call_and_info.json`. Save all the titles and abstracts of ideas into a single csv file in `data/ai-proposals/baseline` , distinguish which model is used to generate that idea.
- For each idea in the csv file,  use the same AI model to write out full proposals using the generate_proposals prompt in `src/promot_templates.py` and add the full proposal for each idea in the same csv file

<!-- REVIEW: Specify exact model versions (e.g., GPT-4o-2024-05-13, Claude 3.5 Sonnet, Gemini 1.5 Pro), temperature settings, and seed/determinism parameters. How many times is each generation run? Stochasticity matters for reproducibility. See Critique §6c. -->

### AI with Background literature:
- [DONE] claude code add PubMed support with `/plugin marketplace add anthropics/life-sciences`  `/plugin install pubmed@life-sciences`
- [DONE] Based on the call for proposal and NCEMS info, search relevant literature (n=10? 30? or?) from PubMed and save the title and abstracts of those articles to `data/literature/call-relevant-corpus`
- Add prompt to prompt_templates.py that instructs AI models to use these background research to generate proposals
<!-- REVIEW: Literature count is unresolved and matters enormously. Pre-specify: use NCEMS call keywords to construct PubMed queries, retrieve top N by relevance, date cutoff, filter criteria (review articles + original research). Report actual search queries. See Critique §4b. -->

### AI with human scientists' prev papers 
- [DONE] Extract all the author names from `data/human-proposals` as a list
- [DONE] For each author name in the list, use PubMed plugin to collect the most highly cited 5 articles by this author and save the titles and abstracts of each article. 
- [DONE] Save the names of authors and corresponding articles (title and abstract) as a structured json file in `data/literature/human-scientists-corpus.json`
- Instructs AI models to take background literature, and take on the persona of each member of each human teams by including previous articles published by each member, and generate research ideas and full proposals (Q: what if it goes out of max context window?)
<!-- REVIEW: The persona condition conflates persona simulation with knowledge injection. Consider splitting into: (a) literature-only (same papers, no persona instruction) and (b) literature + persona. This disentangles whether gains come from "thinking like" the researcher vs. having more relevant literature. See Critique §4a. -->

Save all proposals from each condition and merge with human proposals into a single CSV file for easy access and comparison later.

# PART 2: Compare AI proposals against human proposals
- Embedding model: Use biomedical domain specific embedding model (BioLinkBERT-Large, rank 1 on BLURB as of 02/10/2026) to transfrom each proposal into vectors (AI proposals stored in `data/ai-proposals`, human proposals stored in `data/human-proposals`)

- Save the embedding vectors of all proposals in one single file for easy access and comparison later.

For each set of AI proposals (23 from each AI models), conduct following analysis with human proposals: 



## PART 2-I DIVERSITY: Can AI generate more diverse proposals than teams of human scientists? 

#### Analysis 1.1 With-in group diversity
- Pair-wise comparison within group: human proposals vs AI proposals (from each model and ALL AI) to calculate cosine similarity 
- Compute pairwise cosine distances within each group
- Compare distributions using Mann-Whitney U test 
- Report Cliff's delta effect size
- Run permutation test (10,000 permutations) for robust p-value
- Create visualizations for the differences, effect size, and p-value

**Metrics:**
- Mean/median pairwise distance per group (human, AI from each model, and ALL AI)
- Mann-Whitney U statistic and p-value
- Cliff's delta (effect size): <0.147 negligible, <0.33 small, <0.474 medium, ≥0.474 large


#### Analysis 1.2: Centroid Dispersion Metric

**Rationale:** Complementary to pairwise distances. Measures how scattered proposals are from their group center.

**Steps:**
1. Compute centroid (mean embedding vector) for each group (human, AI from each model, and ALL AI)
2. Compute cosine distance from each proposal to its group centroid
3. Compare distributions of centroid distances between groups
4. Statistical test: Mann-Whitney U + Cliff's delta
5. Visualize the distributions and the statistical test results

**Metrics:**
- Mean distance to centroid per group
- Variance of distances to centroid (spread)

**Interpretation:**
- Higher mean distance to centroid = more dispersed = more diverse
- Can differ from pairwise metric if group has tight subclusters

---

#### Analysis 1.3: Nearest-Neighbor Outlier Detection

**Rationale:** Identifies "lone wolf" ideas far from everything else. High pairwise diversity could come from everyone being moderately different OR a few extreme outliers.

**Steps:**
1. Combine vectors of all proposals (human + AI)
2. For each proposal, find distance to its nearest neighbor among all
3. Compare NN distance distributions between human and AI
4. Identify proposals in top 10% of NN distances as "outliers"
5. Count outliers per group
6. Visualize the distance distributions and outliers for each group

**Metrics:**
- Mean/median nearest-neighbor distance per group
- Number of "outlier" proposals per group (top 10% NN distance)
- Percentage of nearest neighbors from same vs. different group

**Interpretation:**
- Higher NN distance = more outlier-ish idea
- More outliers in one group = that group produces more unique ideas


-

## PART 2-II NOVELTY: Can AI create more novel proposals than human scientists?

- given the corpus of relevant literature and papers published by human scientists, where do human proposals and AI proposals fit? 
- REPORT stats and info on literature corpus

#### Analysis 2.2.1: Compute Novelty Scores

**Steps:**
1. [done] Fetch PubMed abstracts with relevant terms from the call for proposal; saved in `data/literature/call-relevant-corpus.json`; 600 abstracts in total (350 original + 250 supplemental), fetched from relevant search terms based on the call and under-represented topics identified via LDA. Each article has title, abstract, and publication date (e.g., "2018 Aug").
2. Embed all abstracts with same model used for proposals (BioLinkBERT-Large)
3. Since all the PubMed articles only have abstracts, only use Section 1 ("Scientific Background and Research Question") from the standardized proposal template as the embedding input — this section is the closest in register and content to a PubMed abstract and avoids the document-register confound (proposals written in future-tense vs. papers in results-tense).
4. For each proposal, find k=10 nearest neighbors in corpus
5. Raw novelty score = mean cosine distance to k nearest neighbors; higher = farther from existing work
6. Create visualization of the projected embedding with nearest neighbors and outliers.

#### Analysis 2.2.1b: Literature-Normalized Novelty Scores

**Rationale:** Raw k-NN distances are *corpus-relative* — a score of 0.15 vs 0.10 only tells you one proposal is farther, but neither value is interpretable as "objectively novel" because it depends on how densely the corpus covers the topic. If the corpus is sparse in a given area, proposals in that area will always score high regardless of true novelty.

**Normalization approach:** Compute the same k=10 NN distance for each article *against the rest of the corpus* (excluding self). This yields a baseline distribution representing how spread-out the literature itself is. Proposal scores are then expressed relative to that baseline.

**Steps:**
1. Compute within-corpus k=10 NN distances for all literature articles (diagonal excluded)
2. Compute baseline mean (μ_lit) and std (σ_lit) of within-corpus distances
3. **z-score**: `z = (proposal_novelty − μ_lit) / σ_lit`
   - z > 0: proposal farther from literature than the typical inter-article gap → genuinely novel relative to corpus density
   - z ≈ 0: proposal sits at the same distance as a typical article in the corpus
   - z < 0: proposal closer to literature than articles are to each other
4. **Ratio**: `ratio = proposal_novelty / μ_lit`
   - >1: farther from literature than articles are from each other
   - <1: closer to existing work than typical within-corpus spacing

**Metrics:**
- Mean z-score per group (human, each AI model, all AI)
- Mean ratio per group
- Both raw and normalized scores reported side-by-side
- Statistical tests (Mann-Whitney U + Cliff's delta + permutation) run on z-scores

**Visualization:**
- Three-panel plot: raw scores, z-score, and ratio side-by-side with reference lines
- Within-literature baseline distribution (histogram) with group means overlaid as vertical lines

**Interpretation note:** z-scores answer "how far is this proposal relative to how spread out the literature already is?" making results corpus-size-independent and more comparable across different literature collections.


#### Analysis 2.2.2: Compare Novelty Distributions

**Steps:**
1. Compute raw and literature-normalized (z-score) novelty scores for all human and AI proposals
2. Compare distributions: Mann-Whitney U + Cliff's delta + permutation test
3. Report both raw and z-score results side-by-side; flag if conclusions differ
4. Sensitivity analysis: vary k (5, 10, 20, 50) and check robustness

**Metrics:**
- Mean/median novelty score per group (raw and z-score)
- Effect size (Cliff's delta)
- Consistency across different k values



## PART 2-III Thematic and Cluster Analysis

### Rationale
Reviewers will ask: "What are the actual conceptual differences?" This section examines whether human and AI proposals cluster in distinct semantic regions and whether they differ in thematic coverage.

**⚠️ Sample Size Consideration:** With n=23 human and n=69 AI proposals, automated topic modeling is underpowered. We combine conservative automated approaches with visualization-based exploratory analysis.

---

### Analysis 2.3.1: Topic Modeling (Exploratory)

**Approach:** Use Latent Dirichlet Allocation (LDA) instead of BERTopic due to small sample size. LDA allows strong priors that stabilize topics with limited data.

**Steps:**
1. Use only title and abstracts for both human and AI proposals
2. Create TF-IDF representations (remove stop words, min_df=2, max_df=0.7)
3. Fit LDA with conservative parameters:
   - n_topics = 5 (fixed, not "auto")
   - doc_topic_prior (alpha) = 0.5 (strong prior for document regularization)
   - topic_word_prior (beta) = 0.5 (strong prior for topic regularization)
   - max_iter = 100
4. Extract top 10 words per topic
5. Domain expert review to create interpretable topic labels
6. Compute per-document topic distributions (soft assignment)

**Parameters:**
- Embedding: TF-IDF (for LDA input)
- n_topics: 5 (manual selection based on sample size)
- Priors: alpha=0.5, beta=0.5 (strong regularization)

**Library:** sklearn.decomposition.LatentDirichletAllocation

**Validation:**
- Assess topic coherence (c_v metric using gensim)
- Report perplexity
- Stability check: run with 10 different random seeds, report average topic-word distributions
- Label as **EXPLORATORY** - interpret with caution given sample size

---

### Analysis 2.3.2: Topic Distribution Comparison

**Operationalization (soft assignment throughout):** All topic analyses use a soft participation threshold of >20% LDA probability. A proposal "belongs to" a topic if its LDA-assigned probability for that topic exceeds 0.20. A single proposal can contribute to multiple topics. This is consistent with the coverage metric in 2.3.3 and avoids the information loss of winner-takes-all dominant-topic assignment.

**Steps:**
1. Build soft participation table: for each topic, count proposals in each group with >20% probability
2. **Primary test:** Permutation test for distribution difference
   - Shuffle group labels 10,000 times, recompute soft counts, compute chi-square statistic on soft table
   - p-value: proportion of permutations with χ² ≥ observed
3. **Per-topic tests:** Fisher's exact test on binary soft participation (has >20% for topic or not)
   - Test: Is this topic more common in human vs. all AI?
4. **Multiple testing correction:** Benjamini-Hochberg FDR at q=0.10 (exploratory threshold)
5. Identify topics significantly over-represented in each group

**Sample Size Adjustment:**
- For human vs. AI comparisons: subsample AI to n=23, repeat 1000 times using same soft counts
- Report: "Topic X is over-represented in human proposals in 847/1000 subsamples (p=0.015)"
- This accounts for the 3:1 imbalance in group sizes

**Metrics:**
- Permutation p-value (overall distribution difference, soft counts)
- Odds ratios per topic with soft binary participation
- FDR-corrected p-values per topic

**Visualization:**
- Heatmap of topic × source showing % of group with >20% probability (not dominant-topic %)
- Bar plot of soft-participation prevalence by group (with subsample error bars)

---

### Analysis 2.3.3: Topic Coverage and Entropy (with Sample Size Correction)

**All metrics use the same soft assignment threshold (>20% probability) for consistency with 2.3.2.**

**Steps:**
1. **Topic coverage:** Count unique topics where at least one proposal in the group has >20% probability. Already uses soft assignment — unchanged.
2. **Exclusive topics:**
   - Identify topics where one group has ≥2 proposals with >20% probability AND the other group has 0 proposals with >20% probability
   - Threshold lowered from ≥5 to ≥2: with n=23 human proposals, requiring ≥5 is too strict and would suppress all human-exclusive topics by design
   - **Permutation test:** Shuffle labels 10,000 times, count exclusive topics in null using same soft rule
   - Report: "X topics human-exclusive vs. Y expected by chance (p=...)"
3. **Shannon entropy on mean soft topic distribution:**
   - Compute mean LDA probability vector across all proposals in each group (not dominant-topic counts)
   - Apply Miller-Madow bias correction: H_corrected = H + (K−1)/(2N)
   - **Account for sample size:** Subsample AI to n=23, compute soft entropy, repeat 1000 times
   - Report: "Human entropy = X, AI entropy = Y ± Z (mean ± SD from subsampling)"
   - Using mean soft distribution avoids the dominant-topic discretization artifact where a proposal with 35%/33%/32% across three topics is forced into one bin

**Rationale for soft assignment throughout:** Using dominant-topic (winner-takes-all) assignment for coverage, exclusive topics, and entropy produces internally inconsistent results — a topic can appear "100% AI" in the dominant-topic proportion table while Human coverage of that topic is 4/5, because some human proposals have >20% soft probability for that topic without it being their dominant assignment. Soft assignment throughout eliminates this contradiction.

**Metrics:**
- Number of topics covered per group (threshold > 0.20)
- Number of exclusive topics (observed vs. permutation null, min_count=2)
- Shannon entropy of mean soft topic distribution (with Miller-Madow correction and subsample validation)
- Normalized entropy: H / log(K) where K = number of topics

**Interpretation:**
- Topic coverage indicates breadth of thematic exploration
- Entropy indicates evenness of probability mass spread across topics
- **Caution:** With only 5 topics and small sample, differences may reflect noise

---

### Analysis 2.3.4: Cluster Composition/Segregation Analysis

**Rationale:** Do human and AI proposals occupy the same conceptual regions or segregate into different clusters in embedding space?

**Steps:**

**1. Optimal k Selection (Data-Driven)**
- Use embeddings from diversity analysis (BioLinkBERT-Large, full text)
- Test k = 3, 4, 5, 6, 7, 8 using Gaussian Mixture Models (GMM)
- For each k, compute:
  - Silhouette score (higher = better separation)
  - Davies-Bouldin index (lower = better)
  - Bayesian Information Criterion (BIC, lower = better fit)
- Select k using "elbow method" on BIC and validate with silhouette
- **Rationale for GMM:** Allows soft clustering, arbitrary cluster shapes, better than k-means for embeddings

**2. Clustering with Best k**
```python
from sklearn.mixture import GaussianMixture
gmm = GaussianMixture(n_components=k_best, covariance_type='full', random_state=42)
cluster_labels = gmm.fit_predict(embeddings)
cluster_probs = gmm.predict_proba(embeddings)  # Soft assignment
```

**3. Cluster Composition Analysis**
- For each cluster: compute % human, % AI (by model)
- Identify:
  - Human-dominated clusters (>60% human)
  - AI-dominated clusters (>80% AI)
  - Mixed clusters (40-60% human)
- **Account for base rates:** With 23 human / 69 AI (25% baseline), "mixed" means ~25% ± 10%

**4. Segregation Metrics with Permutation Tests**

**Normalized Mutual Information (NMI):**
- Compute: NMI(cluster_labels, source_labels)
- **Permutation test:** Shuffle source labels 10,000 times, compute NMI_null distribution
- Report: "Observed NMI = X, null mean = Y ± Z, p = ..."
- Interpretation: Does clustering recover source better than chance?

**Adjusted Rand Index (ARI):**
- Compute: ARI(cluster_labels, source_labels)  
- **Permutation test:** Same as NMI
- ARI corrects for chance, but still validate against permutation null

**Within-group vs. Between-group Distance:**
- Mean distance within human proposals
- Mean distance within AI proposals  
- Mean distance between human and AI proposals
- **Permutation test:** Shuffle labels, compute distances, compare to observed

**5. Visualization**
- 2D UMAP projection colored by:
  - (a) Cluster assignment
  - (b) Source (human vs. AI)
  - (c) Cluster composition (pie charts showing human/AI mix per cluster)
- Dendrogram from hierarchical clustering for comparison

**Metrics:**
- Silhouette score for chosen k
- NMI score with permutation p-value
- Adjusted Rand Index with permutation p-value  
- Per-cluster composition (% human, % AI by model)
- Number of human-dominated, AI-dominated, mixed clusters
- Within-group vs. between-group distance ratios

**Interpretation:**
- **High NMI/ARI (p < 0.05):** Clusters predict source → segregation → human and AI generate different KINDS of ideas
- **Low NMI/ARI (p > 0.10):** Clustering independent of source → integration → ideas intermixed regardless of source
- **Intermediate:** Some thematic clustering but not strictly by source

**Limitations:**
- With n=92 total, clusters with k>5 may be unstable
- Interpret conservatively and compare to embedding space visualizations
- Segregation may reflect prompt/instruction differences, not inherent idea differences

---

### Analysis 2.3.5: Style vs. Content Diagnostics (Style-Only Baseline)

**Rationale:** Before interpreting embedding distances, clustering segregation (NMI/ARI), or topic separation as “conceptual” differences, quantify how much **purely stylistic** signals can separate Human vs. AI. If a style-only model predicts source well, then a substantial portion of downstream “segregation/diversity” effects may be stylistic rather than conceptual.

**Inputs:**
- Same proposal text used for downstream analyses (abstract-only vs full text should be evaluated separately).
- Labels: `group ∈ {Human, AI}` and optionally `model` for model-specific effects.

**Style feature set (no domain semantics):**
- **Length/structure**: word count, character count, sentence count, avg sentence length, paragraph count, section header count (if structured).
- **Function-word profile**: rates of common stopwords/function words, pronoun rates, determiners/prepositions/conjunctions.
- **Punctuation/formatting**: comma/semicolon/colon/dash rates, parentheses rate, citation-like patterns, bullet/list markers.
- **Readability**: Flesch-Kincaid / Gunning Fog (or similar), type-token ratio / lexical richness proxies.
- **Hedging/stance markers**: rates of “may/might/could/suggest”, “we propose/aim”, “novel”, “significant”, etc. (predefined lexicon).
- **POS distribution (optional)**: coarse POS tag proportions (noun/verb/adj/adv), if a tagger is available.

**Modeling / evaluation:**
- Train a simple classifier on style features only (e.g., regularized logistic regression).
- Report: **AUROC**, balanced accuracy, calibration (optional), and **permutation test** for AUROC (shuffle labels 10,000×).
- **Cross-validation:** stratified CV; report mean ± std. If evaluating by AI model, report one-vs-rest AUROC as a secondary analysis.

**Interpretation:**
- **High AUROC (e.g., ≥0.8):** strong style separability → downstream embedding/topic separation likely includes a large stylistic component.
- **Moderate AUROC (0.6–0.8):** style contributes but does not fully explain separation.
- **Near chance (~0.5):** style-only signals weak → downstream separation more plausibly content-driven (still not guaranteed).

---

### Analysis 2.3.6: Style-Controlled Sensitivity Analyses 

**Rationale:** Reduce stylistic confounding without altering proposal content. Two complementary approaches: (A) adjust outcome metrics for style covariates, (B) perform matched comparisons between Human and AI proposals with similar style/structure.


**A) Residualization / covariate control**
- Define a compact style covariate set (pre-registered from 2.3.5), e.g.:
  - length (log word count), avg sentence length
  - readability score
  - lexical richness proxy
  - hedging rate
  - section/header count (if applicable)
- For each downstream outcome \(Y\) (examples below), fit a regression model \(Y \sim \text{group} + \text{style covariates}\) and evaluate the **group coefficient**:
  - **Embedding distance metrics** (within/between means; centroid dispersion; nearest-neighbor outliers)
  - **Segregation metrics** (NMI/ARI): treat as summary statistics; use permutation tests that preserve style covariates where feasible, and interpret as sensitivity (not definitive causal adjustment).
  - **Topic mixture diversity** (entropy over full topic-probability vectors; avoid dominant-topic-only where it acts as a source classifier)
- Report both:
  - **Unadjusted** group differences (baseline)
  - **Style-adjusted** group differences (residualized or covariate-controlled), with uncertainty (bootstrap or permutation where appropriate)

**Reporting guidance:**
- Label these as **construct-validity / robustness** checks (not primary claims).
- If results change materially after style control, explicitly state which conclusions are sensitive to style normalization.

#### how does it work
What “style-adjustment” is (simple version)
Goal: separate “what the idea is about” from how it’s written.
You first measure something in embedding space (centroid-dispersion, NN distance, clustering). Then you try to subtract the part of that measurement that can be predicted from style features (length, sentence structure, hedging, readability, headers, punctuation).
In practice you’re doing: metric = style‑predictable part + leftover part
and you keep the leftover as “style-adjusted”.
Centroid dispersion: how style-adjustment works
Unadjusted centroid dispersion:
For each group (Human, each AI model), you compute that group’s centroid (average embedding), then for each proposal you compute distance to its group centroid. Bigger distance → more “spread out” within that group.
Style-adjusted centroid dispersion (what your code does):
Compute each proposal’s distance-to-its-group-centroid (y_raw).
Fit a simple linear model: y_raw ~ (style features).
Subtract the model’s prediction from y_raw to get a residual.
Add back the overall mean (just to keep numbers on a similar scale).
Result: y_adj = “dispersion after removing what style can explain”.
Statistical tests on style-adjusted dispersion:
Same tests, just run on y_adj instead of y_raw.
So your MW / Cliff’s delta / permutation test become: “Are groups still different in dispersion after removing style effects?”
Nearest-neighbor (NN) outlier detection: how style-adjustment works
Unadjusted NN distance:
For each proposal, find its closest neighbor (smallest cosine distance). Larger NN distance → more isolated/outlier.
Style-adjusted NN (Option A you added):
Instead of adjusting the distance numbers, you adjust the embeddings themselves.
Fit a linear model per embedding dimension: embedding_dim ~ (style features).
Subtract predicted “style component” → residual embeddings.
Re-normalize residual embeddings and recompute cosine distances + NN distances.
Interpretation: “Is this proposal still an outlier when you remove embedding variation that’s linearly associated with writing style?”
Gaussian mixture clustering: how style-adjustment would work
There are two common ways:
Approach 1 (embedding residuals, recommended):
Residualize embeddings on style (same as NN Option A), then run GMM clustering on the residual embeddings.
Then recompute segregation metrics (NMI/ARI), cluster composition, etc., using cluster labels from residual space.
Approach 2 (cluster on original embeddings, then adjust tests):
Keep clusters, but when you test “Human vs AI separation,” control for style in a downstream model. This is usually weaker/less clean than residualizing embeddings first.
If style is driving the separation, you’d expect cluster segregation to drop after residualization.
Is this a valid way to “counter” stylistic differences, given your style-only AUROC = 1.0?
It’s useful as a sensitivity analysis, but it’s not a silver bullet.
What it can do well: remove linear, measurable style effects captured by your covariates (length/readability/hedging/headers, etc.). If group differences shrink but don’t disappear, that’s evidence there’s something beyond those style signals.
Key limitation: your result (“style alone perfectly separates Human vs AI”) implies style differences are huge. In that case:
embeddings may already encode style strongly,
“content vs style” may be partially entangled,
residualization might remove not only “style,” but also real content variation that correlates with style (e.g., humans write longer and also cover topics differently).
So the right claim is: “After removing the embedding components predictable from style features, do we still see separation?”
Not: “We’ve fully removed style and now what remains is pure content.”
Practical guidance (how to report it)
Report both unadjusted and style-adjusted results side-by-side.
Phrase conclusions as robustness checks:
“Separation persists after style adjustment” (stronger evidence of content/idea differences)
“Separation largely disappears after style adjustment” (suggests style is a major driver)
Be explicit that adjustment is linear and depends on the chosen style covariates.
---

### Multiple Testing Correction Strategy (Section 2.3)

**Test Families:**
1. **Topic distribution tests:** Per-topic Fisher's exact (n ≈ 5 topics × 4 comparisons = 20 tests)
   - FDR correction at q = 0.10 (exploratory threshold)
2. **Topic exclusivity:** One test per comparison (n = 4)
   - No correction (single test per hypothesis)
3. **Segregation metrics:** NMI and ARI (n = 2 primary metrics)
   - No correction (planned comparisons, permutation-based)

**Global Strategy Across Study:**
- Section 2.1 (diversity): 3 metrics × 4 comparisons = 12 tests → FDR q=0.05
- Section 2.2 (novelty): 1 metric × 4 comparisons = 4 tests → FDR q=0.05  
- Section 2.3 (topics/clusters): ~25 tests → FDR q=0.10 (exploratory)
- **Total:** ~40 tests across study
- **Strategy:** Correct within sections, report raw p-values in appendix, clearly label exploratory analyses

---



## PART IV QUALITY: Can AI create proposals of higher quality than teams of human scientists?

- Use the prompt `eval_ncems_criteria` in `human-AI-proposal/src/prompt_templates.py` to instruct EACH AI model (GPT, Gemini, Claude) to evaluate each human proposal (`human-AI-proposal/data/human-proposals/human-proposals-y1.json` and `human-AI-proposal/data/human-proposals/human-proposals-y2.json`) and AI proposals in `human-AI-proposal/data/ai-proposals/baseline/ai_proposals_baseline_complete_20260209_205423.csv`(the model is blinded to authorship, one proposal per API call). save the evaluataions for all proposals from all AI model in a single json file in `data/reviews/ai_reviews` with fields for title, author (human-y1, human-y2, or which AI model), evaluator (which model), and evaluations (should already be json from AI's output).  

- Compare the reviews for human proposals (Y1, Y2, or Y1Y2 combined) and AI proposals, questions we want to answer: (1) whose proposals are rated as higher quality, and on what criteria? (2) are AI reviews a good proxy for expert humans' reviews? 
- Conduct and visualize Mann-Whitney U statistic and p-value and Cliff's delta (effect size) for all comparisons

- Define global color scheme for visualization to have consistent colors for each group
```python 
   colors = {
      'Human': '#DC143C',  # Crimson red (PROMINENT)
      'claude-opus-4-5': '#4A90E2',  # Blue
      'gemini-3-pro-preview': '#7B68EE',  # Purple
      'gpt-5.2': '#FF8C00',  # Dark orange
   }
```

(1) 
   Compare the similarity between AI's qualitative review (reasoning behind their rating) and human experts' qualitative reviews on human-y1 proposals (human reviews: `human-AI-proposal/data/reviews/human_reviews/human_reviews_human-y1.xlsx`, AI reviews: `human-AI-proposal/data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json`) to see whether AI's reviews are a reliable proxy

   - Similarity: 
      - cosine semantic similarity (same embedding model for comparing proposals: BioLinkBERT-Large)
      - Sentiment alignment: agreement in evaluative tone 
         - Sentiment alignment was computed as follows:
            - Polarity scores (-1 to +1) were extracted using TextBlob
            - Reviews were labeled positive (polarity > 0.1), negative (< -0.1), or neutral
            - Alignment score = 1 - (|polarity_1 - polarity_2| / 2), yielding values from 0 (opposite sentiment) to 1 (identical sentiment)
         - We also compute categorical sentiment agreement (agree/partial/disagree) based on whether review pairs shared the same sentiment label.  It is computed from the sentiment labels of each pair of reviews. So:
            - Agree = same category (fully aligned at the label level).
            - Disagree = opposite categories (positive vs negative).
            - Partial = one is neutral, and the other is positive or negative (neither fully agrees nor fully disagrees).
   
   To establish baseline inter-rater similarity, we compute the same metrics for human-human review pairs (since each proposal has multiple human reviewers). Then we conduct a Mann-Whitney U test on the differences between the two groups (human-AI comparisons, human-human comparisons) on each metric to see whether the differences are significant.


(2) 
   - Create summary statistics and visualizations (histogram, box plots, radar chart) for reviews `human-AI-proposal/data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json` for each author (human-y1, human-y2, human-all, each AI model) on overall score (average across criteria) and each review criteria ['Relevance_to_Emergent_Phenomena', 'Novelty_and_Significance', 'Rigor_of_Approach', 'Scope_and_Timeline', 'Synthesis_Focus', 'Data_Identification', 'Open_Science_Commitment']. 
   - Which author scores higher? on what criteria? is the difference statistically significant (p value)? what is the effect size (cliff's delta)?
   - Are there differences in reviews from different AI reviewer? 
      - "AI self-preference" test: do models rate their own outputs higher? Also: how are structured criteria scores aggregated — averaged? weighted?


(3) [TODO] Find human experts to evaluate top human and AI proposals (blinded about authorship)



---



## PART V 3: Review Score Prediction and Outlier Validation

#### 3.0 Overview

This analysis links the embedding and style metrics computed in the style-controlled comparison notebook to the AI-generated review scores (`data/reviews/ai_reviews/ai_reviews_rephrased_*.json`). It has two primary goals:

1. **Metric validation**: Test whether the computed metrics (semantic diversity, style features) can predict review scores on specific criteria — if novelty-related embedding metrics predict "Novelty & Significance" scores, this validates that the metrics are capturing meaningful signal.
2. **Outlier validation**: Test whether the proposals identified as most semantically unique (top-10% nearest-neighbor distance) actually received higher scores on the "Novelty & Significance" criterion.

**Review data structure** (as of `ai_reviews_rephrased_20260314_144505.json`):
- 92 proposals × 3 AI evaluators (GPT, Gemini, Claude) = 276 reviews
- 7 scored criteria: Relevance to Emergent Phenomena, Novelty & Significance, Rigor of Approach, Scope & Timeline, Synthesis Focus, Data Identification, Open Science Commitment

---

#### 3.1 Analysis: Metric–Score Correlation

**Goal**: For each of the 7 review criteria, assess whether the computed embedding/style metrics are correlated with the scores received.

**Steps**:
1. Flatten reviews to one row per proposal, averaging scores across the 3 evaluators for each criterion (N=92 × 7 score columns).
2. Compute Spearman correlations between each metric and each criterion. Present as a heatmap (metrics × criteria).
3. Apply Holm correction for multiple comparisons across the full matrix.

**Theoretically motivated pairs to highlight**:

| Metric | Criterion |
|---|---|
| NN distance (semantic uniqueness) | Novelty & Significance |
| Centroid distance | Novelty & Significance |
| Pairwise diversity | Novelty & Significance |

---

#### 3.2 Analysis: Predictive Modeling of Review Scores

**Goal**: Test whether metrics jointly predict each criterion score beyond chance, and decompose how much of the predictable variance comes from style vs. semantic content.

**Steps**:
1. For each of the 7 criteria, fit a Ridge regression (cross-validated, 5-fold StratifiedKFold on score quartiles) predicting criterion score from all metrics. Report cross-validated R² per criterion.
2. Run two separate models per criterion: (a) style features only; (b) embedding features only (NN distance, centroid distance, pairwise diversity). Compare R² to assess relative contribution of surface style vs. semantic content.
3. Use permutation test (1,000 shuffles) to confirm that any significant R² exceeds the null.

**Interpretation**: If embedding features predict novelty scores but style features do not, this strengthens the argument that the rephrasing successfully removed style as a confound and that the embedding space is capturing genuine semantic differences.

---

#### 3.3 Analysis: Outlier Validation

**Goal**: Test whether proposals identified as semantic outliers (most isolated in embedding space) received higher scores on "Novelty & Significance."

**Steps**:
1. Use the outlier labels from the notebook (top-10% NN distance across all 92 proposals).
2. Compare "Novelty & Significance" scores (averaged across evaluators) between outlier and non-outlier proposals using Mann-Whitney U + Cliff's Delta.
3. Run the same test for all 7 criteria to check whether outlier status is novelty-specific or reflects overall proposal quality.
4. **Within-group outlier analysis**: Repeat using within-group outlier labels (top-10% NN distance computed separately within Human / Claude / Gemini / GPT). Compare global vs. within-group outlier status as predictors of novelty score.

---

#### 3.4 Analysis: Human vs. AI Outlier Comparison

**Goal**: Test whether "novel" AI proposals (AI outliers) are rewarded the same way as "novel" human proposals (human outliers) by the AI reviewers.

**Steps**:
1. Among outlier proposals only, compare "Novelty & Significance" scores between human outliers and AI outliers using Mann-Whitney U.
2. Repeat for each AI model's outliers separately (GPT had 26% outliers; Claude had 0%).
3. Compute the correlation between NN distance and novelty score separately within each group (Human, Claude, Gemini, GPT). Test whether the slope differs across groups (interaction term in a mixed-effects model with group × NN distance).

**Interpretation**: If NN distance predicts novelty scores for human proposals but not for AI proposals (or vice versa), this suggests the AI reviewers and the embedding space are capturing different notions of novelty for the two sources.


---




## 4. PUBLICATION STRATEGY

#### Nature Machine Intelligence (primary target)

Feasible but will require:
- Addressing all critical issues above (especially population mismatch framing, power analysis, human expert evaluation)
- Pre-registration
- Positioning as a methodological contribution with implications for AI-augmented science, not just a comparison
- Strong discussion of limitations

#### Alternative venues (in rough order of fit)

| Venue | Strengths | Considerations |
|-------|-----------|----------------|
| **PNAS** | Interdisciplinary, strong on methodology | Requires broad significance framing |
| **Research Policy** | If framed around science policy implications | Less technical audience |
| **Nature Human Behaviour** | If framed around human vs. AI cognition | Requires cognitive science framing |
| **Patterns (Cell Press)** | Data science + biomedicine, accepts smaller studies | Good fit for methods paper |
| **Quantitative Science Studies (MIT Press)** | Science-of-science venue, comfortable with small N | Niche but respected |
| **Science Advances** | Broad audience, accepts AI + science studies | Competitive |
| **PLOS ONE** | If study is solid but sample size limits novelty claims | Less prestige but solid |

---