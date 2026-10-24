"""PEPPER track, step 2: re-render Pepper's head and bandana on the 320 x 240 grid.

Pepper is painted on a coarser lattice than the rest of the title (about 10 px
pseudo-pixels in x and 9.5 to 10 px in y, against 7.5 px output cells), so no
320-grid can sit on her painted block edges. Her shapes are therefore re-drawn
at the output resolution from the painting's full-resolution label map:

1. thin dark lines (the painting's pure black line colour, at most THIN_W px
   wide) are traced as skeleton polylines, smoothed along the arc and rasterized
   as 1 px pixel-perfect lines;
2. everything else is a fill class (one palette colour, or a checker of two
   palette colours where the painting dithers two tones); every class indicator
   is Gaussian smoothed (a multi-label curvature flow that turns the painting's
   10 px staircases into the curves they stand for) and each output cell takes
   the class with the largest mean inside the cell;
3. checker classes are rebuilt by rule in global phase ((i + j) % 2);
4. coat cells left outside the outline are removed, isolated specks are merged.
"""
import numpy as np, os, json
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
import pepper_seg as S
import lines as LN
import shapes as SH
import pepper_detail as DT

NX, NY = 320, 240
CW, CH = S.CW, S.CH
P = dict(BLACK_W=24.0, THICK_AT=14.5, MIN_LINE=20, INSET=2.5, DARK_FRAC=0.0, SIGMA=3.0, SIGMA_PART=3.0,
         SHAPE_SIGMA=3.0, LINE_S=6.0, LIT_L=28.0, LIT_W=13.0, LIT_MIN=50, FOLD_W=13.0, FOLD_MIN=25, RIDGE_SIZE=17, RIDGE_D=18.0, RIDGE_D_T=10.0, CREASE_W=18.0, FOLD_MIN_B=60,
         DITH_W=23, DITH_OP=5, DITH_T=0.7, DITH_R=0.15, DITH_SC=0.025, MASK_SIGMA=4.0, UNDER_OUTLINE=4.0, OUT_S=12.0, REFINE=True, DETAILS=True, JAW_TONE=1, TONGUE_S=8.0, EAR_BANDS=True, EAR_SIGMA=0.7, EAR_ISLAND=6, EAR_NO_CHECK=[], EAR_QUARTERS=(1, 2, 3), EAR_MODE=2, CLEAR_TONE=1, DITH_REG=True, DITH_MIN=6, PINK_RAMP=[8, 9, 44, 23], RARE_MAX=3, JAW_RUN=5, JAW_BOX=(118, 124, 150, 166), HL_ID=5, HL_COVER=0.3, HL_STRAY=[60, 27, 53, 10, 52, 48, 12, 7], NOSE_MAP=(([10, 53, 27, 60], 22), ([7, 12, 48, 52], 35)), DUP_FRAC=0.5, SIL_NEAR=2.0, SIL_CLOSE=0, OUT_K=26, REFINE_PASSES=8, MIX_W=40.0, OUT_CORNER=75.0, OUT_STRAIGHT=2.5, SPUR=12, BLACK_SPUR=18, BLACK_EXTRA=[2], PURE_FRAC=0.4, NEARBLACK_W=0.0, DARK_SIDES=0.4,
         PAIRS=[(0, 1), (0, 7), (7, 11), (0, 11), (7, 10), (1, 2), (10, 12), (8, 9), (9, 44)],
         MERGE={3: 2, 13: 2})


def cell_maps(shape):
    x0, y0 = S.BOX[:2]
    H, W = shape
    I = np.floor((np.arange(W) + x0 + 0.5) / CW).astype(int)
    J = np.floor((np.arange(H) + y0 + 0.5) / CH).astype(int)
    return I, J


def cell_mean(img, I, J):
    """mean of a full-res float map per output cell -> (NY, NX) with NaN where empty."""
    H, W = img.shape
    idx = (J[:, None] * NX + I[None, :]).ravel()
    s = np.bincount(idx, weights=img.ravel().astype(np.float64), minlength=NX * NY)
    n = np.bincount(idx, minlength=NX * NY)
    with np.errstate(invalid='ignore'):
        return (s / n).reshape(NY, NX), n.reshape(NY, NX)


def dither_pairs(L, O, pairs, W, rmin, scmin, op=9, tmin=0.7):
    """Virtual labels where two tones are mixed at block scale in both directions (a
    dither). The class records the pair and the mix level (1, 2 or 3 quarters of the
    second tone); it is rebuilt on the output grid by an ordered 2 x 2 (Bayer) rule,
    so a half mix is a checker in global phase."""
    out = np.full(L.shape, -1, np.int16); best = np.zeros(L.shape, np.float32)
    lvl_map = np.zeros(L.shape, np.int8)
    for k, (a, b) in enumerate(pairs):
        A = (L == a) | (L == b)
        th = np.zeros(L.shape, np.float32); tv = np.zeros(L.shape, np.float32)
        th[:, :-1] = ((L[:, :-1] == a) & (L[:, 1:] == b)) | ((L[:, :-1] == b) & (L[:, 1:] == a))
        tv[:-1] = ((L[:-1] == a) & (L[1:] == b)) | ((L[:-1] == b) & (L[1:] == a))
        na = ndi.uniform_filter((L == a).astype(np.float32), W)
        nb_ = ndi.uniform_filter((L == b).astype(np.float32), W)
        dh = ndi.uniform_filter(th, W); dv = ndi.uniform_filter(tv, W)
        tot = na + nb_
        rb = nb_ / np.maximum(tot, 1e-6)
        r = np.minimum(rb, 1 - rb)
        sc = np.minimum(dh, dv) / np.maximum(tot, 1e-6)
        m = (tot > tmin) & (r > rmin) & (sc > scmin) & A & O
        v = sc * (0.25 + r)
        upd = m & (v > best)
        out[upd] = k; best[upd] = v[upd]
        lvl_map[upd] = np.clip(np.round(rb[upd] * 4), 1, 3)
    # a dither region is a shape: drop crumbs, close gaps
    res = np.full(L.shape, -1, np.int16)
    for k in range(len(pairs)):
        for lv in (1, 2, 3):
            m = ndi.binary_closing((out == k) & (lvl_map == lv), np.ones((7, 7)))
            m = ndi.binary_opening(m, np.ones((op, op)))
            res[m & (res < 0)] = k * 4 + lv
    return res


BAYER = np.array([[0, 2], [3, 1]])


def fill_small_holes(m, maxa):
    lab, n = ndi.label(~m)
    if n == 0:
        return m
    sz = ndi.sum(~m, lab, range(1, n + 1))
    return m | np.isin(lab, np.flatnonzero(sz <= maxa) + 1)


def split_thin(q, dt, thin_w, win=15):
    """split a skeleton path into stretches whose (median-filtered) width is thin."""
    q = np.asarray(q)
    w = 2 * dt[q[:, 1].astype(int), q[:, 0].astype(int)]
    if len(w) >= 3:
        k = min(win, len(w) // 2 * 2 - 1) if len(w) > 2 else 1
        w = ndi.median_filter(w, size=max(1, k), mode='nearest')
    t = w <= thin_w
    out = []; start = None
    for k_, v in enumerate(t):
        if v and start is None:
            start = k_
        if not v and start is not None:
            out.append(q[start:k_]); start = None
    if start is not None:
        out.append(q[start:])
    return out


def _normals(q, closed):
    d = np.gradient(q, axis=0) if not closed else (np.roll(q, -1, 0) - np.roll(q, 1, 0)) / 2
    n = np.c_[-d[:, 1], d[:, 0]]
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    return n


def _sample(m, pts):
    H, W = m.shape
    x = np.clip(np.round(pts[:, 0]).astype(int), 0, W - 1)
    y = np.clip(np.round(pts[:, 1]).astype(int), 0, H - 1)
    return m[y, x]


def dark_both_sides(seg, dark, p, off=(3, 6, 9), width=None):
    """True when the line runs inside a dark area (both sides dark): it is not a line
    on the coat but a darker blob in a shadow, so the fill handles it."""
    sm = LN.smooth_polyline(seg, 3.0)
    n = _normals(sm, False)
    if width is None:
        width = 2 * np.median(_DT[seg[:, 1].astype(int), seg[:, 0].astype(int)]) if _DT is not None else 10
    off = [o + width / 2 for o in off]
    a = np.mean([_sample(dark, sm + o * n).mean() for o in off])
    b = np.mean([_sample(dark, sm - o * n).mean() for o in off])
    return min(a, b) > p.get('DARK_SIDES', 0.4)


def outer_outline(D, darkm, p):
    """Closed silhouette contours of the dog: smoothed, inset by INSET px, rasterized
    as pixel-perfect 1 px lines on the stretches where the painted edge is dark."""
    import cv2
    x0, y0 = S.BOX[:2]
    # notches narrower than about two cells (a background object's cap cutting into
    # the outline) are closed before the contour is traced
    r = int(p['SIL_CLOSE'])
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx * xx + yy * yy) <= r * r
    Dc = ndi.binary_closing(np.pad(D, r + 2), disk)[r + 2:-r - 2, r + 2:-r - 2] if r > 0 else D
    Dsm = ndi.gaussian_filter(Dc.astype(np.float32), 3.0) > 0.5
    cnts, _ = cv2.findContours(Dsm.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    cells = np.zeros((NY, NX), bool)
    polys, polys_in = [], []
    band = np.zeros(D.shape, bool)
    global _OUTLINE_DRAWN
    _OUTLINE_DRAWN = []
    for c in cnts:
        c = c[:, 0, :].astype(float)
        if len(c) < 40:
            continue
        # corner-aware smoothing (shapes.py): real corners kept, nearly straight
        # stretches made exactly straight, curves smoothed along the arc
        q = SH.smooth_contour(c, s=p['OUT_S'], k=p['OUT_K'], thr=p['OUT_CORNER'], straight_tol=p['OUT_STRAIGHT'])
        q = resample_closed(q)
        n = _normals(q, True)
        # orient normals inward
        if _sample(Dsm, q + 3 * n).mean() < _sample(Dsm, q - 3 * n).mean():
            n = -n
        qi = q + p['INSET'] * n
        # the painted edge is dark: inward samples 1..9 px
        dk = np.mean([_sample(darkm, q + d * n) for d in (2, 4, 6, 8)], axis=0) >= p['DARK_FRAC']
        dk = ndi.median_filter(dk.astype(np.uint8), size=15, mode='wrap').astype(bool)
        polys.append(q); polys_in.append(qi)
        _OUTLINE_DRAWN.append((q, dk))
        # rasterize the drawn stretches
        if dk.all():
            runs = [np.arange(len(qi))]
        else:
            idx = np.arange(len(qi))
            # rotate so the sequence starts at an undrawn point
            st = int(np.flatnonzero(~dk)[0])
            idx = np.roll(idx, -st); d2 = dk[idx]
            runs = []; cur = []
            for k, v in zip(idx, d2):
                if v:
                    cur.append(k)
                elif cur:
                    runs.append(np.array(cur)); cur = []
            if cur:
                runs.append(np.array(cur))
        for r in runs:
            if len(r) < 8:
                continue
            closed = len(r) == len(qi)
            cl = LN.raster_polyline(qi[r] + [x0, y0], CW, CH, closed=closed)
            for i, j in cl:
                if 0 <= i < NX and 0 <= j < NY:
                    cells[j, i] = True
        # band of painted outline pixels next to the edge (excluded from interior lines)
    dist_out = ndi.distance_transform_edt(D)
    band = D & (dist_out <= 14)
    return cells, polys_in, polys, band


def resample_closed(q, step=1.0):
    q = np.vstack([q, q[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
    t = np.arange(0, d[-1], step)
    return np.c_[np.interp(t, d, q[:, 0]), np.interp(t, d, q[:, 1])]


def points_in_polys(polys, cx, cy):
    """even-odd fill of the closed polylines evaluated at points (cx, cy)."""
    import matplotlib.path as mp
    res = np.zeros(cx.shape, bool)
    pts = np.c_[cx.ravel(), cy.ravel()]
    for q in polys:
        res ^= mp.Path(q).contains_points(pts).reshape(cx.shape)
    return res


def near_outline(polys, cx, cy, r):
    from scipy.spatial import cKDTree
    t = cKDTree(np.vstack(polys))
    dist, _ = t.query(np.c_[cx.ravel(), cy.ravel()])
    return (dist < r).reshape(cx.shape)


def near_outline_drawn(polys, cx, cy, r=None):
    """True where the nearest contour point (within 2 cells) is on a drawn stretch."""
    from scipy.spatial import cKDTree
    allq = np.vstack([q for q, _ in _OUTLINE_DRAWN]); alld = np.concatenate([d for _, d in _OUTLINE_DRAWN])
    t = cKDTree(allq)
    dist, k = t.query(np.c_[cx.ravel(), cy.ravel()])
    return (alld[k] & (dist < 2 * CW)).reshape(cx.shape)


_DT = None


def split_turns(seg, k=10, thr=35.0):
    """split a path where it turns sharply (a stroke does not hook)."""
    if len(seg) < 2 * k + 3:
        return [seg]
    sm = LN.smooth_polyline(seg, 2.0)
    cut = []
    for i in range(k, len(sm) - k):
        a = sm[i] - sm[i - k]; b = sm[i + k] - sm[i]
        c = (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
        if np.degrees(np.arccos(np.clip(c, -1, 1))) > thr:
            cut.append(i)
    if not cut:
        return [seg]
    # one cut per run of sharp points, at its middle
    runs, cur = [], [cut[0]]
    for c in cut[1:]:
        if c - cur[-1] <= 2:
            cur.append(c)
        else:
            runs.append(cur); cur = [c]
    runs.append(cur)
    # sm is resampled at unit arc length: map its indices back onto seg
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(seg, axis=0).T))]
    mids = [int(np.searchsorted(d, r[len(r) // 2])) for r in runs]
    idx = [0] + mids + [len(seg)]
    return [seg[a:b + 1] for a, b in zip(idx[:-1], idx[1:]) if b > a]


def extract_lines(M, dt_src, maxw, minlen, spur, smooth, x0, y0, reject=None, thick_at=None, turns=False):
    """Thin stretches of mask M as smoothed polylines rasterized on the output grid.
    Returns a list of dicts (cells, poly, width, path) and the full-res pixels they replace."""
    M = fill_small_holes(M, 40)
    lab, n = ndi.label(M); sz = ndi.sum(M, lab, range(1, n + 1))
    M = np.isin(lab, np.flatnonzero(sz >= 30) + 1)
    # a lightly smoothed mask gives a skeleton without the staircase's side branches
    Ms = (ndi.gaussian_filter(M.astype(np.float32), 2.0) > 0.5) & ndi.binary_dilation(M, iterations=2)
    sk = skeletonize(Ms)
    dt = ndi.distance_transform_edt(Ms)
    paths, _ = LN.trace_skeleton(sk, spur)
    global _DT
    _DT = dt
    out = []; used = np.zeros_like(sk)
    for q in paths:
        segs = split_thin(q, dt, maxw)
        if turns:   # a stroke: the longest piece between sharp turns
            segs = [max(split_turns(s_), key=len) for s_ in segs]
        for seg in segs:
            if len(seg) < minlen:
                continue
            if reject is not None and reject(seg):
                continue
            w = float(np.median(2 * dt[seg[:, 1].astype(int), seg[:, 0].astype(int)]))
            sm = LN.smooth_polyline(seg, smooth)
            closed = np.hypot(*(seg[0] - seg[-1])) < 1.5 and len(seg) > 10
            thick = 1 if thick_at is None else int(np.clip(np.round(w / CW), 1, 3))
            cells = raster_line(sm + [x0, y0], closed, thick)
            out.append(dict(cells=cells, poly=sm, width=w, path=seg, thick=thick))
            for xq, yq in seg.astype(int):
                used[yq, xq] = True
    if used.any():
        _, (iy, ix) = ndi.distance_transform_edt(~sk, return_indices=True)
        rep = (M | Ms) & used[iy, ix]
    else:
        rep = np.zeros_like(M)
    return out, rep


def raster_line(q, closed, thick):
    """1 px pixel-perfect raster of a curve; thick=2 adds the next row (shallow parts)
    or column (steep parts) after shifting the curve back by half a cell, so the
    2 px line stays centred on the painted stroke."""
    if thick == 1:
        cl = LN.raster_polyline(q, CW, CH, closed=closed)
        return set((i, j) for i, j in cl)
    t = np.gradient(q, axis=0)
    shallow = np.abs(t[:, 0]) >= np.abs(t[:, 1])
    qs = q.copy()
    if thick == 2:
        qs[shallow, 1] -= CH / 2; qs[~shallow, 0] -= CW / 2
    cl = LN.raster_polyline(qs, CW, CH, closed=closed)
    # direction per cell from the nearest curve point
    I = np.floor(qs[:, 0] / CW).astype(int); J = np.floor(qs[:, 1] / CH).astype(int)
    sh = {}
    for i, j, s_ in zip(I, J, shallow):
        sh.setdefault((i, j), []).append(s_)
    cells = set()
    for i, j in cl:
        cells.add((i, j))
        v = sh.get((i, j))
        s_ = (np.mean(v) >= 0.5) if v else True
        cells.add((i, j + 1) if s_ else (i + 1, j))
        if thick == 3:
            cells.add((i, j - 1) if s_ else (i - 1, j))
    return cells


def cells_to_mask(cells):
    m = np.zeros((NY, NX), bool)
    for i, j in cells:
        if 0 <= i < NX and 0 <= j < NY:
            m[j, i] = True
    return m


def shape_cells(mask, I, J, sigma):
    m, _ = cell_mean(ndi.gaussian_filter(mask.astype(np.float32), sigma), I, J)
    return np.nan_to_num(m) >= 0.5


def ring_of(shape):
    """inner 4-boundary of a cell shape, with the joints of L-steps given back to the
    interior so the ring is an 8-connected 1 px line."""
    ring = shape & ~ndi.binary_erosion(shape, ndi.generate_binary_structure(2, 1), border_value=0)
    for _ in range(2):
        c = LN.lcorners(ring, keep_corners=False)
        # only the corner cells whose removal keeps the shape closed (diagonal step)
        ring &= ~c
    return ring


def argmax_classes(Lv, region_mask, cell_sel, I, J, sigma, cls, best):
    """per cell argmax of the smoothed class indicators restricted to region_mask."""
    for c in np.unique(Lv[region_mask]):
        ind = ((Lv == c) & region_mask).astype(np.float32)
        if ind.sum() < 12:
            continue
        sm = ndi.gaussian_filter(ind, sigma)
        m, _ = cell_mean(sm, I, J)
        m = np.nan_to_num(m, nan=-1)
        upd = cell_sel & (m > best)
        best[upd] = m[upd]; cls[upd] = c
    return cls, best


def _lum(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114], np.float32)


def render(params=None, verbose=True):
    p = dict(P); p.update(params or {})
    pal, L = S.label_region()
    D, B, O = S.owned_mask(pal, L)
    parts = S.part_masks_from_labels(pal, L, D, B)
    if p['DETAILS']:
        Dt = DT.trim_knot(D, B, S.BOX)
        O = O & Dt
        D = Dt
    # near-identical navy-blacks (dE < 6 from each other) are one colour in the output
    for a_, b_ in p['MERGE'].items():
        L = np.where(L == a_, b_, L)
    g, hexes = S.groups(pal)
    labL = S.srgb_to_lab(pal)[:, 0]
    H, W = L.shape
    I, J = cell_maps(L.shape)
    line_id = g['line'][0]
    x0, y0 = S.BOX[:2]
    dark_ids = g['line'] + g['black']
    darkm = np.isin(L, dark_ids) & D

    # ---- 1. outer outline ------------------------------------------------------
    outer_cells, outer_poly_in, outer_poly, outer_band = outer_outline(D, darkm, p)
    shapes_px = ndi.binary_dilation(parts['eye'] | parts['nose'], np.ones((7, 7)))

    # ---- 2. lines --------------------------------------------------------------
    lines = []      # (cells, colour id, layer)
    replaced = np.zeros(L.shape, bool)
    # black lines
    M = np.isin(L, [line_id] + p['BLACK_EXTRA']) & D & ~outer_band & ~shapes_px
    M = ndi.binary_closing(M, np.ones((3, 3))) & D & ~outer_band & ~shapes_px
    pure = ndi.binary_dilation(L == line_id, np.ones((5, 5)))
    def rej(seg):
        on_pure = _sample(pure, seg).mean()
        w = 2 * np.median(_DT[seg[:, 1].astype(int), seg[:, 0].astype(int)])
        # a near-black stroke counts as a line only when it is thin (lashes, creases)
        return (on_pure < p['PURE_FRAC'] and w > p['NEARBLACK_W']) or dark_both_sides(seg, darkm | ~D, p)
    bl, rep = extract_lines(M, None, p['BLACK_W'], p['MIN_LINE'], p['BLACK_SPUR'], p['LINE_S'], x0, y0, rej, thick_at=p['THICK_AT'])
    for d in bl:
        lines.append((d['cells'], line_id, 3, d))
    replaced |= rep
    black_rep = rep.copy()
    # lit rim lines on the coat (brows, ear edges, lip, cheek)
    lit_ids = [i for i in g['coat'] if labL[i] >= p['LIT_L']]
    M = np.isin(L, lit_ids) & D & ~shapes_px & ~B & ~parts['tongue']
    M = ndi.binary_closing(M, np.ones((3, 3))) & D & ~shapes_px
    ll, rep = extract_lines(M, None, p['LIT_W'], p['LIT_MIN'], p['SPUR'], p['LINE_S'], x0, y0)
    for d in ll:
        lines.append((d['cells'], mode_label(L, d['path'], lit_ids), 1, d))
    replaced |= rep
    # tongue crease and bandana folds (darker lines of their own material)
    for name, part, ids_fn in (('crease', 'tongue', lambda: [i for i in g['pink'] + g['tongue'] if labL[i] < 42]),
                               ('fold', 'bandana', lambda: [i for i in g['pink'] if labL[i] < 45])):
        rd, fmin = (p['RIDGE_D_T'], p['FOLD_MIN']) if name == 'crease' else (p['RIDGE_D'], p['FOLD_MIN_B'])
        ids = ids_fn()
        # dark ridges: pixels darker than the closing of the label luma (a black
        # top-hat), i.e. thin dark strokes on the material, whatever their exact colour
        Y = _lum(pal.astype(np.float32))[L]
        bth = ndi.grey_closing(Y, size=(p['RIDGE_SIZE'], p['RIDGE_SIZE'])) - Y
        inner = ndi.binary_erosion(parts[part], np.ones((7, 7)))
        M = (bth > rd) & inner
        M = ndi.binary_closing(M, np.ones((5, 5))) & inner
        ids = list(np.unique(L[M]))
        cl_, rep = extract_lines(M, None, p['FOLD_W'] if name == 'fold' else p['CREASE_W'], fmin, p['SPUR'], p['LINE_S'], x0, y0, turns=True)
        for d in cl_:
            # the stroke colour: the darkest material colour that covers at least 10 % of
            # the path's neighbourhood (a crease is darker than both of its sides)
            mat = g['pink'] + g['tongue']
            q_ = d['path'].astype(int)
            nbh = np.zeros(L.shape, bool); nbh[q_[:, 1], q_[:, 0]] = True
            nbh = ndi.binary_dilation(nbh, np.ones((5, 5)))
            v, n = np.unique(L[nbh], return_counts=True)
            cand = [(labL[c], c) for c, k in zip(v, n) if c in mat and k >= 0.1 * n.sum()]
            col = min(cand)[1] if cand else min((labL[c], c) for c in mat)[1]
            lines.append((d['cells'], int(col), 2, d))
        replaced |= rep

    # ---- 2b. hand-traced details (lashes, brow) ---------------------------------
    if p['DETAILS']:
        clr = DT.clear_mask(L.shape, S.BOX, LN)
        # automatic black lines that run mostly inside a clear box are replaced
        keep_lines = []
        for item in lines:
            cells_, col_, lay_, d_ = item
            if lay_ == 3 and _sample(clr, d_['path']).mean() > 0.5:
                continue
            keep_lines.append(item)
        lines = keep_lines
        for st in DT.STROKES:
            q = np.array(st['pts'], float)
            q = LN.smooth_polyline(q, 2.0) if len(q) > 3 else q
            th = st.get('thick', 1)
            cl = raster_line(q, False, th)
            d_ = dict(cells=set(cl), poly=q - [x0, y0], width=8.0 * th, path=(q - [x0, y0]), thick=th, name=st['name'])
            lines.append((set(cl), st.get('colour', line_id), st.get('layer', 3), d_))
        nearblack = np.isin(L, [line_id] + p['BLACK_EXTRA'])
        # the wink's thick arc stays (it is below the lash box); the blob around the lashes goes
        replaced |= clr & nearblack

    # ---- 3. fill classes -------------------------------------------------------
    # the 1 px outline covers the painted outline's outer ~1 cell; darker coat further in
    # stays in the fill
    edge_dist = ndi.distance_transform_edt(D)
    under = replaced | (darkm & (edge_dist <= p['INSET'] + p['UNDER_OUTLINE']))
    # iris/catchlight colours belong to the eye and nose; reds to the mouth: elsewhere they
    # are background specks that leaked into the dog mask
    stray = np.isin(L, g['eye'] + g['light'] + g['other']) & ~ndi.binary_dilation(parts['eye'] | parts['nose'], np.ones((9, 9)))
    labp = S.srgb_to_lab(pal)
    bluish = [i for i in range(len(pal)) if labp[i, 2] < -12 and labp[i, 0] > 12]
    # pale greys and lavenders: the nose gloss and the eye's reflections only
    bluish += [i for i in g['coat'] if labp[i, 0] > 44]
    stray |= np.isin(L, bluish) & ~ndi.binary_dilation(parts['eye'] | parts['nose'], np.ones((9, 9)))
    stray |= np.isin(L, g['tongue']) & ~ndi.binary_dilation(parts['tongue'], np.ones((41, 61))) \
        & ~ndi.binary_dilation(parts['eye'], np.ones((9, 9)))
    valid = D & ~under & ~stray
    _, (vy, vx) = ndi.distance_transform_edt(~valid, return_indices=True)
    Lf = L[vy, vx].astype(np.int32)
    if p['DETAILS']:
        # near-black cleared around the traced strokes becomes the coat's darkest tone,
        # so the strokes keep the painting's dark surround without merging into a blob
        Lf[clr & nearblack & D] = p['CLEAR_TONE']
    p['_Lf'] = Lf; p['_valid'] = D & ~black_rep & ~(darkm & (edge_dist <= p['INSET'] + p['UNDER_OUTLINE']))
    p['_Lfull'] = np.where(np.isin(L, g['line']), Lf, L)
    pairs = [pr for pr in p['PAIRS'] if max(pr) < len(pal)]
    dv = dither_pairs(Lf, O & ~shapes_px, pairs, p['DITH_W'], p['DITH_R'], p['DITH_SC'], p['DITH_OP'], p['DITH_T'])
    Lv = np.where(dv >= 0, 1000 + dv, Lf)
    # owned cells: along the dog's silhouette, the cells whose centre lies inside the
    # smoothed (corner-aware) silhouette polygon, so the edge is the digital form of a
    # smooth curve; along the cut to the grid track's body, the cell coverage of O
    jj0, ii0 = np.indices((NY, NX))
    ccx = (ii0 + 0.5) * CW - x0; ccy = (jj0 + 0.5) * CH - y0
    in_sil = points_in_polys(outer_poly, ccx, ccy)
    own_cut = shape_cells(O, I, J, p['MASK_SIGMA'])
    own_any = shape_cells(ndi.binary_dilation(O, np.ones((25, 25))), I, J, 1.0)
    near_sil = near_outline(outer_poly, ccx, ccy, p['SIL_NEAR'] * CW)
    own = np.where(near_sil, in_sil & own_any, own_cut)
    own = fill_small_holes(own, 2)
    best = np.full((NY, NX), -1.0); cls = np.full((NY, NX), -1, np.int32)
    shp = {}
    SHAPES = ('eye', 'nose', 'tongue', 'bandana')
    taken = np.zeros((NY, NX), bool); taken_px = np.zeros(L.shape, bool)
    for k in SHAPES:
        if k == 'tongue' and p['DETAILS']:
            shp[k] = poly_cells(parts[k], p['TONGUE_S'], x0, y0) & own & ~taken
        else:
            shp[k] = shape_cells(parts[k], I, J, p['SHAPE_SIGMA'] if k != 'bandana' else p['MASK_SIGMA']) & own & ~taken
        taken |= shp[k]
    rest = own & ~taken
    for k in SHAPES:
        taken_px |= parts[k]
    cls, best = argmax_classes(Lv, O & ~taken_px, rest, I, J, p['SIGMA'], cls, best)
    for k in SHAPES:
        cls, best = argmax_classes(Lv, parts[k] & ~(taken_px & ~parts[k]), shp[k], I, J,
                                   p['SIGMA_PART'] if k != 'bandana' else p['SIGMA'], cls, best)
    # cells of a shape that got no class (no indicator reached them) take the nearest class
    miss = own & (cls < 0)
    if miss.any():
        _, (my, mx) = ndi.distance_transform_edt(miss | ~own, return_indices=True)
        cls[miss] = cls[my[miss], mx[miss]]

    if p['DETAILS'] and p['DITH_REG']:
        coat_d = [1000 + 4 * k + lv for k, pr in enumerate(pairs) if not set(pr) & ({2, 4} | set(g['pink'])) for lv in (1, 2, 3)]
        sel_ = own & ~(shp['eye'] | shp['nose'] | shp['tongue'])
        cls = regularize_dither(cls, sel_, p['DITH_MIN'], set(coat_d), pairs)
        dark_d = [1000 + 4 * k + lv for k, pr in enumerate(pairs) if set(pr) == {1, 2} for lv in (1, 2, 3)]
        cls = regularize_dither(cls, sel_, p['DITH_MIN'], set(dark_d), pairs, iters=1, join=False)

    # ---- 4. compose ------------------------------------------------------------
    jj, ii = np.indices((NY, NX))
    rgb = np.zeros((NY, NX, 3), np.uint8)
    idx = np.full((NY, NX), -1, np.int32)      # palette index per cell (for QA)
    checker = (ii + jj) % 2 == 0
    for c in np.unique(cls[own]):
        m = own & (cls == c)
        if c >= 1000:
            k_, lv = divmod(c - 1000, 4)
            a_, b_ = pairs[k_]
            useb = BAYER[jj % 2, ii % 2] < lv
            idx[m & ~useb] = a_; idx[m & useb] = b_
        else:
            idx[m] = c
    # outlined shapes: their boundary ring in the line colour
    fixed_idx = np.full((NY, NX), -1, np.int32)
    for k in ('eye', 'nose'):
        r = ring_of(shp[k])
        idx[r] = line_id; fixed_idx[r] = line_id
    # lines in layer order; a black line that runs alongside the silhouette outline
    # (most of its cells touch an outline cell) would double it: dropped
    near_out = ndi.binary_dilation(ring_of(own) & near_sil, np.ones((3, 3)))
    for layer in (1, 2, 3):
        for cells, col, lay, d in lines:
            if lay != layer:
                continue
            m = cells_to_mask(cells) & own
            if layer == 3 and m.sum() and (m & near_out).sum() > p['DUP_FRAC'] * m.sum():
                d['dropped'] = True
                continue
            if layer != 2:      # lines of other materials stop at the tongue and bandana
                inside = m & (shp['tongue'] | shp['bandana'])
                m &= ~inside
                # ...except single cells that would otherwise break the line in two
                st8 = np.ones((3, 3))
                for j_, i_ in zip(*np.nonzero(inside)):
                    n_before = ndi.label(m, st8)[1]
                    m2 = m.copy(); m2[j_, i_] = True
                    if ndi.label(m2, st8)[1] < n_before:
                        m = m2
            idx[m] = col; fixed_idx[m] = col
    # silhouette outline: the owned shape's own boundary ring (8-connected, no L
    # corners), in the line colour wherever the painted edge is dark
    cx = (ii + 0.5) * CW - x0; cy = (jj + 0.5) * CH - y0
    near_drawn = near_outline_drawn(outer_poly, cx, cy)
    # joints of L-steps on the silhouette's drawn stretches leave the shape (else the
    # fill would show outside the 1 px outline there)
    for _ in range(2):
        ring4 = own & ~ndi.binary_erosion(own, ndi.generate_binary_structure(2, 1), border_value=0)
        joints = ring4 & ~ring_of(own) & near_drawn & near_sil
        if not joints.any():
            break
        own &= ~joints
    # one-cell spurs (a cell with at most one owned 4-neighbour) leave the shape
    st4 = ndi.generate_binary_structure(2, 1)
    for _ in range(3):
        n4 = ndi.convolve(own.astype(int), st4.astype(int), mode='constant') - own
        spur = own & (n4 <= 1)
        if not spur.any():
            break
        own &= ~spur
    ring = ring_of(own)
    oc = ring & near_drawn & near_sil
    idx[~own] = -1; fixed_idx[~own] = -1
    idx[oc] = line_id; fixed_idx[oc] = line_id
    # ---- 4b. tone-preserving boundary refinement -------------------------------
    if p['REFINE']:
        import pepper_qa as Q, pepper_refine as RF
        from common import luma as _luma
        Ofull = np.zeros((1792, 2400), bool)
        Ofull[S.BOX[1]:S.BOX[3], S.BOX[0]:S.BOX[2]] = O
        o = _luma(Q.orig_cells()); ox = Q.orig_cells_excluding(Ofull)
        outside = np.where(np.isnan(ox), o, ox)
        target = ndi.uniform_filter(o, 5, mode='nearest')
        alive = idx >= 0
        cmap = np.where(alive & (fixed_idx < 0), cls, -1)
        protect = set(g['light'])
        protect |= set(int(c) for c in np.unique(cmap[shp['eye']]) if c >= 0)
        cmap, idx2, nchg = RF.refine(cmap, fixed_idx, alive, pal, pairs, BAYER, target, outside,
                                     protect=protect, passes=p['REFINE_PASSES'], mix_w=p['MIX_W'])
        if p['DETAILS']:
            before = idx2.copy()
            p['_pal'] = pal
            idx2, cmap = detail_cells(idx2, cmap, fixed_idx, oc, shp, parts, L, I, J, line_id, p)
            # the detail cells stay; a second refinement adapts the fill around them
            chg = (idx2 != before) & alive
            fixed2 = fixed_idx.copy(); fixed2[chg] = idx2[chg]
            cmap[chg] = -1
            cmap, idx2, n2 = RF.refine(cmap, fixed2, alive, pal, pairs, BAYER, target, outside,
                                       protect=protect, passes=p['REFINE_PASSES'], mix_w=p['MIX_W'])
            nchg += n2
        cmap, idx2, ndot = RF.clean_dots(cmap, idx2, fixed_idx == line_id, pal, pairs, BAYER)
        idx = np.where(alive, idx2, -1)
        if verbose:
            print('refine changed', nchg, 'dots cleaned', ndot)
    # ---- 5. cleanup: isolated specks ------------------------------------------
    idx = despeckle(idx, protect=set(g['light']) | {line_id}, linecells=np.zeros_like(oc))
    if p['REFINE']:
        # despeckling can leave a new anti-aliasing dot: one more dot pass, by colour
        cm = np.full(idx.shape, -1, np.int32)
        _, idx, _ = RF.clean_dots(cm, idx.copy(), (fixed_idx == line_id) | (idx < 0), pal, pairs, BAYER)
    alpha = idx >= 0
    rgb[alpha] = pal[idx[alpha]]
    info = dict(pairs=pairs, line_id=line_id, lines=lines, idx=idx, pal=pal, hexes=hexes, D=D, O=O, B=B,
                L=L, Lv=Lv, parts=parts, own=own, outer_cells=oc, shp=shp, g=g)
    if verbose:
        print('lines', len(lines), 'owned cells', alpha.sum())
    return rgb, alpha, info


def ids_dark(L, path, pal):
    """labels along a ridge path, keeping the darker half (the stroke, not the sides)."""
    v = L[path[:, 1].astype(int), path[:, 0].astype(int)]
    y = _lum(pal[v].astype(np.float32))
    return list(np.unique(v[y <= np.median(y)]))


def poly_cells(mask, smooth, x0, y0):
    """cells whose centre lies inside the mask's smoothed outer contour (a convex part
    such as the tongue then gets an even staircase)."""
    import cv2
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=len)[:, 0, :].astype(float)
    q = resample_closed(SH.smooth_contour(c, s=smooth, k=26, thr=75.0, straight_tol=2.5))
    jj, ii = np.indices((NY, NX))
    return points_in_polys([q], (ii + 0.5) * CW - x0, (jj + 0.5) * CH - y0)


def regularize_dither(cls, sel, min_cells, dclasses, pairs, iters=3, join=True):
    """Checker areas as continuous bands (cell level): a dither cell with at most 3 of
    its 3 x 3 neighbourhood in its class takes the neighbourhood's most common class; a
    plain cell with at least 6 neighbours of one dither class joins it (holes filled);
    dither islands under min_cells take their surroundings' most common plain class."""
    cls = cls.copy()
    p_join = 5
    H, W = cls.shape
    for _ in range(iters):
        new = cls.copy()
        for j in range(1, H - 1):
            for i in range(1, W - 1):
                if not sel[j, i]:
                    continue
                win = cls[j - 1:j + 2, i - 1:i + 2].ravel()
                win = win[win >= 0]
                c = cls[j, i]
                u, n = np.unique(win, return_counts=True)
                if c in dclasses and (win == c).sum() <= 3:
                    a_, b_ = pairs[(c - 1000) // 4]
                    o = [(k, x) for x, k in zip(u, n) if x != c and (x in dclasses or x in (a_, b_))]
                    if o:
                        new[j, i] = max(o)[1]
                elif join and 0 <= c < 1000:
                    o = [(k, x) for x, k in zip(u, n) if x in dclasses and k >= p_join and c in pairs[(x - 1000) // 4]]
                    if o:
                        new[j, i] = max(o)[1]
        cls = np.where(sel, new, cls)
    for c in np.unique(cls[sel]):
        if c not in dclasses:
            continue
        lab, n = ndi.label((cls == c) & sel)
        for k in range(1, n + 1):
            m = lab == k
            if m.sum() >= min_cells:
                continue
            ring = ndi.binary_dilation(m, np.ones((3, 3))) & ~m & (cls >= 0) & (cls < 1000)
            if ring.any():
                u, nn = np.unique(cls[ring], return_counts=True)
                cls[m] = u[nn.argmax()]
    return cls


def ear_bands(idx, cmap, fixed_idx, parts, L, I, J, p):
    """Ordered dithering of the painting's smoothed tone over the left ear: the per-cell
    luma (box mean, Gaussian 1 cell) is quantized to the ramp's tones and the 50 %
    checkers between them; the level map is mode-filtered and islands under EAR_ISLAND
    cells merged, so band borders follow the ear's form and each checker band is one
    continuous area on the global (i + j) lattice."""
    pal = p['_pal']
    ramp = DT.EAR_RAMP
    Yp = _lum(pal.astype(np.float32))
    # tone of the fill under the lines (lines and outline are drawn separately)
    vm = p['_valid'].astype(np.float32)
    Ysum, _ = cell_mean(Yp[p['_Lfull']].astype(np.float32) * vm, I, J)
    Vm, _ = cell_mean(vm, I, J)
    with np.errstate(invalid='ignore', divide='ignore'):
        Y = Ysum / Vm
    Yall, _ = cell_mean(Yp[p['_Lf']].astype(np.float32), I, J)
    Y = np.where(np.nan_to_num(Vm) > 0.2, Y, Yall)
    Y = np.nan_to_num(Y)
    Ys = ndi.gaussian_filter(Y, p['EAR_SIGMA']) if p['EAR_SIGMA'] > 0 else Y
    lv_y = []; lv_c = []
    P_ = [tuple(q) for q in p['PAIRS']]
    for k, c in enumerate(ramp):
        lv_y.append(Yp[c]); lv_c.append((c, c, 0))
        if k + 1 < len(ramp) and (c, ramp[k + 1]) not in p['EAR_NO_CHECK']:
            pa, pb = (c, ramp[k + 1]) if (c, ramp[k + 1]) in P_ else (ramp[k + 1], c)
            for q in p['EAR_QUARTERS']:      # share of pb: Bayer levels on the 2 x 2 lattice
                lv_y.append(Yp[pa] + q / 4.0 * (Yp[pb] - Yp[pa])); lv_c.append((pa, pb, q))
    lv_y = np.array(lv_y)
    ear, _ = cell_mean(parts['earL'].astype(np.float32), I, J)
    sel = (np.nan_to_num(ear) >= 0.5) & (fixed_idx < 0) & (idx >= 0)
    sel &= np.isin(idx, ramp)            # only the coat tones (lit rim and lines stay)
    lev = np.abs(Ys[..., None] - lv_y[None, None, :]).argmin(-1)
    lev = np.where(sel, lev, -1)
    # mode filter and island merge on the level map
    for _ in range(p['EAR_MODE']):
        new = lev.copy()
        for j, i in zip(*np.nonzero(sel)):
            w = lev[max(0, j - 1):j + 2, max(0, i - 1):i + 2].ravel(); w = w[w >= 0]
            u, n = np.unique(w, return_counts=True)
            if n.max() >= 5:
                new[j, i] = u[n.argmax()]
        lev = np.where(sel, new, lev)
    for v in np.unique(lev[sel]):
        lab, n = ndi.label((lev == v) & sel)
        for k in range(1, n + 1):
            m = lab == k
            if m.sum() >= p['EAR_ISLAND']:
                continue
            ring = ndi.binary_dilation(m, np.ones((3, 3))) & ~m & sel
            if ring.any():
                u, nn = np.unique(lev[ring], return_counts=True)
                lev[m] = u[nn.argmax()]
    jj, ii = np.indices(idx.shape)
    for v in np.unique(lev[sel]):
        a, b, q = lv_c[v]
        m = sel & (lev == v)
        useb = BAYER[jj % 2, ii % 2] < q
        idx[m & useb] = b
        idx[m & ~useb] = a
        cmap[m] = idx[m]
    return idx, cmap


def detail_cells(idx, cmap, fixed_idx, oc, shp, parts, L, I, J, line_id, p):
    """Round 2 cell rules.
    Jaw and silhouette: a near-black fill cell just inside the 1 px outline takes the
    coat's darkest tone, so the outline reads against the painted dark edge.
    Nose: the highlight is every nose cell at least HL_COVER cream in the painting; the
    grey and tan cells touching its left half become the nose's navy."""
    idx = idx.copy(); cmap = cmap.copy()
    st4 = ndi.generate_binary_structure(2, 1)
    inner = ndi.binary_dilation(oc, st4) & ~oc & (idx >= 0) & (fixed_idx < 0)
    dark = inner & np.isin(idx, [line_id] + p['BLACK_EXTRA'])
    dark &= ~(shp['eye'] | shp['nose'] | shp['tongue'] | shp['bandana'])
    jb = p['JAW_BOX']    # the jaw and cheek right of the mouth (cells)
    box = np.zeros_like(dark); box[jb[1]:jb[3], jb[0]:jb[2]] = True
    dark &= box
    # only long runs along the outline (a painted dark edge band), not the 1 to 3
    # cells where an inner crease meets the outline
    lab, n = ndi.label(dark, np.ones((3, 3)))
    if n:
        sz = ndi.sum(dark, lab, range(1, n + 1))
        dark = np.isin(lab, np.flatnonzero(sz >= p['JAW_RUN']) + 1)
    idx[dark] = p['JAW_TONE']; cmap[dark] = p['JAW_TONE']
    # nose highlight
    cream = p['HL_ID']
    m, _ = cell_mean(((L == cream) & parts['nose']).astype(np.float32), I, J)
    hl = shp['nose'] & (np.nan_to_num(m) >= p['HL_COVER']) & (fixed_idx < 0)
    idx[hl] = cream; cmap[hl] = cream
    hl = shp['nose'] & (idx == cream)
    if hl.any():
        jj, ii = np.nonzero(hl)
        cx = ii.mean()
        # the highlight's left half, its bounding box grown by one cell: grey and tan
        # gloss cells there become the nose's navy
        J_, I_ = np.indices(idx.shape)
        near = (J_ >= jj.min() - 1) & (J_ <= jj.max() + 1) & (I_ >= ii.min() - 1) & (I_ <= cx)
        near &= ~hl & shp['nose'] & (fixed_idx < 0) & np.isin(idx, p['HL_STRAY'])
        # warm greys and tan become the nose's own cool gloss tones of similar value
        for src_ids, dst in p['NOSE_MAP']:
            mm = near & np.isin(idx, src_ids)
            idx[mm] = dst; cmap[mm] = dst
    # dark specks left in the traced-detail boxes (not on a stroke): neighbours' colour
    for bx0, by0, bx1, by1 in DT.CLEAR_BOXES:
        i0_, i1_ = int(bx0 / CW), int(np.ceil(bx1 / CW)); j0_, j1_ = int(by0 / CH), int(np.ceil(by1 / CH))
        for j_ in range(max(1, j0_), min(NY - 1, j1_)):
            for i_ in range(max(1, i0_), min(NX - 1, i1_)):
                if fixed_idx[j_, i_] >= 0 or idx[j_, i_] not in [line_id] + p['BLACK_EXTRA']:
                    continue
                win = idx[j_ - 1:j_ + 2, i_ - 1:i_ + 2].ravel()
                darkn = np.isin(win, [line_id] + p['BLACK_EXTRA']).sum() - 1
                if darkn <= 1:
                    v = win[(win >= 0) & ~np.isin(win, [line_id] + p['BLACK_EXTRA'])]
                    if len(v):
                        u, n = np.unique(v, return_counts=True)
                        idx[j_, i_] = u[n.argmax()]; cmap[j_, i_] = u[n.argmax()]
    # left ear: tone bands on one continuous checker lattice
    if p['EAR_BANDS']:
        idx, cmap = ear_bands(idx, cmap, fixed_idx, parts, L, I, J, p)
    # eye: catchlight and sclera crescent as hand-placed cells (pepper_detail.py)
    want = np.zeros(idx.shape, bool)
    for j_, i_ in DT.EYE_CREAM:
        want[j_, i_] = True
    want &= (fixed_idx < 0)
    old_cream = shp['eye'] & (idx == cream) & ~want & (fixed_idx < 0)
    for j_, i_ in zip(*np.nonzero(old_cream)):
        y0_, y1_ = np.nonzero(J == j_)[0][[0, -1]]; x0_, x1_ = np.nonzero(I == i_)[0][[0, -1]]
        v = L[y0_:y1_ + 1, x0_:x1_ + 1].ravel(); v = v[v != cream]
        u, n = np.unique(v, return_counts=True)
        c = int(u[n.argmax()]) if len(u) else line_id
        idx[j_, i_] = c; cmap[j_, i_] = c
    idx[want] = cream; cmap[want] = cream
    # single-use colours in the bandana snap to the bandana's pink ramp
    ramp = p['PINK_RAMP']
    labp = S.srgb_to_lab(p['_pal'])
    band = shp['bandana'] & (fixed_idx < 0)
    for c in np.unique(idx[band]):
        if c in ramp or c < 0:
            continue
        mm = band & (idx == c)
        if (idx == c).sum() <= p['RARE_MAX']:
            dst = ramp[int(np.argmin([np.linalg.norm(labp[c] - labp[r]) for r in ramp]))]
            idx[mm] = dst; cmap[mm] = dst
    return idx, cmap


def mode_label(L, path, ids):
    v = L[path[:, 1].astype(int), path[:, 0].astype(int)]
    v = v[np.isin(v, ids)]
    if len(v) == 0:
        return ids[0]
    u, n = np.unique(v, return_counts=True)
    return int(u[n.argmax()])


def despeckle(idx, protect, linecells):
    """a single cell whose colour no 8-neighbour shares, surrounded by one colour on
    at least 6 of 8 sides, takes that colour (protected colours stay)."""
    out = idx.copy()
    H, W = idx.shape
    for j in range(1, H - 1):
        for i in range(1, W - 1):
            c = idx[j, i]
            if c < 0 or c in protect:
                continue
            nb_ = idx[j - 1:j + 2, i - 1:i + 2].ravel()
            nb_ = np.delete(nb_, 4)
            if (nb_ == c).any():
                continue
            # a dot of a regular 2 x 2 pattern (same colour two cells away) stays
            if (j >= 2 and idx[j - 2, i] == c) or (j + 2 < H and idx[j + 2, i] == c) or \
               (i >= 2 and idx[j, i - 2] == c) or (i + 2 < W and idx[j, i + 2] == c):
                continue
            u, n = np.unique(nb_[nb_ >= 0], return_counts=True)
            if len(u) and n.max() >= 6:
                out[j, i] = u[n.argmax()]
    return out


def save_rgba(rgb, alpha, path):
    a = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    Image.fromarray(a, 'RGBA').save(path)


if __name__ == '__main__':
    out = os.environ.get('PEPPER_OUT', '/home/claude/wt/rg-pepper/out')
    rgb, alpha, info = render()
    save_rgba(rgb, alpha, os.path.join(out, 'pepper_region.png'))
