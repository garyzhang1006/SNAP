# Slice B status (main.tex 50-136), round 2

Word count (wc -w): slice_B.orig.tex 1620, slice_B.new.tex 1620. All 9 \label kept, no dashes as punctuation, no new citations.

- R2-01 FIXED (slice l.26). Source: results/snap-r2-r1-50/r1_50_crossformat_boot.json (margin point 0.9212, wild 0.8007 to 1.0347). New text: "Centring removes any item effect constant across runs, so only a run-by-item-set deviation shared by both halves enters the numerator, such as a run's deviation on every item of one prompt template, which recurs on any redrawn bank in that format and belongs to fixed-battery run covariance, unlike a component tied to the items both halves share." The 0.124 sentence stays, then: "Cross-format covariances alone give inflation 0.921 \ci{0.801}{1.035}, with pairs averaging 0.007 (Appendix~\ref{app:supplementary}), which constrains a uniform component of that size, while one that follows scoring format is untested in DataDecide and the cross-bank rule of Section~\ref{sec:family} tests it in PolyPythias." Nothing said about bank two's few-shot exemplars. Net longer by about 40 words, paid for by the cuts listed at the end.
- R2-12 FIXED (slice l.18). Source: results/snap-r2-r1-08/r1_08_fixed_bank.json (all_ten fixed_bank wild: margin 1.2375 [1.1370, 1.3313], accuracy 1.0672 [0.9938, 1.1343]; split 1.2439, 1.0784). The pointer to app:derivations was replaced by: "On the released bank, the replicate standard deviation of the full-bank average gives inflation 1.237 \ci{1.137}{1.331} on margins and 1.067 \ci{0.994}{1.134} on accuracy, against 1.244 and 1.078 from the split."
- R2-13 FIXED (slice l.48, appended to the paragraph at main.tex:97). New text: "Subtracting item-sampling variance from the full-data diagonal would use every item but needs independent items and a noise model, while the split needs neither, at the cost of half the items in each score." I dropped the brief's "tolerates the passage and story dependence of Section~\ref{sec:composition}" clause for length, and because l.26 already states the passage condition. No efficiency number.
- R2-17 FIXED (slice l.80). New text: "The analysis plan assigned eight recipes to screening and seventeen to estimation, we never drew that partition, and every choice in the primary analysis could see all 125 configurations, so no holdout survives (Appendix~\ref{app:design})." Enumeration range and threshold sentence deleted per the brief. Coordinator note: R1-49 has since landed (results/snap-r2-r1-49/r1_49_enumeration.json: margin 1.0367 to 1.3165, accuracy 0.9635 to 1.1914, 0 sets reach 1.349 or 1.40), so the "no result file" reason no longer holds. The range could return to app:design if APP wants it.
- R2-27 FIXED (slice l.68). New text: "We report the wild interval, whose coverage across the twelve populations of Table~\ref{tab:coverage}, at 2,000 replicates each, runs from 0.928 to 0.954, while the configuration percentile bootstrap drops to 0.872 under recipe-shared effects." The duplicate range is gone.
- R2-28 FIXED (slice l.78). "removes the 750M band and one 530M configuration".
- R2-29 FIXED (slice l.78). Clause added: "..., although the auxiliary contrast, whose runs sit near their final steps, still excludes one." The 1.256 and Table~\ref{tab:primary} pointer are already in the paragraph's first sentence, so I didn't repeat them.
- R2-30 FIXED (slice l.84). "A smaller earlier transfer check on 4,755 items is in Appendix~\ref{app:transport}."

Length-paying cuts (content is kept in the appendices or implied):
- l.4 "collects the symbols."
- l.26 "by keeping each passage in one half".
- l.66 implementation sentence merged into a parenthetical pointer.
- l.68 bias sentence compressed to "bias the estimate down by 0.011 to 0.016". The 0.014, 0.016 and 0.011 values are in tab:coverage, appendices_bcd.tex:277,285-286.
- l.70 "Appendix~\ref{app:derivations} reports recipe influence."
- l.76: checkpoint ranges 18-44% and 39-89% dropped (appendices_bcd.tex:8 carries them), "puts this step at 41.5\% ... on average and 87\% at 530M".
- l.78: app:schedule sentence reworded, "which reaches zero" dropped (the interval shows it), and the adjacent-step sentence compressed.
- l.82 and l.84: minor rewording.
- Algorithm caption: "checked against a passage-aware one".
