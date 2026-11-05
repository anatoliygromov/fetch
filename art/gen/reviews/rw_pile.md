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

---

# Round 2 (after fix round 1, commit 6c5a228), 5 Nov 2026

asset_qa PASS. Measured: 18 x 182, 2930 opaque px, 8 colours, no semi-alpha, file median luma 39.4, visible part (rows 0-18 and 0-14) median luma 28, darkest on screen 11. Level file: unchanged since round 1.

The round 1 nit is FIXED: the two lashing bands (rows 8-13 and 70-75) are now byte-identical (checked on all four channels). The rim is two rows (row 0 cols 4-13, row 1 cols 2-9 lit and 10-15 a step darker), unchanged.

## asset_qa.md checklist (9)
1. Repeated parts the same: PASS (both lashing bands identical, same checker phase).
2. Round and symmetric: PASS (body cols 1-16, bands cols 0-17, even 3 px corner steps on the dome).
3. One light direction, ramps, no dabs: PASS (left #282a36, centre #21273a, right #17181f, grain in 1 px lines; the #44423a lashing twist pixels are deliberate).
4. Outline 1 px, one ink: PASS (dark silhouette edge #050a17 at 1 px; no light outline on the front layer).
5. Faces: PASS (not applicable: no characters).
6. Scale and slot: PASS (18 x 182 OK; 0.3 m post at the front layer's 60 px/m).
7. Mirrored: PASS (not applicable: not flipped).
8. In game: PASS (only the top 15-19 px show at the bottom edge, with the first band; tops at y 221 and 225 are below every line Pepper stands on).
9. Next to bench, bin, lamp: PASS (same pixel size, clean, no semi-alpha; a front-layer silhouette with rim, grain and lashing is as dense as it needs to be).

## rules.json review_checklist (9)
- Scale: PASS (slot and size OK).
- Layer: PASS (median luma 39.4 in the file, 28 to 30 on screen, limit 40; darker than the play ferry's 128).
- Outline: PASS (dark silhouette, no light outline).
- Shapes: PASS (round post, even dome).
- Shading: PASS (light left, three columns of shade, thin rim).
- Palette: PASS (8 colours, all in riverwalk.gpl).
- View: PASS (front-on post with a thin cap).
- Fit: PASS (front layer; same pixel size as the approved props).
- Read: PASS (a harbour post with a rope lashing at 1x).

VERDICT: PASS
