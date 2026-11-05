#!/usr/bin/env python3
"""fix_traffic2.py: the River Walk traffic 2 cars (road_car2 van, road_car3 taxi, road_car5 estate), 5 Nov 2026.
Made like the reviewed road_car1 and road_car4 (art/rw-traffic-05nov): SpriteCook render cut 1:1
(tools/build_traffic.py cut, then `car`: new-cut clean pass, key remnants, outline), then this script.

  python3 -I tools/fix_traffic2.py base NAME    colour map (one ink #000000, near-ink shades merged, per-car fixes),
                                                 the wheel drawn once by rule and stamped on both centres, the outer
                                                 silhouette in the ink                       -> NAME_base.png
  python3 -I tools/fix_traffic2.py tidy NAME    the new cut's clean pass, by rule (art/source/NAME/tidy.json): specks of
                                                 1-3 px of a body colour inside another body colour take it; each
                                                 window's glass redrawn as one flat dark glass with one 2 px
                                                 reflection band (light from the upper left)   -> NAME_tidy.png
  python3 -I tools/fix_traffic2.py hand NAME    explicit pixel edits art/source/NAME/hand.json  -> NAME_fin.png
  python3 -I tools/fix_traffic2.py grid NAME x0 y0 x1 y1 [SRC]   a 12x enlargement with pixel coordinates

Every changed pixel is logged (edits_base.json, edits_hand.json) and collected in art/source/NAME/edits.json.
No blotch or clean script runs here: the only clean pass is build_traffic.py's, on the new cut (BIBLE 3)."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fix_traffic_r1 as F

INK = (0, 0, 0)
# per car: colour map (hex -> hex). The family's ink is the approved bench's #000000; near-ink shades go to the
# family's one dark grey #373737 (as road_car1 and road_car4, review round 1); the tan glint colour c0ac8e (car1's
# review defect) never stays; tail lamps red.
MAP = {
    'rw_car2': {'050a17': '000000', '393847': '373737', 'c0ac8e': 'e9d1b2'},
    'rw_car3': {'010102': '000000', '5a2e2a': '000000', '17181f': '282a36', '101b15': '282a36', '2b2a25': '282a36',
                'eebc68': 'f4cc69', '767884': '565864'},          # the black roof one dark (282a36) under the ink
    'rw_car5': {'010102': '000000', '5a2e2a': '000000', '17181f': '282a36', '393847': '373737'},   # rails and trim one dark
}
# the wheel, drawn by rule (cut coordinates): centres, outer radius; colours of a steel wheel lit from the upper left
WHEEL = dict(tyre='282a36', rim_edge='565864', rim='c2c4ca', rim_shade='949da6', hub='7b8087', cap='e1e1e1')


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def wheel_px(R=17.5):
    """{(dx, dy): hex} of one car wheel: ink edge, tyre, rim edge, steel rim (shaded down-right), 4 holes, hub."""
    out = {}
    n = int(np.ceil(R)) + 1
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            d = np.hypot(dx, dy)
            if d > R: continue
            if d > R - 1: c = '000000'
            elif d > 10.5: c = WHEEL['tyre']
            elif d > 9.5: c = WHEEL['rim_edge']
            elif d > 3.5:
                c = WHEEL['rim_shade'] if dx + dy > 4 else WHEEL['rim']
                if abs(abs(dx) - abs(dy)) <= 0 and 6.2 < d < 7.8: c = WHEEL['rim_edge']        # 4 holes at 45 deg
            elif d > 2.5: c = WHEEL['hub']
            else: c = WHEEL['cap'] if dx + dy < 0 else WHEEL['rim']
            out[(dx, dy)] = c
    return out


def base(name):
    S = f'art/source/{name}'
    a = np.array(Image.open(f'{S}/{name}_ol.png').convert('RGBA'))
    ed = []; b = a.copy()
    for s_, t_ in MAP[name].items():
        m = np.all(b[..., :3] == hx(s_), -1) & (b[..., 3] > 0); b[m, :3] = hx(t_)
    F.log(ed, a, b, 'colour: one family ink #000000; near-ink shade merged into #373737; no tan glint colour (as road_car1/4, review round 1)')
    W = json.load(open(f'{S}/wheels.json'))
    c = b.copy(); h, w = c.shape[:2]; one = wheel_px(W['R'])
    for cx, cy in W['centres']:
        for (dx, dy), col in one.items():
            x, y = cx + dx, cy + dy
            if 0 <= x < w and 0 <= y < h: c[y, x] = (*hx(col), 255)
    F.log(ed, b, c, 'wheel: one wheel drawn once by rule (round, steel rim lit from the upper left) and stamped on both centres on one axle line')
    d = c.copy(); e = F.outer_edge(c); d[e, :3] = INK; d[e, 3] = 255
    F.log(ed, c, d, 'outline: the outer silhouette in the family ink')
    Image.fromarray(d).save(f'{S}/{name}_base.png')
    json.dump(ed, open(f'{S}/edits_base.json', 'w'))
    print(name, 'base', len(ed), 'px changed,', len(np.unique(d[d[..., 3] > 0][:, :3], axis=0)), 'colours')


def tidy(name):
    S = f'art/source/{name}'; T = json.load(open(f'{S}/tidy.json'))
    a = np.array(Image.open(f'{S}/{name}_base.png').convert('RGBA')); b = a.copy(); ed = []; h, w = a.shape[:2]
    body = [hx(c) for c in T['body']]
    key = lambda p: tuple(int(v) for v in p[:3])
    for _ in range(2):
        prev = b.copy()
        inb = np.zeros((h, w), bool)
        for c in body: inb |= np.all(b[..., :3] == c, -1) & (b[..., 3] > 0)
        for c in body:
            m = np.all(b[..., :3] == c, -1) & (b[..., 3] > 0)
            lbl, n = F.B.label(m); sz = np.bincount(lbl.ravel())
            for i in range(1, n + 1):
                if sz[i] > T.get('speck', 3): continue
                comp = lbl == i; ring = F.B.grow(comp, 1) & ~comp
                if not (ring & inb).all() or not ring.any(): continue            # only specks inside the body fill
                cols = [key(p) for p in b[ring]]
                b[comp, :3] = max(set(cols), key=cols.count)
        F.log(ed, prev, b, 'clean pass on the new cut: a 1-3 px speck of a body colour inside another body colour takes it')
    for win in T.get('windows', []):
        prev = b.copy(); x0, y0, x1, y1 = win['rect']; glass = [hx(c) for c in T['glass']]
        dark, band = hx(T['glass_fill']), hx(T['glass_band'])
        region = None
        if 'seeds' in win:                  # the glass is the area joined to the seeds (4-connected) inside the rect
            region = set(); st = [tuple(s_) for s_ in win['seeds']]
            while st:
                x, y = st.pop()
                if (x, y) in region or not (x0 <= x <= x1 and y0 <= y <= y1): continue
                if not b[y, x, 3] or key(b[y, x]) not in glass: continue
                region.add((x, y)); st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if b[y, x, 3] and key(b[y, x]) in glass and (region is None or (x, y) in region):
                    t = (x - x0) + (y - y0) - win['band_at']
                    b[y, x, :3] = band if 0 <= t < 2 else dark
        F.log(ed, prev, b, 'glass redrawn by rule: one flat dark glass, one 2 px reflection band from the upper left')
    Image.fromarray(b).save(f'{S}/{name}_tidy.png'); json.dump(ed, open(f'{S}/edits_tidy.json', 'w'))
    print(name, 'tidy', len(ed), 'px,', len(np.unique(b[b[..., 3] > 0][:, :3], axis=0)), 'colours')


def hand(name):
    """art/source/NAME/hand.json = [{"xy": [[x, y], ...] | "rect": [x0, y0, x1, y1] (inclusive), "to": "rrggbb" |
    "clear", "only": ["rrggbb", ...] (optional: change only pixels of these colours), "why": ...}]"""
    S = f'art/source/{name}'
    a = np.array(Image.open(f'{S}/{name}_tidy.png').convert('RGBA')); b = a.copy(); ed = []
    for e in json.load(open(f'{S}/hand.json')):
        pts = [tuple(p) for p in e.get('xy', [])]
        if 'rect' in e:
            x0, y0, x1, y1 = e['rect']; pts += [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
        only = {hx(o) for o in e.get('only', [])}
        prev = b.copy()
        for x, y in pts:
            if only and (b[y, x, 3] == 0 or tuple(b[y, x, :3]) not in only): continue
            b[y, x] = (0, 0, 0, 0) if e['to'] == 'clear' else (*hx(e['to']), 255)
        F.log(ed, prev, b, e['why'])
    Image.fromarray(b).save(f'{S}/{name}_fin.png')
    json.dump(ed, open(f'{S}/edits_hand.json', 'w'))
    print(name, 'hand', len(ed), 'px,', len(np.unique(b[b[..., 3] > 0][:, :3], axis=0)), 'colours')


def collect(name):
    S = f'art/source/{name}'; out = {'asset': name, 'source_render': json.load(open(f'art/gen/out/{name}.cut.json'))['render'],
                                     'order': ['cut (build_traffic.py cut)', 'new-cut clean pass, tol 90 (cleanpass.py)',
                                               'pink key remnants', 'outline closed (outline_complete.py)',
                                               'base (fix_traffic2.py: colour map, wheel stamped, outer ink)', 'tidy (fix_traffic2.py: new-cut speck pass, glass by rule)',
                                               'hand (fix_traffic2.py: art/source/NAME/hand.json)'], 'steps': {}}
    for k, f in (('build', 'edits_build.json'), ('base', 'edits_base.json'), ('tidy', 'edits_tidy.json'), ('hand', 'edits_hand.json')):
        if os.path.exists(f'{S}/{f}'): out['steps'][k] = json.load(open(f'{S}/{f}'))
    json.dump(out, open(f'{S}/edits.json', 'w'))


if __name__ == '__main__':
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == 'base': base(name)
    elif cmd == 'tidy': tidy(name)
    elif cmd == 'hand': hand(name); collect(name)
    elif cmd == 'grid':
        box = tuple(int(v) for v in sys.argv[3:7]); src = sys.argv[7] if len(sys.argv) > 7 else f'art/source/{name}/{name}_base.png'
        F.grid(name, box, src).save(f'/tmp/t5/grid_{name}_{box[0]}_{box[1]}.png')
