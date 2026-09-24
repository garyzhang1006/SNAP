"""STE rule 6.2: split appendix paragraphs longer than six sentences.
A split point is a sentence boundary at brace depth zero, outside math, and the next sentence must not open
with a word that points back (This, These, It, Its, The same, ...), so each new paragraph starts on its own
subject. Chunks stay at six sentences or fewer and at two or more.
usage: python3 work/goal/split_paras.py FILE [--apply]"""
import re
import sys
from pathlib import Path

ANAPH = re.compile(r"(This|These|That|Those|It|Its|They|Their|Them|Both|Such|The same|Here|There|Also|However|"
                   r"Neither|Either|Each of these|Together|Instead|Otherwise|So|Then|Thus|Therefore|Hence)\b")
f = Path(sys.argv[1])
lines = f.read_text().split("\n")


def boundaries(s):
    out, depth, math = [], 0, False
    for i, ch in enumerate(s):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == "$":
            math = not math
        if ch == "." and depth == 0 and not math and s[i + 1:i + 2] == " " and i + 2 < len(s):
            nxt = s[i + 2:]
            prev = s[max(0, i - 6):i + 1]
            if re.match(r"[A-Z\\]", nxt) and not re.search(r"(al|e\.g|i\.e|cf|vs|Fig|Eq|No)\.$", prev):
                out.append(i + 1)
    return out


env_depth, changed = 0, 0
for k, l in enumerate(lines):
    if re.match(r"\s*\\begin\{(table|figure|equation|align|tabular|algorithm)", l):
        env_depth += 1
    if re.match(r"\s*\\end\{(table|figure|equation|align|tabular|algorithm)", l):
        env_depth -= 1
        continue
    if env_depth or l.startswith("%") or not l.strip():
        continue
    b = boundaries(l)
    n = len(b) + 1
    if n <= 6:
        continue
    chunks = -(-n // 6)
    ideal = [round(n * j / chunks) for j in range(1, chunks)]
    cuts = []
    for t in ideal:
        best = None
        for d in (0, 1, -1, 2, -2):
            j = t + d
            if 2 <= j <= n - 2 and (not cuts or j - cuts[-1] >= 2) and (j - (cuts[-1] if cuts else 0)) <= 6:
                pos = b[j - 1]
                if not ANAPH.match(l[pos + 1:]):
                    best = j
                    break
        if best is None:
            print(f"--- line {k + 1}: {n} sentences, no clean split near sentence {t}")
            cuts = None
            break
        cuts.append(best)
    if not cuts or n - cuts[-1] > 6:
        if cuts is not None:
            print(f"--- line {k + 1}: {n} sentences, tail too long")
        continue
    new = l
    for j in reversed(cuts):
        pos = b[j - 1]
        new = new[:pos] + "\n\n" + new[pos + 1:]
    print(f"+++ line {k + 1}: {n} sentences split at {cuts}: ...{l[b[cuts[0] - 1] - 60:b[cuts[0] - 1] + 60]}...")
    lines[k] = new
    changed += 1
if "--apply" in sys.argv:
    f.write_text("\n".join(lines))
print("split", changed)
