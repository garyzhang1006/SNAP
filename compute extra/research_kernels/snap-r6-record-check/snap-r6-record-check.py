"""Recomputation of the figures the paper still takes from the original analysis record.

Design fixed before running (2026-09-16, written 00:50 EDT). snap-r6-influence showed that one figure
carried from the original record, the largest recipe's share of squared margin influence, doesn't
reproduce under the definition the paper names. A single failure of that kind is a reason to check the
other numbers the paper still attributes to the record rather than to a run in this revision. Three
remain. The first is the seed-label permutation experiment, reported as coverage 0.925 for margins and
0.954 for accuracy with the margin interval falling below the null in 0.049 of replicates. The second is
the pair of numerator design effects, reported as 2.06 and 1.26 from one plus four times the intraclass
correlation. The third is the pair of squared standard error ratios, reported as 0.24 and 0.53 from
0.045 against 0.093 and 0.038 against 0.052. This run recomputes all three from the 125 shipped
configurations, with the permutation experiment at 2,000 replicates and seed 0, which are the defaults
the record used. Every recomputed value is printed beside the reported one with its gap, and nothing
here is a new analysis, so a gap means the paper needs a correction rather than a new result.
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
from seednoise.inference import cluster_influence, wild_bootstrap_t  # noqa: E402
from seednoise.nulls import permute_seed_labels  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
REPORTED = {"permutation_coverage": {"margin": 0.925, "accuracy": 0.954},
            "permutation_below_null_margin": 0.049,
            "design_effect": {"margin": 2.06, "accuracy": 1.26},
            "se_ratio": {"margin": 0.24, "accuracy": 0.53},
            "se_terms": {"margin": [0.045, 0.093], "accuracy": [0.038, 0.052]}}
report = {"design": __doc__, "reported": REPORTED, "recomputed": {}}

N_REP = 2000
perm = {}
for name in ("margin", "accuracy"):
    t1 = time.time()
    rng = np.random.default_rng(0)
    cov = below = above = bad = 0
    ests = []
    for rep in range(N_REP):
        q = permute_seed_labels(pop, name, rng)
        # permute_seed_labels renames the phenotype, so estimating by the original
        # name would silently score the unpermuted scores instead.
        e = estimate(q, f"{name}|perm", check=False)
        ests.append(float(e.lambda_hat))
        try:
            iv = wild_bootstrap_t(e.T, e.U, q.recipe, n_boot=4999, seed=rep)
            lo, hi = float(iv.lo), float(iv.hi)
        except Exception:  # noqa: BLE001
            lo = hi = float("nan")
        if np.isfinite(lo) and np.isfinite(hi):
            cov += lo <= 1.0 <= hi
            below += hi < 1.0
            above += lo > 1.0
        else:
            bad += 1
    v = np.asarray(ests, float); v = v[np.isfinite(v)]
    perm[name] = {"coverage": cov / N_REP, "interval_below_null": below / N_REP,
                  "interval_above_null": above / N_REP, "undefined": bad / N_REP,
                  "mean_estimate": float(v.mean()), "sd_estimate": float(v.std(ddof=1)),
                  "mc_se": float(np.sqrt((cov / N_REP) * (1 - cov / N_REP) / N_REP)),
                  "seconds": time.time() - t1}
    print(f"[perm/{name}] {json.dumps(perm[name])}", flush=True)
report["recomputed"]["permutation"] = perm

# Numerator design effect 1 + 4 rho_ICC, with rho_ICC the recipe intraclass correlation of T_c.
deff = {}
for name in ("margin", "accuracy"):
    est = estimate(pop, name, check=False)
    T = np.asarray(est.T, float)
    keys, inv = np.unique(np.asarray(pop.recipe), return_inverse=True)
    n_g = np.bincount(inv, minlength=keys.size).astype(float)
    grand = T.mean()
    gm = np.bincount(inv, weights=T, minlength=keys.size) / n_g
    between = float(np.sum(n_g * (gm - grand) ** 2) / (keys.size - 1))
    within = float(np.sum((T - gm[inv]) ** 2) / (T.size - keys.size))
    n0 = float((T.size - np.sum(n_g ** 2) / T.size) / (keys.size - 1))
    var_b = max((between - within) / n0, 0.0)
    rho = var_b / (var_b + within)
    m = float(T.size) / keys.size
    deff[name] = {"rho_icc": rho, "one_plus_four_rho": 1 + 4 * rho,
                  "one_plus_m_minus_one_rho": 1 + (m - 1) * rho, "mean_cluster_size": m,
                  "reported": REPORTED["design_effect"][name]}
    print(f"[deff/{name}] {json.dumps(deff[name])}", flush=True)
report["recomputed"]["design_effect"] = deff

# Standard errors on Lambda, cluster-robust against a configuration-level version.
se = {}
for name in ("margin", "accuracy"):
    est = estimate(pop, name, check=False)
    T, U = np.asarray(est.T, float), np.asarray(est.U, float)
    lam = float(est.lambda_hat)
    theta = float(T.sum() / U.sum())
    psi_recipe, _, _ = cluster_influence(T, U, pop.recipe)
    psi_config, _, _ = cluster_influence(T, U, np.arange(T.size))
    to_lambda = 1.0 / (2.0 * np.sqrt(theta))
    se_recipe = float(np.sqrt(np.sum(psi_recipe ** 2))) * to_lambda
    se_config = float(np.sqrt(np.sum(psi_config ** 2))) * to_lambda
    se[name] = {"lambda_hat": lam, "se_config_cluster": se_config, "se_recipe_cluster": se_recipe,
                "squared_ratio_config_over_recipe": (se_config / se_recipe) ** 2,
                "reported_terms": REPORTED["se_terms"][name], "reported_ratio": REPORTED["se_ratio"][name]}
    print(f"[se/{name}] {json.dumps(se[name])}", flush=True)
report["recomputed"]["standard_errors"] = se

report["wall_seconds"] = time.time() - t0
(W / "r6_record_check.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
