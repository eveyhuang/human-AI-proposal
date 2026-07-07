# RESULTS — rewritten against current tables (2026-07-07)

*This replaces the RESULTS section of `writeup-jun26.md`, whose numbers predate the July rephrase refresh and no longer match the tables. All values below are taken from `results/tables/rephrased/minimal/` (four-group and `all_ai/` notebooks) and `results/tables/quality/minimal/ncems_criteria/`. Primary inference for all embedding-derived diversity metrics is the **group-level permutation (label-shuffle) test**, because proposal-level metrics derived from a shared distance matrix are not independent; Mann–Whitney/Holm values are reported only as secondary effect-size context.*

We compared 23 human-authored NCEMS proposals with 69 AI-authored proposals (Claude, Gemini, GPT-5.2; 23 each), and 85 human expert reviews with matched AI reviews of the same human proposals. Because the pooled AI set is larger than the human set, all size-sensitive AI quantities are computed by bootstrap subsampling to n = 23 (1,000 draws). A style-only classifier trained to separate human from AI text achieved chance performance (AUROC 0.52, permutation p = 0.45), confirming that the rephrasing step removed surface-style signal and that the embedding comparisons below reflect semantic content rather than prose style.

## Result 1 — AI proposal sets are far less diverse than human proposal sets

Across every measure of embedding-space dispersion, the 23 proposals produced by each AI model — and the pooled AI set — cover their semantic neighborhood far more tightly than the 23 human proposals (Table R1; Fig. 1, generation-diversity band). Human proposals have a mean within-set pairwise distance of 0.341, versus 0.152 for the pooled AI set (Cliff's δ = −0.83; permutation p = 1×10⁻⁴). The same ordering holds for centroid dispersion (0.195 vs 0.082; p = 0.009), global-centroid distance (0.191 vs 0.079; p = 0.008), minimum-spanning-tree dispersion (0.100 vs 0.061; p = 0.001), medoid sparseness (0.222 vs 0.093; p = 0.010), and nearest-neighbor isolation (0.075 vs 0.043; p = 2×10⁻⁴). Effect sizes are uniformly large (|δ| = 0.70–0.87). Per-model contrasts are individually significant for Claude, Gemini, and GPT-5.2 in the same direction, and a Kruskal–Wallis preflight found no significant heterogeneity among the three models after correction — the compression is a shared property of all three frontier systems, not one outlier model.

These metrics are correlated views of the same underlying dispersion and should be read as one robust finding measured several ways, not six independent results. Two observations sharpen its interpretation. First, the one metric that captures *total occupied area* rather than average separation — normalized grid entropy — does **not** differ (0.330 vs 0.364 bootstrap; p = 0.77): pooled AI proposals span a comparable overall footprint. The compression is therefore in *local density and redundancy* — AI proposals pile into tight clusters — rather than in the outer extent of the search space. Second, pairwise-distance distributions are bimodal for all groups (Hartigan dip p < 0.005), reflecting a within-cluster mode and a large between-cluster gap; human and AI sets differ mainly in the mass placed in the low, within-cluster mode.

**Table R1. Generation-stage diversity (Human vs pooled AI, n=23 each after bootstrap).**

| Metric | Human | AI (boot) | Cliff's δ | Permutation p |
|---|---|---|---|---|
| Mean pairwise distance | 0.341 | 0.152 | −0.83 | 1×10⁻⁴ |
| Centroid dispersion (LOO) | 0.195 | 0.082 | −0.83 | 0.009 |
| Global-centroid distance | 0.191 | 0.079 | −0.70 | 0.008 |
| MST mean edge | 0.100 | 0.061 | — | 0.001 |
| Sparseness (medoid) | 0.222 | 0.093 | −0.70 | 0.010 |
| Nearest-neighbor isolation | 0.075 | 0.043 | −0.87 | 2×10⁻⁴ |
| Grid entropy (total coverage) | 0.330 | 0.364 | — | 0.77 (n.s.) |

## Result 2 — AI proposals are not closer to the literature on average, but humans supply nearly all of its outliers

We next placed proposals in a fixed map of 39,538 PubMed abstracts (2010–2026) and measured literature-relative novelty (Fig. 2). Contrary to a simple "AI is derivative" hypothesis, **no continuous novelty or coverage metric distinguished human from AI proposals after correction.** Mean-kNN distance to nearest literature neighbors was marginally higher for humans but not significant (k = 10: 0.115 vs 0.099; Holm q = 0.80), as were element-novelty (0.217 vs 0.193; q = 0.13) and normalized novelty-z (0.73 vs 0.55; q = 0.80). Curated-vocabulary coverage told the same null story, and if anything favored AI: mean unique MeSH descriptors were 80.0 (human) vs 85.1 (AI; p = 0.83). Embedding-region breadth (BERTopic) was descriptively higher for humans at the group level (Shannon entropy 1.28 vs 1.00; effective regions 3.60 vs 2.73) but did not survive proposal-level correction, and nearest-literature recency did not differ within region.

The one literature-anchored contrast that is robust concerns the **tail**, not the average. Human proposals are far more likely to sit in sparse, outlying regions of the literature map: 7 of 23 human proposals (30.4%) are top-10% mean-10NN literature-space outliers, versus 3 of 69 AI proposals (4.3%) (Fisher p = 0.002; Holm q = 0.006); the element-novelty outlier definition agrees (26.1% vs 5.8%; q = 0.028). In other words, AI proposals are not systematically anchored nearer to existing work, but human proposals disproportionately populate the frontier of the map (Fig. 2, ringed points). The generation-stage compression is thus best described as a **collapse of the diverse and outlying tail**, not a wholesale shift toward the literature mean.

## Result 3 — AI reviews are less diverse and more interchangeable than human reviews

At the filtering stage, we compared the semantic diversity of the independent reviews written for each human proposal (Fig. 3). Human reviews were more diverse than AI reviews on every metric in the Year-2 cohort (all nine metrics, Wilcoxon q = 0.001; Cliff's δ up to 1.0) and on four of nine in Year-1 (span90, global-centroid, medoid, and sparseness, q = 0.047; mean-pairwise and remote-clique trended the same way, q = 0.096).

Because human proposals received more reviews than AI proposals (3.5–3.9 vs exactly 3), we re-estimated the effect after subsampling each proposal's human reviews to exactly three, matching the AI count (mean over 500 draws; 19 proposals with ≥3 of each). The effect is essentially unchanged: human reviews remain more diverse on mean-pairwise (0.043 vs 0.033; Wilcoxon p = 0.002; δ = +0.73), nearest-neighbor (p = 0.002; δ = +0.73), sparseness (p = 0.002; δ = +0.74), and span90 (p = 0.003; δ = +0.70), with humans more diverse on 79–89% of proposals. The review-diversity gap is therefore not an artifact of review count.

Reviews also converged on one another. Pairwise cosine similarity between two AI reviews of the same proposal was substantially higher than between two human reviews (Cliff's δ = 0.57; Mann–Whitney q = 0.029) and higher than between a human and an AI review (δ = 0.74; q = 0.007), whereas human–AI and human–human similarity did not differ. Consistent with this convergence, inter-rater reliability of the Year-2 rubric scores was markedly higher for human-vs-AI agreement (ICC2k = 0.78) than among human reviewers themselves (ICC2k = 0.49): AI reviewers are, in effect, more interchangeable evaluators than human experts. Notably, this comparison is *conservative* for our thesis, because the AI "panel" comprises three different vendors; a single-model review panel — the realistic automation scenario — would be expected to converge further still.

## Summary

Human and AI systems differ sharply in *diversity* at both stages of collective scientific search but not in average *novelty*. AI-authored proposal sets are dramatically more locally concentrated (Result 1) and rarely reach the outlying frontier of the literature that humans populate (Result 2), and AI review panels apply more homogeneous, mutually interchangeable evaluative filters than human panels (Result 3). The consistent signal is a **compression of diversity and of the tail** — narrower idea neighborhoods and narrower evaluative lenses — rather than a uniform shift toward derivative or lower-novelty content.

---

### Reporting notes for the authors (delete before submission)

- **Do not** cite the MW-Holm p≈10⁻⁹ diversity values as primary; they assume independence the data violate. The permutation p-values above are the defensible headline numbers.
- Result 2 is deliberately framed as a **null on average / significant in the tail**. This is the honest reading of the current tables and is more robust than the draft's "AI is less novel" claim.
- Result 3's n-matched re-analysis is new (script + outputs in `results/figures/review_feedback/`); fold `_review_diversity_nmatched_summary.csv` into a supplementary table.
- Before final submission, confirm Results 1–3 survive (i) the non-rephrased text pipeline and (ii) a second embedding space; add one sentence each as robustness.
