# Kill Argument Report: SNAP (main.tex at 652333f)

Date 2026-09-24. Reviewer: Claude Opus 5.5 in the main session, attack and adjudication written in two separate passes. The skill specifies fresh cross-model codex threads, but no codex tool exists in this session and the user's goal rules out agents, so this run isn't cross-model and carries that weakness. The abstract changed within the last two commits, which the skill maps to NOT_APPLICABLE/headline_unstable. I ran it anyway, because the ICLR deadline won't wait for a stable headline, and the computed verdict below ignores that rule.

Verdict: FAIL (reason_code unresolved_critical)

## Attack memo

The paper's central quantity, margin inflation of 1.244 on DataDecide, is an exploratory estimate from one released population, and every test the authors fixed in advance has failed. The held-out battery rule fails at 1.217 [0.872, 1.498] (main.tex:56, 188), the PolyPythias rule fails at 1.302 [0.921, 1.595] with an interval the authors concede can't separate that family from one (222), and accuracy inflation includes one (54). What remains is a within-format covariance in 25 recipe clusters, scored at checkpoints the authors admit are truncated (41.5% of the final step at 750M, 134), and dominated by BoolQ, which carries 68% of the trace and whose removal swings the estimate between 1.096 and 1.786 (172). The estimand is identified only up to an item component shared across halves (86), and the test built to identify it hasn't reported. The payoff is thin by the paper's own account, since the correction changes few recipe calls (237) and the closing recommendation is to report the replicate standard deviation of the battery average (256), which needs neither SNAP nor this paper. A method whose method isn't needed for its own recommendation, and whose confirmatory tests failed, doesn't clear the ICLR bar.

## Adjudication

P1, confirmatory tests failed. still_unresolved, critical. The text reports both failures plainly (abstract, 56, 188, 222), which answers honesty but not the substance. Research-level, and no rewrite fixes it.

P2, one population at truncated checkpoints. partially_answered, major. The auxiliary contrast 1.256, size-band clusters [1.030, 1.426], adjacent-step check and the 33 shared-final-step configurations (136) address it, but the last gives [0.121, 1.530] and can't test the estimate.

P3, BoolQ dominance and battery dependence. partially_answered, major. The paper states the factor belongs to its battery (172, 176) and every single-benchmark removal keeps the margin interval above one (Figure 2), so the claim is scoped, but a reviewer can still read "one benchmark's format" as the whole finding.

P4, identification up to a shared item component. partially_answered, major. The cross-format bound of 0.319 (86) limits a uniform component, and rule two will report on PolyPythias only.

P5, SNAP unnecessary for the recommendation. still_unresolved, major, writing-level. The paper already holds the counterexample (108): without BoolQ, item noise is 0.578 of the accuracy diagonal and the replicate standard deviation gives 1.285 against the split's 1.558, so the fixed-bank shortcut understates item-general inflation exactly when items are noisy. Neither the abstract nor the contributions say so.

Counts: answered 0, partial 3, unresolved 2 (1 critical).

## Net assessment

The paper wouldn't survive an area chair who reads this memo, because P1 hits the headline and can't be answered with text. P5 can be answered, and the fix costs no compute.

## Top action items

1. State in contribution (ii) and the discussion when the split and the replicate standard deviation diverge, using the 1.285 against 1.558 case already in Section 2.
2. Fill rule two when bank two lands and delete the unused branches.
3. Keep the TMLR fallback in view, since P1 is research-level.
