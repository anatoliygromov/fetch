"""PEPPER track, step 1: region label map, dog mask, owned mask and part masks.

All masks are at the painting's resolution inside the region box BOX
(x0, y0, x1, y1 in painting pixels). Labels come from labels.py (palette from the
painting's flat areas, anti-aliased edge pixels snapped to a nearby flat colour).
"""
import numpy as np, os
from PIL import Image
from scipy import ndimage as ndi
from common import SRC, srgb_to_lab
import labels as LB

BOX = (0, 540, 1170, 1792)
CACHE = os.environ.get('PEPPER_CACHE', '/tmp/claude-0/pep/cache')
os.makedirs(CACHE, exist_ok=True)
CW, CH = 2400 / 320, 1792 / 240   # output cell size in painting pixels


def region():
    a = np.array(Image.open(SRC).convert('RGB'))
    x0, y0, x1, y1 = BOX
    return a[y0:y1, x0:x1]


def label_region(force=False):
    p = os.path.join(CACHE, 'labels.npz')
    if os.path.exists(p) and not force:
        z = np.load(p); return z['pal'], z['L']
    R = region()
    flat, _ = LB.flat_mask(R, 8)
    pal = LB.build_palette(R, flat, k=64, merge_de=2.5)
    L = LB.label_map(R, pal, flat)
    np.savez_compressed(p, pal=pal, L=L)
    return pal, L


def groups(pal):
    """Material groups by colour, as index lists into pal."""
    lab = srgb_to_lab(pal)
    Lr, ar, br = lab[:, 0], lab[:, 1], lab[:, 2]
    hexes = ['#%02x%02x%02x' % tuple(c) for c in pal]
    g = {k: [] for k in ('line', 'black', 'coat', 'navy', 'pink', 'tongue', 'eye', 'light', 'other')}
    for i, (l, a_, b_) in enumerate(zip(Lr, ar, br)):
        c = np.hypot(a_, b_)
        if l < 0.3:
            g['line'].append(i)          # the painting's pure black line colour
        elif l < 3.5:
            g['black'].append(i)         # near-black shadow colours
        elif b_ < -14 and a_ < 12 and l < 60:
            g['navy'].append(i)
        elif a_ > 40 and b_ < 28 and l > 20:
            g['pink'].append(i)
        elif a_ > 30 and b_ >= 28:
            g['tongue'].append(i)
        elif c < 22 and l < 75 and a_ > -6:
            g['coat'].append(i)
        elif a_ > 10 and b_ > 25:
            g['eye'].append(i)
        elif l >= 75 and c < 25:
            g['light'].append(i)
        else:
            g['other'].append(i)
    return g, hexes


def dog_mask(pal, L):
    p = os.path.join(CACHE, 'dog.npy')
    if os.path.exists(p):
        return np.load(p)
    g, _ = groups(pal)
    dog = g['line'] + g['black'] + g['coat'] + g['pink'] + g['tongue'] + g['eye']
    D0 = np.isin(L, dog)
    D = ndi.binary_opening(D0, np.ones((9, 9)))
    lab, n = ndi.label(D); sz = ndi.sum(D, lab, range(1, n + 1))
    D = lab == (np.argmax(sz) + 1)
    D = ndi.binary_fill_holes(D)
    # give back thin details next to the opened mask (outline anti-aliasing, flap tips)
    D = ndi.binary_fill_holes(D | (D0 & ndi.binary_dilation(D, np.ones((7, 7)))))
    lab, n = ndi.label(D); sz = ndi.sum(D, lab, range(1, n + 1))
    D = lab == (np.argmax(sz) + 1)
    np.save(p, D)
    return D


def bandana_mask(pal, L, D):
    g, _ = groups(pal)
    P = np.isin(L, g['pink']) & D
    P = ndi.binary_closing(P, np.ones((5, 5)))
    lab, n = ndi.label(P); sz = ndi.sum(P, lab, range(1, n + 1))
    # the bandana is the large pink component (the tongue's dark reds are far away)
    cy = ndi.center_of_mass(P, lab, range(1, n + 1))
    B = np.isin(lab, [i + 1 for i in range(n) if sz[i] > 300 and cy[i][0] > 1290 - BOX[1]])
    return ndi.binary_fill_holes(B)


def lower_cut(B, D):
    """Per painting column, the lowest row that belongs to this track: the bandana's
    lower edge where the bandana is, and the bandana's end rows held flat beyond it."""
    H, W = B.shape
    cols = np.flatnonzero(B.any(0))
    low = np.full(W, -1)
    for x in cols:
        # above the bandana's upper edge in this column (the bandana itself is added
        # separately), so the body beside the bandana's slanted sides is not taken
        low[x] = np.flatnonzero(B[:, x]).min()
    xl, xr = cols.min(), cols.max()
    inside = np.arange(xl, xr + 1)
    have = low[inside] >= 0
    low[inside] = np.round(np.interp(inside, inside[have], low[inside][have])).astype(int)
    # left of the knot: keep the head and ear; the shoulder starts below the knot's lowest row
    low[:xl] = B[:, xl:xl + 40].any(1).nonzero()[0].max()
    # right of the bandana's end: only the neck above the bandana's upper edge there
    low[xr + 1:] = B[:, xr - 20:xr + 1].any(1).nonzero()[0].min()
    return low


def owned_mask(pal, L):
    D = dog_mask(pal, L)
    B = bandana_mask(pal, L, D)
    low = lower_cut(B, D)
    yy = np.arange(D.shape[0])[:, None]
    O = (D & (yy <= low[None, :])) | B
    # the flaps' own outline below the bandana where it meets the background
    O |= D & ndi.binary_dilation(B, np.ones((13, 13))) & ndi.binary_dilation(~D, np.ones((29, 29)))
    return D, B, O


def _bbox_mask(shape, x0, y0, x1, y1):
    m = np.zeros(shape, bool)
    m[max(0, y0 - BOX[1]):max(0, y1 - BOX[1]), max(0, x0 - BOX[0]):max(0, x1 - BOX[0])] = True
    return m


def _largest(m):
    lab, n = ndi.label(m)
    if n == 0:
        return m
    sz = ndi.sum(m, lab, range(1, n + 1))
    return lab == (np.argmax(sz) + 1)


def _flood(seed_xy, passable):
    x, y = seed_xy[0] - BOX[0], seed_xy[1] - BOX[1]
    lab, n = ndi.label(passable)
    if n == 0:
        return np.zeros_like(passable)
    # the largest component within 40 px of the seed point
    win = lab[max(0, y - 40):y + 41, max(0, x - 40):x + 41]
    ks, cnt = np.unique(win[win > 0], return_counts=True)
    if len(ks) == 0:
        return np.zeros_like(passable)
    return lab == ks[cnt.argmax()]


# seed points (painting coordinates) inside each part, and part boxes
SEEDS = dict(earL=(300, 1000), earR=(1040, 820), eye=(850, 860), nose=(830, 1010), tongue=(840, 1230))
# where an ear's crease fades into the coat at its top, the ear/head border is closed
# by a short straight cut (painting coordinates) from the crease end to the outline
EAR_CUTS = dict(earL=[(420, 790), (450, 745), (500, 660)], earR=[(910, 720), (895, 650), (880, 590)])
PART_BOX = dict(eye=(795, 745, 920, 895), nose=(740, 930, 940, 1080), tongue=(700, 1130, 980, 1300))


def part_masks_from_labels(pal, L, D, B, cache=True):
    """Named part masks at painting resolution, from a label image L (palette pal).
    The same function serves the painting and the re-upscaled result, so the
    geometry gate compares like with like."""
    g, _ = groups(pal)
    dark = np.isin(L, g['line'] + g['black'])
    parts = {}
    # ears: coat reachable from a seed without crossing the dark crease that separates ear and head
    pas = D & ~dark & ~B
    pas = ndi.binary_opening(pas, np.ones((3, 3)))
    import cv2
    barrier = np.zeros(L.shape, np.uint8)
    for k, pts in EAR_CUTS.items():
        q = np.array([(x - BOX[0], y - BOX[1]) for x, y in pts], np.int32).reshape(-1, 1, 2)
        cv2.polylines(barrier, [q], False, 1, 7)
    pas &= ~barrier.astype(bool)
    for k in ('earL', 'earR'):
        m = _flood(SEEDS[k], pas)
        m = ndi.binary_closing(m, np.ones((15, 15)))
        parts[k] = ndi.binary_fill_holes(m) & D
    # eye, nose: everything inside the outline ring (not coat colour) within the part box
    coat = np.isin(L, g['coat'])
    for k in ('eye', 'nose'):
        bx = _bbox_mask(L.shape, *PART_BOX[k])
        m = ~coat & D & bx
        if k == 'nose':   # the nose's gloss uses the coat's lightest greys
            lab_ = srgb_to_lab(pal)
            m |= np.isin(L, [i for i in g['coat'] if lab_[i, 0] > 44]) & bx
        m = ndi.binary_opening(ndi.binary_closing(m, np.ones((5, 5))), np.ones((7, 7)))
        m = _flood(SEEDS[k], m)
        m = ndi.binary_closing(np.pad(m, 20), np.ones((15, 15)))[20:-20, 20:-20]
        parts[k] = ndi.binary_fill_holes(m)
    bx = _bbox_mask(L.shape, *PART_BOX['tongue'])
    t = np.isin(L, g['tongue'] + g['pink']) & bx & ~B
    t = _largest(ndi.binary_closing(t, np.ones((5, 5))))
    # the dark notch at the top of the crease is part of the tongue's shape
    t = ndi.binary_closing(np.pad(t, 20), np.ones((19, 19)))[20:-20, 20:-20]
    parts['tongue'] = ndi.binary_fill_holes(t)
    parts['bandana'] = B.copy()
    yy = np.arange(L.shape[0])[:, None]
    parts['head'] = D & ~B & ~parts['earL'] & ~parts['earR']
    return parts
