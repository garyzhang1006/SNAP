#!/bin/bash
# Token-free continuous queue. Keeps up to MAX Kaggle kernels running by pushing
# the next name from research/queue.txt whenever a slot frees, and attaching a
# monitor to each one it pushes. Never edits the manuscript, never runs compute here.
R="/Users/garyzhang/Documents/ChatGPT/iclr main track"
Q="$R/research/queue.txt"
L="$R/research/queue_runner.log"
K=/Library/Frameworks/Python.framework/Versions/3.14/bin/kaggle
MAX=5
cd "$R" || exit 1
say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$L"; }
if [ "$(pgrep -f queue_runner.sh | grep -vc "^$$$")" -gt 1 ]; then
  say "another runner is already live, exiting"
  exit 0
fi
say "runner started"
while true; do
  # Each live monitor stands for one kernel we are waiting on, so it counts a slot.
  # Match only monitors carrying a kernel argument, so a passing grep cannot inflate the count.
  BUSY=$(pgrep -f "monitor_kernel.sh snap-" | wc -l | tr -d ' ')
  NEXT=$(grep -vE '^\s*(#|$)' "$Q" 2>/dev/null | head -1)
  if [ -z "$NEXT" ]; then
    # Idle rather than exit, so a queue topped up later starts moving without a restart.
    [ "$BUSY" -eq 0 ] && say "queue empty, idling"
  elif [ "$BUSY" -lt "$MAX" ]; then
    OUT=$($K kernels push -p "compute extra/research_kernels/$NEXT" 2>&1 | tail -1)
    case "$OUT" in
      *"successfully pushed"*)
        # Drop only the line we just pushed, leaving the rest of the queue intact.
        # grep exits 1 when it selects no lines, which happens on the last queue entry,
        # so the move must not be conditioned on its status.
        grep -vxF "$NEXT" "$Q" > "$Q.tmp"
        mv "$Q.tmp" "$Q"
        nohup bash "$R/research/monitor_kernel.sh" "$NEXT" >/dev/null 2>&1 &
        disown
        say "pushed $NEXT (busy was $BUSY)"
        sleep 20
        continue;;
      *"Maximum batch"*) say "slots full, holding $NEXT";;
      *) say "push failed for $NEXT: $OUT";;
    esac
  fi
  sleep 90
done
