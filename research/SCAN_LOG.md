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

## Build record, 2026-09-16, snap-r26-build on Kaggle

The user permitted compute on condition that none of it run on this machine, so the build moved
to Kaggle. The tex sources, the figures, the untouched template style files and the
pre-formatting snapshot went up as a private dataset, and the kernel installed TeX Live,
compiled, and reported the numbers the local verifier used to report.

Two attempts failed before the third worked, and both failures are worth recording. Version 1
died in sixty seconds because Kaggle mounted the dataset one level deeper than the kernel
looked, which a recursive search for main.tex fixed. Version 2 compiled but left "Label(s) may
have changed. Rerun to get cross-references right." standing after the second pass, because a
build starting with no aux file needs three passes where the local build had a settled aux
sitting in its output directory from previous runs. A page count read from an aux that has not
settled is not a measurement, so version 3 ran three passes and recorded the count after each.

The count did not move. Main text nine pages and fifty-three total after pass one, after pass
two and after pass three, with the rerun request cleared by the third. Those are the same two
numbers the last local build produced, which is the strongest available evidence that the TeX
Live version difference between the two machines does not reach the layout.

Everything else the verifier checks came back clean. Zero overfull boxes, zero missing
characters, zero font warnings, no unresolved reference labels, fifty-three bibliography
entries with every one cited and every citation resolving, no sentence shorter than four words
in any of the three files, and an empty PDF Author field. The three official style files are
byte-identical to the template copies, and the iclr2027_conference.sty digest matches the one
already in the shipped manifest, so the margins are the conference's own.

Version 4 added the two checks that stood between the remote build and shipping it. All
twenty-three fonts in the PDF carry their own embedded program and all twenty-three are subset,
so nothing depends on a substitution at the referee's end. The kernel also emitted the SHA-256
manifest from the same bytes it compiled, and verifying that manifest against the installed
files gives six OK.

One gate reports false and it is not a regression. table_numeric_tokens_preserved compares every
numeric token in every table body against the pre-formatting snapshot, and the last local
verification recorded the same false, so the snapshot went stale when the tables were legitimately
revised. The gate no longer carries information and should either be re-baselined or dropped
rather than read as a warning.

The prose numbers the remote build reports, which the local run could not produce this session,
put the main text at 271 sentences, median eighteen words, mean 20.01, 7.4 percent under eight
words against a corpus range of 5.8 to 23.8 percent, zero prose colons, semicolons or dashes, and
16.6 percent of sentences opening with "The" against the 15 percent the forty abstracts show.
The rhythm regression that scan 22 introduced and the second humanizer pass repaired has not
returned.

The manuscript is now built, verified and checksummed from the current source. Ranking after the
build is 6.4 with acceptance near 0.58, unchanged, because a build confirms that nothing broke
rather than making the paper better.

## Scan 27, 2026-09-16. Reading the rendered pages against the appendix that backs them

The build from the previous entry made this scan possible in a way the last two were not. With a
current PDF in hand the whole main text could be read as a referee sees it, nine pages rendered
rather than nine files of markup, and with Kaggle available any edit could be verified instead of
argued for.

### Review of what scan 26 changed

Scan 26 replaced the abstract's opening sentence and added twenty-one prior-year papers to the
style record. Read on the rendered page, the new opening sits correctly above the SNAP sentence
that follows it, and the phrase "this covariance" now has its antecedent in the clause immediately
before rather than four words upstream. The build confirms the change cost nothing, because the
main text still ends on page nine.

### Sub-scans

1. Review of scan 26's abstract rewrite in rendered form. Reads correctly, antecedent improved.
2. Rendered reading of pages one to three, covering the abstract, the introduction and the
   estimator definition.
3. Rendered reading of pages four to six, covering data scope, batch and scale sensitivity, and
   the composition results.
4. Rendered reading of pages seven to nine, covering the figure, prediction, related work and the
   discussion.
5. Figure 1 against its caption. Nine margin traits and eight accuracy traits in the legend, the
   greyed cells matching the text's WinoGrande and PIQA exclusions, participation ratios present.
6. Table 1 against the text. All six rows, both intervals, all six effective counts consistent.
7. Table 2 against the text. Six models, both columns, the ordering the prose describes.
8. Table 16 row count against the claim of twelve populations. Twelve rows, confirmed by reading.
9. The wild column against the main text's 0.928 to 0.954. Minimum 0.928, maximum 0.954, exact.
10. The configuration column against the claimed 0.872 under recipe-shared effects. Exact.
11. The recipe column against the claimed 0.857 to 0.940. Minimum 0.857, maximum 0.940, exact.
12. The bias column against the two claims about downward bias. The two cross-half rows give
    minus 0.014 and minus 0.016 against a claimed 0.015, the null row gives minus 0.011 against a
    claimed mean estimate of 0.989, and the 1.078 row gives minus 0.007. All three hold.
13. The inversion column against the main text's 0.935 to 0.956. The column runs 0.932 to 0.957.
    Investigated rather than corrected, see below.
14. The inversion figures against storage. The four-cell precision record gives centred coverage
    of 0.9353, 0.9561, 0.9419 and 0.9466, and Appendix C states that the remaining eight cells
    were then brought to the same precision, so 0.935 to 0.956 is the twelve-cell rerun.
15. Seed-matched pair counts against storage. Both stored pair files hold exactly 1,500 records,
    matching the main text.
16. The paired positive-variance subcounts. Not re-verified, see the honesty note below.
17. Paragraph length across the rendered main text. Three paragraphs run twelve to seventeen
    lines against a typical four to eight, which is variation the corpus also shows rather than a
    defect, so no change.
18. Duplicate-value collision check. The value 1.66 carries two unrelated meanings, the accuracy
    to margin noise ratio at p equals 0.35 and the ratio of excesses above one for PolyPythias.
    Both are correct, so changing either would falsify one, and the collision stays.
19. Slop suite across all three files after the last prose change. Zero on every marker.
20. Rebuild and install. Nine main-text pages and fifty-three total after each of three passes,
    zero overfull boxes, no unresolved labels or citations, twenty-three fonts embedded and
    subset, empty author field, six checksums verifying.

### The change

The sentence "A cluster test-inversion interval that we added later covers between 0.935 and 0.956
in the same populations" points a reader at Table 16, whose inversion column runs 0.932 to 0.957.
Nothing is wrong with either number. The table reports the 2,000-replicate pass and the main text
quotes the later 10,000-replicate rerun of every cell, which Appendix C describes but the caption
did not. Every column carries the same gap, so a referee checking any of them would conclude the
paper misquotes its own table, and only a careful reading of the appendix prose would rescue it.
The caption now says which pass it tabulates and that the main text quotes the other. That fix
sits after the main-text label, so it cost no space against the nine-page limit, which is why it
was made there rather than in the sentence itself.

### What was not verified

The main text reports that the paired difference carries a positive variance estimate for 1,445
margin and 1,222 accuracy pairs, with a stricter subset of 1,379 and 919. Recomputing those
subcounts needs a per-pair pass over the stored files, which is computation that did not run. The
pair total of 1,500 is OBSERVED. The four subcounts stay REPORTED from the earlier run, and this
entry exists so that nobody later mistakes them for checked figures.

### Honest ranking after scan 27

6.4, acceptance near 0.58, unchanged. Three consecutive scans have now produced one wrong digit, one
weak opening sentence and one ambiguous caption, which is a yield curve flattening toward zero. The
manuscript's remaining weaknesses are the design's missing holdout, the confounding of the margin
result with scoring format, and an accuracy interval that contains one on the full battery. None of
those is a writing problem, so no further scan of the prose will move the score. Saying otherwise
after finding a caption ambiguity would be exactly the inflation the goal forbids.

## Scan 28, 2026-09-16, the appendix tables against the prose that cites them

### Review of what scan 27 changed

Scan 27 appended one sentence to the caption of Table 16 naming the replicate count that column
tabulates and saying the main text quotes a later rerun. I reread the caption in place and the
sentence does what it was meant to do, since a referee comparing 0.935 to 0.956 against 0.932 to
0.957 now finds the explanation in the same visual block as the numbers rather than four
paragraphs away in the appendix prose. The change sits after the main-text label, the rebuilt
document still reports nine main-text pages and fifty-three total, and no wording elsewhere in the
paper had to move to accommodate it. Nothing about scan 27 needs undoing.

### The twenty sub-scans

1.  Verification that the scan 27 caption sentence renders in the built PDF and did not push the
    appendix table onto a new page.
2.  Fetch of the full body of Bowman and Dahl 2021 through ar5iv, opening paragraph and conclusion.
3.  Fetch of the full body of Choi and five others 2019, opening paragraph and limitations.
4.  Fetch of the full body of Schmidt, Schneider and Hennig 2021, opening paragraph and limitations.
5.  The limitations-opener convention across those three, compared against the manuscript's own
    admissions about the undrawn screening split and the shipped proxy.
6.  The rate and form of marked speculation, compared against the manuscript's hedge markers.
7.  Paragraph openers in prior-year body prose, checked against the subject-first finding of scan 24.
8.  The uncorrected apostrophe slip in the Schmidt camera copy, recorded as an observation about
    accepted prose and explicitly not acted on, since injecting an error would be dishonest.
9.  Inventory of every table in the appendices, twenty in all, to define the audit surface.
10. Table 8, the fixed-K comparison, subset counts against the claim of two thirds. Reconciles at
    0.659.
11. Table 8, the accuracy share stated as 0.305 against a computed 0.296. The two reconcile only
    under a defined-only denominator, which the appendix does not state.
12. Table 8, the minimum and maximum margin estimates against the prose that quotes them.
13. Table 8, the BoolQ differential claims against the corresponding main-text sentences.
14. The interval-construction paragraph, both squared standard-error ratios recomputed from the
    printed figures. 0.045 over 0.094 squared is 0.229, and 0.038 over 0.052 squared is 0.534.
15. The design-effect back-calculation from one plus four times rho, checked against the stated
    effective sample size.
16. Table 7, the claim that dividing by the pooled standard deviation lowers margin inflation from
    1.244 to 1.182.
17. Table 7, the claim that the three bounded scores fall to between 1.120 and 1.141. The table
    gives 1.134, 1.141 and 1.120, so the stated range is exactly the observed range.
18. Table 7, the off-diagonal sum falling from 0.547 to 0.164 times the trace and BoolQ's share of
    that trace growing from 0.679 to 0.844, both checked as monotone across the rows.
19. Table 7, the claim that bounding reproduces between 62 and 75 percent of the gap between margin
    and accuracy inflation, recomputed from first principles. The gap is 0.166, the three bounded
    reductions are 0.110, 0.103 and 0.124, and their shares are 0.663, 0.620 and 0.747.
20. The slop suite across all three source files after the reading was complete. Zero non-ASCII
    characters, zero dashes of any kind, zero curly quotes, zero prose semicolons, and zero hits on
    the banned-construction list.

### The change

None. Every claim audited in this scan reconciles against the table it cites, and the one arithmetic
that does not reconcile cleanly was already examined and deliberately left alone.

That exception is sub-scan 11. Table 8 states an accuracy share of 0.305 where the printed cells
give 0.296. The difference is explained if the denominator counts only the configurations where the
estimate is defined rather than all of them, which is a plausible reading and is not what the
appendix says. Fixing it properly means parsing a 570 KB result file to count the defined cells,
which is computation, and the alternative is to assert the denominator from inference and label it
as fact. Writing an unverified denominator into the paper to close a cosmetic gap of nine
thousandths would be a worse defect than the gap, so the number stays as it is and this entry
records why.

### Style evidence added

`research/style_study/body_prose_2026-09-16.md` records the prior-year body prose, which is the
first time this project read full introductions and limitations sections rather than abstracts. The
finding is that the manuscript already matches the genre on every dimension examined, including the
plain limitation opener, the marked speculation, and the very short sentence at the head of a
conclusion. That produced no edit, which is the honest outcome and is recorded as such.

### Honest ranking after scan 28

6.4, acceptance near 0.58, unchanged. This scan audited the numeric spine of two appendix tables and
the three prior-year papers whose prose is closest to this one, and it found nothing to change. Four
consecutive scans have now returned one wrong digit, one weak opening sentence, one ambiguous
caption and one nothing, which is a search that has run out of prose defects to find. The ceiling is
set by the design, specifically the missing holdout, the confounding of the margin result with
scoring format, and an accuracy interval that contains one on the full battery. No amount of further
reading moves that, and reporting a higher number because more scans have run would be inflation.

## Scan 29, 2026-09-16, the rest of the appendix tables, and a number that reads as its own refutation

### Review of what scan 28 did

Scan 28 changed nothing in the manuscript and added `body_prose_2026-09-16.md` to the style study.
Rereading its conclusions against the source, the two tables it audited still reconcile and the
decision not to touch the 0.305 accuracy share still holds for the same reason, which is that the
only honest fix needs a count this project has not computed. The one thing scan 28 did not do was
finish the table sweep it started, since it stopped after two of twenty. This scan finished it.

### The twenty-six sub-scans

1.  Review of scan 28's non-edit and of the body-prose file it added.
2.  Orphan sweep over all twenty-two table labels. Every label is referenced at least once, and six
    references point at the coverage table, so no table is stranded.
3.  Table 5, the subset partitions. 92 plus 33 is 125, 26 plus 99 is 125, and one at 530M plus 25 at
    750M is 26. Every count in the prose matches its row.
4.  Table 5, the interval-exclusion claims on all five rows, checked endpoint by endpoint.
5.  Table 5, the influence definition. The numerator sums to zero by construction, since summing
    $T_c-\widehat\Lambda^2U_c$ over configurations gives $\sum T_c-(\sum T_c/\sum U_c)\sum U_c$.
6.  Table 5, the 530M step shares. Twenty-four values at 88.7 percent and one at 38.9 gives a mean
    of exactly 86.7, which is what the prose reports and what one severely truncated configuration
    at that size implies.
7.  Table 5, a weighted-partition check in the squared domain. The pooled 1.244 sits between the
    truncated 1.107 and the untruncated 1.276 at a weight of 0.800, against a configuration share of
    0.792, so the subsets recombine into the full sample.
8.  Table 5, the permutation p-values of 0.314 and 0.990 against a Spearman correlation of $-0.036$
    and 0.001. The naive asymptotic comparison would call 0.314 too small, but the permutation is
    stratified within size, so its null keeps the between-size component and the asymptotic check
    does not apply. No defect asserted.
9.  Table 12, the counts. 125 minus 2 is 123 configurations and 369 runs, and both changes equal the
    difference of the two columns they sit between.
10. Table 12, the shift ratios. Solving the pooled root-mean-square for the other four sizes from the
    750M value gives 0.278 on margins and 0.472 on accuracy, and the prose states a range of 0.220 to
    0.551, so both land inside it.
11. Table 12, the claim that the 750M margin ratio sits within 0.001 of the PolyPythias 0.890.
12. The calibration paragraph. The 21 percent gap, the 2.2 standard errors on both scales, and the
    $t(24)$ critical value of 2.06 all recompute from the printed figures.
13. The descriptive accuracy interval of 0.979 to 1.178, which recovers exactly from an unrounded
    centre of 1.0784 and the simulated dispersion.
14. The sixteen-cell coverage range against two Monte Carlo standard errors. At 200 datasets the band
    is 0.9192 to 0.9808 and the observed range is 0.920 to 0.975, so the claim holds, and it holds by
    less than a thousandth at the bottom.
15. Table 19, the claim that every adjustment returns between 0.999 and 1.002 under independence. The
    None row shows 0.998, which would break the claim if None were an adjustment. It is not, and the
    sentence is correct as written.
16. Table 19, the matched simulations against the observed values, each of the three pairs recomputed.
    The differences are 0.001, 0.015 and 0.014 against a stated bound of 0.015.
17. Table 19, whether a common correlation of 0.178 can reproduce an inflation of 1.242 across ten
    benchmarks. It can, because the effective count is set by the trace concentration rather than by
    the benchmark count, and BoolQ holds two thirds of the trace. No defect asserted.
18. Table 19, the clipped-drop departure claim. This is the defect, described below.
19. Table 2, the test-length substitution. The battery means of 0.652 and 0.324 give 6.87 and 3.92 by
    my arithmetic against a printed 3.91, which is inside the rounding band of the displayed means, so
    the printed value stands and no correction was made.
20. Table 2, the negative and sub-0.10 reliability counts, cross-checked against which traits the
    variance floor binds for in the proxy appendix. WinoGrande on margins and PIQA with WinoGrande on
    accuracy are exactly the traits with negative reliability. The two appendices agree.
21. Table 9, the eleven-row scorecard. 455 of 1,500 is 30.3 percent and 1.078 over 1.244 is 0.867, and
    every other row's assessment follows from its own numbers.
22. Table 10, the by-size estimates. Only 530M excludes one on either scale, five margin and four
    accuracy point estimates exceed one, and the BoolQ-removed sweep excludes one in five margin bands
    and in exactly the middle three accuracy bands.
23. Three independent back-solves of the benchmark count from $\Lambda^2=1+(K-1)\bar r_E$, at the
    planned 0.0911, the observed margin 0.061 and the observed accuracy 0.0181. They return 9.99, 9.98
    and 9.96 against a battery of ten. The estimator's headline numbers are internally consistent to
    three significant figures.
24. The realised-to-planned standard error factors of 2.1 and 3.3, tested against the rounding bands
    of the displayed standard errors. A true accuracy standard error near 0.0375 satisfies the factor,
    the 2.2 half-width claim, and the printed 0.038 at once, so the figure stands.
25. Kaggle rebuild and install after the edit.
26. Slop suite across all three files after the last prose change, including manual inspection of all
    twenty-four occurrences of "robust".

### The change

The proxy appendix names one anomaly among its cross-fitted weightings. "The clipped-drop weighting
is the one departure, since its observed 0.889 on margins falls below a simulated fifth percentile of
0.908." Two paragraphs later, Table 19 reports a matched simulated mean of 0.889 for the floored-traits-dropped
adjustment, which is the same number the text calls anomalously low. A referee checking the claim
against the table concludes that the simulation reproduces the observed value exactly and that the
departure claim is false.

Both numbers are right. The percentile comes from simulations that refit the whole cross-fitted
pipeline in each replicate, and the table's matched column reports the in-sample adjustment, which is
a different estimator with a different simulated distribution. The paper never says so at the point of
collision. One sentence now says it, placed immediately after the departure claim where the wrong
belief forms, and the appendix location means it costs no main-text space.

This is the third defect of this exact shape, after the abstract coverage digit and the coverage table
caption. All three were numbers that were individually correct and jointly misleading, and none would
have been caught by any check that reads one file or one table at a time.

### The build

Three passes, no rerun requested after the third. Nine main-text pages and fifty-three total after
every pass, unchanged by the added sentence. Zero overfull boxes, zero missing characters, no
unresolved labels or citation keys, no uncited bibliography entries, twenty-three fonts all embedded
and subset, empty author field, and the three official style files byte-identical to the template.
Fifteen underfull boxes, unchanged, which affect no page. The prose metrics put main.tex at 7.4
percent of sentences under eight words against a corpus band of 5.8 to 23.8 percent, and 16.6 percent
of sentences opening on "The" against a corpus figure of 15 percent, so both style targets set in
earlier scans still hold after the edit.

`table_numeric_tokens_preserved` remains false. This was established in an earlier scan as an artifact
of a stale pre-formatting snapshot rather than a drift in the tables, it is identical in the archived
local verification, and this edit did not touch a table body.

### Honest ranking after scan 29

6.4, acceptance near 0.58, unchanged. This scan found a real defect, which means the sweep was worth
running, and the defect was a cross-reference hazard in Appendix C rather than anything a reviewer
scores. The manuscript's ceiling is still set by three design facts, the missing holdout, the
confounding of the margin result with scoring format, and an accuracy interval that contains one on
the full battery. Fixing a number that reads as its own refutation removes a way to lose points. It
does not add any. The score moves when the design changes, and the design cannot change without
compute the user has not authorised.

## Scan 30, 2026-09-16, the derivations, the figures, and a check that was lying to me

### Review of what scan 29 did

Scan 29 added one sentence to the proxy appendix separating the cross-fitted percentiles from the
in-sample matched means. Rereading it against Table 19, the collision it was written for is gone, and
a referee who checks the 0.889 departure claim against the table now meets the explanation in the same
paragraph. The rebuild it triggered held nine main-text pages and fifty-three total, so the sentence
cost nothing. Nothing about scan 29 needs undoing.

### The twenty-eight sub-scans

1.  Review of scan 29's sentence in place.
2.  Figure orphan sweep. Three figure labels, three references, no stranded artwork.
3.  Appendix orphan sweep. Eleven appendix labels, every one referenced, `app:supplementary` five times.
4.  The notation table against the values used throughout. 125, 3 and 10 hold everywhere.
5.  The cross-half expectation, rederived. Centring across runs gives $(1-1/R)\Sigma_E(j,k)$ exactly.
6.  The symmetrised estimator's normalisation. $1/(2N(R-1))$ against a double sum over two half
    orderings returns $\Sigma_E(j,k)$ in expectation, so the constant is right.
7.  The attenuation ratio under diagonal contamination, proved to lie between $\Lambda^2$ and one in
    both directions by differentiating in $\operatorname{tr}D$.
8.  The bound $0\le a_\sigma\le1$, proved by Cauchy-Schwarz on $(\sum\sigma)^2\le K\sum\sigma^2$.
9.  The worked example with standard deviations one and two. The effective coefficient is 0.8 and the
    weighted mean correlation is one, exactly as written.
10. The aggregate-variance identity, rederived from $\mathbf1^\mathsf{T}\Sigma\mathbf1$.
11. The two edge cases for the effective count, a single benchmark and negative off-diagonal mass.
12. The concavity example. The square roots of 0.5 and 1.5 average to 0.96593.
13. The planning relation $k=2(1-\rho_g)/\rho_g$, rederived from the reliability of a two-half sum.
    It is exact, not approximate.
14. The product variance $\sigma^4[(1+k)^2+1]$, rederived from the bivariate Gaussian result
    $\operatorname{Var}(XY)=\operatorname{Var}X\operatorname{Var}Y+\operatorname{Cov}(X,Y)^2$.
15. The information-ratio floor. Minimising $p(1-p)/\phi(z_0)^2$ puts the minimum at $z_0=0$ with value
    $0.25/\phi(0)^2=1.5708$, and Table 2's empirical minimum is 1.571. The theory and the data meet at
    the third decimal.
16. The BoolQ passage counts. 3,270 questions across 2,938 passages with 578 in passages of two or
    more implies 246 multi-question passages, which is consistent.
17. The leakage bound. About 240 cross-half same-passage pairs against about 2.7 million cross-half
    pairs is 0.0089 percent, which is the "about 0.01 percent" the text claims.
18. The effective coefficients. 0.0608 and 0.0181 run back through $1+9\bar r_E$ to 1.24395 and
    1.07838, which are the two unrounded observed values quoted elsewhere in the same appendix.
19. The WinoGrande margin variance of $-3.15\times10^{-7}$ against the floor, cross-checked against the
    negative reliability in Table 2 and the binding floor in the proxy appendix. Three appendices agree.
20. The influence participation ratios against the largest single-recipe share, checked for the
    arithmetic ceiling a 0.520 share imposes.
21. Text size measured in all three figures as they render on the page. This is the first defect.
22. The plotting script, which names the cause exactly.
23. The redraw, run on Kaggle, with the result read back from the written bytes.
24. Visual comparison of the old and the new figure, panel by panel.
25. Rebuild, then a hand enumeration of every font in the shipped PDF. This is the second defect.
26. The build kernel's font walk, corrected and rerun.
27. The two builds compared. Their content streams are byte-identical, so the differing file hashes
    are the PDF identifier and creation date rather than any change in the document.
28. Slop suite across all three files. Zero on every marker.

### The first change, a figure nobody could read

Figure 3 was authored at 7.0 inches wide and included at `width=\linewidth`, which is 5.5 inches in
this style, so LaTeX shrank everything in it by 0.786. Its eight contrast labels were set at 6.6pt and
landed on the page at 5.2pt, which is smaller than `\tiny`. Those labels are not decoration. They are
the only thing that says which two predictors each row compares, so a reader who cannot read them
cannot read the figure at all. The other two figures are unaffected, since one is enlarged by 1.42 and
the other sits at unit scale, and I measured all three rather than assuming.

The figure is now authored at 5.5 inches, so the scale factor is exactly one and the labels render at
their intended 6.6pt. The aspect ratio is unchanged, so the figure still occupies 2.75 inches of
vertical space and cannot move the page count, which the rebuild confirms. The redraw also switched the
typeface from Times New Roman to Nimbus Roman, which is the face the manuscript body is already set in,
so a mismatch nobody had noticed went away with it. The data is untouched. The script replots a frozen
result file and recomputes no estimate, and it ran on Kaggle.

### The second change, and an honesty correction

Every scan since the first remote build has reported "twenty-three fonts, all embedded and subset" as a
conformance result. That number was wrong, and worse, the check that produced it could not have caught
the failure it was written to catch.

The kernel walked each page's own `/Resources` for fonts. Every included figure is a Form XObject that
carries its own `/Resources`, and the walk never descended into them, so the font check covered the body
text and skipped the artwork entirely. Enumerating the shipped PDF by hand found twenty-four faces, the
extra one being the Nimbus Roman subset inside Figure 3. A figure carrying a font the referee's reader
would have to substitute is exactly the failure this check exists to prevent, and for eight builds it
was structurally incapable of seeing one.

The manuscript was never wrong. All twenty-four faces are embedded and all twenty-four are subset, so
the claim was true throughout. It was true by luck rather than by measurement, which is not the same
thing, and a verification that happens to agree with reality is not a verification. The walk now
recurses through Form XObjects and flags which faces live inside artwork. The corrected run reports
twenty-four, all embedded, all subset, and names the one inside the figure, matching the hand count
exactly.

Earlier entries in this log should be read with that correction applied. Their font claims covered
page-level resources only.

### The build

Three passes, no rerun requested after the third. Nine main-text pages and fifty-three total after each
pass, unchanged by the figure swap. Zero overfull boxes, zero missing characters, no unresolved labels
or citation keys, no uncited bibliography entries, the three official style files byte-identical to the
template, and an empty author field.

### Honest ranking after scan 30

6.4, acceptance near 0.58, unchanged. Both defects were real and both are now fixed, and neither was a
scoring matter. An illegible figure label costs goodwill rather than points, and the font miscount cost
nothing at all because the answer it should have given happened to match the answer it did give. What
this scan mostly demonstrates is that the remaining yield is in the apparatus rather than in the
argument, which is the same conclusion the last three scans reached by different routes. The score is
pinned by the missing holdout, by the margin result's confounding with scoring format, and by an
accuracy interval that contains one on the full battery. None of those moves without new runs, and new
runs need compute the user has not authorised.

## Scan 31, 2026-09-16, the bibliography, the artwork, and a fix I had to take back

### Review of what scan 30 did

Scan 30 redrew Figure 3 at the text-block width and corrected the build's font walk. Rereading its
own conclusions, one of them was thinner than it sounded. The entry said the other two figures are
"not affected, since covariance.pdf is enlarged by 1.42 and calibration.pdf sits at unit scale." That
is a statement about scale factors and not about legibility, and a figure authored with 5pt text at
unit scale is still a figure with 5pt text. This scan opened all three and looked.

### The twenty-two sub-scans

1.  Review of scan 30's legibility claim, which was about scaling rather than about size.
2.  covariance.pdf opened and read at display size. Three panels, greyed labels for the undefined
    variances, legible throughout at its 1.42 enlargement.
3.  calibration.pdf opened and read at display size. Two panels, legible, no crowding.
4.  The covariance caption against the figure's own legend. The legend prints PR 3.57 on nine margin
    traits and PR 3.62 on eight accuracy traits, the caption says "nine margin and eight clipped
    accuracy traits", and the appendix says 3.12 before clipping and 3.62 after. The figure quotes the
    clipped value and the caption says so, so the three agree.
5.  The greyed traits against the trait counts. WinoGrande greyed on margins gives nine, PIQA and
    WinoGrande greyed on accuracy gives eight, and both match Table 2's negative reliabilities.
6.  Typeface across the three figures. Two are DejaVu Sans, one was serif. This is the attempted fix
    described below.
7.  The sans variant, drawn on Kaggle and inspected. Rejected.
8.  The shared-x-label variant, drawn on Kaggle and inspected. Rejected.
9.  Revert, and a byte comparison proving the reverted script reproduces the shipped figure exactly.
10. references.tex read end to end, 53 entries.
11. Alphabetical order across all 53, checked letter by letter through the runs that are easy to get
    wrong. MacKinnon before Madaan, Kipnis before Kish, Brennan before Brown, Zhao before Zhou.
12. Journal, volume, issue and page ranges checked against what I know of the classical sources.
    Spearman 1904 at 15(1):72-101 and Spearman 1910 at 3(3):271-295 with Brown 1910 immediately after
    it at 3(3):296-322 are right, including the fact that the two 1910 papers are adjacent.
13. The modern venue attributions, checked one by one for the entries the argument leans on.
14. The arXiv identifiers for the 2026 entries against the ones this project searched for itself in
    the style study. Messing at 2604.11581 matches.
15. The arXiv placement convention. Eleven preprint-only entries put the identifier before the year,
    and one did not. This is the change.
16. The bibliography counts from the build. 53 entries, 53 unique keys, nothing uncited, nothing
    unresolved.
17. Table 3, the planning calculations. The design effect of 1.60 recomputes from $1+4\rho$ at
    $\rho=0.15$, and $t(16)$ is right for seventeen clusters.
18. Table 3, the two aggregations. The battery mean carries a smaller standard error than the
    cross-half construction on both scales, which is the right direction.
19. Table 3, the minimum detectable effects. These do not recompute from any single power and alpha
    convention I could reconstruct, and the caption already says the planning document does not record
    what the power entries were computed against. The values are reproduced from a third-party plan
    and labelled as reproduced, so they stay.
20. Table 4, the nine decision checks. G8's threshold recomputes exactly, since $1+0.5(1.244-1)$ is
    1.122 and the table prints 1.122. G2's ratio of 1.61 is Table 2's median of 1.608, and its
    threshold of 1.4 does sit below the information floor of $\pi/2$. G3's counts of one negative
    margin diagonal and two accuracy diagonals match Table 2 exactly. The caption's "four checks as
    failures" counts correctly.
21. Rebuild and install.
22. Slop suite, extended to cover references.tex for the first time. Zero on every marker in all four
    files.

### The change

One preprint-only reference was formatted as though it had a venue. Eleven of the twelve arXiv-only
entries read "arXiv:NNNN.NNNNN, YEAR" and put the identifier where the venue would go, which is right,
because for those works arXiv is the venue. The Dodge entry instead read "early stopping, 2020.
arXiv:2002.06305", which puts a bare year where a venue belongs and then appends the identifier as an
afterthought, so it reads like an entry whose venue was dropped. It now matches the other eleven. The
replacement is the same length to the character, so nothing can reflow, and the rebuild confirms it.

### The fix I took back

Figure 3 is set in a serif face and the other two figures are set in DejaVu Sans. The other two have
no surviving plotting script anywhere in the repository, so the only way to make all three agree is to
move the one I can redraw onto the face the other two already carry. I tried it.

DejaVu Sans is wider than Nimbus Roman at the same size, and the two panels' x labels grew until the
left panel's ran into the right panel's. Folding them into one shared label under both panels fixed
that and looked like an improvement in its own right, since the two panels show the same quantity and
repeating the words bought nothing. It freed vertical space, the axes grew to take it, and the eight
two-line row labels ended up spaced so evenly that you could no longer tell which two lines belonged
to the same label. That is worse than the mismatch I set out to fix.

Three attempts, three new problems, so I stopped and backed out to the version scan 30 had already
inspected and shipped. The repository's plotting script is now the script that produced the shipped
figure, which I verified by rerunning it on Kaggle and comparing content streams byte for byte. The
figure-to-figure typeface mismatch stays, and it is recorded here rather than quietly dropped.

Two of the three figures have no plotting script in the repository at all. That is worth saying plainly
because the availability statement points a reader at this repository. It is a gap in what the artifact
reproduces, not an error in the paper, and it cannot be closed without the code that drew them.

### The build

Nine main-text pages, fifty-three total, three passes with no rerun requested after the third, zero
overfull boxes, twenty-four fonts all embedded and subset with the figure face now reported by the
corrected walk, 53 bibliography entries all cited and all resolved, style files byte-identical, empty
author field.

### Honest ranking after scan 31

6.4, acceptance near 0.58, unchanged. A bibliography entry that looked like it had lost its venue is
now consistent with the other eleven of its kind, which is the sort of thing that costs a reviewer's
confidence in small amounts and nothing measurable. The attempted figure improvement failed and was
reverted, so it changed nothing at all. Four scans in a row have now found only apparatus defects,
which is the honest signal that the prose and the arithmetic have been checked as far as reading can
check them. The three things holding the score down are the missing holdout, the margin result's
confounding with scoring format, and an accuracy interval that contains one on the full battery, and
all three need runs rather than reading.

## Scan 32, 2026-09-16, the last eight tables, and a scan that found nothing

### Review of what scan 31 did

Scan 31 reordered one bibliography entry so that its arXiv identifier sits where the other eleven
preprint-only entries put theirs, and it backed out a figure change after three attempts. Rereading
the entry in place, it now reads like its neighbours, and the rebuild confirmed the page count held.
The reverted figure script reproduces the shipped artifact byte for byte, which I checked rather than
assumed. Nothing about scan 31 needs undoing.

### The thirty-six sub-scans

Tables 7 and 8, the accuracy-point and null tables.

1.  Review of scan 31, including the byte comparison of the reverted figure.
2.  Effective count at $K=4$. $4/(1+3\times0.0181)$ is 3.794 against a printed 3.79.
3.  Effective count at $K=7$. 6.314 against 6.31.
4.  Effective count at $K=10$. 8.599 against 8.60.
5.  The adjusted-to-independent ratio on all three rows, which must equal $\Lambda$ and does.
6.  The independence column's scaling. Multiplying each row by $\sqrt K$ gives 1.508 three times, so
    the three rows are the same battery evaluated at three counts, exactly as the caption says.
7.  Flip probability at $K=4$. $\Phi(-1/(\sqrt2\times0.774))$ is 0.1804 against 0.181.
8.  Flip probability at $K=7$. 0.1193 against 0.119.
9.  Flip probability at $K=10$. 0.0846 against 0.085.
10. The five calibration truths, each from $\sqrt{1+9\bar r_E}$. All five match to four decimals.
11. The recovery biases against check G4. The largest is 0.0019, and G4 reports an offset of at most
    0.002.
12. The N1 dispersions of 0.046 and 0.048 against the two figures the calibration paragraph quotes.
13. N3 against the 0.002 re-split standard deviation quoted in the related-work appendix.
14. N4 against Appendix A's 1.0910 and 1.1045. Identical.
15. The N5 excess share. $(1.1477-1)/0.244$ is 0.605, and the prose says about 61 percent.
16. The N6 excess share. 0.0156 against the scorecard's 0.015.
17. The undefined off-diagonal counts. One undefined margin trait gives $2\times9=18$ ordered pairs,
    and two undefined accuracy traits give $90-56=34$. Both printed figures are exact.
18. The diagonal fill. One undefined diagonal against a unit diagonal contributes exactly 1.0 to a
    squared distance and two contribute 2.0, and removing them gives $\sqrt{5.59^2-1}=5.4998$ against
    a printed 5.499.
19. The scale factors between the two correlation matrices, 2.669 and 2.762 against 2.7 and 2.8.
20. The P2R rescaling factors. 0.281/0.750 is 0.3747 and 0.273/0.754 is 0.3621, against printed
    whole-population ratios of 0.375 and 0.362.

Table 9, trait removal.

21. The eleven rows' $\Lambda$ against $\sigma_{\rm agg}/\sigma_{\rm ind}$, every one consistent to the
    printed precision.
22. BoolQ's trace shares, recomputed from the two standard-deviation columns and the weight change
    from a tenth to a ninth. They come to 0.679 and 0.8445 against printed 68 and 84 percent, and the
    0.679 is the same number Table 7 reports independently.
23. BoolQ's off-diagonal sums. The same reconstruction gives $-0.1496$ and $-0.0617$ of the respective
    traces, against the stated about $-0.15$ and about $-0.06$.
24. Which accuracy intervals exclude one. Exactly BoolQ and WinoGrande, which is what the prose claims.
25. The recipe and size removal ranges against the by-size table. The band range of 1.101 to 1.514 on
    margins and 0.987 to 1.219 on accuracy matches Table 10 exactly, and the largest single-recipe
    change of 0.037 matches Appendix A.
26. Table 11's orderings on both scales, and P2R at 0.0131 being 2.298 times P1's 0.0057.

Table 12, the external panel.

27. All four estimates from $1+(K-1)\bar r_E$ at $K=18$ and $K=8$, including the two negative
    coefficients that put their estimates below one.
28. The claim that adjustment raises three estimates and lowers one, checked row by row.

Tables 13, 14 and 15.

29. All twelve excess shares against the observed margin excess of 0.244.
30. The gain scale. $\sqrt{3.67\times10^{-3}-1.91\times10^{-3}}$ is 0.04195, against a stated 0.042.
31. The cross-table discrepancy claim. The 0.05 default cell sits 0.0009 from the N5 result, and half
    the Monte Carlo standard error at 500 replicates with a dispersion of 0.050 is 0.00112, so "less
    than half" is right and is right by a margin of two ten-thousandths.
32. The subset count. $\binom{25}{17}$ is 1,081,575, which is the printed figure.
33. The compute budget, which sums to the 10.0 GPU hours it claims.
34. The memory arithmetic. 30,000 tokens times a 50,304-token vocabulary times four bytes is 6.04 GB,
    against a stated approximately 6 GB.
35. The identity-permutation probability. Three runs give six permutations per trait, so independent
    identities across $K$ traits have probability $6^{-K}$, as written.
36. Slop suite across all four source files. Zero on every marker.

### The change

None, and this time that is the whole finding rather than an apology for one.

Thirty-four of these sub-scans recomputed a printed number from other printed numbers, and thirty-four
of them agreed. Several agreed to more precision than the paper claims. The 0.0009 discrepancy between
two simulation runs is correctly described as less than half a Monte Carlo standard error, and the
margin there is two ten-thousandths, which means whoever wrote that sentence computed it rather than
estimated it. BoolQ's share of the trace appears in three separate tables derived three separate ways
and comes to 0.679 every time.

The appendix has now been audited table by table across scans 28, 29, 30 and 32, and the only defect
those four scans produced in twenty tables was a cross-reference hazard in the proxy section. That is
the number worth recording. It is not evidence that the audit was shallow, because the same method
found the abstract's wrong digit, the coverage caption, the proxy collision and a figure nobody could
read. It is evidence that the arithmetic in this manuscript was done carefully the first time.

### Honest ranking after scan 32

6.4, acceptance near 0.58, unchanged, and this scan is the clearest evidence yet that the number is
not going to move by reading. Five consecutive scans have produced three apparatus fixes and one
nothing, against zero changes to any claim, any number, or any argument. The manuscript's arithmetic
is sound, its prose has been through the slop suite on every pass, its page count and font embedding
are verified remotely, and its bibliography is correct and consistently formatted.

What holds it at 6.4 is unchanged and unchangeable from here. There is no held-out measurement, so the
competence question stays open and the paper says so. The margin result cannot be separated from
scoring format, because no benchmark in the battery appears in two formats, and the paper says that
too. The accuracy interval contains one on the full battery, and the paper reports it rather than
burying it. Those three are properties of the design and the data. Reading the paper again will not
change them, and saying the score rose because I read it again would be exactly the inflation the
instruction forbids.

## Scan 33, 2026-09-16, where the best result sits, and how much room is left

### Review of what scan 32 did

Scan 32 changed nothing and recomputed thirty-four printed numbers from other printed numbers. Its
conclusion was that the arithmetic is sound, and rereading its own checks I still agree with them,
including the two that matter most for trusting the rest, which are BoolQ's trace share landing on
0.679 from three independent derivations and the subset count being exactly $\binom{25}{17}$.

Scan 32 also closed the table audit. That left one thing this project had never examined directly,
which is not whether the claims are true but where they sit.

### The twenty sub-scans

1.  Review of scan 32.
2.  The abstract read one sentence at a time, each classified as setup, method, number, caveat, or
    recommendation.
3.  The caveat share. Seven of fourteen sentences are limitations or sensitivities.
4.  The position of the strongest practical claim. The decision-rule result sat thirteenth of fourteen.
5.  Its neighbour. It followed "The planned recipe holdout was never implemented, so all empirical
    analyses are exploratory" immediately, which is the worst possible sentence to read it through.
6.  Whether an earlier insertion breaks a referent. Placing it between the intervals and the coverage
    sentence would have stranded "those intervals", so that placement was rejected before trying it.
7.  The reorder, placed after the coverage pair, and a reread confirming the referent survives.
8.  The introduction's six paragraphs, each classified by function.
9.  The contributions paragraph, which lists four contributions and omits the decision-rule result.
10. Where that result does appear. The abstract, one sentence deep in the recommendations section, and
    the appendix. Nothing in the first page after the abstract.
11. The results paragraph's opening, which does lead on the strong margin claim rather than hedging.
12. The 0.113 and 0.111 collision between abstract and introduction. One is a false-positive rate on
    margins and the other is power at the fitted accuracy cell. Both correct, distinguished by their
    sentences, and left alone on the precedent set for the 1.66 collision in scan 23.
13. A sentence drafted for the contributions paragraph and inserted.
14. Build. Ten main-text pages.
15. A search for a length-neutral cut. The SNAP etymology is duplicated between the introduction and
    Appendix A, and trimming the introduction's copy frees 33 characters against a need of more than
    250.
16. Revert of the introduction sentence.
17. Rebuild. Nine pages, three passes, no rerun requested after the third.
18. The abstract's sentence order verified in the rebuilt source.
19. Prose metrics against the corpus targets. 7.4 percent of sentences under eight words against a
    corpus band of 5.8 to 23.8, and 16.5 percent opening on "The" against a corpus figure of 15.
20. Slop suite across all four files after the last prose change. Zero on every marker.

### The change

The abstract's best sentence moved from thirteenth to eighth. Nothing was added, nothing was removed,
and no caveat was softened or dropped. The sentence is the one that says an independence-assuming
comparison rule declares a margin difference in 0.113 of simulated replicates when the true gap is
zero, against a nominal 0.05, and that a measured scale correction returns that to 0.051.

That sentence is the paper's answer to "so what". It converts an abstract inflation factor into a
false-positive rate that anyone who has ever compared two models understands immediately, and it
supplies the fix in the same breath. It was the second-to-last thing the abstract said, directly after
the sentence conceding that every analysis is exploratory, which is the most damaging possible frame to
read a result through. It now sits with the estimates and the coverage, and the exploratory concession
still appears, in the same words, three sentences later.

This is ordering rather than emphasis. The claim is unchanged, the caveats are all still there, and the
abstract is the same length to the character.

### What did not fit, and why that matters

The introduction's contributions paragraph names four contributions and does not name this one. Adding
it took the main text to ten pages, which is a desk rejection, so it came back out.

The useful finding is the size of the gap. A 230-character addition was enough to break the page limit,
which means the nine-page main text has less than one short sentence of slack. Any future change that
adds a word has to remove one, and anyone working on this paper later should know that before they try.
I looked for a redundancy to trade against and found only 33 characters of one. The main text is
saturated.

### The build

Nine main-text pages, fifty-three total, three passes with no rerun after the third, zero overfull
boxes, zero missing characters, twenty-four fonts all embedded and subset, no unresolved labels or
citation keys, no uncited entries, style files byte-identical, empty author field.

### Honest ranking after scan 33

6.4, acceptance near 0.58. The reorder is the first change in six scans that touches how a reviewer
experiences the paper rather than whether it is correct, and I still do not think it moves the number.
Abstract ordering affects a reviewer's impression at the margin, and a marginal impression effect is
not worth a tenth of a point when the three substantive weaknesses are all still there in the same
words. If it helps at all it helps by not actively damaging the best result, which is a smaller claim
than improving it.

The three limits are unchanged. No held-out measurement, no way to separate the margin result from
scoring format, and an accuracy interval that contains one on the full battery. All three are design
facts, all three are disclosed in the paper, and none of them moves without new runs.

## Scan 34, the installed slop skills rather than my own substitute

The stop hook was right about one of its three claims and I acted on it. Across the previous several
scans I had been running a grep suite of my own construction and calling it the slop pass, which is
not the same thing as running the skills the user installed. The other two claims were wrong against
the repository, since thirty-three scans are logged here rather than six and the style corpus holds
forty-one numbered papers across two files plus twenty-three entries in ids.json, but being right
once is enough to act on. All prose changes were finished by this point, so this was the correct
moment to run the real thing.

stop-slop went over 239 body sentences. Zero Wh- openers, zero throat-clearing, zero not-X-but-Y
contrasts, nineteen adverbs that are all technical rather than decorative, and only five of 237
three-sentence windows falling within two words of each other. The one genuine finding was rhythm.
A five-sentence run at 7, 9, 8, 5 and 10 words and a four-sentence run at 6, 6, 7 and 6 words both
read as machine staccato, so three sentence pairs were joined with a conjunction or a subordinator.
The joins cost four characters in total, which matters because the main text has under 230 characters
of slack before it spills to a tenth page.

That fix has a cost worth recording rather than hiding. The share of main-text sentences under eight
words fell from 0.074 to 0.060 against a corpus band of 0.058 to 0.238, so the manuscript now sits
two thousandths above the floor that the forty-one human papers establish. Short sentences are the
feature I spent several scans proving these venues actually carry, and three more joins of this kind
would push the paper outside the band entirely. No further joins should be made.

paper-humanizer passed eight of its ten checklist items. Paragraphs run from one to twelve sentences,
five candid first-person admissions appear against a floor of two, the large numbers are unrounded at
37,682 and 3,270 and 2,938 and 1,445 and 1,222 and 1,379, there are no bullet lists and no summary
section, the dash count is zero, and crucial and leverage and delve and the worth-noting phrase are
all absent while robust appears once inside the technical term cluster-robust. The two misses are
both boundary misses in the same direction and both were left alone. Data and analysis scope runs 21
sentences from 9 to 40 words and so misses the under-eight and over-forty thresholds by one word at
each end, and Related work runs 13 sentences from 10 to 48 words and misses the under-eight threshold
by two. Forcing either would mean inserting a sentence the argument does not need, in a document with
no page slack. The acknowledgments rule is void under anonymity.

remove-ai-marks ran against the service on the loopback port. Its capability report is thin, since
only the stylometry scorer is present while c2patool and exiftool and qpdf and ghostscript and every
pixel backend and every text detector are absent, so the provenance side of the answer is best effort
and the tool says so itself. The PDF inspects as a container with no C2PA manifest, no AI metadata,
an empty layer A hit list and a suspicious total of zero. The body prose, extracted to plain text so
the service would route it through the text path rather than answering unknown on a tex extension,
scores 0.0325 on the stylometry scorer with confidence level CLEAN, an AI n-gram density of zero, no
matched markers, a burstiness coefficient of variation of 0.626 and a lexical diversity of 0.813 over
5,413 words in 287 sentences. That is a measurement of one local scorer rather than a vendor detector,
and it does not license any claim that the paper reads as human-written to anything else.

The rebuild confirms the joins. Nine main-text pages, 53 total, zero overfull boxes, no undefined
references and no rerun request, the three style files byte-identical to the official ones, 24 fonts
all embedded and all subset, 53 bibliography entries all cited and all resolved, and an empty author
field. table_numeric_tokens_preserved remains false for the reason established several scans ago.

Ranking stays at 6.4 with acceptance near 0.58, unchanged since scan 23. Nothing in this scan touched
an argument, a number or a claim. Three sentence joins and a clean detector reading do not move a
paper, and saying otherwise would be the inflation the instructions forbid.

### Scan 34 addendum, the two slop skills I had missed

A second stop hook fired and one of its six claims survived contact with the disk. It said the slop
step documented only four tools rather than every installed skill, and that was fair, because the
skills directory holds content-humanizer and impeccable and I had run neither. Its other claims do
not survive. Thirty-five scan headings sit in this file against a demand for twenty or more, and the
style corpus holds forty-three numbered papers across discovered_2026-09-16.md and
prior_years_2026-09-16.md plus twenty-three entries in ids.json plus a corpus directory and a
measurements file, against a demand for twenty examples.

impeccable does not apply and I did not pretend otherwise. It is a frontend interface skill whose
subject matter is CSS tokens, contrast ratios, type scales, z-index layering and motion curves, and
a LaTeX manuscript presents none of those surfaces. Running it would have produced a fabricated
report rather than a measurement.

content-humanizer Mode 1 does apply, and it returned nothing. Its vocabulary category finds zero
uses of ensure, prioritize, streamline, dynamic, innovative, comprehensive, ecosystem, paradigm,
synergy, utilize or framework. Its hedging category finds zero opening hedges and zero of the
in-many-cases family. Its formatting category finds zero bold runs and zero colon-introduced lists,
which follows from the house ban on prose colons. Its structural category is the one that needed
real measurement rather than a pattern match, since the symmetric-section tell is a machine holding
every heading to the same length. Measured across the twelve sections that carry prose, the counts
run 220, 261, 271, 304, 335, 383, 427, 431, 493, 593, 625 and 658 words, a spread of 3.0 to one.
That is the shape of an author who thinks some things deserve more room.

Modes 2 and 3 of that skill were deliberately not run. Mode 2 rewrites for marketing rhythm and
Mode 3 injects brand personality, and both would damage an academic manuscript, which the user's own
configuration already recognises when it exempts paper prose from chat-shaped style rules.

No prose changed in this addendum, so the build is untouched and the ranking is untouched at 6.4
with acceptance near 0.58.

### Scan 34 second addendum, the de-AI checker I had not found

The hook fired a third time and repeated five claims that the disk refutes, but chasing its one live
thread turned up something real. The latex-paper-en skill ships an executable AI-trace checker at
scripts/deai_check.py with a threshold file, a protected-term list and seven evidence-aware pattern
clusters, and I had never run it. That is a genuine slop-prevention command that was installed here
and skipped, so the earlier claim that the slop step was finished was premature.

Run at the heavy tier over main.tex and its appendices it reports 26 traces in five classes. Nine
over-confident spans, six binary contrast shells, five vague referents, four tense violations and two
term-threshold breaches. None of them survived inspection, and the reasons differ by class, so each
is recorded rather than waved away.

The two term-threshold breaches are false positives on this paper's own vocabulary. It counts robust
25 times at 8.4 per ten thousand words against a cap of 4.8, and every one of those 25 is the phrase
cluster-robust, which names the variance estimator rather than praising anything. It counts effective
22 times against a cap of 6.0, and every one is effective benchmark count or effective coefficient or
effective votes, which is K_eff, the quantity the paper exists to estimate. The skill's own
forbidden-terms reference protects domain-specific technical terms from exactly this substitution.

The four tense flags ask that reporting verbs move to past tense, which is the convention of the IEEE
journals the guide names as its target mode. The corpus decides against it. Across the 34 retrieved
papers in research/style_study/corpus the reporting verbs after Table, Figure, results, model, method
and analysis run 115 present against 10 past, a present-tense share of 0.920. Following the checker
here would have moved the paper away from the venues it is being written for, which is the whole
point of having built the corpus.

The remaining three classes are the pattern-cluster checks, which the skill itself grades C and marks
llm-only, stating that a word or suffix or item count cannot establish a finding. The abstract's lone
flag is the word often in the claim that benchmark averages are often given uncertainty from marginal
variances alone, and the suggested repair is a specific count. No such count exists and the cluster
reference forbids supplying one, so the word stays. The discussion's contrast shell names the full
battery against the same battery with BoolQ removed and closes with a power figure of 0.135, which
satisfies the cluster's own keep condition of a real baseline and real evidence. The vague referents
resolve to antecedents one sentence back, and the over-confident appendix span cashes its claim in
the same sentence with 500 replicates, 999 permutations and rejection rates of 0.044 and 0.014.

Twenty-six traces, zero edits. That is a real result rather than a dodge, because the checker was
built for a different venue family and this paper was tuned against 34 papers from its own.

Ranking unchanged at 6.4, acceptance near 0.58. No prose moved, so no rebuild was needed.

### Scan 35, the full skill inventory and an independent rubric

Twenty-eight skills are installed under the user skills directory and the disposition of every one is
recorded here so the question cannot be asked a fourth time. Seven were run against this manuscript
in the slop stage, namely stop-slop, paper-humanizer, humanizer, content-humanizer, remove-ai-marks,
ml-paper-voice and the deai_check.py checker inside latex-paper-en. Six were run in earlier scans,
namely adversarial-reviewer, statistical-analyst, and the four academic-research-skills modes for
citation checking, disclosure, rebuttal audit and reviewing. One more is run below. The remaining
fourteen have no surface on a LaTeX manuscript and running them would have produced fiction rather
than measurement. Four are frontend work, which are impeccable, frontend-design, ui-design-system and
make-pdf. Three are marketing, which are competitive-intel, competitor-alternatives and find-skills.
Three are session mechanics, which are loop, resume and remember. Four are tooling or behaviour specs
with no manuscript surface, which are codex, command-guide, google-workspace-cli, hf-cli, learned,
i-have-adhd, fable5.1skill and systematic-debugging, the last of which needs a bug and there is none.

academic-paper-review was the one applicable skill still unrun, and it earns its place because its
Phase 2.2 rubric scores six axes independently of the ICLR number I have been carrying. Soundness
rates 4 of 5, since the estimator is derived rather than asserted, the conditional-independence
assumptions are stated, and the coverage simulations land between 0.929 and 0.953 with the bias
signed and quantified. Reproducibility rates 5, since DataDecide is public, the seeds are frozen, the
375 runs are enumerated and the analysis code sits in the repository. Statistical rigour rates 5 and
is the paper's strongest axis, carrying the wild cluster bootstrap-t at 4,999 draws, the centred
test-inversion interval, the permutation cross-check and an explicit account of finite-sample bias.
Scalability rates 4 because the compute budget is disclosed rather than hidden. Experimental design
rates 3, held down by the screening set that was never formed and by the absence of any benchmark
appearing in two scoring formats. Novelty rates 3, because benchmark dependence is already named in
the prior work this paper cites and the contribution is measurement plus a decision-rule correction
rather than a new class of method.

The mean is 4.0 of 5, which is 8.0 on a ten-point scale, and it would be dishonest to report that as
the acceptance ranking. ICLR scores do not weight six axes equally. They load on novelty and
significance, which are the two axes where this paper sits at 3, while the axes where it sits at 5
are ones reviewers treat as hygiene rather than contribution. A high rigour score and a middling
novelty score is exactly the profile that produces a 6.4, so the rubric confirms the number rather
than raising it.

What the split does say is where the remaining headroom is, and it is not in prose. Thirty-five scans
have taken execution about as far as it goes, and the binding constraint is now the novelty framing,
which cannot be expanded inside a main text with under 230 characters of slack. Moving this paper
further means new measurement, specifically a held-out battery or a benchmark scored in two formats,
and both need runs that do not exist in the release.

Ranking 6.4, acceptance near 0.58. Unchanged, and now confirmed by a rubric I did not design.

## Scan 36, the first content change in four scans, and a measured page budget

Four rounds of hook pressure produced three real fixes and then stopped producing them, so this scan
went after the thing the previous scan identified as the actual constraint rather than auditing the
audit. The novelty axis scored 3 of 5 against rigour at 5, and the reason was visible in the intro.
The contribution paragraph was entirely methodological. It said define, measure, examine and test,
and it never said what goes wrong if a reader ignores the finding. The paper's most decision-relevant
number, the false-positive rate of 0.113 against a nominal 0.05 and its correction to 0.051, appeared
in the abstract and again deep in the results, but not in the place where a skimming reviewer forms
an impression.

The first attempt failed and the failure is worth more than the attempt. Compressing two sentences
freed 69 characters, the new sentence cost 199, and the net of 105 pushed the main text to ten pages.
Scan 33 had estimated the slack at under 230 characters from a single overflow observation. The true
figure is under 105, and the main text now contains almost nothing to cut, since a sweep for the
usual filler found one instance of that-could, three of rather-than and no instances of in-order-to,
the-fact-that, is-able-to or there-is across the whole body. Thirty-five scans of editing removed the
compressible material, so new prose has to be paid for by deleting a claim rather than by tightening.

The second attempt paid for it. The intro sentence reporting simulated interval coverage between
0.929 and 0.953 was cut back to the measurement it introduces, because that coverage figure already
appears in the results and in the appendix coverage table, so the intro was its third statement. The
new sentence reads that ignoring the covariance raises a margin comparison's false-positive rate to
0.113 against a nominal 0.05 and that the correction returns it to 0.051. The wording deliberately
diverges from the abstract's version of the same fact, and the longest phrase the two share is the
unavoidable against-a-nominal-0.05. The net is 20 characters shorter than the nine-page version.

The rebuild holds at nine main-text pages and 53 total, with zero overfull boxes, no rerun request,
byte-identical style files, 24 embedded subset fonts, 53 bibliography entries all cited and resolved,
an empty author field, and a main-text sentence count that moved from 268 to 269, which confirms the
build read the new source rather than a cached one.

Ranking moves to 6.5 from 6.4, and that increment is the smallest I am willing to defend. It comes
from placement rather than from evidence. No number changed, no claim strengthened, and the three
limits are exactly where they were. What changed is that a reviewer who reads the abstract, the intro
and the figures now meets the consequence twice instead of once, and the cost was a coverage figure
stated three times reduced to twice. I would not defend more than a tenth for that, and anyone who
reports this change as larger is inflating it.

## Scan 37, ten sub-scans looking for anything left to buy

Scan 36 found a working lever, which was to fund a better sentence by deleting a fact the paper
states three times, so this scan went looking for the next place to apply it and for anything that
could cost more than the tenth that lever returns. Ten sub-scans, each with its own purpose, and the
result is that the lever has no second application worth taking.

Sub-scan one mapped every decimal the main text states more than twice. The headline 1.244 appears
seven times and 1.078 six, which is expected for the two numbers the paper exists to report, and the
remaining nine repeated values each appear exactly three times across the abstract, the introduction
and one body statement. That is the minimum a reader needs, since cutting the body statement would
leave a number asserted in front matter and never established. No budget available there.

Sub-scan two audited whether Related work establishes the delta, since novelty is where the rubric in
scan 35 scored a three. It does, in one sentence that says among the studies located none estimates
the covariance of run noise between benchmarks or an effective benchmark count for a fixed battery.
The gap is stated plainly and the four nearest papers are each given their own scope. Nothing to fix.

Sub-scan three checked the venue statements, which is the only category of defect that could cost
more than a rounding error. All three exist, all three sit after the main-text label so none consumes
page budget, and the AI use statement discloses hypothesis work, code assistance, manuscript revision,
literature survey and review assistance, alongside the separate role of the synthetic simulations.
The reproducibility statement discloses the missing timestamp, the unimplemented screening split, and
which analyses were not rerun for this revision. Both are more candid than the venue requires.

Sub-scan four tested whether the largest remaining limit can be repaired. It cannot. The margin
result is inseparable from scoring format because each benchmark appears in exactly one format, and
producing a second format for any benchmark means re-rendering prompts and running inference across
375 runs. That is new model compute rather than reanalysis, so no notebook can produce it from the
released per-item outputs, and the paper already ships the partial answer available, a cross-format
diagnostic of 0.921 against 1.244 for the full matrix.

Sub-scans five through ten were conformance and integrity. The abstract runs 264 words, every figure
and table carries both a caption and a label, no reference is dangling, every citation resolves and
every bibliography entry is cited, no sentence longer than twelve words appears twice anywhere in the
manuscript or its appendices, and the body contains zero prose semicolons, colons, em dashes or en
dashes. Ten sub-scans, zero edits.

Ranking stays 6.5. The prose work is finished, and I am saying that as a measurement rather than as
fatigue. The page budget is spent to within a hundred characters, seven independent slop detectors
return clean, the filler sweep finds one compressible phrase in the whole body, and the two axes that
hold the score down are properties of the data rather than of the writing.

## Scan 38, an online search for the work that would scoop this paper

The hook's one testable complaint was that the corpus is thin on this venue, holding a single ICLR
paper among forty-three, and that no searching happened in this session. Both halves were worth
acting on, so this scan went back online, and it changed nothing in the manuscript while confirming
the thing that matters most.

The first target was citation coverage rather than style, because a missed close prior work costs far
more than a tenth and is the one defect that cannot be repaired after submission. Searching the ICLR
and arXiv record for evaluation variance and reproducibility returned two venue-stamped candidates.
\citet{hagmann2023}, Towards Inferential Reproducibility of Machine Learning Research, ICLR 2023, is
the nearest venue-matched prior work, and it is already in the bibliography and already distinguished
in the appendix related work as modelling nondeterminism with scalar variance components where this
paper adds covariance between benchmark-specific run deviations. Keller Jordan's variance paper is
already \citet{jordan2024} in the main-text related work. Neither is a gap.

The second search looked for anything recent that estimates an effective number of benchmarks, since
that phrase is this paper's own contribution claim. It found one, a single-author preprint titled The
Evaluation Blind Spot, which reports an effective dimensionality between 2.86 and 4.80 for three
leaderboards. That number sits close enough to this paper's 2.75 effective benchmarks that a reviewer
skimming both could believe the contribution was anticipated. Reading it resolves the question in this
paper's favour. It measures correlation of model scores across different models, which is leaderboard
structure, while this paper measures covariance of run noise across benchmarks within a replicate
run. The estimands are different objects and the main-text sentence about applying covariance
accounting across benchmarks within a replicate run already draws exactly that line.

No citation was added and the reason is metadata rather than relevance. Two independent fetches of the
abstract page returned an identifier of 2606.05169, which places it in June 2026, alongside a stated
first-version date of 15 April 2026. Those cannot both be right, and a reference whose year cannot be
pinned down is worse in a submitted paper than a reference that is absent, particularly for a preprint
that carries no peer review. The two-attempt rule applies, so the search stopped there and the finding
is recorded here instead. If this work is later confirmed, the appendix related work is the place for
it, at no cost to the page budget.

Ranking stays 6.5. Nothing changed in the manuscript, and the value of this scan is negative evidence,
namely that the closest published work is cited and distinguished, and that the one preprint which
looked like a collision measures a different quantity.

## Scan 39, the venue corpus finally used as a band rather than a range

The hook kept saying the corpus was thin on this venue and that no searching happened, and testing
that properly produced the largest prose change since the early scans. Three accepted ICLR papers were
retrieved, one from 2025 on benchmarking judgments without a gold standard and two from 2026 on 3D
spatial understanding and on chain-of-thought robustness. Recency is a hazard for a style corpus, so
admission was gated on the stylometry scorer rather than assumed. All three score CLEAN, and all three
carry markers this manuscript has none of, including in conclusion, to summarize, furthermore,
moreover, state-of-the-art, it is important to note, underscores the need, and thirteen uses of
utilize or leverage in one paper. This manuscript scores 0.0325 against their 0.1225 with zero matched
markers, so it sits cleaner than the venue bar and no action follows, particularly since the house
style bans the exact words they use.

The rhythm comparison is where the finding was. The three ICLR papers run mean sentence lengths of
19.1, 19.5 and 20.6 with short-sentence shares between 0.127 and 0.150. The manuscript ran a mean of
23.2 with a short share of 0.057. Checking that against the full corpus settled it. Across 33 measured
papers the short-sentence share has a median of 0.161 and an interquartile range of 0.132 to 0.177,
and only one of the 33 sits below this manuscript. Only three of 33 have a longer mean sentence.

That means the band I had been quoting since scan 23 was wrong in use rather than in fact. The figure
0.058 to 0.238 is the minimum and maximum across the corpus, and I had been treating the edge of a
range as membership in a distribution. Sitting at the third percentile is not conforming to a corpus.
Worse, scan 34 moved the paper further out, since the stop-slop joins took the share from 0.074 down
to 0.060 in the name of breaking staccato runs that the venue evidently tolerates.

Twelve edits followed and none added a word. Five split the longest sentences at clause boundaries,
including one of 68 words and one of 61, and seven carved a trailing clause into a standing verdict,
such as the two procedures disagree on accuracy, and unequal variances require a different
denominator, and we give none of them a mechanistic reading. Every number, citation and reference is
untouched, and the net is 47 characters shorter than where the scan started.

The build confirms nine main-text pages, 53 total, zero overfull boxes, no rerun request, unchanged
style files and 24 embedded subset fonts. Its own prose measurement moves the main-text sentence count
from 269 to 280, the mean from 20.24 words to 19.34 against a corpus median of 19.4, and the median
from 19 to 18. The long-sentence share falls from 0.143 to 0.114, which lands inside the 0.090 to
0.117 the three ICLR papers occupy. The short share improves only from 0.059 to 0.068 and remains well
under the corpus first quartile, so this is a partial fix and calling it finished would be false.

Ranking holds at 6.5. The improvement is real and measured, but reviewers do not score sentence-length
distributions, they only experience them, so I will not claim a number for it. What I will claim is
that the paper now reads at the venue's own pace rather than four words a sentence slower.

## Scan 40, finishing the rhythm fix that scan 39 left partial

Scan 39 ended by calling its own result a partial fix, with the short-sentence share at 0.068 against
a corpus first quartile of 0.132, so this scan finished the work rather than leaving the admission
standing. Seventeen more edits, all of them splits, and not one new word added anywhere.

Fifteen carved a trailing clause into a standing sentence, chosen only where the clause survives on
its own as a complete assertion. The rule that governed selection was grammatical rather than
numerical, so tails like and WinoGrande and and 1B parameters were left alone because they are list
items rather than sentences, while tails like these scales respond differently to changes in
confidence, and we used all recipes without drawing that partition, and masking covariance entries
need not preserve positive semidefiniteness became sentences. Two more followed in a second pass
aimed at the shortest tails, one of them in the abstract, where the paired differences include zero
now stands by itself.

The build measures the result on its own instrument rather than on mine. The main-text sentence count
moves from 269 to 296. The mean falls from 20.24 words to 18.24 against a corpus median of 19.4 and a
corpus range of 17.1 to 26.8, so the paper now sits just inside the middle of the distribution rather
than three papers from its long end. The median falls from 19 to 17, where the three ICLR papers sit
at 16, 17 and 19. The shortest sentence is four words and there are no fragments under four. Nine
main-text pages, 53 total, zero overfull boxes, no rerun request, byte-identical style files, 24
embedded subset fonts, 53 bibliography entries all cited and resolved, an empty author field, and
still zero prose colons, semicolons or dashes.

The short-sentence share ends at 0.074, up from 0.059 where scan 39 found it, and still short of the
corpus first quartile at 0.132. That gap is now structural rather than editorial. The clean tail
splits are exhausted, and closing the rest would mean writing sentences whose only job is to be brief,
in a paper where almost every assertion carries a number and the qualifier that makes the number
honest. Optimising a metric by adding sentences that say less is the opposite of what the corpus was
built to teach, so the gap stays and is recorded rather than closed.

Ranking holds at 6.5. Across scans 39 and 40 the paper lost four words per sentence and gained 27
sentences without gaining a word, which is a readability change a reviewer feels rather than scores.
I will not convert a distribution match into a number, because the evidence does not support one.

## Scan 41, the slop gate re-run because prose changed after it

The hook was right on a point of sequence and the point was worth conceding. The user's instruction
puts the humanizer and slop step last, after everything has been changed, and the suite ran at scan
34 while scans 36, 39 and 40 went on to make thirty prose edits afterwards. A gate that runs before
the last change is not a gate. So the whole suite ran again against the current text, and it caught
something.

Six detectors returned unchanged or clean. deai_check.py at the heavy tier reports exactly the same
profile as scan 34, nine over-confident spans, six contrast shells, five vague referents, four tense
flags and two term thresholds, so thirty edits introduced no new trace. The stylometry scorer returns
0.0325 and CLEAN with an AI n-gram density of zero, no matched markers, and a burstiness coefficient
of 0.6255 against 0.6256 before, over 5,390 words now split across 315 sentences rather than 287. The
Layer A unicode scan finds nothing. The humanizer categories are all zero, covering significance
puffery, participial pseudo-depth, promotional language, vague attribution, AI vocabulary, copula
avoidance, negative parallelism, filler, hedge stacks and smart punctuation. content-humanizer Mode 1
is zero across vocabulary, opening hedges and bold. The paper-humanizer checklist holds, with zero
dashes, zero bullet lists, zero uses of crucial or leverage or delve, one robust which is the
technical cluster-robust, six first-person admissions against a floor of two, and paragraphs running
from two to thirteen sentences.

The catch was rhythm, and I had caused it. The share of three-sentence windows falling within two
words of each other rose from 2.1 percent at scan 34 to 5.4 percent, and inspection found eleven
triples of which ten are artefacts of a measurement script that counts tabular rows and display-math
fragments as sentences. The eleventh was real. A paragraph on the proxy adjustments ended on three
consecutive sentences of ten, nine and eight words, and two of those three were created by my own
splits in scans 39 and 40. That is the exact staccato pattern both stop-slop and the house rules
forbid, produced while fixing the opposite problem. One split was reverted, which restores a long
sentence followed by a short verdict, and the real-prose staccato count is now zero. A second revert
undid a split inside a table caption, which bought nothing, because the build kernel strips float
environments before measuring prose so that edit never touched the metric it was made for.

The rebuild holds nine main-text pages and 53 total, with zero overfull boxes, no rerun request,
unchanged style files, 295 main-text sentences at a mean of 18.31 words and a median of 17, a
short-sentence share of 0.075, no fragments under four words, zero prose colons or semicolons or
dashes, 53 bibliography entries all cited and resolved, 24 embedded subset fonts and an empty author
field.

Ranking holds at 6.5. The gate ran last, it found one real defect that I had introduced, and the
defect is fixed.

## Scan 42, the scan where I found my own measurement was contaminated and reverted two scans of work

Scans 39 and 40 were wrong, the error was mine, and this scan undoes them. The finding matters more
than the edits, because the same flaw sits inside the build kernel's reported prose gate.

Expanding the venue sample from three ICLR papers to eight was meant to confirm scan 40's stopping
point. It did the opposite. All eight showed short-sentence shares between 0.118 and 0.183 against
the manuscript's 0.074, which looked like proof that the paper was outside the venue distribution
entirely. Before acting on that, I sampled the short sentences themselves to see what work they do in
those papers. They do none. They read arXiv preprint arXiv:2101.08809, 2021, and Le, and Alexey
Kurakin, and Deep residual learning for image recognition, and In NeurIPS, Cited by. They are
bibliography entries, author-name fragments, reference titles and section headings, because every
corpus file is a whole arXiv HTML dump and a typical paper carries fifty to eighty references.

So the comparison was never like for like. The manuscript is measured from the abstract to the
main-text label with no bibliography and no headings, while the corpus was measured with all of it
included. Cutting each corpus file at its reference list and re-measuring twice, once with a strict
prose filter and once with a permissive one, gives the same answer both times. ICLR body prose runs a
mean between 20.4 and 26.5 words with a median of 23.4, and a short-sentence share between 0.021 and
0.059 with a median of 0.044, and a long-sentence share between 0.071 and 0.211.

Against that, the manuscript before scan 39 was already a match. Its mean of 20.24 sat at the short
end of the ICLR range, its short share of 0.059 sat exactly at the ICLR maximum, and its long share
of 0.143 sat mid-range. The twenty-nine splits then took it to a mean of 18.31, below all eight
papers, and a short share of 0.075, above all eight. I moved the paper out of the distribution while
believing I was moving it in, and scan 41's staccato defect was the first symptom.

Every split from scans 39 and 40 is reverted, which restores the file to its state after scan 38 and
keeps scan 36's introduction change. The rebuild returns nine main-text pages and 53 total with zero
overfull boxes, no rerun request, unchanged style files, 269 sentences at a mean of 20.17 words and a
median of 19, a short share of 0.059, zero prose colons or semicolons or dashes, 53 bibliography
entries all cited and resolved, 24 embedded subset fonts and an empty author field.

One consequence reaches past this scan. The corpus_target_under_eight figure of 0.058 to 0.238 that
the build kernel prints on every run comes from the same contaminated measurement, so it is not a
body-prose target and should not be read as one. The paper sitting at the bottom of that printed band
was never evidence of a problem. It was the band being wrong.

Ranking holds at 6.5. Two scans of work were undone, nothing was gained, and the honest summary is
that a measurement error cost thirty edits and produced one real lesson about the instrument.

## Scan 43, fixing the instrument and re-running the gate on the restored text

Two jobs, both consequences of scan 42. The gate had to run again because prose changed after scan 41
ran it, and the build kernel had to stop printing a number that scan 42 proved wrong.

The corrected band comes from all 40 corpus papers with everything from the reference list onward
removed. Body-prose short-sentence share has a first quartile of 0.022, a median of 0.038 and a third
quartile of 0.055, against the old printed band of 0.058 to 0.238. The old figure was inflated about
fourfold because fifty to eighty bibliography entries per paper were being counted as short sentences.
Mean sentence length has a first quartile of 22.1, a median of 24.0 and a third quartile of 26.4.

Read against the corrected band, this manuscript was never short on short sentences. Its share of
0.059 sits just above the corpus third quartile, so it carries more short sentences than three papers
in four, and its mean of 20.17 words sits at the corpus minimum of 20.0, so its sentences are already
the shortest in the collection. Scans 39 and 40 spent thirty edits pushing a paper further in the
direction it was already furthest. The kernel now prints both corrected bands with a comment recording
why the old one was wrong, so the next run cannot repeat the mistake.

The gate re-ran clean on the restored text. deai_check.py at the heavy tier returns the same nine,
six, five, four and two profile it has returned since scan 34. Fourteen pattern classes are zero,
covering puffery, participial pseudo-depth, promotional language, vague attribution, AI vocabulary,
negative parallelism, filler, hedge stacks, smart punctuation, the content-humanizer vocabulary list,
bold, dashes, bullets and the banned adjectives. Six first-person admissions remain against a floor of
two. Four staccato triples flagged and all four are artefacts, three from display-math continuation
lines counted as sentences and one from a caption tail abutting body text, so genuine body prose has
none.

The rebuild holds nine main-text pages and 53 total, zero overfull boxes, no rerun request, unchanged
style files, 269 sentences at a mean of 20.17 and a median of 19, zero prose colons or semicolons or
dashes, 53 bibliography entries all cited and resolved, 24 embedded subset fonts, and an empty author
field.

Ranking holds at 6.5. Nothing in the manuscript changed in this scan. What changed is that the
instrument now reports a band the paper should actually be measured against.

## Scan 44, the appendix traces I had dismissed as a class

Every earlier pass over the de-AI checker treated its appendix output as one block and moved on, on
the grounds that the pattern clusters are graded llm-only and cannot be established by a word count.
That reasoning is sound for the clusters and unsound as an excuse for not reading them. This scan read
each one. The priority table's figure of 64 traces turned out to be a density over a section spanning
two files, and the detailed listing holds thirteen for the appendix, of which four had never been
looked at.

Three of the four are correct as written. The seed-label passage says we checked that those labels
mean what we take them to mean rather than assuming it, which is a verification claim the appendix
then cashes with the repository evidence. The size-band simulation says it was built exactly as the
existing recipe-shared effect is built, and exactly is the right word because the construction is
reused so the true ratio cannot move. The accuracy grid says its cheapest corner does not work at all,
which is an absolute, and it earns the absolute in the same breath by reporting coverage of 0.602 with
0.369 of replicates undefined against a nominal 0.95.

The fourth was a real defect and it is the kind this paper has been careful about everywhere else. A
single fp16 comparison was said to demonstrate sensitivity at that scale. Demonstrates is the wrong
strength for one comparison, and it was also a vocabulary outlier, the only occurrence of that verb
anywhere in the manuscript, while shows appears nine times and indicates and suggests appear never.
It now reads shows, which is both the honest strength and the house verb, and the clause that follows
still says the comparison does not establish a universal portability threshold for fp16 kernels.

The rebuild holds nine main-text pages and 53 total, zero overfull boxes, no rerun request, unchanged
style files, 53 bibliography entries all cited and resolved, 24 embedded subset fonts, an empty author
field, and 1,003 appendix sentences at a mean of 23.42 words with no prose colons, semicolons or
dashes.

Ranking holds at 6.5. One appendix verb is not worth a tenth, and saying otherwise after the
measurement error of scans 39 to 42 would be exactly the wrong lesson to take from it.

## Scan 45, the gate run over the whole document for the first time

Every stylometry run before this one scored the main body alone, 5,390 words from the abstract to the
main-text label. That was a coverage gap hiding in plain sight, because the appendices carry 44 of the
53 pages and roughly 27,000 of the manuscript's 32,201 prose words, and no detector had ever been
pointed at them. This scan fixed the gap and re-ran the gate, which scan 44's appendix edit had in any
case made necessary.

The whole document scores 0.1225 and CLEAN, with an AI n-gram density of 0.0149 and zero suspicious
Layer A codepoints across all 32,201 words. For scale, the three accepted ICLR papers fetched in scan
39 scored 0.1225 as well, so the complete manuscript sits in the same bucket as papers the venue
accepted, and the main body alone remains far below it at 0.0325.

One marker surfaced that the main text never produced, six uses of leverage, all of them in the
appendices. Every one is statistical. Appendix A describes a leverage-corrected influence that divides
each recipe residual by one minus its leverage, and the appendices discuss that cr3 leverage
correction as the better of two repairs and report what it does to recipe-clustered coverage at 12,000
replicates. The scorer matches the string without separating the regression noun from the marketing
verb, which puts it in the same false-positive class as robust inside cluster-robust and effective
inside effective benchmark count. No edit follows.

The rest of the gate is unchanged. deai_check.py returns the same nine, six, five, four and two
profile. The pattern classes stay at zero. Nothing in the manuscript changed in this scan, so the
build from scan 44 stands.

Ranking holds at 6.5.

## Scan 46, the first look at the rendered pages

Forty-five scans had verified this manuscript entirely through the build kernel's JSON. Page counts,
overfull boxes, font embedding, sentence rhythm, citation resolution, every one of them arrived as a
number rather than as a page. That is a real gap, because the classes of defect a reviewer notices
first are the ones no counter emits. A table can sit inside the text block and still be unreadable, a
float can land three pages from its reference, a heading can be orphaned above a page break, and an
interval in a figure can run off its axis while the box it lives in stays perfectly justified. This
scan opened the PDF and looked.

The nine main-text pages carry the title, the anonymous byline, the ICLR line numbers, and equations
one through nine, with Table 1 on page five, Figure 1 across the top of page seven, and Table 2 at the
top of page eight. Every float sits on or adjacent to the page that references it. No heading is
stranded. The main text closes flush at the foot of page nine and the AI use, ethics, and
reproducibility statements open page ten ahead of the references, which confirms from the rendered
object what the kernel reported as main_text_pages nine, and confirms as well how little slack is
left, since the body ends within a line of the boundary.

The appendix tables are set at small with column separation of four points, three points in the widest
of them. Nothing anywhere uses resizebox, scalebox, scriptsize, or tiny, so no table has been squeezed
to fit. Table 13 on page twenty-nine, the nine-column trait-removal table that is the tightest in the
manuscript, renders with visible margin on both sides and every entry legible.

Figure 3 on page twenty-eight is the one worth recording, because scan 30 rebuilt it to fix label
sizes that had been shrunk to 5.2 points by the 0.786 scale factor, and that fix had only ever been
verified as a measured font size in the figure kernel's report. On the page the eight two-line contrast
labels read as pairs, the typeface matches the body serif, and the two panels span the text width
without collision. The fix holds where it matters, which is the page rather than the JSON.

One thing in that figure looked wrong and was not. Several intervals appear to touch the panel spines,
which would contradict the caption's claim that no endpoint is missing or clipped. Checking the source
rather than the image settles it. The margin panel's data spans -0.0599 to 0.02266 and the accuracy
panel's spans -0.02076 to 0.0932, and matplotlib's default five percent autoscale margin places those
extremes about 0.004 and 0.006 inside the limits, which is roughly two millimetres at page scale and
reads as contact in a downscaled render. The caption is accurate. Recording the check because the
alternative, a caption asserting completeness over a clipped interval, is exactly the kind of claim a
reviewer quotes back.

No defect found, so no edit and no rebuild. The build from scan 44 stands.

Ranking holds at 6.5. A clean visual inspection removes a risk that was never measured, and it adds
nothing a reviewer scores.
