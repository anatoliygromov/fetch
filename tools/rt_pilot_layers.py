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
storey = im[198:240]
tall = np.concatenate([im] + [storey] * 3, axis=0)
ter = np.zeros((tall.shape[0], W, 4), np.uint8); ter[..., :3] = tall
ter[:136, :, 3] = 0; ter[136:, :, 3] = 255
Image.fromarray(fl).save(f'{OUT}/pilot_far.png')
Image.fromarray(back).save(f'{OUT}/pilot_back.png')
Image.fromarray(ter).save(f'{OUT}/pilot_terrain.png')
print(f'pilot_far {W}x{FH}, pilot_back 320x240, pilot_terrain 320x{tall.shape[0]}')
