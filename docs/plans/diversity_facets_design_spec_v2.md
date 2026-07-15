# Diversity-Facet Metrics — Coding-Agent Design Spec

Version: 2.0 (clean rebuild)
Date: 2026-07-15

---

## 0. Facet architecture (read before coding)

The manuscript decomposes "narrowing of collective search" into **five facets** (spread, evenness,
richness, dimensionality, coverage) plus a separate directional check (**displacement**). This spec
implements each facet as one or more metrics. **Every metric carries its manuscript facet label**,
so the results tables emit facet names the paper cites directly.

**All seven metrics (M0–M6) are built fresh in this spec.** There is no EXISTING/NEW split anymore.

| Facet (manuscript) | Question | Metric(s) | ID | Spec § | Directional? | Role |
|---|---|---|---|---|---|---|
| **Spread / dispersion** | How far apart are ideas, on average? | `mean_pairwise` (primary) + `centroid_loo`, `mst_dispersion`, `sparseness`, `nn_isolation`, `spherical_variance` (convergent) | **M0** | §3 | no | Facet 1 — **confirmatory** |
| **Evenness** | Uniform, or clumped/repetitive? | Ripley-K / G-function (primary) **+** Vendi profile *slope* over q | **M4** (+M1) | §7 (+§4) | no | Facet 2 |
| **Richness** | How many effectively-distinct ideas? | Vendi profile `VS_q` (low-q end) | **M1** | §4 | no | Facet 3 — **confirmatory (headline)** |
| **Dimensionality** | How many independent axes? | Participation ratio `PR` (+ effective rank) | **M3** | §6 | no | Facet 4 |
| **Coverage** (geometric) | How *much* of the human space is occupied? | support-overlap coverage + density | **M2** | §5 | **yes** | Facet 5 — **confirmatory (headline)** |
| **Coverage** (domain) | *Which* literature areas are engaged? | BERTopic-region coverage, unique-MeSH coverage | **M6** | §9 | **yes** | Facet 5 — convergent |
| *Displacement* | *Same region as humans, or shifted?* | *MMD² + optimal-transport distance* | ***M5*** | §8 | **yes** | *directional check — exploratory* |

**Confirmatory (headline):** M0 (`mean_pairwise`), M1 (`VS_q` at q=1), M2 (`coverage`).
**Exploratory / mechanistic / convergent:** M3, M4, M5, M6, and M0's convergent metrics.

Three structural rules that follow from the manuscript:

1. **Spread is Facet 1 — a first-class facet, not an "anchor."** `mean_pairwise` is its **primary**
   metric; `centroid_loo`, `mst_dispersion`, `sparseness`, `nn_isolation`, `spherical_variance` are
   **convergent support**. One facet reported through several views — **not six findings**. A metric
   correlation panel (§3.4) must demonstrate they co-vary, justifying the collapse.
2. **Evenness is one facet carried by two metrics.** M1's profile *slope* and M4's local-repetition
   curves *jointly* measure evenness. Emit both under `facet="evenness"` (M4 primary; M1's slope as
   a derived column, §4.2).
3. **Coverage has two halves.** Geometric (M2) answers *how much*; domain (M6) answers *which areas*.
   Both tagged `facet="coverage"`. Reviews have no domain half (reviews aren't projected onto PubMed)
   — the review coverage facet is geometric-only.

---

## 1. Global conventions (apply to every metric, every notebook)

### 1.1 Embedding-space rule
Every metric is computed in **full embedding space** on L2-normalized vectors. UMAP/PCA 2-D
coordinates are for **figures only** and must never be fed to a metric. (Chari & Pachter 2023 is the
manuscript's citation for why projected distances/densities are not analyzable.)

### 1.2 Distance / kernel conventions
- L2-normalize every embedding row → cosine similarity = dot product; cosine distance = 1 − dot.
- Default metric = **cosine** everywhere unless a section says otherwise.
- **Centroid-based metrics use Euclidean distance to the un-normalized centroid.** Do *not*
  re-normalize the centroid: the mean of unit vectors has norm < 1, and that shrinkage *is*
  concentration information (see `spherical_variance`, §3.1). Re-normalizing discards it.
- Pairwise distance matrices are computed once per (task, condition, text_version, field) in notebook `00`
  and cached (§2.3). Metrics needing raw embeddings (M1 kernel, M3 covariance, M5 MMD) load the
  embedding arrays, not the matrices.

### 1.3 Equal-n rule (load-bearing)
Every metric here is sample-size biased — more points ⇒ more measured diversity. Absolute values are
comparable across groups **only at equal n**.
- Per-model comparisons are equal-n by construction (Human 23 vs each model 23).
- Pooled Human-vs-All-AI is **not** equal-n (23 vs 69) → use the subsample-to-23 path (§1.5).
- **M6 (domain coverage) is a union/count metric and is the most n-sensitive of all** — a 69-set
  touches more topic regions than a 23-set by counting alone. It **must** go through the subsample
  path. Never report a raw 23-vs-69 union comparison.
- Never compare a diversity value computed at one n against one computed at another n.

### 1.4 Inference engine (two nulls)
- **Between-group significance → label permutation.** Stack the two groups' embeddings, shuffle group
  labels B ≥ 10,000×, recompute the statistic, two-sided p = fraction of |Δ_perm| ≥ |Δ_obs|.
  - `mode="within_diff"` for M0, M1, M3, M4, M6: statistic is `stat(X_a) − stat(X_b)`.
  - `mode="two_sample"` for M5: the statistic *is* the between-group distance; no difference taken.
  - M2 is asymmetric → uses a split-half human reference baseline instead (§5.2).
- **Within-group CIs → jackknife (leave-one-out) or subsampling. NOT bootstrap-with-replacement.**
  With-replacement resampling injects exact duplicate rows, which deflates every metric here
  (duplicates shrink kernel eigenvalues, collapse effective counts, shorten NN distances).
  - Point-estimate CIs: jackknife over the n=23 rows (23 recomputes).
  - Pooled AI: subsample **without replacement** (§1.5) — safe, no duplicates.
  - This is a hard rule in the rebuild. Do not introduce a with-replacement bootstrap anywhere.

### 1.5 Pooled AI subsampling (built by `4a` — see prep spec §2.2)
The cache is generated once per (condition, text_version) in `4a` and reused everywhere:
`data/prepared/{condition}/proposals/{text_version}/subsample_idx_ai_n23_seed42.npy`, shape
(1000, 23), **without replacement**, seed 42. Values are **positional rows** into the proposal
embedding bundle — so `X[idx[b]]` works directly, provided the uid-order assertion passes.
Usage for pooled Human-vs-All-AI at each condition:
- compute the metric on each of the 1000 AI subsamples → a pooled-AI distribution at n=23
- compare against the single Human value (n=23)
- report: Human value, pooled-AI mean + 95% percentile interval, empirical p (fraction of subsamples
  on the "AI ≥ Human" side, or reverse, per metric direction)

### 1.6 Test the gradient as a gradient
The predicted ordering (Claude < Gemini < GPT < Human) is an **ordered** alternative. Run a
**Jonckheere–Terpstra trend test** across the four groups in the predicted order → one p for
"monotone increase." Stronger and more publishable than three pairwise tests. Report per
(condition, task, text_version, facet, metric). **Direction flips for M5** (larger distance = more shifted)
— state the predicted direction explicitly before running JT.

### 1.7 Multiplicity
7 metric families × 3 models × 3 conditions × 2 tasks × 2 text_versions is a large family. Pre-register
**M0 (`mean_pairwise`), M1 (q=1), M2 (`coverage`)** as primary; apply Benjamini–Hochberg FDR across
the secondary family within each (task, text_version, field). State this in Methods.

### 1.8 Palette and figure grammar
Human `#DC143C`, Claude `#4A90E2`, Gemini `#7B68EE`, GPT `#3CB371`, pooled All-AI `#4A90E2`,
unknown `#808080`. **All figure grammar, CI conventions, titles, and export rules are specified in
§1A — read it before writing any plotting cell.**

### 1.9 Robustness passes (pre-empt reviewers)
- **Branch:** run the full battery on both `original` and `rephrased` text. `rephrased` is the
  **primary** (style-controlled); `original` is the robustness check. This is a *config parameter*,
  not a separate notebook (§1.10).
- **Lexical control:** distinct-n and self-BLEU, so that if lexical *and* semantic diversity both
  collapse, the effect can't be pinned on the encoder. One helper in `src/lexical.py`.
- **Encoder control (optional but strong):** re-run M0–M3 with a second sentence encoder.
- **M1 only:** RBF-kernel sensitivity at σ = {0.5, 1, 2} × median pairwise distance.
- **M2 only:** k-sensitivity sweep at k ∈ {2, 3, 5}.

### 1.10 Config-driven parameterization (the structural fix)
**The old pipeline's failure mode was cloning a notebook per text branch** (`5a`/`5b`, `6a`/`6b`),
producing near-identical code that drifted apart. The rebuild does **not** clone. Each analysis
notebook is parameterized and looped over the full grid:

```python
# cell 1 of every analysis notebook — the ONLY thing that varies between runs
CONFIG = dict(
    conditions = ["baseline", "one_at_a_time", "persona"],
    text_versions   = ["rephrased", "original"],        # rephrased = primary
    fields     = ["whole"],                        # reviews add: strengths, weakness
    models     = ["claude", "gemini", "gpt"],
    n_human    = 23,
    seed       = 42,
    B_perm     = 10_000,
    B_sub      = 1_000,
)
```
Every notebook iterates the grid internally and writes one tidy row per cell of the grid. No
notebook is duplicated to change a parameter. If per-run isolation is wanted, execute the same
notebook under `papermill` with different parameters — still one source file.

---

## 1A. Visualization guide

Authoritative for every plotting cell in `02`, `03`, `04`. Built on the project's existing figure
conventions, with corrections where the facet design changes what a panel can honestly show.

### 1A.0 Two kinds of panel — read this before anything else

Every figure in this pipeline is one of two types, and confusing them produces a figure that lies:

| | **Observation-level panel** | **Set-level facet panel** |
|---|---|---|
| What a point is | a real datum — one pairwise distance, one per-proposal review value, one CV fold | **there are no data points.** The metric is a property of the *whole set* — one number per group |
| Examples | M0's pairwise-distance ridge; `03`'s per-proposal paired values | Vendi `VS_1`, participation ratio, coverage, `mean_pairwise` **of a group** |
| What the spread shows | variation among observations | variation of a **resampling distribution** — jackknife replicates (n=23) or subsample values (n=1000) |
| Boxplot grammar (§1A.2) | applies fully | applies **only** to the resampling distribution, and the caption must say so |
| Funded/top-ranked rings | valid where a point = one proposal | **never** — a jackknife replicate is not a proposal |

**The rule:** a jackknife replicate or a subsample value is *not* an observation. Any panel showing
them must label them: *"points = 23 leave-one-out jackknife replicates"* or *"points = 1000 pooled-AI
subsamples (n=23, without replacement)."* Never let a reader read a resampling distribution as data.

> *Optional nicety:* jackknife replicate *i* corresponds to omitting proposal *i*, so replicates can
> legitimately carry `proposal_uid` and be ringed by funding/top-rank. Use only if it earns its space.

### 1A.1 CI source — corrects the existing "bootstrapped mean" convention

The project's standing grammar says *"plot the bootstrapped mean as a filled diamond… with vertical
error bars for the 95% bootstrap confidence interval."* **The visual stays exactly as-is. The CI
source must change for set-level metrics.** §1.4 forbids with-replacement bootstrap across this whole
battery: resampling with replacement injects duplicate rows, which shrink kernel eigenvalues, collapse
effective counts, and shorten nearest-neighbor distances — i.e. it **deflates every diversity metric
here**, and it deflates them most for exactly the groups that are already tight.

| Panel type | CI method | Bootstrap-with-replacement? |
|---|---|---|
| Observation-level mean (pairwise distances, per-proposal review values) | bootstrap the mean | ✅ fine — the mean of observations is not a set-level diversity metric |
| Set-level facet metric, per-model (n=23) | **jackknife** (leave-one-out, 23 recomputes) | ❌ **never** |
| Set-level facet metric, pooled Human-vs-All-AI | **subsample without replacement** (1000 × n=23, §1.5) | ❌ **never** |
| Paired review contrast | paired bootstrap / exact Wilcoxon CI over the **23 proposals** | ✅ resampling proposals is fine — you are not resampling within a set |
| M5 displacement | permutation null band | n/a |

**Caption text must name the method.** `diamond = point estimate; bars = 95% jackknife CI` — not
"bootstrap 95% CI". If a figure says "bootstrap" for a set-level facet metric, it is either mislabeled
or computed wrong; both are bugs.

### 1A.2 Standard boxplot grammar 

For group-comparison distributions. Use one shared helper — never hand-roll per notebook.
- **Box:** median line, IQR box, whiskers, outlier points. Fill with the group color at 70% opacity;
  black outlines and median lines.
- **Jittered scatter:** individual observations, horizontal jitter ≈ `±0.15`, size ≈ `20`, 50% opacity,
  group-color fill. Where proposal metadata exist: **magenta ring** = funded Human proposal;
  **black ring** = top-ranked proposal.
- **Point estimate + 95% CI:** filled diamond ≈ `50` pt with vertical error bars, drawn **above** the
  jitter. CI source per §1A.1.
- Preserve `proposal_uid` (or `review_uid` / `target_proposal_uid`) through every reshape/melt so
  funding and top-rank encodings survive into the plotting layer.
- Non-proposal observations (pairwise distances, CV folds, **jackknife replicates, subsample values**)
  keep the box/point/CI grammar but **must not** carry proposal-level funding/ranking encodings.
- Grouped metric panels (e.g. a metric across several `k` or `q` values) use dodged standardized
  boxplots with a group legend, plus the metadata legend when proposal-level rows are present.

### 1A.3 Violin, ridge, and histogram views (retained, with one promotion)

- **Violins:** sparingly, as descriptive shape diagnostics — not the primary comparison figure where
  inferential interpretation is expected. Prefer §1A.2. If used: same palette, clear median/quartile
  annotation, and don't duplicate an adjacent boxplot unless the shape adds information.
- **Ridge plots:** for dense pairwise-distance distributions where shape and skew matter. Group-colored
  density fills, **solid median** and **dashed mean** lines in the group color.
  - **Promotion:** for **M0 (§3.3 panel 2)** the ridge is **required, not optional.** Bimodality is
    confirmed in some groups, so a mean alone actively misleads — two tight blobs far apart average to
    a large `mean_pairwise` while containing two ideas. The ridge is what makes M0's headline number
    honest, and it is the visual argument for why M1/M3/M4 exist.
- **Histograms:** consistent binning across groups, transparent fills, log-scale counts when long tails
  swamp the distribution. Label as descriptive full-range views.

### 1A.4 Curve panels (new — profiles, scree, envelopes, rarefaction)

The facet battery introduces curve figures the existing grammar doesn't cover.

- **Source rule:** every curve panel reads `facet_diversity_curves.parquet` (§12.3). **Never recompute
  a curve inside a plotting cell.** If a curve isn't in the parquet, the fix is in `02`/`03`, not here.
- **Line + ribbon:** one line per group in the group color; 95% CI as a ribbon at ~20% opacity, same
  hue, no edge. Median solid.
- **Diversity profile (M1, §4.4a):** x = `q`, y = `VS_q`. x may be linear over `{0, 0.5, 1, 2, 4, ∞}`
  with `∞` rendered as a labeled final tick — do **not** plot `∞` as a numeric position. Annotate the
  q=1 headline value.
- **Eigenvalue scree (M1, §4.4b):** x = eigen-index (1…22), y = normalized eigenvalue. Shared axes
  across groups. Log-y when the cliff is steep. This is often the most persuasive panel — give it room.
- **Ripley K / G (M4, §7.4):** observed curve in group color over a **grey simultaneous null envelope**
  (§1A.5). G-function panels are CDFs — y ∈ [0,1], and state that a **left-shifted** curve means
  shorter NN distances = near-duplication.
- **Rarefaction (M6, §9.3):** x = number of proposals sampled `m` (1…23), y = union size (regions or
  MeSH terms), one line per group + CI ribbon. **This is M6's primary panel**, because a union count at
  a single `n` is not interpretable on its own. Annotate whether curves are still climbing at m=23.
- **Cumulative variance (M3, §6.3):** x = component index, y = cumulative variance explained; mark the
  90% crossing per group.

### 1A.5 Null bands and envelopes (new)

- Grey (`#808080`) fill at ~20% opacity, no edge, drawn **beneath** observed curves.
- The legend must state **which** null: `resampling null from pooled cloud (M=999)` for M4;
  `label-permutation null (B=10,000)` for M5; `human split-half reference (1000 splits)` for M2.
- **Simultaneous vs pointwise must be stated in the caption.** M4 uses a *global* envelope
  (Myllymäki et al. 2017) — a single simultaneous band. A pointwise band drawn at many radii invites
  exactly the multiple-testing error the global envelope exists to avoid. If a band is pointwise, say
  so and do not read significance off individual radii.

### 1A.6 Scatter and parity panels (new)

- **Density–coverage scatter (M2, §5.4):** x = coverage, y = density; one marker per model in the group
  palette; the **human split-half point** plotted as an open marker near (1,1) and explicitly labeled
  as the same-distribution reference. Subsample CI ellipses at 95%. Expected pattern (state in caption):
  AI pulled **left** (low coverage) while staying **high** on density.
- **Parity lines (all `04` ratio figures):** dashed, `#404040`, labeled inline (`human parity`). For
  coverage panels the parity line is the **median human split-half coverage**, *not* 1.0 (§15.2) —
  mislabeling it 1.0 overstates the gap.
- **2×2 compression map (§15.4):** parity lines on both axes; label all four quadrants; condition
  encoded by marker shape, model by color; baseline→persona arrows at ~30% opacity.
- **Axis mode:** linear ratio if every ratio < 1; `log2(ratio)` if any exceeds 1, so "half as diverse"
  and "twice as diverse" sit symmetrically about 0. State which in the caption.

### 1A.7 Heatmaps (new)

- **Facet convergence heatmap (§3.4) — required.** Spearman correlations. **Diverging** colormap
  centered at 0 (`RdBu_r`), range `[-1, 1]`, annotated cells. Order rows/columns by facet, and draw
  block separators between facets: the M0 block should read uniformly high (justifying the collapse to
  one facet) while off-block cells read markedly lower (justifying the multi-facet design). This single
  figure defends both halves of the design — do not bury it in a supplement.
- **Region-occupancy heatmap (M6, §9.4):** topic regions × groups, cell = proposal count. **Sequential**
  colormap (`viridis`); zero cells visibly distinct from low-but-nonzero (set `vmin=0` and use a
  masked/`under` color) — "AI never proposes anything in region X" **is the finding**, so a zero must
  not read as merely dark. Sort regions by human occupancy descending.

### 1A.8 UMAP and embedding-space projections (retained, paths corrected)

- **UMAP is never a metric input** (§1.1). It is illustration only, and every UMAP caption must say so.
- **Reuse cached coordinates. Never refit inside a visualization cell.** Paths are now (prep spec §4):
  - proposal-space: `data/prepared/{condition}/proposals/{text_version}/proposal_umap2d.npy`
  - review-space: `data/prepared/{condition}/reviews/{text_version}/review_umap2d.npy`
  - literature-space: `data/embeddings/literature/lit_umap_reducer.pkl` + `lit_umap2d.npy`
  > The older `results/tables/rephrased/minimal/cached/proposal_umap2d.npy` path is **retired** — `4a`
  > now writes UMAP caches per (condition, text_version) under `data/prepared/`.
- **Literature-space UMAPs and BERTopic-region overlays must project abstract-only proposal
  embeddings** (`proposal_embeddings_abstract.pkl`), not full-proposal embeddings — this keeps proposal
  markers comparable to literature abstract embeddings and to the M6 proposal-to-literature KNN, which
  `4a` also builds from `abstract_text` (prep spec §2.6). Proposal-space UMAPs use `full_text`.
- Axis labels identify the coordinate system: `UMAP-1` / `UMAP-2` for proposal-space;
  `Literature UMAP Dim 1` / `Literature UMAP Dim 2` for literature-anchored maps.
- Marker semantics: AI groups in the group palette; Human in the Human color; **magenta ring** = funded
  Human; **black outline** = top-ranked (Human and AI).
- Per-cluster zooms retain marker semantics; titles carry cluster name, total `n`, and compact
  discriminative topic labels where available.
- Literature backgrounds are colored by **BERTopic embedding-region** labels, not LDA lexical topics.
  LDA-colored maps are supplementary diagnostics only.
- Legends must decode black top-ranked outlines, magenta funded rings, outlier rings, and any
  literature-region colors needed to read the panel.

### 1A.9 Effect-size and significance panels (retained, with the facet mapping)

Pair every distribution panel with an effect-size panel where space allows. Effect size is **not** the
same quantity across facets — use this mapping:

| Facet | Metric | Effect size | Effect-panel axis label |
|---|---|---|---|
| spread | `mean_pairwise` | ratio Human ÷ AI | `Mean pairwise distance: Human ÷ AI` |
| richness | `vendi` (q=1) | ratio Human ÷ AI | `Effective distinct proposals: Human ÷ AI` |
| evenness | `ripley_excess` | envelope area | `Excess short-range neighbor mass (AI − null)` |
| dimensionality | `participation_ratio` | ratio or Δ | `Effective dimensionality: Human ÷ AI` |
| coverage | `coverage_geometric` | coverage ∈ [0,1] | `Fraction of human proposal space reached` |
| coverage | `coverage_bertopic_region` | ratio at matched n | `Literature regions covered: Human ÷ AI` |
| displacement | `mmd2` | MMD² | `MMD² (Human ↔ AI), permutation null` |
| **reviews, any facet** | paired | **Cliff's δ** | `Cliff's δ (AI − Human, paired by proposal)` |

- Cliff's δ panels: vertical zero reference line, horizontal CIs, group-colored markers for each
  model-vs-Human contrast.
- Label the **direction** of every effect axis. Where direction flips by metric — **M5 displacement is
  the one that flips** (larger = more shifted, not more diverse) — state it in the axis label or caption.
- **Significance stars:** `*** p<.001`, `** p<.01`, `* p<.05`. Panels must state **which p** is starred:
  `p_raw` for the three pre-registered primaries (M0 `mean_pairwise`, M1 `VS_1`, M2 `coverage`) and
  `p_fdr` for everything else (§1.7). Never mix the two in one panel without saying so.

### 1A.10 Titles, labels, legends 

- **Every title names the facet and the metric.** Format:
  `{Facet} — {metric} · {condition} · {task}/{text_version}`
  e.g. `Richness — Vendi VS₁ · persona · proposals/rephrased`.
  Optional second line for encodings: `diamond = point estimate; bars = 95% jackknife CI`.
- Axis labels use metric units or definitions, never variable names: `Pairwise cosine distance`,
  `Distance to group centroid`, `Cosine distance to global centroid`, `Nearest-neighbor distance`,
  `Unique MeSH descriptors`, `Effective number of distinct proposals`, `Participation ratio`.
- **Sample size is mandatory wherever group size could affect interpretation** — in tick labels, panel
  titles, legends, or an adjacent table. Every facet metric here is n-sensitive (§1.3), so a panel that
  hides n invites the exact misreading the equal-n rule exists to prevent. For pooled panels state
  `AI n=23 subsampled from 69`, never a bare `n=69`.
- Legends only where they decode color, marker, line style, or rings. Place outside or below crowded
  panels.
- Light grids on quantitative y-axes (`alpha` 0.2–0.3); no heavy gridlines on embedding maps.

### 1A.11 Export standards

- `dpi ≥ 200` for notebook diagnostics, `dpi = 300` for manuscript figures; always
  `bbox_inches='tight'`.
- Save **both** `.png` (review) and `.pdf` (vector, manuscript) for any figure headed for the paper.
- Path and filename conventions: **§12.5**. Every figure is saved — no figure exists only in notebook
  output.
- Figures are written from the tidy tables (§12), never from in-memory metric objects, so a figure can
  always be regenerated without re-running `02`/`03`.

---

## 2. Repository layout (new)

### 2.1 Structure
```
src/
  data_io.py            # loading, roster validation, L2-normalization
  diversity_facets.py   # M0–M6 core math — pure functions, no I/O
  diversity_inference.py# permutation, jackknife, subsample, JT, paired Wilcoxon, FDR, envelopes
  panels.py             # review exact-n panel enumeration
  lexical.py            # distinct-n, self-BLEU (robustness)
  plotting.py           # palette, standard figure grammar
notebooks/
  4a_prepare_proposal_for_analysis.ipynb   # EXISTS — proposals + literature map. Modify per prep spec §2
  4b_prepare_review_for_analysis.ipynb     # EXISTS — reviews + panels.    Modify per prep spec §3
  02_facets_proposals.ipynb   # M0–M6, unpaired, looped over condition × text_version
  03_facets_reviews.ipynb     # M0–M5, paired per-proposal, condition × text_version × field
  04_synthesis.ipynb          # cross-task, cross-condition figures (no recomputation)
results/
  tables/   figures/
```

Pipeline: `4a → 4b → 02 → 03 → 04`.

**`4a`/`4b` already exist and are already parameterized over `condition × text_version`.** Do not
recreate or restructure them — see `prep_layer_4a_4b.md`. Only `02`/`03` compute metrics; `04` reads
and plots. Notebooks stay thin — all math lives in `src/`, unit-tested independently of any notebook.

### 2.2 `diversity_facets.py` — public functions
All take L2-normalized `X: np.ndarray (n, d)`.
```
# M0 — spread
mean_pairwise(X, metric="cosine") -> float
centroid_dispersion_loo(X) -> float
mst_dispersion(X) -> float
sparseness(X) -> float
nn_isolation(X) -> float
spherical_variance(X) -> float

# M1 — richness (+ evenness slope)
vendi_scores(X, qs=(0,0.5,1,2,4,np.inf), kernel="cosine", sigma=None) -> dict[q -> float]
vendi_slope(vs: dict) -> float                    # derived evenness statistic, §4.2

# M2 — coverage (geometric)
coverage_density(X_ref, X_gen, k=3) -> dict       # {"coverage":.., "density":..}

# M3 — dimensionality
participation_ratio(X) -> float
effective_rank(X) -> float

# M4 — evenness (local repetition)
nn_distances(X, metric="cosine") -> np.ndarray
g_function(X, radii) -> np.ndarray
ripley_K(X, radii) -> np.ndarray

# M5 — displacement (two-sample)
mmd2_rbf(X, Y, sigma=None) -> float
wasserstein_ot(X, Y, metric="cosine") -> float

# M6 — coverage (domain); takes projected topic/MeSH assignments, not embeddings
region_coverage(topic_ids: np.ndarray, n_regions_total: int) -> dict
mesh_coverage(mesh_sets: list[set]) -> dict
```

### 2.3 `diversity_inference.py` — public functions
```
label_permutation_test(X_a, X_b, stat_fn, B=10000, seed=42, mode="within_diff")
    -> {"stat_obs", "p_two_sided", "null"}
    # mode="within_diff": stat_fn(X_a) - stat_fn(X_b)   [M0, M1, M3, M4, M6]
    # mode="two_sample":  stat_fn(X_a, X_b)             [M5]
jackknife_ci(X, stat_fn, alpha=0.05) -> {"point","lo","hi","replicates"}
subsample_pooled(X_pool, idx_cache, stat_fn) -> np.ndarray
split_half_reference(X_human, stat_fn, n_splits=1000, seed=42) -> np.ndarray   # M2 baseline
jonckheere_terpstra(groups_ordered) -> {"JT","p"}
paired_wilcoxon(human_vals, ai_vals) -> {"W","p","cliffs_delta"}
global_envelope_test(obs_curve, null_curves) -> {"p","lo_env","hi_env"}        # M4
benjamini_hochberg(pvals) -> qvals
```

### 2.4 Prep artifacts (built by `4a`/`4b`)
**Superseded — see `prep_layer_4a_4b.md` §4 (the prep → analysis contract)** for the authoritative
file list, paths, and the load-time assertions `02`/`03` must make. Summary of what `02`/`03` read:
```
data/prepared/{condition}/proposals/{text_version}/
    proposal_master.csv, proposal_embeddings_full.pkl, proposal_embeddings_abstract.pkl,
    proposal_pairwise_cosine_full.npy, proposal_to_literature_knn.npz,
    subsample_idx_ai_n23_seed42.npy, proposal_umap2d.npy (figures only), prepare_manifest.json
data/prepared/{condition}/reviews/{text_version}/
    review_master.csv, review_embeddings_text.pkl, review_embeddings_{strengths,weakness}.pkl,
    review_pairwise_cosine_text.npy, review_panels_exact_n.pkl,
    review_umap2d.npy (figures only), prepare_manifest.json
data/prepared/literature/  +  data/embeddings/literature/
    lit_bertopic_assignments.csv, lit_bertopic_topic_info.csv, literature_mesh_index.parquet,
    literature_prepare_manifest.json, lit_umap2d.npy (figures only)
```
**Positional-index warning:** `subsample_idx_ai_n23_seed42.npy` and `review_panels_exact_n.pkl` store
**row positions**, not uids. `02`/`03` must assert `manifest['proposal_uid_order']` /
`manifest['review_uid_order']` matches the loaded master before using them, or a re-run of prep that
reorders rows silently produces wrong numbers.

### 2.5 Data-source contract — which file feeds which metric

**This section is normative. The agent must not choose an input array on its own.** `4a` builds two
proposal embedding bundles and `4b` builds three review bundles; picking the wrong one silently
changes what "diversity" means.

#### 2.5.1 The canonical choice

| | Primary input | Why |
|---|---|---|
| **Proposals, M0–M5** | **`proposal_embeddings_full.pkl`** (`full_text`) | the proposal as actually submitted and reviewed; the project's established primary (`proposal_pairwise_cosine_full.npy` and the proposal UMAP are both built from it) |
| **Proposals, M6** | **`proposal_to_literature_knn.npz`** (derived from `abstract_text`) | abstracts are the right comparand for PubMed abstracts; `4a` already builds it this way (prep spec §2.6) |
| **Reviews, M0–M2 (whole)** | **`review_embeddings_text.pkl`** (`review_text`) | the full review |
| **Reviews, field-specific** | `review_embeddings_strengths.pkl` / `review_embeddings_weakness.pkl` | **`rephrased` only** — gate on `manifest['fields_available']` |
| **Robustness (secondary)** | `proposal_embeddings_abstract.pkl` for M0–M3 | reported as a robustness pass, never as the headline |



#### 2.5.2 Per-metric input table

All paths relative to `data/prepared/{condition}/{task}/{text_version}/` unless stated.
`X` = the L2-normalized `(n, d)` array from the bundle, sliced to the group's rows.

| Metric | Task | File(s) | Array used | Raw vectors required? |
|---|---|---|---|---|
| **M0** `mean_pairwise`, `mst_dispersion`, `sparseness`, `nn_isolation` | proposals, reviews | `proposal_embeddings_full.pkl` / `review_embeddings_text.pkl` | `X` → pairwise cosine | no — may use the cached matrix (§2.5.4) |
| **M0** `centroid_loo`, `spherical_variance` | proposals, reviews | same | `X` | **yes** — centroid/mean of vectors |
| **M1** `vendi`, `vendi_slope` | proposals, reviews | same | `X` → Gram `X @ X.T` | **yes** |
| **M2** `coverage_geometric` | proposals, reviews | same | `X_ref` = Human rows, `X_gen` = model rows | **yes** |
| **M3** `participation_ratio`, `effective_rank` | proposals, reviews | same | `X` centered → `Xc @ Xc.T` | **yes** |
| **M4** `ripley_excess`, `g_function` | proposals, reviews | same | `X` → pairwise cosine | no — may use the cached matrix |
| **M5** `mmd2`, `ot_wasserstein` | proposals; reviews (pooled only) | same | `X_human`, `X_ai` | **yes** — RBF kernel + median heuristic |
| **M6** `coverage_bertopic_region` | proposals only | `proposal_to_literature_knn.npz` + `data/prepared/literature/lit_bertopic_assignments.csv` + `lit_bertopic_topic_info.csv` | KNN indices `[:, :k]` → topic ids | no |
| **M6** `coverage_mesh_terms` | proposals only | `proposal_to_literature_knn.npz` + `data/prepared/literature/literature_mesh_index.parquet` | KNN indices `[:, :k]` → MeSH sets | no |

**Never a metric input:** `proposal_umap2d.npy`, `review_umap2d.npy`, `lit_umap2d.npy` (§1.1). Figures
only.

#### 2.5.3 Group selection — the exact columns

```python
# PROPOSALS — data/prepared/{condition}/proposals/{text_version}/proposal_master.csv
human_mask = master_df['source_type'] == 'human'          # n = 23
ai_mask    = master_df['source_type'] == 'ai'             # n = 69
model_mask = master_df[MODEL_COL] == 'claude'             # n = 23 per model
# [VERIFY] MODEL_COL: inspect proposal_master.csv for the AI model column name
#          (likely 'model' / 'ai_model' / 'source_model'). Do NOT guess — assert it exists
#          and that ai_mask splits into exactly 3 models × 23.

# REVIEWS — data/prepared/{condition}/reviews/{text_version}/review_master.csv
human_mask = master_df['review_source'] == 'human'
ai_mask    = master_df['review_source'] == 'ai'
model_mask = master_df['review_model'] == 'claude'        # [VERIFY] name against review_master.csv
target     = master_df['target_proposal_uid']             # the pairing key for §11
```
`4b`'s existing code uses `review_source` (its summary cell counts
`(master_df['review_source'] == 'human').sum()`), so that column name is confirmed. `review_model` and
the proposal-side model column are **inferred — verify both against the actual CSVs before use.**

Row order is frozen by `manifest['proposal_uid_order']` / `manifest['review_uid_order']`. Masks,
subsample indices, and panel indices are all **positional against that order** — assert it first
(§2.4).

#### 2.5.4 Raw bundle vs cached cosine matrix

The cached `*_pairwise_cosine_*.npy` is a **convenience fast path for purely distance-based metrics
only** (M0's distance metrics, M4). Everything else needs the raw vectors.

- **Source of truth = the embedding bundle.** If you use the cached matrix, it must be for speed, and
  `02`/`03` should assert agreement on one group at startup:
  `np.allclose(cached[np.ix_(rows, rows)], cosine_distances(X[rows]), atol=1e-6)`.
- **Do not** attempt to reconstruct the Gram matrix for M1 or the centered Gram for M3 from the cached
  distance matrix. It is algebraically possible for L2-normalized vectors (`X @ X.T = 1 − D`, and
  double-centering recovers `Xc @ Xc.T`), but it is a needless cleverness that silently breaks the
  moment normalization or the metric changes. Load the vectors.
- The RBF kernel (M1 robustness, M5) needs raw vectors regardless.

#### 2.5.5 The grid: every metric runs over every cell

```
condition   ∈ {baseline, one_at_a_time, persona}     # all three, always
text_version ∈ {rephrased, original}                 # rephrased = PRIMARY, original = robustness
task        ∈ {proposals, reviews}                   # 02 and 03 respectively
field       ∈ manifest['fields_available']           # reviews: whole always; strengths/weakness rephrased-only
comparison  ∈ {human_vs_claude, human_vs_gemini, human_vs_gpt, human_vs_pooled_ai}
```
`rephrased` is primary because it is style-controlled; `original` is the robustness branch confirming
the effect is not a prose-style artifact (§1.9). Both are computed and both are reported — the
distinction is which one the manuscript headlines, not which one is run.

---

## 3. M0 — Spread / dispersion · facet: SPREAD

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl`; reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl` (+ `strengths`/`weakness` where `fields_available` allows). `centroid_loo` and `spherical_variance` **need raw vectors**; the distance-based four may use the cached `*_pairwise_cosine_*.npy` fast path. Reviews additionally load `review_panels_exact_n.pkl`.

**Facet 1. Confirmatory.** The most direct sense of narrowing: *ideas and reviews grow closer and
more similar to one another.* This is the facet the hypothesis states in plain language, and
`mean_pairwise` is the number the abstract will quote.

**Why several metrics for one facet:** spread can be measured from the pairwise distances, from the
centroid, from the connectivity structure, or from the vector mean. These are alternative views of
the same underlying scale, so they should **co-vary** — and demonstrating that they do is what
licenses collapsing them into one facet in the manuscript (§3.4). Report `mean_pairwise` as primary;
the rest as convergent support. **Do not report them as six separate findings.**

### 3.1 Compute
```python
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import minimum_spanning_tree

def mean_pairwise(X, metric="cosine"):
    """PRIMARY. Mean of the upper-triangle pairwise distances."""
    return float(pdist(X, metric=metric).mean())

def centroid_dispersion_loo(X):
    """Leave-one-out centroid dispersion: mean Euclidean distance from each point to the
    centroid of the OTHER points. LOO avoids each point pulling its own reference."""
    n = len(X)
    out = np.empty(n)
    for i in range(n):
        c = np.delete(X, i, axis=0).mean(axis=0)      # do NOT re-normalize (see §1.2)
        out[i] = np.linalg.norm(X[i] - c)
    return float(out.mean())

def mst_dispersion(X):
    """Mean edge length of the minimum spanning tree over the cosine distance graph.
    Captures how broadly a set covers a CONNECTED region rather than raw scatter."""
    D = squareform(pdist(X, metric="cosine"))
    T = minimum_spanning_tree(D)                      # scipy returns a sparse upper-tri tree
    edges = T.toarray()
    w = edges[edges > 0]
    return float(w.sum() / (len(X) - 1))              # mean edge weight; n-1 edges

def sparseness(X):
    """Mean cosine distance from every point to the set's medoid (the most central actual
    member). Robust to the centroid being a non-datapoint."""
    D = squareform(pdist(X, metric="cosine"))
    medoid = int(np.argmin(D.sum(axis=1)))
    return float(np.delete(D[medoid], medoid).mean())

def nn_isolation(X):
    """Mean nearest-neighbor cosine distance. NOTE: the SCALAR is a spread metric; the
    DISTRIBUTION of NN distances belongs to M4/evenness. Do not double-count (§3.6)."""
    D = squareform(pdist(X, metric="cosine")); np.fill_diagonal(D, np.inf)
    return float(D.min(axis=1).mean())

def spherical_variance(X):
    """1 - ||mean resultant vector||. Classic directional-statistics dispersion measure
    (Mardia & Jupp). For unit vectors: 0 = all identical, 1 = maximally dispersed.
    Cheap, assumption-light, and a natural fit for L2-normalized embeddings."""
    return float(1.0 - np.linalg.norm(X.mean(axis=0)))
```

Notes for the agent:
- All six operate on the same L2-normalized `X`; `mean_pairwise`, `mst_dispersion`, `sparseness`,
  `nn_isolation` can reuse the cached cosine matrix (§2.4) sliced to the group's rows.
- `centroid_dispersion_loo` and `spherical_variance` need the raw vectors.
- `spherical_variance` is a **new addition** vs. the old pipeline — it's the directional-statistics
  analog of variance and pairs naturally with normalized embeddings. Cite Mardia & Jupp,
  *Directional Statistics*. [CHECK: optional — drop it if you want strict continuity with the
  metrics already reported in earlier drafts.]

### 3.2 Effect size + significance
- **Effect size:** ratio `M0(Human) / M0(group)` — "human proposals sit X× farther apart on average."
  Also report the raw difference for `mean_pairwise` since it's in interpretable cosine units.
- **Significance:** `label_permutation_test(..., mode="within_diff")` on each metric, B = 10,000.
  Primary test = `mean_pairwise`; the other five are reported with FDR correction as convergent
  (§1.7).
- **CIs:** `jackknife_ci` over the 23 rows.
- **Pooled Human vs All-AI:** `subsample_pooled` (§1.5) → 1000-value distribution vs the Human scalar.
- **Gradient:** `jonckheere_terpstra` on jackknife replicates of `mean_pairwise` across
  {Claude, Gemini, GPT, Human}, predicted increasing.
- **Reviews:** per-proposal panel values → `paired_wilcoxon` (§11.3). Not permutation.

### 3.3 Visualization
1. **Pooled subsample distribution (headline, per condition).** Histogram + KDE of the 1000 pooled-AI
   `mean_pairwise` subsample values, with the Human value as a vertical rule and the AI 95% interval
   shaded. This is the cleanest single-panel statement of the spread facet.
2. **Full pairwise-distance distributions (ridgeline / half-violin), one row per group.** Given
   confirmed bimodality in some groups, **do not** show only the mean — the distribution of all
   pairwise distances per group shows *how* the spread is composed (one blob vs. two). This panel is
   what a mean cannot say.
3. **Per-model comparison:** boxplot + mean-CI of `mean_pairwise` per group, per condition.
4. **Convergence panel (required, §3.4):** correlation heatmap across the six M0 metrics.

### 3.4 The convergence panel is not optional
The manuscript claims these six metrics are **one facet**. That claim needs evidence. Compute the
Spearman correlation matrix across the six M0 metrics (over all groups × conditions × text_versions) and
show it as a heatmap. Expected: uniformly high positive correlation → they are alternative views of
one construct → collapsing them to one facet with `mean_pairwise` as primary is justified.
**Then extend the same panel across facets** (M0 vs M1 vs M2 vs M3 vs M4): the off-block correlations
should be *markedly lower*, demonstrating the facets are non-redundant. This one figure defends both
the collapse *and* the multi-facet design, and pre-empts the "you measured one thing six times"
critique that the old draft invited.

### 3.5 Interpretation
Low `mean_pairwise` = ideas sit closer together = less diverse in the plainest sense. The ratio is
directly quotable ("human proposals are 1.4× more separated on average").

**The essential caveat — state it in the manuscript, don't let a reviewer find it:** spread is
*necessary but not sufficient*. A set can have **high** mean pairwise distance while being clumpy,
repetitive, and low-dimensional — the classic "two tight blobs far apart" pathology, which averages
to a large distance while containing only two distinct ideas. This is precisely why M1 (richness),
M4 (evenness), and M3 (dimensionality) exist. M0 is the facet the hypothesis names; M1–M4 are the
facets that make the finding hold up. Report M0 first and the others as the reason to believe it.

### 3.6 Cross-metric bookkeeping
- `nn_isolation` (scalar) → `facet="spread"`. The NN-distance **CDF/G-function** → `facet="evenness"`
  (M4). Same underlying quantity, two facets, **different statistics** — the scalar mean and the
  distribution shape. Emit each once; do not double-count the scalar under evenness.
- `centroid_dispersion_loo` measures spread about the group's *own* centroid. A distance to the
  *global* (all-groups) centroid is **not** a spread metric — it is a displacement flavor. If you
  want it, tag it `facet="displacement"`, `metric="global_centroid_dist"`, and treat it as a crude
  companion to M5 (§8), not as M0.

---

## 4. M1 — Vendi diversity profile · facet: RICHNESS (+ EVENNESS via slope)

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl`; reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl` + `review_panels_exact_n.pkl`. **Raw vectors required** (Gram matrix). Do not reconstruct the Gram from the cached distance matrix (§2.5.4).

**Headline.** Directly answers "distances can't see repetition."

### 4.1 Compute
```python
def vendi_scores(X, qs, kernel="cosine", sigma=None):
    n = X.shape[0]
    if kernel == "cosine":
        K = X @ X.T                       # PSD Gram, K_ii ≈ 1 for normalized X
    else:  # rbf
        D2 = pairwise_sq_euclidean(X)     # = 2 - 2*cos for normalized X
        K = np.exp(-D2 / (2 * sigma**2))
    Kn = K / n                            # trace(Kn) = 1
    w = np.linalg.eigvalsh(Kn)
    w = w[w > 1e-12]
    out = {}
    for q in qs:
        if q == 1:
            out[q] = float(np.exp(-np.sum(w * np.log(w))))          # exp(Shannon entropy)
        elif np.isinf(q):
            out[q] = float(1.0 / np.max(w))
        else:
            out[q] = float((np.sum(w**q))**(1.0/(1.0-q)))
    return out
```
- Primary kernel = cosine (no bandwidth). RBF is the robustness check at σ =
  {0.5, 1, 2} × median pairwise distance; report that conclusions do not flip.
- `VS_q` = similarity-sensitive Hill number of order q on the kernel eigen-spectrum (eigenvalues act
  as "latent-mode abundances"). Cites: Leinster & Cobbold 2012; Chao et al. 2014 (ecology);
  Friedman & Dieng 2023, Pasarkar & Dieng 2024 (Vendi).

### 4.2 The evenness slope (derived, feeds Facet 2)
```python
def vendi_slope(vs):
    """Evenness statistic: relative drop from q=0 to q=2.
    Steep drop => a few dominant modes carry the mass => low evenness => repetition."""
    return float((vs[0] - vs[2]) / vs[0])
```
Emit as a separate row: `facet="evenness"`, `metric="vendi_slope"`. This is how M1 contributes to
Facet 2 alongside M4.

### 4.3 Effect size + significance
- Effect size at each q: ratio `VS_q(Human) / VS_q(group)` = "humans produce X× more
  effectively-distinct items."
- Significance: `label_permutation_test` at q ∈ {0, 1, 2}. Headline at q=1.
- Gradient: `jonckheere_terpstra` on jackknife replicates of `VS_1`.
- CIs: `jackknife_ci`.

### 4.4 Visualization
- **(a) Diversity profile:** x = q, y = `VS_q`, one line per group + jackknife CI ribbon.
  Signature: Human on top and *flat*; AI lines *drop faster* as q rises.
- **(b) Eigenvalue scree** per group (sorted normalized eigenvalues), shared axes: AI = few tall
  eigenvalues then a cliff; Human = flatter. Often the single most persuasive panel.
- Standard boxplot/mean-CI grammar for the per-condition q=1 comparison.

### 4.5 Interpretation
`VS_1 = 5` at n=23 ⇒ "these 23 items are as diverse as 5 fully independent ones." The *slope* over q
is the payload: steep q=0→2 drop ⇒ few dominant modes ⇒ low evenness ⇒ repetition. Flat profile ⇒
genuinely distinct items. This is exactly the clumping M0 averages away.

---

## 5. M2 — Coverage / density vs human reference · facet: COVERAGE (geometric)

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl`, split by `source_type` (`X_ref` = the 23 Human rows, `X_gen` = the 23 rows of one model, or a subsample row from `subsample_idx_ai_n23_seed42.npy` for pooled). Reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl` + `review_panels_exact_n.pkl`, per-proposal (`X_ref` = that proposal's human panel). **Raw vectors required.**

**Directional. Headline.** Use the **density & coverage** estimator (Naeem et al. 2020) — more
outlier/small-n robust than Kynkäänniemi et al. 2019 precision/recall. At n=23 that matters.

### 5.1 Compute
```python
def coverage_density(X_ref, X_gen, k=3):
    # X_ref = Human (reference manifold), X_gen = candidate model group
    Dref = cosine_dist(X_ref, X_ref); np.fill_diagonal(Dref, np.inf)
    radius = np.sort(Dref, axis=1)[:, k-1]           # k-th NN radius per ref point
    Dcross = cosine_dist(X_ref, X_gen)               # (n_ref, n_gen)
    inside = Dcross < radius[:, None]
    coverage = float(np.mean(inside.any(axis=1)))    # frac of ref manifold reached
    density  = float(inside.sum() / (k * X_gen.shape[0]))  # ~precision, on-manifold-ness
    return {"coverage": coverage, "density": density}
```
- `k=3` default; sweep {2, 3, 5} and report ordinal stability.
- **coverage** ∈ [0,1] = fraction of human manifold reached → the narrowing number.
- **density** ≈ precision = whether AI points land inside human-plausible space.
- Do **not** use convex-hull volume as coverage — meaningless at d≈768 (hull dominated by outliers).

### 5.2 Reference baseline (replaces permutation; coverage is asymmetric)
`split_half_reference(X_human, ...)`: coverage of one random human half by the other, ×1000. This is
the null band — what coverage looks like when both sets are genuinely human at this n. A model
narrows iff its coverage sits **below** the band. Empirical p = fraction of split-half values ≤
observed model coverage.
- Pooled AI: coverage of Human by each of the 1000 subsampled-23 AI sets (§1.5).
- Optional third handle: authenticity (Alaa et al. 2022) flags memorization/near-duplication —
  complements M4.

### 5.3 Effect size + significance
- Effect size = coverage itself ("AI recovers X% of the human proposal space") — the cleanest
  one-number compression statistic. Report `coverage` and `1 − coverage` (= the human space AI never
  reaches).
- Significance = position relative to the split-half band.
- Gradient: JT on per-model coverage. Report k-sensitivity; treat as robust *ordinally*.

### 5.4 Visualization
- **Density–coverage scatter:** x = coverage, y = density; one marker per model + the human
  split-half point (near (1,1)) + subsample CI ellipses. Expected: AI pulled **left** (low coverage)
  while staying **high** on density.
- Optional literature-anchored UMAP outlining the human region with AI points inside it —
  illustration only.

### 5.5 Interpretation
**High density + low coverage** is the fingerprint of the hypothesis: AI stays in a central,
human-plausible subregion (competent, on-manifold) but fails to reach the periphery humans explore
(narrow). Low coverage = idea-space regions AI never proposes at all.

---

## 6. M3 — Participation ratio · facet: DIMENSIONALITY

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl`; reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl` + `review_panels_exact_n.pkl`. **Raw vectors required** (centered Gram).

### 6.1 Compute
```python
def participation_ratio(X):
    Xc = X - X.mean(0)
    w = np.linalg.eigvalsh(Xc @ Xc.T)   # Gram trick: n<<d, nonzero spectrum = covariance spectrum
    w = w[w > 1e-12]
    return float((w.sum())**2 / (w**2).sum())

def effective_rank(X):
    Xc = X - X.mean(0)
    w = np.linalg.eigvalsh(Xc @ Xc.T); w = w[w > 1e-12]; p = w / w.sum()
    return float(np.exp(-(p*np.log(p)).sum()))
```
- After centering, rank ≤ n−1 = 22, so `PR ≤ 22` for all groups — fine at equal n.
- Report `effective_rank` too; agreement ⇒ not a definition artifact. Cite Del Giudice 2021.

### 6.2 Effect size + significance
Effect size = PR ratio/difference ("AI varies along ~3 effective axes vs ~8 for humans").
Significance: `label_permutation_test` on ΔPR. CI: jackknife. Gradient: JT.

### 6.3 Visualization
Overlaid **cumulative-variance / scree** curves per group (AI shoots up fast: 90% var in 2–3 PCs;
Human gradual) + a PR bar chart with CIs.

### 6.4 Interpretation
Low PR = variation is essentially 1–2 dimensional. A *different* collapse from M1:
high-Vendi/low-PR = many distinct points strung along one axis; low-Vendi/high-PR = few points across
many axes. Reporting both says *which kind* of narrowing AI shows — a mechanistic claim.

---

## 7. M4 — Ripley-K / G-function in embedding space · facet: EVENNESS (local repetition)

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl` (or the cached `proposal_pairwise_cosine_full.npy` fast path); reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl` + `review_panels_exact_n.pkl`. The pooled-cloud null (§7.2) draws from **all groups' rows in the same bundle**.

**Do NOT use textbook analytic Ripley K** (assumes 2-D/3-D domain, analytic edge correction,
Poisson-CSR baseline — none transfer to d≈768). Use the resampling-null form.

### 7.1 Compute
```python
def nn_distances(X, metric="cosine"):
    D = cosine_dist(X, X); np.fill_diagonal(D, np.inf)
    return D.min(axis=1)

def g_function(X, radii):                 # NN-distance CDF
    nnd = nn_distances(X)
    return np.array([(nnd <= r).mean() for r in radii])

def ripley_K(X, radii):                   # mean neighbor count within r
    D = cosine_dist(X, X); np.fill_diagonal(D, np.inf)
    return np.array([(D < r).sum(axis=1).mean() for r in radii])
```
Radii grid = quantiles of the pooled distance distribution (≈20 points, 1st–50th percentile —
small-r is where duplication shows).

### 7.2 Null (resample from the pooled cloud — NOT analytic CSR)
Draw n=23 from the **pooled proposal (or review) cloud across all groups**, M=999×, recompute the
curve. This null preserves the real intrinsic geometry of the embedding space, so the test isolates
*group-specific extra-clumping* rather than rediscovering that embeddings aren't uniform.

### 7.3 Effect size + significance
- **Global envelope test** (Myllymäki et al. 2017) for simultaneous inference over the whole r-range
  → one p-value; avoids pointwise multiple testing.
- Effect size = area between observed curve and null mean over the small-r region (excess short-range
  mass). Gradient: JT on that deviation statistic.

### 7.4 Visualization
- **(a)** `ripley_K(r)` with grey simultaneous null envelope — AI pokes above at small r.
- **(b)** `g_function` overlay (NN-distance CDFs) — most intuitive: AI curves shift **left**.
- **(c)** histogram of nearest-neighbor cosine *similarities* per group.

### 7.5 Interpretation
Excess neighbors at small r / left-shifted NN distances = local repetition and near-duplication — the
UMAP clumps, measured in real space with a significance envelope. Distinguishes "spread out but
locally clumpy" (AI) from "spread out and evenly filled."

---

## 8. M5 — Displacement (MMD² + optimal transport) · directional check (NOT a diversity facet)

> **Inputs (§2.5):** proposals → `data/prepared/{condition}/proposals/{text_version}/``proposal_embeddings_full.pkl`, `X_human` = the 23 Human rows, `X_ai` = one model's 23 rows (or a pooled subsample). Reviews → `data/prepared/{condition}/reviews/{text_version}/``review_embeddings_text.pkl`, **pooled across all proposals per condition — never per-proposal** (§8.5). **Raw vectors required** (RBF kernel + median heuristic).

**What it answers:** M0–M4 measure the *size and shape* of a group's occupied region. Displacement
asks whether the AI region is in a *different place* than the human region, or narrowed toward a
shared central zone. The manuscript makes this claim ("AI narrows *toward a shared region*"), so it
must be computed, not asserted.

**This is a two-sample distance, not a within-group scalar.** There is no "Human value vs AI value"
— the metric *is* the between-group quantity, tested against a label-permutation null directly.

### 8.1 Compute
```python
def mmd2_rbf(X, Y, sigma=None):
    if sigma is None:
        sigma = median_pairwise_distance(np.vstack([X, Y]))
    Kxx = rbf(X, X, sigma); Kyy = rbf(Y, Y, sigma); Kxy = rbf(X, Y, sigma)
    m, n = len(X), len(Y)
    sxx = (Kxx.sum() - np.trace(Kxx)) / (m*(m-1))
    syy = (Kyy.sum() - np.trace(Kyy)) / (n*(n-1))
    sxy = Kxy.mean()
    return float(sxx + syy - 2*sxy)              # unbiased MMD^2; ~0 iff same distribution

def wasserstein_ot(X, Y, metric="cosine"):
    C = cdist(X, Y, metric=metric)
    a = np.ones(len(X))/len(X); b = np.ones(len(Y))/len(Y)
    return float(ot.emd2(a, b, C))               # POT library
```
- Primary: **MMD²**, RBF kernel, median-heuristic bandwidth (Gretton et al. 2012).
- Secondary: **optimal transport** — more interpretable ("average distance to move the AI cloud onto
  the human cloud") but heavier and more n-sensitive. Convergent support, not primary.

### 8.2 Effect size + significance
- Significance: `label_permutation_test(..., mode="two_sample")` — stack the rows, shuffle labels,
  recompute MMD²/OT, B ≥ 10,000. p = fraction of permuted ≥ observed.
- Effect size: MMD² itself; also a normalized MMD²/median-kernel for cross-condition comparability.
- Gradient: JT across per-model Human↔model distances. **Direction flips vs. the diversity facets:**
  larger distance = more shifted, so an increasingly human-like Claude→GPT implies *decreasing*
  distance. State the predicted direction before running JT.

### 8.3 Interpretation — the crucial disambiguation
Displacement must be read **jointly with M2 coverage**:
- **Low coverage + low displacement** = AI sits *inside* the human region but fills less of it →
  "narrowed toward a shared central zone." **This is the manuscript's claim.**
- **Low coverage + high displacement** = AI occupies a *different, smaller* region → narrowed *and*
  shifted (a different, arguably more alarming story).
- **High coverage + high displacement** = comparably large but *elsewhere* → not narrowing.
M5 is never standalone evidence of narrowing; its job is to sharpen M2 from "AI fills less space" to
"AI fills less space *and* stays in the humans' central region." Report the M2+M5 pair together.

### 8.4 Visualization
- **MMD²/OT bar per model** (Human↔Claude/Gemini/GPT/pooled) with permutation null band, plus the
  Human split-half distance as the "same-distribution" floor.
- Optional: the M2 density–coverage scatter with marker *size* encoding displacement — coverage and
  displacement in one panel.

### 8.5 Notes
- Needs POT (`pip install pot`) for OT; MMD² is pure numpy.
- At 23 vs 23, MMD² is low-powered. Report honestly as "consistent with" rather than a sharp test;
  lean on the pooled subsampled version for the headline number.
- **Reviews:** displacement is **not** computed per-proposal (panels of 2–5 are far too small for a
  two-sample distance). Compute once per condition on the *pooled* review clouds (all human vs all
  AI reviews), clearly labeled unpaired and exploratory. Never present it as a paired result.

---

## 9. M6 — Domain coverage (BERTopic regions + MeSH) · facet: COVERAGE (domain half)

> **Inputs (§2.5):** `data/prepared/{condition}/proposals/{text_version}/``proposal_to_literature_knn.npz` (k=50, slice `[:, :k]`, derived from `abstract_text`) **+** `data/prepared/literature/lit_bertopic_assignments.csv` (topic id per article) **+** `data/prepared/literature/lit_bertopic_topic_info.csv` (for `n_regions_excl_outlier`) **+** `data/prepared/literature/literature_mesh_index.parquet`. Pooled comparisons additionally need `subsample_idx_ai_n23_seed42.npy` (§9.3 — union metrics are the most n-sensitive in the spec). No proposal embeddings are loaded directly.

**Proposals only.** Reviews are not projected onto the literature. This is the *interpretable* half
of Facet 5: geometric coverage (M2) says *how much* of the human space AI occupies; M6 says *which
areas of biomedical science* AI under-explores — the panel a domain reviewer will actually care about.

> **[RESOLVED — M6 is cheap to keep]** Earlier drafts debated whether the domain half of Facet 5
> needed its own prep stage. It doesn't: **`4a` already builds the entire literature map** (PubMed
> corpus → embeddings → BERTopic → topic assignments → proposal-to-literature KNN at k=50). M6 is
> therefore mostly *consumption* of artifacts that already exist, and the only prep additions are the
> MeSH index and the BERTopic gate (prep spec §2.3, §2.4). If you still want to defer M6, drop §9 and
> set `M6_REQUIRED = False` in `4a`; the rest of the spec stands and the coverage facet becomes
> geometric-only.

### 9.1 Prep — built by `4a` cell 3 (runs once, not per condition)
**`4a` already does all of this** via `src/prepare_literature_assets.py`
(`load_literature_corpus` → `build_or_load_literature_embeddings` → `fit_or_load_literature_bertopic`
→ `fit_or_load_literature_umap`), hashed and cached. Do not build a separate literature notebook.
The steps below document what must be true, not new work to write — except the MeSH index and the
BERTopic gate (prep spec §2.3, §2.4):
1. Load the PubMed corpus (39,538 abstracts, 2010-01-01 → 2026-05-25).
2. Embed with the same encoder as proposals (BioLinkBERT-large), L2-normalize.
3. Fit **BERTopic** on the literature embeddings → topic regions. Persist the fitted model, the topic
   assignment per abstract, and `n_regions_total`.
4. Build a MeSH index: abstract → set of MeSH descriptors.
5. Cache: `data/cache/literature/{lit_embeddings.npy, bertopic_model/, topic_ids.npy, mesh_index.parquet}`.

**The literature map is fitted once and frozen.** Every condition/text_version/group projects onto the same
fixed map. Never refit BERTopic per group — that would make regions incomparable across groups and
silently invalidate every comparison.

### 9.2 Compute (per proposal group)
```python
def project_to_literature(X_group, lit_embeddings, topic_ids, mesh_index, k=10):
    """For each proposal, find its k nearest literature abstracts; collect their topic
    regions and MeSH terms. Returns per-proposal topic ids and MeSH sets."""
    D = cosine_dist(X_group, lit_embeddings)         # (n_group, 39538)
    nn = np.argsort(D, axis=1)[:, :k]
    topics_per_prop = [set(topic_ids[row]) for row in nn]
    mesh_per_prop   = [set().union(*(mesh_index[i] for i in row)) for row in nn]
    return topics_per_prop, mesh_per_prop

def region_coverage(topics_per_prop, n_regions_total):
    """Union of distinct topic regions the group collectively touches."""
    union = set().union(*topics_per_prop)
    return {"n_regions": len(union), "frac_regions": len(union) / n_regions_total}

def mesh_coverage(mesh_per_prop):
    """Union of unique MeSH descriptors across the group."""
    union = set().union(*mesh_per_prop)
    return {"n_mesh": len(union)}
```
- `k=10` literature neighbors default; sweep {5, 10, 20} as a sensitivity check. **`4a` caches
  `k=50`** (`proposal_to_literature_knn.npz`) — a superset. Slice `[:, :k]` downstream; this is a
  *downstream* parameter, not a prep one. The KNN is built from `abstract_text` while M0–M5 use
  `full_text` — defensible (abstracts match PubMed abstracts), but state it in Methods.
- Tag rows: `facet="coverage"`, `metric ∈ {"coverage_bertopic_region", "coverage_mesh_terms"}`.

### 9.3 Effect size + significance — **the n-sensitivity trap**
These are **union/count** metrics: they are monotonically non-decreasing in n and grow sub-linearly.
This makes them the most sample-size-sensitive metrics in the spec.
- **Per-model (23 vs 23):** equal-n, direct. `label_permutation_test`, `mode="within_diff"`.
- **Pooled (23 vs 69): MUST subsample.** Never compare a 23-set's union against a 69-set's union.
  Use `subsample_pooled` (§1.5).
- **Rarefaction curve (strongly recommended):** plot union size vs. number of proposals sampled
  (m = 1…23), averaged over many draws, one curve per group. This is the honest way to present a
  count metric — it shows the whole accumulation, not one n-dependent point, and it is the standard
  presentation in ecology for exactly this problem (Chao et al. 2014). If the human curve sits above
  and is still climbing while AI curves flatten early, that is a *strong* and very legible result.
- Effect size: ratio of union sizes at matched n; or the ratio of rarefaction-curve asymptotes.
- Gradient: JT on per-model `n_regions` at matched n.

### 9.4 Visualization
1. **Rarefaction curves** (union size vs. m), one line per group, CI ribbons. Primary panel.
2. **Region-occupancy heatmap:** topic regions × groups, cell = number of proposals landing in that
   region. Shows *which* regions AI misses — the domain-interpretable payload.
3. **Literature-anchored UMAP** with proposals overlaid on the frozen literature map — illustration
   only (this is the figure you already have; keep it as a figure, not a metric source).

### 9.5 Interpretation
- Geometric coverage low **and** region/MeSH coverage low → AI both fills less of the human region
  *and* engages fewer areas of biomedical science. The strongest narrowing story.
- Geometric low but region/MeSH comparable → AI touches similar *topics* but explores less *within*
  them — narrowing is intra-topic, not topical. A more specific and more interesting claim.
- The region-occupancy heatmap converts an abstract geometric claim into "AI never proposes anything
  in region X" — which is what makes the result land for a biomedical audience.

---

## 10. `02_facets_proposals.ipynb` — proposals (unpaired)

Proposals are **unpaired**. Inference unit = the proposal set. Free-permutation regime.

### 10.1 Grid
Loop over `condition × text_version` (§1.10). Within each cell:
1. **Per-model** (Human 23 vs Claude/Gemini/GPT 23): M0–M6, equal-n, direct.
   - M0, M1, M3, M4, M6 → label permutation (`within_diff`)
   - M2 → split-half human reference
   - M5 → label permutation (`two_sample`)
2. **Pooled Human vs All-AI** (23 vs 69 → subsample 23): every metric via `subsample_pooled`.
   **M6 must go through this path** (§9.3).
3. **Gradient:** JT across {Claude, Gemini, GPT, Human} per metric.
4. **Cross-condition:** stack pooled results across baseline / one_at_a_time / persona → does
   narrowing change across conditions? Report each metric's AI÷Human diversity-retained ratio per
   condition. *(This is the persona-persistence claim — the manuscript's punchline.)*

### 10.2 Notebook section order
```
## Config                    (the CONFIG dict, §1.10)
## Load                      (§2.5 — proposal_master.csv, proposal_embeddings_full.pkl,
##                            proposal_to_literature_knn.npz, subsample_idx_ai_n23_seed42.npy,
##                            literature map from data/prepared/literature/;
##                            assert manifest uid-order + l2_normalized first, §2.4)
## M0 Spread
## M1 Richness
## M2 Coverage (geometric)
## M3 Dimensionality
## M4 Evenness
## M5 Displacement
## M6 Coverage (domain)
## Facet Convergence Panel   (§3.4 — within-M0 and across-facet correlation heatmaps)
## Gradient Tests
## Cross-condition Ratios
## Figures                   (§12.7 inventory; grammar §1A; read from the tidy tables/curves only)
## Export                    (tidy rows → results/tables/{condition}/{task}/{text_version}/, §12.5;
##                            figures → results/figures/{condition}/{task}/{text_version}/, §12.6)
```
Each metric section computes and appends tidy rows; **no section plots from in-memory objects**. The
`## Figures` section runs last and reads only `facet_diversity_tests.csv` and
`facet_diversity_curves.parquet`, so any figure can be regenerated without re-running the metrics.

### 10.3 Text text_versions
`text_version ∈ {rephrased, original}` is a **config parameter**, not a separate notebook. `rephrased` is
primary (style-controlled); `original` is the robustness check. Both write rows into the same tables,
distinguished by the `text_version` column.

---

## 11. `03_facets_reviews.ipynb` — reviews (paired, nested)

Reviews are **nested**: each human proposal has 2–5 human reviews and 5 AI reviews per model per
condition (a 15-review AI reservoir per proposal per condition). Pooling all reviews confounds
"reviews of *different* proposals differ" with "reviews of the *same* proposal differ." **Only the
second is filtering diversity.** So facet metrics run **per target proposal**, then aggregate with a
**paired** test.

### 11.1 Exact-n panel construction (`src/panels.py`, cached by `4b` — prep spec §3.2)
For each target human proposal p with `m = n_human_reviews(p)`, m ∈ [2, 5]:
- **Human panel** = the m human reviews of p.
- **Per-model AI panel** = choose m of that model's 5 reviews of p → enumerate all C(5, m) panels.
- **Pooled AI panel** = choose m of the 15 reviews of p → C(15, m) panels (cap by sampling if large).
Enumerated AI panels are **computational artifacts, not inferential n**. Summarize each proposal's AI
value as the **mean over enumerated panels**.

### 11.2 Per-proposal facet metrics
For each proposal p and each metric M ∈ {M0, M1, M3, M4}:
```
human_val[p] = M(human_panel_embeddings)
ai_val[p]    = mean over enumerated AI panels of M(panel_embeddings)
```
Small panels (m = 2–5) make any single proposal's value noisy — expected. The signal is the **paired
difference across 23 proposals**, not any one proposal.

**M2 (coverage) for reviews:** reference = the m human reviews of p; candidate = the AI panel for p.
`coverage[p]` = fraction of the human review span reached by AI reviews *of the same proposal* — the
cleanest "AI reviews converge more" statistic.
> **[CHECK — k vs m]** `coverage_density` needs `k < m`. For m=2 proposals you must either fall back
> to k=1 or restrict M2-reviews to the m≥3 subset. Decide once and state it: the m≥3 subset is
> cleaner; k=1 across all keeps full n but is noisier. Your Y2 cohort (2–4 reviews) is most affected.

**M5 (displacement) for reviews:** not per-proposal (§8.5) — pooled per condition, exploratory only.
**M6:** not applicable to reviews.

### 11.3 Aggregate inference — PAIRED
- **Primary test:** `paired_wilcoxon` across the 23 proposals, pairing `human_val[p]` vs `ai_val[p]`.
  **Not** label permutation — the review inferential unit is the proposal.
- Effect size: paired Cliff's δ / matched-pairs rank-biserial.
- Per-model: paired Human-vs-Claude / Gemini / GPT. Pooled: paired Human-vs-All-AI.
- Gradient: JT across per-model paired differences.
- Cross-condition: stack paired results across the three conditions.

The claim this supports, precisely: **given the same proposal, AI reviews converge more than human
reviews do** — the filtering half of double compression.

### 11.4 Fields
`field ∈ {whole, strengths, weakness}` is a **config parameter** (§1.10). `whole` is primary;
strengths/weakness are secondary field-specific analyses. All three write into the same tables via
the `field` column — no cloned notebook.

### 11.5 Visualization
- **Paired-slope** figure per confirmatory metric (human value → AI value, one line per proposal).
- Per-proposal M1 profile small-multiples (optional).
- Review-space UMAP — illustration only.

### 11.6 Notebook section order
Mirrors §10.2, minus M6, with `## Panels` after `## Load` and paired tests throughout.

---

## 12. Results schema

Two headline CSVs + one curves parquet. Everything downstream (including `04`) reads only these.

### 12.1 `facet_diversity_tests.csv`
One row per (condition, task, text_version, field, comparison, facet, metric, param).

| column | type | notes |
|--------|------|-------|
| `condition` | str | baseline / one_at_a_time / persona |
| `task` | str | proposals / reviews |
| `text_version` | str | rephrased (primary) / original |
| `field` | str | whole / strengths / weakness (reviews); whole (proposals) |
| `comparison` | str | human_vs_claude / _gemini / _gpt / _pooled_ai |
| `facet` | str | spread / evenness / richness / dimensionality / coverage / displacement |
| `metric` | str | mean_pairwise / centroid_loo / mst_dispersion / sparseness / nn_isolation / spherical_variance / vendi / vendi_slope / coverage_geometric / participation_ratio / effective_rank / ripley_excess / mmd2 / ot_wasserstein / coverage_bertopic_region / coverage_mesh_terms |
| `is_primary` | bool | true for the facet's primary metric (mean_pairwise, vendi q=1, coverage_geometric, PR, ripley_excess, mmd2) |
| `param` | str | `q=1`, `k=3`, `kernel=cosine`, `k_lit=10`; empty if n/a |
| `human_value` | float | point estimate, Human. **M5: NULL** (two-sample) |
| `ai_value` | float | point estimate, AI (subsample mean if pooled). **M5: NULL** |
| `effect_size` | float | ratio (M0/M1/M3/M6) / coverage (M2) / envelope-area (M4) / MMD² or OT (M5) / Cliff's δ (reviews) |
| `effect_type` | str | ratio / diff / coverage / envelope_area / two_sample_distance / cliffs_delta |
| `ci_lo` `ci_hi` | float | 95% (jackknife / subsample / paired / permutation for M5) |
| `inference` | str | permutation / two_sample_permutation / split_half_reference / paired_wilcoxon / global_envelope |
| `stat` | float | permutation Δ / W / envelope stat / **M5: the distance itself** |
| `p_raw` | float | primary p |
| `p_fdr` | float | BH within (task, text_version, field) |
| `n_human` `n_ai` | int | equal-n check; reviews: mean panel size |
| `n_perm_or_sub` | int | B |
| `notes` | str | k-sensitivity, RBF check, M5 direction convention |

**M5 is the one exception to the human/ai layout:** no per-group value; the distance lives in `stat`
and `effect_size`; `04` skips it when computing ratios.

### 12.2 `facet_diversity_gradient.csv`
| column | notes |
|---|---|
| `condition` `task` `text_version` `field` `facet` `metric` `param` | keys |
| `order` | `claude<gemini<gpt<human` (or the M5-flipped order) |
| `JT` `p_raw` `p_fdr` | trend test |
| `direction_ok` | bool — observed order matches predicted |

### 12.3 `facet_diversity_curves.parquet`
Long form: (condition, task, text_version, field, group, facet, metric, x, y, y_lo, y_hi) where `x` = q
(M1 profile), eigen-index (scree), radius r (M4), or m (M6 rarefaction). One file feeds every curve
figure.

### 12.4 Reviews paired detail
`facet_review_paired_long.csv`: (condition, text_version, field, comparison, facet, metric, param,
proposal_uid, cohort, n_human_reviews, human_value, ai_value, paired_diff) — backs the paired-slope
figures.

### 12.5 File layout — tables

Every output is categorized by `{condition}/{task}/{text_version}`. No output lands in a
notebook-local or ad-hoc directory.

```
results/tables/{condition}/{task}/{text_version}/facet_diversity_tests.csv
results/tables/{condition}/{task}/{text_version}/facet_diversity_gradient.csv
results/tables/{condition}/{task}/{text_version}/facet_diversity_curves.parquet
results/tables/{condition}/reviews/{text_version}/facet_review_paired_long.csv
results/tables/cross_condition/{task}/{text_version}/facet_diversity_tests.csv
results/tables/synthesis/{text_version}/double_compression_summary.csv
```
where `condition ∈ {baseline, one_at_a_time, persona}`, `task ∈ {proposals, reviews}`,
`text_version ∈ {rephrased, original}`.

### 12.6 File layout — figures

```
results/figures/{condition}/{task}/{text_version}/{facet}_{metric}_{view}.{png,pdf}
results/figures/{condition}/{task}/{text_version}/_convergence/facet_convergence_heatmap.{png,pdf}
results/figures/cross_condition/{task}/{text_version}/{facet}_{metric}_{view}.{png,pdf}
results/figures/synthesis/{text_version}/fig{N}_{name}.{png,pdf}
```

**Filename convention:** `{facet}_{metric}_{view}` — lowercase, snake_case, no spaces.
`view ∈ {box, ridge, hist, profile, scree, envelope, cdf, scatter, heatmap, rarefaction, bar,
paired_slope, effect}`.

Examples:
```
results/figures/persona/proposals/rephrased/spread_mean_pairwise_box.png
results/figures/persona/proposals/rephrased/spread_mean_pairwise_ridge.png
results/figures/persona/proposals/rephrased/richness_vendi_profile.png
results/figures/persona/proposals/rephrased/richness_vendi_scree.png
results/figures/persona/proposals/rephrased/coverage_geometric_scatter.png
results/figures/persona/proposals/rephrased/coverage_bertopic_region_rarefaction.png
results/figures/persona/proposals/rephrased/coverage_bertopic_region_heatmap.png
results/figures/persona/proposals/rephrased/evenness_ripley_envelope.png
results/figures/persona/proposals/rephrased/evenness_g_function_cdf.png
results/figures/persona/proposals/rephrased/dimensionality_participation_ratio_box.png
results/figures/persona/proposals/rephrased/displacement_mmd2_bar.png
results/figures/persona/reviews/rephrased/richness_vendi_paired_slope.png
results/figures/synthesis/rephrased/fig1_double_compression_slopegraph.pdf
```

### 12.7 Required figure inventory

`02`/`03` must emit **every** row below for every (condition, task, text_version) in the grid. A
missing figure is a build failure, not an omission. Titles follow §1A.10
(`{Facet} — {metric} · {condition} · {task}/{text_version}`).

| Facet | Metric | Views required | Notebook | §  |
|---|---|---|---|---|
| spread | `mean_pairwise` | `box`, **`ridge`** (required — bimodality), `effect` | 02, 03 | §3.3 |
| spread | convergent (`centroid_loo`, `mst_dispersion`, `sparseness`, `nn_isolation`, `spherical_variance`) | `box` (dodged, one panel) | 02, 03 | §3.3 |
| — | *(all M0 metrics)* | **`facet_convergence_heatmap`** (required) | 02 | §3.4, §1A.7 |
| richness | `vendi` | `profile`, `scree`, `box` (q=1), `effect` | 02, 03 | §4.4 |
| evenness | `ripley_excess` | `envelope`, `cdf` (G-function), `hist` (NN sims) | 02, 03 | §7.4 |
| evenness | `vendi_slope` | `box` | 02, 03 | §4.2 |
| dimensionality | `participation_ratio` | `scree` (cumulative variance), `box`, `effect` | 02, 03 | §6.3 |
| coverage | `coverage_geometric` | `scatter` (density–coverage), `box`, `effect` | 02, 03 | §5.4 |
| coverage | `coverage_bertopic_region` | **`rarefaction`** (primary), `heatmap` (region occupancy) | 02 | §9.4 |
| coverage | `coverage_mesh_terms` | `rarefaction` | 02 | §9.4 |
| displacement | `mmd2` | `bar` (with permutation null band) | 02, 03 | §8.4 |
| *(reviews, per facet)* | primary metrics | **`paired_slope`** | 03 | §11.5 |
| *(illustration)* | — | proposal-space UMAP, review-space UMAP, literature-anchored UMAP | 02, 03 | §1A.8 |

`04_synthesis` emits exactly the five figures in §15.8, no more:
`fig1_double_compression_slopegraph`, `fig2_compression_map`, `fig3_robustness_grid`,
`fig4_paired_umaps_{condition}`, `fig5_condition_gradient`.

**Cross-condition figures** (`results/figures/cross_condition/...`) carry the AI÷Human
diversity-retained ratio per condition for each primary metric — the persona-persistence panel.

---

## 13. Build order

1. `src/diversity_facets.py` — M0–M6 pure functions + unit tests on toy data:
   3 tight clusters vs. uniform-on-sphere ⇒ assert Vendi collapses, PR low, coverage low, G-curve
   left-shifted, `mean_pairwise` **not necessarily** lower (this last assertion is the point of the
   whole multi-facet design — it proves M0 alone is insufficient and the test should encode that).
2. `src/diversity_inference.py` — permutation (both modes), jackknife, subsample, split-half, JT,
   paired Wilcoxon, BH, global envelope.
3. `src/panels.py`, `src/data_io.py`, `src/plotting.py`.
4. **Modify `4a`** — L2-normalization + manifest flag, subsample cache, BERTopic gate,
   `n_regions_total`, MeSH index (prep spec §2).
5. **Modify `4b`** — L2-normalization, exact-n panel enumeration, `fields_available`, roster
   assertion (prep spec §3).
6. Re-run `4a` then `4b` with `REUSE_EXISTING_ARTIFACTS = True` (normalization is a re-save, **not**
   a re-embed — never force a rebuild of the 39,538-abstract corpus).
7. `02_facets_proposals.ipynb` — full grid.
8. `03_facets_reviews.ipynb` — full grid, paired.
9. `04_synthesis.ipynb` — figures from tidy tables only.

---

## 14. Sanity checks the agent must assert

- All metrics on L2-normalized full-D embeddings; **no UMAP/PCA coords in any metric.**
- Every cross-group absolute comparison is equal-n (per-model direct; pooled via subsample).
- **M6 union metrics never compared at unequal n** (the easiest mistake in the whole spec).
- Reviews use paired Wilcoxon, not label permutation (except M5, pooled/unpaired/exploratory).
- **No with-replacement resampling anywhere.** Subsampling without replacement only.
- Per-model results preserved (never collapse AI into one category) — the gradient depends on it.
- Every emitted row carries a `facet` label and an `is_primary` flag.
- **M5 rows have NULL `human_value`/`ai_value`**; distance in `stat`/`effect_size`; `04` skips them
  in the ratio step.
- **M5 reported jointly with M2** (§8.3) — never standalone evidence of narrowing.
- M0's six metrics reported as **one facet** (primary + convergent), never as six findings; the
  convergence panel (§3.4) must be produced to justify this.
- BERTopic fitted **once** on the literature corpus and frozen; never refit per group.
- Bimodal groups: prefer profile curves + full distributions over point estimates.
- No notebook is a copy of another notebook with a parameter changed (§1.10).
- **`assert manifest['embeddings_l2_normalized'] is True`** on every bundle load — unnormalized
  vectors make M1's Vendi spectrum and M5's bandwidth silently wrong rather than raising.
- **`assert manifest['proposal_uid_order'] / ['review_uid_order']` matches the loaded master** before
  using `subsample_idx_*.npy` or `review_panels_exact_n.pkl` — both store positional indices.
- BERTopic `-1` (outlier) handling identical across every group; the choice recorded in the manifest.
- `field ∈ {strengths, weakness}` attempted only where `manifest['fields_available']` allows
  (rephrased only) — `03` skips, never crashes.
- **No set-level facet metric CI is computed by with-replacement bootstrap** (§1A.1) — jackknife
  (per-model) or subsample (pooled) only. A caption reading "bootstrap 95% CI" on a Vendi/PR/coverage
  panel is a bug, not a wording issue.
- **Every figure caption names its CI method and, for resampling distributions, says what the points
  are** (§1A.0) — jackknife replicates and subsample values are never presented as observations.
- **Every figure title names the facet and the metric** (§1A.10); every panel where group size could
  matter states n, and pooled panels say `AI n=23 subsampled from 69`, never `n=69`.
- **Every figure in the §12.7 inventory exists** for every (condition, task, text_version); paths and
  filenames follow §12.5/§12.6. No figure exists only as notebook output.
- **Curve panels read `facet_diversity_curves.parquet`** — no curve is recomputed in a plotting cell
  (§1A.4).
- Coverage parity lines use the human split-half reference, **not 1.0** (§1A.6).
- **Every metric loads the input named in §2.5.2 — no substitutions.** M0–M5 use `full_text`;
  `abstract_text` appears only in the labelled robustness pass; M6 uses the abstract-derived KNN.
- **`MODEL_COL` (proposals) and `review_model` (reviews) are verified against the actual master CSVs**
  before use (§2.5.3), and `ai_mask` splits into exactly 3 models × 23 proposals.
- **The cached cosine matrix is used only for distance-based metrics** (M0's four, M4), and only after
  the startup `np.allclose` agreement check (§2.5.4). M1/M3/M5 load raw vectors — the Gram is never
  reconstructed from distances.

---

## 15. `04_synthesis.ipynb` — double compression

**Purpose:** the one place showing AI narrowing on *both* ends — generation and filtering — across
the three conditions. A **display and comparison layer, not a new computation.**

### 15.1 Hard rules
- **No metric is recomputed.** Inputs are the finished tidy tables from `02`/`03`. This notebook must
  not import `diversity_facets`.
- **Do NOT pool proposals and reviews into one embedding computation.** Different embedding spaces —
  a raw `coverage=0.4` for proposals ≠ `0.4` for reviews. Only a **normalized** quantity (the
  AI÷Human ratio) goes on a shared axis.
- **Do NOT pool conditions.** Keeping baseline / one_at_a_time / persona separate is what shows the
  persona result — the manuscript's punchline.
- Inference stays where computed: paired-Wilcoxon p's from `03`, permutation p's from `02`. This
  notebook carries them onto figures (stars); it generates no new p-values.

### 15.2 The normalized quantity (single source of truth)
```python
T = pd.concat([...])                       # all facet_diversity_tests.csv
is_ratio = T["facet"] != "displacement"    # M5 has no ratio — excluded
T.loc[is_ratio, "ratio"] = T["ai_value"] / T["human_value"]
T["log2ratio"] = np.log2(T["ratio"])       # symmetric axis; use if any ratio > 1
# parity_ref: 1.0 for all metrics EXCEPT coverage, where parity = median split-half
# human self-coverage (must be emitted by 02/03 — see note below)
```
> **[CHECK]** The coverage parity reference must be exported by `02`/`03` (a column or a `notes`
> entry). Without it `04` has no parity line for the coverage figures. Verify the export includes it.

Join keys pairing generation ↔ filtering: `(condition, text_version, comparison, facet, metric, param)`.

### 15.3 Figure 1 — double-compression slopegraph (headline)
Two anchors per condition panel: `gen` (proposals) left, `filter` (reviews) right; shared y =
diversity retained (AI÷Human). One line per model connecting gen → filter. Three panels
(baseline / one_at_a_time / persona). Parity line at `parity_ref`.
Reads as: below parity = narrowing on that end; downward slope = compression **compounds**; panels
rising toward parity left→right = persona rescue. Primary metric = Vendi q=1; supplement versions for
M0, M2, M3, M4.

### 15.4 Figure 2 — 2×2 compression map
Scatter: x = generation ratio, y = filtering ratio, one point per (model, condition); parity lines
split four quadrants; faint arrows baseline→one_at_a_time→persona per model.
Quadrants: bottom-left = "narrows on both" (the thesis); bottom-right = "generates broadly, filters
narrowly"; top-left = reverse; top-right = no narrowing. Separates the two failure modes the
slopegraph merges.

### 15.5 Figure 3 — robustness grid (facets × tasks)
Rows = {spread, evenness, richness, dimensionality, coverage}; columns = {generation, filtering}.
Each cell: per-model bars of the ratio, grouped by condition, parity line, stars from `p_fdr`.
The reviewer-facing backbone: narrowing holds across *orthogonal* facets on *both* ends.

### 15.6 Figure 4 — paired UMAPs (illustration only)
Proposal-space UMAP | review-space UMAP, human region outlined, AI in an interior subregion.
Caption must say: computed for illustration; all metrics computed in full embedding space.

### 15.7 Figure 5 — cross-condition gradient panel
x = condition (baseline → one_at_a_time → persona), y = pooled AI÷Human ratio, one line per task.
Shows whether persona rescue is stronger for generation or filtering.

### 15.8 Outputs
```
results/figures/synthesis/{text_version}/fig1_double_compression_slopegraph.{png,pdf}
results/figures/synthesis/{text_version}/fig2_compression_map.{png,pdf}
results/figures/synthesis/{text_version}/fig3_robustness_grid.{png,pdf}
results/figures/synthesis/{text_version}/fig4_paired_umaps_{condition}.{png,pdf}
results/figures/synthesis/{text_version}/fig5_condition_gradient.{png,pdf}
results/tables/synthesis/{text_version}/double_compression_summary.csv
```
`double_compression_summary.csv` = `T` + ratio/log2ratio/parity_ref — one tidy table backing every
synthesis figure.

### 15.9 Sanity checks (synthesis)
- No import of `diversity_facets` (must not recompute).
- Every ratio pairs proposals↔reviews on identical join keys.
- Coverage uses `parity_ref` = split-half human baseline, **not** 1.0.
- Conditions never pooled; tasks never merged into a shared embedding.
- Axis mode (linear ratio vs log2) chosen by whether any ratio > 1; stated in the caption.
- M5/displacement excluded from all ratio figures.

---

## 16. Key citations (for Methods)

- **Facet framework:** Hill 1973; Jost 2006; Chao et al. 2014.
- **M0 spread:** Mardia & Jupp, *Directional Statistics* (spherical variance / mean resultant length).
- **M1 richness:** Leinster & Cobbold 2012 (similarity-sensitive diversity); Friedman & Dieng 2023;
  Pasarkar & Dieng 2024 (Vendi, order-q extension).
- **M2 coverage:** Naeem et al. 2020 (density & coverage — primary); Kynkäänniemi et al. 2019
  (improved precision/recall); Sajjadi et al. 2018 (PRD); Alaa et al. 2022 (authenticity).
- **M3 dimensionality:** Del Giudice 2021 (participation ratio).
- **M4 evenness:** Ripley 1977 (K-function); Myllymäki et al. 2017 (global envelope test).
- **M5 displacement:** Gretton et al. 2012 (MMD kernel two-sample test).
- **M6 domain coverage:** Chao et al. 2014 (rarefaction / coverage estimation); Grootendorst 2022
  (BERTopic).
- **Projection caution:** Chari & Pachter 2023.
- **Lexical robustness:** Li et al. 2016 (distinct-n); Zhu et al. 2018 (self-BLEU);
  Tevet & Berant 2021 (decomposing generation-diversity metrics).
- **Ideation framing:** Guilford 1967; Shah, Smith & Vargas-Hernandez 2003; Olson et al. 2021 (PNAS,
  Divergent Association Task).
