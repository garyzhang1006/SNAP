"""Build the k02 scoring kernels: the pilot shard, then the production shards.

  python3 tools/make_shards.py pilot
  python3 tools/make_shards.py production --pilot-report PATH/shard_report.json --decision PATH/decision.json

Pilot: c4 at 150M (seeds 2, 14, 15) and 1B (seeds 2, 4, 5), every task in the
request file, so one kernel exercises all five branch labels, gives k03 its
release comparison and backup-rule accuracies, and times both ends of the size
range.

Production: the held-out tasks named in the k03 decision file, over the 375 runs
in config/runs.json minus the pilot's six. Per-run seconds come from the pilot's
measured download + load + scoring times, interpolated linearly in parameter
count between 150M and 1B, and scaled by the ratio of production to pilot token
counts. If the projected session hours exceed the tasks.json threshold, the
scope drops to the fallback sizes and plan.json says so. Each shard is packed so
its estimate, with a 1.3 safety factor, fits two cards inside deadline_hours.

Nothing here contacts Kaggle. tools/push.sh uploads what this writes.
"""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
USER = "garyzhang11111"
CODE_DATASET = f"{USER}/snap-new-code"
REQUESTS_KERNEL = f"{USER}/snap-new-k01-requests"
PARAMS = {"150M": 150e6, "300M": 300e6, "530M": 530e6, "750M": 750e6, "1B": 1e9}
DEADLINE_HOURS = 8.4
SETUP_HOURS = 0.3
SAFETY = 1.3
MARKER = "SHARD = None  # replaced by tools/make_shards.py"


def load(p):
    return json.loads(Path(p).read_text())


def write_kernel(slug, shard, build):
    template = (HERE / "kaggle" / "k02-score" / "k02-score-template.py").read_text()
    assert template.count(MARKER) == 1, "SHARD marker missing from the template"
    code = template.replace(MARKER, "SHARD = json.loads(r'''" + json.dumps(shard) + "''')")
    d = build / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.py").write_text(code)
    meta = {"id": f"{USER}/{slug}", "title": slug, "code_file": f"{slug}.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_tpu": False,
            "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
            "dataset_sources": [CODE_DATASET], "competition_sources": [],
            "kernel_sources": [REQUESTS_KERNEL], "model_sources": []}
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1))
    return d


def pilot(runs, tasks, build):
    want = {tuple(c) for c in tasks["pilot"]["configs"]}
    chosen = [r for r in runs if (r["recipe"], r["size"]) in want]
    assert len(chosen) == 6, f"pilot expects 6 runs, found {len(chosen)}"
    names = [t["name"] for t in tasks["heldout"] + tasks["backups_in_order"]] + [tasks["verification"]["name"]]
    shard = {"name": "pilot", "runs": chosen, "tasks": names, "est_seconds": {}, "deadline_hours": DEADLINE_HOURS}
    d = write_kernel("snap-new-k02-pilot", shard, build)
    print(f"wrote {d} with {len(chosen)} runs and tasks {names}")


def seconds_model(report, runs_by_key, token_ratio):
    """Seconds per production run as a function of size. Download and load time
    carry over from the pilot as measured; scoring time scales with tokens."""
    per_size = {}
    for key, t in report["timing"].items():
        per_size.setdefault(runs_by_key[key]["size"], []).append((t["download"] + t["load"], t["score"]))
    assert set(per_size) >= {"150M", "1B"}, f"pilot timing covers {sorted(per_size)}, needs 150M and 1B"
    anchors = {s: tuple(sum(x[i] for x in per_size[s]) / len(per_size[s]) for i in (0, 1)) for s in ("150M", "1B")}

    def est(size):
        f = (PARAMS[size] - PARAMS["150M"]) / (PARAMS["1B"] - PARAMS["150M"])
        fixed = anchors["150M"][0] + f * (anchors["1B"][0] - anchors["150M"][0])
        score = anchors["150M"][1] + f * (anchors["1B"][1] - anchors["150M"][1])
        return fixed + score * token_ratio
    return est, {s: {"download_plus_load": a[0], "score": a[1]} for s, a in anchors.items()}


def production(runs, tasks, build, pilot_report, decision, token_ratio):
    report = load(pilot_report)
    dec = load(decision)
    assert dec.get("seed_branch_mapping_verified") is True, "k03 did not verify the seed-branch mapping; production is blocked"
    names = dec["heldout_tasks_final"]
    by_key = {r["run_key"]: r for r in runs}
    est, anchors = seconds_model(report, by_key, token_ratio)
    pilot_keys = set(report["done"])
    todo = [r for r in runs if r["run_key"] not in pilot_keys]

    def hours(rs):
        return sum(est(r["size"]) for r in rs) / 3600
    full_card_hours = hours(todo)
    full_session_hours = full_card_hours / 2 + SETUP_HOURS * math.ceil(full_card_hours / 2 / (DEADLINE_HOURS - SETUP_HOURS))
    scope = "full"
    if full_session_hours > tasks["scope"]["fallback_if_projected_t4_hours_above"]:
        scope = "fallback"
        todo = [r for r in todo if r["size"] in tasks["scope"]["fallback"]]

    cap = 2 * (DEADLINE_HOURS - SETUP_HOURS) * 3600 / SAFETY
    shards, cur, cur_s = [], [], 0.0
    for r in sorted(todo, key=lambda r: (-PARAMS[r["size"]], r["recipe"], r["batch"])):
        s = est(r["size"])
        if cur and cur_s + s > cap:
            shards.append(cur)
            cur, cur_s = [], 0.0
        cur.append(r)
        cur_s += s
    if cur:
        shards.append(cur)
    plan = {"scope": scope, "tasks": names, "pilot_seconds_per_run": anchors, "token_ratio": token_ratio,
            "full_scope_projected_session_hours": full_session_hours,
            "shards": []}
    for i, rs in enumerate(shards, start=1):
        slug = f"snap-new-k02-s{i:02d}"
        shard = {"name": slug, "runs": rs, "tasks": names,
                 "est_seconds": {r["run_key"]: est(r["size"]) for r in rs},
                 "deadline_hours": DEADLINE_HOURS}
        write_kernel(slug, shard, build)
        plan["shards"].append({"slug": slug, "runs": len(rs), "projected_session_hours": hours(rs) / 2 + SETUP_HOURS})
    plan["projected_session_hours_total"] = sum(s["projected_session_hours"] for s in plan["shards"])
    # k04 reads every shard's output, so its kernel sources follow the shard list.
    k04 = HERE / "kaggle" / "k04-analyze-heldout" / "kernel-metadata.json"
    meta = load(k04)
    base = [s for s in meta["kernel_sources"] if "-k02-s" not in s]
    meta["kernel_sources"] = base + [f"{USER}/{s['slug']}" for s in plan["shards"]]
    k04.write_text(json.dumps(meta, indent=1) + "\n")
    (build / "plan.json").write_text(json.dumps(plan, indent=1))
    print(json.dumps(plan, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["pilot", "production"])
    ap.add_argument("--pilot-report", help="shard_report.json downloaded from the pilot kernel")
    ap.add_argument("--decision", help="decision.json downloaded from k03")
    ap.add_argument("--token-ratio", type=float, default=None,
                    help="production tokens per run divided by pilot tokens per run; k03 writes it into decision.json")
    args = ap.parse_args()
    runs = load(HERE / "config" / "runs.json")["runs"]
    tasks = load(HERE / "config" / "tasks.json")
    build = HERE / "kaggle" / "k02-score" / "build"
    if args.stage == "pilot":
        pilot(runs, tasks, build)
    else:
        if not (args.pilot_report and args.decision):
            ap.error("production needs --pilot-report and --decision")
        ratio = args.token_ratio if args.token_ratio is not None else load(args.decision)["token_ratio_production_over_pilot"]
        production(runs, tasks, build, args.pilot_report, args.decision, ratio)


if __name__ == "__main__":
    main()
