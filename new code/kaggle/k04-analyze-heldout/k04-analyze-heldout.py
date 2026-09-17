"""k04 (CPU): the held-out test, computed with the paper's own estimator code.

Inputs: every k02 shard output (pilot included), the k01 request file, the k03
decision, seednoise at the paper's commit, and the 375 shipped reduced runs.

Steps, in order:
1. Gather one score file per run, check hashes, steps and completeness.
2. Reduce each run to seednoise per-item phenotypes on the final held-out tasks
   (one trait per task, plain item means, gain = mean per-byte log-likelihood
   over the held-out choices) and save them in seednoise's run format.
3. Split halves once for all runs: split_clustered on passage groups, seed
   tasks.json half_split_seed, so items sharing a passage never straddle halves.
4. Held-out population: estimate() and wild_bootstrap_t(n_boot=4999, seed=0) on
   margin and accuracy, as in seednoise.experiments.e2_primary, plus the
   batch-free contrast.
5. Pre-registered rule (PROTOCOL_heldout.md): PASS if the lower 95% limit of the
   held-out margin Lambda is above 1.
6. Reproduction check: the shipped runs alone must give margin Lambda 1.24395
   (to 5e-4), and the same number restricted to the scored sizes is reported
   next to the held-out one.
7. Combined 14-trait population (10 original + 4 held-out traits), joined on
   recipe, size, seed and step. Reported, not part of the pass rule.
8. Leave-one-task-out on the held-out population. Reported, not pre-registered.
"""
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402

sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn[0].parent)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.halves import MASTER_SEED, split_clustered, split_items  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.phenotypes import ItemPhenotypes, reduce_choices  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402
from seednoise.store import load_run, save_run  # noqa: E402

PAPER_MARGIN_LAMBDA = 1.24395
tasks_cfg = snapnew.read_json(ROOT / "config" / "tasks.json")
runs_cfg = {r["run_key"]: r for r in snapnew.read_json(ROOT / "config" / "runs.json")["runs"]}
frozen = snapnew.read_json(ROOT / "config" / "frozen.json")
decision = snapnew.read_json(snapnew.find_one("decision.json"))
assert decision["seed_branch_mapping_verified"] is True, "k03 did not verify the seed-branch mapping"
FINAL = decision["heldout_tasks_final"]
K_NEW = len(FINAL)
req_path = snapnew.find_one("requests.jsonl.gz")
assert snapnew.sha256(req_path) == frozen["requests_sha256"], "request file is not the frozen one"
requests = snapnew.read_requests(req_path)
log = {"final_tasks": FINAL, "notes": []}

# 1. Gather scores.
files = {}
for p in sorted(Path("/kaggle/input").rglob("scores/*.npz")):
    if p.name.startswith("._") or p.name.endswith(".partial.npz"):
        continue
    key = p.name[:-4]
    files.setdefault(key, []).append(p)
dupes = {k: [str(x) for x in v] for k, v in files.items() if len(v) > 1}
if dupes:
    log["notes"].append(f"{len(dupes)} runs scored twice; the first path in sorted order is used")
files = {k: v[0] for k, v in files.items()}
unknown = sorted(set(files) - set(runs_cfg))
assert not unknown, f"score files for runs not in config/runs.json: {unknown[:5]}"
# The pilot's three c4 150M runs are not a scope on their own; a size counts only
# when more than one configuration at it was scored, and then it must be complete.
per_size = {s: sum(runs_cfg[k]["size"] == s for k in files) for s in tasks_cfg["scope"]["full"]}
sizes_scored = [s for s, n in per_size.items() if n > 3]
dropped = sorted(k for k in files if runs_cfg[k]["size"] not in sizes_scored)
if dropped:
    log["notes"].append(f"{len(dropped)} scored runs at sizes outside the scope are not used: {dropped}")
files = {k: v for k, v in files.items() if runs_cfg[k]["size"] in sizes_scored}
expected = [k for k, r in runs_cfg.items() if r["size"] in sizes_scored]
missing = sorted(set(expected) - set(files))
assert not missing, f"{len(missing)} runs at the scored sizes have no scores, first {missing[:5]}"
log["sizes_scored"] = sizes_scored
log["runs_scored"] = len(files)
print(f"[gather] {len(files)} runs over sizes {sizes_scored}", flush=True)

# 2. Reduce to per-item phenotypes on the final tasks.
task_pos = {t: i for i, t in enumerate(FINAL)}
new_dir = TMP / "runs_heldout"
shutil.rmtree(new_dir, ignore_errors=True)
new_dir.mkdir(parents=True)
cluster_of_item = ref_ids = None
hub_shas = {}
for key, p in sorted(files.items()):
    with np.load(p) as z:
        meta = json.loads(str(z["meta"]))
    assert meta["requests_sha256"] == frozen["requests_sha256"], f"{key} was scored on a different request file"
    reqs = snapnew.select_tasks(requests, meta["tasks"])
    s, meta = snapnew.load_scores(p, reqs)
    pb = s["sum_logits"] / s["num_bytes"]
    iid, tr, score, gold, clus = [], [], [], [], {}
    pos = 0
    for r in reqs:
        k = len(r["continuations"])
        if r["task"] in task_pos:
            i = snapnew.item_id(r["task_index"], r["doc_id"])
            for c in range(k):
                iid.append(i)
                tr.append(task_pos[r["task"]])
                score.append(pb[pos + c])
                gold.append(c == r["label"])
            clus[i] = r["group"]
        pos += k
    assert set(tr) == set(range(K_NEW)), f"{key} lacks some final tasks: scored {meta['tasks']}"
    items = reduce_choices(np.asarray(iid), np.asarray(tr), np.asarray(score), np.asarray(gold))
    if cluster_of_item is None:
        cluster_of_item = np.asarray([clus[int(i)] for i in items.item_id])
        ref_ids = items.item_id
    assert np.array_equal(items.item_id, ref_ids), f"{key} has a different item set"
    run = runs_cfg[key]
    assert meta["step"] == run["step"] and meta["revision"] == run["revision"], f"{key} metadata disagrees with runs.json"
    hub_shas[key] = meta["hub_sha"]
    save_run(new_dir / f"{key}.npz", items,
             {"recipe": run["recipe"], "size": run["size"], "seed": run["seed"], "step": run["step"],
              "batch": run["batch"], "gain": float(np.mean(score))})
_, cluster_codes = np.unique(cluster_of_item, return_inverse=True)
trait_new = load_run(next(new_dir.glob("*.npz")))[0].trait

# 3. Halves.
mask_new = split_clustered(trait_new, cluster_codes, K_NEW, seed=tasks_cfg["half_split_seed"])
log["half_items_per_task"] = {t: [int((mask_new & (trait_new == j)).sum()), int((~mask_new & (trait_new == j)).sum())]
                              for j, t in enumerate(FINAL)}


def headline(pop, label):
    rows = {}
    for name in (MARGIN, ACCURACY):
        for which in ("all", "batch_free"):
            try:
                e = estimate(pop, name, which=which, check=True)
                i = wild_bootstrap_t(e.T, e.U, pop.recipe, n_boot=4999, seed=0)
                rows[f"{name}/{which}"] = {"Lambda": e.lambda_hat, "lo": i.lo, "hi": i.hi, "se": i.se,
                                           "N": e.N, "K": e.K, "clusters": i.n_clusters}
            except Exception as exc:  # noqa: BLE001
                rows[f"{name}/{which}"] = {"error": f"{type(exc).__name__}: {exc}"}
    print(f"[{label}] " + json.dumps({k: {kk: round(vv, 5) if isinstance(vv, float) else vv for kk, vv in v.items()}
                                      for k, v in rows.items()}), flush=True)
    return rows


# 4 and 5. Held-out population and the pass rule.
pop_new, info_new = build_population(new_dir, FINAL, n_runs=3, half_mask=mask_new)
res_new = headline(pop_new, "heldout")
m = res_new[f"{MARGIN}/all"]
verdict = "PASS" if m["lo"] > 1.0 else "FAIL"

# 6. Reproduce the paper's number from the shipped runs.
old_src = sorted({p.parent for p in Path("/kaggle/input").rglob("*.npz")
                  if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")})
assert len(old_src) == 1, f"shipped reduced runs not found in exactly one directory: {old_src}"
old_dir = old_src[0]
pop_old, _ = build_population(old_dir, TRAITS, n_runs=3)
old_lambda = estimate(pop_old, MARGIN).lambda_hat
reproduced = abs(old_lambda - PAPER_MARGIN_LAMBDA) < 5e-4
print(f"[reproduce] shipped runs give margin Lambda {old_lambda:.5f}; paper {PAPER_MARGIN_LAMBDA}", flush=True)
assert reproduced, "the shipped runs don't reproduce the paper's Lambda; stop and investigate before reading held-out numbers"
res_old_same_sizes = headline(build_population(old_dir, TRAITS, n_runs=3, sizes=sizes_scored)[0], "original-traits-same-sizes")

# 7. Combined population.
old_by = {}
for p in sorted(old_dir.glob("*.npz")):
    if p.name.startswith("._"):
        continue
    items, meta = load_run(p)
    old_by[(meta["recipe"].lower(), meta["size"], int(meta["seed"]))] = (items, meta)
comb_dir = TMP / "runs_combined"
shutil.rmtree(comb_dir, ignore_errors=True)
comb_dir.mkdir(parents=True)
mask_old = None
for p in sorted(new_dir.glob("*.npz")):
    items_n, meta_n = load_run(p)
    run = runs_cfg[p.name[:-4]]
    items_o, meta_o = old_by[(run["release_recipe"].lower(), run["size"], run["seed"])]
    assert int(meta_o["step"]) == run["step"], f"{p.name}: shipped run is at step {meta_o['step']}, scored {run['step']}"
    assert int(meta_o["batch"]) == run["batch"], f"{p.name}: batch label disagrees with the shipped run"
    if mask_old is None:
        mask_old = split_items(items_o.trait, len(TRAITS), seed=MASTER_SEED)
    comb = ItemPhenotypes(item_id=np.concatenate([items_o.item_id, items_n.item_id]),
                          trait=np.concatenate([items_o.trait, items_n.trait + len(TRAITS)]),
                          margin=np.concatenate([items_o.margin, items_n.margin]),
                          correct=np.concatenate([items_o.correct, items_n.correct]),
                          group=np.concatenate([items_o.group, items_n.trait + 1000]))
    assert np.all(np.diff(comb.item_id) > 0), "combined item ids are not sorted and unique"
    save_run(comb_dir / p.name, comb, dict(meta_o, recipe=run["recipe"]))
pop_comb, _ = build_population(comb_dir, TRAITS + FINAL, n_runs=3, half_mask=np.concatenate([mask_old, mask_new]))
res_comb = headline(pop_comb, "combined-14")

# 8. Leave one held-out task out.
loto = {}
if K_NEW > 2:
    for j, t in enumerate(FINAL):
        keep = [x for x in FINAL if x != t]
        d = TMP / f"loto_{t}"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        sel = trait_new != j
        remap = {old: new for new, old in enumerate(k for k in range(K_NEW) if k != j)}
        for p in sorted(new_dir.glob("*.npz")):
            items, meta = load_run(p)
            tr = np.asarray([remap[int(x)] for x in items.trait[sel]])
            save_run(d / p.name, ItemPhenotypes(item_id=items.item_id[sel], trait=tr, margin=items.margin[sel],
                                                correct=items.correct[sel], group=tr), meta)
        loto[t] = headline(build_population(d, keep, n_runs=3, half_mask=mask_new[sel])[0], f"without-{t}")

out = {"verdict": verdict, "rule": "PASS if the lower 95% wild-bootstrap limit of held-out margin Lambda is above 1",
       "heldout": res_new, "heldout_info": info_new, "original_traits_same_sizes": res_old_same_sizes,
       "original_margin_lambda_all_sizes": old_lambda, "combined_14_traits": res_comb,
       "leave_one_task_out": loto, "hub_shas": hub_shas, "requests_sha256": frozen["requests_sha256"],
       "log": log, "wall_seconds": time.time() - t0,
       "labels": {"heldout.margin/all": "pre-registered test", "everything else": "reported, not pre-registered"}}
snapnew.write_json(W / "heldout_results.json", out)
with open(W / "heldout_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["population", "phenotype_contrast", "Lambda", "lo", "hi", "N", "K"])
    for label, block in [("heldout", res_new), ("original_same_sizes", res_old_same_sizes), ("combined_14", res_comb)] + \
                        [(f"without_{t}", v) for t, v in loto.items()]:
        for k, v in block.items():
            w.writerow([label, k, v.get("Lambda"), v.get("lo"), v.get("hi"), v.get("N"), v.get("K")])
shutil.rmtree(TMP, ignore_errors=True)
print(f"[verdict] {verdict}: held-out margin Lambda {m['Lambda']:.4f} [{m['lo']:.4f}, {m['hi']:.4f}]", flush=True)
