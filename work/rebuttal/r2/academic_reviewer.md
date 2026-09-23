# Round 2 academic reviewer (quick mode, fresh context)

Target: `deliverables/main.tex` with `appendix_a.tex` and `appendices_bcd.tex` (PDF `deliverables/main.pdf`, 42 pages). Read-only; nothing compiled or rerun. REBUTTAL_LOG.md and `work/rebuttal/r1` were not opened. The `\pending` placeholders and labelled outcome variants in "A second family and a disjoint item bank" were judged on design only.

Field card: ML evaluation methodology (LLM benchmark uncertainty), borrowing split-half reliability and quantitative-genetics covariance estimation. Venue: ICLR 2027 main track, plausible area "datasets and benchmarks" or "probabilistic methods / evaluation". Maturity: complete empirical study with one registered test already scored and two pending rules.

## Seats

ICLR scale (1, 3, 5, 6, 8, 10); confidence 1 to 5.

| Seat | Persona | Score | Conf. | One-line verdict |
|---|---|---|---|---|
| S1 Journal-fit (AC view) | Area chair, LLM evaluation | 5 | 3 | Careful and honest, but the reader can't find the takeaway, and the paper's own transfer result undercuts its utility claim. |
| S2 Methodology | Statistician, clustered inference and resampling | 6 | 4 | Interval calibration is unusually thorough, but both pre-committed rules were designed at roughly one-third power, so they can't settle anything either way. |
| S3 Domain | LLM pretraining and eval practitioner | 5 | 4 | The estimand is item-general, while practitioners compare models on a fixed bank, and seed-matched comparisons barely move (median ratio 1.024). |
| S4 Perspective | Psychometrics and generalizability theory | 6 | 3 | A sensible import of split-half and G-theory ideas, though it isn't compared with an analytic item-noise correction that would use every item. |
| S5 Devil's advocate | Hostile reviewer | 3 | 4 | The headline 1.244 is reproduced by an unmeasured shared item component at a 0.124 share, is set by one benchmark, and fails its own registered transfer test. |

Mean score 5.0 (5, 6, 5, 6, 3). Mean confidence 3.6. Likely outcome: borderline reject, reachable to borderline accept if S1 and S3 move to 6.

### Top weaknesses by seat

S1: an abstract that carries eleven numbers, nested caveats and three outcome variants; a contribution list in which three of four items end on a limitation; and the out-of-sample transfer result (independence beats the plug-in, 0.339 against 0.536) sitting in the Discussion rather than in Results.

S2: R1 passes in 0.356 of replicates at a true 1.244, and R2 has no reported operating characteristics. The registered held-out test ran at a noise level that its own power design didn't cover (observed width 0.626 against simulated 0.258 to 0.431 at the fixed noise levels), and the recipe clustering depends on a band-shared effect that is bounded only by a test with power 0.490.

S3: the item-general target excludes run-by-item deviation on the released bank, which is the quantity a practitioner re-running a fixed benchmark actually faces. Seed-matched recipe comparisons change the wrong-call rate by at most 0.009, and the recommendation ("paired replicate scores") needs no SNAP estimate.

S4: the paper gives no efficiency comparison between the split-half construction and a diagonal correction built from within-run item sampling variance, and generalizability theory (Brennan) appears only in the appendix. The "phenotype/trait" vocabulary adds friction without adding identification.

S5: the estimate is identified only up to a shared item component that the DataDecide data never measure, and BoolQ holds 68% of the trace, so that removing it raises the factor to 1.786. The registered test fails, and the plan's thresholds (1.349 and 1.40) were missed, with five of eleven planning predictions failing.

### Reviewer questions (as they would appear in OpenReview)

1. With three replicates per configuration you can compute the standard deviation of the fixed-bank battery mean directly. What is the fixed-bank inflation, and in which decision does the item-general number beat it?
2. Why split items into halves instead of subtracting the analytic item-sampling variance (per-benchmark item variance over n) from the full-data diagonal? What efficiency do you lose, and what dependence does the split protect against?
3. Given that R1 passes at a true 1.244 in only 0.356 of replicates, what would a failing R1 tell a reader that the point estimate and interval don't already say?
4. What are R2's probabilities of "rejected", "supported" and "undecided" when there's no shared item component, and when a component of share 0.124 is present?
5. Bank two draws mostly from train splits that pretraining corpora may contain. Could memorisation change the run covariance itself, and would that show up as a within-minus-cross difference?
6. How do you reconcile an accuracy interval that includes one with held-out accuracy at 1.220, interval [1.066, 1.359], which excludes it?
7. Removing BoolQ lowers the aggregate SD yet raises the factor to 1.786. Which of the two numbers should a practitioner report for a battery that includes BoolQ?
8. Can you show one published comparison whose conclusion flips once this covariance is accounted for?

## Findings

Severity: Critical, Major, Minor. "Lowers score" means that a typical ICLR reviewer who noticed the finding would lower their score for it.

| ID | Severity | Lowers score | Verbatim quote | Objection | Fix |
|---|---|---|---|---|---|
| AR1 | Major | yes | "Out of sample on margins, independence predicts a configuration's measured ratio with a mean absolute log error of 0.339 against 0.536 for the plug-in and 0.512 for our decomposition" (main.tex:245) | The paper's own transfer test shows that the fitted ratio predicts worse than assuming independence, and this appears only in the Discussion. Together with the recommendation to measure paired replicates directly, it leaves SNAP's practical use unclear. | Move the result into Results next to the pooled-target reversal (0.275 against 0.319, appendices_bcd.tex:345), and name one concrete decision where the SNAP number changes what a practitioner does, for example error bars on a single model's battery average or planning seed counts. |
| AR2 | Major | yes | "so reproducibility on that fixed bank is a separate question" (main.tex:67) | Practitioners re-run a fixed benchmark, so the fixed-bank run variance, including run-by-item deviation, is the quantity they need. The main text never reports it or says when the item-general target is the better one. | Report a fixed-bank inflation from the full-item replicate averages (CPU only), or add a paragraph that states which use each target serves. |
| AR3 | Major | yes | "an item effect we haven't measured or separated from seed covariance" (main.tex:241) | A shared item component at a 0.124 share reproduces the whole margin headline, and the only direct check (R2) runs in a different family. S5 treats this as the central identification gap. | Put the cross-format evidence (mean 0.007, diagnostic 0.921) forward as the main constraint on a uniform component, and state plainly that a format-following component is untested in DataDecide. |
| AR4 | Major | yes | "At a true 1.244 it passes in 0.356 of 4,000 replicates" (main.tex:207) | A pre-committed rule with about one-third power can't confirm or refute transfer. The bound reading was added after the rule was fixed, and R2's operating characteristics aren't reported at all. | Report R2's simulated outcome rates under the null and under a 0.124 share in the same paragraph, give R1's power in the abstract sentence that reports it, and lead with the estimate and its interval rather than the pass/fail. |
| AR5 | Major | yes | "It rejects the shared-item explanation when that cross-bank interval sits above one and the jackknife interval for the within-minus-cross difference in log squared inflation includes zero." (main.tex:207) | A difference interval that includes zero is absence of evidence, so this outcome can't "reject" a shared component, and with 40 contrasts and a bank one sixth the size, noise pushes the rule toward that outcome. The R2-not-supported variants then print "with the shared-item explanation rejected" (abstract) and "rejected" (main.tex:45), which overclaims. | Rename the outcome "not supported" throughout and lead with the upper limit of the difference as the bound, which the R2-not-supported paragraph (main.tex:213) already provides. |
| AR6 | Major | yes | "which removes item-sampling noise the halves don't share, although an item effect shared across benchmarks and halves would enter the estimate, and a 0.124 share of item variance would reproduce our margin value." (main.tex:29) | The abstract and introduction are saturated with numbers and caveats, with roughly 60 numeric values before Section 2. Reviewers will score clarity low and miss the contribution. | Cut the abstract to about five sentences: the problem, the estimator, the headline with its interval, the BoolQ dependence, and the transfer outcome. Move the robustness numbers to Section 4. |
| AR7 | Major | yes | "We adapt the repeated-measurement construction of quantitative genetics to this setting and call it SNAP" (main.tex:35) | The novelty looks thin, because split-half correction and G-theory variance components are classical, and the paper doesn't compare against an analytic diagonal correction that uses all items. | Add a paragraph in Section 2 that says why the split is preferred (robustness to unknown within-benchmark item dependence and no need for an item-noise model), cite Brennan (2001) in main-text related work, and state what the estimand adds over G-theory. |
| AR8 | Major | yes | "BoolQ alone carries 68\% of the covariance trace" (main.tex:29) | With one benchmark setting the magnitude, and its removal raising the factor while the SD falls, reviewers will read Λ and K_eff as unstable summaries of a battery. | Make σ_agg the primary cross-battery quantity in the text and table, and keep Λ as the within-battery diagnostic. The paper already says this at main.tex:95, but only in passing. |
| AR9 | Major | no (unless unresolved) | "\label{maintext:end}" resolves to page 10 in main.aux (`\newlabel{maintext:end}{{6}{10}...}`) | With every outcome variant printed, the main text runs onto page 10 against the nine-page initial limit that READ_ME_FIRST.md cites (and READ_ME_FIRST.md:38 still says eight pages). Whether the resolved variant fits is unverified. | Compile each (\Ronecase, \Rtwocase) combination before submission and confirm that the Discussion ends on page 9. |
| AR10 | Minor | yes | "The analysis plan assigned eight recipes to screening and seventeen to estimation, but we used all recipes without drawing that partition" (main.tex:129) | Stats-minded reviewers will read this, the missed thresholds (1.349 and 1.40) and five failed planning predictions as a failed preregistration, which weakens trust in the two new rules. | Keep the disclosure, but collapse it into one short paragraph that separates the confirmatory analyses (registered test, R1, R2) from everything else, and note that the rule commits lack an external timestamp in the same place. |
| AR11 | Minor | no | "take simulated margin coverage to 0.821 at a quarter of latent variance and 0.580 at a half" (main.tex:243) | The band-shared bound (0.044) comes from a test with power 0.490, so the recipe-clustered interval could be anti-conservative. | Add one clause saying that the size-band-clustered margin interval [1.030, 1.426] (Table 1) still excludes one, which answers the concern with numbers already in the paper. |
| AR12 | Minor | no | "We therefore read our accuracy bound as conditional on the checkpoint we scored." (main.tex:127) | With 750M default runs scored at 41.5% of their final step, schedule truncation is confounded with the replicate contrast. | Say explicitly that R1 on PolyPythias, with one shared final step, is the design answer to this confound, and state what a failing R1 would imply for it. |
| AR13 | Minor | no | "Our accuracy interval \ci{0.993}{1.157} includes one under a low-powered design." (main.tex:29) | Held-out accuracy (1.220, [1.066, 1.359]), the adjacent checkpoint and BoolQ removal all exclude one, so readers may see the accuracy framing as selectively conservative. | Give one sentence in Results that names all the accuracy cuts that exclude one and says why the primary cut governs. |
| AR14 | Minor | no | "In simulation with margin-like covariance, such a comparison declares a difference in 0.113 of replicates with a true gap of zero" (main.tex:33) | The motivating number has no pointer to its simulation (appendices_bcd.tex:218). | Add an appendix reference. |
| AR15 | Minor | no | "calling each benchmark-level score a trait" (main.tex:60) | The genetics vocabulary ("trait", "phenotype") and the backronym add reading cost for an ML audience. | Use "benchmark score" in the main text and keep the analogy to one sentence. |

## Three text-only changes that would most raise the mean

1. Rewrite the abstract and introduction around one takeaway (AR6, AR8), stating that a ten-benchmark average's run SD is 1.244 times its independence value on margins, that one benchmark sets that magnitude, that seed-matched comparisons need little correction, and that σ_agg is the quantity to compare across batteries. This is expected to move S1 and S3 from 5 to 6.
2. Confront the utility question directly in Results (AR1, AR2) by stating which decision the item-general number serves, placing the independence-beats-plug-in result beside the pooled-target reversal, and explaining when a practitioner should report fixed-bank variance instead. Doing this pre-empts S5's strongest counter-argument and S3's main objection.
3. Reframe the confirmatory rules by their operating characteristics (AR4, AR5): give R1's 0.356 power up front, add R2's outcome rates, replace "rejected" with "not supported" plus the upper bound, and justify the split-half design against an analytic diagonal correction (AR7). This is expected to lift S2 and S4 confidence and S5 from 3 toward 5.

## Experiments reviewers would demand

1. Score the 375 DataDecide runs on bank two, so that the cross-bank identification check runs in the family that supplies the headline.
2. Compute fixed-bank inflation from full-item replicate means and an analytic item-noise diagonal correction on the released reductions (CPU only), each compared with SNAP.
3. Run the registered held-out test at full 375-run scope or with larger item counts per task, enough to reach the simulated widths.
4. Add a power or outcome-rate simulation for R2 under null and shared-component alternatives.
5. Score held-out loss at the selected checkpoints (now shown to be reachable) as the competence measurement outside the benchmark scores.
6. Replicate on a larger or different multi-seed population, or on non-multiple-choice scoring, if one becomes available (the paper states that none exists publicly).
7. Show one downstream case, whether a published leaderboard gap or a recipe ranking, where the correction changes a conclusion.
