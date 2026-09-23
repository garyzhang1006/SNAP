# Round 4 academic reviewer (quick mode, fresh context)

Source: deliverables/main.tex, appendix_a.tex, appendices_bcd.tex (read in full for main text and Appendix A; Appendix B-D read at design, calibration, transport, held-out, and competence-proxy sections). Line numbers refer to the file named in each row, main.tex unless stated. The \pending placeholders and outcome variants were judged as design only, as instructed. Read-only, no compute run.

## Journal-fit assessment

The paper fits the ICLR datasets-and-benchmarks / evaluation-methodology audience. It is a careful measurement paper on a narrow estimand (cross-benchmark covariance of run deviations) with unusually thorough calibration, and its main risk at ICLR is significance, because the headline effect (margin inflation 1.244, a 24% larger standard deviation) changes almost no real recipe decisions, the pre-specified held-out test fails, and the second-family replication is powered at 0.259. Reviewers who value rigor will land at 6, and reviewers who ask "what changes for a practitioner" will land at 3 to 5.

## Simulated ICLR seats

| Seat | Profile | Score | Confidence | One-line rationale |
|---|---|---|---|---|
| R1 | Statistician / evaluation methodology | 6 | 4 | Estimator is sound and the coverage work is far above the ICLR norm, but the estimand's identification leans on an untested format-following item component. |
| R2 | LLM pretraining and eval practitioner | 5 | 3 | Useful warning about error bars, but the correction moves 1 to 12 of about 200 calls and the paper itself recommends the plain replicate SD for fixed banks. |
| R3 | Novelty and significance skeptic | 3 | 4 | Split-half cross-covariance is classical; the held-out test fails, the replication has 26% power, and the effect is one benchmark (BoolQ) deep. |
| R4 | Reproducibility and benchmark infrastructure | 6 | 3 | Exemplary disclosure, pre-specification, and release plan; density and 43-page length make it hard to verify which numbers carry the claim. |

Mean score 5.0 (confidence-weighted 4.9). Likely outcome: borderline reject, with an AC-level reject risk from R3 unless the rebuttal reframes significance.

## Top weaknesses (ranked)

1. Practical significance is not established. The only real-decision test shows no effect (line 222), and the paper recommends the replicate SD of the battery average for fixed banks (line 239), which leaves the reader asking when SNAP is needed.
2. Generalization evidence is negative or weak by design. The pre-specified held-out test fails (line 41, 173), and the PolyPythias rules pass in 0.259 and return undecided in 0.761 at the true effect (line 43, 203), so the design cannot confirm transfer with good probability.
3. Identification gap in the headline family. A format-following item component is untested in DataDecide and the cross-bank check was not run there (line 71, 235), yet the contribution list claims the target transfers to redrawn banks (line 45).
4. The effect is carried by battery composition. BoolQ holds 68% of the trace, single removals span 1.096 to 1.786 (line 157, 161), and cross-format covariance alone is 0.921 (line 216), so the 1.244 describes format structure in one ten-benchmark battery.
5. Checkpoint confound. 750M is scored at 41.5% of the default final step, and the 33 shared-final-step configurations give \ci{0.121}{1.530} (line 119, 121).
6. Readability. The abstract carries 20+ numbers and three nested outcome macros, and main-text paragraphs routinely hold five or more statistics, which hides the argument.

## Findings table

| id | severity | lowers score | verbatim quote (file:line) | objection | fix |
|---|---|---|---|---|---|
| AR1 | Critical | yes | "the correction removes between 1 and 12 of the 173 to 223 calls on such pairs, which changes the share of wrong calls by at most 0.009" (main.tex:222) | The paper's motivation is error control (0.113 vs 0.05, line 33), but its only real-decision test finds no measurable change, so significance rests on simulation. | State in the intro which decisions the correction matters for (single-model error bars, replicate planning via K_eff) and give one worked example with numbers; present the decision null as scoping, not as a footnote. |
| AR2 | Critical | yes | "For a fixed released bank the replicate standard deviation of the battery average gives the aggregate uncertainty directly, and we recommend reporting it" (main.tex:239) | With fixed-bank inflation 1.237 against the split's 1.244 (line 63), reviewers will read this as the paper conceding its method is unnecessary for the common case. | Add a two-sentence decision rule early in Section 2: use the replicate SD when the bank is fixed and R is at least 3; use SNAP when planning R, redrawing items, or needing per-benchmark run variances; say what each costs. |
| AR3 | Major | yes | "Unlike the battery average's replicate standard deviation, this target transfers to redrawn banks and separates run variance from item noise." (main.tex:45) | Transfer to redrawn banks is untested in DataDecide: "leaves the 1.244 untested on fresh items" (line 235). Claim exceeds evidence. | Rewrite as "is defined to transfer to redrawn banks under the measurement model, which Section 4.3 tests in PolyPythias only". |
| AR4 | Major | yes | "in simulation the first passes in only 0.259 of replicates at a true 1.244 and the second returns undecided in 0.761, so we read both as bounds" (main.tex:43) | A replication designed with 26% power is a weak design; "read as bounds" is undefined for a pass/fail rule, and the bound reading at line 203 was added after the rule. | Say plainly that R1 can confirm but cannot refute at this power, report the jackknife upper limit as the quantity of interest in every variant, and label the 1.026 reading post hoc in the main text, not only in the rule paragraph. |
| AR5 | Major | yes | "The test fails on all 225 runs, where held-out inflation is 1.217 \ci{0.872}{1.498}" (main.tex:41) | Honest, but the intro gives the failure no interpretation until Section 4.2, so a skim reader sees a failed test with no context. | In the same intro paragraph add that the point estimate matches the original ten at that scope (1.240) and that the four-task battery-size curve fails the same rule in 0.43 to 0.45 of subsets (Table 8), so failure reflects battery size and power more than absence of effect. |
| AR6 | Major | yes | "a component that follows scoring format is untested in DataDecide, and Section~\ref{sec:family}'s cross-bank rule tests it in PolyPythias" (main.tex:71) | The headline family is exactly where the identification check was not run; the R2 simulation never tests a component large enough to explain the effect (line 203). | State this limit in the abstract's final sentences and in the contribution list, and commit in text to what the headline would become under the R2-supported variant. |
| AR7 | Major | yes | "BoolQ, the only benchmark in its format, carries 68\% of the margin covariance trace" (main.tex:157) | One benchmark dominating the trace, with removals spanning 1.096 to 1.786, makes 1.244 a battery property with little portability; R3 will call it a BoolQ artifact. | Lead Section 4.1 with the format model (within 0.624, across 0.007, line 216) as the portable finding and give 1.244 as its instance for this battery; move the removal range into the abstract's first two sentences. |
| AR8 | Major | yes | "On the 33 configurations that share a final step, margin inflation is 1.082 (\ci{0.121}{1.530})" (main.tex:121) | Only checkpoint-clean subset is uninformative; 750M runs at 41.5% of final step mix training stages across replicates. | Add one sentence saying which result a reviewer should trust most (the auxiliary contrast 1.256, whose runs sit near final steps) and why, before listing the subsets. |
| AR9 | Major | yes | "We never drew the analysis plan's split of eight screening and seventeen estimation recipes, so every choice in the primary analysis could see all 125 configurations" (main.tex:123) | Combined with the failed planning predictions (plan thresholds 1.349 and 1.40, appendices_bcd.tex:68, 377) that appear only in the appendix, reviewers may find the main-text framing selective. | Add one main-text sentence: the plan predicted margin above 1.349 and accuracy above 1.40, neither was reached under any of the 1,081,575 estimation subsets. |
| AR10 | Major | no | "The pooled in-sample fit ... The repair we fixed before seeing its output ... gives margin inflation of 0.731 with interval 0.673 to 0.784" (appendices_bcd.tex:308) | A competence adjustment that drives inflation below one is a striking result absent from the main text; a reviewer who finds it will ask whether the inflation is a general-competence factor. | One main-text sentence: competence proxies built from the benchmark scores remove covariance by construction (simulations reproduce 0.745), so mediation needs held-out loss, which is reachable for all 375 runs. |
| AR11 | Minor | yes | "A run-to-run standard error for a benchmark average built from per-benchmark variances ignores covariance between benchmarks, and in simulation a margin-scale comparison using it declares a difference in 0.113 of null replicates" (main.tex:29) | Abstract carries more than twenty numbers and nested outcome text; reviewers form their score from it. | Cut the abstract to the problem, the estimator, 1.244 with interval, the BoolQ range, the held-out failure, and the PolyPythias verdict; move 0.135 power, the uniform-share bound, and the accuracy interval to the intro. |
| AR12 | Minor | yes | "Section~\ref{sec:family} reports that margin inflation there is \pending{R1 lambda} ... and that the shared-item explanation is \outcome{\Rtwocase}{1}..." (main.tex:43) | Under R1 fail plus R2 supported the intro, abstract, and discussion must all shift; the variants exist, but the contribution list (line 45) has no variant and would overclaim. | Add outcome variants to the contribution paragraph, or phrase it outcome-neutrally. |
| AR13 | Minor | no | "Figure~\ref{fig:covariance} in Appendix~\ref{app:supplementary}" (main.tex:157) | The covariance heatmap is the most persuasive single visual for the format story and sits in the appendix. | Move it into the main text if space allows under the selected outcome, or merge it as a panel of Figure 1. |
| AR14 | Minor | no | "the two kinds of pair have paired-difference deviations within a factor of 0.928 to 1.025" (main.tex:222) | Unclear quantity; reads as a ratio range with no reference. | Name the ratio (seed-matched over seed-unmatched SD of paired differences). |
| AR15 | Minor | no | "including an accurate disclosure of AI involvement in generating simulation data" (main.tex:243) | Ambiguous; can read as AI having generated data, which some reviewers flag. | Say the simulations were generated by author-run code, with AI assistance in writing that code. |
| AR16 | Minor | no | "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp." (main.tex:249) | Weakens every "fixed before scoring" claim in the paper. | Point to git commit hashes and any external push record (e.g. a public mirror or OSF upload) that dates the rule commits, if one exists. |

## Reviewer questions (expected)

1. When should a practitioner compute SNAP rather than the replicate SD of the battery average, and what error does using the plain SD cause in that case?
2. Is 1.244 a property of DataDecide or of the MC/cloze/yes-no format mix, and would a battery with no BoolQ-like singleton format show the same excess?
3. Why was the second-family replication designed at 0.259 power, and what would have been required for 0.8?
4. Can seed-driven data-order effects be separated from initialisation effects here, and do they carry different covariance?
5. Does the held-out failure reflect power (four benchmarks, 1,000 items) or absence of the effect, and what does Table 8's four-benchmark curve imply for that?
6. How does the 750M truncation interact with the estimate, given that the only clean subset is uninformative?
7. Does inflation grow or shrink with model size across 150M to 1B, and what is the trend's interval?

## Three text-only changes that would most raise the mean

1. Resolve the significance tension (AR1, AR2): a short decision rule in Section 2 and a worked example converting 1.244 into an error bar and a replicate count, with the decision null framed as a scoping result. Expected gain: R2 +1, R3 +1.
2. Recenter the finding on format structure (AR7, AR13): lead with the within-format 0.624 against cross-format 0.007 as the portable result and 1.244 as this battery's instance, with the BoolQ range in the abstract. Turns R3's "BoolQ artifact" attack into the paper's stated thesis. Expected gain: R1 +0 to +1, R3 +1.
3. Close the claim-evidence gaps (AR3, AR6, AR9, AR12): hedge "transfers to redrawn banks", state the untested DataDecide identification in the abstract, surface the failed planning predictions in one sentence, and make the contribution list outcome-aware. Removes the easy credibility hits a skeptical seat will cite. Expected gain: R1 +0 to +1, R4 +0 to +1.

Projected mean after all three: about 5.75 to 6.0.

## Experiments reviewers would demand

1. Score the 375 DataDecide runs on bank two and run the cross-bank rule in the headline family (flagged by the paper itself at line 235).
2. Score DataDecide runs at their final checkpoints, or at least the 750M default runs at matched late steps, to remove the truncation confound.
3. A larger or independent replicate population: train or source matched multi-seed runs at 1B or above, ideally separating initialisation and data-order seeds.
4. A held-out battery large enough for the rule to have power, e.g. eight or more tasks, or all five sizes, with a power calculation reported beforehand.
5. Held-out loss on the same checkpoints (reachable for all 375 runs per appendices_bcd.tex:316) to test whether a general-competence factor mediates the covariance.
6. Generative or instruction-tuned evaluations, or an argument for why the MC-likelihood result bounds them.
7. A downstream-impact study where covariance changes a decision, such as a benchmark-average leaderboard with replicate runs, to back the 0.113 simulated false-positive rate with an observed case.
