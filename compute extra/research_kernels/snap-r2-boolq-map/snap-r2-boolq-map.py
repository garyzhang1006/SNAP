"""R2 mapping: native ids for all tasks and passage groups for BoolQ, no estimates."""
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
subprocess.call(["df", "-h", "/kaggle/working"])
hits = [p for p in Path("/kaggle/input").rglob("boolq_map.py") if not p.name.startswith("._")]
if not hits:
    sys.exit("boolq_map.py not found under /kaggle/input")
shutil.copy(hits[0], "/kaggle/working/boolq_map.py")
subprocess.check_call([sys.executable, "-m", "pip", "freeze"], stdout=open("/kaggle/working/pip_freeze.txt", "w"))
subprocess.check_call([sys.executable, "/kaggle/working/boolq_map.py", "--out", "/kaggle/working/boolq_map",
                       "--recipe", "c4"])
print(f"[done] {time.time() - t0:.0f}s", flush=True)
