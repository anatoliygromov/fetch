Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), rounds 1-3, 5 Nov 2026

# Review gate 8: cp_mid_birch.png (young mid tree, 28x139) - 5 Nov 2026, independent reviewer

1. Scale: PASS. 139 tall, trunk 5 px (spec 6), crown 28 wide (a poplar-like column).
2. Layer: FAIL. The white trunk #cfd5d1 (luma 210; file x 11-15, rows 90-137) measures 216 on screen after the mid fade (screen 6 y144, x 220-225, y 100-170; the pixels are tagged mid). That is lighter than the far city (190-195), the tree line (175-198) and the sky median (202); it is the lightest object in the middle of the picture, a bright pole standing in front of the city. The ladder needs mid darker than tree line darker than city. Fix: grey or warm the trunk to about 150 (the mid median is 154). asset_qa passes it because it only measures p10 and contrast, not the top end.
3. Outline: PASS. Edge luma 151 against interior 138, 9 % dark.
4. Shapes: PASS. A trunk with dark birch marks, a slim crown.
5. Shading: PASS (with note). 52 lone pixels (2.2 %): crown-edge dots, e.g. (17,7), (19,7), (22,8), (8,12), (1,31), and two at the trunk base (8,95), (10,97). They disappear after the fade at 1x.
6. Palette: PASS.
7. View: PASS.
8. Fit: PASS apart from the value fault in item 2.
9. Read: PASS. Cute and clear.

VERDICT (round 1): FAIL (1 items)

## Round 2 (fix 02fd5cb, fresh frames /tmp/review_cp/r2)

2. Layer: FAIL (minor, the trunk is fixed). The trunk is now #706860 (luma 105) with #504a46; on screen 138-156 (screen 6 y144, x 222-223, y 140-160), under the city (190-195) and sky: round 1 defect fixed, the trunk reads as a grey-tan pole now. But the crown highlight #f9c219 (17.9 % of the art) is (255,202,65) on screen, luma 196-202, over the city's max 195 (shared with cp_mid_lime: 3320 mid px at 196+, mid p99 204). Lower it to about 170-175 on screen.
Other items unchanged: PASS. 7 colours; lone 52 (2.2 %), invisible after the fade.

VERDICT: FAIL (1 items)

# Round 3 (dc2b405; highlights lowered)

2. Layer: PASS. Crown highlight #f9c219 became #d4951e (luma 154 raw); on screen the mid layer max is 184 and the trunk 138-156. Round 2 fault fixed.
5. Shading: PASS. Lone 52 (2.2 %), crown-edge dots, invisible after the fade at 1x. 7 colours; the trunk is now a plain grey #706860 with #504a46 marks, a little bland but correct in value.
Other items unchanged: 1 scale PASS (139 tall, trunk 5), 3 outline PASS, 4 shapes PASS, 6 palette PASS, 7 view PASS, 8 fit PASS, 9 read PASS.

VERDICT: PASS
