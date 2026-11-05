#!/usr/bin/env python3
"""fix_traffic_r2.py: fix round 2 of the lane riders (review round 2, art/gen/reviews/road_rider1.md, road_rider2.md).

  python3 -I tools/fix_traffic_r2.py plan NAME     writes art/source/NAME/hand_r2.json (every pixel, listed)
  python3 -I tools/fix_traffic_r2.py apply NAME    r1.png + hand_r2.json -> r2.png, edits_r2.json

Relight (the riders ride right, the level's light is upper left): each material's light and shade sides swapped.
  - helmet: every row's run of helmet shades is mirrored (its white highlight moves to the left, the grey to the right);
  - coat / jacket: every row's run of cloth shades is mirrored the same way (light on the back, shade on the chest);
  - backpack (rider 2): the same;
  - face: left as it is (rider 1: its skin is lit evenly); rider 2's face is redrawn by hand (below).
Rider 2 also: the skin-coloured fringe on the backpack top, shoulder and sleeve goes (backpack top to its tan, shoulder
top to the jacket light, sleeve edge to the jacket shade; the hand on the handlebar stays), and the face: skin
forehead, a dark brow, an eye with white and pupil, skin cheek and nose, a one-colour beard edge with a lip."""
import sys, os, json
import numpy as np
from PIL import Image

MAT = {
    'rw_road_rider1': {'helmet': {'e1e1e1', 'f7f9fa', '878c92', '9c9ea8', '565864'},
                       'coat': {'ce3531', '7d1c24'}},
    'rw_road_rider2': {'helmet': {'9c9ea8', '878c92', 'c2c4ca', '565864', '5b5b5b'},
                       'jacket': {'284630', '446e48'},
                       'pack': {'a86e3e', '5a2e2a'}},
}
ROWS = {'rw_road_rider1': {'helmet': (0, 9), 'coat': (18, 102)}, 'rw_road_rider2': {'helmet': (0, 10), 'jacket': (20, 102), 'pack': (20, 42)}}
XR = {'rw_road_rider2': {'pack': (26, 46)}}


def hx(c): return '%02x%02x%02x' % tuple(int(v) for v in c[:3])


def plan(name):
    S = f'art/source/{name}'; a = np.array(Image.open(f'{S}/{name}_r1.png').convert('RGBA')); H, W = a.shape[:2]
    cur = {(x, y): hx(a[y, x]) for y in range(H) for x in range(W) if a[y, x, 3]}
    new = {}
    for mat, cols in MAT[name].items():
        y0, y1 = ROWS[name][mat]; x0, x1 = XR.get(name, {}).get(mat, (0, W))
        for y in range(y0, min(y1, H)):
            x = x0
            while x < x1:
                if cur.get((x, y)) in cols:
                    s = x
                    while x < x1 and cur.get((x, y)) in cols: x += 1
                    run = [cur[(i, y)] for i in range(s, x)]
                    for i, c in zip(range(s, x), run[::-1]):
                        if c != cur[(i, y)]: new[(i, y)] = c
                else: x += 1
    if name == 'rw_road_rider2':
        D, A, J2, J8 = 'f7a67f', 'a86e3e', '284630', '446e48'
        after = dict(cur); after.update(new)
        for (x, y), c in list(after.items()):
            if c != D or y < 20 or y > 46 or (y >= 41 and x >= 64): continue
            nb = {after.get((x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
            if nb & {A, '5a2e2a'} and x < 45: new[(x, y)] = A
            elif nb & {J2, J8}: new[(x, y)] = J8 if y <= 22 else J2
        face = {  # row: {x: colour key}   (0 ink, 1 #373737 hair/brow/beard, D skin, E eye white, A lip)
            10: {58: 'D', 59: 'D', 60: 'D', 61: 'D', 62: 'D', 63: 'D'},
            11: {55: '1', 57: 'D', 58: 'D', 59: '1', 60: '1', 61: '1', 62: 'D', 63: 'D'},
            12: {57: 'D', 58: 'D', 59: 'D', 60: 'E', 61: '0', 62: 'D', 63: 'D'},
            13: {52: 'D', 57: 'D', 58: 'D', 59: 'D', 60: 'E', 61: '0', 62: 'D', 63: 'D'},
            14: {54: '1', 57: 'D', 58: 'D', 59: 'D', 60: 'D', 61: 'D', 62: 'D', 63: 'D'},
            15: {52: 'D', 54: '1'},
            16: {56: '1', 63: 'D'},
            17: {56: '1', 57: '1', 58: '1', 59: 'D', 60: 'A', 61: 'A', 62: '1', 63: '1'},
            18: {56: '1', 57: '1', 58: '1', 59: '1', 60: '1', 61: '1', 62: '1'},
            19: {56: '1', 57: '1', 58: '1', 59: '1', 60: '1', 61: '1', 62: '1'},
        }
        K = {'0': '000000', '1': '373737', 'D': D, 'E': 'c2c4ca', 'A': A}
        for y, row in face.items():
            for x, k in row.items():
                if cur.get((x, y)) != K[k]: new[(x, y)] = K[k]
                elif (x, y) in new: del new[(x, y)]
    groups = {}
    for (x, y), c in new.items():
        why = ('relight: helmet' if y < 11 and cur.get((x, y)) in MAT[name].get('helmet', ()) else
               'face redrawn (review A5)' if name == 'rw_road_rider2' and 10 <= y <= 19 and 50 <= x <= 64 else
               'fringe removed / relight' if name == 'rw_road_rider2' else 'relight: coat')
        groups.setdefault((c, why), []).append([x, y])
    out = [{'xy': v, 'to': k[0], 'why': k[1] + ' (light from the upper left, review round 2)'} for k, v in groups.items()]
    json.dump(out, open(f'{S}/hand_r2.json', 'w')); print(name, sum(len(v) for v in groups.values()), 'px planned')


def apply(name):
    S = f'art/source/{name}'; a = np.array(Image.open(f'{S}/{name}_r1.png').convert('RGBA')); b = a.copy(); ed = []
    for e in json.load(open(f'{S}/hand_r2.json')):
        for x, y in e['xy']:
            b[y, x] = (*[int(e['to'][i:i + 2], 16) for i in (0, 2, 4)], 255)
            ed.append({'x': x, 'y': y, 'from': [int(v) for v in a[y, x]], 'to': [int(v) for v in b[y, x]], 'why': e['why']})
    Image.fromarray(b).save(f'{S}/{name}_r2.png'); json.dump(ed, open(f'{S}/edits_r2.json', 'w')); print(name, len(ed), 'px')


if __name__ == '__main__':
    {'plan': plan, 'apply': apply}[sys.argv[1]](sys.argv[2])
