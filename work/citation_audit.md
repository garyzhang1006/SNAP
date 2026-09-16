# Targeted citation audit

Verified on 2026-09-13 using official arXiv records and the publisher's Lynch article. This is a targeted audit of nine entries, not verification of every reference or reproduction of source experiments. All eight requested arXiv identifiers resolve to the expected papers. No fabricated reference was found in this subset.

| Entry | Metadata verified against primary source | Support and correction |
| --- | --- | --- |
| Sha and Zhao, 2026 | [2603.29357](https://arxiv.org/abs/2603.29357), Tommy Sha and Stella Zhao, *BenchScope: How Many Independent Signals Does Your Benchmark Provide?* | Abstract supports ED 1.7 for the six-score Open LLM Leaderboard. It explicitly treats ED as a screening statistic rather than a literal factor count. Avoid equating 1.7 with proven independent latent dimensions. |
| Dufour et al., 2026 | [2606.20536](https://arxiv.org/abs/2606.20536), Nicolas Dufour, Alexei A. Efros, Patrick Pérez, *The FID Lottery: Quantifying Hidden Randomness in Generative-Model Evaluation* | Abstract supports training-versus-generation seed variance on FID and several hundred SiT networks. Original bibliography repeats the arXiv identifier twice. Remove one copy. |
| Hardy et al., 2026 | [2605.25272](https://arxiv.org/abs/2605.25272), Michael Hardy, Anka Reuel, Lijin Zhang, Jodi M. Casabianca, Sang Truong, Yash Dave, Hansol Lee, Benjamin Domingue, Sanmi Koyejo, *AI Cartography: Mapping the Latent Landscape of AI Benchmark Ecosystems* | Abstract explicitly uses confirmatory factor analysis and generalizability theory with more than 4,000 released models. Manuscript's broad description matches. |
| Haupt et al., 2026 | [2605.30916](https://arxiv.org/abs/2605.30916), Andreas Haupt, Justin Hartenstein, Anka Reuel, Mykel Kochenderfer, Sanmi Koyejo, *Welfare, Improvability, and Variance: A Principal-Agent Approach to Optimal Benchmark Item Aggregation* | [Full text](https://arxiv.org/html/2605.30916v1) explicitly states its empirical audit does not recover full covariance and uses item-level proxies. Limitations state approximate item independence conditional on model and seed. The manuscript's distinction from a full seed covariance estimate is supported. |
| Kohli, 2026 | [2605.29800](https://arxiv.org/abs/2605.29800), Guneet Kohli, *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels* | Abstract supports roughly two effective votes from nine judges. It specifies Kish effective sample size and a Condorcet null, so do not group its methodology under generalizability theory without further evidence. |
| Messing, 2026 | [2604.11581](https://arxiv.org/abs/2604.11581), Solomon Messing, *Hidden Measurement Error in LLM Pipelines Distorts Annotation, Evaluation, and Benchmarking* | Latest checked version is v6, May 13, 2026. Abstract supports judge, temperature and prompt variability and naive standard errors 40 to 60 percent smaller than its corrected estimates. These are pipeline results, not training-seed covariance results. |
| Zhao et al., 2026 | [2605.20798](https://arxiv.org/abs/2605.20798), Yang Zhao, Jiahao Lu, Bin Huang, Guhua Zhang, Jie Zhou, *Most Transformer Modifications Still Do Not Transfer at 1-3B: A 2020-2026 Update to Narang et al. (2021) with Downstream Evaluation and a Noise Floor* | [Appendix E.4](https://arxiv.org/html/2605.20798v1) explicitly combines twelve per-task Welch tests through Stouffer's method under an independence assumption. Main text reports three-seed macro-average variation. Preserve 1-3B capitalization. The source's separate claim that this Stouffer combination is conservative under positive dependence is not a claim to inherit. |
| van der Wal et al., 2025 | [2503.09543](https://arxiv.org/abs/2503.09543), Oskar van der Wal, Pietro Lesci, Max Muller-Eberstein, Naomi Saphra, Hailey Schoelkopf, Willem Zuidema, Stella Biderman, *PolyPythias: Stability and Outliers across Fifty Language Model Pre-Training Runs* | Record identifies ICLR 2025 publication. Abstract specifies 45 new runs, nine seeds across five sizes, plus five existing runs. Original uses Müller-Eberstein, while arXiv metadata transliterates the name. This alone is not an error. |

## Lynch entry

[Publisher record](https://link.springer.com/article/10.1007/s10519-026-10280-2) confirms Morgan E. Lynch, Molly Gonenne, Colin D. Freilich, Thalida Em Arpawong, Deborah Finkel, Eric Turkheimer, Christopher R. Beam and Deborah W. Davis, *Genetic and Environmental Associations Between Depressive Symptomatology and Loneliness in Adulthood*, Behavior Genetics 56, pages 225 to 235, 2026, DOI 10.1007/s10519-026-10280-2. Publication date is August 25, 2026, issue date September 2026. Publisher page checked did not display issue number 5 in its recommended citation, so omit the issue number unless separately checked.

The publisher's methods describe measurement error within nonshared environmental components. Its discussion explicitly states that the estimated nonshared environmental correlation includes correlated measurement error. Thus it supports the manuscript's caveat. It does not establish that all behavioral-genetics methods cannot address such error. Avoid that universal claim.

## Concrete prose correction

Original related-work sentence merges methods under generalizability theory. Suggested replacement preserves the distinction.

Hardy et al. (2026) apply generalizability theory to released models, while Kohli (2026) measures correlated judge errors with effective sample size. Messing (2026) separates evaluation uncertainty across judge and prompt choices, which concern different sources of variation from training seeds.

## Remaining scope

All metadata matches above are observed. Abstract-level claim matches are identified as such. Full text was inspected for Haupt, Zhao and Lynch. This audit does not justify the manuscript's blanket claim that every citation has been checked, or its claims of manual author verification.
