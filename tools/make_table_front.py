#!/usr/bin/env python3
"""The City Park picnic table, front-on (art/scene/park_table_front.png, 72 x 28, same size and collision box as
park_table.png, which was drawn three-quarter from above). Seen from the front at Pepper's height, the long side
facing us: the tabletop's front edge with a thin cap (the row Pepper stands on, the collision top y 156), the leg
posts at both ends, and the near bench in front, a little wider than the table. Drawn in park_table.png's own colours,
with the 1 px dark outline every obstacle has. The original stays in the repo."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', 'riverwalk', 'art', 'scene')
C = {'k': (3, 0, 0), 'h': (238, 187, 129), 'l': (224, 176, 127), 'm': (193, 115, 65), 'q': (194, 124, 72),
     'n': (138, 82, 46), 's': (110, 60, 44), 'd': (23, 13, 10)}
W, H = 72, 28
g = [['.'] * W for _ in range(H)]
def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): g[y][x] = c
def board(x0, y0, x1, y1):                     # a plank seen front-on: outline, light cap row, front face, grain
    rect(x0, y0, x1, y1, 'k')
    rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1, 'h')
    rect(x0 + 1, y0 + 2, x1 - 1, y1 - 2, 'm')
    rect(x0 + 1, y1 - 1, x1 - 1, y1 - 1, 'n')
    for x in range(x0 + 5, x1 - 2, 11):        # grain flecks and board ends
        g[y0 + 3][x] = 'q'; g[y0 + 2][x + 3] = 'l'
    for x in range(x0 + 17, x1 - 3, 17):       # joints between the boards
        for y in range(y0 + 2, y1): g[y][x] = 's'
def leg(x0, x1, y0, y1):
    rect(x0, y0, x1, y1, 'k')
    rect(x0 + 1, y0, x1 - 1, y1 - 1, 'n')
    rect(x0 + 1, y0, x0 + 1, y1 - 1, 'q')       # lit edge
    rect(x1 - 1, y0, x1 - 1, y1 - 1, 's')       # shade edge
# the legs (under the table, behind the near bench)
for lx in (9, 57):
    leg(lx, lx + 5, 6, 27)
# the cross brace under the tabletop, in shadow
rect(15, 8, 56, 10, 'k'); rect(15, 9, 56, 9, 's')
# the tabletop's front edge, 68 wide
board(2, 0, 69, 6)
# the near bench, the full 72 wide, at seat height
board(0, 14, 71, 19)
# bench feet below the seat, in front of the legs
for bx in (10, 58):
    rect(bx, 20, bx + 3, 27, 'k'); rect(bx + 1, 20, bx + 2, 26, 'n')
im = Image.new('RGBA', (W, H))
for y in range(H):
    for x in range(W):
        if g[y][x] != '.': im.putpixel((x, y), C[g[y][x]] + (255,))
im.save(os.path.join(ART, 'park_table_front.png'))
print('park_table_front.png', W, 'x', H)
