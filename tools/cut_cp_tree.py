#!/usr/bin/env python3
"""cut_cp_tree.py RENDER NAME [--leaf K] [--bark K] [--rim-lum L] [--bark-box x0,y0,x1,y1] [--mode N]: cut a City Park tree from its SpriteCook render
(5 Nov 2026, the City Park sample screen). The River Walk lime's method (art/source/rw_lime/cut_lime.py and
clean_lime.py), made one script for every tree of the family.

The render is already on its own grid, 1 px = 1 game px (SpriteCook pixel mode; Pepper measures 52 px in it), so it
is never resampled. Steps:
 1. key the magenta; drop Pepper (the scale reference in the bottom left) and anything not joined to the tree
 2. leaf or bark per pixel by the hue of its 5x5 neighbourhood (used only to classify, never as a colour)
 3. colours: each material clustered in Lab (k-means; leaves --leaf, default 6; bark --bark, default 4) and every pixel
    takes its cluster's colour, one colour per pixel; the darkest leaf shade pulled half way to neutral (art
    direction: the darkest shade a neutral dark)
 4. clean pass on the new cut only (BIBLE): holes up to 30 px take their most common neighbour, specks of 1-4 px
    go, lone pixels (tools/cleanpass.py, 3 passes) and blotches (asset_qa's rule) merge into their fill
 5. no outline (decoration): silhouette pixels facing the sun (open above or left) take the leaf mid-light shade, the
    others the leaf mid shade; the trunk's edge the same in the bark ramp
Out: art/source/NAME/NAME_cut.png (after step 3), NAME_leafmask.png, riverwalk/art/scene/NAME.png (after 5) and
art/gen/out/NAME.cut.json with the measures."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
sys.path.insert(0, 'tools')
from make_palette import lab
import cleanpass

a_ = sys.argv[1:]
SRC, NAME = a_[0], a_[1]
KL = int(a_[a_.index('--leaf') + 1]) if '--leaf' in a_ else 6
KB = int(a_[a_.index('--bark') + 1]) if '--bark' in a_ else 4
RIM = int(a_[a_.index('--rim-lum') + 1]) if '--rim-lum' in a_ else 45   # edge pixels darker than this are an ink rim
OUT = f'art/source/{NAME}'; os.makedirs(OUT, exist_ok=True)
LUM = np.array([0.299, 0.587, 0.114])

a = np.array(Image.open(SRC).convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
H0, W0 = r.shape
fg = ~((r - g > 35) & (b - g > 35) & (r > 120) & (b > 120))
fg &= ~((r - g > 40) & (b - g > 40))                         # magenta fringe mixed into an edge pixel
lbl, n = ndimage.label(fg)
sizes = ndimage.sum(fg, lbl, range(1, n + 1))
tree = lbl == (1 + int(np.argmax(sizes)))                   # the tree is the biggest piece; Pepper and specks go
# 2. classify: leaves are warm (red well over blue) and bright; bark is brown-grey, limbs dark
w = ndimage.uniform_filter(tree.astype(float), 5)
def mean(ch): return ndimage.uniform_filter(np.where(tree, ch, 0).astype(float), 5) / np.maximum(w, 1e-6)
mr, mg, mb = mean(r), mean(g), mean(b)
sat = (np.maximum(np.maximum(mr, mg), mb) - np.minimum(np.minimum(mr, mg), mb))
leaf = tree & (sat > 70) & (mr - mb > 60)
for _i, _v in enumerate(a_):                                       # (5 Nov, round 3) the trunk under the crown is bark,
    if _v == '--bark-box':                                           # whatever its lit orange streaks say (repeatable)
        bx0, by0, bx1, by1 = map(int, a_[_i + 1].split(','))
        leaf[by0:by1 + 1, bx0:bx1 + 1] = False
bark = tree & ~leaf
# 3. colours per material
px = a.reshape(-1, 3).astype(float); L = lab(px)
rgb = a.reshape(-1, 3).copy()
for sel, k in ((leaf.reshape(-1), KL), (bark.reshape(-1), KB)):
    if sel.sum() < k: continue
    cent, lab_ = kmeans2(L[sel], k, minit='++', iter=60, seed=7)
    cols = np.array([px[sel][lab_ == j].mean(0) if (lab_ == j).any() else [0, 0, 0] for j in range(k)])
    if k == KL:
        d = np.argmin(cols @ LUM); m = cols[d].mean(); cols[d] = (cols[d] + m) / 2
        for j in range(k):                                           # a pink cluster is magenta fringe: nearest leaf colour
            if cols[j][2] - cols[j][1] > 10 and cols[j][0] > 150:
                o = [i for i in range(k) if i != j]
                cols[j] = cols[o[int(np.argmin([((cols[i] - cols[j]) ** 2).sum() for i in o]))]]
    rgb[sel] = np.rint(cols[lab_]).astype(int)
rgb = rgb.reshape(a.shape)
MODE = int(a_[a_.index('--mode') + 1]) if '--mode' in a_ else 0
if MODE:                                                             # (5 Nov, oak re-cut) a 3x3 majority on the cluster
    from scipy.ndimage import generic_filter                         # labels of each material, MODE passes: ragged fields
    for sel in (leaf, bark):                                         # and 1-3 px islands join their clump. It only picks
        key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]  # among the material's own colours (no averaging)
        key = np.where(sel, key, -1)
        def maj(v):
            c = int(v[4])
            if c < 0: return c
            u, n = np.unique(v[v >= 0], return_counts=True)
            m = u[n.argmax()]
            return int(m) if n.max() >= 5 else c
        for _ in range(MODE):
            key = generic_filter(key, maj, size=3, mode='constant', cval=-1)
        k2 = key[sel]
        rgb[sel] = np.stack([(k2 >> 16) & 255, (k2 >> 8) & 255, k2 & 255], -1)
ys, xs = np.nonzero(tree)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
rgb = rgb[box[1]:box[3], box[0]:box[2]]; al = tree[box[1]:box[3], box[0]:box[2]].copy()
leaf = leaf[box[1]:box[3], box[0]:box[2]].copy()
cut = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); cut[~al] = 0
Image.fromarray(cut, 'RGBA').save(f'{OUT}/{NAME}_cut.png')
Image.fromarray(leaf.astype(np.uint8) * 255).save(f'{OUT}/{NAME}_leafmask.png')
H, W = al.shape
def ramp(mask):
    cols = np.unique(rgb[mask & al], axis=0)
    return cols[np.argsort(cols @ LUM)]
LR, BR = ramp(leaf), ramp(~leaf)
# 4. holes, specks
holes = ~al & ndimage.binary_fill_holes(al)
lb, n = ndimage.label(holes)
for i in range(1, n + 1):
    comp = lb == i
    if comp.sum() > 30: continue
    ring = ndimage.binary_dilation(comp) & al
    cols, cnt = np.unique(rgb[ring], axis=0, return_counts=True)
    rgb[comp] = cols[cnt.argmax()]; al |= comp
    leaf |= comp & (ndimage.binary_dilation(comp, iterations=2) & leaf).any()
lb, n = ndimage.label(al, structure=np.ones((3, 3)))
sz = ndimage.sum(al, lb, range(1, n + 1))
for i, s in enumerate(sz, 1):
    if s <= 4: al[lb == i] = False
# 5. edges: no outline
pa = np.pad(al, 1)
edge = al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
lit = edge & (~pa[:-2, 1:-1] | ~pa[1:-1, :-2])
shade = edge & ~lit
edge[H - 1, :] = lit[H - 1, :] = shade[H - 1, :] = False
# the render's own edge shading is kept (a light rim under a dark clump reads as a halo, 5 Nov pilot); only an ink
# rim goes: an edge pixel darker than luma 45 takes the most common colour of the opaque inner pixels beside it
inner = al & ~edge
lum = rgb @ LUM
for y, x in zip(*np.nonzero(edge & (lum < RIM))):
    nb = [rgb[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1), (y - 2, x), (y + 2, x), (y, x - 2), (y, x + 2))
          if 0 <= yy < H and 0 <= xx < W and inner[yy, xx] and rgb[yy, xx] @ LUM >= RIM]
    if nb:
        cols, cnt = np.unique(np.array(nb), axis=0, return_counts=True); rgb[y, x] = cols[cnt.argmax()]
out_rgb, changed = cleanpass.clean(rgb.astype(np.uint8), al, 70, False)
out_rgb = out_rgb.astype(int)


def blotch_merge(rgb, al):
    key = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    key = np.where(al, key, -1); n = 0
    for k in np.unique(key[al]):
        lab_, c = ndimage.label(key == k, structure=np.ones((3, 3)))
        sizes = np.bincount(lab_.ravel())
        for i in range(1, c + 1):
            if not (2 <= sizes[i] <= 24): continue
            mm = lab_ == i
            ys_, xs_ = np.nonzero(mm)
            if min(np.ptp(ys_), np.ptp(xs_)) == 0 and max(np.ptp(ys_), np.ptp(xs_)) >= 3: continue
            pm = np.pad(mm, 1)
            ring = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & ~mm
            rk = key[ring]
            if (rk < 0).any(): continue
            vals, cnt = np.unique(rk, return_counts=True)
            if cnt.max() / cnt.sum() < 0.8: continue
            o = int(vals[cnt.argmax()])
            oc = np.array([(o >> 16) & 255, (o >> 8) & 255, o & 255])
            if np.sqrt(((oc - rgb[mm][0]) ** 2).sum()) < 45:
                rgb[mm] = oc; key[mm] = o; n += 1
    return rgb, n


nbt = 0
for _ in range(3):
    out_rgb, nb = blotch_merge(out_rgb, al); nbt += nb
im = np.dstack([out_rgb, np.where(al, 255, 0)]).astype(np.uint8); im[~al] = 0
Image.fromarray(im, 'RGBA').save(f'riverwalk/art/scene/{NAME}.png')
m = im[..., 3] > 0
meas = {}
for d in (20, 50, 80):
    xx = np.nonzero(m[H - 1 - d] & ~leaf[H - 1 - d])[0]
    meas[f'trunk_{d}px_up'] = int(xx.max() - xx.min() + 1) if len(xx) else 0
lf = m & leaf
meas['lowest_leaf_px_up'] = int(H - 1 - np.nonzero(lf)[0].max())
meas['crown_width'] = int(np.ptp(np.nonzero(lf)[1]) + 1)
meas['size'] = [W, H]
meas['colours'] = int(len(np.unique(im[m][:, :3], axis=0)))
meas['top_cut_by_frame'] = bool(box[1] == 0)
J = {'name': NAME, 'size': [W, H], 'render': SRC, 'cut_by': f'tools/cut_cp_tree.py {" ".join(a_)} (1x render, no resampling)',
     'colours_in': meas['colours'], 'measures_px': meas, 'lone_changed': int(changed), 'blotches_merged': nbt, 'fails': []}
json.dump(J, open(f'art/gen/out/{NAME}.cut.json', 'w'), indent=1)
print(json.dumps(meas))
