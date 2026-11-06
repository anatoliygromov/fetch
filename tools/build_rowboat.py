#!/usr/bin/env python3
"""tools/build_rowboat.py: the River Walk rowing boat at true scale (owner, 6 Nov: "boat is still ridiculously small";
yes to the credits at 19:37). Writes
  riverwalk/art/scene/rowboat_hull.png   239 x 77, the boat (rows: 0 = the rower's head top, gunwale 40,
                                         waterline 61 when the boat floats at the game's line)
  riverwalk/art/scene/rowboat_rower.png  8 frames of 102 x 77 side by side, the man and the near oar rowing; drawn
                                         over the hull at x 44, y 0 (the game: setpieces.lua Sp.drawRowboat)

Sources (art/source/rw_rowboat/):
  still.png  round 2 (owner 6 Nov 19:53: round 1 "really low quality"): the render rw_rowboat_r2a (SpriteCook GPT 2.5
             Sunburst 2K, 60 credits), tools/cut_rowboat.py (grid4_cut, k-means 18 colours, cleanpass, outline);
             round 1 (NB 2.1 1K, render rw_rowboat_n6a) is kept in art/source/rw_rowboat/r1/
  hull.png, rower.png  from tools/split_rowboat.py (the man and the oar taken off the hull, the hull refilled)
  art/gen/renders/rw_rower_anim_sheet.webp  pixel-engine-v1.5 loop of rower.png cropped to x 44-145 (26 credits):
             8 frames of 102 x 102, the source at the bottom (rows 25-101 = rower rows 0-76)
In round 1 a loop of the whole boat (26 credits, art/gen/renders/rw_rowboat_anim_sheet.webp) redrew 52-72 % of the hull's
pixels in every frame, so it is not used: the hull stays the still and only the rower moves.
Each frame is snapped to the still's colours (nearest, no new colours), alpha made binary, specks under 3 px dropped,
only the biggest connected piece kept, then outline_complete.py --skip-bottom."""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art', 'source', 'rw_rowboat')
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
ANIM = os.path.join(ROOT, 'art', 'gen', 'renders', 'rw_rower_anim_sheet.webp')
N, FS, RW, RH = 8, 102, 102, 77

still = np.array(Image.open(os.path.join(SRC, 'still.png')).convert('RGBA'))
pal = np.unique(still[still[..., 3] > 0][:, :3], axis=0).astype(int)
hull = Image.open(os.path.join(SRC, 'hull.png')).convert('RGBA')
hull.save(os.path.join(OUT, 'rowboat_hull.png'))


def largest(a):
    """only the biggest 8-connected piece (the man, his hands and the oar): the loop kept copies of hull pixels that
    were left on the rower's source along the old oar, and they float loose in the frames where the oar has moved"""
    lab = np.zeros(a.shape, int); n = 0; sizes = {}; H, W = a.shape
    for y, x in zip(*np.nonzero(a)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n; c = 0
        while st:
            cy, cx = st.pop(); c += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and a[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; st.append((ny, nx))
        sizes[n] = c
    return lab == max(sizes, key=sizes.get) if sizes else a


def specks(a):
    out = a.copy(); seen = np.zeros_like(a); H, W = a.shape
    for y, x in zip(*np.nonzero(a)):
        if seen[y, x]: continue
        st, grp = [(y, x)], []; seen[y, x] = True
        while st:
            cy, cx = st.pop(); grp.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1), (cy + 1, cx + 1), (cy - 1, cx - 1), (cy + 1, cx - 1), (cy - 1, cx + 1)):
                if 0 <= ny < H and 0 <= nx < W and a[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; st.append((ny, nx))
        if len(grp) < 3:
            for p in grp: out[p] = False
    return out


sheet = np.array(Image.open(ANIM).convert('RGBA'))
frames = []
for i in range(N):
    f = sheet[FS - RH:FS, i * FS:i * FS + RW]
    a = largest(specks(f[..., 3] > 127))
    d = ((f[..., :3].astype(int)[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    q = np.zeros((RH, RW, 4), np.uint8); q[..., :3] = pal[d.argmin(-1)]; q[..., 3] = np.where(a, 255, 0)
    q[~a] = 0
    frames.append(q)
Image.fromarray(np.concatenate(frames, axis=1), 'RGBA').save(os.path.join(OUT, 'rowboat_rower.png'))
# the 1 px dark outline the play layer asks for (each frame's lowest row, the hips behind the gunwale, left open)
import subprocess, sys
subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'outline_complete.py'), os.path.join(OUT, 'rowboat_rower.png'),
                os.path.join(OUT, 'rowboat_rower.png'), '--skip-bottom', '--frames', f'{RW}x{RH}'], check=True)
print('wrote rowboat_hull.png', hull.size, 'and rowboat_rower.png', RW * N, 'x', RH, 'colours', len(pal))
