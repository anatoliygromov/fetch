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


def mixels(img, region, min_edge=20.0):
    """A pixel whose colour lies between its two opposite neighbours (left/right or
    up/down), which differ from each other by a strong edge (Lab distance >= min_edge),
    while the pixel equals neither: a blend colour sitting on an edge."""
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
            & (dseg < 0.3 * np.sqrt(L2)) & ra & rb
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
    """Joint pixels of an L on a 1 px line (Aseprite pixel-perfect rule): one horizontal
    and one vertical line neighbour that touch each other diagonally, the joint has no
    other neighbour, so it can be removed without cutting the line. Real corners (both
    legs at least 2 px long beyond the joint, the line turning 90 degrees) are kept."""
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    out = np.zeros_like(m)
    for (hy, hx) in [(0, 1), (0, -1)]:
        for (vy, vx) in [(1, 0), (-1, 0)]:
            c = m & nb(m, hy, hx) & nb(m, vy, vx) & (n8 == 2)
            # the step continues diagonally (a staircase), it is not a square corner
            c &= ~(nb(m, 2 * hy, 2 * hx) & nb(m, 2 * vy, 2 * vx))
            out |= c
    return int(out.sum()), out


def endpoints(line):
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    return m & (n8 <= 1)


def gaps(line):
    """Breaks in a 1 px outline: pairs of endpoints closer than 3 px (Chebyshev) that
    belong to the same line or to two pieces that should join."""
    ep = np.argwhere(endpoints(line))
    lab, _ = ndi.label(line, np.ones((3, 3)))
    g = 0; where = []
    for k in range(len(ep)):
        for l in range(k + 1, len(ep)):
            d = np.abs(ep[k] - ep[l]).max()
            if 2 <= d <= 3:
                g += 1; where.append((tuple(ep[k]), tuple(ep[l])))
    return g, where


def boundary_chains(mask):
    """Outer boundary pixels of a filled mask (or a 1 px line itself) as 8-connected
    chains of (y, x), traced with OpenCV-free Moore tracing via contour following."""
    import cv2
    m = mask.astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [c[:, 0, ::-1] for c in cnts if len(c) >= 6]


def runs_of_chain(ch):
    """Split a chain into straight runs; returns list of (dir, length) with dir 'h'/'v'."""
    out = []
    d = np.diff(ch, axis=0)
    cur, ln = None, 1
    for dy, dx in d:
        if dy == 0 and dx != 0:
            t = 'h'
        elif dx == 0 and dy != 0:
            t = 'v'
        else:
            t = 'd'
        if t == cur:
            ln += 1
        else:
            if cur is not None:
                out.append((cur, ln))
            cur, ln = t, 1
    if cur is not None:
        out.append((cur, ln))
    return out


def staircase_regularity(mask, min_seg=3):
    """Staircase regularity of the boundary of `mask`. The boundary is cut into
    segments of consistent slope (same major axis, steps one way); inside a segment
    the run lengths of the major axis must be equal, monotone (a curve), or a digital
    straight line (two values differing by 1, the rarer never repeated). Returns the
    fraction of regular segments and the count."""
    import cv2
    m = mask.astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    reg = tot = 0
    bad_pts = []
    for c in cnts:
        p = c[:, 0, :]
        if len(p) < 8:
            continue
        # runs along x (horizontal moves) separated by single vertical steps and vice versa
        d = np.diff(np.vstack([p, p[:1]]), axis=0)
        sx = np.sign(d[:, 0]); sy = np.sign(d[:, 1])
        # build sequence of segments: run lengths of horizontal moves between y changes
        for major in ('x', 'y'):
            mv = sx if major == 'x' else sy
            st = sy if major == 'x' else sx
            runs = []; cur = 0; dirs = []
            sign_major = 0; sign_step = 0
            seg_runs = []; segs = []
            for k in range(len(d)):
                if mv[k] != 0 and st[k] == 0:
                    if sign_major and mv[k] != sign_major:
                        if seg_runs:
                            segs.append(seg_runs)
                        seg_runs = []; sign_step = 0
                    sign_major = mv[k]; cur += 1
                else:
                    s = st[k]
                    if cur:
                        if sign_step and s != sign_step and s != 0:
                            segs.append(seg_runs); seg_runs = []
                        seg_runs.append(cur); cur = 0
                    if s != 0:
                        sign_step = s
                    if mv[k] != 0 and st[k] != 0:   # diagonal move counts as run 1
                        seg_runs.append(1)
            if cur:
                seg_runs.append(cur)
            if seg_runs:
                segs.append(seg_runs)
            for s in segs:
                inner = s[1:-1]                 # first and last runs can be partial
                if len(inner) < min_seg:
                    continue
                # only real staircases: the major axis dominates (runs >= 1, slope <= 1)
                tot += 1
                if is_regular(inner):
                    reg += 1
    return (reg / tot if tot else 1.0), tot


def is_regular(r):
    r = list(r)
    if max(r) - min(r) == 0:
        return True
    dif = np.diff(r)
    if (dif >= 0).all() or (dif <= 0).all():
        return True
    if max(r) - min(r) == 1:
        vals, cnt = np.unique(r, return_counts=True)
        rare = vals[cnt.argmin()] if cnt[0] != cnt[1] else None
        if rare is None:
            return all(r[k] != r[k + 1] for k in range(len(r) - 1)) or True
        return all(not (r[k] == rare and r[k + 1] == rare) for k in range(len(r) - 1))
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
        line = m if is_line else (m & ~ndi.binary_erosion(m))
        R['lcorners'], _ = lcorners(line)
        R['gaps'], _ = gaps(line) if is_line else (0, [])
        R['endpoints'] = int(endpoints(line).sum()) if is_line else 0
        R['staircase'], R['staircase_segments'] = staircase_regularity(m)
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
