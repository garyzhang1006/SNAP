"""Build research/items.csv, which maps every scored item to its benchmark, task and dependence group.

The benchmark and task indices come out of a reduction file, which carries them for all 37,682 items,
and the BoolQ passage identifiers come from the map that snap-r2-boolq-map built against the release's
own request records. Items outside BoolQ have no measured dependence group, and this table says so
rather than inventing one.
"""
import csv, json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "research/outputs/snap-r6-perm-seeds/runs/dclm-baseline__150M__seed-2__step-37500.npz"
BOOLQ = ROOT / "research/outputs/snap-r2-boolq-map/boolq_map/boolq_groups.json"
OUT = ROOT / "research/items.csv"
TRAITS = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu", "openbookqa",
          "piqa", "socialiqa", "winogrande"]

z = np.load(RUN, allow_pickle=True)
item_id, trait, group = z["item_id"], z["trait"], z["group"]
n = int(z["n_items"])
assert item_id.size == trait.size == group.size == n == 37682, (item_id.size, n)
assert int(trait.max()) + 1 == len(TRAITS), trait.max()

passages = json.loads(BOOLQ.read_text())["boolq"]
boolq_index = TRAITS.index("boolq")
seen = 0
with OUT.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["item_id", "trait_index", "trait_name", "task_index",
                "dependence_group", "dependence_group_source"])
    for i in range(n):
        tid, t, g = int(item_id[i]), int(trait[i]), int(group[i])
        key = str(tid)
        if t == boolq_index and key in passages:
            seen += 1
            w.writerow([tid, t, TRAITS[t], g, passages[key], "boolq_passage_hash"])
        else:
            w.writerow([tid, t, TRAITS[t], g, "", "none_measured"])

counts = {TRAITS[t]: int((trait == t).sum()) for t in range(len(TRAITS))}
print(f"wrote {OUT} rows {n} tasks {int(group.max()) + 1}")
print(f"boolq items with a passage group {seen} of {counts['boolq']}, "
      f"distinct passages {len(set(passages.values()))}")
print(f"items per benchmark {counts}")
