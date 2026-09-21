"""R8 sensitivity of the log-scale prediction comparison to the treatment of nonpositive held-out variances.

Design fixed before running (2026-09-15, written 18:50 EDT). The plan says clipping negative held-out
variances isn't neutral merely because every model receives it, and asks for a sensitivity analysis under a
justified alternative. Models P0, P1, P1g, P3 on the table's five recipe folds (seed 0) and in a 2,000-draw
full-refit recipe bootstrap built exactly as in snap-r8-paired-log (seed 0).
Rules for a trait whose held-out pooled seed variance is nonpositive in a fold:
  clip        the shipped rule, variance set to zero for prediction, target unchanged (must reproduce bakeoff);
  drop        remove that trait from the fold's prediction, its training correlation, and its target;
  train_fill  replace that held-out variance with the training-fold pooled variance of the trait.
Report the traits affected in each fold, each rule's MSE, and the paired intervals for P1-P0, P3-P0,
P1g-P0, and P1-P3.
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
from seednoise.estimator import sigma_e  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125
PHENS = ("margin", "accuracy")
MODELS = ("P0", "P1", "P1g", "P3")
RULES = ("clip", "drop", "train_fill")
CONTRASTS = [("P1", "P0"), ("P3", "P0"), ("P1g", "P0"), ("P1", "P3")]
CORR = {"P0": BASELINES["P0"][1], "P1": BASELINES["P1"][1], "P1g": BASELINES["P1g"][1], "P3": BASELINES["P3"][1]}


def keep_traits(p, keep):
    ph = {k: Phenotype(v.name, v.A[:, :, keep], v.B[:, :, keep]) for k, v in p.phenotypes.items()}
    return Population(ph, p.gainA, p.gainB, p.batch, p.recipe, p.size, [p.traits[i] for i in keep], p.config_ids,
                      None if p.n_items is None else np.asarray(p.n_items)[keep])


def fold_errors(train, test, name, rule):
    """Squared log errors of the four models under one rule for nonpositive held-out variances."""
    d_test = np.diag(sigma_e(test, name)); bad = np.flatnonzero(d_test <= 0)
    info = {"nonpositive": [test.traits[j] for j in bad]}
    if rule == "drop" and bad.size:
        keep = [j for j in range(test.K) if j not in set(bad.tolist())]
        train, test = keep_traits(train, keep), keep_traits(test, keep)
        d_test = np.diag(sigma_e(test, name))
    obs = observed_sigma_agg(test, name)
    if rule == "train_fill":
        d_train = np.diag(sigma_e(train, name))
        d_use = np.where(d_test > 0, d_test, np.clip(d_train, 0.0, None))
    else:
        d_use = np.clip(d_test, 0.0, None)
    sd = np.sqrt(d_use)
    out = {}
    for m in MODELS:
        R = np.asarray(CORR[m](train, test, name), float); R = np.where(np.isfinite(R), R, 0.0); np.fill_diagonal(R, 1.0)
        v = float((np.outer(sd, sd) * R).sum()) / test.K ** 2
        pred = float(np.sqrt(v)) if v > 0 else float("nan")
        ok = np.isfinite(obs) and np.isfinite(pred) and obs > 0 and pred > 0
        out[m] = float((np.log(pred) - np.log(obs)) ** 2) if ok else float("nan")
    return out, info


def run(p, folds, name, rule):
    errs = {m: [] for m in MODELS}; infos = []
    for held, trn in folds:
        e, info = fold_errors(p.subset_clusters(trn), p.subset_clusters(held), name, rule)
        for m in MODELS:
            errs[m].append(e[m])
        infos.append(info)
    return {m: float(np.nanmean(v)) for m, v in errs.items()}, errs, infos


recipes = np.unique(pop.recipe)
rng0 = np.random.default_rng(0); base_folds = [(h, np.setdiff1d(recipes, h)) for h in np.array_split(rng0.permutation(recipes), 5)]
report = {"design": __doc__, "folds": {}, "bootstrap": {}}
for name in PHENS:
    ref = {r["model"]: r["mse_log_sigma_agg"] for r in bakeoff(pop, name, n_folds=5, seed=0)}
    report["folds"][name] = {}
    for rule in RULES:
        mse, errs, infos = run(pop, base_folds, name, rule)
        if rule == "clip":
            assert all(abs(mse[m] - ref[m]) < 1e-12 for m in MODELS), (mse, ref)
        report["folds"][name][rule] = {"mse": mse, "fold_errors": errs, "nonpositive_by_fold": infos}
        print(f"[{name} {rule}] {json.dumps({m: round(v, 4) for m, v in mse.items()})} nonpositive {[i['nonpositive'] for i in infos]}", flush=True)
    t1 = time.time(); rng = np.random.default_rng(0); B = {rule: [] for rule in RULES}
    for b in range(2000):
        draw = rng.choice(recipes, size=recipes.size, replace=True); uniq = np.unique(draw)
        if uniq.size < 5:
            continue
        groups = np.array_split(rng.permutation(uniq), 5)
        folds = [(draw[np.isin(draw, g)], draw[~np.isin(draw, g)]) for g in groups]
        for rule in RULES:
            B[rule].append(run(pop, folds, name, rule)[0])
    report["bootstrap"][name] = {}
    for rule in RULES:
        M = {m: np.array([x[m] for x in B[rule]]) for m in MODELS}
        report["bootstrap"][name][rule] = {"draws": len(B[rule]), "contrasts": {}}
        for a, c in CONTRASTS:
            d = M[a] - M[c]; d = d[np.isfinite(d)]
            report["bootstrap"][name][rule]["contrasts"][f"{a}-{c}"] = {
                "observed": report["folds"][name][rule]["mse"][a] - report["folds"][name][rule]["mse"][c],
                "p025": float(np.percentile(d, 2.5)), "p975": float(np.percentile(d, 97.5)), "share_below_zero": float(np.mean(d < 0)), "n": int(d.size)}
        print(f"[bootstrap {name} {rule}] {time.time() - t1:.0f}s " + json.dumps({k: (round(v['p025'], 4), round(v['p975'], 4)) for k, v in report['bootstrap'][name][rule]['contrasts'].items()}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r8_clipping.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
