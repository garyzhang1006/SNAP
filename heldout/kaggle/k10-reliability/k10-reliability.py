"""k10 (CPU): how much of each benchmark's seed signal survives item noise.

Lambda is a ratio of variances, and every one of those variances is measured
through a finite item sample, so a benchmark whose seed variance is small next
to its item noise contributes mostly noise to the aggregate. The paper reports
one split-half number for the competence proxy and nothing per benchmark, which
leaves a reviewer unable to see which of the ten carry the signal.

This kernel splits each benchmark's within-configuration variance into a seed
part and an item part with seednoise.reliability, converts that to a per
benchmark reliability, and puts a recipe-cluster bootstrap interval on each one.
It also reports the same split per size band, because item noise is a property
of the battery while seed variance is not, so the ratio moves with scale.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = TMP / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402

N_BOOT = 999
SEED = 20260917

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
runs_dir = TMP / "runs_shipped"
shutil.rmtree(runs_dir, ignore_errors=True)
runs_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, runs_dir / p.name)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
sizes = info["sizes"]
recipes = sorted(set(pop.recipe.tolist()))
print(f"[pop] N={pop.N} over {len(recipes)} recipe clusters and sizes {sizes}", flush=True)


def ratio(p, name):
    """Seed share of within-configuration variance, per benchmark."""
    c = variance_components(p, name)
    seed = np.asarray(c.sigma_e2, float)
    item = np.asarray(c.noise2, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return seed / (seed + item)


out = {"n_boot": N_BOOT, "seed": SEED, "traits": list(TRAITS), "by_phenotype": {}, "by_size": {},
       "note": "seed share of within-configuration variance; a negative seed variance is reported "
               "as measured rather than clipped, which can put a share outside zero to one",
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md"}
rng = np.random.default_rng(SEED)
for name in (MARGIN, ACCURACY):
    point = ratio(pop, name)
    draws = []
    for _ in range(N_BOOT):
        drawn = rng.choice(recipes, size=len(recipes), replace=True)
        draws.append(ratio(pop.subset_clusters(drawn), name))
    draws = np.asarray(draws)
    out["by_phenotype"][name] = {
        t: {"seed_share": float(point[j]),
            "ci95": [float(np.nanquantile(draws[:, j], 0.025)), float(np.nanquantile(draws[:, j], 0.975))]}
        for j, t in enumerate(TRAITS)}
    order = np.argsort(-point)
    print(f"[{name}] highest seed share: " + ", ".join(f"{TRAITS[j]} {point[j]:.3f}" for j in order[:3]),
          flush=True)
    print(f"[{name}] lowest seed share:  " + ", ".join(f"{TRAITS[j]} {point[j]:.3f}" for j in order[-3:]),
          flush=True)

for z in sizes:
    idx = np.flatnonzero(pop.size == sizes.index(z))
    sub = pop.subset(idx)
    out["by_size"][z] = {name: {t: float(ratio(sub, name)[j]) for j, t in enumerate(TRAITS)}
                         for name in (MARGIN, ACCURACY)}
    r = ratio(sub, MARGIN)
    print(f"[size {z}] margin seed share median {np.nanmedian(r):.3f}", flush=True)

out["wall_seconds"] = time.time() - t0
(W / "reliability.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
