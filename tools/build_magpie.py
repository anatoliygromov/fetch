#!/usr/bin/env python3
"""build_magpie.py: the City Park magpie sheet riverwalk/art/magpie.png from its SpriteCook sources (6 Nov).

Sources (art/gen/renders, Pixel Engine Image at exactly game size, so the cut is 1:1, pitch 1, nothing resampled):
  cp_magpie_a.png        perched, 30 x 18 (size B of docs/review/06nov/cp_critters/magpie_sizes_4x.png)
  cp_magpie_fly_b.png    flying, wings up, 30 x 22
  cp_magpie_flap_sheet.png  pixel-engine-v1.5 wingbeat of the flight still, 6 frames of 34 x 34 (frame 1 = the
                            still at (2, 6)); frame 5 (wings down) is used; 2, 3 and 4 are not
                            (the body melts while the wings pass under it).
Steps, all by rule, every changed pixel recorded in art/source/cp_magpie/edits.json:
  1. one palette for every frame (10 colours): the flight colours snapped to the perched bird's nearest colour
     when within 40 (Lab-free RGB distance); the animation's 16 colours mapped back to the still's by position.
  2. the tail flick: the perched bird with its tail raised: the perched tail mirrored about the rump row, drawn
     behind the wing tips, closed with the 1 px ink.
  3. wings level: the still with the raised wings taken off, back and primaries drawn by rule; wings down: the\n     animation's frame 5 on the still's palette, its specks fixed by rule, the tail the still's.
  4. one ink: every outline pixel #000000; the outline is closed (no body pixel touches the background).
Sheet: 5 cells of 32 x 26: perch, flick, up, level, down. The feet (perched) are at cell (20, 25): Sc.magpie draws
the cell with that point on (m.x, m.y). The beak tip is at cell (29, 10) perched and (29, 13) flying.
Writes riverwalk/art/magpie.png, art/source/cp_magpie/{magpie.aseprite, edits.json, *_cut.png},
art/gen/out/cp_magpie.cut.json, cp_magpie_fly.cut.json, cp_magpie_flap.cut.json.
Run from the repo root: python3 tools/build_magpie.py"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

RD, SRC = 'art/gen/renders/', 'art/source/cp_magpie/'
os.makedirs(SRC, exist_ok=True)
CW, CH = 32, 26
INK = (0, 0, 0)


def load(p): return np.array(Image.open(p).convert('RGBA')).astype(int)


perch = load(RD + 'cp_magpie_a.png')
fly = load(RD + 'cp_magpie_fly_b.png')
anim = load(RD + 'cp_magpie_flap_sheet.png')
afr = [anim[6:28, i * 34 + 2:i * 34 + 32] for i in range(6)]

# 1. the palette: the perched bird's 8 colours, plus the flight still's colours that are not near any of them
PAL = sorted({tuple(p[:3]) for p in perch.reshape(-1, 4) if p[3]})
def near(c, pal):
    d = [sum((a - b) ** 2 for a, b in zip(c, p)) for p in pal]
    i = int(np.argmin(d)); return pal[i], d[i] ** 0.5
fmap = {}
for p in sorted({tuple(p[:3]) for p in fly.reshape(-1, 4) if p[3]}):
    q, d = near(p, PAL)
    if sum(p) < 12: q, d = INK, 0
    if d > 40: PAL.append(p); q = p
    fmap[p] = q
PAL = sorted(set(PAL))
def snap(img, m):
    out = img.copy()
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y, x, 3]:
                out[y, x, :3] = m[tuple(img[y, x, :3])]
                out[y, x, 3] = 255
            else: out[y, x] = 0
    return out
perch_s = snap(perch, {p: (INK if sum(p) < 12 else p) for p in PAL + [tuple(p[:3]) for p in perch.reshape(-1, 4) if p[3]]})
fly_s = snap(fly, fmap)

# the animation's colours back to the still's: majority by position over frame 1 (= the still)
from collections import Counter, defaultdict
votes = defaultdict(Counter)
for y in range(22):
    for x in range(30):
        if afr[0][y, x, 3] and fly[y, x, 3]: votes[tuple(afr[0][y, x, :3])][fmap[tuple(fly[y, x, :3])]] += 1
amap = {}
for p in {tuple(p[:3]) for f in afr for p in f.reshape(-1, 4) if p[3]}:
    amap[p] = votes[p].most_common(1)[0][0] if p in votes else near(p, PAL)[0]
    if sum(p) < 12: amap[p] = INK


def flight(i):
    """animation frame i on the still's palette (the whole frame: the still's back is hidden under its raised wings,
    so the animation's own back line is kept); the tail and legs, which do not move, are the still's."""
    f = snap(afr[i], amap)
    out = f.copy()
    out[16:, :12] = fly_s[16:, :12]
    return out


def close_outline(a, box=None):
    """every transparent pixel 4-next to a coloured (non-ink) pixel becomes ink; returns how many."""
    h, w = a.shape[:2]; n = 0
    col = (a[..., 3] > 0) & (a[..., :3].sum(-1) > 0)
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] or (box and not (box[0] <= x <= box[2] and box[1] <= y <= box[3])): continue
            if any(0 <= y + dy < h and 0 <= x + dx < w and col[y + dy, x + dx] for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                a[y, x] = (*INK, 255); n += 1
    return n


# 2. the tail flick: the tail (left of x 14, from row 12 down) redrawn as a straight band raised 4 px at the tip
#    (the perched tail, rows 14-17 left of x 13, mirrored about the rump row 13: the same band, pointing up-left
#    behind the wing tips; drawn only where the perched bird is empty, so the wing tips stay in front)
flick = perch_s.copy()
tail = [(y, x) for y in range(14, 18) for x in range(0, 13) if perch_s[y, x, 3]]
for y, x in tail: flick[y, x] = 0
for y, x in tail:
    ty = 26 - y
    if not perch_s[ty, x, 3]: flick[ty, x] = perch_s[y, x]
close_outline(flick, (0, 6, 15, 17))

up = fly_s
# wings level (swept back along the body): the still with its raised wings taken off, the back closed with the ink,
# the white primaries laid back behind the blue coverts (art rows; the sheet places them 4 rows down). The
# animation's own level frame was not used: its back line had holes where the raised wings had hidden the body.
level = fly_s.copy()
level[0:6, 0:23] = 0; level[6:8, 0:22] = 0
WHITE, LIGHT, NAVYF = (245, 248, 252), (194, 196, 202), (31, 35, 54)          # the perched bird's white, light grey, navy
def put(img, y, xs, col): img[y, xs[0]:xs[1] + 1] = (*col, 255)
put(level, 7, (13, 20), INK); put(level, 8, (4, 13), INK); put(level, 8, (19, 21), NAVYF); put(level, 9, (20, 20), NAVYF)
put(level, 9, (3, 3), INK); put(level, 9, (4, 7), WHITE); put(level, 9, (8, 9), LIGHT)
put(level, 10, (4, 4), INK); put(level, 10, (5, 8), WHITE); put(level, 10, (9, 9), LIGHT)
put(level, 11, (5, 9), INK)
# wings down: the animation's frame 5 on the still's palette; its beak-grey specks on the shoulder become the blue
# sheen (rows up to 10) or the navy body, a lone ink pixel off the body is taken out
down = flight(4)
BEAKC, SHEEN = tuple(perch_s[3, 27, :3]), (52, 110, 167)
for y in range(down.shape[0]):
    for x in range(20):
        if down[y, x, 3] and tuple(down[y, x, :3]) == BEAKC: down[y, x, :3] = SHEEN if y <= 10 else NAVYF
for y in range(down.shape[0]):
    for x in range(down.shape[1]):
        if down[y, x, 3] and not any(0 <= y + dy < down.shape[0] and 0 <= x + dx < down.shape[1] and down[y + dy, x + dx, 3]
                                     for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))): down[y, x] = 0
for f in (level, down): close_outline(f)

# 3. the sheet
def place(cell, img, ox, oy):
    h, w = img.shape[:2]
    cell[oy:oy + h, ox:ox + w] = np.where(img[..., 3:] > 0, img, cell[oy:oy + h, ox:ox + w])
frames = []
for img, oy in ((perch_s, 7), (flick, 7), (up, 4), (level, 4), (down, 4)):
    c = np.zeros((CH, CW, 4), int); place(c, img, 0, oy); frames.append(c)
sheet = np.concatenate(frames, axis=1).astype(np.uint8)
Image.fromarray(sheet).save('riverwalk/art/magpie.png')

# records: the cuts (1:1), every changed pixel against the snapped sources, the .aseprite
Image.fromarray(perch.astype(np.uint8)).save(SRC + 'perch_cut.png')
Image.fromarray(fly.astype(np.uint8)).save(SRC + 'fly_cut.png')
Image.fromarray(anim.astype(np.uint8)).save(SRC + 'flap_anim.png')
base = [(perch, 7), (perch, 7), (fly, 4), (fly, 4), (fly, 4)]
px = []
for i, (fr, (b, oy)) in enumerate(zip(frames, base)):
    bc = np.zeros((CH, CW, 4), int); place(bc, b, 0, oy)
    for y, x in zip(*np.nonzero((fr != bc).any(-1))):
        px.append([i, int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in fr[y, x])])
json.dump({'asset': 'cp_magpie', 'sheet': 'riverwalk/art/magpie.png', 'cells': [CW, CH],
           'base': 'frames 1-2 art/source/cp_magpie/perch_cut.png at (0, 7); frames 3-5 fly_cut.png at (0, 4)',
           'method': 'tools/build_magpie.py: palette snap, flick tail by rule, flight wings from the animation frames 2 and 5, outline closed',
           'palette': ['#%02x%02x%02x' % p for p in sorted({tuple(int(v) for v in p[:3]) for p in sheet.reshape(-1, 4) if p[3]})],
           'changed': len(px), 'pixels': px}, open(SRC + 'edits.json', 'w'))
aseprite_io.write(SRC + 'magpie.aseprite', [f.astype(np.uint8) for f in frames], ms=90)
for n, sz in (('cp_magpie', [30, 18]), ('cp_magpie_fly', [30, 22]), ('cp_magpie_flap', [30, 22])):
    json.dump({'name': n, 'size': sz, 'render': {'cp_magpie': RD + 'cp_magpie_a.png', 'cp_magpie_fly': RD + 'cp_magpie_fly_b.png',
               'cp_magpie_flap': RD + 'cp_magpie_flap_sheet.png'}[n],
               'cut_by': 'Pixel Engine Image / pixel-engine-v1.5 output at game size: pitch 1, taken 1:1, nothing resampled; tools/build_magpie.py',
               'colours': len({tuple(p[:3]) for p in sheet.reshape(-1, 4) if p[3]}), 'fails': []},
              open(f'art/gen/out/{n}.cut.json', 'w'), indent=1)
print('magpie.png', sheet.shape[1], 'x', sheet.shape[0], 'colours',
      len({tuple(p[:3]) for p in sheet.reshape(-1, 4) if p[3]}), 'edits', len(px))
