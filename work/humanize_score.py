"""Build the prose extract of a paper file with decimals protected (1.244 -> 1p244) and score it
with the content-humanizer scorer, reporting the score and the sentence-length standard deviation."""
import json, re, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
keys = {k: f'{a.replace("~", " ")} ({y})' for a, y, k in json.loads((root / 'work' / 'citation_keys.json').read_text())}
arg = Path(sys.argv[1] if len(sys.argv) > 1 else 'main.tex')
name = arg.name
t = (arg if arg.is_absolute() else root / 'deliverables' / name).read_text()
if name == 'main.tex':
    t = t[t.index('\\begin{abstract}'):t.index('\\label{maintext:end}')]
t = re.sub(r'\\begin\{(table|figure|algorithm)\}\*?.*?\\end\{\1\}', ' ', t, flags=re.S)
# a display equation breaks the paragraph on the page, so it breaks the extract's paragraph too
t = re.sub(r'\\begin\{(equation|align)\}\*?.*?\\end\{\1\}', '\n\n', t, flags=re.S)
t = re.sub(r'\\\[.*?\\\]', ' mathematical-expression ', t, flags=re.S)
t = re.sub(r'\$[^$]*\$', ' mathematical-expression ', t)
t = re.sub(r'\\ci\{([^{}]*)\}\{([^{}]*)\}', r' [\1, \2] ', t)
t = re.sub(r'\\cite[tp](?:\[([^]]*)\])?\{([^}]+)\}', lambda m: ', '.join(keys.get(k, k) for k in m[2].split(',')), t)
t = re.sub(r'\\(?:section|subsection|subsubsection|paragraph)\*?\{[^{}]*\}', '\n\n', t)
t = re.sub(r'\\(?:label|input|Needspace)\{[^{}]*\}', '', t)
t = re.sub(r'\\(?:ref|eqref)\{[^{}]*\}', ' 1 ', t)
t = t.replace('et al.', 'et al').replace('e.g.', 'eg').replace('i.e.', 'ie')
t = re.sub(r'(?<=\d)\.(?=\d)', 'p', t)
t = re.sub(r'\\(?:begin|end)\{[^{}]*\}', '', t)
t = re.sub(r'\\[a-zA-Z]+\*?', '', t).replace('~', ' ').replace('{', '').replace('}', '').replace('\\', '')
t = re.sub(r'[ \t]+', ' ', t)
out = root / 'work' / ('extract_' + name.replace('.tex', '.txt'))
out.write_text(t)
r = subprocess.run([sys.executable, str(Path.home() / '.claude/skills/content-humanizer/scripts/humanizer_scorer.py'), str(out), '--json'], capture_output=True, text=True)
m = re.search(r'\{.*\}', r.stdout, re.S)
d = json.loads(m.group(0)) if m else {}
print(json.dumps({'file': name, 'score': d.get('humanity_score'), 'std_dev': (d.get('sentence_variance') or d.get('variance') or {}).get('std_dev'), 'breakdown': {k: v.get('score') for k, v in d.items() if isinstance(v, dict) and 'score' in v}}, indent=1))
if not m: print(r.stdout[-1500:], r.stderr[-500:])
