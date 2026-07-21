"""
Shared figure grammar for the diversity-facet notebooks (spec 1A).

Every plotting cell in 02/03/04 goes through these helpers so the palette, CI
labeling, resampling-distribution captions, and export rules stay consistent.
All functions read tidy tables/curves only - no metric is recomputed here.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

os.environ.setdefault("MPLCONFIGDIR", "/tmp/codex-matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse
from scipy.stats import gaussian_kde

PALETTE = {
    "Human": "#DC143C",
    "Claude": "#4A90E2",
    "Gemini": "#7B68EE",
    "GPT": "#3CB371",
    "All AI": "#4A90E2",
    "unknown": "#808080",
}
GROUP_ORDER = ["Human", "Claude", "Gemini", "GPT", "All AI"]
# Redundant marker-shape encoding (redesign spec 4.4): the crimson/green palette pair is a
# red-green confusion risk, so main figures and fingerprints never rely on color alone.
GROUP_MARKERS = {"Human": "o", "Claude": "s", "Gemini": "^", "GPT": "D", "All AI": "P"}
COMPARISON_TO_GROUP = {
    "human_vs_claude": "Claude",
    "human_vs_gemini": "Gemini",
    "human_vs_gpt": "GPT",
    "human_vs_pooled_ai": "All AI",
}
PARITY_COLOR = "#404040"
NULL_BAND_COLOR = "#808080"


def save_fig(fig, path_base: Path, *, dpi: int = 300, formats: Sequence[str] = ("png",)) -> None:
    """Save figure exports. PNG-only for now (user decision 2026-07-16); pass
    formats=("png", "pdf") to restore vector exports for manuscript submission."""
    path_base = Path(path_base)
    path_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(path_base.with_suffix(f".{ext}"), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def star_label(p) -> str:
    if p is None or not np.isfinite(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def row_stars(row) -> str:
    """Stars from p_raw for pre-registered primaries, p_fdr otherwise (spec 1A.9)."""
    if bool(row.get("is_primary", False)):
        return star_label(row.get("p_raw"))
    return star_label(row.get("p_fdr"))


def _caption(fig, text: str) -> None:
    import textwrap
    fig.text(0.01, -0.02, "\n".join(textwrap.wrap(text, 170)), ha="left", va="top",
             fontsize=7.5, color="#333333")


def add_direction_badge(fig, text: str = "↑ more diverse") -> None:
    """Direction Rule badge (redesign spec 1): redundant, consistent corner cue."""
    fig.text(0.995, 0.995, text, ha="right", va="top", fontsize=8, color="#444444",
             bbox=dict(boxstyle="round,pad=0.28", facecolor="#f5f5f5",
                       edgecolor="#bbbbbb", linewidth=0.6))


def _group_of(comparison: str) -> str:
    return COMPARISON_TO_GROUP.get(comparison, "unknown")


def _grid(ax):
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# Set-level metric panels (box / effect) - resampling distributions, spec 1A.0
# ---------------------------------------------------------------------------

def plot_setlevel_box(tests: pd.DataFrame, curves: pd.DataFrame, out_base: Path, *,
                      facet: str, metric: str, param: str, title: str, ylabel: str) -> None:
    """Box of jackknife replicates per group + pooled-subsample box + diamond/CI overlay."""
    jk = curves[curves["metric"].eq(f"{metric}_jackknife")]
    pooled = curves[curves["metric"].eq(f"{metric}_pooled_subsample") & curves["param"].eq(param)]
    trows = tests[tests["metric"].eq(metric) & tests["param"].eq(param) & tests["facet"].eq(facet)]
    groups = [g for g in ["Human", "Claude", "Gemini", "GPT"] if not jk[jk["group"].eq(g)].empty]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    data, labels, colors = [], [], []
    for g in groups:
        data.append(jk.loc[jk["group"].eq(g), "y"].dropna().to_numpy())
        labels.append(f"{g}\n(n=23)")
        colors.append(PALETTE[g])
    if not pooled.empty:
        data.append(pooled["y"].dropna().to_numpy())
        labels.append("All AI pooled\n(n=23 of 69)")
        colors.append(PALETTE["All AI"])
    if not data:
        ax.text(0.5, 0.5, "No replicate rows available", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor("black")
    for med in bp["medians"]:
        med.set_color("black")
    rng = np.random.default_rng(42)
    for x, (vals, color) in enumerate(zip(data, colors), start=1):
        show = vals if len(vals) <= 60 else rng.choice(vals, size=60, replace=False)
        ax.scatter(x + rng.uniform(-0.15, 0.15, size=len(show)), show, s=20, alpha=0.5,
                   color=color, edgecolors="none", zorder=3)
    # Diamond point estimates + 95% jackknife / subsample CI from the tests table.
    for x, g in enumerate(groups, start=1):
        if g == "Human":
            r = trows.iloc[0] if not trows.empty else None
            if r is not None and np.isfinite(r.get("human_value", np.nan)):
                lo, hi = r.get("human_ci_lo", np.nan), r.get("human_ci_hi", np.nan)
                err = None
                if np.isfinite(lo) and np.isfinite(hi):
                    # percentile jackknife CI can exclude the full-sample point; clamp arms at 0
                    err = [[max(0.0, r["human_value"] - lo)], [max(0.0, hi - r["human_value"])]]
                ax.errorbar([x], [r["human_value"]], yerr=err, fmt="D", color="black",
                            markersize=8, capsize=4, zorder=5, markerfacecolor="white")
        else:
            r = trows[trows["comparison"].eq(f"human_vs_{g.lower()}")]
            if not r.empty:
                r = r.iloc[0]
                err = None
                if np.isfinite(r["ci_lo"]) and np.isfinite(r["ci_hi"]):
                    err = [[max(0.0, r["ai_value"] - r["ci_lo"])], [max(0.0, r["ci_hi"] - r["ai_value"])]]
                ax.errorbar([x], [r["ai_value"]], yerr=err, fmt="D", color="black",
                            markersize=8, capsize=4, zorder=5, markerfacecolor="white")
                stars = row_stars(r)
                if stars:
                    ax.annotate(stars, (x, np.nanmax(data[x - 1])), textcoords="offset points",
                                xytext=(0, 8), ha="center", fontsize=11)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    _grid(ax)
    add_direction_badge(fig, "↑ more diverse")
    _caption(fig, "Points = leave-one-out jackknife replicates (23 per group); All AI = 1000 pooled subsamples "
                  "(n=23, without replacement) - resampling distributions, not observations. "
                  "Diamond = point estimate; bars = 95% jackknife CI (subsample CI for pooled). "
                  "Stars: p_raw for pre-registered primaries, p_fdr otherwise; vs Human by permutation/subsample test.")
    save_fig(fig, out_base)


def plot_effect_ratio(tests: pd.DataFrame, out_base: Path, *, facet: str, metric: str, param: str,
                      title: str, xlabel: str, higher_is_more_diverse: bool = True) -> None:
    """Effect panel: Human / AI ratio per comparison with stars (spec 1A.9)."""
    sub = tests[tests["metric"].eq(metric) & tests["param"].eq(param) & tests["facet"].eq(facet)]
    sub = sub[sub["comparison"].isin(COMPARISON_TO_GROUP)]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    if sub.empty:
        ax.text(0.5, 0.5, f"No rows for {facet}/{metric}", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    order = ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
    sub = sub.set_index("comparison").reindex([c for c in order if c in sub["comparison"].values]).reset_index()
    ys = np.arange(len(sub))
    ratios = sub["human_value"] / sub["ai_value"]
    colors = [PALETTE[_group_of(c)] for c in sub["comparison"]]
    ax.barh(ys, ratios, color=colors, alpha=0.85, edgecolor="black", linewidth=0.6)
    for y, (ratio, (_, row)) in enumerate(zip(ratios, sub.iterrows())):
        stars = row_stars(row)
        label = f"{ratio:.2f}{stars}"
        ax.annotate(label, (ratio, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9)
    ax.axvline(1.0, color=PARITY_COLOR, linestyle="--", linewidth=1)
    ax.annotate("parity", (1.0, len(sub) - 0.4), fontsize=8, color=PARITY_COLOR, ha="center")
    labels = []
    for c, (_, row) in zip(sub["comparison"], sub.iterrows()):
        g = _group_of(c)
        labels.append(f"{g} (n=23 of 69)" if g == "All AI" else f"{g} (n=23)")
    ax.set_yticks(ys, labels)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    direction = ">1 = humans more diverse" if higher_is_more_diverse else "see caption for direction"
    add_direction_badge(fig, "→ larger human advantage")
    _caption(fig, f"Effect = Human / AI ratio; {direction}. Stars: p_raw for pre-registered primaries, p_fdr otherwise.")
    save_fig(fig, out_base)


def plot_convergent_spread_box(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Dodged z-scored jackknife-replicate boxes for the five convergent M0 metrics."""
    metrics = ["centroid_loo", "mst_dispersion", "sparseness", "nn_isolation", "spherical_variance"]
    groups = ["Human", "Claude", "Gemini", "GPT"]
    fig, ax = plt.subplots(figsize=(11, 5))
    width = 0.19
    drew = False
    for mi, metric in enumerate(metrics):
        jk = curves[curves["metric"].eq(f"{metric}_jackknife")]
        if jk.empty:
            continue
        all_vals = jk["y"].to_numpy(dtype=float)
        mu, sd = np.nanmean(all_vals), np.nanstd(all_vals)
        sd = sd if sd > 0 else 1.0
        for gi, g in enumerate(groups):
            vals = (jk.loc[jk["group"].eq(g), "y"].to_numpy(dtype=float) - mu) / sd
            if vals.size == 0:
                continue
            pos = mi + (gi - 1.5) * width
            bp = ax.boxplot([vals], positions=[pos], widths=width * 0.9, patch_artist=True)
            bp["boxes"][0].set_facecolor(PALETTE[g])
            bp["boxes"][0].set_alpha(0.7)
            bp["medians"][0].set_color("black")
            drew = True
    if not drew:
        ax.text(0.5, 0.5, "No convergent-metric replicate rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    ax.set_xticks(range(len(metrics)), metrics, rotation=15)
    ax.set_ylabel("z-scored metric (within metric)")
    ax.set_title(title)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=PALETTE[g], alpha=0.7, edgecolor="black") for g in groups]
    ax.legend(handles, [f"{g} (n=23)" for g in groups], fontsize=8, ncols=4, loc="upper right")
    _grid(ax)
    add_direction_badge(fig, "↑ more diverse")
    _caption(fig, "Convergent M0 spread views (one facet, several views - not five findings). "
                  "Boxes = 23 leave-one-out jackknife replicates per group, z-scored within metric for a shared axis.")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# Distribution panels (ridge / hist) - observation-level data
# ---------------------------------------------------------------------------

def plot_pairwise_ridge(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Ridgeline of the full pairwise-distance distribution per group (required, spec 3.3)."""
    sub = curves[curves["metric"].eq("pairwise_distances")]
    groups = [g for g in ["Human", "Claude", "Gemini", "GPT"] if not sub[sub["group"].eq(g)].empty]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    if not groups:
        ax.text(0.5, 0.5, "No pairwise-distance rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    all_vals = sub["y"].to_numpy(dtype=float)
    xs = np.linspace(np.nanmin(all_vals), np.nanmax(all_vals), 300)
    offset = 0.0
    step = 1.15
    for g in groups[::-1]:
        vals = sub.loc[sub["group"].eq(g), "y"].dropna().to_numpy(dtype=float)
        if len(vals) < 3:
            continue
        try:
            dens = gaussian_kde(vals)(xs)
        except Exception:
            dens = np.histogram(vals, bins=30, range=(xs[0], xs[-1]), density=True)[0]
            dens = np.interp(xs, np.linspace(xs[0], xs[-1], len(dens)), dens)
        dens_scaled = dens / dens.max() if dens.max() > 0 else dens
        ax.fill_between(xs, offset, offset + dens_scaled, color=PALETTE[g], alpha=0.55, linewidth=0)
        ax.plot(xs, offset + dens_scaled, color=PALETTE[g], linewidth=1.2)
        med, mean = np.nanmedian(vals), np.nanmean(vals)
        ax.vlines(med, offset, offset + 1.0, color=PALETTE[g], linestyle="-", linewidth=1.6)
        ax.vlines(mean, offset, offset + 1.0, color=PALETTE[g], linestyle="--", linewidth=1.4)
        ax.text(xs[0], offset + 0.5, f"{g} ", ha="right", va="center", color=PALETTE[g], fontsize=10, fontweight="bold")
        offset += step
    ax.set_yticks([])
    ax.set_xlabel("Pairwise cosine distance")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    add_direction_badge(fig, "→ more separated ideas")
    _caption(fig, "All within-group pairwise distances (253 pairs per n=23 group) - observation-level panel. "
                  "Solid line = median, dashed = mean. Bimodality here is why the mean alone can mislead (spec 3.3).")
    save_fig(fig, out_base)


def plot_pooled_subsample_hist(curves: pd.DataFrame, tests: pd.DataFrame, out_base: Path, *,
                               metric: str, param: str, title: str, xlabel: str) -> None:
    """Headline pooled panel (spec 3.3.1): subsample distribution + Human vertical rule."""
    vals = curves.loc[curves["metric"].eq(f"{metric}_pooled_subsample") & curves["param"].eq(param), "y"].dropna().to_numpy()
    trow = tests[tests["metric"].eq(metric) & tests["param"].eq(param) & tests["comparison"].eq("human_vs_pooled_ai")]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if vals.size == 0 or trow.empty:
        ax.text(0.5, 0.5, "No pooled subsample distribution", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    trow = trow.iloc[0]
    ax.hist(vals, bins=40, color=PALETTE["All AI"], alpha=0.6, density=True, label="pooled AI subsamples")
    try:
        xs = np.linspace(min(vals.min(), trow["human_value"]), max(vals.max(), trow["human_value"]), 300)
        ax.plot(xs, gaussian_kde(vals)(xs), color=PALETTE["All AI"], linewidth=1.5)
    except Exception:
        pass
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    ax.axvspan(lo, hi, color=PALETTE["All AI"], alpha=0.15, label="AI 95% interval")
    ax.axvline(trow["human_value"], color=PALETTE["Human"], linewidth=2.2, label="Human (n=23)")
    stars = row_stars(trow)
    ax.set_title(title + (f"   (p={trow['p_raw']:.2g}{stars})" if np.isfinite(trow["p_raw"]) else ""))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("density")
    ax.legend(fontsize=8)
    _grid(ax)
    add_direction_badge(fig, "→ more diverse")
    _caption(fig, "Histogram = 1000 pooled-AI subsamples (n=23 drawn without replacement from 69) - a resampling "
                  "distribution, not observations. Empirical one-sided p vs the Human value; p_raw is starred (primary metric).")
    save_fig(fig, out_base)


def plot_nn_distance_hist(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Histogram of nearest-neighbor cosine DISTANCES per group (spec 7.4c, redesign spec 2:
    right-shifted = more isolated ideas = more diverse)."""
    sub = curves[curves["metric"].eq("nn_distance")]
    groups = [g for g in ["Human", "Claude", "Gemini", "GPT"] if not sub[sub["group"].eq(g)].empty]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not groups:
        ax.text(0.5, 0.5, "No NN-distance rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    dists_all = sub["y"].to_numpy(dtype=float)
    bins = np.linspace(np.nanmin(dists_all), np.nanmax(dists_all), 22)
    for g in groups:
        dists = sub.loc[sub["group"].eq(g), "y"].dropna().to_numpy(dtype=float)
        ax.hist(dists, bins=bins, alpha=0.45, color=PALETTE[g], label=f"{g} (n={len(dists)})")
    ax.set_xlabel("nearest-neighbor cosine distance (right = more isolated ideas)")
    ax.set_ylabel("count")
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    add_direction_badge(fig, "→ more diverse")
    _caption(fig, "Consistent bins across groups. Mass near ZERO = near-duplicate items (local repetition); "
                  "a right-shifted distribution = every idea keeps its distance from its closest sibling.")
    save_fig(fig, out_base)


# Backwards-compatible alias (renamed under the Direction Rule redesign).
plot_nn_similarity_hist = plot_nn_distance_hist


# ---------------------------------------------------------------------------
# Curve panels (profile / scree / envelope / cdf / rarefaction) - spec 1A.4
# ---------------------------------------------------------------------------

def _finite_profile_x(xs: np.ndarray) -> tuple[np.ndarray, list, list]:
    finite = xs[np.isfinite(xs)]
    inf_pos = finite.max() * 1.5 if finite.size else 1.0
    plot_x = np.where(np.isfinite(xs), xs, inf_pos)
    ticks = sorted(set(finite.tolist())) + [inf_pos]
    labels = [f"{t:g}" for t in sorted(set(finite.tolist()))] + ["∞"]
    return plot_x, ticks, labels


def plot_vendi_profile(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    sub = curves[curves["metric"].eq("vendi_profile")]
    fig, ax = plt.subplots(figsize=(8, 5))
    if sub.empty:
        ax.text(0.5, 0.5, "No vendi_profile curve rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    for g in ["Human", "Claude", "Gemini", "GPT", "All AI"]:
        grp = sub[sub["group"].eq(g)].sort_values("x")
        if grp.empty:
            continue
        xs = grp["x"].to_numpy(dtype=float)
        plot_x, ticks, labels = _finite_profile_x(xs)
        ax.plot(plot_x, grp["y"], marker="o", color=PALETTE[g], label=g, linewidth=1.8)
        if grp[["y_lo", "y_hi"]].notna().all(axis=None):
            ax.fill_between(plot_x, grp["y_lo"].astype(float), grp["y_hi"].astype(float),
                            color=PALETTE[g], alpha=0.18, linewidth=0)
        q1 = grp[np.isclose(grp["x"], 1.0)]
        if not q1.empty and g == "Human":
            ax.annotate(f"VS₁ = {float(q1['y'].iloc[0]):.2f}", (1.0, float(q1["y"].iloc[0])),
                        textcoords="offset points", xytext=(6, 6), fontsize=8, color=PALETTE[g])
    ax.set_xticks(ticks, labels)
    ax.set_xlabel("order q")
    ax.set_ylabel("Effective number of distinct items (VS_q)")
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    add_direction_badge(fig, "↑ more distinct items")
    _caption(fig, "Ribbon = 95% leave-one-out jackknife interval (equal-n subsample interval where noted in param). "
                  "∞ is a labeled tick, not a numeric position. Flat profile = evenly distinct items; steep drop = few dominant modes.")
    save_fig(fig, out_base)


def plot_scree(curves: pd.DataFrame, out_base: Path, *, metric: str, title: str, xlabel: str,
               ylabel: str, log_y: bool = False, mark_90: bool = False, max_x: float | None = None,
               residual: bool = False, badge: str | None = None) -> None:
    """Curve panel. With residual=True, cumulative-variance rows are shown as 1 − cumvar
    ("variance remaining beyond the first x components"), so UP = higher-dimensional
    (redesign spec 2); the 90% crossings become 10%-remaining crossings at the same x."""
    sub = curves[curves["metric"].eq(metric)]
    fig, ax = plt.subplots(figsize=(8, 5))
    if sub.empty:
        ax.text(0.5, 0.5, f"No {metric} curve rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    for g in ["Human", "Claude", "Gemini", "GPT", "All AI"]:
        grp = sub[sub["group"].eq(g)].sort_values("x")
        if grp.empty:
            continue
        y = 1.0 - grp["y"].astype(float) if residual else grp["y"].astype(float)
        ax.plot(grp["x"], y, marker=GROUP_MARKERS.get(g, "o"), markersize=3.5,
                color=PALETTE[g], label=g, linewidth=1.6)
        if grp[["y_lo", "y_hi"]].notna().all(axis=None):
            lo = 1.0 - grp["y_hi"].astype(float) if residual else grp["y_lo"].astype(float)
            hi = 1.0 - grp["y_lo"].astype(float) if residual else grp["y_hi"].astype(float)
            ax.fill_between(grp["x"].astype(float), lo, hi, color=PALETTE[g], alpha=0.15, linewidth=0)
        if mark_90:
            above = grp[grp["y"] >= 0.9]
            if not above.empty:
                x90 = float(above["x"].iloc[0])
                ax.axvline(x90, color=PALETTE[g], linestyle=":", linewidth=1.0, alpha=0.7)
    if mark_90:
        ax.axhline(0.1 if residual else 0.9, color=PARITY_COLOR, linewidth=0.8, linestyle="--", alpha=0.6)
    if log_y:
        ax.set_yscale("log")
    if max_x is not None:
        finite_x = pd.to_numeric(sub["x"], errors="coerce").dropna()
        if not finite_x.empty:
            ax.set_xlim(1, min(max_x, float(finite_x.max())))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    if badge:
        add_direction_badge(fig, badge)
    if mark_90 and residual:
        _caption(fig, "Shown as residual variation 1 − cumulative variance: the group whose curve stays HIGHER "
                      "still varies along more independent axes. Dotted vertical lines mark each group's "
                      "10%-remaining crossing (identical x to the canonical 90% crossing). Groups at equal n.")
    elif mark_90:
        _caption(fig, "Dotted vertical lines mark each group's 90% cumulative-variance crossing. Groups at equal n.")
    else:
        _caption(fig, "Shared axes across groups (equal n). A cliff after few eigenvalues = few dominant latent "
                      "modes = LESS diverse (canonical orientation; diagnostic panel).")
    save_fig(fig, out_base)


def plot_ripley_envelope(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Evenness-vs-chance form (redesign spec 2): plot null_mean − K(r), so UP = more even.

    The stored rows keep canonical K with the simultaneous envelope as [center−k95, center+k95];
    this panel re-orients at plot time: aligned curve = center − K, band = ±k95 around 0.
    The global-envelope p is unchanged (the max-deviation statistic is sign-invariant).
    """
    sub = curves[curves["metric"].eq("ripley_K")]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    if sub.empty:
        ax.text(0.5, 0.5, "No ripley_K curve rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    band = sub[sub["group"].eq("Human")].sort_values("x")
    if band.empty:
        band = sub[sub["group"].eq(sub["group"].iloc[0])].sort_values("x")
    have_band = band[["y_lo", "y_hi"]].notna().all(axis=None)
    if have_band:
        k95 = (band["y_hi"].astype(float) - band["y_lo"].astype(float)) / 2.0
        ax.fill_between(band["x"].astype(float), -k95, k95,
                        color=NULL_BAND_COLOR, alpha=0.20, linewidth=0,
                        label="simultaneous 95% global envelope\n(pooled-cloud null, M=999)")
    for g in ["Human", "Claude", "Gemini", "GPT", "All AI"]:
        grp = sub[sub["group"].eq(g)].sort_values("x")
        if grp.empty:
            continue
        if grp[["y_lo", "y_hi"]].notna().all(axis=None):
            center = (grp["y_lo"].astype(float) + grp["y_hi"].astype(float)) / 2.0
        elif have_band:
            center = (band["y_lo"].astype(float) + band["y_hi"].astype(float)) / 2.0
            center = np.interp(grp["x"].astype(float), band["x"].astype(float), center)
        else:
            center = np.zeros(len(grp))
        aligned = np.asarray(center) - grp["y"].to_numpy(dtype=float)
        ax.plot(grp["x"], aligned, marker=GROUP_MARKERS.get(g, "o"), markersize=4,
                color=PALETTE[g], label=g, linewidth=1.7)
    ax.axhline(0.0, color=PARITY_COLOR, linewidth=0.8, linestyle="--")
    ax.set_xlabel("cosine-distance radius r")
    ax.set_ylabel("evenness vs same-size null\n(positive = more evenly spread than chance)")
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    add_direction_badge(fig, "↑ more evenly spread")
    _caption(fig, "Re-oriented Ripley panel: shown as null-mean − K(r), so curves ABOVE the band are more evenly "
                  "spread than a random same-n draw of the pooled cloud; below = excess local clumping (near-"
                  "duplication). Grey band = SIMULTANEOUS 95% global envelope (max-deviation form, Myllymaki et al. "
                  "2017), M=999; the envelope test p is unchanged by the re-orientation. All groups at equal n.")
    save_fig(fig, out_base)


def plot_g_cdf(curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Survival-function form 1 − G(r) (redesign spec 2): UP = fewer near-twins = more diverse."""
    sub = curves[curves["metric"].eq("g_function")]
    fig, ax = plt.subplots(figsize=(8, 5))
    if sub.empty:
        ax.text(0.5, 0.5, "No g_function curve rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    for g in ["Human", "Claude", "Gemini", "GPT", "All AI"]:
        grp = sub[sub["group"].eq(g)].sort_values("x")
        if grp.empty:
            continue
        ax.plot(grp["x"], 1.0 - grp["y"].astype(float), marker=GROUP_MARKERS.get(g, "o"),
                markersize=4, color=PALETTE[g], label=g, linewidth=1.7)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("cosine-distance radius r")
    ax.set_ylabel("fraction of proposals with NO near-twin within r")
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    add_direction_badge(fig, "↑ fewer near-twins")
    _caption(fig, "Shown as the survival function 1 − G(r); the canonical nearest-neighbor CDF G is its complement. "
                  "A curve that stays HIGH keeps its items mutually distinct; dropping early = near-duplication. "
                  "All groups at equal n.")
    save_fig(fig, out_base)


def plot_rarefaction(curves: pd.DataFrame, out_base: Path, *, metric: str, title: str, ylabel: str,
                     param: str = "k_lit=10") -> None:
    sub = curves[curves["metric"].eq(metric) & curves["param"].eq(param)]
    fig, ax = plt.subplots(figsize=(8, 5))
    if sub.empty:
        ax.text(0.5, 0.5, f"No {metric} rows at {param}", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    climbing = []
    for g in ["Human", "Claude", "Gemini", "GPT"]:
        grp = sub[sub["group"].eq(g)].sort_values("x")
        if grp.empty:
            continue
        ax.plot(grp["x"], grp["y"], marker="o", markersize=3.5, color=PALETTE[g], label=f"{g} (n=23)", linewidth=1.7)
        if grp[["y_lo", "y_hi"]].notna().all(axis=None):
            ax.fill_between(grp["x"].astype(float), grp["y_lo"].astype(float), grp["y_hi"].astype(float),
                            color=PALETTE[g], alpha=0.15, linewidth=0)
        ys = grp["y"].to_numpy(dtype=float)
        if len(ys) >= 4 and ys[-4] > 0:
            climbing.append(f"{g}: +{(ys[-1] - ys[-4]) / max(ys[-1], 1e-9) * 100:.1f}% over last 3 draws")
    ax.set_xlabel("number of proposals sampled (m)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    _grid(ax)
    tail = "; ".join(climbing) if climbing else "n/a"
    add_direction_badge(fig, "↑ more regions reached")
    _caption(fig, f"Rarefaction: union size vs sample size, mean over 200 draws, ribbon = 2.5-97.5 pct ({param}). "
                  f"Still-climbing check at m=23: {tail}.")
    save_fig(fig, out_base)


def plot_occupancy_heatmap(matrix: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Region-occupancy heatmap (spec 9.4/1A.7): sequential cmap, exact zeros visibly distinct."""
    fig, ax = plt.subplots(figsize=(7, max(4, 0.45 * len(matrix) + 1.5)))
    if matrix.empty:
        ax.text(0.5, 0.5, "No occupancy rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    data = np.ma.masked_equal(matrix.to_numpy(dtype=float), 0.0)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#f2f2f2")
    im = ax.imshow(data, cmap=cmap, vmin=0, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index, fontsize=8)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix.iat[i, j]
            ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=7.5,
                    color="white" if v > np.nanmax(matrix.values) * 0.5 else ("#666666" if v == 0 else "black"))
    fig.colorbar(im, ax=ax, fraction=0.04, label="proposals touching region")
    ax.set_title(title)
    _caption(fig, "Cell = number of proposals (of 23) whose k=10 nearest literature abstracts include the region. "
                  "Light-grey cells are EXACT ZEROS - regions a group never touches (the finding). "
                  "Regions sorted by Human occupancy, descending.")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# Coverage scatter + displacement bar
# ---------------------------------------------------------------------------

def plot_coverage_scatter(tests: pd.DataFrame, curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    cov = tests[tests["metric"].eq("coverage_geometric") & tests["param"].eq("k=3")]
    den = tests[tests["metric"].eq("coverage_density") & tests["param"].eq("k=3")]
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    if cov.empty:
        ax.text(0.5, 0.5, "No coverage rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    for comp in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]:
        c = cov[cov["comparison"].eq(comp)]
        d = den[den["comparison"].eq(comp)]
        if c.empty or d.empty:
            continue
        g = _group_of(comp)
        label = f"{g} (n=23 of 69)" if g == "All AI" else f"{g} (n=23)"
        marker = "s" if g == "All AI" else "o"
        ax.scatter(c["ai_value"].iloc[0], d["ai_value"].iloc[0], s=110, color=PALETTE[g],
                   edgecolors="black", linewidths=0.8, marker=marker, label=label, zorder=4)
    cov_sub = curves.loc[curves["metric"].eq("coverage_geometric_pooled_subsample"), "y"].to_numpy(dtype=float)
    den_sub = curves.loc[curves["metric"].eq("coverage_density_pooled_subsample"), "y"].to_numpy(dtype=float)
    if cov_sub.size > 2 and den_sub.size == cov_sub.size:
        mean = np.array([cov_sub.mean(), den_sub.mean()])
        c2 = np.cov(np.vstack([cov_sub, den_sub]))
        vals, vecs = np.linalg.eigh(c2)
        angle = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
        w, h = 2 * np.sqrt(np.maximum(vals, 0) * 5.991)  # chi2_2 95%
        ax.add_patch(Ellipse(mean, w, h, angle=angle, facecolor=PALETTE["All AI"], alpha=0.12,
                             edgecolor=PALETTE["All AI"], linewidth=1.0, zorder=2))
    parity = cov["human_value"].dropna()
    if not parity.empty:
        ax.axvline(float(parity.iloc[0]), color=PARITY_COLOR, linestyle="--", linewidth=1.2)
        ax.annotate("human split-half coverage\n(same-distribution parity)", (float(parity.iloc[0]), ax.get_ylim()[0]),
                    textcoords="offset points", xytext=(6, 10), fontsize=7.5, color=PARITY_COLOR)
    ax.set_xlabel("coverage: fraction of human proposal space reached")
    ax.set_ylabel("density (~precision, on-manifold-ness)")
    ax.set_title(title)
    ax.legend(fontsize=8, loc="lower left")
    _grid(ax)
    add_direction_badge(fig, "→ more coverage")
    _caption(fig, "Expected pattern under the hypothesis: AI pulled LEFT (low coverage) while staying HIGH on density "
                  "(competent but narrow, spec 5.5). Parity line = median human split-half coverage, not 1.0. "
                  "Ellipse = 95% subsample ellipse for pooled AI (1000 subsamples of n=23).")
    save_fig(fig, out_base)


def plot_coverage_box(tests: pd.DataFrame, curves: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Coverage per model vs the human split-half reference band."""
    cov = tests[tests["metric"].eq("coverage_geometric") & tests["param"].eq("k=3")]
    split = curves.loc[curves["metric"].eq("coverage_geometric_split_half"), "y"].dropna().to_numpy(dtype=float)
    pooled = curves.loc[curves["metric"].eq("coverage_geometric_pooled_subsample"), "y"].dropna().to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8, 5))
    if cov.empty:
        ax.text(0.5, 0.5, "No coverage rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    if split.size:
        lo, hi = np.nanpercentile(split, [2.5, 97.5])
        ax.axhspan(lo, hi, color=NULL_BAND_COLOR, alpha=0.18, label="human split-half 95% band (1000 splits)")
        ax.axhline(np.nanmedian(split), color=PARITY_COLOR, linestyle="--", linewidth=1.2, label="split-half median (parity)")
    xs, labels = [], []
    x = 0
    for comp in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt"]:
        c = cov[cov["comparison"].eq(comp)]
        if c.empty:
            continue
        g = _group_of(comp)
        r = c.iloc[0]
        ax.scatter([x], [r["ai_value"]], s=140, color=PALETTE[g], edgecolors="black", zorder=4)
        stars = row_stars(r)
        if stars:
            ax.annotate(stars, (x, r["ai_value"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=11)
        xs.append(x)
        labels.append(f"{g}\n(n=23)")
        x += 1
    if pooled.size:
        bp = ax.boxplot([pooled], positions=[x], widths=0.45, patch_artist=True)
        bp["boxes"][0].set_facecolor(PALETTE["All AI"])
        bp["boxes"][0].set_alpha(0.7)
        bp["medians"][0].set_color("black")
        xs.append(x)
        labels.append("All AI pooled\n(n=23 of 69)")
    ax.set_xticks(xs, labels)
    ax.set_ylabel("coverage of the human proposal manifold (k=3)")
    ax.set_title(title)
    ax.legend(fontsize=8, loc="lower left")
    _grid(ax)
    add_direction_badge(fig, "↑ more coverage")
    _caption(fig, "A model narrows iff its coverage sits BELOW the split-half band (spec 5.2); empirical p = fraction "
                  "of split-half values <= observed. Pooled box = 1000 subsample values (resampling distribution). "
                  "Stars: p_raw (coverage is a pre-registered primary).")
    save_fig(fig, out_base)


def plot_coverage_effect(tests: pd.DataFrame, out_base: Path, *, title: str, param: str = "k=3") -> None:
    """Coverage effect panel: coverage itself is the effect size (spec 1A.9)."""
    sub = tests[tests["metric"].eq("coverage_geometric") & tests["param"].eq(param)]
    sub = sub[sub["comparison"].isin(COMPARISON_TO_GROUP)]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    if sub.empty:
        ax.text(0.5, 0.5, "No coverage rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    order = ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
    sub = sub.set_index("comparison").reindex([c for c in order if c in sub["comparison"].values]).reset_index()
    ys = np.arange(len(sub))
    colors = [PALETTE[_group_of(c)] for c in sub["comparison"]]
    ax.barh(ys, sub["ai_value"], color=colors, alpha=0.85, edgecolor="black", linewidth=0.6)
    for y, (_, row) in zip(ys, sub.iterrows()):
        stars = row_stars(row)
        ax.annotate(f"{row['ai_value']:.2f}{stars}  (misses {1 - row['ai_value']:.0%})",
                    (row["ai_value"], y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=8.5)
    parity = sub["human_value"].dropna()
    if not parity.empty:
        ax.axvline(float(parity.iloc[0]), color=PARITY_COLOR, linestyle="--", linewidth=1.2)
        ax.annotate("human split-half parity", (float(parity.iloc[0]), len(sub) - 0.4),
                    fontsize=8, color=PARITY_COLOR, ha="center")
    labels = [f"{_group_of(c)}" + (" (n=23 of 69)" if _group_of(c) == "All AI" else " (n=23)") for c in sub["comparison"]]
    ax.set_yticks(ys, labels)
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("Fraction of human proposal space reached")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    add_direction_badge(fig, "→ more of human space reached")
    _caption(fig, "Effect size = coverage itself; the annotation gives 1 - coverage = the human space AI never reaches "
                  "(spec 5.3). Parity line = median human split-half coverage, NOT 1.0. Stars: p_raw (pre-registered primary).")
    save_fig(fig, out_base)


def plot_mmd_bar(tests: pd.DataFrame, out_base: Path, *, title: str, metric: str = "mmd2") -> None:
    sub = tests[tests["facet"].eq("displacement") & tests["metric"].eq(metric)]
    fig, ax = plt.subplots(figsize=(8, 5))
    if sub.empty:
        ax.text(0.5, 0.5, "No displacement rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    order = ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
    xs, labels = [], []
    x = 0
    for comp in order:
        r = sub[sub["comparison"].eq(comp)]
        if r.empty:
            continue
        r = r.iloc[0]
        g = _group_of(comp)
        if comp != "human_vs_pooled_ai" and np.isfinite(r["ci_lo"]) and np.isfinite(r["ci_hi"]):
            ax.bar([x], [r["ci_hi"] - r["ci_lo"]], bottom=[r["ci_lo"]], width=0.7,
                   color=NULL_BAND_COLOR, alpha=0.20, zorder=1)
        ax.bar([x], [r["effect_size"]], width=0.5, color=PALETTE[g], edgecolor="black", linewidth=0.7, zorder=3)
        stars = row_stars(r)
        note = f"{stars}" if stars else ""
        if np.isfinite(r.get("p_raw", np.nan)):
            note += f"\np={r['p_raw']:.3g}"
        if note:
            ax.annotate(note, (x, r["effect_size"]), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)
        labels.append(f"{_group_of(comp)}" + ("\n(n=23 of 69)" if g == "All AI" else "\n(n=23)"))
        xs.append(x)
        x += 1
    floor = sub[sub["comparison"].eq("human_split_half")]
    if not floor.empty:
        f = floor.iloc[0]
        ax.axhline(f["effect_size"], color=PALETTE["Human"], linestyle="--", linewidth=1.4,
                   label="human split-half floor (same distribution)")
        if np.isfinite(f["ci_lo"]) and np.isfinite(f["ci_hi"]):
            ax.axhspan(f["ci_lo"], f["ci_hi"], color=PALETTE["Human"], alpha=0.10)
        ax.legend(fontsize=8)
    ax.set_xticks(xs, labels)
    # M5 quarantine (redesign spec 1.2): distinct styling, explicit non-diversity direction label.
    ax.set_facecolor("#faf6ef")
    ax.set_ylabel(("MMD²" if metric == "mmd2" else "OT distance")
                  + " — larger = more shifted (NOT less diverse)")
    ax.set_title(title, bbox=dict(boxstyle="square,pad=0.35", facecolor="#f0e9dc", edgecolor="#b8a97e", linewidth=0.8))
    _grid(ax)
    _caption(fig, "DIRECTIONAL CHECK, not a diversity facet: larger = more displaced from the human region — the "
                  "direction rule does not apply to this panel. Grey band = label-permutation null (B=10,000); "
                  "pooled bar = mean over 1000 subsamples. Read jointly with coverage (spec 8.3): low coverage + "
                  "low displacement = narrowed toward the shared human region.")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# UMAP illustration panels (never metric inputs - spec 1A.8)
# ---------------------------------------------------------------------------

def plot_group_umap(coords: np.ndarray, groups: Sequence[str], out_base: Path, *, title: str,
                    funded_mask: np.ndarray | None = None, top_mask: np.ndarray | None = None,
                    xlabel: str = "UMAP-1", ylabel: str = "UMAP-2",
                    background: tuple | None = None) -> None:
    """Group-colored UMAP with funded (magenta ring) / top-ranked (black outline) encodings."""
    fig, ax = plt.subplots(figsize=(7.5, 6))
    if background is not None:
        bg_coords, bg_colors = background
        ax.scatter(bg_coords[:, 0], bg_coords[:, 1], s=4, c=bg_colors, alpha=0.25, linewidths=0, zorder=1)
    groups = np.asarray(groups)
    for g in ["Human", "Claude", "Gemini", "GPT"]:
        mask = groups == g
        if not mask.any():
            continue
        ax.scatter(coords[mask, 0], coords[mask, 1], s=42, color=PALETTE[g], alpha=0.85,
                   edgecolors="white", linewidths=0.4, label=f"{g} (n={int(mask.sum())})", zorder=3)
    if top_mask is not None and np.asarray(top_mask).any():
        m = np.asarray(top_mask, dtype=bool)
        ax.scatter(coords[m, 0], coords[m, 1], s=90, facecolors="none", edgecolors="black",
                   linewidths=1.4, label="top-ranked", zorder=4)
    if funded_mask is not None and np.asarray(funded_mask).any():
        m = np.asarray(funded_mask, dtype=bool)
        ax.scatter(coords[m, 0], coords[m, 1], s=140, facecolors="none", edgecolors="magenta",
                   linewidths=1.6, label="funded (Human)", zorder=5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8, loc="best")
    _caption(fig, "Illustration only: 2-D UMAP projection; ALL metrics are computed in full embedding space (spec 1.1). "
                  "Magenta ring = funded Human proposal; black outline = top-ranked.")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# Review paired panels
# ---------------------------------------------------------------------------

def plot_paired_box(paired: pd.DataFrame, out_base: Path, *, title: str, facet: str, metric: str,
                    ylabel: str, funded_targets: set | None = None) -> None:
    sub = paired[paired["facet"].eq(facet) & paired["metric"].eq(metric)]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    if sub.empty:
        ax.text(0.5, 0.5, f"No paired rows for {facet}/{metric}", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    order = [c for c in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
             if c in set(sub["comparison"])]
    data, colors = [], []
    for c in order:
        data.append(sub.loc[sub["comparison"].eq(c), "paired_diff"].dropna().to_numpy())
        colors.append(PALETTE[_group_of(c)])
    bp = ax.boxplot(data, tick_labels=[_group_of(c) for c in order], patch_artist=True, widths=0.55)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for med in bp["medians"]:
        med.set_color("black")
    rng = np.random.default_rng(42)
    funded_targets = funded_targets or set()
    for x, c in enumerate(order, start=1):
        grp = sub[sub["comparison"].eq(c)].dropna(subset=["paired_diff"])
        jitter = rng.uniform(-0.15, 0.15, size=len(grp))
        ax.scatter(x + jitter, grp["paired_diff"], s=20, alpha=0.5, color=colors[x - 1], zorder=3)
        fund = grp["target_proposal_uid"].astype(str).isin(funded_targets).to_numpy()
        if fund.any():
            ax.scatter(x + jitter[fund], grp.loc[fund, "paired_diff"], s=70, facecolors="none",
                       edgecolors="magenta", linewidths=1.3, zorder=4)
    ax.axhline(0.0, color=PARITY_COLOR, linestyle="--", linewidth=1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    _grid(ax)
    n = sub.groupby("comparison")["target_proposal_uid"].nunique().max()
    add_direction_badge(fig, "↑ humans more diverse (paired)")
    _caption(fig, f"Points = paired per-proposal values (Human panel - AI exact-n panel mean), {n} target proposals. "
                  "Above 0 = human panels more diverse for that proposal. Magenta ring = funded target proposal. "
                  "AI panels are enumeration artifacts, not inferential n (spec 11.1).")
    save_fig(fig, out_base)


def plot_paired_slope(paired: pd.DataFrame, out_base: Path, *, title: str, facet: str, metric: str,
                      ylabel: str, funded_targets: set | None = None) -> None:
    """One line per proposal from Human panel value to AI panel mean (spec 11.5)."""
    sub = paired[paired["facet"].eq(facet) & paired["metric"].eq(metric)]
    comps = [c for c in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
             if c in set(sub["comparison"])]
    fig, axes = plt.subplots(1, max(len(comps), 1), figsize=(3.2 * max(len(comps), 1) + 1, 4.6), sharey=True)
    if sub.empty:
        axes = np.atleast_1d(axes)
        axes[0].text(0.5, 0.5, f"No paired rows for {facet}/{metric}", ha="center", va="center")
        axes[0].set_axis_off()
        save_fig(fig, out_base)
        return
    axes = np.atleast_1d(axes)
    funded_targets = funded_targets or set()
    for ax, comp in zip(axes, comps):
        grp = sub[sub["comparison"].eq(comp)].dropna(subset=["human_value", "ai_value"])
        g = _group_of(comp)
        for _, row in grp.iterrows():
            funded = str(row["target_proposal_uid"]) in funded_targets
            ax.plot([0, 1], [row["human_value"], row["ai_value"]],
                    color="magenta" if funded else "#999999",
                    alpha=0.8 if funded else 0.45, linewidth=1.3 if funded else 0.9, zorder=2)
        ax.scatter(np.zeros(len(grp)), grp["human_value"], s=26, color=PALETTE["Human"], zorder=3)
        ax.scatter(np.ones(len(grp)), grp["ai_value"], s=26, color=PALETTE[g], zorder=3)
        ax.plot([0, 1], [grp["human_value"].mean(), grp["ai_value"].mean()],
                color="black", linewidth=2.6, zorder=4)
        ax.set_xticks([0, 1], ["Human\npanel", f"{g}\npanel mean"])
        ax.set_xlim(-0.35, 1.35)
        ax.set_title(g, fontsize=10)
        _grid(ax)
    axes[0].set_ylabel(ylabel)
    fig.suptitle(title, fontsize=11)
    n = sub.groupby("comparison")["target_proposal_uid"].nunique().max()
    add_direction_badge(fig, "↑ more diverse")
    _caption(fig, f"One line per target proposal ({n} proposals), Human panel -> AI exact-n panel mean at matched "
                  "panel size. Black line = mean slope; magenta = funded target proposals. Downward = AI reviews less diverse.")
    save_fig(fig, out_base)


def plot_effect_delta(tests: pd.DataFrame, out_base: Path, *, title: str, facet: str, metric: str, param: str) -> None:
    """Cliff's delta forest panel for reviews (spec 1A.9): zero line + horizontal CIs."""
    sub = tests[tests["facet"].eq(facet) & tests["metric"].eq(metric) & tests["param"].eq(param)]
    sub = sub[sub["comparison"].isin(COMPARISON_TO_GROUP)]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    if sub.empty:
        ax.text(0.5, 0.5, f"No rows for {facet}/{metric}", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    order = ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
    sub = sub.set_index("comparison").reindex([c for c in order if c in sub["comparison"].values]).reset_index()
    ys = np.arange(len(sub))[::-1]
    for y, (_, row) in zip(ys, sub.iterrows()):
        g = _group_of(row["comparison"])
        # tests store Cliff's delta already in AI - Human orientation (spec 1A.9)
        delta = float(row["effect_size"])
        lo = float(row["ci_lo"]) if np.isfinite(row["ci_lo"]) else np.nan
        hi = float(row["ci_hi"]) if np.isfinite(row["ci_hi"]) else np.nan
        xerr = None
        if np.isfinite(lo) and np.isfinite(hi):
            xerr = [[delta - lo], [hi - delta]]
        ax.errorbar([delta], [y], xerr=xerr, fmt="o", color=PALETTE[g], markersize=9, capsize=4,
                    markeredgecolor="black", linewidth=1.6)
        stars = row_stars(row)
        ax.annotate(f"{stars} p={row['p_raw']:.2g}" if np.isfinite(row["p_raw"]) else "",
                    (delta, y), textcoords="offset points", xytext=(8, 8), fontsize=8)
    ax.axvline(0.0, color=PARITY_COLOR, linewidth=1.2)
    ax.set_yticks(ys, [_group_of(c) for c in sub["comparison"]])
    ax.set_xlabel("Cliff's δ (AI − Human, paired by proposal)")
    ax.set_xlim(-1.1, 1.1)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    add_direction_badge(fig, "→ AI more diverse")
    _caption(fig, "Negative = AI panels lower on this metric than the matched human panels. Bars = bootstrap 95% CI "
                  "of Cliff's delta (resampling the paired proposals). Stars: p_raw for primaries, p_fdr otherwise "
                  "(paired Wilcoxon over target proposals).")
    save_fig(fig, out_base)


def plot_review_coverage_paired_scatter(paired: pd.DataFrame, out_base: Path, *, title: str) -> None:
    """Per-proposal AI coverage vs human LOO self-coverage, with the diagonal as parity."""
    sub = paired[paired["metric"].eq("coverage_geometric")]
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    if sub.empty:
        ax.text(0.5, 0.5, "No coverage paired rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    rng = np.random.default_rng(42)
    for comp in ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]:
        grp = sub[sub["comparison"].eq(comp)].dropna(subset=["human_value", "ai_value"])
        if grp.empty:
            continue
        g = _group_of(comp)
        jx = rng.uniform(-0.015, 0.015, size=len(grp))
        jy = rng.uniform(-0.015, 0.015, size=len(grp))
        ax.scatter(grp["human_value"] + jx, grp["ai_value"] + jy, s=34, alpha=0.6, color=PALETTE[g], label=g)
    ax.plot([0, 1], [0, 1], color=PARITY_COLOR, linestyle="--", linewidth=1.2)
    ax.annotate("parity (AI = human self-coverage)", (0.55, 0.57), rotation=38, fontsize=7.5, color=PARITY_COLOR)
    ax.set_xlabel("human panel LOO self-coverage (m≥3 proposals)")
    ax.set_ylabel("AI panel coverage of the human review span")
    ax.set_xlim(-0.05, 1.08)
    ax.set_ylim(-0.05, 1.08)
    ax.set_title(title)
    ax.legend(fontsize=8, loc="upper left")
    add_direction_badge(fig, "↑ AI reaches more of human span")
    _caption(fig, "One point per (target proposal, model); small jitter for visibility. Below the diagonal = AI reviews "
                  "of the same proposal reach less of the human review span than human reviews reach of each other "
                  "(leave-one-out reference; proposals with m=2 human reviews excluded - spec 11.2 k-vs-m decision).")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# Fingerprint panels (redesign spec 3): one shared sign-aligned axis per cell
# ---------------------------------------------------------------------------

FACET_ROW_LABELS = {
    ("spread", "mean_pairwise"): "spread\n(mean pairwise)",
    ("richness", "vendi"): "richness\n(Vendi VS₁)",
    ("evenness", "ripley_excess"): "evenness\n(−Ripley excess)",
    ("dimensionality", "participation_ratio"): "dimensionality\n(participation ratio)",
    ("coverage", "coverage_geometric"): "coverage, geometric",
    ("coverage", "coverage_bertopic_region"): "coverage, domain\n(literature regions)",
}


def draw_fingerprint(ax, fp: pd.DataFrame, *, mode: str, show_row_labels: bool = True,
                     marker_size: float = 70) -> None:
    """Draw one fingerprint onto ax. fp rows: (facet, metric, group, z, z_ci_lo, z_ci_hi,
    sign_aligned, stars). mode='z' (proposals: SD units vs pooled-cloud null) or
    'delta' (reviews: sign-aligned Cliff's delta, AI − Human)."""
    triples = fp[["facet", "metric"]].drop_duplicates().values.tolist()
    n_rows = len(triples)
    order = ["Human", "Claude", "Gemini", "GPT", "All AI"]
    dodge = {g: (i - 2) * 0.13 for i, g in enumerate(order)}
    for ri, (facet, metric) in enumerate(triples):
        y0 = n_rows - 1 - ri
        if ri % 2 == 0:
            ax.axhspan(y0 - 0.5, y0 + 0.5, color="#000000", alpha=0.035, linewidth=0)
        rows = fp[fp["facet"].eq(facet) & fp["metric"].eq(metric)]
        for _, r in rows.iterrows():
            g = r["group"]
            if g not in order or not np.isfinite(r["z"]):
                continue
            y = y0 + dodge[g]
            xerr = None
            if np.isfinite(r.get("z_ci_lo", np.nan)) and np.isfinite(r.get("z_ci_hi", np.nan)):
                xerr = [[max(0.0, r["z"] - r["z_ci_lo"])], [max(0.0, r["z_ci_hi"] - r["z"])]]
            ax.errorbar([r["z"]], [y], xerr=xerr, fmt=GROUP_MARKERS.get(g, "o"),
                        color=PALETTE[g], markersize=np.sqrt(marker_size), capsize=2.5,
                        markeredgecolor="black", markeredgewidth=0.5, linewidth=1.1,
                        markerfacecolor="none" if g == "All AI" else PALETTE[g], zorder=4)
            stars = str(r.get("stars", "") or "")
            if stars and stars != "nan":
                ax.annotate(stars, (r["z"], y), textcoords="offset points", xytext=(4, 3), fontsize=7)
    ax.axvline(0.0, color=PARITY_COLOR, linewidth=1.2, linestyle="--", zorder=2)
    if mode == "delta":
        # In paired-delta mode the human panels ARE the reference: their position is the
        # zero line itself, so no Human dot is drawn — say so on the line.
        ax.annotate("Human panels\n= 0 (reference)", xy=(0, n_rows - 0.52), xytext=(4, -1),
                    textcoords="offset points", fontsize=6.5, color=PALETTE["Human"],
                    ha="left", va="top", fontstyle="italic")
    if show_row_labels:
        ax.set_yticks(range(n_rows - 1, -1, -1),
                      [FACET_ROW_LABELS.get((f, m), f"{f}\n({m})") for f, m in triples], fontsize=8)
    else:
        ax.set_yticks(range(n_rows - 1, -1, -1), [""] * n_rows)
    ax.set_ylim(-0.55, n_rows - 0.45)
    if mode == "z":
        ax.set_xlabel("standardized diversity (SD units vs pooled-cloud null)\n→ more diverse", fontsize=8)
    else:
        ax.set_xlabel("Cliff's δ (AI − Human), sign-aligned\n→ AI panels more diverse", fontsize=8)
        ax.set_xlim(-1.15, 1.15)
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)


def plot_fingerprint(fp: pd.DataFrame, out_base: Path, *, mode: str, title: str) -> None:
    """Standalone per-cell fingerprint figure (redesign spec 3)."""
    fig, ax = plt.subplots(figsize=(7.5, 0.85 * max(fp[["facet", "metric"]].drop_duplicates().shape[0], 3) + 1.6))
    if fp.empty:
        ax.text(0.5, 0.5, "No fingerprint rows", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    draw_fingerprint(ax, fp, mode=mode)
    ax.set_title(title, fontsize=10)
    handles = [plt.Line2D([], [], marker=GROUP_MARKERS[g], linestyle="", markersize=7,
                          color=PALETTE[g], markeredgecolor="black", markeredgewidth=0.5,
                          markerfacecolor="none" if g == "All AI" else PALETTE[g],
                          label=f"{g} (n=23 of 69)" if g == "All AI" else f"{g} (n=23)")
               for g in ["Human", "Claude", "Gemini", "GPT", "All AI"]
               if g in set(fp["group"])]
    ax.legend(handles=handles, fontsize=7.5, loc="best")
    add_direction_badge(fig, "→ more diverse")
    flipped = sorted(set(fp.loc[fp["sign_aligned"].astype(float) < 0, "facet"].astype(str))) if "sign_aligned" in fp.columns else []
    flip_note = (f" Sign-flipped so right = diverse: {', '.join(flipped)} (clumping metrics enter negated)."
                 if flipped else "")
    if mode == "z":
        _caption(fig, "Every facet on one axis: z = (group value − null mean) / null SD, null = M=999 same-n draws "
                      "of the pooled cloud (coverage: human split-half distribution). Right of 0 = more diverse than "
                      "a chance draw; whiskers = jackknife/subsample 95% CI in z units. Stars: p_raw for primaries, "
                      "p_fdr otherwise, from the standing tests." + flip_note)
    else:
        _caption(fig, "Paired effect per facet: Cliff's δ (AI − Human) across the 23 matched proposal panels; "
                      "left of 0 = AI review panels less diverse than the human panels of the same proposals. "
                      "Whiskers = bootstrap 95% CI. Stars: p_raw for primaries, p_fdr otherwise." + flip_note)
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# SI panel: interleaving statistics (descriptive - "unique territory" check)
# ---------------------------------------------------------------------------

def plot_interleaving_si(inter: pd.DataFrame, out_base: Path, *, task: str, title: str,
                         comparison: str = "human_vs_pooled_ai") -> None:
    """Two-panel SI figure from facet_interleaving.csv rows (long form: stat, value).

    Panel A: medians (dot) + q90 (cap) of the three NN distances per condition.
    Panel B: human-only fringe % and AI-only pocket % vs the ~10% by-construction
    reference. Descriptive geography - deliberately NOT on a diversity axis.
    """
    sub = inter[inter["task"].eq(task) & inter["comparison"].eq(comparison)]
    conditions = ["baseline", "one_at_a_time", "persona"]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 4.8))
    if sub.empty:
        axA.text(0.5, 0.5, "No interleaving rows", ha="center", va="center")
        axA.set_axis_off()
        axB.set_axis_off()
        save_fig(fig, out_base)
        return

    def val(cond, stat):
        r = sub[sub["condition"].eq(cond) & sub["stat"].eq(stat)]
        return float(r["value"].iloc[0]) if not r.empty else np.nan

    # Panel A - the three NN distances.
    series = [
        ("AI → nearest human", "ai_to_nearest_human", PALETTE["All AI"], "P", "full"),
        ("human → nearest other human\n(the yardstick)", "human_to_nearest_human", PALETTE["Human"], "o", "full"),
        ("human → nearest AI", "human_to_nearest_ai", PALETTE["Human"], "o", "none"),
    ]
    for si, (label, stem, color, marker, fill) in enumerate(series):
        xs = np.arange(len(conditions)) + (si - 1) * 0.18
        med = [val(c, f"{stem}_median") for c in conditions]
        q90 = [val(c, f"{stem}_q90") for c in conditions]
        yerr = [[0.0] * len(conditions), [max(0.0, q - m) for m, q in zip(med, q90)]]
        axA.errorbar(xs, med, yerr=yerr, fmt=marker, color=color, markersize=9, capsize=4,
                     linewidth=1.4, markeredgecolor="black", markeredgewidth=0.5,
                     markerfacecolor="none" if fill == "none" else color, label=label)
    axA.set_xticks(range(len(conditions)), conditions)
    axA.set_ylabel("cosine distance to nearest neighbor\n(same proposal's panel)" if task == "reviews"
                   else "cosine distance to nearest neighbor")
    axA.set_title("A · Cross-group nearest-neighbor distances", fontsize=10, loc="left")
    axA.legend(fontsize=7.5, loc="best")
    _grid(axA)

    # Panel B - exclusive-territory shares vs the by-construction reference.
    width = 0.32
    xs = np.arange(len(conditions))
    fringe = [100 * val(c, "share_human_fringe") for c in conditions]
    pocket = [100 * val(c, "share_ai_pocket") for c in conditions]
    axB.bar(xs - width / 2, fringe, width, color=PALETTE["Human"], alpha=0.85, edgecolor="black",
            linewidth=0.6, label="human-only fringe\n(humans no AI reaches)")
    axB.bar(xs + width / 2, pocket, width, color=PALETTE["All AI"], alpha=0.7, hatch="//",
            edgecolor="black", linewidth=0.6, label="AI-only pocket\n(AI no human reaches)")
    for x, v in zip(xs - width / 2, fringe):
        axB.annotate(f"{v:.0f}%", (x, v), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
    for x, v in zip(xs + width / 2, pocket):
        axB.annotate(f"{v:.0f}%", (x, v), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
    top = max([v for v in fringe + pocket if np.isfinite(v)] + [12.0])
    axB.set_ylim(0, top * 1.35)
    axB.axhline(10.0, color=PARITY_COLOR, linestyle="--", linewidth=1.2)
    axB.annotate("~10% = rate for humans against their own\ngroup, by construction of the yardstick",
                 (len(conditions) - 0.5, 10.0), textcoords="offset points", xytext=(0, 6),
                 fontsize=7, color=PARITY_COLOR, ha="right")
    axB.set_xticks(xs, conditions)
    axB.set_ylabel("% beyond the human-spacing yardstick")
    axB.set_title("B · Exclusive-territory shares", fontsize=10, loc="left")
    axB.legend(fontsize=7.5, loc="upper right")
    _grid(axB)

    fig.suptitle(title, fontsize=11.5)
    fig.tight_layout()
    unit = ("distances computed within each proposal's review panel, pooled across the 23 proposals"
            if task == "reviews" else "distances computed across the full proposal groups")
    _caption(fig, f"Descriptive interleaving statistics (no diversity direction; no inference): {unit}. "
                  "Yardstick = 90th percentile of human-to-nearest-other-human spacing; 'fringe'/'pocket' = share "
                  "of items whose nearest cross-group neighbor exceeds it. Values near or below the ~10% reference "
                  "mean the two groups are interleaved rather than occupying exclusive territory. Pooled AI shown "
                  f"({'all AI reviews of each proposal' if task == 'reviews' else 'subsampled to n=23'}); per-model "
                  "rows live in facet_interleaving.csv.")
    save_fig(fig, out_base)


# ---------------------------------------------------------------------------
# Convergence heatmap (spec 3.4) + cross-condition ratios
# ---------------------------------------------------------------------------

FACET_BLOCKS = [
    ("spread", ["mean_pairwise", "centroid_loo", "mst_dispersion", "sparseness", "nn_isolation", "spherical_variance"]),
    ("evenness", ["ripley_excess", "vendi_slope"]),
    ("richness", ["vendi_q1"]),
    ("dimensionality", ["participation_ratio", "effective_rank"]),
    ("coverage", ["coverage_geometric"]),
]


def build_group_value_matrix(tests_all: pd.DataFrame) -> pd.DataFrame:
    """Per-group metric values across all (condition, text_version) cells, for spec 3.4.

    Rows = (condition, text_version, group); columns = metric. Human values come from
    the human_value column (identical across comparisons); model values from ai_value.
    M5 is excluded (two-sample, no per-group value).
    """
    t = tests_all[tests_all["task"].eq("proposals") & tests_all["field"].eq("whole")].copy()
    wanted = {
        ("spread", "mean_pairwise", ""): "mean_pairwise",
        ("spread", "centroid_loo", ""): "centroid_loo",
        ("spread", "mst_dispersion", ""): "mst_dispersion",
        ("spread", "sparseness", ""): "sparseness",
        ("spread", "nn_isolation", ""): "nn_isolation",
        ("spread", "spherical_variance", ""): "spherical_variance",
        ("richness", "vendi", "q=1"): "vendi_q1",
        ("evenness", "vendi_slope", "q=0..2"): "vendi_slope",
        ("evenness", "ripley_excess", "r=pooled_q01_q50"): "ripley_excess",
        ("dimensionality", "participation_ratio", ""): "participation_ratio",
        ("dimensionality", "effective_rank", ""): "effective_rank",
        ("coverage", "coverage_geometric", "k=3"): "coverage_geometric",
    }
    records = {}
    t["param"] = t["param"].fillna("")
    for (facet, metric, param), colname in wanted.items():
        sub = t[t["facet"].eq(facet) & t["metric"].eq(metric) & t["param"].eq(param)]
        for _, row in sub.iterrows():
            comp = row["comparison"]
            if comp not in COMPARISON_TO_GROUP or comp == "human_vs_pooled_ai":
                continue
            g = COMPARISON_TO_GROUP[comp]
            key_g = (row["condition"], row["text_version"], g)
            key_h = (row["condition"], row["text_version"], "Human")
            records.setdefault(key_g, {})[colname] = row["ai_value"]
            records.setdefault(key_h, {})[colname] = row["human_value"]
    mat = pd.DataFrame.from_dict(records, orient="index")
    ordered_cols = [c for _, cols in FACET_BLOCKS for c in cols if c in mat.columns]
    return mat[ordered_cols]


def plot_facet_convergence(mat: pd.DataFrame, out_base: Path, *, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    if mat.empty or mat.shape[0] < 4:
        ax.text(0.5, 0.5, "Not enough group-level rows for correlations", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    corr = mat.corr(method="spearman")
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=90, fontsize=8)
    ax.set_yticks(range(len(corr.index)), corr.index, fontsize=8)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            v = corr.iat[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                        color="white" if abs(v) > 0.6 else "black")
    # Block separators between facets.
    boundaries = []
    pos = 0
    for _, cols in FACET_BLOCKS:
        present = [c for c in cols if c in corr.columns]
        if present:
            pos += len(present)
            boundaries.append(pos - 0.5)
    for b in boundaries[:-1]:
        ax.axhline(b, color="black", linewidth=1.4)
        ax.axvline(b, color="black", linewidth=1.4)
    fig.colorbar(im, ax=ax, fraction=0.046, label="Spearman ρ")
    ax.set_title(title, fontsize=10)
    _caption(fig, f"Spearman correlations over per-group metric VALUES across all conditions x text versions "
                  f"({mat.shape[0]} group-cells; Human + 3 models x 3 conditions x 2 versions). The M0/spread block "
                  "(top-left) should read uniformly high (one facet, several views); off-block cells markedly lower "
                  "(facets are non-redundant). Black lines separate facet blocks. M5 excluded (two-sample).")
    save_fig(fig, out_base)


def plot_cross_condition_ratio(tests_all: pd.DataFrame, out_base: Path, *, facet: str, metric: str,
                               param: str, task: str, text_version: str, title: str) -> None:
    """AI / Human diversity retained per condition per model (persona-persistence panel)."""
    t = tests_all[tests_all["task"].eq(task) & tests_all["text_version"].eq(text_version)
                  & tests_all["field"].eq("whole") & tests_all["facet"].eq(facet)
                  & tests_all["metric"].eq(metric) & tests_all["param"].fillna("").eq(param)].copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    if t.empty:
        ax.text(0.5, 0.5, f"No rows for {facet}/{metric}", ha="center", va="center")
        ax.set_axis_off()
        save_fig(fig, out_base)
        return
    conditions = ["baseline", "one_at_a_time", "persona"]
    comps = ["human_vs_claude", "human_vs_gemini", "human_vs_gpt", "human_vs_pooled_ai"]
    width = 0.2
    for ci, comp in enumerate(comps):
        vals, stars_list = [], []
        for cond in conditions:
            r = t[t["condition"].eq(cond) & t["comparison"].eq(comp)]
            if r.empty:
                vals.append(np.nan)
                stars_list.append("")
            else:
                r = r.iloc[0]
                vals.append(r["ai_value"] / r["human_value"] if r["human_value"] else np.nan)
                stars_list.append(row_stars(r))
        xs = np.arange(len(conditions)) + (ci - 1.5) * width
        g = _group_of(comp)
        ax.bar(xs, vals, width * 0.92, color=PALETTE[g], edgecolor="black", linewidth=0.5,
               alpha=0.9 if g != "All AI" else 0.55,
               label=f"{g}" + (" (pooled, n=23 of 69)" if g == "All AI" else " (n=23)"),
               hatch="//" if g == "All AI" else None)
        for xv, v, s in zip(xs, vals, stars_list):
            if np.isfinite(v) and s:
                ax.annotate(s, (xv, v), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=9)
    ax.axhline(1.0, color=PARITY_COLOR, linestyle="--", linewidth=1.2)
    ax.annotate("parity", (len(conditions) - 0.55, 1.0), textcoords="offset points", xytext=(0, 4),
                fontsize=8, color=PARITY_COLOR)
    ax.set_xticks(range(len(conditions)), conditions)
    ax.set_ylabel("AI / Human diversity retained")
    ax.set_title(title)
    ax.legend(fontsize=8, ncols=2)
    _grid(ax)
    parity_note = ("Coverage parity = the human split-half reference exported by 02/03 (human_value), so parity is "
                   "1.0 in ratio space." if metric == "coverage_geometric" else "Parity = 1.0 (AI matches Human).")
    add_direction_badge(fig, "↑ more diversity retained")
    _caption(fig, f"Persona-persistence panel: below parity = narrowing under that condition. {parity_note} "
                  "Stars: p_raw for pre-registered primaries, p_fdr otherwise.")
    save_fig(fig, out_base)
