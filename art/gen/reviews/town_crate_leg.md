Reviewer: independent (sonnet)

# Round 2

Asset: town_crate_leg (18x37), two bread crates end-on under the board, at x2047-2064 and x2103-2120 (and x3235-3252, x3291-3308), y387-423
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: 14 px crates, no outline (FIXED: two whole crates, 17 px high, 18 px pitch, outlined, play pieces).

1. Scale: PASS - 17 px per crate = the gate crates; end-on width 16; stack 37 = from the board's underside (386) to the street (423).
2. Layer: PASS - 104 on screen against the wall 150.
3. Outline: PASS - rows 0, 18, 36 and columns 0, 17, one ink.
4. Shapes: PASS - the two crates are pixel-identical; 0 lone pixels.
5. Shading: PASS.
6. Palette: PASS - 9 colours in downtown.gpl.
7. View: PASS - end-on front.
8. Fit: PASS - same wood and bread as the gate crates; the board sits flush on their tops.
9. Read: PASS - stacks of crates holding a plank.
Note: the legs are not solid boxes (only the board is); Pepper can walk through them. Same as before.

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
