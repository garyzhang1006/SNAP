# Rebuttal hardening log

Loop: hourly cron job cf2dbd6f (session-only, 7-day expiry). Stop rule: two consecutive completed rounds with zero new findings rated likely to lower the score.

Standing constraints: CPU-only Kaggle kernels for any new numbers (enable_gpu false, enable_tpu false), no local compute, no GPU anywhere, no Workflow tool, no number without a results file in the repo, no citation without citation-audit verification, page-9 limit, stop-slop on edited paragraphs.

## Round 1, started 2026-09-23 00:40 EDT

Pre-round snapshot: commit 27198cd. Excluded from git via .git/info/exclude: deliverables/SNAP_supplement.zip (62M) and research/style_study/corpus3/ (49M).

Skills run this round: superpowers:using-superpowers (rule applied), aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), each as a parallel Agent; Codex CLI (codex exec) stands in for the unavailable mcp__codex__codex cross-model threads. Skipped by the compute rule: aris:run-experiment, aris:vast-gpu, aris:serverless-modal, aris:experiment-queue, aris:experiment-bridge, evaluation:*. Note: aris:kill-argument's own guidance asks not to be wrapped in /loop or CronCreate; the user's loop instruction takes precedence, and later rounds only re-run it when main.tex changed.

Raw reviewer outputs: work/rebuttal/r1/*.md

### Findings (merged, deduplicated, ranked)

Merged 2026-09-23 from KA (kill_argument), CA (claim_audit), CI and the citation-audit tables (citation_audit), PA (paper_audit) and AR (academic_reviewer). Every quote below was checked against deliverables/*.tex at commit 27198cd. Ranking runs from most to least likely to lower the score. Section owners: A abstract and intro, B Secs 2 and 3, C Secs 4.1 and 4.2, D Secs 4.3 to 4.5, E related work, discussion, statements and references.tex, APP appendix files, PAGE the length limit. A finding that spans sections is split into sub-findings with one owner each, and the sibling ids are cross-listed.

Totals: 63 findings (51 FIX-TEXT, 6 NEEDS-EXPERIMENT, 6 REJECT). By section: PAGE 1, A 13, B 11, C 8, D 11, E 15, APP 4.

#### R1-01 | PAGE | critical | lowers score: yes | FIX-TEXT
- Sources: KA8, PA5, AR8; cut targets PA12, PA16, PA21.
- Quote: `\label{maintext:end}` (main.tex:277), which main.aux places at `\newlabel{maintext:end}{{6}{11}...}`.
- Objection: The main text ends on page 11 against the ICLR 2027 nine-page limit, which risks a desk reject before any reviewer reads the paper.
- Rebuttal: The submitted version fits nine pages, since we moved the decision table, the held-out power history, the later interval checks and the information-ratio calculation to existing appendix paragraphs, and no result left the paper.
- Fix: Apply paper_audit cuts C1 to C7 (74 lines against a 60-line need): trim the abstract (see R1-07), move Table 3 `tab:decision` to `app:decision`, move the l.207 power-and-history paragraph to `app:heldout`, move the l.228 calibration and PolyPythias paragraph to `app:calibration`/`app:transport`, cut l.226 from "The fit is in sample" to the end into `app:formatfit`/`app:scale`/`app:proxy`, replace l.126 with one sentence pointing to `app:calibration`, and move l.115 to l.120 with Eq. `eq:information` to Appendix A. Hold C8 to C14 in reserve for text the other fixes add, and recompile to confirm `maintext:end` lands on page 9.
- Status: FIX-TEXT. The line counts are estimates from word counts, so the recompile is the check.

#### R1-02 | A | critical | lowers score: yes | FIX-TEXT
- Sources: KA1, PA2, AR3 (siblings R1-05 in B, R1-06 in E).
- Quote: "takes cross-half products of run-centred scores so item-sampling noise drops out" (abstract, main.tex:29).
- Objection: The title and abstract promise run-to-run covariance unconditionally, while Sec 2.2 concedes that item noise shared across benchmarks and halves enters the numerator and that a 0.124 share of item variance reproduces 1.244.
- Rebuttal: Section 2.2 states the identification condition and quantifies the item share that would reproduce the headline, and the cross-format pairs, which average 0.007 with a diagnostic of 0.921, constrain a uniform shared component. We agree the abstract should carry the condition and have moved it there.
- Fix: Change the abstract clause to "so item-sampling noise that the two halves don't share drops out, although an item effect shared across benchmarks and repeated across halves would enter the estimate, and a 0.124 share of item variance would reproduce the margin value". In the contributions paragraph (l.47) write "item-general run covariance, identified up to a shared item component". The title can stay if the abstract carries this sentence.
- Status: FIX-TEXT.

#### R1-03 | A | critical | lowers score: yes | FIX-TEXT
- Sources: AR1, AR20, KA10, PA4 (siblings R1-04 in D, R1-21 in E).
- Quote: "In simulation with margin-like covariance, such a comparison declares a difference in 0.113 of replicates with a true gap of zero, against a nominal rate of 0.05." (main.tex:33)
- Objection: The introduction motivates the paper with a simulated false-positive rate of 0.113, while the paper's own real recipe comparisons show the covariance changes the wrong-call rate by at most 0.009, and no sentence reconciles the two.
- Rebuttal: The simulation compares two independently trained configurations, while DataDecide's recipe comparisons within a size band share seed labels, and on those paired comparisons the paired-difference standard deviation has median ratio 1.024 to its independence value. The covariance therefore matters most for the error bar on one model's battery average and cancels largely in seed-matched paired comparisons, which is why the real decision effect is small.
- Fix: Add one sentence after l.33: "On DataDecide's recipe comparisons, whose runs within a size band share seed labels, the paired-difference standard deviation has median ratio 1.024 to its independence value and the wrong-call rate changes by at most 0.009, so the covariance matters for the error bar of a single battery average more than for seed-matched comparisons." Keep the seed-label mechanism worded as an explanation, since no analysis on file isolates it (R1-20 would).
- Status: FIX-TEXT.

#### R1-04 | D | critical | lowers score: yes | FIX-TEXT
- Sources: AR1, AR14, PA4 (siblings R1-03 in A, R1-21 in E, R1-20 for the experiment).
- Quote: "That changes the share of wrong calls by at most 0.009, from rates between 0.029 and 0.070, and every recipe-bootstrap interval for that change reaches zero" (main.tex:236).
- Objection: The paper measures an effect and then shows it barely changes real decisions, while independence also predicts measured ratios better out of sample, so a reviewer reads the result as a careful measurement of something that doesn't matter.
- Rebuttal: Sec 4.5 compares recipes at one size, and the release gives every recipe in a size band the same seed labels, so paired recipe differences cancel most of the shared run deviation, and the paired ratio of 1.024 in the same subsection shows it. The covariance changes the error bar of an unpaired or single-model battery average, where Table 1 gives an aggregate standard deviation 1.244 times the independence value on margins.
- Fix: At the end of the l.236 paragraph add "Recipes within a size band share seed labels, so these comparisons are paired, which matches the paired-difference ratio of 1.024 above and explains why the correction changes few calls." Move the l.234 paired-ratio sentence ahead of the decision paragraph so the explanation precedes the null.
- Status: FIX-TEXT.

#### R1-05 | B | major | lowers score: yes | FIX-TEXT
- Sources: KA14, AR3, PA2 (siblings R1-02 in A, R1-06 in E).
- Quote: "Item noise shared across benchmarks and repeated across halves would also enter the numerator, and we therefore read our estimate as identified only up to that component, since Appendix~\ref{app:calibration} shows a 0.124 share of item variance would reproduce 1.244." (main.tex:75)
- Objection: The paper never says operationally what such a shared item effect is or how it differs from a run effect, and it doesn't present 0.124 as a sensitivity bound next to the evidence that constrains it.
- Rebuttal: A shared item effect is a property of the item set that every run inherits, such as a prompt-format artefact present in every item of one template, whereas a run effect differs across runs. The 0.124 share is a sensitivity parameter, and the cross-format average of 0.007 with a diagnostic of 0.921 rules out a uniform component of that size while leaving a format-following one open, which Sec 4.3 tests in PolyPythias.
- Fix: After the l.75 sentence add: "An example is a prompt-format artefact carried by every item of one template, which a split within one item set can't remove. We treat the 0.124 share as a sensitivity parameter, and the cross-format pairs, averaging 0.007 with a diagnostic of 0.921 (Section 4.4), constrain a uniform component but not one that follows scoring format." Move the l.271 share-of-0.05 sentence here if space allows.
- Status: FIX-TEXT.

#### R1-06 | E | major | lowers score: yes | NEEDS-EXPERIMENT
- Sources: AR3, PA2, KA1, AR demanded experiment 1 (siblings R1-02, R1-05).
- Quote: "We didn't score the 375 DataDecide runs on the second bank, which leaves the 1.244 untested on fresh items and the shared-item check unrun in the family that supplies our headline." (main.tex:271)
- Objection: The identification check runs only in PolyPythias, so the family that supplies the headline has no test of the shared-item alternative.
- Rebuttal: We agree this is the main open check, and the limitation says so in the same words. The cross-bank rule in PolyPythias uses the same battery, prompts and OLMES commit, so a pass there constrains the item-set explanation for these ten benchmarks, although it can't settle the DataDecide value.
- Fix: No text removes the objection. Keep l.271 and make sure the abstract names the gap (R1-02).
- Status: NEEDS-EXPERIMENT. Score 375 DataDecide checkpoints on the 6,808-item second bank, which needs GPU inference and is blocked by this loop's CPU-only constraint.

#### R1-07 | A | major | lowers score: yes | FIX-TEXT
- Sources: PA13, AR9, KA8 (cut C1).
- Quote: "(interval \ci{1.143}{1.338}, lower endpoint 1.095 under a test inversion added later)" (abstract, main.tex:29).
- Objection: The abstract runs about 330 to 380 words with more than twenty numbers and several process disclaimers, and it reads as an audit log without a stated thesis.
- Rebuttal: The revised abstract is about 200 words and states the problem, the estimator, the headline with its interval, the battery dependence, the accuracy limit, the registered-test verdict and the practical rule, with the process detail left to the body.
- Fix: Delete the test-inversion parenthetical, the "which makes the ten-benchmark average as noisy as an average of 6.5 independent benchmarks" clause, the "removing it still leaves 1.786" clause, the "while on the same runs the original ten benchmarks give 1.240" comparison and the timestamp clause; keep one sentence each for the method, 1.244 \ci{1.143}{1.338}, BoolQ's 68% share, the accuracy interval, the registered test, the R1/R2 outcome and the recommendation.
- Status: FIX-TEXT.

#### R1-08 | B | major | lowers score: yes | NEEDS-EXPERIMENT
- Sources: AR2, AR question 1, AR demanded experiment 2.
- Quote: "Repeated evaluation of a fixed item bank can retain this component. Its run variance needn't equal the item-general variance estimated here." (appendix_a.tex:6), against "We estimate item-general covariance from two disjoint item halves per benchmark" (main.tex:35).
- Objection: A practitioner evaluates on a fixed released bank, whose run variance includes run-by-item interaction that SNAP removes by construction, and the main text never says which estimand a user needs or reports the fixed-bank value.
- Rebuttal: SNAP targets covariance that generalises to the item population, which is the quantity that transfers to a re-drawn or extended bank, while reproducibility on the released bank is a different question that the replicate standard deviation of the full-bank average answers directly, as our recommendation says. We report both on the same runs in the revision.
- Fix: Move the two appendix_a.tex:6 sentences into Sec 2.2 after l.75 and add one sentence naming which question each estimand answers.
- Status: NEEDS-EXPERIMENT. Compute fixed-bank inflation (replicate SD of the full-bank battery average against the independence value, no split) for margins and accuracy from the released per-item scores; CPU-feasible on a Kaggle CPU kernel.

#### R1-09 | A | major | lowers score: yes | FIX-TEXT
- Sources: CA1, PA3, AR18.
- Quote: "and every recipe, recipe-pair and benchmark deletion leaves an interval that excludes one." (abstract, main.tex:29) and "excludes one under every recipe, pair and benchmark deletion" (main.tex:47).
- Objection: The list leaves out size-band deletion, where dropping 530M gives \ci{0.993}{1.338} and reaches one, so the robustness claim reads as selective.
- Rebuttal: The size deletion is reported in Sec 4.1 and its lower limit is 0.993. We have added it to the abstract and contributions so the robustness statement covers every deletion class.
- Fix: In both places write "every recipe, recipe-pair and benchmark deletion, and four of the five size-band deletions, leaves an interval that excludes one (dropping 530M gives a lower limit of 0.993)".
- Status: FIX-TEXT.

#### R1-10 | A | major | lowers score: yes | FIX-TEXT
- Sources: KA3, AR7, PA8, CA13, KA P3 (siblings R1-37 in B, R1-38 in E).
- Quote: "Every other analysis is exploratory, no registration carries an independently corroborated timestamp" (abstract, main.tex:29) and "Every analysis apart from the registered test is exploratory." (main.tex:49)
- Objection: The contributions and abstract are dominated by admissions, repeated across the paper, and the "every other analysis" wording contradicts the two PolyPythias rules described as fixed before scoring.
- Rebuttal: The disclosure is deliberate, and the revision keeps one consolidated provenance statement in the limitations and one clause in the abstract. The pre-specified analyses are the registered test and the two PolyPythias rules, and everything else is labelled exploratory.
- Fix: Replace both sentences with "Apart from the registered test and the two PolyPythias rules, every analysis is exploratory"; drop "no registration carries an independently corroborated timestamp" from the abstract and "Neither the analysis plan nor the protocol's registration carries an independently corroborated timestamp, and the plan's screening split was never formed" from l.49, keeping both facts in the limitations.
- Status: FIX-TEXT.

#### R1-11 | C | major | lowers score: yes | FIX-TEXT
- Sources: AR6, CA7, KA P4, PA8.
- Quote: "We added a noise level of 2.00 after seeing the two-size width" and "Three earlier results failed the rule as well, at 530M alone, at 530M and 750M, and at those two sizes with the 18 recipes first scored at 1B added, with estimates between 1.181 and 1.201" (main.tex:207).
- Objection: The only registered test failed, the task list changed after a pilot, and the post hoc power simulation and earlier scopes placed beside the failure read as rescue attempts or as forking paths, especially since two further partial readouts go unmentioned.
- Rebuttal: The failure is reported as a failure, and the paragraph closes by saying the later power calculation can't rescue it. Every scope we read is now listed, the 750M-only and 1B-only readouts included, and all of them sit between 1.152 and 1.203, so no scope was dropped for its value.
- Fix: Move the noise-level-2.00 simulation and the earlier-scope sentence to `app:heldout`, and there list all five partial readouts with the range 1.152 to 1.203 (from compute extra/heldout/outputs k04-heldout-750m 1.2029 and k04-interim-1b 1.1521). Keep in the main text only l.183's width explanation and "The later power calculation can't rescue this registered test."
- Status: FIX-TEXT.

#### R1-12 | A | major | lowers score: yes | FIX-TEXT
- Sources: PA1, KA9 (siblings R1-13 in C, R1-14 in B).
- Quote: "which makes the ten-benchmark average as noisy as an average of 6.5 independent benchmarks with the same average variance" (abstract, main.tex:29) and "At that value the ten benchmarks average like 6.5 independent ones of the same average variance, with an interval from 5.6 to 7.7." (main.tex:47)
- Objection: Removing BoolQ raises inflation to 1.786 while the average becomes less noisy, so the effective-benchmark count doesn't rank batteries by aggregate noise and the headline framing misleads.
- Rebuttal: The factor and K_eff compare a battery with independence at its own variances, so they describe the covariance share within one battery and not its absolute noise. The aggregate standard deviation is the cross-battery quantity: on margins it falls from 0.00572 to 0.00516 when BoolQ is removed, even as the factor rises.
- Fix: Delete the 6.5-benchmark clause from the abstract (also cut C1), and in l.47 follow the 6.5 sentence with "a within-battery comparison, since removing BoolQ raises the factor to 1.786 while the aggregate standard deviation falls from 0.00572 to 0.00516" (values from research/outputs/snap-r11-removal/r11_removal.json).
- Status: FIX-TEXT.

#### R1-13 | C | major | lowers score: yes | FIX-TEXT
- Sources: AR4, PA1, KA9 (siblings R1-12, R1-14).
- Quote: "We find that BoolQ dominates the battery, contributing 68\% of the margin covariance trace and 84\% of the accuracy trace." (main.tex:167)
- Objection: One benchmark sets the factor, removals move it from 1.096 to 1.786, and the reviewer asks whether 1.244 describes LLM evaluation or this list of ten benchmarks.
- Rebuttal: The general finding is the format structure, with correlations averaging 0.624 within scoring formats and 0.007 across them, and 1.244 is its value for this battery, where BoolQ is the only benchmark in its format and carries most of the trace.
- Fix: Open the l.167 paragraph with "The factor belongs to the battery: margin correlations follow scoring format (0.624 within, 0.007 across; Section 4.4), and BoolQ, alone in its format, carries 68% of the margin trace." Replace "A larger factor accompanies a less variable average." with "Removing it raises the factor while the margin aggregate standard deviation falls from 0.00572 to 0.00516, because the factor compares the battery with independence at its own variances."
- Status: FIX-TEXT.

#### R1-14 | B | major | lowers score: yes | FIX-TEXT
- Sources: PA1 (siblings R1-12, R1-13).
- Quote: "Note that our $K_{\mathrm{eff}}$ compares this battery against independent benchmarks of the same average variance and doesn't count independent information sources." (main.tex:95)
- Objection: The definition never tells the reader that the factor can't compare batteries, which is what the BoolQ result later exposes.
- Rebuttal: The definition compares a battery with itself under independence, and Table 1's aggregate standard deviation column is the quantity for comparing batteries.
- Fix: Append to l.95: "Because both quantities normalise by the battery's own trace, they can rise when a high-variance benchmark is removed while $\sigma_{\mathrm{agg}}$ falls, so we compare batteries through $\sigma_{\mathrm{agg}}$ (Table~\ref{tab:primary})."
- Status: FIX-TEXT.

#### R1-15 | A | major | lowers score: yes | FIX-TEXT
- Sources: KA2, AR12, KA P2 (sibling R1-16 in B).
- Quote: "As a worked example we apply SNAP to 375 released DataDecide runs spanning 125 configurations and ten benchmarks." (abstract, main.tex:29)
- Objection: DataDecide replicates mix seed with checkpoint step and training schedule, and the abstract never names the estimand as covariance among released runs at the selected checkpoints.
- Rebuttal: Sec 3 defines the estimand as covariance among released runs at the largest step shared by each configuration's three runs, and the auxiliary contrast, which removes the default-versus-auxiliary batch component, gives 1.256 \ci{1.090}{1.400}. PolyPythias seeds rerun one recipe at one shared step and give the schedule-free check.
- Fix: Change the sentence to "to 375 released DataDecide runs at the largest checkpoint step shared within each of 125 configurations, whose replicates differ in seed and partly in checkpoint schedule".
- Status: FIX-TEXT.

#### R1-16 | B | major | lowers score: yes | FIX-TEXT
- Sources: KA2, AR12, AR question 4 (sibling R1-15).
- Quote: "On the 33 configurations that share a final step, margin inflation is 1.082 (\ci{0.121}{1.530}) and accuracy 1.129 (\ci{0.769}{1.397}), and both intervals include one." (main.tex:133)
- Objection: The only truncation-free subset gives an interval that includes one, so part of the headline could be schedule or checkpoint difference rather than seed noise.
- Rebuttal: The 33-configuration interval is 1.41 wide against 0.195 for the full sample, so it can't distinguish 1.0 from 1.244 and carries no evidence either way. The auxiliary contrast in Table 1 removes the batch component and gives 1.256, and dropping the 26 severely truncated configurations gives 1.276 \ci{1.114}{1.420}.
- Fix: Append to the sentence ", an interval 1.41 wide against 0.195 for the full sample, so the subset can't separate 1.0 from 1.244", and add after it "The auxiliary contrast (Table~\ref{tab:primary}, 1.256) removes the default-versus-auxiliary batch component but not differences shared with the checkpoint schedules, and the PolyPythias seeds (Section~\ref{sec:family}) share one final step."
- Status: FIX-TEXT.

#### R1-17 | D | major | lowers score: yes | FIX-TEXT
- Sources: KA6, KA7, AR11, AR question 7, KA P5.
- Quote: "A component that the halves of one item set share can't account for the inflation we measure on PolyPythias." (main.tex:219) and "taking the train split for eight benchmarks" (main.tex:141).
- Objection: The not-supported branch reads an interval that includes zero at a sixth of the items as exclusion, the confound caveat appears only in that branch, and bank two's train split may carry pretraining contamination for Pile-trained Pythia on one side only.
- Rebuttal: The rule's verdict names are fixed, but the interpretation sentence now says the check found no evidence and gives the upper limit of the difference as the bound. The bank differences (split, item count and exemplar overlap) apply to every branch, and train-split contamination is one of them, since it could add a run component on bank two only.
- Fix: Replace the quoted l.219 sentence with "The check gives no evidence that a component the halves of one item set share accounts for the inflation on PolyPythias, and the difference interval bounds such a component at \pending{hi} in log inflation." Move "The two banks also differ in split, in item count, and in exemplar overlap..." from l.219 into the rule paragraph at l.213 and add "and train items are more likely to appear in pretraining data".
- Status: FIX-TEXT.

#### R1-18 | D | major | lowers score: yes | NEEDS-EXPERIMENT
- Sources: KA4.
- Quote: "It supports the explanation when the difference is positive and the cross-bank interval covers one, and we report any other pattern as undecided." (main.tex:213)
- Objection: "Positive" is undefined (point estimate or lower limit), and with bank two at a sixth of bank one a cross-bank interval covering one is likely from noise alone, so "supported" can fire without any shared-item component and no operating characteristics are given.
- Rebuttal: The sentence now quotes the committed rule's definition of "positive" (check the rule commit before drafting; this merge did not read it). We simulated rule two's branch probabilities under no shared component and under a 0.124 share, in the same way we simulated rule one, and report them beside the rule.
- Fix: Replace "the difference is positive" with the committed definition, and add one sentence with the simulated branch probabilities.
- Status: NEEDS-EXPERIMENT. Extend research/outputs/snap-r1-power (r1_power.py) with a bank-two half at one sixth the items and report pass/support/undecided rates at zero and 0.124 shared-item share; CPU-feasible, pure simulation.

#### R1-19 | D | major | lowers score: yes | FIX-TEXT
- Sources: KA5, AR10, AR question 6.
- Quote: "At a true value of 1.244 it passes in 0.356 of 4,000 replicates, and at independence in 0.026, which means the rule can confirm the effect in this family but a failure can't count against it." (main.tex:213)
- Objection: A confirmatory rule with 36% power whose failure can't count against the effect gives the replication no way to hurt the paper.
- Rebuttal: The design was fixed by the released runs, since nine seeds at five sizes is all PolyPythias offers, and we kept the rule as committed rather than changing it after the simulation. The simulated middle 90% of estimates at a true 1.244 runs from 1.026 to 1.456, so readers can judge the pass region before seeing the result, and an estimate below that range would count against transfer.
- Fix: Replace "which means the rule can confirm the effect in this family but a failure can't count against it" with "and at a true 1.244 the middle 90% of estimates runs from 1.026 to 1.456 (research/outputs/snap-r1-power/RESULT.txt), so a pass confirms the effect in this family, a failure with a point estimate inside that range bounds it, and an estimate below 1.026 would count against transfer", labelling the last clause as added after the rule was fixed.
- Status: FIX-TEXT.

#### R1-20 | D | major | lowers score: yes | NEEDS-EXPERIMENT
- Sources: AR demanded experiment 3, AR question 3 (supports R1-03, R1-04).
- Quote: "At each size below 1B we called a pair of recipes when their aggregate gap exceeded two standard errors, computed either under independence or with the estimated covariance, leaving the pair out of both estimates." (main.tex:236)
- Objection: Without a comparison whose runs don't share seeds, the paper can't show any concrete situation where ignoring covariance leads to a wrong call.
- Rebuttal: We repeated the decision analysis with seed-mismatched pairs from the same saved scores, which isolates the case the 0.113 simulation describes.
- Fix: Add one sentence to Sec 4.5 with the unpaired result once it exists, and until then keep the seed-label explanation in R1-03/R1-04 worded as an explanation.
- Status: NEEDS-EXPERIMENT. Rerun compute extra/heldout/outputs/k05-decision logic with seed-mismatched recipe pairs (for example seed 2 against seed 14) on saved per-item scores; CPU-feasible.

#### R1-21 | E | major | lowers score: yes | FIX-TEXT
- Sources: AR21, AR14, AR1 (siblings R1-03, R1-04).
- Quote: "Our estimated ratio is therefore a measurement of this battery and helps only where replicates are missing and the target battery's own ratio is close." (main.tex:275)
- Objection: The recommendation needs the replicates most users lack, and the paper gives no default for a user without them.
- Rebuttal: With replicates, the replicate standard deviation of the battery average is the right quantity and needs no model; without them, an independence standard error scaled by a within-format correlation estimate is the fallback, flagged as untested outside this battery. Paired seed-matched comparisons need little correction, as Sec 4.5 shows.
- Fix: After the quoted sentence add "Without replicates, scaling the independence standard error by the format fit of Section 4.4 is a fallback we haven't tested outside this battery, and seed-matched paired comparisons need little correction, since their paired-difference ratio has median 1.024." At l.273 add a clause tying the shared seed label to that pairing.
- Status: FIX-TEXT.

#### R1-22 | A | major | lowers score: yes | FIX-TEXT
- Sources: AR5.
- Quote: "These two scales respond differently to changes in confidence." (main.tex:37)
- Objection: Accuracy is what most papers report, and there the result is only a bound, so the effect seems to exist on a scale nobody uses.
- Rebuttal: Margins carry more seed signal than accuracy on the same items, with per-benchmark reliability averaging 0.652 against 0.324, and accuracy thresholds the margin at zero, so the margin covariance is the one the data can measure and accuracy inherits it at lower resolution.
- Fix: Extend the sentence with "and margins carry more seed signal, with per-benchmark reliability averaging 0.652 against 0.324 for accuracy (Section~\ref{sec:composition}), so we treat margins as the primary scale and read accuracy as a bound." Don't cite magnusson2025 for this, since the audit didn't verify that use.
- Status: FIX-TEXT.

#### R1-23 | E | major | lowers score: yes | FIX-TEXT
- Sources: AR16, PA20, CI2 (sibling R1-43 in APP).
- Quote: "Among the studies we located, we find none that estimates the covariance of run noise between benchmarks or an effective benchmark count from that covariance." (main.tex:262)
- Objection: Miller (2024) on clustered and paired error bars and the run-resampling work of Henderson and Agarwal appear only in Appendix B, and the paper doesn't say its novelty is the estimand and measurement rather than a new statistical method.
- Rebuttal: Miller treats item-sampling uncertainty with clustered and paired standard errors and takes run variance as fixed, and Henderson and Agarwal resample runs within one task, whereas we preserve paired run effects across benchmarks. The estimator adapts the classical split-half construction, and the contribution is the estimand, its calibration and the measurement.
- Fix: Before the quoted sentence add "\citet{miller2024} gives clustered and paired item-sampling errors for evaluations while treating run variance as fixed, and \citet{henderson2018} and \citet{agarwal2021} resample runs within tasks, whereas we must preserve paired run effects across benchmarks." Replace "Among the studies we located, we find none" with "We know of no study".
- Status: FIX-TEXT.

#### R1-24 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: citation_audit verified missing work 1.
- Quote: "\citet{reimers2017}, \citet{zhou2020}, and \citet{madaan2024} study seed-related evaluation variability" (main.tex:262).
- Objection: The paper omits Fehlauer, Mahowald and Pimentel (EMNLP 2025, https://arxiv.org/abs/2509.26643), recent work on LM pretraining seed variability, the same object SNAP studies.
- Rebuttal: Fehlauer et al. study how language models trained from different seeds converge and diverge, while we measure how run deviations covary across benchmarks at a fixed checkpoint.
- Fix: Add \citet{fehlauer2025} to the quoted list with a references.tex entry built from the arXiv record.
- Status: FIX-TEXT.

#### R1-25 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: citation_audit verified missing work 5 and 6.
- Quote: "whereas we apply covariance accounting across benchmarks within a replicate run" (main.tex:262).
- Objection: A reviewer will say benchmarks are already known to correlate through a low-dimensional capability structure (Ruan, Maddison and Hashimoto, NeurIPS 2024, https://arxiv.org/abs/2405.10938; Burnell et al. 2023, https://arxiv.org/abs/2306.10062), so the covariance is unsurprising.
- Rebuttal: Those studies measure correlation of scores between different models, which reflects shared capability, while SNAP measures covariance of run deviations within one configuration, where capability is held fixed; the two can differ in sign and size.
- Fix: Add one sentence to Related work: "Across models, benchmark scores share a low-dimensional capability structure \citep{ruan2024,burnell2023revealing}, whereas we measure covariance of run deviations with the configuration held fixed." Add both bib entries from the arXiv records.
- Status: FIX-TEXT.

#### R1-26 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: citation_audit positioning note (jordan2024).
- Quote: "\citet{jordan2024} separates example-specific training variance from distribution-level variation and compares accuracies across related evaluation sets." (main.tex:262)
- Objection: Jordan (2024, App. C) finds near-independent run deviations across five ImageNet evaluation sets, the nearest published measurement, and the paper doesn't say why its margin result differs.
- Rebuttal: Jordan measures accuracy of vision classifiers on distribution-shifted versions of one task, while we measure per-byte margins on language benchmarks, and our own accuracy interval includes one, which agrees with Jordan's direction on accuracy.
- Fix: Append "and finds near-independence across ImageNet evaluation sets on accuracy, which matches our accuracy interval, while our margin covariance sits within scoring formats."
- Status: FIX-TEXT.

#### R1-27 | E | major | lowers score: yes | FIX-TEXT
- Sources: AR15, AR demanded experiments 5 and 6.
- Quote: "We analyse 37,682 items per run across 25 recipes at 150M, 300M, 530M, 750M, and 1B parameters" (main.tex:129).
- Objection: Scale stops at 1B (410M for PolyPythias) and every task is multiple-choice log-likelihood, so the result may not hold for generative, exact-match or larger models.
- Rebuttal: No public multi-seed pretraining population above 1B releases per-item replicate scores, as Appendix B.6 documents for Pythia, OLMo-2 and MultiBERTs, and generative tasks lack an answer-likelihood margin, so the format result is scoped to likelihood-scored multiple choice.
- Fix: Add one sentence to the Discussion: "Our populations stop at 1B and use likelihood-scored multiple choice, because no public multi-seed population above that size releases replicate item scores (Appendix~\ref{app:design}), and generative tasks lack the margin our primary scale uses."
- Status: FIX-TEXT. A generative-task or larger-model run would need GPU and is out of scope.

#### R1-28 | A | moderate | lowers score: yes | FIX-TEXT
- Sources: PA6 (siblings R1-29 in C, R1-30 in E).
- Quote: "which includes one and bounds accuracy inflation at 1.157 in the primary analysis" (main.tex:39).
- Objection: Calling a CI endpoint a bound reads stronger than the evidence, since the adjacent checkpoint excludes one.
- Rebuttal: The 1.157 is the upper 95% limit at the scored checkpoint, and the text now says so.
- Fix: Replace with "which includes one, with an upper 95% limit of 1.157 at the scored checkpoint".
- Status: FIX-TEXT.

#### R1-29 | C | moderate | lowers score: yes | FIX-TEXT
- Sources: PA6 (siblings R1-28, R1-30).
- Quote: "That upper endpoint maps under the stated measurement model and fixed battery to $\bar r_E<0.038$ and $K_{\mathrm{eff}}>7.47$." (main.tex:146)
- Objection: Strict inequalities derived from a confidence limit read as proven bounds.
- Rebuttal: The two values are the upper interval limit restated on other scales, and the revision labels them that way.
- Fix: Rewrite as "At that upper limit the effective coefficient is 0.038 and $K_{\mathrm{eff}}$ is 7.47", or cut the sentence to save space.
- Status: FIX-TEXT.

#### R1-30 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: PA6 (siblings R1-28, R1-29).
- Quote: "so the primary analysis gives a bound of 1.157" (main.tex:269).
- Objection: Same overstatement as R1-28, repeated in the Discussion.
- Rebuttal: As in R1-28.
- Fix: Replace with "so the primary analysis gives an upper limit of 1.157 at the scored checkpoint".
- Status: FIX-TEXT.

#### R1-31 | D | moderate | lowers score: yes | FIX-TEXT
- Sources: CA2, CA3.
- Quote: "A practitioner could therefore approximate inflation for a new battery from its formats and seed variances, a use we haven't tested on any other battery." and "With equal variances the same correlations would give 1.803, and the gap comes from BoolQ" (main.tex:226).
- Objection: "Therefore" rests on an in-sample fit that overstates inflation in nine of ten deletions, and BoolQ explains about 74% of the equal-variance gap, not all of it.
- Rebuttal: The leave-one-out predictions fall within 0.054 but mostly overstate, so the format fit is a rough upper guide, and the gap sentence now says most of it comes from BoolQ.
- Fix: Replace "A practitioner could therefore approximate" with "The fit overstates inflation in nine of ten deletions, so a practitioner could at most approximate", and replace "and the gap comes from BoolQ" with "and most of the gap comes from BoolQ over the nine defined traits".
- Status: FIX-TEXT.

#### R1-32 | D | moderate | lowers score: yes | FIX-TEXT
- Sources: PA11, CA6.
- Quote: "PolyPythias gives margin inflation of 1.406 on the three planned sizes and 1.262 with interval \ci{0.927}{1.537} on a five-size rescore" (main.tex:228).
- Objection: An older set of PolyPythias numbers competes with the pre-specified Sec 4.3 result on the same runs, and 1.406 comes from a different pipeline than 1.262 with no result file behind it.
- Rebuttal: These are the earlier nested-sample transfer checks, superseded by the full-battery scoring in Sec 4.3, and they now sit in Appendix `app:transport` with their pipeline named.
- Fix: Move the sentence to `app:transport` (cut C4) and use 1.414 from research/outputs/snap-r12-analysis/r12_analysis.json for the three-size value, or label 1.406 as "the original pipeline".
- Status: FIX-TEXT.

#### R1-33 | D | moderate | lowers score: yes | FIX-TEXT
- Sources: AR19, PA10 (sibling R1-34 in E).
- Quote: "our shipped competence proxy is degenerate, with WinoGrande supplying more than 99.99\% of its squared standardised inputs" (main.tex:226).
- Objection: Reporting a degenerate proxy in the main text signals unfinished analysis.
- Rebuttal: The proxy analyses are exploratory and none enters a conclusion, and the revision keeps them in Appendix `app:proxy` with a one-line pointer.
- Fix: Cut from "Gain adjustment doesn't reduce margin inflation" to the end of the paragraph and replace with "Gain and competence adjustments don't support a mechanistic reading (Appendix~\ref{app:proxy})."
- Status: FIX-TEXT.

#### R1-34 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: PA10 (sibling R1-33).
- Quote: "since repaired margin proxies fall below one even in simulations without a separate competence variable, apart from the clipped-drop weighting at 0.889 against a simulated fifth percentile of 0.908." (main.tex:271)
- Objection: "Repaired margin proxies" and "clipped-drop weighting" are undefined in the main text.
- Rebuttal: The terms are defined in Appendix `app:proxy`, where the sentence now sits.
- Fix: Move the sentence starting "We make no claim about that mechanism" to `app:proxy` (cut C9).
- Status: FIX-TEXT.

#### R1-35 | A | moderate | lowers score: yes | FIX-TEXT
- Sources: PA7, KA13, AR17.
- Quote: "call it SNAP, Seed Noise Across Phenotypes, where phenotype names the score we call a trait. We keep the name though the released runs differ in checkpoint step, training budget and seed." (main.tex:35)
- Objection: The genetics vocabulary costs ML readers effort, and the paper concedes the name doesn't fit, which invites the checkpoint attack.
- Rebuttal: The name follows the quantitative-genetics construction the estimator adapts, and the main text now uses "benchmark score" and keeps the analogy in Appendix A.1.
- Fix: Delete "We keep the name though the released runs differ in checkpoint step, training budget and seed." and replace "where phenotype names the score we call a trait" with "after the quantitative-genetics construction (Appendix A.1)"; use one term for the factor ("inflation factor $\Lambda$") throughout.
- Status: FIX-TEXT.

#### R1-36 | B | moderate | lowers score: yes | FIX-TEXT
- Sources: PA9.
- Quote: "However, we can't sustain that interpretation in full, because training schedules differ within the actual population." (main.tex:67)
- Objection: The model definition weakens itself before stating its assumptions.
- Rebuttal: The schedule caveat belongs with the checkpoint analysis in Sec 3, which covers it in full.
- Fix: Replace with "Section 3 describes where the released runs depart from this assumption."
- Status: FIX-TEXT.

#### R1-37 | B | moderate | lowers score: yes | FIX-TEXT
- Sources: PA8, AR7 (siblings R1-10, R1-38).
- Quote: "The plan also has neither a supplied original file nor an independently corroborated date." (main.tex:135) and "and like the protocol's, that commit time isn't independently corroborated." (main.tex:141)
- Objection: The provenance caveat recurs in many places, which makes the paper argue against itself.
- Rebuttal: The revision states provenance once in the limitations.
- Fix: Delete both clauses and move the l.135 enumeration sentence to Appendix B (cut C14), keeping the first sentence of l.135.
- Status: FIX-TEXT.

#### R1-38 | E | moderate | lowers score: yes | FIX-TEXT
- Sources: PA8 (siblings R1-10, R1-37).
- Quote: "The original analysis plan lacks an independently corroborated timestamp." and "The protocol's commit times aren't corroborated by an independent source." (main.tex:285)
- Objection: The Reproducibility statement repeats the same caveat twice.
- Rebuttal: One provenance sentence remains.
- Fix: Merge into one sentence: "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp, and the plan's screening split was never formed."
- Status: FIX-TEXT.

#### R1-39 | C | moderate | lowers score: yes | FIX-TEXT
- Sources: KA11, AR14.
- Quote: "the release shares one seed label across every recipe inside a size band" (main.tex:273).
- Objection: Recipe-cluster intervals assume independence that shared seed labels can break, and the permutation check has power 0.490.
- Rebuttal: Clustering on the five size bands instead gives a margin interval of 1.030 to 1.426, which still excludes one, and the table now shows it.
- Fix: Add a row "Margin, size-band clusters, 1.244, \ci{1.030}{1.426}" and the accuracy row \ci{0.961}{1.184} to Table 1, which also lets l.126 lose its last sentence.
- Status: FIX-TEXT.

#### R1-40 | A | minor | lowers score: no | FIX-TEXT
- Sources: CA12 (sibling R1-41).
- Quote: "returns the simulated false-positive rate from 0.113 to 0.051 and leaves 0.101 at a battery whose own ratio is 1.5" (main.tex:49).
- Objection: 0.101 comes from a separate transfer simulation whose matched baseline is 0.117/0.052, but the sentence reads as one simulation.
- Rebuttal: The sentence now names the second simulation.
- Fix: Write "and in a separate transfer simulation leaves 0.101 at a battery whose own ratio is 1.5".
- Status: FIX-TEXT.

#### R1-41 | E | minor | lowers score: no | FIX-TEXT
- Sources: CA12 (sibling R1-40).
- Quote: "carried to a battery whose own ratio is 1.5, that scaling leaves the error at 0.101" (main.tex:275).
- Objection: Same merge of two simulations as R1-40.
- Rebuttal: As in R1-40.
- Fix: Write "in a separate transfer simulation carried to a battery whose own ratio is 1.5".
- Status: FIX-TEXT.

#### R1-42 | APP | moderate | lowers score: no | FIX-TEXT
- Sources: CI1.
- Quote: "The Spearman matrix of \citet[Figure 3]{zhou2020} averages checkpoints across seeds, mixing checkpoint progress with seed deviations." (appendices_bcd.tex:73)
- Objection: Zhou et al. average per-seed Spearman correlations computed over each seed's checkpoints, so no seed deviations enter the statistic and "mixing" misreads it.
- Rebuttal: We corrected the description: their Figure 3 measures co-movement along a training trajectory, a different quantity from covariance of seed deviations at a fixed step.
- Fix: Replace with "The Spearman matrix of \citet[Figure 3]{zhou2020} averages per-seed correlations computed over training checkpoints, which measures co-movement along a trajectory rather than covariance of seed deviations at a fixed step."
- Status: FIX-TEXT.

#### R1-43 | APP | minor | lowers score: no | FIX-TEXT
- Sources: CI2 (sibling R1-23).
- Quote: "\citet{dufour2026}, \citet{miller2024}, and \citet{zhao2026} address training versus sampling variation, item-level uncertainty for one model, and per-task tests without cross-task covariance." (appendices_bcd.tex:73)
- Objection: Miller also covers paired two-model comparisons and clustered errors, so "for one model" understates it.
- Rebuttal: The description now covers the clustered and paired cases.
- Fix: Replace "item-level uncertainty for one model" with "item-sampling uncertainty with clustered and paired two-model comparisons, treating run variance as fixed".
- Status: FIX-TEXT.

#### R1-44 | C | minor | lowers score: no | FIX-TEXT
- Sources: PA15, KA12.
- Quote: "The accuracy correlation estimate also contains an entry of 1.296 and an eigenvalue of $-0.55$, and thus it isn't a valid correlation matrix without further regularisation." (main.tex:165)
- Objection: An invalid correlation matrix in the headline subsection raises stability doubts the headline doesn't need.
- Rebuttal: No headline quantity uses the correlation matrix, since the factor uses covariance products directly, and the diagnostic now sits in the appendix.
- Fix: Move the l.165 paragraph from "Per-benchmark reliability" onward to Appendix B "Reliability by trait" (cut C11), keeping the 0.652/0.324 reliability means if R1-22 cites them.
- Status: FIX-TEXT.

#### R1-45 | A | minor | lowers score: no | FIX-TEXT
- Sources: KA15.
- Quote: "which fails a rule fixed before scoring at a design with 40 within-size contrasts." (abstract R1-fail branch, main.tex:29)
- Objection: If rule one fails, the abstract drops the rule-two result, which still decides the identification question.
- Rebuttal: Both abstract branches now report rule two.
- Fix: Append to the R1-fail branch the matching R2 clause from the R1-pass branch ("and pairing that battery with a disjoint item bank \outcome{...}").
- Status: FIX-TEXT.

#### R1-46 | C | minor | lowers score: no | FIX-TEXT
- Sources: CA8.
- Quote: "the rule passes in 0.926 of replicates at a true 1.244 under margin-like item noise and in 0.524 under accuracy-like noise" (main.tex:207).
- Objection: The files give 0.9265 and 0.5245, which round half-up to 0.927 and 0.525.
- Rebuttal: Corrected.
- Fix: Write 0.927 and 0.525 (compute extra/heldout/outputs/k12-rule-power-n073 and -n145), or move the sentence to `app:heldout` with R1-11.
- Status: FIX-TEXT.

#### R1-47 | D | minor | lowers score: no | FIX-TEXT
- Sources: CA5.
- Quote: "drawing seed effects from the DataDecide margin covariance and item noise from the observed reliabilities" (main.tex:213).
- Objection: The wording omits that the covariance was clipped to positive semidefinite and WinoGrande's reliability set to 0.5, and doesn't name which family's reliabilities were used.
- Rebuttal: The two simulation choices are now stated.
- Fix: Write "item noise from the DataDecide margin reliabilities, with WinoGrande's set to 0.5 and the covariance clipped to positive semidefinite".
- Status: FIX-TEXT.

#### R1-48 | B | minor | lowers score: no | FIX-TEXT
- Sources: CA4.
- Quote: "A residual-scaled wild interval covers 0.943 to 0.958 there" (main.tex:126).
- Objection: The appendix gives that coverage at 4,000 replicates, not the 10,000-replicate repeat that "there" points to.
- Rebuttal: Corrected.
- Fix: Replace "there" with "at 4,000 replicates", or drop with cut C6.
- Status: FIX-TEXT.

#### R1-49 | B | minor | lowers score: no | NEEDS-EXPERIMENT
- Sources: CA9, CA10.
- Quote: "we built a second bank of 6,808 items" (main.tex:141) and "an enumeration over the $\binom{25}{17}=1{,}081{,}575$ possible estimation sets produces margin estimates from 1.037 to 1.317 and accuracy estimates from 0.963 to 1.191" (main.tex:135).
- Objection: Neither the bank-two item count nor the enumeration range has a result file in the repo.
- Rebuttal: Both now ship with the artifact: the bank-two manifest with per-benchmark counts, and the enumeration rerun on the current pipeline.
- Fix: None until the files exist; if the rerun range differs, update l.135, or label it "from the earlier pipeline".
- Status: NEEDS-EXPERIMENT. Write the bank-two manifest from the frozen request file and rerun the 1,081,575-set enumeration; both CPU-feasible from saved outputs.

#### R1-50 | D | minor | lowers score: no | NEEDS-EXPERIMENT
- Sources: CA11.
- Quote: "Cross-format off-diagonal covariance alone gives diagnostic inflation of 0.921 with interval \ci{0.801}{1.035}" (main.tex:226).
- Objection: The point value recomputes from the matrices, but the interval has no result file.
- Rebuttal: The masked-matrix interval output now ships with the artifact.
- Fix: None until the file exists.
- Status: NEEDS-EXPERIMENT. Rerun the masked-matrix bootstrap and save its JSON; CPU-feasible from saved per-item reductions.

#### R1-51 | D | minor | lowers score: no | FIX-TEXT
- Sources: PA14.
- Quote: "lower mean squared error of log aggregate standard deviation by about 0.03 from the 0.0358 of independence" with "(Table~\ref{tab:prediction})" (main.tex:232).
- Objection: The main text cites an appendix table as if it were in the body.
- Rebuttal: Corrected.
- Fix: Write "Table~\ref{tab:prediction} in Appendix~\ref{app:supplementary}" at l.232 (and at l.264 if R1-53 keeps the reference).
- Status: FIX-TEXT.

#### R1-52 | C | minor | lowers score: no | FIX-TEXT
- Sources: PA17.
- Quote: "from the trait-removal table of the extended supplement" (Figure 1 caption, main.tex:176).
- Objection: Reviewers can't easily open the extended supplement.
- Rebuttal: The caption now points to an appendix table.
- Fix: Replace with "from the removal table in Appendix~\ref{app:composition}".
- Status: FIX-TEXT.

#### R1-53 | E | minor | lowers score: no | FIX-TEXT
- Sources: PA19, CI6.
- Quote: "\citet{cheverud1988} motivates our phenotypic plug-in comparison (Table~\ref{tab:prediction}), and that comparison fails here on the transfer of correlation structure." and "Our cross-half construction follows repeated-measurement and variance-component ideas from \citet{spearman1904}, \citet{cronbach1951}, and \citet{searle1992}." (main.tex:264)
- Objection: Related work reports a result, and the split-half construction is usually credited to Spearman (1910) and Brown (1910), both already in the bibliography.
- Rebuttal: Corrected.
- Fix: End the Cheverud sentence at "plug-in comparison", and add \citet{spearman1910,brown1910} for the split-half construction.
- Status: FIX-TEXT.

#### R1-54 | APP | minor | lowers score: no | FIX-TEXT
- Sources: CI3, CI4, CI5, CI6.
- Quote: "The OLMo-2 checkpoints considered here lack replicates at matched steps \citep{teamolmo2025}." (appendices_bcd.tex:70); "The bootstrap-t addresses concerns associated with few-cluster approximations, as discussed by \citet{bell2002}" (:213); "\citet{hardy2026}, \citet{kohli2026}, \citet{messing2026}, and \citet{sha2026} measure dependence across models, judges, or prompts" (:75); "The cross-half identity follows \citet{spearman1904}" (:77).
- Objection: OLMo 2 has midtraining soup ingredients that differ only in data order; Bell and McCaffrey don't cover the bootstrap-t; Messing decomposes variance rather than measuring dependence; the split-half credit is loose.
- Rebuttal: Each description is corrected to match the cited source.
- Fix: (:70) "lack pretraining-seed replicates, since the midtraining soup ingredients share one stage-1 checkpoint and vary only data order"; (:213) "few-cluster bias in sandwich variances \citep{bell2002} motivates the bootstrap-t \citep{cameron2008}"; (:75) "measure dependence across models or judges, or variance from prompt and judge choice \citep{messing2026}"; (:77) add \citet{spearman1910,brown1910}.
- Status: FIX-TEXT.

#### R1-55 | E | minor | lowers score: no | FIX-TEXT
- Sources: citation_audit FIX verdicts (sellam2022, zhao2026).
- Quote: "Thibault Sellam, Steve Yadlowsky, Ian Tenney, Jason Wei," (references.tex:139) and "Most transformer modifications still do not transfer at 1--3b" (references.tex:157).
- Objection: Sellam et al. list Tenney eleventh, not third, and the zhao2026 title renders "1-3B" as "1--3b".
- Rebuttal: Corrected against arXiv 2106.16163 and 2605.20798.
- Fix: Reorder to Sellam, Yadlowsky, Wei, Saphra, D'Amour, Linzen, Bastings, Turc, Eisenstein, Das, Tenney, Pavlick; write "at 1--3{B}" so the capital survives.
- Status: FIX-TEXT.

#### R1-56 | B | minor | lowers score: no | FIX-TEXT
- Sources: PA18.
- Quote: "y^H_{crj}=\mu^H_{cj}+E_{crj}+\varepsilon^H_{crj}." (main.tex:65)
- Objection: The only numbered equation without a label, while `eq:effective` and `eq:information` are never cited.
- Rebuttal: Tidied.
- Fix: Add `\label{eq:model}` or use `equation*`, and drop the two unused labels (eq:information moves out with cut C7).
- Status: FIX-TEXT.

#### R1-57 | B | minor | lowers score: no | FIX-TEXT
- Sources: AR13.
- Quote: "one recipe holding 0.520 of the squared influence, and removing that recipe moves the estimate by 0.037" (main.tex:126).
- Objection: The recipe that carries half the squared influence goes unnamed.
- Rebuttal: The recipe is now named.
- Fix: Insert the recipe name from research/outputs/snap-r6-influence/r6_influence.json after "one recipe".
- Status: FIX-TEXT.

#### R1-58 | E | minor | lowers score: no | REJECT
- Sources: citation_audit verified missing work 2, 3, 4, 7, 8, 9, 10.
- Quote: "Our few-cluster inference follows the concerns studied by \citet{cameron2008} and \citet{mackinnon2017}." (main.tex:266)
- Objection: The paper could cite Bowyer et al. 2025, Biderman et al. 2024, Zhang and Hardt 2024, Ilić and Gignac, Perlitz et al. 2024, Summers and Dinneen 2021, Polo et al. 2024, Gu et al. 2025 and Sclar et al. 2024 (arXiv links in citation_audit.md).
- Rebuttal: None needed in advance.
- Fix: None.
- Status: REJECT. None of these answers an objection the paper leaves open: the intervals are calibrated by simulation at 25 clusters (Bowyer's small-sample concern), bouthillier2021 already covers source decomposition (Summers and Dinneen), and the rest concern cross-model structure or prompt sensitivity already covered by R1-25 and messing2026, so adding them costs page budget for no score gain.

#### R1-59 | APP | minor | lowers score: no | REJECT
- Sources: PA script gate (check_references.py).
- Quote: "Table~\ref{tab:notation} in Appendix~\ref{app:derivations}" (main.tex:54), flagged with `app:design`, `app:supplementary`, `S-#1` and others.
- Objection: The script reports undefined references.
- Rebuttal: None needed.
- Fix: None.
- Status: REJECT. The script reads main.tex alone while the labels live in the `\input` appendix files or come through `xr`, and main.log has 0 "undefined" warnings.

#### R1-60 | A | minor | lowers score: no | REJECT
- Sources: PA script gate (anonymity check).
- Quote: "\author{Anonymous authors}" (main.tex:15).
- Objection: The script flags anonymity.
- Rebuttal: None needed.
- Fix: None.
- Status: REJECT. The author block is anonymous and `pdfauthor={}` (main.tex:13).

#### R1-61 | B | minor | lowers score: no | REJECT
- Sources: PA script gate (acronym check).
- Quote: "DataDecide supplies the ten benchmarks ARC-Challenge, ARC-Easy, BoolQ, CommonsenseQA, HellaSwag, MMLU, OpenBookQA, PIQA, Social IQa, and WinoGrande." (main.tex:129)
- Objection: The script flags undefined acronyms.
- Rebuttal: None needed.
- Fix: None.
- Status: REJECT. The flagged strings are benchmark names and a GPU model (PIQA, MMLU, RTX), which are proper names.

#### R1-62 | E | minor | lowers score: no | REJECT
- Sources: PA script gate (L1 `~\cite`).
- Quote: "\citet{bouthillier2021} derive variance inflation" (main.tex:262).
- Objection: The script asks for a non-breaking space before citations.
- Rebuttal: None needed.
- Fix: None.
- Status: REJECT. The flagged cites are `\citet` used as sentence subjects, where a tie is wrong.

#### R1-63 | C | minor | lowers score: no | REJECT
- Sources: AR demanded experiment 4.
- Quote: "Our GPU budget couldn't cover all 375 released checkpoints, and our protocol's scope rule limited the test to those runs at the steps of the primary analysis." (main.tex:185)
- Objection: The held-out test should run at all five sizes and 375 runs, since the registered scope was set by GPU budget and failed on width.
- Rebuttal: Extending a failed registered test to a larger scope after seeing its result is the forking path the registration exists to prevent, so the registered verdict stands at its registered scope.
- Fix: None.
- Status: REJECT. A wider rerun can't change the registered verdict and would need GPU, which this loop excludes.

### Round 1 outcome (2026-09-23 01:05 EDT)

Status per finding is in work/rebuttal/r1/status_{A,B,C,D,E,APP,PAGE}.md. Totals: 50 FIXED, 6 NEEDS-EXPERIMENT, 6 REJECTED, plus R1-01 PAGE FIXED (maintext:end on page 9 for all six outcome combinations, 0 undefined references, verified by recompile).

New findings rated likely to lower the score this round: yes (round 1 is the baseline).

Open NEEDS-EXPERIMENT:
- R1-08: NEEDS-EXPERIMENT. The fixed-bank inflation value (replicate SD of the full-bank battery average against independence, margins and accuracy, from released per-item scores) needs a CPU Kaggle kernel. The text part is done: Sec 2.1 now says the target transfers to a redrawn or extended bank and that item-specific run deviations on the released bank belong to the separate fixed-bank question (pointer to app:derivations).
- R1-49: NEEDS-EXPERIMENT. The bank-two manifest (6,808 items, per-benchmark counts) and the 1,081,575-set enumeration rerun both need result files, which means a CPU job on saved outputs. Text unchanged.
- R1-18: NEEDS-EXPERIMENT (CPU). Text part done ("positive" now reads "that difference interval lies above zero", matching verdicts()). Still needed: extend research/outputs/snap-r1-power (r1_power.py) with a bank-two half at one sixth the items and report not-supported/supported/undecided rates at zero and 0.124 shared-item share.
- R1-20: NEEDS-EXPERIMENT (CPU). Seed-mismatched recipe-pair rerun of the k05-decision logic on saved per-item scores; the R1-04 sentence stays hedged until it exists.
- R1-50: NEEDS-EXPERIMENT (CPU). Masked-matrix bootstrap JSON for the 0.801 to 1.035 interval; no text change.
- R1-06 NEEDS-EXPERIMENT: scoring the 375 DataDecide runs on the 6,808-item second bank needs GPU inference, and the limitation sentence stays unchanged in the Discussion.

CPU-feasible (queue as Kaggle CPU kernels next round, enable_gpu false): R1-08, R1-18, R1-20, R1-49, R1-50. GPU-only, stays open: R1-06.
Carry-over for APP next round: supplement_extended_body.tex l.716 prints 0.926 where the results file gives 0.9265.

Skills also applied in fix phase: stop-slop (every section fixer), superpowers:verification-before-completion (coordinator recompiled all six combos before claiming page 9).

## Round 2, started 2026-09-23 01:32 EDT

Pre-round snapshot: e33a01d. Skills run: superpowers:using-superpowers, aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), stop-slop, superpowers:verification-before-completion; Kaggle CPU kernels for the round 1 CPU-feasible NEEDS-EXPERIMENT items. Raw outputs: work/rebuttal/r2/*.md

### Merged findings (round 2)

Merged 2026-09-23 from work/rebuttal/r2/{kill_argument (KA), claim_audit (CA), citation_audit (CI), paper_audit (PA), academic_reviewer (AR, seats S1 to S5)}.md. Every quote was checked against deliverables/*.tex at e33a01d. Four round-1 CPU kernels landed under results/ before this merge (snap-r2-r1-08, -r1-18, -r1-18b, -r1-20, -r1-50), and three of them change dispositions: R1-08 (fixed-bank inflation) and R1-18 (rule-two operating characteristics) make R2-12 and R2-05 text-fixable, while R1-20 (seed-mismatched pairs) and R1-18b (committed jackknife) contradict text the paper now prints (R2-07, R2-08, R2-06). Slices: A main.tex 28-49 (abstract and introduction, title at line 14), B 50-136 (Sections 2 and 3), C 137-204 (Section 4 up to sec:family), D 205-247 (sec:family through \label{maintext:end}, plus the statements at 248-255 for R2-39 only), APP appendix_a.tex, appendices_bcd.tex, references.tex, and for R2-41 supplement_extended_body.tex. Fix sketches are in work/rebuttal/r2/FIXER_BRIEF.md.

| id | severity | sources | NEW/REPEAT | likely-lower | disposition | slice |
|---|---|---|---|---|---|---|
| R2-01 | critical | KA1+AR3+PA10+S5 | REPEAT R1-05 (residual) | yes | text-fixable | B |
| R2-02 | critical | KA1 | REPEAT R1-05 (residual) | yes | NEEDS-EXPERIMENT (CPU) | none |
| R2-03 | major | AR5 | REPEAT R1-17 (fix failed) | yes | text-fixable | A |
| R2-04 | major | AR5+results/snap-r2-r1-18 | REPEAT R1-17 (fix failed) | yes | text-fixable | D |
| R2-05 | major | AR4+KA3+PA19+S2+AR Q3,Q4 | REPEAT R1-18, R1-19 (residual) | yes | text-fixable | D |
| R2-06 | major | results/snap-r2-r1-18b (merge check) | NEW | no | text-fixable | D |
| R2-07 | major | KA2+PA2+AR14+S3+results/snap-r2-r1-20 | REPEAT R1-03 (fix failed) | yes | text-fixable | A |
| R2-08 | major | KA2+S3+results/snap-r2-r1-20 | REPEAT R1-04, R1-21 (fix failed) | yes | text-fixable | D |
| R2-09 | major | KA5+PA1+AR1+CA9+PA15 | REPEAT R1-04 (residual) | yes | text-fixable | D |
| R2-10 | major | KA4+PA6+AR6+AR8+S1 | REPEAT R1-07, R1-02 (fix failed) | yes | text-fixable | A |
| R2-11 | major | PA8+PA5+S1 | REPEAT R1-10, R1-12 (fix failed) | yes | text-fixable | A |
| R2-12 | major | AR2+S3+AR Q1+results/snap-r2-r1-08 | REPEAT R1-08 (residual, now fixable) | yes | text-fixable | B |
| R2-13 | major | AR7+S4+AR Q2 | NEW | yes | text-fixable | B |
| R2-14 | major | KA P4+AR exp 1 | REPEAT R1-06 (open) | yes | NEEDS-EXPERIMENT (GPU) | none |
| R2-15 | major | CA1 | REPEAT R1-49 (residual) | no | NEEDS-EXPERIMENT (outputs must land; manifest CPU) | none |
| R2-16 | major | AR9 | REPEAT R1-01 | no | REJECTED | none |
| R2-17 | moderate | AR10+KA3+CA2 | REPEAT R1-37, R1-49 (residual) | yes | text-fixable | B |
| R2-18 | moderate | PA7+KA7+CA8 | NEW | no | text-fixable | A |
| R2-19 | moderate | CA6+PA4 | NEW | no | text-fixable | C |
| R2-20 | moderate | CA3 | NEW | no | text-fixable | C |
| R2-21 | moderate | PA9 | NEW | no | text-fixable | C |
| R2-22 | moderate | PA5+PA13 | NEW | no | text-fixable | D |
| R2-23 | moderate | PA3 | NEW | no | text-fixable | D |
| R2-24 | moderate | CI3+AR7 | REPEAT R1-53 (residual) | no | text-fixable | D |
| R2-25 | moderate | CI1 | NEW | no | text-fixable | APP |
| R2-26 | moderate | AR Q2+AR exp 2 | NEW | no | NEEDS-EXPERIMENT (CPU) | none |
| R2-27 | minor | CA7 | NEW | no | text-fixable | B |
| R2-28 | minor | CA10 | NEW | no | text-fixable | B |
| R2-29 | minor | KA6 | NEW | no | text-fixable | B |
| R2-30 | minor | PA15 | NEW | no | text-fixable | B |
| R2-31 | minor | PA14+CI4 | NEW | no | text-fixable | A |
| R2-32 | minor | PA11 | NEW | no | text-fixable | C |
| R2-33 | minor | PA17 | REPEAT R1-11 (residual) | no | text-fixable | C |
| R2-34 | minor | PA18 | NEW | no | text-fixable | C |
| R2-35 | minor | CA5+AR11 | NEW | no | text-fixable | D |
| R2-36 | minor | CA8 | NEW | no | text-fixable | D |
| R2-37 | minor | CA11 | NEW | no | text-fixable | D |
| R2-38 | minor | PA12 | NEW | no | text-fixable | D |
| R2-39 | minor | PA16 | NEW | no | text-fixable | D (statements) |
| R2-40 | minor | KA8+CA13+CA34 | NEW | no | text-fixable | APP |
| R2-41 | minor | CI2+R1 carry-over | REPEAT R1-43 (residual) | no | text-fixable | APP |
| R2-42 | minor | CI verdict notes | NEW | no | text-fixable | APP |
| R2-43 | minor | CA4 | NEW | no | NEEDS-EXPERIMENT (CPU) | none |
| R2-44 | minor | AR15 | REPEAT R1-35 | no | REJECTED | none |
| R2-45 | minor | CA12+KA3 | NEW | no | REJECTED | none |
| R2-46 | minor | AR12 | NEW | no | REJECTED | none |
| R2-47 | minor | AR13 | NEW | no | REJECTED | none |
| R2-48 | minor | PA script advisories | REPEAT R1-56, R1-62 | no | REJECTED | none |

Totals: 48 findings, critical 2, major 14, moderate 10, minor 22. Dispositions: 37 text-fixable (A 6, B 8, C 6, D 13, APP 4), 5 NEEDS-EXPERIMENT (CPU: R2-02, R2-26, R2-43; GPU: R2-14; external outputs: R2-15), 6 REJECTED.

New findings rated likely to lower the score: 1 (R2-13).

#### Finding details (statement, current quote, relation to round 1)

- R2-01. The shared-item alternative is answered only by an unshown claim, the mechanism is vague, and "diagnostic" is undefined at first use. Quote main.tex:75 "The cross-format pairs, averaging 0.007 with a diagnostic of 0.921 (Appendix~\ref{app:supplementary}), constrain a uniform component of that size and leave open one that follows scoring format." Round 1 added the example and this sentence but not the argument that centring removes any item effect constant across runs, so only a run-by-template effect can enter, and that effect recurs on any redrawn bank in the same format.
- R2-02. The calculation behind "constrain a uniform component of that size" is missing: the cross-format diagnostic that a uniform 0.124 share would induce, set against 0.921 \ci{0.801}{1.035}. Quote main.tex:75 as above. CPU kernel on the saved per-item reductions.
- R2-03. The abstract and introduction print "rejected" for an outcome whose rule only returns "not supported". Quotes main.tex:29 "with the shared-item explanation rejected" and main.tex:45 "that the shared-item explanation is \outcome{\Rtwocase}{1}{R2 not supported}{rejected}". Round 1 changed the branch paragraph but left the verdict word.
- R2-04. The rule text says the check "rejects" the explanation, and results/snap-r2-r1-18/r1_18_rule_two.json shows the not-supported branch fires at 0.226 without a shared component and 0.205 with a 0.124 share, so it can't reject anything. Quote main.tex:207 "It rejects the shared-item explanation when that cross-bank interval sits above one".
- R2-05. Neither confirmatory rule has its operating characteristics beside it: R1's power sits mid-paragraph, R2 has none, and the bound reading added after the rule was fixed reads as part of the rule. Quote main.tex:207 "At a true 1.244 it passes in 0.356 of 4,000 replicates". R1-18's kernel now supplies R2's rates.
- R2-06. The printed R1 power (0.356) and null rate (0.026) come from research/outputs/snap-r1-power/r1_power.py, whose jackknife doesn't recentre the remaining seeds, while the committed estimates.seed_jackknife does, and on the same draws the committed rule passes in 0.2585 at a true 1.244 and 0.0155 at a diagonal null (results/snap-r2-r1-18b/r1_18b_jackknife_recentring.json; results/snap-r2-r1-18 independently gives 0.257 with 0 label mismatches against the committed function). Quote main.tex:207 "At a true 1.244 it passes in 0.356 of 4,000 replicates, with the middle 90\% of estimates between 1.026 and 1.456, and at independence in 0.026." The 1.026 to 1.456 range is a point-estimate range and survives (1.0258, 1.4563).
- R2-07. Paragraph 1 closes by shrinking the stakes, and its seed-matching explanation is contradicted by results/snap-r2-r1-20, where seed-matched and seed-mismatched paired deviations differ by a factor of only 0.928 to 1.025. Quote main.tex:33 "which means the covariance matters more for one battery average's error bar than for seed-matched comparisons." The 0.113 has no pointer (AR14). Round 1 added this sentence (R1-03).
- R2-08. Section 4.5 and the Discussion explain the few changed calls by seed matching, which the R1-20 kernel contradicts: single-run comparisons change the wrong-call rate by at most 0.019 when the runs share a seed label and 0.016 when they don't, every interval reaching zero. Quotes main.tex:228 "suggests that most of the covariance cancels in such seed-matched gaps, which would explain the few changed calls" and main.tex:245 "seed-matched paired comparisons need little correction, with median paired-difference ratio 1.024".
- R2-09. The out-of-sample comparison reads as the method losing to a constant because its target (one noisy six-run ratio on the earlier three-size PolyPythias transfer runs) is unnamed and the pooled-target reversal is omitted. Quote main.tex:245 "Out of sample on margins, independence predicts a configuration's measured ratio with a mean absolute log error of 0.339 against 0.536 for the plug-in and 0.512 for our decomposition".
- R2-10. The abstract leads with a 70-word identification caveat that quotes "our margin value" before any value, never says why the covariance matters, and doesn't scope the claim to a fixed battery of likelihood-scored multiple choice or name sigma_agg as the cross-battery quantity. Quote main.tex:29 "although an item effect shared across benchmarks and halves would enter the estimate, and a 0.124 share of item variance would reproduce our margin value." Round 1's R1-02 put the caveat here and R1-07's trim left the abstract number-saturated.
- R2-11. The contribution list spills over two paragraphs, three of four items end on a limitation, and it repeats held-out numbers, the 0.113 to 0.051 result and the exploratory caveat. Quotes main.tex:47 "a within-battery count that doesn't rank batteries" and main.tex:49 "Apart from the registered test and the two PolyPythias rules, every analysis is exploratory." Round 1 inserted the K_eff caveat (R1-12).
- R2-12. The main text never reports fixed-bank run variance, the quantity a practitioner re-running a released bank faces, and results/snap-r2-r1-08 now gives it. Quote main.tex:67 "so reproducibility on that fixed bank is a separate question".
- R2-13. The paper doesn't say why it splits items rather than subtracting an analytic item-sampling variance from the full-data diagonal, which leaves the novelty over split-half and generalizability theory unstated. Quote main.tex:35 "We adapt the repeated-measurement construction of quantitative genetics to this setting and call it SNAP".
- R2-14. The 375 DataDecide runs were never scored on bank two. Quote main.tex:241 "We didn't score the 375 DataDecide runs on the second bank". GPU inference, still blocked.
- R2-15. No output in the repo backs the past-tense 45-run PolyPythias rescore, the byte-match check or the 6,808-item bank-two build. Quotes main.tex:45 "We therefore scored all 45 PolyPythias runs", main.tex:133, main.tex:135 "we built a second bank of 6,808 items". Scoring outputs arrive with the pending R1/R2 results, and the manifest is a CPU job.
- R2-16. The default build ends the main text on page 10. main.aux `\newlabel{maintext:end}{{6}{10}...}`. Rejected because the default build prints every outcome variant and round 1 recompiled all six single-outcome builds to page 9; the brief requires the same check after this round.
- R2-17. The failed-plan disclosure reads as a failed preregistration, and its enumeration range has no result file. Quote main.tex:129 "No estimation set reaches the plan's thresholds of 1.349 and 1.40, and an enumeration over the $\binom{25}{17}=1{,}081{,}575$ possible sets gives margin estimates from 1.037 to 1.317".
- R2-18. Two one-sentence paragraphs list accuracy subsets that exclude one, which reads as a significance search, and the power figure is labelled "fitted accuracy cell" although it uses generic accuracy-like noise. Quote main.tex:41 "The accuracy interval no longer includes one under five of the 25 recipe removals".
- R2-19. Table 1's caption points to gain and competence rows that no longer exist and calls the size-band rows wild bootstrap intervals, while research/outputs/snap-r6-twoway/r6_twoway.json computes cluster-robust t(4) intervals. Quote main.tex:144 "and the gain and competence adjustments are in Appendix~\ref{app:proxy}".
- R2-20. The Dirichlet weighting sweep has no result file. Quote main.tex:167 "A sweep of 2,000 weightings from a flat Dirichlet leaves 0.817 of margin intervals excluding one." The appendix copy (appendices_bcd.tex:204) needs the CPU rerun and stays untouched this round.
- R2-21. Permutation tail fractions read as non-significant p-values, the reverse of the intended point. Quote main.tex:165 "Across 2,000 such permutations 0.087 reach or exceed the observed margin estimate and 0.352 the observed accuracy estimate."
- R2-22. Slice D repeats Section 4.1 word for word and leaves a dangling referent. Quotes main.tex:220 "averaging 0.624 within formats and 0.007 across them" (same wording at main.tex:163) and main.tex:241 "At a share of 0.05 only 0.007 of simulated replicates reach the observed margin value."
- R2-23. The Discussion has text for the R2 not-supported branch only. Quote main.tex:241 "\outcome{\Rtwocase}{1}{R2 not supported}{ The cross-bank check in PolyPythias constrains that item effect in one family".
- R2-24. Related work credits "variance-component ideas" to Spearman 1904 and Cronbach 1951, and generalizability theory (brennan2001, in references.tex) is absent from the main text. Quote main.tex:234 "the variance-component ideas of \citet{spearman1904}, \citet{cronbach1951}, and \citet{searle1992}".
- R2-25. Zhao et al. are described as testing tasks one at a time. Quote appendices_bcd.tex:73 "\citet{zhao2026} test tasks one at a time without cross-task covariance."
- R2-26. No efficiency comparison between the split-half estimate and an analytic diagonal correction that uses all items. CPU kernel on released reductions.
- R2-27. "Covers well" overstates coverage that falls to 0.928. Quote main.tex:117 "We report the wild interval because it covers well across the twelve populations".
- R2-28. The truncation subset also drops one 530M configuration. Quote main.tex:127 "Dropping the 26 severely truncated configurations removes the 750M band".
- R2-29. The 33-configuration subset (1.082) invites a truncation reading that the near-final auxiliary contrast answers, and the text doesn't connect them. Quote main.tex:127 "On the 33 configurations that share a final step, margin inflation is 1.082 (\ci{0.121}{1.530})".
- R2-30. Edit artefact. Quote main.tex:133 "Our earlier transfer check scored a nested sample of 4,755 items and stays in Appendix~\ref{app:transport}."
- R2-31. DataDecide's description reads as the whole release, and "the same OLMES commit" has no antecedent. Quotes main.tex:37 "with 25 data recipes and five model sizes that each have three released replicates" and main.tex:45 "built at the same OLMES commit".
- R2-32. Table 2 prints percentiles in confidence-interval brackets, on five sizes against three elsewhere. Quote main.tex:198 "Original, four-benchmark subsets, all sizes (percentiles) & Margin & 1.176 & \ci{0.982}{1.476}".
- R2-33. Vague and defensive. Quote main.tex:181 "a power simulation that can't rescue the test". Round 1 kept this wording (R1-11).
- R2-34. First figure reference doesn't say the figure is in the appendix. Quote main.tex:163 "(Figure~\ref{fig:covariance})".
- R2-35. 0.821 appears in no result file, and the size-band interval that answers the anti-conservatism concern isn't mentioned. Quote main.tex:243 "take simulated margin coverage to 0.821 at a quarter of latent variance and 0.580 at a half".
- R2-36. Two power figures from different simulated populations sit unlabelled. Quotes main.tex:239 "at a design that would detect a true ratio of 1.10 in 0.135 of replicates" and main.tex:245 "accuracy needs eight to reach 0.803".
- R2-37. 6,808/37,682 is 0.181. Quote main.tex:217 "Bank two holds about a sixth of bank one's items".
- R2-38. The heading promises a mechanism the section doesn't test. Quote main.tex:219 "\subsection{Scoring format and mechanism}".
- R2-39. "This revision" exposes revision history in a blind submission, and "loss-proxy rescoring" is undefined. Quote main.tex:255 "come from earlier execution records that this revision didn't rerun, and the loss-proxy rescoring wasn't run."
- R2-40. Several main-text numbers live only in the extended supplement. Quotes main.tex:47 "every recipe, recipe-pair and benchmark deletion" and main.tex:203 "Removing CoQA lowers held-out margin inflation to 1.090".
- R2-41. Round-1 fixes not carried into the supplement. Quote supplement_extended_body.tex:127 "\citet{miller2024} estimates item-level uncertainty for one model." plus the 0.926 carry-over at supplement_extended_body.tex l.716.
- R2-42. Optional bibliographic completeness. references.tex entries fehlauer2025 (Crossref pp. 32970--32979) and ruan2024 (volume 37).
- R2-43. The 0.044 band-share bound and the 0.008 share have no stored output. Quote main.tex:243 "bounds that effect at 0.044 of the seed covariance on margins".
- R2-44. Rejected: "trait" is defined once at main.tex:60 and indexes the appendix tables, and R1-35 already moved the genetics analogy out of the main text.
- R2-45. Rejected: a commit hash in the text adds no independent corroboration, a third-party timestamp can't be made retroactive, and main.tex:255 already states the gap.
- R2-46. Rejected: main.tex:127 already says the PolyPythias seeds avoid the schedule confound by sharing one final step.
- R2-47. Rejected: main.tex:239 already names the accuracy cuts that exclude one (without BoolQ, adjacent checkpoint, held-out) and says they don't settle the bound.
- R2-48. Rejected: `\citet` ties and unreferenced equation labels are cosmetic, and the long-paragraph flag at main.tex:207 is handled by R2-05.

### Round 2 outcome, 2026-09-23 02:05 EDT
FIXED 37 (slices A 6, B 8, C 6, D 13, APP 4); NEEDS-EXPERIMENT 5; REJECTED 6. All five round 1 CPU-feasible NEEDS-EXPERIMENT items (R1-08, R1-18, R1-20, R1-49, R1-50) ran as Kaggle CPU kernels (enable_gpu false, enable_tpu false); outputs in results/snap-r2-*/, summary results/snap-r2-SUMMARY.md. Three corrected paper claims: rule-one power 0.356/0.026 became 0.259/0.016 (recentred jackknife, snap-r2-r1-18b); the shared-item wording "rejected" became "not supported" (snap-r2-r1-18); the seed-matching explanation was dropped (snap-r2-r1-20). Coordinator edits after splice: removed the unsourced 0.00477 from appendices_bcd.tex, and restored the 1,081,575-set enumeration range in the appendix from snap-r2-r1-49. Compile clean, 0 undefined references, maintext:end on page 9 in all six (Ronecase, Rtwocase) combinations. New findings rated likely to lower the score this round: 1 (R2-13, fixed in slice B).

## Round 3, started 2026-09-23 02:32 EDT
Pre-round snapshot: f23e293. Skills run: superpowers:using-superpowers, aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), stop-slop, superpowers:verification-before-completion. Raw outputs: work/rebuttal/r3/*.md

### Merged findings (round 3)

Merged 2026-09-23 02:47 EDT from work/rebuttal/r3/{kill_argument (KA, codex points P1 to P6), claim_audit (CA), citation_audit (CI), paper_audit (PA), academic_reviewer (AR, demanded experiments E1 to E6)}.md and the three round 2 CPU kernels in results/snap-r3-r2-{02,26,43}/ (summary results/snap-r3-SUMMARY.md). Every quote was checked against deliverables/*.tex at f23e293. Context the reviewers lacked: PolyPythias bank one is being scored on Kaggle now and bank two hasn't been scored, so any main-text claim that these runs were scored or that the release ships their hashes is false until then (R3-02).

The kernels change three round 2 items. R2-02 shows the 0.124 and 0.009 shares printed in the abstract, Sec 2.2, the Discussion and appendices_bcd.tex:259 come from a simulated population (item noise 0.73 on a unit-variance latent) and don't describe the released data: on the released per-half item noise a uniform 0.124 share lifts margin inflation only to 1.024 (cross-format 1.010, inside \ci{0.801}{1.035}), the share that would carry all of 1.244 is 1.42, above one and so unattainable, and it would imply a cross-format value of 1.113 that the interval excludes; on accuracy the explaining share is 0.053 and its implied 1.047 sits inside \ci{0.848}{1.063} (R3-01). R2-26 gives the analytic diagonal correction 1.2456 \ci{1.1439}{1.3398} against the split's 1.2439 \ci{1.1429}{1.3377}, with wild widths within 5 percent on all four batteries, so the split's case rests on needing no item-noise model rather than on precision, and without BoolQ item noise is 0.578 of the full-bank accuracy diagonal, where the fixed-bank value of 1.285 falls well below the split's 1.558 (R3-04, R3-24). R2-43 reproduces the 0.008 share and 0.044 bound from committed code (R3-25).

Slices, by current line numbers: A main.tex 28-45 (abstract and introduction; title at 14 stays), B 46-131 (Sections 2 and 3), C 133-200 (Section 4 up to, not including, sec:family at 201), D 201-243 (sec:family through \label{maintext:end}) plus the reproducibility statement at 250-251, APP appendix_a.tex, appendices_bcd.tex, references.tex and, for R3-40 and R3-41 only, supplement_extended_body.tex. Fix sketches are in work/rebuttal/r3/FIXER_BRIEF.md.

| id | severity | sources | statement | verbatim quote (file:line) | NEW/REPEAT | likely-lower | disposition | slice |
|---|---|---|---|---|---|---|---|---|
| R3-01 | critical | KA P1+P2 (codex critical), KA1, KA6, PA4, AR4, CA15, results/snap-r3-r2-02 | The shared-item sensitivity numbers (0.124, 0.009, 0.05) describe a simulated population, and on the released noise a uniform component can't produce 1.244, so the abstract states a self-weakening number that the data contradict and the cross-format argument cites the wrong reference value | main.tex:29 "A shared item component at 0.124 of item-noise variance would reproduce 1.244." (also main.tex:71, main.tex:237, appendices_bcd.tex:259) | REPEAT R2-02, R1-05 (residual; the round 2 wording, including the abstract sentence R2-10 added, is contradicted by the kernel) | yes | text-fixable | A, B, D, APP |
| R3-02 | critical | CA2, CA3 (part), coordinator context | Main text says the PolyPythias runs and bank two were scored and that the release ships frozen hashes for both request files, while bank one is still scoring, bank two is unscored and the bank-two hash is a deterministic rebuild | main.tex:251 "The PolyPythias battery and the second bank were scored in float32 with transformers 4.57.1 on Kaggle T4 cards"; main.tex:43 "We therefore scored all 45 PolyPythias runs at five sizes on the same 37,682 items" | REPEAT R2-15 (earlier disposition wrong: it waited for outputs instead of fixing the tense) | yes | text-fixable | A, B, D, APP |
| R3-03 | major | KA1, KA P2 adjudication, PA10 | The fixed-bank replicate estimate needs no cross-half assumption and settles the fixed-battery reading, but the paper never says so and never names its denominator | main.tex:237 "We didn't score the 375 DataDecide runs on the second bank, which leaves the 1.244 untested on fresh items and the shared-item check unrun in the family that supplies our headline." | REPEAT R2-12 (residual: round 2 added the number without its role) | yes | text-fixable | B, D |
| R3-04 | major | KA4, PA1, AR2, AR Q1, AR E6, results/snap-r3-r2-26 | With 1.237 printed beside 1.244, the paper never says what the split adds over the replicate SD of the battery average, and the recommendation says the ratio helps only where SNAP can't run | main.tex:241 "Our ratio therefore measures this battery and helps only where replicates are missing and the target battery's own ratio is close." | NEW (created when R2-12 placed 1.237 beside 1.244; related to R1-21) | yes | text-fixable | A, B, D |
| R3-05 | major | CA1, AR3 (part) | The rule-two simulation's 0.124 share lifts the PolyPythias within-bank median only to 1.046, so it never tests the rule against a component that explains the inflation, and "under either explanation" is unsupported | main.tex:205 "under independence with a 0.124 item share it returns supported in 0.033 and undecided in 0.957, so an undecided verdict is expected under either explanation and not supported doesn't exclude a shared component." | NEW (created by the R2-05 edit) | yes | text-fixable | D, APP |
| R3-06 | major | KA2, AR3, AR seat R4 | The PolyPythias rules have low simulated power (0.259 pass at a true 1.244; undecided 0.761), and the introduction presents them without it, so the pending outcomes read as pre-announced inconclusive | main.tex:43 "Two rules fixed before scoring read the results" | REPEAT R1-19, R2-05 (residual) | yes | text-fixable | A |
| R3-07 | major | KA7, AR9, CA3 | "Registered" implies third-party timestamping that no commit has, and the rule-commit timing is untraceable in the result roots | main.tex:29 "A registered test on four unseen tasks fails its lower-limit rule at 1.217 with interval \ci{0.872}{1.498}."; main.tex:251 "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp" | REPEAT R1-10, R1-38, R2-45 (R2-45's rejection left the word in place) | yes | text-fixable | A, B, C, D, APP |
| R3-08 | major | KA3, AR1 | The introduction motivates the paper with a simulated error-control failure while the real recipe decisions change by at most 0.009, and no sentence scopes the claim | main.tex:33 "In simulation with margin-like covariance, such a comparison declares a difference in 0.113 of replicates with a true gap of zero, against a nominal rate of 0.05 (Appendix~\ref{app:supplementary})" | REPEAT R1-03, R1-04, R2-07 (residual) | yes | text-fixable | A |
| R3-09 | major | CA6, AR8, AR11, PA3, PA14 | The R2-10 abstract rewrite dropped the margin label on 0.113 and the checkpoint scope R1-15 had added, joined a composition fact to a recommendation with an unsupported "so", and named the 40 contrasts differently from the body | main.tex:29 "so batteries compare through the aggregate standard deviation." | NEW (regressions from the R2-10 rewrite) | yes | text-fixable | A |
| R3-10 | major | AR7, AR seat R3 | The abstract and results still read as an audit log, with about twenty numbers and process history in results paragraphs | main.tex:115 "Two later additions, a cluster test-inversion interval and a residual-scaled wild interval, move neither verdict across one" | REPEAT R1-07, R2-10 (fix failed) | yes | text-fixable | A, B |
| R3-11 | major | AR6, KA P4 | The abstract doesn't say the design can't resolve accuracy, the scale most papers report | main.tex:29 "Our accuracy interval \ci{0.993}{1.157} includes one." | REPEAT R1-22, R2-18 (residual) | yes | text-fixable | A |
| R3-12 | major | AR4, AR E1, KA P2 | The headline family never gets the cross-bank check | main.tex:237 "We didn't score the 375 DataDecide runs on the second bank" | REPEAT R1-06, R2-14 (open) | yes | NEEDS-EXPERIMENT (GPU) | none |
| R3-13 | major | AR5, AR Q2 | Lambda rises when BoolQ is removed while sigma_agg falls, so the reviewer asks why Lambda is the headline | main.tex:159 "BoolQ, the only benchmark in its format, carries 68\% of the margin covariance trace" | REPEAT R1-12, R1-13, R1-14 | yes | REJECTED | none |
| R3-14 | moderate | AR13 | Novelty over split-half and generalizability theory is one clause | main.tex:230 "and what we add is the estimand and its measurement" | REPEAT R1-23, R2-13, R2-24 (residual) | yes | text-fixable | D |
| R3-15 | moderate | CI1 | The novelty sentence contradicts the Jordan citation two sentences earlier, since Jordan measures run-deviation dependence across ImageNet evaluation sets | main.tex:228 "We know of no study that estimates the covariance of run noise between benchmarks or an effective benchmark count from that covariance." | NEW (created by the R1-23 and R1-26 edits together) | yes | text-fixable | D |
| R3-16 | moderate | PA2, CA11 | Sec 4.5 reports covariance gains while the Discussion reports the decomposition losing to independence, with no sentence linking the two targets, a dangling "three-size PolyPythias runs" pointer and unscoped three-size numbers | main.tex:241 "Against one configuration's six-run margin ratio on the earlier three-size PolyPythias runs" | REPEAT R2-09 (residual) | yes | text-fixable | D |
| R3-17 | moderate | PA8 | The 0.921 diagnostic appears three times, the held-out 1.240 comparison twice and the screening split twice, which reads as padding | main.tex:237 "A scalar component shared by every benchmark would also enter the cross-format pairs, whose diagnostic of 0.921 constrains a uniform component but not one that follows scoring format." | REPEAT R2-22 (residual) | yes | text-fixable | A, D |
| R3-18 | moderate | PA9 | The identification argument is packed into one 60-word sentence whose "unlike" clause carries the target-versus-nuisance distinction | main.tex:71 "Centring removes any item effect constant across runs, so only a run-by-item-set deviation shared by both halves enters the numerator" | NEW (created by the R2-01 edit) | yes | text-fixable | B |
| R3-19 | moderate | PA6 | "Is a bound" doesn't say what is bounded, and the post-hoc reading governs the pending R1-fail text | main.tex:205 "a failing estimate inside the simulated range is a bound and one below 1.026 counts against transfer." | NEW (created by the R2-05 edit) | yes | text-fixable | D |
| R3-20 | moderate | PA13 | "Five-size rescore" collides with the new five-size PolyPythias battery the rules read | main.tex:251 "The PolyPythias transfer, five-size rescore, and checkpoint results come from earlier execution records that we didn't rerun for the final analysis." | NEW | yes | text-fixable | D |
| R3-21 | moderate | PA15 | None of the 14 benchmarks, AGIEval or OLMES has a bibliography entry | main.tex:119 "DataDecide supplies the ten benchmarks ARC-Challenge, ARC-Easy, BoolQ, CommonsenseQA, HellaSwag, MMLU, OpenBookQA, PIQA, Social IQa, and WinoGrande." | NEW (R1-61 rejected only the acronym flag) | yes | text-fixable, deferred until a citation audit verifies the entries | none |
| R3-22 | moderate | PA20 | Three power figures for the same 125-configuration, three-run design (0.997 against 0.970 on margins, 0.135 against 0.111 on accuracy) don't name their true ratio or population | appendices_bcd.tex:379 "At 125 configurations and three runs the margin effect clears one in 0.970 of replicates while the accuracy effect clears it in 0.111." | REPEAT R2-36 (residual) | yes | text-fixable | D, APP |
| R3-23 | moderate | AR E2, AR seat R3 | Scope stops at 1B and likelihood-scored multiple choice | main.tex:237 "Our populations stop at 1B and at likelihood-scored multiple choice" | REPEAT R1-27 (residual) | yes | NEEDS-EXPERIMENT (GPU) | none |
| R3-24 | moderate | KA8, results/snap-r3-r2-26 | "Needs neither" contradicts the cross-half independence caveat, and "at the cost of half the items" implies a precision cost the analytic comparison doesn't show | main.tex:93 "while the split needs neither, at the cost of half the items in each score." | NEW (regression from the R2-13 edit; also closes R2-26) | no | text-fixable | B, APP |
| R3-25 | minor | results/snap-r3-r2-43 | The 0.008 share and 0.044 bound now have a stored output that reproduces them from committed code | main.tex:239 "bounds that effect at 0.044 of the seed covariance on margins" | REPEAT R2-43 (resolved by the kernel) | no | text-fixable (no value change; record source) | APP |
| R3-26 | minor | KA13, AR10 | "Calibrated" overstates coverage of 0.928 to 0.954 and 0.823 under band sharing | main.tex:45 "Algorithm~\ref{alg:snap} gives the measurement recipe with calibrated intervals" | NEW (regression from the R2-11 edit; R2-27 fixed the same overstatement at l.113) | no | text-fixable | A |
| R3-27 | minor | CA8 | The original-ten row values were computed in the kernel that reported the test, so "fixed before any held-out score existed" overstates what was fixed | main.tex:175 "a comparison we fixed before any held-out score existed" | NEW | no | text-fixable | A, C |
| R3-28 | minor | CA9 | The held-out leave-one-out summary omits that removing DROP leaves an interval excluding one | main.tex:199 "while removing any other task leaves it between 1.120 and 1.213" | NEW | no | text-fixable | C |
| R3-29 | minor | KA5 | Held-out accuracy excludes one while margins don't, the reverse of the scale rationale, and the text doesn't reconcile it | main.tex:199 "As an exploratory result, the held-out accuracy inflation interval excludes one." | NEW | no | text-fixable | C |
| R3-30 | minor | PA18, AR12 | AGIEval replacement detail and the width framing read as arguing the failure away | main.tex:175 "Interval width rather than the point gap decides the registered verdict." | REPEAT R1-11, R2-33 (residual) | no | text-fixable | C |
| R3-31 | minor | PA16 | The recipe-pair deletion claim has no Sec 4.1 support | main.tex:45 "every recipe, recipe-pair and benchmark deletion" | REPEAT R2-40 (residual) | no | text-fixable | C |
| R3-32 | minor | KA12, CA5, PA11 | The auxiliary-contrast clause reads as computed on the 33-configuration subset, and "one" reads as a pronoun | main.tex:123 "intervals too wide to separate one from the full-sample estimates, although the auxiliary contrast, whose runs sit near their final steps, still excludes one" | NEW (created by the R2-29 edit) | no | text-fixable | B |
| R3-33 | minor | PA5 | The bias conclusion generalises from two simulated populations | main.tex:113 "so finite-sample bias works against finding an excess" | NEW | no | text-fixable | B |
| R3-34 | minor | PA12 | The modifier attaches to the interval, and the cut list omits the truncation subset 1.120 \ci{1.020}{1.208} | main.tex:235 "The full-battery accuracy interval includes one at accuracy-like item noise, a design that would detect a true ratio of 1.10 in 0.135 of replicates" | REPEAT R2-36, R2-47 (residual) | no | text-fixable | D |
| R3-35 | minor | PA19 | The seed-matching conclusion skips a step | main.tex:224 "so seed matching doesn't explain the few changed calls" | NEW (created by the R2-08 edit) | no | text-fixable | D |
| R3-36 | minor | CA10 | No result file links the OLMES commit to DataDecide's own evaluation | main.tex:131 "with OLMES at the commit DataDecide used" | NEW | no | text-fixable | A, B |
| R3-37 | minor | KA9, CA4 | Appendix prints pooled 12,000-replicate coverage (0.821, 0.580) against the main text's 10,000-replicate 0.823 and 0.581 | appendices_bcd.tex:387 "At a quarter the recipe-clustered interval falls to 0.821 and at a half it reaches 0.580" | REPEAT R2-35 (fix incomplete) | no | text-fixable | APP |
| R3-38 | minor | KA10 | 0.01196 is a single-run threshold applied to three-run recipe-mean gaps | appendices_bcd.tex:216 "the Gaussian calculation gives $P_{\rm flip}>0.05$ for a true gap below 0.01196" | NEW | no | text-fixable | APP |
| R3-39 | minor | CI2 | Zhao et al. state a conditional caveat, not an observed positive correlation | appendices_bcd.tex:73 "noting positive task correlation without estimating it" | NEW (regression from the R2-25 edit) | no | text-fixable | APP |
| R3-40 | minor | CI3 | Miller treats each model as fixed and never models run variance | main.tex:228 "\citet{miller2024} gives clustered and paired item-sampling errors with run variance fixed" | REPEAT R1-43, R2-41 (residual) | no | text-fixable | D, APP |
| R3-41 | minor | CA7 | Half-up rounding is inconsistent inside one supplement row | supplement_extended_body.tex:716 "Three sizes, 75 & 0.73 & 0.019 & 0.258 & 0.792 & 0.927" | REPEAT R1-46, R2-41 (residual) | no | text-fixable | APP |
| R3-42 | minor | AR15 | Third-person audit register in the authors' own appendix | appendix_a.tex:103 "The author-reported power calculation assumes approximately Gaussian half-score deviations." | NEW | no | text-fixable | APP |
| R3-43 | minor | AR16 | A named Kaggle kernel is a double-blind risk | appendices_bcd.tex:375 "(Kaggle CPU kernel snap-r2-r1-49)" | NEW (created by the round 2 coordinator edit) | no | text-fixable | APP |
| R3-44 | minor | PA7 | The rounded estimates differ by 0.023 while the text says 0.024 (0.0239 unrounded) | main.tex:175 "However, the two point estimates differ by 0.024" | NEW | no | text-fixable | C |
| R3-45 | minor | KA11, KA P5, KA P6 | Broad title and battery-specific evidence | main.tex:14 "\title{Estimating Run-to-Run Covariance\\Across Language Model Benchmarks}" | REPEAT R1-02 | no | REJECTED | none |
| R3-46 | minor | CA12 | Two kernels give 0.259 and 0.257 for rule one | main.tex:205 "Over 4,000 replicates the first rule passes in 0.259 at a true 1.244 and in 0.016 at independence" | NEW | no | REJECTED | none |
| R3-47 | minor | CI4 | "The authors" is ambiguous between two cited papers, and the Appendix A.5 pointer is unverified | supplement_extended_body.tex:135 "The authors resample runs within tasks, with an additional task-resampling variant in their Appendix A" | NEW | no | REJECTED | none |
| R3-48 | minor | AR14 | A full appendix audits a proxy the authors conclude is broken | appendices_bcd.tex:308 "the shipped proxy carries no measurable signal about the run it scores" | REPEAT R1-33 | no | REJECTED | none |
| R3-49 | minor | PA17 | The contribution list omits the second-family test | main.tex:45 "This paper makes four contributions to measuring run covariance." | NEW | no | REJECTED | none |

Totals: 49 findings, critical 2, major 11, moderate 11, minor 25. Dispositions: 41 text-fixable (one of them, R3-21, deferred until citation verification and R3-25 confirm-only), 2 NEEDS-EXPERIMENT (both GPU: R3-12, R3-23), 6 REJECTED.

Rejection reasons, each checked against the tex. R3-13: main.tex:91 and main.tex:159 already say the factor compares a battery with itself and that batteries compare through $\sigma_{\mathrm{agg}}$, and Table 1 prints $\sigma_{\mathrm{agg}}$ beside every $\widehat\Lam$, so leading with $\sigma_{\mathrm{agg}}$ would cost length without new information. R3-45: the abstract's second sentence (main.tex:29) scopes the claim to a fixed battery of likelihood-scored multiple-choice benchmarks, and R1-02 kept the title on that condition. R3-46: 0.2585 and 0.257 agree within Monte Carlo error, and appendices_bcd.tex:349 names the committed recentring jackknife as the source, as R2-06 chose. R3-47: supplement_extended_body.tex isn't \input by main.tex and the only fix needs an unverified appendix pointer, so it waits for the next citation audit. R3-48: appendix length doesn't count toward page 9, and appendices_bcd.tex:303-310 is the record of why no competence adjustment enters, which a reviewer would otherwise ask for. R3-49: main.tex:43 introduces the second-family test in the paragraph before the list, and adding it costs page-2 length.

New findings rated likely to lower the score: 8 (R3-04, R3-05, R3-09, R3-15, R3-18, R3-19, R3-20, R3-21)

### Round 3 outcome, 2026-09-23 02:58 EDT
FIXED 39 distinct findings (some span slices; status lines A 12, B 9, C 7, D 16, APP 14); NO-CHANGE 1 (R3-25, confirmed correct); DEFERRED 1 (R3-21, benchmark and OLMES bibliography entries await citation-audit verification); NEEDS-EXPERIMENT 2 (GPU: R3-12 DataDecide on bank two, R3-23 above 1B or generative tasks); REJECTED 6. Round 2 CPU items R2-02, R2-26, R2-43 ran as Kaggle CPU kernels snap-r3-r2-{02,26,43} (enable_gpu false, enable_tpu false); outputs in results/snap-r3-*/. Main corrections: the 0.124 shared-item share now stated on released noise (lifts margins to 1.024; 1.244 would need 1.42, and its implied 1.113 is excluded by 0.921 [0.801, 1.035]); PolyPythias scoring moved from past tense to plan; "registered" replaced by "pre-specified". Compile clean, 0 undefined references, maintext:end on page 9 in all six outcome combinations. New findings rated likely to lower the score this round: 8 (R3-04, R3-05, R3-09, R3-15, R3-18, R3-19, R3-20, R3-21), six of them regressions from round 1-2 edits. Open decision for the author: third-party timestamp on the rule commit before PolyPythias scoring ends (KA7).

## Round 4, started 2026-09-23 03:32 EDT
Pre-round snapshot: 2becd1b. Skills run: superpowers:using-superpowers, aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), stop-slop, superpowers:verification-before-completion. No CPU-feasible NEEDS-EXPERIMENT items remain, so no Kaggle kernel this round. Raw outputs: work/rebuttal/r4/*.md

### Merged findings (round 4)

Merged 2026-09-23 04:25 EDT from work/rebuttal/r4/{kill_argument (KA, codex points P1 to P6), claim_audit (CA), citation_audit (CI), paper_audit (PA), academic_reviewer (AR, demanded experiments "exp 1" to "exp 7")}.md. Every quote was checked against deliverables/*.tex at 2becd1b. Context the reviewers lacked: PolyPythias bank one is being scored on Kaggle and bank two is unscored, so the \pending and \outcome scaffolding stays and no finding asks for PolyPythias numbers; DataDecide on bank two needs GPU and stays NEEDS-EXPERIMENT.

CA1 verified. seednoise.reliability.variance_components (research/outputs/snap-r6-perm-seeds/seed-noise/src/seednoise/reliability.py:59-73, byte-identical in all five vendored src copies) returns noise2 = tot - seed, where tot is the within-half variance of the centred half scores and seed is the cross-half diagonal from sigma_e. A component identical in both halves enters the cross-half product, so it lands in seed and is subtracted out of noise2. results/snap-r3-r2-02/r2_02.py scales the injected component as q sqrt(v_j v_k) with v = noise2, so under its own injection model the measured v is only the non-shared remainder and q* = 1.4225 means the shared variance would be 1.42 times the non-shared item noise, which nothing in the data forbids. The round 3 argument "would need a share of 1.42, more than the item noise" is therefore circular and goes everywhere it appears (main.tex:29, :71, :235 and appendices_bcd.tex:261). The cross-format exclusion survives because it tests the component against the observed cross-format products, and it holds under both scalings the files report: 1.113 under noise-proportional scaling (explain.induced_cross_format_diagnostic 1.1133) and 1.153 under equal pair weights (equal_pair_weight_check 1.1526, printed at appendices_bcd.tex:128), both above the upper limit 1.035 of 0.921 \ci{0.801}{1.035} (cross_format_wild 0.9212 [0.8007, 1.0347]). The 1.024-at-0.124 figure makes no impossibility claim, so it isn't circular, but it rests on the same definition (its 0.124 is a share of the non-shared noise, not of the simulated population's total noise), and once the 1.42 argument goes it constrains nothing and only shows that the simulated share doesn't carry over to the released noise scale. It leaves the main text and stays in the appendix with the definition stated. The accuracy reading (share 0.053, implied 1.047 inside \ci{0.848}{1.063}) is a non-exclusion and survives with the same label fix.

Slices, by current line numbers of deliverables/main.tex (preamble 1-27, tail 242-256): A 28-45 (abstract and introduction; title at 14 stays), B 46-130 (Sections 2 and 3), C 131-198 (Section 4 up to, not including, sec:family at 199), D 199-241 (sec:family through \label{maintext:end}) plus the reproducibility statement at 248-249 (AI-use and ethics statements at 242-246 stay untouched), APP appendix_a.tex, appendices_bcd.tex, references.tex and, for R4-36 and R4-37 only, supplement_extended_body.tex. Fix sketches are in work/rebuttal/r4/FIXER_BRIEF.md.

| id | severity | sources | statement | verbatim quote (file:line) | NEW/REPEAT | likely-lower | disposition | slice |
|---|---|---|---|---|---|---|---|---|
| R4-01 | critical | CA1, KA P1, AR6 (abstract part), PA10 context | The uniform shared-component bound is circular: item noise is defined as within-half variance minus the cross-half diagonal, so a component identical in both halves can never be part of it, and "more than the item noise" restates the injection scaling | main.tex:29 "A uniform item component shared across benchmarks would need more than all released item-noise variance to produce 1.244."; main.tex:71 "would need a share of 1.42, more than the item noise, to produce 1.244"; main.tex:235 "a uniform item effect shared across benchmarks can't produce the margin value"; appendices_bcd.tex:261 "would have to be 1.422, more than the item-noise variance itself" | NEW (regression from the R3-01 edit; AR6's request to state the untested format-following component in the abstract repeats R3-12) | yes | text-fixable | A, B, D, APP |
| R4-02 | critical | KA5, PA1, AR2, AR1 (part), AR Q1, KA P6 | The paper recommends the plain replicate SD for a fixed bank (1.237, needing no split), and the introduction still sells the split through an untested bank-transfer property, so reviewers ask what SNAP adds | main.tex:239 "For a fixed released bank the replicate standard deviation of the battery average gives the aggregate uncertainty directly, and we recommend reporting it with a benchmark-removal check" | REPEAT R3-04 (residual: the answer went into the Discussion, while the contribution paragraph still leads with transfer) | yes | text-fixable | A |
| R4-03 | major | KA1, CA6, AR3, KA P2 | Transfer to redrawn banks is stated as an established property of the target although the Discussion says the 1.244 is untested on fresh items | main.tex:45 "Unlike the battery average's replicate standard deviation, this target transfers to redrawn banks and separates run variance from item noise."; main.tex:63 "This target transfers to a redrawn or extended item bank" | NEW (the line 45 sentence is a regression from the R3-04 edit; line 63 dates from R1-08) | yes | text-fixable | A, B |
| R4-04 | major | AR1, PA3, KA P6 | The abstract opens on the simulated 0.113 error rate and never says the correction moves at most 12 of 173 to 223 real recipe calls | main.tex:29 "in simulation a margin-scale comparison using it declares a difference in 0.113 of null replicates, against a nominal 0.05" | REPEAT R3-08, R2-07, R1-03 (residual: R3-08 scoped the introduction, not the abstract) | yes | text-fixable | A |
| R4-05 | major | KA3, AR5, KA P4 | The abstract and introduction give the held-out failure without the same-scope comparator (1.240 \ci{1.054}{1.397}), so a reader can't see that interval width, not the estimate, failed the rule | main.tex:29 "A pre-specified test on four unseen tasks fails its lower-limit rule at 1.217 \ci{0.872}{1.498}."; main.tex:41 "The test fails on all 225 runs, where held-out inflation is 1.217 \ci{0.872}{1.498} (Section~\ref{sec:heldout})." | NEW (regression: the R3-17 cut deleted the introduction's comparator sentence) | yes | text-fixable | A |
| R4-06 | major | CA3, AR4 (part), KA P5 | "We read both as bounds" contradicts "A first-rule pass confirms the effect", and "bound" is undefined for a pass | main.tex:43 "so we read both as bounds"; main.tex:203 "A first-rule pass confirms the effect in this family." | NEW (regression from the R3-06 edit) | yes | text-fixable | A |
| R4-07 | major | KA4, AR4 (part), AR Q3, KA P5 | Rule one fails in 0.741 of replicates at the true value, so the post hoc 1.026 reading is the likely one, and nothing shows it discriminates: under independence the middle 90% of estimates runs from 0.848 to 1.139 (results/snap-r2-r1-18/r1_18_rule_two.json, independence_share0 within_lambda_5_95), which contains 1.026 | main.tex:203 "a failing estimate at or above 1.026 is consistent with the DataDecide value and its jackknife upper limit bounds inflation in this family, while one below 1.026 counts against transfer." | REPEAT R2-05, R3-19 (residual) | yes | text-fixable | D |
| R4-08 | major | PA2, AR9, PA15 | The main text no longer says the planning predictions (margin above 1.349, accuracy above 1.40) failed under every estimation set or that gain check G5 failed, and the appendix cites a 1.349 threshold the main text never introduces | main.tex:123 "We never drew the analysis plan's split of eight screening and seventeen estimation recipes, so every choice in the primary analysis could see all 125 configurations and no holdout survives (Appendix~\ref{app:design})."; appendices_bcd.tex:294 "the proposed threshold of 1.349" | NEW (regression: the R2-17 edit in f23e293 removed "No estimation set reaches the plan's thresholds of 1.349 and 1.40" from main.tex) | yes | text-fixable | B, APP |
| R4-09 | major | KA2, KA P1 | Section 2.2 states the cross-half assumption without saying that the fixed-bank 1.237 needs neither halves nor the assumption, so the headline reads as wholly conditional on it | main.tex:66 "If the item errors have conditional mean zero and zero covariance between the two halves across the relevant runs and benchmarks, then" | REPEAT R3-03 (residual: the statement sits in Sec 2.1 and the Discussion, not at the assumption) | yes | text-fixable | B |
| R4-10 | major | PA4, CA9, KA5 (numbers) | The line 63 comparison leaves 1.285 undefined (it collides with the format-fit 1.285 at line 216), and "but" contrasts shares from two different batteries | main.tex:63 "Item noise is 0.037 of the margin diagonal but 0.578 of the accuracy diagonal without BoolQ, where 1.285 falls below the split's 1.558." | NEW (regression from the R3-03 and R3-04 edit) | yes | text-fixable | B |
| R4-11 | major | PA14, AR11 | The abstract is hard to read: SNAP is never expanded, "it" has three antecedents, and it carries about twenty numbers | main.tex:29 "SNAP estimates it from cross-half products of run-centred item-half scores" | REPEAT R3-10, R2-10 (fix failed) | yes | text-fixable | A |
| R4-12 | major | AR7, AR Q2 | 1.244 is a battery property carried by BoolQ, so the paper should lead with the format model | main.tex:157 "BoolQ, the only benchmark in its format, carries 68\% of the margin covariance trace" | REPEAT R3-13, R1-12, R1-13, R1-14 | yes | REJECTED | none |
| R4-13 | major | AR8, AR exp 2 | The only checkpoint-clean subset is uninformative and 750M sits at 41.5% of its final step | main.tex:121 "On the 33 configurations that share a final step, margin inflation is 1.082 (\ci{0.121}{1.530})" | REPEAT R2-29, R3-32 (text already names the near-final auxiliary contrast; the gap is experimental) | yes | NEEDS-EXPERIMENT (GPU: score the 750M default runs at their released final checkpoints) | none |
| R4-14 | major | KA P3, AR exp 1 | DataDecide never gets the cross-bank check | main.tex:235 "We didn't score the 375 DataDecide runs on the second bank, which leaves the 1.244 untested on fresh items" | REPEAT R3-12, R2-14, R1-06 (open; R4-03 closes the text exposure) | yes | NEEDS-EXPERIMENT (GPU) | none |
| R4-15 | moderate | CI2 | None of the ten benchmarks, the four held-out tasks, AGIEval with LogiQA and LSAT-LR, or OLMES has a bibliography entry; the citation audit now supplies 17 VERIFIED bibitems | main.tex:117 "DataDecide supplies the ten benchmarks ARC-Challenge, ARC-Easy, BoolQ, CommonsenseQA, HellaSwag, MMLU, OpenBookQA, PIQA, Social IQa, and WinoGrande." | REPEAT R3-21 (deferred, now unblocked) | yes | text-fixable | A, B, C, APP |
| R4-16 | moderate | KA6 | Four appendix sentences refer to a prior version or supplement, which in a double-blind first submission reads as leftover revision history | appendices_bcd.tex:310 "For this revision we fitted four proxy weightings out of fold"; :316 "the obstacle we reported earlier was our own naming"; :343 "which the earlier supplement gave as 1.07395"; :351 "the pass rate of 0.356 that an earlier version reported" | NEW (REPEAT R2-39 in substance, whose fix covered main.tex only; the :351 sentence is a regression from the R2-06 edit) | yes | text-fixable | APP |
| R4-17 | moderate | PA5 | "A seed label that also changes the training batch" reads as data order, which PolyPythias seeds change too, so the stated motive for the second family doesn't hold; the intended contrast is the default-versus-auxiliary schedule mix | main.tex:43 "A single model family and a seed label that also changes the training batch leave open whether the inflation belongs to DataDecide's design." | NEW | yes | text-fixable | A |
| R4-18 | moderate | PA6 | The margin gain uses oracle held-out marginals, and the operational comparison without them also finds no gain on margins (research/outputs/snap-r8-prediction/SNAP/C07_margin/result.json: all three paired intervals include zero), which the text doesn't say | main.tex:220 "We find covariance gains on margins and no separation on accuracy." | NEW | yes | text-fixable | D, APP |
| R4-19 | moderate | AR exp 3, AR exp 6 | No population above 1B, no generative or instruction-tuned tasks | main.tex:235 "Our populations stop at 1B and at likelihood-scored multiple choice" | REPEAT R3-23, R1-27 | yes | NEEDS-EXPERIMENT (GPU) | none |
| R4-20 | moderate | AR10, AR exp 5 | The competence adjustment that drives margin inflation to 0.731 is absent from the main text, and no main-text sentence points to app:proxy or says mediation needs held-out loss | appendices_bcd.tex:308 "It gives margin inflation of 0.731 with interval 0.673 to 0.784" | NEW (regression: the R2-19 caption fix removed the only main-text pointer to app:proxy) | no | text-fixable (the held-out loss run itself is GPU) | D |
| R4-21 | moderate | CA4, PA7 | "Seed signal" is defined by reliability at line 37, and line 197 infers it from which interval excludes one, which undercuts the reason for making margins primary | main.tex:197 "so which scale carries more seed signal depends on the battery" | NEW (regression from the R3-29 edit) | no | text-fixable | C |
| R4-22 | moderate | PA8 | "Can't exclude one" reads as the number one, in a 90-word sentence | main.tex:203 "and not supported can't exclude one." | NEW (regression from the R3-05 edit) | no | text-fixable | D |
| R4-23 | moderate | PA9 | "Fixed-battery run covariance" and "fixed-bank run variance" name different targets one word apart, "a nuisance up to which we identify" doesn't parse, and "that excess" has no antecedent | main.tex:71 "A deviation tied to the items both halves share is a nuisance up to which we identify the estimate."; main.tex:63 "counts as fixed-bank run variance" | NEW (regression from the R3-01 and R3-18 edits) | no | text-fixable | B |
| R4-24 | moderate | PA10 | Line 113 says shared item error biases the estimate down and line 71 says a shared component lifts it, without saying one is within a benchmark and the other across benchmarks | main.tex:113 "Cross-half error correlation of 0.1 and the accuracy-like null population bias the estimate down by 0.011 to 0.016" | NEW | no | text-fixable | B |
| R4-25 | moderate | CA2, KA8 | Main text prints 10,000 replicates with 0.823 and 0.581, the appendix pooled 12,000 with 0.821 and 0.580 | main.tex:237 "take simulated margin coverage over 10,000 replicates to 0.823 at a quarter of latent variance and 0.581 at a half" | REPEAT R3-37 (fix failed: the appendix moved to the pooled values and the main text stayed) | no | text-fixable | D |
| R4-26 | moderate | AR exp 4 | A held-out battery large enough for the rule to have power | main.tex:175 "with 1,000 items in each of the four tasks" | NEW | no | NEEDS-EXPERIMENT (GPU; any new battery would be exploratory, since the pre-specified test is fixed) | none |
| R4-27 | minor | KA7, CA8 | 0.061 and 0.018 are the effective coefficient $\bar r_E$, which main.tex:91 says equals the mean correlation only at equal variances | main.tex:239 "equicorrelated seed covariance at the observed mean correlation"; appendices_bcd.tex:456 "at the observed mean seed correlation, 0.061 on margins and 0.018 on accuracy" | NEW (main-text phrase is a regression from the R3-22 edit) | no | text-fixable | D, APP |
| R4-28 | minor | KA9 | The paper documents a leverage-corrected interval with better coverage and ships its own without naming the alternative in the main text | appendices_bcd.tex:253 "reaches 0.95 in ten cells where ours reaches it in one" | NEW | no | text-fixable (lowest priority in B) | B |
| R4-29 | minor | KA10 | An admitted untraced 0.0007 gap between the sign score and accuracy invites doubt about the scoring pipeline | appendices_bcd.tex:142 "differs from the accuracy estimate of 1.078 by 0.0007 for reasons we haven't traced" | NEW | no | text-fixable | APP |
| R4-30 | minor | CA5 | The range 1.177 to 1.263 reads as the interval although it is the range of point estimates; the lowest lower limit is 1.037 | main.tex:161 "all 300 recipe-pair deletions keep the interval above one, between 1.177 and 1.263" | NEW (regression from the R3-31 edit) | no | text-fixable | C |
| R4-31 | minor | CI1 | The relative clause can attach to "its measurement on released pretraining runs", which Heineman et al. do perform for seed noise | main.tex:228 "and its measurement on released pretraining runs, which \citet{miller2024} and \citet{heineman2025} don't estimate" | NEW (regression from the R3-14 edit) | no | text-fixable | D |
| R4-32 | minor | PA12, KA12 | Terms drift (unseen against held-out; "a rule" against "rules" across abstract variants), "pre-specified" appears twice in one clause, and "fails on all 225 runs" reads as a per-run failure | main.tex:171 "\subsection{A pre-specified test on unseen tasks}"; main.tex:235 "the pre-specified test, which failed at its pre-specified scope"; main.tex:41 "The test fails on all 225 runs" | NEW (the doubled phrase is a regression from the R3-07 mechanical edit) | no | text-fixable | A, B, C, D |
| R4-33 | minor | PA11 | Section 3.2's second paragraph opens by restating the introduction | main.tex:175 "Because the ten benchmarks above shaped our estimator, we pre-specified this test on tasks outside them before any of their production scores existed." | NEW | no | text-fixable | C |
| R4-34 | minor | PA13 | The reproducibility statement's 500 permutation replicates match no main-text permutation analysis | main.tex:249 "500 permutation replicates" | NEW | no | REJECTED | none |
| R4-35 | minor | AR14 | The ratio behind 0.928 to 1.025 is unnamed | main.tex:222 "the two kinds of pair have paired-difference deviations within a factor of 0.928 to 1.025" | NEW | no | text-fixable | D |
| R4-36 | minor | CA10 | The supplement still says "registered" | supplement_extended_body.tex:694 "\paragraph{Registered held-out test}"; :707 "Simulated pass rate of the registered rule" | REPEAT R3-07 (fix incomplete in the supplement) | no | text-fixable | APP |
| R4-37 | minor | CI3 | "The authors" is ambiguous between two cited papers, and the Appendix A.5 pointer is unverified | supplement_extended_body.tex:135 "The authors resample runs within tasks, with an additional task-resampling variant in their Appendix A.5" | REPEAT R3-47 (rejected then; now fixable by dropping the unverified pointer) | no | text-fixable | APP |
| R4-38 | minor | CA7 | Rule-one rates come from two kernels (0.2585/0.0155 against 0.257/0.014) | main.tex:203 "the first rule passes in 0.259 at a true 1.244 and in 0.016 at independence" | REPEAT R3-46 | no | REJECTED | none |
| R4-39 | minor | KA11, CA11, AR16 | Rule and protocol commits carry no corroborated timestamp | main.tex:249 "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp." | REPEAT R2-45, R3-07 (KA7) | no | REJECTED | none |
| R4-40 | minor | PA16, AR12 | The contribution list omits the PolyPythias family and has no outcome variants | main.tex:45 "This paper makes four contributions to measuring run covariance." | REPEAT R3-49 | yes | REJECTED | none |
| R4-41 | minor | AR13 | Move the covariance heatmap into the main text | main.tex:157 "(Figure~\ref{fig:covariance} in Appendix~\ref{app:supplementary})" | NEW | no | REJECTED | none |
| R4-42 | minor | AR15 | AI-use statement wording about simulation data | main.tex:243 "including an accurate disclosure of AI involvement in generating simulation data" | NEW | no | REJECTED | none |
| R4-43 | minor | AR exp 7 | A downstream study where covariance changes a real decision | main.tex:222 "the correction removes between 1 and 12 of the 173 to 223 calls on such pairs" | NEW | no | REJECTED | none |
| R4-44 | minor | PA script advisories | Missing `~` before \citet, unreferenced equation labels | main.tex:54 "\label{eq:scores}" | REPEAT R2-48 | no | REJECTED | none |

Totals: 44 findings, critical 2, major 12, moderate 12, minor 18. Dispositions: 31 text-fixable (A 10, B 10, C 5, D 10, APP 9, counting a finding once per slice it touches), 4 NEEDS-EXPERIMENT (all GPU: R4-13, R4-14, R4-19, R4-26), 9 REJECTED.

Rejection reasons, each checked against the tex. R4-12: the abstract (main.tex:29) already carries BoolQ's 68% share and the 1.096 to 1.786 removal range, main.tex:157 opens Sec 4.1 with "The factor belongs to this battery, since margin correlations track scoring format", and R3-13's reason stands. R4-34: the count is the N2 permutation count reported at appendices_bcd.tex:117 ("In the reported 500 permutations"), so it matches an analysis, and the statement lists settings rather than results. R4-38: 0.2585 and 0.257 agree within Monte Carlo error and appendices_bcd.tex:351 names the committed recentring jackknife, as R2-06 and R3-46 chose. R4-39: a hash in the text adds no independent corroboration and a third-party timestamp can't be made retroactive, and main.tex:249 states the gap (author action KA7 from round 3 remains open). R4-40: R3-49's reason stands (main.tex:43 introduces the second family in the paragraph before the list, and adding it costs page-2 length), and after R4-03 the list makes no claim that a PolyPythias outcome could falsify. R4-41: the main text ends on page 9 with no room for a figure. R4-42: the author asked that the AI-use and ethics statements stay as written. R4-43: Sec 4.5 (main.tex:222) is that study on DataDecide's own recipe comparisons. R4-44: cosmetic, as R2-48 found.

New findings rated likely to lower the score: 9 (R4-01, R4-03, R4-05, R4-06, R4-08, R4-10, R4-16, R4-17, R4-18)

### Round 4 outcome, 2026-09-23 04:32 EDT
FIXED 29 of 31 text-fixable (slices A 10, B 9, C 5, D 9, APP 9, some spanning slices); SKIPPED 2 for page length (R4-20, R4-28); NEEDS-EXPERIMENT 4 (all GPU: R4-13, R4-14, R4-19, R4-26); REJECTED 9. Main correction: the round 3 argument that a uniform shared component "would need a share of 1.42, more than the item noise" was circular (reliability.py variance_components defines item noise as within-half variance minus the cross-half diagonal, so a component identical in both halves cannot enter it) and is removed from the abstract, main.tex and appendix; the defence now rests on the cross-format exclusion (1.113 and 1.153 above the 1.035 upper limit, snap-r3-r2-02). R3-21 closed: 17 benchmark, held-out task and OLMES bibitems verified in work/rebuttal/r4/citation_audit.md and cited. Compile clean, 0 undefined references or citations, maintext:end on page 9 in all six outcome combinations. New findings rated likely to lower the score this round: 9 (R4-01, R4-03, R4-05, R4-06, R4-08, R4-10, R4-16, R4-17, R4-18), most regressions from round 1-3 cuts.

## Round 5, started 2026-09-23 04:32 EDT
Pre-round snapshot: fceef7c. Skills run: superpowers:using-superpowers, aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), stop-slop, superpowers:verification-before-completion. No CPU-feasible NEEDS-EXPERIMENT items open. Raw outputs: work/rebuttal/r5/*.md

### Merged findings (round 5)

Merged 2026-09-23 04:50 EDT from work/rebuttal/r5/{kill_argument (KA, codex points P1 to P6), claim_audit (CA), citation_audit (CI), paper_audit (PA), academic_reviewer (AR, questions Q1 to Q6, demanded experiments "demand 1" to "demand 6", text changes "change 1" to "change 3")}.md. Every quote was checked verbatim against deliverables/*.tex at fceef7c (64 of 64 found at the cited line). Context the reviewers lacked: PolyPythias bank one is being scored and bank two is unscored, so the \pending and \outcome scaffolding stays; DataDecide on bank two needs GPU.

The CPU kernel results/snap-r5-shared-bound (garyzhang11111/snap-r5-shared-bound, landed 04:40, observed cross-format values asserted equal to snap-r2-r1-50) settles KA1 and CA2. Under zero cross-benchmark seed covariance the largest uniform share the margin upper limit 1.0347 allows is 0.420, which alone produces 0.319 of the 0.244 excess on the inflation scale (0.295 on the covariance scale); no positive share fits the point estimate, because 0.921 below one already requires negative cross-format seed covariance, and that covariance could offset a larger component; on accuracy the admissible share 0.072 exceeds the explaining 0.053, so the bound doesn't bind. The Lambda that share produces alone (1.0778) stays out of the main text, since it collides with the accuracy estimate 1.078 and is the reviewer's "about 1.08".

KA2 code check: compute extra/heldout/kaggle/k08-seed-count/k08-seed-count.py calls seednoise.simulate.default_spec(rbar_e=...) with no item_sd, so the seed-count population uses the default simulator's item noise (SimSpec item_sd None, which simulate() sets to 10 against unit seed SD) rather than either battery's measured noise. Its accuracy power (0.267 at three runs, 0.64 at six) runs well above the accuracy-noise compound-symmetric run (0.111 at three, 0.196 at six, appendices_bcd.tex:393) and the measured-matrix run (0.103, supplement_extended_body.tex:673), which agree with each other. The main text cites the k08 figures.

Page slack, observed in a scratch build of fceef7c with each of the six (\Ronecase, \Rtwocase) combinations: maintext:end falls on page 9 in all six, followed on page 9 by the AI-use statement and most of the ethics statement (18 to 20 layout lines, about 12 text lines). Slice budgets in the fixer brief total +125 words against that.

Slices, by current line numbers of deliverables/main.tex (preamble 1-27): A 28-45 (abstract 28-30 and introduction 32-45; title at 14 stays), B 46-130 (Sections 2 and 3), C 131-198 (Section 4 up to, not including, sec:family at 199), D 199-241 (sec:family through \label{maintext:end}) plus the reproducibility statement at 248-249; the tail begins at 242 (AI-use statement 242-243 and ethics statement 245-246 stay untouched; 250-256 are the references and appendix inputs). APP is appendix_a.tex, appendices_bcd.tex and references.tex. Fix sketches are in work/rebuttal/r5/FIXER_BRIEF.md.

| id | severity | sources | statement | verbatim quote (file:line) | NEW/REPEAT | likely-lower | disposition | slice |
|---|---|---|---|---|---|---|---|---|
| R5-01 | major | KA1, CA2, AR6 (part), PA2 (part), PA7 (part), results/snap-r5-shared-bound | The cross-format exclusion holds only for a uniform component acting alone with zero run covariance: 0.921 below one already implies negative net cross-format covariance, which could offset a larger component, and even under zero run covariance the upper limit admits a component carrying 0.319 of the margin excess; "cross-format inflation" is also used undefined in the abstract and Sec 2.2 | main.tex:29 "A uniform shared item component producing 1.244 would imply cross-format inflation of 1.113, outside \ci{0.801}{1.035}."; main.tex:71 "would raise inflation from cross-format covariances alone to 1.113, which the observed 0.921 \ci{0.801}{1.035} excludes"; main.tex:235 "would lift cross-format inflation outside its interval"; appendices_bcd.tex:128 "below the 1.113 that a uniform shared item component carrying the whole margin excess would imply"; appendices_bcd.tex:261 "A uniform component shared by every benchmark is therefore excluded on margins by the cross-format diagnostic" | NEW (regression: the R4-01 replacement argument states as an exclusion what holds only for a component acting alone) | yes | text-fixable (numbers from snap-r5-shared-bound) | A, B, C, D, APP |
| R5-02 | major | KA2, CA3, k08 code check | Two accuracy power populations disagree 2.4-fold at the same design and truth, and the main text plans run counts from the one whose item noise is the default simulator's, which overstates accuracy power | main.tex:239 "three runs each let the margin interval exclude one in 0.997 of replicates, and accuracy needs eight to reach 0.803"; appendices_bcd.tex:393 "so four fifths needs between 500 and 1,000 configurations at six runs"; appendices_bcd.tex:456 "On accuracy the share rises from 0.147 at two runs through 0.267 at three" | REPEAT R3-22, R2-36 (fix failed: the populations were labelled but never reconciled, and the R4-27 relabel kept the high-power figure in the main text) | yes | text-fixable | D, APP |
| R5-03 | major | CA1, PA1 (part) | The abstract drops the resolved-pair scope that main.tex:222 and the tab:decision caption keep; over all calls the correction removes 1 to 34 of 221 to 250 (k05-decision/decision_results.json, 530M margins 246 to 212), so the abstract understates it up to about threefold | main.tex:29 "although on DataDecide's recipe comparisons correcting it removes at most 12 of 173 to 223 calls" | NEW (regression from the R4-04 edit) | yes | text-fixable | A |
| R5-04 | major | KA4, KA P2 | The abstract gives only the split value, whose identification the kill memo attacks, and never the assumption-free fixed-bank 1.237 \ci{1.137}{1.331} | main.tex:29 "the ten-benchmark per-byte margin average has 1.244 times its independent standard deviation \ci{1.143}{1.338}" | REPEAT R3-03, R4-09 (residual: stated in Sec 2 and the Discussion, never in the abstract) | yes | text-fixable | A |
| R5-05 | major | KA3, AR2, AR Q1, AR change 2 | The recommended replicate SD needs no split, and the contributions never name the case where the split and the fixed-bank value part (accuracy without BoolQ, 1.285 against 1.558) or say which one to report | main.tex:45 "The battery average's replicate standard deviation answers the fixed-bank question, while the split separates each benchmark's run variance from item noise and defines a target for redrawn banks, untested on DataDecide" | REPEAT R4-02, R3-04 (residual) | yes | text-fixable | A |
| R5-06 | major | PA1, PA2, AR9, AR change 1, AR seat R3 | The abstract carries about twenty numbers, never defines inflation as a quantity, and opens with one sentence joining three claims | main.tex:29 "A run-to-run standard error of a benchmark average that sums per-benchmark variances ignores cross-benchmark covariance, and a margin-scale comparison using it declares a difference in 0.113 of simulated null replicates" | REPEAT R4-11, R3-10, R2-10, R1-07 (fix failed) | yes | text-fixable | A |
| R5-07 | major | AR1, AR demand 2, AR seat R3 | Real recipe decisions barely move while the headline size error is simulated | main.tex:222 "the correction removes between 1 and 12 of the 173 to 223 calls on such pairs, which changes the share of wrong calls by at most 0.009" | REPEAT R1-03, R1-04, R3-08, R4-04, R4-43 (structural; main.tex:33 says where the understatement shows) | yes | NEEDS-EXPERIMENT (CPU, exploratory: observed false-positive rate of independence and corrected SEs on null seed pairs within PolyPythias configurations, from the 63 reduced runs under research/outputs/snap-r12-polypythias; whether those reductions carry what the test needs is unverified); text part REJECTED | none |
| R5-08 | major | KA5, AR4 | The pre-specified held-out test and the plan predictions both failed, and the reviewers want the width argument beside the failure | main.tex:41 "The test fails at its full scope of 225 runs" | REPEAT R4-05, R3-30, R1-11 | yes | REJECTED | none |
| R5-09 | major | AR5, AR Q2 | Rule-one power borrows DataDecide item noise, which may be optimistic for 14M to 70M models | appendices_bcd.tex:351 "item noise from its margin reliabilities with WinoGrande's set to 0.5" | REPEAT R1-19, R2-05, R3-06 (main.tex:203 names the noise source) | yes | NEEDS-EXPERIMENT (CPU, exploratory: rerun the snap-r2-r1-18 simulation with item noise from the 4,755-item PolyPythias transfer reductions) | none |
| R5-10 | major | AR3 | The factor belongs to one battery and one weighting | main.tex:157 "BoolQ, the only benchmark in its format, carries 68\% of the margin covariance trace" | REPEAT R4-12, R3-13, R1-12, R1-13 | yes | REJECTED | none |
| R5-11 | major | AR demand 1, KA P3 | DataDecide never gets the cross-bank check | main.tex:235 "We didn't score the 375 DataDecide runs on the second bank" | REPEAT R4-14, R3-12, R2-14, R1-06 | yes | NEEDS-EXPERIMENT (GPU) | none |
| R5-12 | moderate | PA3, AR5 (part) | Line 43 says a failing verdict only bounds the effect while line 203 counts an estimate below 1.026 against transfer, and an undecided second rule bounds nothing about size | main.tex:43 "so a pass confirms the effect while a failing or undecided verdict only bounds it" | NEW (regression from the R4-06 edit) | yes | text-fixable | A |
| R5-13 | moderate | PA4 | The last sentence of line 203 reads a failing estimate only through its upper limit and then reads the point estimate against 1.026, "one" has three referents, and the "since" clause doesn't support the upper-limit reading | main.tex:203 "a failing estimate is read only through its jackknife upper limit, which bounds inflation in this family, since under independence the middle 90\% of estimates runs from 0.848 to 1.139" | NEW (regression from the R4-07 edit) | yes | text-fixable | D |
| R5-14 | moderate | PA5 | Default and auxiliary runs are used at main.tex:43, :49, :119, :121 and in Table 1 but never defined in the main text, since the round 4 slice B cut removed "DataDecide stops the auxiliary replicates below 1B at 25 percent of the 1B compute budget" | main.tex:43 "A single model family whose replicates mix default and auxiliary runs on different schedules" | NEW (regression from the round 4 slice B length cut) | yes | text-fixable | B |
| R5-15 | moderate | PA11 | "Gain check G5" and "the default simulator" are undefined in the main text, so the sentence reads as an unexplained failed pre-registered check | main.tex:123 "and its gain check G5 failed under the default simulator" | NEW (regression from the R4-08 edit) | yes | text-fixable | B |
| R5-16 | moderate | PA6, CA6 | Sec 2.1 reports fixed-bank and item-noise numbers before the split, the estimator and the intervals exist, and the item-noise shares come from the analytic item-by-run model without saying so | main.tex:63 "On the released bank, the replicate standard deviation of the full-bank average gives inflation 1.237 \ci{1.137}{1.331}" and "On the full battery item noise is 0.037 of the margin diagonal" | NEW (regression from the R2-12, R3-03 and R4-10 edits) | yes | text-fixable | B |
| R5-17 | moderate | AR7, AR Q5 | The checkpoint-confound evidence reads as one uninformative subset because the round 4 slice B cut removed the influence-truncation sentence; appendices_bcd.tex:10 gives Spearman $-0.036$ on margins and 0.001 on accuracy | main.tex:121 "On the 33 configurations that share a final step, margin inflation is 1.082 (\ci{0.121}{1.530})" | NEW (regression from the round 4 slice B cut; the matched-final-checkpoint rescore stays REPEAT R4-13, GPU) | yes | text-fixable | B |
| R5-18 | moderate | PA9, AR12 | Five sentences for four contributions, "fixed-bank question" undefined in the introduction, and "untested on DataDecide" without a referent | main.tex:45 "This paper makes four contributions to measuring run covariance." | NEW (regression from the R4-02 and R4-03 sentence) | yes | text-fixable | A |
| R5-19 | moderate | CI1 | natbib merges the adjacent Clark keys into "(Clark et al., 2018; 2019; ...)", crediting BoolQ to the ARC authors, and one list after WinoGrande reads as nine citations for it | main.tex:117 "\citep{clark2018arc,clark2019boolq,talmor2019commonsenseqa," | NEW (regression from the R4-15 edit) | yes | text-fixable | B |
| R5-20 | moderate | AR6, AR Q3 | Rule two is never simulated at a shared share large enough to produce 1.244 | main.tex:203 "The simulation never tests the rule against a shared component large enough to explain the inflation" | REPEAT R3-05, R4-22 (the text concedes it) | yes | NEEDS-EXPERIMENT (CPU, exploratory: extend snap-r2-r1-18 to the share that reproduces 1.244 on this family's noise and report verdict rates) | none |
| R5-21 | moderate | PA8, KA9 | "Near-nominal" holds for twelve populations without a band-shared run effect, under which coverage falls to 0.821 and 0.580 | main.tex:45 "Algorithm~\ref{alg:snap} gives the measurement recipe with near-nominal intervals" | REPEAT R3-26 (residual), R4-28 (skipped for length; the leverage-corrected sentence stays out) | no | text-fixable (scope only) | A |
| R5-22 | moderate | PA10 | The reproducibility statement lists 500 permutation replicates while the main-text permutation check uses 2,000 | main.tex:249 "500 permutation replicates"; main.tex:159 "Across 2,000 such permutations" | REPEAT R4-34 (its rejection missed the 2,000-permutation main-text check) | no | text-fixable | D (statement) |
| R5-23 | moderate | KA8, AR10, AR Q6 | No independently corroborated timestamp for the rule commits | main.tex:249 "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp." | REPEAT R4-39, R3-07, R2-45 | yes | REJECTED | none |
| R5-24 | moderate | AR8 | Accuracy gives only a bound; put it in practitioner units | main.tex:233 "at accuracy-like item noise this design detects a true ratio of 1.10 in 0.135 of replicates" | REPEAT R3-11, R1-22 | yes | REJECTED | none |
| R5-25 | moderate | AR11 | Prediction needs replicated marginals, which weakens planning with K_eff | main.tex:220 "an operational comparison refitting without held-out marginals separates no model from independence on either scale" | REPEAT R4-18, R1-21 | no | REJECTED | none |
| R5-26 | moderate | AR demands 3 to 6, AR16 | Larger or multi-format battery, matched final checkpoints, held-out loss, and populations above 1B or generative | main.tex:235 "Our populations stop at 1B and at likelihood-scored multiple choice" | REPEAT R4-13, R4-19, R4-20, R4-26 | yes | NEEDS-EXPERIMENT (GPU) | none |
| R5-27 | minor | PA16 | The prediction sentence stacks five modifiers, "our decomposition" is undefined, "six-run" collides with nine PolyPythias seeds, and the result sits inside the recommendation | main.tex:239 "Against one configuration's six-run margin ratio on the 4,755-item three-size PolyPythias transfer runs of Appendix~\ref{app:transport}" | NEW (regression from the R3-16 edit) | yes | text-fixable | D |
| R5-28 | minor | PA12 | "Both quantities ... can rise" is ambiguous and wrong for K_eff, and $\sigma_{\mathrm{agg}}$ is first used here and defined only in the Table 1 caption | main.tex:91 "Because both quantities normalise by the battery's own trace, they can rise" | NEW | no | text-fixable | B |
| R5-29 | minor | PA13 | $N$ is undefined in the main text | main.tex:86 "where $\Sig=N^{-1}\sum_c\Sigma_{E,c}$ is the configuration-averaged covariance matrix" | NEW | no | text-fixable | B |
| R5-30 | minor | PA14 | Reliability, the stated reason for the primary scale, is undefined in the main text | main.tex:37 "with per-benchmark reliability averaging 0.652 against 0.324 for accuracy" | NEW | no | text-fixable | A |
| R5-31 | minor | PA15 | "Group" is undefined in the main text | main.tex:159 "reshuffles each run's item deviations inside every group" | NEW | no | text-fixable | C |
| R5-32 | minor | PA17 | "Batch slot" is undefined and the phrase misparses | main.tex:237 "A permutation test that aligns runs by batch slot bounds that effect" | NEW | no | text-fixable | D |
| R5-33 | minor | PA18 | "Seed covariance" and "run covariance" drift although auxiliary schedules add variation beyond the seed | main.tex:220 "fitting the seed-covariance models off fold"; main.tex:237 "0.044 of the seed covariance on margins" | NEW | no | text-fixable (only in sentences a slice already touches) | D |
| R5-34 | minor | PA19 | "whose" attaches to 1B or the checkpoints instead of the test | main.tex:41 "on the same checkpoints at 530M, 750M, and 1B, whose rule requires" | NEW | no | text-fixable | A |
| R5-35 | minor | PA20 | The abstract's recommendation differs from main.tex:239's | main.tex:29 "We recommend reporting paired replicate scores with a benchmark-removal check." | NEW | no | text-fixable | A |
| R5-36 | minor | PA21 | "Rank-one plus gain" leaves gain undefined | main.tex:220 "On margins the rank-one, rank-one plus gain, and full models" | NEW | no | text-fixable | D |
| R5-37 | minor | PA22 | The accuracy cut list omits cuts that also exclude one (five recipe deletions, WinoGrande removal, the 0.0867 BoolQ weight) | main.tex:233 "Exploratory cuts whose intervals exclude one, without BoolQ at 1.558" | REPEAT R2-47, R3-34 (residual) | no | text-fixable | D |
| R5-38 | minor | CI2 | The citations credit the multiple-choice format to the DROP and CoQA dataset papers | main.tex:41 "and multiple-choice DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa}" | NEW (from the R4-15 edit) | no | text-fixable | A |
| R5-39 | minor | CA4 | Margins are stored as float16 (seednoise/store.py), so the sign-accuracy gap comes from items whose stored margin is zero, which includes float16 underflow as well as exact ties | appendices_bcd.tex:142 "a gap that only items with a margin of exactly zero can produce" | NEW (regression from the R4-29 edit) | no | text-fixable | APP |
| R5-40 | minor | CA7 | 0.935 and 0.898 belong to the size-clustered $t$ interval (simulation_cells.csv cluster_t_size, pooled 0.9348 and 0.8983); the recipe-clustered $t$ falls with the wild interval | appendices_bcd.tex:389 "while the cluster-robust $t$ interval holds 0.935 and 0.898" | NEW | no | text-fixable | APP |
| R5-41 | minor | KA11 | "All of its neighbourhood" claims more than 2,000 near-flat draws show | appendices_bcd.tex:204 "The conclusion on margins holds across four fifths of the simplex and all of its neighbourhood." | NEW | no | text-fixable | APP |
| R5-42 | minor | AR13 | A classical split-half estimator reads as incremental | main.tex:228 "what we add is the estimand, run covariance across benchmarks at a fixed configuration" | REPEAT R3-14, R2-13, R1-23 | yes | REJECTED | none |
| R5-43 | minor | AR15, AR change 3 | Scattered post-hoc admissions read as an audit log; asks for one deviations table | appendices_bcd.tex:253 "We picked it after seeing the first four cells." | REPEAT R3-10, R1-37 | no | REJECTED | none |
| R5-44 | minor | KA6 | Title broader than the evidence | main.tex:14 "\title{Estimating Run-to-Run Covariance\\Across Language Model Benchmarks}" | REPEAT R3-45, R1-02 | no | REJECTED | none |
| R5-45 | minor | KA7 | The abstract's accuracy interval drops the scored-checkpoint condition | main.tex:29 "The accuracy interval \ci{0.993}{1.157} includes one, at 0.135 power against a true 1.10." | REPEAT R3-09, R1-15, R1-28 | no | REJECTED | none |
| R5-46 | minor | KA10 | A borrowed ratio holds nominal size only within about 0.05 of its source | main.tex:239 "Scaling the independence standard error by a ratio from the same margin population returns the simulated false-positive rate from 0.113 to 0.051." | NEW | no | REJECTED | none |
| R5-47 | minor | CA5 | One paragraph mixes two simulation runs (r1_18b and r1_18) | main.tex:203 "under independence the middle 90\% of estimates runs from 0.848 to 1.139" | REPEAT R4-38, R3-46 | no | REJECTED | none |
| R5-48 | minor | CA8 | PolyPythias present tense and "before scoring of either bank began" read as work done | main.tex:129 "committed to the repository before scoring of either bank began" | REPEAT R3-02 | no | REJECTED | none |
| R5-49 | minor | CI3 | The supplement's shared bibliography lists 17 entries it doesn't cite | supplement_extended.tex:28 "\input{references.tex}" | NEW | no | REJECTED | none |
| R5-50 | minor | AR14 | AI-use statement wording about simulation data | main.tex:243 "including an accurate disclosure of AI involvement in generating simulation data" | REPEAT R4-42 | no | REJECTED | none |
| R5-51 | minor | PA script advisories | Citation ties and unreferenced equation labels | main.tex:54 "\label{eq:scores}" | REPEAT R4-44 | no | REJECTED | none |

Totals: 51 findings, critical 0, major 11, moderate 15, minor 25. Dispositions: 31 text-fixable (A 12, B 8, C 2, D 9, APP 5, counting a finding once per slice it touches), 5 NEEDS-EXPERIMENT (CPU, all exploratory: R5-07, R5-09, R5-20; GPU: R5-11, R5-26), 15 REJECTED.

Rejection reasons, each checked against the tex. R5-07 (text part): main.tex:33 already says the understatement shows in one model's error bar and in run planning rather than in recipe decisions, and main.tex:222 reports the decision study. R5-08: R3-30 removed width framing beside the failure as arguing it away, R4-05 put the same-scope comparator 1.240 \ci{1.054}{1.397} into the abstract and introduction, and Table 2 prints the four-benchmark subset row. R5-10: R4-12's and R3-13's reasons stand (abstract and main.tex:157 state the battery dependence), and moving the Dirichlet result into the main text costs page 9. R5-23: R4-39's reason stands; a hash adds no independent corroboration, and the third-party timestamp remains the author's out-of-loop action. R5-24: main.tex:39, :134 and :233 already give the upper limit 1.157 and K_eff 7.47 at that limit. R5-25: main.tex:220 says covariance models beat independence only with held-out marginal variances, and main.tex:239 gives the no-replicate fallback as untested. R5-42: main.tex:226 and :228 already rest the novelty on the estimand and its measurement. R5-43: a deviations table would rewrite dozens of appendix sentences, the change class that produced most round 3 and 4 regressions. R5-44: R3-45's reason stands. R5-45: the abstract's third sentence scopes every DataDecide value to each configuration's last shared checkpoint. R5-46: the sentence already names a ratio "from the same margin population", and main.tex:157 and Algorithm 1 step 7 say the factor belongs to the battery. R5-47: R4-38's reason stands (Monte Carlo agreement, source named in appendices_bcd.tex:351). R5-48: bank one scoring is under way, so the present tense and "before scoring of either bank began" are accurate, and rule 3 of the brief governs. R5-49: extra uncited entries in the internal supplement's bibliography mislead no reader. R5-50: the author asked that the AI-use and ethics statements stay as written. R5-51: cosmetic, as R4-44 found.

New findings rated likely to lower the score: 11 (R5-01, R5-03, R5-12, R5-13, R5-14, R5-15, R5-16, R5-17, R5-18, R5-19, R5-27)

### Round 5 outcome, 2026-09-23 05:02 EDT
FIXED 29 of 31 text-fixable (slices A 12, B 8, C 2, D 7, APP 5, some spanning slices), with R5-28 fixed in part (the sigma_agg definition clause skipped for length); SKIPPED 2 for page length (R5-36, R5-37); NEEDS-EXPERIMENT 5 (CPU, exploratory: R5-07, R5-09, R5-20; GPU: R5-11, R5-26); REJECTED 15. The shared-component defence now says "acting alone" and cites the snap-r5-shared-bound share 0.420 and 0.319 of the excess. No text added in rounds 1 to 4 was cut, per the round 5 brief. Slice B runs 21 words over its cap, and the page check absorbs it. Compile clean with 0 undefined references or citations, no em or en dashes, and maintext:end on page 9 in all six outcome combinations. New findings rated likely to lower the score this round: 11 (R5-01, R5-03, R5-12, R5-13, R5-14, R5-15, R5-16, R5-17, R5-18, R5-19, R5-27).

## Round 6, started 2026-09-23 05:31 EDT
Pre-round snapshot: 73277c2 (tree clean, so "pre-round snapshot" made no new commit). Skills run: superpowers:using-superpowers, aris:kill-argument, aris:paper-claim-audit, aris:citation-audit, paper-audit, academic-research-skills:academic-paper-reviewer (quick), stop-slop, superpowers:verification-before-completion. Raw outputs: work/rebuttal/r6/*.md

### Merged findings (round 6)

Merged 2026-09-23 05:52 EDT from work/rebuttal/r6/{kill_argument (KA), claim_audit (CA), citation_audit (CI), paper_audit (PA), academic_reviewer (AR)}.md. Panel estimates: academic reviewer mean 4.4 under rule-one fail and 5.2 under pass; kill-argument 5 (about 6 on a pass, 4 on a fail). Every round 5 number the claim audit traced matched its file. Page slack measured at 73277c2 by appending filler to main.tex:242: maintext:end stays on page 9 in all six outcome builds with 80 filler words and moves to page 10 in two builds at 110, so this round's net main-text budget is about +55 real words.

| ID | Sev | Sources | Location | Finding | Likely to lower score | Disposition |
|---|---|---|---|---|---|---|
| R6-01 | major | PA1, CA1, KA1, AR4 | main.tex:29, :71, :235; appendices_bcd.tex:261 | "Acting alone" reads as "sole cause", which makes "at most about a third" self-contradictory; the bound's real premise is zero cross-format run covariance; the abstract drops the offset caveat and leaves "inflation across scoring formats" and "leaves" an interval unresolved | yes (new, round 5 regression) | text: A, B, D, APP |
| R6-02 | moderate | PA2, KA2, AR3, CA7, AR8 | main.tex:45, :216 | "the two part" misparses; 1.285 and 1.558 unlabelled; bare 1.285 collides with the format-fit 1.285 | yes (new, round 5 regression) | text: A, D |
| R6-03 | moderate | PA3 | main.tex:123 | the new G5 definition makes the failed check read as a gain explaining over half the excess, without the matched simulator's six percent (appendices_bcd.tex:62) | yes (new, round 5 regression) | text: B |
| R6-04 | moderate | AR1 | main.tex:43, :29 fail branch, :203 | the introduction presents the rule-one failure reading as design although main.tex:203 says it was added after the rule was fixed; the abstract fail branch gives a design clause and no verdict | yes (new) | text: A |
| R6-05 | moderate | PA4, KA3 | main.tex:239 | "the default simulator" returns undefined in the planning sentence | no | text: D |
| R6-06 | moderate | PA5 | main.tex:43 | the rules sentence gives power for rules the introduction never describes; "the shared-item question" has no antecedent; 0.761 loses its no-shared-component condition | no | text: A |
| R6-07 | moderate | CA2 | main.tex:45 (iii) | "near-nominal intervals unless a run effect follows the size band" names one failure mode as the only one (appendices_bcd.tex:391 lists item noise 3.00, five recipes, noise ramp) | no | text: A |
| R6-08 | moderate | AR2 | main.tex:71, :129, :201 | "tests it" overclaims whether a template-tied component is reachable; whether bank two shares bank one's prompt templates is not stated or recorded in the manifest | no | text: B (wording only; template identity unverified) |
| R6-09 | minor | KA4, AR6, PA12 | main.tex:239, :241 | main text ends on an uninterpreted result where SNAP loses to independence; "the plug-in" and "item noise added to both sides" undefined; "margin ratio" then accuracy errors | no | text: D |
| R6-10 | minor | KA5, PA10 | main.tex:29 | "the correction", "calls" and "resolved 1B ordering" undefined in the abstract | no | text: A |
| R6-11 | minor | PA6 | main.tex:203 | 0.124 orphaned | no | text: D |
| R6-12 | minor | PA7 | main.tex:203 | 75-word sentence with ambiguous "that range" | no | text: D |
| R6-13 | minor | PA8, CA9 | main.tex:121 | Spearman -0.036 printed against "truncation", while the appendix correlates with the selected step's share of the default final step | no | text: B |
| R6-14 | minor | PA9, CA8 | main.tex:251 | "500 and 2,000 permutation replicates for the two permutation checks" miscounts | no | text: D (reproducibility statement) |
| R6-15 | minor | PA11 | main.tex:45 (iv) | "it" points at the algorithm | no | text: A |
| R6-16 | minor | PA13 | main.tex:49, :121, :205 | "batch component" undefined in the main text | no | text: B |
| R6-17 | minor | CA3 | main.tex:237 | 0.044 "bounds" omits the appendix's anti-conservative caveat | no | text: D |
| R6-18 | minor | CA4 | main.tex:37; appendices_bcd.tex:34 | reliabilities 0.652 and 0.324 are one-half values | no | text: A, APP |
| R6-19 | minor | CA5 | main.tex:157 | 0.624 and 0.007 exclude WinoGrande (negative seed variance) | no | text: C |
| R6-20 | minor | CA6 | appendices_bcd.tex:204 | flat and near-flat Dirichlet sweep figures have no result file (R2-20 open since round 2) | no | NEEDS-EXPERIMENT (CPU) |
| R6-21 | minor | CA10 | appendices_bcd.tex:261 | 1.153 is the uniform-contribution reference, printed as a second shared-component value | no | text: APP |
| R6-22 | minor | KA6 | main.tex:71, :157 | positive mean cross-format correlation beside net negative cross-format covariance, unexplained | no | text: B (only from numbers already printed) |
| R6-23 | minor | AR5 | main.tex:237 | coverage of the size-band-clustered interval not given in the main text | no | text: D, lowest priority |
| R6-24 | minor | AR7 | main.tex:29 R2-supported branch | branch does not say the within-bank value can overstate run covariance | no | text: A (inside branch) |
| R6-25 | minor | AR9 | main.tex:192 | "0.982--1.476" renders an en dash | no | text: C |
| R6-26 | moderate | CI1 | main.tex:41, :175; appendices_bcd.tex:399 | Gen2MC multiple-choice DROP and CoQA (LLM-written distractors) unattributed; Olmo 3 bibitem VERIFIED by this round's citation audit | no | text: APP |
| R6-27 | low | CI2 | references.tex karamcheti2021 | title case | no | text: APP |
| R6-S | major | AR-S1 to AR-S6, KA strongest argument | structural | replicate SD needs no split; confirmatory record failed or underpowered; no DataDecide bank-two check; checkpoint confound; battery dependence; accuracy only a bound | repeats of logged items, not new | NEEDS-EXPERIMENT (GPU: R1-06/R5-11, R4-13, R5-26; CPU exploratory: split-versus-replicate decision case) or REJECTED as in R3-13 to R5-10 |

New findings rated likely to lower the score: 4 (R6-01, R6-02, R6-03, R6-04), all text-fixable and three of them regressions from round 5 edits.

### Round 6 outcome, 2026-09-23 05:47 EDT
FIXED 22 of 26 text-fixable (R6-01 to R6-05, R6-08 to R6-19, R6-21, R6-23, R6-25 to R6-27; slices A 6, B 5, C 2, D 9, APP 5, some spanning slices); SKIPPED 4 for page length (R6-06, R6-07, R6-22, R6-24); NEEDS-EXPERIMENT: R6-20 (CPU, Dirichlet sweep source, open since R2-20) and the structural repeats under R6-S (GPU: R1-06/R5-11, R4-13, R5-26; CPU exploratory: a decision where the split and the replicate SD disagree); REJECTED none this round. Slice D found that "the plug-in" at the prediction paragraph is the three-run estimate (snap-r12-predict-pooled.py:56-69), so it used that wording instead of the reviewer's. Olmo 3 (olmo2025olmo3) added at appendices_bcd.tex:399, verified by this round's citation audit. Every slice ended at its word cap, so the main text has no measured slack left. Compile clean with 0 undefined references or citations, no em or en dashes, and maintext:end on page 9 in all six outcome combinations. New findings rated likely to lower the score this round: 4 (R6-01, R6-02, R6-03, R6-04).
