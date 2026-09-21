"""R6 fitted scenario: interval coverage in populations built from the observed data's own structure.

Design fixed before running (2026-09-15, written 18:12 EDT). The plan asks for one scenario with a
documented estimate of the real influence concentration, reported as a fitted scenario and never as
independent confirmation. The twelve R6 cells use exchangeable covariance, and on the observed margins
the test-inversion lower endpoint sits 0.048 below the wild one, which suggests influence structure the
cells don't contain.
SCENARIO "size" (kernel snap-r6-matched-a). Each of the five size bands gets its own seed covariance,
the nearest positive semidefinite matrix to that band's observed sigma_e, and its own item-noise SDs and
margin levels, as in matched_spec. Every replicate simulates the five bands with 25 configurations each,
one per recipe, sharing one random item split per trait, and stacks them into 125 configurations.
SCENARIO "size_recipe" (kernel snap-r6-matched-b). As "size", and each recipe's run deviations are then
scaled by the square root of k_r, the observed recipe sum of U_c over its mean, clipped below at 0.05,
separately for each phenotype. These k_r include sampling noise, so they overstate true heterogeneity.
Each replicate scores the wild cluster bootstrap-t (4,999 draws, seed rep), the cluster-robust t(24), and
the centred and restricted test-inversion intervals of snap-r6-fieller. Margin truth is
sqrt(sum_s sum Sigma_s / sum_s trace Sigma_s). Accuracy truth is the square root of the ratio of mean
summed T to mean summed U over the replicates, since the generator acts on margins. 2,000 replicates,
seeds 20260916 + 104729 rep. Record coverage, tail misses, widths, undefined and unbounded shares, and
the largest recipe share of squared influence, with the observed value for comparison.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

SCENARIO = "size_recipe"
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

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate, nearest_psd, sigma_e  # noqa: E402
from seednoise.inference import cluster_influence, cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402
from seednoise.nulls import NOMINAL_ITEMS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import SimSpec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
PH = ("margin", "accuracy")
REPS = 2000


def invert(T, U, cluster, alpha=0.05, form="centred"):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    t = np.bincount(inv, weights=np.asarray(T, float), minlength=G)
    u = np.bincount(inv, weights=np.asarray(U, float), minlength=G)
    c2 = float(student_t.ppf(1 - alpha / 2, G - 1)) ** 2
    a, b = t.sum(), u.sum()
    Stt, Stu, Suu = float(t @ t), float(t @ u), float(u @ u)
    m, k = (0.0, c2) if form == "restricted" else (c2 / (G - 1), c2 * G / (G - 1))
    A = (1 + m) * b * b - k * Suu
    B = -2 * (1 + m) * a * b + 2 * k * Stu
    C = (1 + m) * a * a - k * Stt
    f = lambda th: A * th * th + B * th + C  # noqa: E731
    disc = B * B - 4 * A * C
    if abs(A) < 1e-300:
        roots = [] if abs(B) < 1e-300 else [-C / B]
    elif disc < 0:
        roots = []
    else:
        s = np.sqrt(disc); roots = sorted([(-B - s) / (2 * A), (-B + s) / (2 * A)])
    edges = sorted([0.0] + [r for r in roots if r > 0]) + [np.inf]
    segs = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mid = lo + 1.0 if not np.isfinite(hi) else 0.5 * (lo + hi)
        if f(mid) <= 0:
            if segs and abs(segs[-1][1] - lo) < 1e-15:
                segs[-1][1] = hi
            else:
                segs.append([lo, hi])
    bounded = len(segs) == 1 and np.isfinite(segs[0][1])
    return [[float(np.sqrt(lo)), float(np.sqrt(hi)) if np.isfinite(hi) else None] for lo, hi in segs], bounded


def max_share(T, U, cluster):
    psi, _, _ = cluster_influence(T, U, cluster)
    s = psi ** 2
    return float(s.max() / s.sum()) if s.sum() > 0 else float("nan")


bands = np.unique(pop.size)
specs, truth_parts = [], {"num": 0.0, "den": 0.0}
for s in bands:
    band = pop.subset(np.flatnonzero(pop.size == s))
    S = sigma_e(band, "margin")
    Sp, clipped = nearest_psd(S, floor=1e-12)
    comp = variance_components(band, "margin")
    n_items = (tuple(int(n) for n in np.asarray(pop.n_items).tolist()) if pop.n_items is not None
               else tuple([NOMINAL_ITEMS] * pop.K))
    n_half = np.maximum(np.asarray(n_items, float) / 2.0, 1.0)
    item_sd = np.sqrt(np.clip(comp.noise2, 1e-12, None) * n_half)
    ph = band.pheno("margin"); level = 0.5 * (ph.A.mean(axis=(0, 1)) + ph.B.mean(axis=(0, 1)))
    specs.append({"sigma": Sp, "item_sd": tuple(item_sd.tolist()), "boundary_z": tuple((-level / item_sd).tolist()),
                  "n_items": n_items, "clipped": clipped})
    truth_parts["num"] += float(Sp.sum()); truth_parts["den"] += float(np.trace(Sp))
truth_margin = float(np.sqrt(truth_parts["num"] / truth_parts["den"]))

k_r = {}
for name in PH:
    e = estimate(pop, name, check=False)
    Ur = np.array([e.U[pop.recipe == r].sum() for r in np.unique(pop.recipe)])
    k_r[name] = np.clip(Ur / Ur.mean(), 0.05, None)

report = {"design": __doc__, "scenario": SCENARIO, "reps": REPS, "truth_margin": truth_margin,
          "band_psd_clipped": [sp["clipped"] for sp in specs], "k_r": {n: v.tolist() for n, v in k_r.items()},
          "observed": {}}
for name in PH:
    e = estimate(pop, name, check=False)
    report["observed"][name] = {"lambda": float(e.lambda_hat), "max_recipe_influence_share": max_share(e.T, e.U, pop.recipe)}
print(f"[setup] truth_margin {truth_margin:.4f} observed {json.dumps(report['observed'])} clipped {report['band_psd_clipped']}", flush=True)


def one_rep(rep):
    rng = np.random.default_rng(20260916 + 104729 * rep)
    halves = []
    for n in specs[0]["n_items"]:
        mask = np.zeros(n, dtype=bool); mask[rng.permutation(n)[: n // 2]] = True; halves.append(mask)
    parts = []
    for i, sp in enumerate(specs):
        spec = SimSpec(n_config=25, n_runs=3, traits=tuple(pop.traits), n_items=sp["n_items"], item_sd=sp["item_sd"],
                       boundary_z=sp["boundary_z"], n_recipes=25, n_sizes=1, seed=int(rng.integers(2 ** 31)))
        spec.sigma_e = sp["sigma"]
        parts.append(simulate(spec, halves=halves))
    phen = {}
    for name in PH:
        A = np.concatenate([p.pheno(name).A for p in parts]); B = np.concatenate([p.pheno(name).B for p in parts])
        if SCENARIO == "size_recipe":
            scale = np.sqrt(np.tile(k_r[name], len(parts)))[:, None, None]
            A = A.mean(axis=1, keepdims=True) + scale * (A - A.mean(axis=1, keepdims=True))
            B = B.mean(axis=1, keepdims=True) + scale * (B - B.mean(axis=1, keepdims=True))
        phen[name] = Phenotype(name, A, B)
    recipe = np.tile(np.arange(25), len(parts)); size = np.repeat(np.arange(len(parts)), 25)
    return Population(phen, recipe=recipe, size=size, traits=list(pop.traits), n_items=np.asarray(specs[0]["n_items"]))


rows = {name: [] for name in PH}; sums = {name: [0.0, 0.0] for name in PH}
for rep in range(REPS):
    sim = one_rep(rep)
    for name in PH:
        e = estimate(sim, name, check=False)
        T, U = e.T, e.U
        sums[name][0] += float(T.sum()); sums[name][1] += float(U.sum())
        row = {"est": float(e.lambda_hat), "max_share": max_share(T, U, sim.recipe)}
        try:
            wb = wild_bootstrap_t(T, U, sim.recipe, n_boot=4999, seed=rep); row["wild"] = [wb.lo, wb.hi]
        except Exception as err:  # noqa: BLE001
            row["wild"] = [float("nan"), float("nan")]; row["wild_error"] = type(err).__name__
        ct = cluster_t_interval(T, U, sim.recipe); row["cluster_t"] = [ct.lo, ct.hi]
        for form in ("centred", "restricted"):
            sets, bounded = invert(T, U, sim.recipe, form=form); row[form] = {"sets": sets, "bounded": bounded}
        rows[name].append(row)
    if rep % 100 == 0:
        print(f"[rep {rep}] {time.time() - t0:.0f}s", flush=True)

report["truth"] = {"margin": truth_margin, "accuracy": float(np.sqrt(sums["accuracy"][0] / sums["accuracy"][1])),
                   "margin_mean_ratio_check": float(np.sqrt(sums["margin"][0] / sums["margin"][1]))}
report["summary"] = {}
for name in PH:
    tr = report["truth"][name]; R = rows[name]; out = {}
    est = np.array([r["est"] for r in R]); fin = est[np.isfinite(est)]
    out["estimate"] = {"mean": float(fin.mean()), "bias": float(fin.mean() - tr), "sd": float(fin.std(ddof=1)), "undefined": int((~np.isfinite(est)).sum())}
    ms = np.array([r["max_share"] for r in R])
    out["max_recipe_influence_share"] = {"p05": float(np.nanpercentile(ms, 5)), "median": float(np.nanmedian(ms)), "p95": float(np.nanpercentile(ms, 95)),
                                        "share_at_or_above_observed": float(np.nanmean(ms >= report["observed"][name]["max_recipe_influence_share"]))}
    for meth in ("wild", "cluster_t"):
        lo = np.array([r[meth][0] for r in R], float); hi = np.array([r[meth][1] for r in R], float)
        ok = np.isfinite(lo) & np.isfinite(hi)
        out[meth] = {"coverage": float(np.mean(ok & (lo <= tr) & (tr <= hi))), "lower_miss": float(np.mean(ok & (lo > tr))),
                     "upper_miss": float(np.mean(ok & (hi < tr))), "undefined": float(np.mean(~ok)),
                     "median_width": float(np.median((hi - lo)[ok])) if ok.any() else None}
    for form in ("centred", "restricted"):
        cov = [any(s[0] <= tr and (s[1] is None or tr <= s[1]) for s in r[form]["sets"]) for r in R]
        low = [bool(r[form]["sets"]) and min(s[0] for s in r[form]["sets"]) > tr for r in R]
        up = [r[form]["bounded"] and r[form]["sets"][0][1] < tr for r in R]
        wid = [r[form]["sets"][0][1] - r[form]["sets"][0][0] for r in R if r[form]["bounded"]]
        out[form] = {"coverage": float(np.mean(cov)), "lower_miss": float(np.mean(low)), "upper_miss": float(np.mean(up)),
                     "unbounded": float(np.mean([not r[form]["bounded"] for r in R])), "median_width": float(np.median(wid)) if wid else None}
    for key in ("wild", "cluster_t", "centred", "restricted"):
        if "coverage" in out[key]:
            out[key]["mc_se"] = float(np.sqrt(out[key]["coverage"] * (1 - out[key]["coverage"]) / REPS))
    report["summary"][name] = out
    print(f"[{name}] truth {tr:.4f} {json.dumps(out)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / f"r6_matched_{SCENARIO}.json").write_text(json.dumps(report, indent=1))
(W / f"rows_{SCENARIO}.json").write_text(json.dumps(rows, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o)))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
