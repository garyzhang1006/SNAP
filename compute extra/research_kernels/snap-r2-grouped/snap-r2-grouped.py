"""R2 empirical comparisons on the matched 37,682-item universe: original, new item, passage-group, and no-BoolQ."""
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
for f in ("snap_adapter.py", "snap_intervals.py"):
    shutil.copy(find(f), W / f)
groups_path = find("boolq_groups_from_requests.json")
report = json.load(open(find("requests_audit_report.json")))
b = report["boolq"]
assert b["items"] == 3270 and b["passage_mismatches"] == 0, f"BoolQ passage join not clean: {b}"
print("[groups] BoolQ", b, flush=True)

runs = W / "runs"; runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._") or "moments" in p.name or "scores" in p.name:
        continue
    shutil.copy(p, runs / p.name); n += 1
assert n == 375, n
data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "full"), "--groups", str(groups_path)])
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "noboolq"), "--exclude", "boolq"])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_job(job, cfg, out):
    cfg_path = W / "configs" / f"{out}.json"; cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps({**cfg, "template_only": False}, indent=2))
    t1 = time.time()
    subprocess.check_call([sys.executable, str(PKG / "runs" / f"{job}.py"), "--config", str(cfg_path), "--out", str(W / "SNAP" / out)])
    print(f"[{job}] {out} in {time.time() - t1:.0f}s", flush=True)
    return json.load(open(W / "SNAP" / out / "result.json"))


def intervals(out, ds):
    subprocess.check_call([sys.executable, str(W / "snap_intervals.py"), "--c01", str(W / "SNAP" / out), "--dataset", ds,
                           "--out", str(W / "SNAP" / out / "original_intervals.json")])


SEED = 20260914
for phen in ("margin", "accuracy"):
    full = str(data / "full" / phen / "scores.json"); nob = str(data / "noboolq" / phen / "scores.json")
    for mode in ("original", "item", "group"):
        name = f"C01_{phen}_{mode}"
        r = run_job("C01", {"seed": SEED, "dataset": full, "split_mode": mode, "bootstrap_draws": 4999}, name)
        print(phen, mode, "lambda", r["lambda"], "recipe-pct", r["uncertainty"]["interval"], flush=True)
        intervals(name, full)
    r = run_job("C01", {"seed": SEED, "dataset": nob, "split_mode": "original", "bootstrap_draws": 4999}, f"C01_{phen}_noboolq_original")
    print(phen, "no BoolQ original", r["lambda"], r["uncertainty"]["interval"], flush=True)
    intervals(f"C01_{phen}_noboolq_original", nob)
    run_job("C03", {"seed": SEED, "dataset": full, "splits": 50}, f"C03_{phen}")
    gain = [0.01, 0.02, 0.03, 0.042, 0.05, 0.10] if phen == "margin" else []
    run_job("C09", {"seed": SEED, "dataset": full, "gain_sd": gain}, f"C09_{phen}")
shutil.rmtree(runs, ignore_errors=True); shutil.rmtree(W / "seed-noise", ignore_errors=True)
for d in (data / "full", data / "noboolq"):
    for phen in ("margin", "accuracy"):
        (d / phen / "scores.npz").unlink(missing_ok=True)   # keep outputs small; manifests stay
print(f"[done] {time.time() - t0:.0f}s", flush=True)
