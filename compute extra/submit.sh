#!/usr/bin/env bash
# Submit one GPU job per shard and print the job ids.
#
#   bash "compute extra/submit.sh"                 # the remaining 1B shard, s03
#   bash "compute extra/submit.sh" s03             # one shard by name
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
for s in "${shards[@]}"; do
    [ -f "$HERE/shards/$s.json" ] || { echo "no shards/$s.json" >&2; exit 2; }
    # shellcheck disable=SC2086
    id=$(cd "$REPO" && sbatch --parsable --job-name="snapx-$s" --export=ALL,SHARD="$s",SNAPX_DIR="$HERE" ${SBATCH_EXTRA:-} "$HERE/run_shard.sbatch")
    echo "$s -> job $id"
done
echo "logs: /athena/accardilab/scratch/$USER/snap-extra/logs/   scores: \${SNAPX_SCORES:-/athena/accardilab/scratch/$USER/snap-extra/scores}"
