"""Pilot: the FETCH! logo rebuilt from shapes, stripes and a rule-based checker gradient."""
import numpy as np
from scipy import ndimage as ndi
from shapes import raster_shape, coverage, clean_mask
from lines import ring, remove_lcorners, isolated, shift, N4, N8
from common import NX, NY

# palette indices (labels.py palette, seed 0)
Y, Y2, O1, O2, O3 = 5, 62, 72, 24, 85
RED, HI_TOP, HI_SIDE = 58, 65, 88
FILLSET = [Y, Y2, O1, O2, O3, RED, HI_TOP, HI_SIDE]
NAVY = 7
NAVYSET = [7, 41, 13, 15, 4]
STRIPES = [HI_TOP, HI_SIDE, RED]


def region(H, W):
    R = np.zeros((H, W), bool)
    R[140:578, 930:2245] = True
    R[578:612, 1990:2245] = True
    return R


def build(L, I, J, pal, out, owner, sm=8.0):
    H, W = L.shape
    R = region(H, W)
    FILL = clean_mask(np.isin(L, FILLSET) & R, 60)
    NAV = np.isin(L, NAVYSET) & R
    OUTER = ndi.binary_fill_holes(clean_mask(FILL | NAV, 200))
    GAP = OUTER & ~FILL & ~NAV
    outer, _ = raster_shape(OUTER, I, J, s=sm)
    fill, fillF = raster_shape(FILL, I, J, s=sm)
    gap, _ = raster_shape(GAP, I, J, s=sm * 0.6, min_area=120)
    fill &= outer
    outer = even_outline(outer, fill, OUTER, I, J)
    gap &= outer & ~fill
    # gap colour: dominant painting label per gap component
    cell = (J.astype(np.int64) * NX + I)
    lab, n = ndi.label(gap)
    navy = outer & ~fill & ~gap
    out[navy] = NAVY
    for c in range(1, n + 1):
        cm = lab == c
        src = cm[J, I] & GAP
        vals = L[src]
        out[cm] = np.bincount(vals).argmax() if len(vals) else NAVY
    # fill: gradient band per cell from local composition
    def frac(labs, s=9.0):
        return ndi.gaussian_filter(np.isin(L, labs).astype(np.float32), s)
    fy, fy2, fo1, fo2 = frac([Y]), frac([Y2]), frac([O1]), frac([O2, O3])
    tot = fy + fy2 + fo1 + fo2 + 1e-6
    u = (fo1 + fo2) / tot          # orange share
    v = (fy2 + fo2) / tot          # lower-ramp share
    uc = coverage_mean(u, fillF, I, J); vc = coverage_mean(v, fillF, I, J)
    uc = smooth_in(uc, fill, 1.2); vc = smooth_in(vc, fill, 1.2)
    band = np.where(uc < 0.27, 0, np.where(uc > 0.78, 3, np.where(vc < 0.5, 1, 2)))
    yy, xx = np.indices((NY, NX)); ph = (yy + xx) % 2 == 1
    col = np.select([band == 0, band == 1, band == 2, band == 3],
                    [Y, np.where(ph, O1, Y), np.where(ph, O2, Y2), O2])
    out[fill] = col[fill]
    # stripes on the inner ring of the fill, by the direction the edge faces
    def ev(labs):
        return coverage(ndi.maximum_filter(np.isin(L, labs), size=5), I, J)
    e_hi = ev([HI_TOP, HI_SIDE]); e_red = ev([RED])
    face = {d: fill & ~shift(fill, *d) for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]}
    top, bot, lef, rig = face[(-1, 0)], face[(1, 0)], face[(0, -1)], face[(0, 1)]
    dom_hi = top | lef
    dom_red = (bot | (rig & ~top)) & ~dom_hi
    hi = (top & (e_hi >= 0.25)) | (lef & (e_hi >= 0.30))
    red = (bot & (e_red >= 0.25)) | (rig & ~top & (e_red >= 0.35))
    red &= ~hi
    hi = close_along(hi, dom_hi); red = close_along(red, dom_red & ~hi)
    for m, colr in ((hi, HI_TOP), (red, RED)):
        m = remove_lcorners(m)
        m &= ~isolated(m)
        out[m] = colr
    owner[outer] = 1
    stats = dict(band_counts=np.bincount(band[fill], minlength=4).tolist())
    return dict(outer=outer, fill=fill, gap=gap, navy=navy, band=band, OUTER=OUTER, FILL=FILL, GAP=GAP, stats=stats)


def coverage_mean(f, mask_full, I, J):
    cell = (J.astype(np.int64) * NX + I).ravel()
    w = mask_full.ravel().astype(np.float64)
    s = np.bincount(cell, weights=f.ravel() * w, minlength=NX * NY)
    n = np.bincount(cell, weights=w, minlength=NX * NY)
    return (s / np.maximum(n, 1e-6)).reshape(NY, NX)


def smooth_in(v, m, s):
    a = ndi.gaussian_filter(np.where(m, v, 0.0), s); b = ndi.gaussian_filter(m.astype(float), s)
    return np.where(m, a / np.maximum(b, 1e-6), v)


def close_along(S, D, it=3):
    """Add domain pixels that sit between two stripe pixels which do not touch each other."""
    S = S.copy()
    offs = N8
    for _ in range(it):
        cand = D & ~S
        add = np.zeros_like(S)
        for i, (ay, ax) in enumerate(offs):
            for (by, bx) in offs[i + 1:]:
                if max(abs(ay - by), abs(ax - bx)) <= 1:
                    continue
                add |= cand & shift(S, ay, ax) & shift(S, by, bx)
        if not add.any():
            break
        S |= add
    return S


def even_outline(outer, fill, OUTER, I, J, pitch=7.48):
    """Make the outline band an offset of the fill: its thickness at each fill edge is the
    painting's own (distance from the fill edge to the sky, in cells, rounded), taken as the
    median along the edge, so the band keeps an even width and loses lumps and notches."""
    edt = ndi.distance_transform_edt(OUTER)
    # painting thickness at each fill ring pixel: sample edt at the source centre of the cell
    H, W = OUTER.shape
    cy = ((np.arange(NY) + 0.5) * H / NY).astype(int); cx = ((np.arange(NX) + 0.5) * W / NX).astype(int)
    e = edt[np.ix_(cy, cx)] / pitch                      # cells from this cell centre to the sky
    rg = ring(fill)
    t = np.where(rg, np.round(e - 0.5), np.nan)
    # median along the edge: over ring pixels in a 7 x 7 window
    tt = t.copy()
    ys, xs = np.nonzero(rg)
    for y, x in zip(ys, xs):
        w = t[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
        tt[y, x] = np.nanmedian(w)
    tt = np.clip(np.nan_to_num(tt, nan=1), 1, 8)
    # distance from every pixel to the fill, and the thickness of the nearest ring pixel
    d, (iy, ix) = ndi.distance_transform_edt(~fill, return_indices=True)
    T = tt[iy, ix]
    band = (~fill) & (d <= T + 0.25)
    new = fill | band
    # interior navy that the painting has between letters stays (not reachable from the sky)
    sky = ~(outer | new)
    lab, n = ndi.label(sky | (outer & ~new & ~fill), structure=np.ones((3, 3)))
    border = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    big = np.isin(lab, border[border > 0])
    keep_inner = outer & ~new & ~big
    return new | keep_inner
