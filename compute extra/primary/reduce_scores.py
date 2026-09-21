"""Reduce verified GPU shards into document losses or explicit choice margins."""
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from snap.core import object_hash, read_json, require, sha256, verify_artifacts, write_json


def load_rows(directories):
    seen = set()
    for directory in directories:
        directory = Path(directory)
        manifest = read_json(directory / "manifest.json")
        require(manifest["status"] == "FINISHED_UNCHECKED", f"Incomplete scoring output {directory}")
        require(manifest["job"] in ("G00", "G01", "G02", "G03"), "Not a GPU scoring job")
        verify_artifacts(directory, manifest)
        for name, digest in manifest["artifacts"].items():
            require(sha256(directory / name) == digest, f"Changed scoring artifact {name}")
            if not name.endswith(".json"):
                continue
            value = read_json(directory / name)
            if "rows_hash" not in value:
                continue
            require(object_hash(value["rows"]) == value["rows_hash"], "Shard content hash mismatch")
            for row in value["rows"]:
                key = (value["run_key"], row["id"])
                require(key not in seen, f"Duplicate scored record {key}")
                seen.add(key)
                yield value["run_key"], row


def reduce_documents(rows):
    groups = defaultdict(lambda: [0., 0])
    hashes = {}
    for run, row in rows:
        require(type(row["target_tokens"]) is int and row["target_tokens"] > 0,
                "Document target count must be a positive integer")
        require(np.isfinite(row["nll_sum"]) and row["nll_sum"] >= 0, "Invalid document negative log likelihood")
        document = row["metadata"]["document_id"]
        key = (run, document)
        digest = row["metadata"]["document_hash"]
        require(key not in hashes or hashes[key] == digest, "Document hash differs across windows")
        hashes[key] = digest
        groups[(run, document)][0] += row["nll_sum"]
        groups[(run, document)][1] += row["target_tokens"]
    return [{"run_key": run, "document_id": doc, "nll_sum": loss, "target_tokens": count,
             "mean_nll": loss / count, "document_hash": hashes[(run, doc)]}
            for (run, doc), (loss, count) in sorted(groups.items())]


def reduce_choices(rows):
    groups = defaultdict(list)
    for run, row in rows:
        require(np.isfinite(row["nll_sum"]) and row["nll_sum"] >= 0, "Invalid choice negative log likelihood")
        meta = row["metadata"]
        groups[(run, meta["benchmark"], meta["item_id"])].append(row)
    output = []
    for (run, benchmark, item), choices in sorted(groups.items()):
        meta = choices[0]["metadata"]
        n = meta["choice_count"]
        require(type(n) is int and n >= 2 and len(choices) == n, f"Incomplete choices for {run}/{item}")
        require({r["metadata"]["choice_index"] for r in choices} == set(range(n)), "Duplicate or missing option index")
        require(all(r["metadata"]["gold_index"] == meta["gold_index"] and r["metadata"]["choice_count"] == n for r in choices), "Inconsistent option metadata")
        gold = meta["gold_index"]
        require(type(gold) is int and 0 <= gold < n, "Invalid gold index")
        scores = np.empty(n)
        for row in choices:
            require(type(row["metadata"]["choice_index"]) is int, "Choice index must be an integer")
            normalizer = float(row["metadata"]["normalizer"])
            require(np.isfinite(normalizer) and normalizer > 0, "Each choice needs explicit positive normalizer")
            scores[row["metadata"]["choice_index"]] = -row["nll_sum"] / normalizer
        best = float(scores.max())
        tied = np.flatnonzero(scores == best)
        # This explicit tie rule is part of the reference protocol, not an original-code claim.
        predicted = int(tied[0])
        output.append({"run_key": run, "benchmark": benchmark, "item_id": item,
                       "margin": float(scores[gold] - np.max(np.delete(scores, gold))),
                       "accuracy": int(predicted == gold), "predicted": predicted,
                       "exact_tie": len(tied) > 1, "choice_scores": scores.tolist()})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["documents", "choices"])
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    require(not Path(args.out).exists(), "Refusing to overwrite reduction")
    rows = load_rows(args.runs)
    result = reduce_documents(rows) if args.kind == "documents" else reduce_choices(rows)
    require(result, "No reduced rows")
    write_json(args.out, {"schema": "snap-reduced-v1", "kind": args.kind, "rows": result,
                         "protocol": "Explicit normalization; choice tie selects smallest index; reconcile with source scorer"})


if __name__ == "__main__":
    main()
