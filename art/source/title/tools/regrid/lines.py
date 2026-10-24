"""Pixel-art line rules on the output grid."""
import numpy as np
from scipy import ndimage as ndi

N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def shift(m, dy, dx, fill=False):
    out = np.full_like(m, fill)
    H, W = m.shape
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


def nb(m, dy, dx):
    """value of the neighbour at (y+dy, x+dx) for every pixel."""
    return shift(m, dy, dx)


def lcorners(line, keep_corners=True):
    """Pixels of a 1 px line that form the joint of an L (Aseprite pixel-perfect):
    one horizontal and one vertical line neighbour, and those two touch diagonally,
    and removing the joint does not cut the line (the joint has no other neighbours)."""
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    out = np.zeros_like(m)
    for (hy, hx) in [(0, 1), (0, -1)]:
        for (vy, vx) in [(1, 0), (-1, 0)]:
            c = m & nb(m, hy, hx) & nb(m, vy, vx) & ~nb(m, vy, hx) & (n8 == 2)
            if keep_corners:
                # a real corner: both legs run on for at least two pixels
                c &= ~(nb(m, 2 * hy, 2 * hx) & nb(m, 2 * vy, 2 * vx))
            out |= c
    return out


def remove_lcorners(line):
    m = line.astype(bool).copy()
    for _ in range(4):
        c = lcorners(m)
        if not c.any():
            break
        # remove one of each adjacent pair only: process in raster order checkerboard
        for par in (0, 1):
            yy, xx = np.indices(m.shape)
            cc = lcorners(m) & ((yy + xx) % 2 == par)
            m &= ~cc
    return m


def isolated(m):
    m = m.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    return m & (n8 == 0)


def ring(fill):
    """inner boundary ring: fill pixels with a 4-neighbour outside the fill."""
    f = fill.astype(bool)
    out = np.zeros_like(f)
    for dy, dx in N4:
        out |= f & ~shift(f, dy, dx, fill=False)
    return out


# ---------------------------------------------------------------------------
# skeleton tracing (full resolution)

def _n8count(m):
    return sum(nb(m, dy, dx).astype(int) for dy, dx in N8)


def trace_skeleton(sk, min_spur=12):
    """Split a 1 px skeleton into polylines between end points and junctions.
    Short spurs (an end point within min_spur px of a junction) are dropped.
    Returns a list of (n, 2) arrays of (x, y) points."""
    sk = sk.astype(bool).copy()
    for _ in range(3):
        paths = _trace(sk)
        deg = _n8count(sk)
        drop = False
        for p in paths:
            if len(p) < min_spur:
                (x0, y0), (x1, y1) = p[0].astype(int), p[-1].astype(int)
                e0 = deg[y0, x0] == 1; e1 = deg[y1, x1] == 1
                j0 = deg[y0, x0] >= 3; j1 = deg[y1, x1] >= 3
                if (e0 and j1) or (e1 and j0) or (e0 and e1 and len(p) < 6):
                    for (x, y) in p.astype(int):
                        if deg[y, x] <= 2:
                            sk[y, x] = False
                    drop = True
        if not drop:
            break
        from skimage.morphology import skeletonize
        sk = skeletonize(sk)
    return _trace(sk), sk


def _trace(sk):
    H, W = sk.shape
    deg = _n8count(sk) * sk
    node = sk & (deg != 2)
    seen = set()
    paths = []
    ys, xs = np.nonzero(node)
    def nbrs(y, x):
        for dy, dx in N8:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and sk[yy, xx]:
                yield yy, xx
    def edge_key(a, b):
        return (a, b) if a < b else (b, a)
    for y, x in zip(ys, xs):
        for ny, nx in nbrs(y, x):
            k = edge_key((y, x), (ny, nx))
            if k in seen:
                continue
            seen.add(k)
            path = [(x, y), (nx, ny)]
            py, px, cy, cx = y, x, ny, nx
            while not node[cy, cx]:
                nxt = None
                for qy, qx in nbrs(cy, cx):
                    if (qy, qx) == (py, px):
                        continue
                    kk = edge_key((cy, cx), (qy, qx))
                    if kk in seen:
                        continue
                    nxt = (qy, qx); break
                if nxt is None:
                    break
                seen.add(edge_key((cy, cx), nxt))
                py, px, cy, cx = cy, cx, nxt[0], nxt[1]
                path.append((cx, cy))
            paths.append(np.array(path, float))
    # closed loops without nodes
    rest = sk.copy()
    for p in paths:
        for x, y in p.astype(int):
            rest[y, x] = False
    while rest.any():
        y, x = map(int, np.argwhere(rest)[0])
        path = [(x, y)]; rest[y, x] = False
        cy, cx = y, x
        while True:
            nxt = None
            for qy, qx in nbrs(cy, cx):
                if rest[qy, qx]:
                    nxt = (qy, qx); break
            if nxt is None:
                break
            rest[nxt] = False; cy, cx = nxt; path.append((cx, cy))
        if len(path) > 4:
            path.append(path[0])
            paths.append(np.array(path, float))
    return paths


def smooth_polyline(p, s=6.0, closed=None):
    """Gaussian smoothing along the arc, ends pinned (point reflection)."""
    p = np.asarray(p, float)
    if len(p) < 4:
        return p
    if closed is None:
        closed = np.hypot(*(p[0] - p[-1])) < 1.5 and len(p) > 10
    # resample to unit spacing first
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    n = max(4, int(d[-1]) + 1)
    t = np.linspace(0, d[-1], n)
    q = np.c_[np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])]
    from scipy.ndimage import gaussian_filter1d
    if closed:
        return gaussian_filter1d(q[:-1], s, axis=0, mode='wrap')
    s = min(s, len(q) / 4)
    pad = min(len(q) - 1, int(3 * s) + 1)
    a, b = q[0], q[-1]
    ext = np.vstack([2 * a - q[1:pad + 1][::-1], q, 2 * b - q[-pad - 1:-1][::-1]])
    sm = gaussian_filter1d(ext, s, axis=0, mode='nearest')[pad:pad + len(q)]
    sm[0], sm[-1] = a, b
    return sm


# ---------------------------------------------------------------------------
# rasterization onto the output grid

def raster_polyline(p, cw, ch, closed=False):
    """Cells (i, j) visited by a curve given in painting pixels, 8-connected,
    then made pixel-perfect (no L-corner doubles)."""
    p = np.asarray(p, float)
    if closed:
        p = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    n = max(2, int(d[-1] * 4) + 1)
    t = np.linspace(0, d[-1], n)
    x = np.interp(t, d, p[:, 0]); y = np.interp(t, d, p[:, 1])
    I = np.floor(x / cw).astype(int); J = np.floor(y / ch).astype(int)
    seq = [(I[0], J[0])]
    for i, j in zip(I[1:], J[1:]):
        if (i, j) != seq[-1]:
            pi, pj = seq[-1]
            # a 4-step into the diagonal cell happens when the curve crosses a cell corner:
            # keep it 8-connected by skipping intermediates that are not needed
            seq.append((i, j))
    # back-and-forth jitter: a cell revisited right after leaving it
    out = []
    for c in seq:
        if len(out) >= 2 and out[-2] == c:
            out.pop()
            continue
        out.append(c)
    return pixel_perfect(out)


def pixel_perfect(seq):
    """Drop the joint of every L made by three consecutive cells (Aseprite's rule)."""
    out = []
    for c in seq:
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1 and \
               (abs(a[0] - b[0]) + abs(a[1] - b[1])) == 1 and (abs(b[0] - c[0]) + abs(b[1] - c[1])) == 1:
                out.pop()
        out.append(c)
    return out


# ---------------------------------------------------------------------------
# metrics

def chains(line):
    """Trace a 1 px line raster (bool) into chains of cells using the skeleton tracer."""
    return _trace(line.astype(bool))


def runs_of_chain(c):
    """Horizontal/vertical run lengths of an 8-connected chain of cells: a run is a
    maximal stretch of cells sharing a row (for shallow parts) or column (steep parts)."""
    c = np.asarray(c, int)
    if len(c) < 3:
        return []
    runs = []; cur = 1
    for k in range(1, len(c)):
        dx, dy = c[k] - c[k - 1]
        straight = (dy == 0) if abs(c[-1][0] - c[0][0]) >= abs(c[-1][1] - c[0][1]) else (dx == 0)
        if straight:
            cur += 1
        else:
            runs.append(cur); cur = 1
    runs.append(cur)
    return runs


def staircase_regularity(line, win=5):
    """Fraction of windows of consecutive runs (interior runs only) whose lengths are
    equal or change monotonically (allowing one-off alternation such as 2,3,2,3)."""
    ok = tot = 0
    for c in chains(line):
        c = np.asarray(c, int)
        if len(c) < 6:
            continue
        # split the chain where its direction octant changes so each piece is monotone
        pieces = _monotone_pieces(c)
        for pc in pieces:
            r = runs_of_chain(pc)[1:-1]
            if len(r) < 3:
                continue
            for k in range(len(r) - 2):
                a, b, cc = r[k], r[k + 1], r[k + 2]
                # monotone runs = a smooth curve; k, k+1, k = a straight line whose
                # slope lies between 1/k and 1/(k+1)
                good = (a <= b <= cc) or (a >= b >= cc) or (a == cc and abs(a - b) == 1)
                ok += good; tot += 1
    return ok / max(tot, 1), tot


def _monotone_pieces(c):
    d = np.diff(c, axis=0)
    sx = np.sign(d[:, 0]); sy = np.sign(d[:, 1])
    pieces = []; start = 0
    cur_sx = cur_sy = 0
    for k in range(len(d)):
        if sx[k] and cur_sx and sx[k] != cur_sx or sy[k] and cur_sy and sy[k] != cur_sy:
            pieces.append(c[start:k + 1]); start = k; cur_sx = cur_sy = 0
        if sx[k]: cur_sx = sx[k]
        if sy[k]: cur_sy = sy[k]
    pieces.append(c[start:])
    return pieces
