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


def paw_cells_axis(F, axis_shift):
    """Main pad: the painted pad mirrored about its vertical axis, smoothed, rasterized
    symmetric about a snapped axis. Toes: axis-aligned pixel ellipses, centres on a half
    cell so each toe is mirror symmetric, sizes and centres chosen for the best overlap with
    the painted toe among shapes with no one-pixel tips, kept clear of the
    pad and of each other by one navy cell, as in the painting (pads are about 1.2 cells apart; two cells would shrink the toes)."""
    toes, pad = paw_parts(F)
    out = np.zeros((NY, NX), bool)
    info = []
    I, J = cell_index(H_SRC, W_SRC)
    if pad is not None:
        ys, xs = np.nonzero(pad)
        ax = xs.mean() + 0.5                       # vertical axis in crop px
        mir = np.zeros_like(pad)
        xm = np.round(2 * ax - 1 - xs).astype(int)
        ok = (xm >= 0) & (xm < pad.shape[1])
        mir[ys[ok], xm[ok]] = True
        sym = ndi.gaussian_filter(pad.astype(np.float32) + mir.astype(np.float32), 2.0) > 1.0
        pol = smooth_polys(sym, s=6.0, straight_tol=2.0, pre=2.0, min_area=200, thr=60.0)
        P = fill_polys(pol, pad.shape)
        cov = coverage(to_full(P), I, J)
        axc = np.floor((ax + X0) / PX) + 0.5 + axis_shift   # axis on a cell centre: odd width, so the
                                                   # checker is mirror symmetric too
        k2 = int(round(2 * axc))                   # mirror: cell i <-> k2 - 1 - i
        ii = np.arange(NX); im = k2 - 1 - ii
        okm = (im >= 0) & (im < NX)
        covm = np.zeros_like(cov); covm[:, okm] = cov[:, im[okm]]
        padc = (cov + covm) / 2 >= 0.5
        padc = notch_bump_clean(padc)
        out |= padc; info.append(('pad', axc))
    order = sorted(toes, key=lambda m: -m.sum())
    for m in order:
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min() + Y0 - 30, ys.max() + Y0 + 30, xs.min() + X0 - 30, xs.max() + X0 + 30
        Jw, Iw = J[y0:y1, x0:x1], I[y0:y1, x0:x1]
        tgt = to_full(m)[y0:y1, x0:x1]
        cx = (xs.mean() + X0 + 0.5) / PX; cy = (ys.mean() + Y0 + 0.5) / PY
        a0, b0 = 2 * xs.std() / PX, 2 * ys.std() / PY
        dist = ndi.distance_transform_edt(~out)
        best = None
        for sep in (2.0, 1.5):
            for scx in np.arange(np.floor(cx) - 0.5, np.floor(cx) + 1.6, 1.0):   # cell centres only
                for scy in np.arange(np.floor(cy * 2) / 2 - 1, np.ceil(cy * 2) / 2 + 1.01, 0.5):
                    for fa in np.arange(0.85, 1.36, 0.05):
                        for fb in np.arange(0.85, 1.36, 0.05):
                            e = raster_ellipse(scx, scy, a0 * fa, b0 * fb)
                            rows = e.sum(1)[e.any(1)]; cols = e.sum(0)[e.any(0)]
                            if len(rows) < 3 or rows[0] < 2 or rows[-1] < 2 or cols[0] < 2 or cols[-1] < 2:
                                continue
                            if np.abs(np.diff(rows)).max() > 2 or np.abs(np.diff(cols)).max() > 2:
                                continue
                            if dist[e].min() < sep:
                                continue
                            ef = e[Jw, Iw]
                            iou = (ef & tgt).sum() / max((ef | tgt).sum(), 1)
                            if best is None or iou > best[0]:
                                best = (iou, e, scx, scy, a0 * fa, b0 * fb, sep)
            if best is not None:
                break
        out |= best[1]
        info.append(('toe', best[2], best[3], round(best[4], 2), round(best[5], 2), round(best[0], 3), best[6]))
    return out, info


def paw_cells(F):
    """Try the pad axis on the two nearest cell centres; keep the paw whose toes fit best."""
    best = None
    for sh in (-1.0, 0.0):
        out, info = paw_cells_axis(F, sh)
        score = sum(t[5] for t in info if t[0] == 'toe')
        if best is None or score > best[0]:
            best = (score, out, info)
    return best[1], best[2]


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
    pawc, pawinfo = paw_cells(M['F'])
    fill = (fill & ~cell_disk_dilate(pawc, 2.0)) | pawc   # the paw sits in front of the "!"
    # 2. constant outline in cell space: every cell within T_OUT cells of the fill
    base = cell_disk_dilate(fill, T_OUT)
    # 3. the painting's own silhouette: depth faces beyond the base outline
    opol = smooth_polys2(M['CL'], s=8.0, rms_tol=3.0, max_tol=8.0, pre=2.0, min_area=200)
    outP = fill_polys(opol, M['CL'].shape)
    painted = cov(outP) >= 0.5
    extra = painted & ~base
    extra = ndi.binary_opening(extra, structure=np.ones((2, 2)))   # no one-cell slivers or lumps
    outer = base | extra
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
    # 4. gaps: the painting's blue inside, never closer than T_OUT cells to the fill
    gpol = smooth_polys2(M['GAP'], s=6.0, rms_tol=3.0, max_tol=8.0, pre=2.0, min_area=150)
    gapP = fill_polys(gpol, M['GAP'].shape)
    gap = (cov(gapP) >= 0.5) & outer & ~base
    gap = clean_mask(gap, 4, 0)
    # inlets of sky reaching in from outside: keep only where at least two cells wide
    touch = ndi.binary_dilation(~outer) & gap
    lab, n = ndi.label(gap)
    inlet = np.isin(lab, np.unique(lab[touch])[1:]) if n else np.zeros_like(gap)
    wide = ndi.binary_opening(gap, structure=np.ones((2, 2)))
    gap = (gap & ~inlet) | (inlet & wide)
    gap = clean_mask(gap, 4, 0)
    lab, n = ndi.label(gap)            # small inlets read as notches in the outline: navy
    for c in range(1, n + 1):
        m = lab == c
        if (m & ndi.binary_dilation(~outer)).any() and m.sum() < 10:
            gap &= ~m
    return dict(outer=outer, fill=fill, gap=gap, base=base, painted=painted, fillP=fillP, pawc=pawc, pawinfo=pawinfo)


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
    num = ndi.gaussian_filter(Ol.astype(np.float32), sigma)
    den = ndi.gaussian_filter((Yl | Ol).astype(np.float32), sigma)
    u = num / np.maximum(den, 1e-3)
    # wider blur where the interior is far (cells along the edges), so every fill cell has
    # an estimate from the nearest interior paint
    num2 = ndi.gaussian_filter(Ol.astype(np.float32), 2 * sigma)
    den2 = ndi.gaussian_filter((Yl | Ol).astype(np.float32), 2 * sigma)
    u = np.where(den > 0.05, u, num2 / np.maximum(den2, 1e-4))
    uc = cell_mean(u)
    lab, n = ndi.label(fill)
    # 2-D field: the painting's gradient follows each stroke, so no per-row model
    a = ndi.gaussian_filter(np.where(fill, uc, 0.0), smooth); b = ndi.gaussian_filter(fill.astype(float), smooth)
    ufit = np.where(fill, a / np.maximum(b, 1e-6), 0.0)
    level = np.clip(np.floor(ufit * 4 + 0.5), 0, 4).astype(np.int8)
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


def dither(level):
    yy, xx = np.indices((NY, NX))
    return BAYER[yy % 2, xx % 2] < level      # True = orange


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
    level, ufit, uc, lab = gradient_levels(L, fill)
    org = dither(level)
    hi, red, e_hi, e_red = stripes(L, fill, ufit)
    # the paw: pure rule (light top, red bottom) so every pad stays symmetric
    pw = G['pawc']; D = ring_dirs(fill)
    hi = (hi & ~pw) | (pw & D['up'])
    red = (red & ~pw) | (pw & D['down'] & ~D['up'])
    hi, red = clean_stripes(hi, red, fill)
    hi, red = complete_runs(hi, red, fill)
    hi, red = complete_sides(hi, red, fill, level)
    level, org, hi, red = paw_colours(G, level, org, hi, red)
    hi, red = clean_stripes(hi, red, fill)
    gk, gnames = gap_colours(L, gap)
    P = lambda n: pal[IDX[n]]
    idx = np.full((NY, NX), -1, np.int16)     # palette index map (into PROTO), -1 transparent
    idx[outer] = IDX['navy']
    for i, g in enumerate(gnames):
        idx[gap & (gk == i)] = IDX[g]
    idx[fill] = IDX['yellow']
    idx[fill & org] = IDX['orange']
    idx[hi] = IDX['hilite']; idx[red] = IDX['red']
    return dict(L=L, pal=pal, M=M, G=G, level=level, ufit=ufit, uc=uc, hi=hi, red=red, idx=idx, gk=gk)


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


def complete_sides(hi, red, fill, level):
    """Side faces: each 8-connected chain of left- or right-facing edge cells, split where the
    gradient turns from the yellow half to the orange half, becomes one stripe end to end
    when the painting marks at least 30 % (highlight) or 40 % (red) of it, and none otherwise (no dashed lines)."""
    D = ring_dirs(fill)
    side = {k: D[k] & ~D['up'] & ~D['down'] for k in ('left', 'right')}
    for k in ('left', 'right'):
        for zone in (level <= 1, level >= 2):
            f = side[k] & zone
            lab, n = ndi.label(f, structure=np.ones((3, 3)))
            for c in range(1, n + 1):
                m = lab == c
                if m.sum() < 3:
                    hi &= ~m; red &= ~m
                    continue
                fh, fr = (hi & m).sum() / m.sum(), (red & m).sum() / m.sum()
                hi &= ~m; red &= ~m
                if fh >= 0.3 and fh >= fr:
                    hi |= m
                elif fr >= 0.4:
                    red |= m
    return hi, red


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
        if m.sum() < 60:      # toe
            lv = np.where(t < 0.45, 0, np.where(t < 0.62, 2, 4))
        else:
            lv = np.where(t < 0.3, 0, np.where(t < 0.62, 2, 4))
        level[m] = lv[m]
    org = np.where(pw, dither(level), org)
    hi = (hi & ~pw) | (pw & D['up'])
    red = (red & ~pw) | (pw & D['down'] & ~D['up'])
    return level, org, hi, red
