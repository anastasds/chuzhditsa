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
"question": dict(adv=560, strokes=[(A,290,520,165,150,-60),(L,372,377,290,250),(D,290,55,0)]),
"guillemetleft": dict(adv=620, strokes=[(L,290,470,150,330),(L,150,330,290,190),(L,510,470,370,330),(L,370,330,510,190)]),
"guillemetright": dict(adv=620, strokes=[(L,110,470,250,330),(L,250,330,110,190),(L,330,470,470,330),(L,470,330,330,190)]),
"emdash": dict(adv=720, strokes=[(L,40,300,680,300)]),
"zero": dict(adv=680, strokes=[(R,340,350,300)]),
"one": dict(adv=460, strokes=[(L,280,0,280,700),(L,280,700,150,560)]),
"two": dict(adv=640, strokes=[(A,330,505,185,160,-15),(L,508,455,140,0),(L,140,0,540,0)]),
"three": dict(adv=640, strokes=[(A,330,520,175,110,-70),(A,330,185,180,70,-110)]),
"four": dict(adv=660, strokes=[(L,440,0,440,700),(L,440,700,140,190),(L,140,190,580,190)]),
"five": dict(adv=640, strokes=[(L,500,700,185,700),(L,185,700,185,430),(A,330,240,200,115,-115)]),
"six": dict(adv=660, strokes=[(R,330,225,195),(A,455,430,330,100,175)]),
"seven": dict(adv=600, strokes=[(L,120,700,540,700),(L,540,700,260,0)]),
"eight": dict(adv=660, strokes=[(R,330,515,160),(R,330,175,190)]),
"nine": dict(adv=660, strokes=[(R,330,475,195),(A,205,270,330,-80,5)]),
"egrave": dict(adv=620, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368),(L,390,790,270,930)]),
"igrave": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(L,390,790,270,930)]),
"middot": dict(adv=300, strokes=[(D,150,300,0)]),
"dotcircle": dict(adv=660, strokes=[(D,330+180,350,28),(D,330-180,350,28),(D,330,350+180,28),(D,330,350-180,28),(D,330+127,350+127,28),(D,330-127,350+127,28),(D,330+127,350-127,28),(D,330-127,350-127,28)]),
"arrow": dict(adv=660, strokes=[(L,70,300,560,300),(L,440,400,560,300),(L,440,200,560,300)]),
"hyphen": dict(adv=420, strokes=[(L,70,300,350,300)]),
"endash": dict(adv=520, strokes=[(L,50,300,470,300)]),
"quoteright": dict(adv=210, strokes=[(L,130,780,80,600)]),
"a": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0),(L,190,230,470,230)]),
"b": dict(adv=660, strokes=[(R,340,190,180),(L,160,190,160,700),(L,160,700,480,700)]),
"v": dict(adv=660, strokes=[(L,160,0,160,700),(R,320,515,155),(R,330,175,170)]),
"g": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700)]),
"d": dict(adv=660, strokes=[(L,330,715,150,140),(L,330,715,510,140),(L,70,140,590,140),(L,110,140,110,-150),(L,550,140,550,-150)]),
"e": dict(adv=620, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368)]),
"zh": dict(adv=660, strokes=[(L,330,0,330,700),(L,70,700,330,390),(L,590,700,330,390),(L,70,0,330,310),(L,590,0,330,310)]),
"z": dict(adv=640, strokes=[(A,330,520,175,110,-70),(A,330,185,180,70,-110)]),
"i": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700)]),
"ibr": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(A,330,930,130,205,335)]),
"k": dict(adv=640, strokes=[(L,160,0,160,700),(L,500,700,170,370),(L,500,0,170,350)]),
"l": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0)]),
"m": dict(adv=660, strokes=[(L,90,0,90,700),(L,90,700,330,270),(L,330,270,570,700),(L,570,0,570,700)]),
"n": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,368,500,368)]),
"o": dict(adv=800, strokes=[(R,400,350,355)]),
"p": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,700,500,700)]),
"r": dict(adv=640, strokes=[(L,160,0,160,700),(R,340,510,180)]),
"s": dict(adv=720, strokes=[(A,400,350,350,50,310)]),
"t": dict(adv=660, strokes=[(L,70,700,590,700),(L,330,0,330,700)]),
"u": dict(adv=660, strokes=[(L,100,700,335,315),(L,560,700,190,-180)]),
"f": dict(adv=660, strokes=[(L,330,-120,330,800),(R,330,350,240)]),
"h": dict(adv=660, strokes=[(L,90,0,570,700),(L,90,700,570,0)]),
"ts": dict(adv=680, strokes=[(L,150,700,150,60),(L,150,60,540,60),(L,540,700,540,60),(L,540,60,540,-150),(L,540,-150,630,-150)]),
"ch": dict(adv=640, strokes=[(L,150,700,150,430),(L,150,430,480,430),(L,480,0,480,700)]),
"sh": dict(adv=680, strokes=[(L,120,700,120,60),(L,340,700,340,60),(L,560,700,560,60),(L,120,60,560,60)]),
"sht": dict(adv=700, strokes=[(L,120,700,120,60),(L,340,700,340,60),(L,560,700,560,60),(L,120,60,560,60),(L,560,60,560,-150),(L,560,-150,650,-150)]),
"er": dict(adv=640, strokes=[(L,60,700,240,700),(L,240,700,240,0),(R,405,165,165)]),
"ermal": dict(adv=600, strokes=[(L,190,0,190,700),(R,355,165,165)]),
"yeru": dict(adv=760, strokes=[(L,130,0,130,700),(R,295,165,165),(L,620,0,620,700)]),
"yu": dict(adv=720, strokes=[(L,130,0,130,700),(L,130,350,270,350),(R,455,350,185)]),
"ya": dict(adv=660, strokes=[(L,500,0,500,700),(R,325,515,175),(L,430,360,160,0)]),
# -- extensions --------------------------------------------------------------
"ubr": dict(adv=660, strokes=[(L,100,700,335,315),(L,560,700,190,-180),(A,330,930,130,205,335)]),
"dz": dict(adv=640, strokes=[(A,340,505,175,40,270),(A,330,190,175,85,-140)]),
"bigyus": dict(adv=660, strokes=[(L,330,715,140,0),(L,330,715,520,0),(L,205,255,455,255),(L,330,255,330,0)]),
"smallyus": dict(adv=660, strokes=[(L,330,715,140,190),(L,330,715,520,190),(L,140,190,520,190),(L,215,190,215,0),(L,445,190,445,0)]),
"dzh": dict(adv=660, strokes=[(L,150,700,150,60),(L,510,700,510,60),(L,150,60,510,60),(L,330,60,330,-160)]),
"shha": dict(adv=640, strokes=[(L,150,0,150,700),(A,315,300,165,180,0),(L,480,0,480,300)]),
"adia": dict(adv=660, strokes=[(L,70,0,330,718),(L,330,718,590,0),(L,190,230,470,230)]+DOTS),
"odia": dict(adv=800, strokes=[(R,400,350,355),(D,295,880,0),(D,505,880,0)]),
"udia": dict(adv=660, strokes=[(L,100,700,335,315),(L,560,700,190,-180)]+DOTS),
"nghk": dict(adv=680, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,368,500,368),(L,500,0,500,-150),(L,500,-150,590,-150)]),
"khk": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,700,170,370),(L,500,0,170,350),(L,500,0,500,-150),(L,500,-150,590,-150)]),
"gbar": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,50,420,310,420)]),
"hhk": dict(adv=700, strokes=[(L,90,0,570,700),(L,90,700,570,0),(L,570,0,570,-150),(L,570,-150,660,-150)]),
"zhk": dict(adv=640, strokes=[(A,330,520,175,110,-70),(A,330,185,180,70,-110),(L,330,5,330,-150),(L,330,-150,420,-150)]),
"shk": dict(adv=640, strokes=[(A,340,350,285,50,310),(L,340,65,340,-150),(L,340,-150,430,-150)]),
"palochka": dict(adv=460, strokes=[(L,230,0,230,700),(L,140,700,320,700),(L,140,0,320,0)]),
"imac": dict(adv=660, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,0,500,700),(L,170,890,490,890)]),
"umac": dict(adv=660, strokes=[(L,100,700,335,315),(L,560,700,190,-180),(L,170,890,490,890)]),
# -- pan-Slavic superset ------------------------------------------------------
# е went angular so that Ukrainian round є keeps the historic wide-e form
"ye": dict(adv=760, strokes=[(A,395,350,345,55,305),(L,320,350,655,350)]),
"yo": dict(adv=620, strokes=[(L,500,700,160,700),(L,160,700,160,0),(L,160,0,500,0),(L,160,368,430,368)]+DOTS),
"ee": dict(adv=790, strokes=[(A,360,350,345,-130,130),(L,205,350,525,350)]),
"iukr": dict(adv=380, strokes=[(L,190,0,190,700)]),
"yi": dict(adv=380, strokes=[(L,190,0,190,700),(D,105,860,0),(D,275,860,0)]),
"geup": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,540,700,540,830)]),
"dje": dict(adv=620, strokes=[(L,60,700,460,700),(L,260,340,260,700),(A,370,340,110,180,0),(L,480,-80,480,340),(L,480,-80,390,-150)]),
"tshe": dict(adv=580, strokes=[(L,180,0,180,700),(L,40,580,340,580),(A,300,330,120,180,0),(L,420,0,420,330)]),
"gje": dict(adv=620, strokes=[(L,160,0,160,700),(L,160,700,540,700),(L,390,790,490,900)]),
"kje": dict(adv=640, strokes=[(L,160,0,160,700),(L,500,700,170,370),(L,500,0,170,350),(L,300,790,400,900)]),
"je": dict(adv=580, strokes=[(L,400,120,400,700),(A,285,120,115,0,-150)]),
# -- combining marks (zero advance, drawn back over previous glyph) ----------
"fita": dict(adv=800, strokes=[(R,400,350,355),(L,185,350,615,350)]),
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
"nsoft": dict(adv=850, strokes=[(L,160,0,160,700),(L,500,0,500,700),(L,160,350,500,350),(R,645,165,145)]),
"lsoft": dict(adv=940, strokes=[(L,70,0,330,700),(L,330,700,590,0),(L,590,0,590,340),(R,735,165,145)]),
# iotated yuses (Old Cyrillic revivals, U+0468/046C): stem + connector + yus
"iotsyus": dict(adv=840, strokes=[(L,130,0,130,700),(L,130,350,385,350),(L,510,700,320,190),(L,510,700,700,190),(L,320,190,700,190),(L,395,190,395,0),(L,625,190,625,0)]),
"iotbyus": dict(adv=840, strokes=[(L,130,0,130,700),(L,130,350,415,350),(L,510,700,320,0),(L,510,700,700,0),(L,385,255,635,255),(L,510,255,510,0)]),
# ejective fusions: in the ligature the palochka rises to the upper half
# (like the apostrophe of t' k'), keeping the fusion distinct from п
"tpal": dict(adv=790, strokes=[(L,70,700,590,700),(L,330,0,330,700),(L,700,360,700,700)]),
"kpal": dict(adv=740, strokes=[(L,160,0,160,700),(L,500,700,170,370),(L,500,0,170,350),(L,650,360,650,700)]),
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
    return (round(x*SX), round(y*SY) if y >= 0 else round(y))

def lc_glyph(gdef):
    strokes = []
    for st in gdef["strokes"]:
        k = st[0]
        if k == L:
            (x1,y1),(x2,y2) = lc_pt(st[1],st[2]), lc_pt(st[3],st[4])
            strokes.append((L,x1,y1,x2,y2))
        elif k == A:
            cx, cy = lc_pt(st[1], st[2])
            strokes.append((A,cx,cy,round(st[3]*SX),st[4],st[5]))
        elif k in (R, D):
            cx, cy = lc_pt(st[1], st[2])
            strokes.append((k,cx,cy,round(st[3]*SX)))
    return dict(adv=round(gdef["adv"]*SX), strokes=strokes)

LC_CUSTOM = {
"a": dict(adv=640, strokes=[(R,300,250,235),(L,535,10,535,490)]),
"b": dict(adv=620, strokes=[(R,320,250,225),(L,95,250,95,700),(L,95,700,400,700)]),
"r": dict(adv=670, strokes=[(L,150,-200,150,500),(R,385,250,235)]),
"f": dict(adv=560, strokes=[(L,280,-180,280,680),(R,280,250,215)]),
# lc ejective fusions: explicit forms with raised half-palochka and clear gap
"tpal": dict(adv=600, strokes=[(L,50,500,425,500),(L,238,0,238,500),(L,510,270,510,500)]),
"kpal": dict(adv=560, strokes=[(L,115,0,115,500),(L,360,500,122,264),(L,360,0,122,252),(L,470,270,470,500)]),
"tspal": dict(adv=590, strokes=[(L,108,500,108,43),(L,108,43,389,43),(L,389,500,389,43),(L,389,43,389,-150),(L,389,-150,454,-150),(L,500,270,500,500)]),
"chpal": dict(adv=545, strokes=[(L,108,500,108,310),(L,108,310,346,310),(L,346,0,346,500),(L,455,270,455,500)]),
"ppal": dict(adv=560, strokes=[(L,115,0,115,500),(L,360,0,360,500),(L,115,500,360,500),(L,470,270,470,500)]),
# lowercase і ї ј carry dots / descender curls the caps lack
"iukr": dict(adv=330, strokes=[(L,165,0,165,500),(D,165,650,0)]),
"yi": dict(adv=330, strokes=[(L,165,0,165,500),(D,82,650,0),(D,248,650,0)]),
"je": dict(adv=440, strokes=[(L,300,-30,300,500),(A,200,-30,100,0,-150),(D,300,650,0)]),
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

def area(pts):
    return sum(x1*y2 - x2*y1 for (x1,y1),(x2,y2) in zip(pts, pts[1:]+pts[:1])) / 2

def ccw(pts):
    return pts if area(pts) > 0 else pts[::-1]

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

    def side(sign):
        out = [cap_pt(pts[0], pts[1], sign*normals[0][0], sign*normals[0][1])]
        for i in range(1, len(pts)-1):
            na, nb = normals[i-1], normals[i]
            d1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
            d2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
            p1 = (pts[i-1][0]+sign*na[0], pts[i-1][1]+sign*na[1])
            p2 = (pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1])
            hit = line_isect(p1, d1, p2, d2)
            # concave side: the intersection is the correct join, no limit
            # (a bevel here would fold the outline over itself)
            concave = (d1[0]*d2[1] - d1[1]*d2[0]) * sign > 0
            if hit and (concave or math.hypot(hit[0]-pts[i][0], hit[1]-pts[i][1]) <= miter_limit*hw):
                out.append(hit)
            else:  # bevel (convex corner past the miter limit)
                out.append((pts[i][0]+sign*na[0], pts[i][1]+sign*na[1]))
                out.append((pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1]))
        out.append(cap_pt(pts[-1], pts[-2], sign*normals[-1][0], sign*normals[-1][1]))
        return out

    return [ccw(side(1) + side(-1)[::-1])]

def chain_paths(paths, tol=1):
    """Merge open centerline paths that meet end-to-end at points shared by
    exactly two strokes, so apexes (Л, И, М, ...) become mitered corners."""
    def key(p):
        return (round(p[0]/tol), round(p[1]/tol))
    degree = {}
    for path in paths:
        for p in (path[0], path[-1]):
            degree[key(p)] = degree.get(key(p), 0) + 1
    paths = [list(p) for p in paths]
    merged = True
    while merged:
        merged = False
        for i in range(len(paths)):
            if merged: break
            for j in range(i+1, len(paths)):
                a, b = paths[i], paths[j]
                joins = None
                if key(a[-1]) == key(b[0]) and degree.get(key(a[-1])) == 2:
                    joins = a + b[1:]
                elif key(a[-1]) == key(b[-1]) and degree.get(key(a[-1])) == 2:
                    joins = a + b[-2::-1]
                elif key(a[0]) == key(b[-1]) and degree.get(key(a[0])) == 2:
                    joins = b + a[1:]
                elif key(a[0]) == key(b[0]) and degree.get(key(a[0])) == 2:
                    joins = b[::-1] + a[1:]
                if joins:
                    paths[i] = joins
                    del paths[j]
                    merged = True
                    break
    return paths

def glyph_contours(gdef, w, dotr, slant, dx=0):
    """Centerline model -> outlines. Shear applies to centerlines so the
    italic keeps constant perpendicular weight; dx shifts bold sidebearings."""
    def sh(pt):
        x, y = pt
        return (x + y*slant + dx, y)
    open_paths, cs = [], []
    for st in gdef["strokes"]:
        kind = st[0]
        if kind == L:
            open_paths.append(([(st[1],st[2]), (st[3],st[4])], w))
        elif kind == A:
            # tight arcs (breve, small bowls) can't carry the full Bold weight
            weff = min(w, max(44, int(st[3]*0.85)))
            pts = arc_pts(st[1],st[2],st[3],st[4],st[5])
            if st[3] >= 290:  # match the big-round compression of о
                pts = [(st[1]+(x-st[1])*0.965, y) for x, y in pts]
            open_paths.append((pts, weff))
        elif kind == R:
            cx, cy = sh((st[1], st[2]))
            r = st[3]
            sqz = 0.965 if r >= 200 else 1.0  # optical: big rounds compress slightly
            wr = min(w, max(44, int(r*0.85)))  # keep counters open in Bold
            cs.append(ccw([(cx+(x-cx)*sqz, y) for x, y in circle_pts(cx,cy,r+wr/2)]))
            cs.append(ccw([(cx+(x-cx)*sqz, y) for x, y in circle_pts(cx,cy,max(10,r-wr/2))])[::-1])
        elif kind == D:
            cx, cy = sh((st[1], st[2]))
            cs.append(ccw(circle_pts(cx,cy,st[3] or dotr)))
        else:
            raise ValueError(kind)
    for weff in sorted({we for _, we in open_paths}):
        group = [p for p, we in open_paths if we == weff]
        for path in chain_paths(group):
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
@T_CAP = [g t gbar geup gje];
@T_LC = [lc.g lc.t lc.gbar lc.geup lc.gje];
@DIAG_CAP = [a l d adia bigyus];
@DIAG_LC = [lc.a lc.l lc.d lc.adia lc.bigyus];
@U_CAP = [u ubr udia umac];
@U_LC = [lc.u lc.ubr lc.udia lc.umac];
@ROUND_CAP = [o odia s ye ee fita];
@ROUND_LC = [lc.o lc.odia lc.s lc.ye lc.ee lc.fita];
feature kern {
  pos @T_CAP @DIAG_CAP -55;   pos @T_LC @DIAG_LC -45;
  pos @T_CAP @ROUND_CAP -60;  pos @T_LC @ROUND_LC -50;
  pos @DIAG_CAP @U_CAP -40;   pos @DIAG_LC @U_LC -35;
  pos @U_CAP @DIAG_CAP -40;   pos @U_LC @DIAG_LC -35;
  pos [t g u lc.t lc.g lc.u] [period comma] -70;
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
        dx = pad // 2 if gdef["adv"] else 0
        plain = glyph_contours(gdef, w, dotr, 0.0, dx)
        boxes[name] = bbox(plain) if plain else (0,0,0,0)
        contours = glyph_contours(gdef, w, dotr, slant, dx) if slant else plain
        adv = gdef["adv"] + (pad if gdef["adv"] else 0)
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
                       "fullName": f"{family} {sub}", "version": "Version 2.3",
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
