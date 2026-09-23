# Teaser figure for main.tex. Values are the null declaration rates printed at
# appendices_bcd.tex:218 (practitioner simulation, 4,000 replicates, true gap zero).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rates = {"Margin-like": (0.113, 0.051, 0.050), "Accuracy-like": (0.067, 0.052, 0.047)}
rules = ("Independence", "SNAP plug-in", "Oracle")
colors = ("#b2182b", "#2166ac", "#9e9e9e")
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times"], "font.size": 9})
fig, ax = plt.subplots(figsize=(5.6, 1.05))
w = 0.26
for g, (pop, vals) in enumerate(rates.items()):
    for r, v in enumerate(vals):
        x = g + (r - 1) * w
        ax.bar(x, v, w * 0.92, color=colors[r], label=rules[r] if g == 0 else None)
        ax.text(x, v + 0.002, f"{v:.3f}", ha="center", va="bottom", fontsize=7.5)
ax.axhline(0.05, ls="--", lw=0.8, color="black")
ax.text(1.7, 0.053, "nominal", ha="right", va="bottom", fontsize=7.5)
ax.set_xticks([0, 1], list(rates))
ax.set_xlim(-0.5, 1.72); ax.set_yticks([0, 0.05, 0.1])
ax.set_ylim(0, 0.15)
ax.set_ylabel("Declared rate", fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=7.5, loc="upper right", ncol=3)
fig.tight_layout(pad=0.3)
fig.savefig("deliverables/figures/teaser.pdf")
