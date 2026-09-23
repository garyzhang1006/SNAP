# Round 6 citation audit

Scope: every `\citep`/`\citet` on a line changed by 73277c2 (`git diff fceef7c 73277c2 -- deliverables/`), which touched citations at main.tex:41 and main.tex:117 only (the edits at main.tex:37 and :43 moved wording around unchanged citations), a context recheck of every citing sentence in main.tex, appendix_a.tex and appendices_bcd.tex, and a key-integrity pass over references.tex. Done directly without Codex, as in rounds 1 to 5. Sources this round: the arXiv abstract page and full PDF of Olmo 3 (arXiv:2512.13961v2), the repository task configs under `compute extra/`, and the r1 to r5 audit records for entries already verified. Items rejected in rounds 3 to 5 (R3-47, R5-49 on the supplement bibliography) are not raised again.

## Integrity

- references.tex holds 73 bibitems with 73 distinct keys. A scripted scan of main.tex, appendix_a.tex and appendices_bcd.tex finds 73 cited keys, with no cited key missing from references.tex and no bibitem left uncited.
- main.pdf (04:58:11) is newer than main.tex (04:58:10), and main.log has no undefined-citation lines.
- Round 5 fixes landed as proposed. main.tex:117 now cites each benchmark after its name, and the PDF renders "ARC-Challenge and ARC-Easy (Clark et al., 2018), BoolQ (Clark et al., 2019)", so the merged "Clark et al., 2018; 2019" label is gone (r5 CI1 / R5-19). main.tex:41 now reads "DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa} in multiple-choice form", which no longer credits the multiple-choice format to the dataset papers (r5 CI2 / R5-38).

## Findings

| id | severity | location | verbatim quote | what the source says | likely to lower the score | proposed fix |
|---|---|---|---|---|---|---|
| CI1 | Moderate | main.tex:41; main.tex:175; appendices_bcd.tex:399 | "and DROP \citep{dua2019drop} and CoQA \citep{reddy2019coqa} in multiple-choice form"; "The battery became SciQ, MedMCQA, and multiple-choice versions of DROP and CoQA"; "the rule replaced them in its listed order with DROP and CoQA as multiple choice" | The paper never says where the multiple-choice versions come from. The task configs (`compute extra/heldout/config/tasks.json:12-13`) load the OLMES aliases `drop:rc::gen2mc` and `coqa:rc::gen2mc`. Olmo 3 (arXiv:2512.13961, Appendix A.4) introduces Gen2MC and says the tasks were built "by taking the original question/answer pairs and generating incorrect multiple-choice distractor answers using a strong LLM", with GPT-4o generating distractors for DROP, Jeopardy, NaturalQs, SQuAD and CoQA. So two of the four held-out tasks have LLM-written distractors from a 2025 AI2 release, and neither fact is stated. | no (an AI2 reviewer will notice the unattributed Gen2MC items, and LLM-written distractors bear on the item noise of the held-out test, but it reads as an attribution gap rather than an error) | Cite Olmo 3 once, at main.tex:175 or appendices_bcd.tex:399, and name the variant, for example appendices_bcd.tex:399: "with the Gen2MC multiple-choice versions of DROP and CoQA \citep{olmo2025olmo3}, whose distractors an LLM generated". Bibitem below. main.tex:41 can stay as it is, since it has no room. |
| CI2 | Low | references.tex, karamcheti2021 | "Mistral: A Journey towards Reproducible Language Model Training." | Every other title in references.tex is in sentence case, and this one is in title case. | no | "Mistral: A journey towards reproducible language model training." |

No citation in the paper is fabricated, points to the wrong paper, or carries metadata that contradicts its canonical record. The remaining 71 entries were verified KEEP in rounds 1 to 5 (r1 fetched every 2026 arXiv ID and matched titles and authors), and their citing sentences are unchanged since then except for the two round-5 fixes above, which are correct.

## Recommended addition

Olmo 3 (source of the Gen2MC DROP and CoQA tasks). VERIFIED against https://arxiv.org/abs/2512.13961: title "Olmo 3", collaboration "Team Olmo" with authors listed alphabetically from Allyson Ettinger, Amanda Bertsch, Bailey Kuehl, David Graham and David Heineman, first submitted 15 December 2025, v2 14 April 2026, no journal reference (arXiv only). The Gen2MC description is in its Appendix A.4.2, and the main text lists Gen2MC among the four new benchmarks in its evaluation suite.

```latex
\bibitem[Team Olmo et~al.(2025b)]{olmo2025olmo3}
Team Olmo, Allyson Ettinger, Amanda Bertsch, Bailey Kuehl, David Graham, David Heineman, et al. Olmo 3. arXiv:2512.13961, 2025.
```

The existing OLMo 2 entry prints as "Team OLMo et al. (2025)", which a reader could not tell apart from this one, so change its label to `\bibitem[Team OLMo et~al.(2025a)]{teamolmo2025}` when adding it. Insert the new item directly after teamolmo2025 so the order stays alphabetical.
