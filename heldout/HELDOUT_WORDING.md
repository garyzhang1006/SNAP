# Held-out test wording, fixed before any 750M held-out score exists

Written 2026-09-18, before s04 to s06 run. Use this only if 750M finishes before the 2026-09-25 deadline and `snap-new-k04-heldout-530m750m` runs. If it doesn't finish, the paper keeps its current 530M text unchanged.

The comparison numbers below come from `outputs/k06-power-530m750m`, which ran on the original ten benchmarks before any 750M held-out score existed, so they're fixed now:

- Original ten benchmarks at 530M and 750M: margin 1.316 [0.880, 1.637], accuracy 1.078 [0.810, 1.287]. The full original battery doesn't pass the registered rule at this scope either.
- Four-benchmark subsets of the original ten at this scope: median margin 1.213, 5th to 95th percentiles 0.983 to 1.535, and 0.55 of 60 subsets exclude one.

Placeholders: {L} {LO} {HI} are held-out margin Lambda and its interval from k04, {PCT} is its percentile among the 60 four-benchmark subsets, and {AL} {ALO} {AHI} are held-out accuracy.

## If the lower limit is above one (PASS)

Abstract sentence: "On the 530M and 750M runs that finished before submission, held-out margin inflation is {L} with interval \ci{{LO}}{{HI}}, so the registered rule passes."

Section paragraph: "Only the 530M and 750M runs finished scoring before submission, so we report the test as modified to those sizes, with 1B missing. Held-out margin inflation is {L} with interval \ci{{LO}}{{HI}}, and the test passes. The rule is demanding at this scope, since the original ten benchmarks give 1.316 with an interval of \ci{0.880}{1.637} that includes one, and only 0.55 of their four-benchmark subsets exclude one. We fixed those two comparisons before any 750M held-out score existed."

## If the lower limit is at or below one (FAIL)

Abstract sentence: "On the 530M and 750M runs that finished before submission, held-out margin inflation is {L} with interval \ci{{LO}}{{HI}}, so the registered rule fails."

Section paragraph: "Only the 530M and 750M runs finished scoring before submission, so we report the test as modified to those sizes, with 1B missing. Held-out margin inflation is {L} with interval \ci{{LO}}{{HI}}, and the test fails. At this scope the original ten benchmarks would also fail the rule, at 1.316 with interval \ci{0.880}{1.637}, and 0.45 of their four-benchmark subsets fail it, with the held-out estimate at their {PCT} percentile. The test therefore couldn't separate transfer of the original covariance from its absence. We fixed those comparisons before any 750M held-out score existed."

## Rules for either outcome

- Report held-out accuracy {AL} \ci{{ALO}}{{AHI}}, the auxiliary contrast, and leave-one-task-out next to the margin result, labelled exploratory.
- Don't call a pass a replication of 1.244, because the battery differs (2026-09-17 amendment).
- Don't call a fail evidence of independence, because the original battery fails the same rule at this scope.
- Keep the 530M-only numbers in Appendix `app:heldout` as the earlier interim result.
