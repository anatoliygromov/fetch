Reviewer: independent (sonnet)

# Round 2

Asset: town_front_tall1 (80x432), town_front_tall2 (88x432), town_front_tall3 (96x432); the same text in all three files
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: string courses unequal and 144 apart (FIXED: rows 0-4 and 7-144 bands, the course is identical at rows 0, 140 and 280, 0 px differ, pitch 140 equals the window pitch); plaster lighter than the far layers (FIXED: on screen 145 to 156 against the old town row 168.5 and far roofs 169).

1. Scale: PASS - Door 93 px body (2.0 m), storey 140 px, window 58x87 (all unchanged); the top is at game y -18 (rows 0-4 are the top course, never on screen).
2. Layer: PASS - plaster on screen 145.4 (red), 147.9 (stone), 150.5, 152.2 (ochre), 156 (cream); old town row 168.5, far roofs 169, so far > back holds in every house colour. Window panes 124.5, frames and sills 171 (a few px lines, 2.5 above the far row; accepted). Pane against plaster is 21 to 31 now (was 55): windows read as flat grey but are still clear.
3. Outline: PASS - none, alpha 255 everywhere, edges are darker plaster or stone shades.
4. Shapes: PASS - windows pixel-identical on both storeys and across all three files (0 px differ); courses identical (see above); 9 equal panes; flat wall; 0 lone pixels in the file.
5. Shading: PASS - one ramp per material, light upper left, drop shadow down and right.
6. Palette: PASS - 11 to 12 colours, all in art/palettes/downtown.gpl (that palette is built from these pieces, so this is by construction). The other house plasters are swapped at draw time (arthooks H.PLASTER), not in the file.
7. View: PASS - front-on elevation, no tops, sides or insides.
8. Fit: PASS - as crisp as rw_home, plainer; 0.00 % lone pixels.
9. Read: PASS - friendly town fronts, no text. Note: with every plaster at 145 to 156 the street is a calm, somewhat drab brown and rose; board call.

VERDICT: PASS


# Round 3

Reviewed bca1ab9 against c3cb066 with 36 fresh frames (18 camera x at y 120 and 240), pixel diff of every file, luma by colour on the frames, asset_qa at the game fade.

Changed since round 2: only the pane colours (raw (62,72,88) to (31,37,45) and its shade), 4,752 to 7,272 px per file; everything else 0 px.
1. Scale: PASS - unchanged (door 93, storey 140, window 58x87).
2. Layer: PASS - panes now 99.9 on screen, plaster 145 to 156, frames 171, old town row 168.5. Pane against plaster 46 to 56 (round 2: 21 to 31), the back layer's range in the S7 frame is 100 to 171, within the limit of 120.
3. Outline: PASS - none, alpha 255.
4. Shapes: PASS - windows pixel-identical on both storeys and equal to the other fronts and to the guild front's windows (0 px differ); courses identical at rows 0, 140, 280; 0 lone pixels; the darker panes did not break the crisp grid (9 equal panes, bars unbroken).
5. Shading: PASS.
6. Palette: PASS - 0 colours outside downtown.gpl.
7. View: PASS - front-on.
8. Fit: PASS - 0.00 % lone pixels, crisp.
9. Read: PASS - windows now read as glass again.

VERDICT: PASS
