"""R11: benchmark composition, separating benchmark count, identity, and weights.

Design fixed before any output was opened (2026-09-15 16:40 EDT). Inputs are the
shipped C01 original-split moments (125 x 10 x 10) from snap-r2-grouped.
1. Every subset of K benchmarks for K = 2..10 (1,013 subsets) with equal weights:
   Lambda, K_eff = K / Lambda^2, wild cluster bootstrap-t interval (4,999 draws,
   recipe clusters), summarised by K so benchmark count is held fixed.
2. Identity at fixed K: for each benchmark, mean Lambda over subsets that contain
   it minus mean over subsets that don't, within each K.
3. Weights on the full battery as separate targets: equal (baseline), item-count
   weights, and inverse pooled seed SD weights over benchmarks with positive
   pooled diagonal (benchmarks with nonpositive diagonal are excluded and listed).
The K = 10 equal-weight cell must reproduce the shipped estimate.
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
    n_items = np.array([len(b["item_ids"]) for b in meta["benchmarks"]], float)
    recipe = np.array([c["recipe"] for c in meta["configs"]])
    K = len(names); assert cov.shape == (125, K, K) and K == 10, cov.shape
    diag = np.diagonal(cov, axis1=1, axis2=2)
    subsets = []
    for k in range(2, K + 1):
        for S in itertools.combinations(range(K), k):
            S = list(S)
            sub = cov[:, S][:, :, S]
            T = sub.sum(axis=(1, 2)); U = diag[:, S].sum(axis=1)
            l = lam(T, U); lo, hi = interval(T, U, recipe)
            subsets.append({"K": k, "benchmarks": [names[j] for j in S], "lambda": l,
                            "k_eff": k / l ** 2 if np.isfinite(l) and l > 0 else None,
                            "wild_lo": lo if not isinstance(hi, str) else None,
                            "wild_hi": hi if not isinstance(hi, str) else None,
                            "error": hi if isinstance(hi, str) else None})
    full = [s for s in subsets if s["K"] == K][0]
    tol = 1e-6 if phen == "margin" else 5e-4
    print(f"[check] {phen} K=10 lambda {full['lambda']:.6f} vs {EXPECTED[phen]}", flush=True)
    assert abs(full["lambda"] - EXPECTED[phen]) < tol, (phen, full["lambda"])
    by_k = {}
    for k in range(2, K + 1):
        rows = [s for s in subsets if s["K"] == k]
        ls = np.array([s["lambda"] for s in rows], float); fin = ls[np.isfinite(ls)]
        excl = [s for s in rows if s["wild_lo"] is not None and s["wild_lo"] > 1]
        below = [s for s in rows if s["wild_hi"] is not None and s["wild_hi"] < 1]
        by_k[k] = {"subsets": len(rows), "undefined_lambda": int((~np.isfinite(ls)).sum()),
                   "min": float(fin.min()), "p10": float(np.percentile(fin, 10)), "median": float(np.median(fin)),
                   "p90": float(np.percentile(fin, 90)), "max": float(fin.max()),
                   "share_interval_above_one": len(excl) / len(rows), "share_interval_below_one": len(below) / len(rows),
                   "share_lower_endpoint_undefined": sum(s["wild_lo"] is None for s in rows) / len(rows),
                   "min_subset": rows[int(np.nanargmin(ls))]["benchmarks"], "max_subset": rows[int(np.nanargmax(ls))]["benchmarks"]}
        print(f"[{phen} K={k}] n={len(rows)} median {by_k[k]['median']:.3f} p10-p90 {by_k[k]['p10']:.3f}-{by_k[k]['p90']:.3f} "
              f"range {by_k[k]['min']:.3f}-{by_k[k]['max']:.3f} above1 {by_k[k]['share_interval_above_one']:.3f}", flush=True)
    identity = {}
    for j, nm in enumerate(names):
        identity[nm] = {}
        for k in range(2, K):
            rows = [s for s in subsets if s["K"] == k and np.isfinite(s["lambda"])]
            a = [s["lambda"] for s in rows if nm in s["benchmarks"]]; b = [s["lambda"] for s in rows if nm not in s["benchmarks"]]
            identity[nm][k] = float(np.mean(a) - np.mean(b))
    weights = {}
    pooled_diag = diag.mean(0)
    schemes = {"equal": np.ones(K), "item_count": n_items}
    pos = pooled_diag > 0
    w_sd = np.zeros(K); w_sd[pos] = 1 / np.sqrt(pooled_diag[pos])
    schemes["inverse_pooled_seed_sd"] = w_sd
    for sname, w in schemes.items():
        w = w / w.sum()
        T = np.einsum("j,cjk,k->c", w, cov, w); U = np.einsum("j,cj->c", w * w, diag)
        lo, hi = interval(T, U, recipe)
        weights[sname] = {"weights": dict(zip(names, w.tolist())), "lambda": lam(T, U),
                          "wild_lo": lo if not isinstance(hi, str) else None, "wild_hi": hi if not isinstance(hi, str) else None,
                          "excluded_nonpositive_diagonal": [names[j] for j in range(K) if sname == "inverse_pooled_seed_sd" and not pos[j]]}
        print(f"[{phen} weights {sname}] lambda {weights[sname]['lambda']:.4f} wild {lo}-{hi}", flush=True)
    results["phenotypes"][phen] = {"benchmarks": names, "pooled_diagonal": dict(zip(names, pooled_diag.tolist())),
                                   "by_K": by_k, "identity_effect_fixed_K": identity, "weights": weights, "subsets": subsets}
results["wall_seconds"] = time.time() - t0
(W / "r11_composition.json").write_text(json.dumps(results, indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
