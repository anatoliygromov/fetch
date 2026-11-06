#!/usr/bin/env python3
"""build_rw_size_sheets.py: the owner's size pick for the River Walk gull and the cat (night of 6 Nov 2026).

Board, 25 Oct 20:16: the gull "has holes and doesn't look like a bird", then "needs to be smaller too"; the cat
"bigger, slightly smaller than the dog". Animals are sized by the owner from a sheet (preflight owner_size), so no
render is asked for tonight. Each sheet: Pepper's real sprite at 1x on the pavement, the animal as the game draws it
now (its own sprite, unchanged, for reference), and grey blockouts at each option, drawn by rule (no pixel of a
rejected sprite is scaled). Labels are in the margin (the sheet is a review picture, not game art).
  gull: wingspan 16, 20, 24 px (now: 22 x 16, gull.png frame 0); a gliding gull, body 0.55 of the span
  cat:  sitting, 24, 27, 30 px tall (now: 20 x 30, cat.png frame 0) and 34 px; Pepper is 38 px to her head top
Writes docs/review/06nov-night/rw/size_sheets/{gull,cat}_sizes_{1x,4x}.png. Run from the repo root."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blockout_lib import pepper

OUT = 'docs/review/06nov-night/rw/size_sheets/'
SKY, PAVE, EDGE, TXT = (196, 214, 232, 255), (226, 206, 170, 255), (180, 160, 128, 255), (40, 40, 48, 255)
BODY, WING, TIP, DARK = (205, 205, 210, 255), (150, 150, 160, 255), (80, 80, 92, 255), (110, 110, 120, 255)
GROUND = 70


def font(s):
    try: return ImageFont.load_default(size=s)
    except TypeError: return ImageFont.load_default()


def gull(d, cx, cy, span):
    """A gliding gull seen from the side: both wings raised in a shallow V from the body, dark wing tips, a white
    body with a round head on the left, a yellow bill and a short tail on the right. Its height is about 0.5 span."""
    h = span / 2
    lw = [(cx - 2, cy - 1), (cx - h * 0.55, cy - span * 0.30), (cx - h, cy - span * 0.42), (cx - h * 0.62, cy - span * 0.20), (cx - 1, cy + 1)]
    rw = [(cx + 2, cy - 1), (cx + h * 0.55, cy - span * 0.30), (cx + h, cy - span * 0.42), (cx + h * 0.62, cy - span * 0.20), (cx + 1, cy + 1)]
    d.polygon(rw, fill=WING); d.polygon(lw, fill=WING)
    d.polygon([lw[2], (cx - h * 0.78, cy - span * 0.37), (cx - h * 0.80, cy - span * 0.28)], fill=TIP)
    d.polygon([rw[2], (cx + h * 0.78, cy - span * 0.37), (cx + h * 0.80, cy - span * 0.28)], fill=TIP)
    bl = span * 0.5; bh = max(3, round(span * 0.16))
    d.ellipse([cx - bl / 2, cy - bh / 2, cx + bl / 2, cy + bh / 2], fill=BODY)                 # body
    d.polygon([(cx + bl / 2 - 1, cy - 1), (cx + bl / 2 + span * 0.12, cy - 2), (cx + bl / 2 + span * 0.1, cy + 2)], fill=BODY)  # tail
    r = max(2, round(span * 0.09))
    d.ellipse([cx - bl / 2 - r, cy - bh / 2 - r, cx - bl / 2 + r, cy - bh / 2 + r], fill=BODY)  # head
    d.polygon([(cx - bl / 2 - r, cy - bh / 2), (cx - bl / 2 - r - max(2, span * 0.1), cy - bh / 2 + 1), (cx - bl / 2 - r, cy - bh / 2 + 2)], fill=(230, 180, 60, 255))


def cat(d, x0, ground, hgt):
    """A sitting cat seen from the side, facing left: haunch, chest, head with two ears, a tail curled at its feet."""
    k = hgt / 30
    w = round(20 * k)
    d.ellipse([x0 + 4 * k, ground - 18 * k, x0 + w, ground], fill=DARK)                       # haunch
    d.polygon([(x0 + 3 * k, ground), (x0 + 4 * k, ground - 18 * k), (x0 + 10 * k, ground - 20 * k), (x0 + 11 * k, ground)], fill=DARK)   # chest, front legs
    d.ellipse([x0, ground - 28 * k, x0 + 11 * k, ground - 18 * k], fill=DARK)                  # head
    d.polygon([(x0 + 1 * k, ground - 25 * k), (x0 + 2 * k, ground - hgt), (x0 + 5 * k, ground - 27 * k)], fill=DARK)   # ears
    d.polygon([(x0 + 6 * k, ground - 27 * k), (x0 + 9 * k, ground - hgt), (x0 + 10 * k, ground - 24 * k)], fill=DARK)
    d.line([(x0 + w - 1, ground - 2), (x0 + w + 6 * k, ground - 3), (x0 + w + 8 * k, ground - 8 * k)], fill=DARK, width=max(2, round(2 * k)))


def sheet(kind, opts, now):
    W = 70 + sum(o[1] + 26 for o in opts) + now.width + 30
    im = Image.new('RGBA', (W, GROUND + 10), SKY); d = ImageDraw.Draw(im)
    d.rectangle([0, GROUND, W, GROUND + 10], fill=PAVE); d.line([(0, GROUND), (W, GROUND)], fill=EDGE)
    p = pepper(); im.alpha_composite(p, (6, GROUND - p.height))
    x = 6 + p.width + 14
    labels = [(6 + p.width // 2, 'Pepper 38 px')]
    top = GROUND - 50 if kind == 'gull' else None
    im.alpha_composite(now, (x, (GROUND - 46 if kind == 'gull' else GROUND - now.height)))
    labels.append((x + now.width // 2, f'now {now.width}x{now.height}'))
    x += now.width + 16
    for name, size in opts:
        if kind == 'gull': gull(d, x + size / 2, GROUND - 40, size); labels.append((x + size // 2, f'{name}: {size} px span'))
        else: cat(d, x, GROUND, size); labels.append((x + size // 2, f'{name}: {size} px tall'))
        x += size + 26
    return im, labels


def save(kind, im, labels):
    os.makedirs(OUT, exist_ok=True)
    for z in (1, 4):
        big = im.resize((im.width * z, im.height * z), Image.NEAREST)
        out = Image.new('RGBA', (big.width, big.height + 20 * z), (255, 255, 255, 255)); out.alpha_composite(big)
        d = ImageDraw.Draw(out); f = font(7 * z if z > 1 else 8)
        for i, (cx, t) in enumerate(labels):
            tw = d.textlength(t, font=f)
            d.text((max(1, cx * z - tw / 2), big.height + 1 + (i % 2) * 8 * z), t, fill=TXT, font=f)
        out.convert('RGB').save(f'{OUT}{kind}_sizes_{z}x.png')


if __name__ == '__main__':
    g = Image.fromarray(np.array(Image.open('riverwalk/art/gull.png').convert('RGBA'))[:, :26]); g = g.crop(g.getbbox())
    c = Image.fromarray(np.array(Image.open('riverwalk/art/cat.png').convert('RGBA'))[:48, :48]); c = c.crop(c.getbbox())
    save('gull', *sheet('gull', [('A', 16), ('B', 20), ('C', 24)], g))
    save('cat', *sheet('cat', [('A', 24), ('B', 27), ('C', 30), ('D', 34)], c))
    print('wrote', OUT)
