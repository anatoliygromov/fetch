Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

# Review gate 8: rw_birch.png (River Walk back layer, 192x250), 6 Nov 2026

Drawn twice, same sprite, not mirrored: x 460 and x 2918 (y0 -76, replaces tree_far). Own frames: /home/claude/rv/x3_sweep_riverwalk_y000_x0300.png and x2800 (in-game, look on, 3x), /home/claude/rv/birch3x.png (file 3x), /home/claude/rv/pep_birch.png (beside Pepper 52x38, 1x). asset_qa WARN decor-ink 44 % only. check_backdrop OK (top at y -76).

Scale at 46 px/m (assumed: a mature silver birch, trunk 0.3-0.4 m, crown 4-6 m): trunk 14-16 px = 0.30-0.35 m; crown 162-192 px = 3.5-4.2 m; lowest leaves 95 px up = 2.1 m; 250 px = 5.4 m of tree on a 174 px ground line. Trunk against Pepper: about her body height. Reads right.

1. Scale: PASS. Numbers above.
2. Layer: FAIL. Highlight #b6d434 (luma 182 raw, 2013 px = 9.1 % of the art) is luma 204 on screen (p99 204 and max 204 in frames x300 and x2800, the leaf-green pixels only). The far city is p99 194 on screen and the approved oak/lime crowns max 191. A back tree must stay darker than every layer behind it (same rule that failed cp_lime round 1 at 208). Medians are fine: back median 151, p10 129. Fix: one more step down on the #b6d434 clumps (to about 190 on screen), crown tops at file rows 0-60 and the upper-left lit side of each clump.
3. Outline: PASS. No ink line; leaves end in their own dark #243728, trunk marks #312f2f (neutral). Edges are leaf shade, not outline. asset_qa decor-ink 44 % is that leaf shade, accepted as with rw_lime (52 %).
4. Shapes: PASS. Trunk straight and 14-16 px wide at every row from 100 to 249 (rows 150 to 200 narrow to 14); branches thin 1-2 px diagonals, no flat cuts (col 0: 3 px, col 191: 3 px, row 0: 165 px, crown top is above the world as intended). Eleven pixels have one neighbour or fewer, none isolated. Leaf drips under the crown are tiny hanging dots, they read as leaf tips.
5. Shading: PASS. Three-step leaf ramp (#4d8a25, #2f6324, #83b826 plus the highlight and the dark shade), trunk cream #ded9bd with grey #837e76 shade side on the right (light from the upper left), black bark marks. No mottled fields. 10 colours in all.
6. Palette: PASS. 10 colours, darks neutral on the trunk. The greens are more yellow than the oak/lime, fine for a birch.
7. View: PASS. Front-on trunk and crown, no tops.
8. Fit: PASS at 1x (clear against sky and clouds). At 3x the clumps are as crisp as rw_lime and cleaner than the old tree_far. The lamp at x 868 stands in front of the trunk without clashing.
9. Read: PASS. Unmistakably a birch (white trunk, black marks, lime clumps), cute, no text.

VERDICT: FAIL (1 item: Layer). Lower the highlight one step and re-review; all other items pass.
