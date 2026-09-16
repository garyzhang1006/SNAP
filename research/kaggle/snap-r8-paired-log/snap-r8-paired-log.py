"""R8 paired uncertainty for the log-scale prediction comparison (Table tab:prediction).

Design fixed before running (2026-09-15, 18:00 EDT). Inputs are the 375 shipped reduced runs.
1. Reproduce seednoise.baselines.bakeoff(pop, phenotype, n_folds=5, seed=0) for P0, P1, P1g, P2, P3
   (reported 0.0358, 0.0057, 0.0063, 0.1073, 0.0068 margin and 0.0143, 0.0140, 0.0260, 0.1682, 0.0105
   accuracy) and the exploratory P2R, which multiplies the held-out R_P off-diagonals by the training
   ratio of mean off-diagonal R_E to mean off-diagonal R_P (reported 0.0131 and 0.0342, factors 0.366
   and 0.370). Save each fold's prediction, observed target, and squared log error.
2. Paired contrasts fixed now: P1-P0, P3-P0, P1g-P0, P2R-P0, P1-P3, P1g-P1, P2R-P1, P2R-P3.
   A negative contrast favours the first model. The practically meaningful difference is 0.005 in
   mean squared log error, which is the squared error of a 7 percent error in the aggregate SD.
3. Partition sensitivity: the same six models on 1,000 random five-fold recipe partitions (seeds 1 to
   1,000), recording each model's MSE, the paired contrasts, and how often each model has the lowest MSE.
4. Full-refit recipe-cluster bootstrap, 2,000 draws with seed 0. Each draw resamples the 25 recipes with
   replacement and assigns folds over the distinct original recipes, so copies of one recipe never sit
   in both the training and the held-out set. The whole five-fold comparison is refitted in each draw.
   Report percentile 2.5 and 97.5 of each contrast, the share of draws below zero, and the share below
   minus 0.005. This interval also integrates fold-partition variation, and it treats recipes as
   exchangeable clusters, which the designed collection of 25 recipes doesn't guarantee.
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

from seednoise.baselines import BASELINES, bakeoff, observed_sigma_agg, predict_sigma_agg  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import correlation, phenotypic_correlation, sigma_e  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125
PHENS = ("margin", "accuracy")
MODELS = ("P0", "P1", "P1g", "P2", "P3", "P2R")
CONTRASTS = [("P1", "P0"), ("P3", "P0"), ("P1g", "P0"), ("P2R", "P0"), ("P1", "P3"), ("P1g", "P1"), ("P2R", "P1"), ("P2R", "P3")]
MEANINGFUL = 0.005
OFF = ~np.eye(pop.K, dtype=bool)


def p2r(train, test, name):
    RE = correlation(sigma_e(train, name)); RPtr = phenotypic_correlation(train, name)
    factor = float(np.nanmean(RE[OFF]) / np.nanmean(RPtr[OFF]))
    R = phenotypic_correlation(test, name) * factor
    np.fill_diagonal(R, 1.0)
    sd = np.sqrt(np.clip(np.diag(sigma_e(test, name)), 0.0, None))
    R = np.where(np.isfinite(R), R, 0.0)
    v = float((np.outer(sd, sd) * R).sum()) / test.K ** 2
    return (float(np.sqrt(v)) if v > 0 else float("nan")), factor


def run_folds(p, folds, name):
    """Five-fold comparison on population p with folds given as lists of recipe draws."""
    out = {m: [] for m in MODELS}; factors = []
    for held_draws, train_draws in folds:
        test = p.subset_clusters(held_draws); train = p.subset_clusters(train_draws)
        obs = observed_sigma_agg(test, name)
        for m in MODELS:
            if m == "P2R":
                pred, f = p2r(train, test, name); factors.append(f)
            else:
                pred = predict_sigma_agg(train, test, name, m)
            ok = np.isfinite(obs) and np.isfinite(pred) and obs > 0 and pred > 0
            out[m].append({"pred": pred, "obs": obs, "se": float((np.log(pred) - np.log(obs)) ** 2) if ok else float("nan")})
    return out, factors


def mse(rows):
    v = np.array([r["se"] for r in rows]); v = v[np.isfinite(v)]
    return float(v.mean()) if v.size else float("nan")


def partition(recipes, seed):
    rng = np.random.default_rng(seed)
    fs = np.array_split(rng.permutation(recipes), 5)
    return [(held, np.setdiff1d(recipes, held)) for held in fs]


recipes = np.unique(pop.recipe)
report = {"design": __doc__, "meaningful_difference": MEANINGFUL, "reproduction": {}, "fold_level": {}, "partitions": {}, "bootstrap": {}}
for name in PHENS:
    ref = {r["model"]: r["mse_log_sigma_agg"] for r in bakeoff(pop, name, n_folds=5, seed=0)}
    rows, factors = run_folds(pop, partition(recipes, 0), name)
    rep = {m: mse(rows[m]) for m in MODELS}
    assert all(abs(rep[m] - ref[m]) < 1e-12 for m in BASELINES), (rep, ref)
    report["reproduction"][name] = {"bakeoff": ref, "this_code": rep, "p2r_factors": factors, "p2r_mean_factor": float(np.mean(factors))}
    report["fold_level"][name] = {m: rows[m] for m in MODELS}
    report["fold_level"][name]["contrasts"] = {f"{a}-{b}": [ra["se"] - rb["se"] for ra, rb in zip(rows[a], rows[b])] for a, b in CONTRASTS}
    print(f"[repro {name}] {json.dumps({m: round(v, 4) for m, v in rep.items()})} factor {np.mean(factors):.3f}", flush=True)

    t1 = time.time(); P = []
    for s in range(1, 1001):
        r, _ = run_folds(pop, partition(recipes, s), name)
        P.append({m: mse(r[m]) for m in MODELS})
    M = {m: np.array([x[m] for x in P]) for m in MODELS}
    best = np.array([min(MODELS, key=lambda m: x[m] if np.isfinite(x[m]) else np.inf) for x in P])
    report["partitions"][name] = {
        "n": len(P), "mse_quantiles": {m: [float(np.nanpercentile(M[m], q)) for q in (2.5, 50, 97.5)] for m in MODELS},
        "share_lowest": {m: float(np.mean(best == m)) for m in MODELS},
        "contrasts": {f"{a}-{b}": {"median": float(np.nanmedian(M[a] - M[b])), "p025": float(np.nanpercentile(M[a] - M[b], 2.5)),
                                   "p975": float(np.nanpercentile(M[a] - M[b], 97.5)), "share_below_zero": float(np.nanmean((M[a] - M[b]) < 0))}
                      for a, b in CONTRASTS}}
    print(f"[partitions {name}] {time.time() - t1:.0f}s lowest {json.dumps(report['partitions'][name]['share_lowest'])}", flush=True)

    t1 = time.time(); rng = np.random.default_rng(0); B = []; skipped = 0
    for b in range(2000):
        draw = rng.choice(recipes, size=recipes.size, replace=True)
        uniq = np.unique(draw)
        if uniq.size < 5:
            skipped += 1; continue
        groups = np.array_split(rng.permutation(uniq), 5)
        folds = [(draw[np.isin(draw, g)], draw[~np.isin(draw, g)]) for g in groups]
        r, _ = run_folds(pop, folds, name)
        B.append({m: mse(r[m]) for m in MODELS})
    MB = {m: np.array([x[m] for x in B]) for m in MODELS}
    report["bootstrap"][name] = {
        "draws_used": len(B), "draws_skipped": skipped,
        "mse_quantiles": {m: [float(np.nanpercentile(MB[m], q)) for q in (2.5, 50, 97.5)] for m in MODELS},
        "contrasts": {}}
    for a, b in CONTRASTS:
        d = MB[a] - MB[b]; d = d[np.isfinite(d)]
        report["bootstrap"][name]["contrasts"][f"{a}-{b}"] = {
            "observed": report["reproduction"][name]["this_code"][a] - report["reproduction"][name]["this_code"][b],
            "n_finite": int(d.size), "p025": float(np.percentile(d, 2.5)), "p975": float(np.percentile(d, 97.5)),
            "share_below_zero": float(np.mean(d < 0)), "share_below_minus_meaningful": float(np.mean(d < -MEANINGFUL)),
            "share_above_meaningful": float(np.mean(d > MEANINGFUL))}
    print(f"[bootstrap {name}] {time.time() - t1:.0f}s " + json.dumps({k: (round(v['p025'], 4), round(v['p975'], 4)) for k, v in report['bootstrap'][name]['contrasts'].items()}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r8_paired_log.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
