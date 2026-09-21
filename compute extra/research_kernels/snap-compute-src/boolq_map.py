"""Recover native ids for every DataDecide task and passage groups for BoolQ.

Streams one recipe tarball from the Hugging Face release, stops after the first
complete run, and records doc_id, native_id and label for each of the 66
prediction files. BoolQ is then joined to the official validation split by
native_id, and the join is verified by label agreement on every item, which is
the check that row order alone would not give. Only hashes of passage text are
written, never the text.

Usage: python boolq_map.py --out OUT_DIR [--recipe c4]
"""
import argparse
import hashlib
import io
import json
import re
import tarfile
import time
import unicodedata
from pathlib import Path

import requests

HF_REPO = "allenai/DataDecide-eval-instances"
ITEM_STRIDE = 10_000_000
MEMBER = re.compile(r"^(?P<recipe>[^/]+)/(?P<size>[^/]+)/seed-(?P<seed>\d+)/step-(?P<step>\d+)\.tar\.gz$")


def norm(text):
    return unicodedata.normalize("NFC", text).strip()


def h16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--recipe", default="c4")
    ap.add_argument("--max-bytes", type=int, default=3_000_000_000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    from huggingface_hub import HfApi
    api = HfApi()
    tree = [{"path": e.path, "size": getattr(e, "size", None)}
            for e in api.list_repo_tree(HF_REPO, repo_type="dataset", recursive=True)]
    (out / "hf_repo_tree.json").write_text(json.dumps(tree, indent=1))
    print(f"[map] {len(tree)} entries in {HF_REPO}; {time.time() - t0:.0f}s", flush=True)

    url = f"https://huggingface.co/datasets/{HF_REPO}/resolve/main/models/{args.recipe}.tar.gz"
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    raw = resp.raw
    raw.decode_content = False
    got = {"bytes": 0}

    class Counter(io.RawIOBase):
        def readable(self):
            return True

        def readinto(self, b):
            chunk = raw.read(len(b))
            got["bytes"] += len(chunk)
            if got["bytes"] > args.max_bytes:
                raise RuntimeError("exceeded max-bytes before finding a complete run")
            b[:len(chunk)] = chunk
            return len(chunk)

    tables, first_records, run = {}, {}, None
    with tarfile.open(fileobj=io.BufferedReader(Counter()), mode="r|gz") as tf:
        for m in tf:
            k = MEMBER.match(m.name)
            if k is None:
                continue
            run = k.groupdict()
            inner = tf.extractfile(m).read()
            with tarfile.open(fileobj=io.BytesIO(inner), mode="r:gz") as it:
                for im in it:
                    if not im.name.endswith("-predictions.jsonl"):
                        continue
                    task = im.name.rsplit("/", 1)[-1][: -len("-predictions.jsonl")]
                    rows = []
                    for line in it.extractfile(im).read().splitlines():
                        if not line.strip():
                            continue
                        r = json.loads(line)
                        if task not in first_records:
                            first_records[task] = {k2: (v if k2 != "model_output" else f"<{len(v)} choices>")
                                                   for k2, v in r.items()}
                        rows.append({"doc_id": r.get("doc_id"), "native_id": r.get("native_id"),
                                     "label": r.get("label"), "n_choices": len(r["model_output"])})
                    tables[task] = rows
            break
    print(f"[map] run {run} read from {got['bytes'] / 1e6:.0f} MB stream; {len(tables)} tasks; "
          f"{time.time() - t0:.0f}s", flush=True)
    (out / "task_native_ids.json").write_text(json.dumps({"run": run, "tables": tables}))
    (out / "first_records.json").write_text(json.dumps(first_records, indent=1, default=str))

    from datasets import load_dataset
    boolq = load_dataset("google/boolq", split="validation")
    rows = tables["boolq"]
    report = {"boolq_prediction_rows": len(rows), "boolq_validation_rows": len(boolq),
              "native_id_types": sorted({type(r["native_id"]).__name__ for r in rows}),
              "doc_id_equals_native_id": all(str(r["doc_id"]) == str(r["native_id"]) for r in rows)}
    labels_ok, unmatched, groups, passages = 0, [], {}, {}
    for r in rows:
        try:
            i = int(r["native_id"])
        except (TypeError, ValueError):
            unmatched.append(r["doc_id"])
            continue
        if not 0 <= i < len(boolq):
            unmatched.append(r["doc_id"])
            continue
        ex = boolq[i]
        if int(bool(ex["answer"])) == int(r["label"]):
            labels_ok += 1
        p = norm(ex["passage"])
        key = h16(p)
        passages.setdefault(key, {"n": 0, "chars": len(p)})
        passages[key]["n"] += 1
        groups[str(2 * ITEM_STRIDE + int(r["doc_id"]))] = key
    sizes = sorted(v["n"] for v in passages.values())
    report.update({"joined": len(groups), "unmatched": len(unmatched), "unmatched_examples": unmatched[:5],
                   "label_agreement": labels_ok, "label_agreement_fraction": labels_ok / max(1, len(groups)),
                   "unique_passages": len(passages),
                   "group_size_histogram": {str(s): sizes.count(s) for s in sorted(set(sizes))},
                   "max_group_size": max(sizes) if sizes else None,
                   "label_convention_check": "label 1 must correspond to answer True; if agreement is near 0 the convention is inverted, near 0.5 the join is wrong"})
    # Questions repeated verbatim on different passages are a second dependence channel.
    q = {}
    for r in rows:
        try:
            i = int(r["native_id"])
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(boolq):
            q.setdefault(h16(norm(boolq[i]["question"])), 0)
            q[h16(norm(boolq[i]["question"]))] += 1
    report["duplicate_question_texts"] = sum(1 for v in q.values() if v > 1)
    (out / "boolq_groups.json").write_text(json.dumps({"boolq": groups}))
    (out / "boolq_map_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1), flush=True)
    print(f"[map] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
