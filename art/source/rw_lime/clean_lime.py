"""Clean pass on the NEW lime cut, before its hand check (BIBLE: a clean pass runs only on a new cut). Review round 1
fixes (art/gen/reviews/rw_lime.md) are in here, so the file is rebuilt the same way every time.
1. the crown's right side, cut straight by the render frame, is carved into three round leaf clumps (scallops)
2. the root flare becomes a gentle splay, half width 12 to 16 px over its last 14 rows (not four claws)
3. holes inside the body up to 30 px take their most common neighbour colour (small sky holes read as gems);
   specks (opaque bits of 1-4 px free of the body) go
4. no outline (decoration): silhouette pixels of the crown facing the sun (transparent above or left) take the leaf
   mid-light shade, those facing away the leaf mid shade; the trunk's edge the same with the bark ramp.
   The darkest shades stay inside the shapes
5. lone pixels (tools/cleanpass.py rule, 3 passes) and blotches (asset_qa's rule: a 2-24 px patch sitting >= 80 %
   inside one near colour takes that colour)
Writes riverwalk/art/scene/rw_lime.png from art/source/rw_lime/rw_lime_cut.png (+ rw_lime_leafmask.png)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
import cleanpass

a = np.array(Image.open('art/source/rw_lime/rw_lime_cut.png').convert('RGBA'))
leaf = np.array(Image.open('art/source/rw_lime/rw_lime_leafmask.png')) > 0
rgb = a[..., :3].astype(int); al = a[..., 3] > 0
H, W = al.shape
LUM = np.array([0.299, 0.587, 0.114])
def ramp(mask):
    cols = np.unique(rgb[mask & al], axis=0)
    return cols[np.argsort(cols @ LUM)]
LR, BR = ramp(leaf), ramp(~leaf)
if BR[0] @ LUM < 20:                                     # a near-black bark cluster (the render's ink) joins the next shade
    rgb[(rgb == BR[0]).all(-1) & al] = BR[1]; BR = BR[1:]
print('leaf ramp', [tuple(c) for c in LR]); print('bark ramp', [tuple(c) for c in BR])

# 1. carve the frame-cut right side into scallops
rows = np.nonzero(al[:, W - 1])[0]
if len(rows):
    y0, y1 = rows.min(), rows.max()
    n = 3; seg = (y1 - y0 + 1) / n
    for y in range(y0, y1 + 1):
        i = min(n - 1, int((y - y0) / seg)); c = y0 + (i + 0.5) * seg
        t = (y - c) / (seg / 2)
        lim = W - 3 - int(round(9 * t * t))
        al[y, lim + 1:] = False
# 2. root flare
mid = np.nonzero(al[H - 30])[0]; cx = int(round(mid.mean()))
for y in range(H - 14, H):                               # a gentle flare: half width 12 at 14 rows up to 16 at the ground
    hw = 12 + int(round((y - (H - 14)) * 4 / 13))
    al[y, :max(0, cx - hw)] = False; al[y, cx + hw:] = False
for y in (H - 2, H - 1):                                 # the foot stands on the ground: no gaps in its last rows
    xx = np.nonzero(al[y])[0]
    if len(xx):
        gap = ~al[y, xx.min():xx.max() + 1]
        rgb[y, xx.min():xx.max() + 1][gap] = BR[1]; al[y, xx.min():xx.max() + 1] = True
# 3. holes and specks
holes = ~al & ndimage.binary_fill_holes(al)
lbl, n = ndimage.label(holes)
for i in range(1, n + 1):
    comp = lbl == i
    if comp.sum() > 30: continue
    ring = ndimage.binary_dilation(comp) & al
    cols, cnt = np.unique(rgb[ring], axis=0, return_counts=True)
    rgb[comp] = cols[cnt.argmax()]; al |= comp
    leaf |= comp & (ndimage.binary_dilation(comp, iterations=2) & leaf).any()
lbl, n = ndimage.label(al, structure=np.ones((3, 3)))
sizes = ndimage.sum(al, lbl, range(1, n + 1))
for i, s in enumerate(sizes, 1):
    if s <= 4: al[lbl == i] = False
# 4. edges
pa = np.pad(al, 1)
edge = al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
lit = edge & (~pa[:-2, 1:-1] | ~pa[1:-1, :-2])
shade = edge & ~lit
edge[H - 1, :] = False; lit[H - 1, :] = False; shade[H - 1, :] = False
lm, ls = LR[3], LR[2]                                    # lit rim: the leaf mid-light; shade rim: the leaf mid
bm, bs = BR[-1], BR[-2]
rgb[lit & leaf] = lm; rgb[shade & leaf] = ls
rgb[lit & ~leaf] = bm; rgb[shade & ~leaf] = bs
# 5. lone pixels and blotches
out_rgb, changed = cleanpass.clean(rgb.astype(np.uint8), al, 70, False)
def blotch_merge(rgb, al):
    key = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    key = np.where(al, key, -1); n = 0
    for k in np.unique(key[al]):
        lab, c = ndimage.label(key == k, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())
        for i in range(1, c + 1):
            if not (2 <= sizes[i] <= 24): continue
            mm = lab == i
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
            if np.sqrt(((oc - rgb[mm][0].astype(int)) ** 2).sum()) < 45:
                rgb[mm] = oc; key[mm] = o; n += 1
    return rgb, n
for _ in range(3):
    out_rgb, nb = blotch_merge(out_rgb, al)
im = np.dstack([out_rgb, np.where(al, 255, 0)]).astype(np.uint8)
im[~al] = 0
Image.fromarray(im, 'RGBA').save('riverwalk/art/scene/rw_lime.png')
A = im; m = A[..., 3] > 0
print('lone changed', changed, 'colours', len(np.unique(A[m][:, :3], axis=0)), 'size', W, H)
for d in (20, 50, 80):
    xx = np.nonzero(m[H - 1 - d])[0]; print(f'trunk {d} px up: {xx.max() - xx.min() + 1} px')
lf = m & leaf
print('lowest leaf', H - 1 - np.nonzero(lf)[0].max(), 'px above the ground')
