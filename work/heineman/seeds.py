# Kernel A: seed noise against checkpoint noise for a multi-task average, on the OLMo 2 1B
# seed and data-order runs that Heineman et al. (2025) release as random_seeds.
# Their Sec. 3.1 / Sec. 6 argue checkpoint-to-checkpoint noise is a cheap proxy for seed noise,
# a claim checked per task. For an average the two agree only if both noise sources have the
# same cross-task correlation, which this compares through the inflation ratio lam().
import json
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

OUT = Path("/kaggle/working")
RNG = np.random.default_rng(20260923)
B = 5000
p = hf_hub_download("allenai/signal-and-noise", "data/random_seeds-00000-of-00001.parquet", repo_type="dataset")
d = pd.read_parquet(p)
print(d.shape, d.columns.tolist(), flush=True)

# Our ten DataDecide tasks, restricted to those every run of a type carries for that metric.
TEN = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu", "openbookqa", "piqa", "socialiqa", "winogrande"]
report = {"source": "allenai/signal-and-noise random_seeds", "bootstrap_draws": B, "results": []}


def cube(rt, metric):
    x = d[(d.run_type == rt) & (d.metric == metric) & d.task_name.isin(TEN)]
    piv = x.pivot_table(index=["run_name", "step"], columns="task_name", values="value", aggfunc="mean")
    runs = sorted(piv.index.get_level_values(0).unique())
    tasks = [t for t in TEN if t in piv.columns and all(piv.loc[r][t].notna().sum() > 0 for r in runs)]
    piv = piv[tasks].dropna()
    steps = None
    for r in runs:
        s = set(piv.loc[r].index)
        steps = s if steps is None else steps & s
    steps = sorted(steps)
    arr = np.stack([piv.loc[r].loc[steps].to_numpy() for r in runs])  # runs x steps x tasks
    return runs, tasks, np.array(steps), arr


def ckpt_cov(arr, W, detrend):
    S = 0
    dof = 0
    for r in range(arr.shape[0]):
        s, k = within_cov(arr[r, -W:, :], detrend)
        S = S + s
        dof += k
    return S / dof


def stats(arr, idx, W):
    fin = arr[idx, -1, :]
    win = arr[idx, -W:, :].mean(1)
    out = {
        "seed_final": lam(np.cov(fin, rowvar=False)),
        "seed_window": lam(np.cov(win, rowvar=False)),
        "ckpt_demean": lam(ckpt_cov(arr[idx], W, False)),
        "ckpt_detrend": lam(ckpt_cov(arr[idx], W, True)),
    }
    out["ratio_final_over_detrend"] = out["seed_final"] / out["ckpt_detrend"]
    out["ratio_window_over_demean"] = out["seed_window"] / out["ckpt_demean"]
    return out


for rt in ["seed", "data"]:
    for metric in ["acc_per_char", "bits_per_byte"]:
        runs, tasks, steps, arr = cube(rt, metric)
        R, T, K = arr.shape
        print(f"\n== run_type={rt} metric={metric}: {R} runs, {T} common steps (last {steps[-1]}), {K} tasks {tasks}", flush=True)
        if R < 4 or K < 3:
            continue
        for W in [5, 20, 30]:
            if T < W:
                continue
            point = stats(arr, np.arange(R), W)
            boots = [stats(arr, RNG.integers(0, R, R), W) for _ in range(B)]
            ci = {k: [pct([b[k] for b in boots], 2.5), pct([b[k] for b in boots], 97.5)] for k in point}
            # Heineman-style per-task proxy: seed SD at the final step over detrended checkpoint SD.
            sd_seed = arr[:, -1, :].std(0, ddof=1)
            Sc = ckpt_cov(arr, W, True)
            sd_ck = np.sqrt(np.diag(Sc))
            avg_seed = arr[:, -1, :].mean(1).std(ddof=1)
            avg_ck = float(np.sqrt(Sc.sum()) / K)
            row = {
                "run_type": rt, "metric": metric, "runs": R, "window": W, "tasks": tasks,
                "final_step": int(steps[-1]), "point": point, "ci95": ci,
                "per_task_seed_over_ckpt_sd": dict(zip(tasks, (sd_seed / sd_ck).round(4).tolist())),
                "average_seed_over_ckpt_sd": avg_seed / avg_ck,
                "task_level_r2_seed_vs_ckpt_sd": float(np.corrcoef(sd_seed, sd_ck)[0, 1] ** 2),
            }
            report["results"].append(row)
            print(json.dumps({k: row[k] for k in ["window", "point", "ci95", "average_seed_over_ckpt_sd"]}, default=float), flush=True)
            print("per-task seed/ckpt SD:", row["per_task_seed_over_ckpt_sd"], flush=True)

(OUT / "heineman_seeds.json").write_text(json.dumps(report, indent=1, default=float))
print("wrote", OUT / "heineman_seeds.json")
