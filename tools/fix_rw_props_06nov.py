#!/usr/bin/env python3
"""fix_rw_props_06nov.py: the River Walk props family's hand fixes by rule (6 Nov 2026, 0 credits). Each piece's
changed pixels go to art/source/NAME/edits.json under "06nov" (x, y, from, to, why), the .aseprite source is written
with tools/aseprite_io.py and the slot png is saved. Existing art is fixed by hand, never by an automated clean pass
(BIBLE 3); every rule below names the exact pixels or colours it touches.

  rw_birch       (new cut) a 3 px near-twin of the leaf highlight (#c3e336 beside #c8dd3c) joins it; then the
                 highlight #c8dd3c (luma 196, 212 on screen) one step down to #b6d434 (185)
  gritbox_front  no text in art: the "SAND" letters (#bcc8ba, rows 17-21) take the plank fill #335437 and the
                 plate gap in the lower board line (row 22, x 35-55) takes that line's shade #294830
  cloud2, cloud5 no dithering in sprites: a pixel whose four neighbours share one other colour takes that colour
                 (the checker patches at cloud2 x 58-61 y 21-25 and cloud5 x 43-54 y 21-23), scanned top-left
                 to bottom-right until nothing changes"""
import sys, os, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

SCENE = 'riverwalk/art/scene'


def load(n):
    return np.array(Image.open(f'{SCENE}/{n}.png').convert('RGBA'))


def save(n, a, ed, key='06nov'):
    d = f'art/source/{n}'; os.makedirs(d, exist_ok=True)
    p = f'{d}/edits.json'
    J = json.load(open(p)) if os.path.exists(p) else {'name': n}
    if key in J: print(n, 'already fixed', key); return
    if not os.path.exists(f'{d}/{n}_before_06nov.png'): shutil.copy(f'{SCENE}/{n}.png', f'{d}/{n}_before_06nov.png')
    J[key] = ed
    json.dump(J, open(p, 'w'), indent=0)
    aseprite_io.write(f'{d}/{n}.aseprite', [a], layer=n)
    Image.fromarray(a, 'RGBA').save(f'{SCENE}/{n}.png')
    print(n, len(ed), 'pixels', 'colours', len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)))


def swap(a, f, t, sel, why, ed):
    m = (a[..., 3] > 0) & (a[..., :3] == f).all(-1) & sel
    for y, x in zip(*np.nonzero(m)):
        ed.append({'x': int(x), 'y': int(y), 'from': list(map(int, f)), 'to': list(map(int, t)), 'why': why})
    a[m, :3] = t


def everywhere(a): return np.ones(a.shape[:2], bool)


def box(a, x0, y0, x1, y1):
    m = np.zeros(a.shape[:2], bool); m[y0:y1 + 1, x0:x1 + 1] = True; return m


done = set(sys.argv[1:]) or {'rw_birch', 'gritbox_front', 'cloud2', 'cloud5'}
if 'rw_birch' in done:
    a = load('rw_birch'); ed = []
    swap(a, (195, 227, 54), (200, 221, 60), everywhere(a), 'near-twin of the highlight', ed)
    save('rw_birch', a, ed)
    # round 2 (the card, 6 Nov): on screen the leaf highlight was 212, above the approved lime's tops; one step down
    a = load('rw_birch'); ed = []
    swap(a, (200, 221, 60), (182, 212, 52), everywhere(a), 'ladder: highlight luma 196 -> 185', ed)
    save('rw_birch', a, ed, '06nov_r2')
if 'gritbox_front' in done:
    a = load('gritbox_front'); ed = []
    swap(a, (188, 200, 186), (51, 84, 55), box(a, 30, 17, 60, 21), 'no text: the SAND letters take the plank fill', ed)
    swap(a, (51, 84, 55), (41, 72, 47), box(a, 35, 22, 55, 22), 'no text: the plate gap takes the board line shade', ed)
    save('gritbox_front', a, ed)
for n in ('cloud2', 'cloud5'):
    if n not in done: continue
    a = load(n); ed = []; H, W = a.shape[:2]
    k = (a[..., 0].astype(int) << 16) | (a[..., 1].astype(int) << 8) | a[..., 2]
    k = np.where(a[..., 3] > 0, k, -1)
    ch = True
    while ch:
        ch = False
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                c = k[y, x]
                if c < 0: continue
                n4 = {k[y - 1, x], k[y + 1, x], k[y, x - 1], k[y, x + 1]}
                if len(n4) == 1:
                    o = int(n4.pop())
                    if o >= 0 and o != c:
                        t = [(o >> 16) & 255, (o >> 8) & 255, o & 255]
                        ed.append({'x': x, 'y': y, 'from': a[y, x, :3].tolist(), 'to': t, 'why': 'no dither: takes its four neighbours\' colour'})
                        a[y, x, :3] = t; k[y, x] = o; ch = True
    save(n, a, ed)
