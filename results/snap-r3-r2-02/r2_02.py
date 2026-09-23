"""snap-r3-r2-02 (CPU only): the cross-format diagnostic that a uniform shared item component would induce.

Paper (main.tex, Sec 2): "Cross-format covariances alone give inflation 0.921 [0.801, 1.035] ... which
constrains a uniform component of that size", where "that size" is the 0.124 share of item-noise
variance that reproduces 1.244 in snap-r6-sharednoise. results/snap-r2-r1-50 computed the observed
diagnostic; this kernel computes what the diagnostic would read if a uniform component were present.

Injection model (the snap-r6-sharednoise generator, applied to the released noise scales). Each half's
item noise on trait k is sigma_k (sqrt(q) f + sqrt(1 - q) z_k), with f one scalar per run shared by all
ten benchmarks and identical in the two halves (rho_f = 1), z_k independent. That adds q sigma_j sigma_k
to every entry (j, k) of the cross-half covariance, diagonal included. sigma_k^2 is the per-half
item-noise variance v_k from seednoise.reliability.variance_components (the committed function that
splits within-configuration variance into seed and item noise on the released runs).

Per configuration, with seednoise at the paper's commit:
  pA, pB    seednoise.estimator.half_projections(half scores, contrast_basis(R))
  T_mask    (1/K^2) mean over contrasts of sum_{j,k in mask} pA_j pB_k (the r1_50 construction; mask =
            diagonal plus the 54 of 90 ordered pairs whose traits differ in format)
  U         (1/K^2) sum_j pA_j pB_j, equal to seednoise.estimator.estimate(...).U (asserted)
  interval  seednoise.inference.wild_bootstrap_t (4,999 draws, seed 0, 25 recipe clusters)

Three readings are reported:
  explain   the uniform component carries the whole excess of the observed full-matrix ratio, with no
            off-diagonal seed covariance. The observed diagonal U already contains q v_k, so the implied
            share is q* = (sum T - sum U) / (N sum_{j != k} sqrt(v_j v_k) / K^2), and the induced
            cross-format diagnostic is sqrt((sum U + N q* sum_{mask, j != k} sqrt(v_j v_k)/K^2) / sum U).
  q0124     the same no-seed-covariance model at exactly q = 0.124 on the released v_k: the full-matrix
            ratio and the cross-format diagnostic it induces.
  additive  q = 0.124 added on top of the observed per-configuration T and U (numerator every masked
            entry, denominator the diagonal), with the wild interval, i.e. what the observed diagnostic
            would read if the released runs also carried such a component.
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
from seednoise.estimator import contrast_basis, estimate, half_projections  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402

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

FORMAT = {"arc_challenge": "mc", "arc_easy": "mc", "boolq": "yesno", "csqa": "mc", "hellaswag": "cloze",
          "mmlu": "mc", "openbookqa": "mc", "piqa": "cloze", "socialiqa": "mc", "winogrande": "cloze"}
Q = 0.124
Wb = contrast_basis(pop.R)
K, N = len(TRAITS), pop.N
fmt = [FORMAT[t] for t in TRAITS]
eye = np.eye(K)
cross = np.array([[1.0 if (j == k or fmt[j] != fmt[k]) else 0.0 for k in range(K)] for j in range(K)])
offd_all, offd_cross = 1.0 - eye, cross - eye


def wild(T, U):
    return wild_bootstrap_t(T, U, pop.recipe, n_boot=4999, seed=0).as_row()


res = {}
for name in (MARGIN, ACCURACY):
    ph = pop.pheno(name)
    pA, pB = half_projections(ph.A, Wb), half_projections(ph.B, Wb)
    T_all = np.einsum("ndj,ndk,jk->nd", pA, pB, np.ones((K, K))).mean(axis=1) / K ** 2
    U = np.einsum("ndj,ndj->nd", pA, pB).mean(axis=1) / K ** 2
    e = estimate(pop, name, check=False)
    assert np.allclose(T_all, e.T, rtol=1e-10, atol=1e-18) and np.allclose(U, e.U, rtol=1e-10, atol=1e-18)
    Tm = np.einsum("ndj,ndk,jk->nd", pA, pB, cross).mean(axis=1) / K ** 2

    comp = variance_components(pop, name)
    v = np.asarray(comp.noise2, float)
    n_neg = int((v < 0).sum())
    s = np.sqrt(np.clip(v, 0.0, None))
    ss = np.outer(s, s)
    sum_off_all = float((ss * offd_all).sum()) / K ** 2      # per configuration
    sum_off_cross = float((ss * offd_cross).sum()) / K ** 2
    sum_diag = float(np.trace(ss)) / K ** 2
    sT, sU, sTm = float(T_all.sum()), float(U.sum()), float(Tm.sum())

    q_star = (sT - sU) / (N * sum_off_all)
    explain_diag = float(np.sqrt((sU + N * q_star * sum_off_cross) / sU))
    uniform_pair_formula = float(np.sqrt(1.0 + (54 / 90) * (sT / sU - 1.0)))

    U_seed = sU - N * Q * sum_diag
    q_full = float(np.sqrt((sU + N * Q * sum_off_all) / sU))
    q_cross = float(np.sqrt((sU + N * Q * sum_off_cross) / sU))

    T_add, U_add = Tm + Q * (sum_off_cross + sum_diag), U + Q * sum_diag
    T_add_all = T_all + Q * (sum_off_all + sum_diag)

    res[name] = {
        "observed": {"lambda_full": float(np.sqrt(sT / sU)), "cross_format_point": float(np.sqrt(sTm / sU)),
                     "cross_format_wild": wild(Tm, U)},
        "item_noise_per_half_v_k": dict(zip(TRAITS, map(float, v))),
        "seed_variance_sigma_e2_k": dict(zip(TRAITS, map(float, comp.sigma_e2))),
        "negative_v_clipped_to_zero": n_neg,
        "explain": {"implied_share_q_star": float(q_star), "induced_cross_format_diagnostic": explain_diag,
                    "equal_pair_weight_check": uniform_pair_formula,
                    "excluded_by_observed_wild_interval": None},
        "q0124": {"share": Q, "induced_full_matrix_lambda": q_full, "induced_cross_format_diagnostic": q_cross,
                  "diag_share_of_U": float(N * Q * sum_diag / sU), "U_seed_after_removing_share": float(U_seed)},
        "additive": {"share": Q, "full_matrix_lambda": float(np.sqrt(T_add_all.sum() / U_add.sum())),
                     "cross_format_point": float(np.sqrt(T_add.sum() / U_add.sum())),
                     "cross_format_wild": wild(T_add, U_add)},
        "sums": {"sum_T": sT, "sum_U": sU, "sum_T_cross_mask": sTm, "N": N,
                 "per_config_offdiag_all_sqrtvv_over_K2": sum_off_all,
                 "per_config_offdiag_cross_sqrtvv_over_K2": sum_off_cross,
                 "per_config_diag_v_over_K2": sum_diag},
    }
    ow = res[name]["observed"]["cross_format_wild"]
    for key, val in (("explain", explain_diag), ("q0124", q_cross)):
        res[name][key]["excluded_by_observed_wild_interval"] = bool(not (ow["lo"] <= val <= ow["hi"]))
    print(f"[{name}] observed cross {ow['point']:.4f} [{ow['lo']:.4f}, {ow['hi']:.4f}] | explain q*={q_star:.4f} "
          f"-> cross {explain_diag:.4f} | q=0.124 -> full {q_full:.4f} cross {q_cross:.4f} | additive cross "
          f"{res[name]['additive']['cross_format_wild']['point']:.4f} [{res[name]['additive']['cross_format_wild']['lo']:.4f}, "
          f"{res[name]['additive']['cross_format_wild']['hi']:.4f}] | neg v {n_neg}", flush=True)

out = {"results": res, "formats": FORMAT,
       "injection_model": ("per-half item noise on trait k is sigma_k (sqrt(q) f + sqrt(1-q) z_k); f is one scalar "
                           "per run shared by all ten benchmarks and identical in both halves (rho_f = 1); z_k "
                           "independent. Adds q sigma_j sigma_k to every cross-half covariance entry, diagonal "
                           "included. sigma_k^2 = seednoise.reliability.variance_components(pop, name).noise2 "
                           "(population-level, per half). Generator from snap-r6-sharednoise (seed 20260920), "
                           "where q = 0.1242 reproduced 1.2439 at noise 0.73 on a unit-variance latent."),
       "readings": {"explain": "no off-diagonal seed covariance; the shared component carries the whole observed "
                               "excess of the full-matrix ratio; share q* solved from sum T - sum U",
                    "q0124": "no off-diagonal seed covariance; q fixed at 0.124 on the released v_k",
                    "additive": "q = 0.124 added to the observed per-configuration T and U"},
       "paper_values": {"cross_format_margin": [0.921, 0.801, 1.035], "cross_format_accuracy": [0.965, 0.848, 1.063],
                        "share_reproducing_margin": 0.124, "share_reproducing_accuracy": 0.009},
       "wall_seconds": time.time() - t0}
(W / "r2_02_shared_component_crossformat.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
