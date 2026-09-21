"""R6 direct test for a run effect shared across recipes inside one size band.

Design fixed before running (2026-09-15, written 23:05 EDT). snap-r6-size-shared showed that the shipped
recipe-clustered interval collapses if the shared run effect follows the size band instead, reaching
0.810 coverage when that effect holds a quarter of latent variance and 0.579 at a half. The release makes
that violation plausible rather than hypothetical, because it uses seeds 2, 14 and 15 below 1B and 2, 4
and 5 at 1B, so one seed label is shared across all 25 recipes inside a band. The paper currently carries
this as an untested limitation. This run tests it. Write the per-run deviation of configuration c on half
A as d_cri, which is that run's score minus the mean over the configuration's three runs. Line the runs
up by their batch index, which is the slot the release's seed labels occupy, and average d across the 25
recipes of a band to get a band mean. A run effect shared across the band survives that average, while
anything specific to a recipe shrinks towards zero. The statistic is the weighted cross-half covariance
of those band means, summed over the five bands. The null permutes each configuration's three runs among
its own batch slots independently, which leaves every configuration's own deviations and its own
cross-half covariance untouched, and destroys only the alignment of runs across recipes. That is the
exact null for this question. Two thousand permutations give the reference distribution, and the run
reports the observed statistic, its share of the per-configuration total, and the permutation tail.
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


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)


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
# Every configuration must carry one run in each batch slot, or the band means mix slots.
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


report = {"design": __doc__, "traits": TR, "n_perm": N_PERM, "seed": SEED, "batteries": {}}
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
        cell = {"observed": obs, "per_config_total": per_config,
                "observed_over_per_config": obs / per_config if per_config else None,
                # Averaging n independent configurations divides a covariance by n, and the
                # band total sums n of them, so the ratio lands near 1/n^2 without sharing.
                "independence_expectation": 1.0 / float((band == bands[0]).sum()) ** 2,
                "null_mean": float(null.mean()), "null_sd": sd,
                "null_p05": float(np.percentile(null, 5)), "null_p95": float(np.percentile(null, 95)),
                "z": (obs - float(null.mean())) / sd if sd > 0 else None,
                "share_at_or_above_observed": float(np.mean(null >= obs)),
                "seconds": time.time() - t1}
        report["batteries"][f"{label}/{name}"] = cell
        print(f"[{label}/{name}] {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_band_share.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
