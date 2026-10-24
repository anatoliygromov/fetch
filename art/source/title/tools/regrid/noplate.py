"""Paint out the "PRESS ANY KEY TO START" plate from the background, by rule.

The plate (its light blue border, navy fill and letters) is found as the cells between the
first and last border cell of each row. Behind it the scene continues:
  * railing slot rows: bar columns (1 px bars on the round 4 pitch, read from the row above
    the plate) continue down to the curb; the slot backgrounds continue the four slot rows
    above the plate, mirrored downwards (no hard repeat, no seam);
  * the bottom rail: one straight row in the rail colour, at the row the railing beside the
    plate has it;
  * the hedge strip under the rail: tiled from the hedge cells beside the plate (bars left out);
  * the curb: one brown row, as beside the plate;
  * the pavement: the pavement rows just below the plate, shifted up, so the stone runs and
    tones continue.
Every filled colour is one the picture already uses next to the plate.
"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, NX, NY, srgb_to_lab, hexs
from scipy import ndimage as ndi

BORDER = {0x3fa9f5, 0x199bf3}
BOX = (148, 188, 280, 208)          # search box for the plate (cells)


def keys(img):
    c = img.astype(np.int64)
    return (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]


PLATE = BORDER | {0x012555, 0xffeacb, 0xfff5ce, 0xfee2b4}


def plate_mask(k, img):
    """The plate: the rectangle spanned by its border rows, with the rounded corner rows
    limited to plate colours, plus the pale glow row the painting has under it."""
    x0, y0, x1, y1 = BOX
    rows = []
    for j in range(y0, y1):
        xs = [i for i in range(x0, x1) if k[j, i] in BORDER]
        if len(xs) >= 2 and xs[-1] - xs[0] > 20:
            rows.append((j, xs[0], xs[-1]))
    pt = min(r[0] for r in rows); pbr = max(r[0] for r in rows)
    pl = min(r[1] for r in rows); pr = max(r[2] for r in rows)
    pb = max([j for j in range(pbr, y1) if any(k[j, i] in BORDER for i in range(pl, pr + 1))])
    m = np.zeros(k.shape, bool)
    m[pt:pb + 1, pl:pr + 1] = True
    for j in (pt, pt + 1, pb - 1, pb):                    # rounded corners: only the ends
        for i in list(range(pl, pl + 4)) + list(range(pr - 3, pr + 1)):
            m[j, i] = k[j, i] in PLATE
    lab = srgb_to_lab(img.astype(np.float32))
    for j in (pb + 1, pb + 2):
        for i in range(pl, pr + 1):
            if (lab[j, i, 0] > 60 and np.hypot(lab[j, i, 1], lab[j, i, 2]) < 12) or lab[j, i, 2] < 0:
                m[j, i] = True
    return m


def main(src=None, dst=None):
    src = src or os.path.join(OUT, 'result_bg_320.png')
    dst = dst or os.path.join(OUT, 'result_bg_noplate_320.png')
    img = np.array(Image.open(src).convert('RGB'))
    k = keys(img)
    m = plate_mask(k, img)
    rows = np.flatnonzero(m.any(1)); cols = np.flatnonzero(m.any(0))
    pt, pb = rows.min(), rows.max()
    pl, pr = cols.min(), cols.max()
    # the rows between the last clean slot row and the plate were left irregular (the railing
    # rule skipped the plate's box): rebuild them too
    m0 = m.copy()
    m[pt - 3:pt, pl:pr + 1] = True
    L = srgb_to_lab(img.astype(np.float32))[..., 0]
    out = img.copy()
    rail = np.array([1, 17, 53], np.uint8)                       # #011135, the railing colour
    israil = (img == rail).all(2)
    # reference columns beside the plate (left and right), used to read the row structure
    side = [i for i in range(pl - 12, pl) if 0 <= i] + [i for i in range(pr + 1, min(NX, pr + 9))]
    # bar columns: rail colour in the row above the plate, 1 px wide
    above = pt - 1
    # bar columns: rail colour on every row of the upper slot band (between the two rails)
    band = [r for r in range(pt - 9, pt - 3) if np.mean(israil[r, pl:pr + 1]) < 0.5]   # rows 182-187: clean slots
    railish = np.array([np.mean([israil[j, i] for j in band]) for i in range(NX)])
    bars = [i for i in range(pl, pr + 1) if railish[i] >= 0.75 and railish[i - 1] < 0.75 and railish[i + 1] < 0.75]
    darkcol = np.array([np.mean([L[j, i] < 25 for j in band]) for i in range(NX)])
    posts = set()
    i = pl
    while i <= pr:
        if darkcol[i] >= 0.75 and i not in bars:
            kx = i
            while kx + 1 <= pr and darkcol[kx + 1] >= 0.75:
                kx += 1
            if kx - i >= 1:
                posts |= set(range(i, kx + 1))
            i = kx + 1
        else:
            i += 1
    post_src = pt - 4
    # bottom rail: first row at or below the plate top where the side cells are mostly rail colour
    def side_frac(j):
        return np.mean([israil[j, i] for i in side])
    bottom = next((j for j in range(pt, pb + 1) if side_frac(j) >= 0.75), pt + 8)
    # curb row: first row below the bottom rail where the side cells are mostly brown
    brown = (img[..., 0] > 110) & (img[..., 0] - img[..., 2] > 60) & (L < 50)
    curb = next((j for j in range(bottom + 1, pb + 3) if np.mean([brown[j, i] for i in side]) >= 0.4), bottom + 4)
    # slot rows above the plate, mirrored downwards
    above = pt - 4
    slot_src = [r for r in range(above - 2, above + 1)] + [r for r in range(pt - 3, pt)]
    period = slot_src + slot_src[::-1]
    # hedge sample: side cells in the hedge rows, without bars
    hedge_rows = list(range(bottom + 1, curb))
    hedge = []
    for i in []:
        colv = [img[j, i] for j in hedge_rows]
        if not any((c == rail).all() for c in colv) and all(int(c[1]) > int(c[2]) and int(c[1]) > int(c[0]) for c in colv):
            hedge.append(colv)
    # hedge strip: per row the most common green beside the plate along the whole railing
    hedge_row = {}
    for j in hedge_rows:
        cand = [tuple(img[j, i]) for i in range(135, 292) if not m[j, i] and int(img[j, i, 1]) > int(img[j, i, 2])
                and int(img[j, i, 1]) > int(img[j, i, 0])]
        hedge_row[j] = cand
    allc = [c for j in hedge_rows for c in hedge_row[j]]
    if allc:
        v, c = np.unique(np.array(allc), axis=0, return_counts=True); hc = v[c.argmax()]
    else:
        hc = rail
    hedge_row = {j: hc for j in hedge_rows}
    brown_col = None
    bvals = [tuple(img[curb, i]) for i in side if brown[curb, i]]
    if bvals:
        v, c = np.unique(np.array(bvals), axis=0, return_counts=True); brown_col = v[c.argmax()]
    shift = (pb - curb) + 4                                       # pavement rows from below the plate's shadow
    for j in range(pt - 3, pb + 1):
        for i in range(pl, pr + 1):
            if not m[j, i]:
                continue
            if i in posts and j < curb:
                out[j, i] = img[post_src, i]
                continue
            if j < bottom:
                if i in bars:
                    out[j, i] = rail
                else:
                    r = period[(j - pt + 3) % len(period)]
                    c = img[r, i]
                    if (c == rail).all() or L[r, i] < 32 or L[r, i] > 80:   # stray dark or sky-gap cell
                        nb = [img[r, x] for x in range(i - 8, i + 9) if x not in bars and not (img[r, x] == rail).all() and 32 <= L[r, x] <= 80]
                        if nb:
                            v, cn = np.unique(np.array(nb), axis=0, return_counts=True); c = v[cn.argmax()]
                    out[j, i] = c
            elif j == bottom:
                out[j, i] = rail
            elif j < curb:
                if i in bars:
                    out[j, i] = rail
                else:
                    out[j, i] = hedge_row[j]
            elif j == curb and brown_col is not None:
                out[j, i] = brown_col
            else:
                c = out[min(NY - 1, j + shift), i]
                cl = srgb_to_lab(c[None].astype(np.float32))[0]
                if cl[2] < 0 or cl[0] > 85:                  # no cool or glow cells in the warm pavement
                    rowv = [tuple(out[j + shift, x]) for x in range(pl, pr + 1)]
                    v, cn = np.unique(np.array(rowv), axis=0, return_counts=True); c = v[cn.argmax()]
                out[j, i] = c
    # mixel repair inside the filled cells: take the opposite neighbour seen most often nearby
    import qa
    for _ in range(4):
        n_m, mm = qa.mixels(out, np.ones(m.shape, bool))
        mm &= ndi.binary_dilation(m, iterations=3)
        if not mm.any():
            break
        for j, i in np.argwhere(mm):
            nb = [tuple(out[y, x]) for y, x in ((j, i - 1), (j, i + 1), (j - 1, i), (j + 1, i))]
            v, c = np.unique(np.array(nb), axis=0, return_counts=True)
            out[j, i] = v[c.argmax()]
    Image.fromarray(out).save(dst)
    Image.fromarray(np.dstack([out, np.full(out.shape[:2], 255, np.uint8)]), 'RGBA').save(dst.replace('.png', '_rgba.png'))
    Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(OUT, 'qa_masks', 'plate_320.png'))
    print('plate cells x %d-%d y %d-%d (%d cells); bars %d; bottom rail row %d; curb row %d' % (
        pl, pr, pt, pb, int(m.sum()), len(bars), bottom, curb))
    return out, m




def final_fixes(path=None):
    """Producer's final fixes on the painted-out picture:
    1. the lower pickets (rows 187 to the bottom rail) carry the same regular bar columns as
       the upper slots, so the bars run continuously from the top rail to the kerb;
    2. light-blue holes inside the right jib take the sail's cream; the pale halo beside the
       left sail takes the water blue;
    3. the left slots of the painted-out area follow the foliage beside them (one green per
       row, the most common green of that row left of the plate), no tan or odd shapes."""
    import build_bg as B
    path = path or os.path.join(OUT, 'result_bg_noplate_320.png')
    o = np.array(Image.open(path).convert('RGB'))
    lab = srgb_to_lab(o.astype(np.float32))
    rail = np.array([1, 17, 53], np.uint8)
    isr = (o == rail).all(2)
    vis = B.visible_mask() | (np.array(Image.open(os.path.join(OUT, 'qa_masks', 'plate_320.png'))) > 0)
    x0, x1 = 135, 290
    clean = [183, 184, 185]
    bars = [i for i in range(x0, x1) if all(isr[j, i] for j in clean)
            and not all(isr[j, i - 1] for j in clean) and not all(isr[j, i + 1] for j in clean)]
    darkL = lab[..., 0] < 25
    posts = [i for i in range(x0, x1) if all(darkL[j, i] for j in clean) and i not in bars]
    bottom = 199
    n1 = 0
    for j in range(187, bottom):
        for i in range(x0, x1):
            if not vis[j, i] or i in posts:
                continue
            if i in bars:
                if not isr[j, i]:
                    o[j, i] = rail; n1 += 1
            elif isr[j, i] or lab[j, i, 0] < 25:
                nb = [tuple(o[j, x]) for x in range(i - 4, i + 5) if x not in bars and x not in posts
                      and 0 <= x < NX and lab[j, x, 0] >= 25]
                if not nb:
                    nb = [tuple(o[j - 1, i])]
                v, c = np.unique(np.array(nb), axis=0, return_counts=True)
                o[j, i] = v[c.argmax()]; n1 += 1
    # 2. sails
    n2 = 0
    for j in range(140, 159):
        for i in range(258, 269):
            c = lab[j, i]
            if c[2] < -10 and c[0] > 55:
                nb = [tuple(o[y, x]) for y in range(j - 2, j + 3) for x in range(i - 2, i + 3)
                      if lab[y, x, 0] > 80 and lab[y, x, 2] > 0]
                l = sum(1 for x in range(258, i) if lab[j, x, 0] > 80); r = sum(1 for x in range(i + 1, 269) if lab[j, x, 0] > 80)
                if nb and l and r:
                    v, cn = np.unique(np.array(nb), axis=0, return_counts=True)
                    o[j, i] = v[cn.argmax()]; n2 += 1
    for j in range(140, 149):
        for i in range(215, 226):
            c = lab[j, i]
            if 60 < c[0] < 88 and c[2] < 5 and not (c[0] > 85):
                nb = [tuple(o[y, x]) for y in range(j - 1, j + 2) for x in range(i - 2, i + 3)
                      if 45 < lab[y, x, 0] < 70 and lab[y, x, 2] < -20]
                if nb:
                    v, cn = np.unique(np.array(nb), axis=0, return_counts=True)
                    o[j, i] = v[cn.argmax()]; n2 += 1
    # 3. left slots of the painted-out area follow the foliage beside them
    n3 = 0
    pl = 154
    g = None
    isr = (o == rail).all(2)
    for j in range(187, bottom):
        greens = [tuple(o[j, x]) for x in range(x0, pl) if x not in bars and x not in posts
                  and int(o[j, x, 1]) > int(o[j, x, 2]) and int(o[j, x, 1]) > int(o[j, x, 0])]
        if greens:
            v, cn = np.unique(np.array(greens), axis=0, return_counts=True); g = v[cn.argmax()]
        if g is None:
            continue
        for i in range(pl, 186):
            if i in bars or i in posts or isr[j, i] or not vis[j, i]:
                continue
            cc = o[j, i]
            green = int(cc[1]) > int(cc[2]) and int(cc[1]) > int(cc[0])
            if not green or True:
                if not (cc == g).all():
                    o[j, i] = g; n3 += 1
    # mixel repair in the touched rows
    import qa
    for _ in range(4):
        n_m, mm = qa.mixels(o, np.ones(o.shape[:2], bool))
        if not mm.any():
            break
        for j, i in np.argwhere(mm):
            nb = [tuple(o[y, x]) for y, x in ((j, i - 1), (j, i + 1), (j - 1, i), (j + 1, i)) if 0 <= y < NY and 0 <= x < NX]
            v, c = np.unique(np.array(nb), axis=0, return_counts=True)
            o[j, i] = v[c.argmax()]
    Image.fromarray(o).save(path)
    Image.fromarray(np.dstack([o, np.full(o.shape[:2], 255, np.uint8)]), 'RGBA').save(path.replace('.png', '_rgba.png'))
    print('final fixes: pickets %d, sails %d, left slots %d; bars %d posts %d' % (n1, n2, n3, len(bars), len(posts)))


if __name__ == '__main__':
    main()
    final_fixes()
