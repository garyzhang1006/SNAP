# Round 3 academic reviewer, QUICK mode (ICLR simulation)

Source: `deliverables/main.tex` with `appendix_a.tex` and `appendices_bcd.tex`, read in full. Fresh context, and I did not read REBUTTAL_LOG.md or r1/r2. I judged the design only, treating `\pending` fields and outcome variants as intended. Read-only, no compute.

Execution provenance: all seats below are personas that one model ran in one context, so they are role-separated and not independent reviews. Criteria binding was unavailable (`criteria_binding_unavailable`), so seats use general ICLR reviewing norms. NOT_CALIBRATED.

## Phase 0 field card

The paper sits in ML evaluation methodology and applied statistics, where it estimates the run-to-run covariance of benchmark scores. It uses a split-half moment estimator with wild cluster bootstrap-t inference, based on released DataDecide item scores (375 runs, 150M to 1B) plus PolyPythias and a pre-specified held-out battery. The likely ICLR area is "datasets and benchmarks" or "evaluation", and the draft is mature, being dense, heavily audited and past several revision rounds.

## Seats and scores (ICLR 1/3/5/6/8/10)

| Seat | Persona | Score | Confidence | One-line verdict |
|---|---|---|---|---|
| R1 | Statistician (variance components, cluster inference) | 6 | 4 | Careful, honest estimator with calibrated inference, but identification stays open in the headline family |
| R2 | LLM evaluation practitioner (benchmarks, seeds) | 5 | 4 | The measurement is real, but the paper shows almost no decision a practitioner would change |
| R3 | Generalist ML reviewer | 5 | 3 | Hard to read, modest novelty and a small-model scope, though the rigor is plain to see |
| R4 | Devil's advocate | 3 | 4 | Both registered generalisation checks fail or are built to be uninformative, and the headline factor is a BoolQ artefact of one battery |
| AC | Journal-fit / meta | lean reject (borderline) | n/a | The rigor is credited, but the significance case is unmade and the density hurts |

Mean 4.75, which lands in the borderline-reject band for ICLR.

### R1, statistician (6, conf 4)
Strengths: the estimand is stated precisely (main.tex:63-91), finite-sample and ratio bias are acknowledged, and coverage is checked across twelve populations plus band-shared and recipe-shared effects. It is also unusually candid about post hoc choices.
Top weaknesses: the shared-item component that would reproduce 1.244 at a 0.124 share has not been measured on DataDecide (AR4); coverage shortfalls to 0.928, and to 0.823 under band sharing, sit beside the word "calibrated" (AR10); and the shipped interval is not the best-covering one that the authors themselves found (appendices_bcd.tex:253).

### R2, evaluation practitioner (5, conf 4)
Strengths: this is the first cross-benchmark covariance measurement of pretraining-run noise, and the recommendation (paired replicates plus a removal check) is sensible.
Top weaknesses: the decision-level effect is at most 0.009 in the wrong-call share, with every interval reaching zero (AR1). If you have replicates, direct SD already gives 1.237, and if you don't, the ratio doesn't transfer (AR2). Accuracy, which is the scale people report, stays unresolved (AR6).

### R3, generalist (5, conf 3)
Strengths: it takes seed noise seriously, and it has pre-specified tests with released artefacts.
Top weaknesses: the abstract and results read as an audit log, with about twenty numbers and conditional clauses (AR7). The novelty over split-half and generalizability theory is stated in one clause (AR13). The scope stops at 1B and at likelihood-scored multiple choice.

### R4, devil's advocate (3, conf 4)
Strongest counter-argument: the headline 1.244 describes one ten-benchmark battery at mid-training checkpoints and moves from 1.096 to 1.786 when one benchmark is removed. The registered test on unseen tasks fails. The PolyPythias replication passes only 0.259 of the time even if the effect is real, and the identification check returns "undecided" in 0.76 to 0.96 of simulated worlds under either explanation. An item-level component at 0.124 of item-noise variance, never measured in DataDecide, would produce the whole margin result. And when the correction is applied to real recipe decisions it changes almost nothing. What remains is a careful measurement whose transferable content is "compute the SD of your own battery average across seeds", which practitioners with replicates already can do.
DA CRITICAL candidates: AR3 and AR4. I adjudicate both as MAJOR rather than CRITICAL, because the paper discloses both limits in the text (main.tex:205, main.tex:237). They still cap the score.

## Findings

| ID | Severity | Lowers score? | Verbatim quote (file:line) | Objection | Fix (text only unless marked) |
|---|---|---|---|---|---|
| AR1 | Major | yes | "which changes the share of wrong calls by at most 0.009" (main.tex:224) | The only real-decision test shows no practical effect, so the significance claim of the intro ("weakens a comparison's error control", main.tex:33) has no empirical instance on real comparisons. | Scope the claim in the intro and abstract to reported standard errors and replicate planning. Say plainly that recipe rankings at 150M to 750M barely move, and explain why (gaps far exceed seed SD). |
| AR2 | Major | yes | "helps only where replicates are missing and the target battery's own ratio is close" (main.tex:241); "the replicate standard deviation of the full-bank average gives inflation 1.237" (main.tex:63) | Given replicates, direct SD of the average gives the same answer. Without them, the ratio fails to transfer. Reviewers will ask who uses SNAP. | Add one intro paragraph naming the use cases the paper supports: diagnosing which benchmark blocks co-move (the format structure), checking the independence assumption inside item-level SE methods such as Miller (2024), and replicate-count planning (main.tex:241 last sentence). |
| AR3 | Major | yes | "Over 4,000 replicates the first rule passes in 0.259 at a true 1.244 and in 0.016 at independence" (main.tex:205) | Both PolyPythias rules were designed so that the most likely outcome is uninformative. A fail on R1 or an undecided R2 then adds little, and a reviewer reads it as a weak design. | Put the pre-computed power of each rule in the intro sentence that introduces the rules (main.tex:43), so every outcome variant reads against its known power. Frame the rules as bounds rather than replications. |
| AR4 | Major | yes | "We didn't score the 375 DataDecide runs on the second bank, which leaves the 1.244 untested on fresh items" (main.tex:237) | The headline family's identification is open, and a 0.124 item share reproduces 1.244. | Text can only scope it. Add "identified up to a shared item component" to the abstract sentence carrying 1.244. Experiment demanded (E1). |
| AR5 | Major | yes | "BoolQ, the only benchmark in its format, carries 68\% of the margin covariance trace" (main.tex:159) | The headline Λ rises when BoolQ is removed while σ_agg falls, and the paper itself says to compare batteries via σ_agg. Why is Λ the headline? | Lead with σ_agg against σ_indep for this fixed battery. Present Λ as its normalised form, and put the 1.096 to 1.786 removal range in the same sentence as 1.244 in the intro (main.tex:39). |
| AR6 | Major | yes | "a design that would detect a true ratio of 1.10 in 0.135 of replicates" (main.tex:235) | Accuracy is the reported scale and gets no answer. | State in the abstract that this design cannot resolve accuracy, and turn the seed-count result (eight runs reach 0.803, main.tex:241) into a positive design recommendation. |
| AR7 | Major | yes | "BoolQ carries 68\% of the covariance trace and single-benchmark removals move the factor from 1.096 to 1.786, so batteries compare through the aggregate standard deviation." (main.tex:29) | The abstract carries about twenty numbers and three conditional variants. Results paragraphs interleave audit history ("Two later additions", main.tex:115, and "Every partial scope we read before the full one", main.tex:177), so a reader can't find the claim. | Cut the abstract to about 150 words and five numbers. Move interim-scope history, later-added intervals and amendment detail to the appendix. Open each results subsection with a single sentence giving its claim. |
| AR8 | Minor | yes | "in simulation a comparison using it declares a difference in 0.113 of replicates with no true gap, against a nominal 0.05" (main.tex:29) | The opening number is for margins, and on accuracy it is 0.067 (appendices_bcd.tex:218). A reviewer who finds that will call the abstract's opening number cherry-picked. | Name the margin scale and give 0.067 for accuracy in the same sentence. |
| AR9 | Moderate | yes | "Neither the analysis plan nor the protocol and rule commits carry an independently corroborated timestamp" (main.tex:251) | "Registered" implies third-party timestamping. The plan's own predictions also mostly failed (appendices_bcd.tex:86), and the main text omits this. | Replace "registered" with "pre-specified" throughout, or cite the commit hashes. Add one main-text clause saying that the plan's thresholds of 1.349 and 1.40 were not met. |
| AR10 | Minor | no | "calibrated intervals, whose wild recipe-cluster coverage runs from 0.928 to 0.954" (main.tex:45) | Coverage under band sharing drops to 0.823 (main.tex:239). The leverage-corrected interval covers better and was left unshipped (appendices_bcd.tex:253). | Say "near-nominal under recipe clustering", and give one sentence on why the shipped interval was kept. |
| AR11 | Moderate | yes | "At 750M the default runs stop well short of their released final models" (main.tex:121) | The estimand is run covariance at mid-training steps that are truncated unevenly, and the shared-final-step subset is uninformative (\ci{0.121}{1.530}). | Put "at the largest shared checkpoint, mid-training for 750M" in the abstract's DataDecide sentence. |
| AR12 | Minor | no | "a bar both AGIEval tasks missed by about a thousandth" (main.tex:177) | Two of the four tasks were swapped by a rule that sits inside sampling error. CoQA then drives the held-out estimate (removal gives 1.090, main.tex:199), which invites a forking-paths reading. | Keep the disclosure. Add that the pre-specified original tasks would have been scored under the same rule. |
| AR13 | Moderate | yes | "what we add is the estimand and its measurement" (main.tex:230) | The estimator is a standard cross-half covariance moment ratio, and the novelty against Madaan (2024), Heineman (2025) and Miller (2024) gets one clause. | Give a three-sentence novelty statement that names what each prior work cannot estimate and why paired run effects across benchmarks need the split. |
| AR14 | Minor | no | "the shipped proxy carries no measurable signal about the run it scores" (appendices_bcd.tex:308) | A full appendix audits an analysis that the authors conclude is broken. It reads as residue and draws fire. | Compress it to one paragraph that states the conclusion (a competence adjustment needs held-out loss) and moves the rest to the extended supplement. |
| AR15 | Minor | no | "The author-reported power calculation assumes approximately Gaussian half-score deviations." (appendix_a.tex:103) | Third-person audit register ("author-reported", "the analysis record", "the shipped") in the authors' own paper reads as if another party wrote it. | Rewrite in the first person. |
| AR16 | Minor | no | "(Kaggle CPU kernel snap-r2-r1-49)" (appendices_bcd.tex:375) | A named Kaggle kernel can resolve to an account, which is a double-blind risk. | Remove the kernel identifier, or anonymise it. |

## Reviewer questions

1. If a practitioner has three replicates, what does SNAP give beyond the direct replicate SD of the battery average (1.237 against 1.244)?
2. Why is Λ, which rises when the highest-variance benchmark is removed, the headline, rather than σ_agg relative to σ_indep?
3. What was the a priori power of the held-out rule at the registered scope, and why was a rule with that power adopted?
4. Can you bound the shared-item component on DataDecide without GPU scoring, for example from cross-format pairs, and how tight is the bound from 0.921?
5. How much of the margin covariance comes from checkpoint truncation rather than initialisation and data order, given that the 750M band sits at 41.5% of the final step?
6. Would any published comparison in the DataDecide or OLMo papers flip under the corrected SE?

## Three text-only changes that most raise the mean

1. Reframe the significance around who uses the result (AR1, AR2, AR5). Lead with σ_agg for the fixed battery and name the three use cases (block structure diagnosis, checks on independence assumptions, replicate planning). State plainly that rankings at this scale barely change. This answers R2's and R4's main objection. Expected lift: R2 5 to 6, and R4 3 to 5.
2. Rewrite the abstract and results openings for readability (AR7, AR8, AR15). Use about 150 words and five numbers, name the scale on the 0.113 figure, put one claim sentence per subsection, and move audit history to the appendix. Expected lift: R3 5 to 6.
3. Put power beside every pre-specified rule in the intro, and use "pre-specified" in place of "registered" (AR3, AR9, AR10). The failed and undecided outcomes then read as bounds from checks of known power, which removes the "designed to be uninformative" line of attack. Expected lift: R1 stays at 6 with higher confidence, and R4 gains up to 1.

Projected mean after all three is about 5.75, still borderline, because AR4 and the scope need experiments.

## Experiments reviewers would demand

- E1: score the 375 DataDecide runs on bank two and run the cross-bank rule in the headline family, which settles AR4.
- E2: add a second family at or above 1B with seed replicates and generative or chain-of-thought tasks, or argue with numbers why none exists (appendices_bcd.tex:70 lists the exclusions).
- E3: run a downstream case where the corrected SE changes a published or realistic conclusion, such as checkpoint selection or small-gap ablations at matched scale.
- E4: measure held-out loss at the selected checkpoints (all 375 are reachable, appendices_bcd.tex:314) to separate a competence or gain channel from covariance.
- E5: add more seeds on one DataDecide configuration band, or use the nine PolyPythias seeds on accuracy, to resolve the accuracy bound at the recommended eight runs.
- E6: compare head to head against the naive practice of taking the SD of the battery average across seeds, with a bootstrap over seeds, to quantify what SNAP adds.
