r"""Post-refutation touch-ups on the Scan 104 main text: two merged sentences that
ended as X, and Y, and Z chains are split again at their original boundary."""
EDITS = [
("and lowers the aggregate standard deviation on both scales, and a larger factor accompanies a less variable average.",
 "and lowers the aggregate standard deviation on both scales. A larger factor accompanies a less variable average."),
("We added a noise level of 2.00 after seeing the two-size width, and its median width is 0.640, close to the observed held-out width, and at that level the rule passes in 0.262 of replicates at a true 1.244 against a size of 0.025.",
 "We added a noise level of 2.00 after seeing the two-size width, and its median width is 0.640, close to the observed held-out width. At that level the rule passes in 0.262 of replicates at a true 1.244 against a size of 0.025."),

# refuter round on the two post-refutation merges: pair A reverted, pair B kept with the comma the refuter asked for,
# and the pronoun it in the scaled-error sentence replaced by a noun on the refuter's antecedent finding
("Out of sample on margins, independence predicts a configuration's measured ratio with a mean absolute log error of 0.339 against 0.536 for the plug-in and 0.512 for our decomposition (Appendix~\\ref{app:transport}), and our estimated ratio is therefore a measurement of this battery and helps only where replicates are missing and the target battery's own ratio is close.",
 "Out of sample on margins, independence predicts a configuration's measured ratio with a mean absolute log error of 0.339 against 0.536 for the plug-in and 0.512 for our decomposition (Appendix~\\ref{app:transport}). Our estimated ratio is therefore a measurement of this battery and helps only where replicates are missing and the target battery's own ratio is close."),
("but because we chose it after seeing four of the cells we report the shipped interval throughout",
 "but because we chose it after seeing four of the cells, we report the shipped interval throughout"),
("and carried to a battery whose own ratio is 1.5, it leaves the error at 0.101.",
 "and carried to a battery whose own ratio is 1.5, the same scaling leaves the error at 0.101."),
]
