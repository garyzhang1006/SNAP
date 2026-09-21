"""R6 the BoolQ result as a continuous dial rather than a switch.

Design fixed before running (2026-09-16, written 13:00 EDT). The accuracy conclusion turns on one
benchmark. BoolQ carries 84 percent of the estimated accuracy variance trace, the full battery gives
1.078 with an interval that includes one, and removing BoolQ outright gives 1.558. A reader is entitled
to ask whether that jump is a smooth function of how much weight BoolQ carries, or whether it appears
only at the moment the benchmark leaves the battery. A binary removal cannot tell them, and the paper
currently reports only the two endpoints of a dial it never turned.
This run turns it. Using the same weighted rebuild that reproduced the shipped numerator and denominator
to one part in 1e19 under flat weights, it sweeps the BoolQ weight from its flat 0.10 down to 0 in
sixteen steps, renormalising the other nine benchmarks to carry the remainder equally, and computes the
estimate and a recipe-clustered wild interval at 4,999 draws for each step on both scales. It reports the
weight at which the accuracy interval stops including one, which is the number a reader wants, and it
carries margins alongside as a control, since the margin conclusion should barely move. A smooth curve
means the accuracy reading is a statement about how much a battery leans on one benchmark. A cliff at the
very end would mean something about BoolQ's removal rather than about its weight, and we would say so.
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


BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
BQ = BOOLQ[0]
K = len(TR)
FLAT = np.full(K, 1.0 / K)
WEIGHTS = [round(0.10 - 0.10 * i / 15.0, 6) for i in range(16)]
SEED = 20260953

report = {"design": __doc__, "traits": TR, "boolq_index": BQ, "n_boot": 4999,
          "boolq_weights": WEIGHTS, "seed": SEED, "scales": {}}
for name in ("margin", "accuracy"):
    t1 = time.time()
    pA, pB = projections(name)
    Tf, Uf = weighted_TU(pA, pB, FLAT)
    ref = estimate(pop, name, check=False)
    check = float(max(np.max(np.abs(Tf - ref.T)), np.max(np.abs(Uf - ref.U))))
    rows, first_excluding = [], None
    for wi, wb in enumerate(WEIGHTS):
        w = np.full(K, (1.0 - wb) / (K - 1))
        w[BQ] = wb
        assert abs(w.sum() - 1.0) < 1e-12, w.sum()
        T, U = weighted_TU(pA, pB, w)
        th = float(np.sum(T)) / float(np.sum(U))
        lam = float(np.sqrt(th)) if th > 0 else None
        lo, hi, th_boot = wild(T, U, pop.recipe, n_boot=4999, seed=SEED + wi)
        excl = bool(lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi)
                    and (lo > 1.0 or hi < 1.0))
        rows.append({"boolq_weight": wb, "other_weight": float(w[0]), "lambda_hat": lam,
                     "lo": lo, "hi": hi, "excludes_one": excl})
        if excl and first_excluding is None:
            first_excluding = wb
        print(f"[{name}/w{wb}] lam {lam:.4f} ci {lo:.4f} {hi:.4f} excl {excl}", flush=True)
    report["scales"][name] = {"shipped_rebuild_max_abs_diff": check, "rows": rows,
                              "first_boolq_weight_excluding_one": first_excluding,
                              "seconds": time.time() - t1}

report["wall_seconds"] = time.time() - t0
(W / "r6_boolq_sweep.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
