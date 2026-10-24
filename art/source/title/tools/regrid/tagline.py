"""TAGLINE track: the "The City Dog Adventurer" plate under the FETCH! logo.

Run:  python3 tagline.py   (writes into <worktree>/out/)

Method (see out/notes.md for the full write-up):
 1. Palette: the plate's three flat colours (navy body/outline, light-blue rim, cream text),
    each the median of the painting's own flat pixels of that material.
 2. Glyphs: every painted letter is cut out (cream coverage = projection of the pixel colour
    onto the navy->cream axis, so anti-aliased edges count fractionally), sampled on its own
    block grid: rows = the painting's text rows, columns = the count (3, 4 or 5) that makes the
    coverage most decisive, summed over all instances of that letter (unfake.js / Perfect Pixel
    style per-cell voting, but per glyph). The cleanest instance (lowest ambiguity) gives the
    letter's bitmap (0.5 threshold); the only overrides are where the 1 px stroke rule needs them
    (RULES: the A shoulders, the n shoulder). Every instance of a letter then uses that one bitmap,
    so repeated letters are identical. A second pass repeats this on the refined grid.
 3. Layout: letter gap 1 px, word gap fitted (least error of glyph centres vs the painting),
    whole line placed where the glyph centres match the painting best.
 4. Local grid: separable refined grid. Rows follow the painting's plate bands and text rows;
    columns follow the plate ends and, in the text, each glyph's own block columns. Used for
    sampling the plate and for every QA comparison (cells re-upscaled to the painting).
 5. Plate: measured parameters (rim rows/cols, outline thickness, 45 degree chamfer lengths,
    top and bottom fitted separately by IoU) -> exact octagon, no anti-aliasing; the rim is the 1 px
    4-boundary of the filled octagon (no L-corner doubles, all-1 runs on the chamfers); the
    navy outline is the 4-neighbour ring outside it plus one extra row at the bottom, owned
    where the painting shows navy there (elsewhere the dark city silhouette touches the rim).
"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tagline_font as TF

SRC = os.environ.get('REGRID_SRC', '/home/claude/fetch/source_title/title_original.png')
ROOT = os.path.abspath(os.path.join(HERE, '../../../../..'))
OUT = os.environ.get('TAG_OUT', os.path.join(ROOT, 'out'))
NX, NY = 320, 240
TEXT = "The City Dog Adventurer"

# region of interest in the painting (source px)
RX0, RX1, RY0, RY1 = 1080, 2230, 555, 745

# painting text rows (source y of the 10 row borders: cap top .. descender bottom)
TROWS = [622.0, 630.0, 636.5, 644.0, 652.0, 660.0, 668.0, 675.0, 681.0, 687.0]
CAP_ROW = 83          # output row of text row 0 (622.0 / 7.5 = 82.9)


def load():
    return np.array(Image.open(SRC).convert('RGB')).astype(np.float64)


def luma(c):
    return np.asarray(c, float) @ np.array([0.299, 0.587, 0.114])


# ----------------------------------------------------------------- palette
def measure_palette(a):
    def med(x0, x1, y0, y1):
        return np.median(a[y0:y1, x0:x1].reshape(-1, 3), 0)
    navy = np.median(np.concatenate([a[640:660, 1150:1200].reshape(-1, 3), a[600:615, 1300:1700].reshape(-1, 3),
                                     a[690:700, 1300:1700].reshape(-1, 3)]), 0)
    rim = np.median(np.concatenate([a[589:596, 1300:1700].reshape(-1, 3), a[707:714, 1300:1700].reshape(-1, 3)]), 0)
    # cream: glyph interiors (eroded cream mask)
    t = cream_cov(a, navy, np.array([255, 233, 196.]))
    core = ndi.binary_erosion(t[615:690, 1200:2120] > 0.9, np.ones((3, 3)))
    cream = np.median(a[615:690, 1200:2120][core], 0)
    return dict(navy=np.round(navy).astype(int), rim=np.round(rim).astype(int), cream=np.round(cream).astype(int))


def cream_cov(a, navy, cream):
    d = cream - navy
    t = ((a - navy) @ d) / (d @ d)
    return np.clip(t, 0, 1)


# ----------------------------------------------------------------- glyphs
def find_glyphs(t):
    Y0, Y1, X0, X1 = 615, 695, 1200, 2120
    lab, n = ndi.label(t[Y0:Y1, X0:X1] > 0.5)
    objs = ndi.find_objects(lab)
    comps = sorted([(o[1].start + X0, o[1].stop + X0, i + 1) for i, o in enumerate(objs)
                    if (lab[o] == i + 1).sum() >= 30])
    groups = []
    for x0, x1, c in comps:
        if groups and x0 < groups[-1][1] - 2:
            groups[-1][1] = max(groups[-1][1], x1)
        else:
            groups.append([x0, x1])
    letters = TEXT.replace(' ', '')
    assert len(groups) == len(letters), (len(groups), len(letters))
    return [dict(ch=ch, x0=g[0], x1=g[1]) for ch, g in zip(letters, groups)]


def coverage(t, x0, x1, nc, rows=TROWS, xb=None):
    """mean cream coverage per (row, column) cell, area-weighted with fractional pixel edges.
    Columns: nc equal columns over [x0, x1) or explicit borders xb (nc + 1 values)."""
    if xb is None:
        xb = [x0 + c * (x1 - x0) / nc for c in range(nc + 1)]
    nc = len(xb) - 1
    C = np.zeros((len(rows) - 1, nc))
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        ys = np.arange(int(np.floor(ya)), int(np.ceil(yb)))
        wy = np.clip(np.minimum(ys + 1, yb) - np.maximum(ys, ya), 0, 1)
        for c in range(nc):
            xa, xbb = xb[c], xb[c + 1]
            xs = np.arange(int(np.floor(xa)), int(np.ceil(xbb)))
            wx = np.clip(np.minimum(xs + 1, xbb) - np.maximum(xs, xa), 0, 1)
            W = wy[:, None] * wx[None]
            C[r, c] = (t[np.ix_(ys, xs)] * W).sum() / W.sum()
    return C


def ambiguity(C):
    return float(np.minimum(C, 1 - C).mean())


def has_block(bm):
    b = np.asarray(bm, bool)
    return bool((b[1:, 1:] & b[:-1, 1:] & b[1:, :-1] & b[:-1, :-1]).any())


# overrides of the cleanest instance's 0.5 threshold, only where the 1 px stroke rule needs it.
# key: (letter, row in the 9-row box, col) -> value; each one is listed in notes.md with its reason.
RULES = {
    # A: the shoulders sit half a block in, so row 1 reads ~0.5 everywhere; '.##.' would double the
    # top stroke into a 2x2 block, so the 1 px reading '#..#' is taken (also what equal columns give)
    ('A', 1, 0): True, ('A', 1, 1): False, ('A', 1, 2): False, ('A', 1, 3): True,
    # n: the painted shoulder thickens the stem (0.70) under the arch; '##.#' would make a 2x2 block
    # with the arch row above (stroke must stay 1 px), so the shoulder cell is dropped, as in h
    ('n', 3, 1): False,
}


def extract_glyphs(t, grid=None):
    """first pass (grid None): equal columns, choose the column count per letter.
    second pass: the refined grid's text rows and each glyph's refined column borders."""
    inst = find_glyphs(t)
    rows = TROWS if grid is None else grid['trows']
    if grid is not None:
        for g, xb in zip(inst, grid['glyph_cols']):
            g['xb'] = xb
    letters = sorted(set(g['ch'] for g in inst))
    table, report = {}, {}
    for ch in letters:
        gs = [g for g in inst if g['ch'] == ch]
        scores = {}
        if grid is None:
            for nc in (3, 4, 5):
                scores[nc] = sum(ambiguity(coverage(t, g['x0'], g['x1'], nc, rows)) for g in gs) / len(gs)
            best = min(scores.values())
            cands = sorted([nc for nc in scores if scores[nc] <= best * 1.05], key=lambda n: scores[n])
        else:
            cands = [len(gs[0]['xb']) - 1]
        chosen = None
        for nc in cands:
            covs = [coverage(t, g['x0'], g['x1'], nc, rows, g.get('xb')) for g in gs]
            k = int(np.argmin([ambiguity(C) for C in covs]))
            bm = covs[k] >= 0.5
            if not has_block(bm) or nc == cands[-1]:
                chosen = (nc, covs, k, bm); break
        nc, covs, k, bm = chosen
        C = covs[k]
        amb_cells = [(int(r), int(c), round(float(C[r, c]), 2)) for r, c in zip(*np.nonzero((C > 0.4) & (C < 0.6)))]
        bm = bm.copy()
        for (cc, r, c), v in RULES.items():
            if cc == ch:
                bm[r, c] = v
        agree = [int(((Ci >= 0.5) == (C >= 0.5)).sum()) for Ci in covs]
        rws = np.nonzero(bm.any(1))[0]
        top, bot = int(rws.min()), int(rws.max())
        table[ch] = (top, [''.join('#' if v else '.' for v in bm[r]) for r in range(top, bot + 1)])
        for g in gs:
            g['nc'] = nc
        report[ch] = dict(nc=nc, nc_scores={k2: round(v, 3) for k2, v in scores.items()}, instances=len(gs),
                          cleanest=k, ambiguity=[round(ambiguity(Ci), 3) for Ci in covs],
                          cells_agree_with_cleanest=agree, cells=int(C.size), ambiguous_cells=amb_cells,
                          coverage_cleanest=[[round(float(v), 2) for v in row] for row in C])
    return inst, table, report


# ----------------------------------------------------------------- layout
def fit_layout(inst, plate_centre=(1134 + 2176) / 2 / 7.5):
    """letter gap is fixed at 1 px; the word space and the start column are fitted: least RMS
    error of glyph centres against the painting (standard cells, x / 7.5), subject to the line
    staying centred on the plate within 1 cell (the painting's line is centred within 0.5)."""
    pc = np.array([(g['x0'] + g['x1']) / 2 / 7.5 for g in inst])
    best, table = None, []
    old = TF.SPACE
    for sp in range(2, 10):
        TF.SPACE = sp
        lay = TF.layout(TEXT, 0)
        W = TF.text_width(TEXT)
        oc = np.array([x + TF.width(ch) / 2 for ch, x in lay])
        for s1 in range(150, 175):
            err = np.abs(oc + s1 - pc)
            rms = float(np.sqrt((err ** 2).mean()))
            centred = abs(s1 + W / 2 - plate_centre) <= 1.0
            table.append((sp, s1, round(rms, 3), round(float(err.max()), 3), centred))
            if centred and (best is None or rms < best[0]):
                best = (rms, sp, s1, err.max(), W, err.mean())
    TF.SPACE = old
    return dict(space=best[1], start=best[2], width=best[4], rms_err=round(float(best[0]), 3), mean_err=round(float(best[5]), 3),
                max_err=round(float(best[3]), 3), plate_centre=round(plate_centre, 2),
                text_centre=best[2] + best[4] / 2)


# ----------------------------------------------------------------- refined grid
def edge_profiles(a, thr=40):
    """counts of strong colour changes (non-max suppressed along the axis) per border position.
    px[y, x]: an edge on the border between x-1 and x; py[y, x]: between y-1 and y."""
    gx = np.abs(np.diff(a, axis=1)).max(2)
    gy = np.abs(np.diff(a, axis=0)).max(2)
    def nms(gr, axis):
        p = np.pad(gr, [(1, 1) if ax == axis else (0, 0) for ax in range(2)], mode='edge')
        if axis == 1:
            l, c, r = p[:, :-2], p[:, 1:-1], p[:, 2:]
        else:
            l, c, r = p[:-2], p[1:-1], p[2:]
        return (c >= l) & (c >= r) & (c > thr)
    ex = np.zeros(a.shape[:2], bool); ey = np.zeros(a.shape[:2], bool)
    ex[:, 1:] = nms(gx, 1); ey[1:, :] = nms(gy, 0)
    return ex, ey


def snap(prof, b, tol, lo, hi, min_count):
    """move border b (float) to the strongest edge position within tol, keeping lo < b < hi."""
    cands = [x for x in range(int(np.ceil(b - tol)), int(np.floor(b + tol)) + 1) if lo < x < hi]
    if not cands:
        return b
    v = [prof[x] for x in cands]
    if max(v) < min_count:
        return b
    best = max(v)
    xs = [x for x, vv in zip(cands, v) if vv == best]
    return float(min(xs, key=lambda x: abs(x - b)))


def build_grid(inst, lay_start, a, t=None):
    """separable refined grid. Start: knots at the painting's plate bands / text rows and at the
    plate ends; in the text each glyph's columns split its painted width equally. Then every
    border is snapped (within 3 px for rows, 2.5 px for columns, never closer than 4 px to its
    neighbours) to the strongest local edge count in the painting."""
    ex, ey = edge_profiles(a)
    # ---- rows
    Y = {}
    Y.update({77: 577.0, 78: 587.0, 79: 597.5})
    for k in range(80, 83):
        Y[k] = 597.5 + (k - 79) * (TROWS[0] - 597.5) / 4
    for i, y in enumerate(TROWS):
        Y[CAP_ROW + i] = y
    Y[93] = (687.0 + 704.5) / 2
    Y.update({94: 704.5, 95: 715.5, 96: 722.5, 97: 729.5})
    for k in range(70, 77):
        Y[k] = 577.0 - (77 - k) * 7.5
    for k in range(98, 106):
        Y[k] = 729.5 + (k - 97) * 7.5
    py = ey[:, 1120:2192].sum(1)
    rows = sorted(Y)
    for i, r in enumerate(rows):
        if 76 <= r <= 98:
            lo = Y[rows[i - 1]] + 4; hi = Y[rows[i + 1]] - 4
            Y[r] = snap(py, Y[r], 3.0, lo, hi, 60)
    trows = [Y[CAP_ROW + i] for i in range(len(TROWS))]
    # ---- columns
    X = {150: 1125.0, 151: 1134.0, 152: 1144.0, 289: 2166.0, 290: 2176.0, 291: 2186.0}
    lay = TF.layout(TEXT, lay_start)
    gcols = []
    for (ch, x), g in zip(lay, inst):
        nc = TF.width(ch)
        xb0 = [g['x0'] + k * (g['x1'] - g['x0']) / nc for k in range(nc + 1)]
        # this glyph's own vertical edges, over the text rows
        pxg = np.zeros(a.shape[1])
        pxg[g['x0'] - 2:g['x1'] + 3] = ex[int(trows[0]):int(trows[-1]) + 1, g['x0'] - 2:g['x1'] + 3].sum(0)
        xb = list(xb0)
        for k in range(1, nc):
            xb[k] = snap(pxg, xb0[k], 2.5, xb[k - 1] + 4, xb0[k + 1] - 4, 6)
        # keep the snapped borders only if the glyph's decisive cells stay the same
        if t is not None:
            b0 = coverage(t, 0, 0, 0, trows, xb0) >= 0.5
            b1 = coverage(t, 0, 0, 0, trows, xb) >= 0.5
            if not np.array_equal(b0, b1):
                xb = xb0
        gcols.append(xb)
        for k in range(nc + 1):
            X[x + k] = xb[k]
    ks = sorted(X)
    for c in range(ks[0], ks[-1] + 1):
        if c not in X:
            lo = max(k for k in ks if k < c); hi = min(k for k in ks if k > c)
            X[c] = X[lo] + (c - lo) * (X[hi] - X[lo]) / (hi - lo)
    # plate-end columns (outside the text) snap to the plate's own edges
    pxp = ex[575:733].sum(0)
    first, last = lay[0][1], lay[-1][1] + TF.width(lay[-1][0])
    X0 = dict(X)
    for c in list(range(150, first)) + list(range(last + 1, 292)):
        X[c] = snap(pxp, X0[c], 3.0, -1e9, 1e9, 6)
    for c in list(range(151, first)) + list(range(last + 1, 292)):
        if X[c] - X[c - 1] < 4.5:            # keep cells at least 4.5 px wide: undo the snap
            X[c] = X0[c] if X0[c] - X[c - 1] >= 4.5 else X[c - 1] + 4.5
    for c in range(140, 150):
        X[c] = 1125.0 - (150 - c) * 7.5
    for c in range(292, 302):
        X[c] = 2186.0 + (c - 291) * 7.5
    cols = np.arange(140, 302); rws = np.arange(70, 106)
    return dict(X=np.array([X[c] for c in cols]), Y=np.array([Y[r] for r in rws]), c0=140, r0=70,
                trows=trows, glyph_cols=gcols)


def cell_of(grid, xs, ys):
    """cell indices (col, row) of source pixel centres."""
    ci = np.searchsorted(grid['X'], xs + 0.5, side='right') - 1 + grid['c0']
    ri = np.searchsorted(grid['Y'], ys + 0.5, side='right') - 1 + grid['r0']
    return ci, ri


def upscale(grid, m, x0=RX0, x1=RX1, y0=RY0, y1=RY1):
    xs = np.arange(x0, x1); ys = np.arange(y0, y1)
    ci, ri = cell_of(grid, xs, ys)
    ci = np.clip(ci, 0, NX - 1); ri = np.clip(ri, 0, NY - 1)
    return m[np.ix_(ri, ci)]


def cell_stats(grid, a_reg, cls_reg, ncls, x0=RX0, y0=RY0):
    """per-cell class fractions and mean colour over the cell's source rectangle."""
    H, W = cls_reg.shape
    xs = np.arange(x0, x0 + W); ys = np.arange(y0, y0 + H)
    ci, ri = cell_of(grid, xs, ys)
    CI = np.broadcast_to(ci[None], (H, W)); RI = np.broadcast_to(ri[:, None], (H, W))
    ok = (CI >= 0) & (CI < NX) & (RI >= 0) & (RI < NY)
    idx = RI[ok] * NX + CI[ok]
    cnt = np.bincount(idx, minlength=NX * NY).reshape(NY, NX).astype(float)
    frac = np.zeros((ncls, NY, NX))
    for k in range(ncls):
        frac[k] = np.bincount(idx, weights=(cls_reg[ok] == k).astype(float), minlength=NX * NY).reshape(NY, NX)
    frac /= np.maximum(cnt, 1)
    L = luma(a_reg)
    meanL = np.bincount(idx, weights=L[ok], minlength=NX * NY).reshape(NY, NX) / np.maximum(cnt, 1)
    return frac, meanL, cnt


# ----------------------------------------------------------------- plate
CLS = ['N', 'R', 'C', 'K', 's', 'M', 'o']   # navy, rim, cream, dark city, sky, city/rim mid-blue, other


def classify(a_reg, pal):
    P = np.array([pal['navy'], pal['rim'], pal['cream'], (1, 17, 52), (110, 178, 224), (20, 112, 198), (255, 99, 3)], float)
    d = ((a_reg[:, :, None, :] - P[None, None]) ** 2).sum(-1)
    return d.argmin(-1)


def corner_insets(runs):
    """insets of the rim rows, starting at the straight (top or bottom) rim row and moving toward
    the middle: the straight row is inset len(runs)+1 columns, then each diagonal column i
    (inset len(runs)-i) lasts runs[i] rows, then inset 0 (the vertical side).
    runs all 1 = a 45 degree chamfer; a 2 at one end rounds that end of the chamfer."""
    k = len(runs) + 1
    ins = [k]
    for i, n in enumerate(runs):
        ins += [k - 1 - i] * n
    return ins


def octagon(rim_top, rim_bot, rim_left, rim_right, top_runs, bot_runs=None, top_runs_r=None, bot_runs_r=None):
    """filled plate shape inside (and including) the rim: straight sides, corners from run lists
    (an int k is shorthand for a 45 degree chamfer: k-1 diagonal pixels between the sides).
    The right-hand corners default to the mirror of the left-hand ones."""
    def norm(v):
        if isinstance(v, int):
            return [1] * (v - 1) if v > 0 else None
        return v
    tl = norm(top_runs); bl = norm(bot_runs) if bot_runs is not None else tl
    tr = norm(top_runs_r) if top_runs_r is not None else tl
    br = norm(bot_runs_r) if bot_runs_r is not None else bl
    ins = lambda runs: corner_insets(runs) if runs is not None else [0]
    TL, BL, TR, BR = ins(tl), ins(bl), ins(tr), ins(br)
    at = lambda lst, i: lst[i] if i < len(lst) else 0
    F = np.zeros((NY, NX), bool)
    for r in range(rim_top, rim_bot + 1):
        a = r - rim_top; b = rim_bot - r
        li = max(at(TL, a), at(BL, b)); ri = max(at(TR, a), at(BR, b))
        F[r, rim_left + li: rim_right - ri + 1] = True
    return F


def corner_candidates(maxlen=6, rounded=False):
    """45 degree chamfers (all runs 1) of every length; with rounded=True also monotone run lists of
    1s and 2s (at most two 2s). Rounded profiles were evaluated (notes.md, iteration 3): they move
    the IoU by under 0.005 and would give the top and bottom corners different styles, so the
    default keeps pure chamfers."""
    out = [[]]
    for n in range(1, maxlen + 1):
        for n2 in (range(0, min(2, n) + 1) if rounded else [0]):
            out.append([2] * n2 + [1] * (n - n2))
            if 0 < n2 < n:
                out.append([1] * (n - n2) + [2] * n2)
    return out


def ring4(F):
    out = np.zeros_like(F)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        out |= F & ~np.roll(np.roll(F, dy, 0), dx, 1)
    return out


def dil4(F):
    out = F.copy()
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        out |= np.roll(np.roll(F, dy, 0), dx, 1)
    return out


def painting_masks(a, pal):
    """the painting's own shape masks at source resolution over the region."""
    reg = a[RY0:RY1, RX0:RX1]
    cls = classify(reg, pal)
    yy = np.arange(RY0, RY1)[:, None] + np.zeros((1, RX1 - RX0))
    band = (yy >= 584) & (yy <= 718)
    rim = ((cls == 1) | (cls == 5)) & band
    rim = ndi.binary_opening(rim, np.ones((2, 2)))
    lab, n = ndi.label(rim)
    sz = ndi.sum(rim, lab, range(1, n + 1))
    rim = lab == (1 + int(np.argmax(sz)))
    fill = ndi.binary_fill_holes(rim)
    body = fill & ~rim
    t = cream_cov(reg, pal['navy'].astype(float), pal['cream'].astype(float))
    text = (t > 0.5) & body
    navy = (cls == 0)
    near = ndi.binary_dilation(fill, iterations=16)
    outline = navy & near & ~fill
    lab, n = ndi.label(outline)
    if n:
        sz = ndi.sum(outline, lab, range(1, n + 1))
        outline = np.isin(lab, np.flatnonzero(sz >= 60) + 1)
    return dict(cls=cls, rim=rim, fill=fill, body=body, text=text, outline=outline, outer=fill | outline)


def iou(a, b):
    return float((a & b).sum() / max(1, (a | b).sum()))


def bdist(a, b, block=7.5):
    def edge(m):
        return m & ~ndi.binary_erosion(m)
    ea, eb = edge(a), edge(b)
    if not ea.any() or not eb.any():
        return float('nan')
    da = ndi.distance_transform_edt(~eb)[ea].mean()
    db = ndi.distance_transform_edt(~ea)[eb].mean()
    return float((da + db) / 2 / block)


def measure_plate(grid, frac, PM):
    N, R = frac[0], frac[1] + frac[5]
    mid = slice(175, 265)
    rim_top = 74 + int(np.argmax(R[74:83, mid].mean(1)))
    rim_bot = 90 + int(np.argmax(R[90:99, mid].mean(1)))
    rim_left = 146 + int(np.argmax(R[84:89, 146:157].mean(0)))
    rim_right = 284 + int(np.argmax(R[84:89, 284:295].mean(0)))
    # outline rows below the rim at mid width
    ob = 0
    for r in range(rim_bot + 1, rim_bot + 5):
        if N[r, mid].mean() > 0.5:
            ob += 1
        else:
            break
    # corners (top and bottom fitted separately, left/right mirrored): among clean staircase
    # profiles, the best mean of the IoU of the filled shape and the IoU of its 1 px rim ring
    # against the painting's (re-upscaled to source px); ties go to the shorter, simpler profile
    best = None
    for tr in corner_candidates():
        for br in corner_candidates():
            F = octagon(rim_top, rim_bot, rim_left, rim_right, tr, br)
            s1 = iou(upscale(grid, F), PM['fill']); s2 = iou(upscale(grid, ring4(F)), PM['rim'])
            sc = round((s1 + s2) / 2, 5)
            key = (sc, -(sum(tr) + sum(br)) * 0, -(len(set(tr)) + len(set(br))))
            if best is None or key > best[0]:
                best = (key, tr, br, s1, s2)
    return dict(rim_top=rim_top, rim_bot=rim_bot, rim_left=rim_left, rim_right=rim_right,
                outline_bottom_rows=ob, corner_top=best[1], corner_bot=best[2],
                corner_fill_iou=round(best[3], 4), corner_ring_iou=round(best[4], 4))


def build_plate(P, frac):
    F = octagon(P['rim_top'], P['rim_bot'], P['rim_left'], P['rim_right'], P['corner_top'], P['corner_bot'])
    rim = ring4(F)
    body = F & ~rim
    D = dil4(F)
    for _ in range(P['outline_bottom_rows'] - 1):
        D = D | np.roll(D, 1, 0)
    band = D & ~F
    N = frac[0]
    city = frac[3] + frac[4]          # dark city silhouette or sky: not plate
    own_band = band & (city < 0.5)
    return dict(F=F, rim=rim, body=body, band=band, outline=own_band)


# ----------------------------------------------------------------- render
def render(plate, textmask, pal):
    img = np.zeros((NY, NX, 4), np.uint8)
    own = plate['outline'] | plate['F']
    img[own, :3] = pal['navy']; img[own, 3] = 255
    img[plate['rim'], :3] = pal['rim']
    tm = textmask & plate['body']
    img[tm, :3] = pal['cream']
    return img, own


def text_mask(lay_start, text=TEXT):
    m = np.zeros((NY, NX), bool)
    return TF.stamp(m, text, lay_start, CAP_ROW)


def plate_with_text(S, text):
    """the same plate with any other text in the same font, centred on the plate, on the same rows."""
    w = TF.text_width(text)
    centre = (S['P']['rim_left'] + S['P']['rim_right'] + 1) / 2
    x0 = int(np.floor(centre - w / 2))
    inner = S['plate']['body']
    cols = np.nonzero(inner[CAP_ROW + 4])[0]
    if x0 < cols.min() + 2 or x0 + w > cols.max() - 1:
        raise ValueError('text too wide for the plate: %d px, room %d' % (w, cols.max() - cols.min() - 2))
    img, _ = render(S['plate'], text_mask(x0, text), S['pal'])
    return img


def run(verbose=True):
    os.makedirs(OUT, exist_ok=True)
    a = load()
    pal = measure_palette(a)
    t = cream_cov(a, pal['navy'].astype(float), pal['cream'].astype(float))
    inst0, table0, grep0 = extract_glyphs(t)
    lay = fit_layout(inst0)
    if lay['space'] != TF.SPACE:
        print('WARNING: fitted space', lay['space'], 'differs from font SPACE', TF.SPACE)
    grid = build_grid(inst0, lay['start'], a, t)
    inst, table, grep = extract_glyphs(t, grid)
    mism = {ch: (table[ch], TF.RECOVERED.get(ch)) for ch in table if TF.RECOVERED.get(ch) != table[ch]}
    mism0 = {ch: (table0[ch], TF.RECOVERED.get(ch)) for ch in table0 if TF.RECOVERED.get(ch) != table0[ch]}
    for ch in grep:
        grep[ch]['nc_scores'] = grep0[ch]['nc_scores']
    PM = painting_masks(a, pal)
    frac, meanL, cnt = cell_stats(grid, a[RY0:RY1, RX0:RX1], PM['cls'], len(CLS))
    P = measure_plate(grid, frac, PM)
    plate = build_plate(P, frac)
    tm = text_mask(lay['start'])
    img, own = render(plate, tm, pal)
    blank, _ = render(plate, np.zeros_like(tm), pal)
    S = dict(a=a, pal=pal, t=t, inst=inst, table=table, grep=grep, mism=mism, lay=lay, grid=grid, PM=PM,
             frac=frac, meanL=meanL, P=P, plate=plate, tm=tm & plate['body'], img=img, own=own, blank=blank)
    if verbose:
        print('palette', {k: v.tolist() for k, v in pal.items()})
        print('layout', lay)
        print('plate', P)
        print('glyph mismatches vs RECOVERED (refined grid):', mism if mism else 'none')
        print('glyph mismatches vs RECOVERED (equal columns):', mism0 if mism0 else 'none')
        print('rows', [round(v, 1) for v in grid['Y'][76 - 70:99 - 70]])
    return S


def save_outputs(S):
    Image.fromarray(S['img']).save(os.path.join(OUT, 'tagline_region.png'))
    m = (S['own'] * 255).astype(np.uint8)
    Image.fromarray(m).save(os.path.join(OUT, 'tagline_mask.png'))
    Image.fromarray(S['blank']).save(os.path.join(OUT, 'tagline_plate_blank.png'))
    Image.fromarray(plate_with_text(S, 'Press Start')).save(os.path.join(OUT, 'tagline_plate_sample_press_start.png'))
    pal = S['pal']
    hexs = ['#%02x%02x%02x' % tuple(pal[k]) for k in ('navy', 'rim', 'cream')]
    json.dump(hexs, open(os.path.join(OUT, 'palette.json'), 'w'), indent=1)
    meta = dict(text=TEXT, cap_row=CAP_ROW, text_start_col=S['lay']['start'], plate=S['P'],
                palette=dict(zip(('navy', 'rim', 'cream'), hexs)),
                text_box=dict(cols=[int(S['P']['rim_left']) + 1, int(S['P']['rim_right']) - 1],
                              rows=[int(S['P']['rim_top']) + 1, int(S['P']['rim_bot']) - 1]),
                glyph_extraction=S['grep'], layout_fit=S['lay'])
    json.dump(meta, open(os.path.join(OUT, 'tagline_meta.json'), 'w'), indent=1, default=int)


if __name__ == '__main__':
    S = run()
    save_outputs(S)
    import tagline_qa
    tagline_qa.main(S)
