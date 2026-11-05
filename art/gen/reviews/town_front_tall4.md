Reviewer: independent (sonnet)

# Round 2

Asset: town_front_tall4 (148x432), the guild house's own front (box x1552-1700)
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

New in round 1; checked as a new piece.

1. Scale: PASS - same door (arched, 93 px body), windows 58x87, storey 140, course rows 0, 140, 280 identical to the other fronts.
2. Layer: PASS - plaster 150.5 on screen against old town row 168.5; asset_qa PASS at fade 0.28.
3. Outline: PASS - none, alpha 255.
4. Shapes: FAIL - the two windows sit flush against the house edges. Left window starts at x0 (wall margin 0, the other fronts have 12 to 20 px); the right window is placed at x92 and is 58 px wide, so its last two columns (x148, x149) fall outside the 148 px file and its drop shadow and frame edge are cut off: it differs from the left window in 1,938 px (checked with a 2 px shift: 0 differ with the clipped columns removed). On screen the guild house's windows touch the seams to the neighbours at x1552 and x1700, at both storeys (rows 19-105 and 159-245). Courses identical, arch door centred (x73.5 of 148), 0 lone pixels.
5. Shading: PASS - light upper left, same ramps as the other fronts.
6. Palette: PASS - 11 colours, all in downtown.gpl.
7. View: PASS - front-on.
8. Fit: PASS - crisp, 0.00 % lone pixels; the windows' clipping is listed under 4.
9. Read: PASS - a house front with a gate at its foot; the gate is mostly hidden by the iron balcony and the plaza house in front (context, see screen review).

Fix list: move the windows in 16 to 20 px from each edge, window 58 wide with its shadow whole (the front is wide enough: 148 - 2 x 18 = 112 between).

VERDICT: FAIL (1 item)
