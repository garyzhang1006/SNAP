"""snap-r8-split-vs-rep (CPU only): decisions whose verdict depends on the uncertainty estimator.

Rebuttal row R6-S (CPU exploratory item) and AR-S1: the replicate SD of the
battery average needs no item split, so is there any recipe or size decision on
the released DataDecide runs where using the split-half estimate instead of the
replicate estimate changes the verdict?

The two estimators of the per-run SD of the battery average (sigma below):
  split       seednoise.estimator.estimate(pop, name).sigma_agg on the split-half
              population from seednoise.build.build_population, i.e. sqrt of the mean
              over configurations of the cross-half product of aggregate deviations
              (the k05 "corrected" sigma, compute extra/heldout/kaggle/k05-decision/k05-decision.py:87-90)
  replicate   the same function on the fixed-bank population with half A = half B =
              full-bank trait scores, which makes it the replicate SD of the full-bank
              battery average with an R-1 divisor
              (results/snap-r2-r1-08/r1_08_fixed_bank.py:67-74)

Decision rules, both taken from k05 with only sigma swapped:
  recipe pair (a, b) at one size: call when |gap| > 2 * sqrt(2/R) * sigma, sigma
      estimated on that size band with a and b left out (k05-decision.py:87-93, 107-114).
  size step for one recipe (size s to the next size s'): call when
      |gap| > 2 * sqrt((sigma_s^2 + sigma_s'^2) / R), each sigma on its own band with
      the recipe left out. This rule is new here and follows the same two-SE logic.
  seed count (k05-decision.py:156-164): n = ceil(2 * (2 * sigma / delta)^2) at delta equal
      to the 25th and 50th percentile of absolute recipe-pair gaps on the band.
The gap is the full-bank battery average (mean over the kept traits of the full-bank
trait scores, averaged over the R runs). k05 used the mean of the two half scores
instead, and calls under that gap are recorded too.

Batteries: all ten benchmarks, and each single-benchmark removal (no_boolq is the
one AR-S1 names). Phenotypes: margin and accuracy. For each recipe-pair disagreement
below 1B the 1B verdict is attached, resolved under either sigma (k05 truth rule,
leave-pair-out). Everything is exploratory.
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
from seednoise.phenotypes import half_scores  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402
from seednoise.store import load_run  # noqa: E402

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
run_dir = Path("/kaggle/tmp") / "runs_shipped"
shutil.rmtree(run_dir, ignore_errors=True)
run_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, run_dir / p.name)
pop, info = build_population(run_dir, TRAITS, n_runs=3)
lam = estimate(pop, MARGIN).lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"
K, R = len(TRAITS), pop.R
sizes, recipes = info["sizes"], info["recipes"]

# Fixed-bank population, built exactly as r1_08_fixed_bank.py:58-74.
cells = {}
for f in sorted(run_dir.glob("*.npz")):
    items, meta = load_run(f)
    m, a = half_scores(items, np.ones(items.n_items, dtype=bool), K)
    cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, m, a))
keys = [tuple(c) for c in pop.config_ids]
assert all(len(cells[k]) == R for k in keys), "a configuration in the population lacks three runs here"
M = np.zeros((pop.N, R, K)); A = np.zeros((pop.N, R, K)); batch = np.zeros((pop.N, R), dtype=np.int64)
for c, k in enumerate(keys):
    for r, (meta, m, a) in enumerate(sorted(cells[k], key=lambda t: t[0]["batch"])):
        M[c, r], A[c, r], batch[c, r] = m, a, meta["batch"]
assert np.array_equal(batch, pop.batch), "run order differs from build_population"
fixed = Population({MARGIN: Phenotype(MARGIN, M, M), ACCURACY: Phenotype(ACCURACY, A, A)},
                   batch=batch, recipe=pop.recipe, size=pop.size, traits=list(TRAITS),
                   config_ids=pop.config_ids)


def keep_traits(p, drop):
    idx = [j for j, t in enumerate(p.traits) if t not in drop]
    ph = {n: Phenotype(n, v.A[:, :, idx], v.B[:, :, idx]) for n, v in p.phenotypes.items()}
    return Population(ph, batch=p.batch, recipe=p.recipe, size=p.size, traits=[p.traits[j] for j in idx], config_ids=p.config_ids)


def band(p, s):
    return p.subset(np.flatnonzero(p.size == sizes.index(s)))


def sigma_without(sub, name, drop_recipes):
    keep = np.flatnonzero(~np.isin(sub.recipe, list(drop_recipes)))
    return estimate(sub.subset(keep), name, check=False).sigma_agg


def scores(sub, name):
    """Per-recipe battery average: full-bank (from the fixed population) and k05's half mean."""
    return {int(sub.recipe[i]): float(sub.pheno(name).A[i].mean()) for i in range(sub.N)}


def half_scores_k05(sub, name):
    ph = sub.pheno(name)
    agg = ((ph.A + ph.B) / 2).mean(axis=(1, 2))
    return {int(sub.recipe[i]): float(agg[i]) for i in range(sub.N)}


se_pair = lambda s: math.sqrt(2.0 / R) * s  # noqa: E731
batteries = [("all_ten", ())] + [(f"no_{t}", (t,)) for t in TRAITS]
sanity, summary, cases, seed_rule = {}, {}, [], {}
for bname, drop in batteries:
    sp_all, fx_all = keep_traits(pop, drop), keep_traits(fixed, drop)
    for name in (MARGIN, ACCURACY):
        es, ef = estimate(sp_all, name, check=False), estimate(fx_all, name, check=False)
        sanity.setdefault(bname, {})[name] = {"lambda_split": es.lambda_hat, "lambda_fixed_bank": ef.lambda_hat,
                                              "sigma_agg_split": es.sigma_agg, "sigma_agg_replicate": ef.sigma_agg}
        sp_b = {s: band(sp_all, s) for s in sizes}
        fx_b = {s: band(fx_all, s) for s in sizes}
        full = {s: scores(fx_b[s], name) for s in sizes}
        halfm = {s: half_scores_k05(sp_b[s], name) for s in sizes}
        # 1B verdict for every pair, under each sigma (k05 truth rule, leave-pair-out).
        truth = {}
        for a, b in itertools.combinations(sorted(full["1B"]), 2):
            gap = full["1B"][a] - full["1B"][b]
            truth[(a, b)] = {"gap_1B": gap,
                             "resolved_1B_split": bool(abs(gap) > 2 * se_pair(sigma_without(sp_b["1B"], name, (a, b)))),
                             "resolved_1B_replicate": bool(abs(gap) > 2 * se_pair(sigma_without(fx_b["1B"], name, (a, b))))}
        cnt = {}
        for s in sizes:
            c = {"decisions": 0, "split_calls": 0, "replicate_calls": 0, "split_only": 0, "replicate_only": 0,
                 "k05_halfgap_split_calls": 0, "k05_halfgap_replicate_calls": 0}
            present = sorted(full[s])
            for a, b in itertools.combinations(present, 2):
                s_sp, s_rep = sigma_without(sp_b[s], name, (a, b)), sigma_without(fx_b[s], name, (a, b))
                gap, hgap = full[s][a] - full[s][b], halfm[s][a] - halfm[s][b]
                call_sp, call_rep = abs(gap) > 2 * se_pair(s_sp), abs(gap) > 2 * se_pair(s_rep)
                c["decisions"] += 1
                c["split_calls"] += call_sp
                c["replicate_calls"] += call_rep
                c["k05_halfgap_split_calls"] += abs(hgap) > 2 * se_pair(s_sp)
                c["k05_halfgap_replicate_calls"] += abs(hgap) > 2 * se_pair(s_rep)
                if call_sp != call_rep:
                    c["split_only" if call_sp else "replicate_only"] += 1
                    row = {"kind": "recipe_pair", "battery": bname, "phenotype": name, "size": s,
                           "a": recipes[a], "b": recipes[b], "gap_full_bank": gap, "gap_k05_half_mean": hgap,
                           "sigma_split": s_sp, "sigma_replicate": s_rep,
                           "threshold_split": 2 * se_pair(s_sp), "threshold_replicate": 2 * se_pair(s_rep),
                           "called_by": "split" if call_sp else "replicate",
                           "half_gap_called_split": bool(abs(hgap) > 2 * se_pair(s_sp)),
                           "half_gap_called_replicate": bool(abs(hgap) > 2 * se_pair(s_rep))}
                    if s != "1B" and (a, b) in truth:
                        t = truth[(a, b)]
                        row.update(t)
                        row["sign_agrees_with_1B"] = bool(np.sign(gap) == np.sign(t["gap_1B"]))
                    cases.append(row)
            cnt[s] = c
        # Size steps, recipe by recipe.
        steps = {}
        for s0, s1 in zip(sizes[:-1], sizes[1:]):
            c = {"decisions": 0, "split_calls": 0, "replicate_calls": 0, "split_only": 0, "replicate_only": 0,
                 "negative_gap_calls_split": 0, "negative_gap_calls_replicate": 0}
            for r in sorted(set(full[s0]) & set(full[s1])):
                gap = full[s1][r] - full[s0][r]
                v_sp = sigma_without(sp_b[s0], name, (r,)) ** 2 + sigma_without(sp_b[s1], name, (r,)) ** 2
                v_rep = sigma_without(fx_b[s0], name, (r,)) ** 2 + sigma_without(fx_b[s1], name, (r,)) ** 2
                thr_sp, thr_rep = 2 * math.sqrt(v_sp / R), 2 * math.sqrt(v_rep / R)
                call_sp, call_rep = abs(gap) > thr_sp, abs(gap) > thr_rep
                c["decisions"] += 1
                c["split_calls"] += call_sp
                c["replicate_calls"] += call_rep
                c["negative_gap_calls_split"] += call_sp and gap < 0
                c["negative_gap_calls_replicate"] += call_rep and gap < 0
                if call_sp != call_rep:
                    c["split_only" if call_sp else "replicate_only"] += 1
                    cases.append({"kind": "size_step", "battery": bname, "phenotype": name, "recipe": recipes[r],
                                  "from": s0, "to": s1, "gap_full_bank": gap,
                                  "sd_of_gap_split": math.sqrt(v_sp / R), "sd_of_gap_replicate": math.sqrt(v_rep / R),
                                  "threshold_split": thr_sp, "threshold_replicate": thr_rep,
                                  "called_by": "split" if call_sp else "replicate"})
            steps[f"{s0}->{s1}"] = c
        summary.setdefault(bname, {})[name] = {"recipe_pairs": cnt, "size_steps": steps}
        # Seed-count rule per band, as k05 with sigma swapped.
        rule = {}
        for s in sizes:
            gaps = np.abs([full[s][a] - full[s][b] for a, b in itertools.combinations(sorted(full[s]), 2)])
            s_sp = estimate(sp_b[s], name, check=False).sigma_agg
            s_rep = estimate(fx_b[s], name, check=False).sigma_agg
            rule[s] = {}
            for q in (25, 50):
                d = float(np.percentile(gaps, q))
                n_sp, n_rep = math.ceil(2 * (2 * s_sp / d) ** 2), math.ceil(2 * (2 * s_rep / d) ** 2)
                rule[s][f"p{q}_gap"] = {"delta": d, "sigma_split": s_sp, "sigma_replicate": s_rep,
                                        "seeds_split": n_sp, "seeds_replicate": n_rep, "differ": n_sp != n_rep}
        seed_rule.setdefault(bname, {})[name] = rule
        tot = {k: sum(v[k] for v in cnt.values()) for k in ("decisions", "split_only", "replicate_only")}
        tst = {k: sum(v[k] for v in steps.values()) for k in ("decisions", "split_only", "replicate_only")}
        print(f"[{bname} {name}] lambda split {es.lambda_hat:.4f} fixed {ef.lambda_hat:.4f} | pairs {tot} | steps {tst}", flush=True)

# Cross-checks against the round-2 fixed-bank kernel (results/snap-r2-r1-08/r1_08_fixed_bank.json).
ref = {("all_ten", MARGIN): (1.2374541977737519, 1.2439499117191137), ("all_ten", ACCURACY): (1.0671540626751113, 1.0783733870898093),
       ("no_boolq", MARGIN): (1.7344218743942301, 1.785617464617265), ("no_boolq", ACCURACY): (1.2851807718465011, 1.5578291363266619)}
for (bn, nm), (lf, ls) in ref.items():
    got = sanity[bn][nm]
    assert abs(got["lambda_fixed_bank"] - lf) < 1e-6 and abs(got["lambda_split"] - ls) < 1e-6, f"{bn} {nm}: {got} vs r1_08 {lf}, {ls}"

n_pair = sum(1 for c in cases if c["kind"] == "recipe_pair")
n_step = sum(1 for c in cases if c["kind"] == "size_step")
n_seed = sum(v[q]["differ"] for b in seed_rule.values() for n in b.values() for v in n.values() for q in v)
out = {"any_disagreement": bool(cases), "n_recipe_pair_disagreements": n_pair, "n_size_step_disagreements": n_step,
       "n_seed_rule_differences": int(n_seed), "cases": cases, "summary": summary, "seed_count_rule": seed_rule,
       "sanity_lambdas_and_sigmas": sanity,
       "population": {"N": pop.N, "R": R, "recipes": len(recipes), "sizes": sizes},
       "estimators": {"split": "seednoise.estimator.estimate(split-half population).sigma_agg",
                      "replicate": "seednoise.estimator.estimate(fixed-bank population, A = B = full bank).sigma_agg"},
       "rules": {"recipe_pair": "|gap| > 2*sqrt(2/R)*sigma, sigma leave-pair-out on the size band (k05)",
                 "size_step": "|gap| > 2*sqrt((sigma_s^2 + sigma_s'^2)/R), each sigma leave-recipe-out on its band (new)",
                 "seed_count": "ceil(2*(2*sigma/delta)^2) at p25 and p50 absolute pair gaps (k05)"},
       "gap": "full-bank battery average over kept traits, mean of R runs; k05 half-mean gap recorded as a check",
       "status": "exploratory", "wall_seconds": time.time() - t0}
(W / "r8_split_vs_rep.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] pair disagreements {n_pair}, size-step disagreements {n_step}, seed-rule differences {n_seed}, {time.time() - t0:.0f}s", flush=True)
