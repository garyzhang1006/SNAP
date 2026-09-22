"""Apply judged unit rewrites to deliverables/main.tex.

usage: python3 work/apply_units.py CHOSEN.json [--dry]

CHOSEN.json is a list of {"id": "P08", "new_text": "..."}. Each id maps to the
current unit text in research/style_study/units_2026-09-21.json, which must occur
exactly once in main.tex. The checker in work/style_check.py runs on every pair
and any hard failure aborts before anything is written. A backup of main.tex is
kept at work/main.before_apply.tex on the first real run.
"""
import json, shutil, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
units = {u['id']: u for u in json.load(open(root / 'research/style_study/units_2026-09-21.json'))}
chosen = json.load(open(sys.argv[1]))
dry = '--dry' in sys.argv
tex_path = root / 'deliverables/main.tex'
tex = tex_path.read_text()
failures, total_delta, applied = [], 0, []
for c in chosen:
    u = units[c['id']]
    old, new = c.get('old_override', u['text']), c['new_text'].strip()
    if new == old:
        continue
    if tex.count(old) != 1:
        failures.append(f"{c['id']}: current text found {tex.count(old)} times in main.tex"); continue
    r = subprocess.run([sys.executable, str(root / 'work/style_check.py'), '--json', json.dumps({'old': old, 'new': new})], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    if rep['hard_failures']:
        failures.append(f"{c['id']}: {rep['hard_failures']}"); continue
    total_delta += rep['delta_words']
    applied.append((c['id'], rep['delta_words'], rep['median_old'], rep['median_new'], rep['over35_old'], rep['over35_new'], rep['so_clauses_new'], rep['which_new'], rep['and_the_new']))
    tex = tex.replace(old, new)
print('applied' if not dry else 'would apply', [a[0] for a in applied], 'net words', total_delta)
for a in applied:
    print('  %s delta %+d median %s->%s over35 %d->%d so %d which %d andthe %d' % a)
if failures:
    print('FAILURES'); [print('  ', f) for f in failures]
    sys.exit(1)
if not dry and applied:
    bk = root / 'work/main.before_apply.tex'
    if not bk.exists():
        shutil.copy(tex_path, bk)
    tex_path.write_text(tex)
    print('written', tex_path)
