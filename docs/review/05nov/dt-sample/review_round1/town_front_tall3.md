Reviewer: independent agent (gate 8), 5 Nov 2026, art/dt-sample-05nov. Judged from the PNG at 5x, numpy, asset_qa and the frames in /tmp/review_dt/frames (tools/dt_sample_frames.sh, 11 screens x camera y 120 and 240). Script PASS not taken as a pass.

Asset: town_front_tall1 (80x432), town_front_tall2 (88x432), town_front_tall3 (96x432). Same findings for all three; this file covers all three.

1. Scale: PASS - Door body 93 px (2.0 m), 108 px with lintel and step; storey pitch 144 px (3.1 m); window 58x87. Top at game y -18 (never on screen, rows 0-18 plain plaster).
2. Layer: FAIL - On screen the plaster is 179.5 (cream/orange) and 154 (salmon); the old town row behind it is 168 (S10 y240, x2880 frame, x0-130) and far roofs 169. Back is lighter than the far layers (ladder: far > back). The builder's README admits "back 169-179" and leaves out the far rows. Plan target was 154.
3. Outline: PASS - none, alpha 255 everywhere, edge = darker plaster/stone shade, right edge 2 px shade.
4. Shapes: FAIL - the string courses are not the same part. Rows 136-139 (game y 118-121): 4 rows, no shade. Rows 280-284 + 285-286 (game y 262-268): 5 rows plus 2 rows of wall shade (176,128,80). Window pitch is 140 (rows 19 and 159) but the courses are 144 apart, so the course sits 31 px under the upper window and 35 px under the lower one. Windows themselves are pixel-identical (storeys and all three files, 0 differing px), centred on the house, 9 equal panes, flat wall. The top course (game y 118) is seen at camera y below about 112 (high road).
5. Shading: PASS - one ramp per material, light upper left, shadows down and right.
6. Palette: PASS - 11 to 12 colours, all in art/palettes/downtown.gpl. (That palette was built from these pieces in this branch, so this is circular.)
7. View: PASS - front-on, flat elevation, no tops or sides.
8. Fit: PASS - 0 lone pixels, 0.00 %. As crisp as rw_home but plainer: one window and one door per bay, no lantern, pipe or sill detail. Acceptable for a back layer.
9. Read: PASS - friendly town fronts; no text.

Fix list: draw one string course part (same rows, same shade) and place it at the window pitch (140) or move the windows to 144; darken the plaster ramp so on-screen plaster sits under the old town row (about 154 on screen).

VERDICT: FAIL (2 items)
