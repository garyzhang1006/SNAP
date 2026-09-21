"""Turn a shard definition into a pushable Kaggle scoring kernel.

  python3 "compute extra/make_kaggle_shard.py" s03
  python3 "compute extra/make_kaggle_shard.py" s03 --slug snap-new-k02-s03-rerun
  python3 "compute extra/make_kaggle_shard.py" --list

This replaces cluster/submit.sh. The Slurm path is retired, so the shards under
shards/ now reach a GPU through Kaggle, which is the same route the finished
s01 and s02 took. Each shard file already carries the schema the k02 template
reads, which is name, runs, tasks, est_seconds and deadline_hours, and its
origin field records the Kaggle shard it was copied from.

The kernel itself is written by heldout/tools/make_shards.py, imported here by
path so the metadata stays single sourced. Kernels come out private, which the
project requires, because that flag lives in write_kernel.

Nothing here contacts Kaggle. Push what it writes with the Kaggle CLI, using
credentials from the environment rather than from any file in this repo.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARDS = HERE / "shards"
BUILD = HERE / "build"
MAKE_SHARDS = HERE / "heldout" / "tools" / "make_shards.py"


def load_make_shards():
    """Import the held-out package's shard writer so kernel metadata can't drift."""
    spec = importlib.util.spec_from_file_location("snap_make_shards", MAKE_SHARDS)
    if spec is None or spec.loader is None:
        sys.exit(f"cannot import {MAKE_SHARDS}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slug_for(shard, explicit):
    if explicit:
        return explicit
    origin = shard.get("origin", "")
    for word in origin.split():
        if word.startswith("snap-"):
            return word.rstrip(",")
    return f"snap-new-k02-{shard['name']}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shard", nargs="?", help="shard name, for example s03")
    ap.add_argument("--slug", help="kernel slug, defaults to the origin recorded in the shard")
    ap.add_argument("--list", action="store_true", help="list the shards and exit")
    args = ap.parse_args()

    available = sorted(p.stem for p in SHARDS.glob("*.json"))
    if args.list or not args.shard:
        for name in available:
            shard = json.loads((SHARDS / f"{name}.json").read_text())
            hours = sum(shard["est_seconds"].values()) / 3600
            print(f"{name:7} {len(shard['runs']):3d} runs  {hours:5.1f} GPU hours over two cards  "
                  f"deadline {shard['deadline_hours']}h  -> {slug_for(shard, None)}")
        return

    path = SHARDS / f"{args.shard}.json"
    if not path.exists():
        sys.exit(f"no {path}; available shards are {', '.join(available)}")
    shard = json.loads(path.read_text())
    slug = slug_for(shard, args.slug)

    mod = load_make_shards()
    d = mod.write_kernel(slug, shard, BUILD)
    meta = json.loads((d / "kernel-metadata.json").read_text())
    assert meta["is_private"] is True, "kernel metadata must stay private"

    hours = sum(shard["est_seconds"].values()) / 3600
    print(f"wrote {d}")
    print(f"  {len(shard['runs'])} runs, {shard['tasks']}, about {hours:.1f} GPU hours across two cards")
    print(f"  attaches {meta['dataset_sources']} and {meta['kernel_sources']}")
    print("push it with the Kaggle CLI, which reads its credentials from the environment:")
    print(f'  kaggle kernels push -p "{d}"')


main()
