# River Walk street backdrop, screen 12 (5 Nov night, track 6)

0 credits. Branch art/rw-street-05nov = art/rw-water-05nov + origin/night/30oct-gable-b (night/25oct-rw-street: gable and cafe built at true scale, its own review rounds 1-2 on 25 Oct; option B on 30 Oct).

New on 5 Nov: `rw_gable_bay.png` is built (tools/build_rw_gable.py `build_bay()`), not cropped: the crop at x 68 cut the wall anchor in half and left stubs of the window's sills and hood on its left edge. The bay now has its own 8 px corner lesene. 1,626 px changed, all in columns 0-9. `rw_gable.png` is byte-identical (verify() passes) and is no longer drawn in the game.

Frames (1x, game look, no HUD): `ingame_x3000/x3300/x3560/x3700_1x.png`, base (art/rw-water-05nov) `before_*`. Board: `board/`. Cards: `cards/PASS_rw_gable_bay.png`, `cards/PASS_rw_cafe.png` (fade 0.28).

Checks: PEPPER UNCHANGED, flow 125/125, Tiled PASSED, BACKDROP OK (no River Walk fail), River Walk physics 55/55, asset_qa --building PASS (bay, cafe; the unused full gable WARNs on contrast 132). Screen 12 luma: far city 194 / p10 147, gable bay 161 / 119, cafe 174 / 140.

Doubts for the reviewer: the cafe's cream walls are light (median 174): the order back < far holds, but check against the approved HOME house's values; the cafe ends at the level's right edge (x 3840) with no corner; the old 25 Oct reviews of rw_gable and rw_cafe are in art/gen/reviews (rw_gable.md reviewed the full gable, not the bay).
