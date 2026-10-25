"""tools/props_check.py: checks the title's rebuilt props (art/source/title/tools/props.py) in the built picture
riverwalk/art/title/base.png. Exit 1 on any failure.
  drawn      every pixel of every object is as specified, unless Pepper's layer covers it
  palette    every pixel of base.png's background is a colour the background had before (pre_props)
  L-corners  no 2x2 block holds 3 pixels of a 1 px line (masts, rigging, the lantern frame, the roof edges, legs)
  columns    the highlight and outline columns run unbroken wherever they are visible (lamp posts, railing posts,
             the bin's slats) and the bench's slat rows run unbroken to the screen edge"""
import os, sys
import numpy as np
from PIL import Image
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'art', 'source', 'title', 'tools'))
import props as P

base = np.array(Image.open(os.path.join(ROOT, 'riverwalk', 'art', 'title', 'base.png')).convert('RGB'))
bg = np.array(Image.open(os.path.join(P.SRC, 'bg_noplate_320.png')).convert('RGB'))
pre = np.array(Image.open(os.path.join(P.SRC, 'pre_props', 'bg_noplate_320.png')).convert('RGB'))
over = np.zeros(base.shape[:2], bool)
for f in ('pepper_region.png', 'logo_r4.png', 'tagline_region.png'):
    over |= np.array(Image.open(os.path.join(P.SRC, f)).convert('RGBA'))[..., 3] > 0
fails = []

# drawn: the object pixels in the background layer (keep pixels, Pepper's painted outline, are allowed to differ)
objs = {'left lamp': P.LEFT_TOP, 'right lamp': P.RIGHT, 'bench': P.BENCH, 'bin': P.BIN, 'posts': P.POSTS,
        'boats': P.BOATS}
for name, rows in objs.items():
    bad = 0; n = 0
    for y, x0, pat in rows:
        for i, ch in enumerate(pat):
            if ch == '.': continue
            x = x0 + i; n += 1
            if over[y, x] or int(pre[y, x].astype(int) @ [30, 59, 11]) // 100 < 12: continue   # Pepper's
            if tuple(bg[y, x]) != P.C[ch]: bad += 1
    print(f'drawn     {name:10s} {n} px, {bad} off spec'); bad and fails.append(name + ' off spec')

pal = set(map(tuple, pre.reshape(-1, 3).tolist()))
newc = set(map(tuple, bg.reshape(-1, 3).tolist())) - pal
print('palette   new colours in the background:', len(newc)); newc and fails.append('palette')


def lines(pts, name):
    s = set(pts); bad = []
    for x, y in s:
        for dx, dy in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
            blk = [(x + dx + i, y + dy + j) in s for i in (0, 1) for j in (0, 1)]
            if sum(blk) == 3: bad.append((x, y))
    print(f'L-corners {name:22s} {len(set(bad))}'); bad and fails.append('L ' + name)


def col(rows, ch):
    return [(x0 + i, y) for y, x0, pat in rows for i, c in enumerate(pat) if c == ch]


rig = [p for p in col(P.BOATS, 'w') if p[0] < 150]
lines([p for p in rig if p[0] <= 141], 'left boat rigging L')
lines([p for p in rig if p[0] >= 143], 'left boat rigging R')
lines([(142, y) for y in range(141, 157)], 'left boat mast')
lines(col(P.BOATS, 'g'), 'small boat, boat 256 masts')
frame = [(x, y) for y in range(57, 69) for x in (26 + (y - 57) // 4, 40 - (y - 57) // 4)]
lines(frame, 'lantern frame')
edges = []
for y, x0, pat in P.LEFT_TOP:
    if 48 <= y <= 55: edges += [(x0, y), (x0 + len(pat) - 1, y)]
lines(edges, 'left roof edges')
edges = []
for y, x0, pat in P.RIGHT:
    if 131 <= y <= 132: edges += [(x0, y), (x0 + len(pat) - 1, y)]
lines(edges, 'right roof edges')
lines([(x, y) for y, x0, pat in P.BENCH if y >= 203 for x in [x0] if x < 301], 'bench front leg (left px)')


def run(name, x, y0, y1, colour):
    seg = [base[y, x].tolist() == list(colour) or over[y, x] for y in range(y0, y1)]
    ok = all(seg)
    print(f'columns   {name:28s} {"unbroken" if ok else "BROKEN"}'); ok or fails.append(name)


run('left post highlight x34', 34, 80, 103, P.C['H'])
run('left post highlight low', 34, 155, 171, P.C['H'])
run('left post outline x31', 31, 80, 117, P.C['O'])
run('left post outline x35', 35, 80, 103, P.C['O'])
run('left base highlight x33', 33, 180, 187, P.C['H'])
run('right post highlight x287', 287, 138, 167, P.C['M'])
run('right post outline x286', 286, 137, 164, P.C['O'])
for x0 in (186, 215):
    run(f'railing post {x0} highlight', x0 + 4, 179, 203, P.C['M'])
    run(f'railing post {x0} outline L', x0, 178, 203, P.C['O'])
    run(f'railing post {x0} outline R', x0 + 5, 178, 203, P.C['O'])
run('bin lit slat x286', 286, 182, 204, P.C['M'])
run('bin lit slat x287', 287, 182, 204, P.C['M'])
for y, ch in ((184, 'L'), (189, 'H'), (194, 'M'), (198, 'L')):
    seg = all(base[y, x].tolist() == list(P.C[ch]) for x in range(300, 320))
    print(f'columns   bench row {y:<19d} {"unbroken" if seg else "BROKEN"}'); seg or fails.append(f'bench row {y}')

print('PROPS', 'ALL PASS' if not fails else 'FAIL: ' + ', '.join(fails))
sys.exit(1 if fails else 0)
