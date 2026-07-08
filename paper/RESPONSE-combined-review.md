# Response to the combined review of the paired submission

**Papers:** *Chuzhditsa: a featural citation register for Cyrillic, from Bulgarian to the Slavic superset* (orthography paper) and *The letter as a program: constructing the Chuzhditsa typeface* (typeface paper).

We thank the reviewer for a careful reading of both manuscripts as a pair. We accept the review's program in full: every requested cross-paper edit has been made, the audit dataset has been made archival and is now also printed in the orthography paper as an appendix, and the repository has been tagged and released. Point-by-point responses follow; all quotations are from the review.

---

## 1. "Use the same system description in both abstracts."

Done, and taken further than requested. The orthography paper's **title** has been changed from "a featural loanword register" to **"a featural citation register"** so that the title, abstract, and body now use the same umbrella term. The typeface paper's footnote citation of the companion title has been updated to match, and its introduction now mirrors the exact phrasing: it introduces Chuzhditsa as "a *phonological citation register* for pan-Slavic Cyrillic — a system for writing foreign words, names, and pedagogical examples so a Cyrillic reader can recover the source pronunciation, with loanword marking as a secondary use."

## 2. "Standardize 'loanword register' vs 'phonological citation register.'"

Done. A sweep of both manuscripts finds **zero** remaining occurrences of "loanword register." "Citation register" is the umbrella term throughout; the loan-marking function is referred to only as the secondary, optional use (and the typeface paper's discussion of the katakana condition now speaks of "the visual register").

## 3. "Fix the featural wording."

Done. The introduction sentence that read "a small set of diacritic operations — each meaning exactly one phonetic feature" now reads: "a small set of recurrent diacritic operations — **most featurally atomic, one (the hook) relational to its base letter** (§ hook section cross-reference) — derives the entire extension inventory." This matches both the paper's own later analysis of the hook and the companion paper's wording.

## 4. "Fix the builder-size mismatch" (∼300 vs ∼700 lines).

Done, by the route the review recommended for Section 8 generally. The orthography paper no longer states a line count at all: the implementation section now describes "a compact parametric builder," states in its second sentence that "the construction itself — terminals, joins, the optical-correction canon, fitting, and the small-size behavior of the marks — is the subject of the companion paper; here we state only its orthographic consequences," and keeps only the orthographically load-bearing material (two-case architecture, computed GPOS anchors, GSUB fusion as executable rules, HarfBuzz-verified falsifiability). In the process we also removed a stale description of a superseded expansion algorithm ("per-segment rectangles and per-vertex discs" — the v1 engine that the companion paper's Figure 3 shows precisely as the *before* case); the reviewer's instinct that Section 8 was "slightly risky" was correct. The line count now appears only in the typeface paper ("roughly seven hundred lines"), which is the paper that documents the builder.

## 5. "Do not make the typeface paper depend on the reader accepting the orthography paper."

Done. The typeface paper's introduction now states explicitly: "The construction method is evaluated on its own terms throughout: nothing below depends on the reader's verdict on the register's adoption prospects. Given a designed orthographic register — this one or another — the question this paper answers is what it takes to make it typographically real."

## 6. "Make repository evidence archival" — the audit dataset.

Done, in three coordinated forms, all generated from the **same source table** that produces the per-language guides, so they cannot drift:

- **`data/audit_20_languages.json`** — the full structured dataset: for each of the twenty languages, the declared reference variety, declared mergers, declared losses, the extension letters exercised, and every example with source form, source-variety IPA, Chuzhditsa rendering, per-example extension usage, and notes in three languages.
- **`data/audit_20_languages.csv`** — the same, flattened to one row per example for spreadsheet inspection.
- **Appendix A of the orthography paper** — the complete example set printed in the manuscript itself, with the Chuzhditsa column set live in the typeface (GSUB fusion and GPOS anchoring active), grouped by language with reference variety and declared mergers/losses restated in each group header.

The classification scheme is stated in the dataset's metadata and in the appendix headnote: mergers and losses are declared per language (as in the paper's §Method), and every rendering not engaging a declared merger or loss is *exact*. One count correction resulted: the example set numbers **125**, not 126 as previously stated; both mentions have been corrected. This is precisely the kind of error the reviewer's "reviewer-proof the dataset" recommendation is designed to catch, and we are glad it surfaced now.

The repository is tagged and released as **v2.4** with the fonts, both compiled manuscripts, and the dataset attached as release assets. A DOI-issuing archive deposit (Zenodo) is planned at submission time.

## 7. "Move some sociolinguistic material out of the Chuzhditsa paper if length is tight."

Deferred, per the review's own framing ("if length is tight"). No venue length constraint currently binds; if one does, the adoption section is the agreed first cut, before any of the mapping, audit, or implementation material.

## On the perception study

We adopt the review's framing exactly: the reader-facing claims — that Cyrillic readers can read the extensions, and that the Glagolitic-derived style reads as *register* rather than as archaism — are the subject of the **next paper**, not a limitation patchable in revision. Both manuscripts already scope this honestly and now do so in matching terms.

## On packaging strategy

We follow the recommendation: the two papers will be offered as a paired package where the venue allows, with the typeface paper positioned as the lead for technical credibility and the orthography paper as the conceptual companion. The cross-references between them have been harmonized as described above, and each paper now survives being read alone.

---

### Summary of changes

| # | Review point | Disposition |
|---|---|---|
| 1 | Same system description in both abstracts | Done (title change + mirrored phrasing) |
| 2 | Terminology standardization | Done (0 occurrences of the old term remain) |
| 3 | Featural overclaim | Done (reworded per review) |
| 4 | 300 vs 700 lines | Done (count removed from orthography paper; §8 now a pointer) |
| 5 | Typeface paper independence | Done (explicit scoping sentence added) |
| 6 | Archival audit evidence | Done (JSON + CSV + printed Appendix A; count corrected 126→125; v2.4 release) |
| 7 | Trim adoption section | Deferred until a length constraint binds, per review |
