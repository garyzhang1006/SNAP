"""k01 (CPU): build the frozen request file with AI2's own OLMES harness.

DataDecide's released scores came from OLMES, so the prompts, few-shot examples
and answer continuations for the new tasks are taken from OLMES at a pinned
commit instead of being rewritten here. OLMES pins torch and a long dependency
list, so it goes into its own virtual environment and never touches the Kaggle
image the other kernels use.

Output: requests.jsonl.gz (every task in config/tasks.json, held-out tasks,
backups and the ARC-Easy verification task), requests_summary.json with item
counts, choice counts, context lengths and the file hash. The hash goes into
PROTOCOL_heldout.md before any model is scored.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

t0 = time.time()
W = Path("/kaggle/working")
TMP = Path("/kaggle/tmp")
TMP.mkdir(parents=True, exist_ok=True)
src = [p for p in Path("/kaggle/input").rglob("snapnew.py") if not p.name.startswith("._")]
assert len(src) == 1, f"common/snapnew.py not found exactly once under /kaggle/input: {src}"
ROOT = src[0].parent.parent
sys.path.insert(0, str(ROOT / "common"))
import snapnew  # noqa: E402

tasks = snapnew.read_json(ROOT / "config" / "tasks.json")
commit = tasks["olmes_commit"]
print("[env] python", sys.version.replace("\n", " "), flush=True)

venv = TMP / "olmes-env"
subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
py = str(venv / "bin" / "python")
subprocess.check_call([py, "-m", "pip", "install", "-q", "--upgrade", "pip"])
subprocess.check_call([py, "-m", "pip", "install", "-q", f"ai2-olmes @ git+https://github.com/allenai/olmes.git@{commit}"])
subprocess.run([py, "-m", "pip", "freeze"], stdout=open(W / "olmes_env_freeze.txt", "w"), check=True)
print(f"[env] OLMES {commit} installed in {time.time() - t0:.0f}s", flush=True)

specs = tasks["heldout"] + tasks["backups_in_order"] + [tasks["verification"]]
BUILDER = r'''
import copy, json, sys
from oe_eval.configs.tasks import TASK_CONFIGS
from oe_eval.run_eval import load_task

specs = json.loads(sys.argv[1])
out = open(sys.argv[2], "w")
for index, spec in enumerate(specs):
    alias = spec["olmes_alias"]
    if alias not in TASK_CONFIGS:
        raise SystemExit(f"OLMES has no task config named {alias!r}")
    cfg = copy.deepcopy(TASK_CONFIGS[alias])
    cfg.update(spec["overrides"])
    cfg.setdefault("metadata", {})["alias"] = alias
    task = load_task(cfg)
    task.download()
    task.build_all_requests()
    docs = {}
    for ins in task._instances:
        if ins.request_type != "loglikelihood":
            raise SystemExit(f"{alias}: request type {ins.request_type} is not a log-likelihood request")
        req = ins.request.__dict__
        d = docs.setdefault(ins.doc_id, {"task": spec["name"], "task_index": index, "doc_id": ins.doc_id,
                                         "native_id": ins.native_id, "label": ins.label,
                                         "context": req["context"], "continuations": {}, "doc": ins.doc})
        if req["context"] != d["context"]:
            raise SystemExit(f"{alias}: doc {ins.doc_id} has choices with different contexts")
        d["continuations"][ins.idx] = req["continuation"]
    for doc_id in sorted(docs):
        d = docs[doc_id]
        conts = [d["continuations"][k] for k in sorted(d["continuations"])]
        if sorted(d["continuations"]) != list(range(len(conts))):
            raise SystemExit(f"{alias}: doc {doc_id} choice indices {sorted(d['continuations'])}")
        if not isinstance(d["label"], int) or not 0 <= d["label"] < len(conts):
            raise SystemExit(f"{alias}: doc {doc_id} label {d['label']!r} for {len(conts)} choices")
        field = spec["group_field"]
        key = d["doc"].get(field) if field else None
        group = f"{spec['name']}:{key}" if key else f"{spec['name']}:doc{doc_id}"
        row = {k: d[k] for k in ("task", "task_index", "doc_id", "native_id", "label", "context")}
        row["continuations"] = conts
        row["group"] = group
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[task] {alias}: {len(docs)} docs", flush=True)
out.close()
'''
(TMP / "build.py").write_text(BUILDER)
raw = TMP / "requests_raw.jsonl"
subprocess.check_call([py, str(TMP / "build.py"), json.dumps(specs), str(raw)])

rows = [json.loads(line) for line in open(raw)]
kept, summary = [], {"olmes_commit": commit, "tasks": {}}
for index, spec in enumerate(specs):
    task_rows = [r for r in rows if r["task_index"] == index]
    assert task_rows, f"no requests built for {spec['name']}"
    keep = set(snapnew.subsample([r["doc_id"] for r in task_rows], spec["max_items"], tasks["subsample_seed"] + index))
    task_rows = [r for r in task_rows if r["doc_id"] in keep]
    kept.extend(task_rows)
    n_choices = [len(r["continuations"]) for r in task_rows]
    ctx_chars = sorted(len(r["context"]) for r in task_rows)
    summary["tasks"][spec["name"]] = {
        "olmes_alias": spec["olmes_alias"], "task_index": index, "items_built": len([r for r in rows if r["task_index"] == index]),
        "items_kept": len(task_rows), "choices_total": sum(n_choices), "choices_per_item": sorted(set(n_choices)),
        "chance_accuracy": sum(1 / k for k in n_choices) / len(n_choices),
        "groups": len({r["group"] for r in task_rows}),
        "context_chars_median": ctx_chars[len(ctx_chars) // 2], "context_chars_max": ctx_chars[-1]}
out = W / "requests.jsonl.gz"
snapnew.write_requests(out, kept)
summary.update(file="requests.jsonl.gz", sha256=snapnew.sha256(out), items=len(kept), wall_seconds=time.time() - t0)
snapnew.write_json(W / "requests_summary.json", summary)
print(json.dumps(summary, indent=1), flush=True)
