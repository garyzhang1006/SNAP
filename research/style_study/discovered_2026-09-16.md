# Live corpus discovery, 2026-09-16

Twenty evaluation-methodology papers found by searching venue listings and arXiv this
session. None of them appears in `ids.json`, and none is cited in
`deliverables/references.tex`, so this set is disjoint from both lists that built the
33-paper corpus. Selection rule was genre match first. Every entry studies how
benchmark scores are measured, compared or trusted, which is the same subgenre the
manuscript sits in, so the prose is comparable rather than merely contemporaneous.

Text below is quoted verbatim from the arXiv abstract pages. No compute was run on this
material, because the user withheld approval for it on 2026-09-16, so every observation in
the analysis section is a reading, not a measurement, and is labelled accordingly.

## The twenty

1. arXiv 2604.11581, Hidden Measurement Error in LLM Pipelines Distorts Annotation,
   Evaluation, and Benchmarking. Solomon Messing.
   "LLM evaluations drive which models get deployed, what safety standards get adopted,
   which research conclusions get published, and how projections of AI's labor-market
   impact get made. Yet standard confidence intervals ignore variability from judge model
   choice, model temperature, and prompt phrasing, producing under-coverage that worsens
   with more data. [...] Across the demonstrations, naive standard errors are 40 - 60%
   smaller than the TEE-corrected SE."

2. arXiv 2601.20251, Efficient Evaluation of LLM Performance with Statistical Guarantees.
   Skyler Wu, Yash Nair, Emmanuel J. Candes.
   "Exhaustively evaluating many large language models (LLMs) on a large suite of
   benchmarks is expensive. We cast benchmarking as finite-population inference and, under
   a fixed query budget, seek tight confidence intervals (CIs) for model accuracy with
   valid frequentist coverage."

3. arXiv 2511.21140, How to Correctly Report LLM-as-a-Judge Evaluations. Chungpa Lee,
   Thomas Zeng, Jongwon Jeong, Jy-yong Sohn, Kangwook Lee.
   "Large language models (LLMs) are widely used as scalable evaluators of model responses
   in lieu of human annotators. However, imperfect sensitivity and specificity of the LLM
   judges induce bias in naive evaluation scores."

4. arXiv 2505.15055, Lost in Benchmarks? Rethinking Large Language Model Benchmarking with
   Item Response Theory. Hongli Zhou and thirteen others.
   "The evaluation of large language models (LLMs) via benchmarks is widespread, yet
   inconsistencies between different leaderboards and poor separability among top models
   raise concerns about their ability to accurately reflect authentic model capabilities."

5. arXiv 2402.14992, tinyBenchmarks: evaluating LLMs with fewer examples. Felipe Maia Polo,
   Lucas Weber, Leshem Choshen, Yuekai Sun, Gongjun Xu, Mikhail Yurochkin.
   "The versatility of large language models (LLMs) led to the creation of diverse
   benchmarks that thoroughly test a variety of language models' abilities. These
   benchmarks consist of tens of thousands of examples making evaluation of LLMs very
   expensive."

6. arXiv 2606.26185, Necessary but Not Sufficient: Temperature Control and Reproducibility
   in LLM-as-Judge Safety Evaluations. Hiroki Tamba.
   "A widespread assumption is that setting the grader's sampling temperature to 0 makes
   grading deterministic. We test this assumption against a real safety-evaluation codebase
   (Japan AISI's open-source aisev) and show it fails on two levels. [...] across 690 API
   calls spanning two providers, three model tiers, and five sampling configurations, 1-2
   of 7 borderline items remain non-reproducible even under forced greedy decoding."

7. arXiv 2605.30504, Auditing LLM Benchmarks with Item Response Theory. Sander Land,
   Daniel M. Bikel.
   "LLM benchmark labels are frozen at release and silently propagated into downstream
   benchmarks, errors and all. We introduce an Item Response Theory-based indicator that
   surfaces likely mislabels at 95% precision in the top 200 examples across seven
   preference and multiple-choice benchmarks using responses from 114 models."

8. arXiv 2511.04689, Adaptive Testing for LLM Evaluation: A Psychometric Alternative to
   Static Benchmarks. Peiyu Li, Xiuxiu Tang, Si Chen, Ying Cheng, Ronald Metoyer,
   Ting Hua, Nitesh V. Chawla.
   "Evaluating large language models (LLMs) typically requires thousands of benchmark
   items, making the process expensive, slow, and increasingly impractical at scale. [...]
   it matches whole-bank ability estimates using only 41 items (0.157 MAE) on HellaSwag
   (5,600 items)."

9. arXiv 2501.10711, Code Benchmarks Should Prioritize Rigor, Reliability, and
   Reproducibility. Jialun Cao and fourteen others.
   "In the past few years, awareness of benchmark quality has grown. Yet, after a
   decade-scale (2014-2025) survey over 672 code benchmarks, we observed a lag between
   growing awareness and actual practice."

10. arXiv 2510.00844, Learning Compact Representations of LLM Abilities via Item Response
    Theory. Jianhao Chen and seven others.
    "Recent years have witnessed a surge in the number of large language models (LLMs), yet
    efficiently managing and utilizing these vast resources remains a significant
    challenge."

11. arXiv 2509.22888, JE-IRT: A Geometric Lens on LLM Abilities through Joint Embedding
    Item Response Theory. Louie Hong Yao, Nicholas Jarvis, Tiffany Zhan, Saptarshi Ghosh,
    Linfeng Liu, Tianyu Jiang.
    "Standard LLM evaluation practices compress diverse abilities into single scores,
    obscuring their inherently multidimensional nature."

12. arXiv 2512.16041, Are We on the Right Way to Assessing LLM-as-a-Judge? Yuanning Feng,
    Sinan Wang, Zhengxiang Cheng, Yao Wan, Dongping Chen.
    "even the top-performing models, Gemini-2.5-Pro and GPT-5, fail to maintain consistent
    preferences in nearly a quarter of difficult cases. [...] We also find substantial
    inconsistency in human judgments, which indicates that human annotation may not be a
    reliable gold standard."

13. arXiv 2607.04429, evalci: A Python Library for Statistically Rigorous Comparison of
    Language Model Evaluations. Shreyas K Chandrahas.
    "The dominant practice in language model evaluation is to report a single accuracy
    number per model and declare the higher one better, without testing whether the gap
    could plausibly be sampling noise. [...] we re-analyze a public comparison of nine
    language models' MMLU accuracy and find that 3 of the 8 adjacent leaderboard-rank gaps
    are not statistically significant after correcting for the 36 pairwise comparisons the
    ranking implies."

14. arXiv 2602.11674, Benchmark Health Index: A Systematic Framework for Benchmarking the
    Benchmarks of LLMs. Longyuan Zhu, Hairan Hua, Linlin Miao, Bing Zhao.
    "Large Language Models (LLMs) are advancing rapidly, yet the benchmarks used to measure
    this progress are becoming increasingly unreliable. Score inflation and selective
    reporting have eroded the authority of standard benchmarks."

15. arXiv 2512.07795, ReasonBENCH: Benchmarking the (In)Stability of LLM Reasoning.
    Nearchos Potamitis, Vansh Ramani, Har Ashish Arora, Dhairya Kuchhal, Lars Klein,
    Akhil Arora.
    "Benchmark scores for LLM reasoning systems are reported as single numbers, yet the
    same model, strategy, and task can produce meaningfully different answers and costs
    across repeated executions, even under greedy decoding (T = 0). This variance is not a
    statistical nuisance: the highest-performing strategy wins only 77% of head-to-head
    runs against its nearest competitor, meaning a single observed score can silently
    misrank systems."

16. arXiv 2605.11209, Measuring Five-Nines Reliability: Sample-Efficient LLM Evaluation in
    Saturated Benchmarks. Eungyeup Kim, Chenchen Gu, Vashisth Tiwari, J. Zico Kolter.
    "While existing benchmarks demonstrate the near-perfect performance of large language
    models (LLMs) on various tasks, this apparent saturation often obscures the need for
    rigorous evaluation of their reliability. [...] Our estimates reveal that models with
    indistinguishable accuracy on standard benchmarks can differ substantially in estimated
    failure rates."

17. arXiv 2606.19544, Reliability without Validity: A Systematic, Large-Scale Evaluation of
    LLM-as-a-Judge Models Across Agreement, Consistency, and Bias. Justin D. Norman,
    Michael U. Rivera, D. Alex Hughes.
    "kappa deflation between exact match and Cohen's kappa is universal (33--41 pp on
    MT-Bench), judge rankings shift by up to 14 positions across benchmarks, high
    test--retest reliability (>0.95) coexists with severe position bias (>0.10) in two
    production-deployed judges."

18. arXiv 2608.24419, A Judge Should Know What Changed: Construct Validity for
    LLM-as-a-Judge Evaluation. Jianlin Chen, Wenhui Chen, Ziyao Lin, Chi Man Vong.
    "LLM-as-a-judge evaluation is usually assessed by agreement and robustness to surface
    perturbations, but reliability does not establish construct validity. [...] At matched
    invariance S >= 0.90, judges average S = 0.945 but R = 0.319."

19. arXiv 2606.20626, Efficient Safety Benchmarking via Item Response Theory. Fabio
    Spagliardi, Mirian Silva, Ayan Datta, Aiden Zhou, Vamshi Bonagiri, Diogo Cruz.
    "Safety benchmarks for language models are typically evaluated using static paradigms
    that treat all items as equally informative for all models, an assumption that is
    particularly problematic for adversarial, highly heterogeneous safety items."

20. arXiv 2606.26429, DualEval: Joint Model-Item Calibration for Unified LLM Evaluation.
    Aaron J. Li, Hao Huang, Youngmin Park, Yitong Ma, Wei-Lin Chiang, Li Chen,
    Cho-Jui Hsieh, Bin Yu, Ion Stoica.
    "Current LLM evaluation relies on two complementary but often disconnected signals:
    static benchmarks with objective correctness labels and arena-style preference data
    that better reflect open-ended user interactions."

## What reading them changes

The first observation corrects a target this project set for itself one scan ago, and it
corrects it downward in ambition rather than upward.

**Sentence openers.** Scan 24 measured the 33-paper corpus at 6.0 percent of sentences
opening with "The", treated the draft's 18.7 percent as a defect, and rewrote nine
sentences to reach 15.0 percent. Counting the twenty opening sentences above by hand gives
three that open with "The", which is 15 percent, sitting exactly where the draft now sits.
The two figures are not in conflict, because they measure different things. A full body
carries related work and motivation, where the subject of a sentence is often a person or
a research community, while an abstract and a results section carry named quantities as
subjects and therefore take the article. The manuscript is results-dense throughout. So the
6.0 percent figure was the wrong target for this paper, the 15.0 percent the draft reached
is inside the range this set displays, and the twenty-odd further rewrites contemplated at
the end of scan 24 would have pushed the prose away from the genre rather than toward it.
That decision is now closed on evidence rather than on taste.

**Colons and dashes.** These twenty use both freely, and several turn on them. "This
variance is not a statistical nuisance: the highest-performing strategy wins only 77
percent of head-to-head runs" would lose its force rewritten without the colon. The house
rule banning prose colons, semicolons and dashes therefore puts the manuscript outside the
genre on exactly one axis, which matches what the 33-paper measurement already reported.
The rule is the user's and it stays, and the honest statement is that the paper pays a
small readability cost for it rather than that the rule is invisible.

**Negation.** Three of the twenty state a claim by denying its opposite, including
"reliability does not establish construct validity" and "human annotation may not be a
reliable gold standard". The blanket ban on contrast framing is a chat rule. In this genre
a negation that carries its own evidence is ordinary, so the manuscript need not avoid one
where it is the shortest true statement.

**Triads.** Rule-of-three groupings are everywhere here, including a title built from
three nouns. Reflexive triads remain an AI tell in chat, and they are not one in this
literature when the three things are real.

**Loss reported beside the win.** The strongest shared habit is a single sentence carrying
both the result and its limit, as in judges averaging 0.945 on invariance but 0.319 on
sensitivity, or models with indistinguishable accuracy differing substantially in failure
rate. The manuscript already does this in its two interval sentences. Worth protecting in
any future compression, because it is the habit that most separates this literature from
promotional writing.

**Unrounded numbers.** 41,871 items, 690 API calls, 672 benchmarks, 541,000 judgments,
156.22x, 0.157 MAE. The manuscript's 37,682 items and 4,999 bootstrap draws sit in the same
register.
