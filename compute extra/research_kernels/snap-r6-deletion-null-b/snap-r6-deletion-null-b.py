"""R6 precision run for the accuracy null calibrated to the observed 1.078, at 8,000 replicates.

Design fixed before running (2026-09-16, written 00:50 EDT). The first pass at 2,000 replicates put the
Monte Carlo standard error of a tail share near 0.003 for the accuracy count and near 0.008 for the band
count. Both of those tails now carry a sentence in the paper, and the accuracy one sits close enough to
five percent that its own noise could move the reading. This run repeats the identical calibration on
one cell at 8,000 replicates with a fresh seed, which cuts the Monte Carlo standard error by half. The
generator, the deletion sweep, the clustering and the conditioning are unchanged from the first pass, so
the two runs can be compared directly and pooled if they agree. Seed 20260942 keeps the draws distinct.
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
 {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45},
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
    latent = np.sqrt(1 - shared) * rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    if shared > 0:
        latent += np.sqrt(shared) * np.repeat(rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
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


SEED, REPS = 20260942, 8000
SIZES_PER_RECIPE = 5


def flips(T, U, labels, groups, cluster):
    """How many leave-one-group-out intervals exclude one, and the closest endpoint to one.

    The cluster vector stays the recipe throughout, matching the observed sweep, so that
    deleting a size band changes the sample without also changing the clustering.
    """
    n_excl, closest = 0, None
    for g in groups:
        keep = labels != g
        lo, hi = _wild(T[keep], U[keep], cluster[keep], seed=0)
        if not (np.isfinite(lo) and np.isfinite(hi)):
            continue
        if lo > 1.0 or hi < 1.0:
            n_excl += 1
        d = lo - 1.0 if lo > 1.0 else 1.0 - hi
        closest = d if closest is None else max(closest, d)
    return n_excl, closest


report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    rows = []
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 600, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        band = np.arange(T.size) % SIZES_PER_RECIPE
        lo, hi = _wild(T, U, recipe, seed=rep)
        full_includes = bool(np.isfinite(lo) and np.isfinite(hi) and lo <= 1.0 <= hi)
        nr, _ = flips(T, U, recipe, np.unique(recipe), recipe)
        ns, _ = flips(T, U, band, np.unique(band), recipe)
        rows.append({"full_includes_one": full_includes, "recipe_flips": nr, "size_flips": ns})
    cond = [r for r in rows if r["full_includes_one"]]
    rv = np.array([r["recipe_flips"] for r in cond], float)
    sv = np.array([r["size_flips"] for r in cond], float)
    out = {"name": cell["name"], "truth": truth, "n_rep": REPS,
           "share_full_includes_one": len(cond) / REPS,
           "recipe_flips_mean": float(rv.mean()) if rv.size else None,
           "recipe_flips_median": float(np.median(rv)) if rv.size else None,
           "recipe_flips_p95": float(np.percentile(rv, 95)) if rv.size else None,
           "recipe_flips_max": float(rv.max()) if rv.size else None,
           "share_recipe_flips_at_least_5": float(np.mean(rv >= 5)) if rv.size else None,
           "share_recipe_flips_at_least_1": float(np.mean(rv >= 1)) if rv.size else None,
           "size_flips_mean": float(sv.mean()) if sv.size else None,
           "share_size_flips_at_least_1": float(np.mean(sv >= 1)) if sv.size else None,
           "seconds": time.time() - t1}
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}] {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_deletion_null_b.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
