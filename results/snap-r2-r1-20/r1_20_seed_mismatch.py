"""snap-r2-r1-20 (CPU only): the k05 decision analysis with single-run, seed-mismatched recipe pairs.

Base: compute extra/heldout/kaggle/k05-decision/k05-decision.py, unchanged in its
population (the 375 shipped reduced runs, seednoise.build.build_population, the
Lambda 1.24395 assertion), its leave-pair-out sigmas (seednoise.estimator.estimate
sigma_indep and sigma_agg on the size band without the pair's two recipes) and
its truth (the 1B gap of three-seed recipe means, resolved when it exceeds two
corrected standard errors, leave-pair-out).

Change. k05 compares three-seed recipe means, whose gap is the same under any
seed pairing, so seed labels can only matter for single runs. Here every pair
(a, b) at a size below 1B is compared run against run: gap = agg(a, seed i) -
agg(b, seed j), called when |gap| > 2 * sqrt(2) * sigma, with sigma from
independence or from the covariance estimate. Seed-matched comparisons use
i = j (3 per pair) and seed-mismatched comparisons use i != j (6 per pair).
build_population sorts each configuration's runs by batch label, so index i
names the same seed label in every configuration; the script checks that and
records the labels.

Reported per phenotype, size, pairing and method: calls, calls on resolved
pairs, wrong-sign calls, wrong-call rate, power, with a 2,000-draw recipe-cluster
bootstrap (weights count_a * count_b, sigmas held fixed, as in k05) for each
rate and for the independence-minus-corrected wrong-rate difference. Also the
empirical mean squared single-run deviation difference, matched against
mismatched, as a direct read of how much a shared seed label cancels.
"""
import itertools
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402

N_BOOT = 2000
shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
old_dir = Path("/kaggle/tmp") / "runs_shipped"
shutil.rmtree(old_dir, ignore_errors=True)
old_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, old_dir / p.name)
pop, info = build_population(old_dir, TRAITS, n_runs=3)
lam = estimate(pop, MARGIN).lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"
sizes, recipes, R = info["sizes"], info["recipes"], pop.R
print(f"[pop] N={pop.N} sizes {sizes}, {len(recipes)} recipes, margin Lambda {lam:.5f}", flush=True)

batch_check = {}
for s, z in enumerate(sizes):
    rows = pop.batch[pop.size == s]
    batch_check[z] = {"identical_labels_across_recipes": bool(np.all(rows == rows[0])),
                      "labels_first_config": rows[0].tolist(), "distinct_label_rows": int(np.unique(rows, axis=0).shape[0])}
print("[batch]", batch_check, flush=True)


def at(size_name, name):
    idx = np.flatnonzero(pop.size == sizes.index(size_name))
    sub = pop.subset(idx)
    ph = sub.pheno(name)
    run_agg = ((ph.A + ph.B) / 2).mean(axis=2)          # (n, R) per-run aggregate
    return sub, {int(sub.recipe[i]): run_agg[i] for i in range(sub.N)}


def sigmas_without(sub, name, a, b):
    keep = np.flatnonzero((sub.recipe != a) & (sub.recipe != b))
    e = estimate(sub.subset(keep), name, check=False)
    return e.sigma_indep, e.sigma_agg


se_mean = lambda s: math.sqrt(2.0 / R) * s  # noqa: E731  (k05's truth rule on three-seed means)
se_run = lambda s: math.sqrt(2.0) * s       # noqa: E731  (one run against one run)
top = "1B"
results, msd = {}, {}
for name in (MARGIN, ACCURACY):
    top_sub, top_runs = at(top, name)
    truth = {}
    for a, b in itertools.combinations(sorted(top_runs), 2):
        _, s_agg = sigmas_without(top_sub, name, a, b)
        gap = top_runs[a].mean() - top_runs[b].mean()
        truth[(a, b)] = (np.sign(gap), abs(gap) > 2 * se_mean(s_agg))
    for size in [z for z in sizes if z != top]:
        sub, runs = at(size, name)
        present = sorted(set(runs) & set(top_runs))
        rec = []   # one row per (pair, i, j)
        sq = {"matched": [], "mismatched": []}
        for a, b in itertools.combinations(present, 2):
            s_ind, s_agg = sigmas_without(sub, name, a, b)
            sign_top, resolved = truth[(a, b)]
            da, db = runs[a] - runs[a].mean(), runs[b] - runs[b].mean()
            for i in range(R):
                for j in range(R):
                    kind = "matched" if i == j else "mismatched"
                    gap = runs[a][i] - runs[b][j]
                    sq[kind].append((da[i] - db[j]) ** 2)
                    row = {"ia": a, "ib": b, "kind": kind, "resolved": bool(resolved)}
                    for method, s in (("independence", s_ind), ("corrected", s_agg)):
                        called = abs(gap) > 2 * se_run(s)
                        row[f"{method}_called"] = bool(called)
                        row[f"{method}_wrong"] = bool(called and resolved and np.sign(gap) != sign_top)
                        row[f"{method}_right"] = bool(called and resolved and np.sign(gap) == sign_top)
                    rec.append(row)
        ia = np.array([r["ia"] for r in rec]); ib = np.array([r["ib"] for r in rec])
        kind = np.array([r["kind"] for r in rec]); res = np.array([r["resolved"] for r in rec])
        arr = {f"{m}_{k}": np.array([r[f"{m}_{k}"] for r in rec]) for m in ("independence", "corrected") for k in ("called", "wrong", "right")}

        def summarise(w):
            out = {}
            for kd in ("matched", "mismatched"):
                sel = kind == kd
                o = {}
                for m in ("independence", "corrected"):
                    c, wr, rt = arr[f"{m}_called"] & sel, arr[f"{m}_wrong"] & sel, arr[f"{m}_right"] & sel
                    cr = float(w[c & res].sum())
                    o[m] = {"calls": float(w[c].sum()), "calls_on_resolved": cr, "wrong": float(w[wr].sum()),
                            "wrong_rate": float(w[wr].sum()) / cr if cr else float("nan"),
                            "power": float(w[rt].sum()) / float(w[sel & res].sum()) if w[sel & res].sum() else float("nan")}
                out[kd] = o
            return out

        point = summarise(np.ones(len(rec)))
        rng = np.random.default_rng(20260923)
        boot = {(kd, m, k): [] for kd in ("matched", "mismatched") for m in ("independence", "corrected") for k in ("wrong_rate", "power")}
        diffs = {kd: [] for kd in ("matched", "mismatched")}
        mm = {m: [] for m in ("independence", "corrected")}
        for _ in range(N_BOOT):
            draw = rng.choice(present, size=len(present), replace=True)
            cnt = np.bincount(draw, minlength=max(present) + 1)
            s = summarise((cnt[ia] * cnt[ib]).astype(float))
            for (kd, m, k) in boot:
                boot[(kd, m, k)].append(s[kd][m][k])
            for kd in diffs:
                diffs[kd].append(s[kd]["independence"]["wrong_rate"] - s[kd]["corrected"]["wrong_rate"])
            for m in mm:
                mm[m].append(s["mismatched"][m]["wrong_rate"] - s["matched"][m]["wrong_rate"])
        ci = lambda v: [float(np.nanquantile(v, 0.025)), float(np.nanquantile(v, 0.975))]  # noqa: E731
        for (kd, m, k), vals in boot.items():
            point[kd][m][f"{k}_ci95"] = ci(vals)
        for kd in diffs:
            point[kd]["wrong_rate_independence_minus_corrected"] = point[kd]["independence"]["wrong_rate"] - point[kd]["corrected"]["wrong_rate"]
            point[kd]["wrong_rate_independence_minus_corrected_ci95"] = ci(diffs[kd])
        point["mismatched_minus_matched_wrong_rate"] = {
            m: {"point": point["mismatched"][m]["wrong_rate"] - point["matched"][m]["wrong_rate"], "ci95": ci(mm[m])} for m in mm}
        full = estimate(sub, name, check=False)
        exp_ind = 2 * (R - 1) / R * full.sigma_indep ** 2
        exp_agg = 2 * (R - 1) / R * full.sigma_agg ** 2
        msd.setdefault(name, {})[size] = {
            "mean_sq_dev_diff_matched": float(np.mean(sq["matched"])), "mean_sq_dev_diff_mismatched": float(np.mean(sq["mismatched"])),
            "sd_ratio_matched_over_mismatched": float(np.sqrt(np.mean(sq["matched"]) / np.mean(sq["mismatched"]))),
            "sd_ratio_mismatched_over_corrected_expectation": float(np.sqrt(np.mean(sq["mismatched"]) / exp_agg)),
            "sd_ratio_mismatched_over_independence_expectation": float(np.sqrt(np.mean(sq["mismatched"]) / exp_ind)),
            "sd_ratio_matched_over_independence_expectation": float(np.sqrt(np.mean(sq["matched"]) / exp_ind)),
            "band_sigma_indep": full.sigma_indep, "band_sigma_agg": full.sigma_agg, "pairs": len(present) * (len(present) - 1) // 2}
        results.setdefault(name, {})[size] = point
        print(f"[{name} {size}] matched indep {point['matched']['independence']['wrong_rate']:.3f} corr {point['matched']['corrected']['wrong_rate']:.3f} | "
              f"mismatched indep {point['mismatched']['independence']['wrong_rate']:.3f} corr {point['mismatched']['corrected']['wrong_rate']:.3f} | "
              f"sd ratio m/mm {msd[name][size]['sd_ratio_matched_over_mismatched']:.3f}", flush=True)

out = {"results": results, "paired_deviation": msd, "batch_check": batch_check, "n_boot": N_BOOT, "seeds_per_recipe": R,
       "comparison": "single run against single run, SE sqrt(2)*sigma, sigma leave-pair-out from seednoise.estimator.estimate",
       "truth": "k05 rule: 1B three-seed mean gap beyond two corrected standard errors, leave-pair-out",
       "note": "sigmas held fixed inside the recipe bootstrap; exploratory", "wall_seconds": time.time() - t0}
(W / "r1_20_seed_mismatch.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
