#!/usr/bin/env bash
# One-off install on the Vast.ai box (2x RTX 5090). Creates the scoring
# virtualenv, installs the pinned stack, checks that both model families load,
# builds the request banks, freezes their hashes and dry-runs the first job.
#
#   bash compute2/setup.sh
#
# The RTX 5090 is compute capability 12.0, which needs a CUDA 12.8 or newer
# torch build; the default PyPI torch wheel (2.8 and later) carries cu128, and
# the driver on the box must be 570 or newer for it. Nothing here needs a
# token: every repository read is public. If you have a Hugging Face read
# token, export HF_TOKEN in the shell before running; it raises the anonymous
# rate limit and is never written to disk by these scripts.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck disable=SC1091
. "$HERE/env.sh"

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
    echo "python3 is $(python3 --version 2>&1); needs 3.10 or newer" >&2; exit 1; }
if [ ! -f "$SNAP2_VENV/bin/activate" ]; then
    python3 -m venv "$SNAP2_VENV"
fi
# shellcheck disable=SC1090
. "$SNAP2_VENV/bin/activate"

PIN="$(python -c 'import json; print(json.load(open("'"$HERE"'/config/banks.json"))["scoring"]["transformers_pin"])')"
pip install -q --upgrade pip
# ai2-olmo 0.6.0 declares numpy<2 and pins transformers and cached_path versions
# that clash with the scoring pin, so it and its two companions go in without
# dependency resolution, exactly as in compute extra/cluster/setup.sh, and the
# transitive imports of hf_olmo are named here.
pip install -q "torch>=2.8" "numpy<2" "scipy>=1.10" "pandas>=2.0" "pyyaml>=6.0" "tqdm>=4.65" \
    "huggingface_hub>=0.23" "transformers==$PIN" omegaconf rich requests filelock \
    boto3 google-cloud-storage safetensors sentencepiece tokenizers packaging datasets importlib_resources accelerate
pip install -q --no-deps "ai2-olmo==0.6.0" "ai2-olmo-core==0.1.0" "cached_path>=1.6.2"
# The analysis imports the paper's estimator from src/.
pip install -q -e "$ROOT"
python - <<'PY'
import torch, transformers
from hf_olmo import OLMoForCausalLM  # noqa: F401
from transformers import GPTNeoXForCausalLM, DynamicCache  # noqa: F401
assert hasattr(DynamicCache, "from_legacy_cache"), "transformers dropped DynamicCache.from_legacy_cache; keep the 4.57.1 pin"
print("imports ok: torch", torch.__version__, "transformers", transformers.__version__, "cuda build", torch.version.cuda)
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        cap = torch.cuda.get_device_capability(i)
        print(f"gpu {i}: {torch.cuda.get_device_name(i)} sm_{cap[0]}{cap[1]} {torch.cuda.get_device_properties(i).total_memory / 2**30:.0f} GiB")
    x = torch.randn(1024, 1024, device="cuda")
    print("matmul ok", float((x @ x).sum()))
else:
    print("no CUDA device visible; scoring will refuse to start")
PY
cd "$HERE"
python make_manifests.py
python requests/build_bank1.py
python requests/build_bank2.py --zero-shot
python requests/freeze.py
python score_runs.py --job verify --dry-run
echo "installed into $SNAP2_VENV; scores go under $SNAP2_SCORES"
echo "next: bash compute2/run_all.sh"
