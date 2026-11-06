#!/usr/bin/env python3
"""cp_trunk_spans.py [--check]: the visible trunk of each City Park art tree, row by row (night 6 Nov 2026, cp fix
round 1). For cp_oak, cp_lime and cp_ash: from 15 rows over the foot up, the run of opaque pixels that holds the run
below's centre, which may only narrow going up (where the crown's leaves widen the run, the trunk's last width is kept;
a trunk narrows upwards, it never widens). Writes riverwalk/cp_tree_spans.lua { name = { w, h, [row] = { x0, x1 } } }
(x1 inclusive), which scene.lua's limbs use to leave the trunk where it is drawn at their height: they used the foot's
width before, so a limb's root lay over sky beside a trunk that narrows upwards and read as a deck, not a limb."""
import sys
import numpy as np
from PIL import Image
OUT = 'riverwalk/cp_tree_spans.lua'
lines = ['-- written by tools/cp_trunk_spans.py: the visible trunk of each art tree per row (x0, x1 inclusive)', 'return {']
for n in ('cp_oak', 'cp_lime', 'cp_ash'):
    a = np.array(Image.open(f'riverwalk/art/scene/{n}.png'))[..., 3] > 0
    H, W = a.shape
    cx = int(round(np.nonzero(a[H - 31])[0].mean()))
    x0 = x1 = None; rows = {}
    for y in range(H - 16, -1, -1):
        if a[y, cx]:
            l = cx
            while l > 0 and a[y, l - 1]: l -= 1
            r = cx
            while r < W - 1 and a[y, r + 1]: r += 1
            x0, x1 = (l, r) if x0 is None else (max(x0, l), min(x1, r))
            if x1 - x0 < 6: x0, x1 = cx - 3, cx + 3
            cx = (x0 + x1) // 2
        if x0 is not None: rows[y] = (x0, x1)
    body = ', '.join(f'[{y}] = {{ {u}, {v} }}' for y, (u, v) in sorted(rows.items()))
    lines.append(f'  {n} = {{ w = {W}, h = {H}, {body} }},')
lines.append('}')
txt = '\n'.join(lines) + '\n'
if '--check' in sys.argv:
    ok = open(OUT).read() == txt; print('OK' if ok else 'DIFF', OUT); sys.exit(0 if ok else 1)
open(OUT, 'w').write(txt); print('wrote', OUT)
