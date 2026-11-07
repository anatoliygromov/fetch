#!/usr/bin/env python3
"""fix_car5_n07.py [--check]: road_car5 (the silver estate), fix by rule (owner, board 7 Nov: "Wheels need some work").
Only the wheels change: the 5 Nov wheels were lumpy (a ragged tyre edge, a flat hubcap with a smeared diagonal). Each
is replaced by the family's built wheel (tools/build_cars_n07.py wheel(), R 19, the same as the estate road_car1),
stamped at the old axle centres (43, 69) and (194, 69), with a 1 px ink ring; the old tyre's pixels outside the new
ring become the dark wheel well above the sill (row 76) and transparent below it. Every changed pixel is listed in
art/source/road_car5/edits.json; the source is the 5 Nov file from git (origin/main), so the fix is repeatable."""
import json, os, subprocess, sys, io
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_cars_n07 as B, aseprite_io

P = 'riverwalk/art/scene/road_car5.png'
BASE = '5f30120'                     # main at the start of day/07nov-chars: the 5 Nov car
CENTRES, R, SILL = [(43, 69), (194, 69)], 19, 76


def build():
    src = np.array(Image.open(io.BytesIO(subprocess.check_output(['git', 'show', f'{BASE}:{P}']))).convert('RGBA'))
    a = src.copy(); H, W = a.shape[:2]
    wa, wm = B.wheel(R)
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy in CENTRES:
        r = np.hypot(xx - cx, yy - cy)
        old = (r <= R + 3.5) & (a[..., 3] > 0) & (a[..., :3].astype(int).sum(-1) < 200)   # the old tyre's dark pixels
        a[old & (r > R + 1.5) & (yy > SILL)] = 0
        a[old & (r > R + 1.5) & (yy <= SILL)] = (*B.WELL, 255)
        ring = (r <= R + 1.3) & ~(r <= R + 0.3) & ((yy > SILL) | (a[..., 3] == 0) | old)
        a[ring] = (*B.INK, 255)
        ys, xs = np.nonzero(wm)
        a[ys + cy - R, xs + cx - R, :3] = wa[ys, xs]; a[ys + cy - R, xs + cx - R, 3] = 255
    # the wheel's colours snapped to the nearest colour the 5 Nov car already has (asset_qa: 20 colours at most)
    pal = np.unique(src[src[..., 3] > 0][:, :3], axis=0).astype(int)
    m = a[..., 3] > 0
    for col in np.unique(a[m][:, :3], axis=0):
        if not (pal == col).all(1).any():
            near = pal[np.argmin(((pal - col.astype(int)) ** 2).sum(1))]
            a[m & np.all(a[..., :3] == col, -1), :3] = near
    return src, a


if __name__ == '__main__':
    src, a = build()
    if '--check' in sys.argv:
        ok = np.array_equal(np.array(Image.open(P).convert('RGBA')), a); print('road_car5', 'OK' if ok else 'DIFFERS'); sys.exit(0 if ok else 1)
    ch = np.argwhere(np.any(src != a, axis=-1))
    os.makedirs('art/source/road_car5', exist_ok=True)
    json.dump({'why': 'owner 7 Nov: wheels need some work; the built family wheel stamped at both axles',
               'tool': 'tools/fix_car5_n07.py', 'changed': [[int(x), int(y), [int(v) for v in src[y, x]], [int(v) for v in a[y, x]]] for y, x in ch]},
              open('art/source/road_car5/edits.json', 'w'))
    Image.fromarray(a).save(P); aseprite_io.write('art/source/road_car5/road_car5.aseprite', [a])
    print(P, len(ch), 'pixels changed')
