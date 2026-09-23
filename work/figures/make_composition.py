# Figure 2 of main.tex (fig:composition). Every value is parsed from tab:original10 in
# deliverables/supplement_extended_body.tex, so the figure can't drift from the table it draws.
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = Path("deliverables/supplement_extended_body.tex").read_text()
body = src[src.index("\\label{tab:original10}"):]
body = body[:body.index("\\bottomrule")]
row = re.compile(r"^(.+?) & ([\d.]+) & \\ci\{([\d.]+)\}\{([\d.]+)\} & [\d.]+ & [\d.]+ & ([\d.]+) & \\ci\{([\d.]+)\}\{([\d.]+)\}", re.M)
rows = {m.group(1).strip(): [float(m.group(i)) for i in range(2, 8)] for m in row.finditer(body)}
assert len(rows) == 11 and "None" in rows, sorted(rows)
full = rows.pop("None")
order = sorted(rows, key=lambda k: rows[k][0])  # ascending margin estimate, the order of the original figure

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times"], "font.size": 9,
                     "pdf.fonttype": 42, "mathtext.fontset": "stix"})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.35))
for ax, off, title in zip(axes, (0, 3), ("Per-byte margins", "Accuracy")):
    x = range(len(order))
    est = [rows[k][off] for k in order]
    lo = [rows[k][off] - rows[k][off + 1] for k in order]
    hi = [rows[k][off + 2] - rows[k][off] for k in order]
    ax.errorbar(x, est, yerr=[lo, hi], fmt="o", color="black", ms=4, capsize=2.5, lw=1)
    ax.axhline(1.0, color="0.3", lw=0.8)
    ax.axhline(full[off], color="0.3", lw=0.8, ls="--")
    ax.set_xticks(list(x), order, rotation=40, ha="right", rotation_mode="anchor", fontsize=8)
    ax.set_title(title, fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel(r"$\widehat{\Lambda}$ after removal")
fig.tight_layout(pad=0.3)
fig.savefig("deliverables/figures/composition.pdf")
