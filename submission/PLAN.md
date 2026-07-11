# Submission plan

This is the running plan for getting the collection out. It records the
agreed sequence, the venue targets, and — importantly — the division of
labor: everything a language model can prepare is prepared here; every step
that requires an accountable human is marked **[you]**.

## The boundary, stated once

The builder can draft, format, verify, and package. It **cannot**, and by
the process paper's own argument **should not**, perform the acts that carry
accountability: creating accounts, obtaining arXiv endorsement, accepting
license terms, entering personal data, or pressing *submit*. Those are the
author's — Anastas Stoyanovsky's — and they are the one place in this project
where the signature has to be a hand, not a workshop. Each is marked **[you]**.

One standing preference: all of it goes under a **personal or academic
identity, not the company (lindenpmg) one** — arXiv email, ORCID, and every
byline contact alike. The `[contact]` placeholders in the cover letters and
pitch take that non-company address.

## Agreed sequence

1. Typeface + orthography papers → arXiv.
2. Same two → journals.
3. Process paper → arXiv, then journal.
4. Op-ed → an outlet.
5. The op-ed's criticism (the two press pieces) → with it.

Rationale for the order (from the reviews): the typeface paper is the
strongest and most conventionally publishable, so it leads and de-risks the
rest; the orthography paper travels as its companion; the process paper is
independent and goes only once the artifacts it describes are public and
inspectable; the press pieces are last because they presuppose the papers.

---

## Stage 1 — arXiv (typeface, then orthography)

**Category recommendations**

| Paper | Primary | Cross-list |
|---|---|---|
| The letter as a program (typeface) | cs.GR (Graphics) | cs.DL, cs.CL |
| Chuzhditsa (orthography) | cs.CL (Computation and Language) | cs.DL |

**Format: PDF-only is the pragmatic choice.** All four papers are XeLaTeX and
depend on two macOS system fonts (Times New Roman, Arial Unicode MS) plus the
project's own embedded fonts. arXiv's build farm has neither system font, so
the LaTeX source will **not** compile there as-is. arXiv accepts PDF-only
submissions; the compiled, linearized PDFs in `paper/` are ready. The full
LaTeX source lives in the public repository the papers already cite, so
"source availability" is satisfied without fighting arXiv's font environment.

- *Alternative, if you want the source on arXiv:* the builder can produce a
  source-compilable variant of each paper with the fonts swapped for arXiv-
  available ones (TeX Gyre Termes for Times; a Libertine/IPA-capable face for
  Arial Unicode MS). This changes the look of the object-language and IPA and
  is only worth doing if a reviewer demands source. Say the word.

**License:** arXiv's default (arXiv.org perpetual, non-exclusive) is fine and
keeps options open for the journals below. CC BY 4.0 is the more open choice
and is compatible with every target venue here; recommended if you have no
reason to hold rights back.

**Plain-text abstracts** (arXiv strips LaTeX; these are paste-ready) live in
`submission/abstracts.txt`.

**Steps**
- **[you]** arXiv account; if not already endorsed for cs.CL / cs.GR, request
  endorsement (an established author in the category vouches — the builder can
  draft the endorsement request).
- **[you]** New submission → upload `paper/typeface.pdf` → paste the plain-text
  abstract, title, author → pick cs.GR primary, cs.DL + cs.CL cross-list →
  choose license → submit. Repeat for `paper/chuzhditsa.pdf`.
- Note the assigned arXiv IDs back here; the journal cover letters cite them.

---

## Stage 2 — journals (typeface, then orthography)

Targets and rationale drawn from the three review rounds. Draft cover letters
are in `submission/cover-letters.md`; they are venue-specific and will be
finalized once you confirm the venue.

**Typeface — "The letter as a program"**
- **First choice: _TUGboat_** (TeX Users Group). The natural home: a paper in
  the direct METAFONT lineage, arguing Knuth's thesis at one design language's
  scale, with a working parametric engine. Practitioner-expert readership,
  fast, and exactly the audience that will enjoy it. Not high-prestige in a
  tenure sense, but the right first room.
- **Alternative: _Visible Language_** — where the Knuth–Hofstadter debate the
  paper re-runs was actually published; poetic fit, slower, humanities-facing.
- **Alternative (archival/CS): _Digital Scholarship in the Humanities_** (OUP)
  or a document-engineering venue, if you want DH indexing.
- Reviewers will ask for expert Cyrillic type review — see **[you]** items
  below; it strengthens but need not precede submission.

**Orthography — "Chuzhditsa"**
- **First choice: _Written Language & Literacy_** (John Benjamins) — a
  writing-systems journal that takes design-and-analysis papers and will
  engage the phonological-citation-register category on its merits.
- **Alternative: the grapholinguistics venue** — *Grapholinguistics and Its
  Applications* (the IGS / "Graphematik" series), explicitly hospitable to
  script-design + artifact papers at the scope this paper now claims.
- **Alternative (design-research): _Digital Creativity_** (T&F) — accepts the
  "design proposition with an inspectable artifact" framing directly.
- A mainstream linguistics journal will require the reader study; the venues
  above will not necessarily. The paper now scopes itself for exactly this.

**Steps**
- **[you]** Confirm venues (or pick alternatives). The builder finalizes the
  cover letter and reformats to the venue's template/word limits.
- **[you]** Journal account, author metadata, suggested/excluded reviewers,
  ORCID, and the submit action. The builder drafts everything that goes *in*
  the form; the form itself is yours.

---

## Stage 3 — process paper ("The critic and the builder")

- **arXiv:** primary **cs.HC**, cross-list **cs.CL, cs.SE, cs.AI**. Same
  PDF-only route. Submit only *after* stages 1–2 exist and the repository is
  public (see below), because the paper's evidence is the inspectable trail.
- **Journal:** the reviews converge on a research-through-design / HCI venue,
  **not** a top archival HCI journal (it is honest n=1). Best fits: **_Digital
  Creativity_** (a reviewer's explicit pick), **DIS** (ACM Designing
  Interactive Systems — RtD-friendly, though a conference), or a
  software-engineering **experience-report** track. The op-ed and its two
  criticisms are *not* submitted here; they are Stage 4.

---

## Stage 4–5 — the op-ed and its criticism

These are press/opinion artifacts, not academic papers, and one honesty note
matters: the op-ed is written *as if by the builder*, and its two reviews are
*styled as* named newspapers. They are performance pieces about the project,
not genuine submissions from those outlets. "Submitting" them means pitching
the **op-ed** (optionally with its self-reviews as a meta-package) to an outlet
that runs reflective tech-culture essays and permits disclosed AI authorship.

- Candidate homes for the essay: *Wired* Ideas, *The Atlantic* (Technology),
  *Aeon* / *Noema* (long-form, ideas-forward and AI-authorship-curious), or a
  Substack/press-release from the repository itself.
- **[you]** Any real pitch is an outward, on-the-record act under your name and
  the outlet's AI policy; it is yours to send. The builder will draft the pitch
  email and a one-paragraph framing that discloses the authorship honestly (the
  disclosure *is* the hook).
- The two criticisms ship *with* the essay as the package's own commentary, or
  stay in the repository as the collection's self-documentation. They read
  best as a set.

---

## Prerequisite that unblocks almost everything — **[you]**

The repository is currently **private**. arXiv PDF-only works regardless, but
every paper cites the repository as the home of its audit trail, fonts, and
data, and the process paper is not meaningfully reviewable while it is closed.
Before Stage 3, and ideally before Stage 1:

- **[you]** Make the repo public, and mint a **Zenodo DOI** for the tagged
  release (Zenodo has a one-click GitHub integration; it needs your account).
  The DOI then goes into all four papers' "data availability" lines — the
  builder will add them once you have the DOI.

## What the builder does next, on your word

- Finalize cover letters once venues are confirmed.
- Draft the arXiv endorsement request and the press pitch.
- Produce arXiv source-compilable variants, if you want source rather than PDF.
- Insert the Zenodo DOI across all papers once it exists.
- Reformat any paper to a specific venue's template and limits.
