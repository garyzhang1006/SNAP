#!/usr/bin/env bash
# The 375 reduced release runs (bank 1 for DataDecide), built from
# allenai/DataDecide-eval-instances with the paper's own reducer. 25 tarballs
# of about 4.9 GB each are downloaded and reduced one at a time, four recipes
# in parallel, into compute2/data/release_runs. About 120 GB of transfer; on
# the box's 450 Mbps link roughly 40 minutes, plus the CPU reduction.
#
#   bash compute2/fetch_release.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$HERE/env.sh"
OUT="$HERE/data/release_runs"
mkdir -p "$OUT" "$SNAP2_TMP/release"
RECIPES=(c4 dclm-baseline dclm-baseline-25p-dolma1.7-75p dclm-baseline-50p-dolma1.7-50p dclm-baseline-75p-dolma1.7-25p
         dclm-baseline-top-10p dclm-baseline-top-20p dclm-baseline-top-fw-10p dclm-baseline-top-fw-3p dclm-baseline-top-fw2-7p
         dclm-baseline-top-fw3-7p dolma1.6++ dolma1.7 dolma1.7-no-code dolma1.7-no-flan dolma1.7-no-math-no-code dolma1.7-no-reddit
         falcon falcon-with-cc falcon-with-cc-top-10p falcon-with-cc-top-20p falcon-with-cc-top-orig-10p falcon-with-cc-top-tulu-10p
         fineweb-edu fineweb-pro)
# Four lanes, each its own temp directory so the tarballs never collide.
for lane in 0 1 2 3; do
    (
        subset=()
        for i in "${!RECIPES[@]}"; do
            if [ $((i % 4)) -eq "$lane" ]; then subset+=("${RECIPES[$i]}"); fi
        done
        seednoise fetch --recipes "${subset[@]}" --tmp "$SNAP2_TMP/release/lane$lane" --out "$OUT/lane$lane" --quiet
    ) > "$SNAP2_ROOT/logs/fetch_release_lane$lane.log" 2>&1 &
done
wait
# One directory of runs for the analysis; the per-lane manifests stay beside them.
find "$OUT"/lane* -name '*.npz' -exec mv -n {} "$OUT"/ \;
n="$(find "$OUT" -maxdepth 1 -name '*.npz' | wc -l)"
echo "release runs reduced: $n (expected 375) under $OUT"
[ "$n" -eq 375 ] || { echo "not all runs reduced; read $SNAP2_ROOT/logs/fetch_release_lane*.log and rerun" >&2; exit 1; }
