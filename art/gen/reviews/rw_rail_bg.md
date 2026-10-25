Reviewer: independent agent (sonnet), 25 Oct, round 2
1. Scale: PASS - Unchanged: 50 px tall (1.09 m at 46 px a metre), pieces 5, 84, 86 wide, drawn at y 124-173 on the pavement's back edge, 22 px above Pepper's head top and 10 px behind her line; it does not cover her.
2. Layer: PASS - asset_qa (fade 0.28): p10 119, median 135, contrast 30, unchanged; lighter than the lamp post and the lime trunk in front, a quiet band in the greyscale frames.
3. Outline: PASS - No ink: the darkest of its 4 colours is (49,64,88). asset_qa's "49 % dark edge" warning is the false alarm of 1-5 px tubes where every pixel is an edge; the lamp post it copies is 100 % and approved. Tubes are lit on the top row and shaded on the bottom row, posts lit left and shaded right.
4. Shapes: PASS - Verified from the pieces: alpha binary, 4 colours, 0.0 % lone pixels, straight tubes, even 3 px posts. The collars are now drawn as 5 px wide, 5 row rings (hi top, li, sh bottom) around each lower tube at every post (4x crop of the assembled sample); they read as clamps, no jaggies. One open irregularity from round 1: the last span is still 86 px against 84 (the end piece's post is at x 82 of 86).
5. Shading: PASS - Four shades, round handrail as hi, li, li, mid, sh, light from the upper left. The post middle column is now 'li' (69,88,112), so posts read as three distinct columns (88,109,134), (69,88,112), (49,64,88) instead of two.
6. Palette: PASS - The four colours are the lamp post's own ironwork ramp, which riverwalk.gpl v2 holds (4 of 4); the ramp is sound (navy iron, lit to shaded, no new hue) and belongs with the level. Conditional on the owner's board approve like the other two. The dark is navy rather than neutral, as on the lamp.
7. View: PASS - Front-on, flat tubes and posts, foot plates on the ground line; no top or inside.
8. Fit: PASS - In the regenerated frames at 1x and 3x it reads as a quay railing behind the trunk, bench and planter and is plainly not the obstacle fence (28 px, balusters, 1 px outline, near-black). The collars add the small ironwork detail the lamp post has. It is still the sparsest piece, but on the crispness bar.
9. Read: PASS - Reads as a plain tube railing at 1x, not the fence she climbs; no text.

Fix list:
- Last span: put the end piece's post at x 80 (3 px tail, still 86 wide) so every span is 84; today the final span is 86.
- Length: Sc.railing places floor((w - 91) / 84) units, so the railing stops 5 px short of its prop at x 184-1288 (ends at 1283) and 67 px short at x 2880-3626 (ends at 3559, a visible gap before the gable); the script docstring still says every railing keeps its length. Pre-existing, not from this piece, but a half unit or a stretched end piece would fix it.
- The unused 'dk' (15,21,40) remains in the script's colour table: delete it.
- The assembled sample (art/source/rw_rail_bg_assembled.png) is 343 px (left + 3 units + end); show 5 units in the review card so the collars and the last span can be judged in one image.
- asset_qa will keep warning decor-ink at about 50 %: add the rail to the owner-approved exceptions the way the lamp post is.
