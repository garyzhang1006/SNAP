# Kill argument, round 3

Date 2026-09-23. Inputs were deliverables/main.tex, appendix_a.tex, appendices_bcd.tex, references.tex and main.pdf, read fresh, with REBUTTAL_LOG.md and work/rebuttal/r1, r2 left unread. Both cross-model threads ran through `codex exec --skip-git-repo-check -m gpt-5.5` as separate fresh calls (attack session 01a0ccf6-ecaf-72f2-a52a-bd11aaf512eb, adjudication session 01a0ccf8-1ef5-7973-a902-332bdff4a02b), and neither call failed. The pending placeholders and labelled outcome variants were declared intentional in both prompts.

Verdict under the skill's mapping of the codex adjudication is FAIL (`unresolved_critical`, one still_unresolved point at critical). My own adjudication below, which checks the codex rulings against the source, lands at WARN (`partial_critical_or_repeated_major`), because the text already holds an answer to the unresolved point at main.tex:63 that the adjudicator missed and that the paper never connects to the identification caveat.

## Attack memo (Thread 1, verbatim)

> Reject because paper’s headline estimand is not identified as run-to-run covariance. SNAP requires zero cross-half item-error covariance, while manuscript concedes disjoint item IDs do not establish that condition and reads estimate only up to shared item components (main.tex:65-71). Exact unmeasured component can reproduce headline 1.244 at 0.124 item-noise variance, and DataDecide never receives cross-bank check that could test it (main.tex:237; appendices_bcd.tex:257-259). Evidence then collapses to fixed-battery diagnostic, not general benchmark-covariance measurement: no primary holdout survives because screening/estimation split was never drawn and all primary choices saw all 125 configurations (main.tex:125); registered unseen-task test, added because original ten shaped estimator, fails at 1.217 with interval [0.872,1.498] (main.tex:173-177); accuracy, actual reported benchmark score scale, includes independence (main.tex:136, main.tex:147-152). Composition further shows battery-specific artifact: correlations track scoring format, BoolQ carries 68% margin trace, cross-format covariance alone gives 0.921 with interval [0.801,1.035], and format/content cannot be separated (main.tex:159; appendices_bcd.tex:126-132). Title and abstract claim covariance estimation across language-model benchmarks, but evidence supports only conditional, exploratory margin inflation on one hand-shaped likelihood multiple-choice battery under unverified assumptions. That gap is fatal for ICLR significance.

The memo misreads one thing, since it calls the battery "hand-shaped" when DataDecide chose the ten benchmarks and the paper only says the estimator was shaped on them (main.tex:177). Its numbers all match the source.

## Adjudication (Thread 2, verbatim)

Read-only adjudication from allowed files only. No edits.

### Point P_1: Identification Assumption
Attack claim: SNAP headline value is not identified as pure run-to-run covariance because zero cross-half item-error covariance is assumed, not established, and shared item components can enter numerator.

Verdict: partially_answered

Evidence (or lack of): Current text explicitly states the needed zero covariance condition and admits disjoint item IDs do not establish it, then says the estimate is identified only up to a shared component; `main.tex:65-71`, `appendix_a.tex:41-56`. That answers disclosure, not identification.

Severity if unresolved: critical

If unresolved, recommended fix: Reframe 1.244 as a sensitivity-dependent fixed-battery cross-half covariance estimate, not as identified run covariance.

### Point P_2: Unmeasured Shared Component
Attack claim: A shared item component can reproduce the headline 1.244, and DataDecide lacks the cross-bank measurement needed to test that component in the headline population.

Verdict: still_unresolved

Evidence (or lack of): Text says a 0.124 item-noise share reproduces 1.244 and that the component has not been measured or separated; `main.tex:237`, `appendices_bcd.tex:257-259`. DataDecide second-bank scoring was not done, leaving the headline untested on fresh items; `main.tex:237`.

Severity if unresolved: critical

If unresolved, recommended fix: Add a sentence in abstract and Discussion: “The DataDecide 1.244 estimate remains unidentified with respect to shared cross-half item components because no DataDecide cross-bank check was run.”

### Point P_3: No Primary Holdout And Failed Registered Test
Attack claim: Primary analysis is exploratory because screening/estimation split was never drawn, and the registered unseen-task confirmation test fails.

Verdict: partially_answered

Evidence (or lack of): Manuscript directly concedes no primary holdout survives because all primary choices could see all 125 configurations; `main.tex:125`, `appendices_bcd.tex:29-31`. Held-out margin test fails at 1.217 with interval `[0.872,1.498]`; `main.tex:173-177`, table at `main.tex:188-194`.

Severity if unresolved: critical

If unresolved, recommended fix: State in Results and abstract that the DataDecide primary result is exploratory and that the only registered unseen-task confirmation failed its decision rule.

### Point P_4: Accuracy Scale Does Not Confirm
Attack claim: Accuracy, the benchmark score scale closest to standard reported task performance, includes independence, so the margin headline does not transfer to accuracy.

Verdict: partially_answered

Evidence (or lack of): Paper reports margins as primary and accuracy as a bound, but accuracy raw interval includes one: 1.078 `[0.993,1.157]`; `main.tex:37-39`, `main.tex:136-152`. Discussion repeats that accuracy does not settle independence; `main.tex:234-235`.

Severity if unresolved: major

If unresolved, recommended fix: Change claim language from “benchmark covariance” to “per-byte margin covariance,” and state that accuracy-scale covariance remains unconfirmed.

### Point P_5: Battery And Format Specificity
Attack claim: Observed inflation is battery-specific: correlations track scoring format, BoolQ dominates trace, cross-format covariance alone does not exceed one, and format/content are confounded.

Verdict: partially_answered

Evidence (or lack of): Text openly says factor belongs to this battery, within-format mean correlation is 0.624 versus 0.007 cross-format, BoolQ carries 68 percent margin trace, and removals span 1.096 to 1.786; `main.tex:159-163`. Appendix says cross-format diagnostic is 0.921 `[0.801,1.035]` and format cannot be causally isolated; `appendices_bcd.tex:126-132`.

Severity if unresolved: major

If unresolved, recommended fix: Add a front-page qualifier that the result is conditional on this hand-shaped ten-task likelihood multiple-choice battery and is not evidence for benchmark collections in general.

### Point P_6: Title And Abstract Overclaim
Attack claim: Title and abstract still sell “covariance across language-model benchmarks,” while evidence supports conditional exploratory margin inflation under unverified assumptions.

Verdict: partially_answered

Evidence (or lack of): Title remains broad; `main.tex:13-14`. Abstract has strong caveats, including fixed battery, shared component sensitivity, failed held-out test, accuracy interval including one, and exploratory status; `main.tex:28-30`. Still, “SNAP measures that covariance” reads stronger than the identification caveat allows.

Severity if unresolved: critical

If unresolved, recommended fix: Retitle to “Estimating Fixed-Battery Run Covariance in Likelihood-Scored LM Benchmarks” and make abstract lead with conditional identification.

## Summary
answered_by_current_text: 0  
partially_answered: 5  
still_unresolved: 1  

Memo misread check: I did not find a material numeric misquote. The memo’s “actual reported benchmark score scale” is interpretive: paper intentionally makes margins primary and accuracy a bound, but the accuracy interval citation is correct.

## Net Assessment
Senior AC likely sustains rejection unless framing changes sharply. Current text is unusually candid and answers many attacks by concession, but concessions do not rescue headline significance. Core result remains exploratory, fixed-battery, margin-scale, and unidentified against a shared item component in DataDecide. That can survive as a careful measurement note; it does not survive as a broad ICLR-significance claim about covariance across language-model benchmarks.

## Top Action Items
1. Demote headline: fixed-battery, likelihood-margin, conditional-on-no-shared-component.
2. Put failed held-out test and no surviving primary holdout in abstract/introduction claim framing.
3. State DataDecide cross-bank identification check was not run; no new compute is avoidable only if run-covariance headline is abandoned.

## Independent adjudication of the codex rulings

I checked every file:line the adjudicator cited, and all of them point at the right text. Three rulings don't survive a reading of the current source.

P1 and P2 (identification, unmeasured shared component). The adjudicator treats the shared-item gap as fatal to the headline, but main.tex:63 already reports the direct replicate standard deviation of the full-bank average, 1.237 \ci{1.137}{1.331} on margins, which uses no halves and so needs no cross-half independence. On a fixed bank any component the items share is run variance by definition, so the attack only bears on the item-general reading (transfer to a redrawn bank), and the fixed-battery claim the abstract makes at main.tex:29 is identified by that number. The paper never makes this connection: main.tex:71 and main.tex:237 present the 0.124 share as an open confound without saying it can't touch the fixed-bank figure. I rate P2 partially_answered at major, and it becomes answered once one sentence links the two.

P3 (no holdout, failed registered test). The adjudicator's fix is to put the failure and the exploratory status into the abstract, and main.tex:29 already says "A registered test on four unseen tasks fails its lower-limit rule" and "every analysis is exploratory". The disclosure is complete, so I rate it answered_by_current_text; what remains is weak confirmatory evidence, which text can't repair and which feeds KA2 and KA3 below.

P6 (title overclaim). The abstract's second sentence restricts the claim to "a fixed battery of likelihood-scored multiple-choice benchmarks", so the broad title reads as a method title followed by an immediate scope statement. I keep it partially_answered, intentional and sustainable, at minor rather than critical.

P4 and P5 stand as partially_answered at major, and both are author-chosen positions (margins primary, fixed battery) that the text defends openly and that hold up, although they cap the paper's significance.

The line of attack that survives best after these corrections isn't identification. It is significance: the two confirmatory elements either failed or can't decide by the paper's own power numbers, the real-data decision analysis finds no detectable consequence of the correction, and the recommended practice is the direct replicate estimate, which the paper shows matches SNAP to 0.007. KA2 to KA4 below carry that argument, and none of them is answered in the current text.

Counts under my adjudication: answered_by_current_text 1 (P3), partially_answered 5 (P1, P2, P4, P5 at major, P6 at minor), still_unresolved 0.

## Findings

Line numbers refer to the current deliverables sources.

| ID | Severity | Lowers score | Verbatim quote (file:line) | Objection | Suggested fix |
|---|---|---|---|---|---|
| KA1 | major | yes | main.tex:237 "We didn't score the 375 DataDecide runs on the second bank, which leaves the 1.244 untested on fresh items and the shared-item check unrun in the family that supplies our headline." | This is the codex kill point: a 0.124 shared-item share reproduces 1.244 and the headline population never gets the check. The paper leaves it open even though its own full-bank estimate (main.tex:63, 1.237 \ci{1.137}{1.331}) is immune to it for the fixed bank. | Add one sentence at main.tex:71 and main.tex:237 (and a clause in the abstract) saying that the fixed-bank replicate estimate needs no cross-half assumption and excludes one, so the shared-item caveat limits only transfer to redrawn items. |
| KA2 | major | yes | main.tex:205 "so an undecided verdict is expected under either explanation and not supported doesn't exclude a shared component." | The PolyPythias rules get a full sentence in the abstract and a paragraph in the introduction, yet R1 passes in 0.259 at a true 1.244 and R2 returns undecided in 0.761 and 0.957 of simulated replicates, so by the paper's own design the second family is unlikely to confirm or separate anything. A reviewer reads the pending section as pre-announced inconclusive. | State the two power figures (0.259; 0.013 to 0.033 for a decisive R2 verdict) in the introduction sentence at main.tex:43, and shorten the abstract's PolyPythias variants to the outcome plus that power. |
| KA3 | major | yes | main.tex:224 "which changes the share of wrong calls by at most 0.009, from rates between 0.029 and 0.070, and every recipe-bootstrap interval for that change reaches zero" | The abstract opens on a simulated false-positive rate of 0.113 (main.tex:29), while on real recipe comparisons the correction changes no call detectably and seed-matched paired ratios have median 1.024. The motivating harm isn't shown on real decisions, and the 0.113 is a margin-scale figure (accuracy gives 0.067, appendices_bcd.tex:218). | Scope the 0.113 in the abstract to unpaired comparisons on the margin scale and add the real-decision null, then frame the contribution as calibrated uncertainty for reported averages rather than changed rankings. |
| KA4 | major | yes | main.tex:63 "On the released bank, the replicate standard deviation of the full-bank average gives inflation 1.237 \ci{1.137}{1.331} on margins and 1.067 \ci{0.994}{1.134} on accuracy, against 1.244 and 1.078 from the split." | The recommendation (main.tex:241) is to compute the aggregate replicate standard deviation directly, and the direct estimate agrees with SNAP within 0.007. A reviewer asks what the cross-half machinery contributes beyond a quantity any practitioner with replicates can compute. | Say in the introduction's contribution paragraph what the split buys that the direct estimate can't: the item-general target, the per-benchmark run versus item-noise decomposition behind the reliabilities, and the diagonal without a noise model. Present the direct estimate as the practitioner's tool and SNAP as the measurement of its item-general counterpart. |
| KA5 | minor | no | main.tex:199 "As an exploratory result, the held-out accuracy inflation interval excludes one." | Margins are primary because they "carry more seed signal" (main.tex:37), but on the held-out tasks accuracy excludes one while margins don't. The paper reports this without reconciling it with the scale rationale. | Add one sentence noting that the scale ordering held on the original ten but reversed on the held-out four, so the choice of primary scale is battery-dependent. |
| KA6 | minor | no | main.tex:71 "which constrains a uniform component of that size" | The main text asserts the constraint without the reference value. The appendix has it (appendices_bcd.tex:128, 1.153 expected from uniformly distributed contributions against 0.921 \ci{0.801}{1.035}), and without it the key mitigation reads as unsupported. | Cite the 1.153 reference beside 0.921 at main.tex:71 and main.tex:218. |
| KA7 | major | yes | main.tex:251 "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp" | "Registered" and "fixed before scoring" carry weight in the abstract, introduction and Section 4.3, yet only author-controlled commits back them. | Before PolyPythias scoring ends, deposit the rule commit hash with a third-party timestamp (for example OSF or OpenTimestamps) and cite it. Otherwise use "pre-specified" in place of "registered". |
| KA8 | minor | no | main.tex:93 "while the split needs neither, at the cost of half the items in each score" | Seven lines earlier the split is said to need zero cross-half error covariance and disjoint IDs aren't enough (main.tex:66, 71), so "needs neither" contradicts the paper's own caveat. | Change it to "while the split needs only independence between halves, not a model of within-half item noise". |
| KA9 | minor | no | main.tex:239 "take simulated margin coverage over 10,000 replicates to 0.823 at a quarter of latent variance and 0.581 at a half" | appendices_bcd.tex:387 reports the same cells as "falls to 0.821 and at a half it reaches 0.580". | Use one run's figures in both places, or name the replicate count of each. |
| KA10 | minor | no | appendices_bcd.tex:216 "the Gaussian calculation gives $P_{\rm flip}>0.05$ for a true gap below 0.01196" | 0.01196 equals 1.645 times the square root of 2 times 0.00514, a single-run comparison, but it is applied to observed gaps between three-run recipe means, where the threshold would be 0.00690. The 0.246 and 0.229 reversal figures are also single-run values. | Say the calculation is for single-run comparisons, or recompute the count of 455 pairs at the three-run threshold. |
| KA11 | minor | no | main.tex:14 "\title{Estimating Run-to-Run Covariance\\Across Language Model Benchmarks}" | Codex rated this critical scope overclaim. The abstract restricts scope in its second sentence, so most reviewers will accept it, but it remains the first thing an attack quotes. | Consider a qualifier such as "for a Fixed Battery of Likelihood-Scored Benchmarks", though the author's current choice is sustainable. |
| KA12 | minor | no | main.tex:123 "although the auxiliary contrast, whose runs sit near their final steps, still excludes one" | The sentence sits in the 33-configuration subset discussion, so it reads as if the auxiliary contrast was computed on that subset, whereas the 1.256 \ci{1.090}{1.400} it refers to is full-sample. | Write "the full-sample auxiliary contrast". |
| KA13 | minor | no | main.tex:45 "gives the measurement recipe with calibrated intervals, whose wild recipe-cluster coverage runs from 0.928 to 0.954" | appendices_bcd.tex:249 concludes that "The shortfall belongs to the construction", and a band-shared effect takes coverage to 0.82, so "calibrated" is stronger than the evidence. | Write "near-nominal intervals". |

Severity counts: critical 0, major 5 (KA1, KA2, KA3, KA4, KA7), minor 8. Codex alone would have scored three points critical (P2, P3, P6), and the independent adjudication above explains why each came down.
