"""R6 shared-noise diagnostic, testing whether the observed covariance carries the contamination pattern.

Design fixed before running (2026-09-15, written 20:45 EDT). snap-r6-sharednoise shows that a scalar
half effect shared by every benchmark, at 0.124 of item-noise variance, reproduces the observed margin
estimate, and at 0.009 reproduces the observed accuracy estimate. That contamination has a signature.
It adds q rho_f sigma_j sigma_k to every cross-half covariance entry, where sigma is the per-half item
noise standard deviation, so the off-diagonal entries of the estimated seed covariance should line up
with the outer product of those noise scales.

We regress the off-diagonal entries of the observed seed covariance on the corresponding entries of
that outer product, with no intercept, and read the slope as the contamination share that the pattern
would imply. We also record the cosine between the two off-diagonal vectors. A recipe-cluster bootstrap
of 999 draws gives intervals. The null is 500 matched simulations with the observed seed covariance
and no shared effect, which say what slope and cosine the honest model produces. A second set of 500
simulations adds the shared effect at the phenotype's matching share, so the diagnostic's power is
visible rather than assumed. The statistic can't separate contamination from a seed covariance that
happens to follow the noise scales, and the report says so.
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
runs = W / "runs"; runs.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate, nearest_psd, sigma_e  # noqa: E402
from seednoise.nulls import NOMINAL_ITEMS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import SimSpec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
N_BOOT, N_REP = 999, 500
MATCH = {"margin": 0.1242, "accuracy": 0.0091}


def noise_sd_half(p, name):
    """Per-half item-noise standard deviation for each benchmark."""
    comp = variance_components(p, name)
    return np.sqrt(np.clip(np.asarray(comp.noise2, float), 1e-18, None))


def statistic(p, name):
    S = sigma_e(p, name)
    s = noise_sd_half(p, name)
    M = np.outer(s, s)
    iu = np.triu_indices(p.K, 1)
    y, x = S[iu], M[iu]
    denom = float(x @ x)
    slope = float(y @ x) / denom if denom > 0 else float("nan")
    ny, nx = float(np.linalg.norm(y)), float(np.linalg.norm(x))
    cos = float(y @ x) / (ny * nx) if ny > 0 and nx > 0 else float("nan")
    return {"slope": slope, "cosine": cos}


report = {"design": __doc__, "n_boot": N_BOOT, "n_rep": N_REP, "matching_share": MATCH,
          "traits": list(pop.traits), "observed": {}, "bootstrap": {}, "null": {}, "power": {}}
n_items = tuple(int(n) for n in np.asarray(pop.n_items).tolist()) if pop.n_items is not None else tuple([NOMINAL_ITEMS] * pop.K)
n_half = np.maximum(np.asarray(n_items, float) / 2.0, 1.0)

for name in ("margin", "accuracy"):
    obs = statistic(pop, name)
    obs["lambda"] = float(estimate(pop, name, check=False).lambda_hat)
    report["observed"][name] = obs
    print(f"[{name}] observed {json.dumps(obs)}", flush=True)

    rng = np.random.default_rng(20260921)
    rs = np.unique(pop.recipe)
    draws = []
    for _ in range(N_BOOT):
        q = pop.subset_clusters(rng.choice(rs, size=rs.size, replace=True))
        draws.append(statistic(q, name))
    report["bootstrap"][name] = {}
    for k in ("slope", "cosine"):
        a = np.asarray([d[k] for d in draws], float); f = a[np.isfinite(a)]
        report["bootstrap"][name][k] = {"p025": float(np.percentile(f, 2.5)), "p50": float(np.percentile(f, 50)),
                                        "p975": float(np.percentile(f, 97.5)), "n_finite": int(f.size)}
    print(f"[{name}/bootstrap] " + json.dumps(report["bootstrap"][name]), flush=True)

    S = sigma_e(pop, name)
    sd = np.sqrt(np.clip(np.diag(S), 1e-9, None))
    R = S / np.outer(sd, sd); np.fill_diagonal(R, 1.0); R = np.where(np.isfinite(R), R, 0.0)
    matched, clipped = nearest_psd(np.outer(sd, sd) * R, floor=1e-12)
    s_noise = noise_sd_half(pop, name)
    item_sd = tuple(np.sqrt(np.clip(np.asarray(variance_components(pop, name).noise2, float), 1e-12, None) * n_half).tolist())
    for label, extra in (("matched", 0.0), ("matched_plus_shared", MATCH[name])):
        t1 = time.time(); rows = []
        for i in range(N_REP):
            spec = SimSpec(n_config=pop.N, n_runs=pop.R, traits=tuple(pop.traits), n_items=n_items,
                           item_sd=item_sd, n_recipes=25, n_sizes=5, seed=20260921 + 7919 * i)
            spec.sigma_e = matched + extra * np.outer(s_noise, s_noise) if extra > 0 else matched
            sim = simulate(spec)
            st = statistic(sim, name)
            st["lambda"] = float(estimate(sim, name, check=False).lambda_hat)
            rows.append(st)
        cell = {}
        for k in ("slope", "cosine", "lambda"):
            a = np.asarray([r[k] for r in rows], float); f = a[np.isfinite(a)]
            cell[k] = {"mean": float(f.mean()), "sd": float(f.std(ddof=1)), "p05": float(np.percentile(f, 5)),
                       "median": float(np.median(f)), "p95": float(np.percentile(f, 95)),
                       "share_at_or_above_observed": float(np.mean(f >= obs.get(k, np.inf)))}
        cell["psd_clipped"] = float(clipped)
        (report["null"] if extra == 0.0 else report["power"])[name] = cell
        print(f"[{name}/{label}] {time.time() - t1:.0f}s " + json.dumps({k: round(v["mean"], 4) for k, v in cell.items() if isinstance(v, dict)}), flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_shared_fit.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
