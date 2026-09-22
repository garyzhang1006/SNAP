"""Apply exact old-to-new prose edits to deliverables/main.tex under the style gate.

usage: python3 work/apply_edits.py EDITS.py [--dry] [--tex PATH] [--backup PATH]

EDITS.py defines EDITS, a list of (old, new) string pairs. Each old string must
occur exactly once in main.tex. Every pair runs through work/style_check.py and
any hard failure aborts before anything is written. The first real run keeps a
backup at work/main.before_edits.tex. Both modes print the sentence-length
profile of the resulting main text so the rhythm can be judged before a build.
"""
import importlib.util, json, re, shutil, statistics as st, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'work'))
from style_check import sentences, words
spec = importlib.util.spec_from_file_location('edits', sys.argv[1])
assert spec is not None and spec.loader is not None, sys.argv[1]
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
dry = '--dry' in sys.argv
def opt(flag, default):
    return Path(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default
tex_path = opt('--tex', root / 'deliverables/main.tex')
tex = tex_path.read_text()
failures, delta, n = [], 0, 0
for old, new in mod.EDITS:
    if tex.count(old) != 1:
        failures.append(f'found {tex.count(old)} times: {old[:70]!r}'); continue
    r = subprocess.run([sys.executable, str(root / 'work/style_check.py'), '--json', json.dumps({'old': old, 'new': new})], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    if rep['hard_failures']:
        failures.append(f'{old[:60]!r}: {rep["hard_failures"]}'); continue
    delta += rep['delta_words']; n += 1
    tex = tex.replace(old, new)
main = tex.split('\\begin{abstract}')[1].split('\\label{maintext:end}')[0] if '\\begin{abstract}' in tex else tex
main = re.sub(r'\\begin\{(table|figure|algorithm)\*?\}.*?\\end\{\1\*?\}', '', main, flags=re.S)
L = [words(s) for s in sentences(main)]
print(f'{"would apply" if dry else "applied"} {n} edits, net words {delta:+d}')
print(f'sentences {len(L)} median {st.median(L)} mean {st.mean(L):.1f} sd {st.pstdev(L):.2f} under12 {sum(x < 12 for x in L)} over35 {sum(x > 35 for x in L)} over40 {sum(x > 40 for x in L)}')
p = main.lower()
print('however', len(re.findall(r'\bhowever\b', p)), ', so', len(re.findall(r', so\b', p)), ', which', len(re.findall(r', which\b', p)), ', and the', len(re.findall(r', and the\b', p)), 'while-family', len(re.findall(r'\b(while|although|whereas)\b', p)))
if failures:
    print('FAILURES'); [print('  ', f) for f in failures]
    sys.exit(1)
if not dry and n:
    bk = opt('--backup', root / 'work/main.before_edits.tex')
    if not bk.exists():
        shutil.copy(tex_path, bk)
    tex_path.write_text(tex)
    print('written', tex_path)
