"""k06 (CPU): how much precision a four-task battery can buy, before the GPUs spend it.

The held-out design scores four tasks, while every number the paper reports
comes from a ten-benchmark battery. Lambda is a property of a battery rather
than of a model, so a four-task Lambda is a different quantity from the shipped
one, and the interval around it is wider for two reasons that this kernel
separates. Fewer traits leave fewer directions for the estimator, and fewer
traits also make the aggregate noisier.

Method. Build the shipped population once, then read every subset of the ten
traits at sizes two through ten, slicing the phenotype arrays on the trait axis
and leaving the design, the runs and the recipe clusters untouched. Sizes with
more than MAX_SUBSETS combinations are sampled without replacement under a fixed
seed. Each subset gets a point estimate and a wild cluster bootstrap-t interval
on 25 recipe clusters, and the summary reports the median point estimate, the
median width, and the share of subsets whose interval excludes one.

What this does and does not say. It measures what battery size costs, using the
shipped tasks as the stand-in for the held-out ones. It cannot predict the
held-out tasks' own correlation, which is the quantity the held-out test exists
to measure, so a low exclusion share at four traits is a warning about power
rather than a prediction of the answer.
"""
import itertools
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

MAX_SUBSETS = 60
N_BOOT = 1999
N_BOOT_FULL = 4999
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
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402

# The shipped dataset carries a 163-byte macOS twin for every run, and those are
# not loadable npz, so only the real files are copied out.
shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
runs_dir = TMP / "runs_shipped"
shutil.rmtree(runs_dir, ignore_errors=True)
runs_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, runs_dir / p.name)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[pop] N={pop.N} R={pop.R} K={pop.K} over {pop.n_clusters} recipe clusters", flush=True)


def with_traits(idx):
    """The same population restricted to the traits at these column indices."""
    ph = {k: Phenotype(v.name, v.A[:, :, idx], v.B[:, :, idx]) for k, v in pop.phenotypes.items()}
    return Population(ph, pop.gainA, pop.gainB, pop.batch, pop.recipe, pop.size,
                      [pop.traits[j] for j in idx], pop.config_ids, pop.n_items)


def read(p, name, n_boot):
    """Point estimate and interval, or NaN bounds when the bootstrap degenerates.

    A two-trait battery leaves so few directions that every draw can return a
    non-finite t, and seednoise raises rather than returning a fake interval, so
    those subsets are counted as undefined instead of ending the sweep.
    """
    e = estimate(p, name, check=False)
    try:
        ci = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=n_boot, seed=0)
    except RuntimeError as error:
        print(f"[undefined] {name} K={p.K} {p.traits}: {error}", flush=True)
        return e.lambda_hat, float("nan"), float("nan")
    return e.lambda_hat, float(ci.lo), float(ci.hi)


full = {}
for name in (MARGIN, ACCURACY):
    lam, lo, hi = read(pop, name, N_BOOT_FULL)
    full[name] = {"lambda_hat": lam, "ci95": [lo, hi], "width": hi - lo, "excludes_one": lo > 1 or hi < 1}
    print(f"[full] {name} {lam:.5f} [{lo:.3f}, {hi:.3f}]", flush=True)
assert abs(full[MARGIN]["lambda_hat"] - 1.24395) < 5e-4, \
    f"shipped runs give margin Lambda {full[MARGIN]['lambda_hat']}, not the paper's 1.24395"

# Scope-matched build: the held-out test reads only these sizes, so the trait
# subsets are read on the same configurations. The ten-trait check above ran on
# all 125 first, which keeps the reproduction gate identical to k06.
KEEP_SIZES = ["530M", "750M"]
pop = pop.subset(np.flatnonzero(np.isin(pop.size, [info["sizes"].index(z) for z in KEEP_SIZES])))
info = dict(info, sizes=KEEP_SIZES)
print(f"[scope] {KEEP_SIZES} N={pop.N} over {pop.n_clusters} recipe clusters", flush=True)
full = {}
for name in (MARGIN, ACCURACY):
    lam, lo, hi = read(pop, name, N_BOOT_FULL)
    full[name] = {"lambda_hat": lam, "ci95": [lo, hi], "width": hi - lo, "excludes_one": lo > 1 or hi < 1}
    print(f"[scope full] {name} {lam:.5f} [{lo:.3f}, {hi:.3f}]", flush=True)

rng = np.random.default_rng(SEED)
rows, by_k = [], {}
for k in range(2, len(TRAITS) + 1):
    combos = list(itertools.combinations(range(len(TRAITS)), k))
    if len(combos) > MAX_SUBSETS:
        pick = rng.choice(len(combos), size=MAX_SUBSETS, replace=False)
        combos = [combos[i] for i in sorted(pick)]
    sub_pops = [(c, with_traits(list(c))) for c in combos]
    for name in (MARGIN, ACCURACY):
        lam, lo, hi = [], [], []
        for c, sp in sub_pops:
            a, b, d = read(sp, name, N_BOOT)
            rows.append({"k": k, "phenotype": name, "traits": [TRAITS[j] for j in c],
                         "lambda_hat": a, "lo": b, "hi": d, "width": d - b,
                         "excludes_one": bool(b > 1 or d < 1)})
            lam.append(a)
            lo.append(b)
            hi.append(d)
        lam, lo, hi = np.asarray(lam), np.asarray(lo), np.asarray(hi)
        ok = np.isfinite(lo) & np.isfinite(hi)
        by_k.setdefault(name, {})[k] = {
            "subsets": len(combos), "defined": int(ok.sum()),
            "exhaustive": len(combos) == len(list(itertools.combinations(range(len(TRAITS)), k))),
            "lambda_defined": int(np.isfinite(lam).sum()),
            "lambda_median": float(np.nanmedian(lam)), "lambda_p05": float(np.nanquantile(lam, 0.05)),
            "lambda_p95": float(np.nanquantile(lam, 0.95)),
            "width_median": float(np.median((hi - lo)[ok])) if ok.any() else float("nan"),
            "excludes_one_share": float(np.mean((lo[ok] > 1) | (hi[ok] < 1))) if ok.any() else float("nan")}
        s = by_k[name][k]
        print(f"[k={k:2d}] {name}: median Lambda {s['lambda_median']:.3f}, median width "
              f"{s['width_median']:.3f}, excludes one in {s['excludes_one_share']:.2f} of "
              f"{s['defined']} defined subsets out of {s['subsets']}", flush=True)

out = {"full_battery": full, "by_k": by_k, "n_boot": N_BOOT, "n_boot_full": N_BOOT_FULL,
       "max_subsets_per_k": MAX_SUBSETS, "seed": SEED, "sizes": info["sizes"],
       "note": "trait subsets of the shipped battery stand in for a smaller held-out battery; "
               "they cannot predict the held-out tasks' own correlation",
       "status": "exploratory unless listed as pre-registered in PROTOCOL_heldout.md",
       "wall_seconds": time.time() - t0}
(W / "power_results.json").write_text(json.dumps(out, indent=1))
(W / "power_subsets.json").write_text(json.dumps(rows, indent=1))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
ks = sorted(by_k[MARGIN])
fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
for name, mark in ((MARGIN, "o"), (ACCURACY, "s")):
    axes[0].plot(ks, [by_k[name][k]["width_median"] for k in ks], marker=mark, label=name)
    axes[1].plot(ks, [by_k[name][k]["excludes_one_share"] for k in ks], marker=mark, label=name)
axes[0].set_ylabel("median 95 percent interval width")
axes[1].set_ylabel("share of batteries excluding one")
for ax in axes:
    ax.set_xlabel("benchmarks in the battery")
    ax.legend(frameon=False, fontsize=8)
axes[1].axvline(4, color="0.6", lw=0.8)
fig.tight_layout()
fig.savefig(W / "power_vs_battery_size.pdf")
fig.savefig(W / "power_vs_battery_size.png", dpi=200)
print(f"[done] {len(rows)} subset fits in {time.time() - t0:.0f}s", flush=True)
