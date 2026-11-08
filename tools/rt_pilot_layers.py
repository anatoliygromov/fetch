#!/usr/bin/env python3
"""rt_pilot_layers.py DIR OUTDIR: split the finished lock-and-complete screen (DIR/final.png) into the game's layers
for the Rooftops pilot at the concept's camera spot (x 4224, y 240): pilot_far.png (sky, spire, far town; opaque, run
on down below the near skyline so the slower layer never shows a hole) and pilot_near.png (the back row, wall, ledges,
skylights, lower wall and hotel; transparent where the far layer shows)."""
import sys, numpy as np
from PIL import Image
D, OUT = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(f'{D}/final.png').convert('RGB'))
far = np.load(f'{D}/far.npy'); H, W = far.shape
line = np.array([np.nonzero(~far[:, x])[0].min() for x in range(W)])
deep = min(H, line.max() + 32)
fl = np.zeros((deep, W, 4), np.uint8); fl[..., 3] = 255
for x in range(W):
    s = line[x]; fl[:s, x, :3] = im[:s, x]; fl[s:, x, :3] = im[max(0, s - 1), x]
near = np.zeros((H, W, 4), np.uint8); near[..., :3] = im; near[..., 3] = np.where(far, 0, 255)
Image.fromarray(fl).save(f'{OUT}/pilot_far.png'); Image.fromarray(near).save(f'{OUT}/pilot_near.png')
print(f'pilot_far 320x{deep}, pilot_near 320x240 (far skyline rows {line.min()}-{line.max()})')
