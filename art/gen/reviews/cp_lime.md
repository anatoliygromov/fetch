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

VERDICT: FAIL (6 items)
