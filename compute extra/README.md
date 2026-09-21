# compute extra: every piece of compute for the SNAP paper

All four compute trees live here now, and the Slurm path is retired. What remains
of the registered held-out test runs on Kaggle, which is the same route that
scored every shard except one.

| folder | what it holds |
| --- | --- |
| `heldout/` | the registered held-out package, with the protocol, the k01 to k12 Kaggle kernels, their outputs, the shared library and the tools that build, push and pack them |
| `primary/` | the primary reduction that the supplement ships as `snap_compute/` |
| `research_kernels/` | the 146 research kernels behind the appendices, one directory per kernel with its script and metadata |
| `cluster/` | the retired Slurm scripts, kept for the record and no longer the way in |
| `shards/`, `common/`, `config/`, `data/`, `score_shard.py` | the standalone scorer, its frozen request file and the shard definitions |

`common/` and `config/` are copies of `heldout/common` and `heldout/config` at the
commit that scored the Kaggle shards, and `data/requests.jsonl.gz` is the frozen
request file, whose SHA-256 is checked against `config/frozen.json` before any
model loads. No file here should hold a credential, so read the Kaggle and
Hugging Face tokens from the environment.

## Nothing is left to run

The registered test scores 225 DataDecide checkpoints on sciq, medmcqa, drop_mc
and coqa_mc across 530M, 750M and 1B, and every shard now has scores.

| shard | runs | scores on disk |
| --- | --- | --- |
| `s01`, `s02` | 20 each at 1B | 20 and 20, scored on Kaggle T4 cards |
| `s03` | 20 at 1B | 20, scored on three RTX 3090 cards on 2026-09-21 after the Kaggle quota ran out |
| `s04` to `s09` | mixed 750M and 1B | 22, 26, 26, 32, 37 and 19 |

The `s03` scores live in the private Kaggle dataset `snap-new-s03-scores`, and
`heldout/kaggle/k04-analyze-heldout/build/snap-new-k04-heldout-full` is the
analysis that read all 225 runs. Its result, held-out margin inflation 1.217
with interval 0.872 to 1.498, is what the paper reports.

## Running a shard on Kaggle

```bash
python3 "compute extra/make_kaggle_shard.py" --list
```

```bash
python3 "compute extra/make_kaggle_shard.py" s03
```

That writes `build/snap-new-k02-s03/` with the kernel and its metadata, private,
on two T4 cards, attaching the `snap-new-code` dataset and the `snap-new-k01-requests`
kernel exactly as `s01` and `s02` did. The kernel body comes from
`heldout/kaggle/k02-score/k02-score-template.py` through the same `write_kernel`
that `heldout/tools/make_shards.py` uses, so the metadata cannot drift from the
shards that already ran. Push it with the Kaggle CLI, which reads its credentials
from the environment.

```bash
kaggle kernels push -p "compute extra/build/snap-new-k02-s03"
```

The shard is 20 runs at 1B, about 12.3 T4 card-hours spread over two cards inside
a deadline of 8.4 hours. Kaggle refused it on 19 September 2026 with the weekly
cap reached, so it ran on three RTX 3090 cards instead, in 6,068 seconds.

The `x150M` to `x1B` shards score the two AGIEval tasks that the protocol listed
first and replaced under its backup rule, after their 1B pilot accuracy fell below
chance plus 0.02. Nothing in the registered analysis reads them, and their
estimates are the four-task estimates scaled by item share, so treat those hours
as rough.

## Bringing the scores back

`heldout/kaggle/k04-analyze-heldout` gathers every `scores/*.npz` it finds under
`/kaggle/input`, so a shard that runs as its own kernel needs that kernel added to
`dataset_sources` or `kernel_sources` in `heldout/kaggle/k04-analyze-heldout/kernel-metadata.json`
before it is pushed with `heldout/tools/push.sh`. k04 checks each file's request
hash, step and revision against `config/runs.json`, takes the first of any
duplicate in sorted order, and reports which sizes it treated as complete, so a
partial upload is caught rather than analysed.

Only the `s` shards belong in that analysis. The `x` shard files carry
`tasks: [logiqa_en, lsat_lr]` and k04 rejects them for lacking the final tasks,
so keep them separate and exploratory.

## What the scorer does

`score_shard.py` starts one worker per visible GPU. Each worker downloads a
checkpoint branch, config, tokenizer and safetensors only, into `$TMPDIR`, loads
it in float32, scores the shard's tasks with `common/scorer.py`, which reproduces
the OLMES log-likelihood path and checks its packed batches against a
one-sequence reference on 16 items before trusting them, writes `<run_key>.npz`
and deletes the checkpoint. A 1B checkpoint branch is 5.1 GB of safetensors on
the hub, and float32 weights with 6,000-token batches stayed inside a 16 GB T4.
The output schema is the one `heldout/common/snapnew.py` reads.

```bash
python3 "compute extra/score_shard.py" --shard "compute extra/shards/s03.json" --dry-run
```

That validates every input without importing torch and prints how many runs
remain. It is the check to run before spending a GPU hour.

## The retired cluster path

`cluster/` holds `setup.sh`, `env.sh`, `submit.sh` and `run_shard.sbatch`, which
submitted these shards to an SCU Slurm partition. They are kept because the
scorer they call is the same one, and because the paper's compute record should
show what was built. Their GPU path was never exercised, since torch and
`ai2-olmo 0.6.0` only ever ran inside Kaggle's image, and `env.sh` reads a
`hf_token` file that belongs in the environment rather than in a repository.
Nothing in the current workflow calls them.
