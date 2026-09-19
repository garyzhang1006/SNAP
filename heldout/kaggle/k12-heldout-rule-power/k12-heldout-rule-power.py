"""k12 (CPU): what the registered held-out rule could have detected at each scope.

Design fixed 2026-09-19, before any 750M held-out score was read and before the
530M+750M analysis kernel ran. The registered rule (PROTOCOL_heldout.md) passes
when the lower 95% limit of the held-out margin Lambda is above one. The
protocol allowed the scope to shrink to the sizes that finished scoring, and the
paper needs to say what a pass or a fail at a reduced scope could mean. That
needs the rule's size and power at every scope it could take, with the four-task
battery and 25 recipe clusters it actually has.

Simulator. The compound-symmetric generator of research/kaggle/snap-r6-detect-power,
unchanged: r runs per configuration, each a latent draw over k traits with
correlation rho plus independent item noise in each half; cross-half products
over runs give T and U, and the recipe-clustered wild bootstrap-t and cluster
robust t intervals follow the shipped estimator code line for line. At four
traits with flat weights rho solves Lambda^2 = 1 + 3 rho.

Cells. Scope in {one size, two sizes, three sizes} (25, 50, 75 configurations,
always 25 recipe clusters), true Lambda in {1.00, 1.10, 1.20, 1.244, 1.316,
1.40, 1.50}, and one item-noise level per kernel copy set by NOISE_SD: 0.73 is
the margin battery's calibrated level, 1.45 the accuracy battery's, and 1.00
sits between them, because the held-out battery's own level is not known
before its scores are read. The pass rate at Lambda 1.00 is the rule's size and
the pass rate at 1.244 is its power against the shipped estimate. 4,000
replicates per cell, so a rate near 0.5 has Monte Carlo error 0.008.

What this is not. It says nothing about which value the held-out battery takes,
only how often the rule would pass if it took each one.
"""
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")

NOISE_SD = float(os.environ.get("K12_NOISE_SD", "__NOISE_SD__"))
SEED, REPS = 20260919, 4000
K_TRAITS, RUNS, RECIPES = 4, 3, 25
SCOPES = {"one_size": 1, "two_sizes": 2, "three_sizes": 3}
LAMBDAS = [1.00, 1.10, 1.20, 1.244, 1.316, 1.40, 1.50]


def simulate(sizes, lam, noise_sd, rng):
    k, r, recipes = K_TRAITS, RUNS, RECIPES
    rho = (lam ** 2 - 1) / (k - 1)
    truth = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    latent = rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    ea = rng.normal(size=latent.shape) * noise_sd
    eb = rng.normal(size=latent.shape) * noise_sd
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    da = a - a.mean(1, keepdims=True)
    db = b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


def wild(T, U, cluster, n_boot=4999, alpha=0.05, seed=0):
    """Wild cluster bootstrap-t with Rademacher weights, as in seednoise.inference."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=(n_boot, G))
    vb = v[:, inv]
    Tb = th * U + vb * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, vb.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = se_b > 0
    tb = ((th_b[ok] - th) / se_b[ok])
    tb = tb[np.isfinite(tb)]
    if tb.size < max(100, int(0.9 * n_boot)):
        return float("nan"), float("nan")
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    lo, hi = th - lo_q * se, th - hi_q * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


def cluster_t(T, U, cluster, alpha=0.05):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    e = np.bincount(inv, weights=np.asarray(T, float) - th * np.asarray(U, float), minlength=G)
    se = float(np.sqrt(G / (G - 1.0) * np.sum(e ** 2))) / sU
    crit = float(student_t.ppf(1 - alpha / 2, G - 1))
    lo, hi = th - crit * se, th + crit * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


METHODS = ("wild_recipe", "cluster_t_recipe")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "noise_sd": NOISE_SD,
          "traits": K_TRAITS, "runs": RUNS, "recipes": RECIPES, "cells": {}}
ci = 0
for scope, sizes in SCOPES.items():
    for lam in LAMBDAS:
        t1 = time.time()
        acc = {m: {"cov": 0, "pass": 0, "bad": 0, "w": [], "lo": []} for m in METHODS}
        truth = float("nan")
        for rep in range(REPS):
            rng = np.random.default_rng([SEED, ci, rep])
            T, U, recipe, truth = simulate(sizes, lam, NOISE_SD, rng)
            ivs = {"wild_recipe": wild(T, U, recipe, seed=rep),
                   "cluster_t_recipe": cluster_t(T, U, recipe)}
            for m, (lo, hi) in ivs.items():
                if np.isfinite(lo) and np.isfinite(hi):
                    acc[m]["cov"] += lo <= truth <= hi
                    # The registered rule is the lower limit above one, scored directly.
                    acc[m]["pass"] += lo > 1.0
                    acc[m]["w"].append(hi - lo)
                    acc[m]["lo"].append(lo)
                else:
                    acc[m]["bad"] += 1
        name = f"{scope}/lambda_{lam:.3f}"
        out = {"scope": scope, "sizes": sizes, "configurations": RECIPES * sizes,
               "true_lambda": truth, "rho": (lam ** 2 - 1) / (K_TRAITS - 1)}
        for m, a in acc.items():
            c = a["cov"] / REPS
            p = a["pass"] / REPS
            out[m] = {"coverage": c, "pass_rate": p,
                      "pass_mc_se": float(np.sqrt(p * (1 - p) / REPS)),
                      "undefined_or_unbounded": a["bad"] / REPS,
                      "median_width": float(np.median(a["w"])) if a["w"] else None,
                      "median_lower_limit": float(np.median(a["lo"])) if a["lo"] else None}
        report["cells"][name] = out
        ci += 1
        print(f"[{name}] {time.time() - t1:.0f}s " +
              json.dumps({m: {"pass": round(out[m]["pass_rate"], 4), "cov": round(out[m]["coverage"], 4)} for m in METHODS}),
              flush=True)

# One table per scope with the pass rate at every true Lambda, for the paper.
report["pass_table"] = {
    scope: {f"{lam:.3f}": report["cells"][f"{scope}/lambda_{lam:.3f}"]["wild_recipe"]["pass_rate"] for lam in LAMBDAS}
    for scope in SCOPES}
report["wall_seconds"] = time.time() - t0
(W / "k12_heldout_rule_power.json").write_text(json.dumps(report, indent=1))
print(json.dumps(report["pass_table"], indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
