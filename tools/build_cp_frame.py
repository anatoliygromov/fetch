#!/usr/bin/env python3
"""build_cp_frame.py [--check] [--roof]: City Park's climbing frame (park_frame.png), built by rule,
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
"random bars"). A playground climbing frame in the build of the approved play tower (tools/build_cp_built.py
tower_deck, tower_post): every surface Pepper stands on is one of the tower's yellow decks (lit cap, flat front,
shade row, bolts, 1 px ink), exactly on its box, and stands on the tower's grey posts.
Round 1 (a full-width red panel between the decks, posts 4 px in from the deck ends, a red box step) failed the
independent review: "a red desk with a bench in front and a crate under it", the porthole round bone 171 a keyhole.
Round 2 (now):
  - posts flush under every deck end (no table-top overhang); a middle post through both decks to the path, so the
    posts run from deck to ground as the tower's do
  - one small red panel, the slide tower's (its porthole cut 1:1 from park_slide.png), in the bay between the left
    and middle posts, clear of bones 171 (2760, 304) and 245 (2724, 316); the rest open between the posts
  - the step the lowest of three decks: the deck cap on a grey block in the posts' colours
  - --roof (the review's fix 5, a red roof bar on raised posts) was tried and not used: 12 px over the top deck it
    crosses Pepper's chest and the magpie and its ball on perch 11
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


def step_block(w, h):
    """(round 2) the step as the lowest of three decks: the tower's yellow deck cap (tower_deck) on a grey block in
    the posts' colours (lit left column), ink round all of it: box w x h"""
    a = canvas(w + 2, h + 1)
    rect(a, 0, 0, w + 2, h + 1, INK)
    rect(a, 1, 8, w, h - 8, P_MID); rect(a, 1, 8, 1, h - 8, P_LT)
    stamp(a, tower_deck(w), 0, 0)
    return a


def roof_bar(w):
    """the slide tower's red roof bar, its rows 0-3 as in park_slide.png: ink, red, dark red, ink"""
    a = canvas(w, 4)
    rect(a, 0, 0, w, 4, INK); rect(a, 1, 1, w - 2, 1, R_MID); rect(a, 1, 2, w - 2, 1, R_DK)
    return a


def build(variant='r2', roof=False):
    """round 2 (independent review round 1: "a red desk with a bench in front and a crate under it"): posts flush
    under every deck end (no table-top overhang), a middle post from the top deck through the low deck to the path
    (posts that run from deck to ground: the tower's frame, not a table's legs), one small red panel like the slide
    tower's in the bay between the left and middle posts (its porthole clear of bones 171 and 245), the rest open;
    the step the lowest of three decks (deck cap on a grey block). roof: the top deck's posts carried 12 px higher
    with the slide's red roof bar between them (the review's fix 5, only if it still reads as a table)"""
    a = canvas(W, H)
    top0, top1, low0, low1 = 2724, 2800, 2712, 2784
    lx, rx = ix(top0) - 1, ix(top1 + 1) - 6                 # the top deck's posts: flush under its ink ends
    ytop = iy(268) if roof else iy(284)
    stamp(a, tower_post(4, FOOT - (ytop + OY)), rx, ytop)                 # right: down to the path
    stamp(a, tower_post(4, 304 - (ytop + OY)), lx, ytop)                  # left: stands on the low deck
    if roof:
        stamp(a, roof_bar(rx + 6 - lx), lx, ytop - 3)
    # a middle post through both decks to the path (the tower's frame: posts run from deck to ground), at the
    # small panel's right end, clear of bone 171 (2760, 304: image x 43-55)
    mx = ix(2748) - 1
    stamp(a, tower_post(4, FOOT - (ytop + OY)), mx, ytop)
    # the small panel: between the left post's and the middle post's ink, under the top deck's bottom ink
    px0 = lx + 5; pw = mx - px0 - 1; ph = (iy(304) - 1) - (iy(280) + 6) - 1   # its bottom ink on the low deck's top ink (row 40)
    p = panel(pw, ph, [1 + (pw - 8) // 2])
    stamp(a, p, px0, iy(280) + 6)
    a[iy(280) + 6:iy(280) + 6 + p.shape[0], px0:px0 + p.shape[1]][p[..., 3] == 0] = 0
    # the low deck's posts, flush under its ends (the left one on the decoration box 2712-2716)
    stamp(a, tower_post(4, FOOT - 308), ix(low0) - 1, iy(308))
    stamp(a, tower_post(4, FOOT - 308), ix(low1 + 1) - 6, iy(308))
    stamp(a, tower_deck(top1 - top0), ix(top0) - 1, iy(280) - 1)
    stamp(a, tower_deck(low1 - low0), ix(low0) - 1, iy(304) - 1)
    stamp(a, step_block(16, 12), ix(2716) - 1, iy(316) - 1)
    a[a[..., 3] == 0] = 0
    return a


def main():
    variant = 'roof' if '--roof' in sys.argv else 'r2'
    a = build(variant, roof='--roof' in sys.argv)
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
