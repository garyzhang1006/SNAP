"""R19: per-size intervals for Lambda with positivity-preserving transforms.

Reads the per-configuration cross-half covariances that C01 saved in the
snap-r2-grouped kernel (moments.npz) together with the matching scores.json
manifests, restricts to one model size at a time (25 configurations, one per
recipe), and reports the pre-registered wild cluster bootstrap-t on theta =
Lambda^2, which returns an undefined lower endpoint whenever the linearised
bound crosses zero, beside three constructions that stay positive: the
configuration percentile bootstrap on theta, the cluster-robust t interval on
log theta, and a wild cluster bootstrap-t on log theta. Nothing is refit; the
inputs are the shipped moments.
"""
import json, platform, sys, time, subprocess, shutil
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find(name, must_contain=None):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if must_contain:
        hits = [p for p in hits if must_contain in str(p)]
    if not hits:
        sys.exit(f"{name} ({must_contain}) not found under /kaggle/input")
    return sorted(hits)[0]


shutil.copytree(find("pyproject.toml").parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
import seednoise  # noqa: E402
from seednoise.inference import (_theta, cluster_se, cluster_t_interval, config_bootstrap,  # noqa: E402
                                 wild_bootstrap_t)
print("[env] numpy", np.__version__, "seednoise", getattr(seednoise, "__version__", "?"), flush=True)

DRAWS, SEED, ALPHA = 4999, 0, 0.05


def sqrt_or_nan(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def log_cluster_t(T, U, cluster, alpha=ALPHA):
    """Cluster-robust t(G-1) on log theta, delta method, then square root."""
    G = np.unique(np.asarray(cluster)).size
    th = _theta(T, U)
    se = cluster_se(T, U, cluster) / th
    crit = float(student_t.ppf(1 - alpha / 2, G - 1))
    return {"lo": sqrt_or_nan(th * np.exp(-crit * se)), "hi": sqrt_or_nan(th * np.exp(crit * se)),
            "se_log_theta": float(se), "method": f"cluster-robust t({G - 1}) on log theta"}


def log_wild_bootstrap_t(T, U, cluster, n_boot=DRAWS, alpha=ALPHA, seed=SEED):
    """Wild cluster bootstrap-t on log theta with Rademacher cluster weights.

    Same imposed-null residual perturbation as seednoise.inference.wild_bootstrap_t,
    the studentised statistic is formed on log theta_b with the delta-method
    standard error se_b / theta_b, so a draw with theta_b <= 0 has no finite
    statistic and is counted rather than silently dropped.
    """
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    th = _theta(T, U)
    sU = float(np.sum(U))
    r = T - th * U
    se = cluster_se(T, U, cluster)
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=(n_boot, G))
    vb = v[:, inv]
    Tb = th * U + vb * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, vb.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = (se_b > 0) & (th_b > 0)
    tb = (np.log(th_b[ok]) - np.log(th)) / (se_b[ok] / th_b[ok])
    tb = tb[np.isfinite(tb)]
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    se_log = se / th
    return {"lo": sqrt_or_nan(th * np.exp(-lo_q * se_log)), "hi": sqrt_or_nan(th * np.exp(-hi_q * se_log)),
            "finite_draws": int(tb.size), "nonpositive_theta_draws": int(np.sum(th_b <= 0)),
            "method": f"wild cluster bootstrap-t on log theta (G={G})"}


def as_row(iv):
    return {"lo": iv.lo, "hi": iv.hi, "se": iv.se, "method": iv.method}


def analyse(T, U, cluster):
    out = {"n": int(T.size), "lambda": sqrt_or_nan(_theta(T, U)), "theta": _theta(T, U),
           "negative_T_count": int(np.sum(T < 0))}
    for name, fn in (("wild_theta", lambda: as_row(wild_bootstrap_t(T, U, cluster, n_boot=DRAWS, seed=SEED))),
                     ("cluster_t_theta", lambda: as_row(cluster_t_interval(T, U, cluster))),
                     ("config_pct_theta", lambda: as_row(config_bootstrap(T, U, n_boot=DRAWS, seed=SEED))),
                     ("cluster_t_log", lambda: log_cluster_t(T, U, cluster)),
                     ("wild_log", lambda: log_wild_bootstrap_t(T, U, cluster))):
        try:
            out[name] = fn()
        except Exception as error:  # noqa: BLE001
            out[name] = {"error": f"{type(error).__name__}: {error}"}
    # Share of configuration-bootstrap draws whose theta_b is nonpositive, the reason a
    # percentile lower endpoint can be undefined.
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, T.size, size=(DRAWS, T.size))
    th_b = T[idx].sum(1) / U[idx].sum(1)
    out["config_pct_nonpositive_theta_share"] = float(np.mean(th_b <= 0))
    return out


results = {"draws": DRAWS, "seed": SEED, "alpha": ALPHA, "cells": {}}
checks = []
for phen in ("margin", "accuracy"):
    for ds, job in (("full", "original"), ("noboolq", "noboolq_original")):
        meta = json.load(open(find("scores.json", f"datasets/{ds}/{phen}/")))
        cov = np.load(find("moments.npz", f"C01_{phen}_{job}/"))["covariance"]
        w = np.asarray(meta["weights"], float)
        T = np.einsum("j,cjk,k->c", w, cov, w)
        U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
        recipe = np.array([c["recipe"] for c in meta["configs"]])
        size = np.array([c["size"] for c in meta["configs"]])
        assert cov.shape[0] == 125 and T.size == 125, cov.shape
        for label in ("all", "150M", "300M", "530M", "750M", "1B"):
            m = np.ones(125, bool) if label == "all" else (size == label)
            assert m.sum() == (125 if label == "all" else 25), (label, m.sum())
            cell = analyse(T[m], U[m], recipe[m])
            results["cells"][f"{phen}/{ds}/{label}"] = cell
            print(f"[{phen}/{ds}/{label}] lambda={cell['lambda']:.5f} "
                  f"wild_theta=({cell['wild_theta'].get('lo')}, {cell['wild_theta'].get('hi')}) "
                  f"config_pct=({cell['config_pct_theta'].get('lo')}, {cell['config_pct_theta'].get('hi')}) "
                  f"ct_log=({cell['cluster_t_log'].get('lo')}, {cell['cluster_t_log'].get('hi')}) "
                  f"wild_log=({cell['wild_log'].get('lo')}, {cell['wild_log'].get('hi')}) "
                  f"negT={cell['negative_T_count']} pct_nonpos={cell['config_pct_nonpositive_theta_share']:.4f}",
                  flush=True)
        if ds == "full":
            checks.append((phen, results["cells"][f"{phen}/full/all"]["lambda"], results["cells"][f"{phen}/full/1B"]["lambda"]))

# Reconciliation against the shipped numbers (C01 original split, seednoise leave-one-out table).
expected = {"margin": (1.243949911719114, 1.14898), "accuracy": (1.078, 1.20454)}
for phen, lam_all, lam_1b in checks:
    e_all, e_1b = expected[phen]
    tol_all = 1e-6 if phen == "margin" else 5e-4
    print(f"[check] {phen}: all {lam_all:.6f} vs {e_all} | 1B {lam_1b:.5f} vs {e_1b}", flush=True)
    assert abs(lam_all - e_all) < tol_all, (phen, lam_all, e_all)
    assert abs(lam_1b - e_1b) < 5e-5, (phen, lam_1b, e_1b)
results["checks"] = {p: {"all": a, "1B": b} for p, a, b in checks}
results["wall_seconds"] = time.time() - t0
(W / "r19_size_intervals.json").write_text(json.dumps(results, indent=1,
                                                       default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
