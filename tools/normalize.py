#!/usr/bin/env python3
"""Normalize chuzhditsa text to its canonical encoding.

Canonical form: NFC; ligature sequences (нь ль ьѧ ьѫ) rather than precomposed
њ љ ѩ ѭ; apostrophe U+2019; palochka U+04C0. Also repairs NFKC damage
(Latin h after a Cyrillic stop back to the aspiration mark U+02B0).

Usage: python3 tools/normalize.py [file ...]   (or stdin -> stdout)
"""
import re, sys, unicodedata

FOLD = {
    "љ": "ль",  # љ -> ль
    "Љ": "ЛЬ",  # Љ -> ЛЬ
    "њ": "нь",  # њ -> нь
    "Њ": "НЬ",  # Њ -> НЬ
    "ѩ": "ьѧ",  # ѩ -> ьѧ
    "Ѩ": "ЬѦ",  # Ѩ -> ЬѦ
    "ѭ": "ьѫ",  # ѭ -> ьѫ
    "Ѭ": "ЬѪ",  # Ѭ -> ЬѪ
    "ӏ": "Ӏ",        # lowercase palochka -> caseless
    "І": "Ӏ",        # Ukrainian І used as palochka stays І — do NOT fold; see below
}
del FOLD["І"]  # І is a real letter; never fold it

ASP_REPAIR = re.compile(r"(?<=[тткпчбдгџТКПЧБДГЏ])h")
ASPV_REPAIR = re.compile(r"(?<=[бдгџБДГЏ])ɦ")  # ɦ after voiced stop

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    for k, v in FOLD.items():
        text = text.replace(k, v)
    # apostrophe: straight quote inside a word -> U+2019
    text = re.sub(r"(?<=\w)'(?=\w)", "’", text)
    # NFKC damage repair: Latin h/ɦ after a Cyrillic obstruent -> modifier letters
    text = ASP_REPAIR.sub("ʰ", text)
    text = ASPV_REPAIR.sub("ʱ", text)
    return text

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            with open(path, encoding="utf-8") as f:
                data = f.read()
            out = normalize(data)
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"normalized {path}" + (" (changed)" if out != data else " (no change)"))
    else:
        sys.stdout.write(normalize(sys.stdin.read()))
