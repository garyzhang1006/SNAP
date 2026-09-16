"""R6 leave-one-out robustness of the reported intervals, over recipes, size bands and benchmarks.

Design fixed before running (2026-09-15, written 22:40 EDT). Appendix A reports that one recipe carries
0.520 of the squared margin influence and that removing it moves the estimate by 0.037, which is the
largest single-recipe change. The paper reports that number as a concentration diagnostic, and it never
asks the question a reviewer will ask next, which is whether the conclusion itself survives each
deletion. The conclusion is that the margin interval excludes one on the full battery, that the accuracy
interval includes one there, and that both stay above one once BoolQ is removed. This run recomputes all
three statements under every deletion the design admits. It drops each of the 25 recipes in turn, each of
the five size bands in turn, and each of the ten benchmarks in turn, and for margins on the full battery
it also drops all 300 pairs of recipes, which is the strictest version of the concentration worry. Every
cell reports the estimate and the shipped wild interval at 4,999 draws with seed 0, so the intervals are
the ones the paper reports rather than a new construction. A deletion that flips any of the three
statements is a finding the paper has to carry, and a clean sweep is a robustness result it currently
lacks.
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
runs_dir = W / "runs"; runs_dir.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs_dir / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)


def restrict(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, :, m], ph.B[:, :, m])
    n_items = None if p.n_items is None else np.asarray(p.n_items)[m]
    return Population({name: sub}, p.gainA, p.gainB, p.batch, p.recipe, p.size,
                      [p.traits[j] for j in m], p.config_ids, n_items)


N_BOOT = 4999
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
RECIPES = list(np.unique(np.asarray(pop.recipe)))
SIZES = list(np.unique(np.asarray(pop.size)))
print(f"[base] {len(RECIPES)} recipes {len(SIZES)} sizes {len(TR)} traits", flush=True)


def interval(p, name, idx, keep_recipes=None):
    """Lambda and the shipped wild interval on a restricted population."""
    q = p if keep_recipes is None else p.subset_clusters(list(keep_recipes))
    sub = restrict(q, name, idx)
    est = estimate(sub, name, check=False)
    iv = wild_bootstrap_t(est.T, est.U, sub.recipe, n_boot=N_BOOT, seed=0)
    lo, hi = float(iv.lo), float(iv.hi)
    return {"lambda_hat": float(est.lambda_hat), "lo": lo, "hi": hi,
            "excludes_one": bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 1.0 or hi < 1.0)),
            "includes_one": bool(np.isfinite(lo) and np.isfinite(hi) and lo <= 1.0 <= hi),
            "defined": bool(np.isfinite(lo) and np.isfinite(hi))}


def size_subset(p, keep):
    """Population restricted to the configurations whose size band is in keep."""
    return p.subset(np.flatnonzero(np.isin(np.asarray(p.size), list(keep))))


BATTERIES = (("full", FULL), ("without_boolq", DROP))
report = {"design": __doc__, "traits": TR, "n_boot": N_BOOT, "recipes": [str(r) for r in RECIPES],
          "sizes": [str(s) for s in SIZES], "base": {}, "leave_one_recipe": {}, "leave_one_size": {},
          "leave_one_trait": {}, "leave_two_recipes_full_margin": {}}

for label, idx in BATTERIES:
    for name in ("margin", "accuracy"):
        report["base"][f"{label}/{name}"] = interval(pop, name, idx)
print(f"[base] {json.dumps(report['base'])}", flush=True)

t1 = time.time()
for label, idx in BATTERIES:
    for name in ("margin", "accuracy"):
        rows = {}
        for g in RECIPES:
            rows[str(g)] = interval(pop, name, idx, keep_recipes=[r for r in RECIPES if r != g])
        report["leave_one_recipe"][f"{label}/{name}"] = rows
print(f"[recipes] {time.time() - t1:.0f}s", flush=True)

for label, idx in BATTERIES:
    for name in ("margin", "accuracy"):
        rows = {}
        for s in SIZES:
            rows[str(s)] = interval(size_subset(pop, [x for x in SIZES if x != s]), name, idx)
        report["leave_one_size"][f"{label}/{name}"] = rows
print("[sizes] done", flush=True)

for name in ("margin", "accuracy"):
    rows = {}
    for j, tr in enumerate(TR):
        rows[tr] = interval(pop, name, [x for x in FULL if x != j])
    report["leave_one_trait"][f"full/{name}"] = rows
print("[traits] done", flush=True)

t2 = time.time()
pairs = {}
for a in range(len(RECIPES)):
    for b in range(a + 1, len(RECIPES)):
        keep = [r for i, r in enumerate(RECIPES) if i not in (a, b)]
        pairs[f"{RECIPES[a]}|{RECIPES[b]}"] = interval(pop, "margin", FULL, keep_recipes=keep)
report["leave_two_recipes_full_margin"] = pairs
print(f"[pairs] {len(pairs)} in {time.time() - t2:.0f}s", flush=True)


def summarise(rows, key):
    v = [r for r in rows.values() if r["defined"]]
    return {"n": len(rows), "n_defined": len(v),
            "n_true": int(sum(r[key] for r in rows.values())),
            "all_true": bool(all(r[key] for r in rows.values())),
            "lambda_min": min(r["lambda_hat"] for r in rows.values()),
            "lambda_max": max(r["lambda_hat"] for r in rows.values()),
            "closest_endpoint_to_one": min((abs(r["lo"] - 1.0) if r["lo"] > 1.0 else abs(r["hi"] - 1.0))
                                           for r in v) if v else None}


summary = {}
for block in ("leave_one_recipe", "leave_one_size", "leave_one_trait"):
    for cellname, rows in report[block].items():
        key = "includes_one" if cellname == "full/accuracy" else "excludes_one"
        summary[f"{block}/{cellname}"] = summarise(rows, key)
summary["leave_two_recipes_full_margin"] = summarise(report["leave_two_recipes_full_margin"], "excludes_one")
report["summary"] = summary
print(f"[summary] {json.dumps(summary)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_leave_one_out.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
