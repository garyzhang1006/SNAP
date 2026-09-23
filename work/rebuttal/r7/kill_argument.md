# Kill argument, round 7

Date 2026-09-23. Paper at ae6d8c6 (deliverables/main.tex, appendix_a.tex, appendices_bcd.tex, references.tex). Both cross-model threads ran as fresh `codex exec -m gpt-5.5 -s read-only` calls with stdin closed and no shared context, using the round 6 prompts unchanged apart from the memo. The first attack call (session 01a0cdd2) hung at task_started for 21 minutes with no model events, so I killed it and reran it (session 01a0cde6), which finished in about three minutes. Neither thread saw REBUTTAL_LOG.md or work/. Prompts and raw output are in work/rebuttal/r7/ka_traces/. I checked every codex point against the round 3 to 6 rejection reasons and R6-S, and I read the round 6 diff (73277c2..ae6d8c6, deliverables/) line by line for regressions. JSON and HTML sidecars were skipped, as in earlier rounds.

## Attack memo (verbatim, codex thread 1)

> Reject. The central empirical claim is an in-sample result on a fixed battery, while the only fresh-task test designed to check that dependence fails. The abstract foregrounds 1.244 \ci{1.143}{1.338} on 375 DataDecide runs and recommends covariance reporting (deliverables/main.tex:29), but the paper admits the estimator was built on the original ten benchmarks (deliverables/main.tex:41), every primary-analysis choice saw all 125 configurations because no planned holdout split survived (deliverables/main.tex:123), and the finite-battery result does not estimate a broader benchmark sequence (deliverables/appendix_a.tex:80). The pre-specified held-out check required the lower 95% limit to exceed one and failed at 1.217 \ci{0.872}{1.498} over 225 runs, with all interim scopes also failing (deliverables/main.tex:173, deliverables/main.tex:175; deliverables/appendices_bcd.tex:401). Item count does not explain that failure (deliverables/appendices_bcd.tex:405). The second-family evidence cannot carry the submitted claim: at true 1.244 its first rule passes only 0.259, and the shared-item rule is undecided in 0.761 (deliverables/main.tex:203; deliverables/appendices_bcd.tex:351). The practical payoff is also minimal: correction changes at most 12 of 173-223 recipe calls and every wrong-call interval reaches zero (deliverables/main.tex:222). The paper therefore asks acceptance for a tuned DataDecide measurement whose own pre-specified out-of-sample obligation failed.

## Adjudication (codex thread 2) and my ruling

Codex counts were 0 answered, 2 partial and 3 unresolved, and it judged that the paper would not survive an AC read. All five points repeat logged structural items, so none of them is a new finding. Its "Other defects" list also repeats settled items: the \outcome scaffolding is intentional, the present tense at main.tex:127 was rejected as R5-48, and the density of contribution (ii) was logged as R5-18 and R6-02.

| Codex point | Codex verdict | Log status | Ruling |
|---|---|---|---|
| P1 headline is a fixed-battery result | partial | R3-45, R5-44, R4-12, R5-10 rejected; abstract main.tex:29 scopes to "a fixed battery" and main.tex:157 says "The factor belongs to this battery" | settled, not re-raised |
| P2 planned holdout never drawn | unresolved | R4-08 fixed the disclosure at main.tex:123; the missing holdout itself can't be fixed after the fact | structural (R6-S), not re-raised |
| P3 pre-specified held-out test failed | unresolved | R5-08 rejected; R4-05 put the same-scope comparator 1.240 into the abstract and introduction | settled, not re-raised |
| P4 PolyPythias rules underpowered | unresolved | R1-19, R2-05, R3-06, R5-09 (CPU experiment open); main.tex:43 prints the power | structural (R6-S), not re-raised |
| P5 decision payoff small | partial | R5-07 text part rejected (main.tex:33 scopes it); CPU experiment open | structural (R6-S), not re-raised |

## New findings (my regression hunt on the round 6 diff)

### KA1, moderate. Round 6 relabel makes the recommended estimator appear to lose to independence
Quote, main.tex:239: "we fitted each configuration on three of its nine seeds and predicted the ratio on the other six. Independence predicts it with mean absolute log error 0.339, against 0.536 for the three-run estimate and 0.512 for SNAP with item noise added to both sides."

The R6-09 fix renamed "the plug-in" to "the three-run estimate" and dropped "margin". The code (compute extra/research_kernels/snap-r12-predict-pooled/snap-r12-predict-pooled.py, `predictions`, key `plug_in`) computes that prediction as SNAP's own cross-half ratio from `sigma_e` on the three chosen seeds, and appendices_bcd.tex:345 calls it "the inflation estimate". Set against "SNAP with item noise", the phrase "the three-run estimate" reads as a non-SNAP quantity, which a reader will take to be the three-run replicate standard deviation, and that is exactly what the next paragraph (main.tex:241) recommends reporting. As written, the paper appears to show its own recommendation predicting worse than assuming independence (0.536 against 0.339), and the reordering places that result directly before the recommendation. Dropping "margin" also leaves 0.339, 0.536 and 0.512 without a scale, although the next sentence splits its numbers by scale; appendices_bcd.tex:345 confirms they are margin values.
LIKELY TO LOWER THE SCORE: yes. A reviewer who reads it this way will say the one recommendation fails the paper's only out-of-sample prediction check.
Fix type: text.
Length-neutral fix: replace "predicted the ratio on the other six" with "predicted the margin ratio on the other six" (+1 word), and replace "against 0.536 for the three-run estimate and 0.512 for SNAP with item noise added" with "against 0.536 for SNAP's three-run estimate and 0.512 with item noise added" (-2 words). Net change is -1 word.

### KA2, minor. The abstract's confound bound rests on a premise that the paper's own point estimate contradicts, and it carries no offset caveat
Quote, main.tex:29: "Without cross-format run covariance, a uniform item component shared by all benchmarks can carry at most about a third of the margin excess, since a larger one pushes cross-format inflation above its interval \ci{0.801}{1.035}."

Main.tex:71 says 0.921 implies negative cross-format run covariance, which "could offset a larger component". The abstract states only the bound under the zero-covariance premise, which the point estimate rejects, so a statistically careful reader who reaches line 71 finds that the abstract's only bound on the shared-item confound rests on a premise the data don't support. This is a residual of R6-01, whose fix added the premise but not the offset caveat. It is not a new regression.
LIKELY TO LOWER THE SCORE: no. The premise is stated explicitly, and main.tex:71 and :235 carry the caveat.
Fix type: text.
Length-neutral fix: replace "can carry at most about a third of the margin excess, since a larger one pushes" with "can carry about a third of the margin excess unless negative covariance offsets it, since more pushes" (+3 words), and offset that by replacing "on DataDecide's recipe comparisons correcting for covariance withdraws" with "on DataDecide's recipe comparisons the correction withdraws" (-2) and "declared orderings whose 1B counterpart" with "calls whose 1B ordering" (-1, which also answers KA3).

### KA3, minor. Abstract drops "corrected" from the 1B resolution rule
Quote, main.tex:29: "declared orderings whose 1B counterpart clears two standard errors". Main.tex:222 and appendices_bcd.tex:430 both say "two corrected standard errors", which is a different reference set from one based on independence standard errors.
LIKELY TO LOWER THE SCORE: no.
Fix type: text.
Length-neutral fix: replace "declared orderings whose 1B counterpart clears two standard errors" with "calls whose 1B ordering clears two corrected standard errors" (-1 word). If KA2 is also applied, the budget above already includes this.

### KA4, minor. "Below an anti-conservative bound" asserts more than the caveat allows
Quote, main.tex:237: "puts that effect below an anti-conservative bound of 0.044 of margin run covariance". The R6-17 edit folded the caveat into a construction that still asserts the effect lies below the bound, while appendices_bcd.tex:395 says the bound "is anti-conservative where it is meant to exclude", meaning the true effect can exceed it.
LIKELY TO LOWER THE SCORE: no.
Fix type: text.
Length-neutral fix: replace "puts that effect below an anti-conservative bound of 0.044 of margin run covariance" with "bounds that effect at 0.044 of margin run covariance, anti-conservatively" (-4 words).

### KA5, minor. The percentile row now prints as an interval
Quote, main.tex:192: "Original, four-benchmark subsets, all sizes (percentiles) & Margin & 1.176 & \ci{0.982}{1.476}\\". The R6-25 fix replaced the en dash with \ci, so the row renders in the Interval column in the same bracket form as the six real intervals, while the caption at main.tex:179 says "not an interval".
LIKELY TO LOWER THE SCORE: no.
Fix type: text.
Length-neutral fix: replace "\ci{0.982}{1.476}" with "0.982 to 1.476" in that cell. This avoids a dash and keeps the table the same height.

### KA6, minor. Round 6 appendix sentence has an unclear antecedent and drifts in terminology
Quote, appendices_bcd.tex:261: "and the margin value also falls below the 1.153 reference for uniformly spread covariance". "The margin value" could mean 1.113, 1.024 or 0.921, but only 0.921 falls below 1.153 in the intended sense (appendices_bcd.tex:128). The same R6 edit also reads "Under zero cross-format seed covariance" while main.tex:71 and :235 say "run covariance".
LIKELY TO LOWER THE SCORE: no.
Fix type: text (appendix, no page limit).
Length-neutral fix: replace "the margin value also falls" with "the observed 0.921 also falls", and replace "zero cross-format seed covariance" with "zero cross-format run covariance".

No other round 6 edit introduced a false number or a contradiction. I checked the Gen2MC and Olmo 3 addition at appendices_bcd.tex:399, the "for one item half" caption, "a benchmark half's replicate variance" at main.tex:37, the G5 sentence at main.tex:123 against appendices_bcd.tex:64 ("six percent at the estimated scale of 0.042"), the size-band coverage figures 0.935 and 0.898 at main.tex:237, the permutation counts in the reproducibility statement, and the batch-component definition at main.tex:49.

## Strongest kill argument

The strongest kill argument remains the structural one that codex reproduced. The 1.244 headline is an in-sample measurement on one battery whose planned holdout was never drawn, the one pre-specified out-of-sample test failed its rule, the PolyPythias rules pass in only 0.259 of simulated replicates at the true value, and the correction moves at most 12 real recipe calls. Every part of it is logged under R6-S, R5-07 and R5-08, and text can't answer it. What would answer it is a PolyPythias rule-one pass, or the DataDecide bank-two run (GPU). The only new exposure this round is KA1, a round 6 regression that makes the paper's single recommendation look beaten by independence. It is text-fixable at -1 word.

Score estimate: unchanged from round 6, at 5 overall, about 6 if rule one passes and 4 if it fails. KA1 left unfixed could cost a borderline reviewer a point on soundness.
