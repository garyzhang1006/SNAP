"""R9 how many replicate runs a comparison needs, and what extra runs cannot fix.

Design fixed before running (2026-09-16, written 00:58 EDT). snap-r9-decision showed that a rule
assuming benchmark independence declares a margin difference in 0.113 of comparisons whose true gap is
zero, and that multiplying its standard error by an estimated ratio returns that to 0.051. The natural
follow-up from a practitioner is how many runs per model they need, and whether buying more runs also
repairs the miscalibration. The second half of that question has an answer worth stating plainly,
because the true standard error and the independence standard error both fall with the square root of
the run count, so their ratio doesn't move and extra runs leave the size error exactly where it was.
This run measures both halves on the same simulator. It sweeps one to ten runs per model at true gaps of
zero, a quarter, a half and one aggregate standard deviation, on a margin-like and an accuracy-like
population, with 4,000 replicates per combination and the same three rules. It reports the declare rate
for each rule at each run count, which gives both the size at a zero gap and the power elsewhere, and it
names the smallest run count whose corrected rule reaches four fifths. Seed 20260944 and a cell offset
of fourteen hundred keep the draws distinct from the first decision run.
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
GAPS = (0.0, 0.25, 0.5, 1.0)          # true gap in units of the true aggregate standard deviation
RUNS_PER_MODEL = tuple(range(1, 11))
Z = 1.959963984540054
SEED, REPS = 20260944, 4000


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
        rng = np.random.default_rng([SEED, ci + 1400, rep])
        lam_hats[rep], lam_true, v_full, v_diag = population(cell, rng)
    ok = np.isfinite(lam_hats)
    out = {"name": cell["name"], "lambda_true": lam_true,
           "lambda_hat_mean": float(lam_hats[ok].mean()), "lambda_hat_sd": float(lam_hats[ok].std(ddof=1)),
           "undefined_estimates": float(np.mean(~ok)), "rules": {}}
    gen = np.random.default_rng([SEED, ci + 1500])
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
    need = {}
    for gap in GAPS:
        if gap == 0.0:
            continue
        hit = [n for n in RUNS_PER_MODEL
               if out["rules"][f"runs{n}/gap{gap}"]["plug_in"]["declare_rate"] >= 0.8]
        need[f"gap{gap}"] = min(hit) if hit else None
    out["runs_for_four_fifths_plug_in"] = need
    out["seconds"] = time.time() - t1
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}/need] {json.dumps(need)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r9_runs.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
