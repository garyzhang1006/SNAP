"""R9 what the plug-in correction costs when it is carried to a comparison it was not measured on.

Design fixed before running (2026-09-16, written 11:05 EDT). snap-r9-decision showed that multiplying an
independence standard error by an estimate of Lambda returns a decision rule to nominal size, and
snap-r9-runs showed that extra runs never repair the uncorrected rule. Both of those measured the
correction on the same population the comparison was drawn from, which is the friendly case and not the
one a practitioner is in. Anyone using this correction will estimate Lambda once, on one battery and one
model family, and then apply it to a comparison whose own dependence they have not measured. A reviewer
should ask what that transfer costs, and the paper should answer before they do.
This run measures it. The correction is estimated from the shipped design on a margin-like population
whose true Lambda is near 1.2446, exactly as in the first decision run, and it is then applied to
comparisons whose own true Lambda is swept from 1.00 to 1.60. For each target it reports the declare rate
at a true gap of zero for four rules, an uncorrected independence rule, the transferred plug-in rule, a
matched plug-in rule that is re-estimated on the target population, and an oracle that knows the target
Lambda. The transferred rule is the honest one, and the gap between it and the matched rule is the price
of transfer. It also reports the same rates at a one standard deviation gap so the power side is visible.
Seed 20260946 with an offset of eighteen hundred keeps the draws distinct. A transferred rule that holds
near 0.05 across the sweep makes the recommendation portable, and one that fails at the ends tells a
reader to re-estimate on their own battery, which is a useful instruction either way.
"""
import json, platform, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")

Z = 1.959963984540054
SEED, REPS = 20260946, 8000
K, RUNS, RECIPES, SIZES = 10, 3, 25, 5
SOURCE = {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73}
# Each target is a compound-symmetric truth whose Lambda is set by rho alone, since with flat weights
# Lambda^2 = (1 + (k - 1) rho) / 1, so rho = (Lambda^2 - 1) / (k - 1).
TARGET_LAMBDAS = (1.00, 1.05, 1.10, 1.20, 1.2446, 1.30, 1.40, 1.50, 1.60)
GAPS = (0.0, 1.0)


def rho_for(lam, k=K):
    return (lam ** 2 - 1.0) / (k - 1.0)


def estimate_lambda(cell, rng):
    """One replicate of the shipped design, returning the cross-half estimate of Lambda."""
    rho = cell["rho"]
    truth = (1 - rho) * np.eye(K) + rho * np.ones((K, K))
    n = RECIPES * SIZES
    latent = rng.multivariate_normal(np.zeros(K), truth, size=(n, RUNS))
    noise = float(cell["noise_sd"])
    a = latent + rng.normal(size=latent.shape) * noise
    b = latent + rng.normal(size=latent.shape) * noise
    w = np.full(K, 1.0 / K)
    da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (RUNS - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    th = float(np.sum(T)) / float(np.sum(U))
    return float(np.sqrt(th)) if th > 0 else float("nan")


w = np.full(K, 1.0 / K)
print("[source] estimating the transferred correction", flush=True)
src_hats = np.empty(REPS)
for rep in range(REPS):
    src_hats[rep] = estimate_lambda(SOURCE, np.random.default_rng([SEED, 1800, rep]))
src_ok = np.isfinite(src_hats)
src_truth = float(np.sqrt((1.0 + (K - 1) * SOURCE["rho"])))
report = {"design": __doc__, "seed": SEED, "reps": REPS, "z": Z,
          "source": {"name": SOURCE["name"], "rho": SOURCE["rho"], "noise_sd": SOURCE["noise_sd"],
                     "lambda_true": src_truth,
                     "lambda_hat_mean": float(src_hats[src_ok].mean()),
                     "lambda_hat_sd": float(src_hats[src_ok].std(ddof=1)),
                     "undefined": float(np.mean(~src_ok))},
          "targets": {}}
print(f"[source] {json.dumps(report['source'], default=float)[:400]}", flush=True)

for ti, lam_t in enumerate(TARGET_LAMBDAS):
    t1 = time.time()
    rho_t = rho_for(lam_t)
    truth_t = (1 - rho_t) * np.eye(K) + rho_t * np.ones((K, K))
    v_full = float(w @ truth_t @ w)
    v_diag = float((w * w) @ np.diag(truth_t))
    lam_check = float(np.sqrt(v_full / v_diag))
    # The matched rule re-estimates on the target population, at the same item noise as the source.
    tgt_cell = {"rho": rho_t, "noise_sd": SOURCE["noise_sd"]}
    tgt_hats = np.empty(REPS)
    for rep in range(REPS):
        tgt_hats[rep] = estimate_lambda(tgt_cell, np.random.default_rng([SEED, ti + 1900, rep]))
    tgt_ok = np.isfinite(tgt_hats)
    out = {"lambda_target": lam_t, "lambda_target_check": lam_check, "rho_target": rho_t,
           "matched_hat_mean": float(tgt_hats[tgt_ok].mean()),
           "matched_hat_sd": float(tgt_hats[tgt_ok].std(ddof=1)),
           "matched_undefined": float(np.mean(~tgt_ok)), "rules": {}}
    gen = np.random.default_rng([SEED, ti + 2000])
    se_true = np.sqrt(2.0 * v_full)
    se_indep = np.sqrt(2.0 * v_diag)
    for gap in GAPS:
        delta = gap * np.sqrt(v_full)
        observed = delta + gen.normal(size=REPS) * se_true
        rules = {"independence": np.full(REPS, se_indep),
                 "transferred": src_hats * se_indep,
                 "matched": tgt_hats * se_indep,
                 "oracle": np.full(REPS, lam_check * se_indep)}
        cellout = {}
        for name, se in rules.items():
            keep = np.isfinite(se)
            fire = np.abs(observed[keep]) > Z * se[keep]
            p = float(np.mean(fire))
            cellout[name] = {"declare_rate": p, "mc_se": float(np.sqrt(p * (1 - p) / fire.size))}
        out["rules"][f"gap{gap}"] = cellout
        print(f"[target{lam_t}/gap{gap}] " +
              json.dumps({k: round(v['declare_rate'], 4) for k, v in cellout.items()}), flush=True)
    out["seconds"] = time.time() - t1
    report["targets"][f"lambda{lam_t}"] = out

report["wall_seconds"] = time.time() - t0
(W / "r9_transfer.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
