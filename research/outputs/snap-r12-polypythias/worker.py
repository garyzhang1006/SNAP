
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
