"""R10 gain part: propagate uncertainty in the gain scale and check the simulators against the data.

Design fixed before running (2026-09-15, 17:40 EDT). Inputs are the 375 shipped reduced runs.
1. Reproduce estimate_gain_sd on margins (reported 0.042, leakage 1.91e-3, total 3.67e-3).
2. Recipe-cluster bootstrap of the gain SD, 999 draws with seed 0, percentile 2.5, 50, 97.5,
   and the share of draws where the leakage-corrected variance is nonpositive.
3. At the point estimate and the three bootstrap quantiles, 300 replicates each of the
   registered default simulator (N5, 125 configurations) and the matched simulator
   (matched_spec), recording mean Lambda for margins and accuracy and the share of the observed
   margin excess.
4. Simulator check at the point estimate. For the matched simulator and the default simulator,
   compare with the observed population, trait by trait: mean half score, SD of configuration
   means, pooled seed variance, per-half item noise variance, and the recovered gain SD, all
   averaged over replicates, with the observed value beside each.
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
from seednoise.estimator import estimate, sigma_e  # noqa: E402
from seednoise.experiments.e5_sensitivity import estimate_gain_sd, matched_spec  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.simulate import default_spec, simulate  # noqa: E402

pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125
N_BOOT, N_REP = 999, 300
lam_obs = {p: float(estimate(pop, p, check=False).lambda_hat) for p in ("margin", "accuracy")}
est = estimate_gain_sd(pop, "margin")
print(f"[gain] {json.dumps(est)} lambda {lam_obs}", flush=True)
report = {"design": __doc__, "observed_lambda": lam_obs, "gain_estimate": est}

rng = np.random.default_rng(0)
recipes = np.unique(pop.recipe)
boot = []
for b in range(N_BOOT):
    draw = rng.choice(recipes, size=recipes.size, replace=True)
    boot.append(estimate_gain_sd(pop.subset_clusters(draw), "margin"))
g = np.array([x["gain_sd"] for x in boot])
report["bootstrap"] = {"draws": N_BOOT, "p025": float(np.percentile(g, 2.5)), "p50": float(np.percentile(g, 50)),
                       "p975": float(np.percentile(g, 97.5)), "share_nonpositive_variance": float(np.mean([x["negative"] for x in boot])),
                       "sd": float(g.std(ddof=1))}
print(f"[bootstrap] {json.dumps(report['bootstrap'])}", flush=True)


def describe(p):
    out = {}
    for name in ("margin", "accuracy"):
        ph = p.pheno(name)
        half = 0.5 * (ph.A + ph.B)
        comp = variance_components(p, name)
        out[name] = {"lambda": float(estimate(p, name, check=False).lambda_hat),
                     "mean": half.mean(axis=(0, 1)).tolist(),
                     "sd_config_means": half.mean(axis=1).std(axis=0, ddof=1).tolist(),
                     "seed_var": np.diag(sigma_e(p, name)).tolist(),
                     "item_noise_var": np.asarray(comp.noise2).tolist()}
    out["gain_sd_recovered"] = float(estimate_gain_sd(p, "margin")["gain_sd"])
    return out


report["observed_description"] = describe(pop)
points = {"estimate": est["gain_sd"], "boot_p025": report["bootstrap"]["p025"],
          "boot_p50": report["bootstrap"]["p50"], "boot_p975": report["bootstrap"]["p975"]}
report["simulations"] = {}
for label, gsd in points.items():
    for spec_name in ("default", "matched"):
        t1 = time.time(); rows = []
        for i in range(N_REP):
            if spec_name == "default":
                spec = default_spec(rbar_e=0.0, n_config=pop.N, seed=104729 * i)
                spec.gain_sd = gsd
            else:
                spec = matched_spec(pop, "margin", gain_sd=gsd, seed=104729 * i)
            sim = simulate(spec)
            rows.append(describe(sim) if label == "estimate" else
                        {p: {"lambda": float(estimate(sim, p, check=False).lambda_hat)} for p in ("margin", "accuracy")})
        cell = {"gain_sd": gsd}
        for p in ("margin", "accuracy"):
            v = np.array([r[p]["lambda"] for r in rows]); v = v[np.isfinite(v)]
            cell[p] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "n": int(v.size)}
        cell["margin_excess_share"] = (cell["margin"]["mean"] - 1) / (lam_obs["margin"] - 1)
        if label == "estimate":
            cell["gain_sd_recovered_mean"] = float(np.mean([r["gain_sd_recovered"] for r in rows]))
            for p in ("margin", "accuracy"):
                for key in ("mean", "sd_config_means", "seed_var", "item_noise_var"):
                    cell.setdefault("check", {}).setdefault(p, {})[key] = {
                        "simulated": np.mean([r[p][key] for r in rows], axis=0).tolist(),
                        "observed": report["observed_description"][p][key]}
        report["simulations"][f"{label}/{spec_name}"] = cell
        print(f"[{label}/{spec_name}] g={gsd:.4f} {time.time() - t1:.0f}s margin {cell['margin']} accuracy {cell['accuracy']} share {cell['margin_excess_share']:.3f}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r10_gain_uncertainty.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
