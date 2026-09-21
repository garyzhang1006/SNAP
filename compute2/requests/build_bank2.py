"""Bank 2: a disjoint item set from the same ten benchmarks, built with OLMES.

The prompts must be the ones DataDecide was scored with, so the request text is
produced by OLMES at the pinned commit (config/banks.json, the commit the
held-out pipeline used) rather than rewritten here. Every task config is taken
verbatim from OLMES's TASK_CONFIGS and only the split is changed, to a split
disjoint from bank 1 (train for eight benchmarks, validation for OpenBookQA and
for the 57 MMLU subjects). The fixed five-shot exemplars OLMES uses come from
FEWSHOT_SOURCES and MMLU's dev split, so they are the same in both banks.

Bank 2 is then filtered and capped: an item whose question text appears in its
own few-shot context (an exemplar drawn from the train split) is dropped, an
item whose context equals a bank-1 context is dropped, and each benchmark is
capped by a deterministic subsample at the count in config/banks.json (600 per
benchmark, chosen for the compute budget; MMLU validation holds about 1,531).
Item noise widens the bank-2 intervals without biasing the ratio, and the
summary records the achieved count per benchmark. The zero-shot bank is the same items rebuilt
with num_shots 0.

OLMES pins its own torch, so it lives in its own uv environment (as in
compute extra/heldout/kaggle/k01-requests/k01-requests.py) and the builder
runs there as a subprocess.

  python requests/build_bank2.py --bank1 data/bank1_requests.jsonl.gz --out-dir data --zero-shot
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import bank  # noqa: E402
from tasks66 import TASK_INDEX, TASKS, trait_of_task  # noqa: E402

BUILDER = r'''
import copy, json, sys
from oe_eval.configs.tasks import TASK_CONFIGS
from oe_eval.run_eval import load_task

specs = json.loads(sys.argv[1])
out = open(sys.argv[2], "w")
configs = {}
for spec in specs:
    alias = spec["olmes_alias"]
    if alias not in TASK_CONFIGS:
        raise SystemExit(f"OLMES has no task config named {alias!r}")
    cfg = copy.deepcopy(TASK_CONFIGS[alias])
    cfg["split"] = spec["split"]
    cfg["limit"] = None
    if spec.get("num_shots") is not None:
        cfg["num_shots"] = spec["num_shots"]
    cfg.pop("gantry_args", None)
    cfg.setdefault("metadata", {})["alias"] = alias
    task = load_task(cfg)
    task.download()
    task.build_all_requests()
    offset = cfg.get("metric_kwargs", {}).get("uncond_docid_offset", 1000000)
    docs = {}
    for ins in task._instances:
        if ins.doc_id >= offset:
            continue
        if ins.request_type != "loglikelihood":
            raise SystemExit(f"{alias}: request type {ins.request_type} is not a log-likelihood request")
        req = ins.request.__dict__
        d = docs.setdefault(ins.doc_id, {"task": spec["task"], "doc_id": ins.doc_id, "native_id": ins.native_id,
                                         "label": ins.label, "context": req["context"], "continuations": {},
                                         "contexts": {}, "query": ins.doc.get("query")})
        d["contexts"][ins.idx] = req["context"]
        d["continuations"][ins.idx] = req["continuation"]
    for doc_id in sorted(docs):
        d = docs[doc_id]
        conts = [d["continuations"][k] for k in sorted(d["continuations"])]
        if sorted(d["continuations"]) != list(range(len(conts))):
            raise SystemExit(f"{alias}: doc {doc_id} choice indices {sorted(d['continuations'])}")
        if not isinstance(d["label"], int) or not 0 <= d["label"] < len(conts):
            raise SystemExit(f"{alias}: doc {doc_id} label {d['label']!r} for {len(conts)} choices")
        d["continuations"] = conts
        ctxs = [d["contexts"][k] for k in range(len(conts))]
        if len(set(ctxs)) > 1:
            d["context"], d["contexts"] = ctxs[0], ctxs
        else:
            del d["contexts"]
        out.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"[task] {alias} split={cfg['split']} shots={cfg.get('num_shots')}: {len(docs)} docs", flush=True)
    configs[spec["task"]] = {k: cfg.get(k) for k in ("num_shots", "split", "primary_metric", "fewshot_source")}
out.close()
open(sys.argv[3], "w").write(json.dumps(configs))
'''


def make_env(commit, tmp):
    """OLMES in its own uv environment, with the pinned tree's data files put back."""
    venv = tmp / "olmes-env"
    py = venv / "bin" / "python"
    if not py.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "uv"])
        subprocess.check_call([sys.executable, "-m", "uv", "venv", str(venv), "--python", "3.12"])
        subprocess.check_call([sys.executable, "-m", "uv", "pip", "install", "-q", "--python", str(py),
                               "setuptools==80.9.0", f"ai2-olmes @ git+https://github.com/allenai/olmes.git@{commit}"])
    site = next((venv / "lib").glob("python3.*/site-packages"))
    clone = tmp / "olmes-src"
    if not clone.exists():
        subprocess.check_call(["git", "clone", "-q", "https://github.com/allenai/olmes.git", str(clone)])
        subprocess.check_call(["git", "-C", str(clone), "checkout", "-q", commit])
    for d in sorted((clone / "oe_eval" / "dependencies").iterdir()):
        if d.is_dir():
            shutil.copytree(d, site / "oe_eval" / "dependencies" / d.name, dirs_exist_ok=True)
    return py, site


def specs_for(cfg, num_shots=None):
    specs = []
    for spec in cfg["bank2"]:
        if spec["trait"] == "mmlu":
            for task in TASKS:
                if task.startswith("mmlu_"):
                    subject = task[len("mmlu_"):]
                    specs.append({"task": task, "olmes_alias": spec["olmes_alias"].replace("{subject}", subject),
                                  "split": spec["split"], "num_shots": num_shots})
        else:
            specs.append({"task": spec["trait"], "olmes_alias": spec["olmes_alias"], "split": spec["split"],
                          "num_shots": num_shots})
    return specs


def question_text(row):
    """The item's own text, to look for inside its few-shot block."""
    q = row.get("query")
    if isinstance(q, str) and q.strip():
        return q.strip()
    # Some OLMES docs carry no query field; the last prompt segment of the
    # context is the item itself.
    return row["context"].rsplit("\n\n", 1)[-1].strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank1", default=str(HERE.parent / "data" / "bank1_requests.jsonl.gz"))
    ap.add_argument("--out-dir", default=str(HERE.parent / "data"))
    ap.add_argument("--tmp", default=str(HERE.parent / "tmp" / "olmes"))
    ap.add_argument("--zero-shot", action="store_true", help="also build bank2zs, the same items at num_shots 0")
    args = ap.parse_args()
    cfg = bank.read_json(HERE.parent / "config" / "banks.json")
    t0 = time.time()
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    py, site = make_env(cfg["olmes_commit"], tmp)
    env = dict(os.environ, PYTHONPATH=str(site), PYTHONNOUSERSITE="1")
    (tmp / "build.py").write_text(BUILDER)

    bank1 = bank.read_requests(args.bank1)
    bank1_contexts = {c for r in bank1 for c in r.get("contexts") or [r["context"]]}
    bank1_count = Counter(trait_of_task(r["task"]) for r in bank1)
    caps = {s["trait"]: s["max_items"] for s in cfg["bank2"]}
    for trait, cap in caps.items():
        if cap is not None and cap > bank1_count[trait]:
            raise SystemExit(f"{trait}: bank2 cap {cap} exceeds bank 1's {bank1_count[trait]} items")

    def build(num_shots, name):
        raw, cfg_path = tmp / f"{name}_raw.jsonl", tmp / f"{name}_configs.json"
        subprocess.check_call([str(py), "-S", str(tmp / "build.py"), json.dumps(specs_for(cfg, num_shots)),
                               str(raw), str(cfg_path)], env=env)
        rows = [json.loads(line) for line in open(raw, encoding="utf-8")]
        return rows, json.loads(cfg_path.read_text())

    rows, task_cfgs = build(None, "bank2")
    kept, dropped = [], Counter()
    by_task = {}
    for r in rows:
        by_task.setdefault(r["task"], []).append(r)
    for task in TASKS:
        task_rows = by_task.get(task, [])
        if not task_rows:
            raise SystemExit(f"no bank-2 requests built for {task}")
        clean = []
        for r in task_rows:
            q = question_text(r)
            ctxs = r.get("contexts") or [r["context"]]
            if q and any(q in c[: max(len(c) - len(q), 0)] for c in ctxs):
                dropped[f"{task}:in_fewshot"] += 1
                continue
            if any(c in bank1_contexts for c in ctxs):
                dropped[f"{task}:in_bank1"] += 1
                continue
            clean.append(r)
        cap = caps[trait_of_task(task)]
        keep = set(bank.subsample([r["doc_id"] for r in clean], cap, cfg["subsample_seed"] + TASK_INDEX[task]))
        for r in clean:
            if r["doc_id"] in keep:
                row = {"task": task, "task_index": TASK_INDEX[task], "doc_id": r["doc_id"],
                       "native_id": r["native_id"], "label": r["label"], "context": r["context"],
                       "continuations": r["continuations"], "group": f"{task}:doc{r['doc_id']}"}
                if r.get("contexts"):
                    row["contexts"] = r["contexts"]
                kept.append(row)
    n = bank.validate_requests(kept)
    # The caps are upper bounds. A split can hold fewer items than bank 1
    # (MMLU validation has about 1,531 against the test split's 14,042, the
    # ARC train splits fall a little short), and the achieved counts are what
    # the analysis sees, so the shortfall is printed and recorded, not hidden.
    built = Counter(trait_of_task(r["task"]) for r in kept)
    shortfall = {t: {"bank1": bank1_count[t], "bank2": built[t]} for t in bank1_count if built[t] < bank1_count[t]}
    for t, v in sorted(shortfall.items()):
        print(f"[short] {t}: bank 2 has {v['bank2']} items against bank 1's {v['bank1']}", flush=True)
    out_dir = Path(args.out_dir)
    out = out_dir / "bank2_requests.jsonl.gz"
    bank.write_requests(out, kept)
    summary = {"bank": "bank2", "olmes_commit": cfg["olmes_commit"], "items": n,
               "per_trait": dict(Counter(trait_of_task(r["task"]) for r in kept)),
               "per_task": dict(Counter(r["task"] for r in kept)), "dropped": dict(dropped), "shortfall": shortfall,
               "task_configs": task_cfgs, "sha256": bank.sha256(out), "file": str(out)}
    bank.write_json(out_dir / "bank2_summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("items", "per_trait", "dropped", "sha256")}, indent=1), flush=True)

    if args.zero_shot:
        # Same items, no exemplars: the doc ids OLMES assigns are stable within a
        # split, so the bank-2 keep set selects the same documents.
        zs_rows, zs_cfgs = build(0, "bank2zs")
        keep = {(r["task_index"], r["doc_id"]) for r in kept}
        zs = []
        for r in zs_rows:
            key = (TASK_INDEX[r["task"]], r["doc_id"])
            if key in keep:
                row = {"task": r["task"], "task_index": key[0], "doc_id": r["doc_id"], "native_id": r["native_id"],
                       "label": r["label"], "context": r["context"], "continuations": r["continuations"],
                       "group": f"{r['task']}:doc{r['doc_id']}"}
                if r.get("contexts"):
                    row["contexts"] = r["contexts"]
                zs.append(row)
        if len(zs) != len(kept):
            raise SystemExit(f"zero-shot rebuild found {len(zs)} of bank 2's {len(kept)} items; doc ids moved")
        zs.sort(key=lambda r: (r["task_index"], r["doc_id"]))
        b2 = {(r["task_index"], r["doc_id"]): r for r in kept}
        for r in zs:
            ref = b2[(r["task_index"], r["doc_id"])]
            if (r["label"] != ref["label"] or r["continuations"] != ref["continuations"]
                    or ("contexts" in r) != ("contexts" in ref)):
                raise SystemExit(f"{r['task']} doc {r['doc_id']}: zero-shot choices differ from the five-shot ones")
            if not (r["native_id"] is None or ref["native_id"] is None) and r["native_id"] != ref["native_id"]:
                raise SystemExit(f"{r['task']} doc {r['doc_id']}: native id moved between builds")
        bank.validate_requests(zs)
        out_zs = out_dir / "bank2zs_requests.jsonl.gz"
        bank.write_requests(out_zs, zs)
        bank.write_json(out_dir / "bank2zs_summary.json",
                        {"bank": "bank2zs", "items": len(zs), "task_configs": zs_cfgs, "sha256": bank.sha256(out_zs),
                         "file": str(out_zs), "same_items_as": summary["sha256"]})
        print(f"[bank2zs] {len(zs)} items, sha256 {bank.sha256(out_zs)}", flush=True)
    print(f"[done] {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
