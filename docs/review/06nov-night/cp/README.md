# City Park (tall), night of 6-7 Nov: cp track

Branch `night/06nov-cp` (base `night/06nov-concepts`, with `origin/art/cp-audit-06nov` merged in). Credits: 76
SpriteCook (the willow, job 816c4bde, run by the producer under the owner's "SpriteCook up to 900 tonight"). Everything
else 0 credits, built or fixed by rule.

## What changed, and why

| Item | Before | After | Files |
| --- | --- | --- | --- |
| 1 Willow | three 1.8-2 m willows (65 px) on the 46 px/m line: bushes | one weeping willow at true scale, 474 x 508 (10 m crown, top cut by the frame, curtain hem 1.4 m up), centred on the WILLOWS crown (x 804), behind the plane tree and the limes | `riverwalk/art/scene/cp_willow.png`, `tools/fix_cp_willow.py`, scene.lua `Sc.bigWillow` |
| 1b Magpie perch 3 | on the old willow's crown top (678, 247): in the air once that willow went | on the hedge's right shoulder (585, 259); barked at from the left, the ball lands on the hedge top (256), which she climbs | maps/citypark_tall.tmx + export, `tests_citypark_tall.lua` spot 3 |
| 2 Pond | (the audit already made the bank) | reeds and bulrushes in the corners, small reeds on the far bank, bank stones, lily pads (built kit), and the path ends in a rounded grassy shoulder instead of a cut; both ponds, both City Parks | `tools/build_cp_pond.py`, cp_reeds / cp_lily / cp_bankstones, scene.lua `Sc.drawPondKit`, `Sc.drawPondShoulders` |
| 3 Floating log | the LOW BOUGH (alder walk's right end) lay on canopy leaves: its trunk was hidden from y 140 to 196 | the trunk is drawn again over the canopy, from above the bough to the ground, its top under the canopy's own leaves: the bough grows out of a tree | scene.lua `Sc.drawTreetops` |
| 4 Trunk pillars | four flat-topped 33 px trunks (1004, 1112, 1216, 1420) under fork ledges, a low band of crowns: tables; the audit: empty sky over the high road at camera 960, y 0-24, and the 1420 trunk the same grey as the mid crowns | lime trees (cp_lime art as at 1528; 1112 and 1420 mirrored whole) whose crowns run out of the top; fork ends within 16 px of the trunk no longer hook down (no crotch on a stub) | scene.lua TREE_ART, `drawFork` |
| 5 Keepers | winch keeper: eye merged into the cap's brim at 1x, frames 3-4 without eye or nose; cart keeper: 52 dirt pixels (WARN) | the same eye, nose and mouth in all 8 frames (26 px); 51 dirt pixels to their fill (PASS) | `tools/fix_cp_keepers.py`, edits.json in art/source/park_keeper_* |
| 5b Goose fly row | after the critters' rounds, one blotch left in the row | its ring colour; the row reads cleanly at 5x | `tools/fix_goose_fly.py` step 6 |

Frames: `frames/<spot>_before_after_colour.png` and `_grey.png` (before left, after right, 3x), `frames/sweep_all_before_1x.png`
and `sweep_all_after_1x.png` (all 27 screens, tiers y 0, 24, 144). Cards: `cards/` (5x, in-game colour and grey, slot).

## Numbers

- asset_qa: cp_willow PASS (fade 0.28: p10 118, median 153, p90 201, 13 colours, lone 0.2 %), cp_reeds, cp_lily,
  cp_bankstones PASS (decoration), park_keeper_winch PASS, park_keeper_cart PASS (was WARN), goose WARN (walk and hiss rows,
  not this track's).
- Ladder (`measure_layers.py --ladder`), City Park: horizon 209/205, clouds 239/201, city 191/178, shore 181/169,
  mid 154/132, back 141/116, play 83/2: light to dark.
- Checks: PEPPER UNCHANGED; flow 125/125; TILED CHECK PASSED; BACKDROP OK; `--physics` citypark_tall 97/97, citypark
  85/85, riverwalk 55/55, downtown_tall 102/102; check_curve T1-T4 PASS (City Park tall kids 12.6, parents 14.6).
- pipeline: cp_willow at polish (next: review); cp_reeds, cp_lily, cp_bankstones at ingame (next: review).

## Open questions for the owner

1. The willow is 10 m across (474 px; spec 7 m, 322 px): the render filled its frame, as the oak's did. True to life for
   an old willow; it now spans x 556-1030 behind the plane tree and the first lime. Keep, or narrow by a new job?
2. Its brightest gold (#fac02f) is about 201 on screen, the lightest thing on the high road after the sky. Keep it as the
   willow's lit edge, or take it one step down to #f1a619 as the oak's highlight was?
3. Magpie perch 3 now drops the ball on the hedge top when barked at from the left (a climb up the hedge), not on the
   path. Fine for a 7 year old ("HOLD: CLIMB UP" is there), or move it?
4. The fork ledges on the limes now taper to a twig at both ends (a "canoe" across the trunk). Is that limb enough, or
   should the two arms be drawn as separate limbs with a gap of trunk between (needs the trunk part to stay a ledge)?

## Not done

- Gate 8 (independent review) for cp_willow and the pond kit: for the producer.
- The flat City Park keeps its three small willows (the brief: tall level only).
