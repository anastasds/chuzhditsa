#!/usr/bin/env python3
"""Build Chuzhditsa 2b — the v3 readability revision — as TTF+OTF in 4 styles.

Direct port of the browser-side reference builder (fontbuild.js) that produced
the approved v3 binaries; slots next to build_font.py in tools/. Same fontTools
stack, same output conventions, writes to ../fonts/v3/.

v3 engine features vs build_font.py:
  - tangent-angle contrast: w(theta) = wh + (wv-wh)|sin theta|^1.3, wh = 0.90 wv
  - two-case skeletons on x-height 500 / cap 700 with class-derived fitting
    (flat 42 / round 34 / diagonal 28 per side, text master)
  - elliptical bowls: +48u vertical radius, overshooting the rounded-terminal
    envelope, not the guides
  - aperture parameter (55 deg) with bar termini flush at arc tips: r cos(.75a)
  - Bold buys back its ink: sidebearing 50, frame x1.10, kerns x0.7
  - 6-class kern matrix (round/flat/diag/top-bar/apex/aperture), 30 rules,
    compiled through feaLib as GPOS
  - round caps/joins: strokes expand to per-segment quads + end discs,
    uniformly CCW, nonzero fill (overlaps render correctly, as in build_font.py)

NOT yet ported (still Regular-only in the original builder, or absent in v3):
  combining-mark anchors, the liga stratum (yus fusions, ejective digraphs),
  and the pan-Slavic superset glyphs beyond the 121 approved v3 glyphs
  (see build_font.py's G dict for their skeletons; they need v3 width
  harmonization before joining this file).

Run:  python3 tools/build_font_v3.py
"""
import math, os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

UPM = 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "fonts", "v3")

# ------------------------------------------------------------- side classes
# two chars per glyph: [left side, right side]
# R round | F flat | D diagonal/open | T top-bar overhang | A apex | O aperture
SIDE = {
    "о": "RR", "с": "RO", "е": "RR", "ҫ": "RO", "з": "OR", "ѕ": "RR", "ҙ": "OR",
    "ә": "OR", "ӧ": "RR", "ф": "RR", "ё": "RR",
    "а": "RF", "ъ": "FR", "в": "FR", "б": "FR", "ь": "FR", "ю": "FR", "р": "FR",
    "н": "FF", "и": "FF", "ц": "FF", "м": "FF", "п": "FF", "ш": "FF", "щ": "FF",
    "џ": "FF", "ң": "FF", "й": "FF", "ӣ": "FF", "ы": "FF", "һ": "FF", "ӏ": "FF",
    "к": "FD", "қ": "FD", "г": "FT", "ғ": "FT", "т": "TT",
    "ч": "DF", "я": "DF",
    "у": "DD", "ж": "DD", "ў": "DD", "х": "DD", "ҳ": "DD", "ӱ": "DD", "ӯ": "DD",
    "д": "AD", "л": "AD", "ѫ": "AD", "ѧ": "AD",
}
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
    Rab = Ra - 12                 # a/р bowl, trimmed (review: reads oversized)

    def L(a, b): return ("L", a[0], a[1], b[0], b[1])
    def A(cx, cy, r, a0, a1): return ("A", cx, cy, r, a0, a1)
    def E(cx, cy, rx, ry, a0, a1): return ("E", cx, cy, rx, ry, a0, a1)
    def DOT(x, y, r): return ("D", x, y, r)
    def breve(cx, cy): return A(cx, cy, 70, 195, 345)
    def dots(y): return [DOT(165, y, 26), DOT(335, y, 26)]
    def macron(y): return L((120, y), (380, y))

    G = {}
    G["о"] = dict(adv=486, s=[E(243, 250, R, Rv, 0, 360)])
    G["с"] = dict(adv=500, s=[E(250, 250, R, Rv, ap, 360 - ap)])
    G["е"] = dict(adv=500, s=[E(250, 250, R, Rv, ap * 0.75, 360 - ap * 0.75),
                              L((70, 270), (250 + R * ct, 270))])
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
    G["ж"] = dict(adv=500, s=[L((250, 0), (250, 500)), L((250, 250), (30, 500)),
                              L((250, 250), (470, 500)), L((250, 250), (30, 0)),
                              L((250, 250), (470, 0))])
    G["д"] = dict(adv=500, s=[L((250, 500), (60, 0)), L((250, 500), (440, 0)),
                              L((20, 0), (480, 0)), L((20, 0), (20, -70)),
                              L((480, 0), (480, -70))])
    G["ц"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 0), (445, 0)), L((445, 0), (445, -110))])
    G["џ"] = dict(adv=490, s=[L((55, 0), (55, 500)), L((445, 0), (445, 500)),
                              L((55, 0), (445, 0)), L((250, 0), (250, -110))])
    G["ѫ"] = dict(adv=500, s=[L((100, 500), (400, 500)), L((250, 500), (250, 290)),
                              L((250, 290), (70, 0)), L((250, 290), (430, 0))])
    G["ѧ"] = dict(adv=500, s=[L((250, 500), (70, 0)), L((250, 500), (430, 0)),
                              L((140, 190), (360, 190))])
    G["қ"] = dict(adv=470, s=G["к"]["s"] + [L((420, 0), (420, -110))])
    G["ҫ"] = dict(adv=500, s=[E(250, 250, R, Rv, ap, 360 - ap),
                              L((250, 250 - Rv), (250, 250 - Rv - 105))])
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
    G["ҙ"] = dict(adv=455, s=G["з"]["s"] + [L((245, 0), (245, -105))])
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
    G["х"] = dict(adv=480, s=[L((50, 500), (430, 0)), L((430, 500), (50, 0))])
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
    G["ә"] = dict(adv=500, s=[E(250, 250, R, Rv, ap * 0.75 + 180, 360 - ap * 0.75 + 180),
                              L((250 - R * ct, 270), (250 + R * 0.92, 270))])
    G["ӧ"] = dict(adv=486, s=[E(243, 250, R, Rv, 0, 360)] + dots(640))
    G["ӣ"] = dict(adv=490, s=G["и"]["s"] + [macron(650)])
    G["ӏ"] = dict(adv=220, s=[L((110, 0), (110, 700))])
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
            if st[0] == "L":
                _, x1, y1, x2, y2 = st
                out.append(("L", x1 * sx, y1 * sy if y1 >= 0 else y1,
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
              "Ѧ": "ѧ", "Ӏ": "ӏ"}
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
    C["Е"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap * 0.75, 360 - ap * 0.75),
                              L((40, 375), (320 + R7 * ct, 375))]); CAP_OF["Е"] = "е"
    C["Ё"] = dict(adv=640, s=C["Е"]["s"] + [DOT(230, 850, 28), DOT(410, 850, 28)])
    CAP_OF["Ё"] = "е"
    C["О"] = dict(adv=640, s=[E(320, 350, R7, R7v, 0, 360)]); CAP_OF["О"] = "о"
    C["С"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap, 360 - ap)]); CAP_OF["С"] = "с"
    C["Ҫ"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap, 360 - ap),
                              L((320, 350 - R7v), (320, 350 - R7v - 105))])
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
    C["Ә"] = dict(adv=640, s=[E(320, 350, R7, R7v, ap * 0.75 + 180, 360 - ap * 0.75 + 180),
                              L((320 - R7 * ct, 375), (320 + R7 * 0.92, 375))])
    CAP_OF["Ә"] = "ә"
    C["Ӧ"] = dict(adv=640, s=[E(320, 350, R7, R7v, 0, 360),
                              DOT(230, 850, 28), DOT(410, 850, 28)]); CAP_OF["Ӧ"] = "о"
    C["Ӱ"] = dict(adv=540, s=C["У"]["s"] + [DOT(190, 850, 28), DOT(370, 850, 28)])
    CAP_OF["Ӱ"] = "у"
    C["Ӣ"] = dict(adv=C["И"]["adv"], s=C["И"]["s"] + [L((140, 860), (420, 860))])
    CAP_OF["Ӣ"] = "и"
    C["Ӯ"] = dict(adv=C["У"]["adv"], s=C["У"]["s"] + [L((150, 860), (430, 860))])
    CAP_OF["Ӯ"] = "у"

    G.update(C)
    return G, CAP_OF

# ------------------------------------------------------------ stroke -> ink
def polyline(st):
    if st[0] == "L":
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

def glyph_contours(gdef, p, slant):
    """Centerline -> quads with per-segment contrast width + end discs.
    Shear applies to centerlines (constant perpendicular weight in italic);
    widthScale applies to x after shear+sidebearing, exactly as the JS."""
    wv = p["wv"]
    wh = wv * (1 - p["contrast"])
    tan = math.tan(math.radians(slant))
    cs = []
    for st in gdef["s"]:
        if st[0] == "D":
            x = (st[1] + st[2] * tan + p["sb"]) * p["widthScale"]
            cs.append(disc(x, st[2], st[3]))
            continue
        raw = polyline(st)
        pts = [((x + y * tan + p["sb"]) * p["widthScale"], y) for x, y in raw]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy)
            if ln < 0.3:
                continue
            t = abs(dy) / ln
            wseg = wh + (wv - wh) * (t ** 1.3)
            px, py = -dy / ln * wseg / 2, dx / ln * wseg / 2
            cs.append(ccw([(x1 + px, y1 + py), (x2 + px, y2 + py),
                           (x2 - px, y2 - py), (x1 - px, y1 - py)]))
            cs.append(disc(x1, y1, wseg / 2))
            cs.append(disc(x2, y2, wseg / 2))
    return cs

# ------------------------------------------------------------------ features
def gname(ch):
    return "uni%04X" % ord(ch)

def make_fea(G, CAP_OF, kern_scale):
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
    return "\n".join(lines)

# ------------------------------------------------------------------- builder
def build(style, wv, italic, fmt):
    p = dict(wv=wv, contrast=0.10, sb=50 if wv > 100 else 38, ov=16,
             aperture=55, widthScale=1.10 if wv > 100 else 1.05)
    slant = 10 if italic else 0
    G, CAP_OF = glyph_set(p)
    order = [".notdef"] + [gname(ch) for ch in G]
    fb = FontBuilder(UPM, isTTF=(fmt == "ttf"))
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(ch): gname(ch) for ch in G})
    metrics, shapes = {}, {}
    all_glyphs = {".notdef": dict(adv=550, s=[])}
    all_glyphs.update({gname(ch): g for ch, g in G.items()})
    for name, gdef in all_glyphs.items():
        contours = [[(round(x), round(y)) for x, y in c]
                    for c in glyph_contours(gdef, p, slant)]
        adv = round((gdef["adv"] + 2 * p["sb"]) * p["widthScale"])
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
    family, sub = "Chuzhditsa 2b", style
    ps = f"Chuzhditsa2b-{style.replace(' ', '')}"
    if fmt == "ttf":
        fb.setupGlyf(shapes)
    else:
        fb.setupCFF(ps, {"FullName": f"{family} {sub}", "FamilyName": family,
                         "ItalicAngle": -slant}, shapes, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=920, descent=-300)
    fb.setupNameTable({"familyName": family, "styleName": sub, "psName": ps,
                       "fullName": f"{family} {sub}", "version": "Version 3.0",
                       "copyright": "Chuzhditsa 2b - the v3 readability revision",
                       "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
                       "licenseInfoURL": "https://openfontlicense.org"})
    bold = wv > 100
    fsSel = (0x01 if italic else 0) | (0x20 if bold else 0) | \
            (0x40 if not (bold or italic) else 0) | 0x80
    fb.setupOS2(sTypoAscender=920, sTypoDescender=-300, sTypoLineGap=0,
                usWinAscent=980, usWinDescent=360, fsSelection=fsSel,
                usWeightClass=700 if bold else 400, sxHeight=500, sCapHeight=700)
    fb.setupPost(italicAngle=-float(slant))
    fb.font["head"].macStyle = (0x01 if bold else 0) | (0x02 if italic else 0)
    addOpenTypeFeaturesFromString(fb.font, make_fea(G, CAP_OF, 0.7 if bold else 1.0))
    path = os.path.join(OUT, f"{ps}.{fmt}")
    fb.save(path)
    return path

STYLES = [("Regular", 76, False), ("Bold", 122, False),
          ("Italic", 76, True), ("BoldItalic", 122, True)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for style, wv, it in STYLES:
        for fmt in ("ttf", "otf"):
            print("built", build(style, wv, it, fmt))
