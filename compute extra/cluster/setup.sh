#!/usr/bin/env bash
# One-off install for the extra scoring jobs. Creates the virtualenv on scratch,
# installs the pinned scoring stack, checks that the OLMo loader imports, and
# dry-runs the first shard against the frozen request file.
#
#   bash "compute extra/setup.sh"
#
# As in slurm/setup.sh, the login nodes' python is 3.6.8, so when the python
# found here is too old the script hands itself to an scu-cpu job with srun and
# builds the venv there. The torch wheel carries its own CUDA runtime, so no
# cuda module is loaded here or in the jobs.
#
# The install lines mirror heldout/kaggle/k02-score/k02-score-template.py:
# transformers at the pin that k00 measured against ai2-olmo 0.6.0, and
# ai2-olmo itself without its dependency pins. On Kaggle the image supplied
# olmo's transitive imports; here they are installed by name. The list was read
# off the v0.6.0 source: importing hf_olmo pulls in olmo.util, which imports
# datasets, boto3, cached_path, google.api_core, requests and rich, and
# olmo_data, which imports importlib_resources. The import check below names
# anything still missing.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export SNAPX_ROOT="${SNAPX_ROOT:-/athena/accardilab/scratch/$USER/snap-extra}"
export SNAPX_VENV="${SNAPX_VENV:-$SNAPX_ROOT/venv}"
mkdir -p "$SNAPX_ROOT"/{scores,logs}

py_ok() { "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; }

if [ -z "${SLURM_JOB_ID:-}" ] && ! py_ok python3; then
    if ! command -v srun >/dev/null; then
        echo "python3 here is $(python3 --version 2>&1) and there is no srun; install with a python >= 3.9" >&2
        exit 1
    fi
    echo "python3 on this node is $(python3 --version 2>&1); building the venv inside an scu-cpu job"
    exec srun --partition=scu-cpu --cpus-per-task=2 --mem=16000M --time=02:00:00 \
        --job-name=snapx-setup --export=ALL bash "$HERE/setup.sh"
fi
py_ok python3 || { echo "python3 is $(python3 --version 2>&1) even on the compute node; load a python >= 3.9 module" >&2; exit 1; }

if [ ! -f "$SNAPX_VENV/bin/activate" ]; then
    python3 -m venv "$SNAPX_VENV"
fi
# shellcheck disable=SC1090
. "$SNAPX_VENV/bin/activate"
py_ok python || { echo "the venv at $SNAPX_VENV was built with $(python --version 2>&1); delete it and rerun" >&2; exit 1; }

PIN="$(python -c 'import json; print(json.load(open("'"$HERE"'/config/tasks.json"))["scoring"]["transformers_pin"])')"
pip install -q --upgrade pip
# ai2-olmo 0.6.0 declares numpy<2, ai2-olmo-core==0.1.0, tokenizers, packaging,
# importlib_resources and cached_path>=1.6.2 besides torch and transformers, and it
# pins versions of the last two that clash with the scoring pin, so those three go
# in without dependency resolution exactly as on Kaggle.
pip install -q "torch>=2.4" "numpy<2" "huggingface_hub>=0.23" "transformers==$PIN" omegaconf rich requests filelock \
    boto3 google-cloud-storage safetensors sentencepiece tokenizers packaging datasets importlib_resources
pip install -q --no-deps "ai2-olmo==0.6.0" "ai2-olmo-core==0.1.0" "cached_path>=1.6.2"
python - <<'PY'
import torch, transformers
from hf_olmo import OLMoForCausalLM  # noqa: F401
print("imports ok: torch", torch.__version__, "transformers", transformers.__version__, "cuda build", torch.version.cuda)
PY
python "$HERE/score_shard.py" --shard "$HERE/shards/s01.json" --dry-run
echo "installed into $SNAPX_VENV; jobs write under $SNAPX_ROOT"
