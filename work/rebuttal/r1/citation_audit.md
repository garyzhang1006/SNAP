# Citation audit, round 1

Scope: `deliverables/references.tex` (thebibliography, 54 entries) against every `\citep`/`\citet` in `main.tex`, `appendix_a.tex` (no cites), `appendices_bcd.tex`, plus `supplement_extended_body.tex` for completeness. All 54 entries are cited at least once, so there is no uncited residual.

Method note: the skill's Codex step failed (`codex exec` returned `The 'gpt-5.6-terra' model requires a newer version of Codex`), so every check below was done directly. Existence and metadata came from the arXiv export API (all 18 arXiv IDs fetched in one batch), Crossref DOIs, the Semantic Scholar batch API (venue and DBLP keys), ACL Anthology, and publisher pages. DBLP's own API refused connections. Context checks that hinge on a specific section or figure were read from the cited PDF text (Dodge 4.3, Zhou Fig. 3, Jordan App. C, DataDecide Table/appendix, Heineman full text, OLMo 2 Section 4.5).

Totals: KEEP 52, FIX 2, REPLACE 0, REMOVE 0. No entry is fabricated, and every 2026 arXiv preprint resolves with matching title and author list.

## Per-entry verdicts

| Key | Verdict | Note | Evidence |
|---|---|---|---|
| agarwal2021 | KEEP | NeurIPS 34, pp. 29304-29320 match | https://arxiv.org/abs/2108.13264 (S2 journal pages 29304-29320) |
| bell2002 | KEEP | Survey Methodology 28(2):169-181 matches | https://www150.statcan.gc.ca/n1/pub/12-001-x/2002002/article/9058-eng.pdf |
| biderman2023 | KEEP | ICML 2023, PMLR 202; DBLP key conf/icml/BidermanSABOHKP23 | https://arxiv.org/abs/2304.01373 |
| bouthillier2021 | KEEP | 17 authors in the listed order; MLSys 2021 | https://arxiv.org/abs/2103.03098 |
| brennan2001 | KEEP | Standard Springer monograph (Statistics for Social Science and Public Policy) | not looked up online; standard reference |
| brown1910 | KEEP | BJP 3(3):296-322 | https://doi.org/10.1111/j.2044-8295.1910.tb00207.x |
| bui2025 | KEEP | IJCNLP-AACL 2025 short, pp. 41-46; anthology lists "Nghia Tuan Bui, Guergana K Savova" (initials only differ) | https://aclanthology.org/2025.ijcnlp-short.3/ |
| burnell2023 | KEEP | Science 380(6641):136-138 | https://doi.org/10.1126/science.adf6369 |
| cameron2008 | KEEP | REStat 90(3):414-427 | https://doi.org/10.1162/rest.90.3.414 |
| campbell1959 | KEEP | Psych. Bull. 56(2):81-105 | https://doi.org/10.1037/h0046016 |
| card2020 | KEEP | EMNLP 2020 pp. 9263-9274 | https://doi.org/10.18653/v1/2020.emnlp-main.745 |
| cheverud1988 | KEEP | Evolution 42(5):958-968 | https://doi.org/10.2307/2408911 |
| cheverud2001 | KEEP | Heredity 87(1):52-58 | https://doi.org/10.1046/j.1365-2540.2001.00901.x |
| cronbach1951 | KEEP | Psychometrika 16(3):297-334 | https://doi.org/10.1007/bf02310555 |
| dehghani2021 | KEEP | arXiv-only is correct | https://arxiv.org/abs/2107.07002 |
| demsar2006 | KEEP | JMLR 7:1-30 | https://jmlr.org/papers/v7/demsar06a.html (standard; S2 lookup refused) |
| dodge2020 | KEEP | arXiv-only is correct; Section 4.3 "Globally good initializations" uses four GLUE tasks (CoLA, RTE, MRPC, SST), matching both uses | https://arxiv.org/abs/2002.06305 |
| dror2017 | KEEP | TACL 5:471-486 | https://doi.org/10.1162/tacl_a_00074 |
| dufour2026 | KEEP | arXiv 2606.20536, authors match; abstract separates training-seed from sampling-seed variation of FID | https://arxiv.org/abs/2606.20536 |
| gorman2019 | KEEP | ACL 2019 pp. 2786-2791 | https://doi.org/10.18653/v1/p19-1267 |
| hagmann2023 | KEEP | ICLR 2023 per S2 venue | https://arxiv.org/abs/2302.04054 |
| hardy2026 | KEEP | arXiv 2605.25272, 9 authors match; CFA and G-theory on 4,000+ Open LLM Leaderboard models | https://arxiv.org/abs/2605.25272 |
| haupt2026 | KEEP | arXiv 2605.30916; uses "the PolyPythias 410M panel for variance" | https://arxiv.org/abs/2605.30916 |
| hedges2010 | KEEP | RSM 1(1):39-65 | https://doi.org/10.1002/jrsm.5 |
| heineman2025 | KEEP | NeurIPS 2025 per S2; full text has no benchmark-covariance estimate, so the "don't estimate covariance between benchmarks" claim holds | https://arxiv.org/abs/2508.13144 |
| henderson2018 | KEEP | AAAI 32(1) | https://doi.org/10.1609/aaai.v32i1.11694 |
| hochlehnert2025 | KEEP | COLM 2025 confirmed | https://github.com/bethgelab/sober-reasoning ; https://arxiv.org/abs/2504.07086 |
| hofmann2025 | KEEP | COLM 2025 per arXiv comment | https://arxiv.org/abs/2509.11106 |
| jordan2024 | KEEP | ICLR 2024 (DBLP key conf/iclr/Jordan24); App. C covers five ImageNet eval sets with max pairwise R^2 = 0.14 (ImageNet-R vs -Sketch), matching the supplement exactly | https://arxiv.org/abs/2304.01910 |
| karamcheti2021 | KEEP | CRFM post lists the same 14 authors, 5 GPT-2 Small + 5 Medium runs, "610 checkpoints for each model", WikiText-103 and OpenWebText validation | https://crfm.stanford.edu/2021/08/26/mistral.html |
| kipnis2024 | KEEP | ICLR 2025 per arXiv comment; abstract gives the r = 0.94 factor-total correlation. Key says 2024 but the rendered label says 2025, which is harmless | https://arxiv.org/abs/2407.12844 |
| kish1965 | KEEP | Standard Wiley monograph | not looked up online; standard reference |
| kohli2026 | KEEP | arXiv 2605.29800; nine judges, about two independent votes | https://arxiv.org/abs/2605.29800 |
| li2005 | KEEP | Heredity 95(3):221-227 | https://doi.org/10.1038/sj.hdy.6800717 |
| mackinnon2017 | KEEP | JAE 32(2):233-254 | https://onlinelibrary.wiley.com/doi/abs/10.1002/jae.2508 |
| madaan2024 | KEEP | arXiv-only is correct (no venue in S2) | https://arxiv.org/abs/2406.10229 |
| magnusson2025 | KEEP | ICML 2025; text says sizes below 1B are "stopped early at 25% of the compute used to train the 1B model for all but the default seed", which matches appendices_bcd.tex:6 | https://arxiv.org/abs/2504.11393 |
| martin1977 | KEEP | Heredity 38(1):79-95 | https://doi.org/10.1038/hdy.1977.9 |
| mccoy2020 | KEEP | BlackboxNLP 2020 pp. 217-227 | https://doi.org/10.18653/v1/2020.blackboxnlp-1.21 |
| messing2026 | KEEP | arXiv 2604.11581 (v6); abstract reports naive SEs 40-60% smaller than corrected SEs | https://arxiv.org/abs/2604.11581 |
| miller2024 | KEEP | arXiv 2411.00640, single author | https://arxiv.org/abs/2411.00640 |
| nyholt2004 | KEEP | AJHG 74(4):765-769 | https://doi.org/10.1086/383251 |
| reimers2017 | KEEP | EMNLP 2017 pp. 338-348 | https://doi.org/10.18653/v1/d17-1035 |
| schaeffer2023 | KEEP | NeurIPS 36 | https://arxiv.org/abs/2304.15004 |
| searle1992 | KEEP | Standard Wiley monograph | not looked up online; standard reference |
| sellam2022 | FIX | Author order is wrong. arXiv and the ICLR 2022 record give Sellam, Yadlowsky, Wei, Saphra, D'Amour, Linzen, Bastings, Turc, Eisenstein, Das, **Tenney**, Pavlick; the bib moves Ian Tenney to third place | https://arxiv.org/abs/2106.16163 ; https://iclr.cc/virtual/2022/spotlight/6292 |
| sha2026 | KEEP | arXiv 2603.29357; Effective Dimensionality across 8,400+ model evaluations | https://arxiv.org/abs/2603.29357 |
| spearman1904 | KEEP | AJP 15(1):72-101 | https://doi.org/10.2307/1412159 |
| spearman1910 | KEEP | BJP 3(3):271-295 | https://doi.org/10.1111/j.2044-8295.1910.tb00206.x |
| teamolmo2025 | KEEP | arXiv 2501.00656, COLM 2025 short version per arXiv comment | https://arxiv.org/abs/2501.00656 |
| vanderwal2025 | KEEP | ICLR 2025, 7 authors match; 9 new seeds at 5 sizes, seed sets initialisation and data order jointly | https://arxiv.org/abs/2503.09543 |
| zhao2026 | FIX | The title reads "at 1--3b" in the bib but the arXiv title is "1-3B", so the rendered text shows a lowercase b | https://arxiv.org/abs/2605.20798 |
| zhou2020 | KEEP | EMNLP 2020 pp. 8215-8228 (the entry is correct, but see CI1 for the appendix sentence) | https://doi.org/10.18653/v1/2020.emnlp-main.659 |

## Context-misuse table

| ID | Severity | Likely to lower score | Location | Verbatim quote | Problem | Fix |
|---|---|---|---|---|---|---|
| CI1 | Medium | no (yes if a reviewer knows Zhou et al.) | appendices_bcd.tex:73 | "The Spearman matrix of \citet[Figure 3]{zhou2020} averages checkpoints across seeds, mixing checkpoint progress with seed deviations." | Zhou et al. compute, for each seed, a Spearman correlation over the T checkpoints of that seed's training curve, then average these per-seed correlations over seeds (Corr_ij = (1/\|S\|) Σ_s Spearman over t). No seed deviations enter the statistic, so the "mixing" claim misreads their definition. | Say instead that their Figure 3 averages per-seed Spearman correlations computed over training checkpoints, which measures co-movement along a training trajectory rather than covariance of seed deviations at a fixed step. |
| CI2 | Low-Medium | no | appendices_bcd.tex:73 | "\citet{dufour2026}, \citet{miller2024}, and \citet{zhao2026} address training versus sampling variation, item-level uncertainty for one model, and per-task tests without cross-task covariance." | Miller's abstract covers "measuring differences between two models" (paired analysis) and clustered standard errors as well as the single-model case, so "for one model" understates it. Miller's clustered-SE treatment of correlated questions is the closest evaluation-stats analogue to SNAP, and a reviewer who knows it may say the paper downplays it. | Describe it as item-sampling uncertainty, including clustered and paired two-model comparisons, and add that it treats run variance as fixed and does not estimate covariance across benchmarks. |
| CI3 | Low | no | appendices_bcd.tex:70 | "The OLMo-2 checkpoints considered here lack replicates at matched steps \citep{teamolmo2025}." | OLMo 2 Section 4.5 trains three midtraining "soup" ingredients per mix that differ only in data order (for example "3 x soup", "different data order seeds"). Those are partial replicates at matched steps. The hedge "considered here" helps, but the citation alone doesn't back an absence claim. I did not verify whether the ingredient checkpoints are public. | Name what is missing: no pretraining-seed replicates, since the midtraining soup ingredients share one stage-1 checkpoint and vary only data order. |
| CI4 | Low | no | appendices_bcd.tex:213 | "The bootstrap-t addresses concerns associated with few-cluster approximations, as discussed by \citet{bell2002}, but it doesn't guarantee coverage at 25 clusters." | Bell and McCaffrey propose bias-reduced linearization (CR2) with small-sample degrees of freedom, and their paper does not cover the bootstrap-t. The citation fits the "concerns" but readers may take it as support for the method. | Cite bell2002 and cameron2008 for the few-cluster concern and cameron2008 for bootstrap-t refinements, for example "few-cluster bias in sandwich variances \citep{bell2002} motivates the bootstrap-t \citep{cameron2008}". |
| CI5 | Low | no | appendices_bcd.tex:75 | "\citet{hardy2026}, \citet{kohli2026}, \citet{messing2026}, and \citet{sha2026} measure dependence across models, judges, or prompts" | Messing decomposes variance by source (judge choice, temperature, prompt phrasing) and does not estimate dependence between those sources. The other three do measure dependence. | Write "measure dependence across models or judges, or variance from prompt and judge choice \citep{messing2026}". |
| CI6 | Low | no | appendices_bcd.tex:77; main.tex:264 | "The cross-half identity follows \citet{spearman1904}" | Spearman 1904 corrects attenuation with repeated measurements, and the split-half idea is usually attributed to Spearman 1910 / Brown 1910 and to Cronbach 1951. This is defensible but loose. | Change the text to "follows the repeated-measurement correction of \citet{spearman1904} and the split-half construction of \citet{spearman1910,brown1910}". |

The following uses were checked and SUPPORT their sentences: bouthillier2021 (correlated-training variance with five case studies), dodge2020 (both uses), jordan2024 (both uses, App. C numbers exact), heineman2025 (both uses, and its full text contains no benchmark-covariance estimate), madaan2024, reimers2017, hagmann2023, bui2025, hochlehnert2025, magnusson2025 (25% early stop exact), vanderwal2025, sellam2022, mccoy2020, biderman2023, karamcheti2021 (all counts exact), haupt2026, hardy2026, kohli2026, sha2026, dufour2026, zhao2026 (the abstract has a multi-seed noise floor, and I did not check the App. E.4 detail), kipnis2024 (0.94 exact), hofmann2025, cheverud1988/2001, nyholt2004, li2005, martin1977, cameron2008, mackinnon2017, kish1965, searle1992, brennan2001, campbell1959, cronbach1951, brown1910/spearman1910, hedges2010, schaeffer2023, dehghani2021, demsar2006, dror2017, card2020, gorman2019, burnell2023, henderson2018, agarwal2021.

One positioning risk that isn't a misuse: Jordan (2024) App. C finds near-independence of run deviations across five ImageNet evaluation sets (all pairs R^2 < 0.01 except one at 0.14). That is the nearest published measurement of cross-benchmark run covariance, and its result points the other way from SNAP's margin finding. The main-text sentence (main.tex:262) mentions it only in passing, so a reviewer may ask why the two results differ. One sentence in related work contrasting the two (vision vs LM, accuracy vs margins, different seed sources) would head this off.

## Verified missing work

Each of these was confirmed to exist via the arXiv export API this session. They are ranked by how likely a reviewer is to raise them.

1. Fehlauer, Mahowald, Pimentel. "Convergence and Divergence of Language Models under Different Random Seeds." EMNLP 2025. https://arxiv.org/abs/2509.26643 . This is recent work on LM pretraining seed variability, the same object SNAP studies.
2. Bowyer, Aitchison, Ivanova. "Position: Don't Use the CLT in LLM Evals With Fewer Than a Few Hundred Datapoints." ICML 2025 spotlight. https://arxiv.org/abs/2503.01747 . It covers small-sample interval coverage in LLM evals and fits beside the few-cluster calibration discussion.
3. Biderman, Schoelkopf, Sutawika, Gao, et al. "Lessons from the Trenches on Reproducible Evaluation of Language Models." 2024. https://arxiv.org/abs/2405.14782 . This is the standard reference for reporting standard errors in lm-eval-harness practice.
4. Zhang and Hardt. "Inherent Trade-Offs between Diversity and Stability in Multi-Task Benchmarks." ICML 2024. https://arxiv.org/abs/2405.01719 . It studies aggregation across benchmarks in a battery.
5. Ruan, Maddison, Hashimoto. "Observational Scaling Laws and the Predictability of Language Model Performance." NeurIPS 2024. https://arxiv.org/abs/2405.10938 . It shows a low-dimensional capability structure across benchmarks between models, the cross-model counterpart the paper already contrasts with hardy2026 and sha2026.
6. Burnell, Hao, Conway, Hernandez-Orallo. "Revealing the Structure of Language Model Capabilities." 2023. https://arxiv.org/abs/2306.10062 . A factor analysis of HELM, in the same cross-model group.
7. Ilić and Gignac. "Evidence of interrelated cognitive-like capabilities in large language models" (published in Intelligence per the search snippet, which I did not check). https://arxiv.org/abs/2310.11616 . It reports a g factor across benchmarks.
8. Perlitz et al. "Do These LLM Benchmarks Agree? Fixing Benchmark Evaluation with BenchBench." 2024. https://arxiv.org/abs/2407.13696 .
9. Summers and Dinneen. "Nondeterminism and Instability in Neural Network Optimization." ICML 2021. https://arxiv.org/abs/2103.04514 . It decomposes run-to-run variance by source.
10. Polo et al. "tinyBenchmarks: evaluating LLMs with fewer examples." ICML 2024. https://arxiv.org/abs/2402.14992 ; Gu et al. "OLMES: A Standard for Language Model Evaluations." Findings of NAACL 2025. https://arxiv.org/abs/2406.08446 ; Sclar et al. "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design." ICLR 2024. https://arxiv.org/abs/2310.11324 . These are lower priority and could each be a one-clause mention.

UNVERIFIED candidates, none of which I located this session: Dror et al. 2018 "The Hitchhiker's Guide to Testing Statistical Significance in NLP" (ACL 2018), and Picard 2021 "torch.manual_seed(3407) is all you need" (the latter exists at https://arxiv.org/abs/2109.08203 but is a weak fit).
