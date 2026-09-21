"""R6: interval calibration for the pooled-ratio estimator under specified populations.

Each cell simulates C = recipes x sizes configurations with R runs and K
benchmarks, forms the two item halves as run effect plus independent (or
deliberately correlated) item noise, computes the per-configuration cross-half
moments, and then applies four interval procedures to the same T_c, U_c:
the original wild cluster bootstrap-t, the cluster-robust t(G-1), the
configuration percentile bootstrap, and the recipe percentile diagnostic used by
the reference implementation. Coverage is scored against the population Lambda
implied by the cell's run covariance, so cells that violate the estimator's
model measure bias as well as coverage.

Usage: python r6_calibration.py --out OUT --cells CELLS_JSON --reps B --draws 4999 --seed S
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from seednoise.inference import cluster_t_interval, config_bootstrap, wild_bootstrap_t


def snap_recipe_percentile(T, U, recipe, draws, seed, alpha=0.05):
    names = sorted(set(recipe))
    idx = [np.flatnonzero(recipe == r) for r in names]
    ct = np.array([T[i].sum() for i in idx])
    cu = np.array([U[i].sum() for i in idx])
    rng = np.random.default_rng(seed)
    sel = rng.integers(len(names), size=(draws, len(names)))
    t, u = ct[sel].sum(1), cu[sel].sum(1)
    keep = (u > 0) & (t >= 0)
    vals = np.sqrt(t[keep] / u[keep])
    invalid = int(draws - keep.sum())
    if invalid or vals.size == 0:
        return None, invalid
    return np.quantile(vals, [alpha / 2, 1 - alpha / 2]).tolist(), invalid


def simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    rho = cell.get("rho", 0.0)
    scale = np.asarray(cell.get("trait_scales", [1.0] * k), float)
    truth = ((1 - rho) * np.eye(k) + rho * np.ones((k, k))) * np.outer(scale, scale)
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    shared = cell.get("recipe_shared", 0.0)
    latent = np.sqrt(1 - shared) * rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    if shared > 0:
        latent += np.sqrt(shared) * np.repeat(rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
    df = cell.get("student_df")
    if df:
        latent *= np.sqrt((df - 2) / rng.chisquare(df, size=(n, r, 1)))
    rs = cell.get("recipe_variance_scales")
    if rs:
        latent *= np.sqrt(np.asarray(rs, float))[recipe][:, None, None]
    noise = np.asarray(cell.get("noise_sd", 1.0), float) * np.ones(k)
    ec = cell.get("cross_half_error_correlation", 0.0)
    ea = rng.normal(size=latent.shape) * noise
    eb = ec * ea + np.sqrt(1 - ec ** 2) * rng.normal(size=latent.shape) * noise
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    da = a - a.mean(1, keepdims=True)
    db = b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--draws", type=int, default=4999)
    ap.add_argument("--seed", type=int, default=20260915)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cells = json.load(open(args.cells))
    t0 = time.time()
    summary = []
    for ci, cell in enumerate(cells):
        rows = []
        for rep in range(args.reps):
            rng = np.random.default_rng([args.seed, ci, rep])
            T, U, recipe, truth = simulate(cell, rng)
            est = float(np.sqrt(T.sum() / U.sum())) if T.sum() >= 0 and U.sum() > 0 else None
            row = {"rep": rep, "truth": truth, "estimate": est}
            for name, fn in (("wild", lambda: wild_bootstrap_t(T, U, recipe, n_boot=args.draws, seed=rep)),
                             ("cluster_t", lambda: cluster_t_interval(T, U, recipe)),
                             ("config", lambda: config_bootstrap(T, U, n_boot=args.draws, seed=rep))):
                try:
                    iv = fn()
                    lo, hi = iv.lo, iv.hi
                    ok = np.isfinite(lo) and np.isfinite(hi)
                    row[name] = {"lo": lo if ok else None, "hi": hi if ok else None,
                                 "covered": bool(ok and lo <= truth <= hi),
                                 "lower_miss": bool(ok and lo > truth), "upper_miss": bool(ok and hi < truth),
                                 "invalid": not ok}
                except Exception as error:  # noqa: BLE001
                    row[name] = {"lo": None, "hi": None, "covered": False, "lower_miss": False, "upper_miss": False,
                                 "invalid": True, "error": type(error).__name__}
            iv, invalid = snap_recipe_percentile(T, U, recipe, args.draws, rep)
            row["recipe_pct"] = {"lo": iv[0] if iv else None, "hi": iv[1] if iv else None,
                                 "covered": bool(iv and iv[0] <= truth <= iv[1]),
                                 "lower_miss": bool(iv and iv[0] > truth), "upper_miss": bool(iv and iv[1] < truth),
                                 "invalid": iv is None, "invalid_draws": invalid}
            rows.append(row)
            if rep % 200 == 0:
                print(f"[r6] cell {ci} rep {rep} {time.time() - t0:.0f}s", flush=True)
        (out / f"cell_{ci:02d}_rows.json").write_text(json.dumps(rows))
        est = np.array([r["estimate"] for r in rows if r["estimate"] is not None])
        truth = rows[0]["truth"]
        s = {"cell": ci, "spec": cell, "reps": len(rows), "true_lambda": truth,
             "estimate_mean": float(est.mean()), "estimate_sd": float(est.std(ddof=1)),
             "bias": float(est.mean() - truth), "undefined_estimates": len(rows) - len(est)}
        for name in ("wild", "cluster_t", "config", "recipe_pct"):
            cov = np.mean([r[name]["covered"] for r in rows])
            widths = [r[name]["hi"] - r[name]["lo"] for r in rows if not r[name]["invalid"]]
            s[name] = {"coverage": float(cov), "mc_se": float(np.sqrt(cov * (1 - cov) / len(rows))),
                       "lower_miss": float(np.mean([r[name]["lower_miss"] for r in rows])),
                       "upper_miss": float(np.mean([r[name]["upper_miss"] for r in rows])),
                       "invalid": int(sum(r[name]["invalid"] for r in rows)),
                       "median_width": float(np.median(widths)) if widths else None}
        summary.append(s)
        print(json.dumps(s), flush=True)
        (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"[r6] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
