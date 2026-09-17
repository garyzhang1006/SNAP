# Held-out test protocol

This file fixes the held-out test before any held-out score exists. It counts as registered once `config/frozen.json` is committed, and the commit time of that file is the registration time. Anything decided after that commit is reported as exploratory.

## Question

The paper estimates Λ̂, the ratio of the seed standard deviation of an aggregate benchmark score to what independent traits would predict, at 1.244 [1.143, 1.338] for per-byte margin and 1.078 [0.993, 1.157] for accuracy, on ten traits and 375 DataDecide runs. A reviewer can fairly say those ten traits were the ones we looked at while building the method. The held-out test asks whether the excess correlation shows up on four tasks the estimate never saw, scored on the same 375 checkpoints at the same steps.

## Primary test

The population is the 125 DataDecide configurations (25 recipes at 150M, 300M, 530M, 750M and 1B, three seeds each) at the steps recorded in `config/runs.json`, scored on the final held-out tasks.

The statistic is `seednoise.estimator.estimate(pop, "margin", which="all")` at the paper's seednoise commit. Traits are the held-out tasks, each trait score is a plain item mean, and halves come from `seednoise.halves.split_clustered` on passage groups with seed 20260917.

The interval is `seednoise.inference.wild_bootstrap_t(T, U, pop.recipe, n_boot=4999, seed=0)`, a 95% wild cluster bootstrap-t over the 25 recipes.

**Pass rule.** The test passes if the lower 95% limit for held-out margin Λ̂ is above 1. Otherwise it fails. Held-out accuracy is reported next to it and doesn't enter the rule, because the paper's own accuracy interval already includes 1.

We report the result in the paper whichever way it comes out, next to the original-trait estimate restricted to the same sizes.

## Tasks

The OLMES harness at commit `5a51f502d463b8cdc4a2dcad7d7096c41ff1197e` builds every prompt and continuation, using the aliases in `config/tasks.json`:

- SciQ (`sciq:rc::olmo3`), all test items.
- MedMCQA (`medmcqa:rc::none`), 1,000 items drawn with seed 20260917.
- AGIEval LogiQA-en (`agi_eval_logiqa-en:rc::none`), all items, grouped by passage.
- AGIEval LSAT-LR (`agi_eval_lsat-lr:rc::none`), all items, grouped by passage.

None of the four is among the paper's ten traits (ARC-Challenge, ARC-Easy, BoolQ, CSQA, HellaSwag, MMLU, OpenBookQA, PIQA, SocialIQA, WinoGrande).

**Backup rule.** A held-out task is replaced only if the pilot's three 1B runs give it mean accuracy below chance plus 0.02, where chance is the mean of one over the choice count across its items. Replacements come in this order: DROP as multiple choice (`drop:rc::gen2mc`), then CoQA as multiple choice (`coqa:rc::gen2mc`), each capped at 1,000 items. The rule reads accuracy only. k03 applies it and writes the outcome to `decision.json`.

## Checks that gate scoring

1. `config/frozen.json` holds the SHA-256 of the request file. Every scoring kernel refuses to run on any other file.
2. The seed-to-branch mapping in `config/runs.json` is an assumption until k03 checks it. The pilot scores ARC-Easy (300 items) on c4 at 150M and 1B, and k03 compares each hub checkpoint with every release seed of its size. A hub run is verified only if its assumed seed alone matches, meaning no label or choice-count mismatches, a median absolute per-choice difference of at most 0.002 nats per byte, and a 99th percentile of at most 0.02. Production scoring doesn't start until all six runs are verified. The same comparison tests that our scorer reproduces OLMES's numbers.
3. Before each run is scored, the cached scorer is compared with the one-sequence reference path on a spread of items and must agree within 0.001 nats. Otherwise the run falls back to a slower path that does agree.
4. k04 recomputes margin Λ̂ from the 375 shipped reduced runs and stops unless it reproduces 1.24395 to within 0.0005.

## Scope fallback

If the pilot timing projects more than 30 Kaggle session hours for all 375 runs, only the 530M, 750M and 1B runs are scored (225 runs, 75 configurations). The pass rule stays the same on that population, and the paper states the reduced scope. `tools/make_shards.py` makes this call from measured pilot timing and records it in `plan.json`.

## Reported but not part of the test

These results are exploratory, and the paper labels them that way:

- the batch-free contrast on the held-out population,
- the 14-trait combined population,
- leave-one-task-out on the held-out tasks,
- everything k05 computes (wrong-call rates, power, the seed-count rule),
- any per-size breakdown.

## Changes after freezing

Don't edit `config/frozen.json` or the `heldout` block of `config/tasks.json` after the freeze commit. If a change becomes unavoidable, for example because an OLMES task fails to build, add a dated entry below that names the change and the reason and says whether any held-out score had been seen. The paper then reports the test as modified.

**2026-09-17, before any held-out score existed.** k06 measured what battery size costs, by reading every subset of the paper's ten benchmarks on the 375 shipped runs and taking a wild cluster bootstrap-t interval for each one. Four-benchmark batteries give a median margin Lambda of 1.176 and exclude one in 0.57 of 60 subsets, against 1.244 and a certain exclusion for the full ten. Lambda rises with the number of benchmarks, so the held-out four-task estimate is a smaller quantity than the headline by construction, and the primary pass rule has roughly even odds of firing even if the held-out tasks correlate like the shipped ones.

Two things follow, and neither touches the primary test above. The paper will not present a held-out Lambda as a replication of 1.244, and it reports the k06 curve next to the held-out number so a reader can see what battery size alone explains. Production also scores the two backup tasks on every run rather than only when the backup rule fires, which makes a six-task battery available, and its estimate is pre-registered here as a secondary analysis with the same statistic, the same interval and the same pass rule. The primary test stays the four tasks the backup rule selects. No held-out score had been produced when this entry was written, and the only scores in hand were ARC-Easy verification scores on c4.

