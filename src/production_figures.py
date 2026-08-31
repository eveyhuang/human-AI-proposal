"""
Production figures for the paper, following docs/plans/paper_figure_Build_Specification.md
(with the 2026-08-30 revisions: Fig 2 A+B merged; Fig 3B color/labels clarified;
Fig 4A conditions merged; Fig 4 rank-aggregation panel removed).

Each panel's plotting lives in a `_draw_*(ax, ...)` helper. Standalone `figX*()`
wrappers save one panel per PNG; `build_fig1/2/3/4()` compose them into single figures.
All output goes to results/figures/production/.

Figure 1 and the Fig-3 computations reuse the validated builders. Fig 2's near-duplicate
curve is computed from the exported pairwise matrix (no parquet reader here).

Conventions: human = crimson, AI = blue; pooled AI is a filled marker; reference lines
recessive gray; only the evenness panel diverges; dimensionality and claim-uniqueness
never appear.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
import plotting as pl  # noqa: E402
import fig1_design_schematic  # noqa: E402
import figure3_regions  # noqa: E402
import core_edge_analysis  # noqa: E402

CONDS = ["baseline", "one_at_a_time", "persona"]
CLAB = ["baseline", "one-at-a-time", "persona"]
HC, AC = pl.PALETTE["Human"], pl.PALETTE["Claude"]
SPREAD_C, RICH_C = "#08519c", "#6baed6"                 # two blues for the merged spread/richness panel
COND_C = {"baseline": "#9ecae1", "one_at_a_time": "#4292c6", "persona": "#08519c"}  # AI condition shades
PARITY, INK = "#606060", "#222222"
OUT = PROJECT_ROOT / "results" / "figures" / "production"


def _tests(cond, task="proposals", branch="rephrased"):
    return pd.read_csv(PROJECT_ROOT / "results" / "tables" / cond / task / branch / "facet_diversity_tests.csv")


def _row(df, *, facet, metric, param, comparison="human_vs_pooled_ai"):
    r = df[(df.facet == facet) & (df.metric == metric) & (df.param.fillna("").eq(param)) & (df.comparison == comparison)]
    return r.iloc[0] if not r.empty else None


def _pairwise(cond, branch="rephrased"):
    prep = PROJECT_ROOT / "data" / "prepared" / cond / "proposals" / branch
    D = np.load(prep / "proposal_pairwise_cosine_full.npy")
    m = pd.read_csv(prep / "proposal_master.csv")
    return D, m["source_group"].to_numpy(), m


# ============================================================ FIG 2 draw helpers
def _draw_spread_richness(ax, branch):
    """Merged spread + richness ratio panel (AI ÷ human). Two blues, one per facet."""
    facets = [("spread", "mean_pairwise", "", SPREAD_C, 0.16, "spread"),
              ("richness", "vendi", "q=1", RICH_C, -0.16, "richness (Vendi)")]
    for yi, cond in enumerate(CONDS):
        y = len(CONDS) - 1 - yi
        df = _tests(cond, branch=branch)
        for facet, metric, param, col, dy, lab in facets:
            r = _row(df, facet=facet, metric=metric, param=param)
            ratio = r["ai_value"] / r["human_value"]
            lo, hi = r.get("ci_lo", np.nan), r.get("ci_hi", np.nan)
            if np.isfinite(lo) and np.isfinite(hi):
                ax.plot([lo / r["human_value"], hi / r["human_value"]], [y + dy, y + dy], color=col, lw=1.5, zorder=3)
            ax.scatter(ratio, y + dy, s=44, color=col, edgecolors="black", linewidths=0.5, zorder=5)
            ax.text(ratio, y + dy + (0.10 if dy > 0 else -0.16), f"{ratio:.2f}", ha="center", fontsize=6, color=col)
    ax.axvline(1.0, color=PARITY, ls="--", lw=1)
    ax.text(1.01, len(CONDS) - 0.5, "human\nparity", fontsize=6, color=PARITY, va="center")
    ax.set_yticks(range(len(CONDS))[::-1], CLAB, fontsize=7.5)
    ax.set_xlim(0.35, 1.15)
    ax.set_ylim(-0.6, len(CONDS) - 0.4)
    ax.set_xlabel("AI ÷ human diversity   (← AI less diverse)", fontsize=7.2)
    ax.set_title("A   AI holds ~two-thirds of human diversity", fontsize=8.3, loc="left")
    ax.grid(axis="x", alpha=0.2)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=SPREAD_C, markeredgecolor="black", markersize=7, label="spread (mean pairwise)"),
                       Line2D([0], [0], marker="o", color="w", markerfacecolor=RICH_C, markeredgecolor="black", markersize=7, label="richness (Vendi)")],
              fontsize=6.3, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, framealpha=0.9)


def _draw_evenness(ax, branch):
    for yi, cond in enumerate(CONDS):
        y = len(CONDS) - 1 - yi
        r = _row(_tests(cond, branch=branch), facet="evenness", metric="ripley_excess", param="r=pooled_q01_q50")
        ax.barh(y, float(r["human_value"]), height=0.55, color=HC, alpha=0.9)
        ax.barh(y, float(r["ai_value"]), height=0.55, color=AC, alpha=0.9)
    ax.axvline(0, color=PARITY, lw=1.1)
    ax.set_yticks(range(len(CONDS))[::-1], CLAB, fontsize=7.5)
    ax.set_xlim(-0.30, 0.22)
    ax.set_xlabel("← more even than chance    more clumped →", fontsize=6.5)
    ax.set_title("B   Evenness: AI clumps, humans do not (P = .001)", fontsize=8.2, loc="left")
    ax.legend(handles=[Patch(facecolor=HC, label="human"), Patch(facecolor=AC, label="pooled AI")], fontsize=6, loc="upper left")


def _draw_nnduplicate(ax, branch):
    ts = np.linspace(0.0, 0.45, 120)

    def curve(D, idx):
        sub = D[np.ix_(idx, idx)].copy()
        np.fill_diagonal(sub, np.inf)
        return np.array([np.mean(sub.min(1) <= t) for t in ts])

    D, g, m = _pairwise("baseline", branch)
    h, a = np.where(g == "Human")[0], np.where(g != "Human")[0]
    claude = np.where(m["model"].fillna("").str.contains("laude"))[0]
    ax.plot(ts, curve(D, h), color=HC, lw=2, label="human")
    ax.plot(ts, curve(D, a), color=AC, lw=2, label="pooled AI")
    if len(claude):
        ax.plot(ts, curve(D, claude), color="#08519c", lw=1.6, label="Claude, baseline")
    t35 = ts[np.argmin(np.abs(curve(D, h) - 0.35))]
    ax.axvline(t35, color=PARITY, ls="--", lw=1)
    ax.annotate("35% of human\nhave a twin", (t35, 0.35), xytext=(t35 + 0.03, 0.24), fontsize=6.2, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    if len(claude):
        ac = curve(D, claude)[np.argmin(np.abs(ts - t35))]
        ax.annotate(f">{ac*100:.0f}% of Claude's do", (t35, ac), xytext=(t35 + 0.02, min(0.92, ac + 0.05)),
                    fontsize=6.2, color="#08519c", arrowprops=dict(arrowstyle="->", color="#08519c", lw=0.7))
    ax.set_xlabel("distance threshold (cosine)", fontsize=7)
    ax.set_ylabel("share with a neighbor within", fontsize=7)
    ax.set_ylim(0, 1.02)
    ax.set_title("C   AI returns to the same wells", fontsize=8.3, loc="left")
    ax.legend(fontsize=6, loc="lower right")
    ax.grid(alpha=0.2)


def _draw_wording(ax, branch):
    wording, idea = [], []
    for cond in CONDS:
        df = _tests(cond, branch=branch)
        mdf = df[(df.facet == "lexical_control") & (df.metric == "distinct_2")]
        wording.append(float(mdf["ai_value"].mean() / mdf["human_value"].iloc[0]) if len(mdf) else np.nan)
        ri = _row(df, facet="richness", metric="vendi", param="q=1")
        idea.append(ri["ai_value"] / ri["human_value"])
    x = np.arange(len(CONDS))
    ax.plot(x, wording, marker="o", color="#8a4b9c", lw=2, label="wording (distinct-2gram)")
    ax.plot(x, idea, marker="s", color=AC, lw=2, label="ideas (richness)")
    ax.axhline(1.0, color=PARITY, ls="--", lw=1)
    ax.annotate("human parity", (0.02, 1.0), xytext=(0, 3), textcoords="offset points", fontsize=6, color=PARITY)
    for xi, w in zip(x, wording):
        ax.text(xi, w + 0.015, f"{w:.2f}", ha="center", fontsize=6, color="#8a4b9c")
    for xi, v in zip(x, idea):
        ax.text(xi, v - 0.035, f"{v:.2f}", ha="center", fontsize=6, color=AC)
    ax.set_xticks(x, CLAB, fontsize=7.5)
    ax.set_ylabel("AI ÷ human ratio", fontsize=7)
    ax.set_ylim(0.5, 1.06)
    ax.set_title("C   Persona changes wording, not ideas", fontsize=8.3, loc="left")
    ax.legend(fontsize=6.3, loc="lower center", ncols=2)
    ax.grid(axis="y", alpha=0.2)


# ============================================================ FIG 3 draw helpers
def _draw_fig3a(ax, branch):
    human, ai = figure3_regions.effective_regions(branch)
    rng = np.random.RandomState(7)
    HUM = human["baseline"]
    for ci, cond in enumerate(CONDS):
        v = ai[cond]
        ax.boxplot(v[np.isfinite(v)], positions=[ci], widths=0.5, patch_artist=True, showfliers=False,
                   medianprops=dict(color="black", lw=1.6), whiskerprops=dict(color=AC), capprops=dict(color=AC),
                   boxprops=dict(facecolor=AC, alpha=0.30, edgecolor=AC))
        show = rng.choice(len(v), min(100, len(v)), replace=False)
        ax.scatter(ci + rng.uniform(-0.16, 0.16, len(show)), v[show], s=8, color=AC, alpha=0.35, zorder=3, edgecolors="none")
        ax.scatter(ci, human[cond], marker="D", s=70, color=HC, edgecolors="black", linewidths=0.6, zorder=5)
    ax.axhline(HUM, color=HC, ls="--", lw=1.2, zorder=1)
    ax.text(2.42, HUM + 0.06, f"human = {HUM:.2f}", color=HC, fontsize=7, ha="right", va="bottom")
    ax.set_xticks(range(3), ["base", "1-at-a", "pers"], fontsize=7)
    ax.set_ylabel("effective literature regions occupied\n(inverse Simpson, of 12)", fontsize=7.5)
    ax.set_title("A   AI concentrates in fewer regions", fontsize=8.5, loc="left")
    ax.set_ylim(1.5, max(5.6, HUM + 0.4))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(handles=[Line2D([0], [0], marker="D", color="w", markerfacecolor=HC, markersize=8, label="human (n=23, fixed)"),
                       Line2D([0], [0], marker="s", color="w", markerfacecolor=AC, markersize=8, label="AI subsampled to 23 (1000×)")],
              fontsize=6, loc="lower left")


def _draw_fig3b(ax_sc, ax_ter, ax_asy, branch):
    df, s = core_edge_analysis.compute(branch)
    x = df["centroid_dist"].to_numpy()
    y = 100 * df["miss_rate_mean"].to_numpy()
    ax_sc.scatter(x, y, s=52, color=AC, alpha=0.5, edgecolors="#08306b", linewidths=0.7, zorder=3)
    z = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax_sc.plot(xs, np.polyval(z, xs), color="#404040", ls="--", lw=1.1)
    ax_sc.set_xlabel("how distinctive a human idea is →", fontsize=7.5)
    ax_sc.set_ylabel("% of equal-sized AI pools that miss it →", fontsize=7.5)
    pstr = "p < 0.001" if s["p_centroid_dist"] < 0.001 else f"p = {s['p_centroid_dist']:.3f}"
    ax_sc.set_title("B   AI reproduces the core, thins the edges", fontsize=8.3, loc="left")
    ax_sc.text(0.03, 0.94, f"ρ = {s['rho_centroid_dist']:+.2f}, {pstr}, n = 23", transform=ax_sc.transAxes, fontsize=6.8, color=INK)
    ax_sc.grid(alpha=0.2)
    ax_sc.annotate("core ideas:\nreproduced", xy=(x.min() + 0.008, 2), xytext=(0.13, 0.5), textcoords="axes fraction",
                   fontsize=6.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    ax_sc.annotate("distinctive edge:\noften missed", xy=(x.max() - 0.008, 96), xytext=(0.48, 0.8), textcoords="axes fraction",
                   fontsize=6.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    # tertile: single color, clearer labels
    mt = s["tertile_miss_core_mid_edge"]
    ax_ter.bar([0, 1, 2], mt, color=HC)
    for i, mm in enumerate(mt):
        ax_ter.text(i, mm + 3, f"{mm:.0f}%", ha="center", fontsize=6.5)
    ax_ter.set_xticks([0, 1, 2], ["core\n(dense)", "mid", "edge\n(sparse)"], fontsize=6.2)
    ax_ter.set_ylim(0, 85)
    ax_ter.set_ylabel("% of human ideas AI misses", fontsize=6.6)
    ax_ter.set_title("grouping human ideas by density", fontsize=7)
    ax_ter.grid(axis="y", alpha=0.2)
    # asymmetry: clearer title + legend
    ho = [100 * s["human_only"][c] for c in CONDS]
    ao = [100 * s["ai_only"][c] for c in CONDS]
    xx = np.arange(3)
    w = 0.36
    ax_asy.bar(xx - w / 2, ho, w, color=HC, label="human ideas, no AI match")
    ax_asy.bar(xx + w / 2, ao, w, color=AC, label="AI ideas, no human match")
    ax_asy.axhline(10, color=PARITY, ls="--", lw=1)
    ax_asy.text(2.4, 10.6, "≈10% (chance)", fontsize=5.6, color=PARITY, ha="right")
    ax_asy.set_xticks(xx, ["base", "1-at-a", "pers"], fontsize=6.2)
    ax_asy.set_ylabel("% with no counterpart", fontsize=6.6)
    ax_asy.set_title("ideas with no match in a 23-vs-23 pool", fontsize=6.6)
    ax_asy.legend(fontsize=5.4, loc="upper center")
    ax_asy.grid(axis="y", alpha=0.2)
    ax_asy.set_ylim(0, max(max(ho), 12) * 1.3)


# ============================================================ FIG 4 draw helpers
DELTA = {"baseline": "−0.39 (ns)", "one_at_a_time": "−0.91", "persona": "−0.74"}


def _within_data(branch):
    """Per-proposal within-panel mean review distance: human (fixed) and AI per condition."""
    ai, human = {}, None
    for cond in CONDS:
        p = pd.read_csv(PROJECT_ROOT / "results/tables" / cond / "reviews" / branch / "facet_review_paired_long.csv")
        p = p[(p.field == "whole") & (p.comparison == "human_vs_pooled_ai") & (p.facet == "spread") & (p.metric == "mean_pairwise")]
        p = p[np.isfinite(p.human_value) & np.isfinite(p.ai_value)]
        ai[cond] = dict(zip(p.target_proposal_uid, p.ai_value))
        if human is None:
            human = dict(zip(p.target_proposal_uid, p.human_value))
    return human, ai


def _within_pvals(branch):
    """Paired Wilcoxon p (and Cliff's δ) for human vs pooled-AI within-panel spread, per condition."""
    out = {}
    for c in CONDS:
        t = pd.read_csv(PROJECT_ROOT / "results/tables" / c / "reviews" / branch / "facet_diversity_tests.csv")
        r = t[(t.field == "whole") & (t.facet == "spread") & (t.metric == "mean_pairwise") & (t.comparison == "human_vs_pooled_ai")].iloc[0]
        out[c] = (float(r.p_raw), float(r.effect_size))
    return out


def _pstr(p):
    return "P < 0.001" if p < 0.001 else (f"P = {p:.2f} (ns)" if p >= 0.05 else f"P = {p:.3f}")


def _draw_within_box(ax, branch):
    """Box + jittered points of within-panel mean review distance, one box per group
    (human, AI baseline/one-at-a-time/persona). P = paired Wilcoxon vs the human panel."""
    human, ai = _within_data(branch)
    pv = _within_pvals(branch)
    uids = list(human)
    groups = [("human panel", np.array([human[u] for u in uids]), HC, None)]
    for c in CONDS:
        groups.append((f"AI · {c.replace('_', '-')}", np.array([ai[c][u] for u in uids if u in ai[c]]), COND_C[c], pv[c]))
    rng = np.random.RandomState(4)
    ytop = max(np.max(v) for _, v, _, _ in groups) * 1.02
    for i, (lab, v, col, stat) in enumerate(groups):
        ax.boxplot(v, positions=[i], widths=0.55, patch_artist=True, showfliers=False,
                   medianprops=dict(color="black", lw=1.7), whiskerprops=dict(color=col, lw=1.1),
                   capprops=dict(color=col, lw=1.1), boxprops=dict(facecolor=col, alpha=0.28, edgecolor=col, lw=1.2))
        ax.scatter(i + rng.uniform(-0.14, 0.14, len(v)), v, s=16, color=col, alpha=0.75,
                   edgecolors="white", linewidths=0.3, zorder=4)
        mu, sd = float(np.mean(v)), float(np.std(v, ddof=1))
        ax.errorbar(i + 0.34, mu, yerr=sd, fmt="o", ms=4, color="black", ecolor="black",
                    elinewidth=1.0, capsize=2.5, zorder=5)
        ax.text(i + 0.40, mu, f"  {mu:.3f}±{sd:.3f}", va="center", fontsize=5.6, color=INK)
        if stat is not None:
            p, d = stat
            ax.text(i, ytop, f"{_pstr(p)}\nδ = {d:+.2f}", ha="center", va="bottom", fontsize=6, color=INK)
    ax.set_xticks(range(len(groups)), ["human", "AI\nbaseline", "AI\n1-at-a-time", "AI\npersona"], fontsize=7)
    ax.set_ylabel("within-panel mean distance\n(↑ reviewers disagree more)", fontsize=7.5)
    ax.set_title("A   AI review panels agree more tightly than human panels", fontsize=8.3, loc="left")
    ax.grid(axis="y", alpha=0.2)
    ax.set_xlim(-0.5, len(groups) - 0.2)
    ax.set_ylim(top=ytop * 1.12)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=5, label="mean ± SD"),
                       Line2D([0], [0], marker="s", color="w", markerfacecolor="#bbbbbb", markersize=7, label="box = median, IQR; dots = 23 proposals"),
                       Line2D([0], [0], marker="", color="w", label="P: paired Wilcoxon vs human; δ: Cliff's")],
              fontsize=6, loc="center", bbox_to_anchor=(0.66, 0.74), framealpha=0.9)


def _draw_within_panel(ax, branch):
    """Merged: 23 human panels (fixed) with each condition's AI panel overlaid."""
    human, ai = _within_data(branch)
    uids = sorted(human, key=lambda u: -human[u])
    for r, u in enumerate(uids):
        vals = [human[u]] + [ai[c].get(u, np.nan) for c in CONDS]
        vals = [v for v in vals if np.isfinite(v)]
        ax.plot([min(vals), max(vals)], [r, r], color="#e6e6e6", lw=0.7, zorder=1)
        for c in CONDS:
            av = ai[c].get(u, np.nan)
            if np.isfinite(av):
                ax.scatter(av, r, s=11, color=COND_C[c], zorder=3)
        ax.scatter(human[u], r, s=24, color=HC, marker="D", edgecolors="white", linewidths=0.3, zorder=4)
    ax.set_yticks([])
    ax.set_ylabel("23 proposals (sorted by human panel spread)", fontsize=7)
    ax.set_xlabel("within-panel mean distance   (← more similar reviews within the panel)", fontsize=7)
    ax.set_title("A   For one proposal, AI reviewers say more similar things than human reviewers", fontsize=8.3, loc="left")
    ax.grid(axis="x", alpha=0.2)
    handles = [Line2D([0], [0], marker="D", color="w", markerfacecolor=HC, markersize=8, label="human panel (fixed)")]
    handles += [Line2D([0], [0], marker="o", color="w", markerfacecolor=COND_C[c], markersize=7,
                       label=f"AI · {CLAB[i]} (δ = {DELTA[c]})") for i, c in enumerate(CONDS)]
    ax.legend(handles=handles, fontsize=6.2, loc="lower right", ncols=2, framealpha=0.9)


def _draw_field(ax, branch):
    fields = [("whole", "#8a4b9c", "whole review"), ("strengths", "#3cb371", "strengths"), ("weakness", "#c0504d", "weakness")]
    w = 0.24
    for fi, (field, col, lab) in enumerate(fields):
        vals = []
        for cond in CONDS:
            t = pd.read_csv(PROJECT_ROOT / "results/tables" / cond / "reviews" / branch / "facet_diversity_tests.csv")
            r = t[(t.field == field) & (t.facet == "spread") & (t.metric == "mean_pairwise") & (t.comparison == "human_vs_pooled_ai")]
            vals.append(float(r.effect_size.iloc[0]) if len(r) else np.nan)
        y = np.arange(len(CONDS)) + (fi - 1) * w
        ax.barh(y, vals, height=w * 0.9, color=col, label=lab)
    ax.axvline(0, color=PARITY, ls="--", lw=1)
    ax.set_yticks(range(len(CONDS)), CLAB, fontsize=7.5)
    ax.set_xlabel("Cliff's δ (AI − human);  ← AI panel less diverse", fontsize=6.8)
    ax.set_xlim(-1.05, 0.3)
    ax.set_title("B   Compression concentrated in the criticism", fontsize=8.3, loc="left")
    ax.legend(fontsize=6, loc="lower left")
    ax.grid(axis="x", alpha=0.2)


def _draw_funding(ax):
    s = pd.read_csv(PROJECT_ROOT / "results/tables/cross_condition/reviews/decision_outcome_summary.csv")
    rows = []
    hr = s[s.group == "Human"].iloc[0]
    rows.append(("Human panel", hr.funding_auc, hr.funding_auc_ci_lo, hr.funding_auc_ci_hi, hr.funding_auc_p_perm, HC))
    for cond in CONDS:
        r = s[(s.group == "AI") & (s.condition == cond)].iloc[0]
        rows.append((f"AI · {cond.replace('_','-')}", r.funding_auc, r.funding_auc_ci_lo, r.funding_auc_ci_hi, r.funding_auc_p_perm, AC))
    for i, (lab, auc, lo, hi, p, col) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], color=col, lw=1.5)
        ax.scatter(auc, y, s=42, color=col, edgecolors="black", linewidths=0.5, zorder=4)
        ax.text(hi + 0.02, y, f"{auc:.2f} (P={p:.2f})", va="center", fontsize=6, color=INK)
    ax.axvline(0.5, color=PARITY, ls="--", lw=1)
    ax.annotate("chance", (0.5, len(rows) - 0.4), xytext=(2, 0), textcoords="offset points", fontsize=6, color=PARITY)
    ax.set_yticks(range(len(rows))[::-1], [r[0] for r in rows], fontsize=7)
    ax.set_xlim(0.0, 1.45)
    ax.set_xlabel("AUC: funded vs not", fontsize=7)
    ax.set_title("C   Panel scores carry no funding signal", fontsize=8.3, loc="left")
    ax.grid(axis="x", alpha=0.2)


# ============================================================ standalone panels
def fig2a(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(4.0, 2.8)); _draw_spread_richness(ax, branch); pl.save_fig(fig, OUT / "Fig2A_spread_richness")
def fig2b(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(3.8, 2.7)); _draw_evenness(ax, branch); pl.save_fig(fig, OUT / "Fig2B_evenness")
def fig2c(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(4.4, 2.8)); _draw_wording(ax, branch); pl.save_fig(fig, OUT / "Fig2C_wording")
def fig4a(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(5.8, 3.8)); _draw_within_box(ax, branch); fig.tight_layout(); pl.save_fig(fig, OUT / "Fig4A_within_panel")
def fig4b(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(4.4, 3.0)); _draw_field(ax, branch); pl.save_fig(fig, OUT / "Fig4B_field_split")
def fig4c(branch="rephrased"):
    fig, ax = plt.subplots(figsize=(4.6, 2.8)); _draw_funding(ax); pl.save_fig(fig, OUT / "Fig4C_funding_auc")


# ============================================================ composed figures
def build_fig1(branch="rephrased"):
    fig1_design_schematic.build(OUT / "Fig1")


def build_fig2(branch="rephrased"):
    fig = plt.figure(figsize=(7.4, 5.4))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.0, 1.05], hspace=0.6, wspace=0.42, figure=fig)
    _draw_spread_richness(fig.add_subplot(gs[0, :]), branch)
    _draw_evenness(fig.add_subplot(gs[1, 0]), branch)
    _draw_wording(fig.add_subplot(gs[1, 1]), branch)
    fig.suptitle("Figure 2 · AI proposal sets are less diverse and less evenly spread", y=0.99, fontsize=10)
    pl.save_fig(fig, OUT / "Fig2")


def build_fig3(branch="rephrased"):
    fig = plt.figure(figsize=(9.4, 4.4))
    gs = gridspec.GridSpec(2, 3, width_ratios=[1.15, 1.55, 0.95], height_ratios=[1, 1], wspace=0.5, hspace=0.5, figure=fig)
    _draw_fig3a(fig.add_subplot(gs[:, 0]), branch)
    _draw_fig3b(fig.add_subplot(gs[:, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 2]), branch)
    fig.suptitle("Figure 3 · Same territory, thinner at the distinctive edges", y=1.0, fontsize=10)
    pl.save_fig(fig, OUT / "Fig3")


def build_fig4(branch="rephrased"):
    fig = plt.figure(figsize=(7.6, 7.0))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.25, 1.0], hspace=0.5, wspace=0.42, figure=fig)
    _draw_within_box(fig.add_subplot(gs[0, :]), branch)
    _draw_field(fig.add_subplot(gs[1, 0]), branch)
    _draw_funding(fig.add_subplot(gs[1, 1]))
    fig.suptitle("Figure 4 · AI review panels converge; scores carry no funding signal", y=0.99, fontsize=10)
    pl.save_fig(fig, OUT / "Fig4")


def build_panels(branch="rephrased"):
    OUT.mkdir(parents=True, exist_ok=True)
    fig2a(branch); fig2b(branch); fig2c(branch)
    figure3_regions.build_panel_a(branch, OUT)
    core_edge_analysis.build_panel_b(branch, OUT, write_table=False)
    fig4a(branch); fig4b(branch); fig4c(branch)


def build_composed(branch="rephrased"):
    OUT.mkdir(parents=True, exist_ok=True)
    build_fig1(branch); build_fig2(branch); build_fig3(branch); build_fig4(branch)


def build_all(branch="rephrased"):
    build_panels(branch)
    build_composed(branch)
    print("wrote production figures to", OUT)
    for f in sorted(OUT.glob("*.png")):
        print("  ", f.name)


if __name__ == "__main__":
    build_all()
