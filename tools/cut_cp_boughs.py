#!/usr/bin/env python3
"""cut_cp_boughs.py [--variant a] [--bark K] [--leaf K] [--mode N]: stage 1 of the City Park climbing parts (6 Nov,
family cp_boughs_06nov). The render (GPT 2.5 Sunburst 2K on the 512 blockout art/gen/blockouts/cp_boughs.png) is cut
1:1 on its own 4 px grid by tools/grid4_cut.py (one real pixel per cell, never an average); this script works on that
cut and never resamples:
 1. key the magenta (and the magenta fringe), drop Pepper (the scale reference, bottom left);
 2. material per pixel: 16 colour clusters in Lab, each cluster leaf or bark by where most of its pixels lie in the
    blockout's key (light grey ovals = leaves; dark grey, mid grey, near-white = bark, nest, cut top);
 3. colours: each material clustered again in Lab (k-means; bark --bark, default 5; leaves --leaf, default 5), every
    pixel takes its cluster's colour (a real mean of one cluster, one colour per pixel); then --mode passes of a 3x3
    majority on each material's labels (the oak re-cut's rule: mottling joins its clump, only the material's own
    colours);
 4. clean pass on this new cut only (BIBLE): holes of up to 6 px filled by their commonest neighbour, specks of 1-4
    px dropped.
Out: art/source/cp_boughs/sheet_cut.png (RGBA, 512 x 512, on the blockout's coordinates), sheet_leaf.png (the leaf
mask), art/gen/out/cp_boughs.cut.json (palette, counts). Stage 2 (tools/build_cp_boughs.py) cuts the parts out."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
sys.path.insert(0, 'tools')
from make_palette import lab

A = sys.argv[1:]
def opt(n, d): return type(d)(A[A.index(n) + 1]) if n in A else d
V, KB, KL, MODE = opt('--variant', 'a'), opt('--bark', 5), opt('--leaf', 5), opt('--mode', 2)
OUT = 'art/source/cp_boughs'; os.makedirs(OUT, exist_ok=True)
LUM = np.array([0.299, 0.587, 0.114])
a = np.array(Image.open(f'art/gen/renders/cp_boughs_{V}_grid4.png').convert('RGB')).astype(int)
bo = np.array(Image.open('art/gen/blockouts/cp_boughs.png').convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
fg = ~((r - g > 35) & (b - g > 35) & (r > 120) & (b > 120)) & ~((r - g > 40) & (b - g > 40))
fg[440:, :68] = False                                              # Pepper
lb, n = ndimage.label(fg, structure=np.ones((3, 3)))
sz = ndimage.sum(fg, lb, range(1, n + 1))
for i, s in enumerate(sz, 1):
    if s <= 4: fg[lb == i] = False
# 2. material
key_leaf = (np.abs(bo - [180, 180, 185]).sum(-1) < 6)
key_bark = (np.abs(bo - [95, 95, 100]).sum(-1) < 6) | (np.abs(bo - [140, 140, 145]).sum(-1) < 6) | (np.abs(bo - [215, 215, 215]).sum(-1) < 6)
near_leaf = ndimage.binary_dilation(key_leaf, iterations=6)
near_bark = ndimage.binary_dilation(key_bark, iterations=3)
px = a[fg].astype(float); L = lab(px)
_, l16 = kmeans2(L, 16, minit='++', iter=60, seed=7)
leafc = []
for j in range(16):
    s = l16 == j
    if not s.any(): continue
    inl = near_leaf[fg][s] & ~near_bark[fg][s]; inb = near_bark[fg][s] & ~near_leaf[fg][s]
    if inl.sum() > inb.sum(): leafc.append(j)
leaf = np.zeros_like(fg); leaf[fg] = np.isin(l16, leafc)
# a leaf-coloured pixel well inside a bark shape is a lit bark streak; a bark-coloured pixel well inside an oval is a
# twig or a gap in the clump: both keep their own cluster's material (no rule needed beyond the clusters)
bark = fg & ~leaf
# 3. colours per material
rgb = a.copy()
pal = {}
for nm, sel, k in (('leaf', leaf, KL), ('bark', bark, KB)):
    P = a[sel].astype(float)
    _, lk = kmeans2(lab(P), k, minit='++', iter=80, seed=7)
    cols = np.array([P[lk == j].mean(0) if (lk == j).any() else [0, 0, 0] for j in range(k)])
    cols = np.rint(cols).astype(int)
    rgb[sel] = cols[lk]
    pal[nm] = sorted([list(map(int, c)) for c in cols], key=lambda c: c[0] * .299 + c[1] * .587 + c[2] * .114)
if MODE:
    from scipy.ndimage import generic_filter
    for sel in (leaf, bark):
        key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
        key = np.where(sel, key, -1)
        def maj(v):
            c = int(v[4])
            if c < 0: return c
            u, cnt = np.unique(v[v >= 0], return_counts=True)
            return int(u[cnt.argmax()]) if cnt.max() >= 5 else c
        for _ in range(MODE):
            key = generic_filter(key, maj, size=3, mode='constant', cval=-1)
        k2 = key[sel]
        rgb[sel] = np.stack([(k2 >> 16) & 255, (k2 >> 8) & 255, k2 & 255], -1)
# 4. holes and specks (this new cut only)
holes = ~fg & ndimage.binary_fill_holes(fg)
hl, n = ndimage.label(holes)
for i in range(1, n + 1):
    comp = hl == i
    if comp.sum() > 6: continue
    ring = ndimage.binary_dilation(comp) & fg
    cols, cnt = np.unique(rgb[ring], axis=0, return_counts=True)
    rgb[comp] = cols[cnt.argmax()]; fg |= comp
    leaf[comp] = leaf[ring].mean() > 0.5
im = np.dstack([rgb, np.where(fg, 255, 0)]).astype(np.uint8); im[~fg] = 0
Image.fromarray(im, 'RGBA').save(f'{OUT}/sheet_cut.png')
Image.fromarray((leaf & fg).astype(np.uint8) * 255).save(f'{OUT}/sheet_leaf.png')
J = {'name': 'cp_boughs', 'render': f'art/gen/renders/cp_boughs_{V}_raw.png', 'grid': f'art/gen/renders/cp_boughs_{V}_grid4.png',
     'cut_by': f'tools/grid4_cut.py then tools/cut_cp_boughs.py {" ".join(A)} (1:1 on the render grid, no resampling)',
     'palette': pal, 'colours': int(len(np.unique(im[fg][:, :3], axis=0))), 'fails': []}
os.makedirs('art/gen/out', exist_ok=True)
json.dump(J, open('art/gen/out/cp_boughs.cut.json', 'w'), indent=1)
print(json.dumps(pal), J['colours'])
