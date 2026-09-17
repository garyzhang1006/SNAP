import json,re,sys,time,urllib.request,html
from pathlib import Path
D=Path('corpus'); D.mkdir(exist_ok=True)
ids=json.load(open('corpus/ids.json'))
UA={'User-Agent':'Mozilla/5.0 (style-study; academic prose analysis)'}
def get(url):
    r=urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(r, timeout=90).read().decode('utf-8','ignore')
def strip(h):
    h=re.sub(r'(?is)<(script|style|math|svg|table|figure)[^>]*>.*?</\1>',' ',h)
    h=re.sub(r'(?is)<sup[^>]*>.*?</sup>',' ',h)
    h=re.sub(r'(?s)<[^>]+>',' ',h)
    return re.sub(r'[ \t]+',' ', html.unescape(h))
for title,(aid,_) in ids.items():
    base=re.sub(r'v\d+$','',aid)
    out=D/(re.sub(r'[^A-Za-z0-9]+','_',title)[:60]+'.txt')
    if out.exists() and out.stat().st_size>8000: print('have',out.name); continue
    txt=None
    for url in (f'https://arxiv.org/html/{aid}', f'https://ar5iv.labs.arxiv.org/html/{base}'):
        try:
            h=get(url); t=strip(h)
            if len(t.split())>2500: txt=t; break
        except Exception as e:
            pass
        time.sleep(2)
    if txt:
        out.write_text(txt); print(f'{len(txt.split()):7d} words  {out.name}')
    else:
        print('FAILED', title[:55])
    time.sleep(2)
