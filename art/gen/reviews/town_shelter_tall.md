Reviewer: independent (sonnet)

# Round 2

Asset: town_shelter_tall (140x115), decoration, 2.5 m
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: glints dashed and white, contrast 159 (FIXED: one 2 px diagonal band per pane in a mid glass colour, no lone dashes; asset_qa PASS at the game fade); legs and board moved out (their own files).

1. Scale: PASS - 115 px = 2.5 m, 140 wide; posts 4 px at x0-3, 68-71, 136-139, panes 64 and 64.
2. Layer: FAIL - the poster card in the left pane is (208,193,164): 194 on screen (1,052 px, S7 y240 frame, x about 10 to 40, y 80 to 150), 25 above the old town row (168.5), 44 above the plaster (150). It is the lightest large patch in the back layer, and the shelter is the one piece a child's eye goes to. Glass 143, frame 110 to 127, plaster behind 145 to 150.
3. Outline: PASS - none; frame edges are darker steel shades.
4. Shapes: PASS - symmetric posts and panes, rail rows 101-102, roof rows 0-8; the glint bands are clean 2 px diagonals; 5 lone pixels (0.10 %) are at the band's ends.
5. Shading: PASS - light upper left, one glass colour.
6. Palette: PASS - 10 colours, all in downtown.gpl.
7. View: PASS - front-on, flat roof bar, no top face.
8. Fit: PASS - crisp; the donut poster is a clean print with no letters.
9. Read: PASS - a tram stop shelter. Caution: the flat roof bar (x2014-2154, y299-307) still looks like a ledge; it is out of reach of the board (77 px up).

Fix list: dim the poster card to about 150 (card colour 170 to 175 raw instead of 208).

VERDICT: FAIL (1 item)


# Round 3

Reviewed bca1ab9 against c3cb066 with 36 fresh frames (18 camera x at y 120 and 240), pixel diff of every file, luma by colour on the frames, asset_qa at the game fade.

Changed: poster card and glint colours (1,317 px).
1. Scale: PASS - 115 px.
2. Layer: PASS - poster card (160,148,135) = 150.1 on screen (round 2: 194), plaster 145 to 156, old town row 168.5; no back pixel group above the far row.
3. Outline: PASS - none.
4. Shapes: PASS - posts, panes and bands unchanged; 5 lone pixels (0.10 %).
5. Shading: PASS.
6. Palette: PASS - 0 outside downtown.gpl.
7. View: PASS.
8. Fit: PASS - crisp.
9. Read: PASS - a shelter; the poster no longer pulls the eye.

VERDICT: PASS
