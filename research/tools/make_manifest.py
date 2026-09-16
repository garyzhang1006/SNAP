"""Build research/manifest.csv, which maps every reduced run to its release identity and its bytes.

The run manifest from R4 carries the design facts, and this script joins three measured things onto
it. The branch name comes from the seed through the mapping that snap-r7-verify and snap-r7-verify-1b
confirmed by rescoring, the repository availability comes from the snap-r7-availability census, and the
hash and size come from the reduction file itself. Nothing here is asserted from memory.
"""
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "research/outputs/snap-r6-perm-seeds/runs"
CENSUS = ROOT / "research/outputs/snap-r7-availability/r7_availability.json"
SRC = ROOT / "research/R4_run_manifest.csv"
OUT = ROOT / "research/manifest.csv"

# Verified by rescoring 150 ARC-Easy documents per cell, 24 cells below 1B and 15 at 1B, no exception.
BRANCH = {("150M", "2"): "default", ("150M", "14"): "small-aux-2", ("150M", "15"): "small-aux-3",
          ("300M", "2"): "default", ("300M", "14"): "small-aux-2", ("300M", "15"): "small-aux-3",
          ("530M", "2"): "default", ("530M", "14"): "small-aux-2", ("530M", "15"): "small-aux-3",
          ("750M", "2"): "default", ("750M", "14"): "small-aux-2", ("750M", "15"): "small-aux-3",
          ("1B", "2"): "default", ("1B", "4"): "large-aux-2", ("1B", "5"): "large-aux-3"}

census = {}
for row in json.loads(CENSUS.read_text())["rows"]:
    census[(row["recipe"], row["size"])] = row["classification"]

rows = list(csv.DictReader(SRC.open()))
out_rows = []
for r in rows:
    npz = RUNS / f"{r['run_id']}.npz"
    data = npz.read_bytes()
    repo = f"allenai/DataDecide-{r['recipe']}-{r['size']}"
    out_rows.append({
        "config_id": r["config_id"], "recipe": r["recipe"], "size": r["size"],
        "run_id": r["run_id"], "seed": r["seed"], "selected_step": r["selected_step"],
        "schedule_label": r["schedule_label"],
        "hf_repo": repo,
        "hf_revision": f"step{r['selected_step']}-seed-{BRANCH[(r['size'], r['seed'])]}",
        "repo_access": census.get((r["recipe"], r["size"]), "not_in_census"),
        "reduction_file": f"{r['run_id']}.npz",
        "reduction_sha256": hashlib.sha256(data).hexdigest(),
        "reduction_bytes": len(data),
        "evidence": "OBSERVED for the hash, the size and the access code; "
                    "OBSERVED for the branch mapping through rescoring",
    })

with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
    w.writeheader()
    w.writerows(out_rows)
print(f"wrote {OUT} rows {len(out_rows)} "
      f"distinct_hashes {len({r['reduction_sha256'] for r in out_rows})} "
      f"access {sorted({r['repo_access'] for r in out_rows})}")
