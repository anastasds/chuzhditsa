#!/usr/bin/env python3
"""Render a proof sheet of the Chuzhditsa fonts for visual inspection."""
import sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
FONTS = os.path.join(HERE, "..", "fonts")

LINES = [
    ("Regular", 64, "абвгдежзийклмнопр"),
    ("Regular", 64, "стуфхцчшщъьыюя"),
    ("Regular", 64, "ў ѕ ѫ ѧ џ һ ӓ ӧ ӱ ы"),
    ("Regular", 64, "ң қ ғ ҳ ҙ ҫ Ӏ ӣ ӯ"),
    ("Regular", 64, "тʰа кʰа бʱарат т̢ик"),
    ("Regular", 64, "ма̀ ма́ ма̌ ма̄ а̨ ӧ"),
    ("Regular", 56, "ўикенд ҫӓңкс ҙис бърҫдей"),
    ("Regular", 56, "муҳаммад һилал халид Ӏумар"),
    ("Bold", 56, "чуждица болд: ўърлд џаз"),
    ("Italic", 56, "чуждица италик: крўаса̨"),
    ("BoldItalic", 56, "болд италик: гӧте мӱнхен"),
]

W = 1480
y, pad = 30, 26
img = Image.new("RGB", (W, 40 + sum(int(s*2.1) + pad for _, s, _ in LINES)), "white")
d = ImageDraw.Draw(img)
for style, size, text in LINES:
    f = ImageFont.truetype(os.path.join(FONTS, f"Chuzhditsa-{style}.ttf"), size)
    d.text((30, y), text, font=f, fill="black")
    y += int(size*2.1) + pad
img.save(os.path.join(HERE, "proof.png"))
print("ok", img.size)
