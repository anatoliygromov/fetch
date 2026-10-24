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
        # local share of the lighter value decides solid A, checker, solid B
        k3 = np.ones((3, 3))
        fB = ndi.convolve(B.astype(float), k3, mode='constant') / np.maximum(ndi.convolve(AB.astype(float), k3, mode='constant'), 1)
        newv = np.where(fB < 0.3, lo, np.where(fB > 0.7, hi, np.where(par, lo, hi)))
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
        if ax == 0:
            m[0] = m[-1] = False
        else:
            m[:, 0] = m[:, -1] = False
        out |= m
    return out


def fix_mixels(R, V, PL, iters=6):
    """Replace each mixel by one of its two opposite neighbours: the one better supported
    in the cell's own painting pixels; if neither occurs in the cell, the nearer colour."""
    R = R.copy()
    for _ in range(iters):
        mm = mixel_mask(R, PL)
        if not mm.any():
            break
        for j, i in zip(*np.nonzero(mm)):
            if not (0 < j < NY - 1 and 0 < i < NX - 1):
                continue
            cands = {int(R[j, i - 1]), int(R[j, i + 1]), int(R[j - 1, i]), int(R[j + 1, i])}
            cands.discard(int(R[j, i]))
            best = max(cands, key=lambda l: (V[j, i, l], -np.linalg.norm(PL[l] - PL[R[j, i]])))
            R[j, i] = best
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
    for (a, b) in ((R[j, i - 1], R[j, i + 1]), (R[j - 1, i], R[j + 1, i])):
        if a == b or r == a or r == b:
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
STROKE_W = (1.5, 6.0)  # median width in px (thinner than a cell)


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
            col = np.bincount(Lp[yi, xi]).argmax()
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
                if (v.astype(int) == vv).sum() < 3:
                    continue
                uu = coef[0] * vv + coef[1] if straight else np.median(u[v.astype(int) == vv])
                c = int(np.floor(uu))
                cells.append((vv, c) if axis == 1 else (c, vv))
            if len(cells) >= 2:
                mask = np.zeros((H, W), bool); mask[sl] = lab_c[sl] == k + 1
                out.append((cells, int(col), mask, axis))
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


def pepper_outline(a, lab, Lp, dp, I, J, PL, n, smooth=8.0):
    """Pepper's silhouette as a smooth shape on the grid and its 1 px black outline.
    Returns (shape cells, outline cells, outline colour, V_in, V_out, full-res mask)."""
    import shapes
    full = pepper_mask(lab, I, J)
    Sm, Sfull = shapes.raster_shape(full, I, J, s=smooth, pre=2.0)
    Sm = ndi.binary_fill_holes(Sm)
    # 8-connected inner boundary: shape cells with a 4-neighbour outside (image border excluded)
    out = ~Sm
    ring = np.zeros_like(Sm)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(out, (dy, dx), (0, 1))
        if dy == 1: nb[0] = False
        if dy == -1: nb[-1] = False
        if dx == 1: nb[:, 0] = False
        if dx == -1: nb[:, -1] = False
        ring |= Sm & nb
    # outline colour: the most common palette colour of the painting's outline band
    dist_in = ndi.distance_transform_edt(full)
    band = full & (dist_in <= 7) & (lab[..., 0] < 12)
    col = int(np.bincount(Lp[band]).argmax())
    # interior votes without the outline band; exterior votes without Pepper
    Vin, Cin = masked_votes(a, I, J, Lp, dp, n, full & ~((dist_in <= 9) & (lab[..., 0] < 12)))
    Vout, Cout = masked_votes(a, I, J, Lp, dp, n, ~ndi.binary_dilation(full, iterations=2))
    return Sm, ring, col, (Vin[..., :n], Cin[..., :n]), (Vout[..., :n], Cout[..., :n]), full


def optimise(R, V, C, PL, pal, ref, locked, sweeps=4, kappa=120.0, sigma=30.0, mu=1e4, cmin=0.15):
    """Coordinate descent over the cells. Each cell may take a colour that occurs in it
    (coverage >= cmin, or the vote winner) or, to resolve a mixel, a 4-neighbour colour.
    Objective: form error (5x5 box blurred luma vs the painting's cell means, squared)
    + kappa * vote deficit + sigma per isolated speck + mu per mixel."""
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
                cand = set(np.flatnonzero(C[j, i] >= cmin).tolist()) | {int(win0[j, i]), int(R[j, i])}
                near_mix = mm[max(0, j - 1):j + 2, max(0, i - 1):i + 2].any()
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
                    ns = sum(is_speck(R, y, x) for y, x in pos8)
                    cost = f + kappa * (Vn[j, i, win0[j, i]] - Vn[j, i, l]) + sigma * ns + mu * nm
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


def build(a=None, XB=None, YB=None, I=None, J=None, pal=None, ramps=None, steps=('pepper', 'strokes', 'checker', 'opt', 'mixel')):
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
        R[ring] = ocol; locked |= ring
        info['pepper_outline_cells'] = int(ring.sum())
        pep_ring, pep_shape = ring, Sm
    if 'strokes' in steps:
        st = strokes(lab, Lp, XB, YB, I, J)
        smask = np.zeros(Lp.shape, bool)
        for cells, col, mask, axis in st:
            smask |= mask
        # cells next to strokes re-vote without the stroke pixels (and their halo)
        halo = ndi.binary_dilation(smask, iterations=2)
        Vx, Cx = votes(a, I, J, np.where(halo, n, Lp), np.where(halo, 99, dp), n + 1)
        touched = np.zeros(R.shape, bool)
        touched[J[halo], I[halo]] = True
        R[touched] = Vx[..., :n].argmax(2)[touched]
        V = np.where(touched[..., None], Vx[..., :n], V); C = np.where(touched[..., None], Cx[..., :n], C)
        ncell = 0
        for cells, col, mask, axis in st:
            for (j, i) in cells:
                if 0 <= j < NY and 0 <= i < NX:
                    R[j, i] = col; locked[j, i] = True; ncell += 1
        info['strokes'] = len(st); info['cells_stroke'] = ncell
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
        info['cells_checker'] = int(ch.sum()); info['cells_checker_logo'] = int(ch2.sum())
    if 'opt' in steps:
        ref = cell_ref(a, I, J)
        R, nch = optimise(R, V, C, PL, pal, ref, locked)
        info['cells_opt'] = nch
    if 'mixel' in steps:
        R = fix_mixels(R, V, PL)
    if 'speck' in steps:
        R = despeckle(R, V, PL)
        R = fix_mixels(R, V, PL)
    return R, pal, info, (Lp, V, C)


if __name__ == '__main__':
    R, pal, info, _ = build()
    img = pal[R]
    Image.fromarray(img).save(os.path.join(OUT, 'result_bg_320.png'))
    rgba = np.dstack([img, np.full(R.shape, 255, np.uint8)])
    Image.fromarray(rgba, 'RGBA').save(os.path.join(OUT, 'result_bg_320_rgba.png'))
    Image.fromarray(np.full(R.shape, 255, np.uint8)).save(os.path.join(OUT, 'mask_bg_320.png'))
    print(info, 'colours used', len(np.unique(R)))
