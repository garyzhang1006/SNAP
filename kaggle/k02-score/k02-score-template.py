"""k02 (2x T4): score DataDecide checkpoints on the frozen request file.

tools/make_shards.py turns this template into one kernel per shard by replacing
the SHARD line below. Nothing else differs between shards.

Each GPU runs one worker process. For each run a worker downloads the branch
(config, tokenizer, safetensors only) into /kaggle/tmp, scores the shard's tasks
with common/scorer.py, writes scores/<run_key>.npz, and deletes the checkpoint.
A worker won't start a run whose estimated time would cross the shard deadline,
so a slow session ends with finished runs saved and the rest listed in
shard_report.json under not_started, ready for a follow-up shard.

The kernel refuses to score unless config/frozen.json exists and its hash
matches the attached request file, so no model sees a request file that wasn't
pre-registered.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SHARD = None  # replaced by tools/make_shards.py

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402

assert SHARD is not None, "run tools/make_shards.py; the template itself is not a kernel"
tasks_cfg = snapnew.read_json(ROOT / "config" / "tasks.json")
frozen_path = ROOT / "config" / "frozen.json"
assert frozen_path.exists(), "config/frozen.json is missing; run tools/freeze.py on the k01 summary and re-push the code dataset"
frozen = snapnew.read_json(frozen_path)
req_path = snapnew.find_one("requests.jsonl.gz")
req_sha = snapnew.sha256(req_path)
assert req_sha == frozen["requests_sha256"], f"request file hash {req_sha} is not the frozen {frozen['requests_sha256']}"

pin = tasks_cfg["scoring"]["transformers_pin"]
assert pin, "config/tasks.json has no transformers_pin; run k00 and copy the version it reports"
# The Kaggle image ships transformers 5, which ai2-olmo 0.6.0's hf_olmo wrapper
# cannot load a checkpoint against; k00 measures which 4.x line works.
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", f"transformers=={pin}"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "ai2-olmo==0.6.0", "cached_path"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "omegaconf"])
print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv"],
                     capture_output=True, text=True).stdout, flush=True)

WORKER = r'''
import json, shutil, sys, time, traceback
from pathlib import Path
job = json.loads(Path(sys.argv[1]).read_text())
sys.path.insert(0, job["common"])
import numpy as np, torch, transformers, huggingface_hub
from huggingface_hub import HfApi, snapshot_download
import snapnew, scorer

requests = snapnew.select_tasks(snapnew.read_requests(job["requests"]), job["tasks"])
table = snapnew.choice_table(requests)
device = "cuda"
versions = {"torch": torch.__version__, "transformers": transformers.__version__,
            "huggingface_hub": huggingface_hub.__version__, "gpu": torch.cuda.get_device_name(0)}
print("[worker]", versions, f"{len(requests)} items", flush=True)
out_dir = Path(job["out"]); out_dir.mkdir(parents=True, exist_ok=True)
report = {"done": [], "failed": [], "not_started": [], "timing": {}}
for run in job["runs"]:
    key = run["run_key"]
    target = out_dir / f"{key}.npz"
    if target.exists():
        report["done"].append(key)
        continue
    if time.time() + 1.3 * job["est_seconds"].get(key, 0) > job["deadline_unix"]:
        report["not_started"].append(key)
        continue
    local = Path(job["tmp"]) / key
    try:
        t = time.time()
        sha = HfApi().model_info(run["repo"], revision=run["revision"]).sha
        snapshot_download(run["repo"], revision=run["revision"], local_dir=str(local),
                          allow_patterns=["*.json", "*.safetensors"])
        t_download = time.time() - t
        t = time.time()
        model, tok = scorer.load_model(str(local), job["scoring"]["dtype"], device)
        t_load = time.time() - t
        sums, stats = scorer.score_requests(model, tok, requests, job["scoring"], device,
                                            log=lambda m: print(m, flush=True))
        meta = dict(run, hub_sha=sha, tasks=job["tasks"], requests_sha256=job["requests_sha256"],
                    scoring=job["scoring"], versions=versions, stats=stats,
                    seconds_download=t_download, seconds_load=t_load)
        tmp_target = out_dir / f"{key}.partial.npz"
        np.savez_compressed(tmp_target, task_index=table["task_index"], doc_id=table["doc_id"],
                            choice=table["choice"], num_bytes=table["num_bytes"], sum_logits=sums,
                            meta=np.asarray(json.dumps(meta, default=str)))
        tmp_target.rename(target)
        report["done"].append(key)
        report["timing"][key] = {"download": t_download, "load": t_load, "score": stats["seconds_scoring"],
                                 "mode": stats["mode"], "check": stats["check_max_abs_diff_nats"]}
        print(f"[run] {key} {stats['mode']} score {stats['seconds_scoring']:.0f}s download {t_download:.0f}s "
              f"check {stats['check_max_abs_diff_nats']}", flush=True)
        del model
        torch.cuda.empty_cache()
    except Exception:
        report["failed"].append({"run_key": key, "error": traceback.format_exc()[-3000:]})
        print(f"[fail] {key}\n{traceback.format_exc()}", flush=True)
        torch.cuda.empty_cache()
    finally:
        shutil.rmtree(local, ignore_errors=True)
Path(job["report"]).write_text(json.dumps(report, indent=1))
'''
(TMP / "worker.py").write_text(WORKER)

# Balance the two GPUs by estimated seconds, largest runs first.
load = {"0": 0.0, "1": 0.0}
plans = {"0": [], "1": []}
for run in sorted(SHARD["runs"], key=lambda r: -SHARD["est_seconds"].get(r["run_key"], 0)):
    gpu = min(load, key=load.get)
    plans[gpu].append(run)
    load[gpu] += SHARD["est_seconds"].get(run["run_key"], 0)
print(f"[plan] {SHARD['name']}: {len(SHARD['runs'])} runs, estimated GPU seconds per card {load}", flush=True)

deadline = t0 + 3600 * SHARD["deadline_hours"]
procs = {}
for gpu, runs in plans.items():
    job = {"runs": runs, "tasks": SHARD["tasks"], "est_seconds": SHARD["est_seconds"], "deadline_unix": deadline,
           "common": str(ROOT / "common"), "requests": str(req_path), "requests_sha256": req_sha,
           "scoring": tasks_cfg["scoring"], "out": str(W / "scores"), "tmp": str(TMP / f"ckpt{gpu}"),
           "report": str(W / f"worker{gpu}_report.json")}
    (TMP / f"job{gpu}.json").write_text(json.dumps(job))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu, HF_HUB_DISABLE_PROGRESS_BARS="1",
               PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True", TOKENIZERS_PARALLELISM="false")
    log = open(W / f"worker{gpu}.log", "w")
    procs[gpu] = (subprocess.Popen([sys.executable, str(TMP / "worker.py"), str(TMP / f"job{gpu}.json")],
                                   env=env, stdout=log, stderr=subprocess.STDOUT), log)
codes = {}
for gpu, (p, log) in procs.items():
    codes[gpu] = p.wait()
    log.close()
    print(f"[worker {gpu}] exit {codes[gpu]}", flush=True)
    print((W / f"worker{gpu}.log").read_text()[-4000:], flush=True)

merged = {"shard": SHARD["name"], "exit_codes": codes, "done": [], "failed": [], "not_started": [], "timing": {},
          "requests_sha256": req_sha, "wall_seconds": None}
for gpu in plans:
    rp = W / f"worker{gpu}_report.json"
    if rp.exists():
        r = json.loads(rp.read_text())
        for k in ("done", "failed", "not_started"):
            merged[k] += r[k]
        merged["timing"].update(r["timing"])
        rp.unlink()
    else:
        merged["failed"] += [{"run_key": run["run_key"], "error": f"worker {gpu} crashed before writing a report"}
                             for run in plans[gpu] if not (W / "scores" / f"{run['run_key']}.npz").exists()]
merged["done"] = sorted(set(merged["done"]) | {p.name[:-4] for p in (W / "scores").glob("*.npz") if not p.name.endswith(".partial.npz")})
merged["wall_seconds"] = time.time() - t0
snapnew.write_json(W / "shard_report.json", merged)
for p in (W / "scores").glob("*.partial.npz"):
    p.unlink()
print(f"[done] {len(merged['done'])} scored, {len(merged['failed'])} failed, {len(merged['not_started'])} not started, "
      f"{merged['wall_seconds']:.0f}s", flush=True)
if merged["failed"] or len(merged["done"]) != len(SHARD["runs"]):
    sys.exit(f"shard incomplete: see shard_report.json")
