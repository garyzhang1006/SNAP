"""k11 (CPU): does any single recipe cluster carry the headline.

The interval clusters on the 25 recipes, so a reader can reasonably ask whether
one recipe supplies the excess correlation. This refits the estimate 25 times,
dropping one recipe each time, and reports the point estimate and interval from
the remaining 24. It also drops each size band in turn, which is the other
grouping the design has.

Nothing here is a robustness claim about the method. It answers a narrower
question, which is whether the number moves when one group leaves.
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
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402

N_BOOT = 4999

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
runs_dir = TMP / "runs_shipped"
shutil.rmtree(runs_dir, ignore_errors=True)
runs_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, runs_dir / p.name)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
recipes, sizes = info["recipes"], info["sizes"]


def cell(p, name):
    e = estimate(p, name, check=False)
    try:
        ci = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=N_BOOT, seed=0)
        lo, hi = float(ci.lo), float(ci.hi)
    except RuntimeError:
        lo = hi = float("nan")
    rob = cluster_t_interval(e.T, e.U, p.recipe)
    return {"lambda_hat": e.lambda_hat, "ci95": [lo, hi],
            "ci95_cluster_robust": [float(rob.lo), float(rob.hi)],
            "excludes_one": bool(lo > 1 or hi < 1), "N": p.N, "clusters": int(p.n_clusters)}


out = {"n_boot": N_BOOT, "full": {}, "leave_recipe_out": {}, "leave_size_out": {},
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md"}
for name in (MARGIN, ACCURACY):
    out["full"][name] = cell(pop, name)
    rows = {}
    for j, r in enumerate(recipes):
        keep = np.flatnonzero(pop.recipe != j)
        rows[r] = cell(pop.subset(keep), name)
    out["leave_recipe_out"][name] = rows
    lo = min(rows, key=lambda k: rows[k]["lambda_hat"])
    hi = max(rows, key=lambda k: rows[k]["lambda_hat"])
    print(f"[{name}] full {out['full'][name]['lambda_hat']:.4f}; dropping {lo} gives "
          f"{rows[lo]['lambda_hat']:.4f} and dropping {hi} gives {rows[hi]['lambda_hat']:.4f}", flush=True)
    srows = {}
    for j, z in enumerate(sizes):
        keep = np.flatnonzero(pop.size != j)
        srows[z] = cell(pop.subset(keep), name)
    out["leave_size_out"][name] = srows
    print(f"[{name}] size drops: " + ", ".join(f"{z} {v['lambda_hat']:.3f}" for z, v in srows.items()), flush=True)

out["wall_seconds"] = time.time() - t0
(W / "leave_group_out.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
