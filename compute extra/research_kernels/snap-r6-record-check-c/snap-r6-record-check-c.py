"""Third pass over the record, covering the battery reliability the b run measured with the wrong quantity.

Design fixed before running (2026-09-16, written 01:30 EDT). The b run tried to check the paper's
battery-level rho_g of 0.73 and computed the mean seed correlation instead, which is a different
quantity and returned 0.0608. The package defines rho_g as Lambda squared over Lambda squared plus
vbar, where vbar is the ratio of summed item-noise variance to summed seed variance, so this run
computes it that way for both scales. It also recomputes the three information-ratio summaries the
pipeline reported without releasing the individual values, which are a median of 1.61, a minimum of
1.571 and a maximum of 1.732, and it counts the accuracy traits with negative reliability and with
reliability below 0.10, recorded as two and two. The planning comparison of 0.49 at Lambda squared
1.819 is a fixed input rather than a measurement, so it needs no recomputation.
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
from seednoise.estimator import correlation, estimate, phenotypic_correlation, rbar_e, sigma_e  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.nulls import permute_seed_labels  # noqa: E402

from seednoise.reliability import aggregate_reliability, information_ratio, variance_components  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
RECORD = {"rho_g": 0.73, "planning_rho_g": 0.49, "planning_lambda2": 1.819,
          "information_ratio": {"median": 1.61, "min": 1.571, "max": 1.732},
          "accuracy_reliability_negative": 2, "accuracy_reliability_below_0.10": 2}
report = {"design": __doc__, "record": RECORD, "recomputed": {}}

for name in ("margin", "accuracy"):
    est = estimate(pop, name, check=False)
    lam = float(est.lambda_hat)
    comp = variance_components(pop, name)
    vbar = float(comp.vbar)
    rel = np.asarray(comp.reliability, float)
    cell = {"lambda_hat": lam, "lambda_squared": lam ** 2, "vbar": vbar,
            "rho_g": float(aggregate_reliability(lam, vbar)),
            "rho_g_at_planning_lambda2": float(aggregate_reliability(np.sqrt(RECORD["planning_lambda2"]), vbar)),
            "n_reliability_negative": int(np.sum(rel < 0)),
            "n_reliability_below_0.10": int(np.sum((rel >= 0) & (rel < 0.10))),
            "n_reliability_undefined": int(np.sum(~np.isfinite(rel))),
            "reliability": rel.tolist(), "traits": list(comp.traits)}
    report["recomputed"][name] = cell
    print(f"[{name}] {json.dumps(cell)}", flush=True)

ph = pop.pheno("accuracy")
p = 0.5 * (ph.A.mean(axis=1) + ph.B.mean(axis=1))
p = np.clip(p.mean(axis=0), 1e-6, 1 - 1e-6)
ir = information_ratio(p)
report["recomputed"]["information_ratio"] = {"median": float(np.median(ir)), "min": float(ir.min()),
                                             "max": float(ir.max()), "per_trait": ir.tolist(),
                                             "mean_accuracy_per_trait": p.tolist(),
                                             "record": RECORD["information_ratio"]}
print(f"[information_ratio] {json.dumps(report['recomputed']['information_ratio'])}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_record_check_c.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
