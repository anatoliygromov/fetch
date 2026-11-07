#!/usr/bin/env python3
"""build_cp_hollowlog_layers.py: City Park's hollow log split into a BACK and a FRONT layer so Pepper crawls INSIDE it
(owner, 7 Nov: "isnt hollow wood suppose to make the dog climb inside? it looks like shes just crawling on the side").

  python3 -I tools/build_cp_hollowlog_layers.py           write riverwalk/art/scene/park_hollowlog_back.png and
                                                          park_hollowlog_front.png (+ .aseprite sources)
  python3 -I tools/build_cp_hollowlog_layers.py --check   fail if the files on disk are not what this script builds

Made from riverwalk/art/scene/park_hollowlog.png (44 x 27, kept as it is): its palette, its ink and its bark (the lit
top, the moss, the horizontal grain and the shaded underside of the trunk) are reused pixel for pixel; the two cut
ends are drawn here by rule, no credits. Both layers are 44 x 27 and sit where the old file sat (x0 - 1, y0 - 1):
row 0 is the ink above the shell (world y 301 in the tall City Park), rows 1-8 the solid shell (y 302-309), rows
8-26 the crawl gap (19 px), the path is the row under the file. Collision is the map's, unchanged.

FRONT (scene.lua: drawn after Pepper while she is inside the log, before her otherwise): the near bark wall and the
  top shell, and the two cut ends, each a ring round a mouth: the ink, a 1 px bark edge, light end grain with a
  growth ring where the ring is wide enough, a dark lip. The mouths are round, their foot cut by the path: open from
  row 6 (world y 307) down to the path, 9 px wide in the middle, so her crawl box (19 px under the shell) fits. They
  are holes in this layer: inside the log she shows there and nowhere else. The far (right) end is a step darker,
  away from the light.
BACK (drawn before Pepper, in the play pass): the hollow inside, a deep warm dark: darkest behind the near wall (where
  the gold bone at x 1585 lies), a step lighter in each mouth, lighter again at each mouth's outer side and on its
  floor, so the tube reads; the far inner wall's grain as two lines behind the near wall.
"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

SRC = 'riverwalk/art/scene/park_hollowlog.png'
OUT_BACK = 'riverwalk/art/scene/park_hollowlog_back.png'
OUT_FRONT = 'riverwalk/art/scene/park_hollowlog_front.png'
W, H = 44, 27

# the old file's palette, all kept; the inside adds one darker step of its own warm dark (D0)
P = {'a': (28, 12, 19), 'b': (240, 179, 95), 'c': (161, 95, 51), 'd': (153, 147, 47), 'e': (238, 167, 79),
     'f': (134, 78, 54), 'g': (111, 68, 53), 'h': (50, 29, 22), 'i': (190, 118, 56), 'j': (213, 139, 61),
     'k': (82, 51, 42)}
D0 = (35, 20, 16)          # the inside, deepest (behind the near wall)
D1 = P['h']                # the inside seen through a mouth
D2 = P['k']                # the inside at a mouth's outer side and on its floor
SHADE = {'b': 'e', 'e': 'j', 'j': 'i', 'f': 'g'}      # the far end, a step darker

FW = 17                    # a cut end's width (cols 0-16 on the left, 27-43 on the right, mirrored)
N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def ell(cx, cy, rx, ry, grow, n=2.0):
    """an ellipse (n = 2) or a fuller, rounder-shouldered one (n > 2)"""
    m = np.zeros((H, FW), bool)
    for y in range(H):
        v = 1 - abs((y - cy) / ry) ** n
        if v < 0: continue
        hw = rx * v ** (1 / n) + grow
        for x in range(FW):
            if abs(x - cx) <= hw: m[y, x] = True
    return m


FACE = ell(8, 15, 8.4, 15.4, 0.2)          # the end: round, sitting on the path
HOLE = ell(8, 17.5, 4.4, 11.6, 0.35, 2.6)  # the mouth: round, its foot cut by the path (rows 6-26)


def end_letters():
    """the left cut end as letters ('.' not the end, 'O' the mouth). Rings by where a pixel lies between the mouth's
    ellipse and the end's: the lip, end grain, a growth ring, end grain, the bark edge; the ink comes after"""
    g = np.full((H, FW), '.', dtype='<U1')
    for y in range(H):
        for x in range(FW):
            if not FACE[y, x]: continue
            if HOLE[y, x]: g[y, x] = 'O'; continue
            rh = np.hypot((x - 8) / 4.75, (y - 17.5) / 11.95)              # 1 on the mouth's edge
            rf = np.hypot((x - 8) / 8.6, (y - 15) / 15.6)                   # 1 on the end's edge
            t = (rh - 1) / max(1e-6, (rh - 1) + (1 - rf))
            if any(0 <= y + dy < H and 0 <= x + dx < FW and HOLE[y + dy, x + dx] for dy, dx in N4): g[y, x] = 'k'
            elif t < 0.5: g[y, x] = 'b'
            elif t < 0.66: g[y, x] = 'j'
            elif t < 0.82: g[y, x] = 'b'
            else: g[y, x] = 'f'
    for y in range(H):                                                     # end grain next to the lip is always light
        for x in range(FW):
            if g[y, x] in 'jf' and any(0 <= y + dy < H and 0 <= x + dx < FW and g[y + dy, x + dx] == 'k' for dy, dx in N4):
                g[y, x] = 'b'
    return g


def build():
    src = np.array(Image.open(SRC).convert('RGBA'))
    assert src.shape[:2] == (H, W), src.shape
    end = end_letters()
    sil = np.zeros((H, W), bool); hole = np.zeros((H, W), bool); face = np.zeros((H, W), bool)
    for x in range(FW):
        for xx in (x, W - 1 - x):
            face[:, xx] |= FACE[:, x]; hole[:, xx] |= HOLE[:, x]
    sil |= face; sil[:, 8:W - 8] = True

    front = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if not sil[y, x] or hole[y, x]: continue
            if face[y, x]:
                if x < FW: front[y, x] = (*P[end[y, x]], 255)
                else: ch = end[y, W - 1 - x]; front[y, x] = (*P[SHADE.get(ch, ch)], 255)
            else:
                front[y, x] = src[y, x]                                    # the old file's bark, where it was
    # the ink: round the whole log, the bottom row too (it lies on the path); then a 1 px bark edge inside the ink
    out = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if sil[y, x] and not hole[y, x]:
                if any(not (0 <= y + dy < H and 0 <= x + dx < W) or not sil[y + dy, x + dx] for dy, dx in N4):
                    out[y, x] = True
    front[out] = (*P['a'], 255)
    for y in range(H):
        for x in range(W):
            if face[y, x] and not hole[y, x] and not out[y, x] and tuple(front[y, x, :3]) not in (P['k'],):
                if any(0 <= y + dy < H and 0 <= x + dx < W and out[y + dy, x + dx] for dy, dx in N4):
                    front[y, x] = (*P['f' if x < FW else 'g'], 255)
    hand(front)

    # BACK: the inside, behind both mouths and the near wall between them
    inside = hole.copy()
    inside[7:, 4:W - 4] = True
    inside &= sil
    back = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if not inside[y, x]: continue
            c = D0
            if hole[y, x]:
                c = D1
                outer = x <= 5 or x >= W - 6                                   # the outer side of each mouth
                if outer or y >= 24: c = D2
                elif y <= 9: c = D0                                             # the crown of the mouth in shade
            elif y >= 24: c = D1                                                # the floor behind the near wall
            back[y, x] = (*c, 255)
    for y, x0, x1 in ((14, 14, 29), (19, 16, 27)):                             # the far inner wall's grain
        for x in range(x0, x1 + 1):
            if inside[y, x] and not hole[y, x]: back[y, x] = (*D1, 255)
    return back, front


# hand edits after the 6x look: (x, y, letter or None for clear, reason)
HAND = [
]


def hand(front):
    for x, y, ch, why in HAND:
        front[y, x] = 0 if ch is None else (*P[ch], 255)


def main():
    back, front = build()
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
    print('wrote', OUT_BACK, OUT_FRONT)


if __name__ == '__main__':
    main()
