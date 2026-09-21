"""R6 interval calibration, cell set a."""
import json, platform, shutil, subprocess, sys, tarfile, time
from pathlib import Path
t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
subprocess.call(["nproc"])
W = Path("/kaggle/working")
def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]
src = find("pyproject.toml").parent
shutil.copytree(src, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
shutil.copy(find("r6_calibration.py"), W / "r6_calibration.py")
CELLS = [{"name": "null_margin_noise", "rho": 0.0, "noise_sd": 0.73}, {"name": "null_accuracy_noise", "rho": 0.0, "noise_sd": 1.45}, {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73}, {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45}, {"name": "margin_like_boolq_trace", "rho": 0.061, "noise_sd": 0.73, "trait_scales": [4.373213921133976, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, {"name": "accuracy_like_boolq_trace", "rho": 0.018, "noise_sd": 1.45, "trait_scales": [6.873863542433759, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}]
(W / "cells.json").write_text(json.dumps(CELLS, indent=1))
subprocess.check_call([sys.executable, str(W / "r6_calibration.py"), "--out", str(W / "r6_a"), "--cells", str(W / "cells.json"),
                       "--reps", "2000", "--draws", "4999", "--seed", "20260915"])
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
