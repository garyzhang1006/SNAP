"""k00 (CPU, about 15 minutes, no GPU quota): prove the stack before spending GPU hours.

1. Logic tests for common/snapnew.py on hand-built inputs with known answers.
2. The install k02 uses (ai2-olmo 0.6.0 without its dependency pins, plus
   omegaconf) imports hf_olmo against the Kaggle image's torch and transformers.
3. The smallest scored checkpoint (c4 150M, default branch) loads on CPU in
   float32 with SDPA attention.
4. The packed-cache scorer agrees with the one-sequence reference path on
   synthetic multiple-choice items, including uneven context lengths, a
   continuation of one token, and an item longer than max_length.
5. Disk space under /kaggle/tmp, which k02 needs for a 5 GB 1B checkpoint per card.

Exit status is non-zero if any check fails. probe_report.json has the details.
"""
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

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

report = {"checks": {}}


def check(name, fn):
    t = time.time()
    try:
        detail = fn()
        report["checks"][name] = {"ok": True, "detail": detail, "seconds": time.time() - t}
        print(f"[ok] {name}: {detail}", flush=True)
    except Exception:  # noqa: BLE001
        report["checks"][name] = {"ok": False, "error": traceback.format_exc()[-3000:], "seconds": time.time() - t}
        print(f"[FAIL] {name}\n{traceback.format_exc()}", flush=True)


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


check("snapnew logic", logic)


def install():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "ai2-olmo==0.6.0", "cached_path"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "omegaconf"])
    out = subprocess.run([sys.executable, "-c",
                          "import torch, transformers, hf_olmo, numpy; print(torch.__version__, transformers.__version__, numpy.__version__)"],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-3000:]
    return out.stdout.strip()


check("install and import hf_olmo", install)

state = {}


def load():
    import importlib
    importlib.invalidate_caches()
    from huggingface_hub import snapshot_download
    import scorer
    runs = snapnew.read_json(ROOT / "config" / "runs.json")["runs"]
    run = next(r for r in runs if r["recipe"] == "c4" and r["size"] == "150M" and r["seed"] == 2)
    local = TMP / "c4-150M"
    snapshot_download(run["repo"], revision=run["revision"], local_dir=str(local), allow_patterns=["*.json", "*.safetensors"])
    model, tok = scorer.load_model(str(local), "float32", "cpu")
    state.update(model=model, tok=tok, scorer=scorer, local=local)
    return f"{run['repo']}@{run['revision']} loaded, {sum(p.numel() for p in model.parameters()) / 1e6:.0f}M parameters"


check("load c4 150M on CPU", load)


def agreement():
    if "model" not in state:
        raise RuntimeError("model did not load")
    scorer, model, tok = state["scorer"], state["model"], state["tok"]
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
    assert stats["mode"] == "packed", f"packed path was rejected: {stats}"
    assert worst <= 1e-3, f"full-set disagreement {worst}"
    assert stats["items_over_max_length"] == 1
    return {"mode": stats["mode"], "max_abs_diff_all_choices": worst, "check": stats["check_max_abs_diff_nats"]}


check("packed cache matches reference", agreement)


def disk():
    free = shutil.disk_usage(TMP).free
    wt = shutil.disk_usage(W)
    assert free > 15e9, f"/kaggle/tmp has {free / 1e9:.1f} GB free"
    return {"tmp_free_gb": round(free / 1e9, 1), "working_free_gb": round(wt.free / 1e9, 1)}


check("disk space", disk)
shutil.rmtree(TMP, ignore_errors=True)
report["wall_seconds"] = time.time() - t0
report["all_ok"] = all(c["ok"] for c in report["checks"].values())
snapnew.write_json(W / "probe_report.json", report)
print(f"[done] all_ok={report['all_ok']} in {report['wall_seconds']:.0f}s", flush=True)
if not report["all_ok"]:
    sys.exit("probe failed; see probe_report.json")
