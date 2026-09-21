"""R6 what an unequal number of seeds per configuration does to the interval.

Design fixed before running (2026-09-16, written 18:45 EDT). Every run sweep so far has given each
configuration the same number of seeds, either the shipped three or a uniform two, four or ten, and the
estimator's divisor was the same everywhere. The release is not like that. Some configurations lose a seed
because a branch stops early or a checkpoint is missing at the shared step, and a practitioner rebuilding
this design will find the same thing on their own runs. The sums that form the estimate then mix
configurations measured with one degree of freedom and configurations measured with two, and nothing we
have run says whether that mixture is harmless or whether it quietly breaks the interval.
This run measures it. It draws a run count per configuration rather than fixing one, and it sweeps the
share of configurations cut to two seeds from none through a tenth, a quarter, a half and all of them, on
the margin-like population at 4,000 replicates per cell. Two of the cells make the loss lumpy instead of
random, cutting whole recipes so the shortfall lines up with the clustering variable, which is the case a
reviewer would worry about because the cluster bootstrap resamples exactly those units. One cell runs the
quarter share on the accuracy-like population, where the interval already sits closest to its edge, and
one mixes two, three and four seeds at once so no single divisor is right anywhere. It reports coverage,
the exclusion rate at the true 1.2446, the median width and the undefined rate for the recipe-clustered
and band-clustered intervals, so the cost shows up as either a coverage loss or a width the paper should
quote. Seed 20260989 keeps the draws distinct.
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

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

CELLS = [
 {"name": "share0.00", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.00},
 {"name": "share0.10", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.10},
 {"name": "share0.25", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.25},
 {"name": "share0.50", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.50},
 {"name": "share1.00", "rho": 0.061, "noise_sd": 0.73, "short_share": 1.00},
 {"name": "lumpy0.25", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.25, "lumpy": True},
 {"name": "lumpy0.50", "rho": 0.061, "noise_sd": 0.73, "short_share": 0.50, "lumpy": True},
 {"name": "mixed234", "rho": 0.061, "noise_sd": 0.73, "run_mix": [2, 3, 4]},
 {"name": "acc_share0.25", "rho": 0.018, "noise_sd": 1.45, "short_share": 0.25},
 {"name": "acc_lumpy0.50", "rho": 0.018, "noise_sd": 1.45, "short_share": 0.50, "lumpy": True},
]
def run_counts_for(cell, n, recipes, sizes, rng):
    """Seeds available per configuration, either a random shortfall, a recipe-wide one, or a mix."""
    mix = cell.get("run_mix")
    if mix:
        return rng.choice(np.asarray(mix, int), size=n)
    full, short = cell.get("runs", 3), cell.get("short_runs", 2)
    share = float(cell.get("short_share", 0.0))
    counts = np.full(n, full, int)
    if share <= 0:
        return counts
    if cell.get("lumpy"):
        # A whole recipe loses a seed, so the shortfall lines up with the cluster the bootstrap resamples.
        hit = rng.random(recipes) < share
        counts[np.repeat(hit, sizes)] = short
    else:
        counts[rng.random(n) < share] = short
    return counts


def r6_simulate(cell, rng):
    k = cell.get("benchmarks", 10)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    counts = run_counts_for(cell, recipes * sizes, recipes, sizes, rng)
    r = int(counts.max())
    rho = cell.get("rho", 0.0)
    scale = np.asarray(cell.get("trait_scales", [1.0] * k), float)
    truth = ((1 - rho) * np.eye(k) + rho * np.ones((k, k))) * np.outer(scale, scale)
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    shared = cell.get("recipe_shared", 0.0)
    size_shared = cell.get("size_shared", 0.0)
    latent = np.sqrt(1 - shared - size_shared) * rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    if shared > 0:
        latent += np.sqrt(shared) * np.repeat(rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
    if size_shared > 0:
        # Configuration c is recipe c // sizes and band c % sizes, so the band effect tiles.
        latent += np.sqrt(size_shared) * np.tile(rng.multivariate_normal(np.zeros(k), truth, size=(sizes, r)), (recipes, 1, 1))
    df = cell.get("student_df")
    if df:
        latent *= np.sqrt((df - 2) / rng.chisquare(df, size=(n, r, 1)))
    rs = cell.get("recipe_variance_scales")
    if rs:
        latent *= np.sqrt(np.asarray(rs, float))[recipe][:, None, None]
    noise = np.asarray(cell.get("noise_sd", 1.0), float) * np.ones(k)
    ec = cell.get("cross_half_error_correlation", 0.0)
    ea = rng.normal(size=latent.shape) * noise
    eb = ec * ea + np.sqrt(1 - ec ** 2) * rng.normal(size=latent.shape) * noise
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    T, U = np.empty(n), np.empty(n)
    for m in np.unique(counts):
        # A configuration with m seeds is centred on its own m runs and divided by its own m - 1.
        idx = np.nonzero(counts == m)[0]
        am, bm = a[idx, :m], b[idx, :m]
        dam = am - am.mean(1, keepdims=True)
        dbm = bm - bm.mean(1, keepdims=True)
        cross = np.einsum("crj,crk->cjk", dam, dbm) / (m - 1)
        cov = (cross + cross.transpose(0, 2, 1)) / 2
        T[idx] = np.einsum("j,cjk,k->c", w, cov, w)
        U[idx] = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda, counts


def _wild(T, U, cluster, n_boot=4999, alpha=0.05, seed=0, weights="rademacher", cr3=False):
    """Wild cluster bootstrap-t, copied from the shipped estimator with two options added."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    if cr3:
        u_g = np.bincount(inv, weights=U, minlength=G)
        h = np.clip(u_g / sU, 0.0, 0.99)
        r = r / (1.0 - h)[inv]
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    rng = np.random.default_rng(seed)
    if weights == "rademacher":
        v = rng.choice([-1.0, 1.0], size=(n_boot, G))
    elif weights == "mammen":
        p5 = np.sqrt(5.0)
        lo, hi = -(p5 - 1) / 2, (p5 + 1) / 2
        v = np.where(rng.random((n_boot, G)) < (p5 + 1) / (2 * p5), lo, hi)
    else:
        w6 = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
        v = w6[rng.integers(0, 6, size=(n_boot, G))]
    vb = v[:, inv]
    Tb = th * U + vb * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, vb.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = se_b > 0
    tb = ((th_b[ok] - th) / se_b[ok])
    tb = tb[np.isfinite(tb)]
    if tb.size < max(100, int(0.9 * n_boot)):
        return float("nan"), float("nan")
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    lo, hi = th - lo_q * se, th - hi_q * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


def _cluster_t_cr1(T, U, cluster, alpha=0.05):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    e = np.bincount(inv, weights=np.asarray(T, float) - th * np.asarray(U, float), minlength=G)
    se = float(np.sqrt(G / (G - 1.0) * np.sum(e ** 2))) / sU
    crit = float(student_t.ppf(1 - alpha / 2, G - 1))
    lo, hi = th - crit * se, th + crit * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


SEED, REPS = 20260989, 4000
SIZES_PER_RECIPE = 5
METHODS = ("wild_recipe", "cluster_t_recipe", "wild_size", "cluster_t_size")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}, "shipped_check": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "lo": 0, "up": 0, "bad": 0, "excl": 0, "w": []} for m in METHODS}
    runs_seen = []
    check = float("nan")
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 3300, rep])
        T, U, recipe, truth, counts = r6_simulate(cell, rng)
        runs_seen.append(float(counts.mean()))
        band = np.arange(T.size) % SIZES_PER_RECIPE
        ivs = {"wild_recipe": _wild(T, U, recipe, seed=rep),
               "cluster_t_recipe": _cluster_t_cr1(T, U, recipe)}
        if np.unique(band).size > 1:
            ivs["wild_size"] = _wild(T, U, band, seed=rep)
            ivs["cluster_t_size"] = _cluster_t_cr1(T, U, band)
        if rep == 0:
            # Confirms the reimplemented wild interval matches the shipped estimator.
            ref = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=rep)
            a, b = ivs["wild_recipe"]
            check = max(abs(a - ref.lo), abs(b - ref.hi))
        for m, (lo, hi) in ivs.items():
            if np.isfinite(lo) and np.isfinite(hi):
                acc[m]["cov"] += lo <= truth <= hi
                acc[m]["lo"] += lo > truth; acc[m]["up"] += hi < truth
                # The paper's conclusion is an exclusion of one, so we score that directly.
                acc[m]["excl"] += lo > 1.0
                acc[m]["w"].append(hi - lo)
            else:
                acc[m]["bad"] += 1
    out = {"name": cell["name"], "truth": truth,
           "mean_runs_per_config": float(np.mean(runs_seen)),
           "varied": {k: v for k, v in cell.items() if k != "name"}}
    for m, a in acc.items():
        if not a["w"] and not a["bad"]:
            continue
        c = a["cov"] / REPS
        out[m] = {"coverage": c, "mc_se": float(np.sqrt(c * (1 - c) / REPS)),
                  "excludes_one_rate": a["excl"] / REPS,
                  "lower_miss": a["lo"] / REPS, "upper_miss": a["up"] / REPS,
                  "undefined_or_unbounded": a["bad"] / REPS,
                  "median_width": float(np.median(a["w"])) if a["w"] else None}
    report["cells"][cell["name"]] = out
    report["shipped_check"][cell["name"]] = float(check)
    print(f"[{cell['name']}] {time.time() - t1:.0f}s check {check:.3g} " + json.dumps({m: round(out[m]["coverage"], 4) for m in METHODS if m in out}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_ragged_runs.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
