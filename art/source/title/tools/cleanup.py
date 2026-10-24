"""Pixel-art cleanup of the title picture (24 Oct, 0 credits). The painting is AI pixel-style art, so sampling it
cell by cell copies its texture noise. Steps:
  1. segment(): the native-grid picture split into materials (hand-tuned boxes and polygons crossed with colour
     rules); saved as art/source/title/masks/<material>.png
  2. ramps(): each material gets a small deliberate ramp from its own colours (k-means in Lab, the counts in RAMP;
     each step the painting's colour most used in its cluster), every pixel snaps to the nearest step (perceptual)
  3. crumbs(): per material, lone pixels and 2-pixel crumbs merge into the shade round them (a mode filter on the
     material's mask only; 1 px lines longer than 2 px, such as railing bars and outlines, are left alone)
  4. the colours of all materials merged where they are near twins (dE < 6) until there are at most MAX_COLOURS
  5. head.py finishes Pepper's head by hand (pixel lists)."""
import os
import numpy as np
from scipy import ndimage
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
from PIL import Image, ImageDraw

MAX_COLOURS = 48
# ramp sizes per material (0: keep the colours as they are)
RAMP = dict(coat=5, nose=0, eye=0, tongue=4, bandana=4, trunk=4, leaves=5, lamp=4, lantern=0, stone=4, sky=4, clouds=3,
            city=0, water=4, boats=0, railing=3, pavement=6, bench=3, flowers=0, rest=0)
CRUMB = dict(city=0)            # the far city keeps its colours and its 1-2 px windows (its texture is the detail)
# the painting shades with a texture of two colours; a soft masked blur (sigma, game px) of a material first turns
# that texture into its tone, so the ramp steps become clean areas that follow the form (0: snap as it is)
SMOOTH = dict(coat=1.0, bandana=0.9, tongue=0.7, leaves=0.6, water=0.7, clouds=0.6, trunk=0.7)            # the far city keeps its 2-pixel windows: only lone pixels merge there

def poly(shape, pts):
    im = Image.new('L', (shape[1], shape[0]), 0); ImageDraw.Draw(im).polygon(pts, fill=1)
    return np.array(im).astype(bool)

def box(shape, x0, y0, x1, y1):
    m = np.zeros(shape, bool); m[y0:y1, x0:x1] = True; return m

# Pepper's silhouette, generous (the colour rules cut her out of it): game pixels
PEPPER = [(0, 240), (0, 192), (14, 186), (19, 168), (18, 146), (22, 128), (34, 112), (44, 98), (58, 88), (76, 80),
          (98, 76), (118, 78), (134, 86), (147, 98), (150, 116), (146, 132), (140, 140), (139, 158), (142, 172),
          (146, 196), (143, 240)]
NOSE = [(100, 128), (104, 123), (112, 121), (119, 123), (123, 130), (122, 140), (117, 146), (108, 148), (101, 144), (98, 136)]
EYE_BOX = (104, 96, 124, 121)
NOSE_BOX = (96, 116, 128, 142)
MOUTH_BOX = (88, 138, 130, 176)

def segment(img, keep=None):
    """returns {material: mask}; keep: pixels left out (the logo and its plate, drawn as layers)"""
    H, W, _ = img.shape
    lab = rgb2lab(img / 255.0); L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    r, g, b = [img[..., i].astype(int) for i in range(3)]
    hue = np.degrees(np.arctan2(B, A)) % 360; ch = np.hypot(A, B)
    S = (H, W)
    M = {}
    gen = poly(S, PEPPER)
    green_ = (hue > 85) & (hue < 170) & (ch > 12)
    body = gen & (((L < 40) & ~green_) | ((A > 18) & (L > 30)))     # her dark coat, the bandana and the tongue
    lb, _ = ndimage.label(body)
    pep = ndimage.binary_fill_holes(lb == lb[200, 60])                # the part joined to her chest, holes filled
    pink = (A > 28) & (hue > 330) | (A > 28) & (hue < 20) & (L > 40)
    dark = L < 32
    tonguec = (A > 18) & (L > 40) & (hue > 20) & (hue < 70)
    M['bandana'] = pep & pink & poly(S, [(26, 160), (60, 166), (132, 170), (132, 232), (100, 226), (60, 190), (26, 176)])
    M['tongue'] = pep & box(S, *MOUTH_BOX) & (tonguec | (A > 18) & (L > 30))
    # the open eye: on each row the span from its near-black ring's first to last pixel (x 104-122, rows 99-117)
    eye = np.zeros(S, bool)
    for y in range(99, 118):
        xs = [x for x in range(104, 123) if L[y, x] < 5]
        if xs: eye[y, min(xs):max(xs) + 1] = True
    M['eye'] = eye
    M['nose'] = poly(S, NOSE) & ~eye
    green0 = (hue > 85) & (hue < 170) & (ch > 12)
    M['coat'] = pep & ~M['bandana'] & ~M['tongue'] & ~M['eye'] & ~M['nose'] & ~green0 & ((L < 40) | ((ch < 22) & (L < 60)))
    # the background
    bg = ~pep
    green = (hue > 85) & (hue < 170) & (ch > 12)
    blue = (b > r + 40) & (hue > 200) & (hue < 300)
    left = box(S, 0, 0, 140, 240)
    M['leaves'] = bg & green
    M['trunk'] = bg & left & (hue > 30) & (hue < 85) & (L < 55) & (ch > 8) & box(S, 0, 0, 70, 120)
    lamp_l = poly(S, [(26, 40), (42, 40), (42, 80), (37, 80), (37, 190), (28, 190), (28, 80), (24, 80)])
    lamp_r = box(S, 282, 122, 292, 168)
    M['lantern'] = bg & (lamp_l | lamp_r) & (B > 30) & (L > 50)
    M['lamp'] = bg & (lamp_l | lamp_r) & ~M['lantern'] & ~M['leaves']
    M['stone'] = bg & box(S, 0, 40, 28, 200) & ~M['leaves'] & ~M['trunk'] & ~M['lamp'] & (L > 40) & (ch < 30)
    M['railing'] = bg & box(S, 130, 168, 320, 206) & (L < 42) & ~M['leaves']
    M['bench'] = bg & box(S, 292, 168, 320, 212) & (L < 42)
    M['pavement'] = bg & box(S, 130, 200, 320, 240) & ~M['railing'] & ~M['bench']
    flowers = bg & box(S, 270, 135, 320, 172) & (ch > 30) & ~green & ~blue
    M['flowers'] = flowers
    bands = rgb2lab(np.array([[[42, 134, 213], [51, 154, 223], [84, 171, 224], [120, 186, 226]]]) / 255.0)[0]
    dsky = np.min([np.sqrt(((lab - c) ** 2).sum(-1)) for c in bands], axis=0)
    sky = bg & (dsky < 7) & box(S, 0, 0, 320, 140) & ~box(S, 140, 98, 320, 140)   # the sky's own band colours (the
    # sky between the far buildings goes with the city, whose blues share them, so the buildings keep their windows)
    M['sky'] = sky
    M['clouds'] = bg & box(S, 0, 0, 320, 140) & (L > 72) & (ch < 30) & ~M['stone']
    M['city'] = bg & box(S, 140, 98, 320, 152) & ~M['sky'] & ~M['clouds'] & ~M['leaves'] & ~M['lamp'] & ~M['lantern'] & ~M['flowers']
    M['water'] = bg & box(S, 132, 140, 300, 186) & blue & (L > 35)
    M['boats'] = bg & box(S, 132, 148, 300, 186) & ~M['water'] & ~M['leaves'] & ~M['railing'] & ~M['flowers'] & ~M['lamp'] & ~M['lantern']
    # one material per pixel (the first listed wins), the rest kept
    order = ['eye', 'nose', 'tongue', 'bandana', 'coat', 'lantern', 'lamp', 'trunk', 'leaves', 'stone', 'flowers', 'bench',
             'railing', 'pavement', 'boats', 'water', 'city', 'clouds', 'sky']
    taken = np.zeros(S, bool) if keep is None else keep.copy()
    out = {}
    for n in order:
        out[n] = M[n] & ~taken; taken |= out[n]
    out['rest'] = ~taken if keep is None else (~taken)
    if keep is not None: out['rest'] &= ~keep
    return out

def ramps(img, mats, seed=1):
    """each material's ramp (k-means in Lab of its own pixels) and the picture snapped to it"""
    out = img.copy(); lab = rgb2lab(img / 255.0); R = {}
    for n, m in mats.items():
        k = RAMP.get(n, 0)
        if k == 0 or m.sum() < k * 4: continue
        X = lab[m]; P = img[m]
        distinct = np.unique(P, axis=0)
        if len(distinct) <= k: R[n] = distinct; continue
        km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(X)
        cols = []
        for c in range(k):                        # each step the painting's own colour most used in its cluster
            v, cnt = np.unique(P[km.labels_ == c], axis=0, return_counts=True); cols.append(v[cnt.argmax()])
        cols = np.array(cols)
        R[n] = cols
        # every pixel to its material's nearest ramp colour (perceptual), after the masked blur when SMOOTH has one;
        # the near-black outline pixels (L < 9) keep their own nearest step, unblurred, so lines stay lines
        cl = rgb2lab(cols[None].astype(float) / 255.0)[0]
        sg = SMOOTH.get(n, 0)
        snap = ((X[:, None] - cl[None]) ** 2).sum(-1).argmin(1)
        if sg:
            # the tone map: a masked blur of lightness; then the steps (ordered by lightness) are dealt out by rank,
            # each step keeping the share of the material it had before, so light textured fur becomes a solid
            # lighter area and the material's overall light stays the same. Outline pixels (L < 9) stay as snapped.
            mf = m.astype(float); den = ndimage.gaussian_filter(mf, sg) + 1e-6
            T = (ndimage.gaussian_filter(lab[..., 0] * mf, sg) / den)[m]
            byL = np.argsort(cl[:, 0]); rank_of = np.empty_like(byL); rank_of[byL] = np.arange(len(byL))
            free = X[:, 0] >= 9
            share = np.bincount(rank_of[snap[free]], minlength=len(cols)).cumsum()
            order = np.argsort(T[free], kind='stable')
            ranks = np.searchsorted(share, np.arange(free.sum()), side='right')
            res = snap.copy(); idxf = np.nonzero(free)[0]
            res[idxf[order]] = byL[np.minimum(ranks, len(cols) - 1)]
            snap = res
        out[m] = cols[snap]
    return out, R

def crumbs(img, mats, passes=3, maxsize=2):
    """per material: components of one colour with <= maxsize pixels take the colour most of their neighbours
    (inside the material) have"""
    out = img.copy(); H, W, _ = img.shape
    for n, m in mats.items():
        if n in ('eye', 'flowers', 'boats'): continue
        ms = CRUMB.get(n, maxsize)
        if ms == 0: continue
        for _ in range(passes):
            key = out[..., 0].astype(np.int64) * 65536 + out[..., 1] * 256 + out[..., 2]
            changed = 0
            for v in np.unique(key[m]):
                lb, nn = ndimage.label((key == v) & m)
                if nn == 0: continue
                sizes = np.bincount(lb.ravel())[1:]
                for i in np.nonzero(sizes <= ms)[0]:
                    comp = lb == i + 1
                    ring = ndimage.binary_dilation(comp, structure=np.ones((3, 3))) & ~comp & m
                    if not ring.any(): continue
                    nv, cnt = np.unique(key[ring], return_counts=True)
                    w = nv[cnt.argmax()]
                    out[comp] = (w >> 16, (w >> 8) & 255, w & 255); key[comp] = w; changed += 1
            if not changed: break
    return out

def merge_colours(img, protect=None, max_colours=MAX_COLOURS, max_de=10.0):
    """the colours merged pair by pair (the closest pair in Lab, the rarer colour into the commoner) until at most
    max_colours, never two colours further apart than max_de"""
    out = img.copy()
    while True:
        cols, inv, cnt = np.unique(out.reshape(-1, 3), axis=0, return_inverse=True, return_counts=True)
        if len(cols) <= max_colours: break
        lab = rgb2lab(cols[None].astype(float) / 255.0)[0]
        d = np.sqrt(((lab[:, None] - lab[None]) ** 2).sum(-1)); np.fill_diagonal(d, 1e9)
        if protect is not None:                   # two steps of one protected ramp (Pepper's) never merge
            pk = {tuple(c) for c in protect}
            pr = np.array([tuple(c) in pk for c in cols])
            d[np.ix_(pr, pr)] = 1e9
        i, j = np.unravel_index(d.argmin(), d.shape)
        if d[i, j] > max_de: break
        src, dst = (i, j) if cnt[i] < cnt[j] else (j, i)
        flat = out.reshape(-1, 3); flat[inv.ravel() == src] = cols[dst]
    return out

def save_masks(mats, d):
    os.makedirs(d, exist_ok=True)
    for n, m in mats.items(): Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(d, n + '.png'))

def lone(a, mask=None):
    a = a.astype(np.int64); k = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
    p = np.pad(k, 1, constant_values=-1); c = p[1:-1, 1:-1]
    same = (p[:-2, 1:-1] == c) | (p[2:, 1:-1] == c) | (p[1:-1, :-2] == c) | (p[1:-1, 2:] == c)
    lo = ~same
    return lo[mask].mean() if mask is not None else lo.mean()

def run(img, keep, masks_dir=None):
    """the whole cleanup; returns the cleaned picture, the materials and the numbers"""
    import head as HD
    mats = segment(img, keep)
    if masks_dir: save_masks(mats, masks_dir)
    a, R = ramps(img, mats)
    b = crumbs(a, mats)
    prot = np.concatenate([R[k] for k in ('coat', 'bandana', 'tongue') if k in R])
    c = merge_colours(b, protect=prot)
    c = crumbs(c, mats, passes=2)
    f = HD.finish(c, img, mats)
    f = crumbs(f, {'nose': mats['nose']}, maxsize=1)
    f = merge_colours(f, protect=prot)
    pep = mats['coat'] | mats['nose'] | mats['eye'] | mats['tongue'] | mats['bandana']
    nk = ~keep
    stats = dict(colours=len(np.unique(f[nk].reshape(-1, 3), axis=0)), lone_all=lone(f, nk), lone_pepper=lone(f, pep),
                 before_all=lone(img, nk), before_pepper=lone(img, pep))
    return f, mats, stats
