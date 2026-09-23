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

R8 rerun for rebuttal finding R6-20 (2026-09-23). The computation above is the snap-r6-weights script
from git commit 0dc2561 (research/kaggle/snap-r6-weights/snap-r6-weights.py), unchanged in seed, draw
counts, concentrations, stream keys and interval code, on the same two datasets. The slug was later
reused for a different coverage simulation, which overwrote the original script and result in the tree.
This rerun adds per-draw records and a mechanical comparison against the values that
deliverables/appendices_bcd.tex:204 quotes, and writes r8_r6_20.json.
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
        per_lo, per_hi = [], []
        worst = None
        for d in range(DRAWS):
            w = rng.dirichlet(np.full(K, conc))
            T, U = weighted_TU(pA, pB, w)
            lo, hi, th = wild(T, U, pop.recipe, seed=d)
            l = float(np.sqrt(th)) if th >= 0 else float("nan")
            lam.append(l); per_lo.append(lo); per_hi.append(hi)
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
            "concentration": conc, "n_excluding_one": int(excl), "share_excluding_one": excl / DRAWS,
            "undefined": bad / DRAWS, "lambda_mean": float(v.mean()),
            "lambda_p05": float(np.percentile(v, 5)), "lambda_p95": float(np.percentile(v, 95)),
            "lambda_min": float(v.min()), "lambda_max": float(v.max()), "lowest_estimate": worst,
            # Per-draw records so any later summary is recomputable without rerunning.
            "per_draw": {"lambda_hat": lam, "lo": per_lo, "hi": per_hi}}
        print(f"[{name}/{fam}] excl {excl / DRAWS:.4f} lam "
              f"{v.min():.3f}-{v.max():.3f} {time.time() - t1:.0f}s", flush=True)
    report["batteries"][name] = cell

# Values quoted in deliverables/appendices_bcd.tex:204 (and supplement_extended_body.tex:370), typed in
# from the sentence text on 2026-09-23. Each entry maps to the computed field and the decimals printed.
PAPER_SENTENCE = (
    "The rebuild reproduces the shipped values to $10^{-19}$ under flat weights, which is the check that "
    "licenses the sweep. Over 2,000 weightings drawn from a flat Dirichlet, 0.817 of margin intervals still "
    "exclude one. The estimate runs from 0.976 to 1.991 with a 5th percentile of 0.999. Over 2,000 "
    "weightings drawn from a Dirichlet concentrated near the flat point, every margin interval excludes one "
    "and the lowest estimate is 1.059. Accuracy behaves in the direction that favours the reported claim, "
    "because 0.386 of flat-Dirichlet intervals and 0.402 of near-flat ones exclude one while the flat "
    "weighting itself gives 0.993 to 1.157 and doesn't.")
PAPER = [
    ("margin flat-Dirichlet share excluding one", ("margin", "dirichlet_flat", "share_excluding_one"), 0.817, 3),
    ("margin flat-Dirichlet lambda min", ("margin", "dirichlet_flat", "lambda_min"), 0.976, 3),
    ("margin flat-Dirichlet lambda max", ("margin", "dirichlet_flat", "lambda_max"), 1.991, 3),
    ("margin flat-Dirichlet lambda p05", ("margin", "dirichlet_flat", "lambda_p05"), 0.999, 3),
    ("margin near-flat share excluding one (every one of 2,000)", ("margin", "dirichlet_near_flat", "share_excluding_one"), 1.0, 3),
    ("margin near-flat lambda min", ("margin", "dirichlet_near_flat", "lambda_min"), 1.059, 3),
    ("accuracy flat-Dirichlet share excluding one", ("accuracy", "dirichlet_flat", "share_excluding_one"), 0.386, 3),
    ("accuracy near-flat share excluding one", ("accuracy", "dirichlet_near_flat", "share_excluding_one"), 0.402, 3),
    ("accuracy flat-weight interval lo", ("accuracy", None, "lo"), 0.993, 3),
    ("accuracy flat-weight interval hi", ("accuracy", None, "hi"), 1.157, 3),
]
comparison = []
for label, (bat, fam, key), quoted, dec in PAPER:
    src_cell = report["batteries"][bat]
    got = src_cell["families"][fam][key] if fam else src_cell["flat"][key]
    diff = float(got) - quoted
    comparison.append({"quantity": label, "computed": got, "paper": quoted, "paper_decimals": dec,
                       "diff": diff, "matches_at_paper_precision": abs(diff) <= 0.5 * 10 ** -dec + 1e-12})
    print(f"[compare] {label}: computed {got!r} paper {quoted} diff {diff:+.6f}", flush=True)
for bat in ("margin", "accuracy"):
    g = report["batteries"][bat]["flat_check_max_abs_gap"]
    comparison.append({"quantity": f"{bat} flat-weight rebuild max abs gap", "computed": g,
                       "paper": 1e-19, "paper_decimals": None, "diff": None,
                       "matches_at_paper_precision": None})
    print(f"[compare] {bat} flat rebuild gap: computed {g!r} paper order 1e-19", flush=True)
report["paper_source"] = {"file": "deliverables/appendices_bcd.tex", "line": 204, "sentence": PAPER_SENTENCE}
report["paper_comparison"] = comparison
report["wall_seconds"] = time.time() - t0
(W / "r8_r6_20.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
