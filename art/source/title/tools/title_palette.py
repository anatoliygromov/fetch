"""Palette for the title: k-means in Lab, done in two groups so Pepper keeps her ramps. Pepper's coat is near black
with a cool sheen; one k-means over the whole picture spends almost nothing on those darks. So the dark coat and
the bandana / tongue / eye pixels (Pepper's box, dark or pink) get their own clusters (K_PEP), everything else the
rest (K_REST). Each pixel then takes its nearest palette colour in Lab, and a lone pixel whose colour is close
(dE < 12) to the colour most of its 8 neighbours share takes that colour (no dithering, no new colours)."""
import numpy as np
from skimage.color import rgb2lab
from sklearn.cluster import KMeans

def pepper_mask(img):
    H, W, _ = img.shape
    lab = rgb2lab(img / 255.0)
    yy, xx = np.mgrid[0:H, 0:W]
    box = (xx < 160) & (yy > 76)
    dark = lab[..., 0] < 30
    pink = (lab[..., 1] > 25) & (img[..., 0] > img[..., 2])
    return box & (dark | pink)

def build(img, k_pep=22, k_rest=40, seed=1):
    lab = rgb2lab(img / 255.0)
    m = pepper_mask(img)
    pal = []
    for sel, k in ((m, k_pep), (~m, k_rest)):
        X = lab[sel]; R = img[sel]
        km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(X)
        for c in range(k):
            pal.append(R[km.labels_ == c].mean(0))
    pal = np.unique(np.array(pal).round().astype(np.uint8), axis=0)
    return pal

def apply(img, pal, despeckle=2, de=12.0):
    lab = rgb2lab(img / 255.0); plab = rgb2lab(pal[None].astype(float) / 255.0)[0]
    d = ((lab[..., None, :] - plab[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    H, W = idx.shape
    for _ in range(despeckle):
        out = idx.copy()
        for y in range(H):
            for x in range(W):
                c = idx[y, x]
                nb = idx[max(0, y - 1):y + 2, max(0, x - 1):x + 2].ravel()
                same = (nb == c).sum() - 1
                if same == 0:
                    vals, cnt = np.unique(nb[nb != c], return_counts=True)
                    v = vals[cnt.argmax()]
                    if cnt.max() >= 4 and np.linalg.norm(plab[c] - plab[v]) < de: out[y, x] = v
        idx = out
    return idx

def nearest(img, pal):
    lab = rgb2lab(img / 255.0); plab = rgb2lab(pal[None].astype(float) / 255.0)[0]
    return ((lab[..., None, :] - plab[None, None]) ** 2).sum(-1).argmin(-1)
