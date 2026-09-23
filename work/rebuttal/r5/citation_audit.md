# Round 5 citation audit

Scope: the 17 bibitems added in fceef7c (`git diff 2becd1b fceef7c -- deliverables/references.tex`), every `\citep`/`\citet` on text changed by that commit in main.tex, appendices_bcd.tex and supplement_extended_body.tex, and a context sweep of every citing sentence in main.tex, appendix_a.tex and appendices_bcd.tex. Done directly without Codex. DBLP timed out, so metadata was not re-fetched; instead each of the 17 committed bibitems was compared string for string against the VERIFIED block in work/rebuttal/r4/citation_audit.md, and all 17 match in both label and body.

## Rendering and bibliography integrity

- The diff adds exactly 17 bibitems: bisk2020piqa, clark2018arc, clark2019boolq, dua2019drop, gu2025olmes, hendrycks2021mmlu, liu2020logiqa, mihaylov2018openbookqa, pal2022medmcqa, reddy2019coqa, sakaguchi2020winogrande, sap2019socialiqa, talmor2019commonsenseqa, wang2022lsat, welbl2017sciq, zellers2019hellaswag, zhong2024agieval.
- references.tex holds 73 bibitems with no duplicate keys, and the list stays in alphabetical order by label and year.
- Across main.tex, appendix_a.tex and appendices_bcd.tex there are no undefined keys and no uncited bibitems, and each new key is cited exactly once (main.tex:41, 43, 117, 175; appendices_bcd.tex:399).
- main.log (04:29:56) is newer than every input file (latest main.tex at 04:29:54), and it contains no `Warning`, `undefined` or `multiply` lines. The PDF text shows every new entry rendered with its author-year label.
- `\begin{thebibliography}{60}` now wraps 73 items. natbib author-year ignores that argument, so it has no visible effect.

## Context table

| id | severity | likely to lower score | location | verbatim quote | problem | fix |
|---|---|---|---|---|---|---|
| CI1 | Moderate | yes | main.tex:117 | "Social IQa, and WinoGrande \citep{clark2018arc,clark2019boolq,talmor2019commonsenseqa,...}" | natbib merges the first two keys because both labels read "Clark et al.", so the PDF prints "(Clark et al., 2018; 2019; Talmor et al., 2019; ...)". That rendering credits BoolQ (Christopher Clark, Lee, Chang et al.) to the ARC authors (Peter Clark, Cowhey, Etzioni et al.), a misattribution that benchmark authors on the committee can spot. The single list placed after "WinoGrande" also reads as nine citations for WinoGrande. | Cite each benchmark after its name: "ARC-Challenge and ARC-Easy \citep{clark2018arc}, BoolQ \citep{clark2019boolq}, CommonsenseQA \citep{talmor2019commonsenseqa}, HellaSwag \citep{zellers2019hellaswag}, MMLU \citep{hendrycks2021mmlu}, OpenBookQA \citep{mihaylov2018openbookqa}, PIQA \citep{bisk2020piqa}, Social IQa \citep{sap2019socialiqa}, and WinoGrande \citep{sakaguchi2020winogrande}". Separating the two Clark keys into different `\citep` calls stops the merge. |
| CI2 | Low | no | main.tex:41 | "and multiple-choice DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa}" | Dua et al. and Reddy et al. release generative reading-comprehension tasks, and the multiple-choice versions come from the harness (appendices_bcd.tex:399 says OLMES builds every prompt). The sentence credits the MC format to the dataset papers. Who first built the MC conversions was not verified this round. | "and DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa} in their OLMES multiple-choice form". |
| CI3 | Low | no | supplement_extended.tex:28 | "\input{references.tex}" | The supplement shares references.tex, so its bibliography now lists all 17 new entries even though supplement_extended_body.tex cites none of them. This matters only if the supplement ships as a standalone PDF. | Leave as is if the supplement stays internal. Otherwise cite the benchmarks at their first table mention in the supplement (for example, the ARC-Challenge row at supplement_extended_body.tex:39) or give the supplement its own bibliography file. |

## Checked and clean

- appendices_bcd.tex:399: LogiQA-en is AGIEval's English LogiQA split, taken from Liu et al. (2020), and AGIEval credits LSAT-LR to Wang et al. (2022), so both new citations support their sentences.
- main.tex:175: `\citep{zhong2024agieval}` sits directly on "two AGIEval reasoning tasks", which is correct.
- main.tex:43: OLMES (Gu et al., 2025) is the evaluation standard and harness used to build the 6,808-item bank, which is correct. main.tex:129 mentions OLMES again after the first citation, so it needs no second one.
- main.tex:41: SciQ and MedMCQA are cited at their first mention, and both are correct.
- main.tex:228: the r4 CI1 rewrite landed as "which neither \citet{miller2024} nor \citet{heineman2025} estimates". It now attaches to the estimand and makes no claim about pretraining runs, so it is accurate.
- main.tex:230: "\citet{heineman2025} relate per-benchmark signal and noise on DataDecide and OLMo checkpoints to decision accuracy" is accurate, and dropping the old "without estimating covariance" clause removed a claim that could be contested.
- supplement_extended_body.tex:135: "Both resample runs within tasks" fixes the r4 CI3 ambiguity and drops the unverified Appendix A.5 pointer.
- None of the remaining citing sentences in main.tex, appendix_a.tex or appendices_bcd.tex has a new context problem. Their entries were verified KEEP in rounds 2 to 4, and this round did not re-fetch their metadata.
