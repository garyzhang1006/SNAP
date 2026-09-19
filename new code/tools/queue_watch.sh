#!/usr/bin/env bash
# Poll Kaggle for the remaining 750M shards. Push s04 when a GPU slot frees
# (Kaggle allows two batch GPU sessions), then push the 530M+750M held-out
# analysis once s04, s05 and s06 are all complete. Emits one line per state
# change so a Monitor can watch it. No compute runs here; only the Kaggle CLI.
# Written for the bash 3 that ships with macOS, so no associative arrays.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
st() { bash "$HERE/tools/push.sh" status "$1" 2>&1 | grep -o 'KernelWorkerStatus\.[A-Z]*' | head -1; }
S06=; S05=; S04=; K04=
s04_pushed=0; k04_pushed=0
while true; do
  s=$(st snap-new-k02-s06); [ -z "$s" ] && s=NONE
  [ "$S06" != "$s" ] && { echo "$(date +%H:%M) s06 $s"; S06=$s; }
  s=$(st snap-new-k02-s05); [ -z "$s" ] && s=NONE
  [ "$S05" != "$s" ] && { echo "$(date +%H:%M) s05 $s"; S05=$s; }
  s=$(st snap-new-k02-s04); [ -z "$s" ] && s=NONE
  [ "$S04" != "$s" ] && { echo "$(date +%H:%M) s04 $s"; S04=$s; }
  running=0
  [ "$S06" = "KernelWorkerStatus.RUNNING" ] && running=$((running+1))
  [ "$S05" = "KernelWorkerStatus.RUNNING" ] && running=$((running+1))
  if [ $s04_pushed -eq 0 ] && [ $running -lt 2 ]; then
    out=$(bash "$HERE/tools/push.sh" kernel "$HERE/kaggle/k02-score/build/snap-new-k02-s04" 2>&1 | tail -1)
    echo "$(date +%H:%M) push s04: $out"
    echo "$out" | grep -q 'successfully pushed' && s04_pushed=1
  fi
  for pair in "s06 $S06" "s05 $S05" "s04 $S04"; do
    case "$pair" in *ERROR*|*CANCEL*) echo "$(date +%H:%M) FAILED $pair";; esac
  done
  if [ $k04_pushed -eq 0 ] && [ "$S06" = "KernelWorkerStatus.COMPLETE" ] && [ "$S05" = "KernelWorkerStatus.COMPLETE" ] && [ "$S04" = "KernelWorkerStatus.COMPLETE" ]; then
    out=$(bash "$HERE/tools/push.sh" kernel "$HERE/kaggle/k04-analyze-heldout/build/snap-new-k04-heldout-530m750m" 2>&1 | tail -1)
    echo "$(date +%H:%M) push k04-530m750m: $out"
    echo "$out" | grep -q 'successfully pushed' && k04_pushed=1
  fi
  if [ $k04_pushed -eq 1 ]; then
    s=$(st snap-new-k04-heldout-530m750m); [ -z "$s" ] && s=NONE
    [ "$K04" != "$s" ] && { echo "$(date +%H:%M) k04-530m750m $s"; K04=$s; }
    case "$s" in KernelWorkerStatus.COMPLETE|KernelWorkerStatus.ERROR) echo "$(date +%H:%M) DONE k04 $s"; exit 0;; esac
  fi
  sleep 300
done
