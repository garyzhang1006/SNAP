"""Collect judge results from a workflow journal into CHOSEN files for review and application.

usage: python3 work/extract_judged.py JOURNAL.jsonl OUT_PREFIX

Judge agents are labelled "judge:<group>" and return {group, choice, units:[{id,new_text}],
reason, checker_summary}. The latest result per group wins. Units whose id starts with A go
to OUT_PREFIX_appendix_a.json and the rest to OUT_PREFIX_appendices_bcd.json, each entry
carrying the group name, the judge's choice and reason, so review_units.py can print them.
"""
import json, sys
from pathlib import Path
journal, prefix = sys.argv[1], sys.argv[2]
started, judged = {}, {}
for line in open(journal):
    e = json.loads(line)
    if e.get('type') == 'started':
        started[e.get('agentId')] = e.get('label') or (e.get('opts') or {}).get('label') or ''
    elif e.get('type') == 'result':
        lab = started.get(e.get('agentId'), '')
        if lab.startswith('judge:') and isinstance(e.get('result'), dict):
            judged[lab[6:]] = e['result']
out = {'appendix_a': [], 'appendices_bcd': []}
for group, r in judged.items():
    for u in r.get('units', []):
        key = 'appendix_a' if u['id'].startswith('A') else 'appendices_bcd'
        out[key].append({'id': u['id'], 'new_text': u['new_text'], 'group': group, 'choice': r.get('choice'),
                         'reason': r.get('reason', ''), 'checker_summary': r.get('checker_summary', '')})
for key, items in out.items():
    items.sort(key=lambda c: (len(c['id']), c['id']))
    p = Path(f'{prefix}_{key}.json'); p.write_text(json.dumps(items, indent=1, ensure_ascii=False))
    print(p, len(items), 'units from', len({c['group'] for c in items}), 'groups')
print('judged groups:', sorted(judged), '| choices:', {g: r.get('choice') for g, r in judged.items()})
