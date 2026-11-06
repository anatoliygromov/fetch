#!/usr/bin/env python3
"""art/source/town_shopsign/fix_pretzel.py: the bakery sign's pretzel redrawn by hand rule (review 6 Nov, item 9:
the old pretzel was two thin dashed gold rings and read as spectacles). Only the plate's field (cols 4-30, rows 14-27)
is touched: it is cleared to the plate's red-brown and one pretzel (19 x 13) is drawn as a knotted loop: two lobes on
top, the arms crossing in the middle, the ends on the bottom of the loop, three holes. Dough in the sign's gold, a 1 px
darker gold edge on its lower and right sides (light from the upper left). No new colours. Every changed pixel is in
edits.json.

  python3 -I art/source/town_shopsign/fix_pretzel.py   writes riverwalk/art/scene/town_shopsign.png, the .aseprite
"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import aseprite_io

PRETZEL = ["...####.....####...",
           ".########.########.",
           "###....#####....###",
           "##......###......##",
           "##.......#.......##",
           "##......###......##",
           "##.....##.##.....##",
           "###...##...##...###",
           ".###.##.....##.###.",
           "..####.......####..",
           "..###.........###..",
           "...#############...",
           ".....#########....."]
FIELD, DOUGH, EDGE = (122, 59, 42), (226, 181, 74), (168, 122, 38)     # the plate, the sign's two golds
old = np.array(Image.open(os.path.join(HERE, 'town_shopsign_v0.png')).convert('RGBA'))
out = old.copy()
out[14:28, 4:31, :3] = FIELD
on = np.array([[c == '#' for c in r] for r in PRETZEL]); h, w = on.shape
X0, Y0 = 4 + (27 - w) // 2, 15
for y in range(h):
    for x in range(w):
        if on[y, x]:
            edge = y + 1 >= h or not on[y + 1, x] or x + 1 >= w or not on[y, x + 1]
            out[Y0 + y, X0 + x, :3] = EDGE if edge else DOUGH
Image.fromarray(out).save(os.path.join(ROOT, 'riverwalk/art/scene/town_shopsign.png'))
aseprite_io.write(os.path.join(HERE, 'town_shopsign.aseprite'), [out])
px = [[x, y, '#%02x%02x%02x%02x' % tuple(int(v) for v in out[y, x])] for y in range(out.shape[0]) for x in range(out.shape[1])
      if not np.array_equal(out[y, x], old[y, x])]
json.dump({"asset": "town_shopsign", "base": "town_shopsign_v0.png (the file before review round 1)",
           "method": "the plate's field cleared, one pretzel drawn by rule (PRETZEL), two golds of the sign",
           "changed": len(px), "pixels": px}, open(os.path.join(HERE, 'edits.json'), 'w'))
print('town_shopsign', out.shape[1], 'x', out.shape[0], len(px), 'pixels changed')
