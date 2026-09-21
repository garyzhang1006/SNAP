"""Seed-to-seed spread of the permutation experiment, to settle the one figure that didn't reproduce.

Design fixed before running (2026-09-16, written 01:45 EDT). Three record-check runs reproduced eleven
of twelve figures the paper carries from the original analysis record. The exception is the seed-label
permutation, where the record reports margin coverage 0.925 from 1,000 permutations and our 2,000
permutations give 0.9435. The formula puts that gap at about two standard errors, which neither
confirms nor refutes the record. This run measures the spread directly. It repeats the experiment ten
times with 1,000 permutations each, which is the record's replicate count, using a different stream for
every repeat, and it scores both the wild interval and the cluster-robust t. If 0.925 falls inside the
observed spread then the record is a draw from the same distribution and the paper should say so. If it
falls outside, the record used a different procedure and the recomputation stands on its own.
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
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.nulls import permute_seed_labels  # noqa: E402

pop, info = build_population(runs, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
RECORD = {"wild": {"margin": 0.925, "accuracy": 0.954}, "cluster_t": {"margin": 0.881, "accuracy": 0.941}}
N_REP, N_SEED = 1000, 10
report = {"design": __doc__, "record": RECORD, "n_rep": N_REP, "n_seed": N_SEED, "phenotypes": {}}

for name in ("margin", "accuracy"):
    rows = []
    for seed in range(N_SEED):
        t1 = time.time()
        rng = np.random.default_rng(seed)
        cw = ct = bw = 0
        for rep in range(N_REP):
            q = permute_seed_labels(pop, name, rng)
            e = estimate(q, f"{name}|perm", check=False)
            iv = wild_bootstrap_t(e.T, e.U, q.recipe, n_boot=4999, seed=rep)
            lo, hi = float(iv.lo), float(iv.hi)
            if np.isfinite(lo) and np.isfinite(hi):
                cw += lo <= 1.0 <= hi
                bw += hi < 1.0
            c = cluster_t_interval(e.T, e.U, q.recipe)
            if np.isfinite(c.lo) and np.isfinite(c.hi):
                ct += c.lo <= 1.0 <= c.hi
        rows.append({"seed": seed, "wild_coverage": cw / N_REP, "cluster_t_coverage": ct / N_REP,
                     "wild_below_null": bw / N_REP, "seconds": time.time() - t1})
        print(f"[{name}/seed {seed}] {json.dumps(rows[-1])}", flush=True)
    cell = {"rows": rows}
    for key in ("wild_coverage", "cluster_t_coverage"):
        v = np.array([r[key] for r in rows])
        rec = RECORD[key.replace("_coverage", "")][name]
        cell[key] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "min": float(v.min()), "max": float(v.max()),
                     "record": rec, "record_inside_range": bool(v.min() <= rec <= v.max()),
                     "z_against_record": float((v.mean() - rec) / (v.std(ddof=1) / np.sqrt(v.size)))}
    report["phenotypes"][name] = cell
    print(f"[{name}] {json.dumps({k: cell[k] for k in ('wild_coverage', 'cluster_t_coverage')})}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_perm_seeds.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
