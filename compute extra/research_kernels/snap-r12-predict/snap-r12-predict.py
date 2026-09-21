"""R12 held-out prediction, testing whether the decomposition predicts a directly observed ratio.

Design fixed before running (2026-09-15, written 21:20 EDT). Every other check compares the estimator
with itself or with a simulation. PolyPythias carries nine seeds per configuration, which is enough to
measure the quantity the estimator is about, so this run predicts it out of sample from disjoint runs.

For a set of runs, the observed ratio is the standard deviation of the battery mean over those runs,
divided by the square root of the weighted sum of per-benchmark variances over the same runs. That
ratio is measurable and it includes item noise, so it sits below the item-general inflation. From a
fitting triple we form three predictions of it. The independence prediction is one. The plug-in of the
inflation estimate is Lambda hat itself, which ignores item noise. The decomposition prediction adds
each benchmark's estimated half-score item noise to both sides, at half its per-half variance because
the score averages two halves, and it is the prediction the measurement model actually implies.

Each configuration contributes the 84 ways of choosing three of its nine runs, and each fitting triple
is scored against the six runs it leaves out. We report the mean absolute log error of each prediction,
the paired differences between them, and the same quantities per configuration, on both phenotypes and
on the three-size and five-size sets. With three or five configurations the comparison is descriptive,
so we report per-configuration values rather than an interval across configurations.
"""
import json, platform, shutil, subprocess, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import sigma_e  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

arm2 = [p for p in Path("/kaggle/input").rglob("arm2__*.npz") if "runs-arm2" in str(p)]
assert len(arm2) == 45, len(arm2)
runs_dir = W / "arm2"; runs_dir.mkdir(exist_ok=True)
for p in arm2:
    shutil.copy(p, runs_dir / p.name)


def sub_runs(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, m, :], ph.B[:, m, :])
    return Population({name: sub}, None, None, None, p.recipe, p.size, list(p.traits), p.config_ids, p.n_items)


def observed_ratio(p, name, config):
    """Standard deviation of the battery mean over runs, against the independent sum."""
    ph = p.pheno(name)
    y = 0.5 * (ph.A[config] + ph.B[config])          # (R, K) full scores
    w = np.full(y.shape[1], 1.0 / y.shape[1])
    agg = y @ w
    num = float(np.var(agg, ddof=1))
    den = float(np.sum(w ** 2 * np.var(y, axis=0, ddof=1)))
    return float(np.sqrt(num / den)) if den > 0 and num >= 0 else float("nan")


def predictions(p, name, config):
    one = sub_runs(p, name, np.arange(p.R)).subset([config])
    S = sigma_e(one, name)
    comp = variance_components(one, name)
    v = np.asarray(comp.noise2, float) / 2.0          # item noise of the averaged score
    K = one.K
    w = np.full(K, 1.0 / K)
    num_g = float(w @ S @ w)
    den_g = float(np.sum(w ** 2 * np.diag(S)))
    lam = float(np.sqrt(num_g / den_g)) if den_g > 0 and num_g >= 0 else float("nan")
    num_t = num_g + float(np.sum(w ** 2 * v))
    den_t = den_g + float(np.sum(w ** 2 * v))
    dec = float(np.sqrt(num_t / den_t)) if den_t > 0 and num_t >= 0 else float("nan")
    return {"independence": 1.0, "plug_in": lam, "decomposition": dec}


report = {"design": __doc__, "sets": {}}
for label, sizes in (("three_sizes", ["70m", "160m", "410m"]), ("five_sizes", ["14m", "31m", "70m", "160m", "410m"])):
    pop, _ = build_population(runs_dir, TRAITS, n_runs=9, sizes=sizes)
    cell = {"N": pop.N, "R": pop.R, "phenotypes": {}}
    for name in ("margin", "accuracy"):
        t1 = time.time(); rows = []
        for c in range(pop.N):
            for fit in combinations(range(pop.R), 3):
                held = [r for r in range(pop.R) if r not in fit]
                fp = sub_runs(pop, name, fit)
                pr = predictions(fp, name, c)
                obs = observed_ratio(sub_runs(pop, name, held), name, c)
                rows.append({"config": c, "fit": list(fit), "observed": obs, **pr})
        out = {"n_rows": len(rows)}
        obs = np.array([r["observed"] for r in rows], float)
        ok = np.isfinite(obs) & (obs > 0)
        out["observed"] = {"n_finite": int(ok.sum()), "mean": float(obs[ok].mean()),
                           "p05": float(np.percentile(obs[ok], 5)), "median": float(np.median(obs[ok])),
                           "p95": float(np.percentile(obs[ok], 95))}
        err = {}
        for k in ("independence", "plug_in", "decomposition"):
            pred = np.array([r[k] for r in rows], float)
            good = ok & np.isfinite(pred) & (pred > 0)
            e = np.abs(np.log(pred[good]) - np.log(obs[good]))
            err[k] = {"n": int(good.sum()), "mean_abs_log_error": float(e.mean()),
                      "median_abs_log_error": float(np.median(e)),
                      "mean_prediction": float(pred[good].mean())}
        for a, b in (("decomposition", "independence"), ("decomposition", "plug_in"), ("plug_in", "independence")):
            pa = np.array([r[a] for r in rows], float); pb = np.array([r[b] for r in rows], float)
            good = ok & np.isfinite(pa) & (pa > 0) & np.isfinite(pb) & (pb > 0)
            d = np.abs(np.log(pa[good]) - np.log(obs[good])) - np.abs(np.log(pb[good]) - np.log(obs[good]))
            err[f"{a}_minus_{b}"] = {"mean": float(d.mean()), "median": float(np.median(d)),
                                     "share_below_zero": float(np.mean(d < 0))}
        out["errors"] = err
        out["by_config"] = {}
        for c in range(pop.N):
            sel = [r for r in rows if r["config"] == c]
            o = np.array([r["observed"] for r in sel], float); m = np.isfinite(o) & (o > 0)
            cfg = {"observed_median": float(np.median(o[m])) if m.any() else None}
            for k in ("independence", "plug_in", "decomposition"):
                pred = np.array([r[k] for r in sel], float); g = m & np.isfinite(pred) & (pred > 0)
                cfg[k] = {"mean_prediction": float(pred[g].mean()) if g.any() else None,
                          "mean_abs_log_error": float(np.mean(np.abs(np.log(pred[g]) - np.log(o[g])))) if g.any() else None}
            out["by_config"][str(pop.config_ids[c])] = cfg
        cell["phenotypes"][name] = out
        print(f"[{label}/{name}] {time.time() - t1:.0f}s obs {out['observed']['median']:.4f} " +
              json.dumps({k: round(v["mean_abs_log_error"], 5) for k, v in err.items() if "mean_abs_log_error" in v}), flush=True)
    report["sets"][label] = cell

report["wall_seconds"] = time.time() - t0
(W / "r12_predict.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
