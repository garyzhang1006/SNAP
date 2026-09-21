"""R12 pooled held-out prediction, giving the fitted predictions a less noisy target.

Design fixed before running (2026-09-15, written 21:35 EDT). snap-r12-predict compares predictions of a
ratio measured on six runs of one configuration, and that target swings from 0.70 to 1.85 between its
fifth and ninety-fifth percentiles, so the comparison may be measuring target noise rather than model
quality. This run pools the target across configurations. For each of the 84 ways of choosing three
runs, the held-out six runs give one pooled ratio, formed from the mean within-configuration variance
of the battery mean over the mean within-configuration variance sum of the benchmarks. The three
predictions are those of snap-r12-predict, fitted on the three-run population across all
configurations. We report the mean absolute log error of each prediction over the 84 splits, the
paired differences, and the spread of the pooled target, for both phenotypes and both size sets.
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



def pooled_ratio(p, name):
    """One ratio for the whole population, from within-configuration variances."""
    ph = p.pheno(name)
    y = 0.5 * (ph.A + ph.B)                      # (N, R, K)
    w = np.full(y.shape[2], 1.0 / y.shape[2])
    agg = y @ w
    num = float(np.mean(np.var(agg, axis=1, ddof=1)))
    den = float(np.sum(w ** 2 * np.mean(np.var(y, axis=1, ddof=1), axis=0)))
    return float(np.sqrt(num / den)) if den > 0 and num >= 0 else float("nan")


def pooled_predictions(p, name):
    S = sigma_e(p, name)
    v = np.asarray(variance_components(p, name).noise2, float) / 2.0
    w = np.full(p.K, 1.0 / p.K)
    num_g, den_g = float(w @ S @ w), float(np.sum(w ** 2 * np.diag(S)))
    lam = float(np.sqrt(num_g / den_g)) if den_g > 0 and num_g >= 0 else float("nan")
    num_t, den_t = num_g + float(np.sum(w ** 2 * v)), den_g + float(np.sum(w ** 2 * v))
    dec = float(np.sqrt(num_t / den_t)) if den_t > 0 and num_t >= 0 else float("nan")
    return {"independence": 1.0, "plug_in": lam, "decomposition": dec}


report = {"design": __doc__, "sets": {}}
for label, sizes in (("three_sizes", ["70m", "160m", "410m"]), ("five_sizes", ["14m", "31m", "70m", "160m", "410m"])):
    pop, _ = build_population(runs_dir, TRAITS, n_runs=9, sizes=sizes)
    cell = {"N": pop.N, "R": pop.R, "phenotypes": {}}
    for name in ("margin", "accuracy"):
        t1 = time.time(); rows = []
        for fit in combinations(range(pop.R), 3):
            held = [r for r in range(pop.R) if r not in fit]
            pr = pooled_predictions(sub_runs(pop, name, fit), name)
            obs = pooled_ratio(sub_runs(pop, name, held), name)
            rows.append({"fit": list(fit), "observed": obs, **pr})
        obs = np.array([r["observed"] for r in rows], float)
        ok = np.isfinite(obs) & (obs > 0)
        out = {"n_splits": len(rows),
               "observed": {"n_finite": int(ok.sum()), "mean": float(obs[ok].mean()), "sd": float(obs[ok].std(ddof=1)),
                            "p05": float(np.percentile(obs[ok], 5)), "median": float(np.median(obs[ok])),
                            "p95": float(np.percentile(obs[ok], 95))},
               "errors": {}}
        for k in ("independence", "plug_in", "decomposition"):
            pred = np.array([r[k] for r in rows], float)
            good = ok & np.isfinite(pred) & (pred > 0)
            e = np.abs(np.log(pred[good]) - np.log(obs[good]))
            out["errors"][k] = {"n": int(good.sum()), "mean_abs_log_error": float(e.mean()),
                                "median_abs_log_error": float(np.median(e)),
                                "mean_prediction": float(pred[good].mean()), "sd_prediction": float(pred[good].std(ddof=1))}
        for a, b in (("decomposition", "independence"), ("decomposition", "plug_in"), ("plug_in", "independence")):
            pa = np.array([r[a] for r in rows], float); pb = np.array([r[b] for r in rows], float)
            good = ok & np.isfinite(pa) & (pa > 0) & np.isfinite(pb) & (pb > 0)
            d = np.abs(np.log(pa[good]) - np.log(obs[good])) - np.abs(np.log(pb[good]) - np.log(obs[good]))
            out["errors"][f"{a}_minus_{b}"] = {"mean": float(d.mean()), "median": float(np.median(d)),
                                               "share_below_zero": float(np.mean(d < 0))}
        out["rows"] = rows
        cell["phenotypes"][name] = out
        print(f"[{label}/{name}] {time.time() - t1:.0f}s obs {out['observed']['median']:.4f} sd {out['observed']['sd']:.4f} " +
              json.dumps({k: round(v["mean_abs_log_error"], 5) for k, v in out["errors"].items() if "mean_abs_log_error" in v}), flush=True)
    report["sets"][label] = cell

report["wall_seconds"] = time.time() - t0
(W / "r12_predict_pooled.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
