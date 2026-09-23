"""R5-07 (CPU, exploratory): false-positive rate of the two decision rules on null seed pairs in PolyPythias.

Design fixed before running (2026-09-23). The DataDecide decision study (compute extra/heldout/kaggle/
k05-decision/k05-decision.py:87-116, reported at main.tex:222) calls a pair when its aggregate gap exceeds
two standard errors, se = sqrt(2 / R) * sigma, with sigma either sigma_indep (the estimator's U) or
sigma_agg (the estimator's T), estimated with the pair left out. There a wrong call can be a real rank
change, so it is no false-positive rate. PolyPythias gives nine seeds of one configuration per size, so any
two disjoint sets of those seeds have a true gap of zero and every call on them is a false positive.

Inputs: the 45 runs-arm2 reductions of snap-r12-polypythias (five sizes, nine seeds, ten traits, step143000),
built with build_population exactly as snap-r12-analysis did. The 18 runs-adjacent reductions cover nine
traits and are not used, since build_population needs all ten.

Per size and phenotype (margin, accuracy), the same aggregate and rule as k05:
1. single_run: every one of the 36 seed pairs, R = 1 per side, sigmas from the other 7 seeds of that
   configuration (N = 1, R = 7).
2. three_run: every one of the 840 unordered pairs of disjoint seed triples, R = 3 per side as in k05,
   sigmas from the remaining 3 seeds (N = 1, R = 3).
3. in_sample_reference: the 36 single-run pairs with sigmas from all 9 seeds, pair included. It separates
   the bias of each standard error from the noise of estimating it on few runs, and it leaves nothing out.
Reported: pairs, pairs with a defined sigma, calls, false-positive rate, the nominal two-sided rate at two
known standard errors, and calls made by independence that the corrected rule drops. A seed jackknife
(rerun of design 1 on each set of eight seeds, sigmas from the other 6) gives a standard error that respects
the shared seeds. Everything here is exploratory.
"""
import itertools, json, math, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from scipy.stats import norm

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402

arm2 = sorted(p for p in Path("/kaggle/input").rglob("arm2__*.npz")
              if not p.name.startswith(("._", "adj")))
assert len(arm2) == 45, f"expected 45 runs-arm2 reductions, found {len(arm2)}: {[p.name for p in arm2][:5]}"
runs_dir = W / "arm2"; runs_dir.mkdir(exist_ok=True)
for p in arm2:
    shutil.copy(p, runs_dir / p.name)
pop, info = build_population(runs_dir, TRAITS, n_runs=9, sizes=["14m", "31m", "70m", "160m", "410m"])
lam = estimate(pop, MARGIN).lambda_hat
# snap-r12-analysis five_sizes margin Lambda, so these are the same runs, split and population.
assert abs(lam - 1.2619855939956985) < 5e-4, f"runs give margin Lambda {lam}, not snap-r12-analysis's 1.26199"
print(f"[pop] N={pop.N} R={pop.R} K={pop.K} configs {pop.config_ids} margin Lambda {lam:.5f}", flush=True)

Z_NOMINAL = float(2 * norm.sf(2.0))


def sigmas(c, name, runs):
    """sigma_indep and sigma_agg of configuration c from the given runs only."""
    ph = {k: Phenotype(k, v.A[[c]][:, runs], v.B[[c]][:, runs]) for k, v in pop.phenotypes.items()}
    e = estimate(Population(ph, traits=pop.traits), name, check=False)
    return e.sigma_indep, e.sigma_agg


def score(c, name, runs):
    ph = pop.pheno(name)
    return float(((ph.A[c, runs] + ph.B[c, runs]) / 2).mean())


def call_rows(c, name, pairs, R, estimation):
    rows = []
    for a, b in pairs:
        est = estimation(a, b)
        s_ind, s_agg = sigmas(c, name, est)
        gap = score(c, name, list(a)) - score(c, name, list(b))
        row = {"a": [int(x) for x in a], "b": [int(x) for x in b], "estimation_runs": [int(x) for x in est],
               "gap": gap, "sigma_indep": s_ind, "sigma_agg": s_agg}
        for method, s in (("independence", s_ind), ("corrected", s_agg)):
            ok = bool(np.isfinite(s))
            row[f"{method}_defined"] = ok
            row[f"{method}_called"] = bool(ok and abs(gap) > 2 * math.sqrt(2.0 / R) * s)
        rows.append(row)
    return rows


def summarise(rows):
    out = {"pairs": len(rows), "nominal_rate": Z_NOMINAL}
    for m in ("independence", "corrected"):
        d = [r for r in rows if r[f"{m}_defined"]]
        k = sum(r[f"{m}_called"] for r in d)
        out[m] = {"defined": len(d), "calls": k, "false_positive_rate": k / len(d) if d else float("nan")}
    both = [r for r in rows if r["independence_defined"] and r["corrected_defined"]]
    out["both_defined"] = len(both)
    out["independence_calls_dropped_by_correction"] = sum(r["independence_called"] and not r["corrected_called"] for r in both)
    out["corrected_calls_not_made_by_independence"] = sum(r["corrected_called"] and not r["independence_called"] for r in both)
    out["rate_independence_minus_corrected_on_both_defined"] = (
        (sum(r["independence_called"] for r in both) - sum(r["corrected_called"] for r in both)) / len(both)
        if both else float("nan"))
    return out


def single_run(seeds):
    pairs = [((a,), (b,)) for a, b in itertools.combinations(seeds, 2)]
    return pairs, (lambda a, b: [s for s in seeds if s not in a + b])


def three_run(seeds):
    pairs = []
    for a in itertools.combinations(seeds, 3):
        rest = [s for s in seeds if s not in a]
        for b in itertools.combinations(rest, 3):
            if min(b) > min(a):
                pairs.append((a, b))
    return pairs, (lambda a, b: [s for s in seeds if s not in a + b])


report = {"design": __doc__, "population": {"N": pop.N, "R": pop.R, "K": pop.K, "configs": pop.config_ids,
          "margin_lambda": lam, "half_A_items": info["half_A_items"], "half_B_items": info["half_B_items"]},
          "results": {}, "jackknife_single_run": {}}
pair_dump = []
all_seeds = list(range(pop.R))
for name in (MARGIN, ACCURACY):
    pooled = {"single_run": [], "three_run": [], "in_sample_reference": []}
    for c, cfg in enumerate(pop.config_ids):
        size = cfg[1]
        cells = {}
        for design, (R, maker) in (("single_run", (1, single_run)), ("three_run", (3, three_run))):
            pairs, est = maker(all_seeds)
            rows = call_rows(c, name, pairs, R, est)
            cells[design] = rows
        pairs, _ = single_run(all_seeds)
        cells["in_sample_reference"] = call_rows(c, name, pairs, 1, lambda a, b: all_seeds)
        for design, rows in cells.items():
            s = summarise(rows)
            report["results"].setdefault(name, {}).setdefault(design, {})[size] = s
            pooled[design] += rows
            pair_dump += [dict(r, phenotype=name, size=size, design=design) for r in rows]
            print(f"[{name} {size} {design}] {json.dumps({m: s[m] for m in ('independence', 'corrected')})}", flush=True)
        # Delete-one-seed jackknife of design 1, rerun whole on the eight remaining seeds.
        jk = {"independence": [], "corrected": []}
        for drop in all_seeds:
            seeds = [s for s in all_seeds if s != drop]
            pairs, est = single_run(seeds)
            s = summarise(call_rows(c, name, pairs, 1, est))
            for m in jk:
                jk[m].append(s[m]["false_positive_rate"])
        cell = {}
        for m, v in jk.items():
            v = np.asarray(v, float)
            n = np.isfinite(v).sum()
            cell[m] = {"leave_one_seed_rates": v.tolist(),
                       "jackknife_se": float(math.sqrt((n - 1) / n * np.nansum((v - np.nanmean(v)) ** 2))) if n > 1 else float("nan")}
        report["jackknife_single_run"].setdefault(name, {})[size] = cell
    for design, rows in pooled.items():
        report["results"][name][design]["pooled_over_sizes"] = summarise(rows)
        print(f"[{name} pooled {design}] {json.dumps(report['results'][name][design]['pooled_over_sizes'])}", flush=True)

report["status"] = "exploratory; null pairs share seeds, so pooled counts are not independent trials"
report["wall_seconds"] = time.time() - t0
(W / "r5_07_null_pairs.json").write_text(json.dumps(report, indent=1))
(W / "r5_07_null_pairs_rows.json").write_text(json.dumps(pair_dump))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
