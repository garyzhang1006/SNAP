#!/bin/bash
# Token-free kernel monitor. Polls one Kaggle kernel until it reaches a terminal
# state, downloads its output, appends one row to research/kernel_status.tsv.
# Never pushes, never re-runs, never touches the manuscript.
K=/Library/Frameworks/Python.framework/Versions/3.14/bin/kaggle
R="/Users/garyzhang/Documents/ChatGPT/iclr main track"
U=garyzhang11111
N="$1"
START=$(date '+%Y-%m-%d %H:%M')
T0=$(date +%s)
S=""
for i in $(seq 1 1440); do
  S=$($K kernels status "$U/$N" 2>&1 | grep -oE 'KernelWorkerStatus\.[A-Z]*' | head -1)
  case "$S" in *COMPLETE*|*ERROR*|*CANCEL*) break;; esac
  sleep 60
done
STATUS=${S##*.}
[ -z "$STATUS" ] && STATUS=TIMEOUT
OUT="$R/research/outputs/$N"
mkdir -p "$OUT"
$K kernels output "$U/$N" -p "$OUT" >/dev/null 2>&1
rm -rf "$OUT/seed-noise"
FILES=$(ls "$OUT" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
LOG="$OUT/$N.log"
if [ "$STATUS" = ERROR ] && [ -f "$LOG" ]; then
  DETAIL=$(grep -E '^[A-Za-z_.]*(Error|Exception)' "$LOG" | tail -1)
elif [ -f "$LOG" ]; then
  DETAIL=$(grep -aE '^\[done\]' "$LOG" | tail -1)
fi
[ -z "$DETAIL" ] && DETAIL=$(tail -1 "$LOG" 2>/dev/null)
MIN=$(( ($(date +%s) - T0) / 60 ))
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$N" "$STATUS" "$START" "$(date '+%Y-%m-%d %H:%M')" "$MIN" "$FILES" "$DETAIL" >> "$R/research/kernel_status.tsv"
