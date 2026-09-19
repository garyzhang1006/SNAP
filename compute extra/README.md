# compute extra: the held-out scoring that Kaggle's quota can't reach

The registered held-out test (`heldout/PROTOCOL_heldout.md`) scores 375 DataDecide checkpoints on four unseen tasks and needs the 530M, 750M and 1B runs. Kaggle's 30 GPU hours a week covered 530M, 750M and 55 of the 75 runs at 1B. What remains is the last 1B shard, `s03`, which this folder runs on the SCU Slurm cluster with the same scorer, the same frozen request file and the same output format as the Kaggle shards, so the score files drop straight into the existing analysis kernel.

Everything here is self-contained: `common/` and `config/` are copies of `heldout/common` and `heldout/config` at the commit that scored the Kaggle shards, `data/requests.jsonl.gz` is the frozen request file (its SHA-256 is checked against `config/frozen.json` before any model loads), and `shards/` lists the runs. No file here holds a token, and every Hugging Face repository read is public.

## Quick start and status

From the repository root on a login node, two commands do the whole job:

```bash
bash "compute extra/setup.sh"
```

```bash
bash "compute extra/submit.sh"
```

What has been verified: `score_shard.py --dry-run` validates both shard types on CPU (frozen hash, run lists against `config/runs.json`, task names against the request file), every shell script passes `bash -n`, and the scorer, request file and output format are the ones that already scored the 530M and 750M shards on Kaggle. What has not: the GPU path on this cluster. Torch and `ai2-olmo 0.6.0` have only run inside Kaggle's image, so a fresh virtualenv may lack a transitive import; `setup.sh` installs the known set and its import check names anything still missing before any GPU job is submitted. The `s03` job is the real test, and its log under `/athena/accardilab/scratch/$USER/snap-extra/logs/` shows the packed-versus-reference check for each run.

The one remaining shard is 20 runs, about 12.3 T4 card-hours by the Kaggle estimate and far less on an L40S. Kaggle has already scored the other 55 runs at 1B (`s01`, `s02` and the twelve inside `s04`), so once `s03` finishes here the 1B scope is complete and the scores merge in the k04 kernel as described under "Bringing the scores back".

## What to run

| shard | runs | tasks | T4 card-hours (estimate) | status |
| --- | --- | --- | --- | --- |
| `s03` | the last 20 runs at 1B | sciq, medmcqa, drop_mc, coqa_mc | 12.3 | needed for the registered test at 1B |
| `x150M` .. `x1B` | all 75 runs at that size | logiqa_en, lsat_lr | 2.4, 4.3, 7.3, 10.1, 13.4 | optional, exploratory |

`s03` is the Kaggle shard `snap-new-k02-s03` with its run list and per-run estimates unchanged. Its twenty runs are dolma1.7-no-flan at seeds 4 and 5 and all three seeds of dolma1.7-no-math-no-code, dolma1.7-no-reddit, falcon, falcon-with-cc, falcon-with-cc-top-10p and falcon-with-cc-top-20p. Kaggle refused this shard on 2026-09-19 with its weekly GPU quota spent, and it has scored every other run in the 530M to 1B scope (`s01`, `s02` and `s04` to `s09`), so after `s03` finishes here every run has scores. The T4 estimates come from the pilot's measured 2,900 s per 1B run in float32 at 6,000-token batches; an L40S should take a fraction of that, and the job asks for 24 hours so a single T4-speed card would still finish a shard.

The `x` shards score the two AGIEval tasks that the registered protocol listed first and replaced under its backup rule, because their 1B pilot accuracy fell below chance plus 0.02. Scoring them on every run gives a six-task exploratory battery. Nothing in the registered analysis reads them, and their estimates are the four-task estimates scaled by item share, so treat those hours as rough.

## Order

1. Once, from the repository root on a login node. This builds a virtualenv on scratch inside an scu-cpu job, installs the pinned stack (`transformers==4.57.1`, `ai2-olmo==0.6.0`, torch), checks that the OLMo loader imports, and dry-runs `s03` against the frozen request file.
   ```bash
   bash "compute extra/setup.sh"
   ```
2. Submit the remaining 1B shard as one GPU job. Add `SBATCH_EXTRA="--gres=gpu:l40s:2"` for two cards per job, which halves the wall time.
   ```bash
   bash "compute extra/submit.sh"
   ```
3. Watch the logs under `/athena/accardilab/scratch/$USER/snap-extra/logs/`. A job that times out exits nonzero with the unfinished runs listed in `scores/shard_report_<shard>.json`; resubmit the same shard and it continues from the files already written.
   ```bash
   bash "compute extra/submit.sh" s03
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

`python "compute extra/score_shard.py" --shard "compute extra/shards/s03.json" --dry-run` validates every input without importing torch and prints how many runs remain.
