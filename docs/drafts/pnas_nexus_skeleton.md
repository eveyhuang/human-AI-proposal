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
2. When AI writes and reviews grant proposals, it narrows the ideas proposed and the judgments applied
3. Frontier AI narrows scientific idea generation and peer review, and prompting for diversity does not fix it

Recommendation: #1 for idea-first venues, #2 to foreground the geometric finding. Keep "double compression" in the title or the abstract.

### Abstract (≤250 words, one paragraph)
Beats in order:
- Scientific grant review has two stages that both depend on variety: many investigators propose ideas, and panels of reviewers judge them.
- AI can now do both jobs. Using it may improve each proposal or review while reducing the range of ideas that are proposed and the range of judgments that are applied.
- Data: 23 confidential proposals to a biomedical funding competition and their expert reviews, unlikely to be in any training set, compared with proposals and reviews from Claude, Gemini, and GPT given the same call and the same review criteria.
- Design: three ways of prompting the models, from a single request to a distinct scientist persona per proposal, chosen to increase the variety of the output.
- Finding 1 (proposals): AI proposal sets contain 25 to 36 percent fewer distinct ideas than human sets and include more near-duplicates, while covering the same research topics.
- Finding 2 (reviews): given the same proposal, AI reviewers agree with one another more than human reviewers do and give nearly the same score, where human reviewers give a range. Each AI review is close to the human reviews, yet at the level of specific points an AI panel and a human panel each raise about half that the other does not. Against the competition's actual funding decisions, an AI panel's scores cannot tell which proposals were funded, while a human panel's scores can.
- Prompting for more variety removes the difference in wording but not the difference in ideas or judgments.
- Judging AI for science by the quality of individual proposals or reviews misses this effect on the range of ideas and judgments.

### Significance statement (50 to 120 words, plain language)
Reuse the draft2 significance statement almost verbatim. Remove any claim of a model ranking; state only that every model falls below humans. Keep the "persists even when we engineer for diversity" sentence as the last line.

---

## INTRODUCTION (5 short paragraphs, 600 to 800 words total; keep each tight)

### Para 1 — grant review has two stages that both depend on variety
**TS:** Scientific grant review is how a research community decides which ideas to fund, through two stages that both depend on variety.
- Proposals come from many investigators, each shaped by their own training and interests.
- Reviewers then judge which proposals are novel, feasible, and worth funding.
- Both stages depend on variety: the range of ideas proposed, and the range of judgments applied to them.
- What a field ends up funding depends on this variety across many proposals and reviews, not on the quality of any single one.

### Para 2 — AI enters both stages, and the risk this carries
**TS:** AI systems can now draft proposals and write reviews, which lets them act at both stages at once.
- Models generate research ideas, search the literature, draft proposals, and produce evaluative judgments [CITE AI-generates-ideas; CITE AI-reviews].
- If institutions rely on a few frontier models, the diversity of ideas and of judgments may fall even as each output looks competent.
- Generative AI has been shown to raise individual creativity while lowering the collective diversity of what a population produces (Doshi & Hauser 2024).
- AI adoption in science concentrates attention on established, data-rich areas (Hao et al. 2024).
- We call this risk double compression: AI may narrow search once by generating a narrower set of candidates, and again by gate-keeping the survivors with more uniform judgment.
- Diverse generation raises the chance that a valuable direction is proposed at all; diverse gate-keeping raises the chance that a proposal's hidden weakness or overlooked strength is caught by someone on the panel.

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

### Para 5 — what we find
**TS:** AI reduces variety at both stages, the two effects differ, and prompting for more variety removes neither.
- In generation, AI proposes fewer distinct ideas within the same topics, in the same region of idea space as human proposals rather than a separate one.
- In review, each AI review is close to the human reviews, but the AI reviews of a proposal resemble one another and their scores barely differ, where human reviews of the same proposal differ.
- Prompting for more variety removes the difference in wording but not the difference in ideas or judgments.
- No reliable ranking separates the three models; all fall below humans.
- We therefore evaluate AI for science by its effect on the range of ideas and judgments across proposals and reviews, rather than the quality of individual ones, and show that better prompting does not remove the effect.

---

## RESULTS (2,000 to 2,400 words)

### Lead paragraph
**TS:** We compared each group in a shared biomedical embedding space, after rewriting every proposal and review into one neutral style so that wording could not stand in for ideas.
- Diversity is not one quantity, so we measured four facets of how a set fills the space: spread, richness, evenness, and coverage, plus a directional displacement check.
- All comparisons are made at matched sample size.
- Generation effects are group ratios, where 1.0 is human parity; gate-keeping effects are paired Cliff's δ, where a negative value means the AI panel was less diverse for that proposal.

*Visual: Fig 1, design schematic. → `results/figures/synthesis/fig1_design_schematic.png`, generated by the standalone script `src/fig1_design_schematic.py` (no data; reuses the project palette). Shows the two-stage pipeline (generation, then gate-keeping) crossed with three models and three conditions, the shared inputs (same call, same 23 human proposals reviewed), and the matched AI-vs-Human comparison at equal n. Optional; fold into text if space is tight.*

### §A — AI generates fewer distinct ideas

#### Para A1 — spread and richness
**TS:** AI proposal sets are less varied than human sets in every condition, holding two-thirds to three-quarters of human diversity in genuinely distinct ideas.
- Ideas sit closer together: pooled AI holds 64 to 70 percent of human spread, significant in every condition (baseline p=.010, one-at-a-time p<.001, persona p=.003).
- The effective count of distinct ideas is lower: pooled AI holds 66 to 75 percent of human richness by the Vendi score, significant in every condition; the classical Simpson index, reported explicitly in SI, agrees (inverse-Simpson AI-to-human 0.73 to 0.76).
- In plain terms, the 23 human proposals behave like about three fully independent ideas, while AI sets behave like about two.
- Per-model contrasts are mostly underpowered at n=23, so the pooled contrast carries the inference.

*Visual: Fig 2, the all-facet Human → pooled-AI slopegraph grid → `results/figures/synthesis/rephrased/fig_main_facet_slopegraph.png` (nb 04 `plot_facet_slopegraph_grid`). Rows = facets (spread, richness, evenness, coverage), columns = stage (generation | gate-keeping); the shared Human anchor fans to pooled AI for each condition (colour), a downward slope = narrowing. Anchors §A1–A2 and §C. The multi-facet z-score fingerprint is retained in SI for readers who want the whole battery at once.*

#### Para A2 — evenness
**TS:** AI proposal sets include near-duplicate proposals; human sets do not.
- Human proposals are spaced more evenly than a random draw would be in every condition (close-neighbour excess −0.14 to −0.23), while AI proposals are more crowded than a random draw (+0.06 to +0.14, p≈.001).
- At a distance where about 35 percent of human proposals have a near-duplicate, over 80 percent of Claude's baseline proposals do.
- Average distance alone would miss this, because near-duplicates and an even spread can give the same average; this is why we use several measures.

*Visual: Fig 2 (evenness row, `fig_main_facet_slopegraph.png`). Nearest-neighbor curve to SI → `results/figures/{baseline,one_at_a_time,persona}/proposals/rephrased/evenness_nn_similarity_hist.png` and `.../evenness_ripley_excess_envelope.png` (nb 02).*

### §B — AI proposals engage the same topics and occupy the same region, packed more tightly

#### Para B1 — same topics, same region, tighter packing, slightly lower coverage
**TS:** AI proposals engage the same research topics as human proposals and fall in the same region of idea space, with the same center and extent, but they are packed more tightly and reach slightly less of it.
- AI engages the same research areas, not a narrower set of them. It touches the same regions of the biomedical literature (all groups touch 5 to 8 of 12) and at least as many subject terms (571 to 598 unique MeSH terms versus 504 for humans, ns). The reduced variety (§A) is within topics, not avoidance of topics.
- The AI and human proposal sets are not separated. A two-sample distance test cannot distinguish the two clouds in any condition (MMD² 0.032 to 0.062, all ns; a second human sample gives about 0). AI proposals reach the same range of distances from the shared center as human proposals do.
- AI reaches slightly fewer of the human proposals than a second human sample would. About 85 percent of human proposals have an AI proposal nearby (geometric coverage 0.81 to 0.86 relative to the human self-benchmark; below it at baseline p=.038 and persona p<.001, marginal at one-at-a-time p=.08).
- This shortfall is not a distinct region that AI never enters. The proposals fall into two topical groups of very different internal density, and one distance cutoff applied to both mislabels proposals in the sparse group as unreached. Assessed within each group, the share of human proposals with no AI nearby is about 9 percent, the same as humans leave among themselves (SI-1). A single global cutoff gave 18 to 26 percent, but that figure is an artifact of the two-group structure.
- Model choice matters more here than for any other measure: Claude covers the human space fully (1.00) while Gemini reaches only 61 percent.

*Visual: Fig 3, generation geometry (projection-free). **Needs rework** (2026-08): the current version (`fig_generation_geometry.png`, nb 04) leads with the global human-only fringe, which we now know is inflated by the two-group structure (per-group ≈ 9%, at the human baseline). Rebuild to lead with (i) the two clouds are not separated — each AI proposal is about as close to a human as humans are to each other (nearest-neighbour panel), and (ii) AI reaches slightly fewer human proposals than a second human sample (coverage bars vs the human self-benchmark). Show the fringe only as a per-group value at the ~10% reference, not as a headline. The UMAP composite is dropped (it implies a separation the distance test refutes; see SI-geometry note). The same-topics point uses domain coverage → SI rarefaction `results/figures/{condition}/proposals/rephrased/coverage_bertopic_region_rarefaction.png` (nb 02).*

### §C — AI reviewers of the same proposal say similar things and give similar scores

#### Para C1 — AI reviews of a proposal resemble one another
**TS:** For a given proposal, the AI reviews resemble one another more than the human reviews do, for nearly every proposal, though the difference is small in absolute terms.
- The difference is in the same direction for almost every proposal. Under one-at-a-time, the AI reviews are more similar to one another than the human reviews on both measures for all or nearly all 23 proposals (paired Cliff's δ = −0.91 for spread, −0.83 for richness; individual models reach −1.00). Persona is similar (δ = −0.74).
- At baseline, Claude and GPT show the same pattern (δ −0.74 to −0.91), but Gemini does not differ from humans (δ +0.04, ns), so the baseline pooled effect is weaker (δ ≈ −0.3 to −0.4, p=.07 to .09).
- In absolute terms the difference is small, because review panels are internally similar for both groups: the average distance between two reviews of the same proposal is 0.044 for human panels and 0.028 to 0.040 for AI panels.
- The direction being consistent across proposals is what matters for funding. A small difference that goes the same way for nearly every proposal shifts which proposals rank highest; a larger but inconsistent one would not.

*Visual: the gate-keeping column of Fig 2 (`fig_main_facet_slopegraph.png`) carries this in the main text (spread and richness slope down, δ annotated). Per-proposal detail — 23 lines per panel — moves to SI → `results/figures/synthesis/rephrased/fig_filtering_panel.png` (Fig. S_paired; `fig_filtering_panel()` in nb 04 from `facet_review_paired_long.csv`; per-panel δ read −0.39 / −0.91*** / −0.74*** for spread and −0.30 / −0.83*** / −0.74*** for richness across baseline/one-at-a-time/persona).*

#### Para C2 — each AI review is broad, but the AI reviews resemble each other
**TS:** Each AI review is close to the range of points the human reviewers made, but the AI reviews of a proposal are also close to one another.
- Taken one at a time, each AI review is near the human reviews: an AI review covers 95 to 98 percent of the span of the human reviews, more than one human review covers the others (83 percent; pooled δ +0.37 to +0.44 in every condition; Claude +1.00 everywhere).
- The AI reviews of a proposal are also close to one another (they cluster; δ +0.91 at one-at-a-time, +0.74 at persona). Combined with the smaller spread in C1, this means a panel of AI reviews contains little that any one of them would not.
- High coverage here means each AI review is located near the human reviews in the embedding, not that the AI reviews raise the same specific points as the humans; whether they do is examined next (C2b).

*Visual: the coverage row of Fig 2's gate-keeping column, which rises from human to AI (δ = +0.37** / +0.44** / +0.37**) while spread and richness fall; the per-proposal version is the SI paired panel (`fig_filtering_panel.png`).*

#### Para C2b — each panel raises points the other does not
**TS:** A single AI review is located near the human reviews, but that does not mean the AI panel raises the same specific points; broken into individual points, the AI panel and the human panel each raise about half that the other does not.
- We split each review into individual points (the sentences of its strengths and weaknesses) and embedded each one. For a proposal, a matched-size AI panel raises 40 to 58 percent of points with no close counterpart in the human panel, and the human panel raises a similar 41 to 58 percent with no counterpart in the AI panel (SI-4).
- A point counts as unmatched only when its nearest point in the other panel is farther apart than two human reviewers of the same proposal typically are; the cutoff is set from the human reviews, not chosen by hand.
- So the two panels overlap but neither contains the other: replacing a human panel with an AI panel of the same size would drop about half of the specific points the human panel would have raised, and add a similar number of different points.
- One limit: two points can be phrased differently but mean the same thing, and the embedding cannot always tell these apart. The most distant unmatched human points are often generic ("defined milestones," "an appropriate timeframe"), so these percentages measure differences in wording as well as in substance; separating the two requires reading and hand-coding a sample of points (SI-4).

*Visual: `results/figures/synthesis/rephrased/si_claim_uniqueness.png` (nb 04). Panel A: matched-panel human-unique vs AI-unique rates per condition and polarity (bars nearly equal height = complementarity). Panel B: the same human-unique rate against a matched panel vs the full 15-review reservoir, showing the panel-size dependence. SI figure; one summary sentence in main text.*

#### Para C3 — human reviewers give a range of scores; AI reviewers give nearly the same score
**TS:** Human reviewers give the same proposal a range of scores, while AI reviewers give it nearly the same score, and this affects which proposals an AI panel would fund.
- On a 1-to-5 scale, the scores a human panel gives one proposal have a standard deviation of about 0.74. AI panels give scores two to ten times closer together; Claude under one-at-a-time gives nearly the same score to every reviewer, for every proposal (standard deviation 0.075).
- We tested whether this changes the funding decision directly, using the competition's actual outcomes. An AI panel's average score cannot tell which proposals were funded (area under the ROC curve 0.47 to 0.50, i.e. chance, in every condition), and adding more AI reviewers does not help (agreement with the real ranking stays near 0.43 from 1 to 15 reviewers). A human panel's average score does track the outcome, and improves as more reviewers are added (0.62 to 0.99); Fig 4.
- The reason an AI panel cannot rank proposals is that its scores barely vary across proposals: it rates most proposals about the same, so it cannot separate them.
- Two limits: only 13 of 23 proposals have two or more scored human reviews, so the human comparison is exploratory; and the funding ranking was itself set by human review, which gives the human panel a built-in advantage. The claim we stand behind is the AI-side one: an AI panel cannot reproduce the funding decisions.

*Visual: Fig 4, the three-panel decision-outcome figure (mechanism → ranking → funding) → `results/figures/synthesis/rephrased/si_decision_outcome.png` (nb 04 `plot_decision_outcome`). The within-panel SD collapse and rank-vs-ceiling detail stay in SI (Table SI-3). Data: `.../decision_outcome_*.csv` and `score_decision_analysis.csv`.*

### §D — prompting for more variety does not restore it

#### Para D1 — persona changes wording, not ideas or judgments
**TS:** Persona conditioning, the strongest available prompt for variety, almost removes the difference in wording but leaves the difference in ideas and judgments unchanged.
- Under persona, AI proposal sets are no more varied in ideas than at baseline (richness 0.75 of human, p=.004).
- The difference in wording nearly disappears under persona (distinct-word ratio 1.04 to 1.07, versus 1.21 to 1.24 at one-at-a-time), while the differences in spread and richness of ideas remain. So personas change how the models write, not what they propose.
- On the review side, prompting for more variety makes the AI reviews of a proposal more similar to one another, not less (pooled δ from about −0.3 at baseline to about −0.9 at one-at-a-time).
- No prompting condition reaches human-level variety at either stage.

*Visual: the persona slope (green) in Fig 2 and Fig 4 (`fig_main_facet_slopegraph.png` shows all three conditions per facet). The across-condition trend also has a dedicated figure → `results/figures/synthesis/rephrased/fig6_condition_gradient.png` (condition gradient, pooled AI subsampled to n=23, nb 04). The wording-vs-idea contrast that carries this paragraph has its own SI figure → `results/figures/synthesis/rephrased/si_wording_vs_idea_gap.png` (nb 04 `plot_wording_vs_idea_gap`): one "AI ÷ human" axis on which the lexical-control line lifts to ~0.95 under persona while richness and spread stay at 0.68–0.75.*

#### Para D2 — all three models fall below humans, in no fixed order
**TS:** The three models differ in which measure they fall on, but all fall below humans, and no ranking among the models holds.
- The pre-specified order (Claude < Gemini < GPT < Human) does not hold at either stage; the human-to-AI difference is what drives the result, not differences among the models.
- Claude covers the human idea space fully but with more near-duplicate proposals; Gemini produces the narrowest proposal set and is the only model whose proposals sit slightly apart from the human region, yet its reviews are the least uniform at baseline; GPT is in between, with proposals closest to the human region.
- What we can state is that humans exceed every model.

*Visual: per-model tables to SI; main text states the null ordering in prose. Supporting figure that shows each model's position and that none orders cleanly → `results/figures/synthesis/rephrased/fig3_compression_map.png` (generation ratio on x, gate-keeping ratio on y, parity lines at 1.0, one marker per model×condition, nb 04). Per-model robustness grid for SI → `results/figures/synthesis/rephrased/fig4_robustness_grid.png` (facets × tasks, never collapsed).*

---

## DISCUSSION (600 to 800 words, 4 paragraphs)

### Para 1 — the two effects differ in kind
**TS:** AI narrows both the set of proposals produced and the way they are judged, but the two effects differ in kind and do not simply add.
- In generation, the effect is large: AI proposal sets hold 25 to 36 percent fewer distinct ideas than human sets.
- In review, the effect on the diversity of a panel is small, but it goes the same way for nearly every proposal, and at the level of specific points an AI panel raises about half of what a human panel would (SI-4).
- The two effects do not compound. Generation changes which proposals enter the pool; review changes how uniformly they are judged.
- Human reviewers of a proposal disagree, which is the reason a proposal is read by more than one person. AI reviewers agree, and this shows up in the decision itself: an AI panel cannot tell which proposals were funded (area under the ROC curve about 0.50 versus 0.77 for humans), and adding more AI reviewers does not help (Fig 4). Averaging more reviewers reduces error only if the reviewers make independent errors, and AI reviewers do not. Because the funding ranking was set by human review, we do not claim AI is less accurate than humans against an outside standard; we claim only that an AI panel does not reproduce the funding decisions.

### Para 2 — wording versus content
**TS:** AI also produces less varied wording, but the effect on ideas is separate from the effect on wording.
- AI text repeats its own phrasing more than human text does (distinct-word ratios 1.04 to 1.24; self-BLEU 0.21 to 0.35 versus 0.19 for humans).
- Persona conditioning removes most of the wording difference but none of the difference in ideas (§D). So the narrowing of ideas is not simply a matter of AI writing in a more uniform style.

### Para 3 — implications and what would and would not help
**TS:** Evaluating AI for science by the quality of individual proposals or reviews misses these effects, and the two stages would need different remedies.
- A benchmark that scores one proposal or one review at a time cannot detect a change in the range of proposals or judgments, because that range is a property of the set, not of any single item.
- Reducing the generation effect would require idea sources that differ from the models, not better prompting of one model.
- Reducing the review effect would require reviewers that judge independently; the same model queried many times does not.
- Persona conditioning does not reduce either effect.

### Para 4 — limitations
**TS:** Several limits bound these claims.
- The samples are small (23 per group), so per-model comparisons in generation are underpowered and the pooled comparisons carry the result.
- The generation effect on spread and richness at baseline is only visible after rewriting all text into one style, because per-model differences in writing style cancel in the raw text; the coverage and evenness effects hold on both raw and rewritten text.
- The review effects are small in absolute size, and the score analysis rests on the 13 proposals that have two or more scored human reviews.
- The results cover one funding competition, one proposal format, three models, and one point in time.

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
- **Facet measures.** Spread is mean pairwise distance; richness is the Vendi score (a similarity-sensitive effective number, the order-1 member of the Hill-number family); evenness is excess close-neighbor mass against a same-size null; coverage is support overlap against a human self-benchmark, with BERTopic regions and MeSH terms for domain coverage; displacement is MMD (with optimal transport as a cross-check). The Simpson diversity index is the order-2 member of the same family as richness and is reported explicitly in SI as a robustness check. Full estimators are in SI.
- **Inference.** Comparisons are at matched sample size. Unpaired proposal comparisons use label permutation; paired within-proposal review comparisons use the Wilcoxon signed-rank test; the ordering across models uses the Jonckheere-Terpstra test. Three comparisons were pre-designated primary (spread, richness, geometric coverage); all others are under Benjamini-Hochberg FDR control. The rephrased branch is primary, with the original branch as robustness.

---

## SI APPENDIX (PNAS Nexus uses one SI Appendix PDF; there is no in-line supplement section)

Route here, in this order. Figure paths are the rephrased branch unless the item is the original-branch comparison itself.
- **SI-1. Nearest-neighbour spacing and the per-group fringe correction.** For each proposal (and each review) we measure the distance to the nearest proposal from the other group, relative to how far apart proposals of the same group are (the 90th-percentile nearest-neighbour distance). By construction about 10 percent of proposals exceed this cutoff against their own group, so a value near 10 percent means "no more separated than same-group proposals are from each other." **Key correction (2026-08):** applied globally, this cutoff flags 18–26 percent of human proposals as having no AI nearby. But the proposals form two topical groups of very different internal density (k-means silhouette 0.68; not the two cohorts), and one cutoff over-flags the sparse group. Assessed within each group, the figure is about 9 percent (baseline; 9–13 percent across conditions), at the by-construction reference. Report both, and state plainly that AI does not leave a distinct region of human ideas unreached; the global number is an artifact of the two-group structure. Panels → `results/figures/synthesis/rephrased/si_interleaving_proposals.png`, `.../si_interleaving_reviews.png`, plus the per-group fringe figure (nb 04). Reviews show 0 percent human-only fringe in every condition. Referenced from §B1 and §C.
- **SI-geometry (UMAP — demoted; include only with a strong caveat, or drop).** `results/figures/synthesis/rephrased/si_generation_geometry_umap.png`. **The UMAP shows two apparently separated clusters that the statistics refute** (displacement MMD²≈0; AI is concentric with humans and populates both clusters; the split is topical, not cohort-driven). It invites exactly the "AI sits off to one side" misread the paper argues against, so it is **not** a good "spatial companion." Recommendation: drop it, or keep it only with a caption stating in bold that the separation is a projection artifact (Chari & Pachter 2023) and the clouds are concentric. The projection-free geometry (Fig 3 dumbbells + the radius / nearest-neighbor panels) is the honest substitute.
- **SI-2. Original-text branch.** Full facet battery on raw text, Tables SI-2a and SI-2b, and the three-pattern reading of style-robust, style-distorted, and style-only effects. Figures: the entire `results/figures/**/original/` tree, including `results/figures/synthesis/original/fig1_diversity_fingerprint.png` and the per-condition `results/figures/{condition}/{proposals,reviews}/original/` panels. This licenses the rephrased branch as primary and is itself a methodological result.
- **SI-3. Score-level decision analysis.** Table SI-3, the variance-collapse finding, and the human split-half ranking-ceiling bound (ρ ≈ 0.40) that contextualises §C3. Referenced from §C3 and Discussion Para 1; the outcome-level result is now main-text **Fig 4** (decision-outcome). Table source: `results/tables/cross_condition/reviews/score_decision_analysis.csv`.
- **SI-paired. Per-proposal gate-keeping panel.** The 23-line-per-panel detail behind Fig 2's gate-keeping column (spread, richness, coverage × three conditions) → `results/figures/synthesis/rephrased/fig_filtering_panel.png` (Fig. S_paired; `fig_filtering_panel()` in nb 04). Demoted from main because Fig 2's gate-keeping column already carries the pooled result.
- **SI-lexical. Wording gap vs idea gap.** The lexical robustness control (distinct-n, self-BLEU; spec §1.9) read against the semantic facets, showing persona closes wording toward parity while ideas stay at ~0.7–0.75. Figure → `results/figures/synthesis/rephrased/si_wording_vs_idea_gap.png` (nb 04); a raw-text companion exists at `.../original/si_wording_vs_idea_gap.png`. Referenced from §D Para D1 and Discussion Para 2. Caption must state wording is a control on style-normalized text, not a facet.
- **Decision-outcome analysis → main Fig 4** (not SI). Uses the competition's actual funding ranking / decision (all 23) as ground truth; AI panels at chance (AUC 0.47–0.50 vs 0.77), rank-agreement plateaus at ρ≈0.43. Code `src/decision_outcome.py`, nb 03 "Decision-outcome Analysis (SI)"; tables `.../decision_outcome_*.csv`. The manuscript should ground the argument in the diversity-prediction theorem / Condorcet independence / algorithmic-monoculture / premature-consensus literature.
- **SI-Simpson. Simpson diversity index (explicit).** The classic Simpson index reported two ways so a reviewer's expectation is met directly: (i) similarity-sensitive Simpson on the embedding (inverse Simpson = Vendi VS₂, Gini-Simpson = 1 − mean squared similarity), for proposals and reviews; (ii) classical categorical Simpson (Σpᵢ²) on the discrete BERTopic literature regions, for proposals. Both reproduce the richness narrowing (proposals inverse-Simpson AI/H 0.73–0.76; regions 0.62–0.78; reviews δ −0.39/−0.83/−0.74), and the categorical form adds diversity-across-literature-areas. Referenced from §A Para A1 and the model-ranking robustness. Figure → `results/figures/synthesis/rephrased/si_simpson_diversity.png` (nb 04; raw-text companion under `.../original/`); tables `results/tables/{condition}/{proposals,reviews}/{branch}/simpson_diversity.csv`; helpers `src/diversity_facets.simpson_similarity`/`simpson_categorical`, inference `src/diversity_inference.build_{proposal,review}_simpson_tests`. Caption must state Simpson is the order-2 relative of the richness facet, reported as a cross-check.
- **SI-4. Claim-level uniqueness.** Table SI-4 and the complementarity finding: at matched panel size, human and AI panels each leave 40 to 58 percent of the other's atomic claims unmatched; the full-15-review reservoir recovers more (human-unmatched drops to 16 to 32 percent). Referenced from §C2b and Discussion Para 1. Includes the calibrated-threshold method and the "unmatched ≠ substantively novel" caveat with the hand-coding protocol as the stated pre-publication step. Figure → `results/figures/synthesis/rephrased/si_claim_uniqueness.png` (nb 04); table source `results/tables/cross_condition/reviews/claim_uniqueness.csv` (+ `claim_uniqueness_examples.csv`); helpers in `src/claim_uniqueness.py`, code in nb 03 section "Claim-level Uniqueness (SI)". This is the cleanest rebuttal to "why not automate the panel," so it strengthens rather than qualifies the thesis.
- **Multi-facet fingerprint (demoted from main).** The z-score / sign-aligned-δ fingerprint across all facets and conditions, kept for readers who want the whole battery at a glance → `results/figures/synthesis/rephrased/fig1_diversity_fingerprint.png`. Replaced as the main multi-facet figure by the Fig 2 slopegraph grid (collaborator found the fingerprint hard to read).
- **Per-model tables and slopegraphs.** Full Tables 1a, 1b, 1c with every model cell and significance, from `results/tables/{condition}/{task}/rephrased/facet_diversity_tests.csv`; the per-model Human→AI slopegraphs (`fig2b_supplement_*`, `fig3_compression_map.png`) and the robustness grid `results/figures/synthesis/rephrased/fig4_robustness_grid.png`. Main-text Fig 2 shows pooled AI only; individual models live here.
- **Persona card construction.** Contents, matching to applicant profiles, and the leakage check. [TODO — no figure; text plus an example card.]
- **Metric definitions and nulls.** Full estimators, jackknife and subsampling intervals, kernel-sensitivity check, and the plain-language statistical notes. Per-facet scree/profile figures exist per condition (e.g. `.../richness_vendi_profile.png`).
- **Robustness.** Kernel sensitivity for richness; neighborhood-size stability for coverage at k = 2, 3, 5; the Gemini-baseline flagged cell and its qualitative check. Figure: `results/figures/synthesis/rephrased/fig4_robustness_grid.png`; convergence check `.../proposals/rephrased/_convergence/facet_convergence_heatmap.png`.

---

## FIGURE CAPTIONS (draft, PNAS style)

PNAS legends open with a result sentence, then label panels (*A*), (*B*), (*C*), then define n, error bars, test, and significance key. Italic *P*. Significance key throughout: **P* < 0.05, ***P* < 0.01, ****P* < 0.001; ns, not significant. Primary branch is the rephrased, style-normalized text unless noted.

**Fig. 1. Design of the two-stage comparison.** Twenty-three biomedical grant proposals from a confidential funding competition, and the expert reviews they received, are compared against proposals and reviews produced by three frontier models (Claude, Gemini, GPT). Each model drafts proposals from the call given to human applicants and reviews the same 23 human proposals under the criteria given to human reviewers, which holds the task environment fixed. Generation and review are each elicited under three conditions of increasing diversity pressure: baseline, one request returning the full set; one-at-a-time, each item from an independent call; and persona, each independent call conditioned on a distinct scientist persona matched to an applicant. All diversity measures are computed in a shared BioLinkBERT embedding space at matched sample size. → `results/figures/synthesis/fig1_design_schematic.png` (`src/fig1_design_schematic.py`)

**Fig. 2. AI narrows diversity at both stages, across facets and elicitation conditions.** Each panel connects the human value (left anchor) to the pooled-AI value (right); a downward slope means AI is less diverse. Rows are the four facets (spread, richness, evenness, coverage); the left column is generation (proposal sets) and the right column is gate-keeping (review panels). The human value is shared across conditions (the human proposals and reviews are fixed), so one anchor fans out to the three elicitation conditions (baseline, one-at-a-time, persona; colour). Generation annotations are the AI÷Human ratio (1.0 = parity); gate-keeping annotations are the paired Cliff's δ (AI − Human) across the 23 matched review panels (−1 = AI lower for every proposal). Evenness is plotted as −clumping so that, like the other rows, down = less diverse. Coverage is the one measure that rises on the gate-keeping side: each AI review is close to the human reviews, even though the AI reviews of a proposal resemble one another (which is why spread and richness fall). Pooled AI is subsampled to n = 23 from 69. Stars are *P*_raw for the pre-registered primaries (spread, richness, geometric coverage) and Benjamini-Hochberg *P*_fdr otherwise. Displacement is a directional check shown in Fig. 3. Original-text branch and the full multi-facet z-score fingerprint in *SI Appendix*. → `synthesis/rephrased/fig_main_facet_slopegraph.png`

**Fig. 3. AI proposals interleave with human proposals rather than occupying a separate region, and a stable human periphery is left unvisited.** Top row: for each of the 23 human proposals (rows, sorted by nearest AI), its distance to the nearest other human (red) and to the nearest AI (blue), computed in the full embedding space, with the AI distance taken as the median over the exported size-23 AI subsamples. For most human proposals the two distances are close, so AI proposals sit among the humans, not beside them. The dashed line is the human q90 nearest-neighbor yardstick; a human whose nearest AI falls beyond it is ringed as the human-only fringe, which holds 18 to 26% of human proposals and is largest under persona. Bottom row: geometric coverage, the fraction of the human idea region reached by AI, benchmarked against human split-half self-coverage (pooled AI reaches 0.81 to 0.86, below the benchmark at baseline and persona); and displacement between the human and AI clouds, measured as MMD² against a shuffle null, near zero in every condition (human split-half floor ≈ 0). n = 23 per group, pooled AI subsampled from 69. → `synthesis/rephrased/fig_generation_geometry.png`

**Fig. 4. An AI review panel cannot reproduce the actual funding decisions.** Ground truth is the competition's real funding ranking and fund-or-not decision for all 23 proposals. (*A*) Each dot is one proposal's mean review score, on the same 13–14 human-scored proposals for every group (box = median and quartiles, dashed line = mean); AI panels vary less across proposals than humans (between-proposal SD 0.31–0.44 vs 0.62) and their variation does not align with funding (filled = funded, open = not funded). (*B*) Rank agreement with the true funding ranking as a function of panel size: human review aggregates upward (Spearman ρ 0.62→0.99, error cancellation) while AI plateaus at ρ≈0.43 at every panel size and in every condition (AI n = 23; human n shrinks as panel size grows, annotated per point). (*C*) Funding discrimination, the area under the ROC curve for funded versus not from the full panel: AI sits at chance (0.47–0.50) in every condition while humans reach 0.77. The funding ranking was set by the human review process, so the human curve carries a built-in advantage; the load-bearing result is the AI side, that an AI panel cannot reproduce the decisions. n = 23 proposals (human scores on a 13–14 subset); exploratory. → `synthesis/rephrased/si_decision_outcome.png`

### Supporting and SI captions

**Fig. S_gradient. Variety of AI proposal sets across the three prompting conditions.** Each measure for pooled AI (subsampled to n = 23 from 69) at baseline, one-at-a-time, and persona, showing that no condition reaches human-level variety and that prompting for more variety does not close the difference in ideas. → `synthesis/rephrased/fig6_condition_gradient.png`

**Fig. S_map. Each model loses diversity, and no ordering among models holds.** Generation ratio (proposals, AI ÷ Human) on the x axis against gate-keeping ratio (reviews, AI ÷ Human) on the y axis, one marker per model and condition, with parity lines at 1.0. Every marker sits below or left of human parity, and the models do not fall in a consistent order. → `synthesis/rephrased/fig3_compression_map.png`

**Fig. S_robustness. Facets by task and model, never pooled.** Rows are facets, columns are generation and gate-keeping, with one series per model; every row reads up for more diverse. Ratio rows show AI ÷ Human against parity at 1; the evenness row is sign-aligned against its null at 0. → `synthesis/rephrased/fig4_robustness_grid.png`

**Fig. S_interleave. AI proposals are interleaved among human proposals, not set apart; the apparent human-only fringe is an artifact of two topical groups.** For each proposal, the distance to the nearest proposal from the other group is compared with same-group nearest-neighbour spacing (the 90th percentile of human-to-nearest-human distance); a value near 10% means no more separated than same-group proposals are. Applied to all proposals at once, 18 to 26% of human proposals fall beyond the cutoff, suggesting a human-only region. But the proposals form two topical groups of very different density (*C*); within each group the figure is about 9%, at the 10% reference, so no distinct human region is left unreached. Reviews show 0% human-only fringe in every condition. → `synthesis/rephrased/si_interleaving_proposals.png`, `si_interleaving_reviews.png`

**Fig. S_original. The facets on raw, unrephrased text.** Same all-facet slopegraph layout as Fig. 2, on the original-text branch. Coverage and evenness narrowing hold on both branches; the pooled baseline spread and richness effects require style normalization to detect, because opposing per-model style artifacts cancel on raw text. → `synthesis/original/fig_main_facet_slopegraph.png` (the z-score fingerprint on raw text, `synthesis/original/fig1_diversity_fingerprint.png`, is also available).

**Fig. S_paired. Given the same proposal, AI review panels are less varied than the human panel yet cover more of what the humans said** (per-proposal detail behind Fig 2's gate-keeping column). Rows are facets (spread, richness, geometric coverage), columns the three conditions; each faint line is one of the 23 target proposals from its human panel to its matched pooled-AI panel, large markers are per-condition medians. Spread and richness fall for nearly every proposal (pooled Cliff's δ −0.91 under one-at-a-time and −0.74 under persona; −1.0 for individual models); geometric coverage rises, each AI panel reaching 0.95–0.98 of the human review span against the human leave-one-out benchmark of 0.83. Together they show AI reviews that are individually broad but collectively interchangeable. → `synthesis/rephrased/fig_filtering_panel.png`

**Fig. S_recovery. Human-to-AI diversity does not recover across conditions at either stage.** Each panel connects the human value to the AI value, generation on top and gate-keeping below, across baseline, one-at-a-time, and persona. No line reaches parity in any condition; the wording gap closes under persona while the idea gap does not. Richness (Vendi VS₁) is shown; the other facets are in the all-facet slopegraph (Fig 2). Pooled AI subsampled to n = 23. → `synthesis/rephrased/fig2b_human_ai_slopegraph.png` (alternates: `fig2_double_compression_slopegraph.png`; per-model `fig3_compression_map.png`)

**Fig. S_wording. Persona conditioning closes the wording gap but not the idea gap.** On a single "AI ÷ human diversity" axis (parity = 1.0), the distinct-2gram lexical control (per model, open shapes, plus their mean) and the pooled semantic facets richness (Vendi VS₁, with its subsample interval) and spread, across the three conditions. Under persona the wording control reaches ~0.95 (Claude at parity, ns) while richness stays at 0.75 and spread at 0.68, both significantly below human. Wording is a lexical robustness control, not a facet; computed on the style-normalized branch, so it is a residual-wording result (on raw text persona wording falls only to its baseline level). → `synthesis/rephrased/si_wording_vs_idea_gap.png`

**Fig. S_simpson. The Simpson diversity index reproduces the richness narrowing at both stages.** (*A*) Proposals, similarity-sensitive Simpson (inverse Simpson = 1/Σλ² on the cosine-similarity eigenvalues, equal to the Vendi score at order 2): pooled AI (n = 23) holds fewer effective distinct proposals than humans in every condition (AI-to-human 0.73 to 0.76). (*B*) Proposals, classical categorical Simpson on the discrete literature region each proposal is nearest to (Σpᵢ²): AI spans fewer effective regions (0.62 to 0.78). (*C*) Reviews, similarity-sensitive Simpson within panels, paired Cliff's δ (AI − Human): AI panels are less diverse for nearly every proposal under structured elicitation (−0.83, −0.74). Higher effective number = more diverse; Simpson is the order-2 relative of the richness facet and is shown as a robustness cross-check. → `synthesis/rephrased/si_simpson_diversity.png`

**Fig. S_claim. At matched panel size, human and AI review panels each raise about half the specific claims the other does not.** Reviews are split into atomic claims (sentences of the strengths and weakness fields), embedded with the same encoder as the main analysis (BioLinkBERT-large, mean pooling). A claim is unmatched when its nearest claim in the other panel is farther than the median nearest-claim distance between two human reviewers of the same proposal (0.084 for strengths, 0.094 for weaknesses). (*A*) Human-unique and AI-unique unmatched rates at matched panel size (exact-n, spec §11.1), by condition and polarity; the paired bars are near-equal, so neither panel is a superset of the other. (*B*) The same human-unmatched rate against a matched AI panel versus the full 15-review reservoir, which recovers more of the human claims (16 to 32 percent unmatched). Descriptive; unmatched indexes non-overlap in expression and is not yet shown to be substantive non-overlap. → `synthesis/rephrased/si_claim_uniqueness.png`

---

## DISPLAY-ITEM BUDGET (4 main plus SI)

1. **Fig 1.** Design schematic: two stages, three models, three conditions, matched comparison. → `results/figures/synthesis/fig1_design_schematic.png` (`src/fig1_design_schematic.py`). Optional; fold into text if space is tight.
2. **Fig 2.** All-facet Human → pooled-AI slopegraph grid  (4 facets × 2 stages; conditions as colour). The multi-facet main figure — a downward slope = narrowing. Anchors §A, §C, §D. → `results/figures/synthesis/rephrased/fig_main_facet_slopegraph.png` (nb 04 `plot_facet_slopegraph_grid`). *Replaces the earlier z-score fingerprint per collaborator feedback (2026-08; the fingerprint was hard to read); the fingerprint moves to SI.*
3. **Fig 3.** Generation geometry: human cloud with the unreached fringe, coverage and displacement insets. Anchors §B. → `results/figures/synthesis/rephrased/fig_generation_geometry.png` (nb 04 `fig_generation_geometry`).
4. **Fig 4.** Decision-outcome: can an AI panel reproduce the actual funding decisions? Three panels — mechanism (AI scores vary less across proposals), ranking (AI plateaus, humans aggregate), funding (AI at chance). Anchors §C3 and Discussion Para 1. → `results/figures/synthesis/rephrased/si_decision_outcome.png` (nb 04 `plot_decision_outcome`).

Each of the four main figures now carries a distinct message — design · narrowing-omnibus · generation-geometry · gate-keeping-consequence — with no doubling. Moved to SI to avoid redundancy: the per-proposal gate-keeping paired panel (`fig_filtering_panel.png`, Fig. S_paired — Fig 2's gate-keeping column already carries the pooled result); the stand-alone richness recovery slopegraph (`fig2b_human_ai_slopegraph.png` / `fig2_double_compression_slopegraph.png`, Fig. S_recovery); and the per-model compression map (`fig3_compression_map.png`). If four is the hard cap, fold the design schematic (Fig 1) into text. **Note the tradeoff on Fig 4:** it is exploratory (n = 23, and the funding ranking was set by the human process), so the caption keeps the load-bearing claim AI-side ("AI cannot reproduce the decisions"); if a reviewer objects to an exploratory main figure, the fallback is to swap it back to SI and restore the paired panel as Fig 4.

**Fig 3 resolved (2026-07-26; UMAP demoted 2026-08):** the canonical Fig 3 is the projection-free interleaving view (`fig_generation_geometry.png`), which shows "AI interleaves with humans, not beside them" without the UMAP's misleading separation. The UMAP composite (`si_generation_geometry_umap.png`) is **demoted** — it implies a separation the statistics refute (displacement ≈ 0; concentric clouds; topical not cohort clusters) and invites the "AI off to one side" misread. Drop it, or keep it only with a bold projection-artifact caveat; use the projection-free radius / nearest-neighbor panels instead.

---

## OPEN ITEMS BEFORE DRAFTING PROSE
- Verify the persona-collapse and De Freitas citations (flagged MEDIUM in draft2).
- Confirm what can be named about the funding program; write the data-availability statement.
- Fill the AlphaFold, AI-generates-ideas, and AI-reviews citation slots.
- Decide C3 placement (recommend SI with one main-text sentence).
- Decide the title.
- SI-4 hand-coding: code a sample of unmatched claims as substantively-novel vs restatement-in-different-words (ideally two coders + a reliability statistic) before the claim-level rates are stated as content non-overlap rather than expression non-overlap. Until done, keep §C2b and the abstract wording at "expression," not "substance."
- Confirm the un-auditable Methods values against the generation/prep configs: sampling temperature (0.9), total human-review count (the `[NUM total]` slot), and the PubMed corpus span.
