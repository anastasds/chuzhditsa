# arXiv submission — click-by-click

Verified against arXiv's current submission and endorsement help pages. The
two papers in Stage 1 are the typeface and orthography papers; the process
paper is Stage 3 (after the repo is public). Everything below is **[you]** —
these are the account, endorsement, and submit actions the builder cannot do.

## 0. One-time setup

1. Register at arxiv.org with a **personal or academic email — not the
   company (lindenpmg) address**; this project stays off the business identity.
   The registration email becomes the semi-public author contact on the record,
   so pick one you're content to keep. An academic address (if you have any
   affiliation) can auto-qualify you and skip endorsement; a personal address
   will not, so plan on the endorsement step below.
2. Add an ORCID iD to your profile if you have one (create one free at
   orcid.org — it's the author identifier journals will also want).

## 1. Endorsement (first submission only)

arXiv requires a first-time submitter to be endorsed in the category. You
start the submission (step 2 below), arXiv emails you an endorsement code and
link, and you send that to one person who has recently published in the
category. They click, and you're cleared — thereafter no endorsement is needed.

- For **cs.CL** or **cs.GR**, an endorser is anyone with a few recent arXiv
  papers in that category. A former classmate, a colleague in CS/linguistics,
  or an academic acquaintance is the usual route.
- Draft request email: `submission/endorsement-request.md`.
- Do **not** mass-email potential endorsers; arXiv considers that abuse. One
  person who knows you is enough.

## 2. Submit the typeface paper (repeat for the orthography paper)

1. arxiv.org → **START NEW SUBMISSION**.
2. **Upload**: `paper/typeface.pdf`. (PDF-only is accepted. arXiv prefers TeX
   for portability, but our XeLaTeX + system-font stack won't build on their
   farm; PDF is the right call, and the source is public in the repo.)
3. **Check/Process**: arXiv will note it's a PDF submission — fine, continue.
   Preview the rendered PDF it shows you.
4. **Metadata**:
   - **Title**: `The letter as a program: constructing the Chuzhditsa typeface`
   - **Authors**: `Stoyanovsky, Anastas`
   - **Abstract**: paste from `submission/abstracts.txt` (the plain-text block
     for this paper — LaTeX already stripped).
   - **Primary category**: `cs.GR`. **Cross-list**: `cs.DL`, `cs.CL`.
   - **Comments** (optional but do it): e.g.
     `19 pages. Fonts, build toolchain, and shaping-test harness at <repo/DOI>.
      Constructed and drafted by a language model under the author's direction;
      see companion process paper.`
   - **License**: **CC BY 4.0** recommended (open, compatible with every target
     journal). arXiv's non-exclusive default is also fine.
   - **ACM class / MSC** (optional): ACM `I.7.2` (Document Preparation) fits.
5. Accept the submission agreement and **Submit**. Submit before 14:00 US
   Eastern for next-cycle announcement.
6. Record the assigned ID (e.g. `arXiv:2601.XXXXX`) in `submission/PLAN.md`.

**Orthography paper**, same flow with:
- Title: `Chuzhditsa: a featural citation register for Cyrillic, from Bulgarian
  to the Slavic superset`
- Primary `cs.CL`, cross-list `cs.DL`; abstract from `abstracts.txt`.

## 3. After both are announced

- The two arXiv IDs go into each journal cover letter (`cover-letters.md`) and
  into the process paper's introduction before Stage 3.
- Cross-reference the companions to each other's arXiv IDs in a v2 update if
  you want (optional; a comment line is enough).

## Data-availability line to add once you have the Zenodo DOI

Paste this into each paper (the builder will place it precisely on your word):

> Data availability. The fonts, build toolchain, machine-readable audit
> dataset, and complete revision history are archived at
> <Zenodo DOI> and developed at <repository URL>.
