#!/usr/bin/env python3
"""build_cp_frame.py [--check] [--variant open|house]: City Park's climbing frame (park_frame.png), built by rule,
0 credits (day/07nov-cpplay, owner 7 Nov board: "park_frame_06n: redraw, looks really weird").

  python3 -I tools/build_cp_frame.py           -> riverwalk/art/scene/park_frame.png, art/source/park_frame/
  python3 -I tools/build_cp_frame.py --check   -> exit 1 if the file differs from what this script builds

What it is in the game (citypark_tall.lua; the flat citypark.lua has the same boxes 144 px higher):
  STEP   2716-2732, top 316, 12 px high, solid, hidden (drawn by this image): the first step up, a hop from the path
  FRAME  2712-2784, top 304, one-way: the low deck, 12 px over the step
  (bar)  2724-2800, top 280, one-way: the top deck, 24 px over the low deck; the magpie's perch 11 (2752, 280)
  posts  2712-2716 and 2796-2800, y 264-328: decoration boxes, not drawn by the game (this image draws them)
The image is 90 x 67 at (FRAME x0 - 1, 119 + dy): image x = world x - 2711, image y = world y - 263 (tall level).

The redraw (was: blue pipes, two tall posts and two stacked bars, a ladder and a yellow stool: "a cage", "a gate",
"random bars"). Now a playground climbing block in the build of the approved play tower (tools/build_cp_built.py
tower_deck, tower_post): every surface Pepper stands on is one of the tower's yellow decks (lit cap, flat front,
shade row, bolts, 1 px ink), every deck stands on the tower's grey posts down to the path (or onto the deck below,
as the tower's upper deck does). The step is a red box (the slide's red) with a yellow tread: a step, not a stool.
Under the top deck a red panel (the slide tower's red panel and its round window, cut 1:1 from park_slide.png)
closes the space between the two decks, from post to post, so the top deck is the roof of a little play house and
the low deck its porch: one piece in the tower's family, not two shelves. Under the low deck it stays open (Pepper
walks the path under it: the deck is one-way). One window, not two (two read as a face).
Parts are drawn once (deck, post, panel, step) and stamped on the integer grid of the boxes. 1 px ink outline round
everything (an obstacle). Light from the upper left."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io
from build_cp_built import (canvas, rect, put, stamp, hx, INK, Y_LT, Y_MID, Y_SH, P_LT, P_MID, tower_deck,
                            tower_post, SCENE, SRC)

# the slide's red (park_slide.png): light, mid, dark
R_LT, R_MID, R_DK = hx('e2715d'), hx('c8473a'), hx('8f2f27')
W, H = 90, 67
OX, OY = 2711, 263                       # image (0, 0) in the tall level's world
FOOT = 328                               # the path line


def ix(wx): return wx - OX


def iy(wy): return wy - OY


def step_box(w, h):
    """the step: box w x h plus the outline; a yellow tread (the decks' cap, 3 rows) on a red box (lit left
    column, a dark bottom row), the ink on all four sides"""
    a = canvas(w + 2, h + 1)
    rect(a, 0, 0, w + 2, h + 1, INK)
    rect(a, 1, 1, w, 1, Y_LT); rect(a, 1, 2, w, 2, Y_MID); rect(a, 1, 4, w, 1, Y_SH)    # the tread
    rect(a, 1, 5, w, 1, INK)                                                            # its edge over the box
    rect(a, 1, 6, w, h - 7, R_MID); rect(a, 1, 6, 1, h - 7, R_LT); rect(a, w, 6, 1, h - 7, R_DK)
    return a


def porthole():
    """the slide tower's round window, cut 1:1 from the approved park_slide.png (rows 17-25, columns 13-20): its ink
    ring, open inside (a hole you see the park through); 8 x 9. The red round it is left to the panel"""
    s = np.array(Image.open(os.path.join(SCENE, 'park_slide.png')).convert('RGBA'))[17:26, 13:21]
    ring = (s[..., 3] > 0) & np.all(s[..., :3] == INK[:3], axis=-1)
    hole = s[..., 3] == 0
    return ring, hole


def panel(w, h, holes):
    """the wall between the decks, the slide tower's red panel (park_slide.png): ink on all four sides, a lit top
    row, the red, a dark bottom row; a porthole (the slide's) at each x in holes (left column of the window)"""
    a = canvas(w + 2, h + 2)
    rect(a, 0, 0, w + 2, h + 2, INK)
    rect(a, 1, 1, w, h, R_MID); rect(a, 1, 1, w, 1, R_LT); rect(a, 1, h, w, 1, R_DK)
    ring, hole = porthole()
    y0 = 1 + (h - ring.shape[0]) // 2
    for x0 in holes:
        sub = a[y0:y0 + ring.shape[0], x0:x0 + ring.shape[1]]
        sub[ring] = INK; sub[hole] = 0
    return a


def build(variant='house'):
    a = canvas(W, H)
    # the top deck's posts: the right one on the decoration box 2796-2800 down to the path; the left one 4 px in
    # from the deck's left end, standing on the low deck (the tower's rule for an upper deck over a lower one)
    top0, top1, low0, low1 = 2724, 2800, 2712, 2784
    stamp(a, tower_post(4, FOOT - 284), ix(2796) - 1, iy(284))
    stamp(a, tower_post(4, 304 - 284), ix(top0 + 4) - 1, iy(284))
    if variant == 'house':                                  # the wall between the decks, from post to post, its
        x0, x1 = ix(top0 + 4) + 4, ix(2796) - 1             # ink rows on the decks' ink rows (top 286, bottom 303)
        pw = x1 - x0 - 1; ph = (iy(304) - 1) - (iy(280) + 6) - 1
        holes = [1 + (pw - 8) // 2]                     # one porthole in the middle (two read as a face)
        p = panel(pw, ph, holes)
        stamp(a, p, x0, iy(280) + 6)
        a[iy(280) + 6:iy(304), x0:x1 + 1][p[..., 3] == 0] = 0     # the portholes: open (stamp skips the clear)
    # the low deck's posts: the left one on the decoration box 2712-2716, the right one 4 px in from its right end
    stamp(a, tower_post(4, FOOT - 308), ix(low0) - 1, iy(308))
    stamp(a, tower_post(4, FOOT - 308), ix(low1 - 8) - 1, iy(308))
    stamp(a, tower_deck(top1 - top0), ix(top0) - 1, iy(280) - 1)
    stamp(a, tower_deck(low1 - low0), ix(low0) - 1, iy(304) - 1)
    stamp(a, step_box(16, 12), ix(2716) - 1, iy(316) - 1)
    a[a[..., 3] == 0] = 0
    return a


def main():
    variant = sys.argv[sys.argv.index('--variant') + 1] if '--variant' in sys.argv else 'house'
    a = build(variant)
    p = os.path.join(SCENE, 'park_frame.png')
    if '--check' in sys.argv:
        same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
        print(('OK   ' if same else 'DIFF ') + 'park_frame'); sys.exit(0 if same else 1)
    if '--out' in sys.argv:
        Image.fromarray(a, 'RGBA').save(sys.argv[sys.argv.index('--out') + 1]); return
    Image.fromarray(a, 'RGBA').save(p)
    d = os.path.join(SRC, 'park_frame'); os.makedirs(d, exist_ok=True)
    Image.fromarray(a, 'RGBA').save(os.path.join(d, 'park_frame.png'))
    aseprite_io.write(os.path.join(d, 'park_frame.aseprite'), [a], layer='park_frame')
    cols = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
    print(f'park_frame {W} x {H}, {cols} colours ({variant})')


if __name__ == '__main__':
    main()
