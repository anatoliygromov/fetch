#!/usr/bin/env python3
"""lockfill.py DIR: lock and complete, the free version (8 Nov, owner: "lock and complete").
DIR holds cut.png (the concept cut 1:1 onto the 320x240 game grid, tools/concept_cut.py), holes.npy (what game sprites
cover in the concept: Pepper, goose, bones, the concept's tile piles) and far.npy (the far layer: sky, spire, far town).
Every hole is filled by copying from the concept itself: for each hole piece the shift or mirror of the concept whose
surroundings match best (the next window along, the other end of a skylight, the stone course beside it), searched
only inside the same layer band. Nothing outside the holes changes (checked: LOCK OK). Writes filled.png and the
layers far.png (complete down to the deepest skyline + 24, for parallax), back.png, terrain.png (RGBA), fill_map.png."""
import sys, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as nd
D = sys.argv[1]
cut = np.asarray(Image.open(f'{D}/cut.png').convert('RGB')).astype(np.uint8)
holes = np.load(f'{D}/holes.npy'); far = np.load(f'{D}/far.npy')
H, W = holes.shape
LEDGE_Y = 136                                             # Pepper's line: the ledge tops (world y 376 at camera y 240)
band = np.where(far, 0, np.where(np.arange(H)[:, None] < LEDGE_Y, 1, 2)).astype(np.int8)
lab = cv2.cvtColor(cut.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
out = cut.copy(); known = ~holes.copy(); orig = ~holes.copy(); src_map = np.zeros((H, W, 3), np.uint8)

PERIOD = [int(v) for v in os.environ.get('LF_PERIOD', '').split(',') if v]   # (8 Nov) the window row's spacing, tried first

def candidates(b):
    if b == 1 and PERIOD:
        for k in (1, -1, 2, -2, 3, -3):
            for p in PERIOD: yield ('shift', k * p, 0)
    for dy in (0, -1, 1, -2, 2):
        for dx in range(-240, 241):
            if abs(dx) >= 6: yield ('shift', dx, dy)
    for c in range(-40, 2 * W + 40):
        yield ('mirror', c, 0)

def mapping(kind, a, dy, ys, xs):
    return (ys + dy, xs + a) if kind == 'shift' else (ys + dy, a - xs)

pieces = []
for b in (0, 1, 2):
    lb, n = nd.label(holes & (band == b))
    for i in range(1, n + 1): pieces.append((b, lb == i))
pieces.sort(key=lambda t: t[1].sum())
report = []
PLAIN = float(os.environ.get('LF_PLAIN', '6'))
for b, hp in pieces:
    ring = nd.binary_dilation(hp, iterations=4) & ~hp & orig & (band == b)
    ry, rx = np.nonzero(ring); rl = lab[ry, rx]
    if len(rl) and np.linalg.norm(rl - np.median(rl, 0), axis=1).mean() < PLAIN:   # bare wall or sky: continue each row
        hy, hx = np.nonzero(hp)
        for y, x in zip(hy, hx):
            row = np.nonzero(orig[y] & (band[y] == b))[0]
            j = row[np.argmin(np.abs(row - x))]; out[y, x] = cut[y, j]
        report.append(f'band {b} {hp.sum():4d} px  plain: row continuation'); src_map[hp] = (0, 120, 255); known |= hp; continue
    left = hp.copy(); steps = []
    while left.any():
        hy, hx = np.nonzero(left); best = None
        for kind, a, dy in candidates(b):
            sy, sx = mapping(kind, a, dy, hy, hx)
            inb = (sy >= 0) & (sx >= 0) & (sy < H) & (sx < W)
            ok = np.zeros(len(hy), bool); ok[inb] = orig[sy[inb], sx[inb]] & (band[sy[inb], sx[inb]] == b)
            cov = ok.mean()
            if cov < 0.25: continue
            qy, qx = mapping(kind, a, dy, ry, rx)
            q = (qy >= 0) & (qx >= 0) & (qy < H) & (qx < W)
            q[q] = orig[qy[q], qx[q]]
            if q.mean() < 0.6: continue
            d = np.linalg.norm(lab[ry[q], rx[q]] - lab[qy[q], qx[q]], axis=1).mean()
            score = d + 6 * (1 - cov)
            if best is None or score < best[0]: best = (score, d, cov, kind, a, dy, ok, sy, sx)
        if best is None:
            for y, x in zip(hy, hx):
                row = np.nonzero(orig[y] & (band[y] == b))[0]
                j = row[np.argmin(np.abs(row - x))]; out[y, x] = cut[y, j]
            src_map[left] = (255, 0, 0); steps.append('row fallback'); break
        score, d, cov, kind, a, dy, ok, sy, sx = best
        out[hy[ok], hx[ok]] = cut[sy[ok], sx[ok]]
        src_map[hy[ok], hx[ok]] = (0, 200, 0) if d < 4 else (240, 200, 0)
        left[hy[ok], hx[ok]] = False
        steps.append(f'{kind} {a:+d},{dy:+d} {cov*100:.0f}% dE {d:.1f}')
    known |= hp
    report.append(f'band {b} {hp.sum():4d} px  ' + ' | '.join(steps))
assert (out[~holes] == cut[~holes]).all(); print('LOCK OK: 0 changed pixels outside the holes')
print('\n'.join(report))
Image.fromarray(out).save(f'{D}/filled.png')
vis = out.copy(); vis[holes] = (vis[holes] * 0.4 + src_map[holes] * 0.6).astype(np.uint8)
Image.fromarray(vis).resize((W * 3, H * 3), Image.NEAREST).save(f'{D}/fill_map.png')
# layers
sky_line = np.array([np.nonzero(~far[:, x])[0].min() if (~far[:, x]).any() else H for x in range(W)])
deep = min(H, sky_line.max() + 24)
fl = np.zeros((deep, W, 4), np.uint8); fl[..., 3] = 255
for x in range(W):
    s = sky_line[x]; fl[:s, x, :3] = out[:s, x]; fl[s:, x, :3] = out[max(0, s - 1), x]   # far wall/sky runs on down
back = np.zeros((H, W, 4), np.uint8); back[..., :3] = out; back[..., 3] = np.where(band == 1, 255, 0)
terr = np.zeros((H, W, 4), np.uint8); terr[..., :3] = out; terr[..., 3] = np.where(band == 2, 255, 0)
Image.fromarray(fl).save(f'{D}/far.png'); Image.fromarray(back).save(f'{D}/back.png'); Image.fromarray(terr).save(f'{D}/terrain.png')
print(f'layers: far 320x{deep}, back and terrain 320x240 (RGBA)')
