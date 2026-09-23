"""snap-r5-shared-bound (CPU only): the largest uniform shared item share the cross-format diagnostic allows.

Extends snap-r3-r2-02 (results/snap-r3-r2-02/r2_02.py), whose setup, data sources, injection model and sums
are reused verbatim. Answers claim_audit CA2 and kill_argument KA1 (work/rebuttal/r5): r2_02 excluded the
share that alone explains margin inflation 1.244, but a smaller share could survive the observed interval.

Model (the r2_02 "explain" reading). Each half's item noise on trait k is sigma_k (sqrt(q) f + sqrt(1 - q) z_k),
f one scalar per run shared by all ten benchmarks and identical in both halves, which adds q sigma_j sigma_k to
every cross-half covariance entry. ASSUMPTION: zero off-diagonal cross-benchmark seed covariance, so every
off-diagonal entry of T comes from the shared component and the observed sum U is the denominator. Then
  Lambda(q) = sqrt(1 + N q A / sum U)     A = per-config sum_{j != k} sqrt(v_j v_k) / K^2 (all 90 pairs)
  D(q)      = sqrt(1 + N q C / sum U)     C = the same over the 54 cross-format ordered pairs
D(q) >= 1 for q >= 0, so the largest share with D(q) <= L is q_L = (L^2 - 1) sum U / (N C) for L >= 1, and
no positive share satisfies L < 1. The share's within-battery inflation is Lambda(q_L), and it accounts for
(Lambda(q_L) - 1) / (Lambda_obs - 1) of the observed excess on the Lambda scale and N q_L A / (sum T - sum U)
of it on the covariance scale.

Observed cross-format values are recomputed here with the r2_02/r1_50 code and asserted equal to the stored
snap-r2-r1-50 values (copied below from results/snap-r2-r1-50/r1_50_crossformat_boot.json).
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

# results/snap-r2-r1-50/r1_50_crossformat_boot.json, results/<name>/cross_format_all_ten
R1_50 = {MARGIN: {"point": 0.9211891046274687, "lo": 0.8006569396931505, "hi": 1.034729865199787,
                  "lambda_full": 1.2439499117191137},
         ACCURACY: {"point": 0.9651889498004318, "lo": 0.8483992935798912, "hi": 1.063438097874525,
                    "lambda_full": 1.0783733870898096}}
PAPER = {MARGIN: (0.921, 0.801, 1.035), ACCURACY: (0.965, 0.848, 1.063)}


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
    sum_off_all = float((ss * offd_all).sum()) / K ** 2
    sum_off_cross = float((ss * offd_cross).sum()) / K ** 2
    sT, sU, sTm = float(T_all.sum()), float(U.sum()), float(Tm.sum())

    ow = wild(Tm, U)
    lam_obs = float(np.sqrt(sT / sU))
    ref = R1_50[name]
    for key, val in (("point", ow["point"]), ("lo", ow["lo"]), ("hi", ow["hi"]), ("lambda_full", lam_obs)):
        assert abs(val - ref[key]) < 1e-9, f"[{name}] recomputed {key} {val} differs from snap-r2-r1-50 {ref[key]}"

    def lam_of(q):
        return float(np.sqrt(1.0 + N * q * sum_off_all / sU))

    def diag_of(q):
        return float(np.sqrt(1.0 + N * q * sum_off_cross / sU))

    q_star = (sT - sU) / (N * sum_off_all)

    def bound(limit):
        if limit < 1.0:
            return {"limit": limit, "largest_share": 0.0, "binding": True,
                    "note": "D(q) >= 1 for every q >= 0, so no positive uniform share keeps the diagnostic at or "
                            "below a limit under 1; under zero seed covariance the observed value below 1 already "
                            "requires negative cross-format seed covariance",
                    "within_battery_lambda_from_share": 1.0, "fraction_of_excess_lambda_scale": 0.0,
                    "fraction_of_excess_covariance_scale": 0.0}
        q = (limit ** 2 - 1.0) * sU / (N * sum_off_cross)
        lam = lam_of(q)
        assert abs(diag_of(q) - limit) < 1e-12
        return {"limit": limit, "largest_share": float(q), "binding": bool(q < q_star),
                "induced_cross_format_diagnostic": diag_of(q),
                "within_battery_lambda_from_share": lam,
                "fraction_of_excess_lambda_scale": float((lam - 1.0) / (lam_obs - 1.0)),
                "fraction_of_excess_covariance_scale": float(N * q * sum_off_all / (sT - sU)),
                "share_exceeds_one": bool(q > 1.0)}

    b_hi, b_hi_paper = bound(float(ow["hi"])), bound(PAPER[name][2])
    b_pt, b_pt_paper = bound(float(ow["point"])), bound(PAPER[name][0])
    # With the share at the upper-limit bound, the cross-format seed covariance sum (per the mask, off-diagonal)
    # that the observed point then requires.
    seed_cross_at_hi = sTm - sU - N * b_hi["largest_share"] * sum_off_cross
    res[name] = {
        "observed": {"lambda_full": lam_obs, "excess_lambda_scale": lam_obs - 1.0,
                     "cross_format_point": float(np.sqrt(sTm / sU)), "cross_format_wild": ow,
                     "matches_snap_r2_r1_50": True},
        "explain_share_q_star": float(q_star), "explain_induced_cross_format": diag_of(q_star),
        "bound_at_observed_upper_limit": b_hi, "bound_at_paper_upper_limit_rounded": b_hi_paper,
        "bound_at_observed_point": b_pt, "bound_at_paper_point_rounded": b_pt_paper,
        "implied_cross_format_seed_cov_sum_zero_share": float(sTm - sU),
        "implied_cross_format_seed_cov_sum_at_upper_bound_share": float(seed_cross_at_hi),
        "negative_v_clipped_to_zero": n_neg,
        "sums": {"sum_T": sT, "sum_U": sU, "sum_T_cross_mask": sTm, "N": N,
                 "per_config_offdiag_all_sqrtvv_over_K2": sum_off_all,
                 "per_config_offdiag_cross_sqrtvv_over_K2": sum_off_cross},
    }
    print(f"[{name}] obs Lambda {lam_obs:.4f} cross {ow['point']:.4f} [{ow['lo']:.4f}, {ow['hi']:.4f}] | q* {q_star:.4f} | "
          f"hi: q {b_hi['largest_share']:.4f} Lambda {b_hi['within_battery_lambda_from_share']:.4f} "
          f"frac {b_hi['fraction_of_excess_lambda_scale']:.4f} (cov {b_hi['fraction_of_excess_covariance_scale']:.4f}) | "
          f"point: q {b_pt['largest_share']:.4f}", flush=True)

out = {"results": res, "formats": FORMAT,
       "assumption_zero_seed_covariance": (
           "Zero off-diagonal cross-benchmark seed covariance: every off-diagonal cross-half covariance is "
           "attributed to the uniform shared item component, and the observed sum U is the denominator. Negative "
           "cross-format seed covariance would offset the component, so under that alternative a larger share is "
           "compatible with the observed diagnostic and these bounds do not hold."),
       "injection_model": ("per-half item noise on trait k is sigma_k (sqrt(q) f + sqrt(1-q) z_k); f is one scalar "
                           "per run shared by all ten benchmarks and identical in both halves (rho_f = 1); z_k "
                           "independent. Adds q sigma_j sigma_k to every cross-half covariance entry. sigma_k^2 = "
                           "seednoise.reliability.variance_components(pop, name).noise2. Same as snap-r3-r2-02."),
       "formulas": {"lambda": "sqrt(1 + N q A / sum U)", "cross_format": "sqrt(1 + N q C / sum U)",
                    "largest_share": "(L^2 - 1) sum U / (N C) for L >= 1, else 0"},
       "observed_source": "results/snap-r2-r1-50/r1_50_crossformat_boot.json (recomputed and asserted equal)",
       "paper_values": {"cross_format_margin": list(PAPER[MARGIN]), "cross_format_accuracy": list(PAPER[ACCURACY])},
       "wall_seconds": time.time() - t0}
(W / "r5_shared_bound.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
