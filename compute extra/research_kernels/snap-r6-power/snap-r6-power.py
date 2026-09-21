"""R6 how much data the accuracy conclusion would need, which the practice recommendation implies.

Design fixed before running (2026-09-16, written 00:35 EDT). The paper recommends paired replicate
scores and an aggregate seed standard deviation, and it reports that the full-battery accuracy interval
includes one at 0.993 to 1.157. A reader following that recommendation gets no guidance on scale,
because the paper never says how many configurations or runs it would take to resolve an effect the size
of the one we estimate. This run supplies that number. It simulates accuracy-like populations at the
fitted cell, whose true ratio sits near the observed 1.078, over 25, 50, 100 and 200 recipes at five
size bands each, with three runs per configuration and again with six, and it reports the share of
recipe-clustered intervals that exclude one at 1,000 replicates per cell. A margin-like cell at the
shipped design runs beside them as a check that the machinery reproduces the power we already observe.
Seed 20260939 and a cell offset of eleven hundred keep the draws distinct. The interesting number is the
smallest design that reaches four fifths, because that is what a group planning a replicate study would
budget against, and the paper can then state it in the same sentence as the recommendation.
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

CELLS = [{"name": f"accuracy_r{r}_runs{n}", "rho": 0.018, "noise_sd": 1.45, "recipes": r, "runs": n}
         for n in (3, 6) for r in (25, 50, 100, 200)]
CELLS.append({"name": "margin_r25_runs3", "rho": 0.061, "noise_sd": 0.73, "recipes": 25, "runs": 3})


def r6_simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    rho = cell.get("rho", 0.0)
    truth = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    latent = rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    noise = float(cell.get("noise_sd", 1.0))
    a = latent + rng.normal(size=latent.shape) * noise
    b = latent + rng.normal(size=latent.shape) * noise
    w = np.full(k, 1.0 / k)
    da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


SEED, REPS = 20260939, 1000
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    excl_above = excl_below = cov = bad = 0
    lam = []
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 1100, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        th = float(np.sum(T)) / float(np.sum(U))
        lam.append(float(np.sqrt(th)) if th >= 0 else np.nan)
        iv = wild_bootstrap_t(T, U, recipe, n_boot=999, seed=rep)
        lo, hi = float(iv.lo), float(iv.hi)
        if np.isfinite(lo) and np.isfinite(hi):
            excl_above += lo > 1.0
            excl_below += hi < 1.0
            cov += lo <= truth <= hi
        else:
            bad += 1
    v = np.asarray(lam, float); v = v[np.isfinite(v)]
    out = {"name": cell["name"], "recipes": cell["recipes"], "runs": cell["runs"], "truth": truth,
           "configurations": cell["recipes"] * 5,
           "share_excluding_one_above": excl_above / REPS,
           "share_excluding_one_below": excl_below / REPS,
           "coverage_of_truth": cov / REPS, "undefined": bad / REPS,
           "mean_estimate": float(v.mean()), "sd_estimate": float(v.std(ddof=1)),
           "seconds": time.time() - t1}
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}] {time.time() - t1:.0f}s power {out['share_excluding_one_above']:.3f} "
          f"cov {out['coverage_of_truth']:.3f}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_power.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
