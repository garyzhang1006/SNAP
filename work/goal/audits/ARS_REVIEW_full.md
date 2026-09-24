# ARS academic-paper-reviewer, full mode, 2026-09-24

Target: deliverables/main.tex at commit efd93ad, real build (rule one filled as a fail, rule two pending).
Execution provenance: all five seats and the synthesis were written in one session by one model (Claude Opus 5.5), in sequence, with no agents and no cross-model reviewer. The seats saw each other's output only in the sense that one model wrote all of them, so this panel has correlated errors and isn't independent. Criteria binding is unavailable (no ReviewTargetContext), so the venue reading below is the reviewer's own reading of the ICLR 2027 call and reviewer guide.

## Phase 0, configuration

Field: ML evaluation methodology, with a statistics core (variance components, few-cluster inference) and an empirical study on released pretraining runs. Paradigm: quantitative, observational reanalysis plus two small pre-registered tests. Maturity: complete draft, heavily revised.

- Journal-Fit Reviewer: an ICLR area chair for datasets and benchmarks, who asks whether the result changes practice.
- R1 Methodology: a statistician who works on clustered bootstrap and variance components.
- R2 Domain: an LLM-evaluation researcher who knows DataDecide, OLMES, Heineman et al. and Madaan et al.
- R3 Perspective: a psychometrician (generalizability theory) who reads ML papers.
- DA: fixed Devil's Advocate.

## Seat 1, Journal-Fit Reviewer

Fit is acceptable, since ICLR takes evaluation-methodology papers, and the question (whether error bars on benchmark averages understate run noise) matters to anyone who reports a battery mean.

Significance is the problem. The paper's own practical finding is that the correction "changes few of DataDecide's recipe orderings" (abstract, and Section 4.5 with at most 0.009 change in wrong-call share, all intervals reaching zero). The recommendation it closes on, reporting the replicate standard deviation of the battery average (Section 6), needs neither the estimator nor the split, and practitioners who already have replicates can do it without this paper. What the split adds (per-benchmark run variances net of item noise, a redrawn-bank target) is shown to matter only where item noise is large (1.285 against 1.558 without BoolQ, Section 2.3), and the redrawn-bank target is explicitly untested on DataDecide.

Originality is moderate. The cross-half product estimator is a textbook split-half and repeated-measures construction, as the paper itself says (Section 5), and the new part is the estimand and the measurement on released runs.

Recommendation signal: reject at the main track in its current state, with the paper clearly written and honest about its limits.

## Seat 2, R1 Methodology

Strengths, which are real. The identity in Equation 3 is correct under the stated assumptions, and the paper states those assumptions precisely, including what disjoint item identifiers can't guarantee (Section 2.2). The inference is careful: the wild cluster bootstrap-t over 25 recipes, a coverage study across twelve populations (0.928 to 0.954), a size-band clustered interval that still excludes one (1.030 to 1.426), and deletion checks at recipe, pair, size and benchmark level. Every main-text decimal traces to a result file (833 files, 0 unmatched in the claim trace).

Weaknesses, in order of weight.

1. The confirmatory evidence fails. Both rules fixed before scoring that have been read have failed: the held-out test (1.217, interval 0.872 to 1.498, Section 4.2) and PolyPythias rule one (1.302, interval 0.921 to 1.595). The paper reports both failures honestly, but it leaves the headline 1.244 as an exploratory estimate on the same data that shaped the estimator, and the analysis plan's screening/estimation split was never drawn (Section 3). Its predicted thresholds and G5 also failed.
2. The power of the pre-specified tests was low by design. Rule one passes in 0.259 of simulated replicates at a true 1.244 and rule two returns undecided in 0.761 (Section 4.3). A test with 0.26 power can't carry a confirmatory claim when it fails, and it couldn't have carried much when it passed. The paper says this, but it means the pre-registration adds rigor without adding evidence.
3. Checkpoint confounding. The 750M default runs are scored at 41.5% of their final step, 26 configurations are truncated by more than a factor of 1.5, and the 33 matched-step configurations give a margin interval of 0.121 to 1.530 that can't test the estimate (Section 3). The auxiliary contrast (1.256) helps with the batch component but not with schedule differences.
4. Seed labels are shared across recipes within a size band, and a band-following run effect drops simulated coverage to 0.821 at a quarter share (Section 6). The bound of 0.044 comes from a permutation test the paper itself calls anti-conservative.
5. Scale choice. The primary scale is per-byte margin, which few comparisons in practice use, and the scale people report (accuracy) gives 1.078 with an interval that includes one. The 0.115 size therefore applies to a scale that practitioners rarely test on.

Accuracy checks I ran: size 2{1-Phi(1.96/1.244)} = 0.1151 and 0.069 at 1.078, r_E = 0.0608 and 0.018, K_eff 6.46 and 7.47 at 1.157, and held-out widths 0.626 and 0.343. All of these match the text.

Recommendation signal: major revision at a journal, reject at ICLR.

## Seat 3, R2 Domain

The related work is adequate and correctly attributed, now including Summers and Dinneen (2021), Sellam et al. (2022), Madaan et al. (2024) and the Heineman et al. (2025) recomputation. The positioning claim ("we know of no study that estimates the covariance of run noise between distinct benchmarks") is plausible and suitably hedged, with Jordan (2024) acknowledged as the shifted-test-set exception.

Domain concerns.

1. Population scale. Everything stops at 1B, and PolyPythias at 410M. Reviewers at ICLR 2027 will ask whether a covariance measured on 150M to 1B models on likelihood-scored multiple choice says anything about the 7B+ models and generative evaluations people report error bars for. The paper names this limit (Section 6) but can't address it.
2. The format finding (within-format margin correlation 0.624, cross-format 0.007) is the most interesting result, yet format and content are confounded (Section 4.4), and BoolQ alone carries 68% of the margin trace. The factor is close to a statement about one benchmark in one battery. Removing CommonsenseQA gives 1.096, and removing BoolQ gives 1.786.
3. The operational payoff for a practitioner deciding between data recipes is small (Section 4.5), which undercuts the motivation that DataDecide exists to support.

Recommendation signal: weak reject.

## Seat 4, R3 Perspective

From generalizability theory the construction is familiar, since it is a G-study with runs as the object of measurement and items as a facet, and the paper cites Brennan (2001) and Searle et al. (1992). The contribution to that field is the application, which is useful to ML readers, but the paper would read better to a psychometrician if it named the design as a G-study with a p x (i:h) structure and reported the variance components in that vocabulary, which it partly does in the appendix.

The equicorrelated planning result (three runs let the margin interval exclude one in 0.997 of replicates, while accuracy needs eight runs to reach 0.803) is practical and should be closer to the front, because it is the one recommendation a lab can act on.

Recommendation signal: borderline, leaning reject for ICLR and accept at TMLR.

## Seat 5, Devil's Advocate

Strongest counter-argument. The paper measures a battery-specific factor of 1.244 on one family, driven mostly by BoolQ's trace share and by format clustering, on checkpoints that are partly truncated, and on a scale nobody tests on. Then the two tests it fixed in advance to check that this generalizes both fail, one on new tasks and one on a new family. What survives is an accuracy-scale bound that includes independence and a recommendation (report the replicate standard deviation) that needs none of the machinery. A reader can accept every sentence in the paper and still conclude that the one claim that would change practice, that battery error bars are materially too narrow in general, isn't shown.

Issues.

- CRITICAL (claim-evidence). Both read confirmatory tests failed, so the generality of the headline is unsupported. Location: abstract, Sections 4.2 and 4.3. The paper doesn't overclaim this, so it is a research-level issue and not a writing one.
- MAJOR (significance). The recommendation doesn't depend on SNAP. Location: Section 6 and the abstract's final sentence. The paper partly answers this by listing what the split adds.
- MAJOR (confound). Checkpoint truncation and shared seed labels. Location: Sections 3 and 6. Partly answered with auxiliary contrast and band clustering.
- MINOR (presentation). The abstract carries 11 numbers and three outcome branches, and the main text reads as a dense sequence of robustness checks with little space for the reader to see the one result that matters.

Alternative explanations not ruled out: a checkpoint-schedule effect shared by every configuration (the paper says its check can't see it), and an item effect shared across both halves, which rule two targets but which remains pending.

## Phase 2, editorial synthesis

Consensus across all five seats: the paper is honest, careful and correctly computed, and its central generality claim fails its own pre-specified tests. No seat found a wrong number or an overclaim in the current text.

DA CRITICAL adjudication: validated. It isn't fixable by writing, because it follows from the test results.

Decision: reject at the ICLR 2027 main track. The editorial reading on the ICLR 1-10 scale is 3, with R3 at 5, and this matches the running estimate of 3 to 3.5 in research/SCAN_LOG.md.

Score ceiling. A score of 9 needs a strong-accept reading from a hostile reviewer, which needs (a) the confirmatory tests to pass or a replacement confirmatory result, (b) a population beyond 1B or a generative setting, and (c) a decision-level consequence larger than a change of 0.009 in wrong-call share. None of these is a writing change, and each needs new compute. Writing work can still lift clarity and the reader's first impression. The panel estimates that the best writing-only version sits at 3 to 4, and that honest grading can't put it above 5 without new evidence.

## Revision roadmap (writing-only items that survive the no-compute constraint)

1. Put the planning result (three runs for margins, eight for accuracy) into the contribution list, since it is the most actionable finding.
2. Cut the abstract's numbers and keep the ones a reader needs to act on.
3. Keep every failure statement exactly as it is now.
4. Items needing compute (DataDecide on bank two, larger models) stay listed as limitations and aren't claimed.
