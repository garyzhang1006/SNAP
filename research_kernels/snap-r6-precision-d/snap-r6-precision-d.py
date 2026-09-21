"""R6 tie-breaker for the one coverage cell whose two 10,000-replicate runs disagree.

Design fixed before running (2026-09-15, written 22:05 EDT). snap-r6-precision returned wild coverage of
0.9404 in the margin-like cell at 10,000 replicates, and snap-r6-precision-c returned 0.9508 for the same
cell at the same count with a different seed. Each carries a Monte Carlo standard error near 0.0022, so
the two sit more than three standard errors of their difference apart, and a homogeneity test across the
runs of that cell gives about 0.005. Diffing the two generators ruled out an implementation difference,
and the median interval widths agree at 0.2417 against 0.2422 with no undefined replicate in either run,
so the remaining explanation is dataset variation. The appendix currently pools the two at 0.946 and
declines to call the cell settled. This run takes the same cell to 40,000 replicates on fresh datasets,
with seed 20260925 and a cell index offset of two hundred, which drops the standard error to about
0.0011 and puts the pooled three-run estimate inside 0.002. It scores the shipped Rademacher version and
the residual-scaled one, so the construction comparison gains precision in the same pass. Nothing else
changes, and a result near 0.946 confirms the pooled value the paper already reports.
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
def invert(T, U, cluster, alpha=0.05, form="restricted"):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    t = np.bincount(inv, weights=np.asarray(T, float), minlength=G)
    u = np.bincount(inv, weights=np.asarray(U, float), minlength=G)
    c2 = float(student_t.ppf(1 - alpha / 2, G - 1)) ** 2
    a, b = t.sum(), u.sum()
    Stt, Stu, Suu = float(t @ t), float(t @ u), float(u @ u)
    if form == "restricted":
        m, k = 0.0, c2
    else:
        m, k = c2 / (G - 1), c2 * G / (G - 1)
    # (1 + m) (a - theta b)^2 - k (Stt - 2 theta Stu + theta^2 Suu) <= 0
    A = (1 + m) * b * b - k * Suu
    B = -2 * (1 + m) * a * b + 2 * k * Stu
    C = (1 + m) * a * a - k * Stt
    f = lambda th: A * th * th + B * th + C  # noqa: E731
    disc = B * B - 4 * A * C
    if abs(A) < 1e-300:
        roots = [] if abs(B) < 1e-300 else [-C / B]
    elif disc < 0:
        roots = []
    else:
        s = np.sqrt(disc); roots = sorted([(-B - s) / (2 * A), (-B + s) / (2 * A)])
    # Acceptance set on [0, inf): evaluate f between breakpoints.
    pts = sorted([0.0] + [r for r in roots if r > 0])
    segs = []
    edges = pts + [np.inf]
    for lo, hi in zip(edges[:-1], edges[1:]):
        mid = lo + 1.0 if not np.isfinite(hi) else 0.5 * (lo + hi)
        if f(mid) <= 0:
            segs.append([lo, hi])
    merged = []
    for s_ in segs:
        if merged and abs(merged[-1][1] - s_[0]) < 1e-15:
            merged[-1][1] = s_[1]
        else:
            merged.append(list(s_))
    if not merged:
        kind = "empty"
    elif len(merged) == 1 and np.isfinite(merged[0][1]):
        kind = "bounded"
    elif len(merged) == 1 and merged[0][0] == 0.0 and not np.isfinite(merged[0][1]):
        kind = "all"
    elif len(merged) == 1:
        kind = "ray"
    else:
        kind = "two_pieces"
    lam = [[float(np.sqrt(lo)), float(np.sqrt(hi)) if np.isfinite(hi) else None] for lo, hi in merged]
    return {"kind": kind, "lambda_sets": lam}


def covers(res, truth):
    return any(lo <= truth and (hi is None or truth <= hi) for lo, hi in res["lambda_sets"])


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


SEED, REPS = 20260925, 40000
METHODS = ("wild_rademacher", "wild_cr3")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}, "shipped_check": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "lo": 0, "up": 0, "bad": 0, "w": []} for m in METHODS}
    check = 0.0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 200, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        ivs = {"wild_rademacher": _wild(T, U, recipe, seed=rep),
               "wild_cr3": _wild(T, U, recipe, seed=rep, cr3=True)}
        if rep == 0:
            ref = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=rep)
            a, b = ivs["wild_rademacher"]
            check = max(abs(a - ref.lo), abs(b - ref.hi))
        for m, (lo, hi) in ivs.items():
            if np.isfinite(lo) and np.isfinite(hi):
                acc[m]["cov"] += lo <= truth <= hi
                acc[m]["lo"] += lo > truth; acc[m]["up"] += hi < truth
                acc[m]["w"].append(hi - lo)
            else:
                acc[m]["bad"] += 1
    out = {"name": cell["name"], "truth": truth}
    for m, a in acc.items():
        c = a["cov"] / REPS
        out[m] = {"coverage": c, "mc_se": float(np.sqrt(c * (1 - c) / REPS)),
                  "lower_miss": a["lo"] / REPS, "upper_miss": a["up"] / REPS,
                  "undefined_or_unbounded": a["bad"] / REPS,
                  "median_width": float(np.median(a["w"])) if a["w"] else None}
    report["cells"][cell["name"]] = out
    report["shipped_check"][cell["name"]] = float(check)
    print(f"[{cell['name']}] {time.time() - t1:.0f}s check {check:.3g} " + json.dumps({m: round(out[m]["coverage"], 4) for m in METHODS}), flush=True)
report["wall_seconds"] = time.time() - t0
(W / "r6_precision_d.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
