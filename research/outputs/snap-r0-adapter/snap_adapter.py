"""Convert seednoise reduced runs (npz) into snap-scores-v1 datasets.

The conversion reuses the original package for the frozen item split so that
C01 in split_mode "original" is scored on exactly the halves the original
pipeline used. MMLU keeps its 57 subjects as strata with equal weights, which
is the macro-average the original half_scores implements.

Usage: python snap_adapter.py --runs RUNS_DIR --out OUT_DIR [--groups GROUPS_JSON]

GROUPS_JSON, when given, maps benchmark name to {item_id: group_id} and is
merged into the manifest as group_ids for that benchmark; every other benchmark
gets its item id as its own group.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from seednoise.data.datadecide import TASKS, TRAITS
from seednoise.halves import MASTER_SEED, split_items
from seednoise.store import load_run

TRAIT_FORMAT = {"arc_challenge": "mc", "arc_easy": "mc", "boolq": "yesno", "csqa": "mc",
                "hellaswag": "cloze", "mmlu": "mc", "openbookqa": "mc", "piqa": "cloze",
                "socialiqa": "mc", "winogrande": "cloze"}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--groups", default=None)
    ap.add_argument("--split-seed", type=int, default=MASTER_SEED)
    args = ap.parse_args()
    files = sorted(Path(args.runs).glob("*.npz"))
    assert files, f"no npz runs under {args.runs}"
    K = len(TRAITS)
    runs, ref = [], None
    for f in files:
        items, meta = load_run(f)
        if ref is None:
            ref = items
        else:
            assert np.array_equal(items.item_id, ref.item_id), f.name
            assert np.array_equal(items.trait, ref.trait), f.name
            assert np.array_equal(items.group, ref.group), f.name
        runs.append((items, meta, f.name))
    mask = split_items(ref.trait, K, seed=args.split_seed)
    cells = {}
    for items, meta, name in runs:
        cells.setdefault((meta["recipe"], meta["size"]), []).append((meta, items, name))
    order = sorted(cells)
    n_runs = {len(v) for v in cells.values()}
    assert n_runs == {3}, f"run counts per cell {n_runs}"
    configs = []
    for recipe, size in order:
        rows = sorted(cells[(recipe, size)], key=lambda t: t[0]["batch"])
        cfg = {"id": f"{recipe}__{size}", "recipe": recipe, "size": size, "runs": []}
        for meta, _, name in rows:
            run_id = name[:-4]
            schedule = "default" if meta["batch"] == 0 else "auxiliary"
            cfg["runs"].append({"id": run_id, "run_key": run_id, "seed": meta["seed"],
                                "batch": meta["batch"], "checkpoint_step": meta["step"],
                                "gain": meta["gain"],
                                "training_signature": f"{recipe}/{size}/step={meta['step']}/schedule={schedule}",
                                "signature_basis": "REPORTED design facts, not a verified run manifest"})
        configs.append(cfg)
    groups = json.load(open(args.groups)) if args.groups else {}
    benchmarks = []
    per_trait_idx = []
    for j, name in enumerate(TRAITS):
        idx = np.flatnonzero(ref.trait == j)
        per_trait_idx.append(idx)
        ids = [str(int(i)) for i in ref.item_id[idx]]
        b = {"name": name, "key": f"b{j}", "format": TRAIT_FORMAT[name], "item_ids": ids,
             "original_half": [0 if mask[i] else 1 for i in idx]}
        if name == "mmlu":
            subjects = [TASKS[int(g)] for g in ref.group[idx]]
            b["strata"] = subjects
            labels = sorted(set(subjects))
            b["stratum_weights"] = {s: 1.0 / len(labels) for s in labels}
        if name in groups:
            g = groups[name]
            missing = [i for i in ids if i not in g]
            assert not missing, f"{name}: {len(missing)} items without a group, first {missing[:3]}"
            b["group_ids"] = [str(g[i]) for i in ids]
        else:
            b["group_ids"] = list(ids)
        benchmarks.append(b)
    layout = {"configs": configs, "benchmarks": benchmarks, "weights": [1.0 / K] * K,
              "split_seed_original": int(args.split_seed),
              "source": "seednoise reduced runs, 375 npz, split_items master seed",
              "run_files": [name for _, _, name in runs]}
    out = Path(args.out)
    written = {}
    for phenotype in ("margin", "accuracy"):
        d = out / phenotype
        d.mkdir(parents=True, exist_ok=True)
        arrays = {}
        for j, b in enumerate(benchmarks):
            idx = per_trait_idx[j]
            x = np.zeros((len(configs), 3, idx.size), dtype=np.float64)
            for ci, (recipe, size) in enumerate(order):
                rows = sorted(cells[(recipe, size)], key=lambda t: t[0]["batch"])
                for ri, (_, items, _) in enumerate(rows):
                    x[ci, ri] = items.margin[idx] if phenotype == "margin" else items.correct[idx].astype(np.float64)
            arrays[b["key"]] = x
        np.savez_compressed(d / "scores.npz", **arrays)
        meta = dict(layout)
        meta.update(schema="snap-scores-v1", phenotype=phenotype, arrays="scores.npz",
                    arrays_sha256=sha256(d / "scores.npz"))
        (d / "scores.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
        written[phenotype] = str(d / "scores.json")
    summary = {"configs": len(configs), "runs": len(runs), "items": int(ref.n_items),
               "half_A": int(mask.sum()), "half_B": int((~mask).sum()),
               "items_per_trait": {TRAITS[j]: int(per_trait_idx[j].size) for j in range(K)},
               "written": written}
    (out / "adapter_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
