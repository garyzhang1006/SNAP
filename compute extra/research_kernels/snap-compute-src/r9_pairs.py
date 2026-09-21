"""Build snap-pairs-v1 from a C01 moments file for the R9 decision analysis.

For every pair of recipes at the same size, the compared quantities are the
three-run means of the equal-weight benchmark average. Under the cross-half
identity the run variance of one run's average is T_c, so the variance of a
three-run mean is T_c / R. Runs are seed-aligned across recipes at a size
(seed 2, 14, 15 below 1B and 2, 4, 5 at 1B), so the paired covariance between
two recipes' means is estimated from the cross-half, cross-configuration
products of seed-matched run deviations, divided by R. The observed gap is the
difference of the two three-run means of the full-item average (mean of the
two halves). Negative or infeasible moments are passed through for C08 to flag.

Usage: python r9_pairs.py --c01 C01_DIR --dataset SCORES_JSON --out PAIRS_JSON
"""
import argparse
import itertools
import json

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--c01", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    meta = json.load(open(args.dataset))
    m = np.load(f"{args.c01}/moments.npz")
    a, b = m["half_a"], m["half_b"]                      # (C, R, K)
    w = np.asarray(meta["weights"], float)
    R = a.shape[1]
    ya, yb = a @ w, b @ w                                # (C, R) aggregate half scores
    da, db = ya - ya.mean(1, keepdims=True), yb - yb.mean(1, keepdims=True)
    T = (da * db).sum(1) / (R - 1)                       # per-configuration single-run aggregate variance
    full_mean = ((ya + yb) / 2).mean(1)
    cfgs = meta["configs"]
    seeds = [[r["seed"] for r in c["runs"]] for c in cfgs]
    pairs = []
    by_size = {}
    for i, c in enumerate(cfgs):
        by_size.setdefault(c["size"], []).append(i)
    for size, idx in by_size.items():
        for i, j in itertools.combinations(idx, 2):
            if seeds[i] != seeds[j]:
                continue                                 # only seed-aligned pairs carry a paired covariance
            cross = ((da[i] * db[j]).sum() + (da[j] * db[i]).sum()) / (2 * (R - 1))
            pairs.append({"id": f"{cfgs[i]['recipe']}|{cfgs[j]['recipe']}|{size}",
                          "size": size, "seeds": seeds[i],
                          "variance_a": float(T[i] / R), "variance_b": float(T[j] / R),
                          "covariance_ab": float(cross / R),
                          "observed_gap": float(full_mean[i] - full_mean[j]),
                          "single_run_variance_a": float(T[i]), "single_run_variance_b": float(T[j])})
    out = {"schema": "snap-pairs-v1", "pairs": pairs,
           "basis": {"runs_per_mean": R, "variance": "cross-half aggregate T_c divided by R",
                     "covariance": "seed-matched cross-half cross-configuration product divided by R",
                     "gap": "difference of three-run means of the full-item equal-weight average"}}
    json.dump(out, open(args.out, "w"), indent=1)
    v = np.array([p["variance_a"] + p["variance_b"] for p in pairs])
    c = np.array([p["covariance_ab"] for p in pairs])
    print(json.dumps({"pairs": len(pairs), "median_sum_variance": float(np.median(v)),
                      "median_covariance": float(np.median(c)), "share_cov_positive": float((c > 0).mean()),
                      "median_2cov_over_sum": float(np.median(2 * c / v))}))


if __name__ == "__main__":
    main()
