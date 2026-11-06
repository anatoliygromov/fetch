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

No box Pepper stands on moved. The map changes are only box properties (`style`, `pipe`).

## Numbers

- Every styled front: `asset_qa --layer back --level dt --building` PASS (windows identical per storey, lone 0 %,
  colours 11-20). On screen (card numbers): darkest 100, median 152, contrast within 120: the back layer's row.
- `tools/measure_layers.py --ladder`: Downtown city 200/187, shore 197/184, mid 171/139, back 152/100, play 97/14:
  light to dark (the fronts stay at the back layer's values).
- Shelter, drainpipe, basin wall, springer, home: PASS.
- Checks: PEPPER UNCHANGED; flow 125/125; check_tiled PASSED; check_backdrop OK; `--physics` downtown_tall 102/102,
  riverwalk 55/55, citypark_tall 97/97; check_curve T1-T4 PASS.

## Where to look

- `sheets/before_after_y<y>_x<x>.png`: before (left) and after (right), colour on top, greyscale under, 2x.
- `before/` and `after/`: the full sweeps (LOOK_STEP=320, tiers y 0, 120, 240).
- `cards/`: one card per piece (5x beside bench, bin and lamp, in-game frame colour and grey, slot).
- `frames/`: the cards' in-game frames.

## Open questions for the owner

1. **Decision 2 (plaza houses):** true scale is the default here (2a). `sheets/decision2_old_vs_truescale_x*.png`
   shows the old doll houses (left) against it. One flag (`H.PLAZA_FRONTS = false`) brings them back.
2. **The guild house:** concept a turned the stepped block into a stepped gable with a tiled roof against the sky.
   That would put a house top on screen, against the BIBLE rule "taller than the viewport" (owner, 25 Oct), so the
   guild house keeps the high road branch's granite ground floor with the steps as its coping. Say if you want the
   gable anyway.
3. **The house styles:** six styles, picked per house in the map. Keep, or fewer and calmer?
4. **The lone house after the canal (x 2640-2736):** one tall narrow front among the low mid row. Keep, or widen it
   into a pair?

Not done: the low-priority kerb end at the level's right edge (audit item 5). Review gate 8 (independent reviewer) is
for the producer; `art/gen/reviews/town_shelter_tall.md` is the old shelter's and needs a new review.
