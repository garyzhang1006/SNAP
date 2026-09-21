"""R6 whether one run, or one seed label, carries either conclusion.

Design fixed before running (2026-09-16, written 00:05 EDT). snap-r6-leave-one-out deleted recipes,
size bands, benchmarks and recipe pairs, which covers every way of dropping a column of the design. It
never drops a run, and the design has only three of them per configuration, so a single anomalous run
inside each configuration is the deletion with the least data standing between it and the estimate. The
release also reuses seed labels across recipes, with labels 2, 14 and 15 below 1B and 2, 4 and 5 at 1B,
so dropping a label is a second deletion that a reader can name. This run does both. It re-estimates
both scales on each of the three pairs of runs, which is what remains after one run is deleted, and on
each population that drops one seed label, with a recipe-clustered wild interval at 4,999 draws in every
case. With two runs left the contrast space has one direction rather than two, so the estimator uses
less information and the intervals should widen, and the run reports the width beside the estimate so
that the widening is visible rather than assumed. A conclusion that holds under all six deletions is
one that no single run carries, and one that fails under a particular deletion names the run to check.
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
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)
BATCH = np.asarray(pop.batch)
print(f"[batch] shape {BATCH.shape} unique {np.unique(BATCH).tolist()}", flush=True)


def drop_run(p, name, keep):
    """Population holding only the run slots in keep, for every configuration."""
    ph = p.pheno(name)
    k = np.asarray(keep, int)
    sub = Phenotype(name, ph.A[:, k, :], ph.B[:, k, :])
    # gainA and gainB are (N, R) as well, so they follow the same run selection.
    return Population({name: sub}, np.asarray(p.gainA)[:, k], np.asarray(p.gainB)[:, k],
                      np.asarray(p.batch)[:, k], p.recipe, p.size,
                      list(p.traits), p.config_ids, p.n_items)


def interval(p, name):
    est = estimate(p, name, check=False)
    iv = wild_bootstrap_t(est.T, est.U, p.recipe, n_boot=4999, seed=0)
    lo, hi = float(iv.lo), float(iv.hi)
    return {"lambda_hat": float(est.lambda_hat), "lo": lo, "hi": hi,
            "width": hi - lo if np.isfinite(lo) and np.isfinite(hi) else None,
            "excludes_one": bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 1.0 or hi < 1.0))}


BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
report = {"design": __doc__, "traits": TR, "base": {}, "leave_one_run": {}, "leave_one_seed_label": {}}
for name in ("margin", "accuracy"):
    report["base"][name] = interval(pop, name)
    print(f"[base/{name}] {json.dumps(report['base'][name])}", flush=True)

for drop in range(3):
    keep = [r for r in range(3) if r != drop]
    for name in ("margin", "accuracy"):
        cell = interval(drop_run(pop, name, keep), name)
        cell["kept_run_slots"] = keep
        report["leave_one_run"][f"drop_slot_{drop}/{name}"] = cell
        print(f"[run/{drop}/{name}] {json.dumps(cell)}", flush=True)

# A seed label sits in a different run slot from one configuration to the next, so dropping a label
# means dropping whichever slot carries it in each configuration, which the batch array records.
labels = sorted(set(int(x) for x in np.unique(BATCH)))
report["seed_labels_present"] = labels
# pop.batch holds 0 for the default run and 1, 2 for the auxiliary batch, so when it carries only
# those three values it indexes run slots and the label deletion would repeat the slot deletion above.
report["batch_holds_slot_indices"] = set(labels) <= {0, 1, 2}
for lab in (labels if not report["batch_holds_slot_indices"] else []):
    hit = BATCH == lab
    per_config = hit.sum(axis=1)
    if per_config.max() != 1 or per_config.min() != 1:
        report["leave_one_seed_label"][f"drop_{lab}"] = {
            "skipped": True,
            "reason": f"label {lab} appears {per_config.min()} to {per_config.max()} times per configuration"}
        print(f"[label/{lab}] skipped, {per_config.min()}-{per_config.max()} per configuration", flush=True)
        continue
    keep_idx = np.argsort(hit, axis=1)[:, :2]
    for name in ("margin", "accuracy"):
        ph = pop.pheno(name)
        A = np.take_along_axis(ph.A, keep_idx[:, :, None], axis=1)
        B = np.take_along_axis(ph.B, keep_idx[:, :, None], axis=1)
        q = Population({name: Phenotype(name, A, B)},
                       np.take_along_axis(np.asarray(pop.gainA), keep_idx, axis=1),
                       np.take_along_axis(np.asarray(pop.gainB), keep_idx, axis=1),
                       np.take_along_axis(BATCH, keep_idx, axis=1), pop.recipe, pop.size,
                       list(pop.traits), pop.config_ids, pop.n_items)
        cell = interval(q, name)
        report["leave_one_seed_label"][f"drop_{lab}/{name}"] = cell
        print(f"[label/{lab}/{name}] {json.dumps(cell)}", flush=True)

if report["batch_holds_slot_indices"]:
    report["leave_one_seed_label"] = {
        "skipped": True,
        "reason": "pop.batch indexes run slots rather than seed labels, so the label deletion would "
                  "repeat the slot deletion, and a label deletion needs the seed identity from the "
                  "run filenames instead"}
    print("[label] skipped, batch holds slot indices", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_leave_one_run.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
