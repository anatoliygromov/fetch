#!/usr/bin/env python3
"""Writes riverwalk/level/night.map (Level 5, Night Harbour): 560 x 30 cells of 8 px (4480 x 240 px, 14 screens).
The quay (feet) is y 184 (row 24 down); every water gap is open from y 184 to 208 and water from y 208 (row 27).
The gaps (x0, x1 in px, multiples of 8) are the only thing in the map; jetty planks, boats and posts are props
and movers in level/night.lua."""
import os
W, H = 560, 30
GAPS = [(400, 448), (1000, 1160), (1320, 1560), (2280, 2520), (2600, 2840), (3240, 3400), (3424, 3520), (3800, 4080)]
rows = [['.'] * W for _ in range(H)]
for r in range(23, H):                      # rows 24..30 (1-based): y 184..240
    for c in range(W):
        rows[r][c] = '#'
for x0, x1 in GAPS:
    for c in range(x0 // 8, x1 // 8):
        for r in range(23, 26): rows[r][c] = '.'
        for r in range(26, H): rows[r][c] = '~'
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'riverwalk', 'level', 'night.map')
open(out, 'w').write('\n'.join(''.join(r) for r in rows) + '\n')
print('night.map', W, 'x', H)
