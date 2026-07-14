#!/usr/bin/env python3
"""Generate the anonymized Written Language & Literacy manuscript.

paper/chuzhditsa.tex -> paper/chuzhditsa_wll.tex. Run from the repo root after
any change to the canonical paper; never hand-edit chuzhditsa_wll.tex.

Transforms: 12pt + 1.5 spacing; author block, repo URL, and PDF docinfo
anonymized for double-blind review; abstract replaced with the 120-word
WLL version + 10 keywords (Benjamins limit: 120 words); book titles
sentence-cased per the Unified Style Sheet / Benjamins guidelines.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "paper", "chuzhditsa.tex")
DST = os.path.join(ROOT, "paper", "chuzhditsa_wll.tex")

ABSTRACT = r"""\begin{abstract}
\noindent Alphabets only patchily provide a middle layer between everyday spelling and technical transcription: a conventional register for writing a foreign word so that its source pronunciation is recoverable. No major Slavic Cyrillic orthography occupies that layer; loanwords enter through recipient-adapting transcription, with systematic indeterminacy as the result (Bulgarian \cz{Вашингтон}~$\sim$~\cz{Уошингтън}). We present \emph{Chuzhditsa} (Bulgarian чуждица, `foreignism'), a computable Cyrillic-based \emph{phonological citation register}: (i) a compositional grammar of diacritic operations deriving letters for non-Slavic phonemes from attested Cyrillic material; (ii) a prosodic layer for stress, tone, length; (iii) a register-marking typeface whose OpenType rules are the orthography's rules, executable rather than merely described. Coverage is evaluated against twenty languages under a three-way classification of exact, merged, and declared loss.

\medskip
\noindent\textbf{Keywords:} writing systems, orthography design, Cyrillic, loanword adaptation, phonological transcription, Slavic languages, katakana, biscriptality, OpenType, Bulgarian
\end{abstract}"""

TITLES = [
    ("Visible Speech: The Science of Universal Alphabetics", "Visible speech: The science of universal alphabetics"),
    ("Biscriptality: A Sociolinguistic Typology", "Biscriptality: A sociolinguistic typology"),
    ("Developing Orthographies for Unwritten Languages", "Developing orthographies for unwritten languages"),
    ("The Slavonic Languages", "The Slavonic languages"),
    ("The World's Writing Systems", "The world's writing systems"),
    ("Writing Systems: An Introduction to their Linguistic Analysis", "Writing systems: An introduction to their linguistic analysis"),
    ("Advances in the Creation and Revision of Writing Systems", "Advances in the creation and revision of writing systems"),
    ("The Esperanto Movement", "The Esperanto movement"),
    ("Esperanto and Its Rivals: The Struggle for an International Language", "Esperanto and its rivals: The struggle for an international language"),
    ("Handbook of the International Phonetic Association: A Guide to the Use of the International Phonetic Alphabet", "Handbook of the International Phonetic Association: A guide to the use of the International Phonetic Alphabet"),
    ("The Blackwell Companion to Phonology", "The Blackwell companion to phonology"),
    ("The Korean Alphabet: Its History and Structure", "The Korean alphabet: Its history and structure"),
    ("Nationalism and the Construction of Korean Identity", "Nationalism and the construction of Korean identity"),
    ("The Korean Language Reform of 1446", "The Korean language reform of 1446"),
    ("A History of the Korean Language", "A history of the Korean language"),
    ("Interslavic Zonal Constructed Language: An Introduction for English-Speakers", "Interslavic zonal constructed language: An introduction for English-speakers"),
    ("Alphabets and Reading: The Initial Teaching Alphabet", "Alphabets and reading: The Initial Teaching Alphabet"),
    ("Scripting Japan: Orthography, Variation, and the Creation of Meaning in Written Japanese", "Scripting Japan: Orthography, variation, and the creation of meaning in written Japanese"),
    ("Writing Systems: A Linguistic Introduction", "Writing systems: A linguistic introduction"),
    ("The Dawn of Slavic: An Introduction to Slavic Philology", "The dawn of Slavic: An introduction to Slavic philology"),
    ("Spelling and Society: The Culture and Politics of Orthography around the World", "Spelling and society: The culture and politics of orthography around the world"),
    ("A History of Writing in Japan", "A history of writing in Japan"),
    ("A Computational Theory of Writing Systems", "A computational theory of writing systems"),
    ("Japanese English: Language and Culture Contact", "Japanese English: Language and culture contact"),
    ("Language and the Modern State: The Reform of Written Japanese", "Language and the modern state: The reform of written Japanese"),
]


def main():
    s = open(SRC).read()
    n = 0

    def rep(a, b, why):
        nonlocal s, n
        if a not in s:
            sys.exit(f"gen_wll: anchor not found ({why}): {a[:60]}...")
        s = s.replace(a, b, 1)
        n += 1

    rep(r"\documentclass[11pt]{article}", r"\documentclass[12pt]{article}", "12pt")
    rep(r"""\author{Anastas Stoyanovsky\thanks{Fonts, build toolchain, and the twenty-language audit are available in the accompanying repository (\texttt{github.com/anastasds/chuzhditsa}); the typeface used for all object-language examples in this manuscript is the system being described.}\\[3pt] {\normalsize Unaffiliated \quad \texttt{anastas@stoyanovs.ky}}}""",
        r"""\author{{\normalsize [Author details withheld for double-blind review]}\thanks{Fonts, build toolchain, and the twenty-language audit are available in an open repository (reference withheld for review); the typeface used for all object-language examples in this manuscript is the system being described.}}""",
        "anonymize author")
    rep(r"\special{pdf:docinfo << /Title (Chuzhditsa: a phonological citation register for Cyrillic) /Author (Anastas Stoyanovsky) >>}",
        r"\special{pdf:docinfo << /Title (Chuzhditsa: a phonological citation register for Cyrillic) >>}",
        "anonymize docinfo")
    rep("\\maketitle", "\\maketitle\n\\onehalfspacing", "spacing")
    rep("is the subject of the companion paper; here we state",
        "is the subject of a companion paper (reference withheld for review); here we state",
        "anonymize companion ref 1")
    rep("A companion paper documents the construction level",
        "A companion paper (reference withheld for review) documents the construction level",
        "anonymize companion ref 2")

    m = re.search(r"\\begin\{abstract\}.*?\\end\{abstract\}", s, re.S)
    if not m:
        sys.exit("gen_wll: abstract not found")
    s = s[: m.start()] + ABSTRACT + s[m.end():]
    n += 1

    for a, b in TITLES:
        if a not in s:
            sys.exit(f"gen_wll: anchor not found (USS title case): {a[:60]}...")
        s = s.replace(a, b)  # all occurrences — some volumes are cited more than once
        n += 1

    for bad in ("Stoyanovsky", "stoyanovs.ky", "anastasds", "lindenpmg"):
        if bad in s:
            sys.exit(f"gen_wll: identity string survived: {bad}")

    open(DST, "w").write(s)
    print(f"gen_wll: {n} transforms -> {os.path.relpath(DST, ROOT)}")


if __name__ == "__main__":
    main()
