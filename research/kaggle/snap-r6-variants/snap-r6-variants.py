"""R6 interval variants, asking whether any construction reaches nominal coverage in the hard cells.

Design fixed before running (2026-09-15, written 20:05 EDT). snap-r6-precision shows the wild cluster
bootstrap-t covering 0.933 to 0.945 at 10,000 replicates, which is a real shortfall rather than Monte
Carlo noise. The plan asks that, when an interval fails, the failure is quantified across plausible
conditions and an adequate construction is found or the limitation is reported. This run scores six
constructions on the same four cells, with 4,000 replicates and seed 20260918 so the datasets are new.
The constructions are the wild bootstrap-t with Rademacher weights, which reproduces the shipped
interval, the same with Mammen weights and with Webb six-point weights, the wild bootstrap-t with
Rademacher weights and leave-one-cluster-out residual scaling by 1/(1-h_g) where h_g is the cluster's
share of the U sum, the cluster-robust t with the usual G/(G-1) correction that the shipped interval
omits, and the centred test inversion. Each replicate scores every construction on one dataset, so
the comparisons are paired. The Rademacher implementation is checked against the shipped estimator on
the first replicate of each cell and the largest endpoint difference is reported.
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
 {"name": "margin_like_cross_half_error_corr_0.1", "rho": 0.061, "noise_sd": 0.73, "cross_half_error_correlation": 0.1},
 {"name": "margin_like_one_dominant_recipe", "rho": 0.061, "noise_sd": 0.73, "recipe_variance_scales": [6.0] + [1.0] * 24},
 {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73},
 {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45},
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


SEED, REPS = 20260918, 4000
METHODS = ("wild_rademacher", "wild_mammen", "wild_webb", "wild_cr3", "cluster_t_cr1", "centred")
report = {"design": __doc__, "seed": SEED, "reps": REPS, "cells": {}, "shipped_check": {}}
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {m: {"cov": 0, "lo": 0, "up": 0, "bad": 0, "w": []} for m in METHODS}
    check = 0.0
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 20, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        ivs = {"wild_rademacher": _wild(T, U, recipe, seed=rep),
               "wild_mammen": _wild(T, U, recipe, seed=rep, weights="mammen"),
               "wild_webb": _wild(T, U, recipe, seed=rep, weights="webb"),
               "wild_cr3": _wild(T, U, recipe, seed=rep, cr3=True),
               "cluster_t_cr1": _cluster_t_cr1(T, U, recipe)}
        res = invert(T, U, recipe, form="centred")
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
        acc["centred"]["cov"] += covers(res, truth)
        if res["kind"] == "bounded":
            lo, hi = res["lambda_sets"][0]
            acc["centred"]["lo"] += lo > truth; acc["centred"]["up"] += hi < truth
            acc["centred"]["w"].append(hi - lo)
        else:
            acc["centred"]["bad"] += 1
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
(W / "r6_variants.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
