#!/usr/bin/env python3
"""rt_pilot_layers.py DIR OUTDIR: the Rooftops pilot's game layers from DIR/final.png (camera x 4224, y 240).
(review fix, 8 Nov 11:40) The far layer is opaque and 320 wide (it wraps). It slides sideways at PILOT_FAR of the
camera but moves with the world up and down, so looking up shows only sky above it (the game paints its top row's
colour there) and never the rows the concept did not paint. What the near roofs hide is filled along its own row
from the nearest far pixel: far roofs run on sideways, sky stays sky (never a column run on downward: the streaks).
The near layer is split into back (above Pepper's line, y < 136) and terrain (y >= 136) and the terrain runs on
below the frame: the lower storey and the hotel repeat (rows 198-239, one storey of 42 rows) three times."""
import sys, numpy as np
from PIL import Image
D, OUT = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(f'{D}/final.png').convert('RGB'))
far = np.load(f'{D}/far.npy'); H, W = far.shape
lum = im.astype(float) @ np.array([.299, .587, .114])
line = np.array([np.nonzero(~far[:, x])[0].min() for x in range(W)])
FH = H
far = far & (lum >= 100)                                    # dark pixels in the far mask are near-roof leaks (chimney pots)
from scipy import ndimage as nd
far = far & ~nd.binary_dilation(~far, iterations=2)          # and the 2 px along the near roofs' edge (their rims)
fl = np.zeros((FH, W, 3), np.uint8)
for y in range(FH):
    vis = np.nonzero(far[y])[0]
    if not len(vis): fl[y] = fl[y - 1]; continue               # below every skyline: never seen (moves with the world)
    for x in range(W):                                         # hidden behind the near roofs: the nearest far pixel of
        j = vis[np.argmin(np.abs(vis - x))]                    # the same row (roofs run on sideways, sky stays sky)
        fl[y, x] = im[y, j] if not far[y, x] else im[y, x]
back = np.zeros((H, W, 4), np.uint8); back[..., :3] = im
back[..., 3] = np.where(~far & (np.arange(H)[:, None] < 136), 255, 0)
storey = im[198:240].copy()
# (round 2) the lower-left wall's cast shadow is a wedge inside this storey; repeating it made a sawtooth. The run-on
# storeys are the LIT storey (columns 0-55 taken from the lit window bay one window to the right, x + 55) and every
# column that is in shadow at the frame's bottom row stays in shadow all the way down: lit colours map to their shadow
# colours by the pairs the concept itself shows (the shadowed window at x 2 against the lit one at x 56, wall beside).
lum2 = im.astype(float) @ np.array([.299, .587, .114])
lit = storey.copy(); lit[:, 0:55] = storey[:, 55:110]
pairs = {}
for yy in range(198, 240):
    for xx in range(0, 54):
        a = tuple(im[yy, xx + 55]); b = tuple(im[yy, xx])
        if lum2[yy, xx] < lum2[yy, xx + 55] - 10: pairs.setdefault(a, []).append(b)
shade_of = {k: max(set(v), key=v.count) for k, v in pairs.items()}
wall_lit = np.median(lum2[236:240, 56:110])
in_shadow = [x for x in range(0, 110) if lum2[236:240, x].mean() < wall_lit - 15]
run = lit.copy()
for x in in_shadow:
    for yy in range(run.shape[0]):
        k = tuple(run[yy, x]); run[yy, x] = shade_of.get(k, (np.array(k) * 0.72).astype(np.uint8))
tall = np.concatenate([im] + [run] * 3, axis=0)
ter = np.zeros((tall.shape[0], W, 4), np.uint8); ter[..., :3] = tall
ter[:136, :, 3] = 0; ter[136:, :, 3] = 255
Image.fromarray(fl).save(f'{OUT}/pilot_far.png')
Image.fromarray(back).save(f'{OUT}/pilot_back.png')
Image.fromarray(ter).save(f'{OUT}/pilot_terrain.png')
print(f'pilot_far {W}x{FH}, pilot_back 320x240, pilot_terrain 320x{tall.shape[0]}')
