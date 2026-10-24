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
| `art/scene/cargo_bike.png` | 96 x 76 (any size works) | **left** (it rides left) | Left edge = the hit box's left edge (the bike's front); bottom row = the wheel line (the street). The hit box is the left 80 px of the image and its bottom 26 px: the cargo box and the front wheel. The rider sits over the back wheel, right of the box, his head about 76 px up. Crisp, outlined (an obstacle) | the code-drawn box bike |
| `art/scene/cargo_bike_pedal.png` | frames of the still's size side by side (8 x 96 = 768 x 76) | left | Like the cyclists' `_roll` sheets: frame 1 at x 0, frame 2 at x 96, ... The game steps one frame per 6 px ridden and loops; the frame count is the width divided by the still's width. Optional: without it the still is drawn | the still |
| `art/scene/tram_vintage.png` | about 300 x 130 | **left** | Centred on the tram's x; bottom row = the rails (the street line minus 10, behind Pepper's line). A driver must be visible in the front (left) cab window; a trolley pole on the roof. No outline, no logos. The front door is about 24 px from the left end: the tram stops with it at the stop sign | the code-drawn tram |

The courtyard gates (were the tram sheds) keep `town_tramshed70.png` and `town_tramshed96.png`; their rows below the
box (the old rails) are no longer drawn.

## Promenade and road cyclists (River Walk)

| File | Size (px) | Facing | Anchor and rules | Replaces |
| --- | --- | --- | --- | --- |
| `art/scene/cyclist_adult1.png`, `cyclist_adult2.png` | about 76 x 76 | **right** (mirrored when riding left) | The promenade bikes: centred on the bike's x, bottom row on the pavement (the hit box stays 70 x 28, wheel to wheel). The road's cyclists: top row at y 190 (below Pepper's feet; the frame crops the wheels, as now) | `road_cyclist1-2.png` (both uses) |
| `art/scene/cyclist_adult1_pedal.png`, `cyclist_adult2_pedal.png` | frames of the still's size side by side (8 frames: 608 x 76) | right | One frame per 6 px ridden, looped. Optional: without it the still is drawn (the old `_roll` wheel frames are not used with the new riders) | `road_cyclist1-2_roll.png` |

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
