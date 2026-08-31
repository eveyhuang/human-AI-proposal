"""
Figure 3, Panel A: same territory, occupied less evenly.

Effective number of literature regions occupied (categorical inverse Simpson,
of 12), at matched sample size. The human set is the full 23 proposals (one
fixed value, 4.94 effective regions); AI is subsampled to n=23, 1000x without
replacement from the 69 (the cached `subsample_idx_ai_n23_seed42.npy`), giving a
distribution drawn as a box + jitter. Reproduces the audit's SI-5 categorical
Simpson (validated: human 4.94; pooled AI 3.85 / 3.06 / 3.60 by condition).

Reads only prepared artifacts (BERTopic region labels + literature-kNN indices +
proposal masters + subsample indices); no facet metric is recomputed.

Wired into `notebooks/04_synthesis.ipynb` via `build_panel_a(branch, out_dir)`.
Run standalone:  python src/figure3_regions.py
Out:  results/figures/synthesis/{branch}/fig3_regions.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
import plotting as pl  # noqa: E402

CONDITIONS = ["baseline", "one_at_a_time", "persona"]
CLABEL = ["baseline", "one-at-a-time", "persona"]
BRANCHES = ["rephrased", "original"]
HC, AC = pl.PALETTE["Human"], pl.PALETTE["Claude"]


def _inverse_simpson(regions: np.ndarray) -> float:
    """Effective number of regions = 1 / sum(p_i^2); outlier bin (-1) dropped."""
    regions = regions[regions != -1]
    if len(regions) == 0:
        return np.nan
    _, counts = np.unique(regions, return_counts=True)
    p = counts / counts.sum()
    return float(1.0 / np.sum(p ** 2))


def effective_regions(branch: str):
    """Per condition: the fixed human value and the AI subsample distribution."""
    assign = pd.read_csv(PROJECT_ROOT / "data" / "prepared" / "literature" / "lit_bertopic_assignments.csv")
    topic = assign.set_index("article_idx")["bertopic_topic"]
    human, ai = {}, {}
    for cond in CONDITIONS:
        prep = PROJECT_ROOT / "data" / "prepared" / cond / "proposals" / branch
        nn1 = np.load(prep / "proposal_to_literature_knn.npz", allow_pickle=False)["neighbor_idx"][:, 0]
        reg = topic.loc[nn1].values                       # each proposal's nearest-region label
        grp = pd.read_csv(prep / "proposal_master.csv")["source_group"].to_numpy()
        sub = np.load(prep / "subsample_idx_ai_n23_seed42.npy")
        human[cond] = _inverse_simpson(reg[np.where(grp == "Human")[0]])
        ai[cond] = np.array([_inverse_simpson(reg[sub[d]]) for d in range(sub.shape[0])])
    return human, ai


def build_panel_a(branch: str, out_dir: Path):
    human, ai = effective_regions(branch)
    rng = np.random.RandomState(7)
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    HUM = human["baseline"]  # human set is fixed across conditions
    ratios = []
    for ci, cond in enumerate(CONDITIONS):
        vals = ai[cond]
        ax.boxplot(vals[np.isfinite(vals)], positions=[ci], widths=0.5, patch_artist=True, showfliers=False,
                   medianprops=dict(color="black", lw=1.8), whiskerprops=dict(color=AC), capprops=dict(color=AC),
                   boxprops=dict(facecolor=AC, alpha=0.30, edgecolor=AC))
        show = rng.choice(len(vals), min(120, len(vals)), replace=False)
        ax.scatter(ci + rng.uniform(-0.16, 0.16, len(show)), vals[show], s=10, color=AC, alpha=0.35, zorder=3, edgecolors="none")
        ax.scatter(ci, human[cond], marker="D", s=90, color=HC, edgecolors="black", linewidths=0.6, zorder=5)
        ratios.append(np.nanmean(vals) / human[cond])
    ax.axhline(HUM, color=HC, ls="--", lw=1.3, zorder=1)
    ax.text(2.42, HUM + 0.06, f"human set = {HUM:.2f}", color=HC, fontsize=8, ha="right", va="bottom")
    ax.set_xticks(range(3), CLABEL, fontsize=9)
    ax.set_ylabel("effective number of literature regions occupied\n(inverse Simpson, of 12; higher = spread across more regions)", fontsize=8.6)
    ax.set_title("A   AI concentrates in fewer literature regions than humans", fontsize=11, loc="left")
    ax.set_ylim(1.5, max(5.6, HUM + 0.4))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(handles=[Line2D([0], [0], marker="D", color="w", markerfacecolor=HC, markersize=9, label="human set (n=23, fixed)"),
                       Line2D([0], [0], marker="s", color="w", markerfacecolor=AC, markersize=9, label="AI subsampled to n=23 (1000×)")],
              fontsize=8, loc="lower left")
    fig.tight_layout()
    pl.save_fig(fig, out_dir / "fig3_regions")
    return human, [np.nanmean(ai[c]) for c in CONDITIONS], ratios


def main():
    for branch in BRANCHES:
        out_dir = PROJECT_ROOT / "results" / "figures" / "synthesis" / branch
        human, ai_means, ratios = build_panel_a(branch, out_dir)
        print(f"[{branch}] human eff-regions={human['baseline']:.2f}  "
              f"AI means={[round(v, 2) for v in ai_means]}  ratios AI/H={[round(r, 2) for r in ratios]}")


if __name__ == "__main__":
    main()
