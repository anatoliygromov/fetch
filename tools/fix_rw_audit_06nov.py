#!/usr/bin/env python3
"""fix_rw_audit_06nov.py: the River Walk audit's prop fixes (6 Nov 2026, 0 credits). Two pieces built by rule, three
fixed by hand by rule. Every changed pixel goes to art/source/NAME/edits.json under "06nov_audit" (x, y, from, to,
why; a built piece of a new size records its rule instead), the .aseprite source is written with
tools/aseprite_io.py and the slot png is saved. No automated clean pass: each rule names the pixels it touches.

  gritbox_front  BUILT (88 x 32, same slot and box): the green chest with a 3/4 side face read as a dumpster and
                 merged with the kiosk. Now front-on (BIBLE: a front and a thin cap): a pine grit box, a lid board
                 that overhangs the body by 2 px a side, three planks, an end batten each side with one nail per
                 plank, an iron hasp under the lid in the middle. 1 px ink outline (an obstacle).
  pontoon        BUILT (54 x 19, was 54 x 12): a grey slab on two stubs read as a table. Now a timber deck (the
                 ferry's mahogany ramp, plank ends every 7 px) on two floats that sit in the river: the waterline
                 (y 224) crosses them, the part under it is water-dark (the ripple beside them is drawn in code, stage.lua). A horn cleat on
                 each end of the deck for the mooring line (setpieces.lua). Drawn 3 rows higher (stage.lua), so the
                 deck top stays at y 212 and Pepper's box is unchanged.
  kennel         HAND: the white corner trim (2 px beside the ink on both sides, full height) read as a white halo
                 outline. The trim takes the falu red planks of its row (the 4-row plank pattern runs on down beside
                 the doorway), so the only edge is the 1 px dark ink (an obstacle). The doorway's top corners are
                 rounded into an arch (a dog house's door).
  bone, bone_gold HAND: the outline was open over and under the shaft (3 px each), so flowers and cobbles showed
                 through and the bone melted into them. A clear pixel 4-next to the bone's fill takes the
                 outline colour: a closed outline, same size, same anchor. Then the outline one step darker
                 (#5b4a36 -> #3a2c1e, gold #6b4410 -> #4a2e0c): on cream cobbles and white daisies the brown was
                 too close to the fill around it.
"""
import sys, os, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

SCENE = 'riverwalk/art/scene'
KEY = '06nov_audit'


def hx(s):
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def load(n):
    return np.array(Image.open(f'{SCENE}/{n}.png').convert('RGBA'))


def save(n, a, ed):
    d = f'art/source/{n}'; os.makedirs(d, exist_ok=True)
    p = f'{d}/edits.json'
    J = json.load(open(p)) if os.path.exists(p) else {'name': n}
    if KEY in J: print(n, 'already done', KEY); return
    if not os.path.exists(f'{d}/{n}_before_{KEY}.png'): shutil.copy(f'{SCENE}/{n}.png', f'{d}/{n}_before_{KEY}.png')
    J[KEY] = ed
    json.dump(J, open(p, 'w'), indent=0)
    aseprite_io.write(f'{d}/{n}.aseprite', [a], layer=n)
    Image.fromarray(a, 'RGBA').save(f'{SCENE}/{n}.png')
    print(n, a.shape[1], 'x', a.shape[0], 'colours', len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)))


def diff(old, new, why):
    """every pixel that differs (same size): x, y, from, to (RGBA), why"""
    ed = []
    for y, x in zip(*np.nonzero((old != new).any(-1))):
        ed.append({'x': int(x), 'y': int(y), 'from': old[y, x].tolist(), 'to': new[y, x].tolist(), 'why': why})
    return ed


class Canvas:
    def __init__(s, w, h): s.a = np.zeros((h, w, 4), np.uint8)
    def px(s, x, y, c):
        if 0 <= y < s.a.shape[0] and 0 <= x < s.a.shape[1]: s.a[y, x] = (*c, 255)
    def rect(s, x0, y0, x1, y1, c):                                   # inclusive
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.px(x, y, c)


INK = hx('050a17')                                                     # the River Walk ink (planter, pile)


# ------------------------------------------------------------------------------------------------ gritbox_front
def gritbox():
    W, H = 88, 32
    LIT, BASE, SHADE, GAP = hx('d8a868'), hx('b8844c'), hx('8c6038'), hx('5c3c24')          # pine
    ILIT, IBASE = hx('7a808c'), hx('4e5462')                                                 # iron
    c = Canvas(W, H)
    # the lid board: rows 0-6, the full 88 px (overhangs the body by 2 px a side), round top corners
    c.rect(1, 0, W - 2, 0, INK)
    c.rect(0, 1, 0, 5, INK); c.rect(W - 1, 1, W - 1, 5, INK)
    c.rect(1, 1, W - 2, 1, LIT); c.rect(1, 2, W - 2, 4, BASE); c.rect(1, 5, W - 2, 5, SHADE)
    c.rect(0, 6, W - 1, 6, INK)
    # the body: cols 2-85, rows 7-31
    L, R = 2, W - 3
    c.rect(L, 7, L, H - 1, INK); c.rect(R, 7, R, H - 1, INK); c.rect(L, H - 1, R, H - 1, INK)
    planks = [(7, 13), (15, 21), (23, 30)]
    for i, (y0, y1) in enumerate(planks):
        c.rect(L + 1, y0, R - 1, y1, BASE)
        c.rect(L + 1, y0, R - 1, y0, SHADE if i == 0 else LIT)        # the top plank lies in the lid's shadow
        c.rect(L + 1, y1, R - 1, y1, SHADE)
    for y in (14, 22): c.rect(L + 1, y, R - 1, y, GAP)                # the gaps between the planks
    for (y, xs) in ((10, (16, 24)), (10, (56, 63)), (18, (29, 37)), (18, (62, 69)), (27, (13, 19)), (27, (48, 56))):
        c.rect(xs[0], y, xs[1], y, SHADE)                              # one grain line per plank half, by rule
    # an end batten each side over the planks: 6 px, lit left edge, shaded right edge, a dark joint inside
    for bx0 in (L + 1, R - 6):
        c.rect(bx0, 7, bx0 + 5, 30, BASE)
        c.rect(bx0, 8, bx0, 30, LIT); c.rect(bx0 + 5, 8, bx0 + 5, 30, SHADE); c.rect(bx0, 7, bx0 + 5, 7, SHADE)
        c.rect(bx0 - 1 if bx0 > L + 1 else bx0 + 6, 7, bx0 - 1 if bx0 > L + 1 else bx0 + 6, 30, GAP)
        for (y0, y1) in planks: c.px(bx0 + 2, (y0 + y1) // 2, GAP); c.px(bx0 + 3, (y0 + y1) // 2, GAP)   # a nail per plank
    # the iron hasp: a plate hanging from the lid, cols 40-47, rows 3-11, a staple slot
    hx0, hx1, hy0, hy1 = 40, 47, 3, 11
    c.rect(hx0, hy0, hx1, hy1, INK)
    c.rect(hx0 + 1, hy0 + 1, hx1 - 1, hy1 - 1, IBASE)
    c.rect(hx0 + 1, hy0 + 1, hx1 - 1, hy0 + 1, ILIT); c.rect(hx0 + 1, hy0 + 1, hx0 + 1, hy1 - 1, ILIT)
    c.rect(hx0 + 3, 7, hx0 + 4, 9, INK)                                # the staple's slot
    return c.a


# ------------------------------------------------------------------------------------------------ pontoon
def pontoon():
    W, H = 54, 19                                                      # rows: y = 209 + r (deck top ink at r 3, y 212)
    LIT, BASE, SHADE, DEEP = hx('d49a54'), hx('a86e3e'), hx('7a4e2c'), hx('5a2e2a')          # the ferry's mahogany
    FLIT, FBASE, FSHADE = hx('788696'), hx('546070'), hx('3a4250')                           # floats
    SUB, SUBE = hx('2c4a7c'), hx('16285a')                             # the floats under the water, their edge
    ILIT, IBASE = hx('9c9ea8'), hx('5f7387')                           # the cleats (the ferry's steel)
    c = Canvas(W, H)
    # two horn cleats on the deck ends (rows 0-2)
    for x0 in (4, W - 11):
        c.rect(x0, 0, x0 + 6, 0, INK)
        c.px(x0, 1, INK); c.rect(x0 + 1, 1, x0 + 5, 1, ILIT); c.px(x0 + 6, 1, INK)
        c.rect(x0 + 1, 2, x0 + 5, 2, INK); c.px(x0 + 3, 2, IBASE)       # the horns' undersides, the stem
    # the deck: rows 3-8, cols 1-52
    c.rect(1, 3, W - 2, 3, INK); c.rect(1, 8, W - 2, 8, INK)
    c.rect(1, 4, 1, 7, INK); c.rect(W - 2, 4, W - 2, 7, INK)
    c.rect(2, 4, W - 3, 4, LIT); c.rect(2, 5, W - 3, 6, BASE); c.rect(2, 7, W - 3, 7, SHADE)
    for x in (9, 16, 23, 30, 37, 44): c.rect(x, 5, x, 7, DEEP)         # plank ends: 7, 6, 6, 6, 6, 6, 7
    # two floats under it, cols 4-23 and 30-49; the waterline at r 15 (y 224)
    for f0 in (4, 30):
        f1 = f0 + 19
        for r in range(9, 15):
            c.px(f0, r, INK); c.px(f1, r, INK)
            col = {9: FSHADE, 10: FBASE, 11: FLIT, 12: FBASE, 13: FBASE, 14: FSHADE}[r]
            c.rect(f0 + 1, r, f1 - 1, r, col)
        for r in range(15, 19):                                        # under the water: dark, a navy edge
            c.px(f0, r, SUBE); c.px(f1, r, SUBE)
            c.rect(f0 + 1, r, f1 - 1, r, SUBE if r == 18 else SUB)
    return c.a


# ------------------------------------------------------------------------------------------------ kennel
def kennel(a):
    b = a.copy()
    plank = {0: hx('9e3a2b'), 1: hx('c0503a'), 2: hx('9e3a2b'), 3: hx('74281f')}   # rows 6-15: f g f h, period 4
    for r in range(6, 35):
        for x in (1, 2, 3, 30, 31, 32): b[r, x, :3] = plank[(r - 6) % 4]
    # the doorway (rows 16-34, cols 4-29): an arch. Inside: rows 17 +: cols 9-24, 7-26, 6-27, then 5-28
    inner = {17: (9, 24), 18: (7, 26), 19: (6, 27)}
    J, K = hx('1e1a1e'), hx('2c262a')
    inside = np.zeros(b.shape[:2], bool)
    for r in range(17, 35):
        x0, x1 = inner.get(r, (5, 28))
        inside[r, x0:x1 + 1] = True
    for r in range(16, 35):
        for x in range(4, 30):
            if inside[r, x]:
                b[r, x, :3] = K if not inside[r - 1, x] else J              # the arch's inner shadow
                continue
            near = inside[max(0, r - 1):r + 2, max(0, x - 1):x + 2].any()
            b[r, x, :3] = INK_K if near else plank[(r - 6) % 4]
    return b


INK_K = hx('12121a')                                                   # the kennel's own ink


# ------------------------------------------------------------------------------------------------ bones
def close_bone(a):
    b = a.copy()
    op = a[..., 3] > 0
    cols, n = np.unique(a[op][:, :3], axis=0, return_counts=True)
    edge = None
    for cc in cols:                                                    # the outline colour: the darkest
        if edge is None or int(cc.astype(int).sum()) < int(edge.astype(int).sum()): edge = cc
    fill = op & ~(a[..., :3] == edge).all(-1)
    H, W = op.shape
    for y in range(H):
        for x in range(W):
            if op[y, x]: continue
            if any(0 <= y + dy < H and 0 <= x + dx < W and fill[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                b[y, x] = (*edge, 255)
    dark = DARKER.get(tuple(int(v) for v in edge))                     # then the outline one step darker, so the
    if dark: b[(b[..., 3] > 0) & (b[..., :3] == edge).all(-1), :3] = dark   # bone stands off cream cobbles and daisies
    return b


DARKER = {hx('5b4a36'): hx('3a2c1e'), hx('6b4410'): hx('4a2e0c')}       # bone, bone_gold


if __name__ == '__main__':
    todo = set(sys.argv[1:]) or {'gritbox_front', 'pontoon', 'kennel', 'bone', 'bone_gold'}
    if 'gritbox_front' in todo:
        old = load('gritbox_front'); new = gritbox()
        save('gritbox_front', new, {'rule': 'built by tools/fix_rw_audit_06nov.py gritbox(): front-on pine grit box, same 88 x 32 slot',
                                    'pixels': diff(old, new, 'rebuilt front-on (audit 6 Nov: read as a dumpster, merged with the kiosk)')})
    if 'pontoon' in todo:
        save('pontoon', pontoon(), {'rule': 'built by tools/fix_rw_audit_06nov.py pontoon(): 54 x 19 (was 54 x 12), timber deck on floats '
                                    'in the water, horn cleats; drawn at the mover y0 - 5 (was - 2)'})
    if 'kennel' in todo:
        old = load('kennel'); save('kennel', kennel(old), diff(old, kennel(old), 'white corner trim read as a halo; arched doorway'))
    for n in ('bone', 'bone_gold'):
        if n in todo:
            old = load(n); save(n, close_bone(old), diff(old, close_bone(old), 'closed outline: the shaft showed what was behind it'))
