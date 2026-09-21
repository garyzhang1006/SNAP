"""R12 analysis: OBSERVED PolyPythias transport and adjacent-checkpoint numbers from the new rescore.

Design fixed before the rescore finished (2026-09-15, 17:50 EDT). Inputs are the 63 runs written
by snap-r12-polypythias with the original seednoise scorer on T4 GPUs with a 6,000-token cap.
1. Transport. build_population on runs-arm2 with nine runs per configuration, for the three
   sizes 70m, 160m, 410m and for all five sizes. Margin and accuracy Lambda, K_eff, the
   configuration bootstrap interval (4,999 draws, seed 0) with its SE, and the excess ratio
   (Lambda_PP - 1) / (Lambda_DD - 1) against DataDecide margin 1.243949911719114 and accuracy
   1.0783733870898093. Reported values for comparison are 1.41372, 1.26199, 2.28589, 1.71085,
   intervals 0.939 to 1.781 and 0.927 to 1.537, SEs 0.190 and 0.150.
2. Adjacent checkpoints. The nine 160m runs at step143000 and step142000 on the nested 200-per-task
   sample of nine non-MMLU traits. A run's aggregate is the equal-weight mean over traits of its
   mean item score. Between-run SD (ddof 1) at step143000, RMS of the step change, their ratio,
   and the across-run correlation of the two steps' aggregates, for margins and accuracy, plus the
   same numbers for BoolQ alone. Reported values are 0.00513, 0.00456, 0.890, 0.573 for margins,
   0.00451, 0.00710, 1.573, -0.070 for accuracy, and BoolQ margin SD 0.0438 with shift 0.0370.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import config_bootstrap  # noqa: E402
from seednoise.store import load_run  # noqa: E402

DD = {"margin": 1.243949911719114, "accuracy": 1.0783733870898093}
arm2 = [p for p in Path("/kaggle/input").rglob("arm2__*.npz") if "runs-arm2" in str(p)]
adj = {s: sorted(p for p in Path("/kaggle/input").rglob("arm2__160m__seed-*.npz") if f"runs-adjacent/{s}" in str(p))
       for s in ("step143000", "step142000")}
print(f"[inputs] arm2 {len(arm2)} adjacent {[len(v) for v in adj.values()]}", flush=True)
assert len(arm2) == 45 and all(len(v) == 9 for v in adj.values())
report = {"design": __doc__, "transport": {}, "adjacent": {}}
runs_dir = W / "arm2"; runs_dir.mkdir(exist_ok=True)
for p in arm2:
    shutil.copy(p, runs_dir / p.name)

for label, sizes in (("three_sizes", ["70m", "160m", "410m"]), ("five_sizes", ["14m", "31m", "70m", "160m", "410m"])):
    pop, info = build_population(runs_dir, TRAITS, n_runs=9, sizes=sizes)
    cell = {"N": pop.N, "R": pop.R, "K": pop.K, "dropped": info.get("dropped_cells")}
    for name in ("margin", "accuracy"):
        e = estimate(pop, name, check=True)
        row = {"Lambda": float(e.lambda_hat), "K_eff": float(e.k_eff), "excess_ratio": float((e.lambda_hat - 1) / (DD[name] - 1))}
        try:
            iv = config_bootstrap(e.T, e.U, n_boot=4999, seed=0)
            row.update(config_lo=float(iv.lo), config_hi=float(iv.hi), config_se=float(iv.se))
        except Exception as error:  # noqa: BLE001
            row["config_error"] = f"{type(error).__name__}: {error}"
        cell[name] = row
    report["transport"][label] = cell
    print(f"[transport {label}] {json.dumps(cell)}", flush=True)


def aggregates(paths, trait_filter=None):
    out = {}
    for p in paths:
        items, meta = load_run(p)
        per = {"margin": [], "accuracy": []}
        traits = sorted(set(items.trait.tolist()))
        if trait_filter is not None:
            traits = [t for t in traits if t == trait_filter]
        for t in traits:
            m = items.trait == t
            per["margin"].append(items.margin[m].mean()); per["accuracy"].append(items.correct[m].mean())
        out[int(meta["seed"])] = {k: float(np.mean(v)) for k, v in per.items()}
        out[int(meta["seed"])]["n_traits"] = len(traits); out[int(meta["seed"])]["n_items"] = int(items.item_id.size)
    return out


boolq_index = list(TRAITS).index("boolq")
for scope, tf in (("battery", None), ("boolq", boolq_index)):
    a1, a0 = aggregates(adj["step143000"], tf), aggregates(adj["step142000"], tf)
    seeds = sorted(a1)
    assert seeds == sorted(a0)
    cell = {"seeds": seeds, "n_traits": a1[seeds[0]]["n_traits"], "n_items": a1[seeds[0]]["n_items"]}
    for name in ("margin", "accuracy"):
        x1 = np.array([a1[s][name] for s in seeds]); x0 = np.array([a0[s][name] for s in seeds])
        sd = float(x1.std(ddof=1)); rms = float(np.sqrt(np.mean((x1 - x0) ** 2)))
        rms_c = float(np.sqrt(np.mean(((x1 - x0) - (x1 - x0).mean()) ** 2)))
        cell[name] = {"between_run_sd": sd, "rms_shift": rms, "ratio": rms / sd, "rms_shift_centred": rms_c,
                      "ratio_centred": rms_c / sd, "corr": float(np.corrcoef(x1, x0)[0, 1]), "mean_shift": float((x1 - x0).mean())}
    report["adjacent"][scope] = cell
    print(f"[adjacent {scope}] {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r12_analysis.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
