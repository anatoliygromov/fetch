Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), rounds 1-3, 5 Nov 2026

# Review gate 8: cp_mid_lime.png (young mid tree, 80x139) - 5 Nov 2026, independent reviewer

1. Scale: PASS. 139 px tall (spec 138), trunk 6-8 px (spec 6), crown 80 px (3.5 m) over 90 rows. Pepper at the mid scale is 13 px; tree is 10.7 Pepper-heights, right for a 6 m tree.
2. Layer: PASS. On screen (mid at fade 0.48) mid median 154, p10 131 across screens 5-9 at y144; order sky 202 > city 190 > tree line 175-181 > mid 154 > back 132-135 > play holds. Highlight #fcc23e reaches about 180, same as the tree line's p90: acceptable. Not lighter than the city.
3. Outline: PASS. Edge luma 126 equals interior 126; 10 % of edge below 60. No ink edge.
4. Shapes: PASS. A lollipop crown on a straight trunk with a small flare; trunk rows 90-138 is clean (no lone pixels).
5. Shading: PASS. 88 lone pixels (1.4 %), at the approved rw_lime's level (1.6 %); they sit on the crown edge, e.g. (15,7), (15-16,11-12), (10,12), (57-59,7-8), and are invisible after the fade at 1x. 8 colours.
6. Palette: PASS.
7. View: PASS.
8. Fit: PASS. Reads as a young tree behind the park, same density as the tree line art; 3 mid designs repeat in a fixed lime, maple, birch cycle, so one design recurs every 3rd tree (100-260 px apart): never twice in one frame.
9. Read: PASS. Note the crown is gold, not green, like the rest of the autumn park.

Task checks (7): the far city is visible between these trees, not above them: tree top is at screen y 42, city top at about y 73. That follows from the plan's 138 px and is not a defect of this file.

VERDICT (round 1): PASS

## Round 2 (fix 02fd5cb; file unchanged)

New finding, present in round 1 and missed there: the mid layer's brightest pixels are lighter than the far city. On screen the crown highlights #fcc23e (12.5 % of this art) are (255,202,65) and (255,202,88), luma 196-202; 3320 mid pixels at 196 or over across screens 5-9 (mid p99 204), against city max 195 and median 190, tree line p99 198. Median order still holds (mid 154 against city 190).

2. Layer: FAIL (minor). Lower the #fcc23e highlight to about luma 170-175 on screen (raw about 150-155).
All other items unchanged: PASS (1, 3-9).

VERDICT: FAIL (1 items)

# Round 3 (dc2b405; highlights lowered)

2. Layer: PASS. Highlight #fcc23e became #d8941c (luma 154 raw). On screen the mid layer is p10 131, median 154, p90 174, p99 184, max 184 (screens 5-9): below the city (190-195), the tree line (175-181 median) and the sky. Round 2 fault fixed.
5. Shading: PASS (with note). The edit merged the two mid tones: #a95906 is now 68.9 % of the art, with thin curved highlight strokes (#d8941c, 12.5 %). At 5x it reads as a flat brown blob; at 1x in the game (mid fade 48 %) it reads as a textured golden tree. Lone 1.13 %.
Other items unchanged: 1 scale PASS (139 tall, trunk 6), 3 outline PASS, 4 shapes PASS, 6 palette PASS (7 colours), 7 view PASS, 8 fit PASS, 9 read PASS.

VERDICT: PASS
