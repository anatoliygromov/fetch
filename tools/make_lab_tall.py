#!/usr/bin/env python3
"""Writes riverwalk/level/lab_tall.map: the height engine's test level, 3 screens wide x 3 screens tall
(120 x 90 cells of 8 px = 960 x 720 px). Greybox. The rest (ledges, lift, lamps, bones) is in level/lab_tall.lua.

  ground floor   y 664, x 0-560, a pit at x 224-256 (open to the bottom of the world: a heart)
  stairs         x 288-384, rising 96 px (12 slope cells) to the landing L1
  L1             y 568, x 384-560 (a solid block down to the ground)
  the pocket     ground floor x 560-816 under the ledges
  F2             y 504, x 816-944 (a solid block down to the bottom; the lift rests on it at x 896-944)
  roof           y 184, x 560-896 (a slab 16 px thick), Mia on it
  right wall     x 944-960, the whole height
Run from the repo root: python3 tools/make_lab_tall.py
"""
COLS, ROWS = 120, 90
g = [['.'] * COLS for _ in range(ROWS)]


def fill(x0, x1, y0, y1, ch='#'):
    for j in range(y0 // 8, y1 // 8):
        for i in range(x0 // 8, x1 // 8):
            g[j][i] = ch


fill(0, 944, 664, 720)                      # the ground floor
fill(224, 256, 664, 720, '.')               # the pit
for k in range(12):                         # the stairs: '/' rises to the right, solid under each step
    i, j = 36 + k, 82 - k
    g[j][i] = '/'
    for jj in range(j + 1, 83):
        g[jj][i] = '#'
fill(384, 560, 568, 664)                    # L1
fill(816, 944, 504, 720)                    # F2
fill(560, 896, 184, 200)                    # the roof
fill(944, 960, 0, 720)                      # the right wall

with open('riverwalk/level/lab_tall.map', 'w') as f:
    for row in g:
        f.write(''.join(row) + '\n')
print('riverwalk/level/lab_tall.map: %d x %d cells' % (COLS, ROWS))
