# Round 6 paper audit (paper-audit skill, reviewer-judgment lane, read only)

Scope: deliverables/main.tex through \label{maintext:end} (line 243) plus the reproducibility statement, with appendix_a.tex and appendices_bcd.tex read wherever a main-text number or term points into them. I read the round 5 diff (git diff fceef7c 73277c2 -- deliverables/) word by word and checked every item against the REBUTTAL_LOG rejection reasons for rounds 3 to 5, so nothing below re-raises a rejected item or a length-skip (R5-28 sigma_agg clause, R5-36 "rank-one plus gain", R5-37 accuracy cut list). Every finding is [LLM] provenance, since no audit script ran (read-only brief). Word costs are net words added to the main text.

Mechanical state, observed: main.log has 0 "undefined" lines. The committed main.pdf is the \Ronecase=0 all-variants build, and in it maintext:end sits on page 10 (main.aux:79), which is expected because that build prints every outcome variant. I didn't recompile the six real outcome combinations, so the round 5 log's page-9 claim for them remains unverified by me.

Seven of the thirteen findings are regressions from round 5 edits (PA1, PA2, PA3, PA4, PA8, PA9, PA11), and three more come from round 5 edits that left an older problem in place (PA5, PA7, PA10).

---

### PA1 | major | LIKELY TO LOWER THE SCORE: yes | text-fixable
Quote: main.tex:29 "Acting alone, a uniform item component shared by all benchmarks could carry at most about a third of the margin excess before inflation across scoring formats leaves \ci{0.801}{1.035}." Same construction at main.tex:235 "A uniform item effect shared across benchmarks and acting alone could carry at most 0.319 of the margin excess before cross-format inflation leaves its interval".

Problem: this is a round 5 regression in the abstract's defence against the main identification attack. "Acting alone" has two readings: the component is the sole cause of the excess, or there is no cross-format run covariance. Under the first reading the sentence contradicts itself, since a sole cause carries all of the excess and can't be capped at a third. Only the second reading is correct (appendices_bcd.tex:128 says "alone, with no seed covariance", and appendices_bcd.tex:261 says "Under the same zero-seed-covariance model"), but neither the abstract nor main.tex:235 says so. The abstract also uses "the margin excess" without defining it, and it says the implied cross-format value "leaves" an interval when the observed interval stays fixed and the implied value passes its upper limit. The abstract also drops the caveat main.tex:71 keeps, "negative run covariance across formats, which 0.921 below one implies, could offset a larger component", so a reader who checks Section 2.2 finds the abstract's "at most" softer in the body. A reviewer pressing on identification will read this as an overclaim.

Fix (about +10 words): abstract, "With no run covariance across scoring formats, a uniform item component shared by all benchmarks could carry at most about a third of the margin excess over one before its implied cross-format inflation passes the observed upper limit of 1.035." At main.tex:235, replace "and acting alone" with "with no cross-format run covariance" (+3) and "before cross-format inflation leaves its interval" with "before its implied cross-format inflation passes the observed upper limit" (+3).

### PA2 | moderate | LIKELY TO LOWER THE SCORE: yes | text-fixable
Quote: main.tex:45 "and the two part where item noise is large, as for accuracy without BoolQ at 1.285 against 1.558 (Section~\ref{sec:estimator})."

Problem: this is a round 5 regression (R5-05 fix). "The two part" reads as a typo because "part" is an uncommon verb here, and it sits in the contribution list, which every reviewer reads. The two numbers carry no labels, so the reader has to guess that 1.285 is the replicate-SD value and 1.558 the split value, which they can only confirm at main.tex:93. The same bare "1.285" also appears at main.tex:216 as the in-sample format-fit value ("gives 1.285 against the observed 1.244"), which brings back the collision R4-10 fixed at line 93.

Fix (about +5 words): "and the two diverge where item noise is large, as for accuracy without BoolQ, where replicates give 1.285 and the split 1.558 (Section~\ref{sec:estimator})." At main.tex:216, "the format fit gives 1.285" (+2).

### PA3 | moderate | LIKELY TO LOWER THE SCORE: yes | text-fixable
Quote: main.tex:123 "and its check G5, that a run-level multiplicative gain explains under half the margin excess, failed under the plan's default simulation settings."

Problem: this is a round 5 regression (R5-15 fix). Now that G5 is defined, a failed G5 tells the reader that a run-level gain explains more than half of the margin excess. That undercuts the headline, and the main text never mentions the result that answers it. appendices_bcd.tex:62 gives that answer: "An empirically matched simulator produces approximately eight percent at the same gain scale and six percent at the estimated scale of 0.042", against 61 percent under the default gain simulator. Without that clause the main text shows a failed plan check against the estimand and doesn't mention the sensitivity result.

Fix (about +17 words): append ", although a simulator matched to each benchmark's variance components puts the gain's share near 0.06 (Appendix~\ref{app:design})".

### PA4 | moderate | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:239 "with the default simulator's item noise, three runs each let the margin interval exclude one in 0.997 of replicates"

Problem: this is a round 5 regression. R5-15 removed "the default simulator" from main.tex:123 because the main text never defines it, and the R5-02 fix then put the same undefined term into the run-planning sentence. The reader can't tell what noise sits behind 0.997 and 0.803, which are the run-count numbers the recommendation paragraph offers for planning.

Fix (about +5 words): "with the planning simulator's generic item noise rather than either battery's measured noise,". I don't state a direction, because the round 5 log says the k08 default sets item_sd to 10 against unit seed SD while its accuracy power runs higher, and the word "generic" doesn't need that settled.

### PA5 | moderate | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:43 "Two rules fixed before scoring read the results, and in simulation the first passes in 0.259 of replicates at a true 1.244 and the second returns undecided in 0.761, so a first-rule pass confirms the effect, a failure bounds it or counts against transfer, and an undecided second rule leaves the shared-item question open."

Problem: round 5 rewrote this sentence, and it now gives power figures for two rules the introduction never describes. The reader doesn't learn that the first rule reads the jackknife lower limit or that the second compares within-bank and cross-bank inflation. "The shared-item question" has no antecedent in the introduction, since line 35 states the conditional-independence assumption but never names a shared item component. The 0.761 also drops its condition (a true 1.244 with no shared item component, main.tex:203). At 55 words the sentence is over-compressed.

Fix (about +16 words): split after "read the results". "The first requires a jackknife lower limit above one, and the second compares within-bank with cross-bank inflation to test whether an item component shared by both halves drives the estimate. In simulation the first passes in 0.259 of replicates at a true 1.244, and with no shared component the second returns undecided in 0.761, so ..."

### PA6 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:203 "while under independence a uniform item share of 0.124, which on this family's noise lifts the median within-bank estimate only to 1.046"

Problem: 0.124 is now orphaned. Round 4 removed every other main-text use, so the main text never says what 0.124 is a share of or why it was chosen. The origin is in appendices_bcd.tex:259: it's the share that reproduces 1.244 in the simulated population with item noise 0.73.

Fix (about +11 words): "a uniform item share of 0.124, the share that reproduces 1.244 in our simulated margin population,".

### PA7 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:203 "is read only through its jackknife upper limit, which bounds inflation in this family, because under independence the middle 90\% of estimates runs from 0.848 to 1.139 and overlaps that range, so the estimate alone can't separate transfer from independence."

Problem: the round 5 fix of R5-13 left a sentence of about 75 words in which "that range" can refer either to "at or above 1.026" or to the first rule's 1.026 to 1.456. The "because" clause explains why the point estimate can't decide, but it doesn't explain why the upper limit bounds inflation, so the causal link R5-13 flagged is still loose.

Fix (about +3 words): end the sentence after "bounds inflation in this family." Then add a new sentence: "Under independence the middle 90\% of estimates runs from 0.848 to 1.139, which overlaps estimates from 1.026 upward, so the point estimate alone can't separate transfer from independence."

### PA8 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:121 "A configuration's influence on the margin estimate has Spearman correlation $-0.036$ with truncation (Appendix~\ref{app:schedule})."

Problem: this is a round 5 addition (R5-17). appendices_bcd.tex:11 correlates influence "with the selected step's share of the default final step", which falls as truncation rises, so the sign printed against "truncation" has the wrong orientation. The main text also never defines "truncation" as a variable. The value is near zero either way, so the conclusion survives, but a careful reader who checks the appendix finds the sign flipped.

Fix (about +7 words): "with the selected step's share of the default final step (Appendix~\ref{app:schedule})."

### PA9 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:251 "500 and 2,000 permutation replicates for the two permutation checks"

Problem: this is a round 5 regression (R5-22 fix). The two permutation checks in the main text are the item-group permutation (main.tex:159, 2,000; appendices_bcd.tex:263) and the batch-slot permutation (main.tex:237, 2,000; appendices_bcd.tex:395). The 500 belongs to the N2 bias check (appendices_bcd.tex:117), which the main text never mentions. The trait-label permutations use 1,000 and 2,000 (appendices_bcd.tex:294). The statement therefore gives the wrong count for one of the two checks it names.

Fix (about +6 words): "2,000 permutation replicates for each main-text permutation check and 500 for the N2 bias check".

### PA10 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:29 "and on DataDecide's recipe comparisons the correction removes at most 12 of the 173 to 223 calls on pairs with a resolved 1B ordering."

Problem: this is a round 5 edit (R5-03). The abstract never defines "the correction" (replacing the independence standard error with the covariance-aware one) or "calls" (declared recipe orderings), so the scope the sentence was meant to restore is hard to read.

Fix (about +5 words): "correcting the standard error for covariance withdraws at most 12 of the 173 to 223 declared recipe orderings on pairs with a resolved 1B ordering."

### PA11 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:45 "(iv) We measure it across the 375 released runs, where every recipe, recipe-pair and benchmark deletion"

Problem: this is a round 5 regression. The cut of "on two score scales" and "margin inflation is 1.244" left "it" pointing at the previous sentence's subject, which is Algorithm 1's measurement recipe, not the covariance.

Fix (about +1 word): "(iv) We measure run covariance across the 375 released runs".

### PA12 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:241 "we fitted each configuration on three of its nine seeds and predicted the margin ratio on the other six. Independence predicts it with mean absolute log error 0.339, against 0.536 for the plug-in and 0.512 for SNAP with item noise added to both sides."

Problem: "the plug-in" is ambiguous, since the main text names only a "rescaled plug-in" (main.tex:220) and a "phenotypic plug-in comparison" (main.tex:228), and appendices_bcd.tex:345 shows this one predicts the full-data inflation estimate. "Item noise added to both sides" is undefined in the main text. The paragraph also restricts itself to "the margin ratio" and then reports accuracy errors (0.367 against 0.523).

Fix (about +2 words): "predicted the ratio on the other six", "0.536 for a plug-in of the full inflation estimate", and "0.512 for SNAP with each benchmark's item noise added back".

### PA13 | minor | LIKELY TO LOWER THE SCORE: no | text-fixable
Quote: main.tex:121 "the auxiliary-run contrast (1.256 in Table~\ref{tab:primary}) removes the default-versus-auxiliary batch component"; also the Table 1 caption and main.tex:205 "no counterpart to the batch component behind our auxiliary contrast".

Problem: "batch component" is never defined in the main text. main.tex:49, as rewritten in round 5, introduces the default and auxiliary schedules but not the term, and the definition sits in appendices_bcd.tex:62 ("A batch offset can enter the same cross-trait products").

Fix (about +8 words): at main.tex:49, end the sentence "which adds run variation beyond the seed, a batch component shared within each run type".

---

Net main-text cost if all are applied: about +104 words, of which PA1 to PA3, the three rated likely to lower the score, take about +40. PA7, PA9 and PA11 together cost about +10 words.
