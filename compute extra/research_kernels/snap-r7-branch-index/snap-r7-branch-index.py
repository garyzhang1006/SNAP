"""R7 branch index: which model-repo branch holds each released eval run, and at which steps.

Design fixed before running (2026-09-15, 17:55 EDT). Metadata only, no weights. For each of the
125 DataDecide model repos, the HF refs API lists branches named step{S}-seed-{name}. For each of
the 375 eval runs, the eval index (snap-r20 step index) gives its set of released steps, and the
reduced run gives its selected step. Each run is matched to the branch name whose step set has
the largest Jaccard overlap with the run's eval steps, with ties and the final-step agreement
recorded. The output says, per run, the matched branch, the overlap, and whether a branch exists
at the selected step, which the held-out loss campaign needs. The GPU pilot tests the matching
on scores; this index covers all 375 runs.
"""
import json, re, shutil, subprocess, sys, time
from collections import Counter
from pathlib import Path
import numpy as np, requests

t0 = time.time()
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
from seednoise.store import load_run  # noqa: E402

eval_steps, seen_parts = {}, set()
for p in sorted(Path("/kaggle/input").rglob("step_index_*.json")):
    d = json.load(open(p))
    if d["part"] in seen_parts:
        continue
    seen_parts.add(d["part"])
    for rec in d["recipes"].values():
        for r in rec["runs"]:
            eval_steps.setdefault((r["recipe"], r["size"], int(r["seed"])), set()).add(int(r["step"]))
print(f"[eval index] parts {sorted(seen_parts)} runs {len(eval_steps)}", flush=True)

selected = {}
for p in Path("/kaggle/input").rglob("*__seed-*.npz"):
    if p.name.startswith("._"):
        continue
    _, meta = load_run(p)
    selected[(meta["recipe"], meta["size"], int(meta["seed"]))] = int(meta["step"])
assert len(selected) == 375, len(selected)

pat = re.compile(r"^step(\d+)-seed-(.+)$")
repos, runs = {}, []
for (recipe, size) in sorted({(r, s) for r, s, _ in selected}):
    repo = f"allenai/DataDecide-{recipe}-{size}"
    for attempt in range(5):
        resp = requests.get(f"https://huggingface.co/api/models/{repo}/refs", timeout=60)
        if resp.status_code == 200:
            break
        time.sleep(5 * (attempt + 1))
    if resp.status_code != 200:
        repos[repo] = {"error": resp.status_code}
        continue
    branches = {}
    for b in resp.json().get("branches", []):
        m = pat.match(b["name"])
        if m:
            branches.setdefault(m.group(2), set()).add(int(m.group(1)))
    repos[repo] = {k: {"n": len(v), "min": min(v), "max": max(v)} for k, v in branches.items()}
    for seed in sorted(s for r, z, s in selected if r == recipe and z == size):
        ev = eval_steps.get((recipe, size, seed), set())
        scores = {name: len(ev & st) / len(ev | st) for name, st in branches.items()} if ev else {}
        best = sorted(scores.items(), key=lambda kv: -kv[1])
        name = best[0][0] if best else None
        sel = selected[(recipe, size, seed)]
        runs.append({"recipe": recipe, "size": size, "seed": seed, "selected_step": sel,
                     "eval_final_step": max(ev) if ev else None, "n_eval_steps": len(ev),
                     "best_branch": name, "jaccard": best[0][1] if best else None,
                     "runner_up": best[1] if len(best) > 1 else None,
                     "branch_final_step": max(branches[name]) if name else None,
                     "selected_step_in_best_branch": bool(name and sel in branches[name]),
                     "selected_step_branches": sorted(k for k, v in branches.items() if sel in v)})

mapping = Counter((r["size"], r["seed"], r["best_branch"]) for r in runs)
summary = {"repos": len(repos), "repo_errors": {k: v for k, v in repos.items() if "error" in v},
           "runs": len(runs), "mapping_counts": [{"size": s, "seed": e, "branch": b, "runs": n} for (s, e, b), n in sorted(mapping.items())],
           "selected_step_available": sum(r["selected_step_in_best_branch"] for r in runs),
           "final_step_agrees": sum(r["eval_final_step"] == r["branch_final_step"] for r in runs),
           "jaccard_min": min(r["jaccard"] for r in runs if r["jaccard"] is not None),
           "jaccard_median": float(np.median([r["jaccard"] for r in runs if r["jaccard"] is not None]))}
print("[summary]", json.dumps(summary, indent=1), flush=True)
for r in runs:
    if not r["selected_step_in_best_branch"] or (r["jaccard"] or 0) < 0.9:
        print("[flag]", json.dumps(r), flush=True)
(W / "r7_branch_index.json").write_text(json.dumps({"design": __doc__, "summary": summary, "repos": repos, "runs": runs,
                                                    "wall_seconds": time.time() - t0}, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
