# Builds the quay railing from the SpriteCook railing (source_scenery/railing_spritecook.png, asset
# 2b178488-3a25-46dd-b8b8-29b44b50dc5d): crop to the railing (88x28), then an 8-colour palette (k-means in Lab;
# the source has 289 near-identical blacks and navies). Written as two pieces for tiling:
#   rail_seg.png  the left post and the span after it (columns 0-81), repeated along the railing
#   rail_end.png  the right post (columns 82-87), closing the railing
# Rows: post caps 0-3, handrail 7-9 (its top, row 7, is where Pepper stands), balusters, bottom rail 23-25.
import os, numpy as np
from PIL import Image
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = np.array(Image.open(os.path.join(ROOT, 'source_scenery', 'railing_spritecook.png')).convert('RGBA'))
ys, xs = np.nonzero(a[..., 3])
a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
op = a[..., 3] > 0
lab = rgb2lab(a[..., :3] / 255.0)
km = KMeans(n_clusters=8, n_init=6, random_state=1).fit(lab[op])
pal = np.array([a[..., :3][op][km.labels_ == k].mean(0) for k in range(8)]).round().astype(np.uint8)
# a neutral grey cluster (r = g = b) is noise on a few balusters: it takes the iron colour of the balusters
grey = [k for k in range(8) if abs(int(pal[k][0]) - int(pal[k][2])) < 6 and pal[k][0] > 60]
iron = min(range(8), key=lambda k: abs(int(pal[k].sum()) - (33 + 39 + 58)))
lab_k = km.labels_.copy()
for k in grey: lab_k[lab_k == k] = iron
km.labels_ = lab_k
out = np.zeros_like(a)
out[op, :3] = pal[km.labels_]; out[op, 3] = 255
D = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
Image.fromarray(out[:, :82]).save(os.path.join(D, 'rail_seg.png'))
Image.fromarray(out[:, 82:]).save(os.path.join(D, 'rail_end.png'))
print('railing', out.shape[1], 'x', out.shape[0], 'palette', [tuple(c) for c in pal])
