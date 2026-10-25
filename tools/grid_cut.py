#!/usr/bin/env python3
"""grid_cut.py RENDER.png NAME [--pitch auto|P]: render -> 1x game sprite, never by averaging (docs/art_generation.md).

Normal use: NAME has a passed preflight (art/gen/prompts/NAME.job.json); the render must be exactly frame x k, and
each k x k cell gives ONE colour: the majority of the cell's inner pixels, else its centre pixel. --pitch samples an
older render on its own detected grid (any pitch, one colour per cell, same rule).
Then: magenta keyed, Pepper and anything outside the subject dropped, compared with the blockout mask (size, drawn on
the blockout, blockout covered, stray scenery), colours mapped to the layer cap (palette map, no resampling).
Writes art/gen/out/NAME.png (+ _4x) and art/gen/out/NAME.cut.json. Exit 1 on FAIL."""
import sys, json, os
import numpy as np
from PIL import Image

R = json.load(open('art/gen/rules.json'))
src, name = sys.argv[1], sys.argv[2]
pitch_arg = sys.argv[sys.argv.index('--pitch') + 1] if '--pitch' in sys.argv else None
os.makedirs('art/gen/out', exist_ok=True)
J = json.load(open(f'art/gen/jobs/{name}.json'))
lay = R['layers'][J['layer']]
mask = np.array(Image.open(f'art/gen/blockouts/{name}_mask.png')) > 0
bo = np.array(Image.open(f'art/gen/blockouts/{name}.png').convert('RGB')).astype(int)
FH, FW = mask.shape
a = np.array(Image.open(src).convert('RGB')).astype(int)
H, W = a.shape[:2]
fails = []


def phase(g, p, n):
    best, bo_ = -1, 0
    for o in np.arange(0, p, max(p / 16, 0.5)):
        s = sum(g[int(round(o + i * p)) - 1] for i in range(1, n) if 0 < int(round(o + i * p)) - 1 < len(g))
        if s > best: best, bo_ = s, o
    return bo_


if pitch_arg is None:
    job = json.load(open(f'art/gen/prompts/{name}.job.json')); k = job['k']
    if (W, H) != (FW * k, FH * k):
        fails.append(f'render {W}x{H} is not the planned {FW * k}x{FH * k} grid'); px = py = W / FW
    px = py = float(k); ox = oy = 0.0
else:
    px = W / FW if pitch_arg == 'auto' else float(pitch_arg); py = H / FH if pitch_arg == 'auto' else float(pitch_arg)
    gx = np.abs(np.diff(a.sum(2), axis=1)).sum(0); gy = np.abs(np.diff(a.sum(2), axis=0)).sum(1)
    ox, oy = phase(gx, px, FW), phase(gy, py, FH)
out = np.zeros((FH, FW, 3), np.uint8); clean = 0
for j in range(FH):
    y0, y1 = int(round(oy + j * py)), int(round(oy + (j + 1) * py))
    for i in range(FW):
        x0, x1 = int(round(ox + i * px)), int(round(ox + (i + 1) * px))
        if y1 > H or x1 > W: out[j, i] = (255, 0, 255); continue
        iy, ix = max(1, (y1 - y0) // 4), max(1, (x1 - x0) // 4)
        cell = a[y0 + iy:y1 - iy, x0 + ix:x1 - ix].reshape(-1, 3)
        q = (cell // 6) * 6
        v, c = np.unique(q, axis=0, return_counts=True)
        if c.max() * 2 > len(cell):
            clean += 1; sel = (q == v[c.argmax()]).all(1); out[j, i] = cell[sel][0]
        else:
            out[j, i] = a[(y0 + y1) // 2, (x0 + x1) // 2]
gridq = clean / (FW * FH)
r, g, b = (out[..., i].astype(int) for i in range(3))
key = (r - g > 35) & (b - g > 35) & (r > 120) & (b > 120)
fg = ~key
# Pepper's place in the blockout: non-magenta pixels there that are not the subject
br, bg_, bb = bo[..., 0], bo[..., 1], bo[..., 2]
pep = ~((br > 250) & (bg_ < 5) & (bb > 250)) & ~mask
def grow(m, n):
    m = m.copy()
    for _ in range(n):
        m[1:] |= m[:-1]; m[:-1] |= m[1:]; m[:, 1:] |= m[:, :-1]; m[:, :-1] |= m[:, 1:]
    return m
near = grow(mask, 4)
sub = fg & near & ~grow(pep, 1)
leak = (fg & ~near & ~grow(pep, 3)).sum() / max(1, (~near).sum())
prec = (sub & grow(mask, 2)).sum() / max(1, sub.sum())
rec = (mask & grow(sub, 2)).sum() / max(1, mask.sum())
ys, xs = np.nonzero(sub); sw, sh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
tw, th = J['target_px']
ew, eh = (sw - tw) / tw, (sh - th) / th
if gridq < 0.7: fails.append(f'only {gridq:.0%} of cells have one clear colour: the render is off its grid')
if abs(ew) > 0.08 or abs(eh) > 0.08: fails.append(f'size {sw}x{sh} vs {tw}x{th}')
if prec < 0.85: fails.append(f'only {prec:.0%} of the drawing lands on the blockout')
if rec < 0.80: fails.append(f'only {rec:.0%} of the blockout is drawn')
if leak > 0.03: fails.append(f'{leak:.1%} stray scenery')
rgba = np.dstack([out, np.where(sub, 255, 0).astype(np.uint8)])
im = Image.fromarray(rgba, 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
cols = len(np.unique(np.array(im)[np.array(im)[..., 3] > 0][:, :3], axis=0))
if cols > lay['colours']:
    al = np.array(im)[..., 3]
    q = im.convert('RGB').quantize(lay['colours'], method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE).convert('RGB')
    im = Image.fromarray(np.dstack([np.array(q), al]), 'RGBA')
im.save(f'art/gen/out/{name}.png'); im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(f'art/gen/out/{name}_4x.png')
res = dict(name=name, size=[int(sw), int(sh)], target=[tw, th], grid_clean=round(gridq, 3), on_blockout=round(prec, 3),
           covered=round(rec, 3), stray=round(leak, 4), colours_in=int(cols), colours_cap=lay['colours'], fails=fails)
json.dump(res, open(f'art/gen/out/{name}.cut.json', 'w'), indent=1)
print(f"{'CUT PASS' if not fails else 'CUT FAIL'} {name}: {sw}x{sh} vs {tw}x{th} ({ew:+.0%}/{eh:+.0%}), grid {gridq:.0%} clean, "
      f"{prec:.0%} on blockout, {rec:.0%} covered, stray {leak:.1%}, {cols} -> {min(cols, lay['colours'])} colours")
for f in fails: print('  -', f)
sys.exit(1 if fails else 0)
