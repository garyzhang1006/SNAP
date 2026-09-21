"""R6 two-way clustering by recipe and size band, which the shipped interval doesn't do.

Design fixed before running (2026-09-15, written 22:50 EDT). The shipped interval clusters the 125
configurations by their 25 data recipes, because a recipe's seed effects plausibly repeat across the
sizes trained on it. Every configuration also sits in one of five size bands, and snap-r6-leave-one-out
just showed that the margin conclusion depends on one of them, since dropping 530M leaves an interval of
0.993 to 1.338 that no longer excludes one. A reader is entitled to ask whether an interval that ignores
the size dimension is wide enough. This run answers that with the standard two-way cluster-robust
variance of Cameron, Gelbach and Miller, which adds the recipe and size band components and subtracts
the component for their intersection, and it reports the same estimate under recipe clustering alone,
under size clustering alone, under the intersection alone, and under the two-way combination. Five size
clusters give a very short degrees-of-freedom count, so the run reports the two-way standard error beside
each one-way standard error rather than presenting a five-cluster interval as trustworthy on its own. It
covers the full battery and the battery without BoolQ on both scales. A two-way interval that still
excludes one on margins says the recipe clustering was not the load-bearing choice, and one that doesn't
is a limitation the paper has to state.
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

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)


def restrict(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, :, m], ph.B[:, :, m])
    n_items = None if p.n_items is None else np.asarray(p.n_items)[m]
    return Population({name: sub}, p.gainA, p.gainB, p.batch, p.recipe, p.size,
                      [p.traits[j] for j in m], p.config_ids, n_items)


def cluster_meat(r, labels, sU):
    """Sum of squared cluster sums of the linearised residual, scaled by the denominator sum."""
    _, inv = np.unique(np.asarray(labels), return_inverse=True)
    e = np.bincount(inv, weights=r, minlength=inv.max() + 1)
    return float(np.sum(e ** 2)) / (sU * sU), int(e.size)


def two_way(T, U, recipe, size, alpha=0.05):
    """Recipe, size, intersection and two-way standard errors of theta, with Lambda endpoints."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    pair = np.asarray([f"{a}|{b}" for a, b in zip(np.asarray(recipe), np.asarray(size))])
    v_r, g_r = cluster_meat(r, recipe, sU)
    v_s, g_s = cluster_meat(r, size, sU)
    v_i, g_i = cluster_meat(r, pair, sU)
    v_two = v_r + v_s - v_i
    out = {"theta": th, "lambda_hat": float(np.sqrt(th)) if th >= 0 else None,
           "n_recipe": g_r, "n_size": g_s, "n_intersection": g_i,
           "se_recipe": float(np.sqrt(v_r)), "se_size": float(np.sqrt(v_s)),
           "se_intersection": float(np.sqrt(v_i)),
           "se_two_way": float(np.sqrt(v_two)) if v_two > 0 else None,
           "two_way_variance_negative": bool(v_two <= 0)}
    for key, v, g in (("recipe", v_r, g_r), ("size", v_s, g_s), ("intersection", v_i, g_i),
                      ("two_way", v_two, min(g_r, g_s))):
        if v is None or v <= 0:
            out[f"interval_{key}"] = None
            continue
        crit = float(student_t.ppf(1 - alpha / 2, max(g - 1, 1)))
        lo, hi = th - crit * np.sqrt(v), th + crit * np.sqrt(v)
        out[f"interval_{key}"] = {
            "df": int(max(g - 1, 1)), "crit": crit,
            "lo": float(np.sqrt(lo)) if lo >= 0 else None,
            "hi": float(np.sqrt(hi)) if hi >= 0 else None,
            "excludes_one": bool(lo > 1.0 or hi < 1.0)}
    return out


BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
report = {"design": __doc__, "traits": TR, "batteries": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    for name in ("margin", "accuracy"):
        sub = restrict(pop, name, idx)
        est = estimate(sub, name, check=False)
        cell = two_way(est.T, est.U, sub.recipe, sub.size)
        shipped = wild_bootstrap_t(est.T, est.U, sub.recipe, n_boot=4999, seed=0)
        cell["shipped_wild"] = {"lo": float(shipped.lo), "hi": float(shipped.hi),
                                "excludes_one": bool(shipped.lo > 1.0 or shipped.hi < 1.0)}
        cell["se_ratio_two_way_over_recipe"] = (cell["se_two_way"] / cell["se_recipe"]
                                                if cell["se_two_way"] else None)
        report["batteries"][f"{label}/{name}"] = cell
        print(f"[{label}/{name}] {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_twoway.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
