# Downtown canal and basin (boats under the parasols, waterline, quay courses, drains, basin walls, stall counters)

Files: `town_punt.png` 52x14, `town_quaydrain.png` 20x22, `town_basin_wall.png` 10x56, `town_ground.png` 240x68
(quay courses), stall counters in `scene.lua`, canal in `scene.lua`/`water_data.lua`. Branch night/06nov-dt 2852d9c.

# Round 1 (reviewer, 6-7 Nov night)

Looked at: pieces at 5x beside bench, bin and lamp; in game at 4x at x 1600 y 240 (basin), x 2560-3056 y 240
(canal), x 2240 (stall counters).

## Script
quaydrain: "ladder darkest 38" with `--layer back` (it is a dark grate in the quay wall below the street, the
play row; run it as play). punt: "ladder 30, decor-ink 100 %" the same way. basin_wall: WARN decor-ink 47 %.
town_ground: FAIL blotches 4, outline 2 %: the cobble band is a many-shade pebble texture; it was like that before
this branch, not a night change, but it is the one noisy fill on the street.

## Per piece
| Piece | Result | Evidence |
| --- | --- | --- |
| boats under the parasols (town_punt) | FAIL | 52 x 14 px is 1.1 m long, 0.3 m deep: a toy beside Pepper (46 px). It is a flat green trapezoid with a 1 px light gunwale. In game (x 2880 y 240 at 4x) the three hulls are drawn 6-8 px below the water's top edge, inside the blue slab, with no waterline cut, no wet band, no ripple: they float in the water like stickers, the same fault as the River Walk rowboat the owner called terrible. The base review's DT2 "parasols grow out of the flood" is not fixed, it has a boat added to it |
| canal waterline | FAIL | the water is a flat saturated blue slab with light streaks from the top edge to the bottom of the screen; the top edge is a 1 px lighter line, nothing sits in it. Reads as a swimming pool seen through glass |
| quay courses | PASS | flat granite courses in 3 shades under the kerb on both banks, straight joints, the stone block the crates stand on (base DT3 fixed) |
| drains (town_quaydrain) | PASS | arched grate in the quay wall, reads at 1x, one per screen |
| basin walls (town_basin_wall) | FAIL | the two granite posts are crisp and stand on the quay, but the basin itself is still a pit cut into the street: the water starts 30 px under the street and runs to the bottom of the screen, no near wall, no floor, so the fountain stands in a canal, not in a basin. Base review "fountain basin" not fixed by the posts alone |
| stall counters | PASS | green counter with a red striped awning on two posts, outlined, on the kerb (x 2240, x 1600): crisp, reads as a market stall |
| fountain jets | FAIL (minor) | 1 px dashed white lines from the bowl to the water; at 1x a dotted thread |

## Fixes
1. Punt: redraw at true scale from metres: a 4 m punt is 184 px long, 20-24 px of hull above the water, 3-4
   shades, a dark 2 px wet band at the waterline. If a 184 px boat does not fit under three parasols, one punt
   under all three parasols (the parasols are its awnings) or a pontoon deck instead of boats.
2. Waterline: draw the water front-on: a 6-8 px band of surface (two shades, a ripple row) and the hull cut by it;
   under the band the deep water one shade darker, no streaks. Every hull, pole and pier gets a 2 px wet band
   where it meets the surface.
3. Basin: a front-on granite kerb (20-24 px tall, the posts' stone) across the pit at street level, the water a
   6-8 px band just below its top, the deep water hidden. Jets 2 px wide (white over light blue) with a splash
   ring where they land.

# Round 2 (reviewer, 6-7 Nov night): after fix round 1 (fab6b50)

Looked at x 1600 and x 2560-3056, y 240, at 4x; `asset_qa town_basin.png --layer back`: ladder 74 (the kerb's
shadow row; it stands on the play row, run it as play). Nothing else flagged.

| Item | Result | Evidence |
| --- | --- | --- |
| canal waterline | PASS | 8 px surface band with a lit edge and ripple rows, quay reflection, deep water in two darker steps; reads as water front-on |
| parasol poles in the flood | PASS | wet band and ripple ring at the surface, the pole under water one step darker and blue-tinted, an iron foot on the bottom: they stand in the canal |
| punts removed | PASS | agreed: a floor over water that costs a heart is a trap for a child; the poles now explain themselves |
| basin (town_basin) | PASS | far coping, water band, near granite kerb front-on on the quay courses; the column stands in the water |
| jets | PASS | 2 px white over light blue, splash rings where they land |
| river stairs x 3497 | PASS | granite steps down from the kerb, straight treads |

Round 1 FAILs on this family are closed.
