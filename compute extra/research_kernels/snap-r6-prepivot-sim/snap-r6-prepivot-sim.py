"""R6 test of whether iterated-bootstrap calibration repairs the coverage shortfall in simulation.

Design fixed before running (2026-09-15, written 22:05 EDT). snap-r6-calibrated applied Beran
prepivoting to the observed data and returned an implied coverage of 0.977 for the nominal levels on the
full margin battery, which says the shipped interval is conservative there. The twelve-population
simulation and ten repeats of the seed-label permutation both say the same interval sits below nominal,
near 0.933 and near 0.931. The appendix explains the disagreement by arguing that prepivoting measures
calibration inside the wild resampling model the interval already assumes, so it cannot see a violation
that the bootstrap shares with the estimator. That argument is currently an assertion, and this run
tests it. It scores three intervals on the four cells that carry the shortfall, which are the two with
the lowest wild coverage and the two calibrated to the observed estimates, with 1,000 replicates each,
seed 20260927 and a cell index offset of three hundred. The three are the shipped wild interval at 4,999
draws, an uncalibrated wild interval at 399 draws, and the prepivoted interval built from 399 outer
resamples each carrying a 399-draw inner bootstrap. The middle one separates the effect of the draw
count from the effect of calibration. If the prepivoted interval covers near 0.95 then calibration
repairs the shortfall and the paper should report it as a remedy. If it tracks the uncalibrated one
near 0.93 then the appendix's explanation holds and prepivoting is blind to this error.
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

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402

CELLS = [
 {"name": "margin_like_cross_half_error_corr_0.1", "rho": 0.061, "noise_sd": 0.73, "cross_half_error_correlation": 0.1},
 {"name": "margin_like_one_dominant_recipe", "rho": 0.061, "noise_sd": 0.73, "recipe_variance_scales": [6.0] + [1.0] * 24},
 {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73},
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


SEED, REPS = 20260927, 1000
B1 = B2 = 399


def prepivot_interval(T, U, cluster, rng, b1=B1, b2=B2, alpha=0.05):
    """Beran-prepivoted wild cluster bootstrap-t, returning Lambda endpoints."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G, sU = keys.size, float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    if not (se > 0):
        return float("nan"), float("nan"), float("nan"), float("nan")
    v = rng.choice([-1.0, 1.0], size=(b1, G))[:, inv]
    Tb = th * U + v * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((b1, G))
    np.add.at(eb, (np.arange(b1)[:, None], np.broadcast_to(inv, v.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    good = se_b > 0
    t_b = np.full(b1, np.nan)
    t_b[good] = (th_b[good] - th) / se_b[good]
    tv = t_b[np.isfinite(t_b)]
    if tv.size < int(0.9 * b1):
        return float("nan"), float("nan"), float("nan"), float("nan")
    n_lo, n_hi = np.percentile(tv, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    plain = (th - n_lo * se, th - n_hi * se)
    u = np.full(b1, np.nan)
    ar = np.arange(b2)[:, None]
    for b in range(b1):
        if not np.isfinite(t_b[b]):
            continue
        w = rng.choice([-1.0, 1.0], size=(b2, G))[:, inv]
        Tc = th_b[b] * U + w * rb[b]
        th_c = Tc.sum(axis=1) / sU
        rc = Tc - th_c[:, None] * U
        ec = np.zeros((b2, G))
        np.add.at(ec, (ar, np.broadcast_to(inv, w.shape)), rc)
        se_c = np.sqrt((ec ** 2).sum(axis=1)) / sU
        ok = se_c > 0
        t_c = (th_c[ok] - th_b[b]) / se_c[ok]
        t_c = t_c[np.isfinite(t_c)]
        if t_c.size >= int(0.9 * b2):
            u[b] = float(np.mean(t_c <= t_b[b]))
    uv = u[np.isfinite(u)]
    if uv.size < int(0.9 * b1):
        return float("nan"), float("nan"), float("nan"), float("nan")
    q_lo, q_hi = float(np.percentile(uv, 100 * alpha / 2)), float(np.percentile(uv, 100 * (1 - alpha / 2)))
    c_lo, c_hi = np.percentile(tv, [100 * q_hi, 100 * q_lo])
    calib = (th - c_lo * se, th - c_hi * se)
    root = lambda x: float(np.sqrt(x)) if x >= 0 else float("nan")  # noqa: E731
    return root(plain[0]), root(plain[1]), root(calib[0]), root(calib[1])


METHODS = ("wild_shipped", "wild_399", "prepivoted")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "b1": B1, "b2": B2, "cells": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "bad": 0, "w": []} for m in METHODS}
    check = float("nan")
    levels = []
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 300, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        ivs = {"wild_shipped": _wild(T, U, recipe, seed=rep)}
        if rep == 0:
            # Confirms the reimplemented wild interval matches the shipped estimator.
            ref = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=rep)
            a, b = ivs["wild_shipped"]
            check = max(abs(a - ref.lo), abs(b - ref.hi))
        p_lo, p_hi, c_lo, c_hi = prepivot_interval(T, U, recipe, rng)
        ivs["wild_399"] = (p_lo, p_hi)
        ivs["prepivoted"] = (c_lo, c_hi)
        for m, (lo, hi) in ivs.items():
            if np.isfinite(lo) and np.isfinite(hi):
                acc[m]["cov"] += lo <= truth <= hi
                acc[m]["w"].append(hi - lo)
            else:
                acc[m]["bad"] += 1
    out = {"name": cell["name"], "truth": truth, "shipped_check": float(check)}
    for m, a in acc.items():
        c = a["cov"] / REPS
        out[m] = {"coverage": c, "mc_se": float(np.sqrt(c * (1 - c) / REPS)),
                  "undefined": a["bad"] / REPS,
                  "median_width": float(np.median(a["w"])) if a["w"] else None}
    report["cells"][cell["name"]] = out
    print(f"[{cell['name']}] {time.time() - t1:.0f}s " + json.dumps({m: round(out[m]["coverage"], 4) for m in METHODS}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_prepivot_sim.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
