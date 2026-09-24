"""CPU kernel: reduce the PolyPythias bank-one and bank-two score files and apply the frozen rules.

Runs compute2's own reduce.py and analysis/estimates.py at SNAP commit 6cfedee,
unchanged, on the staged score files. The attached datasets hold bank one and,
once it is scored, bank two, each staged by work/finalize/collect_scores.py
with its own MANIFEST.sha256. Bank two had no hash frozen before scoring, so the
rebuilt bank must match the 6,808 items the paper states, and reduce.py then
refuses any score file carrying a different request hash. Outputs land in
/kaggle/working/results: pythia.json, verdicts.json and RESULTS.md, which
fill_pending.py reads.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

COMMIT = "6cfedee87ac52695f96665ecc0a62ecdc97e1c35"
BANK1_SHA = "3130d19f88c2cb5dd040ff203200a9a3464e29b873635c1cd7768704b19fbcaf"
BANK2_ITEMS = 6808
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

# Each bank is its own dataset (snap-pythia-bank1-scores, snap-pythia-bank2-scores), since Kaggle flattens folders.
manifests = {m.parent.name.split("-")[2]: m for m in Path("/kaggle/input").rglob("MANIFEST.sha256")}
assert "bank1" in manifests and set(manifests) <= {"bank1", "bank2"}, manifests
banks = sorted(manifests)

# The request files reduce.py checks every score file against, rebuilt as the scoring kernels built them.
for b in banks:
    run("python", f"requests/build_{b}.py")
run("python", "requests/freeze.py")
frozen = json.loads((C2 / "config" / "frozen.json").read_text())["banks"]
assert frozen["bank1"]["sha256"] == BANK1_SHA, frozen["bank1"]
if "bank2" in banks:
    assert frozen["bank2"]["items"] == BANK2_ITEMS, frozen["bank2"]
    print("bank2 sha256", frozen["bank2"]["sha256"], flush=True)

for b in banks:
    src = manifests[b].parent
    dest = C2 / "scores" / f"pythia_{b}_final"
    dest.mkdir(parents=True, exist_ok=True)
    rows = [l.split() for l in manifests[b].read_text().splitlines() if l.strip()]
    assert len(rows) == 45, (b, len(rows))
    for digest, name in rows:
        got = sha256(src / name)
        assert got == digest, (b, name, got, digest)
        shutil.copy2(src / name, dest / name)
    print(f"{b}: 45 score files match MANIFEST.sha256", flush=True)
    run("python", "reduce.py", "--job", f"pythia_{b}_final")
OUT.mkdir(parents=True, exist_ok=True)
# No release runs are attached, so the verify and DataDecide arms report "not run"; rule one reads PolyPythias only.
run("python", "analysis/estimates.py", "--release-runs", "/nonexistent", "--out", OUT)
run("python", "analysis/report.py", "--results", OUT)
for b in banks:
    shutil.copy2(C2 / "reduced" / f"pythia_{b}_final" / "reduce_manifest.json", OUT / f"reduce_manifest_{b}.json")
print(json.dumps(json.loads((OUT / "verdicts.json").read_text()), indent=1), flush=True)
