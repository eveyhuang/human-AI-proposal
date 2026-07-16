# Facet Visualization Redesign — Direction-Aligned Figures

Version: 1.0
Date: 2026-07-16
Status: **amends the visualization layer (§1A, §12.6–12.7, §15) of `diversity_facets_design_spec_v2.md`.**
All statistics, inference, tidy-table schemas, and stored sign conventions from that spec are
unchanged. This document governs presentation only: how notebooks `02`/`03`/`04` draw and export
figures. Target venue: PNAS-class journal.

## 0. Motivation

The current battery mixes two kinds of y-axes: **diversity meters** (up = more diverse: Vendi,
coverage, rarefaction, participation ratio, mean pairwise distance) and **concentration meters**
(up = more clumped: Ripley K, G-function, cumulative variance, NN similarity, self-BLEU,
ripley excess, vendi_slope). Readers must re-derive the direction per panel; in user testing the
PI misread four baseline panels in one pass. A referee gets one pass. The fix has three parts:

- **Strategy B** (notebooks 02/03): re-orient the concentration-meter panels to their
  equal-information complements so up = diverse everywhere.
- **Strategy C** (notebooks 02/03): add one *fingerprint* summary panel per cell on a shared,
  sign-aligned standardized axis.
- **Strategy A** (notebook 04): restructure the synthesis set around a new direction-aligned
  hero figure (fig1), renumbering to six figures.

---

## 1. The Direction Rule (new spec §1A.12)

> **Every quantitative panel is oriented so that up / right = more diverse, or it does not ship.**

1. Each quantitative panel carries a small corner badge: `↑ more diverse` (or `→ more diverse`
   for horizontal axes). The badge is redundant encoding — the axis label must independently
   state the direction in words.
2. **Displacement (M5) is the sole exception** and is visually quarantined: its panels use a
   visibly different style (no group-palette fill on the axis background band; bordered title),
   never share an axis with any facet metric, and the axis label reads
   `MMD² — larger = more shifted (NOT less diverse)`. M5 never appears in a fingerprint.
3. No figure may require the reader to remember a per-panel direction. If a panel cannot be
   re-oriented without distorting the statistic, it must wear its direction in the axis label
   *and* the badge, and it belongs in SI, not main text.
4. The rule binds `02`, `03`, `04`, and any future figure emitted from the facet tables.

---

## 2. Strategy B — panel re-orientation in 02/03

Five panels change to equal-information complements. **No stored value changes**: transforms are
applied at plot time from the same tidy rows; captions state the transform in one sentence.

| Current panel | File stem (unchanged) | New form | New y-axis label |
|---|---|---|---|
| G-function CDF | `evenness_g_function_cdf` | **1 − G(r)** (survival function) | `fraction of proposals with NO near-twin within r` |
| Ripley K + envelope | `evenness_ripley_excess_envelope` | **null_mean − K(r)** ("evenness vs. chance"); envelope flips with it: band = ±k95 around 0 | `evenness vs same-size null (positive = more evenly spread than chance)` |
| Cumulative variance | `dimensionality_participation_ratio_scree` | **1 − cumulative variance** ("residual variation") | `variance remaining beyond first x components` |
| NN-similarity histogram | `evenness_nn_similarity_hist` | NN-**distance** histogram (drop the 1−d flip) | `nearest-neighbor cosine distance (right = more isolated ideas)` |
| self-BLEU (tables/any panel) | n/a (table-facing) | report **1 − self-BLEU** in figures | `lexical distinctness (1 − self-BLEU)` |

Details:

- **1 − G(r):** identical data, complementary CDF. Caption sentence: *"Shown as the survival
  function 1 − G(r); the canonical G is its complement."* The interpretive caption flips
  accordingly: a curve that stays HIGH = few near-duplicates.
- **Evenness vs. chance (null − K):** the observed curve and the simultaneous global envelope
  are both subtracted from the null mean, so the band becomes a symmetric ±k95 ribbon around 0.
  Human curves are expected above 0, AI below. The global-envelope p is unchanged (the max-
  deviation statistic is sign-invariant). Caption keeps the simultaneous-band statement.
- **Residual variance:** the 90% crossing markers become 10% *remaining* crossings — same x
  positions, same interpretation, now the more-dimensional group is on top everywhere.
- **NN distances:** the histogram plots the persisted `nn_distance` rows directly (no similarity
  flip). Near-duplication now reads as mass near **zero**, stated in the caption.
- **Lexical distinctness:** wherever self-BLEU is drawn or quoted in a figure, use 1 − self-BLEU.
  The tests CSV keeps raw self-BLEU (stored values never change).

**Unchanged panels** (already up = diverse, badge only): pairwise-distance ridge, Vendi profile,
coverage box/scatter/effect, rarefaction, region-occupancy heatmap, all paired boxes/slopes
(paired Human − AI diffs: up = humans more diverse, stated on the axis), effect-ratio panels.
The **kernel eigen-scree stays canonical** (log-eigenvalue diagnostics have no honest complement);
it gets the badge + an explicit axis note (`steep cliff = few dominant modes = LESS diverse`) and
is an SI-only panel under the Direction Rule §1.3.

---

## 3. Strategy C — the fingerprint panel in 02/03

One **new required figure per (condition, task, text_version)**: `facet_fingerprint.{png,pdf}`,
plus one **new tidy table** backing it (no plotting-cell computation, per spec §1A.4).

### 3.1 Proposals (02): standardized diversity vs. the pooled-cloud null

- **Statistic:** for each facet's primary metric and each group (Human, Claude, Gemini, GPT),
  `z = (value(group) − mean(null)) / sd(null)`, where the null = the metric evaluated on
  **M = 999 same-n (n=23) draws without replacement from the pooled proposal cloud** — the same
  null construction already used for Ripley (spec §7.2), now applied battery-wide. Exception:
  **coverage_geometric** uses the existing human split-half distribution as its null (spec §5.2);
  **coverage_bertopic_region** uses union counts over the same pooled draws (bitmask machinery).
- **Sign alignment:** `mean_pairwise`, `vendi (q=1)`, `participation_ratio`,
  `coverage_geometric`, `coverage_bertopic_region` enter as-is; **`ripley_excess` enters
  negated**. After alignment, right of 0 = more diverse than a chance draw of the pooled cloud.
- **Rows (top→bottom):** spread, richness, evenness, dimensionality, coverage (geometric),
  coverage (domain). One dot per group (palette color + the marker shapes of §4.4), whiskers =
  jackknife CI transformed to z units ( (ci − mean(null)) / sd(null) ).
- **Layout:** one panel per condition is emitted per cell as usual; the zero line is labeled
  `pooled-cloud chance level`. Badge: `→ more diverse`.
- **Expected reading when the hypothesis holds: red (Human) is rightmost on every row.**

### 3.2 Reviews (03): paired effect fingerprint

- **Statistic:** the already-computed **Cliff's δ (AI − Human)** per facet primary metric, with
  bootstrap CI — but **sign-flipped at plot time for the clumping metrics** (`ripley_excess`,
  and `vendi_slope` if shown) so that on every row **left of 0 = AI panels less diverse**.
- Rows: spread, richness, evenness, dimensionality, coverage. One dot ± CI per model + pooled.
- Zero line labeled `parity with matched human panels`. Caption states which rows were
  sign-flipped. Stored δ in the tests CSV keeps its §1A.9 orientation; the flip is presentation.

### 3.3 New tidy table (written by 02; 03 needs none)

`results/tables/{condition}/proposals/{text_version}/facet_null_reference.parquet` — long form
`(condition, task, text_version, field, facet, metric, param, draw_idx, value)` holding the M=999
per-metric null draws (and the split-half draws for coverage, already persisted in curves; they
may be referenced rather than duplicated). 02's fingerprint (and 04's fig1) read z-scores from a
derived per-cell CSV `facet_fingerprint.csv` with columns
`(condition, task, text_version, facet, metric, param, group, value, z, z_ci_lo, z_ci_hi, sign_aligned)`.
04 must not recompute anything: it concatenates `facet_fingerprint.csv` files only.

---

## 4. Strategy A — notebook 04 restructure

### 4.1 New figure set (supersedes spec §15.8 numbering)

```
fig1_diversity_fingerprint.{png,pdf}      # NEW hero figure
fig2_double_compression_slopegraph        # formerly fig1 (unchanged content)
fig3_compression_map                      # formerly fig2 (unchanged content)
fig4_robustness_grid                      # formerly fig3, re-expressed (see 4.3)
fig5_paired_umaps_{condition}             # formerly fig4 (unchanged content)
fig6_condition_gradient                   # formerly fig5 (unchanged content)
```
`fig1_supplement_*` slopegraphs keep their names. `double_compression_summary.csv` gains columns
`z_generation`, `delta_filtering_aligned` sourced from the fingerprint CSVs.

### 4.2 fig1 — the hero figure

- **Panel A — schematic ("how to read the facets").** A drawn cartoon from seeded synthetic 2-D
  data: one spread-out cloud vs. one same-extent two-tight-blobs cloud, with callouts mapping
  each facet to what it detects (spread: average separation; richness: effective count; evenness:
  near-twins; dimensionality: independent axes; coverage: reach of the reference region).
  Labeled `schematic — illustrative data`. This is the paper's reading key.
- **Panel B — generation fingerprint.** §3.1's plot, small-multiple columns per condition
  (baseline / one_at_a_time / persona), shared x-scale, one zero-parity line per column.
- **Panel C — filtering fingerprint.** §3.2's plot, same column layout.
- Both panels: right = more diverse, humans/parity at 0, per-model dots never collapsed,
  pooled-AI dot hatched/open with `n=23 of 69` in the legend. Stars per the standing p_raw
  (primaries) / p_fdr (secondaries) convention, carried from 02/03.

### 4.3 fig4 (robustness grid) re-expression

The grid keeps rows = facets × columns = tasks, but the **evenness row adopts the standardized
axis of §3** (generation: aligned z; filtering: flipped δ), eliminating the one remaining
mixed-direction cell. The four ratio rows keep `AI ÷ Human diversity retained` (parity 1.0) —
ratios remain the quotable units. Every cell carries the badge.

### 4.4 Publication mechanics

- **Export presets** (new `plotting.py` constants used by all 04 main figures):
  single column 8.7 cm, double column 17.8 cm, max height 22.5 cm, minimum rendered font
  ≈ 6 pt at print size, `dpi=300` PNG + vector PDF (already standard).
- **Accessibility:** the crimson/green pair in the standing palette is a red–green confusion
  risk. Mitigation adopted: **redundant marker shapes per group** in fig1 and every 04 figure
  and in the 02/03 fingerprints — Human ● , Claude ■ , Gemini ▲ , GPT ◆ , All AI ⬠/hatched.
  (Optional, flagged for the user: swap Gemini `#7B68EE` → a yellow-orange such as `#E69F00`
  to make the palette fully Okabe–Ito-compatible; requires a one-line palette change that
  propagates everywhere. Not required for this redesign.)
  Condition, where encoded, stays marker-shape in fig3 — to avoid a clash, fig3 keeps condition
  shapes and uses color-only for models there (it already does), stated in its caption.

---

## 5. Invariants (what deliberately does not change)

- All statistics, p-values, CIs, tidy-table schemas, and stored sign conventions.
- Figures read only from tidy tables/curves (§1A.4); the new nulls are persisted first (§3.3).
- Interpretable units stay primary in per-facet panels and text ("AI reaches 81% of the human
  proposal space"; "23 human proposals behave like ~11 distinct ones").
- Palette hexes (unless the optional Okabe–Ito swap is separately approved); file-stem naming
  scheme `{facet}_{metric}_{view}`; PNG+PDF export; caption conventions (CI source, resampling
  labels, n statements, which p is starred).
- M5's quarantine per §1.
- The equal-n rule everywhere, including the new null draws (all at n=23 / panel size m).

## 6. Implementation inventory

| File | Changes |
|---|---|
| `src/plotting.py` | direction badge helper; transforms in `plot_g_cdf` (1−G), `plot_ripley_envelope` (null−K, symmetric band), `plot_scree` residual-variance mode, NN-distance hist; new `plot_fingerprint` (z and δ modes); marker-shape encoding; PNAS width presets; M5 quarantine styling in `plot_mmd_bar` |
| `src/diversity_inference.py` | `pooled_null_reference(X_pool, stat_fns, n, M, seed)` helper (reuses `_null_curves_from_pool` machinery); emit null draws for the battery in `build_proposal_facet_outputs` |
| `notebooks/02` | write `facet_null_reference.parquet` + `facet_fingerprint.csv`; emit `facet_fingerprint` figure; panels pick up transformed plotting automatically |
| `notebooks/03` | emit review `facet_fingerprint.csv` (δ-based, from existing tests rows) + fingerprint figure |
| `notebooks/04` | fig1 hero (schematic + two fingerprints from the CSVs); renumber fig2–fig6; fig4 evenness row re-expression; summary CSV columns |
| `docs/plans/diversity_facets_design_spec_v2.md` | unchanged (this doc is the amendment of record) |

**Verification checklist for the implementation session:**
every panel passes the Direction Rule (up/right = diverse or SI+badge+label); human dot rightmost
in fingerprints wherever the tables say humans are more diverse; envelope p-values identical
before/after the K re-orientation; fig1 renders at 17.8 cm with legible fonts; 04 still imports
no metric code and recomputes nothing; all previous §14 sanity checks still pass.
