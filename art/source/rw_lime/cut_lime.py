"""Cut the River Walk lime from its SpriteCook render (retry 1, variant b, 256x256, already 1 px = 1 game px).
Never resampled: magenta keyed, Pepper (the scale reference) dropped as the separate shapes in the bottom-left,
then the render's ~12,700 noise colours mapped to 20 (Pillow max-coverage, no dither, every pixel takes one of the
20, no averaging across pixels). The 20 become the lime ramps of the level palette (art/palettes/riverwalk.gpl v2).
Out: art/source/rw_lime/rw_lime_cut.png (1x RGBA) and the measures."""
import numpy as np
from PIL import Image
from scipy import ndimage
SRC = 'art/gen/renders/rw_lime_r1b.png'
a = np.array(Image.open(SRC).convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
fg = ~((r - g > 35) & (b - g > 35) & (r > 120) & (b > 120))
lbl, n = ndimage.label(fg)
sizes = ndimage.sum(fg, lbl, range(1, n + 1))
tree = lbl == (np.argmax(sizes) + 1)
# small bits in the crown's gaps that are not connected (leaf islands) stay if they sit inside the crown's hull rows
for i in range(1, n + 1):
    comp = lbl == i
    ys, xs = np.nonzero(comp)
    if i == np.argmax(sizes) + 1: continue
    if xs.max() < 60 and ys.min() > 190: continue           # Pepper, bottom left
    tree |= comp
# per material: bark (low chroma or warm) and leaves (green), each to its own ramp by k-means in Lab;
# every pixel then takes its nearest ramp colour (one colour per pixel, nothing blended between pixels)
import sys; sys.path.insert(0, 'tools')
from make_palette import lab
from scipy.cluster.vq import kmeans2
px = a.reshape(-1, 3).astype(float); L = lab(px)
chroma = np.hypot(L[:, 1], L[:, 2]); hue = np.degrees(np.arctan2(L[:, 2], L[:, 1])) % 360
leaf = (hue > 95) & (hue < 200) & (chroma > 12) & tree.reshape(-1)
bark = ~leaf & tree.reshape(-1)
rgb = a.reshape(-1, 3).copy()
np.random.seed(7)
for sel, k in ((leaf, 13), (bark, 7)):
    cent, lab_ = kmeans2(L[sel], k, minit='++', iter=40, seed=7)
    cols = np.array([px[sel][lab_ == j].mean(0) if (lab_ == j).any() else [0, 0, 0] for j in range(k)])
    rgb[sel] = np.rint(cols[lab_]).astype(int)
rgb = rgb.reshape(a.shape).astype(np.uint8)
out = np.dstack([rgb, np.where(tree, 255, 0).astype(np.uint8)])
ys, xs = np.nonzero(tree)
im = Image.fromarray(out, 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
im.save('art/source/rw_lime/rw_lime_cut.png')
A = np.array(im); al = A[..., 3] > 0
print('size', im.size, 'colours', len(np.unique(A[al][:, :3], axis=0)))
H = A.shape[0]
for d in (2, 10, 30, 60, 90):
    xx = np.nonzero(al[H - 1 - d])[0]; print(f'row {d} up: x {xx.min()}..{xx.max()} ({len(xx)} px)')
gr = al & (A[..., 1].astype(int) > A[..., 0].astype(int) + 12)
print('lowest leaf', H - 1 - np.nonzero(gr)[0].max(), 'px above ground')
