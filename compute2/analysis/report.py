"""Render results/*.json into results/RESULTS.md.

  python analysis/report.py --results results
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def f3(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "n/a"
    return "nan" if not np.isfinite(x) else f"{x:.3f}"


def iv(row, key):
    r = row.get(key, {})
    if "lo" not in r:
        return f"n/a ({r.get('error', 'not computed')[:60]})" if r else "n/a"
    return f"[{f3(r['lo'])}, {f3(r['hi'])}]"


def block_table(blk, kind, contrasts=("all",)):
    lines = ["| battery | phenotype | contrast | Lambda | K_eff | primary interval | wild (recipe/size) | cluster t | config boot |",
             "|---|---|---|---|---|---|---|---|---|"]
    for battery in ("full", "no_boolq"):
        for name in ("margin", "accuracy"):
            for w in contrasts:
                row = blk[battery][name].get(w)
                if not row:
                    continue
                prim = "jackknife" if kind == "pythia" else "wild"
                lines.append(f"| {battery} | {name} | {w} | {f3(row['lambda'])} | {f3(row['k_eff'])} | "
                             f"{iv(row, prim)} | {iv(row, 'wild')} | {iv(row, 'cluster_t')} | {iv(row, 'config_boot')} |")
    return "\n".join(lines)


def diff_line(d):
    if "lo" not in d:
        return f"{f3(d.get('point_log_theta_diff'))} ({d.get('error', 'no interval')})"
    return f"{f3(d['point_log_theta_diff'])} [{f3(d['lo'])}, {f3(d['hi'])}] on log theta (halve for log Lambda)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(HERE.parent / "results"))
    args = ap.parse_args()
    R = Path(args.results)
    load = lambda n: json.loads((R / f"{n}.json").read_text()) if (R / f"{n}.json").exists() else {}
    ver, py, dd, v = load("verify"), load("pythia"), load("datadecide"), load("verdicts")
    md = ["# compute2 results", "",
          "Every number below is exploratory and post hoc with respect to the paper's registration; "
          "the reading rules were fixed in README.md before any run was scored.", ""]
    md += ["## Verification gate", ""]
    if ver.get("status") == "ok":
        md += [f"Pass: **{ver['pass']}**", "", "| run | items | median abs diff | p99 abs diff | correct agreement | mode | pass |", "|---|---|---|---|---|---|---|"]
        for k, r in ver["runs"].items():
            if "error" in r:
                md.append(f"| {k} | | | | | | {r['error']} |")
            else:
                md.append(f"| {k} | {r['items']} | {r['median_abs_diff_nats_per_byte']:.5f} | {r['p99_abs_diff_nats_per_byte']:.5f} | {r['correct_agreement']:.4f} | {r['mode']} | {r['pass']} |")
    else:
        md.append(f"Not run: {ver.get('reason', ver.get('traceback', 'no result'))}")
    md += ["", "## PolyPythias, nine seeds per size at one matched step, the paper's items and prompts", ""]
    if py.get("status") == "ok":
        md += [f"Items {py['items']}, final step {py['final_step']}, split {py['split']}.", "",
               "### Within bank 1 (the paper's design on the replicate family)", "", block_table(py["within_bank1"], "pythia"), ""]
        md += ["Per size (one configuration, nine seeds, jackknife):", "", "| size | margin Lambda | jackknife | accuracy Lambda | jackknife |", "|---|---|---|---|---|"]
        for s, r in py["within_bank1_per_size"].items():
            md.append(f"| {s} | {f3(r['margin']['lambda'])} | {iv(r['margin'], 'jackknife')} | {f3(r['accuracy']['lambda'])} | {iv(r['accuracy'], 'jackknife')} |")
        if py.get("cross_bank", {}).get("summary"):
            md += ["", "### Cross-bank (A = every bank-1 item, B = every bank-2 item, same runs)", "", block_table(py["cross_bank"], "pythia"), "",
                   "### Within bank 2 (halves of the disjoint items)", "", block_table(py["within_bank2"], "pythia"), "",
                   "Within-bank-1 minus cross-bank, delete-one-seed jackknife:", ""]
            for name in ("margin", "accuracy"):
                md.append(f"- {name}, full battery: {diff_line(py['within_minus_cross'][name]['full'])}")
                md.append(f"- {name}, without BoolQ: {diff_line(py['within_minus_cross'][name]['no_boolq'])}")
        else:
            md.append(f"\nCross-bank not run: {py.get('cross_bank', {}).get('reason')}")
        if py.get("cross_format", {}).get("summary"):
            md += ["", "### Cross-format (A = five-shot bank 1, B = zero-shot bank 2)", "", block_table(py["cross_format"], "pythia"), ""]
            for name in ("margin", "accuracy"):
                md.append(f"- within minus cross-format, {name}: {diff_line(py['within_minus_crossformat'][name])}")
        if py.get("curve", {}).get("per_step"):
            md += ["", "### Across training, every configuration at one matched step", "",
                   "| step | margin Lambda | jackknife | without BoolQ | accuracy Lambda | jackknife |", "|---|---|---|---|---|---|"]
            for step, r in sorted(py["curve"]["per_step"].items(), key=lambda kv: int(kv[0])):
                md.append(f"| {step} | {f3(r['margin']['lambda'])} | {iv(r['margin'], 'jackknife')} | {f3(r['margin']['no_boolq_lambda'])} | {f3(r['accuracy']['lambda'])} | {iv(r['accuracy'], 'jackknife')} |")
            md += ["", "Pooled over steps (configuration = size at step, cluster = size):", "", block_table(py["curve"]["pooled_over_steps"], "pythia")]
    else:
        md.append(f"Not run: {py.get('reason', py.get('traceback', 'no result'))}")
    md += ["", "## DataDecide, 375 runs, bank 1 from the release and bank 2 scored here", ""]
    if dd.get("status") == "ok":
        rep = dd["reproduction"]
        md += [f"Matched runs {dd['matched_runs']} of {dd['scored_runs']} scored; bank-2 items {dd['bank2_items']}. "
               f"Reproduction of the paper on bank 1: margin {f3(rep['margin_lambda'])} (paper {rep['paper']['margin']}), "
               f"accuracy {f3(rep['accuracy_lambda'])} (paper {rep['paper']['accuracy']}), matches: {rep['matches_paper']} over {rep['n_config']} configurations.", "",
               "### Within bank 1 (reproduction)", "", block_table(dd["within_bank1_reproduction"], "datadecide", ("all", "batch_free")), "",
               "### Cross-bank", "", block_table(dd["cross_bank"], "datadecide", ("all", "batch_free")), "",
               "### Within bank 2 (fresh items, the paper's design)", "", block_table(dd["within_bank2"], "datadecide", ("all", "batch_free")), "",
               "Differences, recipe-cluster percentile bootstrap:", ""]
        for name in ("margin", "accuracy"):
            md.append(f"- within-bank-1 minus cross-bank, {name}: {diff_line(dd['within_minus_cross'][name])}")
            md.append(f"- within-bank-2 minus cross-bank, {name}: {diff_line(dd['within2_minus_cross'][name])}")
        md += ["", "Per size band:", "", "| size | mode | margin Lambda | wild | accuracy Lambda | wild |", "|---|---|---|---|---|---|"]
        for s, modes in dd["per_size"].items():
            for mode, r in modes.items():
                md.append(f"| {s} | {mode} | {f3(r['margin']['lambda'])} | {iv(r['margin'], 'wild')} | {f3(r['accuracy']['lambda'])} | {iv(r['accuracy'], 'wild')} |")
        if dd.get("cross_format_1B", {}).get("summary"):
            md += ["", "### Cross-format at 1B (five-shot bank 1 x zero-shot bank 2)", "", block_table(dd["cross_format_1B"], "datadecide", ("all", "batch_free")),
                   "", f"- within-bank-1 minus cross-format, margin: {diff_line(dd['cross_format_1B']['within1_minus_crossformat_margin'])}"]
    else:
        md.append(f"Not run: {dd.get('reason', dd.get('traceback', 'no result'))}")
    md += ["", "## Verdicts under the pre-specified reading rules", "", "```json", json.dumps(v, indent=1, default=float), "```", ""]
    (R / "RESULTS.md").write_text("\n".join(md))
    print(f"wrote {R / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
