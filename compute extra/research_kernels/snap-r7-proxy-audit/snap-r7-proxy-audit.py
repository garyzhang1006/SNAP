"""R7 CPU part: audit of the shipped competence proxy and a cross-fitted regularised proxy.

Design fixed before any output was opened (2026-09-15, 17:05 EDT).
Inputs are the 375 shipped reduced runs, built exactly as `seednoise analyze` builds them.
1. Reproduction. The unadjusted and after-competence estimates must match the shipped
   tab_primary.csv (margin 1.24399 / accuracy 1.07595 after competence) to 5e-5.
2. Audit, per phenotype. Raw pooled seed variance per trait, whether the 1e-12 clip binds,
   the standardising SD, each trait's share of the summed squared standardised deviations
   (the proxy's inputs), the pooled slope b_j, the share of each trait's cross-half seed
   covariance removed by the adjustment, and Lambda with wild and cluster-t intervals.
3. Leave-one-trait-out of the proxy. For each trait m, m is dropped from every proxy and the
   pooled cross-half slopes are refitted, then Lambda and its wild interval are recomputed.
   An own implementation with nothing dropped must equal seednoise's residualise to 1e-10.
4. Regularised cross-fitted proxy (primary new target). Recipes are split into 5 folds by a
   seeded permutation (seed 0). For each fold, the pooled seed variances come from the
   training configurations only and are shrunk halfway to the median positive variance,
   v_k = 0.5 max(v_k, 0) + 0.5 median(v > 0); slopes are fitted on training configurations
   with that SD; held-out configurations are residualised with the training SD and slopes.
   Lambda is computed on the stacked held-out residuals. Secondary cells separate the two
   changes, cross-fitting without shrinkage and shrinkage without cross-fitting.
Intervals use 4,999 Rademacher draws with seed 0 on the 25 recipe clusters.
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

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import deviations, estimate, sigma_e  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.mediation import competence, fit_mediation, residualise  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10, (pop.N, pop.K)
print(f"[pop] N={pop.N} R={pop.R} K={pop.K} clusters={len(np.unique(pop.recipe))}", flush=True)
DRAWS, SEED, ALPHA, FOLDS = 4999, 0, 0.5, 5
SHIPPED_AFTER = {"margin": 1.24399, "accuracy": 1.07595}


def summary(p, name):
    e = estimate(p, name, which="all", check=True)
    out = {"Lambda": float(e.lambda_hat), "K_eff": float(e.k_eff)}
    for key, fn in (("wild", lambda: wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=DRAWS, seed=SEED)),
                    ("t", lambda: cluster_t_interval(e.T, e.U, p.recipe))):
        try:
            iv = fn(); out[f"{key}_lo"], out[f"{key}_hi"] = float(iv.lo), float(iv.hi)
        except Exception as error:  # noqa: BLE001
            out[f"{key}_error"] = f"{type(error).__name__}: {error}"
    return out


def proxy(d, sd, drop=None):
    """Leave-one-trait-out mean of standardised deviations, optionally without trait `drop`."""
    if drop is None:
        return competence(d, sd)
    z = d / sd
    keep = np.ones(d.shape[2], bool); keep[drop] = False
    x = np.empty_like(z)
    for j in range(d.shape[2]):
        m = keep.copy(); m[j] = False
        x[:, :, j] = z[:, :, m].mean(axis=2)
    return x


def slopes(dA, dB, xA, xB):
    b = np.empty(dA.shape[2])
    for j in range(dA.shape[2]):
        c = [np.linalg.lstsq(xo[:, :, j].ravel()[:, None], y[:, :, j].ravel(), rcond=None)[0][0]
             for y, xo in ((dA, xB), (dB, xA))]
        b[j] = np.mean(c)
    return b


def clipped_sd(p, name, alpha=0.0):
    v = np.diag(sigma_e(p, name)).copy()
    if alpha > 0:
        v = (1 - alpha) * np.clip(v, 0, None) + alpha * np.median(v[v > 0])
    return np.sqrt(np.clip(v, 1e-12, None)), v


report = {"design": __doc__, "draws": DRAWS, "seed": SEED, "alpha": ALPHA, "folds": FOLDS,
          "traits": list(pop.traits), "phenotypes": {}}
rng = np.random.default_rng(SEED)
recipes = np.unique(pop.recipe)
perm = rng.permutation(recipes)
fold_of = {int(r): i % FOLDS for i, r in enumerate(perm)}
report["fold_of_recipe"] = {str(k): v for k, v in fold_of.items()}

for name in ("margin", "accuracy"):
    t1 = time.time()
    ph = pop.pheno(name)
    dA, dB = deviations(ph.A), deviations(ph.B)
    R = {"unadjusted": summary(pop, name)}

    # 1. Reproduction of the shipped adjustment.
    fit = fit_mediation(pop, name, terms=("x",))
    res = residualise(pop, name, fit)
    R["after_competence_shipped"] = summary(res, list(res.phenotypes)[-1])
    assert abs(R["after_competence_shipped"]["Lambda"] - SHIPPED_AFTER[name]) < 5e-5, R["after_competence_shipped"]
    sd, raw_v = clipped_sd(pop, name)
    xA, xB = proxy(dA, sd), proxy(dB, sd)
    b = slopes(dA, dB, xA, xB)
    assert np.allclose(b, fit.b, rtol=0, atol=1e-12 + 1e-9 * np.abs(fit.b).max()), (b, fit.b)
    rA = dA - b * xA; rB = dB - b * xB
    assert np.allclose(rA, res.pheno(list(res.phenotypes)[-1]).A, atol=1e-10)

    # 2. Audit.
    zsq = np.array([np.mean((dA[:, :, k] / sd[k]) ** 2 + (dB[:, :, k] / sd[k]) ** 2) / 2 for k in range(pop.K)])
    S = sigma_e(pop, name); Sr = sigma_e(res, list(res.phenotypes)[-1])
    R["audit"] = [{"trait": t, "pooled_seed_variance": float(raw_v[k]), "clip_binds": bool(raw_v[k] <= 1e-12),
                   "sd_used": float(sd[k]), "share_of_standardised_input": float(zsq[k] / zsq.sum()),
                   "b": float(b[k]), "diag_after": float(Sr[k, k]),
                   "diag_removed_share": float(1 - Sr[k, k] / S[k, k]) if S[k, k] > 0 else None}
                  for k, t in enumerate(pop.traits)]
    print(f"[{name}] audit {json.dumps(R['audit'])}", flush=True)

    # 3. Leave one trait out of the proxy.
    R["drop_from_proxy"] = {}
    for m, t in enumerate(pop.traits):
        xA_m, xB_m = proxy(dA, sd, m), proxy(dB, sd, m)
        b_m = slopes(dA, dB, xA_m, xB_m)
        p_m = pop.with_phenotype(f"{name}|drop{m}", dA - b_m * xA_m, dB - b_m * xB_m)
        R["drop_from_proxy"][t] = summary(p_m, f"{name}|drop{m}")
    print(f"[{name}] drop {json.dumps({t: round(v['Lambda'], 5) for t, v in R['drop_from_proxy'].items()})}", flush=True)

    # 4. Cross-fitted and regularised proxies.
    def crossfit(alpha):
        oA, oB = np.full_like(dA, np.nan), np.full_like(dB, np.nan)
        per_fold = []
        for f in range(FOLDS):
            test = np.array([fold_of[int(r)] == f for r in pop.recipe])
            tr = pop.subset(np.flatnonzero(~test))
            sd_f, _ = clipped_sd(tr, name, alpha)
            tA, tB = dA[~test], dB[~test]
            b_f = slopes(tA, tB, proxy(tA, sd_f), proxy(tB, sd_f))
            hA, hB = dA[test], dB[test]
            oA[test] = hA - b_f * proxy(hA, sd_f); oB[test] = hB - b_f * proxy(hB, sd_f)
            per_fold.append({"fold": f, "n_test": int(test.sum()), "b": b_f.tolist(), "sd": sd_f.tolist()})
        assert np.isfinite(oA).all() and np.isfinite(oB).all()
        lab = f"{name}|cf{alpha}"
        return summary(pop.with_phenotype(lab, oA, oB), lab), per_fold

    R["crossfit_regularised"], R["crossfit_regularised_folds"] = crossfit(ALPHA)
    R["crossfit_unregularised"], _ = crossfit(0.0)
    sd_s, _ = clipped_sd(pop, name, ALPHA)
    b_s = slopes(dA, dB, proxy(dA, sd_s), proxy(dB, sd_s))
    R["insample_regularised"] = summary(pop.with_phenotype(f"{name}|is", dA - b_s * proxy(dA, sd_s), dB - b_s * proxy(dB, sd_s)), f"{name}|is")
    R["insample_regularised_b"] = b_s.tolist()
    for key in ("unadjusted", "after_competence_shipped", "crossfit_regularised", "crossfit_unregularised", "insample_regularised"):
        print(f"[{name}] {key} {json.dumps(R[key])}", flush=True)
    print(f"[{name}] {time.time() - t1:.0f}s", flush=True)
    report["phenotypes"][name] = R

report["wall_seconds"] = time.time() - t0
(W / "r7_proxy_audit.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
