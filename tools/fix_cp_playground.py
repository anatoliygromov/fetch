#!/usr/bin/env python3
"""fix_cp_playground.py: the playground's slide tower redrawn by rule, 0 credits (night 6-7 Nov, cp track; the final
gate review, art/gen/reviews/final_06nov_night.md: "the slide is a 2 px red line, the climbing tower a wire frame").
Same file, same size (park_slide.png, 66 x 63), same anchor, so every box stays where it is. On the old file
(kept as art/source/park_slide/park_slide_old.png), each rule listed in art/source/park_slide/edits.json:
  posts    the two tower posts 4 px wide (were 3): the inner column next to each post takes the post's grey, its ink
           moves one column in (the balusters beside them go)
  panel    the cage of 1 px balusters between the top rail and the deck goes; in its place a solid side panel in the
           top rail's red (rows 15-27, between the posts) with a lit top edge, a shaded bottom row and a round
           window (7 px) in the middle, and an open band under the rail (the rail stands on the posts)
  chute    the 2-3 px red line becomes a chute 7 px deep at 45 degrees: the lit rim, the bed in the rail's red, the
           bed's lip in the dark, the side rail's face in the red (2 rows) and its shade, the ink under it (the side
           rail in the dark only read as ink under the look); its legs (4 px) run up to its underside
Run from the repo root: python3 tools/fix_cp_playground.py (idempotent: it starts from the old file)."""
import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

F = 'riverwalk/art/scene/park_slide.png'; D = 'art/source/park_slide'; os.makedirs(D, exist_ok=True)
OLD = f'{D}/park_slide_old.png'
if not os.path.exists(OLD): Image.open(F).save(OLD)
src = np.array(Image.open(OLD).convert('RGBA')); a = src.copy()
H, W = a.shape[:2]
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)
INK, RED, RED_D, RED_L, G_L, G_D, Y = hx('1d1816'), hx('c8473a'), hx('8f2f27'), hx('e2715d'), hx('9aa3ab'), hx('6b737b'), hx('e8b83f')
CLR = np.zeros(4, np.uint8)
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: a[y, x] = c
# posts: rows 3-61, left post colours x 2-4 -> 2-5, ink at 6; right post x 29-31 -> 28-31, ink at 27
for y in range(3, 62):
    if y in range(29, 33): continue                                 # (the deck runs over them)
    put(5, y, G_D); put(6, y, INK)
    put(28, y, G_L); put(27, y, INK)
# panel: clear the balusters between the posts (x 7-26) over rows 3-28, then the panel
for y in range(3, 29):
    for x in range(7, 27): put(x, y, CLR)
for x in range(7, 27):                                              # the rail's underside ink stays at row 3
    put(x, 3, INK)
for y in range(14, 29):
    for x in range(7, 27):
        c = RED
        if y == 14: c = INK
        elif y == 15: c = RED_L
        elif y == 28: c = INK
        elif y == 27: c = RED_D
        put(x, y, c)
cx, cy, r = 16.5, 21, 3.6                                           # the round window
for y in range(16, 27):
    for x in range(7, 27):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if d < r - 0.5: put(x, y, CLR)
        elif d < r + 0.5: put(x, y, INK)
# chute: clear the old line (its reds and ink right of the tower, x >= 34, rows 29-62) but keep the legs
legs = [(34, 37), (44, 47), (54, 57)]
def onleg(x): return any(l <= x <= r for l, r in legs)
for y in range(29, 63):
    for x in range(33, W):
        if not onleg(x): put(x, y, CLR)
def top(x): return 29 + (x - 34)                                    # the old line's top row, 45 degrees
for x in range(33, W):
    t = top(x)
    rows = [(t - 1, INK), (t, RED_L), (t + 1, RED), (t + 2, RED_D), (t + 3, RED), (t + 4, RED), (t + 5, RED_D), (t + 6, INK)]   # rim, bed, its lip line, the side rail's face, its shade
    for y, c in rows:
        if y <= 61: put(x, y, c)
for l, r_ in legs:                                                  # legs from under the chute to the ground (row 61, ink 62)
    for x in range(l, r_ + 1):
        for y in range(top(l) + 7, 62):
            c = INK if x in (l, r_) else (G_L if x == l + 1 else G_D)
            put(x, y, c)
        put(x, 62, INK)
put(W - 1, 61, INK)
ed = [{'x': int(x), 'y': int(y), 'from': src[y, x].tolist(), 'to': a[y, x].tolist()} for y, x in zip(*np.nonzero((a != src).any(-1)))]
json.dump({'asset': 'park_slide', 'base': OLD, 'rules': ['posts', 'panel', 'chute'], 'changed': len(ed), 'pixels': ed}, open(f'{D}/edits.json', 'w'))
Image.fromarray(a, 'RGBA').save(F)
aseprite_io.write(f'{D}/park_slide.aseprite', [a], layer='park_slide')
print('park_slide:', len(ed), 'pixels changed')
