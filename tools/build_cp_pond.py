#!/usr/bin/env python3
"""build_cp_pond.py [--check]: the City Park pond kit, built by rule, 0 credits (night 6 Nov 2026, cp track).

  python3 -I tools/build_cp_pond.py           -> riverwalk/art/scene/cp_reeds.png, cp_lily.png, cp_bankstones.png
                                                 and art/source/<name>/<name>.aseprite
  python3 -I tools/build_cp_pond.py --check   -> exit 1 if a file differs from what this script builds

The design target is the producer's concept art/gen/concepts/cp_pond_concept_a.png (reference only): reeds and
bulrushes at the pond's ends, rounded stones where the bank meets the water, lily pads on the surface. Each part is
drawn once here, on its own pixel grid, and scene.lua stamps it at whole-pixel spots (Sc.drawPondKit). Decoration on
Pepper's line: no outline, each edge a darker shade of its own colour, light from the upper left. True scale at 46 px
a metre: the reeds 0.7 m (a clump of common reed with two bulrush heads), a lily pad 0.2 m across.

Parts:
  cp_reeds       2 cells of 16 x 34: [0] a clump of 6 blades and 2 bulrush heads, [1] a smaller clump of 5 blades and
                 one head (drawn mirrored for variety by scene.lua); the clump's base row is the cell's last row
  cp_lily        3 cells of 10 x 4: two lily pads seen almost edge-on (a lit rim, the face, a shade row, the notch),
                 the third with a small white and pink flower
  cp_bankstones  2 cells of 12 x 7: two and one rounded granite stones (the pond bank's stone ramp), bottom row on
                 the shore"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, 'riverwalk/art/scene')
SRC = os.path.join(ROOT, 'art/source')


def hx(h): return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


# the park's own ramps: the lawn's olive greens (park_ground, BANK.lawn / lip), the reed's dry tan, the bulrush brown,
# the lily green, the bank's granite (scene.lua BANK.st1-3)
REED = {'lit': hx('b5ad55'), 'mid': hx('8f8a3c'), 'dk': hx('66612c'), 'dry': hx('c9a865'), 'dryd': hx('a3824a')}
RUSH = {'lit': hx('9c6238'), 'mid': hx('7a4a2a'), 'dk': hx('573520')}
LILY = {'lit': hx('8fbf5a'), 'mid': hx('5f9445'), 'dk': hx('3f6b35'), 'w': hx('f6efe6'), 'p': hx('e79ab0')}
STONE = {'lit': hx('c9c2b4'), 'ml': hx('b3ac9f'), 'mid': hx('a39b8e'), 'dk': hx('7a736a')}   # the stepping stones' ramp (round 1: 4 shades)


def canvas(w, h): return np.zeros((h, w, 4), np.uint8)


def put(a, x, y, c):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x] = c


def blade(a, bx, tx, ty, bend, col, wide=True):
    """a reed blade from its base (bx, last row) to its tip (tx, ty): one x per row on a smooth bend, 2 px wide in
    its lower half (lit left pixel, its colour right); the top quarter in the dry tan (an autumn reed's tip)"""
    H = a.shape[0]; base = H - 1; n = base - ty
    for k in range(n + 1):
        y = base - k; u = k / n
        x = int(round(bx + (tx - bx) * u + bend * 4 * u * (1 - u)))
        c = col if u < 0.72 else (REED['dry'] if col != REED['dk'] else REED['dryd'])
        if wide and u < 0.5:
            put(a, x, y, REED['lit'] if col != REED['dk'] else REED['mid']); put(a, x + 1, y, col)
        else:
            put(a, x, y, c)


def rush(a, x, top, base):
    """a bulrush: its stalk (1 px, mid green) from the base up to the head, a head 3 x 8 (lit left column, its brown,
    a dark right column, rounded ends) and a 1 px spike over it"""
    for y in range(top + 9, base + 1): put(a, x, y, REED['mid'])
    for y in range(top + 1, top + 9):
        if y in (top + 1, top + 8):                                 # the rounded ends: the middle column only
            put(a, x, y, RUSH['lit'] if y == top + 1 else RUSH['dk'])
        else:
            put(a, x - 1, y, RUSH['lit']); put(a, x, y, RUSH['mid']); put(a, x + 1, y, RUSH['dk'])
    put(a, x, top, REED['dryd'])


def reeds():
    W, H = 16, 34
    A = canvas(W, H); B = canvas(W, H)
    for bx, tx, ty, bend, col in ((5, 1, 6, -2, REED['mid']), (7, 6, 1, 1, REED['dk']), (8, 12, 4, 2, REED['mid']),
                                  (6, 3, 12, -1, REED['dk']), (9, 14, 13, 1, REED['mid']), (10, 11, 9, 0, REED['dk'])):
        blade(A, bx, tx, ty, bend, col)
    rush(A, 4, 2, 30); rush(A, 11, 7, 30)
    for bx, tx, ty, bend, col in ((6, 3, 14, -1, REED['mid']), (7, 8, 10, 1, REED['dk']), (8, 12, 15, 1, REED['mid']),
                                  (9, 13, 20, 0, REED['dk']), (6, 2, 21, 0, REED['dk'])):
        blade(B, bx, tx, ty, bend, col)
    rush(B, 10, 12, 30)
    for a in (A, B):                                                # where blades cross, a closed gap of a few px is the
        from scipy import ndimage                                   # clump's shade between them (no pinholes)
        op = a[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op
        lb, n = ndimage.label(holes)
        for i in range(1, n + 1):
            if (lb == i).sum() <= 6: a[lb == i] = REED['dk']
    return np.concatenate([A, B], 1), (W, H)


def lily():
    W, H = 10, 4
    cells = []
    for k in range(3):
        a = canvas(W, H)
        w = 9 if k != 1 else 7
        x0 = (W - w) // 2
        for x in range(x0, x0 + w):
            e = x in (x0, x0 + w - 1)
            if not e: put(a, x, 1, LILY['lit'])                     # the lit rim
            put(a, x, 2, LILY['mid'])                               # the face
            if not e: put(a, x, 3, LILY['dk'])                      # its shade on the water
        nx = x0 + w // 2 + 1                                        # the notch, a cut to the middle
        put(a, nx, 1, (0, 0, 0, 0)); put(a, nx, 2, LILY['dk'])
        if k == 2:                                                  # a small water lily on the third pad
            for x, y, c in ((3, 0, LILY['w']), (4, 0, LILY['p']), (5, 0, LILY['w']), (4, 1, LILY['w']), (3, 1, LILY['p']), (5, 1, LILY['p'])):
                put(a, x, y, c)
        cells.append(a)
    return np.concatenate(cells, 1), (W, H)


def stones():
    W, H = 12, 7
    def stone(a, x0, w, h):
        y0 = H - h
        for y in range(y0, H):
            for x in range(x0, x0 + w):
                top, bot, left, right = y == y0, y == H - 1, x == x0, x == x0 + w - 1
                if (top or bot) and (left or right): continue      # rounded corners
                if top or (y == y0 + 1 and left and h > 3): c = STONE['lit']
                elif bot or right: c = STONE['dk']
                elif y == y0 + 1 or (left and y < H - 2): c = STONE['ml']   # (round 1) the mid-light under the lit top
                else: c = STONE['mid']
                put(a, x, y, c)
    A = canvas(W, H); stone(A, 0, 7, 6); stone(A, 6, 6, 4)
    B = canvas(W, H); stone(B, 2, 8, 5)
    return np.concatenate([A, B], 1), (W, H)


def main():
    check = '--check' in sys.argv
    bad = 0
    for name, (img, cell) in (('cp_reeds', reeds()), ('cp_lily', lily()), ('cp_bankstones', stones())):
        img[img[..., 3] == 0] = 0
        p = os.path.join(SCENE, name + '.png')
        if check:
            same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), img)
            print(('OK   ' if same else 'DIFF ') + name); bad += 0 if same else 1
            continue
        Image.fromarray(img, 'RGBA').save(p)
        os.makedirs(os.path.join(SRC, name), exist_ok=True)
        n = img.shape[1] // cell[0]
        aseprite_io.write(os.path.join(SRC, name, name + '.aseprite'),
                          [img[:, i * cell[0]:(i + 1) * cell[0]] for i in range(n)], layer=name)
        cols = len(np.unique(img[img[..., 3] > 0][:, :3], axis=0))
        print(name, f'{img.shape[1]}x{img.shape[0]}', f'{n} cells of {cell[0]}x{cell[1]}', cols, 'colours')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
