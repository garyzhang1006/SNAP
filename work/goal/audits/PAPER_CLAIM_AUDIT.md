# Paper Claim Audit: SNAP main text at f4d6c8d

Date 2026-09-24. Auditor: Claude Opus 5.5 in session, not the fresh cross-model thread the skill asks for (no codex tool here, and the goal forbids agents).

Verdict: PASS (all_numbers_match), with the caveat below.

The mechanical half (work/goal/claim_trace.py) matched every decimal of the main text, floats included, to some numeric leaf among 833 result files at the displayed precision. With 476,991 leaves a coincidental match is likely for any single three-decimal number, so this pass proves only that no number is wholly absent. The manual half traced the load-bearing numbers to named keys.

| Paper | Source key | Raw value |
|---|---|---|
| 1.244 [1.143, 1.338] | results/snap-r2-r1-08/r1_08_fixed_bank.json all_ten/margin/split_half_snap | rounds to paper |
| 1.078 [0.993, 1.157] | same file, all_ten/accuracy/split_half_snap | rounds to paper |
| 1.237 | same file, all_ten/margin/fixed_bank/lambda | rounds |
| 1.285 and 1.558 without BoolQ | same file, no_boolq/accuracy fixed_bank and split_half_snap | rounds |
| 1.786 | same file, no_boolq/margin/split_half_snap | rounds |
| 1.217 [0.872, 1.498] | compute extra/heldout/outputs/k04-heldout-full/heldout_results.json heldout margin/all | 1.21651, 0.87217, 1.49823 |
| 1.240 [1.054, 1.397] | same, original_traits_same_sizes/margin/all | 1.2404, 1.054, 1.3974 |
| 1.220 [1.066, 1.359] | same, heldout accuracy/all | 1.2196, 1.066, 1.3593 |
| 1.302 [0.921, 1.595] | results/pythia-bank1-final/pythia.json within_bank1/full/margin/all jackknife | 1.30222, 0.92066, 1.59498 |
| 0.921 cross-format | results/snap-r3-r2-02/r2_02_shared_component_crossformat.json margin/observed/cross_format_point | rounds |
| 0.319 | results/snap-r5-shared-bound/r5_shared_bound.json fraction_of_excess_lambda_scale | rounds |
| 0.259 | results/snap-r2-r1-18b/r1_18b_jackknife_recentring.json pass_rate_recentred_jackknife | rounds |
| 0.761 | results/snap-r2-r1-18/r1_18_rule_two.json run_cov_1244_share0/rates/undecided | rounds |
| 0.113 | research/LEDGER.md snap-r9-decision entry, 0.1133 | rounds |
| 0.115 | analytic, 2(1 - Phi(1.96/1.244)) = 0.11513 | rounds |

No number inflation, best-seed selection or delta error was found. The 0.113 comes from a ledger entry, not a raw file in the repo, so it counts as ambiguous_mapping until the snap-r9-decision output is located.
