# Hostile ICLR review, 2026-09-19

Reviewer stance: area-chair-adjacent reviewer who rejects by default and accepts only what survives every attack. Every number in the main text was traced to a kernel output before this review was written, and the tracing is recorded below so the score rests on evidence rather than on tone.

## Numerical audit (OBSERVED)

All 219 distinct numbers in the abstract through Section 7 were extracted by script and searched in the appendices, the supplement and the research outputs. 180 also appear in the appendices or supplement. The 39 that appear only in the main text were each located in a kernel output file, and the derived quantities were recomputed by hand from their inputs.

| Main-text claim | Source | Check |
|---|---|---|
| Held-out margin 1.201, interval 0.546 to 1.616 | research/outputs/snap-r11-composition/r11_composition.json, research/results/simulation_cells.csv | present |
| Held-out accuracy 1.327 | research/outputs/snap-r6-matched-b/.../tab_resplit.csv | present |
| K_eff column of Table 1 (6.46, 6.15, 6.34, 8.60, 8.31, 8.51) | recomputed as 10 divided by the squared factor | all six agree to two decimals |
| r_E upper bound 0.038 and K_eff lower bound 7.47 at 1.157 | recomputed from Equation 4 | 0.0376 and 7.47 |
| BoolQ off-diagonal sums of about minus 0.15 and minus 0.06 of the trace | recomputed from 1.244, 1.786, 0.68 and 1.078, 1.558, 0.84 | minus 0.153 and minus 0.066 |
| Batch-offset factors 1.004 and 1.003, about 1.5 percent of the excess | tab_nulls.csv row N6, means 1.00375 and 1.00298 | 0.00375 over 0.244 is 1.54 percent |
| Binomial 25 choose 17 equals 1,081,575 | arithmetic | correct |
| Information ratio 1.66 at p equal to 0.35 and minimum pi over 2 | recomputed from Equation 6 | 1.657 and 1.571 |
| Flip probabilities 0.246, 0.085, 0.229, 0.069 | recomputed from Equation 7 with 0.00514 and 0.00514 divided by 1.078 | 0.2458, 0.0844, 0.2292, 0.0690 |
| PolyPythias excess ratio 1.66 and factor ratio 1.13 | recomputed from 1.406 and 1.244 | 1.664 and 1.130 |
| Test-inversion shift of 0.048 | 1.143 minus 1.095 | correct |
| Truncation ranges 39 to 89 percent and 18 to 44 percent | appendices_bcd.tex reports 38.9 to 88.7 and 17.7 to 44.0 | rounding consistent |

Citations: 53 bibitems, 53 cited keys, zero undefined citations or references in main.log and supplement_extended.log. Abstract: 299 words, every number present in the body with the same value.

No numerical, arithmetic or cross-reference defect was found. Nothing in this section changes the score, because the score is capped by what the study shows rather than by how it is written.

## Attacks that stand (these cap the score)

1. The only confirmatory result failed. The registered test on four unseen tasks returned 1.201 with a lower limit of 0.546, and the paper's own power table says the rule passes in 0.785 of replicates at the true ratio under margin-like noise, so a failure at this width carries little information either way. A hostile reader concludes that the paper has one pre-registered claim and it did not pass. The text says exactly this, which is honest, but honesty about a failed test is not evidence of transfer.

2. The accuracy result is a bound, not a finding. The full-battery accuracy interval 0.993 to 1.157 includes one, five of 25 recipe removals flip that, and the earlier-checkpoint interval 1.044 to 1.210 excludes one. The paper's central practical quantity on the scale most people report is therefore undetermined on this battery.

3. The estimand moves with the battery. Removing BoolQ takes margin inflation from 1.244 to 1.786 and accuracy from 1.078 to 1.558. Subsets containing BoolQ sit 0.115 to 0.596 lower than those without it. A reviewer asks what quantity the paper measured, and the answer is the covariance of one fixed ten-benchmark battery, which the paper concedes.

4. The decision analysis undercuts the motivation. On real recipe comparisons checked against the 1B ordering, the covariance-based standard error changes the wrong-call share by at most 0.009 and every bootstrap interval for that change reaches zero. The introduction motivates the work with a false-positive rate that rises from 0.05 to 0.113 in simulation, and the paper's own empirical check finds almost no decision changes. A hostile reviewer reads that as the simulation overstating the stakes.

5. Provenance gaps. The analysis plan has no independently corroborated timestamp, its screening split was never formed, the 1B held-out scoring was unfinished at submission, and the registered test was amended twice for task replacement and scope. Each is disclosed, and disclosure is the right response, but a reviewer who does not want to accept anyone will cite them.

6. Novelty is modest. The cross-half product is the split-half reliability construction from Spearman and Cronbach applied across benchmarks. The contribution is the estimand definition, the assumption audit and the empirical measurement on DataDecide, not a new estimator.

7. Training-schedule confounds. Ninety-two configurations have mismatched final steps, the 750M selected step averages 41.5 percent of the default run's final step, and auxiliary replicates use different budgets. The paper interprets the estimate as covariance among released runs at selected steps, which is correct, but that is a weaker estimand than the one the title suggests.

## Attacks that do not stand

- "The intervals are not calibrated." Simulated coverage 0.928 to 0.954 across twelve populations, with the configuration percentile bootstrap shown to drop to 0.872, is stronger interval validation than most ICLR empirical papers carry.
- "Item leakage explains 1.244." The passage-aware BoolQ split moves the estimates by 0.0002 and 0.0001, and the within-group permutation gives a tail fraction of 0.087 with spread 0.0009. Leakage is bounded, though an unmeasured 0.124 item-variance share could still reproduce the number, and the paper says so.
- "Three seeds are too few." Coverage holds between 0.942 and 0.952 from two to ten runs per configuration.
- "The numbers do not match." Every number traced.

## Score

ICLR scale, 1 to 10. Score: 6, marginally above the acceptance threshold. Confidence 4 of 5.

Why not 8 or higher: attacks 1, 2 and 4 are about what the data show, and no rewrite changes them. An 8 requires a confirmatory result that passed or an empirical decision effect that matters. The paper has a registered test that failed at low power and a decision effect of at most 0.009.

Why not 5 or lower: the interval machinery is validated by simulation, the composition and leakage checks are thorough, the registered test exists and its failure is reported without spin, and every number reproduces. A reviewer who marks this below 6 is penalising honesty about a null result.

What would move it: the 1B held-out shards finishing with a lower limit above one at all three sizes would turn attack 1 into a strength, and that is the only pending item with score leverage. Text edits cannot move the score above 6 and this review does not pretend otherwise.

## Style verdict for the rewrite phase

Zero colons and semicolons in any paper file. Zero contractions before the rewrite. Sentence standard deviation 6.6 words on the main text against 11.9 in the 23-paper human corpus, which is the one measured gap the rewrite phase can close.
