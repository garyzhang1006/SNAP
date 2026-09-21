"""Score one job (a run subset on one request bank) on every visible GPU.

  python score_runs.py --job verify --dry-run
  python score_runs.py --job pythia_bank1_final
  python score_runs.py --all                      # every job in config/jobs.json, in order

One worker process runs per GPU. A worker downloads the next checkpoint while
the current one scores, writes scores/<job>/<run_key>.npz choice by choice in
request-file order, and deletes the checkpoint. A run whose file exists is
skipped, so a rerun continues where the last one stopped. The job's requests
must hash to the value recorded in config/frozen.json, so no model sees a
request file that was not frozen first (run requests/freeze.py after building
the banks).

The score file holds task_index, doc_id, choice, num_bytes and sum_logits
aligned to the request file, plus a JSON meta string with the run row, the hub
commit, the scoring config, library versions, the scorer's mode check and the
timings. reduce.py turns it into the seednoise run format.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "common"))
import bank  # noqa: E402


def load_job(name):
    jobs = {j["name"]: j for j in bank.read_json(HERE / "config" / "jobs.json")["jobs"]}
    if name not in jobs:
        raise SystemExit(f"no job {name!r}; have {sorted(jobs)}")
    job = jobs[name]
    runs = bank.read_json(HERE / "config" / job["runs"])["runs"]
    for key, allowed in job.get("filter", {}).items():
        runs = [r for r in runs if r[key] in allowed]
    if not runs:
        raise SystemExit(f"job {name}: the filter {job.get('filter')} leaves no runs")
    return job, runs


def worker(job_path):
    """Runs in a subprocess with exactly one GPU visible."""
    import shutil
    import traceback
    from concurrent.futures import ThreadPoolExecutor

    import numpy as np
    import torch
    import transformers
    import huggingface_hub
    from huggingface_hub import HfApi, snapshot_download

    import scorer

    job = json.loads(Path(job_path).read_text())
    requests = bank.read_requests(job["requests"])
    if job["tasks"]:
        requests = bank.select_tasks(requests, job["tasks"])
    table = bank.choice_table(requests)
    device = "cuda"
    versions = {"torch": torch.__version__, "transformers": transformers.__version__,
                "huggingface_hub": huggingface_hub.__version__, "gpu": torch.cuda.get_device_name(0),
                "cuda": torch.version.cuda}
    print("[worker]", versions, f"{len(requests)} items", flush=True)
    out_dir = Path(job["out"])
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"done": [], "failed": [], "not_started": [], "timing": {}}

    def fetch(run, local):
        # Anonymous downloads in a long row meet the odd 429 or reset connection;
        # snapshot_download resumes the files it already has, so a retry is cheap.
        for attempt in range(5):
            try:
                sha = HfApi().model_info(run["repo"], revision=run["revision"]).sha
                snapshot_download(run["repo"], revision=run["revision"], local_dir=str(local),
                                  allow_patterns=run["allow_patterns"])
                return sha
            except Exception as e:
                if attempt == 4:
                    raise
                print(f"[retry] {run['run_key']} download try {attempt + 1} of 5: {type(e).__name__}: {e}", flush=True)
                time.sleep(60 * (attempt + 1))

    todo = [r for r in job["runs"] if not (out_dir / f"{r['run_key']}.npz").exists()]
    report["done"] = [r["run_key"] for r in job["runs"] if (out_dir / f"{r['run_key']}.npz").exists()]
    pool = ThreadPoolExecutor(max_workers=1)
    pending = {}

    def prefetch(i):
        if i < len(todo) and todo[i]["run_key"] not in pending:
            run = todo[i]
            local = Path(job["tmp"]) / run["run_key"]
            pending[run["run_key"]] = (pool.submit(fetch, run, local), local, time.time())

    prefetch(0)
    for i, run in enumerate(todo):
        key = run["run_key"]
        target = out_dir / f"{key}.npz"
        if job["deadline_unix"] and time.time() + 1.3 * job["est_seconds"].get(key, 0) > job["deadline_unix"]:
            report["not_started"].append(key)
            ent = pending.pop(key, None)
            if ent is not None:  # do not keep a checkpoint on disk for a run that will not be scored
                fut_skip, local_skip, _ = ent
                if not fut_skip.cancel():
                    try:
                        fut_skip.result()
                    except Exception:
                        pass
                shutil.rmtree(local_skip, ignore_errors=True)
            continue
        prefetch(i)  # a no-op unless the previous run was skipped by the deadline
        prefetch(i + 1)
        fut, local, t_start = pending.pop(key)
        model = None
        try:
            sha = fut.result()
            t_download = time.time() - t_start
            t = time.time()
            model = scorer.load_model(str(local), run["family"], job["scoring"]["dtype"], device)
            t_load = time.time() - t
            sums, stats = scorer.score_requests(model, requests, job["scoring"], device,
                                                log=lambda m: print(m, flush=True))
            meta = dict(run, hub_sha=sha, job=job["name"], bank=job["bank"], tasks=job["tasks"],
                        requests_sha256=job["requests_sha256"], scoring=job["scoring"], versions=versions,
                        stats=stats, seconds_download=t_download, seconds_load=t_load)
            tmp_target = out_dir / f"{key}.partial.npz"
            np.savez_compressed(tmp_target, task_index=table["task_index"], doc_id=table["doc_id"],
                                choice=table["choice"], num_bytes=table["num_bytes"], sum_logits=sums,
                                meta=np.asarray(json.dumps(meta, default=str)))
            tmp_target.rename(target)
            report["done"].append(key)
            report["timing"][key] = {"download": t_download, "load": t_load, "score": stats["seconds_scoring"],
                                     "mode": stats["mode"], "check": stats["check_max_abs_diff_nats"],
                                     "tokens": stats["tokens_total"], "size": run["size"], "family": run["family"]}
            print(f"[run] {key} {stats['mode']} score {stats['seconds_scoring']:.0f}s "
                  f"({stats['tokens_total'] / max(stats['seconds_scoring'], 1e-9):.0f} tok/s) download {t_download:.0f}s "
                  f"check {stats['check_max_abs_diff_nats']}", flush=True)
        except Exception:
            report["failed"].append({"run_key": key, "error": traceback.format_exc()[-3000:]})
            print(f"[fail] {key}\n{traceback.format_exc()}", flush=True)
        finally:
            # Drop the weights after a failure too, or the next run loads beside them.
            model = None
            torch.cuda.empty_cache()
            shutil.rmtree(local, ignore_errors=True)
        Path(job["report"]).write_text(json.dumps(report, indent=1))
    for key, (fut, local, _) in pending.items():
        try:
            fut.result()
        except Exception:
            pass
        shutil.rmtree(local, ignore_errors=True)
    pool.shutdown(wait=True)
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


def prior_estimates(out):
    """Median scoring seconds per (family, size) from this job's finished runs."""
    est = {}
    for rp in out.glob("timing_*.json"):
        for key, t in json.loads(rp.read_text()).items():
            est.setdefault((t["family"], t["size"]), []).append(t["download"] + t["load"] + t["score"])
    return {k: sorted(v)[len(v) // 2] for k, v in est.items()}


def run_job(name, args):
    t0 = time.time()
    job, runs = load_job(name)
    cfg = bank.read_json(HERE / "config" / "banks.json")
    frozen = bank.read_json(HERE / "config" / "frozen.json")
    req_path = HERE / "data" / f"{job['bank']}_requests.jsonl.gz"
    req_sha = bank.sha256(req_path)
    if req_sha != frozen["banks"][job["bank"]]["sha256"]:
        raise SystemExit(f"{req_path} hashes to {req_sha}, frozen is {frozen['banks'][job['bank']]['sha256']}; do not score")
    known = {r["task"] for r in bank.read_requests(req_path)}
    tasks = job.get("tasks") or []
    if not set(tasks) <= known:
        raise SystemExit(f"job tasks {tasks} not all in the request file {sorted(known)}")

    out = Path(args.out) / name
    todo = [r for r in runs if not (out / f"{r['run_key']}.npz").exists()]
    gpus = args.gpus.split(",") if args.gpus else visible_gpus()
    est = prior_estimates(out) if out.exists() else {}
    est_seconds = {r["run_key"]: est.get((r["family"], r["size"]), 0.0) for r in runs}
    known_hours = sum(est_seconds[r["run_key"]] for r in todo) / 3600
    print(f"[plan] job {name} on {job['bank']}: {len(runs)} runs, {len(todo)} still to score, "
          f"tasks {tasks or 'all'}, gpus {gpus or 'none visible'}, "
          f"{known_hours:.1f} card-hours by this job's own timings so far", flush=True)
    if args.dry_run:
        print("[dry-run] inputs valid; nothing scored")
        return True
    if not gpus:
        raise SystemExit("no GPU visible; pass --gpus")
    if not todo:
        print("[done] nothing to score")
        return True

    pin = cfg["scoring"]["transformers_pin"]
    import transformers  # noqa: E402  (setup.sh installs the pin; check rather than reinstall inside a job)
    if transformers.__version__ != pin:
        raise SystemExit(f"transformers {transformers.__version__} installed, pin is {pin}; rerun setup.sh")
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv"],
                         capture_output=True, text=True).stdout, flush=True)

    # Balance the GPUs by estimated seconds, largest runs first; with no
    # timings yet, by parameter count through the size string.
    def params(r):
        s = r["size"].lower()
        return float(s[:-1]) * (1e9 if s.endswith("b") else 1e6)

    # Seconds and parameter counts never mix in one sort: timings are used
    # only when every run to do has one, else the count stands in for all.
    use_est = all(est_seconds[r["run_key"]] > 0 for r in todo)

    def weight(r):
        return est_seconds[r["run_key"]] if use_est else params(r)

    load = {g: 0.0 for g in gpus}
    plans = {g: [] for g in gpus}
    for run in sorted(todo, key=lambda r: -weight(r)):
        g = min(load, key=load.get)
        plans[g].append(run)
        load[g] += weight(run)
    deadline = t0 + 3600 * args.deadline_hours if args.deadline_hours else 0
    procs = {}
    for g, plan in plans.items():
        if not plan:
            continue
        spec = {"name": name, "bank": job["bank"], "runs": plan, "tasks": tasks, "est_seconds": est_seconds,
                "deadline_unix": deadline, "requests": str(req_path), "requests_sha256": req_sha,
                "scoring": cfg["scoring"], "out": str(out), "tmp": str(tmp / f"ckpt{g}"),
                "report": str(out / f"worker{g}.json")}
        jp = tmp / f"job{g}_{name}.json"
        jp.write_text(json.dumps(spec))
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, HF_HUB_DISABLE_PROGRESS_BARS="1",
                   PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True", TOKENIZERS_PARALLELISM="false")
        log = open(out / f"worker{g}.log", "a")
        procs[g] = (subprocess.Popen([sys.executable, str(HERE / "score_runs.py"), "--worker", str(jp)],
                                     env=env, stdout=log, stderr=subprocess.STDOUT), log)
    codes = {}
    for g, (p, log) in procs.items():
        codes[g] = p.wait()
        log.close()
        print(f"[worker {g}] exit {codes[g]}", flush=True)

    merged = {"job": name, "bank": job["bank"], "exit_codes": codes, "done": [], "failed": [], "not_started": [],
              "timing": {}, "requests_sha256": req_sha, "wall_seconds": None}
    for g in plans:
        rp = out / f"worker{g}.json"
        if rp.exists():
            r = json.loads(rp.read_text())
            for k in ("failed", "not_started"):
                merged[k] += r[k]
            merged["timing"].update(r["timing"])
            rp.unlink()
        elif plans[g]:
            merged["failed"] += [{"run_key": run["run_key"], "error": f"worker {g} crashed before writing a report"}
                                 for run in plans[g] if not (out / f"{run['run_key']}.npz").exists()]
    merged["done"] = sorted({r["run_key"] for r in runs if (out / f"{r['run_key']}.npz").exists()})
    merged["wall_seconds"] = time.time() - t0
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime(t0))
    bank.write_json(out / f"timing_{stamp}.json", merged["timing"])
    bank.write_json(out / f"report_{stamp}.json", merged)
    for r in runs:
        (out / f"{r['run_key']}.partial.npz").unlink(missing_ok=True)
    print(f"[done] job {name}: {len(merged['done'])} of {len(runs)} scored, {len(merged['failed'])} failed, "
          f"{len(merged['not_started'])} not started, {merged['wall_seconds']:.0f}s", flush=True)
    return not merged["failed"] and len(merged["done"]) == len(runs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", help="a job name from config/jobs.json")
    ap.add_argument("--all", action="store_true", help="every job in order; stops at the first incomplete one")
    ap.add_argument("--out", default=os.environ.get("SNAP2_SCORES", str(HERE / "scores")))
    ap.add_argument("--tmp", default=os.environ.get("SNAP2_TMP", str(HERE / "tmp")))
    ap.add_argument("--deadline-hours", type=float, default=None, help="wall-clock budget from now; default none")
    ap.add_argument("--gpus", default=None, help="comma-separated GPU ids; default every visible GPU")
    ap.add_argument("--dry-run", action="store_true", help="validate inputs and print the plan; no torch, no downloads")
    ap.add_argument("--worker", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return
    if not args.job and not args.all:
        ap.error("pass --job NAME or --all")
    names = [args.job] if args.job else [j["name"] for j in bank.read_json(HERE / "config" / "jobs.json")["jobs"]]
    for name in names:
        ok = run_job(name, args)
        if not ok:
            sys.exit(f"job {name} incomplete: see scores/{name}/report_*.json, then rerun the same command")


if __name__ == "__main__":
    main()
