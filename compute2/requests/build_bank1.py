"""Bank 1: the release's own request text for the paper's 37,682 items.

allenai/DataDecide-eval-instances ships requests/<task>-requests.jsonl.gz for
each of the 66 tasks, one row per (doc, choice), with the exact five-shot
context and continuation OLMES fed to every DataDecide checkpoint. Rows with
doc_id at or above uncond_docid_offset are OLMES's unconditioned copies (the
context is the bare answer prefix) and are dropped, as in the held-out builder.

  python requests/build_bank1.py --out data/bank1_requests.jsonl.gz

Writes the request file and bank1_summary.json with per-task counts and the
file hash. The counts must equal the release battery (tasks66.RELEASE_ITEMS),
so a bank-1 item scored here carries the same item id as in the reduced release
runs and the two can be joined item by item.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import bank  # noqa: E402
from tasks66 import RELEASE_ITEMS, RELEASE_TOTAL, TASK_INDEX, TASKS, trait_of_task  # noqa: E402


def fetch(repo, path, dest):
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(repo, path, repo_type="dataset", local_dir=str(dest)))


def rows_for_task(path, task, offset):
    docs = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r["doc_id"] >= offset:
                continue
            if r["request_type"] != "loglikelihood":
                raise SystemExit(f"{task}: request type {r['request_type']} is not a log-likelihood request")
            if r["task_name"] != task:
                raise SystemExit(f"{task}: row carries task_name {r['task_name']!r}")
            req = r["request"]
            d = docs.setdefault(r["doc_id"], {"task": task, "task_index": TASK_INDEX[task], "doc_id": r["doc_id"],
                                              "native_id": r["native_id"], "label": r["label"],
                                              "context": req["context"], "continuations": {}, "contexts": {}})
            d["contexts"][r["idx"]] = req["context"]
            if r["label"] != d["label"]:
                raise SystemExit(f"{task}: doc {r['doc_id']} has choices with different labels")
            d["continuations"][r["idx"]] = req["continuation"]
    out = []
    for doc_id in sorted(docs):
        d = docs[doc_id]
        idx = sorted(d["continuations"])
        if idx != list(range(len(idx))):
            raise SystemExit(f"{task}: doc {doc_id} choice indices {idx}")
        d["continuations"] = [d["continuations"][k] for k in idx]
        ctxs = [d["contexts"][k] for k in idx]
        if len(set(ctxs)) > 1:
            # Winogrande: the option sits in the context, the continuation is shared.
            d["context"], d["contexts"] = ctxs[0], ctxs
        else:
            del d["contexts"]
        d["group"] = f"{task}:doc{doc_id}"
        out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(HERE.parent / "data" / "bank1_requests.jsonl.gz"))
    ap.add_argument("--cache", default=str(HERE.parent / "tmp" / "release_requests"))
    ap.add_argument("--tasks", nargs="*", default=None, help="subset for a smoke test; the full file needs all 66")
    args = ap.parse_args()
    cfg = bank.read_json(HERE.parent / "config" / "banks.json")
    t0 = time.time()
    tasks = args.tasks or TASKS
    rows = []
    for task in tasks:
        rel = cfg["release_requests_path"].replace("{task}", task)
        path = fetch(cfg["release_repo"], rel, args.cache)
        got = rows_for_task(path, task, cfg["uncond_docid_offset"])
        rows.extend(got)
        print(f"[task] {task}: {len(got)} docs", flush=True)
    n = bank.validate_requests(rows)
    per_trait = Counter(trait_of_task(r["task"]) for r in rows)
    if args.tasks is None:
        if dict(per_trait) != RELEASE_ITEMS or n != RELEASE_TOTAL:
            raise SystemExit(f"bank 1 has {dict(per_trait)} items, the release battery is {RELEASE_ITEMS}; "
                             "the release request files changed and item ids can no longer be joined")
    bank.write_requests(args.out, rows)
    summary = {"bank": "bank1", "release_repo": cfg["release_repo"], "items": n, "per_trait": dict(per_trait),
               "per_task": dict(Counter(r["task"] for r in rows)), "sha256": bank.sha256(args.out),
               "file": str(args.out), "wall_seconds": time.time() - t0}
    bank.write_json(Path(args.out).with_name("bank1_summary.json"), summary)
    print(json.dumps({k: summary[k] for k in ("items", "per_trait", "sha256")}, indent=1), flush=True)


if __name__ == "__main__":
    main()
