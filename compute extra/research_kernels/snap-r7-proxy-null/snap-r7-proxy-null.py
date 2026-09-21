"""R7 CPU part 2: what the competence adjustments return when the truth is known.

Design fixed after reading r7_proxy_audit.json and before running this kernel
(2026-09-15, 17:20 EDT). The audit found that the regularised proxy moves margin
inflation below one, and a proxy built from the same seed deviations can remove
shared covariance by construction, so no adjusted value is interpretable without
this calibration. Populations are simulated as null N4 simulates them, with the
observed item counts and item noise, 125 configurations, 3 runs, 25 recipes and
5 sizes, under three seed covariances per phenotype.
  independence   diagonal, observed pooled seed variances (floor 1e-9), true Lambda 1
  equicorrelated one correlation r chosen so that the population Lambda equals the observed
                 unadjusted estimate for those variances
  matched        nearest PSD matrix to the observed estimate, the N4 target
Each replicate reports Lambda before adjustment, after the shipped adjustment, after the
in-sample regularised adjustment, and after the 5-fold recipe cross-fitted regularised
adjustment (alpha 0.5), all as in snap-r7-proxy-audit. 300 replicates per cell.
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

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import deviations, estimate, nearest_psd, sigma_e  # noqa: E402
from seednoise.mediation import competence, fit_mediation, residualise  # noqa: E402
from seednoise.nulls import NOMINAL_ITEMS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import SimSpec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
N_REP, ALPHA, FOLDS = 300, 0.5, 5


def proxy(d, sd):
    return competence(d, sd)


def slopes(dA, dB, xA, xB):
    b = np.empty(dA.shape[2])
    for j in range(dA.shape[2]):
        c = [np.linalg.lstsq(xo[:, :, j].ravel()[:, None], y[:, :, j].ravel(), rcond=None)[0][0]
             for y, xo in ((dA, xB), (dB, xA))]
        b[j] = np.mean(c)
    return b


def reg_sd(p, name, alpha):
    v = np.diag(sigma_e(p, name)).copy()
    if alpha > 0:
        v = (1 - alpha) * np.clip(v, 0, None) + alpha * np.median(v[v > 0])
    return np.sqrt(np.clip(v, 1e-12, None))


def lam(p, name):
    return float(estimate(p, name, check=False).lambda_hat)


def adjusted(p, name, fold_seed):
    ph = p.pheno(name)
    dA, dB = deviations(ph.A), deviations(ph.B)
    out = {"before": lam(p, name)}
    fit = fit_mediation(p, name, terms=("x",))
    res = residualise(p, name, fit)
    out["shipped"] = lam(res, list(res.phenotypes)[-1])
    sd = reg_sd(p, name, ALPHA)
    b = slopes(dA, dB, proxy(dA, sd), proxy(dB, sd))
    out["insample_regularised"] = lam(p.with_phenotype("is", dA - b * proxy(dA, sd), dB - b * proxy(dB, sd)), "is")
    recipes = np.unique(p.recipe)
    perm = np.random.default_rng(fold_seed).permutation(recipes)
    fold_of = {int(r): i % FOLDS for i, r in enumerate(perm)}
    oA, oB = np.full_like(dA, np.nan), np.full_like(dB, np.nan)
    for f in range(FOLDS):
        test = np.array([fold_of[int(r)] == f for r in p.recipe])
        tr = p.subset(np.flatnonzero(~test))
        sd_f = reg_sd(tr, name, ALPHA)
        b_f = slopes(dA[~test], dB[~test], proxy(dA[~test], sd_f), proxy(dB[~test], sd_f))
        oA[test] = dA[test] - b_f * proxy(dA[test], sd_f); oB[test] = dB[test] - b_f * proxy(dB[test], sd_f)
    out["crossfit_regularised"] = lam(p.with_phenotype("cf", oA, oB), "cf")
    return out


def stats(v):
    v = np.asarray(v, float); f = v[np.isfinite(v)]
    return {"n_finite": int(f.size), "mean": float(f.mean()), "sd": float(f.std(ddof=1)),
            "p05": float(np.percentile(f, 5)), "median": float(np.median(f)), "p95": float(np.percentile(f, 95))}


report = {"design": __doc__, "n_rep": N_REP, "alpha": ALPHA, "folds": FOLDS, "observed": {}, "cells": {}}
n_items = tuple(int(n) for n in np.asarray(pop.n_items).tolist()) if pop.n_items is not None else tuple([NOMINAL_ITEMS] * pop.K)
n_half = np.maximum(np.asarray(n_items, float) / 2.0, 1.0)
for name in ("margin", "accuracy"):
    report["observed"][name] = adjusted(pop, name, 0)
    S = sigma_e(pop, name)
    sd = np.sqrt(np.clip(np.diag(S), 1e-9, None))
    Rm = S / np.outer(sd, sd); np.fill_diagonal(Rm, 1.0); Rm = np.where(np.isfinite(Rm), Rm, 0.0)
    matched, clipped = nearest_psd(np.outer(sd, sd) * Rm, floor=1e-12)
    lam_obs = report["observed"][name]["before"]
    off = np.outer(sd, sd); np.fill_diagonal(off, 0.0)
    r = (lam_obs ** 2 - 1) * np.sum(sd ** 2) / off.sum()
    equi = np.outer(sd, sd) * ((1 - r) * np.eye(pop.K) + r)
    comp = variance_components(pop, name)
    item_sd = tuple(np.sqrt(np.clip(comp.noise2, 1e-12, None) * n_half).tolist())
    print(f"[{name}] observed {json.dumps(report['observed'][name])} equi r={r:.4f} psd clipped {clipped:.3g}", flush=True)
    for label, target in (("independence", np.diag(sd ** 2)), ("equicorrelated", equi), ("matched", matched)):
        t1 = time.time(); rows = []
        for i in range(N_REP):
            spec = SimSpec(n_config=pop.N, n_runs=pop.R, traits=tuple(pop.traits), n_items=n_items, item_sd=item_sd,
                           n_recipes=25, n_sizes=5, seed=20260915 + 7919 * i)
            spec.sigma_e = target
            rows.append(adjusted(simulate(spec), name, i))
        cell = {k: stats([row[k] for row in rows]) for k in rows[0]}
        cell["r"] = float(r) if label == "equicorrelated" else None
        report["cells"][f"{name}/{label}"] = cell
        print(f"[{name}/{label}] {time.time() - t1:.0f}s " + json.dumps({k: (round(v['mean'], 4), round(v['sd'], 4)) for k, v in cell.items() if isinstance(v, dict)}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r7_proxy_null.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
