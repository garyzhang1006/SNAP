"""Which residual weighting produces the figures the original analysis record reported.

Design fixed before running (2026-09-16, written 00:30 EDT). snap-r6-influence shows that the largest
recipe's share of squared margin influence is 0.5199 under the plain cluster linearisation, under the
delta-method transfer to Lambda, and under the unscaled residual, while the analysis record reported
0.543 with participation ratios 2.88 and 8.68 against the recomputed 3.081 and 9.016. The record's
removal figure does reproduce, so the discrepancy sits in the influence definition rather than in the
data or the cluster grouping. Every small-sample correction in this literature multiplies each cluster
residual by a function of that cluster's leverage h_g, which is the recipe's share of the denominator
sum here, and any such correction raises the share held by the heaviest recipe. This run sweeps the
standard corrections, which are the plain residual, the CR1 factor sqrt(G/(G-1)), the CR2 factor
1/sqrt(1-h_g), the CR3 factor 1/(1-h_g), and the jackknife recomputation that drops each recipe and
rescales, and reports the resulting share and both participation ratios for each. A correction that
returns 0.543 with 2.88 and 8.68 explains the record. If none returns them, the record's figures have no
reproducible definition behind them and the recomputed values stand alone, which is what the paper now
says either way.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find_all(name):
    return sorted(p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._"))


src = [p for p in find_all("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
sel = [p for p in find_all("*.npz") if "__seed-" in p.name]
assert len(sel) == 375, len(sel)
runs = W / "runs"; runs.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
TARGET = {"max_squared_share": 0.543, "participation_ratio_margin": 2.88, "participation_ratio_accuracy": 8.68}
report = {"design": __doc__, "target": TARGET, "phenotypes": {}}


def describe(psi):
    s = psi ** 2
    share = s / s.sum()
    return {"max_squared_share": float(share.max()),
            "participation_ratio_squared": float(1.0 / np.sum(share ** 2)),
            "participation_ratio_from_abs_weights": float(np.sum(np.abs(psi)) ** 2 / float(s.sum()))}


for name in ("margin", "accuracy"):
    est = estimate(pop, name, check=False)
    T, U = np.asarray(est.T, float), np.asarray(est.U, float)
    keys, inv = np.unique(np.asarray(pop.recipe), return_inverse=True)
    G = keys.size
    sU = float(U.sum())
    th = float(T.sum()) / sU
    r = T - th * U
    e = np.bincount(inv, weights=r, minlength=G)
    u_g = np.bincount(inv, weights=U, minlength=G)
    h = u_g / sU
    cell = {"theta": th, "n_clusters": int(G), "max_leverage": float(h.max()),
            "plain": describe(e / sU),
            "cr1": describe(np.sqrt(G / (G - 1.0)) * e / sU),
            "cr2": describe(e / np.sqrt(1.0 - h) / sU),
            "cr3": describe(e / (1.0 - h) / sU)}
    jack = []
    for g in range(G):
        keep = inv != g
        thg = float(T[keep].sum()) / float(U[keep].sum())
        jack.append(float(np.bincount(inv, weights=T - thg * U, minlength=G)[g]) / sU)
    cell["jackknife"] = describe(np.asarray(jack))
    report["phenotypes"][name] = cell
    print(f"[{name}] {json.dumps(cell)}", flush=True)

margin, accuracy = report["phenotypes"]["margin"], report["phenotypes"]["accuracy"]
report["match"] = {k: {"share_gap": abs(margin[k]["max_squared_share"] - TARGET["max_squared_share"]),
                       "pr_margin_gap": abs(margin[k]["participation_ratio_squared"] - TARGET["participation_ratio_margin"]),
                       "pr_accuracy_gap": abs(accuracy[k]["participation_ratio_squared"] - TARGET["participation_ratio_accuracy"])}
                   for k in ("plain", "cr1", "cr2", "cr3", "jackknife")}
best = min(report["match"], key=lambda k: report["match"][k]["share_gap"])
report["closest_to_record"] = best
print(f"[match] {json.dumps(report['match'])} closest {best}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_influence_b.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
