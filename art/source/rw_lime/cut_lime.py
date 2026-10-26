"""Cut the River Walk lime from its SpriteCook render (retry 1, variant b, 256x256, already 1 px = 1 game px).
Never resampled: magenta keyed, Pepper (the scale reference, the small shapes in the bottom left) dropped.
Materials: a pixel is leaf or bark by the hue of its 3x3 neighbourhood (used only to classify, never as a colour), so
the render's near-black ink on the crown's rim counts as leaf and the ink on the trunk's edge as bark.
Colours: each material's pixels are clustered in Lab (k-means: leaves 5, bark 4) and every pixel takes its cluster's
colour: one colour per pixel, nothing blended between pixels. The darkest leaf shade is pulled half way to neutral
(the art direction: darkest shade a neutral dark).
Out: art/source/rw_lime/rw_lime_cut.png (1x RGBA, 256 px canvas cropped to the tree) and the measures."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
sys.path.insert(0, 'tools')
from make_palette import lab

SRC = 'art/gen/renders/rw_lime_r1b.png'
a = np.array(Image.open(SRC).convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
fg = ~((r - g > 35) & (b - g > 35) & (r > 120) & (b > 120))
lbl, n = ndimage.label(fg)
tree = np.zeros_like(fg)
for i in range(1, n + 1):
    comp = lbl == i
    ys, xs = np.nonzero(comp)
    if xs.max() < 60 and ys.min() > 190: continue           # Pepper, bottom left
    tree |= comp
# classify by the neighbourhood's hue (opaque neighbours only)
w = ndimage.uniform_filter(tree.astype(float), 5)
mr = ndimage.uniform_filter(np.where(tree, r, 0).astype(float), 5) / np.maximum(w, 1e-6)
mg = ndimage.uniform_filter(np.where(tree, g, 0).astype(float), 5) / np.maximum(w, 1e-6)
leaf = tree & ((mg - mr > 8) | (g - r > 10))
bark = tree & ~leaf
px = a.reshape(-1, 3).astype(float); L = lab(px)
rgb = a.reshape(-1, 3).copy()
for sel, k in ((leaf.reshape(-1), 5), (bark.reshape(-1), 4)):
    cent, lab_ = kmeans2(L[sel], k, minit='++', iter=60, seed=7)
    cols = np.array([px[sel][lab_ == j].mean(0) if (lab_ == j).any() else [0, 0, 0] for j in range(k)])
    if sel is not None and k == 5:                           # darkest leaf: half way to neutral
        d = np.argmin(cols @ [0.299, 0.587, 0.114]); m = cols[d].mean(); cols[d] = (cols[d] + m) / 2
    rgb[sel] = np.rint(cols[lab_]).astype(int)
rgb = rgb.reshape(a.shape).astype(np.uint8)
out = np.dstack([rgb, np.where(tree, 255, 0).astype(np.uint8)])
np.save('/tmp/rw_lime_leafmask.npy', leaf)
ys, xs = np.nonzero(tree)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
im = Image.fromarray(out, 'RGBA').crop(box)
Image.fromarray(leaf[box[1]:box[3], box[0]:box[2]].astype(np.uint8) * 255).save('art/source/rw_lime/rw_lime_leafmask.png')
im.save('art/source/rw_lime/rw_lime_cut.png')
A = np.array(im); al = A[..., 3] > 0
print('size', im.size, 'colours', len(np.unique(A[al][:, :3], axis=0)))
