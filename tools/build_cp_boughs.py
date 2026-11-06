#!/usr/bin/env python3
"""build_cp_boughs.py: stage 2 of the City Park climbing parts (6 Nov, family cp_boughs_06nov). Takes the stage 1 cut
(art/source/cp_boughs/sheet_cut.png, tools/cut_cp_boughs.py: 1:1 on the render's grid, colours per material by
k-means) and makes the game's parts by rule. Nothing is resampled: every pixel is a pixel of the cut, moved whole.
Rules (each one logged in art/source/cp_boughs/edits.json):
 R1 palette: the cut's ramps snapped to the approved City Park lime's (riverwalk/art/scene/cp_lime.png): its four
    leaf shades, its bark shades plus one own mid brown; the cut's lightest leaf highlight joins the lime's highlight.
 R2 stray: leaf-coloured specks on the bark (leaf islands under 30 px) take the commonest bark colour around them;
    opaque pixels with at most one opaque 8-neighbour (twig specks) and bits of 1-4 px go.
 R3 limbs (the ledges): each column of the limb body is moved up or down whole so the body's top is one straight row
    (Pepper stands on it); bodies thicker than 8 px lose rows from the middle of the column (the lit top 4 and the
    dark underside 4 stay), so the limb is 8 px of bark over the 6 px box.
 R4 low bough: the same, its level part 16 rows (its box), the rest at most 16; the cut free end rounded (corners).
 R5 outline: play pieces (limbs, low bough, stump) get the 1 px ink outline (the old code's INK #1d1816) on every
    side; leaves, nest and trunks are decoration with no outline (their edges are the darker shades of their ramps).
 R6 stump: its 24 px body kept, the bottom rows past 28 cropped (whole rows).
Out (riverwalk/art/scene/): cp_bough_limb.png + cp_bough_limb_leaves.png (thin limb, its tip clump on the same
canvas), cp_bough_limbx.png + cp_bough_limbx_leaves.png (the thick limb), cp_bough_low.png + cp_bough_low_leaves.png,
cp_bough_clumps.png (nine loose clumps), cp_bough_nest.png, cp_bough_stump.png, cp_bough_trunk.png (32 px), and
cp_bough_trunk9/10.png (small trunks, by their width); riverwalk/cp_boughs_data.lua (each part's anchors for scene.lua)."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = 'art/source/cp_boughs'; DST = 'riverwalk/art/scene'
LUM = np.array([0.299, 0.587, 0.114])
INK = (29, 24, 22)
a = np.array(Image.open(f'{SRC}/sheet_cut.png')).astype(int)
leafm = np.array(Image.open(f'{SRC}/sheet_leaf.png')) > 0
al = a[..., 3] > 0
J = json.load(open('art/gen/out/cp_boughs.cut.json'))
EDITS = {'R1': {}, 'R2': {}, 'R3': {}, 'R4': {}, 'R5': {}, 'R6': {}}

# R1 palette: lime ramps (unfaded file colours of riverwalk/art/scene/cp_lime.png)
LIME_LEAF = [(107, 46, 47), (198, 52, 24), (235, 104, 25), (250, 154, 40)]
LIME_BARK = [(62, 36, 33), (95, 51, 38), (142, 74, 38), (203, 107, 35)]
OWN_MID = (173, 87, 36)
snap = {}
for c, t in zip(J['palette']['leaf'], LIME_LEAF + [LIME_LEAF[3]]): snap[tuple(c)] = t
bark_targets = [LIME_BARK[0], LIME_BARK[1], LIME_BARK[2], OWN_MID, LIME_BARK[3]]
for c, t in zip(J['palette']['bark'], bark_targets): snap[tuple(c)] = t
rgb = a[..., :3].copy()
for c, t in snap.items():
    m = al & (rgb == c).all(-1); rgb[m] = t
EDITS['R1'] = {f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}': f'#{t[0]:02x}{t[1]:02x}{t[2]:02x}' for c, t in snap.items()}
LEAFSET = {tuple(c) for c in LIME_LEAF}

# component labels of the sheet (the parts, by the blockout's layout)
lab, n = ndimage.label(al, structure=np.ones((3, 3)))
objs = ndimage.find_objects(lab)
def comp_at(x, y):
    i = lab[y, x]
    assert i, (x, y)
    return i
PART = {'limbx': comp_at(300, 42), 'limb': comp_at(250, 87), 'trunk': comp_at(95, 300),
        'low': comp_at(160, 236), 'stump': comp_at(240, 495),
        'trunk10': comp_at(144, 450), 'trunk9': comp_at(167, 450)}   # named by their drawn width (asked 8 and 10;
# the third, asked 12, came out 9 px as well and is not used)
nest_i = lab[230, 315]; PART['nest'] = nest_i
clumps = sorted([i for i in range(1, n + 1) if objs[i - 1][0].start >= 265 and objs[i - 1][0].stop <= 360
                 and objs[i - 1][1].start >= 240 and (lab == i).sum() > 50], key=lambda i: (objs[i - 1][0].start // 40, objs[i - 1][1].start))


def crop(i, pad=0):
    s = objs[i - 1]
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    m = lab[y0:y1, x0:x1] == i
    c = rgb[y0:y1, x0:x1].copy()
    lf = leafm[y0:y1, x0:x1] & m
    return c, m, lf, (x0, y0)


def is_leafcol(c): return tuple(c) in LEAFSET


BARKSET = np.array(bark_targets)


def r2_clean(c, m, lf, tag, wood=False):
    """leaf islands under 30 px on bark take the bark around them (wood: the whole part is bark, its lit streaks
    take the nearest bark shade); loose specks go"""
    n_fix = 0
    if wood:
        for y, x in zip(*np.nonzero(lf & m)):
            lab_c = c[y, x]
            c[y, x] = BARKSET[np.argmin(((BARKSET - lab_c) ** 2).sum(1))]; n_fix += 1
        lf = lf & False
    lfl, k = ndimage.label(lf & m, structure=np.ones((3, 3)))
    for j in range(1, k + 1):
        comp = lfl == j
        if comp.sum() >= 30: continue
        ring = ndimage.binary_dilation(comp, structure=np.ones((3, 3))) & m & ~lf
        if ring.any():
            cols, cnt = np.unique(c[ring], axis=0, return_counts=True)
            c[comp] = cols[cnt.argmax()]
        else:
            m &= ~comp
        lf &= ~comp; n_fix += int(comp.sum())
    n_drop = 0
    for _ in range(3):
        nb = ndimage.convolve(m.astype(int), np.ones((3, 3), int), mode='constant') - m
        lone = m & (nb <= 1)
        if not lone.any(): break
        m &= ~lone; n_drop += int(lone.sum())
    cl, k = ndimage.label(m, structure=np.ones((3, 3)))
    for j in range(1, k + 1):
        if (cl == j).sum() <= 4: m[cl == j] = False; n_drop += 1
    lf &= m
    EDITS['R2'][tag] = {'leaf_specks_to_bark_px': n_fix, 'loose_px_dropped': n_drop}
    return c, m, lf


def reseat(c, m, lf, x_from, x_to, mid_row, body_max, keep_top, tag, target=None, rows=None, up=5):
    """R3/R4: per column, the body run (the opaque bark run through mid_row) is moved whole so its top sits on one
    row; middle rows dropped past body_max. Columns after x_to keep the last shift. Returns new arrays."""
    H, W = m.shape
    bark = m & ~lf
    tops = {}
    for x in range(W):
        if not bark[mid_row, x]: continue
        y = mid_row
        while y > max(0, mid_row - up) and bark[y - 1, x]: y -= 1
        twig = y == mid_row - up and bark[y - 1, x]                   # a twig rises from the top here: keep the shift
        yb = mid_row
        while yb < H - 1 and bark[yb + 1, x]: yb += 1
        tops[x] = (y, yb, twig)
    if target is None:
        vals = [tops[x][0] for x in range(x_from, x_to) if x in tops and not tops[x][2]]
        target = int(np.bincount(vals).argmax())
    PAD = 8
    C = np.zeros((H + 2 * PAD, W, 3), int); M = np.zeros((H + 2 * PAD, W), bool); LF = np.zeros_like(M)
    shift = 0; moved = 0; dropped = 0
    for x in range(W):
        col_c, col_m, col_l = c[:, x].copy(), m[:, x].copy(), lf[:, x].copy()
        if x in tops:
            t, b, twig = tops[x]
            if x <= x_to and not twig: shift = target - t
            else: t = target - shift
            thick = b - t + 1
            lim = body_max if not rows else rows
            if thick > lim:                                   # drop rows from the middle of the body run
                k = thick - lim
                cut0 = t + keep_top
                keep = np.ones(H, bool); keep[cut0:cut0 + k] = False
                # rows above the body (twigs) keep their place relative to the top
                col_c = np.concatenate([col_c[keep], np.zeros((k, 3), int)]); col_m = np.concatenate([col_m[keep], np.zeros(k, bool)])
                col_l = np.concatenate([col_l[keep], np.zeros(k, bool)]); dropped += k
        if shift: moved += 1
        ys = np.arange(H) + shift + PAD
        ok = (ys >= 0) & (ys < H + 2 * PAD)
        C[ys[ok], x] = col_c[ok]; M[ys[ok], x] = col_m[ok]; LF[ys[ok], x] = col_l[ok]
    rr = np.nonzero(M.any(1))[0]
    C, M, LF = C[rr.min():rr.max() + 1], M[rr.min():rr.max() + 1], LF[rr.min():rr.max() + 1]
    target_out = target + PAD - rr.min()
    EDITS['R3' if tag != 'low' else 'R4'][tag] = {'columns_moved': moved, 'rows_dropped': dropped, 'top_row': int(target_out)}
    return C, M, LF, target_out


import cleanpass


def blotch_merge(rgb, al):
    """asset_qa's blotch rule as a merge (tools/cut_cp_tree.py): a 2-24 px patch inside one fill joins it"""
    key = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    key = np.where(al, key, -1); n = 0
    for k in np.unique(key[al]):
        lab_, cc = ndimage.label(key == k, structure=np.ones((3, 3)))
        sizes = np.bincount(lab_.ravel())
        for i in range(1, cc + 1):
            if not (2 <= sizes[i] <= 24): continue
            mm = lab_ == i
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
            if np.sqrt(((oc - rgb[mm][0]) ** 2).sum()) < 45:
                rgb[mm] = oc; key[mm] = o; n += 1
    return rgb, n


def clean(c, m, tag):
    """R7 clean pass on this new cut only (BIBLE): lone pixels (tools/cleanpass.py, 3 passes) and blotches merge"""
    out, n1 = cleanpass.clean(np.clip(c, 0, 255).astype(np.uint8), m, 70, False)
    out = out.astype(int); n2 = 0
    for _ in range(3):
        out, k = blotch_merge(out, m); n2 += k
    EDITS.setdefault('R7', {})[tag] = {'lone': int(n1), 'blotches': int(n2)}
    return out


MID = np.array(LIME_BARK[2]); DARK2 = np.array(LIME_BARK[1])


def rim(c, m, tag, mid=MID, dark=DARK2):
    """R8 decoration edges (no ink): edge pixels facing the sun (open above or on the left) darker than luma 70 take
    the ramp's mid shade, the other edge pixels darker than luma 45 the next shade up (lime's rule: no ink rim)"""
    pm = np.pad(m, 1)
    edge = m & ~(pm[:-2, 1:-1] & pm[2:, 1:-1] & pm[1:-1, :-2] & pm[1:-1, 2:])
    lit = edge & (~pm[:-2, 1:-1] | ~pm[1:-1, :-2])
    lum = c @ LUM
    a1 = lit & (lum < 70); a2 = edge & ~lit & (lum < 45)
    c[a1] = mid; c[a2] = dark
    EDITS.setdefault('R8', {})[tag] = int(a1.sum() + a2.sum())
    return c


def despeck(m, tag, k=8):
    """free-floating bits of up to k px go (asset_qa specks)"""
    lb_, n_ = ndimage.label(m, structure=np.ones((3, 3)))
    sz_ = np.bincount(lb_.ravel()); big = np.argmax(sz_[1:]) + 1; d = 0
    for j in range(1, n_ + 1):
        if j != big and sz_[j] <= k: m = m & (lb_ != j); d += int(sz_[j])
    EDITS.setdefault('R7', {}).setdefault(tag, {})['specks_px'] = d
    return m


def pinholes(c, m, tag):
    """holes of 1-4 px inside a decoration fill take their commonest neighbour"""
    holes = ~m & ndimage.binary_fill_holes(m)
    hl, n_ = ndimage.label(holes); f = 0
    for j in range(1, n_ + 1):
        comp = hl == j
        if comp.sum() > 4: continue
        ring = ndimage.binary_dilation(comp) & m
        cols, cnt = np.unique(c[ring], axis=0, return_counts=True)
        c[comp] = cols[cnt.argmax()]; m = m | comp; f += int(comp.sum())
    EDITS.setdefault('R7', {}).setdefault(tag, {})['pinholes_px'] = f
    return c, m


def ink(c, m):
    """R5: 1 px ink on every side of the silhouette (4-neighbours), canvas grown by 1"""
    C = np.pad(c, ((1, 1), (1, 1), (0, 0))); M = np.pad(m, 1)
    pm = np.pad(M, 1)
    near = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & ~M
    C[near] = INK
    return C, M | near, int(near.sum())


def save(name, c, m):
    im = np.dstack([c, np.where(m, 255, 0)]).astype(np.uint8); im[~m] = 0
    Image.fromarray(im, 'RGBA').save(f'{DST}/{name}.png')
    return im


def split_save(name, c, m, lf, outline, leaves=True):
    """bark (outlined when a play piece) and leaves on one canvas size, as two files. R2b: bark islands under 40 px
    (leaf-shadow pixels the clustering called bark) join the leaves in the nearest leaf shade, or go"""
    bark = m & ~lf
    bl, k = ndimage.label(bark, structure=np.ones((3, 3)))
    LS = np.array(LIME_LEAF); nj = 0
    for j in range(1, k + 1):
        comp = bl == j
        if comp.sum() >= 40: continue
        if (ndimage.binary_dilation(comp, structure=np.ones((3, 3))) & lf).any():
            for y, x in zip(*np.nonzero(comp)):
                c[y, x] = LS[np.argmin(((LS - c[y, x]) ** 2).sum(1))]
            lf = lf | comp
        else:
            m = m & ~comp
        nj += int(comp.sum())
    EDITS['R2'][name + '_bark_islands'] = nj
    c = clean(c, m, name)
    bark = m & ~lf
    if outline:
        cb, mb, nink = ink(np.where(bark[..., None], c, 0), bark)
        cl = np.pad(c, ((1, 1), (1, 1), (0, 0))); ml = np.pad(lf, 1)
        EDITS['R5'][name] = int(nink)
    else:
        cb, mb, cl, ml = c, bark, c, lf
    save(name, cb, mb)
    if ml.any() and leaves:
        cl, ml = pinholes(cl, ml, name + '_leaves')
        save(name + '_leaves', cl, ml)
    return mb, ml


D = {}
# --- limbs (R3): body top straight; the twig and its clump past the tip
for nm, i, mid, bmax in (('limb', PART['limb'], 87, 8), ('limbx', PART['limbx'], 42, 8)):
    c, m, lf, (ox, oy) = crop(i)
    c, m, lf = r2_clean(c, m, lf, nm)
    c, m, lf, top = reseat(c, m, lf, 0, m.shape[1] - 1, mid - oy, bmax, 4, nm)
    bark = m & ~lf
    # body columns: the run through the top row is at least 5 deep
    W = m.shape[1]; body = [x for x in range(W) if bark[top:top + 5, x].all()]
    body_end = max(x for x in body if x < W - 5 and all(xx in body for xx in range(min(body), x + 1)))
    mb, ml = split_save(f'cp_bough_{nm}', c, m, lf, True, leaves=False)   # its tip clump: the loose clumps (scene.lua)
    ly, lx = np.nonzero(ml)
    tb = mb.copy(); tb[:, :body_end + 2] = False                       # the twig past the tip: its far top end
    ty_, tx_ = np.nonzero(tb & (np.arange(mb.shape[0])[:, None] < top))
    far = np.argmax(tx_ - ty_)
    D[nm] = {'w': int(mb.shape[1]), 'h': int(mb.shape[0]), 'top': int(top + 1), 'body0': 1, 'bodyEnd': int(body_end + 1),
             'tip': int(body_end + 1 - 24), 'clump': [int(tx_[far]) + 3, int(ty_[far]) - 3],
             'clumpBig': [int(lx.mean()), int(ly.mean())] if len(lx) else None}
# --- the low bough (R4): level part 16 rows, the free end on the left
c, m, lf, (ox, oy) = crop(PART['low'])
c, m, lf = r2_clean(c, m, lf, 'low')
c, m, lf, top = reseat(c, m, lf, 0, 32, 236 - oy, 16, 9, 'low', rows=16, up=14)
bark = m & ~lf
x0 = int(np.nonzero(bark.any(0))[0].min())
for (yy, xx) in ((top, x0), (top + 15, x0), (top, x0 + 1), (top + 15, x0 + 1), (top + 1, x0), (top + 14, x0)):
    if m[yy, xx] and not lf[yy, xx]: m[yy, xx] = False                # round the cut free end
EDITS['R4']['low_free_end_rounded'] = 6
mb, ml = split_save('cp_bough_low', c, m, lf, True)
D['low'] = {'w': int(mb.shape[1]), 'h': int(mb.shape[0]), 'top': int(top + 1), 'x0': x0 + 1}
# --- loose clumps (decoration, one sheet in a row, 2 px apart)
cl_imgs = []
for i in clumps:
    c, m, lf, _ = crop(i)
    c, m, lf = r2_clean(c, m, lf, f'clump{i}')
    c = clean(c, m, f'clump{i}')
    cl_imgs.append((c, m))
Wc = sum(cm[1].shape[1] + 2 for cm in cl_imgs); Hc = max(cm[1].shape[0] for cm in cl_imgs)
SC = np.zeros((Hc, Wc, 3), int); SM = np.zeros((Hc, Wc), bool); rects = []; x = 0
for c, m in cl_imgs:
    h, w = m.shape; y = Hc - h
    SC[y:y + h, x:x + w][m] = c[m]; SM[y:y + h, x:x + w] |= m; rects.append([x, y, w, h]); x += w + 2
save('cp_bough_clumps', SC, SM)
D['clumps'] = rects
# --- nest (decoration): the bowl above its little branch, no outline
c, m, lf, (ox, oy) = crop(PART['nest'])
c, m, lf = r2_clean(c, m, lf, 'nest', wood=True)
rows_keep = 236 - oy; cols_keep = 335 - ox
m[rows_keep:, :] = False; m[:, cols_keep:] = False
c2, m2, lf2 = r2_clean(c, m, lf & m, 'nest2')
yy, xx = np.nonzero(m2)
c2, m2 = c2[yy.min():yy.max() + 1, xx.min():xx.max() + 1], m2[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
Hn, Wn = m2.shape                                                      # the bowl's underside rounded (the cut of its
yy_, xx_ = np.mgrid[0:Hn, 0:Wn]                                       # branch left a straight edge on the right)
cxn, cyn = (Wn - 1) / 2, 4
out_ = (yy_ > cyn) & (((xx_ - cxn) / (Wn / 2 - 1)) ** 2 + ((yy_ - cyn) / (Hn - cyn)) ** 2 > 1)
EDITS['R2']['nest_round_px'] = int((m2 & out_).sum()); m2 &= ~out_
c2 = rim(c2, m2, 'nest'); c2 = clean(c2, m2, 'nest'); m2 = despeck(m2, 'nest')
yy, xx = np.nonzero(m2)
c2, m2 = c2[yy.min():yy.max() + 1, xx.min():xx.max() + 1], m2[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
save('cp_bough_nest', c2, m2)
D['nest'] = {'w': int(m2.shape[1]), 'h': int(m2.shape[0])}
# --- stump (R6): 24 px body, 28 rows; outlined (an obstacle)
c, m, lf, (ox, oy) = crop(PART['stump'])
lf0 = leafm[oy:oy + m.shape[0], ox:ox + m.shape[1]] & m
ys_ = np.nonzero(m.any(1))[0]
cut_top = lf0 & (np.arange(m.shape[0])[:, None] < ys_.min() + 6)     # the sawn top: the cut's own light wood and rings
orig = a[oy:oy + m.shape[0], ox:ox + m.shape[1], :3]
c, m, lf = r2_clean(c, m, lf0 & ~cut_top, 'stump', wood=True)
c[cut_top] = orig[cut_top]
red = cut_top & ((orig == (200, 39, 22)).all(-1) | (orig == (130, 31, 47)).all(-1))
c[red] = (235, 98, 17); EDITS['R6']['stump_red_specks_to_ring'] = int(red.sum())
EDITS['R6']['stump_cut_top_kept_px'] = int(cut_top.sum())
lf[:] = False
yy = np.nonzero(m.any(1))[0]; c, m = c[yy.min():yy.min() + 28], m[yy.min():yy.min() + 28]
EDITS['R6']['stump_rows_cropped'] = int(len(yy) - 28)
c = clean(c, m, 'stump')
cs, ms, nk = ink(c, m); EDITS['R5']['cp_bough_stump'] = nk
save('cp_bough_stump', cs, ms)
cols = np.nonzero(m[8])[0]
D['stump'] = {'w': int(ms.shape[1]), 'h': int(ms.shape[0]), 'body0': int(cols.min() + 1), 'bodyW': int(cols.max() - cols.min() + 1)}
# --- trunks (decoration, faded by the game as the back layer)
for nm in ('trunk', 'trunk9', 'trunk10'):
    c, m, lf, _ = crop(PART[nm])
    c, m, lf = r2_clean(c, m, lf, nm, wood=True)
    yy, xx = np.nonzero(m)
    c, m = c[yy.min():, :], m[yy.min():, :]
    c = rim(c, m, nm); c = clean(c, m, nm)
    save(f'cp_bough_{nm}', c, m)
    H = m.shape[0]
    row = np.nonzero(m[H // 3])[0]                                   # the trunk's own width a third down (no stubs)
    runs = np.split(row, np.nonzero(np.diff(row) > 1)[0] + 1)
    main = max(runs, key=len)
    D[nm] = {'w': int(m.shape[1]), 'h': int(H), 'x0': int(main.min()), 'tw': int(len(main))}
json.dump(EDITS, open(f'{SRC}/edits.json', 'w'), indent=1)


def lua(v):
    if isinstance(v, dict): return '{ ' + ', '.join(f'{k} = {lua(x)}' for k, x in v.items()) + ' }'
    if isinstance(v, list): return '{ ' + ', '.join(lua(x) for x in v) + ' }'
    if v is None: return 'nil'
    return str(v)


with open('riverwalk/cp_boughs_data.lua', 'w') as f:
    f.write('-- City Park climbing parts (6 Nov, cp_boughs_06nov): anchors of the art in art/scene/cp_bough_*.png, written\n'
            '-- by tools/build_cp_boughs.py. top: the body\'s top row (the ledge line); bodyEnd: the column after the tip of\n'
            '-- the body (the twig runs past it); tip: where the tip piece starts; clump: the tip clump\'s centre.\n')
    f.write('return ' + lua(D) + '\n')
print(json.dumps(D))
print(json.dumps(EDITS))
