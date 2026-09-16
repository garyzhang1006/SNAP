"""R15 composition sweep over every benchmark subset of size two or more.

Design fixed before running (2026-09-15, written 21:00 EDT). The paper reports single-benchmark
removals, which answer what one benchmark contributes but not how much the conclusion depends on the
battery as a whole. The plan asks that composition be evaluated without treating the ten benchmarks as
a sample from a population of benchmarks, so this run is descriptive. For each of the 1,013 subsets of
size two or more, we estimate inflation on all 125 configurations and attach a wild recipe-cluster
bootstrap interval with 4,999 draws and seed 0. The output records every subset's estimate, its
interval, whether the interval excludes one, and the subset's size and membership, for both
phenotypes. The summary reports the distribution by subset size, the share of subsets whose interval
excludes one, the same shares split by whether BoolQ or WinoGrande is present, and the extreme
subsets. These subsets overlap heavily and aren't independent, so the shares describe this battery
rather than estimating a rate over batteries.
"""
import json, platform, shutil, subprocess, sys, time
from itertools import combinations
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
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
TR = list(pop.traits)


def restrict(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, :, m], ph.B[:, :, m])
    n_items = None if p.n_items is None else np.asarray(p.n_items)[m]
    return Population({name: sub}, p.gainA, p.gainB, p.batch, p.recipe, p.size,
                      [p.traits[j] for j in m], p.config_ids, n_items)


report = {"design": __doc__, "traits": TR, "subsets": {}, "summary": {}}
for name in ("margin", "accuracy"):
    t1 = time.time(); rows = []
    for k in range(2, len(TR) + 1):
        for idx in combinations(range(len(TR)), k):
            sub = restrict(pop, name, idx)
            e = estimate(sub, name, check=False)
            lam = float(e.lambda_hat)
            try:
                iv = wild_bootstrap_t(e.T, e.U, sub.recipe, n_boot=4999, seed=0)
                lo, hi = float(iv.lo), float(iv.hi)
            except Exception:  # noqa: BLE001
                lo, hi = float("nan"), float("nan")
            rows.append({"size": k, "traits": [TR[j] for j in idx], "lambda": lam, "lo": lo, "hi": hi,
                         "excludes_one": bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 1.0 or hi < 1.0)),
                         "above_one": bool(np.isfinite(lo) and lo > 1.0)})
    report["subsets"][name] = rows
    lam = np.array([r["lambda"] for r in rows], float)
    fin = np.isfinite(lam)
    summary = {"n_subsets": len(rows), "n_finite": int(fin.sum()),
               "lambda": {"min": float(lam[fin].min()), "p25": float(np.percentile(lam[fin], 25)),
                          "median": float(np.median(lam[fin])), "p75": float(np.percentile(lam[fin], 75)),
                          "max": float(lam[fin].max())},
               "share_excludes_one": float(np.mean([r["excludes_one"] for r in rows])),
               "share_above_one": float(np.mean([r["above_one"] for r in rows])),
               "share_interval_undefined": float(np.mean([not np.isfinite(r["lo"]) or not np.isfinite(r["hi"]) for r in rows]))}
    summary["by_size"] = {}
    for k in range(2, len(TR) + 1):
        sel_k = [r for r in rows if r["size"] == k]
        v = np.array([r["lambda"] for r in sel_k], float); v = v[np.isfinite(v)]
        summary["by_size"][k] = {"n": len(sel_k), "median": float(np.median(v)), "min": float(v.min()), "max": float(v.max()),
                                 "share_excludes_one": float(np.mean([r["excludes_one"] for r in sel_k])),
                                 "share_above_one": float(np.mean([r["above_one"] for r in sel_k]))}
    for trait in TR:
        inc = [r for r in rows if trait in r["traits"]]
        exc = [r for r in rows if trait not in r["traits"]]
        mi = np.array([r["lambda"] for r in inc], float); me = np.array([r["lambda"] for r in exc], float)
        summary.setdefault("by_trait", {})[trait] = {
            "median_with": float(np.median(mi[np.isfinite(mi)])), "median_without": float(np.median(me[np.isfinite(me)])),
            "share_above_one_with": float(np.mean([r["above_one"] for r in inc])),
            "share_above_one_without": float(np.mean([r["above_one"] for r in exc]))}
    order = sorted([r for r in rows if np.isfinite(r["lambda"])], key=lambda r: r["lambda"])
    summary["lowest"] = order[:5]
    summary["highest"] = order[-5:]
    summary["full_battery"] = [r for r in rows if r["size"] == len(TR)][0]
    report["summary"][name] = summary
    print(f"[{name}] {time.time() - t1:.0f}s " + json.dumps({k: v for k, v in summary.items() if k in ("lambda", "share_excludes_one", "share_above_one", "share_interval_undefined")}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r15_composition.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
