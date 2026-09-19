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

**2026-09-18, re-freeze of the request file.** A rebuild of the request file at the pinned OLMES commit produced different group labels on the four tasks whose passage groups come from the prompt fallback, logiqa_en, lsat_lr, drop_mc and coqa_mc. The builder labelled those groups with Python's built-in hash(), which is salted per process, so no two builds agreed. The fallback now uses the first twelve hex digits of SHA-256 over the passage text. Comparing the two files line by line, the group field is the only one that changed, and on each of the four tasks the partition of items into groups is identical, so the prompts, continuations, labels and item order the scorer reads did not move. The file hash moved from 53a06cf0 to 06a95796, and `config/frozen.json` records both.

When this entry was written the pilot had finished, so the six c4 pilot runs hold scores on every task in the file, the held-out tasks included. None of those scores has been read for anything other than what the protocol already assigns them, namely the ARC-Easy seed check and the backup rule's accuracy bar in k03. The scores stay valid under the new file because they are keyed by task, document and choice, never by group. Group labels only enter the half split at analysis time, which k04 reads from the new file.

CoQA still gets one group per item, 1,000 groups for 1,000 items, because its prompt carries no question marker for the fallback to split on. It is a backup task and the secondary analysis is the only place it can enter, so we leave its grouping as built and report it.

**2026-09-18, backup rule outcome and production scope, before any production score existed.** k03 applied the backup rule to the pilot's three 1B c4 runs. LogiQA-en scored a mean accuracy of 0.2688 against a bar of 0.27 and LSAT-LR scored 0.2190 against 0.22, so both fell below chance plus 0.02 by about a thousandth and the rule replaced them with drop_mc and coqa_mc in the listed order. The primary battery is therefore sciq, medmcqa, drop_mc and coqa_mc. Both misses are narrow, and we apply the rule as written because it was fixed before these accuracies were read.

The pilot timing projects 66.0 Kaggle session hours for all 375 runs on these four tasks, so the scope fallback applies and production scores the 225 runs at 530M, 750M and 1B, projected at 54.9 session hours. That already exceeds one week of Kaggle GPU quota, so the six-task secondary analysis promised in the 2026-09-17 entry is withdrawn and production does not score logiqa_en or lsat_lr. Shards run in the order 530M, 750M, 1B. If the quota runs out before the submission deadline, the paper reports the test on the sizes that finished, says which sizes are missing, and labels the test as modified.

CoQA is now a primary task, and its fallback grouping gives one group per item, which would let questions about the same story land in both halves of the split. Group labels only enter at analysis time, so before k04 reads any production score we will regroup coqa_mc by story with a deterministic key over the story text, record the new request hash here, and leave the scored prompts untouched. The rebuilt file changes the group field on 932 coqa_mc rows and nothing else, gives 479 story groups for the 1,000 items, and moves the request hash from 06a95796 to 77118327. Production shards s08 and s09 were already running on the 06a95796 file, which is identical apart from these labels.

**2026-09-18, interim result at 530M and a comparison added after it.** The weekly GPU quota ran out after the 530M shard and part of the 750M shard. Until more sizes finish, the paper reports the test as modified to 530M under the scope-fallback clause above. The remaining 137 runs sit in shards s01 to s06, which `plan.json` projects at 38.4 session hours, and the three finished shards came within 0.4 hours of their projections. That exceeds one week's 30-hour quota, so 1B can't finish before the full-paper deadline of 2026-09-25, while the 750M runs in s04 to s06 need about 19.0 hours and can finish if the quota resets in time. On the 75 runs at 530M, held-out margin Lambda is 1.198 [0.864, 1.454] and the test fails. After reading that number we ran k06 again restricted to 530M (`snap-new-k06-power-530m`) and to the fallback sizes (`snap-new-k06-power-fallback`), so that the battery-size curve matches the scope of the test. Those two runs are exploratory, the paper says they came after the held-out result, and the all-size k06 curve fixed in the 2026-09-17 entry stays in the paper beside them. If 750M finishes before submission, k04 reads 530M and 750M, names 1B as missing, and that result replaces the 530M one in the paper.

**2026-09-18, comparison for a 530M and 750M result, fixed before any 750M held-out score.** We ran k06 on the original ten benchmarks at 530M and 750M (`snap-new-k06-power-530m750m`) while no 750M held-out score existed. The full original battery gives margin Lambda 1.316 [0.880, 1.637] at that scope, and 0.55 of 60 four-benchmark subsets exclude one. `HELDOUT_WORDING.md` fixes the paper text for a pass and for a fail of the 530M and 750M test, and `kaggle/k04-analyze-heldout/build/snap-new-k04-heldout-530m750m` is the analysis build, prepared and not yet pushed.

**2026-09-19, power of the rule at each scope and a per-size build, fixed before the 530M and 750M analysis ran.** The 750M shards s05 and s06 finished overnight and s04, which holds the last ten 750M runs and twelve 1B runs, was still scoring when this entry was written, so no 750M held-out score had been read. Three CPU kernels (`snap-new-k12-rule-power-n073`, `-n100`, `-n145`) simulate the registered rule at the scopes of one, two and three sizes with four traits, 25 recipe clusters and three runs, sweeping the true Lambda over 1.00, 1.10, 1.20, 1.244, 1.316, 1.40 and 1.50 at item-noise levels 0.73, 1.00 and 1.45, with 4,000 replicates per cell. Their pass rates give the rule's size and its power against the shipped 1.244 at the scope the test takes, and the paper reports them next to the verdict. An exploratory build `snap-new-k04-heldout-750m` runs the same analysis on the 75 runs at 750M alone, listed here under the per-size breakdown the protocol already marks as reported but not part of the test. The first 1B shard s01 was pushed to the freed GPU slot; its scores are not read by the 530M and 750M analysis, and 1B enters only if s01 to s04 all finish before submission, in which case k04 runs at the full registered scope and the paper reports that result in place of the two-size one.

**2026-09-19, result at 530M and 750M.** Shard s04 finished at 10:29 EDT and `snap-new-k04-heldout-530m750m` ran on the 150 runs at 530M and 750M, with the twelve scored 1B runs and the three pilot 150M runs left unused. It reproduced the shipped margin estimate of 1.24395, and held-out margin Lambda is 1.2008 [0.5456, 1.6157], so the test as modified to those two sizes fails. Held-out accuracy Lambda is 1.3268 [1.1529, 1.4840]. The paper now carries this result under the fail wording in `HELDOUT_WORDING.md`, with the held-out estimate at the 50th percentile of the 60 four-benchmark subsets fixed on 2026-09-18, and it keeps the 530M interim in the appendix as an earlier result.
The three k12 kernels finished the same morning. At two sizes and a true Lambda of 1.244 the rule passes in 0.785, 0.631 and 0.371 of replicates at noise 0.73, 1.00 and 1.45, with size 0.015 to 0.017 at a true Lambda of one, and the median simulated interval width at accuracy-like noise is 0.530 against the observed 1.070. The exploratory 750M-only run gives held-out margin Lambda 1.2029 [undefined, 1.8283] and accuracy 1.2991 [0.9594, 1.5840].
After seeing the observed two-size width of 1.070, which exceeds the 0.530 median of the noisiest fixed cell, we ran the same kernel at noise 2.00, 2.50 and 3.00 (`snap-new-k12-rule-power-n200`, `-n250`, `-n300`). Those rows are marked as added after the result. At 2.50 and 3.00 the two-size median widths are 0.972 and 1.146, the pass rate at a true 1.244 is 0.115 and 0.080, and coverage falls to 0.699 and 0.562 with 0.280 and 0.425 of intervals lacking a lower limit.

**2026-09-19, first production 1B shard.** Shard s01 (`snap-new-k02-s01`) finished at 17:56 EDT with 20 of 20 runs at 1B scored and none failed, on the request file with hash 77118327b441931a17a2d2e90ee8e162c0192c99b472f2eedf0bad99a0025c43, in 28,481 wall seconds. Its 20 runs don't overlap the 12 that s04 scored, so 32 of the 75 runs at 1B now hold held-out scores. Shard s02 was still running when this entry was written. No 1B analysis has been run, the reported test still reads 530M and 750M, and the 1B result will be reported as a third size only once every 1B shard has finished, with the same rule and the same interval construction.
