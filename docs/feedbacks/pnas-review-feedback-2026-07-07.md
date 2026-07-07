# Review of the "AI compresses scientific search" study for PNAS

*Reviewer feedback prepared 2026-07-07. Based on `docs/plans/analysis_plan.md`, the current result tables in `results/tables/rephrased/minimal/` and `results/tables/quality/minimal/`, the generation code (`gen_proposals.ipynb`, `src/prompt_templates.py`), and the draft `docs/drafts/writeup-jun26.md`.*

---

## Bottom line up front

The study has:

- **One genuinely strong, PNAS-worthy result** — AI-generated *proposal sets* and AI *review sets* are dramatically less diverse than human ones (Cliff's δ ≈ −0.7 to −1.0, robust to permutation tests).
- **One result the current corrected analysis does not support** — literature-relative *novelty*: every continuous novelty metric is null after correction.
- **One identification problem that, as the design currently stands, undermines the causal claim** ("if we automate science we lose diversity").

The fixes are mostly additional analyses plus one additional generation run you've already scoped (`high_temperature`, independent sampling) — not a teardown.

**Critical precondition:** the draft (`writeup-jun26.md`) reports numbers that no longer match the data. Draft Result 1 says Human pairwise = 0.4429, Claude = 0.0337; current data = 0.3411 and 0.1523. Draft Result 2 says Claude region breadth = 1, entropy = 0.0155; current = breadth 4, entropy 1.09 (and **not significant**). The draft's Results section must be fully rewritten against the current tables before anything else.

---

## (1) Methodological errors that *undermine* the central result

### A. The generation design confounds "AI" with "one model, one completion, one temperature, one draw" — the identification failure

This is the one that can sink the paper. The comparison is:

- **Human set:** 23 proposals from **23 independent scientists**, each contributing one idea drawn from a different career, lab, and subfield.
- **Each AI set:** 23 ideas from **a single model, in a single completion**, prompted `"Generate 23 research ideas … all different from each other"` at `temperature=0.7` (`src/prompt_templates.py:44`, `gen_proposals.ipynb`).

So the contrast is *between-person variance across 23 humans* vs *within-one-autoregressive-sample variance*. A referee will say: you have not shown that AI's idea *distribution* is narrow; you've shown that **asking one model once for a batch of 23 items returns a thematically anchored batch.** That is a sampling-design artifact, not a property of "AI for science." The natural counterfactual for *automated* science — many independent agents/samples, possibly at higher temperature — is exactly what the measured design suppresses. Because a trivial, non-AI explanation (single draw vs 23 draws) fully accounts for the effect, the causal claim is currently **unidentified**. That is why this undermines rather than weakens.

**What partially rescues you (foreground this):** pooling three *different frontier model families* and bootstrap-subsampling to n = 23 still yields 0.152 vs human 0.341 (δ = −0.83, perm p = 0.0001). Three independent vendors is a crude form of independent sampling, and diversity still halves. That rebuts the "single context" critique — but only for *between-model* diversity, not *within-model resampling*.

**Fix (mandatory):** actually run and analyze the independent-sampling condition — each model's 23 ideas as **23 separate calls** (no shared context) — plus the planned `high_temperature = 0.8` and `persona` conditions. If diversity still collapses under independent, high-temperature, persona-primed sampling, the claim becomes airtight and the paper becomes more interesting (see §2).

### B. The headline p-values violate independence; lead with permutation tests

The proposal-level diversity metric (e.g. `mean_pairwise_dist` per proposal = mean distance from that proposal to all others in its group) is derived from a shared pairwise-distance matrix. The 23 values within a group are **not independent**. Running Mann–Whitney + Holm across them and reporting `p = 3.5e-09` overstates evidence by treating correlated quantities as i.i.d. The **group-level permutation test you already compute is the correct inference**, and the effect survives it (perm p = 0.0001–0.01). This is a *reporting* error, not fatal — but as written, the strongest table leans on an invalid test. **Report permutation p-values as primary and drop/footnote the MW-Holm values** for all derived-from-matrix metrics.

### C. The novelty leg is null — you cannot currently claim "AI proposals are less novel"

After correction, **not one continuous novelty metric distinguishes human from AI**:

| Metric | Human | AI | Effect | Corrected sig |
|---|---|---|---|---|
| Mean-kNN k10 | 0.115 | 0.099 | δ = −0.19 | q = 0.80 (n.s.) |
| novelty_z | 0.732 | 0.547 | δ = −0.15 | q = 0.80 (n.s.) |
| element_novel_10 | 0.217 | 0.193 | δ = −0.26 | q = 0.13 (n.s.) |
| MeSH coverage (mean) | 80.0 | 85.1 | AI **higher** | n.s. |
| BERTopic region coverage | — | — | — | n.s. after Holm |
| Grid entropy (coverage) | 0.330 | 0.364 (boot) | AI slightly **broader** | p = 0.77 |

The **only** surviving literature-anchored signal is a binary outlier count (Human 7/23 vs AI 3/69 in mean-10NN literature outliers, q = 0.006).

Draft Results 2 and 3 ("Human proposals are more novel relative to literature," "cover broader regions and topics") are **not supported.** Two honest options (prefer the first):

1. **Reframe around what's robust:** AI compresses *local diversity/redundancy* at generation and *diversity of evaluative filters* at review. Novelty becomes a *nuance*: AI proposals aren't closer to the literature on average, but humans supply almost all the literature-space *outliers* — the **tail**, not the mean, collapses.
2. Substantially strengthen novelty measurement (different reference corpus, contamination-controlled, alternative operationalizations) — riskier and slower.

Either way, the current draft's novelty claims must go.

### D. Review-diversity is confounded by reviews-per-proposal

Human proposals get **3.5–3.9 reviews each**; the AI condition has **exactly 3** (one Claude, one Gemini, one GPT). Several "significant" review-diversity metrics — `span90` (a 90th-percentile extreme), `medoid_dist`, `sparseness`, `global_centroid_dist` — are **upward-biased with n**. Tellingly, in Y1 the n-robust metrics (`mean_pairwise`, `remote_clique`) did *not* pass FDR while the n-sensitive ones did. Y2 is stronger (even `mean_pairwise` significant, δ = 1.0), but the confound is real. **Fix: subsample human reviews to 3 per proposal** (bootstrap over which 3), or model n as a covariate, and re-report. The paired-slope figure (`results/figures/quality/minimal/ncems_criteria/quality_review_diversity_y2_paired_slopes.png`) is persuasive but must survive n-matching.

Conceptual note: AI review "diversity" is measured across **three vendors**, a *generous* (pro-diversity) setup for AI. The more policy-relevant automation scenario — one lab runs *one* model for all reviews — is the strongest version of the worry and is currently **not measured** (per-model within-proposal diversity is inestimable at 1 review/model). Have each model review each proposal 3× (temperature sampling) to get within-model review diversity.

### E. The Gemini-rephrasing step is an uncontrolled homogenization confound

All proposals and reviews are passed through Gemini to "standardize style." This pulls texts toward one model's distribution, with no guarantee it compresses human and AI equally. The style-classifier (AUROC 0.52) shows it removed *style* signal — good — but says nothing about *semantic* homogenization, which is exactly what the embeddings measure. There is currently **no rendered non-rephrased (`baseline(minimal)-original`) diversity comparison.** **Fix: run the identical diversity pipeline on the original (un-rephrased) texts and show the ordering holds.**

### F. (Minor but will be raised) The six diversity metrics are one finding measured six ways

Pairwise, centroid, global-centroid, MST, sparseness, and Chamfer/NN are near-monotone transforms of "spread in embedding space." Six is not six independent confirmations. The one metric that measures *area coverage* rather than average distance — grid entropy — is **null**. State that these are correlated views of dispersion (report their intercorrelation), pick 2–3 as primary, and be honest that *total 2-D coverage* does not differ — the collapse is in **local density/redundancy**, not footprint. The bimodal pairwise-distance distribution confirms this: all groups share the ~0.7 between-cluster gap; AI piles up near 0 in the low mode.

---

## (2) The most critical missing pieces for PNAS

In rough priority order:

1. **Run the generation-mechanism conditions already scoped, and analyze them.** Independent per-idea sampling, `temperature=0.8`, and `persona`. This is the difference between "one query returns a clustered batch" (not PNAS) and "AI's idea distribution is intrinsically compressed, and here's what does/doesn't recover it" (PNAS). **If you can show a *lever* — e.g., persona/high-temperature partially restores diversity but never reaches human levels — that is a far stronger paper than a pure deficit finding.** Biggest opportunity.

2. **Tie diversity loss to something that matters.** The "so what" is currently asserted, not shown. Options: (a) funding outcomes — but among the 23 human proposals, funded (14) vs not (9) show **no** significant novelty/outlier difference (all MW p > 0.35; n far too small); (b) the planned **blinded external expert evaluation** of top human vs AI proposals — essential and not yet done. Without a value link, a reviewer says "less diverse ≠ worse."

3. **Embedding-model robustness.** The entire result lives in one anisotropic encoder (BioLinkBERT-large). Replicate the core diversity contrast in ≥1 independent space (SPECTER2 for scientific documents, or a modern sentence-transformer / API embedding). Three spaces at δ ≈ −0.8 = bulletproof.

4. **Multiple-comparisons discipline / pre-registration.** Many metrics, clustering methods (Ward, GMM, BERTopic, LDA), and corrections were tried. Designate a *small* confirmatory set (e.g., pairwise distance + NN isolation for generation; n-matched mean-pairwise for review) as primary; mark the rest exploratory/robustness; freeze a pre-registration before the new conditions.

5. **Generality.** One funding call, one biomedical foundation, n = 23, three model versions at one date. Minimum: a candid limitations paragraph on single-call/single-domain and model-version dependence. Stronger: a second call or domain to show the compression is not NCEMS-specific.

6. **Contamination argument for the novelty corpus.** The corpus runs to 2026-05-25 and the models trained on much of PubMed. Make the contamination argument explicit and tested (e.g., recency of nearest neighbors — Analysis 3.8, currently null). Right now this cuts against the framing.

---

## (3) The most effective graphs to make the point

Existing figures are notebook-diagnostic quality (multi-panel, embedded tables, log axes). PNAS needs 3–4 clean, self-contained figures.

**Figure 1 — The two-stage compression, honestly.** Prototype built from the real numbers: `results/figures/review_feedback/PROPOSED_two_stage_compression_forest.png`. A single forest of Cliff's δ (AI − Human) grouped into three bands — *generation-diversity* (strongly negative, filled = significant), *generation-novelty* (near zero, open = n.s.), *review-diversity* (strongly negative). One panel that tells the whole story **and** disarms reviewers by not overclaiming novelty. Best candidate for the lead figure. Pair with a small conceptual schematic of the two-stage funnel (generate → filter).

**Figure 2 — Proposals on the literature map.** `results/figures/rephrased/minimal/literature_umap_with_bertopic_regions.png` is the most intuitive "AI clusters" visual. Clean it: move region text to a legend, enlarge/deduplicate proposal markers, split into **two side-by-side panels** (human vs pooled-AI, identical axes) so the AI point cloud visibly contracts. Ring the literature-space outliers (the one surviving novelty signal — humans own the tail).

**Figure 3 — Review paired-slopes, n-matched.** `results/figures/quality/minimal/ncems_criteria/quality_review_diversity_y2_paired_slopes.png` already shows every proposal's human reviews more diverse than its AI reviews (every slope descends). Re-render after subsampling humans to 3 reviews; keep 1–2 metrics.

**Figure 4 — The recovery/lever panel (once conditions run).** Diversity as % of human on the y-axis across conditions: baseline → high-temp → persona → independent-sampling → human reference at 100%. If AI never reaches the human line, that's the thesis in one bar chart, and it neutralizes the mechanism-identification critique (§1A).

**Presentation move throughout:** report a **"diversity retained"** ratio (AI ÷ human) so magnitude is legible to a general audience — e.g., "AI proposal sets retain ~45% of human pairwise diversity and ~30% of human nearest-neighbor isolation."

---

## Things not asked but critical

- **Reconcile the draft with current results before writing another sentence.** The draft is numerically a different experiment; that erodes confidence.
- **Reframe around the two robust legs; make novelty a nuance, not a pillar.** "AI collapses the *tails* and the *local diversity* of both idea generation and evaluation" is true, defensible, and still a big claim.
- **Lead the diversity inference with permutation, not MW-Holm** (§1B).
- **Positioning vs. prior work.** Doshi & Hauser (2024) and Hao et al. (2024) already show AI raises individual quality while narrowing collective diversity. The novelty here is the *high-stakes, confidential grant* setting and the *two-stage* (generate + review) design. Say that sharply.
- **Model/version reproducibility.** Freeze and report exact model IDs, dates, temperatures, prompts, and that results are conditional on a 2026 snapshot.

---

## Suggested execution order

1. Rewrite Results against current tables; reframe thesis (robust diversity legs; novelty as tail-collapse nuance).
2. Re-report diversity with permutation-primary inference; n-match review diversity.
3. Run non-rephrased robustness + second embedding space for the core diversity contrast.
4. Run independent-sampling + high_temperature + persona generation conditions; build the recovery figure.
5. Blinded external expert evaluation for the value link.
6. Pre-register confirmatory set; freeze figures/tables.

---

# Follow-up deliverables (2026-07-07)

Three items were produced after the initial review: (a) a rewritten Results section, (b) two cleaned figures plus a new n-matched re-analysis, and (c) an analysis spec for the generation-condition experiments. Key update: **the review-diversity n-confound (§1D) turned out to be harmless — the effect survives n-matching.** Details below.

## (a) Rewritten Results section

Written against the current tables at `docs/drafts/results-rewrite-2026-07-07.md`. It reorganizes into three honest results — (1) generation diversity collapses (robust), (2) novelty is null on average but humans own the literature tail/outliers, (3) review diversity collapses and AI reviews are mutually interchangeable — leads all diversity inference with permutation tests, and drops the draft's unsupported novelty/coverage claims.

## (b) New figures

All saved under `results/figures/review_feedback/`.

### Fig A — Two-stage compression forest (lead-figure candidate)
`PROPOSED_two_stage_compression_forest.png`. Cliff's δ (AI − Human) across three bands: generation-diversity (strongly negative, significant), generation-novelty (near zero, n.s.), review-diversity (strongly negative). Tells the whole story in one panel and pre-empts the "you overclaim novelty" critique.

### Fig B — Literature map, human vs AI-by-model
`PROPOSED_literature_map_two_panel.png`. Proposals projected on the fixed 39,538-abstract literature UMAP. Left: humans scatter and hold 7 of the 10 literature-space outliers (magenta rings). Right: AI colored by model — each model collapses into a few tight knots, with only 3 outliers total. **Honest caveat baked into the design:** the AI *total* footprint (convex-hull area 36.6) is similar to human (39.5), so the figure is titled around *local clustering + tail collapse*, not "smaller footprint" — matching what the statistics actually support (grid entropy null; outlier count significant).

### Fig C — n-matched review diversity (resolves §1D)
`PROPOSED_review_diversity_nmatched.png`. Recomputed review diversity after subsampling each proposal's human reviews to exactly 3, matching the AI count (mean over 500 draws; 19 proposals with ≥3 of each). **The effect is essentially unchanged:**

| Metric | Human (n=3) | AI (n=3) | Wilcoxon p | Cliff's δ | % proposals H>AI |
|---|---|---|---|---|---|
| Mean pairwise | 0.043 | 0.033 | 0.0017 | +0.73 | 89% |
| Nearest-neighbor | 0.038 | 0.029 | 0.0024 | +0.73 | 84% |
| Sparseness (medoid) | 0.026 | 0.020 | 0.0024 | +0.74 | 84% |
| Span90 | 0.017 | 0.012 | 0.0028 | +0.70 | 79% |

So the reviews-per-proposal confound does **not** explain the review-diversity result — this *strengthens* the paper. Supporting data: `results/figures/review_feedback/_review_diversity_nmatched_summary.csv` and `_review_diversity_nmatched.csv`. (The original critique in §1D still stands as a reason to *report* the n-matched version; it just no longer threatens the conclusion.)

## (c) Analysis spec — generation-condition experiments (the identification fix for §1A)

**Goal.** Show that the generation-diversity collapse (Result 1) is a property of the model's idea *distribution*, not an artifact of asking one model once for a batch of 23 ideas. This is the single most important addition for PNAS: it converts a confounded contrast into an identified causal claim and, ideally, exposes a *lever* that partially recovers diversity.

**The confound to break.** Baseline = 23 humans (one idea each) vs 1 model × 1 completion producing 23 ideas at temperature 0.7 with an explicit "all different from each other" instruction. Four things vary at once with "human vs AI": number of agents, number of sampling occasions, shared vs independent context, and temperature. The conditions below vary them one at a time.

### Conditions (all use the identical NCEMS call, rephrasing, embedding, and diversity pipeline as baseline)

| ID | Condition | What changes vs baseline | Isolates |
|---|---|---|---|
| G0 | Baseline (done) | — | reference |
| G1 | **Independent sampling** | 23 separate API calls, each returns **one** idea, no shared context; keep temp 0.7 | shared-context / anti-redundancy list effect |
| G2 | **High temperature** | same single-completion batch, `temperature = 0.8` (and 1.0 as a second point) | sampling entropy |
| G3 | **Independent + high-temp** | 23 independent calls at temp 1.0 | upper bound of naive diversification |
| G4 | **Persona** | independent calls, each primed with a distinct human-scientist persona (recent-paper titles/abstracts), matched in count to the 23 humans | agent heterogeneity |
| G5 | **Ensemble-of-models** | pool independent calls across Claude+Gemini+GPT (already partially in `all_ai`) | vendor heterogeneity |

Run each condition **per model** (Claude, Gemini, GPT-5.2), 23 ideas → 23 full proposals, so every condition is directly comparable to baseline and to the 23 humans.

### Design controls
- **Fixed N and bootstrap.** Every condition yields 23 proposals per model; compare to humans at n=23; bootstrap-subsample any pooled set to 23 (1,000 draws), exactly as `compare_proposals_all_ai.ipynb` already does.
- **Same everything downstream.** Reuse the rephrase → BioLinkBERT → distance-matrix → diversity pipeline unchanged so condition is the only moving part. Cache embeddings per condition.
- **Seeds / repeats.** For the stochastic conditions (G2, G3), draw ≥3 independent replicate sets per model so between-run variance is visible; report mean ± range.
- **Cost note.** G1/G3/G4 are 23× more calls than G0 per model (one idea per call). Budget ~23 × 3 models × conditions; cheap relative to the payoff.

### Primary analyses
1. **Diversity vs condition.** For the pre-registered primary metrics (mean-pairwise distance and nearest-neighbor isolation), plot Human reference line and each condition's bootstrap mean ± CI. Primary test per condition = permutation (label-shuffle) vs Human; secondary = vs baseline G0.
2. **"Diversity retained" ratio.** Report each condition's diversity as a fraction of the human value. Headline question: *does any intervention close the gap, and how far?*
3. **Novelty/outliers vs condition.** Re-run the literature-space outlier test per condition — does higher temperature/persona push AI proposals into the human-occupied tail (Result 2)?
4. **Interaction check.** Two-way (model × condition) permutation ANOVA-style test on diversity to confirm the pattern is shared across vendors.

### Interpretation rules (state before running)
- If **G1 ≈ G0** (independent sampling doesn't help): the collapse is intrinsic to the idea distribution — strongest possible support for the thesis; the single-completion critique is dead.
- If **G3/G4 recover toward human but plateau below**: even aggressive diversification can't match distributed human search — a nuanced, more citable result. Build the recovery bar chart (feedback §3, Figure 4).
- If **G3/G4 reach the human line**: the baseline effect was largely a sampling-design artifact; the paper must be reframed around "naive automation compresses, but simple interventions restore diversity." Better to learn this now than in review.

### Deliverable figure
Recovery panel: x = condition (G0→G5), y = diversity as % of human (100% reference line), one series per model, novelty-outlier rate on a twin axis. This single figure answers the reviewer's identification objection and states the paper's practical implication.
