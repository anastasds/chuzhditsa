#!/usr/bin/env python3
"""Render docs/hero.png and docs/hero-dark.png for the README."""
import os
from PIL import Image, ImageDraw
from proof import render

HERE = os.path.dirname(__file__)
DOCS = os.path.join(HERE, "..", "docs")
os.makedirs(DOCS, exist_ok=True)
S = 2

def hero(fill, name):
    img = Image.new("RGBA", (1520*S, 430*S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    clear = (0, 0, 0, 0)
    render(d, "Regular", "чуждица", 60*S, 195*S, 190*S, fill=fill, holefill=clear)
    render(d, "Regular", "ўӣкенд · ҫӓңкс · т̢ʰӣк · Муҳаммад · крўаса̨ · бѩ", 62*S, 330*S, 44*S, fill=fill, holefill=clear)
    render(d, "Italic", "думи от чужбина, писани на чуждица", 62*S, 405*S, 40*S, fill=fill, holefill=clear)
    img = img.resize((1520, 430), Image.LANCZOS)
    img.save(os.path.join(DOCS, name))
    print(name)

hero("black", "hero.png")
hero("white", "hero-dark.png")
