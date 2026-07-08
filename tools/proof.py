#!/usr/bin/env python3
"""Render the Chuzhditsa proof sheet with real shaping (HarfBuzz: GSUB+GPOS live).
Output: tools/proof.png, rendered at 2x and downsampled."""
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
FONTS = os.path.join(HERE, "..", "fonts")
S = 2  # supersample factor

_cache = {}
def load(style):
    if style not in _cache:
        path = os.path.join(FONTS, f"Chuzhditsa-{style}.ttf")
        _cache[style] = (TTFont(path), hb.Font(hb.Face(hb.Blob.from_file_path(path))))
    return _cache[style]

def render(draw, style, text, x0, y0, size, fill="black", holefill="white"):
    tt, f = load(style)
    glyf, names, scale = tt["glyf"], tt.getGlyphOrder(), size/1000.0
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(f, buf)
    penx = x0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = glyf[names[info.codepoint]]
        if g.numberOfContours > 0:
            coords, ends, _ = g.getCoordinates(glyf); start, sol, hol = 0, [], []
            for e in ends:
                pts = [(penx+(pos.x_offset+cx)*scale, y0-(pos.y_offset+cy)*scale) for cx,cy in coords[start:e+1]]
                a = sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(pts,pts[1:]+pts[:1]))
                (hol if a>0 else sol).append(pts); start = e+1
            for p in sol: draw.polygon(p, fill=fill)
            for p in hol: draw.polygon(p, fill=holefill)
        penx += pos.x_advance*scale
    return penx

LINES = [
    ("Regular", 46, "АаБбВвГгДдЕеЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧч"),
    ("Regular", 46, "ШшЩщЪъЬьЫыЮюЯя · ЄєЁёЭэІіЇїҐґЂђЋћЃѓЌќЈј 0123456789"),
    ("Regular", 46, "Ўў Џџ Ҫҫ Ҙҙ Ңң Ққ Ғғ Ҳҳ Һһ Ӓӓ Ӧӧ Ӱӱ Ѫѫ Ѧѧ Ѕѕ Ӏӏ Ѩѩ Ѭѭ"),
    ("Regular", 46, "ўӣкенд · ҫӓңкс · т̢ʰӣк · Муҳаммад · Пе̌йчиң · крўаса̨ · бѩ"),
    ("Regular", 46, "нињо · фамиљя · пѩч · тӀыру · цӀқӀали · Кеня · Вроцўаф"),
    ("Bold",    46, "Прекарахме ўӣкенда в Мӱнхен с Һӓри!"),
    ("Italic",  46, "О̄сака, То̄кьо̄, Съул, Ҫесалоники, Шкьипъри́а"),
    ("BoldItalic", 46, "думи от чужбина, писани на чуждица"),
]

W = 1560
pitch, top, margin = 118, 70, 60
img = Image.new("RGB", (W*S, (top + pitch*len(LINES) + 40)*S), "white")
d = ImageDraw.Draw(img)
y = top
for style, size, text in LINES:
    render(d, style, text, margin*S, y*S, size*S)
    y += pitch
img = img.resize((W, img.height//S), Image.LANCZOS)
img.save(os.path.join(HERE, "proof.png"))
print("proof.png", img.size)
