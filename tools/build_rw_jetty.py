#!/usr/bin/env python3
"""build_rw_jetty.py: the River Walk jetty between the rowing boats (x 2496-2544, deck y 196), BUILT by rule
(night of 6 Nov 2026, final review: "it still reads as a table in the water").

  python3 -I tools/build_rw_jetty.py           write riverwalk/art/scene/rw_jetty.png (+ art/source/rw_jetty/rw_jetty.aseprite)
  python3 -I tools/build_rw_jetty.py --check   fail if the file on disk is not what this script builds

What a small landing stage has, front-on, 48 x 51 (row 0 = world y 189, the bottom row = y 239, the screen's foot):
  * the deck (rows 6-14): one ink top row (y 195) under Pepper's feet (y 196), the plank tops' lit edge, the cross
    planks' ends (a joint every 6 px), a shade line, the stringer beam, ink;
  * an iron bollard on the deck's right end (x 39-44, rows 0-5) to moor the boats to;
  * three timber piles (6 px: ink, lit, two mid, shade, ink) from the deck down past the screen, green weed for 3 rows
    at the waterline (y 221-223); the water's tint below y 224 and the ripple are drawn in code (setpieces.lua);
  * X bracing between the middle and the right pile (two 2 px boards), an iron ladder between the left and the
    middle pile, from the deck down into the water (two rails, a rung every 5 px).
One ink, outlined parts (it is an obstacle). Timber and iron from riverwalk.gpl. Drawn by setpieces.lua jetty() with
its bottom row on world y 239."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

hexc = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255], np.uint8)
INK = hexc('#17181f')
T_L, T_M, T_S = hexc('#a87046'), hexc('#805032'), hexc('#583626')               # deck timber
P_L, P_M, P_S = hexc('#7c7870'), hexc('#5e5c4d'), hexc('#44423a')               # pile timber, weathered
I_L, I_M, I_S = hexc('#7b8087'), hexc('#5b5b5b'), hexc('#373737')               # iron
WEED_L, WEED = hexc('#568442'), hexc('#3f6540')
W, H, Y0 = 48, 51, 189
DECK = 195 - Y0                                                                 # the deck's ink top row (6)
PILES = (2, 21, 40)


def build():
    a = np.zeros((H, W, 4), np.uint8)
    def px(x, y, c):
        if 0 <= x < W and 0 <= y < H: a[y, x] = c
    # the piles, from under the deck to the bottom, weed at the waterline
    for x0 in PILES:
        for y in range(DECK + 9, H):
            wy = y + Y0
            cols = (INK, P_L, P_M, P_M, P_S, INK)
            for i, c in enumerate(cols):
                if 221 <= wy <= 223 and 0 < i < 5: c = WEED_L if (i + wy) % 3 == 0 else WEED
                px(x0 + i, y, c)
    # X bracing between the middle and the right pile (rows 17-30), 2 px boards with ink edges
    def board(xa, ya, xb, yb):
        n = max(abs(xb - xa), abs(yb - ya))
        pts = [(round(xa + (xb - xa) * t / n), round(ya + (yb - ya) * t / n)) for t in range(n + 1)]
        for x, y in pts:
            for dy, c in ((-1, INK), (2, INK)):
                if a[y + dy, x, 3] == 0 or tuple(a[y + dy, x]) == tuple(INK): px(x, y + dy, c)
        for x, y in pts: px(x, y, T_M); px(x, y + 1, T_S)
    board(27, 17, 39, 29); board(27, 29, 39, 17)
    # the ladder between the left and the middle pile: two iron rails, a rung every 5 px, into the water
    for y in range(DECK + 9, H):
        for x, c in ((9, INK), (10, I_L), (11, INK), (16, INK), (17, I_M), (18, INK)):
            px(x, y, c)
    for y in range(DECK + 13, H - 1, 5):
        for x in range(11, 17): px(x, y - 1, INK); px(x, y, I_L); px(x, y + 1, INK)   # a rung: ink, lit, ink
        px(11, y, I_L); px(16, y, I_L)
    # the deck (rows 6-14)
    for x in range(W):
        px(x, DECK, INK)
        px(x, DECK + 1, T_L)                                          # the plank tops' lit edge
        for y in (DECK + 2, DECK + 3): px(x, y, T_S if x % 6 == 5 else T_M)   # cross planks' ends, a joint every 6
        px(x, DECK + 4, T_S)
        px(x, DECK + 5, T_L if x % 16 else T_M)                      # the stringer: lit top, bolts every 16 px
        px(x, DECK + 6, T_M); px(x, DECK + 7, T_S)
        px(x, DECK + 8, INK)
    for y in range(DECK, DECK + 9): px(0, y, INK); px(W - 1, y, INK)
    for x in (8, 24, 40): px(x, DECK + 6, I_S)                        # bolt heads in the stringer
    # the iron bollard on the deck's right end (x 39-44): a cap, a waisted neck, a foot plate on the deck
    bol = ['kkkkkk', 'kLLMSk', '.kLSk.', '.kLSk.', 'kLMMSk', 'kkkkkk']
    for j, row in enumerate(bol):
        for i, ch in enumerate(row):
            c = {'k': INK, 'L': I_L, 'M': I_M, 'S': I_S}.get(ch)
            if c is not None: px(39 + i, j, c)
    for x in range(W):                                                # the screen's foot: the piles and the ladder end
        if a[H - 1, x, 3]: a[H - 1, x] = INK                          # on an ink row (under the water's tint)
    return a


if __name__ == '__main__':
    out = 'riverwalk/art/scene/rw_jetty.png'
    a = build()
    if '--check' in sys.argv:
        ok = os.path.exists(out) and np.array_equal(np.array(Image.open(out).convert('RGBA')), a)
        print('CHECK PASS' if ok else 'CHECK FAIL: ' + out); sys.exit(0 if ok else 1)
    Image.fromarray(a).save(out)
    os.makedirs('art/source/rw_jetty', exist_ok=True); aseprite_io.write('art/source/rw_jetty/rw_jetty.aseprite', [a])
    print('rw_jetty.png', W, 'x', H, 'colours', len({tuple(p) for p in a.reshape(-1, 4) if p[3]}))
