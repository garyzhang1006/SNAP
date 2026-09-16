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
