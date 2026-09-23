# Round 4 fixer brief

Merged findings, statements and quotes are in REBUTTAL_LOG.md under "### Merged findings (round 4)". Each slice fixer edits only its own line range or files, so the five slices can run in parallel. Line numbers refer to deliverables/main.tex at commit 2becd1b.

| Slice | Range | Findings |
|---|---|---|
| A | main.tex 28-45 (abstract and introduction; title at line 14 stays) | R4-01, R4-02, R4-03, R4-04, R4-05, R4-06, R4-11, R4-15, R4-17, R4-32 |
| B | main.tex 46-130 (Sections 2 and 3) | R4-01, R4-03, R4-08, R4-09, R4-10, R4-15, R4-23, R4-24, R4-28, R4-32 |
| C | main.tex 131-198 (Section 4 up to, not including, sec:family at 199) | R4-15, R4-21, R4-30, R4-32, R4-33 |
| D | main.tex 199-241 (sec:family through \label{maintext:end}) and the reproducibility statement at 248-249 | R4-01, R4-07, R4-18, R4-20, R4-22, R4-25, R4-27, R4-31, R4-32, R4-35 |
| APP | appendix_a.tex, appendices_bcd.tex, references.tex, and supplement_extended_body.tex for R4-36 and R4-37 only | R4-01, R4-08, R4-15, R4-16, R4-18, R4-27, R4-29, R4-36, R4-37 |

## Global rules

1. Invent no number. Use only numbers already printed in the paper or stored in a result file, and when you move a number into the text, name its source path in your status note. Round half-up to the paper's precision. Numbers derived in REBUTTAL_LOG.md's CA1 note that no file stores (the total-noise equivalents of the 1.42 and 0.124 shares) stay out of the paper.
2. Add no citation unless its key is already in deliverables/references.tex or work/rebuttal/r4/citation_audit.md marks it VERIFIED. The 17 VERIFIED bibitems in that file may now be cited (R4-15). A \citep key costs little source text, and new bibitems lengthen only the reference list, which sits after maintext:end and doesn't threaten page 9. Count a \citep as zero words in your slice word count, but note that ten author-year citations render at about a line and a half, so slice B should bank a real cut against them; the coordinator's page-9 recompile is the binding check.
3. PolyPythias bank one is being scored now and bank two hasn't been scored. No sentence outside the \outcome branches may say these runs were scored, that the release ships their outputs or hashes, or describe any PolyPythias bank result as existing. DataDecide on bank two stays unscored (GPU).
4. Use no em dashes and no en dashes as punctuation. Write continuous academic prose in the paper's register, with contractions as the surrounding text uses them, no bullet lists in the paper, no "not X but Y" contrasts, and none of the banned vocabulary in CLAUDE.md.
5. The main text must still end on page 9 with a single outcome selected. Every edit in slices A to D is net length-neutral or shorter within its own slice, measured in words over the slice, and the cuts named below pay for the additions. Report the slice's word count before and after in the status file (2becd1b counts: A 970, B 1620, C 1195, D 2006 for lines 199-241, reproducibility statement 298). The coordinator recompiles all six (\Ronecase, \Rtwocase) combinations after the merge and checks `maintext:end` in main.aux. The reproducibility statement sits after maintext:end and doesn't count.
6. The \pending and \outcome scaffolding in the abstract, the introduction and sec:family stays, with every branch, and so do all \label commands. New outcome-dependent text uses the same `\outcome{\Rtwocase}{k}{label}{text}` form. The AI-use and ethics statements (main.tex:242-246) stay untouched.
7. Don't edit outside your slice. Pointers use labels that already exist (app:derivations, app:design, app:schedule, app:supplementary, app:formatfit, app:scale, app:paired, app:composition, app:checkpoint, app:calibration, app:proxy, app:transport, app:heldout, app:decision, app:implementation, app:centring, sec:estimator, sec:data, sec:composition, sec:heldout, sec:family, sec:prediction).
8. R4-01 applies everywhere: no sentence may say or imply that a shared item component is impossible because it would exceed the item noise. The only surviving argument against a uniform shared component is the cross-format one (it would lift cross-format inflation to 1.113, or 1.153 under equal pair weights, and the observed 0.921 \ci{0.801}{1.035} excludes both). The 1.024-at-0.124 figure leaves the main text.
9. Write one status line per finding to work/rebuttal/r4/status_{A,B,C,D,APP}.md as FIXED, SKIPPED (with reason and word count) or NO-CHANGE, quoting the new text.

## Slice A (main.tex 28-45)

Abstract target: the words outside the \outcome scaffolding go from 165 to at most 180, and the rest of slice A pays the difference so the slice stays at or under 970. The reviewers asked for two comparators (R4-04, R4-05) that outweigh the extra length, and the cuts below cover it.

R4-01. Replace "A uniform item component shared across benchmarks would need more than all released item-noise variance to produce 1.244." with "A uniform shared item component producing 1.244 would imply cross-format inflation of 1.113, outside \ci{0.801}{1.035}." (results/snap-r3-r2-02/r2_02_shared_component_crossformat.json: margin explain.induced_cross_format_diagnostic 1.1133, observed cross_format_wild [0.8007, 1.0347]). AR6's request to name the untested format-following component in the abstract is declined for length; main.tex:71 and :235 carry it.

R4-04. Extend the first sentence: "..., against a nominal 0.05, although on DataDecide's own recipe comparisons correcting it removes at most 12 of 173 to 223 calls." (main.tex:222; results in Table~\ref{tab:decision}). Drop "own" if the budget needs it.

R4-05. Abstract: "A pre-specified test on four held-out tasks fails its lower-limit rule at 1.217 \ci{0.872}{1.498}, against 1.240 \ci{1.054}{1.397} for the original ten." Introduction line 41: "The test fails at its full scope of 225 runs, where held-out inflation is 1.217 \ci{0.872}{1.498} against 1.240 \ci{1.054}{1.397} for the original ten on the same runs (Section~\ref{sec:heldout})." (compute extra/heldout/outputs/k04-heldout-full/heldout_results.json; Table~\ref{tab:heldout}). Add no gloss about width; R3-30 removed that framing.

R4-06. Line 43: "so we read both as bounds" becomes "so a pass confirms the effect while a failing or undecided verdict only bounds it". Keep the 0.259 and 0.761 figures.

R4-11. Abstract second sentence: "SNAP (Seed Noise Across Phenotypes) estimates that covariance from cross-half products of run-centred item-half scores on a fixed battery of likelihood-scored multiple-choice benchmarks." Tighten the first sentence to "A run-to-run standard error of a benchmark average that sums per-benchmark variances ignores covariance between benchmarks, ...". Replace "The accuracy interval \ci{0.993}{1.157} includes one, but this design detects a true 1.10 in 0.135 of replicates." with "The accuracy interval \ci{0.993}{1.157} includes one, at 0.135 power against a true 1.10." Add no new numbers beyond R4-04 and R4-05.

R4-32 (A part). Abstract "four unseen tasks" becomes "four held-out tasks". Inside the scaffolding, "Under a rule fixed before scoring" in the R2 supported and R2 undecided variants of the R1-pass branch becomes "Under rules fixed before scoring" (branch wording may change, the branches stay). Line 41: "fails on all 225 runs" is handled by R4-05.

R4-02 and R4-03 (edit together, line 45). Replace "Unlike the battery average's replicate standard deviation, this target transfers to redrawn banks and separates run variance from item noise." with "The battery average's replicate standard deviation answers the fixed-bank question, while the split separates each benchmark's run variance from item noise and defines a target for redrawn banks that we haven't tested on DataDecide (Section~\ref{sec:estimator})." At most 15 words longer than the sentence it replaces.

R4-15 (A part). Line 41: cite the held-out tasks at first mention, "SciQ \citep{welbl2017sciq}, MedMCQA \citep{pal2022medmcqa}, and multiple-choice DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa}", or one \citep list after "CoQA". Line 43: "built with the OLMES harness \citep{gu2025olmes} at a pinned commit".

R4-17. Line 43: "A single model family and a seed label that also changes the training batch leave open whether the inflation belongs to DataDecide's design." becomes "A single model family whose replicates mix default and auxiliary runs on different schedules leaves open whether the inflation belongs to DataDecide's design." (main.tex:119 and :121 describe the schedules and the batch component).

Cuts that pay for A, in this order: delete the last sentence of line 45 ("We also pre-specify a test on unseen tasks and report that it fails at its pre-specified scope.", 17 words; the abstract and line 41 carry it); line 37, delete "These two scales respond differently to changes in confidence, and" and start the clause "Margins carry more seed signal"; line 33, "Covariance adds the off-diagonal terms to that variance, and assuming independence therefore weakens a comparison's error control." becomes "Assuming independence drops the off-diagonal terms and weakens a comparison's error control." If A still runs long, shorten the R4-02 sentence before cutting anything else.

## Slice B (main.tex 46-130)

R4-01, R4-09 and R4-23 (edit line 71 together). Replace "A deviation tied to the items both halves share is a nuisance up to which we identify the estimate." with "We identify the estimate only up to a deviation tied to items that both halves share." Replace the two sentences from "On the released item noise, a uniform component shared across benchmarks lifts margin inflation to 1.024" through "tests it in PolyPythias." with: "A uniform component shared across benchmarks and large enough to carry the observed excess of 0.244 would raise inflation from cross-format covariances alone to 1.113, which the observed 0.921 \ci{0.801}{1.035} excludes (Appendix~\ref{app:calibration}), while a component that follows scoring format is untested in DataDecide, and Section~\ref{sec:family}'s cross-bank rule tests it in PolyPythias." (results/snap-r3-r2-02: explain.induced_cross_format_diagnostic 1.1133, cross_format_wild [0.8007, 1.0347]). Then close the paragraph with R4-09: "The fixed-bank inflation of 1.237 in Section~\ref{sec:estimator} uses no halves and needs neither assumption, so only the item-general reading and the per-benchmark run variances rest on them." Drop 1.024, 0.124 and 1.42 from line 71 entirely.

R4-03 (B part). Line 63: "This target transfers to a redrawn or extended item bank, while a run's item-specific deviations on the released bank fall into $\varepsilon$, so reproducibility on that fixed bank is a separate question." becomes "This target is defined for a redrawn or extended item bank, while a run's item-specific deviations on the released bank fall into $\varepsilon$, so reproducibility on that fixed bank is a separate question."

R4-10. Line 63 last sentence becomes "Item noise is 0.037 of the full-bank margin diagonal and 0.186 of the accuracy one, so the two targets nearly coincide on the full battery, while without BoolQ it reaches 0.578 of the accuracy diagonal and fixed-bank accuracy inflation of 1.285 falls well below the split's 1.558." (results/snap-r3-r2-26/r2_26_analytic_vs_split.json: share_of_diag_removed 0.0366, 0.1860, 0.5777; no_boolq accuracy full_bank_uncorrected 1.2852, split_half 1.5578.)

R4-23 (rest). Define the two words once, in Section 2.1 after the first sentence of line 49: "We call the set of benchmarks the battery and the set of items the bank." Then check lines 63 and 71 use them strictly ("fixed-bank run variance" at 63 stays; "fixed-battery run covariance" at 71 becomes "run covariance of the fixed battery").

R4-24. Line 113: "Cross-half error correlation of 0.1" becomes "Within-benchmark cross-half error correlation of 0.1".

R4-08. Line 123, after the first sentence, add: "The plan also predicted margin inflation above 1.349 and accuracy inflation above 1.40, which none of its $\binom{25}{17}=1{,}081{,}575$ possible estimation sets reaches, and its gain check G5 failed under the default simulator (Appendix~\ref{app:design})." (appendices_bcd.tex:68, :377 from results/snap-r2-r1-49, :64 and :375.)

R4-15 (B part). Line 117: one \citep list at the end of the benchmark sentence, \citep{clark2018arc,clark2019boolq,talmor2019commonsenseqa,zellers2019hellaswag,hendrycks2021mmlu,mihaylov2018openbookqa,bisk2020piqa,sap2019socialiqa,sakaguchi2020winogrande} (clark2018arc covers both ARC sets). Line 129 "with OLMES at a pinned commit" needs no second OLMES citation.

R4-32 (B part). Line 129: "Both reading rules in Section~\ref{sec:family}" becomes "Both rules of Section~\ref{sec:family}".

R4-28, lowest priority in B. Line 113, after the coverage sentence: "A leverage-corrected wild interval, chosen after seeing the first calibration cells, covers closer to 0.95 and gives \ci{1.130}{1.349} on margins, which changes no conclusion (Appendix~\ref{app:calibration})." (appendices_bcd.tex:253.) SKIP with the word count if B can't pay.

Cuts that pay for B: the line 71 rewrite saves about 40 words. Then delete line 121 "A configuration's influence on the estimate shows no detectable rank correlation with its truncation (Appendix~\ref{app:schedule})." and line 111's last sentence "We also report a configuration percentile bootstrap that resamples both sums but ignores recipe dependence." (line 113 still names that bootstrap and its 0.872). Bank one more cut of about 30 words for the rendered benchmark citations, for example line 119 "DataDecide stops the auxiliary replicates below 1B at 25 percent of the 1B compute budget." if the 750M sentence that follows still reads without it.

## Slice C (main.tex 131-198)

R4-21. Line 197: "so which scale carries more seed signal depends on the battery" becomes "so which scale's interval excludes one depends on the battery".

R4-30. Line 161: "and all 300 recipe-pair deletions keep the interval above one, between 1.177 and 1.263" becomes "and all 300 recipe-pair deletions keep the interval above one, with estimates from 1.177 to 1.263 and no lower limit below 1.037" (research/outputs/snap-r6-leave-one-out/r6_leave_one_out.json, leave_two_recipes_full_margin lambda_min 1.1773, lambda_max 1.2629, closest_endpoint_to_one 0.0369).

R4-32 (C part). Line 171: "\subsection{A pre-specified test on unseen tasks}" becomes "\subsection{A pre-specified test on held-out tasks}". The label sec:heldout stays.

R4-33. Line 175: delete the opening sentence "Because the ten benchmarks above shaped our estimator, we pre-specified this test on tasks outside them before any of their production scores existed." and write the next one as "The protocol named SciQ, MedMCQA, and two AGIEval \citep{zhong2024agieval} reasoning tasks, with a pre-specified rule replacing any task ...". That also carries R4-15's C part.

## Slice D (main.tex 199-241, reproducibility statement 248-249)

R4-07. Line 203, last sentence becomes: "In an exploratory reading we added after fixing that rule, a failing estimate is read only through its jackknife upper limit, which bounds inflation in this family, since under independence the middle 90\% of estimates runs from 0.848 to 1.139 and an estimate in that range can't separate the two explanations, while one below 1.026 counts against transfer." (results/snap-r2-r1-18/r1_18_rule_two.json, independence_share0 within_lambda_5_95 [0.8479, 1.1390]; the point estimates don't depend on the jackknife recentring, so this file and r1_18b agree on them.) The R1-fail branch's "\pending{bounds the effect in this family / counts against transfer}" stays.

R4-22. Line 203, the long rule-two sentence: end it after "gives supported in 0.033 and undecided in 0.957." and add "The simulation therefore never tests the rule against a shared component large enough to explain the inflation, and a verdict of not supported can't rule such a component out."

R4-01 (D part). Line 235: replace "On the released item noise a uniform item effect shared across benchmarks can't produce the margin value (Section~\ref{sec:estimator}), while on accuracy a share of 0.053 of item-noise variance would reproduce 1.078 and the accuracy cross-format interval \ci{0.848}{1.063} doesn't exclude the 1.047 it implies," with "A uniform item effect shared across benchmarks that produced the margin value would lift cross-format inflation outside its interval (Section~\ref{sec:estimator}), while on accuracy such an effect could reproduce 1.078 with a cross-format value of 1.047 that the interval \ci{0.848}{1.063} doesn't exclude," and keep the rest of the sentence and the three \outcome{\Rtwocase} sentences. (results/snap-r3-r2-02: accuracy explain induced 1.0469, cross_format_wild [0.8484, 1.0634].)

R4-32 (D part). Line 235: "Apart from the pre-specified test, which failed at its pre-specified scope," becomes "Apart from the pre-specified test, which failed at its protocol scope,".

R4-18. Line 220: "We find covariance gains on margins and no separation on accuracy." becomes "With held-out marginal variances supplied, covariance models predict better on margins, and without them no model separates from independence on either scale." The last sentence becomes "On accuracy every such interval includes zero, and an operational comparison refitting without held-out marginals separates no model from independence on either scale." (research/outputs/snap-r8-prediction/SNAP/C07_margin/result.json and C07_accuracy/result.json, paired_difference_intervals_given_valid all include zero.)

R4-35. Line 222: "the two kinds of pair have paired-difference deviations within a factor of 0.928 to 1.025" becomes "the ratio of seed-matched to seed-unmatched paired-difference standard deviations runs from 0.928 to 1.025" (results/snap-r2-r1-20/r1_20_seed_mismatch.json).

R4-31. Line 228: "and what we add is the estimand, run covariance across benchmarks at a fixed configuration, and its measurement on released pretraining runs, which \citet{miller2024} and \citet{heineman2025} don't estimate" becomes "and what we add is the estimand, run covariance across benchmarks at a fixed configuration, which neither \citet{miller2024} nor \citet{heineman2025} estimates, and its measurement on released pretraining runs".

R4-25. Line 237: "take simulated margin coverage over 10,000 replicates to 0.823 at a quarter of latent variance and 0.581 at a half" becomes "take simulated margin coverage over 12,000 pooled replicates to 0.821 at a quarter of latent variance and 0.580 at a half" (appendices_bcd.tex:389; research/outputs/snap-r6-size-shared-b/r6_size_shared_b.json 10,000 reps at 0.8227 and 0.5805 pooled with snap-r6-size-shared/r6_size_shared.json 2,000 reps at 0.8095 and 0.5785 give 0.8205 and 0.5802).

R4-27 (D part). Line 239: "equicorrelated seed covariance at the observed mean correlation" becomes "equicorrelated seed covariance at the observed $\bar r_E$ of 0.061" (compute extra/heldout/outputs/k08-seed-count/seed_count_power.json, margin observed_rbar_e 0.0608).

R4-20, lowest priority in D. In the Discussion (after the first paragraph at line 233, or at the end of line 235's paragraph before the \outcome sentences), add: "Competence proxies built from the benchmark scores remove shared covariance by construction, so a test of mediation needs held-out loss on the same checkpoints, which are public but need GPU time (Appendix~\ref{app:proxy})." (appendices_bcd.tex:312, :314, :316.) SKIP with the word count if D can't pay.

Cuts that pay for D: line 239 "whose middle 90\% runs from 0.70 to 1.85," and "The ratio itself belongs to this battery." (line 157 says the factor belongs to this battery); the R4-01 and R4-22 rewrites should each come out shorter than the text they replace.

## Slice APP

R4-01 (APP part). appendices_bcd.tex:261: in the injection sentence, state that each benchmark's component is scaled to its measured per-half item noise, the within-half variance less the cross-half covariance (seednoise.reliability.variance_components), which by construction excludes any component identical in both halves. Replace "A share carrying the whole observed excess would have to be 1.422, more than the item-noise variance itself, and it would push the cross-format diagnostic to 1.113" with "A share carrying the whole observed excess would be 1.422 times that measured noise, a value the definition leaves unconstrained, but it would push the cross-format diagnostic to 1.113". Label the 0.124 and 0.053 shares in the same paragraph as shares of the measured per-half item noise. Replace "A uniform component shared by every benchmark is therefore bounded on the released margin noise" with "A uniform component shared by every benchmark is therefore excluded on margins by the cross-format diagnostic, at 1.113 under noise-proportional scaling and at the 1.153 of equal pair weights (Appendix~\ref{app:supplementary})". Grep appendix_a.tex and appendices_bcd.tex for any other "more than the item" or "unattainable" wording and apply rule 8. appendices_bcd.tex:128 already states the cross-format comparison correctly and stays.

R4-08 (APP part). appendices_bcd.tex:294 "the proposed threshold of 1.349" becomes "the planning document's margin threshold of 1.349 (Appendix~\ref{app:design})", and appendices_bcd.tex:253 "the planned threshold" becomes "the planning document's threshold of 1.349".

R4-15 (APP part). Paste the 17 VERIFIED bibitems from work/rebuttal/r4/citation_audit.md verbatim into references.tex in alphabetical order by first author (keys clark2018arc, clark2019boolq, talmor2019commonsenseqa, zellers2019hellaswag, hendrycks2021mmlu, mihaylov2018openbookqa, bisk2020piqa, sap2019socialiqa, sakaguchi2020winogrande, welbl2017sciq, pal2022medmcqa, dua2019drop, reddy2019coqa, zhong2024agieval, liu2020logiqa, wang2022lsat, gu2025olmes). Leave the \begin{thebibliography}{60} argument alone. In appendices_bcd.tex (the held-out paragraph near line 399), cite \citep{liu2020logiqa} after "LogiQA-en" and \citep{wang2022lsat} after "LSAT-LR" where those names appear.

R4-16. appendices_bcd.tex:310: "For this revision we fitted four proxy weightings out of fold" becomes "We also fitted four proxy weightings out of fold". :316: delete ", and the obstacle we reported earlier was our own naming rather than access control" (the paragraph already explains the naming). :343: "The repeat corrects the five-size excess ratio, which the earlier supplement gave as 1.07395, and the inversion sets are new, since the earlier supplement reported none." becomes "The repeat gives the five-size excess ratio of 1.07393 stated above and adds the inversion sets." (appendices_bcd.tex:342 prints 1.07393.) :351: "Our earlier power script dropped a seed's term without recentring the others, which understates the jackknife standard error, and on the same draws it gave the pass rate of 0.356 that an earlier version reported." becomes "A jackknife that drops a seed's term without recentring the others understates the standard error and on the same draws passes in 0.356." (results/snap-r2-r1-18b/r1_18b_jackknife_recentring.json, pass_rate_r1_power_jackknife 0.356.) Keep "That script also assigns ..." but write "The uncentred script also assigns ...".

R4-18 (APP part). appendices_bcd.tex:183: "differ from independence by amounts whose 2,000-draw recipe-resampling intervals all include zero" becomes "differ from independence on both scales by amounts whose 2,000-draw recipe-resampling intervals all include zero" (snap-r8-prediction C07_margin and C07_accuracy).

R4-27 (APP part). appendices_bcd.tex:456: "at the observed mean seed correlation, 0.061 on margins and 0.018 on accuracy" becomes "at the observed effective coefficient $\bar r_E$, 0.061 on margins and 0.018 on accuracy", and "These shares describe a battery with the same average correlation" becomes "These shares describe a battery with the same $\bar r_E$".

R4-29. appendices_bcd.tex:142: read the sign score's definition (app:scale and the supplement's tab:scale). If it is sign(m) with sign(0) = 0, replace "for reasons we haven't traced" with "a gap that only items with a margin of exactly zero can produce, since elsewhere the sign score is an affine map of correctness and the tenfold-rescaling check shows the estimate is scale-invariant". If the definition differs, delete "for reasons we haven't traced" and keep the numbers. Record which in the status file, since the explanation is an inference, not a measurement.

R4-36. supplement_extended_body.tex: every "registered" becomes "pre-specified" and "Registered" becomes "Pre-specified" (lines 694, 707 and any other grep hit), with articles fixed. The label app:heldout stays.

R4-37. supplement_extended_body.tex:135: "The authors resample runs within tasks, with an additional task-resampling variant in their Appendix A.5" becomes "Both resample runs within tasks", which matches main.tex:226 and drops the unverified appendix pointer.

## Not for fixers

NEEDS-EXPERIMENT, all GPU: R4-13 (score the 750M default runs at their released final checkpoints), R4-14 (score the 375 DataDecide runs on bank two), R4-19 (a population above 1B or generative tasks), R4-26 (a larger held-out battery, exploratory by construction). REJECTED: R4-12, R4-34, R4-38 to R4-44, reasons in REBUTTAL_LOG.md.

Out-of-loop action for the author, carried from round 3 (KA7): a third-party timestamp of the rule commit made before PolyPythias scoring ends is the only way the paper can cite independent corroboration for the two rules (R4-39). It reaches an outside service, so the loop doesn't do it.
