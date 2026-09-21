"""Prepare held-out documents for G01 using a frozen tokenizer and strided windows."""
import argparse
import json
from pathlib import Path

from snap.core import object_hash, require, sha256, write_json
from snap.gpu import token_windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents", required=True, help='JSONL rows with unique id and text')
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--max-length", type=int, required=True)
    parser.add_argument("--stride", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    require(args.revision != "main", "Use immutable tokenizer revision")
    target = Path(args.out)
    require(not target.exists(), "Output exists; choose a new path")
    target.parent.mkdir(parents=True, exist_ok=True)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, revision=args.revision, trust_remote_code=False)
    seen, records, tokens, doc_rows = set(), 0, 0, []
    temp = target.with_name(target.name + ".tmp")
    with open(args.documents, encoding="utf-8") as source, open(temp, "w", encoding="utf-8") as output:
        for line in source:
            row = json.loads(line)
            require(row["id"] not in seen and isinstance(row["text"], str), "Duplicate document or invalid text")
            seen.add(row["id"])
            ids = tokenizer.encode(row["text"], add_special_tokens=False)
            require(len(ids) >= 2, f"Document {row['id']} has fewer than two tokens; select corpus prospectively")
            count = 0
            for begin, part, mask in token_windows(ids, args.max_length, args.stride):
                record = {"id": object_hash([row["id"], begin]), "input_ids": part, "target_mask": mask,
                          "metadata": {"document_id": row["id"], "window_begin": begin,
                                       "document_hash": object_hash(row["text"])}}
                output.write(json.dumps(record) + "\n")
                records += 1
                count += sum(mask)
            require(count == len(ids) - 1, "Window target accounting failure")
            tokens += count
            doc_rows.append({"id": row["id"], "scored_tokens": count})
    require(records > 0, "Empty document corpus")
    temp.replace(target)
    write_json(str(target) + ".manifest.json", {"records_sha256": sha256(target), "expected_records": records,
               "source_sha256": sha256(args.documents), "tokenizer_id": args.tokenizer,
               "tokenizer_revision": args.revision, "max_length": args.max_length, "stride": args.stride,
               "documents": doc_rows, "scored_tokens": tokens,
               "protocol": "Documents separate, no special tokens, first token unscored; report token NLL, not bits per byte"})


if __name__ == "__main__":
    main()
