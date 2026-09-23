# Kill argument, round 6

Date 2026-09-23. Paper at 73277c2: deliverables/main.tex, appendix_a.tex, appendices_bcd.tex, references.tex. Both cross-model threads ran as fresh `codex exec -m gpt-5.5 -s read-only` calls with stdin closed (the CLI default model gpt-5.6-terra refused to run on codex-cli 0.139.0, so I used the model rounds 3 to 5 used). Attack session 01a0cd9b-e545-7270-a75e-dc29a9363730, adjudication session 01a0cd9d-4239-7f73-b9e2-88d9526fa210, with no shared context. Neither thread saw REBUTTAL_LOG.md or work/. Raw traces and prompts are in work/rebuttal/r6/ka_traces/. I checked every codex ruling against the source and against the round 3 to 5 rejection reasons, and I read the round 5 diff (fceef7c..73277c2) line by line for regressions. JSON and HTML sidecars were skipped, as in earlier rounds.

## Attack memo (verbatim, codex thread 1)

> Reject. Central result is an exploratory, battery-specific estimate elevated past its evidential base. SNAP estimates run covariance only under cross-half independence assumptions (deliverables/main.tex:35, deliverables/main.tex:66-71), while appendix admits item identifiers cannot verify those conditions (deliverables/appendix_a.tex:54) and DataDecide headline 1.244 was never tested on fresh items or with shared-item check in the headline family (deliverables/main.tex:235). Confirmatory evidence fails: pre-specified held-out margin test misses its lower-limit rule, 1.217 [0.872, 1.498], despite original ten passing on same runs (deliverables/main.tex:41, deliverables/main.tex:173-175). Original analysis also abandoned planned screening/estimation split, leaving no holdout; its planned thresholds are not reached by any of 1,081,575 reconstructed estimation sets (deliverables/main.tex:123, deliverables/appendices_bcd.tex:377-379). Statistical validity is fragile to exact dependence structure: size-band run effects drive recipe-clustered coverage to 0.821 or 0.580 (deliverables/main.tex:237, deliverables/appendices_bcd.tex:389). Result: paper asks reviewer to accept an exploratory in-sample covariance pattern as a measurement contribution after its own confirmatory test failed.

## Adjudication (codex thread 2, with my final ruling)

Codex counts: 0 answered, 5 partial, 1 unresolved. After checking the source and the log, none of the six points is new, and I overrule codex on P3 and P5.

| Point | Codex ruling | Final ruling | Reason |
|---|---|---|---|
| P1 cross-half assumption unverifiable | partial, major | answered for the fixed-bank value, partial for the split target | The abstract (main.tex:29) now gives 1.237 \ci{1.137}{1.331} "from replicate standard deviations alone, which need no item split", and main.tex:71 says only the redrawn-bank target and per-benchmark variances rest on the assumption. REPEAT of R3-03, R4-09, R5-04, all fixed. |
| P2 1.244 untested on fresh DataDecide items | partial, critical | partial, GPU | REPEAT R5-11 (NEEDS-EXPERIMENT, GPU). main.tex:235 states it. |
| P3 held-out test failed | unresolved, critical | answered as disclosure; the failure itself is inherent | Codex's fix ("state it in abstract and intro") is already done at main.tex:29 and :41. R5-08's rejection reason stands. |
| P4 planned split never drawn | partial, major | answered | main.tex:123 states it plainly. REPEAT R4-08, R5-15, both fixed. |
| P5 size-band dependence | partial, major | answered | Table 1 prints the size-band interval \ci{1.030}{1.426} beside the raw one, and main.tex:237 gives the 0.044 bound and its 0.490 power. |
| P6 exploratory pattern sold as measurement | partial, critical | partial, author position | The abstract says "Beyond the pre-specified test and two PolyPythias rules, analyses are exploratory." The position is sustainable only if PolyPythias rule one passes; if it fails, P6 becomes the review's summary sentence. REPEAT of the significance line (R5-07, R3-08). |

The memo repeats settled points and would not surprise a reader of the paper, since the body discloses each of them. Its force is cumulative: every confirmatory element either failed, is pending, or needs GPU, and the combination is what an AC will read.

## Findings

Only KA1 to KA6 are new or residual after round 5 edits. Rejected items (R3-45, R4-12, R5-08, R5-10, R5-23, R5-42, R5-44) are not re-raised, since their rejection reasons still hold against the current text.

### KA1, moderate, round 5 regression
Quote, main.tex:29: "Acting alone, a uniform item component shared by all benchmarks could carry at most about a third of the margin excess before inflation across scoring formats leaves \ci{0.801}{1.035}."
Attack: the abstract states a bound whose premise the paper's own point estimate contradicts. main.tex:71 and appendices_bcd.tex:261 concede that 0.921 below one already requires negative cross-format run covariance, which "could offset a larger component", so in the only model consistent with the data (item component plus run covariance) the one-third bound doesn't hold. The abstract also uses "inflation across scoring formats" undefined, and "leaves" an interval reads as a verb of motion with no subject a reader can resolve.
Likely to lower the score: no (the body is candid, and a reviewer who checks finds the caveat), but it is the sentence a methods reviewer will quote to show the abstract oversells identification.
Fix type: text.
Fix: either cut the sentence from the abstract (main.tex:71 carries it), or rewrite to "A uniform item component shared by all benchmarks, with no cross-format run covariance, could carry at most about a third of the margin excess, since the covariances between benchmarks of different formats give 0.921 \ci{0.801}{1.035}." The appendix wording ("zero-seed-covariance model") names the premise more exactly than "acting alone".

### KA2, moderate, round 5 regression
Quote, main.tex:45: "while the split adds per-benchmark run variances net of item noise and a redrawn-bank target, untested on DataDecide, and the two part where item noise is large, as for accuracy without BoolQ at 1.285 against 1.558 (Section~\ref{sec:estimator})."
Attack: "the two part" is ungrammatical and reads as "two-part" (codex flagged it independently). The two numbers carry no labels, so a reader can't tell which is fixed-bank and which is split, and 1.285 collides with the format-fit 1.285 at main.tex:216, the collision R4-10 fixed at line 93 and this edit reintroduced in the contributions.
Likely to lower the score: no.
Fix type: text.
Fix: "and the two targets diverge where item noise is large, as for accuracy without BoolQ, where the fixed-bank value is 1.285 and the split gives 1.558".

### KA3, moderate, residual of R5-02 (fix incomplete)
Quote, main.tex:239: "with the default simulator's item noise, three runs each let the margin interval exclude one in 0.997 of replicates and accuracy needs eight to reach 0.803, but at the accuracy battery's own noise three runs detect a true 1.078 in 0.111 of replicates"
Attack: the sentence keeps a planning number ("accuracy needs eight [runs]") that the paper's own measured-noise simulation contradicts, since appendices_bcd.tex:393 says four fifths needs "between 500 and 1,000 configurations at six runs". A planning recommendation followed by "but" and a 7-fold lower power figure invites the question of which number a practitioner should use, and the paper never answers it. R5-02's rejection doesn't apply; its fix labelled the populations but left the contradicted figure as the planning result.
Likely to lower the score: no.
Fix type: text.
Fix: replace the default-noise clause with the measured-noise figures: "at each battery's own item noise, three runs let the margin interval exclude one in 0.970 of replicates at a true 1.25, while accuracy at a true 1.078 reaches 0.111, and four fifths would need 500 to 1,000 configurations at six runs (Appendix~\ref{app:supplementary})." Check the 0.970 population label at appendices_bcd.tex:381 (compound-symmetric, margin item noise 0.73) before using it.

### KA4, moderate, round 5 regression (placement)
Quote, main.tex:241: "Independence predicts it with mean absolute log error 0.339, against 0.536 for the plug-in and 0.512 for SNAP with item noise added to both sides."
Attack: round 5 moved this result out of the recommendation paragraph into its own paragraph, so the main text now ends on SNAP losing to independence per configuration, with "item noise added to both sides" undefined and no sentence telling the reader what to conclude. The last paragraph a reviewer reads before the statements is an uninterpreted negative result.
Likely to lower the score: no, though it hands the significance attack its closing line.
Fix type: text.
Fix: add one interpretive clause, for example "so a three-seed fit can't recover one configuration's ratio, and SNAP's ratio is a pooled property of the population", and define or drop "with item noise added to both sides". The interpretation is INFERRED from the pooled-target result in the next sentence; verify it matches appendix_transport before printing.

### KA5, minor, round 5 regression
Quote, main.tex:29: "the correction removes at most 12 of the 173 to 223 calls on pairs with a resolved 1B ordering."
Attack: "resolved 1B ordering" is defined only at main.tex:222 (the 1B gap clears two corrected standard errors), so the abstract uses jargon introduced by the R5-03 fix. Codex flagged it independently.
Likely to lower the score: no.
Fix type: text.
Fix: "on recipe pairs whose 1B ordering clears two standard errors".

### KA6, minor, NEW
Quote, main.tex:157: "averaging 0.624 within formats and 0.007 across them", beside main.tex:71: "negative run covariance across formats, which 0.921 below one implies"
Attack: a reader sees a positive mean cross-format correlation next to a claim that cross-format covariance is net negative. The two agree only because BoolQ's negative covariances carry the largest variance weight (main.tex:157, about $-0.15$ of the margin trace), and Section 2.2 never says so.
Likely to lower the score: no.
Fix type: text.
Fix: at main.tex:71 add "because BoolQ's cross-format covariances are negative and carry most of the variance weight".

### Checks with no finding
Round 5 numbers against their sources: 0.420, 0.319 and 0.295 match results/snap-r5-shared-bound/r5_shared_bound.json (largest_share 0.41982, fraction_of_excess 0.31874 and 0.29513); Spearman $-0.036$ matches appendices_bcd.tex:10; 0.817 of flat-Dirichlet weightings matches appendices_bcd.tex:204; 0.111 and 0.103 match appendices_bcd.tex:393 and the supplement row cited in R5-02; the 66 item groups match appendices_bcd.tex:263; 12 of 173 to 223 matches main.tex:222. The contribution list, intro line 43 and Sec 4.3 line 203 now agree on what a pass, a failure and an undecided verdict mean (R5-12, R5-13 closed). Default and auxiliary runs are defined at main.tex:49 (R5-14 closed).

## Strongest single kill argument

Every confirmatory leg is missing: the one pre-specified test failed (1.217 \ci{0.872}{1.498}), the analysis plan's holdout was never drawn, the shared-item check was never run on DataDecide, and the PolyPythias rules have 0.259 simulated pass power. The practice the paper recommends, reporting the replicate SD of the battery average, needs no new estimator, and the correction moves at most 12 of 173 to 223 real recipe calls. A reviewer can therefore write that the paper contributes an exploratory in-sample estimate on one ten-benchmark battery whose value BoolQ drives (1.096 to 1.786 under single removals), plus a split estimator whose distinct target is untested. The text answers each piece honestly, but candour doesn't supply the missing confirmation, so the paper's fate rests on PolyPythias rule one.

## Estimated score

5/10 as it stands (borderline, weak reject to weak accept depending on the reviewer's weight on significance). A rule-one pass on PolyPythias would move it to about 6; a rule-one failure would move it to about 4. KA1 to KA6 are polish that protect against losing half a point, and none of them changes the estimate.
