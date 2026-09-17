"""k03a (CPU): pull ARC-Easy's released per-choice scores out of the c4 tarball.

k03 compares our scores against these. Splitting the download out lets it run
while the pilot is still on the GPU, and it keeps the 4.9 GB fetch from being
repeated every time the comparison is rerun.

Covers every size and seed c4 has at the paper's frozen steps, not only the
pilot's two sizes, so a later check can use the same file. The output holds one
row per choice: size, seed, native_id, doc_id, choice index, gold flag and the
per-byte log-likelihood in nats, recovered from the release's logits_per_byte
the same way seednoise.data.datadecide.read_predictions does it.
"""
import io
import json
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402

sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = TMP / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.data.datadecide import LN2, download_recipe, parse_member  # noqa: E402

def per_byte(o, where):
    """Nats per byte from one released choice, as seednoise.read_predictions does it.

    Most releases carry logits_per_byte, a positive bits-per-byte loss, but some
    prediction files omit it and only give sum_logits with num_chars, so the
    fallback divides directly rather than dropping the choice.
    """
    lpb = o.get("logits_per_byte")
    if lpb is not None:
        return -float(lpb) * LN2
    nb = o.get("num_chars")
    if not nb:
        raise ValueError(f"{where} has neither logits_per_byte nor num_chars")
    return float(o["sum_logits"]) / float(nb)


tasks_cfg = snapnew.read_json(ROOT / "config" / "tasks.json")
task = tasks_cfg["verification"]["release_task"]
runs = [r for r in snapnew.read_json(ROOT / "config" / "runs.json")["runs"] if r["recipe"] == "c4"]
wanted = {(r["size"], r["seed"], r["step"]) for r in runs}
print(f"[plan] {len(wanted)} c4 runs, task {task}", flush=True)

tar = TMP / "c4.tar.gz"
for attempt in range(1, 4):
    try:
        download_recipe("c4", tar, progress=False)
        break
    except Exception as error:  # noqa: BLE001
        print(f"[release] attempt {attempt} failed: {type(error).__name__}: {error}", flush=True)
        tar.unlink(missing_ok=True)
        if attempt == 3:
            raise
        time.sleep(30)
print(f"[release] downloaded {tar.stat().st_size / 1e9:.2f} GB in {time.time() - t0:.0f}s", flush=True)

cols = {k: [] for k in ("size", "seed", "native_id", "doc_id", "choice", "is_gold", "per_byte")}
found = []
with tarfile.open(tar, mode="r|gz") as tf:
    for m in tf:
        k = parse_member(m.name)
        if k is None or (k.size, k.seed, k.step) not in wanted:
            continue
        handle = tf.extractfile(m)
        if handle is None:
            continue
        inner = handle.read()
        with tarfile.open(fileobj=io.BytesIO(inner), mode="r:gz") as it:
            for im in it:
                if im.name.rsplit("/", 1)[-1] != f"{task}-predictions.jsonl":
                    continue
                n = 0
                inner_handle = it.extractfile(im)
                if inner_handle is None:
                    continue
                for line in inner_handle.read().splitlines():
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    for c, o in enumerate(r["model_output"]):
                        cols["size"].append(k.size)
                        cols["seed"].append(k.seed)
                        cols["native_id"].append(str(r["native_id"]))
                        cols["doc_id"].append(int(r["doc_id"]))
                        cols["choice"].append(c)
                        cols["is_gold"].append(c == r["label"])
                        cols["per_byte"].append(per_byte(o, f"{k.size} seed {k.seed} doc {r['doc_id']} choice {c}"))
                    n += 1
                found.append({"size": k.size, "seed": k.seed, "step": k.step, "items": n})
                print(f"[release] {k.size} seed {k.seed} step {k.step}: {n} items", flush=True)
tar.unlink(missing_ok=True)
assert len(found) == len(wanted), f"{len(found)} of {len(wanted)} runs found in the tarball"

np.savez_compressed(W / "release_arc.npz",
                    size=np.asarray(cols["size"]), seed=np.asarray(cols["seed"], np.int64),
                    native_id=np.asarray(cols["native_id"]), doc_id=np.asarray(cols["doc_id"], np.int64),
                    choice=np.asarray(cols["choice"], np.int64), is_gold=np.asarray(cols["is_gold"], bool),
                    per_byte=np.asarray(cols["per_byte"], np.float64))
snapnew.write_json(W / "release_arc_summary.json",
                   {"task": task, "recipe": "c4", "runs": found, "choices": len(cols["choice"]),
                    "wall_seconds": time.time() - t0})
print(f"[done] {len(cols['choice'])} choices over {len(found)} runs in {time.time() - t0:.0f}s", flush=True)
