# Figure Build Specification

### Figures 1–4 for *Double compression: AI narrows both the generation and the gatekeeping of scientific ideas*

**One caveat before you start.** I have not seen your rendered figures — only the audit's textual descriptions of them. Where I say an asset "already is" a panel, that judgment comes from the audit's own description of what the file draws. Open each one and confirm before treating it as done.

---

# 0. Resolve these three things first

These affect what you draw, so settle them before opening a plotting script.

### ⚠ FLAG 1 — Your two fringe statistics disagree about which condition is worst

| Source | baseline | one-at-a-time | persona |
|---|---|---|---|
| SI-1 table (`facet_interleaving.csv`) | 22% | 18% | **26%** |
| `fig_generation_geometry.png`, per §2.7 | **26%** | 17% | 22% |

Same three numbers, opposite condition assignment. The one-at-a-time values differ by a single point (18 vs 17), which is consistent with the two using genuinely different rules — SI-1 uses a 90th-percentile human-spacing yardstick, the figure uses a majority-of-subsamples rule. But baseline and persona landing exactly on each other's values looks like a transposition in one of the two write-ups.

**Why this blocks Fig. 3*B* (the asymmetry inset).** The Results text says the fringe is *"widest under persona (26%)"* — argumentative, because the strongest available fix makes the periphery worse. If baseline is actually 26%, that sentence is wrong and the panel contradicts the paragraph beside it.

**Resolution (2026-08-30).** The two statistics are two aggregations of the same q90 rule. The **mean miss-probability** (average over subsamples of "nearest AI > yardstick") gives **23 / 18 / 26** across baseline / one-at-a-time / persona — persona widest — matching SI-1 (22 / 18 / 26) and the Results sentence "widest under persona (26%)." The **majority-of-subsamples** rule gives 26 / 17 / 22 and is the odd one out. **Standardize the Fig 3*B* asymmetry inset and the core-vs-edge miss-rate on the mean-probability rule** so the figure and the text agree; the core→edge gradient (ρ = +0.86, tertiles 0 / 4 / 69%) is unaffected by the choice.

### ⚠ FLAG 2 — The audit contradicts itself on the geometry, and Fig. 3 has to pick a side

§2.7 (rewritten in August): *"AI is concentric with and interleaved among the human cloud (same center, same radial extent)… This is **not** strict containment (AI is not a smaller region inside)."*

§4.1 (not updated): *"AI occupies a smaller region **inside** the human territory."*

**Update (2026-08-30).** Displacement is no longer a Fig. 3 panel (it is reported in the text), so the misread-prone projection is gone — but the *wording* still has to pick a side. Follow §2.7: AI is **concentric with and interleaved among** the human cloud (same center, same radial extent), filled unevenly, **not** a smaller region strictly inside it. The core-vs-edge result (§2.10) reinforces exactly this: same center, uneven filling, distinctive edges under-reproduced. §4.1 of the audit still needs correcting to match.

### ⚠ FLAG 3 — Dimensionality is out of the paper entirely

No panel, no axis, no row in any grid. It stays in the SI only as one of the six pre-registered primaries. If you reuse `facet_fingerprint.png` or the filtering panel as a base, strip the dimensionality rows rather than leaving them greyed.

---

# 1. Conventions that apply to every panel

**Two identities, fixed forever.** Human and AI. Assign each a hue in Fig. 1 and never reassign it, in any panel, under any filter. This is the single most load-bearing color decision in the paper because the pair appears in all four figures.

**The three models are not three more identities.** Render Claude, Gemini, and GPT as three steps of the *AI* hue — light, mid, dark — not as three new categorical colors. Reasons: it keeps the human/AI contrast legible when models are also on the plot; it avoids seating a fourth categorical hue, where colorblind separation starts to strain; and it correctly signals that "model" is a sub-level of "AI" rather than a peer of "human."

**Validate the human/AI pair rather than eyeballing it.** Check separation under deuteranopia and protanopia at the size it will print. If your figure template already fixes these hues, validate them anyway — this pair carries identity in every panel.

**Diverging color appears exactly once.** Fig. 2*C* is the only signed-about-zero quantity in the paper. It gets two opposed hues (one warm, one cool) with a neutral **gray** midpoint. Nowhere else. Ratios around 1.0 are magnitudes against a benchmark, not polarities — do not give them a diverging ramp.

**Reference lines are furniture.** Parity at 1.0, chance at 0.5, zero excess, the 0.83 human self-benchmark, the ~10% fringe reference. All dashed, recessive gray, behind the marks, labeled once per figure rather than once per panel.

**Text never wears the series color.** Values, tick labels, and annotations in neutral ink; a small colored marker beside a label carries identity. This matters most in Fig. 3*C* and Fig. 4*A*, where 23 rows of two-hue labels would be unreadable.

**Uncertainty is not decoration.** Jackknife intervals on the generation ratios, bootstrap intervals on the AUCs. Fig. 4*C* (funding AUC) without intervals would assert precisely the human-versus-AI gap the audit withdrew.

**Never put two scales on one axis.** Two measures that cannot share a base become two panels or small multiples.

**Sizing.** All text between 6 pt and 12 pt at final size. Single column ≈ 8.7 cm, full width ≈ 17.8 cm. RGB.

**Direction rule, and the two panels that fight it.** Your spec requires every panel to read *up or right = more diverse*. Two exceptions need an explicit decision, stated in the legend:

- **Fig. 2*B*** (evenness) — positive close-neighbor excess means clumping, i.e. *less* diverse. Either invert the axis or label the poles in words ("more evenly spaced than chance" / "more clumped than chance").
- **Fig. 4*B* coverage rows** — positive δ means the AI panel covers more of the human review span, which the paper argues is a *deficit* (the central blanket), not a strength. Do not let the direction rule imply AI wins here. Label the axis "AI panel covers more of the human span →" and let the text carry the interpretation.

**Never appears in any figure:** dimensionality; the raw/`original` branch as a primary series (SI only); model-ranking annotations, since the trend test failed and the audit declines to rank; significance stars without the underlying value; anything read from `…/{branch}/facet/`, which is a stale directory the current notebooks do not rewrite.

---

# 2. Asset inventory

| Panel | Status | Existing asset |
|---|---|---|
| Fig. 1 | **Build new** | none |
| Fig. 2*A* (spread+richness merged) | **Built** | `production_figures.py::_draw_spread_richness` |
| Fig. 2*B* (evenness) | **Built** | `production_figures.py::_draw_evenness` |
| Fig. 2*C* (wording) | **Built** | `production_figures.py::_draw_wording` (from `si_wording_vs_idea_gap`) |
| ~~Near-duplicate curve~~ | **Removed from main fig** | builder `_draw_nnduplicate` retained for optional SI |
| Fig. 3*A* | **Wired** | `src/figure3_regions.py` (nb 04) → `fig3_regions.png` |
| Fig. 3*B* | **Wired** | `src/core_edge_analysis.py` (nb 04) → `fig3_core_edge.png` + `core_edge_{branch}.csv` |
| Fig. 4*A* (box+jitter) | **Built** | `production_figures.py::_draw_within_box` |
| Fig. 4*B* | **Built** | `production_figures.py::_draw_field` |
| Fig. 4*C* | **Nearly done** | `si_decision_outcome.png` panel C (funding AUC) |
| SI (not in Fig 4) | **Nearly done** | `si_decision_outcome.png` panel B (rank aggregation) |
| SI-4 (not in Fig 4) | **Nearly done** | `si_claim_uniqueness.png` |

Most panels exist in some form. Fig. 3's two panels are build-new but both have validated prototypes (Panel A reproduces the audit's Simpson values; Panel B is the new core-vs-edge analysis, §2.10). Elsewhere the work is re-cutting to one visual grammar and writing annotations, not new analysis.

---

# FIGURE 1 — Design

**Status:** build new. Draw it **last**, once Figs. 2–4 are final, so its color vocabulary matches theirs.

**Not a chart.** A flow diagram. Its job is to make "the task environment was held fixed" visible rather than merely asserted, and to put the study's scale in front of the reader once.

**Layout — three horizontal bands, full column width.**

*Top band, inputs.* Draw the call text once and the review criteria once, each as a single labeled block, with arrows fanning to both the human and the AI lane. Drawing them once is the entire rhetorical point; two copies would undercut the claim.

*Middle band, generation.* Human lane: 23 proposal glyphs, marked as two applicant cohorts. AI lane: 3 models × 3 conditions, each producing 23. Gloss each condition in one line — single request / independent calls / independent calls plus persona.

*Bottom band, gate-keeping.* The 23 human proposals feed a human panel (85 reviews, 2–5 per proposal) and an AI panel (345 reviews, 5 per model per proposal). Draw a bracket showing the comparison is paired *within proposal* at matched panel size — this is the design feature reviewers most often miss.

*Right margin, analysis path.* A narrow vertical strip: rewrite to neutral style → embed (BioLinkBERT-large, 1,024-d, cosine) → four facets + displacement.

**Numbers that must appear on the diagram:** 23 proposals, two cohorts, 85 human reviews, 345 AI reviews, 5 AI reviews per model per proposal, 3 conditions. (The 12 literature regions now live in Fig. 3A, so they are optional on this schematic.)

**Do NOT include:** results of any kind; the two text branches as parallel pipelines (mention the raw branch as a single side note, or the diagram becomes about methods bookkeeping); icons for the specific commercial models; dimensionality in the facet list.

---

# FIGURE 2 — Generation narrowing

**Two-column width, three panels (revised 2026-08-30).** Spread and richness are **merged into one panel 2A** (they are small multiples of the same ratio comparison and read better sharing an axis); evenness becomes **2B**; wording-vs-ideas becomes **2C**. The **near-duplicate curve panel was removed** by author decision — the same "AI clumps into near-twins" message is carried by the evenness panel (2B) and by one text statistic (35% of human proposals have a near-twin vs >80% of Claude's baseline); the `_draw_nnduplicate` builder is retained for optional SI use. Suggested arrangement: *A* spanning the top row, *B* and *C* side by side beneath.

## Panel 2A — Spread and richness (merged)

**Status:** built. `src/production_figures.py::_draw_spread_richness`.

**Question:** are AI proposal sets less spread out *and* less rich than human sets, and by how much?

**Chart type:** dot-and-interval plot (horizontal), two facets overlaid per condition — spread and richness as two blue hues.

**Data:** `results/tables/{condition}/proposals/rephrased/facet_diversity_tests.csv`. Spread facet, metric `mean_pairwise`, pooled 0.70 / 0.64 / 0.68. Richness facet, Vendi at *q* = 1, pooled 0.74 / 0.66 / 0.75. Pooled-AI rows only (one marker per facet per condition; **no per-model open markers** — they were removed in the merge to keep the panel legible).

**Axes:** *y* = the three conditions, ordered baseline → one-at-a-time → persona top to bottom (keep this order in every panel of every figure). *x* = AI ÷ human diversity, range roughly 0.35 to 1.15, with a dashed parity line at 1.0.

**Encoding:** two blue hues — dark = spread (mean pairwise), light = richness (Vendi) — each a filled dot with its jackknife 95% interval, offset vertically within the condition row so they do not overplot. A two-entry legend identifies the hues. Human is the parity line, not a series.

**Annotate:** the ratio value beside each marker; a "human parity" label at the dashed line. *P* values live in the text, not on the markers (0.010 / <0.001 / 0.003 for spread; 0.005 / <0.001 / 0.004 for richness).

**Simpson placement (reconciled with draft):** the draft reports the embedding Simpson (inverse-Simpson = Vendi VS₂, ratios 0.76 / 0.73 / 0.76) in **SI-5**, not on this panel. The *categorical* region Simpson is a different quantity and lives in Fig. 3A.

**Do NOT:** color markers darker where the ratio is larger — that double-encodes length as hue; split spread and richness back into two panels; report the absolute Vendi values (3.15 human, 2.09–2.37 AI) anywhere on the figure (the audit is explicit that only the ratio is meaningful on dense embeddings); omit the parity line, without which a ratio plot has no meaning.

## Panel 2B — Evenness

**Status:** build new.

**Question:** does AI pile up near-duplicates rather than spacing ideas out?

**Chart type:** diverging bar centered on zero. The only diverging panel in the paper.

**Data:** same file, evenness facet, metric `ripley_excess`. Human: −0.141 / −0.234 / −0.115. Pooled AI: +0.077 / +0.142 / +0.062.

**Axes:** *y* = the three conditions. *x* = close-neighbor excess relative to a same-size chance draw, symmetric about zero, roughly −0.28 to +0.20.

**Encoding:** two opposed hues, neutral gray zero line. Human bars extend one way, AI the other.

**Annotate:** label the two directions in words at the axis ends — "more evenly spaced than chance" and "more clumped than chance." Numbers alone will be misread. *P* = 0.001 throughout.

**Do NOT:** place a hue at the zero midpoint — it must read as "nothing"; use two cool hues as the poles, which do not read as opposites; put human and AI on separate axes or separate panels, since the whole point is that they fall on opposite sides of the same zero; compare excess values *across* conditions — the chance benchmark is condition-specific by construction and the audit forbids it.

## (Removed) Near-duplicate curve — moved out of Figure 2

**Status:** **removed from the main figure (2026-08-30, author decision).** The cumulative near-duplicate curve read as confusing and duplicated the evenness message. The `_draw_nnduplicate` builder in `src/production_figures.py` is retained for optional SI use (three lines — human, pooled AI, Claude-at-baseline; vertical guide at the 35%-human threshold, crossings labeled 35% human / >80% Claude baseline). The finding survives in the draft as one text statistic in the Evenness paragraph. Build it only if a reviewer asks for the curve inline.

## Panel 2C — Wording against ideas

**Status:** **`si_wording_vs_idea_gap.png` already is this panel.** The audit describes it as "one 'AI ÷ human' axis on which the wording line rises to ~0.95 under persona while richness and spread stay at 0.68–0.75." That is exactly the specification below.

**What needs to change:** recolor to the paper's two-identity scheme; confirm the orientation fix below was actually applied rather than assumed; add direct labels at the right edge if it currently uses a legend box; confirm the condition order matches the other panels.

**Question:** does prompting for diversity change what the models propose, or only how they write?

**Chart type:** slopegraph across three conditions.

**Data:** `facet_diversity_tests.csv` — `lexical_control` rows for the wording series, spread and richness facet rows for the idea series.

**Axes:** *x* = the three conditions in the standard order. *y* = AI ÷ human ratio, one shared axis, parity line at 1.0.

**⚠ Orientation trap.** The lexical measure is tabulated as **human ÷ AI** (1.07–1.14 / 1.21–1.24 / 1.04–1.07) while every facet is **AI ÷ human**. Plotted as tabulated, the two lines appear to move in opposite directions when they do not. Invert the lexical values first: ≈0.88–0.93 baseline, ≈0.81–0.83 one-at-a-time, ≈0.93–0.96 persona. The audit's description of the existing figure ("rises to ~0.95 under persona") suggests the inversion was applied there — verify rather than assume.

**Annotate:** direct-label both lines at the right edge. Two labeled series need no legend box.

**Do NOT:** put wording and ideas on two y-axes — this is the single most tempting dual-axis in the paper and it would invent a relationship the data do not contain; add self-BLEU to this panel, since it runs the opposite direction (higher = more repetitive) and belongs in the SI; add a third and fourth line for spread and richness separately if they overlap — show one idea line with a band, or pick richness.

---

# FIGURE 3 — Same territory, thinner at the distinctive edges

**Two panels, redesigned 2026-08-30.** Panel A (setup) shows AI works the same biomedical territory as humans but occupies it less evenly; Panel B (payoff) shows the ideas AI fails to reproduce are specifically the distinctive, sparsely-populated ones, regardless of quality. Suggested layout, two-column width: A on the left (~40%), B on the right (~60%) with its scatter dominant and two small companions (tertile, asymmetry) stacked at its right.

**Displacement is dropped from the figure and reported in the text only.** The 2-D projection was the paper's most-misread panel (it shows an apparent group separation the statistics deny), and the "not displaced" result reads better as one sentence: *the two clouds are statistically indistinguishable (MMD² = 0.032–0.062, all ns, against a human split-half floor ≈ 0); AI is concentric with the human cloud, not beside it.* The old MeSH accumulation curve and the set-level region touch-count (5–8 of 12) also leave the figure; the set-level number goes in the Fig 3 caption, the MeSH accumulation to SI.

**Retired builders kept as SI alternates.** The earlier per-proposal fringe dumbbell (`fig_generation_geometry.png`) and the MDS/UMAP projection (`si_generation_geometry_umap.png`) are no longer the main Figure 3 assets; nb 04 still generates them, but they are SI alternates only. Their majority-of-subsamples fringe numbers (26/17/22, baseline widest) are **superseded** by the mean-probability rule used in Panel 3B and the audit (23/18/26, persona widest, consistent with SI-1).

## Panel 3A — Same territory, occupied less evenly

**Status:** wired into the pipeline. `src/figure3_regions.py::build_panel_a`, called from `notebooks/04_synthesis.ipynb` per branch; output `results/figures/synthesis/{branch}/fig3_regions.png`. Reproduces the audit's SI-5 categorical Simpson values (human 4.94; pooled AI 3.85 / 3.06 / 3.60). Re-cut to final sizing/hues remains.

**Question:** does AI engage the same areas of the biomedical literature as humans, and does it occupy them as evenly?

**Chart type:** box-plus-jitter, one AI box per condition with the human set as a fixed reference marker and line.

**The measure — effective number of regions, not a raw count.** Per-proposal region *counts* do not discriminate (human and AI proposals each engage ~2 of 12 regions; a raw-count box plot is flat and useless — I checked). Use the **categorical inverse-Simpson effective number of regions**: assign each proposal to the single literature region it sits nearest to (BERTopic; drop the outlier bin −1), take pᵢ = the fraction of a set in region i, report 1/Σpᵢ². This is "how evenly the set spreads across regions" and is exactly the audit's SI-5 categorical Simpson.

**Matched-N sampling — follow the audit convention exactly.** Human is the full 23-proposal set → one fixed value, **4.94** effective regions; draw it as a diamond marker per condition plus a horizontal dashed reference line (identical across conditions because the human set is fixed). AI is subsampled **to n = 23, 1000× without replacement** from the 69 (the cached `subsample_idx_ai_n23_seed42.npy`) → a distribution; draw it as a box (median + IQR + whiskers) with a thinned jitter (~120 of the 1000 draws) behind it. Do **not** bootstrap the human set with replacement — the audit forbids it (duplicates corrupt diversity metrics); human stays a point because at matched N it *is* the population.

**Data:** region labels `data/prepared/literature/lit_bertopic_assignments.csv` (`bertopic_topic`, 12 regions 0–11, outlier −1, `article_idx` = row index); nearest-neighbor indices `data/prepared/{condition}/proposals/rephrased/proposal_to_literature_knn.npz` (`neighbor_idx[:,0]` = nearest literature article, aligns row-for-row with `proposal_master.csv`); group labels from `proposal_master.csv`; AI subsample indices `subsample_idx_ai_n23_seed42.npy`. Cross-check every value against `simpson_diversity.csv` (`metric = inverse_simpson`, `param = literature_region`): human **4.94**; pooled AI **3.85 / 3.06 / 3.60**; ratio AI÷H **0.78 / 0.62 / 0.73**; pooled p 0.021 / … (recompute per condition). Reproduction matches to two decimals.

**Axes:** *y* = effective number of regions occupied (inverse Simpson, of 12), roughly 1.5–5.6, up = spread across more regions. *x* = the three conditions in the standard order.

**Encoding:** AI box + jitter in the AI hue; human diamond + dashed line in the human hue. The human line sitting above every AI box is the whole message — build it to read at a glance. One-at-a-time is the strongest concentration (AI median 3.1); worth a word since it is where structured elicitation bites hardest.

**Annotate:** the human value (4.94) on its line; the AI÷H ratios (0.78 / 0.62 / 0.73); a one-line gloss "same regions touched, occupied less evenly."

**Do NOT:** use the raw per-proposal region count (flat, ~2 for both groups); give human a box (it is the full population at matched N, not a sample); bootstrap human with replacement; use 12 colors for 12 regions; add the MeSH accumulation or set-level touch-count to this panel (caption/SI).

## Panel 3B — AI reproduces the core, thins the distinctive edges

**Status:** wired into the pipeline. `src/core_edge_analysis.py::build_panel_b`, called from `notebooks/04_synthesis.ipynb` per branch; outputs `results/figures/synthesis/{branch}/fig3_core_edge.png` and the table `results/tables/synthesis/core_edge_{branch}.csv`. New analysis, audit §2.10. The asymmetry inset uses the mean-probability rule (FLAG 1 resolution). Re-cut to final sizing/hues remains.

**Question:** are the human ideas AI fails to reproduce a random fifth, or specifically the distinctive, sparsely-populated ones?

**Chart type:** a composite — one main scatter (large) with two small companions (tertile bars, asymmetry bars) stacked to its right.

**B main — the core→edge gradient.** Scatter, one point per human proposal (n = 23). *x* = peripherality = distance from the centroid of human idea space (human-to-human geometry only). *y* = miss-rate = the share of equal-sized (n = 23) AI pools, across conditions and subsamples, whose nearest proposal to that human idea exceeds the human q90 nearest-neighbor yardstick. Encode miss-rate as a **sequential** ramp (steps of the AI hue) — **not** the diverging palette (reserved for the evenness panel, Fig 2B). Dashed fit line; annotate **Spearman ρ = +0.86, p < 0.001, n = 23**. Direct-label the two ends ("core ideas: always reproduced" near the origin; "distinctive edge ideas: often missed" near top-right). *Direction-rule exception:* up = more missed = less covered — label it in words ("% of equal-sized AI pools that MISS it →"); do not let "up" read as good.

**B tertile inset.** Three bars, humans split into local-density tertiles core / middle / edge, height = mean miss-rate: **0% / 4% / 69%**. The headline number; keep it small and adjacent.

**B asymmetry inset.** Paired bars per condition — human ideas with no AI counterpart vs AI ideas with no human counterpart — with the ~10% by-construction reference as a dashed line. Human-only **18–26%** vs AI-only **4–9%**. This one uses the human/AI **identity hues** (here it genuinely is a human-vs-AI comparison). **Title it accurately** — "humans leave more uncovered ground than AI (AI near chance)"; **never** "only humans hold uncovered ground" (false — 4–9% of AI proposals have no human counterpart).

**Data:** `results/tables/synthesis/core_edge_{branch}.csv` (per-human `centroid_dist`, `local_density`, `miss_rate_mean`, `is_funded_human`, `ranking`); the asymmetry recomputed from the pairwise matrices + `subsample_idx_ai_n23_seed42.npy`.

**Quality guard — in the caption, not a panel.** The ideas AI misses are unrelated to the competition's funding/ranking (funded vs rejected miss-rate 0.20 vs 0.26, Mann–Whitney p = .77; all p > 0.3; the one directional wiggle flips between text branches). One caption sentence forecloses the "AI only misses the ideas humans rejected" deflation.

**Do NOT:** use the diverging palette for the scatter; let the direction rule imply high miss-rate is good; title the asymmetry inset "only humans"; claim the edge is a large population (n = 23, one dense core plus a modest number of distinctive outliers — report ρ with the n); read fringe numbers from a rule that disagrees with the text (see FLAG 1).

---

# FIGURE 4 — Gate-keeping convergence

Two-column width, three panels: **A** (within-panel convergence — box + jitter of within-panel distance for the human panel and the three AI conditions), **B** (field split), **C** (funding discrimination). **Two analyses were moved out of Figure 4 (2026-08-30):** claim-level uniqueness (it measures complementarity, not convergence, and is provisional pending a hand-coding pass) and rank aggregation (removed from the main figure by author decision — note the audit still considers rank the sturdier half of the decision finding, so it stays in SI). Both specs are retained below under "SI figure" headings.

## Panel 4A — Within-panel convergence

**Status:** built. `src/production_figures.py::_draw_within_box`. (Revised 2026-08-30: the earlier 23-row dumbbell overlay was too dense to read; replaced with a box + jitter across four groups.)

**Question:** for a given proposal, do the AI reviewers say more similar things than the human reviewers?

**Chart type:** box + jittered points, one box per group (human panel, AI baseline, AI one-at-a-time, AI persona). Box = median + IQR + whiskers; dots = the 23 proposals; a black marker to the right of each box = mean ± SD.

**Data:** `results/tables/{condition}/reviews/rephrased/facet_review_paired_long.csv`, spread facet, metric `mean_pairwise`, `field = whole`, `comparison = human_vs_pooled_ai`. Human within-panel mean ≈ 0.044 (fixed across conditions); pooled AI 0.032–0.040. P and δ per condition come from `facet_diversity_tests.csv` (`p_raw`, `effect_size`): baseline δ = −0.39, P = 0.07 (ns); one-at-a-time δ = −0.91, P < 0.001; persona δ = −0.74, P < 0.001.

**Axes:** *y* = within-panel mean distance, roughly 0.025 to 0.065, up = reviewers disagree more. *x* = four groups (human, then the three AI conditions in standard order).

**Encoding:** human box in the human hue (crimson); the three AI boxes in the three AI-hue steps. The tall human box beside the short AI boxes is the message — build it to read at a glance.

**Annotate:** above each AI box, the paired Wilcoxon *P* vs human and Cliff's δ (P = 0.07 (ns), δ = −0.39 / P < 0.001, δ = −0.91 / P < 0.001, δ = −0.74). Mean ± SD label beside each black marker. A legend giving the box/dot/marker semantics.

**Note on pairing:** the comparison is paired within proposal (that is where the Cliff's δ and Wilcoxon P come from); the box + jitter shows the group distributions for legibility, and the paired statistics are annotated so nothing quantitative is lost. Panel 4B carries the same paired δ decomposed by field.

**Do NOT:** revert to the 23-row dumbbell (too dense); drop the P/δ annotations (they are what make the boxes a paired test rather than four unpaired distributions); bootstrap the human group (it is fixed at matched N).

## Panel 4B — Where the compression lives

**Status:** recut from `fig_filtering_panel`, adding the field axis.

**Question:** is the compression in the praise or in the criticism?

**Chart type:** dot plot with a zero reference line.

**Data:** same file, `field` column ∈ {whole, strengths, weakness}. Spread and richness rows.

**Axes:** *y* = three conditions. *x* = Cliff's δ, −1 to +1, dashed zero line.

**Encoding:** three series by field — three is comfortable, but direct-label them anyway. Weakness pinned at −0.91 while strengths sits at −0.57 to −0.65 is the message.

**Annotate:** an adjacent strip showing human within-panel absolute spread by field — 0.044 whole, 0.069 strengths, 0.084 weakness. Half the argument is that the compression is largest exactly where human panels vary most, and the δ values alone do not show that.

**Do NOT:** include dimensionality rows; use a rainbow heatmap for the field × condition grid; let the direction rule imply that positive coverage δ is good — see the convention above; present the fields as independent replications, since they are a decomposition of the same 23 paired comparisons.

## SI-4 figure — Unmatched claims (moved out of main Figure 4)

**Status:** SI only (not a main-figure panel). **`si_claim_uniqueness.png` already is this figure.** Build it with the SI figures, not with Figure 4. The spec below still applies to the SI figure.

**What needs to change:** confirm both `matching` values appear — the audit is explicit that reporting only one overstates or understates AI coverage by 10–24 points. If the existing figure shows only `exact_n`, add the reservoir rate.

**Question:** if an AI panel replaced a human panel, which specific points would go unsaid?

**Chart type:** mirrored horizontal bars, human-unmatched extending left and AI-unmatched right from a shared center.

**Data:** `cross_condition/reviews/claim_uniqueness.csv`, column `matching` distinguishing `exact_n` from `full_ai_reservoir`. Human-unmatched 40–58%, AI-unmatched 41–58%, reservoir 16–32%.

**Axes:** *y* = condition × polarity (six rows: three conditions × strengths/weaknesses). *x* = share of claims unmatched, mirrored, 0 to 60% each way.

**Encoding:** human and AI identity hues, one per side. Overlay the full-reservoir rate as an open marker on each human bar.

**Annotate:** the near-symmetry is the finding — a short note that neither panel contains the other. Weaknesses overlap more than strengths (40–50% vs 50–58%).

**Do NOT:** stack the two rates as parts of a whole — they are not complementary shares and stacking would imply they sum to something meaningful; show only the matched-panel number; use this panel to claim substantive complementarity, which the hand-coding pass has not yet established.

## Panel 4C — Funding discrimination

**Status:** **`si_decision_outcome.png` panel C already is this**, with the intervals added in the August re-audit.

**What needs to change:** confirm the matched variants appear alongside the headline AUC, not only in a table. The robustness of the AI null across matching is what makes the claim defensible.

**Question:** can a panel's scores tell which proposals were funded?

**Chart type:** forest plot (dot and interval).

**Data:** `decision_outcome_summary.csv` and `decision_outcome_matched_auc.csv`.

**Axes:** *y* = human panel, then pooled AI × three conditions, then the matched variants B and C. *x* = AUC, 0 to 1, dashed chance line at 0.5.

**Encoding:** point estimates with stratified bootstrap 95% intervals. Human 0.77 [0.48, 1.00]; AI 0.50 [0.25, 0.75], 0.47 [0.22, 0.72], 0.50 [0.25, 0.76]; matched C 0.50, 0.45, 0.50 with intervals near ±0.35.

**Annotate:** label-permutation *P* values (0.99 / 0.84 / 0.99, human 0.089). The overlap between the human interval and every AI interval must be visually obvious — build the panel to show it rather than to imply a gap.

**Do NOT — this panel has the most ways to go wrong:** omit the intervals; draw a bracket, connector, or significance annotation between the human row and any AI row, which would assert the comparison the audit explicitly withdrew; put a star on the human row, whose *P* is 0.089; sort rows so the human sits visually apart from the AI rows as a contrast; crop the *x* axis to make the intervals look tighter.

## SI figure — Rank aggregation (moved out of main Figure 4)

**Status:** SI only (not a main-figure panel), 2026-08-30. **`si_decision_outcome.png` panel B already is this.** Build it with the SI figures. The audit still considers rank the sturdier half of the decision finding, so keep it in SI; the spec below applies to the SI figure. The human curve must be drawn only to *k* = 4 with the remainder shaded.

**What needs to change:** confirm the human curve is drawn as a truncated segment ending at *k* = 4 with the unavailable region shaded. If it runs to *k* = 15 by extrapolation, that is a serious problem — the audit notes the human curve's high-*k* points already rest on about six proposals.

**Question:** does adding reviewers help? The audit calls this the sturdier half of the decision finding.

**Chart type:** line chart.

**Data:** `decision_outcome_curves.csv`, the rank-agreement-versus-*k* series.

**Axes:** *x* = number of reviewers, 1 to 15. *y* = Spearman ρ with the competition's ranking, 0 to 1.

**Encoding:** three AI curves in the AI-hue steps, rising from 0.21 / 0.28 / 0.32 and flattening at 0.41–0.43 by the eighth reviewer. One human curve in the human hue, climbing 0.63 → 0.99 across *k* = 1 to 4, drawn as a clearly truncated segment.

**Annotate:** shade *k* > 4 as "no human comparison available." Mark the eighth-reviewer saturation point. Note that the last four AI reviewers are worth ≤ 0.04, and that the persona curve declines.

**Do NOT:** extrapolate, dash, or fade the human curve beyond *k* = 4 in a way that suggests continuation; omit the shading; place this panel where a reader will take the human-versus-AI gap as a demonstrated accuracy difference — the funding ranking was itself set by human review, and the caption must say so.


---

# 3. Production checklist

- [ ] FLAG 1 resolved — Fig. 3*B* asymmetry + core-vs-edge miss-rate use the mean-probability rule (23/18/26, persona widest), matching the Results sentence
- [ ] FLAG 2 resolved — displacement is text-only; the text says concentric/interleaved (§2.7), not "smaller region inside," and §4.1 of the audit is corrected
- [ ] FLAG 3 — no dimensionality anywhere in any panel
- [ ] Human and AI hues fixed once and identical across all four figures
- [ ] Models rendered as steps of the AI hue, never as new categorical hues
- [ ] Human/AI pair validated for colorblind separation at print size
- [ ] Diverging color used only in the evenness panel Fig. 2*B*, with a gray midpoint
- [ ] Condition order identical in every panel (baseline → one-at-a-time → persona)
- [ ] No dual axes anywhere; wording panel Fig. 2*C* verified inverted to AI ÷ human
- [ ] Direction-rule exceptions (evenness 2*B*, 4*B* coverage) labeled in words and stated in the legend
- [ ] Every reference line present: parity 1.0, chance 0.5, zero excess, 0.83 self-benchmark, ~10% fringe
- [ ] Intervals present on 2*A* (spread and richness) and 4*C* (funding AUC)
- [ ] No significance bracket between human and AI in 4*C* (funding AUC)
- [ ] Rank aggregation is an **SI** figure (not in Figure 4); its human curve truncated at *k* = 4 with the rest shaded
- [ ] Fig. 3*A* uses effective regions (inverse Simpson), human as a fixed marker/line at 4.94, AI as a matched-n=23 box+jitter (no human box, no replacement bootstrap)
- [ ] Fig. 3*B* scatter uses a sequential (not diverging) ramp; asymmetry inset titled accurately (not "only humans"); funding-independence guard in the caption
- [ ] Displacement appears only in the Results text (MMD² sentence), not as a panel
- [ ] Claim uniqueness is in **SI-4**, not Figure 4; its SI figure shows both matched and full-reservoir rates
- [ ] Figure 2 has three panels (A spread+richness merged, B evenness, C wording); the near-duplicate curve is removed from the main figure (retained builder for optional SI)
- [ ] Figure 4 has three panels (A within-panel box+jitter with paired P/δ annotations, B field split, C funding AUC); claim-uniqueness and rank aggregation are SI, not in Figure 4
- [ ] All text 6–12 pt at final size; RGB; single column 8.7 cm or full width 17.8 cm
- [ ] No numbers read from `…/{branch}/facet/`
- [ ] Each panel cited in the Results text, panel by panel, in caption order
- [ ] Figure legends updated if any panel lettering changed
