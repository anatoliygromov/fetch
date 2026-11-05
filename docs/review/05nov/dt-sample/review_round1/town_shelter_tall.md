Reviewer: independent agent (gate 8), 5 Nov 2026, art/dt-sample-05nov. Judged from the PNG at 5x, numpy, asset_qa and the frames in /tmp/review_dt/frames (tools/dt_sample_frames.sh, 11 screens x camera y 120 and 240). Script PASS not taken as a pass.

Asset: town_shelter_tall (140x115), decoration on the back line, drawn behind the board and her; tram stop shelter at 2.5 m.

1. Scale: PASS - 115 px = 2.5 m, 140 wide; Pepper stands against a post 26 px at the withers, the board is 48 px up, the roof bar 125 px up.
2. Layer: FAIL - asset_qa WARN: contrast 159 (back allows 120). The cause is the white glints (255) in the glass; on screen (S7 y240) they are the lightest pixels of the back layer (p90 215 against plaster 180) and read as scratches over the door behind. Pane median 154.
3. Outline: PASS - none; frame edges are darker steel shades.
4. Shapes: PASS - posts 4 px at x0-3, 68-71, 136-139, panes 64 and 64 px wide, rail rows 101-102, roof rows 0-8; symmetric. The glints are 1 px dashed diagonals (6 lone pixels at (22,29), (15,49), (14,50), (25,50), (13,51), (26,51)), a warning.
5. Shading: PASS - warning for the glints, see 2.
6. Palette: PASS - 11 colours, all in downtown.gpl.
7. View: PASS - front-on. Roof bar is a flat beam with no top face.
8. Fit: PASS - 0.12 % lone pixels; crisp. The donut poster (left pane) is a clean 3-colour print with no letters.
9. Read: PASS as a shelter. Caution: the flat grey roof bar (x2014-2154, y299-307) looks like the high road's stone ledges; keep it off Pepper's reach.

Fix list: drop the glints to a mid blue-white or one short stroke per pane.

VERDICT: FAIL (1 item)
