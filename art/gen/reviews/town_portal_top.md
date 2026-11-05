Reviewer: independent (sonnet)

# Round 2

Asset: town_portal_top (122x50), the guild house's stepped gable as a portal top: 11 play steps GUILD ROOF x1560-1680, drawn at (1559, 243)
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

New in round 1 (replaces town_roof_gable in this level).

1. Scale: PASS - 122x50; all 11 steps checked against the boxes: the first opaque row of each step is the box top minus 1 (outline) at x1560 y271 down to the plateau x1616-1656 y243, then back down to x1672 y255; step width 8, rise 4, as the boxes. Nothing Pepper stands on moved. The art hangs to y293, 15 px below the lowest box (y278), which is a front, not a perch.
2. Layer: PASS - median 103.6 on screen (S6 y240, x1560-1680), the guild wall 145 to 150; outline 14.5; a play piece darker than the back by 45.
3. Outline: PASS - unbroken 1 px ink (asset_qa PASS as play; its WARN "decoration outlined" appears only when tested as back, wrong layer).
4. Shapes: PASS - brick courses straight and level, steps even, 0 lone pixels, 7 colours.
5. Shading: PASS - light upper left, one shade row under each course.
6. Palette: PASS - all 7 colours in downtown.gpl.
7. View: PASS - a flat front with a stepped silhouette; no top face, no side.
8. Fit: PASS - crisp as the other fronts; the medallion is an 8x8 round with a ring, clean, orange-brown (157,90,37), 104 on screen, not gold, so it cannot be mistaken for the golden bone (246,207,79, 204).
9. Read: PASS - a brick stepped pediment over the guild gate. Notes: it is 122 wide over a 48 px door, and from the street the door is covered by the iron balcony (x1552-1608, y344) and the plaza houses, so the pediment reads as a hat over a wall; it is the heaviest dark mass on the high road. Owner call.

VERDICT: PASS
