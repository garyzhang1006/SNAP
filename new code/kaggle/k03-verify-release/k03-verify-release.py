"""k03 (CPU): check the pilot against the DataDecide release, then apply the backup rule.

Three checks, all written to decision.json, and production scoring is blocked
unless the first two pass.

1. Seed-branch mapping. For c4 at 150M and 1B the pilot scored ARC-Easy on
   hub branches default, small-aux-2, small-aux-3 (150M) and default,
   large-aux-2, large-aux-3 (1B). The release tarball holds OLMES's own ARC-Easy
   predictions for seeds 2, 14, 15 and 2, 4, 5 at the same steps. Every hub run
   is compared with every release seed of its size, per choice, in nats per
   byte. The mapping is verified only if each hub run matches its assumed seed
   within the tasks.json thresholds and no other seed also matches.

2. Scoring fidelity. The matched pairs above are the fidelity test: if the
   scorer, prompt or tokenisation differed from OLMES, the matched differences
   would miss the thresholds even with the right seeds.

3. Backup rule (pre-registered in tasks.json). Mean accuracy of the three 1B
   runs per held-out task against chance plus 0.02; a task below the bar is
   replaced by the first backup that clears it. Only accuracy is read.

Also writes token_ratio_production_over_pilot for tools/make_shards.py.
"""
import io
import json
import subprocess
import sys
import tarfile
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
from seednoise.data.datadecide import LN2, download_recipe, parse_member  # noqa: E402

tasks_cfg = snapnew.read_json(ROOT / "config" / "tasks.json")
ver = tasks_cfg["verification"]
requests = snapnew.read_requests(snapnew.find_one("requests.jsonl.gz"))
pilot_dir = snapnew.find_one("shard_report.json").parent
report = snapnew.read_json(pilot_dir / "shard_report.json")
assert report["shard"] == "pilot", f"attached shard report is {report['shard']}, expected the pilot"
assert not report["failed"] and not report["not_started"], "pilot is incomplete; rerun it before verifying"

scores = {}
for p in sorted((pilot_dir / "scores").glob("*.npz")):
    with np.load(p) as z:
        meta = json.loads(str(z["meta"]))
    reqs = snapnew.select_tasks(requests, meta["tasks"])
    s, meta = snapnew.load_scores(p, reqs)
    scores[meta["run_key"]] = (s, meta, reqs)
print(f"[pilot] {len(scores)} runs: {sorted(scores)}", flush=True)
modes = {k: v[1]["stats"]["mode"] for k, v in scores.items()}
checks = {k: v[1]["stats"]["check_max_abs_diff_nats"] for k, v in scores.items()}

# 1 and 2: ARC-Easy against the release.
ours = {}
for key, (s, meta, reqs) in scores.items():
    pb = s["sum_logits"] / s["num_bytes"]
    pos, per_doc = 0, {}
    for r in reqs:
        k = len(r["continuations"])
        if r["task"] == ver["name"]:
            per_doc[str(r["native_id"])] = (r["doc_id"], r["label"], pb[pos:pos + k])
        pos += k
    ours[key] = per_doc

tar = TMP / "c4.tar.gz"
for attempt in range(1, 4):
    try:
        download_recipe("c4", tar, progress=False)
        break
    except Exception as error:  # noqa: BLE001
        print(f"[release] attempt {attempt} failed: {type(error).__name__}: {error}", flush=True)
        tar.unlink(missing_ok=True)
        if attempt == 3:
            raise
        time.sleep(30)
pilot_runs = [v[1] for v in scores.values()]
wanted = {(m["size"], m["step"]) for m in pilot_runs}
release = {}
with tarfile.open(tar, mode="r|gz") as tf:
    for m in tf:
        k = parse_member(m.name)
        if k is None or (k.size, k.step) not in wanted:
            continue
        inner = tf.extractfile(m).read()
        with tarfile.open(fileobj=io.BytesIO(inner), mode="r:gz") as it:
            for im in it:
                if im.name.rsplit("/", 1)[-1] == f"{ver['release_task']}-predictions.jsonl":
                    rows = {}
                    for line in it.extractfile(im).read().splitlines():
                        if line.strip():
                            r = json.loads(line)
                            pb = np.asarray([-float(o["logits_per_byte"]) * LN2 for o in r["model_output"]])
                            rows[str(r["native_id"])] = (r["doc_id"], r["label"], pb)
                    release[(k.size, k.seed)] = rows
tar.unlink(missing_ok=True)
print(f"[release] ARC-Easy predictions for {sorted(release)}", flush=True)

comparisons, mapping_ok = [], True
for m in pilot_runs:
    mine = ours[m["run_key"]]
    row = {"run_key": m["run_key"], "assumed_seed": m["seed"], "branch": m["revision"], "by_release_seed": {}}
    for (size, seed), rel in sorted(release.items()):
        if size != m["size"]:
            continue
        shared = sorted(set(mine) & set(rel))
        label_mismatch = sum(mine[n][1] != rel[n][1] for n in shared)
        choice_mismatch = sum(len(mine[n][2]) != len(rel[n][2]) for n in shared)
        d = np.concatenate([np.abs(mine[n][2] - rel[n][2]) for n in shared
                            if len(mine[n][2]) == len(rel[n][2])] or [np.asarray([np.inf])])
        ok = (len(shared) >= 0.9 * len(mine) and label_mismatch == 0 and choice_mismatch == 0
              and float(np.median(d)) <= ver["pass_median_abs_diff_nats_per_byte"]
              and float(np.quantile(d, 0.99)) <= ver["pass_p99_abs_diff_nats_per_byte"])
        row["by_release_seed"][str(seed)] = {"items_shared": len(shared), "items_ours": len(mine),
                                             "label_mismatches": label_mismatch, "choice_count_mismatches": choice_mismatch,
                                             "median_abs_diff": float(np.median(d)), "p99_abs_diff": float(np.quantile(d, 0.99)),
                                             "max_abs_diff": float(d.max()), "passes": ok}
    matches = [s for s, v in row["by_release_seed"].items() if v["passes"]]
    row["matching_release_seeds"] = matches
    row["verified"] = matches == [str(m["seed"])]
    mapping_ok &= row["verified"]
    comparisons.append(row)
    print(f"[verify] {m['run_key']} ({m['revision']}) matches release seeds {matches}", flush=True)
mapping_ok &= {(m["size"], m["seed"]) for m in pilot_runs} <= set(release)

# 3: backup rule, accuracy only.
def accuracy_by_task(key):
    s, _, reqs = scores[key]
    it = snapnew.per_item(s, reqs)
    names = {r["task_index"]: r["task"] for r in reqs}
    return {names[t]: float(it["correct"][it["task_index"] == t].mean()) for t in np.unique(it["task_index"])}

chance = {}
for r in requests:
    chance.setdefault(r["task"], []).append(1 / len(r["continuations"]))
chance = {t: float(np.mean(v)) for t, v in chance.items()}
one_b = [k for k, v in scores.items() if v[1]["size"] == "1B"]
acc = {t: float(np.mean([accuracy_by_task(k)[t] for k in one_b])) for t in chance}
bar = {t: chance[t] + 0.02 for t in chance}
passes = {t: acc[t] >= bar[t] for t in chance}
backups = [b["name"] for b in tasks_cfg["backups_in_order"]]
final, replacements = [], {}
for t in [h["name"] for h in tasks_cfg["heldout"]]:
    if passes[t]:
        final.append(t)
        continue
    sub = next((b for b in backups if passes[b] and b not in final), None)
    if sub is not None:
        backups.remove(sub)
        final.append(sub)
    replacements[t] = sub

def chars(names):
    rs = [r for r in requests if r["task"] in names]
    return sum(len(r["context"]) + sum(len(c) for c in r["continuations"]) for r in rs)

pilot_tasks = scores[one_b[0]][1]["tasks"]
decision = {
    "seed_branch_mapping_verified": bool(mapping_ok),
    "comparisons": comparisons,
    "scoring_modes": modes, "cache_check_max_abs_diff_nats": checks,
    "backup_rule": tasks_cfg["backup_rule"], "accuracy_1b_mean": acc, "chance": chance, "bar": bar,
    "heldout_replacements": replacements, "heldout_tasks_final": final,
    "token_ratio_production_over_pilot": chars(final) / chars(pilot_tasks),
    "token_ratio_note": "character ratio of context plus continuations, used as a stand-in for the token ratio",
    "wall_seconds": time.time() - t0,
}
snapnew.write_json(W / "decision.json", decision)
print(json.dumps({k: decision[k] for k in ("seed_branch_mapping_verified", "accuracy_1b_mean", "heldout_replacements",
                                            "heldout_tasks_final", "token_ratio_production_over_pilot")}, indent=1), flush=True)
if not mapping_ok:
    sys.exit("seed-branch mapping or scoring fidelity failed; read decision.json comparisons before changing anything")
