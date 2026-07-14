# Submitting to Digital Creativity (Taylor & Francis) — checklist

You already have a submission started in the T&F portal (Research Article).
Upload these:

| File | Portal slot |
|---|---|
| `paper/process_dc_anon.pdf` | **Main document (anonymized)** — 27 pp, [ANON] placeholders, verified clean |
| `paper/process_dc.pdf` | Complete/non-anonymized version, if the portal asks for one |
| `paper/dc_titlepage.pdf` | **Title page** (author, word count, AI-use declaration, data availability, bio) |
| `submission/dc_cover_letter.txt` | Cover letter — paste into the form |

Metadata to paste:
- Title: *The critic and the builder: how the Chuzhditsa papers were written*
- Abstract: the 147-word paragraph from p. 1 of the DC PDFs
- Keywords: `artificial intelligence; creative collaboration; criticism; design process; large language models; type design`

Notes:
- **AI policy**: T&F's policy forbids listing AI as an author and requires disclosure
  of AI use — the title page carries an explicit declaration, the author note
  discloses the drafting, and the manuscript analyzes its own case in the
  Authorship section. This is the honest-compliance posture; the editor decides.
- **Word count**: ~9,400 body words. If the form enforces a lower cap (some T&F
  arts journals cap research articles at 8,000), stop and tell me — I'll produce
  a trimmed cut rather than have you misdeclare.
- References are author-year; T&F journal style conversion (if requested) happens
  at revision.
- Generated files: `tools/gen_dc.py` regenerates both versions from the canonical
  `paper/process.tex` — never hand-edit the `_dc` files.
