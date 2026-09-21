"""R6 item-sharing permutation test, asking whether item-level clustering feeds the estimate.

Design fixed before running (2026-09-15, written 22:30 EDT). snap-r6-sharednoise shows that a half
effect shared across benchmarks inflates the estimate, and snap-r6-shared-fit shows that regressing
the off-diagonal seed covariance on the item-noise outer product can't detect it. This run tests the
one channel that item-level data can identify. Write the per-item phenotype of run r in
configuration c as x_cri. Let mu_ci be the mean of x over the three runs of that configuration, so
d_cri = x_cri - mu_ci holds everything specific to the run, which is the seed effect plus item noise.
Permuting d within a group, separately for every run, leaves every group mean untouched and therefore
leaves each run's trait score untouched, and it leaves a component shared by every item of the group
untouched as well, since permuting a constant returns the constant. What it destroys is the
association between particular items and particular runs, which is exactly the channel a shared
passage or a shared source document travels through. An estimate that sits above the permutation
distribution has item-level sharing in it. An estimate inside the distribution bounds that channel.
The run also re-draws the item half split 200 times on the real data and on permuted data, so the
spread of the estimate over splits can be compared against the spread the null produces.
Groups rather than traits are the permutation blocks, because a trait score is the macro-average over
its groups and permuting across groups would move mass between the 57 MMLU subjects.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find_all(name):
    return sorted(p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._"))


src = [p for p in find_all("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
sel = [p for p in find_all("*.npz") if "__seed-" in p.name]
assert len(sel) == 375, len(sel)
runs_dir = W / "runs"; runs_dir.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs_dir / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.halves import MASTER_SEED, split_items  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.store import load_run  # noqa: E402

K = len(TRAITS)
base, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
lam_obs = {p: float(estimate(base, p, check=False).lambda_hat) for p in ("margin", "accuracy")}
print(f"[base] lambda {lam_obs}", flush=True)

# Re-assemble the population in memory so a permutation doesn't need a rewrite to disk.
records = [load_run(f) for f in sorted(runs_dir.glob("*.npz"))]
trait = records[0][0].trait
group = records[0][0].group
n_items = trait.size
cells = {}
for items, meta in records:
    cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, items))
keep = {k: v for k, v in cells.items() if len(v) == 3}
order = sorted(keep)
N = len(order)
assert N == base.N, (N, base.N)
MARG = np.zeros((N, 3, n_items)); CORR = np.zeros((N, 3, n_items))
for c, key in enumerate(order):
    rows = sorted(keep[key], key=lambda t: t[0]["batch"])
    for r, (meta, items) in enumerate(rows):
        MARG[c, r] = items.margin
        CORR[c, r] = items.correct.astype(np.float64)

# Group-macro-average half scores, matching seednoise.phenotypes.half_scores exactly.
gkeys, ginv = np.unique(group, return_inverse=True)
G = gkeys.size
trait_of_group = np.zeros(G, dtype=np.int64)
trait_of_group[ginv] = trait
n_per_trait = np.bincount(trait_of_group, minlength=K)[:K]


def half_means(vals, mask):
    """(N, 3, K) trait scores over the items in one half, for a (N, 3, n_items) array."""
    sel = np.flatnonzero(mask)
    gi = ginv[sel]
    n_g = np.bincount(gi, minlength=G).astype(float)
    assert (n_g > 0).all(), "a group is empty in this half"
    flat = vals[:, :, sel].reshape(-1, sel.size)
    gm = np.stack([np.bincount(gi, weights=row, minlength=G) for row in flat]) / n_g
    tm = np.stack([np.bincount(trait_of_group, weights=row, minlength=K)[:K] for row in gm])
    return (tm / n_per_trait).reshape(vals.shape[0], vals.shape[1], K)


def population_for(mask, marg=MARG, corr=CORR):
    p = base.with_phenotype("margin", half_means(marg, mask), half_means(marg, ~mask))
    return p.with_phenotype("accuracy", half_means(corr, mask), half_means(corr, ~mask))


shipped = split_items(trait, K, seed=MASTER_SEED)
check = population_for(shipped)
for name in ("margin", "accuracy"):
    d = max(np.abs(check.pheno(name).A - base.pheno(name).A).max(),
            np.abs(check.pheno(name).B - base.pheno(name).B).max())
    print(f"[check] {name} reassembly max abs difference {d:.3e}", flush=True)
    assert d < 1e-12, d
report = {"design": __doc__, "observed": lam_obs, "n_config": N, "n_items": int(n_items), "n_groups": int(G)}

report["observed_interval"] = {}
for name in ("margin", "accuracy"):
    est = estimate(base, name, check=False)
    iv = wild_bootstrap_t(est.T, est.U, base.recipe, n_boot=4999, seed=0)
    report["observed_interval"][name] = [float(iv.lo), float(iv.hi)]
print(f"[base] intervals {report['observed_interval']}", flush=True)

# 1. The estimate over 200 fresh item half splits of the real data.
SPLITS = 200
split_seeds = [MASTER_SEED + 1 + i for i in range(SPLITS)]
rows = []
for s in split_seeds:
    m = split_items(trait, K, seed=s)
    p = population_for(m)
    rows.append({p_: float(estimate(p, p_, check=False).lambda_hat) for p_ in ("margin", "accuracy")})
report["resplit"] = {}
for name in ("margin", "accuracy"):
    v = np.array([r[name] for r in rows]); v = v[np.isfinite(v)]
    report["resplit"][name] = {"n": int(v.size), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                               "p05": float(np.percentile(v, 5)), "median": float(np.median(v)),
                               "p95": float(np.percentile(v, 95)), "min": float(v.min()), "max": float(v.max())}
print(f"[resplit] {json.dumps(report['resplit'])} {time.time() - t0:.0f}s", flush=True)

# 2. Permutation of run-specific item deviations inside each group.
PERMS = 200
mu_m, mu_c = MARG.mean(axis=1, keepdims=True), CORR.mean(axis=1, keepdims=True)
dev_m, dev_c = MARG - mu_m, CORR - mu_c
block = ginv.astype(np.float64)
rng = np.random.default_rng(20260921)
perm_rows, perm_split_sd = [], []
for b in range(PERMS):
    keys = block[None, None, :] + rng.random((N, 3, n_items))
    idx = np.argsort(keys, axis=2)
    pm = mu_m + np.take_along_axis(dev_m, idx, axis=2)
    pc = mu_c + np.take_along_axis(dev_c, idx, axis=2)
    p = population_for(shipped, pm, pc)
    row = {n_: float(estimate(p, n_, check=False).lambda_hat) for n_ in ("margin", "accuracy")}
    perm_rows.append(row)
    if b < 20:  # the split spread the null produces, on a subset for time
        sv = {"margin": [], "accuracy": []}
        for s in split_seeds[:25]:
            q = population_for(split_items(trait, K, seed=s), pm, pc)
            for n_ in sv:
                sv[n_].append(float(estimate(q, n_, check=False).lambda_hat))
        for n_ in sv:
            a = np.asarray(sv[n_], float); a = a[np.isfinite(a)]
            sv[n_] = float(a.std(ddof=1))
        perm_split_sd.append(sv)
    if (b + 1) % 20 == 0:
        print(f"[perm] {b + 1}/{PERMS} {json.dumps(row)} {time.time() - t0:.0f}s", flush=True)
report["permutation"] = {}
for name in ("margin", "accuracy"):
    v = np.array([r[name] for r in perm_rows]); v = v[np.isfinite(v)]
    o = lam_obs[name]
    report["permutation"][name] = {
        "n": int(v.size), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
        "p05": float(np.percentile(v, 5)), "median": float(np.median(v)), "p95": float(np.percentile(v, 95)),
        "share_at_or_above_observed": float(np.mean(v >= o)),
        "observed_minus_mean": float(o - v.mean()),
        "null_split_sd_mean": float(np.mean([r[name] for r in perm_split_sd])),
        "real_split_sd": report["resplit"][name]["sd"]}
print(f"[perm] {json.dumps(report['permutation'])}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_itemshare.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
