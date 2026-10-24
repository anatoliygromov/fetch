"""QA gates for the logo track: geometry, lines, colour, pattern, form."""
import numpy as np
from scipy import ndimage as ndi
from logo_common import *
from logo_lines import lcorners
import logo as LG


# ------------------------------------------------------------------ geometry
def boundary(m):
    return m & ~ndi.binary_erosion(m)


def iou_bd(res_full, ref_full):
    """IoU and symmetric mean boundary distance (in blocks of 7.5 px) of two full-res masks."""
    inter = (res_full & ref_full).sum(); uni = (res_full | ref_full).sum()
    br, bf = boundary(res_full), boundary(ref_full)
    dr = ndi.distance_transform_edt(~br); df = ndi.distance_transform_edt(~bf)
    d = 0.5 * (dr[bf].mean() + df[br].mean())
    return inter / max(uni, 1), d / PX


def named_shapes(R):
    """Pairs (name, result cell mask, painting crop mask)."""
    L, M, G = R['L'], R['M'], R['G']
    F = M['F']
    fill = G['fill']
    toes, pad = LG.paw_parts(F)
    pawF = np.zeros_like(F)
    for m in toes + [pad]:
        pawF |= m
    out = []
    # letters: painting components of the letter fill, ordered by x; result: cells whose
    # component overlaps them
    lab, n = ndi.label(F & ~pawF)
    comps = []
    for c in range(1, n + 1):
        m = lab == c
        if m.sum() < 3000:
            continue
        comps.append((np.nonzero(m)[1].mean(), m))
    comps.sort(key=lambda t: t[0])
    names = ['F', 'E', 'T', 'C', 'H', '!']
    I, J = cell_index(H_SRC, W_SRC)
    rl, rn = ndi.label(fill)
    for name, (_, m) in zip(names, comps):
        full = LG.to_full(m)
        ids = np.unique(rl[J[full], I[full]]); ids = ids[ids > 0]
        cells = np.isin(rl, ids)
        # keep only the part of the result component(s) nearest this painted letter
        out.append((name, cells, m))
    pc = G['pawc']
    pl, pn = ndi.label(pc)
    parts = [('toe', t) for t in toes] + [('pad', pad)]
    for k, (kind, m) in enumerate(parts):
        full = LG.to_full(m)
        v = pl[J[full], I[full]]; v = v[v > 0]
        cells = pl == (np.bincount(v).argmax() if len(v) else -1)     # the result part overlapping most
        out.append(('paw_%s%d' % (kind, k) if kind == 'toe' else 'paw_pad', cells, m))
    out.append(('silhouette', G['outer'], M['CL']))
    out.append(('gaps', G['gap'], M['GAP']))
    return out


def geometry_gate(R):
    rows = []
    for name, cells, ref in named_shapes(R):
        res_full = upscale(cells)[LG.Y0:LG.Y1, LG.X0:LG.X1]
        iou, bd = iou_bd(res_full, ref)
        rows.append((name, iou, bd))
    return rows


# ------------------------------------------------------------------ lines
DIRS8 = {(1, 0): 0, (1, 1): 1, (0, 1): 2, (-1, 1): 3, (-1, 0): 4, (-1, -1): 5, (0, -1): 6, (1, -1): 7}


def chain_codes(mask):
    """8-direction chain codes of every contour (outer and holes) of a cell mask."""
    import cv2
    m = np.pad(mask.astype(np.uint8), 1)
    cnts, _ = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cnts:
        p = c[:, 0, :]
        if len(p) < 6:
            continue
        d = np.diff(np.vstack([p, p[:1]]), axis=0)
        out.append([DIRS8[(int(np.sign(v[0])), int(np.sign(v[1])))] for v in d if v.any()])
    return out


def staircase_regularity(mask, min_inner=2):
    """Split each contour's chain into maximal segments made of two adjacent directions
    (one digital line or staircase). In a segment the major direction forms runs between
    single minor steps; the inner runs (not the two end runs) must be equal within one or
    change monotonically. Returns (regular, total, list of irregular run sequences)."""
    ok = tot = 0
    bad = []
    for ch in chain_codes(mask):
        n = len(ch)
        # rotate so that the chain starts at a direction change
        k0 = next((i for i in range(n) if ch[i] != ch[i - 1]), 0)
        ch = ch[k0:] + ch[:k0]
        i = 0
        while i < n:
            dirs = {ch[i]}
            j = i
            while j + 1 < n:
                nd = dirs | {ch[j + 1]}
                if len(nd) > 2 or (len(nd) == 2 and (max(nd) - min(nd)) % 8 not in (1, 7)):
                    break
                dirs = nd; j += 1
            seg = ch[i:j + 1]
            if len(dirs) == 2:
                runs = []
                for c in seg:
                    if runs and runs[-1][0] == c:
                        runs[-1][1] += 1
                    else:
                        runs.append([c, 1])
                for maj in dirs:
                    mino = (dirs - {maj}).pop()
                    mins = [r[1] for r in runs if r[0] == mino]
                    if max(mins) == 1:
                        majs = [r[1] for r in runs if r[0] == maj]
                        inner = majs[1:-1]
                        if len(inner) >= min_inner:
                            tot += 1
                            dif = np.diff(inner)
                            reg = (max(inner) - min(inner) <= 1) or (dif >= 0).all() or (dif <= 0).all()
                            ok += bool(reg)
                            if not reg:
                                bad.append(inner)
                        break
            i = j + 1
    return ok, tot, bad


def stripe_gaps(s, ring):
    """ring cells not in the stripe that sit between two stripe cells which do not touch."""
    from logo_lines import nb
    cand = ring & ~s
    add = np.zeros_like(s)
    for i, (ay, ax) in enumerate(N8):
        for (by, bx) in N8[i + 1:]:
            if max(abs(ay - by), abs(ax - bx)) <= 1:
                continue
            add |= cand & nb(s, ay, ax) & nb(s, by, bx)
    return int(add.sum())


def lines_gate(R):
    G = R['G']; fill, outer = G['fill'], G['outer']
    D = LG.ring_dirs(fill)
    ring = D['up'] | D['down'] | D['left'] | D['right']
    res = {}
    res['lcorner_hi'] = int(lcorners(R['hi']).sum())
    res['lcorner_red'] = int(lcorners(R['red']).sum())
    res['gaps_hi'] = stripe_gaps(R['hi'], ring & ~R['red'])
    res['gaps_red'] = stripe_gaps(R['red'], ring & ~R['hi'])
    # navy band: thickness from fill to anything that is not the logo, in cells
    d = ndi.distance_transform_edt(outer)   # distance of each logo cell to the outside
    res['fill_cells_thinner_than_2'] = int((fill & (d <= 2.0)).sum())
    gapd = ndi.distance_transform_edt(~G['gap'])
    res['fill_cells_within_2_of_gap'] = int((fill & (gapd <= 2.0)).sum())
    # top-face outline thickness histogram (navy cells straight above a top-facing fill cell)
    th = []
    ys, xs = np.nonzero(D['up'])
    for y, x in zip(ys, xs):
        k = 0
        while y - 1 - k >= 0 and outer[y - 1 - k, x] and not fill[y - 1 - k, x] and not G['gap'][y - 1 - k, x]:
            k += 1
        if y - 1 - k >= 0 and not outer[y - 1 - k, x]:
            th.append(k)
    res['top_outline_thickness_hist'] = {int(k): int(v) for k, v in zip(*np.unique(th, return_counts=True))}
    sr = {}; lumps = {}
    for name, m in (('silhouette', outer), ('fill', fill)):
        ok, tot, bad = staircase_regularity(m, min_inner=2)
        sr[name] = (ok, tot, bad[:5])
        lm = np.zeros_like(m); nt = np.zeros_like(m)
        lab, n = ndi.label(m)
        for c in range(1, n + 1):          # per shape, so the slit between two letters is no notch
            a, b = lumps_notches(lab == c)
            lm |= a; nt |= b & ~m
        lumps[name] = dict(lumps=int(lm.sum()), notches=int(nt.sum()),
                           where=[(int(y), int(x)) for y, x in zip(*np.nonzero(lm | nt))][:12])
    res['staircase'] = sr
    res['lumps_notches'] = lumps
    return res


# ------------------------------------------------------------------ colour
def mixels(rgb, mask):
    """pixels whose colour lies between two different neighbours on opposite sides."""
    f = rgb.astype(np.float32)
    cnt = np.zeros(mask.shape, bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = np.roll(f, (dy, dx), (0, 1)); b = np.roll(f, (-dy, -dx), (0, 1))
        dab = np.linalg.norm(a - b, axis=-1)
        dap = np.linalg.norm(a - f, axis=-1); dpb = np.linalg.norm(f - b, axis=-1)
        both = np.roll(mask, (dy, dx), (0, 1)) & np.roll(mask, (-dy, -dx), (0, 1))
        between = both & (dab > 30) & (dap > 8) & (dpb > 8) & (dap + dpb <= 1.08 * dab)
        cnt |= between
    m = mask & cnt
    m[0] = m[-1] = False; m[:, 0] = m[:, -1] = False
    return m


def colour_gate(R, rgba, palette_hex):
    m = rgba[..., 3] > 0
    rgb = rgba[..., :3]
    pal = np.array([hx(h[1:]) for h in palette_hex])
    d = np.abs(rgb[m][:, None, :].astype(int) - pal[None].astype(int)).sum(-1).min(1)
    off = int((d > 0).sum())
    # no green, beige or brown in the palette: hue/saturation check
    def kind(c):
        r, g, b = [int(v) for v in c]
        if g > r and g > b and g - max(r, b) > 20:
            return 'green'
        if r > b and g > b and abs(r - g) < 40 and r < 230 and b > 60:
            return 'beige'
        if r > g > b and r < 150 and g > 40:
            return 'brown'
        return None
    bad = [h for h, c in zip(palette_hex, pal) if kind(c)]
    mx = mixels(rgb, m)
    return dict(off_palette=off, bad_hues=bad, mixels=int(mx.sum()), mixel_map=mx)


# ------------------------------------------------------------------ pattern
def pattern_gate(R):
    """Every dithered fill cell carries exactly the colour its level's pattern gives on the fixed
    screen phase; the 50 % rows are the exact checker."""
    G = R['G']; idx = R['idx']; lvl = R['level']
    fill = G['fill'] & ~R['hi'] & ~R['red'] & ~R.get('lite', np.zeros_like(G['fill']))
    exp = np.full((NY, NX), -1)
    for k in np.unique(lvl[fill]):
        b, a, d = LG.ramp_tones(int(k))
        m = fill & (lvl == k)
        exp[m] = LG.IDX[b]; exp[m & LG.pattern(d)] = LG.IDX[a]
    wrong = fill & (idx != exp)
    yy, xx = np.indices((NY, NX))
    band = fill & (lvl == 4)
    phase_bad = band & ((idx == LG.IDX['orange']) != ((yy + xx) % 2 == 0))
    return dict(cells=int(fill.sum()), wrong_rule=int(wrong.sum()), band50_cells=int(band.sum()),
                band50_out_of_phase=int(phase_bad.sum()), levels_used=sorted(int(v) for v in np.unique(lvl[fill])))


# ------------------------------------------------------------------ form
def form_gate(rgba, mask):
    src = load_src()
    Y = luma(src)
    I, J = cell_index(H_SRC, W_SRC)
    cell = (J.astype(np.int64) * NX + I).ravel()
    orig = (np.bincount(cell, weights=Y.ravel(), minlength=NX * NY) / np.bincount(cell, minlength=NX * NY)).reshape(NY, NX)
    res = np.where(rgba[..., 3] > 0, luma(rgba[..., :3]), orig)
    bo = ndi.uniform_filter(orig, 5); br = ndi.uniform_filter(res, 5)
    d = np.abs(bo - br)[mask]
    return dict(mean=float(d.mean()), p95=float(np.percentile(d, 95)), max=float(d.max()))


def lumps_notches(m):
    """one- or two-cell lumps on an edge (cells a 3x3 opening removes) and notches (cells a
    3x3 closing adds). Square corners and straight or staircase edges of any slope survive
    both; only protrusions and dents thinner than three cells are counted."""
    k = np.ones((3, 3), bool)
    mp = np.pad(m, 3)
    op = ndi.binary_opening(mp, structure=k)[3:-3, 3:-3]
    cl = ndi.binary_closing(mp, structure=k)[3:-3, 3:-3]
    return m & ~op, cl & ~m


def form_gate_fair(rgba, mask, sigma=1.5):
    """Fair form test asked by the producer: Gaussian blur (sigma 1.5 cells) of the luma of
    the result (painting box average outside the owned cells) vs the same blur of the painting
    box-averaged to 320 x 240; target mean < 4, p95 < 10."""
    from PIL import Image
    src = Image.open(SRC).convert('RGB').resize((NX, NY), Image.BOX)
    orig = luma(np.array(src))
    res = np.where(rgba[..., 3] > 0, luma(rgba[..., :3]), orig)
    d = np.abs(ndi.gaussian_filter(orig, sigma) - ndi.gaussian_filter(res, sigma))[mask]
    return dict(mean=float(d.mean()), p95=float(np.percentile(d, 95)), max=float(d.max()))


def row_luma_gate(R):
    """Per shape (letters, pad, toes), per cell row: mean luma of the result's fill vs the
    painting. 'dither' = the shape's dithered cells (the ramp; edge cells excluded where the row
    has inner cells), painting luma averaged over exactly those cells. 'all' = every fill cell
    of the row vs the painting's own fill paint (warm pixels of that letter) in the same rows,
    so the painting's anti-aliased navy edges do not count as fill."""
    G = R['G']; fill = G['fill']; idx = R['idx']; pal = R['pal']; src = R['src_l']
    L, M = R['L'], R['M']
    rgb = np.zeros((NY, NX, 3)); rgb[idx >= 0] = pal[idx[idx >= 0]]
    ol = luma(rgb)
    D = LG.ring_dirs(fill); ring = D['up'] | D['down'] | D['left'] | D['right']
    stripes = R['hi'] | R['red'] | R['lite']
    a = load_src()[LG.Y0:LG.Y1, LG.X0:LG.X1]; lu = luma(a)
    I, J = cell_index(H_SRC, W_SRC); Jc, Ic = J[LG.Y0:LG.Y1, LG.X0:LG.X1], I[LG.Y0:LG.Y1, LG.X0:LG.X1]
    pl, pn = ndi.label(M['F'])
    lab, n = ndi.label(fill)
    out = {}
    for c in range(1, n + 1):
        m = lab == c
        name = 'x%d' % int(np.nonzero(m)[1].mean())
        full = upscale(m)[LG.Y0:LG.Y1, LG.X0:LG.X1]
        v = pl[full]; v = v[v > 0]
        pm = (pl == np.bincount(v).argmax()) if len(v) else np.zeros_like(M['F'])
        res = {}
        body = m & ~stripes
        d = []; small = []
        for r in np.flatnonzero(body.any(1)):
            core = body[r] & ~ring[r]
            sel = core if core.sum() >= 2 else body[r]
            v = ol[r][sel].mean() - src[r][sel].mean()
            (d if sel.sum() >= 5 else small).append(v)     # a row of < 5 cells cannot hold a
        d = np.array(d) if d else np.zeros(1)               # density finer than 1/4 (17 luma)
        res['dither'] = (round(float(np.abs(d).max()), 2), round(float(np.abs(d).mean()), 2), int(len(d)))
        res['short_rows_max'] = round(float(np.abs(small).max()), 1) if small else 0.0
        d = []
        for r in np.flatnonzero(m.any(1)):
            pp = pm & (Jc == r)
            if pp.sum() < 20:
                continue
            d.append(ol[r][m[r]].mean() - lu[pp].mean())
        d = np.array(d)
        res['all'] = (round(float(np.abs(d).max()), 2), round(float(np.abs(d).mean()), 2), int(len(d)))
        out[name] = res
    return out


def lone_dither_rows(R):
    """cells of a dithered density whose row is sandwiched between two flat (solid) rows in the
    same column of the same shape: a lone dotted row."""
    lv = R['level']; fill = R['G']['fill']
    f = fill & ~(R['hi'] | R['red'] | R['lite'])
    flat = np.isin(lv, [-8, 0, 8, 16])
    up_f = shift(f, -1, 0) & shift(flat, -1, 0)
    dn_f = shift(f, 1, 0) & shift(flat, 1, 0)
    return int((f & ~flat & up_f & dn_f).sum())
