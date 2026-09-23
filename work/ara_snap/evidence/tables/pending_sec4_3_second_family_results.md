# Pending - Second family and disjoint item bank results (§4.3)

**Source**: Section 4.3 "A second family and a disjoint item bank" (main.tex, label sec:family), abstract and §1 paragraph 6
**Caption**: Placeholder for the rule R1 and rule R2 results. In the source every number is a `\pending{...}` macro and every outcome sentence sits inside an `\outcome{...}` switch with `\Ronecase=0` and `\Rtwocase=0` (pending). No value or verdict below is taken from, or implied by, the source.
**Extraction type**: pending_placeholder (not a source table; no source table exists yet)

| Quantity (as named in source) | Rule | Value | Interval | Verdict |
| --- | --- | --- | --- | --- |
| R1 lambda: PolyPythias margin inflation, 45 runs, bank 1 | R1 (jackknife t(8) lower endpoint > 1) | Not available: scoring in progress | Not available: scoring in progress | Not available: scoring in progress |
| acc lambda: PolyPythias accuracy inflation | reported beside R1 | Not available: scoring in progress | Not available: scoring in progress | not read by a rule |
| Per-size jackknives (min, max, sizes) | reported beside R1 | Not available: scoring in progress | not applicable | not read by a rule |
| noBoolQ lambda: margin inflation without BoolQ | reported beside R1 | Not available: scoring in progress | Not available: scoring in progress | not read by a rule |
| cross lambda: cross-bank margin inflation (A = bank 1, B = bank 2) | R2 | Not available: scoring in progress | Not available: scoring in progress | Not available: scoring in progress |
| Within-minus-cross difference in log inflation | R2 (jackknife) | Not available: scoring in progress | Not available: scoring in progress | Not available: scoring in progress |

Fixed design facts stated in the source (not results): nine seeds at each of 14M, 31M, 70M, 160M, 410M; step 143,000; bank 1 of 37,682 items; bank 2 of 6,808 items; 40 within-configuration contrasts against 250 in DataDecide; synthetic population in the released code returns estimates between 0.94 and 1.36 around a true 1.24 at this design (stated in the pre-written R1-fail branch and in compute2/README.md).
