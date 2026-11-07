#!/usr/bin/env python3
"""build_cp_bush.py [--check]: City Park's front bush (park_bush.png, 75 x 34, front layer), built by rule, 0 credits
(day/07nov-cpplay, owner 7 Nov board: "park_bush_06n: redraw").

  python3 -I tools/build_cp_bush.py           -> riverwalk/art/scene/park_bush.png, art/source/park_bush/
  python3 -I tools/build_cp_bush.py --check   -> exit 1 if the file differs from what this script builds

Where it shows: the two front props of the City Parks (citypark_tall x 620 and 1900, y 365; scene.lua
Sc.drawPropArt, `T.bush`), centred on the prop, top at y 365, scrolled 1.4x; only its top 19 rows are on the screen
(the screen's bottom edge), on the dark earth band, never near Pepper (her feet are at 328 or higher).

Was (6 Nov): a painted lump re-shaded by fix_cp_bush.py and fix_cp_audit.py on its old silhouette: twigs and spikes
sticking up, one flat mass, a rim of orange dots that read as specks. Now a clean leafy mound in the front layer's
row of the ladder (dark silhouette, median luma 40 or less, max contrast 40, 3-8 colours, a thin back-lit rim on
top), made of a few big leaf clumps:
  CLUMP   one clump per size (R 11 and R 8), drawn once: a core disc and round leaf lobes (r 3.5) round its upper
          rim every 30 degrees, so the edge is scalloped by whole leaves, not by noise. Shaded once: the back-lit rim
          (look.lua City Park fg.rim) on its top edge, a crescent of the fg mid on its upper left, the fg dark inside.
  STAMP   the clumps stamped back to front on the integer grid below (the back row higher, the front row lower and
          overlapping, so each clump's lit edge separates it from the one behind); the base filled with the fg dark
          to the bottom row between the outer clumps. No outline (decoration): the silhouette is the edge.
The palette is the City Park foreground band's own (look.lua: fg dark 1d1525, mid 2b1f33, rim 594257), so the bush
belongs to the band it stands on. No warm rim pixels (they read as specks)."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, 'riverwalk/art/scene')
SRC = os.path.join(ROOT, 'art/source')
W, H = 75, 34


def hx(h): return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


DARK, RIM = hx('1d1525'), hx('594257')                         # look.lua City Park fg dark, rim
MID = hx('423045')        # a clump's edge over the clump behind: half way from fg mid (2b1f33) to the rim (asset_qa:
                          # the fg mid itself is too near the dark, its arcs flagged as blotches)
LOBE_R = 4


def clump(R):
    """a leaf clump of radius R: its mask on a (2R+1)^2 grid, centre (R, R): a core disc (R - 4) and round leaves
    (r 4) on a ring of R - 4, one every 45 degrees, so the edge is scalloped by whole leaves"""
    n = 2 * R + 1
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx - R, yy - R
    m = dx * dx + dy * dy <= (R - 5) ** 2
    for k in range(8):
        t = np.radians(k * 45 - 90)
        lx, ly = (R - LOBE_R) * np.cos(t), (R - LOBE_R) * np.sin(t)
        m |= (dx - lx) ** 2 + (dy - ly) ** 2 <= LOBE_R * LOBE_R + 0.5
    return m


BIG, SMALL = clump(11), clump(8)
# (clump, centre x, centre y), back to front: the back row higher, the outer clumps lowest (a round mound)
LAYOUT = [(SMALL, 8, 25), (SMALL, 66, 25), (BIG, 26, 14), (BIG, 48, 13),
          (SMALL, 15, 21), (SMALL, 59, 20), (BIG, 37, 19)]


def build():
    a = np.zeros((H, W, 4), np.uint8)
    sil = np.zeros((H, W), bool)
    front = np.zeros((H, W), int) - 1                     # which clump is in front at each pixel
    own = np.zeros((H, W), bool)                          # in that clump's own mask (not its fill to the base)
    for k, (m, cx, cy) in enumerate(LAYOUT):
        R = m.shape[0] // 2
        for j, i in zip(*np.nonzero(m)):
            y, x = cy - R + j, cx - R + i
            if 0 <= y < H and 0 <= x < W: sil[y, x] = True; front[y, x] = k; own[y, x] = True
        for i in range(m.shape[1]):                       # each clump fills down to the bottom row (the bush's base)
            col = np.nonzero(m[:, i])[0]
            x = cx - R + i
            if len(col) and 0 <= x < W:
                for y in range(cy - R + col.max() + 1, H):
                    if not sil[y, x]: sil[y, x] = True; front[y, x] = k; own[y, x] = False
    a[sil] = DARK
    masks = []                                            # each clump's own mask in the bush's grid
    for m, cx, cy in LAYOUT:
        R = m.shape[0] // 2
        mk = np.zeros((H + 2, W + 2), bool)
        for j, i in zip(*np.nonzero(m)):
            y, x = cy - R + j, cx - R + i
            if 0 <= y < H and 0 <= x < W: mk[y + 1, x + 1] = True
        masks.append((mk, cy))
    pad = np.pad(sil, 1)
    for y in range(H):
        for x in range(W):
            if not sil[y, x]: continue
            if not pad[y, x + 1]: a[y, x] = RIM; continue  # the silhouette's top edge: back-lit
            k = front[y, x]
            mk, cy = masks[k]
            if not own[y, x] or y > cy - 4: continue           # (the upper part only: lower down it reads as a crack)
            # a clump's upper edge where it lies over a clump behind it: its edge pixels (up, left or right
            # neighbour outside it) whose outside neighbour is a clump further back
            for j, i in ((-1, 0), (0, -1), (0, 1)):
                yy, xx = y + j, x + i
                if 0 <= yy < H and 0 <= xx < W and not mk[yy + 1, xx + 1] and sil[yy, xx] and front[yy, xx] < k:
                    a[y, x] = MID; break
    lone = []                                             # a MID pixel with no MID or RIM next to it is a dot: dark
    for y in range(H):
        for x in range(W):
            if tuple(a[y, x]) != MID: continue
            nb = [tuple(a[y + j, x + i]) for j in (-1, 0, 1) for i in (-1, 0, 1)
                  if (i or j) and 0 <= y + j < H and 0 <= x + i < W]
            if MID not in nb and RIM not in nb: lone.append((y, x))
    for y, x in lone: a[y, x] = DARK
    return a


def main():
    a = build()
    p = os.path.join(SCENE, 'park_bush.png')
    if '--check' in sys.argv:
        same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
        print(('OK   ' if same else 'DIFF ') + 'park_bush'); sys.exit(0 if same else 1)
    if '--out' in sys.argv:
        Image.fromarray(a, 'RGBA').save(sys.argv[sys.argv.index('--out') + 1]); return
    Image.fromarray(a, 'RGBA').save(p)
    d = os.path.join(SRC, 'park_bush'); os.makedirs(d, exist_ok=True)
    Image.fromarray(a, 'RGBA').save(os.path.join(d, 'park_bush.png'))
    aseprite_io.write(os.path.join(d, 'park_bush.aseprite'), [a], layer='park_bush')
    cols = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
    print(f'park_bush {W} x {H}, {cols} colours')


if __name__ == '__main__':
    main()
