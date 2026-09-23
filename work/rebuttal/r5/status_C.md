# Slice C status (round 5)

Word count (raw wc -w, one \citep in each file counted as zero): orig 1181 (1180), new 1149 (1148); cap 1151.

- R5-01 (C part, format list): FIXED. Line 157 now reads "since margin correlations track scoring format (cloze for HellaSwag, PIQA and WinoGrande, yes/no for BoolQ, and multiple choice for the other six),". Source: results/snap-r5-shared-bound/r5_shared_bound.json "formats".
- R5-31: FIXED. Line 159 now reads "A permutation that reshuffles each run's item deviations inside each of the 66 item groups, MMLU's 57 subjects and the other nine benchmarks, leaves all trait scores fixed". Source: n_groups 66 in research/outputs/snap-r6-itemshare/r6_itemshare.json, and the kernel docstring (compute extra/research_kernels/snap-r6-itemshare/snap-r6-itemshare.py:17-18) sets the permutation blocks to the macro-average groups, i.e. the 57 MMLU subjects (main.tex:56) plus one group per other benchmark.
- Banked cut, line 134: FIXED. "Inflation reaches 1.244 on margins, where the raw interval excludes one, and 1.078 on accuracy, where it includes one (Table~\ref{tab:primary})." deleted; the first sentence now ends "while accuracy gives only a bound (Table~\ref{tab:primary})." Sentence first added in 88718c3 (pre-loop).
- Banked cut, line 161: FIXED. "Among equal-weight subsets of the same size, those containing BoolQ average 0.115 lower margin inflation ..." deleted; content kept at appendices_bcd.tex:206. Added in 02006c7 (pre-loop).
- Banked cut, line 161: FIXED. "The corresponding accuracy ranges run from 1.065 to 1.099 and from 1.047 to 1.115." deleted; both ranges kept at appendices_bcd.tex:191. Added in 88718c3/b69481a/4ec2ec4 (pre-loop).

All \label commands, tables and figures unchanged (label list diffed identical); no em or en dashes; no new numbers beyond 66 and 57, both already printed in the paper.
