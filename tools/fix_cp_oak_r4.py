#!/usr/bin/env python3
"""fix_cp_oak_r4.py: hand rules on the oak's retry-2 cut (6 Nov 2026), after tools/polish_cp_trees.py cp_oak.
One rule, found at 5x and in the frames (sweep y 24, x 1600): the leaf highlight #fc9e1e (luma 172, about 185 on
screen) is lighter than the tree line's median (181) and near the far city (190). It takes the park lime's
highlight #f68a21 (luma 158, about 176 on screen), so the oak and the lime share their top shade. Every changed pixel
is added to art/source/cp_oak/edits.json under "r4"; the .aseprite source and the slot png are written again."""
import sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import aseprite_io

P = 'riverwalk/art/scene/cp_oak.png'
a = np.array(Image.open(P).convert('RGBA'))
J = json.load(open('art/source/cp_oak/edits.json'))
if 'r4d' in J: sys.exit('already applied')
RULES = [((252, 158, 30), (246, 138, 33), 'ladder: highlight to the lime\'s #f68a21')]
ed = []
for f, t, why in RULES:
    sel = (a[..., 3] > 0) & (a[..., :3] == f).all(-1)
    for y, x in zip(*np.nonzero(sel)):
        ed.append({'x': int(x), 'y': int(y), 'from': list(f), 'to': list(t), 'why': why})
    a[sel, :3] = t
if 'r4' not in J: J['r4'] = ed
# r4b: the five small highlight patches asset_qa then reads as blotches (now near the orange around them) join the
# colour most of their 4-neighbour ring has (file x,y boxes from docs/review/06nov/cp_oak/qa.json)
BL = [[(108, 0), (109, 0), (110, 0)], [(158, 22), (159, 22), (160, 22), (159, 23), (160, 23), (161, 23), (159, 24), (160, 24)],
      [(329, 169), (330, 169), (331, 169), (332, 169), (330, 170), (331, 170), (332, 170)],
      [(79, 206), (78, 207), (79, 207), (80, 207), (78, 208), (79, 208), (80, 208)], [(347, 289), (348, 289), (347, 290)]]
eb = []
for blob in BL:
    S = set(blob); ring = []
    for x, y in blob:
        for xx, yy in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (xx, yy) not in S and 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy, xx, 3]: ring.append(tuple(int(v) for v in a[yy, xx, :3]))
    t = max(set(ring), key=ring.count)
    for x, y in blob:
        eb.append({'x': x, 'y': y, 'from': a[y, x, :3].tolist(), 'to': list(t), 'why': 'blotch: joins its clump'}); a[y, x, :3] = t
if 'r4b' not in J: J['r4b'] = eb
# r4c: the bark at 5x beside the bench was mottled: four darks within 20 luma (50, 60, 66, 69) and leaf reds on the
# trunk. The two middle darks join #6c3628 (69) everywhere (bark only); on the trunk below the crown (from y 345
# down, the run that holds x 260) the leaf reds take the bark shade next to them in luma: #d43918 -> #9e4b21, #a83025 / #81302f / #7b3132 ->
# #6c3628. Bark ramp after: 50, 69, 95, lit 146.
ec = []
def trunk_mask():                       # each row from y 345 down: the opaque run that holds the trunk's centre (x 260)
    m = np.zeros(a.shape[:2], bool)
    for y in range(345, a.shape[0]):
        if not a[y, 260, 3]: continue
        x0 = 260; x1 = 260
        while x0 > 0 and a[y, x0 - 1, 3]: x0 -= 1
        while x1 < a.shape[1] - 1 and a[y, x1 + 1, 3]: x1 += 1
        m[y, x0:x1 + 1] = True
    return m
def swap(f, t, box=None, why=''):
    sel = (a[..., 3] > 0) & (a[..., :3] == f).all(-1)
    if box is not None: sel &= box
    for y, x in zip(*np.nonzero(sel)):
        ec.append({'x': int(x), 'y': int(y), 'from': list(f), 'to': list(t), 'why': why})
    a[sel, :3] = t
for f in ((89, 49, 43), (86, 59, 52)): swap(f, (108, 54, 40), None, 'bark: one dark shade')
TB = trunk_mask()
swap((212, 57, 24), (158, 75, 33), TB, 'trunk: leaf red to bark mid')
for f in ((168, 48, 37), (129, 48, 50), (123, 49, 50)): swap(f, (108, 54, 40), TB, 'trunk: leaf dark to bark dark')
if 'r4c' not in J: J['r4c'] = ec
# r4d: asset_qa's blotches after r4c (patches of 2-24 px that now sit in a near colour, mostly bark darks joined in
# r4c): each patch, grouped by 8-connectivity from docs/review/06nov/cp_oak/qa.json, takes its ring's majority colour
from scipy import ndimage
q = json.load(open('docs/review/06nov/cp_oak/qa.json'))[0]
pts = [p for c in q['checks'] if c['id'] == 'blotches' for p in c['pixels']]
mk = np.zeros(a.shape[:2], bool)
for x, y in pts: mk[y, x] = True
lb, nb = ndimage.label(mk, structure=np.ones((3, 3)))
ed4 = []
for i in range(1, nb + 1):
    comp = lb == i
    ring = ndimage.binary_dilation(comp) & ~comp & (a[..., 3] > 0)
    cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
    t = cols[cnt.argmax()]
    for y, x in zip(*np.nonzero(comp)):
        ed4.append({'x': int(x), 'y': int(y), 'from': a[y, x, :3].tolist(), 'to': t.tolist(), 'why': 'blotch: joins its fill'})
    a[comp, :3] = t
J['r4d'] = ed4
json.dump(J, open('art/source/cp_oak/edits.json', 'w'), indent=0)
aseprite_io.write('art/source/cp_oak/cp_oak.aseprite', [a], layer='cp_oak')
Image.fromarray(a, 'RGBA').save(P)
print('r4 edits', len(ed), 'r4c', len(ec), 'colours', len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)))
