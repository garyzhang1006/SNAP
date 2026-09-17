import re,statistics as st
from pathlib import Path
def sentences(t):
    t=re.sub(r'\s+',' ',t)
    t=re.sub(r'\b(et al|e\.g|i\.e|cf|vs|Fig|Eq|Sec|Tab|Dr|approx|no)\.','\\1<D>',t)
    t=re.sub(r'(?<=\d)\.(?=\d)','<P>',t)
    s=[x.strip() for x in re.split(r'(?<=[.!?])\s+',t)]
    return [x for x in s if len(re.findall(r'[A-Za-z]',x))>15]
def stats(t,name):
    ss=sentences(t)
    L=[len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",s)) for s in ss]
    L=[x for x in L if 3<=x<=120]
    if len(L)<80: return None
    w=sum(L)
    per=lambda n: round(1000*n/w,2)
    low=lambda p: sum(1 for x in L if x<p)/len(L)
    tl=t.lower()
    return dict(name=name, sents=len(L), words=w,
      mean=round(st.mean(L),1), median=st.median(L), sd=round(st.pstdev(L),1),
      p10=sorted(L)[len(L)//10], p90=sorted(L)[9*len(L)//10],
      under8=round(low(8),3), under12=round(low(12),3), over35=round(sum(1 for x in L if x>35)/len(L),3),
      we=per(len(re.findall(r'\bwe\b',tl))), our=per(len(re.findall(r'\bour\b',tl))),
      hedge=per(len(re.findall(r'\b(may|might|could|appears?|seems?|suggests?|likely|possibly|perhaps)\b',tl))),
      contract=per(len(re.findall(r"\b\w+n't\b|\bdoesn|\bdon't\b|\bcan't\b|\bisn't\b|\bwe're\b|\bit's\b",tl))),
      notXbutY=per(len(re.findall(r'not (only|just|merely)\b|\bnot \w+,? but\b',tl))),
      semicolon=per(tl.count(';')), colon=per(tl.count(':')), dash=per(tl.count('—')+tl.count(' -- ')),
      however=per(len(re.findall(r'\bhowever\b',tl))), thus=per(len(re.findall(r'\bthus\b',tl))),
      note_that=per(len(re.findall(r'\bnote that\b',tl))),
      crucial=per(len(re.findall(r'\b(crucial|pivotal|robust|leverage|delve|comprehensive|holistic|seamless)\b',tl))),
      significant=per(len(re.findall(r'\bsignificant(ly)?\b',tl))),
      passive=per(len(re.findall(r'\b(is|are|was|were|been|be) [a-z]+ed\b',tl))))
rows=[]
for p in sorted(Path('corpus').glob('*.txt')):
    r=stats(p.read_text(errors='ignore'), p.stem[:34])
    if r: rows.append(r)
# SNAP
root=Path('/Users/garyzhang/Documents/ChatGPT/iclr main track/deliverables')
m=root.joinpath('main.tex').read_text()
body=m[m.index('\\begin{abstract}'):m.index('\\label{maintext:end}')]
body=re.sub(r'\\begin\{(table|figure|equation|align|tabular)\}\*?.*?\\end\{\1\}',' ',body,flags=re.S)
body=re.sub(r'\$[^$]*\$',' X ',body); body=re.sub(r'\\ci\{[^}]*\}\{[^}]*\}',' X ',body)
body=re.sub(r'\\cite[tp]\{[^}]*\}',' Author (2020) ',body)
body=re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?','',body).replace('{','').replace('}','').replace('~',' ')
snap=stats(body,'*** SNAP (this paper) ***')
keys=['sents','mean','median','sd','p10','p90','under8','under12','over35','we','our','hedge','contract','notXbutY','semicolon','colon','dash','however','thus','note_that','crucial','significant','passive']
print(f"{'paper':36s} "+' '.join(k[:7].rjust(7) for k in keys))
for r in rows: print(f"{r['name']:36s} "+' '.join(str(r[k]).rjust(7) for k in keys))
print('-'*250)
import statistics as S
med={k:round(S.median([r[k] for r in rows]),3) for k in keys}
print(f"{'CORPUS MEDIAN (n=%d)'%len(rows):36s} "+' '.join(str(med[k]).rjust(7) for k in keys))
print(f"{snap['name']:36s} "+' '.join(str(snap[k]).rjust(7) for k in keys))
