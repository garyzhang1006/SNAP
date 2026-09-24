# ARS academic-paper citation-check, 2026-09-24

Scope is main.tex, appendix_a.tex and appendices_bcd.tex against references.tex (75 entries), run in session with no agents.

Orphans: work/goal/scan.py P13 reports no cited key missing from references.tex and no reference that goes uncited.

Existence: all 23 arXiv identifiers in references.tex were fetched from the arXiv export API (https://export.arxiv.org/api/query) on 2026-09-24, and every returned title matches the entry's title. The arXiv MCP tool returned "not found" for real papers (1803.05457, 2504.11393), so its results were discarded as a tool failure. The remaining 52 entries are journal or proceedings papers and books that earlier citation audits checked (research/ rebuttal logs, CI1 to CI6), and this run didn't recheck them online.

Completeness: every entry has authors, a title, a year and a venue or an arXiv identifier. Entries flagged by the first regex pass (Heredity, Psychometrika, a/b year suffixes) were false positives.

Verdict: PASS, with no edits needed.
