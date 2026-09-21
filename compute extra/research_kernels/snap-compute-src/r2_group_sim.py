"""R2 simulation: item splits versus passage-group splits when passages carry run effects.

One benchmark of the ten has passage structure drawn from a supplied group
size histogram. Each run gets, on top of its item-general effect, a
run-by-passage interaction with standard deviation tau that is shared by every
question on that passage. Question-level errors are independent. Under an item
split, a passage can land on both halves and its interaction leaks into the
cross-half diagonal; under a passage split it cannot. The target is the
item-general covariance, so the grouped estimator should be unbiased for the
benchmark's diagonal and the item-split estimator should be biased upward by
the leaked interaction.

Usage: python r2_group_sim.py --out OUT --histogram HIST_JSON --reps B --seed S
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np


def group_sizes(hist, rng):
    sizes = np.array([int(k) for k in hist], int)
    counts = np.array([hist[k] for k in hist], int)
    groups = np.repeat(sizes, counts)
    return rng.permutation(groups)


def split_group(groups_of_items, rng):
    ids = np.unique(groups_of_items)
    order = rng.permutation(ids.size)
    left = set(ids[order[: ids.size // 2]])
    return np.array([0 if g in left else 1 for g in groups_of_items])


def one_rep(cfg, tau, rng):
    k, r, c = 10, 3, cfg["configs"]
    rho = cfg["rho"]
    scale = np.asarray(cfg["trait_scales"], float)
    truth = ((1 - rho) * np.eye(k) + rho * np.ones((k, k))) * np.outer(scale, scale)
    E = rng.multivariate_normal(np.zeros(k), truth, size=(c, r))          # (C, R, K) item-general run effects
    sizes = cfg["sizes_per_trait"]
    w = np.full(k, 1.0 / k)
    results = {}
    # Benchmark 0 carries passages; its items are laid out from the histogram.
    g_items = group_sizes(cfg["histogram"], rng)
    passage_of_item = np.repeat(np.arange(g_items.size), g_items)
    n0 = passage_of_item.size
    assignments = {"item": rng.integers(0, 2, size=n0), "group": split_group(passage_of_item, rng)}
    # Force both halves nonempty for the item split.
    for mode, assign in assignments.items():
        a = np.zeros((c, r, k)); b = np.zeros((c, r, k))
        for j in range(k):
            n = n0 if j == 0 else sizes[j]
            noise = rng.normal(size=(c, r, n)) * cfg["item_noise_sd"][j]
            y = E[:, :, j][:, :, None] + noise
            if j == 0 and tau > 0:
                inter = rng.normal(size=(c, r, g_items.size)) * tau
                y = y + inter[:, :, passage_of_item]
            if j == 0:
                h = assign
            else:
                h = rng.integers(0, 2, size=n)
            a[:, :, j] = y[:, :, h == 0].mean(-1)
            b[:, :, j] = y[:, :, h == 1].mean(-1)
        da = a - a.mean(1, keepdims=True); db = b - b.mean(1, keepdims=True)
        cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
        cov = ((cross + cross.transpose(0, 2, 1)) / 2).mean(0)
        T = float(w @ cov @ w); U = float((w * w) @ np.diag(cov))
        results[mode] = {"lambda": float(np.sqrt(T / U)) if T >= 0 and U > 0 else None,
                         "boolq_diag": float(cov[0, 0]), "trace": float(np.trace(cov)),
                         "offdiag_aggregate": float(T - U), "T": T, "U": U}
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return {"truth_lambda": true_lambda, "truth_boolq_diag": float(truth[0, 0]), **results}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--histogram", required=True)
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20260915)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    hist = json.load(open(args.histogram))
    # Scales mimic the observed margin battery: BoolQ variance share about 0.68 of the trace.
    v = 0.68 * 9 / 0.32
    cfg = {"configs": 125, "rho": 0.061, "trait_scales": [v ** 0.5] + [1.0] * 9,
           "sizes_per_trait": [None, 1172, 2376, 1221, 10042, 14042, 500, 1838, 1954, 1267],
           "item_noise_sd": [4.0] + [25.0] * 9, "histogram": hist}
    # Item noise is large relative to run effects so that trait reliabilities sit near the observed range.
    summary = []
    t0 = time.time()
    for tau in (0.0, 0.5, 1.0, 2.0, 4.0):
        rows = [one_rep(cfg, tau, np.random.default_rng([args.seed, int(tau * 100), rep])) for rep in range(args.reps)]
        s = {"tau": tau, "reps": len(rows), "truth_lambda": rows[0]["truth_lambda"], "truth_boolq_diag": rows[0]["truth_boolq_diag"]}
        for mode in ("item", "group"):
            lam = np.array([r[mode]["lambda"] for r in rows if r[mode]["lambda"] is not None])
            bd = np.array([r[mode]["boolq_diag"] for r in rows])
            s[mode] = {"lambda_mean": float(lam.mean()), "lambda_sd": float(lam.std(ddof=1)),
                       "lambda_bias": float(lam.mean() - rows[0]["truth_lambda"]),
                       "boolq_diag_mean": float(bd.mean()), "boolq_diag_bias": float(bd.mean() - rows[0]["truth_boolq_diag"]),
                       "boolq_diag_relative_bias": float(bd.mean() / rows[0]["truth_boolq_diag"] - 1),
                       "undefined": int(len(rows) - lam.size)}
        paired = np.array([r["group"]["lambda"] - r["item"]["lambda"] for r in rows
                           if r["group"]["lambda"] is not None and r["item"]["lambda"] is not None])
        s["paired_group_minus_item"] = {"mean": float(paired.mean()), "sd": float(paired.std(ddof=1))}
        summary.append(s)
        print(json.dumps(s), flush=True)
        (out / "summary.json").write_text(json.dumps({"config": {k: v for k, v in cfg.items() if k != "histogram"},
                                                     "cells": summary}, indent=1))
    print(f"[r2sim] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
