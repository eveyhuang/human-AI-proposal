# Do AI Systems Narrow Collective Scientific Search? Audited Results Across Five Diversity Facets, Two Pipeline Stages, and Three Elicitation Conditions

**Status:** internal results report (audited) · **Date:** 2026-07-16
**Data version:** prompt-corrected AI reviews (regenerated 2026-07-16); `rephrased` (style-controlled) text branch is primary throughout, `original` reported as robustness.
**Provenance:** all statistics recomputed by the rebuilt facet pipeline (`02_facets_proposals` → `03_facets_reviews` → `04_synthesis`) after a full audit against `docs/plans/diversity_facets_design_spec_v2.md`; figures follow the direction-aligned conventions of `docs/plans/facet_visualization_redesign_spec.md`. Every number below is traceable to `results/tables/{condition}/{task}/rephrased/facet_diversity_tests.csv`.

---

## Reader's guide (start here)

**The question.** When AI systems both *generate* research proposals and *review* them, does the collective search of science narrow — fewer genuinely different ideas proposed, and less independent judgment filtering them?

**The design.** 23 human proposals (two cohorts of biomedical scientists) are compared with 23 proposals from each of three AI models (Claude, Gemini, GPT), under three elicitation conditions: **baseline** (a single request), **one_at_a_time** (ideas requested one per conversation), and **persona** (the model is given a distinct scientist persona per proposal). On the filtering side, each human proposal was reviewed by 2–5 human reviewers and by 5 AI reviewers per model; AI review panels are compared with the human panel *of the same proposal*, at matched panel size.

**"Diversity" is not one number.** We decompose it into five facets, each answering a different question:

| Facet | Plain-language question |
|---|---|
| **Spread** | How far apart are the ideas from one another, on average? |
| **Richness** | How many *effectively distinct* ideas are there, once near-repeats are discounted? |
| **Evenness** | Are ideas spaced out, or do they pile up in near-duplicate clumps? |
| **Dimensionality** | Along how many independent directions do the ideas vary? |
| **Coverage** | How much of the territory that humans explore does AI reach? (Measured two ways: geometrically in idea-space, and by which regions of the biomedical literature are engaged.) |

A separate **displacement** check (not a diversity facet) asks whether AI occupies a *different place* than humans, or a smaller region *inside* the human territory.

**How to read significance.** Stars mean `*** p<0.001`, `** p<0.01`, `* p<0.05`, `ns` not significant. Three pre-registered primary comparisons (spread, richness, geometric coverage) are tested at face value; all other tests carry a correction for testing many things at once (Benjamini–Hochberg false-discovery-rate control), so a starred secondary result already accounts for the size of the test battery. Plain-language explanations of every statistical device appear in §5.

**Two different effect sizes, by design.** Generation compares whole groups (23 vs 23), so effects are **ratios**: *AI ÷ Human diversity retained*, where 1.0 = parity and 0.70 = "AI retains 70% of human diversity." Filtering is a *paired* design — each proposal's AI panel vs its own human panel — so effects are **Cliff's δ**, a consistency measure: δ = −1 means the AI panel came out lower for *every single one* of the 23 proposals; δ = 0 means no systematic direction. The two cannot be placed on one axis honestly, but both are oriented so that **negative/below-1 = AI less diverse**.

---

## 1. Results at a glance

### Table 1a — Generation (proposals): AI ÷ Human diversity retained

Cells show the ratio (1.00 = human parity; lower = AI narrower) with significance vs the human group. Pooled AI is always evaluated at n = 23 subsampled from the 69 AI proposals, so every comparison is at equal sample size.

| Facet (metric) | Condition | Claude | Gemini | GPT | **Pooled AI** |
|---|---|---|---|---|---|
| **Spread** (mean pairwise distance) | baseline | 0.61 ns | 0.73 ns | 0.78 ns | **0.70 \*\*** |
| | one_at_a_time | 0.81 ns | 0.45 \* | 0.64 ns | **0.64 \*\*\*** |
| | persona | 0.69 ns | 0.50 \* | 0.86 ns | **0.68 \*\*** |
| **Richness** (Vendi VS₁, effective distinct proposals) | baseline | 0.68 ns | 0.77 ns | 0.75 ns | **0.74 \*\*** |
| | one_at_a_time | 0.74 ns | 0.56 \* | 0.65 \* | **0.66 \*\*\*** |
| | persona | 0.77 ns | 0.63 \* | 0.86 ns | **0.75 \*\*** |
| **Evenness** (clumping vs. chance)† | baseline | AI clumped \* | ≈ chance ns | AI clumped \* | **AI clumped \*\*\*** |
| | one_at_a_time | AI clumped ns | AI clumped \*\* | AI clumped \* | **AI clumped \*\*\*** |
| | persona | AI clumped ns | AI clumped \* | AI clumped ns | **AI clumped \*\*\*** |
| **Dimensionality** (participation ratio) | baseline | 0.98 ns | 0.99 ns | 0.86 \* | **0.97 ns** |
| | one_at_a_time | 0.78 \*\*\* | 0.91 ns | 0.82 \* | **0.85 \*** |
| | persona | 1.08 ns | 1.07 ns | 0.97 ns | **1.06 ns** |
| **Coverage, geometric** (fraction of human idea-space reached)‡ | baseline | 1.00 ns | 0.61 \* | 0.87 ns | **0.85 \*** |
| | one_at_a_time | 1.00 ns | 0.61 \* | 0.78 ns | **0.86 ns** |
| | persona | 0.83 ns | 0.87 ns | 0.78 ns | **0.81 \*\*\*** |
| **Coverage, domain** (literature regions touched, of 12) | baseline | 1.00 ns | 1.14 ns | 0.86 ns | **0.98 ns** |
| | one_at_a_time | 0.86 ns | 0.71 ns | 0.86 ns | **0.84 \*\*** |
| | persona | 1.14 ns | 0.86 ns | 1.00 ns | **1.01 ns** |

† Evenness is an area statistic (excess close-neighbor mass relative to a same-size chance draw of all proposals), not a ratio. In every condition, humans are *more evenly spread than chance* (excess −0.14 to −0.23) while pooled AI shows *excess clumping* (+0.06 to +0.14); cells summarize direction and significance. ‡ Coverage is judged against how well one random half of the human set covers the other half (the honest "same-distribution" benchmark), not against 100%.

### Table 1b — Filtering (reviews): Cliff's δ, AI panel vs the human panel of the same proposal

δ < 0 = AI panels less diverse; |δ| = 1 means the effect held for all 23 proposals. Human reviewers of a given proposal are the built-in reference (they define zero).

| Facet | Condition | Claude | Gemini | GPT | **Pooled AI** |
|---|---|---|---|---|---|
| **Spread** | baseline | −0.74 \*\*\* | +0.04 ns | −0.91 \*\*\* | **−0.39 ns (p=.07)** |
| | one_at_a_time | −1.00 \*\*\* | −1.00 \*\*\* | −0.91 \*\*\* | **−0.91 \*\*\*** |
| | persona | −0.91 \*\*\* | −0.74 \*\*\* | −1.00 \*\*\* | **−0.74 \*\*\*** |
| **Richness** | baseline | −0.74 \*\*\* | +0.04 ns | −0.91 \*\*\* | **−0.30 ns (p=.09)** |
| | one_at_a_time | −1.00 \*\*\* | −1.00 \*\*\* | −0.91 \*\*\* | **−0.83 \*\*\*** |
| | persona | −0.83 \*\*\* | −0.74 \*\*\* | −1.00 \*\*\* | **−0.74 \*\*\*** |
| **Evenness** (δ > 0 = AI clumpier) | baseline | +0.74 \*\*\* | −0.04 ns | +0.74 \*\*\* | **+0.22 ns** |
| | one_at_a_time | +1.00 \*\*\* | +0.91 \*\*\* | +0.91 \*\*\* | **+0.91 \*\*\*** |
| | persona | +0.83 \*\*\* | +0.74 \*\*\* | +1.00 \*\*\* | **+0.74 \*\*\*** |
| **Dimensionality** | baseline | −0.09 ns | −0.09 ns | +0.09 ns | **−0.00 ns** |
| | one_at_a_time | +0.18 ns | −0.09 ns | −0.09 ns | **−0.00 ns** |
| | persona | +0.18 ns | −0.09 ns | +0.09 ns | **−0.00 ns** |
| **Coverage** (δ > 0 = AI panels reach *more* of the human review span) | baseline | +1.00 \*\* | +0.22 ns | +0.85 \*\* | **+0.37 \*\*** |
| | one_at_a_time | +1.00 \*\* | +1.00 \*\* | +1.00 \*\* | **+0.44 \*\*** |
| | persona | +1.00 \*\* | +0.60 ns | +0.83 \*\* | **+0.37 \*\*** |

### Table 1c — Directional and control checks

| Check | baseline | one_at_a_time | persona | Reading |
|---|---|---|---|---|
| Displacement, proposals (MMD², pooled AI vs Human) | 0.037 ns | 0.062 ns | 0.032 ns | AI proposals sit *inside* the human region, not beside it |
| Displacement, reviews (MMD², whole clouds; exploratory) | 0.0073 \*\*\* | 0.0116 \*\*\* | 0.0155 \*\*\* | AI reviews occupy a systematically shifted position; shift grows with structured elicitation |
| Lexical diversity (distinct 2-grams, Human ÷ AI) | 1.07–1.14 \*\* | 1.21–1.24 \*\* | 1.04 ns–1.07 \*\* | Wording also narrows — the effect is not an artifact of the text encoder; persona nearly closes the *wording* gap only |
| Self-repetition (self-BLEU; higher = more repetitive) | AI 0.27–0.32 vs H 0.19 | AI 0.34–0.35 vs H 0.19 | AI 0.21–0.26 vs H 0.19 | AI reuses its own phrasing more, in every condition |
| Model ordering (Claude < Gemini < GPT < Human trend test) | not supported as an internal AI ordering in either stage | | | Humans exceed every model; no reliable ranking *among* models |

---

## 2. Generation: how AI narrows the production of ideas

All generation analyses operate on the full text of each proposal, represented in a high-dimensional semantic embedding space; "distance" below means dissimilarity of scientific content, with prose style already normalized away (the `rephrased` branch rewrites all proposals into one house style before embedding, so wording habits cannot masquerade as ideas).

### 2.1 Spread — AI proposals sit closer together

*What was tested.* The average distance between all pairs of proposals within a group, compared between humans and each AI group by a permutation test (shuffle the group labels 10,000 times and ask how often chance alone produces a gap this large).

*Result.* Human proposals average 0.416 apart; pooled AI proposals average 0.268–0.293 — AI retains **64–70% of human spread**, significant in every condition (baseline p = .010; one_at_a_time p < .001; persona p = .003). Individual models at n = 23 mostly do not reach significance on their own (the study is powered for the pooled contrast); Gemini is the significant exception under one_at_a_time and persona (ratios 0.45–0.50).

*Implication.* The most direct sense of narrowing — ideas closer together — is present in every condition. But spread alone cannot say *why*: two tight clusters far apart also average a large spread. The next two facets say why.

### 2.2 Richness — fewer effectively distinct proposals

*What was tested.* The Vendi score VS₁ converts a set's mutual similarities into an "effective number of fully distinct items." The unit is intuitive: the 23 human proposals behave like **3.15 completely independent ideas**, while pooled AI sets behave like **2.09–2.37** (absolute Vendi values are conservative on dense semantic embeddings; the *ratio* is the meaningful quantity).

*Result.* AI retains **66–75% of human effective richness**, significant in all conditions (pooled p = .005 / <.001 / .004). This is a pre-registered primary result. Gemini is again the weakest single model (0.56 at one_at_a_time).

*Implication.* Narrowing is not merely "closer together" — it is genuinely *fewer distinct ideas*. If a funder replaced its human idea pool with an equal-sized AI pool, roughly a quarter to a third of the effective intellectual variety would disappear, under every elicitation strategy tested.

### 2.3 Evenness — AI re-proposes near-duplicates; humans do not

*What was tested.* For each group, we count how many close neighbors each proposal has within growing distance thresholds, and compare that against what a random same-size draw of *all* proposals (human and AI together) would produce. Positive excess = more tight clustering than chance ("near-duplicate clumps"); negative = more evenly spaced than chance.

*Result.* The starkest qualitative contrast in the study. **Humans are more evenly spread than chance in all three conditions** (excess −0.14 to −0.23), while **pooled AI shows excess clumping in all three** (+0.06 to +0.14; p ≈ .001 throughout, simultaneous-envelope test). In nearest-neighbor terms: at a distance where only ~35% of human proposals have a close "twin," over 80% of Claude's baseline proposals already do.

*Implication.* AI's narrowing takes a specific and recognizable form — it returns to the same wells. This is exactly the failure mode that averaged distance metrics can hide, and it is why the multi-facet design exists.

### 2.4 Dimensionality — narrowing is *not* a collapse onto fewer axes

*What was tested.* The participation ratio: an effective count of independent directions along which a group's proposals vary.

*Result.* Essentially null. Ratios are 0.85–1.06 across conditions; only one_at_a_time shows a modest, significant reduction (0.85, p = .02), and under persona AI is numerically *above* parity (1.06, ns).

*Implication.* This is an informative negative. AI proposals vary along roughly as many independent directions as human proposals — they are not "flattened." Combined with §2.2–2.3, the mechanism is precise: **similar number of axes, fewer distinct positions along them, with repeated returns to the same positions.**

### 2.5 Coverage (geometric) — AI reaches most, not all, of the human territory

*What was tested.* For each human proposal, does any AI proposal fall within its local neighborhood? The benchmark is not 100%: even a second, equally human set would miss some — so AI is judged against how well one random half of the human set covers the other half.

*Result.* Pooled AI reaches **81–86% of the human idea-space**, below the human self-benchmark at baseline (p = .038) and persona (p < .001), marginal at one_at_a_time (p = .08). The model split is the striking part: **Claude covers the human space fully (ratio 1.00 at baseline and one_at_a_time), while Gemini reaches only 61%.** A stability check across neighborhood sizes (k = 2, 3, 5) preserves this ordering.

*Implication.* There is a periphery of human proposals — roughly one in six — that the AI pool never approaches, and *which* AI you use matters more here than for any other facet.

### 2.6 Coverage (domain) — the narrowing is inside topics, not across them

*What was tested.* Each proposal was mapped to its ten nearest abstracts among ~39,500 PubMed papers; a group's domain coverage is how many of the 12 literature regions, and how many unique MeSH subject terms, it collectively touches — always compared at equal group size, with accumulation curves to make the counts honest.

*Result.* Essentially null, and the direction is mixed. All groups touch 5–8 of 12 regions; the only significant cell after correction is pooled AI at one_at_a_time (5.9 vs 7 regions, p_fdr = .008). AI proposals nominally touch *more* unique MeSH terms than humans (e.g., 571–598 vs 504, ns). The region-occupancy maps show only rare exclusive territories (e.g., a clinical-risk/patient-studies region touched only by humans at baseline).

*Implication.* AI is not avoiding areas of biomedical science. Read jointly with §2.5, the claim sharpens into the more interesting one: **AI engages the same topics but explores less variety *within* them.** For a biomedical audience: same subject headings, fewer genuinely different ideas per heading.

### 2.7 Displacement check — a smaller region *inside* the human one

*What was tested.* Whether the AI proposal cloud sits somewhere *else* than the human cloud (kernel two-sample distance MMD², against a shuffle-based null), which would change the story from "narrower" to "different."

*Result.* Pooled displacement is small and non-significant in every condition (0.032–0.062, all ns; the human split-half floor is ≈ 0). Per model: GPT is essentially undisplaced (persona MMD² = 0.000); Gemini is the only repeat offender (significant at one_at_a_time and persona).

*Implication.* Low coverage plus low displacement is the specific geometric signature of the central claim: **AI narrows *toward the shared human center*, occupying a competent, plausible core while missing the periphery** — as opposed to wandering into territory of its own. Gemini is the partial exception: narrowest *and* somewhat shifted.

### 2.8 Controls and robustness

- **Lexical control.** Human proposals are also more diverse in raw wording (distinct 2-gram ratios 1.04–1.24, significant almost everywhere), and AI text repeats its own phrasing more (self-BLEU 0.21–0.35 vs 0.19). Semantic narrowing therefore cannot be an artifact of the text encoder. Notably, **persona nearly closes the wording gap (ratios drop to ~1.04–1.07) while the idea-level gaps of §2.1–2.3 persist** — personas diversify *how* models write more than *what* they propose.
- **Style sensitivity (text branch).** On the unrephrased `original` text, the pooled baseline spread/richness contrasts disappear (ratios 1.02/0.96, ns) — but not because the models agree with humans: Claude and GPT are significantly *narrower* on raw text (0.58–0.87, \*\*\*) while Gemini's raw prose is *wider* than human (spread ratio 1.52), and the opposing style effects cancel in the pool. One_at_a_time and persona replicate on both branches, and geometric coverage narrows on *both* branches (baseline original 0.60, p < .001). The pre-registered primary branch is `rephrased`; the full original-branch results, and what the rephrased-vs-original contrast reveals about style versus ideas, are reported in **SI-2**.
- **Kernel sensitivity.** The richness result's direction is preserved under an alternative (RBF) similarity kernel across bandwidths; individual per-model significances vary (4–6 of 9 cells), consistent with per-model tests being underpowered rather than direction-unstable.
- **Ordering across models.** Trend tests for the pre-specified ordering Claude < Gemini < GPT < Human are dominated entirely by the human–AI gap; the internal AI ordering is not supported (Gemini, not Claude, is typically the narrowest). We report "humans above every model" and decline the model-ranking claim.

---

## 3. Filtering: how AI narrows the judgment of ideas

The filtering analyses respect the nested structure of review: reviews of *different* proposals differ for reasons that have nothing to do with reviewer independence. So every metric is computed *within* a proposal — the 2–5 human reviews of proposal X versus same-sized panels drawn from the AI reviews of proposal X — and then the 23 within-proposal comparisons are combined with a paired test. The human panel is thus the built-in reference: effects are read as "AI panels relative to the human panels of the very same proposals."

Two reference conventions matter and are stated on every figure: the human self-benchmark for panel *coverage* is leave-one-out self-coverage (how well each human review is covered by the rest of its own panel; 0.83 on average — not 1.0), and panel *clumping* is judged against random same-sized draws from that condition's full review pool.

### 3.1 Spread and richness — AI reviewers agree with each other more

*Result.* AI panels are tighter and less rich than the matched human panels, with near-ceiling consistency under structured elicitation: at one_at_a_time, pooled δ = −0.91 (spread) and −0.83 (richness), with several model-level cells at δ = −1.00 — lower for *every one* of the 23 proposals (p ≈ 10⁻⁶–10⁻⁷). Persona is similar (pooled δ = −0.74). At baseline, Claude and GPT show the same strong pattern (δ = −0.74 to −0.91, \*\*\*), while **Gemini sits exactly at parity (δ = +0.04, ns)**, which dilutes the pooled baseline contrast to marginal (δ ≈ −0.3 to −0.4, p = .07–.09).

*Magnitude vs consistency — an essential distinction.* In absolute units the effect is small: human panels average 0.044 mutual distance, AI panels 0.028–0.040 (a 8–36% tightening; effective richness 1.13–1.19 vs 1.18 — review panels are highly homogeneous for everyone). What is remarkable is the *consistency*: the tightening recurs proposal after proposal, which is exactly what a funding process should care about, because systematic small biases — unlike noisy large ones — do not average out across a portfolio. The same collapse appears in the numeric scores committees actually consume — and, at this sample size, without demonstrable divergence in the resulting rankings — see **SI-3**.

### 3.2 Evenness — AI reviews clump; mirror image of generation

*Result.* Relative to same-sized random panels, AI review panels carry excess near-duplicate mass in every condition and for every model except Gemini at baseline (pooled δ = +0.91 at one_at_a_time, +0.74 at persona, all \*\*\*). AI reviewers do not merely agree in score — they say near-interchangeable things.

### 3.3 Dimensionality — cleanly null

*Result.* Twelve of twelve cells ns, |δ| ≤ 0.18. AI panels vary along as many independent axes of critique as human panels; they simply occupy less of each axis. The generation-side negative (§2.4) is exactly reproduced on the filtering side — a satisfying internal consistency check.

### 3.4 Coverage — the "central blanket" pattern

*Result.* This facet runs the *other* way, and the combination is the most diagnostic finding on the filtering side. AI panels cover **95–98%** of the human review span, *exceeding* the human self-benchmark of 83% (pooled δ = +0.37 to +0.44, \*\* in all conditions; Claude δ = +1.00 everywhere).

*Implication.* Read §3.1–3.2 and §3.4 together: AI reviews are *individually near everything the humans said* (high coverage) while being *collectively interchangeable* (low spread, high clumping). AI review panels behave like several copies of one thorough, centrally positioned reviewer — a blanket over the human review span — whereas human panels behave like distinct voices that each miss things but disagree informatively. For a decision process, coverage of this kind is not a substitute for independent perspectives: the variance that a deciding committee learns from is precisely what is missing.

### 3.5 Displacement and ordering checks

The pooled AI review cloud is significantly displaced from the human cloud in every condition (whole-cloud, exploratory: MMD² = 0.0073 → 0.0116 → 0.0155 from baseline to persona, all p ≤ 2×10⁻⁴) — AI reviews have a systematic stylistic/positional signature that *grows* under structured elicitation even as panel diversity shrinks. (The branch comparison in SI-2 shows this signature is overwhelmingly stylistic: on raw text the displacement is ~20× larger and rephrasing removes almost all of it.) Trend tests across models are uniformly non-significant on the filtering side: no model ordering, again.

### 3.6 One flagged cell

Gemini-at-baseline is the only AI cell at parity across spread/richness/evenness, followed by δ = −1.00 under one_at_a_time — a within-model jump no other model shows. Data-level checks (duplicate texts, review lengths, panel counts) found no anomaly, and the same pattern appears on the `original` text branch, so it appears to be a real elicitation effect; we nonetheless recommend a qualitative read of Gemini's baseline reviews before this cell is quoted.

---

## 4. Synthesis: the coherent story

**1. AI narrows the generation of scientific ideas — substantially, in a specific way, in every condition tested.** Pooled across models, AI proposal sets retain roughly two-thirds to three-quarters of human diversity on the facets that count distinct ideas (spread 0.64–0.70, richness 0.66–0.75, all significant), and the loss has a signature: excess near-duplication (humans are more evenly spread than chance; AI is clumpier than chance, every condition) inside a space of undiminished dimensionality and undiminished topical breadth. AI proposals engage the same regions of the biomedical literature, touch as many subject headings, and vary along as many axes — **the narrowing is intra-topic: fewer genuinely different ideas per area of science, with repeated returns to the same ones.** The displacement check certifies the geometry: AI occupies a smaller region *inside* the human territory (low coverage, no displacement), not a different region beside it. And the lexical control shows the same compression in raw wording, ruling out the embedding model as the source.

**2. AI also narrows the filtering of ideas — mildly in magnitude, but with near-deterministic consistency, and most strongly under exactly the elicitation styles that improve generation hygiene.** Given the same proposal, AI review panels are tighter, less rich, and more mutually duplicative than the human panel — for essentially every proposal under one_at_a_time and persona (δ ≈ −0.7 to −1.0), and for two of three models at baseline. Yet AI panels *cover* the human review span better than human reviewers cover each other. The picture is a central blanket: each AI review is competent and touches everything; the panel as a whole contains one voice. Independence of judgment, not quality of judgment, is what filtering loses.

**3. "Double compression" is real but asymmetric — and honesty about the asymmetry strengthens the paper.** The two stages compress differently: generation loses 25–36% of effective diversity (large magnitude), filtering loses only a few percent in ratio terms but does so for nearly every proposal (large consistency). Compression does not *compound* in the naive multiplicative sense — the slopegraphs rise toward parity from generation to filtering — but the two losses are complementary in kind: generation narrows *what enters the pool*; filtering standardizes *how the pool is judged*. A pipeline with both stages automated would draw from a poorer menu and evaluate it with a single palate.

**4. Elicitation strategy redistributes the problem; it does not solve it.** The persona manipulation — the strongest candidate rescue — leaves idea-level generation narrowing intact (pooled richness 0.75, p = .004, indistinguishable from baseline) while nearly closing the *wording* gap: personas make models sound more varied without making them think more variedly. On the filtering side the structured conditions actively *strengthen* review compression (baseline δ ≈ −0.3 pooled → −0.9 at one_at_a_time) and increase the displacement of AI reviews from human ones. There is no condition in which either stage reaches human diversity.

**5. Which AI matters — but not in the predicted order.** The pre-specified capability ordering (Claude < Gemini < GPT < Human) fails on both stages; the defensible statement is "humans above every model." The texture that survives: **Claude** covers the human idea-space fully but with clumped, repetitive proposals; **Gemini** is the narrowest and the only displaced model on the generation side, yet the least compressed reviewer at baseline; **GPT** is unremarkably in between and geometrically the most human-like in position. Model choice shifts *which* facet of diversity you lose, not *whether* you lose one.

**Limitations to state.** Samples are small (23 per group; per-model generation contrasts are underpowered and the pooled contrasts carry the inference). The pooled baseline generation effect on spread/richness requires style normalization to detect — on raw text it is hidden by *opposing* per-model style artifacts that cancel in the pool (SI-2, pattern B) — while coverage and evenness narrowing are robust on both text branches. Review-panel effects, while extraordinarily consistent, are small in absolute units, and review-cloud displacement is exploratory. Human evenness reference values are condition-specific by construction (the chance benchmark includes each condition's AI reviews) and are never compared across conditions. All results concern one scientific domain, one proposal format, and three models at one point in time.

**The one-sentence version.** *Across five statistically independent facets, three elicitation strategies, and three frontier models, AI systems reproduce the competent center of human scientific search while thinning its edges — proposing fewer genuinely distinct ideas within the same topical territory, and reviewing them with less independent judgment than the smallest human panel — and no prompting strategy tested restores either loss.*

---

## SI-1. Interleaving: does either group hold territory the other never touches?

A natural question about all of the above: do the coverage and displacement results mean humans and AI occupy *separate regions* — ideas or judgments the other side simply never produces? This supplementary analysis answers it directly and descriptively (no significance testing; the point is geography, not inference). For every proposal (or every review, within its own proposal's panel), we measure the distance to its nearest neighbor **from the other group**, and benchmark against human-to-human spacing. The yardstick is the 90th percentile of human→nearest-other-human distance; by construction, ~10% of human items exceed it against their own group, so shares near 10% mean "no more exclusive than humans are from each other."

**Table SI-1 — Exclusive-territory shares and nearest-neighbor distances (pooled AI, rephrased branch).**

| Statistic | | baseline | one_at_a_time | persona |
|---|---|---|---|---|
| **Proposals** | human-only fringe (human proposals no AI proposal approaches) | **22%** | **18%** | **26%** |
| | AI-only pocket (AI proposals no human proposal approaches) | 9% | 4% | 8% |
| | AI proposal → nearest human proposal (median) | 0.041 | 0.035 | 0.038 |
| | human proposal → nearest other human (median; yardstick base) | 0.048 | 0.048 | 0.048 |
| | human proposal → nearest AI proposal (median) | 0.046 | 0.048 | 0.046 |
| **Reviews** | human-only fringe (human reviews no AI review approaches) | **0%** | **0%** | **0%** |
| | AI-only pocket (AI reviews no human review approaches) | 12% | 4% | 6% |
| | AI review → nearest human review (median) | 0.035 | 0.033 | 0.034 |
| | human review → nearest other human review (median; yardstick base) | 0.036 | 0.036 | 0.036 |
| | human review → nearest AI review (median) | 0.030 | 0.030 | 0.031 |

*Reference: ~10% of human items exceed the yardstick against their own group by construction. Pooled AI is subsampled to n = 23 for proposals (200 draws) and uses all 15 AI reviews per proposal for reviews. Per-model rows: `facet_interleaving.csv`. Panels: `results/figures/synthesis/{text_version}/si_interleaving_{proposals,reviews}.png`.*

**Reading, proposals — a real human-only periphery, no AI-only territory.** The typical human proposal has an AI proposal about as close as its nearest human peer (0.046 vs 0.048), and AI-only pockets sit at or below the 10% reference: AI proposes nothing humans don't approach. But **18–26% of human proposals have no AI proposal within normal human spacing — roughly double the by-construction reference** — and, notably, the fringe is *largest under persona* (26%). This is the granular form of the geometric-coverage result (§2.5): the narrowing of generation is territorial. About one human proposal in five occupies ground the equal-sized AI pool simply does not reach.

**Reading, reviews — complete interleaving; no territory lost on either side.** *Every* human review has an AI review within normal human spacing (fringe = 0% in all conditions) — indeed the closest other opinion to any given human review is usually an AI review (0.030), closer than the nearest fellow human (0.036). AI-only pockets are at or below reference. So the significant review displacement (§3.5) is not territorial: it is a subtle, systematic *accent* — a small shared component carried by every AI review — detectable only because the whole-cloud test runs on 430 reviews. (Note that review MMD², 0.007–0.016, is *smaller* than the non-significant proposal-side MMD², 0.03–0.06; the review result owes its stars to statistical power, not to a large shift.)

**Together, the sharpest one-line contrast in the study:** *on the generation side, AI loses territory — a fifth of the human idea-space goes unvisited; on the filtering side, AI loses no territory at all — only independence.* This is also why the two stages need different remedies: generation narrowing calls for sources of genuinely peripheral ideas, filtering narrowing calls for genuinely independent judges.

---

## SI-2. The original-text branch: full results, and what the style contrast measures

All main-text results use the `rephrased` branch, in which every proposal and review is rewritten into one neutral house style before embedding, so that differences in *wording habits* cannot masquerade as differences in *ideas*. The `original` branch repeats the entire battery on the raw, unrephrased text. It is reported here in full — not merely as a robustness check, but because the *difference* between the two branches is itself a measurement: any effect present on both branches lives in the ideas; any effect present only on raw text lives in the prose.

### Table SI-2a — Generation, original text: AI ÷ Human diversity retained

| Facet (metric) | Condition | Claude | Gemini | GPT | **Pooled AI** |
|---|---|---|---|---|---|
| **Spread** | baseline | 0.70 \*\*\* | 1.52 ns | 0.58 \*\*\* | **1.02 ns** |
| | one_at_a_time | 0.17 \*\*\* | 0.14 \*\*\* | 0.17 \*\*\* | **0.28 \*\*\*** |
| | persona | 0.72 \*\*\* | 0.48 \*\*\* | 0.67 \*\*\* | **0.69 \*\*\*** |
| **Richness** | baseline | 0.87 \*\*\* | 1.08 ns | 0.82 \*\*\* | **0.96 ns** |
| | one_at_a_time | 0.65 \*\*\* | 0.64 \*\*\* | 0.65 \*\*\* | **0.69 \*\*\*** |
| | persona | 0.88 \*\*\* | 0.78 \*\*\* | 0.85 \*\*\* | **0.86 \*\*\*** |
| **Evenness**† | baseline | AI clumped \*\* | ≈ chance ns | AI clumped \*\* | **AI clumped \*\*\*** |
| | one_at_a_time | AI clumped \*\* | AI clumped \*\* | AI clumped \*\* | **AI clumped \*\*\*** |
| | persona | AI clumped ns | AI clumped \*\* | AI clumped \*\* | **AI clumped \*\*\*** |
| **Dimensionality** | baseline | 1.14 ns | 0.31 ns | 1.12 ns | **0.79 ns** |
| | one_at_a_time | 1.28 \* | 1.23 ns | 0.98 ns | **0.49 \*\*\*** |
| | persona | 1.08 ns | 0.94 ns | 0.95 ns | **0.89 \*** |
| **Coverage, geometric** | baseline | 0.74 ns | 0.39 \*\* | 0.52 \* | **0.60 \*\*\*** |
| | one_at_a_time | 0.43 \*\* | 0.39 \*\* | 0.61 \* | **0.64 \*\*\*** |
| | persona | 0.91 ns | 0.96 ns | 0.83 ns | **0.89 \*** |
| **Coverage, domain** (regions) | baseline | 1.14 ns | 1.14 ns | 0.57 \* | **0.99 ns** |
| | one_at_a_time | 0.29 \*\*\* | 0.29 \*\*\* | 0.29 \*\*\* | **0.29 \*\*** |
| | persona | 0.71 ns | 0.57 ns | 0.71 ns | **0.65 \*\*** |

† Human excess −0.08 to −0.14 (more even than chance) vs. pooled AI +0.07 to +0.11, as on the rephrased branch.

### Table SI-2b — Filtering, original text: Cliff's δ (AI panel − human panel)

| Facet | Condition | Claude | Gemini | GPT | **Pooled AI** |
|---|---|---|---|---|---|
| **Spread** | baseline | −0.57 \*\* | −0.22 ns | −0.74 \*\*\* | **+0.04 ns** |
| | one_at_a_time | −1.00 \*\*\* | −0.91 \*\*\* | −1.00 \*\*\* | **−0.91 \*\*\*** |
| | persona | −1.00 \*\*\* | −1.00 \*\*\* | −1.00 \*\*\* | **−0.91 \*\*\*** |
| **Richness** | baseline | −0.57 \*\* | −0.13 ns | −0.74 \*\*\* | **+0.04 ns** |
| | one_at_a_time | −1.00 \*\*\* | −0.91 \*\*\* | −1.00 \*\*\* | **−0.91 \*\*\*** |
| | persona | −1.00 \*\*\* | −1.00 \*\*\* | −1.00 \*\*\* | **−0.91 \*\*\*** |
| **Evenness** (δ > 0 = AI clumpier) | baseline | +0.57 \*\* | +0.13 ns | +0.74 \*\*\* | **+0.04 ns** |
| | one_at_a_time | +1.00 \*\*\* | +0.91 \*\*\* | +1.00 \*\*\* | **+0.91 \*\*\*** |
| | persona | +1.00 \*\*\* | +1.00 \*\*\* | +1.00 \*\*\* | **+0.83 \*\*\*** |
| **Dimensionality** | baseline | +0.64 \*\* | +0.36 \* | +0.64 \*\*\* | **+0.36 ns** |
| | one_at_a_time | +0.45 \* | −0.00 ns | +0.36 \* | **−0.27 ns** |
| | persona | +0.73 \*\* | +0.18 ns | +0.64 \*\* | **−0.36 ns** |
| **Coverage** | baseline | −1.00 \*\*\* | −1.00 \*\*\* | −0.73 \*\*\* | **−0.91 \*\*\*** |
| | one_at_a_time | −0.89 \*\*\* | −0.90 \*\*\* | −0.50 \*\* | **−0.73 \*\*\*** |
| | persona | −0.90 \*\*\* | −1.00 \*\*\* | −0.91 \*\*\* | **−0.82 \*\*\*** |

### Table SI-2c — Where the two branches diverge tells you what is style

| Quantity | rephrased (ideas only) | original (ideas + prose) |
|---|---|---|
| Proposal displacement (MMD², pooled) | 0.032–0.062, all ns | 0.069–0.204, all \*\* (every model \*\*\*) |
| Review displacement (MMD², pooled clouds) | 0.007–0.016 | 0.247–0.273 (~20× larger) |
| Review coverage of the human span (pooled δ) | **+0.37 to +0.44 \*\*** (AI blankets the span) | **−0.73 to −0.91 \*\*\*** (AI misses the span) |
| Review interleaving: human-only fringe / AI-only pocket | 0% / 4–12% | 51–69% / 33–80% |
| Proposal interleaving: human-only fringe | 18–26% | 13–31% |
| Lexical distinct-2 (Human vs pooled models) | 0.741 vs 0.60–0.72 | 0.681 vs 0.43–0.63 |

### Reading: three patterns

**A. Style-robust conclusions (present on both branches — these are about ideas).**
Geometric coverage narrowing (original is *stronger*: pooled 0.60–0.89, significant in all conditions); evenness — human sets more even than chance, AI sets clumped, pooled \*\*\* in all six branch×condition cells; filtering compression under one_at_a_time and persona (δ ≈ −0.9 to −1.0 on both branches) and for Claude/GPT at baseline; the Gemini-at-baseline parity anomaly (replicates exactly on raw text: δ = −0.13 to −0.22, ns); and the human-only proposal fringe (13–31% across branches). Everything the synthesis (§4) leans on hardest survives the branch change.

**B. Style-dependent magnitudes (direction survives; size is distorted by prose).**
Raw text distorts the spread/richness facets in *both* directions, and the pooled baseline null (1.02/0.96 ns) is a cancellation, not an agreement: on raw text Claude and GPT are significantly narrower (0.58–0.87 \*\*\*) while Gemini's verbose, varied prose makes it appear *wider than human* (spread 1.52) — opposing style artifacts that sum to zero in the pool. In the other direction, one_at_a_time's raw ratios (0.14–0.28) wildly *overstate* narrowing because each model answers repeated single requests in a near-template voice; rephrasing brings those cells back to 0.45–0.81. The rephrased branch sits between the two distortions, which is precisely why it is the primary: **raw prose can hide idea-level narrowing (varied wording, repeated ideas) or manufacture it (templated wording, distinct ideas).**

**C. Style-only effects (vanish after rephrasing — these are about prose, not ideas).**
On raw text, every AI model's proposal cloud is significantly displaced from the human cloud (MMD² up to 0.28, all \*\*\*), AI review panels *fail to cover* the human review span (δ ≈ −0.9), and the interleaving statistics show outright segregation (up to 80% of AI reviews in "AI-only pockets," up to 69% of human reviews in a "human-only fringe"). After style normalization, all of this collapses: displacement falls ~20-fold, review coverage flips to *exceeding* the human self-benchmark, and the clouds interleave completely (SI-1). The inference is clean and quotable: **AI text is strongly segregated from human text by style; AI *ideas* are not segregated from human ideas — they are an interleaved, thinned subset.** This also settles the interpretation of the small residual review displacement in §3.5: the "accent" is overwhelmingly stylistic, and what remains after rephrasing is its faint semantic residue.

*Sources: same table paths with `text_version = original`; SI figures for the original branch under `results/figures/synthesis/original/`.*

---

## SI-3. Score-level decision analysis: does the lost disagreement matter for decisions?

A fair challenge to the filtering results runs: *if each AI review covers everything the human reviewers say (SI-1), does the loss of panel diversity matter at all — could review simply be automated?* The facet metrics measure review *text*; funding decisions consume review *scores*. This analysis therefore asks three questions of the numeric `overall_score` data (1–5 scale; never previously used by the diversity pipeline): **(i)** do AI panels disagree less in their scores, proposal by proposal? **(ii)** does human score disagreement predict where human and AI mean scores diverge — i.e., is disagreement carrying information? **(iii)** would AI panels *rank* the proposals differently than the human panels did?

**Method in brief.** For each proposal, the human panel's score spread (standard deviation) is compared with AI panel spreads computed at *matched panel size* (averaging over all same-sized subsets of each model's five reviews), combined across proposals with the same paired test as the facet battery. Rankings compare each panel's mean score across proposals (Spearman correlation). Crucially, the rank comparison is read against a **human-vs-human reliability ceiling**: how well half of the human panel's ranking predicts the other half's, estimated over 500 random splits.

**Data caveats, stated first.** Only 13 of 23 proposals have ≥ 2 numerically scored human reviews (9 have none); variance analyses use that subset, mean/rank analyses the 14 with ≥ 1. Human scores are shared across conditions and text branches (they predate the pipeline). AI reviewers never award a 1 (AI range 2–5 vs human 1–5) — a range restriction that itself depresses AI spreads. Small n makes the correlational results exploratory.

### Table SI-3 — Score disagreement and rank agreement (rephrased masters; scores branch-invariant)

Human panel score SD = **0.74** in every condition (shared reviews). δ = Cliff's paired effect (AI − Human); negative = AI panels less variable.

| Condition | | Claude | Gemini | GPT | **Pooled AI** |
|---|---|---|---|---|---|
| baseline | panel score SD | 0.31 (δ −0.54 \*) | 0.58 (δ −0.08 ns) | 0.41 (δ −0.54 \*) | **0.51 (δ −0.23, p=.09)** |
| | rank agreement ρ | +0.08 ns | +0.45 ns | +0.73 \*\* | **+0.46 (p=.10)** |
| one_at_a_time | panel score SD | **0.08 (δ −1.00 \*\*\*)** | 0.32 (δ −0.69 \*\*) | **0.10 (δ −1.00 \*\*\*)** | **0.34 (δ −0.85 \*\*)** |
| | rank agreement ρ | +0.28 ns | +0.34 ns | +0.52 (p=.06) | **+0.44 ns** |
| persona | panel score SD | 0.25 (δ −0.85 \*\*) | 0.17 (δ −0.83 \*\*) | 0.21 (δ −0.69 \*\*) | **0.29 (δ −0.85 \*\*)** |
| | rank agreement ρ | +0.37 ns | +0.33 ns | +0.39 ns | **+0.43 ns** |

*Reference for the rank rows: the human split-half reliability ceiling is **ρ ≈ +0.40** — half the human panel predicts the other half's ranking no better than this, so values near 0.40 are at the measurable maximum. Disagreement-predicts-divergence correlations (question ii): ρ between −0.40 and +0.43, all ns at n = 13 — inconclusive. Full rows: `results/tables/cross_condition/reviews/score_decision_analysis.csv`; code and printed output: notebook `03_facets_reviews`, section "Score-level Decision Analysis (SI)".*

### Findings

**(i) The disagreement collapse replicates in the scores — the channel a committee actually consumes.** Human panels disagree substantially (SD 0.74 on a 5-point scale: think a 2 and a 4 on the same proposal). AI panels compress this two- to ten-fold, near-deterministically under structured elicitation — Claude under one_at_a_time scores with near-total unanimity (SD 0.075, lower for *every* scoreable proposal). The condition ordering mirrors the semantic facets exactly (baseline mildest, one_at_a_time strongest), and **Gemini-at-baseline is again the lone exception** (δ = −0.08, ns) — that anomaly now replicates across review semantics, both text branches, and numeric scores, arguing strongly that it is a real elicitation effect rather than a processing artifact.

**(ii–iii) But no demonstrable decision divergence — and the honest reason why.** Pooled AI rankings correlate with the human ranking at ρ = 0.43–0.46, which would look like substantial disagreement — except the human panel's *own* split-half ceiling is ρ ≈ 0.40. AI panels track the human ranking as well as half the human panel tracks the other half; with 13–14 scoreable proposals and 1–4 scores each, "AI ranks differently" and "the human ranking is too noisy to rank against" are indistinguishable. GPT at baseline even exceeds the ceiling (ρ = 0.73). The disagreement-predicts-divergence test is likewise inconclusive at this n.

### Interpretation

This analysis strengthens one half of the filtering claim and honestly bounds the other. **Strengthened:** the variance channel — flagged divisiveness, triggered discussion, confidence calibration — is measurably empty in AI panels, in the numeric currency committees actually use, and no elicitation strategy tested restores it. **Bounded:** we cannot show, from this sample, that the resulting *rankings* differ from human ones; on point estimates, AI panels are as human-like as the human panels are self-consistent. The automation question therefore turns on what a panel is *for*: if it is a scoring machine, this data offers no evidence of harm; if it is a deliberation input — where disagreement selects which proposals get argued about — the input is gone. Resolving whether the lost disagreement changes *outcomes* requires either the claim-level uniqueness analysis (do humans catch load-bearing points AI misses?) or a larger corpus of numerically scored human reviews; both are natural next studies.

---

## 5. Statistical notes for the general reader

- **Permutation test.** To ask whether two groups differ more than chance allows, we repeatedly shuffle the group labels (10,000 times) and recompute the difference. The p-value is the fraction of shuffles producing a gap as large as the real one. No distributional assumptions.
- **Cliff's δ (paired).** For each of the 23 proposals we ask: did the AI panel come out lower or higher than the human panel? δ is the balance of those outcomes: −1 (lower every time) to +1 (higher every time). It measures *consistency of direction*, complementing the raw magnitude. Its p-value comes from the exact paired Wilcoxon test, whose floor at n = 23 is ~2×10⁻⁷ — values at that floor mean "as significant as this design can express."
- **Effective numbers (Vendi score).** A set's similarity structure is converted into "this set of 23 behaves like N fully distinct items." It is the same mathematics ecologists use to say a forest with 23 trees of highly overlapping species behaves like 3 effective species.
- **Chance references (nulls).** Wherever a metric has no natural zero, we manufacture the honest benchmark: random same-sized draws from the pooled data (for clumping), one random half of the human set covering the other (for coverage), or leave-one-out self-coverage (for review panels). "Significant" always means "outside what those benchmarks produce."
- **Confidence intervals.** Set-level metrics use leave-one-out (jackknife) intervals — recompute 23 times, each time omitting one proposal. Pooled-AI values use 1,000 subsamples of 23 drawn without replacement. We never resample with replacement, which would inject duplicates into metrics that are exquisitely sensitive to duplicates.
- **Multiple testing.** With ~7 metric families × 3 models × 3 conditions × 2 stages, some "significant" results would arise by chance. Three comparisons were designated primary in advance and read at face value; every other p-value shown has been inflated by the Benjamini–Hochberg procedure to control the expected fraction of false discoveries.
- **Equal sample sizes everywhere.** Every diversity metric grows with the number of items measured, so all comparisons — including the pooled-AI ones and all union counts — are made at exactly 23 vs 23.

---

## Appendix: audit and reproducibility

- **Audit trail.** The statistical pipeline was audited line-by-line against the design specification (2026-07-15/16): the review-side coverage and evenness pairings, the trend-test direction, domain-coverage inference, FDR family structure, and the evenness-slope metric were corrected; presentation was subsequently re-oriented so that every panel reads "up/right = more diverse" (Direction Rule), with statistics verified byte-identical before and after the visual redesign. AI reviews were regenerated with the corrected prompt on 2026-07-16 and notebooks 03–04 recomputed; proposal-side inputs (embeddings, group structure) were verified unchanged, so generation results carry over exactly.
- **Superseded result.** An earlier run (incorrect review prompt) showed baseline AI review panels as *more* diverse than human panels; that finding did not survive the prompt correction and should not be cited.
- **Sources.** Tables: `results/tables/{condition}/{task}/{text_version}/facet_diversity_tests.csv` (+ `facet_fingerprint.csv`, `facet_interleaving.csv`, `facet_diversity_gradient.csv`, curve/null parquets) and `results/tables/cross_condition/reviews/score_decision_analysis.csv` (SI-3). Figures: `results/figures/.../facet_fingerprint.png`, per-facet panels, `results/figures/synthesis/{text_version}/fig1–fig6` + `fig2b_human_ai_slopegraph` (+ supplements), and the SI interleaving panels `si_interleaving_{proposals,reviews}.png`. Specs: `docs/plans/diversity_facets_design_spec_v2.md`, `docs/plans/facet_visualization_redesign_spec.md`.
