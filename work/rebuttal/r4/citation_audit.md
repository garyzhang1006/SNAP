# Citation audit, round 4

Scope: every `\citep`/`\citet` on a line changed between f23e293 and 2becd1b in `deliverables/` (main.tex:226, 228; appendices_bcd.tex:73, 77; the PolyPythias sentence in the family section, where only non-citation wording moved), a context recheck of the rest of the paper, and the R3-21 bibliography gap. Entries that rounds 1 to 3 verified as KEEP were not re-verified for metadata. Done directly without Codex. Sources: ACL Anthology `.bib` exports, the arXiv API, Crossref, PMLR and IJCAI proceedings pages, the iclr.cc virtual poster page, and arXiv HTML full text of Heineman et al. (2508.13144). DBLP returned a bot challenge and was not used.

## Context checks on edited text

Supported:

- miller2024, main.tex:226 ("with each model treated as fixed"), appendices_bcd.tex:73 and 77 ("covers item-sampling uncertainty with clustered and paired two-model comparisons, treating each evaluated model as fixed"). This is the round-3 CI3 fix, and it matches Miller's framing of the model as a fixed object.
- zhao2026, appendices_bcd.tex:73 ("noting that positive task correlation would make the combination conservative, without estimating that correlation"). This is the round-3 CI2 fix and matches the source's conditional caveat on Stouffer's method.
- jordan2024, main.tex:226 ("nearly independent across shifted ImageNet test sets ... Apart from such shifted test sets, we know of no study that estimates the covariance of run noise between distinct benchmarks"). This is the round-3 CI1 fix, and the main text no longer contradicts its own citation.
- heineman2025, main.tex:228 and 230. Signal and Noise measures per-benchmark seed, data-order, and checkpoint-to-checkpoint noise (Appendix A.3) and correlates these noise sources with each other and SNR with decision accuracy across benchmarks, and it never estimates a covariance of run deviations between benchmarks, so "run covariance across benchmarks at a fixed configuration ... which \citet{heineman2025} don't estimate" holds. One wording issue is logged as CI1.

| ID | Severity | Likely to lower score | Location | Verbatim quote | Problem | Fix |
|---|---|---|---|---|---|---|
| CI1 | Low | no | main.tex:228 | "what we add is the estimand, run covariance across benchmarks at a fixed configuration, and its measurement on released pretraining runs, which \citet{miller2024} and \citet{heineman2025} don't estimate" | The relative clause can attach to "its measurement on released pretraining runs", and Heineman et al. do measure seed noise on pretraining runs they train and release (20 1B runs varying seed and data order, Section 3.1 and Appendix A.3). A reader who takes that reading sees a false claim about a paper by the DataDecide authors, who are likely reviewers. | "what we add is the estimand, run covariance across benchmarks at a fixed configuration, which neither \citet{miller2024} nor \citet{heineman2025} estimates, and its measurement on released pretraining runs." |
| CI2 | Moderate | yes | main.tex:117, 129, 175; main.tex:43; appendices_bcd.tex:399 | "DataDecide supplies the ten benchmarks ARC-Challenge, ARC-Easy, BoolQ, CommonsenseQA, HellaSwag, MMLU, OpenBookQA, PIQA, Social IQa, and WinoGrande." | R3-21 is still open. None of the ten benchmarks, the four held-out tasks, AGIEval with its two named subtasks, or OLMES has a bibliography entry, and a reviewer from the benchmark or OLMo community will read that as careless attribution. | Paste the 17 VERIFIED bibitems below and cite them at first mention: main.tex:117 after each benchmark name (or one `\citep{...}` list at the end of the sentence), main.tex:175 after SciQ, MedMCQA, AGIEval, DROP and CoQA, and main.tex:43 or 129 after the first "OLMES". appendices_bcd.tex:399 can cite liu2020logiqa and wang2022lsat after "LogiQA-en" and "LSAT-LR". |
| CI3 | Low | no | supplement_extended_body.tex:135 | "\citet{henderson2018} and \citet{agarwal2021} address seed sensitivity and uncertainty in reinforcement learning. The authors resample runs within tasks, with an additional task-resampling variant in their Appendix A.5" | Carried over unchanged from round-3 CI4: "The authors" is ambiguous between two cited papers, and the Appendix A.5 pointer remains UNVERIFIED. The file is not `\input` by main.tex, so this matters only if the supplement ships. | "\citet{agarwal2021} resample runs within tasks ..." after checking the appendix number. |

No citation in the edited text is fabricated, points to the wrong paper, or carries wrong metadata, and round-3 CI1 to CI3 are resolved in the current text.

## VERIFIED bibitems for R3-21

Style copied from references.tex (sentence-case titles, "In Proceedings of ..., pp. X--Y, YEAR.", journal volume(issue):pages). Keys are new and do not collide with existing ones. Insert alphabetically. The `\begin{thebibliography}{60}` width argument is ignored by natbib author-year labels, so the count rising from 56 to 73 needs no change there. No new author-year label collides with an existing one, and clark2018arc and clark2019boolq stay distinct because their years differ.

ARC-Easy and ARC-Challenge. VERIFIED, https://arxiv.org/abs/1803.05457 (arXiv only, no archival venue).
```latex
\bibitem[Clark et~al.(2018)]{clark2018arc}
Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord. Think you have solved question answering? Try ARC, the AI2 reasoning challenge. arXiv:1803.05457, 2018.
```

BoolQ. VERIFIED, https://aclanthology.org/N19-1300/
```latex
\bibitem[Clark et~al.(2019)]{clark2019boolq}
Christopher Clark, Kenton Lee, Ming-Wei Chang, Tom Kwiatkowski, Michael Collins, and Kristina Toutanova. BoolQ: Exploring the surprising difficulty of natural yes/no questions. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pp. 2924--2936, 2019.
```

CommonsenseQA. VERIFIED, https://aclanthology.org/N19-1421/
```latex
\bibitem[Talmor et~al.(2019)]{talmor2019commonsenseqa}
Alon Talmor, Jonathan Herzig, Nicholas Lourie, and Jonathan Berant. CommonsenseQA: A question answering challenge targeting commonsense knowledge. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pp. 4149--4158, 2019.
```

HellaSwag. VERIFIED, https://aclanthology.org/P19-1472/
```latex
\bibitem[Zellers et~al.(2019)]{zellers2019hellaswag}
Rowan Zellers, Ari Holtzman, Yonatan Bisk, Ali Farhadi, and Yejin Choi. HellaSwag: Can a machine really finish your sentence? In Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics, pp. 4791--4800, 2019.
```

MMLU. VERIFIED, https://iclr.cc/virtual/2021/poster/2962 and https://arxiv.org/abs/2009.03300
```latex
\bibitem[Hendrycks et~al.(2021)]{hendrycks2021mmlu}
Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. Measuring massive multitask language understanding. In International Conference on Learning Representations, 2021.
```

OpenBookQA. VERIFIED, https://aclanthology.org/D18-1260/
```latex
\bibitem[Mihaylov et~al.(2018)]{mihaylov2018openbookqa}
Todor Mihaylov, Peter Clark, Tushar Khot, and Ashish Sabharwal. Can a suit of armor conduct electricity? A new dataset for open book question answering. In Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, pp. 2381--2391, 2018.
```

PIQA. VERIFIED, https://doi.org/10.1609/aaai.v34i05.6239 (Crossref: AAAI 34(05):7432--7439, 2020)
```latex
\bibitem[Bisk et~al.(2020)]{bisk2020piqa}
Yonatan Bisk, Rowan Zellers, Ronan Le Bras, Jianfeng Gao, and Yejin Choi. PIQA: Reasoning about physical commonsense in natural language. Proceedings of the AAAI Conference on Artificial Intelligence, 34(05):7432--7439, 2020.
```

Social IQa. VERIFIED, https://aclanthology.org/D19-1454/
```latex
\bibitem[Sap et~al.(2019)]{sap2019socialiqa}
Maarten Sap, Hannah Rashkin, Derek Chen, Ronan Le Bras, and Yejin Choi. Social IQa: Commonsense reasoning about social interactions. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), pp. 4463--4473, 2019.
```

WinoGrande. VERIFIED, https://doi.org/10.1609/aaai.v34i05.6399 (Crossref: AAAI 34(05):8732--8740, 2020)
```latex
\bibitem[Sakaguchi et~al.(2020)]{sakaguchi2020winogrande}
Keisuke Sakaguchi, Ronan Le Bras, Chandra Bhagavatula, and Yejin Choi. WinoGrande: An adversarial Winograd schema challenge at scale. Proceedings of the AAAI Conference on Artificial Intelligence, 34(05):8732--8740, 2020.
```

SciQ. VERIFIED, https://aclanthology.org/W17-4413/
```latex
\bibitem[Welbl et~al.(2017)]{welbl2017sciq}
Johannes Welbl, Nelson F. Liu, and Matt Gardner. Crowdsourcing multiple choice science questions. In Proceedings of the 3rd Workshop on Noisy User-generated Text, pp. 94--106, 2017.
```

MedMCQA. VERIFIED, https://proceedings.mlr.press/v174/pal22a.html
```latex
\bibitem[Pal et~al.(2022)]{pal2022medmcqa}
Ankit Pal, Logesh Kumar Umapathi, and Malaikannan Sankarasubbu. MedMCQA: A large-scale multi-subject multi-choice dataset for medical domain question answering. In Conference on Health, Inference, and Learning, volume 174 of Proceedings of Machine Learning Research, pp. 248--260, 2022.
```

DROP. VERIFIED, https://aclanthology.org/N19-1246/
```latex
\bibitem[Dua et~al.(2019)]{dua2019drop}
Dheeru Dua, Yizhong Wang, Pradeep Dasigi, Gabriel Stanovsky, Sameer Singh, and Matt Gardner. DROP: A reading comprehension benchmark requiring discrete reasoning over paragraphs. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pp. 2368--2378, 2019.
```

CoQA. VERIFIED, https://aclanthology.org/Q19-1016/
```latex
\bibitem[Reddy et~al.(2019)]{reddy2019coqa}
Siva Reddy, Danqi Chen, and Christopher D. Manning. CoQA: A conversational question answering challenge. Transactions of the Association for Computational Linguistics, 7:249--266, 2019.
```

AGIEval. VERIFIED, https://aclanthology.org/2024.findings-naacl.149/
```latex
\bibitem[Zhong et~al.(2024)]{zhong2024agieval}
Wanjun Zhong, Ruixiang Cui, Yiduo Guo, Yaobo Liang, Shuai Lu, Yanlin Wang, Amin Saied, Weizhu Chen, and Nan Duan. AGIEval: A human-centric benchmark for evaluating foundation models. In Findings of the Association for Computational Linguistics: NAACL 2024, pp. 2299--2314, 2024.
```

LogiQA (source of the AGIEval task LogiQA-en). VERIFIED, https://www.ijcai.org/proceedings/2020/501
```latex
\bibitem[Liu et~al.(2020)]{liu2020logiqa}
Jian Liu, Leyang Cui, Hanmeng Liu, Dandan Huang, Yile Wang, and Yue Zhang. LogiQA: A challenge dataset for machine reading comprehension with logical reasoning. In Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence, pp. 3622--3628, 2020.
```

LSAT-LR (source of the AGIEval task LSAT-LR). VERIFIED, https://doi.org/10.1109/TASLP.2022.3164218 (Crossref: TASLP 30:2201--2216, 2022; arXiv:2108.00648)
```latex
\bibitem[Wang et~al.(2022)]{wang2022lsat}
Siyuan Wang, Zhongkun Liu, Wanjun Zhong, Ming Zhou, Zhongyu Wei, Zhumin Chen, and Nan Duan. From LSAT: The progress and challenges of complex reasoning. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 30:2201--2216, 2022.
```

OLMES. VERIFIED, https://aclanthology.org/2025.findings-naacl.282/
```latex
\bibitem[Gu et~al.(2025)]{gu2025olmes}
Yuling Gu, Oyvind Tafjord, Bailey Kuehl, Dany Haddad, Jesse Dodge, and Hannaneh Hajishirzi. OLMES: A standard for language model evaluations. In Findings of the Association for Computational Linguistics: NAACL 2025, pp. 5020--5048, 2025.
```

Notes. ARC has no archival venue, and the arXiv preprint is the record the ARC authors and OLMES cite. LogiQA and LSAT-LR are optional, since citing AGIEval covers the task names at main.tex:175, but appendices_bcd.tex:399 names both subtasks. Welbl et al. (SciQ) is a W-NUT workshop paper, which is its only published record.
