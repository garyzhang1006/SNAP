"""Scan 115 helper: propose splitting ", so <clause>" in an appendix file into two sentences.
A candidate qualifies only at brace depth zero, outside math, when "so" isn't "so that" or
"so far", when the sentence doesn't open with a subordinator whose scope would change, and when
both halves keep eight words. Prints candidates; --apply writes them."""
import re, sys
from pathlib import Path
f = Path(sys.argv[1]); s = f.read_text()
SUB = re.compile(r"(?:^|[.!?]\s+|\n)(If|When|Because|Since|Although|While|As|Once|Unless|Whenever)\b[^.]*$")
words = lambda t: len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", re.sub(r"\$[^$]*\$", " X ", t)))
out, i, n = [], 0, 0
for m in re.finditer(r", so (?!that\b|far\b|much\b|many\b|long\b)", s):
    pre = s[:m.start()]
    if pre.count("{") - pre.count("}") != 0 or pre.count("$") % 2: continue
    st = max(pre.rfind(". "), pre.rfind("\n"), pre.rfind(".}")) + 1
    left = pre[st:]
    rest = s[m.end():]
    en = min([k for k in (rest.find(". "), rest.find(".\n"), rest.find(".}")) if k >= 0] or [len(rest)])
    right = rest[:en]
    if SUB.search(left) or re.match(r"\s*(If|When|Because|Since|Although|While|As)\b", left): continue
    if words(left) < 8 or words(right) < 8: continue
    n += 1
    print(f"--- {n}: ...{left[-90:]} || {right[:90]}...")
    out.append((m.start(), m.end()))
if "--apply" in sys.argv:
    for a, b in reversed(out):
        nxt = s[b]
        s = s[:a] + ". " + nxt.upper() + s[b + 1:]
    f.write_text(s)
    print("applied", len(out))
