"""QA gates, 10x comparison images and the font sheet for the tagline track."""
import os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import tagline as T
import tagline_font as TF

NX, NY = T.NX, T.NY


# ----------------------------------------------------------------- gates
def grid_alignment(S, thr=40):
    """fraction of strong colour changes (non-max suppressed along the axis) within 1 px of a
    refined cell border, over the plate's bounding box."""
    a = S['a']; g = S['grid']
    x0, x1, y0, y1 = 1120, 2192, 572, 734
    reg = a[y0:y1, x0:x1]
    gx = np.abs(np.diff(reg, axis=1)).max(2)          # between x and x+1 -> border at x+1
    gy = np.abs(np.diff(reg, axis=0)).max(2)
    def nms(gr, axis):
        p = np.pad(gr, [(1, 1) if ax == axis else (0, 0) for ax in range(2)], mode='edge')
        if axis == 1:
            l, c, r = p[:, :-2], p[:, 1:-1], p[:, 2:]
        else:
            l, c, r = p[:-2], p[1:-1], p[2:]
        return (c >= l) & (c >= r) & (c > thr)
    ex = nms(gx, 1); ey = nms(gy, 0)
    bx = np.array(g['X']); by = np.array(g['Y'])
    xs = np.arange(x0, x1 - 1) + 1.0
    ys = np.arange(y0, y1 - 1) + 1.0
    dx = np.abs(xs[:, None] - bx[None]).min(1)
    dy = np.abs(ys[:, None] - by[None]).min(1)
    okx = (dx <= 1.0)[None].repeat(ex.shape[0], 0)[ex]
    oky = (dy <= 1.0)[:, None].repeat(ey.shape[1], 1)[ey]
    return dict(x=round(float(okx.mean()), 3), y=round(float(oky.mean()), 3),
                all=round(float(np.concatenate([okx, oky]).mean()), 3), n=int(okx.size + oky.size))


def geometry(S):
    g = S['grid']; PM = S['PM']; P = S['plate']
    up = lambda m: T.upscale(g, m)
    res = {}
    shapes = {
        'plate_outer': (P['F'] | P['outline'], PM['outer']),
        'rim_filled': (P['F'], PM['fill']),
        'body': (P['body'], PM['body']),
        'rim_ring': (P['rim'], PM['rim']),
        'text': (S['tm'], PM['text']),
    }
    for name, (m, ref) in shapes.items():
        u = up(m)
        res[name] = dict(iou=round(T.iou(u, ref), 4), bdist=round(T.bdist(u, ref), 3))
    # per word
    words = T.TEXT.split(' ')
    lay = TF.layout(T.TEXT, S['lay']['start'])
    i = 0
    for w in words:
        gl = lay[i:i + len(w)]; inst = S['inst'][i:i + len(w)]
        c0 = gl[0][1]; c1 = gl[-1][1] + TF.width(gl[-1][0])
        xa = int(inst[0]['x0']) - 4; xb = int(inst[-1]['x1']) + 4
        m = np.zeros_like(S['tm']); m[:, c0:c1] = S['tm'][:, c0:c1]
        u = up(m)[:, xa - T.RX0:xb - T.RX0]; ref = PM['text'][:, xa - T.RX0:xb - T.RX0]
        res['word_' + w] = dict(iou=round(T.iou(u, ref), 4), bdist=round(T.bdist(u, ref), 3))
        i += len(w)
    return res


def lines(S):
    rim = S['plate']['rim']
    H, W = rim.shape
    n8 = sum(np.roll(np.roll(rim, dy, 0), dx, 1).astype(int) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    # L-corner double: pixel with a horizontal and a vertical ring neighbour that touch diagonally
    lc = 0
    ys, xs = np.nonzero(rim)
    for y, x in zip(ys, xs):
        for hx in (-1, 1):
            for vy in (-1, 1):
                if rim[y, x + hx] and rim[y + vy, x] and n8[y, x] == 2:
                    lc += 1
    lab, ncomp = ndi.label(rim, np.ones((3, 3)))
    gaps = int((rim & (n8 < 2)).sum()) + (ncomp - 1)
    branch = int((rim & (n8 > 2)).sum())
    # staircase regularity: trace each chamfer (pixels between the straight sides) and get its runs
    P = S['P']
    segs = []
    for (ra, rb, side) in [((P['rim_top'], P['rim_left']), None, 'tl')]:
        pass
    def runs_of(pts):
        """vertical run length per column and horizontal run length per row of a staircase."""
        cols = {}; rows = {}
        for c, r in pts:
            cols[c] = cols.get(c, 0) + 1; rows[r] = rows.get(r, 0) + 1
        return [cols[c] for c in sorted(cols)], [rows[r] for r in sorted(rows)]
    def monotone(v):
        return all(a <= b for a, b in zip(v, v[1:])) or all(a >= b for a, b in zip(v, v[1:]))
    kt, kb = len(P['corner_top']) + 1, len(P['corner_bot']) + 1
    rt, rb_, rl, rr = P['rim_top'], P['rim_bot'], P['rim_left'], P['rim_right']
    # the diagonal part only: rows strictly between the straight rim row and the vertical side
    def diag(rows_, side):
        pts = []
        for r in rows_:
            cs = np.nonzero(rim[r, rl:rr + 1])[0] + rl
            cs = cs[cs <= rl + kt + kb] if side == 'L' else cs[cs >= rr - kt - kb]
            pts += [(int(c), int(r)) for c in cs]
        return pts
    vstart = rt + len(T.corner_insets(P['corner_top'])) if P['corner_top'] is not None else rt + 1
    vend = rb_ - len(T.corner_insets(P['corner_bot'])) if P['corner_bot'] is not None else rb_ - 1
    chams = {'top_left': diag(range(rt + 1, vstart), 'L'), 'top_right': diag(range(rt + 1, vstart), 'R'),
             'bot_left': diag(range(vend + 1, rb_), 'L'), 'bot_right': diag(range(vend + 1, rb_), 'R')}
    reg = 0; info = {}
    for name, pts in chams.items():
        vr, hr = runs_of(pts)
        ok = monotone(vr) and monotone(hr)
        reg += ok; info[name] = dict(vertical_runs=vr, horizontal_runs=hr, regular=ok)
    # outline: the owned navy band must be 4-connected to the plate (no stray specks)
    return dict(lcorners=lc, gaps=gaps, branches=branch, components=int(ncomp),
                staircase_regularity=round(reg / len(chams), 3), chamfer_runs=info)


def colour(S):
    img = S['img']; own = S['own']
    pal = [tuple(S['pal'][k]) for k in ('navy', 'rim', 'cream')]
    px = img[own][:, :3]
    off = int(sum(1 for p in map(tuple, px) if p not in pal))
    L = T.luma(img[:, :, :3].astype(float))
    mix = 0
    ys, xs = np.nonzero(own)
    for y, x in zip(ys, xs):
        c = L[y, x]
        for (dy, dx) in ((0, 1), (1, 0)):
            ya, xa, yb, xb = y - dy, x - dx, y + dy, x + dx
            if not (own[ya, xa] and own[yb, xb]):
                continue
            la, lb = L[ya, xa], L[yb, xb]
            if abs(la - lb) > 1 and abs(c - la) > 1 and abs(c - lb) > 1 and min(la, lb) < c < max(la, lb):
                mix += 1
    ncol = len(set(map(tuple, px)))
    txt = S['tm']
    tcols = set(map(tuple, img[S['plate']['body']][:, :3]))
    return dict(off_palette=off, mixels=mix, colours=ncol, body_colours=len(tcols))


def form(S):
    """5x5 box blur of luma over the cell grid: result vs original cell means (refined cells)."""
    own = S['own']
    orig = S['meanL'].copy()
    res = orig.copy()
    res[own] = T.luma(S['img'][own][:, :3].astype(float))
    bo = ndi.uniform_filter(orig, 5); br = ndi.uniform_filter(res, 5)
    d = np.abs(bo - br)[own]
    return dict(mean=round(float(d.mean()), 2), p95=round(float(np.percentile(d, 95)), 2), max=round(float(d.max()), 2))


def glyph_checks(S):
    tm = S['tm']
    lay = TF.layout(T.TEXT, S['lay']['start'])
    crops = {}
    for ch, x in lay:
        w = TF.width(ch)
        crops.setdefault(ch, []).append(tm[T.CAP_ROW:T.CAP_ROW + 9, x:x + w].copy())
    ident = {ch: all(np.array_equal(v[0], c) for c in v) for ch, v in crops.items() if len(v) > 1}
    blocks = bool((tm[1:, 1:] & tm[:-1, 1:] & tm[1:, :-1] & tm[:-1, :-1]).any())
    # stroke width: every ink run along x and y inside a glyph is 1 px except deliberate bars
    gaps = [lay[i + 1][1] - (lay[i][1] + TF.width(lay[i][0])) for i in range(len(lay) - 1)]
    return dict(repeated_identical=ident, any_2x2_block=blocks, letter_gaps=sorted(set(gaps)))


def text_width_px(tm):
    return int(tm.any(0).sum())


# ----------------------------------------------------------------- images
def orig_crop(S, c0, c1, r0, r1, scale=10):
    a = S['a']
    x0, x1, y0, y1 = c0 * 7.5, c1 * 7.5, r0 * 7.5, r1 * 7.5
    im = Image.fromarray(a[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))].astype(np.uint8))
    return im.resize(((c1 - c0) * scale, (r1 - r0) * scale), Image.LANCZOS)


def orig_px(S, x0, x1, y0=607.5, y1=697.5, scale=10):
    a = S['a']
    im = Image.fromarray(a[int(y0):int(y1), int(x0):int(x1)].astype(np.uint8))
    return im.resize((int(round((x1 - x0) * scale / 7.5)), int(round((y1 - y0) * scale / 7.5))), Image.LANCZOS)


def res_crop(S, c0, c1, r0, r1, scale=10, img=None, bg=(255, 0, 255)):
    img = S['img'] if img is None else img
    sub = img[r0:r1, c0:c1]
    rgb = np.where(sub[:, :, 3:4] > 0, sub[:, :, :3], np.array(bg, np.uint8)[None, None])
    # show the painting through the transparent cells, darkened, for context
    return Image.fromarray(rgb.astype(np.uint8)).resize(((c1 - c0) * scale, (r1 - r0) * scale), Image.NEAREST)


def ctx_crop(S, c0, c1, r0, r1, scale=10, img=None):
    """result composited over a coarse version of the painting (transparent cells show a 7.5 px
    box sample of the painting, dimmed), so the plate is seen in place."""
    img = S['img'] if img is None else img
    a = S['a']
    base = np.zeros((r1 - r0, c1 - c0, 3))
    for r in range(r0, r1):
        for c in range(c0, c1):
            base[r - r0, c - c0] = a[int(r * 7.5):int((r + 1) * 7.5), int(c * 7.5):int((c + 1) * 7.5)].reshape(-1, 3).mean(0)
    base = base * 0.55 + 40
    sub = img[r0:r1, c0:c1]
    rgb = np.where(sub[:, :, 3:4] > 0, sub[:, :, :3], base)
    return Image.fromarray(rgb.astype(np.uint8)).resize(((c1 - c0) * scale, (r1 - r0) * scale), Image.NEAREST)


def stack(ims, vertical=True, pad=6, col=(255, 0, 255)):
    if vertical:
        W = max(i.width for i in ims); H = sum(i.height for i in ims) + pad * (len(ims) - 1)
    else:
        W = sum(i.width for i in ims) + pad * (len(ims) - 1); H = max(i.height for i in ims)
    out = Image.new('RGB', (W, H), col)
    o = 0
    for i in ims:
        out.paste(i, ((W - i.width) // 2, o) if vertical else (o, (H - i.height) // 2))
        o += (i.height if vertical else i.width) + pad
    return out


def comparisons(S, out):
    P = S['P']
    c0, c1 = P['rim_left'] - 3, P['rim_right'] + 4
    r0, r1 = P['rim_top'] - 3, P['rim_bot'] + 4
    paths = []
    im = stack([orig_crop(S, c0, c1, r0, r1), ctx_crop(S, c0, c1, r0, r1)])
    p = os.path.join(out, 'cmp_plate.png'); im.save(p); paths.append(p)
    # halves at a larger look: left end and right end
    for name, (a0, a1) in {'left': (c0, c0 + 40), 'right': (c1 - 40, c1)}.items():
        im = stack([orig_crop(S, a0, a1, r0, r1), ctx_crop(S, a0, a1, r0, r1)], vertical=False)
        p = os.path.join(out, 'cmp_end_%s.png' % name); im.save(p); paths.append(p)
    # words
    lay = TF.layout(T.TEXT, S['lay']['start'])
    i = 0
    for w in T.TEXT.split(' '):
        gl = lay[i:i + len(w)]
        a0 = gl[0][1] - 2; a1 = gl[-1][1] + TF.width(gl[-1][0]) + 2
        # painting span may be wider: take the union of both spans
        inst = S['inst'][i:i + len(w)]
        b0 = int(np.floor(inst[0]['x0'] / 7.5)) - 2; b1 = int(np.ceil(inst[-1]['x1'] / 7.5)) + 2
        a0 = min(a0, b0); a1 = max(a1, b1)
        im = stack([orig_crop(S, a0, a1, 81, 93), res_crop(S, a0, a1, 81, 93)])
        p = os.path.join(out, 'cmp_word_%s.png' % w); im.save(p); paths.append(p)
        i += len(w)
    # repeated letters: each instance, painting above, result below
    rows = []
    letters = [g['ch'] for g in S['inst']]
    for ch in sorted(set(letters), key=letters.index):
        idx = [k for k, c in enumerate(letters) if c == ch]
        if len(idx) < 2:
            continue
        cells = []
        for k in idx:
            g = S['inst'][k]; x = lay[k][1]; w = TF.width(ch)
            o = orig_px(S, g['x0'] - 6, g['x1'] + 6)
            r = res_crop(S, x - 1, x + w + 1, 81, 93)
            cells.append(stack([o, r]))
        rows.append(stack(cells, vertical=False, pad=14))
    im = stack(rows, pad=14, col=(40, 40, 40))
    p = os.path.join(out, 'cmp_repeated_letters.png'); im.save(p); paths.append(p)
    # every letter (single instances too)
    cells = []
    for k, g in enumerate(S['inst']):
        x = lay[k][1]; w = TF.width(g['ch'])
        cells.append(stack([orig_px(S, g['x0'] - 6, g['x1'] + 6), res_crop(S, x - 1, x + w + 1, 81, 93)]))
    im = stack(cells, vertical=False, pad=8, col=(40, 40, 40))
    p = os.path.join(out, 'cmp_all_letters.png'); im.save(p); paths.append(p)
    # blank plate
    im = stack([orig_crop(S, c0, c1, r0, r1), ctx_crop(S, c0, c1, r0, r1, img=S['blank'])])
    p = os.path.join(out, 'cmp_plate_blank.png'); im.save(p); paths.append(p)
    return paths


def font_sheet(S, out):
    chars = (list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") +
             list("0123456789") + list("!?.,'-:"))
    cell_w, cell_h = 6, 10          # 5 px max glyph + 1 gap, 9 rows + 1
    per_row = 26
    nrow = (len(chars) + per_row - 1) // per_row
    navy, cream, rim = [tuple(S['pal'][k]) for k in ('navy', 'cream', 'rim')]
    sheet = np.zeros((nrow * cell_h, per_row * cell_w, 4), np.uint8)
    meta = dict(cell=[cell_w, cell_h], rows=9, cap_height=7, x_height=5, descender=2, baseline_row=6,
                letter_gap=TF.GAP, space=TF.SPACE, stroke=1, colour=dict(ink='#%02x%02x%02x' % cream,
                                                                      ground='#%02x%02x%02x' % navy),
                note=("Glyph boxes are left-aligned in their sheet cell; 'x','y' are the cell's top-left in "
                      "font_glyphs.png, 'w' the glyph width, 'top' the first ink row in the 9-row box, "
                      "'bitmap' the rows from 'top'. 'source' is 'painting' for letters measured from the "
                      "painting, 'drawn' for letters drawn to match."),
                glyphs={})
    for i, ch in enumerate(chars):
        top, rows = TF.glyph(ch)
        gx, gy = (i % per_row) * cell_w, (i // per_row) * cell_h
        for r, line in enumerate(rows):
            for c, v in enumerate(line):
                if v == '#':
                    sheet[gy + top + r, gx + c] = (*cream, 255)
        meta['glyphs'][ch] = dict(x=gx, y=gy, w=len(rows[0]), top=top, bitmap=rows,
                                  source='painting' if ch in TF.RECOVERED else 'drawn')
    Image.fromarray(sheet).save(os.path.join(out, 'font_glyphs.png'))
    json.dump(meta, open(os.path.join(out, 'font_glyphs.json'), 'w'), indent=1)
    # a 6x preview on navy, painted letters cream, drawn letters a lighter tint to tell them apart
    prev = np.zeros(sheet.shape[:2] + (3,), np.uint8); prev[:] = navy
    for i, ch in enumerate(chars):
        top, rows = TF.glyph(ch)
        gx, gy = (i % per_row) * cell_w, (i // per_row) * cell_h
        col = cream if ch in TF.RECOVERED else (170, 220, 255)
        for r, line in enumerate(rows):
            for c, v in enumerate(line):
                if v == '#':
                    prev[gy + top + r, gx + c] = col
    pad = np.zeros((prev.shape[0] + 2, prev.shape[1] + 2, 3), np.uint8); pad[:] = navy; pad[1:-1, 1:-1] = prev
    Image.fromarray(pad).resize((pad.shape[1] * 8, pad.shape[0] * 8), Image.NEAREST).save(
        os.path.join(out, 'font_glyphs_preview8x.png'))
    # a sample line in the font on the blank plate
    return meta


def main(S, out=None):
    out = out or T.OUT
    M = dict(grid=grid_alignment(S), geometry=geometry(S), lines=lines(S), colour=colour(S), form=form(S),
             glyphs=glyph_checks(S), layout=S['lay'], plate=S['P'])
    paths = comparisons(S, out)
    font_sheet(S, out)
    json.dump(M, open(os.path.join(out, 'metrics.json'), 'w'), indent=1, default=str)
    print(json.dumps(M, indent=1, default=str))
    return M, paths
