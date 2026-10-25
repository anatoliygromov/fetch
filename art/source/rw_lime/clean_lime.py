"""Clean pass on the NEW lime cut, before its hand polish (BIBLE: a clean pass runs only on a new cut).
1. the render's near-black ink (2,7,2) goes: inside the crown it becomes the deepest leaf green, on the trunk the
   deepest bark brown; the two odd violet bark shades become the bark browns next to them in lightness
2. decoration has no outline: silhouette edge pixels that face the light (transparent above or to the left) and are
   darker than luma 70 take the leaf mid green (39,96,17) / bark mid (76,74,63): a lit rim from the upper-left sun;
   the shadow side keeps its dark green, a darker shade of its own colour
3. pinholes (enclosed transparent holes of 1-12 px: small sky holes read as specks) take their most common neighbour; specks (opaque bits of 1-4 px
   free of the body) go
4. lone pixels: tools/cleanpass.py rule (most common 8-neighbour colour when close), 3 passes
Writes riverwalk/art/scene/rw_lime.png and rw_lime_flip.png from art/source/rw_lime/rw_lime_cut.png."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
import cleanpass

a = np.array(Image.open('art/source/rw_lime/rw_lime_cut.png').convert('RGBA'))
rgb = a[..., :3].astype(int); al = a[..., 3] > 0
lum = rgb @ np.array([0.299, 0.587, 0.114])
def is_(c): return al & (rgb == np.array(c)).all(-1)
leafy = al & (rgb[..., 1] > rgb[..., 0] + 15)
near_leaf = ndimage.uniform_filter(leafy.astype(float), 7) > 0.35
ink = is_((2, 7, 2))
rgb[ink & near_leaf] = (7, 40, 23); rgb[ink & ~near_leaf] = (42, 41, 36)
rgb[is_((39, 24, 39))] = (42, 41, 36); rgb[is_((68, 25, 66))] = (62, 60, 53)
lum = rgb @ np.array([0.299, 0.587, 0.114])
pa = np.pad(al, 1)
lit = al & (~pa[:-2, 1:-1] | ~pa[1:-1, :-2])                     # transparent above or left
rows = np.nonzero(al.any(1))[0]; lit[rows.max(), :] = False
leafy = rgb[..., 1] > rgb[..., 0] + 15
m = lit & (lum < 70)
rgb[m & leafy] = (39, 96, 17); rgb[m & ~leafy] = (76, 74, 63)
holes = ~al & ndimage.binary_fill_holes(al)
lbl, n = ndimage.label(holes)
for i in range(1, n + 1):
    comp = lbl == i
    if comp.sum() > 12: continue
    ring = ndimage.binary_dilation(comp) & al
    cols, cnt = np.unique(rgb[ring], axis=0, return_counts=True)
    rgb[comp] = cols[cnt.argmax()]; al = al | comp
lbl, n = ndimage.label(al, structure=np.ones((3, 3)))
sizes = ndimage.sum(al, lbl, range(1, n + 1))
for i, s in enumerate(sizes, 1):
    if s <= 4: al[lbl == i] = False
out_rgb, changed = cleanpass.clean(rgb.astype(np.uint8), al, 70, False)
# 5. blotches (the asset_qa rule): a 2-24 px patch of one colour that sits >= 80 % inside ONE near colour (RGB
#    distance < 45) takes that colour; leaf shapes in a clearly different shade stay
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
    print('blotches merged', nb)
im = np.dstack([out_rgb, np.where(al, 255, 0)]).astype(np.uint8)
im[~al] = 0
Image.fromarray(im, 'RGBA').save('riverwalk/art/scene/rw_lime.png')
Image.fromarray(im, 'RGBA').transpose(Image.FLIP_LEFT_RIGHT).save('riverwalk/art/scene/rw_lime_flip.png')
print('lone pixels changed', changed, 'colours', len(np.unique(im[al][:, :3], axis=0)))
