"""R6 how much cross-half item-noise correlation would be needed to manufacture the observed result.

Design fixed before running (2026-09-15, written 23:56 EDT). The whole estimator rests on one
assumption, which is that the item-sampling noise on half A is independent of the noise on half B given
the run. The paper checks the one concrete threat to that assumption, which is BoolQ's shared passages,
and it reports a passage-aware split. It never says what a violation would cost, so a reviewer has no way
to judge how close to the edge the design sits. This run answers the question in the form the reviewer
would ask it. It simulates a population whose true ratio is exactly one, with the fitted noise scale of
0.73, and sweeps a correlation between the two halves' item noise from zero to 0.2 with 2,000 replicates
at each value. Each cell reports the mean estimate, the share of recipe-clustered intervals that exclude
one, and the implied bias, so the curve says how much correlation it takes to move a null population to
the observed 1.244. Seed 20260937 and a cell offset of one thousand keep the draws distinct. A
correlation that has to exceed a tenth to explain the result is a different finding from one that only
needs a hundredth, and the paper should quote whichever number this returns.
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

from seednoise.inference import wild_bootstrap_t  # noqa: E402

CELLS = [{"name": f"ec_{e}", "rho": 0.0, "noise_sd": 0.73, "cross_half_error_correlation": e}
         for e in (0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20)]


def r6_simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    rho = cell.get("rho", 0.0)
    truth = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    latent = rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    noise = float(cell.get("noise_sd", 1.0))
    ec = float(cell.get("cross_half_error_correlation", 0.0))
    ea = rng.normal(size=latent.shape) * noise
    eb = ec * ea + np.sqrt(1 - ec ** 2) * rng.normal(size=latent.shape) * noise
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


SEED, REPS, OBSERVED = 20260937, 2000, 1.2439
report = {"design": __doc__, "seed": SEED, "reps": REPS, "observed_margin_estimate": OBSERVED,
          "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    lam, excl, cov_one, bad = [], 0, 0, 0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 1000, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        th = float(np.sum(T)) / float(np.sum(U))
        lam.append(float(np.sqrt(th)) if th >= 0 else np.nan)
        iv = wild_bootstrap_t(T, U, recipe, n_boot=999, seed=rep)
        lo, hi = float(iv.lo), float(iv.hi)
        if np.isfinite(lo) and np.isfinite(hi):
            excl += lo > 1.0 or hi < 1.0
            cov_one += lo <= 1.0 <= hi
        else:
            bad += 1
    v = np.asarray(lam, float); v = v[np.isfinite(v)]
    out = {"name": cell["name"], "cross_half_error_correlation": cell["cross_half_error_correlation"],
           "true_lambda": truth, "mean_estimate": float(v.mean()),
           "sd_estimate": float(v.std(ddof=1)), "median_estimate": float(np.median(v)),
           "share_excluding_one": excl / REPS, "coverage_of_one": cov_one / REPS,
           "undefined": bad / REPS,
           "mean_gap_to_observed": float(v.mean()) - OBSERVED}
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}] {time.time() - t1:.0f}s mean {out['mean_estimate']:.4f} "
          f"excl {out['share_excluding_one']:.4f}", flush=True)

xs = np.array([c["cross_half_error_correlation"] for c in report["cells"].values()], float)
ys = np.array([c["mean_estimate"] for c in report["cells"].values()], float)
if ys.max() >= OBSERVED >= ys.min():
    report["correlation_matching_observed"] = float(np.interp(OBSERVED, ys, xs))
else:
    report["correlation_matching_observed"] = None
    report["note"] = "the observed estimate lies outside the simulated range of mean estimates"
print(f"[solve] {report['correlation_matching_observed']}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_crosshalf.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
