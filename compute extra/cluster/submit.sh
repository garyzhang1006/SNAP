#!/usr/bin/env bash
# Submit one GPU job per shard and print the job ids.
#
#   bash "compute extra/cluster/submit.sh"             # the remaining 1B shard, s03
#   bash "compute extra/cluster/submit.sh" s03         # one shard by name
#   bash "compute extra/submit.sh" --extras        # the five exploratory two-task shards x150M .. x1B
#   SBATCH_EXTRA="--gres=gpu:l40s:2" bash "compute extra/submit.sh"   # pass sbatch options through
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
shards=("$@")
if [ "${1:-}" = "--extras" ]; then
    shards=(x150M x300M x530M x750M x1B)
elif [ ${#shards[@]} -eq 0 ]; then
    shards=(s03)
fi
ROOT="${SNAPX_ROOT:-/athena/accardilab/scratch/$USER/snap-extra}"
[ -f "${SNAPX_VENV:-$ROOT/venv}/bin/activate" ] || { echo "no virtualenv under $ROOT; run bash \"compute extra/setup.sh\" first" >&2; exit 2; }
for s in "${shards[@]}"; do
    [ -f "$HERE/shards/$s.json" ] || { echo "no shards/$s.json" >&2; exit 2; }
done
# Slurm ends a job at once, with no log, when the --output directory is missing.
mkdir -p "$ROOT/logs" "${SNAPX_SCORES:-$ROOT/scores}"
for s in "${shards[@]}"; do
    # SHARD and SNAPX_DIR travel in the environment rather than in the --export
    # string, because this folder's path has a space in it.
    # shellcheck disable=SC2086
    id=$(cd "$REPO" && SHARD="$s" SNAPX_DIR="$HERE" sbatch --parsable --job-name="snapx-$s" --export=ALL \
        --output="$ROOT/logs/%x-%j.out" ${SBATCH_EXTRA:-} "$HERE/run_shard.sbatch" | cut -d';' -f1)
    echo "$s -> job $id"
done
echo "logs: $ROOT/logs/   scores: ${SNAPX_SCORES:-$ROOT/scores}"
