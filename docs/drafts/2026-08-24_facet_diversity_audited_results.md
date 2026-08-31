# Do AI Systems Narrow Collective Scientific Search? Audited Results Across Five Diversity Facets, Two Pipeline Stages, and Three Elicitation Conditions

**Status:** internal results report (audited) · **First written:** 2026-07-16 · **Re-audited against the notebooks:** 2026-08-24
**Data version:** prompt-corrected AI reviews (regenerated 2026-07-16); `rephrased` (style-controlled) text branch is primary throughout, `original` reported as robustness.
**Provenance:** all statistics recomputed by the rebuilt facet pipeline (`02_facets_proposals` → `03_facets_reviews` → `04_synthesis`) after a full audit against `docs/plans/diversity_facets_design_spec_v2.md`; figures follow the direction-aligned conventions of `docs/plans/facet_visualization_redesign_spec.md`. Every number below is traceable to `results/tables/{condition}/{task}/rephrased/facet_diversity_tests.csv`.

**What changed in the 2026-08-24 re-audit** (every table cell in §1 was re-derived from the CSVs the notebooks currently write and reproduced exactly; the corrections below are to descriptions, ranges, and coverage of the analysis set):
1. The primary/secondary split was stated as **three** pre-registered primaries; the pipeline designates **six** (`PRIMARY` in `02`/`03`) and reports all six on `p_raw`. Corrected here and in §5. **Manuscript scope (2026-08-31):** dimensionality is dropped from the paper as a null (§2.4, §3.3), so the manuscript reports **five** primaries — spread, richness, evenness, geometric coverage, and displacement; the pipeline still computes the dimensionality primary and it is retained in this audit record only.
2. The **field axis of the review battery** (`whole` / `strengths` / `weakness`, notebook `03` `CONFIG["fields"]`) was not reported at all. Added as **§3.7**.
3. §2.7 cited a "radius percentile" statistic that no notebook computes; replaced with the fringe statistics that are actually exported.
4. Corrected stale numeric ranges: evenness human excess (§2.3, Table 1a footnote), the kernel-sensitivity count (§2.9), the model-ordering trend summary (Table 1c, §2.9), review coverage magnitude (§3.4), per-model claim-uniqueness range and AI claim count (SI-4), and the between-proposal score SD plus the rank-agreement "plateau" description (SI-6).
5. **New in SI-6, two additions:** (a) the funding AUC now carries a stratified-bootstrap 95% CI and a label-permutation p-value (`decision_outcome.funding_auc_inference`; point estimates unchanged) — the intervals are ~±0.25 wide, so the conclusion is restated as *absence of evidence* rather than a proven null, and `plot_decision_outcome` panel C draws them. (b) The AI and human panels in that AUC were never matched — 15 pooled AI reviews over 23 proposals versus 1–4 human reviews over 14 (11 of them cohort y2) — so a **size- and proposal-matched decomposition** was added (`decision_outcome.matched_funding_auc`, new notebook `03` cells, `decision_outcome_matched_auc.csv`). The AI null survives matching unchanged; the human-vs-AI gap does not survive it and is withdrawn as unpowered.
6. Figure/table inventory in the Appendix brought in line with what `04` writes today (`fig_generation_geometry`, `fig_filtering_panel`, `fig_main_facet_slopegraph`, `si_generation_geometry_umap`, the `fig2_supplement_*`/`fig2b_supplement_*` families, and `results/tables/synthesis/{branch}/double_compression_summary.csv`).

*Path note:* the live tables are `results/tables/{condition}/{task}/{branch}/…`. A `…/{branch}/facet/` subdirectory survives from an earlier pipeline version and is **not** rewritten by the current notebooks — do not read numbers from it.

---

## Reader's guide (start here)

**The question.** When AI systems both *generate* research proposals and *review* them, does the collective search of science narrow — fewer genuinely different ideas proposed, and less independent judgment gate-keeping them?

**The design.** 23 human proposals (two cohorts of biomedical scientists) are compared with 23 proposals from each of three AI models (Claude, Gemini, GPT), under three elicitation conditions: **baseline** (a single request), **one_at_a_time** (ideas requested one per conversation), and **persona** (the model is given a distinct scientist persona per proposal). On the gate-keeping side, each human proposal was reviewed by 2–5 human reviewers (85 human reviews in all, mean 3.70 per proposal) and by 5 AI reviewers per model (345 AI reviews); AI review panels are compared with the human panel *of the same proposal*, at matched panel size. The whole review battery is run three times over a **field** axis — the whole review, its `strengths` section alone, and its `weakness` section alone (§3.7).

**"Diversity" is not one number.** We decompose it into five facets, each answering a different question:

| Facet | Plain-language question |
|---|---|
| **Spread** | How far apart are the ideas from one another, on average? |
| **Richness** | How many *effectively distinct* ideas are there, once near-repeats are discounted? |
| **Evenness** | Are ideas spaced out, or do they pile up in near-duplicate clumps? |
| **Dimensionality** | Along how many independent directions do the ideas vary? |
| **Coverage** | How much of the territory that humans explore does AI reach? (Measured two ways: geometrically in idea-space, and by which regions of the biomedical literature are engaged.) |

A separate **displacement** check (not a diversity facet) asks whether AI occupies a *different place* than humans, or a smaller region *inside* the human territory.

**How to read significance.** Stars mean `*** p<0.001`, `** p<0.01`, `* p<0.05`, `ns` not significant. **Primary comparisons — one headline metric per facet plus the displacement check — are tested at face value.** The pipeline designates **six** primaries (spread `mean_pairwise`, richness `vendi q=1`, evenness `ripley_excess`, dimensionality `participation_ratio`, geometric coverage, and displacement `mmd2`; the `PRIMARY` set in notebooks `02`/`03`, whose `p_fdr` is NaN by design). The manuscript drops dimensionality as a null (§2.4, §3.3) and therefore reports **five**: spread, richness, evenness, geometric coverage, and displacement. Every other test carries a correction for testing many things at once (Benjamini–Hochberg false-discovery-rate control over the whole secondary family within each `task × text_version × field` — 510 tests on the proposal side), so a starred secondary result already accounts for the size of the test battery. Throughout this report, stars on a primary row are `p_raw` and stars on any other row are `p_fdr`. Plain-language explanations of every statistical device appear in §5.

**Two different effect sizes, by design.** Generation compares whole groups (23 vs 23), so effects are **ratios**: *AI ÷ Human diversity retained*, where 1.0 = parity and 0.70 = "AI retains 70% of human diversity." Gate-keeping is a *paired* design — each proposal's AI panel vs its own human panel — so effects are **Cliff's δ**, a consistency measure: δ = −1 means the AI panel came out lower for *every single one* of the 23 proposals; δ = 0 means no systematic direction. The two cannot be placed on one axis honestly, but both are oriented so that **negative/below-1 = AI less diverse**.

---

## Map of all analyses (so nothing is lost track of)

This report contains **every analysis run by notebooks `02_facets_proposals` and `03_facets_reviews`** (`04_synthesis` adds no statistics — it is a display layer that reads the tidy tables `02`/`03` write and emits the synthesis figures and `double_compression_summary.csv`). The table is the index; each linked section carries the full "what it is / what question / why it fits / what it means" write-up in plain language. Analyses are computed on both text branches (rephrased = style-normalized, primary; original = raw prose, robustness), all three elicitation conditions, and — on the review side — all three fields (whole / strengths / weakness, rephrased only), unless noted.

**Shared setup for every analysis below:** all text is embedded with **BioLinkBERT-large** (a biomedical language model; each proposal/review becomes one 1024-number "meaning fingerprint"), distances are **cosine** (1 = identical meaning), and every comparison is made at **matched sample size** (23 vs 23 for proposals; equal-sized panels for reviews). Three models generate/review: **Claude, Gemini, GPT**; humans are 23 proposals (2 cohorts) and their 2–5 expert reviews each.

### Generation side — do AI models propose as varied a set of ideas as humans? (notebook 02)

| # | Analysis | The plain question it answers | Section |
|---|---|---|---|
| 1 | **Spread** | Are AI ideas closer together than human ideas, on average? | §2.1 |
| 2 | **Richness** (Vendi) | How many *effectively different* ideas are there, once near-repeats are discounted? | §2.2 |
| 3 | **Evenness** | Does AI pile up near-duplicate ideas rather than spacing them out? | §2.3 |
| 4 | **Dimensionality** | Do AI ideas vary along fewer independent "themes/axes"? | §2.4 |
| 5 | **Coverage, geometric** | How much of the *territory* of human ideas does AI actually reach? | §2.5 |
| 6 | **Coverage, domain** | Does AI engage the same *areas of the biomedical literature* (topics, MeSH terms)? | §2.6 |
| 7 | **Displacement** (MMD² + optimal transport) | Is AI somewhere *else*, or a smaller region *inside* the human one? | §2.7 |
| 8 | **Wording control** (distinct-n, self-BLEU) | Does raw *wording* narrow too — so the effect can't be blamed on the embedding model? | §2.8 |
| 9 | **Convergent-validity checks** (multiple estimators + convergence heatmap; kernel & neighborhood-size sensitivity; text-branch contrast) | Do we get the same story when we measure each facet a different way, tune the knobs, or use raw vs normalized text? | §2.9 |
| 10 | **Condition gradient** | Does idea diversity *recover* as we push harder for it (baseline → one-at-a-time → persona)? | §2.9, §4.4 |
| 11 | **Model-ordering trend test** (Jonckheere–Terpstra) | Is there a reliable ranking *among* the three models (Claude < Gemini < GPT)? | §2.9 |
| 25 | **Core vs edge** (peripherality → miss-rate) *(new, 2026-08-30)* | Are the human ideas AI fails to reproduce specifically the distinctive, sparsely-populated ones? | §2.10 |

### Gate-keeping side — do AI review panels judge a proposal as diversely as human panels? (notebook 03)

| # | Analysis | The plain question it answers | Section |
|---|---|---|---|
| 12 | **Spread & richness within panels** | For one proposal, do the AI reviewers say more similar things than the human reviewers? | §3.1 |
| 13 | **Evenness within panels** | Do AI reviewers produce near-interchangeable reviews (clumps)? | §3.2 |
| 14 | **Dimensionality within panels** | Do AI reviewers vary along as many axes of critique as humans? | §3.3 |
| 15 | **Coverage — the "central blanket"** | Does each AI review sit near everything the human reviewers wrote? | §3.4 |
| 16 | **Displacement of the review cloud** (MMD² + OT) | Do AI reviews carry a systematic "accent" that sets them apart? | §3.5 |
| 17 | **Gemini-at-baseline flag** | Is the one odd cell a real effect or a data glitch? | §3.6 |
| 18 | **Field split: strengths vs weaknesses** | Is the compression in the *praise* or in the *criticism* half of the review? | §3.7 |
| 19 | **Interleaving** (SI) | Does either side hold *exclusive territory* the other never reaches? | SI-1 |
| 20 | **Score-level decision analysis** (SI) | Does the lost disagreement show up in the *numeric scores* a committee uses, and would rankings differ? | SI-3 |
| 21 | **Claim-level uniqueness** (SI) | At the level of *specific points*, does each panel raise things the other misses? | SI-4 |
| 22 | **Simpson diversity index** (both stages) | The classic Simpson index, reported explicitly two ways (embedding + categorical) — does it agree with the richness result? | SI-5 |
| 23 | **Decision-outcome** (SI) | Using the *actual funding decisions* — can an AI panel reproduce which proposals got funded? | SI-6 |
| 24 | **Matched decision-outcome** (SI) | Does that answer survive putting the AI panel at the human panel's size and proposal set? | SI-6, Table SI-6b |

*A cross-cutting robustness pass, the **original (raw-text) branch**, repeats analyses 1–17 on unedited prose and is reported in SI-2 (the field split of analysis 18, and SI-3/SI-4/SI-6, exist on the `rephrased` branch only — `strengths`/`weakness` sections and claim text are not carried on raw prose, and the score/decision data are branch-invariant). The wording-vs-idea contrast (analyses 8 + 2) has its own figure, `si_wording_vs_idea_gap.png`; the Simpson index (analysis 22) is the order-2 relative of the richness facet, reported for readers who expect it.*

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

† Evenness is an area statistic (excess close-neighbor mass relative to a same-size chance draw of all proposals), not a ratio. In every condition, humans are *more evenly spread than chance* (excess −0.115 at persona, −0.141 at baseline, −0.234 at one_at_a_time) while pooled AI shows *excess clumping* (+0.062 / +0.077 / +0.142); cells summarize direction and significance. Evenness is a pre-registered primary, so its stars are `p_raw`. ‡ Coverage is judged against how well one random half of the human set covers the other half (the honest "same-distribution" benchmark), not against 100%.

### Table 1b — Gate-keeping (reviews): Cliff's δ, AI panel vs the human panel of the same proposal

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
| Model ordering (Claude < Gemini < GPT < Human trend test) | generation: JT significant in 18 of 36 cells, but the predicted monotone chain (`direction_ok`) holds in only **3 of 36** | | gate-keeping: **0 of 15** cells significant (all p_fdr = .98) | The significant JT statistics are driven by the human–AI gap, not by an ordering among models; humans exceed every model and no reliable ranking *among* models survives |

---

## 2. Generation: how AI narrows the production of ideas

All generation analyses operate on the full text of each proposal, represented in a high-dimensional semantic embedding space; "distance" below means dissimilarity of scientific content, with prose style already normalized away (the `rephrased` branch rewrites all proposals into one house style before embedding, so wording habits cannot masquerade as ideas).

### 2.1 Spread — AI proposals sit closer together

*What was tested.* The average distance between all pairs of proposals within a group, compared between humans and each AI group by a permutation test (shuffle the group labels 10,000 times and ask how often chance alone produces a gap this large).

*Why it fits.* Spread is the most basic meaning of "variety" — how far ideas sit from one another — and the permutation test makes no assumption about the shape of the data, so it is trustworthy on samples as small as 23. (As a convergent check, spread is also measured five other ways — nearest-neighbor isolation, minimum-spanning-tree dispersion, and others; §2.9 confirms they agree.)

*Result.* Human proposals average 0.416 apart; pooled AI proposals average 0.268–0.293 — AI retains **64–70% of human spread**, significant in every condition (baseline p = .010; one_at_a_time p < .001; persona p = .003). Individual models at n = 23 mostly do not reach significance on their own (the study is powered for the pooled contrast); Gemini is the significant exception under one_at_a_time and persona (ratios 0.45–0.50).

*Implication.* The most direct sense of narrowing — ideas closer together — is present in every condition. But spread alone cannot say *why*: two tight clusters far apart also average a large spread. The next two facets say why.

### 2.2 Richness — fewer effectively distinct proposals

*What was tested.* The Vendi score VS₁ converts a set's mutual similarities into an "effective number of fully distinct items." The unit is intuitive: the 23 human proposals behave like **3.15 completely independent ideas**, while pooled AI sets behave like **2.09–2.37** (absolute Vendi values are conservative on dense semantic embeddings; the *ratio* is the meaningful quantity).

*Why it fits.* Counting raw proposals is meaningless (every group has 23); the Vendi score is the standard way to turn "how similar is everything to everything else" into an honest count of *genuinely* distinct items — the same idea ecologists use to say a stand of 23 trees from overlapping species behaves like 3 effective species.

*Result.* AI retains **66–75% of human effective richness**, significant in all conditions (pooled p = .005 / <.001 / .004). This is a pre-registered primary result. Gemini is again the weakest single model (0.56 at one_at_a_time).

*Implication.* Narrowing is not merely "closer together" — it is genuinely *fewer distinct ideas*. If a funder replaced its human idea pool with an equal-sized AI pool, roughly a quarter to a third of the effective intellectual variety would disappear, under every elicitation strategy tested. (The **Simpson diversity index** — the order-2 member of this same Vendi/Hill-number family — is reported explicitly in **SI-5** and reproduces this result, as a cross-check for readers who expect the classic index.)

### 2.3 Evenness — AI re-proposes near-duplicates; humans do not

*What was tested.* For each group, we count how many close neighbors each proposal has within growing distance thresholds, and compare that against what a random same-size draw of *all* proposals (human and AI together) would produce. Positive excess = more tight clustering than chance ("near-duplicate clumps"); negative = more evenly spaced than chance.

*Why it fits.* Two very different patterns — a few tight clumps, or a smooth even sprinkle — can produce the *same* average spread, so we need a measure aimed specifically at near-duplicate crowding, judged against what a pure chance draw would produce rather than an arbitrary threshold.

*Result.* The starkest qualitative contrast in the study. **Humans are more evenly spread than chance in all three conditions** (excess −0.115 persona, −0.141 baseline, −0.234 one_at_a_time), while **pooled AI shows excess clumping in all three** (+0.062 / +0.077 / +0.142; p = .001 throughout, simultaneous-envelope test). In nearest-neighbor terms: at a distance where only ~35% of human proposals have a close "twin," over 80% of Claude's baseline proposals already do.

*Implication.* AI's narrowing takes a specific and recognizable form — it returns to the same wells. This is exactly the failure mode that averaged distance metrics can hide, and it is why the multi-facet design exists.

### 2.4 Dimensionality — narrowing is *not* a collapse onto fewer axes

> **Excluded from the manuscript (null).** Kept here for the completeness of the audit record, but dropped from the paper: dimensionality is non-significant at both stages, so it earns no main-text or SI space in the manuscript.

*What was tested.* The participation ratio: an effective count of independent directions ("themes/axes") along which a group's proposals vary.

*Why it fits.* Narrowing could mean two very different things — fewer positions along the same axes, or a collapse onto fewer axes entirely; the participation ratio isolates the second by estimating how many independent directions actually carry the variation, so §2.2–2.3 and §2.4 together pin down the mechanism.

*Result.* Essentially null. Ratios are 0.85–1.06 across conditions; only one_at_a_time shows a modest, significant reduction (0.85, p = .02), and under persona AI is numerically *above* parity (1.06, ns).

*Implication.* This is an informative negative. AI proposals vary along roughly as many independent directions as human proposals — they are not "flattened." Combined with §2.2–2.3, the mechanism is precise: **similar number of axes, fewer distinct positions along them, with repeated returns to the same positions.**

### 2.5 Coverage (geometric) — AI reaches most, not all, of the human territory

*What was tested.* For each human proposal, does any AI proposal fall within its local neighborhood? The benchmark is not 100%: even a second, equally human set would miss some — so AI is judged against how well one random half of the human set covers the other half.

*Why it fits.* Being spread out is not the same as covering the *same ground* — AI could be varied yet clustered off to one side; coverage asks the reach question directly, and using "one human half covering the other" as the yardstick keeps the bar honest instead of demanding an impossible 100%.

*Result.* Pooled AI reaches **81–86% of the human idea-space**, below the human self-benchmark at baseline (p = .038) and persona (p < .001), marginal at one_at_a_time (p = .08). The model split is the striking part: **Claude covers the human space fully (ratio 1.00 at baseline and one_at_a_time), while Gemini reaches only 61%.** A stability check across neighborhood sizes (k = 2, 3, 5) preserves this ordering.

*Implication.* There is a periphery of human proposals — roughly one in six — that the AI pool never approaches, and *which* AI you use matters more here than for any other facet.

### 2.6 Coverage (domain) — the narrowing is inside topics, not across them

*What was tested.* Each proposal was mapped to its ten nearest abstracts among ~39,500 PubMed papers; a group's domain coverage is how many of the 12 literature regions, and how many unique MeSH subject terms, it collectively touches — always compared at equal group size, with accumulation curves to make the counts honest. (MeSH = the National Library of Medicine's standardized biomedical subject headings.)

*Why it fits.* The geometric result could have a mundane explanation — maybe AI simply avoids whole areas of biology; anchoring every proposal to its nearest real PubMed papers checks that directly, in units (topic regions, subject headings) a biomedical reader recognizes.

*Result.* Essentially null, and the direction is mixed. All groups touch 5–8 of 12 regions; the only significant cell after correction is pooled AI at one_at_a_time (5.9 vs 7 regions, p_fdr = .008). AI proposals nominally touch *more* unique MeSH terms than humans (e.g., 571–598 vs 504, ns). The region-occupancy maps show only rare exclusive territories (e.g., a clinical-risk/patient-studies region touched only by humans at baseline).

*Implication.* AI is not avoiding areas of biomedical science. Read jointly with §2.5, the claim sharpens into the more interesting one: **AI engages the same topics but explores less variety *within* them.** For a biomedical audience: same subject headings, fewer genuinely different ideas per heading.

### 2.7 Displacement check — a smaller region *inside* the human one

*What was tested.* Whether the AI proposal cloud sits somewhere *else* than the human cloud (kernel two-sample distance MMD² — "how distinguishable are the two clouds?" — against a shuffle-based null), which would change the story from "narrower" to "different." A second, mathematically independent distance, **optimal transport** (Wasserstein — "how much work to slide one cloud onto the other?"), is computed the same way as a cross-check, so the conclusion never rests on a single estimator.

*Why it fits.* "Less coverage" has two opposite meanings — a smaller region *inside* the human cloud, or a shove into *different* territory — and only a whole-cloud distance test can tell them apart; running two different distances guards against either one having a quirk.

*Result.* Pooled displacement is small and non-significant in every condition (MMD² 0.032–0.062, all ns; the human split-half floor is ≈ 0), and **optimal transport agrees** (same near-zero, non-significant pattern). Per model: GPT is essentially undisplaced (persona MMD² = 0.000); Gemini is the only repeat offender (significant at one_at_a_time and persona).

*Implication.* Low coverage plus low displacement is the specific geometric signature of the central claim: **AI is concentric with and interleaved among the human cloud (same center, same radial extent), but fills it less evenly and thins at the edges** — more clumped (spread 0.70×) and covering the periphery sparsely, so the humans it fails to reach are the peripheral ones. The exported statistic for that periphery is the **human-only fringe** (SI-1): 18–26% of human proposals have no AI proposal within normal human spacing, against a ~10% by-construction reference. The main-text **Fig. 3*B*** foregrounds this fringe per condition — 23% / 18% / 26% under baseline / one_at_a_time / persona on the **mean-probability rule** (average over subsamples of "nearest AI beyond the human q90 yardstick"), widest under persona and consistent with SI-1's 22% / 18% / 26% — and its core-vs-edge panel (§2.10) shows the missed proposals are specifically the distinctive, peripheral ones. (An earlier majority-of-subsamples rule reported 26% / 17% / 22%, which flipped which condition looked widest; the mean-probability rule is used throughout now. The retired per-proposal dumbbell, `fig_generation_geometry.png`, is kept only as an SI alternate.) This is *not* strict containment (AI is not a smaller region inside, and small AI-only pockets exist); it is a concentric, more-clumped cloud with an asymmetric human periphery. Gemini is the partial exception: narrowest *and* somewhat shifted. *(The two visible clusters in a UMAP are a real topical split, not the two cohorts — cohorts distribute across both clusters and AI populates both; the UMAP separation is a projection artifact, Chari & Pachter 2023.)*

### 2.8 Wording control — does the narrowing show up in raw wording too?

*What was tested.* Two text-only measures that never touch the embedding: **distinct-n** (the share of word pairs that are unique — higher = more varied wording) and **self-BLEU** (how much a group reuses its own phrasing — higher = more repetitive). Human vs each AI group, per condition, on both text branches.

*Why it fits.* Every facet above is computed inside the BioLinkBERT embedding, so a skeptic could object that the "narrowing" is a quirk of that one model. Wording is measured in plain words instead; if wording narrows the *same way* the embedding does, the encoder cannot be the cause.

*Result.* Human proposals are more varied in raw wording too (distinct-2gram ratios 1.04–1.24, significant almost everywhere) and AI reuses its own phrasing more (self-BLEU 0.21–0.35 vs human 0.19), in every condition — so the semantic narrowing is real, not an encoder artifact. One twist stands out: on the primary (style-normalized) branch, **persona nearly closes the *wording* gap (ratios fall to ~1.04–1.07, Claude at parity) while the idea-level gaps of §2.1–2.3 do not budge** — personas change *how* models write far more than *what* they propose.

*How to read it.* This is a **control, not a diversity facet** (self-BLEU is descriptive, with no significance test), so it sits beside the facets, not among them. The wording-vs-idea contrast has a dedicated figure, `results/figures/synthesis/{rephrased,original}/si_wording_vs_idea_gap.png`: one "AI ÷ human" axis on which the wording line rises to ~0.95 under persona while richness and spread stay at 0.68–0.75. *Caveat:* because the primary branch rewrites all text into one neutral house style, this is a *residual*-wording result; on raw text (SI-2) persona wording only returns to its baseline level, so the "closes to parity" reading is specific to the normalized branch.

### 2.9 Robustness and convergent-validity checks

*Why these exist.* A single number can mislead for boring reasons — the particular estimator chosen, a tuning knob, or raw-versus-edited prose. Each check below re-asks the same question a different way; the findings the synthesis (§4) leans on are the ones that survive all of them.

- **Convergent validity — many estimators per facet.** Each facet is deliberately measured *several ways*: spread six ways (mean pairwise distance, nearest-neighbor isolation, minimum-spanning-tree dispersion, sparseness, spherical variance, centroid distance), dimensionality two ways (participation ratio and effective rank), evenness two ways (Ripley clumping and a Vendi-slope), coverage two ways (geometric support overlap and a density companion), displacement two ways (MMD² and optimal transport). A **convergence heatmap** (`.../proposals/{branch}/_convergence/facet_convergence_heatmap.png`) shows the estimators within each facet move together. *How to read it:* agreement across estimators means the facet is a stable property, not an artifact of one formula — so reporting one headline metric per facet is safe.
- **Style sensitivity (text branch).** On the unrephrased `original` text, the pooled baseline spread/richness contrasts disappear (ratios 1.02/0.96, ns) — but not because the models agree with humans: Claude and GPT are significantly *narrower* on raw text (0.58–0.87, \*\*\*) while Gemini's raw prose is *wider* than human (spread ratio 1.52), and the opposing style effects cancel in the pool. One_at_a_time and persona replicate on both branches, and geometric coverage narrows on *both* branches (baseline original 0.60, p < .001). The pre-registered primary branch is `rephrased`; the full original-branch results, and what the rephrased-vs-original contrast reveals about style versus ideas, are reported in **SI-2**.
- **Kernel and neighborhood-size sensitivity.** The richness result's direction holds under an alternative (RBF) similarity kernel across three bandwidths: **all 27 per-model cells (3 models × 3 bandwidths × 3 conditions) sit below parity**, ratios 0.36–0.91. Significance is the underpowered part, as expected for per-model tests: 6 of 27 cells survive FDR (4 of 9 at σ = 0.5× median, 1 of 9 at each wider bandwidth), 14 of 27 on uncorrected p. Geometric coverage holds across neighborhood sizes k = 2, 3, 5 (per-model ratios 0.58–1.01 at k=2, 0.61–1.00 at k=3, 0.74–1.00 at k=5, with Gemini lowest at every k). *How to read it:* the **direction** is invariant to tuning; only the per-model star count moves.
- **Condition gradient — does diversity recover as we push for it?** The same facets are tracked across the three conditions (baseline → one_at_a_time → persona; figure `fig6_condition_gradient.png`, pooled AI subsampled to 23) to see whether stronger diversity pressure closes the gap. *Result:* it does not — no facet reaches human parity in any condition, and persona (the strongest push) leaves the idea-level gaps essentially where baseline had them (§4.4).
- **Ordering across models (Jonckheere–Terpstra trend test).** A formal trend test for the pre-specified ranking Claude < Gemini < GPT < Human, run over jackknife replicates at matched n and exported with a `direction_ok` flag that records whether the point estimates actually rise monotonically. *Result:* on the generation side 18 of 36 gradient cells reach p_fdr < .05, but `direction_ok` is true in only **3 of 36** — the significant statistics are carried by the human–AI gap, not by an ordering among models (Gemini, not Claude, is typically the narrowest). On the gate-keeping side **0 of 15 cells** are significant (every p_fdr = .98). *How to read it:* we report "humans above every model" and decline any model-ranking claim.

---

### 2.10 Core vs edge — which human ideas does AI fail to reproduce? *(new, 2026-08-30)*

*Why this exists.* §2.5 and SI-1 establish that an equal-sized AI pool misses roughly 1 in 5 human proposals. This asks the sharper question: are the missed proposals a random fifth, or specifically the distinctive, sparsely-populated ones? If the latter, the coverage gap becomes a *directional* claim about what kind of ideas AI underproduces.

*What was tested.* For each of the 23 human proposals we measured its **peripherality** in human idea space, using human-to-human distances only, three ways: distance from the human centroid, isolation (mean distance to its 3 nearest human neighbors), and local density (number of human neighbors within the human q90 yardstick). Separately, its **miss-rate**: the fraction of equal-sized (n=23) AI pools, across conditions and subsamples, whose nearest proposal to that human idea exceeds the yardstick (its per-item fringe probability). Peripherality is computed from human geometry alone and miss-rate from human–AI distances, so the two share no inputs and the relationship is not circular.

*Result.* Peripherality predicts being missed almost deterministically. On the rephrased branch, Spearman ρ between miss-rate and centroid distance is **+0.86**, isolation **+0.88**, local density **−0.99** (all p < 1e-6, n = 23). Binned into density tertiles, AI misses **0% of core (dense) human ideas, 4% of the middle, and 69% of the edge (sparse) ideas**. The effect replicates on the original-text branch (ρ_centroid +0.89, ρ_density −0.89; tertiles 0% / 13% / 58%), so it is not a standardization artifact.

*How to read it.* The human proposals AI fails to reproduce are not a random fifth; they are specifically the most distinctive, sparsely-populated ones. This upgrades the coverage result from "AI covers less space" to the directional claim: **AI preferentially reproduces the dense semantic core of human scientific ideas and underrepresents their sparse edges.** *Caveats:* n = 23, and the human set is one dense core plus a modest number of distinctive outliers, so "the edge" is a small population of distinctive proposals, not a smooth rim.

*Quality guard — are the missed ideas just the ones humans rejected?* No. Splitting the 23 proposals by the program's own outcomes, the ideas AI misses are statistically indistinguishable from those it reproduces on funding (funded 14 vs rejected 9: mean miss-rate 0.20 vs 0.26, Mann–Whitney p = .77) and on top-5 ranking (p = .94), and miss-rate is uncorrelated with funding (Spearman −0.07, p = .76). The lone directional wiggle — the sparsest tertile funded at 71% vs 50% for the core on the rephrased branch — does not replicate (the original branch runs the other way, 75% / 50% / 57%), so it is noise. *What it means:* the coverage gap is not explained away by the missed ideas being lower quality; the distinctive ideas AI fails to reproduce span the full range of funding outcomes. *Caveat:* n = 23 with 7–8 per tertile, so this bounds rather than proves independence. Funding/ranking fields (`is_funded_human`, `is_top5_ranked_human`, `ranking`) are carried in the exported table for anyone who wants to re-test.

*Sources.* `src/core_edge_analysis.py` (Panel B, `build_panel_b`) and `src/figure3_regions.py` (Panel A, `build_panel_a`), both wired into `notebooks/04_synthesis.ipynb` and regenerated per branch; table `results/tables/synthesis/core_edge_{branch}.csv` (per-human peripherality, miss-rate, funding/ranking); figures `results/figures/synthesis/{branch}/fig3_core_edge.png` (core vs edge) and `fig3_regions.png` (effective regions).

---

## 3. Gate-keeping: how AI narrows the judgment of ideas

The gate-keeping analyses respect the nested structure of review: reviews of *different* proposals differ for reasons that have nothing to do with reviewer independence. So every metric is computed *within* a proposal — the 2–5 human reviews of proposal X versus same-sized panels drawn from the AI reviews of proposal X — and then the 23 within-proposal comparisons are combined with a paired test. The human panel is thus the built-in reference: effects are read as "AI panels relative to the human panels of the very same proposals."

*The five facets are the same measures as §2* (spread, richness, evenness, dimensionality, coverage, plus a displacement check), so each facet's "what it is / why it fits" rationale carries over; what changes here is only the **design** — paired within-proposal instead of group-vs-group, and therefore reported as Cliff's δ (consistency of direction) rather than a ratio.

Two reference conventions matter and are stated on every figure: the human self-benchmark for panel *coverage* is leave-one-out self-coverage (how well each human review is covered by the rest of its own panel; 0.83 on average — not 1.0), and panel *clumping* is judged against random same-sized draws from that condition's full review pool.

### 3.1 Spread and richness — AI reviewers agree with each other more

*Result.* AI panels are tighter and less rich than the matched human panels, with near-ceiling consistency under structured elicitation: at one_at_a_time, pooled δ = −0.91 (spread) and −0.83 (richness), with several model-level cells at δ = −1.00 — lower for *every one* of the 23 proposals (p ≈ 10⁻⁶–10⁻⁷). Persona is similar (pooled δ = −0.74). At baseline, Claude and GPT show the same strong pattern (δ = −0.74 to −0.91, \*\*\*), while **Gemini sits exactly at parity (δ = +0.04, ns)**, which dilutes the pooled baseline contrast to marginal (δ ≈ −0.3 to −0.4, p = .07–.09).

*Magnitude vs consistency — an essential distinction.* In absolute units the effect is small: human panels average 0.0438 mutual distance, pooled AI panels 0.032–0.040 and individual models 0.028–0.044 (a 0–36% tightening, the 0 being Gemini at baseline; effective richness 1.12–1.19 vs the human 1.18 — review panels are highly homogeneous for everyone). What is remarkable is the *consistency*: the tightening recurs proposal after proposal, which is exactly what a funding process should care about, because systematic small biases — unlike noisy large ones — do not average out across a portfolio. The same collapse appears in the numeric scores committees actually consume — and, at this sample size, without demonstrable divergence in the resulting rankings — see **SI-3**.

### 3.2 Evenness — AI reviews clump; mirror image of generation

*Result.* Relative to same-sized random panels, AI review panels carry excess near-duplicate mass in every condition and for every model except Gemini at baseline (pooled δ = +0.91 at one_at_a_time, +0.74 at persona, all \*\*\*). AI reviewers do not merely agree in score — they say near-interchangeable things.

### 3.3 Dimensionality — cleanly null

> **Excluded from the manuscript (null).** Kept here for the audit record only; dropped from the paper (non-significant, 12/12 cells ns).

*Result.* Twelve of twelve cells ns, |δ| ≤ 0.18. AI panels vary along as many independent axes of critique as human panels; they simply occupy less of each axis. The generation-side negative (§2.4) is exactly reproduced on the gate-keeping side — a satisfying internal consistency check.

### 3.4 Coverage — the "central blanket" pattern

*Result.* This facet runs the *other* way, and the combination is the most diagnostic finding on the gate-keeping side. Pooled AI panels cover **96–97%** of the human review span (per model 89–98%), *exceeding* the human self-benchmark of 83% (pooled δ = +0.37 to +0.44, \*\* in all conditions; Claude δ = +1.00 everywhere; Gemini is the only cell that fails to clear it, ns at baseline and persona).

*Implication.* Read §3.1–3.2 and §3.4 together: AI reviews are *individually near everything the humans said* (high coverage) while being *collectively interchangeable* (low spread, high clumping). AI review panels behave like several copies of one thorough, centrally positioned reviewer — a blanket over the human review span — whereas human panels behave like distinct voices that each miss things but disagree informatively. For a decision process, coverage of this kind is not a substitute for independent perspectives: the variance that a deciding committee learns from is precisely what is missing. **Note the resolution limit:** this coverage is measured between whole reviews. At claim resolution (**SI-4**), matched-size panels miss roughly half of each other's specific points — so "near everything the humans said" describes *position*, not *content*.

### 3.5 Displacement and ordering checks

The pooled AI review cloud is significantly displaced from the human cloud in every condition (whole-cloud, exploratory: MMD² = 0.0073 → 0.0116 → 0.0155 from baseline to persona, all p ≤ 2×10⁻⁴; the second distance, optimal transport, shows the same growing pattern) — AI reviews have a systematic stylistic/positional signature that *grows* under structured elicitation even as panel diversity shrinks. (The branch comparison in SI-2 shows this signature is overwhelmingly stylistic: on raw text the displacement is ~20× larger and rephrasing removes almost all of it.) Trend tests across models are uniformly non-significant on the gate-keeping side: no model ordering, again.

### 3.6 One flagged cell

Gemini-at-baseline is the only AI cell at parity across spread/richness/evenness, followed by δ = −1.00 under one_at_a_time — a within-model jump no other model shows. Data-level checks (duplicate texts, review lengths, panel counts) found no anomaly, and the same pattern appears on the `original` text branch, so it appears to be a real elicitation effect; we nonetheless recommend a qualitative read of Gemini's baseline reviews before this cell is quoted.

### 3.7 Strengths versus weaknesses — where in the review the compression lives

*What was tested.* Notebook `03` runs the entire facet battery three times, over a **field** axis: the whole review, the `strengths` section alone, and the `weakness` section alone (`CONFIG["fields"] = ["whole", "strengths", "weakness"]`, consuming the separate section-level embedding bundles written by the prep layer). Design, pairing, and inference are identical to §3.1–3.4 — only the text each review contributes changes. The section fields exist on the `rephrased` branch only (`fields_available` in the review prep manifest lists `whole` alone for `original`), so this is a rephrased-branch analysis with no raw-text counterpart.

*Why it fits.* A review does two different jobs, and a funder cares about them differently. "AI panels are less diverse" is a much stronger claim if the compression is in the **criticism** — the half that decides outcomes — than if it is only in the praise. Whole-review embeddings average the two together and cannot tell them apart.

### Table 3.7 — Pooled AI vs the human panel of the same proposal, by field (Cliff's δ, rephrased)

Same convention as Table 1b: δ < 0 = AI panels less diverse (evenness and coverage flip sign as noted).

| Facet | Condition | whole | strengths | weakness |
|---|---|---|---|---|
| **Spread** | baseline | −0.39 ns (p=.07) | +0.04 ns | −0.04 ns |
| | one_at_a_time | −0.91 \*\*\* | −0.65 \*\*\* | −0.91 \*\*\* |
| | persona | −0.74 \*\*\* | −0.57 \*\* | −0.91 \*\*\* |
| **Richness** | baseline | −0.30 ns (p=.09) | +0.13 ns | −0.04 ns |
| | one_at_a_time | −0.83 \*\*\* | −0.65 \*\*\* | −0.91 \*\*\* |
| | persona | −0.74 \*\*\* | −0.57 \*\* | −0.91 \*\*\* |
| **Evenness** (δ > 0 = AI clumpier) | baseline | +0.22 ns | +0.04 ns | **+0.48 \*** |
| | one_at_a_time | +0.91 \*\*\* | +0.65 \*\*\* | +0.91 \*\*\* |
| | persona | +0.74 \*\*\* | +0.57 \*\* | +0.91 \*\*\* |
| **Coverage** (δ > 0 = AI reaches more) | baseline | +0.37 \*\* | +0.10 ns (p=.07) | +0.27 \* |
| | one_at_a_time | +0.44 \*\* | +0.26 \* | +0.27 \*\* |
| | persona | +0.37 \*\* | +0.16 ns (p=.07) | +0.27 \* |
| **Dimensionality** | baseline | −0.00 ns | −0.18 ns | −0.36 ns |
| | one_at_a_time | −0.00 ns | −0.00 ns | −0.18 ns |
| | persona | −0.00 ns | −0.18 ns | −0.09 ns |

*Human absolute values (mean pairwise distance within panel): whole 0.044, strengths 0.069, weakness 0.084 — human reviewers of the same proposal disagree most about its weaknesses, and section-level text is roughly twice as internally varied as the whole-document average. Source: `results/tables/{condition}/reviews/rephrased/facet_diversity_tests.csv`, `field` column.*

### Findings

**1. The compression is concentrated in the criticism.** Under both structured conditions, weakness panels compress at the design ceiling (δ = −0.91 for spread and richness, +0.91 for clumping — i.e. the AI panel is narrower for 22 of 23 proposals) while strengths compress substantially less (δ = −0.57 to −0.65). The weakness half is also where human panels have the most diversity to lose (human within-panel spread 0.084 vs 0.069 for strengths), so the loss is larger in both effect size and absolute units. **The section that carries the decision is the section AI homogenizes hardest.**

**2. Baseline is null in both fields at the pooled level — but not per model.** Pooled baseline δ is ns for both sections, mirroring the whole-review dilution of §3.1. The per-model cells show the same Gemini-driven cancellation: at baseline GPT compresses both fields (strengths δ = −0.65 \*\*\*, weaknesses −0.83 \*\*\*) and Claude compresses weaknesses (−0.74 \*\*\*) while leaving strengths at parity (−0.04 ns), and Gemini is at or above parity in both. The Gemini-at-baseline anomaly (§3.6) therefore replicates a fourth time — whole reviews, both text branches, numeric scores, and now both review sections.

**3. Human weakness panels are *more even than chance*; AI weakness panels are not.** The human evenness reference for weaknesses is at or below zero under both structured conditions (excess −0.006 and −0.003) while pooled AI runs +0.026 — the same "humans spread, AI returns to the same wells" signature found on the generation side (§2.3), now inside a single proposal's criticism. Weaknesses are the only field where the clumping contrast is already significant at baseline (δ = +0.48 \*).

**4. The "central blanket" is mostly a whole-document effect.** Coverage still runs the other way — AI panels exceed the human self-benchmark — but at half the strength of the whole-review result, and only the weakness field clears significance in every condition (δ = +0.27, \*/\*\*/\*). Strengths coverage is ns at baseline and persona. Read with SI-4: AI's apparent completeness shrinks steadily as the unit of analysis shrinks — whole review (δ +0.37 to +0.44) → section (+0.10 to +0.27) → individual claim (~half of each side's points unmatched).

**5. Dimensionality is null in every field** — 12 of 12 cells ns in each of the three fields (36 cells, smallest p = .06, |δ| ≤ 0.36), reproducing §2.4 and §3.3 a third time.

*Caveat.* Section-level panels are the same 23 paired comparisons as §3.1–3.4, so the fields are not independent tests of one another; the field split is a decomposition, not a replication. The six pre-registered primaries stay primary in every field (stars above are `p_raw` for spread, richness, evenness, dimensionality and coverage); FDR for the secondary metrics is applied separately within each `field` stratum.

---

## 4. Synthesis: the coherent story

**1. AI narrows the generation of scientific ideas — substantially, in a specific way, in every condition tested.** Pooled across models, AI proposal sets retain roughly two-thirds to three-quarters of human diversity on the facets that count distinct ideas (spread 0.64–0.70, richness 0.66–0.75, all significant), and the loss has a signature: excess near-duplication (humans are more evenly spread than chance; AI is clumpier than chance, every condition) inside a space of undiminished dimensionality and undiminished topical breadth. AI proposals engage the same regions of the biomedical literature, touch as many subject headings, and vary along as many axes — **the narrowing is intra-topic: fewer genuinely different ideas per area of science, with repeated returns to the same ones.** The displacement check certifies the geometry: AI occupies a smaller region *inside* the human territory (low coverage, no displacement), not a different region beside it. And the lexical control shows the same compression in raw wording, ruling out the embedding model as the source.

**2. AI also narrows the gate-keeping of ideas — mildly in magnitude, but with near-deterministic consistency, and most strongly under exactly the elicitation styles that improve generation hygiene.** Given the same proposal, AI review panels are tighter, less rich, and more mutually duplicative than the human panel — for essentially every proposal under one_at_a_time and persona (δ ≈ −0.7 to −1.0), and for two of three models at baseline. Yet AI panels *cover* the human review span better than human reviewers cover each other. The picture is a central blanket: each AI review is competent and touches everything; the panel as a whole contains one voice. Independence of judgment, not quality of judgment, is what gate-keeping loses — with two refinements. From **§3.7**: splitting each review into its praise and its criticism shows the compression is concentrated in the **criticism** (weakness panels compress at the design ceiling, δ = −0.91, where strengths reach only −0.57 to −0.65), i.e. in the half of the review that decides outcomes and where human panels disagree most to begin with. From **SI-4**: at *claim* resolution, matched-size human and AI panels each make ~40–58% points the other does not, so an AI panel also loses about half the specific content a human panel would have raised, even while sitting near it in review space. The two refinements point the same way — AI's apparent completeness is an artifact of the coarse unit, and it erodes as the unit gets finer (whole review → section → claim).

**3. "Double compression" is real but asymmetric — and honesty about the asymmetry strengthens the paper.** The two stages compress differently: generation loses 25–36% of effective diversity (large magnitude), gate-keeping loses only a few percent in ratio terms but does so for nearly every proposal (large consistency). Compression does not *compound* in the naive multiplicative sense — the slopegraphs rise toward parity from generation to gate-keeping — but the two losses are complementary in kind: generation narrows *what enters the pool*; gate-keeping standardizes *how the pool is judged*. A pipeline with both stages automated would draw from a poorer menu and evaluate it with a single palate.

**4. Elicitation strategy redistributes the problem; it does not solve it.** The persona manipulation — the strongest candidate rescue — leaves idea-level generation narrowing intact (pooled richness 0.75, p = .004, indistinguishable from baseline) while nearly closing the *wording* gap: personas make models sound more varied without making them think more variedly. On the gate-keeping side the structured conditions actively *strengthen* review compression (baseline δ ≈ −0.3 pooled → −0.9 at one_at_a_time) and increase the displacement of AI reviews from human ones. There is no condition in which either stage reaches human diversity.

**5. Which AI matters — but not in the predicted order.** The pre-specified capability ordering (Claude < Gemini < GPT < Human) fails on both stages; the defensible statement is "humans above every model." The texture that survives: **Claude** covers the human idea-space fully but with clumped, repetitive proposals; **Gemini** is the narrowest and the only displaced model on the generation side, yet the least compressed reviewer at baseline; **GPT** is unremarkably in between and geometrically the most human-like in position. Model choice shifts *which* facet of diversity you lose, not *whether* you lose one.

**Limitations to state.** Samples are small (23 per group; per-model generation contrasts are underpowered and the pooled contrasts carry the inference). The pooled baseline generation effect on spread/richness requires style normalization to detect — on raw text it is hidden by *opposing* per-model style artifacts that cancel in the pool (SI-2, pattern B) — while coverage and evenness narrowing are robust on both text branches. Review-panel effects, while extraordinarily consistent, are small in absolute units, and review-cloud displacement is exploratory. Human evenness reference values are condition-specific by construction (the chance benchmark includes each condition's AI reviews) and are never compared across conditions. Several analyses exist on the primary branch only and have no raw-text replication: the strengths/weakness field split (§3.7), claim-level uniqueness (SI-4), and the decision-outcome analysis (SI-6). The field split of §3.7 is a decomposition of the same 23 paired comparisons, not an independent replication of them. The decision-outcome AUCs (SI-6) carry ~±0.25 confidence intervals at 14-vs-9 class balance — ~±0.35 once AI panels are matched to human panel size and proposal set — which is wide enough that no AUC comparison in this study, including human-vs-AI, is statistically separable from chance; only the AI-side point estimates (stable across every matching variant) and the rank-aggregation curves carry interpretable signal there. All results concern one scientific domain, one proposal format, and three models at one point in time.

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

**Reading, proposals — a real human-only periphery, no AI-only territory.** The typical human proposal has an AI proposal about as close as its nearest human peer (0.046 vs 0.048), and AI-only pockets sit at or below the 10% reference: AI proposes nothing humans don't approach. But **18–26% of human proposals have no AI proposal within normal human spacing — roughly double the by-construction reference** — and, notably, the fringe is *largest under persona* (26%). (The main-text Fig. 3*B* uses the mean-probability variant of the same q90 rule and reports 23% / 18% / 26%, which agrees; the earlier majority-of-subsamples figure rule, 26% / 17% / 22%, is superseded.) This is the granular form of the geometric-coverage result (§2.5): the narrowing of generation is territorial. About one human proposal in five occupies ground the equal-sized AI pool simply does not reach.

**Reading, reviews — complete interleaving at review resolution; no territory lost on either side.** *Every* human review has an AI review within normal human spacing (fringe = 0% in all conditions) — indeed the closest other opinion to any given human review is usually an AI review (0.030), closer than the nearest fellow human (0.036). AI-only pockets are at or below reference. So the significant review displacement (§3.5) is not territorial: it is a subtle, systematic *accent* — a small shared component carried by every AI review — detectable only because the whole-cloud test runs on 430 reviews. (Note that review MMD², 0.007–0.016, is *smaller* than the non-significant proposal-side MMD², 0.03–0.06; the review result owes its stars to statistical power, not to a large shift.)

**Together, the sharpest one-line contrast in the study:** *on the generation side, AI loses territory — a fifth of the human idea-space goes unvisited; on the gate-keeping side, AI loses no territory at all — only independence.* This is also why the two stages need different remedies: generation narrowing calls for sources of genuinely peripheral ideas, gate-keeping narrowing calls for genuinely independent judges.

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

### Table SI-2b — Gate-keeping, original text: Cliff's δ (AI panel − human panel)

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
Geometric coverage narrowing (original is *stronger*: pooled 0.60–0.89, significant in all conditions); evenness — human sets more even than chance, AI sets clumped, pooled \*\*\* in all six branch×condition cells; gate-keeping compression under one_at_a_time and persona (δ ≈ −0.9 to −1.0 on both branches) and for Claude/GPT at baseline; the Gemini-at-baseline parity anomaly (replicates exactly on raw text: δ = −0.13 to −0.22, ns); and the human-only proposal fringe (13–31% across branches). Everything the synthesis (§4) leans on hardest survives the branch change.

**B. Style-dependent magnitudes (direction survives; size is distorted by prose).**
Raw text distorts the spread/richness facets in *both* directions, and the pooled baseline null (1.02/0.96 ns) is a cancellation, not an agreement: on raw text Claude and GPT are significantly narrower (0.58–0.87 \*\*\*) while Gemini's verbose, varied prose makes it appear *wider than human* (spread 1.52) — opposing style artifacts that sum to zero in the pool. In the other direction, one_at_a_time's raw ratios (0.14–0.28) wildly *overstate* narrowing because each model answers repeated single requests in a near-template voice; rephrasing brings those cells back to 0.45–0.81. The rephrased branch sits between the two distortions, which is precisely why it is the primary: **raw prose can hide idea-level narrowing (varied wording, repeated ideas) or manufacture it (templated wording, distinct ideas).**

**C. Style-only effects (vanish after rephrasing — these are about prose, not ideas).**
On raw text, every AI model's proposal cloud is significantly displaced from the human cloud (MMD² up to 0.28, all \*\*\*), AI review panels *fail to cover* the human review span (δ ≈ −0.9), and the interleaving statistics show outright segregation (up to 80% of AI reviews in "AI-only pockets," up to 69% of human reviews in a "human-only fringe"). After style normalization, all of this collapses: displacement falls ~20-fold, review coverage flips to *exceeding* the human self-benchmark, and the clouds interleave completely (SI-1). The inference is clean and quotable: **AI text is strongly segregated from human text by style; AI *ideas* are not segregated from human ideas — they are an interleaved, thinned subset.** This also settles the interpretation of the small residual review displacement in §3.5: the "accent" is overwhelmingly stylistic, and what remains after rephrasing is its faint semantic residue.

*Sources: same table paths with `text_version = original`; SI figures for the original branch under `results/figures/synthesis/original/`.*

---

## SI-3. Score-level decision analysis: does the lost disagreement matter for decisions?

A fair challenge to the gate-keeping results runs: *if each AI review covers everything the human reviewers say (SI-1), does the loss of panel diversity matter at all — could review simply be automated?* The facet metrics measure review *text*; funding decisions consume review *scores*. This analysis therefore asks three questions of the numeric `overall_score` data (1–5 scale; never previously used by the diversity pipeline): **(i)** do AI panels disagree less in their scores, proposal by proposal? **(ii)** does human score disagreement predict where human and AI mean scores diverge — i.e., is disagreement carrying information? **(iii)** would AI panels *rank* the proposals differently than the human panels did?

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

This analysis strengthens one half of the gate-keeping claim and honestly bounds the other. **Strengthened:** the variance channel — flagged divisiveness, triggered discussion, confidence calibration — is measurably empty in AI panels, in the numeric currency committees actually use, and no elicitation strategy tested restores it. **Bounded:** we cannot show, from this sample, that the resulting *rankings* differ from human ones; on point estimates, AI panels are as human-like as the human panels are self-consistent. The automation question therefore turns on what a panel is *for*: if it is a scoring machine, this data offers no evidence of harm; if it is a deliberation input — where disagreement selects which proposals get argued about — the input is gone. Resolving whether the lost disagreement changes *outcomes* requires either the claim-level uniqueness analysis (do humans catch load-bearing points AI misses? — now **SI-4**) or a test against real decisions (**SI-6** takes this step using the actual funding outcomes: AI panel scores show no funding signal at all — though with n = 23 the interval is too wide to call that a proven null).

---

## SI-4. Claim-level uniqueness: do human reviewers make points AI panels do not?

SI-1 shows AI reviews are *positioned* near every human review, and SI-3 shows their scores agree too closely. Neither settles the question a program officer would actually ask: **if an AI panel replaced a human panel, which specific points would go unsaid?** Whole-review embeddings cannot answer it — a review is mostly standard assessment plus, occasionally, one decisive catch, and document-level averaging washes that catch out. This analysis works at claim resolution.

**Method.** Each review's `strengths_text` and `weakness_text` is split into atomic claims (sentences; 1,699 claims per condition: 333 human — 170 strengths, 163 weaknesses — and 1,366 AI, median 17 words per claim). Every claim is embedded with the **same encoder and pooling as the prep layer** (BioLinkBERT-large, mean pooling, L2-normalized) by delegating to the prep function itself, so the representation is identical by construction. For each target proposal we then ask, in both directions, whether each claim has a counterpart in the other panel.

Two design choices carry the analysis:

- **The threshold is calibrated, not chosen.** A claim counts as *unmatched* when its nearest claim in the other panel is farther than the median nearest-claim distance between **different human reviewers of the same proposal** (0.084 for strengths, 0.094 for weaknesses). "Unmatched" therefore means "farther apart than two human reviewers of the same proposal typically are" — the same yardstick logic as SI-1.
- **Panels are compared at exact-n** (spec §11.1), drawing the AI side from the *same enumerated panels* every facet metric uses: *m* AI reviews for a proposal with *m* human reviews, averaged over panels (4,505 pooled panels; ~7.5 claims per side). Strengths and weaknesses are matched separately, since a strength "matching" a weakness would be a false match.

### Table SI-4 — Unmatched-claim rates (rephrased branch; pooled AI)

| Condition · polarity | Human claims unmatched | AI claims unmatched | Human unmatched vs the *full* 15-review reservoir |
|---|---|---|---|
| baseline · strengths | 58% | 58% | 30% |
| baseline · weaknesses | 50% | 53% | 21% |
| one_at_a_time · strengths | 50% | 42% | 27% |
| one_at_a_time · weaknesses | 40% | 41% | 16% |
| persona · strengths | 53% | 47% | 32% |
| persona · weaknesses | 40% | 42% | 20% |

*Per-model rates (Claude, Gemini, GPT) span 36–67% human-unmatched and 34–69% AI-unmatched at exact-n — GPT is consistently the closest match to human claims (36–54% human-unmatched) and Gemini the farthest (55–65%) — and are in `results/tables/cross_condition/reviews/claim_uniqueness.csv` (column `matching` distinguishes `exact_n` from `full_ai_reservoir`). Figure: `results/figures/synthesis/rephrased/si_claim_uniqueness.png`. Code: notebook `03_facets_reviews`, section "Claim-level Uniqueness (SI)"; helpers in `src/claim_uniqueness.py`.*

### Findings

**1. Neither panel is a superset of the other.** At matched panel size, a human panel makes **40–58% claims with no counterpart in the AI panel**, and the AI panel makes **41–58% claims with no counterpart in the human panel** — the two rates are near-identical in most cells (e.g. one_at_a_time weaknesses: 40% vs 41%). Human and AI review panels are **complementary, not nested**. This directly refutes the strongest case for automation ("AI already says everything the humans say"): at the panel size a funder would actually deploy, roughly half of what each side contributes is unique to it.

**2. Panel size is the whole ballgame — and the two questions must not be confused.** The right-hand column shows the same human-unique statistic computed against *all fifteen* AI reviews: it falls to 16–32%. That comparison is not wrong, it answers a different question — *does the full AI reservoir contain this point somewhere?* — and its answer is meaningfully more optimistic. The distinction matters practically: **querying many AI reviews and pooling recovers substantially more of what humans say than deploying an equal-sized AI panel does.** Reporting only the pooled number would overstate AI's coverage by 10–24 percentage points; reporting only the matched number would understate what a larger AI reservoir could retrieve. Both are in the table for that reason.

**3. Weaknesses overlap more than strengths** (human-unmatched 40–50% vs 50–58% across conditions). AI reproduces human *criticism* better than human *praise* — the more decision-relevant direction, and a mild point in favor of AI as a critique aid.

**4. one_at_a_time maximizes claim coverage — the same condition that most homogenizes panels internally.** Its human-unmatched rates are the lowest in every polarity (40–50% matched; 16–27% pooled), yet SI-3 and §3 show it produces the *most* internally uniform panels and the largest score-disagreement collapse. Breadth of content and independence of judgment are dissociable, and this elicitation strategy trades one for the other.

### The essential caveat

**Unmatched ≠ substantively novel.** Inspecting the most-distant unmatched human claims (printed by the notebook and saved to `claim_uniqueness_examples.csv`) shows many are generic — "defined milestones and strict adherence to open science principles," "an appropriate timeframe to execute the planned synthesis" — i.e. phrasing-level rather than substantive non-overlap. Because human-unique and AI-unique rates are now nearly *equal*, the interesting question is entirely about which unmatched claims carry decision weight, and embedding distance cannot tell substance from wording. **Before publication these rates require a hand-coding pass** on a sample of unmatched claims (coded: substantively novel point vs restatement in different words), ideally by two coders with a reliability statistic. The examples file exists for exactly that purpose; until then, SI-4 establishes complementarity in *expression* and bounds — but does not yet establish — complementarity in *substance*.

---

## SI-5. Simpson's diversity index (reported explicitly)

*Why this section exists.* Readers of an ecology/diversity paper often expect the classic **Simpson diversity index**. Our headline richness metric (the Vendi score at order q = 1) is from the same mathematical family, and Simpson is exactly its order-2 member — so we compute Simpson directly here, two ways, and it reproduces the richness result.

*What Simpson is, in plain terms.* Simpson's index answers "if I pick two items at random, how likely are they the *same*?" The concentration is D = Σpᵢ² over the category shares pᵢ. Two friendlier forms: **Gini-Simpson** = 1 − D (the chance two picks *differ*; higher = more diverse) and **inverse Simpson** = 1/D (an *effective number* of equally-common categories; higher = more diverse).

*How we compute it — two ways.*

1. **Embedding (similarity-sensitive) Simpson.** Proposals and reviews are points in meaning-space with no discrete "species," so we substitute the eigenvalues λᵢ of the normalized cosine-similarity matrix K/n (which sum to 1, just like proportions) for the category shares pᵢ. Then **inverse Simpson = 1/Σλᵢ²** and **Gini-Simpson = 1 − Σλᵢ²**. Two exact identities we rely on (and verified numerically): 1/Σλᵢ² equals the **Vendi score at q = 2**, and Σλᵢ² equals the **mean squared cosine similarity** — so Gini-Simpson is literally "1 − average squared similarity." This is the honest Simpson for continuous data; the classic categorical index is its special case when items fall into hard, separate groups.
2. **Classical categorical Simpson.** The textbook D = Σpᵢ² on genuinely discrete categories: each proposal is assigned to the single **literature region** it sits nearest to (BERTopic; the outlier bin is dropped), and pᵢ is the fraction of a group's proposals in region i.

*Why both.* The embedding version stays consistent with every other facet (same space, same equal-n and permutation machinery). The categorical version is the exact formula a reader pictures, and it adds genuinely new information — diversity *across areas of the literature* — rather than restating the embedding geometry. Reviews get only the embedding flavor (there is no region label for a review).

*Inference (identical to the facets).* Proposals: Human vs each model at 23-vs-23 (label permutation) and Human vs pooled AI over the cached equal-n subsamples, with jackknife CIs. Reviews: paired within proposal (AI = mean over the exact-n panels), Cliff's δ. Higher effective number = more diverse throughout.

### Table SI-5 — Simpson index, pooled AI vs Human (rephrased branch)

| Stage · flavor | quantity | baseline | one_at_a_time | persona |
|---|---|---|---|---|
| Proposals · embedding Simpson | inverse Simpson, AI ÷ H | 0.76 \*\* | 0.73 \*\*\* | 0.76 \*\* |
| Proposals · categorical (regions) | inverse Simpson, AI ÷ H | 0.78 \* | 0.62 \*\*\* | 0.73 \* |
| Reviews · embedding Simpson | Cliff's δ (AI − H) | −0.39 (p = .09) | −0.83 \*\*\* | −0.74 \*\*\* |

*Absolute values: proposal embedding Simpson — Human behaves like **2.12** effective distinct proposals, pooled AI **1.5–1.6**; categorical region Simpson — Human **4.94** effective regions, pooled AI **3.1–3.9**. Gini-Simpson tells the same story (proposal pooled AI ÷ H ≈ 0.65–0.71). Figures: `results/figures/synthesis/{rephrased,original}/si_simpson_diversity.png`, and the paper's **Fig. 3*A*** version of the categorical region Simpson — `fig3_regions.png`, an effective-regions box+jitter (human fixed at 4.94, AI subsampled to n=23 1000× per condition) built by `src/figure3_regions.py` in notebook 04. Tables: `results/tables/{condition}/{proposals,reviews}/{branch}/simpson_diversity.csv` (+ `cross_condition/simpson/simpson_diversity_all.csv`). Code: notebooks 02/03 section "Simpson Diversity Index (for reporting)"; `src/diversity_facets.simpson_similarity` / `simpson_categorical`; `src/diversity_inference.build_{proposal,review}_simpson_tests`.*

### What it means

Both Simpson flavors and the review δ **reproduce the narrowing already seen in richness** — AI proposal sets hold ~24–38% less effective Simpson diversity, and AI review panels are less diverse for nearly every proposal under structured elicitation (baseline marginal, one_at_a_time and persona strong), exactly mirroring the richness facet (§2.2, §3.1). Two things of added value: (i) the **inverse Simpson equals the Vendi VS₂ exactly** (2.122 for human proposals — a numeric agreement confirming the two implementations match), and (ii) the **categorical region Simpson** shows the narrowing is not only geometric but also spread across *fewer effective areas of the biomedical literature* (one_at_a_time strongest at 0.62). Because Simpson (order 2) weights the most common/duplicated items more heavily than the Shannon-based richness (order 1) does, its close agreement with the q = 1 headline confirms the finding is not an artifact of which diversity "order" we chose to report.

---

## SI-6. Decision-outcome analysis: can a panel reproduce the *actual* funding decisions?

Every gate-keeping metric so far measures review *text* (facets, interleaving, claims) or within-panel score spread (SI-3). None asks the question a funder ultimately cares about: **if you swapped the human panel for an AI panel, would the same proposals get funded?** This analysis uses the competition's **real funding ranking and fund/not decision** for all 23 proposals as ground truth.

**Ground truth, and where it comes from.** The outcome labels are the competition's own `proposal_status` field in `data/human-proposals/human-proposals-y{1,2}.json` — **14 `Accepted`, 9 `Rejected` across the 23 proposals** — together with each proposal's `ranking`. The prep layer converts status to the boolean `target_funding` (`is_accepted_or_funded` in `src/prepare_reviews_for_analysis.py`) and carries it, with `target_ranking`, into `data/prepared/{condition}/reviews/proposal_review_scores_summary.csv`, which is what `src/decision_outcome.py` consumes. Nothing here is derived from review text or review scores.

**What was tested.** For each panel (human; and AI under each condition) we take the panel's mean `overall_score` per proposal and ask: (i) how well it reproduces the actual funding ranking (Spearman ρ); (ii) whether it can tell funded from not-funded proposals (area under the ROC curve; 0.5 = chance); and (iii) whether *adding reviewers* improves the ranking agreement (the error-cancellation / Condorcet question).

**Panel composition — read this before comparing the two sides.** The headline AUC is deliberately *unmatched*, and in three separate ways:

| | AI panel | Human panel |
|---|---|---|
| Reviews per proposal | **15** — 5 Claude + 5 Gemini + 5 GPT, pooled | **1–4** scored reviews (mean **3.14**) |
| Proposals in the AUC | **all 23** (14 funded vs 9 not; 126 discordance pairs) | **14** with ≥1 score (8 vs 6; 48 pairs) |
| Cohort mix of those proposals | 12 y1 + 11 y2 | **11 y2 + 3 y1** — 9 of 12 y1 proposals carry no human scores at all |

This is the right design for the **AI-side-alone** question — *do AI panel scores carry any funding signal?* — where using all 23 proposals and the full reservoir is simply better powered. It is **not** a fair human-vs-AI contrast, and unlike every other metric in §3 it does not use the exact-n matching of spec §11.1. The next subsection removes all three asymmetries and reports what changes. Note the expected direction first: a larger panel averages away more noise, so the unmatched design is **generous to AI**, not punitive — shrinking AI's panel could not rescue it.

**How the AUC is bounded (added 2026-08-24).** A bare AUC of 0.50 is ambiguous at this sample size: it can mean "demonstrably at chance" or "too few proposals to tell." Two distribution-free devices separate the readings (`decision_outcome.funding_auc_inference`, B = 10,000 each):
- a **stratified bootstrap 95% CI** — funded and not-funded proposals resampled *within class* with replacement, both class sizes held fixed so every draw has a computable AUC — answering *how much would this AUC move on another sample of proposals?*;
- a **two-sided label-permutation p** — the funded/not labels shuffled across the scored proposals with the scores held fixed, p = the share of shuffles whose |AUC − 0.5| is at least the observed one — answering *could scores carrying no outcome signal have produced this?*

**Why it fits.** A review panel's job is not to enumerate issues — which AI does about as well as humans (SI-4) — but to make a reliable fund/reject decision. Two mechanisms give a panel that reliability, and both require *disagreement*: **error cancellation** (independent judgments average out idiosyncratic error; *correlated* judgments do not — the diversity-prediction theorem, and the Condorcet jury theorem's conditional-independence assumption) and **discrimination** (a panel can only rank proposals if its scores actually vary across them). Testing against the real outcome measures both.

**Result.**
- **AI panel scores carry no detectable funding signal — and the interval says how weak a claim that is.**

  | Panel | AUC | 95% bootstrap CI | permutation p | class balance |
  |---|---|---|---|---|
  | Human | 0.77 | [0.48, 1.00] | .089 | 8 funded vs 6 not (14 scored) |
  | AI · baseline | 0.50 | [0.25, 0.75] | .990 | 14 vs 9 (all 23) |
  | AI · one-at-a-time | 0.47 | [0.22, 0.72] | .839 | 14 vs 9 (all 23) |
  | AI · persona | 0.50 | [0.25, 0.76] | .988 | 14 vs 9 (all 23) |

  The AI point estimates sit **exactly** at chance and the permutation p-values are as unremarkable as a p-value gets (.84–.99) — there is no hint of signal in these scores. But the CIs are **~±0.25 wide**, so the data are equally consistent with a *moderately useful* panel (AUC ≈ 0.72–0.76) as with chance. **This is an absence of evidence, not a precise null**, and the earlier phrasing ("an AI panel cannot reproduce the decisions") claimed more precision than n = 23 supports.
- **The human–AI AUC gap is not itself demonstrated.** The human 0.77 rests on 8 × 6 = 48 discordance pairs; its CI is [0.48, 1.00] and it does not clear chance either (p = .089). Every AI interval overlaps it. Whatever else this table shows, it does not establish that human panels out-discriminate AI panels — and the panels being compared are not even the same shape (see the matched decomposition below).
- **AI rank-agreement with the actual funding ranking saturates early and low.** A single AI reviewer reaches ρ = 0.21 (baseline) / 0.28 (one-at-a-time) / 0.32 (persona); adding reviewers buys a little at first and then flattens: by the eighth reviewer every condition sits at ρ = 0.41–0.43, and the last four reviewers are worth **≤ 0.04** (baseline +0.03, one-at-a-time +0.02, persona −0.01 — it declines). Human review, by contrast, *aggregates upward without saturating over the range available* (ρ 0.63 → 0.99 from 1 to 4 reviewers, on the scored subset). Correlated judgments stop cancelling error; independent ones keep cancelling it.
- **The mechanism.** AI panel scores vary *less across proposals* than human scores (between-proposal SD 0.36 baseline / 0.54 one-at-a-time / 0.52 persona vs 0.62 for humans on the shared scored proposals), and — critically — even where AI varies almost as much as humans (one-at-a-time, persona), its variation does not align with the funding outcome (AUC 0.47 and 0.50). AI's score-convergence (the "central blanket," §3.4), in the currency of the decision, leaves the panel with no *measurable* ability to discriminate proposals — bounded, as above, by an interval that cannot rule out a moderate one.

**How to read it / implications.** On point estimates, an AI panel — however many reviewers it has — reproduces the real funding decisions no better than chance, and the *rank* evidence (which uses all 23 proposals and every panel size, not just the binary outcome) is the sturdier half of the finding: the AI curve saturates at ρ ≈ 0.44 while human review keeps aggregating. The AUC's job here is to say *how strongly* that can be asserted, and the answer is: directionally, not quantitatively. **What survives the interval:** AI panel scores show no funding signal, and no elicitation strategy tested produces one. **What does not survive it:** any claim that AI panels are *demonstrably worse* than human panels at the funding decision, or that AI discrimination is precisely zero. This is the decision-currency version of the gate-keeping thesis: what an AI panel loses is not issue *coverage* (SI-4) but the *independent, discriminating judgment* that lets a panel rank, and that a funder actually consumes. It rests on well-established theory about why judgment diversity matters for collective decisions: the **diversity-prediction theorem** (collective error = average individual error − judgment diversity), the **Condorcet jury theorem's** requirement of conditionally independent voters, **algorithmic monoculture** (shared models → correlated, systemic failures), and the epistemic value of **transient disagreement** (premature consensus converges on worse answers). *(Manuscript citations to be finalized.)*

### Is the human-vs-AI comparison fair? The matched decomposition

Because the two panels differ in size, in proposal set, and in cohort mix, the human-vs-AI AUC contrast above cannot be read at face value. This subsection strips the asymmetries away one at a time (`decision_outcome.matched_funding_auc`; notebook `03`, section *"Decision-outcome, size- and proposal-matched"*):

- **A — as published.** AI, 15 reviews, all 23 proposals.
- **B — proposal-matched.** AI, still 15 reviews, restricted to the 14 human-scored proposals. Isolates the *proposal-set* effect (and with it most of the cohort skew).
- **C — fully matched.** AI panels drawn at **exactly the human panel size for that proposal** (1–4 reviews, mean 3.14), without replacement, on those same 14 proposals, averaged over 2,000 draws. Adds the *panel-size* effect on top of B, and puts AI on precisely the exact-n footing used by every other metric in §3.

The human row is unchanged across variants — its own 1–4 reviews on its own 14 proposals *are* variant C.

### Table SI-6b — Funding AUC as the asymmetries are removed (pooled AI, rephrased)

| Panel | Variant | baseline | one-at-a-time | persona |
|---|---|---|---|---|
| **Human** (14 props, 3.14 reviews) | C | 0.77 [0.48, 1.00] p=.089 | *(same — scores are condition-invariant)* | |
| Pooled AI | **A** 15 rev, 23 props | 0.50 [0.25, 0.75] p=.990 | 0.47 [0.22, 0.72] p=.839 | 0.50 [0.25, 0.76] p=.988 |
| Pooled AI | **B** 15 rev, 14 props | 0.51 [0.19, 0.81] p=.977 | 0.42 [0.08, 0.75] p=.635 | 0.46 [0.15, 0.79] p=.833 |
| Pooled AI | **C** exact-n, 14 props | 0.50 [0.13, 0.86] p=.973 | 0.45 [0.10, 0.78] p=.783 | 0.50 [0.17, 0.83] p=.972 |

**Per-model, variant C** (exact-n, 14 proposals): Claude 0.43 / 0.43 / 0.53, Gemini 0.51 / 0.50 / 0.52, GPT 0.58 / 0.46 / 0.48 (baseline / one-at-a-time / persona). All nine cells ns, permutation p = .63–.97; every CI spans chance. Full rows: `results/tables/cross_condition/reviews/decision_outcome_matched_auc.csv`.

### What the decomposition shows

**1. The AI null is not an artifact of the mismatch.** Across A → B → C the pooled AI AUC moves by at most 0.06 within a condition and never leaves the neighbourhood of chance (0.42–0.51 overall, every permutation p ≥ .63). Neither restricting to the human proposal set nor shrinking the AI panel from 15 reviews to ~3 changes the conclusion. The unmatched design was **generous** to AI — more reviewers, more proposals — and AI did not benefit from the generosity, which is itself informative: it is what the score-convergence mechanism predicts (if every reviewer says ~4, averaging more of them changes nothing).

**2. But it makes the human-vs-AI contrast unusable, and that is the honest finding.** Matching costs precision on both axes: variant C's intervals run **~±0.33 to ±0.37** (baseline [0.13, 0.86]), against ±0.25 for variant A. On the properly matched comparison — the only version anyone should quote for human-vs-AI — the human 0.77 [0.48, 1.00] and the AI 0.45–0.50 (intervals from ≈0.10 to ≈0.86) overlap across almost their entire range. **At 14 proposals with ~3-review panels there is no resolving power for a human-vs-AI accuracy claim in either direction.**

**3. What this does and does not license.** *Licensed:* "AI panel scores show no funding signal, and this holds whether the AI panel is 15 reviews over 23 proposals or size-matched to the human panel over the same 14." *Not licensed:* any statement that human panels discriminate better than AI panels. That comparison was never powered, and the earlier version of this section leaned on it more than the data allow.

**Why the rank curve (panel B of the figure) is the sturdier evidence.** It sidesteps the worst of this: `rank_corr_vs_k` matches panel size explicitly (k reviewers drawn from each source at each k) and the AI side uses all 23 proposals at every k. Its finding — AI saturating at ρ ≈ 0.44 while human review keeps aggregating to 0.99 — rests on far more data than the single binary AUC, though the human and AI curves still run over different proposal sets (proposals with ≥ k human scores: 14, 13, 11, 6 as k goes 1→4).

**Caveats, stated plainly.** The funding ranking was set by the human review process, so the **human curve has a built-in advantage** — the human-vs-AI gap is *not* a task-independent accuracy comparison, and at these intervals it is not a demonstrated gap at all. The headline AUC additionally compares unmatched panels (15 AI reviews over 23 proposals vs 1–4 human reviews over 14, skewed to cohort y2); Table SI-6b matches them and shows the AI conclusion is unaffected while the human-vs-AI contrast loses what little resolving power it had. The load-bearing, defensible result is the **AI side alone: AI panel scores show no funding signal**, phrased as an absence of evidence rather than a proven null (CIs ~±0.25). Numeric human scores exist for only 13–14 proposals (the human curve's high-*k* points rest on ~6 proposals); the AI results use all 23. The analysis is **exploratory** at n = 23, and the AUC interval is the honest statement of what that costs: at 14-vs-9 the analytic (Hanley–McNeil) standard error is 0.126, giving ±0.247 — an independent check that reproduces the bootstrap half-width of ~0.25 — and detecting a genuinely useful AUC of 0.65 against chance at 80% power would need about **4–5× as many proposals (~100–115)**. Nothing about this design was ever going to resolve a moderate effect. Figure: `results/figures/synthesis/rephrased/si_decision_outcome.png`. Tables: `results/tables/cross_condition/reviews/decision_outcome_{proposal_scores,curves,summary}.csv`. Code: notebook `03_facets_reviews` section "Decision-outcome Analysis (SI)"; `src/decision_outcome.py`.

---

## 5. Statistical notes for the general reader

- **Permutation test.** To ask whether two groups differ more than chance allows, we repeatedly shuffle the group labels (10,000 times) and recompute the difference. The p-value is the fraction of shuffles producing a gap as large as the real one. No distributional assumptions.
- **Cliff's δ (paired).** For each of the 23 proposals we ask: did the AI panel come out lower or higher than the human panel? δ is the balance of those outcomes: −1 (lower every time) to +1 (higher every time). It measures *consistency of direction*, complementing the raw magnitude. Its p-value comes from the exact paired Wilcoxon test, whose floor at n = 23 is ~2×10⁻⁷ — values at that floor mean "as significant as this design can express."
- **Effective numbers (Vendi score).** A set's similarity structure is converted into "this set of 23 behaves like N fully distinct items." It is the same mathematics ecologists use to say a forest with 23 trees of highly overlapping species behaves like 3 effective species. These "effective numbers" form a family indexed by an order q; **richness (our headline) is order 1** (the Shannon-equivalent) and **Simpson's index is order 2** (weights common items more). We report richness as primary and Simpson explicitly in **SI-5**; they agree.
- **Chance references (nulls).** Wherever a metric has no natural zero, we manufacture the honest benchmark: random same-sized draws from the pooled data (for clumping), one random half of the human set covering the other (for coverage), or leave-one-out self-coverage (for review panels). "Significant" always means "outside what those benchmarks produce."
- **Confidence intervals.** Set-level metrics use leave-one-out (jackknife) intervals — recompute 23 times, each time omitting one proposal. Pooled-AI values use 1,000 subsamples of 23 drawn without replacement. We never resample with replacement, which would inject duplicates into metrics that are exquisitely sensitive to duplicates.
- **Multiple testing.** With ~7 metric families × 3 models × 3 conditions × 2 stages × 3 review fields, some "significant" results would arise by chance. **Six comparisons were designated primary in advance in the pipeline** — one headline metric per facet (spread, richness, evenness, dimensionality, geometric coverage) plus the displacement check — and are read at face value on `p_raw`; the manuscript drops dimensionality as a null (§2.4, §3.3) and reports the remaining **five** primaries. every other p-value shown has been inflated by the Benjamini–Hochberg procedure, run once over the whole secondary family within each `task × text_version × field` stratum (510 tests on the proposal side), to control the expected fraction of false discoveries.
- **Equal sample sizes everywhere.** Every diversity metric grows with the number of items measured, so all comparisons — including the pooled-AI ones and all union counts — are made at exactly 23 vs 23.

---

## Appendix: audit and reproducibility

- **Audit trail.** The statistical pipeline was audited line-by-line against the design specification (2026-07-15/16): the review-side coverage and evenness pairings, the trend-test direction, domain-coverage inference, FDR family structure, and the evenness-slope metric were corrected; presentation was subsequently re-oriented so that every panel reads "up/right = more diverse" (Direction Rule), with statistics verified byte-identical before and after the visual redesign. AI reviews were regenerated with the corrected prompt on 2026-07-16 and notebooks 03–04 recomputed; proposal-side inputs (embeddings, group structure) were verified unchanged, so generation results carry over exactly. **Second audit, 2026-08-24:** every cell of Tables 1a/1b/1c, SI-2a/2b/2c, SI-3, SI-4, SI-5 and SI-6 was re-derived directly from the CSVs the current notebooks write and reproduced exactly; the corrections applied were to the primary/secondary description, four numeric ranges, one statistic that no notebook computes, the figure/table inventory, and the omission of the review `field` axis (now §3.7) — itemized at the top of this document.
- **Superseded result.** An earlier run (incorrect review prompt) showed baseline AI review panels as *more* diverse than human panels; that finding did not survive the prompt correction and should not be cited.
- **Sources — tables.** Per cell, `results/tables/{condition}/{task}/{text_version}/`:
  - `facet_diversity_tests.csv` — every facet metric *plus* the `lexical_control` rows of §2.8, the `displacement` MMD²/`ot_wasserstein` rows of §2.7/§3.5, and the multiple per-facet estimators of §2.9. On the review side the `field` column carries `whole` / `strengths` / `weakness` (§3.7).
  - `facet_fingerprint.csv` (sign-aligned one-axis summary: z-scores vs the same-size null for proposals, Cliff's δ for reviews), `facet_interleaving.csv` (SI-1), `facet_diversity_gradient.csv` (JT trend tests with the `direction_ok` flag), `facet_diversity_curves.parquet`, `facet_null_reference.parquet` (proposals), `facet_review_paired_long.csv` (the 23 per-proposal paired rows), `simpson_diversity.csv` (SI-5).
  - Cross-condition copies under `results/tables/cross_condition/{proposals,reviews}/{branch}/` and `results/tables/cross_condition/simpson/simpson_diversity_all.csv`.
  - Review-only, cross-condition: `results/tables/cross_condition/reviews/score_decision_analysis.csv` (SI-3), `claim_uniqueness.csv` + `claim_uniqueness_examples.csv` (SI-4), `decision_outcome_{proposal_scores,curves,summary}.csv` (SI-6 — `decision_outcome_summary.csv` carries `funding_auc`, `funding_auc_ci_lo/_hi`, `funding_auc_p_perm`, `n_funded`, `n_not_funded`, `between_proposal_sd`, from `decision_outcome.funding_auc_inference`), and `decision_outcome_matched_auc.csv` (Table SI-6b — the A/B/C size- and proposal-matched decomposition, pooled and per model, from `decision_outcome.matched_funding_auc`).
  - Synthesis: `results/tables/synthesis/{branch}/double_compression_summary.csv` — the merged ratio/z/δ table `04` builds and every synthesis figure is drawn from (717 rows rephrased, 429 original).
  - *Not a source:* `results/tables/{condition}/{task}/{branch}/facet/…` is a superseded location from an earlier pipeline version and is no longer written.
- **Sources — figures.** Per cell, `results/figures/{condition}/{task}/{branch}/`: `facet_fingerprint`, the per-facet panels (box / ridge / effect / profile / scree / envelope / CDF / NN histogram / coverage scatter / rarefaction / region-occupancy heatmap / MMD² bar / paired slopes), the illustration UMAPs, and `_convergence/facet_convergence_heatmap` (§2.9; computed over all 24 group-cells × 12 metrics and written under every cell path). Synthesis, `results/figures/synthesis/{branch}/`:
  - `fig1_diversity_fingerprint`, `fig2_double_compression_slopegraph` (+ `fig2_supplement_{spread,coverage,dimensionality,evenness}_*`), `fig2b_human_ai_slopegraph` (+ `fig2b_supplement_*`; Human→AI slopes in natural units), `fig3_compression_map`, `fig4_robustness_grid`, `fig5_paired_umaps_{condition}`, `fig6_condition_gradient`.
  - `fig_generation_geometry` (§2.7 — per-proposal nearest-human vs nearest-AI with the fringe ringed, plus coverage and displacement bar insets), `fig_filtering_panel` (§3 — 23 per-proposal Human→AI panel lines), `fig_main_facet_slopegraph` (all facets, both stages, one grid), `si_generation_geometry_umap` (UMAP alternate to `fig_generation_geometry`).
  - SI panels: `si_interleaving_{proposals,reviews}` (SI-1), `si_wording_vs_idea_gap` (§2.8), `si_simpson_diversity` (SI-5), and — `rephrased` only — `si_claim_uniqueness` (SI-4) and `si_decision_outcome` (SI-6).
- **Specs:** `docs/plans/diversity_facets_design_spec_v2.md`, `docs/plans/facet_visualization_redesign_spec.md`.
