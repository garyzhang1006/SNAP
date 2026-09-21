"""R6 null calibration of the one deletion that breaks the margin conclusion.

Design fixed before running (2026-09-16, written 00:25 EDT). snap-r6-deletion-null calibrated the
accuracy side of the deletion sweep and found that five recipe flips out of 25 sit in the upper few
percent of chance. The margin side has the mirror problem and no calibration at all. Every recipe
deletion, every recipe pair and every benchmark deletion leaves the margin interval excluding one, and
exactly one deletion breaks it, which is the 530M band at 0.993 to 1.338. That single exception is the
paper's largest disclosed weakness, and a reader cannot tell whether one failure out of five band
deletions is surprising or ordinary. This run measures it. It simulates a margin-like population at the
fitted cell whose true ratio sits near the observed 1.244, with 2,000 replicates, and for each replicate
whose full interval excludes one it recomputes the 25 recipe deletions and the five band deletions with
the shipped construction. It reports how often at least one band deletion loses the exclusion, which is
the observed event, and the same for recipe deletions. Seed 20260938 keeps the draws distinct from the
accuracy calibration. A band failure that is ordinary under the null weakens the deletion as evidence,
and one that is rare means the 530M band carries something the other four don't.
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
 {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73},
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


SEED, REPS = 20260938, 2000
SIZES_PER_RECIPE = 5


def losses(T, U, labels, groups, cluster):
    """How many leave-one-group-out intervals exclude one, and the closest endpoint to one.

    The cluster vector stays the recipe throughout, matching the observed sweep, so that
    deleting a size band changes the sample without also changing the clustering.
    """
    n_lost, worst = 0, None
    for g in groups:
        keep = labels != g
        lo, hi = _wild(T[keep], U[keep], cluster[keep], seed=0)
        if not (np.isfinite(lo) and np.isfinite(hi)):
            n_lost += 1
            continue
        if lo <= 1.0 <= hi:
            n_lost += 1
        # How far the lower endpoint sits above one, so the smallest margin over the sweep is visible.
        worst = lo - 1.0 if worst is None else min(worst, lo - 1.0)
    return n_lost, worst


report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    rows = []
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 600, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        band = np.arange(T.size) % SIZES_PER_RECIPE
        lo, hi = _wild(T, U, recipe, seed=rep)
        full_excludes = bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 1.0 or hi < 1.0))
        nr, wr = losses(T, U, recipe, np.unique(recipe), recipe)
        ns, ws = losses(T, U, band, np.unique(band), recipe)
        rows.append({"full_excludes_one": full_excludes, "recipe_flips": nr, "size_flips": ns,
                     "recipe_worst_margin": wr, "size_worst_margin": ws})
    cond = [r for r in rows if r["full_excludes_one"]]
    rv = np.array([r["recipe_flips"] for r in cond], float)
    sv = np.array([r["size_flips"] for r in cond], float)
    out = {"name": cell["name"], "truth": truth, "n_rep": REPS,
           "share_full_excludes_one": len(cond) / REPS,
           "recipe_losses_mean": float(rv.mean()) if rv.size else None,
           "recipe_losses_median": float(np.median(rv)) if rv.size else None,
           "recipe_losses_p95": float(np.percentile(rv, 95)) if rv.size else None,
           "recipe_losses_max": float(rv.max()) if rv.size else None,
           "share_recipe_losses_at_least_1": float(np.mean(rv >= 1)) if rv.size else None,
           "size_losses_mean": float(sv.mean()) if sv.size else None,
           "share_size_losses_at_least_1": float(np.mean(sv >= 1)) if sv.size else None,
           "share_size_losses_at_least_2": float(np.mean(sv >= 2)) if sv.size else None,
           "size_worst_margin_median": float(np.median(
               [r["size_worst_margin"] for r in cond if r["size_worst_margin"] is not None]))
               if cond else None,
           "seconds": time.time() - t1}
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}] {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_deletion_null_margin.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
