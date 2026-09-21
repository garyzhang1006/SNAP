"""R11 removal table: the quantities the plan requires for each single-benchmark removal.

Design fixed before running (2026-09-15, 17:30 EDT). Inputs are the shipped C01 original-split
moments (125 x 10 x 10) from snap-r2-grouped, with equal weights. For the full battery and each
of the ten nine-benchmark batteries, per phenotype, the kernel reports the remaining benchmarks,
K, the weight 1/K, the pooled covariance trace and off-diagonal sum (means over configurations of
the equal-weight sums), Lambda, K_eff = K / Lambda^2, the aggregate standard deviation
sqrt(mean_c T_c), the independence standard deviation sqrt(mean_c U_c), and the wild recipe-cluster
interval (4,999 draws, seed 0). The full battery must reproduce the shipped estimates.
"""
import itertools, json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find(name, must_contain=None):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if must_contain:
        hits = [p for p in hits if must_contain in str(p)]
    if not hits:
        sys.exit(f"{name} ({must_contain}) not found under /kaggle/input")
    return sorted(hits)[0]


src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
from seednoise.inference import wild_bootstrap_t  # noqa: E402

DRAWS, SEED = 4999, 0
EXPECTED = {"margin": 1.243949911719114, "accuracy": 1.078}


def interval(T, U, recipe):
    try:
        iv = wild_bootstrap_t(T, U, recipe, n_boot=DRAWS, seed=SEED)
        return iv.lo, iv.hi
    except Exception as error:  # noqa: BLE001
        return None, f"{type(error).__name__}: {error}"


def lam(T, U):
    th = T.sum() / U.sum()
    return float(np.sqrt(th)) if th >= 0 and U.sum() > 0 else float("nan")


results = {"draws": DRAWS, "seed": SEED, "phenotypes": {}}
for phen in ("margin", "accuracy"):
    meta = json.load(open(find("scores.json", f"datasets/full/{phen}/")))
    cov = np.load(find("moments.npz", f"C01_{phen}_original/"))["covariance"]
    names = [b["name"] for b in meta["benchmarks"]]
    recipe = np.array([c["recipe"] for c in meta["configs"]])
    K = len(names); assert cov.shape == (125, K, K) and K == 10, cov.shape
    rows = []
    for drop in [None] + list(range(K)):
        S = [j for j in range(K) if j != drop]; k = len(S); w = 1.0 / k
        sub = cov[:, S][:, :, S] * w * w
        T = sub.sum(axis=(1, 2)); U = np.diagonal(sub, axis1=1, axis2=2).sum(axis=1)
        l = lam(T, U); lo, hi = interval(T, U, recipe)
        rows.append({"removed": None if drop is None else names[drop], "remaining": [names[j] for j in S], "K": k,
                     "weight": w, "trace": float(U.mean()), "offdiagonal_sum": float((T - U).mean()),
                     "lambda": l, "k_eff": k / l ** 2 if np.isfinite(l) and l > 0 else None,
                     "aggregate_sd": float(np.sqrt(T.mean())) if T.mean() > 0 else None,
                     "independence_sd": float(np.sqrt(U.mean())),
                     "wild_lo": lo if not isinstance(hi, str) else None, "wild_hi": hi if not isinstance(hi, str) else None,
                     "error": hi if isinstance(hi, str) else None})
        print(f"[{phen}] {json.dumps({k2: v for k2, v in rows[-1].items() if k2 != 'remaining'})}", flush=True)
    tol = 1e-6 if phen == "margin" else 5e-4
    assert abs(rows[0]["lambda"] - EXPECTED[phen]) < tol, rows[0]["lambda"]
    results["phenotypes"][phen] = rows
results["wall_seconds"] = time.time() - t0
(W / "r11_removal.json").write_text(json.dumps(results, indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
