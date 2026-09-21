"""R8 and R9: C07 covariance prediction comparison and C08 paired decision arithmetic, both phenotypes."""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


shutil.copytree(find("run_two_gpus.py").parent, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
shutil.copytree(find("pyproject.toml").parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
for f in ("snap_adapter.py", "r9_pairs.py"):
    shutil.copy(find(f), W / f)
runs = W / "runs"; runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._") or "moments" in p.name or "scores" in p.name:
        continue
    shutil.copy(p, runs / p.name); n += 1
assert n == 375, n
data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "full")])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_job(job, cfg, out):
    cfg_path = W / "configs" / f"{out}.json"; cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps({**cfg, "template_only": False}, indent=2))
    t1 = time.time()
    subprocess.check_call([sys.executable, str(PKG / "runs" / f"{job}.py"), "--config", str(cfg_path), "--out", str(W / "SNAP" / out)])
    print(f"[{job}] {out} in {time.time() - t1:.0f}s", flush=True)
    return json.load(open(W / "SNAP" / out / "result.json"))


SEED = 20260914
for phen in ("margin", "accuracy"):
    ds = str(data / "full" / phen / "scores.json")
    run_job("C01", {"seed": SEED, "dataset": ds, "split_mode": "original", "bootstrap_draws": 0}, f"C01_{phen}")
    r = run_job("C07", {"seed": SEED, "dataset": ds, "split_mode": "original", "bootstrap_draws": 0, "folds": 5,
                        "prediction_bootstrap_draws": 2000}, f"C07_{phen}")
    print(phen, "C07", json.dumps({k: v for k, v in r.items() if k not in ("per_configuration", "rows", "predictions")})[:3000], flush=True)
    pairs = W / "SNAP" / f"pairs_{phen}.json"
    subprocess.check_call([sys.executable, str(W / "r9_pairs.py"), "--c01", str(W / "SNAP" / f"C01_{phen}"), "--dataset", ds, "--out", str(pairs)])
    r = run_job("C08", {"seed": SEED, "pairs": str(pairs)}, f"C08_{phen}")
    rows = r["pairs"]
    print(phen, "C08", len(rows), "keys", list(rows[0].keys()), flush=True)
shutil.rmtree(runs, ignore_errors=True); shutil.rmtree(W / "seed-noise", ignore_errors=True)
for phen in ("margin", "accuracy"):
    (data / "full" / phen / "scores.npz").unlink(missing_ok=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
