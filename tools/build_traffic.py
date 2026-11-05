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
    H, W = mask.shape; a = a[:H, :W] if a.shape[0] >= H and a.shape[1] >= W else np.dstack([np.pad(a[..., c], ((0, max(0, H - a.shape[0])), (0, max(0, W - a.shape[1]))), constant_values=v) for c, v in enumerate((255, 0, 255))])[:H, :W]  # (5 Nov, traffic 2) pad with the key, not black: a 252 px render left a black column by a subject that reaches the frame's right side
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


def wheels(name, src=None, dst=None, rot=0.0, centres=None, guess=None, rs=(14, 15, 16)):
    """Redraw both wheels of a cyclist. Inside each wheel's disc the cut's pixels are kept only where they are part
    of the bike or the rider (components of 8 px or more inside the disc, or joined to the frame outside it); the
    tyre ring is the new wheel's. Writes the edits list."""
    src = src or f'art/source/{name}/{name}_cut.png'; dst = dst or f'art/source/{name}/{name}_wheels.png'
    a = np.array(Image.open(src).convert('RGBA')); h, w = a.shape[:2]
    cj = json.load(open(f'art/gen/out/{name}.cut.json')); bx, by = cj['box'][:2]
    bom = json.load(open(f'art/gen/blockouts/{name}.json')); G = bom['ground']
    guess = [(gx - bx, gy - by) for gx, gy in guess] if guess else [(144 - bx, G - 16 - by), (195 - bx, G - 16 - by)]
    fits = centres or [fit_wheel(a, gx, gy, rs)[1:] for gx, gy in guess]
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


def pipeline_cyclist(name, rot=0.0, guess=None, rs=(14, 15, 16)):
    S = f'art/source/{name}'
    os.system(f'python3 -I tools/cleanpass.py {S}/{name}_cut.png {S}/{name}_clean.png --tol 90')
    ed = fix_key(f'{S}/{name}_clean.png', f'{S}/{name}_clean.png')
    f, e = wheels(name, src=f'{S}/{name}_clean.png', guess=guess, rs=rs)
    os.system(f'python3 -I tools/outline_complete.py {S}/{name}_wheels.png {S}/{name}_ol.png --skip-bottom')
    json.dump({'centres': [list(map(int, c)) for c in f], 'key_edits': ed, 'wheel_edits': e}, open(f'{S}/edits_build.json', 'w'))
    return f


if __name__ == '__main__' and sys.argv[1] == 'cyclist':
    pipeline_cyclist(sys.argv[2])
if __name__ == '__main__' and sys.argv[1] == 'lanerider':                 # 55 px/m: wheels 39 px (R 18-20)
    k = 55 / 46
    pipeline_cyclist(sys.argv[2], guess=[(130, round(200 - 16 * k)), (round(130 + 51 * k), round(200 - 16 * k))], rs=(17, 18, 19, 20))


def pipeline_car(name):
    S = f'art/source/{name}'
    os.system(f'python3 -I tools/cleanpass.py {S}/{name}_cut.png {S}/{name}_clean.png --tol 90')
    ed = fix_key(f'{S}/{name}_clean.png', f'{S}/{name}_clean.png')
    os.system(f'python3 -I tools/outline_complete.py {S}/{name}_clean.png {S}/{name}_ol.png')
    json.dump({'key_edits': ed}, open(f'{S}/edits_build.json', 'w'))


if __name__ == '__main__' and sys.argv[1] == 'car':
    pipeline_car(sys.argv[2])


def fix_blotches(src, dst, layer, max_px=8, why='blotch: a small patch in a near colour takes its surrounding colour'):
    """asset_qa's blotches (2-24 px of a near colour inside a fill): patches up to max_px take the colour around them.
    Longer ones are drawn lines (door seams) and stay. Returns the edits."""
    import subprocess, tempfile
    tj = tempfile.mktemp(suffix='.json')
    subprocess.run(['python3', '-I', 'tools/asset_qa.py', '--file', src, '--layer', layer, '--level', 'rw', '--json', tj],
                   capture_output=True)
    d = json.load(open(tj))[0]; a = np.array(Image.open(src).convert('RGBA')); out = a.copy(); ed = []
    pts_ = [tuple(p) for c in d['checks'] if c['id'] == 'blotches' for p in c['pixels']]
    m = np.zeros(a.shape[:2], bool)
    for x, y in pts_: m[y, x] = True
    lbl, n = label(m)
    for i in range(1, n + 1):
        comp = lbl == i
        if comp.sum() > max_px: continue
        ring = grow(comp, 1) & ~comp & (a[..., 3] > 0)
        cols = [tuple(c) for c in a[ring].tolist()]
        if not cols: continue
        c = max(set(cols), key=cols.count)
        for y, x in zip(*np.nonzero(comp)):
            ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in a[y, x]], 'to': list(c), 'why': why})
            out[y, x] = c
    Image.fromarray(out).save(dst); return ed


if __name__ == '__main__' and sys.argv[1] == 'blotches':
    e = fix_blotches(sys.argv[3], sys.argv[4], sys.argv[5])
    p = f'art/source/{sys.argv[2]}/edits_polish.json'
    old = json.load(open(p)) if os.path.exists(p) else []
    json.dump(old + e, open(p, 'w')); print(len(e), 'px')


def pedal(name, zone=(18, 40, 58, 87), off=(8, 13), nframes=8):
    """The pedal loop: 8 frames of the still's size. Outside the leg zone every frame is the polished still,
    pixel-identical; in the zone (hip to pedals, not the wheels) the pixel-engine frame's pixels, snapped to the
    still's own colours (no flicker, no new colour); the wheels are redrawn by rule in every frame, turned 22.5 degrees
    a frame (one frame per 6 px ridden is about 22 degrees on a 31 px wheel; 8 x 22.5 = 180, a whole spoke step:
    the loop is seamless)."""
    S = f'art/source/{name}'
    st = np.array(Image.open(f'{S}/{name}_pol.png').convert('RGBA')); H, W = st.shape[:2]
    cl = np.array(Image.open(f'{S}/{name}_clean.png').convert('RGBA'))
    sh = np.array(Image.open(f'art/gen/renders/{name}_pedal_sheet.png').convert('RGBA'))
    fw = sh.shape[1] // nframes
    cols = np.unique(st[st[..., 3] > 0][:, :3], axis=0).astype(float)
    cent = json.load(open(f'{S}/edits_build.json'))['centres']
    Y, X = np.mgrid[0:H, 0:W]
    disc = np.zeros((H, W), bool)
    for cx, cy, R_ in cent: disc |= np.hypot(X - cx, Y - cy) < R_ + 0.5
    x0, y0, x1, y1 = zone
    zm = np.zeros((H, W), bool); zm[y0:y1, x0:x1] = True; zm &= ~disc
    frames = []
    for f in range(nframes):
        fr = sh[off[1]:off[1] + H, f * fw + off[0]:f * fw + off[0] + W].copy()
        out = st.copy()
        # the wheels, turned: inside each disc only the bike's own pieces are kept (found on the cut before its
        # wheels were drawn, as wheels() does), the rest is cleared and the wheel drawn again at this frame's turn
        for cx, cy, R_ in cent:
            d = np.hypot(X - cx, Y - cy)
            spk = (d < R_ - 1.5) & (cl[..., 3] > 0)
            lbl, n = label(spk); sz = np.bincount(lbl.ravel())
            keepm = np.zeros_like(spk)
            for i in range(1, n + 1):
                comp = lbl == i
                if sz[i] >= 8 or (grow(comp, 1) & (cl[..., 3] > 0) & ~(d < R_ + 0.5)).any(): keepm |= comp
            out[(d < R_ + 0.5) & ~keepm] = 0
            ink = tuple(int(v) for v in st[int(cy) + R_, int(cx)][:3])
            wc = dict(ink=ink, tyre=ink, rim=tuple(int(v) for v in st[int(cy) + R_ - 1, int(cx)][:3]),
                      spoke=(55, 55, 55), hub=tuple(int(v) for v in st[int(cy), int(cx)][:3]))
            for (x, y), c in wheel_px(cx, cy, R_, 8, 22.5 * f, wc).items():
                if 0 <= x < W and 0 <= y < H and not (keepm[y, x] and np.hypot(x - cx, y - cy) < R_ - 1.5):
                    out[y, x] = (*c, 255)
        # the legs from the pixel-engine frame, snapped to the still's colours
        a = fr[..., 3] > 127
        rgb = fr[..., :3].reshape(-1, 3).astype(float)
        idx = np.argmin(((rgb[:, None] - cols[None]) ** 2).sum(2), 1)
        snap = cols[idx].reshape(H, W, 3).astype(np.uint8)
        out[zm & a, :3] = snap[zm & a]; out[zm & a, 3] = 255
        out[zm & ~a] = 0
        frames.append(out)
    sheet = np.concatenate(frames, 1)
    Image.fromarray(sheet).save(f'{S}/{name}_pedal_raw.png')
    return frames


if __name__ == '__main__' and sys.argv[1] == 'pedal':
    pedal(sys.argv[2])


def finish_pedal(name):
    """The pedal sheet's polish: the outline closed per frame, pinholes asset_qa finds filled with the colour around
    them; every changed pixel listed in edits_pedal.json."""
    S = f'art/source/{name}'; import subprocess, tempfile
    raw = f'{S}/{name}_pedal_raw.png'; ol = f'{S}/{name}_pedal_ol.png'
    subprocess.run(['python3', '-I', 'tools/outline_complete.py', raw, ol, '--skip-bottom', '--frames', '84x87'])
    tj = tempfile.mktemp(suffix='.json')
    subprocess.run(['python3', '-I', 'tools/asset_qa.py', '--file', ol, '--layer', 'char', '--level', 'rw', '--frames', '84x87', '--json', tj], capture_output=True)
    d = json.load(open(tj))[0]; a = np.array(Image.open(ol).convert('RGBA')); out = a.copy(); ed = []
    for c in d['checks']:
        if c['id'] != 'pinholes': continue
        for x, y in c['pixels']:
            nb = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if a[yy, xx, 3] > 0]
            if nb:
                out[y, x] = max(set(nb), key=nb.count)
                ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in a[y, x]], 'to': [int(v) for v in out[y, x]], 'why': 'pinhole'})
    r = np.array(Image.open(raw).convert('RGBA'))
    for y, x in zip(*np.nonzero((out != r).any(2))):
        if not any(e['x'] == x and e['y'] == y for e in ed):
            ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in r[y, x]], 'to': [int(v) for v in out[y, x]], 'why': 'outline closed (outline_complete.py)'})
    Image.fromarray(out).save(f'{S}/{name}_pedal.png'); json.dump(ed, open(f'{S}/edits_pedal.json', 'w'))
    print(name, 'pedal polish', len(ed), 'px')


if __name__ == '__main__' and sys.argv[1] == 'finish_pedal':
    finish_pedal(sys.argv[2])
