Reviewer: independent gate-8 art reviewer (Claude, did not make this asset), 6 Nov 2026

# Review gate 8: park_hedge.png (66x72, board redraw) - round 1

asset_qa: WARN (lone 3.1 %, aim under 3 %). check_backdrop: OK. Placed at tall City Park x 528 (box 64x53, y 256-309; 19 px crawl gap under it).
Own frames (tests_look sweep, colour 3x and grey 2x; Pepper crawling, 6x): art/gen/reviews/cp_props_06nov_frames/hedge_x440_3x.png, hedge_x440_grey2x.png, hedge_crawl_6x_a.png, hedge_crawl_6x_b.png, hedge_seam_8x.png, hedge_5x_beside_bench.png, scale_vs_pepper_4x.png.

Scale (46 px/m): 66x72 = 1.43 m wide, 1.57 m tall (solid body 53 px = 1.15 m, crawl gap 19 px = 0.41 m). I assume a clipped park hedge of 1.5 m. Pepper stands 26 px (0.57 m) and reaches the top only by the bench jump, as designed.

Seams (art/source/park_hedge/edits.json: cut 77 rows, rows 47-51 removed, seam at row 47 of the file): compared against the uncut render at 8x. Rows 46/47 continue: leaf clumps line up, left and right edges move by at most 1 px (left edge 0/1, right edge 63/64), no jump in the scallop, no line. One casualty: the orange autumn leaf that straddled the cut is left as a 2x2 orange dab at (15-16, 45-46) with no leaf shape (all other orange leaves are 5x5 to 7x6 with a leaf outline). It reads as a stray orange dot at 1x and 3x.

1. Scale: PASS.
2. Layer: PASS. Play layer, full contrast; lightest #d3cb3b (4.4 %), it is the most saturated thing on screen but the back trees stay lighter in luma on screen.
3. Outline: PASS. One unbroken 1 px ink #0b091c all round (215 edge px, no other colour). Note: ink is slightly blue-violet, the bench is #000000.
4. Shapes: FAIL (minor). Chopped autumn leaf at (15-16, 45-46), a 2x2 orange fragment left by the row splice at row 47. Fix: redraw it as a 5x5 leaf or paint it out with the leaf green by hand. Nothing else visible at the seam.
5. Shading: PASS. Leaf shapes in a 4-step green ramp, light from the upper left (yellow-green top left, darker right), no mottling. Lone pixels 3.1 % (WARN), e.g. the single yellow pixel at (2, 42) and the dabs along the right edge.
6. Palette: PASS. 16 colours, greens and autumn orange of the park; darks #0b091c and #0f1615 (gap shade) near neutral.
7. View: PASS. Front-on, scalloped cap, shady gap with eight stems and leaf litter.
8. Fit: PASS at 1x and 3x. Greener and busier than the park around it, the same pixel size and crispness as the bench and lamp.
9. Read: PASS. A clipped hedge with autumn leaves.

Crawl in game (checked, tests_look copy with the down and right keys forced, Pepper crawling in from x 532 and 548, y 328): Pepper passes under, no visible clash. Her back (top at screen y about 166) is drawn over the 1 to 2 lowest leaf rows (leaves run to file row 54, the box ends at row 53), so she overlaps the leaves, never cut by them. She is black on the dark gap shade, but her silhouette, pink bandana and the bright leaf litter keep her readable. PASS.

VERDICT: FAIL (1 item, shapes, a one-spot hand fix)


# Round 2

Reviewer: independent gate-8 art reviewer (Claude, did not make this asset), 6 Nov 2026. Head 33d1a06.

asset_qa: WARN (lone 3.1 %, 4 small blotches, organic leaf texture; same numbers as round 1). check_backdrop: OK.
Own frames (tall City Park, camera x 440 and 420, y 144): art/gen/reviews/cp_props_06nov_frames/r2_hedge_x440_3x.png, r2_hedge_x440_grey2x.png, r2_x420_3x.png, r2_files_5x_beside_bench_bin_lamp.png.

Round 1 FAIL (item 4): fixed. Pixels (15-16, 45-46) are now leaf green #365032 / #284127, a normal leaf cell, no orange. The four remaining orange leaves are whole 5x5 to 7x6 leaf shapes.
Round 1 note (greener and busier): fixed enough. Greens are olive with a warm gold lit top, they sit with the autumn lime and ash and the orange trees behind at 1x and 3x. In grey it is the darkest, most textured block but reads as a play-layer obstacle like the bench. Scale unchanged (1.43 m x 1.57 m at 46 px/m).

1 Scale PASS. 2 Layer PASS. 3 Outline PASS. 4 Shapes PASS. 5 Shading PASS (ramp, upper-left light, texture is leaf shapes). 6 Palette PASS. 7 View PASS. 8 Fit PASS. 9 Read PASS.

VERDICT: PASS
