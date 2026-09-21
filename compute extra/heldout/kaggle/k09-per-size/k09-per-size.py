"""k09 (CPU): the shipped-battery estimate on each size band, which the held-out result sits next to.

The protocol says the held-out number is reported beside the original-trait
estimate restricted to the same sizes, and that comparison needs the per-band
numbers to exist before the held-out scores do. This kernel writes them, along
with the estimate on the fallback scope of 530M and larger, so both possible
production scopes have their reference ready.

Every cell uses the paper's own statistic and the same wild cluster bootstrap-t
over recipe clusters. Bands hold 25 configurations each, which is the cluster
count the interval is designed for, so the per-band intervals are wider than the
pooled one by design rather than by accident.
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
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402

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
sizes = info["sizes"]
print(f"[pop] N={pop.N} over sizes {sizes}", flush=True)


def cell(p, name):
    """Both intervals, because one size band can degenerate the bootstrap.

    A single band carries 25 configurations in 25 recipe clusters with one
    configuration each, and the wild bootstrap-t can then return no finite draw
    at all. The cluster-robust t is defined whenever the influence values are,
    so the per-band rows carry it next to the bootstrap rather than a gap.
    """
    e = estimate(p, name, check=False)
    try:
        ci = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=N_BOOT, seed=0)
        lo, hi = float(ci.lo), float(ci.hi)
    except RuntimeError as error:
        print(f"[undefined] {name}: {error}", flush=True)
        lo = hi = float("nan")
    rob = cluster_t_interval(e.T, e.U, p.recipe)
    return {"lambda_hat": e.lambda_hat, "ci95": [lo, hi], "width": hi - lo,
            "excludes_one": bool(lo > 1 or hi < 1),
            "ci95_cluster_robust": [float(rob.lo), float(rob.hi)],
            "excludes_one_cluster_robust": bool(rob.lo > 1 or rob.hi < 1),
            "N": p.N, "clusters": int(p.n_clusters),
            "sigma_agg": float(e.sigma_agg), "sigma_indep": float(e.sigma_indep),
            "k_eff": float(e.k_eff), "rbar_e": float(e.rbar_e)}


groups = {"all": sizes, "fallback_530M_and_up": [z for z in sizes if z in ("530M", "750M", "1B")]}
groups.update({z: [z] for z in sizes})
out = {"n_boot": N_BOOT, "groups": {}, "sizes": sizes,
       "note": "the shipped ten-benchmark battery, for the held-out number to sit beside",
       "status": "pre-registered as the comparison in PROTOCOL_heldout.md"}
for label, keep in groups.items():
    idx = np.flatnonzero(np.isin(pop.size, [sizes.index(z) for z in keep]))
    sub = pop.subset(idx)
    out["groups"][label] = {name: cell(sub, name) for name in (MARGIN, ACCURACY)}
    m = out["groups"][label][MARGIN]
    print(f"[{label:>20}] margin {m['lambda_hat']:.4f} [{m['ci95'][0]:.3f}, {m['ci95'][1]:.3f}] "
          f"over N={m['N']} in {m['clusters']} clusters", flush=True)

# Leave one benchmark out, exhaustively, so no single benchmark can be said to
# carry the headline without the number that shows it.
out["leave_one_out"] = {}
for name in (MARGIN, ACCURACY):
    rows = {}
    for j, trait in enumerate(TRAITS):
        idx = [i for i in range(pop.K) if i != j]
        ph = {k: Phenotype(v.name, v.A[:, :, idx], v.B[:, :, idx]) for k, v in pop.phenotypes.items()}
        sub = Population(ph, pop.gainA, pop.gainB, pop.batch, pop.recipe, pop.size,
                         [pop.traits[i] for i in idx], pop.config_ids, pop.n_items)
        rows[trait] = cell(sub, name)
    out["leave_one_out"][name] = rows
    worst = min(rows, key=lambda t2: rows[t2]["lambda_hat"])
    best = max(rows, key=lambda t2: rows[t2]["lambda_hat"])
    print(f"[leave-one-out {name}] dropping {worst} gives {rows[worst]['lambda_hat']:.4f}, "
          f"dropping {best} gives {rows[best]['lambda_hat']:.4f}", flush=True)

out["wall_seconds"] = time.time() - t0
(W / "per_size_reference.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
