# Overnight audit, started 2026-09-20 00:35 EDT

Loop: one parent scan per 45-minute wakeup, twenty sub-scans each, logged in SCAN_LOG.md as scans 71 onward (round 3). Each scan opens by re-checking what the previous scan changed. Mechanical sub-scans run from scratchpad/subscans.py (build, page 9, undefined, citations, refs, labels, punctuation, contractions, floor, ceiling, vocabulary, anonymity, abstract numbers, number tracing, contrast crutches, rhythm, duplicates, graphics, key facts, PDF), then judgment sub-scans by reading (claims versus evidence, logic, related work, limitations, reproducibility, abstract against body, evidence labels, notation, figures and tables).

## Step status

1. Skills: 23 ran on 2026-09-19 (10 of 16 ars plus 13 others, SCAN_LOG entry of that evening). Rerun on the current text: ars-citation-check at scan 82 (no defect), the rest pending.
2. Hostile review: research/HOSTILE_REVIEW_2026-09-19.md, score 6 of 10, confidence 4 of 5. Rescore after each scan: pending per scan.
3. Parent scans 71 to 90: 13 of 20 done (71 to 83), loop stopped by the user at 10:19 EDT on 2026-09-20. Scan 84 (10:22 EDT) is the reframe pass under the new goal.
4. Corpus: research/style_study/corpus2 holds 23 accepted papers from 2015 to 2022 (22 before 2022) with measured targets in memory (median 16 words, sd 11.9, under-12 share 0.314, clause-join maxima). Re-measured at scan 81: main text median 16, sd 12.3, under-12 0.318, every join rate under the corpus maximum.
5. Controlled-language rewrite: main text done 2026-09-19; appendices and supplement have contractions and punctuation, eight-word floor met on all four files at scan 77, long-sentence pass on the supplement pending.
6. Final humanizer, stop-slop and remove-ai-marks pass over all four files: done at scan 84 on freshly regenerated extracts, main text 100 of 100, appendix A 85, appendix C 73, supplement 71 (remaining hits are the technical terms cluster-robust and leverage); the banned-vocabulary and contrast-crutch sub-scans read zero on all four files.
7. Rebuild, page 9, checks, commit, make_supplement after each step: standing.

## Scan ledger

(appended per scan: number, findings, edits, score)

- Scan 71 (00:45 EDT): 3 failures fixed (supplement label aliasing, abstract power number 0.135 added to the introduction, anonymity pattern narrowed to the full name), 3 checker false positives fixed, rhythm warnings carried forward. Score 6 of 10, ranking 6.3.
- Scan 72 (01:50 EDT): Table 1 caption now defines the aggregate standard deviation symbol, BoolQ removal logic and evidence-label placement checked, splitter made body-only and equation-aware, main text now has no sentence outside the 8 to 50 word band. Score 6 of 10, ranking 6.3.
- Scan 73 (02:35 EDT): Table 2 and the leave-one-task-out sentence traced cell by cell to the k04 and k06 outputs, no defect, no edit. Score 6 of 10, ranking 6.3.
- Scan 74 (03:30 EDT): discussion's seed-count power sentence now states its equicorrelation condition, practice recommendation folded to hold page 9, figure, limitations and reproducibility statement checked, 1B interval traced to the r19 kernel. Score 6 of 10, ranking 6.3.
- Scan 75 (04:15 EDT): related work checked against the Bouthillier and Jordan abstracts online, abstract checked sentence by sentence against the body, no defect, no edit. Score 6 of 10, ranking 6.3.
- Scan 76 (05:00 EDT): Table 1 derived quantities, Equation 1 and 2 normalisations, the information ratio and the test-inversion shift recomputed, all agree, no edit. Score 6 of 10, ranking 6.3.
- Scan 77 (05:50 EDT): Sections 3 and 4 traced to the item-count, checkpoint and PolyPythias outputs, four short supplement sentences joined to their neighbours, eight-word floor now met everywhere. Score 6 of 10, ranking 6.3.
- Scan 78 (06:45 EDT): batch-offset null N6 now reported in Appendix B, unsupported "calibrated" removed from Section 5.3, one redundant sentence cut to hold page 9, "as Appendix" join varied, 18 of 20 mechanical sub-scans pass. Score 6 of 10, ranking 6.3.
- Scan 79 (07:30 EDT): keyword-aware trace of every Section 5.3 number, pooled adjustment results added to Appendix C from tab_primary.csv, gain shares recomputed. Score 6 of 10, ranking 6.3.
- Scan 80 (08:10 EDT): keyword-aware trace extended to all 124 main-text decimals, three flags all explained, AI use and ethics statements read, no edit. Score 6 of 10, ranking 6.3.
- Scan 81 (09:00 EDT): main text re-measured against the corpus and inside it on every statistic, one caption join varied, supplement long sentences read and kept. Score 6 of 10, ranking 6.3.
- Scan 82 (09:45 EDT): Appendix A checked against Section 2 symbol for symbol, citation check rerun with no defect, no edit. Score 6 of 10, ranking 6.3.
- Scan 83 (10:14 EDT): Appendix B design section and held-out paragraph traced to r21, tab_reliability, tab_primary, the k03 decision, plan.json and the k04 interims, the 1B run count corrected from 52 to 55 (pilot c4 runs included). Score 6 of 10, ranking 6.3. Loop stopped by the user after this scan.
- Scan 84 (10:22 EDT): reframe pass from two fresh-context reviews (scores 5 and 4 before the edits), abstract cut to 282 words, contribution paragraph added, failed test framed with the pre-fixed comparison and the post-hoc levels named, five appendix-only disclosures brought into the main text, rhythm restored after the page-9 merges, humanizer 100 on a fresh extract. Score 6 of 10, ranking 6.3.
