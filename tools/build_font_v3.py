#!/usr/bin/env python3
"""Build the Chuzhditsa v3 families — 2b, Grotesk, Serif, Inline — as TTF+OTF, 4 styles each.

Direct port of the browser-side reference builder (fontbuild.js) that produced
the approved v3 binaries; slots next to build_font.py in tools/. Same fontTools
stack, same output conventions, writes to ../fonts/v3/.

v3 engine features vs build_font.py:
  - tangent-angle contrast: w(theta) = wh + (wv-wh)|sin theta|^1.3, wh = 0.90 wv
  - two-case skeletons on x-height 500 / cap 700; fitting is a per-family
    scalar sidebearing over per-glyph advances baked into the skeletons
    (the R/F/D/T/A/O side classes drive kerning only, not fitting)
  - elliptical bowls: +48u vertical radius, overshooting the rounded-terminal
    envelope, not the guides
  - aperture parameter (55 deg) with bar termini flush at arc tips: r cos(.75a)
  - Bold buys back its ink: sidebearing 50, frame x1.10, kerns x0.7
  - 6-class kern matrix (round/flat/diag/top-bar/apex/aperture), 30 rules,
    compiled through feaLib as GPOS
  - family parameters: cap finish (round/butt), stem-slab serifs, contrast,
    diagonal weight clamp, vertical scale — four faces from one skeleton set
    (2b round-cap original; Grotesk for UI; Serif for long-form web reading;
    Inline weight-matched to Times for citation inside serif text)
  - round caps/joins: strokes expand to per-segment quads + end discs,
    then boolean-unioned into disjoint outlines (skia-pathops) so coverage-
    summing rasterizers cannot darken the overlap seams into a fake bold

Full character set: the pan-Slavic superset, the combining-mark GPOS anchors,
and the ligature stratum (yus fusions, soft-sign fusions, ejective digraphs)
are ALL built here, per family, so every family carries the same ~175 codepoints
plus liga + mark + kern features (merged from the migration in build_font.py).

Run:  python3 tools/build_font_v3.py
Reproducible: head timestamps are pinned via SOURCE_DATE_EPOCH (overridable
in the environment), so identical sources produce byte-identical binaries.
"""
import math, os
os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")  # 2026-01-01T00:00:00Z
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import pathops

UPM = 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "fonts", "v3")

# ------------------------------------------------------------- side classes
# two chars per glyph: [left side, right side]
# R round | F flat | D diagonal/open | T top-bar overhang | A apex | O aperture
SIDE = {
    "о": "RR", "с": "RO", "е": "RR", "ҫ": "RO", "з": "OR", "ѕ": "RR", "ҙ": "OR",
    "ӧ": "RR", "ф": "RR", "ё": "RR", "ә": "RR",
    "а": "RF", "ъ": "FR", "в": "FR", "б": "FR", "ь": "FR", "ю": "FR", "р": "FR",
    "н": "FF", "и": "FF", "ц": "FF", "м": "FF", "п": "FF", "ш": "FF", "щ": "FF",
    "џ": "FF", "ң": "FF", "й": "FF", "ӣ": "FF", "ы": "FF", "һ": "FF", "ӏ": "FF",
    "к": "FD", "қ": "FD", "г": "FT", "ғ": "FT", "т": "TT",
    "ч": "DF", "я": "DF",
    "у": "DD", "ж": "DD", "ў": "DD", "х": "DD", "ҳ": "DD", "ӱ": "DD", "ӯ": "DD",
    "д": "AD", "л": "AD", "ѫ": "AD", "ѧ": "AD",
    # migrated superset (extension letters inherit their base letters' sides)
    "э": "OR", "є": "RO", "ѳ": "RR", "і": "FF", "ї": "FF", "ј": "FF",
    "ђ": "FF", "ћ": "FF", "ѓ": "FT", "ќ": "FD", "љ": "AR", "њ": "FR",
    "ѩ": "FD", "ѭ": "FD", "ѐ": "RR", "ѝ": "FF", "ӓ": "RF", "ґ": "FT",
}
# combining marks (drawn trailing at negative x, v2.5 geometry; GPOS mark
# anchors do the placement, so the drawn spot only matters as the
# unanchored fallback) and the ligature stratum, both ported from
# build_font.py. Lookup order is orthographic law: yus fusion first,
# or н/л consume the soft sign before ьѧ can fuse (paper, Fig. 12).
TOPMARKS = {"\u0300": [("L", -270, 820, -400, 970)],
            "\u0301": [("L", -390, 820, -260, 970)],
            "\u0304": [("L", -490, 880, -170, 880)],
            "\u030C": [("L", -450, 970, -330, 850), ("L", -330, 850, -210, 970)],
            "\u0308": [("D", -435, 870, 26), ("D", -225, 870, 26)],
            "\u0306": [("A", -330, 930, 130, 205, 335)]}
BOTMARKS = {"\u0328": [("L", -330, 0, -385, -80), ("L", -385, -80, -275, -150)],
            "\u0322": [("L", -300, 0, -300, -150), ("L", -300, -150, -210, -150)]}
OVERLAYS = {"\u0335": [("L", -450, 370, -215, 370)]}
BOT_X = {"т": 240, "р": 55, "Т": 264, "Р": 50}
YUS_LIGA = [("ь", "ѧ", "ѩ"), ("й", "ѧ", "ѩ"), ("ь", "ѫ", "ѭ"), ("й", "ѫ", "ѭ"),
            ("Ь", "Ѧ", "Ѩ"), ("Й", "Ѧ", "Ѩ"), ("Ь", "Ѫ", "Ѭ"), ("Й", "Ѫ", "Ѭ")]
SOFT_LIGA = [("н", "ь", "њ"), ("л", "ь", "љ"), ("Н", "Ь", "Њ"), ("Л", "Ь", "Љ")]
EJECTIVES = [("т", "tpal"), ("к", "kpal"), ("ц", "tspal"), ("ч", "chpal"), ("п", "ppal")]
KERN = {
    "RR": -14, "RF": -6, "FR": -6, "FF": 0, "DD": -28, "DR": -20, "RD": -20,
    "DF": -14, "FD": -14, "TT": 0, "TR": -12, "RT": -12, "TF": -4, "FT": -4,
    "TD": -16, "DT": -16, "RA": -22, "FA": -16, "DA": -28, "TA": -95,
    "OO": -34, "OR": -16, "OF": -8, "OD": -24, "OA": -26, "OT": -14,
    "FO": -10, "RO": -18, "DO": -24, "TO": -16,
}

# --------------------------------------------------------------- skeletons
# stroke kinds: ("L",x1,y1,x2,y2) ("A",cx,cy,r,a0,a1) ("E",cx,cy,rx,ry,a0,a1)
# ("D",cx,cy,r). All coordinates derive from the parameter sheet (p) — a bare
# number that could vary by style is a style bug (see the paper, "The literal
# audit").

def glyph_set(p):
    w, ov, ap = p["wv"], p["ov"], p["aperture"]
    R = 250 - w / 2 + ov          # x-height bowl radius
    Ra = 225 - w / 2 + ov         # a/р bowl radius base
    R7 = 350 - w / 2 + ov         # cap bowl radius
    Rv, R7v = R + 48, R7 + 48     # vertical radii: overshoot the cap envelope
    Rav = Rv - (0 if w > 100 else 16)  # narrow a/р bowl reads taller: reduced allowance
    ct = math.cos(math.radians(ap * 0.75))  # bar terminus: flush at arc tips
    ct_e = math.cos(math.radians(ap * 0.45))  # closed-е bar terminus
    Rab = Ra - 12                 # a/р bowl, trimmed (review: reads oversized)
    dr = max(26, min(w * 0.60, 62))  # diacritic dot radius: weight-derived (eval pass)

    def L(a, b): return ("L", a[0], a[1], b[0], b[1])
    def LD(a, b): return ("LD", a[0], a[1], b[0], b[1])  # diagonal: clamped by fam["diagClamp"]
    def A(cx, cy, r, a0, a1): return ("A", cx, cy, r, a0, a1)
    def E(cx, cy, rx, ry, a0, a1): return ("E", cx, cy, rx, ry, a0, a1)
    def DOT(x, y, r): return ("D", x, y, r)
    def breve(cx, cy): return A(cx, cy, 70, 195, 345)
    def dots(y): return [DOT(165, y, dr), DOT(335, y, dr)]
    def macron(y): return L((120, y), (380, y))

    G = {}
    G["о"] = dict(adv=486, s=[E(243, 250, R, Rv, 0, 360)])
    # с/ҫ open on the right, so the aperture recedes there; a 420 advance
    # gives them a normal right sidebearing instead of the round-letter default
    # that left ҫӓ, са, со gaping (typographer/kerning fix)
    G["с"] = dict(adv=420, s=[E(250, 250, R, Rv, ap, 360 - ap)])
    # е: a closed bowl (aperture ap·0.45) so its silhouette differs from the
    # open epsilon of є by shape, not merely by bar length (typographer review)
    G["е"] = dict(adv=500, s=[E(250, 250, R, Rv, ap * 0.45, 360 - ap * 0.45),
                              L((70, 270), (250 + R * ct_e, 270))])
    G["ё"] = dict(adv=500, s=G["е"]["s"] + dots(640))
    G["н"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 250), (445, 250))])
    G["и"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 70), (445, 430))])
    G["й"] = dict(adv=490, s=G["и"]["s"] + [breve(250, 685)])
    G["к"] = dict(adv=470, s=[L((40, 0), (40, 500)), L((40, 250), (400, 500)),
                              L((40, 250), (420, 0))])
    G["а"] = dict(adv=500, s=[E(428 - Rab, 250, Rab, Rav, 0, 360),
                              L((455, 0), (455, 500))])
    G["ъ"] = dict(adv=470, s=[L((0, 500), (155, 500)), L((155, 0), (155, 500)),
                              L((155, 280), (300, 280)), A(300, 140, 140, 90, -90),
                              L((300, 0), (155, 0))])
    G["ь"] = dict(adv=365, s=[L((40, 0), (40, 500)), L((40, 280), (185, 280)),
                              A(185, 140, 140, 90, -90), L((185, 0), (40, 0))])
    G["ы"] = dict(adv=520, s=G["ь"]["s"] + [L((480, 0), (480, 500))])
    G["ч"] = dict(adv=500, s=[L((40, 500), (40, 390)), A(250, 390, 210, 180, 360),
                              L((460, 0), (460, 500))])
    G["у"] = dict(adv=500, s=[L((40, 500), (268, 80)), L((460, 500), (150, -180))])
    G["ў"] = dict(adv=500, s=G["у"]["s"] + [breve(254, 685)])
    G["ӱ"] = dict(adv=500, s=G["у"]["s"] + dots(660))
    G["ӯ"] = dict(adv=500, s=G["у"]["s"] + [macron(650)])
    G["ж"] = dict(adv=500, s=[L((250, 0), (250, 500)), LD((250, 250), (30, 500)),
                              LD((250, 250), (470, 500)), LD((250, 250), (30, 0)),
                              LD((250, 250), (470, 0))])
    G["д"] = dict(adv=500, s=[L((250, 500), (60, 0)), L((250, 500), (440, 0)),
                              L((20, 0), (480, 0)), L((20, 0), (20, -70)),
                              L((480, 0), (480, -70))])
    G["ц"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 0), (445, 0)), L((445, 0), (445, -110))])
    G["џ"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 0), (445, 0)), L((250, 0), (250, -110))])
    # big yus: the canonical inverted-triangle body (▽ under the bar) over a
    # central stem with flared trident legs — not a bare pillar (Times/Georgia/
    # STIX all draw the ▽; the earlier skeleton omitted it)
    G["ѫ"] = dict(adv=500, s=[L((88, 500), (412, 500)),
                              L((88, 500), (250, 235)), L((412, 500), (250, 235)),
                              L((250, 235), (250, 0)),
                              L((250, 140), (88, 0)), L((250, 140), (412, 0))])
    # small yus: an 'A' with the yus's inner element — a central stem hanging
    # from the crossbar to the baseline (the Arial-Unicode form; without it ѧ
    # is a bare A indistinguishable from А)
    G["ѧ"] = dict(adv=500, s=[L((250, 500), (70, 0)), L((250, 500), (430, 0)),
                              L((146, 210), (354, 210)), L((250, 210), (250, 0))])
    G["қ"] = dict(adv=470, s=G["к"]["s"] + [L((420, 0), (420, -110))])
    G["ҫ"] = dict(adv=420, s=[E(250, 250, R, Rv, ap, 360 - ap),
                              L((250, 250 - Rv), (250, 250 - Rv - 135))])
    G["б"] = dict(adv=470, s=[L((40, 0), (40, 500)), L((40, 500), (360, 500)),
                              L((40, 280), (210, 280)), E(210, 140, 168, 140, 90, -90),
                              L((210, 0), (40, 0))])
    G["в"] = dict(adv=375, s=[L((40, 0), (40, 500)), L((40, 500), (185, 500)),
                              L((40, 250), (185, 250)), L((40, 0), (185, 0)),
                              E(185, 375, 150, 125, 90, -90), E(185, 125, 150, 125, 90, -90)])
    G["г"] = dict(adv=440, s=[L((40, 0), (40, 500)), L((40, 500), (400, 500))])
    G["ғ"] = dict(adv=440, s=G["г"]["s"] + [L((0, 310), (240, 310))])
    G["з"] = dict(adv=455, s=[E(245, 378, 158, 134, 150, -80),
                              E(245, 127, 165, 139, 85, -165)])
    G["ҙ"] = dict(adv=455, s=G["з"]["s"] + [L((245, 0), (245, -135))])
    G["ѕ"] = dict(adv=455, s=[E(245, 381, 158, 131, 45, 270),
                              E(245, 119, 165, 131, 90, -135)])
    G["л"] = dict(adv=500, s=[L((250, 500), (70, 0)), L((250, 500), (430, 0))])
    G["м"] = dict(adv=560, s=[L((40, 0), (40, 500)), L((520, 0), (520, 500)),
                              L((40, 500), (280, 160)), L((520, 500), (280, 160))])
    G["п"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 500), (445, 500))])
    G["р"] = dict(adv=520, s=[L((55, -200), (55, 500)),
                              E(82 + Rab, 250, Rab, Rav, 0, 360)])
    G["т"] = dict(adv=480, s=[L((240, 0), (240, 500)), L((30, 500), (450, 500))])
    G["ф"] = dict(adv=560, s=[E(280, 250, R, Rv, 0, 360), L((280, -170), (280, 650))])
    G["х"] = dict(adv=480, s=[LD((50, 500), (430, 0)), LD((430, 500), (50, 0))])
    G["ҳ"] = dict(adv=480, s=G["х"]["s"] + [L((430, 0), (430, -110))])
    G["ш"] = dict(adv=600, s=[L((40, 0), (40, 500)), L((300, 0), (300, 500)),
                              L((560, 0), (560, 500)), L((40, 0), (560, 0))])
    G["щ"] = dict(adv=600, s=G["ш"]["s"] + [L((560, 0), (560, -110))])
    G["ю"] = dict(adv=605, s=[L((40, 0), (40, 500)), L((40, 250), (172, 250)),
                              E(370, 250, 220 - w / 2 + ov, Rv, 0, 360)])
    G["я"] = dict(adv=480, s=[L((440, 0), (440, 500)), L((440, 500), (190, 500)),
                              E(190, 390, 150, 110, 90, 270), L((190, 280), (440, 280)),
                              L((300, 280), (80, 0))])
    G["ң"] = dict(adv=490, s=G["н"]["s"] + [L((445, 0), (445, -110))])
    G["һ"] = dict(adv=500, s=[L((40, 0), (40, 700)), A(250, 290, 210, 0, 180),
                              L((460, 0), (460, 290))])
    # ә (schwa, U+04D9): an 'e' rotated 180° — aperture at the upper right and a
    # mid bar, so it does not collide with э (backwards-e, aperture on the left)
    G["ә"] = dict(adv=500, s=[E(250, 250, R, Rv, 55 + ap * 0.6, 415 - ap * 0.6),
                              L((250 - R * ct, 250), (250 + R * 0.85, 250))])
    G["ӧ"] = dict(adv=486, s=[E(243, 250, R, Rv, 0, 360)] + dots(640))
    G["ӣ"] = dict(adv=490, s=G["и"]["s"] + [macron(650)])
    G["ӏ"] = dict(adv=220, s=[L((110, 0), (110, 700))])
    # ------------------------------------------- migrated pan-Slavic superset
    G["э"] = dict(adv=500, s=[E(250, 250, R, Rv, ap * 0.75 + 180, 360 - ap * 0.75 + 180),
                              L((250 - R * 0.30, 270), (250 + R * 0.92, 270))])
    # є carries a half-bar from the bowl's centre to the arc tips — е's
    # full bar is what the revision's round е took over, so the pair's
    # contrast must live in the bar length (instrumented: 0 px before this)
    G["є"] = dict(adv=500, s=[E(250, 250, R, Rv, ap, 360 - ap),
                              L((250, 270), (250 + R * math.cos(math.radians(ap)), 270))])
    G["ѳ"] = dict(adv=486, s=[E(243, 250, R, Rv, 0, 360),
                              L((243 - R * 0.92, 250), (243 + R * 0.92, 250))])
    G["і"] = dict(adv=330, s=[L((165, 0), (165, 500)), DOT(165, 650, dr)])
    G["ї"] = dict(adv=330, s=[L((165, 0), (165, 500)), DOT(82, 650, dr), DOT(248, 650, dr)])
    G["ј"] = dict(adv=440, s=[L((300, -30), (300, 500)), A(200, -72, 103, 0, -150),
                              DOT(300, 650, dr)])
    G["ћ"] = dict(adv=500, s=[L((40, 0), (40, 700)), L((0, 560), (210, 560)),
                              A(250, 290, 210, 0, 180), L((460, 0), (460, 290))])
    G["ђ"] = dict(adv=500, s=[L((40, 0), (40, 700)), L((0, 560), (210, 560)),
                              A(250, 290, 210, 0, 180), L((460, -40), (460, 290)),
                              A(355, -40, 105, 0, -150)])
    G["ѓ"] = dict(adv=440, s=G["г"]["s"] + [L((230, 610), (300, 700))])
    G["ќ"] = dict(adv=470, s=G["к"]["s"] + [L((250, 610), (320, 700))])
    G["ѐ"] = dict(adv=500, s=G["е"]["s"] + [L((215, 700), (285, 610))])
    G["ѝ"] = dict(adv=490, s=G["и"]["s"] + [L((215, 700), (285, 610))])
    G["ӓ"] = dict(adv=500, s=G["а"]["s"] + [DOT(190, 640, dr), DOT(360, 640, dr)])
    G["ґ"] = dict(adv=440, s=G["г"]["s"] + [L((400, 500), (400, 600))])
    G["њ"] = dict(adv=730, s=[L((40, 0), (40, 500)), L((400, 0), (400, 500)),
                              L((40, 250), (400, 250)), L((400, 280), (545, 280)),
                              A(545, 140, 140, 90, -90), L((545, 0), (400, 0))])
    # љ: the bowl attaches to a vertical only — the right leg breaks
    # diagonal-then-vertical (the Љ construction the first repair loop proved)
    G["љ"] = dict(adv=690, s=[L((230, 500), (60, 0)), L((230, 500), (400, 240)),
                              L((400, 240), (400, 0)), L((400, 240), (520, 240)),
                              A(520, 120, 120, 90, -90), L((520, 0), (400, 0))])
    G["ѩ"] = dict(adv=640, s=[L((70, 0), (70, 500)), L((70, 250), (310, 250)),
                              L((390, 500), (230, 0)), L((390, 500), (550, 0)),
                              L((297, 210), (483, 210)), L((390, 210), (390, 0))])
    # iotated big yus: iota element + the corrected big-yus body (▽ + stem + legs)
    G["ѭ"] = dict(adv=680, s=[L((70, 0), (70, 500)), L((70, 500), (620, 500)),
                              L((300, 500), (450, 240)), L((620, 500), (450, 240)),
                              L((450, 240), (450, 0)),
                              L((450, 140), (290, 0)), L((450, 140), (610, 0))])
    # ejective fusions: the palochka rises to the upper half, keeping the
    # ligature distinct from п (unencoded; reached only through GSUB)
    G["tpal"] = dict(adv=600, s=[L((50, 500), (425, 500)), L((238, 0), (238, 500)),
                                 L((510, 270), (510, 500))])
    G["kpal"] = dict(adv=580, s=[L((40, 0), (40, 500)), L((40, 250), (400, 500)),
                                 L((40, 250), (420, 0)), L((530, 270), (530, 500))])
    G["tspal"] = dict(adv=600, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                                  L((55, 0), (445, 0)), L((445, 0), (445, -110)),
                                  L((555, 270), (555, 500))])
    G["chpal"] = dict(adv=620, s=[L((40, 500), (40, 390)), A(250, 390, 210, 180, 360),
                                  L((460, 0), (460, 500)), L((570, 270), (570, 500))])
    G["ppal"] = dict(adv=610, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                                 L((55, 500), (445, 500)), L((555, 270), (555, 500))])
    # modifier letters (caseless): the aspiration marks are a raised small һ
    G["\u02B0"] = dict(adv=340, s=[L((85, 420), (85, 840)), A(190, 610, 105, 180, 0),
                                   L((295, 420), (295, 610))])
    G["\u02B1"] = dict(adv=340, s=[L((85, 420), (85, 840)), L((85, 840), (25, 900)),
                                   A(190, 610, 105, 180, 0), L((295, 420), (295, 610))])
    # combining marks and overlays (zero advance). The ink sits at positive x
    # (+660 from the v2.5 trailing-negative convention): a zero-advance glyph
    # whose bbox is entirely negative is legal but unconventional, and some
    # glyph caches handle it poorly; GPOS anchors are computed from the built
    # bbox, so attachment is identical either way.
    def _mk(st):
        if st[0] == "D":
            return ("D", st[1] + 660, st[2], dr)
        if st[0] == "L":
            return ("L", st[1] + 660, st[2], st[3] + 660, st[4])
        return (st[0], st[1] + 660, *st[2:])  # A: cx shifts, radius/angles keep
    for ch, strokes in list(TOPMARKS.items()) + list(BOTMARKS.items()) + list(OVERLAYS.items()):
        G[ch] = dict(adv=0, s=[_mk(st) for st in strokes])
    # ------------------------------------------------------------ punctuation
    G["!"] = dict(adv=240, s=[L((120, 190), (120, 700)), DOT(120, 35, dr)])
    G["?"] = dict(adv=500, s=[A(250, 545, 145, 180, -90), L((250, 400), (250, 190)),
                              DOT(250, 35, dr)])
    G["'"] = dict(adv=240, s=[L((125, 700), (108, 560))])
    G["\u2019"] = dict(adv=240, s=[L((125, 700), (108, 560))])
    G["\u00AB"] = dict(adv=460, s=[L((210, 375), (90, 250)), L((90, 250), (210, 125)),
                                   L((370, 375), (250, 250)), L((250, 250), (370, 125))])
    G["\u00BB"] = dict(adv=460, s=[L((90, 375), (210, 250)), L((210, 250), (90, 125)),
                                   L((250, 375), (370, 250)), L((370, 250), (250, 125))])
    G["\u00B7"] = dict(adv=240, s=[DOT(120, 250, dr)])
    # brackets and quotes that frame a citation \u2014 a register face must set its
    # own parentheses and quotation marks, not fall back to the host (review)
    G["("] = dict(adv=300, s=[E(410, 250, 340, 410, 129, 231)])
    G[")"] = dict(adv=300, s=[E(-110, 250, 340, 410, -51, 51)])
    G["["] = dict(adv=300, s=[L((95, -110), (95, 700)), L((95, 700), (240, 700)),
                              L((95, -110), (240, -110))])
    G["]"] = dict(adv=300, s=[L((205, -110), (205, 700)), L((60, 700), (205, 700)),
                              L((60, -110), (205, -110))])
    G[";"] = dict(adv=240, s=[DOT(120, 400, dr), L((130, 60), (90, -90))])
    G["\u0022"] = dict(adv=380, s=[L((120, 700), (120, 540)), L((260, 700), (260, 540))])
    G["\u201C"] = dict(adv=420, s=[L((110, 700), (140, 545)), L((250, 700), (280, 545))])
    G["\u201D"] = dict(adv=420, s=[L((140, 700), (110, 545)), L((280, 700), (250, 545))])
    G["\u2018"] = dict(adv=240, s=[L((108, 700), (125, 560))])
    G["\u2010"] = dict(adv=340, s=[L((50, 250), (290, 250))])
    G["\u2013"] = dict(adv=400, s=[L((40, 250), (360, 250))])
    G["\u2014"] = dict(adv=700, s=[L((40, 250), (660, 250))])
    G["\u2192"] = dict(adv=640, s=[L((60, 250), (540, 250)), L((540, 250), (410, 355)),
                                   L((540, 250), (410, 145))])
    G["\u25CC"] = dict(adv=500, s=[DOT(250 + 170 * math.cos(math.pi * i / 6),
                                       250 + 170 * math.sin(math.pi * i / 6), 16)
                                   for i in range(12)])
    G["\u00A0"] = dict(adv=340, s=[])
    G["0"] = dict(adv=500, s=[E(250, 350, 210 - w / 2 + ov, 315 - w / 2 + ov + 36, 0, 360)])
    G["1"] = dict(adv=400, s=[L((230, 0), (230, 700)), L((230, 700), (100, 540))])
    G["2"] = dict(adv=500, s=[A(250, 505, 170, 165, -35), L((389, 407), (75, 0)),
                              L((75, 0), (430, 0))])
    G["3"] = dict(adv=500, s=[A(250, 520, 165, 150, -80), A(250, 180, 180, 85, -165)])
    G["4"] = dict(adv=520, s=[L((350, 0), (350, 700)), L((350, 700), (70, 235)),
                              L((70, 235), (470, 235))])
    G["5"] = dict(adv=500, s=[L((120, 700), (410, 700)), L((120, 700), (120, 435)),
                              L((120, 435), (245, 435)), A(245, 218, 218, 90, -90),
                              L((245, 0), (105, 0))])
    r69x, r69y = 195 - w / 2 + ov, 195 - w / 2 + ov + 8
    G["6"] = dict(adv=500, s=[E(250, 205, r69x, r69y, 0, 360),
                              L((390, 700), (250 - r69x * 0.469, 205 + r69y * 0.883))])
    G["7"] = dict(adv=480, s=[L((60, 700), (430, 700)), L((430, 700), (160, 0))])
    G["8"] = dict(adv=500, s=[E(250, 510, 152 - w / 2 + ov, 152 - w / 2 + ov + 36, 0, 360),
                              E(250, 178, 180 - w / 2 + ov, 180 - w / 2 + ov - 4, 0, 360)])
    G["9"] = dict(adv=500, s=[E(250, 495, r69x, r69y, 0, 360),
                              L((250 + r69x * 0.766, 495 - r69y * 0.643), (212, 0))])
    G["."] = dict(adv=240, s=[DOT(120, 35, 28)])
    G[","] = dict(adv=240, s=[L((130, 60), (90, -90))])
    G["-"] = dict(adv=340, s=[L((50, 250), (290, 250))])
    G[":"] = dict(adv=240, s=[DOT(120, 35, 28), DOT(120, 400, 28)])
    G[" "] = dict(adv=340, s=[])

    # ---------------------------------------------------------- uppercase
    CAP_OF = {}

    def scale_glyph(g, sx, sy):
        out = []
        for st in g["s"]:
            if st[0] in ("L", "LD"):
                k, x1, y1, x2, y2 = st
                out.append((k, x1 * sx, y1 * sy if y1 >= 0 else y1,
                            x2 * sx, y2 * sy if y2 >= 0 else y2))
            elif st[0] == "D":
                _, x, y, r = st
                out.append(("D", x * sx, y * sy if y >= 0 else y, r))
            else:  # A or E -> anisotropic ellipse, exactly like scaled endpoints
                if st[0] == "A":
                    _, cx, cy, r, a0, a1 = st
                    rx = ry = r
                else:
                    _, cx, cy, rx, ry, a0, a1 = st
                out.append(("E", cx * sx, cy * sy if cy >= 0 else cy,
                            rx * sx, ry * sy, a0, a1))
        return dict(adv=round(g["adv"] * sx), s=out)

    C = {}
    scaled = {"В": "в", "Г": "г", "Ж": "ж", "З": "з", "И": "и", "Й": "й", "К": "к",
              "Л": "л", "М": "м", "Н": "н", "П": "п", "Т": "т", "Х": "х", "Ц": "ц",
              "Ч": "ч", "Ш": "ш", "Щ": "щ", "Ъ": "ъ", "Ь": "ь", "Ы": "ы", "Џ": "џ",
              "Ң": "ң", "Ғ": "ғ", "Қ": "қ", "Ҳ": "ҳ", "Ҙ": "ҙ", "Ѕ": "ѕ", "Ѫ": "ѫ",
              "Ѧ": "ѧ", "Ӏ": "ӏ",
              "Ѓ": "ѓ", "Ќ": "ќ", "Ѩ": "ѩ", "Ѭ": "ѭ", "Љ": "љ", "Њ": "њ",
              "Ґ": "ґ",
              "tpal.cap": "tpal", "kpal.cap": "kpal", "tspal.cap": "tspal",
              "chpal.cap": "chpal", "ppal.cap": "ppal"}
    for cap, low in scaled.items():
        C[cap] = scale_glyph(G[low], 1.10, 1.4)
        CAP_OF[cap] = low
    C["А"] = dict(adv=520, s=[L((260, 700), (70, 0)), L((260, 700), (450, 0)),
                              L((130, 210), (390, 210))]); CAP_OF["А"] = "л"
    C["Б"] = dict(adv=520, s=[L((40, 0), (40, 700)), L((40, 700), (440, 700)),
                              L((40, 360), (240, 360)), E(240, 180, 205, 180, 90, -90),
                              L((240, 0), (40, 0))]); CAP_OF["Б"] = "б"
    C["Д"] = dict(adv=540, s=[L((270, 700), (70, 0)), L((270, 700), (470, 0)),
                              L((25, 0), (515, 0)), L((25, 0), (25, -85)),
                              L((515, 0), (515, -85))]); CAP_OF["Д"] = "д"
    C["Е"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap * 0.45, 360 - ap * 0.45),
                              L((40, 375), (320 + R7 * ct_e, 375))]); CAP_OF["Е"] = "е"
    C["Ё"] = dict(adv=640, s=C["Е"]["s"] + [DOT(230, 850, dr), DOT(410, 850, dr)])
    CAP_OF["Ё"] = "е"
    C["О"] = dict(adv=640, s=[E(320, 350, R7, R7v, 0, 360)]); CAP_OF["О"] = "о"
    C["С"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap, 360 - ap)]); CAP_OF["С"] = "с"
    C["Ҫ"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap, 360 - ap),
                              L((320, 350 - R7v), (320, 350 - R7v - 135))])
    CAP_OF["Ҫ"] = "с"
    C["Ф"] = dict(adv=660, s=[E(330, 350, R7 - 40, R7v - 40, 0, 360),
                              L((330, -40), (330, 740))]); CAP_OF["Ф"] = "ф"
    C["Р"] = dict(adv=500, s=[L((50, 0), (50, 700)), L((50, 700), (240, 700)),
                              A(240, 540, 160, 90, -90), L((240, 380), (50, 380))])
    CAP_OF["Р"] = "р"
    C["У"] = dict(adv=540, s=[L((50, 700), (287, 295)), L((490, 700), (160, 0))])
    CAP_OF["У"] = "у"
    C["Ў"] = dict(adv=540, s=C["У"]["s"] + [breve(280, 880)]); CAP_OF["Ў"] = "у"
    C["Ю"] = dict(adv=805, s=[L((40, 0), (40, 700)), L((40, 350), (180, 350)),
                              E(480, 350, 310 - w / 2 + ov, R7v, 0, 360)])
    CAP_OF["Ю"] = "ю"
    C["Я"] = dict(adv=520, s=[L((470, 0), (470, 700)), L((470, 700), (200, 700)),
                              E(200, 540, 170, 160, 90, 270), L((200, 380), (470, 380)),
                              L((320, 380), (90, 0))]); CAP_OF["Я"] = "я"
    C["Һ"] = dict(adv=540, s=[L((40, 0), (40, 700)), A(270, 400, 230, 0, 180),
                              L((500, 0), (500, 400))]); CAP_OF["Һ"] = "һ"
    C["Ә"] = dict(adv=640, s=[E(320, 350, R7, R7v, 55 + ap * 0.6, 415 - ap * 0.6),
                              L((320 - R7 * ct, 350), (320 + R7 * 0.85, 350))])
    CAP_OF["Ә"] = "ә"
    C["Ӧ"] = dict(adv=640, s=[E(320, 350, R7, R7v, 0, 360),
                              DOT(230, 850, dr), DOT(410, 850, dr)]); CAP_OF["Ӧ"] = "о"
    C["Ӱ"] = dict(adv=540, s=C["У"]["s"] + [DOT(190, 850, dr), DOT(370, 850, dr)])
    CAP_OF["Ӱ"] = "у"
    C["Ӣ"] = dict(adv=C["И"]["adv"], s=C["И"]["s"] + [L((140, 860), (420, 860))])
    CAP_OF["Ӣ"] = "и"
    C["Ӯ"] = dict(adv=C["У"]["adv"], s=C["У"]["s"] + [L((150, 860), (430, 860))])
    CAP_OF["Ӯ"] = "у"


    C["Э"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap * 0.75 + 180, 360 - ap * 0.75 + 180),
                              L((320 - R7 * 0.30, 375), (320 + R7 * 0.92, 375))])
    CAP_OF["Э"] = "э"
    C["Є"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap * 0.75, 360 - ap * 0.75),
                              L((320 - R7 * 0.92, 375), (320 + R7 * ct, 375))])
    CAP_OF["Є"] = "є"
    C["Ѳ"] = dict(adv=640, s=[E(320, 350, R7, R7v, 0, 360),
                              L((320 - R7 * 0.92, 350), (320 + R7 * 0.92, 350))])
    CAP_OF["Ѳ"] = "ѳ"
    C["Ѐ"] = dict(adv=C["Е"]["adv"], s=C["Е"]["s"] + [L((285, 900), (355, 810))])
    CAP_OF["Ѐ"] = "е"
    C["Ѝ"] = dict(adv=C["И"]["adv"], s=C["И"]["s"] + [L((245, 900), (315, 810))])
    CAP_OF["Ѝ"] = "и"
    C["Ӓ"] = dict(adv=C["А"]["adv"], s=C["А"]["s"] + [DOT(170, 850, dr), DOT(350, 850, dr)])
    CAP_OF["Ӓ"] = "а"
    C["І"] = dict(adv=360, s=[L((180, 0), (180, 700))]); CAP_OF["І"] = "і"
    C["Ї"] = dict(adv=360, s=[L((180, 0), (180, 700)), DOT(95, 850, 28),
                              DOT(265, 850, dr)]); CAP_OF["Ї"] = "ї"
    C["Ј"] = dict(adv=480, s=[L((330, -40), (330, 700)), A(220, -82, 113, 0, -150)])
    CAP_OF["Ј"] = "ј"
    C["Ћ"] = dict(adv=560, s=[L((30, 700), (490, 700)), L((150, 0), (150, 700)),
                              A(330, 300, 180, 0, 180), L((510, 0), (510, 300))])
    CAP_OF["Ћ"] = "ћ"
    C["Ђ"] = dict(adv=560, s=[L((30, 700), (490, 700)), L((150, 0), (150, 700)),
                              A(330, 300, 180, 0, 180), L((510, -40), (510, 300)),
                              A(405, -40, 105, 0, -150)]); CAP_OF["Ђ"] = "ђ"
    caps_k = p.get("capScale", 1.0)
    if caps_k != 1.0:
        # cap-height correction toward the host serif face (Inline): Cyrillic's
        # x/cap ratio (500/700) is taller than Times' (448/662), so one yScale
        # cannot match both; caps and digits get their own vertical scale, with
        # negative y (descender feet) left untouched by scale_glyph's rule
        for name in list(C):
            C[name] = scale_glyph(C[name], 1.0, caps_k)
            C[name]["adv"] = round(C[name]["adv"] / 1.0)
        for dg in "0123456789":
            G[dg] = scale_glyph(G[dg], 1.0, caps_k)
    G.update(C)
    return G, CAP_OF

# ------------------------------------------------------------ stroke -> ink
def polyline(st):
    if st[0] in ("L", "LD"):
        return [(st[1], st[2]), (st[3], st[4])]
    if st[0] == "A":
        _, cx, cy, r, a0, a1 = st
        rx = ry = r
    else:
        _, cx, cy, rx, ry, a0, a1 = st
    n = max(6, int(math.ceil(abs(a1 - a0) / 5.0)))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]

def ccw(pts):
    a = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]

def disc(cx, cy, r, n=36):
    return ccw([(cx + r * math.cos(2 * math.pi * i / n),
                 cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])

def glyph_contours(gdef, p, slant, fam):
    """Centerline -> quads with per-segment contrast width; terminals per family.
    Shear applies to centerlines (constant perpendicular weight in italic);
    widthScale applies to x after shear+sidebearing; yScale compresses the
    skeleton toward serif proportions (Inline). Free stroke terminals take the
    family cap: 'round' keeps the end disc, 'butt' drops it; serif families
    grow slabs on near-vertical free terminals at the guide lines."""
    wv = p["wv"]
    wh = wv * (1 - p["contrast"])
    tan = math.tan(math.radians(slant))
    ysc = fam.get("yScale", 1.0)
    line_kinds = ("L", "LD")

    term_pts = []
    for st in gdef["s"]:
        if st[0] == "D":
            continue
        raw = polyline(st)
        term_pts.append(raw[0])
        term_pts.append(raw[-1])

    def is_shared(pt):
        return sum(1 for q in term_pts
                   if math.hypot(q[0] - pt[0], q[1] - pt[1]) <= 32) >= 2

    def horiz_cover(x, y):
        for st in gdef["s"]:
            if st[0] in line_kinds and abs(st[2] - st[4]) < 8 and abs(st[2] - y) <= 40 \
               and min(st[1], st[3]) - 20 <= x <= max(st[1], st[3]) + 20:
                return True
        return False

    cs = []
    for st in gdef["s"]:
        if st[0] == "D":
            x = (st[1] + st[2] * tan + p["sb"]) * p["widthScale"]
            cs.append(disc(x, st[2] * ysc, st[3]))
            continue
        raw = polyline(st)
        pts = [((x + y * tan + p["sb"]) * p["widthScale"], y * ysc) for x, y in raw]
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy)
            if ln < 0.3:
                continue
            t = abs(dy) / ln
            wseg = wh + (wv - wh) * (t ** 1.3)
            if fam.get("diagClamp") and st[0] == "LD":
                wseg = min(wseg, fam["diagClamp"])
            px, py = -dy / ln * wseg / 2, dx / ln * wseg / 2
            cs.append(ccw([(x1 + px, y1 + py), (x2 + px, y2 + py),
                           (x2 - px, y2 - py), (x1 - px, y1 - py)]))
            skip_start = i == 0 and fam["caps"] == "butt" and not is_shared(raw[0])
            skip_end = (i == len(pts) - 2 and fam["caps"] == "butt"
                        and not is_shared(raw[-1]))
            if not skip_start:
                cs.append(disc(x1, y1, wseg / 2))
            if not skip_end:
                cs.append(disc(x2, y2, wseg / 2))
        # serifs: slabs on free near-vertical terminals at the guide lines
        if fam.get("serifs") and st[0] in line_kinds:
            (xa, ya), (xb, yb) = (st[1], st[2]), (st[3], st[4])
            dxr, dyr = xb - xa, yb - ya
            lnr = math.hypot(dxr, dyr) or 1.0
            tr = abs(dyr) / lnr
            if tr >= 0.93:
                w_end = wh + (wv - wh) * (tr ** 1.3)
                for pt in ((xa, ya), (xb, yb)):
                    y = pt[1]
                    at_line = abs(y) <= 8 or abs(y - 500) <= 8 or abs(y - 700) <= 8 \
                        or (y <= -160 and tr > 0.95) or (y >= 630 and tr > 0.95)
                    if not at_line or is_shared(pt) or horiz_cover(pt[0], y):
                        continue
                    ext = (w_end / 2 + fam.get("serifLen", 56)) * p["widthScale"]
                    th = max(fam.get("serifTh", 32), wh * fam.get("serifThF", 0.62))
                    xc = (pt[0] + y * tan + p["sb"]) * p["widthScale"]
                    up = y <= 8
                    ya2, yb2 = (y, y + th) if up else (y - th, y)
                    cs.append(ccw([(xc - ext, ya2 * ysc), (xc + ext, ya2 * ysc),
                                   (xc + ext, yb2 * ysc), (xc - ext, yb2 * ysc)]))
    return cs

# ------------------------------------------------------------------ features
def gname(ch):
    return "uni%04X" % ord(ch) if len(ch) == 1 else ch

def make_fea(G, CAP_OF, kern_scale, boxes, xf, register=True):
    def cls(ch):
        return SIDE.get(ch) or (SIDE.get(CAP_OF[ch]) if ch in CAP_OF else None)
    chars = [ch for ch in G if cls(ch)]
    lefts, rights = {}, {}
    for ch in chars:
        lefts.setdefault(cls(ch)[1], []).append(gname(ch))
        rights.setdefault(cls(ch)[0], []).append(gname(ch))
    lines = ["languagesystem DFLT dflt;", "languagesystem cyrl dflt;"]
    for k, names in sorted(lefts.items()):
        lines.append(f"@FIRST_{k} = [{' '.join(sorted(names))}];")
    for k, names in sorted(rights.items()):
        lines.append(f"@SECOND_{k} = [{' '.join(sorted(names))}];")
    lines.append("feature kern {")
    for k, v in KERN.items():
        sv = round(v * kern_scale)
        if sv and k[0] in lefts and k[1] in rights:
            lines.append(f"  pos @FIRST_{k[0]} @SECOND_{k[1]} {sv};")
    lines.append("} kern;")
    # mark-to-base anchors from the built (post-shear) contours, v2.5 recipe:
    # base top anchor at (centre, top+40); mark anchor at its own bbox edge
    for m in TOPMARKS:
        x0, y0, x1, y1 = boxes[gname(m)]
        lines.append(f"markClass {gname(m)} <anchor {round((x0+x1)/2)} {round(y0-10)}> @TOP;")
    for m in BOTMARKS:
        x0, y0, x1, y1 = boxes[gname(m)]
        lines.append(f"markClass {gname(m)} <anchor {round((x0+x1)/2)} {round(y1)}> @BOT;")
    lines.append("feature mark {")
    for ch in G:
        if len(ch) != 1 or not ch.isalpha() or gname(ch) not in boxes:
            continue
        x0, y0, x1, y1 = boxes[gname(ch)]
        tx, ty = round((x0 + x1) / 2), round(y1 + 40)
        bx = xf(BOT_X[ch], -70) if ch in BOT_X else round((x0 + x1) / 2)
        by = round(max(min(0, y0), -60) - 10)
        lines.append(f"  pos base {gname(ch)} <anchor {tx} {ty}> mark @TOP <anchor {bx} {by}> mark @BOT;")
    lines.append("} mark;")
    # ligature stratum, ordered: yus fusion must win before н/л consume ь.
    # register-only: the orthographic fusions (нь->њ etc.) change letter
    # identity and would corrupt ordinary Cyrillic (деньги->дењги), so only the
    # register cuts (2b, Inline) carry them; the general text/UI cuts (Grotesk,
    # Serif) ship without any fusion, safe for plain Cyrillic (typographer
    # review). In a register cut, disable 'liga' to set non-Chuzhditsa text.
    if register:
        lines.append("feature liga {\n  lookup IOTYUS {")
        for a1, a2, out in YUS_LIGA:
            lines.append(f"    sub {gname(a1)} {gname(a2)} by {gname(out)};")
        lines.append("  } IOTYUS;\n  lookup SOFTFUSE {")
        for a1, a2, out in SOFT_LIGA:
            lines.append(f"    sub {gname(a1)} {gname(a2)} by {gname(out)};")
        for base, out in EJECTIVES:
            for pal in ("\u04C0", "\u04CF"):  # palochka is written caseless
                lines.append(f"    sub {gname(base.upper())} {gname(pal)} by {out}.cap;")
                lines.append(f"    sub {gname(base)} {gname(pal)} by {out};")
        lines.append("  } SOFTFUSE;\n} liga;")
    return "\n".join(lines)

def union_contours(contours):
    """Boolean-union the overlapping per-segment quads and discs into clean
    disjoint outlines ('union before you emit'). Nonzero-winding rasterizers
    draw the overlapping form correctly, but renderers that accumulate
    per-contour antialiasing coverage darken every seam, reading as a fake
    bold; a unioned outline is seam-free everywhere."""
    if not contours:
        return contours
    path = pathops.Path()
    for c in contours:
        path.moveTo(*c[0])
        for pt in c[1:]:
            path.lineTo(*pt)
        path.close()
    path.fillType = pathops.FillType.WINDING
    simple = pathops.simplify(path, clockwise=False)
    out, cur = [], []
    for verb, pts in simple:
        if verb == pathops.PathVerb.MOVE:
            if cur: out.append(cur)
            cur = [(round(pts[0][0]), round(pts[0][1]))]
        elif verb == pathops.PathVerb.LINE:
            cur.append((round(pts[0][0]), round(pts[0][1])))
        elif verb == pathops.PathVerb.CLOSE:
            if cur: out.append(cur); cur = []
        else:  # QUAD/CUBIC should not occur from line input; flatten defensively
            cur.append((round(pts[-1][0]), round(pts[-1][1])))
    if cur: out.append(cur)
    return out

# ------------------------------------------------------------------- builder
def build(style, italic, fmt, fam):
    bold = style.startswith("Bold")
    wv = fam["wvBold"] if bold else fam["wvText"]
    p = dict(wv=wv, contrast=fam["contrast"],
             sb=fam["sbBold"] if bold else fam["sbText"], ov=16,
             aperture=fam["aperture"],
             capScale=fam.get("capScale", 1.0),
             widthScale=fam["wsBold"] if bold else fam["wsText"])
    slant = 10 if italic else 0
    G, CAP_OF = glyph_set(p)
    order = [".notdef"] + [gname(ch) for ch in G]
    fb = FontBuilder(UPM, isTTF=(fmt == "ttf"))
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(ch): gname(ch) for ch in G if len(ch) == 1})
    metrics, shapes, boxes = {}, {}, {}
    all_glyphs = {".notdef": dict(adv=550, s=[])}
    all_glyphs.update({gname(ch): g for ch, g in G.items()})
    for name, gdef in all_glyphs.items():
        contours = [[(round(x), round(y)) for x, y in c]
                    for c in glyph_contours(gdef, p, slant, fam)]
        contours = union_contours(contours)
        if contours:
            xs0 = [x for c in contours for x, y in c]
            ys0 = [y for c in contours for x, y in c]
            boxes[name] = (min(xs0), min(ys0), max(xs0), max(ys0))
        adv = round((gdef["adv"] + 2 * p["sb"]) * p["widthScale"])
        if gdef["adv"] == 0:
            adv = 0  # combining marks / overlays carry no advance
        xs = [x for c in contours for x, y in c]
        metrics[name] = (adv, min(xs) if xs else 0)
        if fmt == "ttf":
            pen = TTGlyphPen(None)
        else:
            pen = T2CharStringPen(adv, None)
        for c in contours:
            pen.moveTo(c[0])
            for pt in c[1:]:
                pen.lineTo(pt)
            pen.closePath()
        shapes[name] = pen.glyph() if fmt == "ttf" else pen.getCharString()
    family, sub = fam["name"], style
    ps = f"{fam['file']}-{style.replace(' ', '')}"
    if fmt == "ttf":
        fb.setupGlyf(shapes)
    else:
        fb.setupCFF(ps, {"FullName": f"{family} {sub}", "FamilyName": family,
                         "ItalicAngle": -slant}, shapes, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=920, descent=-300)
    disp = {"BoldItalic": "Bold Italic"}.get(sub, sub)
    fb.setupNameTable({"familyName": family, "styleName": disp, "psName": ps,
                       "fullName": f"{family} {disp}", "version": "Version 3.0",
                       "copyright": "Chuzhditsa - a designed Cyrillic citation register (v3)",
                       "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
                       "licenseInfoURL": "https://openfontlicense.org"})
    fsSel = (0x01 if italic else 0) | (0x20 if bold else 0) | \
            (0x40 if not (bold or italic) else 0) | 0x80
    fb.setupOS2(sTypoAscender=920, sTypoDescender=-300, sTypoLineGap=0,
                usWinAscent=980, usWinDescent=360, fsSelection=fsSel, fsType=0,
                usWeightClass=700 if bold else 400,
                sxHeight=round(500 * fam.get("yScale", 1)),
                sCapHeight=round(700 * fam.get("capScale", 1) * fam.get("yScale", 1)))
    fb.setupPost(italicAngle=-float(slant))
    fb.font["head"].macStyle = (0x01 if bold else 0) | (0x02 if italic else 0)
    tan = math.tan(math.radians(slant))
    xf = lambda x, y: round((x + y * tan + p["sb"]) * p["widthScale"])
    addOpenTypeFeaturesFromString(fb.font,
                                  make_fea(G, CAP_OF, 0.7 if bold else 1.0, boxes, xf,
                                           register=fam.get("register", False)))
    path = os.path.join(OUT, f"{ps}.{fmt}")
    fb.save(path)
    return path

FAMILIES = [
    dict(name="Chuzhditsa 2b", file="Chuzhditsa2b", caps="round", serifs=False,
         contrast=0.10, aperture=55, wvText=76, wvBold=122,
         sbText=50, sbBold=62, wsText=1.05, wsBold=1.10, register=True),
    dict(name="Chuzhditsa Grotesk", file="ChuzhditsaGrotesk", caps="butt", serifs=False,
         contrast=0.08, aperture=50, wvText=84, wvBold=130,
         sbText=52, sbBold=60, wsText=1.02, wsBold=1.07),
    dict(name="Chuzhditsa Serif", file="ChuzhditsaSerif", caps="butt", serifs=True,
         diagClamp=108, contrast=0.34, aperture=52, wvText=92, wvBold=136,
         sbText=58, sbBold=66, wsText=1.02, wsBold=1.06),
    # Inline weight/fit converged by reader proofing after the boolean union
    # invalidated the seam-era calibration: 84/0.52 with a 58-unit fit —
    # density metrics read darker/tighter than the page does; capScale closes
    # the cap-height gap (Cyrillic 500/700 vs Times 448/662 share no yScale)
    dict(name="Chuzhditsa Inline", file="ChuzhditsaInline", caps="butt", serifs=True,
         serifLen=52, serifTh=16, serifThF=0.4, diagClamp=86,
         contrast=0.54, aperture=52, wvText=80, wvBold=126,
         sbText=58, sbBold=68, wsText=0.93, wsBold=0.98, yScale=0.88,
         capScale=1.0714, register=True),
]
STYLES = [("Regular", False), ("Bold", False),
          ("Italic", True), ("BoldItalic", True)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fam in FAMILIES:
        for style, it in STYLES:
            for fmt in ("ttf", "otf"):
                print("built", build(style, it, fmt, fam))
