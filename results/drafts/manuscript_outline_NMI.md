# Manuscript Outline: Nature Machine Intelligence

**Working Title:** Diverse but Not Novel: Embedding-Based Analysis Reveals Systematic Differences Between AI-Generated and Human-Written Research Proposals

**Target:** Nature Machine Intelligence (Article format)

**Format constraints:** Abstract ≤150 words; Main text 3,000–3,500 words (excl. Abstract, Methods, References, Figure legends); ≤6 main figures; ≤50 references; separate Results and Discussion sections.

---

## Abstract (≤150 words)

- Large language models are increasingly used to generate scientific ideas, but whether AI output matches the diversity and novelty of human researchers remains unclear.
- We compare 23 human-written and 69 AI-generated (GPT-5.2, Gemini 3 Pro, Claude Opus 4.5) research proposals responding to a real NSF funding call in molecular and cellular bioscience.
- Using BioLinkBERT-large embeddings and non-parametric statistical tests, we assess three complementary dimensions: within-group diversity, novelty relative to a 350-article PubMed corpus, and thematic/cluster composition.
- Key findings: (1) diversity varies dramatically by model (Claude > Human > Gemini > GPT-5.2); (2) human proposals are significantly more novel than AI (Cliff's d = −0.34, p = 0.014); (3) human and AI proposals occupy distinct semantic territories, confirmed by nearest-neighbor analysis, topic modeling, and clustering.
- AI models can generate varied output, but that variation operates within a different—and less novel—conceptual space than human scientists.

---

## 1. Introduction

- The promise of AI-assisted scientific ideation: LLMs as tools for brainstorming, hypothesis generation, and proposal writing
- Recent work on AI-generated research ideas (cite Si et al. 2024 "Can LLMs Generate Novel Research Ideas?"; Liang et al. 2024 on AI idea novelty ratings)
- Gap: most evaluations rely on human judges rating novelty/quality on Likert scales — subjective, expensive, small scale
  - No studies comparing AI and human proposals using quantitative, embedding-based analyses across multiple complementary dimensions
  - No studies using real-world funding call contexts where human proposals reflect genuine scientific stakes
- The distinction between diversity, novelty, and thematic content:
  - Diversity (within-group): Are the ideas varied?
  - Novelty (vs. literature): Are they genuinely new relative to the field?
  - Thematic composition: Do AI and human proposals explore the same conceptual regions?
  - These are independent dimensions — a model can score high on one and low on another
- Study framing: We do not claim a head-to-head competition. Human proposals were written under real funding stakes with domain expertise, lab capabilities, and collaborative context; AI proposals were generated in zero-stakes, zero-context conditions. We characterize AI ideation capability relative to a human baseline, not AI superiority/inferiority.
- Overview of this study: 23 human proposals + 69 AI proposals (3 frontier models × 23 each) for the NSF NCEMS call, analyzed via BioLinkBERT embeddings across three dimensions

---

## 2. Results

### 2.1 Within-Group Diversity Varies Dramatically by Model

Pairwise cosine distances within each group reveal a striking range across AI models, with no single "AI diversity" story.

**Pairwise diversity.** We computed all n(n−1)/2 pairwise cosine distances within each group's BioLinkBERT embeddings (1,024 dimensions). Human proposals showed moderate internal diversity (mean pairwise distance = 0.066, SD = 0.017). Among AI models, Claude Opus 4.5 was the only model significantly *more* diverse than humans (mean = 0.340, Cliff's δ = +0.25, p < 0.001), though with a highly skewed distribution (median = 0.072, long tail to 0.8). GPT-5.2 exhibited extreme homogeneity (mean = 0.022, Cliff's δ = −1.00, p < 0.001) — its proposals were near-identical in embedding space. Gemini 3 Pro was intermediate (mean = 0.096, Cliff's δ = −0.73, large effect, p < 0.001). All AI combined showed only a small negative effect (δ = −0.29), masking dramatic between-model differences.

**Centroid dispersion.** Distances from each proposal to its group centroid confirmed the same ranking. Claude showed near-maximum dispersion (mean distance to centroid = 0.179, δ = +0.99, p < 0.001). GPT-5.2 was maximally clustered (mean = 0.010, δ = −1.00, p < 0.001; variance = 5 × 10⁻⁶ vs. human variance = 8.5 × 10⁻⁵). Gemini was less dispersed than humans (mean = 0.047, δ = −0.82, p < 0.001). Notably, the all-AI-combined comparison was not significant (δ = −0.17, p = 0.22), illustrating how aggregation across models produces misleading null results: Claude's high dispersion offsets GPT-5.2's near-zero dispersion.

**Nearest-neighbor analysis.** In the combined 92-proposal space, we identified each proposal's nearest neighbor and flagged proposals in the top 10% of nearest-neighbor distances as outliers. GPT-5.2 paradoxically had the highest outlier rate (26.1%) despite the lowest internal diversity — its tight, isolated cluster sits far from all other proposals. Claude had zero outliers (0%) despite the highest diversity, forming subclusters that are individually tight but spread across the space. Humans produced 13.0% outliers: genuine lone-wolf ideas with no close neighbor.

A critical finding: 100% of AI proposals' nearest neighbors were other AI proposals. No AI proposal was closest to any human proposal. Among Claude proposals, 95.7% had a Claude nearest neighbor. Among humans, 43.5% had a human nearest neighbor and 56.5% had an AI nearest neighbor — humans occupy shared territory, but AI does not reciprocate.

### 2.2 Human Proposals Are More Novel Than AI

Novelty was measured as the mean cosine distance from each proposal's title-and-abstract embedding to its k = 10 nearest neighbors in a reference corpus of 350 PubMed articles spanning seven search queries relevant to the NCEMS call (see Methods). We embedded only titles and abstracts (not full proposal text) to ensure a fair comparison with the PubMed abstracts.

Human proposals were significantly more novel than AI combined (human mean = 0.151 vs. AI mean = 0.117; Cliff's δ = −0.34, medium effect, p = 0.014). Among individual models, Claude was closest to human novelty (δ = −0.21, small effect, p = 0.22, not significant). Both GPT-5.2 (δ = −0.40, p = 0.020) and Gemini (δ = −0.42, p = 0.016) were significantly less novel than humans, with medium effect sizes.

The most novel proposal overall was a human submission on "Cytokinetic Bottlenecks of Heat Waves" (novelty score 0.260). The least novel AI proposal was a Gemini submission on antibiotic resistance (score 0.059), nearly overlapping published work.

UMAP projection of proposals alongside the 350 PubMed articles provided qualitative confirmation: human proposals sit at the periphery of the literature cluster, while AI proposals concentrate closer to dense literature regions — particularly GPT-5.2 and Gemini. Claude proposals showed more scatter, with some overlapping human territory, consistent with its non-significant novelty difference.

Importantly, novelty and diversity are independent dimensions. Claude produces the most diverse proposals but is only moderately novel, suggesting its spread is within AI-typical semantic territory. Humans are moderately diverse but most novel — exploring territory that the published literature does not cover.

### 2.3 Human and AI Proposals Occupy Distinct Semantic Territories

**Topic modeling.** LDA with k = 5 topics and strong Dirichlet priors (α = β = 0.5, stability-validated across 10 random seeds) revealed complete thematic separation. All 23 human proposals mapped to a single dominant topic (Topic 3: evolutionary and species-level biology). All 69 AI proposals distributed across the other four topics (mechanical/structural, transport/diffusion, imaging/perturbation, splicing/allosteric mechanisms). The overall chi-square permutation test was highly significant (p < 0.0001). Per-topic Fisher's exact tests with FDR correction confirmed: Topic 3 was exclusively human (p < 0.0001); Topics 1, 4, and 5 were significantly AI-overrepresented (p < 0.05). Subsample validation (drawing n = 23 AI proposals 1,000 times) confirmed robustness for Topics 1 and 3 (> 98% of subsamples significant) but not Topic 2 (18.5%).

We note that perfect separation is a potential red flag: LDA may capture systematic stylistic or templating artifacts rather than genuine scientific themes. Human entropy = 0 (all proposals in one topic) is suspicious. These results are explicitly exploratory and require expert validation.

**Cluster segregation.** Gaussian Mixture Model clustering (k = 3, selected by BIC; full covariance) yielded three clusters with asymmetric composition: Cluster 0 (n = 27, 100% AI), Cluster 1 (n = 7, 100% AI), and Cluster 2 (n = 58, 40% human, 60% AI). All 23 human proposals landed in a single mixed cluster, while AI proposals spread across all three. NMI = 0.197 (p < 0.0001 by permutation): cluster identity predicts source better than chance. The between-group/within-group distance ratio was 1.085 (p = 0.004): human and AI proposals were measurably more distant from each other than from their own group. ARI was −0.035 (p = 0.86), expected given the unbalanced group sizes.

**Convergence across methods.** Three independent methods — nearest-neighbor analysis (100% AI-AI nearest neighbors), LDA topic modeling (complete topic separation), and GMM clustering (two AI-only clusters, NMI p < 0.0001) — converge on the same conclusion: human and AI proposals occupy different regions of semantic space.

---

## 3. Discussion

- **Summary of convergent findings**: AI models can generate internally diverse proposals, but that diversity operates within a conceptual space that is systematically different from — and less novel than — the space human scientists occupy
- **The diversity–novelty dissociation**:
  - Claude is the most diverse model but only moderately novel — high diversity within AI-typical territory
  - Humans are moderately diverse but most novel — exploring beyond what the published literature covers
  - This dissociation cautions against using diversity alone as a proxy for creativity or scientific originality
- **Model-specific behaviors suggest different failure modes**:
  - GPT-5.2: mode collapse — generates near-identical proposals (Cliff's δ = −1.00)
  - Gemini: moderate diversity but low novelty — varied restatements of known ideas
  - Claude: high diversity with subclustering — possible topic sampling from distinct training data regions, but not genuinely novel territory
- **Semantic segregation and what it means**:
  - 100% AI-AI nearest neighbors across all models — systematic framing differences
  - May reflect training data distribution, prompt formatting, or systematic differences in how AI approaches scientific writing
  - Implication: AI proposals may explore a parallel but distinct idea space, limiting their utility as direct substitutes for human ideation
- **AI as complement, not replacement**:
  - Human novelty advantage suggests AI is better positioned for extending existing lines of inquiry
  - Humans contribute genuinely novel framings — perspectives not derivable from training data alone
  - Practical recommendation: use AI to broaden the space of conventional ideas, then rely on human expertise to push boundaries
- **Relation to prior work**:
  - Compare with Si et al. 2024 (human judges rated AI ideas as more novel — possible mismatch with quantitative measures)
  - Compare with Liang et al. 2024 (reviewer biases in novelty judgments)
  - Our embedding-based approach provides scalable, reproducible metrics complementary to subjective ratings
- **Limitations** (must be prominently addressed):
  - Single funding call (NCEMS) — generalizability to other domains unknown
  - Small sample (n = 23 human, n = 69 AI) — limited statistical power for subtle effects; no formal power analysis
  - Embedding distance ≠ conceptual diversity. BioLinkBERT may conflate stylistic with semantic differences; expert validation needed
  - Novelty score conflates genuine novelty with incoherence — distance from literature could mean a genuinely new idea OR a poorly formulated one
  - Topic separation may be an artifact of writing style or prompt templating, not genuine thematic differences; LDA results are exploratory
  - Population mismatch: humans wrote under real funding stakes with domain expertise and lab capabilities; AI under zero-stakes, zero-context conditions. This confounds any direct comparison
  - No quality evaluation yet — diversity and novelty do not imply good science
  - AI model versions are a snapshot; rapid model improvements may change results
- **Future directions**:
  - Human expert evaluation of proposal quality (blinded, with inter-rater reliability)
  - Augmented AI conditions: literature-enriched prompts, persona-based generation
  - Construct validation: domain expert ratings of proposal pairs correlated with embedding distances
  - Multi-call replication across different funding agencies and scientific domains
  - Style-controlled analysis: embed keyword/concept extractions only, stripping writing style

---

## 4. Methods

### 4.1 Data

**Funding call.** The NSF National Synthesis Center for Emergence in Molecular and Cellular Sciences (NCEMS) issued a call for proposals on emergence in molecular and cellular biosciences. The call specified research requirements, evaluation criteria, and areas of interest.

**Human proposals.** 23 proposals were submitted by teams of human scientists across two annual cohorts (Year 1: n = 12; Year 2: n = 11) responding to the same NCEMS call. These represent real submissions written under genuine funding stakes, with domain expertise, lab capabilities, and collaborative context. [Note: cohort effects between Y1 and Y2 should be tested — e.g., Kolmogorov-Smirnov test on embedding distributions — before pooling.]

**AI proposals.** Three frontier large language models — GPT-5.2 (OpenAI), Gemini 3 Pro Preview (Google DeepMind), and Claude Opus 4.5 (Anthropic) — each generated 23 proposals. [Specify exact model version identifiers, API dates, temperature settings, and seed parameters.] All models received the same prompt containing the NCEMS call for proposals, background information about NCEMS, and evaluation criteria — the same materials available to human applicants. [Full prompts to be provided as supplementary material.]

### 4.2 Embedding Pipeline

All proposals were encoded using BioLinkBERT-large, a 340M-parameter biomedical language model pretrained on PubMed with citation-link structure, ranked #1 on the BLURB biomedical NLP benchmark as of February 2026. Each proposal was split into overlapping 400-word chunks and encoded into 1,024-dimensional vectors, which were averaged to produce a single embedding per proposal. For novelty analysis, only titles and abstracts were embedded (not full proposal text) to ensure comparability with PubMed abstracts.

### 4.3 Part I: Within-Group Diversity Analysis

Three complementary metrics were computed:

**Pairwise cosine distances.** For each group (Human, Claude, Gemini, GPT-5.2, All AI), all n(n−1)/2 pairwise cosine distances were computed between proposal embeddings. Group distributions were compared using Mann-Whitney U tests with Cliff's delta effect sizes (thresholds: < 0.147 negligible, < 0.33 small, < 0.474 medium, ≥ 0.474 large). Permutation tests (10,000 iterations) provided robust p-values.

**Centroid dispersion.** The centroid (mean embedding vector) was computed for each group. Each proposal's cosine distance to its group centroid was calculated. Distributions of centroid distances were compared using the same statistical framework.

**Nearest-neighbor outlier detection.** All 92 proposals (23 human + 69 AI) were combined. For each proposal, the nearest neighbor (by cosine distance) was identified. Proposals in the top 10% of nearest-neighbor distances were classified as outliers. We recorded the group identity of each proposal's nearest neighbor to assess cross-group proximity.

### 4.4 Part II: Novelty Analysis

**Literature corpus.** 350 PubMed articles were retrieved using seven targeted search queries derived from the NCEMS call: emergent properties in molecular/cellular biology (59 articles), mesoscale biology and biomolecular organization (49), biomolecular condensates and phase separation (49), multi-omics data integration (50), AI/ML in molecular and cellular biology (59), systems biology and network analysis (44), and protein self-assembly and supramolecular organization (40). Mean abstract length: 1,351 characters. All abstracts were embedded using the same BioLinkBERT pipeline.

**Novelty score.** For each proposal, the k = 10 nearest neighbors in the PubMed corpus were identified by cosine distance. The novelty score is the mean cosine distance to these 10 nearest neighbors. Higher scores indicate greater distance from published literature. Only title-and-abstract embeddings were used for proposals to ensure fair comparison with PubMed abstracts.

**Statistical comparison.** Novelty score distributions were compared between groups using Mann-Whitney U tests, Cliff's delta, and permutation tests (10,000 iterations).

### 4.5 Part III: Thematic and Cluster Analysis

**Topic modeling.** Latent Dirichlet Allocation (LDA) was applied to TF-IDF representations of proposal titles and abstracts (stop words removed, min_df = 2, max_df = 0.7). We used k = 5 topics with strong Dirichlet priors (α = 0.5, β = 0.5) to stabilize topics given the small sample size. Stability was validated across 10 random seeds. Per-document topic distributions (soft assignment) were computed. [Report topic coherence (c_v metric) and perplexity.]

**Topic distribution comparison.** The overall distribution was tested using a chi-square permutation test (10,000 permutations). Per-topic tests used Fisher's exact test with Benjamini-Hochberg FDR correction at q = 0.10 (exploratory threshold). To account for the 3:1 group size imbalance, AI proposals were subsampled to n = 23 in 1,000 iterations, and the proportion of subsamples yielding significance was reported.

**Cluster analysis.** Gaussian Mixture Model (GMM) clustering was applied to full-text BioLinkBERT embeddings. The number of clusters was selected by BIC across k = 3–8 (k = 3 optimal). Covariance type: full. Cluster composition (% human, % AI by model) was computed.

**Segregation metrics.** Normalized Mutual Information (NMI) and Adjusted Rand Index (ARI) were computed between cluster labels and source labels (human vs. AI). Both were tested against permutation null distributions (10,000 iterations). Between-group vs. within-group cosine distance ratios were computed with permutation tests.

### 4.6 Multiple Testing Correction

FDR correction (Benjamini-Hochberg, q = 0.05) was applied within each analysis family: diversity (12 tests: 3 metrics × 4 comparisons), novelty (4 tests: 1 metric × 4 comparisons). Thematic/cluster analyses used FDR q = 0.10 (exploratory). Raw p-values are reported in supplementary tables.

### 4.7 Visualization

UMAP projections (2D) were computed for embedding space visualization, with t-SNE as a confirmatory check. All statistical analyses were implemented in Python using scipy, scikit-learn, and gensim.

---

## Figures (≤6 main, ≤10 Extended Data)

| # | Figure | Content |
|---|--------|---------|
| 1 | **Study design schematic** | Overview of the 23 human + 69 AI proposals, embedding pipeline, and three analysis dimensions |
| 2 | **Pairwise diversity and centroid dispersion** | (a) Violin/box plots of pairwise cosine distances by group with Cliff's δ annotations; (b) Centroid dispersion distributions; (c) Effect size forest plot |
| 3 | **Embedding space visualization** | UMAP 2D projection of 92 proposals, colored by source, with centroids and outlier annotations |
| 4 | **Novelty analysis** | (a) Novelty score distributions by group with statistical annotations; (b) UMAP of proposals + 350 PubMed articles showing distance from literature |
| 5 | **Topic distribution** | (a) Stacked bar chart of topic prevalence by group; (b) Heatmap of Fisher's exact test results (FDR-corrected); (c) Per-topic subsample validation |
| 6 | **Cluster segregation** | (a) GMM cluster composition (% human/AI per cluster); (b) UMAP colored by cluster; (c) Nearest-neighbor origin analysis (% same-source NN) |

**Extended Data candidates:**
- ED1: Literature corpus statistics (articles per query, date distribution)
- ED2: t-SNE confirmatory projections
- ED3: Full statistical tables for all comparisons
- ED4: LDA topic word distributions and coherence scores
- ED5: BIC curve for GMM cluster selection
- ED6: Sensitivity analysis for novelty k parameter (k = 5, 10, 20, 50)

---

## Supplementary Information

- Full prompts used for AI proposal generation
- Complete PubMed search queries and article metadata
- Per-proposal novelty scores and topic assignments
- Raw p-values for all statistical tests
- LDA topic word lists and coherence metrics
- Cohort analysis (Year 1 vs. Year 2 human proposals)
- Code and data availability statement

---

## References (key citations to include, ≤50 total)

1. Si, C. et al. "Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers." (2024)
2. Liang, W. et al. "Can large language models provide useful feedback on research papers?" (2024)
3. Yasunaga, M. et al. "LinkBERT: Pretraining Language Models with Document Links." ACL (2022) — BioLinkBERT
4. Lu, C. et al. "AI-Driven Scientific Discovery." Nature (2024)
5. Krenn, M. et al. "On scientific understanding with artificial intelligence." Nature Reviews Physics (2022)
6. Zheng, L. et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS (2023)
7. Panickssery, A. et al. "LLM Evaluators Recognize and Favor Their Own Generations." (2024)
8. Blei, D.M. et al. "Latent Dirichlet Allocation." JMLR (2003)
9. McInnes, L. et al. "UMAP: Uniform Manifold Approximation and Projection." (2018)
10. Cliff, N. "Dominance statistics: Ordinal analyses to answer ordinal questions." Psychological Bulletin (1993)
11. Benjamini, Y. & Hochberg, Y. "Controlling the false discovery rate." JRSS-B (1995)
12. [Additional references on AI scientific ideation, embedding-based novelty measurement, science of science]

---

## Notes for Authors

### Unresolved items before submission
- [ ] Specify exact model versions, API dates, temperature settings, and seeds
- [ ] Test for cohort effects between Year 1 and Year 2 human proposals before pooling
- [ ] Conduct construct validation: have domain experts rate conceptual similarity of proposal pairs and correlate with embedding distances
- [ ] Complete human expert evaluation of proposal quality (blinded)
- [ ] Add formal power analysis or minimum detectable effect size calculation
- [ ] Report LDA topic coherence (c_v) and perplexity values
- [ ] Sensitivity analysis: vary novelty k parameter (5, 10, 20, 50) and report robustness
- [ ] Consider style-controlled analysis (embed keyword/concept extractions only)
- [ ] Ethics/IRB statement for use of human proposal data
- [ ] Pre-registration on OSF (if feasible at this stage)
- [ ] Data and code availability statement
