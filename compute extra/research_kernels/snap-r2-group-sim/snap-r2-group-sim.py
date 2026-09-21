"""R2 simulation of item versus passage-group splitting with the observed BoolQ group-size histogram."""
import json, shutil, subprocess, sys, time
from pathlib import Path
t0 = time.time()
W = Path("/kaggle/working")
def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]
hist = json.load(open(find("requests_audit_report.json")))["boolq"]["group_size_histogram"]
(W / "hist.json").write_text(json.dumps(hist))
shutil.copy(find("r2_group_sim.py"), W / "r2_group_sim.py")
subprocess.check_call([sys.executable, str(W / "r2_group_sim.py"), "--out", str(W / "r2sim"), "--histogram", str(W / "hist.json"),
                       "--reps", "500", "--seed", "20260915"])
print(f"[done] {time.time() - t0:.0f}s", flush=True)
