"""R6 whether a battery with gaps costs more on the accuracy scale than on margins.

Design fixed before running (2026-09-16, written 18:20 EDT). snap-r6-missing-configs drops configurations
from a margin-like population, which is the easier of the two scales this paper reports, because its
latent signal is four times the accuracy scale's and its item noise is half. Every other place we have
looked, the accuracy scale has been the one that breaks first, since single-band coverage falls to 0.707
there at three runs while margins hold, and the accuracy conclusion is a null with power near 0.135 at a
true ratio of 1.10. A reader who plans an incomplete accuracy comparison gets no guidance from a margin
result, and the two scales have already diverged enough that assuming they agree would be a guess.
This run repeats the same drops on an accuracy-like population, removing a tenth, a quarter, a third and
a half of the 125 cells at random, plus a lumpy quarter that takes six whole recipes, at 4,000 replicates
each. It reports coverage, the exclusion rate and the median width beside the complete design, so the
cost of a gap is separable from the cost of the scale. Seed 20260981 keeps the draws distinct.
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
 {"name": "complete", "rho": 0.018, "noise_sd": 1.45},
 {"name": "drop_10pct", "rho": 0.018, "noise_sd": 1.45, "drop_fraction": 0.10},
 {"name": "drop_25pct", "rho": 0.018, "noise_sd": 1.45, "drop_fraction": 0.25},
 {"name": "drop_33pct", "rho": 0.018, "noise_sd": 1.45, "drop_fraction": 0.33},
 {"name": "drop_50pct", "rho": 0.018, "noise_sd": 1.45, "drop_fraction": 0.50},
 {"name": "drop_whole_recipes_25pct", "rho": 0.018, "noise_sd": 1.45, "drop_recipes": 6},
]
def r6_simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
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
    da = a - a.mean(1, keepdims=True)
    db = b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    # Dropping cells after the population is built leaves the truth untouched, so only the
    # information available to the estimator changes.
    drop_f = cell.get("drop_fraction", 0.0)
    drop_r = cell.get("drop_recipes", 0)
    if drop_f > 0 or drop_r > 0:
        keep = np.ones(T.size, bool)
        if drop_r > 0:
            gone = rng.choice(recipes, size=int(drop_r), replace=False)
            keep &= ~np.isin(recipe, gone)
        if drop_f > 0:
            idx = rng.choice(T.size, size=int(round(drop_f * T.size)), replace=False)
            keep[idx] = False
        # A cluster-robust interval needs at least two surviving recipes to be defined at all.
        if np.unique(recipe[keep]).size >= 2:
            T, U, recipe = T[keep], U[keep], recipe[keep]
    return T, U, recipe, true_lambda


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


SEED, REPS = 20260981, 4000
SIZES_PER_RECIPE = 5
METHODS = ("wild_recipe", "cluster_t_recipe", "wild_size", "cluster_t_size")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}, "shipped_check": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "lo": 0, "up": 0, "bad": 0, "excl": 0, "w": []} for m in METHODS}
    check = float("nan")
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 500, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        band = recipe % SIZES_PER_RECIPE
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
(W / "r6_missing_acc.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
