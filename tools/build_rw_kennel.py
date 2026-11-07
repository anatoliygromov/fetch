#!/usr/bin/env python3
"""build_rw_kennel.py: Pepper's kennel in her front garden (River Walk x 0), BUILT by rule at true scale.

  python3 -I tools/build_rw_kennel.py           write riverwalk/art/scene/kennel.png (+ art/source/kennel/kennel.aseprite)
  python3 -I tools/build_rw_kennel.py --check   fail if the file on disk is not what this script builds

History: 6 Nov night, a 44 x 44 side-on kennel (slate roof as a trapezoid, door on the right). Owner, 7 Nov board:
"Kennel like this would never be on the street" and "Why is the dog house look so weird?". Day of 7 Nov
(day/07nov-ground): a classic, cute dog house seen from its gable end, and it stands on the lawn of Pepper's front
garden (scene.lua Sc.paintGarden), not on the street paving.

True scale: a Labrador's kennel is about 0.95 m wide and tall: 44 x 44 px at 46 px/m. Front-on (BIBLE: the gable end):
  * the roof: two boards seen end-on, 5 px thick, pitched 1 in 2 (even 2 px steps) from a peak over the middle (cols 21-22, row 0) to
    the eaves, overhanging the walls by 3 px a side; lit top edge, slate body with shingle ends every 4 px in
    running bond, a dark underside (sun upper left: the left board one step lighter on top);
  * a 1 px shadow row on the wall under the roof boards;
  * the gable wall in falu red planks, 4 px courses (lit row, two mid rows, a dark lap), a lit left corner post and
    a shaded right one;
  * a round door in the middle (opening cols 12-31, 20 px), a semicircle arch with its crown on row 25 (world y 165:
    19 px to crawl under, as before), a cream frame, a dark inside with the arch's inner shadow;
  * a name plate over the door: a cream board with a dark edge and two nails, no letters (no text in art);
  * one 1 px ink outline round the whole (an obstacle), the kennel's own ink #12121a; the door is open at the bottom.
Art row 0 = world y 140, the bottom row 43 = y 183 (Pepper's line is y 184). Drawn by setpieces.lua kennel().
Collision (level/riverwalk.lua): the ridge box x 16-28 from y 140 and the eaves box x 0-44 from y 150 (the roof
boards' top at the walls' corners), so she stands on the roof wherever she is on it; the door crown stays y 165."""
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
CREAM, CREAM_D = hexc('#f1dbbb'), hexc('#d3c3b4')                                 # door frame, plate
IN_D, IN = hexc('#1c1c1c'), hexc('#2b2a25')                                       # the inside
W, H = 44, 44
BAND = 5                                                                          # the roof boards' thickness
WALL_X0, WALL_X1 = 3, 40                                                          # the walls (overhang 3 px a side)
DOOR_X0, DOOR_X1, CROWN = 12, 31, 25                                              # the opening, the arch's crown row
PLATE = (15, 28, 17, 21)                                                          # x0, x1, y0, y1 (inclusive)


def roof_top(x):
    """the roof's top row at column x: 1 in 2 from the peak (cols 21 and 22 at row 0), even 2 px steps"""
    return int(abs(x - 21.5) - 0.5) // 2


def build():
    a = np.zeros((H, W, 4), np.uint8)
    inside = np.zeros((H, W), bool)
    # the gable wall: under the roof boards, cols 3-40, down to the bottom
    for x in range(WALL_X0, WALL_X1 + 1):
        for r in range(roof_top(x) + BAND, H):
            inside[r, x] = True
            k = r % 4
            c = (RED_L, RED, RED, LAP)[k]
            if x == WALL_X0 + 1: c = RED_L                                # the corner posts: lit left, shaded right
            if x == WALL_X1 - 1: c = RED_D
            if r == roof_top(x) + BAND: c = LAP                           # the roof's shadow on the wall
            a[r, x] = c
    # the roof boards
    for x in range(W):
        t = roof_top(x)
        for i in range(BAND):
            r = t + i
            if r >= H: continue
            inside[r, x] = True
            if i == 0: c = SLATE_L if x <= 21 else SLATE
            elif i == BAND - 1: c = SLATE_D
            else:
                c = SLATE
                if i in (1, 2) and ((x if x <= 21 else 43 - x) + 2 * (i % 2)) % 4 == 0: c = SLATE_D   # shingle ends
            a[r, x] = c
    # the round door: a semicircle arch (radius 10, centre col 21.5, row 35) on straight jambs
    door = np.zeros((H, W), bool)
    cx, cr, rad = 21.5, CROWN + 10, 10
    for r in range(CROWN, H):
        for x in range(DOOR_X0, DOOR_X1 + 1):
            if r >= cr or (x - cx) ** 2 + (r - cr + 0.5) ** 2 <= rad * rad: door[r, x] = True
    for r in range(H):
        for x in range(W):
            if not door[r, x]: continue
            edge_top = r > 0 and not door[r - 1, x]
            a[r, x] = IN_D if edge_top or not door[r, min(W - 1, x + 1)] or not door[r, max(0, x - 1)] else IN
    for r in range(H):                                                # the cream frame round the opening
        for x in range(W):
            if door[r, x] or not inside[r, x]: continue
            if any(0 <= r + dy < H and 0 <= x + dx < W and door[r + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                a[r, x] = CREAM if x < cx else CREAM_D
    # the name plate: cream board, a dark edge, two nails, no letters
    x0, x1, y0, y1 = PLATE
    for r in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = r in (y0, y1) or x in (x0, x1)
            a[r, x] = LAP if edge else (CREAM if r < y1 - 1 else CREAM_D)
    a[y0 + 2, x0 + 2] = SLATE_D; a[y0 + 2, x1 - 2] = SLATE_D
    # one ink outline: every inside pixel touching the outside
    for r in range(H):
        for x in range(W):
            if not inside[r, x]: continue
            if any(not (0 <= r + dy < H and 0 <= x + dx < W) or not inside[r + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                a[r, x] = INK
    # the door is open at the bottom (she crawls in): the bottom row of the opening stays the inside
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
