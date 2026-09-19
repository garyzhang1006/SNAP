"""Pack the anonymized supplement zip the paper promises.

  python3 tools/make_supplement.py [--out deliverables/SNAP_supplement.zip]

Two trees go in: this folder as heldout/ (protocol, amendments, wording, kernels,
configs, tools and the kernel outputs the paper cites) and deliverables/snap_compute
as snap_compute/ (the primary reduction). Text files are rewritten so the Kaggle
handle and local paths never reach reviewers, and the zip is scanned afterwards;
any surviving identity string fails the build. Nothing here contacts Kaggle or
runs models. Rerun after the 750M shards and the 530M+750M analysis land.
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parent
HANDLE = "garyzhang11111"
# Strings that must not survive. The email is the user's OpenReview login and
# the home path names the author, so both are scrubbed before the zip is scanned.
IDENTITY = [HANDLE, "/Users/garyzhang", "jakobingerbrigsten", "Gary Zhang"]
REPLACEMENTS = [
    (HANDLE, "anonymous"),
    ("/Users/garyzhang/Documents/ChatGPT/iclr main track", "<repo>"),
    ("/Users/garyzhang", "<home>"),
]
SKIP_DIRS = {"__pycache__", "_stage", ".git", ".pytest_cache"}
# The packer names the strings it scrubs, so it stays out of its own zip.
SKIP_FILES = {"research_queue_watch.log", ".DS_Store", "make_supplement.py"}
TEXT_SUFFIXES = {".py", ".json", ".md", ".txt", ".sh", ".log", ".csv", ".tex", ".jsonl", ".yaml", ".yml", ".cfg", ".toml"}


def wanted(p: Path) -> bool:
    if any(part in SKIP_DIRS or part.startswith("._") for part in p.parts):
        return False
    return p.name not in SKIP_FILES and not p.name.startswith(".")


def rewrite(data: bytes, suffix: str) -> bytes:
    if suffix not in TEXT_SUFFIXES:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text.encode("utf-8")


def add_tree(zf: zipfile.ZipFile, src: Path, prefix: str) -> int:
    n = 0
    for p in sorted(src.rglob("*")):
        if not p.is_file() or not wanted(p.relative_to(src)):
            continue
        zf.writestr(f"{prefix}/{p.relative_to(src).as_posix()}", rewrite(p.read_bytes(), p.suffix))
        n += 1
    return n


def scan(zip_path: Path) -> list:
    hits = []
    pat = re.compile("|".join(re.escape(s) for s in IDENTITY).encode())
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if pat.search(info.filename.encode()):
                hits.append(f"{info.filename} (name)")
            if Path(info.filename).suffix in TEXT_SUFFIXES and pat.search(zf.read(info)):
                hits.append(info.filename)
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "deliverables" / "SNAP_supplement.zip"))
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        n_new = add_tree(zf, HERE, "heldout")
        n_old = add_tree(zf, ROOT / "deliverables" / "snap_compute", "snap_compute")
    hits = scan(out)
    size_mb = out.stat().st_size / 1e6
    print(f"{out} : heldout {n_new} files, snap_compute {n_old} files, {size_mb:.1f} MB")
    if hits:
        print("identity strings survived in:", *hits, sep="\n  ")
        out.unlink()
        sys.exit(1)
    print("identity scan clean")


if __name__ == "__main__":
    main()
