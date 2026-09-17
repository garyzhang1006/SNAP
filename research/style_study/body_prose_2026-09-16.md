# Body prose from the prior-year corpus, 2026-09-16

The two earlier collections read abstracts, which is the wrong evidence for the parts of the
manuscript a referee spends most of their time inside. This pass fetched full body text through
ar5iv for three of the twenty-one prior-year papers and read their opening introduction
paragraphs and their limitations or conclusion paragraphs, which are the two places where a
paper's honesty and its voice are most exposed. Text below is quoted verbatim from the fetched
HTML. No compute was run on this material.

## Sources read in full

- arXiv 2104.02145, Bowman and Dahl, What Will it Take to Fix Benchmarking in Natural Language
  Understanding, NAACL 2021.
- arXiv 1910.05446, Choi, Shallue, Nado, Lee, Maddison and Dahl, On Empirical Comparisons of
  Optimizers for Deep Learning, 2019.
- arXiv 2007.01547, Schmidt, Schneider and Hennig, Descending through a Crowded Valley, ICML 2021.

## What the body prose shows that the abstracts did not

**A limitations paragraph opens by naming the limit, in a plain sentence, with no cushioning
clause in front of it.** Schmidt opens with "Any empirical benchmark has constraints and
limitations." Choi opens with "Our experiments have some important limitations and we should be
careful not to overgeneralize from our results. The first major caveat is that we did not measure
the effects of varying the batch size." Neither paper spends a sentence explaining why the
limitation is acceptable before stating it, and neither hedges the verb. The manuscript's own
limitation sentences, including the one saying the planned screening split was never drawn and the
one saying the shipped proxy carries no measurable signal about a run, already follow this shape,
which is one more reason not to soften them in any later compression pass.

**Choi's construction is worth copying exactly.** A general sentence admitting the class of
limitation, then "The first major caveat is that" followed by the specific omission. The specific
omission is a thing the authors did not do, stated as a thing they did not do, with no appeal to
scope or resources. That is a stronger move than listing caveats without ranking them, because
naming a first caveat tells the referee the authors know which one matters most.

**Conclusions can open on four words.** Bowman and Dahl open theirs with "Benchmarking for NLU is
broken." The manuscript's house rule against short sentences was already reversed on corpus
evidence in an earlier scan, and this is the strongest single instance of that reversal in the
whole collection, since it sits at the top of a conclusion in a NAACL paper by two authors whose
names carry weight.

**Speculation is marked and then stated anyway.** Schmidt writes "we strongly suspect that" and
continues into a claim the data does not establish. The marking does the work. The manuscript uses
the same device in several places, and this confirms the rate is normal rather than evasive.

**Published papers in this genre carry uncorrected low-level slips.** The Schmidt ICML camera copy
contains "some of ours' and", an apostrophe on a possessive that does not take one. This is
recorded as an observation about what real accepted prose looks like, not as licence to introduce
errors. The manuscript's own text stays clean, and no slip was injected anywhere.

## What was not changed as a result

Nothing. Every pattern above is one the manuscript already follows, which is itself the finding.
The prior-year body prose supports the current draft rather than indicting it, and inventing an
edit to justify the reading time would be worse than recording that the reading produced none.
