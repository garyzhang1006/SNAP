"""R8 known-truth check of the log-scale prediction comparison.

Design fixed before running (2026-09-15, 18:05 EDT), as a companion to snap-r8-paired-log.
The observed target in Table tab:prediction is the noisy three-run aggregate SD of each held-out fold.
This kernel simulates populations with known seed covariance and asks whether the fold comparison
ranks models by their error against the truth or by their error against the noisy target.
1. Structures are those of snap-r7-proxy-null for each phenotype. Independence uses the observed pooled
   seed SDs, equicorrelated uses the single correlation that reproduces the observed inflation, and
   matched uses the nearest positive semidefinite matrix to the observed seed covariance. Item SDs come
   from the observed item-noise variances, with 125 configurations, three runs, 25 recipes, five sizes.
2. 300 replicates per structure and phenotype, seeds 20260915 + 7919 i, five recipe folds with seed i.
   Models P0, P1, P1g, P2, P3, and P2R as in snap-r8-paired-log.
3. For margins, the true aggregate SD is sqrt(sum Sigma_E)/K from the generating matrix. For accuracy
   the generator acts on margins, so the truth is the mean of sigma_e(accuracy) over the 300
   replicates of that structure, which averages 37,500 simulated configurations.
4. Per model, record mean squared log error against the observed fold target and against the truth,
   the share of replicates where each model is lowest under each target, and the paired contrasts of
   snap-r8-paired-log under both targets with Monte Carlo standard errors. Also record the mean squared
   log error of the observed target itself against the truth.
Simulated populations share one covariance across recipes, so this check omits recipe heterogeneity.
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

from seednoise.baselines import observed_sigma_agg, predict_sigma_agg  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import correlation, estimate, nearest_psd, phenotypic_correlation, sigma_e  # noqa: E402
from seednoise.nulls import NOMINAL_ITEMS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import SimSpec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
N_REP = 300
MODELS = ("P0", "P1", "P1g", "P2", "P3", "P2R")
CONTRASTS = [("P1", "P0"), ("P3", "P0"), ("P1g", "P0"), ("P2R", "P0"), ("P1", "P3"), ("P1g", "P1"), ("P2R", "P1"), ("P2R", "P3")]
OFF = ~np.eye(pop.K, dtype=bool)


def predict(train, test, name, m):
    if m != "P2R":
        return predict_sigma_agg(train, test, name, m)
    RE = correlation(sigma_e(train, name)); RPtr = phenotypic_correlation(train, name)
    R = phenotypic_correlation(test, name) * float(np.nanmean(RE[OFF]) / np.nanmean(RPtr[OFF]))
    np.fill_diagonal(R, 1.0); R = np.where(np.isfinite(R), R, 0.0)
    sd = np.sqrt(np.clip(np.diag(sigma_e(test, name)), 0.0, None))
    v = float((np.outer(sd, sd) * R).sum()) / test.K ** 2
    return float(np.sqrt(v)) if v > 0 else float("nan")


def fold_rows(sim, name, seed):
    rec = np.unique(sim.recipe); rng = np.random.default_rng(seed)
    rows = []
    for held in np.array_split(rng.permutation(rec), 5):
        test = sim.subset_clusters(held); train = sim.subset_clusters(np.setdiff1d(rec, held))
        rows.append({"obs": observed_sigma_agg(test, name), **{m: predict(train, test, name, m) for m in MODELS}})
    return rows


def le(a, b):
    return float((np.log(a) - np.log(b)) ** 2) if (np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0) else float("nan")


def summarise(reps, truth):
    per = {"observed": {m: [] for m in MODELS}, "truth": {m: [] for m in MODELS}}; target_err = []
    for rows in reps:
        for m in MODELS:
            per["observed"][m].append(np.nanmean([le(r[m], r["obs"]) for r in rows]))
            per["truth"][m].append(np.nanmean([le(r[m], truth) for r in rows]))
        target_err.append(np.nanmean([le(r["obs"], truth) for r in rows]))
    out = {"truth_sigma_agg": truth, "target_mse_vs_truth": float(np.nanmean(target_err))}
    for tgt in ("observed", "truth"):
        A = {m: np.array(per[tgt][m]) for m in MODELS}
        low = [min(MODELS, key=lambda m: A[m][i] if np.isfinite(A[m][i]) else np.inf) for i in range(len(reps))]
        out[tgt] = {"mse_mean": {m: float(np.nanmean(A[m])) for m in MODELS},
                    "share_lowest": {m: float(np.mean(np.array(low) == m)) for m in MODELS},
                    "contrasts": {f"{a}-{b}": {"mean": float(np.nanmean(A[a] - A[b])),
                                               "mc_se": float(np.nanstd(A[a] - A[b], ddof=1) / np.sqrt(np.isfinite(A[a] - A[b]).sum())),
                                               "share_below_zero": float(np.nanmean((A[a] - A[b]) < 0))} for a, b in CONTRASTS}}
    return out


n_items = tuple(int(n) for n in np.asarray(pop.n_items).tolist()) if pop.n_items is not None else tuple([NOMINAL_ITEMS] * pop.K)
n_half = np.maximum(np.asarray(n_items, float) / 2.0, 1.0)
report = {"design": __doc__, "n_rep": N_REP, "cells": {}}
for name in ("margin", "accuracy"):
    S = sigma_e(pop, name)
    sd = np.sqrt(np.clip(np.diag(S), 1e-9, None))
    Rm = S / np.outer(sd, sd); np.fill_diagonal(Rm, 1.0); Rm = np.where(np.isfinite(Rm), Rm, 0.0)
    matched, clipped = nearest_psd(np.outer(sd, sd) * Rm, floor=1e-12)
    lam = float(estimate(pop, name, check=False).lambda_hat)
    off = np.outer(sd, sd); np.fill_diagonal(off, 0.0)
    r = (lam ** 2 - 1) * np.sum(sd ** 2) / off.sum()
    equi = np.outer(sd, sd) * ((1 - r) * np.eye(pop.K) + r)
    item_sd = tuple(np.sqrt(np.clip(variance_components(pop, name).noise2, 1e-12, None) * n_half).tolist())
    for label, target in (("independence", np.diag(sd ** 2)), ("equicorrelated", equi), ("matched", matched)):
        t1 = time.time(); reps = []; Sacc = []
        for i in range(N_REP):
            spec = SimSpec(n_config=pop.N, n_runs=pop.R, traits=tuple(pop.traits), n_items=n_items, item_sd=item_sd,
                           n_recipes=25, n_sizes=5, seed=20260915 + 7919 * i)
            spec.sigma_e = target
            sim = simulate(spec)
            reps.append(fold_rows(sim, name, i))
            if name == "accuracy":
                Sacc.append(sigma_e(sim, name))
        if name == "margin":
            truth = float(np.sqrt(target.sum()) / pop.K)
        else:
            Sbar = np.mean(Sacc, axis=0); truth = float(np.sqrt(max(Sbar.sum(), 1e-300)) / pop.K)
        cell = summarise(reps, truth)
        cell["equicorrelation"] = float(r) if label == "equicorrelated" else None
        report["cells"][f"{name}/{label}"] = cell
        print(f"[{name}/{label}] {time.time() - t1:.0f}s truth {truth:.3e} target_mse {cell['target_mse_vs_truth']:.4f} "
              f"obs {json.dumps({m: round(v, 4) for m, v in cell['observed']['mse_mean'].items()})} "
              f"truth {json.dumps({m: round(v, 4) for m, v in cell['truth']['mse_mean'].items()})}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r8_known_truth.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
