Reviewer: independent (sonnet)

# Round 2

Asset: town_gateway (80x138), 3 m arch in a house's ground floor, decoration, drawn at the bay centre of x1912-2000 (centre 1956, x1916-1996)
Method: PNG at 5x to 8x, numpy, asset_qa (now at the game fade), fresh frames of 18 camera x positions at y 120 and 240 (tools/dt_sample_frames.sh at 0c95386), colour luma Rec.601 on the frames, a bike injected into a copy of the repo for the rider checks.

Round 1 findings: block across a seam (FIXED: no wall of its own, inside one house), stone lighter than far (FIXED: stone 148 to 166 on screen, interior 111), colours not in palette (FIXED: all 12 in downtown.gpl), alone on screen 10 (FIXED: no gateway where no house).

1. Scale: PASS - 138 px = 3.0 m; piers 8 px, opening 64 px, keystone 8 px above the arch.
2. Layer: PASS - piers and voussoirs (158,145,136) 148, (176,164,150) 166, interior (120,106,117) 111; old town row 168.5; house plaster beside it 150.
3. Outline: PASS - none; edges darker stone.
4. Shapes: PASS - jamb courses identical both sides, keystone centred, arch even steps; mirror differences are the light side only. 33 lone pixels = 0.34 %, under 2 %.
5. Shading: PASS - light upper left; one shade band inside.
6. Palette: PASS - 12 colours, all in downtown.gpl.
7. View: PASS - front-on.
8. Fit: PASS - sits in the house with 4 px of plaster each side, the seams at x1912 and x2000 clean; the crates stand to its left (x1867-1938). The courtyard cream block with one window and hedge reads as a house far back.
9. Read: PASS - a courtyard archway. Not a perch: the pier tops (x1916-1924 and 1988-1996, 108 px up) are flat but out of reach.
Context (screen file): the street lamp at x1958 stands in the middle of the passage.

VERDICT: PASS
