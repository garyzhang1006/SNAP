"""R9 the quarter standard deviation gap, which is the only cell the run sweeps never reached.

Design fixed before running (2026-09-16, written 12:05 EDT). snap-r9-runs-b took the run sweep to 80 runs
per model and closed the one and the half standard deviation gaps, where four fifths arrives at 16 and 63
runs. The quarter gap stayed open, because the closed form puts it at 252 runs and the sweep stopped far
below that. A number that large deserves a simulation rather than a normal approximation alone, since the
plug-in correction carries its own noise and the closed form ignores that entirely. This run sweeps 100,
140, 180, 220, 252, 300 and 360 runs per model at gaps of zero and a quarter, on both populations, with
8,000 replicates per combination. It reports the smallest swept count whose corrected rule reaches four
fifths beside the closed-form prediction, so a reader can see whether estimating the correction costs
anything at that scale, and it carries the zero gap through so the size claim extends to 360 runs.
Seed 20260949 and a cell offset of twenty four hundred keep the draws distinct from both earlier sweeps.
"""
import json, platform, sys, time
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
from pathlib import Path
W = Path("/kaggle/working")

CELLS = [
 {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73},
 {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45},
]
GAPS = (0.0, 0.25)
RUNS_PER_MODEL = (100, 140, 180, 220, 252, 300, 360)
Z = 1.959963984540054
SEED, REPS = 20260949, 8000


def population(cell, rng):
    """One replicate of the shipped design, returning the cross-half estimate and the truth."""
    k, r = 10, 3
    recipes, sizes = 25, 5
    rho = cell["rho"]
    truth = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    n = recipes * sizes
    latent = rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    noise = float(cell["noise_sd"])
    a = latent + rng.normal(size=latent.shape) * noise
    b = latent + rng.normal(size=latent.shape) * noise
    w = np.full(k, 1.0 / k)
    da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    th = float(np.sum(T)) / float(np.sum(U))
    lam_hat = float(np.sqrt(th)) if th > 0 else float("nan")
    v_full = float(w @ truth @ w)
    v_diag = float((w * w) @ np.diag(truth))
    return lam_hat, np.sqrt(v_full / v_diag), v_full, v_diag


def oracle_runs_for(power, gap, z=Z):
    """Smallest n whose oracle rule reaches the target power, from the normal calculation."""
    from math import erf, sqrt
    def cdf(x):
        return 0.5 * (1.0 + erf(x / sqrt(2.0)))
    for n in range(1, 100001):
        # delta = gap * sqrt(v_full) and se_true = sqrt(2 v_full / n), so the ratio is gap sqrt(n/2).
        d = gap * np.sqrt(n / 2.0)
        if (1.0 - cdf(z - d)) + cdf(-z - d) >= power:
            return n
    return None


report = {"design": __doc__, "seed": SEED, "reps": REPS, "z": Z,
          "runs_swept": list(RUNS_PER_MODEL), "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    lam_hats = np.empty(REPS)
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 2400, rep])
        lam_hats[rep], lam_true, v_full, v_diag = population(cell, rng)
    ok = np.isfinite(lam_hats)
    out = {"name": cell["name"], "lambda_true": lam_true,
           "lambda_hat_mean": float(lam_hats[ok].mean()),
           "lambda_hat_sd": float(lam_hats[ok].std(ddof=1)),
           "undefined_estimates": float(np.mean(~ok)), "rules": {}}
    gen = np.random.default_rng([SEED, ci + 2500])
    for n in RUNS_PER_MODEL:
        se_true = np.sqrt(2.0 * v_full / n)
        se_indep = np.sqrt(2.0 * v_diag / n)
        for gap in GAPS:
            delta = gap * np.sqrt(v_full)
            observed = delta + gen.normal(size=REPS) * se_true
            rules = {"independence": np.full(REPS, se_indep),
                     "plug_in": lam_hats * se_indep,
                     "oracle": np.full(REPS, lam_true * se_indep)}
            cellout = {}
            for name, se in rules.items():
                fire = np.abs(observed) > Z * se
                fire = fire[np.isfinite(se)]
                p = float(np.mean(fire))
                cellout[name] = {"declare_rate": p,
                                 "mc_se": float(np.sqrt(p * (1 - p) / fire.size))}
            out["rules"][f"runs{n}/gap{gap}"] = cellout
            print(f"[{cell['name']}/runs{n}/gap{gap}] " +
                  json.dumps({k: round(v['declare_rate'], 4) for k, v in cellout.items()}), flush=True)
    need, closed = {}, {}
    for gap in GAPS:
        if gap == 0.0:
            continue
        hit = [n for n in RUNS_PER_MODEL
               if out["rules"][f"runs{n}/gap{gap}"]["plug_in"]["declare_rate"] >= 0.8]
        need[f"gap{gap}"] = min(hit) if hit else None
        closed[f"gap{gap}"] = oracle_runs_for(0.8, gap)
    out["runs_for_four_fifths_plug_in"] = need
    out["runs_for_four_fifths_closed_form"] = closed
    out["size_at_zero_gap"] = {f"runs{n}": out["rules"][f"runs{n}/gap0.0"]["independence"]["declare_rate"]
                               for n in RUNS_PER_MODEL}
    out["seconds"] = time.time() - t1
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}/need] swept {json.dumps(need)} closed {json.dumps(closed)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r9_runs_quarter.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
