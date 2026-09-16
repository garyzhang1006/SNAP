"""Build research/results/, the frozen tables every simulation claim in the paper reads from.

Two tables come out of this. simulation_cells.csv holds one row per kernel, cell and interval
construction for every result file that carries the standard coverage shape, with the unrounded
coverage, its Monte Carlo standard error, the exclusion rate, the undefined rate and the median width.
index.csv holds one row per result file with its hash, its size and the terminal state the monitor
recorded, so a reader can tell which bytes produced a number. Neither table recomputes an estimate.
"""
import csv, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "research/outputs"
STATUS = ROOT / "research/kernel_status.tsv"
DEST = ROOT / "research/results"
DEST.mkdir(exist_ok=True)

terminal = {}
if STATUS.exists():
    for line in STATUS.read_text(errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            terminal[parts[0]] = parts[1]

cell_rows, index_rows = [], []
for path in sorted(OUTPUTS.rglob("*.json")):
    if path.name.startswith("._"):
        continue
    # A kernel's working directory holds a vendored copy of the analysis package, whose own JSON
    # files are code rather than results, so they stay out of the index.
    if "seed-noise" in path.parts or "site-packages" in path.parts:
        continue
    raw = path.read_bytes()
    kernel = path.relative_to(OUTPUTS).parts[0]
    index_rows.append({"kernel": kernel, "file": str(path.relative_to(ROOT)),
                       "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                       "kernel_state": terminal.get(kernel, "not_recorded")})
    try:
        report = json.loads(raw)
    except ValueError:
        continue
    if not isinstance(report, dict):
        continue
    cells = report.get("cells")
    reps = report.get("reps")
    if not isinstance(cells, dict) or not isinstance(reps, int):
        continue
    for cell_name, cell in cells.items():
        if not isinstance(cell, dict):
            continue
        for method, body in cell.items():
            if not isinstance(body, dict) or "coverage" not in body:
                continue
            cov = body["coverage"]
            cell_rows.append({
                "kernel": kernel, "cell": cell_name, "method": method,
                "true_ratio": cell.get("truth", ""),
                "varied": json.dumps(cell.get("varied", {}), sort_keys=True,
                                     default=lambda o: "array"),
                "replicates": reps, "seed": report.get("seed", ""),
                "coverage": cov,
                "mc_se": body.get("mc_se", math.sqrt(cov * (1 - cov) / reps) if reps else ""),
                "excludes_one_rate": body.get("excludes_one_rate", ""),
                "undefined_or_unbounded": body.get("undefined_or_unbounded", ""),
                "median_width": body.get("median_width", ""),
                "interval_status": ("undefined_present"
                                    if body.get("undefined_or_unbounded") else "all_defined"),
            })

for name, rows in (("simulation_cells.csv", cell_rows), ("index.csv", index_rows)):
    with (DEST / name).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {DEST / name} rows {len(rows)}")
print(f"kernels with coverage cells {len({r['kernel'] for r in cell_rows})}, "
      f"result files indexed {len(index_rows)}")
