# Slice A status (round 6)

Word count, raw `wc -w`: before 1043, after 1065 (cap 1065). No \citep changed. No number added or moved; every number printed already appeared in slice A.

- R6-01 FIXED (+6). Abstract: "Without cross-format run covariance, a uniform item component shared by all benchmarks can carry at most about a third of the margin excess, since a larger one pushes cross-format inflation above its interval \ci{0.801}{1.035}." Brief target trimmed by three words ("If run covariance across scoring formats is zero" -> "Without cross-format run covariance", "would push" -> "pushes"); premise from results/snap-r5-shared-bound/r5_shared_bound.json as named in the brief. No "acting alone" left in slice A.
- R6-04 FIXED (+11). Intro (main.tex:43): "a failure, in a reading added after fixing the rules, bounds it or counts against transfer" (+8). Abstract R1-fail branch: "which fails a rule fixed before scoring and \pending{bounds inflation in this family / counts against transfer}, and a disjoint item bank ..." replacing "at a design with 40 within-configuration contrasts" (+3), mirroring main.tex:207's two-way \pending.
- R6-02 FIXED (+4). main.tex:45: "and the two diverge where item noise is large, as for accuracy without BoolQ, where replicates give 1.285 and the split 1.558".
- R6-10 FIXED (+1). Abstract: "and on DataDecide's recipe comparisons correcting for covariance withdraws at most 12 of 173 to 223 declared orderings whose 1B counterpart clears two standard errors." (definition of a resolved ordering from main.tex:222).
- R6-15 FIXED (-1). "(iv) We measure run covariance across the 375 released runs, where every recipe, recipe-pair and benchmark deletion and four of five size-band deletions leave a margin interval that excludes one." ("along with" -> "and", "the five" -> "five" to pay for the added word; content unchanged.)
- R6-18 FIXED (+1, main.tex:37 part). "(run variance's share of a benchmark half's replicate variance;" per reliability.py:41-44 cited in claim_audit CA4.
- R6-06 SKIPPED (about +16 per PA5; 0 words left). Rules undescribed in the intro, "the shared-item question" antecedent and the 0.761 no-shared-component condition remain open.
- R6-07 SKIPPED (about +5 minimum for "except under size-band run effects, very large item noise or few recipes"; 0 words left).
- R6-24 SKIPPED (about +11 for ", so the within-bank value, including DataDecide's 1.244, can overstate run covariance"; 0 words left).

Checks: no em or en dashes, no `--`, no banned vocabulary (the one "harness" is the OLMES evaluation harness, unchanged). All \pending, \outcome, \Ronecase, \Rtwocase branches and labels kept. stop-slop pass run on the abstract and intro paragraphs 3, 6 and 7; no further revision needed within the cap.
