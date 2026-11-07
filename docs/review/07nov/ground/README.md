# GROUND track, 7 Nov: River Walk and City Park ground

Branch `day/07nov-ground`. 0 credits, no image service called. Downtown and the vehicles, animals, bones and hint
bubbles were not touched. Pepper unchanged.

## 1. Put back what the owner liked better

Each item side by side (rejected 6 Nov version | now) in `reverts/`.

| Board id | Owner said | What is in the game now | Kept from the 6 Nov fix |
| --- | --- | --- | --- |
| rw_road_06n | "previous was better, more textured" | road.png as before 8f91328, pixel for pixel (`tools/make_road.py` restored): grain, tyre tracks, cracks, patches, worn dashes | nothing |
| park_ground_06n | "was better before" | park_ground.png before the flat-band fix | nothing |
| park_stone_06n | "prev was better" | the pink granite stone, cut at the water | the pond drawing (ripple ring, reflection) |
| pontoon_06n | "previous pontoon was better" | the 54 x 12 slab on two floats | the mooring (the old line ended at a post in open water): lines to the quay cleat and the pile, ripples |
| gritbox_front_06n | "Green sand box was better in terms of colors" | the old forest greens | the front-on shape (the old 3/4 side face read as a dumpster) |
| rw_front_hedge_06n | "Im not sure what that is" | the previous grass verges with shrubs and bollards (same seed, same places) | nothing |

Frames: `reverts/ingame_*` (before | after, colour over greyscale), `reverts/*_5x/6x` (the files).

## 2. Ground joins as one system

The audit (`origin/audit/07nov-ground-joins`) found 29 cut joins. One cause: each column painted alone. Now:

- **Kind map and rule table**: `riverwalk/joins.lua`. Every change of ground kind has a rule (what is stamped, which
  painter). The painters mark what they stamp. The check runs in each level's `--physics` tests and fails on any
  change with no rule or nothing stamped: River Walk PASS (11 changes), City Park tall PASS (4).
- **River Walk** (`scene.lua Sc.paintQuay`):
  - The ramps are stone steps, 8 px rise per 8 px run (a slope tile), treads level, joints at the step edges. They
    land on the quay paving with no seam (RW2, RW3, RW9).
  - The road ends in a granite kerb return with a rounded corner. The wall corner has quoins. The road has a contact
    line or the wall's cast shadow (RW1, RW10). The light strip to the screen bottom is gone.
  - Quay ends (4 of them): the coping overhangs by 2 px with a shadow under it, a wet dark arris from the waterline,
    a ripple and a reflection in the water (RW4, 5, 7, 8).
  - The bridge shadow is a parallelogram with slanted ends and a 1 px penumbra (RW6).
  - Contact shadow on the paving under the house fronts, trees and pots (RW12-14). A tree grate was tried and dropped:
    it read as a bar in front of the trunk.
- **City Park tall** (`Sc.nearBanks`, `Sc.drawFarArt`, `Sc.drawTreeFeet`):
  - Near pond banks at both ends of both ponds: a rounded shoulder, then a 2 px slope tile into the water, so the
    path and the earth bands step back instead of ending in a vertical cut. Grass lip, wet foot, ripples (CP2-5).
  - Up in the trees, the far tree line now stands on its own lawn (the kit lawn faded as the shore), so nothing
    ends over the flat sky colour (CP9). The mid row has its lawn and a tuft row over its feet (CP6).
  - Grass tufts over the tree feet's straight line (CP8).
- **The kit**: `tools/make_ground_kit.py` (`--check`) draws the textured parts (kit_cp_midlawn, kit_cp_tufts,
  kit_cp_roots, asset_qa PASS). The geometric parts are drawn by rule from each level's palette in scene.lua.
- Not changed: CP1 (the earth bands), because the owner asked for the previous texture back. RW11 (railing ends at
  the steps) and RW15 (the hedges, now verges again) are open.

Frames: `joins/rw_x*_ba_3x.png`, `joins/cp_pond_*`, `joins/cp_y000/024_*` (camera up), `joins/cp_y144_x1600` (tree
feet). All screens: `rw_all_before/after.png`, `cp_all_before/after.png`.

## 3. The kennel

Board: "Kennel like this would never be on the street", "Why is the dog house look so weird?".

- A classic dog house from its gable end, built by rule (`tools/build_rw_kennel.py`): pitched slate roof with even
  2 px steps, red planks, a round door in the middle, a name plate with no letters. 44 x 44 at true scale, 11
  colours, asset_qa PASS.
- It stands in Pepper's front garden: a lawn across the house front (x 0-184), the paved path from the green door
  (where she starts), grass over the paving's edges, a low white picket edging along the kerb, never over her.
- Same place, same door height, same gold bone, same reach. The eaves box is y 150 (was 158), on the new roof.

Frames: `kennel/` (8x file, before | after at 3x, Pepper on the roof at 5x, the garden joins at 5x).

## Checks (all on the final commit)

PEPPER UNCHANGED; check_flow 125/125; TILED CHECK PASSED; BACKDROP OK; physics riverwalk 56/56, citypark_tall
98/98, downtown_tall 102/102; check_curve T1-T4 PASS; asset_qa PASS on kennel, gritbox_front, pontoon,
park_stone and the 3 kit parts. road and park_ground WARN on noise and blotches: that is the texture the owner asked
for. measure_layers: City Park still light to dark (mid median 154 to 177, under the shore's 181); River Walk's flag
"shore > back median" was there on main before.

Cards: `cards/` (7, all PASS). Pipeline: the 7 pieces are at review (family rw_ground_07nov). The independent review
is for the producer.

## Questions for the owner

1. The steps down to the quay are 8 px stone steps (0.17 m). OK, or a smooth ramp?
2. The front garden goes across the whole house front, with the bench in it. OK?
3. Pepper stands on the peak of the new kennel roof: her paws float about 3 px over the slopes. OK?
4. The road is the previous textured one. The front band is the previous verge with bollards. OK?
