#!/usr/bin/env python3
"""cut_cp_props.py NAME: cut one City Park prop of the 6 Nov family (cp_props_06nov) from its GPT 2.5 render.

  python3 -I tools/cut_cp_props.py park_hedge [--variant b]      -> art/source/NAME/NAME_cut.png + art/gen/out/NAME.cut.json

The render is GPT 2.5 Sunburst 1K on the 256 px blockout frame, 4 image px per art px; tools/grid4_cut.py has already
put it on its own grid (one colour per cell, majority, never an average; art/gen/renders/JOB_V_grid4.png). Pepper
measures 52 px in it, so it is 1 px = 1 game px and is never resampled. Steps (BIBLE: a clean pass only on a new cut):
 1. key the magenta and its pink fringe; keep only what lies in the piece's window of the blockout frame (Pepper, the
    other piece of a two-piece job and anything outside go); drop specks of 1-4 px
 2. colours: k-means in Lab over the piece (K = the layer's cap less room for the polish); each cluster takes its
    medoid, a real pixel of the render, never an average; one colour per pixel
 3. clean pass on the new cut (tools/cleanpass.py rules: lone pixels into a close majority, 3 passes)
 4. obstacles: the 1 px outline in one ink (the piece's darkest colour); decoration: no ink, every edge pixel darker
    than luma 45 takes the darkest shade of its own colour instead
Every number is in the cut json. The polish (fit to the slot, hand edits) is tools/polish_cp_props.py."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_palette import lab
import cleanpass

LUM = np.array([0.299, 0.587, 0.114])
# name: job, default variant, window in the 256 frame (x0, y0, x1, y1 inclusive, from the blockout json, padded),
#       K colours, outline (obstacle) or not (decoration), target size
SPEC = {
    'park_hedge':       ('cp_hedge',    'b', (100, 150, 185, 240), 16, True,  (64, 72)),
    'park_leaves':      ('cp_leaves',   'a', (92, 200, 155, 240), 8, False, (48, 22)),
    'park_leaves_flat': ('cp_leaves',   'a', (165, 220, 240, 240), 8, False, (54, 9)),
    'park_stone':       ('cp_rocklog',  'a', (92, 170, 135, 240), 12, True,  (26, 55)),
    'park_hollowlog':   ('cp_rocklog',  'a', (150, 195, 245, 240), 12, True,  (44, 27)),
    'park_boat_front':  ('cp_duckboat', 'a', (100, 190, 175, 240), 14, True,  (54, 33)),
}


def medoid_kmeans(px, k, seed=7):
    """k-means in Lab; every cluster's colour is the real pixel nearest its centre (a medoid, not an average)."""
    L = lab(px.astype(float))
    np.random.seed(seed)
    cen, lab_ = kmeans2(L, min(k, len(np.unique(px, axis=0))), minit='++', iter=30, seed=seed)
    out = np.zeros_like(px)
    for c in np.unique(lab_):
        m = lab_ == c
        d = ((L[m] - cen[c]) ** 2).sum(1)
        out[m] = px[m][d.argmin()]
    return out


def cut(name, variant=None):
    job, v0, win, K, outline, target = SPEC[name]
    v = variant or v0
    src = f'art/gen/renders/{job}_{"r1" if job == "cp_hedge" else ""}{v}_grid4.png'
    a = np.array(Image.open(src).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fg = ~((r - g > 35) & (b - g > 35) & (r > 120) & (b > 120))
    fg &= ~((r - g > 40) & (b - g > 40))
    x0, y0, x1, y1 = win
    w = np.zeros_like(fg); w[y0:y1 + 1, x0:x1 + 1] = True
    fg &= w
    lab_, n = ndimage.label(fg, structure=np.ones((3, 3)))
    sizes = ndimage.sum(fg, lab_, range(1, n + 1))
    specks = 0
    for i, s in enumerate(sizes, 1):
        if s <= 4: fg[lab_ == i] = False; specks += 1
    ys, xs = np.nonzero(fg)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    rgb = a[by0:by1 + 1, bx0:bx1 + 1].copy(); al = fg[by0:by1 + 1, bx0:bx1 + 1]
    n_in = len(np.unique(rgb[al], axis=0))
    rgb[al] = medoid_kmeans(rgb[al], K)
    rgb = rgb.astype(np.uint8)
    rgb, changed = cleanpass.clean(rgb, al, 60, False)
    lum = rgb.astype(float) @ LUM
    pa = np.pad(al, 1)
    edge = al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
    cols = np.unique(rgb[al], axis=0); cl = cols.astype(float) @ LUM
    if outline:
        ink = cols[cl.argmin()]
        fix = edge.copy()
        bottom = np.zeros_like(al);
        rgb[fix] = ink
    else:
        dark = cols[cl < 45]
        floor = cols[cl >= 45][np.argmin(cl[cl >= 45])] if (cl >= 45).any() else cols[cl.argmax()]
        fix = edge & (lum < 45)
        rgb[fix] = floor
        ink = None
    out = np.dstack([rgb, (al * 255).astype(np.uint8)])
    os.makedirs(f'art/source/{name}', exist_ok=True); os.makedirs('art/gen/out', exist_ok=True)
    Image.fromarray(out).save(f'art/source/{name}/{name}_cut.png')
    info = {'name': name, 'render': src, 'variant': v, 'window': win, 'bbox_in_frame': [int(bx0), int(by0), int(bx1), int(by1)],
            'size': [int(bx1 - bx0 + 1), int(by1 - by0 + 1)], 'target': list(target), 'colours_in': int(n_in),
            'colours': int(len(np.unique(rgb[al], axis=0))), 'specks_dropped': int(specks), 'clean_changed': int(changed),
            'outline': bool(outline), 'ink': None if ink is None else [int(c) for c in ink], 'edge_recoloured': int(fix.sum()),
            'lone_pct': round(float(cleanpass.lone_pct(rgb, al)), 2), 'fails': []}
    if abs(info['size'][0] - target[0]) > 3 or abs(info['size'][1] - target[1]) > 6:
        info['fails'].append(f"size {info['size']} vs target {list(target)}")
    json.dump(info, open(f'art/gen/out/{name}.cut.json', 'w'), indent=1)
    print(name, v, 'size', info['size'], 'target', list(target), 'colours', n_in, '->', info['colours'],
          'lone', info['lone_pct'], '%', 'fails', info['fails'])
    return info


if __name__ == '__main__':
    args = sys.argv[1:]
    var = args[args.index('--variant') + 1] if '--variant' in args else None
    names = [x for x in args if x in SPEC] or list(SPEC)
    for nm in names: cut(nm, var)
