#!/usr/bin/env python3
"""fix_cp_bush.py: City Park's front bush (park_bush.png, 75 x 34, front layer) redrawn by rule on its own silhouette
(review 6 Nov, cp_props_06nov round 1: mottled fill, lone pixels, twig dots, 6 blotches). Not a clean pass: the shape
is kept pixel for pixel (only free twig dots of 1-3 px that touch nothing go) and the inside is painted again in four
flat shades of its own colours, by these rules (front layer: a dark silhouette with a thin rim of light on top):
  RIM   (59, 57, 33)  the top edge: an opaque pixel whose upper neighbour is empty (twigs excepted)
  LIT   (46, 45, 29)  the lit upper left of the mass: 1 to about LIT_DEPTH px under the top edge (a scalloped lower edge,
                      one clump every 11 px), left of the shade line
  SHADE (33, 30, 25)  the rest of the mass
  DARK  (19, 16, 15)  twigs (1 px wide parts) and the left, right and bottom edge
Every changed pixel: art/source/park_bush/edits.json. The old file: art/source/park_bush/park_bush_before.png."""
import os, json, shutil
import numpy as np
from PIL import Image
from scipy import ndimage

F = 'riverwalk/art/scene/park_bush.png'; OUT = 'art/source/park_bush'
os.makedirs(OUT, exist_ok=True)
if not os.path.exists(f'{OUT}/park_bush_before.png'): shutil.copy(F, f'{OUT}/park_bush_before.png')
a = np.array(Image.open(f'{OUT}/park_bush_before.png').convert('RGBA'))
al = a[..., 3] > 0; H, W = al.shape
RIM, LIT, SHADE, DARK = (59, 57, 33), (46, 45, 29), (33, 30, 25), (19, 16, 15)
LIT_DEPTH = 9
# free twig dots: components of 1-3 px not joined to the bush (8-connected)
lab, n = ndimage.label(al, structure=np.ones((3, 3)))
sizes = ndimage.sum(al, lab, range(1, n + 1))
dots = np.zeros_like(al)
for i, s in enumerate(sizes, 1):
    if s <= 3: dots |= lab == i
al2 = al & ~dots
# twigs: pixels of the silhouette less than 3 px thick (an opening by a 3x3 square removes them)
body = ndimage.binary_opening(al2, structure=np.ones((3, 3)))
twig = al2 & ~body
pa = np.pad(al2, 1)
up_empty = al2 & ~pa[:-2, 1:-1]
side_edge = al2 & ~(pa[1:-1, :-2] & pa[1:-1, 2:] & pa[2:, 1:-1])
top = np.full(W, H)
for x in range(W):
    ys = np.nonzero(body[:, x])[0]
    if len(ys): top[x] = ys.min()
depth = np.arange(H)[:, None] - top[None, :]
shade_line = 0.62 * W                       # the light comes from the upper left: the right part is in shade
out = np.zeros_like(a)
rgb = np.zeros((H, W, 3), np.uint8)
rgb[al2] = SHADE
xs = np.arange(W)[None, :]
scal = LIT_DEPTH + np.round(3 * np.abs(np.sin(np.pi * (xs + 3) / 11.0))) - 1   # leaf clumps: a scalloped lower edge, 11 px a clump
lit = al2 & (depth >= 1) & (depth <= scal) & (xs < shade_line - depth * 0.6)
rgb[lit] = LIT
rgb[side_edge] = DARK
rgb[up_empty & body] = RIM
rgb[twig] = DARK
out[..., :3] = rgb; out[..., 3] = (al2 * 255).astype(np.uint8)
Image.fromarray(out).save(F)
ch = [[int(x), int(y), [int(v) for v in a[y, x, :3]], [int(v) for v in out[y, x, :3]] if al2[y, x] else None]
      for y, x in zip(*np.nonzero(al)) if not al2[y, x] or tuple(a[y, x, :3]) != tuple(out[y, x, :3])]
json.dump({'name': 'park_bush', 'rule': __doc__, 'twig_dots_removed': int(dots.sum()), 'changed': ch},
          open(f'{OUT}/edits.json', 'w'), indent=0)
import sys; sys.path.insert(0, 'tools'); import aseprite_io
aseprite_io.write(f'{OUT}/park_bush.aseprite', [out])
print('park_bush: changed', len(ch), 'px, twig dots removed', int(dots.sum()), 'colours', len(np.unique(rgb[al2], axis=0)))
