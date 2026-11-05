# Review gate 8: cp_mid_maple.png (young mid tree, 72x139) - 5 Nov 2026, independent reviewer

1. Scale: PASS. 139 tall, trunk 6-8 px, crown 71 wide.
2. Layer: PASS. On screen the mid layer measures median 154, p10 131, min 116 (screens 5-9, y144): below the tree line (175-181), above the back (132-135). Maple colours (#df4a0a, #f27116, luma 111-141) are darker than the tree line, which is right.
3. Outline: PASS (with note). asset_qa decor-ink WARN 39 %: a dark maroon #471616 (luma 36, 14.5 % of the art) rims the lower left, bottom and right of the crown, file blotches (49,39)-(72,65), (13,62)-(38,86), (2,51)-(18,76), (40,68)-(64,86). It is a darker shade of the crown's own red, not neutral ink, and at the mid fade it lands at luma 116+, so it is a rim, not an outline. Keep an eye on it.
4. Shapes: PASS. Straight trunk, oval crown, trunk 6 px wide, widening to 7-8 below y 114 and 12 at the foot.
5. Shading: FAIL. 119 lone pixels (2.3 %, above rw_lime 1.6 % and above the other two mids): dark specks scattered through the top of the crown, clusters at (24-29,3-5), (46-48,3-4), (28-29,4-5), plus loose dark dots inside the orange. The crown reads as mottled and the right side is a large dark blotch mass instead of a ramp. One stray dark pixel in the trunk at (36,113).
6. Palette: PASS. 8 colours.
7. View: PASS.
8. Fit: PASS at 1x (specks soften with the fade), WARN at 3x.
9. Read: PASS. A bright red-orange tree, cute.

VERDICT (round 1): FAIL (1 items)

## Round 2 (fix 02fd5cb, fresh frames /tmp/review_cp/r2)

5. Shading: PASS now. Lone pixels 119 to 51 (1.0 %, below rw_lime's 1.6 %); the dark #471616 mass is 6.8 % of the art (was 14.5 %), the large blotch gone. 8 colours, still decor-ink WARN 38 % (a red shade rim, on screen min 116).
Nothing broken: crown still reads, no merged islands, trunk 6-7 px unchanged. Maple highlight #f27116 is luma 141, under the city. Items 1-4, 6-9 PASS as in round 1.

VERDICT: PASS
