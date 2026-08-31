"""
Fig. 1 for the PNAS Nexus draft: study-design schematic.

Standalone (not part of the 02/03/04 pipeline): it draws no data, only the
design. It reuses `plotting.PALETTE` and `plotting.save_fig` so colors and the
export path match the data figures.

Run:  python src/fig1_design_schematic.py
Out:  results/figures/synthesis/fig1_design_schematic.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
import plotting as pl  # noqa: E402

INK = "#222222"
MUTED = "#666666"
HUMAN = pl.PALETTE["Human"]
MODEL_COLORS = [pl.PALETTE["Claude"], pl.PALETTE["Gemini"], pl.PALETTE["GPT"]]
HUMAN_FILL = "#fdecef"
AI_FILL = "#eef3fb"
BAND_FILL = "#f4f4f4"


def _box(ax, x, y, w, h, *, fc, ec, lw=1.2, radius=0.02):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, mutation_aspect=0.6, zorder=2))


def _text(ax, x, y, s, *, size=10, weight="normal", color=INK, ha="center", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va,
            style=style, zorder=4)


def _arrow(ax, xy0, xy1, *, color=MUTED, lw=1.6):
    ax.add_patch(FancyArrowPatch(
        xy0, xy1, arrowstyle="-|>", mutation_scale=14, color=color, linewidth=lw, zorder=3))


def build(out_base: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # column headers: the two stages
    _text(ax, 33, 96, "STAGE 1 · GENERATION", size=12, weight="bold")
    _text(ax, 72, 96, "STAGE 2 · GATE-KEEPING", size=12, weight="bold")
    _text(ax, 33, 92.3, "who proposes the ideas", size=9, color=MUTED, style="italic")
    _text(ax, 72, 92.3, "who judges the ideas", size=9, color=MUTED, style="italic")

    # row labels
    _text(ax, 4.5, 74, "HUMAN", size=11, weight="bold", color=HUMAN, ha="center")
    _text(ax, 4.5, 44, "AI", size=11, weight="bold", color=pl.PALETTE["Claude"], ha="center")

    # ---- Human row ----
    _box(ax, 14, 64, 38, 20, fc=HUMAN_FILL, ec=HUMAN)
    _text(ax, 33, 78, "23 proposals", size=11, weight="bold")
    _text(ax, 33, 72.5, "faculty investigators, a real molecular\nand cellular bioscience competition", size=9, color=MUTED)

    _box(ax, 55, 64, 38, 20, fc=HUMAN_FILL, ec=HUMAN)
    _text(ax, 72, 78, "expert review panels", size=11, weight="bold")
    _text(ax, 72, 72.5, "2 to 5 senior reviewers per proposal,\nprogram criteria", size=9, color=MUTED)

    # ---- AI row ----
    _box(ax, 14, 30, 38, 26, fc=AI_FILL, ec=pl.PALETTE["Claude"])
    _text(ax, 33, 51.5, "Claude · Gemini · GPT", size=10.5, weight="bold")
    _text(ax, 33, 47, "each drafts 23 proposals from the\nsame call given to applicants", size=9, color=MUTED)

    _box(ax, 55, 30, 38, 26, fc=AI_FILL, ec=pl.PALETTE["Claude"])
    _text(ax, 72, 51.5, "Claude · Gemini · GPT", size=10.5, weight="bold")
    _text(ax, 72, 47, "each reviews the same 23 human\nproposals under the same criteria", size=9, color=MUTED)

    # condition chips inside both AI boxes
    conds = ["baseline", "one-at-a-time", "persona"]
    for cx0, label_y in [(15.5, 34), (56.5, 34)]:
        _text(ax, cx0 + 17, 39, "three elicitation conditions, rising diversity pressure", size=8, color=MUTED, style="italic")
        for i, cond in enumerate(conds):
            chip_x = cx0 + i * 11.7
            _box(ax, chip_x, 31, 10.6, 4.2, fc="white", ec=pl.PALETTE["Claude"], lw=1.0, radius=0.015)
            _text(ax, chip_x + 5.3, 33.1, cond, size=7.6, color=INK)
        _arrow(ax, (cx0 + 0.3, 30.2), (cx0 + 34.4, 30.2), color=pl.PALETTE["Claude"], lw=1.0)

    # top row: the human proposals are read by the human expert panel
    _arrow(ax, (52.2, 74), (55, 74), color=MUTED)
    _text(ax, 53.5, 76.2, "reviews", size=7.5, color=MUTED)

    # the shared inputs (same call, same 23 human proposals) are stated in the AI box
    # text, so no crossing arrows are needed. The comparison itself is the vertical
    # link between the Human row and the AI row, drawn once per stage.
    for cx in (33, 72):
        ax.add_patch(FancyArrowPatch(
            (cx, 63.4), (cx, 56.4), arrowstyle="<|-|>", mutation_scale=13,
            color=INK, linewidth=1.5, zorder=3))
        _text(ax, cx - 7.5, 60, "matched\ncomparison", size=7.6, color=INK, ha="right", style="italic")

    # method footer: how each comparison is computed (shared across both stages)
    _box(ax, 14, 7, 79, 15, fc=BAND_FILL, ec="#cccccc", lw=1.0)
    _text(ax, 53.5, 18.3, "HOW DIVERSITY IS MEASURED", size=10.5, weight="bold")
    _text(ax, 53.5, 13.6,
          "standardize the writing style  ·  embed with BioLinkBERT  ·  four facets in the full space",
          size=9, color=INK)
    _text(ax, 53.5, 10.3,
          "spread · richness · evenness · coverage,  AI vs Human at matched n = 23",
          size=9, color=MUTED)

    pl.save_fig(fig, out_base)


if __name__ == "__main__":
    out = PROJECT_ROOT / "results" / "figures" / "synthesis" / "fig1_design_schematic"
    build(out)
    print(f"wrote {out.with_suffix('.png')}")
