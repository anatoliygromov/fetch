Reviewer: independent gate-8 art reviewer (Claude, did not make this), 7 Nov 2026
Branch day/07nov-ground at fc03880 (riverwalk/joins.lua, tools/make_ground_kit.py, Sc.paintQuay, Sc.nearBanks, Sc.drawTreeFeet, root and lawn tufts), worktree review-ground07. Every screen of riverwalk (13) and citypark_tall (27: tiers y 144, 24, 0) rendered with LOOK_SWEEP=1 LOOK_STEP=320, looked at as 2x contact sheets in colour and greyscale, every screen at 3x, every join at 6x to 12x. Own view formed before reading docs/review/07nov/ground/README.md.

The owner's words: "whenever we see two different types of ground connecting, they look cut, including the hills etc."

# Round 1 (reviewer, 7 Nov)

## The system
riverwalk/joins.lua gives every change of ground kind a rule and the --physics test checks that each is stamped. That is the right shape. The eye test below is what matters: three joins still read as cut, and they are the ones with the most screen time (the quay top against the water in River Walk, the pond banks in City Park).

## Every join seen, PASS/FAIL, with its screen (camera x, screen x/y at 1x)

### River Walk
| # | Join | Where | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| RW-a | paving / kerb / road | x 0 to 1280, x 2880 to 3728, y 194-198 | PASS | lit kerb top row, dark kerb face, then the textured road |
| RW-b | garden lawn / paved door path | x 0, screen x 42 and 84, y 172-184 | PASS | grass blades over the path's edges |
| RW-c | garden lawn and pickets / kerb | x 0, y 184 | PASS | pales stand on the kerb row, grass between them |
| RW-d | kennel foot / lawn | x 0, screen x 0-44, y 183 | PASS | blades over the lower right corner, the ink sits in the grass |
| RW-e | bench legs / lawn | x 0, screen x 93-189 | PASS | legs go into the grass behind the pales |
| RW-f | house plinth / lawn, path and paving | x 0 (screen x 0-184), x 3728 (the door houses and the cafe) | PASS | a plinth band with a 2 px shade on the ground |
| RW-g | lime trunk foot / paving | x 0, screen x 236-262, y 172-174 | PASS (weak) | root flare and a 2 px darker contact strip; no grate. Reads as a street tree. |
| RW-h | birch trunk foot / paving | x 320, screen x 225-245, y 172-174 | PASS (weak) | same as RW-g |
| RW-i | pot, log, lamp bases / paving | x 0, x 320, x 960, x 3200 | PASS | the log has a cast shadow, the pot and lamps a base on the stone |
| RW-j | quay paving top edge / water (behind the railing) | x 320, 640, 960, 2880 (lower quay, screen x 0-120), 3200, 3520, y 171-172 | FAIL | the paving ends in one straight cream row and the water starts on the next row. No coping, no dark edge, no waterline. At 1x the quay reads as a sticker laid on the water. This is the longest join in the level (about 2,000 px of it). Fix: a 1 px coping row in the paving's darkest stone over a 1 px dark wet row (the arris colour already used at the quay ends), the whole length, under the railing posts. |
| RW-k | stone steps / lower quay and / upper paving | x 1280 (screen x 0-55), x 2880 (screen x 120-160) | PASS | 8 px rises, level treads, faces lit, they land on the paving with no seam |
| RW-l | quay-end caps / water (4) | x 1280 screen x 110; x 1600 screen x 207; x 2880 the lower quay's left end | PASS | 2 px coping overhang, a dark wet arris, a white ripple at the waterline; the reflection is faint but there |
| RW-m | kerb return / road (the wall's quoins) | x 2880, screen x 157-165, y 200-240 | PASS | quoin blocks on the corner, the wall's shadow across the road's end, no light strip |
| RW-n | bridge pier plinth / paving | x 1920, screen x 20-148, y 190-200 | FAIL | the slanted shadow on the paving (new) is good. Under the plinth the old dark lens is still there: a bowl-shaped dark patch with lumpy ends between the plinth and the paving. At 1x it reads as a hollow under the pier, as if the pier stood on a cushion of shade. Pre-existing, but it is the pier's ground join and the branch claims RW6. Fix: cut the lens; the plinth's bottom course sits straight on the paving with a 1 px dark contact row, the slanted shadow does the rest. |
| RW-o | pontoon / water | x 1280, screen x 220-280 | PASS | floats in the water, ripples at the floats, moored both ends |
| RW-p | tug, rowboat / water | x 1600, x 2240, x 2560 | PASS | waterline on the hull (approved pieces) |
| RW-q | jetty legs / water | x 2240, screen x 255-305 | PASS | legs into the water, ripple dashes |
| RW-r | kiosk feet / paving | x 640, screen x 105-165 and 250-320 | PASS (weak) | a dark bottom row, no plinth; acceptable for the back row |
| RW-s | grit box / paving | x 640, x 3200 | PASS | sits on its ink |
| RW-t | front verge / road | all road screens | PASS | the dark silhouette is the front layer, not a ground join |

### City Park (tall)
| # | Join | Where | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| CP-a | lawn strip / sand path | every y 144 screen, y 170-172 | PASS | the owner's old tile: a jaggy tuft row over the path |
| CP-b | sand path / earth strata | every y 144 screen, y 200-204 | PASS | grass fringe (old tile) |
| CP-c | tree line trunk feet / lawn | x 960 (screen x 130-175, 240-280), x 1280, x 1600, x 2560 | PASS (weak) | root flare, and the tuft row now laps 1 to 2 px over the foot. But the tuft strip is one 16 px pattern (three square bumps) repeated the whole lawn: at 3x it is a battlement, at 1x a regular sawtooth. Not a cut any more; mechanical. Fix: a 48 px tuft pattern with bumps of 1 to 3 px width and 1 to 3 px height in no order. |
| CP-d | gate pillars and gate bars / lawn | x 0, screen x 0-28 and 88-118, y 166-168 | PASS (weak) | the same tuft row laps the brick feet; no plinth |
| CP-e | poplar, lamp posts / lawn | x 0 (screen x 200-215, 290-300), x 1280, x 1920 | PASS (weak) | hidden by the tuft row |
| CP-f | near pond bank / water, both ends of both ponds | x 640 screen x 75-110 (left) and 300-320 (right); x 1920 screen x 75-110; x 2240 screen x 30-65 | FAIL | the path and the earth strata end on one straight 1 in 2 diagonal with a 1 px lit edge, and the water starts on the next pixel. No waterline, no wet band, no ripple where the water meets the bank: a trapezoid of water cut into the ground, plainest in greyscale (x 640, x 1920). On top of it, the two creek banks (x 1920 left, x 2240 right) carry a flat olive rounded wedge on the sand path that reads as a green blob, while the pond banks (x 640) have a sand wedge: the same tile in two colours. Fix: (1) a 2 px dark wet row along the whole diagonal under the water's edge, and 3 to 4 ripple dashes on the water against it; (2) one colour for the shoulder wedge (sand, the pond's), or drop the wedge and let the lip be the lit 1 px edge only; (3) break the diagonal's lower half with 2 px steps every 8 rows so the strata read as banked earth, not a saw cut. |
| CP-g | far bank / water | x 640, x 1920, y 185-188 | PASS | a khaki shore row, a dark olive edge, the reeds on it |
| CP-h | stepping stones / water | x 640, x 1920 | PASS | cut at the waterline, ripple ring, dark reflection |
| CP-i | duck boat / water and / right bank | x 640, screen x 215-300 | PASS (note) | floats; its stern lies over the right bank's slope, so the hull crosses the earth. Fine if the boat is meant to be beached. |
| CP-j | rope-bridge post foot / path | x 1920, screen x 50-66, y 183 | FAIL | the post ends on the path in a straight cut with no base, no dark row, no tuft. The only thing standing on the sand with nothing under it. Fix: a 1 px dark contact row 2 px wider than the post, or a 6 x 2 stone footing. |
| CP-k | pergola posts / path | x 2240, screen x 105-160, y 182 | PASS (weak) | thin vine-wrapped posts, no base; a 1 px dark row would ground them |
| CP-l | hedge, leaf piles, log, stump, bin, bench, picnic table / path | x 0, 320, 960, 1280, 2240 | PASS | each has a cast shadow or fallen leaves at its foot |
| CP-m | climbing frame, swing frame / path and lawn | x 2560 | PASS (weak) | 1 px darker row under the bars; the swing legs are behind the tuft row |
| CP-n | mid-row lawn / tree line, up in the trees | y 24 and y 0 tiers, screen y 215-240 behind the leaf front | PASS (weak) | the trunks now end on a khaki lawn band instead of sky. The band is a flat fill with rows of 2 px dashes on a grid (kit_cp_midlawn): a dot grid, not grass. Mostly hidden by the leaf front. Fix if seen: replace the dash grid with the tuft pattern of CP-c in 3 rows. |
| CP-o | branch ledges / trunks | all tiers | PASS | every ledge meets a trunk |
| CP-p | hills | none seen | n/a | the tall City Park has no hill in these frames |

## Checklist for the join system as a piece
1. Scale: PASS (8 px steps 0.17 m, kerb 4 px, coping 2 px).
2. Layer: PASS (greyscale sheets: paving light, road dark, water mid; the park lawn lighter than the earth).
3. Outline: PASS (ground is decoration: edges by its own darker shade; the kit parts have no ink).
4. Shapes: FAIL (the pond diagonals and the pier lens, CP-f and RW-n).
5. Shading: PASS (steps and quoins lit from the upper left).
6. Palette: PASS.
7. View: PASS.
8. Fit: PASS where it passes; the quay top edge (RW-j) is the one place the paving stops looking like a quay.
9. Read: FAIL on RW-j and CP-f (a child sees the water painted up to a line).

VERDICT: FAIL. Three joins read as cut (RW-j, RW-n, CP-f) plus the post foot CP-j. The rest is grounded.

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-ground at f1bd7ca. Every screen of both levels re-rendered (13 + 27), sheets in colour and greyscale, the fixed joins at 8x and 12x, pixel rows read where it mattered. Own view formed before reading the maker's list.

| # | Join | Round 2 | Evidence |
| --- | --- | --- | --- |
| RW-j | quay paving top edge / water | PASS | along the whole quay (x 320 to 1280, the lower quay at 2880, 3200 to 3728): row 171 a dark wet row (92,99,89), row 172 a grey-mauve coping row (176,168,179), then the paving. At 1x the quay now has an edge and the water a line it stops at. Under the railing posts, the lamp bases, the birch and lime feet and the kiosk feet the rows run behind the piece, nothing drawn over a foot. The quay-end caps meet the coping cleanly. |
| RW-n | bridge pier plinth / paving | PASS | the dark lens is gone: a plain stone course under the plinth, a 1 px shade line under the plinth's lip, the course on the paving inside the slanted shadow. Reads as a pier standing on the quay. |
| RW-2880 blob | road by the kerb return | PASS | gone (the manhole cover is clipped by the road scroll). |
| CP-f | near pond and creek banks / water (4) | PASS (weak) | one shoulder colour (sand) at all four, the olive blob gone. Along each diagonal a 2 px darker wet earth row, 2 px steps in the strata's lower half, and 3 to 4 pale ripple dashes on the water against the bank (x 640 screen x 75-110 and 300-320; x 1920 screen x 75-110; x 2240 screen x 30-65). It reads as a wet bank meeting water, not as new stripes: the wet row is earth-dark, not a line, and the steps are small enough to read as broken soil. What remains is the level's own convention, a section through the ground with water up to a slope; that is design, not a cut. |
| CP-j | rope-bridge post foot / path | PASS | a grey granite footing (about 10 x 2 px) under the post at x 1920 screen x 50-66, y 183. Grounded. The pergola posts at x 2240 stand on the lawn behind the tuft row, fine. |
| CP-c | tree line and gate feet / lawn, the tuft row | PASS | the 48 px pattern (kit_cp_roots 48 x 5, kit_cp_tufts 240 x 5): bumps of 1 to 3 px in width and height in two shades, no repeat visible at 3x or 6x. At 12x the trunk feet sit in grass, not behind a battlement. Not mechanical any more. |
| CP-n | mid-row lawn up in the trees | PASS (weak) | unchanged: the dash grid is still there behind the leaf front. Note only. |
| all other joins | | PASS | as in round 1; nothing broken by the new rows. Checked: the wet row is not drawn over any lamp, tree, kiosk, bin, pot or step; the steps at x 1280 and x 2880 still land on the paving without a seam; the quay-end ripples still sit at the waterline. |

Checklist for the system: 1 Scale PASS, 2 Layer PASS (greyscale sheets unchanged in the ladder), 3 Outline PASS, 4 Shapes PASS (the lens and the olive wedge gone), 5 Shading PASS, 6 Palette PASS, 7 View PASS, 8 Fit PASS, 9 Read PASS (the quay reads as a quay, the banks as banks).

VERDICT: PASS. Every join seen is grounded. Remaining notes, not fails: the mid-row lawn's dash grid (CP-n); the quay-end reflection is faint.
