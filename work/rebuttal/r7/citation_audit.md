# Round 7 citation audit

Scope: every citation on a line that ae6d8c6 changed (`git diff 73277c2 ae6d8c6 -- deliverables/`), a key-integrity pass over references.tex against main.tex, appendix_a.tex and appendices_bcd.tex, and a render check of main.aux, main.log and main.pdf. Done directly without Codex, as in rounds 1 to 6. Round 6 changed citations only at appendices_bcd.tex:399 (new `\citep{olmo2025olmo3}`) and references.tex (the new bibitem, the teamolmo2025 relabel, the karamcheti2021 title). The other edited lines (main.tex:49, main.tex:56) reworded text around the unchanged citations magnusson2025 and gu2025olmes. Settled items R3-47 and R5-49 (supplement bibliography) and the main.tex:41 attribution choice in r6 CI1 are not raised again.

## Integrity

- references.tex holds 74 bibitems with 74 distinct keys, and a scripted scan of the three body files finds 74 cited keys, with no cited key missing a bibitem and no bibitem left uncited. The count rose from 73 by exactly the one Olmo 3 entry.
- main.pdf (05:44:21) is newer than main.tex (05:44:20), appendices_bcd.tex and references.tex (05:42:23), and main.log has no undefined-citation lines and no rerun warning.
- main.aux resolves the two OLMo keys to distinct labels, `\bibcite{teamolmo2025}{{66}{2025a}{{Team OLMo et~al.}}{{}}}` and `\bibcite{olmo2025olmo3}{{67}{2025b}{{Team Olmo et~al.}}{{}}}`. The PDF renders "(Team OLMo et al., 2025a)" in Appendix B.6 at appendices_bcd.tex:70 and "(Team Olmo et al., 2025b)" in the held-out paragraph at appendices_bcd.tex:399, so the two citations can no longer be confused in the text.
- R6-27 landed, and karamcheti2021 now reads "Mistral: A journey towards reproducible language model training."

## Olmo 3 against the Gen2MC sentence

Citing sentence, appendices_bcd.tex:399: "so the rule replaced them in its listed order with the Gen2MC multiple-choice versions of DROP and CoQA \citep{olmo2025olmo3}, whose distractors an LLM generated, and it reads accuracy only."

Checked against https://arxiv.org/html/2512.13961v2 (fetched 2026-09-23). Section 3.3.4 lists Gen2MC among four new benchmarks, "a multiple-choice version of 5 short-form generative tasks". Appendix A.4.2 says the tasks were built by taking the original question/answer pairs and generating incorrect distractors "using a strong LLM", and names the five tasks as DROP, Jeopardy, NaturalQs, SQuAD and CoQA, with GPT-4o as the generator and GPT-4.1 as a fallback when parsing failed. Tables 2 and 3 report "DROP Gen2MC" and "CoQA Gen2MC". The repository config `compute extra/heldout/config/tasks.json` loads `drop:rc::gen2mc` and `coqa:rc::gen2mc`, so the cited source supplies the items the paper scores. Verdict SUPPORTS. Olmo 3 reports these tasks in its lettered MC format while the paper scores the same items with the rc (cloze) formulation, but the sentence names only the item source and "multiple-choice versions" describes the items correctly under either scoring.

Metadata, checked against https://arxiv.org/abs/2512.13961: title "Olmo 3"; author header "Team Olmo: Allyson Ettinger, Amanda Bertsch, Bailey Kuehl, David Graham, David Heineman, Dirk Groeneveld, ..."; v1 15 December 2025, v2 14 April 2026; arXiv only, no journal reference. The bibitem matches on title, collaboration name, first five authors, arXiv ID and year. Verdict KEEP.

## Findings

| id | severity | location | verbatim quote | what the source says | likely to lower the score | fix |
|---|---|---|---|---|---|---|
| CI1 | Low | references.tex:198-202 (and the same pattern at :27-31) | `\bibitem[Team OLMo et~al.(2025a)]{teamolmo2025}` ... "arXiv:2501.00656, 2025." and `\bibitem[Team Olmo et~al.(2025b)]{olmo2025olmo3}` ... "Olmo 3. arXiv:2512.13961, 2025." | The in-text labels carry the a/b suffixes, but both reference-list entries print the bare year "2025", so a reader holding "2025b" matches it to an entry only by list order or by the OLMo/Olmo casing. Burnell et al. 2023a/2023b at references.tex:27-31 follow the same convention, so this is house style rather than a round 6 regression. Both casings are correct for their papers (OLMo 2 uses "Team OLMo", Olmo 3 uses "Team Olmo"). | no | Optional and length-neutral in the main text: end the four entries with "2025a.", "2025b.", "2023a." and "2023b." in place of the bare years. |

No citation touched in round 6 is fabricated, misattributed or used for a claim its source does not support, and the relabel removed the ambiguity round 6 flagged. The other 71 entries carry their round 1 to 6 KEEP verdicts, and their citing sentences did not change in ae6d8c6.
