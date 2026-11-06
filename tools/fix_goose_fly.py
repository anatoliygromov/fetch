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
           [(84, 76), (85, 77)], [(84, 79), (85, 79)]]
for patch in PATCHES:                                       # each patch to the colour of the pixels all round it
    ring = [tuple(before[y + dy, x + dx]) for x, y in patch for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
            if (x + dx, y + dy) not in patch and before[y + dy, x + dx, 3]]
    vals, cnt = np.unique(np.array(ring), axis=0, return_counts=True)
    for x, y in patch: a[y, x] = vals[cnt.argmax()]
Image.fromarray(a).save(F)
px = [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in a[y, x])] for y, x in zip(*np.nonzero((a != before).any(-1)))]
json.dump({'asset': 'goose', 'base': SRC + 'goose_before.png (the file as on preview/05nov-night)',
           'method': 'tools/fix_goose_fly.py: fly row cell 4 := cell 5, cell 6 := cell 7, two blotches to their ring colour',
           'changed': len(px), 'pixels': px}, open(SRC + 'edits.json', 'w'))
print('goose fly row fixed:', len(px), 'pixels changed')
