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



##  PART 1: Use AI models to generate proposals

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

## PART 2: Compare AI proposals against human proposals
- Embedding model: Use biomedical domain specific embedding model (BioLinkBERT-Large, rank 1 on BLURB as of 02/10/2026) to transfrom each proposal into vectors (AI proposals stored in `data/ai-proposals`, human proposals stored in `data/human-proposals`)

- Save the embedding vectors of all proposals in one single file for easy access and comparison later.

For each set of AI proposals (23 from each AI models), conduct following analysis with human proposals: 

### 2.1 DIVERSITY: Can AI generate more diverse proposals than teams of human scientists? 

#### Analysis 2.1.1 With-in group diversity
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


#### Analysis 2.1.2: Centroid Dispersion Metric

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

#### Analysis 2.1.3: Nearest-Neighbor Outlier Detection

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

### 2.2 NOVELTY: Can AI create more novel proposals than teams of human scientists?

- given the corpus of relevant literature and papers published by human scientists, where do human proposals and AI proposals fit? 

#### Analysis 2.2.1: Compute Novelty Scores

**Steps:**
1. [done] Fetch PubMed abstracts with relevant terms from the call for proposal; saved in `data/literature/call-relevant-corpus.json`
2. Embed all abstracts with same model used for proposals
3. For each proposal, find k nearest neighbors in corpus (k=10)
4. Novelty score = mean distance to k nearest neighbors
5. Higher score = farther from existing work = more novel
<!-- REVIEW: Distance from corpus captures both genuine novelty AND incoherence/nonsense. A proposal far from all literature could be novel or simply infeasible. Add a feasibility filter: only compute novelty for proposals passing a minimum quality threshold, or compute novelty conditional on quality. Also: corpus construction is critical — report N abstracts, date range, subfield distribution, MeSH terms used. Test sensitivity to corpus composition. See Critique §2b and §5b. -->



#### Analysis 2.2.2: Compare Novelty Distributions

**Steps:**
1. Compute novelty scores for all human and AI proposals
2. Compare distributions: Mann-Whitney U + Cliff's delta
3. Sensitivity analysis: vary k (5, 10, 20, 50) and check robustness

**Metrics:**
- Mean/median novelty score per group
- Effect size (Cliff's delta)
- Consistency across different k values



### 2.3 QUALITY: Can AI create proposals of higher quality than teams of human scientists?

- Give the criteria `data/evaluation_criteria.json` to AI models and instruct them to evaluate all human and AI proposals (blinded to authorship), then compare the evaluations
- Invite human experts to blindly review a subset of human and AI proposals, and compare
- Compare the similarity between AI's and human experts' reviews to see whether AI's reviews are reliable proxy
<!-- REVIEW: CRITICAL — Using AI to evaluate AI-generated proposals creates circularity (self-preference bias; see Zheng et al. 2023 "Judging LLM-as-a-Judge"). AI models may favor their own stylistic patterns and miss domain-specific issues. Human expert evaluation should be PRIMARY, not supplementary. Specify: minimum 3 independent reviewers per proposal, recruited from relevant domain, blinded to source, with inter-rater reliability (Krippendorff's alpha or ICC). Add explicit "AI self-preference" test: do models rate their own outputs higher? Also: how are structured criteria scores aggregated — averaged? weighted? See Critique §3. -->



### 2.4 More differences through topic modeling and cluster analysis

###$ Rationale
Reviewers will ask: "What are the actual conceptual differences?" Topic modeling provides interpretable insight into how human and AI ideation differs.

###$ Analysis 2.4.1: BERTopic Modeling

**Steps:**
1. Preprocess proposals (remove boilerplate, keep substantive content)
2. Fit BERTopic model on all 144 proposals <!-- REVIEW: Where does 144 come from? 23 human + (10×3 models × 3 conditions) = 113, or a different calculation? Clarify. See Critique §4c. -->
3. Extract topics, top words, and representative documents
4. Create interpretable topic labels (domain expert review)

**Parameters:**
- Embedding model: nomic-embed-text-v1 (same as diversity analysis)
- min_topic_size: 3 (small given n=144) <!-- REVIEW: min_topic_size=3 on ~100-150 docs will produce unstable topics. Consider increasing to 5. -->
- nr_topics: "auto"

**Library:** bertopic, sentence-transformers

###$ Analysis 2.4.2: Topic Distribution Comparison

**Steps:**
1. Create contingency table: topics × source (human/AI)
2. Overall chi-square test for distribution difference <!-- REVIEW: Chi-square may have cells with expected count <5. Fisher's exact as backup is correct but should be the default with this sample size. -->
3. Per-topic Fisher's exact test for over/under-representation
4. Apply FDR correction for multiple comparisons <!-- REVIEW: FDR is applied here but not across the entire study. With 3 AI conditions × 4 dimensions × multiple sub-analyses, define a global correction strategy. See Critique §1c. -->
5. Identify topics significantly over-represented in each group

**Metrics:**
- Chi-square statistic and p-value (overall)
- Odds ratios per topic
- FDR-corrected p-values per topic

###$ Analysis 2.4.3: Topic Coverage and Entropy

**Steps:**
1. Compute topic coverage: how many topics does each group cover?
2. Identify exclusive topics (only in one group)
3. Compute Shannon entropy of topic distribution per group <!-- REVIEW: Entropy comparison between groups of different sizes is tricky. Normalize by group size or use rarefaction. -->
4. Higher entropy = more even spread = higher diversity

**Metrics:**
- Number of topics covered per group
- Number of exclusive topics per group
- Shannon entropy (normalized by max possible)

#### Analysis 2.4.4: Cluster Composition/Segregation Analysis

**Rationale:** Do human and AI proposals occupy the same conceptual regions or segregate into different clusters?

**Steps:**
1. Run K-means clustering on all embeddings (try k = 3, 5, 7, 10)
2. For each cluster, compute composition (% human, % AI)
3. Compute Normalized Mutual Information (NMI) between cluster labels and source labels
4. High NMI = clusters predict source = segregation

**Metrics:**
- NMI score (0 = no segregation, 1 = perfect segregation)
- Adjusted Rand Index
- Per-cluster dominance (how far from 50-50)
- Number of human-dominated, AI-dominated, and mixed clusters

**Interpretation:**
- High segregation: human and AI generate different KINDS of ideas
- Low segregation: ideas intermixed regardless of source

---
---

## CRITIQUE AND REVIEW

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
- Alternatively, add a condition where human scientists are given the same constrained task (generate ideas in a short timeframe without their usual resources) — though this may be infeasible
- At minimum, acknowledge this prominently in the introduction and discussion, and discuss how it limits interpretation of all results

#### 1b. Sample Size and Statistical Power

- 23 human proposals (12 Y1 + 11 Y2) is very small
- No power analysis is presented
- Y1 and Y2 are different cohorts responding to potentially different calls — can they be pooled?
- With n=12 vs. n=30 (per AI condition), Mann-Whitney U has limited power to detect moderate effects
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



