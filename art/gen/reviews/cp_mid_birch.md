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

VERDICT: FAIL (1 items)
