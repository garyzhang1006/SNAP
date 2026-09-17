"""R30 redraw the paired-prediction figure so its labels are legible on the page.

Scan 30 measured the text of every figure as it actually renders. prediction.pdf was authored at
7.0 inches wide and included at width=\\linewidth, which is 5.5 inches in the ICLR style, so LaTeX
shrank it by 0.786 and put the eight contrast labels on the page at 5.2pt. That is below \\tiny.
The other two figures are not affected, since covariance.pdf is enlarged by 1.42 and calibration.pdf
sits at unit scale.

The fix authors the figure at 5.5 inches so the scale factor is exactly one. The aspect ratio is
unchanged, so the figure keeps the same footprint on the page and cannot move the page count. Nothing
here recomputes an estimate, it replots a frozen result file, so this is a drawing job rather than
compute in the usual sense. It runs here because the user has withheld local compute entirely.

The font is Nimbus Roman rather than Times New Roman. Nimbus is the URW Times clone that the
manuscript body is already set in, so this also removes a mismatch the earlier figure carried.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

OUT = Path("/kaggle/working")


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


report: dict = {"steps": []}

# Nimbus Roman ships in the URW base35 set. Without it matplotlib silently falls back to DejaVu
# Serif, which would change the figure's typeface rather than only its size, so the install is
# checked rather than assumed.
rc, out = run(["apt-get", "install", "-y", "-qq", "fonts-urw-base35"])
report["steps"].append({"step": "apt fonts-urw-base35", "returncode": rc, "tail": out[-400:]})

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# addfont is the public way in. Rebuilding the cache through the private loader works on some
# matplotlib versions and raises on others, and a crash here would cost a whole kernel run.
added = []
for pattern in ("*.otf", "*.ttf"):
    for path in Path("/usr/share/fonts").rglob(pattern):
        if "nimbus" in path.name.lower() or "NimbusRom" in path.name:
            try:
                fm.fontManager.addfont(str(path))
                added.append(path.name)
            except Exception as exc:  # a single unreadable face must not end the run
                report["steps"].append({"step": f"addfont {path.name}", "error": repr(exc)})
report["fonts_added"] = sorted(added)
available = sorted({f.name for f in fm.fontManager.ttflist})
report["nimbus_roman_available"] = "Nimbus Roman" in available
report["serif_candidates"] = [n for n in available if "Nimbus" in n or "Times" in n]

src = None
for cand in sorted(Path("/kaggle/input").rglob("r8_paired_log.json")):
    src = cand
    break
if src is None:
    report["error"] = "no r8_paired_log.json in input"
    report["input_tree"] = [str(p) for p in sorted(Path("/kaggle/input").rglob("*"))][:80]
    (OUT / "r30_figure.json").write_text(json.dumps(report, indent=2))
    sys.exit(1)
report["source"] = str(src)

LABELS = {"P1-P0": "P1 rank one\nminus P0 independence",
          "P3-P0": "P3 full covariance\nminus P0 independence",
          "P1g-P0": "P1G rank one plus gain\nminus P0 independence",
          "P2R-P0": "P2R rescaled performance\nminus P0 independence",
          "P1-P3": "P1 rank one\nminus P3 full covariance",
          "P1g-P1": "P1G rank one plus gain\nminus P1 rank one",
          "P2R-P1": "P2R rescaled performance\nminus P1 rank one",
          "P2R-P3": "P2R rescaled performance\nminus P3 full covariance"}

data = json.loads(src.read_text())
meaningful = data["meaningful_difference"]
order = list(data["bootstrap"]["margin"]["contrasts"])
report["meaningful_difference"] = meaningful
report["order"] = order

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "pdf.fonttype": 42, "ps.fonttype": 42,
                     "font.serif": ["Nimbus Roman", "Times New Roman", "Times", "DejaVu Serif"]})
fig, axes = plt.subplots(1, 2, figsize=(5.5, 2.75), sharey=True)
for ax, scale, title in zip(axes, ("margin", "accuracy"), ("Margins", "Accuracy")):
    boot = data["bootstrap"][scale]["contrasts"]
    part = data["partitions"][scale]["contrasts"]
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
fig.tight_layout()
target = OUT / "prediction.pdf"
fig.savefig(target)
report["bytes"] = target.stat().st_size

# Read the result back rather than trusting the call. The page scale is the whole point of the
# change, so the mediabox and every type-setting size get measured from the bytes that were written.
from pypdf import PdfReader

page = PdfReader(str(target)).pages[0]
width_bp = float(page.mediabox.width)
height_bp = float(page.mediabox.height)
stream = page.get_contents().get_data()
sizes = sorted({float(m) for m in re.findall(rb"/F\d+\s+([\d.]+)\s+Tf", stream)})
scale = 396.0 / width_bp  # 5.5 true inches of ICLR text block, in PostScript points
res = page.get("/Resources").get_object()
fonts = res.get("/Font")
fonts = fonts.get_object() if fonts is not None else {}
report["mediabox_bp"] = [round(width_bp, 1), round(height_bp, 1)]
report["latex_scale_at_linewidth"] = round(scale, 4)
report["natural_tf_sizes"] = sizes
report["effective_page_sizes"] = [round(s * scale, 2) for s in sizes]
report["smallest_effective_pt"] = round(min(sizes) * scale, 2) if sizes else None
report["embedded_faces"] = sorted({str(v.get_object().get("/BaseFont", "?")) for v in fonts.values()})
report["displayed_height_inches"] = round(height_bp * scale / 72.0, 3)

(OUT / "r30_figure.json").write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != "steps"}, indent=2))
