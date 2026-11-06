# Downtown (tall) audit fixes, 6 Nov evening (branch art/dt-audit-06nov, 0 credits)

From origin/preview/06nov-run with origin/art/dt-highroad-06nov merged. Each PNG: before (left) and after (right), colour
over grey, 3x. Before frames: the merge commit 334c16c (LOOK_SWEEP, y 240 / 120); tram frames: LOOK_TRAM at the stop.
No box Pepper stands on and no bone moved. Built pieces: `tools/build_dt_audit.py` (`--check`), sources in
`art/source/dt_audit/` (.aseprite, the old town_ground and town_rim).

| Fix | Files | What changed |
| --- | --- | --- |
| 1 tram | fix01_tram_lane1, fix01_tram_lane2 | Cause: `H.TRAM_FADE` 0.40 to the back haze (efe6da), so the tram was 150 on screen, at the far city's value, lighter than the street in front. Now 0.10: opaque, 10th pct 88, median 106 (under the far city 145 and the fronts). The art and its alpha (binary) are unchanged. |
| 2 quay wall | fix02_quay_wall, fix02_quay_wall_x1280 | town_ground.png rows 32-67 rebuilt: 3 flat granite courses of 12 rows, blocks 26-54 px in running bond, lit top and left, shaded foot and right. Rows 0-31 (cobbles, kerb) kept pixel for pixel. asset_qa blotches 55 to 4 (the old cobbles). |
| 3 canal ends | fix03_canal_x2400, fix03_fountain_x1600, fix03_square_x2720, fix03_square_x2880 | `Sc.quayEnds` (scene.lua, the ground paint): the kerb turns the corner up the cobbles' end, the quay wall ends in dressed quoins. The far quay's face is a coursed granite band with a wet foot; the water has a waterline (dark reflection rows, drifting light ripples). |
| 4 tram stop | fix04_stop_sign | The sign is drawn after the shelter (H.drawTownStops). The shelter file is not changed: a draw-time copy leaves out the one glass reflection stroke (150 166 174) round the sign's pole. |
| 5 ledges | fix05_ledges_x1760, fix05_ledges_x2240 | The ledges already sit on corbels (dt-highroad's consoles). The flower ledge gets granite corbels at its ends and iron hangers between its boxes. The two lamps on the high road (x 1830, 2420) are wall lanterns: the approved lamp's lantern (rows 0-26, not changed) on an iron bracket (town_lantern_bracket), on the wall pier between two windows (the nearest bay edge). The checkpoints are where they were. |
| 6 water | fix06_boats_x2720, fix06_boats_x2880, fix06_crates_x2560 | Each parasol over the flooded square stands in a moored green boat (town_punt, outlined: it carries the parasol). The crate stack at x 2624 is drawn only above the street (4 crates); the quay wall shows below. |
| 7 domes | fix07_drain_x0480, fix07_drain_x3040 | The black domes were the front bollards' tops. No bollard in the tall Downtown; a drain arch with a grate (town_quaydrain) in the quay wall at each, only on dry quay. |
| 8 cubes | fix08_rims_x1600 | The fountain's RIM boxes (town_rim) are granite corner bollards: chamfered cap, round shaft, plinth, no joints. |
| 9 footbridge | fix09_footbridge_y240, fix09_footbridge_y120 | Granite piers (town_bridge_pier, 14 x 113) from each arch foot (y 311) down to the quays (y 424), behind the crates. Pepper stands on the deck's top with the railing behind her (unchanged). |
| 10 stalls | fix10_stalls_x0800, fix10_stalls_x2400 | Every street awning without a STALL gets a counter (pine top, green planked front, code-drawn flat fills, no ink). The awning at x 872 had one post: the second is drawn at its other end. |

Checks: PEPPER UNCHANGED (4745 steps), flow 125/125, check_tiled PASSED, check_backdrop OK, downtown_tall `--physics`
102/102, `--auto` GOOD GIRL (65/102 bones, 56.2 s), flat downtown `--physics` 81/81. asset_qa: town_rim, town_quaydrain,
town_bridge_pier, town_punt, town_lantern_bracket PASS; town_ground WARN (4 blotches, all in the kept cobble rows).
