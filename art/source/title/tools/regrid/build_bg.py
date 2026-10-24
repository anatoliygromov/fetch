"""Step 3: the whole picture at 320x240 on the local grid with the global palette.

Every output pixel is one palette colour that really occurs inside its cell:
  1. every source pixel is snapped to its nearest palette colour (Lab);
  2. each cell votes (Proper Pixel Art / Perfect Pixel "most common colour per cell"):
     flat pixels weigh 1, anti-aliased edge pixels 0.25, the cell's outer ring 0.35,
     pixels far from every palette colour 0.3. No mean, no median, no blend;
  3. thin features (masts, rigging, rails, sparkle rows: painted strokes thinner than
     a cell) are kept as 1 px lines: a minority colour that forms a stripe across
     the cell (background on both sides, or a thin union with the neighbour cell)
     and continues into the next cell along the stripe wins the cell;
  4. checker dither (Pepper's coat): where the painting interleaves two neighbouring
     coat ramp values, the cells are rebuilt as a regular 1-cell checker in global
     phase ((x + y) even = darker value), solid where one value dominates;
  5. pixel rules: a pixel whose colour lies between its two opposite neighbours across
     a strong edge (a mixel) takes whichever of those two colours is better supported
     in its cell; low-contrast single specks take the surrounding colour when that
     colour is also well supported in the cell.
"""
import numpy as np, os, json, sys
from PIL import Image
from scipy import ndimage as ndi
from common import load_src, srgb_to_lab, NX, NY, OUT, CACHE, load_mask, hexs, unhex
import grid as G
import qa
import labels as LB

FLAT_T = 10


def nearest_palette(lab, PL, chunk=1 << 19):
    flat = lab.reshape(-1, 3)
    idx = np.empty(len(flat), np.int16); dist = np.empty(len(flat), np.float32)
    for s in range(0, len(flat), chunk):
        d = ((flat[s:s + chunk, None, :] - PL[None]) ** 2).sum(-1)
        k = d.argmin(1); idx[s:s + chunk] = k; dist[s:s + chunk] = np.sqrt(d[np.arange(len(k)), k])
    return idx.reshape(lab.shape[:2]), dist.reshape(lab.shape[:2])


def votes(a, I, J, Lp, dp, n):
    g = LB.flatness(a)
    inn = LB.interior_mask(I, J)
    w = np.where(g < FLAT_T, 1.0, 0.25) * np.where(inn, 1.0, 0.35) * np.where(dp < 12, 1.0, 0.3)
    cell = (J.astype(np.int64) * NX + I).ravel()
    key = cell * n + Lp.ravel()
    V = np.bincount(key, weights=w.ravel(), minlength=NX * NY * n).reshape(NY, NX, n)
    # C: fraction of the cell's pixels that are FLAT and of this colour (a colour that
    # really occurs in the cell, not an anti-aliasing blend)
    fl = (g < FLAT_T) & (dp < 12)
    C = np.bincount(key, weights=fl.ravel().astype(np.float64), minlength=NX * NY * n).reshape(NY, NX, n)
    tot = np.bincount(cell, minlength=NX * NY).reshape(NY, NX, 1)
    C = (C / np.maximum(tot, 1)).astype(np.float32)
    return V, C


def stripe(m):
    """m: bool mask of one colour inside a cell box. Returns (orient, lo_touch, hi_touch, width) or None.
    orient 'v': a vertical stripe of full-ish height; 'h': horizontal."""
    best = None
    for orient, ax in (('v', 0), ('h', 1)):
        occ = m.mean(ax)                       # per column (v) / per row (h) occupancy
        cols = occ >= 0.6
        if cols.sum() == 0:
            continue
        idx = np.flatnonzero(cols)
        if idx[-1] - idx[0] + 1 != len(idx):   # not contiguous
            continue
        w = len(idx); L = len(occ)
        if w > 0.6 * L:
            continue
        if m.sum() < 0.7 * w * m.shape[ax]:    # stripe must cover most of its band
            continue
        lo, hi = idx[0] == 0, idx[-1] == L - 1
        cand = (orient, lo, hi, w, occ[cols].mean())
        if best is None or cand[4] > best[4]:
            best = cand
    return best


def between(c, a, b, tol=0.4):
    ab = b - a; L2 = float((ab ** 2).sum())
    if L2 < 1e-6:
        return False
    t = float(((c - a) * ab).sum()) / L2
    dseg = float(np.linalg.norm(c - (a + t * ab)))
    return -0.1 < t < 1.1 and dseg < tol * np.sqrt(L2) + 4


def thin_features(Lp, PL, XB, YB, win, C, min_cov=0.10, max_cov=0.6, min_de=18.0):
    """Returns dict (j, i) -> label for cells taken over by a thin stroke."""
    n = PL.shape[0]
    dwin = np.linalg.norm(PL[win][..., None, :] - PL[None, None], axis=-1)   # NY x NX x n
    cand = (C >= min_cov) & (C <= max_cov) & (dwin >= min_de)
    cand[np.arange(NY)[:, None], np.arange(NX)[None], win] = False
    found = {}
    for j, i, l in zip(*np.nonzero(cand)):
        x0, x1 = XB[j, i], XB[j, i + 1]; y0, y1 = YB[i, j], YB[i, j + 1]
        if x1 - x0 < 3 or y1 - y0 < 3:
            continue
        m = Lp[y0:y1, x0:x1] == l
        s = stripe(m)
        if s is None:
            continue
        orient, lo, hi, w, occ = s
        if lo and hi:
            continue
        found.setdefault((j, i), []).append((l, orient, lo, hi, w, C[j, i, l]))
    # thin union across a touched side; continuity along the stripe
    out = {}
    def has(jj, ii, l, orient):
        if not (0 <= jj < NY and 0 <= ii < NX):
            return False
        if win[jj, ii] == l:
            return True
        return any(e[0] == l and e[1] == orient for e in found.get((jj, ii), []))
    for (j, i), lst in found.items():
        for (l, orient, lo, hi, w, cov) in sorted(lst, key=lambda e: -e[5]):
            if orient == 'v':
                along = [(j - 1, i), (j + 1, i)]; across = {(True): (j, i - 1), (False): (j, i + 1)}
            else:
                along = [(j, i - 1), (j, i + 1)]; across = {(True): (j - 1, i), (False): (j + 1, i)}
            if not any(has(jj, ii, l, orient) for jj, ii in along):
                continue
            ok = True
            for side, touch in ((True, lo), (False, hi)):
                if not touch:
                    continue
                jj, ii = across[side]
                if not (0 <= jj < NY and 0 <= ii < NX):
                    continue
                if win[jj, ii] == l:
                    ok = False; break             # part of a block, not a thin stroke
                if between(PL[l], PL[win[j, i]], PL[win[jj, ii]]):
                    ok = False; break             # an anti-aliasing band between two blocks
                other = [e for e in found.get((jj, ii), []) if e[0] == l and e[1] == orient]
                if other:
                    o = other[0]
                    if o[4] + w > 6:               # union too wide for a thin stroke
                        ok = False; break
                    if o[5] > cov or (o[5] == cov and side):
                        ok = False; break          # the neighbour carries it
            if ok:
                out[(j, i)] = l
                break
    return out


def coat_checker(R, V, coat_ramp, region, PL, dmax=30.0):
    """Rebuild interleaved pairs of neighbouring coat values as a regular checker."""
    R = R.copy()
    rank = {l: k for k, l in enumerate(coat_ramp)}
    pos = np.full(R.shape, np.nan)
    for l, k in rank.items():
        pos[R == l] = k
    inr = region & ~np.isnan(pos)
    yy, xx = np.mgrid[0:NY, 0:NX]
    par = (yy + xx) % 2 == 0
    changed = np.zeros(R.shape, bool)
    # candidate pairs: any two coat values 5..30 apart in Lab, most frequent pairs first
    pairs = []
    for x in range(len(coat_ramp)):
        for y in range(x + 1, len(coat_ramp)):
            lo, hi = coat_ramp[x], coat_ramp[y]
            d = np.linalg.norm(PL[lo] - PL[hi])
            if 5 <= d <= dmax:
                adj = ((R[:, :-1] == lo) & (R[:, 1:] == hi)).sum() + ((R[:, :-1] == hi) & (R[:, 1:] == lo)).sum()
                pairs.append((adj, lo, hi))
    pairs.sort(reverse=True)
    for _, lo, hi in pairs:
        if PL[lo, 0] > PL[hi, 0]:
            lo, hi = hi, lo
        A = (R == lo) & inr & ~changed; B = (R == hi) & inr & ~changed
        AB = A | B
        k5 = np.ones((5, 5))
        nA = ndi.convolve(A.astype(float), k5, mode='constant'); nB = ndi.convolve(B.astype(float), k5, mode='constant')
        # A-B adjacencies in the window
        adj = np.zeros(R.shape)
        adj[:, :-1] += (A[:, :-1] & B[:, 1:]) | (B[:, :-1] & A[:, 1:])
        adj[:-1] += (A[:-1] & B[1:]) | (B[:-1] & A[1:])
        same = np.zeros(R.shape)
        same[:, :-1] += AB[:, :-1] & AB[:, 1:]
        same[:-1] += AB[:-1] & AB[1:]
        nadj = ndi.convolve(adj, k5, mode='constant'); nsame = ndi.convolve(same, k5, mode='constant')
        tot = nA + nB
        zone = AB & (tot >= 15) & (nA >= 0.25 * tot) & (nB >= 0.25 * tot) & (nadj >= 0.35 * nsame)
        # continuous tone bands: close gaps, fill holes, drop islands under 10 cells
        zone = ndi.binary_closing(zone, np.ones((3, 3))) & AB
        zone = ndi.binary_fill_holes(zone) & AB
        lz, nz = ndi.label(zone)
        if nz:
            sz = ndi.sum(zone, lz, range(1, nz + 1))
            zone = np.isin(lz, np.flatnonzero(sz >= 10) + 1)
        # local share of the lighter value (5x5, smooth) decides solid A, checker, solid B;
        # hysteresis keeps solid patches from forming islands inside a checker band
        fB = ndi.convolve(B.astype(float), k5, mode='constant') / np.maximum(ndi.convolve(AB.astype(float), k5, mode='constant'), 1)
        newv = np.where(fB < 0.2, lo, np.where(fB > 0.8, hi, np.where(par, lo, hi)))
        R[zone] = newv[zone]; changed |= zone
    return R, changed


def mixel_mask(R, PL, min_edge=20.0):
    c = PL[R]
    out = np.zeros(R.shape, bool)
    for ax in (0, 1):
        a = np.roll(c, 1, ax); b = np.roll(c, -1, ax)
        ra = np.roll(R, 1, ax); rb = np.roll(R, -1, ax)
        ab = b - a; L2 = (ab ** 2).sum(-1)
        t = ((c - a) * ab).sum(-1) / np.maximum(L2, 1e-6)
        proj = a + t[..., None] * ab
        dseg = np.linalg.norm(c - proj, axis=-1)
        m = (ra != rb) & (R != ra) & (R != rb) & (np.sqrt(L2) >= min_edge) & (t > 0.12) & (t < 0.88) & (dseg < 0.3 * np.sqrt(L2))
        m &= ~qa.run3(R, 1 - ax)
        if ax == 0:
            m[0] = m[-1] = False
        else:
            m[:, 0] = m[:, -1] = False
        out |= m
    return out


def fix_mixels(R, V, PL, iters=6, locked=None):
    """Replace each mixel by one of its two opposite neighbours: the one better supported
    in the cell's own painting pixels; if neither occurs in the cell, the nearer colour."""
    R = R.copy()
    for _ in range(iters):
        mm = mixel_mask(R, PL)
        if not mm.any():
            break
        for j, i in zip(*np.nonzero(mm)):
            if locked is not None and locked[j, i]:
                continue
            cands = {int(R[y, x]) for y, x in ((j, i - 1), (j, i + 1), (j - 1, i), (j + 1, i))
                     if 0 <= y < NY and 0 <= x < NX}
            cands.discard(int(R[j, i]))
            def score(l):
                old = R[j, i]; R[j, i] = l
                nm = sum(is_mixel(R, PL, y, x) for y in range(j - 1, j + 2) for x in range(i - 1, i + 2)
                         if 0 <= y < NY and 0 <= x < NX)
                R[j, i] = old
                return (-nm, V[j, i, l], -np.linalg.norm(PL[l] - PL[R[j, i]]))
            R[j, i] = max(cands, key=score)
    return R


def despeckle(R, V, PL, max_de=15.0):
    R = R.copy()
    H, W = R.shape
    for j in range(1, H - 1):
        for i in range(1, W - 1):
            nb = R[j - 1:j + 2, i - 1:i + 2].ravel()
            nb = np.delete(nb, 4)
            if (nb == R[j, i]).any():
                continue
            vals, cnt = np.unique(nb, return_counts=True)
            m = vals[cnt.argmax()]
            if cnt.max() < 5:
                continue
            de = np.linalg.norm(PL[R[j, i]] - PL[m])
            weak = V[j, i, m] >= 0.7 * V[j, i, R[j, i]]
            if de < max_de or weak:
                R[j, i] = m
    return R


def is_mixel(R, PL, j, i, min_edge=20.0):
    if not (0 < j < NY - 1 and 0 < i < NX - 1):
        return False
    r = R[j, i]; c = PL[r]
    for (a, b), along in (((R[j, i - 1], R[j, i + 1]), 0), ((R[j - 1, i], R[j + 1, i]), 1)):
        if a == b or r == a or r == b:
            continue
        if along == 0:
            run = [R[y, i] == r if 0 <= y < NY else False for y in (j - 2, j - 1, j + 1, j + 2)]
        else:
            run = [R[j, x] == r if 0 <= x < NX else False for x in (i - 2, i - 1, i + 1, i + 2)]
        if (run[1] and run[2]) or (run[0] and run[1]) or (run[2] and run[3]):
            continue
        A = PL[a]; ab = PL[b] - A; L2 = float(ab @ ab)
        if L2 < min_edge * min_edge:
            continue
        t = float((c - A) @ ab) / L2
        if 0.12 < t < 0.88 and np.linalg.norm(c - (A + t * ab)) < 0.3 * np.sqrt(L2):
            return True
    return False


def is_speck(R, j, i):
    if not (0 < j < NY - 1 and 0 < i < NX - 1):
        return False
    w = R[j - 1:j + 2, i - 1:i + 2]
    return int((w == R[j, i]).sum()) == 1


STROKE_T = 20.0      # Lab contrast of a stroke against both sides
STROKE_MINLEN = 15   # px along the stroke
STROKE_W = (1.5, 6.0)
STROKE_MINCELLS = 4  # shorter strokes are left to the cell vote  # median width in px (thinner than a cell)


def ridge(lab, axis, rs=(3, 4)):
    """Stroke strength across `axis` (axis=1: vertical strokes, compare left/right).
    A pixel belongs to a stroke when it differs from the pixels r px away on BOTH sides
    and is not a blend of them (anti-aliasing between two blocks)."""
    best = np.zeros(lab.shape[:2], np.float32)
    for r in rs:
        A = np.roll(lab, r, axis); B = np.roll(lab, -r, axis)
        s = np.minimum(np.linalg.norm(lab - A, axis=2), np.linalg.norm(lab - B, axis=2))
        ab = B - A; L2 = (ab ** 2).sum(2)
        t = ((lab - A) * ab).sum(2) / np.maximum(L2, 1e-6)
        dseg = np.linalg.norm(lab - (A + t[..., None] * ab), axis=2)
        blend = (np.sqrt(L2) > 15) & (t > 0.1) & (t < 0.9) & (dseg < 0.35 * np.sqrt(L2))
        s[blend] = 0
        best = np.maximum(best, s)
    return best


def strokes(lab, Lp, XB, YB, I, J):
    """Thin painted strokes (masts, rigging, thin posts): components of the ridge mask that
    are long and thinner than a cell. Each is fitted with a straight line in local cell
    coordinates (or followed row by row when curved) and rasterised as a 1 px digital line
    in ONE colour (the most common palette colour on the stroke's centre line).
    Returns list of (cells [(j, i)], label, full-res mask)."""
    H, W = Lp.shape
    out = []
    for axis in (1, 0):
        rd = ridge(lab, axis)
        m = rd >= STROKE_T
        lab_c, n = ndi.label(m, np.ones((3, 3)))
        objs = ndi.find_objects(lab_c)
        for k, sl in enumerate(objs):
            if sl is None:
                continue
            comp = lab_c[sl] == k + 1
            if axis == 0:
                comp = comp.T                      # work as if vertical: rows = along
            along = comp.shape[0]
            if along < STROKE_MINLEN:
                continue
            widths = comp.sum(1); rows = np.flatnonzero(widths)
            if len(rows) < 0.8 * along:
                continue
            wmed = np.median(widths[rows])
            if not (STROKE_W[0] <= wmed <= STROKE_W[1]):
                continue
            if along < 4 * wmed:
                continue
            # centre line per row (in full-res coords)
            xs = np.array([np.flatnonzero(comp[r]).mean() for r in rows])
            if axis == 1:
                ys_f = rows + sl[0].start; xs_f = xs + sl[1].start
            else:
                xs_f = rows + sl[1].start; ys_f = xs + sl[0].start   # along = x, across = y
            yi = np.clip(np.round(ys_f).astype(int), 0, H - 1); xi = np.clip(np.round(xs_f).astype(int), 0, W - 1)
            # stroke colour: the palette colour carrying most ridge strength (the core of the
            # stroke contrasts most with both sides; a highlight strip beside it does not)
            mfull = np.zeros((H, W), bool); mfull[sl] = lab_c[sl] == k + 1
            col = np.bincount(Lp[mfull], weights=rd[mfull]).argmax()
            # local cell coordinates of the centre points
            jj = J[yi, xi].astype(int); ii = I[yi, xi].astype(int)
            if axis == 1:
                u = ii + (xs_f - XB[jj, ii]) / np.maximum(XB[jj, ii + 1] - XB[jj, ii], 1)   # across
                v = jj.astype(float)
            else:
                u = jj + (ys_f - YB[ii, jj]) / np.maximum(YB[ii, jj + 1] - YB[ii, jj], 1)
                v = ii.astype(float)
            cells = []
            vals = np.unique(v.astype(int))
            # straight fit u = a v + b if it explains the stroke, else per-row median
            if len(vals) >= 2:
                A_ = np.c_[v, np.ones_like(v)]
                coef, *_ = np.linalg.lstsq(A_, u, rcond=None)
                res = np.abs(A_ @ coef - u)
                straight = np.percentile(res, 90) <= 0.6
            else:
                straight = True; coef = np.array([0.0, np.median(u)])
            # a stroke row must be covered by at least 40% of the cell's extent
            for vv in vals:
                # a cell row (column) belongs to the stroke only when the painted stroke
                # covers about two thirds of it: the line starts and ends where the painting does
                if axis == 1:
                    cc = int(np.clip(np.median(ii[v.astype(int) == vv]), 0, NX - 1))
                    ext = YB[cc, vv + 1] - YB[cc, vv]
                else:
                    cc = int(np.clip(np.median(jj[v.astype(int) == vv]), 0, NY - 1))
                    ext = XB[cc, vv + 1] - XB[cc, vv]
                if (v.astype(int) == vv).sum() < max(3, 0.65 * ext):
                    continue
                uu = coef[0] * vv + coef[1] if straight else np.median(u[v.astype(int) == vv])
                c = int(np.floor(uu))
                cells.append((vv, c) if axis == 1 else (c, vv))
            if len(cells) >= STROKE_MINCELLS:
                mask = np.zeros((H, W), bool); mask[sl] = lab_c[sl] == k + 1
                out.append((cells, int(col), mask, axis, (yi, xi)))
    return out


def pepper_mask(lab, I, J):
    """Pepper's full silhouette at the painting's resolution: inside the rough 320x240
    material masks (dilated 2 cells), the pixels with Pepper's colours (neutral darks of
    the coat and outline, the bandana pink), closed, opened, largest piece, holes filled."""
    P = np.zeros((NY, NX), bool)
    for nme in ('coat', 'bandana', 'eye', 'nose', 'tongue'):
        P |= load_mask(nme)
    P = ndi.binary_fill_holes(P)
    L = lab[..., 0]; chroma = np.hypot(lab[..., 1], lab[..., 2])
    pep = ((L < 40) & (chroma < 14)) | ((lab[..., 1] > 35) & (L > 35))
    full = ndi.binary_dilation(P, iterations=2)[J, I] & pep
    full = ndi.binary_closing(full, iterations=2)
    full = ndi.binary_opening(full, iterations=4)
    lab_c, n = ndi.label(full)
    sz = ndi.sum(full, lab_c, range(1, n + 1))
    full = lab_c == (np.argmax(sz) + 1)
    return ndi.binary_fill_holes(full)


def masked_votes(a, I, J, Lp, dp, n, keep):
    """Votes counting only the pixels in `keep`."""
    return votes(a, I, J, np.where(keep, Lp, n), np.where(keep, dp, 99), n + 1)


def outline_ring(Sm):
    """1 px outline of a shape: shape cells with a 4-neighbour outside (image border
    excluded), then pixel-perfect (one pixel of every L-corner double dropped)."""
    out = ~Sm
    ring = np.zeros_like(Sm)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(out, (dy, dx), (0, 1))
        if dy == 1: nb[0] = False
        if dy == -1: nb[-1] = False
        if dx == 1: nb[:, 0] = False
        if dx == -1: nb[:, -1] = False
        ring |= Sm & nb
    for _ in range(6):
        n_l, lc = qa.lcorners(ring)
        if n_l == 0:
            break
        lab_l, nl = ndi.label(lc)
        for q in range(1, nl + 1):
            ys, xs = np.nonzero(lab_l == q)
            ring[ys[0], xs[0]] = False
    return ring


def regularize(Sm, cov, passes=4, band=(0.2, 0.8), measure=None):
    """Greedy staircase clean-up of a rasterised shape: flip boundary cells whose
    coverage is not decisive (band) when the flip lowers the number of irregular
    staircase windows (jaggies such as 1,4,1 or 4,1,3) on the boundary."""
    Sm = Sm.copy()
    def irregular(m):
        if measure is not None:
            f, n, bad = qa.staircase_regularity(measure(m), line=True)
        else:
            f, n, bad = qa.staircase_regularity(m)
        return len(bad), n
    cur, _ = irregular(Sm)
    flips = 0
    for _ in range(passes):
        changed = False
        inner = Sm & ~ndi.binary_erosion(Sm)
        outer = ndi.binary_dilation(Sm) & ~Sm
        cand = np.argwhere((inner | outer) & (cov > band[0]) & (cov < band[1]))
        # most ambiguous first
        cand = sorted(cand.tolist(), key=lambda p: abs(cov[p[0], p[1]] - 0.5))
        for j, i in cand:
            Sm[j, i] = ~Sm[j, i]
            nb, _ = irregular(Sm)
            if nb < cur:
                cur = nb; flips += 1; changed = True
            else:
                Sm[j, i] = ~Sm[j, i]
        if not changed:
            break
    return Sm, flips


def pepper_outline(a, lab, Lp, dp, I, J, PL, n, smooth=8.0):
    """Pepper's silhouette as a smooth shape on the grid and its 1 px black outline.
    Returns (shape cells, outline cells, outline colour, V_in, V_out, full-res mask)."""
    import shapes
    full = pepper_mask(lab, I, J)
    Sm, Sfull = shapes.raster_shape(full, I, J, s=smooth, pre=2.0)
    Sm = ndi.binary_fill_holes(Sm)
    # remove slivers one or two cells wide (they would give doubled outlines); restore
    # tiny corner bits the opening shaves off (ear tips)
    op = ndi.binary_opening(Sm, np.ones((3, 3)))
    diff, nd = ndi.label(Sm & ~op)
    for q in range(1, nd + 1):
        if (diff == q).sum() <= 2:
            op |= diff == q
    Sm = op
    lab_s, ns = ndi.label(Sm)
    if ns > 1:
        sz = ndi.sum(Sm, lab_s, range(1, ns + 1)); Sm = lab_s == (np.argmax(sz) + 1)
    Sm, _ = regularize(Sm, shapes.coverage(Sfull, I, J), passes=8, band=(0.05, 0.95), measure=outline_ring)
    ring = outline_ring(Sm)
    # outline colour: the most common palette colour of the painting's outline band
    dist_in = ndi.distance_transform_edt(full)
    band = full & (dist_in <= 7) & (lab[..., 0] < 12)
    col = int(np.bincount(Lp[band]).argmax())
    # interior votes without the outline band; exterior votes without Pepper
    Vin, Cin = masked_votes(a, I, J, Lp, dp, n, full & ~((dist_in <= 9) & (lab[..., 0] < 12)))
    Vout, Cout = masked_votes(a, I, J, Lp, dp, n, ~ndi.binary_dilation(full, iterations=2))
    return Sm, ring, col, (Vin[..., :n], Cin[..., :n]), (Vout[..., :n], Cout[..., :n]), full


# dark structures rebuilt as shapes (railing, bench): (name, 320 mask, max Lab L of the class)
# (name, 320 mask, extra region box in cells or None, max Lab L, max Lab b)
STRUCTURES = [('railing', 'railing', (110, 168, 320, 205), 20.0, -12.0), ('bench', 'bench', None, 20.0, 99.0),
              ('lamp', 'lamp', None, 16.0, 99.0)]


def structure_layer(R, V, a, lab, Lp, dp, I, J, PL, n, mask_name, box, maxL, maxb, exclude_full, exclude320, smooth=3.0):
    """A dark painted structure (railing bars and rails, bench frame) as one shape: its dark
    pixels inside the material mask are smoothed and rasterised at coverage 0.5 (straight
    bars stay 1 cell wide and continuous), every connected piece takes ONE dark colour (the
    best supported one in its cells), and region cells outside the shape re-vote without
    the dark pixels. Returns (R, V, cells changed, shape mask)."""
    import shapes
    reg = ndi.binary_dilation(load_mask(mask_name), iterations=1)
    if box is not None:
        x0, y0, x1, y1 = box
        reg[y0:y1, x0:x1] = True
    reg &= ~exclude320
    cls_full = (lab[..., 0] < maxL) & (lab[..., 2] < maxb)
    full = reg[J, I] & cls_full & ~exclude_full
    if full.sum() < 50:
        return R, V, np.zeros(R.shape, bool), np.zeros(R.shape, bool)
    Sm, _ = shapes.raster_shape(full, I, J, s=smooth, pre=1.0, min_area=30)
    Sm &= reg
    dark = (PL[:, 0] < maxL) & (PL[:, 2] < maxb)
    R = R.copy(); V = V.copy()
    changed = np.zeros(R.shape, bool)
    # thin parts (bars, rails: not inside a 3x3 opening) take ONE colour per piece so a
    # rail never alternates between two dark values; thick parts (a bin, a post) keep a
    # per-cell vote among the dark colours, so their painted shading survives
    thick = ndi.binary_opening(Sm, np.ones((3, 3)))
    lab_c, nc = ndi.label(Sm, np.ones((3, 3)))
    for q in range(1, nc + 1):
        cm = lab_c == q
        tot = (V[cm & ~thick] * dark[None]).sum(0)
        if tot.sum() > 0:
            thin_c = cm & ~thick
            R[thin_c] = int(tot.argmax()); changed |= thin_c
    vd = V * dark[None, None]
    tk = thick & (vd.sum(2) > 0)
    R[tk] = vd.argmax(2)[tk]; changed |= tk
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~(reg[J, I] & cls_full))
    outside = reg & ~Sm & dark[R] & (Vo[..., :n].sum(2) > 0)
    R[outside] = Vo[..., :n].argmax(2)[outside]
    V[outside] = Vo[..., :n][outside]
    changed |= outside
    return R, V, changed, Sm


TEXTURE_MATERIALS = ('leaves', 'flowers')


def speck_rule(R, PL, ramps, locked, texture_cells, C=None, passes=3, block=0.5, strict=None):
    """Single-pixel specks (no 8-neighbour shares the colour): kept only where the painting
    has them as texture (foliage, flowers, checker dither, and the locked line layers);
    every other speck snaps to the most common 8-neighbour colour of the cell's own
    material (its ramp), else to the most common neighbour colour. A speck the painting
    paints as a block of its own (that colour covers >= `block` of the cell in flat pixels,
    or is the cell's most common flat colour with >= 25 %: a window, a sparkle) is the
    painting's, not noise, and stays."""
    mat, names = LB.material_map()
    R = R.copy()
    removed = kept = 0
    for _ in range(passes):
        n_sp, sp = qa.specks(R.astype(np.int64), np.ones(R.shape, bool))
        keep = locked | texture_cells
        if C is not None:
            jj, ii = np.nonzero(sp)
            painted = np.zeros(R.shape, bool)
            weak_ok = ~strict[jj, ii] if strict is not None else np.ones(len(jj), bool)
            painted[jj, ii] = (C[jj, ii, R[jj, ii]] >= block) | (
                (C[jj, ii].argmax(1) == R[jj, ii]) & (C[jj, ii, R[jj, ii]] >= 0.25) & weak_ok)
            keep = keep | painted
        todo = sp & ~keep
        kept = int((sp & keep).sum())
        if not todo.any():
            break
        for j, i in np.argwhere(todo):
            nb = [int(R[y, x]) for y in range(j - 1, j + 2) for x in range(i - 1, i + 2)
                  if (y, x) != (j, i) and 0 <= y < NY and 0 <= x < NX]
            ramp = set(ramps.get(names[mat[j, i]], []))
            same = [l for l in nb if l in ramp]
            pool = same if same else nb
            vals, cnt = np.unique(pool, return_counts=True)
            R[j, i] = vals[cnt.argmax()]; removed += 1
    return R, removed, kept


def unify_small_features(R, PL, C, Vfull, locked, de=12.0, reach=12):
    """Small painted features of one kind (a row of windows: blobs of 1 to 2 cells on the
    same surrounding colour, within `reach` cells along a row) that landed on two nearby
    palette colours take the colour most of them have, when that colour is close (dE < de)
    and also occurs in the cell's own painting pixels."""
    lab_c, nc = ndi.label(np.ones(R.shape, bool) & False)
    feats = []
    for col in np.unique(R):
        m = R == col
        lc, k = ndi.label(m)
        if k == 0:
            continue
        sizes = ndi.sum(m, lc, range(1, k + 1))
        for q in np.flatnonzero(sizes <= 2) + 1:
            cells = np.argwhere(lc == q)
            ring = ndi.binary_dilation(lc == q) & ~(lc == q)
            sv, sc = np.unique(R[ring], return_counts=True)
            feats.append((cells, int(col), int(sv[sc.argmax()])))
    changed = 0
    for idx, (cells, col, bg) in enumerate(feats):
        j, i = cells[0]
        group = [f for f in feats if f[2] == bg and abs(f[0][0][0] - j) <= 1 and abs(f[0][0][1] - i) <= reach
                 and np.linalg.norm(PL[f[1]] - PL[col]) < de]
        if len(group) < 3:
            continue
        cols, cnt = np.unique([f[1] for f in group], return_counts=True)
        tgt = int(cols[cnt.argmax()])
        if tgt == col or cnt.max() <= len(group) / 2:
            continue
        if all((C[y, x, tgt] > 0.02 or Vfull[y, x, tgt] > 0) and not locked[y, x] for y, x in cells):
            for y, x in cells:
                R[y, x] = tgt; changed += 1
    return R, changed


# ---------------------------------------------------------------- round 3 rules
BRIDGE_BOX = (1080, 1088, 1760, 1146)   # source px: deck and arches


def rebuild_arches(R, Lp, lab, locked, PL):
    """Each painted arch of the bridge becomes a clean symmetric stepped arch: its opening
    (non-stone pixels in the arch band) gives a centre and a half width per row, the half
    widths are made symmetric and monotone (wider downwards), and the arch is rasterised
    on the uniform grid, centred on a cell centre or a cell border (whichever is nearer),
    in the arch's own shadow colour; stray dark cells beside it take the stone colour."""
    x0, y0, x1, y1 = BRIDGE_BOX
    L = lab[y0:y1, x0:x1, 0]; ch = np.hypot(lab[y0:y1, x0:x1, 1], lab[y0:y1, x0:x1, 2])
    stone = (L > 55) & (ch < 30)
    band = np.zeros_like(stone); band[14:45] = True          # y 1110 to 1140 (water starts at 1144)
    lab_c, nc = ndi.label(~stone & band)
    R = R.copy(); n_arch = 0
    for q in range(1, nc + 1):
        comp = lab_c == q
        ys, xs = np.nonzero(comp)
        if xs.max() - xs.min() < 40 or xs.max() - xs.min() > 130 or ys.max() - ys.min() < 12:
            continue
        rows = np.arange(ys.min(), ys.max() + 1)
        xl = np.array([xs[ys == r].min() if (ys == r).any() else np.nan for r in rows])
        xr = np.array([xs[ys == r].max() + 1 if (ys == r).any() else np.nan for r in rows])
        ok = ~np.isnan(xl)
        low = rows[ok][-12:]
        cx = np.median(((xl + xr) / 2)[ok][-12:]) + x0
        hw = np.maximum.accumulate(np.nan_to_num((xr - xl) / 2))   # monotone, wider downwards
        top_y = rows[np.argmax(hw > 4)] + y0
        bot_y = rows[-1] + y0
        u = cx / (2400 / NX)
        centred = abs((u - np.floor(u)) - 0.5) < 0.25
        cc = (np.floor(u) + 0.5) if centred else np.round(u)
        int_col = int(np.bincount(Lp[y0:y1, x0:x1][comp]).argmax())
        Lsub = Lp[y0:y1, x0:x1]
        ya, yb_ = max(0, ys.min() - 2), ys.max() + 1
        xa, xb_ = max(0, xs.min() - 8), min(stone.shape[1], xs.max() + 8)
        sb = stone[ya:yb_, xa:xb_]
        st_col = int(np.bincount(Lsub[ya:yb_, xa:xb_][sb]).argmax()) if sb.any() else int_col
        jt, jb = int(top_y * NY / 1792), int(bot_y * NY / 1792)
        for j in range(jt, jb + 1):
            yc = (j + 0.5) * 1792 / NY - y0
            r_i = int(np.clip(np.round(yc - rows[0]), 0, len(hw) - 1))
            if yc < rows[0]:
                continue
            h = hw[r_i] / (2400 / NX)
            for i in range(int(cc - h - 2), int(cc + h + 3)):
                if not (0 <= i < NX) or locked[j, i]:
                    continue
                inside = abs((i + 0.5) - cc) <= h
                if inside:
                    R[j, i] = int_col
                elif PL[R[j, i], 0] < 50 and PL[R[j, i], 2] < -15:
                    R[j, i] = st_col
                locked[j, i] = True
        n_arch += 1
    return R, n_arch


def clean_rows(R, box_cells, locked, PL, de=20.0, share=0.5):
    """Deck lines: in each row of the box, the colour covering at least `share` of the row
    replaces cells of a similar tone (dE < de), so a painted line reads as one clean line."""
    x0, y0, x1, y1 = box_cells
    R = R.copy(); n = 0
    for j in range(y0, y1):
        row = R[j, x0:x1]
        vals, cnt = np.unique(row, return_counts=True)
        d = vals[cnt.argmax()]
        if cnt.max() < share * len(row):
            continue
        for i in range(x0, x1):
            if R[j, i] != d and not locked[j, i] and np.linalg.norm(PL[R[j, i]] - PL[d]) < de:
                R[j, i] = d; n += 1
    return R, n


def deck_lines(R, Lp, lab, locked, PL):
    """The bridge deck: source rows where one dark line runs across >= 60 % of the bridge
    become one continuous output row in that line's colour; stone rows of the parapet
    above it take one stone colour where the cell is stone-like."""
    x0, y0, x1, y1 = BRIDGE_BOX
    L = lab[y0:y1, x0:x1, 0]; ch = np.hypot(lab[y0:y1, x0:x1, 1], lab[y0:y1, x0:x1, 2])
    stone = (L > 55) & (ch < 30)
    i0, i1 = int(np.ceil(1088 * NX / 2400)), int(1745 * NX / 2400)
    R = R.copy(); n = 0
    line_rows = [r for r in range(0, 20) if (~stone[r, 8:665]).mean() > 0.6]
    for j in range(int(y0 * NY / 1792), int((y0 + 20) * NY / 1792) + 1):
        ya, yb = int(j * 1792 / NY) - y0, int((j + 1) * 1792 / NY) - y0
        rr = [r for r in line_rows if ya <= r < yb]
        if len(rr) >= 0.5 * (yb - ya) and rr:
            m = np.zeros_like(stone); m[rr, 8:665] = ~stone[rr, 8:665]
            col = int(np.bincount(Lp[y0:y1, x0:x1][m]).argmax())
            for i in range(i0, i1):
                if not locked[j, i]:
                    R[j, i] = col; locked[j, i] = True; n += 1
        else:
            ya = max(ya, 0)
            srow = stone[ya:yb, 8:665]
            if srow.size and srow.mean() > 0.5:
                col = int(np.bincount(Lp[y0 + ya:y0 + yb, x0 + 8:x0 + 665][srow]).argmax())
                for i in range(i0, i1):
                    c = PL[R[j, i]]
                    if not locked[j, i] and c[0] > 55 and np.hypot(c[1], c[2]) < 30:
                        R[j, i] = col; n += 1
    return R, n


def railing_bars(R, V, a, lab, Lp, dp, I, J, PL, n, Sm, locked, x_range=(990, 2400), exclude320=None):
    """Railing balusters as exact 1 px bars at the painting's bar centres. Rows of the
    railing shape that are not rails (the slots) are found; per run of slot rows the
    painted bars (navy runs 3 to 14 px wide in those source rows) give the centres; the
    old bar cells of the slots re-vote without navy, then each bar is one column, top to
    bottom of the slot band, in the rail colour."""
    if Sm is None or not Sm.any():
        return R, 0
    navy = (lab[..., 0] < 20) & (lab[..., 2] < -12)
    cols = np.zeros(NX, bool)
    i0, i1 = int(x_range[0] * NX / 2400), int(x_range[1] * NX / 2400)
    cols[i0:i1] = True
    rowfrac = (Sm[:, cols].sum(1)) / max(1, cols.sum())
    rows_rs = np.flatnonzero(Sm[:, cols].any(1))
    if len(rows_rs) == 0:
        return R, 0
    jr0, jr1 = rows_rs.min(), rows_rs.max()
    rail = rowfrac > 0.35
    thin_cells = Sm & ~ndi.binary_opening(Sm, np.ones((3, 3)))
    vals = R[Sm & rail[:, None]]
    railcol = int(np.bincount(vals).argmax()) if len(vals) else int(np.bincount(R[Sm]).argmax())
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~navy)
    R = R.copy(); nb = 0
    j = jr0
    while j <= jr1:
        if rail[j]:
            j += 1; continue
        k = j
        while k + 1 <= jr1 and not rail[k + 1]:
            k += 1
        ya, yb = int(j * 1792 / NY), int((k + 1) * 1792 / NY)
        prof = navy[ya:yb, x_range[0]:x_range[1]].mean(0)
        m = prof > 0.5
        d = np.diff(np.r_[0, m.astype(int), 0]); st_ = np.flatnonzero(d == 1); en = np.flatnonzero(d == -1)
        bars = [(s0 + e0) / 2 + x_range[0] for s0, e0 in zip(st_, en) if 3 <= e0 - s0 <= 14]
        # clear old thin bar cells in these rows (posts and thick parts stay)
        for jj in range(j, k + 1):
            for ii in range(i0, i1):
                if exclude320 is not None and exclude320[jj, ii]:
                    continue
                if thin_cells[jj, ii] and Vo[jj, ii, :n].sum() > 0:
                    R[jj, ii] = Vo[jj, ii, :n].argmax(); locked[jj, ii] = True
        ym = int((ya + yb) / 2)
        for cx in bars:
            ii = int(I[ym, int(cx)])
            for jj in range(j, k + 1):
                if exclude320 is not None and exclude320[jj, ii]:
                    continue
                sa, sb_ = int(jj * 1792 / NY), int((jj + 1) * 1792 / NY)
                if navy[sa:sb_, int(cx) - 3:int(cx) + 4].mean() >= 0.5:   # the painted bar is here
                    R[jj, ii] = railcol; locked[jj, ii] = True
            nb += 1
        j = k + 1
    return R, nb


def nub_rule(R, C, locked, keep, passes=2, support=0.4):
    """1 px nubs and notches: a pixel whose 4-neighbours agree on another colour on at
    least 3 sides takes that colour, unless the painting paints this cell in its own
    colour (its most common flat colour with >= `support`), or it is locked or kept."""
    R = R.copy(); n = 0
    for _ in range(passes):
        P = np.pad(R, 1, mode='edge')
        nb = np.stack([P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]])
        cand = np.zeros(R.shape, bool); tgt = np.zeros(R.shape, R.dtype)
        for k in range(4):
            same = (nb == nb[k]).sum(0)
            m = (same >= 3) & (nb[k] != R)
            cand |= m; tgt = np.where(m, nb[k], tgt)
        jj, ii = np.nonzero(cand & ~locked & ~keep)
        painted = (C[jj, ii].argmax(1) == R[jj, ii]) & (C[jj, ii, R[jj, ii]] >= support)
        jj, ii = jj[~painted], ii[~painted]
        if len(jj) == 0:
            break
        R[jj, ii] = tgt[jj, ii]; n += len(jj)
    return R, n


def reduce_material(R, PL, mat, names, name, cover=0.92, locked=None):
    """Fewer shades in one material: its colours, by pixel count, are kept until they cover
    `cover` of the material; the rarer ones snap to the nearest kept colour (Lab)."""
    m = (mat == names.index(name))
    if locked is not None:
        m &= ~locked
    vals, cnt = np.unique(R[m], return_counts=True)
    if len(vals) < 4:
        return R, 0
    o = np.argsort(-cnt); cum = np.cumsum(cnt[o]) / cnt.sum()
    keep = vals[o][:np.searchsorted(cum, cover) + 1]
    R = R.copy(); n = 0
    for v in vals:
        if v in keep:
            continue
        t = keep[np.linalg.norm(PL[keep] - PL[v], axis=1).argmin()]
        sel = m & (R == v)
        R[sel] = t; n += int(sel.sum())
    return R, n


def rare_colours(R, PL, ramps, mat, names, max_px=3, vis=None):
    """Colours used by max_px pixels or fewer snap to the nearest well-used colour of the
    pixel's material ramp (or of the whole picture when the ramp has none)."""
    vis = np.ones(R.shape, bool) if vis is None else vis
    vals, cnt = np.unique(R[vis], return_counts=True)
    used = vals[cnt > max_px]
    R = R.copy(); n = 0
    for v in vals[cnt <= max_px]:
        for j, i in np.argwhere((R == v) & vis):
            ramp = [l for l in ramps.get(names[mat[j, i]], []) if l in used]
            pool = np.array(ramp if ramp else used)
            R[j, i] = pool[np.linalg.norm(PL[pool] - PL[v], axis=1).argmin()]; n += 1
    return R, n


def sail_halo(R, PL, V, mat, names, locked):
    """A pale 1 px band between a cream sail (or hull) and darker water or trees, lying
    between the two in colour, is a halo: it takes the better supported of the two."""
    m = np.isin(mat, [names.index(x) for x in ('boats', 'water')])
    R = R.copy(); n = 0
    for j, i in np.argwhere(m & ~locked):
        if not (0 < j < NY - 1 and 0 < i < NX - 1):
            continue
        c = PL[R[j, i]]
        if not (60 < c[0] < 90):
            continue
        for (a_, b_) in (((j, i - 1), (j, i + 1)), ((j, i + 1), (j, i - 1)), ((j - 1, i), (j + 1, i)), ((j + 1, i), (j - 1, i))):
            ca, cb = PL[R[a_]], PL[R[b_]]
            if ca[0] >= 88 and np.hypot(ca[1], ca[2]) < 30 and cb[0] < c[0] - 5 and between(c, ca, cb, tol=0.45):
                R[j, i] = R[a_] if V[j, i, R[a_]] >= V[j, i, R[b_]] else R[b_]; n += 1
                break
    return R, n


OTHER_MASKS = ['/home/claude/wt/rg-logo/out/logo_mask.png', '/home/claude/wt/rg-pepper/out/pepper_mask.png',
               '/home/claude/wt/rg-tag/out/tagline_mask.png']


def visible_mask():
    """Cells of this background that stay visible in the composite: not covered by the
    other tracks' masks (read-only, when present), else not in their boxes."""
    vis = np.ones((NY, NX), bool); found = False
    for p in OTHER_MASKS:
        if os.path.exists(p):
            m = np.array(Image.open(p).convert('L')) > 127
            if m.shape == vis.shape:
                vis &= ~m; found = True
    if not found:
        for (x0, y0, x1, y1) in OTHER_TRACKS:
            vis[y0:y1, x0:x1] = False
    return vis


SPIRE = dict(box=(1660, 732, 1750, 898), maxL=50.0, maxb=-15.0)
BIRD = dict(box=(1860, 760, 2000, 835), maxL=60.0, maxb=-30.0)


def _cls(lab, box, maxL, maxb):
    x0, y0, x1, y1 = box
    return (lab[y0:y1, x0:x1, 0] < maxL) & (lab[y0:y1, x0:x1, 2] < maxb)


def rebuild_spire(R, V, a, lab, Lp, dp, I, J, PL, n, locked):
    """The spire's taper: per output row the painted left and right edges (row averaged),
    made monotone (the spire only widens downwards on each side), rasterised on the uniform
    grid; cells inside keep a spire colour, cells outside re-vote without spire pixels."""
    x0, y0, x1, y1 = SPIRE['box']
    m = _cls(lab, SPIRE['box'], SPIRE['maxL'], SPIRE['maxb'])
    full = np.zeros(lab.shape[:2], bool); full[y0:y1, x0:x1] = m
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~full)
    dark = (PL[:, 0] < SPIRE['maxL']) & (PL[:, 2] < SPIRE['maxb'])
    spcol = int(np.bincount(Lp[full]).argmax())
    j0, j1 = int(np.ceil(y0 * NY / 1792)), int(y1 * NY / 1792)
    lefts, rights = [], []
    for j in range(j0, j1):
        ya, yb = int(j * 1792 / NY) - y0, int((j + 1) * 1792 / NY) - y0
        prof = m[ya:yb].mean(0) > 0.5
        xs = np.flatnonzero(prof)
        lefts.append(xs.min() + x0 if len(xs) else np.nan); rights.append(xs.max() + 1 + x0 if len(xs) else np.nan)
    lefts = np.fmin.accumulate(np.array(lefts)); rights = np.fmax.accumulate(np.array(rights))
    R = R.copy(); nchg = 0
    i0, i1 = int(x0 * NX / 2400) - 1, int(x1 * NX / 2400) + 1
    for k, j in enumerate(range(j0, j1)):
        if np.isnan(lefts[k]):
            continue
        l, r = lefts[k] * NX / 2400, rights[k] * NX / 2400
        axis = int(np.floor((l + r) / 2))
        for i in range(i0, i1 + 1):
            if locked[j, i]:
                continue
            inside = (l <= i + 0.5 <= r) or i == axis
            if inside:
                new = R[j, i] if dark[R[j, i]] else spcol
            elif dark[R[j, i]] and Vo[j, i, :n].sum() > 0:
                new = int(Vo[j, i, :n].argmax())
            else:
                continue
            if new != R[j, i]:
                R[j, i] = new; nchg += 1
            locked[j, i] = True
    return R, nchg


def rebuild_bird(R, a, lab, Lp, dp, I, J, PL, n, locked):
    """The bird as a 1 px pixel-perfect polyline: per output column the painted wing's
    mean height gives a row, neighbouring columns are joined into an 8-connected line,
    L-corners dropped; old bird cells re-vote without the bird's pixels."""
    x0, y0, x1, y1 = BIRD['box']
    m = _cls(lab, BIRD['box'], BIRD['maxL'], BIRD['maxb'])
    m = ndi.binary_opening(m, np.ones((2, 2)))
    if m.sum() < 30:
        return R, 0
    full = np.zeros(lab.shape[:2], bool); full[y0:y1, x0:x1] = m
    col = int(np.bincount(Lp[full]).argmax())
    boxm = np.zeros(lab.shape[:2], bool); boxm[y0:y1, x0:x1] = True
    sky = int(np.bincount(Lp[boxm & ~ndi.binary_dilation(full, iterations=3)]).argmax())
    dark = (PL[:, 0] < BIRD['maxL']) & (PL[:, 2] < BIRD['maxb'])
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~ndi.binary_dilation(full, iterations=2))
    pts = []
    for i in range(int(x0 * NX / 2400), int(x1 * NX / 2400) + 1):
        xa, xb = int(i * 2400 / NX) - x0, int((i + 1) * 2400 / NX) - x0
        sub = m[:, max(0, xa):max(0, xb)]
        if sub.sum() < 4:
            continue
        ys = np.nonzero(sub)[0]
        pts.append((int((ys.mean() + y0) * NY / 1792), i))
    line = np.zeros(R.shape, bool)
    for (ja, ia), (jb, ib) in zip(pts[:-1], pts[1:]):
        line[ja, ia] = True
        if ib - ia == 1:
            step = 1 if jb > ja else -1
            for jj in range(ja + step, jb, step):      # vertical step inside the column pair
                line[jj, ia if abs(jj - ja) <= abs(jj - jb) else ib] = True
    if pts:
        line[pts[-1]] = True
    for _ in range(4):
        nl, lc = qa.lcorners(line)
        if nl == 0:
            break
        lab_l, k = ndi.label(lc)
        for q in range(1, k + 1):
            ys, xs = np.nonzero(lab_l == q); line[ys[0], xs[0]] = False
    R = R.copy(); nchg = 0
    jj0, jj1 = int(y0 * NY / 1792), int(y1 * NY / 1792) + 1
    ii0, ii1 = int(x0 * NX / 2400), int(x1 * NX / 2400) + 1
    for j in range(jj0, jj1):
        for i in range(ii0, ii1):
            if line[j, i]:
                R[j, i] = col; locked[j, i] = True; nchg += 1
            elif (dark[R[j, i]] or PL[R[j, i], 0] < 68) and not locked[j, i]:
                if Vo[j, i, :n].sum() > 0 and PL[Vo[j, i, :n].argmax(), 0] >= 68:
                    R[j, i] = int(Vo[j, i, :n].argmax())
                else:                                   # cell lies wholly in the wing: sky around it
                    nbv = [R[y, x] for y in range(j - 1, j + 2) for x in range(i - 1, i + 2)
                           if 0 <= y < NY and 0 <= x < NX and not dark[R[y, x]]]
                    R[j, i] = np.bincount(nbv).argmax() if nbv else sky
                locked[j, i] = True; nchg += 1
    return R, nchg


# straight vertical bodies whose painted shading runs in vertical stripes:
# (name, cell box x0, y0, x1, y1, max Lab L of the object's colours)
COLUMNS = [('bin', (274, 181, 291, 206), 32.0), ('left_post', (25, 86, 34, 168), 45.0)]


def column_uniform(R, PL, box, maxL, exclude=None):
    """A straight vertical body (the bin's ribs, the lamp post and its highlight): every
    column of the body takes its most common object colour along the body, so a painted
    highlight stripe stays one unbroken column."""
    x0, y0, x1, y1 = box
    R = R.copy(); n = 0
    obj = PL[:, 0] < maxL
    ex = np.zeros(R.shape, bool) if exclude is None else exclude
    for i in range(x0, x1):
        rows = [j for j in range(y0, y1) if not ex[j, i]]
        if len(rows) < 4:
            continue
        col = R[rows, i]
        m = obj[col]
        if m.sum() < 0.6 * len(col):
            continue
        v = np.bincount(col[m]).argmax()
        for j in rows:
            if obj[R[j, i]] and R[j, i] != v:
                R[j, i] = v; n += 1
    return R, n


def small_features(R, a, lab, Lp, I, J, PL, mat, names, locked, material='city', de=12.0, area=(12, 90), reg=None):
    """Windows and lit squares on a facade: painted blobs that differ from the local facade
    colour (median of 15 px) by dE > `de` and are 12 to 90 px large (about one cell) each
    put their own dominant colour on the cell holding their centre, so a row of windows is
    not lost to the facade in the cell vote."""
    from scipy.ndimage import median_filter
    if reg is None:
        reg = (mat == names.index(material))
    regf = reg[J, I]
    ys, xs = np.nonzero(regf)
    if len(ys) == 0:
        return R, 0
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = lab[y0:y1, x0:x1]
    bg = np.stack([median_filter(sub[..., c], size=15) for c in range(3)], -1)
    diff = np.linalg.norm(sub - bg, axis=2) > de
    diff &= regf[y0:y1, x0:x1]
    lc, k = ndi.label(diff)
    if k == 0:
        return R, 0
    sizes = ndi.sum(diff, lc, range(1, k + 1))
    coms = ndi.center_of_mass(diff, lc, range(1, k + 1))
    R = R.copy(); n = 0
    for q, (sz, (cy, cx)) in enumerate(zip(sizes, coms)):
        if not (area[0] <= sz <= area[1]):
            continue
        m = lc == q + 1
        bb = ndi.find_objects(m.astype(int))[0]
        if bb[0].stop - bb[0].start > 14 or bb[1].stop - bb[1].start > 14:
            continue
        col = int(np.bincount(Lp[y0:y1, x0:x1][m]).argmax())
        j, i = int(J[int(cy) + y0, int(cx) + x0]), int(I[int(cy) + y0, int(cx) + x0])
        if not locked[j, i] and reg[j, i] and R[j, i] != col:
            R[j, i] = col; locked[j, i] = True; n += 1
    return R, n


def rebuild_bridge(R, Lp, lab, locked, PL):
    """Repeated structure rule: the bridge is BUILT, not copied. Per output row across the
    span one colour (the painting's dominant label of that row band: parapet, deck line,
    spandrel stone); the painted arch openings give ONE template (median half width per
    row, monotone) and ONE spacing (least squares over the arch centres, whole cells), and
    identical arches are stamped at even spacing in the arch shadow colour. Cells already
    holding a boat, sail or stroke (locked or light sail colours) are left alone."""
    x0, y0, x1, y1 = BRIDGE_BOX
    sub = lab[y0:y1, x0:x1]
    stone = (sub[..., 0] > 55) & (np.hypot(sub[..., 1], sub[..., 2]) < 30)
    band = np.zeros_like(stone); band[1110 - y0:1141 - y0] = True
    lab_c, nc = ndi.label(~stone & band)
    arches = []
    for q in range(1, nc + 1):
        comp = lab_c == q
        ys, xs = np.nonzero(comp)
        if xs.max() - xs.min() < 40 or xs.max() - xs.min() > 130 or ys.max() - ys.min() < 12:
            continue
        arches.append(comp)
    if len(arches) < 2:
        return R, 0
    P = 2400 / NX; Q = 1792 / NY
    i0, i1 = int(np.ceil((x0 + 8) / P)), int((x0 + 665) / P)
    j0, j1 = int(np.ceil(y0 / Q)), int(1142 / Q)
    Lsub = Lp[y0:y1, x0:x1]
    # row colours: stone rows take the stone pixels' dominant label, line rows (mostly not
    # stone outside the arches) the non-stone pixels' dominant label
    rowcol = {}
    for j in range(j0, j1 + 1):
        ya, yb = max(0, int(j * Q) - y0), min(y1 - y0, int((j + 1) * Q) - y0)
        if yb <= ya:
            continue
        rows = np.zeros_like(stone); rows[ya:yb, 8:665] = True
        for comp in arches:
            rows &= ~comp
        st_ = rows & stone
        rowcol[j] = int(np.bincount(Lsub[st_ if st_.sum() >= 0.3 * rows.sum() else rows & ~stone]).argmax())
    # the deck line is thinner than a cell: the row holding its centre takes its colour
    srow = stone[:, 8:665].mean(1)
    lr = [r for r in range(0, 1110 - y0) if srow[r] < 0.1]
    if lr:
        jl = int((np.mean(lr) + y0) / Q)
        m = np.zeros_like(stone); m[lr, 8:665] = True; m &= ~stone
        rowcol[jl] = int(np.bincount(Lsub[m]).argmax())
    # template from the full arches, spacing from the median gap of neighbouring arches
    full = []
    for comp in arches:
        ys, xs = np.nonzero(comp)
        if 60 <= xs.max() - xs.min() <= 110:
            full.append(comp)
    cxs = np.sort([(np.nonzero(c)[1].min() + np.nonzero(c)[1].max() + 1) / 2 + x0 for c in full])
    gaps = np.diff(cxs)
    s_px = np.median(gaps[gaps < 1.5 * np.median(gaps)])
    s_cells = int(np.round(s_px / P))
    kk = np.round((cxs - cxs[0]) / (s_cells * P))
    c0 = int(np.round(np.mean(cxs / P - kk * s_cells)))
    span0, span1 = (x0 + 8) / P, (x0 + 665) / P
    centres = [c for c in range(c0 - 10 * s_cells, c0 + 10 * s_cells + 1, s_cells) if span0 + 3 <= c <= span1 - 3]
    c_h = stone.shape[0]
    width = {}
    run = 0
    for j in range(j0, j1 + 1):
        ya, yb = max(0, int(j * Q) - y0), min(y1 - y0, int((j + 1) * Q) - y0)
        yc = int((j + 0.5) * Q) - y0                       # centre sampling of the row band
        ws = [c[yc].sum() / P for c in full] if 0 <= yc < c_h else [0]
        w = np.median(ws)
        wi = int(2 * np.round(w / 2))
        run = max(run, wi) if wi > 0 else 0
        width[j] = run if wi > 0 else 0
    cxs = centres
    inner = int(np.bincount(np.concatenate([Lsub[c] for c in arches])).argmax())
    R = R.copy(); n = 0
    def free(j, i):
        return 0 <= i < NX and not locked[j, i] and not (PL[R[j, i], 0] > 85)
    for j in range(j0, j1 + 1):
        if j not in rowcol:
            continue
        for i in range(i0, i1 + 1):
            if not free(j, i):
                continue
            new = rowcol[j]
            for c in cxs:
                if width[j] and c - width[j] // 2 <= i < c + width[j] // 2:
                    new = inner
            if new != R[j, i]:
                R[j, i] = new; n += 1
            locked[j, i] = True
    return R, n


RAIL_BOX = (135, 180, 292, 201)   # cells x0, y0, x1, y1


def regular_railing(R, a, lab, Lp, dp, I, J, PL, n, Sm, locked, exclude320, pitch=None):
    """Repeated structure rule for the waterfront railing: the big posts stay where painted;
    every rail becomes ONE straight row (the row of its run with the most painted navy);
    between posts, identical 1 px bars at one constant pitch (the painting's mean bar pitch),
    centred in each gap, from the top rail down; old bar and rail cells take the colour the
    painting has behind the railing (votes without navy)."""
    x0, y0, x1, y1 = RAIL_BOX
    navy = (lab[..., 0] < 20) & (lab[..., 2] < -12)
    box = np.zeros(R.shape, bool); box[y0:y1, x0:x1] = True
    box &= ~exclude320
    thick = ndi.binary_opening(Sm, np.ones((3, 3))) & box if Sm is not None else np.zeros(R.shape, bool)
    # posts: runs of 3+ columns that the painting fills with dark (L < 32) over the railing
    # height (rows y0 to 190), or the structure layer's thick parts
    darkf = lab[..., 0] < 32
    ya_, yb_ = int(y0 * 1792 / NY), int(191 * 1792 / NY)
    colfrac = np.array([darkf[ya_:yb_, int(i * 7.5):int((i + 1) * 7.5)].mean() for i in range(NX)])
    srcpost = colfrac >= 0.8
    postcols = [i for i in range(x0, x1) if thick[y0:y1, i].sum() >= 4 or
                (srcpost[i] and (srcpost[max(0, i - 2):i + 3].sum() >= 3))]
    posts = []
    for i in postcols:
        if posts and i == posts[-1][1] + 1:
            posts[-1][1] = i
        else:
            posts.append([i, i])
    posts = [p for p in posts if p[1] - p[0] >= 2]
    ispost = np.zeros(NX, bool)
    for p0, p1 in posts:
        ispost[p0:p1 + 1] = True
    railcol = int(np.bincount(R[Sm & box & ~thick]).argmax()) if (Sm & box & ~thick).any() else int(np.bincount(R[box]).argmax())
    dark = PL[:, 0] < 22
    # rails: rows where most non-post cells are dark
    cols = [i for i in range(x0, x1) if not ispost[i]]
    fr = np.array([dark[R[j, cols]].mean() for j in range(y0, y1)])
    runs, j = [], 0
    while j < len(fr):
        if fr[j] >= 0.7:
            k = j
            while k + 1 < len(fr) and fr[k + 1] >= 0.7:
                k += 1
            runs.append((j + y0, k + y0)); j = k + 1
        else:
            j += 1
    rail_rows = []
    for ra, rb in runs:
        best = max(range(ra, rb + 1), key=lambda jj: navy[int(jj * 1792 / NY):int((jj + 1) * 1792 / NY), x0 * 15 // 2:x1 * 15 // 2].mean())
        rail_rows.append(best)
    if not rail_rows:
        return R, 0, 0, 0
    # painted bar pitch (game px) in the slot rows below the top rail
    if pitch is None:
        ya, yb = int((rail_rows[0] + 1) * 1792 / NY), int((rail_rows[0] + 3) * 1792 / NY)
        prof = navy[ya:yb, x0 * 15 // 2:x1 * 15 // 2].mean(0) > 0.5
        d = np.diff(np.r_[0, prof.astype(int), 0]); st_ = np.flatnonzero(d == 1); en = np.flatnonzero(d == -1)
        c = np.array([(s0 + e0) / 2 for s0, e0 in zip(st_, en) if 3 <= e0 - s0 <= 14]) / (2400 / NX)
        # bars per game px over the gaps between posts (counts every painted bar, so the
        # wide and narrow painted gaps average out)
        gx = np.array([not ispost[int(v) + x0] for v in c if 0 <= int(v) + x0 < NX])
        free_w = sum(1 for i in range(x0, x1) if not ispost[i] and not exclude320[top_row_dummy, i]) if False else sum(1 for i in range(x0, x1) if not ispost[i])
        nbar = int(gx.sum())
        pitch = int(np.round(free_w / max(nbar, 1))) if nbar else 5
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~navy)
    bg = Vo[..., :n].argmax(2)
    hasbg = Vo[..., :n].sum(2) > 0
    # cells wholly covered by painted navy: the background of the nearest cell that has one
    _, (iy, ix) = ndi.distance_transform_edt(~hasbg, return_indices=True)
    bg = bg[iy, ix]; hasbg = np.ones_like(hasbg)
    R = R.copy(); nchg = 0; nbars = 0
    old = R.copy()
    top = rail_rows[0]
    for j in range(top, y1):
        for i in range(x0, x1):
            if not box[j, i] or ispost[i] or locked[j, i]:
                continue
            new = railcol if j in rail_rows else (bg[j, i] if (dark[R[j, i]] and hasbg[j, i]) else R[j, i])
            R[j, i] = new
    # the row right above the top rail (a doubled rail) clears too
    for i in range(x0, x1):
        j = top - 1
        if j >= y0 and box[j, i] and not ispost[i] and not locked[j, i] and dark[R[j, i]]:
            R[j, i] = bg[j, i]
    for j in range(y0, top):
        for i in range(x0, x1):
            if box[j, i] and not ispost[i] and not locked[j, i] and dark[R[j, i]] and hasbg[j, i] and fr[j - y0] >= 0.7:
                R[j, i] = bg[j, i]
    # bars between posts (and from the last post to the box edge)
    edges = [x0 - 1] + [v for p in posts for v in p] + [x1]
    gaps = [(edges[k] + 1, edges[k + 1] - 1) for k in range(0, len(edges) - 1, 2)]
    for g0, g1 in gaps:
        w = g1 - g0 + 1
        if w < pitch:
            continue
        nb_ = (w - 1) // pitch
        if nb_ < 1:
            continue
        span = (nb_ - 1) * pitch
        first = g0 + (w - 1 - span) // 2
        for b in range(nb_):
            i = first + b * pitch
            for j in range(top, y1):
                if box[j, i] and not locked[j, i]:
                    R[j, i] = railcol
            nbars += 1
    # slots: between two bars, dark leftovers take the slot's most common light colour
    barcol = np.zeros(NX, bool)
    for g0, g1 in gaps:
        w = g1 - g0 + 1
        nb_ = (w - 1) // pitch if w >= pitch else 0
        if nb_ >= 1:
            first = g0 + (w - 1 - (nb_ - 1) * pitch) // 2
            barcol[first:first + nb_ * pitch:pitch] = True
    for j in range(top + 1, y1):
        if j in rail_rows:
            continue
        i = x0
        while i < x1:
            if ispost[i] or barcol[i] or not box[j, i]:
                i += 1; continue
            k = i
            while k + 1 < x1 and not (ispost[k + 1] or barcol[k + 1] or not box[j, k + 1]):
                k += 1
            seg = R[j, i:k + 1]
            dk = PL[:, 0] < 38
            light = seg[~dk[seg]]
            if not len(light):                       # whole slot run dark: borrow from the slot rows around
                nbr = np.concatenate([R[jj, i:k + 1] for jj in (j - 1, j + 1, j - 2) if top < jj < y1 and jj not in rail_rows])
                light = nbr[~dk[nbr]] if len(nbr) else nbr
            if len(light):
                maj = np.bincount(light).argmax()
                for ii in range(i, k + 1):
                    if dk[R[j, ii]] and not locked[j, ii]:
                        R[j, ii] = maj
            i = k + 1
    for j in range(y0, y1):
        for i in range(x0, x1):
            if box[j, i]:
                locked[j, i] = True
    nchg = int((R != old).sum())
    return R, nchg, nbars, pitch


WATER_BOX = (135, 145, 320, 196)


def regular_water(R, PL, mat, names, locked, hard, vis, nblue=4):
    """Water as flat bands of a few blues with clean 1 px ripple dashes: the water cells
    keep the `nblue` most used blues (every other blue snaps to the nearest of them) and at
    most two highlight colours; highlight runs are made 1 px tall (only the top cell of a
    vertical run stays) and at least 2 px long; single cells of a blue between two cells
    of another colour in a row take that colour (no specks, dashes run horizontally)."""
    x0, y0, x1, y1 = WATER_BOX
    m = np.zeros(R.shape, bool); m[y0:y1, x0:x1] = True
    m &= (mat == names.index('water')) & ~locked & ~hard & vis
    if m.sum() < 50:
        return R, 0
    R = R.copy(); old = R.copy()
    cols, cnt = np.unique(R[m], return_counts=True)
    light = PL[cols, 0] > 75
    # blues: greedy choice of the `nblue` colours that best represent all water blues
    # (each step adds the colour that most lowers the pixel-weighted Lab error)
    bc, bn = cols[~light], cnt[~light].astype(float)
    D = np.linalg.norm(PL[bc][:, None] - PL[bc][None], axis=2)
    chosen = [int(np.argmax(bn))]
    for _ in range(nblue - 1):
        cur = D[:, chosen].min(1)
        gain = [(bn * np.maximum(cur - D[:, c], 0)).sum() if c not in chosen else -1 for c in range(len(bc))]
        chosen.append(int(np.argmax(gain)))
    blues = bc[chosen]
    hls = cols[light][np.argsort(-cnt[light])][:3]
    for j, i in np.argwhere(m):
        c = R[j, i]
        pool = hls if (PL[c, 0] > 80 and len(hls)) else blues
        R[j, i] = pool[np.linalg.norm(PL[pool] - PL[c], axis=1).argmin()]
    ishl = np.isin(R, hls) & m
    # 1 px tall highlights: cells under another highlight cell become the row's base blue
    for j, i in np.argwhere(ishl):
        if j - 1 >= 0 and ishl[j - 1, i]:
            row = R[j, max(x0, i - 4):i + 5]
            b = row[np.isin(row, blues)]
            R[j, i] = np.bincount(b).argmax() if len(b) else blues[0]
    for _ in range(2):
        for j, i in np.argwhere(m):
            if 0 < i < NX - 1 and R[j, i - 1] == R[j, i + 1] and R[j, i] != R[j, i - 1] and m[j, i - 1] and m[j, i + 1]:
                R[j, i] = R[j, i - 1]
    return R, int((R != old).sum())


# facades rebuilt on a window grid: (name, cell box x0, y0, x1, y1, facade class)
FACADES = [('grey_block', (281, 116, 302, 142), 'bluegrey'), ('tower', (216, 116, 231, 146), 'brick')]


def _facade_class(lab, cls):
    L, A, Bb = lab[..., 0], lab[..., 1], lab[..., 2]
    if cls == 'brick':
        return (A > 12) & (Bb > 18) & (L > 35)
    return (L > 35) & (L < 78) & (Bb < 5) & (A < 12)


def build_facade(R, Lp, lab, PL, box, cls, locked):
    """Repeated structure rule for a facade: flat faces (one colour each, split where the
    painted face colour changes) and identical windows on one even grid per face (pitch and
    phase from the painting's window blobs), window colour the painting's most common."""
    from scipy.ndimage import median_filter
    x0, y0, x1, y1 = box
    P, Q = 2400 / NX, 1792 / NY
    sx0, sy0, sx1, sy1 = int(x0 * P), int(y0 * Q), int(x1 * P), int(y1 * Q)
    sub = lab[sy0:sy1, sx0:sx1]; Ls = Lp[sy0:sy1, sx0:sx1]
    fac = _facade_class(sub, cls)
    bgc = np.stack([median_filter(sub[..., c], size=15) for c in range(3)], -1)
    inside = ndi.binary_fill_holes(ndi.binary_closing(fac, iterations=3))
    win = (np.linalg.norm(sub - bgc, axis=2) > 12) & (bgc[..., 0] - sub[..., 0] > 6) & inside   # darker blobs
    bmask = ndi.binary_fill_holes(ndi.binary_closing(fac | win, iterations=2))
    fac = fac & ~win
    # cell level silhouette (uniform cells)
    sil = np.zeros(R.shape, bool); wc = []
    for j in range(y0, y1):
        for i in range(x0, x1):
            ya, yb = int(j * Q) - sy0, int((j + 1) * Q) - sy0; xa, xb = int(i * P) - sx0, int((i + 1) * P) - sx0
            sil[j, i] = bmask[ya:yb, xa:xb].mean() >= 0.5
    if sil.sum() < 20:
        return R, 0
    # faces: per column median facade colour, split at the largest jump
    colmed = []
    for i in range(x0, x1):
        xa, xb = int(i * P) - sx0, int((i + 1) * P) - sx0
        m = fac[:, xa:xb]
        colmed.append(np.median(sub[:, xa:xb][m], 0) if m.sum() > 10 else np.full(3, np.nan))
    colmed = np.array(colmed)
    ok = ~np.isnan(colmed[:, 0])
    jumps = [np.linalg.norm(colmed[k + 1] - colmed[k]) if ok[k] and ok[k + 1] else 0 for k in range(len(colmed) - 1)]
    split = x0 + int(np.argmax(jumps)) + 1 if max(jumps) > 8 else x1
    faces = [(x0, split), (split, x1)] if split < x1 else [(x0, x1)]
    lc, k = ndi.label(win)
    R = R.copy(); old = R.copy()
    for fx0, fx1 in faces:
        xa, xb = int(fx0 * P) - sx0, int(fx1 * P) - sx0
        fm = fac[:, xa:xb]
        if fm.sum() < 20:
            continue
        fcol = int(np.bincount(Ls[:, xa:xb][fm]).argmax())
        wm = win[:, xa:xb]
        wcol = int(np.bincount(Ls[:, xa:xb][wm]).argmax()) if wm.sum() else None
        # window centres in cell coordinates
        cents = []
        for q in range(1, k + 1):
            m = lc == q
            ys, xs = np.nonzero(m)
            if not (6 <= len(ys) <= 120) or not (xa <= xs.mean() < xb):
                continue
            cents.append(((ys.mean() + sy0) / Q, (xs.mean() + sx0) / P))
        for j in range(y0, y1):
            for i in range(fx0, fx1):
                if sil[j, i] and not locked[j, i]:
                    R[j, i] = fcol
        if wcol is None or len(cents) < 2:
            continue
        cy = np.array([c[0] for c in cents]); cx = np.array([c[1] for c in cents])
        def grid(v):
            u = np.unique(np.floor(v).astype(int))
            d = np.diff(u); d = d[d >= 2]
            p = int(np.median(d)) if len(d) else 2
            ph = np.bincount(np.floor(v).astype(int) % p).argmax()
            return p, ph, int(np.floor(v.min())), int(np.floor(v.max()))
        py, phy, ymin, ymax = grid(cy); px, phx, xmin, xmax = grid(cx)
        for j in range(ymin, ymax + 1):
            if j % py != phy:
                continue
            for i in range(max(xmin, fx0 + 1), min(xmax, fx1 - 2) + 1):
                if i % px != phx:
                    continue
                if sil[j, i] and not locked[j, i] and all(sil[jj, ii] for jj, ii in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1))):
                    R[j, i] = wcol
    for j in range(y0, y1):
        for i in range(x0, x1):
            if sil[j, i]:
                locked[j, i] = True
    return R, int((R != old).sum())


# sails rebuilt as clean shapes: (name, source box)
SAILS = [('sail_mast_boat', (1745, 1020, 1900, 1215)), ('sail_jib_boat', (1870, 1000, 2010, 1165)),
         ('sail_small', (1255, 1090, 1335, 1200))]


def rebuild_sail(R, a, lab, Lp, dp, I, J, PL, n, box, locked):
    """A sail as one smooth shape: the painting's sail pixels (light, low chroma) in the box
    are smoothed and rasterised at coverage 0.5, the staircase regularised; cells inside keep
    their light sail colour (so the two-tone shading stays) or take the sail's main colour,
    cells outside that hold a light sail colour (halo, bites) re-vote without sail pixels."""
    import shapes
    x0, y0, x1, y1 = box
    sail = (lab[..., 0] > 78) & (np.hypot(lab[..., 1], lab[..., 2]) < 32)
    full = np.zeros(sail.shape, bool); full[y0:y1, x0:x1] = sail[y0:y1, x0:x1]
    full = ndi.binary_opening(full, iterations=1)
    if full.sum() < 60:
        return R, 0
    lc_, k_ = ndi.label(full)
    sz = ndi.sum(full, lc_, range(1, k_ + 1))
    full = np.isin(lc_, np.flatnonzero(sz >= 0.25 * sz.max()) + 1)
    # the mast splits main sail and jib: close across it so both read as one sail plan
    full = ndi.binary_closing(full, np.ones((1, 13))) & ndi.binary_dilation(full, np.ones((1, 13)))
    main = int(np.bincount(Lp[full]).argmax())
    Sm, Sf = shapes.raster_shape(full, I, J, s=3.0, pre=1.5, min_area=30)
    Sm, _ = regularize(Sm, shapes.coverage(Sf, I, J), passes=4, band=(0.15, 0.85))
    light = (PL[:, 0] > 78) & (np.hypot(PL[:, 1], PL[:, 2]) < 32)
    if not light[main]:
        main = int(np.bincount(Lp[full & sail]).argmax())
    Vo, Co = masked_votes(a, I, J, Lp, dp, n, ~ndi.binary_dilation(full, iterations=2))
    R = R.copy(); old = R.copy()
    j0, j1 = int(y0 * NY / 1792), int(y1 * NY / 1792) + 1
    i0, i1 = int(x0 * NX / 2400), int(x1 * NX / 2400) + 1
    for j in range(j0, j1):
        for i in range(i0, i1):
            if locked[j, i]:
                continue
            if Sm[j, i]:
                if not light[R[j, i]]:
                    R[j, i] = main
                locked[j, i] = True
            elif light[R[j, i]] or (PL[R[j, i], 0] > 70 and PL[R[j, i], 2] < -5 and Vo[j, i, :n].sum() > 0):
                v = Vo[j, i, :n]
                if v.sum() > 0:
                    R[j, i] = int(v.argmax())
                else:
                    nb = [R[y, x] for y in range(j - 1, j + 2) for x in range(i - 1, i + 2)
                          if 0 <= y < NY and 0 <= x < NX and not Sm[y, x] and not light[R[y, x]]]
                    if nb:
                        R[j, i] = np.bincount(nb).argmax()
    # a dark mast through the sail (thinner than a cell): the darkest thin column in the
    # sail rows becomes a 1 px line in its painted colour where the painting has it
    dark = lab[..., 0] < 45
    best = None
    for i in range(i0, i1):
        xa, xb = int(i * 2400 / NX), int((i + 1) * 2400 / NX)
        rows = [j for j in range(j0, j1) if Sm[j, i] or (i > 0 and Sm[j, i - 1] and i + 1 < NX and Sm[j, i + 1])]
        if len(rows) < 4:
            continue
        f = np.mean([dark[int(j * 1792 / NY):int((j + 1) * 1792 / NY), xa:xb].any(1).mean() for j in rows])
        if best is None or f > best[0]:
            best = (f, i, rows)
    if best is not None and best[0] >= 0.4:
        f, i, rows = best
        xa, xb = int(i * 2400 / NX), int((i + 1) * 2400 / NX)
        for j in range(min(rows), max(rows) + 1):       # only across the sail itself
            ya, yb = int(j * 1792 / NY), int((j + 1) * 1792 / NY)
            seg = dark[ya:yb, xa:xb]
            if PL[R[j, i], 0] < 45:
                continue                                  # already a dark mast cell (stroke layer)
            if seg.any(1).mean() >= 0.5:      # the mast wins over a pale stroke here
                R[j, i] = int(np.bincount(Lp[ya:yb, xa:xb][seg]).argmax()); locked[j, i] = True
    return R, int((R != old).sum())


REGULARISED = [(135, 180, 292, 201), (145, 145, 235, 154), (135, 145, 320, 196), (281, 116, 302, 142), (216, 116, 231, 146)]
FOLIAGE_BOXES = [(240, 125, 320, 170), (0, 85, 30, 165)]


def foliage_clumps(R, PL, mat, names, locked, hard, vis, box, ntones=3, passes=3):
    """Foliage as leaf clumps: the leaf cells in the box keep the `ntones` greens (greedy
    best representatives, by pixel count) and every other leaf colour snaps to the nearest;
    then cells with fewer than 2 same-coloured 8-neighbours take the majority of their
    4-neighbours (clean cluster shapes, no lone specks)."""
    x0, y0, x1, y1 = box
    m = np.zeros(R.shape, bool); m[y0:y1, x0:x1] = True
    m &= np.isin(mat, [names.index(x) for x in ('leaves', 'trunk', 'rest', 'other')]) & ~locked & ~hard & vis
    green = (PL[:, 1] < -5) & (PL[:, 0] > 25)
    m &= green[R]
    if m.sum() < 30:
        return R, 0
    R = R.copy(); old = R.copy()
    cols, cnt = np.unique(R[m], return_counts=True)
    cnt = cnt.astype(float)
    D = np.linalg.norm(PL[cols][:, None] - PL[cols][None], axis=2)
    chosen = [int(np.argmax(cnt))]
    for _ in range(min(ntones, len(cols)) - 1):
        cur = D[:, chosen].min(1)
        gain = [(cnt * np.maximum(cur - D[:, c], 0)).sum() if c not in chosen else -1 for c in range(len(cols))]
        chosen.append(int(np.argmax(gain)))
    tones = cols[chosen]
    for j, i in np.argwhere(m):
        R[j, i] = tones[np.linalg.norm(PL[tones] - PL[R[j, i]], axis=1).argmin()]
    for _ in range(passes):
        P = np.pad(R, 1, mode='edge')
        same = sum((P[1 + dy:NY + 1 + dy, 1 + dx:NX + 1 + dx] == R).astype(int)
                   for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
        for j, i in np.argwhere(m & (same < 2)):
            nb = [R[y, x] for y, x in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1)) if 0 <= y < NY and 0 <= x < NX]
            v, c = np.unique(nb, return_counts=True)
            R[j, i] = v[c.argmax()]
    return R, int((R != old).sum())


def optimise(R, V, C, PL, pal, ref, locked, sweeps=4, kappa=120.0, sigma=30.0, mu=1e4, cmin=0.15, tie=0.5, potts=20.0, speck_ok=None):
    """Coordinate descent over the cells. Each cell may take a colour that occurs in it
    (coverage >= cmin, or the vote winner) or, to resolve a mixel, a 4-neighbour colour.
    Objective: form error (5x5 box blurred luma vs the painting's cell means, squared)
    + kappa * vote deficit + sigma per isolated speck + mu per mixel
    + potts per differing 4-neighbour (a boundary length term: no new notches)."""
    from scipy.ndimage import uniform_filter
    R = R.copy()
    lum = pal.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    Vn = V / np.maximum(V.sum(2, keepdims=True), 1e-6)
    win0 = Vn.argmax(2)
    E = uniform_filter(lum[R], 5, mode='nearest') - uniform_filter(ref, 5, mode='nearest')
    changed_total = 0
    for sw in range(sweeps):
        changed = 0
        mm = mixel_mask(R, PL)
        for j in range(NY):
            for i in range(NX):
                if locked[j, i]:
                    continue
                # only near ties may change: colours that occur flat in the cell and have at
                # least `tie` of the winner's vote (a clearly decided cell keeps its colour)
                vw = Vn[j, i, win0[j, i]]
                cand = set(np.flatnonzero((C[j, i] >= cmin) & (Vn[j, i] >= tie * vw)).tolist()) | {int(win0[j, i]), int(R[j, i])}
                # never trade the cell's two main painted colours for a colour lying between
                # them (that would be a blend in effect, e.g. grey windows on a beige wall)
                top2 = np.argsort(C[j, i])[-2:]
                if C[j, i, top2[0]] >= cmin:
                    ca, cb = PL[top2[0]], PL[top2[1]]
                    cand = {l for l in cand if l in (int(top2[0]), int(top2[1]), int(R[j, i]))
                            or not between(PL[l], ca, cb, tol=0.3)}
                near_mix = mm[j, i]   # neighbour colours only to resolve a mixel AT this cell
                if near_mix:
                    for (dj, di) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                        jj, ii = j + dj, i + di
                        if 0 <= jj < NY and 0 <= ii < NX:
                            cand.add(int(R[jj, ii]))
                if len(cand) == 1:
                    continue
                y0, y1 = max(0, j - 2), min(NY, j + 3); x0, x1 = max(0, i - 2), min(NX, i + 3)
                Ew = E[y0:y1, x0:x1]; sE = Ew.sum(); nW = Ew.size
                cur = int(R[j, i])
                pos = [(j, i), (j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1)]
                pos8 = [(j + dj, i + di) for dj in (-1, 0, 1) for di in (-1, 0, 1)]
                best, bestc = cur, None
                for l in cand:
                    d = (lum[l] - lum[cur]) / 25.0
                    f = 2 * d * sE + nW * d * d
                    R[j, i] = l
                    nm = sum(is_mixel(R, PL, y, x) for y, x in pos)
                    ns = sum((sigma if speck_ok is None or speck_ok[y, x] or C[y, x, R[y, x]] >= 0.5
                              or (C[y, x].argmax() == R[y, x] and C[y, x, R[y, x]] >= 0.25) else 1e4)
                             * is_speck(R, y, x) for y, x in pos8 if 0 <= y < NY and 0 <= x < NX) / sigma
                    nd = sum(1 for (y, x) in pos[1:] if 0 <= y < NY and 0 <= x < NX and R[y, x] != l)
                    cost = f + kappa * (Vn[j, i, win0[j, i]] - Vn[j, i, l]) + sigma * ns + mu * nm + potts * nd
                    if Vn[j, i, l] == 0:
                        cost += kappa
                    if bestc is None or cost < bestc - 1e-9:
                        best, bestc = l, cost
                R[j, i] = best
                if best != cur:
                    d = (lum[best] - lum[cur]) / 25.0
                    E[y0:y1, x0:x1] += d
                    changed += 1
        changed_total += changed
        if changed == 0:
            break
    return R, changed_total


def cell_ref(a, I, J):
    lumsrc = a.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    cell = (J.astype(np.int64) * NX + I).ravel()
    cnt = np.bincount(cell, minlength=NX * NY)
    return (np.bincount(cell, weights=lumsrc.ravel(), minlength=NX * NY) / np.maximum(cnt, 1)).reshape(NY, NX)


def build(a=None, XB=None, YB=None, I=None, J=None, pal=None, ramps=None, steps=('pepper', 'structures', 'strokes', 'checker', 'opt', 'regular', 'bridge', 'shapes3', 'sails', 'clean', 'specks', 'foliage', 'water', 'unify', 'mixel')):
    if a is None:
        a = load_src()
    if XB is None:
        XB, YB, I, J = G.run()
    if pal is None:
        pal, ramps = LB.run()
    PL = srgb_to_lab(pal.astype(np.float32))
    lab = srgb_to_lab(a)
    Lp, dp = nearest_palette(lab, PL)
    n = len(pal)
    V, C = votes(a, I, J, Lp, dp, n)
    R = V.argmax(2).astype(np.int16)
    info = {'cells_thin': 0, 'cells_checker': 0}
    hard = np.zeros((NY, NX), bool)     # rebuilt repeated structures: later repairs keep off
    locked = np.zeros(R.shape, bool)
    if 'pepper' in steps:
        Sm, ring, ocol, (Vin, Cin), (Vout, Cout), pfull = pepper_outline(a, lab, Lp, dp, I, J, PL, n)
        # cells whose box straddles the silhouette re-vote on their own side only
        edge = np.zeros(R.shape, bool)
        bnd = pfull ^ ndi.binary_erosion(pfull, iterations=10)
        edge[J[bnd], I[bnd]] = True
        bnd2 = ndi.binary_dilation(pfull, iterations=10) & ~pfull
        edge[J[bnd2], I[bnd2]] = True
        inside = Sm & ~ring & edge & (Vin.sum(2) > 0)
        outside = ~Sm & edge & (Vout.sum(2) > 0)
        R[inside] = Vin.argmax(2)[inside]; R[outside] = Vout.argmax(2)[outside]
        V = np.where(inside[..., None], Vin, np.where(outside[..., None], Vout, V))
        C = np.where(inside[..., None], Cin, np.where(outside[..., None], Cout, C))
        # shape cells dropped from the outline by the pixel-perfect rule take the interior vote
        dropped = Sm & ~ring & edge & (Vin.sum(2) > 0)
        R[dropped] = Vin.argmax(2)[dropped]
        R[ring] = ocol; locked |= ring
        info['pepper_outline_cells'] = int(ring.sum())
        info['_masks'] = {'pepper_outline': ring.copy(), 'pepper_shape': Sm.copy(), 'pepper_full': pfull}
    if 'structures' in steps:
        ex320 = np.zeros(R.shape, bool)
        for (x0, y0, x1, y1) in OTHER_TRACKS[1:2]:
            ex320[y0:y1, x0:x1] = True
        exf = info.get('_masks', {}).get('pepper_full', np.zeros(Lp.shape, bool))
        nst = 0
        locked_pre = locked.copy()
        for sname, mname, sbox, maxL, maxb in STRUCTURES:
            R, V, ch, Sm_s = structure_layer(R, V, a, lab, Lp, dp, I, J, PL, n, mname, sbox, maxL, maxb, exf, ex320)
            locked |= ch; nst += int(ch.sum())
            info.setdefault('_masks', {})['struct_' + sname] = Sm_s
        info['cells_structures'] = nst
        lk = locked_pre.copy()
        R, nrl, nbars, rpitch = regular_railing(R, a, lab, Lp, dp, I, J, PL, n, info['_masks'].get('struct_railing'), lk, ex320)
        locked |= lk
        rb = np.zeros_like(hard); x0r, y0r, x1r, y1r = RAIL_BOX; rb[y0r:y1r, x0r:x1r] = True
        hard |= rb & ~ex320 & (PL[R, 0] < 22)          # bars, rails, posts; slot backgrounds stay repairable
        info['railing_bars'] = nbars; info['railing_pitch'] = rpitch
    if 'strokes' in steps:
        st = strokes(lab, Lp, XB, YB, I, J)
        smask = np.zeros(Lp.shape, bool)
        for cells, col, mask, axis, ctr in st:
            smask |= mask
        # the cells either side of a stroke cell re-vote without the stroke's own pixels
        # (its anti-aliased halo would otherwise smear the stroke colour sideways)
        halo = ndi.binary_dilation(smask, iterations=1)
        Vx, Cx = votes(a, I, J, np.where(halo, n, Lp), np.where(halo, 99, dp), n + 1)
        scells = set()
        side = set()
        for cells, col, mask, axis, ctr in st:
            for (j, i) in cells:
                scells.add((j, i))
                for dj, di in (((0, -1), (0, 1)) if axis == 1 else ((-1, 0), (1, 0))):
                    side.add((j + dj, i + di))
        kept = Vx[..., :n].sum(2) / np.maximum(Vx.sum(2), 1e-6)
        scol = {}
        for cells, col, mask, axis, ctr in st:
            for c in cells:
                scol[c] = col
        for (j, i) in side - scells:
            if 0 <= j < NY and 0 <= i < NX and kept[j, i] >= 0.3:
                v = Vx[j, i, :n].copy()
                # a side cell never repeats the stroke colour (no spurs beside a mast)
                for (dj, di) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    c = scol.get((j + dj, i + di))
                    if c is not None:
                        v[np.linalg.norm(PL - PL[c], axis=1) < 15] = 0
                if v.sum() > 0:
                    R[j, i] = v.argmax(); V[j, i] = v; C[j, i] = Cx[j, i, :n]
                    locked[j, i] = True
        # join pieces of one stroke split by a short gap (aligned ends, up to 3 cells apart)
        pieces = []
        for cells, col, mask, axis, ctr in st:
            cs = sorted(cells, key=lambda c: c[0] if axis == 1 else c[1])
            pieces.append([cs, col, axis])
        for p in pieces:
            for q in pieces:
                if p is q or p[2] != q[2]:
                    continue
                ax = p[2]; ka = 0 if ax == 1 else 1; kb = 1 - ka
                e, s0 = p[0][-1], q[0][0]
                gap = s0[ka] - e[ka]
                if 2 <= gap <= 4 and abs(s0[kb] - e[kb]) <= 1:
                    fill = []
                    for t in range(1, gap):
                        c = [0, 0]; c[ka] = e[ka] + t; c[kb] = e[kb] if t < gap / 2 else s0[kb]
                        fill.append(tuple(c))
                    longer = p if len(p[0]) >= len(q[0]) else q
                    p.append(('fill', fill, longer[1]))
        # a weaker stroke running right beside a longer one (a highlight strip next to a
        # mast) would double the line: drop it
        pieces.sort(key=lambda p: -len(p[0]))
        taken = set(); kept_p = []
        for p in pieces:
            nbr = sum(1 for (j, i) in p[0] if any((j + dj, i + di) in taken for dj, di in ((0, -1), (0, 1), (-1, 0), (1, 0), (0, 0))))
            if nbr >= 0.5 * len(p[0]):
                continue
            kept_p.append(p); taken |= set(p[0])
        pieces = kept_p
        # strokes inside dark structures (post highlights on the railing) are left to the
        # structure layer: a 1 px highlight would run past the post
        if 'structures' in steps:
            rreg = ndi.binary_dilation(load_mask('railing'), iterations=1)
            rreg[168:205, 110:320] = True
            pieces = [p for p in pieces if np.mean([rreg[c] if 0 <= c[0] < NY and 0 <= c[1] < NX else False for c in p[0]]) < 0.5]
        # drop stray single cells of a stroke (no 8-neighbour within the same stroke)
        for p in pieces:
            cs = set(p[0])
            p[0] = [c for c in p[0] if any((c[0] + dj, c[1] + di) in cs
                                           for dj in (-1, 0, 1) for di in (-1, 0, 1) if dj or di)]
        ncell = 0
        smk = np.zeros(R.shape, bool)
        for p in pieces:
            for (j, i) in p[0]:
                if 0 <= j < NY and 0 <= i < NX:
                    R[j, i] = p[1]; locked[j, i] = True; smk[j, i] = True; ncell += 1
            for extra in p[3:]:
                for (j, i) in extra[1]:
                    if 0 <= j < NY and 0 <= i < NX and not smk[j, i]:
                        R[j, i] = extra[2]; locked[j, i] = True; smk[j, i] = True; ncell += 1
        # pixel-perfect: drop one pixel of every L-corner double on the strokes
        for _ in range(6):
            n_l, lc = qa.lcorners(smk)
            if n_l == 0:
                break
            lab_l, nl = ndi.label(lc)
            for q in range(1, nl + 1):
                ys, xs = np.nonzero(lab_l == q)
                j, i = ys[-1], xs[-1]
                smk[j, i] = False; locked[j, i] = False
                R[j, i] = Vx[j, i, :n].argmax() if Vx[j, i, :n].sum() > 0 else V[j, i].argmax()
                ncell -= 1
        info['strokes'] = len(st); info['cells_stroke'] = ncell
        info.setdefault('_masks', {})['strokes'] = smk.copy()
        info['_strokes'] = st
    if 'thin' in steps:
        th = thin_features(Lp, PL, XB, YB, R, C)
        for (j, i), l in th.items():
            R[j, i] = l; locked[j, i] = True
        info['cells_thin'] = len(th)
    if 'checker' in steps:
        coat = load_mask('coat')
        cr = [l for l in ramps['coat'] if PL[l, 0] < 45]
        R, ch = coat_checker(R, V, cr, coat, PL)
        # the logo's yellow to orange gradient uses the same block checker
        mat, names = LB.material_map()
        logo = mat == names.index('logo')
        chroma = np.hypot(PL[:, 1], PL[:, 2])
        lr = [l for l in ramps.get('logo', []) if PL[l, 0] > 50 and chroma[l] > 50]
        R, ch2 = coat_checker(R, V, lr, logo, PL, dmax=50.0)
        locked |= ch | ch2
        checker_cells = ch | ch2
        info['cells_checker'] = int(ch.sum()); info['cells_checker_logo'] = int(ch2.sum())
    if 'opt' in steps:
        ref = cell_ref(a, I, J)
        R, nch = optimise(R, V, C, PL, pal, ref, locked)
    if 'bridge' in steps:
        lb = locked.copy()
        R, nr = rebuild_bridge(R, Lp, lab, locked, PL)
        hard |= locked & ~lb
        info['bridge_cells'] = nr
    if 'shapes3' in steps:
        R, nsp = rebuild_spire(R, V, a, lab, Lp, dp, I, J, PL, n, locked)
        lb0 = locked.copy()
        R, nbd = rebuild_bird(R, a, lab, Lp, dp, I, J, PL, n, locked)
        bx0, by0, bx1, by1 = BIRD['box']
        birdbox = np.zeros(R.shape, bool)
        birdbox[int(by0 * NY / 1792):int(by1 * NY / 1792) + 1, int(bx0 * NX / 2400):int(bx1 * NX / 2400) + 1] = True
        bird_line = birdbox & (PL[R, 0] < 60)
        hard |= birdbox
        info['spire_cells'] = nsp; info['bird_cells'] = nbd
    if 'sails' in steps:
        nsl = 0
        mk = info.get('_masks', {})
        slk = mk.get('strokes', np.zeros(R.shape, bool)) | mk.get('pepper_outline', np.zeros(R.shape, bool)) | hard
        for sname, sbox in SAILS:
            slk2 = slk.copy()
            R, ns1 = rebuild_sail(R, a, lab, Lp, dp, I, J, PL, n, sbox, slk2)
            locked |= slk2
            nsl += ns1
        info['sail_cells'] = nsl
    if 'clean' in steps:
        mat, names = LB.material_map()
        chk = checker_cells if 'checker' in steps else np.zeros(R.shape, bool)
        R, nh = sail_halo(R, PL, V, mat, names, locked)
        nubmat = np.isin(mat, [names.index(x) for x in ('sky', 'clouds', 'city', 'water', 'pavement', 'boats', 'stone', 'leaves', 'rest')])
        oth = np.zeros(R.shape, bool)
        for (x0, y0, x1, y1) in OTHER_TRACKS:
            oth[y0:y1, x0:x1] = True
        R, nn = nub_rule(R, C, locked, chk | ~nubmat | oth, passes=1, support=0.3)
        R, nw = reduce_material(R, PL, mat, names, 'water', locked=locked)
        for mname in ('leaves', 'city'):
            R, nw2 = reduce_material(R, PL, mat, names, mname, cover=0.93, locked=locked)
            nw += nw2
        nc = 0
        for cname, cbox, cmaxL in COLUMNS:
            pex = ndi.binary_dilation(info.get('_masks', {}).get('pepper_shape', np.zeros(R.shape, bool)))
            R, nc1 = column_uniform(R, PL, cbox, cmaxL, exclude=pex)
            nc += nc1
        info['column_cells'] = nc
        nfac = 0
        for fname, fbox, fcls in FACADES:
            R, nf1 = build_facade(R, Lp, lab, PL, fbox, fcls, locked)
            nfac += nf1
        info['facade_cells'] = nfac
        R, nsf = small_features(R, a, lab, Lp, I, J, PL, mat, names, locked)

        R, nsf3 = small_features(R, a, lab, Lp, I, J, PL, mat, names, locked, material='boats', de=20.0, area=(10, 60))
        nsf += nsf3
        info['window_cells'] = nsf
        info['halo_cells'] = nh; info['nub_cells'] = nn; info['water_reduced'] = nw
    if 'specks' in steps:
        mat, names = LB.material_map()
        tex = np.isin(mat, [names.index(t) for t in TEXTURE_MATERIALS])
        strict_m = np.isin(mat, [names.index(t) for t in ('pavement', 'water', 'sky', 'clouds', 'bandana')])
        chk = checker_cells if 'checker' in steps else np.zeros(R.shape, bool)
        R, nrem, nkeep = speck_rule(R, PL, ramps, locked & ~chk, tex | chk, C, strict=strict_m)
        info['specks_removed'] = nrem; info['specks_kept_texture'] = nkeep
        if 'opt' in steps:
            # recover the form without creating specks outside texture
            R, nch2 = optimise(R, V, C, PL, pal, ref, locked, speck_ok=tex | chk | locked, tie=0.35, cmin=0.1, sweeps=6)
            nch += nch2
    if 'opt' in steps:
        info['cells_opt'] = nch
    if 'regular' in steps:
        nfl = 0
        H, W = Lp.shape
        cellid = (J.astype(np.int64) * NX + I).ravel()
        cnt = np.bincount(cellid, minlength=NX * NY)
        for name, (x0, y0, x1, y1), cls in SHAPES:
            cc = colour_class(PL, cls)
            i0, i1 = x0 * NX // W, -(-x1 * NX // W); j0, j1 = y0 * NY // H, -(-y1 * NY // H)
            box = np.zeros(R.shape, bool); box[j0:j1, i0:i1] = True
            srcm = cc[Lp]
            cov = (np.bincount(cellid, weights=srcm.ravel(), minlength=NX * NY) / np.maximum(cnt, 1)).reshape(NY, NX)
            res = cc[R] & box
            new, fl = regularize(res, np.where(box & ~locked, cov, 0.0))
            for j, i in np.argwhere(new != res):
                nbrs = [R[y, x] for y, x in ((j, i - 1), (j, i + 1), (j - 1, i), (j + 1, i)) if 0 <= y < NY and 0 <= x < NX]
                want = [l for l in nbrs if cc[l] == new[j, i]]
                if want:
                    vals, c = np.unique(want, return_counts=True)
                    R[j, i] = vals[c.argmax()]; nfl += 1
        info['cells_regular'] = nfl
    if 'foliage' in steps:
        mat, names = LB.material_map()
        nfo = 0
        for fb in FOLIAGE_BOXES:
            R, nf1 = foliage_clumps(R, PL, mat, names, locked, hard, visible_mask(), fb)
            nfo += nf1
        info['foliage_cells'] = nfo
    if 'water' in steps:
        mat, names = LB.material_map()
        R, nwat = regular_water(R, PL, mat, names, locked, hard, visible_mask())
        info['water_cells'] = nwat
    if 'unify' in steps:
        R, nu = unify_small_features(R, PL, C, V, locked)
        info['cells_unified'] = nu
    if 'mixel' in steps:
        R = fix_mixels(R, V, PL, locked=hard)
        if 'shapes3' in steps:                        # bird box: sky around the 1 px line only
            for j, i in np.argwhere(birdbox & ~bird_line & (PL[R, 0] < 68)):
                nb = [R[y, x] for y in range(j - 1, j + 2) for x in range(i - 1, i + 2)
                      if 0 <= y < NY and 0 <= x < NX and PL[R[y, x], 0] >= 68]
                if nb:
                    R[j, i] = np.bincount(nb).argmax()
        cm = load_mask('coat') & ~(info.get('_masks', {}).get('pepper_outline', np.zeros(R.shape, bool)))
        for j, i in np.argwhere(cm & (PL[R, 2] < -15)):
            if qa.specks(R[max(0, j - 1):j + 2, max(0, i - 1):i + 2].astype(np.int64), np.ones((min(NY, j + 2) - max(0, j - 1), min(NX, i + 2) - max(0, i - 1)), bool))[0] or \
               (R[max(0, j - 1):j + 2, max(0, i - 1):i + 2] == R[j, i]).sum() <= 2:
                nb = [R[y, x] for y, x in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1)) if 0 <= y < NY and 0 <= x < NX and PL[R[y, x], 2] >= -15]
                if nb:
                    R[j, i] = np.bincount(nb).argmax()
        if 'clean' in steps:
            mat, names = LB.material_map()
            R, nrare = rare_colours(R, PL, ramps, mat, names, vis=visible_mask())
            info['rare_cells'] = nrare
            R = fix_mixels(R, V, PL, locked=hard)
        if 'specks' in steps:
            for _ in range(2):
                R, nr2, nkeep = speck_rule(R, PL, ramps, locked & ~chk, tex | chk, C, strict=strict_m)
                info['specks_kept'] = nkeep
                R = fix_mixels(R, V, PL, locked=hard)
                info['specks_removed'] += nr2
    if 'speck' in steps:
        R = despeckle(R, V, PL)
        R = fix_mixels(R, V, PL, locked=hard)
    if 'mixel' in steps:                     # last resort: no mixel survives, line layers kept
        mk = info.get('_masks', {})
        keep = mk.get('pepper_outline', np.zeros(R.shape, bool)) | mk.get('strokes', np.zeros(R.shape, bool))
        if 'shapes3' in steps:
            keep = keep | bird_line
        R = fix_mixels(R, V, PL, locked=keep)
    return R, pal, info, (Lp, V, C)



# ---------------------------------------------------------------- QA report
# named shapes: (name, source box x0, y0, x1, y1, palette colour class)
SHAPES = [
    ('sail_left', (1760, 1030, 1900, 1212), 'cream'),
    ('sail_right', (1880, 1010, 1995, 1172), 'cream'),
    ('lantern_glass', (190, 370, 330, 480), 'glow'),
    ('lantern_frame', (160, 300, 340, 560), 'dark'),
    ('bench', (2210, 1370, 2400, 1580), 'dark'),
    ('bridge_stone', (1100, 1070, 1700, 1150), 'stone'),
    ('cloud_left', (280, 520, 600, 700), 'cream'),
    ('clouds_city_left', (1050, 740, 1700, 900), 'cream'),
    ('clouds_city_right', (1700, 740, 2400, 900), 'cream'),
    ('railing', (1000, 1300, 1700, 1480), 'dark'),
    ('bandana', (0, 1100, 1100, 1792), 'pink'),
]
# regions the logo, tagline and head tracks will overwrite (cells x0, y0, x1, y1)
OTHER_TRACKS = [(95, 12, 305, 98), (150, 188, 280, 210), (55, 62, 125, 150)]


def colour_class(PL, cls):
    L, a, b = PL[:, 0], PL[:, 1], PL[:, 2]
    ch = np.hypot(a, b)
    return {'cream': (L > 80) & (ch < 25), 'glow': (L > 55) & (b > 40), 'dark': L < 25,
            'stone': (L > 55) & (L < 80) & (ch < 25), 'pink': (a > 35) & (L > 35)}[cls]


def report(R, pal, info, Lp, a, write=True):
    import json
    PL = srgb_to_lab(pal.astype(np.float32))
    img = pal[R]
    H, W = Lp.shape
    ones = np.ones(R.shape, bool)
    mine = visible_mask()
    rep = {}
    rep['off_palette'] = qa.off_palette(img, pal, ones)[0]
    rep['mixels'] = qa.mixels(img, ones)[0]
    rep['specks'] = qa.specks(img, ones)[0]
    rep['specks_visible'] = int((qa.specks(img, ones)[1] & mine).sum())
    kv = qa.keys(img)[mine]; vv, cc = np.unique(kv, return_counts=True)
    rep['colours_visible'] = int(len(vv)); rep['rare_colours_visible'] = int((cc <= 3).sum())
    gj = os.path.join(OUT, 'grid.json')
    rep['form_all'] = qa.form(img, ones, a, gj)[:2]
    rep['form_mine'] = qa.form(img, mine, a, gj)[:2]
    reg_ex = mine.copy()
    for (x0, y0, x1, y1) in REGULARISED:
        reg_ex[y0:y1, x0:x1] = False
    rep['form_mine_excl_regularised'] = qa.form(img, reg_ex, a, gj)[:2]
    rep['form_all_uniform_cells'] = qa.form(img, ones, a, None)[:2]
    rep['checker_phase'] = qa.checker_phase(img, ones)
    rep['checker_phase_mine'] = qa.checker_phase(img, mine)
    md = os.path.join(OUT, 'qa_masks'); os.makedirs(md, exist_ok=True)
    shapes = {}
    for name, (x0, y0, x1, y1), cls in SHAPES:
        cc = colour_class(PL, cls)
        box = np.zeros((H, W), bool); box[y0:y1, x0:x1] = True
        src = cc[Lp] & box
        src = ndi.binary_opening(src, iterations=1)
        i0, i1 = x0 * NX // W, -(-x1 * NX // W); j0, j1 = y0 * NY // H, -(-y1 * NY // H)
        res = np.zeros(R.shape, bool); res[j0:j1, i0:i1] = cc[R[j0:j1, i0:i1]]
        up_box = qa.upscale_mask(res, (H, W)) & box
        res_c = res.copy()
        iou, bd = qa.geometry(res_c, src) if False else _geom_box(res, src, box)
        st = qa.staircase_regularity(res)
        shapes[name] = {'iou': round(iou, 3), 'boundary_dist_blocks': round(bd, 3),
                        'staircase': round(st[0], 3), 'segments': st[1]}
        if write:
            Image.fromarray((res * 255).astype(np.uint8)).save(os.path.join(md, name + '_320.png'))
            Image.fromarray((src * 255).astype(np.uint8)).save(os.path.join(md, name + '_src.png'))
    # Pepper silhouette (shape layer) against the painting's silhouette
    m = info.get('_masks', {})
    if 'pepper_shape' in m:
        iou, bd = qa.geometry(m['pepper_shape'], m['pepper_full'])
        st = qa.staircase_regularity(m['pepper_shape'])
        shapes['pepper_silhouette'] = {'iou': round(iou, 3), 'boundary_dist_blocks': round(bd, 3),
                                       'staircase': round(st[0], 3), 'segments': st[1]}
    rep['shapes'] = shapes
    lines = {}
    for name in ('pepper_outline', 'strokes'):
        if name in m:
            ln = m[name]
            lines[name] = {'lcorners': qa.lcorners(ln)[0], 'gaps': qa.gaps(ln)[0],
                           'endpoints': int(qa.endpoints(ln).sum()), 'pixels': int(ln.sum())}
            if write:
                Image.fromarray((ln * 255).astype(np.uint8)).save(os.path.join(md, name + '_320.png'))
    for name in ('pepper_outline', 'strokes'):
        if name in m:
            f, nw, _ = qa.staircase_regularity(m[name], line=True)
            lines[name]['staircase'] = round(f, 3); lines[name]['staircase_windows'] = nw
    rep['lines'] = lines
    if write:
        json.dump(rep, open(os.path.join(OUT, 'qa_bg.json'), 'w'), indent=1, default=float)
    return rep


def _geom_box(res320, src, box):
    """IoU and mean boundary distance (blocks) inside a box; the 320 mask is upscaled
    uniformly (as the game shows it)."""
    up = qa.upscale_mask(res320, src.shape) & box
    inter = (up & src).sum(); uni = (up | src).sum()
    iou = inter / max(uni, 1)
    def bnd(mm):
        return mm & ~ndi.binary_erosion(mm)
    b1, b2 = bnd(up), bnd(src)
    if b1.sum() == 0 or b2.sum() == 0:
        return float(iou), float('inf')
    sl = np.nonzero(box.any(1))[0], np.nonzero(box.any(0))[0]
    ys = slice(sl[0][0], sl[0][-1] + 1); xs = slice(sl[1][0], sl[1][-1] + 1)
    d2 = ndi.distance_transform_edt(~b2[ys, xs]); d1 = ndi.distance_transform_edt(~b1[ys, xs])
    md = 0.5 * (d2[b1[ys, xs]].mean() + d1[b2[ys, xs]].mean()) / (src.shape[1] / NX)
    return float(iou), float(md)


if __name__ == '__main__':
    R, pal, info, _ = build()
    img = pal[R]
    Image.fromarray(img).save(os.path.join(OUT, 'result_bg_320.png'))
    rgba = np.dstack([img, np.full(R.shape, 255, np.uint8)])
    Image.fromarray(rgba, 'RGBA').save(os.path.join(OUT, 'result_bg_320_rgba.png'))
    Image.fromarray(np.full(R.shape, 255, np.uint8)).save(os.path.join(OUT, 'mask_bg_320.png'))
    print({k: v for k, v in info.items() if not k.startswith('_')}, 'colours used', len(np.unique(R)))
    rep = report(R, pal, info, _[0], load_src())
    import json
    print(json.dumps(rep, indent=1, default=float))
