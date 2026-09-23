"""snap-r2-r1-08 (CPU only): fixed-bank inflation on the 375 released DataDecide runs.

The question a user of the released bank asks: across replicate runs, how much
larger is the standard deviation of the full-bank battery average than the
independence value built from the per-benchmark run variances on the same
items? No item split, so run-by-item deviations on the fixed bank stay in both
numerator and denominator.

Computation, all with seednoise at the paper's commit (Kaggle dataset
garyzhang11111/seed-noise-src, the one k05 used):
  full-bank trait scores  seednoise.phenotypes.half_scores(items, all-True mask, K)
  population              seednoise.population.Population with half A = half B = full-bank scores,
                          configurations and run order exactly as seednoise.build.build_population
                          (the script asserts the configuration ids match)
  ratio                   seednoise.estimator.estimate(...).lambda_hat, i.e. sqrt(sum T / sum U), where
                          with A = B, T is the replicate variance of the battery average and U the
                          independence value (sum of per-benchmark replicate variances over K^2)
  intervals               seednoise.inference.wild_bootstrap_t (4,999 draws, seed 0, 25 recipe clusters)
                          and cluster_t_interval, as compute2/analysis/estimates.all_intervals
Beside it, the split-half SNAP estimate on the same population (the paper's 1.24395).
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
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.phenotypes import half_scores  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402
from seednoise.store import load_run  # noqa: E402

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
run_dir = Path("/kaggle/tmp") / "runs_shipped"
shutil.rmtree(run_dir, ignore_errors=True)
run_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, run_dir / p.name)
pop, info = build_population(run_dir, TRAITS, n_runs=3)
lam = estimate(pop, MARGIN).lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"
K, R = len(TRAITS), pop.R

cells = {}
for f in sorted(run_dir.glob("*.npz")):
    items, meta = load_run(f)
    m, a = half_scores(items, np.ones(items.n_items, dtype=bool), K)
    cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, m, a))
keys = [tuple(c) for c in pop.config_ids]
assert all(len(cells[k]) == R for k in keys), "a configuration in the population lacks three runs here"
M = np.zeros((pop.N, R, K)); A = np.zeros((pop.N, R, K)); batch = np.zeros((pop.N, R), dtype=np.int64)
for c, k in enumerate(keys):
    for r, (meta, m, a) in enumerate(sorted(cells[k], key=lambda t: t[0]["batch"])):
        M[c, r], A[c, r], batch[c, r] = m, a, meta["batch"]
assert np.array_equal(batch, pop.batch), "run order differs from build_population"
fixed = Population({MARGIN: Phenotype(MARGIN, M, M), ACCURACY: Phenotype(ACCURACY, A, A)},
                   batch=batch, recipe=pop.recipe, size=pop.size, traits=list(TRAITS),
                   config_ids=pop.config_ids)


def keep_traits(p, drop):
    idx = [j for j, t in enumerate(p.traits) if t not in drop]
    ph = {n: Phenotype(n, v.A[:, :, idx], v.B[:, :, idx]) for n, v in p.phenotypes.items()}
    return Population(ph, batch=p.batch, recipe=p.recipe, size=p.size, traits=[p.traits[j] for j in idx], config_ids=p.config_ids)


def row(p, name):
    e = estimate(p, name, check=False)
    out = {"lambda": e.lambda_hat, "sigma_agg": e.sigma_agg, "sigma_indep": e.sigma_indep,
           "sum_T": float(e.T.sum()), "sum_U": float(e.U.sum()), "N": p.N, "K": p.K}
    out["wild"] = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=4999, seed=0).as_row()
    try:
        out["cluster_t"] = cluster_t_interval(e.T, e.U, p.recipe).as_row()
    except Exception as ex:  # noqa: BLE001
        out["cluster_t"] = {"error": f"{type(ex).__name__}: {ex}"}
    return out


res = {}
for battery, drop in (("all_ten", ()), ("no_boolq", ("boolq",))):
    for name in (MARGIN, ACCURACY):
        fb, sp = row(keep_traits(fixed, drop), name), row(keep_traits(pop, drop), name)
        res.setdefault(battery, {})[name] = {"fixed_bank": fb, "split_half_snap": sp,
                                             "fixed_over_split_sigma_agg": fb["sigma_agg"] / sp["sigma_agg"],
                                             "fixed_over_split_sigma_indep": fb["sigma_indep"] / sp["sigma_indep"]}
        print(f"[{battery} {name}] fixed-bank {fb['lambda']:.4f} [{fb['wild']['lo']:.4f}, {fb['wild']['hi']:.4f}] | "
              f"split {sp['lambda']:.4f} [{sp['wild']['lo']:.4f}, {sp['wild']['hi']:.4f}]", flush=True)

out = {"results": res, "population": {"N": pop.N, "R": R, "recipes": len(info["recipes"]), "sizes": info["sizes"]},
       "estimand": "sqrt(replicate variance of the full-bank battery average / independence value), same 375 runs, no item split",
       "wall_seconds": time.time() - t0}
(W / "r1_08_fixed_bank.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
