#!/usr/bin/env python3
"""build_rw_arch.py: the underpass under River Walk's bridge (screen 7, world x 1939-2068, y 192-215), BUILT by rule.

  python3 -I tools/build_rw_arch.py           write riverwalk/art/scene/rw_arch.png (+ art/source/rw_arch/rw_arch.aseprite)
  python3 -I tools/build_rw_arch.py --check   fail if the file on disk is not what this script builds

History: 6 Nov (art/rw-ground-06nov), scene.lua archBack drew a low wide slot under the approved pier art: 6 px stone
jambs, a 6 px rise segmental arch, a dark vault. Owner, 7 Nov board: "rw_bridge_arch_06n: redraw". It read as the
pier block sitting on a dark gap, not as a stone bridge you walk under.

7 Nov (day/07nov-rwarch): a stone underpass seen end on, as on Stockholm's quays, under the pier art's plinth (the
approved pier's pixels are not touched; this piece starts on the row under the plinth's dark bottom line).
Art (0, 0) = world (1939, 192): the plinth's own width (1939-2068), down to row 23 (y 215); Pepper's line is y 216.
  * the jambs: 18 px of the pier's own ashlar (10 px courses: a lit top row, the face, a shade row, a joint row; the
    vertical joints alternate per course), a base course like the pier's plinth (lit top, face, shade), the outer
    edges as the pier's sides (lit 158 left, 109 right). They stand on the paving: the pier's face comes down to
    Pepper's line, so it hides the paving behind it.
  * the arch: a segmental arch (span 94 px, rise 16), its crown at row 0 right under the plinth, so the opening is as
    tall as the passage Pepper crawls through (y 192-216). A ring of voussoirs (5 px) on each haunch in the pier's
    light granite (219) with radial joints and an arris (158), a lit row along the arris (243), a joint (97) round
    its back; the ring runs up under the plinth, so the plinth reads as the band course over the arch. The keystone
    hangs from the plinth at the crown: a wedge 8 px wide, rows 0-2 (y 192-194; Pepper's crawling back is at y 194-197).
  * the passage inside, in one-point perspective from the eye point (row VPY, about Pepper's eye height): the soffit
    and the side walls in darker shades of the same stone (soffit 128 then 109, walls 109 then 97, a 2 px ring joint
    half way in; deeper is darker), the floor left open, so the paving runs through (painted with the ground, with
    its slanted shadow bands);
  * at the far end a lit opening, the same arch scaled by K about the eye point: daylight (the sky's horizon colour),
    the far quay's trees and paving.
Flat ramps from the pier art's palette (no new stone colours), parts drawn once by rule on the pixel grid; the
voussoirs are symmetric about the crown (the left half is built, the right half is its mirror)."""
import os, sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

def rgb(r, g, b): return np.array([r, g, b, 255], np.uint8)
# the pier art's own stone (riverwalk/art/scene/pier.png): lightest to darkest
HI, LIT, FACE, H2, EDGE, SHADE, DARKE, JOINT, DEEP, DEEPEST = (
    rgb(243, 226, 220), rgb(219, 199, 195), rgb(201, 180, 177), rgb(166, 146, 146), rgb(158, 138, 140),
    rgb(128, 112, 117), rgb(109, 95, 99), rgb(97, 83, 88), rgb(89, 77, 83), rgb(75, 65, 71))   # (DEEPEST: unused)
# the far end: daylight (the sky's horizon colour), the far quay's trees and its paving (pavement.png's colours)
SKY, TREE, TREE_D, PAVE, PAVE_B = rgb(221, 229, 236), rgb(141, 169, 137), rgb(98, 122, 106), rgb(214, 206, 202), rgb(184, 183, 190)

W, H = 130, 24                     # world x 1939-2068, y 192-215
J = 18                             # jamb width
X0, X1 = J, W - J - 1              # the opening's columns (18 .. 111)
CX = W / 2                         # 65.0: the opening's centre line (between cols 64 and 65)
HS = (X1 + 1 - X0) / 2             # 47: half span
CROWN = 0                          # the intrados' crown row (y 192)
SPRING = 16                        # the springing row on the jamb faces (y 208): rise 16
RING = 5                           # the ring's thickness (radial px)
NV = 15                            # voussoirs over the whole arch (odd: a keystone)
FLOOR = 24                         # the front floor line (Pepper's line, y 216)
VPY, K = 9.0, 0.44                 # the eye point's row and the far opening's scale
R = (HS * HS + (SPRING - CROWN) ** 2) / (2 * (SPRING - CROWN))   # the intrados' radius
CY = CROWN + R                     # its centre row
THS = math.asin(HS / R)            # the half angle at the springing (from the vertical)


def front_open(x, y):
    """(x, y) a point (pixel centre) in art space: inside the front opening?"""
    if x < X0 or x > X1 + 1 or y > FLOOR: return False
    if y >= SPRING: return True
    return (x - CX) ** 2 + (y - CY) ** 2 < R * R


def depth(px, py):
    """the scale t (K .. 1) about the eye point at which the opening's outline passes through the pixel centre, and
    the surface it lies on ('soffit', 'wall', 'floor'); t < K: inside the far opening (None)."""
    inside = lambda t: front_open(CX + (px - CX) / t, VPY + (py - VPY) / t)
    if inside(K): return K, 'far', px, py                                     # seen through the far opening
    lo, hi = K, 1.0                                                           # the outline at t: inside above it
    for _ in range(40):
        mid = (lo + hi) / 2
        if inside(mid): hi = mid
        else: lo = mid
    t = hi
    qx, qy = CX + (px - CX) / t, VPY + (py - VPY) / t                          # the matching point on the front outline
    if qy >= FLOOR - 0.01: surf = 'floor'
    elif qy >= SPRING: surf = 'wall'
    else: surf = 'soffit'
    return t, surf, qx, qy


def stone(y, lx, right):
    """the pier's ashlar at row y, lx px in from the pier's outer side (both jambs and the spandrels)"""
    if y >= 20:                                                              # the base course (as the pier's plinth)
        c = HI if y == 20 else (SHADE if y == 23 else FACE)
    else:
        r, course = y % 10, y // 10
        vj = 24 if course == 0 else J                                        # the vertical joints alternate
        if r == 9: c = JOINT                                                 # the bed joint
        elif r == 8: c = EDGE                                                # the stone's shaded lower edge
        elif lx == vj: c = DARKE                                             # the head joint
        elif r == 0 or lx == vj + 1: c = LIT if (lx - (vj + 1 if lx > vj else 0)) > 3 else HI   # lit top and left
        else: c = FACE
    if lx == 0 and (y >= 20 or y % 10 < 9): c = DARKE if right else EDGE    # the pier's sides: 158 left, 109 right
    return c


def ring_px(px, py):
    """the ring at a pixel centre: None, or its colour (left half; voussoir k = 0 is the keystone)"""
    dx, dy = px - CX, py - CY
    d = math.hypot(dx, dy)
    ang = math.atan2(-dx, -dy)                                               # 0 at the crown, + towards the left
    if ang > THS + 1e-9 or d < R: return None
    if py >= SPRING + 0.5 and px < X0: return None
    if d >= R + RING:
        return JOINT if d < R + RING + 1 else None                            # the joint round the ring's back
    step = 2 * THS / NV
    k = int((ang + step / 2) // step)
    joint = int((math.atan2(-(dx + 1), -dy) + step / 2) // step) != k        # a radial joint (left side of a stone)
    if joint: return EDGE
    if d < R + 1: return EDGE                                                # the intrados' arris (in shade)
    return HI if d < R + 2 else LIT                                          # a lit row along the arris, the face


def build():
    a = np.zeros((H, W, 4), np.uint8)
    # 1 the jambs and the spandrels: the pier's ashlar (10 px courses), the base course; mirrored about the centre
    for y in range(H):
        for x in range(W):
            right = x >= W // 2
            a[y, x] = stone(y, (W - 1 - x) if right else x, right)
    # 2 the passage inside the opening: soffit, walls, the far opening; the floor stays open (the paving)
    fy = VPY + (FLOOR - VPY) * K                                              # the far opening's floor row
    for y in range(H):
        for x in range(X0, X1 + 1):
            px, py = x + 0.5, y + 0.5
            if not front_open(px, py): continue
            t, surf, qx, qy = depth(px, py)
            lx = min(x, W - 1 - x)
            if surf == 'far':                                                 # daylight: sky, trees, the far quay
                d = fy - py
                if d < 2: c = PAVE
                elif d < 3: c = PAVE_B
                elif d < 5: c = TREE_D if lx % 6 == 0 else TREE
                else: c = SKY
                a[y, x] = c
                continue
            if surf == 'floor':
                a[y, x] = 0
                continue
            s = (1 - t) / (1 - K)                                            # 0 at the face .. 1 at the far end
            # deeper is darker: the soffit one step lighter than the walls (it takes the light off the paving)
            c = SHADE if surf == 'soffit' else DARKE
            if s >= 0.5: c = DARKE if surf == 'soffit' else JOINT
            if 0.42 <= s < 0.54: c = JOINT if surf == 'soffit' else DEEP     # a ring joint half way in (2 px)
            a[y, x] = c
    # 3 the ring of voussoirs with radial joints (left half, mirrored)
    for y in range(H):
        for x in range(W // 2):
            c = ring_px(x + 0.5, y + 0.5)
            if c is not None: a[y, x] = c; a[y, W - 1 - x] = c
    # 4 the keystone hangs from the plinth at the crown: a wedge, 8 px wide on row 0, 6 px on row 2
    for y in range(3):
        for lx in range(int(CX) - 4 + y // 2, int(CX)):
            edge = lx == int(CX) - 4 + y // 2 or y == 2
            c = EDGE if edge else (HI if lx < int(CX) - 1 else LIT)
            a[y, lx] = c; a[y, W - 1 - lx] = c if c is not HI else LIT
    return a


if __name__ == '__main__':
    out = 'riverwalk/art/scene/rw_arch.png'
    a = build()
    if '--check' in sys.argv:
        ok = os.path.exists(out) and np.array_equal(np.array(Image.open(out).convert('RGBA')), a)
        print('CHECK PASS' if ok else 'CHECK FAIL: ' + out); sys.exit(0 if ok else 1)
    if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
    Image.fromarray(a).save(out)
    if out.startswith('riverwalk/'):
        os.makedirs('art/source/rw_arch', exist_ok=True); aseprite_io.write('art/source/rw_arch/rw_arch.aseprite', [a])
    print(os.path.basename(out), W, 'x', H, 'colours', len({tuple(p) for p in a.reshape(-1, 4) if p[3]}))
