"""Fetch the proceedings versions of the corpus-3 exemplars and strip them to main text.

Each entry names the venue page that establishes acceptance and the PDF that carries
the accepted text. ICLR entries use the arXiv version that matches the OpenReview camera-ready, since openreview.net refuses scripted PDF downloads, ICML entries PMLR,
EMNLP entries the ACL Anthology, and the rest the arXiv version matching the
proceedings paper. PDFs stay under corpus3/pdf. Text is cut at the references heading so appendices and
bibliographies never enter the sentence statistics.
"""
import re, sys, time, urllib.request
import pymupdf
from pathlib import Path
D = Path('corpus3')
UA = {'User-Agent': 'Mozilla/5.0 (style-study; academic prose analysis)'}
PAPERS = {
 'Melis_LM_Evaluation_ICLR2018':      'https://arxiv.org/pdf/1707.05589v2',
 'Chen_Fewshot_ICLR2019':             'https://arxiv.org/pdf/1904.04232v2',
 'Chan_RL_Reliability_ICLR2020':      'https://arxiv.org/pdf/1912.05663v2',
 'Mosbach_BERT_Stability_ICLR2021':   'https://arxiv.org/pdf/2006.04884v3',
 'Zhang_Fewsample_BERT_ICLR2021':     'https://arxiv.org/pdf/2006.05987v3',
 'Bouthillier_Unreproducible_ICML2019': 'https://proceedings.mlr.press/v97/bouthillier19a/bouthillier19a.pdf',
 'Recht_ImageNet_ICML2019':           'https://proceedings.mlr.press/v97/recht19a/recht19a.pdf',
 'Dodge_ShowYourWork_EMNLP2019':      'https://aclanthology.org/D19-1224.pdf',
 'Card_LittlePower_EMNLP2020':        'https://aclanthology.org/2020.emnlp-main.745.pdf',
 'Henderson_DeepRL_AAAI2018':         'https://arxiv.org/pdf/1709.06560v3',
 'Bouthillier_Variance_MLSys2021':    'https://arxiv.org/pdf/2103.03098v1',
 'Agarwal_Precipice_NeurIPS2021':     'https://arxiv.org/pdf/2108.13264v4',
}
def clean(txt):
    txt = txt.replace('\f', '\n')
    # cut at the references heading, searched from the back so an early "References" mention survives
    m = None
    for mm in re.finditer(r'\n\s*(References|REFERENCES|Bibliography|R EFERENCES)\s*\n', txt):
        if mm.start() > 0.35 * len(txt): m = mm
    if m: txt = txt[:m.start()]
    txt = re.sub(r'-\n(?=[a-z])', '', txt)          # de-hyphenate line breaks
    txt = re.sub(r'(?<!\n)\n(?!\n)', ' ', txt)       # join lines inside paragraphs
    txt = re.sub(r'[ \t]+', ' ', txt)
    return txt
for name, url in PAPERS.items():
    out = D / (name + '.txt')
    if out.exists() and out.stat().st_size > 8000:
        print('have', name); continue
    try:
        pdf = D / 'pdf' / (name + '.pdf'); pdf.parent.mkdir(exist_ok=True)
        if not pdf.exists():
            pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
        # PyMuPDF returns the content-stream order, which for LaTeX output is column order,
        # where pdftotext's layout analysis interleaved the two columns of the ACL and AAAI PDFs.
        raw = '\n'.join(page.get_text() for page in pymupdf.open(pdf))
        txt = clean(raw)
        out.write_text(txt)
        print('ok', name, len(raw), '->', len(txt))
    except Exception as e:
        print('FAIL', name, url, e)
    time.sleep(1.5)
