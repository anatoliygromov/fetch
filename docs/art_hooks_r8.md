# Art hooks for the first batch (r8/levels, 23 Oct)

The game looks for each file below by name. When a file is there it is drawn; when it is not, the game draws what
it drew before (today's art) or a placeholder in code. So a finished piece goes in by copying it to its name: no
code change. Rename the art agent's files (docs/art_batch1.md on `r8/art`) to these names.

All art at 1x game pixels, PNG with transparency. Obstacles (things Pepper stands on or is hurt by): crisp, with
their own 1 px dark outline. Decoration: no outline; the game fades it towards the haze itself (28%, the far lane
40%, the spire 45%), so deliver it at full colour. Code: `riverwalk/arthooks.lua` (cargo bike, tram, roof kit, house
fronts, spire), `riverwalk/road.lua` (cyclists), `riverwalk/bonus.lua` (Mia's throw), `riverwalk/scene.lua` (the
row across the square).

**Try a file without committing it:** put it in the LOVE save folder under the same path (for example
`$XDG_DATA_HOME/love/pepper_riverwalk/art/scene/cargo_bike.png`); LOVE reads the save folder before the game folder.
`tools/preview_art_hooks.py <save folder>` writes labelled stand-ins for every hook there, to see each anchor
(`love riverwalk --level downtown_tall --test` then shows them in its screenshots).

Coordinates: x grows right, y grows down. "Anchor" is the pixel of the image that is put on the named point.

## Downtown street (both Downtowns)

| File | Size (px) | Facing | Anchor and rules | Replaces |
| --- | --- | --- | --- | --- |
| `art/scene/cargo_bike.png` | 116 x 88 (6 Nov: true scale, rider 1.85 m with the helmet = 85 px at 46 px/m, bike 2.5 m; any size works) | **left** (it rides left) | Left edge = the hit box's left edge (the bike's front); bottom row = the wheel line (the street). The hit box is the left 80 px of the image and its bottom 26 px: the front wheel and the cargo box. The rider sits over the back wheel, right of the box. Crisp, outlined (an obstacle) | the code-drawn box bike |
| `art/scene/cargo_bike_pedal.png` | frames of the still's size side by side (8 x 116 = 928 x 88) | left | Frame 1 at x 0, frame 2 at x 116, ... The game steps one frame per `H.CARGO_PEDAL_PX` (13) px ridden and loops; the frame count is the width divided by the still's width. Optional: without it the still is drawn | the still |
| `art/scene/tram_vintage.png` | 586 x 188 (6 Nov: true scale, 12.7 m body, 3.3 m to the clerestory at 46 px/m, the trolley pole above) | **left** | Centred on the tram's x; bottom row = the rails (the street line minus 10, behind Pepper's line). The driver in the front (left) cab window; a trolley pole on the roof. No outline, no logos. The front door's middle is 60 px from the left end (`H.TRAM_ART.door`): the tram stops with it at the stop sign. Its wheels: `tram_vintage_wheel.png`, 4 frames of 31 x 31 side by side, centres `H.TRAM_ART.wheels` (x in the image) and 16 px above the rails, drawn behind the body, one frame per 3 px ridden | the code-drawn tram (300 x 130, door 24 px in) |

The courtyard gates (were the tram sheds) keep `town_tramshed70.png` and `town_tramshed96.png`; their rows below the
box (the old rails) are no longer drawn.

## Promenade and road cyclists (River Walk)

| File | Size (px) | Facing | Anchor and rules | Replaces |
| --- | --- | --- | --- | --- |
| `art/scene/cyclist_adult1.png`, `cyclist_adult2.png` | 88 x 87 (5 Nov: true scale, 1.85 m with the helmet = 85 px at 46 px/m; wheels 31 px; 2 px clear each side so no wheel touches the edge) | **right** (mirrored when riding left) | The promenade bikes: centred on the bike's x, bottom row on the pavement (the hit box stays 70 x 28, wheel to wheel). The road's cyclists: top row at y 190 (below Pepper's feet; the frame crops the wheels, as now) | `road_cyclist1-2.png` (both uses) |
| `art/scene/cyclist_adult1_pedal.png`, `cyclist_adult2_pedal.png` | frames of the still's size side by side (8 frames: 704 x 87, no gutter: the game cuts each frame by the still's width) | right | One frame per 26 px ridden (road.lua `Rd.PEDAL_PX`: a pedal turn about once a second at riding speed), looped. Optional: without it the still is drawn (the old `_roll` wheel frames are not used with the new riders) | `road_cyclist1-2_roll.png` |
| `art/scene/road_rider1.png`, `road_rider2.png` | 105 x 110 (7 Nov, tools/build_bikes_n07.py: the bike lane's 55 px/m, like the cars; the render's riders are 1.98 m with the helmet, the bike the promenade geometry x 55/46; was 104 x 102) | **right** (mirrored when riding left), lit from the upper left | The road's bike lane only: top row at y 190, rows 0-49 show (head, body, hands); no pedal loop | the promenade riders in the lane |

## Mia's throw (FETCH FRENZY, the bonus round)

| File | Size (px) | Facing | Anchor and rules |
| --- | --- | --- | --- |
| `art/girl_throw.png` | one row of 8 frames of 66 x 66 (528 x 66), as `girl.png`'s cells | right | Feet centre at (33, 66) of each cell. Frame 1 standing with the item; 2 to 5 the wind-up (the ball behind her head, the step forward), shown over the 0.36 s before she lets go; 6 the release; 7 and 8 the follow-through (0.3 s). The item is drawn by the game (ball, stick or frisbee) at her hand: about (-13, -27) from her feet in frames 1-2, (-15, -39) in 3, (-11, -45) in 4-5, and it leaves at (15, -33) in frame 6, so her hand should be there (no ball in the art). Needs all 8 frames, else the old wave and cheer clips are used |

## The tall Downtown's old town (D2)

The high road's pieces are obstacles: crisp, outlined, front-on with only a thin top edge. **Rule for every roof kit
piece: the image's top row goes 1 px above the box's top (the outline over the edge Pepper walks on), and it is
centred on the box.** So make it the box's width + 2. What hangs below the top (the loggia's arcade, the gallery's
balusters, the dormer's window) is drawn below; Pepper only stands on the top.

| File | Box in the level (x, y top, w x h) | Image | Notes |
| --- | --- | --- | --- |
| `art/scene/town_roof_loggia.png` | LOGGIA 1416, 280, 120 x 6 | 122 x about 48 | arcade front under a cornice; it sits on a back house front (1404-1548) |
| `art/scene/town_roof_gallery88.png` | GALLERY 1680, 256, 88 x 6 | 90 x about 32 | a balustrade (the first half) |
| `art/scene/town_roof_gallery72.png` | GALLERY 1816, 256, 72 x 6 | 74 x about 32 | the second half (`town_roof_gallery.png` is used for both if the sized ones are missing) |
| `art/scene/town_roof_chimney.png` | CHIMNEY 1628, 200, 16 x 44 (solid) | 18 x 46 | brick with a stone cap; the golden bone sits on its top, so pots must not rise above the top row |
| `art/scene/town_roof_dormer.png` | DORMER 1920, 264, 56 x 6 | 58 x about 36 | copper cap (the top) over a little window gable |
| `art/scene/town_roof_flower_roof.png` | FLOWER ROOF 2288, 232, 88 x 6 | 90 x about 14 | a ledge with flower boxes along its front |
| `art/scene/town_roof_gable.png` | GUILD ROOF 1560, 272, 8 x 6 and the 10 steps right of it to x 1680; the highest step top y 244 | 122 x about 80 | the guild house's stepped gable. **Anchor: top-left at (1559, 243)** = the steps' left - 1, the highest step's top - 1. Each step's top must be on its box's top (8 px wide steps, 4 px apart in height: 272, 268, 264, 260, 256, 252, 248, the top 1616-1656 at 244, then 248, 252, 256 down to 1680) |
| `art/scene/town_roof_ledge.png` | the unnamed ledges: 2016, 248, 56 x 6; 2112, 264, 56 x 6; 2416, 248, 48 x 6 | at least 12 wide, about 9 tall | a stone ledge drawn as a **3-slice**: the left 4 px, the middle repeated, the right 4 px; top row at the box's top - 1 |
| `art/scene/town_footbridge.png` | FOOTBRIDGE 2480, 272, 160 x 6 (solid) | 162 x about 52 | **the top 12 rows are the railing** (behind Pepper, thin), row 12 is the deck's outline (box top - 1), then the deck and a shallow arch below. Centred |
| `art/scene/town_front_tall1.png`, `2`, `3` | the back boxes under the roofs: BAKERY 1180-1320 (300-414), 1320-1400 (278-414), 1404-1548 (286-414), GUILD HOUSE 1552-1700 (250-414), 1912-2180 (270-414), 2296-2384 (238-414) | 80, 88, 96 x **240** | decoration (no outline). Each box is filled left to right with front 1, 2, 3, 1, ... in turn, each standing on the box's bottom (y 414, the decoration base) and **cut at the box's top** (the roofline the route runs on) and at the box's right end. So the lower 136 to 176 px always show: put the doors and the shop fronts at the bottom, the storeys above; 240 tall covers every box |
| `art/scene/town_row.png` | the near facades layer (both Downtowns), scrolls at 0.5 | 320 x about 130, repeats | the row of old town houses across the square, with volume; stands on screen y 178 (as `town_facades.png`, which it replaces); faded 40% by the game |
| `art/scene/spire_riddarholmen.png` | RIDDARHOLMEN 3380-3412, 24-414 | 32 x about 400 | the far landmark: centred on the box, standing on its bottom (y 414); faded 45% by the game; no outline |

Not hooked (they already have art): the high road's BALCONY (`drawBalcony`), the springy window AWNING (the awning
art), the SIGN boards, Downtown's HOUSE fronts with their balconies (`town_house1-3.png`), the cafe and street
pieces.

## Landed on art/placement (23 Oct): built from stamped parts, 0 credits

The high road's pieces and the fronts under them are drawn by `tools/build_roof_kit.py`, `tools/build_tall_fronts.py`
and `tools/build_spire.py` (each `--check` proves the file is what it builds). Changes to the slots above, because the
fronts are now true scale (46 px a metre: a door 2.0 m = 92 px) and a piece hanging lower than about 25 px under its
roofline would cover the doors and shop fronts:

| File | Size | What changed |
| --- | --- | --- |
| `town_front_tall1-3.png` | 80, 88, 96 x 240 | One ground-floor **bay** each (a door, a shop front, a carriage gate), every feature centred, at most 70 px wide and below row 131 (the lowest box, 114 px, shows rows 126 on). A box is one building: arthooks.lua splits it into bays of about 88 px (or the box's property `fronts`, "2,1"), crops each bay symmetrically or widens it with its own edge column, swaps the yellow plaster ramp for the box's `plaster` (yellow, red, cream, ochre, stone) by exact colour, then fades it; the cut at the box's top gets a stone coping, its right edge a 2 px shade |
| `town_roof_gable.png` | 122 x **40** (was about 80) | Coped brick steps on the 8 x 4 px boxes, an oculus, a string course at its foot (y 282); the GUILD HOUSE box now starts there (y 282), so the gable stands on the house |
| `town_roof_loggia.png` | 122 x **26** (was about 48) | A cornice over a blind arcade of five round arches |
| `town_roof_ledge.png` | 16 x 9 | 3-slice as above (left 4, middle 8, right 4) |
| `spire_riddarholmen.png` | **36 x 260** (was 32 x about 400) | Drawn far (arthooks.lua `H.drawFarSpire`, called by scene.lua between the far roofs and the facades): scroll 0.3, the shore's haze and fade, placed so that at the level's end it stands where its box is, its tip 8 px under the screen's top. It was at scroll 1.0 in front of the facade row |

The other pieces keep their slots: chimney 18 x 46, gallery 90 x 32 and 74 x 32, dormer 58 x 36, flower roof 90 x 14,
footbridge 162 x 52. New back boxes (maps/downtown_tall.tmx) put a house under every high road piece that floated:
1700-1912 (top 288, the galleries), 1912-2000 / 2000-2088 / 2088-2180 (270 / 256 / 272, the dormer and the two
ledges; the old 1912-2180 box), 2180-2296 (240, the window awning), 2384-2480 (256, the ledge and the footbridge's
left end), 2640-2736 (262, its right end).

## How to switch a piece off

Delete (or rename) its file: the placeholder or the old art comes back. The placeholders are in `arthooks.lua`
(`cargoCode`, `tramCode`, `kitCode`, `frontCode`, `spireCode`).

## Downtown sample screen (art/dt-sample-05nov, decisions 1a and 4a; review round 1)

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `town_front_tall1-3.png` | 80, 88, 96 x **432** | as above, but every front box (and any box without `cut`) is drawn at its full height: the file's bottom on y 414, its top at y -18 (two upper storeys of 140 px over the 152 px ground floor), no coping; a gap of up to 8 px to the next front is closed by the last bay |
| `town_front_tall4.png` | 148 x 432 | the GUILD HOUSE's front (its gate, the upper windows at the sides) |
| `town_portal_top.png` | 122 x 50 | the stepped gable (GUILD ROOF and the steps right of it) as the guild house's portal top: at the steps' x0 - 1, top - 1 |
| `town_oriel.png` | 18 x 45 | the CHIMNEY (16 x 44, solid) exactly: the bay window's central pier with a copper cap (the golden bone's perch), at x0 - 1, y0 - 1 |
| `town_oriel_bay.png` | 58 x 44 | decoration: the bay window round it (roof, two lights, corbel), centred on the CHIMNEY box, bottom on the box's bottom, drawn with the fronts |
| `town_crates70.png` | 71 x 37 | a GATE (70 x 36) whose right end is in a full-height house: at x0 - 1, y0 - 1, drawn before the cargo bikes (another GATE keeps the old gate piece) |
| `town_breadboard.png` | 74 x 12 | the SHELTER's one-way perch (72 x 4, 48 px up): at x0 - 1, y0 - 1, drawn before the cargo bikes |
| `town_crate_leg.png` | 18 x 37 | two per SHELTER (play, outlined): at its box's x0 - 1 and x1 - 17, bottom on the street (y 424), before the cargo bikes |
| `town_shelter_tall.png` | 140 x 115 | decoration: centred on the SHELTER box, bottom on y 414, drawn after the tram |
| `town_gateway.png` | 80 x 138 | decoration: centred in the bay that holds the GATE's right end, bottom on y 414, drawn with the fronts |

## Downtown redraws and fixes (art/dt-built-06nov, the board's calls of 25 Oct; 0 credits)

Built from parts by `tools/build_dt_built.py` (`--check` proves each file), hand fixes by rule in
`tools/fix_dt_06nov.py` (every changed pixel in `art/source/<name>/edits.json`). Sizes from metres:

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `town_facades.png` | 806 x 210 | the old town row at its layer's true scale (23 px/m: ground floor 76, first floor 70, then a gable or roof); a strip at scroll 0.5, bottom on screen y 178, as before (scene.lua, unchanged) |
| `town_roofs.png` | 524 x 254 | the far roofs at 13 px/m (storeys 39, windows 8 x 12), two church towers; a strip at scroll 0.25, bottom on y 160, as before |
| `town_door.png` | 140 x 432 | the start door as Pepper's home: a house front at the level's left end (its left on x 0), the door 2.1 m (97 px), the street's upper storeys; bottom on y 414 (scene.lua DOOR, as before) |
| `town_tramshed96.png` | 160 x 161 | screen 10's GATE (3072-3168, no house front there): the sample screen's gateway in a 3.5 m plastered courtyard wall, decoration, centred on the box, bottom on y 414 (arthooks.lua `H.freeGate`, `drawTownGateways`). The flat Downtown draws its old code gate for it (scene.lua `courtyardGate`) |
| `town_gatestep96.png` | 98 x 37 | that GATE's solid box (96 x 36): the gateway's granite doorstep, play, outlined, at x0 - 1, y0 - 1 (`drawTownPerches`) |
| `town_house3.png` | 52 x 118 | unchanged slot (the plaza house scale is the owner's open decision 2) |
| `town_bollard.png` | 16 x 54 | 0.9 m at the front's 60 px/m; its top at screen y 221 as before (only the top 19 rows show) |

## Downtown roof kit, spire and code-drawn pieces rebuilt (art/dt-roofs-06nov, 0 credits)

Built from parts drawn once, in the sample screen's ramps and ink (every colour from `art/palettes/downtown.gpl`):
`tools/build_roof_kit.py` (the roof kit), `tools/build_spire.py`, `tools/build_dt_details.py` (the rest). Each script's
`--check` proves the file is what it builds. Sources: `art/source/dt_roofs/*.aseprite`. Without a file the game draws
what it drew before (the code fallback stays).

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `town_roof_loggia.png` | 122 x 26 | as before (LOGGIA); granite about 103 on screen, so `H.STONE_TINT` is empty now |
| `town_roof_gallery88.png`, `town_roof_gallery72.png` | 90 x 32, 74 x 32 | as before; vase balusters (8 x 20, drawn once) on a 10 px pitch; no tint |
| `town_roof_flower_roof.png` | 90 x 14 | as before |
| `town_roof_ledge.png` | 16 x 9 | as before, a 3-slice: one modillion per 8 px middle tile |
| `town_footbridge.png` | 162 x 52 | as before |
| `spire_riddarholmen.png` | 36 x 260 | as before (far, the shore haze at the shore's 0.70); a silhouette in 8 colours |
| `town_balcony56.png`, `town_balcony64.png` | 58 x 60, 66 x 60 | a BALCONY w wide (scene.lua drawBalcony): at x0 - 1, y0 - 1 - `Sc.BALCONY_RAIL` (46); the slab's ink row is row 46; an open railing (fix round 1) |
| `town_spring.png` | 36 x 10 | the coil (scene.lua `Sc.spring`): 4 frames 9 x 10 for h = 7, 8, 9, 10; rows 0 .. h - 1 of frame h - 7 at x - 4, y |
| `town_stopsign.png` | 19 x 101 | the tram stop sign (arthooks.lua stopSign), faded as back decoration: column 9 on the stop's x + 1, bottom on the rail line |
| `town_jet.png` | 24 x 88 | the fountain's water (scene.lua drawTerrainArt): 4 frames 6 x 88 at 20 fps; left at the TIER's x0 - 7, the right one mirrored at x1 + 7, top at the TIER's top + 3 |
| `town_tier.png`, `town_bowl.png`, `town_rim.png` | 50 x 58, 34 x 82, 18 x 18 | as before, redrawn in the sample's granite |

## River Walk harbour and kennel, built by parts (night/06nov-rw, SpriteCook 64 for the rower)

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `rw_rowboat.png` | 185 x 62 | the ROWBOAT hull (setpieces.lua `Sp.drawRowboat`), built by `tools/build_rw_rowboat.py`: bow left; its left column at the mover's x0 - 25, its top row at the mover's y0 - 36 (row 36 = the rail = Pepper's deck, y 212; row 48 = the waterline, y 224). Outlined (an obstacle). The water's tint under row 48 is drawn in code |
| `rw_rower.png` | 644 x 62 (7 frames of 92 x 62) | the rower (at the stern thwart, rowlock hull x 150), the oar and his near arm, drawn over the hull at hull x 106, same top; frames 1-6 the stroke while the boat moves right (7 fps), backwards while it moves left, frame 7 at rest (the oar shipped along the hull). Nothing below the rail of its own column except the oar (it is outboard) |
| `kennel.png` | 44 x 44 | the KENNEL piece (setpieces.lua kennel()), built by `tools/build_rw_kennel.py`: top-left at (x0, y0) = (0, 140), bottom row on the path (y 183); the doorway's crown on row 25 (y 165). Outlined. Its collision: the ridge cap x 16-28 from y 140 and the eaves x 0-44 from y 158 |
| `rw_jetty.png` | 48 x 51 | the jetty, built by `tools/build_rw_jetty.py`: its bottom row on world y 239 (the deck's ink row on y 195, the box top 196), x on the JETTY piece's x0; the water's tint under y 224 and a ripple round each pile in code |
| `ferry.png` (7 Nov: rebuilt by rule, tools/build_ferry_n07.py, same lines) | 252 x 79 | the BOAT prop has `wet = true`: setpieces.lua tints its columns under y 224 and runs a ripple row along it |
| `pontoon.png` (unchanged) | 54 x 19 | in code its floats take the water's tint under y 224 (`Sp.pontoonWater`); its mooring lines sag |

## City Park (tall), night 6 Nov (cp track)

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `cp_willow.png` | 474 x 508 (10 m crown, kept at this size: review round 1, 6-7 Nov night) | the tall level's weeping willow (scene.lua `Sc.bigWillow`, drawn first in `Sc.drawTreetops`): its trunk's centre (30 px over its foot) on the WILLOWS crown's middle (x 804), its last row on the back props line (`def.foot - 10`), faded 0.28 (`TREE_FADE`); the old park_willow / park_willow_tall are not drawn on that level |
| `cp_lime.png` (reused) | 371 x 509 | now also the LIMES trunks at x 1004, 1216 and, mirrored whole (`cp_lime@flip`), 1112 and 1420 (scene.lua TREE_ART) |
| `cp_reeds.png` | 32 x 34 (2 cells of 16 x 34) | `Sc.drawPondKit`, with each park pond's water: both cells in each corner (base on the curved shore's row), cell 2 on the far bank at a third and two thirds when clear of a stepping stone; base row = the cell's last row |
| `cp_lily.png` | 30 x 4 (3 cells of 10 x 4) | `Sc.drawPondKit`: one every 52 px from 14 px in, rows 3 to 9 under the waterline (`p.y0 - Sc.POND_RISE`), off the stepping stones |
| `cp_bankstones.png` | 24 x 7 (2 cells of 12 x 7) | `Sc.drawPondKit`: one per pond end, 9 px in, bottom row on the shore |

## Downtown high road attached to its fronts (art/dt-highroad-06nov, 0 credits)

Built by `tools/build_highroad.py` (`--check`) from the 5 Nov fronts' parts and the roof kit's ink and granite.
Drawn by `arthooks.lua` (`townPiece`, `H.drawHighWall` after the fronts). No box moves. Without a file the game draws
what it drew before. One flag: `H.PLAZA_FRONTS` (decision 2a; `false` brings back the plaza houses).

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `town_front_tall6.png` | 148 x 432 | the GUILD HOUSE's front (instead of front 4): granite ground floor, its top on the steps' line, a 2.1 m door at x 1632, French windows at x 1580 and 1674 |
| `town_front_tall5.png` | 88 x 432 | a plain bay (no door, shop or gate): with `H.PLAZA_FRONTS`, any bay whose door, shop or gate a plaza BALCONY would cross |
| `town_guild_steps.png` | 122 x 35 | the stepped coping on GUILD ROOF and its steps: at the steps' x0 - 1, top - 1 (instead of town_portal_top) |
| `town_guild_pier.png` | 18 x 46 | the CHIMNEY box as a stone pedestal: at x0 - 1, y0 - 1 (instead of town_oriel; no town_oriel_bay) |
| `town_console.png` | 8 x 7 | under both ends of every ledge (unnamed, DORMER): at x + 2 and x + w - 10, y0 + 4 (its ink row on the slab's) |
| `town_window_door.png` | 52 x 50 | decoration: the first-floor window carried down to a high BALCONY or a ledge under it (window within 8 px): at the window's x - 25, front foot - 192, cut at the slab |
| `town_window_rail.png` | 44 x 24 | decoration: a French balcony's flush railing over a ledge: at the window's x - 22, its foot on the ledge's top - 1 |
| `town_balcony_door.png` | 38 x 52 | decoration (`H.PLAZA_FRONTS`): behind a plaza BALCONY, centred on it inside its house, top at the front's foot - 119, cut at the slab |
| `town_pilaster.png` | 14 x 101 | decoration: two per LOGGIA, 3 px in from its ends, from its top + 25 to the plinth; the house under a LOGGIA is one bay (its gate centred) |
| (code) | | the galleries' string course: the fronts' course (5 rows) at a GALLERY's top + 31 along the whole front of each house it stands on; cast shadows of every high road piece and balcony, 2 px right and 3 down, multiplied so the wall's W turns into its S |

## Downtown (tall) audit fixes (art/dt-audit-06nov, 0 credits)

Built by `tools/build_dt_audit.py` (`--check`); `town_rim.png` by `tools/build_dt_details.py`. Review: `docs/review/06nov/dt_audit/`.

| File | Size | Where and how it is drawn |
| --- | --- | --- |
| `town_ground.png` | 240 x 68 | as before (scene.lua paintGroundArt); rows 32-67, the quay wall, are flat granite courses |
| `town_rim.png` | 18 x 18 | each RIM at x0 - 1, y0 - 1, as before: a granite corner bollard |
| `town_quaydrain.png` | 20 x 22 | decoration in the quay wall (arthooks.lua `H.drawQuayDrains`, after the ground): one per front-layer prop, its bottom 2 px over the world's bottom, on dry quay only. The tall Downtown draws no front bollards |
| `town_bridge_pier.png` | 14 x 113 | decoration, unfaded (`H.drawBridgePiers`, the back pass): centred under each foot of the FOOTBRIDGE's arch, from the foot to the street |
| `town_punt.png` | 52 x 14 | play, outlined (scene.lua PARASOL with no table over water): its gunwale at the street + 13, the pole's foot 2 px inside it |
| `town_lantern_bracket.png` | 18 x 12 | back, faded as the lamp (`H.wallLantern`, stage.lua): a lamp on a high-road ledge is the lamp's lantern (rows 0-26) hanging from this bracket, 44 px over the ledge, on the house front's nearest bay edge |
| (code) | | `Sc.quayEnds`: kerb corner and quoins where the street ends at water; the far quay's coursed face and the waterline in a town pool; `H.flowerBrackets` under the FLOWER ROOF; street awnings' counters and missing posts (scene.lua AWNING); CRATES drawn only above the street; the tram's fade 0.10; the stop sign after the shelter |

## Downtown facade lift (night/06nov-dt, 0 credits)

Built by `tools/build_dt_facades.py` (`--check`) after the producer's concept dt_highroad_concept_a (design only).

| File | Size | Slot and anchor |
| --- | --- | --- |
| `town_front_tall<k>_<s>.png` | 80 / 88 / 96 / 88 / 148 / 148 x 432 (k 1, 2, 3, 5, 6, 7) | as `town_front_tall<k>.png`: a front box whose `style` property is s (a-f) draws them (arthooks.lua `frontImg`, `H.STYLED`); the plaster W / S swapped per box; window glass, frame and sill rows unchanged (the carried-down French windows meet them). k 7: the LOGGIA's house as one 148 px portal bay, two window axes (x 40, 108) |
| `town_drainpipe.png` | 6 x 432 | a full-height front box with `pipe` = true: at its right end - 8, bottom on the box's bottom (y 414), faded as the fronts |
| `town_bridge_springer.png` | 14 x 20 | play, outlined: the FOOTBRIDGE's arch feet, on the two house corners, top at the bridge art's row 42; the right one mirrored (arthooks.lua townPiece) |
| `town_basin_wall.png` | 10 x 56 | ground: under a fountain RIM on the water's side, from the rim's bottom (y 424) down; mirrored on the right (scene.lua RIM) |
| `town_shelter_tall.png` | 140 x 115 | unchanged slot (decoration, centred on the SHELTER, bottom on y 414), redrawn in green cast iron |

## The sky (day of 7 Nov, look.lua Look.PAINTED; LOOK_SKY=bands is the old band sky)

| File | Size (px) | Facing | Anchor and rules | Replaces |
| --- | --- | --- | --- | --- |
| `art/scene/sky_riverwalk.png`, `sky_citypark.png`, `sky_downtown.png` | 960 x 360, opaque | - | Built by `tools/build_sky.py` (`--check`). Row 0 = screen y -120 (a tall level's sky above y 0); a flat level draws rows 120-359 at y 0. Wraps sideways: drawn at 0.05 of the camera plus 2 px a second (Look.SKY_SPEED, Look.SKY_DRIFT), no look shader. 4-6 sky tones + 4 cloud tones (clouds luma 185 or more) | the band sky and the drifting cloud sprites (cloud1-8 are no longer drawn while it is on) |
| `art/scene/skyline_riverwalk.png`, `skyline_citypark.png` (320 x 77); `skyline_downtown.png` (320 x 30: the low simple city, built from flat, gable and dome parts, tops 20-28 px, no spires) | 320 x 77 / 320 x 30 | - | Built by `tools/build_sky.py` from the approved `skyline.png` (unchanged): its silhouette in 2 clean tones plus a 1 px warm rim on the lit edges. Bottom at y 138 (River Walk) or 150 (art levels), repeats every 320 px, drawn with the neutral city look (final colours) | `skyline.png` under the city haze |

## River Walk and City Park ground, the owner's reverts, the kennel garden (day/07nov-ground, 0 credits)
| File | Size | Where the game draws it |
| --- | --- | --- |
| `kennel.png` | (removed) | owner 7 Nov 12:45: "I don't think we need kennel really, let's assume the dog lives at home". The file, its boxes, its piece and the GARDEN prop are out of River Walk; `tools/build_rw_kennel.py` can rebuild the round 3 low gable. The gold bone stays at x 16 on her doorstep (secret DOORSTEP) |
| `gritbox_front.png` | 88 x 32 | unchanged slot; the front-on build in the old box's greens (`tools/fix_gritbox_07nov.py`) |
| `pontoon.png` | 54 x 12 | the previous pontoon again, drawn at the mover's x0 - 3, y0 - 2 (`Sp.PONT_DY`); the mooring lines tie on under the deck's ends |
| `park_stone.png` | 26 x 21 | the previous pink granite stone again (as the cp-pond branch drew it) |
| `park_ground.png`, `road.png` | 240 x 68, 640 x 41 | the previous textured files again (`tools/revert_ground_07nov.py`, `tools/make_road.py`) |
| `kit_cp_midlawn.png` | 240 x 96 | City Park tall only: under the mid row (top y 176, scroll 0.5, faded as mid) and under the far tree line (top y 175, scroll 0.25, faded as the shore), scene.lua `Sc.drawFarArt` |
| `kit_cp_tufts.png` | 240 x 5 | City Park tall: over the mid row's feet, rows 176-180, scroll 0.5, faded as mid |
| `kit_cp_roots.png` | 48 x 5 | City Park tall: over every tree foot (bottom on the foot line), a 48 px pattern anchored in the world, faded as the back (scene.lua `rootTufts`) |

## Downtown (tall): the low row, option A (day/07nov-dt, 7 Nov, 0 credits)

The owner's pick of 7 Nov (docs/review/07nov/dt/design/README.md): the street is lined with low true-scale buildings
whose roofs are the high road; the tall houses stand on the mid row behind; sky above. `tools/build_dt_rooftops.py`
(`--check`) writes the files and `riverwalk/dt_lowrow.lua`, the placement table `arthooks.lua` reads (`H.LOW_ROW`;
with the table absent everything draws as before).

| File | Layer | Placed | Built from |
| --- | --- | --- | --- |
| `dtl_<building>_front.png` (start, bakery, wing, arcade, guild, pav1, pav2, shed, kioskhouse, shelterhouse, hall, canalhouse, closed1-22) | back, faded 28 % | `H.drawLowRow`: the table's `fx, fy` (top-left, world); the bottom row on the back line 414 | the approved styled fronts' ground floors (rows 284-431, plaster swapped as `plasterImg`), `town_door` (the start house), `town_gateway` (the shed); the arcade, the guild's ashlar and the glass hall drawn by rule; the decorative roofs in the fronts' own ramps |
| `dtl_<building>_roof.png` | play, outlined, unfaded | `H.lowRowPiece`: drawn when the building's trigger box is drawn, at `rx, ry`; the walk's ink row at the box's top - 1, the image the box + 1 px a side | tile courses, lead sheets, granite coping and parapet, the guild's crow steps, the chimney, the shed's dormer, the hall's flower boxes |
| `dtl_<building>_canopy<k>.png` | play, outlined | the middle tier: PORCH (1568, 312), CANOPY (1680, 336), (1816, 344) | a granite slab on brackets over the guild door; cloth canopies in the street awning's ramp over the pavilions' shop windows (round 2) |
| `dtl_fountain_basin/rim/plinth/column.png` | basin: ground (unfaded, no outline); the rest play, outlined | FOUNTAIN (1776, 400) draws the plinth and the basin band, RIM (1720/1848, 408) the rim blocks, TIER (1768, 344) the column with the bowl and the ball finial (top 296); jets in code (`H.drawLowFountainJets`) | round 2, the A2 concept |
| `town_facades.png` (960 x 244) | mid, scroll 0.5, moving with the world (`L.vmid = 1.0`, vcam.lua) | `strip(T.facades, ...)`, its foot at screen 190 on the street tier (`Sc.MID_FOOT_LOW`, world 430: under the street line) | rebuilt at half size, three storeys, tinted, 14 colours (round 3) |
| `dtl_canalhouse_canopy1.png` | play, outlined | CANOPY (2420, 328) | the canal house's cloth canopy (round 3) |
| (no far band) | | in low-row mode the far roofs and spires strip is not drawn; nothing between the mid row and the sky (round 5; the painted sky branch brings its own skyline) | |
| `dtl_fountain_face.png` | ground, ungraded | `H.drawLowRaw` with the quay wall (stage.lua, Look.off()) at (1736, foot) | the basin's face below the street (round 4) |

Map (`maps/downtown_tall.tmx`): BALCONY 1552 y 344 -> PORCH 1568-1618 y 312 (a porch over a 2.1 m door), DORMER 1920-1976 -> SHED ROOF 1912-2000
(the whole shed roof), FLOWER ROOF 2288-2376 -> 2216-2376 (the whole hall roof; the springy awning's bounce now ends on
it), the middle tier's balconies -> CANOPY 1680-1752 y 336 and 1816-1888 y 344, GATE 1868 -> 1864-1934 with zone 1's depot
at 1934 (the shed gate's left jamb). The high road's boxes renamed to what they are (WING ROOF, ARCADE ROOF, PAVILION ROOF,
SHED ROOF, KIOSK ROOF, SHELTER ROOF, CANAL ROOF). Every other box unchanged. Hidden by the table (claims): the HOUSE boxes, the plaza balconies' rails
(`Sc.drawBalconyRails`), the tall fronts, the high lamps' wall brackets (a post on the roof instead).
