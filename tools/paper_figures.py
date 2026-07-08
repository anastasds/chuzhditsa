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
    LABEL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22*S)
except Exception:
    LABEL = ImageFont.load_default()

def canvas(w, h):
    img = Image.new("RGB", (w*S, h*S), "white")
    return img, ImageDraw.Draw(img)

def save(img, name):
    img = img.resize((img.width//S, img.height//S), Image.LANCZOS)
    from PIL import ImageChops
    bg = Image.new("RGB", img.size, "white")
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        pad = 22
        bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad),
                min(img.width, bbox[2]+pad), min(img.height, bbox[3]+pad))
        img = img.crop(bbox)
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
    return bf.chain_paths(paths)

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
              (offset_perp(bf.chain_paths([([(70,0),(330,718)],90),([(330,718),(590,0)],90)])[0][0], 45), "butt caps, angled feet"),
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
    img, d = canvas(1460, 720)
    word = ["p","o","l","e","n","o"]
    sc5 = 0.32
    for row,(pad,name) in enumerate([(0,"Bold strokes on Regular advances"),(60,"Bold advances widened by the weight delta")]):
        oy = 300 + row*330
        label(d, 120, oy-255, name)
        ox = 120
        for gname in word:
            g = bf.G["lc."+gname]
            gpad = pad + (pad*32)//60 if ("lc."+gname) in bf.DIAG_FLARE and pad else pad
            draw_contours(d, bf.glyph_contours(g, 150, 66, 0, gpad//2), ox, oy, sc5)
            ox += (g["adv"] + gpad) * sc5
    save(img, "fig5_bold_color.png")

def fig6():
    img, d = canvas(1460, 560)
    o = bf.G["o"]
    slant = math.tan(math.radians(12))
    upright = bf.glyph_contours(o, 90, 50, 0)
    sheared_after = [[(x+y*slant, y) for x,y in c] for c in upright]
    sheared_center = bf.glyph_contours(o, 90, 50, slant)
    ox, oy, sc = 120, 460, 0.56
    for cs, color, wd in ((sheared_after, (200,60,60), 3), (sheared_center, "black", 2)):
        for c in cs:
            pts = [((ox+x*sc)*S, (oy-y*sc)*S) for x, y in c]
            d.line(pts + [pts[0]], fill=color, width=wd*S)
    label(d, 100, 490, "overlaid outlines: red = outline sheared, black = centerline sheared")
    px, py, pw, ph = 780, 420, 560, 300
    d.rectangle([px*S, (py-ph)*S, (px+pw)*S, py*S], outline=(150,150,150), width=S)
    k = slant
    def thickness(theta):
        c_, s_ = math.cos(theta), math.sin(theta)
        return 90/math.hypot(c_, s_ - k*c_)
    for t, color in ((None, "black"), (thickness, (200,60,60))):
        pts = []
        for i in range(181):
            th = i/180*2*math.pi
            val = 90 if t is None else t(th)
            X = px + pw*i/180
            Y = py - ph*(val-70)/40
            pts.append((X*S, Y*S))
        d.line(pts, fill=color, width=2*S)
    label(d, px, py+14, "stroke thickness around the ring, 0-360°")
    label(d, px-60, py-ph*(90-70)/40-14, "90")
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

# ---------------- second batch: exhaustive-coverage figures ------------------

def offset_fold(pts, hw):
    """The buggy join: bevel on BOTH sides, folding the outline on concave corners."""
    normals = []
    for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
        dd = math.hypot(x2-x1, y2-y1) or 1
        normals.append(((y1-y2)/dd*hw, (x2-x1)/dd*hw))
    def side(sign):
        out = [(pts[0][0]+sign*normals[0][0], pts[0][1]+sign*normals[0][1])]
        for i in range(1, len(pts)-1):
            na, nb = normals[i-1], normals[i]
            out.append((pts[i][0]+sign*na[0], pts[i][1]+sign*na[1]))
            out.append((pts[i][0]+sign*nb[0], pts[i][1]+sign*nb[1]))
        out.append((pts[-1][0]+sign*normals[-1][0], pts[-1][1]+sign*normals[-1][1]))
        return out
    return [side(1) + side(-1)[::-1]]

def fig11():
    img, d = canvas(1460, 560)
    # (a) join anatomy diagram
    ox, oy, sc = 60, 430, 0.5
    p = [(80,0),(330,700),(580,0)]
    for sign,color in ((1,(120,120,220)),(-1,(220,120,120))):
        pts = offset_perp(p, 60)[0]
        n = len(p)
        left = pts[:len(pts)//2+2]
        d.line([((ox+x*sc)*S,(oy-y*sc)*S) for x,y in bf.chain_paths([(p,90)])[0][0]], fill="black", width=2*S)
    # centerline + offsets drawn simply
    def line(a, b, color, wd=2, dash=False):
        d.line([((ox+a[0]*sc)*S,(oy-a[1]*sc)*S),((ox+b[0]*sc)*S,(oy-b[1]*sc)*S)], fill=color, width=wd*S)
    line((80,0),(330,700),"black",3); line((330,700),(580,0),"black",3)
    hw = 90
    for sign,color in ((1,(70,70,200)),(-1,(200,70,70))):
        s1 = offset_perp([(80,0),(330,700),(580,0)], hw)[0]
        half = s1[:3] if sign>0 else s1[3:][::-1]
        for a,b in zip(half, half[1:]):
            line(a,b,color,2)
        apex = half[1]
        r = 8*S
        cxp, cyp = (ox+apex[0]*sc)*S, (oy-apex[1]*sc)*S
        d.ellipse([cxp-r,cyp-r,cxp+r,cyp+r], outline=color, width=S)
    label(d, 60, 460, "offset sides: outer miter, inner exact")
    # (b) folded outline under even-odd
    m = [(90,0),(90,700),(330,270),(570,700),(570,0)]
    folded = offset_fold(m, 45)
    pts = [((760+x*0.42)*S,(430-y*0.42)*S) for x,y in folded[0]]
    d.polygon(pts, fill="black")
    label(d, 730, 460, "concave bevel: the fold")
    # (c) correct
    draw_contours(d, bf.glyph_contours(bf.G["m"], 90, 50, 0), 1130, 430, 0.42)
    label(d, 1120, 460, "exact intersection")
    save(img, "fig11_join_anatomy.png")

def fig12():
    img, d = canvas(1460, 700)
    # wrong lookup order: soft-fusion consumes ь first -> љ + ѫ
    ox = 140
    for g in ("lc.lsoft", "lc.bigyus"):
        draw_contours(d, bf.glyph_contours(bf.G[g], 90, 50, 0), ox, 250, 0.34)
        ox += bf.G[g]["adv"]*0.34
    label(d, 140, 285, "soft-sign fusion first:  љ + ѫ  — the documented spelling is unreachable")
    ox = 140
    for g in ("lc.l", "lc.iotbyus"):
        draw_contours(d, bf.glyph_contours(bf.G[g], 90, 50, 0), ox, 610, 0.34)
        ox += bf.G[g]["adv"]*0.34
    label(d, 140, 645, "yus fusion ordered first:  л + ѭ  — as the orthography specifies")
    save(img, "fig12_lookup_order.png")

def fig13():
    img, d = canvas(1460, 620)
    pairs = [(("lc.n","lc.ermal"), "lc.nsoft"), (("lc.l","lc.ermal"), "lc.lsoft"),
             (("lc.ermal","lc.smallyus"), "lc.iotsyus"), (("lc.ermal","lc.bigyus"), "lc.iotbyus")]
    for i, (parts, fused) in enumerate(pairs):
        ox = 90 + (i % 2)*700
        oy = 230 + (i // 2)*290
        for g in parts:
            draw_contours(d, bf.glyph_contours(bf.G[g], 90, 50, 0), ox, oy, 0.26)
            ox += bf.G[g]["adv"]*0.26 + 10
        ox += 16
        draw_contours(d, bf.glyph_contours(bf.G["arrow"], 90, 50, 0), ox, oy+13, 0.26)
        ox += bf.G["arrow"]["adv"]*0.26 + 26
        draw_contours(d, bf.glyph_contours(bf.G[fused], 90, 50, 0), ox, oy, 0.26)
    label(d, 90, 555, "the GSUB fusion inventory: нь, ль, ьѧ, ьѫ — sequence in, silhouette out")
    save(img, "fig13_fusions.png")

def unclamped_contours(gdef, w):
    cs = []
    for st in gdef["strokes"]:
        k = st[0]
        if k == "L":
            cs.extend(bf.offset_polyline([(st[1],st[2]),(st[3],st[4])], w/2))
        elif k == "A":
            cs.extend(bf.offset_polyline(bf.arc_pts(st[1],st[2],st[3],st[4],st[5]), w/2))
        elif k == "R":
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],st[3]+w/2)))
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],max(10,st[3]-w/2)))[::-1])
        elif k == "D":
            cs.append(bf.ccw(bf.circle_pts(st[1],st[2],st[3] or 66)))
    return cs

def fig14():
    img, d = canvas(1460, 1240)
    glyphs = ["lc.ubr", "lc.dz", "lc.v"]
    for row, (fn, name) in enumerate([(unclamped_contours, "Bold stroke uncapped: small arcs and bowls clog"),
                                      (lambda g,w: bf.glyph_contours(g, w, 66, 0), "stroke clamped to the local radius budget")]):
        ox, oy = 160, 470 + row*580
        label(d, 160, oy+96, name)
        for gname in glyphs:
            g = bf.G[gname]
            draw_contours(d, fn(g, 150), ox, oy, 0.4)
            ox += (g["adv"]+60)*0.4 + 40
    save(img, "fig14_clamp.png")

def fig15():
    img, d = canvas(1460, 900)
    ox, oy, sc = 110, 330, 0.4
    for gname in ("n", "o", "a"):
        g = bf.G[gname]
        cs = bf.glyph_contours(g, 90, 50, 0)
        xs = [x for c in cs for x,_ in c]
        lsb, rsb = min(xs), g["adv"]-max(xs)
        d.rectangle([(ox)*S,(oy-700*sc-20)*S,(ox+g["adv"]*sc)*S,(oy+20)*S], outline=(150,150,150), width=S)
        d.rectangle([(ox)*S,(oy-700*sc-20)*S,(ox+lsb*sc)*S,(oy+20)*S], fill=(235,235,245))
        d.rectangle([(ox+(g["adv"]-rsb)*sc)*S,(oy-700*sc-20)*S,(ox+g["adv"]*sc)*S,(oy+20)*S], fill=(235,235,245))
        draw_contours(d, cs, ox, oy, sc)
        label(d, ox, oy+34, f"{int(lsb)} | {int(rsb)}")
        ox += g["adv"]*sc + 90
    label(d, 110, 420, "advance boxes and sidebearings: straights carry more air than rounds")
    oy2 = 800
    ox = 110
    for g in ("g","a"):
        draw_contours(d, bf.glyph_contours(bf.G[g], 90, 50, 0), ox, oy2, sc)
        ox += bf.G[g]["adv"]*sc
    label(d, 110, oy2+34, "unkerned")
    hb_render(d, "Regular", "ГА", 700*S, oy2*S, 280*S)
    label(d, 700, oy2+34, "class kern −55")
    save(img, "fig15_fitting.png")

def fig16():
    from PIL import Image as I, ImageDraw as D, ImageFont as F
    img = I.new("RGB", (1460, 560), "white")
    d = D.Draw(img)
    y = 40
    for size in (64, 44, 32, 24, 18, 13):
        f = F.truetype(os.path.join(FIG, "..", "..", "fonts", "Chuzhditsa-Regular.ttf"), size)
        d.text((50, y), f"{size}  Прекарахме ўӣкенда в Мӱнхен с Һӓри: ўиски и џаз.", font=f, fill="black")
        y += size + 24
    img.save(os.path.join(FIG, "fig16_waterfall.png"))
    print("fig16_waterfall.png")

def fig17():
    img, d = canvas(1460, 420)
    hb_render(d, "Regular", "0123456789", 60*S, 180*S, 110*S)
    hb_render(d, "Regular", "«чуждица» — тире · !?", 60*S, 330*S, 110*S)
    label(d, 60, 360, "figures and punctuation, same vocabulary: rings, lines, dots")
    save(img, "fig17_digits.png")

if __name__ == "__main__":
    pass

def fig18():
    from PIL import Image as I, ImageDraw as D, ImageFont as F, ImageOps
    pairs = "еє  зҙ  сҫ  кқ  хҳһ  ийў  ѫю  ѧя"
    lbl = F.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    rows = []
    for px, mag in ((48, 1), (18, 3), (12, 4)):
        f = F.truetype(os.path.join(FIG, "..", "..", "fonts", "Chuzhditsa-Regular.ttf"), px)
        canvas_row = I.new("L", (int(px*30), int(px*2.2)), 255)
        D.Draw(canvas_row).text((2, 2), pairs, font=f, fill=0)
        bbox = ImageOps.invert(canvas_row).getbbox()
        canvas_row = canvas_row.crop(bbox)
        canvas_row = canvas_row.resize((canvas_row.width*mag, canvas_row.height*mag), I.NEAREST)
        rows.append((px, mag, canvas_row))
    W = max(r.width for _, _, r in rows) + 190
    H = sum(r.height for _, _, r in rows) + 40*len(rows) + 30
    img = I.new("RGB", (W, H), "white")
    d = D.Draw(img)
    y = 20
    for px, mag, r in rows:
        img.paste(r.convert("RGB"), (170, y))
        tag = f"{px} px" + (f"  (x{mag})" if mag > 1 else "")
        d.text((16, y + r.height//2 - 14), tag, font=lbl, fill=(90,90,90))
        y += r.height + 40
    img.save(os.path.join(FIG, "fig18_confusables.png"))
    print("fig18_confusables.png")

if __name__ == "__main__":
    for f in (fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18):
        f()
