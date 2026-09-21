"""Join reduced scores onto a frozen layout, rejecting every missing or extra key."""
import argparse
import copy
from pathlib import Path

import numpy as np

from snap.core import load_dataset, read_json, require, sha256, write_json


def pack(layout, rows, phenotype, out):
    require(phenotype in ("margin", "accuracy"), "Unknown phenotype")
    meta = copy.deepcopy(layout)
    out = Path(out)
    require(not out.exists(), "Use a new dataset output directory")
    runs = {}
    for i, c in enumerate(meta["configs"]):
        for j, r in enumerate(c["runs"]):
            require(r["run_key"] not in runs, "Duplicate global run_key in layout")
            runs[r["run_key"]] = (i, j)
    benchmarks = {b["name"]: b for b in meta["benchmarks"]}
    require(len(benchmarks) == len(meta["benchmarks"]), "Duplicate benchmark name")
    items = {name: {item: n for n, item in enumerate(b["item_ids"])} for name, b in benchmarks.items()}
    shape = (len(meta["configs"]), len(meta["configs"][0]["runs"]))
    arrays = {b["key"]: np.full((*shape, len(b["item_ids"])), np.nan) for b in benchmarks.values()}
    seen = set()
    for row in rows:
        key = (row["run_key"], row["benchmark"], row["item_id"])
        require(key not in seen, f"Duplicate score {key}")
        seen.add(key)
        require(key[0] in runs and key[1] in benchmarks and key[2] in items[key[1]], f"Unexpected score key {key}")
        i, j = runs[key[0]]
        arrays[benchmarks[key[1]]["key"]][i, j, items[key[1]][key[2]]] = row[phenotype]
    require(all(np.isfinite(x).all() for x in arrays.values()), "Missing or nonfinite scores; no incomplete dataset will be written")
    if phenotype == "accuracy":
        require(all(np.isin(x, [0, 1]).all() for x in arrays.values()), "Accuracy rows must be binary")
    out.mkdir(parents=True)
    np.savez_compressed(out / "scores.npz", **arrays)
    meta.update(schema="snap-scores-v1", phenotype=phenotype, arrays="scores.npz", arrays_sha256=sha256(out / "scores.npz"))
    write_json(out / "scores.json", meta)
    load_dataset(out / "scores.json")
    return out / "scores.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--rows", required=True, help="JSON produced by reduce_scores.py choices")
    parser.add_argument("--phenotype", required=True, choices=["margin", "accuracy"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    value = read_json(args.rows)
    require(value.get("kind") == "choices", "Expected choice reductions")
    print(pack(read_json(args.layout), value["rows"], args.phenotype, args.out))


if __name__ == "__main__":
    main()
