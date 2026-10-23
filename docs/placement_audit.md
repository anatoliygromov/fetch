# Placement audit: River Walk, City Park (tall), Downtown (tall) (art/placement, 23 Oct 2026)

How it was looked at: every screen of each level rendered with the look on and no HUD
(`LOOK_SWEEP=1 love riverwalk --level L --lookshots`, tests_look.lua: the camera steps 300 px along the level at
each height tier, the bottom of the world, then every 120 px up; Pepper on the highest floor at the camera + 140),
viewed at 2x, the suspects at 3x, plus colour and greyscale. Sizes against 46 px a metre (Pepper about 0.6 m at
the back, 26 px; a door 2 m = 92 px, a storey 3 m = 138 px, a lamp post 4 m = 184 px, a bench seat 0.45 m = 21 px,
a car 1.5 m = 69 px). `python3 -I tools/asset_qa.py --all` for the quality column (state on main v0.6: 44 PASS,
57 WARN, 32 FAIL, most FAILs are batch 1 files the game does not load).

Evidence crops (3x, frames of main v0.6): `docs/placement_audit/<name>.png`, named in the tables.
Severity: 3 = reads wrong at a glance (floats, placeholder, a door smaller than a child), 2 = visible on a look,
1 = polish. Fix: move, scale-by-redraw, re-crop, redraw, compose. Status: what this branch did.

Approved art (BIBLE 3; River Walk's concept set: building, cafe, gable, bench, bin, lamp, both kiosks, planter,
flower box, pavement, and the starter tree, railing and pot from the owner's concept scene) is not changed here:
its findings are listed for the owner.

## River Walk (3840 x 240, 13 frames)

| Asset | x (y) | Problem | Sev | Fix | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| gable | 3626 | Scale: door about 14 x 28 px (0.6 m) beside Mia (60 px, 1.3 m); storeys about 30 px (0.65 m). Mia is taller than the door. `rw_gable_door_mia` | 3 | redraw at true scale (a mid-row house, or a ground floor only at 46 px/m) | yes (approved) | listed |
| cafe | 3690 (top -31) | Scale: shop door about 13 x 40 px (0.9 m), storey about 62 px (1.35 m): half size | 3 | redraw at true scale | yes (approved) | listed |
| building (HOME) | 0 | Scale: windows about 27 px (0.6 m), half size. Stray 4.5 % (limit 2 %), noise 1.6 % (asset_qa FAIL) | 2 | redraw at true scale, built from stamped parts | yes (approved) | listed |
| tree (HOME tree) | -2 (top 47) | Crown cut flat along its top row (x 0-75, y 47) right under the house cornice: a hard horizontal edge. Decoration with a 64 % dark edge (decor-ink), 6 pinholes. `rw_tree_top` in out_place | 2 | re-crop: round the crown's top (a few rows of leaf lobes) | yes (owner's starter composition) | listed |
| tree_far, tree_near | 520, 1056, 2978 | Scale: 100 and 135 px tall = 2.2 and 2.9 m; a street lime is 8-12 m. They read as saplings next to the 2.2 m lamp. tree_far: 66 % dark edge, 10 pinholes, 4.5 % stray. `rw_tree_far` | 2 | scale-by-redraw (crowns cut by the screen top, as Lion King does) or keep as the concept's stylisation | yes (concept pieces) | listed |
| lamp_post | 590, 1350, 2120, 2660, 3215 | Scale: 101 px = 2.2 m, a Stockholm lamp post is about 4 m (184 px). Approved size from the concept. `rw_kiosk_lamp_scale` | 2 | redraw taller (lamp hearts and light move with it) | yes (approved) | listed |
| kiosk_kaffe, kiosk_glass | 748, 900 | Scale: awning top 72 px over the pavement = 1.6 m (a kiosk is about 2.5 m); the awning height is the high route's ledge (y 112), so the kiosk cannot grow without a level change | 2 | design: keep (perch height) | yes (approved) | listed |
| railing (rail_bg_*) | 80-1288, 2880-3626 | Scale: 30 px = 0.65 m; a river railing is about 1.1 m (50 px). Decoration with a 76 % dark edge (decor-ink warn) | 2 | scale-by-redraw (decoration only, no collision) | yes (concept piece) | listed |
| bench | 93, 3548 | Seat top 28 px over the pavement = 0.6 m (0.45 m = 21 px), set by the 19 px crawl gap | 1 | none (gameplay) | yes (approved) | listed |
| ferry | 1560 | Scale: 252 x 93 = 5.5 x 2 m; a commuter ferry is 20-25 m. Its decks are Pepper's route. Play piece with a 69 % outline (asset_qa FAIL, kept on art/freefix). `rw_ferry_scale` | 2 | design (route) | yes | listed |
| road under the bridge pier | 1936-2072 (y 199-240) | The road (asphalt, lane dashes) is drawn over the quay pavement and the quay wall under the pier: hard seams at x 1936 and 2072. Cause: road.lua counts the pier's row at y 184 as promenade. `rw_pier_road` | 2 | code: road spans only where the top terrain is the promenade | no | **fixed** |
| stairs down to the quay | 1240-1300, 2756-2816 | The road's rows follow the slope: the lane dash runs diagonally under the steps. `rw_stairs_road` | 1 | code: no road rows under slopes | no | listed |
| pier | 1935 | Reads as a free-standing tower in the river (no deck going back over the quay) | 1 | compose (a deck cap going back) | yes | listed |
| road (ground art) | everywhere | Noise 3.3 %, blotches 10.9 % (asset_qa WARN): grain by design (make_road.py), reads as asphalt at 1x, speckled at 3x | 1 | redraw clean asphalt (flat fill, sparse aggregate, the same rows for the row scroll) | no (not on the approved list; from make_road.py) | listed |
| front band | everywhere | Fine: dark silhouettes, never over Pepper | - | - | - | - |

Composition: the start and the end are composed; promenade A and B repeat bin, planter, flower box, grit box, pot
by design (each is a lesson). The harbour (2100-2700) is open water by design. Pepper reads everywhere (dark dog on
light pavement and water). Greyscale: sky, skyline, far shore, water, back, play from light to dark.

## City Park, tall (2880 x 384, 30 frames at camera y 144, 24, 0)

| Asset | x (y) | Problem | Sev | Fix | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| lamp posts on the high road | 864 (216), 1696 (192), 2624 (216) | Float: the post's foot is drawn 10 px above the walk, the crown branch and the play tower deck (stage.lua puts every lamp's foot at the pavement's back edge, EDGE). `cp_lamp_float_crown`, `cp_lamp_float_walk`, `cp_lamp_float_tower` | 3 | code: a lamp on the high road stands on its ledge | no | to fix |
| play tower post | 2604-2608 (222-296) | Drawn as a 4 px tree trunk from the oak canopy (y 64) to the path: a pole from the sky. It is the post of the play tower's lower deck (2600-2656, y 256); tier() missed it because the upper deck starts at 2616. `cp_thin_trunk` | 3 | code: a post a deck crosses is a tower post | no | to fix |
| treetop trunks | 640, 1004, 1112, 1216, 1420, 1528, 1916, 2392, 2584 | 8-12 px (0.2 m), long and bare: they read as poles; the park tree art has the same 8 px trunks under 87 px crowns, so the proportion is the art's | 1 | redraw with the crowns (taper, a fork under the crown) | no | listed |
| LOW BOUGH | 2216-2248 (166-182) | Drawn as a 16 px slab rising diagonally: reads as a crate seen from above at an angle (a top face), not front-on. `cp_low_bough` | 2 | code: a front-on bough, tapering and curving up into the leaves (same solid box) | no | to fix |
| pond banks | 736, 1008 (pond 1), 2040, 2272 (pond 2) | The path and its soil bands end in a straight vertical cut at the water. `cp_pond_bank` | 2 | code: a rounded earth lip at each bank | no | listed |
| park_keeper_winch | 960 | Scale: the keeper about 62 px = 1.35 m (an adult 1.75 m = 80 px). `cp_keeper_scale` | 2 | scale-by-redraw (animated sheet) | yes | listed |
| park_table_front | 1416, 2500 | 28 px = 0.6 m table (0.75 m = 34 px); its top is a perch (y 300) | 1 | design (perch height) | yes | listed |
| HEDGE | 528-592 | A box hedge on two stems: reads as topiary on stilts | 1 | redraw (a hedge to the ground with a crawl gap of leaves) | no | listed |
| NEST | 2824 (78-88) | A dark lump; reads as a box from below | 1 | redraw (twig ring, eggs or the magpie's tail) | no | listed |
| park_tree1/2, park_oak (mid and back crowns) | everywhere | asset_qa WARN: 1.5 % dirt, 4.5 % stray, blotches 2 % (organic, warn only) | 1 | redraw later | no | listed |
| high road sky | 300-2400 at camera y 0 | The top half of the screen is empty sky at the treetop tier | 1 | compose (the canopy's upper crowns, birds) | yes | listed |

Composition: the low road is well paced (gate, leaves, log, bench, hedge, pond, keeper, picnic, playground). The
treetop tier reads, Pepper is always the darkest shape. Greyscale: crowns behind the high road are as light as the
mid trees (both faded); the ladder holds by the dark planks.

## Downtown, tall (3520 x 480, 36 frames at camera y 240, 120, 0)

| Asset | x (y) | Problem | Sev | Fix | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| tall house fronts (town_front_tall1-3) | BAKERY 1180-1320, 1320-1400, 1404-1548, GUILD HOUSE 1552-1700, 1912-2180, 2296-2384 (tops 238-300, base 414) | Code placeholders: flat yellow and salmon blocks with grey squares for windows; the largest shapes on the high road screens, and as light as the facade row behind them (no depth step). `dt_fronts_placeholder` | 3 | redraw: three fronts from stamped parts at true scale (door 2.2 m, storey 3 m), in their 80 / 88 / 96 x 240 slots | no (placeholders) | to redraw |
| high road ledges with nothing under them | GALLERY 1816-1888 (256, 40 px over the house below), the ledge 2016-2072 (248, 22 px over its roofline), the ledge 2416-2464 (248, 48 px over the house), AWNING 2208-2264 (272: a window awning with no wall), FOOTBRIDGE 2480-2640 (272: both ends in the air). `dt_gallery_float`, `dt_awning_float`, `dt_footbridge_float` | Float in the sky over the facade row | 3 | compose: tall fronts (decoration back boxes, no collision) under them, so each is a cornice, a window awning or a bridge between two houses | no | to fix |
| lamp posts on the high road | 1830 (256), 2420 (248) | Float 10 px over the gallery and the ledge (as City Park). `dt_gallery_float` | 3 | code (stage.lua, as City Park) | no | to fix |
| roof kit placeholders | LOGGIA 1416, GALLERY 1680 and 1816, DORMER 1920, FLOWER ROOF 2288, GUILD ROOF 1560, the ledges, FOOTBRIDGE 2480 | Code placeholders (flat beige boxes, a stepped brick line, a plank and a thin arch). `dt_gable_kit` | 2 | redraw each in its hook slot (docs/art_hooks_r8.md) | no | to redraw |
| RIDDARHOLMEN spire | 3380-3412 (24-414) | Code placeholder (a salmon block and a grey cone with white dashes); drawn at scroll 1.0 in front of the 0.5 facade row, so the far landmark stands in front of nearer houses. `dt_spire` | 3 | redraw (32 x about 390, brick tower and openwork iron spire) and draw it on a slower layer behind the row | no | listed |
| town_house1-3 | HOUSE 1536, 1644, 1832, 2404 | Scale: doors about 12 x 25 px (0.55 m), the whole house 2.6 m: a quarter of true size; Pepper is a third of a house. Their balconies are perches 80-96 px up (gameplay). `dt_houses_scale` | 3 | scale-by-redraw (decision 2, true-scale buildings) | yes (decision 2) | listed |
| DOOR | 0-28 (360-424) | town_door 34 x 58: 1.25 m door (2.1 m = 97 px). `dt_door_scale` | 2 | scale-by-redraw | yes | listed |
| market tables, parasols, stall, awnings, shelter | 368-536, 688, 872, 1008, 1232, 2048, 2336, 3236 | Scale: table tops 0.56 m, parasols 1.35 m, stall roof 1.5 m, shelter roof 1.0 m (2.2-2.5 m real): set by the perches (shelter: owner exception) | 2 | design (perch heights) | yes | listed |
| crate towers | 2624-2720 | Eight identical crates stacked in the canal; repeated sprite side by side | 1 | compose (vary lids and fruit) | no | listed |
| town_facades | the near row | Owned by the facades track (art/pilot-oldtown) | - | - | - | not touched |

Composition: the street is busy and readable; the high road was a row of pieces floating over the facade row (fixed
by the fronts under them). Greyscale (before): the code fronts were as light as the facades behind; the redrawn
fronts sit one step darker than the row and lighter than Pepper's line.

## Counts

| Level | Sev 3 | Sev 2 | Sev 1 | Fixed or redrawn here | For the owner |
| --- | --- | --- | --- | --- | --- |
| River Walk | 2 | 8 | 4 | 1 | 11 |
| City Park | 2 | 4 | 5 | 4 | 3 |
| Downtown | 5 | 3 | 1 | 4 | 4 |

## For the owner (approved art and design calls; nothing changed)

1. River Walk's houses (building, gable, cafe) at half to a third of true scale: Mia is taller than the gable's door.
2. River Walk's lamp posts (2.2 m), railing (0.65 m), trees (2-3 m): true scale would be 4 m, 1.1 m, 8-12 m.
3. The home tree's crown is cut flat along its top row under the cornice: may it be rounded?
4. The ferry (5.5 m), the kiosks (1.6 m), the market tables, parasols and shelter: perch heights set their size.
5. Downtown's town_house1-3 at a quarter of true size (decision 2).
