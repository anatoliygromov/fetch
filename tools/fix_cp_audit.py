#!/usr/bin/env python3
"""fix_cp_audit.py: hand fixes by rule for the City Park tall weirdness audit (art/cp-audit-06nov, 6 Nov 2026, 0 credits).

  python3 -I tools/fix_cp_audit.py [stone] [hedge] [bush] [ground]      (no argument: all four)

No automated clean pass on existing art (owner, 25 Oct): each fix is a listed rule, every changed pixel (or the
colour map) is recorded in art/source/<name>/edits.json under the key "audit", the .aseprite source is rewritten
(tools/aseprite_io.py). Each fix starts from the file as it was before this branch (kept once as
art/source/<name>/<name>_pre_audit.png), so running it twice gives the same pixels.

  stone   park_stone (26 x 21): pink granite read as eggs or hams. A colour map, nothing else moves: the pink ramp to
          a warm grey granite ramp (the same lightness order, one to one), the two blue-grey darks to warm darks; the
          moss and the ink outline kept. The box and the shape are unchanged.
  hedge   park_hedge (66 x 72): a green cube twice Pepper's height. Its top trimmed so it reads as a clipped hedge:
          the two top corners rounded (radius 7, the leaves outside the arc taken off), the outline closed along the
          new edge in the hedge's own ink. The top row over the box (where Pepper stands) keeps its middle 50 px.
  bush    park_bush (75 x 34, the front layer): a flat dark lump on the earth band. The front layer's rule (dark
          silhouette, a thin rim on top): the top pixel of every column takes the City Park front rim (look.lua fg.rim
          594257), every 5th of them the warm rim (b5793f), as Look.front's clumps are lit.
  ground  park_ground (240 x 68): speckled path and earth strata. The path rows 9-28 and the earth rows 34-67 become
          flat bands: each row its majority colour (the speckle, the dark flecks and the ragged band edges go). The
          lawn rows 0-8 and the verge's grass fringe rows 29-33 (blades, not speckle) are kept.
"""
import os, sys, json, shutil
from collections import Counter
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, 'riverwalk/art/scene')
BRANCH, DATE = 'art/cp-audit-06nov', '2026-11-06'


def hx(c): return '%02x%02x%02x' % tuple(int(v) for v in c[:3])


def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


def start(name):
    """the file before this branch (kept once), as an RGBA array"""
    src = os.path.join(ROOT, 'art/source', name)
    os.makedirs(src, exist_ok=True)
    pre = os.path.join(src, name + '_pre_audit.png')
    if not os.path.exists(pre): shutil.copyfile(os.path.join(SCENE, name + '.png'), pre)
    return np.array(Image.open(pre).convert('RGBA'))


def finish(name, a, entry):
    src = os.path.join(ROOT, 'art/source', name)
    Image.fromarray(a, 'RGBA').save(os.path.join(SCENE, name + '.png'))
    aseprite_io.write(os.path.join(src, name + '.aseprite'), [a], layer=name)
    ed = os.path.join(src, 'edits.json')
    log = json.load(open(ed)) if os.path.exists(ed) else {}
    if isinstance(log, list): log = {'earlier': log}
    entry.update({'date': DATE, 'branch': BRANCH, 'source': f'art/source/{name}/{name}_pre_audit.png',
                  'size': [int(a.shape[1]), int(a.shape[0])],
                  'colours': int(len(np.unique(a[..., :3][a[..., 3] > 0], axis=0)))})
    log['audit'] = entry
    json.dump(log, open(ed, 'w'), indent=1)
    print(f"{name}: {entry['why'][:70]}... {entry['colours']} colours")


# ------------------------------------------------------------------------------------------------ stone
STONE_MAP = {'debca1': 'c9c2b4', 'cca093': 'b3ac9f', 'bc8b8f': 'a39b8e', '8f636c': '7a736a',
             '585b71': '5d5953', '3b3e47': '403d3a'}


def stone():
    a = start('park_stone')
    n = 0
    for f, t in STONE_MAP.items():
        m = (a[..., 3] > 0) & np.all(a[..., :3] == rgb(f), -1)
        a[m, :3] = rgb(t); n += int(m.sum())
    finish('park_stone', a, {'why': 'audit 6 Nov: the pink stones read as eggs or hams, not stones. A warm grey granite '
                                    'ramp, one colour to one, same lightness order; moss and ink kept; box and shape unchanged',
                             'colour_map': STONE_MAP, 'pixels': n})


# ------------------------------------------------------------------------------------------------ hedge
def hedge(R=7):
    a = start('park_hedge')
    al = a[..., 3] > 0
    H, W = al.shape
    cols = np.unique(a[..., :3][al], axis=0)
    ink = cols[(cols.astype(float) @ [0.299, 0.587, 0.114]).argmin()]
    top = min(y for y in range(H) if al[y].any())
    left = min(x for x in range(W) if al[:, x].any()); right = max(x for x in range(W) if al[:, x].any())
    hand = []
    # the arc's centres: R in from the art's outer edge (its outline) and R down from its top row
    for cx, sx in ((left + R, -1), (right - R, 1)):
        cy = top + R
        for y in range(top, cy + 1):
            for x in range(W):
                if (x - cx) * sx <= 0: continue
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d > R + 0.5 and al[y, x]:
                    hand.append({'x': x, 'y': y, 'from': hx(a[y, x]), 'to': 'clear', 'why': 'outside the rounded corner'})
                    a[y, x] = 0; al[y, x] = False
    # close the outline: an opaque pixel next to a cleared one (4-neighbour) on the new edge becomes ink
    for y in range(top, top + R + 2):
        for x in range(W):
            if not al[y, x] or (a[y, x, :3] == ink).all(): continue
            nb = [(y + dy, x + dx) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            if any(not (0 <= q[0] < H and 0 <= q[1] < W) or not al[q] for q in nb):
                hand.append({'x': x, 'y': y, 'from': hx(a[y, x]), 'to': hx(ink), 'why': 'the outline along the new edge'})
                a[y, x, :3] = ink
    finish('park_hedge', a, {'why': 'audit 6 Nov: a green cube twice Pepper\'s height. Its top trimmed to read as a clipped '
                                    f'hedge: both top corners rounded (radius {R}), outline closed in its ink; box unchanged',
                             'hand': hand})


# ------------------------------------------------------------------------------------------------ bush
RIM, WARM = '594257', 'b5793f'                     # look.lua citypark fg.rim, fg.warm


def bush():
    a = start('park_bush')
    al = a[..., 3] > 0
    hand = []
    k = 0
    for x in range(a.shape[1]):
        ys = np.nonzero(al[:, x])[0]
        if not len(ys): continue
        y = int(ys[0]); c = WARM if k % 5 == 2 else RIM; k += 1
        hand.append({'x': x, 'y': y, 'from': hx(a[y, x]), 'to': c, 'why': 'the front layer\'s thin rim on top'})
        a[y, x, :3] = rgb(c)
    finish('park_bush', a, {'why': 'audit 6 Nov: a flat black smudge on the earth band. Front layer rule: dark silhouette, '
                                   'a thin back-lit rim on top (the City Park front rim, every 5th column warm)', 'hand': hand})


# ------------------------------------------------------------------------------------------------ ground
def ground():
    a = start('park_ground')
    rows = list(range(9, 29)) + list(range(34, a.shape[0]))
    bands = {}
    n = 0
    for y in rows:
        c = Counter(tuple(int(v) for v in a[y, x, :3]) for x in range(a.shape[1]))
        top = np.array(c.most_common(1)[0][0], np.uint8)
        m = ~np.all(a[y, :, :3] == top, -1)
        n += int(m.sum()); a[y, :, :3] = top; bands[y] = hx(top)
    finish('park_ground', a, {'why': 'audit 6 Nov: speckle and dark flecks in the path and earth strata. Flat bands: each '
                                     'of rows 9-28 and 34-67 its majority colour (lawn 0-8 and the grass fringe 29-33 kept)',
                              'bands': bands, 'pixels': n})


if __name__ == '__main__':
    todo = sys.argv[1:] or ['stone', 'hedge', 'bush', 'ground']
    for t in todo: globals()[t]()
