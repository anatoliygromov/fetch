#!/usr/bin/env python3
"""fix_traffic_r1.py: fix round 1 of the River Walk traffic family (review 5 Nov, art/gen/reviews/*.md).

  python3 -I tools/fix_traffic_r1.py base     NAME   pad, one family ink, near-ink shades merged, outline -> r1_base.png
  python3 -I tools/fix_traffic_r1.py hand     NAME   the hand edits listed in art/source/NAME/hand_r1.json -> r1.png
  python3 -I tools/fix_traffic_r1.py grid     NAME [x0 y0 x1 y1]   a 12x enlargement with pixel coordinates (for the hand edits)

base (no blotch or clean script; every change listed in art/source/NAME/edits_r1.json):
  1. riders: the canvas padded by 2 whole pixels left and right (88 x 87), so no wheel touches the edge;
  2. colours: the family ink is the approved bench's #000000; the file's own ink becomes it, and the mottling near-ink
     shades named in the review merge into one dark grey (#373737); colour map per file below;
  3. riders: one wheel drawn once and stamped on both centres (the same pixels; the bike's frame tubes that cross a
     wheel are drawn over it, as on a real bike);
  4. the outline: every pixel on the outer silhouette (next to the transparent area outside the piece) takes the ink;
     holes inside (the see-through wheels) keep their rim and spokes."""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_traffic as B

INK = (0, 0, 0)
MAP = {
    'rw_cyclist_adult': {'050a17': '000000', '21273a': '373737', '2b2a25': '373737', '393847': '373737', '44423a': '373737'},
    'rw_cyclist_adult2': {'050a17': '000000', '1c1c1c': '000000', '282a36': '373737', '2b2a25': '373737', '393847': '373737', '44423a': '373737'},
    'rw_car1': {'010102': '000000', '2b2a25': '1c1c1c', '393847': '373737'},
    'rw_car4': {'020202': '000000', '393847': '373737'},
    'rw_road_rider1': {'010102': '000000', '1c1c1c': '000000', '21273a': '373737', '2b2a25': '373737', '44423a': '373737'},
    'rw_road_rider2': {'010102': '000000', '1c1c1c': '000000', '282a36': '373737', '2b2a25': '373737', '44423a': '373737'},
}
PAD = {'rw_cyclist_adult': 2, 'rw_cyclist_adult2': 2, 'rw_car1': 0, 'rw_car4': 0, 'rw_road_rider1': 2, 'rw_road_rider2': 2}


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def outside(a):
    """the transparent area connected to the canvas border (4-connected)"""
    t = a[..., 3] == 0; h, w = t.shape; o = np.zeros_like(t); st = []
    for y in range(h):
        for x in (0, w - 1):
            if t[y, x] and not o[y, x]: o[y, x] = True; st.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if t[y, x] and not o[y, x]: o[y, x] = True; st.append((y, x))
    while st:
        y, x = st.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and t[ny, nx] and not o[ny, nx]: o[ny, nx] = True; st.append((ny, nx))
    return o


def outer_edge(a):
    o = np.pad(outside(a), 1, constant_values=True)
    nb = o[:-2, 1:-1] | o[2:, 1:-1] | o[1:-1, :-2] | o[1:-1, 2:]
    return (a[..., 3] > 0) & nb


def log(ed, before, after, why):
    for y, x in zip(*np.nonzero((before != after).any(2))):
        ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in before[y, x]], 'to': [int(v) for v in after[y, x]], 'why': why})


def stamp_wheels(a, clean, cent, rot=0.0, spokes=8):
    """one wheel (wheel_px at the first centre's radius) stamped on every centre; inside the discs only the bike's
    own pieces from the cut (frame tubes, chain guard, foot) are kept over it."""
    h, w = a.shape[:2]; Y, X = np.mgrid[0:h, 0:w]; out = a.copy()
    R_ = cent[0][2]
    ink = INK; rim = (156, 158, 168); spoke = (55, 55, 55); hub = (118, 120, 132)
    one = B.wheel_px(0, 0, R_, spokes, rot, dict(ink=ink, tyre=ink, rim=rim, spoke=spoke, hub=hub))
    for cx, cy, _ in cent:
        d = np.hypot(X - cx, Y - cy)
        spk = (d < R_ - 1.5) & (clean[..., 3] > 0)
        lbl, n = B.label(spk); sz = np.bincount(lbl.ravel()); keepm = np.zeros_like(spk)
        for i in range(1, n + 1):
            comp = lbl == i
            if sz[i] >= 8 or (B.grow(comp, 1) & (clean[..., 3] > 0) & ~(d < R_ + 0.5)).any(): keepm |= comp
        out[(d < R_ + 0.5) & ~keepm] = 0
        for (x, y), c in one.items():
            X_, Y_ = x + cx, y + cy
            if 0 <= X_ < w and 0 <= Y_ < h and not keepm[Y_, X_]:
                out[Y_, X_] = (*c, 255)
    return out


def base(name):
    S = f'art/source/{name}'; p = PAD[name]
    a = np.array(Image.open(f'{S}/{name}_pol.png' if os.path.exists(f'{S}/{name}_pol.png') else f'{S}/{name}_ol.png').convert('RGBA'))
    a = np.pad(a, ((0, 0), (p, p), (0, 0)))
    ed = []
    b = a.copy()
    for s_, t_ in MAP[name].items():
        m = np.all(b[..., :3] == hx(s_), -1) & (b[..., 3] > 0); b[m, :3] = hx(t_)
    log(ed, a, b, 'colour: one family ink #000000 / near-ink shades merged into #373737 (review A3, A4)')
    if name.startswith('rw_cyclist') or name.startswith('rw_road_rider'):
        cl = np.array(Image.open(f'{S}/{name}_clean.png').convert('RGBA')); cl = np.pad(cl, ((0, 0), (p, p), (0, 0)))
        cent = [[c[0] + p, c[1], c[2]] for c in json.load(open(f'{S}/edits_build.json'))['centres']]
        cy = max(c[1] for c in cent); cent = [[c[0], cy, c[2]] for c in cent]      # one axle line
        c2 = stamp_wheels(b, cl, cent)
        log(ed, b, c2, 'wheel: one wheel drawn once, stamped on both centres (review A1)'); b = c2
        json.dump({'centres': cent, 'pad': p}, open(f'{S}/r1_wheels.json', 'w'))
    c3 = b.copy(); e = outer_edge(b); c3[e, :3] = INK; c3[e, 3] = 255
    log(ed, b, c3, 'outline: the outer silhouette in the family ink (review A4)')
    Image.fromarray(c3).save(f'{S}/{name}_r1_base.png')
    json.dump(ed, open(f'{S}/edits_r1_base.json', 'w'))
    print(name, 'base', c3.shape[1], 'x', c3.shape[0], len(ed), 'px changed',
          len(np.unique(c3[c3[..., 3] > 0][:, :3], axis=0)), 'colours')


def grid(name, box=None, src=None, k=12):
    S = f'art/source/{name}'; src = src or f'{S}/{name}_r1_base.png'
    a = Image.open(src).convert('RGBA')
    if box: a = a.crop(box)
    x0, y0 = (box[0], box[1]) if box else (0, 0)
    c = Image.new('RGBA', a.size, (200, 215, 225, 255)); c.alpha_composite(a)
    c = c.resize((a.width * k, a.height * k), Image.NEAREST).convert('RGB')
    m = 24; C = Image.new('RGB', (c.width + m, c.height + m), (255, 255, 255)); C.paste(c, (m, m)); d = ImageDraw.Draw(C)
    for i in range(a.width + 1):
        col = (255, 0, 0) if (x0 + i) % 10 == 0 else (170, 170, 170)
        if (x0 + i) % 5 == 0 or k >= 12: d.line([(m + i * k, m), (m + i * k, C.height)], fill=col if (x0 + i) % 5 == 0 else (215, 215, 215))
        if (x0 + i) % 5 == 0: d.text((m + i * k + 1, 2), str(x0 + i), fill=(0, 0, 0))
    for j in range(a.height + 1):
        col = (255, 0, 0) if (y0 + j) % 10 == 0 else (170, 170, 170)
        d.line([(m, m + j * k), (C.width, m + j * k)], fill=col if (y0 + j) % 5 == 0 else (215, 215, 215))
        if (y0 + j) % 5 == 0: d.text((1, m + j * k + 1), str(y0 + j), fill=(0, 0, 0))
    return C


def hand(name, src=None, dst=None):
    """explicit pixel edits: art/source/NAME/hand_r1.json = [{"xy": [[x, y], ...], "to": "rrggbb" | "clear", "why": ...}]"""
    S = f'art/source/{name}'; src = src or f'{S}/{name}_r1_base.png'; dst = dst or f'{S}/{name}_r1.png'
    a = np.array(Image.open(src).convert('RGBA')); b = a.copy(); ed = []
    for e in json.load(open(f'{S}/hand_r1.json')):
        for x, y in e['xy']:
            b[y, x] = (0, 0, 0, 0) if e['to'] == 'clear' else (*hx(e['to']), 255)
        log(ed, a, b, e['why']); a = b.copy()
    Image.fromarray(b).save(dst)
    json.dump(ed, open(f'{S}/edits_r1_hand.json', 'w')); print(name, 'hand', len(ed), 'px')


if __name__ == '__main__':
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == 'base': base(name)
    elif cmd == 'hand': hand(name)
    elif cmd == 'grid':
        box = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) > 6 else None
        src = sys.argv[7] if len(sys.argv) > 7 else None
        grid(name, box, src).save(f'/tmp/claude-0/grid_{name}.png')


def pedal(name, zone=(20, 40, 60, 87), off=(8, 13), nframes=8, phase=11.25):
    """Pedal loop round 1: the r1 still (padded) everywhere outside the leg zone; in the zone the pixel-engine frame
    snapped to the still's colours; one wheel drawn once per frame and stamped on both centres, the wheel phase
    stepping 11.25 degrees a frame (0, 11.25, 22.5, 33.75 and again: 4 distinct phases, each used twice); outer
    silhouette in ink; transparent holes inside the leg zone (gaps that open in one frame) closed with the colour
    around them; light pixels the engine left at the pedals (rim and sky blues) taken out of the zone."""
    S = f'art/source/{name}'; W0 = json.load(open(f'{S}/r1_wheels.json')); p = W0['pad']; cent = W0['centres']
    st = np.array(Image.open(f'{S}/{name}_r1.png').convert('RGBA')); H, W = st.shape[:2]
    cl = np.pad(np.array(Image.open(f'{S}/{name}_clean.png').convert('RGBA')), ((0, 0), (p, p), (0, 0)))
    sh = np.array(Image.open(f'art/gen/renders/{name}_pedal_sheet.png').convert('RGBA')); fw = sh.shape[1] // nframes
    cols = np.unique(st[st[..., 3] > 0][:, :3], axis=0).astype(float)
    lum = cols @ [0.299, 0.587, 0.114]
    legcols = cols[(lum < 140)]                                        # the zone takes no light colour (no blue glints)
    Y, X = np.mgrid[0:H, 0:W]
    disc = np.zeros((H, W), bool)
    for cx, cy, R_ in cent: disc |= np.hypot(X - cx, Y - cy) < R_ + 0.5
    x0, y0, x1, y1 = zone
    zm = np.zeros((H, W), bool); zm[y0:y1, x0:x1] = True; zm &= ~disc
    frames, ed = [], []
    for f in range(nframes):
        fr = np.pad(sh[off[1]:off[1] + H, f * fw + off[0]:f * fw + off[0] + W - 2 * p], ((0, 0), (p, p), (0, 0)))
        out = st.copy()
        a = fr[..., 3] > 127
        rgb = fr[..., :3].reshape(-1, 3).astype(float)
        keepcol = np.array([tuple(c) for c in st[zm & (st[..., 3] > 0)][:, :3].tolist()] or [[0, 0, 0]], float)
        idx = np.argmin(((rgb[:, None] - legcols[None]) ** 2).sum(2), 1)
        snap = legcols[idx].reshape(H, W, 3).astype(np.uint8)
        out[zm & a, :3] = snap[zm & a]; out[zm & a, 3] = 255; out[zm & ~a] = 0
        # the still's light pixels in the zone (the chain guard's highlight, the crank) stay where the still has them
        light = zm & (st[..., 3] > 0) & ((st[..., :3].astype(float) @ [0.299, 0.587, 0.114]) >= 140)
        out[light] = st[light]
        out = stamp_wheels(out, cl, cent, rot=phase * (f % 4))
        # holes in the zone: transparent islands not joined to the outside, not inside a wheel
        hole = (out[..., 3] == 0) & ~outside(out) & zm
        lbl, n = B.label(hole)
        for i in range(1, n + 1):
            comp = lbl == i
            ring = B.grow(comp, 1) & ~comp & (out[..., 3] > 0)
            cs = [tuple(c) for c in out[ring].tolist()]
            if cs and comp.sum() <= 16: out[comp] = max(set(cs), key=cs.count)
        e = outer_edge(out); out[e, :3] = INK; out[e, 3] = 255
        frames.append(out)
    sheet = np.concatenate(frames, 1)
    Image.fromarray(sheet).save(f'{S}/{name}_pedal_r1_base.png')
    print(name, 'pedal r1', sheet.shape[1], 'x', sheet.shape[0])


if __name__ == '__main__' and sys.argv[1] == 'pedal':
    pedal(sys.argv[2])
