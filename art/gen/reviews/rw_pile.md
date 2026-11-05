# Gate 6 review: rw_pile (riverwalk/art/scene/pile.png, 18 x 182, front layer), 5 Nov 2026

Reviewer: independent. Method: 5x and 20x enlargements, numpy luma and colour counts, rows and columns, in-game frames, level diff.
Script: `asset_qa.py --file pile.png --layer front --level rw` PASS (8 colours, on screen median 30, darkest 11).

Placement (riverwalk.lua, unchanged in this diff): three props, tops at y 221, 225, 221; the screen ends at y 240, so only the top 19 px (15 px for the second) is ever
drawn. Rows 0-18 contain: the rim (rows 0-1), the domed top, the first lashing band (rows 8-13). The second band (rows 70-75) and the rest are never on screen.

## asset_qa.md checklist (9)
1. Repeated parts the same: PASS for what shows. The two lashing bands are not byte-identical: the 1 px diagonal checker is phase-shifted by one column between row 9-12 and rows 71-74 (the second band is below y 240 and never drawn). Nit only: align the phase if the file is touched again.
2. Round and symmetric: PASS. Body cols 1-16 with a 1 px dark rim, band cols 0-17 (1 px lashing bulge each side), top corner steps 3 px (row 0 cols 4-13, row 1 cols 1-16). Light left, dark right, as a round post should shade.
3. Light direction, ramps, no dabs: PASS. Columns left to right: #282a36 (3 px), #21273a, #17181f (3 px), edge #050a17. Dark vertical grain lines are 1 px, long, on the same ramp. No dabs.
4. Outline 1 px, one ink: PASS (front layer: dark silhouette edge #050a17, 1 px, no lone breaks; not an obstacle).
5. Faces: N/A.
6. Scale / slot: PASS. 18 x 182 OK; 18 px at the front layer's about 60 px/m is a 0.3 m mooring post, believable.
7. Mirrored: N/A (not flipped).
8. In game: PASS. In ingame_pile_quay_1x and the pontoon frames the piles show as dark posts with one lashing band at the bottom edge; they never cover Pepper (tops y 221 and 225, lowest line she stands on is 216).
9. Next to bench, bin, lamp: PASS. Same pixel size, clean, no semi-alpha; as a front-layer silhouette it is meant to be simple, and it has a rim, grain and a lashing, so it is not plain.

## rules.json review_checklist (9)
- Scale: PASS. Layer: PASS, file median luma 39.4 (limit 40), on screen as drawn 30 (visible part rows 0-18: median 28), darkest 11, contrast 40 or less; darker than the ferry (play, median 128): ladder order holds.
- Outline: PASS (dark silhouette, no light outline). Shapes: PASS. Shading: PASS (thin rim of #5f7387 on the top 2 rows, 3 columns of shade; the 28 #44423a lashing pixels are the rope twist, deliberate). Palette: PASS (8 colours, all in riverwalk.gpl; the navy is a palette dark). View: PASS (front-on post and a thin dome cap). Fit: PASS (front layer, not compared with play props). Read: PASS (reads as a harbour post at 1x; the rope band is legible).

## Notes
- Median luma 39.4 is 0.6 under the limit. Do not lighten the rim or add colours without re-measuring.
- Rim light: only 10 px wide on row 0 and 8 on row 1, fine at 1x; no change needed.

VERDICT: PASS
