"""R0 baseline: install the original seednoise package, self-test, and rerun the primary analysis."""
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
subprocess.call(["df", "-h", "/kaggle/working"])
subprocess.call(["nproc"])
subprocess.call(["free", "-g"])

hits = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and "._" not in p.name]
if not hits:
    sys.exit("seed-noise source not found under /kaggle/input")
src = hits[0].parent
print("[env] source at", src, flush=True)
shutil.copytree(src, "/kaggle/working/seed-noise")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "/kaggle/working/seed-noise[hub]"])
head = (src / ".git" / "HEAD")
print("[env] git HEAD present:", head.exists(), flush=True)
subprocess.check_call([sys.executable, "-m", "pip", "freeze"], stdout=open("/kaggle/working/pip_freeze.txt", "w"))

runs = Path("/kaggle/working/runs")
runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._"):
        continue
    shutil.copy(p, runs / p.name)
    n += 1
print(f"[runs] {n} reduced runs gathered at {time.time() - t0:.0f}s", flush=True)
if n != 375:
    sys.exit(f"expected 375 reduced runs, found {n}")

subprocess.check_call(["seednoise", "selftest", "--out", "/kaggle/working/selftest"])
print(f"[selftest] done at {time.time() - t0:.0f}s", flush=True)

out = "/kaggle/working/results"
t1 = time.time()
subprocess.check_call(["seednoise", "analyze", "--runs", str(runs), "--out", out,
                       "--n-boot", "4999", "--skip-nulls", "--quiet"])
print(f"[analyze] done in {time.time() - t1:.0f}s", flush=True)
for name in ("tab_primary.csv", "tab_gates.csv", "tab_reliability.csv"):
    p = Path(out) / name
    if p.exists():
        print(f"\n===== {name}\n{p.read_text()}", flush=True)
json.dump({"seconds_total": time.time() - t0, "seconds_analyze": time.time() - t1, "runs": n},
          open("/kaggle/working/timing.json", "w"))
shutil.rmtree("/kaggle/working/seed-noise", ignore_errors=True)
shutil.rmtree(runs, ignore_errors=True)
