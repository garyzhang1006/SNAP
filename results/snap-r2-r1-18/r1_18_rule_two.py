"""snap-r2-r1-18 (CPU only): operating characteristics of the committed PolyPythias rule two.

Extends research/outputs/snap-r1-power/r1_power.py (rule one, 4,000 replicates,
nine seeds at five sizes) with a second item bank at one sixth of bank one's
items, and applies rule two exactly as SNAP compute2/analysis/estimates.py
verdicts() does:

  not supported  cross-bank jackknife lower limit > 1 and the within-minus-cross
                 log-theta difference interval covers zero
  supported      difference interval lower limit > 0, cross-bank upper limit >= 1,
                 and not (cross-bank lower limit > 1)
  undecided      anything else

Intervals follow estimates.seed_jackknife (delete-one-seed jackknife on theta,
t(8), endpoints square-rooted, nan when theta - crit*se < 0) and
estimates.jackknife_logdiff (delete-one-seed jackknife of log theta_within minus
log theta_cross, t(8)); every jackknife replicate recentres the remaining seeds.
The first CHECK replicates of every scenario are also run through the committed
functions themselves (SNAP at commit 6cfedee, cloned from GitHub) and their
verdict labels compared with the vectorised ones, so the rates below are the
committed rule's rates rather than a re-implementation's.

Model, as r1_power.py: Sigma_E is the snap-r6-matched-b margin matrix (4-digit
rounding, PSD-clipped); per-trait item-noise variance of a full bank-one trait
mean is noise_k = v_k (1 - rel_k) / rel_k with r1_power.py's rel vector; a
bank-one half carries 2 noise_k, a bank-two full score 6 noise_k.
Shared-item component at share s (the construction in the supplement's
calibration section): each bank-one half carries a scalar per-run effect that
every benchmark loads on with variance s * 2 noise_k, repeated exactly in the
other half, and the independent part keeps (1 - s) * 2 noise_k. Bank two has
its own independent scalar effect, so nothing is shared across banks.

Scenarios: run covariance at the observed 1.244 (no shared item effect);
independence (diagonal Sigma_E, no shared item effect); independence plus a
0.124 shared-item share; observed covariance plus a 0.124 share.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

t0 = time.time()
W = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path(".")
REPS, CHECK, SIZES, R, K = 4000, 25, 5, 9, 10
SEED = 20260923
CRIT = float(student_t.ppf(0.975, R - 1))
SNAP_COMMIT = "6cfedee87ac52695f96665ecc0a62ecdc97e1c35"

S = np.array([[1.5434e-05,2.8509e-05,-1.5923e-05,6.3360e-05,3.2814e-07,1.1676e-05,1.4808e-05,-4.0919e-07,2.5973e-05,4.4317e-07],
 [2.8509e-05,8.2182e-05,-5.3772e-05,1.3961e-04,8.1074e-07,2.3456e-05,2.8577e-05,1.1207e-06,5.7357e-05,2.8235e-07],
 [-1.5923e-05,-5.3772e-05,1.4337e-03,-7.7178e-05,-2.4860e-06,-9.4041e-06,1.7853e-05,3.5287e-07,-1.9656e-05,-3.3875e-06],
 [6.3360e-05,1.3961e-04,-7.7178e-05,4.3401e-04,1.9061e-06,4.8008e-05,6.9736e-05,-1.1707e-07,1.6556e-04,-1.0158e-06],
 [3.2814e-07,8.1074e-07,-2.4860e-06,1.9061e-06,6.7365e-07,3.9806e-07,1.8321e-07,8.2570e-08,9.8076e-08,-2.3876e-09],
 [1.1676e-05,2.3456e-05,-9.4041e-06,4.8008e-05,3.9806e-07,1.4210e-05,1.0622e-05,-1.8317e-07,1.8578e-05,-8.8690e-08],
 [1.4808e-05,2.8577e-05,1.7853e-05,6.9736e-05,1.8321e-07,1.0622e-05,3.2552e-05,5.6932e-07,3.1616e-05,6.6854e-08],
 [-4.0919e-07,1.1207e-06,3.5287e-07,-1.1707e-07,8.2570e-08,-1.8317e-07,5.6932e-07,7.5772e-07,2.5154e-07,8.4758e-08],
 [2.5973e-05,5.7357e-05,-1.9656e-05,1.6556e-04,9.8076e-08,1.8578e-05,3.1616e-05,2.5154e-07,9.8193e-05,-9.0688e-07],
 [4.4317e-07,2.8235e-07,-3.3875e-06,-1.0158e-06,-2.3876e-09,-8.8690e-08,6.6854e-08,8.4758e-08,-9.0688e-07,1.5477e-07]])
rel = np.array([0.927, 0.584, 0.993, 0.93, 0.757, 0.86, 0.392, 0.273, 0.888, 0.5])
v = np.clip(np.diag(S), 1e-9, None)
noise = v * (1 - rel) / rel
S = (S + S.T) / 2
w_, V_ = np.linalg.eigh(S)
S = (V_ * np.clip(w_, 0, None)) @ V_.T
L_obs = V_ * np.sqrt(np.clip(w_, 0, None))
L_ind = np.diag(np.sqrt(np.diag(S)))
true_obs = float(np.sqrt(S.sum() / np.trace(S)))
BANK2_RATIO = 6.0


def draw(rng, L, share):
    """One replicate: bank-one halves a, b and bank-one full / bank-two full, all (SIZES, R, K)."""
    e = np.einsum("jk,crk->crj", L, rng.normal(size=(SIZES, R, K)))
    u1 = rng.normal(size=(SIZES, R, 1))      # shared scalar, bank one, repeated in both halves
    u2 = rng.normal(size=(SIZES, R, 1))      # bank two's own scalar
    sh1 = u1 * np.sqrt(share * 2 * noise)
    ia = rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * 2 * noise)
    ib = rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * 2 * noise)
    a, b = e + sh1 + ia, e + sh1 + ib
    full1 = (a + b) / 2
    full2 = e + u2 * np.sqrt(share * BANK2_RATIO * noise) + rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * BANK2_RATIO * noise)
    return a, b, full1, full2


def theta(A, B):
    d = A - A.mean(1, keepdims=True)
    f = B - B.mean(1, keepdims=True)
    T = float((d.sum(-1) * f.sum(-1)).sum())
    U = float((d * f).sum())
    return T / U if U != 0 else float("nan")


def loo(A, B):
    return np.array([theta(np.delete(A, r, 1), np.delete(B, r, 1)) for r in range(R)])


def sq(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def jack(A, B):
    th, l = theta(A, B), loo(A, B)
    se = float(np.sqrt((R - 1) / R * np.sum((l - l.mean()) ** 2)))
    return {"point": sq(th), "lo": sq(th - CRIT * se), "hi": sq(th + CRIT * se)}


def logdiff(a, b, f1, f2):
    tw, tc = theta(a, b), theta(f1, f2)
    full = float(np.log(tw) - np.log(tc)) if tw > 0 and tc > 0 else float("nan")
    lw, lc = loo(a, b), loo(f1, f2)
    ok = (lw > 0) & (lc > 0)
    if not ok.all() or not np.isfinite(full):
        return {"point_log_theta_diff": full, "error": "a leave-one-out ratio was not positive"}
    l = np.log(lw) - np.log(lc)
    se = float(np.sqrt((R - 1) / R * np.sum((l - l.mean()) ** 2)))
    return {"point_log_theta_diff": full, "lo": full - CRIT * se, "hi": full + CRIT * se}


def verdict(civ, diff):
    clo, chi = civ["lo"], civ["hi"]
    if np.isfinite(clo) and clo > 1.0 and "lo" in diff and diff["lo"] <= 0.0 <= diff["hi"]:
        return "not supported"
    if "lo" in diff and diff["lo"] > 0.0 and np.isfinite(chi) and chi >= 1.0 and not (np.isfinite(clo) and clo > 1.0):
        return "supported"
    return "undecided"


# ---- the committed functions, for the per-replicate cross-check ------------------
snap = Path("/kaggle/tmp/SNAP")
if not snap.exists():
    subprocess.check_call(["git", "clone", "-q", "https://github.com/garyzhang1006/SNAP.git", str(snap)])
subprocess.check_call(["git", "-C", str(snap), "checkout", "-q", SNAP_COMMIT])
sys.path[:0] = [str(snap / "src"), str(snap / "compute2" / "common"), str(snap / "compute2" / "analysis")]
import estimates as E  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402


def pop_of(A, B):
    N = A.shape[0]
    return Population({MARGIN: Phenotype(MARGIN, A, B), ACCURACY: Phenotype(ACCURACY, A, B)},
                      batch=np.tile(np.arange(R), (N, 1)), recipe=np.arange(N), size=np.arange(N),
                      traits=[f"t{j}" for j in range(K)])


def committed(a, b, f1, f2):
    pw, pc = pop_of(a, b), pop_of(f1, f2)
    res = {"pythia": {"status": "ok",
                      "within_bank1": {"full": {n: {"all": {"lambda": float("nan"), "jackknife": E.seed_jackknife(pw, n)}} for n in (MARGIN, ACCURACY)}},
                      "cross_bank": {"summary": True, "full": {n: {"all": {"lambda": float("nan"), "jackknife": E.seed_jackknife(pc, n)}} for n in (MARGIN, ACCURACY)}},
                      "within_minus_cross": {n: {"full": E.jackknife_logdiff(pw, pc, n)} for n in (MARGIN, ACCURACY)}}}
    v = E.verdicts(res)
    return v[f"R2_pythia_identification_{MARGIN}"], v[f"R1_pythia_replicates_{MARGIN}"]


SCEN = {"run_cov_1244_share0": (L_obs, 0.0), "independence_share0": (L_ind, 0.0),
        "independence_share0124": (L_ind, 0.124), "run_cov_1244_share0124": (L_obs, 0.124)}
out = {"design": {"reps": REPS, "sizes": SIZES, "seeds": R, "traits": K, "bank2_item_ratio": 1 / BANK2_RATIO,
                  "seed": SEED, "t_crit": CRIT, "true_lambda_run_cov": true_obs, "snap_commit": SNAP_COMMIT,
                  "rule_source": "SNAP compute2/analysis/estimates.py verdicts(), seed_jackknife(), jackknife_logdiff()"},
       "scenarios": {}}
for name, (L, share) in SCEN.items():
    rng = np.random.default_rng(SEED)
    labels, lam_w, lam_c, r1pass, dpt = [], [], [], [], []
    mism, checked = 0, 0
    for i in range(REPS):
        a, b, f1, f2 = draw(rng, L, share)
        jw, jc, d = jack(a, b), jack(f1, f2), logdiff(a, b, f1, f2)
        lab = verdict(jc, d)
        labels.append(lab)
        lam_w.append(jw["point"]); lam_c.append(jc["point"]); dpt.append(d["point_log_theta_diff"])
        r1pass.append(bool(np.isfinite(jw["lo"]) and jw["lo"] > 1.0))
        if i < CHECK:
            r2, r1 = committed(a, b, f1, f2)
            checked += 1
            if r2["shared_item_explanation"] != lab or r1["pass"] != r1pass[-1]:
                mism += 1
    labels = np.array(labels)
    row = {"shared_item_share": share,
           "rates": {k: float((labels == k).mean()) for k in ("not supported", "supported", "undecided")},
           "rule_one_pass_rate": float(np.mean(r1pass)),
           "within_lambda_median": float(np.nanmedian(lam_w)), "within_lambda_5_95": [float(x) for x in np.nanpercentile(lam_w, [5, 95])],
           "cross_lambda_median": float(np.nanmedian(lam_c)), "cross_lambda_5_95": [float(x) for x in np.nanpercentile(lam_c, [5, 95])],
           "cross_lambda_undefined_share": float(np.mean(~np.isfinite(lam_c))),
           "logdiff_median": float(np.nanmedian(dpt)),
           "committed_function_check": {"replicates": checked, "label_mismatches": mism}}
    row["mc_se_max"] = float(np.sqrt(max(p * (1 - p) for p in row["rates"].values()) / REPS))
    out["scenarios"][name] = row
    print(f"[{name}] {row['rates']} R1 pass {row['rule_one_pass_rate']:.3f} within med {row['within_lambda_median']:.3f} "
          f"cross med {row['cross_lambda_median']:.3f} check {checked} mismatches {mism} {time.time() - t0:.0f}s", flush=True)
out["wall_seconds"] = time.time() - t0
(W / "r1_18_rule_two.json").write_text(json.dumps(out, indent=1))
print("[done]", round(time.time() - t0), "s")
