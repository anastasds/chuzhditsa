#!/usr/bin/env python3
"""Generate the figures for paper/typeface.tex directly from the font engine."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont
import build_font as bf
from proof import render as hb_render

FIG = os.path.join(os.path.dirname(__file__), "..", "paper", "figures")
os.makedirs(FIG, exist_ok=True)
S = 2  # supersample

try:
    LABEL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26*S)
except Exception:
    LABEL = ImageFont.load_default()

def canvas(w, h):
    img = Image.new("RGB", (w*S, h*S), "white")
    return img, ImageDraw.Draw(img)

def save(img, name):
    img = img.resize((img.width//S, img.height//S), Image.LANCZOS)
    img.save(os.path.join(FIG, name))
    print(name)

def draw_contours(d, contours, ox, oy, sc):
    sol, hol = [], []
    for c in contours:
        a = sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(c, c[1:]+c[:1]))
        pts = [((ox+x*sc)*S, (oy-y*sc)*S) for x, y in c]
        (sol if a > 0 else hol).append(pts)
    for p in sol: d.polygon(p, fill="black")
    for p in hol: d.polygon(p, fill="white")

def rule(d, y, x0, x1, color=(220,60,60)):
    d.line([(x0*S, y*S), (x1*S, y*S)], fill=color, width=S)

def label(d, x, y, text):
    d.text((x*S, y*S), text, font=LABEL, fill=(90,90,90))

# --- legacy expanders (the "before" of the failure figures) ------------------
def legacy_contours(gdef, w):
    """v1 engine: per-segment rectangles + round discs at every vertex."""
    cs = []
    for st in gdef["strokes"]:
        k = st[0]
        if k == "L":
            pts = [(st[1],st[2]),(st[3],st[4])]
        elif k == "A":
            pts = bf.arc_pts(st[1],st[2],st[3],st[4],st[5])
        elif k == "R":
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],st[3]+w/2)))
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],max(10,st[3]-w/2)))[::-1])
            continue
        else:
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],st[3] or 50)))
            continue
        hw = w/2
        for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
            dx, dy = x2-x1, y2-y1
            dd = math.hypot(dx,dy) or 1
            nx, ny = -dy/dd*hw, dx/dd*hw
            cs.append(bf.ccw([(x1+nx,y1+ny),(x2+nx,y2+ny),(x2-nx,y2-ny),(x1-nx,y1-ny)]))
        for (x,y) in pts:
            cs.append(bf.ccw(bf.circle_pts(x, y, hw, 14)))
    return cs

def perp_contours(gdef, w):
    """Butt caps perpendicular to the stroke (no horizontal terminal cut)."""
    cs, paths = [], []
    for st in gdef["strokes"]:
        if st[0] == "L":
            paths.append(([(st[1],st[2]),(st[3],st[4])], w))
        elif st[0] == "A":
            paths.append((bf.arc_pts(st[1],st[2],st[3],st[4],st[5]), w))
    for path, ww in paths and bf_chain(paths) or []:
        cs.extend(offset_perp(path, ww/2))
    return cs

def bf_chain(paths):
    grouped = bf.chain_paths([p for p, _ in paths])
    return [(g, paths[0][1]) for g in grouped]

def offset_perp(pts, hw):
    normals = []
    for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
        dd = math.hypot(x2-x1, y2-y1) or 1
        normals.append(((y1-y2)/dd*hw, (x2-x1)/dd*hw))
    def isect(p, d1, q, d2):
        det = d1[0]*d2[1]-d1[1]*d2[0]
        if abs(det) < 1e-9: return None
        t = ((q[0]-p[0])*d2[1]-(q[1]-p[1])*d2[0])/det
        return (p[0]+d1[0]*t, p[1]+d1[1]*t)
    def side(sign):
        out = [(pts[0][0]+sign*normals[0][0], pts[0][1]+sign*normals[0][1])]
        for i in range(1, len(pts)-1):
            na, nb = normals[i-1], normals[i]
            d1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
            d2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
            hit = isect((pts[i-1][0]+sign*na[0], pts[i-1][1]+sign*na[1]), d1,
                        (pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1]), d2)
            concave = (d1[0]*d2[1]-d1[1]*d2[0])*sign > 0
            if hit and (concave or math.hypot(hit[0]-pts[i][0], hit[1]-pts[i][1]) <= 4*hw):
                out.append(hit)
            else:
                out.append((pts[i][0]+sign*na[0], pts[i][1]+sign*na[1]))
                out.append((pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1]))
        out.append((pts[-1][0]+sign*normals[-1][0], pts[-1][1]+sign*normals[-1][1]))
        return out
    return [bf.ccw(side(1) + side(-1)[::-1])]

SC = 0.42  # font units -> px at 1x

def fig1():
    img, d = canvas(1460, 460)
    g = bf.G["b"]
    ox, oy = 90, 380
    for st in g["strokes"]:  # skeleton
        if st[0] == "L":
            d.line([((ox+st[1]*SC)*S,(oy-st[2]*SC)*S),((ox+st[3]*SC)*S,(oy-st[4]*SC)*S)], fill="black", width=2*S)
            for (x,y) in ((st[1],st[2]),(st[3],st[4])):
                r = 7*S
                d.ellipse([(ox+x*SC)*S-r,(oy-y*SC)*S-r,(ox+x*SC)*S+r,(oy-y*SC)*S+r], fill=(220,60,60))
        elif st[0] == "R":
            x0,y0 = (ox+(st[1]-st[3])*SC)*S,(oy-(st[2]+st[3])*SC)*S
            x1,y1 = (ox+(st[1]+st[3])*SC)*S,(oy-(st[2]-st[3])*SC)*S
            d.ellipse([x0,y0,x1,y1], outline="black", width=2*S)
    label(d, 90, 400, "skeleton")
    for i,(w,slant,name) in enumerate([(90,0,"Regular  w=90"),(150,0,"Bold  w=150"),(90,math.tan(math.radians(12)),"Italic  12°")]):
        ox = 470 + i*340
        draw_contours(d, bf.glyph_contours(g, w, 50 if w<100 else 66, slant), ox, 380, SC)
        label(d, ox, 400, name)
    save(img, "fig1_stroke_model.png")

def fig2():
    img, d = canvas(1460, 480)
    ldef = bf.G["l"]
    rule(d, 380, 40, 1420, (200,200,200))
    rule(d, 380-700*SC, 40, 1420, (200,200,200))
    panels = [(legacy_contours(ldef, 90), "v1: round caps"),
              (offset_perp(bf.chain_paths([[(70,0),(330,718)],[(330,718),(590,0)]])[0], 45), "butt caps, angled feet"),
              (bf.glyph_contours(ldef, 90, 50, 0), "horizontal terminal cut")]
    for i,(cs,name) in enumerate(panels):
        ox = 120 + i*450
        draw_contours(d, cs, ox, 380, SC)
        label(d, ox, 410, name)
    save(img, "fig2_terminals.png")

def fig3():
    img, d = canvas(1460, 480)
    mdef = bf.G["m"]
    for i,(cs,name) in enumerate([(legacy_contours(mdef, 90), "v1: overlapped strokes, disc joints"),
                                  (bf.glyph_contours(mdef, 90, 50, 0), "chained paths, mitered corners")]):
        ox = 180 + i*600
        draw_contours(d, cs, ox, 380, SC)
        label(d, ox, 410, name)
    save(img, "fig3_joints.png")

def fig4():
    img, d = canvas(1460, 1000)
    a700 = dict(adv=660, strokes=[("L",70,0,330,700),("L",330,700,590,0),("L",190,230,470,230)])
    e350 = dict(adv=620, strokes=[("L",500,700,160,700),("L",160,700,160,0),("L",160,0,500,0),("L",160,350,430,350)])
    ring0 = [bf.ccw(bf.circle_pts(400,350,305+45)), bf.ccw(bf.circle_pts(400,350,305-45))[::-1]]
    perfect = [bf.ccw(bf.circle_pts(400,350,355+45)), bf.ccw(bf.circle_pts(400,350,355-45))[::-1]]
    rows = [
        [(ring0, "flush"), (bf.glyph_contours(bf.G["o"],90,50,0), "overshot"),
         (bf.glyph_contours(a700,90,50,0), "apex 700"), (bf.glyph_contours(bf.G["a"],90,50,0), "apex 718")],
        [(bf.glyph_contours(e350,90,50,0), "bar 350"), (bf.glyph_contours(bf.G["e"],90,50,0), "bar 368"),
         (perfect, "true circle"), (bf.glyph_contours(bf.G["o"],90,50,0), "96.5% wide")],
    ]
    for r, row in enumerate(rows):
        base = 400 + r*460
        rule(d, base, 40, 1420); rule(d, base-700*SC, 40, 1420)
        x = 90
        for cs, name in row:
            draw_contours(d, cs, x, base, SC)
            label(d, x+30, base+30, name)
            x += 350
    save(img, "fig4_optical.png")

def fig5():
    img, d = canvas(1460, 680)
    word = ["p","o","l","e","n","o"]
    for row,(pad,name) in enumerate([(0,"Bold strokes on Regular advances"),(60,"Bold advances widened by the weight delta")]):
        ox, oy = 120, 320 + row*290
        label(d, 120, oy-312 if row == 0 else oy-262, name)
        for gname in word:
            g = bf.G["lc."+gname]
            draw_contours(d, bf.glyph_contours(g, 150, 66, 0, pad//2), ox, oy, SC)
            ox += (g["adv"] + pad) * SC
    save(img, "fig5_bold_color.png")

def fig6():
    img, d = canvas(1460, 500)
    o = bf.G["o"]
    slant = math.tan(math.radians(12))
    upright = bf.glyph_contours(o, 90, 50, 0)
    sheared_after = [[(x+y*slant, y) for x,y in c] for c in upright]
    for i,(cs,name) in enumerate([(sheared_after, "outline sheared: weight wobbles ±10%"),
                                  (bf.glyph_contours(o, 90, 50, slant), "centerline sheared: constant weight")]):
        ox = 200 + i*620
        draw_contours(d, cs, ox, 400, SC)
        label(d, ox, 430, name)
    save(img, "fig6_italic.png")

def fig7():
    img, d = canvas(1460, 500)
    tpal_v1 = dict(adv=780, strokes=[("L",70,700,590,700),("L",330,0,330,700),("L",650,0,650,700)])
    for i,(g,name) in enumerate([(tpal_v1,"тӀ fused, full palochka"),(bf.G["p"],"п"),(bf.G["tpal"],"тӀ shipped: raised palochka")]):
        ox = 130 + i*470
        draw_contours(d, bf.glyph_contours(g, 90, 50, 0), ox, 380, SC)
        label(d, ox, 410, name)
    save(img, "fig7_ligature.png")

def fig8():
    img, d = canvas(1460, 460)
    hb_render(d, "Regular", "А̄ а̄ ӧ̄ т̢ Т̢", 80*S, 360*S, 300*S)
    label(d, 80, 400, "one mark, five computed anchors: cap, x-height, above dots, under stem")
    save(img, "fig8_anchors.png")

def fig9():
    img, d = canvas(1560, 700)
    rows = [
        ("Regular", 52, "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЫЮЯ"),
        ("Regular", 52, "абвгдежзийклмнопрстуфхцчшщъьыюя"),
        ("Regular", 52, "Ўў Џџ Ҫҫ Ҙҙ Ққ Ңң Ҳҳ Ғғ Һһ Ѕѕ Ӏ Ӓӓ Ӧӧ Ӱӱ Ыы"),
        ("Regular", 52, "Ѫѫ Ѧѧ Ѩѩ Ѭѭ Ӣӣ Ӯӯ · тʰ дʱ т̢ а̨ а̄ а́ а̌"),
        ("Bold", 52, "ўӣкенд ҫӓңкс Пе̌йчиң Муҳаммад крўаса̨ бѩ"),
        ("Italic", 52, "думи от чужбина, писани на чуждица"),
    ]
    y = 95
    for style, size, text in rows:
        hb_render(d, style, text, 50*S, y*S, size*S)
        y += 105
    save(img, "fig9_specimen.png")

def fig10():
    img, d = canvas(1460, 400)
    hb_render(d, "Regular", "Аа Бб Рр Фф Ѩѩ", 70*S, 300*S, 165*S)
    label(d, 70, 350, "two-case architecture: custom а б р ф; systematic derivation elsewhere")
    save(img, "fig10_cases.png")

if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10):
        f()
