"""R6 sensitivity of both conclusions to the equal weighting of the ten benchmarks.

Design fixed before running (2026-09-15, written 23:35 EDT). The estimator aggregates the ten benchmarks
with a flat weight of one tenth each, and every interval in the paper inherits that choice. Dropping one
benchmark at a time is already covered by snap-r6-leave-one-out, which is the coarsest possible probe of
the weighting, since it moves one weight to zero and leaves the other nine flat. A reader who thinks the
flat weight is doing work will ask the finer question, which is what happens across the whole simplex of
weightings rather than at its ten corners. This run answers that directly. It rebuilds the numerator and
the denominator under arbitrary weights from the same contrast projections the shipped estimator uses,
checks that flat weights reproduce the shipped statistic to machine precision, and then draws 2,000
weightings from a flat Dirichlet and 2,000 more from a Dirichlet concentrated near the flat point. Each
weighting gets its own recipe-clustered wild interval at 4,999 draws, and the run reports the share of
weightings whose interval still excludes one, the range of the point estimate, and the weighting that
minimises it. A conclusion that survives the flat simplex is not resting on the equal weighting, and one
that doesn't is a limitation the paper has to state in the same sentence as the estimate.
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
runs_dir = W / "runs"; runs_dir.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs_dir / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import contrast_basis, estimate, half_projections  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402

TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
BASIS = np.atleast_2d(contrast_basis(pop.R))


def projections(name):
    """(N, D, K) contrast projections of each half, which every weighting reuses."""
    ph = pop.pheno(name)
    return half_projections(ph.A, BASIS), half_projections(ph.B, BASIS)


def weighted_TU(pA, pB, w):
    """Numerator and denominator under an arbitrary benchmark weight vector."""
    w = np.asarray(w, float)
    gA, gB = pA @ w, pB @ w
    T = (gA * gB).mean(axis=1)
    per_trait = (pA * pB).mean(axis=1)
    U = per_trait @ (w * w)
    return T, U


def wild(T, U, cluster, n_boot=4999, alpha=0.05, seed=0):
    """Recipe-clustered wild bootstrap-t on Lambda, matching the shipped estimator."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=(n_boot, G))[:, inv]
    Tb = th * U + v * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, v.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = se_b > 0
    tb = (th_b[ok] - th) / se_b[ok]
    tb = tb[np.isfinite(tb)]
    if tb.size < max(100, int(0.9 * n_boot)):
        return float("nan"), float("nan"), th
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    lo, hi = th - lo_q * se, th - hi_q * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"), th)


K = len(TR)
FLAT = np.full(K, 1.0 / K)
DRAWS = 2000
SEED = 20260935
report = {"design": __doc__, "traits": TR, "draws_per_family": DRAWS, "seed": SEED, "batteries": {}}
for name in ("margin", "accuracy"):
    t1 = time.time()
    pA, pB = projections(name)
    Tf, Uf = weighted_TU(pA, pB, FLAT)
    ref = estimate(pop, name, check=False)
    gap = max(float(np.max(np.abs(Tf - np.asarray(ref.T, float)))),
              float(np.max(np.abs(Uf - np.asarray(ref.U, float)))))
    assert gap < 1e-12, (name, gap)
    lo_f, hi_f, th_f = wild(Tf, Uf, pop.recipe, seed=0)
    shipped = wild_bootstrap_t(ref.T, ref.U, pop.recipe, n_boot=4999, seed=0)
    cell = {"flat_check_max_abs_gap": gap,
            "flat": {"lambda_hat": float(np.sqrt(th_f)), "lo": lo_f, "hi": hi_f},
            "shipped": {"lo": float(shipped.lo), "hi": float(shipped.hi)}, "families": {}}
    for fi, (fam, conc) in enumerate((("dirichlet_flat", 1.0), ("dirichlet_near_flat", 20.0))):
        # String hashing is salted per process, so the family index seeds the stream instead.
        rng = np.random.default_rng([SEED, fi, len(name)])
        lam, excl, bad = [], 0, 0
        worst = None
        for d in range(DRAWS):
            w = rng.dirichlet(np.full(K, conc))
            T, U = weighted_TU(pA, pB, w)
            lo, hi, th = wild(T, U, pop.recipe, seed=d)
            l = float(np.sqrt(th)) if th >= 0 else float("nan")
            lam.append(l)
            if np.isfinite(lo) and np.isfinite(hi):
                e = lo > 1.0 or hi < 1.0
                excl += e
                if worst is None or (np.isfinite(l) and l < worst["lambda_hat"]):
                    worst = {"lambda_hat": l, "lo": lo, "hi": hi, "excludes_one": bool(e),
                             "weights": [round(float(x), 5) for x in w]}
            else:
                bad += 1
        v = np.asarray(lam, float); v = v[np.isfinite(v)]
        cell["families"][fam] = {
            "concentration": conc, "share_excluding_one": excl / DRAWS,
            "undefined": bad / DRAWS, "lambda_mean": float(v.mean()),
            "lambda_p05": float(np.percentile(v, 5)), "lambda_p95": float(np.percentile(v, 95)),
            "lambda_min": float(v.min()), "lambda_max": float(v.max()), "lowest_estimate": worst}
        print(f"[{name}/{fam}] excl {excl / DRAWS:.4f} lam "
              f"{v.min():.3f}-{v.max():.3f} {time.time() - t1:.0f}s", flush=True)
    report["batteries"][name] = cell

report["wall_seconds"] = time.time() - t0
(W / "r6_weights.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
