# Shared environment for compute2. Sourced by setup.sh and run_all.sh.
# Everything the jobs write goes under SNAP2_ROOT, which should sit on the
# box's NVMe; the Hugging Face cache goes there too so the root disk stays small.
export SNAP2_ROOT="${SNAP2_ROOT:-$HOME/snap2}"
export SNAP2_VENV="${SNAP2_VENV:-$SNAP2_ROOT/venv}"
export SNAP2_SCORES="${SNAP2_SCORES:-$SNAP2_ROOT/scores}"
export SNAP2_TMP="${SNAP2_TMP:-$SNAP2_ROOT/tmp}"
export HF_HOME="${HF_HOME:-$SNAP2_ROOT/hf}"
export HF_HUB_OFFLINE=0
export HF_HUB_DISABLE_PROGRESS_BARS=1
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
# A read token raises the anonymous rate limit; export HF_TOKEN yourself, no
# file under the repository ever holds one.
mkdir -p "$SNAP2_ROOT"/{scores,tmp,logs} "$HF_HOME"
if [ -f "$SNAP2_VENV/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$SNAP2_VENV/bin/activate"
fi
