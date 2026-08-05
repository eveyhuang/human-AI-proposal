"""
Inference and notebook-adapter helpers for diversity-facet analyses.

Spec: docs/plans/diversity_facets_design_spec_v2.md. All statistics operate on
L2-normalized full-space embeddings; UMAP/PCA coordinates never enter a metric.
"""

from __future__ import annotations

import itertools
import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

os.environ.setdefault("MPLCONFIGDIR", "/tmp/codex-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/codex-cache")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial.distance import squareform
from scipy.stats import norm, wilcoxon
from statsmodels.stats.multitest import multipletests

from diversity_facets import (
    centroid_dispersion_loo,
    cosine_dist,
    coverage_density,
    effective_rank,
    g_function,
    l2_normalize,
    loo_self_coverage,
    mean_pairwise,
    median_pairwise_distance,
    mmd2_rbf,
    mst_dispersion,
    nn_isolation,
    nn_distances,
    pairwise_sq_euclidean,
    participation_ratio,
    ripley_K,
    simpson_categorical,
    simpson_similarity,
    sparseness,
    spherical_variance,
    vendi_scores,
    vendi_slope,
    wasserstein_ot,
)
from lexical import distinct_n, self_bleu


GROUP_ORDER = ["Claude", "Gemini", "GPT", "Human"]
COMPARISON_TO_GROUP = {
    "human_vs_claude": "Claude",
    "human_vs_gemini": "Gemini",
    "human_vs_gpt": "GPT",
    "human_vs_pooled_ai": "All AI",
}
GROUP_TO_COMPARISON = {v: k for k, v in COMPARISON_TO_GROUP.items()}
MODEL_GROUPS = ["Claude", "Gemini", "GPT"]
PALETTE = {
    "Human": "#DC143C",
    "Claude": "#4A90E2",
    "Gemini": "#7B68EE",
    "GPT": "#3CB371",
    "All AI": "#4A90E2",
    "unknown": "#808080",
}


def label_permutation_test(
    X_a: np.ndarray,
    X_b: np.ndarray,
    stat_fn: Callable[..., float],
    *,
    B: int = 10000,
    seed: int = 42,
    mode: str = "within_diff",
) -> Dict[str, Any]:
    """Permutation test for within-group differences or two-sample distances."""
    Xa = l2_normalize(X_a)
    Xb = l2_normalize(X_b)
    combined = np.vstack([Xa, Xb])
    n_a = Xa.shape[0]
    rng = np.random.default_rng(seed)
    if mode == "within_diff":
        obs = float(stat_fn(Xa) - stat_fn(Xb))
        null = np.empty(B, dtype=float)
        for i in range(B):
            perm = rng.permutation(combined.shape[0])
            null[i] = float(stat_fn(combined[perm[:n_a]]) - stat_fn(combined[perm[n_a:]]))
        p = float((np.sum(np.abs(null) >= abs(obs)) + 1) / (B + 1))
    elif mode == "two_sample":
        obs = float(stat_fn(Xa, Xb))
        null = np.empty(B, dtype=float)
        for i in range(B):
            perm = rng.permutation(combined.shape[0])
            null[i] = float(stat_fn(combined[perm[:n_a]], combined[perm[n_a:]]))
        p = float((np.sum(null >= obs) + 1) / (B + 1))
    else:
        raise ValueError(f"Unsupported permutation mode: {mode}")
    return {"delta_obs": obs, "p_two_sided": p, "null": null}


def _mmd2_from_kernel(K: np.ndarray, idx_a: np.ndarray, idx_b: np.ndarray) -> float:
    """Unbiased MMD^2 from a precomputed kernel over the stacked sample."""
    Kaa = K[np.ix_(idx_a, idx_a)]
    Kbb = K[np.ix_(idx_b, idx_b)]
    Kab = K[np.ix_(idx_a, idx_b)]
    m, n = len(idx_a), len(idx_b)
    saa = (Kaa.sum() - np.trace(Kaa)) / (m * (m - 1))
    sbb = (Kbb.sum() - np.trace(Kbb)) / (n * (n - 1))
    return float(max(0.0, saa + sbb - 2.0 * Kab.mean()))


def mmd2_permutation_test(X: np.ndarray, Y: np.ndarray, *, B: int = 10000, seed: int = 42) -> Dict[str, Any]:
    """Two-sample MMD^2 permutation test with a kernel computed once (fast for large clouds)."""
    Xn = l2_normalize(X)
    Yn = l2_normalize(Y)
    stacked = np.vstack([Xn, Yn])
    sigma = max(median_pairwise_distance(stacked), 1e-12)
    K = np.exp(-pairwise_sq_euclidean(stacked) / (2.0 * sigma**2))
    n_a = Xn.shape[0]
    n_tot = stacked.shape[0]
    obs = _mmd2_from_kernel(K, np.arange(n_a), np.arange(n_a, n_tot))
    rng = np.random.default_rng(seed)
    null = np.empty(B, dtype=float)
    for i in range(B):
        perm = rng.permutation(n_tot)
        null[i] = _mmd2_from_kernel(K, perm[:n_a], perm[n_a:])
    p = float((np.sum(null >= obs) + 1) / (B + 1))
    return {"delta_obs": obs, "p_two_sided": p, "null": null}


def ot_permutation_test(X: np.ndarray, Y: np.ndarray, *, B: int = 1000, seed: int = 42) -> Dict[str, Any]:
    """Optimal-transport two-sample permutation test with the cost matrix computed once."""
    import ot as pot

    Xn = l2_normalize(X)
    Yn = l2_normalize(Y)
    stacked = np.vstack([Xn, Yn])
    C = cosine_dist(stacked, stacked)
    n_a = Xn.shape[0]
    n_tot = stacked.shape[0]

    def _emd(idx_a, idx_b):
        sub = C[np.ix_(idx_a, idx_b)]
        a = np.ones(len(idx_a)) / len(idx_a)
        b = np.ones(len(idx_b)) / len(idx_b)
        return float(pot.emd2(a, b, sub))

    obs = _emd(np.arange(n_a), np.arange(n_a, n_tot))
    rng = np.random.default_rng(seed)
    null = np.empty(B, dtype=float)
    for i in range(B):
        perm = rng.permutation(n_tot)
        null[i] = _emd(perm[:n_a], perm[n_a:])
    p = float((np.sum(null >= obs) + 1) / (B + 1))
    return {"delta_obs": obs, "p_two_sided": p, "null": null}


def jackknife_ci(X: np.ndarray, stat_fn: Callable[[np.ndarray], float], alpha: float = 0.05) -> Dict[str, Any]:
    """Leave-one-out jackknife point estimate and percentile interval."""
    Xn = l2_normalize(X)
    point = float(stat_fn(Xn))
    reps = []
    for i in range(Xn.shape[0]):
        reps.append(float(stat_fn(np.delete(Xn, i, axis=0))))
    reps_arr = np.asarray(reps, dtype=float)
    lo, hi = np.nanpercentile(reps_arr, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"point": point, "lo": float(lo), "hi": float(hi), "replicates": reps_arr}


def subsample_pooled(X_pool: np.ndarray, idx_cache: np.ndarray, stat_fn: Callable[[np.ndarray], float]) -> np.ndarray:
    """Evaluate a statistic over cached without-replacement pooled-AI subsamples."""
    Xn = l2_normalize(X_pool)
    return np.asarray([float(stat_fn(Xn[np.asarray(idx, dtype=int)])) for idx in idx_cache], dtype=float)


def jonckheere_terpstra(groups_ordered: Sequence[np.ndarray], *, alternative: str = "increasing") -> Dict[str, float]:
    """Jonckheere-Terpstra trend test using the large-sample normal approximation."""
    groups = [np.asarray(g, dtype=float)[np.isfinite(g)] for g in groups_ordered]
    if any(len(g) == 0 for g in groups):
        return {"JT": np.nan, "p": np.nan}
    jt = 0.0
    for i in range(len(groups) - 1):
        for j in range(i + 1, len(groups)):
            a = groups[i][:, None]
            b = groups[j][None, :]
            jt += float(np.sum(a < b) + 0.5 * np.sum(a == b))
    ns = np.asarray([len(g) for g in groups], dtype=float)
    n = ns.sum()
    mean = (n * n - np.sum(ns**2)) / 4.0
    var = (n * n * (2 * n + 3) - np.sum(ns**2 * (2 * ns + 3))) / 72.0
    if var <= 0:
        return {"JT": float(jt), "p": np.nan}
    z = (jt - mean) / math.sqrt(var)
    p = float(norm.sf(z) if alternative == "increasing" else norm.cdf(z))
    return {"JT": float(jt), "p": p}


def paired_wilcoxon(human_vals: Iterable[float], ai_vals: Iterable[float]) -> Dict[str, float]:
    """Paired Wilcoxon plus matched-pairs rank-biserial effect."""
    x = np.asarray(list(human_vals), dtype=float)
    y = np.asarray(list(ai_vals), dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size == 0:
        return {"W": np.nan, "p": np.nan, "cliffs_delta": np.nan, "n_pairs": 0}
    diff = x - y
    if np.allclose(diff, 0):
        W, p = 0.0, 1.0
    else:
        res = wilcoxon(x, y, zero_method="wilcox", alternative="two-sided", mode="auto")
        W, p = float(res.statistic), float(res.pvalue)
    nonzero = diff[np.abs(diff) > 0]
    delta = 0.0 if nonzero.size == 0 else float((np.sum(nonzero > 0) - np.sum(nonzero < 0)) / nonzero.size)
    return {"W": W, "p": p, "cliffs_delta": delta, "n_pairs": int(x.size)}


def paired_delta_bootstrap_ci(
    human_vals: np.ndarray,
    ai_vals: np.ndarray,
    *,
    B: int = 2000,
    seed: int = 42,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Bootstrap CI for the matched-pairs rank-biserial delta, resampling proposals.

    Resampling proposals with replacement is allowed here (spec 1A.1: paired review
    contrast) - it is not a set-level diversity metric.
    """
    x = np.asarray(human_vals, dtype=float)
    y = np.asarray(ai_vals, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size < 3:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    deltas = np.empty(B, dtype=float)
    n = x.size
    for i in range(B):
        idx = rng.integers(0, n, size=n)
        d = x[idx] - y[idx]
        nz = d[np.abs(d) > 0]
        deltas[i] = 0.0 if nz.size == 0 else (np.sum(nz > 0) - np.sum(nz < 0)) / nz.size
    lo, hi = np.nanpercentile(deltas, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(lo), float(hi))


def benjamini_hochberg(pvals: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(pvals), dtype=float)
    out = np.full(p.shape, np.nan, dtype=float)
    mask = np.isfinite(p)
    if mask.any():
        out[mask] = multipletests(p[mask], method="fdr_bh")[1]
    return out


def apply_family_fdr(df: pd.DataFrame, family_cols: Sequence[str] = ("task", "text_version", "field")) -> pd.DataFrame:
    """BH-FDR over the SECONDARY family within each (task, text_version, field).

    Spec 1.7: the three pre-registered primaries are reported on p_raw and are not
    part of the BH family; secondaries are corrected across conditions and
    comparisons within each family. Primary rows keep p_fdr = NaN.
    """
    out = df.copy()
    out["p_fdr"] = np.nan
    cols = [c for c in family_cols if c in out.columns]
    is_primary = out.get("is_primary", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    p_raw = pd.to_numeric(out["p_raw"], errors="coerce")
    secondary = (~is_primary) & np.isfinite(p_raw)
    if not secondary.any():
        return out
    for _, idx in out[secondary].groupby(cols, dropna=False).groups.items():
        idx = list(idx)
        out.loc[idx, "p_fdr"] = benjamini_hochberg(out.loc[idx, "p_raw"])
    return out


def global_envelope_test(obs_curve: np.ndarray, null_curves: np.ndarray) -> Dict[str, Any]:
    """Simultaneous max-deviation envelope test (Myllymaki-style global envelope).

    The returned lo_env/hi_env form a SIMULTANEOUS 95% band (center +/- the 95th
    percentile of the null max-absolute-deviation), not a pointwise band.
    """
    obs = np.asarray(obs_curve, dtype=float)
    null = np.asarray(null_curves, dtype=float)
    if null.ndim != 2 or null.shape[0] == 0:
        return {"p": np.nan, "lo_env": np.full_like(obs, np.nan), "hi_env": np.full_like(obs, np.nan), "center": np.full_like(obs, np.nan)}
    center = np.nanmean(null, axis=0)
    obs_stat = float(np.nanmax(np.abs(obs - center)))
    null_stats = np.nanmax(np.abs(null - center[None, :]), axis=1)
    p = float((np.sum(null_stats >= obs_stat) + 1) / (len(null_stats) + 1))
    k95 = float(np.nanpercentile(null_stats, 95))
    return {"p": p, "lo_env": center - k95, "hi_env": center + k95, "center": center, "stat": obs_stat}


def split_half_reference(
    X_human: np.ndarray,
    stat_fn: Callable[[np.ndarray, np.ndarray], float],
    *,
    n_splits: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """Human split-half reference distribution for asymmetric coverage metrics."""
    Xn = l2_normalize(X_human)
    n = Xn.shape[0]
    half = n // 2
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_splits):
        perm = rng.permutation(n)
        vals.append(float(stat_fn(Xn[perm[:half]], Xn[perm[half : half + half]])))
    return np.asarray(vals, dtype=float)


SPREAD_STATS = {
    "mean_pairwise": mean_pairwise,
    "centroid_loo": centroid_dispersion_loo,
    "mst_dispersion": mst_dispersion,
    "sparseness": sparseness,
    "nn_isolation": nn_isolation,
    "spherical_variance": spherical_variance,
}

# Set-level metrics whose jackknife replicates are persisted for boxplot panels.
REPLICATE_METRICS = {
    "mean_pairwise": ("spread", mean_pairwise),
    "centroid_loo": ("spread", centroid_dispersion_loo),
    "mst_dispersion": ("spread", mst_dispersion),
    "sparseness": ("spread", sparseness),
    "nn_isolation": ("spread", nn_isolation),
    "spherical_variance": ("spread", spherical_variance),
    "vendi": ("richness", lambda Z: vendi_scores(Z, (1,))[1]),
    "vendi_slope": ("evenness", lambda Z: vendi_slope(vendi_scores(Z, (0, 2)))),
    "participation_ratio": ("dimensionality", participation_ratio),
    "effective_rank": ("dimensionality", effective_rank),
}


def _metric_row(
    *,
    condition: str,
    task: str,
    text_branch: str,
    field: str,
    comparison: str,
    facet: str,
    metric: str,
    param: str = "",
    human_value: float | None = None,
    ai_value: float | None = None,
    effect_size: float | None = None,
    effect_type: str = "",
    ci_lo: float | None = None,
    ci_hi: float | None = None,
    human_ci_lo: float | None = None,
    human_ci_hi: float | None = None,
    inference: str = "",
    stat: float | None = None,
    p_raw: float | None = None,
    n_human: int | float | None = None,
    n_ai: int | float | None = None,
    n_perm_or_boot: int | None = None,
    notes: str = "",
) -> Dict[str, Any]:
    return {
        "condition": condition,
        "task": task,
        "text_branch": text_branch,
        "field": field,
        "comparison": comparison,
        "facet": facet,
        "metric": metric,
        "param": param,
        "human_value": np.nan if human_value is None else human_value,
        "ai_value": np.nan if ai_value is None else ai_value,
        "effect_size": np.nan if effect_size is None else effect_size,
        "effect_type": effect_type,
        "ci_lo": np.nan if ci_lo is None else ci_lo,
        "ci_hi": np.nan if ci_hi is None else ci_hi,
        "human_ci_lo": np.nan if human_ci_lo is None else human_ci_lo,
        "human_ci_hi": np.nan if human_ci_hi is None else human_ci_hi,
        "inference": inference,
        "stat": np.nan if stat is None else stat,
        "p_raw": np.nan if p_raw is None else p_raw,
        "p_fdr": np.nan,
        "n_human": np.nan if n_human is None else n_human,
        "n_ai": np.nan if n_ai is None else n_ai,
        "n_perm_or_boot": np.nan if n_perm_or_boot is None else n_perm_or_boot,
        "notes": notes,
    }


def _comparison_from_group(group: str) -> str:
    return GROUP_TO_COMPARISON.get(group, f"human_vs_{str(group).lower().replace(' ', '_')}")


def _group_indices(master_df: pd.DataFrame) -> Dict[str, np.ndarray]:
    out = {"Human": master_df.index[master_df["source_group"].eq("Human") | master_df["source_type"].eq("human")].to_numpy()}
    for group in MODEL_GROUPS:
        out[group] = master_df.index[master_df["source_group"].eq(group)].to_numpy()
    out["All AI"] = master_df.index[master_df["source_type"].eq("ai")].to_numpy()
    return out


def _radii_from_pooled(X: np.ndarray) -> np.ndarray:
    D = cosine_dist(X)
    tri = D[np.triu_indices(D.shape[0], k=1)]
    tri = tri[np.isfinite(tri) & (tri > 0)]
    if tri.size == 0:
        return np.linspace(0.01, 0.5, 20)
    return np.unique(np.quantile(tri, np.linspace(0.01, 0.50, 20)))


def _null_curves_from_pool(
    X_pool: np.ndarray,
    radii: np.ndarray,
    *,
    n: int,
    B: int,
    seed: int,
    curve_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    Xn = l2_normalize(X_pool)
    B_eff = min(B, 999)
    curves = np.empty((B_eff, len(radii)), dtype=float)
    for i in range(B_eff):
        idx = rng.choice(Xn.shape[0], size=n, replace=False)
        curves[i] = curve_fn(Xn[idx], radii)
    return curves


def _curve_row(
    *,
    condition: str,
    task: str,
    text_branch: str,
    field: str,
    group: str,
    facet: str,
    metric: str,
    param: str = "",
    x: float,
    y: float,
    y_lo: float = np.nan,
    y_hi: float = np.nan,
) -> Dict[str, Any]:
    return {
        "condition": condition, "task": task, "text_branch": text_branch, "field": field,
        "group": group, "facet": facet, "metric": metric, "param": param,
        "x": float(x), "y": float(y), "y_lo": float(y_lo), "y_hi": float(y_hi),
    }


def _persist_values(curves, base, *, group, facet, metric, param, values) -> None:
    for i, v in enumerate(np.asarray(values, dtype=float)):
        curves.append(_curve_row(**base, group=group, facet=facet, metric=metric, param=param, x=i, y=v))


def _append_embedding_curve_rows(
    curves: List[Dict[str, Any]],
    *,
    base: Dict[str, Any],
    group: str,
    X_group: np.ndarray,
    radii: np.ndarray,
    envelope: Dict[str, Any] | None,
    profile_jackknife: bool = True,
) -> None:
    """Append tidy curve rows for one embedding group (all points at equal n by caller)."""
    Xg = l2_normalize(np.asarray(X_group, dtype=float))
    if Xg.shape[0] < 2:
        return

    qs = (0, 0.5, 1, 2, 4, np.inf)
    scores = vendi_scores(Xg, qs)
    if profile_jackknife and Xg.shape[0] >= 3:
        reps = np.asarray([[vendi_scores(np.delete(Xg, i, axis=0), qs)[q] for q in qs] for i in range(Xg.shape[0])])
        lo = np.nanpercentile(reps, 2.5, axis=0)
        hi = np.nanpercentile(reps, 97.5, axis=0)
    else:
        lo = np.full(len(qs), np.nan)
        hi = np.full(len(qs), np.nan)
    for j, q in enumerate(qs):
        curves.append(_curve_row(**base, group=group, facet="richness", metric="vendi_profile",
                                 x=float(q), y=float(scores[q]), y_lo=float(lo[j]), y_hi=float(hi[j])))

    kernel_eigs = np.linalg.eigvalsh((Xg @ Xg.T) / Xg.shape[0])
    for pos, val in enumerate(sorted(np.clip(kernel_eigs, 0, None), reverse=True), start=1):
        curves.append(_curve_row(**base, group=group, facet="richness", metric="kernel_eigen_scree", x=pos, y=float(val)))

    X_centered = Xg - Xg.mean(axis=0, keepdims=True)
    singular_values = np.linalg.svd(X_centered, full_matrices=False, compute_uv=False)
    variance = np.square(singular_values)
    if np.nansum(variance) > 0:
        cumulative_variance = np.cumsum(variance / np.nansum(variance))
        for pos, val in enumerate(cumulative_variance, start=1):
            curves.append(_curve_row(**base, group=group, facet="dimensionality", metric="participation_ratio_scree", x=pos, y=float(val)))

    K_curve = ripley_K(Xg, radii)
    G_curve = g_function(Xg, radii)
    if envelope is not None:
        lo_env, hi_env = envelope["lo_env"], envelope["hi_env"]
    else:
        lo_env = np.full(len(radii), np.nan)
        hi_env = np.full(len(radii), np.nan)
    for r, y, lo_e, hi_e in zip(radii, K_curve, lo_env, hi_env):
        curves.append(_curve_row(**base, group=group, facet="evenness", metric="ripley_K",
                                 param="null=global_envelope_95", x=float(r), y=float(y),
                                 y_lo=float(lo_e), y_hi=float(hi_e)))
    for r, y in zip(radii, G_curve):
        curves.append(_curve_row(**base, group=group, facet="evenness", metric="g_function", x=float(r), y=float(y)))

    # Raw distributions backing ridge / NN-similarity histogram panels.
    D = cosine_dist(Xg)
    tri = D[np.triu_indices(D.shape[0], k=1)]
    _persist_values(curves, base, group=group, facet="spread", metric="pairwise_distances", param="", values=tri)
    _persist_values(curves, base, group=group, facet="evenness", metric="nn_distance", param="", values=nn_distances(Xg))


def _append_equal_n_curve_rows(
    curves: List[Dict[str, Any]],
    *,
    base: Dict[str, Any],
    group: str,
    X_group: np.ndarray,
    n_ref: int,
    radii: np.ndarray,
    envelope: Dict[str, Any] | None,
    n_draws: int = 100,
    seed: int = 42,
) -> None:
    """Equal-n curve rows: groups larger than n_ref are subsampled without replacement.

    Review whole-cloud groups differ in size (Human panels vs 5-per-model vs pooled),
    and every curve here is n-sensitive (spec 1.3), so each group is brought to the
    human n before curves are compared. y = mean over draws, ribbon = 2.5/97.5 pct.
    """
    Xg = l2_normalize(np.asarray(X_group, dtype=float))
    if Xg.shape[0] < 2:
        return
    if Xg.shape[0] <= n_ref:
        _append_embedding_curve_rows(curves, base=base, group=group, X_group=Xg, radii=radii,
                                     envelope=envelope, profile_jackknife=True)
        return

    rng = np.random.default_rng(seed)
    qs = (0, 0.5, 1, 2, 4, np.inf)
    prof, scree, cumvar, Ks, Gs = [], [], [], [], []
    nn_last = None
    tri_last = None
    for _ in range(n_draws):
        idx = rng.choice(Xg.shape[0], size=n_ref, replace=False)
        Xs = Xg[idx]
        s = vendi_scores(Xs, qs)
        prof.append([s[q] for q in qs])
        eigs = np.linalg.eigvalsh((Xs @ Xs.T) / n_ref)
        scree.append(sorted(np.clip(eigs, 0, None), reverse=True))
        sv = np.linalg.svd(Xs - Xs.mean(axis=0, keepdims=True), full_matrices=False, compute_uv=False)
        var = np.square(sv)
        cumvar.append(np.cumsum(var / var.sum()) if var.sum() > 0 else np.full(n_ref, np.nan))
        Ks.append(ripley_K(Xs, radii))
        Gs.append(g_function(Xs, radii))
        D = cosine_dist(Xs)
        tri_last = D[np.triu_indices(n_ref, k=1)]
        nn_last = nn_distances(Xs)

    def _emit(metric, facet, xs, arr, param=""):
        arr = np.asarray(arr, dtype=float)
        y = np.nanmean(arr, axis=0)
        lo = np.nanpercentile(arr, 2.5, axis=0)
        hi = np.nanpercentile(arr, 97.5, axis=0)
        for xv, yv, l, h in zip(xs, y, lo, hi):
            curves.append(_curve_row(**base, group=group, facet=facet, metric=metric, param=param,
                                     x=float(xv), y=float(yv), y_lo=float(l), y_hi=float(h)))

    _emit("vendi_profile", "richness", [float(q) for q in qs], prof, param=f"equal_n={n_ref}")
    _emit("kernel_eigen_scree", "richness", np.arange(1, n_ref + 1), scree, param=f"equal_n={n_ref}")
    _emit("participation_ratio_scree", "dimensionality", np.arange(1, n_ref + 1), cumvar, param=f"equal_n={n_ref}")
    if envelope is not None:
        for r, y, lo_e, hi_e in zip(radii, np.nanmean(np.asarray(Ks), axis=0), envelope["lo_env"], envelope["hi_env"]):
            curves.append(_curve_row(**base, group=group, facet="evenness", metric="ripley_K",
                                     param=f"equal_n={n_ref};null=global_envelope_95",
                                     x=float(r), y=float(y), y_lo=float(lo_e), y_hi=float(hi_e)))
    else:
        _emit("ripley_K", "evenness", radii, Ks, param=f"equal_n={n_ref}")
    _emit("g_function", "evenness", radii, Gs, param=f"equal_n={n_ref}")
    _persist_values(curves, base, group=group, facet="spread", metric="pairwise_distances", param=f"equal_n={n_ref};one_draw", values=tri_last)
    _persist_values(curves, base, group=group, facet="evenness", metric="nn_distance", param=f"equal_n={n_ref};one_draw", values=nn_last)


def _ngram_bitmasks(token_lists: Sequence[Sequence[str]], n: int) -> Tuple[List[int], np.ndarray]:
    """Per-text unique-n-gram bitmasks over a shared vocabulary + per-text n-gram totals.

    Group distinct-n = popcount(OR of member masks) / sum(member totals), which makes
    the label-permutation null cheap (integer ORs instead of set unions per draw).
    """
    vocab: Dict[Tuple[str, ...], int] = {}
    masks: List[int] = []
    totals = np.zeros(len(token_lists), dtype=float)
    for ti, tokens in enumerate(token_lists):
        grams = [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
        totals[ti] = len(grams)
        mask = 0
        for g in set(grams):
            pos = vocab.setdefault(g, len(vocab))
            mask |= 1 << pos
        masks.append(mask)
    return masks, totals


def _lexical_rows(master: pd.DataFrame, idx: Dict[str, np.ndarray], *, base_kwargs: Dict[str, Any],
                  text_col: str, n_perm: int = 10000, seed: int = 42) -> List[Dict[str, Any]]:
    """Lexical-control rows (spec 1.9): distinct-n with permutation p, self-BLEU descriptive."""
    if text_col not in master.columns:
        return []
    texts = master[text_col].astype(str).tolist()
    tokens = [t.lower().split() for t in texts]
    rows: List[Dict[str, Any]] = []
    human_rows = np.asarray(idx["Human"], dtype=int)

    self_bleu_cache: Dict[str, float] = {}

    def _sb(group_name, rows_idx):
        if group_name not in self_bleu_cache:
            self_bleu_cache[group_name] = self_bleu([tokens[int(i)] for i in rows_idx])
        return self_bleu_cache[group_name]

    for n_gram in (1, 2):
        masks, totals = _ngram_bitmasks(tokens, n_gram)

        def _distinct(rows_idx):
            u = 0
            tot = 0.0
            for r in rows_idx:
                u |= masks[int(r)]
                tot += totals[int(r)]
            return (bin(u).count("1") / tot) if tot else np.nan

        h_val = _distinct(human_rows)
        for group in MODEL_GROUPS:
            g_rows = np.asarray(idx[group], dtype=int)
            comparison = _comparison_from_group(group)
            g_val = _distinct(g_rows)
            combined = np.concatenate([human_rows, g_rows])
            n_h = len(human_rows)
            obs = h_val - g_val
            rng = np.random.default_rng(seed)
            null = np.empty(n_perm, dtype=float)
            for b in range(n_perm):
                perm = rng.permutation(len(combined))
                sel = combined[perm]
                null[b] = _distinct(sel[:n_h]) - _distinct(sel[n_h:])
            p = float((np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1))
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="lexical_control",
                                    metric=f"distinct_{n_gram}", param=f"n={n_gram}", human_value=h_val, ai_value=g_val,
                                    effect_size=h_val / g_val if g_val else np.nan, effect_type="ratio",
                                    inference="permutation", stat=obs, p_raw=p,
                                    n_human=len(human_rows), n_ai=len(g_rows), n_perm_or_boot=n_perm,
                                    notes="lexical robustness control (spec 1.9); higher = more lexically diverse"))

    h_sb = _sb("Human", human_rows)
    for group in MODEL_GROUPS:
        g_sb = _sb(group, idx[group])
        rows.append(_metric_row(**base_kwargs, comparison=_comparison_from_group(group), facet="lexical_control",
                                metric="self_bleu", param="n=1..4", human_value=h_sb, ai_value=g_sb,
                                effect_size=g_sb - h_sb, effect_type="diff",
                                inference="descriptive", stat=g_sb - h_sb, p_raw=np.nan,
                                n_human=len(human_rows), n_ai=len(idx[group]),
                                notes="lexical robustness control; higher self-BLEU = more repetitive (descriptive, no test)"))
    return rows


def pooled_null_reference(
    X_pool: np.ndarray,
    stat_fns: Mapping[Tuple[str, str, str], Callable[[np.ndarray], float]],
    *,
    n: int,
    M: int = 999,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Same-n pooled-cloud null draws for the fingerprint axis (redesign spec 3.1).

    Returns long-form records (facet, metric, param, draw_idx, value): each of M draws of
    size n WITHOUT replacement from the pooled cloud, evaluated under every statistic. One
    draw loop serves all metrics so the draws are shared across the battery.
    """
    Xn = l2_normalize(X_pool)
    rng = np.random.default_rng(seed)
    records: List[Dict[str, Any]] = []
    for i in range(M):
        idx = rng.choice(Xn.shape[0], size=n, replace=False)
        Xs = Xn[idx]
        for (facet, metric, param), fn in stat_fns.items():
            records.append({"facet": facet, "metric": metric, "param": param,
                            "draw_idx": i, "value": float(fn(Xs))})
    return records


def build_proposal_facet_outputs(
    analysis: Any,
    *,
    text_branch: str,
    bootstrap_ai_idx_samples: np.ndarray,
    n_perm: int = 10000,
    n_boot: int = 1000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute proposal facet tests, gradient, curve, and null-reference rows for one condition."""
    master = analysis.proposal_master.copy()
    X = l2_normalize(np.asarray(analysis.full_embeddings["embeddings"], dtype=float))
    idx = _group_indices(master)
    human = idx["Human"]
    rows: List[Dict[str, Any]] = []
    curves: List[Dict[str, Any]] = []
    grad_rows: List[Dict[str, Any]] = []
    radii = _radii_from_pooled(X)
    null_K = _null_curves_from_pool(X, radii, n=len(human), B=999, seed=seed, curve_fn=ripley_K)
    null_K_mean = np.nanmean(null_K, axis=0)

    base = dict(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole")
    base_kwargs = dict(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole")

    Xh = X[human]
    n_h = len(Xh)

    # Human M4 reference values (used as human_value on every comparison row).
    K_h = ripley_K(Xh, radii)
    env_h = global_envelope_test(K_h, null_K)
    area_h = float(np.trapz(K_h - null_K_mean, radii))

    for group in ["Human", *MODEL_GROUPS]:
        env_for_curves = global_envelope_test(ripley_K(X[idx[group]], radii), null_K)
        _append_embedding_curve_rows(curves, base=base, group=group, X_group=X[idx[group]],
                                     radii=radii, envelope=env_for_curves)

    # Jackknife replicates persisted once per group for boxplot panels (spec 1A.0).
    jack_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for group in ["Human", *MODEL_GROUPS]:
        for metric, (facet, stat_fn) in REPLICATE_METRICS.items():
            jk = jackknife_ci(X[idx[group]], stat_fn)
            jack_cache[(group, metric)] = jk
            _persist_values(curves, base, group=group, facet=facet,
                            metric=f"{metric}_jackknife", param="", values=jk["replicates"])

    for group in MODEL_GROUPS:
        Xg = X[idx[group]]
        comparison = _comparison_from_group(group)
        n_g = len(Xg)

        # M0 spread (six convergent views, mean_pairwise primary).
        for metric, stat_fn in SPREAD_STATS.items():
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_jk = jack_cache[("Human", metric)]
            g_jk = jack_cache[(group, metric)]
            ratio = h_jk["point"] / g_jk["point"] if g_jk["point"] else np.nan
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="spread", metric=metric,
                                    human_value=h_jk["point"], ai_value=g_jk["point"], effect_size=ratio,
                                    effect_type="ratio", ci_lo=g_jk["lo"], ci_hi=g_jk["hi"],
                                    human_ci_lo=h_jk["lo"], human_ci_hi=h_jk["hi"],
                                    inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm,
                                    notes="spread facet; ci = 95% jackknife (AI group), human_ci = 95% jackknife (Human)"))

        # M1 richness (cosine kernel, q in {0,1,2}; headline q=1).
        for q in (0, 1, 2):
            stat_fn = lambda Z, q=q: vendi_scores(Z, (q,))[q]
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            if q == 1:
                h_jk = jack_cache[("Human", "vendi")]
                g_jk = jack_cache[(group, "vendi")]
            else:
                h_jk = jackknife_ci(Xh, stat_fn)
                g_jk = jackknife_ci(Xg, stat_fn)
            ratio = h_jk["point"] / g_jk["point"] if g_jk["point"] else np.nan
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="richness", metric="vendi",
                                    param=f"q={q}", human_value=h_jk["point"], ai_value=g_jk["point"],
                                    effect_size=ratio, effect_type="ratio", ci_lo=g_jk["lo"], ci_hi=g_jk["hi"],
                                    human_ci_lo=h_jk["lo"], human_ci_hi=h_jk["hi"],
                                    inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm))

        # M1 RBF-kernel sensitivity at sigma = {0.5, 1, 2} x median pairwise distance (spec 1.9).
        med = median_pairwise_distance(np.vstack([Xh, Xg]))
        for mult in (0.5, 1.0, 2.0):
            sigma = mult * med
            stat_fn = lambda Z, s=sigma: vendi_scores(Z, (1,), kernel="rbf", sigma=s)[1]
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_val = float(stat_fn(Xh))
            g_val = float(stat_fn(Xg))
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="richness", metric="vendi",
                                    param=f"q=1;kernel=rbf;sigma={mult}x_median", human_value=h_val, ai_value=g_val,
                                    effect_size=h_val / g_val if g_val else np.nan, effect_type="ratio",
                                    inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm,
                                    notes="RBF kernel-sensitivity robustness pass (spec 1.9)"))

        # M1-derived evenness slope (spec 4.2 formula: (VS0 - VS2) / VS0; larger = less even).
        slope_fn = lambda Z: vendi_slope(vendi_scores(Z, (0, 2)))
        perm = label_permutation_test(Xh, Xg, slope_fn, B=n_perm, seed=seed, mode="within_diff")
        h_jk = jack_cache[("Human", "vendi_slope")]
        g_jk = jack_cache[(group, "vendi_slope")]
        rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="evenness", metric="vendi_slope",
                                param="q=0..2", human_value=h_jk["point"], ai_value=g_jk["point"],
                                effect_size=g_jk["point"] - h_jk["point"], effect_type="diff",
                                ci_lo=g_jk["lo"], ci_hi=g_jk["hi"], human_ci_lo=h_jk["lo"], human_ci_hi=h_jk["hi"],
                                inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm,
                                notes="relative VS0->VS2 drop (spec 4.2); larger = few dominant modes = less even; effect = AI - Human"))

        # M2 geometric coverage, k in {2, 3, 5}; k=3 primary (spec 5.1 sweep).
        for k in (2, 3, 5):
            cov = coverage_density(Xh, Xg, k=k)
            split = split_half_reference(Xh, lambda A, B, kk=k: coverage_density(A, B, k=kk)["coverage"], n_splits=n_boot, seed=seed)
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="coverage", metric="coverage_geometric",
                                    param=f"k={k}", human_value=float(np.nanmedian(split)), ai_value=cov["coverage"],
                                    effect_size=cov["coverage"], effect_type="coverage",
                                    ci_lo=float(np.nanpercentile(split, 2.5)), ci_hi=float(np.nanpercentile(split, 97.5)),
                                    inference="split_half_reference", stat=cov["coverage"],
                                    p_raw=float((np.sum(split <= cov["coverage"]) + 1) / (len(split) + 1)),
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_boot,
                                    notes=f"density={cov['density']:.4g}; human_value = median human split-half coverage (parity ref); ci = split-half band"))
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="coverage", metric="coverage_density",
                                    param=f"k={k}", human_value=np.nan, ai_value=cov["density"],
                                    effect_size=cov["density"], effect_type="density",
                                    inference="descriptive", stat=cov["density"],
                                    n_human=n_h, n_ai=n_g,
                                    notes="companion to coverage_geometric (Naeem et al. 2020); ~precision / on-manifold-ness"))

        # M3 dimensionality.
        for metric, stat_fn in [("participation_ratio", participation_ratio), ("effective_rank", effective_rank)]:
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_jk = jack_cache[("Human", metric)]
            g_jk = jack_cache[(group, metric)]
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="dimensionality", metric=metric,
                                    human_value=h_jk["point"], ai_value=g_jk["point"],
                                    effect_size=h_jk["point"] - g_jk["point"], effect_type="diff",
                                    ci_lo=g_jk["lo"], ci_hi=g_jk["hi"], human_ci_lo=h_jk["lo"], human_ci_hi=h_jk["hi"],
                                    inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm))

        # M4 evenness (global envelope; human excess area carried as human_value).
        K_obs = ripley_K(Xg, radii)
        env = global_envelope_test(K_obs, null_K)
        area = float(np.trapz(K_obs - null_K_mean, radii))
        rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="evenness", metric="ripley_excess",
                                param="r=pooled_q01_q50", human_value=area_h, ai_value=area,
                                effect_size=area, effect_type="envelope_area",
                                inference="global_envelope", stat=env.get("stat"), p_raw=env["p"],
                                n_human=n_h, n_ai=n_g, n_perm_or_boot=999,
                                notes=f"AI excess short-range mass vs pooled-cloud null (M=999); human excess = {area_h:.4g} (env p = {env_h['p']:.4g}); simultaneous envelope"))

        # M5 displacement.
        for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="two_sample")
            rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="displacement", metric=metric,
                                    human_value=None, ai_value=None, effect_size=perm["delta_obs"],
                                    effect_type="two_sample_distance",
                                    ci_lo=float(np.nanpercentile(perm["null"], 2.5)), ci_hi=float(np.nanpercentile(perm["null"], 97.5)),
                                    inference="two_sample_permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"],
                                    n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm,
                                    notes="M5 directional check; read jointly with coverage (spec 8.3); larger = more displaced; ci = permutation null band"))

    # Human split-half displacement floor (spec 8.4): the same-distribution reference.
    for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
        floor = split_half_reference(Xh, stat_fn, n_splits=min(n_boot, 500), seed=seed)
        rows.append(_metric_row(**base_kwargs, comparison="human_split_half", facet="displacement", metric=metric,
                                human_value=None, ai_value=None, effect_size=float(np.nanmedian(floor)),
                                effect_type="two_sample_distance",
                                ci_lo=float(np.nanpercentile(floor, 2.5)), ci_hi=float(np.nanpercentile(floor, 97.5)),
                                inference="split_half_reference", stat=float(np.nanmedian(floor)),
                                n_human=n_h, n_ai=n_h, n_perm_or_boot=len(floor),
                                notes="human split-half same-distribution floor for the M5 bar figure (spec 8.4)"))

    # Pooled Human vs All-AI: every metric via the cached without-replacement subsamples.
    Xai_pool = X[idx["All AI"]]
    ai_abs = idx["All AI"]
    abs_to_pool = {int(abs_i): pos for pos, abs_i in enumerate(ai_abs)}
    pool_samples = np.asarray([[abs_to_pool[int(v)] for v in sample] for sample in bootstrap_ai_idx_samples], dtype=int)
    comparison = "human_vs_pooled_ai"
    pooled_note = "pooled All-AI without-replacement subsample to n=23 (AI n=23 subsampled from 69)"

    pooled_stats: Dict[Tuple[str, str, str], Callable[[np.ndarray], float]] = {}
    for metric, stat_fn in SPREAD_STATS.items():
        pooled_stats[("spread", metric, "")] = stat_fn
    for q in (0, 1, 2):
        pooled_stats[("richness", "vendi", f"q={q}")] = lambda Z, q=q: vendi_scores(Z, (q,))[q]
    pooled_stats[("evenness", "vendi_slope", "q=0..2")] = lambda Z: vendi_slope(vendi_scores(Z, (0, 2)))
    pooled_stats[("dimensionality", "participation_ratio", "")] = participation_ratio
    pooled_stats[("dimensionality", "effective_rank", "")] = effective_rank
    pooled_stats[("evenness", "ripley_excess", "r=pooled_q01_q50")] = lambda Z: float(np.trapz(ripley_K(Z, radii) - null_K_mean, radii))

    for (facet, metric_name, param), stat_fn in pooled_stats.items():
        human_value = float(stat_fn(Xh))
        vals = subsample_pooled(Xai_pool, pool_samples, stat_fn)
        ai_mean = float(np.nanmean(vals))
        if facet in {"spread", "richness"}:
            effect, effect_type = (human_value / ai_mean if ai_mean else np.nan), "ratio"
        elif metric_name == "ripley_excess":
            effect, effect_type = ai_mean, "envelope_area"
        else:
            effect, effect_type = human_value - ai_mean, "diff"
        # One-sided empirical p in the predicted direction (AI below Human for
        # diversity metrics; AI above for clumping metrics ripley_excess / vendi_slope).
        if metric_name in {"ripley_excess", "vendi_slope"}:
            p = float((np.sum(vals <= human_value) + 1) / (len(vals) + 1))
        else:
            p = float((np.sum(vals >= human_value) + 1) / (len(vals) + 1))
        rows.append(_metric_row(**base_kwargs, comparison=comparison, facet=facet, metric=metric_name, param=param,
                                human_value=human_value, ai_value=ai_mean, effect_size=effect, effect_type=effect_type,
                                ci_lo=float(np.nanpercentile(vals, 2.5)), ci_hi=float(np.nanpercentile(vals, 97.5)),
                                inference="same_size_subsample", stat=human_value - ai_mean, p_raw=p,
                                n_human=n_h, n_ai=n_h, n_perm_or_boot=len(vals), notes=pooled_note))
        _persist_values(curves, base, group="All AI", facet=facet,
                        metric=f"{metric_name}_pooled_subsample", param=param, values=vals)

    # Pooled coverage + density.
    cov_pairs = [coverage_density(Xh, Xai_pool[s], k=3) for s in pool_samples]
    cov_vals = np.asarray([c["coverage"] for c in cov_pairs], dtype=float)
    den_vals = np.asarray([c["density"] for c in cov_pairs], dtype=float)
    split = split_half_reference(Xh, lambda A, B: coverage_density(A, B, k=3)["coverage"], n_splits=n_boot, seed=seed)
    rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="coverage", metric="coverage_geometric",
                            param="k=3", human_value=float(np.nanmedian(split)), ai_value=float(np.nanmean(cov_vals)),
                            effect_size=float(np.nanmean(cov_vals)), effect_type="coverage",
                            ci_lo=float(np.nanpercentile(cov_vals, 2.5)), ci_hi=float(np.nanpercentile(cov_vals, 97.5)),
                            inference="same_size_subsample_vs_split_half", stat=float(np.nanmean(cov_vals)),
                            p_raw=float((np.sum(cov_vals >= np.nanmedian(split)) + 1) / (len(cov_vals) + 1)),
                            n_human=n_h, n_ai=n_h, n_perm_or_boot=len(cov_vals),
                            notes="human_value = median split-half coverage (parity ref); " + pooled_note))
    rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="coverage", metric="coverage_density",
                            param="k=3", human_value=np.nan, ai_value=float(np.nanmean(den_vals)),
                            effect_size=float(np.nanmean(den_vals)), effect_type="density",
                            ci_lo=float(np.nanpercentile(den_vals, 2.5)), ci_hi=float(np.nanpercentile(den_vals, 97.5)),
                            inference="same_size_subsample", stat=float(np.nanmean(den_vals)),
                            n_human=n_h, n_ai=n_h, n_perm_or_boot=len(den_vals), notes=pooled_note))
    _persist_values(curves, base, group="All AI", facet="coverage", metric="coverage_geometric_pooled_subsample", param="k=3", values=cov_vals)
    _persist_values(curves, base, group="All AI", facet="coverage", metric="coverage_density_pooled_subsample", param="k=3", values=den_vals)
    _persist_values(curves, base, group="Human", facet="coverage", metric="coverage_geometric_split_half", param="k=3", values=split)

    # Pooled displacement: subsample distribution, referenced against the split-half floor.
    for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
        vals = np.asarray([stat_fn(Xh, Xai_pool[s]) for s in pool_samples], dtype=float)
        floor = split_half_reference(Xh, stat_fn, n_splits=min(n_boot, 500), seed=seed)
        p = float((np.sum(floor >= np.nanmean(vals)) + 1) / (len(floor) + 1))
        rows.append(_metric_row(**base_kwargs, comparison=comparison, facet="displacement", metric=metric,
                                human_value=None, ai_value=None, effect_size=float(np.nanmean(vals)),
                                effect_type="two_sample_distance",
                                ci_lo=float(np.nanpercentile(vals, 2.5)), ci_hi=float(np.nanpercentile(vals, 97.5)),
                                inference="same_size_subsample_vs_split_half_floor", stat=float(np.nanmean(vals)), p_raw=p,
                                n_human=n_h, n_ai=n_h, n_perm_or_boot=len(vals),
                                notes="p = fraction of human split-half floor >= pooled mean (exploratory); " + pooled_note))
        _persist_values(curves, base, group="All AI", facet="displacement", metric=f"{metric}_pooled_subsample", param="", values=vals)

    # Lexical robustness control (spec 1.9).
    rows.extend(_lexical_rows(master, idx, base_kwargs=base_kwargs, text_col="full_text",
                              n_perm=min(n_perm, 1000), seed=seed))

    tests_df = pd.DataFrame(rows)

    # Gradient tests (spec 1.6): predicted diversity ordering Claude < Gemini < GPT < Human.
    gradient_specs = [
        ("spread", "mean_pairwise", "", lambda Z: mean_pairwise(Z), "increasing", "claude<gemini<gpt<human"),
        ("richness", "vendi", "q=1", lambda Z: vendi_scores(Z, (1,))[1], "increasing", "claude<gemini<gpt<human"),
        ("dimensionality", "participation_ratio", "", participation_ratio, "increasing", "claude<gemini<gpt<human"),
        ("coverage", "coverage_geometric", "k=3", None, "increasing", "claude<gemini<gpt<human"),
        ("evenness", "ripley_excess", "r=pooled_q01_q50", lambda Z: -float(np.trapz(ripley_K(Z, radii) - null_K_mean, radii)), "increasing", "claude<gemini<gpt<human"),
        ("displacement", "mmd2", "", None, "decreasing", "claude>gemini>gpt (M5 flip: larger = more displaced)"),
    ]
    for facet, metric, param, stat_fn, direction, order_label in gradient_specs:
        if metric == "coverage_geometric":
            values = [coverage_density(Xh, X[idx[g]], k=3)["coverage"] for g in MODEL_GROUPS]
            values.append(float(np.nanmedian(split)))
            groups_for_jt = [np.array([v]) for v in values]
            note = "single coverage values per group; human = split-half median"
        elif metric == "mmd2":
            groups_for_jt = []
            values = []
            for g in MODEL_GROUPS:
                Xg = X[idx[g]]
                reps = np.asarray([mmd2_rbf(Xh, np.delete(Xg, i, axis=0)) for i in range(len(Xg))], dtype=float)
                groups_for_jt.append(reps)
                values.append(float(mmd2_rbf(Xh, Xg)))
            note = "JT over LOO replicates of Human<->model MMD2; predicted DECREASING (spec 8.2 direction flip)"
        else:
            groups_for_jt = [jackknife_ci(X[idx[g]], stat_fn)["replicates"] for g in ["Claude", "Gemini", "GPT", "Human"]]
            values = [float(stat_fn(X[idx[g]])) for g in ["Claude", "Gemini", "GPT", "Human"]]
            note = "JT over leave-one-out jackknife replicates"
        jt = jonckheere_terpstra(groups_for_jt, alternative=direction)
        if direction == "increasing":
            direction_ok = bool(all(x <= y for x, y in zip(values, values[1:])))
        else:
            direction_ok = bool(all(x >= y for x, y in zip(values, values[1:])))
        grad_rows.append({"condition": analysis.condition, "task": "proposals", "text_branch": text_branch,
                          "field": "whole", "facet": facet, "metric": metric, "param": param, "order": order_label,
                          "JT": jt["JT"], "p_raw": jt["p"], "p_fdr": np.nan, "direction_ok": direction_ok,
                          "notes": note})
    grad_df = pd.DataFrame(grad_rows)
    if not grad_df.empty:
        grad_df["p_fdr"] = benjamini_hochberg(grad_df["p_raw"])

    # Fingerprint null reference (redesign spec 3.1): M=999 same-n draws of the pooled
    # proposal cloud under the battery statistics. Ripley excess reuses the null_K curves
    # already drawn (same construction), so no extra draws are needed for it. Uses a
    # dedicated rng stream (seed+1) so every pre-existing seeded computation is untouched.
    null_stat_fns = {
        ("spread", "mean_pairwise", ""): mean_pairwise,
        ("richness", "vendi", "q=1"): lambda Z: vendi_scores(Z, (1,))[1],
        ("dimensionality", "participation_ratio", ""): participation_ratio,
        ("evenness", "vendi_slope", "q=0..2"): lambda Z: vendi_slope(vendi_scores(Z, (0, 2))),
    }
    null_records = pooled_null_reference(X, null_stat_fns, n=len(human), M=999, seed=seed + 1)
    for i, curve in enumerate(null_K):
        null_records.append({"facet": "evenness", "metric": "ripley_excess", "param": "r=pooled_q01_q50",
                             "draw_idx": i, "value": float(np.trapz(curve - null_K_mean, radii))})
    nulls_df = pd.DataFrame(null_records)
    for col, val in [("condition", analysis.condition), ("task", "proposals"),
                     ("text_branch", text_branch), ("field", "whole")]:
        nulls_df[col] = val
    return tests_df, grad_df, pd.DataFrame(curves), nulls_df


def _review_panel_metrics_human(Xh: np.ndarray, radii: np.ndarray, null_mean: np.ndarray) -> Dict[Tuple[str, str, str], float]:
    """Human panel values, computed once per proposal (independent of AI combos)."""
    m = Xh.shape[0]
    out = {
        ("richness", "vendi", "q=1"): vendi_scores(Xh, (1,))[1],
        ("dimensionality", "participation_ratio", ""): participation_ratio(Xh),
        ("dimensionality", "effective_rank", ""): effective_rank(Xh),
        ("coverage", "coverage_geometric", "k=panel_adaptive"): loo_self_coverage(Xh, k=3) if m >= 3 else np.nan,
        ("evenness", "vendi_slope", "q=0..2"): vendi_slope(vendi_scores(Xh, (0, 2))),
        ("evenness", "ripley_excess", "r=pooled_q01_q50"): float(np.trapz(ripley_K(Xh, radii) - null_mean, radii)),
    }
    for metric, stat_fn in SPREAD_STATS.items():
        out[("spread", metric, "")] = stat_fn(Xh)
    return out


def _review_panel_metrics_ai(Xh: np.ndarray, Xa: np.ndarray, radii: np.ndarray, null_mean: np.ndarray) -> Dict[Tuple[str, str, str], float]:
    """AI panel values for one enumerated exact-n combination."""
    m = Xh.shape[0]
    out = {
        ("richness", "vendi", "q=1"): vendi_scores(Xa, (1,))[1],
        ("dimensionality", "participation_ratio", ""): participation_ratio(Xa),
        ("dimensionality", "effective_rank", ""): effective_rank(Xa),
        ("coverage", "coverage_geometric", "k=panel_adaptive"): coverage_density(Xh, Xa, k=min(3, max(1, m - 1)))["coverage"],
        ("evenness", "vendi_slope", "q=0..2"): vendi_slope(vendi_scores(Xa, (0, 2))),
        ("evenness", "ripley_excess", "r=pooled_q01_q50"): float(np.trapz(ripley_K(Xa, radii) - null_mean, radii)),
    }
    for metric, stat_fn in SPREAD_STATS.items():
        out[("spread", metric, "")] = stat_fn(Xa)
    return out


def build_review_facet_outputs(
    analysis: Any,
    combination_cache: Mapping[str, Mapping[str, Dict[str, Any]]],
    *,
    text_branch: str,
    field: str = "whole",
    n_boot: int = 1000,
    n_perm: int = 10000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute paired review facet outputs for one condition and field."""
    review_master = analysis.review_master.copy()
    X = l2_normalize(np.asarray(analysis.review_embeddings["embeddings"], dtype=float))
    uid_to_idx = {str(uid): i for i, uid in enumerate(review_master["review_uid"].astype(str))}
    cohort_by_target: Dict[str, str] = {}
    if "target_cohort" in review_master.columns:
        cohort_by_target = (review_master.groupby(review_master["target_proposal_uid"].astype(str))["target_cohort"]
                            .first().astype(str).to_dict())
    rows: List[Dict[str, Any]] = []
    paired_rows: List[Dict[str, Any]] = []
    curves: List[Dict[str, Any]] = []
    per_metric_values: Dict[Tuple[str, str, str], List[Tuple[float, float]]] = {}
    base = dict(condition=analysis.condition, task="reviews", text_branch=text_branch, field=field)
    base_kwargs = dict(condition=analysis.condition, task="reviews", text_branch=text_branch, field=field)

    # Shared radii + per-panel-size pooled-cloud nulls (spec 7.2): one grid per cell,
    # M=999 draws of size m from the whole review cloud.
    radii = _radii_from_pooled(X)
    panel_sizes = sorted({len(info["human_review_uids"]) for comp in combination_cache.values() for info in comp.values() if info.get("eligible", False)})
    null_mean_by_m: Dict[int, np.ndarray] = {}
    for m in panel_sizes:
        null_curves = _null_curves_from_pool(X, radii, n=m, B=999, seed=seed + m, curve_fn=ripley_K)
        null_mean_by_m[m] = np.nanmean(null_curves, axis=0)

    # Whole-cloud illustration curves at EQUAL n (groups subsampled to the human count).
    curve_groups: Dict[str, np.ndarray] = {}
    if "source_group" in review_master.columns:
        for group in ["Human", *MODEL_GROUPS]:
            idx = review_master.index[review_master["source_group"].eq(group)].to_numpy()
            if len(idx) >= 2:
                curve_groups[group] = idx
    if "review_source" in review_master.columns:
        ai_idx_all = review_master.index[review_master["review_source"].eq("ai")].to_numpy()
    elif "source_family" in review_master.columns:
        ai_idx_all = review_master.index[review_master["source_family"].ne("human")].to_numpy()
    else:
        ai_idx_all = np.array([], dtype=int)
    if len(ai_idx_all) >= 2:
        curve_groups["All AI"] = ai_idx_all
    if curve_groups:
        n_ref = min(len(v) for v in curve_groups.values())
        null_curves_ref = _null_curves_from_pool(X, radii, n=n_ref, B=999, seed=seed, curve_fn=ripley_K)
        envelope_ref = {"lo_env": np.nanpercentile(null_curves_ref, 2.5, axis=0), "hi_env": np.nanpercentile(null_curves_ref, 97.5, axis=0)}
        # For the illustration band use the simultaneous form as well.
        center = np.nanmean(null_curves_ref, axis=0)
        k95 = float(np.nanpercentile(np.nanmax(np.abs(null_curves_ref - center[None, :]), axis=1), 95))
        envelope_ref = {"lo_env": center - k95, "hi_env": center + k95}
        for group, idx_for_group in curve_groups.items():
            _append_equal_n_curve_rows(curves, base=base, group=group, X_group=X[idx_for_group],
                                       n_ref=n_ref, radii=radii, envelope=envelope_ref, seed=seed)

    for comparison in ["all_ai", "claude", "gemini", "gpt"]:
        comp_map = combination_cache.get(comparison, {})
        comparison_name = "human_vs_pooled_ai" if comparison == "all_ai" else f"human_vs_{comparison}"
        values_by_metric: Dict[Tuple[str, str, str], List[Tuple[str, float, float, int]]] = {}
        for target_uid, info in comp_map.items():
            if not info.get("eligible", False):
                continue
            human_uids = [str(u) for u in info["human_review_uids"]]
            human_idx = [uid_to_idx[u] for u in human_uids]
            Xh = X[human_idx]
            m = len(human_idx)
            null_mean = null_mean_by_m[m]
            h_metrics = _review_panel_metrics_human(Xh, radii, null_mean)
            ai_metric_accum: Dict[Tuple[str, str, str], List[float]] = {}
            for combo in info["ai_panel_combinations"]:
                ai_idx = [uid_to_idx[str(u)] for u in combo]
                Xa = X[ai_idx]
                metrics = _review_panel_metrics_ai(Xh, Xa, radii, null_mean)
                for key, a_val in metrics.items():
                    ai_metric_accum.setdefault(key, []).append(a_val)
            for key, ai_vals in ai_metric_accum.items():
                h_val = h_metrics[key]
                ai_val = float(np.nanmean(ai_vals))
                values_by_metric.setdefault(key, []).append((str(target_uid), h_val, ai_val, m))

        for (facet, metric, param), vals in values_by_metric.items():
            if not vals:
                continue
            target_uids, h_vals, a_vals, ns = zip(*vals)
            h_arr = np.asarray(h_vals, dtype=float)
            a_arr = np.asarray(a_vals, dtype=float)
            test = paired_wilcoxon(h_arr, a_arr)
            delta_lo, delta_hi = paired_delta_bootstrap_ci(h_arr, a_arr, seed=seed)
            # Spec 1A.9 orientation: Cliff's delta (AI - Human) - negative = AI panels lower.
            delta_ai = -test["cliffs_delta"]
            delta_ci = (-delta_hi if np.isfinite(delta_hi) else np.nan, -delta_lo if np.isfinite(delta_lo) else np.nan)
            notes = ("paired across target proposals; AI value = mean over exact-n enumerated panels; "
                     "effect = Cliff's delta (AI - Human), negative = AI lower; ci = bootstrap 95% CI of the delta (resampling proposals)")
            if metric == "coverage_geometric":
                notes += "; human reference = leave-one-out self-coverage, defined for m>=3 panels only (spec 11.2 k-vs-m decision)"
            if metric == "ripley_excess":
                notes += "; excess area vs pooled review-cloud null at matched panel size m"
            rows.append(_metric_row(**base_kwargs, comparison=comparison_name, facet=facet, metric=metric, param=param,
                                    human_value=float(np.nanmean(h_arr)), ai_value=float(np.nanmean(a_arr)),
                                    effect_size=delta_ai, effect_type="cliffs_delta",
                                    ci_lo=delta_ci[0], ci_hi=delta_ci[1],
                                    inference="paired_wilcoxon", stat=test["W"], p_raw=test["p"],
                                    n_human=float(np.nanmean(ns)), n_ai=float(np.nanmean(ns)),
                                    n_perm_or_boot=test["n_pairs"], notes=notes))
            per_metric_values[(comparison_name, metric, param)] = list(zip(h_arr, a_arr))
            for target_uid, h_val, a_val, n_h in vals:
                paired_rows.append({"condition": analysis.condition, "text_branch": text_branch, "field": field,
                                    "comparison": comparison_name, "facet": facet, "metric": metric, "param": param,
                                    "target_proposal_uid": target_uid,
                                    "target_cohort": cohort_by_target.get(str(target_uid), ""),
                                    "n_human_reviews": n_h, "human_value": h_val, "ai_value": a_val,
                                    "paired_diff": h_val - a_val})

    # Reviews M5: pooled whole-cloud exploratory companion, not paired (spec 8.5).
    if field == "whole":
        human_idx = review_master.index[review_master["review_source"].eq("human")].to_numpy()
        ai_idx = review_master.index[review_master["review_source"].eq("ai")].to_numpy()
        mmd_res = mmd2_permutation_test(X[human_idx], X[ai_idx], B=n_perm, seed=seed)
        rows.append(_metric_row(**base_kwargs, comparison="human_vs_pooled_ai", facet="displacement", metric="mmd2",
                                human_value=None, ai_value=None, effect_size=mmd_res["delta_obs"],
                                effect_type="two_sample_distance",
                                ci_lo=float(np.nanpercentile(mmd_res["null"], 2.5)), ci_hi=float(np.nanpercentile(mmd_res["null"], 97.5)),
                                inference="two_sample_permutation", stat=mmd_res["delta_obs"], p_raw=mmd_res["p_two_sided"],
                                n_human=len(human_idx), n_ai=len(ai_idx), n_perm_or_boot=n_perm,
                                notes="M5 review companion; UNPAIRED whole-cloud, exploratory (spec 8.5); ci = permutation null band"))
        try:
            ot_res = ot_permutation_test(X[human_idx], X[ai_idx], B=min(n_perm, 1000), seed=seed)
            rows.append(_metric_row(**base_kwargs, comparison="human_vs_pooled_ai", facet="displacement", metric="ot_wasserstein",
                                    human_value=None, ai_value=None, effect_size=ot_res["delta_obs"],
                                    effect_type="two_sample_distance",
                                    ci_lo=float(np.nanpercentile(ot_res["null"], 2.5)), ci_hi=float(np.nanpercentile(ot_res["null"], 97.5)),
                                    inference="two_sample_permutation", stat=ot_res["delta_obs"], p_raw=ot_res["p_two_sided"],
                                    n_human=len(human_idx), n_ai=len(ai_idx), n_perm_or_boot=min(n_perm, 1000),
                                    notes="M5 review companion; UNPAIRED whole-cloud, exploratory (spec 8.5)"))
        except ImportError:
            pass

    tests_df = pd.DataFrame(rows)

    # Gradient over paired Human-AI differences. Predicted diversity ordering is
    # Claude < Gemini < GPT (< Human), so the paired differences (Human - AI) are
    # predicted to DECREASE from Claude to GPT (spec 1.6 + 11.3).
    grad_rows = []
    for facet, metric, param in [("richness", "vendi", "q=1"),
                                 ("spread", "mean_pairwise", ""),
                                 ("dimensionality", "participation_ratio", ""),
                                 ("coverage", "coverage_geometric", "k=panel_adaptive"),
                                 ("evenness", "ripley_excess", "r=pooled_q01_q50")]:
        vals = []
        for comp in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt"]:
            key = (comp, metric, param)
            if key not in per_metric_values:
                vals.append(np.array([np.nan]))
            else:
                h, a = zip(*per_metric_values[key])
                vals.append(np.asarray(h, dtype=float) - np.asarray(a, dtype=float))
        if all(np.isfinite(v).any() for v in vals):
            jt = jonckheere_terpstra(vals, alternative="decreasing")
            means = [float(np.nanmean(v)) for v in vals]
            grad_rows.append({"condition": analysis.condition, "task": "reviews", "text_branch": text_branch,
                              "field": field, "facet": facet, "metric": metric, "param": param,
                              "order": "claude<gemini<gpt<human (diversity); paired diffs predicted decreasing",
                              "JT": jt["JT"], "p_raw": jt["p"], "p_fdr": np.nan,
                              "direction_ok": bool(all(x >= y for x, y in zip(means, means[1:]))),
                              "notes": "JT over paired Human-AI differences by model, alternative = decreasing"})
    grad_df = pd.DataFrame(grad_rows)
    if not grad_df.empty:
        grad_df["p_fdr"] = benjamini_hochberg(grad_df["p_raw"])
    return tests_df, grad_df, pd.DataFrame(curves), pd.DataFrame(paired_rows)


# ---------------------------------------------------------------------------
# Interleaving statistics (descriptive; SI panel). Answers "does either group
# occupy territory the other never touches?" via cross-group nearest-neighbor
# distances, benchmarked against human-to-human spacing. No inference is run.
# ---------------------------------------------------------------------------

def interleaving_distances(X_human: np.ndarray, X_ai: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cross-group NN distances: (AI->nearest human, human->nearest other human, human->nearest AI)."""
    Xh = l2_normalize(X_human)
    Xa = l2_normalize(X_ai)
    D_ah = cosine_dist(Xa, Xh)
    d_ah = D_ah.min(axis=1)
    d_ha = D_ah.min(axis=0)
    D_hh = cosine_dist(Xh)
    np.fill_diagonal(D_hh, np.inf)
    d_hh = D_hh.min(axis=1)
    return d_ah, d_hh, d_ha


def interleaving_summary(d_ah: np.ndarray, d_hh: np.ndarray, d_ha: np.ndarray) -> Dict[str, float]:
    """Summary rows for the interleaving CSV.

    The yardstick is q90 of human-to-human NN spacing: 'human-only fringe' = share of
    human items whose nearest AI item is farther than that yardstick; 'AI-only pocket'
    = share of AI items whose nearest human item is farther. By construction ~10% of
    human items exceed the yardstick against their own group - that is the reference
    rate against which the two shares are read.
    """
    d_ah = np.asarray(d_ah, dtype=float)
    d_hh = np.asarray(d_hh, dtype=float)
    d_ha = np.asarray(d_ha, dtype=float)
    q90 = float(np.percentile(d_hh, 90))
    return {
        "ai_to_nearest_human_median": float(np.median(d_ah)),
        "ai_to_nearest_human_q90": float(np.percentile(d_ah, 90)),
        "human_to_nearest_human_median": float(np.median(d_hh)),
        "human_to_nearest_human_q90": q90,
        "human_to_nearest_ai_median": float(np.median(d_ha)),
        "human_to_nearest_ai_q90": float(np.percentile(d_ha, 90)),
        "share_human_fringe": float(np.mean(d_ha > q90)),
        "share_ai_pocket": float(np.mean(d_ah > q90)),
        "n_ai": float(len(d_ah)),
        "n_human": float(len(d_hh)),
    }


# ---------------------------------------------------------------------------
# M6 domain-coverage helpers (union metrics; used by notebook 02).
# ---------------------------------------------------------------------------

def popcount(x: int) -> int:
    return bin(x).count("1")


def union_mask(masks: Sequence[int], rows: Iterable[int]) -> int:
    out = 0
    for r in rows:
        out |= masks[int(r)]
    return out


def union_count(masks: Sequence[int], rows: Iterable[int]) -> int:
    return popcount(union_mask(masks, rows))


def permutation_union_test(masks: Sequence[int], rows_a: np.ndarray, rows_b: np.ndarray,
                           *, B: int = 10000, seed: int = 42) -> Dict[str, Any]:
    """Label-permutation test on the union-count difference (spec 9.3, within_diff mode)."""
    rows_a = np.asarray(rows_a, dtype=int)
    rows_b = np.asarray(rows_b, dtype=int)
    combined = np.concatenate([rows_a, rows_b])
    n_a = len(rows_a)
    obs = union_count(masks, rows_a) - union_count(masks, rows_b)
    rng = np.random.default_rng(seed)
    null = np.empty(B, dtype=float)
    for i in range(B):
        perm = rng.permutation(len(combined))
        sel = combined[perm]
        null[i] = union_count(masks, sel[:n_a]) - union_count(masks, sel[n_a:])
    p = float((np.sum(np.abs(null) >= abs(obs)) + 1) / (B + 1))
    return {"delta_obs": float(obs), "p_two_sided": p, "null": null}


def jackknife_union(masks: Sequence[int], rows: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    """Leave-one-out jackknife for a union count."""
    rows = np.asarray(rows, dtype=int)
    point = union_count(masks, rows)
    reps = np.asarray([union_count(masks, np.delete(rows, i)) for i in range(len(rows))], dtype=float)
    lo, hi = np.nanpercentile(reps, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"point": float(point), "lo": float(lo), "hi": float(hi), "replicates": reps}


def write_facet_outputs(
    tables_dir: Path,
    figures_dir: Path,
    tests_df: pd.DataFrame,
    gradient_df: pd.DataFrame,
    curves_df: pd.DataFrame,
    paired_df: pd.DataFrame | None = None,
) -> None:
    """Persist standard facet output files (legacy helper; notebooks now write directly)."""
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    tests_df.to_csv(tables_dir / "facet_diversity_tests.csv", index=False)
    gradient_df.to_csv(tables_dir / "facet_diversity_gradient.csv", index=False)
    curves_to_write = curves_df.copy()
    for numeric_col in ["x", "y", "y_lo", "y_hi"]:
        if numeric_col in curves_to_write.columns:
            curves_to_write[numeric_col] = pd.to_numeric(curves_to_write[numeric_col], errors="coerce")
    try:
        curves_to_write.to_parquet(tables_dir / "facet_diversity_curves.parquet", index=False)
    except Exception:
        curves_to_write.to_csv(tables_dir / "facet_diversity_curves.csv", index=False)
    if paired_df is not None and not paired_df.empty:
        paired_df.to_csv(tables_dir / "facet_review_paired_long.csv", index=False)


# ---------------------------------------------------------------------------
# Simpson diversity index (explicit, for reporting) - spec companion to richness.
# Two flavors, both at matched sample size:
#   * similarity-sensitive (embedding): Simpson on the kernel eigenvalues; inverse
#     Simpson == Vendi VS_2, Gini-Simpson == 1 - mean squared cosine similarity.
#   * classical categorical: textbook D = sum(p_i^2) on discrete literature regions.
# Inference mirrors the facet battery: per-model 23-vs-23 label permutation, pooled
# Human-vs-All-AI via cached equal-n subsamples, jackknife CIs; reviews are paired
# within proposal with Cliff's delta, exactly like the other review facets.
# ---------------------------------------------------------------------------

_SIMPSON_KINDS = (("gini_simpson", "gini"), ("inverse_simpson", "inverse"))


def build_proposal_simpson_tests(
    embeddings: np.ndarray,
    master: pd.DataFrame,
    idx_cache: np.ndarray,
    *,
    condition: str,
    text_branch: str,
    region_labels: Sequence[Any] | None = None,
    n_perm: int = 10000,
    seed: int = 42,
) -> pd.DataFrame:
    """Simpson diversity for proposals (similarity-sensitive + optional categorical).

    `embeddings` is the full proposal embedding matrix; `master` provides the group
    membership; `idx_cache` is the cached (B, n_human) without-replacement subsample of
    the pooled-AI rows used everywhere else for equal-n comparison; `region_labels`, if
    given (one discrete literature region per proposal, NaN allowed), adds the classical
    categorical Simpson. All comparisons are Human vs each model and Human vs pooled AI at
    matched n = 23.
    """
    X = np.asarray(embeddings, dtype=float)
    groups = _group_indices(master)
    human_idx = groups["Human"]
    ai_pool = groups["All AI"]
    model_groups = [g for g in MODEL_GROUPS if g in groups and len(groups[g])]
    rows: List[Dict[str, Any]] = []
    base = dict(condition=condition, task="proposals", text_branch=text_branch, field="whole")

    def _emit_similarity(kind_label, kind):
        stat = lambda M: simpson_similarity(M, kind=kind)   # noqa: E731
        h_ci = jackknife_ci(X[human_idx], stat)
        # Per-model, 23 vs 23, label permutation on the within-group Simpson difference.
        for g in model_groups:
            g_ci = jackknife_ci(X[groups[g]], stat)
            perm = label_permutation_test(X[human_idx], X[groups[g]], stat, B=n_perm, seed=seed, mode="within_diff")
            rows.append(_metric_row(**base, comparison=f"human_vs_{g.lower()}", facet="simpson_similarity",
                                    metric=kind_label, param="", human_value=h_ci["point"], ai_value=g_ci["point"],
                                    effect_size=(g_ci["point"] / h_ci["point"] if h_ci["point"] else np.nan),
                                    effect_type="ratio", ci_lo=g_ci["lo"], ci_hi=g_ci["hi"],
                                    human_ci_lo=h_ci["lo"], human_ci_hi=h_ci["hi"], inference="permutation",
                                    stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=len(human_idx), n_ai=len(groups[g]),
                                    n_perm_or_boot=n_perm, notes="similarity-sensitive Simpson on kernel eigenvalues; "
                                    "higher = more diverse; equal-n; ci = 95% jackknife"))
        # Pooled Human vs All-AI via the shared equal-n subsample cache (idx_cache holds
        # full-master row indices of the sampled AI proposals, so pass the full matrix).
        vals = subsample_pooled(X, idx_cache, stat)
        ai_mean = float(np.nanmean(vals))
        # two-sided empirical p: how often the equal-n AI draw is at least as extreme as human
        p = float((np.sum(np.abs(vals - ai_mean) >= abs(h_ci["point"] - ai_mean)) + 1) / (len(vals) + 1))
        rows.append(_metric_row(**base, comparison="human_vs_pooled_ai", facet="simpson_similarity",
                                metric=kind_label, param="", human_value=h_ci["point"], ai_value=ai_mean,
                                effect_size=(ai_mean / h_ci["point"] if h_ci["point"] else np.nan), effect_type="ratio",
                                ci_lo=float(np.percentile(vals, 2.5)), ci_hi=float(np.percentile(vals, 97.5)),
                                human_ci_lo=h_ci["lo"], human_ci_hi=h_ci["hi"], inference="same_size_subsample",
                                stat=h_ci["point"] - ai_mean, p_raw=p, n_human=len(human_idx), n_ai=len(human_idx),
                                n_perm_or_boot=len(vals), notes="similarity-sensitive Simpson; AI n=23 subsampled from "
                                "69 (without replacement); higher = more diverse"))

    for kind_label, kind in _SIMPSON_KINDS:
        _emit_similarity(kind_label, kind)

    if region_labels is not None:
        labels = np.asarray(region_labels, dtype=float)   # NaN = outlier/unassigned

        def cat_stat(idx, kind):
            return simpson_categorical(labels[np.asarray(idx, dtype=int)])[kind]

        for kind_label, kind in _SIMPSON_KINDS:
            h_point = cat_stat(human_idx, kind)
            # Per-model permutation on the categorical Simpson (shuffle the human/model labels).
            for g in model_groups:
                g_point = cat_stat(groups[g], kind)
                pooled = np.concatenate([human_idx, groups[g]])
                rng = np.random.default_rng(seed)
                obs = abs(h_point - g_point)
                nh = len(human_idx)
                count = 0
                for _ in range(n_perm):
                    perm = rng.permutation(pooled)
                    d = abs(cat_stat(perm[:nh], kind) - cat_stat(perm[nh:], kind))
                    if d >= obs - 1e-12:
                        count += 1
                p = (count + 1) / (n_perm + 1)
                rows.append(_metric_row(**base, comparison=f"human_vs_{g.lower()}", facet="simpson_categorical",
                                        metric=kind_label, param="literature_region", human_value=h_point, ai_value=g_point,
                                        effect_size=(g_point / h_point if h_point else np.nan), effect_type="ratio",
                                        inference="permutation", stat=obs, p_raw=p, n_human=len(human_idx), n_ai=len(groups[g]),
                                        n_perm_or_boot=n_perm, notes="classical Simpson on the nearest-literature-region label "
                                        "(BERTopic outlier bin dropped); higher = more diverse; equal-n"))
            # Pooled: categorical Simpson over the same equal-n AI subsamples.
            vals = np.asarray([cat_stat(sample, kind) for sample in idx_cache], dtype=float)
            ai_mean = float(np.nanmean(vals))
            p = float((np.sum(np.abs(vals - ai_mean) >= abs(h_point - ai_mean)) + 1) / (len(vals) + 1))
            rows.append(_metric_row(**base, comparison="human_vs_pooled_ai", facet="simpson_categorical",
                                    metric=kind_label, param="literature_region", human_value=h_point, ai_value=ai_mean,
                                    effect_size=(ai_mean / h_point if h_point else np.nan), effect_type="ratio",
                                    ci_lo=float(np.percentile(vals, 2.5)), ci_hi=float(np.percentile(vals, 97.5)),
                                    inference="same_size_subsample", stat=h_point - ai_mean, p_raw=p,
                                    n_human=len(human_idx), n_ai=len(human_idx), n_perm_or_boot=len(vals),
                                    notes="classical Simpson on nearest literature region; AI n=23 subsampled from 69"))
    return pd.DataFrame(rows)


def build_review_simpson_tests(
    review_master: pd.DataFrame,
    review_embeddings: Mapping[str, Any],
    combination_cache: Mapping[str, Mapping[str, Dict[str, Any]]],
    *,
    condition: str,
    text_branch: str,
    field: str = "whole",
    seed: int = 42,
) -> pd.DataFrame:
    """Similarity-sensitive Simpson for review panels, paired within proposal.

    Mirrors `build_review_facet_outputs`: for each target proposal the human panel's
    Simpson is compared with the mean over the exact-n enumerated AI panels of the same
    size, then combined across proposals with a paired Wilcoxon and Cliff's delta
    (AI - Human; negative = AI panels less diverse). Only the embedding (similarity-
    sensitive) Simpson applies to reviews - there is no literature-region label here.
    """
    X = l2_normalize(np.asarray(review_embeddings["embeddings"], dtype=float))
    uid_to_idx = {str(uid): i for i, uid in enumerate(review_master["review_uid"].astype(str))}
    rows: List[Dict[str, Any]] = []
    base = dict(condition=condition, task="reviews", text_branch=text_branch, field=field)

    for comparison in ["all_ai", "claude", "gemini", "gpt"]:
        comp_map = combination_cache.get(comparison, {})
        comparison_name = "human_vs_pooled_ai" if comparison == "all_ai" else f"human_vs_{comparison}"
        for kind_label, kind in _SIMPSON_KINDS:
            h_vals, a_vals, ns = [], [], []
            for _target_uid, info in comp_map.items():
                if not info.get("eligible", False):
                    continue
                human_idx = [uid_to_idx[str(u)] for u in info["human_review_uids"]]
                combos = info["ai_panel_combinations"]
                if len(human_idx) < 2 or not combos:
                    continue
                h_val = simpson_similarity(X[human_idx], kind=kind)
                combo_vals = [simpson_similarity(X[[uid_to_idx[str(u)] for u in combo]], kind=kind) for combo in combos]
                h_vals.append(h_val)
                a_vals.append(float(np.nanmean(combo_vals)))
                ns.append(len(human_idx))
            if not h_vals:
                continue
            h_arr = np.asarray(h_vals, dtype=float)
            a_arr = np.asarray(a_vals, dtype=float)
            test = paired_wilcoxon(h_arr, a_arr)
            delta_lo, delta_hi = paired_delta_bootstrap_ci(h_arr, a_arr, seed=seed)
            delta_ai = -test["cliffs_delta"]
            ci = (-delta_hi if np.isfinite(delta_hi) else np.nan, -delta_lo if np.isfinite(delta_lo) else np.nan)
            rows.append(_metric_row(**base, comparison=comparison_name, facet="simpson_similarity", metric=kind_label,
                                    param="", human_value=float(np.nanmean(h_arr)), ai_value=float(np.nanmean(a_arr)),
                                    effect_size=delta_ai, effect_type="cliffs_delta", ci_lo=ci[0], ci_hi=ci[1],
                                    inference="paired_wilcoxon", stat=test["W"], p_raw=test["p"],
                                    n_human=float(np.nanmean(ns)), n_ai=float(np.nanmean(ns)), n_perm_or_boot=test["n_pairs"],
                                    notes="similarity-sensitive Simpson per panel; paired across proposals; AI = mean over "
                                    "exact-n panels; Cliff's delta (AI - Human), negative = AI panels less diverse"))
    return pd.DataFrame(rows)
