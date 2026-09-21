"""R0 reconciliation: build snap-scores-v1 from the reduced runs and run C00, C02, C01."""
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
subprocess.call(["df", "-h", "/kaggle/working"])
W = Path("/kaggle/working")


def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


def locate(tarball, marker):
    """Kaggle may unpack an uploaded tarball; accept either the archive or the tree."""
    dirs = [p.parent for p in Path("/kaggle/input").rglob(marker) if not p.name.startswith("._")]
    if dirs:
        return dirs[0]
    with tarfile.open(find(tarball)) as tf:
        tf.extractall(W)
    hit = [p.parent for p in W.rglob(marker)]
    assert hit, f"{marker} missing after extracting {tarball}"
    return hit[0]


src_pkg = locate("snap_compute.tar.gz", "run_two_gpus.py")
shutil.copytree(src_pkg, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
assert (PKG / "run.py").is_file()
src_sn = locate("seednoise_src.tar.gz", "pyproject.toml")
shutil.copytree(src_sn, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
shutil.copy(find("snap_adapter.py"), W / "snap_adapter.py")

runs = W / "runs"
runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._"):
        continue
    shutil.copy(p, runs / p.name)
    n += 1
print(f"[runs] {n} reduced runs at {time.time() - t0:.0f}s", flush=True)
if n != 375:
    sys.exit(f"expected 375 reduced runs, found {n}")

data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data)])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_job(job, cfg, out):
    cfg_path = W / "configs" / f"{job}_{out}.json"
    cfg_path.parent.mkdir(exist_ok=True)
    cfg = {**cfg, "template_only": False}
    cfg_path.write_text(json.dumps(cfg, indent=2))
    t1 = time.time()
    subprocess.check_call([sys.executable, str(PKG / "runs" / f"{job}.py"), "--config", str(cfg_path),
                           "--out", str(W / "SNAP" / out)])
    print(f"[{job}] {out} finished in {time.time() - t1:.0f}s", flush=True)
    return json.load(open(W / "SNAP" / out / "result.json"))


run_job("C02", {"seed": 20260914}, "C02_tests")
print((W / "SNAP" / "C02_tests" / "tests.txt").read_text()[-3000:], flush=True)
for phen in ("margin", "accuracy"):
    ds = str(data / phen / "scores.json")
    r0 = run_job("C00", {"seed": 20260914, "inputs": [ds, str(data / phen / "scores.npz")], "dataset": ds}, f"C00_{phen}")
    print(json.dumps({k: r0[k] for k in ("versions", "dataset", "missing")}, indent=1), flush=True)
    r1 = run_job("C01", {"seed": 20260914, "dataset": ds, "split_mode": "original", "bootstrap_draws": 4999},
                 f"C01_{phen}_original")
    print(phen, "original split:", json.dumps({k: r1[k] for k in ("lambda", "lambda_squared", "T", "U", "aggregate_sd",
                                                                    "negative_diagonal_count", "status")}, indent=1),
          "interval:", r1["uncertainty"]["interval"], "invalid:", r1["uncertainty"]["invalid_draws"], flush=True)
    r2 = run_job("C01", {"seed": 20260914, "dataset": ds, "split_mode": "item", "bootstrap_draws": 4999},
                 f"C01_{phen}_item_seed20260914")
    print(phen, "new item split:", r2["lambda"], r2["uncertainty"]["interval"], flush=True)
json.dump({"seconds_total": time.time() - t0}, open(W / "timing.json", "w"))
shutil.rmtree(runs, ignore_errors=True)
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
