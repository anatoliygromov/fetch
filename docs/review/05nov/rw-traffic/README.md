# River Walk traffic family, 5 Nov 2026 (branch art/rw-traffic-05nov)

Owner's redraw calls (board, 25 Oct): road_car1, road_car4, road_cyclist1 (+ roll), road_cyclist2 (+ roll). The
riders are made as the hooks ask (docs/art_hooks_r8.md): cyclist_adult1-2.png and their pedal loops replace
road_cyclist1-2 in both uses (promenade bikes and the bike lane; road.lua picks them when they exist).

| Asset | Game file | Size | Render (SpriteCook NB 2.1, 1K, pixel) | Credits |
| --- | --- | --- | --- | --- |
| rw_cyclist_adult (pilot) | cyclist_adult1.png, cyclist_adult1_pedal.png | 84x87, 8 x 84x87 | rw_cyclist_adult_n5b | 24 still + 26 loop |
| rw_cyclist_adult2 | cyclist_adult2.png, cyclist_adult2_pedal.png | 84x87, 8 x 84x87 | rw_cyclist_adult2_n5a | 24 + 26 |
| rw_car1 | road_car1.png | 241x88 | rw_car1_n5b | 24 |
| rw_car4 | road_car4.png | 185x77 | rw_car4_n5a | 24 |

Method (tools/build_traffic.py): 256 x 256 blockout with Pepper at 1x; the render read 1 px = 1 art px (pitch 1, no
resampling); magenta and its pink blends keyed; snapped to art/palettes/riverwalk.gpl; one ink; near twins merged;
a clean pass on the new cut only; wheels drawn by rule (round, 8 even spokes, fitted on the render's own tyre ring);
outline closed; small blotches filled. The pedal loop: still everywhere, the animation's pixels only in the leg zone,
snapped to the still's colours, wheels turned 22.5 degrees a frame (8 frames = 180 degrees = a whole spoke step).
Every changed pixel: art/source/NAME/edits.json. Sources: art/source/NAME/*.aseprite (tools/aseprite_io.py).

Also fixed: tools/grid_cut.py read only palette lines without a leading space, so every colour with red under 100
(all the darks) was dropped from the level palette when snapping. New layer `lane` (55 px/m) in art/gen/rules.json.

Checks: PEPPER UNCHANGED, flow 125/125, check_backdrop: only the known gable, asset_qa: riders WARN (lone pixels
3.5-3.9 %), cars PASS, library FAILs unchanged from the base. Cards: cards/. In-game frames: ingame_*_1x.png.

## Fix round 1 (independent review 5 Nov: art/gen/reviews/*.md, all 6 FAIL)

tools/fix_traffic_r1.py: `base` (riders padded 2 px a side to 88 wide; family ink #000000 = the bench's; near-ink
shades merged into #373737; one wheel drawn once and stamped on both centres on one axle line; the outer silhouette in
the ink), then `hand` (art/source/NAME/hand_r1.json: the faces, helmet vents, collar, car1 glints and rack, car4
pillars, rear glass and strays, the cars' wheels stamped front to rear), then `pedal` (wheel phases 0, 11.25, 22.5,
33.75 degrees, each twice; holes in the leg zone closed; no light glints at the pedals). Code: road.lua
`Rd.PEDAL_PX = 26` (a pedal turn per 208 px, about 1 a second); the bike lane draws road_rider1-2 (55 px/m) when they
exist. asset_qa.py: layer `lane` (play look), road cars and lane riders checked as lane. Frames have no gutter: the
game cuts each pedal frame by the still's width (road.lua quads), so none is needed.

| Asset | Credits this round |
| --- | --- |
| road_rider1 (new, lane) | 24 |
| road_rider2 (new, lane) | 24 + 24 (family retry 1: both variants came back on a 2-3 px grid; the one input changed: the style images, card only) |
