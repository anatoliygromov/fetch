#!/usr/bin/env python3
"""rt_pilot_tile.py: the Rooftops loose tile (24 x 6, the game's size; an obstacle: 1 px ink outline) in the concept's
clay colours. The concept drew the tiles as two loose piles; the game keeps its 24 x 6 tiles (3 per skylight) and takes
only their look: four clay tile ends side by side, lit from the upper left, each with its own shade on the right."""
import numpy as np, cv2
from PIL import Image
c = np.asarray(Image.open('art/source/rt_lockfill/cut.png').convert('RGB')).astype(int)
pile = c[130:160, 55:98].reshape(-1, 3)
tile = pile[(pile[:, 0] > 140) & (pile[:, 0] - pile[:, 1] > 75) & (pile[:, 1] < 125)].astype(np.float32)
_, lb, cen = cv2.kmeans(tile, 3, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3, cv2.KMEANS_PP_CENTERS)
cen = cen[np.argsort(cen @ np.array([.299, .587, .114]))]           # dark to light
sh, body, hi = [tuple(int(v) for v in x) for x in cen]
sh = tuple(int(v * 0.74) for v in body)                    # a clear step down: the k-means shade sat too close to the body
dark = c[130:160, 55:98].reshape(-1, 3); dark = dark[(dark @ np.array([.299, .587, .114])) < 70]
ink = tuple(int(v) for v in (np.median(dark, 0) if len(dark) else (60, 30, 28)))
T = np.zeros((6, 24, 4), np.uint8)
def px(x, y, col): T[y, x, :3] = col; T[y, x, 3] = 255
for x in range(24):
    px(x, 0, ink); px(x, 5, ink)
for y in range(6): px(0, y, ink); px(23, y, ink)
for i in range(4):                                       # four tile ends, 6 px each (the outline eats the outer column)
    x0 = i * 6
    for x in range(max(1, x0), min(23, x0 + 6)):
        px(x, 1, hi); px(x, 2, body); px(x, 3, body); px(x, 4, sh)
    if 0 < x0 + 5 < 23:
        for y in (2, 3): px(x0 + 5, y, sh)               # the gap between two tiles: the right tile's shade
    if x0 + 1 < 23: px(max(1, x0 + 1), 2, hi)            # a lit corner on each tile
Image.fromarray(T).save('riverwalk/levelart/rooftops/pilot_tile.png')
print('ink', ink, 'hi', hi, 'body', body, 'shade', sh)
