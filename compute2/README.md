# compute2: the evidence the reviews asked for, on two RTX 5090s

The paper's estimate, Lambda = 1.244 [1.143, 1.338] on margins over 375 DataDecide
runs, rests on one model family, on the release's own item set, and on a
three-seed design where two of the three seeds also change the batch. Four
blind panels scored the text at 4 to 4.5 of 10 and named the same three gaps:
a second model family with a clean seed design, a check that the inflation is
not carried by a shared item component (which needs a disjoint item bank), and
a reproduction of the headline on fresh items. This directory scores what those
three checks need and applies reading rules that were fixed before any run was
scored. It does not promise a result; the rules say what each outcome means.

Everything runs on the Vast.ai box (2x RTX 5090, 32 GB each, NVMe). Nothing
here needs a token: every repository read is public. If `HF_TOKEN` is set in
the shell it raises the anonymous rate limit and is never written to disk.

## What gets scored

Three request banks, all ten benchmarks of the paper, all five-shot OLMES
prompts except the zero-shot arm:

| bank | items | what it is |
|---|---|---|
| bank1 | 37,682 | the release's own request text for the items the paper scores, byte-identical prompts |
| bank2 | about 6,900 | disjoint items from the same benchmarks (train splits, MMLU validation), same OLMES commit and few-shot configs, capped at 600 per benchmark for the compute budget (MMLU validation holds about 1,531 and is not capped) |
| bank2zs | same as bank2 | bank 2's items at zero shots, same labels and continuations |

Two model families:

| family | runs | design |
|---|---|---|
| PolyPythias (GPT-NeoX) | 5 sizes (14m to 410m) x 9 seeds | every seed a clean re-run at one matched step (143,000), plus five earlier steps for the curve |
| DataDecide (OLMo) | 25 recipes x 5 sizes x 3 seeds = 375 | the paper's own runs, now scored on bank 2 and bank 2zs |

Jobs, in the order run_all.sh runs them (config/jobs.json):

| job | runs | bank | what it establishes |
|---|---|---|---|
| verify | 6 (c4, 150M and 1B) | bank1, five tasks | the scorer reproduces the release's per-item margins; gate for everything else |
| pythia_bank1_final | 45 | bank1 | R1: the paper's design on a second family with nine clean seeds |
| pythia_bank2_final | 45 | bank2 | R2 for PolyPythias: cross-bank against within-bank |
| datadecide_bank2 | 375 | bank2 | R3: the headline on fresh items; R2 for DataDecide with bank 1 from the release |
| pythia_bank1_curve (optional) | 225 | bank1 | Lambda across training at matched steps |
| pythia_bank2zs_final (optional) | 45 | bank2zs | cross-format check, five-shot against zero-shot |
| datadecide_bank2zs_1B (optional) | 75 | bank2zs | the same at 1B for the paper's family |

Cost, inferred from the measured 3090 rate (655 s for a 1B four-task run,
about 3,870 tokens per second). Bank 1 is about 14M tokens per run, so a 1B
run takes about 60 minutes on a 3090 and time scales with parameter count;
bank 2 at about 6,900 items is under a fifth of that. The core jobs come to
about 45 card-hours on 3090s: verify under one, pythia_bank1_final about 6,
pythia_bank2_final about 1, and datadecide_bank2 about 35 (the 1B band is
15 of those). On three 3090s that is about 16 hours of wall clock, with the
R1 and R2 readings in the first 4 hours and R3 at the end. The optional arms
add about 30 card-hours for the curve and about 10 for the two zero-shot
jobs. A 5090 should run about 1.6 times faster. Measure the verify job's
rate before trusting any of these.

The 600-item cap on bank 2 is a compute decision, made before scoring. Item
noise does not bias the estimator, whose numerator and denominator are both
cross-half covariances, but it widens the within-bank-2 interval that rule R3
reads, so a true 1.24 can come out as a lower endpoint above one or as an
interval that covers one. R1 and R2 are much less affected because bank 1
enters them with all 37,682 items. Raising the caps in config/banks.json and
rebuilding is the only change needed to buy the width back.

## Run it

```bash
git clone https://github.com/garyzhang1006/SNAP && cd SNAP
bash compute2/setup.sh          # venv, pinned stack, GPU check, banks built and frozen, dry run
bash compute2/run_all.sh        # release fetch, the four core jobs in order, reduce, analyse, report
bash compute2/run_all.sh all    # the same plus the three optional arms
```

`run_all.sh` is resumable: rerun it after any interruption and it continues
from the last finished run. A single job: `bash compute2/run_all.sh verify`.
Results land in `compute2/results/RESULTS.md` with the JSON beside it. The
scores and reduced files are the deliverable; the analysis is rerunnable on a
laptop from `compute2/reduced` and `compute2/data/release_runs`.

Individual steps, for when something needs a second look:

```bash
python compute2/requests/build_bank1.py            # release requests -> data/bank1_requests.jsonl.gz
python compute2/requests/build_bank2.py --zero-shot   # OLMES at the pinned commit -> bank2 and bank2zs
python compute2/requests/freeze.py                 # hashes into config/frozen.json
python compute2/score_runs.py --job verify --dry-run
python compute2/score_runs.py --job verify
python compute2/reduce.py --job verify
python compute2/analysis/estimates.py && python compute2/analysis/report.py
```

## Reading rules, fixed before scoring

The interval named in each rule is the one the verdict uses; the others are
reported beside it. Every number is exploratory with respect to the paper's
registration, and the paper says so wherever one is quoted.

V0, verification. Every verify run reproduces the release margins per item
with median absolute difference at most 0.002 and 99th percentile at most 0.02
nats per byte, and at least 99 percent agreement on correctness. If V0 fails,
nothing else is read; the scorer is fixed first.

R0, reproduction. The 375 release runs, reduced by the paper's own code and
joined here by recipe, size, seed and step, give the paper's 1.244 and 1.078
to within 0.005 when all 125 cells match. This checks the join, not the
paper.

R1, a second family replicates. On PolyPythias, bank 1, the paper's item split
and phenotypes, all five sizes at step 143,000, the delete-one-seed jackknife
interval (t with 8 degrees of freedom, endpoints square-rooted) for margins
has a lower endpoint above one. The jackknife is primary because nine seeds
are the replicate unit and the size clusters are five, too few for the wild
bootstrap. Reported alongside: the recipe-clustered wild bootstrap-t, the
cluster t interval, the configuration bootstrap, per-size estimates, and the
same without BoolQ.

R2, identification against a shared item component. If the inflation were an
artefact of the two halves sharing an item-level component, it would vanish
when A and B are disjoint banks. The cross-bank estimate uses every bank-1
item as A and every bank-2 item as B on the same runs. The shared-item
explanation is not supported when the cross-bank interval sits above one and
the within-minus-cross difference (delete-one-seed jackknife of the log ratio
difference for PolyPythias, recipe-cluster percentile bootstrap for
DataDecide) includes zero. It is supported when the difference is positive
and the cross-bank interval covers one. Anything else is undecided and is
reported as undecided. Note the cross-bank estimate also carries any format or
distribution difference between the banks, which the zero-shot arm probes.

R3, the headline on fresh items. Within bank 2 on the 375 DataDecide runs,
halves balanced within every task, the paper's recipe-clustered wild
bootstrap-t (25 clusters, t(24), 4,999 draws, seed 0) for margins has a lower
endpoint above one. Reported alongside: batch-free contrasts, per size band,
accuracy, without BoolQ.

The curve and the cross-format arms are descriptive and optional; no rule reads them.

## What the outcomes mean for the paper

If V0, R1 and R3 pass and R2 says not supported, the paper gains what the
panels asked for: a second family with a clean seed design, a disjoint-bank
identification, and the headline reproduced on fresh items. The text can then
say the inflation is not an artefact of one family, one item set, or the
batch confound. That is the case for a 6.

If R1 fails, the PolyPythias interval covers one, and the paper has to say so:
five sizes by nine seeds is 40 within-configuration contrasts against the
paper's 250, so the interval will be wide, and a null result there is a
power statement as much as an effect statement. The per-size jackknives say
which sizes carry it. On the synthetic population in tests/, five sizes by
nine seeds gives draws from 0.94 to 1.36 around a true 1.24, so a wide
interval is the expected shape, not a failure of the code.

If R2 says supported, the paper's construct changes: the inflation is at
least partly a shared item component, and the cross-bank estimate is the
number to report. If R3 fails, the 1.244 does not survive fresh items and the
paper cannot keep it as the headline.

None of these outcomes is guaranteed by this code, and the code does not
choose among them. The job order puts R1 and R2 first so a stop after five
hours still returns a reading.

## Layout

```
common/tasks66.py      task order, traits, item-id spaces (vendored; asserted equal to seednoise's)
common/bank.py         request files, choice tables, per-item reduction, no torch
common/scorer.py       OLMES log-likelihood scoring for OLMo (hf_olmo) and GPT-NeoX (transformers)
config/banks.json      bank specs, OLMES commit, scoring config, verification thresholds
config/jobs.json       jobs; runs_pythia.json and runs_datadecide.json are the manifests
config/frozen.json     request-file hashes, written by requests/freeze.py, checked by every job
requests/              bank builders and the freeze step
make_manifests.py      writes the run manifests and jobs
score_runs.py          one worker per GPU, resumable, prefetching, hash-gated
reduce.py              score files -> seednoise run format
analysis/estimates.py  the estimator, the intervals and the rules; imports src/seednoise
analysis/report.py     results/*.json -> results/RESULTS.md
tests/                 CPU-only checks (python -m pytest compute2/tests)
setup.sh env.sh fetch_release.sh run_all.sh
```

Pinned: transformers 4.57.1 (transformers 5 removed what hf_olmo needs),
ai2-olmo 0.6.0 without dependency resolution, OLMES commit
5a51f502d463b8cdc4a2dcad7d7096c41ff1197e for bank 2, torch 2.8 or newer with a
CUDA 12.8 build for the 5090's compute capability 12.0. The GPU parts have not
been run; the CPU parts are covered by the tests, and the scorer copies the
held-out scorer that was verified against the release on a 3090.
