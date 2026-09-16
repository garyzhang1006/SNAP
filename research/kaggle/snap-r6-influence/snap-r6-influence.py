"""Recomputation of the recipe influence concentration, to settle two numbers that disagree.

Design fixed before running (2026-09-15, written 23:55 EDT). Appendix A reports a participation ratio of
2.88 on margins and 8.68 on accuracy, says that one recipe carries 0.543 of the squared margin influence,
and says that removing that recipe moves the estimate by at most 0.037. Those figures come from the
original analysis record. The fitted-scenario run snap-r6-matched-a recomputed the same concentration on
the same data with cluster_influence and returned 0.5199, which the coverage appendix prints as 0.520.
Both passages describe the largest recipe's share of squared influence, so one of them is wrong or the
two use different definitions. This run recomputes every version. It reports the influence vector on
theta, its participation ratio under two conventions, the largest share of squared influence, the same
quantities computed on Lambda rather than on theta through the delta method, the same quantities with
the theta residual left unscaled by the denominator, and the change in the estimate from removing each
recipe in turn. Whichever definition returns 0.543 is the one Appendix A used, and if none does then the
0.543 figure doesn't survive and the paper carries the recomputed value.
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
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_influence  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
report = {"design": __doc__, "n_config": pop.N, "phenotypes": {}}


def concentration(psi):
    s = psi ** 2
    tot = float(s.sum())
    share = s / tot
    return {"max_squared_share": float(share.max()),
            "participation_ratio_squared": float(1.0 / np.sum(share ** 2)),
            "participation_ratio_abs": float(tot ** 2 / np.sum(psi ** 4)),
            "participation_ratio_from_abs_weights": float(np.sum(np.abs(psi)) ** 2 / tot),
            "top_share_rank2": float(np.sort(share)[-2]),
            "n_clusters": int(psi.size)}


for name in ("margin", "accuracy"):
    est = estimate(pop, name, check=False)
    T, U = np.asarray(est.T, float), np.asarray(est.U, float)
    lam = float(est.lambda_hat)
    theta = float(T.sum() / U.sum())
    psi, keys, inv = cluster_influence(T, U, pop.recipe)
    cell = {"lambda_hat": lam, "theta": theta, "on_theta": concentration(psi)}
    # Delta method carries the same influence to Lambda by a constant factor, so
    # every share is identical; recorded here so the check is explicit rather than assumed.
    cell["on_lambda"] = concentration(psi / (2.0 * np.sqrt(theta)))
    # The unscaled residual drops the 1/sum U factor, which is also constant.
    e = np.bincount(inv, weights=T - theta * U, minlength=keys.size)
    cell["unscaled_residual"] = concentration(e)
    # A concentration measure on the cluster numerators themselves, which is a different quantity.
    cell["on_cluster_numerator"] = concentration(np.bincount(inv, weights=T, minlength=keys.size))
    cell["on_cluster_denominator"] = concentration(np.bincount(inv, weights=U, minlength=keys.size))
    drops = []
    for g in keys:
        sub = pop.subset_clusters([k for k in keys if k != g])
        drops.append(abs(float(estimate(sub, name, check=False).lambda_hat) - lam))
    cell["removal"] = {"max_abs_change": float(np.max(drops)), "median_abs_change": float(np.median(drops)),
                       "change_for_top_influence_recipe": float(drops[int(np.argmax(psi ** 2))])}
    report["phenotypes"][name] = cell
    print(f"[{name}] {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_influence.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
