"""k08 (CPU): how many seeds per model a practitioner needs to see the excess.

The paper's practical claim is that seeds are correlated across benchmarks, and
the number that decides whether anyone can act on it is the seed count. The
shipped design has three runs per configuration, so the question has to be
answered by simulation, and this kernel runs it at the correlation the observed
data implies rather than at a round number.

Method. Read the shipped population, take its estimated mean seed correlation
for each phenotype, and simulate populations at that correlation with the real
item counts and 125 configurations, sweeping the runs per configuration from two
to eight. Each replicate gets the same wild cluster bootstrap-t the paper uses,
and the sweep reports how often the interval excludes one along with the median
width. The simulation is equicorrelated, which is the same matching the appendix
uses, so it describes a battery whose excess is spread evenly rather than
concentrated in one pair.
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
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402
from seednoise.simulate import default_spec, simulate  # noqa: E402

RUNS = [2, 3, 4, 5, 6, 8]
N_REP = 300
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

out = {"runs_swept": RUNS, "n_rep": N_REP, "n_boot": N_BOOT, "seed": SEED, "by_phenotype": {},
       "note": "equicorrelated seed covariance matched to the observed mean correlation, "
               "125 configurations, released item counts",
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md"}
for name in (MARGIN, ACCURACY):
    obs = estimate(pop, name, check=False)
    rbar = float(obs.rbar_e)
    out["by_phenotype"][name] = {"observed_lambda": obs.lambda_hat, "observed_rbar_e": rbar, "by_runs": {}}
    print(f"[obs] {name} Lambda {obs.lambda_hat:.4f}, mean seed correlation {rbar:.4f}", flush=True)
    for R in RUNS:
        excl, width, lam = 0, [], []
        for rep in range(N_REP):
            spec = default_spec(rbar_e=rbar, n_config=125, n_runs=R, n_recipes=25, n_sizes=5,
                                seed=SEED + 1000 * R + rep)
            sim = simulate(spec)
            sim_pop = sim[0] if isinstance(sim, tuple) else sim
            e = estimate(sim_pop, name, check=False)
            lam.append(e.lambda_hat)
            try:
                ci = wild_bootstrap_t(e.T, e.U, sim_pop.recipe, n_boot=N_BOOT, seed=rep)
            except RuntimeError:
                continue
            width.append(ci.hi - ci.lo)
            excl += int(ci.lo > 1 or ci.hi < 1)
        out["by_phenotype"][name]["by_runs"][R] = {
            "replicates": N_REP, "defined": len(width),
            "lambda_median": float(np.median(lam)),
            "width_median": float(np.median(width)) if width else float("nan"),
            "excludes_one_share": excl / len(width) if width else float("nan")}
        s = out["by_phenotype"][name]["by_runs"][R]
        print(f"[R={R}] {name}: median Lambda {s['lambda_median']:.3f}, median width "
              f"{s['width_median']:.3f}, excludes one in {s['excludes_one_share']:.2f}", flush=True)

out["wall_seconds"] = time.time() - t0
(W / "seed_count_power.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
