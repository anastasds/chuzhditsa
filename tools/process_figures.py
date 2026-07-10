#!/usr/bin/env python3
"""Figures for the process paper (paper/process.tex).

fig_p1: the repository's one-day commit timeline, annotated with release
tags and the critique episodes that drove each phase. Data is read from
`git log` at run time so the figure cannot drift from the history it
depicts (the same no-parallel-paths rule the typeface paper's Figure 6
taught us).
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "paper", "figures")

def font(size, bold=False):
    cands = (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else
             ["/System/Library/Fonts/Supplemental/Arial.ttf"])
    for c in cands:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            pass
    return ImageFont.load_default()

def commits():
    out = subprocess.run(
        ["git", "-C", REPO, "log", "--reverse", "--format=%ad|%h|%s",
         "--date=format:%H:%M"], capture_output=True, text=True).stdout
    rows = []
    for line in out.strip().splitlines():
        t, h, s = line.split("|", 2)
        hh, mm = map(int, t.split(":"))
        rows.append((hh + mm / 60, h, s))
    return rows

# critique episodes: (hour placed at the commit that answered them, label)
EPISODES = [
    (14.38, "“curves that don’t\nmeet properly”"),
    (15.38, "“3 missing half of itself\n… heights jarring …\nkerning absolutely terrible”"),
    (16.53, "“check for mathematical\nand visual correctness”"),
    (17.60, "“rethink your approach\n… make it sound”"),
    (19.45, "“the B shapes are clearly\ndifferent — the model\nis obviously incorrect”"),
    (20.02, "“a typeface paper that\ncan’t make a typeface —\nconsult open typefaces”"),
    (20.28, "“now look at existing\nfonts to learn\nhow to kern”"),
]
TAGS = {"83dc417": ("v2.4", 0), "593407c": ("v2.5", 0),
        "3305e14": ("v2.3", 0), "80a7ed5": ("v2", 0),
        "b305f0d": ("reference\nreconstruction", -130),
        "f77ef68": ("reference\nkerning", 95)}
PHASES = [(0.0, 1.5, "system, docs,\nkeyboard scaffold"),
          (7.5, 13.0, "papers + four\nreview rounds"),
          (14.0, 21.0, "criticism-driven\nrepair loop")]

W, H = 2200, 760
AX_Y = 470
X0, X1 = 110, W - 60
T0, T1 = -0.6, 21.4

def x(hour):
    return X0 + (hour - T0) / (T1 - T0) * (X1 - X0)

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
f_tick, f_lab, f_ep, f_tag = font(26), font(28), font(25), font(27, True)

# phase bands
for a, b, lab in PHASES:
    d.rectangle([x(a), AX_Y - 46, x(b), AX_Y + 46], fill=(243, 243, 243))
    d.text(((x(a) + x(b)) / 2, AX_Y + 100), lab, font=f_lab,
           fill=(90, 90, 90), anchor="ma", align="center")

# axis
d.line([X0, AX_Y, X1, AX_Y], fill="black", width=3)
for hh in range(0, 22, 3):
    d.line([x(hh), AX_Y - 8, x(hh), AX_Y + 8], fill="black", width=3)
    d.text((x(hh), AX_Y + 16), f"{hh:02d}:00", font=f_tick,
           fill="black", anchor="ma")
d.text(((X0 + X1) / 2, H - 40), "8 July 2026 (repository time)",
       font=f_lab, fill="black", anchor="ma")

# commits
rows = commits()
for hour, h, s in rows:
    d.ellipse([x(hour) - 7, AX_Y - 7, x(hour) + 7, AX_Y + 7],
              fill="black")
    if h in TAGS:
        lab, dx = TAGS[h]
        d.line([x(hour), AX_Y - 12, x(hour), AX_Y - 52], fill="black", width=2)
        d.text((x(hour) + dx, AX_Y - 58), lab, font=f_tag, fill="black",
               anchor="md", align="center")

# critique callouts in fixed slots across the top, elbow connectors down
n = len(EPISODES)
slot_w = (X1 - X0 - 120) / (n - 1)
for i, (hour, lab) in enumerate(EPISODES):
    sx = X0 + 60 + i * slot_w
    d.text((sx, 30), lab, font=f_ep, fill=(60, 60, 60),
           anchor="ma", align="center")
    lines = lab.count("\n") + 1
    top = 30 + lines * 31 + 10
    d.line([sx, top, sx, 220], fill=(160, 160, 160), width=2)
    d.line([sx, 220, x(hour), AX_Y - 130], fill=(160, 160, 160), width=2)
    d.line([x(hour), AX_Y - 130, x(hour), AX_Y - 14], fill=(160, 160, 160), width=2)

d.text((X1, H - 40), f"{len(rows)} commits", font=f_lab, fill="black", anchor="ra")

os.makedirs(OUT, exist_ok=True)
img.save(os.path.join(OUT, "fig_p1_timeline.png"))
print("fig_p1_timeline.png", img.size, f"{len(rows)} commits")
