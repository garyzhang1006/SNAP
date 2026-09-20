# Overnight audit, started 2026-09-20 00:35 EDT

Loop: one parent scan per 45-minute wakeup, twenty sub-scans each, logged in SCAN_LOG.md as scans 71 onward (round 3). Each scan opens by re-checking what the previous scan changed. Mechanical sub-scans run from scratchpad/subscans.py (build, page 9, undefined, citations, refs, labels, punctuation, contractions, floor, ceiling, vocabulary, anonymity, abstract numbers, number tracing, contrast crutches, rhythm, duplicates, graphics, key facts, PDF), then judgment sub-scans by reading (claims versus evidence, logic, related work, limitations, reproducibility, abstract against body, evidence labels, notation, figures and tables).

## Step status

1. Skills: 23 ran on 2026-09-19 (10 of 16 ars plus 13 others, SCAN_LOG entry of that evening). Rerun on the current text: pending.
2. Hostile review: research/HOSTILE_REVIEW_2026-09-19.md, score 6 of 10, confidence 4 of 5. Rescore after each scan: pending per scan.
3. Parent scans 71 to 90: 6 of 20 done (71 to 76).
4. Corpus: research/style_study/corpus2 holds 23 accepted papers from 2015 to 2022 (22 before 2022) with measured targets in memory (median 16 words, sd 11.9, under-12 share 0.314, clause-join maxima). Re-measure against the current text: pending.
5. Controlled-language rewrite: main text done 2026-09-19; appendices and supplement have contractions and punctuation only, rhythm pending.
6. Final humanizer, stop-slop and remove-ai-marks pass over all four files: pending, runs last.
7. Rebuild, page 9, checks, commit, make_supplement after each step: standing.

## Scan ledger

(appended per scan: number, findings, edits, score)

- Scan 71 (00:45 EDT): 3 failures fixed (supplement label aliasing, abstract power number 0.135 added to the introduction, anonymity pattern narrowed to the full name), 3 checker false positives fixed, rhythm warnings carried forward. Score 6 of 10, ranking 6.3.
- Scan 72 (01:50 EDT): Table 1 caption now defines the aggregate standard deviation symbol, BoolQ removal logic and evidence-label placement checked, splitter made body-only and equation-aware, main text now has no sentence outside the 8 to 50 word band. Score 6 of 10, ranking 6.3.
- Scan 73 (02:35 EDT): Table 2 and the leave-one-task-out sentence traced cell by cell to the k04 and k06 outputs, no defect, no edit. Score 6 of 10, ranking 6.3.
- Scan 74 (03:30 EDT): discussion's seed-count power sentence now states its equicorrelation condition, practice recommendation folded to hold page 9, figure, limitations and reproducibility statement checked, 1B interval traced to the r19 kernel. Score 6 of 10, ranking 6.3.
- Scan 75 (04:15 EDT): related work checked against the Bouthillier and Jordan abstracts online, abstract checked sentence by sentence against the body, no defect, no edit. Score 6 of 10, ranking 6.3.
- Scan 76 (05:00 EDT): Table 1 derived quantities, Equation 1 and 2 normalisations, the information ratio and the test-inversion shift recomputed, all agree, no edit. Score 6 of 10, ranking 6.3.
