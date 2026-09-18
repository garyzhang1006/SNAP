"""k01b (CPU): resolve all 375 hub branches before any GPU time is spent on them.

A production shard that meets a missing branch or a checkpoint without weights
wastes the GPU minutes it already spent downloading. This kernel asks the hub
for every run in config/runs.json, records the commit the branch points at, and
checks that the revision carries a config, a tokenizer and at least one
safetensors file. It also sums the weight bytes per run, which gives
tools/make_shards.py a measured download size per size class instead of a guess.

runs_verified.json holds one row per run plus a per-size summary. Exit status is
non-zero when any run fails, and the failures are listed first in the output.
"""
import concurrent.futures as cf
import sys
import time
from pathlib import Path

W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402
from huggingface_hub import HfApi  # noqa: E402

t0 = time.time()
runs = snapnew.read_json(ROOT / "config" / "runs.json")["runs"]
api = HfApi()


def look(run):
    row = {"run_key": run["run_key"], "repo": run["repo"], "revision": run["revision"],
           "size": run["size"], "recipe": run["recipe"], "seed": run["seed"], "step": run["step"]}
    try:
        info = api.model_info(run["repo"], revision=run["revision"], files_metadata=True)
        files = {f.rfilename: (f.size or 0) for f in (info.siblings or [])}
        weights = {n: s for n, s in files.items() if n.endswith(".safetensors")}
        row.update(commit=info.sha, weight_bytes=sum(weights.values()), weight_files=len(weights),
                   has_config="config.json" in files,
                   has_tokenizer=any("tokenizer" in n for n in files))
        row["ok"] = bool(weights) and row["has_config"] and row["has_tokenizer"]
        if not row["ok"]:
            row["error"] = f"missing pieces among {sorted(files)[:12]}"
    except Exception as error:  # noqa: BLE001
        row.update(ok=False, error=f"{type(error).__name__}: {error}")
    return row


with cf.ThreadPoolExecutor(max_workers=16) as pool:
    rows = list(pool.map(look, runs))
rows.sort(key=lambda r: (not r["ok"], r["run_key"]))
bad = [r for r in rows if not r["ok"]]
for r in bad:
    print(f"[fail] {r['run_key']} {r['repo']}@{r['revision']}: {r['error']}", flush=True)

by_size = {}
for r in rows:
    if r["ok"]:
        by_size.setdefault(r["size"], []).append(r["weight_bytes"])
summary = {s: {"runs": len(v), "weight_gb_median": round(sorted(v)[len(v) // 2] / 1e9, 3),
               "weight_gb_max": round(max(v) / 1e9, 3)} for s, v in sorted(by_size.items())}
distinct = len({(r["repo"], r.get("commit")) for r in rows if r["ok"]})
snapnew.write_json(W / "runs_verified.json",
                   {"runs": rows, "by_size": summary, "n_ok": len(rows) - len(bad), "n_failed": len(bad),
                    "distinct_repo_commits": distinct, "wall_seconds": time.time() - t0})
print(f"[done] {len(rows) - len(bad)} of {len(rows)} runs resolve, {distinct} distinct commits, "
      f"{time.time() - t0:.0f}s", flush=True)
for s, v in summary.items():
    print(f"[size] {s}: {v['runs']} runs, median {v['weight_gb_median']} GB, max {v['weight_gb_max']} GB", flush=True)
if bad:
    sys.exit(f"{len(bad)} runs do not resolve; see runs_verified.json")
