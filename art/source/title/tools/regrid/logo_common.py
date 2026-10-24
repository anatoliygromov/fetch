"""Self-contained helpers for the FETCH! logo track (copied and trimmed from common.py,
shapes.py and lines.py so the logo track does not depend on modules other tracks own)."""
import numpy as np, cv2, os
from PIL import Image
from scipy import ndimage as ndi

SRC = os.environ.get('REGRID_SRC', '/home/claude/fetch/source_title/title_original.png')
NX, NY = 320, 240
W_SRC, H_SRC = 2400, 1792
PX, PY = W_SRC / NX, H_SRC / NY          # 7.5 x 7.4667 source px per output cell

N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def load_src():
    return np.array(Image.open(SRC).convert('RGB'))


def srgb_to_lab(rgb):
    c = np.asarray(rgb, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = c @ M.T
    xyz /= np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1).astype(np.float32)


def luma(rgb):
    return np.asarray(rgb, np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def hx(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


def tohex(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c)


def shift(m, dy, dx, fill=False):
    out = np.full_like(m, fill)
    H, W = m.shape
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


def clean_mask(m, min_area=40, hole_area=None):
    m = m.astype(bool)
    hole_area = min_area if hole_area is None else hole_area
    lab, n = ndi.label(m)
    if n:
        sz = ndi.sum(m, lab, np.arange(1, n + 1))
        m = np.isin(lab, np.flatnonzero(sz >= min_area) + 1)
    lab, n = ndi.label(~m)
    if n:
        sz = ndi.sum(~m, lab, np.arange(1, n + 1))
        m = m | np.isin(lab, np.flatnonzero(sz < hole_area) + 1)
    return m


# ---------------------------------------------------------------- contour smoothing
def _turn(p, k):
    a = p - np.roll(p, k, 0); b = np.roll(p, -k, 0) - p
    na = np.linalg.norm(a, axis=1) + 1e-9; nb_ = np.linalg.norm(b, axis=1) + 1e-9
    c = (a * b).sum(1) / (na * nb_)
    s = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    return np.degrees(np.arctan2(s / (na * nb_), c))


def find_corners(p, k=14, thr=50.0):
    n = len(p)
    if n < 4 * k:
        return []
    t = np.abs(_turn(p.astype(float), k))
    th = np.abs(_turn(p.astype(float), max(3, k // 2)))
    t = np.where(th >= 0.75 * t, t, 0)
    cand = [i for i in range(n) if t[i] >= thr and t[i] == max(t[(i + d) % n] for d in range(-k, k + 1))]
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
        a0, a1 = abs(_area(p)), abs(_area(sm))
        if a1 > 1:
            c = sm.mean(0); sm = c + (sm - c) * np.sqrt(a0 / a1)
        return sm
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
        m = ndi.gaussian_filter(m.astype(np.float32), pre) > 0.5
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
        pts = [np.round(q * 16).astype(np.int32).reshape(-1, 1, 2) for q in polys]
        cv2.fillPoly(out, pts, 1, lineType=cv2.LINE_8, shift=4)
    return out.astype(bool)


# ---------------------------------------------------------------- grid helpers
def cell_index(H, W, ox=0.0, oy=0.0):
    """Uniform 320 x 240 cell index of every source pixel (pixel centre), optional offset."""
    xx = np.arange(W) + 0.5 - ox; yy = np.arange(H) + 0.5 - oy
    I = np.clip(np.floor(xx / PX), 0, NX - 1).astype(np.int16)
    J = np.clip(np.floor(yy / PY), 0, NY - 1).astype(np.int16)
    return np.broadcast_to(I[None, :], (H, W)), np.broadcast_to(J[:, None], (H, W))


def coverage(mask_full, I, J):
    cell = (J.astype(np.int64) * NX + I).ravel()
    tot = np.bincount(cell, minlength=NX * NY)
    on = np.bincount(cell, weights=mask_full.ravel().astype(np.float64), minlength=NX * NY)
    return (on / np.maximum(tot, 1)).reshape(NY, NX)


def upscale(m, H=H_SRC, W=W_SRC):
    """Cell mask -> source-resolution mask on the uniform grid."""
    I, J = cell_index(H, W)
    return m[J, I]


def save(arr, path, scale=1):
    im = Image.fromarray(np.asarray(arr, np.uint8))
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


def _tls(pts):
    c = pts.mean(0); u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    d = vt[0]; nrm = np.array([-d[1], d[0]])
    dev = (pts - c) @ nrm
    return c, d, dev


def smooth_contour2(p, s=8.0, k=14, thr=50.0, rms_tol=3.5, max_tol=9.0, corner_move=12.0, min_len=12):
    """Corners kept; every piece between corners that a total-least-squares line fits
    (RMS <= rms_tol, max <= max_tol) becomes that exact line, and corners between two
    such lines move to their intersection; other pieces are Gaussian-smoothed along arc
    length with their ends pinned."""
    p = p.astype(float)
    n = len(p)
    cs = find_corners(p, k, thr)
    if len(cs) < 2:
        return smooth_contour(p, s, k, thr, 0.0)
    segs = []
    for a_i, b_i in zip(cs, cs[1:] + [cs[0] + n]):
        idx = np.arange(a_i, b_i + 1) % n
        seg = p[idx]
        inner = seg[2:-2] if len(seg) > 8 else seg
        c, d, dev = _tls(inner)
        straight = len(seg) >= min_len and np.sqrt((dev ** 2).mean()) <= rms_tol and np.abs(dev).max() <= max_tol
        segs.append(dict(seg=seg, straight=straight, c=c, d=d))
    m = len(segs)
    corners = []
    for i in range(m):
        prev, nxt = segs[i - 1], segs[i]
        raw = nxt['seg'][0]
        q = None
        if prev['straight'] and nxt['straight']:
            q = _intersect(prev['c'], prev['d'], nxt['c'], nxt['d'])
        elif nxt['straight'] or prev['straight']:
            sg = nxt if nxt['straight'] else prev
            # project the raw corner on the straight neighbour
            q = sg['c'] + ((raw - sg['c']) @ sg['d']) * sg['d']
        if q is None or np.linalg.norm(q - raw) > corner_move:
            q = raw
        corners.append(q)
    out = []
    for i in range(m):
        a, b = corners[i], corners[(i + 1) % m]
        sg = segs[i]
        L = len(sg['seg'])
        if sg['straight']:
            t = np.linspace(0, 1, max(L, 2))[:, None]
            pts = a + t * (b - a)
        else:
            seg = sg['seg'].copy(); seg[0] = a; seg[-1] = b
            pts = _smooth_open(seg, s)
        out.append(pts[:-1])
    return np.vstack(out)


def smooth_polys2(mask, s=8.0, k=14, thr=50.0, rms_tol=3.5, max_tol=9.0, pre=2.0, min_area=40):
    m = clean_mask(mask, min_area)
    if pre:
        m = ndi.gaussian_filter(m.astype(np.float32), pre) > 0.5
    cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in cnts:
        c = c[:, 0, :].astype(float)
        if len(c) < 6:
            continue
        polys.append(smooth_contour2(c, s, k, thr, rms_tol, max_tol))
    return polys
