# City Park sample screen, 5 Nov 2026 (branch art/cp-sample-05nov)

Screen 6 of `citypark_tall` (x 1600-1920), the old oak, at the high camera (y 0 and 24) and the low one (y 144).
Frames are the game's own (`tools/layer_frames_tall.py citypark_tall OUT --ids`): `before_*` the base 427a5a0, `after_*` this branch, 1x. Board images in `board/`, QA cards in `cards/`, the draft board entry `board_item.json`.

## Pieces
| Piece | File | Size | Measures | Credits |
| --- | --- | --- | --- | --- |
| old oak | cp_oak.png | 388x343 | trunk 54-55 px at 50-80 px up (spec 46), crown 388, top at y -24 | 72 (probe + retry 1, 2 variants each) |
| park lime | cp_lime.png | 468x508 | trunk 35-36 px (spec 23), crown 468 (spec 250), top at y -189 | 36 |
| young mid trees | cp_mid_lime/maple/birch.png | 80/72/28 x 139 | 139 tall (spec 138), trunks 5-7 (spec 6) | 24 |

Renders: `art/gen/renders/cp_*`; SpriteCook asset ids in `art/gen/spritecook_assets_cp.json`. The oak used is retry 1 variant b on SpriteCook's own pixel grid (392x348); the probe (cp_oak_a, trunk 74 px) and r1a (left the grey blockout crown as background) are not used.

## Luma (median / darkest 10 %), screen 6
| Camera | Layer | Before | After |
| --- | --- | --- | --- |
| y 24 | back | 134 / 108 | 135 / 100 |
| y 24 | play | 91 / 20 | 91 / 20 |
| y 144 | far city | 193 / 178 | 191 / 178 |
| y 144 | tree line | 181 / 169 | 181 / 169 |
| y 144 | mid | 148 / 127 | 154 / 131 |
| y 144 | back | 132 / 107 | 132 / 83 |
| y 144 | play | 91 / 20 | 91 / 20 |
Whole level (all frames): sky 202, far city 191, tree line 181, mid 154 -> 159, back 138/108 -> 138/108 (y 0) and 134/105 -> 134/100 (y 144), play 80-87. At y 0 and 24 the oak's leaves fill the screen behind the high road (back 86-93 % of screen 6; sky and mid hidden there).

## Checks (this branch)
PEPPER UNCHANGED (4591 steps); flow 125/125; Tiled PASSED; `--physics` citypark_tall 97/97; `--qa` 0 problems in 12762 runs; check_curve T1-T4 PASS (10 seeds, the level order); check_backdrop: only the known River Walk gable (it does not cover City Park; the trees' tops are at y -24 and -189, above any camera). asset_qa: oak WARN decor-ink 71 %, lime WARN 52 %, maple WARN 39 %, mid lime and birch PASS, all at their game fades.

## For the reviewer
- Scale: both big trees came out bigger than their spec (see the cut jsons' `waived`). Judge against Pepper and the plan's true sizes.
- The lime stands in for the ash at x 1916 (right edge of screen 6) until the ash is made.
- Screens 5 and 7 mix the new crowns with the old small canopy crowns (the rest of the family is not made).
- The high road's ledges are play pieces drawn by code over the oak's limbs; check that she and the ledges still read (greyscale frames).
- The street lamps on the high road are still there (plan decision 6, held by the owner).

## Review round 1 (5 Nov, art/gen/reviews/cp_*.md: FAIL) and what changed
All pixel changes by `tools/fix_cp_round1.py`, listed in `art/source/<name>/edits.json` under `round1`; 0 credits.
- cp_oak: nine floating limb fragments deleted (filled with the leaf colour around them) plus 99 loose bark specks and the light streak one left; ink edge #150e15/#332324 next to leaves or air -> the bark's #55382b, #150e15 inside -> #332324, leaf #281b1a -> #832918 (no near-black left); highlight #f6ad35 -> #e48c28 (back p99 on screen 179, was 193-209); the flat cuts at x 0 and 387 carved round; 56 leaf islands merged in the reviewer's two patchwork boxes. Trunk kept at 54 px: a board question.
- cp_lime: ten loose bars (its darkest leaf red) filled; ink edge #0e0508/#261020 -> #553128, #0e0508 inside -> #261020, leaf #3d1413 on the edge -> #79200f; leaf ramp one step down (#ed8b04 -> #d97a06, highlight #fdd527 -> #e4901a). Scale kept as the owner's call: the recolour of rw_lime was not run (251 px tall cannot reach above the world here; see cut json `waived`). Now at x 1528 only.
- cp_mid_maple: 235 dark specks and the trunk pixel (36,113); #471616 inside the two right-side blotches -> #a53008, the rim kept.
- cp_mid_birch: trunk #cfd5d1/#cbbea8 -> #706860 (about 150 on screen), its shade #888187 -> #504a46.
- scene.lua: x 1916 (the ash) back to its code trunk (no second lime); an old canopy crown that touches a new tree's crown is left out (`CANOPY_SKIP`), so old canopies end in whole crowns before the new tree instead of showing through or abutting it.
Left as warnings: oak/lime blotches (small highlight dabs now near the mid orange), decor-ink 73 / 52 / 38 % (own darker shades, no ink). The back layer's lamp glass (215) and the old ash canopy crowns (188) on screen 7 are older art.

## Review round 2 (FAIL) and round 3 (5 Nov)
Two failed rounds on the lime, so its method changed (BIBLE): **GPT 2.5 Sunburst 2K** (`sc_gpt25_2k` in rules.json), a new blockout at the plan's size (trunk 23 px, crown 250, top above the world, `art/gen/blockouts/cp_lime.py`; the first one is `cp_lime_r0.*`), the approved rw_lime and the fixed cp_oak as style references. One job for the lime (the family's last retry) and one probe for the ash (`art/gen/blockouts/cp_ash.py`), 2 variants each, 76 credits each (SpriteCook bills the 3 references per variation; preflight's cost formula is fixed). The renders follow the blockout's 4 px grid (88-92 % clean cells): cut by `tools/grid4_cut.py` (one real pixel per cell, majority, never an average), then `tools/cut_cp_tree.py` (k-means ramps; `--bark-box` keeps the lit trunk bark, `--rim-lum 60`), then `tools/polish_cp_trees.py`.
- cp_lime: variant r2a. Trunk 36 px at 80 up (still wider than the 23 asked; owner's call), crown 371 (8 m), 9 colours, darkest #3b2320 (luma 42, a dark brown), highlight #f68a21 (luma 158, about 176 on screen). The round 1-2 lime is kept in `art/source/cp_lime/round2/`.
- cp_ash: variant a (b drew a 41 px trunk). Trunk 29-33 px, crown 509 leaning right over the alder walk, top at y -186, 10 colours, highlight #e89413 (158).
- cp_oak (`tools/fix_cp_round3.py`): 170 pixels, leaf patches of 2-24 px in the reviewer's boxes and asset_qa's blotches merged into their clump (blotch warn 19 -> 9); checked at 5x, the clumps keep their lit tops.
- cp_mid_lime: highlight #fcc23e -> #d8941c, #d58d11 joins #a95906; cp_mid_birch: #f9c219 -> #d4951e, #ca8106 -> #b46e06. Mid p99 on screen 174-184 (was 202-204), under the city.
- scene.lua: the ash in `TREE_ART`; an old canopy crown is left out only when the new tree's leaves cover it at its middle row (per-row extents of the art), so the wedge of sky on screen 5 is filled by the old crowns behind the lime.
Frames after: the board images; back p99 on screen 179-188 (188: the old canopy crowns on screens 5 and 7, older art), new trees about 176 at most.

## Review round 3 (oak FAIL, the rest PASS) and the oak re-cut (5 Nov, 0 credits)
Three rounds of pixel fixes left the oak's leaf patchwork, so its method changed: `tools/recut_cp_oak.py` re-cuts it from its own render (`cp_oak_r1b.png`) with the lime's pipeline: `cut_cp_tree.py --leaf 5 --bark 4 --rim-lum 60 --mode 2` (new `--mode`: a 3x3 majority on each material's cluster labels, two passes, picking only the material's own colours; a clean pass on the new cut), `polish_cp_trees.py`, then the round 1 rules on the new colours (nine loose limb fragments and 102 loose bark specks filled, no bark or leaf under luma 45 on an edge, nothing under 30 inside, highlight #e48c28, a muddy brown leaf tone to #b8501a, flat cuts carved; all in edits.json "recut"). Leaf ramp 80, 105, 134, 155; bark 40-87. Old rounds kept in `art/source/cp_oak/round3/`; the round scripts now refuse to run (RECUT marker).
At 4x (`board/cp_oak_recut_vs_round3_vs_lime_4x.png`): the ragged rust fields and small dark islands are gone and the clumps read as clumps with lit tops; it is flatter and lower in contrast than the lime. A darker gap rust (#832918) gave more depth but asset_qa read it as an outline (81 %), so the gaps stay at #993518.
On screen 6: back p10 100-115, median 127, p99 179, min 68. Checks: PEPPER UNCHANGED, flow 125/125, Tiled, physics 97/97, QA 0, curve T1-T4 PASS. asset_qa: oak WARN blotches 19 (no decor-ink warning now).
