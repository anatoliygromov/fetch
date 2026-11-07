# Review round 1: City Park playground redraws (branch day/07nov-cpplay, 7 Nov 2026)

Independent reviewer (did not make the work). Base: origin/main. Branch head 5e1f4b2.
Looked at both files at 4x and 6x (nearest neighbour) in colour and greyscale, in LOOK_SWEEP frames of every
citypark_tall screen where they show (LOOK_STEP 80, all three tiers y 0 / 24 / 144, branch and main), with Pepper
rendered on each deck (cam 2560, LOOK_PX 154 / 166 / 190 / 215 / 236 / 250) and on the step (LOOK_SPOTS 2724,316
and 2716,304), and against every earlier version in git.

| Piece | Verdict |
| --- | --- |
| park_frame (climbing frame) | **FAIL** (reads as furniture) |
| park_bush (front bush) | **FAIL** (reads as two hills, edge comb and dotted lines) |
| play tower, rope bridges, other approved pieces | unchanged (no diff in cp_tower_*, cp_built.lua) |

## Checks I ran (each with a fresh XDG_DATA_HOME, `SDL_AUDIODRIVER=dummy xvfb-run -a`)

| Check | Result |
| --- | --- |
| tools/check_pepper.sh | PEPPER UNCHANGED (3908 steps identical) |
| tools/check_flow.sh | 125 of 125 |
| love riverwalk --level citypark_tall --physics | 97 of 97 |
| asset_qa.py park_frame park_bush, and --file for each (play cp / front cp) | PASS, PASS |
| build_cp_frame.py --check / build_cp_bush.py --check | OK / OK |
| build_cp_built.py | has no --check: a run rewrites its files, all byte-identical (git diff empty) |
| measure_layers.py | City Park light to dark. park_bush front: median 20, p10 20, 3 colours (row OK); **dither 1.0 (main: 0.0)**. park_frame play: outline 100 %, lone 0.3 % |

The scripts pass both pieces. The fails below are what the scripts cannot judge (asset_qa.md gate 6).

## 1. park_frame (riverwalk/art/scene/park_frame.png, 90 x 67): FAIL

What is right: clean build, straight lines straight, outline unbroken, no lone pixels, 9 colours all from the tower
and the slide. Every top matches its box (I rendered Pepper on each): top deck cap at image row 17 = world 280,
low deck row 41 = 304, step tread row 53 = 316; her feet and shadow sit on the yellow. All four posts reach the
path (rows 65-66). Nothing floats, no free bar ends. Cleaner than every earlier version (22 Oct greybox, 22 Oct
rungs, 6 Nov ladder and stool), which were all the same blue pipe cage.

Why it fails: it does not read as a playground piece. At 1x and 3x, colour and greyscale, it reads as furniture:
a red desk or sideboard (the 76 px yellow top on two legs over a closed red front), a bench in front of it (the low
deck on two legs) and a crate under the bench (the step). 48 px high by 90 wide is table proportion, and the
closed full-width front turns the open "table and bench" the maker rejected into a desk. Next to the tower it is in
the same colours but not the same build: the tower reads as play equipment through its open frame, its height,
the small framed panel and the slide; this piece has none of those. Worse in game: bone 171 (world 2760, 304)
is drawn exactly in the porthole (image x 49-56, rows 27-35), and the ring plus the bone read as a keyhole or a
drawer handle: a locked red chest. Seen in every frame at cam 2480-2560, tier 144.

Fixes (numbered, pixel areas in image coordinates; image x = world x - 2711, image y = world y - 263):
1. Remove the full-width closed panel (x 21-84, rows 23-40). Use the slide tower's panel proportion instead: one
   red panel about 24-28 px wide hung under the top deck against its left post (about x 22-48, rows 23-33), the
   rest of the space between the decks open, so the piece is posts and decks with one small panel, like the tower.
2. Take away the table-top overhang: the top deck sticks out 4 px past its left post (x 12-15) and the low deck
   4 px past its right post (x 70-73). Put the posts flush under the deck ends, as the top deck's right end already
   is (x 84-89). Overhanging tops on legs are the table tell.
3. Keep the porthole off the bone: with fix 1 it sits in the moved panel, centred near world x 2738 (image x
   23-30 wide ring). Never put the ring under bone 171 (2760, 304) or bone 245 (2724, 316).
4. The step (x 4-21, rows 52-64) reads as a crate or toolbox (red box, yellow lid). Draw it as the lowest of three
   decks in the same build: the yellow deck cap on a grey block in the post colours (or two short grey posts), so
   step, low deck and top deck read as one stair of decks. It stays solid, 16 x 12, on its box.
5. If after 1 to 4 the top still reads as a table in the 3x frame, add one height cue in the tower's language: the
   two top-deck posts (x 16-21, 84-89) carried up about 12 px over the deck with the slide's red roof bar
   (park_slide.png rows 0-2) between them. Check that bone 172 (2752, 280) and the magpie on perch 11 stay clear.
6. After the change: re-render Pepper on each deck and on the step (LOOK_PX 154-236 at cam 2560, LOOK_SPOTS
   2724,316), and the frames with bones 171, 172 and 245, colour and greyscale, at 3x.

Level note (not the art's fault, the boxes did not move): Pepper can scramble onto the step (316) under the
one-way low deck (304); standing there the low deck crosses her chest (LOOK_SPOTS 2724,316). It was the same with
the old stool. Worth a line to the level track.

## 2. park_bush (riverwalk/art/scene/park_bush.png, 75 x 34): FAIL

What is right: front row of the ladder holds (median 20, 3 colours, darker than the play line), it never covers
Pepper (on screen only rows 221-239 at tier 144, at cam 400-560 and 1680-1840; Pepper's feet are at 184 or higher
on screen; not on screen at tiers 24 and 0). No twigs, no orange specks, no painted noise: cleaner than the
22 Oct painted bush and both 6 Nov re-shades.

Why it fails: on screen it reads as two dark pointed hills (or ears), not a bush. The two crowns are the same
size, side by side, each ending in a single-pixel apex; the "back-lit rim" is the same colour as the earth band
behind it (89,66,87 on the band's purple), so on screen it does not read as light, only as a jagged edge; and the
clump lines inside are dotted, which measure as dither (1.0) and read as faint scribbles.

Fixes (image coordinates x, y):
1. Break the twin peaks: three or four crown clumps of different sizes and heights (for example the tallest
   centre-left, a smaller one right, the lowest left), not two equal lobes side by side.
2. No single-pixel apex: (26,3) and (48,2) and the 1 px tips under them. Each clump top a flat run of 3-5 px.
3. Close the comb on the top edge: 1 px notches between rim pixels at (22,5), (30,5), (38,8), (44,4), (52,4),
   with the tips beside them (21,5), (23,5), (29,5), (31,5), (37,8), (39,8), (43,4), (45,4), (51,4), (53,4).
   The silhouette edge should be continuous runs, scalloped by whole leaves of at least 2 px, not 1 px teeth.
4. Inner clump lines (rows 9-17, for example (32,10), (34,10), (40,10), (42,10), (29,11)-(31,11), (45,12)) are
   dotted (o, dark, o): make each a continuous 1 px arc, or drop them; no checker pattern (dither must be 0).
5. The rim: either a colour that differs from the band it sits on (the README's lever: a warmer rim on the top
   clumps, as continuous 1 px runs, never dots), or no rim. As it is, it is invisible and only adds jaggies.
6. Re-render cam 480 and 1760 at tier 144, colour and greyscale, 3x and 6x crops of y 212-240.

## Is the new one better than every earlier version?

- Frame: cleaner than all three earlier versions, but not better as a read: they read as a cage, this reads as a
  desk and a bench. Not ready for the board.
- Bush: cleaner than all three earlier versions (no twigs, no specks), but loses the bush read the 6 Nov
  versions had. Not ready for the board.

Frames I made for this review (scratch, not committed): sweeps of both branches, Pepper on each deck, on the
step, bush crops at 6x. The maker's own frames in docs/review/07nov/cpplay/frames show the same problems
(frame_x2560_before_after_3x.png: the bone in the porthole; bush_x0460_before_after_3x.png: the two humps).
