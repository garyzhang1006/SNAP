# SNAP manuscript scan log

Durable state for the 20-parent-scan review the user requested on 2026-09-16 at 19:45 EDT.
Rules carried through every scan. No agents. No workflows. No compute without asking first.
Every parent scan re-reads what the previous scan changed before it starts its own sub-scans.
Grades are honest and never inflated, and a scan that finds nothing says so.

## Ranking method

After each parent scan I record an honest ICLR-scale estimate. The scale is the ICLR reviewer
scale of 1 to 10, plus a rough acceptance probability. I hold the same rubric across scans so the
numbers are comparable, and I only move a number when a specific change justifies it.

Baseline before scan 1, carried from the independent reviewer pass earlier in this project.

| dimension | reading |
|---|---|
| soundness | strong, since every number traces to a stored result and the limitations are stated without hedging |
| novelty | moderate, since the estimator is an established split-half construction applied to a new unit |
| significance | moderate to strong for evaluation practice |
| clarity | the weakest axis, because the prose is dense and the appendix runs very long |
| honest overall estimate | 6.0, acceptance probability near 0.55 |

## Scan index

| scan | focus | defects found | defects fixed | rank after |
|---|---|---|---|---|
| 1 | mechanical correctness, all three tex files | 7 | 7 | 6.0 |
| 2 | hostile claim audit, adversarial-reviewer | 4 | 4 | 6.1 |
| 3 | framing, positioning and first-page impression | 3 | 3 | 6.1 |
| 4 | numerical consistency and result coverage | 3 | 3 | 6.2 |
| 5 | figures, tables and float hygiene | 3 | 3 | 6.2 |
| 6 | method completeness and reproducibility | 4 | 4 | 6.3 |
| 7 | corpus style study and rhythm calibration | 3 | 3 | 6.3 |
| 8 | split verification and grammar after automation | 6 | 6 | 6.3 |


## Scan 1, mechanical correctness, 20 sub-scans

Sub-scans run. Compile warnings, punctuation, grammar agreement, banned punctuation, sentence floor,
number consistency between abstract and body, interval formatting, citation resolution, cross-reference
resolution, caption completeness, anonymity, page compliance, equation labelling, terminology drift,
tense, spelling variants, acronym first use, URL validity, duplicated sentences, and decimal style.

Defects found and fixed.

1. `main.tex` carried a comma splice, `than those without it, Sweeping 2,000 weightings`, now a full stop.
2. `fig:prediction` had a caption and no reference anywhere, which I introduced earlier today when I
   added the figure. The paired-uncertainty paragraph now points at it.
3. Four appendix tables, `tab:original5`, `tab:original12`, `tab:original14` and `tab:original15`, had
   labels that nothing referenced. Each now has a pointer in the paragraph that introduces it.
4. The two accuracy power figures, 0.111 from the compound-symmetric design run and 0.103 from the
   measured-matrix run, sat in different sections with nothing tying them. The appendix now states that
   they differ by 1.6 Monte Carlo standard errors.

One defect I created and caught inside the same scan. My first pointer for `tab:original5` landed inside
that table's own caption, producing a self-reference, and I reverted it before the build.

Non-defects recorded rather than edited.

- Mixed `\%` and the word percent. The paper-humanizer evidence base treats typographic inconsistency as
  a human trait and tells me not to normalise it, so I left it.
- Four equation labels that nothing references. A displayed equation discussed in the sentence beneath it
  needs no cross-reference, and adding four would cost main-text lines on a page-tight build.
- `centre` against `center` and one doubled-word hit were both false positives, from `\centering` and from
  the phrase `beats the plug-in in 0.81 of margin splits`.

Build after scan 1. Nine main-text pages, clean sentence gate, no overfull box anywhere in the log, no
unresolved citation, no unresolved reference, no unreferenced label outside the equation set.

Honest ranking after scan 1. Unchanged at 6.0 with acceptance near 0.55. Mechanical fixes remove one
reviewer complaint that a figure was never discussed, and none of them changes what the paper argues.

## Scan 2, hostile claim audit under the adversarial-reviewer skill, 20 sub-scans

Scan 2 first re-read every scan 1 change in the built PDF, and all seven held.

Sub-scans run. Traceability of every quantitative claim, verb strength, hedge adequacy on causal claims,
abstract against body, introduction against body, novelty defensibility, generalisation scope, fidelity
of claims about cited work, provenance claims, simulation attribution, unstated assumptions, selective
reporting, reviewer-bait sentences, internal contradictions, undefined terms, appendix contradictions,
symmetry between power and limitation, limitations in the abstract, support for the recommendation, and
the accuracy of the AI and ethics statements.

Defects found and fixed.

1. `At accuracy $p=0.35$` carried no justification anywhere in the paper, and no stored result gives the
   battery's mean accuracy, so the value is now labelled illustrative rather than empirical. Measuring
   the real mean would need a run over the reductions, which is compute I did not have permission for.
2. The abstract advertised simulated coverage of 0.933 to 0.953 while the discussion reports 0.821 under
   the band-sharing violation that the paper itself calls its main clustering risk. The abstract now
   carries that number, with the quarter-of-latent-variance condition attached.
3. One abstract sentence ran 55 words and repeated `paired intervals` twice. It is now two sentences of
   28 and 20 words that keep both findings.
4. Two further abstract sentences at 40 and 37 words are now 35 and 34.

One defect I created and caught inside the same scan. My first version of the coverage caveat said
coverage falls to 0.821 whenever a run effect follows the size band, which overstates it, since 0.821 is
the value at a quarter of latent variance. The condition is now in the sentence.

Non-defects recorded rather than edited.

- Verb strength came back clean. Every occurrence of prove, establish and confirm in the body sits in a
  negative construction or describes the construction as established, so the paper does not oversell.
- Seven numbers appear without an attached interval. Each is either a diagnostic the text labels as one
  or a value whose interval sits in the table beside it.

Honest ranking after scan 2. 6.1 with acceptance near 0.57. The abstract caveat is the first change today
that a reviewer would actually weigh, because it moves the paper's main clustering risk from the back of
the discussion into the first thing a reviewer reads, and papers that state their own worst number early
read as more careful rather than less.

## Scan 3, framing and positioning, 20 sub-scans

Scan 3 re-read every scan 2 change in the built PDF first. The illustrative accuracy label, the abstract
coverage caveat with its quarter-of-latent-variance condition, and the four shortened abstract sentences
all held, and the sentence gate stayed clean.

Sub-scans run. Introduction paragraph order, contribution-statement placement, contribution verbs,
novelty language, positioning against the closest prior work, related-work coverage, section length
balance, paragraph length distribution, section openers, forward pointers, abstract length, abstract
sentence load, first-page impression, ordering of caveats against findings, roadmap adequacy, agency of
sentence subjects, recap detection, redundancy between related work and discussion, internal consistency
between main text and appendix on the provenance census, and overclaiming vocabulary.

Defects found and fixed.

1. The provenance census contradicted itself across files. The stored result classifies the 125 model
   repositories as 80 refusing an unauthenticated request, 40 resolving anonymously, and five carrying a
   name the Hub rejects as malformed. The appendix called all 85 non-resolving repositories HTTP 401,
   which the census does not support, and the main text gave 80 and 40 while leaving five unexplained to
   anyone who subtracts. Both sentences now carry all three categories.
2. The limitations paragraph ran 329 words over eleven sentences, the longest block in the paper. It is
   now two paragraphs, splitting the data and measurement caveats from the clustering caveats.
3. The discussion opened by restating what the estimator does, which Section 2 already establishes. That
   recap is gone and the section now opens on the finding.

One change I made and then reverted inside the same scan. I reordered the introduction so the contribution
paragraph came before the two caveat paragraphs, and the build held at nine pages. I reverted it because
contributions-last is the convention I can actually name, and I have no evidence yet that this population
of venues does otherwise. The twenty-paper style study this goal requires is the right evidence base for
that decision, so the ordering question is deferred to it rather than settled by preference.

Page budget. The paragraph split and the census clause cost two lines, which I paid for with seven
compressions rather than by dropping content. The abstract lost its BoolQ passage-split sentence, which
is a robustness detail the body and appendix both still carry, taking it from 307 words to 280. Related
work lost a calibration clause that duplicated the discussion, and four wordy passages in results and
related work were tightened. Main text is nine pages, body 4,902 words.

Non-defects recorded rather than edited.

- Related work runs 214 words, which is short for this venue. It names the gap in one explicit sentence
  and positions against the four closest papers, and expanding it would cost main-text lines that the
  results need more. Recorded as a known weakness rather than fixed.
- The Results section has no lead-in text before its first subsection. Adding one would cost a line and
  the subsection titles already carry the itinerary.
- No overclaiming vocabulary anywhere in the body. The single occurrence of `first` is ordinal, in
  `the first scale`, and nothing in the paper calls itself novel, comprehensive or state of the art.

Honest ranking after scan 3. Unchanged at 6.1 with acceptance near 0.57. The census fix removes a real
internal contradiction, but it sits in a limitation sentence that most reviewers will not check against
the appendix, so it protects against a downside rather than adding upside. The clarity changes make the
discussion easier to skim without changing what the paper argues or what it can support.

## Scan 4, numerical consistency and result coverage, 20 sub-scans

Scan 4 re-read every scan 3 change in the built PDF first. All five held, counting the two deletions as
absences, and the census now reads the same way in both files.

Sub-scans run. Main-text decimals against appendix backing, interval endpoint ordering, point estimates
inside their own intervals, table column integrity, rounding precision across files, thousands separators,
percent style, design counts, replicate counts, seed attribution, Monte Carlo standard errors against
replicate counts, coverage ranges against their replicate counts, the effective-benchmark arithmetic, the
external-panel figures, table values against their source runs, every stored simulation cell against the
text that reports it, cells run and never reported, the per-size rows against their run, my own additions
against their run, and overclaiming vocabulary.

The arithmetic came back clean. Every one of the 288 main-text decimals is either backed in an appendix or
sits in a main-text table that is itself the primary source. Every interval has its endpoints in order,
every point estimate lies inside its own interval, and no quantity appears at two precisions except the
simulation input 1.2446, which is deliberately distinct from the reported estimate 1.244. The three
coverage ranges 0.928 to 0.954, 0.933 to 0.953 and 0.929 to 0.950 all describe the same twelve populations
at different replicate counts and seeds, and each is labelled with which.

Defects found and fixed. All three are the same defect class, a result that was computed and never
reported, which the selective-reporting sub-scan is built to catch.

1. The band-noise sweep ran a sixteen-fold ramp whose coverage collapses to 0.111 with 0.885 of replicates
   undefined. The appendix reported the two-fold and four-fold ramps and stopped, which left out the cell
   that most clearly supports its own reading that the loudest band rather than the unevenness is what
   breaks the estimator. It is now reported.
2. The accuracy permutation power sweep ran a share of 0.02 and rejected in 0.110 of replicates. The
   appendix jumped from zero to the 0.044 bound. The 0.02 cell is now in the same sentence.
3. The per-size run also estimated every size band with BoolQ removed, and none of those ten cells reached
   the paper. On margins all five bands exclude one, including the 1B cell whose full-battery lower
   endpoint is unavailable, and on accuracy the middle three exclude one. The appendix now reports all ten
   with their intervals, and the main text qualifies its within-size weakness sentence.

Coverage of stored results after the fixes. I checked every cell of every stored simulation JSON against
the three tex files, 58 R6 kernels and 34 further cells elsewhere. Every cell that carries a coverage,
exclusion, width, undefined or rejection number now appears in the paper.

Non-defects recorded rather than edited.

- The 43 table column mismatches my first checker reported were all my own regex failing on the custom
  `L{}` column type. The build runs under `-halt-on-error`, which would fail on a real mismatch.
- The appendix figure 1.707 for standardised accuracy inflation on eight traits and the main-text 1.705 for
  the external likelihood panel are different quantities that share three digits.

Honest ranking after scan 4. 6.2 with acceptance near 0.58, moved by defect 3 alone. The sentence saying
the within-size evidence is weaker because the 1B margin interval includes one is one of the two sentences
an earlier rebuttal audit named as the ones a reviewer would quote back, and it now carries its own answer
in the same sentence. The honest counterweight is that a reviewer can read a no-BoolQ subset result as
chosen after the fact, which is why both the appendix passage and the main-text clause present it as the
composition sensitivity at size resolution rather than as independent support. That caveat is what keeps
this a two-tenths move rather than more.

## Scan 5, figures, tables and float hygiene, 20 sub-scans

Scan 5 re-read every scan 4 change in the built PDF first, and all four held.

Sub-scans run. Float inventory, labels present, every float referenced, caption presence, caption length,
caption self-containedness, undefined symbols in legends, undefined symbols in captions, units stated,
sample sizes stated, embedded font types, font family against the body text, colour map choice, legend
completeness, panel titles, axis labels, tick legibility at print size, float placement specifiers, float
order against first reference, and duplication between a figure and a table.

The paper carries three figures and 22 tables. Every float except one is labelled, referenced at least
once, and carries a caption of at least twenty words.

Defects found and fixed.

1. The notation table in Appendix A had a caption and no label, so nothing anywhere pointed at it. A
   reader meeting the symbols in Section 2.1 had no way to learn the table exists. It is now
   `tab:notation` and the sentence that introduces the indices points at it.
2. `figures/prediction.pdf` embedded Type 3 DejaVu Serif outlines while the other two figures carry Type 1
   Nimbus, so the newest figure rendered in the wrong family and in the font class that several venues
   reject. The generating script set `font.family` and never set `pdf.fonttype`, which is the matplotlib
   default that produces Type 3. The script now sets `pdf.fonttype` and `ps.fonttype` to 42 and prefers
   Times, and the figure re-renders as a single embedded subset of Times New Roman. Nothing was
   recomputed, since the script reads the frozen `snap-r8-paired-log` result and only draws it.
3. The main-text covariance figure's right panel labels its curves `PR 3.57` and `PR 3.62`, and
   participation ratio is defined only in the appendices. The caption now defines it.

Not a defect but worth the trade. Paying for the caption line, the sensitivity paragraph's list of four of
the twelve coverage populations became a pointer to `tab:coverage`, which lists all twelve with their
constructions. The paper gained coverage of its own simulation design and lost an illustrative list.

Non-defects recorded rather than edited.

- Five floats have their `\label` before their first `\ref`. LaTeX resolves these either way, and each
  sits within a page of the text that discusses it under an `[!htb]` or `[t]` specifier.
- The identity line in the calibration figure is invisible because the recovered mean sits exactly on it,
  which is the figure's finding rather than a drawing fault.
- The diverging red and blue map in the covariance figure is the colour-vision-safe choice already.

Honest ranking after scan 5. Unchanged at 6.2 with acceptance near 0.58. The `PR` definition unblocks a
reader of the main-text figure and the font fix removes a production flaw, but no reviewer scores a paper
on embedded font types, and none of these changes what the paper argues or what it can support. The
coverage-table pointer is the only change here that a reviewer might actually notice.

## Scan 6, method completeness and reproducibility, 20 sub-scans

Scan 6 re-read every scan 5 change in the built PDF first, and caught one of them failing.

Sub-scans run. Estimator definition completeness, stated assumptions, half-assignment procedure,
weighting scheme, aggregation across benchmarks, linearisation, bootstrap construction, studentisation,
quantile rule, draw count, seed handling, cluster definition, negative-variance handling, checkpoint
selection, data filtering, item counts, software versions, artifact availability, symbol definition at
first use, and the verification script's own coverage.

The method itself reimplements from the paper alone. Appendix D gives the squared-ratio estimator, the
recipe linearisation with its standard error, the Rademacher sign construction, the pseudo-numerator, the
studentised statistic, the quantile interval, 4,999 draws and bootstrap seed zero. The cross-half identity
in Section 2.2 states its conditional-mean-zero and zero-cross-half-covariance assumption explicitly and
then names the specific way item structure can break it. Every symbol used in main-text mathematics is
either in the notation table or defined at first use, including the less common ones.

Defects found and fixed.

1. My own scan 5 fix was broken. I put `\label{tab:notation}` before its `\caption`, which LaTeX resolves
   against the wrong counter, so the main text shipped `Table ??` in the built PDF. The label now sits
   after the caption and the reference reads Table 3.
2. The verification script tested `undefined_references_or_citations` as a single boolean buried in the
   build block, which I was not reading. It now also reports `unresolved_reference_labels` by name, built
   by differencing every `\ref` against every `\newlabel` in the aux file, so a broken reference cannot
   pass unnoticed again.
3. No software version appeared anywhere, which matters here because every interval is a quantile of a
   seeded generator whose stream is version-dependent. Appendix D now records Python 3.12.13 with
   NumPy 2.0.2 under Linux beside the bootstrap seed.
4. The paper had no artifact availability statement at all, at a venue that scores reproducibility. The
   reproducibility statement listed exactly what a reader needs and never said it would be provided. After
   confirming with the author that the artifacts exist, it now commits to releasing all four alongside the
   paper.

Non-defects recorded rather than edited.

- The structured weighting results, where the estimand itself moves from 1.2446 under flat weights to
  1.0975 under item-count weights, sit in the appendix with a main-text pointer. They deserve main-text
  space that the results section needs more.
- The package version of the analysis code is deliberately left out, because the package name would
  weaken anonymity for no reproducibility gain.

Honest ranking after scan 6. 6.3 with acceptance near 0.60, moved by defect 4. Reproducibility is an
explicitly scored axis at this venue, and a reviewer working the checklist now finds an availability
commitment and a version record where before they found neither. The honest counterweight is that this is
one sentence, and a reviewer who already read Appendix D as thorough will not move their score far on it.
Defect 1 is a restoration rather than an improvement, since I introduced it myself in scan 5.

## Scan 7, corpus style study and rhythm calibration, 20 sub-scans

Scan 7 re-read every scan 6 change first. The notation reference now reads Table 3, the version record and
the release commitment are both in the built PDF, and the verifier reports no unresolved label.

This scan is also the twenty-paper style study the goal asks for. I built the corpus myself without agents,
resolving titles through the arXiv API and downloading full text from arXiv and ar5iv. It holds 23 papers
and 328,000 words of evaluation-methodology writing from ICLR, NeurIPS, EMNLP, ICML, MLSys and CACM, listed
in `research/style_study/corpus_papers.txt`. Seventeen of the 23 were published in 2022 or earlier, which
puts them before the period when generated prose became common, and they read as human on inspection. The
measurement script and its full output sit beside the list.

Sub-scans run, each a measured feature rather than an impression. Mean and median sentence length, sentence
length standard deviation, tenth and ninetieth percentiles, share under eight words, share under twelve
words, share over 35 words, first-person rate, possessive rate, hedging rate, contraction rate,
not-X-but-Y rate, semicolon rate, colon rate, dash rate, sentence-initial and medial `however`, `thus`,
`note that`, AI-vocabulary rate, `significant` rate and passive-voice rate.

The study found three divergences where this paper sat outside the observed range of all 23 papers, and
each traced to a house rule rather than to the content.

1. Sentences under eight words. Every corpus paper carries between 5.8 and 23.8 percent, with a median of
   16.3. This paper carried 0.0 percent, because the house eight-word floor forbade them outright. The
   floor was adopted to stop staccato generated prose, and at zero it had pushed the paper past uniform in
   the other direction. The paper-humanizer skill already asks for one sub-eight-word sentence per page,
   so the floor contradicted it. I retargeted the verification gate to catch true fragments under four
   words and to report the distribution against the corpus range, then raised the share by splitting 21
   main-text compound sentences and 68 appendix ones at clause boundaries that were already independent,
   which changed no wording and no number. The main text now sits at 8.5 percent, inside the range.
2. Contracted negatives. The corpus median is 0.12 per thousand words and the highest of all 23, a
   deliberately polemical essay, reaches 0.96. This paper stood at 5.25, which is 28 instances in a
   5,329-word body and more than five times the most informal paper in the corpus. I expanded all 164
   contractions across the three files. Six of the 23 papers use none at all, so zero sits inside the
   range. This reverses the house contracted-negatives rule for this paper, on the author's instruction to
   do whatever serves the paper.
3. The connective `however`. Nineteen of the 23 papers open a sentence with it, at a median of 0.28 per
   thousand words, and this paper used it zero times anywhere. Two main-text instances now put it at 0.37.

One piece of skill advice the evidence contradicted. The paper-humanizer reference, built from four
computer-vision papers, recommends sentence-initial `But` as a human habit. Seventeen of these 23 papers
never do it. I followed the corpus and left `But` out.

Divergences kept on purpose. Mean sentence length is 22.2 against a corpus median of 18.8, which reflects
a paper that carries a number in almost every sentence. Hedging runs 0.91 against 2.82 and passive voice
0.73 against 5.79, and both directions are ones this venue rewards, since the paper states claims at the
size of its evidence and names who did what.

Honest ranking after scan 7. Unchanged at 6.3, with acceptance moving from 0.58 to 0.61. No reviewer scores
a sentence-length distribution, and the content here is identical to what it was before the scan. What
changes is tail risk. A 2027 reviewer primed to spot generated prose would have found a paper with no short
sentences at all and contractions at five times the rate of the most informal paper in its field, and that
combination is now gone. I am not claiming a score move from prose, because there is no evidence for one.

## Scan 8, split verification and grammar, 20 sub-scans

Scan 7 made 89 automated prose edits, which is the largest unreviewed change of the day, so scan 8 exists
mostly to audit it. That discipline paid for itself, because the automation broke six sentences.

Sub-scans run. Double periods, comma before period, lowercase sentence starts, double spaces, stranded
conjunctions, sentence-initial `And`, space before punctuation, doubled words, article agreement before
vowels and consonants, subject-verb agreement on singular and plural subjects, double negatives, noun-phrase
sentences without a finite verb, list boundaries mistaken for clause boundaries, every short sentence read
in context, a random sample of split sites read against the sentence before, overfull boxes, unresolved
labels, page count, the corpus short-sentence share after repair, and the count of surviving `and` joints.

Defects found and fixed, all six created by scan 7.

1. A five-item list of score transformations lost its last item to a period, leaving `The sign of each
   margin.` standing alone as a noun phrase.
2. A three-rule enumeration in the design-effect simulation left `An oracle rule that uses the true value.`
   as a fragment.
3. An eight-construction interval list left `The restricted inversion at 1.074 to 1.329.` with no verb.
4. The fitted-scenario sentence split across the middle of its own list, producing both a truncated first
   half and `Their recipe weights from the same data...` as a second fragment.
5. The original scorecard's tally lost `and two predictions that could not be tested as written.`
6. A four-way parallel list of interval constructions was split for no gain, and reads better joined.

How they were found. The mechanical artifact scan came back at zero, and a subject-and-verb heuristic
produced 62 hits that were all my own verb lexicon being incomplete. What actually found the six was
reading every sentence in the paper under ten words, 150 of them, against its neighbour. The lesson is
that an automated prose edit needs a human-style read of its output, not another automated check.

After repair the main text holds 8.5 percent of sentences under eight words, still inside the corpus range
of 5.8 to 23.8. The build carries no overfull box, no unresolved label and nine main-text pages.

Non-defects recorded rather than edited. The grammar sweep returned five hits and all five were false,
being `the plug-in in 0.81`, `a usable`, `half-A and half-B`, and two plural subjects correctly taking
`do not`. Three noun-phrase candidates were also false, since `differ`, `agree` and `ran` are verbs my
pattern did not list.

Honest ranking after scan 8. Unchanged at 6.3 with acceptance near 0.61. This scan restored correctness
that scan 7 broke and added nothing the paper did not already have. Recording it as a zero-improvement
scan is the accurate reading, and the useful result is that the review-the-previous-scan rule caught six
defects that would otherwise have shipped.

## Scan 9. Reviewer simulation

Review of scan 8. The six repaired sentences all read correctly in the built PDF, and the short-sentence
share stayed at 8.5 percent. Nothing from scan 8 needed reverting.

Twenty-one sub-scans ran under one question, which is what an ICLR reviewer would write in the box after
reading the paper once. The rhythm sub-scans came back mostly negative and are recorded below as
non-defects. The substantive finding is the one that moved the paper.

Defect 1, the paper's most actionable number was buried. The simulation showing that a comparison rule
assuming benchmark independence declares a margin difference in 0.113 of replicates with no true gap,
against a nominal 0.05, sat in the last paragraph of the discussion. That number is the answer to the
question a reviewer asks about any measurement paper, which is what a practitioner does differently
after reading it. The abstract closed instead on a generic recommendation to report replicate
uncertainty. The sentence now appears in the abstract with the corrected 0.051 beside it.

Paying for it. The addition cost two lines and the main text went to ten pages three times during the
repair. The final accounting removed the secondary prediction-model result from the abstract, which
reported that a full correlation model beats independence on margins and that no model separates on
accuracy. That result is a null on the scale most readers care about and the body and Table 2 still
carry it in full. The abstract fell from 279 words to 260 and now ends on a consequence rather than on
advice. Four smaller redundancies paid the rest, all of them restatements of a number given one clause
earlier, and the lineage sentence in related work lost a clause about genetic components that the model
never claimed to separate.

Defect 2, self-inflicted. Compressing the discussion sentence dropped the condition that makes 0.113 a
false positive rate, leaving it reading as an unconditional error rate. Caught by re-reading the
compressed sentence in isolation rather than in the diff. Restored.

Defect 3, self-inflicted. Trimming the abstract's checkpoint sentence left `paired intervals for both
changes` with only one change named. Rewritten to `the paired differences`.

Non-defects recorded rather than edited. Short-sentence clustering is not a defect, since corpus papers
routinely run ten to forty four consecutive sentences under twelve words. The abstract did carry four
consecutive sentences of 46, 43, 43 and 41 words against a corpus p90 of 34, and three were split before
the substantive work began; it now runs a maximum of 33 with a spread from 7 to 33. One sentence-initial
`So` was replaced with `We therefore`, since 20 of the 23 corpus papers never open a sentence with it.
Related work stays at roughly 210 words. Expanding it means cutting a result to pay for the page, and on
the reviewer trade that is a net loss, so the thinness is accepted rather than fixed.

Honest ranking after scan 9. 6.4 with acceptance near 0.62, up from 6.3 and 0.61. The increment is small
and I am reluctant to claim more. Nothing new was measured and no weakness was closed. What changed is
that the strongest existing result now sits where a reviewer reads it in the first thirty seconds, and a
null moved out of that position. The single-population scope, the exploratory status, the accuracy
interval that includes one, and the novelty framing as an established construction applied to a new unit
are all untouched and all still cap this paper below a 7.

## Scan 10. Notation, derivations, and the stylometric residual

Review of scan 9. The abstract reads correctly in the built PDF and now closes on the 0.113 to 0.051
correction rather than on advice. The two self-inflicted defects scan 9 recorded are both repaired in the
built text. Nothing needed reverting.

Twenty-two sub-scans across the estimator exposition, the stored numeric ledger, and the style corpus.

Defect 1, a symbol collision two rows apart in the notation table. The accuracy trait was written
$y^A$ while the half index runs over $\{A,B\}$, so $y^A_{crj}$ could be read as either the accuracy score
or the half-A score. The table listed both meanings on consecutive rows. The trait superscripts are now
$y^{\mathrm{marg}}$ and $y^{\mathrm{acc}}$, which leaves the half index unambiguous everywhere. The trait
symbols appeared only twice in the whole paper, so the rename was cheap and the halves keep the letters
they carry in the prose.

Defect 2, dead notation. The table declared $\sigma_{\mathrm{indep}}$ and no equation or sentence ever
used it. Rather than delete the row, the identity it belongs to is now stated, since
$\sigma_{\mathrm{indep}}^2=\bar\sigma_E^2/K$ makes $\Lam=\sigma_{\mathrm{agg}}/\sigma_{\mathrm{indep}}$
explicit, which is the paper's headline quantity written as a ratio for the first time.

Defect 3, the paper's largest stylometric deviation from the corpus. Across the 23 human papers, passive
constructions run between 1.91 and 9.33 per thousand words with a median of 5.79. This paper's main text
ran 0.75, below every one of them. That is the fingerprint of a style rule rather than of a writer, since
banning passive voice is standard advice in generated-prose guidance and is not how evaluation-methodology
papers actually read. Five main-text sentences were converted where passive is the better academic choice,
including two that had an inanimate subject performing a human verb, and the main text now runs 2.10.

What was deliberately not fixed, and why. The appendices run 1.27 and the whole paper 1.50, both still
below the corpus minimum. Closing that gap needs roughly fifty more conversions, and an inspection of the
candidates shows why it should not happen. Of fifty-six procedural sentences in the appendices, almost all
are first-person accountability statements, such as choosing subsets after seeing the full-sample
estimates, not implementing a planned separation, and not testing an additional assumption. Rewriting
those in the passive would hide the agent in exactly the sentences where naming the agent is the point.
The candor is worth more to a reviewer than the statistic, so three genuine false-agency constructions
were converted and the rest were left alone. The deviation is recorded here as accepted rather than closed.

Non-defects recorded rather than edited. Every effective-count entry in Table 1 was recomputed as
$K/\widehat\Lam^2$ and all six agree to the reported digits. The two derived off-diagonal sums were
recomputed from the stored trace shares of 0.679 and 0.844 and give -0.155 and -0.061 against the reported
-0.15 and -0.06. The illustrative resolution ratio at $p=0.35$ recomputes to 1.658 against the reported
1.66, and its stated minimum of $\pi/2$ is correct. Every unbiasedness claim in Section 2 was checked by
expanding the expectations, and the $R/(R-1)$ factors cancel as the text states. All seventeen ledger
claims resolve to numbers present in the manuscript once rounding is applied, and the two that first
appeared missing were rounded reporting rather than discrepancies. Four equation labels are defined and
never referenced, which costs the reader nothing since the equations are numbered anyway.

Honest ranking after scan 10. 6.4 with acceptance near 0.62, unchanged. The notation collision was real
and would have cost the paper a line in a careful reviewer's writing-quality remark, but it was not going
to change an accept or reject. The passive-voice finding is the most interesting result of this scan and
it produced the smallest edit, because the measurement was right and the obvious remedy was wrong. No
substantive weakness moved.

## Scan 11. Floats as standalone artifacts

Review of scan 10. The renamed trait superscripts render correctly and the half index is now unambiguous
throughout. The new $\sigma_{\mathrm{indep}}$ identity sits where the aggregate variance is derived. The
five passive conversions were read back in full context and all five hold their meaning.

Defect 1, and the largest thing any scan has found. Two of the three figures carried a complete hidden
copy of a page from an earlier build of this paper. The submission PDF's text layer held the ICLR running
header twice on the figure page, together with a stale caption reading `Figure 1: R-hat on all 125
configurations, margin (left) and accuracy (centre), traits ordered by scoring`, which contradicts the
caption the page actually displays. None of it was visible in the rendered page, and none of it appeared
when the figure files were read on their own, because the content sits outside their media boxes and the
text is encoded as subset glyph indices rather than as readable strings. It surfaced only from extracting
the built PDF page by page and noticing that page seven reported two running headers where every other
page of fifty-two reported one.

How it got there. Both files carry a Ghostscript and then a MuPDF producer chain on top of a Matplotlib
creator, and both were roughly six times the size of the one figure that still carries the plain
Matplotlib producer. A crop step had reduced the media box without discarding the page behind it.

The repair. Both figures were redistilled, which reproduces them pixel for pixel at 200 dpi and drops the
hidden content. covariance fell from 218,893 to 80,152 bytes and calibration from 209,065 to 32,836. The
built PDF fell from 928,328 to 628,537 bytes, so just under a third of the submission was hidden material
from an older draft. The figure page now reports one header, the stale caption no longer appears anywhere
in the text layer, and all 24 fonts remain embedded and subset with no Type 3.

Why it mattered beyond tidiness. Any text extraction of the submission, which is what indexing and
screening pipelines run, would have read a figure caption that the paper does not contain and that
disagrees with the one it does. The anonymity check was rerun over the extracted text and still finds no
personal identifier, so nothing was leaked, but the exposure was real until it was removed.

Defect 2, a caption regression. The hidden old caption named which panel was which, and the current
caption had dropped that, leaving a reader to infer panel identity from small in-plot titles. The caption
now names margins on the left, accuracy in the centre, and the spectra on the right, and the main text
still holds nine pages.

Non-defects recorded rather than edited. Every table and figure is referenced somewhere in the document,
and the four unreferenced equation labels from scan 10 are the only labels without a pointer. The build
reports zero overfull boxes; the nineteen box warnings are all underfull hboxes inside ragged-right table
cells. Both diverging heatmaps and the two-series spectrum panel survive colour-blind reading, since the
series differ in marker shape as well as hue. Both cleaned figures were rendered and compared against
their originals before the swap.

Honest ranking after scan 11. 6.4 with acceptance near 0.62, unchanged. The hidden-content defect was
serious as a submission-hygiene failure and would have embarrassed the authors if anyone extracted the
text, but no reviewer reads a text layer and no score moves because a PDF got smaller. The caption fix is
worth a fraction of a point at most. Recording this as a zero-improvement scan on the score while noting
it is the most important thing found so far is the accurate reading.

## Scan 12. Provenance of every number, and the bibliography

Review of scan 11. The rebuilt figures render identically to their originals, the figure page now reports
one running header like every other page, and the restored panel guide reads correctly in the caption.

The provenance sweep. Every decimal number in the paper was extracted and matched against the 311 MB of
stored artifacts under `research`, allowing a reported value to match a longer stored value truncated to
the reported digits. All 218 distinct decimals in the main text matched. Of 982 distinct decimals in the
appendices, 981 matched. The single exception is the planned effective coefficient of 0.0911, which is
not a stored output at all but a derivation from the planned threshold, since $(1.349^2-1)/9=0.09109$ for
ten benchmarks. The observed value quoted beside it checks the same way, since $(1.244^2-1)/9=0.06084$
rounds to the 0.061 the sentence gives. Twelve hundred numbers with no unsupported value is the strongest
evidence any scan has produced that the manuscript reports what was actually computed.

The bibliography. All 53 entries are unique, all 53 are cited, every citation resolves, and no entry is
orphaned.

Defect 1, two published works cited as preprints. `kipnis2024` and `hofmann2025` carried no venue. Both
were checked against OpenReview rather than from memory. metabench returns venue `ICLR 2025 Poster` with
an author list matching the entry exactly, and Fluid Language Model Benchmarking returns venue `COLM 2025`
with an inproceedings record and an exact author match. Both entries now carry their venue, and the
metabench in-text year moves from 2024 to 2025 to match the published version while its key is unchanged.

Non-defects recorded rather than edited. The two primary data sources were already cited to their venues,
DataDecide to ICML and PolyPythias to ICLR 2025, and Signal and Noise to NeurIPS 2025. The remaining
sixteen preprint citations are genuine preprints, mostly 2026 work with no venue yet, and the two
classical-methods entries flagged by the venue pattern are books. An automated lookup service returned
HTTP 429 and a second sat behind a bot check, which was left alone rather than worked around.

Honest ranking after scan 12. 6.4 with acceptance near 0.62, unchanged. Two venue corrections do not move
a score. The provenance result does not move it either, because a reviewer assumes numbers are real and
gives no credit for proving it, but it is the check that would have been catastrophic to fail, and it
passed on twelve hundred values.

## Scan 13. The argument as a reviewer follows it

Review of scan 12. Both corrected citations render with their venues, and the metabench in-text year now
reads 2025 against the published ICLR version while its key is unchanged, so no other citation moved.

Defect 1, the introduction never stated the paper's positive result. Its empirical paragraph opened on
`The accuracy estimate is close to independence for the full battery` and then spent 170 words on how
fragile that null is. A reviewer who reads the abstract, the introduction, and the discussion, which is
how a paper is usually triaged, finished the introduction believing the paper had found nothing. The
margin result, which is the finding that survives every sensitivity in the paper, appeared nowhere in the
section. The paragraph now opens with the 1.244 factor and its interval excluding one, and the accuracy
null follows as the contrast it actually is. The page budget was paid from the same paragraph, where a
clause asserting that the intervals all land above one restated the preceding clause.

Defect 2, a baseline lost to my own earlier compression. Scan 9 trimmed the abstract's checkpoint sentence
to `moves accuracy to 1.130`, which invites a reader to subtract from the 1.078 headline when the actual
baseline is the 1.082 of the 123-configuration subset. The abstract again names the subset and both
endpoints. This is the second time a scan-9 compression lost a qualifier, which is worth recording as a
pattern rather than as two accidents.

Non-defects recorded rather than edited. A sweep for causal and evaluative overclaiming returned three
sentences, and all three are either a direct observation from a computed index or an explicit denial of a
stronger reading. There are no vague forward references of the `as we show below` kind anywhere in the
main text, and all eleven appendix pointers name a label. The contributions paragraph promises four things
and the section order delivers them, with the mechanism work split between its setup in Section 4 and its
results in Section 5.2. The paper states what would have falsified its resolution model and reports that
the planned threshold could not have done so, which is a candid inclusion most submissions omit.

Honest ranking after scan 13. 6.5 with acceptance near 0.63, up from 6.4 and 0.62. This is the first
increment since scan 9 that I think is defensible. The introduction is the section a reviewer reads most
carefully before forming a prior, and it previously argued against the paper by omission. Stating the
surviving result there costs nothing in honesty, since the fragility follows immediately and in the same
paragraph, and it removes a reason to score the work as a null finding.

## Scan 14. The appendices as a reader-facing artifact

Review of scan 13. The introduction's empirical paragraph now opens on the 1.244 factor, and the abstract
again names the 123-configuration subset and both checkpoint endpoints.

Defect 1, a stray numbered heading. Appendix C organises its 420 lines with eighteen run-in paragraph
headings, and one late heading had been written as a subsection instead. It rendered as a single `C.1` at
the very end of an otherwise unnumbered section, which reads as a formatting accident rather than as
structure. It is now a run-in heading like the other eighteen, and no `C.1` appears in the built document.

Defect 2, two headings with the same name. `Adjacent-checkpoint variation` appeared twice in a row, once
for the nine PolyPythias 160M runs and once for DataDecide. The first now names its population.

Defect 3, a claim that reads wider than its evidence. The main text said that all five bands exclude one
once BoolQ is removed, in a sentence about the 1B margin estimate. The appendix supports that for margins,
where the five intervals run from \ci{1.325}{1.742} to \ci{1.215}{2.001}, but on accuracy only the middle
three bands exclude one while the smallest and the largest do not. A reviewer skimming the sentence could
have read it as covering both scales, which would be false. The sentence now says `on margins`.

Non-defects recorded rather than edited. No sentence longer than seven words is duplicated between the
main text and the appendices, and no pair reaches a Jaccard overlap of 0.8, so the appendices restate
nothing. There are no TODO, FIXME or placeholder markers anywhere in the sources. The compute table is
explicitly labelled as the planning budget rather than as measured cost, which is the honest framing given
that not every listed operation was measured. The practical-considerations subsection carries four real
entries, each naming a specific trap, which is the minimum a reader should expect and more than most
submissions include. All six headline values appear in both the main text and the appendices, and each of
the eight distinct main-text pointers into an appendix was opened and found to contain what the pointer
claims.

Honest ranking after scan 14. 6.5 with acceptance near 0.63, unchanged. The stray `C.1` would have been
noticed and would have cost a sentence in a writing-quality remark, and the scale ambiguity was the kind
of thing a hostile reviewer quotes back, so removing it matters more than its size suggests. Neither moves
a score on its own.

## Scan 15. ICLR 2027 submission conformance

Review of scan 14. No `C.1` appears anywhere in the built document, the two adjacent-checkpoint headings
now name their populations, and the per-band claim reads `on margins` as the appendix evidence requires.

This scan found nothing wrong with the submission itself, which is worth recording as plainly as a scan
that found ten things.

What was checked and passed. The document metadata carries an empty author field and a title only. The
PDF was fully decompressed with qpdf and searched for the user name, home paths, the project path and the
account address, and it contains none of them, so the anonymity check now covers compressed object
streams rather than only the extracted text layer. The three embedded figures record relative paths in
their PTEX entries rather than absolute ones. Page size is letter at 612 by 792 points. The main text is
nine pages and the three required statements sit after it, where they do not count against the limit. No
acknowledgement, institution, funder or grant number appears anywhere. There is no self-reference of the
`in our previous work` kind. The single URL in the bibliography returns HTTP 200.

No page-limit gaming. The only spacing commands in the main text are a `\small` with adjusted column
separation inside the two tables, and the row stretch there is 1.12, which increases the spacing rather
than compressing it. There is no `\vspace`, no `enlargethispage`, no altered text height and no changed
baseline stretch anywhere in the sources.

One improvement to the safety net. The verifier compared only `iclr2027_conference.sty` against its
pristine copy, so an altered `fancyhdr.sty` or `natbib.sty` could have changed the layout without tripping
the check. All three now have to match byte for byte, and the report names which files it checked. All
three do match.

Observed and left alone. The paper carries no footnotes at all, where the corpus papers use them for
caveats and side facts. Adding footnotes to a manuscript already at the page limit would cost results, and
adding them only in the appendix to move a statistic is the same cargo-culting the passive-voice finding
in scan 10 was right to refuse. Recorded rather than acted on.

Honest ranking after scan 15. 6.5 with acceptance near 0.63, unchanged. Conformance is a gate rather than
a score, so passing it earns nothing and failing it would have cost everything. The widened style check
protects a future revision rather than this one.

## Scan 16. Statistical rigor, multiplicity, and selective reporting

Review of scan 15. The widened style check passes on all three template files and names them in the
report, and the conformance findings all still hold on the rebuilt document.

Defect 1, a calibration attached to more than it measured. The introduction said that the accuracy
interval stops including one under five of the 25 recipe removals, the 750M band, and WinoGrande, and
called that `a count a null sweep reaches in 0.018 of replicates`. Tracing 0.018 to its source shows it is
the rate at which five or more recipe deletions flip under a true-one null, conditioned on the replicates
whose full interval includes one, pooled over two runs at 10,000 populations. It is not the rate for the
compound event the sentence lists, which also includes a size band and a trait and would be rarer still.
The sentence now attributes the rate to the recipe count that was actually calibrated.

Defect 2, a count that disagreed with its own appendix. The same sentence listed seven exceptions while
the appendix counts eight, because the main text omitted the BoolQ removal from the list. Both now say
eight.

A false pass in my own scan-12 sweep. The provenance check matched the main text's 0.018 against a stored
0.0181, which is the accuracy effective coefficient and a different quantity entirely. Prefix matching
across a corpus that large will do this, so the sweep should be read as evidence that no number is
invented rather than as evidence that every number is attached to the right analysis. Scan 16 caught this
one by reading rather than by matching.

Non-defects recorded rather than edited. Every sentence in the main text that says an accuracy interval
excludes one states in the same sentence that the paired difference includes zero. The paper refuses to
read its own small full-battery estimate as evidence of independence and reports that its design excludes
one in only 0.111 of replicates at the fitted accuracy cell against 0.970 on margins, which is a candid
power admission. Intervals are called nominal throughout and their simulated coverage is reported
separately rather than assumed. The primary interval construction is justified on simulated coverage
rather than on how it looked against the data, and the one construction chosen after seeing results says
so. The bootstrap uses 4,999 draws, which keeps the quantile index integral at 95 percent, and the
coverage shortfall is separated from Monte Carlo noise by two repeats at 10,000 replicates where the
reported spread is several times the Monte Carlo standard error.

Honest ranking after scan 16. 6.5 with acceptance near 0.63, unchanged. The misattached calibration was a
genuine precision defect in the introduction and a reviewer who chased the number would have found it, but
correcting it does not add evidence. What this scan mostly establishes is that the inferential claims
survive an adversarial reading, which was already the paper's strongest property.

## Scan 17. Related work, the weakness carried since scan 3

Review of scan 16. The corrected null-sweep sentence now attributes 0.018 to the recipe count it
calibrates and lists eight exceptions to match the appendix.

Defect 1, the closest contemporary work got six words. The section said only that `\citet{heineman2025}
study evaluation signal and noise`. That work appeared at NeurIPS 2025, uses DataDecide among its data,
and asks a neighbouring question about evaluation noise, so a reviewer who knows it would have asked how
this paper differs and found no answer anywhere, since the appendix mentioned it once only as a co-author
link for another citation. The sentence now says what they measure, per-benchmark signal and noise on
DataDecide and OLMo checkpoints related to decision accuracy, and names the difference, which is that they
do not estimate covariance between benchmarks. Stating what the neighbour does before naming the gap is
also what makes the gap claim credible rather than dismissive. The page was paid for by dropping two
permutation means whose ranges are given in the same sentence and whose values are in the appendix.

Defect 2, the citation whose title most threatens the novelty claim was left undistinguished. BenchScope
asks how many independent signals a benchmark provides, which sounds like the effective count this paper
reports, and the appendix stated what it does without saying why it differs. It now says that BenchScope
counts variation between different models while our effective count describes run-to-run covariance at a
fixed configuration. The main-text gap sentence already carried the qualifiers `of run noise` and `for a
fixed battery` that make it survive this comparison, so it was left alone.

Non-defects recorded rather than edited. The gap claim is hedged as `among the studies we located`, which
is the honest form. The section is now 223 words, still short for an ICLR related-work section, and it
stays short on purpose, since expanding it means deleting a result to pay for the page and the section now
engages the one neighbour that mattered.

Honest ranking after scan 17. 6.6 with acceptance near 0.64, up from 6.5 and 0.63. I am fairly confident
in this one. An unanswered `how is this different from Signal and Noise` is the kind of objection that
turns a weak accept into a weak reject, because the reviewer cannot tell whether the authors knew about
the work or avoided it. Answering it in the section itself removes that reading, and the BenchScope
clarification closes the same hole on the novelty claim.

## Scan 18. Terminology discipline

Review of scan 17. The Heineman comparison and the BenchScope clarification both read correctly in the
built document, and related work sits at 223 words with the page still at nine.

Defect 1, two defined terms meaning the same thing, and one of them also meaning a third thing. The paper
defined trait as a benchmark-level score and phenotype as the measured score, which are the same object,
and then used trait 90 times and phenotype 11 times. Worse, seven of the phenotype uses meant neither
object but the score scale, as in `either phenotype` for margins and accuracy, and two of those were table
column headers whose entries read Margin and Accuracy. A reader who accepted the stated definition would
have parsed those sentences wrongly. Phenotype now survives only where it earns its place, in the SNAP
acronym and in the quantitative-genetics method names `phenotypic plug-in` and `phenotypic correlation`,
and the seven scale uses say score scale. Both definitions now name trait as the word the paper actually
uses, so the genetics borrowing is explained rather than left as a silent synonym.

Non-defects recorded rather than edited. The word cell appears 66 times in the appendices without a
definition and in three senses, a grid position in a simulation sweep, a configuration, and a size band's
estimate. Every use is clear from its sentence, cell for a grid position is ordinary statistical English,
and `scattered cells` set against `whole recipes` says something `configurations` would say less well, so
none of them was changed. Configuration, recipe, replicate run and seed are each defined at their first
technical use in Section 2, and their earlier appearances are in the abstract, where a term standing
undefined is normal.

Honest ranking after scan 18. 6.6 with acceptance near 0.64, unchanged. A reviewer would not reject over
a synonym, but the phenotype collision was the kind of thing that makes a careful reader slow down and
reread, and three of the seven bad uses sat in table headers where a reader checks a definition rather
than infers one. Worth fixing, not worth a point.

## Scan 19. Reading the built pages as a reviewer reads them

Review of scan 18. Phenotype now appears only in the acronym and the two genetics method names, and both
definitions name trait. The seven converted sentences and two table headers were read in the built PDF.

This scan rendered pages and read them rather than grepping the source, which is how the two findings
below surfaced after eighteen scans of source-level checking missed them.

Defect 1, the reader meets Table 3 before Table 1. The first table reference in the document sits on page
two and points at the notation table, which is numbered 3 because it lives in Appendix A. A reader has
seen no table at that point and is sent to a number two ahead of the one they are about to meet. The
sentence now says Table 3 in Appendix A, so the number reads as a destination rather than as a gap.

Defect 2, an implicit causal link at a paragraph end. The limitations paragraph closed by saying that no
claim is made about the competence mechanism, which needs held-out loss on the same checkpoints, and then
that 80 of the 125 repositories refuse an unauthenticated request. The connection between the two, which
is that the loss cannot be scored because the weights are gated, was left for the reader to supply. The
sentence now reads that the mechanism needs held-out loss scored on the same checkpoints that 80 of the
125 repositories will not serve without credentials, which is also one word shorter.

Non-defects verified by arithmetic while reading. The accuracy upper endpoint of 1.157 maps to the quoted
$\bar r_E<0.038$ and $K_{\mathrm{eff}}>7.47$, which recompute to 0.0376 and 7.470. The BoolQ passage
counts close, since 2,938 passages carrying 3,270 questions with 578 questions in shared passages implies
246 shared passages and 2,692 singletons, which sum back to both totals. The resolution model's minimum of
$\pi/2$ does exceed the planned 1.4 threshold, so the paper's statement that the threshold could not have
falsified the model is correct rather than rhetorical. Equation 5 is referenced in the results, so the
unreferenced-equation note from scan 10 covers four labels and not the central one.

Honest ranking after scan 19. 6.6 with acceptance near 0.64, unchanged. Neither finding changes an
assessment. The useful result is methodological, which is that rendering and reading pages found two
things that nineteen scans of source grepping did not, so the remaining scans should include a reading
pass rather than only mechanical sweeps.

## Scan 20. Reading the appendix pages the way a determined reviewer reads them

Review of scan 19. The forward table reference now reads Table 3 in Appendix A, and the limitations
sentence carries its causal link. Both render correctly. Scan 19's methodological finding was that
rendering and reading beats source grepping, so this scan applied that to the forty appendix pages, which
no earlier scan had read as continuous prose. It read pages 14, 17, 20, 23, 27, 30, 33, 36, 41, 44, 48 and
52 and checked every number on them against the stored artefacts.

Defect 1, a wrong digit in a permutation standard deviation. Appendix C reports that re-drawing the item
half split moves the estimate further than permutation does, and gave the permuted accuracy spread as
0.0055 in the comparison sentence two lines after giving it as 0.0053 in the sentence that introduced it.
The artefact at research/outputs/snap-r6-itemshare-b/r6_itemshare_b.json records 0.005336, so 0.0053 was
right and 0.0055 was a transcription error. Every other number in that passage reproduces exactly,
including the 200-split spreads of 0.0018 and 0.0083, the permutation means of 1.2428 and 1.0763, the
tail shares of 0.087 and 0.352, and the medians and ranges of the re-split distributions. This is the
first wrong digit found in twenty scans, and it was found by reading two adjacent sentences together
rather than by matching either one against storage on its own.

Defect 2, a bias claim that outran its own table. The band-share power sweep reported that the plug-in
estimate misses the truth by 0.0009 or less at every share up to a quarter. The stored cells give biases
of 0.00037, 0.00029, 0.0009, 0.00142 and 0.00738 at shares of zero, 0.02, 0.044, 0.10 and 0.25, so the
claim held only as far as the bound and failed at the two larger shares. The accuracy version of the same
sentence, which claims 0.0034 or less, is exact and inclusive of the quarter, which is how the margin
sentence read as though it had been checked. It now states 0.0009 up to the bound and 0.0074 through a
quarter, which is what the run measured.

Defect 3, a rounding slip in the same paragraph. The reported accuracy standard error under no sharing is
0.039548, quoted as 0.0396. Corrected to 0.0395.

Defect 4, an overstated equality. The step comparison said the 750M margin ratio equals the PolyPythias
value of 0.890 when our own number on the same line is 0.889. It now says it sits within 0.001 of that
value.

Defect 5, two undefined symbols in a table that the main text promises is complete. Section 2.1 says the
notation table collects every symbol used below, and the appendices use $\Lambda_M$ and $\Lambda_A$
thirteen times without ever defining them. The notation table gains a row. A third symbol,
$\Lambda_{\rm alt}$, appeared exactly once inside a scorecard cell and is now stated in words, since one
occurrence does not earn a symbol.

Defect 6, model labels that disagreed with their own figure. The prediction comparison writes P1 G and
P2 R in prose while Figure 3 and its axis labels write P1G and P2R. Twelve occurrences in the source now
match the figure, which is the artefact that cannot be edited cheaply.

Defect 7, a broken relative clause on the last page. Raw cross-half products contain squared configuration
means, which the analysis record reports can inflate the ratio, has no grammatical reading. Rewritten as
two coordinated clauses.

Defects 8 through 10, three sentences that read as unfinished. The estimator behaves, with no complement;
the joint corner the data allows it covers, which garden-paths on allows; and a separate run at 1B now
covers five recipes rather than one, where now is a revision artefact and rather than one refers to a
count the reader was never given. All three rewritten.

Defect 11, a table label the prose never bound to its own term. Table 19 labels its rows bits per byte
while the surrounding prose calls those estimates likelihood, which is the paper's term elsewhere and is
correct, but the bridge between the two was left implicit. One sentence now carries it.

Non-defects verified by arithmetic while reading. The repository census closes three ways, at 80 plus 5
plus 40 equal to 125, at 16 plus 1 plus 8 equal to 25 per band, and at 8 resolving recipes plus 17 absent
ones equal to 25. The seed-matching census closes at 20 plus 4 equal to 24 branch cells and 15 cells
covering 5 recipes at 1B. The planning scorecard's eleven predictions match their eleven table rows, and
its four failures match the caption. Table 9 supports its own summary, since five margin estimates and
four accuracy estimates exceed one and the BoolQ-removed bands exclude one in five cells on margins and
three on accuracy. Equation 19 derives correctly from its stated assumptions, including the factor of two
in $k=2(1-\rho_g)/\rho_g$ that comes from a half carrying twice the item noise of the full set. The
item-level channel accounting of 0.001 and 0.002 against excesses of 0.244 and 0.078 reproduces from the
stored means. The GPU arm's 18 of 4,755 is 0.38 percent and its accuracy shift of 4.2e-4 is the stated
difference of the two quoted battery scores.

Honest ranking after scan 20. 6.7 with acceptance near 0.65, up from 6.6 and 0.64. The move is small and
it is earned by one thing only, which is that a reviewer who checks the appendix arithmetic now finds it
checks out, where before this scan they would have found a number that contradicts the sentence two lines
above it and a bias claim that its own table refutes. Reviewers who dig into appendices are the ones who
write the decisive reviews, and a wrong digit found by a reviewer costs far more than the 0.1 this fix
returns. The seven presentational fixes do not move the rating on their own. Nothing about the design,
the evidence, or the contribution changed in this scan, and the ceiling those impose is unchanged.

## Humanizer and slop-prevention pass, run last as instructed

All seven installed skills were applied to the finished manuscript after every scan was complete.
These are paper-humanizer, ml-paper-voice, stop-slop, humanizer, content-humanizer, remove-ai-marks and
impeccable. House overrides applied throughout, which are no prose colons, semicolons or dashes, no
eight-word sentence floor, and the truthful AI disclosure retained.

What the detectors found clean. Zero em dashes and zero en dashes across all four source files. Zero
curly quotation marks. Zero non-ASCII codepoints of any kind, so no zero-width joiners, no soft hyphens,
no homoglyphs and no narrow spaces, which is the whole of what a Unicode watermark scan looks for. Zero
prose colons and zero prose semicolons. Zero rhetorical questions. Zero negative parallelisms, zero
contrast crutches of the is-not-X-but-Y family, and zero hedge stacks. Zero instances of In conclusion,
Overall or To sum up. No bulleted list anywhere in the main text and no summary section. The PDF carries
an empty Author field, so anonymity holds at the metadata level as well as in the body.

Banned vocabulary. Thirty-one hits resolve to three fixed technical terms on inspection, which are
cluster-robust in the Cameron and Miller sense, statistical leverage in the cr3 correction, and the
evaluation harness the releases share. None is the banned sense of the word. Adverb census over 1,312
sentences returns only, approximately and exactly as the only items above twelve occurrences, and none of
the intensifier family that marks generated prose.

Rhythm. Sentence length averages 19.2 words in the main text and 23.0 in the appendices, with standard
deviations of 9.9 and 12.0 and a range of 4 to 63 words. Runs of three consecutive sentences within three
words of each other occur in 2.7 percent of positions, so the metronome tell is absent.

Defect the pass found and fixed, one. Appendix D contained a single paragraph of 32,909 characters, which
is roughly 5,300 words and eleven printed pages of text with no break in it, and two more of 4,491 and
2,959 characters, and six others above 2,400. Eleven unbroken pages is worse for a reviewer than any
stylistic tell, and no source-level scan catches it because the source is one line. It was split at 43
topic seams across the nine paragraphs, with no word changed, taking the appendix paragraph count from
132 to 177 and its longest paragraph from 195 sentences to 13. The document grew by one page, from 52 to
53, and the main text stayed at nine.

Second defect, a repeated syntactic template. The pseudo-cleft opener What X is Y appeared nine times,
five of them as the near-identical What the X costs or buys is Y inside one appendix. A pseudo-cleft is
ordinary English and human writers use it, but five copies of one frame in one section is a generated
rhythm. Six were converted to plain subject-verb order and three kept.

Honest ranking after the humanizer pass. 6.7 with acceptance near 0.65, unchanged by the prose work
itself. The paragraph split is the one change here a reviewer would actually feel, and it improves how
the appendix reads rather than what it says, so it does not move a rating that is set by the design and
the evidence. The detectors finding nothing else is the expected result after twenty scans, not a
surprise, and it is recorded here as a negative result rather than as a win.

## Scan 21. Conformance to the measured style corpus, and what the corpus does not justify changing

Review of scan 20 and the humanizer pass. All eleven scan-20 fixes render. The 43 paragraph splits hold,
the document sits at 53 pages with the main text at nine, and no split orphaned a topic sentence except
where noted below.

Sub-scan on the corpus. The 23-paper corpus in research/style_study, fetched from arXiv by identifier and
measured per 1,000 words, was re-scored against the current build. Twenty-one of the twenty-three metrics
now sit inside the corpus range. Passive voice, which sat at 0.73 and below every corpus paper when the
study was first run, now measures 2.02 against a corpus floor of 1.91, so the appendix conversions carried
it into range without costing the first-person accountability that is the paper's strongest rhetorical
asset. Two metrics remain below every corpus paper. Colons run 3.85 against a floor of 5.93, which is the
deliberate house rule and stays. Hedge markers run 0.92 against a floor of 1.00, which is a real
divergence and is examined below.

Defect 1, a null result promoted to a positive attribution. The results section said that the BoolQ
diagonal moves by 0.03 and 0.15 percent under passage-aware splitting, so its trace share reflects a large
seed variance rather than leaked passage effects. The measurement eliminates one alternative inside one
benchmark. It does not establish what the trace share is, and the appendix says of the companion
cross-benchmark diagnostic that it has no power rather than that it is a clean check. The sentence now
says that shared passages do not account for the trace share, and names the channel the check does not
reach. This is the sentence in the results a referee would have quoted back.

Defect 2, an opaque opener created by the humanizer pass. Three of the 43 new paragraph boundaries begin
with a backward pronoun. Two of them, Those sweeps and Those drops, read as ordinary transitions that name
what came before. The third, Neither test, sat too far from its antecedents, so it now names the band test
and the mirror test.

Measured and declined. Mean sentence length is 22.3 words against a corpus ceiling of 23.5, median 20.0
against a ceiling of 20.0, and the share under twelve words is 0.189 against a floor of 0.12. The paper
therefore sits at the long end of the human range on three related measures at once. Chopping sentences
to move those numbers would be gaming a histogram no referee computes, and the dispersion measure that
actually governs how prose reads, a standard deviation of 12.3 against a corpus median of 12.4, is already
exactly typical. The hedge deficit was examined the same way. Sweeping every causal and mechanistic claim
in the main text returned 23 candidates, of which 22 are measured justifications that are correctly
unhedged, and the twenty-third is defect 1 above, which was repaired by removing an overclaim rather than
by adding a hedge word. Sprinkling may and might to reach a corpus floor would lower the paper.

Integrity sub-scans, all clean. Fifty-three citations resolve and no bibliography entry is uncited. Every
referenced label is defined, with four unreferenced equation labels carried from scan 10. Zero undefined
references and zero overfull boxes in the build log. Every font embedded. No author, affiliation, email,
path or repository string anywhere in the sources, and an empty Author field in the PDF. The headline
numbers reproduce exactly from storage, including a near-coincidence worth recording, which is that
removing BoolQ alone gives 1.78562 while the best eight-benchmark subset gives 1.78616, two different
subsets landing four ten-thousandths apart. Both are correct. Table 1 was recomputed end to end, and all
six effective counts follow from their own inflation figures.

Honest ranking after scan 21. 6.7 with acceptance near 0.65, unchanged. Defect 1 removes a sentence a
referee would have attacked, which protects the rating rather than raising it, and defect 2 is cosmetic.
The corpus work produced one repair and one documented refusal, and the refusal is the more useful result,
because it establishes that the remaining distance from the corpus is a house style choice and a
consequence of writing dense quantitative prose rather than an artefact worth editing away.

## Scan 22. Reading the results and discussion pages, and paying for the additions

Review of scan 21. The BoolQ sentence now states what was measured, and the band and mirror tests are
named at the paragraph boundary that separated them from their antecedents. Both render.

This scan read main-text pages 5, 7 and 9, which carry the results, the external panels and the whole
discussion, and checked every figure, table and interval on them against storage.

Defect 1, an interval quoted without naming its construction. The discussion said the 1B margin estimate
has a log-scale interval of 0.811 to 1.628 that includes one. Appendix C gives three constructions for
that cell, and 0.811 to 1.628 is the narrowest of them, from the cluster-robust statistic rather than the
wild bootstrap the paper uses everywhere else. Quoting the narrowest without saying so understates a
limitation the paper is otherwise candid about, and a referee checking Table 9, which shows an undefined
lower endpoint for the same cell, would not be able to reconcile the two. The sentence now names the
construction and says a wild-bootstrap interval is wider.

Defect 2, two incomparable objects joined by a vague verb. The permutation results read that the accuracy
tail fractions of 0.028 and 0.021 both differ from the primary cluster interval, which contains one. A
tail fraction and an interval cannot differ from one another. The sentence now says both reach one in
twenty while the cluster interval contains one, so the two procedures disagree on accuracy, which is the
disagreement the paper is being honest about and was burying in a weak verb.

Paying for it. The two repairs and the scan-21 repair pushed the main text to ten pages. Four
compressions brought it back to nine, none of which dropped a number or a qualifier. The phrase paired
benchmark scores from replicate runs appeared twice within three sentences of the introduction and the
second was folded away. A sentence in the results restated its own previous clause, saying values are
conditional on the measurement model one sentence after saying under the stated measurement model. A
topic sentence in the discussion announced a finding its next two sentences demonstrate. A repeated unit
name in adjacent sentences became the same units. The rendered page was re-read afterwards to confirm
that every qualifier survived, which is the check scan 9 failed twice and scan 13 had to repair.

Non-defects verified by arithmetic. Table 1 recomputes end to end, since all six effective counts equal
ten over the square of their own inflation figures to the digit printed. The accuracy upper endpoint of
1.157 maps to 0.0376 and 7.470. Figure 1's grey cells match the text, at one undefined margin variance for
WinoGrande and two accuracy variances for PIQA and WinoGrande, giving the nine and eight traits its legend
reports. The PolyPythias excess ratio of 1.66 and inflation ratio of 1.13 both follow from 1.406 and 1.244.
The BoolQ-removal figures reproduce exactly from the composition artefact at 1.78562 and 1.55783 with
intervals to the last digit printed.

Honest ranking after scan 22. 6.7 with acceptance near 0.65, unchanged. Both defects were in the two
sections a referee reads hardest, and the first was a quiet understatement of a limitation, which is the
kind of thing that costs credibility when found rather than points when fixed. The rating does not move
because nothing about the evidence moved. The paper is now at the point where each scan returns
presentation defects rather than substance defects, which is the signal that the scanning has reached its
floor rather than that the paper has reached its ceiling.

## Humanizer and slop-prevention pass, second run, after scans 21 and 22

The first humanizer pass ran after scan 20. Scans 21 and 22 then changed prose, so the pass was run again
against the current build, because a last step that runs before the last change is not a last step.

Detectors, all clean on the three prose files. Zero em dashes, zero en dashes, zero curly quotes, zero
non-ASCII codepoints of any kind, zero prose colons, zero prose semicolons, zero rhetorical questions,
zero negative parallelisms, zero contrast crutches, zero hedge stacks, and zero banned vocabulary. Fifty
detector hits in references.tex are page ranges, volume-and-page pairs, and colons inside the published
titles of cited papers, none of which is prose and none of which may be altered. One In conclusion hit
resolved to the phrase margin conclusion. Paragraph structure held from the first pass, with 177 appendix
paragraphs running one to thirteen sentences and a longest paragraph of 2,255 characters against 32,909
before the split. The pseudo-cleft count stayed at the three that were deliberately kept.

Defect this pass found, a rhythm regression I caused. Scan 22 paid for its additions by removing four
redundancies, and three of those were short sentences, which lifted the main text's median sentence length
from 20.0 to 20.5 against a corpus ceiling of 20.0. The paper had left the human range on a measure it was
inside before, and the cause was my own compression rather than anything in the original draft. Three
main-text sentences of 63, 51 and 51 words were split at clause boundaries where each carried two
independent claims. The median returned to 20.0, the standard deviation moved from 12.3 to 11.9 against a
corpus median of 12.4, and the main text held at nine pages. The three splits improve the sentences on
their own terms, since none of them needed to be one sentence.

Final corpus position. Fourteen of the sixteen style metrics sit inside the range of all 23 human papers.
The two that do not are the colon count, at 3.85 against a floor of 5.93, which is the house rule, and the
hedge count, at 0.92 against a floor of 1.00, which scan 21 examined claim by claim and declined to patch
because the only genuinely unhedged inference was an overclaim that was removed rather than softened.

Honest ranking after the second humanizer pass. 6.7 with acceptance near 0.65, unchanged. The pass found
one defect and it was one I had introduced an hour earlier, which is the argument for running the pass
after the last change rather than merely last in the plan. Nothing here moves a rating.

## Scan 23. Twenty reviewer objections, tested one at a time against what the paper actually says

Skills initiated for this scan. The full installed inventory was enumerated, at 524 skills across the
user directory and every plugin cache. Most are irrelevant to a manuscript, covering trading, Kubernetes,
Slack, IoT and Airflow. Four that had not yet run and do bear on this work were applied. From
superpowers, verification-before-completion supplied the rule that no completion claim is made without a
verification command run in the same message, and it earned its place below. From engineering-advanced,
grill-me supplied the structure of this scan, which is its interview discipline turned on the paper
rather than on a person, one objection at a time, each resolved by reading the artefacts rather than by
asserting. Also from engineering-advanced, self-eval supplied the two-axis scoring and the mandatory
devil's advocate that produced the ranking revision at the end. The pii-detect skill's MCP backend is
unauthenticated in this session, so its check was run directly instead, and it returns nothing.

Review of scan 22 and the second humanizer pass. The three sentence splits, the four compressions, the
named interval construction and the explicit permutation disagreement all render. The main text holds nine
pages.

The twenty sub-scans. Each is one objection a referee raises, tested by searching all three sources for
the paper's answer and reading what came back rather than counting matches. In order, they are that the
estimator is a renamed reliability coefficient, that cross-half independence is assumed rather than
tested, that one release cannot generalise, that three runs cannot support a covariance estimate, that
BoolQ drives every number, that the accuracy interval includes one so there is no accuracy result, that
recipe clustering is the choice that flatters the authors, that nothing was preregistered, that checkpoint
selection is a confound, that the gain mechanism is unidentified, that a square root of a ratio of sums is
biased, that 25 clusters are too few, that item-level leakage inflates the estimate, that provenance from
gated weights is unverifiable, that the PolyPythias transfer contradicts the DataDecide numbers, that the
practical rule is not validated out of sample, that the effective count is a rescaling of the inflation
factor, that the main text cannot stand without 44 pages of appendix, that a negative eigenvalue
invalidates the spectrum, and that the contribution is one number.

Eighteen are answered, most of them in the main text and all of them somewhere. Two returned no main-text
match on the first probe and were examined directly.

The first, estimator bias, is not a gap. The first probe searched for the wrong phrases. The main text
already says that unbiased estimates of the two sums do not make their ratio or square root unbiased,
that the transformations can introduce bias, and that measured bias runs downward, so it understates
rather than manufactures an accuracy excess. Adding a sentence would have duplicated an answer the paper
already gives, and the verification rule is what stopped it, because the claim that the main text was
silent did not survive being checked.

The second, run-count adequacy, is a real gap and is now fixed. The main text described three runs as a
fact of the design and never said whether three suffice. A referee looking at two degrees of freedom per
configuration asks that immediately. Section 2.3 now reports that coverage holds between 0.942 and 0.952
as the runs per configuration move from two to ten, so the three the release ships are not the binding
constraint. Both endpoints were verified against snap-r6-run-count-cov, whose five cells give 0.9423,
0.9513, 0.9467, 0.9493 and 0.9515. The addition fits inside nine pages with no compression.

Verification, run fresh in the same pass. Main text nine pages, 53 total, official style byte-identical,
zero unresolved references, zero unresolved citations, zero overfull boxes, zero short-sentence
violations, zero slop-detector hits, zero non-ASCII codepoints, empty PDF Author field, six checksums
matching.

Honest ranking after scan 23, revised downward. 6.4 with acceptance near 0.58, down from 6.7 and 0.65.
This is not a response to a new defect. It is the devil's advocate that self-eval requires, and the prompt
for it is that the last five entries in this log all read 6.6 or 6.7, which is the score clustering the
skill exists to catch. Arguing the high side, the paper measures a quantity nobody has measured, discloses
its exploratory status in its own abstract, reports its failed diagnostics as failures, and ships an
operational correction that moves a false declaration rate from 0.113 to 0.051. Arguing the low side, it
is one release of models from 150M to 1B, its accuracy conclusion is null, one benchmark carries 68
percent of the margin trace so composition sensitivity is the story a hostile referee tells, nothing was
preregistered by the authors' own statement, and the thing that transfers is a procedure rather than the
number, which is a weaker claim than the abstract's framing suggests. Resolving the two, the rigour is
genuinely top-decile and the scope is genuinely narrow, and ICLR scoring weights novelty and generality
more heavily than care. A paper with this profile draws scores around six with real variance, not a
comfortable accept. The earlier 6.7 was defensible on craft and optimistic on how referees actually
weight a careful null on small models. Twenty-three scans have not changed that, because no scan can, and
saying so is the point.

## Scan 24. A style corpus collected in this session, and imitation driven by it

Permission. Fetching papers is a bulk network download, and the standing rule is to ask before any
download or compute, so this scan began by asking. The user approved fetching about 25 papers as plain
text and chose style imitation as the focus for the remaining work. Nothing was run before that answer.

The corpus, collected now rather than inherited. All 23 papers from the earlier study were re-fetched
from arXiv by identifier, at 332,000 words. Eleven more were then added by taking the arXiv identifiers
out of this paper's own bibliography, on the reasoning that a submission's related work is by
construction venue-matched and human-written. Four of those eleven are the ones that failed to fetch in
the earlier session, which are The Benchmark Lottery, DataDecide, PolyPythias and Signal and Noise, and
the rest are metabench, Adding Error Bars to Evals, Fluid Benchmarking, OLMo 2 Furious, Fine-Tuning
Pretrained Language Models, and the random-seed macro and micro effects paper. One duplicate was removed
after the first analysis showed two filenames with identical statistics. The corpus is 33 papers and 2.9
MB of text on disk, and analyze.py now runs end to end against it instead of against a stored table.

What the larger corpus changed. Measured against 33 papers rather than 23, the draft now sits inside the
range of every one of them on 21 of 22 metrics. The single exception is the colon count, at 3.82 against
a floor of 5.93, which is the house rule and stays. Two metrics that were outside the old corpus are now
inside, and both vindicate earlier refusals. Median sentence length sits at 20.5 against a new ceiling of
22, because metabench and Adding Error Bars are long-sentence papers. More usefully, the hedge count of
0.91 is no longer below the floor, because DataDecide hedges at 0.64, and DataDecide is the release this
paper analyses. Scan 21 declined to sprinkle may and might to clear a floor of 1.00 and instead removed an
overclaim. A wider sample of the genre says that refusal was right, and that the floor was an artefact of
which 23 papers happened to be in the study.

Defect, subject-first monotony. The measurement table does not capture sentence openers, so they were
mined directly. Across 8,846 prose sentences in the 33 papers, with bibliographies cut so that reference
lines do not pose as sentences, the corpus opens 6.0 percent of sentences with The and 24.2 percent with a
fronted circumstance such as In, For, To, As, While or Since. The draft opened 18.7 percent with The and
17.1 percent with a fronted circumstance. Nearly three times the corpus rate of definite-article openers
is real monotony and is the kind of thing that reads as mechanical even when every individual sentence is
sound. Nine sentences were rewritten to front a circumstantial phrase that the sentence already contained,
which is length-neutral, so the main text held nine pages with no compression. Examples are that the
largest checkpoint step sentence now opens In each configuration, the permutation shortfall now opens
Across those ten runs, and the gain simulation now opens At a gain standard deviation of 0.05. The rate
moved from 18.7 to 15.0 percent and the fronted rate from 17.1 to 18.3.

Measured and declined, again. Closing the remaining distance to 6.0 percent would take roughly
twenty-five more rewrites, and the sentences that remain are ones where the definite article is carrying
the sentence, including the short verdicts that give the prose its rhythm, such as that the denominator
falls by more and that the shortfall is not simulation noise. The residual gap is also partly genre. The
corpus contains motivation-heavy papers whose subjects are people and ideas, while this is a
results-dense paper whose subjects are named quantities, so The margin interval and The accuracy estimate
are the natural subjects of most of its sentences. Nine natural conversions were worth making and
twenty-five contorted ones would not be. This is the same judgement as the hedge decision and it is
recorded for the same reason, which is that a metric moved toward a target is not evidence unless the
sentences got better.

Humanizer and slop suite, run after the last prose change. Zero slop-detector hits and zero non-ASCII
codepoints across the three prose files. Nine pages, 53 total, official style byte-identical, zero
unresolved references, zero short-sentence violations, six checksums matching.

Honest ranking after scan 24. 6.4 with acceptance near 0.58, unchanged from scan 23. The opener work
makes the paper read less mechanically and removes one detectable signature, and a corpus of 33 rather
than 23 raises confidence that the prose now sits inside the human range. Neither changes what a referee
scores, which is the design, the evidence and the scope. The downward revision in scan 23 stands, and
nothing in this scan argues against it.

## Scan 25, 2026-09-16. Live corpus discovery, and an abstract that contradicted its own section

Compute was withheld for this scan. The user answered "dont run any compute" to a direct
question that listed shell and Python over repo files, pdflatex rebuilds, style metrics and
page rendering, so none of those ran. What follows is therefore built from reading files,
from searching online, and from arithmetic done by hand, and every claim below carries the
label its evidence supports. Two consequences matter. Every edit had to be length neutral,
because a page count cannot be checked without a build. And the shipped PDF is now one
revision behind the source, which is stated again at the end rather than buried.

### Review of what scan 24 changed

Scan 24 rewrote nine sentence openers to move the draft from 18.7 percent "The" openers to
15.0 percent, against a corpus figure of 6.0 percent, and it left roughly twenty-five
further rewrites on the table. Reading the twenty newly discovered papers closes that
question against the earlier target. Counting the opening sentence of each of the twenty
abstracts by hand gives three that begin with "The", which is 15 percent, sitting exactly
where the draft now sits. The two measurements do not conflict, because a full body carries
related work and motivation where the subject is often a person or a community, while an
abstract and a results section carry named quantities as subjects and therefore take the
article. This manuscript is results-dense from the abstract to the discussion. So the 6.0
percent target was wrong for this paper, the nine rewrites happened to land in the right
place, and the further twenty-five would have pushed the prose out of its genre. The
decision to stop is now closed on evidence instead of on judgement, which is the better
reason. Recorded in research/style_study/discovered_2026-09-16.md.

### Sub-scans

1. Review of scan 24's opener rewrites against new evidence. Closed as above, no change.
2. Live venue search for papers outside both known lists. Twenty found and recorded.
3. Abstract against Results for every shared number. One defect, below.
4. Introduction against body for every shared number. Clean.
5. Interval endpoints against Table 1. Clean, all six rows.
6. Effective-count arithmetic. Recomputed all six K_eff entries by hand from K over Lambda
   squared. All six correct to the printed precision.
7. The accuracy upper endpoint mapping. 1.157 gives an effective coefficient of 0.0376 and
   an effective count of 7.470, matching the printed 0.038 and 7.47.
8. The resolution ratio at p equals 0.35. Recomputed as 0.2275 over 0.1372, which is 1.658,
   matching the printed 1.66, and the stated minimum of pi over two is the value at p equals
   one half. Both correct.
9. The BoolQ off-diagonal sums. Reconstructed from the full and reduced factors and the
   stated trace shares. Margins give minus 0.153 of the trace against a printed minus 0.15,
   accuracy gives minus 0.066 against a printed minus 0.06. Both correct.
10. The sign-reversal probabilities. All four recomputed from the printed aggregate
    deviation and the independence value. 0.246, 0.085, 0.229 and 0.069 all reproduce.
11. The enumeration count. 25 choose 17 is 1,081,575 as printed.
12. Truncation percentages for internal consistency. An average of 87 percent with a range
    of 39 to 89 at 530M is only possible if one configuration is severely truncated, which
    is exactly what the same paragraph states. Consistent.
13. The repository-credentials claim. The recheck record observes 80 refusing unauthenticated
    requests, 40 resolving anonymously and 5 invalid identifiers, summing to 125. The
    manuscript's "80 of the 125" is OBSERVED and correct. The earlier worry recorded in the
    R7 design note, that the count measured something other than credentials, was settled by
    that recheck and needs no further action.
14. PolyPythias figures against stored records. 1.406 and 1.711 appear nowhere in
    research/outputs, only in the manuscript and this log. The paper already discloses that
    these come from earlier execution records this revision did not rerun, so the disclosure
    matches the evidence. Logged as a reviewer risk, not a defect.
15. Reviewer-objection pass over ten standing objections. Every one is already answered in
    the text, including format confounding, the twenty-five-cluster inference, the missing
    holdout, and the circularity of the local scale correction.
16. Non-ASCII, em dash, en dash and curly quote scan on all three tex files. Zero hits.
17. Banned-vocabulary scan. One "robust" in main.tex, inside "cluster-robust", which is a
    named estimator class. Six "leverage" in the appendices, all the hat-matrix quantity in
    the CR3 correction. Both technical, neither is slop, no change.
18. Prose semicolon and colon scan. Zero, as the house rule requires.
19. Genre fit on the habit that most separates this literature from promotional writing,
    which is stating the loss in the same sentence as the win. The manuscript does this in
    both interval sentences and in the discussion's opening. Worth protecting in any future
    compression.
20. Rhythm. Unverified this scan. The only edits were single digits, so the sentence-length
    distribution is unchanged from the state scan 24 measured, and no new measurement was
    permitted.

### The defect

The abstract said simulated coverage "lies between 0.933 and 0.953 across twelve
populations". Section 2.3 reports two repeats at 10,000 replicates, the first covering 0.933
to 0.953 and the second 0.929 to 0.950. So the abstract quoted the floor of the better of
two repeats as though it were the floor of both, and a referee who read Section 2.3 would
find the abstract contradicted two lines later by the paper's own second run. Changed to
0.929 in the abstract and in the same claim in the introduction. Both replacements are one
character for one character, so no line can reflow and the page count cannot have moved.

This is the second wrong figure found in twenty-five scans, and like the first it was found
by reading two adjacent sentences against each other rather than by checking either against
storage. Selective quoting of the friendlier of two repeats is the failure mode to watch,
because nothing about it looks like an error in isolation.

### What the twenty new papers say about the house rules

Colons and dashes are used freely across all twenty, and several sentences turn on them.
The house ban therefore keeps this manuscript outside its genre on exactly one axis, which
is what the 33-paper measurement already reported. The rule is the user's and it stands, and
the honest statement is that the paper pays a small readability cost rather than that the
cost is zero. Three of the twenty state a claim by denying its opposite, so a negation that
carries its own evidence is ordinary here and need not be avoided. Rule-of-three groupings
are everywhere, including in a title. Unrounded counts are the norm, and the manuscript's
37,682 items and 4,999 draws sit in the same register.

### Humanizer and slop suite

Run after the last prose change, as the goal requires. Zero non-ASCII codepoints, zero em or
en dashes, zero curly quotes, zero prose semicolons or colons, and no banned vocabulary once
the two technical terms are excluded. The rhythm half of the suite could not run without
compute, and since the only changes were two digits, the last measured rhythm still applies.

### Build state, stated plainly

The source now differs from deliverables/SNAP_revised_draft.pdf by two digits. No rebuild was
permitted, so the PDF, the snapshot copies and SHA256SUMS.txt are all one revision stale. The
last verified build state, from scan 24, was 9 main-text pages, 53 total, official style file
unchanged, no unresolved reference labels, no short sentences and an empty PDF Author field.
Nothing in this scan can change the page count, because both edits swap one character for
another inside an existing number. A rebuild is still required before submission, and until
it runs the page count for this exact source is INFERRED rather than OBSERVED.

### Honest ranking after scan 25

6.4, acceptance near 0.58, unchanged. Fixing an abstract that contradicted its own section
removes a cheap shot a referee could take, and closing the opener question on real evidence
stops a change that would have made the prose worse. Neither touches what actually gets
scored, which is a design with no holdout, a headline margin result confounded with scoring
format, and an accuracy result whose interval contains one on the full battery. The downward
revision made in scan 23 stands, and this scan gives no reason to move it in either
direction.

## Scan 26, 2026-09-16. Prior-year proceedings, and the first sentence of the paper

Compute remains withheld, so this scan is again reading, searching and hand arithmetic, and
every edit is length neutral by construction.

### Review of what scan 25 changed

Scan 25 changed two digits, taking the abstract and introduction from a coverage floor of
0.933 to 0.929 so that the abstract stops contradicting Section 2.3's second repeat. Read
back in context, both sentences still parse, both still carry the same clause structure, and
neither can have reflowed because each swaps one character for another. Scan 25 also
cancelled the twenty-five further opener rewrites it had been holding. Nothing in this scan
argues for reinstating them.

### Why this scan happened at all

Scan 25's twenty discovered papers were all from 2025 and 2026. The goal asked for papers
from prior years of this conference or related conferences, and recent arXiv postings do not
satisfy that, both because they are not prior-year proceedings and because papers written
after 2023 cannot be assumed free of machine assistance. That was a real gap and this scan
closes it with twenty-one papers dated 2015 to 2022, including two ACL Anthology proceedings
pages with no arXiv version, which is the literal form the goal asked for. Every arXiv
identifier was confirmed by fetching the page and matching the returned title rather than
recalled from memory. Recorded in research/style_study/prior_years_2026-09-16.md.

### Sub-scans

1. Review of scan 25's two digit edits in context. Both read correctly, no reflow possible.
2. Prior-year proceedings discovery. Twenty-one papers, 2015 to 2022, none in any earlier
   list.
3. Identifier verification. Each arXiv abstract page fetched and its title matched against
   the intended paper. No identifier guessed, none discarded.
4. Abstract opening sentence against the genre, now across fifty-four papers from three
   independently assembled sets. One finding, below.
5. Antecedent check after the rewrite. The next sentence opens "We study this covariance",
   and the new first sentence now ends on "the covariance between scores", so the antecedent
   is adjacent rather than four words upstream. Better than before.
6. Truth check on the new claim. "often given a run-to-run uncertainty from marginal
   variances alone, which omits the covariance between scores" is a weaker statement than
   the paper's own related work, which says that among the studies located, none estimates
   the covariance of run noise between benchmarks. Supported, and deliberately understated.
7. Length arithmetic. Old sentence 132 characters, new one 133. One character longer, so a
   line cannot break differently in any realistic justification.
8. Does the abstract still state the estimand. Yes, in the same sentence, as the thing that
   is omitted rather than as the thing that is required.
9. Overclaim check on the new sentence. "often" is a frequency claim about practice, chosen
   over "usually" precisely because the paper's evidence bounds the literature it located
   rather than the field.
10. Hedge count. No hedge added, none removed.
11. Sentence floor. Eighteen words, well clear of any floor, and not a fragment.
12. Terminology consistency. The body says "marginal standard deviations" where the abstract
    says "marginal variances". Same information on two scales, and the abstract used the
    variance form before this edit, so nothing changed.
13. Non-ASCII scan on all three tex files. Zero in each.
14. Em dash, en dash and curly quote scan on all three. Zero in each.
15. Prose semicolon and colon scan. Zero.
16. Contrast crutch, rhetorical setup and summary opener scan. One hit for "in conclusion",
    which turned out to be the substring inside "the margin conclusion holds". False
    positive, no change.
17. Banned vocabulary re-check after the edit. Unchanged from scan 25, one "cluster-robust"
    and six hat-matrix "leverage", both technical.
18. Candour inventory. The manuscript's plainest admissions, that the screening split was
    never drawn and that the shipped proxy carries no measurable signal about a run, match
    the register of Li and Talwalkar on missing source material and Ferrari Dacrema on seven
    of eighteen reproducing. Flagged as protected in any future compression.
19. Enumeration style. Inline (i), (ii), (iii) lists are common in the prior-year set and
    absent here. Logged as a difference rather than a defect, because converting prose to
    enumerations costs length that cannot be checked without a build.
20. Build state. Unchanged from scan 25 and restated below.

### The change

Not one of the fifty-four papers across the three sets opens its abstract by saying what a
quantity is or what estimating it requires. They open by naming what the field does now and
where that falls short. Blum and Hardt open on participants overfitting a leaderboard.
Gorman and Bedrick open on standard practice and what few researchers do. Bowman and Dahl
open with the flat sentence that evaluation is broken. Schmidt opens on decisions made from
anecdotes. The 2026 set does the same, so the habit holds across eleven years and is not an
artefact of one cohort.

This paper opened on a requirement. It now opens on the practice and its omission, at a cost
of one character. The first sentence of an abstract is the sentence that decides whether a
referee believes the paper is about anything, which makes this the highest-leverage
single-sentence change available, and it is the only edit this scan makes.

### Humanizer and slop suite

Re-run after the last prose change, which was the abstract rewrite above. Zero non-ASCII
codepoints, zero em or en dashes, zero curly quotes, zero prose semicolons or colons, no
banned vocabulary once the two technical terms are excluded, and no contrast crutch, no
rhetorical setup and no summary opener. The rhythm half of the suite still cannot run
without compute. The only prose change since the last full rhythm measurement is one
eighteen-word sentence replacing an eighteen-word sentence, so that measurement still holds.

### Build state

The source now differs from deliverables/SNAP_revised_draft.pdf by two digits and one
sentence. No rebuild has been permitted, so the PDF, the snapshot copies and SHA256SUMS.txt
are stale. The last verified build, from scan 24, was 9 main-text pages and 53 total, style
file unchanged, no unresolved labels, no short sentences, empty PDF Author field. The page
count for this exact source is INFERRED from the fact that every edit since is length
neutral to within one character, not OBSERVED. A rebuild is required before submission and is
the one outstanding item on this paper.

### Honest ranking after scan 26

6.4, acceptance near 0.58, unchanged. The new first sentence should make a referee more
likely to keep reading, and fifty-four papers agree on the pattern it now follows, but a
better opening sentence does not change a design with no holdout, a headline margin result
confounded with scoring format, or an accuracy interval that contains one on the full
battery. Claiming a ranking move for a framing change would be exactly the inflation the
goal forbids. The scan 23 revision stands.
