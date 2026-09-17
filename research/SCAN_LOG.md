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
