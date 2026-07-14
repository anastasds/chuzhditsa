#!/usr/bin/env python3
"""Emit the twenty-language audit in reviewer-inspectable forms, from the
same LANGS single source that generates the language guides:

  data/audit_20_languages.json   full structured dataset (notes in bg/en/uk)
  data/audit_20_languages.csv    flat per-example table (English notes)
  paper/audit_appendix.tex       Appendix A of the orthography paper

Run after any change to gen_docs.LANGS so paper, guides, and dataset
cannot drift apart."""
import csv, json, os, sys, unicodedata

sys.path.insert(0, os.path.dirname(__file__))
from gen_docs import LANGS

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Language-level audit facts (reference variety, declared mergers and
# losses), mirroring Table "tab:audit" of the paper. Keyed by the English
# language name used in LANGS.
META = {
 "English":      ("General American", "rhotic → р", "—"),
 "Mandarin":     ("Standard (Beijing)", "tʂ tɕ → ч; ʐ → ж", "tone sandhi; T1 = neutral tone"),
 "Hindi-Urdu":   ("Delhi", "ɦ → һ", "—"),
 "Spanish":      ("Castilian", "rhotics → р (β ð ɣ by positional rule)", "—"),
 "French":       ("Parisian", "ʁ → р; ɛ ɔ œ → е о ӧ; ɥ → ӱ", "—"),
 "Arabic (MSA)": ("Modern Standard Arabic", "χ → х; emphatics → plain", "—"),
 "Bengali":      ("Standard (Kolkata)", "ɔ → о", "—"),
 "Portuguese":   ("Brazilian", "ʁ → р; ɛ ɔ → е о", "—"),
 "Russian":      ("Standard", "ɕː → шч", "reduction (phonemic input)"),
 "Japanese":     ("Tokyo", "ɸ → ф; ɯ → у (conv.); ʑ → џ; ɴ → н; ɕ → ш (entrenched)", "pitch accent"),
 "German":       ("Standard", "ɛː/eː → е̄", "—"),
 "Korean":       ("Seoul", "tense = geminate", "—"),
 "Vietnamese":   ("Hanoi", "ɓ ɗ → б д", "6 tones → 4 marks; length under tone"),
 "Turkish":      ("Istanbul", "ɫ → л", "—"),
 "Italian":      ("Standard", "ɛ ɔ → е о; ʎʎ → ль", "—"),
 "Persian":      ("Tehran", "ɢ → қ", "ʔ dropped"),
 "Swahili":      ("Standard", "implosives → б д", "—"),
 "Greek":        ("Standard Modern", "—", "—"),
 "Polish":       ("Standard", "ʂ → ш; tʂ tɕ → ч", "—"),
 "Indonesian":   ("Standard", "—", "—"),
}

# Extension inventory a rendering can exercise: precomposed letters,
# combining marks, and modifier letters (data is NFC; ў ӣ etc. arrive
# composed, while а̨ т̢ е̌ о̄ arrive as base + combining mark).
EXT_LETTERS = set("ўҫҙӓӧӱңқғҳһѕџѫѧѩѭӣӯыъ" + "ўҫҙӓӧӱңқғҳһѕџѫѧѩѭӣӯыъ".upper() + "Ӏӏ")
EXT_MARKS = {"̀": "◌̀", "́": "◌́", "̄": "◌̄", "̆": "◌̆",
             "̌": "◌̌", "̢": "◌̢", "̨": "◌̨"}
EXT_MODS = {"ʰ", "ʱ"}
# precomposed carriers whose diacritic must still register in extensions_used
EXT_PRECOMPOSED = {"ѐ": "◌̀", "Ѐ": "◌̀", "ѝ": "◌̀", "Ѝ": "◌̀"}


def extensions_used(rendering):
    used, seen = [], set()
    for ch in rendering:
        tag = None
        if ch in EXT_LETTERS:
            tag = ch.lower()
        elif ch in EXT_MARKS:
            tag = EXT_MARKS[ch]
        elif ch in EXT_MODS:
            tag = ch
        elif ch in EXT_PRECOMPOSED:
            tag = EXT_PRECOMPOSED[ch]
        if tag and tag not in seen:
            seen.add(tag)
            used.append(tag)
    return used


def tex_escape(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}")):
        s = s.replace(a, b)
    return s


def build():
    langs_out, rows, n = [], [], 0
    for (names, examples) in LANGS:
        name_en = names[1]
        variety, mergers, losses = META[name_en]
        exts_lang, ex_out = [], []
        for (word, ipa, chz, notes) in examples:
            n += 1
            exts = extensions_used(chz)
            for e in exts:
                if e not in exts_lang:
                    exts_lang.append(e)
            ex_out.append(dict(word=word, ipa=ipa, chuzhditsa=chz,
                               extensions=exts,
                               note_bg=notes[0], note_en=notes[1], note_uk=notes[2]))
            rows.append([name_en, variety, word, ipa, chz,
                         " ".join(exts), notes[1], mergers, losses])
        langs_out.append(dict(language=name_en, name_bg=names[0], name_uk=names[2],
                              reference_variety=variety, mergers=mergers,
                              losses=losses, extensions_exercised=exts_lang,
                              examples=ex_out))

    meta = dict(
        title="Chuzhditsa twenty-language audit",
        description="Full example set of the coverage audit: for each language, "
                    "the declared reference variety, the extension letters and "
                    "marks each rendering exercises, and the declared mergers "
                    "and losses. Classification follows the paper's Method: "
                    "exact / conventional merger / declared loss; mergers and "
                    "losses are declared per language, and every rendering not "
                    "engaging a declared merger or loss is exact.",
        classification=["exact", "conventional merger", "declared loss"],
        languages=len(langs_out), examples=n, encoding="NFC",
    )

    with open(os.path.join(ROOT, "data", "audit_20_languages.json"), "w") as f:
        json.dump(dict(meta=meta, languages=langs_out), f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "data", "audit_20_languages.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["language", "reference_variety", "word", "ipa", "chuzhditsa",
                    "extensions_used", "note", "declared_mergers", "declared_losses"])
        w.writerows(rows)

    # ---- Appendix A ---------------------------------------------------------
    L = []
    L.append("% AUTO-GENERATED by tools/gen_audit.py from tools/gen_docs.py LANGS.")
    L.append("% Do not edit by hand; regenerate.")
    L.append(r"\begin{longtable}{@{}p{0.22\linewidth}p{0.19\linewidth}p{0.16\linewidth}p{0.30\linewidth}@{}}")
    L.append(r"\caption{The full 125-item audit example set.}\label{tab:auditfull}\\")
    L.append(r"\toprule Source & IPA & Chuzhditsa & Notes \\ \midrule \endfirsthead")
    L.append(r"\toprule Source & IPA & Chuzhditsa & Notes \\ \midrule \endhead")
    L.append(r"\bottomrule \endlastfoot")
    for lang in langs_out:
        hdr = r"\textbf{%s} (%s)" % (tex_escape(lang["language"]), tex_escape(lang["reference_variety"]))
        decl = []
        if lang["mergers"] != "—":
            decl.append("mergers: {\\ipafont %s}" % tex_escape(lang["mergers"]))
        if lang["losses"] != "—":
            decl.append("declared loss: {\\ipafont %s}" % tex_escape(lang["losses"]))
        if decl:
            hdr += " — " + "; ".join(decl)
        L.append(r"\multicolumn{4}{@{}p{0.97\linewidth}@{}}{%s} \\*" % hdr)
        for ex in lang["examples"]:
            ipa = ex["ipa"].strip("/")
            # Arial Unicode MS lacks a few IPA combining marks (the Korean
            # fortis U+0348); the body font has them, so such rows fall back
            ipa_tex = (r"{\normalfont/%s/}" if "͈" in ipa else r"\ph{%s}") % tex_escape(ipa)
            note_font = r"\normalfont" if "͈" in ex["note_en"] else r"\ipafont"
            L.append(r"\src{%s} & %s & \cz{%s} & {%s\footnotesize %s} \\" %
                     (tex_escape(ex["word"]), ipa_tex,
                      tex_escape(ex["chuzhditsa"]), note_font, tex_escape(ex["note_en"])))
        L.append(r"\addlinespace[6pt]")
    L.append(r"\end{longtable}")
    with open(os.path.join(ROOT, "paper", "audit_appendix.tex"), "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"audit dataset: {len(langs_out)} languages, {n} examples")
    return n


if __name__ == "__main__":
    build()
