"""snap-r3-r2-26 (CPU only): split-half estimate against an analytic diagonal correction on all items.

Question (REBUTTAL_LOG R2-26, R2-13): what does splitting the items cost or buy against the obvious
alternative, which scores every item once and subtracts an analytic item-sampling variance from the
diagonal of the full-battery replicate covariance?

Estimators, per configuration c, all with seednoise at the paper's commit:
  split-half   seednoise.estimator.estimate(pop, name).T and .U, the paper's estimator (1.24395 margin).
  full bank    T_full, U_full = seednoise.estimator.estimate on a Population whose halves are both the
               full-bank trait scores (seednoise.phenotypes.half_scores with an all-True mask), exactly the
               snap-r2-r1-08 construction. With A = B, T_full = 1'S_c 1 / K^2 and U_full = tr(S_c) / K^2
               where S_c is the replicate covariance (divisor R - 1) of the full-bank trait scores.
  analytic     S_c - diag(v_c), with v_cj the item-sampling variance of trait j's full-bank score:
               v_cj = (1/G_j^2) sum_{g in j} MS_g / n_g, MS_g the item-by-run interaction mean square of the
               per-item scores in group g, sum_{r, i in g} (e_icr - ebar_gcr)^2 / ((R-1)(n_g-1)), with
               e_icr the item's score minus its mean over the configuration's runs and ebar_gcr the group
               mean of e for that run (which removes the run's seed shift). G_j is the number of groups
               (57 for MMLU's macro-average, one elsewhere), matching half_scores. Then
               T_an = T_full - sum_j v_cj / K^2 and U_an = U_full - sum_j v_cj / K^2 (off-diagonals carry no
               item noise because traits have disjoint items).
Intervals: seednoise.inference.wild_bootstrap_t (4,999 draws, seed 0) and cluster_t_interval, both on the
25 recipe clusters, and seednoise.inference.cluster_se. Width is hi - lo on the Lambda scale.
Check: the analytic per-trait seed variance mean_c(S_cjj - v_cj) beside the split-half
seednoise.estimator.sigma_e diagonal, and v against seednoise.reliability.variance_components noise2.
"""
import json
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
from seednoise.estimator import estimate, sigma_e  # noqa: E402
from seednoise.inference import cluster_se, cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.phenotypes import half_scores  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
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
K, R, N = len(TRAITS), pop.R, pop.N

cells, ref = {}, None
for f in sorted(run_dir.glob("*.npz")):
    items, meta = load_run(f)
    if ref is None:
        ref = items
    assert np.array_equal(items.item_id, ref.item_id) and np.array_equal(items.group, ref.group)
    m, a = half_scores(items, np.ones(items.n_items, dtype=bool), K)
    cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, m, a, items.margin, items.correct.astype(np.float64)))
keys = [tuple(c) for c in pop.config_ids]
assert all(len(cells[k]) == R for k in keys)

# Group bookkeeping exactly as half_scores builds its macro-average.
gkeys, ginv = np.unique(ref.group, return_inverse=True)
n_g = np.bincount(ginv, minlength=gkeys.size).astype(float)
trait_of_group = np.zeros(gkeys.size, dtype=np.int64)
trait_of_group[ginv] = ref.trait
G_j = np.bincount(trait_of_group, minlength=K)[:K].astype(float)
assert (n_g >= 2).all(), "a group with one item has no interaction mean square"


def item_noise(X):
    """(K,) item-sampling variance of the full-bank trait scores for one configuration, X is (R, n)."""
    e = X - X.mean(axis=0, keepdims=True)
    ss = np.zeros(gkeys.size)
    for r in range(R):
        s1 = np.bincount(ginv, weights=e[r], minlength=gkeys.size)
        s2 = np.bincount(ginv, weights=e[r] ** 2, minlength=gkeys.size)
        ss += s2 - s1 ** 2 / n_g
    ms = ss / ((R - 1) * (n_g - 1))
    return np.bincount(trait_of_group, weights=ms / n_g, minlength=K)[:K] / G_j ** 2


M = np.zeros((N, R, K)); A = np.zeros((N, R, K)); batch = np.zeros((N, R), dtype=np.int64)
V = {MARGIN: np.zeros((N, K)), ACCURACY: np.zeros((N, K))}
for c, k in enumerate(keys):
    rows = sorted(cells[k], key=lambda t: t[0]["batch"])
    for r, (meta, m, a, _, _) in enumerate(rows):
        M[c, r], A[c, r], batch[c, r] = m, a, meta["batch"]
    V[MARGIN][c] = item_noise(np.stack([t[3] for t in rows]))
    V[ACCURACY][c] = item_noise(np.stack([t[4] for t in rows]))
assert np.array_equal(batch, pop.batch)
fixed = Population({MARGIN: Phenotype(MARGIN, M, M), ACCURACY: Phenotype(ACCURACY, A, A)},
                   batch=batch, recipe=pop.recipe, size=pop.size, traits=list(TRAITS), config_ids=pop.config_ids)


def summarise(T, U, recipe):
    th = float(T.sum() / U.sum())
    wb = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=0).as_row()
    try:
        ct = cluster_t_interval(T, U, recipe).as_row()
    except Exception as ex:  # noqa: BLE001
        ct = {"error": f"{type(ex).__name__}: {ex}"}
    return {"lambda": float(np.sqrt(th)) if th >= 0 else float("nan"), "theta": th,
            "cluster_se_theta": cluster_se(T, U, recipe), "wild": wb,
            "wild_width": wb["hi"] - wb["lo"],
            "cluster_t": ct, "cluster_t_width": (ct["hi"] - ct["lo"]) if "hi" in ct else None,
            "sum_T": float(T.sum()), "sum_U": float(U.sum())}


res = {}
for battery, drop in (("all_ten", ()), ("no_boolq", ("boolq",))):
    idx = [j for j, t in enumerate(TRAITS) if t not in drop]
    Kb = len(idx)
    for name in (MARGIN, ACCURACY):
        phs, phf = pop.pheno(name), fixed.pheno(name)
        sp_pop = Population({name: Phenotype(name, phs.A[:, :, idx], phs.B[:, :, idx])}, batch=pop.batch,
                            recipe=pop.recipe, size=pop.size, traits=[TRAITS[j] for j in idx], config_ids=pop.config_ids)
        fx_pop = Population({name: Phenotype(name, phf.A[:, :, idx], phf.B[:, :, idx])}, batch=pop.batch,
                            recipe=pop.recipe, size=pop.size, traits=[TRAITS[j] for j in idx], config_ids=pop.config_ids)
        es, ef = estimate(sp_pop, name, check=False), estimate(fx_pop, name, check=False)
        vsum = V[name][:, idx].sum(axis=1) / Kb ** 2
        T_an, U_an = ef.T - vsum, ef.U - vsum
        split = summarise(es.T, es.U, pop.recipe)
        fixedb = summarise(ef.T, ef.U, pop.recipe)
        anal = summarise(T_an, U_an, pop.recipe)
        S_split = np.diag(sigma_e(sp_pop, name))
        S_full = np.diag(sigma_e(fx_pop, name))
        seed_an = S_full - V[name][:, idx].mean(axis=0)
        noise_half = variance_components(sp_pop, name).noise2
        cell = {"split_half": split, "full_bank_uncorrected": fixedb, "analytic_diagonal_correction": anal,
                "width_ratio_analytic_over_split_wild": anal["wild_width"] / split["wild_width"],
                "width_ratio_analytic_over_split_cluster_t": (anal["cluster_t_width"] / split["cluster_t_width"])
                if anal["cluster_t_width"] and split["cluster_t_width"] else None,
                "se_ratio_analytic_over_split_theta": anal["cluster_se_theta"] / split["cluster_se_theta"],
                "per_trait": {TRAITS[j]: {"seed_var_split": float(S_split[i]), "seed_var_analytic": float(seed_an[i]),
                                          "item_noise_full_analytic": float(V[name][:, j].mean()),
                                          "item_noise_half_split_variance_components": float(noise_half[i])}
                              for i, j in enumerate(idx)},
                "share_of_diag_removed": float(vsum.sum() / ef.U.sum())}
        res.setdefault(battery, {})[name] = cell
        print(f"[{battery} {name}] split {split['lambda']:.4f} [{split['wild']['lo']:.4f}, {split['wild']['hi']:.4f}] w "
              f"{split['wild_width']:.4f} | analytic {anal['lambda']:.4f} [{anal['wild']['lo']:.4f}, {anal['wild']['hi']:.4f}] "
              f"w {anal['wild_width']:.4f} | uncorrected {fixedb['lambda']:.4f} | removed {cell['share_of_diag_removed']:.3f}",
              flush=True)

out = {"results": res, "population": {"N": N, "R": R, "recipes": len(info["recipes"]), "sizes": info["sizes"],
                                      "n_items": int(ref.n_items), "n_groups": int(gkeys.size)},
       "lambda_margin_check": lam, "wall_seconds": time.time() - t0}
(W / "r2_26_analytic_vs_split.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
