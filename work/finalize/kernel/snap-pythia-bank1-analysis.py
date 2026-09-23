"""CPU kernel: reduce the 45 PolyPythias bank-one score files and apply the frozen rules.

Runs compute2's own reduce.py and analysis/estimates.py at SNAP commit 6cfedee,
unchanged, on the staged score files (dataset snap-pythia-bank1-scores, built by
work/finalize/collect_scores.py). Outputs land in /kaggle/working/results:
pythia.json, verdicts.json and RESULTS.md, which fill_pending.py reads.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

COMMIT = "6cfedee87ac52695f96665ecc0a62ecdc97e1c35"
BANK1_SHA = "3130d19f88c2cb5dd040ff203200a9a3464e29b873635c1cd7768704b19fbcaf"
REPO = Path("/tmp/SNAP")
C2 = REPO / "compute2"
OUT = Path("/kaggle/working/results")


def run(*args, cwd=C2):
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run([str(a) for a in args], check=True, cwd=cwd)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


run("git", "clone", "-q", "https://github.com/garyzhang1006/SNAP.git", REPO, cwd=Path("/tmp"))
run("git", "-C", REPO, "checkout", "-q", COMMIT, cwd=Path("/tmp"))
head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == COMMIT, head

# The request file reduce.py checks every score file against, rebuilt as the scoring kernels built it.
run("python", "requests/build_bank1.py")
run("python", "requests/freeze.py")
frozen = json.loads((C2 / "config" / "frozen.json").read_text())["banks"]
assert frozen["bank1"]["sha256"] == BANK1_SHA, frozen["bank1"]

manifests = list(Path("/kaggle/input").rglob("MANIFEST.sha256"))
assert len(manifests) == 1, manifests
src = manifests[0].parent
dest = C2 / "scores" / "pythia_bank1_final"
dest.mkdir(parents=True, exist_ok=True)
rows = [l.split() for l in manifests[0].read_text().splitlines() if l.strip()]
assert len(rows) == 45, len(rows)
for digest, name in rows:
    got = sha256(src / name)
    assert got == digest, (name, got, digest)
    shutil.copy2(src / name, dest / name)
print("45 score files match MANIFEST.sha256", flush=True)

run("python", "reduce.py", "--job", "pythia_bank1_final")
OUT.mkdir(parents=True, exist_ok=True)
# No release runs are attached, so the verify and DataDecide arms report "not run"; rule one reads PolyPythias only.
run("python", "analysis/estimates.py", "--release-runs", "/nonexistent", "--out", OUT)
run("python", "analysis/report.py", "--results", OUT)
shutil.copy2(C2 / "reduced" / "pythia_bank1_final" / "reduce_manifest.json", OUT / "reduce_manifest.json")
print(json.dumps(json.loads((OUT / "verdicts.json").read_text()), indent=1), flush=True)
