"""Step 1: a local grid fit for the whole picture.

The painting's pseudo-pixels are not on one lattice. Block edges drift 1 to 3 px
against a uniform 7.5 px grid within a few cells, block widths vary (7 to 12 px),
and Pepper's coat uses larger blocks (about 11 px). The output must stay 320 x 240
with the painting's geometry, so every grid line may only move a few pixels away
from its uniform position (k * 7.5); within that budget it follows the painting's
real block edges.

Method (coarse to fine, in the spirit of Perfect Pixel's "global grid, then per
line refinement within a tolerance", with unfake.js style edge profiles):
  * edge strength per border position: max channel difference of the two pixels
    either side, plus half of the two neighbouring differences (an anti-aliased
    edge spread over 2 px gives one peak);
  * for a band of rows, the column profile is the mean of the clipped edge
    strength; all 319 x lines of the band are placed jointly by dynamic
    programming: score = profile at the line - mu * (distance to the coarser
    level's line)^2 - alpha * (distance to the uniform line beyond FREE px)^2,
    lines strictly ordered with a minimum cell width;
  * bands of 16, 8, 4, 2 and 1 cell rows, each level searching only +-t px around
    the coarser level; at the finest level every cell row has its own x lines
    (and every cell column its own y lines).
Verification: per region of REG x REG cells, the fraction of strong colour changes
(non-maximum-suppressed edge peaks) lying within 1 px of a cell border.
"""
import numpy as np, os, json
from scipy.ndimage import maximum_filter1d
from common import load_src, NX, NY, CACHE, OUT

TMAX = 4          # hard limit: a line never moves more than this from k * pitch
FREE = 1.5        # free movement before the uniform-anchor penalty starts
ALPHA = 3.0
CAP = 80.0        # clip edge strength so many edges count more than one huge edge
MINW = 4          # minimum cell width in source px
LEVELS = [(16, 3, 0.3), (8, 2, 0.5), (4, 2, 0.8), (2, 2, 1.0), (1, 1, 1.5)]  # (band cells, search t, mu)
REG = 8           # verification region size in cells
THR = 48.0        # a "strong colour change"


def edge_strength(a):
    """ex[y, b]: edge at border b (between pixel b-1 and b), b = 0..W (0 and W unused)."""
    f = a.astype(np.float32)
    dx = np.abs(np.diff(f, axis=1)).max(2)          # H x W-1, border b = index + 1
    dy = np.abs(np.diff(f, axis=0)).max(2)          # H-1 x W
    H, W = a.shape[:2]
    ex = np.zeros((H, W + 1), np.float32); ex[:, 1:W] = dx
    ey = np.zeros((H + 1, W), np.float32); ey[1:H] = dy
    ex2 = ex.copy(); ex2[:, 1:-1] += 0.5 * (ex[:, :-2] + ex[:, 2:])
    ey2 = ey.copy(); ey2[1:-1] += 0.5 * (ey[:-2] + ey[2:])
    return ex2, ey2


def dp_lines(prof, prior, base, t, mu):
    """prof: profile over border positions 0..L; prior, base: float arrays of n-1 lines."""
    L = len(prof) - 1
    n1 = len(prior)
    offs = np.arange(-t, t + 1)
    cand = np.round(prior).astype(int)[:, None] + offs[None, :]           # n1 x m
    valid = (np.abs(cand - base[:, None]) <= TMAX) & (cand >= 1) & (cand <= L - 1)
    dev = np.maximum(np.abs(cand - base[:, None]) - FREE, 0)
    sc_local = prof[np.clip(cand, 0, L)] - mu * (cand - prior[:, None]) ** 2 - ALPHA * dev ** 2
    sc_local = np.where(valid, sc_local, -1e9)
    # the line nearest the prior must stay feasible
    m = len(offs)
    S = sc_local[0].copy(); BP = np.zeros((n1, m), int)
    for k in range(1, n1):
        w = cand[k][:, None] - cand[k - 1][None, :]                       # m(cur) x m(prev)
        tot = S[None, :] + np.where(w >= MINW, 0.0, -1e9)
        BP[k] = tot.argmax(1)
        S = tot.max(1) + sc_local[k]
    j = int(S.argmax()); out = np.zeros(n1)
    for k in range(n1 - 1, -1, -1):
        out[k] = cand[k, j]; j = BP[k, j]
    return out


def fit_axis(e, n_lines_cells, n_band_cells, length, across):
    """e: edge strength with border axis last (rows x (length+1)). Returns per finest band lines."""
    base = np.arange(1, n_lines_cells) * length / n_lines_cells
    prior_rows = None
    for band, t, mu in LEVELS:
        nb = int(np.ceil(n_band_cells / band))
        res = np.zeros((nb, n_lines_cells - 1))
        for b in range(nb):
            c0, c1 = b * band, min(n_band_cells, (b + 1) * band)
            # profile rows: the band plus half a band either side (triangular weight)
            r0 = (c0 - band / 2) * across / n_band_cells; r1 = (c1 + band / 2) * across / n_band_cells
            rr = np.arange(max(0, int(r0)), min(across, int(np.ceil(r1))))
            mid = (r0 + r1) / 2; half = (r1 - r0) / 2
            wgt = np.clip(1.25 - np.abs(rr - mid) / half, 0, 1)[:, None]
            prof = (np.minimum(e[rr], CAP) * wgt).sum(0) / wgt.sum()
            if prior_rows is None:
                prior = base
            else:
                # prior: coarser solution for the cell rows of this band (mean)
                prior = prior_rows[c0:c1].mean(0)
            res[b] = dp_lines(prof, prior, base, t, mu)
        prior_rows = np.repeat(res, band, axis=0)[:n_band_cells]
    return prior_rows  # n_band_cells x (n_lines_cells - 1)


def build(a):
    H, W = a.shape[:2]
    ex, ey = edge_strength(a)
    XBi = fit_axis(ex, NX, NY, W, H)            # NY x 319 (x lines per cell row)
    YBi = fit_axis(ey.T, NY, NX, H, W)          # NX x 239 (y lines per cell column)
    XB = np.c_[np.zeros(NY), XBi, np.full(NY, W)].astype(int)
    YB = np.c_[np.zeros(NX), YBi, np.full(NX, H)].astype(int)
    return XB, YB


def uniform(H, W):
    XB = np.tile(np.round(np.arange(NX + 1) * W / NX), (NY, 1)).astype(int)
    YB = np.tile(np.round(np.arange(NY + 1) * H / NY), (NX, 1)).astype(int)
    return XB, YB


def index_maps(XB, YB, H, W):
    """I[y,x], J[y,x]: output cell of every source pixel."""
    xx = np.arange(W); yy = np.arange(H)
    i0 = np.minimum((xx * NX) // W, NX - 1)
    J = np.empty((H, W), np.int16)
    for x in range(W):
        J[:, x] = np.searchsorted(YB[i0[x]], yy, 'right') - 1
    J = np.clip(J, 0, NY - 1)
    I = np.empty((H, W), np.int16)
    for j in range(NY):
        m = J == j
        ys, xs = np.nonzero(m)
        I[ys, xs] = np.searchsorted(XB[j], xs, 'right') - 1
    I = np.clip(I, 0, NX - 1)
    # second pass for J with the refined column index
    for i in range(NX):
        m = I == i
        ys, xs = np.nonzero(m)
        J[ys, xs] = np.clip(np.searchsorted(YB[i], ys, 'right') - 1, 0, NY - 1)
    return I, J


def cell_boxes(XB, YB):
    jj, ii = np.mgrid[0:NY, 0:NX]
    x0 = XB[jj, ii]; x1 = XB[jj, ii + 1]
    y0 = YB[ii, jj]; y1 = YB[ii, jj + 1]
    return x0, x1, y0, y1


def verify(a, XB, YB, thr=THR, reg=REG, ex=None, ey=None):
    """Per region fraction of strong edge peaks within 1 px of a cell border."""
    H, W = a.shape[:2]
    if ex is None:
        ex, ey = edge_strength(a)
    pkx = (ex == maximum_filter1d(ex, 5, axis=1)) & (ex >= thr)
    pky = (ey == maximum_filter1d(ey, 5, axis=0)) & (ey >= thr)
    nr = (int(np.ceil(NY / reg)), int(np.ceil(NX / reg)))
    tot = np.zeros(nr); ok = np.zeros(nr)
    # x peaks: row y, border b. cell row from YB of the uniform column
    ys, bs = np.nonzero(pkx)
    i0 = np.minimum((np.minimum(bs, W - 1) * NX) // W, NX - 1)
    j = np.array([np.searchsorted(YB[i], y, 'right') - 1 for i, y in zip(i0, ys)]).clip(0, NY - 1)
    lines = XB[j]                                     # n x 321
    k = np.array([np.searchsorted(l, b) for l, b in zip(lines, bs)])
    d = np.minimum(np.abs(lines[np.arange(len(k)), np.clip(k, 0, NX)] - bs),
                   np.abs(lines[np.arange(len(k)), np.clip(k - 1, 0, NX)] - bs))
    ci = np.clip(np.searchsorted(XB[0], bs, 'right') - 1, 0, NX - 1)
    ci = np.clip(k - 1, 0, NX - 1)
    np.add.at(tot, (j // reg, ci // reg), 1); np.add.at(ok, (j // reg, ci // reg), d <= 1)
    xs, bs = np.nonzero(pky.T)
    j0 = np.minimum((np.minimum(bs, H - 1) * NY) // H, NY - 1)
    i = np.array([np.searchsorted(XB[jj], x, 'right') - 1 for jj, x in zip(j0, xs)]).clip(0, NX - 1)
    lines = YB[i]
    k = np.array([np.searchsorted(l, b) for l, b in zip(lines, bs)])
    d = np.minimum(np.abs(lines[np.arange(len(k)), np.clip(k, 0, NY)] - bs),
                   np.abs(lines[np.arange(len(k)), np.clip(k - 1, 0, NY)] - bs))
    cj = np.clip(k - 1, 0, NY - 1)
    np.add.at(tot, (cj // reg, i // reg), 1); np.add.at(ok, (cj // reg, i // reg), d <= 1)
    return ok / np.maximum(tot, 1), tot, ok.sum() / max(tot.sum(), 1)


def save_json(XB, YB, path, score=None, tot=None):
    x0, x1, y0, y1 = cell_boxes(XB, YB)
    d = {
        'about': 'FETCH! title regrid: local grid fit of title_original.png (2400x1792) to 320x240 cells. '
                 'x_borders[j] lists the 321 x positions (source px, border between pixel b-1 and b) of the cell '
                 'borders in cell row j; y_borders[i] lists the 241 y positions in cell column i. Cell (i, j) '
                 'covers x in [x_borders[j][i], x_borders[j][i+1]) and y in [y_borders[i][j], y_borders[i][j+1]). '
                 'cells_x0/x1/y0/y1 give the same boxes as 240 x 320 arrays (row j, column i).',
        'src_size': [2400, 1792], 'cells': [NX, NY],
        'x_borders': XB.tolist(), 'y_borders': YB.tolist(),
        'cells_x0': x0.tolist(), 'cells_x1': x1.tolist(), 'cells_y0': y0.tolist(), 'cells_y1': y1.tolist(),
    }
    if score is not None:
        d['verify'] = {'region_cells': REG, 'threshold': THR,
                       'score': np.round(score, 3).tolist(), 'edges': tot.astype(int).tolist()}
    with open(path, 'w') as f:
        json.dump(d, f, separators=(',', ':'))


def load(path=None):
    path = path or os.path.join(OUT, 'grid.json')
    d = json.load(open(path))
    return np.array(d['x_borders']), np.array(d['y_borders'])


def run(force=False):
    p = os.path.join(CACHE, 'grid_local.npz')
    if os.path.exists(p) and not force:
        z = np.load(p); return z['XB'], z['YB'], z['I'], z['J']
    a = load_src(); H, W = a.shape[:2]
    XB, YB = build(a)
    I, J = index_maps(XB, YB, H, W)
    np.savez_compressed(p, XB=XB, YB=YB, I=I, J=J)
    return XB, YB, I, J


if __name__ == '__main__':
    import sys
    a = load_src(); H, W = a.shape[:2]
    ex, ey = edge_strength(a)
    XU, YU = uniform(H, W)
    fu, tu, ou = verify(a, XU, YU, ex=ex, ey=ey)
    XB, YB, I, J = run(force=True)
    fr, tr, orr = verify(a, XB, YB, ex=ex, ey=ey)
    sig = tr >= 40
    print('uniform overall %.3f  median region %.3f' % (ou, np.median(fu[sig])))
    print('local   overall %.3f  median region %.3f  regions>=0.9: %d/%d  >=0.8: %d' % (
        orr, np.median(fr[sig]), (fr[sig] >= 0.9).sum(), sig.sum(), (fr[sig] >= 0.8).sum()))
    dx = XB[:, 1:-1] - np.arange(1, NX) * W / NX
    dy = YB[:, 1:-1] - np.arange(1, NY) * H / NY
    print('line deviation px: x mean %.2f max %.1f, y mean %.2f max %.1f' % (
        np.abs(dx).mean(), np.abs(dx).max(), np.abs(dy).mean(), np.abs(dy).max()))
    save_json(XB, YB, os.path.join(OUT, 'grid.json'), fr, tr)
