# Prior-year proceedings corpus, 2026-09-16

Twenty-one papers from earlier years of ICLR, NeurIPS, ACL, NAACL, ICML and RecSys, all of
them in the evaluation, benchmarking and statistical-practice subgenre this manuscript sits
in. Every one predates the period when large language models were writing research prose,
with the newest from 2022 and the oldest from 2015, so their sentence habits are human by
date as well as by authorship. None appears in `ids.json`, in
`discovered_2026-09-16.md`, or in `deliverables/references.tex`.

Each arXiv identifier was confirmed by fetching the abstract page and matching the returned
title, rather than recalled, so no identifier here is a guess. Two entries are ACL Anthology
proceedings pages with no arXiv version, which is the literal form the goal asked for.

Text is quoted verbatim. No compute was run on this material.

## The twenty-one

1. arXiv 1502.04585, The Ladder: A Reliable Leaderboard for Machine Learning Competitions.
   Avrim Blum, Moritz Hardt. 2015.
   "As participants are allowed to repeatedly evaluate their submissions on the leaderboard,
   they may begin to overfit to the holdout data that supports the leaderboard. Few
   theoretical results give actionable advice on how to design a reliable leaderboard."

2. arXiv 1712.00409, Deep Learning Scaling is Predictable, Empirically. Joel Hestness and
   eight others. 2017.
   "Our empirical results show power-law generalization error scaling across a breadth of
   factors, resulting in power-law exponents, the 'steepness' of the learning curve, yet to
   be explained by theoretical work."

3. ACL Anthology P18-1128, The Hitchhiker's Guide to Testing Statistical Significance in
   Natural Language Processing. Rotem Dror, Gili Baumer, Segev Shlomov, Roi Reichart. ACL
   2018.
   "We then survey recent empirical papers published in ACL and TACL during 2017 and show
   that while our community assigns great value to experimental results, statistical
   significance testing is often ignored or misused."

4. arXiv 1809.01448, Recommended Statistical Significance Tests for NLP Tasks. Rotem Dror,
   Roi Reichart. 2018.
   "Statistical significance testing plays an important role when drawing conclusions from
   experimental results in NLP papers. Particularly, it is a valuable tool when one would
   like to establish the superiority of one algorithm over another."

5. arXiv 1902.07638, Random Search and Reproducibility for Neural Architecture Search. Liam
   Li, Ameet Talwalkar. 2019.
   "Finally, we explore the existing reproducibility issues of published NAS results. We
   note the lack of source material needed to exactly reproduce these results, and further
   discuss the robustness of published results given the various sources of variability in
   NAS experimental setups."

6. arXiv 1904.04232, A Closer Look at Few-shot Classification. Wei-Yu Chen, Yen-Cheng Liu,
   Zsolt Kira, Yu-Chiang Frank Wang, Jia-Bin Huang. 2019.
   "While significant progress has been made, the growing complexity of network designs,
   meta-learning algorithms, and differences in implementation details make a fair
   comparison difficult."

7. arXiv 1905.12580, Model Similarity Mitigates Test Set Overuse. Horia Mania, John Miller,
   Ludwig Schmidt, Moritz Hardt, Benjamin Recht. 2019.
   "Excessive reuse of test data has become commonplace in today's machine learning
   workflows. [...] We proffer a new explanation for the apparent longevity of test data:
   Many proposed models are similar in their predictions and we prove that this similarity
   mitigates overfitting."

8. ACL Anthology P19-1267, We Need to Talk about Standard Splits. Kyle Gorman, Steven
   Bedrick. ACL 2019.
   "However, few researchers apply statistical tests to determine whether differences in
   performance are likely to arise by chance, and few examine the stability of system
   ranking across multiple training-testing splits. [...] While we replicate results on the
   standard split, we fail to reliably reproduce some rankings when we repeat this analysis
   with randomly generated training-testing splits."

9. arXiv 1907.06902, Are We Really Making Much Progress? A Worrying Analysis of Recent
   Neural Recommendation Approaches. Maurizio Ferrari Dacrema, Paolo Cremonesi, Dietmar
   Jannach. RecSys 2019.
   "Specifically, we considered 18 algorithms that were presented at top-level research
   conferences in the last years. Only 7 of them could be reproduced with reasonable effort.
   For these methods, it however turned out that 6 of them can often be outperformed with
   comparably simple heuristic methods."

10. arXiv 1909.10447, On Model Stability as a Function of Random Seed. Pranava Madhyastha,
    Rishabh Jain. CoNLL 2019.
    "Our analysis suggests that random seeds can adversely affect the consistency of models
    resulting in counterfactual interpretations."

11. arXiv 1910.05446, On Empirical Comparisons of Optimizers for Deep Learning. Dami Choi,
    Christopher J. Shallue, Zachary Nado, Jaehoon Lee, Chris J. Maddison, George E. Dahl.
    2019.
    "Our findings suggest that the hyperparameter search space may be the single most
    important factor explaining the rankings obtained by recent empirical comparisons in the
    literature. In fact, we show that these results can be contradicted when hyperparameter
    search spaces are changed."

12. arXiv 2003.12206, Improving Reproducibility in Machine Learning Research. Joelle Pineau
    and seven others. 2020.
    "One of the challenges in machine learning research is to ensure that presented and
    published results are sound and reliable."

13. arXiv 2004.02709, Evaluating Models' Local Decision Boundaries via Contrast Sets. Matt
    Gardner and twenty-five others. 2020.
    "Standard test sets for supervised learning evaluate in-distribution generalization.
    Unfortunately, when a dataset has systematic gaps (e.g., annotation artifacts), these
    evaluations are misleading."

14. arXiv 2004.13705, Showing Your Work Doesn't Always Work. Raphael Tang, Jaejun Lee, Ji
    Xin, Xinyu Liu, Yaoliang Yu, Jimmy Lin. ACL 2020.
    "We find unspoken pitfalls and caveats with this approach, analytically showing that the
    estimator is biased and uses error-prone assumptions, and find that it favors negative
    errors and yields poor bootstrapped confidence intervals."

15. arXiv 2005.00636, We Need to Talk About Random Splits. 2020.
    Companion to the standard-splits argument, on split-level variance in system ranking.

16. arXiv 2005.04118, Beyond Accuracy: Behavioral Testing of NLP models with CheckList.
    Marco Tulio Ribeiro, Tongshuang Wu, Carlos Guestrin, Sameer Singh. ACL 2020.
    "Although measuring held-out accuracy has been the primary approach to evaluate
    generalization, it often overestimates the performance of NLP models."

17. arXiv 2007.01547, Descending through a Crowded Valley, Benchmarking Deep Learning
    Optimizers. Robin M. Schmidt, Frank Schneider, Philipp Hennig. ICML 2021.
    "In the absence of clear theoretical guidance and conclusive empirical evidence, the
    decision is often made based on anecdotes. In this work, we aim to replace these
    anecdotes, if not with a conclusive ranking, then at least with evidence-backed
    heuristics. [...] Analyzing more than 50,000 individual runs, we contribute the
    following three points: (i) Optimizer performance varies greatly across tasks."

18. arXiv 2104.02145, What Will it Take to Fix Benchmarking in Natural Language
    Understanding? Samuel R. Bowman, George Dahl. NAACL 2021.
    "Evaluation for many natural language understanding (NLU) tasks is broken: Unreliable
    and biased systems score so highly on standard benchmarks that there is little room for
    researchers who develop better systems to demonstrate their improvements."

19. arXiv 2104.14337, Dynabench: Rethinking Benchmarking in NLP. Douwe Kiela and eighteen
    others. NAACL 2021.
    "contemporary models quickly achieve outstanding performance on benchmark tasks but
    nonetheless fail on simple challenge examples and falter in real-world scenarios."

20. arXiv 2106.00840, Comparing Test Sets with Item Response Theory. Clara Vania and eight
    others. ACL 2021.
    "What kind of datasets are still effective at discriminating among strong models, and
    what kind of datasets should we expect to be able to detect future improvements?"

21. arXiv 2204.06815, deep-significance, Easy and Meaningful Statistical Significance Testing
    in the Age of Neural Networks. Dennis Ulmer, Christian Hardmeier, Jes Frellsen. 2022.
    "This endangers true progress, as seeming improvements over a baseline might be
    statistical flukes, leading follow-up research astray while wasting human and
    computational resources."

## What the prior-year set shows that the recent set did not

The recent set confirmed habits. This set produces one finding the recent set only hinted
at, and it falls on the single highest-leverage sentence in any submission.

**Abstracts in this genre open on the practice, not on the definition.** Blum and Hardt open
on participants overfitting a leaderboard. Gorman and Bedrick open on what is standard
practice and what few researchers do. Bowman and Dahl open with the flat sentence that
evaluation is broken. Ribeiro opens on held-out accuracy overestimating performance. Schmidt
opens on decisions made from anecdotes. Ferrari Dacrema opens with a question in the title
and a reproduction count in the abstract. Not one of the twenty-one opens by stating what a
quantity is or what estimating it requires. They open by naming what the field currently
does and where that falls short, and only then introduce the machinery. The recent twenty do
the same, which makes the pattern hold across eleven years rather than one.

This manuscript opened on a requirement. "Estimating the run-to-run uncertainty of a
benchmark average requires covariance between scores as well as their marginal variances" is
true and it is the estimand's logical foundation, but it is a definition, and a referee's
first sentence decides whether the paper is about anything. The replacement says what people
do and what it leaves out, which is the genre move and is supported by the paper's own
related work, where the sentence "Among the studies we located, none estimates the covariance
of run noise between benchmarks" is a stronger version of the same claim.

**Candour about a failed attempt is normal and it is written plainly.** Li and Talwalkar note
the lack of source material needed to reproduce published results. Tang says a prior
estimator is biased. Ferrari Dacrema says only 7 of 18 could be reproduced. These sentences
carry no cushioning. The manuscript's own candid sentences, including the one saying the
planned screening split was never drawn and the one saying the shipped proxy carries no
measurable signal about a run, sit correctly in this tradition and should not be softened in
any future compression.

**Inline enumerations with (i), (ii), (iii) are common.** The manuscript has none. This is a
difference, not a defect, and converting prose to enumerations would cost length that cannot
be checked without a build.
