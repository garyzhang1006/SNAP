"""k05 (CPU, no GPU): what the correlated-noise correction changes about real decisions.

Uses only the 375 shipped reduced runs and seednoise at the paper's commit.

Setting. A practitioner trains every recipe at a small size with three seeds
and ranks recipe pairs by the gap in aggregate score (mean over the ten traits),
calling a pair when the gap exceeds two standard errors. The standard error
comes either from the independence assumption (sigma_indep, the estimator's U)
or from the correlated-noise estimate (sigma_agg, the estimator's T). For every
pair the sigmas are estimated at that size with the pair's own two recipes left
out, so a pair's call never uses its own noise.

Truth is the same pair at 1B: resolved when the 1B gap exceeds two corrected
standard errors (again leaving the pair out), with the 1B sign as the answer.

Reported per size below 1B, per phenotype, per method:
  calls, calls on resolved pairs, wrong-sign calls, wrong-call rate among
  resolved calls, calls on unresolved pairs, power (correct calls / resolved).
Uncertainty: a recipe-cluster bootstrap (2,000 draws) over the precomputed pair
outcomes; sigmas are not re-estimated inside the bootstrap, which the output
says.

Seed-count rule. For each size and method, the seeds per recipe needed for a
two-standard-error call on a gap delta, n = ceil(2 * (2 * sigma / delta)^2), at
delta equal to the 25th and 50th percentile of observed absolute gaps.

Everything here is exploratory unless PROTOCOL_heldout.md lists it as
pre-registered before this kernel ran.
"""
import csv
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
# The build writes next to the sources, and /kaggle/input is read-only, so the
# tree is copied out first, exactly as the earlier kernels in compute extra/research_kernels do.
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402

N_BOOT = 2000
# The shipped dataset carries a macOS metadata twin for every run, and those
# 163-byte files are not loadable npz, so only the real ones are copied out.
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
sizes = info["sizes"]
recipes = info["recipes"]
R = pop.R
print(f"[pop] N={pop.N} sizes {sizes}, {len(recipes)} recipes, margin Lambda {lam:.5f}", flush=True)


def at(size_name, name):
    """Per-recipe aggregate score at one size and the sub-population there."""
    idx = np.flatnonzero(pop.size == sizes.index(size_name))
    sub = pop.subset(idx)
    ph = sub.pheno(name)
    agg = ((ph.A + ph.B) / 2).mean(axis=(1, 2))
    return sub, {int(sub.recipe[i]): float(agg[i]) for i in range(sub.N)}


def sigmas_without(sub, name, a, b):
    keep = np.flatnonzero((sub.recipe != a) & (sub.recipe != b))
    e = estimate(sub.subset(keep), name, check=False)
    return e.sigma_indep, e.sigma_agg


se = lambda s: math.sqrt(2.0 / R) * s  # noqa: E731
results, pair_rows, seed_rule = {}, [], {}
top = "1B"
for name in (MARGIN, ACCURACY):
    top_sub, top_score = at(top, name)
    truth = {}
    for a, b in itertools.combinations(sorted(top_score), 2):
        _, s_agg = sigmas_without(top_sub, name, a, b)
        gap = top_score[a] - top_score[b]
        truth[(a, b)] = (np.sign(gap), abs(gap) > 2 * se(s_agg), gap)
    for size in [z for z in sizes if z != top]:
        sub, score = at(size, name)
        rows = []
        for a, b in itertools.combinations(sorted(set(score) & set(top_score)), 2):
            s_ind, s_agg = sigmas_without(sub, name, a, b)
            gap = score[a] - score[b]
            sign_top, resolved, gap_top = truth[(a, b)]
            row = {"phenotype": name, "size": size, "a": recipes[a], "b": recipes[b], "ia": a, "ib": b,
                   "gap": gap, "gap_1B": gap_top, "resolved_1B": bool(resolved),
                   "sigma_indep": s_ind, "sigma_agg": s_agg}
            for method, s in (("independence", s_ind), ("corrected", s_agg)):
                called = abs(gap) > 2 * se(s)
                row[f"{method}_called"] = bool(called)
                row[f"{method}_wrong"] = bool(called and resolved and np.sign(gap) != sign_top)
                row[f"{method}_right"] = bool(called and resolved and np.sign(gap) == sign_top)
            rows.append(row)
        pair_rows += rows

        def summarise(weights):
            out = {}
            w = np.asarray(weights, float)
            res = np.asarray([r["resolved_1B"] for r in rows])
            for method in ("independence", "corrected"):
                c = np.asarray([r[f"{method}_called"] for r in rows])
                wr = np.asarray([r[f"{method}_wrong"] for r in rows])
                rt = np.asarray([r[f"{method}_right"] for r in rows])
                calls_res = float(w[c & res].sum())
                out[method] = {"calls": float(w[c].sum()), "calls_on_resolved": calls_res,
                               "wrong": float(w[wr].sum()), "calls_on_unresolved": float(w[c & ~res].sum()),
                               "wrong_rate": float(w[wr].sum()) / calls_res if calls_res else float("nan"),
                               "power": float(w[rt].sum()) / float(w[res].sum()) if w[res].sum() else float("nan")}
            return out

        point = summarise(np.ones(len(rows)))
        rng = np.random.default_rng(20260917)
        present = sorted(set(score) & set(top_score))
        boot = {m: {"wrong_rate": [], "power": []} for m in ("independence", "corrected")}
        diff = []
        for _ in range(N_BOOT):
            draw = rng.choice(present, size=len(present), replace=True)
            cnt = {r: int((draw == r).sum()) for r in present}
            s = summarise([cnt[r["ia"]] * cnt[r["ib"]] for r in rows])
            for m in boot:
                for k in boot[m]:
                    boot[m][k].append(s[m][k])
            diff.append(s["independence"]["wrong_rate"] - s["corrected"]["wrong_rate"])
        ci = lambda v: [float(np.nanquantile(v, 0.025)), float(np.nanquantile(v, 0.975))]  # noqa: E731
        for m in boot:
            for k in boot[m]:
                point[m][f"{k}_ci95"] = ci(boot[m][k])
        point["wrong_rate_independence_minus_corrected_ci95"] = ci(diff)
        results.setdefault(name, {})[size] = point

        gaps = np.abs([r["gap"] for r in rows])
        s_ind_all = estimate(sub, name, check=False)
        rule = {}
        for q in (25, 50):
            delta = float(np.percentile(gaps, q))
            rule[f"p{q}_gap"] = {"delta": delta,
                                 "seeds_independence": math.ceil(2 * (2 * s_ind_all.sigma_indep / delta) ** 2),
                                 "seeds_corrected": math.ceil(2 * (2 * s_ind_all.sigma_agg / delta) ** 2)}
        seed_rule.setdefault(name, {})[size] = rule
        print(f"[{name} {size}] indep wrong {point['independence']['wrong_rate']:.3f} power {point['independence']['power']:.3f} | "
              f"corrected wrong {point['corrected']['wrong_rate']:.3f} power {point['corrected']['power']:.3f}", flush=True)

out = {"results": results, "seed_count_rule": seed_rule, "n_boot": N_BOOT, "seeds_per_recipe": R,
       "note": "sigmas are estimated leave-pair-out once and held fixed inside the recipe bootstrap",
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md", "wall_seconds": time.time() - t0}
(W / "decision_results.json").write_text(json.dumps(out, indent=1))
with open(W / "decision_pairs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(pair_rows[0]))
    w.writeheader()
    w.writerows(pair_rows)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=False)
small = [z for z in sizes if z != top]
for ax, name in zip(axes, (MARGIN, ACCURACY)):
    x = np.arange(len(small))
    for off, m, label in ((-0.15, "independence", "independence SE"), (0.15, "corrected", r"$\hat\Lambda$-corrected SE")):
        y = [results[name][z][m]["wrong_rate"] for z in small]
        lo = [results[name][z][m]["wrong_rate_ci95"][0] for z in small]
        hi = [results[name][z][m]["wrong_rate_ci95"][1] for z in small]
        ax.errorbar(x + off, y, yerr=[np.subtract(y, lo), np.subtract(hi, y)], fmt="o", capsize=3, label=label)
    ax.set_xticks(x, small)
    ax.set_title(name)
    ax.set_xlabel("decision size")
axes[0].set_ylabel("wrong-sign calls / calls on pairs resolved at 1B")
axes[1].legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(W / "decision_wrong_calls.pdf")
fig.savefig(W / "decision_wrong_calls.png", dpi=200)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
