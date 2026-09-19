# Shared environment for the extra held-out scoring jobs on the SCU cluster.
# Sourced by run_shard.sbatch and setup.sh; nothing here submits a job.
# Follows slurm/env.sh: everything the jobs write goes under SNAPX_ROOT on the
# Lustre scratch, which both login and compute nodes mount, and the Hugging
# Face cache sits on scratch rather than the NFS home.

export SNAPX_ROOT="${SNAPX_ROOT:-/athena/accardilab/scratch/$USER/snap-extra}"
export SNAPX_VENV="${SNAPX_VENV:-$SNAPX_ROOT/venv}"
export SNAPX_SCORES="${SNAPX_SCORES:-$SNAPX_ROOT/scores}"
export HF_HOME="${HF_HOME:-/athena/accardilab/scratch/$USER/hf}"

# These jobs download each checkpoint from the hub as they go (20 checkpoints
# for the remaining 1B shard, deleted run by run), so the hub stays reachable.
# At most one download runs per GPU worker, which stayed under the anonymous
# rate limit on Kaggle. A read token raises that limit; put one in
# compute extra/hf_token (gitignored, chmod 600) or in $HF_HOME/token and the
# hub library picks it up. Every repo read is public, so none is required.
export HF_HUB_OFFLINE=0
export HF_HUB_DISABLE_PROGRESS_BARS=1
_SNAPX_TOKEN="$(dirname "${BASH_SOURCE[0]}")/hf_token"
if [ -z "${HF_TOKEN:-}" ] && [ -f "$_SNAPX_TOKEN" ]; then
    HF_TOKEN="$(tr -d '[:space:]' < "$_SNAPX_TOKEN")"
    export HF_TOKEN
fi
unset _SNAPX_TOKEN

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

mkdir -p "$SNAPX_ROOT"/{scores,logs} "$HF_HOME"

if [ -f "$SNAPX_VENV/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$SNAPX_VENV/bin/activate"
else
    echo "no virtualenv at $SNAPX_VENV; run bash \"compute extra/setup.sh\" first" >&2
    exit 2
fi
# The login nodes' system python is 3.6.8 and transformers 4.57 needs 3.9.
python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || {
    echo "python in $SNAPX_VENV is $(python --version 2>&1); needs >= 3.9. Rebuild with setup.sh (it builds inside an scu-cpu job)" >&2
    exit 2
}
