"""R6 whether the permutation test that bounds band sharing can detect band sharing at all.

Design fixed before running (2026-09-16, written 12:20 EDT). The paper's answer to its own worst
limitation is a bound. Recipe clustering breaks if a run effect follows the size band instead of the
recipe, which takes simulated coverage to 0.810 at a quarter of latent variance, and a permutation test
that aligns runs by batch slot bounds the observed band share at 0.044 with a standard error of 0.018.
That bound is only worth the paper it sits in if the test can see sharing when sharing is there. A test
with no power returns a small share whatever the truth, and the bound would then be an artefact of the
procedure rather than a fact about these runs. Nothing we have run so far measures that.
This run measures it directly on simulated data whose band share we set. It sweeps shares of 0, 0.02,
0.044, 0.10, 0.25 and 0.50 on a margin-like population, and for each of 500 replicates per share it forms
the same weighted cross-half covariance of the band means, builds the same within-configuration run
permutation null at 999 draws, and reads off both the one-sided tail and the plug-in share estimate. It
reports how often the test rejects independence at one in twenty, and how close the estimated share lands
to the truth, together with the coverage of the interval the paper actually quotes. A test that rejects
almost always at a quarter, and whose estimate tracks the truth at 0.044, turns the bound into a
measurement. A test that misses a quarter would mean the bound says nothing, and we would have to say so.
Seed 20260951 with a cell offset of twenty eight hundred keeps the draws distinct.
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
SEED, REPS, N_PERM = 20260951, 500, 999
RHO, NOISE = 0.061, 0.73
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


report = {"design": __doc__, "seed": SEED, "reps": REPS, "n_perm": N_PERM,
          "configs_per_band": N_PER_BAND, "shares": list(SHARES), "cells": {}}
for si, share in enumerate(SHARES):
    t1 = time.time()
    tails, qhats, ses, covered, defined = [], [], [], 0, 0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, si + 2800, rep])
        dA, dB = simulate(share, rng)
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
    report["cells"][f"share{share}"] = out
    print(f"[share {share}] {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_share_power.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
