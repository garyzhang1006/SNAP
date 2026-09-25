# Style profile of three pre-LLM, heavily cited evaluation-statistics papers (2026-09-24)

## Sources and why they can't be machine written

| Paper | Venue, year | Citations (OpenAlex, 2026-09-24) | Main-text words measured |
|---|---|---|---|
| Demšar, Statistical Comparisons of Classifiers over Multiple Data Sets | JMLR 7, 2006 | 11,210 | 12,360 |
| Koehn, Statistical Significance Tests for Machine Translation Evaluation | EMNLP 2004 | 1,467 | 4,624 |
| Bengio and Grandvalet, No Unbiased Estimator of the Variance of K-Fold Cross-Validation | JMLR 5, 2004 | 623 + 707 (two OpenAlex records) | 6,240 |

All three were published between 2004 and 2006, sixteen years before public LLM writing tools, and none of them was in corpus, corpus2 or corpus3. Dietterich (1998, Neural Computation, 3,803 citations) was the first third pick, but every mirror we tried served a PDF with a broken font encoding, so Bengio and Grandvalet replaced it. Its subject (a covariance matrix of fold errors split into three variance components, with naive estimators that ignore the correlation) is the closest of any candidate to SNAP.

Texts are in this folder (`*_main.txt`, references and acknowledgments cut). Numbers below come from `profile_numbers.txt`, produced with the analyze3.py sentence splitter and measures.

## Measured profile (per thousand words unless marked)

| Feature | Demšar | Koehn | Bengio-G. | SNAP before | Direction for SNAP |
|---|---|---|---|---|---|
| Median sentence length (words) | 24 | 21 | 21 | 24 | hold |
| Sentence-length SD | 15.3 | 16.1 | 14.4 | 14.7 | hold |
| Share over 35 words | 0.225 | 0.114 | 0.161 | 0.268 | lower slightly |
| Share of sentences opening with We or Our | 0.080 | 0.134 | 0.051 | 0.167 | lower |
| "our" | 2.75 | 1.30 | 0.96 | 4.92 | lower |
| Passive constructions | 9.71 | 4.97 | 10.74 | 1.76 | raise |
| Hedges (may, seems, suggests, likely, ...) | 2.83 | 3.03 | 1.76 | 1.05 | raise |
| Signpost markers (note that, in other words, for instance, in particular, that is) | 1.38 | 2.16 | 1.28 | 0.00 | raise |
| "however" | 0.81 | 1.51 | 0.64 | 0.18 | raise |
| "while / although / whereas" | 1.70 | 0.65 | 0.64 | 2.64 | lower |
| "because" | 0.32 | 0.00 | 0.64 | 1.05 | lower, move to "since" |
| "since" | 2.51 | 2.38 | 0.96 | 1.58 | hold or raise |
| "therefore / thus / hence" | 1.94 | 1.30 | 2.40 | 1.41 | hold |
| e.g. / i.e. | 0.08 | 0.87 | 1.76 | 0.00 | add one or two |
| Question marks | 7.36 | 1.08 | 0.32 | 0.00 | add one research question |
| Sentences pointing to a figure, table, section or appendix | 0.08 | 0.11 | 0.08 | 0.23 | deliberate deviation, see below |
| Colons | 3.24 | 9.30 | 8.17 | 0 | house rule keeps 0 |
| Semicolons | 2.27 | 1.51 | 3.21 | 0 | house rule keeps 0 |
| Contractions | 0 | 0 | 0 | 4.22 | house rule keeps contractions |

## Qualitative features

**Voice and stance.** All three write in a plain first-person plural that includes the reader, with the paper itself as a frequent subject ("This paper studies", "This article reviews", "This paper builds upon"). Koehn addresses the reader with "Let us" imperatives ("Let us highlight two properties", "Let us start with the following experiment", "Let us clearly state this assumption") and with direct instructions to look ("First, look at Table 1", "See Figure 8"). Demšar's "we" is often the authors as members of the field ("we probably prefer classifiers that behave well"). Nobody sells. Stance is stated once and flatly ("Our stance is that statistical tests provide certain reassurance").

**Tone.** Measured, with occasional sharp words where the authors disagree with practice. Demšar uses "astounding", "dubious", "naive", "pestered", "ironically", "questionable at best", and irony about common practice ("as if the tests for multiple comparisons ... are yet to be invented"). Bengio and Grandvalet say naive estimators "grossly underestimate" variance. Koehn is conversational ("we resort to a trick", "we often do not have the luxury", "Loosely speaking, the 95% confidence level is actually 97% correct"). None of them is enthusiastic about its own results.

**Candour.** Each paper admits a weakness in the body in plain words with the cause named. Koehn: "That we draw one wrong conclusion, is unfortunate, but should not come as a surprise." Demšar: "In the empirical study we provided no analysis of Type 1/Type 2 error rates. The main reason for this is ...". Koehn also limits scope in the same breath as a finding ("this particular finding is specific to our test scenario").

**Diction.** Plain Latinate statistics vocabulary (commensurability, homogeneity, replicability, overlap, underestimation) beside everyday words (huge, trick, hard, fair, safe). Intensifiers "very", "quite", "rather", "much" appear freely ("very commonly used", "treated with much caution", "rather naive"). Terms of art get named once in a plain sentence ("Let us call this a broad sample", "We call this method paired bootstrap resampling, since we compare a pair of systems") and then used without reminder.

**Sentence openers.** "Formally," before a definition in all three. "Note that", "Recall that", "In other words,", "For instance,", "Of course,", "Unfortunately,", "Fortunately,", "Consequently,", "Moreover,", "Furthermore,", "Surely,", "Ironically,", "Here,", "Again,", "Since", "However,". Each paper leans on two or three of these as its own habit (Koehn on "Let us" and "Recall that", Bengio-Grandvalet on "Note that" and "Consequently", Demšar on "Since" and "However").

**Voice of procedures.** Established facts and procedures are often passive ("It has been shown that", "is taken as evidence", "This was achieved by considering the set of 20,000 examples to be the population", "The details of this experiment are given below"). Choices and findings stay active with "we".

**Questions.** Research questions appear as questions in running text, never answered in the next breath with a flourish. Koehn opens his abstract with one ("If two translation systems differ in performance on a test set, can we trust that this indicates a difference in true system quality?") and later asks "Can we conclude that the better scoring system is truly better?" and "How often can we draw conclusions with 95% statistical significance? How often are we correct?"

**Stress markers.** "We would like to stress that", "We should also stress that", "Let us stress in conclusion at this point that". Each marks a scope limit a reader might miss.

**Paragraphs.** Lengths swing from two sentences to ten. Section openers are one or two sentences stating what the section does ("In this section, we describe the experimental framework of our work", "This section addresses how our main result can be transposed"). Headings are plain noun phrases ("Broad Sampling", "Special Cases", "Selecting a Test Set"), never claims.

**Enumeration.** Problems are counted in prose and then taken in order with ordinal openers ("the t-test suffers from three weaknesses. The first is commensurability ... The second problem ... The third problem ...").

**Numbers.** Written into sentences with their range or instance ("vary from 21% to 37%", "on test set no. 10, 81, and 88", "only roughly half (7.8%) of the 4-gram precision"). Approximation words are "about", "roughly", "of the order of".

**Citation integration.** Authors are grammatical subjects ("Dietterich (1998) ... he focuses", "Nadeau and Bengio (2003) consider", "As Salzberg himself notes"), and the paper places itself against one named predecessor ("This paper builds upon the work of Nadeau and Bengio (2003) ... Our analysis departs from this work in ...").

**Roadmap.** Each introduction ends with a plain roadmap ("This paper is organized as follows. Section 2 defines ...", "In this paper, after providing some background, we will examine ...", "In Section 3 we shall observe ..."), often in the future tense.

**Endings.** Conclusions restate what was done in the past tense ("We applied ... We described ... We provided empirical evidence ...") and close on a forward-looking wish or next step ("we hope that it becomes common practice in published machine translation research to report on the statistical significance of test results", "the next step of this study consists in building and comparing variance estimators dedicated to the very specific structure of the test error dependencies"). Demšar closes by answering the opposing view in a stance paragraph.

**Typography.** Parentheses carry definitions and asides ("(so-called parallel corpora)", "(valid under all distributions)", "(or, put another way, by the covariance between the classifiers)"). e.g. and i.e. sit inside sentences. Footnotes carry side facts. Minor slips survive ("differ differ", "Is has become", "reprensenting"), which a human draft keeps and we don't inject.

## What SNAP takes and what it keeps

SNAP takes the moves that don't collide with the user's standing rules, which are fewer "We/Our" openers, more passive procedure descriptions, more hedges on interpretation, the signpost openers, one research question, a stress marker on scope, one sharp evaluative word ("naive", from Bengio-Grandvalet), a roadmap-free intro (page budget), "since" in place of "because", and a Bengio-style next-step ending.

SNAP keeps its house rules where the references differ, which are contractions, no colons, semicolons or dashes, an eight-word sentence floor, and the macro and label set. Its figure, table and appendix pointer rate stays above the references (0.23 against about 0.1) on purpose, since the pointers carry the claim-to-evidence trace that the ICLR page limit forces into appendices, and the three reference papers had no page limit that pushed evidence out of the body.
