"""Write the run manifests and the job list that score_runs.py executes.

  python make_manifests.py            # writes config/runs_pythia.json, runs_datadecide.json, jobs.json

DataDecide runs are the 375 rows of compute extra/config/runs.json (repo and
branch per run, verified by k01b and k03), with the model family added.
PolyPythias runs are EleutherAI/pythia-{size}-seed{k} for the five sizes and
seeds 1 to 9 at the final step 143000 and at five earlier steps that every
seed reached, so every configuration compares runs at exactly the same step of
the same schedule. The original Pythia run is not a replicate of that design
(it predates the PolyPythias training code), so it is off by default and
--include-original adds it as a tenth seed for a sensitivity arm only.

Jobs run in the listed order; each pairs a run subset with a request bank.
Verification comes first: bank-1 scores of six DataDecide runs must reproduce
the release's own per-item margins before any other result is read.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "common"))
import bank  # noqa: E402

PYTHIA_SIZES = ["14m", "31m", "70m", "160m", "410m"]
PYTHIA_SEEDS = list(range(1, 10))
PYTHIA_FINAL = 143000
PYTHIA_CURVE = [4000, 16000, 36000, 72000, 108000]
VERIFY_TASKS = ["arc_easy", "csqa", "openbookqa", "piqa", "winogrande"]


def pythia_rows(include_original):
    rows = []
    seeds = ([0] if include_original else []) + PYTHIA_SEEDS
    for size in PYTHIA_SIZES:
        for step in [PYTHIA_FINAL] + PYTHIA_CURVE:
            for i, seed in enumerate(seeds):
                repo = f"EleutherAI/pythia-{size}" if seed == 0 else f"EleutherAI/pythia-{size}-seed{seed}"
                rows.append({"run_key": f"polypythias__{size}__seed-{seed}__step-{step}", "family": "gptneox",
                             "recipe": "polypythias", "size": size, "seed": seed, "batch": i, "step": step,
                             "repo": repo, "revision": f"step{step}",
                             "allow_patterns": ["*.json", "*.bin", "*.safetensors", "*.txt"]})
    return rows


def datadecide_rows():
    src = bank.read_json(HERE.parent / "compute extra" / "config" / "runs.json")
    rows = []
    for r in src["runs"]:
        rows.append(dict(r, family="olmo", allow_patterns=["*.json", "*.safetensors"]))
    return rows, src


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--include-original", action="store_true")
    args = ap.parse_args()
    py = pythia_rows(args.include_original)
    dd, src = datadecide_rows()
    bank.write_json(HERE / "config" / "runs_pythia.json",
                    {"schema": "snap-compute2-runs-v1", "family": "gptneox", "n_runs": len(py),
                     "sizes": PYTHIA_SIZES, "seeds": ([0] if args.include_original else []) + PYTHIA_SEEDS,
                     "steps": [PYTHIA_FINAL] + PYTHIA_CURVE, "final_step": PYTHIA_FINAL,
                     "include_original": args.include_original, "runs": py})
    bank.write_json(HERE / "config" / "runs_datadecide.json",
                    {"schema": "snap-compute2-runs-v1", "family": "olmo", "n_runs": len(dd),
                     "source": "compute extra/config/runs.json", "source_schema": src.get("schema"),
                     "seed_branch_mapping": src.get("seed_branch_mapping"), "runs": dd})
    jobs = [
        {"name": "verify", "runs": "runs_datadecide.json", "bank": "bank1", "tasks": VERIFY_TASKS,
         "filter": {"recipe": ["c4"], "size": ["150M", "1B"]},
         "purpose": "bank-1 scores must reproduce the release's per-item margins (gate for everything below)"},
        {"name": "pythia_bank1_final", "runs": "runs_pythia.json", "bank": "bank1", "filter": {"step": [PYTHIA_FINAL]},
         "purpose": "replicate design, nine seeds per size at one step, the paper's exact items and prompts"},
        {"name": "pythia_bank2_final", "runs": "runs_pythia.json", "bank": "bank2", "filter": {"step": [PYTHIA_FINAL]},
         "purpose": "disjoint items on the same runs, for the cross-bank estimate"},
        {"name": "datadecide_bank2", "runs": "runs_datadecide.json", "bank": "bank2",
         "purpose": "disjoint items on all 375 DataDecide runs; bank 1 comes from the release"},
        {"name": "pythia_bank1_curve", "optional": True, "runs": "runs_pythia.json", "bank": "bank1", "filter": {"step": PYTHIA_CURVE},
         "purpose": "the inflation factor across training at exactly matched steps"},
        {"name": "pythia_bank2zs_final", "optional": True, "runs": "runs_pythia.json", "bank": "bank2zs", "filter": {"step": [PYTHIA_FINAL]},
         "purpose": "same disjoint items without exemplars, for the cross-format estimate"},
        {"name": "datadecide_bank2zs_1B", "optional": True, "runs": "runs_datadecide.json", "bank": "bank2zs", "filter": {"size": ["1B"]},
         "purpose": "cross-format estimate on the 1B band of DataDecide"},
    ]
    bank.write_json(HERE / "config" / "jobs.json", {"schema": "snap-compute2-jobs-v1", "jobs": jobs})
    print(json.dumps({"pythia_runs": len(py), "datadecide_runs": len(dd), "jobs": [j["name"] for j in jobs]}, indent=1))


if __name__ == "__main__":
    main()
