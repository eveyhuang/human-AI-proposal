# IC2S2 Extended Abstract

---

**Title:** Diverse but Not Novel: Embedding-Based Analysis Reveals Systematic Differences Between AI-Generated and Human-Written Research Proposals

**Keywords:** large language models, scientific ideation, embedding-based analysis, human-AI comparison, science of science

---

## Extended Abstract

### Background

Research on AI and creativity consistently finds that LLMs boost individual-level output while narrowing collective diversity: individuals using ChatGPT produce higher-rated stories [1] and more original product concepts [2], yet groups relying on AI converge on fewer distinct ideas than unaided humans [2,3]. For *scientific* ideation specifically, Si et al. [4] found that LLM-generated research ideas were rated as more novel than expert human ideas—but by human judges using subjective Likert scales, which cannot distinguish ideas that read as fresh from those that genuinely venture beyond the published literature. A parallel limitation affects quality assessment: LLM feedback aligns with human reviewer text yet homogenizes critical perspectives [5], and LLM evaluators actively favor their own outputs [6], a self-preference bias that most AI-versus-human comparisons leave uncontrolled.

We address three gaps. First, we replace subjective ratings with quantitative embedding-based metrics that separately measure within-group diversity, novelty relative to the published literature, and thematic segregation—decomposing constructs prior work conflated. Second, we use a real, high-stakes funding call (not a constructed task), so human proposals reflect genuine scientific stakes and domain expertise. Third, we explicitly model and correct for AI evaluator self-preference, enabling fair quality comparisons across three frontier models simultaneously.

### Study

We collected 23 human-authored proposals submitted across two cohorts to the NSF National Synthesis Center for Emergence in Molecular and Cellular Sciences (NCEMS) call, and generated 69 AI proposals by prompting GPT-5.2, Gemini 3 Pro Preview, and Claude Opus 4.5 with the identical call materials. All 92 proposals were encoded with BioLinkBERT-large (1,024-dimensional biomedical embeddings) and analyzed across four dimensions: within-group diversity, novelty against a 350-article PubMed corpus, thematic and cluster composition, and AI-evaluated quality.

**Diversity.** Pairwise cosine distances reveal dramatic between-model variation: Claude far exceeds human diversity (Cliff's δ = +1.00), Gemini matches humans (δ = +0.30, p = 0.083), and GPT-5.2 collapses to near-identical proposals (δ = −1.00). In the combined proposal space, 100% of AI proposals have another AI proposal as their nearest neighbor—no AI proposal is closest to any human. After residualizing embeddings on style features (sentence length, function-word rates, readability, hedging), 94.2% of AI nearest-neighbor links remain same-source, confirming the separation is not a writing-style artifact.

**Novelty.** Human proposals are significantly more novel than AI combined when measured as mean cosine distance to the 10 nearest PubMed neighbors (human mean = 0.151 vs. AI mean = 0.117; Cliff's δ = −0.34, p = 0.014). This inverts the subjective-rating result of Si et al. [4], suggesting LLMs produce ideas that read as novel while remaining semantically close to well-covered territory [7]. Critically, diversity and novelty dissociate: Claude is the most internally diverse model yet significantly less novel than humans (δ = −0.40); GPT-5.2 collapses internally but is not significantly less novel. High within-group diversity is not a proxy for scientific originality.

**Thematic Segregation.** LDA (k = 5) shows that one topic—evolutionary and species-level biology—is dominated by humans (21 vs. 3 AI proposals; OR = 231, FDR q < 0.001), while two topics are significantly AI-overrepresented. GMM clustering (k = 3) produces two AI-only clusters and one mixed cluster containing all human proposals (NMI = 0.197, permutation p < 0.0001; between/within distance ratio = 1.085, p = 0.004). Three independent methods converge: human and AI proposals occupy distinct semantic territories.

**Quality Under AI Evaluation.** All three models evaluated all 92 proposals on a 7-criterion rubric. AI–AI review similarity is far higher than Human–Human similarity (δ = 0.93), consistent with the homogenization reported by Liang et al. [5]. Under cross-evaluator-only scoring (self-evaluations excluded to control for self-preference [6]), GPT-5.2 proposals score substantially above humans (mean = 4.55 vs. 3.65; δ = −1.00); Gemini's apparent advantage disappears, exposing it as a self-evaluation artifact; Claude is statistically equivalent to humans. Self-preference bias is model-divergent: GPT self-inflates (δ = +0.987), Claude self-deflates (δ = −0.581), Gemini shows no bias—underscoring that this confound must be characterized per evaluator, not assumed uniform.

### Summary of Findings

Across all four dimensions, a consistent picture emerges: AI and human proposals occupy different conceptual territories, and that difference is not reducible to writing style. On **diversity**, no single "AI" story holds—models range from extreme mode collapse (GPT-5.2) to near-human spread (Gemini) to above-human dispersion (Claude), revealing model-specific rather than generic AI behavior. On **novelty**, humans are systematically further from the existing literature than any AI model, and this advantage holds even for Claude, which is the most internally diverse model—demonstrating that within-group diversity and distance from the literature are independent axes that can point in opposite directions. On **thematic content**, three independent methods (nearest-neighbor analysis, LDA, GMM clustering) agree that human and AI proposals carve out different semantic regions, with AI proposals concentrated in two clusters that contain no human proposals at all. On **quality**, GPT-5.2 proposals are robustly rated higher by external AI evaluators after correcting for self-preference; Claude proposals are rated equivalent to humans; and Gemini's apparent advantage is entirely an artifact of self-inflation. Taken together, the findings show that AI models can generate varied scientific text, but that variation operates within a conceptual space that is less novel, thematically distinct, and differently structured than what human scientists produce under real stakes.

### Implications

The human novelty advantage supports a complementarity framing over substitution [7]: AI is best deployed as a first-pass brainstorming layer that broadens coverage of well-mapped territory, while human scientists retain a comparative advantage in generating ideas that genuinely push beyond the existing literature. For science policy, the sharp between-model differences caution against treating any single model's output as representative of "AI-generated science"—evaluation frameworks need to be model-specific. For computational social scientists more broadly, two methodological lessons transfer beyond this context: within-group diversity metrics must be paired with external benchmarks to avoid rewarding models that merely diversify within a constrained region, and AI-as-evaluator pipelines require per-model self-preference audits before group differences can be trusted.

---

*Figures (not counted toward page limit): (1) UMAP of 92 proposals + 350 PubMed articles illustrating novelty positioning by source and model; (2) Diversity and novelty effect-size forest plot (Cliff's δ) by model; (3) GMM cluster composition and LDA topic prevalence; (4) Self-preference and cross-evaluator quality comparison.*

---

### References

[1] Lee, B. C., & Chung, J. An empirical investigation of the impact of ChatGPT on creativity. *Nature Human Behaviour*, **8**, 1906–1914 (2024). https://doi.org/10.1038/s41562-024-01953-1

[2] Doshi, A. R., & Hauser, O. P. Generative AI enhances individual creativity but reduces the collective diversity of novel content. *Science Advances*, **10**(28), eadn5290 (2024). https://doi.org/10.1126/sciadv.adn5290

[3] Meincke, L., Nave, G., & Terwiesch, C. ChatGPT decreases idea diversity in brainstorming. *Nature Human Behaviour*, **9**, 1107–1109 (2025). https://doi.org/10.1038/s41562-025-02173-x

[4] Si, C., Yang, D., & Hashimoto, T. Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers. *arXiv* preprint arXiv:2409.04109 (2024). https://doi.org/10.48550/arXiv.2409.04109

[5] Liang, W., et al. Can large language models provide useful feedback on research papers? A large-scale empirical analysis. *NEJM AI*, **1**(8) (2024). https://doi.org/10.1056/AIoa2400196

[6] Panickssery, A., et al. LLM Evaluators Recognize and Favor Their Own Generations. *Advances in Neural Information Processing Systems* (*NeurIPS*) 37 (2024). https://arxiv.org/abs/2404.13076

[7] Ding, A. W., & Li, S. Generative AI lacks the human creativity to achieve scientific discovery from scratch. *Scientific Reports*, **15**, 9587 (2025). https://doi.org/10.1038/s41598-025-93794-9
