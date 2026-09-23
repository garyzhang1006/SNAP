"""snap-r2-r1-49 (CPU only): the 1,081,575-set enumeration and a bank-two manifest.

Part 1, enumeration (paper main.tex:129: margin estimates 1.037 to 1.317,
accuracy 0.963 to 1.191, no set reaching the plan thresholds 1.349 and 1.40).
Population: the 375 shipped reduced runs through seednoise.build.build_population
(Lambda 1.24395 asserted). Per configuration T_c and U_c from
seednoise.estimator.estimate(pop, name).T / .U; for a recipe set S the estimator
is sqrt(sum_{c in S} T_c / sum_{c in S} U_c) (supplement_extended_body.tex:602),
so each recipe's T and U are summed over its five sizes once and every
17-of-25 subset is scored exactly.

Part 2, bank-two manifest. No frozen bank-two request file exists in the repo
or the SNAP release, so this rebuilds it with the committed builders at SNAP
6cfedee: compute2/requests/build_bank1.py (release requests from
allenai/DataDecide-eval-instances) then compute2/requests/build_bank2.py
(OLMES at 5a51f502 in its own uv env, the train/validation splits, the
few-shot and bank-one context filters, the 600-per-benchmark cap with
subsample_seed 20260921). The builder's bank2_summary.json (per-trait and
per-task counts, drops, sha256) is copied out as the manifest. Part 2 runs
after part 1 has written its file, and a failure there is recorded, not raised.
"""
import itertools
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
run_dir = Path("/kaggle/tmp") / "runs_shipped"
shutil.rmtree(run_dir, ignore_errors=True)
run_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, run_dir / p.name)
pop, info = build_population(run_dir, TRAITS, n_runs=3)
lam = estimate(pop, MARGIN).lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"
G = pop.n_clusters
assert G == 25

combos = np.array(list(itertools.combinations(range(G), 17)), dtype=np.int8)
assert combos.shape[0] == 1081575
enum = {"n_sets": int(combos.shape[0])}
THRESH = {MARGIN: 1.349, ACCURACY: 1.40}
for name in (MARGIN, ACCURACY):
    e = estimate(pop, name)
    Tr = np.bincount(pop.recipe, weights=e.T, minlength=G)
    Ur = np.bincount(pop.recipe, weights=e.U, minlength=G)
    th = Tr[combos].sum(1) / Ur[combos].sum(1)
    lamS = np.where(th >= 0, np.sqrt(np.clip(th, 0, None)), np.nan)
    i_lo, i_hi = int(np.nanargmin(lamS)), int(np.nanargmax(lamS))
    enum[name] = {"full_lambda": e.lambda_hat, "min": float(np.nanmin(lamS)), "max": float(np.nanmax(lamS)),
                  "median": float(np.nanmedian(lamS)), "p05_p95": [float(x) for x in np.nanpercentile(lamS, [5, 95])],
                  "undefined_sets": int(np.isnan(lamS).sum()), "plan_threshold": THRESH[name],
                  "sets_reaching_threshold": int((lamS >= THRESH[name]).sum()),
                  "argmin_recipes": [info["recipes"][int(j)] for j in combos[i_lo]],
                  "argmax_recipes": [info["recipes"][int(j)] for j in combos[i_hi]]}
    print(f"[enum {name}] min {enum[name]['min']:.4f} max {enum[name]['max']:.4f} reach {enum[name]['sets_reaching_threshold']}", flush=True)
enum["estimator"] = "sqrt(sum_{c in S} T_c / sum_{c in S} U_c), T and U from seednoise.estimator.estimate on the 375 shipped runs"
(W / "r1_49_enumeration.json").write_text(json.dumps(enum, indent=1))
print(f"[enum] written {time.time() - t0:.0f}s", flush=True)

# ---- part 2: bank-two manifest ------------------------------------------------------------
SNAP_COMMIT = "6cfedee87ac52695f96665ecc0a62ecdc97e1c35"
manifest = {"status": "not run"}
try:
    snap = Path("/kaggle/tmp/SNAP")
    if not snap.exists():
        subprocess.check_call(["git", "clone", "-q", "https://github.com/garyzhang1006/SNAP.git", str(snap)])
    subprocess.check_call(["git", "-C", str(snap), "checkout", "-q", SNAP_COMMIT])
    c2 = snap / "compute2"
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"])
    subprocess.check_call([sys.executable, str(c2 / "requests" / "build_bank1.py")], cwd=str(c2), timeout=3 * 3600)
    print(f"[bank1] built {time.time() - t0:.0f}s", flush=True)
    subprocess.check_call([sys.executable, str(c2 / "requests" / "build_bank2.py")], cwd=str(c2), timeout=6 * 3600)
    summ = json.loads((c2 / "data" / "bank2_summary.json").read_text())
    summ.pop("file", None)
    b1 = c2 / "data" / "bank1_summary.json"
    manifest = {"status": "ok", "snap_commit": SNAP_COMMIT, "bank2_summary": summ,
                "bank1_summary": json.loads(b1.read_text()) if b1.exists() else None}
    shutil.copy(c2 / "data" / "bank2_requests.jsonl.gz", W / "bank2_requests.jsonl.gz")
    print(f"[bank2] items {summ.get('items')} per_trait {summ.get('per_trait')}", flush=True)
except Exception:  # noqa: BLE001
    manifest = {"status": "error", "traceback": traceback.format_exc()[-6000:]}
    print(manifest["traceback"], flush=True)
manifest["wall_seconds"] = time.time() - t0
(W / "r1_49_bank2_manifest.json").write_text(json.dumps(manifest, indent=1, default=str))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
