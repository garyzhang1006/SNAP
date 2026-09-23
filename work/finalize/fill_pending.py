"""Write deliverables/pythia_values.tex from the frozen compute2 analysis output.

  python work/finalize/fill_pending.py --results <dir with pythia.json and verdicts.json>

The inputs are the files compute2/analysis/estimates.py (SNAP commit 6cfedee)
writes. This script applies no rule of its own: the rule-one pass and the
rule-two verdict are read from verdicts.json as estimates.py computed them.
The two wording choices the paper fixed in advance are applied as the paper
states them: a failing rule-one estimate at or above 1.026 "bounds inflation in
this family", one below it "counts against transfer" (main.tex, Section 4.3),
and the without-BoolQ sentence says "same direction" when removing BoolQ raises
margin inflation, as it does on DataDecide (1.244 to 1.786, Figure 3 caption).

main.tex prints each value through \\res{key}{label}; keys without a value keep
their red placeholder, so rule two stays pending until bank two is scored.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRANSFER_CUT = 1.026  # 5th percentile of rule-one estimates at a true 1.244 (main.tex, Section 4.3)
R2_CASE = {"not supported": 1, "supported": 2, "undecided": 3}


def num(x, what):
    try:
        x = float(x)
    except (TypeError, ValueError):
        raise SystemExit(f"{what} is {x!r}, not a number; check the analysis output before filling the paper")
    if not math.isfinite(x):
        raise SystemExit(f"{what} is {x}; the paper was not filled, since only a lower interval endpoint may be undefined")
    return x


def f3(x):
    return f"{x:.3f}"


def lower(x, what):
    """A jackknife lower endpoint is undefined when theta's lower limit falls
    below zero; the paper prints such an endpoint as n/a (appendices_bcd.tex,
    the 1B row of the per-size table), so the same convention is used here."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        raise SystemExit(f"{what} is {x!r}, not a number; check the analysis output before filling the paper")
    return "\\mathrm{n/a}" if math.isnan(x) else f3(num(x, what))


def size_label(s):
    return s[:-1] + "M" if s.endswith("m") else s


def values(py, v):
    if py.get("status") != "ok":
        raise SystemExit(f"pythia.json status is {py.get('status')!r}: {py.get('reason') or py.get('traceback', '')[:300]}")
    vm, va = v["R1_pythia_replicates_margin"], v["R1_pythia_replicates_accuracy"]
    wb = py["within_bank1"]
    runs = wb["full"]["margin"]["all"]["N"] * wb["full"]["margin"]["all"]["R"]
    if runs != 45:
        raise SystemExit(f"rule one ran on {runs} runs, the paper describes 45; do not fill from a partial set")
    out, cases = {}, {}
    r1lam = num(vm["lambda"], "rule-one margin lambda")
    out["r1lam"], out["r1lo"], out["r1hi"] = f3(r1lam), lower(vm["lo"], "rule-one lower endpoint"), f3(num(vm["hi"], "rule-one upper endpoint"))
    out["acclam"], out["acclo"], out["acchi"] = (f3(num(va["lambda"], "accuracy lambda")),
                                                lower(va["lo"], "accuracy lower endpoint"), f3(num(va["hi"], "accuracy upper endpoint")))
    passed = bool(vm["pass"])
    cases["Ronecase"] = 1 if passed else 2
    # Compare the printed value, so a reader checking 1.026 against the text sees the same reading.
    bounds = round(r1lam, 3) >= TRANSFER_CUT
    out["r1read"] = "bounds inflation in this family" if bounds else "counts against transfer"
    out["r1readb"] = "bounds the effect in this family" if bounds else "counts against transfer"

    per = {s: num(r["margin"]["lambda"], f"{s} margin lambda") for s, r in py["within_bank1_per_size"].items()}
    if len(per) != 5:
        raise SystemExit(f"per-size estimates cover {sorted(per)}, expected five sizes")
    lo_s, hi_s = min(per, key=lambda s: per[s]), max(per, key=lambda s: per[s])
    out["szmin"], out["szminat"], out["szmax"], out["szmaxat"] = f3(per[lo_s]), size_label(lo_s), f3(per[hi_s]), size_label(hi_s)

    nb = wb["no_boolq"]["margin"]["all"]
    nbj = nb.get("jackknife", {})
    nblam = num(nb["lambda"], "without-BoolQ margin lambda")
    out["nbqlam"], out["nbqlo"], out["nbqhi"] = (f3(nblam), lower(nbj.get("lo"), "without-BoolQ lower endpoint"),
                                                 f3(num(nbj.get("hi"), "without-BoolQ upper endpoint")))
    out["nbqdir"] = ("which moves in the same direction as on DataDecide" if nblam > r1lam
                     else "which doesn't move the way it does on DataDecide")

    r2 = v.get("R2_pythia_identification_margin")
    if r2:
        cases["Rtwocase"] = R2_CASE[r2["shared_item_explanation"]]
        out["xlam"], out["xlo"], out["xhi"] = (f3(num(r2["cross_lambda"], "cross-bank lambda")),
                                            lower(r2["cross_lo"], "cross-bank lower endpoint"), f3(num(r2["cross_hi"], "cross-bank upper endpoint")))
        out["dlo"], out["dhi"] = f3(num(r2["diff_lo"], "difference lower endpoint")), f3(num(r2["diff_hi"], "difference upper endpoint"))
    return out, cases


def render(out, cases, source):
    lines = [f"% Written by work/finalize/fill_pending.py from {source}. Do not edit by hand."]
    for k, c in cases.items():
        lines.append(f"\\renewcommand{{\\{k}}}{{{c}}}")
    for k, val in out.items():
        lines.append(f"\\expandafter\\def\\csname res@{k}\\endcsname{{{val}}}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", required=True, help="directory holding pythia.json and verdicts.json from estimates.py")
    ap.add_argument("--out", default=str(ROOT / "deliverables" / "pythia_values.tex"))
    args = ap.parse_args()
    R = Path(args.results)
    py = json.loads((R / "pythia.json").read_text())
    v = json.loads((R / "verdicts.json").read_text())
    out, cases = values(py, v)
    Path(args.out).write_text(render(out, cases, R))
    print(f"wrote {args.out}: rule one {'pass' if cases['Ronecase'] == 1 else 'fail'}, "
          f"rule two {'case ' + str(cases['Rtwocase']) if 'Rtwocase' in cases else 'not in verdicts (bank two unscored), left pending'}")
    for k, val in out.items():
        print(f"  {k} = {val}")


if __name__ == "__main__":
    main()
