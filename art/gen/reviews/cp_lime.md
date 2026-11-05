Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), rounds 1-3, 5 Nov 2026

# Review gate 8: cp_lime.png (park lime, 468x508) - 5 Nov 2026, independent reviewer

Used at trunk x 1528 and x 1916 (same sprite twice, not mirrored). Positions are x,y in the file unless "screen".

1. Scale: FAIL. Trunk 35-36 px at 50-60 px up (39 at 40, 42 at 30, 55 at 10); plan spec 23 px (+12 px, +52 %); the approved rw_lime trunk is 22-24. Crown 458 px wide at row 167 (README spec 250, +83 %), 508 px tall. At 1x the crown spans 1.5 screens and hides the whole back of screens 5-7 at the high camera. Top is above the world (y -189), as asked.
2. Layer: FAIL. Highlight #fdd527 (8.1 % of the art) is (255,218,44) on screen, luma 208, equal to the sky (202-209) and above the far city (190-195), tree line (175) and mid (154). 257 px at y24 screen 6, 389 px at y0 screen 7, e.g. file (370-460,430-470). Back layer must stay darker than every layer behind it. Medians pass (back 135-139).
3. Outline: FAIL. Trunk and limbs have a near-black edge: #261020 (luma 24, 4.1 %), #3d1413 (3.2 %), #0e0508 (luma 8, 2.0 %) at the trunk foot (213,478)-(229,508). asset_qa decor-ink WARN 52 % (file edge luma below 60 on 53 % of edge px). On screen it fades to violet 67-83 around the trunk (screen 7, x 0-60, y 60-210 at y24).
4. Shapes: FAIL (minor). Ten detached, ink-outlined limb bars float inside the leaves: (419,360)-(440,415), (398,390)-(414,427), (44,267)-(84,277), (379,146)-(389,161), (96,197)-(109,209), (93,396)-(101,421), (364,12)-(378,32), (414,403)-(432,421), (378,389)-(388,407), (435,211)-(447,227). They look like loose planks. Sky holes are fine.
5. Shading: FAIL. Leaf puffs are 2-3 flat tones with scalloped saw-tooth edges and loose bright flecks inside the orange: file (157-167,173-182), (83-93,203-212), (315-330,355-365). The approved rw_lime shows individual leaves with a clean four-step ramp; this is blotchy by comparison. Lone pixels 0.53 %, fine.
6. Palette: PASS. 9 colours. (Self-built palette; #0e0508 is reddish black, not neutral.)
7. View: PASS.
8. Fit: FAIL. Not as crisp or as dense as rw_lime/bench/lamp at 1x and 3x; also 1.9x the lime's size, so it overpowers the oak beside it. Old small canopies still abut its edges (screen item 6).
9. Read: PASS. Friendly autumn tree, reads at 1x.

VERDICT (round 1): FAIL (6 items)

## Round 2 (fix 02fd5cb, fresh frames /tmp/review_cp/r2)

Scale is an owner question: trunk 35-36 at 50-60 up (39 at 40, 44 at 20), crown 458-468 wide, 508 tall. Not failed. Now used once (x 1528); x 1916 is back to its 8 px code trunk.

1. Scale: PASS (owner question, measures above).
2. Layer: PASS. Highlight #fdd527 became #e4901a (luma 155); on screen back p99 188, max of the lime about 190. No lighter than the city.
3. Outline: FAIL. Still ink: #261020 (luma 24) is now 5.6 % of the art (was 4.1 %), edge below 60 on 53 % of the edge (unchanged), asset_qa decor-ink 52 %. The trunk's right half and all limbs are that near-black violet, 6x/5x crop of file (150-330,350-508) shows a thick ink side and ring round every limb. Only #0e0508 was removed. On screen it sets the back layer's minimum at 67.
4. Shapes: FAIL. The loose limb bars were not removed from the lime: still present at file (419,360)-(440,415), (398,390)-(414,427), (379,146)-(389,161), (96,197)-(109,209), (93,396)-(100,421), (414,403)-(432,421), (378,389)-(388,407). Three of the round 1 ten are gone ((44,267), (364,12), (435,211)).
5. Shading: FAIL. Patchwork unchanged; asset_qa now also WARNs blotches: 14 patches. Flecks inside the orange remain at (157-167,173-182) and (83-93,203-212).
6. Palette: PASS (8 colours).
7. View: PASS.
8. Fit: FAIL (same as 5; still 1.9x the rw_lime in crown width, owner question).
9. Read: PASS.

VERDICT: FAIL (4 items)

# Round 3 (dc2b405; the lime was remade: GPT render on a 4 px grid, tools/grid4_cut.py; 371x509)

Scale is an owner question: trunk 38 at 50-60 up (42 at 30, 51 at 20, 36 at 80); crown 371 wide (was 468), 509 tall; spec 23 / 250. Not failed.

1. Scale: PASS (owner question, measures above).
2. Layer: PASS. Colours luma 43-169 (highlight #fa9a28 = 169 raw; on screen the tree stays under 190). Back p10 112, median 135.
3. Outline: PASS. No ink: darkest #3e2421 (luma 43, 4.0 %) is the shaded trunk side; leaf puffs are rimmed by #6b2e2f maroon (their own darker shade). #261020 and #0e0508 are gone. asset_qa decor-ink WARN 67 % is the maroon puff rims, which I accept under the rule.
4. Shapes: PASS. The loose ink limb bars are gone. A few brown limb pieces show through leaf gaps without ink, e.g. file (117,133)-(145,172), (148,81)-(157,107), (125,261)-(151,292); they read as limbs behind leaves. No flat cuts (x=0: 4 px, x=370: 5 px); crown top is cut at row 0 (cols 26-327) above the world, as intended. Sky holes small.
5. Shading: PASS. Puffs in a clean 4-tone ramp (#fa9a28, #eb6819, #c63418, #6b2e2f), lone 0.37 %, asset_qa no blotches, no mottled fields. Less leaf detail than rw_lime (runs of 8+ px: 26 % horizontal against rw_lime 10 %).
   Grid cut: no half cells or doubled columns found. Run-length check: runs of 2 px (23 %) exceed runs of 1 px (19 %) horizontally, where rw_lime has 33 % against 19 %; P(equal to right neighbour) is 0.50 on even x and 0.545 on odd x, a 4.5 % parity bias (the accepted oak has a 6 % one in y). No seam lines at 4 px multiples; the 6x crop shows 1 px steps throughout.
6. Palette: PASS (9 colours).
7. View: PASS.
8. Fit: PASS at 1x (same family as oak and ash); at 3x the puffs are chunkier than rw_lime's single leaves (WARN).
9. Read: PASS.

VERDICT: PASS
