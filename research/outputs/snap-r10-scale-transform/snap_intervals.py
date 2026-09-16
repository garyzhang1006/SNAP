"""Original-pipeline intervals on the per-configuration moments a C01 run saved.

C01 writes moments.npz with the (C, K, K) cross-half covariance per
configuration. This script forms T_c and U_c with the manifest weights and
applies the original wild cluster bootstrap-t, the cluster-robust t(G-1) and
the configuration percentile bootstrap from the seednoise package, so a grouped
or re-split estimate gets the same interval machinery as the published one.

Usage: python snap_intervals.py --c01 C01_OUT_DIR --dataset SCORES_JSON --out RESULT_JSON
"""
import argparse
import json

import numpy as np

from seednoise.inference import cluster_t_interval, config_bootstrap, wild_bootstrap_t


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--c01", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--draws", type=int, default=4999)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    meta = json.load(open(args.dataset))
    cov = np.load(f"{args.c01}/moments.npz")["covariance"]
    w = np.asarray(meta["weights"], float)
    names = [b["name"] for b in meta["benchmarks"]]
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    recipe = np.array([c["recipe"] for c in meta["configs"]])
    mean = cov.mean(0)
    diag = np.diag(mean)
    out = {"lambda": float(np.sqrt(T.sum() / U.sum())), "T_sum": float(T.sum()), "U_sum": float(U.sum()),
           "aggregate_sd": float(np.sqrt(T.mean())) if T.mean() >= 0 else None,
           "diagonal": dict(zip(names, diag.tolist())), "trace": float(diag.sum()),
           "trace_shares": dict(zip(names, (diag / diag.sum()).tolist())),
           "offdiagonal_sum": float(mean.sum() - diag.sum()),
           "aggregate_offdiagonal_contribution": float((w @ mean @ w) - ((w * w) @ diag))}
    for name, fn in (("wild", lambda: wild_bootstrap_t(T, U, recipe, n_boot=args.draws, seed=args.seed)),
                     ("cluster_t", lambda: cluster_t_interval(T, U, recipe)),
                     ("config", lambda: config_bootstrap(T, U, n_boot=args.draws, seed=args.seed))):
        try:
            iv = fn()
            out[name] = {"lo": iv.lo, "hi": iv.hi, "se": iv.se, "method": iv.method}
        except Exception as error:  # noqa: BLE001
            out[name] = {"error": f"{type(error).__name__}: {error}"}
    json.dump(out, open(args.out, "w"), indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x)
    print(json.dumps({k: out[k] for k in ("lambda", "wild", "cluster_t", "config", "aggregate_sd")}, default=str))


if __name__ == "__main__":
    main()
