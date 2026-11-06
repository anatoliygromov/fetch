# Round 1 (reviewer, 6-7 Nov night)

Pieces: the four LIMES trunk pillars turned into lime trees at world x 1004, 1112, 1216, 1420 (scene.lua treetops, crowns over the high road), the low bough's trunk (cp_bough_low joins the lime at 1420), and the fork ledges on those trunks and on the oak at x 1600-1700 and 2560-2880 (cp_bough_* play pieces).
Looked at: sweep frames x 960, 1280, 1600, 2560 at y 144, 24 and 0, colour and greyscale, at 2x and 3x, and a 6x crop of the three ledges at x 960 y 144.

## Lime trees (trunks and crowns)
| Item | Verdict | Evidence |
| --- | --- | --- |
| Scale | PASS | trunks 36-40 px wide = 0.8 m, crowns fill the sky over the high road |
| Layer | PASS | trunk at 1420 on screen p10 102, p50 116; mid trees 131-178; far city 172-207. The base review's CP2 (trunks at the mid value) is fixed: one step darker than the crowns and the mid row, lighter than the boughs |
| Outline | PASS | none |
| Shapes | PASS | bark bands vertical and straight; crowns in leaf clumps, no lumps |
| Shading | PASS | 5 bark browns, 4 crown oranges, flat |
| Empty sky (base CP1) | PASS | crowns now cover x 880-1150 at y 0 and y 24 |
| floats | PASS with a note | every trunk ends on the lawn line. No root flare and no dark base row, so at 3x the feet look sawn off at the lawn. Minor |
| owner test | PASS | |

## Low bough's trunk
PASS. The bough (world x 1280-1420) thickens into a root and meets the lime at 1420 (frame x 1280 y 144, screen x 120-135). Its outline is unbroken and its free tip ends in a twig, not a bracket.

## Fork ledges
| Item | Verdict | Evidence |
| --- | --- | --- |
| Shapes | FAIL | every crotch ledge is a lens: one flat orange deck with a light top stripe, dark tips that curl up at BOTH ends, crossing the trunk symmetrically (frame x 960 y 144 at screen x 10-85, 125-190, 225-295; same shapes on the oak at x 1600 and 2560). Nothing says branch: no taper from a thick root to a thin tip, no bark bands, no collar where it leaves the trunk, and the darkest part is the upturned tips. At 1x they read as canoes laid across the trunks. The 8f4e5b9 fix (stub ends taper to a twig) did not change the read |
| owner test | FAIL | "what are those boats in the trees" is the first thing a child asks |

Exact fix (tools/build_cp_boughs or the cp_bough_* sheets, 0 credits): draw each crotch ledge as two limbs leaving the trunk, not one deck through it. Each limb 8-10 px thick at the trunk with a 2 px bark collar, tapering to a 2-3 px tip that ends in a small fork; the two limbs at different lengths and angles (one rises 2-4 px, the other droops); bark bands along the limb in the trunk's browns; the light stand-on edge only on the flat top; no upturned dark hooks. The flat level's oak limbs (citypark x 1600) already read right and are the model.

## The maker's question: do the fork ledges read as canoes across the trunk?
Yes, all of them, at every tier. See the fix above.

# Round 2 (reviewer, 6-7 Nov night)

Branch night/06nov-cp at e4b9c9e merged into review/06nov-cp. Re-rendered all 27 tall frames; looked at x 960, 1280, 1600 and 2560 at 4x, one lime fork at 10x (frame x 960 y 144, screen x 5-95, y 45-75), the feet at 5x.

## Tree feet (Sc.drawTreeFeet)
PASS. Every lime and the oak now widens into a root skirt with 2 dark base rows on the lawn; nothing ends sawn off. Note: the skirt is one smooth bell; at 5x it reads as a buttress rather than separate roots. Fine at 1x.

## Fork ledges
| Item | Verdict | Evidence |
| --- | --- | --- |
| Shapes, lime forks (8-18 px stubs at 1004, 1112, 1216, 1420) | FAIL | still brackets. At 10x each stub is a flat plate with a dark 1 px outline, a dark triangular gusset under it, and a vertical dark edge at the OUTER end: the thick end is the tip and the thin end is at the trunk, the taper of a shelf bracket, not a limb. The top edge is dead straight |
| The bar across the trunk | FAIL | the pair is joined by a 1 px dark line across the bark (frame x 960 y 144, screen y 57 across x 30-70; same on every fork, and across the oak at x 1600 at screen y 46, 104, 178). It reads as a plank pushed through the trunk. The trunk must cover it |
| Shapes, oak long limbs (x 1600-1700, 2560-2880, 60-100 px) | PASS with a fix | they now leave the trunk thick and end in a forked twig; no upturned hooks. They read as boughs lit from above, but as flat boards: straight top edge, straight wedge underside, no bark bands. Passable once the bar across the trunk is gone |
| Canoe read | PASS | gone |
| owner test | FAIL on the lime stubs | "little shelves nailed to the trees" |

Answer to the maker: the lime forks are still brackets, not limbs, for three reasons: the taper runs the wrong way (thick at the tip), the top is a straight plate with a gusset, and the pair is tied by a line through the trunk. 8-18 px is also too short for a limb to read at 1x.

Exact fix (0 credits, tools/cp_trunk_spans.py and the fork drawing):
1. Reverse the taper: 6-8 px tall at the collar on the trunk, 2-3 px at the tip, the tip ending in a 1 px twig, no vertical end edge.
2. Round the top: the top edge rises 1 px at the collar and drops 1-2 px toward the tip; the underside follows the same curve 3 px lower, not a straight wedge.
3. Never draw the ledge across the trunk span: clip the ledge art to outside the trunk's per-row span (cp_tree_spans.lua already has it), or draw the trunk after the ledge.
4. Make each stand-on fork one limb 24-40 px long on one side (the side Pepper lands from), and on the other side a 4-6 px knot in the bark colours. Keep the hit box as it is.
5. Two bark bands along each limb in the trunk's browns so the limb and the trunk are one material.

# Round 3 (reviewer, 6-7 Nov night)

Branch night/06nov-cp at cf27696 merged into review/06nov-cp. Re-rendered x 960, 1280, 1600, 2560 at y 144, 24, 0; 10x crops of the fork at 1004 (frame x 960 y 144, screen x 0-100, y 40-80) and of Pepper's fork at 1420 (frame x 1280, screen x 90-190, y 50-90).

| Item | Verdict | Evidence |
| --- | --- | --- |
| Lime forks (1004, 1112, 1216, 1420) | PASS | each is now one limb thick at a bark collar (7-8 rows), thinning to a 1 px twig, with a curved top and two bark bands, plus a short tapered stub on the far side. The taper runs the right way, no plate, no gusset, no vertical end edge. At 1x and 2x a child sees a branch |
| Bar across the trunk | PASS | gone on every fork and on both oaks; the trunks are clean bark |
| Oak long limbs (1600-1700, 2560-2880) | PASS | stop at the trunk edge, forked twig tips; still flat-topped boards with a wedge underside, passable. Optional: two bark bands along each |
| Nothing floats | PASS (note) | Pepper on the fork at 1420 stands across the crotch with the limb under her front paws and the stub under her hind paws; between them her paws rest on bare bark. It reads as standing in the fork. Optional: a 2 px bark saddle in the trunk's own browns along the hit box's top row where it crosses the trunk, so the crotch has a visible lip |
| owner test | PASS | no boats, no shelves |

Answer to the maker: they read as limbs now. A longer decorative limb past the box is not needed.
