#!/usr/bin/env python3
"""art/source/town_tub/build_tub.py: the Downtown flower tub with a clipped box shrub (art/dt-props-06nov).

The tub (the old file's rows 18-45, = the TUB box 32 x 28) is kept pixel for pixel. Its 17 px sprig was "super small";
the shrub is cut 1:1 from SpriteCook Pixel Engine Image render art/gen/renders/town_tub_r1a.png (drawn at exactly
32 x 51, no resampling): its rows 0-22 (the ball above its own tub's rim) go on top of the old tub. Clean pass on the
new cut only: its pure black ink becomes the tub's ink, three rare greens (17 px in all) join their nearest ramp
shade. Every pixel that differs from the old file is in edits.json.

  python3 -I art/source/town_tub/build_tub.py      writes riverwalk/art/scene/town_tub.png (32 x 51), the
                                                   .aseprite source and edits.json
"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import aseprite_io

old = np.array(Image.open(os.path.join(HERE, 'town_tub_v0.png')).convert('RGBA'))
cut = np.array(Image.open(os.path.join(ROOT, 'art/gen/renders/town_tub_r1a.png')).convert('RGBA'))
INK = tuple(old[18, 0, :3])                                            # the tub's ink (5, 10, 23)
MERGE = {(0, 0, 0): INK, (17, 48, 16): (40, 94, 41), (114, 175, 77): (97, 158, 69), (57, 115, 43): (40, 94, 41)}
SHRUB_ROWS = 23                                                        # cut rows 0-22: the ball over its rim
out = np.zeros((SHRUB_ROWS + 28, 32, 4), np.uint8)
sh = cut[:SHRUB_ROWS].copy()
for y in range(SHRUB_ROWS):
    for x in range(32):
        if sh[y, x, 3]:
            c = tuple(int(v) for v in sh[y, x, :3]); sh[y, x, :3] = MERGE.get(c, c); sh[y, x, 3] = 255
out[:SHRUB_ROWS] = sh
out[SHRUB_ROWS:] = old[18:46]                                          # the tub, unchanged
Image.fromarray(out).save(os.path.join(ROOT, 'riverwalk/art/scene/town_tub.png'))
Image.fromarray(cut).save(os.path.join(HERE, 'town_tub_cut.png'))
# edits: every pixel of the new file against the old one placed 5 rows lower (its tub rows line up)
ref = np.zeros_like(out); ref[5:] = old
px = [[x, y, '#%02x%02x%02x%02x' % tuple(int(v) for v in out[y, x])] for y in range(out.shape[0]) for x in range(32)
      if not np.array_equal(out[y, x], ref[y, x])]
json.dump({"asset": "town_tub", "base": "town_tub_v0.png (the old file) placed 5 rows lower; rows 23-50 = its rows 18-45 unchanged",
           "method": "shrub rows 0-22 cut 1:1 from art/gen/renders/town_tub_r1a.png (SpriteCook Pixel Engine Image, 32 x 51); ink and 3 rare greens merged",
           "merge": {str(k): str(v) for k, v in MERGE.items()}, "changed": len(px), "of": int((out[..., 3] > 0).sum()), "pixels": px},
          open(os.path.join(HERE, 'edits.json'), 'w'))
ncol = len({tuple(c) for c in out[out[..., 3] > 0][:, :3].tolist()})
# the cut record (tools/pipeline.py step "cut"): Pixel Engine Image draws at exactly the target size, one image pixel
# per art pixel, so the cut is 1:1 with no grid search; checked here instead of tools/grid_cut.py (which expects a
# render of a blockout frame)
fails = []
if cut.shape[:2] != (51, 32): fails.append(f'render is {cut.shape[1]} x {cut.shape[0]}, not 32 x 51')
if set(np.unique(cut[..., 3]).tolist()) - {0, 255}: fails.append('semi-transparent pixels in the render')
if ncol > 20: fails.append(f'{ncol} colours (play cap 20)')
os.makedirs(os.path.join(ROOT, 'art/gen/out'), exist_ok=True)
json.dump({"name": "town_tub", "render": "art/gen/renders/town_tub_r1a.png", "pitch": 1, "method": "1:1, no resampling (Pixel Engine Image at 32 x 51)",
           "size": [32, int(out.shape[0])], "colours": ncol, "fails": fails}, open(os.path.join(ROOT, 'art/gen/out/town_tub.cut.json'), 'w'), indent=1)
print('town_tub 32 x', out.shape[0], ncol, 'colours,', len(px), 'pixels changed')
# the polished source (after the cut record: the ink and green merges are the polish on the new cut)
aseprite_io.write(os.path.join(HERE, 'town_tub.aseprite'), [out])
