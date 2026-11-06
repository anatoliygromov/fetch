# Downtown (tall), night of 6 Nov: track DT (branch `night/06nov-dt`, 0 credits)

Design targets: the producer's concepts `art/gen/concepts/dt_highroad_concept_a.png` and `dt_street_concept_a.png`
(design only, nothing cut from them). Everything below is built from parts drawn once and stamped on the grid.

Merged or taken in first: `art/dt-highroad-06nov` (the high road attached to the true-scale fronts, decision 2a),
`art/dt-built-06nov` round 2, and the three Downtown commits of `art/dt-audit-06nov` (cherry-picked ac57e59, f272a95,
b90e3b1: solid tram, canal ends, wall lanterns, boats under the parasols, drains, bridge piers, stall counters, quay
courses, rim bollards). Where this branch had made the same fix (lanterns, parasol piers, the quay under the crates),
it was dropped for theirs.

## What changed, and why

| Brief item | What the sweep showed | What is there now | Files |
| --- | --- | --- | --- |
| 1 Fronts | big flat walls, the same grey windows everywhere | each house one style (a-f, box property `style`): triangular pediments, segmental arches with keystones, eared surrounds or hoods (the same on a storey, different per house); shutters, geranium boxes, wrought-iron anchors, dentil or fillet cornices, lace valances or red drapes, shop fronts in green, oxblood, blue or ink green with a lit room and goods on shelves, a hanging iron sign with a picture (boot, cup, key, fish; no letters), zinc downpipes between houses; Pepper's home in style a upstairs | `tools/build_dt_facades.py` (37 files `town_front_tall<k>_<s>.png`, `town_drainpipe.png`), `tools/build_dt_built.py` (`town_door`), `arthooks.lua` `frontImg` / `H.STYLED`, `maps/downtown_tall.tmx` |
| 1 Loggia house | one window over 148 px of wall | a 148 px portal bay with two window axes | `town_front_tall7_<s>.png`, `arthooks.lua` `bays` |
| 2 High road floats | (fixed on `art/dt-highroad-06nov` and the audit) | plus: the footbridge's arch feet on granite springers capping the audit's piers; the springy awning at x 2208 hung from the cornice on two irons | `tools/build_roof_kit.py` `town_bridge_springer`, `arthooks.lua` FOOTBRIDGE, `scene.lua` AWNING |
| 3 Scale breaks | doll houses inside the bays (x 1600, 2240) | decision 2a is on (`H.PLAZA_FRONTS`, from `art/dt-highroad-06nov`): the true-scale fronts' own ground floors with a French window behind each plaza balcony | frames in `sheets/decision2_old_vs_truescale_x*.png` |
| 4 Shelter | thin grey wireframe | dark green cast-iron posts on stepped feet, a glass canopy with glazing bars and an iron cresting, quarter-round brackets, a slatted bench, the poster in an iron frame (concept street a) | `tools/build_dt_street.py` `town_shelter_tall.png` (same slot 140 x 115) |
| 5 Basin | hard blue rectangle | the rim's granite carried down as a basin wall on the water's side, under the audit's rim bollards | `tools/build_dt_details.py` `town_basin_wall.png`, `scene.lua` RIM |
| 6 Cat | - | not touched (track RW makes the size sheet) | - |

No box Pepper stands on moved. The map changes are box properties (`style`, `pipe`) and one new decoration box (the house at x 2736). `--auto` GOOD GIRL (56 s).

## Numbers

- Every styled front: `asset_qa --layer back --level dt --building` PASS (windows identical per storey, lone 0 %,
  colours 11-20). On screen (card numbers): darkest 100, median 152, contrast within 120: the back layer's row.
- `tools/measure_layers.py --ladder`: Downtown city 200/187, shore 197/184, mid 171/139, back 152/100, play 97/14:
  light to dark (the fronts stay at the back layer's values).
- Shelter, drainpipe, basin wall, springer, home: PASS.
- Checks: PEPPER UNCHANGED; flow 125/125; check_tiled PASSED; check_backdrop OK; `--physics` downtown_tall 102/102,
  riverwalk 55/55, citypark_tall 97/97; check_curve T1-T4 PASS. After fix round 1: the same, plus downtown (flat) 81/81 and `--auto` GOOD GIRL; check_flow needs its own XDG_DATA_HOME when tracks run it at once (shared saves gave 4 false FAILs).

## Where to look

- `sheets/before_after_y<y>_x<x>.png`: before (left) and after (right), colour on top, greyscale under, 2x.
- `before/` and `after/`: the full sweeps (LOOK_STEP=320, tiers y 0, 120, 240).
- `cards/`: one card per piece (5x beside bench, bin and lamp, in-game frame colour and grey, slot).
- `frames/`: the cards' in-game frames.

## Fix round 1 (independent review on `review/06nov-dt`, 0 credits)

| Review item | What is there now |
| --- | --- |
| 1 Small houses beside the true-scale fronts (x 0-1100, 2740-3520) | they were the mid row (scroll 0.5) showing between the fronts. 22 new decoration front boxes fill x 140-1180, the canal gap 2480-2640 and x 2816-3520 with the styled fronts (two or three plasters per screen); the screen 10 courtyard gate stays free in front of its house (`nogate`). Every Downtown screen is now true-scale fronts |
| 2 Toy boats under the parasols | removed. A boat or a pontoon would draw a floor over water that costs a heart, so for a 7-year-old the poles go into the flood instead: a wet band, a ripple ring, and under the surface the pole and its cast-iron foot one step darker |
| 3 Canal a flat slab | front-on water: an 8 px surface band (lit edge, the quay's reflection, drifting ripples), the deep water in two darker steps, no streaks |
| 4 Basin a pit | `town_basin.png`: far coping, an 8 px water band, the near granite kerb, the quay's courses below; the column stands in the water behind the kerb. Jets 2 px with splash rings |
| 5 Rib, pier, cresting | the bridge rib 3 px; the guild pedestal is an urn (its lid the golden bone's perch); a solid rail on the shelter's cresting |
| 6 Kerb end x 3497 | the river stairs are granite steps, no sheared cobbles |

Cards: `round1/cards/` (basin, jets, urn, footbridge, shelter), frames `round1/frames/`. `town_jet`, `town_guild_pier` and
`town_footbridge` belong to the dt_roofs and dt_highroad families and need their gate 8 again.

**Fix round 2:** those 22 boxes are behind one flag, `H.CLOSED_STREET` (arthooks.lua), default false, because decision
6a (the spire on screen) is the owner's pick and decision 2 is open. With it off the ends are open squares: the mid row
(scroll 0.5) across them, the sky and the spire above, and every front flank on a square ends in granite quoins
(`town_quoin.png`). There were no plaza houses at scroll 1.0 on the ends; what the review saw there is the mid row.
`decision2_street/open_vs_closed_y<y>_x<x>.png`: open (left) against closed (right), colour and grey, 24 spots.

## Open questions for the owner

1. **Decision 2 (plaza houses):** true scale is the default here (2a). `sheets/decision2_old_vs_truescale_x*.png`
   shows the old doll houses (left) against it. One flag (`H.PLAZA_FRONTS = false`) brings them back.
2. **The guild house:** concept a turned the stepped block into a stepped gable with a tiled roof against the sky.
   That would put a house top on screen, against the BIBLE rule "taller than the viewport" (owner, 25 Oct), so the
   guild house keeps the high road branch's granite ground floor with the steps as its coping. Say if you want the
   gable anyway.
3. **The house styles:** six styles, picked per house in the map. Keep, or fewer and calmer?
4. **Decision 2, the street:** open squares at both ends with the spire (default) or the closed street
   (`H.CLOSED_STREET = true`)? Sheets in `decision2_street/`.

Review gate 8 (independent reviewer) is
for the producer; `art/gen/reviews/town_shelter_tall.md` is the old shelter's and needs a new review.
