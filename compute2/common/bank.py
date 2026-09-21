"""Request files, choice tables and the per-item reduction, without torch.

A request file is gzip JSONL, one object per evaluation item:

    {"task": "arc_easy", "task_index": 1, "doc_id": 17, "native_id": "...",
     "label": 2, "group": "arc_easy:doc17", "context": "...",
     "continuations": [" a", " b", " c", " d"]}

Winogrande puts the option inside the context and shares the continuation, so
its rows also carry "contexts", one string per choice, with "context" equal to
the first of them. Every other task has one context per item and no such key.

task_index is the index into tasks66.TASKS, so the item id of a row is fixed by
the bank and the row alone. A score file is one compressed NPZ per run, aligned
choice by choice to the request file order (see score_runs.py), and per_item
turns it into the paper's two phenotypes. NPZ files are read with numpy's
default loader, which refuses object arrays.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from tasks66 import TASK_INDEX, TRAIT_INDEX, item_id, trait_of_task


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def read_requests(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_requests(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # mtime 0 so a rebuild with identical rows gives an identical file hash.
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
        for r in rows:
            gz.write((json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8"))


def num_bytes(continuation):
    """OLMES divides sum_logits by the UTF-8 length of the continuation, leading
    space included, and so does the release's logits_per_byte."""
    return max(len(continuation.encode("utf-8")), 1)


def validate_requests(rows):
    """Every structural assumption the scorer and the reducer make, checked once."""
    seen = set()
    for r in rows:
        if r["task"] not in TASK_INDEX or TASK_INDEX[r["task"]] != r["task_index"]:
            raise ValueError(f"{r['task']}: task_index {r['task_index']} is not its index in tasks66.TASKS")
        k = len(r["continuations"])
        if k < 2:
            raise ValueError(f"{r['task']} doc {r['doc_id']}: {k} choices, an item needs two")
        if not isinstance(r["label"], int) or not 0 <= r["label"] < k:
            raise ValueError(f"{r['task']} doc {r['doc_id']}: label {r['label']!r} for {k} choices")
        if any(c == "" for c in r["continuations"]):
            raise ValueError(f"{r['task']} doc {r['doc_id']}: an empty continuation has no byte count")
        if "contexts" in r:
            cs = r["contexts"]
            if not isinstance(cs, list) or len(cs) != k or any(not isinstance(c, str) or c == "" for c in cs):
                raise ValueError(f"{r['task']} doc {r['doc_id']}: contexts must be {k} non-empty strings")
            if cs[0] != r["context"] or len(set(cs)) == 1:
                raise ValueError(f"{r['task']} doc {r['doc_id']}: contexts must differ and start with the row's context")
        key = (r["task_index"], r["doc_id"])
        if key in seen:
            raise ValueError(f"{r['task']} doc {r['doc_id']} appears twice")
        seen.add(key)
    return len(rows)


def subsample(doc_ids, max_items, seed):
    """Deterministic item cap; returns the kept doc ids in their original order."""
    doc_ids = list(doc_ids)
    if max_items is None or len(doc_ids) <= max_items:
        return doc_ids
    rng = np.random.default_rng(seed)
    keep = set(rng.choice(len(doc_ids), size=max_items, replace=False).tolist())
    return [d for i, d in enumerate(doc_ids) if i in keep]


def select_tasks(requests, names):
    names = set(names)
    missing = names - {r["task"] for r in requests}
    if missing:
        raise KeyError(f"tasks {sorted(missing)} are not in the request file")
    return [r for r in requests if r["task"] in names]


def choice_table(requests):
    """Flatten requests into per-choice arrays in file order."""
    task, doc, choice, gold, nb = [], [], [], [], []
    for r in requests:
        for k, cont in enumerate(r["continuations"]):
            task.append(r["task_index"])
            doc.append(r["doc_id"])
            choice.append(k)
            gold.append(k == r["label"])
            nb.append(num_bytes(cont))
    return {"task_index": np.asarray(task, np.int64), "doc_id": np.asarray(doc, np.int64),
            "choice": np.asarray(choice, np.int64), "is_gold": np.asarray(gold, bool),
            "num_bytes": np.asarray(nb, np.int64)}


def load_scores(path, requests):
    """One run's score file, checked column by column against the request file."""
    with np.load(path) as z:
        s = {k: z[k] for k in z.files}
    ref = choice_table(requests)
    for key in ("task_index", "doc_id", "choice", "num_bytes"):
        if not np.array_equal(s[key], ref[key]):
            raise ValueError(f"{path}: column {key} disagrees with the request file; scores and requests are misaligned")
    if not np.isfinite(s["sum_logits"]).all():
        raise ValueError(f"{path}: {int((~np.isfinite(s['sum_logits'])).sum())} non-finite log-likelihoods")
    return s, json.loads(str(s["meta"]))


def per_item(scores, requests, bank):
    """Per-byte margin and correctness per item, the paper's equation (1).

    Returns item_id, trait, group (the 66-task index), margin and correct, all
    sorted by item_id. A zero margin scores wrong, as in
    seednoise.phenotypes.reduce_choices.
    """
    pb = scores["sum_logits"] / scores["num_bytes"]
    ids, trait, group, margin = [], [], [], []
    pos = 0
    for r in requests:
        k = len(r["continuations"])
        v = pb[pos:pos + k]
        other = np.max(np.delete(v, r["label"]))
        ids.append(item_id(bank, r["task_index"], r["doc_id"]))
        trait.append(TRAIT_INDEX[trait_of_task(r["task"])])
        group.append(r["task_index"])
        margin.append(float(v[r["label"]] - other))
        pos += k
    if pos != pb.size:
        raise ValueError(f"{pb.size} choices scored but the requests hold {pos}")
    ids = np.asarray(ids, np.int64)
    order = np.argsort(ids, kind="stable")
    margin = np.asarray(margin, np.float64)[order]
    return {"item_id": ids[order], "trait": np.asarray(trait, np.int64)[order],
            "group": np.asarray(group, np.int64)[order], "margin": margin, "correct": margin > 0.0}


def gain(scores):
    """Mean per-byte log-likelihood over every choice, the paper's gain covariate."""
    return float(np.mean(scores["sum_logits"] / scores["num_bytes"]))
