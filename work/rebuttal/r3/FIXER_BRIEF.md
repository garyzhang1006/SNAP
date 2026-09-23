# Round 3 fixer brief

Merged findings, statements and quotes are in REBUTTAL_LOG.md under "### Merged findings (round 3)". Each slice fixer edits only its own line range or files, so the five slices can run in parallel. Line numbers refer to deliverables/main.tex at commit f23e293.

| Slice | Range | Findings |
|---|---|---|
| A | main.tex 28-45 (abstract and introduction; title at line 14 stays) | R3-01, R3-02, R3-04, R3-06, R3-07, R3-08, R3-09, R3-10, R3-11, R3-17, R3-26, R3-27, R3-36 |
| B | main.tex 46-131 (Sections 2 and 3) | R3-01, R3-02, R3-03, R3-04, R3-07, R3-10, R3-18, R3-24, R3-32, R3-33, R3-36 |
| C | main.tex 133-200 (Section 4 up to, not including, sec:family at 201) | R3-07, R3-27, R3-28, R3-29, R3-30, R3-31, R3-44 |
| D | main.tex 201-243 (sec:family through \label{maintext:end}) and the reproducibility statement at 250-251 | R3-01, R3-02, R3-03, R3-04, R3-05, R3-07, R3-14, R3-15, R3-16, R3-17, R3-19, R3-20, R3-22, R3-34, R3-35, R3-40 |
| APP | appendix_a.tex, appendices_bcd.tex, references.tex, and supplement_extended_body.tex for R3-40 and R3-41 only | R3-01, R3-02, R3-05, R3-07, R3-22, R3-24, R3-25, R3-37, R3-38, R3-39, R3-40, R3-41, R3-42, R3-43 |

## Global rules

1. Invent no number. Use only numbers already printed in the paper or stored in a result file, and when you move a number into the text, name its source path in your status note. Round half-up to the paper's precision. The round 3 kernel files are results/snap-r3-r2-02/r2_02_shared_component_crossformat.json, results/snap-r3-r2-26/r2_26_analytic_vs_split.json and results/snap-r3-r2-43/r2_43_band_share.json, summarised in results/snap-r3-SUMMARY.md.
2. Add no citation unless its key is already in deliverables/references.tex or work/rebuttal/r3/citation_audit.md verified it. No benchmark, AGIEval or OLMES entry exists, so cite none of them (R3-21 is deferred).
3. PolyPythias bank one is being scored now and bank two hasn't been scored. No sentence outside the \outcome branches may say these runs were scored, that the release ships their outputs or hashes, or describe any PolyPythias bank result as existing. Write the scoring as design or plan in present or future tense ("we score", "the release will include"), and invent no status detail.
4. Use no em dashes and no en dashes as punctuation. Write continuous academic prose in the paper's register, with contractions as the surrounding text uses them, no bullet lists in the paper, no "not X but Y" contrasts, and none of the banned vocabulary in CLAUDE.md.
5. The main text must still end on page 9 with a single outcome selected. Every edit in slices A to D is net length-neutral or shorter within its own slice, measured in words over the slice, and the cuts named below pay for the additions. Report the slice's word count before and after in the status file. The coordinator recompiles all six (\Ronecase, \Rtwocase) combinations after the merge and checks `maintext:end` in main.aux. The reproducibility statement sits after maintext:end and doesn't count.
6. The \pending and \outcome scaffolding in the abstract, the introduction and sec:family stays, with every branch, and so do all \label commands. New outcome-dependent text uses the same `\outcome{\Rtwocase}{k}{label}{text}` form.
7. Don't edit outside your slice. Pointers use labels that already exist (app:derivations, app:design, app:schedule, app:supplementary, app:formatfit, app:scale, app:paired, app:composition, app:checkpoint, app:calibration, app:proxy, app:transport, app:heldout, app:decision, app:implementation, app:centring, sec:estimator, sec:data, sec:composition, sec:heldout, sec:family, sec:prediction).
8. R3-07 is mechanical: every "registered" in your slice becomes "pre-specified" (and "Registered" becomes "Pre-specified"), with articles fixed ("a pre-specified test"). Change nothing else in those sentences for R3-07.
9. Write one status line per finding to work/rebuttal/r3/status_{A,B,C,D,APP}.md as FIXED, SKIPPED (with reason) or NO-CHANGE, quoting the new text.

## Slice A (main.tex 28-45)

Abstract target: the words outside the \outcome scaffolding fall from 172 to at most 165 after all A edits.

R3-01. Replace "A shared item component at 0.124 of item-noise variance would reproduce 1.244." with "On the released item noise, a uniform item component shared across benchmarks would need more than the whole item-noise variance to produce that value." (results/snap-r3-r2-02: implied share 1.4225 on margins).

R3-02. Line 43: "We therefore scored all 45 PolyPythias runs ... and paired that battery" becomes "We therefore score all 45 PolyPythias runs ... and pair that battery". Keep the rest of the sentence apart from R3-36.

R3-04. Line 45, first contribution: after "identified up to an item component shared across benchmarks and halves" add at most 20 words saying the target transfers to a redrawn or extended bank and separates each benchmark's run variance from item noise, whereas the replicate standard deviation of the released-bank average answers only the fixed-bank question.

R3-06. Line 43, after "Two rules fixed before scoring read the results": add ", and in simulation the first passes in only 0.259 of replicates at a true 1.244 and the second returns undecided in 0.761, so we read both as bounds" (main.tex:205; results/snap-r2-r1-18b, results/snap-r2-r1-18). Don't quote the 0.957 figure (see R3-05).

R3-07. Lines 29, 41, 45: "registered" to "pre-specified".

R3-08. Line 33: scope the simulation to "a comparison of two independently trained configurations on the margin scale", and replace the closing clause "and the same understatement reaches the error bar of one model's battery average and the number of replicate runs a study plans" with a clause of the same length saying that on DataDecide's own recipe comparisons the correction changes few calls (Section~\ref{sec:prediction}), so the understatement shows mainly in the error bar of one model's battery average and in planning replicate runs. No new number.

R3-09. Abstract: write "a comparison on the margin scale declares a difference in 0.113"; add to the DataDecide sentence "at the largest checkpoint each configuration's runs share" (R1-15's scope; the 750M caveat stays in Section 3); delete ", so batteries compare through the aggregate standard deviation" (main.tex:91 carries it); in the R1-fail branch change "40 within-size contrasts" to "40 within-configuration contrasts" (wording inside a branch may change, the branch itself stays).

R3-10. Cut the abstract so the target above holds after R3-01, R3-09 and R3-11. Candidates: "with interval" before \ci where a comma does the job, and the "single-benchmark removals" clause shortened to "removals of one benchmark move the factor from 1.096 to 1.786". Keep the pre-specified-test sentence and the exploratory sentence, since KA's adjudication (P3) credits both.

R3-11. Replace "Our accuracy interval \ci{0.993}{1.157} includes one." with "On accuracy the interval \ci{0.993}{1.157} includes one, at a design that detects a true 1.10 in only 0.135 of replicates." (research/outputs/snap-r6-detect-power/r6_detect_power.json, lambda_1.10 0.13525).

R3-17. Pay for R3-06 and R3-11: delete the last sentence of line 41 ("The original ten benchmarks on the same runs give 1.240 ... (Section~\ref{sec:heldout})"), which Section 4.2 and Table 2 carry, and delete from line 39 the clause ", although at accuracy-like item noise this design detects a true ratio of 1.10 in only 0.135 of replicates" now that the abstract and the Discussion carry it.

R3-26. Line 45: "calibrated intervals" becomes "near-nominal intervals".

R3-27. If any "fixed before any held-out score existed" survives in A after R3-17, write "specified before any held-out score existed".

R3-36. Line 43: "built with the OLMES harness at the commit DataDecide used" becomes "built with the OLMES harness at a pinned commit" (appendices_bcd.tex:397 uses "pinned commit"), since no result file ties the commit to DataDecide's own evaluation (CA10).

## Slice B (main.tex 46-131)

R3-01 and R3-18 (edit together, line 71). Split the "Centring removes ..." sentence into two: one saying a run's deviation on every item of one prompt template recurs on any redrawn bank in that format and so belongs to fixed-battery run covariance, and one saying a run deviation tied to the particular items both halves share is a nuisance up to which the estimate is identified. Then replace the sensitivity and cross-format sentences ("whose share of item variance we treat as a sensitivity parameter that reproduces 1.244 at 0.124 (Appendix~\ref{app:calibration}). Cross-format covariances alone give inflation 0.921 \ci{0.801}{1.035}, with pairs averaging 0.007 (Appendix~\ref{app:supplementary}), which constrains a uniform component of that size,") with the released-noise result: on the released per-half item noise a uniform component shared by all ten benchmarks lifts margin inflation only to 1.024 at a share of 0.124 and would need a share of 1.42, more than the item noise itself, to produce 1.244, and a component carrying that excess would raise inflation from cross-format covariances alone to 1.113, which the observed 0.921 \ci{0.801}{1.035} excludes (Appendix~\ref{app:calibration}; results/snap-r3-r2-02: q0124 induced_full_matrix_lambda 1.0236, implied_share_q_star 1.4225, induced_cross_format_diagnostic 1.1133, cross_format_wild 0.9212 [0.8007, 1.0347]). Keep the closing clause that a component following scoring format is untested in DataDecide and that the cross-bank rule tests it in PolyPythias. Line 71 must end no longer than it is now.

R3-02. Line 131: "Both reading rules in Section~\ref{sec:family} were committed to the repository before any of these runs was scored." becomes "Both reading rules in Section~\ref{sec:family} were committed to the repository before scoring of either bank began." Line 129 "we score all 45 runs" already reads as design and stays.

R3-03 and R3-04 (edit together, line 63, at most 45 added words in total). After the fixed-bank sentence, say that this ratio takes the independent value from the per-benchmark replicate variances of the full-bank scores and uses no halves, so it needs no cross-half independence, and any item component the halves share counts as run variance on the fixed bank. Then say the two targets nearly coincide on margins because item noise is 0.037 of the full-bank margin diagonal, while without BoolQ it is 0.578 of the accuracy diagonal and the fixed-bank value of 1.285 falls well below the split's 1.558 (results/snap-r3-r2-26: share_of_diag_removed 0.0366 and 0.5777; no_boolq accuracy full_bank_uncorrected 1.2852, split_half 1.5578).

R3-07. Line 96 (Algorithm caption): "registered test" to "pre-specified test".

R3-10. Pay for B's additions: delete line 115 ("Two later additions ... reports recipe influence."), whose content sits in app:calibration and app:derivations, and cut "and neither interval width alone identifies a design effect" from line 111. If more room is needed, cut the last sentence of line 127 ("Our standardised diagnostics ... inherit that problem.").

R3-24. Line 93, second sentence: replace with "Subtracting item-sampling variance from the full-data diagonal uses every item but needs a model of within-half item noise, while the split needs only independence between halves, and on the released runs the two agree, 1.246 \ci{1.144}{1.340} against 1.244 on margins with interval widths within 5 percent, since recipe-level seed variation sets the width (Appendix~\ref{app:implementation})." (results/snap-r3-r2-26: analytic 1.2456 [1.1439, 1.3398]; wild width ratios 1.0054, 1.0246, 0.9539, 0.9865). APP adds the backing paragraph.

R3-32. Line 123: "intervals too wide to separate the value one from the full-sample estimates, although the full-sample margin auxiliary contrast, whose runs sit near their final steps, still excludes one".

R3-33. Line 113: "so in these populations finite-sample bias works against finding an excess". Add no mechanism.

R3-36. Line 131: "with OLMES at the commit DataDecide used" becomes "with OLMES at a pinned commit".

## Slice C (main.tex 133-200)

R3-07. Lines 173 (subsection title "A pre-specified test on unseen tasks"), 175, 177, 181: "registered" to "pre-specified". The label sec:heldout stays.

R3-27. Line 175: "a comparison we fixed before any held-out score existed" becomes "a comparison we specified before any held-out score existed". Table 2 caption (line 181): "the original rows read the released runs at the same sizes and were fixed before any held-out score existed" becomes "the original rows read the released runs at the same sizes as a comparison specified before any held-out score existed".

R3-28. Line 199: after "between 1.120 and 1.213" add "and the removal of DROP, at 1.213 \ci{1.035}{1.377}, is the only one whose interval excludes one" (compute extra/heldout/outputs/k04-heldout-full/heldout_table.csv, without_drop_mc margin/all 1.2135 [1.0347, 1.3766]; SciQ, MedMCQA and CoQA removals all reach below one).

R3-29. Line 199: add one clause saying that on these tasks accuracy excludes one while margins don't, so which scale carries more seed signal depends on the battery. Drop it if C can't pay for it, and record SKIPPED with the word count.

R3-30. Line 175: delete "Interval width rather than the point gap decides the registered verdict." Line 177: shorten "a bar both AGIEval tasks missed by about a thousandth, inside the pilot's sampling error of about 0.010" to "a bar both AGIEval tasks narrowly missed (Appendix~\ref{app:heldout})". These cuts pay for R3-28, R3-29 and R3-31.

R3-31. Line 163: after the recipe-removal range add "and all 300 recipe-pair deletions keep the margin interval above one, between 1.177 and 1.263 (Appendix~\ref{app:supplementary})" (research/outputs/snap-r6-leave-one-out/r6_leave_one_out.json, leave_two_recipes_full_margin 300/300, 1.17726 to 1.26289).

R3-44. Line 175: "the two point estimates differ by 0.024" becomes "the two point estimates differ by about 0.02".

## Slice D (main.tex 201-243, reproducibility statement 250-251)

R3-01 and R3-17 (line 237). Replace "A scalar item effect shared across benchmarks ... (Appendix~\ref{app:calibration})." with: a uniform item effect shared across benchmarks can't produce the margin value on the released item noise (Section~\ref{sec:estimator}), while on accuracy a share of 0.053 of item-noise variance would reproduce 1.078 and the accuracy cross-format interval \ci{0.848}{1.063} doesn't exclude the 1.047 it implies, and a component that follows scoring format remains unmeasured in DataDecide (results/snap-r3-r2-02: accuracy implied_share_q_star 0.0526, induced 1.0469, cross_format_wild [0.8484, 1.0634]). Drop the 0.05 and 0.007 simulated-population figures from the main text (APP keeps them, labelled). Delete the paragraph's last sentence ("A scalar component shared by every benchmark would also enter the cross-format pairs ... scoring format."), which repeats line 71. Keep the three \outcome{\Rtwocase} sentences.

R3-02. Line 251: replace "The PolyPythias battery and the second bank were scored in float32 with transformers 4.57.1 on Kaggle T4 cards, each run checking its cached scores against an uncached reference on 24 items to within 0.001 nats, and the release ships the frozen hashes of both request files with the kernels that scored them." with "We score the PolyPythias battery on both banks in float32 with transformers 4.57.1 on Kaggle T4 cards, each run checking its cached scores against an uncached reference on 24 items to within 0.001 nats, and the release will include the hashes of both request files, the bank-two file as a deterministic rebuild from its manifest, with the scoring kernels." (results/snap-r2-r1-49/r1_49_bank2_manifest.json is a rebuild, not a pre-scoring freeze.)

R3-03. Line 237: after "the shared-item check unrun in the family that supplies our headline" add ", although the fixed-bank value of 1.237 (Section~\ref{sec:estimator}) needs no such check for the released bank".

R3-04. Line 241: replace the first sentence with one saying that for a fixed released bank the replicate standard deviation of the battery average gives the aggregate uncertainty directly and we recommend reporting it with a benchmark-removal check, while the split adds the item-general value for a redrawn or extended bank, the per-benchmark run variances and $K_{\mathrm{eff}}$ for planning run counts. Replace "Our ratio therefore measures this battery and helps only where replicates are missing and the target battery's own ratio is close." with "The ratio itself belongs to this battery." Net neutral.

R3-05. Line 205: replace "and under independence with a 0.124 item share it returns supported in 0.033 and undecided in 0.957, so an undecided verdict is expected under either explanation and not supported doesn't exclude a shared component." with "while a uniform item share of 0.124, which on this family's noise lifts the median within-bank estimate only to 1.046, gives supported in 0.033 and undecided in 0.957, so the simulation doesn't show the rule's behaviour under a component large enough to explain the inflation, and not supported can't exclude one." (results/snap-r2-r1-18/r1_18_rule_two.json, independence_share0124 within_lambda_median 1.0458.)

R3-07. Line 237 ("Apart from the registered test, which failed at its registered scope") and line 251 ("The registered test ships with its protocol"): "registered" to "pre-specified". The line 251 held-out sentence describes a finished test and stays in the past tense otherwise.

R3-14. Line 230: replace "and what we add is the estimand and its measurement" with "and what we add is the estimand, run covariance across benchmarks at a fixed configuration, and its measurement on released pretraining runs, which \citet{miller2024} and \citet{heineman2025} don't estimate" (both keys verified; the Heineman claim matches line 232). Don't characterise generalizability theory further (R2-24).

R3-15. Line 228: "finds run deviations in accuracy nearly independent across ImageNet evaluation sets" becomes "finds run deviations in accuracy nearly independent across shifted ImageNet test sets", and "We know of no study that estimates the covariance of run noise between benchmarks" becomes "Apart from such shifted test sets, we know of no study that estimates the covariance of run noise between distinct benchmarks" (citation_audit.md CI1).

R3-16. Line 241: name the data as "the 4,755-item three-size PolyPythias transfer runs of Appendix~\ref{app:transport}", add "at three sizes" to the pooled-target numbers (0.275 against 0.319 and 0.367 against 0.523 are three-size values, research/outputs/snap-r12-predict-pooled/r12_predict_pooled.json), and add one clause saying this target is one configuration's six-run ratio, unlike the pooled recipe folds of Section~\ref{sec:prediction}. Pay with R3-04's replacement sentence.

R3-19. Line 205, last sentence: "In an exploratory reading we added after fixing that rule, a failing estimate at or above 1.026 is consistent with the DataDecide value and its jackknife upper limit bounds inflation in this family, while one below 1.026 counts against transfer." Leave the R1-fail branch's "\pending{bounds the effect in this family / counts against transfer}" as it is.

R3-20. Line 251: "The PolyPythias transfer, five-size rescore, and checkpoint results come from earlier execution records" becomes "The earlier 4,755-item PolyPythias transfer check, its five-size extension, and the checkpoint results come from earlier execution records". Also cut ", and the plan's screening split was never formed" from the same paragraph (R3-17; line 125 carries it).

R3-22. Line 241: "three runs each let the margin interval exclude one in 0.997 of replicates" becomes "at the observed mean seed correlation, three runs each let the margin interval exclude one in 0.997 of replicates" (compute extra/heldout/outputs/k08-seed-count/seed_count_power.json; appendices_bcd.tex:454 gives 0.061 on margins).

R3-34. Line 235: "The full-battery accuracy interval includes one, and at accuracy-like item noise this design detects a true ratio of 1.10 in only 0.135 of replicates, and the primary analysis gives an upper limit of 1.157 at the scored checkpoint." Add the truncation subset to the list of exploratory cuts: "without BoolQ at 1.558, without the 26 truncated configurations at 1.120, at the adjacent checkpoint and on the held-out tasks" (main.tex:123, 1.120 \ci{1.020}{1.208}).

R3-35. Line 224: "so seed matching doesn't explain the few changed calls" becomes "so shared seed labels don't change the correction's effect".

R3-40. Line 228: "\citet{miller2024} gives clustered and paired item-sampling errors with run variance fixed" becomes "\citet{miller2024} gives clustered and paired item-sampling errors with each model treated as fixed" (citation_audit.md CI3).

Cuts available in D if the slice runs long: line 218 "A masked matrix needn't stay positive semidefinite, and" (keep "format and task content aren't separable here"), and line 239 "At 1B alone the cluster-$t$ margin interval of 0.811 to 1.628 includes one (Appendix~\ref{app:supplementary})."

## Slice APP

R3-01. appendices_bcd.tex:259: label the existing sweep as a simulated population ("In a simulated population with item noise of 0.73 on a unit-variance latent, a share near 0.124 reproduces ..., and accuracy reaches 1.078 near 0.009"; source: injection_model field of r2_02_shared_component_crossformat.json and the snap-r6-sharednoise generator). Then add one paragraph with the released-noise results from results/snap-r3-r2-02: margin q* 1.4225 with induced cross-format 1.1133 excluded by \ci{0.801}{1.035}; share 0.124 gives full-matrix 1.024 and cross-format 1.010; accuracy q* 0.0526 with induced 1.047 inside \ci{0.848}{1.063}; share 0.124 on accuracy gives 1.177 and cross-format 1.107, which the accuracy interval excludes; adding the 0.124 share to the observed products gives margin cross-format 0.933 \ci{0.808}{1.050}. State the injection model in one sentence (one run-level scalar shared by all ten benchmarks and identical in both halves). Replace "We haven't measured this component in the released scores" with a sentence saying a uniform component is now bounded as above while a format-following one stays unmeasured in DataDecide. appendices_bcd.tex:128: after "the 1.153 expected from uniformly distributed covariance contributions" add that a uniform shared item component carrying the whole margin excess would imply 1.113, which the interval also excludes.

R3-02. appendices_bcd.tex:349: "close to the released ratio of 6,808 to 37,682" becomes "close to the built ratio of 6,808 to 37,682". Grep the appendix files for any other past-tense PolyPythias bank-one or bank-two scoring claim and apply global rule 3.

R3-05. appendices_bcd.tex:349: replace "When a shared item share of 0.124 alone produces the within-bank excess, it returns" with "Under independence with a uniform shared item share of 0.124, it returns", keep "and on this family's item noise that share lifts the median within-bank estimate only to 1.046 against a cross-bank median of 0.999", and replace "An undecided second rule is the expected outcome under either explanation, and a verdict of not supported doesn't exclude a shared component." with "That share falls far short of the inflation it would need to explain, as it does on the released DataDecide noise, so the simulation doesn't show the rule's behaviour under such a component, and a verdict of not supported can't exclude one."

R3-07. appendices_bcd.tex (four occurrences): "registered" to "pre-specified".

R3-22. appendices_bcd.tex:379: "At 125 configurations and three runs the margin effect clears one in 0.970 of replicates" becomes "At a true ratio of 1.25 under compound-symmetric correlation and margin item noise of 0.73, 125 configurations and three runs clear one in 0.970 of replicates" (research/outputs/snap-r6-detect-power-margin/r6_detect_power_margin.json, lambda_1.25 0.96975). Find the source of the accuracy 0.111 (appendices_bcd.tex:379 and :391) under research/outputs or compute extra/*/outputs; name its true ratio and population if found, and delete the clause if not, recording which in the status file.

R3-24. Add one paragraph to app:implementation (Interval calculation) with the R2-26 comparison: the analytic correction subtracts $\sum_j v_{cj}/K^2$ from $T_c$ and $U_c$, with $v_{cj}$ from the item-by-run interaction mean square in each group, and it assumes item-by-run noise independent across items within a group; margins 1.246 \ci{1.144}{1.340} against 1.244 \ci{1.143}{1.338}; accuracy 1.082 \ci{0.994}{1.162} against 1.078 \ci{0.993}{1.157}; without BoolQ 1.792 \ci{1.699}{1.878} against 1.786 on margins and 1.595 \ci{1.450}{1.721} against 1.558 on accuracy; wild width ratios 1.005, 1.025, 0.954 and 0.986; item noise 0.037, 0.186, 0.092 and 0.578 of the full-bank diagonal, where the uncorrected full-bank values are 1.237, 1.067, 1.734 and 1.285 (results/snap-r3-r2-26/r2_26_analytic_vs_split.json).

R3-25. appendices_bcd.tex:393: no value changes, since 0.00824 and 0.04382 round to the printed 0.008 and 0.044. Record NO-CHANGE with the source results/snap-r3-r2-43/r2_43_band_share.json.

R3-37. appendices_bcd.tex:387: check research/outputs/snap-r6-size-shared-b/r6_size_shared_b.json and snap-r6-size-shared for the other cells in the same sentence (0.943, 0.951, 0.935, 0.898). If they come from the 10,000-replicate run, print 0.823 and 0.581; otherwise append "(pooled over 12,000 replicates)" to the 0.821 and 0.580 clause.

R3-38. appendices_bcd.tex:216: "for a true gap below 0.01196" becomes "for a single-run comparison with a true gap below 0.01196", and "At a true gap of 0.005 the same calculation gives" becomes "At a true gap of 0.005 the same single-run calculation gives". Don't recompute the 455 count.

R3-39. appendices_bcd.tex:73: "noting positive task correlation without estimating it" becomes "noting that positive task correlation would make the combination conservative, without estimating that correlation" (citation_audit.md CI2).

R3-40. appendices_bcd.tex:73 and supplement_extended_body.tex:127: "while holding run variance fixed" becomes "while treating each evaluated model as fixed".

R3-41. supplement_extended_body.tex:715 and :716: apply half-up rounding against compute extra/heldout/outputs/k12-rule-power-n073/k12_heldout_rule_power.json pass_table, giving 0.181 for 0.1805 and 0.793 for 0.7925; check every cell of both rows against the file.

R3-42. appendix_a.tex:103: "The author-reported power calculation" becomes "Our planning power calculation". Apply the same first-person change to "the shipped" where it means our own interval or proxy, and leave "the analysis record" where it names a document. Change no fact.

R3-43. appendices_bcd.tex:375: delete " (Kaggle CPU kernel snap-r2-r1-49)".

## Not for fixers

NEEDS-EXPERIMENT: R3-12 (GPU, score the 375 DataDecide runs on bank two) and R3-23 (GPU, a population above 1B or generative tasks). Deferred: R3-21 needs a citation audit to verify entries for the fourteen benchmarks, AGIEval and OLMES before anyone cites them. REJECTED: R3-13, R3-45 to R3-49, reasons in REBUTTAL_LOG.md.

Out-of-loop action for the author (KA7): a third-party timestamp (for example OpenTimestamps or an OSF deposit) of the rule commit, made before PolyPythias scoring ends, would let the paper cite independent corroboration for the two rules. It reaches an outside service, so the loop doesn't do it.
