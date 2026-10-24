"""FETCH! logo track: the letters, the paw, their navy outline and depth faces and the
blue gaps inside the logo, rebuilt as clean pixel art on the 320 x 240 grid.

Pipeline (see out/notes.md):
 1. label every source pixel with a logo palette colour; anti-aliased edge pixels take the
    colour of the nearest flat pixel, so blends never become a third colour;
 2. material masks at full resolution: FILL (warm letter paint), NAVY, GAP (blue inside);
 3. each mask's contours are smoothed (corners kept, straight runs made exact) and
    rasterized onto the uniform grid by cell-centre coverage (no anti-aliasing);
 4. the navy band is given a minimum constant thickness, the gaps are cleaned;
 5. the fill gets a rule-based ordered dither between yellow and orange (5 levels, one
    global phase), banded where the painting's gradient is, measured per letter;
 6. one-pixel light-yellow highlight on top-facing edges and red-orange on bottom-facing
    edges, where the painting has them, cleaned with pixel-perfect line rules.
"""
import numpy as np, json, os, sys
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_common import *

OUT = os.environ.get('LOGO_OUT', '/home/claude/wt/rg-logo/out')
CACHE = os.environ.get('LOGO_CACHE', '/tmp/claude-0/lg/cache')
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)

# working crop of the source (source px)
X0, Y0, X1, Y1 = 880, 40, 2300, 660
# the tagline plate (starts with its dark top line at y 578; its left border at x ~1150)
PLATE = (1150, 578, 2195, 1792)

# prototypes: name, hex, material. Blend prototypes (b_*) exist only to be recognised and
# then snapped; they never reach the output.
PROTO = [
    ('navy', '011135', 'N'), ('b_navy_blue', '022753', 'x'),
    ('yellow', 'ffbc03', 'F'), ('orange', 'ff6203', 'F'), ('b_yo', 'ff8f03', 'x'),
    ('hilite', 'ffe56f', 'F'), ('b_yh', 'ffd02f', 'x'), ('red', 'd83813', 'F'),
    ('b_brown', '574722', 'x'),
    ('sky', '2b86d5', 'B'), ('blue1', '1676c6', 'B'), ('blue2', '0f6dc1', 'B'), ('blue3', '075eac', 'B'),
    ('blue4', '02478d', 'B'), ('blue5', '013a77', 'B'), ('sky_l', '439bdc', 'B'), ('sky_l2', '40a9f5', 'B'),
    ('green', '85a40c', 'G'), ('green_d', '3b5d26', 'G'),
]
NAMES = [p[0] for p in PROTO]
IDX = {n: i for i, n in enumerate(NAMES)}
MAT = np.array([p[2] for p in PROTO])


def flat_mask(a, thr=7.0):
    f = a.astype(np.float32)
    g = np.zeros(a.shape[:2], np.float32)
    for ax in (0, 1):
        d = np.abs(np.roll(f, -1, ax) - np.roll(f, 1, ax)).max(2) * 0.5
        g = np.maximum(g, d)
    return g < thr


def label(force=False):
    p = os.path.join(CACHE, 'label.npz')
    if os.path.exists(p) and not force:
        z = np.load(p); return z['L'], z['pal'], z['flat']
    a = load_src()[Y0:Y1, X0:X1]
    lab = srgb_to_lab(a)
    pro = np.array([hx(h) for _, h, _ in PROTO])
    pl = srgb_to_lab(pro)
    d = ((lab[:, :, None, :] - pl[None, None]) ** 2).sum(-1)
    L0 = d.argmin(-1).astype(np.int16)
    flat = flat_mask(a)
    real = MAT[L0] != 'x'
    seed = flat & real
    # palette colour = mean of the most common 4-level bin among flat pixels of that label
    pal = pro.astype(np.float32).copy()
    for i in range(len(PROTO)):
        m = seed & (L0 == i)
        if m.sum() < 30:
            continue
        sub = a[m].astype(np.int32)
        q = sub // 4; key = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]
        v, n = np.unique(key, return_counts=True)
        pal[i] = sub[key == v[n.argmax()]].mean(0)
    pal = np.round(pal).astype(np.uint8)
    pl = srgb_to_lab(pal)
    # snap every other pixel to the closest colour among nearby seed pixels (radius <= 5)
    L = np.where(seed, L0, -1).astype(np.int16)
    best = np.where(seed, 0.0, np.inf).astype(np.float32)
    offs = [(dy, dx) for r in range(1, 6) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if max(abs(dy), abs(dx)) == r]
    for dy, dx in offs:
        Ls = np.roll(L0, (-dy, -dx), (0, 1)); fs = np.roll(seed, (-dy, -dx), (0, 1))
        dd = ((lab - pl[Ls]) ** 2).sum(-1) + 2.0 * (dy * dy + dx * dx)
        dd = np.where(fs, dd, np.inf)
        upd = (~seed) & (dd < best)
        best[upd] = dd[upd]; L[upd] = Ls[upd]
    # anything still unlabelled: nearest real prototype
    un = L < 0
    if un.any():
        dr = np.where(np.array([m != 'x' for m in MAT])[None, None, :], d, np.inf)
        L[un] = dr.argmin(-1)[un]
    np.savez_compressed(p, L=L, pal=pal, flat=flat)
    return L, pal, flat


def masks(L):
    H, W = L.shape
    yy, xx = np.indices((H, W))
    plate = (xx + X0 >= PLATE[0]) & (yy + Y0 >= PLATE[1]) & (xx + X0 <= PLATE[2])
    m = MAT[L]
    F = clean_mask((m == 'F') & ~plate, 80)
    N = (m == 'N') & ~plate
    lab, n = ndi.label(F | N)
    ids = np.unique(lab[F]); ids = ids[ids > 0]
    s = ndi.sum(F, lab, ids)
    C = lab == ids[np.argmax(s)]
    F &= C
    SOLID = ndi.binary_fill_holes(C)
    # narrow sky inlets between letters belong to the logo too (closing, 25 px)
    CL = ndi.binary_fill_holes(ndi.binary_closing(np.pad(SOLID, 20), structure=np.ones((25, 25)))[20:-20, 20:-20])
    CL &= ~plate
    GAP = CL & ~C
    return dict(F=F, N=N & C, C=C, SOLID=SOLID, CL=CL, GAP=GAP, plate=plate)


def to_full(m):
    """crop mask -> full-size source mask"""
    out = np.zeros((H_SRC, W_SRC), bool)
    out[Y0:Y1, X0:X1] = m
    return out


def raster(mask_crop, s=8.0, pre=2.5, min_area=60, thr=0.5, straight_tol=2.5):
    polys = smooth_polys(mask_crop, s=s, pre=pre, min_area=min_area, straight_tol=straight_tol)
    m = fill_polys(polys, mask_crop.shape)
    full = to_full(m)
    I, J = cell_index(H_SRC, W_SRC)
    cov = coverage(full, I, J)
    return cov >= thr, full, cov


if __name__ == '__main__':
    L, pal, flat = label(force='-f' in sys.argv)
    print({n: tohex(pal[i]) for i, n in enumerate(NAMES)})


# ------------------------------------------------------------------ geometry
T_OUT = 2.0            # navy outline thickness in cells (painting: 13 px = 1.73 cells on top faces)


def edt_cells(m):
    """Euclidean distance (in cells) from every pixel outside m to m, on a crop mask."""
    return ndi.distance_transform_edt(~m, sampling=(1.0 / PY, 1.0 / PX))


def cell_disk_dilate(m, r):
    """Cells within Euclidean distance r (cell units) of m."""
    return ndi.distance_transform_edt(~m) <= r + 1e-6


def paw_parts(F):
    """Fill components of the paw (toes and main pad) in the crop."""
    lab, n = ndi.label(F)
    toes, pad = [], None
    for c in range(1, n + 1):
        m = lab == c
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean() + X0, ys.mean() + Y0
        if cx < 2040 or cy < 400:
            continue
        if m.sum() > 4000:
            pad = m
        else:
            toes.append(m)
    return toes, pad


def snap_half(v):
    """nearest multiple of 0.5 (a cell centre or a cell border) in cell units"""
    return np.round(v * 2) / 2


def raster_ellipse(cx, cy, a, b):
    yy, xx = np.indices((NY, NX))
    return (((xx + 0.5 - cx) / a) ** 2 + ((yy + 0.5 - cy) / b) ** 2) <= 1.0


def paw_cells(F):
    """Main pad: the painted pad, smoothed and rasterized where it is painted. Toes: round
    pixel blobs (axis-aligned pixel ellipses with no one-pixel tips) at the painted size
    (area +5 % to +35 % over the painted toe mask, which the painting's soft edges undercount) and position, best overlap with the painted
    toe, one navy cell clear of the pad and of each other as painted."""
    toes, pad = paw_parts(F)
    out = np.zeros((NY, NX), bool)
    info = []
    I, J = cell_index(H_SRC, W_SRC)
    if pad is not None:
        pol = smooth_polys(pad, s=6.0, straight_tol=2.0, pre=2.0, min_area=200, thr=60.0)
        P = fill_polys(pol, pad.shape)
        padc = notch_bump_clean(coverage(to_full(P), I, J) >= 0.5)
        out |= padc
        ys, xs = np.nonzero(padc); info.append(('pad', int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())))
    for m in sorted(toes, key=lambda m: -m.sum()):
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min() + Y0 - 30, ys.max() + Y0 + 30, xs.min() + X0 - 30, xs.max() + X0 + 30
        Jw, Iw = J[y0:y1, x0:x1], I[y0:y1, x0:x1]
        tgt = to_full(m)[y0:y1, x0:x1]
        area = m.sum() / (PX * PY)
        cx = (xs.mean() + X0 + 0.5) / PX; cy = (ys.mean() + Y0 + 0.5) / PY
        a0, b0 = 2 * xs.std() / PX, 2 * ys.std() / PY
        dist = ndi.distance_transform_edt(~out)
        best = None
        for scx in np.arange(np.round(cx * 2) / 2 - 1, np.round(cx * 2) / 2 + 1.01, 0.5):
            for scy in np.arange(np.round(cy * 2) / 2 - 1, np.round(cy * 2) / 2 + 1.01, 0.5):
                for fa in np.arange(0.85, 1.41, 0.05):
                    for fb in np.arange(0.85, 1.41, 0.05):
                        e = raster_ellipse(scx, scy, a0 * fa, b0 * fb)
                        if not (1.15 * area <= e.sum() <= 1.5 * area):   # painted blobs read larger than their hard mask
                            continue
                        rows = e.sum(1)[e.any(1)]; cols = e.sum(0)[e.any(0)]
                        if len(rows) < 3 or rows[0] < 2 or rows[-1] < 2 or cols[0] < 2 or cols[-1] < 2:
                            continue
                        if np.abs(np.diff(rows)).max() > 2 or np.abs(np.diff(cols)).max() > 2:
                            continue
                        if dist[e].min() < 2.0:
                            continue
                        ef = e[Jw, Iw]
                        iou = (ef & tgt).sum() / max((ef | tgt).sum(), 1)
                        sc = iou + 0.01 * e.sum()            # prefer the fuller blob
                        if best is None or sc > best[6]:
                            best = (iou, e, scx, scy, a0 * fa, b0 * fb, sc)
        out |= best[1]
        info.append(('toe', best[2], best[3], round(best[4], 2), round(best[5], 2), round(best[0], 3), int(best[1].sum()), round(area, 1)))
    return out, info


def painted_depth(M, letter_crop):
    """Median painted navy thickness (cells) below and left of one painted letter: from each
    bottom- / left-facing paint edge, through navy, to sky or a blue gap."""
    F, C = M['F'], M['C']
    H, W = F.shape
    out = {}
    for name, (dy, dx), P in (('down', (1, 0), PY), ('left', (0, -1), PX)):
        edge = letter_crop & ~shift(letter_crop, dy, dx)
        ys, xs = np.nonzero(edge)
        runs = []
        for y, x in zip(ys[::3], xs[::3]):
            k = 0; yy, xx = y + dy, x + dx
            while 0 <= yy < H and 0 <= xx < W and C[yy, xx] and not F[yy, xx] and k < 200:
                k += 1; yy += dy; xx += dx
            if 0 <= yy < H and 0 <= xx < W and not F[yy, xx] and not C[yy, xx] and k < 8 * P:
                runs.append(k)          # longer runs cross into another letter's navy
        out[name] = float(np.median(runs)) / P if runs else 0.0
    return out


def extrude_letters(fill, M):
    """Each letter's fill swept down by (depth_down - 2) and left by (depth_left - 2) cells,
    the painted depth minus the outline that wraps it, so outline plus extrusion is as thick as
    painted below and left of every letter."""
    I, J = cell_index(H_SRC, W_SRC)
    Jc, Ic = J[Y0:Y1, X0:X1], I[Y0:Y1, X0:X1]
    lab, n = ndi.label(M['F'])
    rl, rn = ndi.label(fill)
    ext = fill.copy()
    depth = {}
    for c in range(1, n + 1):
        m = lab == c
        if m.sum() < 3000:
            continue
        v = rl[Jc[m], Ic[m]]; v = v[v > 0]
        if not len(v):
            continue
        rc = np.bincount(v).argmax()
        d = painted_depth(M, m)
        td = max(0, int(np.floor(d['down'] + 0.5)) - int(T_OUT))
        tl = max(0, int(np.floor(d['left'] + 0.5)) - int(T_OUT))
        f = rl == rc
        e = f.copy()
        for k in range(1, td + 1):
            e |= shift(f, -k, 0)            # value from k rows above: the shape moves down
        e2 = e.copy()
        for k in range(1, tl + 1):
            e2 |= shift(e, 0, k)            # moves left
        ext |= e2
        depth[int(rc)] = (round(d['down'], 2), round(d['left'], 2), td, tl)
    return ext, depth


def carve_letters(fill, sep=3.0):
    """Letters to the right sit in front: a letter's cells closer than sep (cell units) to
    a letter on its right are given to that letter's outline, so two navy cells always
    separate two letters, as the constant outline needs."""
    lab, n = ndi.label(fill)
    cs = sorted(range(1, n + 1), key=lambda c: np.nonzero(lab == c)[1].mean())
    out = fill.copy()
    for k, c in enumerate(cs):
        front = lab == c
        d = ndi.distance_transform_edt(~front)
        for b in cs[:k]:
            out &= ~((lab == b) & (d < sep))
    return clean_mask(out, 4, 0)


def notch_bump_clean(m, it=3):
    """remove one-cell bumps (a cell with a single 4-neighbour inside) and fill one-cell
    notches (an outside cell with three 4-neighbours inside)."""
    m = m.copy()
    for _ in range(it):
        n4 = sum(shift(m, dy, dx).astype(int) for dy, dx in N4)
        bump = m & (n4 <= 1)
        notch = ~m & (n4 >= 3)
        if not bump.any() and not notch.any():
            break
        m = (m & ~bump) | notch
    return m


def geometry(L, M, s=12.0, tol=7.0):
    I, J = cell_index(H_SRC, W_SRC)
    cov = lambda m: coverage(to_full(m), I, J)
    # 1. letter fill: smoothed polygons at full resolution, rasterized by coverage
    toes, pad = paw_parts(M['F'])
    pawF = np.zeros_like(M['F'])
    for m in toes + ([pad] if pad is not None else []):
        pawF |= m
    fpol = smooth_polys2(M['F'] & ~pawF, s=8.0, rms_tol=3.0, max_tol=8.0, pre=2.0, min_area=80)
    fillP = fill_polys(fpol, M['F'].shape)
    fill = cov(fillP) >= 0.5
    fill = carve_letters(fill)
    for _ in range(2):                 # one-cell tips (a cell with at most one 4-neighbour)
        n4 = sum(shift(fill, dy, dx).astype(int) for dy, dx in N4)
        fill &= ~(fill & (n4 <= 1))
    pawc, pawinfo = paw_cells(M['F'])
    fill = (fill & ~cell_disk_dilate(pawc, 2.0)) | pawc   # the paw sits in front of the "!"
    # 2. the painting's own silhouette
    opol = smooth_polys2(M['CL'], s=8.0, rms_tol=3.0, max_tol=8.0, pre=2.0, min_area=200)
    outP = fill_polys(opol, M['CL'].shape)
    painted = cov(outP) >= 0.5
    # 3. depth faces: each letter extruded down and left by its painted depth (measured per
    #    letter in cells), then the constant 2-cell outline around fill and extrusion
    ext, depth = extrude_letters(fill & ~pawc, M)
    base = cell_disk_dilate(fill, T_OUT)
    ext_base = cell_disk_dilate(ext, T_OUT) & ndi.binary_dilation(painted)
    extra = painted & ~base & ~ext_base
    extra = ndi.binary_opening(extra, structure=np.ones((2, 2)))   # no one-cell slivers or lumps
    outer = base | ext_base | extra
    outer = ndi.binary_fill_holes(ndi.binary_closing(np.pad(outer, 4), structure=np.ones((4, 4)))[4:-4, 4:-4])
    outer = notch_bump_clean(outer) | base
    # lumps one cell deep and up to three long on the outer contour (a 3x3 opening removes
    # them, square corners and staircases of any slope survive it); the base outline stays
    op = ndi.binary_opening(np.pad(outer, 3), structure=np.ones((3, 3)))[3:-3, 3:-3]
    lm = outer & ~op & ~base
    lab, n = ndi.label(lm)
    for c in range(1, n + 1):
        if (lab == c).sum() <= 3:
            outer &= ~(lab == c)
    # 4. gaps and counters as open as painted: the painting's blue inside, only kept off the
    #    fill itself (never touching a letter, so the letter keeps a navy edge)
    gpol = smooth_polys2(M['GAP'], s=6.0, rms_tol=3.0, max_tol=8.0, pre=2.0, min_area=150)
    gapP = fill_polys(gpol, M['GAP'].shape)
    gap = (cov(gapP) >= 0.5) & outer & ~ndi.binary_dilation(fill, structure=np.ones((3, 3)))
    gap = clean_mask(gap, 3, 0)
    lab, n = ndi.label(gap)            # tiny inlets read as notches in the outline: navy
    for c in range(1, n + 1):
        m = lab == c
        if (m & ndi.binary_dilation(~outer)).any() and m.sum() < 4:
            gap &= ~m
    return dict(outer=outer, fill=fill, gap=gap, base=base, painted=painted, fillP=fillP, pawc=pawc, pawinfo=pawinfo,
                ext=ext, depth=depth)


# ------------------------------------------------------------------ colour
BAYER = np.array([[0, 2], [3, 1]])     # 2x2 ordered dither; level k (0..4): orange where BAYER < k


def cell_mean(f_crop, I=None, J=None):
    full = np.zeros((H_SRC, W_SRC), np.float64); full[Y0:Y1, X0:X1] = f_crop
    w = np.zeros((H_SRC, W_SRC), np.float64); w[Y0:Y1, X0:X1] = 1
    if I is None:
        I, J = cell_index(H_SRC, W_SRC)
    cell = (J.astype(np.int64) * NX + I).ravel()
    s = np.bincount(cell, weights=(full * w).ravel(), minlength=NX * NY)
    n = np.bincount(cell, weights=w.ravel(), minlength=NX * NY)
    return (s / np.maximum(n, 1e-9)).reshape(NY, NX)


def isotonic(y, w):
    """weighted isotonic (non-decreasing) regression, pool adjacent violators."""
    blocks = [[y[i] * w[i], w[i], 1] for i in range(len(y))]
    out = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][0] / max(out[-2][1], 1e-9) > out[-1][0] / max(out[-1][1], 1e-9):
            a2 = out.pop(); a1 = out.pop()
            out.append([a1[0] + a2[0], a1[1] + a2[1], a1[2] + a2[2]])
    res = []
    for s, ww, n in out:
        res += [s / max(ww, 1e-9)] * n
    return np.array(res)


def gradient_levels(L, fill, sigma=12.0, smooth=1.0, min_cells=8):
    """Per cell dither level 0..4 from the painting's local orange share, fitted per letter
    as a non-decreasing function of the row (the painting's bands run horizontally)."""
    # only the letters' interior counts (9 px in from the paint edge): the stripes and the
    # side faces say nothing about the gradient; the normalised blur carries it to the edges
    inner = ndi.binary_erosion(MAT[L] == 'F', structure=np.ones((3, 3)), iterations=9)
    Yl = (L == IDX['yellow']) & inner; Ol = (L == IDX['orange']) & inner
    # tone share from the painting's own luma (its anti-aliased checker edges are mid-orange,
    # which makes the painted bands read darker than a pure yellow/orange count says)
    a = load_src()[Y0:Y1, X0:X1]
    lu = luma(a); pal = None
    ly, lo = 187.4, 133.8                     # luma of #febd03 and #fe6202
    t = np.clip((ly - lu) / (ly - lo), 0, 1)
    mid = inner & np.isin(L, [IDX['yellow'], IDX['orange']])
    num = ndi.gaussian_filter((t * mid).astype(np.float32), sigma)
    den = ndi.gaussian_filter(mid.astype(np.float32), sigma)
    u = num / np.maximum(den, 1e-3)
    # wider blur where the interior is far (cells along the edges), so every fill cell has
    # an estimate from the nearest interior paint
    num2 = ndi.gaussian_filter((t * mid).astype(np.float32), 2 * sigma)
    den2 = ndi.gaussian_filter(mid.astype(np.float32), 2 * sigma)
    u = np.where(den > 0.05, u, num2 / np.maximum(den2, 1e-4))
    uc = cell_mean(u)
    lab, n = ndi.label(fill)
    # 2-D field: the painting's gradient follows each stroke, so no per-row model
    a = ndi.gaussian_filter(np.where(fill, uc, 0.0), smooth); b = ndi.gaussian_filter(fill.astype(float), smooth)
    ufit = np.where(fill, a / np.maximum(b, 1e-6), 0.0)
    # three distinct bands as painted: solid yellow, exact one-cell checker (the painted
    # checker squares are 9 to 10 px = 1.2 to 1.3 cells, measured per letter), solid orange
    level = np.where(ufit < 0.2, 0, np.where(ufit < 0.7, 2, 4)).astype(np.int8)
    level = merge_small_levels(level, fill, min_cells)
    level = min_row_runs(level, fill, ufit)
    return level, ufit, uc, lab


def min_row_runs(level, fill, ufit):
    """In every column a dither band is at least two rows tall (one full pattern period);
    a one-row band joins the neighbouring band whose level is closer to the painting's value."""
    level = level.copy()
    for x in range(NX):
        col = np.flatnonzero(fill[:, x])
        if len(col) < 3:
            continue
        for _ in range(2):
            for i, y in enumerate(col):
                up = level[col[i - 1], x] if i > 0 and col[i - 1] == y - 1 else None
                dn = level[col[i + 1], x] if i + 1 < len(col) and col[i + 1] == y + 1 else None
                v = level[y, x]
                if up is not None and dn is not None and up != v and dn != v:
                    level[y, x] = up if abs(ufit[y, x] * 4 - up) <= abs(ufit[y, x] * 4 - dn) else dn
    return level


def merge_small_levels(level, fill, min_cells):
    """Level islands smaller than min_cells take the most common level around them."""
    level = level.copy()
    for _ in range(3):
        changed = False
        for k in range(5):
            lab, n = ndi.label((level == k) & fill)
            for c in range(1, n + 1):
                m = lab == c
                if m.sum() >= min_cells:
                    continue
                ring = ndi.binary_dilation(m) & ~m & fill
                if ring.any():
                    level[m] = np.bincount(level[ring], minlength=5).argmax(); changed = True
        if not changed:
            break
    return level


def dither5(level):
    yy, xx = np.indices((NY, NX))
    return BAYER[yy % 2, xx % 2] < level      # True = orange (5-level zones, not drawn)


LH, LY, LO, LR = 224.0, 187.23, 133.70, 99.8   # luma of #ffe671, #febd03, #fe6202, #da3611


BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def pattern(k):
    """Cells of the second tone for density k/8 (k = 0..8): one 4x4 Bayer matrix on absolute
    cell position (threshold 2k of 16), so every density is a nested subset of the next and
    every dot sits on the same lattice; k = 4 is the exact one-cell checker."""
    y, x = np.indices((NY, NX))
    return BAYER4[y % 4, x % 4] < 2 * int(k)


def ramp_tones(level):
    """level -8..16 on one scale: -8..0 highlight to yellow, 0..8 yellow to orange, 8..16
    orange to red-orange. Returns (base, second, k) palette names and density for a level."""
    if level < 0:
        return 'yellow', 'hilite', -level
    if level <= 8:
        return 'yellow', 'orange', level
    return 'orange', 'red', level - 8


def dither(level):
    """True where the level's second tone goes (used for the yellow/orange part)."""
    out = np.zeros((NY, NX), bool)
    for k in range(9):
        out |= (level == k) & pattern(k)
    out |= level > 8
    return out


def luma_to_level(pl):
    if pl > LY:
        return -min(8.0, (pl - LY) / (LH - LY) * 8)
    if pl >= LO:
        return (LY - pl) / (LY - LO) * 8
    return 8 + min(8.0, (LO - pl) / (LO - LR) * 8)


def level_luma(k):
    b, a, d = ramp_tones(k)
    T = {'hilite': LH, 'yellow': LY, 'orange': LO, 'red': LR}
    return T[b] + (T[a] - T[b]) * d / 8


LEVELS = list(range(-8, 17))


def min_run_of(k):
    d = ramp_tones(k)[2]
    return 1        # all densities share one Bayer lattice, so a level may change on any row


def ramp_rows(tl, table, w, jump=0.02, allow=None, gpen=None):
    gpen = np.zeros_like(table) if gpen is None else gpen
    """Levels per row minimising the weighted squared error between the painting's row luma
    tl[i] and the luma the level really gives on that row's cells (table[i, level]); sparse
    densities are held for at least two rows, and jumps of more than one level cost a little,
    so the ramp fades through the densities instead of switching."""
    n = len(tl); INF = 1e18; R = 2
    nl = len(LEVELS)
    mr = [min_run_of(k) for k in LEVELS]
    # a dithered row costs as much as a 3-luma miss: a row within ~3 luma of a flat tone
    # stays flat, so the solid yellow and orange areas get no stray dots
    dz = np.array([0.0 if k in (-8, 0, 8, 16) else 3.0 ** 2 for k in LEVELS])
    cost = np.full((n, nl, R + 1), INF); back = np.zeros((n, nl, R + 1, 2), int)
    for k in range(nl):
        cost[0, k, 1] = w[0] * ((tl[0] - table[0, k]) ** 2 + dz[k] + gpen[0, k]) + (0 if allow is None or allow[0, k] else INF)
    for i in range(1, n):
        for k in range(nl):
            c = w[i] * ((tl[i] - table[i, k]) ** 2 + dz[k] + gpen[i, k])
            if allow is not None and not allow[i, k]:
                continue
            for r in range(1, R + 1):
                rr = min(r + 1, R)
                v = cost[i - 1, k, r] + c
                if v < cost[i, k, rr]:
                    cost[i, k, rr] = v; back[i, k, rr] = (k, r)
            for kp in range(nl):
                if kp == k:
                    continue
                pen = jump * w[i] * 45.0 * max(0, abs(kp - k) - 1)
                for r in range(mr[kp], R + 1):
                    v = cost[i - 1, kp, r] + c + pen
                    if v < cost[i, k, 1]:
                        cost[i, k, 1] = v; back[i, k, 1] = (kp, r)
    best = (INF, 0, R)
    for k in range(nl):
        for r in range(mr[k], R + 1):
            if cost[-1, k, r] < best[0]:
                best = (cost[-1, k, r], k, r)
    out = np.zeros(n, int); k, r = best[1], best[2]
    for i in range(n - 1, -1, -1):
        out[i] = LEVELS[k]
        if i:
            k, r = back[i, k, r]
    return out


def row_ramp(fill, skip, stripes_mask, src_luma_cells, ofrac=None):
    """Per shape (letter, pad, toe), per cell row: the painting's mean luma over the shape's
    dithered cells (not stripes, not edge cells when the row has inner cells) is the target;
    each candidate level is scored by the luma it really gives on exactly those cells."""
    D = ring_dirs(fill)
    ring = D['up'] | D['down'] | D['left'] | D['right']
    lab, n = ndi.label(fill & ~skip)
    level = np.zeros((NY, NX), np.int16)
    T = {'hilite': LH, 'yellow': LY, 'orange': LO, 'red': LR}
    pats = [pattern(k) for k in range(9)]
    info = {}
    for c in range(1, n + 1):
        m = lab == c
        body = m & ~stripes_mask
        core = body & ~ring
        rows = np.flatnonzero(body.any(1))
        if not len(rows):
            continue
        tl, ws, table, ns = [], [], [], []
        for r in rows:
            sel = core[r] if core[r].sum() >= 2 else body[r]
            ns.append(int(sel.sum()))
            tl.append(src_luma_cells[r][sel].mean()); ws.append(max(int(body[r].sum()), 1))
            row = []
            for k in LEVELS:
                b, a2, d = ramp_tones(k)
                frac = pats[d][r][sel].mean()
                row.append(T[b] + (T[a2] - T[b]) * frac)
            table.append(row)
        # where dither may go: the solid top stays solid down to the first row where the
        # painting's interior shows orange paint (its fade start); toes are too small for
        # dither, each toe row is solid yellow or solid orange
        allow = np.ones((len(rows), len(LEVELS)), bool)
        LV = np.array(LEVELS)
        if m.sum() < 40:
            allow[:] = np.isin(LV, [0, 8])[None]
        elif ofrac is not None:
            # fade start: the first row from which the painting stays at least 4 luma darker
            # than solid yellow for three rows running (its first sparse orange)
            dk = np.array(tl) <= LY - 4
            start = next((i for i in range(len(rows)) if dk[i:i + 3].all()), len(rows))
            allow[:start] = (LV == 0)[None]
            allow[start:] &= (LV >= 0)[None]
        # the row-luma gate as a hard constraint on rows that can hold a fine density (>= 5
        # cells): every level within 5.9 luma of the painting is allowed there, overriding the
        # solid top only when no solid level is close enough
        err = np.abs(np.array(table) - np.array(tl)[:, None])
        pen = np.zeros_like(err)
        for i in range(len(rows)):
            if m.sum() < 40 or ns[i] < 5:
                continue
            ok = err[i] <= 8.0
            if not (allow[i] & ok).any() and (ok & (LV >= 0)).any():
                allow[i] |= ok & (LV >= 0)       # the painting's own fade starts here
                for j in (i - 1, i + 1):         # and its neighbour, so a sparse density
                    if 0 <= j < len(rows):        # can be held for two rows
                        allow[j] |= ok & (LV >= 0) & (err[j] <= 8.0)
            pen[i] = np.where(ok, 0.0, 4e3)       # soft: the DP stays feasible
        lv = ramp_rows(np.array(tl), np.array(table), np.array(ws, float), allow=allow, gpen=pen)
        for r, k in zip(rows, lv):
            level[r][m[r]] = k
        info[int(c)] = (rows.tolist(), [round(float(v), 1) for v in tl], lv.tolist())
    return level, info


def ring_dirs(fill):
    return {k: fill & ~shift(fill, dy, dx) for k, (dy, dx) in
            dict(up=(-1, 0), down=(1, 0), left=(0, -1), right=(0, 1)).items()}


def stripes(L, fill, ufit):
    def ev(name, grow=3):
        m = ndi.maximum_filter(L == IDX[name], size=grow)
        return cell_mean(m.astype(np.float32))
    e_hi, e_red = ev('hilite'), ev('red')
    D = ring_dirs(fill)
    hi = D['up'] & (e_hi >= 0.2)
    red = D['down'] & ~hi & (e_red >= 0.2)
    side = (D['left'] | D['right']) & ~hi & ~red & ~D['up'] & ~D['down']
    hi |= side & D['left'] & (e_hi >= 0.3) & (e_hi >= e_red)
    red |= side & ~hi & (e_red >= 0.35)
    return hi, red, e_hi, e_red


GAP_GROUPS = {'sky': ['sky', 'sky_l', 'sky_l2'], 'blue1': ['blue1', 'blue2'], 'blue3': ['blue3', 'blue4'], 'blue5': ['blue5']}


def gap_colours(L, gap, min_cells=4):
    """Per gap cell the painting's dominant blue (four groups), then islands merged so each
    shade is a clean patch."""
    names = list(GAP_GROUPS)
    votes = np.stack([cell_mean(np.isin(L, [IDX[n] for n in GAP_GROUPS[g]]).astype(np.float32)) for g in names], -1)
    k = votes.argmax(-1)
    k = np.where(gap, k, -1)
    # 3x3 mode filter inside the gap, twice
    for _ in range(2):
        cnt = np.stack([ndi.uniform_filter((k == i).astype(float), 3) for i in range(len(names))], -1)
        k = np.where(gap, cnt.argmax(-1), -1)
    for _ in range(3):
        for i in range(len(names)):
            lab, n = ndi.label(k == i)
            for c in range(1, n + 1):
                m = lab == c
                if m.sum() >= min_cells:
                    continue
                ring = ndi.binary_dilation(m) & ~m & gap
                if ring.any():
                    k[m] = np.bincount(k[ring][k[ring] >= 0], minlength=len(names)).argmax()
    return k, names


def build(verbose=True):
    L, pal, flat = label()
    M = masks(L)
    G = geometry(L, M)
    outer, fill, gap = G['outer'], G['fill'], G['gap']
    level, ufit, uc, lab = gradient_levels(L, fill)      # 5-level zones: which half is orange
    org = dither5(level)
    hi, red, e_hi, e_red = stripes(L, fill, ufit)
    # the paw: pure rule (light top, red bottom) so every pad stays symmetric
    pw = G['pawc']; D = ring_dirs(fill)
    hi = (hi & ~pw) | (pw & D['up'])
    red = (red & ~pw) | (pw & D['down'] & ~D['up'])
    hi, red = clean_stripes(hi, red, fill)
    hi, red = complete_runs(hi, red, fill)
    hi, red, lite = complete_sides(hi, red, fill, level, L)
    zone = level
    _, _, hi, red = paw_colours(G, np.zeros_like(level), org, hi, red)
    hi, red = clean_stripes(hi, red, fill)
    lite &= ~hi & ~red & ~G['pawc']
    red = deep_bottom(red, fill & ~G['pawc'], L, hi)
    hi = deep_top(hi, fill & ~G['pawc'], L, red)
    hi, red = clean_stripes(hi, red, fill)
    lite &= ~hi & ~red
    # the fill: an ordered-dither ramp per letter, row by row from the painting's luma
    src_l = cell_mean(luma(load_src()[Y0:Y1, X0:X1]))
    ofr = cell_mean((L == IDX['orange']).astype(np.float32))
    toes = G['pawc'] & ~largest(G['pawc'])
    red &= ~toes                       # toes: solid tone plus the painted 1-cell highlight
    level, ramp = row_ramp(fill, np.zeros_like(fill), hi | red | lite, src_l, ofr)
    gk, gnames = gap_colours(L, gap)
    P = lambda n: pal[IDX[n]]
    idx = np.full((NY, NX), -1, np.int16)     # palette index map (into PROTO), -1 transparent
    idx[outer] = IDX['navy']
    for i, g in enumerate(gnames):
        idx[gap & (gk == i)] = IDX[g]
    for k in np.unique(level[fill]):
        b, a2, d = ramp_tones(int(k))
        m = fill & (level == k)
        idx[m] = IDX[b]
        idx[m & pattern(d)] = IDX[a2]
    idx[lite] = IDX['yellow']
    idx[hi] = IDX['hilite']; idx[red] = IDX['red']
    return dict(L=L, pal=pal, M=M, G=G, level=level, zone=zone, ufit=ufit, uc=uc, hi=hi, red=red, lite=lite, idx=idx,
                gk=gk, ramp=ramp, src_l=src_l)


def largest(m):
    lab, n = ndi.label(m)
    if not n:
        return m
    return lab == (np.bincount(lab.ravel())[1:].argmax() + 1)


def clean_stripes(hi, red, fill):
    """pixel-perfect stripes: one-cell gaps along the edge bridged, lone cells dropped,
    L-corner doubles removed."""
    from logo_lines import remove_lcorners, bridge_gaps, drop_short
    D = ring_dirs(fill)
    ring = D['up'] | D['down'] | D['left'] | D['right']
    out = []
    side = (D['left'] | D['right']) & ~D['up'] & ~D['down']
    for s in (hi, red):
        s = bridge_gaps(s, ring & ~(hi | red) | s)
        s = remove_lcorners(s)
        s = drop_short(s, 2)
        # stripe pieces that run only along a side face need three cells to read as a line
        lab, n = ndi.label(s, structure=np.ones((3, 3)))
        for c in range(1, n + 1):
            m = lab == c
            if (m & ~side).sum() == 0 and m.sum() < 3:
                s &= ~m
        out.append(s)
    hi, red = out
    red &= ~hi
    return hi, red


def complete_runs(hi, red, fill):
    """A top-facing run that is mostly highlight becomes highlight end to end; a bottom-facing
    run that is mostly red becomes red end to end (no stray yellow corner cells)."""
    D = ring_dirs(fill)
    for face, s, other in (('up', hi, red), ('down', red, hi)):
        f = D[face]
        lab, n = ndi.label(f, structure=np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]]))
        for c in range(1, n + 1):
            m = lab == c
            if (s & m).sum() >= 0.5 * m.sum():
                s |= m
                other &= ~m
    return hi, red


def evidence(L):
    """Per cell: share of painted highlight (grown 1 px), red-orange (grown 1 px) and of
    flat light paint (yellow or highlight, not grown) inside the cell."""
    g = lambda m: cell_mean(ndi.maximum_filter(m, size=3).astype(np.float32))
    e_hi = g(L == IDX['hilite']); e_red = g(L == IDX['red'])
    e_lite = cell_mean(np.isin(L, [IDX['yellow'], IDX['hilite']]).astype(np.float32))
    return e_hi, e_red, e_lite


def chains(m, horizontal=False):
    st = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]]) if horizontal else np.ones((3, 3))
    lab, n = ndi.label(m, structure=st)
    return [lab == c for c in range(1, n + 1)]


def complete_sides(hi, red, fill, level, L):
    """Side and orange-half edges as whole chains, decided by the painting's evidence along
    the chain (no dashed lines). Left faces: highlight in the yellow half, red-orange in the
    orange half. Right faces: red-orange where painted (the right side of the "!"), else a
    light (yellow) edge in the orange half where painted. Top faces in the orange half: the
    light (yellow) edge as painted, highlight only where the painting has highlight there.
    Returns hi, red and lite (cells drawn in flat yellow over the dither)."""
    e_hi, e_red, e_lite = evidence(L)
    D = ring_dirs(fill)
    lite = np.zeros_like(fill)
    side = {k: D[k] & ~D['up'] & ~D['down'] for k in ('left', 'right')}
    yz, oz = level == 0, level >= 2
    for k in ('left', 'right'):
        for zname, zone in (('y', yz), ('o', oz)):
            for m in chains(side[k] & zone):
                hi &= ~m; red &= ~m
                if m.sum() < 3:
                    continue
                h, r, l = e_hi[m].mean(), e_red[m].mean(), e_lite[m].mean()
                if k == 'left' and zname == 'y' and h >= 0.3:
                    hi |= m
                elif k == 'left' and zname == 'o' and r >= 0.35:
                    red |= m
                elif k == 'right' and r >= (0.25 if zname == 'y' else 0.35):
                    red |= m
                elif k == 'right' and zname == 'y' and h >= 0.4:
                    hi |= m
                elif k == 'right' and zname == 'o' and l >= 0.65:
                    lite |= m
    for m in chains(D['up'] & oz & ~D['down'], horizontal=True):
        if m.sum() < 2:
            continue
        hi &= ~m
        if e_hi[m].mean() >= 0.4:
            hi |= m
        elif e_lite[m].mean() >= 0.65:
            lite |= m
    return hi, red, lite


def deep_top(hi, fill, L, red):
    """The painted highlight on top faces is 9 to 12 px (1.2 to 1.6 cells): a run of the top
    stripe gets a second row below it where the painting is highlight there."""
    e_hi = cell_mean((L == IDX['hilite']).astype(np.float32))
    D = ring_dirs(fill)
    top = hi & D['up']
    cand = fill & shift(top, -1, 0) & ~top & ~red
    add = np.zeros_like(fill)
    for m in chains(cand, horizontal=True):
        if e_hi[m].mean() >= 0.35:
            add |= m
    return hi | add


def deep_bottom(red, fill, L, hi):
    """The painted red-orange under each letter is 10 to 15 px (1.5 to 2 cells): a run of
    the bottom stripe gets a second row above it where the painting is red-orange there."""
    e_red = cell_mean((L == IDX['red']).astype(np.float32))
    D = ring_dirs(fill)
    bottom = red & D['down']
    cand = fill & shift(bottom, 1, 0) & ~bottom & ~hi
    add = np.zeros_like(fill)
    for m in chains(cand, horizontal=True):
        if e_red[m].mean() >= 0.25:
            add |= m
    return red | add


def paw_colours(G, level, org, hi, red):
    """Paw pads coloured by rule, row by row, so every pad stays symmetric and no lone dither
    dots appear on the small toes: highlight top, yellow, one checker row, orange, red bottom.
    The main pad uses yellow, checker and orange bands by its rows."""
    pw = G['pawc']; fill = G['fill']
    D = ring_dirs(fill)
    yy, xx = np.indices((NY, NX))
    lab, n = ndi.label(pw)
    level = level.copy()
    for c in range(1, n + 1):
        m = lab == c
        rows = np.flatnonzero(m.any(1)); top, bot = rows[0], rows[-1]
        t = (yy - top) / max(bot - top, 1)
        if m.sum() < 60:      # toe: mostly yellow as painted, orange lower third
            lv = np.where(t < 0.55, 0, np.where(t < 0.75, 4, 8))
        else:
            lv = np.where(t < 0.3, 0, np.where(t < 0.62, 4, 8))
        level[m] = lv[m]
    org = np.where(pw, dither(level), org)
    hi = (hi & ~pw) | (pw & D['up'])
    red = (red & ~pw) | (pw & D['down'] & ~D['up'])
    return level, org, hi, red
