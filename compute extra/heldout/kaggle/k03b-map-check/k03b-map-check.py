"""k03b (CPU): check the seed-to-branch mapping on every scored verification run.

k03 does this for the pilot's six c4 runs and gates production on the result.
This kernel runs the same comparison over whatever verification shards are
attached, so the check can widen to other sizes and recipes without touching
the gate. The paper's own seed-label argument rests on eight recipes at 150M
and five at 1B, and that limit came from repository names we had wrong rather
than from anything about the release.

For each scored run the per-choice per-byte scores are compared with every
released seed of the same recipe and size. A run matches a seed when no label or
choice count disagrees and the absolute differences clear the tasks.json
thresholds, and the mapping is confirmed for that run only when its assumed seed
is the single match. mapping_check.json carries one row per run with the numbers
behind the verdict, including the best wrong seed, which is what shows whether a
cell was close to ambiguous.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402

tasks_cfg = snapnew.read_json(ROOT / "config" / "tasks.json")
ver = tasks_cfg["verification"]
requests = snapnew.read_requests(snapnew.find_one("requests.jsonl.gz"))

release = {}
files = [p for p in Path("/kaggle/input").rglob("release_arc.npz") if not p.name.startswith("._")]
assert files, "no release_arc.npz attached; run k03a and its slices first"
for f in sorted(files):
    with np.load(f) as z:
        cols = {k: z[k] for k in z.files}
    recipe = cols["recipe"] if "recipe" in cols else np.full(cols["size"].shape, "c4")
    for i in np.lexsort((cols["choice"], cols["doc_id"], cols["seed"], cols["size"], recipe)):
        key = (str(recipe[i]), str(cols["size"][i]), int(cols["seed"][i]))
        rows = release.setdefault(key, {})
        nid = str(cols["native_id"][i])
        doc, label, vals = rows.get(nid, (int(cols["doc_id"][i]), -1, []))
        if cols["is_gold"][i]:
            label = int(cols["choice"][i])
        rows[nid] = (doc, label, vals + [float(cols["per_byte"][i])])
release = {k: {n: (d, lab, np.asarray(v)) for n, (d, lab, v) in rows.items()} for k, rows in release.items()}
print(f"[release] {len(release)} run cells over {len({k[0] for k in release})} recipes", flush=True)

reports = [p for p in Path("/kaggle/input").rglob("shard_report.json") if not p.name.startswith("._")]
assert reports, "no shard_report.json attached; attach a verification shard"
rows, checked = [], 0
for rp in sorted(reports):
    shard = snapnew.read_json(rp)
    for p in sorted((rp.parent / "scores").glob("*.npz")):
        if p.name.startswith("._"):
            continue
        with np.load(p) as z:
            meta = json.loads(str(z["meta"]))
        if ver["name"] not in meta["tasks"]:
            continue
        reqs = snapnew.select_tasks(requests, meta["tasks"])
        s, meta = snapnew.load_scores(p, reqs)
        pb = s["sum_logits"] / s["num_bytes"]
        pos, mine = 0, {}
        for r in reqs:
            k = len(r["continuations"])
            if r["task"] == ver["name"]:
                mine[str(r["native_id"])] = (r["doc_id"], r["label"], pb[pos:pos + k])
            pos += k
        row = {"shard": shard["shard"], "run_key": meta["run_key"], "recipe": meta["recipe"],
               "size": meta["size"], "assumed_seed": meta["seed"], "branch": meta["revision"],
               "by_release_seed": {}}
        for (recipe, size, seed), rel in sorted(release.items()):
            if recipe != meta["recipe"] or size != meta["size"]:
                continue
            shared = sorted(set(mine) & set(rel))
            label_bad = sum(mine[n][1] != rel[n][1] for n in shared)
            count_bad = sum(len(mine[n][2]) != len(rel[n][2]) for n in shared)
            d = np.concatenate([np.abs(mine[n][2] - rel[n][2]) for n in shared
                                if len(mine[n][2]) == len(rel[n][2])] or [np.asarray([np.inf])])
            ok = (len(shared) >= 0.9 * len(mine) and label_bad == 0 and count_bad == 0
                  and float(np.median(d)) <= ver["pass_median_abs_diff_nats_per_byte"]
                  and float(np.quantile(d, 0.99)) <= ver["pass_p99_abs_diff_nats_per_byte"])
            row["by_release_seed"][str(seed)] = {
                "items_shared": len(shared), "items_ours": len(mine), "label_mismatches": label_bad,
                "choice_count_mismatches": count_bad, "median_abs_diff": float(np.median(d)),
                "p99_abs_diff": float(np.quantile(d, 0.99)), "max_abs_diff": float(d.max()), "passes": ok}
        matches = [s2 for s2, v in row["by_release_seed"].items() if v["passes"]]
        wrong = [v["median_abs_diff"] for s2, v in row["by_release_seed"].items() if s2 != str(meta["seed"])]
        row["matching_release_seeds"] = matches
        row["best_wrong_seed_median_abs_diff"] = min(wrong) if wrong else None
        row["verified"] = matches == [str(meta["seed"])]
        rows.append(row)
        checked += 1
        print(f"[check] {row['run_key']} ({row['branch']}) matches {matches}, "
              f"own median {row['by_release_seed'].get(str(meta['seed']), {}).get('median_abs_diff')}", flush=True)

assert checked, "no verification-task scores were found in the attached shards"
by_recipe = {}
for r in rows:
    by_recipe.setdefault(r["recipe"], []).append(r["verified"])
summary = {"runs_checked": checked, "runs_verified": sum(r["verified"] for r in rows),
           "recipes": {k: {"runs": len(v), "verified": int(sum(v))} for k, v in sorted(by_recipe.items())},
           "sizes_checked": sorted({r["size"] for r in rows}),
           "all_verified": all(r["verified"] for r in rows),
           "thresholds": {"median": ver["pass_median_abs_diff_nats_per_byte"],
                          "p99": ver["pass_p99_abs_diff_nats_per_byte"]},
           "wall_seconds": time.time() - t0}
snapnew.write_json(W / "mapping_check.json", {"summary": summary, "runs": rows})
print(json.dumps(summary, indent=1), flush=True)
if not summary["all_verified"]:
    sys.exit("some runs did not match their assumed seed alone; read mapping_check.json")
