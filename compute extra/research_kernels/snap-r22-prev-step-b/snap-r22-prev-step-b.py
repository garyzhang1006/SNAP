"""R22 part b: reduce every configuration at the checkpoint before its selected step.

For each recipe the script downloads the release tarball, indexes it, and for
every size takes the same common step the original fetch used (the largest
step all seeds reached) and the largest step all seeds share below it. It then
reduces the runs at that earlier step with seednoise's own reduce_run and
save_run, so the files have the same layout, item ids and metadata as the
shipped reduced runs, and records both steps and their gap. Nothing about the
selected-step runs is recomputed here.
"""
import json, platform, shutil, subprocess, sys, tarfile, time
from pathlib import Path

RECIPES = ["dclm-baseline-50p-dolma1.7-50p", "dclm-baseline-75p-dolma1.7-25p", "dclm-baseline-top-10p", "dclm-baseline-top-20p", "dclm-baseline-top-fw-10p"]
W = Path("/kaggle/working"); TMP = Path("/kaggle/tmp"); TMP.mkdir(parents=True, exist_ok=True)
t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
hits = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if not p.name.startswith("._") and "seed-noise" in str(p)]
assert hits, "seednoise source not found under /kaggle/input"
shutil.copytree(hits[0].parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
shutil.rmtree(W / "seed-noise", ignore_errors=True)
from seednoise.data.datadecide import batch_labels, download_recipe, index_tar, parse_member, reduce_run  # noqa: E402
from seednoise.store import save_run  # noqa: E402

out_runs = W / "runs_prev"; out_runs.mkdir(exist_ok=True)
manifest = {"part": "b", "recipes": {}, "failures": {}}
for recipe in RECIPES:
    t1 = time.time()
    tar = TMP / f"{recipe}.tar"
    try:
        for attempt in range(1, 4):
            try:
                download_recipe(recipe, tar, progress=False)
                keys = index_tar(tar)
                break
            except Exception as error:  # noqa: BLE001
                print(f"[{recipe}] attempt {attempt} failed: {type(error).__name__}: {error}", flush=True)
                tar.unlink(missing_ok=True)
                if attempt == 3:
                    raise
                time.sleep(30)
        cells, targets = {}, {}
        for size in sorted({k.size for k in keys}):
            by_seed = {}
            for k in keys:
                if k.size == size:
                    by_seed.setdefault(k.seed, set()).add(k.step)
            if len(by_seed) < 2:
                continue
            shared = set.intersection(*by_seed.values())
            if not shared:
                continue
            common = max(shared)
            below = sorted(s for s in shared if s < common)
            cell = {"seeds": sorted(by_seed), "common_step": common, "max_step_by_seed": {str(s): max(v) for s, v in by_seed.items()},
                    "previous_step": below[-1] if below else None, "gap": (common - below[-1]) if below else None}
            cells[size] = cell
            if below:
                labels = batch_labels(sorted(by_seed))
                for s in by_seed:
                    targets[(size, s, below[-1])] = labels[s]
        rows = []
        with tarfile.open(tar, mode="r|gz") as tf:
            for m in tf:
                k = parse_member(m.name)
                if k is None or (k.size, k.seed, k.step) not in targets:
                    continue
                items, gain, seen = reduce_run(tf.extractfile(m).read())
                meta = {"recipe": k.recipe, "size": k.size, "seed": k.seed, "step": k.step, "batch": targets[(k.size, k.seed, k.step)],
                        "gain": gain, "n_tasks": len(seen), "n_items": items.n_items}
                save_run(out_runs / f"{k.name()}.npz", items, meta)
                rows.append(meta)
        manifest["recipes"][recipe] = {"member_recipe": keys[0].recipe, "cells": cells, "runs": rows, "seconds": time.time() - t1}
        print(f"[{recipe}] {len(rows)} runs reduced at the previous shared step in {time.time() - t1:.0f}s; "
              f"gaps { {s: c['gap'] for s, c in cells.items()} }", flush=True)
    except Exception as error:  # noqa: BLE001
        manifest["failures"][recipe] = f"{type(error).__name__}: {error}"
        print(f"[{recipe}] FAILED: {manifest['failures'][recipe]}", flush=True)
    finally:
        tar.unlink(missing_ok=True)
    (W / "prev_manifest_b.json").write_text(json.dumps(manifest, indent=1))
manifest["wall_seconds"] = time.time() - t0
(W / "prev_manifest_b.json").write_text(json.dumps(manifest, indent=1))
print(f"[done] {len(manifest['recipes'])} of {len(RECIPES)} recipes in {time.time() - t0:.0f}s", flush=True)
if manifest["failures"]:
    sys.exit(f"failed recipes: {sorted(manifest['failures'])}")
