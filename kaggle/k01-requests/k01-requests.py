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
import os
import shutil
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

# The Kaggle image's python has no working ensurepip, so venv creation fails;
# uv builds the environment without it and installs OLMES's pinned dependencies
# where they can't disturb the image the other kernels run in.
venv = TMP / "olmes-env"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "uv"])
subprocess.check_call([sys.executable, "-m", "uv", "venv", str(venv), "--python", "3.12"])
py = str(venv / "bin" / "python")
# setuptools is explicit because uv environments ship without it, and it is
# pinned below 81 because one of OLMES's transitive imports (alpaca_eval) still
# reaches for pkg_resources, which setuptools dropped after 80.
subprocess.check_call([sys.executable, "-m", "uv", "pip", "install", "-q", "--python", py, "setuptools==80.9.0",
                       f"ai2-olmes @ git+https://github.com/allenai/olmes.git@{commit}"])
subprocess.run([sys.executable, "-m", "uv", "pip", "freeze", "--python", py],
               stdout=open(W / "olmes_env_freeze.txt", "w"), check=True)
print(f"[env] OLMES {commit} installed in {time.time() - t0:.0f}s", flush=True)

specs = tasks["heldout"] + tasks["backups_in_order"] + [tasks["verification"]]
BUILDER = r'''
import copy, json, sys
from oe_eval.configs.tasks import TASK_CONFIGS
from oe_eval.run_eval import load_task

specs = json.loads(sys.argv[1])
out = open(sys.argv[2], "w")
configs = {}
for index, spec in enumerate(specs):
    alias = spec["olmes_alias"]
    if alias not in TASK_CONFIGS:
        raise SystemExit(f"OLMES has no task config named {alias!r}")
    cfg = copy.deepcopy(TASK_CONFIGS[alias])
    cfg.update(spec["overrides"])
    # gantry_args is a launcher hint on some task configs, and OLMES's own config
    # hasher rejects any key it doesn't know, so it goes before the task is built.
    cfg.pop("gantry_args", None)
    cfg.setdefault("metadata", {})["alias"] = alias
    task = load_task(cfg)
    task.download()
    task.build_all_requests()
    docs = {}
    # OLMES adds a second, unconditioned copy of every doc, whose context is just
    # the answer prefix and whose scores feed acc_uncond, which nothing here uses.
    # Those copies carry doc_id shifted by uncond_docid_offset (base_task.py).
    offset = cfg.get("metric_kwargs", {}).get("uncond_docid_offset", 1000000)
    for ins in task._instances:
        if ins.doc_id >= offset:
            continue
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
        if field and not key and "\nQuestion:" in d["context"]:
            # The processed doc drops the passage field on some tasks, so items
            # sharing a passage are recognised by the prompt they share instead.
            key = str(abs(hash(d["context"].rsplit("\nQuestion:", 1)[0])) % 10**12)
        group = f"{spec['name']}:{key}" if key else f"{spec['name']}:doc{doc_id}"
        row = {k: d[k] for k in ("task", "task_index", "doc_id", "native_id", "label", "context")}
        row["continuations"] = conts
        row["group"] = group
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[task] {alias}: {len(docs)} docs", flush=True)
    configs[spec["name"]] = {k: cfg.get(k) for k in ("num_shots", "split", "dataset_path", "dataset_name", "primary_metric")}
out.close()
open(sys.argv[3], "w").write(json.dumps(configs))
'''
(TMP / "build.py").write_text(BUILDER)
raw = TMP / "requests_raw.jsonl"
# Kaggle installs a sitecustomize hook that intercepts google.cloud imports and
# needs kaggle_gcp, which only exists in the image's own site-packages, so it
# raises inside this environment. Running with -S skips site setup entirely and
# the environment is put on the path directly, which also keeps the image's
# torch and transformers out of the OLMES environment.
site = next((venv / "lib").glob("python3.*/site-packages"))
# The wheel built from the repository leaves oe_eval/dependencies empty, and
# AGIEval, DROP and CoQA read their items from files that live there, so the
# pinned tree is cloned and those files are put back next to the installed code.
clone = TMP / "olmes-src"
subprocess.check_call(["git", "clone", "-q", "https://github.com/allenai/olmes.git", str(clone)])
subprocess.check_call(["git", "-C", str(clone), "checkout", "-q", commit])
for d in sorted((clone / "oe_eval" / "dependencies").iterdir()):
    if d.is_dir():
        shutil.copytree(d, site / "oe_eval" / "dependencies" / d.name, dirs_exist_ok=True)
print("[deps] copied", sorted(p.name for p in (site / "oe_eval" / "dependencies").iterdir()), flush=True)
env = dict(os.environ, PYTHONPATH=str(site), PYTHONNOUSERSITE="1")
cfg_path = TMP / "task_configs.json"
subprocess.check_call([py, "-S", str(TMP / "build.py"), json.dumps(specs), str(raw), str(cfg_path)], env=env)
task_configs = json.loads(cfg_path.read_text())

rows = [json.loads(line) for line in open(raw)]
kept, summary = [], {"olmes_commit": commit, "tasks": {}, "task_configs": task_configs}
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
        "num_shots": task_configs[spec["name"]].get("num_shots"), "split": task_configs[spec["name"]].get("split"),
        "items_kept": len(task_rows), "choices_total": sum(n_choices), "choices_per_item": sorted(set(n_choices)),
        "chance_accuracy": sum(1 / k for k in n_choices) / len(n_choices),
        "groups": len({r["group"] for r in task_rows}),
        "context_chars_median": ctx_chars[len(ctx_chars) // 2], "context_chars_max": ctx_chars[-1]}
out = W / "requests.jsonl.gz"
snapnew.write_requests(out, kept)
summary.update(file="requests.jsonl.gz", sha256=snapnew.sha256(out), items=len(kept), wall_seconds=time.time() - t0)
snapnew.write_json(W / "requests_summary.json", summary)
print(json.dumps(summary, indent=1), flush=True)
