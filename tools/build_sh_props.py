#!/usr/bin/env python3
"""build_sh_props.py: the Söder cafe parasol and table (8 Nov props pilot, family sh_props_08nov), BUILT by rule.

  python3 -I tools/build_sh_props.py        -> riverwalk/levelart/soder/props/parasol.png (66 x 43), table.png (50 x 26)

Why built: the pilot failed twice on geometry. GPT 2.5 on the blockout (sh_cafe_table, 64 credits) drew the parasol
1.65x and 1.8x too wide and domed; Pixel Engine Image at exact size (sh_parasol, sh_table, 24 credits) domed the canopy
again and drew the table top 12 rows thick, seen from above. The PARASOL box is a flat 64 px platform (Pepper stands on
y 108) and the TABLE box a 7 px ledge with 19 px to crawl under, so both are flat geometry: drawn here on the boxes.
The curly iron legs were first taken from Pixel Engine table a (1x); at 4x beside the bench they read thin and
gappy, so they are hand-placed here too (a centre line per leg, mirrored, 1 px strokes with ink round them). The
three renders are kept as the design and colour references (docs/review/08nov/props/cafe_table/raw). Colours: the concept's canopy red and cream (sampled from
art/gen/concepts/sh_cafe_concept_a.png), its walnut table top, Söder's ink and iron (soder/palette.lua).
Light from the right (rules.json, Söder: low sun from the right)."""
import json, os
import numpy as np
from PIL import Image

def hx(s): return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)
INK, IRON, IRON_LIT = hx('1c1718'), hx('3a3232'), hx('6c625e')          # soder/palette.lua ink, iron, iron_lit
RED = {'lit': hx('d8604c'), 'base': hx('c04840'), 'shade': hx('983430'), 'deep': hx('74282a')}
CREAM = {'lit': hx('fbf0cc'), 'base': hx('ecdca4'), 'shade': hx('cfb98a'), 'deep': hx('a8936a')}
WOOD = {'lit': hx('8e5440'), 'base': hx('683a2e'), 'shade': hx('512c24'), 'deep': hx('3c2020')}
T = (0, 0, 0, 0)


def parasol():
    W, H = 66, 43
    a = np.zeros((H, W, 4), np.uint8)
    def put(y, x, c): a[y, x] = c
    for x in range(1, 65): put(0, x, INK)                                  # the flat top: Pepper's platform, y 107
    # 8 panels, red and cream. On the canopy (rows 1-9) the seams fan out from the pole like a parasol's ribs: seam k
    # sits at c + (x_k - c) * f(y), f from 0.84 at the top to 1 at the hem (straight lines, even steps); the hem
    # (row 10, a dark band) and the scalloped valance (rows 11-13) keep the 8 px panels.
    c = 32.5
    xs = [1 + 8 * k for k in range(9)]
    def look(i):
        R = RED if i % 2 == 0 else CREAM
        # light from the right: the two left panels a shade darker, the two right ones a shade lighter
        return R, (R['shade'] if i < 2 else (R['lit'] if i >= 6 else R['base'])), (R['base'] if i < 2 else R['lit'])
    for y in range(1, 10):
        f = 0.84 + 0.16 * (y - 1) / 8
        b = [c + (x - c) * f for x in xs]
        for x in range(1, 65):
            i = max(0, min(7, sum(1 for k in range(1, 8) if x + 0.5 >= b[k])))
            R, body, top = look(i)
            put(y, x, top if y == 1 else body)
    for i in range(8):
        p = xs[i]; R, body, top = look(i)
        for x in range(p, p + 8):
            put(10, x, R['deep'] if i < 2 else R['shade'])                # the hem
            put(11, x, body)
        for x in range(p + 1, p + 7): put(12, x, R['shade'] if i < 2 else body)   # the scallop, round at the bottom
        put(12, p, INK); put(12, p + 7, INK)
        for x in range(p + 1, p + 7): put(13, x, INK)
    for y in range(1, 12): put(y, 0, INK); put(y, 65, INK)
    for y in range(11, 43):                                                # the pole, down to the table top
        put(y, 31, INK); put(y, 32, IRON); put(y, 33, IRON_LIT); put(y, 34, INK)
    for x, c in zip(range(30, 36), (INK, IRON, IRON, IRON_LIT, IRON, INK)): put(14, x, c)     # a collar under
    for x, c in zip(range(30, 36), (INK, INK, IRON, IRON_LIT, INK, INK)): put(15, x, c)      # the canopy
    return a


def line(p0, p1):
    """the pixels of a straight line (Bresenham): even steps, no doubled corners"""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = abs(x1 - x0), -abs(y1 - y0); sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
    err, out = dx + dy, []
    while True:
        out.append((x0, y0))
        if (x0, y0) == (x1, y1): return out
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy


# the left leg's centre line, hand-placed (x, y): out of the column's knob, a long S down to the street, a scroll
# turning out and up at the foot; the right leg is its mirror (x -> 49 - x). Rows 8-25 = y 158-175.
LEG = [(22, 15), (19, 16), (16, 18), (14, 20), (13, 22), (12, 23), (11, 24), (9, 24), (8, 23), (8, 22)]


def table():
    W, H = 50, 26
    a = np.zeros((H, W, 4), np.uint8)
    def put(y, x, c): a[y, x] = c
    # the top: a walnut slab seen side-on, on the TABLE box (cols 1-48 = x 2700-2747, rows 0-6 = y 150-156)
    for x in range(1, 49): put(0, x, INK); put(7, x, INK)
    for y in range(1, 7): put(y, 0, INK); put(y, 49, INK)
    for x in range(1, 49):
        put(1, x, WOOD['lit'])
        for y in (2, 3, 4): put(y, x, WOOD['base'])
        put(5, x, WOOD['shade']); put(6, x, WOOD['deep'])           # the thick rim, turning under
    for x in range(43, 49): put(2, x, WOOD['lit'])                  # the low sun on the right end
    for x in list(range(4, 19)) + list(range(27, 40)): put(3, x, WOOD['shade'])   # two long grain lines
    # the iron base, hand-placed: a column down to the street with a knob, two curly legs (iron on the left, lit on
    # the right: the sun is on the right), each stroke 1 px with ink round it
    stroke = np.zeros((H, W), bool); fillc = {}
    for x0 in (24, 25):
        for y in range(8, 25): stroke[y, x0] = True; fillc[(y, x0)] = IRON if x0 == 24 else IRON_LIT
    for y in (14, 15):
        for x in (23, 26): stroke[y, x] = True; fillc[(y, x)] = IRON if x == 23 else IRON_LIT
    for i in range(len(LEG) - 1):
        for (x, y) in line(LEG[i], LEG[i + 1]):
            for xx, c in ((x, IRON), (49 - x, IRON_LIT)):
                stroke[y, xx] = True; fillc[(y, xx)] = c
    for (y, x), c in fillc.items(): put(y, x, c)
    for y in range(8, H):
        for x in range(W):
            if a[y, x, 3]: continue
            near = any(0 <= y + dy < H and 0 <= x + dx < W and stroke[y + dy, x + dx]
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if near: put(y, x, INK)
    return a


if __name__ == '__main__':
    os.makedirs('riverwalk/levelart/soder/props', exist_ok=True)
    for name, f, out in (('sh_parasol', parasol, 'parasol'), ('sh_table', table, 'table')):
        a = f()
        Image.fromarray(a).save(f'riverwalk/levelart/soder/props/{out}.png')
        Image.fromarray(a).save(f'art/source/{name}/{name}.png')
        n = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
        print(out, a.shape[1], 'x', a.shape[0], n, 'colours')
