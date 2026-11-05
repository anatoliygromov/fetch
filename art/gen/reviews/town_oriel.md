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


# Round 3

Reviewed bca1ab9 against c3cb066 with 36 fresh frames (18 camera x at y 120 and 240), pixel diff of every file, luma by colour on the frames, asset_qa at the game fade.

Changed: town_oriel is now only the copper roof cap, 60x9, drawn at (box centre - 30, 199), its flat top (14 px of light between the end outlines, row 1) at y200 where the box top is. The bay under it is town_oriel_bay (decoration).
1. Scale: PASS - 60x9; the flat top is the box's 16 px with its outline; the golden bone box (x1628-1644, y188-200) is unmoved, 12 px above the top.
2. Layer: PASS - cap green 112.7 and 87.8 on screen against wall 150.5 (S6 y120).
3. Outline: PASS - unbroken 1 px ink round the whole hip (asset_qa PASS as play).
4. Shapes: PASS - even 4 px steps each side, symmetric; 2 lone pixels (0.53 %) are the eave tips at (0,7) and (59,7).
5. Shading: PASS - light top row, two shades below.
6. Palette: PASS - 4 colours, all in downtown.gpl.
7. View: PASS - a front-on hip profile, no top face.
8. Fit: FAIL - the art is 60 px wide over a 16 px solid box (CHIMNEY x1628-1644, y200-244), and the bay behind it is 58 wide. The solid part is the middle 16 px only: the roof's sloping sides (x1606-1628 and 1644-1666, y200-207) and the bay's face to either side are passable, while a 16 px invisible core stands in the middle of the bay's face down to the plateau (x1616-1656, y244). Pepper walking the plateau is stopped by air at x1628, and can jump up through the roof's slope to land on the 14 px top. A hit box smaller than the art (defect catalogue). The level cannot change.
9. Read: PASS - a copper roof over a bay window; reads as the bay's roof, with the golden bone above.

Fix list: make the solid core read as part of the art (draw a 16 px pilaster or chimney breast in front of the bay's centre, as a play piece with the outline), or narrow the bay and roof to the box (about 16 to 24 px) as in round 2 but at a believable scale.

VERDICT: FAIL (1 item)
