"""snap-r3-r2-43 (CPU only): store the 0.008 band share and its 0.044 upper bound.

Paper: main.tex "bounds that effect at 0.044 of the seed covariance on margins" and appendices_bcd.tex
"the share comes to 0.008 on full-battery margins with a 95 percent upper bound of 0.044".

Source, both committed in SNAP at 6cfedee under "compute extra/research_kernels/":
  snap-r6-band-share/snap-r6-band-share.py   deviations(), weighted_cross(), band_statistic() and the
                                             2,000-permutation batch-slot null (seed 20260931), copied
                                             below verbatim. Its stored output
                                             (research/outputs/snap-r6-band-share/r6_band_share.json) holds
                                             the statistic and null but not the share, which was converted
                                             by hand in research/LEDGER.md (2026-09-15 23:01 EDT).
  snap-r6-share-power/snap-r6-share-power.py the committed plug-in conversion, copied below verbatim:
                                             slope = total (1/n - 1/n^2), q = (obs - null_mean)/slope,
                                             se = null_sd/slope, with n = 25 configurations per band and
                                             Z = 1.959963984540054; the upper bound is q + Z se.
Only the preamble differs: seednoise comes from garyzhang11111/seed-noise-src rather than
snap-compute-src, and the script asserts the paper's margin Lambda 1.24395 first.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])

sel = [p for p in Path("/kaggle/input").rglob("*.npz")
       if "seed-noise-reduced-runs" in str(p) and "__seed-" in p.name and not p.name.startswith("._")]
assert len(sel) == 375, len(sel)
runs_dir = Path("/kaggle/tmp") / "runs"
shutil.rmtree(runs_dir, ignore_errors=True); runs_dir.mkdir(parents=True)
for p in sel:
    shutil.copy(p, runs_dir / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
lam = estimate(pop, "margin").lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"

# ---- verbatim from snap-r6-band-share.py (SNAP 6cfedee) ----
N_PERM = 2000
SEED = 20260931
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
band = np.asarray(pop.size)
batch = np.asarray(pop.batch)
bands = np.unique(band)
K_ALL = len(TR)
print(f"[base] bands {bands.tolist()} batch values {np.unique(batch).tolist()}", flush=True)
for c in range(pop.N):
    assert sorted(batch[c].tolist()) == sorted(np.unique(batch).tolist()), (c, batch[c])


def deviations(name, idx):
    """Run deviations on both halves, with runs ordered by batch slot."""
    ph = pop.pheno(name)
    A, B = ph.A[:, :, idx], ph.B[:, :, idx]
    order = np.argsort(batch, axis=1)
    A = np.take_along_axis(A, order[:, :, None], axis=1)
    B = np.take_along_axis(B, order[:, :, None], axis=1)
    return A - A.mean(1, keepdims=True), B - B.mean(1, keepdims=True)


def weighted_cross(dA, dB, w):
    """Weighted cross-half covariance of a stack of deviation arrays, summed over its first axis."""
    r = dA.shape[1]
    cross = np.einsum("crj,crk->cjk", dA, dB) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    return float(T.sum()), float(U.sum())


def band_statistic(dA, dB, w, perm=None):
    """Weighted cross-half covariance of the band means, summed over bands."""
    a, b = (dA, dB) if perm is None else (np.take_along_axis(dA, perm[:, :, None], axis=1),
                                         np.take_along_axis(dB, perm[:, :, None], axis=1))
    mA = np.stack([a[band == z].mean(axis=0) for z in bands])
    mB = np.stack([b[band == z].mean(axis=0) for z in bands])
    T, _ = weighted_cross(mA, mB, w)
    return T
# ---- end verbatim ----


# ---- plug-in share, verbatim arithmetic from snap-r6-share-power.py (SNAP 6cfedee) ----
Z = 1.959963984540054
N_PER_BAND = int((band == bands[0]).sum())
assert N_PER_BAND == 25, N_PER_BAND

# Stored output of the original run, for the reproduction check.
STORED = {"full/margin": (7.794077959781909e-06, 0.004083877356163356, 6.502025584075332e-06, 2.8465395129734238e-06),
          "full/accuracy": (3.311917703681002e-06, 0.00330499535460678, 5.29820050526234e-06, 2.7380920407485624e-06),
          "without_boolq/margin": (7.792765156509719e-06, 0.003334278651727164, 5.270059460607419e-06, 2.1435639945364947e-06),
          "without_boolq/accuracy": (2.4568877316259944e-06, 0.001328968563001426, 2.1145008378770393e-06, 1.5251511847542426e-06)}

report = {"design": __doc__, "traits": TR, "n_perm": N_PERM, "seed": SEED, "Z": Z, "n_per_band": N_PER_BAND,
          "lambda_margin_check": lam, "batteries": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    w = np.full(len(idx), 1.0 / len(idx))
    for name in ("margin", "accuracy"):
        t1 = time.time()
        dA, dB = deviations(name, idx)
        obs = band_statistic(dA, dB, w)
        per_config, _ = weighted_cross(dA, dB, w)
        rng = np.random.default_rng(SEED)
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            perm = np.argsort(rng.random(dA.shape[:2]), axis=1)
            null[p] = band_statistic(dA, dB, w, perm)
        sd = float(null.std(ddof=1))
        slope = per_config * (1.0 / N_PER_BAND - 1.0 / N_PER_BAND ** 2)
        q = (obs - float(null.mean())) / slope
        se = sd / slope
        key = f"{label}/{name}"
        so, st, sm, ss = STORED[key]
        sq, sse = (so - sm) / (st * (1.0 / 25 - 1.0 / 625)), ss / (st * (1.0 / 25 - 1.0 / 625))
        cell = {"observed": obs, "per_config_total": per_config,
                "null_mean": float(null.mean()), "null_sd": sd,
                "share_at_or_above_observed": float(np.mean(null >= obs)),
                "slope": slope, "share_q": q, "share_se": se, "upper_bound_95": q + Z * se,
                "lower_bound_95": q - Z * se,
                "stored_r6_share_q": sq, "stored_r6_share_se": sse, "stored_r6_upper_bound_95": sq + Z * sse,
                "matches_stored_r6_statistics": bool(np.allclose([obs, per_config, float(null.mean()), sd],
                                                                 [so, st, sm, ss], rtol=1e-9, atol=0)),
                "seconds": time.time() - t1}
        report["batteries"][key] = cell
        print(f"[{key}] q {q:.5f} se {se:.5f} upper {q + Z * se:.5f} tail {cell['share_at_or_above_observed']:.4f} "
              f"matches stored {cell['matches_stored_r6_statistics']}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r2_43_band_share.json").write_text(json.dumps(report, indent=1))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
