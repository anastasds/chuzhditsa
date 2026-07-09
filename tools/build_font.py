#!/usr/bin/env python3
"""Build the Chuzhditsa typeface: a Glagolitic-inspired monoline Cyrillic
with extensions for foreign phonemes. Two-case, GPOS mark anchoring, kerning.
Emits TTF+OTF in 4 styles."""
import math, os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

UPM = 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "fonts")

# ---------------------------------------------------------------- glyph data
# strokes: L x1 y1 x2 y2 | A cx cy r a0 a1 (deg, sweep a0->a1 either dir)
#          R cx cy r (stroked ring) | D cx cy r (filled dot; r=0 -> style dot)
L, A, R, D = "L", "A", "R", "D"
DOTS = [(D, 225, 860, 0), (D, 435, 860, 0)]

G = {
".notdef": dict(adv=660, strokes=[(L,80,0,80,700),(L,80,700,580,700),(L,580,700,580,0),(L,580,0,80,0)]),
"space": dict(adv=400, strokes=[]),
"period": dict(adv=260, strokes=[(D,130,50,0)]),
"comma": dict(adv=260, strokes=[(D,135,60,0),(L,135,10,75,-130)]),
"colon": dict(adv=260, strokes=[(D,130,50,0),(D,130,470,0)]),
"exclam": dict(adv=380, strokes=[(L,190,700,190,240),(D,190,55,0)]),
"question": dict(adv=560, strokes=[(A,290,538,168,150,-60),(L,374,392.5,290,250),(D,290,55,0)]),
"guillemetleft": dict(adv=620, strokes=[(L,270,470,130,330),(L,130,330,270,190),(L,490,470,350,330),(L,350,330,490,190)]),
"guillemetright": dict(adv=620, strokes=[(L,130,470,270,330),(L,270,330,130,190),(L,350,470,490,330),(L,490,330,350,190)]),
"emdash": dict(adv=720, strokes=[(L,40,300,680,300)]),
"zero": dict(adv=680, strokes=[(R,340,350,355,0.78)]),
"one": dict(adv=460, strokes=[(L,280,0,280,700),(L,280,700,150,560)]),
"two": dict(adv=640, strokes=[(A,330,522,185,160,-39.45),(L,472.8,404.4,140,0),(L,140,0,540,0)]),
# the lower bowl runs THROUGH the circles' intersection (388.7,355.2) and a
# little past; the upper bowl ends exactly there, its cap buried inside the
# lower band (and the lower's tip inside the upper band). One continuous
# silhouette, a naturally pointed beak: no wedge, no miter needle
"three": dict(adv=640, strokes=[(A,282,530,175,128,-70.15),(A,282,185,190,88,-110)]),
"four": dict(adv=660, strokes=[(L,440,0,440,700),(L,440,700,140,190),(L,140,190,580,190)]),
# the vertical runs down to the exact point where the bowl circle crosses x=185
"five": dict(adv=640, strokes=[(L,457,700,142,700),(L,142,700,142,385.2),(A,287,217,222,145,-115)]),
# spur circle internally tangent to the bowl at its 170-degree point: the
# spur continues the bowl's left side upward in one unbroken curve
"six": dict(adv=660, strokes=[(R,330,190,195),(A,748.1,123.5,600,168,108)]),
"seven": dict(adv=650, strokes=[(L,120,700,540,700),(L,540,700,260,0)]),
"eight": dict(adv=660, strokes=[(R,330,540,165),(R,330,183,188)]),
"nine": dict(adv=660, strokes=[(R,330,510,195),(A,-283.7,663,800,-12,-51)]),
"egrave": dict(adv=600, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368),(L,390,790,270,930)]),
"igrave": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(L,390,790,270,930)]),
"middot": dict(adv=300, strokes=[(D,150,300,0)]),
"dotcircle": dict(adv=660, strokes=[(D,330+180,350,28),(D,330-180,350,28),(D,330,350+180,28),(D,330,350-180,28),(D,330+127,350+127,28),(D,330-127,350+127,28),(D,330+127,350-127,28),(D,330-127,350-127,28)]),
"arrow": dict(adv=660, strokes=[(L,70,300,560,300),(L,440,400,560,300),(L,440,200,560,300)]),
"hyphen": dict(adv=420, strokes=[(L,70,300,350,300)]),
"endash": dict(adv=520, strokes=[(L,50,300,470,300)]),
"quoteright": dict(adv=210, strokes=[(L,130,780,80,600)]),
"a": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0),(L,190,230,470,230)]),
"b": dict(adv=580, strokes=[(L,160,0,160,700),(L,160,700,480,700),(A,300,183,188,138,-138)]),
"v": dict(adv=565, strokes=[(L,160,0,160,700),(A,277,545,163,136,-136),(A,292,173,178,138,-138)]),
"g": dict(adv=600, strokes=[(L,160,0,160,700),(L,160,700,540,700)]),
"d": dict(adv=660, strokes=[(L,330,715,150,140),(L,330,715,510,140),(L,70,140,590,140),(L,110,140,110,-150),(L,550,140,550,-150)]),
"e": dict(adv=600, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368)]),
# Ж: diagonals capped so the five-stroke crossing keeps its counters in Bold
"zh": dict(adv=660, strokes=[(L,330,0,330,700),(L,70,700,330,390,126),(L,590,700,330,390,126),(L,70,0,330,310,126),(L,590,0,330,310,126)]),
"z": dict(adv=640, strokes=[(A,282,530,175,128,-70.15),(A,282,185,190,88,-110)]),
"i": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700)]),
"ibr": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(A,330,955,130,205,335)]),
# both arms end at one shared point buried in the stem band -> they chain
# into a single mitered > and the junction is covered by the stem
"k": dict(adv=640, strokes=[(L,160,0,160,700),(L,500,700,168,360),(L,500,0,168,360)]),
"l": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0)]),
"m": dict(adv=660, strokes=[(L,90,0,90,700),(L,90,700,330,270),(L,330,270,570,700),(L,570,0,570,700)]),
"n": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,368,500,368)]),
"o": dict(adv=830, strokes=[(R,415,350,358)]),
"p": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,700,500,700)]),
"r": dict(adv=570, strokes=[(L,160,0,160,700),(A,289,528,180,136,-136)]),
"s": dict(adv=720, strokes=[(A,400,350,355,50,310)]),
"t": dict(adv=655, strokes=[(L,70,700,590,700),(L,330,0,330,700)]),
# the arm ends exactly on the long stem's centerline (their intersection),
# so its butt cap is fully buried -- stopping short leaves a wedge notch
"u": dict(adv=640, strokes=[(L,100,700,372.4,253.7),(L,560,700,190,-180)]),
"f": dict(adv=660, strokes=[(L,330,-120,330,800),(R,330,350,240)]),
"h": dict(adv=660, strokes=[(L,90,0,570,700),(L,90,700,570,0)]),
"ts": dict(adv=680, strokes=[(L,150,700,150,60),(L,150,60,540,60),(L,540,700,540,60),(L,540,60,540,-150),(L,540,-150,630,-150)]),
"ch": dict(adv=640, strokes=[(L,150,700,150,430),(L,150,430,480,430),(L,480,0,480,700)]),
"sh": dict(adv=680, strokes=[(L,120,700,120,60),(L,340,700,340,60),(L,560,700,560,60),(L,120,60,560,60)]),
"sht": dict(adv=700, strokes=[(L,120,700,120,60),(L,340,700,340,60),(L,560,700,560,60),(L,120,60,560,60),(L,560,60,560,-150),(L,560,-150,650,-150)]),
"er": dict(adv=620, strokes=[(L,60,700,240,700),(L,240,700,240,0),(A,369,163,168,140,-140)]),
"ermal": dict(adv=570, strokes=[(L,190,0,190,700),(A,319,163,168,140,-140)]),
"yeru": dict(adv=760, strokes=[(L,130,0,130,700),(A,259,163,168,140,-140),(L,620,0,620,700)]),
"yu": dict(adv=720, strokes=[(L,130,0,130,700),(L,130,350,270,350),(R,455,350,185)]),
"ya": dict(adv=660, strokes=[(L,500,0,500,700),(A,374,533,175,44,316),(L,430,360,160,0)]),
# -- extensions --------------------------------------------------------------
"ubr": dict(adv=640, strokes=[(L,100,700,372.4,253.7),(L,560,700,190,-180),(A,330,955,130,205,335)]),
# S spine: two tangent circles (r1+r2 spans cap height exactly), junction at
# (335,370) shared by both arcs -> they chain into one smooth stroke
"dz": dict(adv=640, strokes=[(A,335,540,165,40,270),(A,335,185,190,90,-140)]),
# yuses: legs spread for daylight, internals weight-capped (the counter
# between leg, bar and inner stem drowns at full Bold weight)
"bigyus": dict(adv=660, strokes=[(L,330,715,120,0,116),(L,330,715,540,0,116),(L,195,255,465,255,96),(L,330,255,330,0,96)]),
"smallyus": dict(adv=660, strokes=[(L,330,715,120,190,116),(L,330,715,540,190,116),(L,120,190,540,190,116),(L,200,190,200,0),(L,460,190,460,0)]),
"dzh": dict(adv=660, strokes=[(L,150,700,150,60),(L,510,700,510,60),(L,150,60,510,60),(L,330,60,330,-160)]),
"shha": dict(adv=640, strokes=[(L,150,0,150,700),(A,315,300,165,180,0),(L,480,0,480,300)]),
"adia": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0),(L,190,230,470,230)]+DOTS),
"odia": dict(adv=830, strokes=[(R,415,350,358),(D,310,880,0),(D,520,880,0)]),
"udia": dict(adv=640, strokes=[(L,100,700,372.4,253.7),(L,560,700,190,-180)]+DOTS),
"nghk": dict(adv=680, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,368,500,368),(L,500,0,500,-150),(L,500,-150,590,-150)]),
"khk": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,700,168,360),(L,500,0,168,360),(L,500,0,500,-150),(L,500,-150,590,-150)]),
"gbar": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,50,420,310,420)]),
"hhk": dict(adv=700, strokes=[(L,90,0,570,700),(L,90,700,570,0),(L,570,0,570,-150),(L,570,-150,660,-150)]),
"zhk": dict(adv=640, strokes=[(A,282,530,175,128,-70.15),(A,282,185,190,88,-110),(L,282,5,282,-150),(L,282,-150,372,-150)]),
"shk": dict(adv=720, strokes=[(A,400,350,355,50,310),(L,400,-5,400,-150),(L,400,-150,490,-150)]),
"palochka": dict(adv=460, strokes=[(L,230,0,230,700),(L,140,700,320,700),(L,140,0,320,0)]),
"imac": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(L,170,890,490,890)]),
"umac": dict(adv=640, strokes=[(L,100,700,372.4,253.7),(L,560,700,190,-180),(L,170,890,490,890)]),
# -- pan-Slavic superset ------------------------------------------------------
# е went angular so that Ukrainian round є keeps the historic wide-e form
"ye": dict(adv=760, strokes=[(A,395,350,355,55,305),(L,70,350,640,350)]),
"yo": dict(adv=600, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368)]+DOTS),
"ee": dict(adv=790, strokes=[(A,360,350,355,-130,130),(L,205,350,675,350)]),
"iukr": dict(adv=380, strokes=[(L,190,0,190,700)]),
"yi": dict(adv=380, strokes=[(L,190,0,190,700),(D,105,860,0),(D,275,860,0)]),
"geup": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,540,700,540,830)]),
"dje": dict(adv=620, strokes=[(L,60,700,460,700),(L,260,340,260,700),(A,370,340,110,180,0),(L,480,-80,480,340),(L,480,-80,390,-150)]),
"tshe": dict(adv=580, strokes=[(L,180,0,180,700),(L,40,580,340,580),(A,300,330,120,180,0),(L,420,0,420,330)]),
"gje": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,390,790,490,900)]),
"kje": dict(adv=640, strokes=[(L,160,0,160,700),(L,500,700,168,360),(L,500,0,168,360),(L,300,790,400,900)]),
"je": dict(adv=580, strokes=[(L,400,120,400,700),(A,285,115,120,0,-150)]),
# -- combining marks (zero advance, drawn back over previous glyph) ----------
"fita": dict(adv=830, strokes=[(R,415,350,358),(L,200,350,630,350)]),
"gravecmb": dict(adv=0, strokes=[(L,-270,820,-400,970)]),
"brevecmb": dict(adv=0, strokes=[(A,-330,930,130,205,335)]),
"barcmb": dict(adv=0, strokes=[(L,-450,370,-215,370)]),
"acutecmb": dict(adv=0, strokes=[(L,-390,820,-260,970)]),
"macroncmb": dict(adv=0, strokes=[(L,-490,880,-170,880)]),
"caroncmb": dict(adv=0, strokes=[(L,-450,970,-330,850),(L,-330,850,-210,970)]),
"diacmb": dict(adv=0, strokes=[(D,-435,870,0),(D,-225,870,0)]),
"ogonekcmb": dict(adv=0, strokes=[(L,-330,0,-385,-80),(L,-385,-80,-275,-150)]),
"retrocmb": dict(adv=0, strokes=[(L,-300,0,-300,-150),(L,-300,-150,-210,-150)]),
# -- modifier letters ---------------------------------------------------------
"asp": dict(adv=340, strokes=[(L,85,420,85,840),(A,190,610,105,180,0),(L,295,420,295,610)]),
"aspv": dict(adv=340, strokes=[(L,85,420,85,840),(L,85,840,25,900),(A,190,610,105,180,0),(L,295,420,295,610)]),
# -- ligatures ----------------------------------------------------------------
# fused palatals (Serbian precedent: n/l + soft sign share the stem)
"nsoft": dict(adv=880, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,350,500,350),(A,629,163,168,140,-140)]),
# the soft sign's stem IS the lower segment of the leg: diagonal to (520,340),
# vertical to the baseline, ring tangent to the vertical -- the diagonal
# lives entirely above the bowl and can never cross its counter
"lsoft": dict(adv=900, strokes=[(L,70,0,330,700),(L,330,700,520,340),(L,520,340,520,0),(A,649,163,168,140,-140)]),
# iotated yuses (Old Cyrillic revivals, U+0468/046C): stem + connector + yus
"iotsyus": dict(adv=840, strokes=[(L,130,0,130,700),(L,130,350,366,350,116),(L,510,700,300,190,116),(L,510,700,720,190,116),(L,300,190,720,190,116),(L,395,190,395,0,116),(L,625,190,625,0,116)]),
"iotbyus": dict(adv=840, strokes=[(L,130,0,130,700),(L,130,350,405,350,116),(L,510,700,300,0,116),(L,510,700,720,0,116),(L,376.5,255,643.5,255,96),(L,510,255,510,0,96)]),
# ejective fusions: in the ligature the palochka rises to the upper half
# (like the apostrophe of t' k'), keeping the fusion distinct from п
"tpal": dict(adv=790, strokes=[(L,70,700,590,700),(L,330,0,330,700),(L,700,360,700,700)]),
"kpal": dict(adv=740, strokes=[(L,160,0,160,700),(L,500,700,168,360),(L,500,0,168,360),(L,650,360,650,700)]),
"tspal": dict(adv=760, strokes=[(L,150,700,150,60),(L,150,60,540,60),(L,540,700,540,60),(L,540,60,540,-150),(L,540,-150,630,-150),(L,660,360,660,700)]),
"chpal": dict(adv=720, strokes=[(L,150,700,150,430),(L,150,430,480,430),(L,480,0,480,700),(L,630,360,630,700)]),
"ppal": dict(adv=740, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,700,500,700),(L,650,360,650,700)]),
}

CASED = [n for n in G if n not in
         (".notdef","space","period","comma","colon","hyphen","endash","quoteright",
          "gravecmb","acutecmb","macroncmb","caroncmb","diacmb","ogonekcmb","retrocmb",
          "asp","aspv")]

# -------------------------------------------------------- lowercase derivation
SX, SY = 0.72, 500/700  # x-height 500

def lc_pt(x, y):
    if y > 560:
        # marks above the letter keep their ABSOLUTE clearance: scaling
        # them by 5/7 leaves Bold dots 3 units off the lowercase (cap 700
        # -> x-height 500, so high coordinates shift down by the same 200)
        return (round(x*SX), round(y) - 200)
    return (round(x*SX), round(y*SY) if y >= 0 else round(y))

def lc_glyph(gdef):
    strokes = []
    for st in gdef["strokes"]:
        k = st[0]
        if k == L:
            (x1,y1),(x2,y2) = lc_pt(st[1],st[2]), lc_pt(st[3],st[4])
            strokes.append((L,x1,y1,x2,y2) + ((round(st[5]*SX),) if len(st) > 5 else ()))
        elif k == A:
            cx, cy = lc_pt(st[1], st[2])
            strokes.append((A,cx,cy,round(st[3]*SX),st[4],st[5]))
        elif k in (R, D):
            cx, cy = lc_pt(st[1], st[2])
            strokes.append((k,cx,cy,round(st[3]*SX)))
    return dict(adv=round(gdef["adv"]*SX), strokes=strokes)

LC_CUSTOM = {
"a": dict(adv=640, strokes=[(R,287,243,248),(L,535,10,535,490)]),
# lc dz needs its own construction: the anisotropic case scaling (x 0.72,
# y 5/7) cannot preserve circle tangency, and the 2-unit seam it leaves
# kinks the spine. Tangency re-imposed exactly: 386-119 = 267 = 131+136,
# with the junction invariant under the engine's baseline pinning
"dz": dict(adv=461, strokes=[(A,241,386,119,40,270),(A,241,131,136,90,-140)]),
"b": dict(adv=620, strokes=[(R,345,245,250),(L,95,245,95,700),(L,95,700,400,700)]),
"r": dict(adv=670, strokes=[(L,150,-200,150,500),(R,400,245,250)]),
"f": dict(adv=560, strokes=[(L,280,-180,280,680),(R,280,245,250)]),
# lc ejective fusions: explicit forms with raised half-palochka and clear gap
"tpal": dict(adv=600, strokes=[(L,50,500,425,500),(L,238,0,238,500),(L,510,270,510,500)]),
"kpal": dict(adv=560, strokes=[(L,115,0,115,500),(L,360,500,121,258),(L,360,0,121,258),(L,470,270,470,500)]),
"tspal": dict(adv=590, strokes=[(L,108,500,108,43),(L,108,43,389,43),(L,389,500,389,43),(L,389,43,389,-150),(L,389,-150,454,-150),(L,500,270,500,500)]),
"chpal": dict(adv=545, strokes=[(L,108,500,108,310),(L,108,310,346,310),(L,346,0,346,500),(L,455,270,455,500)]),
"ppal": dict(adv=560, strokes=[(L,115,0,115,500),(L,360,0,360,500),(L,115,500,360,500),(L,470,270,470,500)]),
# lowercase і ї ј carry dots / descender curls the caps lack
"iukr": dict(adv=330, strokes=[(L,165,0,165,500),(D,165,650,0)]),
"yi": dict(adv=330, strokes=[(L,165,0,165,500),(D,82,650,0),(D,248,650,0)]),
"je": dict(adv=440, strokes=[(L,300,-30,300,500),(A,200,-72,103,0,-150),(D,300,650,0)]),
}

for name in CASED:
    G["lc." + name] = LC_CUSTOM.get(name) or lc_glyph(G[name])

# codepoints -> glyph names (upper -> cap glyph, lower -> lc glyph)
def pair(lo, hi, name): return [(lo, "lc."+name), (hi, name)]
CMAP_PAIRS = (
 pair(0x0430,0x0410,"a")+pair(0x0431,0x0411,"b")+pair(0x0432,0x0412,"v")+
 pair(0x0433,0x0413,"g")+pair(0x0434,0x0414,"d")+pair(0x0435,0x0415,"e")+
 pair(0x0436,0x0416,"zh")+pair(0x0437,0x0417,"z")+pair(0x0438,0x0418,"i")+
 pair(0x0439,0x0419,"ibr")+pair(0x043A,0x041A,"k")+pair(0x043B,0x041B,"l")+
 pair(0x043C,0x041C,"m")+pair(0x043D,0x041D,"n")+pair(0x043E,0x041E,"o")+
 pair(0x043F,0x041F,"p")+pair(0x0440,0x0420,"r")+pair(0x0441,0x0421,"s")+
 pair(0x0442,0x0422,"t")+pair(0x0443,0x0423,"u")+pair(0x0444,0x0424,"f")+
 pair(0x0445,0x0425,"h")+pair(0x0446,0x0426,"ts")+pair(0x0447,0x0427,"ch")+
 pair(0x0448,0x0428,"sh")+pair(0x0449,0x0429,"sht")+pair(0x044A,0x042A,"er")+
 pair(0x044C,0x042C,"ermal")+pair(0x044B,0x042B,"yeru")+pair(0x044E,0x042E,"yu")+
 pair(0x044F,0x042F,"ya")+
 pair(0x045E,0x040E,"ubr")+pair(0x0455,0x0405,"dz")+pair(0x046B,0x046A,"bigyus")+
 pair(0x0467,0x0466,"smallyus")+pair(0x045F,0x040F,"dzh")+pair(0x04BB,0x04BA,"shha")+
 pair(0x04D3,0x04D2,"adia")+pair(0x04D9,0x04D8,"adia")+pair(0x04E7,0x04E6,"odia")+
 pair(0x04F1,0x04F0,"udia")+pair(0x04A3,0x04A2,"nghk")+pair(0x049B,0x049A,"khk")+
 pair(0x0493,0x0492,"gbar")+pair(0x04B3,0x04B2,"hhk")+pair(0x0499,0x0498,"zhk")+
 pair(0x04AB,0x04AA,"shk")+pair(0x04CF,0x04C0,"palochka")+
 pair(0x04E3,0x04E2,"imac")+pair(0x04EF,0x04EE,"umac")+
 pair(0x0469,0x0468,"iotsyus")+pair(0x046D,0x046C,"iotbyus")+
 pair(0x045A,0x040A,"nsoft")+pair(0x0459,0x0409,"lsoft")+
 pair(0x0454,0x0404,"ye")+pair(0x0451,0x0401,"yo")+pair(0x044D,0x042D,"ee")+
 pair(0x0456,0x0406,"iukr")+pair(0x0457,0x0407,"yi")+pair(0x0491,0x0490,"geup")+
 pair(0x0452,0x0402,"dje")+pair(0x045B,0x040B,"tshe")+pair(0x0453,0x0403,"gje")+
 pair(0x045C,0x040C,"kje")+pair(0x0458,0x0408,"je")+
 pair(0x0450,0x0400,"egrave")+pair(0x045D,0x040D,"igrave")+
 [(0x0020,"space"),(0x00A0,"space"),(0x002E,"period"),(0x002C,"comma"),
  (0x003A,"colon"),(0x00B7,"middot"),(0x002D,"hyphen"),(0x2010,"hyphen"),(0x2013,"endash"),(0x2014,"emdash"),
  (0x0021,"exclam"),(0x003F,"question"),(0x00AB,"guillemetleft"),(0x00BB,"guillemetright"),
  (0x0030,"zero"),(0x0031,"one"),(0x0032,"two"),(0x0033,"three"),(0x0034,"four"),
  (0x0035,"five"),(0x0036,"six"),(0x0037,"seven"),(0x0038,"eight"),(0x0039,"nine"),
  (0x0027,"quoteright"),(0x2019,"quoteright"),(0x25CC,"dotcircle"),(0x2192,"arrow"),
  (0x0300,"gravecmb"),(0x0301,"acutecmb"),(0x0304,"macroncmb"),
  (0x030C,"caroncmb"),(0x0308,"diacmb"),(0x0328,"ogonekcmb"),(0x0322,"retrocmb"),
  (0x0306,"brevecmb"),(0x0335,"barcmb"),(0x0473,"fita"),(0x0472,"fita"),
  (0x02B0,"asp"),(0x02B1,"aspv")]
)
CMAP = dict(CMAP_PAIRS)

TOPMARKS = ["gravecmb","acutecmb","macroncmb","caroncmb","diacmb","brevecmb"]
BOTMARKS = ["ogonekcmb","retrocmb"]
MARKS = TOPMARKS + BOTMARKS
BASES = [n for n in G if n not in MARKS and G[n]["strokes"]]
# bottom-anchor x overrides: hooks land on the letter's working stem
BOT_X = {"t":330,"r":160,"n":500,"lc.t":238,"lc.r":150,"lc.n":360}

# ------------------------------------------------------------ stroke -> outline
def circle_pts(cx, cy, r, n=None):
    n = n or max(48, min(128, int(r)))
    return [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)]

def arc_pts(cx, cy, r, a0, a1):
    n = max(12, int(abs(a1-a0)/2.5) + 1)
    return [(cx + r*math.cos(math.radians(a0+(a1-a0)*i/n)),
             cy + r*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

def sweeps_bottom(a0, a1):
    """Does the arc pass through its circle's bottom extreme (270 deg)?"""
    lo, hi = min(a0, a1), max(a0, a1)
    t = -90.0
    while t < lo:
        t += 360.0
    return t <= hi

def pin_bottom(cy, r, w):
    """Baseline pinning. A stroked circle grows ink DOWN by w/2 as weight
    grows, while stems keep their feet exactly on the baseline; a bowl that
    sits on the baseline therefore dips w/2 below it and reads sunken next
    to every flat letter. Shifting the center up w/4 and shrinking the
    radius by w/4 pins the ink bottom at exactly cy - r in every weight,
    while the ink top keeps growing by w/2 like the flat letters' tops.
    (cy + r is invariant, so junctions at a bowl's top survive exactly.)"""
    return cy + w/4.0, r - w/4.0

def area(pts):
    return sum(x1*y2 - x2*y1 for (x1,y1),(x2,y2) in zip(pts, pts[1:]+pts[:1])) / 2

def ccw(pts):
    return pts if area(pts) > 0 else pts[::-1]

def _hline_isect(p, d, Y):
    if abs(d[1]) < 1e-9:
        return None
    t = (Y - p[1]) / d[1]
    return (p[0] + d[0]*t, Y)

def _clip_join(cand, corner, p1, d1, p2, d2, hw):
    """A join at a cap-line apex may legitimately pierce the line (the eye
    wants it), but a miter tip is unbounded: the apex of А reached 132 units
    past the cap band. Cut any join that escapes the pierce allowance flat,
    at the allowance line — the punchcutter's flat apex. Ditto at the
    baseline: the И corner's bevel dipped 20 units under it.

    Applies to CORNERS only. A sampled arc is a chain of near-collinear
    vertices; treating them as corners would flat-cut every round bottom's
    legitimate overshoot (and the near-horizontal edge there sends the
    clip intersection kilometers sideways)."""
    l1, l2 = math.hypot(*d1) or 1.0, math.hypot(*d2) or 1.0
    if (d1[0]*d2[0] + d1[1]*d2[1]) / (l1*l2) > 0.8:
        return cand
    if 420 < corner[1] <= 502 + hw:
        ylim = 516 + hw          # x-height: ink 500+hw, allowance 16
    elif 560 < corner[1] <= 702 + hw:
        ylim = 718 + hw          # caps: ink cap 700+hw, pierce allowance 18
    else:
        ylim = None
    if ylim and any(p[1] > ylim for p in cand):
        a, b = _hline_isect(p1, d1, ylim), _hline_isect(p2, d2, ylim)
        if a and b:
            return [a, b]
    if -20 < corner[1] <= 120 and any(p[1] < -2 for p in cand):
        a, b = _hline_isect(p1, d1, 0.0), _hline_isect(p2, d2, 0.0)
        if a and b:
            return [a, b]
    return cand

def offset_polyline(pts, hw, miter_limit=3.0):
    """Stroke a polyline as one clean outline: butt caps, mitered corners
    (bevel past the miter limit). This is what makes terminals and apexes
    crisp instead of marker-pen blobs."""
    normals = []
    for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
        d = math.hypot(x2-x1, y2-y1) or 1.0
        normals.append(((y1-y2)/d*hw, (x2-x1)/d*hw))

    def line_isect(p, d1, q, d2):
        det = d1[0]*d2[1] - d1[1]*d2[0]
        if abs(det) < 1e-9:
            return None
        t = ((q[0]-p[0])*d2[1] - (q[1]-p[1])*d2[0]) / det
        return (p[0] + d1[0]*t, p[1] + d1[1]*t)

    def cap_pt(p_end, p_prev, nx, ny):
        """Terminal point: straight diagonal strokes get a horizontal cut
        (type-design convention: feet sit flat on the baseline), curves and
        horizontals keep the perpendicular butt cap."""
        ux, uy = p_end[0]-p_prev[0], p_end[1]-p_prev[1]
        seg = math.hypot(ux, uy) or 1.0
        ux, uy = ux/seg, uy/seg
        if seg > 40 and abs(uy) > 0.35:
            t = -ny/uy
            return (p_end[0]+nx+ux*t, p_end[1])
        return (p_end[0]+nx, p_end[1]+ny)

    def clip_join(cand, corner, p1, d1, p2, d2):
        return _clip_join(cand, corner, p1, d1, p2, d2, hw)

    def side(sign):
        out = [cap_pt(pts[0], pts[1], sign*normals[0][0], sign*normals[0][1])]
        for i in range(1, len(pts)-1):
            na, nb = normals[i-1], normals[i]
            d1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
            d2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
            p1 = (pts[i-1][0]+sign*na[0], pts[i-1][1]+sign*na[1])
            p2 = (pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1])
            hit = line_isect(p1, d1, p2, d2)
            # concave side: the intersection is the correct join and gets a
            # generous limit (a bevel here would fold the outline over
            # itself) -- but NOT an infinite one: at a hairpin (the hook of
            # Ђ reversing off its stem) the offsets run near-parallel and
            # the "intersection" races off to infinity
            concave = (d1[0]*d2[1] - d1[1]*d2[0]) * sign > 0
            limit = 6.0 if concave else miter_limit
            if hit and math.hypot(hit[0]-pts[i][0], hit[1]-pts[i][1]) <= limit*hw:
                cand = [hit]
            else:  # bevel
                cand = [(pts[i][0]+sign*na[0], pts[i][1]+sign*na[1]),
                        (pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1])]
            out.extend(clip_join(cand, pts[i], p1, d1, p2, d2))
        out.append(cap_pt(pts[-1], pts[-2], sign*normals[-1][0], sign*normals[-1][1]))
        return out

    return [ccw(side(1) + side(-1)[::-1])]

def offset_closed(pts, hw, miter_limit=3.0):
    """Stroke a CLOSED centerline loop: mitered outer ring + inner hole.
    Without this, a circuit of chained strokes (the triangle of ѧ) collapses
    into a filled shape with a seam where the two butt caps meet."""
    n = len(pts)
    normals = []
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i+1) % n]
        d = math.hypot(x2-x1, y2-y1) or 1.0
        normals.append(((y1-y2)/d*hw, (x2-x1)/d*hw))

    def line_isect(p, d1, q, d2):
        det = d1[0]*d2[1] - d1[1]*d2[0]
        if abs(det) < 1e-9:
            return None
        t = ((q[0]-p[0])*d2[1] - (q[1]-p[1])*d2[0]) / det
        return (p[0] + d1[0]*t, p[1] + d1[1]*t)

    def ring(sign):
        out = []
        for i in range(n):
            na, nb = normals[i-1], normals[i]
            pa, pb, pc = pts[i-1], pts[i], pts[(i+1) % n]
            d1 = (pb[0]-pa[0], pb[1]-pa[1])
            d2 = (pc[0]-pb[0], pc[1]-pb[1])
            p1 = (pa[0]+sign*na[0], pa[1]+sign*na[1])
            p2 = (pb[0]+sign*nb[0], pb[1]+sign*nb[1])
            hit = line_isect(p1, d1, p2, d2)
            concave = (d1[0]*d2[1] - d1[1]*d2[0]) * sign > 0
            limit = 6.0 if concave else miter_limit
            if hit and math.hypot(hit[0]-pb[0], hit[1]-pb[1]) <= limit*hw:
                cand = [hit]
            else:
                cand = [(pb[0]+sign*na[0], pb[1]+sign*na[1]),
                        (pb[0]+sign*nb[0], pb[1]+sign*nb[1])]
            out.extend(_clip_join(cand, pb, p1, d1, p2, d2, hw))
        return out

    r1, r2 = ring(1), ring(-1)
    if abs(area(r1)) < abs(area(r2)):  # outer ring is the larger one
        r1, r2 = r2, r1
    return [ccw(r1), ccw(r2)[::-1]]

def chain_paths(items, tol=4.0, wtol=0.15):
    """Merge open centerline paths that meet end-to-end at points shared by
    exactly two strokes, so apexes (Л, И, М, ...) become mitered corners.

    items: list of (path, weight). Endpoints closer than `tol` count as the
    same node and are snapped to their midpoint — rounding in the lowercase
    derivation and float endpoints of arcs must not leave hairline notches.
    Paths of different clamped weights merge when the weights are within
    `wtol` (merged path takes the lighter weight, protecting the tight
    counter that caused the clamp); a hook clamped far below its stems
    (Bold ј, ђ) stays a separate stroke — its butt cap buries in the stem.
    Returns list of (path, weight)."""
    def close(p, q):
        return math.hypot(p[0]-q[0], p[1]-q[1]) <= tol
    def self_crosses(path):
        # a chained path must not cross itself: the offset outline of a
        # self-intersecting centerline double-covers the crossing, which
        # even-odd consumers (figure renderers, some path processors)
        # display as a hole (the bar of 4 crossing its own stem). Leave
        # such strokes as separate overlapping paths instead.
        def x(a1, a2, b1, b2):
            def o(p, q, r):
                v = (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
                return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
            return o(a1,a2,b1) != o(a1,a2,b2) and o(b1,b2,a1) != o(b1,b2,a2)
        n = len(path)
        return any(x(path[i], path[i+1], path[j], path[j+1])
                   for i in range(n-1) for j in range(i+2, n-1))
    # node degree over all endpoints (cluster by proximity)
    endpoints = [p for path, _ in items for p in (path[0], path[-1])]
    def degree(p):
        return sum(1 for q in endpoints if close(p, q))
    items = [(list(p), w) for p, w in items]
    merged = True
    while merged:
        merged = False
        for i in range(len(items)):
            if merged: break
            for j in range(i+1, len(items)):
                (a, wa), (b, wb) = items[i], items[j]
                if abs(wa-wb) > wtol*max(wa, wb):
                    continue
                joins = None
                if close(a[-1], b[0]) and degree(a[-1]) == 2:
                    joins = a[:-1] + [mid(a[-1], b[0])] + b[1:]
                elif close(a[-1], b[-1]) and degree(a[-1]) == 2:
                    joins = a[:-1] + [mid(a[-1], b[-1])] + b[-2::-1]
                elif close(a[0], b[-1]) and degree(a[0]) == 2:
                    joins = b[:-1] + [mid(b[-1], a[0])] + a[1:]
                elif close(a[0], b[0]) and degree(a[0]) == 2:
                    joins = b[::-1][:-1] + [mid(b[0], a[0])] + a[1:]
                if joins and not self_crosses(joins):
                    items[i] = (joins, min(wa, wb))
                    del items[j]
                    merged = True
                    break
    return items

def mid(p, q):
    return ((p[0]+q[0])/2, (p[1]+q[1])/2)

def glyph_contours(gdef, w, dotr, slant, dx=0, clamp=True):
    """Centerline model -> outlines. Shear applies to centerlines so the
    italic keeps constant perpendicular weight; dx shifts bold sidebearings."""
    def sh(pt):
        x, y = pt
        return (x + y*slant + dx, y)
    open_paths, cs = [], []
    # endpoints of horizontal strokes: a stem that meets a bar keeps its
    # declared end (the bar's band makes the ink); a free stem top rises
    hbar_ends = {(round(s[1]), round(s[2])) for s in gdef["strokes"]
                 if s[0] == L and s[2] == s[4]} | \
                {(round(s[3]), round(s[4])) for s in gdef["strokes"]
                 if s[0] == L and s[2] == s[4]}
    rings = [(s[1], s[2], s[3]) for s in gdef["strokes"] if s[0] == R]
    def cap_line_extend(x, y, weff):
        """y=700 (caps) / y=500 (x-height) endpoints are INK lines, but a
        butt-capped stroke ends exactly at its endpoint while a bar through
        the same y makes ink to y+w/2: stems next to bars read 45 units
        short. Free stem tops therefore rise by w/2 to the same ink line.
        Not when a bar shares the endpoint (its band makes the ink), and
        not when the endpoint sits inside a ring's band — the bowl of В is
        the silhouette there, and an extended stem pokes past it, notching
        the shoulder."""
        if y not in (700, 500) or (round(x), round(y)) in hbar_ends:
            return y
        for (rx, ry, rr) in rings:
            if abs(math.hypot(x-rx, y-ry) - rr) <= weff/2.0 + 15:
                return y
        return y + weff/2.0
    for st in gdef["strokes"]:
        kind = st[0]
        if kind == L:
            # optional 6th element: absolute weight cap. The straight-stroke
            # analogue of the arc clamp -- the internals of the yuses cannot
            # carry full Bold weight without swallowing their counters
            weff = min(w, st[5]) if clamp and len(st) > 5 else w
            (x1, y1), (x2, y2) = (st[1], st[2]), (st[3], st[4])
            if y1 == y2 and 0 <= y1 <= 60:
                # a bottom bar is an INK floor: pin its underside to the
                # baseline in every weight (it sat 45 low at y=0, and the
                # bar of Ш floated 15 high in Regular yet dipped in Bold)
                y1 = y2 = weff/2.0
            else:
                y1 = cap_line_extend(x1, y1, weff)
                y2 = cap_line_extend(x2, y2, weff)
            open_paths.append(([(x1, y1), (x2, y2)], weff))
        elif kind == A:
            # tight arcs (breve, small hooks) can't carry the full Bold
            # weight. An OPEN arc keeps a half-radius of daylight at weight
            # r, so it clamps at 1.0r; closed counters (rings, loops below)
            # stay at the stricter 0.85
            weff = min(w, max(44, int(st[3]))) if clamp else w
            acx, acy, ar = st[1], st[2], st[3]
            if sweeps_bottom(st[4], st[5]) and acy - ar <= 60:
                acy, ar = pin_bottom(acy, ar, weff)
            pts = arc_pts(acx,acy,ar,st[4],st[5])
            if st[3] >= 290 and abs(st[5]-st[4]) >= 120:
                # big-round compression of о — bowls only; a large-radius
                # construction arc (the spur of 6/9) must keep its geometry
                # or it detaches from the ring it is tangent to
                pts = [(acx+(x-acx)*0.965, y) for x, y in pts]
            open_paths.append((pts, weff))
        elif kind == R:
            rx, ry, r = st[1], st[2], st[3]
            xs = st[4] if len(st) > 4 else 1.0  # optional: oval (the digit 0)
            sqz = xs * (0.965 if r >= 200 else 1.0)  # big rounds compress slightly
            wr = min(w, max(44, int(r*0.85))) if clamp else w  # keep counters open in Bold
            if ry - r <= 60:  # bowls on the baseline get their bottoms pinned
                # the pin shrinks r by w/4, which would slide a declared
                # stem tangency off the stem. The declaration stays PURE
                # (circle exactly tangent to the stem line); the engine
                # steps the center toward the stem by the same w/4, and
                # the ink is flush with the stem in every weight, exactly
                side = 0
                for s in gdef["strokes"]:
                    if s[0] == L and s[1] == s[3]:
                        if abs(s[1] - (rx - r)) <= 2:
                            side = -1
                        elif abs(s[1] - (rx + r)) <= 2:
                            side = 1
                ry, r = pin_bottom(ry, r, wr)
                rx += side * wr/4.0
            cx, cy = sh((rx, ry))
            cs.append(ccw([(cx+(x-cx)*sqz, y) for x, y in circle_pts(cx,cy,r+wr/2)]))
            cs.append(ccw([(cx+(x-cx)*sqz, y) for x, y in circle_pts(cx,cy,max(10,r-wr/2))])[::-1])
        elif kind == D:
            rr = st[3] or dotr
            dy = st[2]
            if dy <= 100:  # baseline dots ride up so Bold doesn't sink them
                dy = max(dy, rr - 5)
            cx, cy = sh((st[1], dy))
            cs.append(ccw(circle_pts(cx,cy,rr)))
        else:
            raise ValueError(kind)
    for path, weff in chain_paths(open_paths):
        closed = (len(path) >= 4 and
                  math.hypot(path[0][0]-path[-1][0], path[0][1]-path[-1][1]) <= 4.0)
        if closed:
            loop = path[:-1]
            a = abs(area(loop))
            per = sum(math.hypot(loop[(i+1) % len(loop)][0]-loop[i][0],
                                 loop[(i+1) % len(loop)][1]-loop[i][1]) for i in range(len(loop)))
            inradius = 2*a/per if per else weff
            wc = min(weff, max(44, int(0.85 * inradius))) if clamp else weff  # keep loop counters open
            cs.extend(offset_closed([sh(p) for p in loop], wc/2))
        else:
            cs.extend(offset_polyline([sh(p) for p in path], weff/2))
    return cs

def bbox(contours):
    xs = [x for c in contours for (x,y) in c]
    ys = [y for c in contours for (x,y) in c]
    return min(xs), min(ys), max(xs), max(ys)

# ------------------------------------------------------------------ features
def make_fea(boxes, slant):
    """GPOS: mark-to-base anchors from computed bboxes, plus a small kern set."""
    def sh(x, y):
        return round(x + y*slant), round(y)
    lines = ["languagesystem DFLT dflt;", "languagesystem cyrl dflt;"]
    for m in TOPMARKS:
        x0,y0,x1,y1 = boxes[m]
        ax, ay = sh((x0+x1)/2, y0 - 10)
        lines.append(f"markClass {m} <anchor {ax} {ay}> @TOP;")
    for m in BOTMARKS:
        x0,y0,x1,y1 = boxes[m]
        ax, ay = sh((x0+x1)/2, y1)
        lines.append(f"markClass {m} <anchor {ax} {ay}> @BOT;")
    lines.append("feature mark {")
    for b in BASES:
        x0,y0,x1,y1 = boxes[b]
        tx, ty = sh((x0+x1)/2, y1 + 40)
        # clamp so bottom hooks don't stack below existing descenders
        bx, by = sh(BOT_X.get(b, (x0+x1)/2), max(min(0, y0), -60) - 10)
        lines.append(f"  pos base {b} <anchor {tx} {ty}> mark @TOP <anchor {bx} {by}> mark @BOT;")
    lines.append("} mark;")
    lines.append("""
# kern: class matrix modeled on measured Golos/PT Sans/Montserrat systems.
# LEFT classes are mutually disjoint and RIGHT classes are mutually disjoint
# (a glyph in two left classes splits the lookup into subtables, and
# first-match-wins silently disables every rule after the first)
@T_CAP = [g t gbar geup gje dje tshe];
@T_LC = [lc.g lc.t lc.gbar lc.geup lc.gje lc.dje lc.tshe];
@U_CAP = [u ubr udia umac ch];
@U_LC = [lc.u lc.ubr lc.udia lc.umac lc.ch];
@DIAG_CAP = [a l adia bigyus smallyus];
@DIAG_LC = [lc.a lc.l lc.adia lc.bigyus lc.smallyus];
@ROUND_CAP = [o odia s ye ee fita shk];
@ROUND_LC = [lc.o lc.odia lc.s lc.ye lc.ee lc.fita lc.shk];
@ZH_CAP = [zh k h khk kje hhk ya];
@ZH_LC = [lc.zh lc.k lc.h lc.khk lc.kje lc.hhk lc.ya];
@FEET_CAP = [d ts sht dzh];
@FEET_LC = [lc.d lc.ts lc.sht lc.dzh];
@ER_CAP = [er ermal];
@ER_LC = [lc.er lc.ermal];
@STR_LC = [lc.i lc.ibr lc.n lc.p lc.m lc.sh lc.yeru lc.iukr lc.yi lc.v lc.z lc.e lc.yo lc.b lc.f lc.imac lc.igrave];
@DASH = [hyphen endash emdash];
# right-side targets (disjoint among themselves)
@TBAR_R = [t er tpal];
@TBARLC_R = [lc.t lc.er lc.tpal];
@DIAGR_CAP = [a l adia bigyus smallyus d];
@DIAGR_LC = [lc.a lc.l lc.adia lc.bigyus lc.smallyus lc.d];
@UR_CAP = [u ubr udia umac ch];
@UR_LC = [lc.u lc.ubr lc.udia lc.umac lc.ch];
@ROUNDR_CAP = [o odia s ye ee fita shk];
@ROUNDR_LC = [lc.o lc.odia lc.s lc.ye lc.ee lc.fita lc.shk];
@STRR_LC = [lc.i lc.ibr lc.n lc.p lc.m lc.sh lc.yeru lc.iukr lc.yi lc.v lc.z lc.e lc.yo lc.zh lc.k lc.h lc.ts lc.sht lc.ermal lc.ya lc.yu];
@PUNCT = [period comma];
feature kern {
  pos @T_CAP @DIAGR_CAP -85;   pos @T_CAP @ROUNDR_CAP -15;
  pos @T_CAP @DIAGR_LC -90;    pos @T_CAP @ROUNDR_LC -90;
  pos @T_CAP @STRR_LC -90;     pos @T_CAP @UR_LC -90;
  pos @T_CAP @TBARLC_R -60;
  pos @T_CAP @PUNCT -130;      pos @T_CAP @DASH -60;
  pos @T_LC @DIAGR_LC -60;     pos @T_LC @ROUNDR_LC -12;
  pos @T_LC @PUNCT -95;        pos @T_LC @DASH -45;
  pos @U_CAP @DIAGR_CAP -80;   pos @U_CAP @ROUNDR_CAP -25;
  pos @U_CAP @DIAGR_LC -60;    pos @U_CAP @ROUNDR_LC -55;
  pos @U_CAP @STRR_LC -55;     pos @U_CAP @UR_LC -55;
  pos @U_CAP @PUNCT -140;      pos @U_CAP @DASH -20;
  pos @U_LC @DIAGR_LC -40;     pos @U_LC @PUNCT -60;
  pos @DIAG_CAP @TBAR_R -80;   pos @DIAG_CAP @UR_CAP -60;
  pos @DIAG_CAP @ROUNDR_CAP -20; pos @DIAG_CAP @UR_LC -45;
  pos @DIAG_CAP @TBARLC_R -55;
  pos @DIAG_LC @TBAR_R -90;    pos @DIAG_LC @TBARLC_R -55;
  pos @DIAG_LC @UR_LC -45;
  pos @ROUND_CAP @TBAR_R -25;  pos @ROUND_CAP @DIAGR_CAP -20;
  pos @ROUND_CAP @UR_CAP -25;  pos @ROUND_CAP @DIAGR_LC -15;
  pos @ROUND_CAP @PUNCT -20;
  pos @ROUND_LC @TBAR_R -95;   pos @ROUND_LC @TBARLC_R -18;
  pos @ROUND_LC @DIAGR_LC -12; pos @ROUND_LC @UR_LC -15;
  pos @ZH_CAP @ROUNDR_CAP -20; pos @ZH_CAP @ROUNDR_LC -25;
  pos @ZH_CAP @TBAR_R -25;     pos @ZH_CAP @UR_LC -30;
  pos @ZH_LC @ROUNDR_LC -15;   pos @ZH_LC @TBARLC_R -12;
  pos @FEET_CAP @TBAR_R -20;   pos @FEET_CAP @UR_CAP -20;
  pos @FEET_CAP @UR_LC -25;
  pos @FEET_LC @PUNCT 40;      pos @FEET_LC @TBARLC_R -12;
  pos @ER_CAP @TBAR_R -80;     pos @ER_CAP @UR_CAP -60;
  pos @ER_CAP @UR_LC -40;
  pos @ER_LC @TBAR_R -90;      pos @ER_LC @TBARLC_R -45;
  pos @ER_LC @UR_LC -40;
  pos @STR_LC @TBAR_R -100;    pos @STR_LC @TBARLC_R -50;
  pos [r] @DIAGR_CAP -80;      pos [r] @DIAGR_LC -55;
  pos [r] @PUNCT -125;
  pos [lc.r] @DIAGR_LC -25;    pos [lc.r] @PUNCT -20;
  pos @DASH @TBAR_R -30;       pos @DASH @TBARLC_R -25;
} kern;
""")
    yus = [("ermal","smallyus","iotsyus"),("ibr","smallyus","iotsyus"),
           ("ermal","bigyus","iotbyus"),("ibr","bigyus","iotbyus")]
    soft = [("n","ermal","nsoft"),("l","ermal","lsoft"),
            ("t","palochka","tpal"),("k","palochka","kpal"),
            ("ts","palochka","tspal"),("ch","palochka","chpal"),
            ("p","palochka","ppal")]
    # ordered lookups: yus fusion must win before н/л consume the soft sign
    lines.append("feature liga {\n  lookup IOTYUS {")
    for a, b, out in yus:
        lines.append(f"    sub {a} {b} by {out};")
        lines.append(f"    sub lc.{a} lc.{b} by lc.{out};")
    lines.append("  } IOTYUS;\n  lookup SOFTFUSE {")
    for a, b, out in soft:
        lines.append(f"    sub {a} {b} by {out};")
        lines.append(f"    sub lc.{a} lc.{b} by lc.{out};")
        if b == "palochka":  # convention: palochka is written caseless as U+04C0
            lines.append(f"    sub lc.{a} {b} by lc.{out};")
    lines.append("  } SOFTFUSE;\n} liga;")
    return "\n".join(lines)

# ------------------------------------------------------------------- builder
def draw(pen, contours):
    for c in contours:
        pen.moveTo(c[0])
        for p in c[1:]:
            pen.lineTo(p)
        pen.closePath()

# letters whose diagonals reach the baseline with flat-cut feet
# (lc.a is excluded: its custom lowercase is a bowl, not a diagonal)
DIAG_FLARE = {"a", "l", "h", "zh", "adia", "bigyus",
              "lc.l", "lc.h", "lc.zh", "lc.adia", "lc.bigyus"}

def build(style, w, italic, fmt):
    slant = math.tan(math.radians(12)) if italic else 0.0
    dotr = 50 if w <= 100 else 66
    order = list(G.keys())
    fb = FontBuilder(UPM, isTTF=(fmt == "ttf"))
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({cp: n for cp, n in CMAP.items()})
    metrics, shapes, boxes = {}, {}, {}
    pad = w - 90  # Bold strokes are wider; advances widen to preserve sidebearings
    for name, gdef in G.items():
        # diagonal-footed letters flare at the baseline (the horizontal
        # terminal cut widens with weight faster than the stroke): the flat
        # weight delta under-compensates them and Bold АЛ welded at the feet.
        # Their advances widen by the flare's growth too
        gpad = pad + (pad * 32) // 60 if name in DIAG_FLARE and pad else pad
        dx = gpad // 2 if gdef["adv"] else 0
        plain = glyph_contours(gdef, w, dotr, 0.0, dx)
        boxes[name] = bbox(plain) if plain else (0,0,0,0)
        contours = glyph_contours(gdef, w, dotr, slant, dx) if slant else plain
        adv = gdef["adv"] + (gpad if gdef["adv"] else 0)
        xs = [x for c in contours for (x,y) in c]
        metrics[name] = (adv, int(min(xs)) if xs else 0)
        if fmt == "ttf":
            pen = TTGlyphPen(None)
            draw(pen, contours)
            shapes[name] = pen.glyph()
        else:
            pen = T2CharStringPen(adv, None)
            draw(pen, contours)
            shapes[name] = pen.getCharString()
    family, sub = "Chuzhditsa", style
    ps = f"Chuzhditsa-{style.replace(' ', '')}"
    if fmt == "ttf":
        fb.setupGlyf(shapes)
    else:
        fb.setupCFF(ps, {"FullName": f"{family} {sub}", "FamilyName": family,
                         "ItalicAngle": -12 if italic else 0}, shapes, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1050, descent=-350)
    fb.setupNameTable({"familyName": family, "styleName": sub, "psName": ps,
                       "fullName": f"{family} {sub}", "version": "Version 2.5",
                       "copyright": "Chuzhditsa - a Glagolitic-inspired pan-Slavic loanword face",
                       "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
                       "licenseInfoURL": "https://openfontlicense.org"})
    bold = w > 100
    fsSel = (0x01 if italic else 0) | (0x20 if bold else 0) | (0x40 if not (bold or italic) else 0) | 0x80
    fb.setupOS2(sTypoAscender=1050, sTypoDescender=-350, sTypoLineGap=0,
                usWinAscent=1100, usWinDescent=450, fsSelection=fsSel,
                usWeightClass=700 if bold else 400, sxHeight=500, sCapHeight=700)
    fb.setupPost(italicAngle=-12.0 if italic else 0.0)
    fb.font["head"].macStyle = (0x01 if bold else 0) | (0x02 if italic else 0)
    addOpenTypeFeaturesFromString(fb.font, make_fea(boxes, slant))
    path = os.path.join(OUT, f"{ps}.{fmt}")
    fb.save(path)
    return path

STYLES = [("Regular", 90, False), ("Bold", 150, False),
          ("Italic", 90, True), ("BoldItalic", 150, True)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for style, w, it in STYLES:
        for fmt in ("ttf", "otf"):
            print("built", build(style, w, it, fmt))
