# Kernel B: checkpoint-noise covariance on the DataDecide models themselves, from the
# datadecide_intermediate split Heineman et al. (2025) release. Their noise for DataDecide is the
# spread over each model's final 5 checkpoints. Our paper measures seed-noise inflation of the
# ten-task average on the same recipes and sizes (accuracy 1.078, margin 1.244); this gives the
# checkpoint-noise inflation to set against it, with a recipe-clustered bootstrap.
import json
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

OUT = Path("/kaggle/working")
RNG = np.random.default_rng(20260923)
B = 5000
p = hf_hub_download("allenai/signal-and-noise", "data/datadecide_intermediate-00000-of-00001.parquet", repo_type="dataset")
d = pd.read_parquet(p)
print(d.shape, flush=True)
print(d.dtypes.to_string(), flush=True)
print(d.head(3).T.to_string(), flush=True)

TEN = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu", "openbookqa", "piqa", "socialiqa", "winogrande"]
SIZES = ["150M", "300M", "530M", "750M", "1B"]
# primary_metric holds each task's OLMES score; margin_per_byte is the per-byte margin our paper uses.
METRICS = [m for m in ["primary_metric", "margin_per_byte", "acc_per_char", "bits_per_byte_corr"] if m in d.columns and d[m].notna().any()]
print("metrics:", METRICS, flush=True)
print("tasks:", d.task.value_counts().to_dict(), flush=True)
print("chinchilla:", d.chinchilla.value_counts().to_dict(), "group:", d.group.value_counts().head(10).to_dict(), flush=True)
print("seeds per model:", d.groupby("model").seed.nunique().value_counts().to_dict(), flush=True)
report = {"source": "allenai/signal-and-noise datadecide_intermediate", "bootstrap_draws": B, "results": [], "checks": {}}

# The released macro average should be the plain mean of the ten primary scores.
if "olmes_10_macro_avg" in set(d.task):
    w = d[d.task.isin(TEN + ["olmes_10_macro_avg"])].pivot_table(index=["model", "seed", "step"], columns="task", values="primary_metric", aggfunc="mean")
    have = [t for t in TEN if t in w.columns]
    w = w[have + ["olmes_10_macro_avg"]].dropna()
    report["checks"]["macro_avg_tasks"] = have
    report["checks"]["macro_avg_max_abs_diff"] = float((w[have].mean(1) - w["olmes_10_macro_avg"]).abs().max()) if len(w) else float("nan")
    print("macro avg check:", report["checks"], flush=True)

sub = d[d.task.isin(TEN) & d["size"].isin(SIZES)]


def model_blocks(metric, W):
    # A run is one model (mix, size, token multiplier) at one seed; checkpoints vary within it.
    piv = sub.pivot_table(index=["mix", "size", "model", "seed", "step"], columns="task", values=metric, aggfunc="mean")
    piv = piv[[t for t in TEN if t in piv.columns]].dropna()
    blocks = {}
    for key, g in piv.groupby(level=[0, 1, 2, 3]):
        g = g.sort_index(level=4)
        if len(g) >= W:
            blocks[key] = g.to_numpy()[-W:]
    return list(piv.columns), blocks


def pooled(cache, keys):
    S = sum(cache[k][0] for k in keys)
    dof = sum(cache[k][1] for k in keys)
    return S / dof


for metric in METRICS:
    for W in [5, 10]:
        tasks, blocks = model_blocks(metric, W)
        mixes = sorted({k[0] for k in blocks})
        for scope in SIZES + ["all"]:
            keys = [k for k in blocks if scope == "all" or k[1] == scope]
            if len(keys) < 5:
                continue
            row = {"metric": metric, "window": W, "scope": scope, "models": len(keys), "tasks": tasks}
            for detrend in [False, True]:
                name = "detrend" if detrend else "demean"
                cache = {k: within_cov(blocks[k], detrend) for k in keys}
                by_mix = {m: [k for k in keys if k[0] == m] for m in mixes}
                point = lam(pooled(cache, keys))
                bs = []
                for _ in range(B):
                    draw = RNG.choice(mixes, len(mixes), replace=True)
                    kk = [k for m in draw for k in by_mix[m]]
                    bs.append(lam(pooled(cache, kk)) if kk else np.nan)
                row[name] = {"lam": point, "ci95": [pct(bs, 2.5), pct(bs, 97.5)]}
            report["results"].append(row)
            print(json.dumps(row, default=float), flush=True)

(OUT / "heineman_datadecide.json").write_text(json.dumps(report, indent=1, default=float))
print("wrote", OUT / "heineman_datadecide.json")
