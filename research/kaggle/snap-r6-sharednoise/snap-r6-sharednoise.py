"""R6 shared item noise, asking how much of the observed estimate a common half effect could fake.

Design fixed before running (2026-09-15, written 20:30 EDT). snap-r6-crosshalf shows that item noise
correlated across halves within one benchmark can't manufacture inflation, because it adds the same
quantity to the numerator and the denominator and pulls the ratio toward one. A different violation
can manufacture it. If something in a half is shared across benchmarks and repeats in the opposite
half, such as a formatting artefact or a shared source document, the cross-half product picks up an
off-diagonal term that the denominator never sees.

The generator here extends the R6 one. Each half's item noise for benchmark k is
sigma_k (sqrt(q) f_half + sqrt(1 - q) z_k), where f is a scalar half effect shared by every benchmark
and z is independent. The two halves' shared effects correlate at rho_f. Only the product q rho_f
matters for the cross-half covariance, so the sweep runs over that product with the true seed
correlation held at zero. The run reports the mean estimate, its dispersion, and the share of
replicates at or above the observed value, with 2,000 replicates per grid point and seed 20260920.
A check at zero must return a mean near one, since the generator reduces to the R6 null there.
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

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402


def simulate_shared(noise_sd, share, rng, k=10, r=3, recipes=25, sizes=5):
    """R6 null population with a scalar half effect shared across benchmarks."""
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    latent = rng.multivariate_normal(np.zeros(k), np.eye(k), size=(n, r))
    q = float(np.clip(abs(share), 0.0, 1.0))
    sgn = 1.0 if share >= 0 else -1.0
    fa = rng.normal(size=(n, r, 1))
    fb = sgn * fa if q > 0 else rng.normal(size=(n, r, 1))
    za, zb = rng.normal(size=(n, r, k)), rng.normal(size=(n, r, k))
    ea = noise_sd * (np.sqrt(q) * fa + np.sqrt(1 - q) * za)
    eb = noise_sd * (np.sqrt(q) * fb + np.sqrt(1 - q) * zb)
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    da = a - a.mean(1, keepdims=True)
    db = b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    return T, U, recipe


SEED, REPS = 20260920, 2000
GRID = [0.0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
OBSERVED = {"margin": 1.2439499117191137, "accuracy": 1.0783733870898096}
NOISE = {"margin": 0.73, "accuracy": 1.45}
report = {"design": __doc__, "seed": SEED, "reps": REPS, "grid": GRID, "observed": OBSERVED, "curves": {}}
for pi, (name, noise) in enumerate(NOISE.items()):
    curve = []
    for gi, share in enumerate(GRID):
        t1 = time.time(); vals = []
        for rep in range(REPS):
            rng = np.random.default_rng([SEED, pi, gi, rep])
            T, U, _ = simulate_shared(noise, share, rng)
            th = float(np.sum(T)) / float(np.sum(U))
            vals.append(float(np.sqrt(th)) if th >= 0 else float("nan"))
        v = np.asarray(vals, float); f = v[np.isfinite(v)]
        row = {"shared_share": share, "n_finite": int(f.size), "mean": float(f.mean()), "sd": float(f.std(ddof=1)),
               "median": float(np.median(f)), "p05": float(np.percentile(f, 5)), "p95": float(np.percentile(f, 95)),
               "share_at_or_above_observed": float(np.mean(f >= OBSERVED[name])), "seconds": time.time() - t1}
        curve.append(row)
        print(f"[{name}] q={share} mean {row['mean']:.4f} sd {row['sd']:.4f} share {row['share_at_or_above_observed']:.3f} {row['seconds']:.0f}s", flush=True)
    means = np.array([r["mean"] for r in curve]); qs = np.array(GRID, float)
    o = OBSERVED[name]
    monotone = bool(np.all(np.diff(means) > -1e-9))
    match = float(np.interp(o, means, qs)) if monotone and means.max() >= o >= means.min() else None
    report["curves"][name] = {"rows": curve, "monotone": monotone, "matching_share": match}
    print(f"[{name}] matching shared share {match}", flush=True)
report["wall_seconds"] = time.time() - t0
(W / "r6_sharednoise.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
