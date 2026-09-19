"""Score one shard of DataDecide checkpoints on the frozen held-out request file.

Cluster version of heldout/kaggle/k02-score/k02-score-template.py. Same scorer,
same request file, same output format, so the score files feed
heldout/kaggle/k04-analyze-heldout unchanged. Nothing here reads /kaggle.

  python score_shard.py --shard shards/s01.json --dry-run
  python score_shard.py --shard shards/s01.json --out $SNAPX_ROOT/scores --tmp $TMPDIR --deadline-hours 23

One worker process runs per visible GPU. For each run a worker downloads the
branch (config, tokenizer, safetensors only) into --tmp, scores the shard's
tasks with common/scorer.py, writes <out>/<run_key>.npz, and deletes the
checkpoint. A run whose file already exists is skipped, so a resubmitted job
continues where the last one stopped. A worker won't start a run whose
estimated time would cross the deadline; such runs are listed under
not_started in shard_report_<shard>.json and the job exits nonzero, which is
the signal to resubmit.

The script refuses to score unless config/frozen.json matches the request file
hash, so no model sees a request file that wasn't pre-registered.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "common"))
import snapnew  # noqa: E402


def worker(job_path):
    """Runs in a subprocess with exactly one GPU visible."""
    import shutil
    import traceback

    import numpy as np
    import torch
    import transformers
    import huggingface_hub
    from huggingface_hub import HfApi, snapshot_download

    import scorer

    job = json.loads(Path(job_path).read_text())
    requests = snapnew.select_tasks(snapnew.read_requests(job["requests"]), job["tasks"])
    table = snapnew.choice_table(requests)
    device = "cuda"
    versions = {"torch": torch.__version__, "transformers": transformers.__version__,
                "huggingface_hub": huggingface_hub.__version__, "gpu": torch.cuda.get_device_name(0)}
    print("[worker]", versions, f"{len(requests)} items", flush=True)
    out_dir = Path(job["out"])
    out_dir.mkdir(parents=True, exist_ok=True)
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


def visible_gpus():
    env = os.environ.get("CUDA_VISIBLE_DEVICES")
    if env:
        return [g.strip() for g in env.split(",") if g.strip()]
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"],
                             capture_output=True, text=True, check=True).stdout
        return [line.strip() for line in out.splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError):
        return []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shard", required=True, help="a JSON file under shards/")
    ap.add_argument("--out", default=os.environ.get("SNAPX_SCORES", str(HERE / "scores")),
                    help="directory for <run_key>.npz; shared across shards")
    ap.add_argument("--tmp", default=os.environ.get("TMPDIR", str(HERE / "tmp")),
                    help="node-local scratch for checkpoints, deleted run by run")
    ap.add_argument("--deadline-hours", type=float, default=None,
                    help="wall-clock budget from now; defaults to the shard's deadline_hours")
    ap.add_argument("--gpus", default=None, help="comma-separated GPU ids; default is every visible GPU")
    ap.add_argument("--dry-run", action="store_true", help="validate inputs and print the plan; no torch, no downloads")
    ap.add_argument("--worker", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return

    t0 = time.time()
    shard = snapnew.read_json(args.shard)
    tasks_cfg = snapnew.read_json(HERE / "config" / "tasks.json")
    frozen = snapnew.read_json(HERE / "config" / "frozen.json")
    req_path = HERE / "data" / "requests.jsonl.gz"
    req_sha = snapnew.sha256(req_path)
    assert req_sha == frozen["requests_sha256"], \
        f"data/requests.jsonl.gz hashes to {req_sha}, frozen is {frozen['requests_sha256']}; do not score"
    runs_cfg = {r["run_key"]: r for r in snapnew.read_json(HERE / "config" / "runs.json")["runs"]}
    for r in shard["runs"]:
        assert runs_cfg[r["run_key"]] == r, f"{r['run_key']} in the shard differs from config/runs.json"
    known = {r["task"] for r in snapnew.read_requests(req_path)}
    assert set(shard["tasks"]) <= known, f"shard tasks {shard['tasks']} not all in the request file {sorted(known)}"

    out = Path(args.out)
    todo = [r for r in shard["runs"] if not (out / f"{r['run_key']}.npz").exists()]
    hours = sum(shard["est_seconds"].get(r["run_key"], 0) for r in todo) / 3600
    deadline_hours = args.deadline_hours if args.deadline_hours is not None else shard["deadline_hours"]
    gpus = args.gpus.split(",") if args.gpus else visible_gpus()
    print(f"[plan] shard {shard['name']}: {len(shard['runs'])} runs, {len(todo)} still to score on tasks {shard['tasks']}, "
          f"about {hours:.1f} T4 card-hours of estimate left, deadline {deadline_hours} h, gpus {gpus or 'none visible'}", flush=True)
    if args.dry_run:
        print("[dry-run] inputs valid; nothing scored")
        return
    assert gpus, "no GPU visible; run inside a GPU job or pass --gpus"

    pin = tasks_cfg["scoring"]["transformers_pin"]
    import transformers  # noqa: E402  (setup.sh installs the pin; check rather than reinstall inside a job)
    assert transformers.__version__ == pin, f"transformers {transformers.__version__} installed, pin is {pin}; rerun setup.sh"
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv"],
                         capture_output=True, text=True).stdout, flush=True)

    # Balance the GPUs by estimated seconds, largest runs first.
    load = {g: 0.0 for g in gpus}
    plans = {g: [] for g in gpus}
    for run in sorted(todo, key=lambda r: -shard["est_seconds"].get(r["run_key"], 0)):
        g = min(load, key=load.get)
        plans[g].append(run)
        load[g] += shard["est_seconds"].get(run["run_key"], 0)
    deadline = t0 + 3600 * deadline_hours
    procs = {}
    for g, runs in plans.items():
        job = {"runs": runs, "tasks": shard["tasks"], "est_seconds": shard["est_seconds"], "deadline_unix": deadline,
               "requests": str(req_path), "requests_sha256": req_sha, "scoring": tasks_cfg["scoring"],
               "out": str(out), "tmp": str(tmp / f"ckpt{g}"), "report": str(out / f"worker{g}_{shard['name']}.json")}
        jp = tmp / f"job{g}_{shard['name']}.json"
        jp.write_text(json.dumps(job))
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, HF_HUB_DISABLE_PROGRESS_BARS="1",
                   PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True", TOKENIZERS_PARALLELISM="false")
        log = open(out / f"worker{g}_{shard['name']}.log", "a")
        procs[g] = (subprocess.Popen([sys.executable, str(HERE / "score_shard.py"), "--shard", args.shard,
                                      "--worker", str(jp)], env=env, stdout=log, stderr=subprocess.STDOUT), log)
    codes = {}
    for g, (p, log) in procs.items():
        codes[g] = p.wait()
        log.close()
        print(f"[worker {g}] exit {codes[g]}", flush=True)

    merged = {"shard": shard["name"], "exit_codes": codes, "done": [], "failed": [], "not_started": [], "timing": {},
              "requests_sha256": req_sha, "wall_seconds": None}
    for g in plans:
        rp = out / f"worker{g}_{shard['name']}.json"
        if rp.exists():
            r = json.loads(rp.read_text())
            for k in ("done", "failed", "not_started"):
                merged[k] += r[k]
            merged["timing"].update(r["timing"])
            rp.unlink()
        else:
            merged["failed"] += [{"run_key": run["run_key"], "error": f"worker {g} crashed before writing a report"}
                                 for run in plans[g] if not (out / f"{run['run_key']}.npz").exists()]
    merged["done"] = sorted({r["run_key"] for r in shard["runs"] if (out / f"{r['run_key']}.npz").exists()})
    merged["wall_seconds"] = time.time() - t0
    snapnew.write_json(out / f"shard_report_{shard['name']}.json", merged)
    for p in out.glob("*.partial.npz"):
        p.unlink()
    print(f"[done] {len(merged['done'])} of {len(shard['runs'])} scored, {len(merged['failed'])} failed, "
          f"{len(merged['not_started'])} not started, {merged['wall_seconds']:.0f}s", flush=True)
    if merged["failed"] or len(merged["done"]) != len(shard["runs"]):
        sys.exit(f"shard {shard['name']} incomplete: see shard_report_{shard['name']}.json, then resubmit the same shard")


if __name__ == "__main__":
    main()
