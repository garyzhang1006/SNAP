# Exemplar profile, twelve evaluation-methodology papers, 2018-2021

Sources: the twelve per-paper profiles, checked against `/Users/garyzhang/Documents/ChatGPT/iclr main track/research/style_study/corpus3/*.txt`. SNAP text read from `\begin{abstract}` to `\label{maintext:end}` in `/Users/garyzhang/Documents/ChatGPT/iclr main track/deliverables/main.tex`, about 5,900 words, 144 sentences, 321 decimal numbers in running prose and tables, 64 occurrences of "we".

## Collective register

1. **Claim before number, always in that order (12 of 12).** The plain-language verdict is stated first, and the figure arrives later in the same sentence, in the next sentence, in parentheses, or not at all. Recht: "All models see a large drop in accuracy," then the next sentence gives 8% and 11%.

2. **"We" is the default subject and carries four distinct jobs (12 of 12).** Action, finding, opinion, and deliberate scope limit, all under the same pronoun, at 76 to 106 occurrences per paper in eleven of the twelve, with Melis the outlier at 41. Mosbach: "We decided to not show results for BERTBASE."

3. **A first-person finding verb is available in every paper and does real announcing work in about half of them (12 of 12 for presence).** The recurring frames are "we find", "we observe", "we see", "we show", and "we conclude", at rates from one instance in Melis to twenty-six in Mosbach, so the reader usually knows whether a sentence reports or interprets. Zhang: "we observe that transferring the top pre-trained layers slows down learning."

4. **One hedge per hedged claim, with three stacked hedges in the whole corpus (12 of 12).** The vocabulary is small, mostly "likely", "may", "could", "suggests", "possibly", and measured facts carry no hedge at all. Melis: "This is most likely due to optimisation being limited to 14 epochs."

5. **Where a null or negative result is reported, it is stated flatly with a plain negative verb (8 of 12, the other four report no null in the main text).** No apology, no cushioning clause, and the disappointing direction is named. Zhang: "We observe no noticeable improvement using pre-trained weight decay."

6. **Paragraphs close on a consequence or a qualification rather than trailing off (verified in four papers from the sentences before each heading).** The four-to-eight-sentence length claim is unverified, because the corpus3 extraction collapsed paragraph breaks. Bouthillier 2021: "It must be accounted for when benchmarking pipelines."

7. **Long clause-joined sentences alternate with an occasional short verdict (12 of 12), and runs of three short sentences are uncommon rather than absent (8 of 12).** Medians sit at 20 to 29 words with about half of all sentences in the 20-to-40 band, and the verdict lands at eight to fourteen. Card: "Routinely running experiments with low statistical power undermines the scientific enterprise."

8. **Concreteness comes from named artifacts and exact inline settings (12 of 12).** Systems, datasets, library versions, and seed counts are named in running prose, and number density varies from 3.9 decimals per thousand words in Chan to 40.1 in Zhang, so low density is not part of the habit. Henderson: "(64, 64, ReLU) for both actor and critic."

9. **Figures and tables are usually the grammatical subject of an active verb, or a short trailing pointer (9 of 12).** "Figure N shows", "Table N summarizes", or a bare parenthetical after the claim, with the long "as can be seen in" construction rare rather than absent (once each in Card and Henderson). Zhang: "Figure 5 shows the effect of the choice of L."

10. **The conclusion neither recaps numbers nor opens with a summarising formula (12 of 12).** No instance of "In conclusion" or "To sum up" anywhere in the twelve, and results figures are not repeated. Melis: "this paper does not offer a practical methodological solution."

11. **Parentheses carry citations, glosses, exact settings, and pointers, and nothing rhetorical (12 of 12).** The argument itself never depends on what is inside a bracket. Chan: "Dispersion across Time (DT)."

12. **Limitations sit next to the claim they qualify rather than being gathered into a terminal section (11 of 12).** Bouthillier 2019 is the single exception, with its numbered limitations section, and it also concedes inline. Recht: "we remark that they do not exclude all variants."

13. **Sections open with a claim, a fact, or a scope statement rather than an itinerary (10 of 12).** Chen and Bouthillier 2021 are the exceptions, and both keep the itinerary to a single sentence. Melis: "The scientific process by which the deep learning research community operates is guided by empirical studies."

14. **A bold or italic run-in label is the organising unit below the section heading (10 of 12).** The label states the topic so the first sentence can start straight into mechanism. Recht: "Gathering Data." and "Cleaning Data."

15. **Forward pointers are short and specific where they appear, at roughly one per page in the median paper and up to three in Card (10 of 12).** They name a section number or an appendix and stop, Henderson uses none and Melis uses one. Card: "please refer to Appendix B."

16. **Opinion about the field is stated in the authors' own voice without a shield (11 of 12).** The shielded "we believe" appears in five of the twelve, most often in Chen, and never replaces the flat assertion entirely. Zhang: "the common one-size-fits-all three-epochs practice for BERT fine-tuning is sub-optimal."

17. **The connective inventory is small and adversative, with "However" the most common marker and the flashy stance adverbs largely absent (11 of 12).** A Python count gives "However" between 2 and 9 per paper and the most common adversative in ten of twelve, while "Importantly" reaches one occurrence in four papers and "Interestingly" one in a few. Agarwal: "However," six times against one "Moreover."

18. **The formal register is broken on purpose, usually once or twice but up to fifteen times in Chan and ten in Recht, by a colloquialism, a scare-quoted term of art, or an evaluative adverb (9 of 12).** Chan: "to ensure apples-to-apples comparison."

## Where SNAP departs

1. **Claim before number.** Departs inside the results sections, and this is the single largest gap. The abstract and the Introduction open on claims, but the results prose is number-first, as in Section 4.1's opener, "Table~\ref{tab:primary} reports full-battery inflation of 1.244 on margins," and the abstract's "the standard deviation of the battery average is 1.244 times what independence predicts." Edit: reorder so a verdict sentence leads and the frozen number follows in the next clause or the next sentence.

2. **"We" doing four jobs.** Partly follows. SNAP uses "we" for action and for scope limits and has 64 occurrences against the exemplars' 76 to 106, but almost never for a finding or an opinion. Edit: add first-person finding and stance sentences, without changing any evidence label.

3. **A finding verb announces every result.** Departs completely. Grep over the main text returns zero "we find", zero "we observe", zero "we see", and one "we show." Results are announced by inanimate subjects instead, as in Section 4.1's "Recipe removal moves margin inflation between 1.207 and 1.256." Edit: add a claim sentence with a first-person finding verb ahead of each results block.

4. **One hedge, never stacked.** Follows. SNAP hedges once per claim and marks uncertainty through frozen evidence labels rather than through modal stacking, as in the Introduction's "we read the full-battery accuracy estimate as a bound."

5. **Flat null results.** Follows, and this is SNAP's strongest match. Section 4.2's "so the registered test fails" and Section 3's "the plan's screening split was never formed" are unsoftened.

6. **Paragraph shape.** Departs in five places. The contributions paragraph in the Introduction runs 243 words as one undivided block, the checkpoint paragraph in Section 3 runs 314, the BoolQ paragraph in Section 4.1 runs 275, the calibration paragraph in Section 2.3 runs 245, and the registered-test paragraph in Section 4.2 runs 228. Each carries six to twelve separate findings with no topic sentence, and three of the five end without a consequence sentence. Edit: split each into two or three paragraphs, and give every resulting paragraph an opening claim and a closing consequence sentence.

7. **Rhythm.** Partly departs. Of 194 sentences, 71 carry no digit and the shortest are verdicts ("Covariance adds the off-diagonal terms to that variance"), but the results paragraphs run number-laden sentence after sentence with a median of 25 words and 0.275 of sentences over 35, so the long-long-short alternation rarely resolves there. Edit: end each results paragraph with a verdict sentence of twelve to sixteen words carrying no new figure.

8. **Concreteness.** Follows on naming and overshoots on density. Benchmarks, sizes, seed labels, and torch versions are all named, but 321 decimal values sit in roughly 5,900 words, about one every eighteen words, against exemplars that keep result values in tables. Edit: move second and third numbers of a sentence into the following sentence or into the existing tables, since none may be cut.

9. **Figure and table pointers.** Departs by scarcity. The main text names "Figure~" twice and "Table~" eight times against 28 appendix pointers, four pointers already sit as trailing parentheticals and "Figure~\ref{fig:composition} shows" is the exemplar form, but the results opener leads with the table, as in "Table~\ref{tab:primary} reports full-battery inflation of 1.244." Edit: reorder to claim-first with the table as a trailing pointer, and add a pointer sentence at the head of each results subsection.

10. **Conclusion without a recap of numbers.** Departs. Section 6 opens on the accuracy result and immediately restates 1.10, 0.135, 1.157, and 1.558 with its interval, so the discussion re-runs the results table. Edit: cut the repeated figures back to the claims they support, keeping every number that appears only there.

11. **Parentheses.** Follows. SNAP's parentheses carry appendix, table and section pointers, equation references and inline notation, and no citation, since citations run through \citet in the sentence body.

12. **Inline limitations.** Follows in the body and departs at the section level. The caveats are attached to their claims, as in Section 3's "this retrospective calculation can't restore a holdout," but Section 6 is titled "Discussion and limitations" and gathers a second round of them. Edit: keep the section, and cut from it whatever is already conceded at the point of claim.

13. **Section openers.** Follows. The Introduction opens on "A benchmark average can change across training runs," Section 3 on "DataDecide supplies the ten benchmarks," and neither is an itinerary.

14. **Run-in labels below the heading.** Departs. SNAP has none, and the long undivided paragraphs named in habit 6 are exactly where the exemplars would place one. Edit: add a run-in label to open each split paragraph, ending it with a period rather than a colon.

15. **Short forward pointers.** Partly follows. The 28 appendix pointers match the exemplar habit, but there are only two section cross-references and no "we now turn to" transitions, so the reader gets no map inside the results. Edit: add a signpost sentence at the head of Section 4 and of Section 4.3.

16. **Unshielded opinion about the field.** Departs. SNAP states recommendations twice, in the abstract and in Section 6, and states no judgement about current practice anywhere, even though the Introduction's simulated 0.113 against a nominal 0.05 invites one. Edit: add one claim sentence in the Introduction saying what the independence assumption costs in practice.

17. **Small adversative connective inventory.** Departs. Grep returns zero "However", zero "Note that", zero "For example", and zero "First,", so contrast is carried by "while" (11), "so" (15), "although" (6), "but" (8) and "whereas" (2), which puts most reversals into a subordinate clause. Edit: promote the load-bearing reversals to sentence-initial "However" and give the contributions paragraph an explicit ordinal chain.

18. **A deliberate break in register.** Met by the contractions the house rules require, and the main text has no scare-quoted term and only two evaluative adverbs ("severely truncated", "almost entirely"). No edit.

Furthest from the register, in order: the contributions paragraph in the Introduction, the checkpoint paragraph in Section 3, the BoolQ paragraph in Section 4.1, the calibration paragraph in Section 2.3, and the registered-test paragraph in Section 4.2. All five are single blocks over 220 words that lead with numbers, carry no finding verb, and end without a consequence sentence.

## Constraints the rewrite keeps

The rewrite keeps every contraction on a verb-plus-not form, admits no colon, semicolon, or dash in prose, holds every sentence at eight words or more, and freezes every number and every evidence label, meaning registered, exploratory, post hoc, added later, and fixed before. Four exemplar habits collide with those rules, and the constraints win each time.

The colon ban kills the exemplars' commonest signposting device, Mosbach's "we perform the following experiment:" and Bouthillier 2019's "Methods Reproducibility:" definition blocks. Habit 15 survives as a full sentence and habit 14 survives with the run-in label ending in a period, which is how Recht and Mosbach write theirs anyway.

The eight-word floor kills the shortest verdicts that give the exemplars their rhythm, Bouthillier 2019's "Hence our irreverent title.", Card's "But how many?", and Bouthillier 2021's "Bad news first:". Habit 7 therefore has to be realised at twelve to sixteen words, which is long for a verdict but still well short of SNAP's current thirty-plus.

The contraction rule runs against the register rather than with it, since Henderson has no contractions at all and Card has four in a whole paper, so SNAP will read more informally than any exemplar. Habit 18 is already satisfied by the contractions, and no further colloquialism is needed to meet it.

The frozen numbers forbid the obvious fix for habit 1 and habit 8, which in the exemplars is to delete a figure and keep the claim. Every reordering has to move a number into a later sentence or into an existing table rather than cut it, and the frozen evidence labels likewise forbid the exemplars' habit of asserting a result flatly once it has been measured.

## Refutation record

Two Opus 5 refuters checked the odd and even habits against the twelve source files and the SNAP text on 2026-09-21. No habit was refuted outright, thirteen were adjusted in count or wording as now shown above, and five were confirmed as written (1, 10, 11, 13, 14). In part 2 the refuters corrected the section numbering (the discussion is Section 6, not 5), the rhythm line (71 of 194 SNAP sentences carry no digit), the "throughout" and "entirely" overstatements, the parentheses description, the item-18 contradiction with part 3, and two of the five long paragraphs that do end on a consequence. The four-to-eight-sentence paragraph claim stays unverified because the PDF extraction collapsed paragraph breaks.
