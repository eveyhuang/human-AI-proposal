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
1. [done] Fetch PubMed abstracts with relevant terms from the call for proposal; saved in `data/literature/call-relevant-corpus.json`; there are 350 abstracts in total, fetched from relevant search terms based on the call (7 distinct queries), and each article has title, abstract, and publication date (e.g., "2018 Aug")
2. Embed all abstracts with same model used for proposals (BioLinkBERT-Large)
3. Since all the PubMed articles only have abstracts, only use abstracts from humans' and AI proposals as well. and re-embed them with only title and abstracts. 
3. For each proposal, find k nearest neighbors in corpus (k=10)
4. Novelty score = mean distance to k nearest neighbors;  Higher score = farther from existing work = more novel
5. Create visulization of the projected embedding with nearest neighbors and outliers. 



#### Analysis 2.2.2: Compare Novelty Distributions

**Steps:**
1. Compute novelty scores for all human and AI proposals
2. Compare distributions: Mann-Whitney U + Cliff's delta
3. Sensitivity analysis: vary k (5, 10, 20, 50) and check robustness

**Metrics:**
- Mean/median novelty score per group
- Effect size (Cliff's delta)
- Consistency across different k values



## PART 2-III Thematic and Cluster Analysis

#### Rationale
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

**Steps:**
1. Create contingency table: topics × source (human/AI/per-model)
2. **Primary test:** Permutation test for distribution difference
   - Null: shuffle labels 10,000 times, compute chi-square statistic
   - p-value: proportion of permutations with χ² ≥ observed
   - This avoids chi-square assumptions about cell counts
3. **Per-topic tests:** Fisher's exact test for each topic's over/under-representation
   - Test: Is this topic more common in human vs. all AI?
   - Test: Is this topic more common in human vs. each AI model?
4. **Multiple testing correction:** Benjamini-Hochberg FDR at q=0.10 (exploratory threshold)
5. Identify topics significantly over-represented in each group

**Sample Size Adjustment:**
- For human vs. AI comparisons: subsample AI to n=23, repeat 1000 times
- Report: "Topic X is over-represented in human proposals in 847/1000 subsamples (p=0.015)"
- This accounts for the 3:1 imbalance in group sizes

**Metrics:**
- Permutation p-value (overall distribution difference)
- Odds ratios per topic with 95% CI
- FDR-corrected p-values per topic
- Effect size: Cramér's V

**Visualization:**
- Heatmap of topic × source with count proportions
- Bar plot of topic prevalence by group (with error bars from subsampling)

---

### Analysis 2.3.3: Topic Coverage and Entropy (with Sample Size Correction)

**Steps:**
1. **Topic coverage:** Count unique topics represented per group (threshold: topic probability > 0.20)
2. **Exclusive topics:** 
   - Identify topics appearing in one group but not the other
   - **Permutation test:** Shuffle labels 10,000 times, count exclusive topics in null
   - Report: "X topics human-exclusive vs. Y expected by chance (p=...)"
   - Only consider "exclusive" if topic appears in ≥5 proposals from one group, 0 from other
3. **Shannon entropy:** 
   - Compute entropy of topic distribution for each group
   - **Account for sample size:** Subsample AI to n=23, compute entropy, repeat 1000 times
   - Report: "Human entropy = X, AI entropy = Y ± Z (mean ± SD from subsampling)"
   - Use Miller-Madow bias correction: H_corrected = H + (K-1)/(2*N) where K=topics, N=samples
4. Higher entropy = more even spread across topics

**Metrics:**
- Number of topics covered per group (threshold > 0.20)
- Number of exclusive topics (observed vs. permutation null)
- Shannon entropy (with Miller-Madow correction and subsample validation)
- Normalized entropy: H / log(K) where K = number of topics

**Interpretation:**
- Topic coverage indicates breadth of thematic exploration
- Entropy indicates evenness of distribution across themes
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

**B) Matched comparisons (style/structure matching)**
- Construct matched sets pairing each Human proposal with \(m\) AI proposals (e.g., \(m=1\) or \(m=3\)) using nearest-neighbor matching on standardized style covariates:
  - log word count, avg sentence length, readability, header count, hedging rate (minimum set)
- Validate match quality: standardized mean differences for covariates before/after matching.
- Re-run key comparisons on the matched dataset:
  - within/between embedding distances
  - cluster composition and segregation metrics
  - topic mixture diversity (entropy over mixtures)
- **Interpretation:** If results persist after matching, they are less likely to be driven by trivial style differences; if they attenuate substantially, that supports the “style confound” concern.

**Reporting guidance:**
- Label these as **construct-validity / robustness** checks (not primary claims).
- If results change materially after style control, explicitly state which conclusions are sensitive to style normalization.

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



### PART IV QUALITY: Can AI create proposals of higher quality than teams of human scientists?

- Give the criteria `data/evaluation_criteria.json` to AI models and instruct them to evaluate all human and AI proposals (blinded to authorship), then compare the evaluations
- Invite human experts to blindly review a subset of human and AI proposals, and compare
- Compare the similarity between AI's and human experts' reviews to see whether AI's reviews are reliable proxy
- "AI self-preference" test: do models rate their own outputs higher? Also: how are structured criteria scores aggregated — averaged? weighted?
- [TODO] Find human experts to evaluate top human and AI proposals (blinded about authorship)



---

# CRITIQUE AND REVIEW

*This section provides a structured critique of the analysis plan above, identifying issues that should be addressed before submission to a top venue. Issues are organized by severity and type. Inline `<!-- REVIEW: ... -->` comments are placed throughout the plan above at specific locations where issues arise.*

### Summary Assessment

**Strengths:** The plan is ambitious and well-structured, covering multiple meaningful dimensions (diversity, novelty, quality, topics). The statistical methods are generally appropriate (non-parametric tests, effect sizes, permutation tests, FDR correction). The multi-model approach (GPT, Gemini, Claude) and multi-condition design add robustness.

**Main concerns:** Several fundamental design issues threaten internal validity and publishability at a top venue. The most critical are: (1) a severe population mismatch confound between human and AI proposals, (2) small and unbalanced sample sizes with no power analysis, (3) construct validity gaps for embedding-based metrics, (4) circularity in AI-as-evaluator design, and (5) missing pre-registration and ethics/IRB discussion.

---

### 1. CRITICAL ISSUES (Must Address Before Submission)

#### 1a. Population Mismatch Confound

The human proposals were written by motivated teams responding to a real funding call with real stakes (career, funding). AI proposals are generated in zero-stakes, zero-context conditions. This is not an apples-to-apples comparison. Human proposals reflect domain expertise, lab capabilities, existing collaborations, and institutional context that AI cannot possess. **This confound undermines every downstream comparison.**

**Suggested fixes:**
- Reframe the study as "AI ideation capability" rather than "AI vs. human scientists"
- At minimum, acknowledge this prominently in the introduction and discussion, and discuss how it limits interpretation of all results

#### 1b. Sample Size and Statistical Power

- 23 human proposals (12 Y1 + 11 Y2) is very small
- No power analysis is presented 
- Permutation tests help with p-value robustness but cannot create statistical power from thin air

**Suggested fixes:**
- Add a formal power analysis (e.g., using G*Power or simulation) for the primary comparisons
- Report minimum detectable effect sizes given current sample sizes
- Test for cohort effects between Y1 and Y2 before pooling (e.g., compare embedding distributions, use Kolmogorov-Smirnov test)
- Be transparent about power limitations in the manuscript

#### 1c. Multiple Comparisons Across the Full Study

The plan mentions FDR correction within Analysis 2.4.2 but not across the entire study. With 3 AI conditions × 4 evaluation dimensions × multiple sub-analyses, the total number of tests is large. Without a global correction strategy, false positive risk is high.

**Suggested fixes:**
- Define a clear hierarchy: primary outcome(s) vs. secondary/exploratory analyses
- Apply family-wise correction (e.g., Bonferroni or Holm) across primary outcomes
- Apply FDR correction within each analysis family
- Label everything beyond primary outcomes as exploratory

#### 1d. Construct Validity: Embedding Distance ≠ Conceptual Diversity/Novelty

The plan equates cosine distance in embedding space with "diversity" and "novelty." This is a strong assumption. Embedding models capture textual similarity, which may reflect:
- Writing style differences (AI text is stylistically distinct from human academic writing)
- Vocabulary differences (AI may use different jargon)
- Surface-level paraphrasing rather than conceptual distance

A proposal could be semantically distant in embedding space while being conceptually derivative, or vice versa.

**Suggested fixes:**
- **Validate the embedding metric:** Take a subset of proposal pairs, have domain experts rate their conceptual similarity, and correlate with cosine distance. This calibration step is essential for any top venue.
- **Use multiple embedding models** (not just nomic-embed-text-v1) and report consistency. Consider biomedical-specific models like BioSentVec, PubMedBERT, or SciNCL.
- **Add a "style control" analysis:** Embed proposals after stripping them to keywords/concepts only (e.g., extract MeSH terms or key noun phrases) to separate conceptual content from writing style.

#### 1e. Novelty Score Conflates Novelty with Incoherence

A proposal that is far from all existing literature could be genuinely novel OR nonsensical. Distance from corpus captures both.

**Suggested fixes:**
- Add a "feasibility filter" — only compute novelty for proposals that pass a minimum quality threshold
- Or compute novelty conditional on quality scores (e.g., report novelty for the subset above median quality)
- Discuss this limitation explicitly

#### 1f. AI-as-Evaluator Circularity (Section 2.3)

Using AI models to evaluate AI-generated proposals creates a circularity problem. AI models may:
- Favor their own stylistic patterns (self-preference bias, documented in literature)
- Systematically rate AI proposals higher due to format/style alignment
- Miss domain-specific issues that human experts would catch

The plan mentions human expert review but doesn't specify the protocol.

**Suggested fixes:**
- Make human expert evaluation the **primary** quality measure, not AI evaluation
- Specify: minimum 3 independent reviewers per proposal, recruited from relevant biomedical domain, blinded to source (human vs. AI), with inter-rater reliability metrics (Krippendorff's alpha or ICC)
- Use AI evaluation as a secondary/supplementary analysis only
- Add an explicit "AI self-preference" test: do models rate their own outputs higher than other models' outputs?
- Reference the growing literature on LLM evaluation biases (e.g., Zheng et al. 2023, "Judging LLM-as-a-Judge"; Panickssery et al. 2024)

---

### 2. METHODOLOGICAL IMPROVEMENTS

#### 2a. Part 1 Design: Persona Condition (Section "AI with Background + human scientists' persona")

The persona condition has several gaps:
- How does "taking on the persona" work in the prompt? Including 5 papers per author doesn't make the AI "become" that researcher
- This condition conflates persona simulation with knowledge injection — is the AI performing better because it "thinks like" the researcher or because it has more relevant literature?

**Suggested fixes:**
- Split into two sub-conditions: (a) literature-only (same papers, no persona instruction) and (b) literature + persona instruction. This disentangles the two effects.
- Alternatively, simplify and drop the persona framing — just call it "AI with author-specific literature priming"

#### 2b. Part 1 Design: Literature Condition

- Literature count ("n=10? 30? or?") is still unresolved
- Search strategy for PubMed is not specified (queries, date range, filters)
- The number of articles matters enormously for results

**Suggested fixes:**
- Pre-specify: use NCEMS call keywords to construct PubMed queries
- Retrieve top N articles by relevance (specify N)
- Use explicit date cutoff
- Filter to review articles + original research
- Report the actual search queries used as supplementary material



#### 2d. Analysis 2.2 (Novelty): Corpus Construction

PubMed corpus construction is critical but underspecified:
- What MeSH terms? How many abstracts? What date range?
- What if the corpus is biased toward certain subfields? The "novelty" measure would then be biased.

**Suggested fixes:**
- Report corpus statistics (N abstracts, date range, subfield distribution)
- Test sensitivity to corpus composition (e.g., leave-one-subfield-out)
- Provide the corpus construction code and parameters as supplementary material

#### 2e. Analysis 2.4 (Topic Modeling): Stability Concerns

- BERTopic with min_topic_size=3 on ~100-150 documents will produce unstable topics. Consider increasing to 5.
- The total proposal count of "144" (line 149) is unexplained — clarify derivation (23 human + 3* 23 for human = 92)
- Shannon entropy comparison between groups of different sizes needs normalization or rarefaction
- Chi-square test may have cells with expected count <5 — Fisher's exact should be the default at this sample size

---

### 3. MISSING ELEMENTS

#### 3a. Pre-registration

For a study making claims about AI capabilities, pre-registration (e.g., OSF, AsPredicted) would dramatically increase credibility. Top venues will ask about this. Pre-register:
- Primary hypotheses and outcomes
- Analysis pipeline (which tests, which corrections)
- Sample size justification


#### 3b. Reproducibility Plan

Specify and report:
- Exact model versions and API dates (e.g., GPT-4o-2024-05-13, Claude 3.5 Sonnet v2, Gemini 1.5 Pro)
- Temperature and sampling parameters for each generation
- Number of generation runs per condition (stochasticity matters)
- Seed/determinism settings where available
- Full prompts used (as supplementary material)
- Code and data availability statement

#### 3c. Visualization Plan

No mention of how results will be visualized. For publication, consider:
- **UMAP/t-SNE projections** of embeddings colored by source (human vs. AI) and condition
- **Violin plots** for distribution comparisons (diversity scores, novelty scores, quality scores)
- **Heatmaps** for topic × source matrices
- **Radar/spider charts** for multi-criteria quality scores
- **Sankey diagrams** showing topic flow between conditions
- **Forest plots** for effect sizes across analyses

---

### 4. PUBLICATION STRATEGY

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

### 5. RECOMMENDED PRIORITY ORDER

1. **Resolve the framing** — reframe as AI ideation capability, not head-to-head competition (§1a)
2. **Add power analysis** — justify sample sizes or be transparent about limitations (§1b)
3. **Design human expert evaluation protocol** — make this primary for quality (§1f)
4. **Validate embedding metrics** — expert calibration study (§1d)
5. **Pre-register** on OSF before running analyses (§3a)
6. **Specify all generation parameters** — model versions, temperatures, seeds (§3c)
7. **Resolve literature condition details** — PubMed query strategy, article counts (§2b)
8. **Add multiple comparisons strategy** across full study (§1c)
9. **Add visualization plan** (§3d)
10. **Address ethics/IRB** (§3b)



