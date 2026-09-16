"""R12: rescore PolyPythias with the original seednoise arm-2 scorer on two T4s.

Reproduces the REPORTED transport inputs and the adjacent-checkpoint check with
the source pipeline's own code (seednoise git 5a59526, polypythias.run_arm2,
fp16 on CUDA, 6,000-token batch cap, nested item subsample):
  GPU 0: arm 2 at 70m and 160m, 500 items per task, step143000 (18 runs),
         then 160m at step143000 and step142000, 200 items per task on the nine
         non-MMLU traits (18 runs, the adjacent-checkpoint sample)
  GPU 1: arm 2 at 410m, then the 14m and 31m extension, 500 items per task,
         step143000 (27 runs)
Each run is saved as soon as it is scored, so a timeout keeps finished runs.
The seednoise size whitelist is widened to include 14m and 31m, which the
manuscript's extension used; model ids stay EleutherAI/pythia-{size}-seed{seed}.
"""
import json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

t0 = time.time()
W = Path("/kaggle/working")
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv"], capture_output=True, text=True).stdout, flush=True)

WORKER = r'''
import json, sys, time
from pathlib import Path
import torch, transformers
import seednoise.data.polypythias as pp
pp.SIZES = ("14m", "31m", "70m", "160m", "410m")
jobs = json.loads(sys.argv[1])
print("[worker] torch", torch.__version__, "transformers", transformers.__version__, torch.cuda.get_device_name(0), flush=True)
for job in jobs:
    t = time.time()
    out = Path(job["out"])
    res = pp.run_arm2(out, sizes=job["sizes"], seeds=list(pp.SEEDS), n_per_task=job["n"], revision=job["revision"],
                      max_tokens=6000, tasks=job.get("tasks"), device="cuda", progress=True)
    (out / f"manifest_{'_'.join(job['sizes'])}_{job['revision']}.json").write_text(json.dumps(res, indent=1, default=str))
    print(f"[job] {job['sizes']} {job['revision']} n={job['n']} items={res['n_items']} in {time.time()-t:.0f}s", flush=True)
'''
(W / "worker.py").write_text(WORKER)
NON_MMLU = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "openbookqa", "piqa", "socialiqa", "winogrande"]
plans = {
    "0": [{"sizes": ["70m"], "n": 500, "revision": "step143000", "out": str(W / "runs-arm2")},
          {"sizes": ["160m"], "n": 500, "revision": "step143000", "out": str(W / "runs-arm2")},
          {"sizes": ["160m"], "n": 200, "revision": "step143000", "tasks": NON_MMLU, "out": str(W / "runs-adjacent" / "step143000")},
          {"sizes": ["160m"], "n": 200, "revision": "step142000", "tasks": NON_MMLU, "out": str(W / "runs-adjacent" / "step142000")}],
    "1": [{"sizes": ["410m"], "n": 500, "revision": "step143000", "out": str(W / "runs-arm2")},
          {"sizes": ["14m"], "n": 500, "revision": "step143000", "out": str(W / "runs-arm2")},
          {"sizes": ["31m"], "n": 500, "revision": "step143000", "out": str(W / "runs-arm2")}],
}
procs = {}
for gpu, jobs in plans.items():
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu, HF_HUB_DISABLE_PROGRESS_BARS="1", PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
    log = open(W / f"worker{gpu}.log", "w")
    procs[gpu] = (subprocess.Popen([sys.executable, str(W / "worker.py"), json.dumps(jobs)], env=env, stdout=log, stderr=subprocess.STDOUT), log)
codes = {}
for gpu, (p, log) in procs.items():
    codes[gpu] = p.wait(); log.close()
    print(f"[worker {gpu}] exit {codes[gpu]}", flush=True)
    print((W / f"worker{gpu}.log").read_text()[-4000:], flush=True)
runs = sorted(str(p.relative_to(W)) for p in W.rglob("*.npz"))
print(f"[runs] {len(runs)} saved", flush=True)
(W / "r12_inventory.json").write_text(json.dumps({"exit_codes": codes, "runs": runs, "wall_seconds": time.time() - t0}, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
if any(codes.values()) or len(runs) != 63:
    sys.exit(f"incomplete: exit codes {codes}, {len(runs)} of 63 runs")
print(f"[done] {time.time() - t0:.0f}s", flush=True)
