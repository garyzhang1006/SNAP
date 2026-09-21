"""R10: score-scale interventions on the same saved margins, items and runs held fixed.

Design fixed before any output was opened (2026-09-15 16:45 EDT). The adapter
builds the original margin dataset from the 375 shipped runs. For each benchmark
j, s_j is the pooled standard deviation of per-item margins across all
configurations, runs, and items (a scale fixed by the data, not by any estimate).
Transformations applied item by item before C01 in split mode "original":
  identity           must reproduce the shipped margin estimate
  global_x10         construction check, Lambda must not change
  standardised       m / s_j, a linear per-benchmark rescaling (changes weights)
  winsorised         clip(m, -s_j, s_j) / s_j
  tanh               tanh(m / s_j), a bounded saturating score
  tanh_half          tanh(2 m / s_j), stronger saturation
  sign               sign(m), which differs from accuracy only at zero margins
Each result gets the original wild, cluster-t, and configuration intervals.
These are scoring-scale interventions, not training-mechanism tests.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find_all(name):
    return sorted(p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._"))


def find(name):
    hits = find_all(name)
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


shutil.copytree(find("run_two_gpus.py").parent, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
src = [p for p in find_all("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
for f in ("snap_adapter.py", "snap_intervals.py"):
    shutil.copy(find(f), W / f)

sel = [p for p in find_all("*.npz") if "__seed-" in p.name]
assert len(sel) == 375, len(sel)
runs = W / "runs"; runs.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs / p.name)
data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "base")])
base = data / "base" / "margin"
meta = json.load(open(base / "scores.json"))
z = dict(np.load(base / "scores.npz"))
scale = {b["key"]: float(np.std(z[b["key"]])) for b in meta["benchmarks"]}
print("[scale]", json.dumps({b["name"]: scale[b["key"]] for b in meta["benchmarks"]}), flush=True)

TRANSFORMS = {
    "identity": lambda x, s: x,
    "global_x10": lambda x, s: 10.0 * x,
    "standardised": lambda x, s: x / s,
    "winsorised": lambda x, s: np.clip(x, -s, s) / s,
    "tanh": lambda x, s: np.tanh(x / s),
    "tanh_half": lambda x, s: np.tanh(2.0 * x / s),
    "sign": lambda x, s: np.sign(x),
}


def sha256(path):
    import hashlib
    h = hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()


def run_c01(ds, out):
    cfg = W / "configs" / f"{out}.json"; cfg.parent.mkdir(exist_ok=True)
    cfg.write_text(json.dumps({"seed": 20260914, "dataset": str(ds), "split_mode": "original", "bootstrap_draws": 4999, "template_only": False}, indent=2))
    subprocess.check_call([sys.executable, str(PKG / "runs" / "C01.py"), "--config", str(cfg), "--out", str(W / "SNAP" / out)])
    subprocess.check_call([sys.executable, str(W / "snap_intervals.py"), "--c01", str(W / "SNAP" / out), "--dataset", str(ds),
                           "--out", str(W / "SNAP" / out / "original_intervals.json")])
    return json.load(open(W / "SNAP" / out / "original_intervals.json"))


results = {"scale_pooled_item_sd": {b["name"]: scale[b["key"]] for b in meta["benchmarks"]}, "transforms": {}}
for name, fn in TRANSFORMS.items():
    d = data / name; d.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(d / "scores.npz", **{k: fn(v, scale[k]) for k, v in z.items()})
    m = dict(meta); m["arrays_sha256"] = sha256(d / "scores.npz"); m["transform"] = name
    (d / "scores.json").write_text(json.dumps(m, indent=1, sort_keys=True))
    iv = run_c01(d / "scores.json", f"C01_margin_{name}")
    results["transforms"][name] = iv
    print(f"[{name}] lambda {iv['lambda']:.5f} wild {iv['wild']} trace_shares {json.dumps(iv['trace_shares'])}", flush=True)
lam = {k: v["lambda"] for k, v in results["transforms"].items()}
assert abs(lam["identity"] - 1.243949911719114) < 1e-6, lam["identity"]
assert abs(lam["global_x10"] - lam["identity"]) < 1e-9, lam
results["wall_seconds"] = time.time() - t0
(W / "r10_scale_transform.json").write_text(json.dumps(results, indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
for d in ("seed-noise", "runs", "datasets"):
    shutil.rmtree(W / d, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
