# Citation audit, round 2

Scope: the five entries added or edited this round (fehlauer2025, ruan2024, burnell2023revealing, sellam2022, zhao2026), every `\citep`/`\citet` on a line of `main.tex` or `appendices_bcd.tex` changed since commit 27198cd (10 added lines), and a sweep of the round-1 context findings across `main.tex`, `appendices_bcd.tex`, `supplement_extended_body.tex` (`appendix_a.tex` has no citations). Round-1 KEEP verdicts with URLs were not re-verified.

Method: arXiv export API for metadata and abstracts, arXiv HTML full text for OLMo 2 (2501.00656) and Zhao et al. (2605.20798), Crossref for the EMNLP record. DBLP timed out and Semantic Scholar returned HTTP 429, so NeurIPS 2024 for ruan2024 rests on the arXiv comment. Codex was not used.

## Entry verdicts

| Key | Verdict | Evidence | Note |
|---|---|---|---|
| fehlauer2025 | KEEP (optional FIX) | https://arxiv.org/abs/2509.26643 ; https://doi.org/10.18653/v1/2025.emnlp-main.1675 | Title, three authors in order, and EMNLP 2025 main all match. Crossref gives pp. 32970--32979, which the entry omits. |
| ruan2024 | KEEP | https://arxiv.org/abs/2405.10938 | Title and three authors match; arXiv comment reads "Accepted at NeurIPS 2024 as a spotlight". Volume 37 could be added. |
| burnell2023revealing | KEEP | https://arxiv.org/abs/2306.10062 | Title and four authors match (arXiv writes "Jose Hernandez Orallo" without hyphen). arXiv lists no journal ref; I found no venue version, so arXiv-only stands. The 2023a/2023b labels disambiguate correctly from burnell2023 (Science). |
| sellam2022 | KEEP (round-1 FIX resolved) | https://arxiv.org/abs/2106.16163 | The 12-author order now matches arXiv exactly, with Tenney eleventh. ICLR 2022 per arXiv comment. |
| zhao2026 | KEEP (round-1 FIX resolved) | https://arxiv.org/abs/2605.20798 | `1--3{B}` now matches the arXiv title "1-3B"; five authors match. See CI1 for the context problem. |

## Context checks on edited text

Supported: fehlauer2025 as seed-variability work (per-token KL across pretraining seeds, four-phase convergence), ruan2024 and burnell2023revealing for "a low-dimensional capability structure" across models (Ruan: low-dimensional capability space from about 100 models; Burnell: three factors from 29 LLMs on 27 tasks), sellam2022 for 25 seeds of one configuration, teamolmo2025 for the new soup clause (Section 2.3 says the mid-training step is repeated "multiple times with different random data orders" before averaging, and Section 4.5 tabulates "3 x soup" per mix), miller2024 in both edited appendix and main-text wording, messing2026 split from the dependence group, spearman1904/spearman1910/brown1910 in appendices_bcd.tex:77, bell2002 plus cameron2008 at appendices_bcd.tex:213, vanderwal2025 ("9 new seeds across 5 model sizes", seed fixes initialisation and data order), and the remaining related-work citations, which round 1 already verified and whose sentences changed only in wording.

| ID | Severity | Likely to lower score | Location | Verbatim quote | Problem | Fix |
|---|---|---|---|---|---|---|
| CI1 | Medium | yes, if a reviewer reads Zhao et al. | appendices_bcd.tex:73 | "\citet{zhao2026} test tasks one at a time without cross-task covariance." | Zhao's primary test is a three-seed bootstrap and Welch test on the CLIMB-12 macro-average (Section 3.3), and the per-task Welch tests appear only as a cross-check combined by Stouffer in Appendix E.4. That appendix also says "Stouffer combination is conservative under positively-correlated tasks", so they acknowledge cross-task correlation without estimating it. "One at a time" misstates the design and also contradicts supplement_extended_body.tex:127, which describes it correctly. | "\citet{zhao2026} set a three-seed noise floor on a twelve-task average and combine per-task Welch tests by Stouffer's method, noting positive task correlation without estimating it." |
| CI2 | Low | no | supplement_extended_body.tex:127 | "\citet{miller2024} estimates item-level uncertainty for one model." | This is the round-1 CI2 wording, which was fixed in appendices_bcd.tex:73 and main.tex:232 but left in the supplement. Miller covers clustered errors and paired two-model comparisons. | Copy the appendix wording: "treats item-sampling uncertainty with clustered and paired two-model comparisons while holding run variance fixed". |
| CI3 | Low | no | main.tex:234 | "the variance-component ideas of \citet{spearman1904}, \citet{cronbach1951}, and \citet{searle1992}" | Searle fits "variance-component ideas", but Spearman 1904 is the attenuation correction and Cronbach 1951 is coefficient alpha, and neither frames reliability as variance components (that comes later with generalizability theory, which brennan2001 covers). appendices_bcd.tex:77 already describes both accurately. | "the attenuation correction of \citet{spearman1904}, the random-split reliability of \citet{cronbach1951}, and the variance components of \citet{searle1992}". |
| CI4 | Low | no | main.tex:37 | "DataDecide \citep{magnusson2025}, with 25 data recipes and five model sizes that each have three released replicates" | The sentence reads as a description of DataDecide as a whole, which spans more sizes (up to 1B), and below 1B two of the three replicates stop at 25 percent of the 1B budget (appendices_bcd.tex:6). The main text handles the truncation through the shared-step rule, so this is wording only. | "with 25 data recipes and five of its model sizes, each with three released replicates". |

No citation in the edited text is fabricated or points to the wrong paper.
