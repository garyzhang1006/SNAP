# Round 1 fixer brief (shared by all section fixers)

Repo: /Users/garyzhang/Documents/ChatGPT/iclr main track. Paper: deliverables/main.tex (ICLR 2027 submission on SNAP, a cross-half estimator of run-to-run covariance between benchmark scores). Findings: REBUTTAL_LOG.md, section "Findings (merged, deduplicated, ranked)". You own exactly one section letter; handle only findings whose header line carries your letter.

## What to produce
- Section A to D: start from work/rebuttal/r1/slice_<X>.orig.tex (the exact current text of your section of main.tex) and write the full revised section to work/rebuttal/r1/slice_<X>.new.tex. Do NOT edit deliverables/main.tex; the coordinator splices your file in. Keep every \label, \ref, \outcome{...}, \pending{...}, figure/table environment and LaTeX macro intact unless a finding requires changing it.
- Section E: same for slice_E, and you may also edit deliverables/references.tex directly (you are its only editor).
- Section APP: edit deliverables/appendix_a.tex and deliverables/appendices_bcd.tex directly (you are their only editor).
- Everyone: write work/rebuttal/r1/status_<X>.md with one line per finding id: FIXED (what changed, one line), NEEDS-EXPERIMENT (one line: what and CPU/GPU), or REJECTED (one line why the reviewer is wrong).

## Hard rules
1. Never invent or change a number. Every number you add must already appear in the paper, its appendices, or a results file under research/outputs/ (cite the path in your status line). If a fix needs a number that doesn't exist, mark NEEDS-EXPERIMENT.
2. No new citation unless the citation audit (work/rebuttal/r1/citation_audit.md) verified it with a URL; only section E adds bibliography entries.
3. Page budget: the main text is about 1.1 pages over the 9-page limit and a separate cut pass follows you. Net length of your section must not grow; prefer tightening. Sections A to D should aim to come out shorter than they went in.
4. Paper style (the author's rules): continuous academic prose, contractions throughout (don't, isn't, can't, we'd), no colons or semicolons in prose, no em dashes, no sentence under eight words, varied sentence length, no ", so the" joins, no "not X but Y" contrasts, no rule-of-three lists, none of these words: delve, robust, seamless, leverage, crucial, vital, pivotal, holistic, landscape, navigate, unlock, harness, foster, utilize, facilitate. Keep honest framing: exploratory versus registered labels stay exactly as they are.
5. After editing, run the stop-slop pass yourself on every paragraph you changed: read /Users/garyzhang/.claude/skills/stop-slop/SKILL.md and apply it.
6. No compute of any kind on this machine (no models, no data processing). Reading JSON result files to copy a number is fine. Do not run LaTeX (the coordinator compiles once all fixers finish, to avoid clobbering build files).
7. Intentional, not a defect: \pending{} placeholders and \outcome variants in subsection "A second family and a disjoint item bank" (results still being scored).

Return to the coordinator under 10 lines: counts FIXED / NEEDS-EXPERIMENT / REJECTED, and the character length of your old vs new slice (A to E) or the files you edited (APP).
