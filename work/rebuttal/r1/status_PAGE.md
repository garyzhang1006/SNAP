# Status, PAGE (round 1, R1-01)

Files edited: deliverables/main.tex, deliverables/appendix_a.tex, deliverables/appendices_bcd.tex. No number was added or changed, and the \outcome and \pending machinery is untouched.

Cuts applied (paper_audit.md plan):

- C1 abstract: already done by section A (R1-07), nothing further cut.
- C2 Table `tab:decision`: moved as a float to `app:decision` (appendices_bcd.tex, before "Runs per configuration"), placement changed from [t] to [!htb]. The Sec 4.5 decision paragraph now cites "Table~\ref{tab:decision} in Appendix~\ref{app:decision}".
- C3 held-out scoring paragraph (old l.208): deleted the RTX 3090, torch 2.14.0 and batch-check sentence, which `app:heldout` already reports in full. The partial-scope sentence (1.152 to 1.203) is kept and merged into the end of the preceding Sec 4.2 paragraph, with a pointer to `app:heldout` for the five scopes, the hardware and the power simulation. "The later power calculation can't rescue this registered test" is folded into that pointer.
- C4 calibration and external checks paragraph (old l.229): the calibration sentences (1.0009, 1.0004, slope 0.998, re-split SDs 0.002 and 0.008, schedule-confounding caveat) moved verbatim to the opening of `app:calibration`. The earlier PolyPythias rescore (1.414, 1.262 with its interval, 1.711 with its interval, unbounded inversion) was deleted because `app:transport` reports it (1.41372, 1.26199, 0.927 to 1.537, 1.71085, 0.869 to 2.428, unbounded accuracy sets). The Heineman panel sentence was deleted because Table `tab:original12` in the external random-seed panel paragraph reports 1.705, 1.625, 0.989 and 0.868 with the same caveats. Subsection renamed "Scoring format and mechanism".
- C5 mechanism paragraph (old l.227), from "The fit is in sample" to the end: replaced by one sentence pointing to `app:formatfit`. The leave-one-out result (within 0.054, overstates in nine of ten) lives in `app:formatfit`, the practitioner-use caveat in the Discussion's format-fit fallback sentence and in `app:formatfit`, the gain and competence pointer in the Table 1 caption and `app:proxy`. The sign-score interval \ci{0.992}{1.158} was only in main.tex, so it moved into the `app:scale` sentence that already gives 1.079.
- C6 later interval checks (old l.124): replaced by one sentence pointing to `app:calibration` and `app:derivations`. Test inversion (0.935 to 0.956, 1.095 to 1.323, 0.995 to 1.162) and the residual-scaled interval (0.943 to 0.958, chosen after four cells) are in `app:calibration`. Recipe influence (3.08, 0.520, 0.037) is in appendix_a.tex "Pooling and finite-sample bias", where I added the recipe name dolma1.7-no-math-no-code, which only main.tex carried. The size-band cluster intervals are in Table 1 (section C's R1-39 fix).
- C7 information ratio (old l.114 to 118): the paragraph and its equation moved verbatim to appendix_a.tex "Planning calculations and information ratio", ahead of the derivation paragraph, with `\label{eq:information}` restored on the equation. The main-text subsection is renamed "Interval inference".
- `eq:effective`: label restored on the $\bar r_E$ equation in Sec 2.2 (main.tex), which appendix_a.tex cites.
- C8 to C14: not needed, held in reserve.

Result (latexmk, maintext:end page in the .aux):

| \Ronecase | \Rtwocase | page |
|---|---|---|
| 1 | 1 | 9 |
| 1 | 2 | 9 |
| 1 | 3 | 9 |
| 2 | 1 | 9 |
| 2 | 2 | 9 |
| 2 | 3 | 9 |

Default build (switches at 0, every variant printed): maintext:end on page 10, 0 undefined references in main.log (eq:effective and eq:information now resolve). Slack in combos 12 and 22 is about five lines at the foot of page 9, and filled \pending values are shorter than their placeholders.
