#!/usr/bin/env bash
# The whole pipeline in order, resumable: rerun the same command after any
# interruption and it continues from the last finished run.
#
#   bash compute2/run_all.sh                # everything
#   bash compute2/run_all.sh verify         # one job, then reduce and analyse
#
# Order and purpose (config/jobs.json): verify gates everything; the two
# PolyPythias final-step jobs and the DataDecide bank-2 job carry the reading
# rules; the curve and the zero-shot jobs are the supporting arms and can be
# stopped early without touching the rules.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$HERE/env.sh"
cd "$HERE"
n_release="$(find "$HERE/data/release_runs" -maxdepth 1 -name '*.npz' 2>/dev/null | wc -l | tr -d '[:space:]')"
if [ "${n_release:-0}" -ne 375 ]; then
    bash "$HERE/fetch_release.sh" 2>&1 | tee -a "$SNAP2_ROOT/logs/fetch_release.log"
fi
if [ $# -gt 0 ]; then
    JOBS=("$@")
else
    mapfile -t JOBS < <(python -c 'import json; print("\n".join(j["name"] for j in json.load(open("config/jobs.json"))["jobs"]))')
    if [ "${#JOBS[@]}" -eq 0 ]; then
        echo "could not enumerate jobs from $HERE/config/jobs.json (see the traceback above); fix the file or pass job names" >&2
        exit 1
    fi
fi
for job in "${JOBS[@]}"; do
    python score_runs.py --job "$job" --out "$SNAP2_SCORES" --tmp "$SNAP2_TMP" 2>&1 | tee -a "$SNAP2_ROOT/logs/$job.log"
    python reduce.py --job "$job" --scores "$SNAP2_SCORES" --out "$HERE/reduced" 2>&1 | tee -a "$SNAP2_ROOT/logs/$job.log"
    python analysis/estimates.py --reduced "$HERE/reduced" --scores "$SNAP2_SCORES" --release-runs "$HERE/data/release_runs" --out "$HERE/results"
    python analysis/report.py --results "$HERE/results"
    if [ "$job" = verify ]; then
        python - <<'PY'
import json, sys
v = json.load(open("results/verify.json"))
if v.get("status") != "ok" or not v.get("pass"):
    sys.exit(f"verification did not pass: {json.dumps(v, default=float)[:2000]}\nfix the scorer before scoring anything else")
print("verification passed")
PY
    fi
done
echo "all requested jobs finished; read compute2/results/RESULTS.md"
