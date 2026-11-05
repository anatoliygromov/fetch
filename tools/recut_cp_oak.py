#!/usr/bin/env python3
"""recut_cp_oak.py: the old oak re-cut (5 Nov 2026, review round 3: three rounds of pixel fixes left a leaf patchwork,
so the method changes, 0 credits). From its original render art/gen/renders/cp_oak_r1b.png, with the pipeline that
made the lime and ash clean:
  1. tools/cut_cp_tree.py --leaf 5 --bark 4 --rim-lum 60 --mode 2: per-material k-means ramps, then a 3x3 majority on
     each material's cluster labels (two passes) so leaf fields form clear clumps (a clean pass on the new cut only;
     it picks among the material's own colours, never an average)
  2. tools/polish_cp_trees.py: lone glints, 1 px spikes, pinholes
  3. this script, the round 1 rules on the new colours (every pixel listed in art/source/cp_oak/edits.json, "recut"):
     the nine loose limb fragments (same render, same crop, same boxes) and loose bark specks filled with the leaf
     colour around them; no near-black: bark under luma 45 on an edge takes the next bark shade, inside it the second
     darkest, leaf under luma 45 the next leaf shade; the leaf highlight brought to luma 155 (about 174 on screen);
     the crown's flat cuts at x 0 and x 387 carved round with the dark leaf rim.
Old rounds: art/source/cp_oak/round3/."""
import sys, os, json, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
import aseprite_io

LUM = np.array([0.299, 0.587, 0.114])
if '--no-cut' not in sys.argv:
    subprocess.run([sys.executable, 'tools/cut_cp_tree.py', 'art/gen/renders/cp_oak_r1b.png', 'cp_oak', '--leaf', '5', '--bark', '4',
                    '--rim-lum', '60', '--mode', '2'], check=True)
    if os.path.exists('art/source/cp_oak/cp_oak_clean.png'): os.remove('art/source/cp_oak/cp_oak_clean.png')
    subprocess.run([sys.executable, 'tools/polish_cp_trees.py', 'cp_oak'], check=True)
a = np.array(Image.open('riverwalk/art/scene/cp_oak.png').convert('RGBA'))
Image.fromarray(a).save('art/source/cp_oak/cp_oak_polish.png')
rgb = a[..., :3].astype(int); al = a[..., 3] > 0
leafm = np.array(Image.open('art/source/cp_oak/cp_oak_leafmask.png')) > 0
H, W = al.shape
cols = np.unique(rgb[al], axis=0)
def share_leaf(c):
    m = (rgb == c).all(-1) & al
    return (m & leafm).sum() / max(1, m.sum())
LEAF = sorted([c for c in cols if share_leaf(c) >= 0.5], key=lambda c: c @ LUM)
BARK = sorted([c for c in cols if share_leaf(c) < 0.5], key=lambda c: c @ LUM)
print('leaf ramp', ['#%02x%02x%02x %d' % (*c, round(c @ LUM)) for c in LEAF])
print('bark ramp', ['#%02x%02x%02x %d' % (*c, round(c @ LUM)) for c in BARK])
edits = []
def setp(y, x, c, why):
    edits.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist() if al[y, x] else None,
                  'to': None if c is None else [int(v) for v in c], 'why': why})
    if c is None: al[y, x] = False
    else: rgb[y, x] = c; al[y, x] = True
def isin(c, ramp): return any((c == r).all() for r in ramp)

def fill(boxes, why):
    for (x0, y0, x1, y1) in boxes:
        todo = [(y, x) for y in range(max(0, y0), min(H, y1 + 1)) for x in range(max(0, x0), min(W, x1 + 1))
                if al[y, x] and not isin(rgb[y, x], LEAF)]
        for _ in range(60):
            if not todo: break
            nxt = []
            for y, x in todo:
                nb = [tuple(rgb[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
                      if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and al[yy, xx] and isin(rgb[yy, xx], LEAF)]
                if len(nb) >= 2: setp(y, x, max(set(nb), key=nb.count), why)
                else: nxt.append((y, x))
            if len(nxt) == len(todo):
                for y, x in nxt: setp(y, x, None, why + ' (no leaf beside it)')
                nxt = []
            todo = nxt

# loose limb fragments (the reviewer's round 1 boxes) and loose bark specks
fill([(259, 70, 293, 86), (93, 70, 134, 96), (313, 148, 340, 167), (67, 104, 105, 116), (220, 54, 239, 78),
      (288, 201, 316, 215), (38, 108, 67, 120), (286, 98, 305, 114), (147, 34, 163, 52)], 'loose limb fragment')
bark = np.zeros_like(al)
for c in BARK: bark |= (rgb == c).all(-1) & al
lb, n = ndimage.label(bark, structure=np.ones((3, 3))); sz = np.bincount(lb.ravel()); sz[0] = 0
for i in range(1, n + 1):
    if sz[i] < 60 and i != sz.argmax():
        ys, xs = np.nonzero(lb == i); fill([(xs.min(), ys.min(), xs.max(), ys.max())], 'loose bark speck')
# no near-black
bark = np.zeros_like(al)
for c in BARK: bark |= (rgb == c).all(-1) & al
pa = np.pad(bark, 1)
nonbark_nb = ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
dark_b = [c for c in BARK if c @ LUM < 45]; ok_b = [c for c in BARK if c @ LUM >= 45]
for c in dark_b:                                                     # an ink edge: the bark's dark shade
    sel = (rgb == c).all(-1) & al
    for y, x in zip(*np.nonzero(sel & nonbark_nb)): setp(y, x, ok_b[0], 'bark ink edge -> the bark dark shade')
furrow = [c for c in BARK if c @ LUM >= 30]                          # inside, nothing under luma 30 (a dark brown stays)
for c in [c for c in BARK if c @ LUM < 30]:
    for y, x in zip(*np.nonzero((rgb == c).all(-1) & al)): setp(y, x, furrow[0], 'near-black inside the bark -> dark brown')
dark_l = [c for c in LEAF if c @ LUM < 45]; ok_l = [c for c in LEAF if c @ LUM >= 45]
GAP = ok_l[0]                                                        # the gaps between clumps: the leaf's dark rust (luma 80;
for c in dark_l:                                                     # a darker rust read as an outline round the crown)
    for y, x in zip(*np.nonzero((rgb == c).all(-1) & al)): setp(y, x, GAP, 'leaf near-black -> leaf dark shade')
# highlight
for c in LEAF:
    l = c @ LUM
    if l > 156:
        t = np.array([0xe4, 0x8c, 0x28])                            # the warm orange-gold the reviewer passed (luma 155)
        for y, x in zip(*np.nonzero((rgb == c).all(-1) & al)): setp(y, x, t, 'leaf highlight to luma 155 (about 174 on screen)')
# a brown leaf tone (#9f6734 classed leaf: the render's lit twigs inside clumps) reads muddy among the oranges: in the
# leaves it becomes a true orange-red mid shade #b8501a (luma 105), so the leaf ramp is 80, 105, 134, 155
for c in LEAF:
    if abs(c[0] - c[1]) < 70 and 100 < c @ LUM < 125:
        for y, x in zip(*np.nonzero((rgb == c).all(-1) & al & leafm)): setp(y, x, [0xb8, 0x50, 0x1a], 'muddy brown in the leaves -> orange-red mid shade')
# carve the flat cuts
rim = GAP
for col, step in ((0, 1), (W - 1, -1)):
    rows = np.nonzero(al[:, col])[0]
    if not len(rows): continue
    for r in np.split(rows, np.nonzero(np.diff(rows) > 1)[0] + 1):
        y0, y1 = r[0], r[-1]; c0 = (y0 + y1) / 2; half = max(1, (y1 - y0 + 2) / 2)
        d = min(6, max(2, int((y1 - y0 + 1) / 4)))
        for y in range(y0, y1 + 1):
            bite = int(round(d * ((y - c0) / half) ** 2))
            for k in range(bite):
                x = col + step * k
                if al[y, x]: setp(y, x, None, 'flat frame cut carved round')
            x = col + step * bite
            if 0 <= x < W and al[y, x]: setp(y, x, rim, 'new crown edge: dark leaf rim')
# holes the deletions left
h = ~al & ndimage.binary_fill_holes(al)
lb, n = ndimage.label(h)
for i in range(1, n + 1):
    m = lb == i
    if m.sum() > 4: continue
    v = [tuple(c) for c in rgb[ndimage.binary_dilation(m) & al]]
    for y, x in zip(*np.nonzero(m)): setp(y, x, max(set(v), key=v.count), 'pinhole closed')
out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); out[~al] = 0
p = 'art/source/cp_oak/edits.json'; J = json.load(open(p))
J['recut'] = {'from': 'art/source/cp_oak/cp_oak_polish.png', 'review': 'art/gen/reviews/cp_oak.md (Round 3)', 'edits': edits}
json.dump(J, open(p, 'w'), indent=0)
aseprite_io.write('art/source/cp_oak/cp_oak.aseprite', [out], layer='cp_oak')
Image.fromarray(out, 'RGBA').save('riverwalk/art/scene/cp_oak.png')
w = {}
for e in edits: w[e['why']] = w.get(e['why'], 0) + 1
print('cp_oak re-cut', w, 'colours', len(np.unique(out[al][:, :3], axis=0)))
