"""Pilot: the tagline plate and its text, two colours for the text (cream on navy).

Plate: outer silhouette and the shape inside the light-blue line are rasterized as
smoothed shapes; the light-blue line is the 1 px inner ring of the second one
(L-corners removed on the chamfers). Text: each glyph's centre line (skeleton of
the painted glyph) is put on the grid, so every stroke is exactly 1 px wide; the
glyphs of a repeated letter are then replaced by one canonical bitmap (the most
common one among its instances), so the same letter is identical everywhere.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, thin
from shapes import raster_shape, clean_mask
from lines import ring, remove_lcorners, isolated
from common import NX, NY

NAVYP, LINE, CREAM = 8, 33, 3
TEXTSET = [3, 64]
PLATESET = [8, 33, 3, 64, 13, 78]
TEXT = "TheCityDogAdventurer"


def region(H, W):
    R = np.zeros((H, W), bool); R[566:742, 1100:2200] = True
    return R


def build(L, I, J, pal, out, owner):
    H, W = L.shape
    R = region(H, W)
    M = np.isin(L, [NAVYP] + TEXTSET) & R
    lab, n = ndi.label(M)
    c = np.bincount(lab[620:680, 1500:1800].ravel()); c[0] = 0
    INNER = ndi.binary_fill_holes(lab == c.argmax())          # navy inside the light-blue line
    TXT = np.isin(L, TEXTSET) & INNER
    LINEM = ndi.binary_dilation(INNER, np.ones((11, 11))) & ~INNER   # the painted line band, for QA
    PALL = clean_mask(np.isin(L, PLATESET) & R, 400)
    OUTERP = ndi.binary_fill_holes(PALL | INNER | LINEM)
    outerP, _ = raster_shape(OUTERP, I, J, s=8.0)
    inner, _ = raster_shape(INNER, I, J, s=8.0)
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    line = ndi.binary_dilation(inner, cross) & ~inner
    line = remove_lcorners(line)
    outerP |= line | inner
    inl = inner | line
    out[outerP] = NAVYP
    out[line] = LINE
    interior = inner
    txt, info = glyphs(TXT, I, J, interior)
    out[txt] = CREAM
    owner[outerP] = 2
    return dict(outer=outerP, inner=inner, line=line, text=txt, OUTER=OUTERP, INNER=INNER, LINEM=LINEM, TXT=TXT, info=info)


def glyph_bitmap(gm, I, J, x0, x1, ncols):
    """Sample one glyph on its own column grid (ncols equal columns across its painted width)
    and the output rows; a sub-cell is on when the glyph covers at least half of it."""
    ys, xs = np.nonzero(gm)
    col = np.clip(((xs - x0) * ncols) // max(1, (x1 - x0)), 0, ncols - 1)
    rows = J[ys, xs]
    r0, r1 = rows.min(), rows.max()
    on = np.zeros((r1 - r0 + 1, ncols))
    np.add.at(on, (rows - r0, col), 1)
    # sub-cell areas
    yy = np.arange(gm.shape[0])[:, None]
    area = np.zeros_like(on)
    band = np.zeros(gm.shape[1], bool); band[x0:x1] = True
    cols_all = np.clip(((np.arange(gm.shape[1]) - x0) * ncols) // max(1, (x1 - x0)), 0, ncols - 1)
    for r in range(r0, r1 + 1):
        rowsel = (J[:, x0:x1] == r)
        cnt = rowsel.sum(0)                                     # pixels of this row per source column
        area[r - r0] = np.bincount(cols_all[x0:x1], weights=cnt, minlength=ncols)
    bm = on / np.maximum(area, 1) >= 0.45
    return bm, r0


def glyphs(TXT, I, J, interior):
    lab, n = ndi.label(TXT)
    objs = ndi.find_objects(lab)
    sz = ndi.sum(TXT, lab, range(1, n + 1))
    comps = [(o[1].start, o[1].stop, i + 1) for i, o in enumerate(objs) if sz[i] >= 20]
    comps.sort()
    # merge components that overlap in x (the dot of the i)
    groups = []
    for x0, x1, c in comps:
        if groups and x0 < groups[-1][1] - 2:
            groups[-1][1] = max(groups[-1][1], x1); groups[-1][2].append(c)
        else:
            groups.append([x0, x1, [c]])
    out = np.zeros((NY, NX), bool)
    bms = []
    for x0, x1, cs in groups:
        gm = np.isin(lab, cs)
        ncols = max(2, int(round((x1 - x0) / 8.25)))
        bm, r0 = glyph_bitmap(gm, I, J, x0, x1, ncols)
        full = np.zeros((NY, NX), bool)
        c0 = int(round(x0 / (gm.shape[1] / NX)))
        full[r0:r0 + bm.shape[0], c0:c0 + bm.shape[1]] = bm
        ys, xs = np.nonzero(full)
        bms.append((full, (ys.min(), xs.min(), ys.max(), xs.max())))
    info = dict(n_glyphs=len(groups), text_ok=len(groups) == len(TEXT))
    if len(groups) != len(TEXT):
        for bm, _ in bms:
            out |= bm
        return out, info
    # canonical bitmap per letter: crop each instance relative to the baseline row and its left column
    base = max(b[1][2] for b, ch in zip(bms, TEXT) if ch in 'TheCiDAdvnur')  # baseline row
    crops = {}
    for (bm, bb), ch in zip(bms, TEXT):
        y0, x0, y1, x1 = bb
        top = base - 8
        crops.setdefault(ch, []).append((bm[top:base + 3, x0:x1 + 1].copy(), x0))
    chosen = {}
    for ch, inst in crops.items():
        keys = {}
        for c, x0 in inst:
            k = (c.shape, c.tobytes()); keys.setdefault(k, []).append(c)
        best = max(keys.values(), key=len)[0]
        chosen[ch] = best
    info['instances'] = {ch: len(v) for ch, v in crops.items()}
    info['variants'] = {ch: len({(c.shape, c.tobytes()) for c, _ in v}) for ch, v in crops.items()}
    for (bm, bb), ch in zip(bms, TEXT):
        c = chosen[ch]; x0 = bb[1]; top = base - 8
        h, w = c.shape
        out[top:top + h, x0:x0 + w] |= c
    out &= interior
    return out, info
