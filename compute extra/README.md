# compute extra: the held-out scoring that Kaggle's quota can't reach

The registered held-out test (`heldout/PROTOCOL_heldout.md`) scores 375 DataDecide checkpoints on four unseen tasks and needs the 530M, 750M and 1B runs. Kaggle's 30 GPU hours a week covered 530M and most of 750M. What remains is the 1B scope, which this folder runs on the SCU Slurm cluster with the same scorer, the same frozen request file and the same output format as the Kaggle shards, so the score files drop straight into the existing analysis kernel.

Everything here is self-contained: `common/` and `config/` are copies of `heldout/common` and `heldout/config` at the commit that scored the Kaggle shards, `data/requests.jsonl.gz` is the frozen request file (its SHA-256 is checked against `config/frozen.json` before any model loads), and `shards/` lists the runs. No file here holds a token, and every Hugging Face repository read is public.

## What to run

| shard | runs | tasks | T4 card-hours (estimate) | status |
| --- | --- | --- | --- | --- |
| `s01`, `s02`, `s03` | 20 runs at 1B each | sciq, medmcqa, drop_mc, coqa_mc | 12.3 each, 37 in total | needed for the registered test at 1B |
| `x150M` .. `x1B` | all 75 runs at that size | logiqa_en, lsat_lr | 2.4, 4.3, 7.3, 10.1, 13.4 | optional, exploratory |

The three `s` shards are the Kaggle shards `snap-new-k02-s01` to `s03` with the run lists and per-run estimates unchanged. The Kaggle queue still holds `s04` (the last 12 runs at 1B plus 10 at 750M), so after `s01` to `s03` finish here and `s04` finishes there, every run in the 530M to 1B scope has scores. The T4 estimates come from the pilot's measured 2,900 s per 1B run in float32 at 6,000-token batches; an L40S should take a fraction of that, and the job asks for 24 hours so a single T4-speed card would still finish a shard.

The `x` shards score the two AGIEval tasks that the registered protocol listed first and replaced under its backup rule, because their 1B pilot accuracy fell below chance plus 0.02. Scoring them on every run gives a six-task exploratory battery. Nothing in the registered analysis reads them, and their estimates are the four-task estimates scaled by item share, so treat those hours as rough.

## Order

1. Once, from the repository root on a login node. This builds a virtualenv on scratch inside an scu-cpu job, installs the pinned stack (`transformers==4.57.1`, `ai2-olmo==0.6.0`, torch), checks that the OLMo loader imports, and dry-runs `s01` against the frozen request file.
   ```bash
   bash "compute extra/setup.sh"
   ```
2. Submit the three 1B shards, one GPU job each. Add `SBATCH_EXTRA="--gres=gpu:l40s:2"` for two cards per job, which halves the wall time.
   ```bash
   bash "compute extra/submit.sh"
   ```
3. Watch the logs under `/athena/accardilab/scratch/$USER/snap-extra/logs/`. A job that times out exits nonzero with the unfinished runs listed in `scores/shard_report_<shard>.json`; resubmit the same shard and it continues from the files already written.
   ```bash
   bash "compute extra/submit.sh" s02
   ```
4. Optional: the exploratory two-task shards.
   ```bash
   bash "compute extra/submit.sh" --extras
   ```

## Bringing the scores back

The analysis kernel `heldout/kaggle/k04-analyze-heldout` gathers every `scores/*.npz` it finds under `/kaggle/input`, so the cluster output travels to Kaggle as a dataset:

```bash
mkdir -p upload/scores && cp /athena/accardilab/scratch/$USER/snap-extra/scores/*.npz upload/scores/
cd upload && kaggle datasets create -p . --dir-mode zip   # with a dataset-metadata.json naming <user>/snap-new-cluster-scores
```

Then add that dataset to `dataset_sources` in `heldout/kaggle/k04-analyze-heldout/kernel-metadata.json` and push the kernel with `heldout/tools/push.sh`. k04 checks each file's request hash, step and revision against `config/runs.json`, refuses duplicates silently only by taking the first in sorted order, and reports which sizes it treated as complete, so a partial upload is caught rather than analysed.

Only the `s` shards belong in that dataset for the registered test. The `x` shard files carry `tasks: [logiqa_en, lsat_lr]` in their metadata and k04 would reject them for lacking the final tasks, so keep them in a separate dataset for a separate, exploratory analysis.

## What the scorer does

`score_shard.py` starts one worker per visible GPU. Each worker downloads a checkpoint branch (config, tokenizer and safetensors only) into `$TMPDIR`, loads it in float32, scores the shard's tasks with `common/scorer.py`, which reproduces the OLMES log-likelihood path and checks its packed batches against a one-sequence reference on 16 items before trusting them, writes `<run_key>.npz` and deletes the checkpoint. A 1B checkpoint branch is 5.1 GB of safetensors on the hub, and float32 weights plus 6,000-token batches stayed within a 16 GB T4 on Kaggle. The output schema is the one `heldout/common/snapnew.py` reads.

`python "compute extra/score_shard.py" --shard "compute extra/shards/s01.json" --dry-run` validates every input without importing torch and prints how many runs remain.
