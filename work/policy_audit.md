# ICLR 2027 policy and requested style audit

Verified against official sources on 2026-09-13. This audit covers policy and manuscript text, not submission-account status or the truth of unprovided experimental records.

## Submission requirements

The [ICLR 2027 author guide](https://iclr.cc/Conferences/2027/AuthorGuidelines) requires an abstract by September 18, 2026 and the full paper by September 25, both 23:59 Anywhere on Earth. Finalize authors by the abstract deadline. Every author needs an accurate OpenReview profile.

Initial main text must fit nine pages. References and appendices are excluded, with appendices after references. AI, ethics and reproducibility statements are excluded. Use the [official 2027 template](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip). The guide has stale wording calling ten pages the submission limit in later FAQs, so follow its explicit nine-page initial-submission rule.

Identity disclosure in paper or supplement causes desk rejection. Check code, links and PDF metadata. Each author has a 20-paper quota and at most one submission without any eligible reciprocal reviewer. Qualified authors must meet reciprocal reviewing requirements, including six reviews when submitting three or more papers. Eligibility depends on accepted publications by the abstract deadline, with an exemption for teams lacking an eligible reviewer.

Substantially overlapping archival submissions or publications violate the dual-submission policy. Nonarchival preprints are allowed. Code-of-ethics violations, false profile information and prohibited sanctioned affiliations can also trigger rejection. These author-level facts require author verification. [Author guide](https://iclr.cc/Conferences/2027/AuthorGuidelines)

## AI disclosure

The [official author AI policy](https://iclr.cc/Conferences/2027/AIPolicyForAuthors) requires a paper disclosure section and submission-form reporting. Methodology feedback, hypothesis refinement, results interpretation, theoretical assistance and implementation of methods require disclosure. Readability editing, paper drafting and literature assistance are recommended disclosure categories. This revision includes work beyond cosmetic editing and must remain disclosed.

The existing statement on page 10 lists substantial AI use. Preserve that history. The statement also asserts manual author proof derivation and citation auditing. We cannot certify those author actions from this PDF. The authors must verify them before submission. The statement denies AI-generated synthetic datasets entering reported results, while the manuscript describes synthetic coverage and artifact simulations. These facts are not inherently inconsistent, but authors must clarify whether AI contributed to simulated-data generation. The policy makes authors responsible for substantive AI-produced falsehoods or misrepresentation.

## Manuscript-specific observations and fixes

- Original main discussion ends on page 9, followed by excluded statements on page 10. Preserve this separation in the rebuilt document and verify rendered page boundaries.
- Original first page uses anonymous authors and an ICLR 2027 review header. Those visible features pass inspection, but this is not a complete anonymity audit.
- Title claims freedom from item-sampling error. Body admits conditional-independence assumptions and passage leakage. Qualify the title or opening claim so it does not imply unconditional error removal.
- Original abstract recommends treating benchmarks as independent despite an accuracy interval spanning both independence and positive inflation. Distinguish an inconclusive test from evidence establishing independence.
- Original repeatedly uses registered and pre-committed language while acknowledging no timestamp corroboration and an unimplemented split. Describe the analysis as exploratory and use a dated analysis plan without implying independently verified preregistration.
- Original disclosure claims supplied supplementary matrices and code. No supplement was included with the assigned PDF. A paper assertion cannot replace an actual anonymous supplement. Keep this as an unresolved author deliverable unless files are found and verified.
- Scientific merit and author-level compliance can still cause rejection after document formatting passes. A language score does not measure acceptance probability.

## ASD-STE100 and the requested exceptions

The official [ASD-STE100 Issue 9 PDF](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf), dated January 15, 2025, is the applicable verified source. Rule 4.2 prohibits contractions. Rule 6.3 limits descriptive sentences to 25 words, and Rule 5.1 limits procedural sentences to 20. The requested contractions and absence of a maximum therefore prevent a claim of full conformity.

Rule 8.1 prohibits semicolons and permits other standard punctuation. Avoiding prose colons is an additional house rule. Rule 3.6 favors active voice, with passive descriptive text allowed when the actor is unknown. Rules 4.1 and 6.5 favor one topic per sentence and paragraph. Rules 1.1 and 9.4 govern vocabulary and terminology consistency, including permitted technical terms.

Use an STE-informed research style with explicit user exceptions. An eight-word sentence minimum is a working assumption awaiting the user's chosen number, not an STE requirement. Exempt headings, equations, mathematical notation, table cells and bibliographic titles from prose length and punctuation checks. Preserve technical terms, assumptions and exact numerical meaning. Avoid forcing a human actor into mathematical statements when that changes their meaning.

## Limits on the requested 50/50 score

Stop-slop defines five subjective editorial dimensions, not a calibrated AI detector. Repeated passes can address examples, but cannot prove the absence of AI authorship signals or justify a perfect score by iteration alone. Report each dimension with concrete evidence and deduct points for remaining dense or formulaic passages. If a final score is below 50, state it. An unsupported 50/50 would violate the requested candor.
