Reviewer: independent (sonnet)

# Round 2

Asset: town_oriel (18x45), the guild house's bay window, replaces the chimney: box CHIMNEY x1628-1644, y200-244 (solid), drawn at (1627, 199); the golden bone box x1628-1644, y188-200
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

New in round 1.

1. Scale: FAIL - the window is 11 px wide in an 18 px piece, a fifth of the 58x87 windows of the same house (1.0 m tall bay, 0.39 m wide; a bay window is about 1.5 m wide). It reads as a chimney with a small window. The box is fixed by the level (16 wide), so the piece cannot grow unless the bay wall is drawn wider behind it as decoration.
2. Layer: FAIL - body fill (180,143,112) = 150.5 on screen, the plaster of the wall it stands on, 150.5; the copper roof, the perch with the golden bone, is 145.4. Only the outline separates the perch from the wall (the portal top below it is 104; apple crates 111).
3. Outline: PASS - unbroken 1 px ink (asset_qa PASS as play).
4. Shapes: PASS - frame, two panes, three corbel rows; straight; 0 lone pixels.
5. Shading: PASS - light upper left; a 2 px shaded right side.
6. Palette: PASS - 9 colours, all in downtown.gpl.
7. View: PASS - front-on with a thin roof cap and a shaded side strip of 2 px (acceptable).
8. Fit: PASS - sits exactly on the portal top's plateau (y243), box and art aligned; the golden bone is where it was, 12 px over the roof top at y200 (level unchanged).
9. Read: FAIL - from the street and from the high road it reads as the old chimney with a window in it, a small turret standing on the gable; the 1a pick asked for a bay window's roof.

Fix list: darken the body to about 110 on screen; draw the bay wide behind the box (decoration, about 60 px, windows 58 wide in the house's grid) with the box as its roof's perch.

VERDICT: FAIL (3 items)
