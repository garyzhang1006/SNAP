# Citation audit, round 3

Scope: every `\citep`/`\citet` on a line changed between e33a01d and f23e293 in `deliverables/` (main.tex:37, 129, 230; appendices_bcd.tex:73; supplement_extended_body.tex:127), the two edited bibliography entries (fehlauer2025, ruan2024), and a context sweep of all remaining citation sentences in main.tex, appendix_a.tex (no citations), appendices_bcd.tex, and supplement_extended_body.tex (which main.tex does not `\input`). Entries that rounds 1 and 2 verified as KEEP were not re-verified for metadata.

Method: done directly without Codex. Crossref for the EMNLP record, the NeurIPS 2024 proceedings index and abstract page for Ruan et al., and arXiv HTML full text for Zhao et al. (2605.20798) and Miller (2411.00640). DBLP returned a bot challenge and Semantic Scholar returned HTTP 429, so neither was used.

## Entry verdicts

| Key | Verdict | Evidence | Note |
|---|---|---|---|
| fehlauer2025 | KEEP | https://doi.org/10.18653/v1/2025.emnlp-main.1675 (Crossref: title, Fehlauer/Mahowald/Pimentel, EMNLP 2025 proceedings, page 32970-32979) | The added pp. 32970--32979 match Crossref exactly. |
| ruan2024 | KEEP | https://proceedings.neurips.cc/paper_files/paper/2024/hash/1cded4f97cf5f01a284c574110b7e3b9-Abstract-Conference.html | Listed under "Advances in Neural Information Processing Systems 37", Main Conference Track, authors Ruan, Maddison, Hashimoto, so "volume 37" is correct. The proceedings page misspells "Langauge" in the title, and the bib correctly keeps the arXiv spelling. |
| brennan2001 | KEEP | round 1 | Newly cited in main.tex:230 for generalizability theory, which is the book's subject. |
| cronbach1951 | KEEP | round 1 | Removed from main.tex:230 but still cited at appendices_bcd.tex:77, so it is not orphaned. |
| zhao2026, miller2024, magnusson2025, vanderwal2025, spearman1904, spearman1910, brown1910, searle1992, and the other keys in edited sentences | KEEP | rounds 1-2 | Metadata unchanged this round. |

## Context checks on edited text

Supported:

- zhao2026, appendices_bcd.tex:73 rewrite. Section 3.3 sets the significance threshold from "three independent seeds" of the baseline on the CLIMB-12 macro-average, and Appendix E.4 combines "12 per-task one-sided p-values via Stouffer's Z" from per-task Welch tests. The supplement_extended_body.tex:127 wording is also supported (https://arxiv.org/html/2605.20798). One small wording issue is logged as CI2.
- miller2024, appendices_bcd.tex:73, supplement_extended_body.tex:127, main.tex:228. Miller's recommendations include clustered standard errors and question-level paired differences for two-model comparisons (Sections 2.2 and 4.2, Appendix A), which matches the new wording (https://arxiv.org/html/2411.00640). A nuance is logged as CI3.
- main.tex:230. Spearman 1904 is now described as the attenuation correction, Spearman 1910/Brown 1910 as the split-half construction, and Searle plus Brennan as variance components and G-theory. This resolves round-2 CI3.
- main.tex:37. "five of its model sizes, each with three released replicates" resolves round-2 CI4.
- main.tex:129. The vanderwal2025 wording change is cosmetic, and round 2 already verified nine seeds at five sizes with the seed setting initialisation and data order together.

## Context sweep, whole paper

The other citation sentences in main.tex:228-232, appendices_bcd.tex:6, 70, 75, 77, 211, 213, 300, and supplement_extended_body.tex:3-145 are consistent with the round-1 and round-2 evidence. I checked the hofmann2025/heineman2025 "seven authors shared" claim (supplement:145) against references.tex, and the two author lists overlap in exactly seven names (Hofmann, Heineman, Magnusson, Lo, Dodge, Hajishirzi, Smith).

| ID | Severity | Likely to lower score | Location | Verbatim quote | Problem | Fix |
|---|---|---|---|---|---|---|
| CI1 | Medium | yes | main.tex:228 | "\citet{jordan2024} finds run deviations in accuracy nearly independent across ImageNet evaluation sets ... We know of no study that estimates the covariance of run noise between benchmarks" | The novelty sentence contradicts a citation two sentences earlier in the same paragraph. Jordan's Appendix C does estimate run-deviation dependence ($R^2$) across five ImageNet evaluation sets, and the main text drops the "shifted versions of one benchmark" qualifier that appendices_bcd.tex:73 and supplement:125 use. A reviewer reading only the main text will see a novelty claim undercut by the paper's own citation. | "\citet{jordan2024} finds run deviations in accuracy nearly independent across shifted ImageNet test sets ... Apart from such shifted test sets, we know of no study that estimates the covariance of run noise between distinct benchmarks or an effective benchmark count from that covariance." |
| CI2 | Low | no | appendices_bcd.tex:73 | "combine per-task Welch tests by Stouffer's method, noting positive task correlation without estimating it" | Zhao et al. do not report that tasks are positively correlated. They write that "Stouffer combination is conservative under positively-correlated tasks", which is a conditional caveat and not an observation. | "..., noting that positive task correlation would make the combination conservative, without estimating that correlation." |
| CI3 | Low | no | appendices_bcd.tex:73; supplement:127; main.tex:228 | "treats item-sampling uncertainty with clustered and paired two-model comparisons while holding run variance fixed" | Miller never mentions training runs or seeds. The model is treated as a fixed object, and the only model-side randomness is answer sampling, which Section 3.1 reduces by resampling. "Holding run variance fixed" implies that Miller models run variance and then conditions on it. This is defensible but loose. | "... while treating each evaluated model as fixed" (main.tex: "with each model treated as fixed"). |
| CI4 | Low | no | supplement_extended_body.tex:135 | "\citet{henderson2018} and \citet{agarwal2021} address seed sensitivity ... The authors resample runs within tasks, with an additional task-resampling variant in their Appendix A.5" | "The authors" is ambiguous between two cited papers, and I did not verify the Appendix A.5 pointer or which paper it belongs to (UNVERIFIED; most likely Agarwal et al., whose stratified bootstrap resamples runs within tasks). This file is not `\input` by main.tex, so the issue matters only if the supplement ships. | "\citet{agarwal2021} resample runs within tasks, with an additional task-resampling variant in their Appendix A.5" after checking the appendix number. |

No citation in the edited text is fabricated, points to the wrong paper, or carries wrong metadata. Rounds 1-2 issues CI1-CI6 (round 1) and CI1-CI4 (round 2) are resolved in the current text.
