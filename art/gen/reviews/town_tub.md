Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

# Review gate 8: town_tub.png (32x51, box 32x28)

Frames (mine, colour 1x, 3x, grey), camera y 240, x 160, 560, 1260, 1880, 2200, 2760: /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/y240/ (names sweep_downtown_y240_xNNNN.png, _3x, _grey3x); RIVER sign x 3300: /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/sign/; grey 3x: /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/grey/g1260.png. File at 5x beside Pepper (cell 0,0,60,52), bench, bin, lamp: /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/c1_5x.png, c2_5x.png, c3_5x.png, c4_4x.png; 8x: /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/z8.png. asset_qa PASS and check_backdrop OK re-run on bde1a87.
Scale assumes 46 px/m on the play line. Pepper's sprite is 52 x 38 (1.13 x 0.83 m); a real labrador is about 0.9 x 0.6 m, so she is already about 1.4x true. Mia (7 years, about 1.2 m) is about 55 px.

1. Scale: PASS. Tub 28 px = 0.61 m, 32 wide = 0.70 m, shrub 31 x 23 = 0.67 x 0.5 m, total 1.1 m. A street planter with a clipped shrub is 0.9 to 1.2 m: true. Pepper is a little taller than the tub; the shrub reaches her head height in frame x1260.
2. Layer: PASS. Play piece. The old tub's ink is #050a17 (luma 9), darker than the sample's #12121a (luma 19); the shrub uses it too. Barely visible, noted.
3. Outline: FAIL. Edge 153 px: 152 are ink #050a17, one is green #285e29 at (13,2), a 1 px gap in the shrub's top outline (a notch on the upper left of the dome at 8x).
4. Shapes: PASS. Dome round, rim straight, four corner brackets equal.
5. Shading: FAIL. Shrub rows 0-22: 4 colours, 31 of 578 opaque px (5.4 %) are lone (no same-colour 4-neighbour), over the 5 % bar for non-buildings. The dark #285e29 flecks, e.g. (7,6), (15,9), (22,7), (19,14), are scattered, not a ramp, and read as mottle at 1x and in grey 3x (g1260: the dome looks dithered beside the clean crate and plinth). asset_qa passes because it counts the whole 32x51 file (2.2 %).
6. Palette: PASS. Greens #8ec956, #619e45, #285e29 plus the tub colours, all in the set.
7. View: PASS. Front-on tub with a thin rim; the dome reads as a ball.
8. Fit: PASS. Tub body as crisp as bench and bin at 1x; the shrub is busier than anything around it. Counted under item 5.
9. Read: PASS. A potted bush. Cute, reads at 1x.

VERDICT: FAIL (2 items: 3 and 5)
