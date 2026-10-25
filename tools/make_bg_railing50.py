#!/usr/bin/env python3
"""The decorative quay railing at true scale (25 Oct 2026): 1.1 m = 50 px at 46 px a metre (was 30 px, a third
small; layer plan "railing: too small, rebuild"). Tier C, built in code: an open iron railing, a round handrail tube
and two lower tube rails on slim posts, no balusters, so it never looks like the obstacle fence. Colours: the lamp
post's own five (as the old railing), light from the upper left: each tube lit on its top row and a darker shade of
its own iron on its bottom row, each post lit on its left column and shaded on its right (no ink outline). The game fades it like all decoration.
Same piece widths as before (left 5, unit 84, end 86), so every railing in the level keeps its length.
Writes riverwalk/art/scene/rail_bg_left.png, rail_bg_unit.png, rail_bg_end.png."""
import os
import numpy as np
from PIL import Image

H = 50
C = {'hi': (88, 109, 134), 'li': (69, 88, 112), 'mid': (53, 69, 95), 'sh': (49, 64, 88), 'dk': (15, 21, 40)}
TUBES = [(0, ['hi', 'li', 'li', 'mid', 'sh']), (23, ['hi', 'li', 'sh']), (38, ['hi', 'li', 'sh'])]   # (top row, rows)


def piece(w, posts, rail_end=None):
    a = np.zeros((H, w, 4), np.uint8)
    def put(x, y, c):
        if 0 <= x < w and 0 <= y < H: a[y, x] = (*C[c], 255)
    for x0 in posts:                                    # posts: 3 px shaft, a 5 px foot plate
        for y in range(H):
            put(x0, y, 'hi'); put(x0 + 1, y, 'li'); put(x0 + 2, y, 'sh')
        for y in (H - 3, H - 2):
            for dx in range(-1, 4): put(x0 + dx, y, 'li' if y == H - 3 else 'sh')
        for dx in range(-1, 4): put(x0 + dx, H - 1, 'sh')
    for top, rows in TUBES:                             # tubes run over the posts
        for i, c in enumerate(rows):
            for x in range(rail_end or w): put(x, top + i, c)
    for x0 in posts:                                    # collars where the lower rails meet a post: 5 px wide rings
        for top, rows in TUBES[1:]:
            for dy in range(-1, len(rows) + 1):
                for dx in range(-1, 4):
                    put(x0 + dx, top + dy, 'hi' if dy == -1 else ('sh' if dy == len(rows) else 'li'))
    return a


D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'riverwalk', 'art', 'scene')
Image.fromarray(piece(5, [1])).save(os.path.join(D, 'rail_bg_left.png'))
Image.fromarray(piece(84, [80])).save(os.path.join(D, 'rail_bg_unit.png'))
Image.fromarray(piece(86, [80], rail_end=84)).save(os.path.join(D, 'rail_bg_end.png'))   # last span 80 like the rest
print('quay railing', H, 'px tall: left 5, unit 84, end 86')
