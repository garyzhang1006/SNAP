"""R6 whether the permutation null stays exact when the population stops being well behaved.

Design fixed before running (2026-09-16, written 15:35 EDT). The paper calls the within-configuration run
permutation an exact null, and it is exact under exchangeability of a configuration's runs, which is a
weaker assumption than normality. snap-r6-share-power confirmed the size is right at 0.044 against a
nominal one in twenty, and it confirmed it on a normal population with identical recipes. Exchangeability
should survive heavy tails and unequal recipe variances, and should is a word this paper tries not to
lean on.
This run tests it. It holds the true band share at zero and varies the population instead, drawing the
latent effects from a multivariate t with 5 and with 3 degrees of freedom, giving the 25 recipes variance
scales spread over a sixteen-fold range, and combining the two. It reports the rejection rate at one in
twenty and at one in a hundred over 500 replicates and 999 permutations per cell. A size that stays near
nominal in every cell earns the word exact. A size that climbs would mean the bound the limitation
section quotes is measured against a null that is itself wrong. Seed 20260969 keeps the draws distinct.
"""
import json, platform, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")

K, RUNS, RECIPES, SIZES = 10, 3, 25, 5
N_PER_BAND = RECIPES                      # configurations averaged inside one band
SHARES = (0.0,)
SEED, REPS, N_PERM = 20260969, 500, 999
RHO, NOISE = 0.061, 0.73
Z = 1.959963984540054
W_FLAT = np.full(K, 1.0 / K)
BAND = np.arange(RECIPES * SIZES) % SIZES
BANDS = np.unique(BAND)


# Each population breaks one assumption the exact null is supposed to survive.
_SPREAD16 = np.linspace(0.25, 4.0, RECIPES)
_SPREAD16 = _SPREAD16 / _SPREAD16.mean()
POPULATIONS = [
 {"name": "normal_equal", "student_df": None, "spread": None},
 {"name": "student_df_05", "student_df": 5, "spread": None},
 {"name": "student_df_03", "student_df": 3, "spread": None},
 {"name": "recipe_spread_16x", "student_df": None, "spread": _SPREAD16},
 {"name": "student_05_spread_16x", "student_df": 5, "spread": _SPREAD16},
]
RECIPE_OF = np.repeat(np.arange(RECIPES), SIZES)


def simulate(size_shared, rng, pop=None):
    """The R6 generator with a band-shared run effect, returning both halves of run deviations."""
    pop = pop or POPULATIONS[0]
    truth = (1 - RHO) * np.eye(K) + RHO * np.ones((K, K))
    n = RECIPES * SIZES
    latent = np.sqrt(1 - size_shared) * rng.multivariate_normal(np.zeros(K), truth, size=(n, RUNS))
    df = pop.get("student_df")
    if df:
        latent *= np.sqrt((df - 2) / rng.chisquare(df, size=(n, RUNS, 1)))
    if pop.get("spread") is not None:
        latent *= np.sqrt(np.asarray(pop["spread"], float))[RECIPE_OF][:, None, None]
    if size_shared > 0:
        # Configuration c is recipe c // sizes and band c % sizes, so a band effect tiles.
        latent += np.sqrt(size_shared) * np.tile(
            rng.multivariate_normal(np.zeros(K), truth, size=(SIZES, RUNS)), (RECIPES, 1, 1))
    a = latent + rng.normal(size=latent.shape) * NOISE
    b = latent + rng.normal(size=latent.shape) * NOISE
    return a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)


def weighted_cross(dA, dB):
    """Weighted cross-half covariance of a stack of deviation arrays, summed over its first axis."""
    cross = np.einsum("crj,crk->cjk", dA, dB) / (RUNS - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", W_FLAT, cov, W_FLAT)
    return float(T.sum())


def band_statistic(dA, dB, perm=None):
    """Weighted cross-half covariance of the band means, summed over bands."""
    a, b = (dA, dB) if perm is None else (np.take_along_axis(dA, perm[:, :, None], axis=1),
                                          np.take_along_axis(dB, perm[:, :, None], axis=1))
    mA = np.stack([a[BAND == z].mean(axis=0) for z in BANDS])
    mB = np.stack([b[BAND == z].mean(axis=0) for z in BANDS])
    return weighted_cross(mA, mB)


report = {"design": __doc__, "seed": SEED, "reps": REPS, "n_perm": N_PERM,
          "configs_per_band": N_PER_BAND, "populations": [p["name"] for p in POPULATIONS], "cells": {}}
for si, pop_cell in enumerate(POPULATIONS):
    share = 0.0
    t1 = time.time()
    tails, qhats, ses, covered, defined = [], [], [], 0, 0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, si + 2800, rep])
        dA, dB = simulate(share, rng, pop_cell)
        obs = band_statistic(dA, dB)
        total = weighted_cross(dA, dB)
        prng = np.random.default_rng([SEED, si + 2900, rep])
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            perm = np.argsort(prng.random(dA.shape[:2]), axis=1)
            null[p] = band_statistic(dA, dB, perm)
        tail = float(np.mean(null >= obs))
        # Averaging n independent configurations divides a covariance by n and the band total sums n
        # of them, so an added share q moves the statistic by total times (1/n - 1/n^2).
        slope = total * (1.0 / N_PER_BAND - 1.0 / N_PER_BAND ** 2)
        if slope <= 0:
            tails.append(tail)
            continue
        defined += 1
        q = (obs - float(null.mean())) / slope
        se = float(null.std(ddof=1)) / slope
        tails.append(tail)
        qhats.append(q)
        ses.append(se)
        covered += (q - Z * se) <= share <= (q + Z * se)
    tails = np.asarray(tails)
    qh, sea = np.asarray(qhats), np.asarray(ses)
    out = {"share": share, "reps": REPS, "defined_slope": defined,
           "reject_at_05": float(np.mean(tails <= 0.05)),
           "reject_at_01": float(np.mean(tails <= 0.01)),
           "median_tail": float(np.median(tails)),
           "qhat_mean": float(qh.mean()) if qh.size else None,
           "qhat_sd": float(qh.std(ddof=1)) if qh.size > 1 else None,
           "qhat_bias": float(qh.mean() - share) if qh.size else None,
           "mean_reported_se": float(sea.mean()) if sea.size else None,
           "interval_coverage": covered / defined if defined else None,
           "upper_bound_mean": float((qh + Z * sea).mean()) if qh.size else None,
           "seconds": time.time() - t1}
    out["population"] = pop_cell["name"]
    report["cells"][pop_cell["name"]] = out
    print(f"[{pop_cell['name']}] {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_perm_exact.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
