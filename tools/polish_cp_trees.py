#!/usr/bin/env python3
"""polish_cp_trees.py NAME [NAME ...]: the polish step (docs/WORKFLOW.md step 7) for the City Park sample-screen trees,
5 Nov 2026. Every pixel it changes is listed in art/source/NAME/edits.json (x, y, from, to, why), the result is saved
as the .aseprite source (tools/aseprite_io.py) and exported to the slot png. Three defects, found at 5x:
  glint   a lone pixel (none of its 8 neighbours shares its colour) more than 60 luma off the colour most of its
          neighbours have: the bright orange specks in the oak's bark, dark dots in a leaf clump. It takes that colour.
  spike   a silhouette pixel with at most one opaque 4-neighbour (a 1 px whisker on the crown's edge): removed.
  pinhole a transparent pixel with all four 4-neighbours opaque (a 1 px sky hole): the neighbours' majority colour.
Runs on the cut (riverwalk/art/scene/NAME.png as tools/cut_cp_tree.py wrote it) once; the cut is kept as
art/source/NAME/NAME_clean.png so the polish can be rerun from it."""
import sys, os, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

LUM = np.array([0.299, 0.587, 0.114])
for name in sys.argv[1:]:
    src = f'art/source/{name}/{name}_clean.png'
    if not os.path.exists(src): shutil.copy(f'riverwalk/art/scene/{name}.png', src)
    a = np.array(Image.open(src).convert('RGBA'))
    H, W = a.shape[:2]
    rgb = a[..., :3].astype(int); al = a[..., 3] > 0
    edits = []
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    key = np.where(al, key, -1)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not al[y, x]: continue
            nb = key[y - 1:y + 2, x - 1:x + 2].ravel(); nb = np.delete(nb, 4)
            if (nb == key[y, x]).any() or (nb < 0).sum() > 2: continue
            vals, cnt = np.unique(nb[nb >= 0], return_counts=True)
            o = int(vals[cnt.argmax()]); oc = np.array([(o >> 16) & 255, (o >> 8) & 255, o & 255])
            if abs(oc @ LUM - rgb[y, x] @ LUM) > 60:
                edits.append({'x': x, 'y': y, 'from': rgb[y, x].tolist(), 'to': oc.tolist(), 'why': 'glint'})
    for e in edits: rgb[e['y'], e['x']] = e['to']
    pa = np.pad(al, 1)
    n4 = pa[:-2, 1:-1].astype(int) + pa[2:, 1:-1] + pa[1:-1, :-2] + pa[1:-1, 2:]
    sp = al & (n4 <= 1); sp[H - 1, :] = False
    for y, x in zip(*np.nonzero(sp)):
        edits.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist(), 'to': None, 'why': 'spike'}); al[y, x] = False
    pa = np.pad(al, 1)
    n4 = pa[:-2, 1:-1].astype(int) + pa[2:, 1:-1] + pa[1:-1, :-2] + pa[1:-1, 2:]
    for y, x in zip(*np.nonzero(~al & (n4 == 4))):
        nbs = [tuple(rgb[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))]
        c = max(set(nbs), key=nbs.count)
        edits.append({'x': int(x), 'y': int(y), 'from': None, 'to': list(map(int, c)), 'why': 'pinhole'})
        rgb[y, x] = c; al[y, x] = True
    out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); out[~al] = 0
    os.makedirs(f'art/source/{name}', exist_ok=True)
    json.dump({'name': name, 'from': src, 'edits': edits}, open(f'art/source/{name}/edits.json', 'w'), indent=0)
    aseprite_io.write(f'art/source/{name}/{name}.aseprite', [out], layer=name)
    Image.fromarray(out, 'RGBA').save(f'riverwalk/art/scene/{name}.png')
    k = {w: sum(1 for e in edits if e['why'] == w) for w in ('glint', 'spike', 'pinhole')}
    print(name, f'{W}x{H}', k, 'colours', len(np.unique(out[al][:, :3], axis=0)))
