"""Cut a LaTeX file into paragraph units for the register rewrite.

usage: python3 research/style_study/cut_units.py deliverables/appendix_a.tex A research/style_study/units_appendix_a.json

A unit is one prose paragraph (text between blank lines) with any display
equation that sits inside it, labels included, so that a unit's text occurs
verbatim in the source and can be replaced as a block. Floats (table, figure,
algorithm) and headings are skipped, and the enclosing section and subsection
titles are recorded for grouping. Units under 25 words (lead-ins, captions
left outside floats) are kept but flagged short so writers leave them alone.
"""
import json, re, sys
from pathlib import Path

src, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
text = Path(src).read_text()
# blank out floats and comments, preserving newlines so offsets stay stable
def blank(m):
    return re.sub(r'[^\n]', ' ', m.group(0))
masked = re.sub(r'\\begin\{(table|figure|algorithm|tabular|longtable)\*?\}.*?\\end\{\1\*?\}', blank, text, flags=re.S)
masked = re.sub(r'(?m)^%.*$', lambda m: ' ' * len(m.group(0)), masked)
units, section, subsection = [], '', ''
pos = 0
for chunk in re.split(r'\n[ \t]*\n', masked):
    start = masked.index(chunk, pos); pos = start + len(chunk)
    raw = text[start:start + len(chunk)]
    if not chunk.strip():
        continue
    head = re.match(r'\s*\\(sub)?section\*?\{([^}]*)\}', chunk)
    body = raw
    if head:
        if head.group(1):
            subsection = head.group(2)
        else:
            section, subsection = head.group(2), ''
        # a paragraph may start on the line after the heading inside the same chunk
        body = raw
        while True:
            m = re.match(r'\s*\\(sub)?section\*?\{([^}]*)\}[ \t]*\n?|\s*\\label\{[^}]*\}[ \t]*\n?', body)
            if not m:
                break
            if m.group(2) is not None:
                if m.group(1):
                    subsection = m.group(2)
                else:
                    section, subsection = m.group(2), ''
            body = body[m.end():]
        if not body.strip():
            continue
    body = body.strip('\n')
    if body != raw.strip('\n') and text.count(body) != 1:
        body = raw.strip('\n')
    prose = re.sub(r'\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}', ' ', body, flags=re.S)
    prose = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*', ' ', prose)
    words = len(re.findall(r'[A-Za-z]{2,}', prose))
    if words < 8 or text.count(body) != 1:
        continue
    units.append({'id': f'{prefix}{len(units) + 1:02d}', 'section': section, 'subsection': subsection,
                  'words': words, 'short': words < 25, 'text': body})
Path(out).write_text(json.dumps(units, indent=1, ensure_ascii=False))
print(out, len(units), 'units,', sum(u['words'] for u in units), 'words,', sum(u['short'] for u in units), 'short')
for u in units:
    print(f"  {u['id']} {u['words']:4d}w  {u['section'][:28]:28s} | {u['subsection'][:30]:30s} | {u['text'][:60].replace(chr(10), ' ')!r}")
