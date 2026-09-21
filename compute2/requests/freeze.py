"""Record the request-bank hashes that score_runs.py refuses to score without.

  python requests/freeze.py

Writes config/frozen.json with the sha256 and item count of every bank file
under data/. Run it once after the banks are built and before any model is
scored; rebuilding a bank afterwards changes its hash and every score file
carrying the old hash stops being comparable, which reduce.py refuses.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import bank  # noqa: E402

BANKS = ("bank1", "bank2", "bank2zs")


def main():
    out = HERE.parent / "config" / "frozen.json"
    prev = bank.read_json(out) if out.exists() else {"banks": {}, "history": []}
    banks = {}
    for b in BANKS:
        path = HERE.parent / "data" / f"{b}_requests.jsonl.gz"
        if not path.exists():
            continue
        rows = bank.read_requests(path)
        n = bank.validate_requests(rows)
        banks[b] = {"sha256": bank.sha256(path), "items": n, "file": path.name}
        old = prev["banks"].get(b)
        if old and old["sha256"] != banks[b]["sha256"]:
            prev["history"].append({"bank": b, "superseded_sha256": old["sha256"], "at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            print(f"[freeze] {b}: hash changed from {old['sha256'][:12]}; score files on the old hash are void", flush=True)
    if not banks:
        raise SystemExit("no bank files under data/; build them first")
    bank.write_json(out, {"schema": "snap-compute2-frozen-v1", "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "banks": banks, "history": prev.get("history", [])})
    for b, v in banks.items():
        print(f"[freeze] {b}: {v['items']} items, sha256 {v['sha256']}", flush=True)


if __name__ == "__main__":
    main()
