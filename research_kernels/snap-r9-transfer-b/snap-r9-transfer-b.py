"""R9 the transfer question again, with the accuracy design supplying the correction.

Design fixed before running (2026-09-16, written 12:05 EDT). snap-r9-transfer estimated the correction on
the shipped margin design, whose true ratio is 1.245, and carried it to targets from 1.00 to 1.60. It
holds nominal size only where the two ratios agree, turns conservative below and under-corrects above, at
0.101 for a target of 1.50 against 0.188 with no correction at all. That result came from one source, and
a reader deciding whether to borrow a published ratio will want to know whether the shape depends on
which design produced it. This run repeats the identical sweep with the accuracy design as the source,
whose true ratio is 1.078 and whose estimate is noisier at a standard deviation near 0.099. The two runs
answer the same question from opposite ends, because a correction near one can only under-correct as the
target rises, and its extra estimation noise is the second thing worth pricing. Everything else is
unchanged, so the two sweeps can be read side by side. Seed 20260950 with an offset of twenty six hundred
keeps the draws distinct.
"""
import json, platform, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")

Z = 1.959963984540054
SEED, REPS = 20260950, 8000
K, RUNS, RECIPES, SIZES = 10, 3, 25, 5
SOURCE = {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45}
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
    src_hats[rep] = estimate_lambda(SOURCE, np.random.default_rng([SEED, 2600, rep]))
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
        tgt_hats[rep] = estimate_lambda(tgt_cell, np.random.default_rng([SEED, ti + 2700, rep]))
    tgt_ok = np.isfinite(tgt_hats)
    out = {"lambda_target": lam_t, "lambda_target_check": lam_check, "rho_target": rho_t,
           "matched_hat_mean": float(tgt_hats[tgt_ok].mean()),
           "matched_hat_sd": float(tgt_hats[tgt_ok].std(ddof=1)),
           "matched_undefined": float(np.mean(~tgt_ok)), "rules": {}}
    gen = np.random.default_rng([SEED, ti + 2800])
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
(W / "r9_transfer_b.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
