# Real pixels for the title screen (22 Oct): turns the title painting into pixel art on the game's 320x240 grid.
# The old way (a median per cell, then 64 colours) kept the painting's AI texture: noisy fur, random speckle
# "dither", wobbly outlines. Here every pixel is placed by a rule a pixel artist would follow:
#   1. Flat colour areas: the painting averaged per cell, smoothed (edges kept), then 30 colours on the VGA
#      6-bit grid. No colour is used for a single stray pixel: clusters under 4 px join their neighbour.
#   2. Clean outlines: on every strong edge the darker side takes a darker shade of its own colour (sel-out),
#      so silhouettes get one even line. Drawn lines (mouth, wink, ears) come from the painting's dark lines,
#      thinned to 1 px; short scraps are dropped.
#   3. The logo is rebuilt: the letter shapes are cleaned, filled with four bands of yellow to orange joined by
#      a 2x2 checker (the 16-bit way), a light top edge, a dark lower edge and a 2-colour outline.
#   4. The subtitle and PRESS ANY KEY boxes: 4 colours each (border, fill, text, shadow), so the letters are crisp.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2lab, lab2rgb
from skimage.restoration import denoise_tv_chambolle
from skimage.measure import label
from skimage.morphology import skeletonize
from sklearn.cluster import KMeans

W, H = 320, 240
N4 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
LOGO = (118, 10, 304, 84)          # x0, y0, x1, y1: the logo letters and their outline
SUB = (150, 78, 292, 100)          # the subtitle banner
PRESS = (154, 187, 272, 207)       # the PRESS ANY KEY box


def vga(c):
    return np.round(np.round(np.asarray(c, float) / 255 * 63) * 255 / 63)


def merge_small(idx, pl, minsz, de):
    """Clusters smaller than minsz px take their main neighbour's colour (unless the two are far apart)."""
    for _ in range(4):
        changed = 0
        for k in range(len(pl)):
            lb, nl = label(idx == k, connectivity=1, return_num=True)
            if nl == 0: continue
            sizes = ndi.sum(np.ones_like(lb), lb, index=np.arange(1, nl + 1))
            for ci in np.nonzero(sizes < minsz)[0] + 1:
                m = lb == ci
                ring = ndi.binary_dilation(m, structure=N4) & ~m
                nb = idx[ring]
                if len(nb) == 0: continue
                vals, cnt = np.unique(nb, return_counts=True)
                t = vals[cnt.argmax()]
                if np.linalg.norm(pl[k] - pl[t]) < de:
                    idx[m] = t; changed += 1
        if not changed: break
    return idx


def darker_of(pl, k, drop):
    """The palette entry at least `drop` L darker than k, with the closest hue."""
    c = [j for j in range(len(pl)) if pl[j, 0] <= pl[k, 0] - drop]
    if not c: return int(pl[:, 0].argmin())
    d = [np.linalg.norm(pl[j, 1:] - pl[k, 1:]) + 0.3 * abs(pl[k, 0] - drop - pl[j, 0]) for j in c]
    return c[int(np.argmin(d))]


def scene(src):
    tone = np.array(Image.fromarray(src).resize((W, H), Image.BOX)).astype(float)
    lab = denoise_tv_chambolle(rgb2lab(tone / 255.0), weight=3, channel_axis=-1)
    km = KMeans(n_clusters=30, n_init=4, random_state=1).fit(lab.reshape(-1, 3))
    pal = vga(np.clip(lab2rgb(km.cluster_centers_[None])[0] * 255, 0, 255))
    pl = rgb2lab(pal[None] / 255.0)[0]
    idx = ((lab[:, :, None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    idx = merge_small(idx, pl, 4, 30)
    base = idx.copy(); Lm = pl[base][..., 0]
    # sel-out on strong edges
    out = idx.copy()
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        edge = (np.roll(Lm, (-dy, -dx), (0, 1)) - Lm > 35) & (Lm < 45)
        for k in np.unique(base[edge]): out[edge & (base == k)] = darker_of(pl, k, 8)
    idx = out
    # drawn lines: thin dark lines of the painting (black-hat), 1 px, no scraps; in light areas only long ones (stone joints, not cloth texture)
    Ls = (0.3 * src[..., 0] + 0.59 * src[..., 1] + 0.11 * src[..., 2]).astype(np.float32)
    bh = ndi.grey_closing(Ls, size=(17, 17)) - Ls
    bhs = np.array(Image.fromarray(bh).resize((W, H), Image.BOX))
    sk = skeletonize(bhs > 18)
    lb, nl = label(sk, connectivity=2, return_num=True)
    sizes = ndi.sum(sk, lb, index=np.arange(1, nl + 1))
    for ci in np.nonzero(sizes >= 8)[0] + 1:
        ys, xs = np.nonzero(lb == ci)
        dark_area = np.median(Lm[ys, xs]) < 40
        if dark_area or len(ys) >= 30:
            for y, x in zip(ys, xs):
                if dark_area or Lm[y, x] < 70: idx[y, x] = darker_of(pl, base[y, x], 18)
    return pal[idx].astype(np.uint8)


def boxes(img, old):
    """Subtitle and PRESS boxes: the old crisp-ish pixels snapped to 4 colours each."""
    for x0, y0, x1, y1 in (SUB, PRESS):
        reg = old[y0:y1, x0:x1].reshape(-1, 3).astype(float)
        km = KMeans(n_clusters=4, n_init=4, random_state=1).fit(rgb2lab(reg[None] / 255.0)[0])
        cols = np.array([reg[km.labels_ == k].mean(0) for k in range(4)])
        # keep only the box itself: pixels whose old colour is navy/blue/cream (not sky or water around it)
        img[y0:y1, x0:x1] = vga(cols)[km.labels_].reshape(y1 - y0, x1 - x0, 3)
    return img


def logo(img, old):
    x0, y0, x1, y1 = LOGO
    reg = old[y0:y1, x0:x1].astype(int)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    warm = (r > b + 40) & (lum >= 60)                      # the letters: every warm pixel, light or dark orange
    warm = ndi.median_filter(warm.astype(np.uint8), size=3).astype(bool)
    warm = ndi.binary_opening(ndi.binary_closing(warm, structure=N4), structure=N4)
    comp, n = label(warm, connectivity=1, return_num=True)    # leaves at the box's edge are not letters
    for ci in range(1, n + 1):
        ys, xs = np.nonzero(comp == ci)
        if ys.min() == 0 or xs.min() == 0 or ys.max() == warm.shape[0] - 1 or xs.max() == warm.shape[1] - 1: warm[comp == ci] = False
    comp, n = label(warm, connectivity=1, return_num=True)    # small bits keep only if they sit by a letter (paw toes)
    sizes = ndi.sum(warm, comp, index=np.arange(1, n + 1))
    big = np.isin(comp, np.nonzero(sizes >= 30)[0] + 1)
    near = ndi.binary_dilation(big, structure=np.ones((3, 3)), iterations=5)
    for ci in np.nonzero(sizes < 30)[0] + 1:
        if not (near & (comp == ci)).any(): warm[comp == ci] = False
    dark = lum < 70
    outline = ndi.binary_dilation(warm, structure=np.ones((3, 3)), iterations=2) & ~warm
    shadow = (np.roll(np.roll(outline | warm, 2, 0), 1, 1)) & ~outline & ~warm & dark
    navy, shade = vga((22, 26, 58)), vga((12, 14, 34))
    ramp = [vga(c) for c in ((255, 236, 120), (255, 200, 40), (255, 150, 26), (236, 100, 16))]
    hi, lo = vga((255, 250, 210)), vga((196, 72, 12))
    out = img[y0:y1, x0:x1].copy()
    # band position: height within each letter (its connected shape), so tilted letters get level bands
    comp, n = label(warm, connectivity=1, return_num=True)
    for ci in range(1, n + 1):
        ys, xs = np.nonzero(comp == ci)
        top, bot = ys.min(), ys.max()
        for y, x in zip(ys, xs):
            t = (y - top) / max(1, bot - top) * 3.0          # 0..3 across four bands
            band = int(t); frac = t - band
            if band < 3 and frac > 0.62 and (x + y) % 2 == 0: band += 1   # a checker row joins two bands
            out[y, x] = ramp[min(band, 3)]
    up = np.roll(warm, 1, 0); dn = np.roll(warm, -1, 0)
    out[warm & ~up] = hi                                     # light top edge
    out[warm & ~dn] = lo                                     # dark lower edge
    out[outline] = navy
    out[shadow] = shade
    img[y0:y1, x0:x1] = out
    return img


def repixel(src, old):
    """src: the painting (RGB array); old: the previous 320x240 cut (for the logo shapes and the box texts)."""
    img = scene(src)
    img = logo(img, old)
    img = boxes(img, old)
    return img.astype(int)
