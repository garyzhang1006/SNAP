"""R21: schedule-matched subset and truncation severity, from the R20 step index and the C01 moments.

For each of the 125 configurations the R20 index gives every seed's maximum
released step. A configuration is schedule-matched when its three runs share
the same maximum step. Truncation severity is the selected common step over
the default run's maximum step (seed 2, batch flag 0). The script reports the
inflation estimate on the matched subset, on the subset without the severely
truncated configurations (largest maximum over smallest above 1.5), and the
relation between each configuration's influence on the ratio and its severity,
with recipe-cluster intervals from seednoise.inference. It first checks that
the index reproduces the manuscript's counts of 92 mismatched and 26 severe
configurations and that the reduced runs' recorded steps equal the index's
common step, and stops if either check fails.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t, spearmanr, pearsonr

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find(name, must_contain=None):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if must_contain:
        hits = [p for p in hits if must_contain in str(p)]
    if not hits:
        sys.exit(f"{name} ({must_contain}) not found under /kaggle/input")
    return sorted(hits)


shutil.copytree(find("pyproject.toml")[0].parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
from seednoise.inference import _theta, cluster_se, cluster_t_interval, config_bootstrap, wild_bootstrap_t  # noqa: E402

DRAWS, SEED, ALPHA = 4999, 0, 0.05

# 1. Step index: every seed's maximum step per (recipe, size).
index = {}
parts = sorted(find("step_index_*.json"))
assert len(parts) == 5, parts
for p in parts:
    d = json.load(open(p))
    assert not d["failures"], (p, d["failures"])
    for recipe, r in d["recipes"].items():
        for row in r["runs"]:
            index.setdefault((row["recipe"], row["size"]), {}).setdefault(row["seed"], set()).add(row["step"])
print(f"[index] {len(index)} recipe-size cells from {len(parts)} parts", flush=True)


def sqrt_or_nan(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def as_row(iv):
    return {"lo": iv.lo, "hi": iv.hi, "se": iv.se, "method": iv.method}


def log_cluster_t(T, U, cluster, alpha=ALPHA):
    G = np.unique(np.asarray(cluster)).size
    th = _theta(T, U); se = cluster_se(T, U, cluster) / th
    crit = float(student_t.ppf(1 - alpha / 2, G - 1))
    return {"lo": sqrt_or_nan(th * np.exp(-crit * se)), "hi": sqrt_or_nan(th * np.exp(crit * se)), "method": f"cluster-robust t({G - 1}) on log theta"}


def analyse(T, U, cluster):
    out = {"n": int(T.size), "n_clusters": int(np.unique(cluster).size), "lambda": sqrt_or_nan(_theta(T, U))}
    for name, fn in (("wild_theta", lambda: as_row(wild_bootstrap_t(T, U, cluster, n_boot=DRAWS, seed=SEED))),
                     ("cluster_t_theta", lambda: as_row(cluster_t_interval(T, U, cluster))),
                     ("config_pct_theta", lambda: as_row(config_bootstrap(T, U, n_boot=DRAWS, seed=SEED))),
                     ("cluster_t_log", lambda: log_cluster_t(T, U, cluster))):
        try:
            out[name] = fn()
        except Exception as error:  # noqa: BLE001
            out[name] = {"error": f"{type(error).__name__}: {error}"}
    return out


results = {"draws": DRAWS, "seed": SEED, "checks": {}, "cells": {}, "severity": {}}
for phen in ("margin", "accuracy"):
    meta = json.load(open(find("scores.json", f"datasets/full/{phen}/")[0]))
    cov = np.load(find("moments.npz", f"C01_{phen}_original/")[0])["covariance"]
    w = np.asarray(meta["weights"], float)
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    recipe = np.array([c["recipe"] for c in meta["configs"]])
    size = np.array([c["size"] for c in meta["configs"]])
    # 2. Per-configuration schedule facts from the index, checked against the reduced runs.
    matched, severity, severity_max, ratio, selected = [], [], [], [], []
    for c in meta["configs"]:
        cell = index[(c["recipe"], c["size"])]
        seeds_used = sorted({r["seed"] for r in c["runs"]})
        assert all(s in cell for s in seeds_used), (c["id"], seeds_used, sorted(cell))
        maxima = {s: max(cell[s]) for s in seeds_used}
        common = max(set.intersection(*(cell[s] for s in seeds_used)))
        steps_recorded = {r["checkpoint_step"] for r in c["runs"]}
        assert steps_recorded == {common}, (c["id"], steps_recorded, common)
        default = [r["seed"] for r in c["runs"] if r["batch"] == 0]
        assert len(default) == 1, (c["id"], default)
        matched.append(len(set(maxima.values())) == 1)
        severity.append(common / maxima[default[0]])
        severity_max.append(common / max(maxima.values()))
        ratio.append(max(maxima.values()) / min(maxima.values()))
        selected.append(common)
    matched = np.array(matched); severity = np.array(severity); severity_max = np.array(severity_max); ratio = np.array(ratio)
    severe = ratio > 1.5
    checks = {"mismatched": int((~matched).sum()), "matched": int(matched.sum()), "severe_over_1p5": int(severe.sum()),
              "severe_sizes": sorted(set(size[severe].tolist())),
              "mean_severity_530M": float(severity[size == "530M"].mean()), "mean_severity_750M": float(severity[size == "750M"].mean()),
              "matched_by_size": {s: int(matched[size == s].sum()) for s in ("150M", "300M", "530M", "750M", "1B")}}
    print(f"[{phen}] checks {json.dumps(checks)}", flush=True)
    results["checks"][phen] = checks
    if phen == "margin":
        assert checks["mismatched"] == 92, checks
        assert checks["severe_over_1p5"] == 26, checks
    # 3. Estimates on subsets.
    for label, m in (("all", np.ones(125, bool)), ("matched", matched), ("not_severe", ~severe), ("severe_only", severe), ("mismatched", ~matched)):
        cell = analyse(T[m], U[m], recipe[m])
        cell["sizes"] = {s: int((size[m] == s).sum()) for s in ("150M", "300M", "530M", "750M", "1B")}
        results["cells"][f"{phen}/{label}"] = cell
        print(f"[{phen}/{label}] n={cell['n']} G={cell['n_clusters']} lambda={cell['lambda']:.4f} wild=({cell['wild_theta'].get('lo')}, {cell['wild_theta'].get('hi')}) ct_log=({cell['cluster_t_log'].get('lo')}, {cell['cluster_t_log'].get('hi')})", flush=True)
    # 4. Influence against severity over all 125, with a within-size permutation reference.
    th = _theta(T, U); psi = (T - th * U) / U.sum()
    rs, ps = spearmanr(psi, severity); rp, pp = pearsonr(psi, severity)
    rng = np.random.default_rng(SEED)
    perm = []
    for _ in range(DRAWS):
        s2 = severity.copy()
        for s in np.unique(size):
            idx = np.where(size == s)[0]; s2[idx] = s2[rng.permutation(idx)]
        perm.append(spearmanr(psi, s2)[0])
    perm = np.array(perm)
    p_within = float((np.sum(np.abs(perm) >= abs(rs)) + 1) / (perm.size + 1))
    # Same relation inside the two bands where severity varies.
    bands = {}
    for s in ("530M", "750M"):
        i = size == s
        if np.unique(severity[i]).size > 1:
            bands[s] = {"spearman": float(spearmanr(psi[i], severity[i])[0]), "n": int(i.sum()), "severity_range": [float(severity[i].min()), float(severity[i].max())]}
    results["severity"][phen] = {"spearman": float(rs), "spearman_p_naive": float(ps), "pearson": float(rp), "pearson_p_naive": float(pp),
                                 "spearman_p_within_size_permutation": p_within, "bands": bands,
                                 "severity_by_size_mean": {s: float(severity[size == s].mean()) for s in ("150M", "300M", "530M", "750M", "1B")},
                                 "influence_sum_by_size": {s: float(psi[size == s].sum()) for s in ("150M", "300M", "530M", "750M", "1B")}}
    print(f"[{phen}/severity] {json.dumps(results['severity'][phen])}", flush=True)
    results.setdefault("per_config", {})[phen] = [{"id": c["id"], "size": str(sz), "matched": bool(mt), "severity": float(sv), "severity_vs_max": float(svm), "ratio": float(rt), "selected_step": int(st), "T": float(tt), "U": float(uu), "influence": float(pi)}
                                                 for c, sz, mt, sv, svm, rt, st, tt, uu, pi in zip(meta["configs"], size, matched, severity, severity_max, ratio, selected, T, U, psi)]

results["wall_seconds"] = time.time() - t0
(W / "r21_matched_step.json").write_text(json.dumps(results, indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
