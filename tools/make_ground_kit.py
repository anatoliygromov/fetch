#!/usr/bin/env python3
"""make_ground_kit.py: the ground transition kit's drawn parts (day/07nov-ground, 0 credits).

The owner, 7 Nov: "whenever we see two different types of ground connecting, they look cut, including the hills
etc". The joins audit (docs/review/07nov/ground_joins/README.md) found 29 cut joins. The fix is one transition system:
a per-column ground kind map and a rule table (riverwalk/joins.lua) that stamps a transition at every change, from
pieces built by rule. The geometric pieces (stone steps as 8 px slope tiles, kerb returns, quay-end caps, the near
pond bank as a 2 px slope tile, contact shadows) are drawn by rule in scene.lua from each level's own palette; the
textured parts are drawn here once, on the 8 px grid where they repeat, in the level's palette, and stamped:

  kit_cp_midlawn.png   240 x 96   City Park's mid row stands on its own lawn (audit CP9: with the camera up in the
                                  trees the mid row ended straight over the sky). The ground art's lawn colour
                                  (#9e983f), a darker seam row on top where the row's trees stand, tufts (a lit pair over a dark
                                  pair) on an 8 px grid in four offset rows, tiling at 240 like park_ground.png. Faded as the mid
                                  layer in the game (scene.lua Sc.townArt), so it sits in the mid haze.
  kit_cp_tufts.png     240 x 5    a tuft row drawn over the mid row's feet (audit CP6: the bushes stood cut flat on
                                  the lawn's top line): 2 px clumps every 8 px on a dark foot row, transparent
                                  between; also faded as mid.
  kit_cp_roots.png     48 x 5     grass over a trunk's foot (audit CP8: root flares ended in a straight line): the
                                  path's lawn greens, stamped over each tree's foot in the back pass.

  python3 -I tools/make_ground_kit.py           write the parts
  python3 -I tools/make_ground_kit.py --check   fail if a part on disk differs from the build
"""
import os, sys
import numpy as np
from PIL import Image

OUT = 'riverwalk/art/scene'
hexc = lambda h: (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
LAWN, LAWN_D, LAWN_L, SEAM = hexc('9e983f'), hexc('867744'), hexc('b5ad55'), hexc('665c3b')   # park_ground.png's lawn


# (round 2, review CP-c / CP-n: "one 16 px pattern repeated: a battlement"; the lawn "a dot grid, not grass") one
# 48 px tuft pattern in no regular order: bumps 1 to 3 px wide and 1 to 3 px tall with gaps of 1 to 3 px, from a fixed
# list (so the build is the same every time); a 1 px wide bump is never 1 px tall (no lone pixels). It tiles at 48.
BUMPS = [(2, 1, 2), (1, 3, 1), (3, 2, 3), (2, 2, 1), (1, 2, 2), (3, 1, 1), (2, 3, 3), (1, 2, 2), (2, 1, 2), (3, 3, 2),
         (1, 3, 3), (2, 2, 3)]                                       # (width, height, gap after) - 48 px in all
assert sum(w + g for w, h, g in BUMPS) == 48


def tuft_row(W, colour_of):
    """the pattern's columns over width W: a list of (x, height); colour_of(k, h) gives the colour of row k (0 = foot)"""
    out = []
    x = 0
    while x < W:
        for w, h, g in BUMPS:
            for dx in range(w):
                if x + dx < W: out.append((x + dx, h))
            x += w + g
            if x >= W: break
    return out


def midlawn():
    W, H = 240, 96
    a = np.zeros((H, W, 4), np.uint8); a[:, :] = LAWN
    a[0, :] = SEAM                                                   # the seam under the row's feet
    a[1, :] = LAWN_D
    for row, off in ((7, 0), (19, 17), (37, 31)):                    # the tuft pattern in 3 rows, each shifted
        for x, h in tuft_row(W + 48, None):
            if h == 1: continue                                      # (on the open lawn only the 2-3 px tufts)
            xx = (x + off) % W
            for k in range(h): a[row - k, xx] = LAWN_D if k == 0 else LAWN_L
    return a


def tufts():
    W, H = 240, 5
    a = np.zeros((H, W, 4), np.uint8)
    a[H - 1, :] = LAWN_D                                             # a dark foot row, the bumps of the pattern on it
    for x, h in tuft_row(W, None):
        for k in range(1, h + 1): a[H - 1 - k, x] = LAWN
    return a


def roots():
    W, H = 48, 5
    a = np.zeros((H, W, 4), np.uint8)
    a[H - 1, :] = LAWN_D
    for x, h in tuft_row(W, None):
        for k in range(1, h + 1): a[H - 1 - k, x] = LAWN
    return a


PARTS = {'kit_cp_midlawn': midlawn, 'kit_cp_tufts': tufts, 'kit_cp_roots': roots}


def main():
    check = '--check' in sys.argv
    bad = 0
    for n, f in PARTS.items():
        a = f(); p = f'{OUT}/{n}.png'
        if check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
            print(n, 'OK' if ok else 'DIFFERS'); bad += not ok
        else:
            Image.fromarray(a, 'RGBA').save(p); print(n, a.shape[1], 'x', a.shape[0])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
