# Round 2 fixer brief

Merged findings, statements and quotes are in REBUTTAL_LOG.md under "### Merged findings (round 2)". Each slice fixer edits only its own line range or files, so the five slices can run in parallel. Line numbers refer to deliverables/main.tex at commit e33a01d.

| Slice | Range | Findings |
|---|---|---|
| A | main.tex 28-49 (abstract and introduction; title at line 14 stays) | R2-03, R2-07, R2-10, R2-11, R2-18, R2-31 |
| B | main.tex 50-136 (Sections 2 and 3) | R2-01, R2-12, R2-13, R2-17, R2-27, R2-28, R2-29, R2-30 |
| C | main.tex 137-204 (Section 4 up to sec:family) | R2-19, R2-20, R2-21, R2-32, R2-33, R2-34 |
| D | main.tex 205-247 (sec:family to \label{maintext:end}), plus 248-255 for R2-39 only | R2-04, R2-05, R2-06, R2-08, R2-09, R2-22, R2-23, R2-24, R2-35, R2-36, R2-37, R2-38, R2-39 |
| APP | appendix_a.tex, appendices_bcd.tex, references.tex, and supplement_extended_body.tex for R2-41 | R2-25, R2-40, R2-41, R2-42 |

## Global rules

1. Invent no number. Use only numbers already printed in the paper or stored in a result file, and when you move a number into the main text, name its source path in your status note. Round half-up to the paper's precision.
2. Add no citation unless its key is already in deliverables/references.tex or citation_audit.md verified it. OLMES has no entry, so don't cite it.
3. Use no em dashes and no en dashes as punctuation. Write continuous academic prose in the paper's register, with contractions as the surrounding text uses them, no bullet lists in the paper, no "not X but Y" contrasts, and none of the banned vocabulary in CLAUDE.md.
4. The main text must still end on page 9 with a single outcome selected. Every edit in slices A to D is net length-neutral or shorter within its own slice, and the cuts named below pay for the additions. The coordinator recompiles all six (\Ronecase, \Rtwocase) combinations after the merge and checks `maintext:end` in main.aux.
5. The \pending and \outcome scaffolding in sec:family and the abstract stays, including every branch. New outcome-dependent text uses the same `\outcome{\Rtwocase}{k}{label}{text}` form.
6. Don't edit outside your slice. When a fix needs a pointer to an appendix label, use a label that already exists (app:derivations, app:design, app:schedule, app:supplementary, app:formatfit, app:scale, app:paired, app:composition, app:checkpoint, app:calibration, app:proxy, app:transport, app:heldout, app:decision, app:implementation, app:centring).
7. Write one status line per finding to work/rebuttal/r2/status_{A,B,C,D,APP}.md as FIXED, SKIPPED (with reason) or NO-CHANGE, quoting the new text.

## Slice A (main.tex 28-49)

R2-03. The rule-two outcome word is "not supported", never "rejected". In both abstract branches at line 29 replace "leaves \pending{cross lambda} with the shared-item explanation rejected" by "leaves \pending{cross lambda}, which gives no support to the shared-item explanation". At line 45 change the R2=1 text of the `\outcome` from "rejected" to "not supported".

R2-07. End paragraph 1 (line 33) on the stakes. Keep the 0.113 against 0.05 sentence with a pointer "(Appendix~\ref{app:supplementary})", and follow it with at most one clause naming the uses it bears on, the error bar of one model's battery average and the number of replicate runs to plan. Delete the sentence starting "On DataDecide's recipe comparisons", because Section 4.5 carries those numbers and results/snap-r2-r1-20 shows seed matching doesn't explain them. Net shorter.

R2-10. Rewrite the abstract (line 29) so that its word count falls. Order: the problem with its consequence (0.113 against 0.05 in simulation); SNAP in one sentence, scoped to a fixed battery of likelihood-scored multiple-choice benchmarks; data and headline 1.244 \ci{1.143}{1.338}; BoolQ's 68% share with the removal range 1.096 to 1.786 and one clause saying the aggregate standard deviation, not the factor, compares batteries; the identification caveat after the result ("a shared item component at 0.124 of item-noise variance would reproduce it"); the accuracy interval; the registered test; the unchanged R1/R2 \outcome block (with R2-03's wording); the exploratory sentence and the recommendation. Drop "under a low-powered design" and "whose replicates differ in seed and partly in checkpoint schedule" only if the word count requires it. The title stays.

R2-11. Merge lines 47 and 49 into one paragraph with four flat contributions: the estimand identified up to a shared item component; the recipe with calibrated intervals (0.928 to 0.954); the two-scale measurement (1.244, with the deletion result and the 530M exception); the registered test reported as a failure at its scope. Cut the K_eff clause from "At that value the ten benchmarks" to "0.00516" (line 95 and Section 4.1 already carry it), cut the 0.626 against 0.343 clause (Section 4.2 has it), cut the 0.113 to 0.051 sentence (the Discussion keeps it), and cut "Apart from the registered test and the two PolyPythias rules, every analysis is exploratory." (abstract and Discussion keep it). Net shorter by several lines, which gives slice A its slack.

R2-18. Delete the one-sentence paragraph at line 41. Append to line 39: ", and at accuracy-like item noise this design detects a true ratio of 1.10 in only 0.135 of replicates" (research/outputs/snap-r6-detect-power/r6_detect_power.json). The exploratory accuracy cuts stay in the Discussion at line 239.

R2-31. Line 37: "with 25 data recipes and five of its model sizes, each with three released replicates". Line 45: "built with the OLMES harness at the commit DataDecide used". No citation for OLMES.

## Slice B (main.tex 50-136)

R2-01. Rewrite the last two sentences of line 75 without adding length. Say that centring across replicate runs removes any item effect constant across runs, so only a run-by-item-set deviation shared by both halves can enter the numerator, and a run's deviation on every item of one prompt template is such a term; that deviation recurs on any redrawn bank in the same format and therefore belongs to fixed-battery run covariance, while a component tied to the particular items both halves share would not. Then define the diagnostic in a clause: "the inflation computed from cross-format covariances alone is 0.921 \ci{0.801}{1.035} (results/snap-r2-r1-50/r1_50_crossformat_boot.json), with cross-format pairs averaging 0.007". Keep "constrain a uniform component" and state plainly that a component following scoring format is untested in DataDecide and that the cross-bank rule of Section~\ref{sec:family} tests it in PolyPythias. Don't claim that bank two shares or avoids bank one's few-shot exemplars, since nothing in the repo records it. The 0.124 sensitivity sentence stays.

R2-12. After "so reproducibility on that fixed bank is a separate question" (line 67), add one sentence: on the released bank the replicate standard deviation of the full-bank average gives inflation 1.237 \ci{1.137}{1.331} on margins and 1.067 \ci{0.994}{1.134} on accuracy, against 1.244 and 1.078 from the split (results/snap-r2-r1-08/r1_08_fixed_bank.json, wild recipe-cluster intervals). Replace the pointer with that sentence rather than lengthening the paragraph further.

R2-13. Add at most two lines after Equation~\ref{eq:identity}'s paragraph or at line 97: subtracting per-benchmark item variance over $n$ from the full-data diagonal would use every item but assumes independent items and a model for their noise, while the split needs neither and tolerates the passage and story dependence of Section~\ref{sec:composition}, at the cost of halving the items per half. No efficiency number (R2-26 would supply one).

R2-17. Replace line 129 by one sentence: the plan assigned eight recipes to screening and seventeen to estimation, we never drew that partition, and every choice in the primary analysis could see all 125 configurations, so no holdout survives (Appendix~\ref{app:design}). Delete the enumeration range and the threshold sentence, whose values have no result file (R1-49 still open). This cut pays for R2-12 and R2-13.

R2-27. Line 117: "We report the wild interval, whose coverage across the twelve populations of Table~\ref{tab:coverage} runs from 0.928 to 0.954", and remove the duplicate range from the next sentence.

R2-28. Line 127: "removes the 750M band and one 530M configuration".

R2-29. Line 127, after the 33-configuration sentence, add one clause: the auxiliary contrast compares runs that sit near their own final steps and still gives 1.256 with an interval excluding one (Table~\ref{tab:primary}). Keep it to one clause.

R2-30. Line 133: "A smaller earlier transfer check on 4,755 items is in Appendix~\ref{app:transport}."

## Slice C (main.tex 137-204)

R2-19. Table 1 caption (line 144): delete "and the gain and competence adjustments are in Appendix~\ref{app:proxy}", and change "or size-band clusters where marked" to "or cluster-robust $t(4)$ intervals over the five size bands where marked" (research/outputs/snap-r6-twoway/r6_twoway.json).

R2-20. Delete the Dirichlet sentence at line 167. The appendix copy stays until a CPU rerun exists.

R2-21. Line 165: lead with the effect size, "the permuted estimates sit about 0.001 below the observed margin value and 0.002 below accuracy", and put the tail fractions in parentheses after it or drop them. Net shorter.

R2-32. Table 2 (line 198): print the last row's bracket as "0.982--1.476" without \ci and add to the caption that this row's range gives percentiles over subsets, not an interval. Keep the caption no longer than now by trimming its wording.

R2-33. Line 181: replace "and a power simulation that can't rescue the test" with "and a power simulation of the rule at each scope it could take".

R2-34. Line 163: "(Figure~\ref{fig:covariance} in Appendix~\ref{app:supplementary})".

## Slice D (main.tex 205-247, statements 248-255 for R2-39)

R2-04. Line 207: "It returns not supported when that cross-bank interval sits above one and ...". Keep the rule definitions verbatim otherwise.

R2-05 and R2-06 (edit together). Split the line 207 paragraph after the rule definitions and the bank caveats. Open the second paragraph with both rules' simulated behaviour. R1, using the committed seed-recentring jackknife on the same 4,000 draws, passes in 0.259 of replicates at a true 1.244 and 0.016 at independence, with the middle 90% of estimates between 1.026 and 1.456 (results/snap-r2-r1-18b/r1_18b_jackknife_recentring.json: 0.2585, 0.0155, 1.0258, 1.4563). This replaces 0.356 and 0.026, which came from a jackknife that doesn't recentre. R2, at a true 1.244 with no shared item component, returns not supported in 0.226, supported in 0.013 and undecided in 0.761 of 4,000 replicates, and when a 0.124 share alone produces the within-bank excess it returns supported in only 0.033 and undecided in 0.957 (results/snap-r2-r1-18/r1_18_rule_two.json, scenarios run_cov_1244_share0 and independence_share0124). Say in one clause what that means: an undecided R2 is the expected outcome under either explanation, and not supported doesn't exclude a shared component. Then give the reading added after fixing the rule as its own sentence labelled exploratory. Pay for the added length with R2-08, R2-22 and the cuts listed there.

R2-08. Line 228: replace the last sentence ("Recipes inside a size band share seed labels ... few changed calls") with the R1-20 result: in single-run comparisons the correction changes the wrong-call rate by at most 0.019 when the two runs share a seed label and by at most 0.016 when they don't, every interval reaching zero, and seed-matched and seed-mismatched pairs have paired-difference deviations within a factor of 0.93 to 1.03 of each other, so seed matching doesn't explain the few changed calls (results/snap-r2-r1-20/r1_20_seed_mismatch.json). Line 245: delete "and seed-matched paired comparisons need little correction, with median paired-difference ratio 1.024 (Appendix~\ref{app:paired})". Line 226 keeps the 1.024 median as a measured fact.

R2-09. Line 245: scope the comparison and add the reversal in one sentence of about the same length: against one configuration's six-run ratio on the earlier three-size PolyPythias transfer runs, whose own 5th to 95th percentiles run from 0.70 to 1.85, independence predicts with mean absolute log error 0.339 against 0.536 for the plug-in and 0.512 for the decomposition, while against a target pooled across configurations the decomposition wins, 0.275 against 0.319 on margins and 0.367 against 0.523 on accuracy (Appendix~\ref{app:transport}; appendices_bcd.tex:343 and 345, research/outputs/snap-r12-predict-pooled). Keep "Our ratio therefore measures this battery ...".

R2-22. Line 220: replace "our estimated correlations track scoring format, averaging 0.624 within formats and 0.007 across them" with a back-reference to Section~\ref{sec:composition} that keeps the numbers only where the fit sentence needs them. Line 241: attach the share-of-0.05 result to the 0.124 sentence ("..., reproduce 1.244 and 1.078, while at a share of 0.05 only 0.007 of simulated replicates reach the margin value"), and delete the passage-aware sentence ("The passage-aware split moves both estimates ... sensitive test."), which repeats line 165. Line 226: the first sentence (0.246 against 0.229 and the 455 gaps) may move out, since APP adds it to app:supplementary under R2-40; cut it if D needs the space.

R2-23. Line 241: add `\outcome{\Rtwocase}{2}{R2 supported}{ The cross-bank check in PolyPythias finds such a component in one family, so the within-bank value can overstate run covariance there.}` and `\outcome{\Rtwocase}{3}{R2 undecided}{ The cross-bank check in PolyPythias leaves that item effect undecided in one family.}` beside the existing R2=1 sentence. Only one prints per build.

R2-24. Line 234: "adapts the split-half construction of \citet{spearman1910,brown1910}, the attenuation correction of \citet{spearman1904}, and the variance components of \citet{searle1992} and generalizability theory \citep{brennan2001}", dropping cronbach1951 here if length requires (appendices_bcd.tex:77 cites it). Keep the existing "what we add is the estimand and its measurement" and don't characterise generalizability theory further, since multivariate G-theory does model covariance across measures and the text must not imply otherwise. Length-neutral.

R2-35. Line 243: replace 0.821 and 0.580 with 0.823 and 0.581 at 10,000 replicates (research/outputs/snap-r6-size-shared-b/r6_size_shared_b.json), and add one clause that the size-band-clustered margin interval \ci{1.030}{1.426} of Table~\ref{tab:primary} still excludes one.

R2-36. Line 239: "at accuracy-like item noise, a design that would detect ...". Line 245: "in a population with the released item counts and equicorrelated seed covariance, three runs each let ..." (compute extra/heldout/outputs/k08-seed-count/seed_count_power.json).

R2-37. Line 217: "Bank two holds under a fifth of bank one's items".

R2-38. Line 219: rename the subsection "Concentration by scoring format".

R2-39. Line 255: "come from earlier execution records that we didn't rerun for the final analysis", and delete ", and the loss-proxy rescoring wasn't run". The statements sit after maintext:end and don't count toward page 9.

## Slice APP

R2-25. appendices_bcd.tex:73: "\citet{zhao2026} set a three-seed noise floor on a twelve-task average and combine per-task Welch tests by Stouffer's method, noting positive task correlation without estimating it."

R2-40. Give the supplement-only main-text numbers an appendix home, one sentence each: in app:composition, all 300 recipe-pair deletions leave a margin interval excluding one (research/outputs/snap-r6-leave-one-out/r6_leave_one_out.json, leave_two_recipes); in app:heldout, removing CoQA gives held-out margin inflation 1.090 and removing any other task 1.120 to 1.213 (compute extra/heldout/outputs/k04-heldout-full/heldout_table.csv); in app:supplementary, the sign-reversal probabilities 0.246 against 0.229 and the 455 of 1,500 gaps below the 5% threshold (research/outputs/snap-r0-baseline/results/tab_practitioner.csv; the 455 is already printed at main.tex:226), and the BoolQ-removal aggregate standard deviation 0.00516 (research/outputs/snap-r11-removal/r11_removal.json). Add the R1 power figures to app:transport with the committed-jackknife values of R2-06 (0.2585 at a true 1.244, 0.0155 at independence, 5th to 95th percentile 1.026 to 1.456, results/snap-r2-r1-18b) and the R2 outcome rates of R2-05 (results/snap-r2-r1-18), so the main text has a backing paragraph.

R2-41. supplement_extended_body.tex:127: "\citet{miller2024} treats item-sampling uncertainty with clustered and paired two-model comparisons while holding run variance fixed." At supplement_extended_body.tex l.716 print 0.927 for the 0.9265 value (compute extra/heldout/outputs/k12-rule-power-n073), matching round 1's rounding rule.

R2-42. references.tex: add pages 32970--32979 to fehlauer2025 and volume 37 to ruan2024, both from citation_audit.md.

## Not for fixers

NEEDS-EXPERIMENT: R2-02 (CPU, cross-format diagnostic under a uniform 0.124 share), R2-14 (GPU, DataDecide on bank two), R2-15 (PolyPythias and bank-two outputs, manifest CPU), R2-26 (CPU, analytic diagonal correction against SNAP), R2-43 (CPU, store the 0.044 bound and 0.008 share). REJECTED: R2-16, R2-44 to R2-48, reasons in REBUTTAL_LOG.md.
