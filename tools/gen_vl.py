#!/usr/bin/env python3
"""Generate the Visible Language submission versions of the typeface paper.

paper/typeface.tex -> paper/typeface_vl.tex      (complete version)
                   -> paper/typeface_vl_anon.tex (anonymized version)

Run from the repo root after any change to the canonical paper; never
hand-edit the generated files.

Transforms (both versions): 12pt + 1.5 spacing; VL abstract (200-300 words,
single paragraph, no citations) + keywords (3-6, alphabetical) + an
"Implications for practice" block (100-200 words); in-text citations and
bibliography converted to APA 7th. Anonymized version additionally: author
block and repository/companion references replaced with [ANON], PDF docinfo
author removed (per VL's double-blind instructions).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "paper", "typeface.tex")
DST_FULL = os.path.join(ROOT, "paper", "typeface_vl.tex")
DST_ANON = os.path.join(ROOT, "paper", "typeface_vl_anon.tex")

FRONT = r"""\begin{abstract}
\noindent Chuzhditsa is a Cyrillic typeface family of four cuts — a round-capped register face, a grotesk, a slab serif, and an inline cut weight-matched to Times for setting citations inside serif text — each in Regular, Bold, Italic, and Bold Italic, generated entirely from one set of centerline skeletons by a parametric builder of roughly eight hundred lines. The family exists to serve a designed writing system: a phonological citation register that extends Cyrillic for writing foreign words so that their source pronunciation is recoverable. This paper describes how the typeface works, as an implementation. A stroke model declares every glyph as centerline primitives and expands them with a disc whose diameter varies with the path's tangent angle, supplying both page texture and junction relief in one function. A boolean-union outline policy resolves at build time what coverage-summing and even-odd rasterizers would otherwise mishandle. An optical-correction canon — overshoots, apex piercing, optical centering, round compression — is implemented as build-time arithmetic, with every coordinate derived from a single parameter sheet. Per-family terminal, slab, and clamp rules separate the four cuts; a six-class kerning matrix covers the fitting space in thirty rules that extension letters inherit by construction. The OpenType layer functions as an executable reference implementation of the orthography the face serves: ligature lookup order, register-gated fusions, computed mark anchors, and a normalization-closed character map, verified by a shaping-test suite. An instrumented evaluation measures per-cut small-size floors, and the build is byte-reproducible. The parametric claim is deliberately scoped: parameters hold within one design language, never across all letterforms.

\medskip
\noindent\textbf{Keywords:} Cyrillic; OpenType; optical corrections; parametric type design; type engineering; writing systems

\medskip
\noindent\textbf{Implications for practice.} The transferable content is a set of named rules with stated rationales: union overlapping outlines before emitting, because coverage-summing rasterizers darken every seam and even-odd consumers open white slits; ship pair kerning as GPOS, because the legacy kern table is ignored in CFF-flavored fonts; widen advances with weight, because advance width is a property of the counter, not the stroke; trim advances on open-sided letters, whose apertures recede; and derive every coordinate from the parameter sheet, so that a value which holds in only one style is exposed as a bug rather than shipped as a glyph. Treating optical corrections as engine-level arithmetic lets them generalize across a large character set at no marginal cost. For designers extending scripts for new orthographies, the executable-reference-implementation pattern — spelling rules compiled as OpenType lookups and verified by shaping assertions — makes orthographic claims mechanically testable.
\end{abstract}"""

# in-text citations: USS author-year -> APA 7th
CITES = [
    ("(Knuth 1982)", "(Knuth, 1982)"),
    ("(Noordzij 2005)", "(Noordzij, 2005)"),
    ("(Johnston 1906: 273--274)", "(Johnston, 1906, pp.\\ 273--274)"),
    ("(Johnston 1906)", "(Johnston, 1906)"),
    ("(Bigelow \\& Holmes 1993)", "(Bigelow \\& Holmes, 1993)"),
    ("(Smeijers 1996)", "(Smeijers, 1996)"),
    ("(Zhukov 1996)", "(Zhukov, 1996)"),
    ("(Йончев \\& Йончева 1982)", "(Yonchev \\& Yoncheva, 1982)"),
    ("(Bringhurst 2004: 17)", "(Bringhurst, 2004, p.\\ 17)"),
    ("(Burke 1998: 101--102)", "(Burke, 1998, pp.\\ 101--102)"),
    ("(Tracy 1986: 71)", "(Tracy, 1986, p.\\ 71)"),
    ("(Southall 1985)", "(Southall, 1985)"),
]

APA_BIB = r"""\begin{thebibliography}{99}
\bibitem{bigelow} Bigelow, C., \& Holmes, K. (1993). The design of a Unicode font. \emph{Electronic Publishing}, \emph{6}(3), 289--305.
\bibitem{bringhurst} Bringhurst, R. (2004). \emph{The elements of typographic style} (3rd ed.). Hartley \& Marks.
\bibitem{burke} Burke, C. (1998). \emph{Paul Renner: The art of typography}. Hyphen Press.
\bibitem{hofstadter} Hofstadter, D. R. (1982). Metafont, metamathematics, and metaphysics: Comments on Donald Knuth's article ``The concept of a meta-font''. \emph{Visible Language}, \emph{16}(4), 309--338.
\bibitem{johnston} Johnston, E. (1906). \emph{Writing \& illuminating, \& lettering}. John Hogg.
\bibitem{knuth82} Knuth, D. E. (1982). The concept of a meta-font. \emph{Visible Language}, \emph{16}(1), 3--27.
\bibitem{noordzij} Noordzij, G. (2005). \emph{The stroke: Theory of writing}. Hyphen Press.
\bibitem{smeijers} Smeijers, F. (1996). \emph{Counterpunch: Making type in the sixteenth century, designing typefaces now}. Hyphen Press.
\bibitem{southall} Southall, R. (1985). \emph{Designing new typefaces with Metafont} (Report No.\ STAN-CS-85-1074). Stanford University, Department of Computer Science.
\bibitem{tracy} Tracy, W. (1986). \emph{Letters of credit: A view of type design}. Gordon Fraser.
\bibitem{yonchev} Yonchev, V., \& Yoncheva, O. (1982). \emph{Древен и съвременен български шрифт} [Ancient and modern Bulgarian type]. Balgarski hudozhnik.
\bibitem{zhukov} Zhukov, M. (1996). The peculiarities of Cyrillic letterforms: Design variation and correlation in Russian typefaces. \emph{Typography Papers}, \emph{1}.
\end{thebibliography}"""

AUTHOR_FULL = r"""\author{Anastas Stoyanovsky\thanks{The builder discussed here (\texttt{tools/build\_font\_v3.py}, $\sim$800 lines of Python) is distributed with the fonts (\texttt{github.com/anastasds/chuzhditsa}); every object-language example in this manuscript is set in the typeface under discussion. The system paper (\emph{Chuzhditsa: a phonological citation register for Cyrillic}, LingBuzz 010134) documents the orthography this family serves.}\\[3pt] {\normalsize Unaffiliated \quad \texttt{anastas@stoyanovs.ky}}}"""

AUTHOR_ANON = r"""\author{{\normalsize [ANON]}\thanks{The builder discussed here ($\sim$800 lines of Python) is distributed with the fonts in an open repository ([ANON] — redacted for review); every object-language example in this manuscript is set in the typeface under discussion. A companion system paper ([ANON]) documents the orthography this family serves.}}"""


def build(dst, anon):
    s = open(SRC).read()
    n = 0

    def rep(a, b, why, count=1):
        nonlocal s, n
        if a not in s:
            sys.exit(f"gen_vl: anchor not found ({why}): {a[:60]}...")
        s = s.replace(a, b, count)
        n += 1

    rep(r"\documentclass[11pt]{article}", r"\documentclass[12pt]{article}", "12pt")
    rep("\\maketitle", "\\maketitle\n\\onehalfspacing", "spacing")
    if "setspace" not in s:
        rep(r"\usepackage{microtype}", "\\usepackage{microtype}\n\\usepackage{setspace}", "setspace pkg")

    # author block
    m = re.search(r"\\author\{.*?\}\n\\date\{\}", s, re.S)
    if not m:
        sys.exit("gen_vl: author block not found")
    s = s[: m.start()] + (AUTHOR_ANON if anon else AUTHOR_FULL) + "\n\\date{}" + s[m.end():]
    n += 1

    if anon:
        rep(r"\special{pdf:docinfo << /Title (The letter as a program: how the Chuzhditsa typeface works) /Author (Anastas Stoyanovsky) >>}",
            r"\special{pdf:docinfo << /Title (The letter as a program: how the Chuzhditsa typeface works) >>}",
            "anonymize docinfo")
        rep("The companion paper describes Chuzhditsa's function",
            "A companion paper ([ANON]) describes Chuzhditsa's function", "anonymize companion ref")

    # front matter
    m = re.search(r"\\begin\{abstract\}.*?\\end\{abstract\}", s, re.S)
    if not m:
        sys.exit("gen_vl: abstract not found")
    s = s[: m.start()] + FRONT + s[m.end():]
    n += 1

    # citations
    for a, b in CITES:
        rep(a, b, f"APA cite {a[:24]}")
    # narrative citation with page-style reference
    rep("as Hofstadter (1982) argued", "as Hofstadter (1982) argued", "hofstadter narrative")  # unchanged, assert presence

    # bibliography
    m = re.search(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", s, re.S)
    if not m:
        sys.exit("gen_vl: bibliography not found")
    s = s[: m.start()] + APA_BIB + s[m.end():]
    n += 1

    if anon:
        for bad in ("Stoyanovsky", "stoyanovs.ky", "anastasds", "lindenpmg"):
            if bad in s:
                sys.exit(f"gen_vl: identity string survived in anon version: {bad}")

    open(dst, "w").write(s)
    print(f"gen_vl: {n} transforms -> {os.path.relpath(dst, ROOT)}")


if __name__ == "__main__":
    build(DST_FULL, anon=False)
    build(DST_ANON, anon=True)
