import re,sys,time,urllib.request,html,subprocess
from pathlib import Path
D=Path('corpus2')
IDS={'1502.04585':'Ladder_Blum_Hardt_2015','1712.00409':'Scaling_Predictable_Hestness_2017','1809.01448':'Recommended_Significance_Dror_2018',
'1902.07638':'Random_Search_NAS_Li_2019','1904.04232':'Closer_Look_Fewshot_Chen_2019','1905.12580':'Model_Similarity_Mania_2019',
'1907.06902':'Worrying_Analysis_Ferrari_2019','1909.10447':'Model_Stability_Seed_Madhyastha_2019','1910.05446':'Optimizer_Comparisons_Choi_2019',
'2003.12206':'Reproducibility_Report_Pineau_2020','2004.02709':'Contrast_Sets_Gardner_2020','2004.13705':'Showing_Work_Tang_2020',
'2005.00636':'Random_Splits_Sogaard_2020','2005.04118':'CheckList_Ribeiro_2020','2007.01547':'Crowded_Valley_Schmidt_2020',
'2104.02145':'Fix_Benchmarking_Bowman_2021','2104.14337':'Dynabench_Kiela_2021','2106.00840':'IRT_Test_Sets_Vania_2021',
'2204.06815':'deep_significance_Ulmer_2022','1812.04529':'Variance_Reduced_Ineffective_Defazio_2018','1707.09861':'Score_Distributions_Reimers_2017'}
UA={'User-Agent':'Mozilla/5.0 (style-study; academic prose analysis)'}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read().decode('utf-8','ignore')
def strip(h):
    h=re.sub(r'(?is)<(script|style|math|svg|table|figure)[^>]*>.*?</\1>',' ',h)
    h=re.sub(r'(?is)<sup[^>]*>.*?</sup>',' ',h); h=re.sub(r'(?s)<[^>]+>',' ',h)
    return re.sub(r'[ \t]+',' ',html.unescape(h))
for aid,name in IDS.items():
    out=D/(name+'.txt')
    if out.exists() and out.stat().st_size>8000: print('have',name); continue
    txt=None
    for url in (f'https://arxiv.org/html/{aid}',f'https://ar5iv.labs.arxiv.org/html/{aid}'):
        try:
            h=get(url)
            if 'Introduction' in h or 'Abstract' in h:
                t=strip(h)
                if len(t)>8000: txt=t; break
        except Exception as e: print('fail',url,e)
    if txt is None:
        try:
            pdf=D/(name+'.pdf'); pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(f'https://arxiv.org/pdf/{aid}',headers=UA),timeout=120).read())
            txt=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True).stdout; pdf.unlink()
        except Exception as e: print('pdf fail',aid,e)
    if txt: out.write_text(txt); print('ok',name,len(txt))
    time.sleep(2)
for acl,name in [('P18-1128','Hitchhikers_Guide_Dror_2018'),('P19-1267','Standard_Splits_Gorman_2019')]:
    out=D/(name+'.txt')
    if out.exists(): continue
    try:
        pdf=D/(name+'.pdf'); pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(f'https://aclanthology.org/{acl}.pdf',headers=UA),timeout=120).read())
        out.write_text(subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True).stdout); pdf.unlink(); print('ok',name)
    except Exception as e: print('acl fail',acl,e)
