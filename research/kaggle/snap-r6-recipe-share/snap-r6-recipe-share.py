"""R6 test for the run effect the shipped clustering assumes, shared across sizes inside one recipe.

Design fixed before running (2026-09-15, written 23:10 EDT). snap-r6-band-share asks whether a run effect
is shared across recipes inside a size band, which is the violation that breaks the shipped interval.
This run asks the mirror question, which is whether the sharing the shipped interval assumes is present
at all. The interval clusters on the 25 recipes because a recipe's seed effects plausibly repeat across
the five sizes trained on it. snap-r6-twoway already gave a reason to doubt that, since the component
that puts every configuration in its own cluster gives 0.233 on the full-battery margin and exceeds the
recipe component of 0.112, which is what happens when the recipe sums cancel rather than reinforce. The
statistic here is the one from the size-band run with the grouping swapped. Line each configuration's
runs up by batch slot, average the run deviations over the five sizes of a recipe, and take the weighted
cross-half covariance of those recipe means summed over the 25 recipes. The null permutes each
configuration's runs among its own batch slots, which preserves every configuration's own deviations and
destroys only the alignment across sizes. A statistic above the null says the recipe clustering answers
to something real in the data. A statistic inside the null says the clustering is a precaution rather
than a correction, which is worth saying plainly beside the coverage results.
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
SEED = 20260932
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
group = np.asarray(pop.recipe)
batch = np.asarray(pop.batch)
groups = np.unique(group)
K_ALL = len(TR)
print(f"[base] {groups.size} recipes, batch values {np.unique(batch).tolist()}", flush=True)
# Every configuration must carry one run in each batch slot, or the recipe means mix slots.
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


def group_statistic(dA, dB, w, perm=None):
    """Weighted cross-half covariance of the recipe means, summed over recipes."""
    a, b = (dA, dB) if perm is None else (np.take_along_axis(dA, perm[:, :, None], axis=1),
                                         np.take_along_axis(dB, perm[:, :, None], axis=1))
    mA = np.stack([a[group == z].mean(axis=0) for z in groups])
    mB = np.stack([b[group == z].mean(axis=0) for z in groups])
    T, _ = weighted_cross(mA, mB, w)
    return T


report = {"design": __doc__, "traits": TR, "n_perm": N_PERM, "seed": SEED, "batteries": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    w = np.full(len(idx), 1.0 / len(idx))
    for name in ("margin", "accuracy"):
        t1 = time.time()
        dA, dB = deviations(name, idx)
        obs = group_statistic(dA, dB, w)
        per_config, _ = weighted_cross(dA, dB, w)
        rng = np.random.default_rng(SEED)
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            perm = np.argsort(rng.random(dA.shape[:2]), axis=1)
            null[p] = group_statistic(dA, dB, w, perm)
        sd = float(null.std(ddof=1))
        cell = {"observed": obs, "per_config_total": per_config,
                "observed_over_per_config": obs / per_config if per_config else None,
                # Averaging n independent configurations divides a covariance by n, and the
                # group total sums n of them, so the ratio lands near 1/n^2 without sharing.
                "independence_expectation": 1.0 / float((group == groups[0]).sum()) ** 2,
                "null_mean": float(null.mean()), "null_sd": sd,
                "null_p05": float(np.percentile(null, 5)), "null_p95": float(np.percentile(null, 95)),
                "z": (obs - float(null.mean())) / sd if sd > 0 else None,
                "share_at_or_above_observed": float(np.mean(null >= obs)),
                "seconds": time.time() - t1}
        report["batteries"][f"{label}/{name}"] = cell
        print(f"[{label}/{name}] {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_recipe_share.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
