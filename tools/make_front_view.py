#!/usr/bin/env python3
"""Front-on versions of two River Walk obstacles whose art was drawn from above (branch lk/look).

The scene is seen from the front, at about Pepper's height: the bench, the bin and the square planter show only
their front, with a thin cap on top. Two SpriteCook props did not match:
  flowerbox: the box's top rim was drawn as a trapezoid seen from above, with the soil inside showing.
             -> the slanted rim and the soil are removed; the flowers grow out of a bed of leaves that sits
                behind the rim's straight front edge (rows 17-24 are kept, so the top Pepper stands on, y 152,
                is unchanged). Same 104 x 49 size.
  gritbox:   drawn three-quarter: the sloped lid's top and the box's left side were visible.
             -> only the front face is kept: the lid becomes a thin band (a few of its own rows, as a slope seen
                almost edge-on), the side face is dropped, and plain plank columns are repeated so the box keeps its
                88 px width (collision 86 wide). It is 32 rows high, so its top is the collision top (y 152).
                The SAND lettering stays centred.
Only pixels of the art itself are moved or repeated, plus the leaf bed and outline in the art's own colours.
Writes art/scene/flowerbox_front.png and art/scene/gritbox_front.png; the originals are untouched.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', 'riverwalk', 'art', 'scene')
CLEAR = (0, 0, 0, 0)


def load(n):
    return Image.open(os.path.join(ART, n)).convert('RGBA')


def flowerbox():
    im = load('flowerbox.png')
    w, h = im.size
    px = im.load()
    OUT = (1, 0, 1, 255)
    wood = {(191, 109, 54, 255), (149, 79, 46, 255), (212, 131, 75, 255), (90, 46, 42, 255)}
    soil = {(44, 46, 53, 255)}
    leaves = [(45, 70, 54, 255), (73, 110, 57, 255), (107, 152, 64, 255)]   # the art's own greens, dark to light
    plant = set(leaves) | {(148, 37, 34, 255), (220, 60, 49, 255), (242, 248, 232, 255), (168, 170, 153, 255),
                           (89, 57, 119, 255), (163, 93, 197, 255), (246, 186, 120, 255)}
    TOP = 17                                                       # the rim's front edge starts here (kept)
    out = Image.new('RGBA', (w, h), CLEAR)
    o = out.load()
    for y in range(TOP, h):
        for x in range(w):
            o[x, y] = px[x, y]

    def near_plant(x, y):
        return any(0 <= x + dx < w and 0 <= y + dy < TOP and px[x + dx, y + dy] in plant
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    for y in range(TOP):
        for x in range(w):
            c = px[x, y]
            if c in plant or (c == OUT and near_plant(x, y)):
                o[x, y] = c                                        # flowers, leaves and their outlines
    # the leaf bed: rows 12-16 between the box's corners, where rim wood or soil showed, now leaves (a 2 x 2
    # pattern of the art's greens, darker low down), so the plants sit on the rim instead of floating
    plantcols = {x for x in range(w) for y in range(TOP) if px[x, y] in plant}
    for y in range(12, TOP):
        inset = 6 + max(0, 14 - y)                                 # the bed's ends are rounded
        for x in range(inset, w - inset):
            near = any(c in plantcols for c in range(x - 2, x + 3))
            if y < 14 and not (near and (x // 3 + y) % 2 == 0): continue   # a leafy, uneven top edge
            if o[x, y][3] == 0:
                k = (x + y) % 2
                o[x, y] = leaves[0] if y >= 15 else (leaves[k] if y >= 13 else leaves[1 + k])
    # a 1 px outline around the plants' new silhouette (outside it), as on every obstacle
    # (only next to coloured pixels: where the art already has its outline, it is not doubled)
    colour = lambda x, y: 0 <= x < w and 0 <= y < h and o[x, y][3] > 0 and o[x, y] != OUT
    ring = [(x, y) for y in range(TOP) for x in range(w)
            if o[x, y][3] == 0 and any(colour(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in ring:
        o[x, y] = OUT
    out.save(os.path.join(ART, 'flowerbox_front.png'))
    return out


def gritbox():
    im = load('gritbox.png')
    w, h = im.size
    px = im.load()
    OUT = (0, 1, 0, 255)
    X0, X1 = 21, 87                                                # the front face, posts included
    cols = list(range(X0, X1 + 1))
    extra = 88 - len(cols)                                         # widen to the old footprint
    a, b = extra // 2, extra - extra // 2
    cols = cols[:35 - X0] + [35] * a + cols[35 - X0:72 - X0] + [72] * b + cols[72 - X0:]  # plain plank columns
    # rows: outline, the sloped lid seen almost edge-on (a few of its own rows: highlight, surface, front edge),
    # then the front face (18-39). 32 rows in all, so the top is the collision top (y 152) and nothing of the
    # box rises above it any more.
    rows = [None, 6, 8, 10, 12, 14, 15, 16, 17] + list(range(18, 40))
    rows = rows[:9 + 35 - 18] + [35] * (32 - len(rows)) + rows[9 + 35 - 18:]
    out = Image.new('RGBA', (len(cols), len(rows)), CLEAR)
    o = out.load()
    for j, y in enumerate(rows):
        for i, x in enumerate(cols):
            o[i, j] = OUT if y is None else px[x, y]
    W = len(cols)
    for j, y in enumerate(rows):                                   # the lid band: each row in its own colour (taken
        if y is not None and y <= 17:                              # mid-lid), straight across, outlined at both ends
            c = px[50, y]
            for i in range(1, W - 1): o[i, j] = c
            o[0, j] = OUT; o[W - 1, j] = OUT
    out.save(os.path.join(ART, 'gritbox_front.png'))
    return out


if __name__ == '__main__':
    f, g = flowerbox(), gritbox()
    print('flowerbox_front', f.size, 'gritbox_front', g.size)
