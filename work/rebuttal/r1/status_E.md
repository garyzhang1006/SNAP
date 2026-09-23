# Section E status, round 1

Slice length: orig 9,060 chars (main text before \label{maintext:end} 5,516), new 8,891 (main text 5,515).

- R1-06 NEEDS-EXPERIMENT: scoring the 375 DataDecide runs on the 6,808-item second bank needs GPU inference, and the limitation sentence stays unchanged in the Discussion.
- R1-21 FIXED: the practice paragraph now adds an untested fallback via the format fit (Appendix app:formatfit) and says seed-matched paired comparisons need little correction at median 1.024 (appendices_bcd.tex:185, Appendix app:paired), and the band sentence now notes that seed-matched paired comparisons cancel a band-level run effect.
- R1-23 FIXED: added the miller2024 sentence (clustered and paired item-sampling errors with run variance fixed) plus henderson2018 and agarwal2021 resampling within a task, and replaced "Among the studies we located, we find none" with "We know of no study"; the next paragraph states that our contribution is the estimand and its measurement.
- R1-24 FIXED: added \citet{fehlauer2025} to the seed-variability list, with a new references.tex entry taken from arXiv 2509.26643 (EMNLP 2025).
- R1-25 FIXED: added the cross-model capability-structure sentence citing ruan2024 and burnell2023revealing, with new entries taken from arXiv 2405.10938 (NeurIPS 2024) and 2306.10062. The existing Science paper is now labelled Burnell et al. (2023a) and the new one (2023b), so readers can tell them apart.
- R1-26 FIXED: the jordan2024 sentence now says his accuracy deviations are nearly independent across ImageNet evaluation sets, which our accuracy interval allows, while our margin covariance sits within formats.
- R1-27 FIXED: added a scope sentence to the Discussion covering 1B, likelihood-scored multiple choice, no larger public multi-seed replicate population (Appendix app:design) and generative tasks lacking the margin.
- R1-30 FIXED: "a bound of 1.157" became "an upper limit of 1.157 at the scored checkpoint", and the ", so the" join became ", and the".
- R1-34 FIXED: deleted the "We make no claim about that mechanism..." sentence. Its content (clipped-drop 0.889 against a simulated fifth percentile of 0.908) is already in app:proxy at appendices_bcd.tex:308, so APP needs no change.
- R1-38 FIXED: merged the two timestamp caveats into a single sentence, and also dropped the redundant "require their own execution records" sentence.
- R1-41 FIXED: the sentence now reads "a separate transfer simulation to a battery whose own ratio is 1.5 leaves it at 0.101" (appendices_bcd.tex:222).
- R1-53 FIXED: the cheverud1988 sentence now ends at the plug-in comparison without reporting a result, and the construction is credited to the split-half work of \citet{spearman1910,brown1910}.
- R1-55 FIXED: sellam2022 now has Tenney eleventh per arXiv 2106.16163, and the zhao2026 title reads "1--3{B}".
- R1-58 REJECTED: per the log, the remaining audit candidates answer no open objection and would cost page budget.
- R1-62 REJECTED: the flagged \citet calls are sentence subjects, where a tie is wrong.

Offsetting cuts (no numbers changed): I dropped the cheverud2001/nyholt2004/li2005 sentence, which appendices_bcd.tex:75 still carries, along with the BoolQ interval \ci{1.412}{1.687} (1.558 kept), the Discussion sentence repeating the within-format finding, and the 0.007 cross-format average, which Sec 4.4 reports. I also tightened wording in the bouthillier2021, heineman2025 and martin1977 sentences and in the practice paragraph. main.tex no longer cites cheverud2001, nyholt2004 or li2005, but the appendix still does.
