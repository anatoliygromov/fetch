# Review round 2: City Park playground redraws (branch day/07nov-cpplay, head 49f9e5a, 7 Nov 2026)

Independent reviewer, same method as round 1 (review_round1.md): both files at 6x, colour and greyscale, a text
dump of every pixel, LOOK_SWEEP frames at cam 2480 and 2560 (tier 144) with Pepper at LOOK_PX 154 / 166 / 190 /
215 / 236, LOOK_SPOTS 2724,316 and 2716,304 (the step and the low deck), and the bush at cam 320-560 and
1600-1840 at all three tiers (144, 24, 0).

| Piece | Verdict |
| --- | --- |
| park_frame | **FAIL, one small fix** (the rest passes) |
| park_bush | **PASS** |
| play tower and other approved pieces | unchanged (build_cp_built.py rebuilds them byte for byte, git diff empty) |

## Checks (each with a fresh XDG_DATA_HOME, `SDL_AUDIODRIVER=dummy xvfb-run -a`)

| Check | Result |
| --- | --- |
| tools/check_pepper.sh | PEPPER UNCHANGED (3908 steps identical) |
| tools/check_flow.sh | 125 of 125 |
| love riverwalk --level citypark_tall --physics | 97 of 97 |
| asset_qa.py park_frame park_bush | PASS, PASS |
| build_cp_frame.py --check / build_cp_bush.py --check | OK / OK |
| measure_layers.py | City Park light to dark. park_bush front: median 20, p90 27, 3 colours, lone 0.1 %, dither 0.0. park_frame: 9 colours, outline 100 %, lone 0.5 %, dither 0.0 |

## 1. park_frame: FAIL, one small fix

Round 1 fixes, checked one by one:
1. Full-width panel gone: one red panel x 17-36, rows 23-37, between the left and the middle post; the rest open. Done.
2. Posts flush under every deck end: top deck x 12-89 on posts x 12-17 and 84-89; low deck x 0-73 on posts
   x 0-5 and 68-73; the middle post x 36-41 runs from the top deck through the low deck to the path. Done.
3. Porthole at x 22-31 (world 2733-2742), clear of bone 171 (2760, 304) and bone 245 (2724, 316). Done: in game the
   ring is empty and bone 171 floats in the open bay, as a pickup should.
4. Step: the deck cap on a grey block in the post colours, x 4-21, rows 52-64. It reads as the lowest of three
   decks. Done.
5. Roof bar tried and dropped for a good reason (it would cross Pepper and the magpie). Accepted.

The read: in game, next to the tower, it now reads at once as a stepped play frame of the same set (yellow decks,
grey posts, one small red panel with the slide's round window). No desk, no chest, no crate. Every top matches its
box: Pepper's feet and shadow sit on the yellow cap at 280 (top deck), 304 (low deck) and 316 (step). All posts end
on the path line (bottom ink row 64 = world 327, the path at 328). Outline unbroken, straight lines straight, bolts
the tower's 2 x 2, no lone pixels, nothing floats, no free bar ends. Better than every earlier version (three blue
pipe cages and round 1's desk).

The one fix:
1. The panel stops 2 rows short of the low deck: its bottom ink is row 37, then rows 38-39 are open (x 18-35), then
   the low deck's ink at row 40. In game this is a 2 px line of background under the red panel, at 3x clearly a
   crack, at 1x a panel that looks cut short. The slide tower's panel (park_slide.png) sits straight on its deck.
   Extend the panel 2 rows down (red to row 38, its dark row on 39) so its bottom ink is the low deck's ink row 40.
   The porthole may stay where it is or move down 1 row to stay centred. A re-check of that area at 6x and one
   in-game frame (cam 2560, tier 144) is enough after that; no new full round needed.

Level note (unchanged from round 1, not the art): Pepper can stand on the step (316) under the one-way low deck
(304), and the deck then crosses her chest (LOOK_SPOTS 2724,316).

## 2. park_bush: PASS

Round 1 fixes, checked one by one:
1. Four clumps of different sizes and heights (tops at rows 2, 7, 11, 13): no twin peaks. Done.
2. Flat tops (runs of 16, 14, 9 and 8 px), round shoulders, no 1 px apex. Done.
3. Top edge: continuous runs, no notches, no teeth (checked every edge pixel in the dump). Done.
4. Solid 2-3 row lit bands (43,31,51) and continuous joins between clumps (x 46 rows 10-12, x 20-21 rows 16-19,
   x 57-58 rows 16-20); dither 0.0. Done.
5. Rim warm brown (107,74,58), continuous along the top edges, clearly different from the earth band. Done.

On screen (cam 480 and 1760, tier 144) it reads as a dark scalloped shrub silhouette at the bottom edge, in the
front row of the ladder (median 20, p90 27, on-screen luma 20-56), the rim a thin warm edge, no specks. It never
covers Pepper (on screen rows 221-239 only, her feet at 184 or higher; not on screen at tiers 24 and 0). Better than
every earlier version: no twigs, no orange dots, no noise, and unlike round 1 it reads as a bush.

## Frames (scratch, not committed)

Pepper on each deck and on the step, colour and greyscale at 3x; the bush crops at 6x and the bottom of the
screen at 2x; the pixel dumps of both files.
