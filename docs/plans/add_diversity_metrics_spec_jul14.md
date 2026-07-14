# Diversity-Facet Metrics — Coding-Agent Spec

Date: 2026-07-14
Scope: 
(1) adds five new metrics (four diversity facets + one displacement check) to the existing proposal- and review-comparison notebooks (`5a`/`5b` for proposals, `6a`/`6b` for reviews) in the
`human-AI-proposal-comparison` project. This spec is written to slot into the pipeline,
inference rules, and file layout already defined in `study_redesign_spec_2026-07-08.md`.
It does not replace existing metrics; it fills facets the current metrics are blind to.

(2) adds a new notebook `7_synthesis_double_compression.ipynb`

---

## 0. Facet architecture (read before coding) — aligned to the manuscript

This spec computes the diversity **facets** the manuscript's Variables section defines. The
manuscript decomposes "narrowing of collective search" into **five facets** (spread, evenness,
richness, dimensionality, coverage) plus a separate directional check (**displacement**). This
spec implements each facet as one or more metrics. The metric IDs (M1–M5) are kept for the
coding agent, but **every metric carries its manuscript facet label** so the results tables emit
facet names the paper can cite directly.

Mapping (this is the single source of truth linking code ↔ manuscript):

| Facet (manuscript) | Question | Metric(s) here | ID | Directional? | Role |
|---|---|---|---|---|---|
| **Spread / dispersion** | How far apart, on average? | `mean_pairwise` (primary) + `centroid_loo`, `mst_dispersion`, `sparseness` (convergent) | *existing (5a/5b)* | no | Facet 1 — **confirmatory** |
| **Evenness** | Uniform, or clumped/repetitive? | Ripley-K / G-function (local repetition) **+** Vendi profile *slope* over q | M4 (+ M1) | no | Facet 2 |
| **Richness** | How many effectively-distinct ideas? | Vendi profile `VS_q` (low-q end) | M1 | no | Facet 3 — **confirmatory (headline)** |
| **Dimensionality** | How many independent axes? | Participation ratio `PR` (+ effective rank) | M3 | no | Facet 4 |
| **Coverage** | How much of the *human* space is occupied? | Support-overlap coverage/density vs human ref | M2 | **yes** | Facet 5 — **confirmatory (headline)** |
| *Displacement (separate check)* | *Same region as humans, or shifted?* | *MMD + optimal-transport distance* | *M5* | **yes** | *directional check — exploratory* |

Key alignment notes (these changed from the pre-manuscript draft of this spec):
- **Spread is Facet 1, not a mere "anchor."** The manuscript promotes `mean_pairwise` and its
  convergent metrics (`centroid_loo`, `mst_dispersion`, `sparseness`) to a first-class facet
  framed as "ideas grow closer and more similar." These already exist in `5a/5b/6a/6b`; this spec
  does **not** recompute them, but the facet tables must **label them `facet=spread`** and report
  `mean_pairwise` as the facet's primary metric with the others as convergent support (one facet,
  several views — not four findings).
- **Evenness is one facet carried by two metrics.** M1's profile *slope* and M4's local-repetition
  curves *jointly* measure evenness. Emit both under `facet=evenness` (M1's slope as a derived
  column, see §3; M4 as the primary), so the manuscript can cite "evenness" as one construct.
- **M5 displacement is now a real, computed metric** (§7), not a citation aside. The manuscript
  makes a displacement *claim* ("AI narrows *toward a shared region*"), so a notebook must produce it.
- **Coverage (Facet 5) has a geometric half and a domain half.** This spec computes only the
  **geometric** half (M2, support-overlap). The **BERTopic-region + MeSH-term** coverage lives in
  the existing `5a/5b` literature-coverage families and is **kept there** — do not fold it in here.
  Cross-reference only: the facet tables should carry `facet=coverage` for M2 **and** the existing
  region/MeSH metrics should be tagged `facet=coverage` in their own exports, so the synthesis
  notebook (§13) can join both under one facet label. (See §7A.)

Confirmatory vs exploratory (mirrors the manuscript's headline structure):
- **Confirmatory (headline):** M1 (`VS_q` at q=1, richness), M2 (`coverage`), and the existing
  spread facet (`mean_pairwise`).
- **Exploratory / mechanistic:** M3 (`PR`), M4 (Ripley/G evenness), M5 (displacement).

---

## 1. Global conventions (apply to every metric, both notebooks)

### 1.1 Embedding-space rule
Every metric is computed in **full embedding space** on L2-normalized vectors.
UMAP/PCA 2-D coordinates are for figures only and must never be fed to a metric.
(Cite Chari & Pachter 2023 in the manuscript for why UMAP distances/densities are
not trustworthy.) This matches the existing rule that literature-space UMAPs are
illustration only.

### 1.2 Distance / kernel
- Vectors are L2-normalized → cosine similarity = dot product; cosine distance = 1 − dot.
- Reuse the existing saved matrices where they exist:
  - proposals: `proposal_pairwise_cosine_full.npy` (from `4a`)
  - reviews: `review_pairwise_cosine_text.npy` (+ `strengths`/`weakness`) (from `4b`)
- Only recompute a matrix if the metric needs the raw embeddings (M1 kernel, M3 covariance);
  in that case load `*_embeddings_full.pkl` / `review_embeddings_text.pkl`.

### 1.3 Equal-n rule (load-bearing)
Every one of these metrics is biased by sample size — more points ⇒ more measured
diversity. Absolute values are comparable across groups **only at equal n**.
- Per-model comparisons are already equal-n (Human 23 vs each model 23).
- Pooled Human-vs-All-AI is **not** equal-n (23 vs 69). Use the existing
  without-replacement subsample-to-23 machinery (see §1.5). Never compare a
  diversity value computed at one n to one computed at another n.

### 1.4 Two nulls (shared inference engine)
- **Between-group significance → label permutation.** Stack the two groups' embeddings,
  shuffle group labels B≥10,000 times, recompute the metric difference each time,
  two-sided p = fraction of |Δ_perm| ≥ |Δ_obs|. This is the permutation-primary rule
  the spec already mandates for matrix-derived metrics. Applies to M1, M3, M4.
  M2 is asymmetric — it uses a split-half reference baseline instead (see §4).
- **Within-group CIs → jackknife (leave-one-out) or subsampling, NOT bootstrap-with-
  replacement.** Bootstrap injects exact duplicate rows, which deflates every metric here
  (duplicates shrink kernel eigenvalues, collapse effective counts, shorten NN distances).
  - For CIs on point estimates: jackknife over the 23 rows (23 recomputes).
  - **Reconciliation with the existing seed-42 pooled bootstrap:** the pipeline already
    caches `bootstrap_ai_idx_samples_n23_seed42.npy` and draws *without replacement*
    (subsampling, not classical bootstrap). Subsampling does NOT inject duplicates, so it
    is safe for these metrics — reuse that cache for the pooled AI side. The only thing to
    avoid is *with-replacement* resampling of a fixed 23-row group. Keep with-replacement
    only for the legacy `mean_pairwise` figure if continuity is needed, and note the
    downward bias hits all groups equally so comparisons stay valid.

### 1.5 Pooled AI subsampling (reuse existing cache)
For pooled Human-vs-All-AI at each condition:
- load `results/tables/{condition}/proposals/original/shared_cache/bootstrap_ai_idx_samples_n23_seed42.npy`
  (or the rephrased/review equivalent). Shape `(1000, 23)`, without-replacement indices into the 69-row AI pool.
- compute the metric on each of the 1000 subsamples → a distribution of the pooled-AI metric at n=23.
- compare against the single Human value (n=23). Report Human value, pooled-AI mean + 95% percentile interval, and an empirical p (fraction of subsamples on the "AI ≥ Human" side, or the reverse depending on metric direction).

### 1.6 Test the gradient as a gradient
The Claude < Gemini < GPT < Human ordering is an *ordered* alternative. After computing
per-model point estimates + jackknife replicates, run a **Jonckheere–Terpstra trend test**
across the four groups in the predicted order → one p for "monotone increase." This is a
stronger, more publishable claim than three pairwise tests. Report it per (condition, task, metric).

### 1.7 Multiplicity
4 metrics × 3 models × 3 conditions × 2 tasks × 2 text branches is a large family.
Pre-register M1(q=1) and M2 as primary; apply Benjamini–Hochberg FDR across the
secondary family within each (task, text_branch). State this in Methods.

### 1.8 Palette (from the study viz guide)
Human `#DC143C`, Claude `#4A90E2`, Gemini `#7B68EE`, GPT `#3CB371`, pooled All-AI `#4A90E2`,
unknown `#808080`. Keep the boxplot/mean-CI grammar and legend conventions already specified.

### 1.9 Robustness passes to pre-empt reviewers
- Re-run the whole battery on the **rephrased** branch (already in the pipeline as `5b`/`6b`) —
  confirms the effect is not a raw-style artifact.
- Add a lexical control (distinct-n; self-BLEU) so that if lexical AND semantic diversity
  both collapse, the effect is not pinned on the sentence encoder. (Optional, one helper.)
- M1 only: report an RBF-kernel sensitivity check at σ = {0.5, 1, 2} × median pairwise distance.

---

## 2. Module layout

Two new `src` helpers, imported by the existing notebooks. Keep the notebooks thin.

```
src/
  diversity_facets.py          # M1–M5 core math, pure functions, no I/O
  diversity_inference.py       # permutation, jackknife, JT trend, subsample drivers, FDR
notebooks/
  5a_compare_proposals_original.ipynb    # + "## Facet Diversity (M1–M5)" section
  5b_compare_proposals_rephrased.ipynb   # same, rephrased branch
  6a_compare_reviews_original.ipynb      # + paired per-proposal facet section
  6b_compare_reviews_rephrased.ipynb     # same, rephrased + strengths/weakness
```

`diversity_facets.py` public functions (all take L2-normalized `X: np.ndarray (n,d)`):

```
vendi_scores(X, qs=(0,0.5,1,2,4,np.inf), kernel="cosine", sigma=None) -> dict[q -> float]
participation_ratio(X) -> float
effective_rank(X) -> float                      # exp(entropy of normalized eigenvalues)
coverage_density(X_ref, X_gen, k=3) -> dict      # {"coverage":..,"density":..}
ripley_K(X, radii, metric="cosine") -> np.ndarray
g_function(X, radii, metric="cosine") -> np.ndarray
nn_distances(X, metric="cosine") -> np.ndarray   # per-point nearest-neighbor distance
mmd2_rbf(X, Y, sigma=None) -> float               # M5: unbiased MMD^2, two-sample
wasserstein_ot(X, Y, metric="cosine") -> float    # M5: optimal-transport distance (POT)
```

`diversity_inference.py` public functions:

```
label_permutation_test(X_a, X_b, stat_fn, B=10000, seed=42, mode="within_diff") -> {"delta_obs","p_two_sided","null"}
# mode="within_diff": stat_fn(X_a)-stat_fn(X_b) (M1,M3,M4). mode="two_sample": stat_fn(X_a,X_b) directly (M5).
jackknife_ci(X, stat_fn, alpha=0.05) -> {"point","lo","hi","replicates"}
subsample_pooled(X_pool, idx_cache, stat_fn) -> np.ndarray          # metric per subsample row
jonckheere_terpstra(groups_ordered: list[np.ndarray]) -> {"JT","p"} # ordered increasing
paired_wilcoxon(human_vals, ai_vals) -> {"W","p","cliffs_delta"}    # reviews only
benjamini_hochberg(pvals) -> qvals
global_envelope_test(obs_curve, null_curves) -> {"p","lo_env","hi_env"}  # M4
split_half_reference(X_human, stat_fn, n_splits=1000, seed=42) -> np.ndarray  # M2 baseline
```

---

## 3. M1 — Vendi diversity profile  ·  facet: RICHNESS (+ EVENNESS via slope)

**Facet:** richness + evenness. **Headline.** Directly answers "distances can't see repetition."

### 3.1 Compute
```
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
  {0.5,1,2}×median pairwise distance; report that conclusions do not flip.
- `VS_q` = similarity-sensitive Hill number of order q on the kernel eigen-spectrum
  (eigenvalues act as "latent-mode abundances"). Cites: Leinster & Cobbold 2012;
  Chao et al. 2014 (ecology); Friedman & Dieng 2023, Pasarkar & Dieng 2024 (Vendi).

### 3.2 Effect size + significance
- Effect size at each q: ratio `VS_q(Human)/VS_q(group)` = "humans produce X× more
  effectively-distinct items."
- Significance: `label_permutation_test` with `stat_fn = lambda X: vendi_scores(X,{1})[1]`
  at q ∈ {0,1,2}. Headline at q=1.
- Gradient: `jonckheere_terpstra` on jackknife replicates of `VS_1` across the 4 groups.
- CIs: `jackknife_ci`.

### 3.3 Visualization
- **(a) Diversity profile:** x = q, y = `VS_q`, one line per group + jackknife CI ribbon.
  Signature to look for: Human on top and *flat*; AI lines *drop faster* as q rises.
- **(b) Eigenvalue scree** per group (sorted normalized eigenvalues) on shared axes:
  AI = few tall eigenvalues then a cliff; Human = flatter. Often the single most
  persuasive panel.
- Follow the standard boxplot/mean-CI grammar for the per-condition q=1 comparison.

### 3.4 Interpretation
`VS_1 = 5` at n=23 ⇒ "these 23 items are as diverse as 5 fully independent ones."
The *slope* over q is the payload: steep q=0→2 drop ⇒ a few dominant modes carry the
mass ⇒ low evenness ⇒ repetition. Flat profile ⇒ genuinely distinct items.
This is exactly the clumping the distance metrics average away.

---

## 4. M2 — Coverage / density vs human reference  ·  facet: COVERAGE (geometric half)

**Facet:** how much of the *human* idea-space AI reaches. **Directional. Headline.**
Use the **density & coverage** estimator (Naeem et al. 2020) — more outlier/small-n robust
than Kynkäänniemi et al. 2019 precision/recall. At n=23 that robustness matters.

### 4.1 Compute
```
def coverage_density(X_ref, X_gen, k=3):
    # X_ref = Human (reference manifold), X_gen = candidate model group
    # radius_i = distance to k-th NN of ref point i WITHIN ref
    Dref = cosine_dist(X_ref, X_ref); np.fill_diagonal(Dref, np.inf)
    radius = np.sort(Dref, axis=1)[:, k-1]           # k-th NN radius per ref point
    Dcross = cosine_dist(X_ref, X_gen)               # (n_ref, n_gen)
    inside = Dcross < radius[:, None]                # gen point falls in ref ball i
    coverage = float(np.mean(inside.any(axis=1)))    # frac of ref manifold reached
    density  = float(inside.sum() / (k * X_gen.shape[0]))  # ~precision, on-manifold-ness
    return {"coverage": coverage, "density": density}
```
- `k=3` default; sweep {2,3,5} and report ordinal stability.
- **coverage** ∈ [0,1] = fraction of human manifold reached → the narrowing number.
- **density** ≈ precision = whether AI points land inside human-plausible space.
- Do **not** use convex-hull volume as coverage — meaningless in d≈768 (hull dominated
  by outliers, curse of dimensionality).

### 4.2 Reference baseline (replaces permutation; coverage is asymmetric)
```
def split_half_reference(X_human, stat_fn, n_splits=1000, seed=42):
    # coverage of one human half by the other → "what coverage looks like when both
    # sets are genuinely human at this n". Gives the null band for narrowing.
    ...
```
A model narrows iff its coverage sits **below** the human self-coverage band. Empirical p =
fraction of split-half values ≤ observed model coverage.
- Pooled AI: compute coverage of Human by each of the 1000 subsampled-23 AI sets (§1.5).
- Optional third handle: authenticity score (Alaa et al. 2022) flags memorization / near-
  duplication — complements M4.

### 4.3 Effect size + significance
- Effect size = coverage itself ("AI recovers X% of the human proposal space") — the
  cleanest one-number compression statistic. Report `coverage` and `1 − coverage`
  (= fraction of human space AI never reaches).
- Significance = position of model coverage relative to split-half human band.
- Gradient: `jonckheere_terpstra` on per-model coverage (bootstrapped via subsample where
  applicable). Report k-sensitivity; treat as robust *ordinally*.

### 4.4 Visualization
- **Density–coverage scatter:** x = coverage, y = density; one marker per model (palette)
  + the human split-half point (near (1,1)) + subsample CI ellipses. Expected pattern:
  AI pulled **left** (low coverage) while often **high** on density.
- Optional literature-anchored UMAP outlining the human region with AI points in an
  interior subregion — illustration only (metric computed in full space).

### 4.5 Interpretation
**High density + low coverage** is the fingerprint of the hypothesis: AI stays in a central,
human-plausible subregion (competent, on-manifold) but fails to reach the periphery humans
explore (narrow). Low coverage = idea-space regions AI never proposes at all.

---

## 5. M3 — Participation ratio  ·  facet: DIMENSIONALITY

**Facet:** how many independent axes ideas vary along. Cheapest metric; distinct from M1
(count of items) and M2 (area).

### 5.1 Compute
```
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
- Report `effective_rank` too; agreement between PR and effective_rank ⇒ not a
  definition artifact. Cite Del Giudice 2021 for PR as effective-dimensionality.

### 5.2 Effect size + significance
- Effect size = PR ratio/difference ("AI varies along ~3 effective axes vs ~8 for humans").
- Significance: `label_permutation_test` on ΔPR. CI: jackknife. Gradient: JT.

### 5.3 Visualization
- Overlaid **cumulative-variance / scree** curves per group (AI shoots up fast: 90% var in
  2–3 PCs; Human gradual) + a PR bar chart with CIs (standard grammar).

### 5.4 Interpretation
Low PR = variation is essentially 1–2 dimensional — ideas differ along few conceptual axes.
This is a *different* collapse from M1: high-Vendi/low-PR = many distinct points strung along
one axis; low-Vendi/high-PR = few points across many axes. Reporting both says *which kind*
of narrowing AI shows — a mechanistic claim, not just "less diverse."

---

## 6. M4 — Ripley-K / G-function in embedding space  ·  facet: EVENNESS (local repetition)

**Facet:** local clumping / near-duplication — the dense knots visible in UMAP, quantified
in full space. **Do NOT use textbook analytic Ripley K** (assumes 2-D/3-D domain, analytic
edge correction, Poisson-CSR baseline — none transfer to d≈768). Use the resampling-null form.

### 6.1 Compute
```
def nn_distances(X, metric="cosine"):
    D = cosine_dist(X, X); np.fill_diagonal(D, np.inf)
    return D.min(axis=1)

def g_function(X, radii):                 # NN-distance CDF
    nnd = nn_distances(X)
    return np.array([(nnd <= r).mean() for r in radii])

def ripley_K(X, radii):                   # mean neighbor count within r
    D = cosine_dist(X, X); np.fill_diagonal(D, np.inf)
    return np.array([ (D < r).sum(axis=1).mean() for r in radii ])
```
- Work on normalized vectors, cosine/chord distance. Radii grid = quantiles of the pooled
  distance distribution (e.g. 20 points from 1st–50th percentile — small-r is where
  duplication shows).

### 6.2 Null (resample from the pooled cloud — NOT analytic CSR)
Draw n=23 points from the **pooled proposal (or review) cloud across all groups**, M=999×,
recompute the curve. This null preserves the real intrinsic geometry of the embedding space,
so the test isolates *group-specific extra-clumping* rather than rediscovering that
embeddings aren't uniform.

### 6.3 Effect size + significance
- **Global envelope test** (Myllymäki et al. 2017) for simultaneous inference over the whole
  r-range → one p-value; avoids pointwise multiple testing. `global_envelope_test`.
- Effect size = area between observed curve and null mean over the small-r region (excess
  short-range mass). Gradient: order of that deviation statistic across models (JT).

### 6.4 Visualization
- **(a)** `ripley_K(r)` (or observed curve) with grey simultaneous null envelope — AI pokes
  above the envelope at small r.
- **(b)** `g_function` overlay (NN-distance CDFs) — most intuitive: AI curves shift **left**
  (shorter NN distances = near-duplication).
- **(c)** companion histogram of nearest-neighbor cosine *similarities* per group.

### 6.5 Interpretation
Excess neighbors at small r / left-shifted NN distances = local repetition and near-
duplication — the UMAP clumps, now measured in real space with a significance envelope.
Distinguishes "spread out but locally clumpy" (AI) from "spread out and evenly filled."

---

## 6A. M5 — Displacement (MMD + optimal transport)  ·  directional check (NOT a diversity facet)

**What it answers:** the five facets measure the *size and shape* of a group's occupied region.
Displacement asks a different question — is the AI region in a *different place* than the human
region, or narrowed toward a shared central zone? The manuscript makes this claim ("AI narrows
*toward a shared region*"), so it must be computed, not asserted. Keep it conceptually separate
from the diversity facets: a set can be displaced without being narrower, or narrower without
being displaced.

**This is a two-sample distance between the Human and AI point clouds, not a within-group scalar.**
That changes the inference: there is no "Human value vs AI value" to compare — the metric *is* the
between-group quantity, tested against a label-permutation null directly.

### 6A.1 Compute
```
def mmd2_rbf(X, Y, sigma=None):
    # unbiased MMD^2 with RBF kernel; sigma via median heuristic on pooled pairwise dists
    if sigma is None:
        sigma = median_pairwise_distance(np.vstack([X, Y]))
    Kxx = rbf(X, X, sigma); Kyy = rbf(Y, Y, sigma); Kxy = rbf(X, Y, sigma)
    m, n = len(X), len(Y)
    # remove diagonal for unbiased estimate
    sxx = (Kxx.sum() - np.trace(Kxx)) / (m*(m-1))
    syy = (Kyy.sum() - np.trace(Kyy)) / (n*(n-1))
    sxy = Kxy.mean()
    return float(sxx + syy - 2*sxy)              # MMD^2 ; ~0 iff same distribution

def wasserstein_ot(X, Y, metric="cosine"):
    # empirical OT (earth-mover) distance between the two clouds
    C = cdist(X, Y, metric=metric)               # cost matrix
    a = np.ones(len(X))/len(X); b = np.ones(len(Y))/len(Y)
    return float(ot.emd2(a, b, C))               # POT library; squared-cost variant optional
```
- Primary: **MMD²** with RBF kernel, median-heuristic bandwidth (Gretton et al. 2012). Robust,
  kernel-based, well-understood permutation test.
- Secondary: **optimal-transport / Wasserstein** distance (POT `ot.emd2`) — more interpretable
  ("average distance to move the AI cloud onto the human cloud") but heavier and sensitive to n.
  Report as convergent support, not the primary.
- Both on L2-normalized full-space embeddings; MMD uses squared-Euclidean-in-RBF (= a function of
  cosine for normalized vectors), OT uses cosine cost.

### 6A.2 Effect size + significance
- **The statistic is directional-agnostic** (distance ≥ 0), so the test is: is the Human↔AI
  distance larger than expected if the two were the same distribution?
- Significance: **label-permutation** — stack the 46 (or 23+23 subsampled) rows, shuffle labels,
  recompute MMD²/OT, B ≥ 10,000. p = fraction of permuted ≥ observed. Reuse
  `label_permutation_test` with `stat_fn = mmd2_rbf` but note it returns a *single* between-group
  stat, not a difference of two within-group stats (add a `mode="two_sample"` flag).
- Effect size: MMD² itself, and a normalized version MMD²/median-kernel for cross-condition
  comparability. For OT, the raw distance in cosine units.
- Gradient: JT across per-model Human↔model distances (Claude/Gemini/GPT). **Direction flips vs.
  the diversity facets:** for displacement, a *larger* Human↔AI distance = more shifted, so if AI
  models are increasingly human-like Claude→GPT, the ordering is *decreasing* distance. State the
  predicted direction explicitly per the manuscript before running JT.

### 6A.3 Interpretation — the crucial disambiguation
Displacement must be read **jointly with coverage (M2)** to mean anything:
- **Low coverage + low displacement** = AI sits *inside* the human region but fills less of it →
  "narrowed toward a shared central zone." **This is the manuscript's claim.**
- **Low coverage + high displacement** = AI occupies a *different, smaller* region → narrowed *and*
  shifted (a different and arguably more alarming story).
- **High coverage + high displacement** = AI covers a comparably large but *elsewhere* region → not
  narrowing, just different.
So M5 is not a standalone headline; its job is to sharpen M2 from "AI fills less space" into "AI
fills less space *and* stays in the humans' central region." Report the M2+M5 pair together.

### 6A.4 Visualization
- **MMD²/OT bar per model** (Human↔Claude, Human↔Gemini, Human↔GPT, Human↔pooled) with permutation
  null band; plus the Human split-half distance as the "same-distribution" floor.
- Optional: the density–coverage scatter from M2 with marker *size* encoding displacement, so
  coverage and displacement read in one panel.

### 6A.5 Dependencies / notes
- Needs the POT library (`pip install pot`) for OT; MMD² is pure numpy.
- At n=23 vs 23, MMD² is usable but low-powered; report it honestly as "consistent with / evidence
  for" rather than a sharp test, and lean on the pooled (subsampled) version for the headline number.
- Reviews (paired setting): displacement is **not** computed per-proposal (panels of 2–5 are too
  small for a two-sample distance). Instead compute it once per condition on the *pooled* review
  clouds (all human reviews vs all AI reviews), clearly labeled as an unpaired, exploratory
  companion to the paired facet results. Do not present it as a paired result.

---

## 6B. Coverage facet — geometric half here, domain half in `5a/5b` (do NOT merge)

The manuscript's **coverage facet has two halves**: the geometric support-overlap coverage (M2,
this spec) and the domain-grounded **BERTopic-region coverage + unique-MeSH-term coverage** (already
implemented in the existing `5a/5b` literature-coverage families). Per the design decision, these
stay in their current locations — this spec does **not** re-implement region/MeSH coverage.

The only requirement is a **shared facet label** so the synthesis notebook can join them:
- M2 exports rows with `facet="coverage"`, `metric="coverage_geometric"`.
- The existing `5a/5b` region-coverage and MeSH-coverage exports must be tagged `facet="coverage"`,
  `metric ∈ {"coverage_bertopic_region", "coverage_mesh_terms"}` in their result tables (a one-line
  addition to those notebooks' export step — flag it there, don't move the computation).
- The synthesis notebook (§13) then treats all three as `facet=coverage` and can show them side by
  side. Geometric coverage answers *how much* of the human space; region/MeSH answer *which* areas
  of biomedical science are under-explored. Together they are the manuscript's Facet 5.

Reviews have no literature-coverage analog (reviews aren't projected onto PubMed), so the review
coverage facet is geometric-only (M2). State this in the reviews section.

---

## 7. PROPOSALS notebook wiring (`5a` original, `5b` rephrased)

Proposals are **unpaired**. Inference unit = the proposal set. This is the free-permutation
regime.

### 7.1 Layers to run (per condition ∈ {baseline, one_at_a_time, persona})
1. **Per-model** (Human 23 vs Claude/Gemini/GPT 23 each): all of M1–M5, equal-n, direct.
   - between-group: label permutation (M1,M3,M4 as within-group Δ; M5 as two-sample) / split-half reference (M2).
   - M5 displacement is two-sample (Human↔model), not a within-group value — see §6A.2.
2. **Pooled Human vs All-AI** (23 vs 69→subsample 23): reuse
   `bootstrap_ai_idx_samples_n23_seed42.npy`; compute each metric per subsample (§1.5);
   compare to the single Human value.
3. **Gradient** across {Claude,Gemini,GPT,Human}: JT trend per metric (§1.6).
4. **Cross-condition** (after per-condition runs): stack the pooled Human-vs-All-AI results
   for baseline / one_at_a_time / persona → does the narrowing *change* across conditions?
   Report each metric's AI÷Human "diversity-retained" ratio per condition + a cross-condition
   figure. (Mirrors the existing `2` cross-condition analysis.)

### 7.2 Where metrics attach
Add one section `## Facet Diversity (M1–M5)` after the existing
`proposal-space diversity` block. Keep `mean_pairwise` as the scale anchor in that block;
cross-reference (don't duplicate) `mst_dispersion` as convergent scale evidence.
Emit the metric-correlation table already required by the spec, now including M1–M5 **plus the existing spread-facet metrics** (`mean_pairwise`, `centroid_loo`, `mst_dispersion`, `sparseness`), so the
manuscript can show the facets load on *different* constructs — and can justify collapsing the spread metrics into one facet.

### 7.3 Text branches
`5a` = original, `5b` = rephrased. Identical code path; the rephrased branch is the
style-controlled robustness pass. Report both; headline on rephrased if style confounds are
a concern (matches spec's treatment of `5b`/`6b` as style-controlled).

---

## 8. REVIEWS notebook wiring (`6a` original, `6b` rephrased)

Reviews are **nested**: each Human proposal has 3–5 Human reviews (Y1: 3–5, Y2: 2–4) and
5 AI reviews per model. Pooling all reviews confounds "reviews of *different* proposals
differ" with "reviews of the *same* proposal differ." **Only the second is filtering
diversity.** So the facet metrics run **per target proposal**, then aggregate with a **paired**
test. This is exactly the exact-n panel design already in the spec.

### 8.1 Exact-n panel construction (reuse existing machinery)
For each target Human proposal p with `n_human_reviews = m` (m ∈ [2,5]):
- Human panel = the m Human reviews of p.
- Per-model AI panel = choose m of that model's 5 reviews of p → enumerate all C(5,m)
  panels (reuse the `6a` exact-n panel-combination cache; `6b` reuses it when the
  `review_uid` roster matches, else rebuilds — per spec §11.3).
- Pooled AI panel = choose m of the 15 (5×3) reviews of p → C(15,m) panels.
Enumerated AI panels are **computational artifacts, not inferential n** (spec §11.4).
Summarize each proposal's AI diversity as the **mean over enumerated panels** (or median).

### 8.2 Per-proposal facet metrics
For each proposal p and each metric M ∈ {M1 `VS_q`, M3 `PR`, M4 clumping summary}:
- `human_val[p]  = M(human_panel_embeddings)`
- `ai_val[p]     = mean over enumerated AI panels of M(panel_embeddings)`
Small panel size (m=2–5) makes any single proposal's value noisy — that is expected; the
signal is in the **paired difference across 23 proposals**, not any one proposal.

**M2 (coverage) in the review setting:** reference = the m Human reviews of p; candidate =
the AI panel for p. `coverage[p]` = fraction of the Human review span reached by AI reviews
of the *same* proposal. This is the cleanest "AI reviews converge more" statistic. (k must be
< m; for m=2 fall back to k=1 or report M2 only for m≥3 proposals and note it.)

### 8.3 Aggregate inference — PAIRED
- **Primary test: paired Wilcoxon signed-rank** across the 23 proposals, pairing
  `human_val[p]` vs `ai_val[p]` (spec already mandates paired Wilcoxon as the correct
  primary test for the review inferential unit — do NOT use free label permutation here).
- Effect size: paired Cliff's δ or matched-pairs rank-biserial. `paired_wilcoxon`.
- Per-model: paired Human-vs-Claude / Gemini / GPT.
- Pooled: paired Human-vs-All-AI (pooled AI panels).
- Gradient: JT across per-model paired differences.
- Cross-condition: stack paired results across baseline / one_at_a_time / persona.

The precise claim this supports: **given the same proposal, AI reviews converge more than
human reviews do** — the filtering half of "double compression."

### 8.4 Field-specific (rephrased `6b` only)
Repeat the per-proposal paired battery on strengths and weakness embeddings
(`review_embeddings_strengths.pkl`, `review_embeddings_weakness.pkl`), labeled secondary to
the whole-review story (spec §11.5).

### 8.5 Visualization (reviews)
- **Paired-slope** figure per confirmatory metric (Human value → AI value, one line per
  proposal) — matches the existing whole-review paired-slopes figure requirement.
- Per-proposal M1 profile faceted small-multiples optional.
- Review-space UMAP for illustration only.

---

## 9. Results schema (so figures/tables have a stable shape)

One tidy long table per (task, text_branch), appended across conditions and metrics.
Coding agent should emit these two CSV schemas.

### 9.1 `facet_diversity_tests.csv` (headline between-group tests)
One row per (condition, task, text_branch, comparison, metric, param).

| column | type | notes |
|--------|------|-------|
| `condition` | str | baseline / one_at_a_time / persona |
| `task` | str | proposals / reviews |
| `text_branch` | str | original / rephrased |
| `field` | str | whole / strengths / weakness (reviews); whole (proposals) |
| `comparison` | str | human_vs_claude / _gemini / _gpt / _pooled_ai |
| `facet` | str | spread / evenness / richness / dimensionality / coverage / displacement |
| `metric` | str | mean_pairwise / vendi / coverage_geometric / participation_ratio / ripley_excess / effective_rank / mmd2 / ot_wasserstein / coverage_bertopic_region / coverage_mesh_terms |
| `param` | str | e.g. `q=1`, `k=3`, `kernel=cosine`; empty if n/a |
| `human_value` | float | point estimate, group=Human. **M5 (displacement): leave NULL** — it is a two-sample distance with no within-group value. |
| `ai_value` | float | group=AI (subsample mean if pooled). **M5: leave NULL** (see `stat`). |
| `effect_size` | float | ratio (M1/spread) / coverage (M2) / ΔPR (M3) / envelope-area (M4) / **MMD² or OT distance (M5)** / Cliff's δ (reviews) |
| `effect_type` | str | ratio / coverage / diff / envelope_area / **two_sample_distance (M5)** / cliffs_delta |
| `ci_lo` `ci_hi` | float | 95% (jackknife / subsample / paired / **permutation for M5**) |
| `inference` | str | permutation / split_half_reference / paired_wilcoxon / global_envelope / **two_sample_permutation (M5)** |
| `stat` | float | permutation Δ / W / JT / envelope stat / **MMD² or OT value (M5, the metric itself)** |
| `p_raw` | float | primary p |
| `p_fdr` | float | BH-corrected within (task, text_branch, field) family |
| `n_human` `n_ai` | int | equal-n check; reviews: mean panel size |
| `n_perm_or_boot` | int | B |
| `notes` | str | k-sensitivity flag, RBF-check pass, **M5 direction convention**, etc. |

**M5 rows are the one exception to the human/ai value layout:** displacement has no per-group value,
so `human_value`/`ai_value` are NULL and the distance lives in both `stat` and `effect_size`. The
synthesis notebook (§13) must skip M5 when computing the AI÷Human ratio (there is no ratio) and
instead plot it as a standalone directional panel or as marker-size on the coverage scatter.

### 9.2 `facet_diversity_gradient.csv` (JT trend, one row per gradient test)
| column | type | notes |
|--------|------|-------|
| `condition` `task` `text_branch` `field` `metric` `param` | | keys |
| `order` | str | `claude<gemini<gpt<human` |
| `JT` | float | Jonckheere–Terpstra statistic |
| `p_raw` `p_fdr` | float | |
| `direction_ok` | bool | observed order matches predicted |
| `notes` | str | |

### 9.3 `facet_diversity_curves.parquet` (for profile/scree/envelope figures)
Long form: (condition, task, text_branch, field, group, metric, x, y, y_lo, y_hi)
where `x` = q (M1 profile), eigen-index (scree), or radius r (M4). One file feeds all
curve figures.

### 9.4 Reviews paired detail (optional, for paired-slope figures)
`facet_review_paired_long.csv`: (condition, text_branch, field, comparison, metric, param,
target_proposal_uid, target_cohort, n_human_reviews, human_value, ai_value, paired_diff).

### 9.5 File layout (mirror existing convention)
```
results/tables/{condition}/proposals/{branch}/facet/facet_diversity_tests.csv
results/tables/{condition}/reviews/{branch}/facet/facet_diversity_tests.csv
results/tables/proposals/{branch}/cross_condition/facet_diversity_tests.csv
results/tables/reviews/{branch}/cross_condition/facet_diversity_tests.csv
results/figures/{condition}/proposals/{branch}/facet/...
```

---

## 10. Build order for the agent

1. `src/diversity_facets.py` — pure functions M1–M5 (M5 = MMD²+OT two-sample) + unit tests on toy data
   (e.g. 3 tight clusters vs uniform-on-sphere: assert VS collapses, PR≈low, coverage low,
   G-curve left-shifted for the clustered set).
2. `src/diversity_inference.py` — permutation, jackknife, subsample driver, JT, paired
   Wilcoxon, BH, global envelope, split-half reference.
3. Wire into `5a` (proposals, original): per-model → pooled → gradient → cross-condition.
4. Clone into `5b` (rephrased).
5. Wire into `6a` (reviews, original) using exact-n panels + paired Wilcoxon.
6. Clone into `6b` (rephrased) + strengths/weakness.
7. Emit the two headline CSVs + curves parquet; build figures from those, never recompute
   metrics inside plotting cells.

## 11. Sanity checks the agent must assert
- All metrics computed on L2-normalized full-D embeddings; no UMAP coords in any metric.
- Every cross-group absolute comparison is equal-n (per-model direct; pooled via subsample).
- Reviews use paired Wilcoxon, not label permutation (except M5, which is unpaired/pooled for reviews).
- No with-replacement resampling of a fixed 23-row group for these metrics (subsample OK).
- Per-model results preserved (never collapse AI into one category) so the gradient survives.
- Bimodal groups: prefer profile curves + full distributions over single point estimates.
- **Every emitted row carries a `facet` label** (spread/evenness/richness/dimensionality/coverage/
  displacement) — the manuscript cites facets, not metric IDs.
- **M5 rows have NULL `human_value`/`ai_value`**; the distance is in `stat`/`effect_size`; the
  synthesis ratio step skips `facet=="displacement"`.
- **M5 is reported jointly with M2** (§6A.3): never present displacement as standalone evidence of
  narrowing — it disambiguates *where* the narrowing sits, read against coverage.
- The existing spread metrics (`mean_pairwise` etc.) and region/MeSH coverage are **tagged with
  facet labels but not recomputed here** — verify the `5a/5b` export step adds the labels.

## 13. Add a new SYNTHESIS notebook (`7_synthesis_double_compression.ipynb`)

**Purpose:** one place that shows AI narrowing on *both* ends — generation (proposals) and
filtering (reviews) — across the three conditions. It is a **display and comparison layer,
not a new computation**. It reads the finished tidy tables from `5a/5b/6a/6b` and plots them.

### 13.1 Hard rules (why this is a synthesis, not a re-analysis)
- **No metric is recomputed here.** No embeddings, no permutations, no panels. Inputs are the
  already-emitted `facet_diversity_tests.csv` / `_gradient.csv` / `_curves.parquet`.
- **Do NOT pool proposals and reviews into one embedding computation.** They live in different
  embedding spaces; a raw `coverage=0.4` for proposals ≠ `0.4` for reviews. The *only* thing
  that goes on a shared axis is a **normalized** quantity (the AI÷Human ratio or a standardized
  effect), never a raw metric value.
- **Do NOT pool the three conditions.** Keeping baseline / one_at_a_time / persona separate is
  what lets the figure show whether persona rescues diversity — the main condition effect.
- Inference stays where it was computed: paired-Wilcoxon p-values come from `6a/6b`,
  permutation p-values from `5a/5b`. This notebook only *carries them through* onto the figures
  (e.g. significance stars), it does not generate new p-values.

### 13.2 Inputs
For each condition ∈ {baseline, one_at_a_time, persona} and each branch ∈ {original, rephrased}:
```
results/tables/{condition}/proposals/{branch}/facet/facet_diversity_tests.csv
results/tables/{condition}/reviews/{branch}/facet/facet_diversity_tests.csv
results/tables/{condition}/proposals/{branch}/facet/facet_diversity_gradient.csv
results/tables/{condition}/reviews/{branch}/facet/facet_diversity_gradient.csv
# optional, for the paired-UMAP illustration only:
data/prepared/{condition}/proposals/{branch}/proposal_umap2d.npy
data/prepared/{condition}/reviews/{branch}/review_umap2d.npy
```
Concatenate all `facet_diversity_tests.csv` into one long frame `T`. The schema is already
defined in §9.1, so no reshaping logic is needed beyond `pd.concat` + an added `task` column
(present) and `branch` column (add from path).

### 13.3 The normalized quantity (single source of truth)
Compute once, reuse in every figure:
```
# M5 displacement has no human/ai split and no ratio — exclude it from the ratio frame.
# Keep it aside for its own directional panel (§13.5 marker-size, or a standalone bar).
is_ratio_metric = T["facet"] != "displacement"
# ratio = AI diversity / Human diversity, on the SAME metric+param+condition+task+branch
T.loc[is_ratio_metric, "ratio"] = T["ai_value"] / T["human_value"]
# for coverage, ai_value already IS the AI-vs-Human coverage in [0,1];
# treat coverage's "human parity" as the split-half human self-coverage baseline,
# NOT 1.0. Store that baseline per (condition,task,branch) as `parity_ref`:
#   - non-coverage metrics: parity_ref = 1.0
#   - coverage metric:      parity_ref = median split-half human self-coverage
T["log2ratio"] = np.log2(T["ratio"])          # symmetric axis; use when any ratio > 1
```
- **Axis choice:** if all ratios < 1, plot `ratio` on a linear axis (reads directly:
  "AI retains 62% of human diversity"). If any ratio exceeds 1, plot `log2ratio` so
  "half as diverse" (−1) and "twice as diverse" (+1) are symmetric around 0.
- **Join keys** for pairing generation vs filtering: `(condition, branch, comparison, metric, param)`.
  A model-condition point in the 2×2 map (§13.5) is one proposals-row joined to one reviews-row on
  these keys.

### 13.4 Figure 1 — double-compression slopegraph (headline)
Two anchors per condition panel: `gen` (proposals) left, `filter` (reviews) right; shared y =
diversity retained. One line per model connecting its gen ratio to its filter ratio. Three panels
side by side (baseline / one_at_a_time / persona). Parity line at the metric's `parity_ref`.
```
def slopegraph(T, metric="vendi", param="q=1", branch="rephrased", comparison_set=MODELS):
    # x positions: gen=0, filter=1 per panel; palette from §1.8
    # for each (condition, model): draw line (gen_ratio -> filter_ratio) + endpoint dots
    # annotate parity line; stars from p_fdr on each endpoint
```
- Primary: `metric="vendi", param="q=1"`. Supplement: same figure for coverage, PR, ripley_excess.
- Reads as: below parity = narrowing on that end; downward slope = compression compounds
  (filtering narrower than generation) = the "double" claim; panels rising toward parity
  left→right = persona rescue.

### 13.5 Figure 2 — 2×2 compression map (most analytically revealing)
Scatter: x = generation ratio, y = filtering ratio, one point per (model, condition). Parity
lines at x=parity_ref and y=parity_ref split four quadrants. Faint arrows baseline→one_at_a_time
→persona per model show condition movement.
```
def compression_map(T, metric="vendi", param="q=1", branch="rephrased"):
    gen = T[(T.task=="proposals")...]; filt = T[(T.task=="reviews")...]
    P = gen.merge(filt, on=["condition","branch","comparison","metric","param"],
                  suffixes=("_gen","_filt"))
    # scatter ratio_gen vs ratio_filt; color by model; marker by condition;
    # draw baseline->persona arrows per model; quadrant labels
```
- Quadrant semantics: bottom-left = "narrows on both" (the thesis); bottom-right = "generates
  broadly but filters narrowly"; top-left = the reverse; top-right = no narrowing. This separates
  the two failure modes the slopegraph merges — keep it as Figure 2.

### 13.6 Figure 3 — small-multiples robustness grid (metrics × tasks)
Rows = {vendi q=1, coverage, participation_ratio, ripley_excess}; columns = {generation, filtering}.
Each cell: compact per-model bar of the ratio with a parity line, one bar cluster per condition.
```
def robustness_grid(T, branch="rephrased"):
    # 4 rows x 2 cols; each cell = grouped bars (x=condition, hue=model), y=ratio
    # shared parity line; stars from p_fdr; shared y-limits per row
```
- This is the reviewer-facing backbone: narrowing holds across *orthogonal* facets on *both*
  ends. Less punchy than Fig 1, but it's the "multiple independent facets collapse at once"
  evidence.

### 13.7 Figure 4 — paired UMAPs (illustration only)
Left = proposal-space UMAP, right = review-space UMAP, same condition; human region outlined
(convex hull or KDE contour of Human points in 2-D — **for display only**), AI points shown
occupying an interior subregion in both.
```
def paired_umaps(condition, branch="rephrased"):
    # load *_umap2d.npy; scatter by group (palette); outline Human region;
    # title: "computed for illustration; all metrics computed in full embedding space"
```
- Explicitly captioned as non-inferential. This is the intuition pump, not evidence. Figure-1
  opener or supplement.

### 13.8 Cross-condition gradient panel (optional 5th)
Small line panel: x = condition (baseline → one_at_a_time → persona), y = pooled AI÷Human ratio,
one line per task (generation vs filtering), for the primary metric. Shows at a glance whether
the *rescue* is stronger for generation or filtering. Pull straight from `T` (pooled comparison
rows), no new computation.

### 13.9 Outputs
```
results/figures/synthesis/{branch}/fig1_double_compression_slopegraph.{png,pdf}
results/figures/synthesis/{branch}/fig2_compression_map.{png,pdf}
results/figures/synthesis/{branch}/fig3_robustness_grid.{png,pdf}
results/figures/synthesis/{branch}/fig4_paired_umaps_{condition}.{png,pdf}
results/tables/synthesis/{branch}/double_compression_summary.csv   # T + ratio + log2ratio, tidy
```
`double_compression_summary.csv` is just `T` with the `ratio`/`log2ratio`/`parity_ref` columns
added — one tidy table backing every synthesis figure, so figures never recompute.

### 13.10 Notebook structure
```
1. ## Configuration            (branch, primary metric+param, palette, axis mode)
2. ## Load Tidy Result Tables  (concat all facet_diversity_tests.csv -> T)
3. ## Compute Ratios           (§13.3, add ratio/log2ratio/parity_ref)
4. ## Figure 1 Slopegraph
5. ## Figure 2 Compression Map
6. ## Figure 3 Robustness Grid
7. ## Figure 4 Paired UMAPs
8. ## Figure 5 Gradient Panel   (optional)
9. ## Export Summary Table + Figures
```

### 13.11 Sanity checks the agent must assert (synthesis)
- No call into `diversity_facets.py` from this notebook (it must not recompute metrics).
- Every ratio pairs proposals↔reviews on identical `(condition,branch,comparison,metric,param)`.
- Coverage uses `parity_ref` = split-half human baseline, not 1.0.
- Conditions never pooled; tasks never merged into a shared embedding.
- Axis mode (linear ratio vs log2) chosen by whether any ratio > 1, stated in the caption.

## 14. Key citations (for Methods)
- Hill 1973; Jost 2006; Chao et al. 2014 — diversity as orthogonal facets / Hill numbers.
- Leinster & Cobbold 2012 — similarity-sensitive diversity.
- Friedman & Dieng 2023; Pasarkar & Dieng 2024 — Vendi Score + order-q extension.
- Naeem et al. 2020 — density & coverage (primary M2); Kynkäänniemi et al. 2019 —
  improved precision/recall; Sajjadi et al. 2018 — PRD; Alaa et al. 2022 — authenticity.
- Del Giudice 2021 — participation ratio / effective dimensionality.
- Ripley 1977 — K-function; Myllymäki et al. 2017 — global envelope test.
- Gretton et al. 2012 — MMD (optional displacement test, not in the core four).
- Chari & Pachter 2023 — why not to trust UMAP distances/densities.
- Li et al. 2016 — distinct-n; Zhu et al. 2018 — self-BLEU (lexical robustness).
- Tevet & Berant 2021 — decomposing/validating generation-diversity metrics.
- Guilford 1967; Shah, Smith & Vargas-Hernandez 2003 — ideation fluency/flexibility/variety.
- Olson et al. 2021 (PNAS, Divergent Association Task) — embedding distance as originality.
