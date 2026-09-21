"""R2/R3 provenance audit from the release request files; no estimates."""
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)


def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


shutil.copy(find("requests_audit.py"), "/kaggle/working/requests_audit.py")
subprocess.check_call([sys.executable, "/kaggle/working/requests_audit.py", "--out", "/kaggle/working/requests_audit",
                       "--native", str(find("task_native_ids.json"))])
print(f"[done] {time.time() - t0:.0f}s", flush=True)
