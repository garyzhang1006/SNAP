"""Mechanical gate for a rewritten paragraph of the SNAP main text.

usage: python3 work/style_check.py OLD.txt NEW.txt
       python3 work/style_check.py --json '{"old": "...", "new": "..."}'

Fails when the rewrite adds, drops or changes any number, citation, reference or
label command, drops an evidence-label word, introduces a colon, semicolon or
dash, leaves an uncontracted negative, or writes a sentence under eight words.
Reports the word delta and the sentence-length distribution so the page budget
and the rhythm can be judged. Exit 1 on any hard failure.
"""
import json, re, statistics as st, sys

LABELS = ['registered', 'exploratory', 'post hoc', 'added later', 'added afterwards', 'fixed before',
          'can\'t rescue', 'never', 'independently corroborated', 'exploratory', 'primary analysis',
          'nominal', 'simulat', 'held-out', 'includes one', 'excludes one', 'include one', 'exclude one',
          'reaches zero', 'reach zero']
NEG = r'\b(?:do not|does not|did not|can not|cannot|will not|is not|are not|was not|were not|have not|has not|had not|should not|could not|would not|need not|must not)\b'


def numbers(t):
    t = re.sub(r'\\ci\{([^{}]*)\}\{([^{}]*)\}', r' \1 \2 ', t)
    t = re.sub(r'\\(?:ref|eqref|label|cite[tp]?)\{[^{}]*\}', ' ', t)
    t = t.replace('{,}', ',')
    return sorted(re.findall(r'(?<![A-Za-z\\])[-+]?\d[\d,]*(?:\.\d+)?%?', t))


def commands(t):
    return sorted(re.findall(r'\\(?:ref|eqref|label|cite[tp]?|ci)\{[^{}]*\}(?:\{[^{}]*\})?', t))


def prose(t):
    # a display equation breaks the paragraph on the page, so it breaks the sentence list here too
    t = re.sub(r'\\begin\{(equation|align|algorithmic|algorithm)\}\*?.*?\\end\{\1\}', '\n\n', t, flags=re.S)
    t = re.sub(r'\\ci\{[^{}]*\}\{[^{}]*\}', ' INTERVAL ', t)
    t = re.sub(r'\$[^$]*\$', ' MATH ', t)
    t = re.sub(r'\\cite[tp]\{[^{}]*\}', ' Author (2020) ', t)
    t = re.sub(r'\\(?:ref|eqref)\{[^{}]*\}', ' 1 ', t)
    t = re.sub(r'\\label\{[^{}]*\}', '', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', '', t).replace('{', '').replace('}', '').replace('~', ' ').replace('\\%', '%')
    t = t.replace('et al.', 'et al').replace('e.g.', 'eg').replace('i.e.', 'ie')
    t = re.sub(r'(?<=\d)\.(?=\d)', 'DECIMAL', t)
    return t


def sentences(t):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\s*\n', prose(t)) if re.search(r'[A-Za-z]', s)]


def words(s):
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", s))


def check(old, new):
    hard = []
    if numbers(old) != numbers(new):
        a, b = numbers(old), numbers(new)
        hard.append(f'numbers differ: removed {sorted(set(a) - set(b))} added {sorted(set(b) - set(a))} (multiset old {len(a)} new {len(b)})')
    if commands(old) != commands(new):
        hard.append(f'commands differ: old {commands(old)} new {commands(new)}')
    lo, ln = old.lower(), new.lower()
    for lab in LABELS:
        if lab in lo and lab not in ln:
            hard.append(f'label word dropped: {lab!r}')
    p = prose(new)
    if re.search(r'[:;—–]|--', p):
        hard.append('colon, semicolon or dash in prose')
    negs = re.findall(NEG, p, re.I)
    if negs:
        hard.append(f'uncontracted negatives: {negs}')
    ss = sentences(new)
    short = [(words(s), s) for s in ss if words(s) < 8]
    if short:
        hard.append(f'sentences under eight words: {short}')
    L = [words(s) for s in ss]
    Lo = [words(s) for s in sentences(old)]
    report = {
        'hard_failures': hard,
        'words_old': words(prose(old)), 'words_new': words(prose(new)),
        'delta_words': words(prose(new)) - words(prose(old)),
        'sentences_old': len(Lo), 'sentences_new': len(L),
        'median_old': st.median(Lo) if Lo else None, 'median_new': st.median(L) if L else None,
        'over35_old': sum(x > 35 for x in Lo), 'over35_new': sum(x > 35 for x in L),
        'under12_new': sum(x < 12 for x in L),
        'so_clauses_new': len(re.findall(r', so\b', p.lower())),
        'and_the_new': len(re.findall(r', and the\b', p.lower())),
        'which_new': len(re.findall(r', which\b', p.lower())),
        'lengths_new': L,
    }
    return report


if __name__ == '__main__':
    if sys.argv[1] == '--json':
        d = json.loads(sys.argv[2]); old, new = d['old'], d['new']
    else:
        old, new = open(sys.argv[1]).read(), open(sys.argv[2]).read()
    r = check(old, new)
    print(json.dumps(r, indent=1))
    sys.exit(1 if r['hard_failures'] else 0)
