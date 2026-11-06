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
