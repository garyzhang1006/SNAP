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
LIMIT_MIN=$(squeue -h -j "$SLURM_JOB_ID" -o %l | awk -F'[-:]' '{ if (NF==4) print $1*1440+$2*60+$3; else if (NF==3) print $1*60+$2; else print $1 }')
DEADLINE_H=$(python -c "print(max(1.0, ${LIMIT_MIN:-1440}/60 - 1))")
python "$HERE/score_shard.py" --shard "$HERE/shards/$SHARD.json" --out "$SNAPX_SCORES" \
    --tmp "${TMPDIR:-$SNAPX_ROOT/tmp}" --deadline-hours "$DEADLINE_H"
