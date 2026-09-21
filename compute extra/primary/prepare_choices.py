"""Tokenize explicit per-choice contexts. Reconcile this protocol with original code."""
import argparse
import json
from pathlib import Path

from snap.core import object_hash, require, sha256, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choices", required=True, help="JSONL, one row per answer choice")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--max-length", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    require(args.revision != "main", "Use immutable tokenizer revision")
    target = Path(args.out)
    require(not target.exists(), "Refusing to overwrite token records")
    target.parent.mkdir(parents=True, exist_ok=True)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, revision=args.revision, trust_remote_code=False)
    temp = target.with_name(target.name + ".tmp")
    seen, count = set(), 0
    with open(args.choices, encoding="utf-8") as source, open(temp, "w", encoding="utf-8") as output:
        for line in source:
            row = json.loads(line)
            key = [row["benchmark"], row["item_id"], row["choice_index"]]
            identity = object_hash(key)
            require(identity not in seen, f"Duplicate choice {key}")
            seen.add(identity)
            context, continuation = row["context"], row["continuation"]
            prefix = tokenizer.encode(context, add_special_tokens=False)
            ids = tokenizer.encode(context + continuation, add_special_tokens=False)
            require(prefix and len(ids) > len(prefix) and ids[:len(prefix)] == prefix,
                    f"Token boundary merges or empty context/answer for {key}; recover exact original boundary rule rather than silently retokenizing")
            require(len(ids) <= args.max_length, f"Overlength choice {key}; no silent truncation")
            require(row["normalizer"] > 0, "Supply positive normalizer, e.g. verified continuation bytes")
            record = {"id": identity, "input_ids": ids,
                      "target_mask": [False] * len(prefix) + [True] * (len(ids) - len(prefix)),
                      "metadata": {k: row[k] for k in ("benchmark", "item_id", "choice_index", "choice_count", "gold_index", "normalizer")}}
            output.write(json.dumps(record) + "\n")
            count += 1
    require(count > 0, "No input choices")
    temp.replace(target)
    write_json(str(target) + ".manifest.json", {"records_sha256": sha256(target), "expected_records": count,
               "source_sha256": sha256(args.choices), "tokenizer_id": args.tokenizer,
               "tokenizer_revision": args.revision, "max_length": args.max_length,
               "protocol": "Explicit context+continuation, no added special tokens, prefix-stable boundaries, supplied normalization"})


if __name__ == "__main__":
    main()
