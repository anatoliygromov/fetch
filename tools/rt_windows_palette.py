#!/usr/bin/env python3
"""rt_windows_palette.py DIR: crispness pass for the Rooftops pilot (8 Nov; owner 10:38: window lines "a little flaky").
1. Windows: every window on a storey is the same window, pixel for pixel (crispness bar). The cleanest window of each
   storey (fully visible in the concept) is stamped onto the others in place; window positions stay as the concept has
   them. The lower storey's window in the deep shadow is left as it is.
2. Palette: ramps instead of near-duplicates. Colours are clustered in Lab (k-means, 64), then merged while two
   colours are closer than dE 3.5, and every pixel snaps to the nearest kept colour (no dithering).
3. Lone pixels: a pixel unlike all 8 neighbours, whose neighbours agree on one colour within dE 12, takes that colour.
Writes final.png and prints the counts. Fidelity numbers against the concept: tools/concept_score-style dE."""
import sys, numpy as np, cv2
from PIL import Image
D = sys.argv[1]
im = np.asarray(Image.open(f'{D}/filled.png').convert('RGB')).copy()
holes = np.load(f'{D}/holes.npy')
H, W, _ = im.shape
STOREYS = [  # (template left x, rows y0..y1 inclusive, width, the other windows' left x)
    (205, 112, 135, 22, [-9, 34, 77, 120, 163, 248, 291]),     # upper storey, above the ledge line
    (111, 198, 231, 24, [56]),                                 # lower storey (x 2 is in deep shadow: kept)
    (221, 205, 239, 25, [172, 264, 307]),                      # the hotel's tall windows
]
stamped = 0; skipped = []
lum = im.astype(float) @ np.array([.299, .587, .114])
def wall_luma(x, y0, y1, w):                              # the wall just left and right of a window (2 px each side)
    cols = [c for c in (x - 3, x - 2, x + w + 1, x + w + 2) if 0 <= c < W]
    return np.median(lum[y0:y1 + 1, cols]) if cols else None
for tx, y0, y1, w, others in STOREYS:
    tpl = im[y0:y1 + 1, tx:tx + w].copy(); ref = wall_luma(tx, y0, y1, w)
    for ox in others:
        wl = wall_luma(ox, y0, y1, w)
        if wl is not None and ref is not None and wl < ref - 18:   # (review fix) a cast shadow over this window: keep it
            skipped.append(ox); continue
        a, b = max(0, ox), min(W, ox + w)
        t = tpl[:, a - ox:b - ox]; cur = im[y0:y1 + 1, a:b]
        lt = t.astype(float) @ np.array([.299, .587, .114]); lc = cur.astype(float) @ np.array([.299, .587, .114])
        shade = (lc < lt * 0.85) & ~holes[y0:y1 + 1, a:b]  # (review fix) a cast shadow over a concept pixel: keep it
        im[y0:y1 + 1, a:b] = np.where(shade[..., None], cur, t); stamped += 1
# (review fix) the upper windows over the skylight dips get a sill: their frame's bottom row, a stone sill 1 px wider
# each side, its shade under it (colours from the window frame and the coping)
FRAME = im[124, 205 + 1].copy(); SILL = im[90, 160].copy(); SHADE = (im[100, 160].astype(int) * 0.82).astype(np.uint8)
for ox in [-9, 34, 77, 163, 205, 248]:
    for x in range(ox - 1, ox + 23):
        if 0 <= x < W and (x < 96 or 160 <= x < 256):
            if ox <= x < ox + 22: im[135, x] = FRAME
            im[136, x] = SILL; im[137, x] = SHADE
lab = cv2.cvtColor(im.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
Z = lab.reshape(-1, 3)
_, lbl, cen = cv2.kmeans(Z, 64, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2), 3, cv2.KMEANS_PP_CENTERS)
cnt = np.bincount(lbl.ravel(), minlength=64).astype(float)
cen = [c for c in cen]; cnt = list(cnt)
while True:
    best = None
    for i in range(len(cen)):
        for j in range(i + 1, len(cen)):
            d = np.linalg.norm(cen[i] - cen[j])
            if d < 3.5 and (best is None or d < best[0]): best = (d, i, j)
    if not best: break
    _, i, j = best
    cen[i] = (cen[i] * cnt[i] + cen[j] * cnt[j]) / (cnt[i] + cnt[j]); cnt[i] += cnt[j]; del cen[j]; del cnt[j]
C = np.array(cen, np.float32)
idx = np.argmin(((Z[:, None, :] - C[None]) ** 2).sum(2), 1).reshape(H, W)
rgb = (cv2.cvtColor(C[None], cv2.COLOR_LAB2RGB)[0] * 255).round().clip(0, 255).astype(np.uint8)
lone = 0
for _ in range(2):
    new = idx.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            nb = np.concatenate([idx[y - 1, x - 1:x + 2], idx[y, [x - 1, x + 1]], idx[y + 1, x - 1:x + 2]])
            if (nb != idx[y, x]).all():
                v, c = np.unique(nb, return_counts=True); m = v[c.argmax()]
                if c.max() >= 5 and np.linalg.norm(C[m] - C[idx[y, x]]) < 12: new[y, x] = m; lone += 1
    idx = new
out = rgb[idx]
Image.fromarray(out).save(f'{D}/final.png')
np.save(f'{D}/palette.npy', rgb)
print(f'windows stamped {stamped} (kept in shadow: {skipped}); palette {len(C)} colours (from 64, merged under dE 3.5); lone pixels fixed {lone}')
