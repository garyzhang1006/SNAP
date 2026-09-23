# Round 7 paper audit (paper-audit skill, conversation-level reading)

Scope: regressions introduced by round 6 (`git diff 73277c2 ae6d8c6 -- deliverables/`), checked against main.tex, appendix_a.tex, appendices_bcd.tex at ae6d8c6. Every finding below is [LLM] provenance (read by hand, no audit script run; read only, no compute). Items logged in REBUTTAL_LOG rounds 3 to 6 as REJECTED or length-skipped (R6-06, R6-07, R6-22, R6-24) are not re-raised. Word costs count whitespace-separated tokens, with `\ref{}` and `\ci{}` as one word each.

Two findings are rated likely to lower the score (PA1, PA2), and both are regressions from round 6 fixes (R6-11, R6-04).

---

## PA1 | moderate | LIKELY TO LOWER THE SCORE: yes | text-fixable

Quote, main.tex:203: "while under independence the uniform item share of 0.124 that reproduces 1.244 at simulated margin noise, which lifts this family's median within-bank estimate only to 1.046, gives supported in 0.033 and undecided in 0.957. The simulation never tests the rule against a shared component large enough to explain the inflation"

Problem: The R6-11 fix defines 0.124 as the share "that reproduces 1.244 at simulated margin noise", and the paragraph's first sentence says this simulation draws "item noise from the DataDecide margin fit". A reader therefore takes "simulated margin noise" to mean this simulation's noise. Under that noise the same share lifts the estimate only to 1.046, and the next sentence says the simulation never tests a component "large enough to explain the inflation". Read that way, the passage contradicts itself about the rule-two power simulation, and that simulation is the only evidence for what rule two can detect. The 1.244 figure comes from a different population, the unit-latent population with item noise 0.73 (appendices_bcd.tex:259). appendices_bcd.tex:351 says the share "falls far short of the inflation it would need to explain", and appendices_bcd.tex:261 says it reaches only 1.024 on released noise. The same number now has three noise contexts, and the main text names the wrong one beside the rule.

Fix (net 0 words): replace "the uniform item share of 0.124 that reproduces 1.244 at simulated margin noise, which lifts this family's median within-bank estimate only to 1.046," (23) with "a uniform item share of 0.124, which reproduces 1.244 only in the population of Appendix~\ref{app:calibration} and lifts the median within-bank estimate to 1.046," (23). app:calibration is the paragraph that holds line 259 (label at appendices_bcd.tex:238).

## PA2 | moderate | LIKELY TO LOWER THE SCORE: yes (R1-fail builds only) | text-fixable

Quote, main.tex:29 (R1 fail branch): "which fails a rule fixed before scoring and \pending{bounds inflation in this family / counts against transfer}, and a disjoint item bank"

Problem: The R6-04 fix added a verdict to the fail branch. That verdict is the failure reading, which main.tex:203 calls "an exploratory reading we added after fixing that rule", and main.tex:43 now flags it as post hoc. The abstract puts the verdict in the same clause as "a rule fixed before scoring" and then says "Beyond the pre-specified test and two PolyPythias rules, analyses are exploratory", so it reads as part of the pre-specified rule. R6-04 flagged this same mislabel in the introduction, where it was rated likely to lower the score. In a fail build, a reviewer comparing the abstract with Section 4.3 finds it in the abstract.

Fix (net -1 word): change "On a second family, nine seeds" to "Nine seeds" (-4; the pass branches already open this way, and "PolyPythias" names the family). Change "and \pending{" to "and, read post hoc, \pending{" (+3). Total -1.

## PA3 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:237: "the size-band-clustered margin interval \ci{1.030}{1.426} of Table~\ref{tab:primary}, covering 0.935 and 0.898 there, still excludes one"

Problem: The R6-23 insertion places "covering 0.935 and 0.898" directly after the interval [1.030, 1.426], so it reads as saying the interval contains those two values, which it doesn't. The numbers are coverage rates in the 0.25 and 0.5 latent-variance cells (appendices_bcd.tex:389).

Fix (net -1): replace ", covering 0.935 and 0.898 there," (5) with " (coverage 0.935 and 0.898)" (4).

## PA4 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:157: "averaging 0.624 within formats and 0.007 across them, excluding WinoGrande's undefined correlations (Figure~\ref{fig:covariance} in Appendix~\ref{app:supplementary}), and BoolQ, the only benchmark in its format, carries 68\%"

Problem: The R6-19 insertion creates a garden path. The reader parses "excluding WinoGrande's undefined correlations ... and BoolQ", as though BoolQ were also excluded from the averages, and has to reparse at "carries".

Fix (net -1): replace "), and BoolQ, the only" with "). BoolQ, the only".

## PA5 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:239: "we fitted each configuration on three of its nine seeds and predicted the ratio on the other six. Independence predicts it with mean absolute log error 0.339, against 0.536 for the three-run estimate and 0.512 for SNAP with item noise added to both sides."

Problem: Round 6 replaced "margin ratio" with "the ratio", which has no referent in the moved paragraph. It also drops the scale, although 0.339, 0.536 and 0.512 are margin figures ("On margins across three sizes", appendices_bcd.tex:345). The next sentence then gives both scales, so the first comparison reads as pooled over scales. The main text calls the two methods "the three-run estimate" and "SNAP with item noise added to both sides", while the appendix calls them "the plug-in" and "the decomposition". The reader cannot match the two descriptions, and "item noise added to both sides" is still undefined.

Fix (net 0): replace "predicted the ratio" (3) with "predicted margin inflation" (3). The terminology mismatch is left unfixed, because changing it would cost words.

## PA6 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:121: "A configuration's margin influence has Spearman correlation $-0.036$ with its selected step's share of the default final step (Appendix~\ref{app:schedule})."

Problem: The R6-13 edit compressed "influence on the margin estimate" into "margin influence", which is an undefined noun phrase. The sentence also never says what a near-zero correlation shows, namely that truncation does not drive the estimate. R5-17 restored this sentence for exactly that purpose.

Fix (net -5): replace "margin influence" with "influence on margin inflation" (+2). Cut ", whose runs sit near their final steps," from the preceding sentence of the same paragraph (-7), because main.tex:119 already says "the auxiliary runs sit near their final steps".

## PA7 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:29: "on DataDecide's recipe comparisons correcting for covariance withdraws at most 12 of 173 to 223 declared orderings whose 1B counterpart clears two standard errors"

Problem: The body (main.tex:222) filters on 1B orderings that clear "two corrected standard errors". The abstract drops "corrected", so the filter reads as the independence standard error, which would give a different pair set and different counts.

Fix (net 0): change "clears two standard errors" to "clears two corrected standard errors" (+1), and change "on DataDecide's recipe comparisons" to "on recipe comparisons" (-1), since the abstract names DataDecide two sentences earlier.

## PA8 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, appendices_bcd.tex:261: "A uniform component shared by every benchmark is therefore excluded on margins as the whole explanation only when it acts alone, at 1.113 under noise-proportional scaling, and the margin value also falls below the 1.153 reference for uniformly spread covariance"

Problem: This sentence has three problems. (a) "acts alone" survives here after R6-01 removed it from the main text as misreadable, and next to "as the whole explanation" it reads as a tautology. Its real premise is zero cross-format seed covariance, as this paragraph's own earlier sentence states. (b) "the margin value" has no referent in this paragraph, which lists 1.010, 1.113 and 0.933. The value meant is the observed 0.921 (appendices_bcd.tex:128). (c) The 1.153 clause is a non sequitur inside a sentence about excluding a shared component.

Fix (net 0): replace "only when it acts alone" (5) with "only under zero cross-format seed covariance" (6). Replace "the margin value" with "the observed 0.921" (0). Delete "instead" from "Adding a 0.124 share to the observed products instead gives" in the same paragraph (-1).

## PA9 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, appendices_bcd.tex:34: "\caption{Cross-half reliability of run deviations for one item half, across all 25 recipes."

Problem: The R6-18 insertion makes the caption say "cross-half" and "for one item half" in the same phrase, and the two read as contradictory. The intended meaning is the reliability of a single half score, estimated from cross-half products.

Fix (net -2): "\caption{Reliability of one item half's run deviations across all 25 recipes." The formula in the next sentence already shows how it is estimated.

## PA10 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable

Quote, main.tex:29: "since a larger one pushes cross-format inflation above its interval \ci{0.801}{1.035}"

Problem: This is left over from R5-01 and R6-01. R6-01 replaced "inflation across scoring formats" with the jargon "cross-format inflation", which the abstract never defines, and "its interval" never gets its point estimate (0.921). The finding stays minor because the premise clause makes the claim readable.

Fix (net 0): replace "cross-format inflation above its interval" (5) with "inflation restricted to cross-format pairs above their interval" (7, +2). Cut "about" from "at most about a third" (-1), which stays accurate since 0.319 is below 1/3. Change "fails its lower-limit rule" to "fails its rule" (-1), since main.tex:41 states the lower-limit rule.

---

Checked and clean: main.tex:45 (ii) labels (1.285 replicate, 1.558 split) match main.tex:93. main.tex:71 and :235 agree with appendices_bcd.tex:261 on 0.319, 1.113, 1.035 and 1.047 inside [0.848, 1.063]. main.tex:123 G5 and "six percent" match appendices_bcd.tex:62 ("six percent at the estimated scale of 0.042"). main.tex:237 "anti-conservative bound of 0.044" and power 0.490 match appendices_bcd.tex:395. The main.tex:251 permutation counts (2,000 item-group, 2,000 batch-slot, 500 run-label bias check) match appendices_bcd.tex:117, :159 and :395. main.tex:43 now flags the failure reading as post hoc, consistent with :203. The main.tex:49 "batch component" matches its uses at :121, :138, :205 and appendices_bcd.tex:62 ("batch offset"). Cross-format pair count: 54 of 90 ordered pairs (appendices_bcd.tex:128) matches 3 cloze, 1 yes/no, 6 MC.
