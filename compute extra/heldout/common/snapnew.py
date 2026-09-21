"""Shared helpers for the held-out scoring pipeline.

Nothing here imports torch, so the CPU kernels can use it without a GPU stack.
The request format is the one contract every stage shares, one JSON object per
evaluation item:

    {"task": "sciq", "task_index": 0, "doc_id": 17, "native_id": "...",
     "label": 2, "group": "sciq:17", "context": "...",
     "continuations": [" a", " b", " c", " d"]}

Scores go the other way as one compressed NPZ per run, aligned choice by choice
to the request file order, with sum_logits and num_bytes for every continuation.
NPZ files are read with numpy's default loader, which refuses object arrays.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

# Held-out item ids sit above every released task id (66 tasks times 10**7),
# so a combined population can't collide with the paper's items.
HELDOUT_ID_BASE = 100
ITEM_STRIDE = 10_000_000


def find_one(pattern, root="/kaggle/input"):
    hits = sorted(p for p in Path(root).rglob(pattern) if not p.name.startswith("._"))
    if len(hits) != 1:
        raise FileNotFoundError(f"expected exactly one {pattern!r} under {root}, found {len(hits)}: {hits[:5]}")
    return hits[0]


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
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def num_bytes(continuation):
    """OLMES divides sum_logits by the UTF-8 length of the request continuation,
    leading space included (oe_eval/metrics/metric.py), and so does the paper."""
    return max(len(continuation.encode("utf-8")), 1)


def subsample(doc_ids, max_items, seed):
    """Deterministic item cap. Returns the kept doc ids in their original order."""
    doc_ids = list(doc_ids)
    if max_items is None or len(doc_ids) <= max_items:
        return doc_ids
    rng = np.random.default_rng(seed)
    keep = set(rng.choice(len(doc_ids), size=max_items, replace=False).tolist())
    return [d for i, d in enumerate(doc_ids) if i in keep]


def item_id(task_index, doc_id):
    return (HELDOUT_ID_BASE + int(task_index)) * ITEM_STRIDE + int(doc_id)


def select_tasks(requests, names):
    """The requests a scorer shard actually scored, in file order."""
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
    """Load one run's scores and check they line up with the request file."""
    with np.load(path) as z:
        s = {k: z[k] for k in z.files}
    ref = choice_table(requests)
    for key in ("task_index", "doc_id", "choice", "num_bytes"):
        if not np.array_equal(s[key], ref[key]):
            raise ValueError(f"{path}: column {key} disagrees with the request file; scores and requests are misaligned")
    if not np.isfinite(s["sum_logits"]).all():
        raise ValueError(f"{path}: {int((~np.isfinite(s['sum_logits'])).sum())} non-finite log-likelihoods")
    meta = json.loads(str(s["meta"]))
    return s, meta


def per_item(scores, requests, tasks=None):
    """Per-byte margin and correctness per item, the paper's equation (1).

    Returns item_id, task_index, margin, correct, choice count and the passage
    group string, all sorted by item_id. A zero margin is scored wrong, as in
    seednoise.phenotypes.reduce_choices.
    """
    pb = scores["sum_logits"] / scores["num_bytes"]
    out = {"item_id": [], "task_index": [], "margin": [], "correct": [], "n_choices": [], "group": []}
    pos = 0
    for r in requests:
        k = len(r["continuations"])
        if tasks is None or r["task"] in tasks:
            v = pb[pos:pos + k]
            other = np.max(np.delete(v, r["label"]))
            m = float(v[r["label"]] - other)
            out["item_id"].append(item_id(r["task_index"], r["doc_id"]))
            out["task_index"].append(r["task_index"])
            out["margin"].append(m)
            out["correct"].append(m > 0.0)
            out["n_choices"].append(k)
            out["group"].append(r["group"])
        pos += k
    order = np.argsort(np.asarray(out["item_id"]), kind="stable")
    return {key: np.asarray(val)[order] for key, val in out.items()}


def gain(scores):
    """Mean per-byte log-likelihood over every choice, the paper's gain covariate."""
    return float(np.mean(scores["sum_logits"] / scores["num_bytes"]))
