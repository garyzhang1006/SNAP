# Round 8 hostile review: diff 7bb3d2c..39e53bb (main.tex, appendices_bcd.tex)

Every number in the diff matches its source JSON under half-up rounding, with one wrong claim (R8-4). I checked the counts with python3 on the JSON, and the t tail masses with scipy. The prose passes the rules: the added lines have no em or en dashes, none of the banned words and no "not X but Y" contrasts. The findings below are ranked most severe first.

---

## R8-1 (likely to lower score): the main-text null-pair sentence reads as the DataDecide rule's real false-positive rate, and it picks the one favourable contrast

Quote, main.tex:222: "On null pairs of PolyPythias seeds both rules call 0.133 of single-seed margin pairs against a nominal 0.046, and when all nine seeds estimate the deviation the corrected rule calls 0.050 against 0.122 under independence (Appendix~\ref{app:decision})."

Problem: the sentence comes right after the DataDecide decision rates, so a reader takes 0.133 as the error rate of that rule. The DataDecide rule, though, estimates its deviation from 23 recipes with three runs each. Here each deviation comes from one configuration's seven held-out seeds (six degrees of freedom), or from three seeds for triples. A reviewer would weaponise the sentence in three ways:
- In the only real-data null test, the correction gives no gain in held-out error control: both rules land at 0.133 and differ on 14 pairs, seven each way.
- For three-run comparisons, which match DataDecide's R=3, the corrected margin rule is worse: 0.218 against 0.193. The main text leaves this out.
- The only favourable contrast (0.050 against 0.122) uses a deviation that includes the tested pair. That makes the statistic self-studentised and conservative, and moving from seven seeds to nine swings the corrected rate from 0.133 to 0.050, which shows these rates are dominated by estimation noise.

Together these undercut the abstract's 0.113-against-0.05 motivation (main.tex:29, main.tex:33) and the plug-in claim that the corrected rate returns to 0.051 (main.tex:241, appendices_bcd.tex:218). Those claims rest on a ratio estimated from a large population, which is a different regime from these per-configuration deviations.

Evidence: r5_07_null_pairs.json results.margin:
- single_run pooled: independence 24/180 and corrected 24/180, with 7 calls dropped by the correction and 7 added.
- three_run pooled: independence 808/4190 = 0.193 and corrected 861/3950 = 0.218.
- in_sample_reference pooled: independence 22/180 = 0.122 and corrected 9/180 = 0.050.

The design docstring states that the DataDecide rule leaves the pair out and that the null check uses N = 1.

Replacement (36 words, same count): "On PolyPythias null seed pairs, with deviations from the other seven seeds of one configuration, both rules call 0.133 of margin pairs against a nominal 0.046, or 0.092 for $t$ with six degrees of freedom (Appendix~\ref{app:decision})."

---

## R8-2 (likely to lower score): "so a not-supported verdict can't rule such a component out" does not follow from the numbers and contradicts the R2 outcome text

Quotes: main.tex:203, "At a share of 0.755, which alone gives 1.244 on this noise, the second rule returns supported in 0.067 and undecided in 0.919, so a not-supported verdict can't rule such a component out." Also appendices_bcd.tex:351, "The second rule therefore rarely detects a shared component large enough to explain the inflation, and a verdict of not supported can't exclude one."

Problem: the conclusion is about the not-supported verdict, but the sentence gives only the supported and undecided rates. The omitted rate points the other way. At the share that explains all the inflation, the rule returns not supported in 0.0145, against 0.226 under true run covariance with no share. So not supported is about 15 times likelier without the component. The \Rtwocase{1} outcome block at main.tex:211 says the difference's upper limit "bounds such a component", which contradicts the new sentence. A hostile reader sees the pre-registered rule described as unable to answer its own question. The verdict that can't exclude the component is undecided (0.919 at the share against 0.761 without it).

"Rarely detects" is supported, since supported runs from 0.026 to 0.070 across the three noise sources.

Evidence, r5_20_rule_two_share.json:
- independence_share_star "not supported": datadecide_rel_original 0.0145, pp_pooled_bank1 0.0145, pp_pooled_4755 0.0165.
- run_cov_1244_share0 "not supported": 0.22575.

Replacement, main.tex:203 (33 words, same count): "At a share of 0.755, which alone gives 1.244 on this noise, the second returns supported in 0.067, not supported in 0.015 and undecided in 0.919, so an undecided verdict can't exclude one."

Replacement, appendices_bcd.tex:351: "The second rule therefore rarely detects a shared component large enough to explain the inflation, returns not supported in at most 0.017 of replicates at that share, and an undecided verdict can't exclude one."

---

## R8-3 (moderate): the main text leaves out that rule one passes more often under a pure shared-item artifact, then says a pass "confirms the effect"

Quote, main.tex:203: "A first-rule pass confirms the effect in this family."

Problem: at share 0.755 under independence, rule one passes in 0.338. On the same draws it passes in 0.257 at a true 1.244 run covariance. A reviewer will say a rule-one pass cannot separate run covariance from a shared item component, and the paper's own new number is the evidence. Contribution (i) (main.tex:45) already says the estimand is "identified up to an item component shared across benchmarks and halves", so the sentence should name what it confirms.

Evidence: r5_20 independence_share_star rule_one_pass_rate is 0.3375 (datadecide), 0.3465 (bank1) and 0.27675 (4755). run_cov_1244_share0 is 0.257. The appendix (appendices_bcd.tex:351) reports 0.338. The main text does not.

Replacement (9 words, same count): "A first-rule pass confirms within-bank inflation in this family."

---

## R8-4 (moderate): factual error about where the largest corrected rate occurs

Quote, appendices_bcd.tex:456: "The largest single-seed margin rates come at 410M, 0.333 under independence and 0.167 corrected."

Problem: the largest corrected single-seed margin rate is at 70M, 0.222, which exceeds the 0.167 at 410M.

Evidence: r5_07 margin.single_run corrected false_positive_rate is 14m 0.111, 160m 0.083, 31m 0.083, 410m 0.167 and 70m 0.222.

Replacement: "The largest single-seed margin rates are 0.333 under independence at 410M and 0.222 corrected at 70M."

---

## R8-5 (moderate): "Part of the excess ... reflects" makes a causal claim nothing tested, and it cites only the six-df reference

Quote, appendices_bcd.tex:456: "Part of the excess in the held-out designs reflects a deviation estimated on few runs, since a $t$ reference with six degrees of freedom already puts 0.092 of its mass beyond two standard errors."

Problem: no analysis separates the degrees-of-freedom effect from anything else, so "reflects" is inferred. "Held-out designs" is plural, but the triple design estimates its deviation from three seeds, which gives two degrees of freedom. A $t$ reference with two degrees of freedom puts 0.184 beyond two standard errors, which covers most of the triple margin rates (0.193, 0.218). Citing only six degrees of freedom understates the paper's own defence. What the six-df reference leaves unexplained is the single-seed rate of 0.133 against 0.092, and the in-sample independence rate at 410M of 0.333.

Evidence: scipy gives 2*t.sf(2,6) = 0.0924 and 2*t.sf(2,2) = 0.1835.

Replacement: "The held-out designs estimate each deviation on seven or three runs, and $t$ references with six and two degrees of freedom put 0.092 and 0.184 of their mass beyond two standard errors."

---

## R8-6 (moderate): the opening of the null-pair paragraph claims to supply the false-positive rate that Table 3 lacks

Quote, appendices_bcd.tex:456: "A wrong call in Table~\ref{tab:decision} can be a genuine rank change, so the table gives no false-positive rate. PolyPythias gives one, since its nine seeds at each size rerun one recipe and any two disjoint sets of them differ only by seed."

Problem: the check gives a false-positive rate for the same threshold but a different deviation estimate. It uses one configuration and three to seven runs, on the 4,755 transfer items. The table's rule uses 23 recipes with three runs each, on the full banks. Read as written, the paragraph assigns 0.133 to the DataDecide rule, which is the setup that R8-1 describes.

Evidence: r5_07_null_pairs.py docstring, where the sigmas are "from the other 7 seeds of that configuration (N = 1, R = 7)". appendices_bcd.tex:430 says the table's deviation leaves out only the pair's two recipes.

Replacement: "A wrong call in Table~\ref{tab:decision} can be a genuine rank change, so the table gives no false-positive rate. PolyPythias gives one for the same threshold with deviations from one configuration's seeds, since its nine seeds at each size rerun one recipe and any two disjoint sets of them differ only by seed."

---

## R8-7 (minor): the split-versus-replicate result follows mechanically from the deviation ordering, and "borderline" is asserted without evidence

Quotes, appendices_bcd.tex:459: "The replicate estimate never made a call that the split withheld." And: "The two estimates part only on borderline decisions, most of them on accuracy, and the replicate deviation is the more cautious of the two."

Problem: the replicate aggregate deviation exceeds the split one in all 22 battery-by-score cells, so the one-sided disagreement follows from the thresholds and was not a discovery. The paragraph presents it as a finding. Nobody measured how far the disputed gaps sit from either threshold, and on accuracy without BoolQ the thresholds differ by 24 percent, so "borderline" is unsupported. "More cautious" is accurate. The same file supports caution: 27 of the 198 resolved extra calls disagree with 1B, which is 0.136 against the table's 0.029 to 0.070.

Evidence: r8_split_vs_rep.json sanity_lambdas_and_sigmas, where sigma_agg_replicate/sigma_agg_split runs from 1.007 to 1.014 on margins and from 1.064 to 1.243 on accuracy. The minimum threshold_replicate/threshold_split over the cases is 1.005.

Replacement for the last sentence: "The replicate deviation exceeds the split one in every battery, by about one percent on margins and 6 to 24 percent on accuracy, so it is the more cautious of the two and the decisions it changes are mostly on accuracy." In the earlier sentence, change "the removal of BoolQ adds the most on accuracy, 61" to "the battery without BoolQ has the most on accuracy, 61", because the current wording reads as an increment over the full battery.

---

## R8-8 (minor): denominators for triples that have no defined deviation go undisclosed

Quote, appendices_bcd.tex:456: "With triples the margin rates are 0.193 under independence and 0.218 corrected, and the accuracy rates are 0.296 and 0.217."

Problem: 31 percent of accuracy triples have no defined independence deviation. At 70M only 70 of 840 are defined, and those 70 call at 0.757. So the 0.296 is conditioned on a selected subset. The single-seed accuracy sentence does report its defined counts, which makes the paragraph internally inconsistent.

Evidence: r5_07 accuracy.three_run pooled has independence defined 2900 with 857 calls, and corrected defined 3310 with 718 calls. margin.three_run has corrected defined 3950.

Replacement: "With triples the margin rates are 0.193 under independence and 0.218 corrected, and the accuracy rates are 0.296 of 2,900 defined pairs and 0.217 of 3,310."

---

## R8-9 (minor): the rates carry no uncertainty

Quote, appendices_bcd.tex:456: "The check uses one configuration per size, and the pairs at one size share seeds, so its rates are exploratory."

Problem: the JSON includes a seed jackknife, but the paper reports no uncertainty, so a reader can't judge whether 0.133 against 0.046 exceeds noise. The per-size standard errors are large.

Evidence: r5_07 jackknife_single_run margin jackknife_se: independence 0.000 to 0.222 (70m) and corrected 0.042 to 0.126. There is no pooled standard error.

Replacement: "The check uses one configuration per size, the pairs at one size share seeds, and seed-jackknife standard errors of the per-size margin rates reach 0.222, so its rates are exploratory."

---

## R8-10 (minor): two nominal rates for the same two-standard-error rule

Quote, main.tex:222 and appendices_bcd.tex:456: "against a nominal 0.046". Elsewhere the paper says "against a nominal 0.05" (main.tex:29, main.tex:33, appendices_bcd.tex:218).

Problem: a reader sees the nominal rate change between sections. The value 0.046 is correct for two known standard errors (2*norm.sf(2) = 0.0455). If the 0.113 simulation also uses a two-standard-error threshold, its nominal rate is 0.046 too, and 0.05 understates the excess there.

Replacement: none needed in the diff lines. Check that the 0.113 simulation's threshold matches its stated nominal rate.

---

## R8-11 (minor): the Dirichlet reproduction sentence is accurate, but the claims it re-certifies are slightly loose

Quote, appendices_bcd.tex:204: "A rerun of the sweep from its committed script reproduces each of these figures to the third decimal."

Problem: the rerun confirms every quoted value. r8_r6_20.json paper_comparison has all matches_at_paper_precision true, with 0.8165 rounded half-up to 0.817. The nearby, pre-existing claim that accuracy "behaves in the direction that favours the reported claim" includes 4 of the 772 flat-Dirichlet accuracy intervals that exclude one from below, and 0.018 of the flat-Dirichlet accuracy draws are undefined. Neither fact is stated.

Evidence: from per_draw, accuracy dirichlet_flat has 768 intervals above one and 4 below. undefined is 0.018.

Replacement (optional): "Accuracy behaves in the direction that favours the reported claim, because 0.386 of flat-Dirichlet intervals, all but 4 of them from above, and 0.402 of near-flat ones exclude one while the flat weighting itself gives 0.993 to 1.157 and doesn't."

---

## Checked and correct (no action)

- **R5-07 (null pairs):** 36 and 840 pairs, the 0.046 nominal rate, 24/180 = 0.133, 29/142 = 0.204, 28/152 = 0.184, the triple rates 0.193, 0.218, 0.296 and 0.217, the in-sample rates 0.050, 0.122, 0.104 and 0.215, the 410M independence rate of 0.333 and the 4,755 items.
- **R5-09 (rule-one power on PolyPythias noise):**
  - The anchors are 0.257 and 0.014, which match r1_18.
  - Rule one at a true 1.244 runs from 0.205 to 0.257, and its largest pass rate under independence is 0.015.
  - The widest middle 90% runs from 0.993 to 1.488 (per size, 4,755 items).
  - The two bank-one versions pass in 0.254 and 0.257.
  - The set-to-0.5 rule matches the traits whose sigma_e2 is not positive.
- **R5-20 (rule two at the reproducing share):** the shares 0.755, 0.848 and 0.230, rule-one pass 0.338, supported and undecided 0.067/0.919, 0.070/0.916 and 0.026/0.958, and the medians 1.240 and 1.003.
- **Split versus replicate:** 16,500 pair decisions per score, 60 and 382 extra calls, 11,705/11,645 and 12,861/12,479, 4 and 25 on the full battery, 61 without BoolQ, 318/198/171, 17 of 2,200 size-step decisions and 34 of 220 seed-count cases with 26 on accuracy. Every difference goes in the direction the paper states.
- **Main text against appendix wording:** consistent apart from R8-2 (the not-supported verdict) and R8-3 (the rule-one pass rate of 0.338, which appears only in the appendix).
