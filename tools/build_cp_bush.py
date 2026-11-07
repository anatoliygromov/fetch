#!/usr/bin/env python3
"""build_cp_bush.py [--check]: City Park's front bush (park_bush.png, 75 x 34, front layer), built by rule, 0 credits
(day/07nov-cpplay, owner 7 Nov board: "park_bush_06n: redraw").

  python3 -I tools/build_cp_bush.py           -> riverwalk/art/scene/park_bush.png, art/source/park_bush/
  python3 -I tools/build_cp_bush.py --check   -> exit 1 if the file differs from what this script builds

Where it shows: the two front props of the City Parks (citypark_tall x 620 and 1900, y 365; scene.lua
Sc.drawPropArt, `T.bush`), centred on the prop, top at y 365, scrolled 1.4x; only its top 19 rows are on the screen
(the screen's bottom edge), on the dark earth band, never near Pepper (her feet are at 328 or higher).

Was (6 Nov): a painted lump re-shaded by fix_cp_bush.py and fix_cp_audit.py on its old silhouette: twigs and spikes
sticking up, one flat mass, a rim of orange dots that read as specks. Round 1 (7 Nov): seven lobed clumps; the
independent review failed it: two equal pointed crowns (two hills), a comb of 1 px notches along the top, dotted
inner lines (measured as dither), and a rim in the earth band's own colour (invisible, only jagged).
Round 2 (now), in the front layer's row of the ladder (dark silhouette, median luma 40 or less, max contrast 40,
3-8 colours, a thin back-lit rim on top):
  CLUMP   one clump per size, drawn once by rule: a flat top run (no 1 px apex) and round shoulders of radius r,
          so the edge is continuous runs, no teeth
  STAMP   four clumps of different sizes and heights, back to front (the tallest centre-left, a smaller one right,
          the lowest left, a low one far right); each fills down to the bottom row and lays its back-lit top band
          (3 rows of the fg mid, solid) over the clumps behind, so a clump's edge over another is a solid band,
          never a dotted line
  RIM     the silhouette's top pixel in each column, one warm brown (6b4a3a), continuous runs: it differs from the
          earth band behind (the fg rim 594257 is that band's colour)
No outline (decoration). 3 colours, no dither."""
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


DARK = hx('1d1525')        # look.lua City Park fg dark: the mass
LIT = hx('2b1f33')         # look.lua City Park fg mid: each clump's back-lit top band (a solid band, 3 rows)
RIM = hx('6b4a3a')         # (round 2) a warm rim, continuous runs on the silhouette's top: the band's fg rim (594257)
                           # was the earth band's own colour behind it, so it read as a jagged edge, not as light
BAND = 3


def clump(w, r):
    """a leaf clump w px wide: a flat top (no 1 px apex) and round shoulders of radius r; returns, per column, how
    far its top drops below the clump's top row. Drawn once per size and stamped"""
    drop = []
    for x in range(w):
        e = min(x, w - 1 - x)
        d = r - (r * r - (r - e - 0.5) ** 2) ** 0.5 if e < r else 0.0
        drop.append(int(round(d)))
    return drop


# (round 2) four clumps of different sizes and heights, back to front: the tallest centre-left, a smaller one
# right, the lowest left, a low one far right. (clump, left x, top row)
BIG, MIDC, SMALL, LOW = clump(32, 11), clump(24, 9), clump(22, 9), clump(18, 8)
LAYOUT = [(MIDC, 40, 7), (BIG, 15, 2), (SMALL, 0, 11), (LOW, 57, 13)]


def build():
    a = np.zeros((H, W, 4), np.uint8)
    for drop, x0, top in LAYOUT:                          # stamped back to front: each clump over the ones behind
        for i, d in enumerate(drop):
            x = x0 + i
            if not 0 <= x < W: continue
            y0 = top + d
            a[y0:, x] = DARK
            a[y0:min(H, y0 + BAND), x] = LIT              # its back-lit top band, over whatever is behind
    al = a[..., 3] > 0
    for x in range(W):                                    # the rim: the silhouette's top pixel in every column
        ys = np.nonzero(al[:, x])[0]
        if len(ys): a[ys[0], x] = RIM
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
