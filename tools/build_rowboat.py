#!/usr/bin/env python3
"""build_rowboat.py: the rowing boat at real size (round 2, 25 Oct 2026; owner: "do you see the size of the boats?",
then "go" on real size, about 160 px, with wider harbours).

Sources (SpriteCook, art/gen/renders/):
  rw_rowboat_b.png          NB 2.1 still on the blockout (a grown man rowing a wooden boat, Pepper beside it for
                            scale); cut 1:1 (pitch 1: the dog came out at Pepper's 52 px), magenta keyed, the dog
                            dropped, 17 colours (k-means in Lab, each colour a real pixel of the render), one ink,
                            lone pixels merged: art/gen/out/rw_rowboat.png, 182 x 95, the hull 182 long
  rw_rowboat_row_sheet.png  pixel-engine-v1.5 from that cut, 8 frames 222 x 222 at 1x (hull still 182)
Only the stroke frames 1-3 are used (4 broke the blade at the bow, 5-6 drew the oars doubled over the hull, 7
left a blue streak): they play 1 1 2 3 3 3 2 1, a pull and return. Every frame is the clean cut with the frame's moving parts laid on it:
the frame is snapped to the cut's 17 colours, and only the changes that belong to the man and his oar are kept
(a change kept must reach outside the boat's own outline or into the man's box); small changes on the hull (the
animator's noise on the gunwale and planks) and the white splash under the waterline are dropped. So the hull is
pixel-identical in every frame and nothing flickers.
Out: riverwalk/art/scene/rowboat.png, 8 cells of CELL, the rower at the right of the middle facing right, the
hull's bottom on row HULL_BOTTOM; the deck (where Pepper stands) is the gunwale's top row, DECK_ROW, over x
DECK_X0-DECK_X1 of the cell."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_palette import lab

SRC = 'art/gen/out/rw_rowboat.png'
SHEET = 'art/gen/renders/rw_rowboat_row_sheet.png'
FW = 222
ORDER = [1, 1, 2, 3, 3, 3, 2, 1]
PAD = 4                                  # columns of room left and right of the hull in each cell


def merge_blotches(f):
    """the clean pass for 'dirty fill' (tools/asset_qa.py blotches): a 2-24 px patch of one colour sitting inside a
    near colour (distance under 45, the patch's ring at least 80 % that colour) takes that colour. Drawn 1 px lines
    (4 px or longer) stay, as the check allows them. Repeated until nothing changes."""
    for _ in range(4):
        al = f[..., 3] > 0
        key = (f[..., 0].astype(int) << 16) | (f[..., 1].astype(int) << 8) | f[..., 2]
        key[~al] = -1; changed = 0
        for k in np.unique(key[al]):
            lbl, n = ndimage.label(key == k)
            if not n: continue
            sizes = np.bincount(lbl.ravel())
            for i in range(1, n + 1):
                if not (2 <= sizes[i] <= 24): continue
                mm = lbl == i
                ys_, xs_ = np.nonzero(mm)
                if min(np.ptp(ys_), np.ptp(xs_)) == 0 and max(np.ptp(ys_), np.ptp(xs_)) >= 3: continue
                pm = np.pad(mm, 1)
                ring = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & ~mm
                rk = key[ring]
                if (rk < 0).any(): continue
                vals, cnt = np.unique(rk, return_counts=True)
                if cnt.max() / cnt.sum() < 0.8: continue
                o = int(vals[cnt.argmax()])
                oc = np.array([(o >> 16) & 255, (o >> 8) & 255, o & 255])
                kc = np.array([(int(k) >> 16) & 255, (int(k) >> 8) & 255, int(k) & 255])
                if np.sqrt(((oc - kc) ** 2).sum()) < 45:
                    f[mm, :3] = oc; changed += 1
        if not changed: break
    return f


def main():
    src = np.array(Image.open(SRC).convert('RGBA'))
    sh, sw = src.shape[:2]
    pal = np.unique(src[src[..., 3] > 0][:, :3], axis=0)
    sheet = np.array(Image.open(SHEET).convert('RGBA'))
    # where the cut sits in each animation frame: frame 1's box (the source pose, hull unchanged)
    f1 = sheet[:, :FW, 3] >= 128
    ys, xs = np.nonzero(f1)
    ox, oy = xs.min(), ys.max() - (sh - 1)
    assert xs.max() - xs.min() + 1 == sw, 'the animated hull is not 1x'
    salpha = src[..., 3] > 0
    # the gunwale: per column, the hull's top (ink) row, read where nothing stands above it; across the man and the
    # oar (x MAN0-MAN1) it runs straight between its neighbours
    gun = np.zeros(sw, int)
    for x in range(sw):
        ys_ = np.nonzero(salpha[:, x])[0]; gun[x] = ys_.min()
    MAN0, MAN1 = 56, 120
    gun[MAN0:MAN1] = np.round(np.interp(np.arange(MAN0, MAN1), [MAN0 - 1, MAN1], [gun[MAN0 - 1], gun[MAN1]])).astype(int)
    hull_bottom = np.array([np.nonzero(salpha[:, x])[0].max() if x < 24 or x > 40 else 0 for x in range(sw)])
    water = int(np.median(hull_bottom[60:160]))                   # the hull's flat bottom row (the waterline)
    rows_i, cols_i = np.mgrid[0:sh, 0:sw]
    above = rows_i < gun[None, :]
    below = rows_i > water
    sheet = np.pad(sheet, ((0, 8), (0, 8), (0, 0)))
    Ls = lab(src[..., :3].reshape(-1, 3).astype(float)).reshape(sh, sw, 3)
    reg = salpha & (rows_i > gun[None, :] + 1) & (rows_i <= water) & (cols_i > 124)   # plain hull, for the offset

    def frame(k):
        """frame k on the cut's grid (its hull lined up with the cut's), snapped to the cut's colours"""
        best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                fr = sheet[oy + dy:oy + dy + sh, (k - 1) * FW + ox + dx:(k - 1) * FW + ox + dx + sw].astype(float)
                e = np.sqrt(((lab(fr[..., :3].reshape(-1, 3)).reshape(sh, sw, 3) - Ls) ** 2).sum(2))[reg].mean()
                if best is None or e < best[0]: best = (e, dx, dy)
        _, dx, dy = best
        big = np.zeros((sh + 2 * M, sw + 2 * M, 4), np.uint8)       # with room around for the blade and splash
        y0, x0 = oy + dy - M, (k - 1) * FW + ox + dx - M
        for yy in range(big.shape[0]):
            sy = y0 + yy
            if 0 <= sy < sheet.shape[0]:
                a, b = max((k - 1) * FW, x0), min(k * FW, x0 + big.shape[1])
                big[yy, a - x0:b - x0] = sheet[sy, a:b]
        al = big[..., 3] >= 128
        big[..., 3] = np.where(al, 255, 0); big[~al] = 0
        px = big[al][:, :3].astype(float)
        idx = np.argmin(((lab(px)[:, None] - lab(pal.astype(float))[None]) ** 2).sum(2), 1)
        big[al, :3] = pal[idx]
        return big, (dx, dy)

    def oar_mask(big):
        """the oar: a straight shaft from the hands to the blade. Its pixels outside the hull (above the gunwale left
        of the man, or under the hull or past its bow) give the line; the mask is every pixel within 3 px of it"""
        al = big[..., 3] > 0
        H2, W2 = al.shape
        r, c = np.mgrid[0:H2, 0:W2]
        gx = np.clip(c - M, 0, sw - 1)
        abv = (r - M < gun[gx]) & (c - M < 76)
        bel = (r - M > water) | (c - M < 0)
        wood = (big[..., 0].astype(int) > big[..., 2] + 40)
        pts = np.argwhere(al & wood & (abv | bel))
        if len(pts) < 10: return np.zeros_like(al)
        mu = pts.mean(0); u = np.linalg.svd(pts - mu)[2][0]
        t = (pts - mu) @ u; t0, t1 = t.min() - 1, t.max() + 1
        P = np.stack([r, c], -1).reshape(-1, 2) - mu
        tt = P @ u; d = np.abs(P @ np.array([-u[1], u[0]]))
        m = ((d <= 3.0) & (tt >= t0) & (tt <= t1)).reshape(H2, W2)
        return m

    def oar_core(big):
        """the shaft's middle line (within 1.2 px of the oar's axis), above the waterline"""
        al = big[..., 3] > 0
        H2, W2 = al.shape
        r, c = np.mgrid[0:H2, 0:W2]
        gx = np.clip(c - M, 0, sw - 1)
        abv = (r - M < gun[gx]) & (c - M < 76)
        bel = (r - M > water) | (c - M < 0)
        wood = (big[..., 0].astype(int) > big[..., 2] + 40)
        pts = np.argwhere(al & wood & (abv | bel))
        if len(pts) < 10: return np.zeros_like(al)
        mu = pts.mean(0); u = np.linalg.svd(pts - mu)[2][0]
        t = (pts - mu) @ u; t0, t1 = t.min() - 1, t.max() + 1
        P = np.stack([r, c], -1).reshape(-1, 2) - mu
        tt = P @ u; d = np.abs(P @ np.array([-u[1], u[0]]))
        return ((d <= 1.2) & (tt >= t0) & (tt <= t1)).reshape(H2, W2) & (r - M <= water)

    M = 24
    src = src.copy()
    if tuple(src[57, 55, :3]) == (214, 213, 218): src[57, 55, :3] = (251, 219, 170)   # review B3: a grey speck in the sand row
    hull = src.copy(); hull[above | below] = 0                         # the hull alone: under the gunwale, over the waterline
    hull = merge_blotches(hull)                                        # its clean pass, once (identical in every frame)
    base = np.zeros((sh + 2 * M, sw + 2 * M, 4), np.uint8); base[M:M + sh, M:M + sw] = hull
    bal = base[..., 3] > 0
    srcb = np.zeros_like(base); srcb[M:M + sh, M:M + sw] = src
    src_oar = oar_mask(srcb)
    above_b = np.zeros_like(bal); above_b[M:M + sh, M:M + sw] = above
    below_b = np.ones_like(bal); below_b[M:M + sh, M:M + sw] = below
    man_cols = np.zeros_like(bal); man_cols[:, M + MAN0:M + MAN1 + 2] = True
    ink = np.array([24, 20, 24], np.uint8)
    outs, moving = {}, {}
    for k in sorted(set(ORDER)):
        big, off = frame(k)
        oar = oar_mask(big)
        # what comes from the animation: the man (above the gunwale, over his own columns), the oar now and where the
        # source's oar was (the hull under it as the animator drew it), nothing else: the gunwale, bow and stern stay
        # the clean hull's pixels in every frame (review B1, B2)
        left = np.zeros_like(bal); left[:, :M] = True
        take = (above_b & man_cols) | oar | src_oar | (below_b & ~bal) | left   # (+ the blade under the waterline or past the bow)
        light = (big[..., :3].astype(float) @ [0.299, 0.587, 0.114]) > 170
        take &= ~(below_b & light)                                    # no white splash under the waterline
        out = base.copy(); out[take] = big[take]
        # the oar's grain (review B4): the seat's grey-brown dithered into the shaft and blade takes the oar's own
        # neighbouring wood colour
        grey = take & oar & (out[..., :3] == (85, 67, 57)).all(2)
        for y, x in zip(*np.nonzero(grey)):
            nb = [tuple(out[yy, xx, :3]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                  if (yy, xx) != (y, x) and out[yy, xx, 3] and tuple(out[yy, xx, :3]) not in ((85, 67, 57), tuple(ink))]
            if nb: out[y, x, :3] = Counter(nb).most_common(1)[0][0]
        # the shaft's middle (review r2 R1): dark flecks and the grey along it take the shaft's own most common colour
        core = oar_core(big) & (out[..., 3] > 0)
        if core.any():
            lum = out[..., :3].astype(float) @ [0.299, 0.587, 0.114]
            okc = core & (lum >= 90)
            if okc.any():
                cols, cnt = np.unique(out[okc][:, :3], axis=0, return_counts=True)
                bad = core & ((lum < 90) | (out[..., :3] == (85, 67, 57)).all(2))
                out[bad, :3] = cols[cnt.argmax()]
        al2 = out[..., 3] > 0                                         # crumbs left by the selection go: all but the boat
        lbl2, n2 = ndimage.label(al2, structure=np.ones((3, 3)))
        if n2 > 1:
            sizes = ndimage.sum(al2, lbl2, range(1, n2 + 1))
            out[(lbl2 != int(np.argmax(sizes)) + 1) & al2] = 0
        moving[k] = take
        outs[k] = out
        print(f'frame {k}: offset {off}, taken from the animation {int((take & (out[..., 3] > 0)).sum())} px')
    H, W = base.shape[:2]; up = M; PADX = M
    # one cell size: the union box of the used frames
    U = np.zeros((H, W), bool)
    for o in outs.values(): U |= o[..., 3] > 0
    ys, xs = np.nonzero(U)
    cy0, cy1, cx0, cx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cw, ch = cx1 - cx0, cy1 - cy0
    res = np.zeros((ch, cw * 8, 4), np.uint8)
    for i, k in enumerate(ORDER):
        f = merge_blotches(outs[k][cy0:cy1, cx0:cx1].copy())
        keep = ~moving[k][cy0:cy1, cx0:cx1]                               # outside the man and the oar: the hull as is
        f[keep] = base[cy0:cy1, cx0:cx1][keep]
        for y in range(56, 60):                                           # review r2 R2: the grey speck at the gunwale's end
            if tuple(f[y, 55, :3]) == (214, 213, 218) and tuple(f[y, 54, :3]) == (251, 219, 170): f[y, 55, :3] = (251, 219, 170)
        res[:, i * cw:(i + 1) * cw] = f
    Image.fromarray(res).save('riverwalk/art/scene/rowboat.png')
    import outline_complete                                           # the blade's and the cap's edge: one ink
    outline_complete.run('riverwalk/art/scene/rowboat.png', 'riverwalk/art/scene/rowboat.png', frames=(cw, ch))
    # the deck: the gunwale's top row over the flat part of the hull (the bow end at the left)
    hull_x0, hull_x1 = PADX - cx0, PADX + sw - cx0
    print(f'rowboat.png {cw * 8}x{ch}: 8 cells of {cw} x {ch}; hull x {hull_x0}-{hull_x1 - 1}, waterline row {up + water - cy0}, '
          f'gunwale rows {up + gun[0] - cy0} (bow) .. {up + gun[MAN0] - cy0} (middle) .. {up + gun[-1] - cy0} (stern)')


if __name__ == '__main__':
    main()
