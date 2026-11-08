#!/usr/bin/env python3
"""defect_map.py PIECE.png [--bg COLOURS.png] OUT.png: find the defect kinds the owner has pointed at (8 Nov), on a
piece cut from a concept, and draw them numbered on a 16x view with a pixel grid. Kinds:
  A leftover background: pixels in the colours of what was AROUND the piece (wall, sky, roof), on its outer edge
  B mixed line: a straight line (frame, bar, edge band) made of two near-identical shades (dE 3-14) mixed together
  C speck or dash: a cluster of 1-6 px of a colour unlike the flat area around it
  D clipped: the piece's outline is a straight cut through its colours (no edge shade), 3 rows or more
  E streak: 4 or more identical rows in a row (a part completed by repeating one row)
  F unequal: repeated parts that should match (panes, pots) differ in size
Each finding is numbered; the list is printed. Nothing is changed."""
import sys, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
P, OUT = sys.argv[1], sys.argv[-1]
BG = sys.argv[sys.argv.index('--bg') + 1] if '--bg' in sys.argv else None
im = np.asarray(Image.open(P).convert('RGBA')).astype(int); H, W = im.shape[:2]
rgb, on = im[..., :3], im[..., 3] > 0
lab = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
lum = rgb @ np.array([.299, .587, .114])
found = []
def add(kind, ys, xs, note):
    found.append({'kind': kind, 'x': int(np.mean(xs)), 'y': int(np.mean(ys)), 'px': [(int(a), int(b)) for a, b in zip(ys, xs)], 'note': note})
# A
if BG:
    bgc = np.unique(np.asarray(Image.open(BG).convert('RGB')).reshape(-1, 3), axis=0).astype(np.float32)
    bgl = cv2.cvtColor(bgc[None] / 255, cv2.COLOR_RGB2LAB)[0]
    d = np.min(np.linalg.norm(lab[..., None, :] - bgl[None, None], axis=-1), axis=-1)
    edge = on & ~nd.binary_erosion(on, iterations=3)
    lb, n = nd.label(on & edge & (d < 4))
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lb == i)
        if len(ys) >= 1: add('A', ys, xs, f'{len(ys)} px in the colours of what was around the piece')
# B: along rows and columns, runs of 2 shades closer than dE 14 alternating
for axis in (0, 1):
    L = lab if axis == 0 else lab.transpose(1, 0, 2); O = on if axis == 0 else on.T
    for i in range(L.shape[0]):
        row, ok = L[i], O[i]
        j = 0
        while j < len(row) - 1:
            if not ok[j]: j += 1; continue
            k = j
            while k + 1 < len(row) and ok[k + 1] and np.linalg.norm(row[k + 1] - row[j]) < 14: k += 1
            if k - j >= 5:
                seg = row[j:k + 1]; ref = seg[0]
                diff = [m for m in range(len(seg)) if 3 < np.linalg.norm(seg[m] - ref) < 14]
                same = len(seg) - len(diff)
                if diff and same and min(len(diff), same) >= 2 and min(len(diff), same) / len(seg) > 0.15:
                    idx = np.arange(j, k + 1)[diff]
                    ys, xs = (np.full(len(idx), i), idx) if axis == 0 else (idx, np.full(len(idx), i))
                    add('B', ys, xs, f'a {"row" if axis == 0 else "column"} line of {len(seg)} px mixes two near-identical shades')
            j = k + 1
# C: small same-colour clusters unlike their surroundings
keys = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
for v in np.unique(keys[on]):
    lb, n = nd.label((keys == v) & on)
    for i in range(1, n + 1):
        m = lb == i; s = m.sum()
        if s > 6: continue
        ring = nd.binary_dilation(m, iterations=2) & ~m & on
        if ring.sum() < 8: continue
        rl = lab[ring]; med = np.median(rl, 0)
        if np.mean(np.linalg.norm(rl - med, axis=1)) < 8 and np.linalg.norm(lab[m].mean(0) - med) > 12:
            ys, xs = np.nonzero(m); add('C', ys, xs, f'{s} px speck unlike the flat area around it')
# D: straight vertical cut through colour (outer column pixels that are not darker than their inner neighbour)
for side in (0, 1):
    run = []
    for y in range(H):
        xs = np.nonzero(on[y])[0]
        if not len(xs): run = []; continue
        x = xs[0] if side == 0 else xs[-1]; xi = x + 1 if side == 0 else x - 1
        flat = 0 <= xi < W and on[y, xi] and lum[y, x] >= lum[y, xi] - 4 and lum[y, x] > 60
        straight = run and abs(run[-1][1] - x) == 0
        if flat and (not run or straight): run.append((y, x))
        else:
            if len(run) >= 3: add('D', [r[0] for r in run], [r[1] for r in run], f'{len(run)} rows cut straight through, no edge shade ({"left" if side == 0 else "right"})')
            run = [(y, x)] if flat else []
    if len(run) >= 3: add('D', [r[0] for r in run], [r[1] for r in run], f'{len(run)} rows cut straight through')
# E: repeated identical rows
y = 0
while y < H - 1:
    k = y
    while k + 1 < H and (rgb[k + 1][on[k + 1]].shape == rgb[y][on[y]].shape) and np.array_equal(rgb[k + 1], rgb[y]) and on[y].any(): k += 1
    if k - y >= 3: add('E', [y, k], [W // 2, W // 2], f'{k - y + 1} identical rows (a streak)')
    y = k + 1
json.dump(found, open(OUT.rsplit('.', 1)[0] + '.json', 'w'))
# draw
K = 16; big = Image.new('RGBA', (W * K, H * K), (40, 44, 52, 255))
big.alpha_composite(Image.fromarray(im.astype(np.uint8)).resize((W * K, H * K), Image.NEAREST))
dr = ImageDraw.Draw(big)
for x in range(0, W * K, K): dr.line([(x, 0), (x, H * K)], fill=(0, 0, 0, 50))
for yy in range(0, H * K, K): dr.line([(0, yy), (W * K, yy)], fill=(0, 0, 0, 50))
COL = {'A': (0, 220, 255), 'B': (255, 210, 0), 'C': (255, 0, 200), 'D': (255, 90, 40), 'E': (120, 255, 120), 'F': (255, 255, 255)}
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
for n, f in enumerate(found, 1):
    for (yy, xx) in f['px']: dr.rectangle([xx * K + 2, yy * K + 2, xx * K + K - 3, yy * K + K - 3], outline=COL[f['kind']], width=2)
    tx, ty = f['x'] * K + K, f['y'] * K - 4
    dr.rectangle([tx - 2, ty - 2, tx + 34, ty + 20], fill=(0, 0, 0, 200)); dr.text((tx, ty), f"{f['kind']}{n}", font=F, fill=COL[f['kind']])
big.convert('RGB').save(OUT)
for n, f in enumerate(found, 1): print(f"{f['kind']}{n} at ({f['x']},{f['y']}): {f['note']}")
