"""Collective style profile of corpus4: the twelve corpus3 papers plus nine corpus2 papers whose
acceptance was confirmed on ACL Anthology or PMLR pages on 2026-09-24 (21 accepted papers, 2017-2021),
against the SNAP main text. Derived from analyze3.py (twelve accepted 2018-2021 papers, main text only)
against the SNAP main text. Same sentence splitter as analyze2.py, with clause-join and
number-density measures added, since those are where the earlier passes found the machine tell."""
import re, statistics as st, sys
from pathlib import Path
def sentences(t):
    t=re.sub(r'\s+',' ',t)
    t=re.sub(r'\b(et al|e\.g|i\.e|cf|vs|Fig|Eq|Sec|Tab|Dr|approx|no|resp|Eqs|Figs)\.','\\1<D>',t)
    t=re.sub(r'(?<=\d)\.(?=\d)','<P>',t)
    s=[x.strip() for x in re.split(r'(?<=[.!?])\s+',t)]
    return [x for x in s if len(re.findall(r'[A-Za-z]',x))>15]
SUB=r'^(In|For|On|At|When|If|Because|Since|Although|While|As|Given|Under|With|To|After|Before|Across|Despite|Unlike|Following|Even|Once|Without|Beyond|By|From|Over|During|Whereas|Though)\b'
def stats(t,name):
    ss=sentences(t)
    pairs=[(s,len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",s))) for s in ss]
    pairs=[(s,l) for s,l in pairs if 3<=l<=120]
    if len(pairs)<60: return None
    ss=[s for s,_ in pairs]; L=[l for _,l in pairs]
    w=sum(L); n=len(L)
    per=lambda k: round(1000*k/w,2)
    share=lambda f: round(sum(1 for s in ss if f(s))/n,3)
    tl=t.lower()
    return dict(name=name, sents=n, words=w,
      mean=round(st.mean(L),1), median=st.median(L), sd=round(st.pstdev(L),1),
      under8=round(sum(1 for x in L if x<8)/n,3), under12=round(sum(1 for x in L if x<12)/n,3), over35=round(sum(1 for x in L if x>35)/n,3),
      we=per(len(re.findall(r'\bwe\b',tl))), our=per(len(re.findall(r'\bour\b',tl))),
      we_start=share(lambda s: bool(re.match(r'^(We|Our)\b',s))),
      sub_start=share(lambda s: bool(re.match(SUB,s))),
      num_sent=share(lambda s: bool(re.search(r'\d',s))),
      digits=per(len(re.findall(r'(?<![A-Za-z])\d+(?:<P>\d+)?%?',re.sub(r'(?<=\d)\.(?=\d)','<P>',t)))),
      ref_sent=share(lambda s: bool(re.search(r'\b(Figure|Fig|Table|Section|Appendix|Equation|Eq|Algorithm)\b',s))),
      cite_sent=share(lambda s: bool(re.search(r'\(\s*[A-Z][A-Za-z\-]+(?: et al)?\.?,? ?\d{4}|\[\d+\]|et al\.? \(?\d{4}',s))),
      hedge=per(len(re.findall(r'\b(may|might|could|appears?|seems?|suggests?|likely|possibly|perhaps)\b',tl))),
      find=per(len(re.findall(r'\bwe (find|found|observe|observed|see|show|note|argue|hypothesi[sz]e|expect|believe|conclude|recommend|propose|suspect|speculate)\b',tl))),
      contract=per(len(re.findall(r"\b\w+n't\b|\bit's\b|\bwe're\b|\bthat's\b",tl))),
      semicolon=per(tl.count(';')), colon=per(len(re.findall(r':(?!\d)',tl))), dash=per(tl.count('—')+tl.count('–')+tl.count(' -- ')),
      paren=per(tl.count('(')), egie=per(len(re.findall(r'\be\.g\.|\bi\.e\.',tl))),
      commas=round(sum(s.count(',') for s in ss)/n,2),
      so=per(len(re.findall(r', so\b',tl))), andthe=per(len(re.findall(r', and the\b',tl))),
      which=per(len(re.findall(r', which\b',tl))), because=per(len(re.findall(r'\bbecause\b',tl))),
      since=per(len(re.findall(r'\bsince\b',tl))), therefore=per(len(re.findall(r'\b(therefore|thus|hence)\b',tl))),
      however=per(len(re.findall(r'\bhowever\b',tl))), while_=per(len(re.findall(r'\b(while|although|whereas)\b',tl))),
      note=per(len(re.findall(r'\bnote that\b|\bnotably\b|\binterestingly\b|\bsurprisingly\b|\bin particular\b|\bfor example\b|\bfor instance\b|\bin other words\b|\bthat is\b',tl))),
      question=per(t.count('?')),
      passive=per(len(re.findall(r'\b(is|are|was|were|been|be) [a-z]+ed\b',tl))))
def snap_text(part='all'):
    root=Path('/Users/garyzhang/Documents/ChatGPT/iclr main track/deliverables')
    m=root.joinpath('main.tex').read_text()
    body=m[m.index('\\begin{abstract}'):m.index('\\label{maintext:end}')]
    if part=='intro': body=body[:body.index('\\section{Estimand')]
    body=re.sub(r'\\begin\{(table|figure|equation|align|tabular|algorithm|algorithmic)\}\*?.*?\\end\{\1\}',' ',body,flags=re.S)
    body=re.sub(r'\\ci\{([^}]*)\}\{([^}]*)\}',r'[\1, \2]',body)
    body=re.sub(r'\$[^$]*\$',' X ',body)
    body=re.sub(r'\\cite[tp]\{[^}]*\}',' Author (2020) ',body)
    body=re.sub(r'\\(?:section|subsection)\*?\{[^}]*\}','\n',body)
    body=re.sub(r'\\(?:ref|label)\{[^}]*\}',' 1 ',body)
    body=re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?','',body).replace('{','').replace('}','').replace('~',' ').replace('\\%','%')
    return body
rows=[]
C2OK=['Hitchhikers_Guide_Dror_2018','Score_Distributions_Reimers_2017','Standard_Splits_Gorman_2019','CheckList_Ribeiro_2020',
      'Fix_Benchmarking_Bowman_2021','Dynabench_Kiela_2021','Random_Search_NAS_Li_2019','Model_Stability_Seed_Madhyastha_2019','Contrast_Sets_Gardner_2020']
for p in sorted(Path('corpus3').glob('*.txt'))+[Path('corpus2')/(n+'.txt') for n in C2OK]:
    r=stats(p.read_text(errors='ignore'), p.stem[:30])
    if r: rows.append(r)
c2=[]
for p in sorted(Path('corpus2').glob('*.txt')):
    r=stats(p.read_text(errors='ignore'), p.stem[:30])
    if r: c2.append(r)
snap=stats(snap_text(),'*** SNAP main text ***'); snapi=stats(snap_text('intro'),'*** SNAP abstract+intro ***')
keys=[k for k in rows[0] if k not in ('name',)]
def fmt(v): return (f'{v:.2f}' if isinstance(v,float) else str(v)).rjust(7)
print(f"{'paper':32s}"+''.join(k[:7].rjust(7) for k in keys))
for r in rows: print(f"{r['name']:32s}"+''.join(fmt(r[k]) for k in keys))
print('-'*260)
med={k:round(st.median([r[k] for r in rows]),3) for k in keys}
lo={k:min(r[k] for r in rows) for k in keys}; hi={k:max(r[k] for r in rows) for k in keys}
med2={k:round(st.median([r[k] for r in c2]),3) for k in keys}
print(f"{'CORPUS4 MEDIAN (n=%d)'%len(rows):32s}"+''.join(fmt(med[k]) for k in keys))
print(f"{'CORPUS4 MIN':32s}"+''.join(fmt(lo[k]) for k in keys))
print(f"{'CORPUS4 MAX':32s}"+''.join(fmt(hi[k]) for k in keys))
print(f"{'corpus2 median (n=%d)'%len(c2):32s}"+''.join(fmt(med2[k]) for k in keys))
print(f"{snap['name']:32s}"+''.join(fmt(snap[k]) for k in keys))
if snapi: print(f"{snapi['name']:32s}"+''.join(fmt(snapi[k]) for k in keys))
p10={k:sorted(r[k] for r in rows)[len(rows)//10] for k in keys}; p90={k:sorted(r[k] for r in rows)[-1-len(rows)//10] for k in keys}
print(f"{'CORPUS4 P10':32s}"+''.join(fmt(p10[k]) for k in keys))
print(f"{'CORPUS4 P90':32s}"+''.join(fmt(p90[k]) for k in keys))
print('\nOUTSIDE CORPUS4 RANGE (SNAP main text):')
for k in keys:
    if k in ('sents','words'): continue
    v=snap[k]
    if v<lo[k] or v>hi[k]: print(f"  {k:10s} SNAP {v}  corpus4 median {med[k]}  range [{lo[k]}, {hi[k]}]")
