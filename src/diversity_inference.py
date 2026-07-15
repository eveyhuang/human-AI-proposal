"""
Inference and notebook-adapter helpers for diversity-facet analyses.
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
    mean_pairwise,
    mmd2_rbf,
    mst_dispersion,
    nn_isolation,
    nn_distances,
    participation_ratio,
    ripley_K,
    sparseness,
    spherical_variance,
    vendi_evenness_slope,
    vendi_scores,
    wasserstein_ot,
)


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
        return {"W": np.nan, "p": np.nan, "cliffs_delta": np.nan}
    diff = x - y
    if np.allclose(diff, 0):
        W, p = 0.0, 1.0
    else:
        res = wilcoxon(x, y, zero_method="wilcox", alternative="two-sided", mode="auto")
        W, p = float(res.statistic), float(res.pvalue)
    nonzero = diff[np.abs(diff) > 0]
    delta = 0.0 if nonzero.size == 0 else float((np.sum(nonzero > 0) - np.sum(nonzero < 0)) / nonzero.size)
    return {"W": W, "p": p, "cliffs_delta": delta}


def benjamini_hochberg(pvals: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(pvals), dtype=float)
    out = np.full(p.shape, np.nan, dtype=float)
    mask = np.isfinite(p)
    if mask.any():
        out[mask] = multipletests(p[mask], method="fdr_bh")[1]
    return out


def global_envelope_test(obs_curve: np.ndarray, null_curves: np.ndarray) -> Dict[str, Any]:
    """Simple simultaneous envelope test based on max absolute null deviation."""
    obs = np.asarray(obs_curve, dtype=float)
    null = np.asarray(null_curves, dtype=float)
    if null.ndim != 2 or null.shape[0] == 0:
        return {"p": np.nan, "lo_env": np.full_like(obs, np.nan), "hi_env": np.full_like(obs, np.nan)}
    center = np.nanmean(null, axis=0)
    obs_stat = float(np.nanmax(np.abs(obs - center)))
    null_stats = np.nanmax(np.abs(null - center[None, :]), axis=1)
    p = float((np.sum(null_stats >= obs_stat) + 1) / (len(null_stats) + 1))
    lo, hi = np.nanpercentile(null, [2.5, 97.5], axis=0)
    return {"p": p, "lo_env": lo, "hi_env": hi, "stat": obs_stat}


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


def _mean_pairwise(X: np.ndarray) -> float:
    D = cosine_dist(X)
    tri = D[np.triu_indices(D.shape[0], k=1)]
    return float(np.mean(tri)) if tri.size else np.nan


def _centroid_loo(X: np.ndarray) -> float:
    Xn = l2_normalize(X)
    vals = []
    for i in range(Xn.shape[0]):
        others = np.delete(Xn, i, axis=0)
        c = others.mean(axis=0)
        norm_c = np.linalg.norm(c)
        if norm_c > 0:
            vals.append(1.0 - float(np.clip(Xn[i] @ (c / norm_c), -1.0, 1.0)))
    return float(np.mean(vals)) if vals else np.nan


def _mst_dispersion(X: np.ndarray) -> float:
    from scipy.sparse.csgraph import minimum_spanning_tree

    D = cosine_dist(X)
    mst = minimum_spanning_tree(D)
    return float(np.mean(mst.data)) if mst.data.size else np.nan


def _sparseness(X: np.ndarray) -> float:
    Xn = l2_normalize(X)
    c = Xn.mean(axis=0)
    norm_c = np.linalg.norm(c)
    if norm_c == 0:
        return np.nan
    c = c / norm_c
    return float(np.mean(1.0 - np.clip(Xn @ c, -1.0, 1.0)))


SPREAD_STATS = {
    "mean_pairwise": mean_pairwise,
    "centroid_loo": centroid_dispersion_loo,
    "mst_dispersion": mst_dispersion,
    "sparseness": sparseness,
    "nn_isolation": nn_isolation,
    "spherical_variance": spherical_variance,
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


def _append_embedding_curve_rows(
    curves: List[Dict[str, Any]],
    *,
    condition: str,
    task: str,
    text_branch: str,
    field: str,
    group: str,
    X_group: np.ndarray,
    radii: np.ndarray,
    null_K: np.ndarray,
) -> None:
    """Append tidy curve rows for one embedding group."""
    Xg = l2_normalize(np.asarray(X_group, dtype=float))
    if Xg.shape[0] < 2:
        return

    qs = (0, 0.5, 1, 2, 4, np.inf)
    scores = vendi_scores(Xg, qs)
    for q in qs:
        curves.append({
            "condition": condition,
            "task": task,
            "text_branch": text_branch,
            "field": field,
            "group": group,
            "facet": "richness",
            "metric": "vendi_profile",
            "x": float(q),
            "y": float(scores[q]),
            "y_lo": np.nan,
            "y_hi": np.nan,
        })

    kernel_eigs = np.linalg.eigvalsh((Xg @ Xg.T) / Xg.shape[0])
    for pos, val in enumerate(sorted(np.clip(kernel_eigs, 0, None), reverse=True), start=1):
        curves.append({
            "condition": condition,
            "task": task,
            "text_branch": text_branch,
            "field": field,
            "group": group,
            "facet": "richness",
            "metric": "kernel_eigen_scree",
            "x": pos,
            "y": float(val),
            "y_lo": np.nan,
            "y_hi": np.nan,
        })

    X_centered = Xg - Xg.mean(axis=0, keepdims=True)
    singular_values = np.linalg.svd(X_centered, full_matrices=False, compute_uv=False)
    variance = np.square(singular_values)
    if np.nansum(variance) > 0:
        cumulative_variance = np.cumsum(variance / np.nansum(variance))
        for pos, val in enumerate(cumulative_variance, start=1):
            curves.append({
                "condition": condition,
                "task": task,
                "text_branch": text_branch,
                "field": field,
                "group": group,
                "facet": "dimensionality",
                "metric": "participation_ratio_scree",
                "x": pos,
                "y": float(val),
                "y_lo": np.nan,
                "y_hi": np.nan,
            })

    K_curve = ripley_K(Xg, radii)
    G_curve = g_function(Xg, radii)
    if null_K.size:
        lo_env, hi_env = np.nanpercentile(null_K, [2.5, 97.5], axis=0)
    else:
        lo_env = np.full(len(radii), np.nan)
        hi_env = np.full(len(radii), np.nan)
    for r, y, lo, hi in zip(radii, K_curve, lo_env, hi_env):
        curves.append({
            "condition": condition,
            "task": task,
            "text_branch": text_branch,
            "field": field,
            "group": group,
            "facet": "evenness",
            "metric": "ripley_K",
            "x": float(r),
            "y": float(y),
            "y_lo": float(lo),
            "y_hi": float(hi),
        })
    for r, y in zip(radii, G_curve):
        curves.append({
            "condition": condition,
            "task": task,
            "text_branch": text_branch,
            "field": field,
            "group": group,
            "facet": "evenness",
            "metric": "g_function",
            "x": float(r),
            "y": float(y),
            "y_lo": np.nan,
            "y_hi": np.nan,
        })


def _add_fdr(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    group_cols = [c for c in ["task", "text_branch", "field"] if c in out.columns]
    for _, idx in out.groupby(group_cols, dropna=False).groups.items():
        out.loc[list(idx), "p_fdr"] = benjamini_hochberg(out.loc[list(idx), "p_raw"])
    return out


def build_proposal_facet_outputs(
    analysis: Any,
    *,
    text_branch: str,
    bootstrap_ai_idx_samples: np.ndarray,
    n_perm: int = 10000,
    n_boot: int = 1000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute proposal facet tests, gradient rows, and curve rows for one condition."""
    master = analysis.proposal_master.copy()
    X = l2_normalize(np.asarray(analysis.full_embeddings["embeddings"], dtype=float))
    idx = _group_indices(master)
    human = idx["Human"]
    rows: List[Dict[str, Any]] = []
    curves: List[Dict[str, Any]] = []
    grad_rows: List[Dict[str, Any]] = []
    qs = (0, 0.5, 1, 2, 4, np.inf)
    radii = _radii_from_pooled(X)
    null_K = _null_curves_from_pool(X, radii, n=len(human), B=999, seed=seed, curve_fn=ripley_K)
    null_K_mean = np.nanmean(null_K, axis=0)

    def add_profile_curves(group: str, Xg: np.ndarray) -> None:
        _append_embedding_curve_rows(
            curves,
            condition=analysis.condition,
            task="proposals",
            text_branch=text_branch,
            field="whole",
            group=group,
            X_group=Xg,
            radii=radii,
            null_K=null_K,
        )

    for group in ["Human", *MODEL_GROUPS, "All AI"]:
        if group == "All AI":
            continue
        add_profile_curves(group, X[idx[group]])

    for group in MODEL_GROUPS:
        Xh = X[human]
        Xg = X[idx[group]]
        comparison = _comparison_from_group(group)
        n_h, n_g = len(Xh), len(Xg)

        for metric, stat_fn in SPREAD_STATS.items():
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_jk = jackknife_ci(Xh, stat_fn)
            g_jk = jackknife_ci(Xg, stat_fn)
            ratio = h_jk["point"] / g_jk["point"] if g_jk["point"] else np.nan
            rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="spread", metric=metric, human_value=h_jk["point"], ai_value=g_jk["point"], effect_size=ratio, effect_type="ratio", ci_lo=g_jk["lo"], ci_hi=g_jk["hi"], inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm, notes="existing spread facet tagged for synthesis"))

        for q in (0, 1, 2):
            stat_fn = lambda Z, q=q: vendi_scores(Z, (q,))[q]
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_jk = jackknife_ci(Xh, stat_fn)
            g_jk = jackknife_ci(Xg, stat_fn)
            ratio = h_jk["point"] / g_jk["point"] if g_jk["point"] else np.nan
            rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="richness", metric="vendi", param=f"q={q}", human_value=h_jk["point"], ai_value=g_jk["point"], effect_size=ratio, effect_type="ratio", ci_lo=g_jk["lo"], ci_hi=g_jk["hi"], inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm))

        slope_fn = lambda Z: vendi_evenness_slope(vendi_scores(Z, (0, 2)))
        perm = label_permutation_test(Xh, Xg, slope_fn, B=n_perm, seed=seed, mode="within_diff")
        rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="evenness", metric="vendi_slope", param="q=0..2", human_value=slope_fn(Xh), ai_value=slope_fn(Xg), effect_size=slope_fn(Xh) - slope_fn(Xg), effect_type="diff", inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm))

        cov = coverage_density(Xh, Xg, k=3)
        split = split_half_reference(Xh, lambda A, B: coverage_density(A, B, k=3)["coverage"], n_splits=n_boot, seed=seed)
        rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="coverage", metric="coverage_geometric", param="k=3", human_value=float(np.nanmedian(split)), ai_value=cov["coverage"], effect_size=cov["coverage"], effect_type="coverage", ci_lo=float(np.nanpercentile(split, 2.5)), ci_hi=float(np.nanpercentile(split, 97.5)), inference="split_half_reference", stat=cov["coverage"], p_raw=float((np.sum(split <= cov["coverage"]) + 1) / (len(split) + 1)), n_human=n_h, n_ai=n_g, n_perm_or_boot=n_boot, notes=f"density={cov['density']:.4g}; human_value is split-half parity_ref"))

        for metric, stat_fn in [("participation_ratio", participation_ratio), ("effective_rank", effective_rank)]:
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="within_diff")
            h_jk = jackknife_ci(Xh, stat_fn)
            g_jk = jackknife_ci(Xg, stat_fn)
            rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="dimensionality", metric=metric, human_value=h_jk["point"], ai_value=g_jk["point"], effect_size=h_jk["point"] - g_jk["point"], effect_type="diff", ci_lo=g_jk["lo"], ci_hi=g_jk["hi"], inference="permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm))

        K_obs = ripley_K(Xg, radii)
        env = global_envelope_test(K_obs, null_K)
        area = float(np.trapz(K_obs - null_K_mean, radii))
        rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="evenness", metric="ripley_excess", param="r=pooled_q01_q50", human_value=np.nan, ai_value=area, effect_size=area, effect_type="envelope_area", ci_lo=np.nan, ci_hi=np.nan, inference="global_envelope", stat=env.get("stat"), p_raw=env["p"], n_human=n_h, n_ai=n_g, n_perm_or_boot=999, notes="positive means excess short-range neighbor mass vs pooled-cloud null"))

        for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
            perm = label_permutation_test(Xh, Xg, stat_fn, B=n_perm, seed=seed, mode="two_sample")
            rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="displacement", metric=metric, human_value=None, ai_value=None, effect_size=perm["delta_obs"], effect_type="two_sample_distance", ci_lo=float(np.nanpercentile(perm["null"], 2.5)), ci_hi=float(np.nanpercentile(perm["null"], 97.5)), inference="two_sample_permutation", stat=perm["delta_obs"], p_raw=perm["p_two_sided"], n_human=n_h, n_ai=n_g, n_perm_or_boot=n_perm, notes="M5 directional check; read jointly with coverage; larger means more displaced"))

    Xai_pool = X[idx["All AI"]]
    # Convert absolute row indices into positions within the All-AI pool for cached samples.
    ai_abs = idx["All AI"]
    abs_to_pool = {int(abs_i): pos for pos, abs_i in enumerate(ai_abs)}
    pool_samples = np.asarray([[abs_to_pool[int(v)] for v in sample] for sample in bootstrap_ai_idx_samples], dtype=int)
    Xh = X[human]
    comparison = "human_vs_pooled_ai"
    for metric, stat_fn in {**SPREAD_STATS, "vendi_q1": lambda Z: vendi_scores(Z, (1,))[1], "participation_ratio": participation_ratio, "effective_rank": effective_rank}.items():
        facet = "spread" if metric in SPREAD_STATS else "richness" if metric == "vendi_q1" else "dimensionality"
        metric_name = "vendi" if metric == "vendi_q1" else metric
        param = "q=1" if metric == "vendi_q1" else ""
        human_value = float(stat_fn(Xh))
        vals = subsample_pooled(Xai_pool, pool_samples, stat_fn)
        ai_mean = float(np.nanmean(vals))
        ratio = human_value / ai_mean if ai_mean else np.nan
        p = float((np.sum(vals >= human_value) + 1) / (len(vals) + 1))
        rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet=facet, metric=metric_name, param=param, human_value=human_value, ai_value=ai_mean, effect_size=ratio if facet in {"spread", "richness"} else human_value - ai_mean, effect_type="ratio" if facet in {"spread", "richness"} else "diff", ci_lo=float(np.nanpercentile(vals, 2.5)), ci_hi=float(np.nanpercentile(vals, 97.5)), inference="same_size_subsample", stat=human_value - ai_mean, p_raw=p, n_human=len(human), n_ai=len(human), n_perm_or_boot=len(vals), notes="pooled All-AI without-replacement subsample to n=23"))

    cov_vals = np.asarray([coverage_density(Xh, Xai_pool[s], k=3)["coverage"] for s in pool_samples], dtype=float)
    split = split_half_reference(Xh, lambda A, B: coverage_density(A, B, k=3)["coverage"], n_splits=n_boot, seed=seed)
    rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="coverage", metric="coverage_geometric", param="k=3", human_value=float(np.nanmedian(split)), ai_value=float(np.nanmean(cov_vals)), effect_size=float(np.nanmean(cov_vals)), effect_type="coverage", ci_lo=float(np.nanpercentile(cov_vals, 2.5)), ci_hi=float(np.nanpercentile(cov_vals, 97.5)), inference="same_size_subsample_vs_split_half", stat=float(np.nanmean(cov_vals)), p_raw=float((np.sum(cov_vals >= np.nanmedian(split)) + 1) / (len(cov_vals) + 1)), n_human=len(human), n_ai=len(human), n_perm_or_boot=len(cov_vals), notes="human_value is split-half parity_ref; ai_value is mean pooled-AI coverage"))

    for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
        vals = np.asarray([stat_fn(Xh, Xai_pool[s]) for s in pool_samples], dtype=float)
        rows.append(_metric_row(condition=analysis.condition, task="proposals", text_branch=text_branch, field="whole", comparison=comparison, facet="displacement", metric=metric, human_value=None, ai_value=None, effect_size=float(np.nanmean(vals)), effect_type="two_sample_distance", ci_lo=float(np.nanpercentile(vals, 2.5)), ci_hi=float(np.nanpercentile(vals, 97.5)), inference="same_size_subsample", stat=float(np.nanmean(vals)), p_raw=np.nan, n_human=len(human), n_ai=len(human), n_perm_or_boot=len(vals), notes="M5 pooled All-AI directional check; no AI/Human ratio"))

    tests_df = _add_fdr(pd.DataFrame(rows))

    gradient_specs = [
        ("richness", "vendi", "q=1", lambda Z: vendi_scores(Z, (1,))[1], "increasing"),
        ("dimensionality", "participation_ratio", "", participation_ratio, "increasing"),
        ("coverage", "coverage_geometric", "k=3", None, "increasing"),
        ("evenness", "ripley_excess", "r=pooled_q01_q50", lambda Z: -float(np.trapz(ripley_K(Z, radii) - null_K_mean, radii)), "increasing"),
    ]
    for facet, metric, param, stat_fn, direction in gradient_specs:
        if metric == "coverage_geometric":
            values = [coverage_density(Xh, X[idx[g]], k=3)["coverage"] for g in MODEL_GROUPS] + [np.nanmedian(split_half_reference(Xh, lambda A, B: coverage_density(A, B, k=3)["coverage"], n_splits=200, seed=seed))]
            groups_for_jt = [np.array([v]) for v in values]
        else:
            groups_for_jt = [jackknife_ci(X[idx[g]], stat_fn)["replicates"] for g in ["Claude", "Gemini", "GPT", "Human"]]
            values = [float(stat_fn(X[idx[g]])) for g in ["Claude", "Gemini", "GPT", "Human"]]
        jt = jonckheere_terpstra(groups_for_jt, alternative=direction)
        grad_rows.append({"condition": analysis.condition, "task": "proposals", "text_branch": text_branch, "field": "whole", "metric": metric, "param": param, "order": "claude<gemini<gpt<human", "JT": jt["JT"], "p_raw": jt["p"], "p_fdr": np.nan, "direction_ok": bool(all(x <= y for x, y in zip(values, values[1:]))), "notes": f"facet={facet}"})
    grad_df = pd.DataFrame(grad_rows)
    if not grad_df.empty:
        grad_df["p_fdr"] = benjamini_hochberg(grad_df["p_raw"])
    return tests_df, grad_df, pd.DataFrame(curves)


def build_review_facet_outputs(
    analysis: Any,
    combination_cache: Mapping[str, Mapping[str, Dict[str, Any]]],
    *,
    text_branch: str,
    field: str = "whole",
    n_boot: int = 1000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute paired review facet outputs for one condition and field."""
    review_master = analysis.review_master.copy()
    X = l2_normalize(np.asarray(analysis.review_embeddings["embeddings"], dtype=float))
    uid_to_idx = {str(uid): i for i, uid in enumerate(review_master["review_uid"].astype(str))}
    rows: List[Dict[str, Any]] = []
    paired_rows: List[Dict[str, Any]] = []
    curves: List[Dict[str, Any]] = []
    per_metric_values: Dict[Tuple[str, str, str], List[Tuple[float, float]]] = {}

    curve_groups: Dict[str, np.ndarray] = {}
    if "source_group" in review_master.columns:
        for group in ["Human", *MODEL_GROUPS]:
            idx = review_master.index[review_master["source_group"].eq(group)].to_numpy()
            if len(idx) >= 2:
                curve_groups[group] = idx
    if "review_source" in review_master.columns:
        ai_idx = review_master.index[review_master["review_source"].eq("ai")].to_numpy()
    elif "source_family" in review_master.columns:
        ai_idx = review_master.index[review_master["source_family"].ne("human")].to_numpy()
    else:
        ai_idx = np.array([], dtype=int)
    if len(ai_idx) >= 2:
        curve_groups["All AI"] = ai_idx
    if curve_groups:
        radii_for_curves = _radii_from_pooled(X)
        human_for_null = curve_groups.get("Human", next(iter(curve_groups.values())))
        null_K = _null_curves_from_pool(
            X,
            radii_for_curves,
            n=len(human_for_null),
            B=999,
            seed=seed,
            curve_fn=ripley_K,
        )
        for group, idx_for_group in curve_groups.items():
            _append_embedding_curve_rows(
                curves,
                condition=analysis.condition,
                task="reviews",
                text_branch=text_branch,
                field=field,
                group=group,
                X_group=X[idx_for_group],
                radii=radii_for_curves,
                null_K=null_K,
            )

    def panel_metrics(Xh: np.ndarray, Xa: np.ndarray) -> Dict[Tuple[str, str, str], Tuple[float, float]]:
        radii = _radii_from_pooled(np.vstack([Xh, Xa]))
        null_K_mean = np.zeros(len(radii), dtype=float)
        out = {
            ("richness", "vendi", "q=1"): (vendi_scores(Xh, (1,))[1], vendi_scores(Xa, (1,))[1]),
            ("dimensionality", "participation_ratio", ""): (participation_ratio(Xh), participation_ratio(Xa)),
            ("dimensionality", "effective_rank", ""): (effective_rank(Xh), effective_rank(Xa)),
            ("coverage", "coverage_geometric", "k=panel_adaptive"): (np.nan, coverage_density(Xh, Xa, k=min(3, max(1, len(Xh) - 1)))["coverage"]),
            ("evenness", "vendi_slope", "q=0..2"): (vendi_evenness_slope(vendi_scores(Xh, (0, 2))), vendi_evenness_slope(vendi_scores(Xa, (0, 2)))),
            ("evenness", "ripley_excess", "r=panel_q01_q50"): (0.0, float(np.trapz(ripley_K(Xa, radii) - null_K_mean, radii))),
        }
        for metric, stat_fn in SPREAD_STATS.items():
            out[("spread", metric, "")] = (stat_fn(Xh), stat_fn(Xa))
        return out

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
            ai_metric_accum: Dict[Tuple[str, str, str], List[float]] = {}
            h_metric_ref: Dict[Tuple[str, str, str], float] = {}
            for combo in info["ai_panel_combinations"]:
                ai_idx = [uid_to_idx[str(u)] for u in combo]
                Xa = X[ai_idx]
                metrics = panel_metrics(Xh, Xa)
                for key, (h_val, a_val) in metrics.items():
                    h_metric_ref[key] = h_val
                    ai_metric_accum.setdefault(key, []).append(a_val)
            for key, ai_vals in ai_metric_accum.items():
                h_val = h_metric_ref[key]
                if key[1] == "coverage_geometric":
                    h_val = 1.0
                ai_val = float(np.nanmean(ai_vals))
                values_by_metric.setdefault(key, []).append((str(target_uid), h_val, ai_val, len(human_uids)))

        for (facet, metric, param), vals in values_by_metric.items():
            if not vals:
                continue
            target_uids, h_vals, a_vals, ns = zip(*vals)
            h_arr = np.asarray(h_vals, dtype=float)
            a_arr = np.asarray(a_vals, dtype=float)
            test = paired_wilcoxon(h_arr, a_arr)
            diff = h_arr - a_arr
            rows.append(_metric_row(condition=analysis.condition, task="reviews", text_branch=text_branch, field=field, comparison=comparison_name, facet=facet, metric=metric, param=param, human_value=float(np.nanmean(h_arr)), ai_value=float(np.nanmean(a_arr)), effect_size=test["cliffs_delta"], effect_type="cliffs_delta", ci_lo=float(np.nanpercentile(diff, 2.5)), ci_hi=float(np.nanpercentile(diff, 97.5)), inference="paired_wilcoxon", stat=test["W"], p_raw=test["p"], n_human=float(np.nanmean(ns)), n_ai=float(np.nanmean(ns)), n_perm_or_boot=len(vals), notes="paired across target proposals; AI value is mean over exact-n enumerated panels"))
            per_metric_values[(comparison_name, metric, param)] = list(zip(h_arr, a_arr))
            for target_uid, h_val, a_val, n_h in vals:
                paired_rows.append({"condition": analysis.condition, "text_branch": text_branch, "field": field, "comparison": comparison_name, "facet": facet, "metric": metric, "param": param, "target_proposal_uid": target_uid, "target_cohort": "", "n_human_reviews": n_h, "human_value": h_val, "ai_value": a_val, "paired_diff": h_val - a_val})

    # Reviews M5: pooled whole-cloud exploratory companion, not paired.
    if field == "whole":
        human_idx = review_master.index[review_master["review_source"].eq("human")].to_numpy()
        ai_idx = review_master.index[review_master["review_source"].eq("ai")].to_numpy()
        for metric, stat_fn in [("mmd2", mmd2_rbf), ("ot_wasserstein", wasserstein_ot)]:
            stat = float(stat_fn(X[human_idx], X[ai_idx]))
            rows.append(_metric_row(condition=analysis.condition, task="reviews", text_branch=text_branch, field=field, comparison="human_vs_pooled_ai", facet="displacement", metric=metric, human_value=None, ai_value=None, effect_size=stat, effect_type="two_sample_distance", inference="unpaired_whole_cloud", stat=stat, p_raw=np.nan, n_human=len(human_idx), n_ai=len(ai_idx), notes="M5 review companion only; not per-proposal paired"))

    tests_df = _add_fdr(pd.DataFrame(rows))
    grad_rows = []
    for metric, param in [("vendi", "q=1"), ("participation_ratio", ""), ("coverage_geometric", "k=panel_adaptive"), ("ripley_excess", "r=panel_q01_q50")]:
        vals = []
        for comp in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt"]:
            key = (comp, metric, param)
            if key not in per_metric_values:
                vals.append(np.array([np.nan]))
            else:
                h, a = zip(*per_metric_values[key])
                vals.append(np.asarray(h, dtype=float) - np.asarray(a, dtype=float))
        if all(np.isfinite(v).any() for v in vals):
            jt = jonckheere_terpstra(vals, alternative="increasing")
            means = [float(np.nanmean(v)) for v in vals]
            grad_rows.append({"condition": analysis.condition, "task": "reviews", "text_branch": text_branch, "field": field, "metric": metric, "param": param, "order": "claude<gemini<gpt<human", "JT": jt["JT"], "p_raw": jt["p"], "p_fdr": np.nan, "direction_ok": bool(all(x <= y for x, y in zip(means, means[1:]))), "notes": "JT over paired Human-AI differences by model"})
    grad_df = pd.DataFrame(grad_rows)
    if not grad_df.empty:
        grad_df["p_fdr"] = benjamini_hochberg(grad_df["p_raw"])
    return tests_df, grad_df, pd.DataFrame(curves), pd.DataFrame(paired_rows)


def tag_coverage_exports(df: pd.DataFrame, *, family: str) -> pd.DataFrame:
    """Add manuscript facet labels to existing BERTopic/MeSH coverage exports."""
    out = df.copy()
    out["facet"] = "coverage"
    if family == "bertopic":
        out["metric"] = out.get("metric", "coverage_bertopic_region")
        if "metric" not in df.columns:
            out["metric"] = "coverage_bertopic_region"
    elif family == "mesh":
        out["metric"] = out.get("metric", "coverage_mesh_terms")
        if "metric" not in df.columns:
            out["metric"] = "coverage_mesh_terms"
    return out


def write_facet_outputs(
    tables_dir: Path,
    figures_dir: Path,
    tests_df: pd.DataFrame,
    gradient_df: pd.DataFrame,
    curves_df: pd.DataFrame,
    paired_df: pd.DataFrame | None = None,
) -> None:
    """Persist standard facet output files and simple diagnostic figures."""
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

    plot_df = tests_df[(tests_df["facet"] != "displacement") & tests_df["comparison"].isin(["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"])].copy()
    plot_df = plot_df[plot_df["metric"].isin(["vendi", "coverage_geometric", "participation_ratio", "ripley_excess"])]
    if not plot_df.empty:
        plot_df["ratio"] = plot_df["ai_value"] / plot_df["human_value"]
        fig, ax = plt.subplots(figsize=(11, max(4, 0.4 * len(plot_df))))
        sns.barplot(data=plot_df, x="ratio", y="metric", hue="comparison", ax=ax)
        ax.axvline(1.0, color="black", linewidth=1.0)
        ax.set_title("Facet diversity retained (AI / Human or parity reference)")
        ax.set_xlabel("Ratio")
        ax.set_ylabel("")
        fig.tight_layout()
        fig.savefig(figures_dir / "facet_diversity_retained_summary.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
