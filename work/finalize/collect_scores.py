"""Gather the 45 PolyPythias bank-one score files into one folder for the analysis kernel.

  python work/finalize/collect_scores.py --out <staging dir> <source dir> [<source dir> ...]

Each source is searched recursively for polypythias__<size>__seed-<n>__step-143000.npz.
The script copies files only; it never opens them. It refuses to stage anything
unless the set is exactly five sizes by nine seeds, and it refuses a run key that
appears in two sources with different bytes. It writes MANIFEST.sha256 beside
the files so the kernel can check what it received.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path

SIZES = ["14m", "31m", "70m", "160m", "410m"]
SEEDS = list(range(1, 10))
NAME = re.compile(r"^polypythias__(\d+m)__seed-(\d+)__step-143000\.npz$")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("sources", nargs="+")
    args = ap.parse_args()
    found = {}
    for src in args.sources:
        for p in sorted(Path(src).rglob("*.npz")):
            m = NAME.match(p.name)
            if not m:
                continue
            key = (m.group(1), int(m.group(2)))
            digest = sha256(p)
            if key in found and found[key][1] != digest:
                raise SystemExit(f"{p.name} appears in {found[key][0]} and {p} with different contents; resolve before staging")
            found.setdefault(key, (p, digest))
    want = {(s, n) for s in SIZES for n in SEEDS}
    missing, extra = sorted(want - set(found)), sorted(set(found) - want)
    print(f"found {len(found)} of {len(want)} run keys")
    if missing or extra:
        raise SystemExit(f"not staged: missing {missing}, unexpected {extra}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lines = []
    for key in sorted(found, key=lambda k: (SIZES.index(k[0]), k[1])):
        p, digest = found[key]
        shutil.copy2(p, out / p.name)
        lines.append(f"{digest}  {p.name}")
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print(f"staged 45 files and MANIFEST.sha256 in {out}")


if __name__ == "__main__":
    main()
