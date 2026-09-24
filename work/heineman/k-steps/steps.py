# Seed-noise inflation of the ten-task average at each of the last 30 checkpoints of the
# OLMo 2 1B seed and data-order runs, to see whether the final-step value is typical.
import json
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

TEN = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu", "openbookqa", "piqa", "socialiqa", "winogrande"]
d = pd.read_parquet(hf_hub_download("allenai/signal-and-noise", "data/random_seeds-00000-of-00001.parquet", repo_type="dataset"))


def lam(S):
    tr, tot = np.trace(S), S.sum()
    return float(np.sqrt(tot / tr)) if tr > 0 and tot > 0 else float("nan")


out = []
for rt in ["seed", "data"]:
    for metric in ["acc_per_char", "bits_per_byte"]:
        x = d[(d.run_type == rt) & (d.metric == metric) & d.task_name.isin(TEN)]
        piv = x.pivot_table(index=["run_name", "step"], columns="task_name", values="value", aggfunc="mean")
        runs = sorted(piv.index.get_level_values(0).unique())
        tasks = [t for t in TEN if t in piv.columns and all(piv.loc[r][t].notna().sum() > 0 for r in runs)]
        piv = piv[tasks].dropna()
        steps = sorted(set.intersection(*[set(piv.loc[r].index) for r in runs]))
        arr = np.stack([piv.loc[r].loc[steps].to_numpy() for r in runs])
        vals = [lam(np.cov(arr[:, i, :], rowvar=False)) for i in range(len(steps) - 30, len(steps))]
        v = np.array(vals)
        row = {"run_type": rt, "metric": metric, "runs": len(runs), "tasks": tasks, "steps": [int(s) for s in steps[-30:]],
               "lam_per_step": vals, "last": vals[-1], "mean_last20": float(np.nanmean(v[-20:])), "median_last30": float(np.nanmedian(v)),
               "min_last30": float(np.nanmin(v)), "max_last30": float(np.nanmax(v)),
               "rank_of_last_among_30": int((v < v[-1]).sum()) + 1}
        out.append(row)
        print(json.dumps({k: row[k] for k in row if k not in ("lam_per_step", "steps", "tasks")}), flush=True)
        print("per step:", [round(a, 3) for a in vals], flush=True)
json.dump(out, open("/kaggle/working/heineman_steps.json", "w"), indent=1)
print("wrote /kaggle/working/heineman_steps.json")
