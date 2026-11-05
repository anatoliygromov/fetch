Reviewer: independent (sonnet)

# Round 2

Asset: town_breadboard (74x12), the SHELTER perch (box x2048-2120, y376; x3236-3308), drawn at y375
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: median 179, equal to the wall (FIXED: planks 104 to 128 on screen); thickness now 12 rows, two planks.

1. Scale: PASS - 74 on a 72 box, 12 thick (0.26 m), top 48 px above the street as before; legs begin at y387, directly under its last row (386). Pepper's feet land on the first light row (y376).
2. Layer: PASS - 104 to 128 on screen against the wall 150; outline 14.
3. Outline: FAIL - one pixel of the outline is gone: at x73, y8 (right end, third plank row) the ink (18,18,26) is replaced by plank shade (104,78,48), a 1 px notch in the end of the board. The rest of the outline is closed (rows 0 and 11, columns 0 and 73).
4. Shapes: PASS - seven nail marks, even, straight; two plank seams level.
5. Shading: PASS - two planks, light top row on each, shade row under each.
6. Palette: PASS - 4 colours in downtown.gpl.
7. View: PASS - front-on edge.
8. Fit: PASS - 1 lone pixel (the notch above), 0.11 %; the rider now passes in front of it, uncut (checked with a bike at x2090 and x3250).
9. Read: PASS - a baker's plank on bread crates, clearly something to stand on.

Fix list: paint (73,8) ink.

VERDICT: FAIL (1 item)
