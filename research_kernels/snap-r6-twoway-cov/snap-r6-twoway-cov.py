"""R6 whether the two-way bootstrap really covers worse than recipe clustering, at eight times the precision.

Design fixed before running (2026-09-16, written 11:20 EDT). snap-r6-twoway-boot found that the two-way
wild bootstrap repairs the negative analytic variance on the observed cells but repairs no coverage, at
0.824 against 0.839 where band sharing sits at a quarter and 0.932 against 0.936 at the joint corner the
data allows. Those two comparisons came from 1,000 replicates at 999 draws, which puts the Monte Carlo
standard error near 0.012 on each side, so neither difference is resolved and the appendix currently
states a dead end it has not actually measured. A reviewer who wants the two-way interval adopted will
notice that. This run repeats the identical two cells at 8,000 replicates and 2,999 draws, which brings
the standard error on each coverage figure to about 0.004 and on the paired difference lower still, since
both intervals are computed on the same replicate. The observed four cells are recomputed at 9,999 draws
with the same seed as before, which is a reproduction check rather than a new result, and they should
return the identical numbers. Seed 20260948 and a cell offset of twenty two hundred keep the simulated
draws distinct. The paired difference is what the appendix should quote, so this run reports it directly.
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
from seednoise.estimator import estimate  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402


def restrict(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, :, m], ph.B[:, :, m])
    n_items = None if p.n_items is None else np.asarray(p.n_items)[m]
    return Population({name: sub}, p.gainA, p.gainB, p.batch, p.recipe, p.size,
                      [p.traits[j] for j in m], p.config_ids, n_items)


def meat(r, inv, G, sU):
    e = np.bincount(inv, weights=r, minlength=G)
    return float(np.sum(e ** 2)) / (sU * sU)


def two_way_boot(T, U, recipe, size, n_boot=9999, alpha=0.05, seed=0):
    """Wild bootstrap with one Rademacher draw per clustering dimension, multiplied together."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    _, ir = np.unique(np.asarray(recipe), return_inverse=True)
    _, isz = np.unique(np.asarray(size), return_inverse=True)
    Gr, Gs = ir.max() + 1, isz.max() + 1
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    pair = ir * Gs + isz
    _, ip = np.unique(pair, return_inverse=True)
    v_two = meat(r, ir, Gr, sU) + meat(r, isz, Gs, sU) - meat(r, ip, ip.max() + 1, sU)
    rng = np.random.default_rng(seed)
    a = rng.choice([-1.0, 1.0], size=(n_boot, Gr))[:, ir]
    b = rng.choice([-1.0, 1.0], size=(n_boot, Gs))[:, isz]
    Tb = th * U + (a * b) * r
    th_b = Tb.sum(axis=1) / sU
    th_b = th_b[np.isfinite(th_b)]
    lo_q, hi_q = np.percentile(th_b - th, [100 * (alpha / 2), 100 * (1 - alpha / 2)])
    # Basic bootstrap on theta, which needs no variance estimate and so cannot go negative.
    lo, hi = th - hi_q, th - lo_q
    return {"theta": th, "lambda_hat": float(np.sqrt(th)) if th >= 0 else None,
            "lo": float(np.sqrt(lo)) if lo >= 0 else None,
            "hi": float(np.sqrt(hi)) if hi >= 0 else None,
            "boot_sd_theta": float(np.std(th_b, ddof=1)),
            "analytic_two_way_variance": v_two,
            "analytic_two_way_variance_negative": bool(v_two <= 0)}


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
report = {"design": __doc__, "traits": TR, "observed": {}, "simulation": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    for name in ("margin", "accuracy"):
        sub = restrict(pop, name, idx)
        est = estimate(sub, name, check=False)
        cell = two_way_boot(est.T, est.U, sub.recipe, sub.size, seed=0)
        cell["excludes_one"] = bool(cell["lo"] is not None and cell["hi"] is not None
                                    and (cell["lo"] > 1.0 or cell["hi"] < 1.0))
        report["observed"][f"{label}/{name}"] = cell
        print(f"[obs/{label}/{name}] {json.dumps(cell)}", flush=True)


def r6_simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    rho = cell.get("rho", 0.0)
    truth = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    shared, size_shared = cell.get("recipe_shared", 0.0), cell.get("size_shared", 0.0)
    latent = np.sqrt(1 - shared - size_shared) * rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    if shared > 0:
        latent += np.sqrt(shared) * np.repeat(
            rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
    if size_shared > 0:
        # Configuration c is recipe c // sizes and band c % sizes, so the band effect tiles.
        latent += np.sqrt(size_shared) * np.tile(
            rng.multivariate_normal(np.zeros(k), truth, size=(sizes, r)), (recipes, 1, 1))
    noise = float(cell.get("noise_sd", 1.0))
    a = latent + rng.normal(size=latent.shape) * noise
    b = latent + rng.normal(size=latent.shape) * noise
    w = np.full(k, 1.0 / k)
    da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


def wild_one_way(T, U, cluster, n_boot=999, alpha=0.05, seed=0):
    T, U = np.asarray(T, float), np.asarray(U, float)
    _, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = inv.max() + 1
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
        return float("nan"), float("nan")
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    lo, hi = th - lo_q * se, th - hi_q * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


CELLS = [
 {"name": "joint_bound", "rho": 0.061, "noise_sd": 0.73, "recipe_shared": 0.114, "size_shared": 0.044},
 {"name": "band_quarter", "rho": 0.061, "noise_sd": 0.73, "recipe_shared": 0.0, "size_shared": 0.25},
]
SEED, REPS, SIZES = 20260948, 8000, 5
for ci, cell in enumerate(CELLS):
    t1 = time.time()
    acc = {"two_way_boot": 0, "wild_recipe": 0}
    bad = {"two_way_boot": 0, "wild_recipe": 0}
    paired = []
    for rep in range(REPS):
        rng = np.random.default_rng([SEED, ci + 2200, rep])
        T, U, recipe, truth = r6_simulate(cell, rng)
        band = np.arange(T.size) % SIZES
        tw = two_way_boot(T, U, recipe, band, n_boot=2999, seed=rep)
        pairs = {"two_way_boot": (tw["lo"], tw["hi"]),
                 "wild_recipe": wild_one_way(T, U, recipe, n_boot=2999, seed=rep)}
        hit = {}
        for m, (lo, hi) in pairs.items():
            if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi):
                acc[m] += lo <= truth <= hi
                hit[m] = bool(lo <= truth <= hi)
            else:
                bad[m] += 1
        # Both intervals see the same replicate, so the paired difference is what carries the comparison.
        if len(hit) == 2:
            paired.append(int(hit["two_way_boot"]) - int(hit["wild_recipe"]))
    out = {"name": cell["name"], "truth": truth, "recipe_shared": cell["recipe_shared"],
           "size_shared": cell["size_shared"], "reps": REPS}
    for m in acc:
        c = acc[m] / REPS
        out[m] = {"coverage": c, "mc_se": float(np.sqrt(c * (1 - c) / REPS)),
                  "undefined": bad[m] / REPS}
    d = np.asarray(paired, float)
    out["paired_difference"] = {
        "n": int(d.size), "mean": float(d.mean()) if d.size else None,
        "se": float(d.std(ddof=1) / np.sqrt(d.size)) if d.size > 1 else None,
        "two_way_only": int(np.sum(d > 0)), "recipe_only": int(np.sum(d < 0))}
    report["simulation"][cell["name"]] = out
    print(f"[sim/{cell['name']}] {time.time() - t1:.0f}s {json.dumps({m: out[m]['coverage'] for m in acc})}",
          flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_twoway_cov.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
