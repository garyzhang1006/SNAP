"""Second pass over the record, covering the figures snap-r6-record-check left alone.

Design fixed before running (2026-09-16, written 01:15 EDT). The first pass found that the design
effects and three of four standard errors reproduce, that one standard error had been rounded down, and
that the permutation coverage sits about two standard errors away from the recorded value. Five figures
from the same record remain in the paper. The first is the pair of Frobenius distances between the seed
correlation and the phenotypic correlation, recorded as 5.59 and 6.49, together with the counts of
undefined off-diagonal entries, recorded as eighteen and 34, and the contributions of substituted
diagonal entries, recorded as 1.0 and 2.0. The second is the pair of interval half-widths, recorded as
0.0974 and 0.082. The third is the cluster-robust comparator under the same seed-label permutation,
recorded as coverage 0.881 and 0.941 with above-one rates 0.044 and 0.023, together with the statement
that no margin permutation reaches the observed estimate and that the accuracy upper tail holds 0.021.
The fourth is the pair of delete-one-recipe jackknife standard errors, recorded as 0.049 and 0.039. The
fifth is the battery-level seed correlation, recorded as 0.73, with two accuracy traits at negative
reliability and two more below 0.10. Each one is recomputed here and printed beside the recorded value.
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
from seednoise.reliability import variance_components  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
K = pop.K
RECORD = {"frobenius": {"margin": 5.59, "accuracy": 6.49},
          "undefined_offdiagonal": {"margin": 18, "accuracy": 34},
          "diagonal_contribution": {"margin": 1.0, "accuracy": 2.0},
          "half_width": {"margin": 0.0974, "accuracy": 0.082},
          "permutation_cluster_t_coverage": {"margin": 0.881, "accuracy": 0.941},
          "permutation_cluster_t_above": {"margin": 0.044, "accuracy": 0.023},
          "permutation_accuracy_upper_tail": 0.021,
          "jackknife_se": {"margin": 0.049, "accuracy": 0.039},
          "battery_rbar_e": 0.73}
report = {"design": __doc__, "record": RECORD, "recomputed": {}}

# 1. Frobenius distance between the seed correlation and the phenotypic correlation.
frob = {}
for name in ("margin", "accuracy"):
    S = sigma_e(pop, name)
    RE = correlation(S)
    RP = phenotypic_correlation(pop, name)
    bad = ~np.isfinite(RE)
    filled = np.where(bad, 0.0, RE)
    D = filled - RP
    off = ~np.eye(K, dtype=bool)
    frob[name] = {"distance": float(np.sqrt(np.sum(D ** 2))),
                  "undefined_offdiagonal_ordered": int(np.sum(bad & off)),
                  "undefined_diagonal": int(np.sum(bad & np.eye(K, dtype=bool))),
                  "diagonal_squared_contribution": float(np.sum(np.diag(D) ** 2)),
                  "negative_seed_variances": int(np.sum(np.diag(S) <= 0)),
                  "record_distance": RECORD["frobenius"][name]}
    print(f"[frobenius/{name}] {json.dumps(frob[name])}", flush=True)
report["recomputed"]["frobenius"] = frob

# 2. Interval half-widths on the shipped wild interval.
half = {}
for name in ("margin", "accuracy"):
    e = estimate(pop, name, check=False)
    iv = wild_bootstrap_t(e.T, e.U, pop.recipe, n_boot=4999, seed=0)
    ct = cluster_t_interval(e.T, e.U, pop.recipe)
    half[name] = {"wild_half_width": float((iv.hi - iv.lo) / 2), "wild": [float(iv.lo), float(iv.hi)],
                  "cluster_t_half_width": float((ct.hi - ct.lo) / 2), "record": RECORD["half_width"][name]}
    print(f"[halfwidth/{name}] {json.dumps(half[name])}", flush=True)
report["recomputed"]["half_width"] = half

# 3. Cluster-robust comparator under the seed-label permutation, 2,000 permutations.
N_REP = 2000
perm = {}
for name in ("margin", "accuracy"):
    t1 = time.time()
    obs = float(estimate(pop, name, check=False).lambda_hat)
    rng = np.random.default_rng(0)
    cov = above = below = bad = 0
    reach = 0
    for rep in range(N_REP):
        q = permute_seed_labels(pop, name, rng)
        e = estimate(q, f"{name}|perm", check=False)
        reach += float(e.lambda_hat) >= obs
        ct = cluster_t_interval(e.T, e.U, q.recipe)
        lo, hi = float(ct.lo), float(ct.hi)
        if np.isfinite(lo) and np.isfinite(hi):
            cov += lo <= 1.0 <= hi; above += lo > 1.0; below += hi < 1.0
        else:
            bad += 1
    perm[name] = {"cluster_t_coverage": cov / N_REP, "above_one": above / N_REP, "below_one": below / N_REP,
                  "undefined": bad / N_REP, "share_reaching_observed": reach / N_REP,
                  "observed": obs, "record_coverage": RECORD["permutation_cluster_t_coverage"][name],
                  "record_above": RECORD["permutation_cluster_t_above"][name], "seconds": time.time() - t1}
    print(f"[perm/{name}] {json.dumps(perm[name])}", flush=True)
report["recomputed"]["permutation_cluster_t"] = perm

# 4. Delete-one-recipe jackknife standard error of Lambda.
jack = {}
recipes = np.unique(pop.recipe)
G = recipes.size
for name in ("margin", "accuracy"):
    full = float(estimate(pop, name, check=False).lambda_hat)
    vals = np.array([float(estimate(pop.subset_clusters([r for r in recipes if r != g]), name,
                                    check=False).lambda_hat) for g in recipes])
    se = float(np.sqrt((G - 1.0) / G * np.sum((vals - vals.mean()) ** 2)))
    jack[name] = {"jackknife_se": se, "full": full, "mean_leave_one_out": float(vals.mean()),
                  "record": RECORD["jackknife_se"][name]}
    print(f"[jackknife/{name}] {json.dumps(jack[name])}", flush=True)
report["recomputed"]["jackknife"] = jack

# 5. Battery-level seed correlation and the per-trait reliabilities.
bat = {}
for name in ("margin", "accuracy"):
    lam = float(estimate(pop, name, check=False).lambda_hat)
    comp = variance_components(pop, name)
    rel = np.asarray(comp.reliability if hasattr(comp, "reliability") else [], float)
    bat[name] = {"lambda_hat": lam, "rbar_e": float(rbar_e(lam, K)),
                 "n_reliability_negative": int(np.sum(rel < 0)) if rel.size else None,
                 "n_reliability_below_0.10": int(np.sum((rel >= 0) & (rel < 0.10))) if rel.size else None,
                 "reliability": rel.tolist() if rel.size else None}
    print(f"[battery/{name}] {json.dumps(bat[name])}", flush=True)
report["recomputed"]["battery"] = bat
report["record_battery_rbar_e"] = RECORD["battery_rbar_e"]

report["wall_seconds"] = time.time() - t0
(W / "r6_record_check_b.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
