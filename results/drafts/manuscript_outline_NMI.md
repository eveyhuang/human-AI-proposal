# Manuscript Outline: Nature Machine Intelligence

**Working Title:** Diverse but Not Novel: Embedding-Based Analysis Reveals Systematic Differences Between AI-Generated and Human-Written Research Proposals

**Target:** Nature Machine Intelligence (Article format)

**Format constraints:** Abstract ≤150 words; Main text 3,000–3,500 words (excl. Abstract, Methods, References, Figure legends); ≤6 main figures; ≤50 references; separate Results and Discussion sections.

---

## Abstract (≤150 words)

- Large language models are increasingly used to generate scientific ideas, but whether AI output matches the diversity, novelty, and quality of human researchers remains unclear.
- We compare 23 human-written and 69 AI-generated (GPT-5.2, Gemini 3 Pro Preview, Claude Opus 4.5) research proposals responding to a real NSF funding call in molecular and cellular bioscience.
- Using BioLinkBERT-large embeddings and non-parametric statistical tests, we assess four complementary dimensions: within-group diversity, novelty relative to a 350-article PubMed corpus, thematic/cluster composition, and proposal quality under AI evaluation.
- Key findings: (1) diversity varies dramatically by model (Claude >> Human > Gemini ≈ Human >> GPT-5.2); (2) human proposals are significantly more novel than AI (Cliff's d = −0.34, p = 0.014); (3) human and AI proposals occupy distinct semantic territories, even after style adjustment; (4) GPT-5.2 proposals receive substantially higher quality scores under AI evaluation, even after removing self-preference bias.
- AI models can generate varied output, but that variation operates within a different—and less novel—conceptual space than human scientists.

---

## 1. Introduction

- The promise of AI-assisted scientific ideation: LLMs as tools for brainstorming, hypothesis generation, and proposal writing
- Recent work on AI-generated research ideas (cite Si et al. 2024 "Can LLMs Generate Novel Research Ideas?"; Liang et al. 2024 on AI idea novelty ratings)
- Gap: most evaluations rely on human judges rating novelty/quality on Likert scales — subjective, expensive, small scale
  - No studies comparing AI and human proposals using quantitative, embedding-based analyses across multiple complementary dimensions
  - No studies using real-world funding call contexts where human proposals reflect genuine scientific stakes
- The distinction between diversity, novelty, thematic content, and quality:
  - Diversity (within-group): Are the ideas varied?
  - Novelty (vs. literature): Are they genuinely new relative to the field?
  - Thematic composition: Do AI and human proposals explore the same conceptual regions?
  - Quality: Are proposals scientifically rigorous, relevant, and fundable?
  - These are independent dimensions — a model can score high on one and low on another
- Study framing: We do not claim a head-to-head competition. Human proposals were written under real funding stakes with domain expertise, lab capabilities, and collaborative context; AI proposals were generated in zero-stakes, zero-context conditions. We characterize AI ideation capability relative to a human baseline, not AI superiority/inferiority.
- Overview of this study: 23 human proposals + 69 AI proposals (3 frontier models × 23 each) for the NSF NCEMS call, analyzed via BioLinkBERT embeddings across four dimensions

---

## 2. Results

### 2.1 Within-Group Diversity Varies Dramatically by Model

Pairwise cosine distances within each group reveal a striking range across AI models, with no single "AI diversity" story.

**Pairwise diversity.** We computed all n(n−1)/2 pairwise cosine distances within each group's BioLinkBERT embeddings (1,024 dimensions). Human proposals showed moderate internal diversity (mean pairwise distance = 0.066, SD = 0.018; median = 0.064). Among AI models, Claude Opus 4.5 was substantially *more* diverse than humans (Cliff's δ = +1.00, mean difference vs. human = +0.274, 95% CI [0.209, 0.344], p < 1×10⁻⁸). Gemini 3 Pro showed no significant difference from humans at the proposal level (δ = +0.30, mean diff = +0.030, 95% CI [−0.001, 0.091], p = 0.083). GPT-5.2 exhibited extreme homogeneity (Cliff's δ = −1.00, mean diff = −0.045, 95% CI [−0.049, −0.041], p < 1×10⁻⁸) — its proposals were near-identical in embedding space. All AI combined showed significantly higher proposal-level diversity than humans (δ = +1.00, mean diff = +0.107, 95% CI [0.068, 0.150], Holm-adjusted permutation p = 0.015), though this aggregate statistic masks dramatic between-model differences.

**Centroid dispersion.** Distances from each proposal to its group centroid confirmed the same ranking. Human baseline: mean = 0.032, median = 0.029, SD = 0.009. Claude showed near-maximum dispersion (mean distance to centroid = 0.179; δ = +0.99, p < 0.001; proposals spread widely around center). GPT-5.2 was maximally clustered (mean = 0.010, δ = −1.00, p < 0.001; variance = 5 × 10⁻⁶ vs. human variance = 8 × 10⁻⁵; near-zero spread: all proposals essentially the same point in embedding space). Gemini was less dispersed than humans (mean = 0.047; median = 0.018; SD = 0.135; δ = −0.82, p < 0.001), though with some high-distance outlier proposals skewing the mean. Notably, the all-AI-combined comparison was not significant (δ = −0.17, p = 0.22), illustrating how aggregation across models produces misleading null results: Claude's high dispersion offsets GPT-5.2's near-zero dispersion.

**Nearest-neighbor analysis.** In the combined 92-proposal space, we identified each proposal's nearest neighbor and flagged proposals in the top 10% of nearest-neighbor distances as outliers. Claude had the highest outlier rate (26.1%) consistent with its large centroid dispersion — many proposals fall far from their nearest neighbor in the global space. Human proposals produced genuine outliers (13.0%): genuine lone-wolf ideas with no close neighbor. Gemini produced few outliers (4.3%). GPT-5.2 had zero outliers (0%) and the smallest nearest-neighbor distances (mean = 0.014), as its near-identical proposals are always extremely close to another GPT-5.2 proposal.

A critical finding: 100% of AI proposals' nearest neighbors were other AI proposals. No AI proposal was closest to any human proposal. Among GPT-5.2 proposals, 95.7% had a GPT-5.2 nearest neighbor. Among humans, 43.5% had a human nearest neighbor and 56.5% had an AI nearest neighbor — humans occupy shared territory, but AI does not reciprocate.

### 2.2 Human Proposals Are More Novel Than AI

Novelty was measured as the mean cosine distance from each proposal's title-and-abstract embedding to its k = 10 nearest neighbors in a reference corpus of 350 PubMed articles spanning seven search queries relevant to the NCEMS call (see Methods). We embedded only titles and abstracts (not full proposal text) to ensure a fair comparison with the PubMed abstracts.

Human proposals were significantly more novel than AI combined (human mean = 0.151 vs. AI mean = 0.117; Cliff's δ = −0.34, medium effect, p = 0.014). Among individual models, GPT-5.2 was closest to human novelty (δ = −0.21, p = 0.219, not significant after Holm correction). Both Claude (δ = −0.40, p = 0.020) and Gemini (δ = −0.42, p = 0.016) were significantly less novel than humans, with medium-to-large effect sizes.

The most novel proposal overall was a human submission on "Cytokinetic Bottlenecks of Heat Waves" (novelty score = 0.260). The least novel AI proposal was a Gemini submission on antibiotic resistance (score = 0.059), nearly overlapping published work.

UMAP projection of proposals alongside the 350 PubMed articles provided qualitative confirmation: human proposals sit at the periphery of the literature cluster, while AI proposals concentrate closer to dense literature regions. GPT-5.2's tight internal cluster maps onto well-published territory (high internal similarity + low novelty = AI re-deriving the same ideas from training data). Claude proposals show more scatter, consistent with its non-significant novelty deficit being the smallest among AI models.

Importantly, novelty and diversity are independent dimensions. Claude produces the most diverse proposals but is significantly less novel than humans, suggesting its spread is within AI-typical semantic territory. GPT-5.2 is the least diverse (mode collapse) yet not significantly less novel — repetitively exploring territory that the published literature has not fully mapped.

### 2.3 Human and AI Proposals Occupy Distinct Semantic Territories

**Topic modeling.** LDA with k = 5 topics and strong Dirichlet priors (α = β = 0.5, stability-validated across 10 random seeds) revealed strong but not complete thematic separation. Topic 3 (evolutionary and species-level biology) was heavily human-dominated (21 human, 3 AI proposals; OR = 231, FDR-corrected q < 0.001). Topics 1 and 4 were significantly AI-overrepresented (q < 0.01). Topics 2 and 5 showed no significant differential representation after FDR correction. The overall chi-square permutation test was highly significant (p < 0.0001). Subsample validation (drawing n = 23 AI proposals 1,000 times) confirmed robustness for Topics 1, 3, and 4 (> 98% of subsamples significant). Human topic entropy = 0.448 (not zero, reflecting the 2 human proposals in Topic 5); AI subsampled entropy ≈ 1.99, indicating much broader thematic spread.

We note that the near-complete separation is a potential indicator of stylistic or templating artifacts rather than purely genuine scientific themes (see Section 2.4 on style controls). These results are explicitly exploratory and require expert validation.

**Cluster segregation.** Gaussian Mixture Model clustering (k = 3, selected by BIC; full covariance) yielded three clusters with asymmetric composition: Cluster 0 (n = 27, 100% AI), Cluster 1 (n = 7, 100% AI), and Cluster 2 (n = 58, 40% human, 60% AI). All 23 human proposals landed in a single mixed cluster, while AI proposals spread across all three. NMI = 0.197 (p < 0.0001 by permutation): cluster identity predicts source better than chance. The between-group/within-group distance ratio was 1.085 (p = 0.004): human and AI proposals were measurably more distant from each other than from their own group. ARI = −0.035 (p = 0.86), expected given the unbalanced group sizes.

**Convergence across methods.** Three independent methods — nearest-neighbor analysis (100% AI-AI nearest neighbors), LDA topic modeling (strong topic separation, chi-square p < 0.0001), and GMM clustering (two AI-only clusters, NMI p < 0.0001) — converge on the same conclusion: human and AI proposals occupy different regions of semantic space.

### 2.4 Stylistic Signals Strongly Separate Sources, But Semantic Segregation Persists After Style Adjustment

**Style-only baseline.** We constructed a style feature set capturing purely structural and lexical properties of each proposal (word/sentence/paragraph count, function-word rates, punctuation patterns, readability scores, hedging/stance markers, section header counts, and type-token ratio) without domain-semantic content. A regularized logistic regression classifier trained on style features alone achieved AUROC = 1.000 ± 0.000 and balanced accuracy = 1.000 (permutation test p = 0.001, null AUROC = 0.505 ± 0.098). Human and AI proposals are perfectly separable by writing style alone, motivating style-adjusted sensitivity analyses.

**Style-adjusted centroid dispersion.** We residualized BioLinkBERT embeddings on style features (fit y_raw ~ style features, subtract predicted component, analyze adjusted distances). After removing the linearly style-predictable embedding variance, the AI-vs-human centroid dispersion coefficient remains positive and significant (+0.049, permutation p = 0.0002). Per-model effects in residual space: Gemini δ = −0.611 (p = 4.0 × 10⁻⁴), Claude δ = +0.123 (not significant), GPT-5.2 δ = −0.172 (not significant).

**Style-adjusted nearest-neighbor analysis.** After style residualization, human/AI neighborhood asymmetry persists: 94.2% of AI proposals still have a same-source nearest neighbor in the style-adjusted embedding space (reduced from 100%, but still strongly asymmetric). Style adjustment substantially changes outlier profiles: Claude's outlier rate drops from 26.1% to 0%; GPT-5.2's outlier rate increases from 0% to 30.4% (becoming the most isolated group in style-corrected space); Human and Gemini rates remain near 13% and 0%, respectively. Style leakage into principal components is substantially reduced (mean |corr(style, PC)|: 0.204 → 0.041), confirming effective adjustment. The residual semantic segregation — not attributable to the measured style features — indicates content-level differences beyond writing style.

### 2.5 AI-Evaluated Proposal Quality: Instrument Validation, Group Differences, and Evaluator Bias

**2.5.1 R1 — Proxy validity: Are AI reviews aligned with human expert reviews?**

Twelve Year 1 human proposals were reviewed by both expert human panels and all three AI models, enabling direct comparison across three pair types: Human–Human (HH), Human–AI (HAI), and AI–AI (AIAI). Scores were averaged to the proposal level (n = 12) before testing to avoid pairwise pseudo-replication. Paired Wilcoxon signed-rank tests with BH-FDR correction were the primary inference.

Human–AI cosine similarity was not significantly lower than Human–Human similarity (q = 0.237, δ = −0.29, small, not significant) — AI reviews are not detectably more dissimilar from human expert reviews than human reviews are from each other. However, AI–AI similarity was dramatically higher than Human–Human (Wilcoxon p = 0.016, q = 0.025, δ = 0.58, large) and than Human–AI (p = 0.00049, q < 0.001, δ = 0.93, large). AI models converge on far more similar review language than human experts do, suggesting the AI judge panel lacks the heterogeneity of human expert panels, compressing the diversity of critical perspectives.

**2.5.2 R2 — Proposal quality under AI evaluation**

Before pooling the two human cohorts, we tested for cohort effects across 8 scored dimensions. Year 1 (n = 12) and Year 2 (n = 11) proposals were statistically equivalent on 7 of 8 criteria (all q > 0.05). The single exception was Data Identification (Y1 mean = 3.36, Y2 mean = 4.06, q = 0.005, δ = −0.69, large), likely reflecting evolved grant-writing norms. Pooling as "human-all" is justified for overall quality comparisons, with this cohort effect noted.

Under pooled AI evaluation (all 3 evaluators), human-all mean overall score = 3.65. GPT-5.2 proposals scored substantially higher (mean = 4.39, q < 0.001, robust bootstrap human−GPT = −0.74, 95% CI [−0.91, −0.57]). Gemini proposals scored higher (mean = 4.12, q < 0.001, human−Gemini = −0.47, 95% CI [−0.68, −0.23]). Claude proposals were statistically indistinguishable from human proposals (mean = 3.50, q = 0.358, human−Claude = +0.15, 95% CI [−0.11, +0.43]). Criterion-level analysis reveals heterogeneous patterns: all AI models score near-ceiling (5.0) on Relevance while humans average ~3.75 (δ ≈ −0.87 large for all models); humans score significantly *higher* than Claude on Rigor (δ = +0.48) and Scope/Timeline (δ = +0.58).

**IMPORTANT CAVEAT:** These pooled scores include self-evaluations (AI evaluating its own proposals). R3 (§2.5.3) demonstrates that self-preference bias is large and model-divergent.

**2.5.3 R3 — Evaluator bias: leniency differences and self-preference**

Kruskal–Wallis test across all 276 AI reviews confirms that evaluator identity is a highly significant predictor of score (H = 70.034, p = 6.2 × 10⁻¹⁶). Gemini evaluator is most lenient (mean = 4.32), followed by Claude (3.80), then GPT-5.2 (3.62, most strict). The 0.71-point spread between Gemini and GPT evaluator means exceeds the nominal human–GPT author group difference.

Self-preference analysis reveals model-divergent biases: GPT evaluator shows strong self-inflation (δ = +0.987, q < 0.001; own proposals mean = 4.08 vs. others = 3.57), concentrated in Rigor (+1.33 mean diff), Data Identification (+0.93), and Open Science (+0.80). Claude evaluator shows strong self-deprecation (δ = −0.581, q < 0.001; own proposals mean = 3.54 vs. others = 4.10), concentrated in Rigor (−0.98) and Scope/Timeline (−0.67). Gemini evaluator shows no significant self-preference (δ = +0.128, q = 0.327). Fixed-effects regression including proposal identity, evaluator, and author group confirms that self-preference persists after controlling for proposal quality and evaluator severity (+0.33 points net for GPT self-evaluation, HC3-robust SEs).

**Sensitivity analyses.** Two controlled reruns test robustness to the identified confounds:

*Sensitivity 1 (cross-evaluator only):* Removing self-evaluations for AI authors (each AI proposal scored only by the 2 models that did not write it). GPT advantage remains highly significant (mean = 4.55, q < 0.001, δ = −1.00 large; human−GPT bootstrap = −0.89, 95% CI [−1.06, −0.73]). Gemini advantage disappears (q = 0.070, marginal; human−Gemini bootstrap = −0.19, 95% CI [−0.40, +0.02], ns) — Gemini's elevated baseline score was substantially driven by self-evaluation inflation. Claude remains statistically equivalent to humans (q = 0.262, ns).

*Sensitivity 2 (Gemini-only evaluator):* Restricting to Gemini reviews eliminates leniency-mix bias. Claude proposals now score significantly *lower* than human proposals (Claude mean = 3.58 vs. human mean = 4.23, q = 0.029; human−Claude bootstrap = +0.65, 95% CI [+0.27, +1.03]). GPT proposals remain elevated above humans (mean = 4.83, q < 0.001). Note: Gemini evaluates its own proposals in this analysis, so Gemini results remain potentially inflated.

**Summary of R1–R3:** AI reviews pass the basic proxy-validity threshold (Human–AI textual similarity ≈ Human–Human) but compress critique diversity. GPT-5.2 proposals are rated substantially higher than human proposals by cross-evaluators (robust finding). Gemini's advantage is an artifact of self-evaluation inflation. Claude proposals are equivalent to or fall below human quality depending on evaluator configuration.

---

## 3. Discussion

- **Summary of convergent findings**: AI models can generate internally diverse proposals, but that diversity operates within a conceptual space that is systematically different from — and less novel than — the space human scientists occupy; AI-evaluated quality is model-specific, with GPT-5.2 proposals robustly outscoring humans under external AI evaluation while Claude proposals are comparable to or below human quality
- **The diversity–novelty dissociation**:
  - Claude is the most diverse model but significantly less novel than humans — high diversity within AI-typical territory
  - GPT-5.2 shows mode collapse (δ = −1.00) yet is not significantly less novel — repetitively but consistently exploring a somewhat unexplored niche
  - Humans are moderately diverse but most novel — exploring beyond what the published literature covers
  - This dissociation cautions against using diversity alone as a proxy for creativity or scientific originality
- **Model-specific behaviors suggest different failure modes**:
  - GPT-5.2: mode collapse — generates near-identical proposals, occupying a tight isolated cluster in embedding space; paradoxically maintains moderate novelty scores
  - Gemini: near-human pairwise diversity but significantly less novel — varied restatements of well-mapped conceptual territory; quality advantage disappears under fair evaluation (cross-evaluator only)
  - Claude: highest diversity with clear subclustering — possible topic sampling from distinct training data regions, but not genuinely novel territory; quality comparable to humans under fair evaluation, falls below under strict single-evaluator
- **The role of writing style**:
  - Perfect style separability (AUROC = 1.00) confirms that AI and human proposals differ profoundly in how they are written, not just what they propose
  - However, style adjustment reduces but does not eliminate semantic segregation (94.2% AI same-group NN after adjustment vs. 100% before) — content-level differences exist beyond style
  - The style confound means all embedding-based differences should be interpreted cautiously; expert conceptual validation is essential before strong claims
- **Semantic segregation and what it means**:
  - 100% AI-AI nearest neighbors across all models before style adjustment; 94.2% after — systematic framing differences persist beyond writing style
  - May reflect training data distribution, prompt formatting, or systematic differences in how AI approaches scientific writing and ideation
  - Implication: AI proposals may explore a parallel but distinct idea space, limiting their utility as direct substitutes for human ideation
- **AI quality as evaluated by AI — a bounded proxy**:
  - AI reviews are textually aligned with human expert reviews but homogenize critique (AI-AI similarity >> Human-Human similarity)
  - GPT-5.2's quality advantage is robust to self-preference controls and survives cross-model evaluation — a more credible signal
  - Quality and novelty can dissociate: GPT-5.2 scores highest on quality but contributes little to within-group diversity; humans score highest on novelty but are not rated highest by AI evaluators
- **AI as complement, not replacement**:
  - Human novelty advantage suggests AI is better positioned for extending existing lines of inquiry
  - Humans contribute genuinely novel framings — perspectives not derivable from training data alone
  - Practical recommendation: use AI to broaden the space of conventional ideas and improve structured proposal elements (Relevance, Open Science), then rely on human expertise to push conceptual boundaries
- **Relation to prior work**:
  - Compare with Si et al. 2024 (human judges rated AI ideas as more novel — possible mismatch with quantitative measures; scale and domain differ)
  - Compare with Liang et al. 2024 (reviewer biases in novelty judgments)
  - Our embedding-based approach provides scalable, reproducible metrics complementary to subjective ratings; self-preference bias found here corroborates Panickssery et al. 2024
- **Limitations** (must be prominently addressed):
  - Single funding call (NCEMS) — generalizability to other domains unknown
  - Small sample (n = 23 human, n = 69 AI) — limited statistical power for subtle effects; no formal power analysis
  - Embedding distance ≠ conceptual diversity. BioLinkBERT may conflate stylistic with semantic differences even after style residualization; expert validation needed
  - Novelty score conflates genuine novelty with incoherence — distance from literature could mean a genuinely new idea OR a poorly formulated one
  - Topic separation may be partly an artifact of writing style; LDA results are exploratory
  - Population mismatch: humans wrote under real funding stakes with domain expertise and lab capabilities; AI under zero-stakes, zero-context conditions. This confounds any direct comparison
  - Quality evaluation is AI-only (except for n = 12 Y1 human proposals); human blinded review of AI proposals is pending (§2.5 R1 inverse direction untested)
  - GPT-5.2 near-zero variance in quality scores (SD ≈ 0.05) warrants investigation — possible rubric saturation
  - AI model versions are a snapshot; rapid model improvements may change results
- **Future directions**:
  - Human expert evaluation of proposal quality (blinded, with inter-rater reliability), especially AI proposal evaluation by humans
  - Repair proxy-validity harmonization (ICC and rank-correlation with human panel currently unavailable)
  - Recruit blinded human reviewers to rate AI proposals (inverse direction of R1)
  - Test whether AI–AI homogeneity in reviews leads to worse ranking discrimination than human review panels
  - Augmented AI conditions: literature-enriched prompts, persona-based generation
  - Construct validation: domain expert ratings of proposal pairs correlated with embedding distances
  - Multi-call replication across different funding agencies and scientific domains
  - Style-controlled analysis: embed keyword/concept extractions only, stripping writing style

---

## 4. Methods

### 4.1 Data

**Funding call.** The NSF National Synthesis Center for Emergence in Molecular and Cellular Sciences (NCEMS) issued a call for proposals on emergence in molecular and cellular biosciences. The call specified research requirements, evaluation criteria, and areas of interest.

**Human proposals.** 23 proposals were submitted by teams of human scientists across two annual cohorts (Year 1: n = 12; Year 2: n = 11) responding to the same NCEMS call. These represent real submissions written under genuine funding stakes, with domain expertise, lab capabilities, and collaborative context. Cohort comparability was tested on all 8 quality criteria prior to pooling (see §2.5.2).

**AI proposals.** Three frontier large language models — GPT-5.2 (OpenAI), Gemini 3 Pro Preview (Google DeepMind), and Claude Opus 4.5 (Anthropic) — each generated 23 proposals. [Specify exact model version identifiers, API dates, temperature settings, and seed parameters.] All models received the same prompt containing the NCEMS call for proposals, background information about NCEMS, and evaluation criteria — the same materials available to human applicants. [Full prompts to be provided as supplementary material.]

### 4.2 Embedding Pipeline

All proposals were encoded using BioLinkBERT-large, a 340M-parameter biomedical language model pretrained on PubMed with citation-link structure, ranked #1 on the BLURB biomedical NLP benchmark as of February 2026. Each proposal was split into overlapping 400-word chunks and encoded into 1,024-dimensional vectors, which were averaged to produce a single embedding per proposal. For novelty analysis and topic-level analyses, only titles and abstracts were embedded (not full proposal text) to ensure comparability with PubMed abstracts.

### 4.3 Part I: Within-Group Diversity Analysis

Three complementary metrics were computed:

**Pairwise cosine distances.** For each group (Human, Claude, Gemini, GPT-5.2, All AI), all n(n−1)/2 pairwise cosine distances were computed between proposal embeddings. Group distributions were compared using Mann-Whitney U tests with Cliff's delta effect sizes (thresholds: < 0.147 negligible, < 0.33 small, < 0.474 medium, ≥ 0.474 large). Permutation tests (10,000 iterations) and bootstrap 95% CIs were computed; Holm correction was applied across model-wise comparisons.

**Centroid dispersion.** The centroid (mean embedding vector) was computed for each group. Each proposal's cosine distance to its group centroid was calculated. Distributions of centroid distances were compared using the same statistical framework.

**Nearest-neighbor outlier detection.** All 92 proposals (23 human + 69 AI) were combined. For each proposal, the nearest neighbor (by cosine distance) was identified. Proposals in the top 10% of nearest-neighbor distances were classified as outliers. We recorded the group identity of each proposal's nearest neighbor to assess cross-group proximity.

### 4.4 Part II: Novelty Analysis

**Literature corpus.** 350 PubMed articles were retrieved using seven targeted search queries derived from the NCEMS call: emergent properties in molecular/cellular biology (59 articles), mesoscale biology and biomolecular organization (49), biomolecular condensates and phase separation (49), multi-omics data integration (50), AI/ML in molecular and cellular biology (59), systems biology and network analysis (44), and protein self-assembly and supramolecular organization (40). Mean abstract length: 1,351 characters. All abstracts were embedded using the same BioLinkBERT pipeline.

**Novelty score.** For each proposal, the k = 10 nearest neighbors in the PubMed corpus were identified by cosine distance. The novelty score is the mean cosine distance to these 10 nearest neighbors. Higher scores indicate greater distance from published literature. Only title-and-abstract embeddings were used for proposals to ensure fair comparison with PubMed abstracts.

**Statistical comparison.** Novelty score distributions were compared between groups using Mann-Whitney U tests, Cliff's delta, and permutation tests (10,000 iterations), with Holm correction across model-wise comparisons.

### 4.5 Part III: Thematic and Cluster Analysis

**Topic modeling.** Latent Dirichlet Allocation (LDA) was applied to TF-IDF representations of proposal titles and abstracts (stop words removed, min_df = 2, max_df = 0.7). We used k = 5 topics with strong Dirichlet priors (α = 0.5, β = 0.5) to stabilize topics given the small sample size. Stability was validated across 10 random seeds. Per-document topic distributions (soft assignment) were computed. [Report topic coherence (c_v metric) and perplexity.]

**Topic distribution comparison.** The overall distribution was tested using a chi-square permutation test (10,000 permutations). Per-topic tests used Fisher's exact test with Benjamini-Hochberg FDR correction at q = 0.10 (exploratory threshold). To account for the 3:1 group size imbalance, AI proposals were subsampled to n = 23 in 1,000 iterations, and the proportion of subsamples yielding significance was reported.

**Cluster analysis.** Gaussian Mixture Model (GMM) clustering was applied to full-text BioLinkBERT embeddings. The number of clusters was selected by BIC across k = 3–8 (k = 3 optimal). Covariance type: full. Cluster composition (% human, % AI by model) was computed.

**Segregation metrics.** Normalized Mutual Information (NMI) and Adjusted Rand Index (ARI) were computed between cluster labels and source labels (human vs. AI). Both were tested against permutation null distributions (10,000 iterations). Between-group vs. within-group cosine distance ratios were computed with permutation tests.

### 4.6 Part IV: Style Analysis and Style-Adjusted Sensitivity Analyses

**Style feature set.** Style-only features were constructed to capture how proposals are written without domain-semantic content: word/sentence/paragraph count, average sentence length, function-word rates, punctuation/formatting rates, readability scores (Flesch-Kincaid/Gunning Fog), type-token ratio, hedging/stance marker rates, and section header counts.

**Style-only baseline classifier.** A regularized logistic regression (L2 penalty, cross-validated) was trained on style features only with human vs. AI labels. AUROC was computed via stratified cross-validation. A permutation test (1,000 label shuffles) assessed statistical significance.

**Style residualization.** For centroid dispersion and nearest-neighbor analyses, BioLinkBERT embeddings were residualized on style features using linear regression (per embedding dimension). Analyses were then re-run on residual embeddings using the same statistical framework. Style leakage was quantified as the mean absolute correlation between style features and the top principal components of the residual embedding space.

### 4.7 Part V: Quality Analysis

**AI reviews.** All three AI models (GPT-5.2, Gemini 3 Pro Preview, Claude Opus 4.5) evaluated each of the 92 proposals (23 human + 69 AI) using the NCEMS evaluation criteria [blinded to authorship, one proposal per API call]. Reviews were saved with fields for title, author (human-Y1, human-Y2, or AI model), evaluator, and structured scores on 7 criteria: Relevance_to_Emergent_Phenomena, Novelty_and_Significance, Rigor_of_Approach, Scope_and_Timeline, Synthesis_Focus, Data_Identification, Open_Science_Commitment (each 1–5).

**R1: Proxy validity.** For the 12 Year 1 proposals reviewed by both human experts and all 3 AI models, review pairs were characterized by: (1) cosine similarity (sentence-BERT embeddings of qualitative review text), (2) sentiment polarity alignment (TextBlob polarity scores; alignment = 1 − |polarity_1 − polarity_2| / 2), and (3) categorical sentiment agreement. Scores were averaged to the proposal level before testing. Primary test: paired Wilcoxon signed-rank with BH-FDR correction. Pair types: Human–Human (HH), Human–AI (HAI), AI–AI (AIAI).

**R2: Proposal quality.** Proposal-level mean scores (averaged across evaluators) were compared between author groups using Mann–Whitney U + Cliff's δ + BH-FDR + bootstrap 95% CIs. Criterion-level decomposition examined the 7 rubric dimensions. Two sensitivity analyses controlled for identified biases (see R3): (1) cross-evaluator-only (removing self-evaluations for AI authors), (2) Gemini-only evaluator (single-evaluator control).

**R3: Evaluator bias.** Evaluator leniency was tested via Kruskal–Wallis across all AI reviews stratified by evaluator identity. Self-preference was assessed by comparing each AI evaluator's scores for its own vs. other models' proposals (Mann–Whitney + Cliff's δ + BH-FDR). A fixed-effects regression (score ~ is_self × criterion + evaluator + author + proposal_uid, HC3-robust SEs) tested whether self-preference persists after controlling for proposal quality and evaluator severity.

### 4.8 Multiple Testing Correction

FDR correction (Benjamini-Hochberg, q = 0.05) was applied within each analysis family: diversity (Holm correction for 4 model-wise comparisons per metric), novelty (Holm correction for 4 model-wise comparisons). Thematic/cluster analyses used FDR q = 0.10 (exploratory). Quality analyses used BH-FDR at q = 0.05, within criterion families. Raw p-values are reported in supplementary tables.

### 4.9 Visualization

UMAP projections (2D) were computed for embedding space visualization, with t-SNE as a confirmatory check. All statistical analyses were implemented in Python using scipy, scikit-learn, and gensim.

---

## Figures (≤6 main, ≤10 Extended Data)

| # | Figure | Content |
|---|--------|---------|
| 1 | **Study design schematic** | Overview of the 23 human + 69 AI proposals, embedding pipeline, and four analysis dimensions (diversity, novelty, thematic/style, quality) |
| 2 | **Pairwise diversity and centroid dispersion** | (a) Violin/box plots of pairwise cosine distances by group with Cliff's δ and bootstrap CI annotations; (b) Centroid dispersion distributions; (c) Effect size forest plot |
| 3 | **Novelty analysis** | (a) Novelty score distributions by group with statistical annotations; (b) UMAP of proposals + 350 PubMed articles showing distance from literature |
| 4 | **Embedding space and nearest-neighbor analysis** | (a) UMAP 2D projection of 92 proposals, colored by source, with centroids and outlier annotations; (b) Nearest-neighbor origin matrix (% same-source NN, raw and style-adjusted); (c) Style-adjusted UMAP in residual embedding space |
| 5 | **Thematic and cluster analysis** | (a) Stacked bar chart of topic prevalence by group; (b) GMM cluster composition (% human/AI per cluster); (c) Segregation metric summary (NMI, distance ratio) |
| 6 | **Quality analysis** | (a) Overall score distributions by author group under pooled AI evaluation; (b) Criterion-level effect-size heatmap; (c) Self-preference forest plot (R3); (d) Cross-evaluator-only sensitivity comparison |

**Extended Data candidates:**
- ED1: Literature corpus statistics (articles per query, date distribution)
- ED2: t-SNE confirmatory projections
- ED3: Full statistical tables for all comparisons (raw p-values, bootstrap CIs)
- ED4: LDA topic word distributions and coherence scores
- ED5: BIC curve for GMM cluster selection
- ED6: Sensitivity analysis for novelty k parameter (k = 5, 10, 20, 50)
- ED7: Style feature distributions by group and style-only classifier details
- ED8: R1 proxy validity detailed results (cosine similarity, sentiment alignment by model)
- ED9: R2 criterion-level decomposition with bootstrap CIs
- ED10: R3 fixed-effects regression table (evaluator bias after proposal quality controls)

---

## Supplementary Information

- Full prompts used for AI proposal generation
- Complete PubMed search queries and article metadata
- Per-proposal novelty scores and topic assignments
- Raw p-values for all statistical tests
- LDA topic word lists and coherence metrics
- Cohort analysis (Year 1 vs. Year 2 human proposals)
- Style feature definitions and logistic regression coefficients
- AI review instrument (NCEMS evaluation criteria and rubric)
- Per-proposal AI review scores and qualitative text
- Human expert review data (Y1 proposals)
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
- [ ] Repair proxy-validity harmonization: ICC and rank-correlation between AI and human review panels are currently unavailable — this must be resolved before R1 conclusions are finalized
- [ ] Recruit blinded human reviewers to rate AI proposals (the inverse direction of R1 is entirely untested)
- [ ] Investigate GPT-5.2 near-zero variance in quality scores (SD ≈ 0.05) — possible rubric saturation or generation artifact
- [ ] Conduct construct validation: have domain experts rate conceptual similarity of proposal pairs and correlate with embedding distances
- [ ] Complete human expert evaluation of proposal quality (blinded)
- [ ] Add formal power analysis or minimum detectable effect size calculation
- [ ] Report LDA topic coherence (c_v) and perplexity values
- [ ] Sensitivity analysis: vary novelty k parameter (5, 10, 20, 50) and report robustness
- [ ] Consider style-controlled analysis (embed keyword/concept extractions only)
- [ ] Ethics/IRB statement for use of human proposal data
- [ ] Pre-registration on OSF (if feasible at this stage)
- [ ] Data and code availability statement
- [ ] Verify figure count: 6 main figures with 4-panel Fig. 6 may require splitting; confirm NMI format constraints

### Key corrections from previous outline version
- **Pairwise diversity**: Claude δ = +1.00 (updated from +0.25); Gemini is NOT significantly different from humans (δ = +0.30, p = 0.083, updated from significantly less diverse); All AI combined δ = +1.00 (updated from −0.29)
- **Nearest-neighbor outliers**: Claude 26.1% outlier rate (was incorrectly listed as 0%), GPT-5.2 0% outliers (was incorrectly listed as 26.1%) — these were previously swapped
- **Novelty by model**: Claude δ = −0.40 (significant), GPT-5.2 δ = −0.21 (NOT significant) — previously swapped between Claude and GPT
- **Topic separation**: Not perfect; Human entropy = 0.448 (not 0); Topics 2 and 5 are not significantly AI-overrepresented after FDR correction
- **New Section 2.4**: Style analysis (AUROC = 1.000; 94.2% AI same-group NN after adjustment)
- **New Section 2.5**: Full quality analysis including R1 proxy validity, R2 proposal quality, R3 evaluator bias, and two sensitivity analyses
