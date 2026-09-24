"""ASD-STE100 (Issue 9) writing-rule checks that a pattern can decide, with the user's overrides.

usage: python3 work/goal/stecheck.py [file.tex ...] [--detail]

Overrides from the user (2026-09-24): no sentence-length ceiling (STE 4.x/5.x), a floor of eight words,
contractions required (STE prefers full forms), and no colons or semicolons in prose. The dictionary rule
(STE 1.1, approved words only) can't be applied to a statistics paper, since estimator, covariance and
most of the method vocabulary are technical names (STE 1.5) that STE permits, so it isn't checked here.

Checked rules
  R2.2  noun clusters longer than three words
  R3.4  -ing verb forms that aren't technical names or modifiers
  R3.7  passive voice in descriptive text, reported as a rate (STE asks for active voice where possible)
  R3.x  phrasal verbs STE lists as unapproved (carry out, set up, find out, ...)
  R6.2  paragraphs longer than six sentences in descriptive text
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "work" / "goal"))
sys.path.insert(0, str(ROOT / "work"))
from scan import prose_lines, strip_outcomes  # noqa: E402
from style_check import sentence_units  # noqa: E402

PHRASAL = ["carry out", "carried out", "set up", "find out", "found out", "point out", "pointed out", "make up",
           "made up", "turn out", "turns out", "turned out", "bring about", "come up with", "look into", "rule out",
           "ruled out", "leave out", "left out", "figure out", "end up", "ends up"]
# -ing words that are nouns, technical names or fixed adjectives here, not verb forms
ING_OK = {"string", "during", "bootstrapping", "sampling", "scoring", "setting", "settings", "training", "pretraining",
          "centring", "resampling", "linearisation", "missing", "remaining", "matching", "corresponding", "leading",
          "following", "underlying", "shifting", "sharing", "clustering", "thing", "nothing", "something", "anything",
          "everything", "bring", "king", "ring", "spring", "wing", "rounding", "weighting", "weightings", "reading",
          "wording", "screening", "planning", "finding", "findings", "ordering", "orderings", "recording", "timing",
          "wrong-call", "understanding", "meaning", "fine-tuning", "decoding", "binding", "embedding", "labelling",
          "modelling", "testing", "encoding", "grouping", "rescoring", "rescaling", "morning", "ceiling", "evening",
          "caching", "casting", "king", "during", "within-configuration", "outstanding", "interesting", "existing",
          "neighbouring", "increasing", "decreasing", "varying", "working", "training-fold", "rising", "falling"}
STOP = set("a an the of in on at to for from by with and or but as is are was were be been this that these those "
           "it its we our their they which who than then when where while since because so if not no each every all "
           "any both one two three four five across under over into onto per between among".split())


def paragraphs(name):
    """Group prose lines into paragraphs by blank-line adjacency in the source."""
    lines = prose_lines(name)
    paras, cur, last = [], [], None
    for ln, text in lines:
        # a \cparagraph heading or a display equation starts a new paragraph in LaTeX
        if last is not None and (ln != last + 1 or text.lstrip().startswith(("\\cparagraph", "\\[", "\\paragraph"))):
            paras.append(cur)
            cur = []
        cur.append((ln, text))
        last = ln
    if cur:
        paras.append(cur)
    return paras


def plain(t):
    t = strip_outcomes(t)
    t = re.sub(r"\$[^$]*\$", " X ", t)
    t = re.sub(r"\\(?:cite[tp]?|ref|label|res|ci|supfig|suptab)\{[^{}]*\}(\{[^{}]*\})?", " X ", t)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)
    return re.sub(r"[{}~]", " ", t)


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")] or ["main.tex"]
    detail = "--detail" in sys.argv
    for f in files:
        out = {"R2.2": [], "R3.4": [], "R3.x": [], "R6.2": []}
        words = passive = 0
        for para in paragraphs(f):
            text = " ".join(t for _, t in para)
            n = len(sentence_units(strip_outcomes(text)))
            if n > 6:
                out["R6.2"].append(f"{f}:{para[0][0]} paragraph of {n} sentences")
            for ln, raw in para:
                p = plain(raw)
                low = p.lower()
                words += len(re.findall(r"[A-Za-z]+", p))
                passive += len(re.findall(r"\b(is|are|was|were|been|be|being)\s+(\w+ly\s+)?\w+(ed|en)\b", low))
                for ph in PHRASAL:
                    for _ in re.finditer(r"\b" + ph + r"\b", low):
                        out["R3.x"].append(f"{f}:{ln} '{ph}'")
                for m in re.finditer(r"\b([a-z][a-z-]*ing)\b", low):
                    w = m.group(1)
                    if w not in ING_OK and len(w) > 5:
                        out["R3.4"].append(f"{f}:{ln} '{w}'  ...{low[max(0, m.start() - 30):m.end() + 20]}...")
                # noun clusters: runs of 4+ content words with no stopword, verb or punctuation between them
                for seg in re.split(r"[,.;:()\n]", p):
                    run = []
                    for tok in seg.split():
                        tl = tok.lower().strip("'\"")
                        if tl in STOP or re.fullmatch(r"x|[\d.%]+", tl) or tl.endswith("ly") or tl in {"can't", "don't", "doesn't", "isn't", "aren't", "didn't", "couldn't", "won't"}:
                            if len(run) >= 4:
                                out["R2.2"].append(f"{f}:{ln} '{' '.join(run)}'")
                            run = []
                        else:
                            run.append(tok)
                    if len(run) >= 4:
                        out["R2.2"].append(f"{f}:{ln} '{' '.join(run)}'")
        print(f"== {f}: {words} words, passive {1000 * passive / max(words, 1):.1f}/1k")
        for k, v in out.items():
            print(f"  {k}: {len(v)}")
            if detail:
                for x in (v if "--all" in sys.argv else v[:60]):
                    print("     ", x)


if __name__ == "__main__":
    main()
