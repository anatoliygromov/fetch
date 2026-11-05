#!/usr/bin/env python3
"""fix_cp_round3.py: review round 2 fixes (5 Nov 2026; art/gen/reviews/cp_*.md "Round 2"), run after fix_cp_round1.py.
Starts from art/source/NAME/NAME_round1.png (the round 1 result, kept), lists every pixel under "round3" in
edits.json, writes the .aseprite and the slot png.
cp_oak (item 5, patchwork): in the reviewer's boxes (120-300, 40-140), (20-60, 60-80), (0-90, 140-200), and at the
  19 blotches asset_qa lists, a leaf patch of 2-24 px whose ring is at least 70 % one other leaf colour takes that
  colour, so each leaf mass reads as 3-4 shade clumps. Bark and the crown's edge are not touched.
cp_mid_lime, cp_mid_birch (item 2): the crown highlight down to about luma 170-175 on screen (raw about 150-155):
  mid lime #fcc23e -> #d8941c and its next shade #d58d11 joins #a95906 (three clear shades: 63, 103, 155; a fourth
  between them read as blotches); birch #f9c219 -> #d4951e and its mid #ca8106 -> #b46e06 (the steps stay apart)."""
import sys, os, json, shutil
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
import aseprite_io

if os.path.exists('art/source/cp_oak/RECUT'):
    sys.exit('history: the oak was re-cut on 5 Nov (tools/recut_cp_oak.py); the round scripts no longer run')
def hx(s): return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)])

def load(name):
    src = f'art/source/{name}/{name}_round1.png'
    if not os.path.exists(src): shutil.copy(f'riverwalk/art/scene/{name}.png', src)
    a = np.array(Image.open(src).convert('RGBA')); return a[..., :3].astype(int), a[..., 3] > 0, src

def save(name, rgb, al, edits, src):
    out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); out[~al] = 0
    p = f'art/source/{name}/edits.json'; J = json.load(open(p))
    J['round3'] = {'from': src, 'review': f'art/gen/reviews/{name}.md (Round 2)', 'edits': edits}
    json.dump(J, open(p, 'w'), indent=0)
    aseprite_io.write(f'art/source/{name}/{name}.aseprite', [out], layer=name)
    Image.fromarray(out, 'RGBA').save(f'riverwalk/art/scene/{name}.png')
    print(name, len(edits), 'pixels', 'colours', len(np.unique(out[al][:, :3], axis=0)))

# --- oak patchwork
rgb, al, src = load('cp_oak'); edits = []
LEAF = [hx(c) for c in ('#832918', '#ae4015', '#dc6e1d', '#e48c28')]
def isleaf(c): return any((c == l).all() for l in LEAF)
pa = np.pad(al, 1); edge = al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
boxes = [(120, 40, 300, 140), (20, 60, 60, 80), (0, 140, 90, 200)]
inbox = np.zeros_like(al)
for x0, y0, x1, y1 in boxes: inbox[y0:y1 + 1, x0:x1 + 1] = True
for _ in range(2):
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]; key = np.where(al, key, -1)
    for L in LEAF:
        k = (L[0] << 16) | (L[1] << 8) | L[2]
        lb, n = ndimage.label(key == k, structure=np.ones((3, 3)))
        sz = np.bincount(lb.ravel())
        for i in range(1, n + 1):
            if not (1 <= sz[i] <= 24): continue
            m = lb == i
            ys, xs = np.nonzero(m)
            if not (inbox[m].any() or sz[i] >= 2) or (edge & m).any(): continue
            if not inbox[m].any() and sz[i] > 24: continue
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m
            if (ring & ~al).any(): continue
            vals = key[ring]; u, c = np.unique(vals, return_counts=True); o = int(u[c.argmax()])
            oc = np.array([(o >> 16) & 255, (o >> 8) & 255, o & 255])
            if c.max() / c.sum() < 0.7 or not isleaf(oc): continue
            if not inbox[m].any() and np.sqrt(((oc - L) ** 2).sum()) >= 45: continue   # outside the boxes: asset_qa's blotches only
            for y, x in zip(ys, xs):
                edits.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist(), 'to': oc.tolist(), 'why': 'leaf patch merged into its clump'})
                rgb[y, x] = oc
save('cp_oak', rgb, al, edits, src)

# --- mid highlights
for name, pairs in (('cp_mid_lime', (('#d58d11', '#a95906'), ('#fcc23e', '#d8941c'))),
                    ('cp_mid_birch', (('#ca8106', '#b46e06'), ('#f9c219', '#d4951e')))):
    rgb, al, src = load(name); edits = []
    for f, t in pairs:
        sel = (rgb == hx(f)).all(-1) & al
        for y, x in zip(*np.nonzero(sel)):
            edits.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist(), 'to': hx(t).tolist(), 'why': 'highlight to about 172 on screen'})
        rgb[sel] = hx(t)
    save(name, rgb, al, edits, src)
