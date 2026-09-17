"""Freeze the request file before any checkpoint is scored.

  python3 tools/freeze.py PATH/requests_summary.json

Writes config/frozen.json with the request file's SHA-256, the OLMES commit, the
per-task item counts and the UTC time. k02 refuses to run unless the attached
request file matches this hash. The script won't overwrite an existing freeze,
because a second freeze after scoring started would void the pre-registration;
PROTOCOL_heldout.md says how to record a deliberate change instead.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

if len(sys.argv) != 2:
    sys.exit(__doc__)
summary = json.loads(Path(sys.argv[1]).read_text())
out = HERE / "config" / "frozen.json"
if out.exists():
    sys.exit(f"{out} already exists; see PROTOCOL_heldout.md, section 'Changes after freezing'")
tasks = json.loads((HERE / "config" / "tasks.json").read_text())
assert summary["olmes_commit"] == tasks["olmes_commit"], "summary was built at a different OLMES commit than tasks.json pins"
frozen = {"requests_sha256": summary["sha256"], "olmes_commit": summary["olmes_commit"],
          "items_per_task": {k: v["items_kept"] for k, v in summary["tasks"].items()},
          "frozen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
out.write_text(json.dumps(frozen, indent=1) + "\n")
print(json.dumps(frozen, indent=1))
print("Commit config/frozen.json now, before pushing any k02 kernel; the commit time is the public freeze time.")
