# Ground joins audit, 7 Nov

Owner, 7 Nov: "whenever we see two different types of ground connecting, they look cut, including the hills etc."

Read-only audit of `riverwalk`, `citypark_tall` and `downtown_tall` on `origin/main` at 5f30120. No game files changed, no image service called.

How it was done:

- Every screen at every height tier: `LOOK_SWEEP=1 LOOK_STEP=320 ... love riverwalk --level <L> --lookshots` (River Walk 13 frames at camY 0, City Park 27 at camY 0/24/144, Downtown 33 at camY 0/120/240).
- Every change of terrain kind or height listed from the maps (`level/riverwalk.map`, the `tiled_*.map` files the game writes), then each spot rendered again with `LOOK_XS` / `LOOK_YS` centred on it and checked at 4x to 6x.
- Each join traced to the code or art that draws it.

Camera (x, y) is the frame the join was judged in. World x is the join itself. Severity: High = visible at once at 1x, Med = visible when you look, Low = minor, OK = no fix needed.

## Count

| Level | Joins checked | Look cut | OK |
| --- | --- | --- | --- |
| riverwalk | 16 | 15 | 1 |
| citypark_tall | 10 | 8 | 2 |
| downtown_tall | 9 | 6 | 3 |
| total | 35 | 29 | 6 |

## Joins

### River Walk (`L.ground = "quay"`, Sc.paintQuay; flat world, camY 0)

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RW1 | 1120,0 | 1272-1280 | asphalt road / ramp quay wall | The road ends in the 8 px kerb return, which reads as a 1-2 px light vertical strip running straight down to the screen bottom. Asphalt, kerb and granite wall stand side by side with no depth and no shadow. | scene.lua Sc.paintQuay `cornerColour`, Sc.drawRoadEnds (redrawn over Look.road) | A retaining-wall return piece: a coping lip row over the road's end, a 2 px cast shadow on the asphalt beside it, the wall's quoins on the return face. | High | 01 |
| RW2 | 1120,0 | 1280-1312 | promenade paving / ramp | The ramp is the flat recipe shifted per column: slab courses offset 6 px per column, so the rows read as sheared stair steps. Its top edge is a bare diagonal of the back-edge colour against the water, no lip. The first and last columns are full-height joint colour: two vertical seams. | Sc.paintQuay `column()`, `k == "ramp"` branch | Slope tiles stamped per 8 px map cell: a lit coping along the top diagonal, slabs as parallelograms with joints square to the slope, a head slab where it meets the flat. | High | 01 |
| RW3 | 1120,0 | 1312 | ramp / lower quay paving | Vertical joint column at the foot; the band's slab rows do not meet the flat paving's rows. | Sc.paintQuay ramp branch (`first`/`last`) | A landing slab tile that takes the slope courses into the flat paving rows. | High | 01 |
| RW4 | 1120,0 | 1392 | lower quay / river | Paving, kerb face and wall end in one vertical line to the screen bottom. The coping is a 3 px light strip; the wall meets the water with no waterline (no wet band, no reflection row, no overhang). | Sc.paintQuay `dR`/`dL` coping, `wallColour` quoins; water in Sc.drawWater | Quay-end cap: coping overhanging the wall by 1-2 px with a shadow under it, a dark wet band at the waterline, a reflection row in the water. | Med | 03 |
| RW5 | 1650,0 | 1808 | river / far quay | As RW4, mirrored. | as RW4 | as RW4 | Med | |
| RW6 | 1900,0 | 1936 and 2072 | open paving / bridge shadow on paving | The three flat shade bands under the bridge start and stop with a vertical edge at the passage's sides. | Sc.paintQuay `under[]`, `SHADE` | A shadow edge built by rule: the band boundary stepping 1 px per row (a diagonal falloff), the darkest band narrowest. | Med | 04 |
| RW7 | 2060,0 | 2192 | far quay / river | As RW4. | as RW4 | as RW4 | Med | |
| RW8 | 2700,0 | 2848 | river / quay | As RW4, mirrored. | as RW4 | as RW4 | Med | |
| RW9 | 2860,0 | 3000-3032 | lower quay / ramp up | As RW2 and RW3, mirrored. | Sc.paintQuay ramp branch | as RW2 | High | 02 |
| RW10 | 2860,0 | 3032-3040 | ramp quay wall / road | As RW1, mirrored: the road starts at a light vertical strip to the screen bottom. | `cornerColour`, Sc.drawRoadEnds | as RW1 | High | 02 |
| RW11 | 2860,0 | 3032-3088 (and 1280) | promenade back edge / railing | The railing starts 56 px after the ramp's top with a bare end post; along both ramps the paving's back edge meets the water with no parapet. | level/riverwalk.lua railing props (x0 184-1280, 3088-3844), Sc.railing | Sloped railing bays down the ramp, or a granite parapet end block at the ramp head. | Low | 02 |
| RW12 | 0,0 | 0-184 | house front / paving | The facade's foot sits straight on the paving's back row: no plinth course, no contact shadow. | HOME prop (rw_home, y1 174) | A 2 px plinth course and a 1 px shadow row on the paving, stamped under every building. | Low | |
| RW13 | 3728,0 | 3840-4048 | cafe front / paving | As RW12. | rw_cafe / gable props | as RW12 | Low | |
| RW14 | 0,0 | ~250, ~3240, 214 | tree trunk, pot / paving | The lime and birch trunks end in a flat cut at the paving's back edge: no tree pit, grate or root flare. | rw_lime, birch, pot art | A cast-iron tree grate stamp with a 2 px root flare, and a contact shadow under the pot. | Med | |
| RW15 | 0,0 | every road stretch (e.g. 50-170) | front hedge / asphalt | The clipped hedges stand straight on the asphalt. Their ends are quarter circles of radius 8 on a 16 px mass, so the lower half of each end is a vertical cut. No verge, no near kerb under them. | look.lua `clump(..., "hedge")`, Look.front | A near kerb and grass verge strip in the front band, hedge ends rounded over the full height, grass tufts over the kerb. | Med | 05 |
| RW16 | all | promenade | paving / kerb / asphalt | Lit kerb top, 5 row face, joints every 16 px. Reads as a kerb. | Sc.paintQuay steps 1-3 | OK (optional 1 px gutter shadow on the asphalt). | OK | |

### City Park tall (`L.art = "park"`, Sc.paintGroundArt; path line 328, path tier camY 144)

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CP1 | 0-2560,144 | whole level | path verge / earth strata (front band) | Six flat colour bands with hard horizontal seams, no stones, roots or texture: reads as a striped flag under the path. | park_ground.png rows 31-67 (tools/make_town_art.py `park_ground`, flattened by tools/fix_cp_audit.py on 6 Nov), stamped by Sc.paintGroundArt | Earth front built by rule: a grass lip with tufts hanging over the first row, stones and roots stamped on a grid, band boundaries broken by a 1-2 px tooth pattern. | High | 06 |
| CP2 | 560,144 | 704 | path, verge, strata / pond | The path, its verge and all six earth bands end in a straight vertical cut down to the world's bottom. Only the water's own sloped basin edge exists; the near side has no bank. | Sc.paintGroundArt (`wetCol` skips the dark edge), Sc.drawPondBank (curves only the far bank) | A near-bank piece: the path's edge rounding down to the water, a grass lip overhang, stones at the waterline, the strata stepping back 1 px per row. | High | 07 |
| CP3 | 800,144 | 944 | pond / path, verge, strata | As CP2, mirrored. | as CP2 | as CP2 | High | |
| CP4 | 1860,144 | 2000 | path, verge, strata / pond | As CP2. | as CP2 | as CP2 | High | |
| CP5 | 2150,144 | 2296 | pond / path, verge, strata | As CP2, plus the lawn shoulder (`i < 4` in Sc.drawPondBank) pokes over the path as a green blob. | as CP2 | as CP2; the shoulder ends behind the path's back edge. | High | 08 |
| CP6 | all,144 | whole level | back lawn / mid-row trees | The lawn's top is a straight line and the bushes' bottoms are cut flat on it; nothing grows up into them. | park_ground.png rows 0-7, Sc.drawFarArt mid row at y 180 - h | A tuft row stamped every 7 px over the bushes' feet, or a 1 px shadow under the row. | Med | 06 |
| CP7 | all,144 | whole level | lawn / path | Dark 1 px line with tufts both sides. Reads as an edge. | park_ground.png rows 7-11, 28-30 | OK | OK | |
| CP8 | 1600,144 | ~1530, ~1760, ~2440 | oak trunk / lawn | The root flares end in a straight horizontal line on the lawn's top row. | Sc.drawTreetops, drawTrunk (scene.lua:2363), trunk art cut at the foot | Roots going into grass: a tuft strip stamped over the trunk's foot, root tips tapering into the lawn, a 1 px shadow. | Med | 10 |
| CP9 | 1860,24 (and every frame at camY 0 and 24) | whole level | mid-row trees / nothing (sky) | With the camera up in the trees the mid row rises at 0.6x and its lawn leaves the screen: tree trunks, bushes and the lamp posts' heads end in a straight line over the flat warm sky colour. | vcam.lua Vc.parallax (Vc.MID 0.6), Sc.drawFarArt mid row (no lawn under it) | A mid lawn strip drawn under the row at the same vertical shift (the bankLawn quad, faded as mid), run down to the screen's bottom. | High | 09 |
| CP10 | 2500,144 | 2624-2688 | path / slide-tower step and slope | Hidden behind the tower art; the path runs on behind it. | Sc.paintGroundArt (`top < foot` clamp) | OK | OK | |

### Downtown tall (`L.art = "town"`, Sc.paintGroundArt; street line 424, street tier camY 240)

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DT1 | 3200,240 | 3488-3520 | cobbles, kerb, quay wall / river stairs | The street ends in one vertical cut: no kerb return, no quoins (Sc.quayEnds only runs where the street meets water). A flat pale wedge shows above the steps (nothing is painted there). The steps have no cheek wall. | Sc.paintGroundArt stair branch (`foot > 184`), Sc.quayEnds | The quay-end corner for any end, not only water; a stair cheek wall with coping; stair tiles at 4 px rise per step with a lit nosing. | High | 11 |
| DT2 | 1630,240 | 1736 and 1848 | cobbles / fountain basin | Quoins and kerb return are there (6 Nov). The basin's far face (grey 12 px courses) meets the purple near wall with no coping overhang and its courses do not line up with the wall. | Sc.drawFarArt basin, Sc.quayEnds | Line the courses up; a 1 px coping overhang with a shadow row. | Low | |
| DT3 | 2430,240 | 2560 and 2624 | cobbles / canal | Kerb return and quoins; reads as a quay end. | Sc.quayEnds | OK (optional wet band at the waterline) | OK | |
| DT4 | 2700,240 | 2816 and 3072 | cobbles / canal | As DT3. | Sc.quayEnds | OK | OK | |
| DT5 | 2950,240 | 3072-3168 | cobbles / GATE block | The granite block stands on the cobbles with no contact shadow, its left side flush with the quay end; its courses do not line up with the quay wall's. | Sc.courtyardGate (scene.lua:2240), arthooks GATE | A plinth row and a 1 px shadow on the cobbles; set back 2 px from the quay end. | Med | 12 |
| DT6 | 960,240 | ~1180, ~2475, ~2815 | mid-row square floor (light band) / tall front plinth | The light pavement band stops dead against the tall fronts' plinths: two floors at different heights meet in a vertical line. | arthooks.lua H.drawTownBack (:674) over Sc.drawFarArt `squareFloor` | A 2-3 px shaded side return on each front's open end and a contact shadow on the band. | Med | |
| DT7 | 0,240 | ~130 | HOME house / square floor | As DT6. | home building art, `squareFloor` | as DT6 | Med | |
| DT8 | 0,120 | upper tiers | mid-row facades / square floor | Facade feet on a floor of the same tone, no shadow line. | `squareFloor` strip, Sc.drawFarArt | A 1 px shadow row under the row. | Low | |
| DT9 | all,240 | whole street | back band / cobbles / kerb / quay wall | Dark edge row and lit kerb present; reads well. | town_ground.png | OK | OK | |

## The 12 worst, 4x

| Crop | Join |
| --- | --- |
| `01_rw_ramp_down_x1280.png` | RW1, RW2, RW3 |
| `02_rw_ramp_up_x3000.png` | RW9, RW10, RW11 |
| `03_rw_quay_end_x1392.png` | RW4 |
| `04_rw_pier_shade_x1936.png` | RW6 |
| `05_rw_hedge_on_asphalt_x110.png` | RW15 |
| `06_cp_earth_strata_x100.png` | CP1, CP6 |
| `07_cp_pond_x704.png` | CP2 |
| `08_cp_pond_x2296.png` | CP5 |
| `09_cp_up_midrow_on_sky_x1990.png` | CP9 |
| `10_cp_oak_roots_x1760.png` | CP8 |
| `11_dt_river_stairs_x3488.png` | DT1 |
| `12_dt_gate_block_x3072.png` | DT5 |

## Common causes

1. **One column at a time, no neighbours.** Sc.paintQuay `column(x)` and Sc.paintGroundArt paint each x on its own from a recipe for that column's kind. A change of kind is therefore always a one-column vertical seam. Ends are then patched case by case (`cornerColour`, the `d <= 3` coping, Sc.quayEnds), each for one situation only: Sc.quayEnds fires only next to water, so the river stairs' head gets nothing, and no patch draws anything onto the neighbouring column (no overhang, no shadow).
2. **The ground is a stack of horizontal strata.** pavement.png, park_ground.png and town_ground.png are stamped per column from `top - 12`. Where a column ends, the whole stack ends at once (CP2 to CP5, RW4, DT1); nothing turns the corner.
3. **Slopes are the flat recipe shifted.** The ramp offsets slab rows per column (RW2, RW9); the stairs floor the slope to 4 px but keep a flat fill. There are no slope tiles.
4. **No contact pass.** Nothing stamps a shadow row, a plinth or a grass strip where an object or a layer meets the ground: houses (RW12, RW13), trunks (RW14, CP8), the GATE block (DT5), the hedges (RW15), the mid rows (CP6, DT8).
5. **Parallax layers with no ground of their own.** City Park's mid row (CP9) and Downtown's square floor (DT6, DT7) end where the layer's art ends; when the camera moves up, or a nearer front cuts across, the edge shows.
6. **Texture removed on 6 Nov.** tools/fix_cp_audit.py turned the earth strata into flat bands to remove specks; that left CP1 as plain stripes.

## Proposed fix approach

One transition pass by rule, in place of per-spot patches:

1. **Kind map.** Keep the per-column `top` and `kind` that Sc.paintQuay already works out and add it to Sc.paintGroundArt (road, quay, ramp, stair, path, water, pond).
2. **Transition kit on the 8 px grid**, built once by a tools/make_ground_kit.py (flat fills and 2-4 colour parts, per level palette): end caps (coping overhang, wet band, quoins), kerb returns, landing slabs, a near pond bank, grass tuft strips, a 1 px contact shadow, a lip or overhang row, and slope tiles at 1, 2 and 4 px rise per step (smooth ramp, stepped ramp, stairs), each with a lit top edge and courses square to the slope.
3. **A rule table** (kind A, kind B, height change) to piece, stamped at every change in the kind map after the columns are painted, so every join of the same kind looks the same and new levels get it free. Sc.quayEnds and `cornerColour` become two rows of that table.
4. **A contact pass** for things standing on the ground: a shadow row and a tuft or plinth strip under every building, trunk, block and hedge, from its box.
5. **Layers get their own ground:** a mid lawn strip under City Park's mid row at the same vertical shift; a side return and shadow on Downtown's tall fronts over the square floor.
6. **Earth front by rule** for City Park: grass lip, stones and roots on a grid, toothed band edges, in place of the flat stripes.

Check after the fix: the same sweep, plus a script that lists every kind change from the kind map and fails if any lacks a stamped transition.
