#!/usr/bin/env python3
"""fix_cp_round1.py: review round 1 fixes for the City Park sample screen trees (5 Nov 2026; art/gen/reviews/cp_*.md).
Runs on the polished files (tools/polish_cp_trees.py output, kept as art/source/NAME/NAME_polish.png), applies only the
reviewer's findings at the listed positions, lists every changed pixel in art/source/NAME/edits.json under "round1",
writes the .aseprite source and the slot png. Rerunnable: it always starts from NAME_polish.png.

cp_oak  (review items 2, 3, 4, 5)
  floating  the nine detached limb fragments (reviewer's boxes) are deleted: their bark pixels take the leaf colour
            most of their leaf neighbours have, filled from the outside in
  ink       the bark's near-black edge (#150e15, #332324 next to a leaf or transparent pixel) becomes the bark's own
            darker shade #55382b; #150e15 left inside the bark becomes #332324 (the furrows stay the darkest bark,
            no near-black left); the leaves' near-black #281b1a becomes their dark rust #832918
  light     the highlight #f6ad35 (luma 181, 193 on screen) becomes #e48c28 (luma 155, about 174 on screen after the
            0.28 fade): nothing in the back layer lighter than the tree line
  cut       the crown's flat cuts at x 0 and x 387 are carved into round bulges (the new edge pixel in the dark rust)
  patch     in the reviewer's boxes (120-300, 40-140) and (0-90, 140-200): leaf islands of 1-6 px inside one other leaf
            colour take that colour (the mottling), each pixel listed
cp_lime (review items 2, 3, 4)
  floating  the ten detached limb bars (reviewer's boxes), as the oak's
  ink       bark edge #0e0508, #261020 -> #553128; #0e0508 inside -> #261020; leaf #3d1413 on the edge -> #79200f
  light     the leaf ramp moves down one step so the highlight is under luma 156: #fdd527 -> #e4901a, #ed8b04 -> #d97a06
cp_mid_maple (item 5): lone dark specks in the crown top rows and the trunk pixel (36, 113) take their neighbours'
            colour; the dark maroon #471616 inside the right-side blotch (49-72, 39-65) and (40-64, 68-86), not on the
            crown's edge, becomes the next shade #a53008
cp_mid_birch (item 2): the white trunk #cfd5d1 and #cbbea8 become a warm grey #706860 (luma 105, about 150 on screen
            after the mid fade), its shade #888187 becomes #504a46"""
import sys, os, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

LUM = np.array([0.299, 0.587, 0.114])
def hx(s): return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)])
def eq(rgb, c): return (rgb == hx(c)).all(-1)


def load(name):
    src = f'art/source/{name}/{name}_polish.png'
    if not os.path.exists(src): shutil.copy(f'riverwalk/art/scene/{name}.png', src)
    a = np.array(Image.open(src).convert('RGBA'))
    return a[..., :3].astype(int), a[..., 3] > 0


class Ed:
    def __init__(s, rgb, al): s.rgb, s.al, s.list = rgb, al, []
    def set(s, y, x, c, why):
        c = None if c is None else np.asarray(c, int)
        s.list.append({'x': int(x), 'y': int(y), 'from': s.rgb[y, x].tolist() if s.al[y, x] else None,
                       'to': None if c is None else c.tolist(), 'why': why})
        if c is None: s.al[y, x] = False
        else: s.rgb[y, x] = c; s.al[y, x] = True


def save(name, E):
    out = np.dstack([E.rgb, np.where(E.al, 255, 0)]).astype(np.uint8); out[~E.al] = 0
    p = f'art/source/{name}/edits.json'; J = json.load(open(p))
    J['round1'] = {'from': f'art/source/{name}/{name}_polish.png', 'review': f'art/gen/reviews/{name}.md', 'edits': E.list}
    json.dump(J, open(p, 'w'), indent=0)
    aseprite_io.write(f'art/source/{name}/{name}.aseprite', [out], layer=name)
    Image.fromarray(out, 'RGBA').save(f'riverwalk/art/scene/{name}.png')
    whys = {}
    for e in E.list: whys[e['why']] = whys.get(e['why'], 0) + 1
    print(name, whys, 'colours', len(np.unique(out[E.al][:, :3], axis=0)))


def floating(E, boxes, leafcols, why='floating limb deleted'):
    leafset = {tuple(hx(c)) for c in leafcols}
    H, W = E.al.shape
    for (x0, y0, x1, y1) in boxes:
        todo = [(y, x) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                if 0 <= y < H and 0 <= x < W and E.al[y, x] and tuple(E.rgb[y, x]) not in leafset]
        for _ in range(60):
            if not todo: break
            nxt = []
            for y, x in todo:
                nb = [tuple(E.rgb[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
                      if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and E.al[yy, xx] and tuple(E.rgb[yy, xx]) in leafset]
                if len(nb) >= 2:
                    E.set(y, x, max(set(nb), key=nb.count), why)
                else: nxt.append((y, x))
            if len(nxt) == len(todo):
                for y, x in nxt: E.set(y, x, None, why + ' (no leaf beside it)')
                nxt = []
            todo = nxt


def edge_of(al):
    pa = np.pad(al, 1)
    return al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])


def ink(E, inks, barkcols, bark_edge, inner_from, inner_to, leaf_dark=None, leaf_dark_to=None, leaf_edge_only=False):
    rgb, al = E.rgb, E.al
    H, W = al.shape
    bark = np.zeros_like(al)
    for c in barkcols + inks: bark |= eq(rgb, c) & al
    isink = np.zeros_like(al)
    for c in inks: isink |= eq(rgb, c) & al
    pa = np.pad(bark, 1)
    nonbark_nb = ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
    for y, x in zip(*np.nonzero(isink & nonbark_nb)): E.set(y, x, hx(bark_edge), 'ink edge -> bark dark shade')
    for y, x in zip(*np.nonzero(eq(rgb, inner_from) & al)): E.set(y, x, hx(inner_to), 'near-black inside the bark -> furrow shade')
    if leaf_dark:
        sel = eq(rgb, leaf_dark) & al
        if leaf_edge_only: sel &= edge_of(al)
        for y, x in zip(*np.nonzero(sel)): E.set(y, x, hx(leaf_dark_to), 'leaf near-black -> leaf dark shade')


def recolour(E, frm, to, why):
    for y, x in zip(*np.nonzero(eq(E.rgb, frm) & E.al)): E.set(y, x, hx(to), why)


def carve(E, col, rimc, depth=6):
    al = E.al; H, W = al.shape
    rows = np.nonzero(al[:, col])[0]
    if not len(rows): return
    runs = np.split(rows, np.nonzero(np.diff(rows) > 1)[0] + 1)
    step = 1 if col == 0 else -1
    for r in runs:
        y0, y1 = r[0], r[-1]; c = (y0 + y1) / 2; half = max(1, (y1 - y0 + 2) / 2)
        d = min(depth, max(2, int((y1 - y0 + 1) / 4)))
        for y in range(y0, y1 + 1):
            t = (y - c) / half
            bite = int(round(d * t * t))
            for k in range(bite):
                x = col + step * k
                if al[y, x]: E.set(y, x, None, 'flat frame cut carved round')
            x = col + step * bite
            if 0 <= x < W and al[y, x]: E.set(y, x, hx(rimc), 'new crown edge: dark rust rim')


def patch(E, boxes, leafcols, maxn=6):
    from scipy import ndimage
    leafset = [hx(c) for c in leafcols]
    for (x0, y0, x1, y1) in boxes:
        sub = E.rgb[y0:y1 + 1, x0:x1 + 1]; sa = E.al[y0:y1 + 1, x0:x1 + 1]
        for c in leafset:
            m = (sub == c).all(-1) & sa
            lb, n = ndimage.label(m, structure=np.ones((3, 3)))
            sz = np.bincount(lb.ravel())
            for i in range(1, n + 1):
                if sz[i] > maxn: continue
                comp = lb == i
                ring = ndimage.binary_dilation(comp, structure=np.ones((3, 3))) & ~comp
                if (ring & ~sa).any(): continue
                vals = [tuple(v) for v in sub[ring]]
                o = max(set(vals), key=vals.count)
                if vals.count(o) / len(vals) < 0.85 or not any((np.array(o) == l).all() for l in leafset): continue
                for yy, xx in zip(*np.nonzero(comp)): E.set(y0 + yy, x0 + xx, o, 'leaf island merged (mottling)')


# --- cp_oak
rgb, al = load('cp_oak'); E = Ed(rgb, al)
OAK_LEAF = ['#281b1a', '#832918', '#ae4015', '#dc6e1d', '#f6ad35']   # (#9a6333, the limbs' light edge, goes with them)
floating(E, [(259, 70, 293, 86), (93, 70, 134, 96), (313, 148, 340, 167), (67, 104, 105, 116), (220, 54, 239, 78),
             (288, 201, 316, 215), (38, 108, 67, 120), (286, 98, 305, 114), (147, 34, 163, 52)], OAK_LEAF)
ink(E, ['#150e15', '#332324'], ['#55382b', '#84492c', '#9a6333'], '#55382b', '#150e15', '#332324', '#281b1a', '#832918')
# the bark bits left outside the boxes that touch no limb (specks of the deleted fragments): the same fill
from scipy import ndimage as _nd
_bark = np.zeros_like(E.al)
for _c in ('#332324', '#55382b', '#84492c'): _bark |= eq(E.rgb, _c) & E.al
_lb, _n = _nd.label(_bark, structure=np.ones((3, 3)))
_sz = np.bincount(_lb.ravel()); _sz[0] = 0
for _i in range(1, _n + 1):
    if _sz[_i] < 60 and _i != _sz.argmax():
        ys, xs = np.nonzero(_lb == _i)
        floating(E, [(xs.min(), ys.min(), xs.max(), ys.max())], OAK_LEAF, 'loose bark speck deleted')
recolour(E, '#f6ad35', '#e48c28', 'highlight down to luma 155 (about 174 on screen)')
carve(E, 0, '#832918'); carve(E, E.al.shape[1] - 1, '#832918')
patch(E, [(120, 40, 300, 140), (0, 140, 90, 200)], ['#832918', '#ae4015', '#dc6e1d', '#e48c28'])
# a lit limb edge left as a thin light streak in the dark rust after the fragment at (93,70)-(134,96) went (5x check)
for _ in range(3):
    for y in range(76, 93):
        for x in range(108, 125):
            if E.al[y, x] and not eq(E.rgb[y:y + 1, x:x + 1], '#832918')[0, 0]:
                nb = [tuple(E.rgb[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1) if E.al[yy, xx]]
                if nb.count(tuple(hx('#832918'))) >= 3: E.set(y, x, hx('#832918'), 'light streak of a deleted limb')
_h = ~E.al & _nd.binary_fill_holes(E.al)                         # holes of 1-4 px the deletions left: closed
_lb, _n = _nd.label(_h)
for _i in range(1, _n + 1):
    _m = _lb == _i
    if _m.sum() > 4: continue
    _ring = _nd.binary_dilation(_m) & E.al
    _v = [tuple(v) for v in E.rgb[_ring]]
    for y, x in zip(*np.nonzero(_m)): E.set(y, x, max(set(_v), key=_v.count), 'pinhole closed')
save('cp_oak', E)

# --- cp_lime
rgb, al = load('cp_lime'); E = Ed(rgb, al)
LIME_LEAF = ['#3d1413', '#79200f', '#bf4403', '#ed8b04', '#fdd527']
floating(E, [(419, 360, 440, 415), (398, 390, 414, 427), (44, 267, 84, 277), (379, 146, 389, 161), (96, 197, 109, 209),
             (93, 396, 101, 421), (364, 12, 378, 32), (414, 403, 432, 421), (378, 389, 388, 407), (435, 211, 447, 227)],
         LIME_LEAF[1:])   # (the lime's loose bars are drawn in its darkest leaf red #3d1413: that colour goes in the boxes)
ink(E, ['#0e0508', '#261020'], ['#553128', '#8f7963'], '#553128', '#0e0508', '#261020', '#3d1413', '#79200f', leaf_edge_only=True)
recolour(E, '#ed8b04', '#d97a06', 'leaf ramp one step down')
recolour(E, '#fdd527', '#e4901a', 'highlight down to luma 156 (about 174 on screen)')
save('cp_lime', E)

# --- cp_mid_maple
rgb, al = load('cp_mid_maple'); E = Ed(rgb, al)
DARK = [hx('#471616'), hx('#582e1e'), hx('#491c17'), hx('#5c1b2d')]
H, W = al.shape
def lone_dark(E, y, x):
    if not E.al[y, x] or not any((E.rgb[y, x] == d).all() for d in DARK): return
    nb = [tuple(E.rgb[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
          if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and E.al[yy, xx]]
    darkn = sum(1 for v in nb if any((np.array(v) == d).all() for d in DARK))
    if nb and darkn <= 2:
        light = [v for v in nb if not any((np.array(v) == d).all() for d in DARK)]
        if light: E.set(y, x, max(set(light), key=light.count), 'dark speck in the crown')
for y in range(0, 14):
    for x in range(W): lone_dark(E, y, x)
for y in range(14, 90):
    for x in range(W):
        if not edge_of(E.al)[y, x]: lone_dark(E, y, x)
if E.al[113, 36]: E.set(113, 36, E.rgb[113, 35] if E.al[113, 35] else E.rgb[112, 36], 'stray dark pixel in the trunk')
ed = edge_of(E.al)
for (x0, y0, x1, y1) in [(49, 39, 72, 65), (40, 68, 64, 86)]:
    for y in range(y0, y1 + 1):
        for x in range(x0, min(x1, W - 1) + 1):
            if E.al[y, x] and eq(E.rgb[y:y + 1, x:x + 1], '#471616')[0, 0] and not ed[y, x]:
                E.set(y, x, hx('#a53008'), 'dark blotch inside the crown -> next shade')
save('cp_mid_maple', E)

# --- cp_mid_birch
rgb, al = load('cp_mid_birch'); E = Ed(rgb, al)
recolour(E, '#cfd5d1', '#706860', 'white trunk -> warm grey (about 150 on screen)')
recolour(E, '#cbbea8', '#706860', 'light trunk top -> warm grey')
recolour(E, '#888187', '#504a46', 'trunk shade below the new grey')
save('cp_mid_birch', E)
