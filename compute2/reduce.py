"""Turn score files into the seednoise reduced-run format.

  python reduce.py --job pythia_bank1_final
  python reduce.py --all

Reads scores/<job>/<run_key>.npz, checks each against the job's request file,
and writes reduced/<job>/<run_key>.npz with the keys seednoise.store.load_run
reads: item_id (int64), trait (int8), group (int16, the 66-task index),
margin (float16), correct (bit-packed), n_items, meta. The meta carries recipe,
size, seed, step, batch and gain as the adapter and build_population expect,
plus the family, bank, request hash and the hub commit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "common"))
import bank  # noqa: E402


def save_reduced(path, items, meta):
    with np.errstate(over="ignore"):
        m16 = items["margin"].astype(np.float16)
    if not np.isfinite(m16).all():
        raise ValueError(f"{path}: {int((~np.isfinite(m16)).sum())} margins overflow float16")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".partial.npz")
    np.savez_compressed(tmp, item_id=items["item_id"].astype(np.int64), trait=items["trait"].astype(np.int8),
                        group=items["group"].astype(np.int16), margin=m16,
                        correct=np.packbits(items["correct"]), n_items=np.int64(items["item_id"].size),
                        meta=json.dumps(meta))
    tmp.rename(path)


def reduce_job(name, scores_root, out_root, force=False):
    job = {j["name"]: j for j in bank.read_json(HERE / "config" / "jobs.json")["jobs"]}[name]
    req_path = HERE / "data" / f"{job['bank']}_requests.jsonl.gz"
    req_sha = bank.sha256(req_path)
    requests = bank.read_requests(req_path)
    if job.get("tasks"):
        requests = bank.select_tasks(requests, job["tasks"])
    src = Path(scores_root) / name
    files = sorted(src.glob("*.npz"))
    files = [f for f in files if not f.name.endswith(".partial.npz")]
    if not files:
        raise SystemExit(f"no score files under {src}")
    out_dir = Path(out_root) / name
    rows, skipped = [], 0
    for f in files:
        target = out_dir / f.name
        if target.exists() and not force:
            skipped += 1
            continue
        scores, meta = bank.load_scores(f, requests)
        if meta["requests_sha256"] != req_sha:
            raise SystemExit(f"{f}: scored on request hash {meta['requests_sha256']}, the bank now hashes to {req_sha}")
        if meta["bank"] != job["bank"] or meta["job"] != name:
            raise SystemExit(f"{f}: meta says job {meta['job']} on {meta['bank']}, expected {name} on {job['bank']}")
        items = bank.per_item(scores, requests, job["bank"])
        red = {"recipe": meta["recipe"], "size": meta["size"], "seed": int(meta["seed"]), "step": int(meta["step"]),
               "batch": int(meta["batch"]), "gain": bank.gain(scores), "n_items": int(items["item_id"].size),
               "family": meta["family"], "bank": job["bank"], "job": name, "repo": meta["repo"],
               "revision": meta["revision"], "hub_sha": meta["hub_sha"], "requests_sha256": req_sha,
               "tasks": job.get("tasks") or "all", "mode": meta["stats"]["mode"],
               "check_max_abs_diff_nats": meta["stats"]["check_max_abs_diff_nats"], "run_key": meta["run_key"]}
        save_reduced(target, items, red)
        rows.append(red)
    bank.write_json(out_dir / "reduce_manifest.json",
                    {"job": name, "bank": job["bank"], "requests_sha256": req_sha, "reduced": len(rows),
                     "already_present": skipped, "runs": rows})
    print(f"[reduce] {name}: {len(rows)} reduced, {skipped} already present, under {out_dir}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--scores", default=str(HERE / "scores"))
    ap.add_argument("--out", default=str(HERE / "reduced"))
    ap.add_argument("--force", action="store_true", help="rewrite files that already exist")
    args = ap.parse_args()
    if not args.job and not args.all:
        ap.error("pass --job NAME or --all")
    names = [args.job] if args.job else [j["name"] for j in bank.read_json(HERE / "config" / "jobs.json")["jobs"]]
    for name in names:
        if args.all and not (Path(args.scores) / name).exists():
            print(f"[reduce] {name}: no scores yet, skipped", flush=True)
            continue
        reduce_job(name, args.scores, args.out, force=args.force)


if __name__ == "__main__":
    main()
