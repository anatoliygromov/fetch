#!/usr/bin/env python3
"""fix_cp_keepers.py: hand rules on the two City Park keepers (night 6 Nov 2026, cp track, 0 credits). No automated
clean pass: each rule names the pixels it changes, and every change is written to art/source/<name>/edits.json.

  python3 -I tools/fix_cp_keepers.py   -> riverwalk/art/scene/park_keeper_winch.png, park_keeper_cart.png and their
                                          .aseprite sources (8 frames each). Re-running is a no-op.

park_keeper_winch (the base audit, art/gen/reviews/base_sweep_06nov.md: "the keeper has no face at 1x"): the eye is
  one ink pixel right under the cap's brim, so with the 35 % back fade it reads as part of the brim, and frames 3 and 4
  have no eye and no nose at all. Per frame, from the brim's bottom row b (the row over the face's first skin row): the eye is the ink pixel at (34, b + 3), the pixel over it skin again (the brow stays at b + 1); the nose is a
  skin pixel at (36, b + 4) with its ink at (37, b + 4) where a frame lacks it; the mouth a lip shade (#744a31, the
  face's own dark) at (34, b + 6). The same face in all 8 frames, moving with the head.
park_keeper_cart (the board: "fix", dirt pixels; asset_qa noise 52 pixels, 0.4 %): each single pixel a shade off the
  fill around it takes the colour most of its 8 neighbours have (never an average); the ink outline is never touched."""
import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
INK = (4, 3, 2); SKIN = (217, 153, 120); LIP = (116, 74, 49)


def winch():
    F = 'riverwalk/art/scene/park_keeper_winch.png'; E = 'art/source/park_keeper_winch/edits.json'
    J = json.load(open(E))
    if 'face_06nov_night' in J: return 'park_keeper_winch: already applied'
    a = np.array(Image.open(F).convert('RGBA')); ed = []
    def setp(fx, x, y, c, why):
        X = fx * 80 + x
        old = tuple(int(v) for v in a[y, X])
        new = tuple(c) + (255,)
        if old != new:
            ed.append({'frame': fx, 'x': X, 'y': y, 'from': list(old), 'to': list(new), 'why': why}); a[y, X] = new
    for fx in range(8):
        f = a[:, fx * 80:(fx + 1) * 80, :3].astype(int)
        sk = (f == SKIN).all(-1); sk[40:] = False                  # (the face: the skin above row 40)
        b = int(np.nonzero(sk[:, 28:37].any(1))[0].min()) - 1        # the brim's bottom: the row over the first skin row
        if (f[b + 2, 34] == INK).all(): setp(fx, 34, b + 2, SKIN, 'eye off the brim: skin')
        setp(fx, 34, b + 3, INK, 'eye')
        if not (f[b + 4, 36] == SKIN).all():
            setp(fx, 36, b + 4, SKIN, 'nose'); setp(fx, 37, b + 4, INK, 'nose outline')
        setp(fx, 34, b + 6, LIP, 'mouth')
    J['face_06nov_night'] = ed
    json.dump(J, open(E, 'w'), indent=0)
    Image.fromarray(a, 'RGBA').save(F)
    aseprite_io.write('art/source/park_keeper_winch/park_keeper_winch.aseprite', [a[:, i * 80:(i + 1) * 80] for i in range(8)], layer='park_keeper_winch')
    return f'park_keeper_winch: {len(ed)} pixels (eye, nose, mouth in 8 frames)'


def cart():
    F = 'riverwalk/art/scene/park_keeper_cart.png'; D = 'art/source/park_keeper_cart'; E = f'{D}/edits.json'
    os.makedirs(D, exist_ok=True)
    if os.path.exists(E): return 'park_keeper_cart: already applied'
    if not os.path.exists(f'{D}/park_keeper_cart_old.png'): Image.open(F).save(f'{D}/park_keeper_cart_old.png')
    a = np.array(Image.open(F).convert('RGBA')); H, W = a.shape[:2]
    rgb = a[..., :3].astype(int); al = a[..., 3] > 0
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    ed = []
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not al[y, x] or (rgb[y, x] == INK).all(): continue
            if x % 82 in (0, 81): continue
            nb = [tuple(rgb[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1) if (yy, xx) != (y, x)]
            if not all(al[yy, xx] for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)): continue
            if tuple(rgb[y, x]) in nb: continue                        # it has a neighbour of its own colour
            t = max(set(nb), key=nb.count)
            if nb.count(t) < 5 or t == INK: continue                   # a fill around it: 5 of 8 one colour
            if abs(np.array(t) @ np.array([0.299, 0.587, 0.114]) - lum[y, x]) > 60: continue   # a detail, not dirt
            ed.append({'x': x, 'y': y, 'frame': x // 82, 'from': rgb[y, x].tolist(), 'to': list(map(int, t)), 'why': 'dirt'})
    for e in ed: rgb[e['y'], e['x']] = e['to']
    out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); out[~al] = 0
    json.dump({'asset': 'park_keeper_cart', 'method': 'tools/fix_cp_keepers.py (dirt: 8-neighbour majority)', 'pixels': ed},
              open(E, 'w'), indent=0)
    Image.fromarray(out, 'RGBA').save(F)
    aseprite_io.write(f'{D}/park_keeper_cart.aseprite', [out[:, i * 82:(i + 1) * 82] for i in range(8)], layer='park_keeper_cart')
    return f'park_keeper_cart: {len(ed)} dirt pixels'


print(winch()); print(cart())
