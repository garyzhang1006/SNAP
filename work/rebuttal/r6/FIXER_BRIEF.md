# Round 6 fixer brief

Merged findings are in REBUTTAL_LOG.md under "### Merged findings (round 6)", and the raw reviewer reports, with each reviewer's proposed wording, are in work/rebuttal/r6/{paper_audit,claim_audit,kill_argument,academic_reviewer,citation_audit}.md. Read the report rows for your findings before editing. Line numbers refer to deliverables/main.tex at 73277c2. Each fixer edits only its own file, so the five run in parallel.

| Slice | File you edit | main.tex lines | Findings, in priority order |
|---|---|---|---|
| A | work/rebuttal/r6/slice_A.new.tex | 28-45 | R6-01, R6-04, R6-02, R6-10, R6-15, R6-06, R6-07, R6-18 (main.tex:37 part), R6-24 |
| B | work/rebuttal/r6/slice_B.new.tex | 46-130 | R6-03, R6-01 (main.tex:71), R6-13, R6-16, R6-08, R6-22 |
| C | work/rebuttal/r6/slice_C.new.tex | 131-198 | R6-25, R6-19 |
| D | work/rebuttal/r6/slice_D.new.tex | 199-252 | R6-01 (main.tex:235), R6-02 (main.tex:216), R6-05, R6-09, R6-12, R6-11, R6-14, R6-17, R6-23 |
| APP | deliverables/appendices_bcd.tex, appendix_a.tex, references.tex | none | R6-01 (appendices_bcd.tex:261), R6-21, R6-18 (caption at appendices_bcd.tex:34), R6-26, R6-27 |

Slice D contains the AI-use statement and ethics statement (main.tex:244-249) and the \label{maintext:end} line (243). Leave all of those byte-identical. The reproducibility statement (250-251) is yours.

## Global rules

1. Invent no number. Use only numbers already printed in the paper or stored in a result file, and name the source in your status note for any number you move or add.
2. Add no citation except olmo2025olmo3 (APP only, verified by this round's citation audit; bibitem text is in citation_audit.md).
3. PolyPythias bank one is being scored and bank two is unscored. No sentence outside the \outcome branches may say either was scored or describe a result. Keep every \pending, \outcome, \Ronecase, \Rtwocase branch and every \label.
4. No em dashes, no en dashes (including LaTeX `--`), no "not X but Y" contrasts, no banned vocabulary from CLAUDE.md, and continuous academic prose in the paper's register with its contractions. Run the stop-slop checks on each paragraph you edit.
5. Page budget. The main text has about 55 real words of slack across all six outcome builds (measured by filler at 73277c2). Net word caps, raw `wc -w` of your slice with each \citep counted as zero: A at most 1065 (orig 1043, +22), B at most 1720 (orig 1700, +20), C at most 1154 (orig 1149, +5), D lines 199-243 at most 2051 (orig 2041, +10; the reproducibility statement doesn't count). Apply findings in the priority order above and SKIP later ones that don't fit, reporting the count. The coordinator compiles all six builds after the merge, and that check binds.
6. Don't cut what rounds 1 to 5 fixed. You may shorten wording inside a sentence you are already rewriting for a finding if its content survives, but don't delete another sentence or clause to buy room. `git log -S "<phrase>" -- deliverables/main.tex` shows which commit added a phrase.
7. Define and split before you add. Add no claim beyond the finding's fix.
8. Write one status line per finding to work/rebuttal/r6/status_{A,B,C,D,APP}.md as FIXED, SKIPPED (reason and word count) or NO-CHANGE, quoting the new text, with before and after word counts.

## Target wording for the four findings rated likely to lower the score

R6-01 (the premise is zero cross-format run covariance, from results/snap-r5-shared-bound/r5_shared_bound.json; "acting alone" stays only where a component carries the whole excess, as with 1.113). Abstract target: "If run covariance across scoring formats is zero, a uniform item component shared by all benchmarks can carry at most about a third of the margin excess, since a larger one would push cross-format inflation above its interval \ci{0.801}{1.035}." Main text and appendix: replace "acting alone" in every bound sentence with "with no cross-format run covariance" (or "under zero cross-format seed covariance" in the appendix), say the implied cross-format inflation passes the observed upper limit of 1.035 instead of "leaves its interval", and keep main.tex:71's offset caveat (negative cross-format run covariance, implied by 0.921 below one, could offset a larger component).

R6-02. Slice A, main.tex:45: "and the two diverge where item noise is large, as for accuracy without BoolQ, where replicates give 1.285 and the split 1.558". Slice D, main.tex:216: label the format-fit value so it can't be read as the fixed-bank 1.285 (for example "the format fit gives margin inflation of 1.285").

R6-03. Slice B, main.tex:123: after the G5 clause add a clause saying a simulator matched to each benchmark's variance components puts the gain's share near six percent, citing the appendix section that holds appendices_bcd.tex:62 (find its \label). Source: appendices_bcd.tex:62 "six percent at the estimated scale of 0.042".

R6-04. Slice A. At main.tex:43 state that the failure reading was added after the rule was fixed, matching main.tex:203's wording. In the abstract's rule-one fail branch replace the design clause "at a design with 40 within-configuration contrasts" with a verdict sub-branch that mirrors the two-way \pending main.tex:207 carries (upper limit bounds inflation in this family / estimate below 1.026 counts against transfer). Read main.tex:199-207 first so the wording matches.

For the remaining findings use the reviewers' proposed wording from the reports, trimmed to fit your cap. R6-08: change "tests it" to wording that limits the rule to a component tied to the item set, and add no claim about whether the templates match. R6-22: use only numbers already printed at main.tex:157 and :71. R6-09: prefer the zero-length fix (swap main.tex:239 and :241 so the recommendation paragraph closes the Discussion) plus defining "the plug-in"; the swap stays inside slice D. R6-26: cite Olmo 3 once at appendices_bcd.tex:399, name the Gen2MC variant and say an LLM wrote the distractors, add the bibitem after teamolmo2025 and relabel teamolmo2025 to (2025a).
