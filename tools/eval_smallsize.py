#!/usr/bin/env python3
"""Instrumented small-size evaluation (typeface paper, Table 2).

Method, exactly as the table caption states: glyphs rendered through
FreeType (PIL) at fixed pixel sizes, ink thresholded at 50%; mark
survival = ink pixels strictly above the base letter's topmost row;
confusable-pair contrast = symmetric difference of ink in pixels;
counter check = the о counter still encloses white not reachable from
the bitmap border. Run against any font file:

    python3 tools/eval_smallsize.py fonts/v3/Chuzhditsa2b-Regular.ttf
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

SIZES = (10, 12, 14, 18, 24)
MARKS = [("ў", "у"), ("ӣ", "и"), ("ӓ", "а")]
PAIRS = [("с", "ҫ"), ("з", "ҙ"), ("к", "қ"), ("е", "є")]


def ink(font, ch, px):
    img = Image.new("L", (px * 4, px * 4), 255)
    ImageDraw.Draw(img).text((px, px), ch, font=font, fill=0)
    w, h = img.size
    return {(x, y) for y in range(h) for x in range(w)
            if img.getpixel((x, y)) < 128}


def mark_survival(font, marked, base, px):
    b, m = ink(font, base, px), ink(font, marked, px)
    if not b:
        return 0
    top = min(y for _, y in b)
    return sum(1 for _, y in m if y < top)


def pair_contrast(font, a, b, px):
    return len(ink(font, a, px) ^ ink(font, b, px))


def counter_open(font, px):
    img = Image.new("L", (px * 4, px * 4), 255)
    ImageDraw.Draw(img).text((px, px), "о", font=font, fill=0)
    img = img.point(lambda v: 255 if v >= 128 else 0)
    w, h = img.size
    # flood the outside white from the border; an open counter leaves
    # unreached white inside the bowl
    seen, stack = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + \
                        [(x, y) for y in range(h) for x in (0, w - 1)]
    stack = [p for p in stack if img.getpixel(p) == 255]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        x, y = p
        for q in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen \
               and img.getpixel(q) == 255:
                stack.append(q)
    inside = sum(1 for y in range(h) for x in range(w)
                 if img.getpixel((x, y)) == 255 and (x, y) not in seen)
    return inside > 0


def evaluate(path):
    print(path)
    hdr = ["px"] + [f"{m}({b})" for m, b in MARKS] + \
          ["/".join(p) for p in PAIRS] + ["о counter"]
    print("  ".join(hdr))
    rows = []
    for px in SIZES:
        f = ImageFont.truetype(path, px)
        row = [px] + [mark_survival(f, m, b, px) for m, b in MARKS] + \
              [pair_contrast(f, a, b, px) for a, b in PAIRS] + \
              ["open" if counter_open(f, px) else "CLOSED"]
        rows.append(row)
        print("  ".join(str(v) for v in row))
    return rows


if __name__ == "__main__":
    paths = sys.argv[1:] or [
        os.path.join(os.path.dirname(__file__), "..", "fonts", "v3", f)
        for f in ("Chuzhditsa2b-Regular.ttf", "Chuzhditsa2b-Bold.ttf")]
    for p in paths:
        evaluate(p)
        print()
