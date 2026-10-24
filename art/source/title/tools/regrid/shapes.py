"""Step 3: shape geometry.

A shape is a binary mask at the painting's resolution. Its contours are traced,
split at real corners, each piece between corners is smoothed along its arc
length (Gaussian, ends pinned by point reflection so tangents are kept), nearly
straight pieces become exact straight segments, and corners are moved to the
intersection of the two neighbouring tangents. The smoothed polygons are filled
(even-odd, so holes stay holes) at full resolution and then rasterized onto the
output grid with a coverage threshold of 0.5 (no anti-aliasing). On the uniform
grid this is the same as sampling the cell centres, so a straight edge becomes a
digital straight line and a smooth curve becomes runs that change steadily.
"""
import numpy as np, cv2
from scipy import ndimage as ndi
from common import NX, NY


def clean_mask(m, min_area=40):
    m = m.astype(bool)
    lab, n = ndi.label(m)
    if n:
        sz = ndi.sum(m, lab, np.arange(1, n + 1))
        m = np.isin(lab, np.flatnonzero(sz >= min_area) + 1)
    lab, n = ndi.label(~m)
    if n:
        sz = ndi.sum(~m, lab, np.arange(1, n + 1))
        m = m | np.isin(lab, np.flatnonzero(sz < min_area) + 1)
    return m


def presmooth(m, s=2.5):
    return ndi.gaussian_filter(m.astype(np.float32), s) > 0.5


def _turn(p, k):
    n = len(p)
    a = p - np.roll(p, k, 0); b = np.roll(p, -k, 0) - p
    na = np.linalg.norm(a, axis=1) + 1e-9; nb = np.linalg.norm(b, axis=1) + 1e-9
    c = (a * b).sum(1) / (na * nb)
    s = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    return np.degrees(np.arctan2(s / (na * nb), c))


def find_corners(p, k=14, thr=50.0):
    n = len(p)
    if n < 4 * k:
        return []
    t = np.abs(_turn(p.astype(float), k))
    th = np.abs(_turn(p.astype(float), max(3, k // 2)))
    # a corner turns as much over half the reach as over the whole reach; a curve turns half as much
    t = np.where(th >= 0.75 * t, t, 0)
    cand = [i for i in range(n) if t[i] >= thr and t[i] == max(t[(i + d) % n] for d in range(-k, k + 1))]
    # keep the strongest when two are close
    out = []
    for i in sorted(cand, key=lambda i: -t[i]):
        if all(min(abs(i - j), n - abs(i - j)) > k for j in out):
            out.append(i)
    return sorted(out)


def _smooth_open(seg, s):
    n = len(seg)
    if n < 3 or s <= 0:
        return seg.astype(float)
    pad = min(n - 1, int(3 * s))
    a, b = seg[0].astype(float), seg[-1].astype(float)
    left = 2 * a - seg[1:pad + 1][::-1]
    right = 2 * b - seg[-pad - 1:-1][::-1]
    ext = np.vstack([left, seg, right]).astype(float)
    sm = ndi.gaussian_filter1d(ext, s, axis=0, mode='nearest')
    out = sm[pad:pad + n]
    out[0], out[-1] = a, b
    return out


def _straighten(seg, tol):
    a, b = seg[0], seg[-1]
    d = b - a; L = np.linalg.norm(d)
    if L < 1e-6:
        return seg
    nrm = np.array([-d[1], d[0]]) / L
    dev = np.abs((seg - a) @ nrm)
    if dev.max() <= tol:
        t = ((seg - a) @ d) / (L * L)
        return a + np.outer(np.clip(t, 0, 1), d)
    return seg


def _line_fit(pts):
    c = pts.mean(0); u, s, vt = np.linalg.svd(pts - c)
    return c, vt[0]


def _intersect(c1, d1, c2, d2):
    A = np.array([d1, -d2]).T
    if abs(np.linalg.det(A)) < 1e-3:
        return None
    t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * d1


def _area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * (x * np.roll(y, -1) - np.roll(x, -1) * y).sum()


def smooth_contour(p, s=8.0, k=14, thr=50.0, straight_tol=2.5, corner_fit=18, corner_move=6.0):
    p = p.astype(float)
    n = len(p)
    cs = find_corners(p, k, thr)
    if not cs:
        if n < 8:
            return p
        sm = ndi.gaussian_filter1d(p, min(s, n / 6), axis=0, mode='wrap')
        # smoothing a closed curve shrinks it: scale back about the centroid to keep the area
        a0, a1 = abs(_area(p)), abs(_area(sm))
        if a1 > 1:
            c = sm.mean(0); sm = c + (sm - c) * np.sqrt(a0 / a1)
        return sm
    # move corners to the intersection of the neighbouring tangent lines
    newc = {}
    for i in cs:
        before = np.array([p[(i - d) % n] for d in range(3, corner_fit)])
        after = np.array([p[(i + d) % n] for d in range(3, corner_fit)])
        c1, d1 = _line_fit(before); c2, d2 = _line_fit(after)
        q = _intersect(c1, d1, c2, d2)
        newc[i] = q if q is not None and np.linalg.norm(q - p[i]) <= corner_move else p[i]
    out = []
    for a_i, b_i in zip(cs, cs[1:] + [cs[0] + n]):
        idx = np.arange(a_i, b_i + 1) % n
        seg = p[idx].copy()
        seg[0] = newc[a_i]; seg[-1] = newc[b_i % n]
        seg = _smooth_open(seg, s)
        seg = _straighten(seg, straight_tol)
        out.append(seg[:-1])
    return np.vstack(out)


def smooth_polys(mask, s=8.0, k=14, thr=50.0, straight_tol=2.5, pre=2.5, min_area=40):
    m = clean_mask(mask, min_area)
    if pre:
        m = presmooth(m, pre)
    cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in cnts:
        c = c[:, 0, :].astype(float)
        if len(c) < 6:
            continue
        polys.append(smooth_contour(c, s, k, thr, straight_tol))
    return polys


def fill_polys(polys, shape):
    out = np.zeros(shape, np.uint8)
    if polys:
        pts = [np.round((q + 0.0) * 16).astype(np.int32).reshape(-1, 1, 2) for q in polys]
        cv2.fillPoly(out, pts, 1, lineType=cv2.LINE_8, shift=4)
    return out.astype(bool)


def coverage(mask_full, I, J):
    """Fraction of each output cell covered by the full-res mask."""
    cell = (J.astype(np.int64) * NX + I).ravel()
    tot = np.bincount(cell, minlength=NX * NY)
    on = np.bincount(cell, weights=mask_full.ravel().astype(np.float64), minlength=NX * NY)
    return (on / np.maximum(tot, 1)).reshape(NY, NX)


def raster_shape(mask_full, I, J, **kw):
    polys = smooth_polys(mask_full, **kw)
    m = fill_polys(polys, mask_full.shape)
    return coverage(m, I, J) >= 0.5, m
