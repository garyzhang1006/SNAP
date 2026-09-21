#!/usr/bin/env bash
# Score one shard on the scu-gpu partition.
#
#   sbatch --export=ALL,SHARD=s01 "compute extra/run_shard.sbatch"
#   sbatch --export=ALL,SHARD=s01 --gres=gpu:l40s:2 "compute extra/run_shard.sbatch"   # two cards, twice as fast
#
# Defaults: one GPU of any type, 8 cores, 48 GB, 24 hours. The 20 one-billion
# parameter runs of a 1B shard took an estimated 12.3 card-hours on a Kaggle
# T4 (2,900 s of scoring per run in float32 at 6,000-token batches); an L40S
# should need a fraction of that, and the 24-hour request stays under the
# partition's two-day cap either way. The scorer refuses to start a run it
# cannot finish before the deadline, writes every finished run, and exits
# nonzero with the rest listed in shard_report_<SHARD>.json, so on a timeout
# resubmit the same line and it continues.
#
# Checkpoints stream into $TMPDIR (node-local, deleted with the job) and are
# removed run by run, so the job never holds more than one checkpoint per GPU.
# Scores go to $SNAPX_SCORES on the Lustre scratch.
#SBATCH --job-name=snapx
#SBATCH --partition=scu-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48000M
#SBATCH --time=1-00:00:00
#SBATCH --output=/athena/accardilab/scratch/%u/snap-extra/logs/%x-%j.out
set -euo pipefail
HERE="${SNAPX_DIR:-$SLURM_SUBMIT_DIR/compute extra}"
[ -f "$HERE/env.sh" ] || { echo "submit from the repository root or export SNAPX_DIR to the compute extra folder" >&2; exit 2; }
# shellcheck disable=SC1091
. "$HERE/env.sh"
: "${SHARD:?set SHARD, for example --export=ALL,SHARD=s01}"
[ -f "$HERE/shards/$SHARD.json" ] || { echo "no shards/$SHARD.json" >&2; exit 2; }

nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
python -c 'import torch; assert torch.cuda.is_available(), "no CUDA device visible"'
# Leave an hour of the requested time for the last run to save and for cleanup.
# squeue can time out against a busy controller or answer UNLIMITED; either
# falls back to the 24 hours this script requests instead of ending the job.
LIMIT_MIN=$( { squeue -h -j "$SLURM_JOB_ID" -o %l 2>/dev/null || true; } | awk -F'[-:]' '{ if (NF==4) print $1*1440+$2*60+$3; else if (NF==3) print $1*60+$2; else print $1 }')
case "$LIMIT_MIN" in ''|*[!0-9]*) LIMIT_MIN=1440 ;; esac
DEADLINE_H=$(python -c "print(max(1.0, $LIMIT_MIN/60 - 1))")
# Every run downloads its checkpoint from the hub, so a node without outbound
# network would fail all of them one by one; ask for the first run's revision
# here and stop with the reason if three tries a minute apart get no answer.
python - "$HERE/shards/$SHARD.json" <<'PY' || { echo "this node cannot reach huggingface.co, so no checkpoint can be downloaded; resubmit to land on another node, or ask whether scu-gpu nodes have outbound network" >&2; exit 3; }
import json, sys, time
from huggingface_hub import HfApi
run = json.load(open(sys.argv[1]))["runs"][0]
for attempt in range(3):
    try:
        print("[hub] reachable:", run["repo"], HfApi().model_info(run["repo"], revision=run["revision"]).sha, flush=True)
        break
    except Exception as e:
        print(f"[hub] try {attempt + 1} of 3 failed: {type(e).__name__}: {e}", flush=True)
        if attempt == 2:
            sys.exit(1)
        time.sleep(60)
PY
python "$HERE/score_shard.py" --shard "$HERE/shards/$SHARD.json" --out "$SNAPX_SCORES" \
    --tmp "${TMPDIR:-$SNAPX_ROOT/tmp}" --deadline-hours "$DEADLINE_H"
