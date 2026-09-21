"""Print the paper edits a 530M+750M held-out result implies.

  python3 tools/heldout_change_sheet.py outputs/k04-heldout-530m750m/heldout_results.json

Fills the placeholders in HELDOUT_WORDING.md from the k04 output and from the
fixed k06 comparison in outputs/k06-power-530m750m, decides pass or fail by the
registered rule, and lists every line in deliverables/*.tex that still reads the
530M-only result. It edits nothing, so the numbers can be checked before any
sentence changes. Runs on JSON only.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parent
K06 = HERE / "outputs" / "k06-power-530m750m"


def fmt(x):
    return f"{x:.3f}"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    res = json.loads(Path(sys.argv[1]).read_text())
    sizes = res.get("heldout_info", {}).get("sizes_scored") or res.get("heldout_info", {}).get("sizes")
    m = res["heldout"]["margin/all"]
    a = res["heldout"]["accuracy/all"]
    passed = m["lo"] > 1
    assert res["verdict"] == ("PASS" if passed else "FAIL"), (res["verdict"], m["lo"])

    power = json.loads((K06 / "power_results.json").read_text())
    subsets = json.loads((K06 / "power_subsets.json").read_text())
    four = [s for s in subsets if s["k"] == 4 and s["phenotype"] == "margin" and s.get("lambda_hat") is not None]
    below = sum(1 for s in four if s["lambda_hat"] < m["Lambda"])
    pct = round(100 * below / len(four))
    fb = power["full_battery"]["margin"]
    k4 = power["by_k"]["margin"]["4"]
    fill = {
        "{L}": fmt(m["Lambda"]), "{LO}": fmt(m["lo"]), "{HI}": fmt(m["hi"]),
        "{PCT}": f"{pct}th", "{AL}": fmt(a["Lambda"]), "{ALO}": fmt(a["lo"]), "{AHI}": fmt(a["hi"]),
    }

    print(f"sizes scored: {sizes}")
    print(f"held-out margin {fill['{L}']} [{fill['{LO}']}, {fill['{HI}']}]  ->  {'PASS' if passed else 'FAIL'}")
    print(f"held-out accuracy {fill['{AL}']} [{fill['{ALO}']}, {fill['{AHI}']}]")
    print(f"original ten at this scope: {fmt(fb['lambda_hat'])} [{fmt(fb['ci95'][0])}, {fmt(fb['ci95'][1])}]  (wording says 1.316 [0.880, 1.637])")
    print(f"four-benchmark subsets: median {fmt(k4['lambda_median'])}, share excluding one {k4['excludes_one_share']:.2f} of {k4['subsets']}, held-out at {pct}th percentile")
    print()

    wording = (HERE / "HELDOUT_WORDING.md").read_text()
    head = "## If the lower limit is above one (PASS)" if passed else "## If the lower limit is at or below one (FAIL)"
    block = wording.split(head)[1].split("\n## ")[0]
    for k, v in fill.items():
        block = block.replace(k, v)
    print(head)
    print(block.strip())
    print()

    print("lines that still read the 530M-only result:")
    pat = re.compile(r"530M|1\.198|0\.864|1\.454|1\.373|1\.138|1\.567")
    for tex in sorted((ROOT / "deliverables").glob("*.tex")):
        for i, line in enumerate(tex.read_text().splitlines(), 1):
            if pat.search(line) and re.search(r"held-out|heldout|registered|finished|Only the|subsets", line, re.I):
                print(f"  {tex.name}:{i}  {line[:110]}")


if __name__ == "__main__":
    main()
