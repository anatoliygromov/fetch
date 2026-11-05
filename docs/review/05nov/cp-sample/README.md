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
