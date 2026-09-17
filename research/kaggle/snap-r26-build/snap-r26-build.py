"""R26 build the manuscript remotely and read back the page count that three edits left unverified.

Design fixed before running (2026-09-16, written 22:35 EDT). Scans 25 and 26 made three changes to
the source. Two swapped a single digit so the abstract would stop contradicting Section 2.3's second
coverage repeat, and one replaced the abstract's opening sentence with one character more than it
removed. Every one is length neutral to within a character, so the nine-page main text almost
certainly still holds, but almost certainly is not a measurement, and a paper that runs to ten pages
is desk rejected before anyone reads it. The user has withheld local compute, so the build runs here.
This kernel installs a TeX distribution, compiles main.tex twice so cross-references settle, and then
reports the numbers the local verifier would have reported. It reads the main-text page count from the
aux file's maintext:end label rather than from the page total, because the appendices are unbounded and
only the main text is capped. It compares the three official style files against the untouched template
copies byte for byte, since a gamed margin is the one way a page count can be made to lie. It lists any
reference that never resolved, counts overfull boxes and missing characters, and checks that no numeric
token inside any table body drifted from the pre-formatting snapshot. Nothing here loads a model or
touches the released run data, so it is a typesetting job rather than compute in the usual sense.
Whatever the page count says, the manuscript gets treated accordingly, and a ten means the next scan
spends its budget buying a line back rather than polishing prose.
"""
import hashlib, json, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), flush=True)
W = Path("/kaggle/working")
BUILD = W / "build"
BUILD.mkdir(exist_ok=True)


def run(cmd, **kw):
    """Run a command and return (returncode, combined output), never raising on failure."""
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# The dataset was uploaded with directory zipping, so each top-level folder may arrive either
# as a directory or as an archive beside it. Accept both rather than guess which.
root = None
for cand in sorted(Path("/kaggle/input").rglob("main.tex")):
    if cand.parent.name == "src":
        root = cand.parent.parent
        break
if root is None:
    for cand in sorted(Path("/kaggle/input").rglob("src.zip")):
        root = cand.parent
        break
if root is None:
    tree = [str(p) for p in sorted(Path("/kaggle/input").rglob("*"))[:60]]
    raise SystemExit(f"no input carrying src, saw {tree}")
print(f"[input] {root} -> {sorted(p.name for p in root.iterdir())}", flush=True)

STAGE = W / "stage"
STAGE.mkdir(exist_ok=True)
for name in ("src", "template", "before_format_pass"):
    dest = STAGE / name
    if (root / name).is_dir():
        shutil.copytree(root / name, dest, dirs_exist_ok=True)
    elif (root / f"{name}.zip").exists():
        dest.mkdir(exist_ok=True)
        with zipfile.ZipFile(root / f"{name}.zip") as z:
            z.extractall(dest)
    else:
        raise SystemExit(f"missing {name}")
keys_path = root / "citation_keys.json"
print(f"[stage] {sorted(p.name for p in (STAGE / 'src').iterdir())}", flush=True)

# TeX first, because everything downstream depends on a pdf existing.
rc, out = run("which pdflatex")
if rc != 0:
    print("[tex] installing", flush=True)
    run("apt-get -qq update")
    rc, out = run("DEBIAN_FRONTEND=noninteractive apt-get -qq install -y --no-install-recommends "
                  "texlive-latex-base texlive-latex-recommended texlive-fonts-recommended "
                  "texlive-latex-extra")
    print(f"[tex] install rc {rc} tail {out[-400:]}", flush=True)
rc, ver = run("pdflatex --version")
print(f"[tex] {ver.splitlines()[0] if ver.strip() else 'absent'}", flush=True)

src = STAGE / "src"
for f in src.iterdir():
    if f.is_file():
        shutil.copy(f, BUILD / f.name)
shutil.copytree(src / "figures", BUILD / "figures", dirs_exist_ok=True)

# Three passes, not two. A build starting with no aux file left "Label(s) may have changed" standing
# after the second pass, and a page count read from an aux that has not settled is not a measurement.
# Recording the count after each pass shows whether it moved, which is the thing actually in doubt.
passes = []
for i in (1, 2, 3):
    rc, out = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=BUILD)
    a = (BUILD / "main.aux").read_text(errors="replace") if (BUILD / "main.aux").exists() else ""
    mm = re.search(r"\\newlabel\{maintext:end\}\{\{[^}]*\}\{(\d+)\}", a)
    lg = (BUILD / "main.log").read_text(errors="replace") if (BUILD / "main.log").exists() else ""
    mt = re.search(r"Output written on main\.pdf \((\d+) pages?", lg)
    passes.append({"pass": i, "returncode": rc,
                   "main_text_pages": int(mm[1]) if mm else None,
                   "total_pages": int(mt[1]) if mt else None,
                   "rerun_requested": "Rerun to get" in lg})
    print(f"[pass {i}] rc {rc} main {passes[-1]['main_text_pages']} "
          f"total {passes[-1]['total_pages']} rerun {passes[-1]['rerun_requested']}", flush=True)
    if rc != 0:
        # The first real error line is worth more than the whole log, so surface it and stop.
        err = [l for l in out.splitlines() if l.startswith("!")]
        print(f"[pass {i}] first error {err[:3]}", flush=True)
        (W / "build_failure.log").write_text(out[-20000:])
        raise SystemExit(f"pdflatex failed on pass {i}")

log = (BUILD / "main.log").read_text(errors="replace")
aux = (BUILD / "main.aux").read_text(errors="replace")

report = {"design": __doc__, "passes": passes}

m = re.search(r"\\newlabel\{maintext:end\}\{\{[^}]*\}\{(\d+)\}", aux)
report["main_text_pages"] = int(m[1]) if m else None
m = re.search(r"Output written on main\.pdf \((\d+) pages?, (\d+) bytes\)", log)
report["total_pages"] = int(m[1]) if m else None
report["pdf_bytes"] = int(m[2]) if m else None

report["build"] = {
    "overfull_boxes": log.count("Overfull"),
    "underfull_boxes": log.count("Underfull"),
    "missing_characters": log.count("Missing character"),
    "font_warnings": log.count("LaTeX Font Warning"),
    "undefined_or_rerun": bool(re.search(r"undefined|Rerun to get", log)),
}

# A margin change is the one way a page count can be made to lie, so compare bytes not names.
tpl = STAGE / "template"
style = {}
for f in ("iclr2027_conference.sty", "fancyhdr.sty", "natbib.sty"):
    a, b = src / f, tpl / f
    style[f] = (a.read_bytes() == b.read_bytes()) if a.exists() and b.exists() else None
report["official_style_unchanged"] = all(v is True for v in style.values())
report["official_style_per_file"] = style
report["style_sha256"] = {f: hashlib.sha256((src / f).read_bytes()).hexdigest()[:16]
                          for f in style if (src / f).exists()}

alltex = "\n".join((src / n).read_text() for n in ("main.tex", "appendix_a.tex", "appendices_bcd.tex"))
defined = set(re.findall(r"\\newlabel\{([^}]+)\}", aux))
refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", alltex))
report["unresolved_reference_labels"] = sorted(refs - defined)

bkeys = re.findall(r"\\bibitem\[.*?\]\{([^}]+)\}", (src / "references.tex").read_text())
cites = [k for g in re.findall(r"\\cite[tp](?:\[[^]]*\])?\{([^}]+)\}", alltex) for k in g.split(",")]
report["bibliography"] = {"entries": len(bkeys), "unique_keys": len(set(bkeys)),
                          "unresolved_citation_keys": sorted(set(cites) - set(bkeys)),
                          "uncited_entries": sorted(set(bkeys) - set(cites))}


def table_numbers(text):
    """Every numeric token inside each tabular body, in order, with \\ci stripped so its braces do not split one."""
    bodies = re.findall(r"\\begin\{tabular\}.*?\n(.*?)\\end\{tabular\}", text, re.S)
    return [re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", b.replace("\\ci", "")) for b in bodies]


bfp = STAGE / "before_format_pass"
report["table_numeric_tokens_preserved"] = all(
    table_numbers((src / n).read_text()) == table_numbers((bfp / n).read_text())
    for n in ("main.tex", "appendix_a.tex", "appendices_bcd.tex") if (bfp / n).exists())

# Prose markers, recomputed here so the remote build reports the same gates the local one did.
prose = {}
keys = {}
if keys_path.exists():
    keys = {k: f'{a.replace("~", " ")} ({y})' for a, y, k in json.loads(keys_path.read_text())}
short = []
for name in ("main.tex", "appendix_a.tex", "appendices_bcd.tex"):
    t = (src / name).read_text()
    if name == "main.tex":
        t = t.split("\\maketitle", 1)[1].split("\\input{references}", 1)[0]
    t = re.sub(r"\\begin\{(table|figure|equation|align)\}\*?.*?\\end\{\1\}", " ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " mathematical-expression ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " mathematical-expression ", t)
    t = re.sub(r"\\ci\{[^{}]*\}\{[^{}]*\}", " mathematical-expression ", t)
    if keys:
        t = re.sub(r"\\cite[tp](?:\[([^]]*)\])?\{([^}]+)\}",
                   lambda m: ", ".join(keys.get(k, k) for k in m[2].split(",")) + (" " + m[1] if m[1] else ""), t)
    t = re.sub(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{[^{}]*\}", "\n", t)
    t = re.sub(r"\\(?:label|input|Needspace)\{[^{}]*\}", "", t)
    t = re.sub(r"\\(?:ref|eqref)\{[^{}]*\}", " reference ", t)
    t = t.replace("et al.", "et al").replace("e.g.", "eg").replace("i.e.", "ie")
    t = re.sub(r"(?<=\d)\.(?=\d)", "DECIMAL", t)
    t = re.sub(r"\\(?:begin|end)\{[^{}]*\}", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t).replace("~", " ").replace("{", "").replace("}", "").replace("\\", "")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\s*\n", t) if re.search(r"[A-Za-z]", s)]
    counts = [len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", s)) for s in sents]
    lows = [(c, s) for c, s in zip(counts, sents) if c < 4]
    short.extend((name, c, s) for c, s in lows)
    srt = sorted(counts)
    prose[name] = {
        "sentence_count": len(counts),
        "minimum_words": min(counts),
        "median_words": srt[len(srt) // 2],
        "mean_words": round(sum(counts) / len(counts), 2),
        "fragments_under_four_words": len(lows),
        "share_under_eight_words": round(sum(1 for c in counts if c < 8) / len(counts), 3),
        "corpus_target_under_eight": "0.058 to 0.238",
        "prose_colons_semicolons_dashes": len(re.findall(r"[:;\u2014\u2013]|--", t)),
        "the_openers_share": round(sum(1 for s in sents if s.startswith("The ")) / len(sents), 3),
        "corpus_target_the_openers": "0.15 observed across twenty prior-year and twenty recent abstracts",
    }
report["prose"] = prose
report["short_sentences"] = short

try:
    import pypdf
    reader = pypdf.PdfReader(str(BUILD / "main.pdf"))
    meta = reader.metadata or {}
    report["pdf_metadata"] = {"author": meta.get("/Author", ""), "title": meta.get("/Title", ""),
                              "empty_author": not (meta.get("/Author") or "").strip()}
    # A font the reader has to substitute renders differently on the referee's machine, so every
    # font must carry its own program. Subsetting shows up as the six-letter ABCDEF+ name prefix.
    # The walk has to descend into Form XObjects. Every included figure is one, and it carries its
    # own /Resources, so a page-level scan reports the body fonts and silently skips whatever the
    # artwork embeds. Scan 30 caught this by enumerating the shipped PDF by hand and finding a
    # twenty-fourth face inside the paired-prediction figure that this check had never seen.
    fonts = {}

    def collect(res, depth=0):
        if res is None:
            return
        res = res.get_object()
        for ref in (res.get("/Font") or {}).values():
            f = ref.get_object()
            for face in ([f] if "/FontDescriptor" in f else
                         [d.get_object() for d in (f.get("/DescendantFonts") or [])]):
                name = str(face.get("/BaseFont", "?"))
                desc = face.get("/FontDescriptor")
                embedded = bool(desc) and any(k in desc.get_object()
                                              for k in ("/FontFile", "/FontFile2", "/FontFile3"))
                fonts[name] = {"embedded": embedded, "subset": len(name) > 7 and name[7:8] == "+",
                               "in_xobject": depth > 0}
        if depth < 6:
            for ref in (res.get("/XObject") or {}).values():
                xo = ref.get_object()
                if xo.get("/Subtype") == "/Form":
                    collect(xo.get("/Resources"), depth + 1)

    for page in reader.pages:
        collect(page.get("/Resources"))
    report["fonts"] = {"count": len(fonts), "all_embedded": all(v["embedded"] for v in fonts.values()),
                       "all_subset": all(v["subset"] for v in fonts.values()),
                       "not_embedded": sorted(n for n, v in fonts.items() if not v["embedded"]),
                       "faces": fonts}
except Exception as exc:
    report["pdf_metadata"] = {"error": f"{type(exc).__name__}: {exc}"[:200]}

# Emit the manifest here, so the checksums are generated from the same bytes the build consumed.
digests = {n: hashlib.sha256((src / n).read_bytes()).hexdigest()
           for n in ("main.tex", "appendix_a.tex", "appendices_bcd.tex", "references.tex",
                     "iclr2027_conference.sty") if (src / n).exists()}
digests["SNAP_revised_draft.pdf"] = hashlib.sha256((BUILD / "main.pdf").read_bytes()).hexdigest()
report["sha256"] = digests
(W / "SHA256SUMS.txt").write_text("".join(
    f"{digests[n]}  {n}\n" for n in ("main.tex", "appendix_a.tex", "appendices_bcd.tex",
                                     "references.tex", "SNAP_revised_draft.pdf",
                                     "iclr2027_conference.sty") if n in digests))

shutil.copy(BUILD / "main.pdf", W / "main.pdf")
shutil.copy(BUILD / "main.log", W / "main.log")
shutil.copy(BUILD / "main.aux", W / "main.aux")
shutil.rmtree(STAGE, ignore_errors=True)
shutil.rmtree(BUILD, ignore_errors=True)

report["wall_seconds"] = time.time() - t0
(W / "r26_build.json").write_text(json.dumps(report, indent=1))
print("[pages] main_text", report["main_text_pages"], "total", report["total_pages"], flush=True)
print("[style] unchanged", report["official_style_unchanged"], flush=True)
print("[refs] unresolved", report["unresolved_reference_labels"], flush=True)
print("[short]", short, flush=True)
print("[summary]", json.dumps({k: report[k] for k in
                               ("main_text_pages", "total_pages", "official_style_unchanged",
                                "table_numeric_tokens_preserved")}), flush=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
