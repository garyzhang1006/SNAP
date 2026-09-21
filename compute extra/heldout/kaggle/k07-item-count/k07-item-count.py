"""k07 (CPU): what item count per benchmark costs the interval.

The held-out tasks carry 1,000 items for SciQ and MedMCQA, 651 for LogiQA-en and
510 for LSAT-LR, while the shipped benchmarks that produced 1.244 are mostly
larger. Item noise enters the estimator through U, so a battery of the same
width but fewer items per benchmark gives a wider interval, and this kernel
measures that on the shipped runs instead of assuming it.

Method. Read the 375 reduced runs once at item level. For each cap in CAPS,
draw that many items per benchmark under a fixed seed, split the drawn items
into halves by group so a passage never spans both halves, recompute each run's
trait scores on the two halves, and assemble the population by hand the way
seednoise.build does. Every cap is read on the full ten benchmarks and on the
same four-benchmark subsets k06 used, so the item axis and the width axis can be
read separately.

The caps are counts per benchmark before the half split, so a cap of 1,000
leaves about 500 items on each side, which is what a 1,000-item held-out task
gives the estimator.
"""
import itertools
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

CAPS = [200, 400, 600, 1000, 2000, None]
N_SUBSETS_K4 = 20
N_BOOT = 1999
SEED = 20260917

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = TMP / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", str(sn_copy)])
from seednoise.build import SIZE_ORDER  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.phenotypes import half_scores  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402
from seednoise.store import load_run  # noqa: E402

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
runs_dir = TMP / "runs_shipped"
shutil.rmtree(runs_dir, ignore_errors=True)
runs_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, runs_dir / p.name)

K = len(TRAITS)
runs = [load_run(f) for f in sorted(runs_dir.glob("*.npz"))]
ref = runs[0][0]
for items, _ in runs:
    assert np.array_equal(items.item_id, ref.item_id), "the runs are not on one item set"
per_trait = np.bincount(ref.trait, minlength=K)
print(f"[items] {ref.n_items} items over {K} benchmarks: "
      f"{dict(zip(TRAITS, per_trait.tolist()))}", flush=True)


def masks_for(cap, seed):
    """Half masks over a capped draw of items, split by group inside each benchmark."""
    rng = np.random.default_rng(seed)
    keep = np.zeros(ref.n_items, bool)
    for t in range(K):
        idx = np.flatnonzero(ref.trait == t)
        if cap is not None and idx.size > cap:
            idx = rng.choice(idx, size=cap, replace=False)
        keep[idx] = True
    a = np.zeros(ref.n_items, bool)
    for t in range(K):
        idx = np.flatnonzero(keep & (ref.trait == t))
        groups = np.unique(ref.group[idx])
        pick = rng.permutation(groups)[: max(1, groups.size // 2)]
        a[idx] = np.isin(ref.group[idx], pick)
        # A benchmark whose groups all land on one side would leave the other empty.
        if a[idx].all() or not a[idx].any():
            half = idx[: idx.size // 2]
            a[idx] = False
            a[half] = True
    return a & keep, (~a) & keep


def population_for(cap, seed):
    mA, mB = masks_for(cap, seed)
    cells = {}
    for items, meta in runs:
        m_a, a_a = half_scores(items, mA, K)
        m_b, a_b = half_scores(items, mB, K)
        cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, m_a, a_a, m_b, a_b))
    order = sorted(k for k, v in cells.items() if len(v) == 3)
    N = len(order)
    A_m, A_a, B_m, B_a = (np.zeros((N, 3, K)) for _ in range(4))
    batch = np.zeros((N, 3), dtype=np.int64)
    recipe_code = {r: i for i, r in enumerate(sorted({k[0] for k in order}))}
    size_code = {z: i for i, z in enumerate(sorted({k[1] for k in order},
                                                  key=lambda z: SIZE_ORDER.index(z)))}
    recipe = np.zeros(N, dtype=np.int64)
    size = np.zeros(N, dtype=np.int64)
    for c, key in enumerate(order):
        rows = sorted(cells[key], key=lambda t: t[0]["batch"])
        recipe[c], size[c] = recipe_code[key[0]], size_code[key[1]]
        for r, (meta, m_a, a_a, m_b, a_b) in enumerate(rows):
            A_m[c, r], A_a[c, r], B_m[c, r], B_a[c, r] = m_a, a_a, m_b, a_b
            batch[c, r] = meta["batch"]
    return Population({MARGIN: Phenotype(MARGIN, A_m, B_m), ACCURACY: Phenotype(ACCURACY, A_a, B_a)},
                      batch=batch, recipe=recipe, size=size, traits=list(TRAITS),
                      config_ids=[list(k) for k in order]), int(mA.sum() + mB.sum())


def with_traits(pop, idx):
    ph = {k: Phenotype(v.name, v.A[:, :, idx], v.B[:, :, idx]) for k, v in pop.phenotypes.items()}
    return Population(ph, pop.gainA, pop.gainB, pop.batch, pop.recipe, pop.size,
                      [pop.traits[j] for j in idx], pop.config_ids, pop.n_items)


def read(p, name):
    e = estimate(p, name, check=False)
    try:
        ci = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=N_BOOT, seed=0)
    except RuntimeError as error:
        print(f"[undefined] {name} K={p.K} cap: {error}", flush=True)
        return e.lambda_hat, float("nan"), float("nan")
    return e.lambda_hat, float(ci.lo), float(ci.hi)


rng = np.random.default_rng(SEED)
all_four = list(itertools.combinations(range(K), 4))
four = [all_four[i] for i in sorted(rng.choice(len(all_four), size=N_SUBSETS_K4, replace=False))]
out = {"caps": [], "items_per_trait_full": dict(zip(TRAITS, per_trait.tolist())),
       "n_boot": N_BOOT, "seed": SEED, "four_trait_subsets": [[TRAITS[j] for j in c] for c in four],
       "note": "caps are items per benchmark before the half split, so half that many reach each half",
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md"}
for cap in CAPS:
    pop, n_items = population_for(cap, SEED)
    row = {"cap": cap, "items_used": n_items, "full_battery": {}, "four_trait": {}}
    for name in (MARGIN, ACCURACY):
        lam, lo, hi = read(pop, name)
        row["full_battery"][name] = {"lambda_hat": lam, "ci95": [lo, hi], "width": hi - lo,
                                     "excludes_one": bool(lo > 1 or hi < 1)}
        vals = [read(with_traits(pop, list(c)), name) for c in four]
        w = np.asarray([h - l for _, l, h in vals])
        lam4 = np.asarray([a for a, _, _ in vals])
        excl = np.asarray([(l > 1) or (h < 1) for _, l, h in vals])
        ok = np.isfinite(w)
        row["four_trait"][name] = {"lambda_median": float(np.nanmedian(lam4)),
                                   "width_median": float(np.median(w[ok])) if ok.any() else float("nan"),
                                   "excludes_one_share": float(np.mean(excl[ok])) if ok.any() else float("nan"),
                                   "defined": int(ok.sum()), "subsets": len(four)}
    out["caps"].append(row)
    m, f4 = row["full_battery"][MARGIN], row["four_trait"][MARGIN]
    print(f"[cap {str(cap):>5}] {n_items:6d} items: ten-benchmark margin {m['lambda_hat']:.3f} "
          f"[{m['ci95'][0]:.3f}, {m['ci95'][1]:.3f}] width {m['width']:.3f} | four-benchmark median width "
          f"{f4['width_median']:.3f}, excludes one in {f4['excludes_one_share']:.2f}", flush=True)

out["wall_seconds"] = time.time() - t0
(W / "item_count_results.json").write_text(json.dumps(out, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
