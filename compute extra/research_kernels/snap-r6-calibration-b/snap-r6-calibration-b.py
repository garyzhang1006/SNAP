"""R6 interval calibration, cell set b."""
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
CELLS = [{"name": "margin_like_recipe_shared", "rho": 0.061, "noise_sd": 0.73, "recipe_shared": 0.5}, {"name": "margin_like_heavy_tails", "rho": 0.061, "noise_sd": 0.73, "student_df": 4}, {"name": "margin_like_one_dominant_recipe", "rho": 0.061, "noise_sd": 0.73, "recipe_variance_scales": [6.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, {"name": "margin_like_cross_half_error_corr_0.1", "rho": 0.061, "noise_sd": 0.73, "cross_half_error_correlation": 0.1}, {"name": "accuracy_like_cross_half_error_corr_0.1", "rho": 0.018, "noise_sd": 1.45, "cross_half_error_correlation": 0.1}, {"name": "rho_0.2_margin_noise", "rho": 0.2, "noise_sd": 0.73}]
(W / "cells.json").write_text(json.dumps(CELLS, indent=1))
subprocess.check_call([sys.executable, str(W / "r6_calibration.py"), "--out", str(W / "r6_b"), "--cells", str(W / "cells.json"),
                       "--reps", "2000", "--draws", "4999", "--seed", "20260915"])
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
