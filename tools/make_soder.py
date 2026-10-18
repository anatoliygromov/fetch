#!/usr/bin/env python3
"""Writes riverwalk/level/soder.map, the terrain of Level 4, Söder Hill (the chase), from the profile below.

The street steps down the hill from y 112 at the top to the quay at y 208, 16 px at a time, on short flights of
stairs (two 45-degree slope cells, so Pepper runs down them without a jump). Open cellar hatches are gaps in the
street: no terrain at all, so she falls out of the bottom of the screen (chase.lua takes a heart for that).
All x and y are level pixels and multiples of 8 (one map cell). 5120 px = 16 screens = 640 columns; 30 rows.
"""
import os

W, ROWS, CELL = 5120, 30, 8
TOP = 112
# (x, the street steps down 16 px here: two stair cells at x and x + 8)
STAIRS = [400, 1176, 1936, 2616, 3216, 3896]
# (x0, x1): open cellar hatches
HATCHES = [(1040, 1072), (1824, 1856), (2320, 2344), (2424, 2456), (3040, 3080), (3600, 3632), (3720, 3752)]

def ground_at(x):
    """the street's feet y at column x (left of a stair's first cell the upper level, after its second the lower)"""
    y = TOP
    for s in STAIRS:
        if x >= s + 16:
            y += 16
    return y

def main():
    cols = W // CELL
    grid = [['.'] * cols for _ in range(ROWS)]
    for c in range(cols):
        x = c * CELL
        if any(a <= x < b for a, b in HATCHES):
            continue
        stair = next((s for s in STAIRS if s <= x < s + 16), None)
        if stair is not None:
            top = ground_at(stair)                 # the upper level
            k = (x - stair) // CELL                # 0 or 1
            r = top // CELL + k
            grid[r][c] = '\\'
            for rr in range(r + 1, ROWS):
                grid[rr][c] = '#'
            continue
        for rr in range(ground_at(x) // CELL, ROWS):
            grid[rr][c] = '#'
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'riverwalk', 'level', 'soder.map')
    with open(out, 'w') as f:
        for row in grid:
            f.write(''.join(row) + '\n')
    print('level/soder.map', cols, 'x', ROWS, 'street', TOP, '->', ground_at(W - 1))

if __name__ == '__main__':
    main()
