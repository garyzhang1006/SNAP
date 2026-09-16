"""Map held-out document losses into the keyed C06 proxy contract."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from snap.core import object_hash, read_json, require, sha256, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--losses", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--corpus", required=True, help="Original frozen document JSONL, hashed for provenance")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    require(not Path(args.out).exists(), "Use a new output path")
    value = read_json(args.losses)
    require(value.get("kind") == "documents", "Expected document reductions")
    corpus = {}
    with open(args.corpus, encoding="utf-8") as handle:
        for line in handle:
            document = json.loads(line)
            require(document["id"] not in corpus and isinstance(document["text"], str), "Invalid or duplicate corpus document")
            corpus[document["id"]] = object_hash(document["text"])
    require(corpus, "Empty corpus")
    groups = defaultdict(dict)
    for row in value["rows"]:
        require(row["document_id"] in corpus and row["document_hash"] == corpus[row["document_id"]],
                f"Document loss does not match supplied corpus: {row['document_id']}")
        require(type(row["target_tokens"]) is int and row["target_tokens"] > 0 and np.isfinite(row["nll_sum"]) and row["nll_sum"] >= 0,
                "Invalid loss or target count in document reduction")
        require(row["document_id"] not in groups[row["run_key"]], "Duplicate document reduction")
        groups[row["run_key"]][row["document_id"]] = row
    meta = read_json(args.dataset)
    result, reference = {}, None
    for c in meta["configs"]:
        result[c["id"]] = {}
        for r in c["runs"]:
            rows = groups[r["run_key"]]
            require(rows, f"Missing proxy run {r['run_key']}")
            require(set(rows) == set(corpus), f"Incomplete corpus coverage for {r['run_key']}")
            bank = sorted((key, row["document_hash"], row["target_tokens"]) for key, row in rows.items())
            if reference is None:
                reference = bank
            require(bank == reference, "Proxy runs differ in corpus or scored token counts; use a common tokenizer family and corpus")
            result[c["id"]][r["id"]] = sum(x["nll_sum"] for x in rows.values()) / sum(x["target_tokens"] for x in rows.values())
    write_json(args.out, {"schema": "snap-proxy-v1", "independent_corpus_hash": sha256(args.corpus),
               "values": result, "unit": "mean_token_nll", "independence_is_author_assertion": True})


if __name__ == "__main__":
    main()
