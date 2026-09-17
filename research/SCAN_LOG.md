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
