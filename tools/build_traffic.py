#!/usr/bin/env python3
"""build_traffic.py: the River Walk traffic family (5 Nov 2026), cut from SpriteCook renders 1:1. Never resampled.

  python3 -I tools/build_traffic.py cut NAME RENDER.png        -> art/source/NAME/NAME_cut.png + art/gen/out/NAME.cut.json
  python3 -I tools/build_traffic.py wheels NAME                -> art/source/NAME/NAME_wheels.png (cyclists: wheels redrawn)

cut: SpriteCook pixel mode at 1K returns the 256 frame at about 1 px = 1 art px (docs/art_generation.md), so every
render pixel is one art pixel (pitch 1). The magenta and the pink pixels where the model blended into it are keyed
(only pixels touching the key: the riders' red coats stay), Pepper (the scale reference) and loose specks of a new
cut are dropped, every pixel is snapped to the level palette (art/palettes/riverwalk.gpl, nearest in Lab, no new
colour, no averaging), and the least used colours are merged into their nearest kept colour until the layer's cap
less 2 (room for the polish). The measures are compared with the blockout as grid_cut.py does.

wheels: a bicycle wheel is a repeated part (docs/asset_qa.md checklist 1-2): both wheels are drawn by rule from the
cut's own ink and grey, round, with even spokes, on the centres the render put them (fitted on the tyre ring).
Every changed pixel is listed in art/source/NAME/edits.json."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_palette import lab

R = json.load(open('art/gen/rules.json'))


def palette(level):
    f = R['palettes'][level]
    return np.array([[int(v) for v in l.split()[:3]] for l in open(f) if l.split() and l.split()[0].isdigit()], float)


def grow(m, n=1):
    m = m.copy()
    for _ in range(n):
        m[1:] |= m[:-1]; m[:-1] |= m[1:]; m[:, 1:] |= m[:, :-1]; m[:, :-1] |= m[:, 1:]
    return m


def label(m):
    """4-connected components without scipy."""
    h, w = m.shape; lab_ = np.zeros((h, w), int); n = 0
    for y in range(h):
        for x in range(w):
            if m[y, x] and not lab_[y, x]:
                n += 1; st = [(y, x)]; lab_[y, x] = n
                while st:
                    cy, cx = st.pop()
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab_[ny, nx]:
                            lab_[ny, nx] = n; st.append((ny, nx))
    return lab_, n


def cut(name, src):
    J = json.load(open(f'art/gen/jobs/{name}.json')); lay = R['layers'][J['layer']]
    mask = np.array(Image.open(f'art/gen/blockouts/{name}_mask.png')) > 0
    a = np.array(Image.open(src).convert('RGB')).astype(int)
    H, W = mask.shape; a = a[:H, :W] if a.shape[0] >= H and a.shape[1] >= W else np.pad(a, ((0, max(0, H - a.shape[0])), (0, max(0, W - a.shape[1])), (0, 0)), constant_values=0)[:H, :W]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    key = (r - g > 35) & (b - g > 35) & (r > 120) & (b > 120)
    # blends into the magenta: pinkish-purple pixels joined to the key (repeat: fringes 2 px deep)
    blend = (r - g > 18) & (b - g > 18) & (b > 90)
    for _ in range(3):
        key |= blend & grow(key, 1)
    fg = ~key
    lbl, n = label(fg)
    near = grow(mask, 6)
    keep = np.zeros_like(fg)
    sizes = np.bincount(lbl.ravel())
    for i in range(1, n + 1):
        comp = lbl == i
        if not (comp & near).any(): continue                     # Pepper and anything off the subject
        if sizes[i] < 6 and not (comp & grow(keep | (lbl == np.argmax(sizes[1:]) + 1), 1)).any(): continue
        keep |= comp
    # loose specks of the new cut: components of under 6 px not touching the main body
    lbl2, n2 = label(keep); s2 = np.bincount(lbl2.ravel()); s2[0] = 0
    for i in range(1, n2 + 1):
        if s2[i] < 6: keep[lbl2 == i] = False
    pal = palette(J['level']); px = a.reshape(-1, 3).astype(float)
    sel = keep.ravel()
    idx = np.argmin(((lab(px[sel])[:, None] - lab(pal)[None]) ** 2).sum(2), 1)
    cap = lay['colours'] - 2
    used, cnt = np.unique(idx, return_counts=True)
    # one ink: every palette near-black (luma under 14) becomes the most used of them (art direction: one ink colour)
    lum = pal @ [0.299, 0.587, 0.114]
    darks = [u for u in used if lum[u] < 14]
    if len(darks) > 1:
        ink = max(darks, key=lambda u: cnt[list(used).index(u)])
        for u in darks: idx[idx == u] = ink
        used, cnt = np.unique(idx, return_counts=True)
    # near twins (Lab distance under 7) merge into the more used one: shading in ramps, not in noise
    while len(used) > 1:
        L = lab(pal[used]); d = ((L[:, None] - L[None]) ** 2).sum(2) ** 0.5; np.fill_diagonal(d, 1e9)
        i, j = np.unravel_index(np.argmin(d), d.shape)
        if d[i, j] >= 7: break
        lo, hi = (used[i], used[j]) if cnt[i] < cnt[j] else (used[j], used[i])
        idx[idx == lo] = hi; used, cnt = np.unique(idx, return_counts=True)
    while len(used) > cap:                                         # merge the least used into its nearest kept colour
        j = used[np.argmin(cnt)]; rest = used[used != j]
        t = rest[np.argmin(((lab(pal[[j]]) - lab(pal[rest])) ** 2).sum(1))]
        idx[idx == j] = t; used, cnt = np.unique(idx, return_counts=True)
    out = np.zeros((H, W, 4), np.uint8)
    o = out.reshape(-1, 4); o[sel, :3] = pal[idx].astype(np.uint8); o[sel, 3] = 255
    ys, xs = np.nonzero(keep); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    im = Image.fromarray(out, 'RGBA').crop(box)
    os.makedirs(f'art/source/{name}', exist_ok=True)
    im.save(f'art/source/{name}/{name}_cut.png'); im.save(f'art/gen/out/{name}.png')
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(f'art/gen/out/{name}_4x.png')
    sw, sh = im.size; tw, th = J['target_px']
    prec = (keep & grow(mask, 2)).sum() / keep.sum(); rec = (mask & grow(keep, 2)).sum() / mask.sum()
    fails = []
    if abs(sw - tw) / tw > 0.08 or abs(sh - th) / th > 0.08: fails.append(f'size {sw}x{sh} vs {tw}x{th}')
    if prec < 0.85: fails.append(f'only {prec:.0%} of the drawing lands on the blockout')
    if rec < 0.80: fails.append(f'only {rec:.0%} of the blockout is drawn')
    res = dict(name=name, size=[int(sw), int(sh)], target=[tw, th], grid_clean=1.0, on_blockout=round(float(prec), 3),
               covered=round(float(rec), 3), stray=0.0, colours_in=int(len(np.unique(px[sel], axis=0))),
               colours_cap=lay['colours'], colours_out=int(len(used)), fails=fails, render=src, box=[int(v) for v in box],
               cut_by='tools/build_traffic.py cut (1x render, pitch 1, palette snap riverwalk.gpl, no resampling)')
    json.dump(res, open(f'art/gen/out/{name}.cut.json', 'w'), indent=1)
    print(f"{'CUT PASS' if not fails else 'CUT FAIL'} {name}: {sw}x{sh} vs {tw}x{th}, {prec:.0%} on blockout, "
          f"{rec:.0%} covered, {res['colours_in']} -> {len(used)} colours", *fails)
    return not fails


if __name__ == '__main__':
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == 'cut': sys.exit(0 if cut(name, sys.argv[3]) else 1)


def fit_wheel(a, gx, gy, rs=(14, 15, 16)):
    """The tyre ring's centre and radius near (gx, gy): most dark pixels on the ring d = R +- 0.5."""
    dark = (a[..., 3] > 0) & ((a[..., :3].astype(int) @ [299, 587, 114]) < 70000)
    h, w = dark.shape; Y, X = np.mgrid[0:h, 0:w]; best = None
    for R_ in rs:
        for cy in range(gy - 7, gy + 8):
            for cx in range(gx - 7, gx + 8):
                d = np.hypot(X - cx, Y - cy); ring = (d >= R_ - 0.5) & (d < R_ + 0.5)
                s = (dark & ring).sum() / ring.sum()
                if best is None or s > best[0]: best = (s, cx, cy, R_)
    return best


def wheel_px(cx, cy, R_, spokes, rot, col):
    """Pixels of one wheel drawn by rule: ink tyre edge, tyre, rim, even spokes, hub. Returns {(x, y): rgb}."""
    out = {}
    for y in range(cy - R_ - 1, cy + R_ + 2):
        for x in range(cx - R_ - 1, cx + R_ + 2):
            k = int(round(np.hypot(x - cx, y - cy)))
            if k == R_: out[(x, y)] = col['ink']                     # the tyre's outline
            elif k == R_ - 1: out[(x, y)] = col['rim']                # the steel rim, one light line
            elif k == R_ - 2: out[(x, y)] = col['ink']                # its inner edge (outline towards the see-through)
            elif k <= 1: out[(x, y)] = col['ink'] if k == 1 else col['hub']
    for s in range(spokes):
        t = np.radians(rot + s * 360 / spokes)
        for q in np.arange(2.0, R_ - 1.5, 0.2):
            x, y = int(round(cx + q * np.cos(t))), int(round(cy + q * np.sin(t)))
            if (x, y) not in out: out[(x, y)] = col['spoke']
    return out


def wheels(name, src=None, dst=None, rot=0.0, centres=None):
    """Redraw both wheels of a cyclist. Inside each wheel's disc the cut's pixels are kept only where they are part
    of the bike or the rider (components of 8 px or more inside the disc, or joined to the frame outside it); the
    tyre ring is the new wheel's. Writes the edits list."""
    src = src or f'art/source/{name}/{name}_cut.png'; dst = dst or f'art/source/{name}/{name}_wheels.png'
    a = np.array(Image.open(src).convert('RGBA')); h, w = a.shape[:2]
    cj = json.load(open(f'art/gen/out/{name}.cut.json')); bx, by = cj['box'][:2]
    bom = json.load(open(f'art/gen/blockouts/{name}.json')); G = bom['ground']
    guess = [(144 - bx, G - 16 - by), (195 - bx, G - 16 - by)]
    fits = centres or [fit_wheel(a, gx, gy)[1:] for gx, gy in guess]
    pal = {tuple(c) for c in a[a[..., 3] > 0][:, :3].tolist()}
    byl = sorted(pal, key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])
    grey = [c for c in byl if max(c) - min(c) < 24]
    near = lambda L: min(grey, key=lambda c: abs(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] - L))
    col = dict(ink=byl[0], tyre=near(55), rim=near(160), spoke=near(55), hub=near(120))
    edits, out = [], a.copy()
    for cx, cy, R_ in fits:
        Y, X = np.mgrid[0:h, 0:w]; d = np.hypot(X - cx, Y - cy)
        disc = d < R_ + 0.5
        inner = (d < R_ - 1.5) & (a[..., 3] > 0)
        # inner pixels to keep: big pieces (frame, chain guard, foot), not spoke remnants
        lbl, n = label(inner); sizes = np.bincount(lbl.ravel())
        outside = (a[..., 3] > 0) & ~disc
        keepm = np.zeros_like(inner)
        for i in range(1, n + 1):
            comp = lbl == i
            if sizes[i] >= 8 or (grow(comp, 1) & outside).any(): keepm |= comp
        for (x, y) in zip(*np.nonzero(disc.T)):
            if not keepm[y, x] and a[y, x, 3] > 0 or (d[y, x] >= R_ - 1.5 and a[y, x, 3] > 0):
                out[y, x] = 0
        for (x, y), c in wheel_px(cx, cy, R_, 8, rot, col).items():
            if 0 <= x < w and 0 <= y < h and not (keepm[y, x] and d[y, x] < R_ - 1.5):
                out[y, x] = (*c, 255)
    for y, x in zip(*np.nonzero((out != a).any(2))):
        edits.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in a[y, x]], 'to': [int(v) for v in out[y, x]],
                      'why': 'wheel redrawn by rule: round, 8 even spokes'})
    Image.fromarray(out, 'RGBA').save(dst)
    print(name, 'wheels at', fits, 'colours', col, len(edits), 'px changed')
    return fits, edits


if __name__ == '__main__' and sys.argv[1] == 'wheels':
    f, e = wheels(sys.argv[2])
    json.dump({'step': 'wheels', 'centres': [list(map(int, c)) for c in f], 'edits': e},
              open(f'art/source/{sys.argv[2]}/edits_wheels.json', 'w'))


def fix_key(src, dst, key=((155, 46, 118), (196, 60, 150), (149, 69, 178))):
    """Pink-purple pixels left from the magenta key: on the edge they go, inside they take their neighbours' colour."""
    a = np.array(Image.open(src).convert('RGBA')); out = a.copy(); h, w = a.shape[:2]; ed = []
    for y, x in zip(*np.nonzero(np.isin(a[..., :3].reshape(-1, 3).view([('', 'u1')] * 3).ravel(),
                                        np.array(key, np.uint8).view([('', 'u1')] * 3).ravel()).reshape(h, w) & (a[..., 3] > 0))):
        nb = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < h and 0 <= xx < w]
        if any(n[3] == 0 for n in nb): out[y, x] = 0
        else:
            cand = [n for n in nb if tuple(n[:3]) not in key]
            if cand: out[y, x] = max(set(cand), key=cand.count)
        ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in a[y, x]], 'to': [int(v) for v in out[y, x]],
                   'why': 'pink key remnant'})
    Image.fromarray(out).save(dst); return ed


def pipeline_cyclist(name, rot=0.0):
    S = f'art/source/{name}'
    os.system(f'python3 -I tools/cleanpass.py {S}/{name}_cut.png {S}/{name}_clean.png --tol 90')
    ed = fix_key(f'{S}/{name}_clean.png', f'{S}/{name}_clean.png')
    f, e = wheels(name, src=f'{S}/{name}_clean.png')
    os.system(f'python3 -I tools/outline_complete.py {S}/{name}_wheels.png {S}/{name}_ol.png --skip-bottom')
    json.dump({'centres': [list(map(int, c)) for c in f], 'key_edits': ed, 'wheel_edits': e}, open(f'{S}/edits_build.json', 'w'))
    return f


if __name__ == '__main__' and sys.argv[1] == 'cyclist':
    pipeline_cyclist(sys.argv[2])
