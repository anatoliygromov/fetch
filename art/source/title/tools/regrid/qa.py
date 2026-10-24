#!/usr/bin/env python3
"""Reusable QA gates for the FETCH! title regrid (copy freely between tracks).

CLI:
  python3 -I qa.py result.png --palette palette.json [--mask m.png] [--src-mask s.png]
          [--region r.png] [--src title_original.png] [--grid grid.json] [--json out.json]

  result.png   320x240 RGB or RGBA (transparent pixels are ignored everywhere)
  --palette    JSON list of hex colours (or a dict of ramps; all values are used)
  --mask       320x240 mask of an outline / shape in the result (white = on)
               -> L-corner doubles, gaps, endpoints, staircase regularity
               -> with --src-mask also geometry IoU and boundary distance
  --src-mask   full resolution mask (2400x1792) of the same shape in the painting
  --region     320x240 mask restricting colour, form and pattern gates (default: opaque)
  --grid       grid.json (local grid); the form check then averages the painting per
               refined cell, else per uniform 7.5 x 7.467 cell

Gates (thresholds from the shared brief):
  off_palette == 0, mixels == 0, lcorners == 0, gaps == 0, staircase >= 0.9,
  iou >= 0.92, boundary_dist < 0.35 block, form mean < 3 and p95 < 8,
  checker phase == 1.0 (all checker pixels of a colour pair in one phase).
Module use: import qa; qa.off_palette(img, pal) ... every gate is a function.
Also: python3 -I qa.py --compare src_x0,src_y0,src_x1,src_y1 result.png out.png [--grid grid.json]
  writes a 10x side by side (original | result) of that source box.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

NX, NY = 320, 240
SRC_DEFAULT = '/home/claude/fetch/source_title/title_original.png'
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


# ---------------------------------------------------------------- helpers
def unhex(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_palette(path):
    d = json.load(open(path))
    if isinstance(d, dict):
        d = [h for v in d.values() for h in (v if isinstance(v, list) else [v])]
    return np.array(sorted(set(unhex(h) for h in d)), np.uint8)


def load_img(path):
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    return a[..., :3], a[..., 3] > 127


def load_mask(path, shape=None):
    m = np.array(Image.open(path).convert('L')) > 127
    if shape is not None and m.shape != shape:
        raise SystemExit('mask %s has shape %s, expected %s' % (path, m.shape, shape))
    return m


def srgb_to_lab(rgb):
    c = np.asarray(rgb, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = (c @ M.T) / np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def luma(rgb):
    return np.asarray(rgb, np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def shift(m, dy, dx, fill=False):
    out = np.full_like(m, fill)
    H, W = m.shape[:2]
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


def keys(img):
    c = img.astype(np.int64)
    return (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]


# ---------------------------------------------------------------- colour gates
def off_palette(img, pal, region):
    pk = set(keys(pal[None])[0].tolist())
    k = keys(img)
    bad = region & ~np.isin(k, list(pk))
    return int(bad.sum()), bad


def run3(k, ax):
    """Pixel lies in a run of >= 3 equal values along axis ax."""
    def sh(d):
        return shift(k, d if ax == 0 else 0, d if ax == 1 else 0, -1)
    p1 = sh(1) == k; m1 = sh(-1) == k
    p2 = sh(2) == k; m2 = sh(-2) == k
    return (p1 & m1) | (p1 & p2) | (m1 & m2)


def mixels(img, region, min_edge=20.0):
    """A pixel whose colour lies between its two opposite neighbours (left/right or
    up/down), which differ from each other by a strong edge (Lab distance >= min_edge),
    while the pixel equals neither: a blend colour sitting on an edge. A pixel that is
    part of a run of 3 or more same-coloured pixels ALONG the edge is a band (a deck
    stripe, a rim light), not a mixel."""
    lab = srgb_to_lab(img); k = keys(img)
    out = np.zeros(k.shape, bool)
    for ax in (0, 1):
        a = np.roll(lab, 1, ax); b = np.roll(lab, -1, ax)
        ka = np.roll(k, 1, ax); kb = np.roll(k, -1, ax)
        ra = np.roll(region, 1, ax); rb = np.roll(region, -1, ax)
        ab = b - a; L2 = (ab ** 2).sum(-1)
        t = ((lab - a) * ab).sum(-1) / np.maximum(L2, 1e-6)
        dseg = np.linalg.norm(lab - (a + t[..., None] * ab), axis=-1)
        m = (ka != kb) & (k != ka) & (k != kb) & (np.sqrt(L2) >= min_edge) & (t > 0.12) & (t < 0.88) \
            & (dseg < 0.3 * np.sqrt(L2)) & ra & rb & ~run3(k, 1 - ax)
        if ax == 0:
            m[0] = m[-1] = False
        else:
            m[:, 0] = m[:, -1] = False
        out |= m
    out &= region
    return int(out.sum()), out


def specks(img, region):
    """Isolated pixels: a colour that none of the 8 neighbours shares (informative noise count)."""
    k = keys(img)
    same = sum((shift(k, dy, dx, -1) == k).astype(int) for dy, dx in N8)
    m = region & (same == 0)
    m[0] = m[-1] = False; m[:, 0] = m[:, -1] = False
    return int(m.sum()), m


# ---------------------------------------------------------------- line gates
def nb(m, dy, dx):
    return shift(m, dy, dx)


def lcorners(line):
    """Corner doubles on a 1 px line (the Aseprite pixel-perfect rule): a pixel with
    exactly one horizontal and exactly one vertical line neighbour. Those two touch
    diagonally, so the pixel can go without breaking the line. A deliberate square
    corner (both legs run straight on for 2 more pixels) is not counted."""
    m = line.astype(bool)
    L, Rt, U, D = nb(m, 0, -1), nb(m, 0, 1), nb(m, -1, 0), nb(m, 1, 0)
    out = np.zeros_like(m)
    for h, hx in ((L, -1), (Rt, 1)):
        oh = Rt if hx == -1 else L
        for v, vy in ((U, -1), (D, 1)):
            ov = D if vy == -1 else U
            c = m & h & v & ~oh & ~ov
            c &= ~(nb(m, 0, 2 * hx) & nb(m, 2 * vy, 0) & ~nb(m, -vy, -hx))
            out |= c
    # the two pixels of one L both qualify: count each L once (4-connected pieces)
    n = ndi.label(out)[1]
    return int(n), out


def endpoints(line):
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    return m & (n8 <= 1)


def gaps(line):
    """Breaks in a 1 px line: two endpoints of DIFFERENT line pieces, 2 to 3 px apart
    (Chebyshev), each pointing at the other within about 36 degrees (the line would
    continue across the gap).
    Parallel lines and the two ends of one short line are not gaps."""
    m = line.astype(bool)
    ep = np.argwhere(endpoints(m))
    lab, _ = ndi.label(m, np.ones((3, 3)))
    def outward(p):
        y, x = p
        for dy, dx in N8:
            yy, xx = y + dy, x + dx
            if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx]:
                return np.array([-dy, -dx], float)
        return None
    g = 0; where = []
    for k in range(len(ep)):
        for l in range(k + 1, len(ep)):
            p, q = ep[k], ep[l]
            d = np.abs(p - q).max()
            if not (2 <= d <= 3) or lab[tuple(p)] == lab[tuple(q)]:
                continue
            dp, dq = outward(p), outward(q)
            v = (q - p).astype(float); v /= np.linalg.norm(v)
            if dp is None or dq is None:
                continue
            if (dp @ v) / np.linalg.norm(dp) >= 0.8 and (dq @ -v) / np.linalg.norm(dq) >= 0.8:
                g += 1; where.append((tuple(p), tuple(q)))
    return g, where


DIRS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # (dy, dx), 45 deg steps


def boundary_chains(mask):
    """Boundary pixel chains of a mask (8-connected, OpenCV contour following), as (y, x)."""
    import cv2
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [c[:, 0, ::-1] for c in cnts if len(c) >= 6]


def line_chains(line):
    """Ordered pixel chains of a 1 px line (walks from each endpoint; loops from any pixel)."""
    m = line.astype(bool).copy()
    H, W = m.shape
    seen = np.zeros_like(m)
    def nbrs(p):
        y, x = p
        out = []
        for dy, dx in N4 + N8[4:]:          # orthogonal neighbours first
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                out.append((yy, xx))
        return out
    chains = []
    starts = [tuple(p) for p in np.argwhere(endpoints(m))] + [tuple(p) for p in np.argwhere(m)]
    for s0 in starts:
        if seen[s0]:
            continue
        ch = [s0]; seen[s0] = True
        while True:
            nb_ = nbrs(ch[-1])
            if not nb_:
                break
            ch.append(nb_[0]); seen[nb_[0]] = True
        if len(ch) >= 6:
            chains.append(np.array(ch))
    return chains


def chain_segments(ch, closed=True):
    """Cut a boundary chain into staircase segments. A segment uses only one axis
    direction A and one diagonal D next to it (45 deg apart); its run lengths are the
    numbers of pixels in each A run (between D steps). Returns lists of run lengths."""
    pts = np.vstack([ch, ch[:1]]) if closed else ch
    mv = []
    for d in np.diff(pts, axis=0):
        t = (int(np.sign(d[0])), int(np.sign(d[1])))
        if t in DIRS:
            mv.append(DIRS.index(t))
    segs, cur, pair, run = [], [], None, 0
    def close():
        if cur:
            segs.append(cur[:])
    for m in mv:
        if pair is None:
            pair = {m}; run = 1 if m % 2 == 0 else 0
            if m % 2 == 1:
                cur.append(1)
            continue
        cand = pair | {m}
        ok = len(cand) <= 2 and (len(cand) < 2 or (abs(list(cand)[0] - list(cand)[1]) in (1, 7)))
        if not ok:
            if run:
                cur.append(run + 1)
            close(); cur = []; pair = {m}; run = 1 if m % 2 == 0 else 0
            continue
        pair = cand
        if m % 2 == 0:
            run += 1
        else:
            cur.append(run + 1 if run else 1); run = 0
    if run:
        cur.append(run + 1)
    close()
    return segs


def staircase_regularity(mask, win=3, line=False):
    """Staircase regularity of the boundary of `mask`: the boundary is cut into staircase
    segments (one axis direction plus the diagonal next to it); every window of `win`
    consecutive run lengths inside a segment (first and last runs dropped, they can be
    cut short) counts as one segment piece, regular when its runs are equal, monotone
    (a curve) or within one of each other (a digital straight line such as 2,3,2).
    A jaggy such as 1,3,1 or 3,1,2 is irregular.
    Returns (fraction regular, number of windows, list of irregular windows)."""
    reg = tot = 0; bad = []
    chains = [(c, False) for c in line_chains(mask)] if line else [(c, True) for c in boundary_chains(mask)]
    for ch, closed in chains:
        for runs in chain_segments(ch, closed):
            inner = runs[1:-1]
            for k in range(len(inner) - win + 1):
                w = inner[k:k + win]
                tot += 1
                if is_regular(w):
                    reg += 1
                else:
                    bad.append(w)
    return (reg / tot if tot else 1.0), tot, bad


def is_regular(r):
    r = list(r)
    if max(r) - min(r) == 0:
        return True
    dif = np.diff(r)
    if (dif >= 0).all() or (dif <= 0).all():
        return True
    if max(r) - min(r) == 1:
        return True
    return False


# ---------------------------------------------------------------- geometry gates
def upscale_mask(m320, shape):
    H, W = shape
    yi = np.minimum((np.arange(H) * NY) // H, NY - 1)
    xi = np.minimum((np.arange(W) * NX) // W, NX - 1)
    return m320[yi[:, None], xi[None, :]]


def geometry(m320, src_mask):
    """IoU of the result mask re-upscaled (uniformly) to the painting vs the painting's
    mask, and the mean symmetric boundary distance in blocks (7.5 px)."""
    up = upscale_mask(m320, src_mask.shape)
    inter = (up & src_mask).sum(); uni = (up | src_mask).sum()
    iou = inter / max(uni, 1)
    def bnd(m):
        return m & ~ndi.binary_erosion(m)
    b1, b2 = bnd(up), bnd(src_mask)
    if b1.sum() == 0 or b2.sum() == 0:
        return float(iou), float('inf')
    d2 = ndi.distance_transform_edt(~b2); d1 = ndi.distance_transform_edt(~b1)
    md = 0.5 * (d2[b1].mean() + d1[b2].mean()) / (src_mask.shape[1] / NX)
    return float(iou), float(md)


# ---------------------------------------------------------------- form and pattern
def cell_means(src, grid=None):
    H, W = src.shape[:2]
    if grid is not None:
        d = json.load(open(grid))
        x0 = np.array(d['cells_x0']); x1 = np.array(d['cells_x1'])
        y0 = np.array(d['cells_y0']); y1 = np.array(d['cells_y1'])
    else:
        xs = np.round(np.arange(NX + 1) * W / NX).astype(int); ys = np.round(np.arange(NY + 1) * H / NY).astype(int)
        x0 = np.tile(xs[:-1], (NY, 1)); x1 = np.tile(xs[1:], (NY, 1))
        y0 = np.tile(ys[:-1, None], (1, NX)); y1 = np.tile(ys[1:, None], (1, NX))
    lum = luma(src)
    S = np.zeros((H + 1, W + 1)); S[1:, 1:] = lum.cumsum(0).cumsum(1)
    tot = S[y1, x1] - S[y0, x1] - S[y1, x0] + S[y0, x0]
    return tot / np.maximum((x1 - x0) * (y1 - y0), 1)


def form(img, region, src=None, grid=None):
    """5x5 box blur of luma, result vs the painting averaged per cell, over region."""
    src = src if src is not None else np.array(Image.open(SRC_DEFAULT).convert('RGB'))
    ref = cell_means(src, grid)
    res = luma(img)
    k = np.ones((5, 5)) / 25.0
    d = np.abs(ndi.convolve(res, k, mode='nearest') - ndi.convolve(ref, k, mode='nearest'))
    v = d[region]
    return float(v.mean()), float(np.percentile(v, 95)), d


def checker_phase(img, region, min_pair=8):
    """Checker pixels: all four 4-neighbours share one other colour B and the four
    diagonals share the pixel's colour A. Per (A, B) pair, the fraction of A pixels
    on the majority parity of (x + y), over pairs with at least min_pair checker
    pixels (a dither band, not an accidental single pixel). Returns the worst pair fraction and the count."""
    k = keys(img)
    n = [shift(k, dy, dx, -1) for dy, dx in N4]
    d = [shift(k, dy, dx, -1) for dy, dx in N8[4:]]
    chk = region & (n[0] == n[1]) & (n[1] == n[2]) & (n[2] == n[3]) & (n[0] != k) & \
        (d[0] == k) & (d[1] == k) & (d[2] == k) & (d[3] == k)
    yy, xx = np.mgrid[0:k.shape[0], 0:k.shape[1]]
    par = (yy + xx) % 2
    res = {}
    for A, B, p in zip(k[chk], n[0][chk], par[chk]):
        pair = (min(A, B), max(A, B))
        sideA = (A == pair[0])
        r = res.setdefault(pair, [0, 0]); r[int(p ^ (0 if sideA else 1))] += 1
    res = {p: v for p, v in res.items() if sum(v) >= min_pair}
    if not res:
        return 1.0, 0
    worst = min(max(v) / sum(v) for v in res.values())
    return float(worst), int(sum(sum(v) for v in res.values()))


# ---------------------------------------------------------------- compare image
def compare(box, result_path, out_path, scale=10, grid=None, src=None):
    """10x side by side: the painting box (resampled so one cell = `scale` px) | result."""
    src = src if src is not None else np.array(Image.open(SRC_DEFAULT).convert('RGB'))
    H, W = src.shape[:2]
    x0, y0, x1, y1 = box
    i0, i1 = int(np.floor(x0 * NX / W)), int(np.ceil(x1 * NX / W))
    j0, j1 = int(np.floor(y0 * NY / H)), int(np.ceil(y1 * NY / H))
    res = np.array(Image.open(result_path).convert('RGB'))[j0:j1, i0:i1]
    rw, rh = (i1 - i0) * scale, (j1 - j0) * scale
    sx0, sx1 = i0 * W / NX, i1 * W / NX; sy0, sy1 = j0 * H / NY, j1 * H / NY
    crop = Image.fromarray(src).crop((int(round(sx0)), int(round(sy0)), int(round(sx1)), int(round(sy1))))
    left = np.array(crop.resize((rw, rh), Image.NEAREST))
    right = np.array(Image.fromarray(res).resize((rw, rh), Image.NEAREST))
    gap = np.full((rh, 6, 3), 255, np.uint8)
    Image.fromarray(np.hstack([left, gap, right])).save(out_path)


# ---------------------------------------------------------------- run all
def run_all(result, palette, mask=None, src_mask=None, region=None, src=None, grid=None):
    img, alpha = load_img(result)
    pal = load_palette(palette)
    reg = alpha.copy()
    if region:
        reg &= load_mask(region, alpha.shape)
    R = {}
    R['off_palette'], _ = off_palette(img, pal, reg)
    R['mixels'], _ = mixels(img, reg)
    R['specks'], _ = specks(img, reg)
    s = np.array(Image.open(src).convert('RGB')) if src else None
    R['form_mean'], R['form_p95'], _ = form(img, reg, s, grid)
    R['checker_phase'], R['checker_pixels'] = checker_phase(img, reg)
    if mask:
        m = load_mask(mask, alpha.shape)
        thin = m & ~ndi.binary_erosion(m, np.ones((3, 3)))
        is_line = thin.sum() >= 0.9 * m.sum()
        if is_line:                          # a 1 px outline or stroke
            R['lcorners'], _ = lcorners(m)
            R['gaps'], _ = gaps(m)
            R['endpoints'] = int(endpoints(m).sum())
        R['staircase'], R['staircase_segments'], _ = staircase_regularity(m, line=is_line)
        if src_mask:
            sm = np.array(Image.open(src_mask).convert('L')) > 127
            R['iou'], R['boundary_dist'] = geometry(m, sm)
    R['pass'] = gate_pass(R)
    return R


def gate_pass(R):
    p = {'off_palette': R['off_palette'] == 0, 'mixels': R['mixels'] == 0,
         'form': R['form_mean'] < 3 and R['form_p95'] < 8, 'checker': R['checker_phase'] >= 1.0}
    if 'lcorners' in R:
        p['lcorners'] = R['lcorners'] == 0; p['gaps'] = R['gaps'] == 0
    if 'staircase' in R:
        p['staircase'] = R['staircase'] >= 0.9
    if 'iou' in R:
        p['geometry'] = R['iou'] >= 0.92 and R['boundary_dist'] < 0.35
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('result', nargs='?')
    ap.add_argument('--palette')
    ap.add_argument('--mask'); ap.add_argument('--src-mask'); ap.add_argument('--region')
    ap.add_argument('--src'); ap.add_argument('--grid'); ap.add_argument('--json')
    ap.add_argument('--compare', nargs=3, metavar=('BOX', 'RESULT', 'OUT'))
    a = ap.parse_args(argv)
    if a.compare:
        box = tuple(int(v) for v in a.compare[0].split(','))
        compare(box, a.compare[1], a.compare[2], grid=a.grid)
        return
    R = run_all(a.result, a.palette, a.mask, a.src_mask, a.region, a.src, a.grid)
    for k, v in R.items():
        print('%-20s %s' % (k, v))
    if a.json:
        json.dump(R, open(a.json, 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
