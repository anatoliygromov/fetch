Reviewer: independent (sonnet), did not build this piece. File: rw_gable_bay.png (80x180), art for GABLE x3636-3716, y0 -6.

# Round 1 (05 Nov, screen 12 street, branch art/rw-street-05nov)
Judged from the PNG, the level code and fresh --lookshots frames (bay, bench, river view), plus a greyscale copy. asset_qa --layer back --level rw --fade 0.28 --building: PASS, 20 colours, alpha 255. Columns 10-79 are byte-identical to the previously approved rw_gable.png columns 78-147 (0 px differ); columns 0-9 are new.
1. Scale: PASS - door leaf, transom and storeys match rw_home and the cafe at 46 px/m; Pepper (51 px) and Mia (about 59 px) read correctly against the door.
2. Layer: PASS (note) - p10 139, median 191, p90 218. Darkest keeps the ladder order against the far city and far shore; median is lighter than the far city, the documented River Walk back-row exception, and below approved rw_home (208). In greyscale it sits between the home and the cafe, clearly in front of the far layers.
3. Outline: PASS - decoration, no outline; edges are darker shades of their own colour.
4. Shapes: PASS - the left corner pilaster (cols 0-9: col 0 light edge, cols 1-6 mid, cols 7-9 shade) is flat and straight, runs full height with the granite socle at the foot, and meets the wall without a stub or cut anchor. Windows and door parts repeat identically. Lone pixels 65 (0.45 %), all glint diagonals.
5. Shading: PASS - pilaster lit from the left, shade to the right, matching the rest of the front.
6. Palette: PASS - 20 colours, same wall (234,162,100) and granite (210,206,192) as the street family.
7. View: PASS - flat front, top at y -6, never on screen (check_backdrop OK).
8. Fit: PASS - the pilaster closes the left side, so only the door bay shows (option B) and the river view stays 116 px; the right edge joins the cafe at x 3716 with no seam. No sill stubs remain.
9. Read: PASS - reads as the end house of the row with its door; the bench and river view in front read clearly.
VERDICT: PASS
