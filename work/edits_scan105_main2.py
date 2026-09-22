r"""Two deletions from the same flow read, held for a second reader before application:
a paragraph-closing sentence that restates its opener ("Our remaining checks leave both
verdicts in place."), and a forward pointer at the end of the primary-results paragraph
whose result is stated with numbers in the shared-passages paragraph and again in the
discussion. (A third candidate, shortening the introduction's "a comparison fixed before
any held-out score existed", was dropped because style_check reads the phrase as an
evidence label and the shorter wording weakened it.)"""
EDITS = [
('while the accuracy interval runs 0.961 to 1.184 and still includes one (Appendix~\\ref{app:supplementary}). None of these variants moves the margin interval across one or the accuracy interval off it.',
 'while the accuracy interval runs 0.961 to 1.184 and still includes one (Appendix~\\ref{app:supplementary}).'),
('That upper endpoint maps under the stated measurement model and fixed battery to $\\bar r_E<0.038$ and $K_{\\mathrm{eff}}>7.47$. The passage-aware split below moves both estimates within re-split variation.',
 'That upper endpoint maps under the stated measurement model and fixed battery to $\\bar r_E<0.038$ and $K_{\\mathrm{eff}}>7.47$.'),
]
