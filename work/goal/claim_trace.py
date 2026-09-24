"""Paper-claim audit, mechanical half: every decimal in the main text (abstract to
maintext:end, floats included) is looked up among the numeric leaves of every result JSON and
CSV under results/, work/ and research/, at the paper's displayed precision. Numbers with no
match are printed with context for manual tracing."""
import json, re, csv
from pathlib import Path
R = Path(__file__).resolve().parents[2]
m = (R / "deliverables/main.tex").read_text()
body = m[m.index("\\begin{abstract}"): m.index("\\label{maintext:end}")]
vals = set()
def walk(x):
    if isinstance(x, bool): return
    if isinstance(x, (int, float)): vals.add(float(x))
    elif isinstance(x, dict): [walk(v) for v in x.values()]
    elif isinstance(x, list): [walk(v) for v in x[:20000]]
files = [p for d in ("results", "work", "research") for p in (R / d).rglob("*") if p.suffix in (".json", ".csv", ".tsv") and p.stat().st_size < 30e6]
for p in files:
    try:
        if p.suffix == ".json": walk(json.load(open(p)))
        else:
            for row in csv.reader(open(p, errors="ignore"), delimiter="\t" if p.suffix == ".tsv" else ","):
                for c in row:
                    try: vals.add(float(c))
                    except ValueError: pass
    except Exception: pass
rounded = {}
for v in vals:
    for d in (1, 2, 3, 4, 5):
        rounded.setdefault(d, set()).add(round(v, d)); rounded[d].add(round(-v, d))
        rounded[d].add(round(100 * v, d)); rounded[d].add(round(v / 100, d))
miss = []
for mt in re.finditer(r"(?<![\w.{])(-?\d+\.\d+)(?![\d])", body):
    s = mt.group(1); d = len(s.split(".")[1]); v = float(s)
    if round(v, d) not in rounded.get(d, ()):
        ln = m[: m.index("\\begin{abstract}") + mt.start()].count("\n") + 1
        miss.append((ln, s, body[max(0, mt.start() - 60): mt.end() + 20].replace("\n", " ")))
print(len(files), "files,", len(vals), "numeric leaves")
print(len(set(x[1] for x in miss)), "distinct unmatched numbers")
for x in miss: print(x[0], x[1], "|", x[2])
