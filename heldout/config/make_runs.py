"""Build config/runs.json, the frozen table of the 375 checkpoints to score.

Every row comes from the paper's own reduction manifests
(research/outputs/snap-r22-prev-step-*/prev_manifest_*.json), so the new scores
land on exactly the recipe, size, seed and checkpoint step the published
estimates used. The only new facts are the Hugging Face repository and branch
for each run, and both are checked against the hub before the table is written.

Two mappings are needed and neither is published as a table.

Repository names. The eval-instances release names recipes one way
("falcon-with-cc-top-orig-10p", "dolma1.6++") and the model repositories another
("falcon-and-cc-qc-orig-10p", "dolma1_6plus"). The census behind the paper's
"80 of 125 repositories refuse unauthenticated requests" built repository names
from the release spelling, and those names don't exist, so the 401s were wrong
names and not access control. REPO_NAME below uses the names that allenai's own
signal-and-noise release records in its model_path column, and every one of
the 125 resolves anonymously.

Seed branches. The release numbers seeds 2, 14, 15 below 1B and 2, 4, 5 at 1B,
while the model repositories label branches "default", "small-aux-2",
"small-aux-3", "large-aux-2" and "large-aux-3". Seed 2 is the default run
(seednoise.data.datadecide.batch_labels). The auxiliary assignment below is
ASSUMED from the numbering, because branch step lists can't tell aux-2 from
aux-3. kaggle/k03-verify-release tests it by comparing ARC-Easy scores from the
hub checkpoints with the released per-item scores, and the analysis refuses to
run until that check passes.

Usage (network only, no model download):
    python3 config/make_runs.py --manifests ../research/outputs --out config/runs.json
"""
import argparse
import glob
import json
import urllib.request
from pathlib import Path

REPO_NAME = {
    "c4": "c4",
    "dclm-baseline": "dclm-baseline",
    "dclm-baseline-25p-dolma1.7-75p": "dclm-baseline-25p-dolma1.7-75p",
    "dclm-baseline-50p-dolma1.7-50p": "dclm-baseline-50p-dolma1.7-50p",
    "dclm-baseline-75p-dolma1.7-25p": "dclm-baseline-75p-dolma1.7-25p",
    "dclm-baseline-top-10p": "dclm-baseline-qc-10p",
    "dclm-baseline-top-20p": "dclm-baseline-qc-20p",
    "dclm-baseline-top-fw-10p": "dclm-baseline-qc-fw-10p",
    "dclm-baseline-top-fw-3p": "dclm-baseline-qc-fw-3p",
    "dclm-baseline-top-fw2-7p": "dclm-baseline-qc-7p-fw2",
    "dclm-baseline-top-fw3-7p": "dclm-baseline-qc-7p-fw3",
    "dolma1.6++": "dolma1_6plus",
    "dolma1.7": "dolma1_7",
    "dolma1.7-no-code": "dolma1_7-no-code",
    "dolma1.7-no-flan": "dolma1_7-no-flan",
    "dolma1.7-no-math-no-code": "dolma1_7-no-math-code",
    "dolma1.7-no-reddit": "dolma1_7-no-reddit",
    "falcon": "falcon",
    "falcon-with-cc": "falcon-and-cc",
    "falcon-with-cc-top-10p": "falcon-and-cc-qc-10p",
    "falcon-with-cc-top-20p": "falcon-and-cc-qc-20p",
    "falcon-with-cc-top-orig-10p": "falcon-and-cc-qc-orig-10p",
    "falcon-with-cc-top-tulu-10p": "falcon-and-cc-qc-tulu-10p",
    "fineweb-edu": "fineweb-edu",
    "fineweb-pro": "fineweb-pro",
}

# ASSUMED, verified by k03 before any analysis (see module docstring).
SEED_BRANCH = {2: "default", 14: "small-aux-2", 15: "small-aux-3", 4: "large-aux-2", 5: "large-aux-3"}
SIZES = ["150M", "300M", "530M", "750M", "1B"]


def hub_branches(repo):
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/refs", timeout=60) as r:
        return {b["name"] for b in json.load(r)["branches"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifests", required=True, help="directory holding snap-r22-prev-step-*/prev_manifest_*.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    files = sorted(glob.glob(f"{args.manifests}/snap-r22-prev-step-*/prev_manifest_*.json"))
    assert len(files) == 5, f"expected 5 manifests, found {len(files)}: {files}"
    rows, problems = [], []
    for f in files:
        m = json.load(open(f))
        assert not m.get("failures"), f"{f} records failed recipes {m['failures']}"
        for recipe, v in m["recipes"].items():
            for size, cell in v["cells"].items():
                if size not in SIZES:
                    continue
                repo = f"allenai/DataDecide-{REPO_NAME[recipe]}-{size}"
                branches = hub_branches(repo)
                batch = {2: 0}
                for i, s in enumerate(sorted(x for x in cell["seeds"] if x != 2), start=1):
                    batch[s] = i
                for seed in cell["seeds"]:
                    branch = f"step{cell['common_step']}-seed-{SEED_BRANCH[seed]}"
                    if branch not in branches:
                        problems.append(f"{repo}@{branch} missing")
                    rows.append({"run_key": f"{recipe}__{size}__seed-{seed}__step-{cell['common_step']}",
                                 "recipe": recipe, "release_recipe": v.get("member_recipe") or v["runs"][0]["recipe"], "size": size,
                                 "seed": seed, "batch": batch[seed], "step": cell["common_step"],
                                 "repo": repo, "revision": branch})
    assert not problems, "branches missing on the hub:\n" + "\n".join(problems)
    cells = {(r["recipe"], r["size"]) for r in rows}
    assert len(rows) == 375 and len(cells) == 125, f"{len(rows)} runs over {len(cells)} configurations"
    rows.sort(key=lambda r: (SIZES.index(r["size"]), r["recipe"], r["batch"]))
    out = {"schema": "snap-new-runs-v1", "n_runs": len(rows), "n_configs": len(cells),
           "source": [str(Path(f).name) for f in files],
           "seed_branch_mapping": {str(k): v for k, v in SEED_BRANCH.items()},
           "seed_branch_mapping_status": "ASSUMED until k03-verify-release passes",
           "runs": rows}
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"wrote {len(rows)} runs over {len(cells)} configurations to {args.out}")


if __name__ == "__main__":
    main()
