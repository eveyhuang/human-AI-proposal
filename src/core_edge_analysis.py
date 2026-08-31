"""
Core-vs-edge analysis (Figure 3, Panel B): which human proposals does an
equal-sized AI pool fail to reproduce, and are they the distinctive / sparsely
populated ones?

Reads only prepared artifacts (pairwise cosine matrices, proposal masters,
exported AI subsample indices) — no facet metric is recomputed; peripherality
and miss-rate are geometry over exported distances. Exports, per text branch:
  * a tidy table `results/tables/synthesis/core_edge_{branch}.csv`
  * the Panel B composite `results/figures/synthesis/{branch}/fig3_core_edge.png`

Per human proposal it measures:
  * peripherality in HUMAN idea space (human-to-human distances only):
      centroid_dist, knn3_dist (isolation), local_density.
  * miss_rate per condition: fraction of equal-sized (n=23) AI pools whose
    nearest proposal to that human idea exceeds the human q90 yardstick
    (the per-item fringe probability; the mean-probability rule, FLAG 1).
Set-level asymmetry per condition (human-only vs AI-only fringe) and the
funding/ranking quality guard are computed for the caption.

Wired into `notebooks/04_synthesis.ipynb` via `build_panel_b(branch, out_dir)`.
Run standalone:  python src/core_edge_analysis.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy.stats import spearmanr, mannwhitneyu

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
import plotting as pl  # noqa: E402

CONDITIONS = ["baseline", "one_at_a_time", "persona"]
BRANCHES = ["rephrased", "original"]
HC, AC, INK = pl.PALETTE["Human"], pl.PALETTE["Claude"], "#333333"


def _load(condition: str, branch: str):
    prep = PROJECT_ROOT / "data" / "prepared" / condition / "proposals" / branch
    D = np.load(prep / "proposal_pairwise_cosine_full.npy")
    master = pd.read_csv(prep / "proposal_master.csv")
    grp = master["source_group"].to_numpy()
    return (D, np.where(grp == "Human")[0], np.where(grp != "Human")[0],
            master.iloc[np.where(grp == "Human")[0]].reset_index(drop=True), prep)


def compute(branch: str):
    # Human geometry is identical across conditions; take it from baseline.
    Db, hb, _, hmaster, _ = _load("baseline", branch)
    Dhh = Db[np.ix_(hb, hb)]
    off = Dhh.copy()
    np.fill_diagonal(off, np.inf)
    yq = float(np.quantile(off.min(1), 0.9))  # human q90 nearest-neighbor yardstick

    sqE = 2.0 * Dhh
    centroid = np.sqrt(np.clip(sqE.mean(1) - 0.5 * sqE.mean(), 0, None))
    knn3 = np.sort(off, 1)[:, :3].mean(1)
    local_density = (Dhh <= yq).sum(1) - 1

    out = pd.DataFrame({
        "proposal_uid": hmaster["proposal_uid"].to_numpy(),
        "title": hmaster.get("title", pd.Series([""] * len(hb))).to_numpy(),
        "cohort": hmaster.get("cohort", pd.Series([""] * len(hb))).to_numpy(),
        "is_funded_human": hmaster.get("is_funded_human", pd.Series([np.nan] * len(hb))).to_numpy(),
        "is_top5_ranked_human": hmaster.get("is_top5_ranked_human", pd.Series([np.nan] * len(hb))).to_numpy(),
        "ranking": hmaster.get("ranking", pd.Series([np.nan] * len(hb))).to_numpy(),
        "centroid_dist": centroid,
        "knn3_dist": knn3,
        "local_density": local_density,
    })

    human_only, ai_only = {}, {}
    for cond in CONDITIONS:
        D, h, a, _, prep = _load(cond, branch)
        sub = np.load(prep / "subsample_idx_ai_n23_seed42.npy")
        miss = np.zeros(len(h))
        ao = 0.0
        for d in range(sub.shape[0]):
            miss += (D[np.ix_(h, sub[d])].min(1) > yq)        # human idea has no AI within yardstick
            ao += float(np.mean(D[np.ix_(sub[d], h)].min(1) > yq))  # AI idea has no human within yardstick
        out[f"miss_rate_{cond}"] = miss / sub.shape[0]
        human_only[cond] = float((miss / sub.shape[0]).mean())
        ai_only[cond] = ao / sub.shape[0]
    out["miss_rate_mean"] = out[[f"miss_rate_{c}" for c in CONDITIONS]].mean(1)

    miss = out["miss_rate_mean"].to_numpy()
    summary = {"yardstick_q90": yq, "n_human": len(hb),
               "human_only": human_only, "ai_only": ai_only}
    for name in ["centroid_dist", "knn3_dist", "local_density"]:
        r, p = spearmanr(out[name], miss)
        summary[f"rho_{name}"], summary[f"p_{name}"] = float(r), float(p)
    order = np.argsort(-out["local_density"].to_numpy())
    ters = np.array_split(order, 3)
    summary["tertile_miss_core_mid_edge"] = [float(100 * miss[t].mean()) for t in ters]

    # quality-independence guard
    fund = out["is_funded_human"].astype(bool).to_numpy()

    def _mwu(col, mask):
        a, b = out[col].to_numpy()[mask], out[col].to_numpy()[~mask]
        return float("nan") if (len(a) == 0 or len(b) == 0) else float(mannwhitneyu(a, b, alternative="two-sided").pvalue)

    summary["n_funded"], summary["n_rejected"] = int(fund.sum()), int((~fund).sum())
    summary["miss_funded_mean"] = float(miss[fund].mean()) if fund.any() else float("nan")
    summary["miss_rejected_mean"] = float(miss[~fund].mean()) if (~fund).any() else float("nan")
    summary["miss_by_funded_mwu_p"] = _mwu("miss_rate_mean", fund)
    if out["is_top5_ranked_human"].notna().any():
        summary["miss_by_top5_mwu_p"] = _mwu("miss_rate_mean", out["is_top5_ranked_human"].astype(bool).to_numpy())
    r, p = spearmanr(miss, fund.astype(int))
    summary["rho_miss_vs_funded"], summary["p_miss_vs_funded"] = float(r), float(p)
    summary["tertile_funded_core_mid_edge"] = [float(fund[t].mean()) for t in ters]
    return out, summary


def build_panel_b(branch: str, out_dir: Path, *, write_table: bool = True):
    """Figure 3 Panel B composite: core-vs-edge scatter + tertile inset + asymmetry inset."""
    df, s = compute(branch)
    if write_table:
        tdir = PROJECT_ROOT / "results" / "tables" / "synthesis"
        tdir.mkdir(parents=True, exist_ok=True)
        df.to_csv(tdir / f"core_edge_{branch}.csv", index=False)

    x = df["centroid_dist"].to_numpy()
    y = 100 * df["miss_rate_mean"].to_numpy()
    fig = plt.figure(figsize=(9.2, 4.8))
    gs = gridspec.GridSpec(2, 2, width_ratios=[1.85, 1.0], height_ratios=[1, 1], wspace=0.42, hspace=0.55, figure=fig)

    ax = fig.add_subplot(gs[:, 0])
    ax.scatter(x, y, c=y, cmap="Blues", vmin=0, vmax=100, s=80, edgecolors="black", linewidths=0.4, zorder=3)
    z = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, np.polyval(z, xs), color="#404040", ls="--", lw=1.2)
    ax.set_xlabel("how distinctive a human idea is\n(distance from center of human idea space) →", fontsize=8.5)
    ax.set_ylabel("% of equal-sized AI pools that MISS it →", fontsize=8.5)
    pstr = "p < 0.001" if s["p_centroid_dist"] < 0.001 else f"p = {s['p_centroid_dist']:.3f}"
    ax.set_title(f"B   AI reproduces the core, thins the distinctive edges\n(Spearman ρ = {s['rho_centroid_dist']:+.2f}, {pstr}, n = {s['n_human']})", fontsize=10, loc="left")
    ax.grid(alpha=0.2)
    ax.annotate("core ideas:\nalways reproduced", xy=(x.min() + 0.008, 2), xytext=(0.14, 0.52),
                textcoords="axes fraction", fontsize=7.4, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.annotate("distinctive edge ideas:\noften missed", xy=(x.max() - 0.008, 96), xytext=(0.5, 0.82),
                textcoords="axes fraction", fontsize=7.4, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))

    axT = fig.add_subplot(gs[0, 1])
    mt = s["tertile_miss_core_mid_edge"]
    axT.bar([0, 1, 2], mt, color=["#c6dbef", "#6baed6", "#08519c"])
    for i, m in enumerate(mt):
        axT.text(i, m + 3, f"{m:.0f}%", ha="center", fontsize=7.5)
    axT.set_xticks([0, 1, 2], ["core", "mid", "edge"], fontsize=7.3)
    axT.set_ylim(0, 85)
    axT.set_ylabel("% missed", fontsize=7.8)
    axT.set_title("miss-rate by density tertile", fontsize=8)
    axT.grid(axis="y", alpha=0.2)

    axS = fig.add_subplot(gs[1, 1])
    ho = [100 * s["human_only"][c] for c in CONDITIONS]
    ao = [100 * s["ai_only"][c] for c in CONDITIONS]
    xx = np.arange(3)
    w = 0.36
    axS.bar(xx - w / 2, ho, w, color=HC, label="human w/ no AI")
    axS.bar(xx + w / 2, ao, w, color=AC, label="AI w/ no human")
    axS.axhline(10, color="#404040", ls="--", lw=1)
    axS.text(2.45, 10.6, "~10% chance", fontsize=6, color="#404040", ha="right")
    for i, v in enumerate(ho):
        axS.text(i - w / 2, v + 0.6, f"{v:.0f}", ha="center", fontsize=6.6)
    for i, v in enumerate(ao):
        axS.text(i + w / 2, v + 0.6, f"{v:.0f}", ha="center", fontsize=6.6)
    axS.set_xticks(xx, ["base", "1-at-a", "pers"], fontsize=7)
    axS.set_ylabel("% uncovered", fontsize=7.8)
    axS.set_title("humans leave more uncovered\nground than AI (AI near chance)", fontsize=7.6)
    axS.legend(fontsize=6, loc="upper center")
    axS.grid(axis="y", alpha=0.2)
    axS.set_ylim(0, max(max(ho), 12) * 1.25)

    pl.save_fig(fig, out_dir / "fig3_core_edge")
    return df, s


def main():
    for branch in BRANCHES:
        out_dir = PROJECT_ROOT / "results" / "figures" / "synthesis" / branch
        _, s = build_panel_b(branch, out_dir)
        print(f"[{branch}] n={s['n_human']} yardstick={s['yardstick_q90']:.3f}")
        for name in ["centroid_dist", "knn3_dist", "local_density"]:
            print(f"    rho[{name}] = {s[f'rho_{name}']:+.2f}  p = {s[f'p_{name}']:.4g}")
        c, m, e = s["tertile_miss_core_mid_edge"]
        print(f"    tertile miss core/mid/edge = {c:.0f}% / {m:.0f}% / {e:.0f}%")
        print(f"    human-only {[round(100*s['human_only'][x]) for x in CONDITIONS]}  "
              f"AI-only {[round(100*s['ai_only'][x]) for x in CONDITIONS]}")
        print(f"    quality guard: funded {s['n_funded']} vs rejected {s['n_rejected']}; "
              f"miss {s['miss_funded_mean']:.2f} vs {s['miss_rejected_mean']:.2f} (MWU p={s['miss_by_funded_mwu_p']:.2f})")


if __name__ == "__main__":
    main()
