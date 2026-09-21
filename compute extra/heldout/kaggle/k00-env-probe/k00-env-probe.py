"""k00 (CPU, no GPU quota): prove the stack before spending GPU hours.

1. Logic tests for common/snapnew.py on hand-built inputs with known answers.
2. Disk space under /kaggle/tmp, which k02 needs for a 5 GB 1B checkpoint per card.
3. A working transformers version. The Kaggle image ships transformers 5, whose
   from_pretrained calls all_tied_weights_keys, an attribute the 2024-era hf_olmo
   wrapper in ai2-olmo 0.6.0 does not define, so the DataDecide checkpoints can't
   load against it. Each candidate in CANDIDATES is installed in turn and tried in
   a fresh subprocess, which loads c4 150M on CPU in float32 and checks the packed
   scorer against the one-sequence reference path on synthetic items, including
   uneven context lengths and an item longer than max_length.

probe_report.json names the first candidate that passes as transformers_pin.
Copy it into config/tasks.json under scoring, then k02 installs exactly that.
Exit status is non-zero if no candidate works.
"""
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

CANDIDATES = ["4.57.1", "4.50.3", "4.46.3", "4.40.2"]

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import numpy as np  # noqa: E402

import snapnew  # noqa: E402

report = {"checks": {}, "candidates": {}}


def check(name, fn):
    t = time.time()
    try:
        detail = fn()
        report["checks"][name] = {"ok": True, "detail": detail, "seconds": time.time() - t}
        print(f"[ok] {name}: {detail}", flush=True)
        return True
    except Exception:  # noqa: BLE001
        report["checks"][name] = {"ok": False, "error": traceback.format_exc()[-3000:], "seconds": time.time() - t}
        print(f"[FAIL] {name}\n{traceback.format_exc()}", flush=True)
        return False


def logic():
    a = snapnew.subsample(list(range(100)), 10, 7)
    assert a == snapnew.subsample(list(range(100)), 10, 7) and len(a) == 10 and a == sorted(a)
    assert snapnew.subsample([5, 3], None, 1) == [5, 3]
    assert snapnew.num_bytes(" é") == 3 and snapnew.num_bytes("") == 1
    assert snapnew.item_id(2, 17) == 102 * 10**7 + 17
    reqs = [{"task": "t", "task_index": 0, "doc_id": 1, "native_id": "x", "label": 1, "group": "t:doc1",
             "context": "Q", "continuations": [" ab", " cdef"]},
            {"task": "u", "task_index": 1, "doc_id": 0, "native_id": "y", "label": 0, "group": "u:p",
             "context": "R", "continuations": [" a", " b", " c"]}]
    tab = snapnew.choice_table(reqs)
    assert tab["num_bytes"].tolist() == [3, 5, 2, 2, 2] and tab["is_gold"].tolist() == [False, True, True, False, False]
    sums = np.asarray([-3.0, -2.5, -1.0, -1.2, -0.8])
    path = TMP / "toy.npz"
    np.savez_compressed(path, task_index=tab["task_index"], doc_id=tab["doc_id"], choice=tab["choice"],
                        num_bytes=tab["num_bytes"], sum_logits=sums, meta=np.asarray(json.dumps({"k": 1})))
    s, _ = snapnew.load_scores(path, reqs)
    it = snapnew.per_item(s, reqs)
    # item t: gold -2.5/5 = -0.5, other -3/3 = -1, margin 0.5; item u: gold -0.5, best other -0.4, margin -0.1
    assert np.allclose(it["margin"], [0.5, -0.1]) and it["correct"].tolist() == [True, False]
    assert snapnew.select_tasks(reqs, ["u"]) == [reqs[1]]
    bad = dict(tab, choice=tab["choice"][::-1])
    np.savez_compressed(path, **{k: v for k, v in bad.items() if k != "is_gold"}, sum_logits=sums, meta=np.asarray("{}"))
    try:
        snapnew.load_scores(path, reqs)
        raise AssertionError("misaligned scores were accepted")
    except ValueError:
        pass
    return "subsample, bytes, ids, alignment and margins behave as specified"


def disk():
    free = shutil.disk_usage(TMP).free
    assert free > 15e9, f"/kaggle/tmp has {free / 1e9:.1f} GB free"
    return {"tmp_free_gb": round(free / 1e9, 1), "working_free_gb": round(shutil.disk_usage(W).free / 1e9, 1)}


check("snapnew logic", logic)
check("disk space", disk)

subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "ai2-olmo==0.6.0", "cached_path"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "omegaconf"])
runs = snapnew.read_json(ROOT / "config" / "runs.json")["runs"]
run = next(r for r in runs if r["recipe"] == "c4" and r["size"] == "150M" and r["seed"] == 2)
local = TMP / "c4-150M"
from huggingface_hub import snapshot_download  # noqa: E402

snapshot_download(run["repo"], revision=run["revision"], local_dir=str(local), allow_patterns=["*.json", "*.safetensors"])
print(f"[hub] {run['repo']}@{run['revision']} downloaded at {time.time() - t0:.0f}s", flush=True)

CHILD = r'''
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import torch, transformers
import scorer
local = sys.argv[2]
model, tok = scorer.load_model(local, "float32", "cpu")
rng = np.random.default_rng(0)
words = "the of and to in is was for on that with as by at from it an be this are".split()
reqs = []
for i in range(12):
    ctx = "Question: " + " ".join(rng.choice(words, size=int(rng.integers(3, 120)))) + "\nAnswer:"
    conts = [" " + " ".join(rng.choice(words, size=int(rng.integers(1, 6)))) for _ in range(int(rng.integers(2, 5)))]
    conts[0] = " the"
    reqs.append({"task": "probe", "task_index": 0, "doc_id": i, "label": 0, "group": f"probe:{i}",
                 "context": ctx + (" " if i % 3 == 0 else ""), "continuations": conts})
reqs.append({"task": "probe", "task_index": 0, "doc_id": 99, "label": 0, "group": "probe:99",
             "context": " ".join(["alpha"] * 2100), "continuations": [" beta", " gamma delta"]})
cfg = {"max_length": 2048, "contexts_per_batch": 4, "max_batch_tokens": 3000, "kv_check_items": 6,
       "kv_check_tolerance_nats": 1e-3, "dtype": "float32"}
sums, stats = scorer.score_requests(model, tok, reqs, cfg, "cpu")
ref = []
for r in reqs:
    for c in r["continuations"]:
        ctx_t, cont_t = scorer.encode_pair(tok, r["context"], c)
        ref.append(scorer.score_reference(model, ctx_t, cont_t, 2048, "cpu"))
worst = float(np.max(np.abs(sums - np.asarray(ref))))
out = {"transformers": transformers.__version__, "torch": torch.__version__,
       "parameters_millions": round(sum(p.numel() for p in model.parameters()) / 1e6),
       "mode": stats["mode"], "max_abs_diff_all_choices": worst,
       "check_max_abs_diff_nats": stats["check_max_abs_diff_nats"],
       "items_over_max_length": stats["items_over_max_length"],
       "seconds_scoring": stats["seconds_scoring"], "first_sum_logits": float(sums[0])}
assert stats["mode"] == "packed", f"packed path rejected: {stats}"
assert worst <= 1e-3, f"full-set disagreement {worst}"
assert stats["items_over_max_length"] == 1
print("RESULT " + json.dumps(out))
'''
(TMP / "child.py").write_text(CHILD)

pin = None
for version in CANDIDATES:
    t = time.time()
    install = subprocess.run([sys.executable, "-m", "pip", "install", "-q", f"transformers=={version}"],
                             capture_output=True, text=True)
    if install.returncode != 0:
        report["candidates"][version] = {"ok": False, "stage": "pip", "error": install.stderr[-2000:]}
        print(f"[candidate {version}] pip failed", flush=True)
        continue
    out = subprocess.run([sys.executable, str(TMP / "child.py"), str(ROOT / "common"), str(local)],
                         capture_output=True, text=True)
    line = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    if out.returncode == 0 and line:
        pin = version
        report["candidates"][version] = {"ok": True, **json.loads(line[0][len("RESULT "):]), "seconds": time.time() - t}
        print(f"[candidate {version}] ok: {report['candidates'][version]}", flush=True)
        break
    report["candidates"][version] = {"ok": False, "stage": "load", "error": (out.stderr or out.stdout)[-2500:],
                                     "seconds": time.time() - t}
    print(f"[candidate {version}] failed:\n{(out.stderr or out.stdout)[-2500:]}", flush=True)

report["transformers_pin"] = pin
report["checks"]["a transformers version loads and scores"] = {"ok": pin is not None,
                                                               "detail": pin, "seconds": 0}
shutil.rmtree(TMP, ignore_errors=True)
report["wall_seconds"] = time.time() - t0
report["all_ok"] = all(c["ok"] for c in report["checks"].values())
snapnew.write_json(W / "probe_report.json", report)
print(f"[done] all_ok={report['all_ok']} pin={pin} in {report['wall_seconds']:.0f}s", flush=True)
if not report["all_ok"]:
    sys.exit("probe failed; see probe_report.json")
