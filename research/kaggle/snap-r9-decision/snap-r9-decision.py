"""R9 whether correcting a decision rule for covariance helps once the correction is estimated.

Design fixed before running (2026-09-16, written 00:45 EDT). The paper reports a flip probability under
the fitted model and a census of 1,500 observed gaps, and it recommends paired replicate scores. It
never asks the question a practitioner actually faces, which is whether applying our correction to their
own decision rule makes that rule better or worse once the correction carries the noise of a three-run
design. A practitioner who measures per-benchmark run variances and assumes independence uses a standard
error that is too small by the factor Lambda, so their nominal five percent test rejects more often than
five percent. Multiplying by an estimated Lambda repairs that in expectation, and it also injects the
estimate's own sampling error into every decision. This run measures both effects together. Each
replicate simulates the shipped design of 125 configurations with three runs, estimates Lambda from it
with the cross-half estimator, and then applies three rules to a fresh comparison of two model averages,
which are the uncorrected independence rule, the plug-in rule using the estimate, and an oracle rule
using the true value. It reports the false declaration rate at a true gap of zero and the power at gaps
of half and one aggregate standard deviation, for one run and for three runs per model, on a margin-like
and an accuracy-like population at 4,000 replicates each. Seed 20260940 keeps the draws distinct. A
plug-in rule that lands near five percent is a usable recommendation, and one that overshoots because of
its own noise is a finding that the correction needs more runs than this design gives.
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

CELLS = [
 {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73},
 {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45},
]
GAPS = (0.0, 0.5, 1.0)          # true gap in units of the true aggregate standard deviation
RUNS_PER_MODEL = (1, 3)
Z = 1.959963984540054
SEED, REPS = 20260940, 4000


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


report = {"design": __doc__, "seed": SEED, "reps": REPS, "z": Z, "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    lam_hats = np.empty(REPS)
    # One estimate per replicate, reused across gaps and run counts so the comparison is paired.
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 1200, rep])
        lam_hats[rep], lam_true, v_full, v_diag = population(cell, rng)
    ok = np.isfinite(lam_hats)
    out = {"name": cell["name"], "lambda_true": lam_true,
           "lambda_hat_mean": float(lam_hats[ok].mean()), "lambda_hat_sd": float(lam_hats[ok].std(ddof=1)),
           "undefined_estimates": float(np.mean(~ok)), "rules": {}}
    gen = np.random.default_rng([SEED, ci + 1300])
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
    out["seconds"] = time.time() - t1
    report["cells"][cell["name"]] = out

report["wall_seconds"] = time.time() - t0
(W / "r9_decision.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
