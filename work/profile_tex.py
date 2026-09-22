"""Sentence and clause-join profile of a LaTeX file, comparable across passes.

usage: python3 work/profile_tex.py deliverables/appendix_a.tex [more files]

Floats, comments, display mathematics and headings are removed before splitting with
work/style_check.py's sentence splitter. Rates are per thousand words. Corpus3 medians
from research/style_study/analyze3.py for the same markers: sd 14.1, under12 0.11,
over35 0.17, we 15.2, our 4.44, ", so" 0, ", and the" 0.57, ", which" 0.97,
while/although/whereas 1.41, However 1.04, parentheses 24.2, passive 5.79.
"""
import re, statistics as st, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'work'))
from style_check import sentences, words
def prose(t):
    if '\\begin{abstract}' in t and '\\label{maintext:end}' in t:
        t = t.split('\\begin{abstract}')[1].split('\\label{maintext:end}')[0]
    t = re.sub(r'(?m)^%.*$', '', t)
    t = re.sub(r'\\begin\{(table|figure|algorithm|tabular|longtable)\*?\}.*?\\end\{\1\*?\}', ' ', t, flags=re.S)
    t = re.sub(r'\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}', ' ', t, flags=re.S)
    t = re.sub(r'\\(?:section|subsection|subsubsection|paragraph)\*?\{[^{}]*\}', ' ', t)
    return t
for f in sys.argv[1:]:
    p = prose(Path(f).read_text())
    S = sentences(p); L = [words(s) for s in S]; n = len(L); W = sum(L) or 1
    low = p.lower(); kw = lambda pat: 1000 * len(re.findall(pat, low)) / W
    print(f'{Path(f).name}: {n} sentences, {W} words, median {st.median(L)}, mean {st.mean(L):.1f}, sd {st.pstdev(L):.1f}, '
          f'under12 {sum(x < 12 for x in L)/n:.2f}, over35 {sum(x > 35 for x in L)/n:.2f}, longest {max(L)}')
    print(f'  per kw: we {kw(r"\bwe\b"):.2f}, our {kw(r"\bour\b"):.2f}, ", so" {kw(r", so\b"):.2f}, ", and the" {kw(r", and the\b"):.2f}, '
          f'", which" {kw(r", which\b"):.2f}, while-family {kw(r"\b(while|although|whereas)\b"):.2f}, however {kw(r"\bhowever\b"):.2f}, '
          f'paren {1000 * p.count("(") / W:.2f}, passive {kw(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b"):.2f}, contractions {kw(r"\w'(t|s|re|ve|ll|d)\b"):.2f}')
