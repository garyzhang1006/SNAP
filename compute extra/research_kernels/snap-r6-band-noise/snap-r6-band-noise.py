"""R6 what happens when the item noise is louder in some size bands than in others.

Design fixed before running (2026-09-16, written 18:56 EDT). Every simulation this appendix reports gives
all 125 configurations the same item noise, and the noise sweep moved that single number rather than
spreading it. Real batteries are not like that, because a 150M model and a 1B model do not score with the
same consistency, and the shipped design pairs each recipe with all five bands. Noise that tracks the band
is therefore heteroscedasticity aligned with a variable the recipe clustering never models, which is the
shape cluster-robust inference is usually warned about. The estimator sums numerator and denominator over
configurations with flat weights, so a loud band contributes as much as a quiet one while carrying several
times its sampling variance, and nothing we have run says what that costs.
This run measures it. It multiplies the item noise by a per-band factor rather than a single constant, and
it sweeps the spread of that factor from none through a two-fold, four-fold and sixteen-fold ramp across
the five bands, with a matching pair that puts the loud band at one end and then at the other so a reader
can see whether the direction matters. Two further cells scramble the ramp so the loud bands are not
adjacent, and two run the four-fold ramp on the accuracy-like population, where the base noise is already
double. Each cell runs 4,000 replicates and reports coverage, the exclusion rate at the true 1.2446, the
median width and the undefined rate for the recipe-clustered and band-clustered intervals. Because the
true ratio is a property of the latent covariance rather than of the noise, the truth stays fixed across
the whole sweep and the cells are directly comparable. Seed 20260991 keeps the draws distinct.
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
 {"name": "flat", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 1.0, 1.0, 1.0, 1.0]},
 {"name": "ramp2_up", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 1.25, 1.5, 1.75, 2.0]},
 {"name": "ramp4_up", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 1.75, 2.5, 3.25, 4.0]},
 {"name": "ramp4_down", "rho": 0.061, "noise_sd": 0.73, "band_noise": [4.0, 3.25, 2.5, 1.75, 1.0]},
 {"name": "ramp16_up", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 4.75, 8.5, 12.25, 16.0]},
 {"name": "one_loud", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 1.0, 4.0, 1.0, 1.0]},
 {"name": "alternating", "rho": 0.061, "noise_sd": 0.73, "band_noise": [1.0, 4.0, 1.0, 4.0, 1.0]},
 {"name": "acc_flat", "rho": 0.018, "noise_sd": 1.45, "band_noise": [1.0, 1.0, 1.0, 1.0, 1.0]},
 {"name": "acc_ramp4", "rho": 0.018, "noise_sd": 1.45, "band_noise": [1.0, 1.75, 2.5, 3.25, 4.0]},
 {"name": "acc_one_loud", "rho": 0.018, "noise_sd": 1.45, "band_noise": [1.0, 1.0, 4.0, 1.0, 1.0]},
]
def r6_simulate(cell, rng):
    k = cell.get("benchmarks", 10)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    r = cell.get("runs", 3)
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
    bn = cell.get("band_noise")
    if bn:
        # Configuration c sits in band c % sizes, so the band factor tiles down the configuration axis.
        noise = noise[None, None, :] * np.tile(np.asarray(bn, float), recipes)[:, None, None]
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


SEED, REPS = 20260991, 4000
SIZES_PER_RECIPE = 5
METHODS = ("wild_recipe", "cluster_t_recipe", "wild_size", "cluster_t_size")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}, "shipped_check": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "lo": 0, "up": 0, "bad": 0, "excl": 0, "w": []} for m in METHODS}
    check = float("nan")
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 3600, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
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
(W / "r6_band_noise.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
