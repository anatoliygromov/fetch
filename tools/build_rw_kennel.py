#!/usr/bin/env python3
"""build_rw_kennel.py: Pepper's kennel by her house (River Walk x 0), BUILT by rule at true scale (night of 6 Nov 2026).

  python3 -I tools/build_rw_kennel.py           write riverwalk/art/scene/kennel.png (+ art/source/kennel/kennel.aseprite)
  python3 -I tools/build_rw_kennel.py --check   fail if the file on disk is not what this script builds

Why (base audit 6 Nov): the 34 x 36 kennel with a flat dark top read as a red post box. A Labrador's kennel is about
0.95 m wide and tall: 44 x 44 px at 46 px/m. Seen front-on (BIBLE: the gable end, no sides or tops):
  * a pitched roof of dark slate shingles: eaves 1 px over the walls at row 18, the slopes rising 1 px in 1 to a
    ridge cap 12 px wide (rows 0-2; Pepper can stand on it: the KENNEL box x 16-28), shingle courses every 4 rows
    in running bond, the lit edge along the top of each slope (sun upper left: the left slope lighter);
  * a fascia board along the eaves (row 18-19): the KENNEL EAVES box x 0-44, y 158 (she can stand on it);
  * red plank walls, 4 px courses (lit top row, two mid rows, a dark lap), the left corner post lit;
  * an arched doorway on the right (opening cols 16-36, 21 px), its crown on row 25 (world y 165: 19 px to crawl
    under), straight jambs, a cream frame, a dark inside with the arch's inner shadow;
  * one 1 px ink outline round the whole (an obstacle), the kennel's own ink #12121a.
Art row 0 = world y 140, the bottom row 43 = y 183 (the pavement's line is y 184). Drawn by setpieces.lua kennel()."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

hexc = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255], np.uint8)
INK = hexc('#12121a')
SLATE_L, SLATE, SLATE_D = hexc('#7e8086'), hexc('#565864'), hexc('#393847')     # roof (riverwalk.gpl greys)
RED_L, RED, RED_D = hexc('#da4640'), hexc('#ce3531'), hexc('#a42c30')             # wall planks
LAP = hexc('#7d1c24')
CREAM, CREAM_D = hexc('#f1dbbb'), hexc('#d3c3b4')                                 # door frame, plaque
IN_D, IN = hexc('#1c1c1c'), hexc('#2b2a25')                                       # the inside
W, H = 44, 44
EAVE, DOOR_X0, DOOR_X1, CROWN = 18, 15, 37, 25


def build():
    a = np.zeros((H, W, 4), np.uint8)
    inside = np.zeros((H, W), bool)
    # the roof: a trapezoid from the eaves (row 18, cols 0-43) up to the ridge cap (row 0, cols 16-27)
    for r in range(0, EAVE + 1):
        half = 6 + r                                                  # 1 in 1 slopes from a 12 px ridge
        x0, x1 = max(0, 22 - half), min(W - 1, 21 + half)
        for x in range(x0, x1 + 1):
            inside[r, x] = True
            if r <= 2: c = SLATE_L if r == 1 else SLATE              # the ridge cap
            else:
                course = (r - 3) // 4; k = (r - 3) % 4
                c = SLATE_D if k == 3 else (SLATE_L if k == 0 and x < 22 else SLATE)
                if k in (1, 2) and (x + 4 * (course % 2)) % 8 == 0: c = SLATE_D   # shingle joints, running bond
            if x == x0 + 1 and r > 2: c = SLATE_L if x < 22 else SLATE_D          # the slope's lit / shaded edge
            a[r, x] = c
    # the fascia board under the eaves (rows 18-19)
    for r in (EAVE, EAVE + 1):
        for x in range(0, W):
            inside[r, x] = True; a[r, x] = CREAM if r == EAVE else CREAM_D
    # the walls (rows 20-43, cols 1-42): planks of 4 rows
    for r in range(EAVE + 2, H):
        for x in range(1, W - 1):
            inside[r, x] = True
            k = (r - EAVE - 2) % 4
            a[r, x] = (RED_L, RED, RED, LAP)[k] if x > 2 else RED_L        # the left corner post lit
    # the doorway: straight jambs from the ground up to row 29, then a round arch to the crown (row 25)
    cx = (DOOR_X0 + DOOR_X1) / 2
    ARCH = {CROWN: (21, 31), CROWN + 1: (18, 34), CROWN + 2: (17, 35)}   # the arch's rows, then straight jambs 16-36
    door = np.zeros((H, W), bool)
    for r in range(CROWN, H):
        x0, x1 = ARCH.get(r, (DOOR_X0 + 1, DOOR_X1 - 1))
        door[r, x0:x1 + 1] = True
    for r in range(H):
        for x in range(W):
            if not door[r, x]: continue
            a[r, x] = IN_D if (r > 0 and not door[r - 1, x]) or x == DOOR_X1 or not door[r, min(W - 1, x + 1)] else IN
    for r in range(H):                                                # the cream frame round the opening
        for x in range(W):
            if door[r, x] or not inside[r, x] or r <= EAVE + 1: continue
            if any(0 <= r + dy < H and 0 <= x + dx < W and door[r + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                a[r, x] = CREAM if x < cx else CREAM_D
    # one ink outline: every inside pixel touching the outside
    for r in range(H):
        for x in range(W):
            if not inside[r, x]: continue
            if any(not (0 <= r + dy < H and 0 <= x + dx < W) or not inside[r + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                a[r, x] = INK
    for x in range(W):                                                # the eaves' underside: ink under the overhang
        if inside[EAVE + 1, x] and (x == 0 or x == W - 1): a[EAVE + 1, x] = INK
    # the doorway's opening to the pavement: the ink stops at the door (she crawls in), the bottom row stays inside
    for x in range(DOOR_X0, DOOR_X1 + 1):
        if door[H - 1, x]: a[H - 1, x] = IN
    return a


if __name__ == '__main__':
    out = 'riverwalk/art/scene/kennel.png'
    a = build()
    if '--check' in sys.argv:
        ok = os.path.exists(out) and np.array_equal(np.array(Image.open(out).convert('RGBA')), a)
        print('CHECK PASS' if ok else 'CHECK FAIL: ' + out); sys.exit(0 if ok else 1)
    Image.fromarray(a).save(out)
    os.makedirs('art/source/kennel', exist_ok=True); aseprite_io.write('art/source/kennel/kennel.aseprite', [a])
    print('kennel.png', W, 'x', H, 'colours', len({tuple(p) for p in a.reshape(-1, 4) if p[3]}))
