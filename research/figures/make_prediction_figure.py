"""Figure C, paired prediction differences with both uncertainty families.

Reads the frozen result file from snap-r8-paired-log and draws one row per fixed contrast on each
score scale. The recipe bootstrap interval is the one the appendix quotes, and the repartition
interval is drawn beneath it so a reader can see how much of the uncertainty comes from the fold
assignment rather than from the recipes. Nothing here recomputes an estimate.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/outputs/snap-r8-paired-log/r8_paired_log.json"
OUT = ROOT / "deliverables/figures/prediction.pdf"
LABELS = {"P1-P0": "P1 rank one\nminus P0 independence",
          "P3-P0": "P3 full covariance\nminus P0 independence",
          "P1g-P0": "P1G rank one plus gain\nminus P0 independence",
          "P2R-P0": "P2R rescaled performance\nminus P0 independence",
          "P1-P3": "P1 rank one\nminus P3 full covariance",
          "P1g-P1": "P1G rank one plus gain\nminus P1 rank one",
          "P2R-P1": "P2R rescaled performance\nminus P1 rank one",
          "P2R-P3": "P2R rescaled performance\nminus P3 full covariance"}

report = json.loads(SRC.read_text())
meaningful = report["meaningful_difference"]
order = list(report["bootstrap"]["margin"]["contrasts"])

# Type 42 keeps the glyphs as embedded TrueType rather than the Type 3 outlines matplotlib
# emits by default, which is what the other two figures in this paper already carry.
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "pdf.fonttype": 42, "ps.fonttype": 42,
                     "font.serif": ["Times New Roman", "Times", "DejaVu Serif"]})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.5), sharey=True)
for ax, scale, title in zip(axes, ("margin", "accuracy"), ("Margins", "Accuracy")):
    boot = report["bootstrap"][scale]["contrasts"]
    part = report["partitions"][scale]["contrasts"]
    ax.axvspan(-meaningful, meaningful, color="0.90", zorder=0)
    ax.axvline(0.0, color="0.35", linewidth=0.7, zorder=1)
    for i, key in enumerate(order):
        y = len(order) - 1 - i
        b, p = boot[key], part[key]
        ax.plot([p["p025"], p["p975"]], [y - 0.17, y - 0.17], color="0.55",
                linewidth=1.2, solid_capstyle="butt", zorder=2)
        ax.plot([p["median"]], [y - 0.17], marker="|", color="0.55", markersize=5, zorder=3)
        ax.plot([b["p025"], b["p975"]], [y + 0.10, y + 0.10], color="0.10",
                linewidth=1.4, solid_capstyle="butt", zorder=4)
        ax.plot([b["observed"]], [y + 0.10], marker="o", color="0.10", markersize=3.2, zorder=5)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([LABELS[k] for k in reversed(order)], fontsize=6.6)
    ax.set_xlabel("difference in mean squared log error")
    ax.set_title(title, fontsize=8.5)
    ax.tick_params(length=2.5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].set_ylim(-0.6, len(order) - 0.4)
# The key belongs in the LaTeX caption rather than inside the artwork, so the page sets it.
fig.tight_layout()
fig.savefig(OUT)
print("wrote", OUT, OUT.stat().st_size, "bytes")
