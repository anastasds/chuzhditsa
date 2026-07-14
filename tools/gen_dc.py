#!/usr/bin/env python3
"""Generate the Digital Creativity (Taylor & Francis) submission versions of
the process paper.

paper/process.tex -> paper/process_dc.tex      (complete version)
                  -> paper/process_dc_anon.tex (anonymized version)

Run from the repo root after any change to the canonical paper; never
hand-edit the generated files.

Transforms (both): 12pt + 1.5 spacing; condensed abstract (~210 words, T&F
journals cap around 250) + 6 alphabetized keywords. Anonymized version:
author block replaced with [ANON] (T&F double-anonymous review); the thanks
footnote keeps the project-identifying companion titles (the study is
reflexive; the project is its subject) but drops name, affiliation, email.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "paper", "process.tex")
DST_FULL = os.path.join(ROOT, "paper", "process_dc.tex")
DST_ANON = os.path.join(ROOT, "paper", "process_dc_anon.tex")

ABSTRACT = r"""\begin{abstract}
\noindent We document a configuration of human--AI production in a creative-technical task and make it auditable. Over a compressed span of days, an AI coding agent constructed a parametric Cyrillic typeface family and drafted the manuscripts describing it, steered by a human who wrote no code and drew no letterforms: his contribution was criticism — verdicts on rendered artifacts, mostly withholding solutions by design. The complete criticism channel is archived, coded, and recomputable: a machine-readable corpus and a shipped audit script re-derive every count this paper states from the archived record. On that record, criticism changed the builder's \emph{method} more than its artifacts: patching gave way to preserving relationships, trusting compilation to testing behavior, local repairs to reusable checks. The record also complicates the method it documents: the solution-free discipline held while the builder converged and broke on a stubborn glyph; machine verification repeatedly certified defects the human eye caught in seconds, because the instruments measured the wrong axis; and by the end criticism itself was partly delegated, the human commissioning machine-run adversarial review panels against the machine's own work. We report the configuration, a portable toolkit of artifact-checkable working rules, and an authorship analysis whose subject includes this text: the manuscript was drafted by the model whose conduct it documents, under disclosed human direction and editorial control.

\medskip
\noindent\textbf{Keywords:} artificial intelligence; creative collaboration; criticism; design process; large language models; type design
\end{abstract}"""

AUTHOR_ANON = r"""\author{{\normalsize [ANON]}\thanks{This manuscript documents the production of two companion papers — \emph{Chuzhditsa: a phonological citation register for Cyrillic} and \emph{The letter as a program: how the Chuzhditsa typeface works} — and was drafted, like them, by the language model whose work it describes, at the direction and under the editorial control of the human author ([ANON]). Section~\ref{sec:authorship} states the authorship position in full. The repository named in the companion papers ([ANON] for review) contains the complete audit trail cited here.}}"""


def build(dst, anon):
    s = open(SRC).read()
    n = 0

    def rep(a, b, why, count=1):
        nonlocal s, n
        if a not in s:
            sys.exit(f"gen_dc: anchor not found ({why}): {a[:60]}...")
        s = s.replace(a, b, count)
        n += 1

    rep(r"\documentclass[11pt]{article}", r"\documentclass[12pt]{article}", "12pt")
    if "\\usepackage{setspace}" not in s:
        rep(r"\usepackage{microtype}", "\\usepackage{microtype}\n\\usepackage{setspace}", "setspace")
    rep("\\maketitle", "\\maketitle\n\\onehalfspacing", "spacing")

    if anon:
        m = re.search(r"\\author\{.*?\}\n\\date\{\}", s, re.S)
        if not m:
            sys.exit("gen_dc: author block not found")
        s = s[: m.start()] + AUTHOR_ANON + "\n\\date{}" + s[m.end():]
        n += 1

    m = re.search(r"\\begin\{abstract\}.*?\\end\{abstract\}", s, re.S)
    if not m:
        sys.exit("gen_dc: abstract not found")
    s = s[: m.start()] + ABSTRACT + s[m.end():]
    n += 1

    if anon:
        for bad in ("Stoyanovsky", "stoyanovs.ky", "anastasds", "lindenpmg"):
            if bad in s:
                sys.exit(f"gen_dc: identity string survived in anon version: {bad}")

    open(dst, "w").write(s)
    print(f"gen_dc: {n} transforms -> {os.path.relpath(dst, ROOT)}")


if __name__ == "__main__":
    build(DST_FULL, anon=False)
    build(DST_ANON, anon=True)
