#!/usr/bin/env python3
"""build_pile.py: River Walk's foreground mooring pile (front layer, tier C: built by rule, 0 credits; 5 Nov 2026).

  python3 -I tools/build_pile.py   -> riverwalk/art/scene/pile.png (18 x 182) and art/source/rw_pile/rw_pile.aseprite

A tarred timber pile 0.27 m thick at the front layer's 60 px/m (16 px), rising out of the bottom of the screen in
front of the river (level/riverwalk.lua: three piles, tops at y 221-225, so only the top 15-19 px are ever seen).
The front layer rule (docs/layer_ladder.md): a dark silhouette with a thin rim of light on the top edge, no outline,
3-8 colours, median luma 40 or less. Light from the upper left: the domed top catches a rim of light, the left
side a shade lighter than the right. One rope lashing near the top (the part that shows), one lower down. No lone
pixels: the grain is long unbroken lines; the rope's twist is a regular 4 px diagonal."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

hexc = lambda h: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
EDGE, SHADE, BASE, LIT, RIM = hexc('#050a17'), hexc('#17181f'), hexc('#21273a'), hexc('#282a36'), hexc('#393847')
ROPE, ROPE_HI = hexc('#1c1c1c'), hexc('#44423a')
W_, H_ = 18, 182
a = np.zeros((H_, W_, 4), np.uint8)

for y in range(H_):
    for x in range(1, 17):
        a[y, x] = EDGE if x in (1, 16) else LIT if x <= 4 else SHADE if x >= 13 else BASE
for x0, y0, y1 in ((7, 4, 44), (10, 14, 64), (6, 52, 120), (11, 80, 150), (8, 128, 181)):   # grain: long cracks
    a[y0:y1 + 1, x0] = SHADE
# the domed top: a rim of light, brightest on the sun side
a[0] = 0; a[1] = 0
SKY = hexc('#5f7387')                                    # the rim: the sky's light on the wet top
a[0, 4:14] = SKY
a[1, 2:16] = SKY; a[1, 10:16] = RIM; a[1, 1] = EDGE; a[1, 16] = EDGE
a[2, 2:7] = RIM
for y0 in (8, 70):                                       # rope lashings, a hair wider than the timber
    a[y0, 0:18] = EDGE; a[y0 + 5, 0:18] = EDGE
    for y in range(y0 + 1, y0 + 5):
        for x in range(0, 18):
            a[y, x] = ROPE_HI if (x + y) % 4 == 0 and x < 15 else ROPE
        a[y, 0] = EDGE; a[y, 17] = EDGE

out = Image.fromarray(a, 'RGBA')
os.makedirs('art/source/rw_pile', exist_ok=True)
out.save('riverwalk/art/scene/pile.png'); out.save('art/source/rw_pile/rw_pile.png')
aseprite_io.write('art/source/rw_pile/rw_pile.aseprite', [a], layer='rw_pile')
print('pile', out.size, 'colours', len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)))
