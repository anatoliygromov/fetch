#!/usr/bin/env python3
"""fix_cp_willow.py: one hand rule on the willow's cut (night 6 Nov 2026, cp track), after tools/cut_cp_tree.py and
tools/polish_cp_trees.py cp_willow. Found at 5x: the strand tips and the gaps between strands carry specks of the
bark ramp (61,42,43 / 84,56,52 / 127,85,70 / 172,92,74), 1 to 6 px each, not joined to the trunk or a limb: pink dots
on golden leaves. Rule 'bark speck': a bark-coloured patch of 6 px or fewer (8-connected) takes, pixel by pixel, the
colour most of its opaque non-bark 8-neighbours have (a leaf shade; never an average). Patches of 7 px and more are
limbs seen through the curtain and stay. Every changed pixel goes in art/source/cp_willow/edits.json under "r1";
the .aseprite source and the slot png are written again. r1b: one blotch by asset_qa's rule. Re-running is a no-op."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
import aseprite_io

P = 'riverwalk/art/scene/cp_willow.png'
J = json.load(open('art/source/cp_willow/edits.json'))
a = np.array(Image.open(P).convert('RGBA'))
al = a[..., 3] > 0; rgb = a[..., :3].astype(int)
H, W = al.shape
B = [(61, 42, 43), (84, 56, 52), (127, 85, 70), (172, 92, 74)]
bark = np.zeros(al.shape, bool)
for c in B: bark |= (rgb == c).all(-1) & al
lb, n = ndimage.label(bark, structure=np.ones((3, 3)))
sz = np.bincount(lb.ravel())
ed = []
for _ in range(3 if 'r1' not in J else 0):                                  # (a speck inside a speck: its neighbours fill in on the next pass)
    small = bark & (sz[lb] <= 6)
    for y, x in zip(*np.nonzero(small)):
        nb = [tuple(rgb[yy, xx]) for yy in range(max(0, y - 1), min(H, y + 2)) for xx in range(max(0, x - 1), min(W, x + 2))
              if al[yy, xx] and not bark[yy, xx]]
        if not nb: continue
        t = max(set(nb), key=nb.count)
        ed.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist(), 'to': list(map(int, t)), 'why': 'bark speck'})
        rgb[y, x] = t; bark[y, x] = False
if 'r1' not in J: J['r1'] = ed
# r1b: the one 2 px blotch asset_qa then reads (x 13, y 175-176, a near shade inside a strand) takes the colour most
# of its 4-neighbour ring has
if 'r1b' not in J:
    BL = [(13, 175), (13, 176)]
    ring = [(x + dx, y + dy) for x, y in BL for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) not in BL]
    cols = [tuple(rgb[y, x]) for x, y in ring if al[y, x]]
    t = max(set(cols), key=cols.count)
    J['r1b'] = [{'x': x, 'y': y, 'from': rgb[y, x].tolist(), 'to': list(map(int, t)), 'why': 'blotch'} for x, y in BL]
    for x, y in BL: rgb[y, x] = t
# r1c: the mid and light bark shades (127,85,70 / 172,92,74) in a bark patch under 100 px (not the trunk or one of
# the four big limbs, 150 px and over) are the strands' fringe clustered as bark: pink smears on the curtain at 5x.
# Each takes, pixel by pixel, the colour most of its opaque leaf 8-neighbours have, as r1.
if 'r1c' not in J:
    bark = np.zeros(al.shape, bool)
    for c in B: bark |= (rgb == c).all(-1) & al
    lb, n = ndimage.label(bark, structure=np.ones((3, 3)))
    sz = np.bincount(lb.ravel())
    mid = (((rgb == B[2]).all(-1)) | ((rgb == B[3]).all(-1))) & bark & (sz[lb] < 100)
    ec = []
    for _ in range(4):
        for y, x in zip(*np.nonzero(mid)):
            nb = [tuple(rgb[yy, xx]) for yy in range(max(0, y - 1), min(H, y + 2)) for xx in range(max(0, x - 1), min(W, x + 2))
                  if al[yy, xx] and not bark[yy, xx]]
            if not nb: continue
            t = max(set(nb), key=nb.count)
            ec.append({'x': int(x), 'y': int(y), 'from': rgb[y, x].tolist(), 'to': list(map(int, t)), 'why': 'fringe as bark'})
            rgb[y, x] = t; bark[y, x] = False; mid[y, x] = False
    J['r1c'] = ec
# r1d: the two blotches asset_qa reads after r1c (file x,y from its json), each to its 4-neighbour ring's majority
if 'r1d' not in J:
    G = [[(331, 362), (331, 363), (332, 363), (331, 364)],
         [(471, 276), (472, 276), (470, 277), (471, 277), (472, 277), (473, 277), (470, 278), (471, 278), (472, 278), (473, 278),
          (470, 279), (471, 279), (472, 279), (473, 279), (471, 280), (472, 280), (473, 280), (471, 281), (472, 281), (473, 281),
          (472, 282), (473, 282), (473, 283)]]
    J['r1d'] = []
    for BL in G:
        ring = [(x + dx, y + dy) for x, y in BL for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if (x + dx, y + dy) not in BL and 0 <= x + dx < W and 0 <= y + dy < H]
        cols = [tuple(rgb[y, x]) for x, y in ring if al[y, x]]
        t = max(set(cols), key=cols.count)
        J['r1d'] += [{'x': x, 'y': y, 'from': rgb[y, x].tolist(), 'to': list(map(int, t)), 'why': 'blotch'} for x, y in BL]
        for x, y in BL: rgb[y, x] = t
out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8); out[~al] = 0
json.dump(J, open('art/source/cp_willow/edits.json', 'w'), indent=0)
aseprite_io.write('art/source/cp_willow/cp_willow.aseprite', [out], layer='cp_willow')
Image.fromarray(out, 'RGBA').save(P)
print('cp_willow r1:', len(J['r1']), 'bark specks, r1b:', len(J['r1b']), 'blotch pixels, r1c:', len(J['r1c']), 'fringe pixels; colours', len(np.unique(out[al][:, :3], axis=0)))
