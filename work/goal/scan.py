"""Mechanical sub-scans of the SNAP main text, one per purpose, for the Scan 106+ series.

usage: python3 work/goal/scan.py [--appendix] [--quiet]

Each purpose prints its findings with a line number in deliverables/main.tex (or the
appendix file), so the manual sub-scans can go straight to them. The judgment purposes
(claim support, logic, reviewer attacks) are done by reading and logged in
research/SCAN_LOG.md; this script only covers what a pattern can decide.
"""
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "deliverables"
sys.path.insert(0, str(ROOT / "work"))
from style_check import sentence_units, NEG  # noqa: E402

FILES = ["main.tex"] + (["appendix_a.tex", "appendices_bcd.tex"] if "--appendix" in sys.argv else [])
BANNED = ["delve", "robust", "seamless", "leverage", "crucial", "vital", "pivotal", "holistic", "synergy", "tapestry",
          "testament", "landscape", "navigate", "journey", "unlock", "empower", "elevate", "harness", "foster", "realm",
          "game-changer", "cutting-edge", "state-of-the-art", "it's worth noting", "at the end of the day", "dive into",
          "deep dive", "utilize", "facilitate", "a wide range of", "plays a key role", "notably", "interestingly",
          "importantly", "furthermore", "moreover", "additionally", "comprehensive", "novel", "remarkabl", "significantly",
          "underscore", "showcase", "intricate", "meticulous", "paramount", "nuanced", "in conclusion", "overall,"]
# names of standard methods that contain a banned stem and are not style choices
ALLOW = ["cluster-robust", "leverage score", "hat-matrix leverage", "olmes harness"]


def prose_lines(name):
    """(line number, text) for prose paragraphs of the main text only, skipping preamble,
    floats, equations and back matter, so every finding points at text a reader sees."""
    lines = (D / name).read_text().splitlines()
    out, skip = [], name == "main.tex"
    depth = 0
    for i, l in enumerate(lines, 1):
        if name == "main.tex":
            if l.startswith("\\begin{abstract}"):
                skip = False
                continue
            if "\\label{maintext:end}" in l:
                break
        if skip:
            continue
        env = r"(table\*?|figure\*?|equation\*?|algorithm|algorithmic|tabular|align\*?)"
        if re.match(r"\s*\\begin\{" + env + r"\}", l):
            depth += 1
        if depth:
            if re.match(r"\s*\\end\{" + env + r"\}", l):
                depth -= 1
            continue
        if l.strip() and not l.startswith("%") and not re.match(r"\\(section|subsection|label|end|begin|centering|caption)", l.strip()):
            out.append((i, l))
    return out


def strip_outcomes(t):
    # keep the filled branch text of \outcome{..}{..}{label}{text} so prose checks see real sentences
    return re.sub(r"\\outcome\{[^{}]*\}\{\d\}\{[^{}]*\}\{", "{", t)


def main():
    findings = {}

    def add(p, where, msg):
        findings.setdefault(p, []).append(f"{where}: {msg}")

    all_sents = []
    for f in FILES:
        for ln, raw in prose_lines(f):
            t = strip_outcomes(raw)
            units = sentence_units(t)
            for s, exempt in units:
                w = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", s))
                all_sents.append((f, ln, s, w))
                if w < 8 and not exempt:
                    add("P01 sentence under 8 words", f"{f}:{ln}", s[:90])
                if w > 50:
                    add("P02 sentence over 50 words", f"{f}:{ln}", f"{w} words, {s[:70]}...")
            low = t.lower()
            plain = re.sub(r"\$[^$]*\$", " ", t)
            plain = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", " ", plain)
            if re.search(r"(?<![\\\d]):(?!\d)", plain) or ";" in plain or "---" in plain or "--" in re.sub(r"\d--\d", "", plain) or "—" in plain or "–" in plain:
                add("P03 colon semicolon or dash", f"{f}:{ln}", re.findall(r".{0,30}[:;—–].{0,30}|.{0,30}--.{0,30}", plain)[:2])
            for m in re.finditer(NEG, low):
                add("P04 uncontracted negative", f"{f}:{ln}", m.group(0))
            for b in BANNED:
                for m in re.finditer(r"\b" + re.escape(b), low):
                    ctx = low[max(0, m.start() - 12): m.end() + 12]
                    if not any(a in ctx for a in ALLOW):
                        add("P05 banned or marked vocabulary", f"{f}:{ln}", b)
            for pat in [r"\bnot only\b", r"\brather than\b", r"\bnot [a-z]+ but\b", r"\bisn't just\b", r"\bmore than just\b"]:
                for m in re.finditer(pat, low):
                    add("P06 contrast crutch", f"{f}:{ln}", m.group(0))
            for pat in [r"\b(may|might|could) (potentially|possibly|perhaps)\b", r"\bperhaps\b.*\bmay\b"]:
                for m in re.finditer(pat, low):
                    add("P08 hedge stack", f"{f}:{ln}", m.group(0))
            if "?" in plain:
                add("P19 question in prose", f"{f}:{ln}", plain[plain.index("?") - 40: plain.index("?") + 1])
            for m in re.finditer(r"[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]", raw):
                add("P20 invisible unicode", f"{f}:{ln}", hex(ord(m.group(0))))

    words = sum(w for *_, w in all_sents)
    per = lambda n: round(1000 * n / max(words, 1), 2)
    text = " ".join(s for _, _, s, _ in all_sents).lower()
    rates = {", so": per(len(re.findall(r", so\b", text))), ", and the": per(len(re.findall(r", and the\b", text))),
             "therefore/thus/hence": per(len(re.findall(r"\b(therefore|thus|hence)\b", text))),
             "because": per(len(re.findall(r"\bbecause\b", text))), ", which": per(len(re.findall(r", which\b", text)))}
    # maxima over the 12 verified accepted papers in research/style_study/corpus3, measured 2026-09-24
    caps = {", so": 0.88, ", and the": 0.91, "therefore/thus/hence": 1.82, "because": 1.44, ", which": 2.23}
    for k, v in rates.items():
        if v > caps[k]:
            add("P07 clause-join rate above corpus max", "main text", f"{k} {v} per 1k words, corpus max {caps[k]}")

    # P09 numbers in abstract and introduction that never recur in the body
    m = (D / "main.tex").read_text()
    front = m[m.index("\\begin{abstract}"): m.index("\\section{Estimand")]
    body = m[m.index("\\section{Estimand"):] + (D / "appendix_a.tex").read_text() + (D / "appendices_bcd.tex").read_text()
    num = lambda t: set(re.findall(r"(?<![\w.])\d+\.\d+", t))
    for n in sorted(num(front) - num(body)):
        add("P09 front-matter number absent from body", "abstract/intro", n)

    # P10 repeated 6-word phrases in the main text
    toks = re.findall(r"[a-z0-9']+", text)
    grams = {}
    for i in range(len(toks) - 5):
        g = " ".join(toks[i:i + 6])
        grams[g] = grams.get(g, 0) + 1
    for g, c in sorted(grams.items(), key=lambda x: -x[1]):
        if c >= 3 and not re.search(r"\b(interval|appendix|table|section|inflation)\b", g):
            add("P10 phrase repeated 3+ times", "main text", f"{c}x '{g}'")

    # P13 citation keys that don't exist in references.tex
    refs = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", (D / "references.tex").read_text()))
    used = set()
    for f in ["main.tex", "appendix_a.tex", "appendices_bcd.tex"]:
        for c in re.findall(r"\\cite[tp]?\{([^}]+)\}", (D / f).read_text()):
            used.update(x.strip() for x in c.split(","))
    for k in sorted(used - refs):
        add("P13 citation key missing from references", "all", k)
    for k in sorted(refs - used):
        add("P13 reference never cited", "references.tex", k)

    # P14 acronyms used before definition in the main text (first use without parentheses nearby)
    for a in ["SNAP", "OLMES", "MMLU", "GPU", "CR3"]:
        i = m.find(a, m.index("\\begin{abstract}"))
        if i > 0 and "(" not in m[i: i + 60] and a in ("SNAP",) and "Seed Noise" not in m[i - 200: i + 200]:
            add("P14 acronym first use without expansion", "main.tex", a)

    # P15 passive rate and P16 paragraph length spread and P18 sentence openers
    passive = per(len(re.findall(r"\b(is|are|was|were|been|be) [a-z]+ed\b", text)))
    L = [w for *_, w in all_sents]
    openers = {}
    for _, _, s, _ in all_sents:
        o = " ".join(s.split()[:2])
        openers[o] = openers.get(o, 0) + 1
    for o, c in openers.items():
        if c >= 5:
            add("P18 repeated sentence opener", "main text", f"{c}x '{o}'")

    print(f"main text: {len(L)} sentences, {words} words, median {st.median(L)}, sd {st.pstdev(L):.1f}, "
          f"share<12 {sum(x < 12 for x in L) / len(L):.3f}, share>35 {sum(x > 35 for x in L) / len(L):.3f}, passive {passive}/1k")
    print("clause-join rates per 1k words:", rates)
    for p in sorted(findings):
        print(f"\n[{p}] {len(findings[p])}")
        if "--quiet" not in sys.argv:
            for x in findings[p][:12]:
                print("   ", x)
    return findings


if __name__ == "__main__":
    main()
