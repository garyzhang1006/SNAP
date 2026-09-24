#!/bin/zsh
# After both bank-two scoring kernels finish: download their scores, stage the 45 files,
# upload them as joshkerr1111/snap-pythia-bank2-scores, run the two-bank CPU analysis
# kernel, download its results and fill the paper. Stops at the first failure.
#   KAGGLE_API_TOKEN=~/.kaggle-josh/access_token zsh work/finalize/finish_bank2.sh
set -e
setopt nullglob
ROOT="${0:A:h:h:h}"
cd "$ROOT"
K=joshkerr1111

# Kaggle downloads sometimes stall on one file, so each attempt is capped and retried.
fetch() {
  local kernel=$1 dest=$2
  for attempt in 1 2 3; do
    find "$dest" -size 0 -type f -delete 2>/dev/null || true
    perl -e 'alarm 300; exec @ARGV' kaggle kernels output "$kernel" -p "$dest" --page-size 200 >/dev/null 2>&1 && return 0
    echo "download of $kernel stalled, attempt $attempt"
  done
  return 1
}

for k in a b; do
  mkdir -p results/pythia-bank2-josh/$k
  fetch $K/snap-pythia-bank2-$k results/pythia-bank2-josh/$k
  echo "bank2-$k: $(find results/pythia-bank2-josh/$k -name '*.npz' -size +0 | wc -l | tr -d ' ') score files"
done

rm -rf work/finalize/stage2
python3 work/finalize/collect_scores.py --out work/finalize/stage2 results/pythia-bank2-josh
printf '{"title":"snap-pythia-bank2-scores","id":"%s/snap-pythia-bank2-scores","licenses":[{"name":"CC0-1.0"}]}' $K > work/finalize/stage2/dataset-metadata.json
kaggle datasets create -p work/finalize/stage2 >/dev/null
until [ "$(kaggle datasets status $K/snap-pythia-bank2-scores 2>&1)" = ready ]; do sleep 15; done

P=$(mktemp -d)
cp work/finalize/kernel2/snap-pythia-banks-analysis.py $P/
sed 's#"dataset_sources":\[[^]]*\]#"dataset_sources":["'$K'/snap-pythia-bank1-scores","'$K'/snap-pythia-bank2-scores"]#' \
  work/finalize/kernel2/kernel-metadata.json > $P/kernel-metadata.json
kaggle kernels push -p $P
sleep 30
while kaggle kernels status $K/snap-pythia-banks-analysis 2>&1 | grep -q 'RUNNING\|QUEUED'; do sleep 20; done
kaggle kernels status $K/snap-pythia-banks-analysis

O=results/pythia-banks-final-dl
rm -rf $O; mkdir -p $O
fetch $K/snap-pythia-banks-analysis $O
test -f $O/results/verdicts.json
rm -rf results/pythia-banks-final
cp -R $O/results results/pythia-banks-final
cp $O/snap-pythia-banks-analysis.log results/pythia-banks-final/
python3 work/finalize/fill_pending.py --results results/pythia-banks-final
