# SNAP recipe to reach the 6 to 6.5 ceiling

Written 17 September 2026. Every date, file, and number below was checked today unless it carries the tag UNVERIFIED. The ceiling is an average reviewer score of about 6 to 6.5 and roughly 40 to 50 percent acceptance, and it holds only if the held-out test passes. No step here can push the paper to an 8, because the estimator is classical and the topic is evaluation methodology.

## 0. Facts that set the schedule

- The ICLR 2027 abstract deadline is 18 September 2026 at 23:59 AOE, which is tomorrow, and the full paper and supplement are due 25 September 2026 at 23:59 AOE ([call for papers](https://iclr.cc/Conferences/2027/CallForPapers)).
- The final abstract has to stay substantially similar to the registered one, and authors can't be added after registration ([author guidelines](https://iclr.cc/Conferences/2027/AuthorGuidelines)).
- Every submission needs at least one author who registers to review at least three papers and holds a qualifying publication at ICLR, NeurIPS, ICML, CVPR, AAAI, or a similar venue. If no author qualifies, the paper is at risk of desk rejection before anyone reads it.
- Authors can revise the PDF until 18 November, with a 10-page limit, but reviewers may ignore substantially changed revisions. Results added during the discussion period count for less than results in the submitted PDF.
- Kaggle gives about 30 GPU-hours per week on a P100 or two T4s, with a 9-hour session cap ([Kaggle docs](https://www.kaggle.com/docs/efficient-gpu-usage)). That quota is the binding constraint on the new experiment.
- The public `allenai/signal-and-noise` release holds DataDecide scores on about 240 tasks in both `:rc` and `:mc` formats, but only one seed per recipe and size (225 cells, one seed each, checked in `core.parquet` today). It can't replace new scoring, because seed covariance needs all three replicates.
- 80 of the 125 DataDecide model repositories refuse unauthenticated requests, 40 resolve, and 5 carry invalid `dolma1.6++` identifiers (`research/outputs/snap-r7-availability-recheck/r7_availability_recheck.json`).
- The last scoring job ran 27 runs on 4,755 items in under one L40S card-hour (`deliverables/appendices_bcd.tex:783`). Extrapolating to T4s at roughly a third of L40S speed gives about 1.4 T4-minutes per 1,000 items for a 1B run (INFERRED, confirm with the pilot in step 3).

## 1. Today and tomorrow (17 and 18 September), blockers first

1. **Check reviewer eligibility.** Confirm that one author has a qualifying publication and can register for three reviews on OpenReview. If nobody qualifies, stop here and target ICML 2027 with the full recipe, because every later step is wasted on a desk rejection.
2. **Register the abstract by 18 September 23:59 AOE.** Write it so it stays true whichever way the held-out test comes out. Lead with the question and the design (held-out benchmarks, pre-registered rule, two score scales) and leave the held-out numbers out, so the final abstract can add them without becoming "substantially different." Only you can submit this, because it goes out under your OpenReview account.
3. **Use the verified checkpoint table.** No Hugging Face token is needed: all 125 DataDecide model repositories download anonymously once the repository names follow allenai's own spelling (for example `dolma1_6plus`, `falcon-and-cc-qc-orig-10p`). `new code/config/runs.json` lists all 375 runs with their branches, each checked on the hub. The paper's statement that 80 of 125 repositories refuse unauthenticated requests came from misspelled names and must be corrected in the appendix and the Discussion.
4. **Approve the compute budget in writing.** The held-out scoring in step 3 needs about 12 to 30 Kaggle GPU-hours depending on scope. Nothing launches until you say yes in chat.

## 2. Freeze the pre-registration (18 September, before any new score exists)

Create `research/prereg/SNAP_heldout_protocol.md`, commit it, and record the commit hash and a SHA-256 of the file in `research/SCAN_LOG.md`. For an external timestamp that keeps anonymity, upload the hash (not the file) to an anonymous OSF registration or email it to yourself. The protocol has to fix all of the following before scoring starts.

- **Held-out benchmarks, four of them.** They must be multiple-choice log-likelihood tasks, not in the current ten, above chance at 1B, and free of shared passages. The candidates are SciQ, MedMCQA, AGIEval LogiQA-en in `:rc` format, and AutoBencher, all of which appear in the oe-eval task list inside `core.parquet`. Before freezing, check the exact task names in oe-eval and confirm with the one-run pilot that 1B accuracy clears chance. If a candidate fails that pilot, the protocol names the replacement in advance (Jeopardy is excluded because it's generative).
- **Runs.** State the scope before seeing any cost overrun. The full version uses all reachable configurations at the step rule already in the paper (the largest step shared by all three runs). The fallback, written in now, keeps the 530M, 750M, and 1B bands (75 configurations, 225 runs) if the pilot projects more than 30 GPU-hours.
- **Estimand and primary endpoint.** The primary endpoint is margin inflation Λ on the four held-out benchmarks alone, estimated with the unchanged cross-half estimator, fixed half-split seed, and wild recipe-cluster bootstrap-t with 4,999 Rademacher draws.
- **Pass rule.** The primary hypothesis passes if the lower 95 percent limit of held-out margin Λ exceeds 1. The secondary endpoint is the fourteen-benchmark margin Λ, compared against the current 1.244. Accuracy stays secondary on both batteries, reported without a pass rule, because the design can't power it.
- **Failure handling.** The protocol states in advance what the paper will say if the test fails (step 6), and that no benchmark gets swapped after scoring.
- **Frozen code.** Run the analysis script end to end on simulated scores with known Λ (reuse the `snap-r8-known-truth` generator) and commit it before the real scores arrive. Any later code change gets its own dated log entry.

## 3. Held-out scoring on Kaggle (19 to 23 September, after your approval)

1. **Pilot.** Score one 1B configuration (three runs) on the four benchmarks at the frozen step. Record wall time per 1,000 items, peak memory, disk, and download time, then write the projected total into the log before starting the full job.
2. **Pick the scope from the pilot, using the rule frozen in step 2.** Above 30 GPU-hours projected, run the three-band fallback. The weekly quota resets during the window, so a 30 to 45 hour full scope is possible only if the pilot is fast.
3. **Full run.** Stream one checkpoint revision at a time, because Kaggle's working disk is about 20 GB, and delete each checkpoint after scoring. Save per-item gold log-likelihood, byte counts, and all alternatives' scores, since the margin needs them. Checkpoint progress to the output every configuration, so a 9-hour session cap costs one configuration and not the job.
4. **Integrity checks before analysis.** Confirm item counts per benchmark, no duplicate run IDs, and that re-scoring one existing benchmark on one run reproduces the saved DataDecide margins to the tolerance already used in the GPU-architecture appendix.
5. **Run the frozen analysis once.** Record the output hash, then report the result as it lands.

## 4. CPU-only work that runs alongside scoring (18 to 22 September)

These use data already on disk, so they need no GPU and no new approval.

1. **Observed decision consequences.** This replaces the predicted-reversal census as the main practical result. For each size below 1B, take all 300 recipe pairs, compare their three-seed mean aggregates, and declare a winner when the 95 percent interval excludes zero. Build the interval once under independence and once with the SNAP-corrected aggregate variance. Treat as ground truth the 1B ordering of pairs whose 1B gap exceeds twice its own standard error. Report two things for each interval rule, the rate of confident calls that contradict 1B and the share of true orderings that were called. Freeze this design in the protocol file before running it, and label it exploratory, because the analyst has seen this data. If the corrected rule changes almost nothing, say so and drop the practical-importance claim.
2. **A seed-count rule for practitioners.** `appendices_bcd.tex:684` already shows coverage holds at ten recipes and two runs. Turn that into one main-text statement of how many runs and recipes a lab needs before an independence-based interval undercovers by more than a stated amount, derived from the fitted Λ and the existing coverage simulations.
3. **A headline figure.** Plot the false-positive rate of an independence-based comparison against the true gap, for margins and accuracy, with the corrected rule overlaid, using the existing 0.113 and 0.051 simulation outputs. This becomes Figure 1, and the correlation heatmap moves to the appendix.

## 5. Rewrite the main text (22 to 25 September)

The page is full to within about 100 characters, so every addition needs an equal cut first.

**Cut or move to the appendix, freeing about 0.8 page.**
- The competence-proxy paragraph and its −0.086 split-half result (Discussion, second paragraph).
- The gain-simulation paragraph with the 2 to 91 percent share (Results 5.2, third and fourth paragraphs).
- The permutation-versus-cluster disagreement paragraph (Results 5.3, second paragraph), leaving one sentence and a pointer.
- The phenotypic plug-in rows and their discussion in Table 2, leaving the Cheverud citation in related work.
- The checkpoint-shift details in the last Discussion paragraph, leaving one sentence.

**Add, in this order of priority.**
1. The held-out result as its own subsection directly after the full-battery estimates, with the protocol hash cited and the pass rule quoted.
2. The observed decision-consequence result from step 4.1.
3. The seed-count rule, as the last paragraph before related work.
4. The new Figure 1.

**Restructure the argument.**
- The introduction's first paragraph ends on the effective count. Ten DataDecide benchmarks behave like 6.46 independent ones on margins, and ignoring that more than doubles the false-positive rate (0.113 against 0.05).
- The fifth introduction paragraph, currently a list of exceptions, shrinks to two sentences. The exceptions move to Discussion, where they stay in full.
- Accuracy becomes an explicit bound. The design rules out accuracy inflation above 1.157, and it can't distinguish 1.08 from 1. State that once, early, and stop defending it elsewhere.
- Format becomes a stated open question. Report the 0.624 against 0.007 contrast, say the design can't separate format from content, and name the two-format experiment as the test.
- The contribution paragraph lists three things, the estimator's conditions, the pre-registered held-out test, and the decision consequence. Drop "we examine batch, gain, and format mechanisms" from the contribution list, because none of those produced an identified result.
- Related work gets one sentence that separates SNAP from `miller2024` (clustered standard errors within one benchmark) and from `heineman2025` (per-benchmark signal and noise), since those are the first two papers a reviewer will cite against novelty.

**After the prose is final, run the checks in this order.** Rebuild on the Kaggle build kernel, confirm 9 main-text pages, zero overfull boxes and zero undefined references, verify every new number against its JSON output, run the citation check, then run the humanizer and slop gate as the last step.

## 6. Decision gates after the held-out result

- **Held-out lower limit above 1.** Submit with the result in the abstract. Expected average around 6 to 6.5 if steps 4 and 5 also land.
- **Held-out point estimate above 1, interval includes 1.** Submit, report it as consistent but underpowered, and don't call it confirmation. Expected average around 5.5.
- **Held-out point estimate at or below 1.** The margin covariance is specific to the original battery. Submitting still beats withdrawing, provided the paper says plainly that the held-out test failed and reframes the finding as composition dependence. Expected average around 5, with roughly 20 percent acceptance. The stronger alternative is ICML 2027 with a second population added.
- **Scoring can't finish by 23 September.** Submit on 25 September without the held-out result, since the rewrite in step 5 still lifts clarity, and add the result during discussion. Expect reviewers to weigh it less.

## 7. Discussion period (5 to 18 November)

1. **Two-format experiment.** For each of the ten benchmarks, score the other format (`:rc` for the current multiple-choice traits, `:mc` for the cloze ones) on the same checkpoints, and compare within-benchmark cross-format correlation with the current 0.007. First run a pilot on one 1B configuration, because multiple-choice letter formats sit near chance below about 1B in OLMES-style evaluations (INFERRED from the OLMES format results, UNVERIFIED for DataDecide). If `:mc` is at chance, the test can't run at these sizes, and the reply to reviewers says so with the pilot numbers.
2. **Prepared replies to the four predictable objections.** Novelty (split-half is classical, the contribution is the estimand, the conditions, and the held-out evidence), scale (1B maximum, point to the PolyPythias transfer and state the limit), BoolQ dominance (passage-aware split and the 1.558 removal result), and accuracy including 1 (the explicit bound from step 5).
3. **Keep revisions small.** Put new results in the appendix with a one-sentence main-text pointer, so the PDF diff stays readable and reviewers don't discount it.

## 8. Work that won't move the score, so skip it

More humanizer or slop passes, more sentence merging, more permutation or bootstrap repeats, renaming the method, extra appendix robustness tables, and further PolyPythias rescoring at the same sizes. The appendix already has more checks than reviewers read, and 50 editing scans held the score flat.

## 9. How each step maps to reviewer sub-scores

| Sub-score | Now | After the recipe, if the held-out test passes | Step that moves it |
|---|---|---|---|
| Soundness | 2 | 3 | Pre-registered held-out test (2, 3) |
| Significance | 2 | 3 | Observed decision consequences and seed-count rule (4.1, 4.2) |
| Clarity | 3 | 3 to 4 | Rewrite and new Figure 1 (5) |
| Novelty | 2 | 2 | Nothing available moves it, which is why the ceiling stops near 6.5 |
