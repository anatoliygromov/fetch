Reviewer: independent gate-8 art reviewer (Claude, did not make this), 7 Nov 2026
Branch day/07nov-ground at fc03880, worktree review-ground07. Frames: the River Walk sweep (LOOK_SWEEP=1 LOOK_STEP=320), the start screen at 3x, the kennel at 6x and 12x, Pepper on the roof at 8x with LOOK_XS=0 LOOK_YS=0 LOOK_PX=16/22/30, the file at 10x. asset_qa: PASS (44x44, play).

# Round 1 (reviewer, 7 Nov)

## kennel (art/scene/kennel.png, 44x44, play, x 0-44, y 140-184)

Numbers: eave to ground 44 px (0.96 m), width 44 px, door opening 17 x 19 px (0.37 x 0.41 m), ridge 4 px wide at y 140, roof pitch 1 in 2 (2 px per row). Pepper: 34 px high at the head, about 25 px at the shoulder, paws about 26 px apart.

1. Scale: PASS with a note. The house is a Labrador's kennel at 46 px/m. The door opening is 19 px (0.41 m); her shoulder is at 25 px, so she could not walk in without crouching. The crawl is the designed way in, so this is a note, not a FAIL. Fix if wanted: a door 22 x 24 px (crown at y 160), the plate moved up 2 px.
2. Layer: PASS. Play values, outline ink, reads darker than the house and the lawn behind.
3. Outline: PASS. One unbroken 1 px ink round the walls, roof and eaves.
4. Shapes: PASS. Even 2 px roof steps, straight planks, a round door crown with a 2 px cream arch, eaves 2 px past the walls.
5. Shading: PASS. Red in 3 shades (plank lines every 3 px), slate in 2, light from the upper left on the left eave. No specks.
6. Palette: PASS (11 colours, the River Walk ramps).
7. View: PASS. Gable end front-on, the roof a thin cap, no sides.
8. Fit: PASS. Beside the approved bench at 3x it is as crisp; the pickets and lawn under both are one piece.
9. Read: PASS. A child says "dog house" at 1x. Cute.
10. Off the street: PASS. It stands on the lawn of the front garden (x 0-184, y 172-184) behind a white picket edging, with the paved door path at x 42-84. Not on the paving, not on the road.
11. Nothing floats, Pepper on the roof peak: FAIL. Measured on the frames: with her centre at x 22 (on the peak box x 16-28) her back paws hang 5 to 7 px over the left slope and her front paws 5 to 6 px over the right slope; at x 16 the back paws hang 6 to 9 px; at x 30 the front paws 4 to 9 px. The maker's "about 3 px" is the gap at the peak box's own edges (x 16 and 28, 2 px), not under her paws. At 1x the gap under the hind paws is a visible sliver of yellow wall between her and the roof: the owner would call this floating. The cause is a 4 px ridge on a 1 in 2 pitch; any dog 40 px long must straddle the slopes.
    Fix (pick one, the first is best): (a) a flat ridge board: make rows 0 to 3 of the roof a level 24 px cap (x 10-33) so the paws land on a flat, keep the eaves box; (b) lower the pitch to 1 in 3 so the drop under her paws is 2 to 3 px; (c) drop the peak box to y 142 so her paws sink 2 px into the ridge (hides her toes, worst).
12. Placement: note. The left eave is on the level's x 0, which is the screen edge at the start camera. It is whole, but with nothing to its left it reads as pinned to the frame. 4 px of lawn to its left would help if the box and the secret can move with it.

VERDICT: FAIL on one item (11, she floats on the peak). Everything else is finished work.

## The front garden (Sc.paintGarden: lawn x 0-184, path x 42-84, pickets)
- Lawn / paved path: PASS, grass blades over the path's edges at x 42 and 84.
- Lawn / kerb: PASS, the pickets stand on the kerb row, the grass shows between the pales.
- Kennel foot / lawn: PASS, blades over its lower right corner; the left corner is at the screen edge.
- Bench legs / lawn: PASS, the legs go into the grass behind the pickets.
- House plinth / lawn and path: PASS, the plinth band sits on the ground with a 2 px shade.
- Note for the owner's question 2: the public bench stands inside her picket garden. It reads fine; whether a street bench belongs in a front garden is the owner's call.

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-ground at f1bd7ca. Re-rendered the start screen and Pepper on the roof at x 16, 22 and 30 (LOOK_XS=0 LOOK_YS=0 LOOK_PX), gaps measured per column against the frame without her. asset_qa PASS.

Roof now: a level 32 px board (x 6-37) three rows deep, then a 1 in 2 chamfer to the eaves over three rows; the whole roof is 6 rows (y 140-145) and the red wall grew from 30 to 38 rows.

- Paw gaps measured: x 22: 2 to 4 px under the heel of the hind paw only (columns 3-5), 0 under everything else. x 16: 3 to 4 px under columns 0-3, 1 under 4-5. x 30: 1 to 4 px under columns 38-43. At 1x that is a 2 to 3 px sliver under the outer edge of one paw at the chamfers, and nothing when she stands anywhere on the board. Float: PASS. The maker's reason for 32 over 24 holds (at 24 the paws reached the chamfer).
- Read as a classic dog house: FAIL. The gable is gone. With a 32 px flat top on a 44 px box the roof is a dark lid with two tiny corner cuts: at 1x and 3x the piece reads as a red chest, a post box or a pedestal with a round hatch, not a dog house. The taller plain wall makes it boxier still. The owner called the last kennel "weird"; this one is clean but it is a box with a lid, and Pepper standing on it reads as a dog on a crate. The round door and plate carry the "dog house" read alone.
- Everything else (crisp, ink, colours, scale, garden, off the street): PASS as in round 1.

Fix: keep a visible pitch and a shorter flat. A 20 px ridge board (x 12-31, 2 rows) on a 1 in 4 pitch (4 px per row, 3 rows to the eaves at x 0-43), eaves 2 px past the walls, roof 6 rows tall as now, wall back to 30 rows. Gaps then: under the hind paw at x 3 about 2 px (9 px from the board's end at 1 in 4), under columns 5-9 about 1 px: no sliver. The silhouette is a low gable, which is still a dog house. If the owner prefers the gable of round 1 with the 2 to 3 px slivers, that is his call (his question 3).

Not done, accepted: 4 px of lawn left of the kennel. With the left eave on the frame edge it reads pinned but whole; acceptable, since moving it breaks the frozen start trace.

VERDICT: FAIL on read (a box, not a dog house). Float fixed.
