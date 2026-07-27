# PNAS Nexus submission — paragraph skeleton

**Target:** Research Report, ~4,000 words main text, ~4 display items, ~50 references, single SI Appendix.
**Structure:** results-first, Materials and Methods last (PNAS-family convention).
**Numbers below are the audited values** from `2026-07-16_facet_diversity_audited_results.md` (rephrased branch is primary).

Format of this file: each section gives its heading, a candidate topic sentence (**TS**) per paragraph, and the ordered points that paragraph makes as bullets. Citations sit inline in the bullet that needs them. Visuals appear as a line under the paragraph they anchor.

Writing rules held throughout: no em dashes, no forced triplets, mixed sentence lengths, no filler vocabulary.

---

## FRONT MATTER

### Title (pick one)
1. Double compression: how AI narrows both the generation and the review of scientific ideas
2. AI reproduces the center of scientific search and thins its edges
3. Frontier AI narrows scientific idea generation and peer review, and prompting for diversity does not fix it

Recommendation: #1 for idea-first venues, #2 to foreground the geometric finding. Keep "double compression" in the title or the abstract.

### Abstract (≤250 words, one paragraph)
Beats in order:
- Grant review is a cultural practice of science with two diversity-dependent stages: proposing ideas, and judging them.
- AI now does both jobs, so adopting it may raise individual output quality while shrinking collective range.
- Data: 23 confidential biomedical proposals and their expert reviews, unlikely to be in training data, against Claude, Gemini, and GPT given the same call and criteria.
- Design: three elicitation conditions of rising diversity pressure, up to persona conditioning.
- Finding 1 (generation): AI proposal sets hold 64 to 75 percent of human diversity in distinct ideas, cover 81 to 86 percent of the human idea space, and cluster into near-duplicates, while touching the same literature topics.
- Finding 2 (filtering): Given the same proposal, AI review panels are tighter and less varied than the human panel for nearly every proposal (Cliff's δ down to −1.0 under structured prompting), yet each AI panel individually sits within 95 to 98 percent of the human review span. Each AI review is thorough, but a panel of them says nearly the same thing repeatedly, while in a human panel each reviewer says different things. At the level of specific points, neither side is a superset: a matched AI panel and a human panel each raise roughly half the claims the other does not. [current abstract wording, in use]
- Twist: persona conditioning restores neither loss. It closes the wording gap without closing the idea gap.
- Close: evaluating AI for science by individual output quality misses this collective cost.

### Significance statement (50 to 120 words, plain language)
Reuse the draft2 significance statement almost verbatim. Remove any claim of a model ranking; state only that every model falls below humans. Keep the "persists even when we engineer for diversity" sentence as the last line.

---

## INTRODUCTION (5 short paragraphs, 600 to 800 words total; keep each tight)

### Para 1 — grant review as two-stage collective search, and a cultural practice
**TS:** Scientific grant review is where a research community decides which ideas to pursue, and it works through two stages that both depend on variety.
- Proposals come from a decentralized pool of investigators, each shaped by their own training and interests.
- Reviewers then judge which proposals are novel, feasible, and worth funding.
- Both stages are collective search: generation of candidate directions, then filtering of them.
- Peer review is an institution of science, an epistemic culture through which a field forms shared judgment.
- The health of that culture depends on the range of what is proposed and the range of judgments applied, not on the quality of any single proposal or review.

### Para 2 — AI enters both stages, and the risk this carries
**TS:** AI systems can now draft proposals and write reviews, which lets them act at both stages at once.
- Models generate research ideas, search the literature, draft proposals, and produce evaluative judgments [CITE AI-generates-ideas; CITE AI-reviews].
- If institutions rely on a few frontier models, the diversity of ideas and of judgments may fall even as each output looks competent.
- Generative AI has been shown to raise individual creativity while lowering the collective diversity of what a population produces (Doshi & Hauser 2024).
- AI adoption in science concentrates attention on established, data-rich areas (Hao et al. 2024).
- We call this risk double compression: AI may narrow search once by generating a narrower set of candidates, and again by filtering the survivors with more uniform judgment.
- Diverse generation raises the chance that a valuable direction is proposed at all; diverse filtering raises the chance that a proposal's hidden weakness or overlooked strength is caught by someone on the panel.

### Para 3 — why this has been hard to study
**TS:** This has been hard to test, because the raw material of scientific search is usually hidden and most AI evaluations score individual outputs.
- Grant proposals and expert reviews are confidential, so the distribution of real scientific ideas is rarely available for analysis.
- Controlled ideation studies lack the stakes, expertise, and institutional realism of actual funding (Doshi & Hauser 2024).
- Quality metrics for an individual proposal or review cannot, by construction, detect a change in the distribution of ideas or judgments.
- The obvious shortcut of comparing public proposals against AI ones is confounded, because frontier models have likely trained on any publicly available proposals.

### Para 4 — the data and the design
**TS:** We study this with data that avoids these problems and a design that separates a property of the models from an artifact of prompting.
- Our corpus is 23 proposals submitted to a real molecular and cellular bioscience competition, together with their expert reviews, unlikely to appear in any training set because the process is confidential.
- Three frontier models (Claude, Gemini, GPT) draft proposals from the same call given to the human scientists, and review the same proposals under the same criteria given to the human reviewers, which holds the task environment fixed across humans and AI.
- AI idea diversity sits below human levels but shifts with how models are prompted (Meincke et al. 2024), so a single-strategy test could not tell a model property apart from a prompting artifact.
- We therefore generate and review under three conditions of rising diversity pressure: baseline, where one request returns the whole set; one-at-a-time, where each item comes from an independent call, removing the within-context homogenization by which a model conditions each new item on the ones before it; and persona, where each independent call is conditioned on a distinct scientist persona matched to a real applicant.
- Persona conditioning is the strongest documented intervention against LLM homogeneity (Meincke et al. 2024; De Freitas et al. 2025), so if narrowing were a prompting artifact it should ease under one-at-a-time and dissolve under persona.
- Two questions follow: do AI models generate proposal sets as diverse as those of human scientists, and do AI panels review a given proposal as diversely as human panels.

### Para 5 — findings and contribution
**TS:** We find that AI narrows search at both stages, that the two kinds of narrowing differ in character, and that engineering for diversity removes neither.
- In generation, AI proposes fewer distinct ideas inside the same topics, and occupies a smaller region that sits within the human one rather than beside it.
- In filtering, AI review panels lose independence rather than coverage: each AI review is broad, but a panel of them repeats itself while human reviewers disagree.
- Persona conditioning leaves both idea-level gaps intact while nearly closing the gap in wording.
- No reliable ranking separates the three models, and every model sits below humans.
- Our contribution moves the evaluation of AI for science from individual output quality to collective search, and shows that the fix is harder than better prompting.

---

## RESULTS (2,000 to 2,400 words)

### Lead paragraph
**TS:** We compared each group in a shared biomedical embedding space, after rewriting every proposal and review into one neutral style so that wording could not stand in for ideas.
- Diversity is not one quantity, so we measured five facets of how a set fills the space: spread, richness, evenness, dimensionality, and coverage, plus a directional displacement check.
- All comparisons are made at matched sample size.
- Generation effects are group ratios, where 1.0 is human parity; filtering effects are paired Cliff's δ, where a negative value means the AI panel was less diverse for that proposal.

*Visual: Fig 1, design schematic. → `results/figures/synthesis/fig1_design_schematic.png`, generated by the standalone script `src/fig1_design_schematic.py` (no data; reuses the project palette). Shows the two-stage pipeline (generation, then filtering) crossed with three models and three conditions, the shared inputs (same call, same 23 human proposals reviewed), and the matched AI-vs-Human comparison at equal n. Optional; fold into text if space is tight.*

### §A — AI generates fewer distinct ideas within the same topics

#### Para A1 — spread and richness
**TS:** AI proposal sets are less varied than human sets in every condition, holding two-thirds to three-quarters of human diversity in genuinely distinct ideas.
- Ideas sit closer together: pooled AI holds 64 to 70 percent of human spread, significant in every condition (baseline p=.010, one-at-a-time p<.001, persona p=.003).
- The effective count of distinct ideas is lower: pooled AI holds 66 to 75 percent of human richness by the Vendi score, significant in every condition.
- In plain terms, the 23 human proposals behave like about three fully independent ideas, while AI sets behave like about two.
- Per-model contrasts are mostly underpowered at n=23, so the pooled contrast carries the inference.

*Visual: Fig 2, facet fingerprint across the three conditions, oriented so that up means more diverse. → `results/figures/synthesis/rephrased/fig1_diversity_fingerprint.png` (nb 04). Top block is generation (per-facet z scores vs a same-n pooled-cloud null, with jackknife/subsample CIs); bottom block carries the filtering δ used in §C, so one file anchors both stages. (Schematic reading-key panel and the B/C panel letters removed in nb 04 on 2026-07-26.)*

#### Para A2 — evenness
**TS:** The narrowing takes a specific form: AI returns to the same ideas and produces near-duplicate clumps that human sets do not.
- Human proposals spread more evenly than chance in every condition (excess −0.14 to −0.23), while pooled AI clumps more than chance (+0.06 to +0.14, p≈.001).
- At a distance where about 35 percent of human proposals have a close twin, over 80 percent of Claude's baseline proposals already do.
- This is the failure mode that average-distance metrics hide, which is why the multi-facet design exists.

*Visual: Fig 2 (same fingerprint, `results/figures/synthesis/rephrased/fig1_diversity_fingerprint.png`). Nearest-neighbor curve to SI → `results/figures/{baseline,one_at_a_time,persona}/proposals/rephrased/evenness_nn_similarity_hist.png` and `.../evenness_ripley_excess_envelope.png` (nb 02).*

#### Para A3 — dimensionality and domain coverage are null
**TS:** The narrowing is not a collapse onto fewer axes or a retreat from areas of biology, but a thinning of variety inside the same topics.
- AI proposals vary along about as many independent axes as human proposals (participation ratio 0.85 to 1.06; only one-at-a-time is modestly reduced at 0.85, p=.02).
- AI touches the same regions of the literature and at least as many subject terms (all groups touch 5 to 8 of 12 regions; AI touches 571 to 598 unique MeSH terms against 504 for humans, ns).
- Read with A1 and A2, the mechanism is precise: the same number of axes, the same topics, fewer distinct positions along them, and repeated returns to those positions.

*Visual: Fig 2 (the null facets sit at parity beside the narrowed ones, `results/figures/synthesis/rephrased/fig1_diversity_fingerprint.png`). Supporting per-facet panels: `results/figures/{condition}/proposals/rephrased/dimensionality_participation_ratio_box.png` and `.../coverage_bertopic_region_rarefaction.png` (nb 02).*

### §B — AI narrows toward a shared center, not into new territory

#### Para B1 — coverage and displacement
**TS:** AI reaches most of the human idea space but not its edges, and it sits inside the human region rather than off to one side.
- Pooled AI covers 81 to 86 percent of the human idea space, below the human self-benchmark at baseline (p=.038) and persona (p<.001), and marginal at one-at-a-time (p=.08).
- Displacement is near zero in every condition (MMD² 0.032 to 0.062, all ns; the human split-half floor is about 0), so AI occupies a competent central core and misses the periphery rather than wandering into its own territory.
- Model choice matters more here than for any other facet: Claude covers the human space fully (1.00) while Gemini reaches only 61 percent.
- The missed periphery is concrete: 18 to 26 percent of human proposals have no AI proposal within normal human spacing, and the fringe is largest under persona (26 percent).

*Visual: Fig 3, generation geometry (interleaving, projection-free): per-condition dumbbells of each human proposal's distance to its nearest other human versus its nearest AI, with the human-only fringe ringed, plus coverage and displacement bar insets. → `results/figures/synthesis/rephrased/fig_generation_geometry.png`, built by `fig_generation_geometry()` in nb 04. For most humans the nearest AI is about as close as the nearest human (AI interleaved, not beside); fringe = nearest AI beyond the human q90 yardstick (26/17/22% by condition). Coverage bars use `coverage_geometric` ai_value (k=3); displacement bars use the `mmd2` effect_size, computed in the full embedding space. The UMAP composite is retained as an SI alternate, `si_generation_geometry_umap.png` (see SI note).*

### §C — AI review panels lose independence, and at the level of specific points, roughly half the content

#### Para C1 — spread and richness within panels
**TS:** Given the same proposal, AI review panels are tighter and less varied than the human panel for nearly every proposal, though the gap is small in size.
- The direction is near-deterministic: at one-at-a-time, pooled δ = −0.91 for spread and −0.83 for richness, with several model cells at δ = −1.00, meaning lower for all 23 proposals; persona is similar (pooled δ = −0.74).
- At baseline, Claude and GPT show the same pattern (δ −0.74 to −0.91), but Gemini sits at parity (δ +0.04, ns), which dilutes the pooled baseline to marginal (δ ≈ −0.3 to −0.4, p=.07 to .09).
- The absolute gap is small: human panels average 0.044 mutual distance against 0.028 to 0.040 for AI, and effective richness is 1.13 to 1.19 against 1.18.
- Consistency, not magnitude, is what a funding portfolio should care about, because a small systematic bias does not average out across many decisions the way a large noisy one would.

*Visual: Fig 4, filtering: per-proposal paired slopes, rows = facets (spread, richness, coverage), columns = conditions, each line one of the 23 target proposals from its human panel to its matched pooled-AI panel. → `results/figures/synthesis/rephrased/fig_filtering_panel.png`, built by `fig_filtering_panel()` in nb 04 from `facet_review_paired_long.csv`. Spread and richness rows fall; per-panel δ annotations read −0.39 / −0.91*** / −0.74*** and −0.30 / −0.83*** / −0.74***. The δ-across-facets view also exists in the filtering block of `fig1_diversity_fingerprint.png`.*

#### Para C2 — coverage runs the other way at the level of whole reviews
**TS:** As whole documents, AI reviews sit near everything the human reviewers wrote, so the panel loses independence without drifting into a separate region.
- AI panels cover 95 to 98 percent of the human review span, above the human self-benchmark of 83 percent (pooled δ +0.37 to +0.44, significant in every condition; Claude δ +1.00 everywhere).
- AI panels also clump more than chance (pooled δ +0.91 at one-at-a-time, +0.74 at persona) and vary along as many axes as human panels (dimensionality null, 12 of 12 cells ns).
- High coverage together with low spread and heavy clumping describes several copies of one thorough, centrally positioned reviewer.
- A committee learns from disagreement among its reviewers, and that is exactly what an AI panel does not provide.
- This coverage is positional, not propositional: it says AI reviews occupy the same region, not that they make the same points (see C2b).

*Visual: the coverage row of `fig_generation_geometry`'s counterpart on the filtering side, i.e. the bottom row of `results/figures/synthesis/rephrased/fig_filtering_panel.png`, where lines rise from human to AI (δ = +0.37** / +0.44** / +0.37**), making the central-blanket pattern visible beside the falling spread and richness rows above it.*

#### Para C2b — at the level of specific points, neither panel is a superset
**TS:** The high whole-review coverage describes position, not content: when reviews are broken into their individual claims, a matched AI panel and the human panel each raise about half the points the other does not.
- Splitting every review into atomic claims (sentences of its strengths and weaknesses, embedded with the same encoder), a matched-size AI panel leaves 40 to 58 percent of the human panel's claims with no near counterpart, and the human panel leaves a near-equal 41 to 58 percent of the AI panel's claims unmatched (SI-4).
- The threshold is calibrated, not chosen: a claim is unmatched only when its nearest claim in the other panel is farther than two human reviewers of the same proposal typically are from each other.
- Human and AI review panels are therefore complementary, not nested, which is the direct answer to "why not automate the panel": an equal-sized AI panel does not just lose disagreement, it loses about half the specific content the human panel would have raised.
- The honest bound: unmatched is not yet shown to mean substantively novel. The most-distant unmatched human claims read as generic ("defined milestones," "an appropriate timeframe"), so these rates measure non-overlap in expression, and a hand-coding pass is needed before the substance claim is made (SI-4 caveat).

*Visual: `results/figures/synthesis/rephrased/si_claim_uniqueness.png` (nb 04). Panel A: matched-panel human-unique vs AI-unique rates per condition and polarity (bars nearly equal height = complementarity). Panel B: the same human-unique rate against a matched panel vs the full 15-review reservoir, showing the panel-size dependence. SI figure; one summary sentence in main text.*

#### Para C3 — the loss reaches the scores committees use
**TS:** The lost disagreement reaches the numeric scores a committee consumes, though at this sample we can bound its effect on rankings rather than assert one.
- Human panels disagree substantially (score SD 0.74 on a five-point scale), while AI panels compress this two- to tenfold, with Claude at one-at-a-time near unanimous (SD 0.075, lower for every scoreable proposal).
- AI rankings track the human ranking (ρ 0.43 to 0.46) about as well as half the human panel tracks the other half (split-half ceiling ρ ≈ 0.40), so we cannot show the rankings differ.
- Only 13 of 23 proposals have two or more scored human reviews, which limits this analysis.
- A panel used as a scoring machine loses nothing here; a panel used as a deliberation input loses its trigger.

*Visual/placement: full analysis in SI Appendix (Table SI-3), with one summary sentence in main text to protect the word budget. **No figure exists.** Optional SI figure **[TODO]**: per-proposal human-panel vs AI-panel score SD, plus rank agreement against the human split-half ceiling (ρ ≈ 0.40). Data: `results/tables/cross_condition/reviews/score_decision_analysis.csv`, generated in nb 03 section "Score-level Decision Analysis (SI)".*

### §D — engineering for diversity does not restore diversity

#### Para D1 — persona persists on ideas and closes wording
**TS:** Persona conditioning, the strongest available intervention against AI homogeneity, leaves the idea-level narrowing intact while nearly closing the gap in wording.
- Persona generation richness is 0.75 (p=.004), indistinguishable from baseline.
- The lexical gap in wording narrows to 1.04 to 1.07 under persona while the idea-level spread and richness gaps persist, so personas change how models write, not what they propose.
- On the filtering side the structured conditions strengthen review compression rather than easing it, from baseline (δ ≈ −0.3 pooled) to one-at-a-time (δ ≈ −0.9).
- No condition reaches human diversity at either stage.

*Visual: annotate the persona column in Fig 2 and Fig 4 (`fig1_diversity_fingerprint.png` shows all three conditions side by side). The across-condition trend also has a dedicated figure → `results/figures/synthesis/rephrased/fig6_condition_gradient.png` (condition gradient, pooled AI subsampled to n=23, nb 04).*

#### Para D2 — no model ranking holds
**TS:** The three models differ in which facet they lose, not in whether they lose one, and no ordering among them holds up.
- The pre-specified ordering (Claude < Gemini < GPT < Human) fails on both stages, and the effect is dominated by the human-AI gap.
- Claude covers the human idea space fully but with repetitive proposals; Gemini is the narrowest and the only displaced model in generation, yet the least compressed reviewer at baseline; GPT is intermediate and the most human-like in position.
- The defensible statement is that humans sit above every model.

*Visual: per-model tables to SI; main text states the null ordering in prose. Supporting figure that shows each model's position and that none orders cleanly → `results/figures/synthesis/rephrased/fig3_compression_map.png` (generation ratio on x, filtering ratio on y, parity lines at 1.0, one marker per model×condition, nb 04). Per-model robustness grid for SI → `results/figures/synthesis/rephrased/fig4_robustness_grid.png` (facets × tasks, never collapsed).*

---

## DISCUSSION (600 to 800 words, 4 paragraphs)

### Para 1 — the compression is asymmetric, not symmetric
**TS:** AI compresses scientific search at both stages, but the two compressions differ in kind, and saying so is more accurate than claiming a single doubled effect.
- Generation loses large magnitude, 25 to 36 percent of effective diversity.
- Filtering loses little diversity in size but almost all independence, proposal after proposal, and at the level of specific points it also loses about half the content a human panel would have raised (SI-4).
- The two do not multiply; they are complementary, because generation narrows what enters the pool while filtering standardizes how the pool is judged.
- AI reviewers agree with one another, while human reviewers disagree, and that disagreement is the reason a proposal gets more than one reader. The score-level analysis (SI-3) shows this disagreement is measurably absent from the numbers a committee consumes, though at this sample we can bound its effect on the resulting rankings rather than assert one.
- A fully automated pipeline would draw from a poorer menu and judge it with one palate, and would miss roughly half the specific strengths and flaws a human panel would have flagged.

### Para 2 — culture of science and language diversity
**TS:** Read as a cultural process, grant review is where a field builds shared judgment, and AI adoption pushes that judgment toward a single center.
- Peer review is a cultural practice of science that AI is now embedded in and reshaping, so the risk is homogenization of an epistemic culture rather than low quality of any single output.
- AI also narrows wording (lexical ratios 1.04 to 1.24; self-BLEU 0.21 to 0.35 against 0.19 for humans), and persona closes the wording gap without closing the idea gap, which separates linguistic variety from conceptual variety.
- Language diversity is one demonstrated facet of the effect here, not its core.

### Para 3 — practical implication and stage-specific remedies
**TS:** Institutions should evaluate AI for science by its effect on collective search, and the two stages need different fixes.
- Individual-output benchmarks miss this cost by construction.
- Generation narrowing calls for genuinely peripheral sources of ideas, not better prompting of one model.
- Filtering narrowing calls for genuinely independent judges, since one model reviewed many times is one voice.
- Persona prompting is not a remedy for either.

### Para 4 — limitations
**TS:** Several limits bound these claims and point to the next studies.
- Samples are small at 23 per group, so per-model generation contrasts are underpowered and the pooled contrasts carry the inference.
- The pooled baseline generation effect on spread and richness needs style normalization to detect, because opposing per-model style artifacts cancel on raw text; coverage and evenness narrowing hold on both text branches.
- Review-panel effects are small in absolute units, and the score analysis rests on 13 proposals with scored human reviews.
- The results cover one domain, one proposal format, three models, and one point in time.

---

## MATERIALS AND METHODS (800 to 1,000 words; detail to SI)

Each subsection is two to four sentences and points to the SI Appendix for full detail.

- **Human proposals.** 23 proposals to a molecular and cellular bioscience competition across two cohorts, confidential and so unlikely to be in training data. [Open item: confirm what can be named about the program; add a data-availability statement.]
- **AI proposals.** Claude, Gemini, and GPT each received the same call, generated 23 ideas, and expanded each into a full proposal per condition, giving 69 AI proposals per condition and matching the human set per model. Temperature was 0.9, raised rather than lowered so as not to hobble the AI side.
- **Generation conditions.** Baseline generates all 23 in one pass; one-at-a-time draws each idea from an independent call; persona conditions each independent call on a distinct scientist persona card matched to an applicant. A persona card carries career stage, subfield, and methodological orientation, and does not contain proposal content.
- **Human reviews.** Expert reviews of the 23 proposals under the program criteria, 2 to 5 per proposal, [NUM total]. Only 13 proposals have two or more numerically scored reviews.
- **AI reviews.** Each model reviewed each human proposal under the same criteria, 5 reviews per model per proposal, across the three conditions. Reviewing the human proposals holds the object of evaluation fixed, so any difference reflects the reviewers.
- **Literature corpus.** 39,538 PubMed abstracts from January 2010 to May 2026, used for domain coverage only.
- **Text standardization and embedding.** All texts were rephrased into one neutral style before embedding so comparisons reflect content and not prose, then embedded with BioLinkBERT-large. Diversity is computed in the full embedding space; two-dimensional projections are used only for display.
- **Facet measures.** Spread is mean pairwise distance; richness is the Vendi score; evenness is excess close-neighbor mass against a same-size null; dimensionality is the participation ratio; coverage is support overlap against a human self-benchmark, with BERTopic regions and MeSH terms for domain coverage; displacement is MMD. Full estimators are in SI.
- **Inference.** Comparisons are at matched sample size. Unpaired proposal comparisons use label permutation; paired within-proposal review comparisons use the Wilcoxon signed-rank test; the ordering across models uses the Jonckheere-Terpstra test. Three comparisons were pre-designated primary (spread, richness, geometric coverage); all others are under Benjamini-Hochberg FDR control. The rephrased branch is primary, with the original branch as robustness.

---

## SI APPENDIX (PNAS Nexus uses one SI Appendix PDF; there is no in-line supplement section)

Route here, in this order. Figure paths are the rephrased branch unless the item is the original-branch comparison itself.
- **SI-1. Interleaving.** Human-only fringe and AI-only pockets, nearest-neighbor spacing, per group. Table SI-1 and the two interleaving panels → `results/figures/synthesis/rephrased/si_interleaving_proposals.png` and `.../si_interleaving_reviews.png` (nb 04). Granular geography behind Fig 3 and §C2.
- **SI-geometry (UMAP alternate).** The projection view of generation geometry → `results/figures/synthesis/rephrased/si_generation_geometry_umap.png` (nb 04 `fig_generation_geometry_umap`). Same fringe rings and coverage/displacement insets as Fig 3, on a 2D UMAP. Caption must state that the human/AI separation is a projection artifact (Chari and Pachter, 2023) and that displacement is near zero; keep it as the reader-facing "spatial" companion to the interleaving Fig 3.
- **SI-2. Original-text branch.** Full facet battery on raw text, Tables SI-2a and SI-2b, and the three-pattern reading of style-robust, style-distorted, and style-only effects. Figures: the entire `results/figures/**/original/` tree, including `results/figures/synthesis/original/fig1_diversity_fingerprint.png` and the per-condition `results/figures/{condition}/{proposals,reviews}/original/` panels. This licenses the rephrased branch as primary and is itself a methodological result.
- **SI-3. Score-level decision analysis.** Table SI-3, the variance-collapse finding, and the ranking-ceiling bound. Referenced from §C3 and Discussion Para 1. Table source: `results/tables/cross_condition/reviews/score_decision_analysis.csv`. **No figure exists**; optional [TODO] figure described under §C3.
- **SI-4. Claim-level uniqueness.** Table SI-4 and the complementarity finding: at matched panel size, human and AI panels each leave 40 to 58 percent of the other's atomic claims unmatched; the full-15-review reservoir recovers more (human-unmatched drops to 16 to 32 percent). Referenced from §C2b and Discussion Para 1. Includes the calibrated-threshold method and the "unmatched ≠ substantively novel" caveat with the hand-coding protocol as the stated pre-publication step. Figure → `results/figures/synthesis/rephrased/si_claim_uniqueness.png` (nb 04); table source `results/tables/cross_condition/reviews/claim_uniqueness.csv` (+ `claim_uniqueness_examples.csv`); helpers in `src/claim_uniqueness.py`, code in nb 03 section "Claim-level Uniqueness (SI)". This is the cleanest rebuttal to "why not automate the panel," so it strengthens rather than qualifies the thesis.
- **Per-model tables.** Full Tables 1a, 1b, and 1c with every model cell and significance, from `results/tables/{condition}/{task}/rephrased/facet_diversity_tests.csv`. Supporting figure: `results/figures/synthesis/rephrased/fig4_robustness_grid.png`.
- **Persona card construction.** Contents, matching to applicant profiles, and the leakage check. [TODO — no figure; text plus an example card.]
- **Metric definitions and nulls.** Full estimators, jackknife and subsampling intervals, kernel-sensitivity check, and the plain-language statistical notes. Per-facet scree/profile figures exist per condition (e.g. `.../richness_vendi_profile.png`, `.../dimensionality_participation_ratio_scree.png`).
- **Robustness.** Kernel sensitivity for richness; neighborhood-size stability for coverage at k = 2, 3, 5; the Gemini-baseline flagged cell and its qualitative check. Figure: `results/figures/synthesis/rephrased/fig4_robustness_grid.png`; convergence check `.../proposals/rephrased/_convergence/facet_convergence_heatmap.png`.

---

## FIGURE CAPTIONS (draft, PNAS style)

PNAS legends open with a result sentence, then label panels (*A*), (*B*), (*C*), then define n, error bars, test, and significance key. Italic *P*. Significance key throughout: **P* < 0.05, ***P* < 0.01, ****P* < 0.001; ns, not significant. Primary branch is the rephrased, style-normalized text unless noted.

**Fig. 1. Design of the two-stage comparison.** Twenty-three biomedical grant proposals from a confidential funding competition, and the expert reviews they received, are compared against proposals and reviews produced by three frontier models (Claude, Gemini, GPT). Each model drafts proposals from the call given to human applicants and reviews the same 23 human proposals under the criteria given to human reviewers, which holds the task environment fixed. Generation and review are each elicited under three conditions of increasing diversity pressure: baseline, one request returning the full set; one-at-a-time, each item from an independent call; and persona, each independent call conditioned on a distinct scientist persona matched to an applicant. All diversity measures are computed in a shared BioLinkBERT embedding space at matched sample size. → `results/figures/synthesis/fig1_design_schematic.png` (`src/fig1_design_schematic.py`)

**Fig. 2. AI narrows generation and review on the facets that count distinct ideas, not on the number of axes or the range of topics.** Diversity is decomposed into five facets, each oriented so that higher is more diverse (Direction Rule), for the three elicitation conditions (columns). The top block (generation) shows each facet as a z score against a same-n pooled-cloud null (999 draws; coverage against the human split-half null), so values right of zero are more diverse than the human reference and values left are narrower. The bottom block (filtering) shows sign-aligned Cliff's δ (AI − Human) across the 23 matched review panels, where negative means the AI panel is less diverse for that proposal. Evenness is a clumping metric and enters negated to share the common direction. Whiskers are 95% jackknife or subsample intervals in the generation block and bootstrap intervals in the filtering block; pooled AI is subsampled to n = 23 from 69 proposals. Stars are *P*_raw for the three pre-registered primaries (spread, richness, geometric coverage) and Benjamini-Hochberg *P*_fdr otherwise. Displacement is a directional check rather than a diversity facet and appears in Fig. 3. Original-text branch in *SI Appendix*. → `synthesis/rephrased/fig1_diversity_fingerprint.png`

**Fig. 3. AI proposals interleave with human proposals rather than occupying a separate region, and a stable human periphery is left unvisited.** Top row: for each of the 23 human proposals (rows, sorted by nearest AI), its distance to the nearest other human (red) and to the nearest AI (blue), computed in the full embedding space, with the AI distance taken as the median over the exported size-23 AI subsamples. For most human proposals the two distances are close, so AI proposals sit among the humans, not beside them. The dashed line is the human q90 nearest-neighbor yardstick; a human whose nearest AI falls beyond it is ringed as the human-only fringe, which holds 18 to 26% of human proposals and is largest under persona. Bottom row: geometric coverage, the fraction of the human idea region reached by AI, benchmarked against human split-half self-coverage (pooled AI reaches 0.81 to 0.86, below the benchmark at baseline and persona); and displacement between the human and AI clouds, measured as MMD² against a shuffle null, near zero in every condition (human split-half floor ≈ 0). n = 23 per group, pooled AI subsampled from 69. → `synthesis/rephrased/fig_generation_geometry.png`

**Fig. 4. Given the same proposal, AI review panels are less varied than the human panel yet cover more of what the humans said.** Rows are facets (spread, richness, geometric coverage) and columns are the three conditions. Each faint line is one of the 23 target proposals, connecting its human panel to the matched pooled-AI panel of equal size; large markers are per-condition medians. Spread and richness fall from human to AI for nearly every proposal, with paired Cliff's δ reaching −0.91 for the pooled panel under one-at-a-time and persona (−1.0 for individual models); the absolute gap is small because review panels are homogeneous for all groups. Geometric coverage rises from human to AI, each AI panel reaching 0.95 to 0.98 of the human review span, above the human leave-one-out self-benchmark of 0.83. The rows together show AI reviews that are individually broad but collectively interchangeable. δ annotations are paired Cliff's δ (AI − Human) with stars from the review tests. → `synthesis/rephrased/fig_filtering_panel.png`

**Fig. 5. Human-to-AI diversity does not recover across conditions at either stage.** Each panel connects the human value to the AI value, with generation on the top row and filtering on the bottom, across baseline, one-at-a-time, and persona from left to right. A line rising toward parity from left to right would show that stronger elicitation restores diversity; no line reaches parity in any condition, and the wording gap closes under persona while the idea gap does not. Richness (Vendi score) is shown as the primary facet; other facets are in *SI Appendix*. Pooled AI subsampled to n = 23. → `synthesis/rephrased/fig2b_human_ai_slopegraph.png` (alternate framings: `fig2_double_compression_slopegraph.png`; per-model `fig3_compression_map.png`)

### Supporting and SI captions

**Fig. S_gradient. Diversity across the three conditions, pooled AI.** Facet values for pooled AI (subsampled to n = 23 from 69) at baseline, one-at-a-time, and persona, showing that no condition reaches human diversity and that structured elicitation does not close the idea-level gap. → `synthesis/rephrased/fig6_condition_gradient.png`

**Fig. S_map. Each model loses diversity, and no ordering among models holds.** Generation ratio (proposals, AI ÷ Human) on the x axis against filtering ratio (reviews, AI ÷ Human) on the y axis, one marker per model and condition, with parity lines at 1.0. Every marker sits below or left of human parity, and the models do not fall in a consistent order. → `synthesis/rephrased/fig3_compression_map.png`

**Fig. S_robustness. Facets by task and model, never pooled.** Rows are facets, columns are generation and filtering, with one series per model; every row reads up for more diverse. Ratio rows show AI ÷ Human against parity at 1; the evenness row is sign-aligned against its null at 0. → `synthesis/rephrased/fig4_robustness_grid.png`

**Fig. S_interleave. Neither side holds territory the other never reaches on the review side, while a fifth of the human idea space goes unvisited on the generation side.** Nearest-neighbor distances to the opposite group, benchmarked against human-to-human spacing (the 90th percentile of human-to-nearest-human distance). Shares near 10% mean no more exclusive than humans are from each other. Proposals show an 18 to 26% human-only fringe with no matching AI-only pocket; reviews show 0% human-only fringe. → `synthesis/rephrased/si_interleaving_proposals.png`, `si_interleaving_reviews.png`

**Fig. S_original. The facet battery on raw, unrephrased text.** Same layout as Fig. 2 on the original-text branch. Coverage and evenness narrowing hold on both branches; the pooled baseline spread and richness effects require style normalization to detect, because opposing per-model style artifacts cancel on raw text. → `synthesis/original/fig1_diversity_fingerprint.png`

**Fig. S_score. Score disagreement collapses in AI panels, while rankings cannot be shown to differ at this sample.** *[TODO: figure not yet generated.]* Per-proposal human-panel score SD against matched AI-panel score SD, and rank agreement between panels benchmarked against the human split-half reliability ceiling (ρ ≈ 0.40). Data: `results/tables/cross_condition/reviews/score_decision_analysis.csv` (nb 03).

**Fig. S_claim. At matched panel size, human and AI review panels each raise about half the specific claims the other does not.** Reviews are split into atomic claims (sentences of the strengths and weakness fields), embedded with the same encoder as the main analysis (BioLinkBERT-large, mean pooling). A claim is unmatched when its nearest claim in the other panel is farther than the median nearest-claim distance between two human reviewers of the same proposal (0.084 for strengths, 0.094 for weaknesses). (*A*) Human-unique and AI-unique unmatched rates at matched panel size (exact-n, spec §11.1), by condition and polarity; the paired bars are near-equal, so neither panel is a superset of the other. (*B*) The same human-unmatched rate against a matched AI panel versus the full 15-review reservoir, which recovers more of the human claims (16 to 32 percent unmatched). Descriptive; unmatched indexes non-overlap in expression and is not yet shown to be substantive non-overlap. → `synthesis/rephrased/si_claim_uniqueness.png`

---

## DISPLAY-ITEM BUDGET (4 main plus SI)

1. **Fig 1.** Design schematic: two stages, three models, three conditions, matched comparison. → `results/figures/synthesis/fig1_design_schematic.png` (`src/fig1_design_schematic.py`). Optional; fold into text if space is tight.
2. **Fig 2.** Generation facet fingerprint across the three conditions, oriented up = more diverse. Anchors §A and §D. → `results/figures/synthesis/rephrased/fig1_diversity_fingerprint.png` (exists; Panel A generation, Panel C filtering).
3. **Fig 3.** Generation geometry: human cloud with the unreached fringe, coverage and displacement insets. Anchors §B. → `results/figures/synthesis/rephrased/fig_generation_geometry.png` (nb 04 `fig_generation_geometry`).
4. **Fig 4.** Filtering: paired spread and richness (negative δ) beside coverage (positive δ), showing the central-blanket pattern. Anchors §C and §D. → `results/figures/synthesis/rephrased/fig_filtering_panel.png` (nb 04 `fig_filtering_panel`).
5. **Slopegraph** (human versus AI, generation to filtering) as Fig 1b or the first SI figure, to show the asymmetry from Discussion Para 1. → `results/figures/synthesis/rephrased/fig2b_human_ai_slopegraph.png` (exists; see also `fig2_double_compression_slopegraph.png` and the per-model `fig3_compression_map.png`).

If four is the hard cap: Fig 2, Fig 3, Fig 4, and the slopegraph; move the design schematic into text. All five (Fig 1, Fig 2, Fig 3, Fig 4, slopegraph) now exist as generated files.

**Fig 3 resolved (2026-07-26):** the canonical Fig 3 is the projection-free interleaving view (`fig_generation_geometry.png`), which shows "AI interleaves with humans, not beside them" without the UMAP's misleading separation. The UMAP composite is kept as an SI alternate (`si_generation_geometry_umap.png`) for readers who want a spatial view; its caption must state that the visual separation is a projection artifact and that the displacement statistic is near zero.

---

## OPEN ITEMS BEFORE DRAFTING PROSE
- Verify the persona-collapse and De Freitas citations (flagged MEDIUM in draft2).
- Confirm what can be named about the funding program; write the data-availability statement.
- Fill the AlphaFold, AI-generates-ideas, and AI-reviews citation slots.
- Decide C3 placement (recommend SI with one main-text sentence).
- Decide the title.
- SI-4 hand-coding: code a sample of unmatched claims as substantively-novel vs restatement-in-different-words (ideally two coders + a reliability statistic) before the claim-level rates are stated as content non-overlap rather than expression non-overlap. Until done, keep §C2b and the abstract wording at "expression," not "substance."
- Confirm the un-auditable Methods values against the generation/prep configs: sampling temperature (0.9), total human-review count (the `[NUM total]` slot), and the PubMed corpus span.
