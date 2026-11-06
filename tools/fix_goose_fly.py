#!/usr/bin/env python3
"""fix_goose_fly.py: hand fix of the goose's fly row (row 3 of riverwalk/art/goose.png, 34 x 34 cells), 6 Nov fix round
1 of art/cp-critters-06nov (review art/gen/reviews/cp_critters.md: shading FAIL, the fly row rough). No automated
clean pass (BIBLE 3): every edit is named here, every changed pixel recorded in art/source/goose/edits.json.
The walk and hiss rows are not touched.
  1. cell 4 (the take-off's third frame, a squashed, lumpy down-stroke) := cell 5 (the clean wings-down glide), so the
     take-off reads 2 wings open, 3 wings up, 4 wings down (critters.lua gooseFrame plays 2 3 4, then loops 5-8).
  2. cell 6 (the loop's lumpy wings-flat frame) := cell 7 (wings up): the loop is down, up, up, down.
  3. the two flagged blotches by hand, each patch to the one colour all round it: cell 2 (x 43-47, y 86-88) and
     cell 3 (x 84-85, y 76-79), wing shading specks inside the wing's mid grey.
  4. (round 2) cell 2: the far wing that hung down beside the neck like a second neck (x 23-29, rows 12-22 of the
     cell) taken off; the neck keeps its right ink (x 22 on rows 12-13, x 23 on 14-16), the body its own edge; what
     shows is the near wing opening behind the back, the take-off into cell 3's wings up.
  5. (round 2) cells 2 and 3: the black stub off the beak (x 25-28 of the beak row and one pixel under it) taken out;
     the beak is a 2 x 2 orange tip closed with the ink, like the walk frames.
  7. (night 6 Nov, cp fix round 1) cell 5: the wings-level stroke (the wings under the belly off, one wing level along
     the back), so the loop is down, level, up, up, down instead of down, down, up, up, down.
  6. (night 6 Nov, cp track) cell 1 (the stand before take-off): the 2 px blotch asset_qa flags (x 9-10, y 90) to its ring.
Run from the repo root on the original (art/source/goose/goose_before.png is kept): python3 tools/fix_goose_fly.py"""
import json, os, shutil
import numpy as np
from PIL import Image

F, SRC = 'riverwalk/art/goose.png', 'art/source/goose/'
os.makedirs(SRC, exist_ok=True)
if not os.path.exists(SRC + 'goose_before.png'): shutil.copy(F, SRC + 'goose_before.png')
before = np.array(Image.open(SRC + 'goose_before.png').convert('RGBA'))
a = before.copy()
C, ROW = 34, 2
cell = lambda i: (slice(ROW * C, ROW * C + C), slice((i - 1) * C, i * C))
a[cell(4)] = before[cell(5)]
a[cell(6)] = before[cell(7)]
PATCHES = [[(43, 86), (44, 86), (43, 87), (44, 87), (45, 87), (46, 87), (44, 88), (45, 88), (46, 88), (47, 88)],
           [(84, 76), (85, 77)], [(84, 79), (85, 79)],
           [(9, 90), (10, 90)]]                             # (night 6 Nov, cp) 6. cell 1's 2 px blotch in the body (asset_qa)
for patch in PATCHES:                                       # each patch to the colour of the pixels all round it
    ring = [tuple(before[y + dy, x + dx]) for x, y in patch for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
            if (x + dx, y + dy) not in patch and before[y + dy, x + dx, 3]]
    vals, cnt = np.unique(np.array(ring), axis=0, return_counts=True)
    for x, y in patch: a[y, x] = vals[cnt.argmax()]
INK, ORANGE = before[68 + 6, 34 + 21].copy(), before[68 + 8, 34 + 24].copy()     # cell 2's neck ink, beak orange
def cpx(c, x, y): return 68 + y, (c - 1) * 34 + x
# 4. cell 2: the hanging far wing
for y, edge in ((12, 22), (13, 22), (14, 23), (15, 23), (16, 23)):
    for x in range(edge + 1, 31): a[cpx(2, x, y)] = 0
for y in range(17, 23):
    x = 20
    while a[cpx(2, x, y)][3]: x += 1                          # the body's own run from the neck
    for x2 in range(x, 34): a[cpx(2, x2, y)] = 0
# 5. the beak stubs: cell 2 beak rows 8-9, cell 3 beak rows 9-10 (the tip at x 24-25, the ink at x 26)
for c, r in ((2, 8), (3, 9)):
    for y in (r, r + 1):
        a[cpx(c, 24, y)] = ORANGE; a[cpx(c, 25, y)] = ORANGE; a[cpx(c, 26, y)] = INK
        for x in range(27, 30): a[cpx(c, x, y)] = 0
    for x in range(24, 27):
        a[cpx(c, x, r - 1)] = INK if not a[cpx(c, x, r - 1)][3] or x >= 25 else a[cpx(c, x, r - 1)]
        a[cpx(c, x, r + 2)] = INK
    for x in range(27, 30): a[cpx(c, x, r + 2)] = 0
# 7. (night 6 Nov, cp fix round 1; review cp_goose_fly: "frames 4 and 5 are near twins") cell 5 becomes the wings-level
#    stroke between the down (cell 4) and up (cells 6-7) frames: from cell 5's glide, the two wings hanging under the
#    belly (rows 22 and down) are taken off, the feet tucked under the tail as in cell 6, the belly closed with the ink;
#    the near wing is laid level along the back, seen edge-on: a band over the back (rows 11-13, x 7-19) in the
#    wing's own greys (lit top, mid, the dark primaries at its back end), closed with the ink.
def P(x, y): return 68 + y, 4 * 34 + x                       # cell 5, x and y in the cell
INK5 = INK
G = {k: before[68 + y, 4 * 34 + x].copy() for k, (x, y) in {'1': (2, 19), '2': (3, 19), '3': (12, 14), '7': (8, 15)}.items()}
for y in range(22, 34):
    for x in range(0, 34): a[P(x, y)] = 0
for y in range(23, 29):                                         # the feet tucked under the tail, as in cell 6 (1 row up)
    for x in range(0, 12):
        q = before[68 + y, 5 * 34 + x]
        if q[3]: a[P(x, y - 1)] = q
for x in range(1, 23):                                          # the belly's ink under the last body pixel
    ys = [y for y in range(10, 22) if a[P(x, y)][3]]
    if ys and not (a[P(x, ys[-1])][:3] == INK5[:3]).all():
        a[P(x, ys[-1] + 1)] = INK5
# (polish, review c06cfb6: "spread the near wing flat") the level wing is spread out flat: 5 rows from the shoulder
# (x 20) back past the rump to its tip (x 2), the lit leading edge on top, the coverts, the dark primaries at the back
# end in a 3-step tip; the outline is closed by the next step
BAND = {10: (9, 18, None), 11: (6, 19, '3'), 12: (4, 20, '2'), 13: (2, 20, '2'), 14: (2, 12, '1')}
for y, (x0, x1, c) in BAND.items():
    for x in range(x0, x1 + 1):
        edge = c is None or x == x1 or (x == x0 and y < 14)
        prim = x <= x0 + 4 and y >= 12                               # the primaries
        a[P(x, y)] = INK5 if edge else (G['7'] if prim else G[c])
for _ in range(1):                                              # the ink closed round every edge of the new cell 5
    add = []
    for y in range(34):
        for x in range(34):
            if a[P(x, y)][3]: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < 34 and 0 <= y + dy < 34:
                    q = a[P(x + dx, y + dy)]
                    if q[3] and not (q[:3] == INK[:3]).all(): add.append((x, y)); break
    for x, y in add: a[P(x, y)] = INK
Image.fromarray(a).save(F)
px = [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in a[y, x])] for y, x in zip(*np.nonzero((a != before).any(-1)))]
json.dump({'asset': 'goose', 'base': SRC + 'goose_before.png (the file as on preview/05nov-night)',
           'method': 'tools/fix_goose_fly.py: fly row cell 4 := cell 5, cell 6 := cell 7, two blotches to their ring colour',
           'changed': len(px), 'pixels': px}, open(SRC + 'edits.json', 'w'))
print('goose fly row fixed:', len(px), 'pixels changed')
