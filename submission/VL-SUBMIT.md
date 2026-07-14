# Submitting to Visible Language — checklist

Everything is prepared; the clicks are yours.

## Files

| File | Role |
|---|---|
| `paper/typeface_vl.pdf` | **Complete version** (18 pp, author-identified) |
| `paper/typeface_vl_anon.pdf` | **Anonymized version** ([ANON] placeholders, docinfo scrubbed) |
| `submission/vl_cover_letter.txt` | Cover letter + author bio (<100 words) |

Both are generated from `paper/typeface.tex` by `tools/gen_vl.py` — if the canonical
paper changes, regenerate; never hand-edit the `_vl` files.

## Steps

1. Go to https://journals.uc.edu/index.php/vl/about/submissions (OJS; register/log in
   as author — use anastas@stoyanovs.ky, affiliation "Independent researcher").
2. Upload BOTH versions (the platform asks for complete + anonymized). Keep the
   filenames as-is — they carry no author identity.
3. Metadata: title *The letter as a program: how the Chuzhditsa typeface works*;
   abstract = the 258-word single paragraph from p. 1 (no citations); keywords
   (3–6, alphabetical, semicolons): `Cyrillic; OpenType; optical corrections;
   parametric type design; type engineering; writing systems`.
4. Paste the "Implications for practice" block (189 words, p. 1–2) where the form
   asks for it, and the author bio from the cover letter.
5. Paste/attach the cover letter; submit.

## Notes

- **Review model**: double-blind; the anonymized PDF is verified clean (no name,
  email, repo, LingBuzz number, or PDF-metadata author). The repo is public and
  findable — as with WL&L, that's normal preprint reality; don't cite it in the
  anonymized text (it's [ANON]-ed).
- **References**: converted to APA 7th (VL's requirement) in the `_vl` versions;
  the canonical paper keeps USS.
- **Figures**: on acceptance VL wants separate PNG/TIFF at 300 ppi in RGB *and*
  CMYK — the PNGs in `paper/figures/` are the sources; CMYK conversion is a
  10-minute batch job at that point.
- **Timing**: Vol 60.3's deadline (1 July 2026) has passed; a rolling submission
  lands in the next regular issue. The Sept 2 special issue (Typographic
  Landscapes) is off-topic for this paper.
- Venue-fit hook the cover letter uses: the Knuth–Hofstadter meta-font exchange
  ran in *Visible Language* 16(1)/16(4) — this paper is a working resolution of
  that debate, in the same pages.
