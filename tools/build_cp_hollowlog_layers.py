#!/usr/bin/env python3
"""build_cp_hollowlog_layers.py: City Park's hollow log, lengthened and split into a BACK and a FRONT layer so Pepper
crawls INSIDE it (owner, 7 Nov: "isnt hollow wood suppose to make the dog climb inside? it looks like shes just
crawling on the side"; round 2: the original 3/4 log kept, one open end, long enough to swallow her).

  python3 -I tools/build_cp_hollowlog_layers.py           write riverwalk/art/scene/park_hollowlog_back.png and
                                                          park_hollowlog_front.png (+ .aseprite sources)
  python3 -I tools/build_cp_hollowlog_layers.py --check   fail if the files on disk are not what this script builds

Made from riverwalk/art/scene/park_hollowlog.png (44 x 27, kept as it is), not redrawn: the 3/4 log with its open
left end (the ellipse, the dark inside), the bark body running right and the closed, rounded right end. It is made
30 columns longer (74 x 27, for the 72 px box at x 1553-1625 plus its 1 px ink each side) by inserting bark columns
of its own middle after column 26: the top band (rows 0-7, the lit top under the ink, no moss) from columns 21-26,
the rest (rows 8-26, the grain and the shaded underside) from columns 18-36, each in a different order, forwards and
backwards, so the grain does not repeat at one period. Rows are never moved, so the ink line along the top (row 0,
world y 301), the shell (rows 1-8) and the bottom ink on the path stay as they were. Sits at (x0 - 1, y0 - 1).

FRONT (scene.lua: drawn after Pepper while she crawls inside the log, before her otherwise): the lengthened log with
  only the dark inside of the left ellipse taken out (its dark pixels, flood-filled from the middle of the mouth).
BACK (drawn before Pepper, in the play pass): that dark inside, the same pixels, plus a slightly darker tunnel tone
  behind the bark, where her body is while she is in the log (and where the gold bone, now at x 1589, lies).
Front over back is exactly the lengthened log.
"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

SRC = 'riverwalk/art/scene/park_hollowlog.png'
OUT_BACK = 'riverwalk/art/scene/park_hollowlog_back.png'
OUT_FRONT = 'riverwalk/art/scene/park_hollowlog_front.png'
H = 27
AT = 27                                                        # the new columns go in before the old column 27
TOP = [23, 24, 25, 26, 25, 24, 23, 24, 25, 26, 21, 22, 24, 25, 26, 25, 24, 23, 24, 25,               # rows 0-7: the
       26, 24, 23, 25, 26, 25, 24, 23, 24, 25]                                                  # moss-free lit top
MID = list(range(18, 33)) + list(range(36, 21, -1))                                             # rows 8-26
assert len(TOP) == len(MID) == 30
W = 44 + len(TOP)
TUNNEL = (35, 20, 16)                                          # the tunnel behind the bark: one step under the
DARK = 110                                                     # inside's darkest (50, 29, 22); a "dark" pixel: luma


def lengthen(src):
    out = np.zeros((H, W, 4), np.uint8)
    out[:, :AT] = src[:, :AT]
    out[:, AT + 30:] = src[:, AT:]
    for i in range(30):
        out[:8, AT + i] = src[:8, TOP[i]]
        out[8:, AT + i] = src[8:, MID[i]]
    return out


def inside_mask(img):
    """the dark inside of the left ellipse: dark pixels joined to the middle of the mouth, left of the bark body"""
    lum = img[:, :, :3].astype(float) @ np.array([0.299, 0.587, 0.114])
    m = np.zeros((H, W), bool)
    stack = [(12, 8)]
    while stack:
        y, x = stack.pop()
        if not (0 <= y < H and 0 <= x < 14) or m[y, x] or img[y, x, 3] == 0 or lum[y, x] >= DARK: continue
        m[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return m


def build():
    src = np.array(Image.open(SRC).convert('RGBA'))
    assert src.shape[:2] == (H, 44), src.shape
    log = lengthen(src)
    hand(log)
    hole = inside_mask(log)
    front = log.copy(); front[hole] = 0
    back = np.zeros_like(log)
    back[hole] = log[hole]
    # the tunnel: behind the bark from the mouth to the closed end, as high as the mouth (rows 5-22) and down to the
    # path, inside the log's outline
    rows = np.nonzero(hole.any(1))[0]
    right = max(np.nonzero(hole.any(0))[0])
    for y in range(rows.min(), H - 1):
        for x in range(right + 1, W - 2):
            if log[y, x, 3] and log[y, x - 1, 3] and log[y, x + 1, 3]: back[y, x] = (*TUNNEL, 255)
    return back, front, log


# hand edits after the 6x look (x, y, rgb from the old palette, reason), on the lengthened log
E, G = (238, 167, 79), (111, 68, 53)
HAND = [(x, 2, E, 'asset_qa noise: a lone growth-ring pixel of column 23 or 21 in the lit top, painted with the lit top')
        for x in (27, 33, 37, 38, 44, 49, 54)] + [
    (38, 8, G, 'asset_qa noise: a lone dark grain pixel, painted with the bark round it'),
    (49, 8, G, 'asset_qa noise: the same'),
] + [(x, 20, G, 'asset_qa blotch: a 3 px streak cut short by the insert, painted with the bark round it') for x in (42, 43, 44)]
# review round 1 (7 Nov): columns 36-51 of the insert mirror round x 43.5 (a butterfly of dark strokes at rows 8-9 and
# 13-16). Broken on the right half: the row 8 stroke cut to a dash, and a knot in the bark at x 44-47, rows 12-16
J, K, INK, C = (213, 139, 61), (82, 51, 42), (28, 12, 19), (161, 95, 51)
HAND += [(x, 8, J, 'review: the mirrored row 8 stroke cut to a dash (the lit grain of the row)') for x in (49, 50, 51)]
HAND += [(x, y, c, 'review: a knot at x 44-47 to break the mirror') for x, y, c in (
    (45, 12, G), (46, 12, G),
    (44, 13, G), (45, 13, K), (46, 13, K), (47, 13, G),
    (44, 14, K), (45, 14, INK), (46, 14, INK), (47, 14, K),
    (44, 15, G), (45, 15, K), (46, 15, K), (47, 15, G),
    (45, 16, C), (46, 16, C))]


def hand(img):
    for x, y, rgb, why in HAND:
        img[y, x] = (*rgb, 255)


def main():
    back, front, log = build()
    if '--check' in sys.argv:
        ok = True
        for path, a in ((OUT_BACK, back), (OUT_FRONT, front)):
            if not os.path.exists(path) or not np.array_equal(np.array(Image.open(path).convert('RGBA')), a):
                print('DIFFERS', path); ok = False
        print('OK' if ok else 'FAIL'); sys.exit(0 if ok else 1)
    Image.fromarray(back).save(OUT_BACK)
    Image.fromarray(front).save(OUT_FRONT)
    os.makedirs('art/source/park_hollowlog', exist_ok=True)
    aseprite_io.write('art/source/park_hollowlog/park_hollowlog_back.aseprite', [back], layer='back')
    aseprite_io.write('art/source/park_hollowlog/park_hollowlog_front.aseprite', [front], layer='front')
    print('wrote', OUT_BACK, OUT_FRONT, f'{W} x {H}')


if __name__ == '__main__':
    main()
