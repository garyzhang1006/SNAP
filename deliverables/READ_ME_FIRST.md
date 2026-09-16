# Revision status

This is a revised manuscript draft, not a submission-readiness certificate. The supplied PDF was the only research artifact available for this revision. Its reported experiments weren't rerun, and its promised supplementary files weren't inspected. The original PDF remains untouched.

The main text was rewritten around an exploratory study of run covariance. The revised title avoids promising unconditional removal of item-sampling error. Mathematical and interpretive corrections address the square-root expectation, covariance coefficient, jackknife arithmetic, information-ratio assumptions, noisy-gap census, training schedules, and gain simulations. The appendices retain the reported tables, the two original figures, and the 60 bibliography entries.

Use `SNAP_revised_draft.pdf` for review and `SNAP_editable_source.zip` for editing. Compile `main.tex` with pdfLaTeX at least twice, until cross-reference warnings disappear. The verified build uses pdfLaTeX from TeX Live 2026. The source package includes the unchanged official ICLR 2027 conference style and its local dependencies. It doesn't contain experimental code or data. The editorial audit is separate from the manuscript and shouldn't be uploaded as its research supplement.

## Changes that affect scientific claims

| Original claim | Correction |
|---|---|
| The permutation mean of inflation is exactly one | The squared ratio has that expectation with a fixed positive denominator. The square root doesn't inherit it. |
| The coefficient is a variance-weighted mean correlation | It is an effective covariance coefficient. Unequal marginal variances prevent the original weights from summing to one. |
| The jackknife check excludes one on accuracy | A 95% t interval calculated from the rounded reported inputs is approximately 0.998 to 1.158 and includes one. |
| The information ratio is a general empirical advantage | The calculation requires Gaussian margins and a local additive shift. Its lower planned threshold lies below the model's minimum. |
| Noisy small gaps give a lower bound on small true gaps | Measurement noise can move a gap across the threshold in either direction. The count is descriptive. |
| Matching checkpoint steps isolates seed effects | Training schedules still differ, so the full-set estimate concerns the released runs at selected steps. |
| Gain explains between 6% and 61% of the observed excess | Those percentages are outcomes from selected simulator settings, not identified causal bounds. |
| The registered study confirms or falsifies prospective predictions | The original plan lacks corroborated timing and the screening split wasn't implemented. All empirical analyses remain exploratory. |
| Accuracy benchmarks can be averaged as independent | The small full-battery estimate is conditional on weighting, item assumptions, and population. BoolQ removal and transfer results limit generalisation. |
| One predictor earns nothing over another | Reported fold means rank the models, but no paired uncertainty estimate establishes superiority or equivalence. |

The new algebra checks verified the reported subset count of 1,081,575, the accuracy upper-endpoint conversion to an effective coefficient of 0.037628 and effective count of 7.4702, and the Gaussian flip probabilities of approximately 0.2458 and 0.0845. A 100,000-population toy simulation reproduced the cross-half covariance identity within 0.0051 absolute error under its specified independent-error model. These checks aren't reproductions of the paper's empirical pipeline and haven't been added as research results.

## What still prevents a submission-ready claim

The largest scientific risk is unresolved dependence between BoolQ questions sharing a passage. BoolQ supplies 84% of the reported accuracy variance trace, and excluding it changes inflation from 1.078 to 1.558. A passage-aware split and rerun are needed to determine how much this affects the result. Deleting the caveat would weaken the paper's credibility.

The competence proxy uses a tiny floor for negative variance estimates, allowing one trait to dominate. Fixing that proxy requires an explicitly chosen measurement method and a rerun. The full-versus-rank-one comparison also needs paired fold or resampling uncertainty, with its held-out scale estimation and clipping convention accounted for. The bootstrap should be checked under relevant nonzero effects and observed influence concentration, rather than only its conditional permutation reference.

The source data, analysis code, selected-checkpoint table, and complete anonymous supplement still need verification. The paper reports those assets and execution outcomes, but a PDF assertion isn't execution evidence. The revised AI disclosure preserves the substantial AI involvement already described and adds this technical revision. Authors must verify its account of simulation work and complete the submission-form disclosure.

Author-level requirements remain outside the PDF audit. Verify the complete author list, OpenReview profiles, reviewer eligibility or exemption, submission quotas, and absence of overlapping archival submissions. Check the final supplement for names, identifying links, and metadata before upload.

## Official submission rules checked

The [ICLR 2027 author guide](https://iclr.cc/Conferences/2027/AuthorGuidelines) limits the initial main text to nine pages and requires anonymity in the manuscript and supplement. The revised main text occupies eight pages, with statements beginning on page eight and appendices after references. The conference style file is byte-identical to the [official template](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip).

Abstracts are due September 18, 2026, and full papers September 25, both at 23:59 Anywhere on Earth. The guide also specifies reciprocal-reviewing rules and author quotas, including at most one submission per author without an eligible reciprocal reviewer. Check eligibility against the actual author list rather than assuming an exemption. [Official author guide](https://iclr.cc/Conferences/2027/AuthorGuidelines)

The required AI statement and submission-form reporting follow the [ICLR 2027 AI policy](https://iclr.cc/Conferences/2027/AIPolicyForAuthors). Removing AI disclosure to make the prose appear human would conflict with that policy.

## Writing audit and score

Stop-slop and humanizer were applied through a full rewrite, an audit of the reconstructed draft, and a further revision followed by a final scan. The first reconstructed draft is retained separately in `SNAP_first_rewrite.zip`. Its remaining problems included terse equation introductions, repeated editorial framing, and dense sequences of numerical comparisons. The final revision expands the short prose sentences, removes more reconstruction commentary, and connects the comparisons to their limits.

The final editorial score is **47/50**, not 50/50.

| Dimension | Score | Evidence and remaining deduction |
|---|---:|---|
| Directness | 10 | The abstract states the design, estimates, composition sensitivity, and exploratory status without an inflated novelty claim. |
| Rhythm | 9 | Prose length varies, but long appendix passages still follow similar result-then-qualification patterns. |
| Trust | 10 | The revision exposes the missing holdout and measurement assumptions, and removes unsupported causal and equivalence claims. |
| Authenticity | 9 | The prose uses specific methodological detail and restrained interpretation. Repeated reporting constructions remain in the numerical appendix. |
| Density | 9 | Main text is shorter and the abstract has one argument. The preserved planning record and sensitivity appendix still repeat some qualifications. |

These are subjective editorial judgments, not calibrated measurements of AI authorship or acceptance probability. Further deleting technical qualifications to reach a nominal 50 would trade scientific accuracy for a score. A perfect score isn't justified by the present prose, and repeating the same rubric can't prove an absence of AI signals.

Technical uses of words such as `approximately` remain where they distinguish rounded arithmetic from an exact result. Mathematical statements retain nonhuman subjects where a forced human actor would be misleading. These are deliberate research-writing exceptions to literal stop-slop rules, not overlooked filler.

## Requested STE variant

The revision uses plain, consistent terminology and active constructions where they clarify the actor. It contracts negative auxiliaries, avoids prose colons and semicolons, and removes prose em and en dashes. With no chosen number supplied, the revision uses an eight-word minimum for prose. It imposes no maximum.

This is an **STE-informed house style**, not full ASD-STE100 conformity. [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) prohibits contractions in Rule 4.2 and limits descriptive sentences in Rule 6.3. The requested departures override those rules. No dictionary-wide STE certification was performed.

The sentence scan excludes headings, captions, table cells, references, and displayed equations, and counts inline mathematical expressions as one token. Caption labels use a period, while exact bibliographic punctuation remains. Bibliographic titles retain their original wording, including uncontracted negatives and dash punctuation, because rewriting published titles would corrupt the references.

## Verification limits

The PDF compiled successfully, its main text fits the page limit, and no overfull text boxes or undefined references remain. A text-bound check found no content outside the inspected page bounds, while rendered contact sheets and enlarged key pages were inspected for layout. PDF author metadata is empty, and a targeted search found no personal workspace path or author identifier. This doesn't verify the anonymity of an unprovided supplement.

All 60 original bibliography entries were preserved. Nine selected recent or unusual citations had matching primary-source metadata, with no fabricated entry found in that targeted check. The remaining entries and every literature interpretation haven't received an exhaustive source audit. The final pdfLaTeX build has no font-substitution, imported-PDF-version, missing-character, unresolved-citation, or overfull-box warnings. Some underfull spacing diagnostics remain and were visually inspected. These diagnostics concern unused or stretched space, rather than content overflowing its box.

The remaining substantive work requires the research artifacts, rather than another language pass. The revised draft is clearer and more defensible, but neither desk-rejection immunity nor a numerical acceptance probability can be inferred from these checks.

## Final formatting pass

The PDF now has 31 pages, including eight pages of main text. The earlier Tectonic build silently substituted Latin Modern for the requested Times-family body text and lost heading styles. The final build explicitly selects T1 font encoding and embeds the intended Times-family fonts. The official conference style remains byte-identical to the downloaded template.

The title uses a deliberate two-line break. Tables share a nine-point body, ten-point captions, booktabs rules, row spacing, and left-aligned wrapped text. Caption labels use periods. Numeric intervals use one bracket-and-spacing convention. Figures stay after their first reference, and the last appendix heading stays with its paragraph. Words never split across page boundaries, and individual bibliography entries stay on one page. The two original figure PDFs are preserved.

All 60 bibliography entries now use native natbib author-year keys and hanging indents. In-text citations and internal references resolve through LaTeX, and arXiv labels use a consistent prefix. Published titles retain their wording. British spelling is consistent in manuscript prose. No numerical token in any table changed during this formatting pass.

The final prose scan also includes equation introductions and expands citation commands before counting words. This caught short passages that the earlier scan missed. Their revisions add definitions or identify the relevant quantity, rather than adding filler. The scan remains a deterministic editorial check, not a linguistic certification.

## Additional requested style audit

A further two-pass stop-slop and humanizer revision made 36 documented edits. `STYLE_AUDIT.md` records every change and explains the retained 47/50 editorial score. `SNAP_style_pass_draft.zip` preserves its intermediate draft. No score here is an AI-authorship probability.
