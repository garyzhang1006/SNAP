"""Print judged unit rewrites next to their originals for hand verification.

usage: python3 work/review_units.py CHOSEN.json --units UNITS.json [--tex FILE] [--ids A01,A02]

For every {"id", "new_text"} in CHOSEN.json the script prints the unit id, the word
delta, the style_check verdict against the current text of the unit, a word-level
diff (deleted words in [-...-], inserted words in {+...+}), and any refuter or judge
note stored under "note" or "reason". Numbers, references and macros are frozen by the
checker, so the diff is the place to read for claim changes, lost qualifiers and
evidence-label drift, which are the things the checker can't see.
"""
import difflib, json, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
def opt(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default
chosen = json.load(open(sys.argv[1]))
units = {u['id']: u for u in json.load(open(opt('--units', root / 'research/style_study/units_2026-09-21.json')))}
tex_arg = opt('--tex')
tex = Path(tex_arg).read_text() if tex_arg else None
only = set(opt('--ids', '').split(',')) - {''}
def wdiff(a, b):
    A, B = a.split(), b.split()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if tag == 'equal':
            out.append(' '.join(A[i1:i2]))
        else:
            if i2 > i1: out.append('[-' + ' '.join(A[i1:i2]) + '-]')
            if j2 > j1: out.append('{+' + ' '.join(B[j1:j2]) + '+}')
    return ' '.join(out)
for c in chosen:
    if only and c['id'] not in only:
        continue
    u = units[c['id']]; old, new = c.get('old_override', u['text']), c['new_text'].strip()
    if new == old:
        print(f"=== {c['id']} unchanged"); continue
    r = subprocess.run([sys.executable, str(root / 'work/style_check.py'), '--json', json.dumps({'old': old, 'new': new})], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    found = f"found {tex.count(old)}x in tex" if tex is not None else ''
    print(f"=== {c['id']} {u.get('section','')[:30]} | {u.get('subsection','')[:30]} | delta {rep['delta_words']:+d} words | median {rep['median_old']}->{rep['median_new']} | {found}")
    if rep['hard_failures']:
        print('  HARD FAILURES:', rep['hard_failures'])
    for k in ('note', 'reason', 'refuter', 'judge'):
        if c.get(k): print(f'  {k}:', str(c[k])[:600])
    print('  ' + wdiff(old, new).replace('\n', ' '))
    print()
