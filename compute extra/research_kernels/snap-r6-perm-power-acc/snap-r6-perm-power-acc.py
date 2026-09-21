"""R6 whether the permutation bound on band sharing has any power at the accuracy battery's noise.

Design fixed before running (2026-09-16, written 18:52 EDT). snap-r6-share-power measured the permutation
test on a margin-like population and found it sound, since it rejects 0.044 of the time when the true band
share is zero and 0.992 of the time at a quarter. The paper reports the same bound on all four batteries,
including the two accuracy ones, and the accuracy scale carries item noise of 1.45 against the margin
scale's 0.73. That noise sits in the denominator of the plug-in share, so a test with ample power on
margins can be close to blind on accuracy, and the bound we quote there would then be an artefact of the
procedure. Nothing we have run separates those two possibilities.
This run measures the same test on an accuracy-like population, sweeping the true band share over 0, 0.02,
0.044, 0.10, 0.25 and 0.50 at 500 replicates and 999 permutations each, exactly as the margin run did, so
the two are directly comparable cell by cell. It reports the rejection rate at one in twenty and one in a
hundred, the bias and spread of the plug-in share, the coverage of the interval the paper quotes, and the
mean upper bound the test would return. A rejection rate near a twentieth at a true share of zero keeps
the accuracy bound honest about its size, and the power column says which shares that bound can actually
exclude. Seed 20260990 with a cell offset of three thousand four hundred keeps the draws distinct.
"""
import json, platform, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")

K, RUNS, RECIPES, SIZES = 10, 3, 25, 5
N_PER_BAND = RECIPES                      # configurations averaged inside one band
SHARES = (0.0, 0.02, 0.044, 0.10, 0.25, 0.50)
SEED, REPS, N_PERM = 20260990, 500, 999
RHO, NOISE = 0.018, 1.45
Z = 1.959963984540054
W_FLAT = np.full(K, 1.0 / K)
BAND = np.arange(RECIPES * SIZES) % SIZES
BANDS = np.unique(BAND)


def simulate(size_shared, rng):
    """The R6 generator with a band-shared run effect, returning both halves of run deviations."""
    truth = (1 - RHO) * np.eye(K) + RHO * np.ones((K, K))
    n = RECIPES * SIZES
    latent = np.sqrt(1 - size_shared) * rng.multivariate_normal(np.zeros(K), truth, size=(n, RUNS))
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


report = {"design": __doc__, "seed": SEED, "rho": RHO, "noise_sd": NOISE, "reps": REPS, "n_perm": N_PERM,
          "configs_per_band": N_PER_BAND, "shares": list(SHARES), "cells": {}}
for si, share in enumerate(SHARES):
    t1 = time.time()
    tails, qhats, ses, covered, defined = [], [], [], 0, 0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, si + 3400, rep])
        dA, dB = simulate(share, rng)
        obs = band_statistic(dA, dB)
        total = weighted_cross(dA, dB)
        prng = np.random.default_rng([SEED, si + 3500, rep])
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
    report["cells"][f"share{share}"] = out
    print(f"[share {share}] {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_perm_power_acc.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
