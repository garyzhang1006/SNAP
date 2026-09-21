"""R7 cross-fitted proxies against known seed covariance, so their adjusted values can be read.

Design fixed before running (2026-09-15, written 19:55 EDT). snap-r7-crossfit reports cross-fitted
inflation of 0.9725 for the one-factor proxy on margins, together with an independence null near one.
An independence null only shows that a proxy doesn't create covariance. It doesn't say what a proxy
returns when the covariance is real and no competence variable exists, which is the value the
observed number must be read against. This run therefore repeats the four cross-fitted weightings on
300 simulated populations for each of the three structures of Table 11, which are independence, a
single common correlation that reproduces the observed inflation, and the nearest positive
semidefinite matrix to the observed seed covariance. The proxy code, the folds and the seeds follow
snap-r7-crossfit, and the simulator follows snap-r7-proxy-null2.
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
from seednoise.nulls import NOMINAL_ITEMS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import SimSpec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
VARIANTS = ("shipped", "shrunk", "factor", "clip_drop")
N_FOLDS, N_REP, FLOOR = 5, 300, 1e-12


def weights(p, name, variant):
    """Per-benchmark weights and standardising SDs, learned on the given (training) population."""
    S = sigma_e(p, name)
    v = np.diag(S).copy()
    pos = v[v > FLOOR]
    med = float(np.median(pos)) if pos.size else FLOOR
    if variant == "shipped":
        return np.ones(p.K), np.sqrt(np.clip(v, FLOOR, None))
    if variant == "clip_drop":
        return (v > FLOOR).astype(float), np.sqrt(np.clip(v, FLOOR, None))
    vs = 0.5 * np.clip(v, 0.0, None) + 0.5 * med
    sd = np.sqrt(np.clip(vs, FLOOR, None))
    if variant == "shrunk":
        return np.ones(p.K), sd
    R = S / np.outer(sd, sd)
    R = np.where(np.isfinite(R), R, 0.0)
    np.fill_diagonal(R, 1.0)
    w_eig, V = np.linalg.eigh(0.5 * (R + R.T))
    lam1 = V[:, -1] * np.sqrt(max(w_eig[-1], 0.0))
    if lam1.sum() < 0:
        lam1 = -lam1
    lam1 = np.clip(lam1, -0.99, 0.99)
    w = lam1 / np.maximum(1.0 - lam1 ** 2, 0.05)
    return w, sd


def proxy(d, w, sd):
    """Leave-one-benchmark-out weighted proxy, shape (N, R, K)."""
    z = (d / sd) * w
    tot = z.sum(axis=2, keepdims=True)
    den = w.sum() - w
    den = np.where(np.abs(den) < 1e-9, np.nan, den)
    return (tot - z) / den


def slopes(dA, dB, xA, xB):
    b = np.zeros(dA.shape[2])
    for j in range(dA.shape[2]):
        vals = []
        for y, xo in ((dA, xB), (dB, xA)):
            x = xo[:, :, j].ravel(); yy = y[:, :, j].ravel()
            ok = np.isfinite(x) & np.isfinite(yy)
            if ok.sum() > 2 and np.any(x[ok] != 0):
                vals.append(float(np.linalg.lstsq(x[ok][:, None], yy[ok], rcond=None)[0][0]))
        b[j] = float(np.mean(vals)) if vals else 0.0
    return b


def lam(p, name):
    return float(estimate(p, name, check=False).lambda_hat)


def folds_of(p, n_folds, seed=0):
    rs = np.unique(p.recipe)
    order = np.random.default_rng(seed).permutation(rs)
    return [np.asarray(order[f::n_folds]) for f in range(n_folds)]


def crossfit(p, name, variant, n_folds=N_FOLDS):
    ph = p.pheno(name)
    dA, dB = deviations(ph.A), deviations(ph.B)
    rA, rB = dA.copy(), dB.copy()
    fold_w, fold_b = [], []
    for held in folds_of(p, n_folds):
        test = np.isin(p.recipe, held)
        tr = p.subset(np.flatnonzero(~test))
        w, sd = weights(tr, name, variant)
        tph = tr.pheno(name)
        tA, tB = deviations(tph.A), deviations(tph.B)
        b = slopes(tA, tB, proxy(tA, w, sd), proxy(tB, w, sd))
        xA, xB = proxy(dA, w, sd), proxy(dB, w, sd)
        i = np.flatnonzero(test)
        rA[i] = dA[i] - b * np.nan_to_num(xA[i])
        rB[i] = dB[i] - b * np.nan_to_num(xB[i])
        fold_w.append(np.abs(w) / max(np.abs(w).sum(), 1e-12)); fold_b.append(b)
    out = lam(p.with_phenotype("cf", rA, rB), "cf")
    return out, np.asarray(fold_w), np.asarray(fold_b)


def insample(p, name, variant):
    ph = p.pheno(name)
    dA, dB = deviations(ph.A), deviations(ph.B)
    w, sd = weights(p, name, variant)
    xA, xB = proxy(dA, w, sd), proxy(dB, w, sd)
    b = slopes(dA, dB, xA, xB)
    return lam(p.with_phenotype("is", dA - b * np.nan_to_num(xA), dB - b * np.nan_to_num(xB)), "is")


def reliability(p, name, variant):
    """Correlation between the half-A and half-B proxy over all runs, full battery."""
    w, sd = weights(p, name, variant)
    ph = p.pheno(name)
    a = ((deviations(ph.A) / sd) * w).sum(axis=2).ravel()
    b = ((deviations(ph.B) / sd) * w).sum(axis=2).ravel()
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def min_fold_corr(fw):
    c = np.corrcoef(fw)
    return float(np.min(c[np.triu_indices_from(c, 1)]))



report = {"design": __doc__, "variants": list(VARIANTS), "n_folds": N_FOLDS, "n_rep": N_REP,
          "traits": list(pop.traits), "observed": {}, "cells": {}}
n_items = tuple(int(n) for n in np.asarray(pop.n_items).tolist()) if pop.n_items is not None else tuple([NOMINAL_ITEMS] * pop.K)
n_half = np.maximum(np.asarray(n_items, float) / 2.0, 1.0)

for name in ("margin", "accuracy"):
    base = lam(pop, name)
    report["observed"][name] = {"unadjusted": base,
                                **{v: crossfit(pop, name, v)[0] for v in VARIANTS}}
    print(f"[{name}] observed " + json.dumps({k: round(v, 4) for k, v in report["observed"][name].items()}), flush=True)
    S = sigma_e(pop, name)
    sd = np.sqrt(np.clip(np.diag(S), 1e-9, None))
    Rm = S / np.outer(sd, sd); np.fill_diagonal(Rm, 1.0); Rm = np.where(np.isfinite(Rm), Rm, 0.0)
    matched, clipped = nearest_psd(np.outer(sd, sd) * Rm, floor=FLOOR)
    off = np.outer(sd, sd); np.fill_diagonal(off, 0.0)
    r = (base ** 2 - 1) * np.sum(sd ** 2) / off.sum()
    equi = np.outer(sd, sd) * ((1 - r) * np.eye(pop.K) + r)
    comp = variance_components(pop, name)
    item_sd = tuple(np.sqrt(np.clip(comp.noise2, 1e-12, None) * n_half).tolist())
    for label, target in (("independence", np.diag(sd ** 2)), ("equicorrelated", equi), ("matched", matched)):
        t1 = time.time(); rows = []
        for i in range(N_REP):
            spec = SimSpec(n_config=pop.N, n_runs=pop.R, traits=tuple(pop.traits), n_items=n_items,
                           item_sd=item_sd, n_recipes=25, n_sizes=5, seed=20260915 + 7919 * i)
            spec.sigma_e = target
            sim = simulate(spec)
            rows.append({"unadjusted": lam(sim, name), **{v: crossfit(sim, name, v)[0] for v in VARIANTS}})
        cell = {"r": float(r) if label == "equicorrelated" else None,
                "psd_clipped": float(clipped) if label == "matched" else None}
        for k in rows[0]:
            a = np.asarray([row[k] for row in rows], float); f = a[np.isfinite(a)]
            cell[k] = {"n_finite": int(f.size), "mean": float(f.mean()), "sd": float(f.std(ddof=1)),
                       "p05": float(np.percentile(f, 5)), "median": float(np.median(f)), "p95": float(np.percentile(f, 95))}
        report["cells"][f"{name}/{label}"] = cell
        print(f"[{name}/{label}] {time.time() - t1:.0f}s " + json.dumps({k: round(v["mean"], 4) for k, v in cell.items() if isinstance(v, dict)}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r7_crossfit_null.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
