#!/usr/bin/env python3
"""build_duckboat.py: the City Park duck boat riverwalk/art/scene/cp_duckboat.png from its SpriteCook render (6 Nov).

Source: art/gen/renders/cp_duckboat_a.png, Pixel Engine Image at exactly 92 x 60 (a two-seat pedal boat shaped like
a white duck, 2.0 m long at 46 px/m, facing left). The render is at game size: the cut is 1:1 (pitch 1), nothing
resampled. Hand edits by rule, every changed pixel in art/source/cp_duckboat/edits.json:
  1. front-on (BIBLE 3, no insides): the boat's inside and far rim between the duck's breast (cut at the render's
     own dark line down its side, which becomes the ink) and the seat back (rows 34-40) taken out, so the flat gunwale (the ink on row 41) is the deck line Pepper stands on, with the seat
     back and the tail standing on it; the breast's cut edge and the seat's left edge closed with the ink.
  2. one ink: the render's near-black outline (1, 1, 2) is #000000 (it already is one colour).
Layout for scene.lua Sc.drawMoverArt: deck = row 41; the mover's box is cols 8-87 (80 px), so the art is drawn at
(box x - 8, deck y - 41), mirrored about the box when the boat paddles right. The pond's surface is at deck + 7
(row 48: the red stripe sits on it); the rest of the hull is under the water.
Writes riverwalk/art/scene/cp_duckboat.png, art/source/cp_duckboat/{cp_duckboat.aseprite, edits.json, cut.png},
art/gen/out/cp_duckboat.cut.json. Run from the repo root: python3 tools/build_duckboat.py"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

SRC = 'art/source/cp_duckboat/'
os.makedirs(SRC, exist_ok=True)
cut = np.array(Image.open('art/gen/renders/cp_duckboat_a.png').convert('RGBA')).astype(int)
Image.fromarray(cut.astype(np.uint8)).save(SRC + 'cut.png')
a = cut.copy()
INK = np.array([0, 0, 0, 255])
isink = lambda p: p[3] and p[:3].sum() < 12
for y in range(a.shape[0]):
    for x in range(a.shape[1]):
        if isink(a[y, x]): a[y, x] = INK
DECK, SEAT_X = 41, 58
# 1. the inside: on rows 34-40, from the breast's edge (the last pixel of the breast run, counted from the left
#    across the white and light hull colours, stopped by the dark edge line) to the seat back's left ink
EDGEC = {(38, 52, 73), (94, 109, 127)}                      # the dark line down the breast's side (the render's)
edge = {}
for y in range(34, DECK):
    x = 30
    while x < SEAT_X and not (isink(a[y, x]) or tuple(a[y, x, :3]) in EDGEC): x += 1
    edge[y] = x                                                # the breast's dark edge (row 34: the far rim's ink)
    a[y, x + 1:SEAT_X] = 0
    a[y, x] = INK
# the seat back's left side and the rows just above the gunwale: closed with the ink where they meet the cut
for y in range(30, DECK):
    if a[y, SEAT_X, 3] and not isink(a[y, SEAT_X]): a[y, SEAT_X] = INK
Image.fromarray(a.astype(np.uint8)).save('riverwalk/art/scene/cp_duckboat.png')
px = [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in a[y, x])] for y, x in zip(*np.nonzero((a != cut).any(-1)))]
cols = sorted({tuple(int(v) for v in p[:3]) for p in a.reshape(-1, 4) if p[3]})
json.dump({'asset': 'cp_duckboat', 'base': SRC + 'cut.png (= art/gen/renders/cp_duckboat_a.png, 1:1)',
           'method': 'tools/build_duckboat.py: one ink; the inside and far rim taken out (front-on), edges closed',
           'deck_row': DECK, 'box_cols': [8, 87], 'colours': len(cols), 'changed': len(px), 'pixels': px},
          open(SRC + 'edits.json', 'w'))
aseprite_io.write(SRC + 'cp_duckboat.aseprite', [a.astype(np.uint8)])
json.dump({'name': 'cp_duckboat', 'size': [a.shape[1], a.shape[0]], 'render': 'art/gen/renders/cp_duckboat_a.png',
           'cut_by': 'Pixel Engine Image output at game size: pitch 1, taken 1:1, nothing resampled; tools/build_duckboat.py',
           'measures_px': {'length': 91, 'deck_row': DECK, 'head_top_row': 0, 'water_row': DECK + 7}, 'colours': len(cols), 'fails': []},
          open('art/gen/out/cp_duckboat.cut.json', 'w'), indent=1)
print('cp_duckboat.png', a.shape[1], 'x', a.shape[0], 'colours', len(cols), 'edits', len(px), 'breast edge', edge)
