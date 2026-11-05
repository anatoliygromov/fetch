Reviewer: independent (sonnet)

# Round 2

Asset: town_crates70 (71x37), the GATE perch at x1867-1938, y387-423 (box x1868-1938, y388-424)
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: as light as the wall (FIXED: crate wood 107, shade 81, bread 128; wall 150, apple crates 111), sizes 35, 32 and 14 (FIXED: one crate, 34x17 front-on, 18 px pitch; the 96 stack is deleted).

1. Scale: PASS - stack 37 px incl. top outline = the box 36; crate 17 px (0.37 m), loaves 3 per crate; same height as the shelter's end-on crates.
2. Layer: PASS - median 106.9 on screen (S7 y240 x128-200), against plaster 150 and apple crates 111; Pepper's dark 14 to 24 stays the darkest; the perch is 44 under the wall.
3. Outline: PASS - 1 px ink rows 0, 18, 36 and columns 0, 35, 70, one colour (18,18,26).
4. Shapes: PASS - all four crates pixel-identical (0 px differ), slats straight, loaves even; 0 lone pixels.
5. Shading: PASS - 3-shade wood, light upper left.
6. Palette: PASS - 9 colours, all in downtown.gpl.
7. View: PASS - front-on.
8. Fit: PASS - 0.00 % lone pixels; as crisp as the apple crates; same outline convention as the other play props; the rider now passes in front of it (perches drawn before the bikes).
9. Read: PASS - bread crates, clearly a perch. Only the GATE at x1868-1938 uses it; the one at x3072-3168 keeps the old brick gate.

VERDICT: PASS


# Round 3

Reviewed bca1ab9 against c3cb066 with 36 fresh frames (18 camera x at y 120 and 240), pixel diff of every file, luma by colour on the frames, asset_qa at the game fade.

Unchanged since round 2: 0 px differ against c3cb066, and the draw code for it is unchanged.
1. Scale: PASS (unchanged).
2. Layer: PASS (unchanged; perch values 104 to 107, portal top 104, wall 150).
3. Outline: PASS (unchanged).
4. Shapes: PASS (unchanged).
5. Shading: PASS (unchanged).
6. Palette: PASS (unchanged).
7. View: PASS (unchanged).
8. Fit: PASS (unchanged; the portal top's 11 step tops still equal the boxes).
9. Read: PASS (unchanged).

VERDICT: PASS
