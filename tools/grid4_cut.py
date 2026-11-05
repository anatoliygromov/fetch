#!/usr/bin/env python3
"""grid4_cut.py RAW OUT [--pitch 4]: a GPT 2.5 render (2048 px, the blockout's 512 grid at 4 image px per art px) to
1x on its own grid (5 Nov). The phase is the offset with the least colour spread inside cells; each cell takes ONE
colour: the majority of its pixels when one colour holds over half of them (after a 4-bit snap used only to count),
else its centre pixel. Never an average. Prints the cell cleanliness (share of cells with a clear majority)."""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
P = int(sys.argv[sys.argv.index('--pitch') + 1]) if '--pitch' in sys.argv else 4
a = np.array(Image.open(src).convert('RGB')).astype(int)
H, W = a.shape[:2]
best = None
for oy in range(P):
    for ox in range(P):
        n = (H - oy) // P; m = (W - ox) // P
        c = a[oy:oy + n * P, ox:ox + m * P].reshape(n, P, m, P, 3)
        sd = c.std(axis=(1, 3)).mean()
        if best is None or sd < best[0]: best = (sd, ox, oy)
_, ox, oy = best
n = (H - oy) // P; m = (W - ox) // P
c = a[oy:oy + n * P, ox:ox + m * P].reshape(n, P, m, P, 3).transpose(0, 2, 1, 3, 4).reshape(n, m, P * P, 3)
q = c >> 4
key = (q[..., 0] << 8) | (q[..., 1] << 4) | q[..., 2]
res = np.zeros((n, m, 3), np.uint8); clean = 0
for i in range(n):
    for j in range(m):
        vals, cnt = np.unique(key[i, j], return_counts=True)
        k = cnt.argmax()
        if cnt[k] > P * P / 2:
            sel = key[i, j] == vals[k]; px = c[i, j][sel]
            res[i, j] = px[len(px) // 2]; clean += 1          # a real pixel of the majority, not their average
        else:
            res[i, j] = c[i, j][(P // 2) * P + P // 2]
Image.fromarray(res).save(out)
print(out, f'{m}x{n}', 'phase', (ox, oy), f'clean cells {clean / (n * m):.0%}')
