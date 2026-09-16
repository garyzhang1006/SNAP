# R1. Estimand specification for SNAP on DataDecide

Written 2026-09-15 before any grouped BoolQ estimate was opened. Labels: OBSERVED means read from code or data this session, REPORTED means taken from the draft or an earlier result table.

## Three targets that the draft has been mixing

Target 1 is the run variance of the benchmark average on this fixed item bank. It treats the 37,682 items as fixed, treats the 375 released runs as the only random quantity, and asks how much an equally weighted average of the ten benchmark scores moves from one released run to another within a configuration. Repeated evaluation of the same items on new runs is what this target describes, and a practitioner who reruns training and rescores the same bank sees exactly this quantity. Item-specific run effects, where a run happens to parse one passage well, belong inside this target.

Target 2 is the item-general run covariance under an item population model. Each benchmark's items are treated as a sample from a larger population of items, the run effect E_crj is the part of the run deviation that would persist on fresh items from that population, and the item error epsilon is what would change. The cross-half identity in Equation eq:identity of the draft estimates this covariance, diagonal included, only when the errors on half A and half B are conditionally uncorrelated given the run. Two BoolQ questions on one passage violate that condition when they land in different halves, so the current estimator sits between target 1 and target 2 for the BoolQ diagonal. This is the target the draft's Lambda, K_eff and r_bar_E refer to, and it is the one the repaired analysis will keep.

Target 3 is variation over a population of benchmark batteries. Leave-one-benchmark-out sweeps and the standardised-trait diagnostics describe sensitivity of the fixed-battery quantity to composition, and the draft already says they are not draws from a benchmark population. Nothing in R2 or R3 changes that. Passage grouping changes the item sampling design within one benchmark, and it does not by itself say anything about batteries.

## What is random and what is fixed in the repaired analysis

Configurations are fixed design cells, 25 recipes by 5 sizes, and the recipe is the cluster for inference because configurations that share a recipe share training data (OBSERVED in inference.py). Runs are random within a configuration, with R equal to 3 and the R minus 1 divisor coming from the identity rather than a Bessel correction (OBSERVED in estimator.py). Items are random under target 2 and fixed under target 1. The half assignment is a frozen function of the master seed 20260101 and the trait labels (OBSERVED in halves.py), so it is a design constant and not a source of sampling variation. Repeated re-splits therefore measure algorithmic sensitivity of one estimate, and the draft is right to report their spread as a standard deviation rather than as an interval.

The interval reported is a recipe-cluster interval over the 25 recipes for the ratio of pooled sums, transformed by the square root. It covers the population value of Lambda under resampling of recipes with the item halves held fixed, so it answers a target 2 question conditional on the chosen split. The snap_compute recipe percentile bootstrap (OBSERVED in core.py) is a different procedure from the wild bootstrap-t (OBSERVED in inference.py), and the two will be reported side by side rather than treated as interchangeable.

## Weighting decisions frozen for R2

The benchmark average keeps equal weights of one tenth per benchmark. Within MMLU, subjects keep equal weights, which reproduces the macro-average the original half_scores computes (OBSERVED in phenotypes.py). Within BoolQ, the grouped split assigns whole passages to halves and then averages questions, so the target stays question weighted rather than passage weighted. Half means then have unequal denominators, and the plan's warning applies: the equal-half derivation is not automatic, so C03 reports the grouped estimate as a sensitivity estimate and the C05-style simulation with heterogeneous passage sizes is what supports or rejects it.

## Comparisons frozen for R2 before any grouped result is opened

On the same 37,682-item universe: the exact original split (split_mode original), a new random item split under the snap_compute machinery (split_mode item), the passage-group split for BoolQ with item splits elsewhere (split_mode group), and the battery without BoolQ. For each, the BoolQ diagonal, total diagonal sum, aggregate off-diagonal contribution, sigma_agg, Lambda, and the paired change against the original split. If the passage join drops any BoolQ item, the item-restriction change and the grouping change are reported separately on the matched universe.

## What the interval does and does not cover

It covers recipe resampling of the pooled ratio at fixed halves. It does not cover item resampling, it does not cover split choice, and it does not cover the schedule differences between default and auxiliary runs, which enter the full-set target as part of the run deviation. The auxiliary contrast narrows that last exposure by construction and widens the interval by losing one contrast per configuration.
