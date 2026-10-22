# Level 4: Rooftops (beat sheet, as built)

Early afternoon over the roofs, sun on copper and tin. The first level that only goes up. Greybox, level 4 (r6/levels):
`love riverwalk --level rooftops`, fourth in `levels.lua`.

- **Files:** the map `maps/rooftops.tmx` (edit it in Tiled; its export `riverwalk/level/tiled/rooftops.lua`), the
  loader `riverwalk/level/rooftops.lua`, the generator of this version `tools/make_rooftops.py` (it will not
  overwrite the map without `--force`), the mechanics `riverwalk/roofs.lua`, the checks `riverwalk/tests_rooftops.lua`.
  The first paper map (`maps/rooftops_sketch.tmx`) is kept for reference only.
- **Renders:** `/home/claude/out/r3-rooftops/rooftops_routes.png` (the map with both roads, lamps, secrets, the
  golden bone, puffs, loose tiles, the landmark; `python3 tools/draw_routes.py rooftops <out.png>`).
- **Size:** 12 x 5 screens, 3840 x 1200 px (480 x 150 cells). From the street (feet y 1144, bottom left) to the
  nest chimney's top (y 184, top right): 960 px of climbing, 4 screens.
- **Story:** Mia and Pepper sit at the street cafe. A gull lands on the table, snatches the ball and flies up to its
  nest on the tallest chimney, over the roof cafe at the top of the block. Mia: "MEET ME AT THE ROOF CAFE!" She goes
  up the building's own stairs (dogs are not allowed inside); Pepper goes over the roofs. Mia waits at the roof
  cafe's table on the terrace (3000, 376), right under the nest chimney. Pepper barks the gull off its nest, takes
  the ball and brings it down to her: a real fetch ends the level.
- **Manner:** climbing. The idea: **steam puffs lift Pepper**; loose tiles are the pressure.
- **Dog logic:** no ladders, ropes or walls. Up by the stairwell, pitched roofs, steam puffs (each one has someone
  making it: a baker, a dryer, a dishwasher, a sauna guest), a springy awning and hops. Every wall between the
  tiers is 96 px: too tall to jump (58 px with a scramble, checked), so the puffs are the way up.

## The tiers (feet y, world px; y grows downwards)

| Tier | y | x | What is there |
| --- | --- | --- | --- |
| Street | 1144 | 0-576 | the street cafe and its table (hop on or crawl under), stairwell A (576-768) |
| T1, the bakery | 952 | 768-1280 | pitched roof R1, the kitchen fan by the wall |
| T1b | 856 | 1280-2048 | the light well (1568-1664, 96 deep) with three loose tiles and a fan in it, pitched roof R2, the laundry vent |
| T2, market hall and laundry | 760 | 2048-3328 | glass roof R3, the sweep's chimney block (top 664), the skylight dip (2528-2624) with three loose tiles and a fan, the roof garden's goose, the garden vent, the balcony (664) with three loose tiles and its vent |
| T3, the roof bar | 568 | 3328-3552 | the gull, the springy awning (552, bounce 120), the water tank (448) and its vent |
| T4, the roof terrace | 376 | 3552-3840 | Mia's roof cafe, the terrace fan, the nest chimney (3728-3760) |
| Copper roof | 280 | 3456-3712 (one-way) | the sauna (bark), the finale's lamp-free last climb |
| Nest | 184 | 3728-3760 | the gull's nest with the ball |

## The idea, in four beats

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | T1 and T1b (screens 3 to 6) | The kitchen fan stands against a wall too tall to jump. It rattles (0.8 s, the cap turns orange and hops, "!"), then puffs: Pepper rides up 108 px onto T1b. A miss leaves her on the flat roof. Then the light well: three loose tiles over a 96 px well, "LOOSE TILES! RUN!". Running, she crosses; walking, she drops into the well (no harm, a bone down there) and its courtyard fan lifts her out. |
| 2 Practise | T2, the market hall and the balcony (screens 7 to 10) | The laundry vent up to T2. The sweep's vent lifts her over a block of chimneys; the skylight is the light well again (tiles, a fan in the dip). The garden vent lifts her onto the balcony: three loose tiles between two ledges, then the balcony vent up to T3. Falls land on T2. |
| 3 Combine with earlier mechanics | the roof garden and the roof bar (screens 9 to 11) | The roof garden's goose (City Park: bark it off or hop it) before the garden vent. On the roof bar the gull circles (River Walk: duck, or bark while it squawks) over the springy awning (Downtown: a tap hop onto it bounces her 120 px onto the water tank) and the tank's vent, which lifts her onto the roof terrace. |
| 4 Twist, then the fetch | the roof terrace and the nest (screen 12) | The terrace fan lifts her up through the one-way copper roof. The sauna never puffs by itself: one bark makes the gull drop the ball on its chimney and the guest throw water on the stones; the puff carries her onto the nest chimney. The ball, a step off onto the sauna's hood, Down + A onto the terrace, and GIVE: GOOD GIRL! |

## The two roads

**The low road (main route):** street, table, stairwell A, R1, the kitchen fan, the light well's tiles, R2, the
laundry vent, R3, the sweep's vent, the skylight's tiles, the goose, the garden vent, the balcony's tiles, the
balcony vent, the gull, the awning, the tank vent, the finale. 10 puffs, 6 loose tiles, 1 goose, 1 gull.

**The high road (golden bone):** from T1b the attic fan (108) to the attic ledge (760), two loose tiles (tap hops),
ledges 760, 728, 696 (held jumps, gaps 32, +32 each), the loft vent to the pigeon loft (600, lamp), ledges 568
and 536 over the market hall, two loose tiles, down to 600, two more loose tiles, the chimney pot (552, a held jump
and a scramble: **the golden bone**), the bakery chimney's puff (156) to the roof walkway (456, lamp, secret ROOF
WALKWAY), two loose tiles, a held jump up to ledge 424 over the roof bar, the bar fan (156) onto the copper roof.
It skips the goose, the gull, the awning and the terrace fan; it has 8 loose tiles, 5 puffs and more bones for the
distance.

**Dropping off the high road lands on the low road:** every ledge is over a roof, a pitched roof, the light well or
the skylight dip (both have a fan out). The checks prove it for every high ledge, off each end and with Down + A
through it: 27 falls, no heart lost, none out of the map.

## Every jump, with Pepper's numbers

Tap hop 24 px, held jump 46 px, scramble to 58 px, a gap she falls into at least 64 px. Each is simulated by
`--physics` with Pepper's own controller from where a player stands.

| Jump | Gap | Up | Needs | Lands |
| --- | --- | --- | --- | --- |
| street -> cafe table | 0 | +24 | running jump (or crawl under) | 1120 |
| a wall between tiers | 0 | +96 | not possible without a puff (checked) | stays below |
| light well, skylight, balcony tiles | 8 | 0 | run straight across | 856, 760, 664 |
| sweep's chimney block -> market roof | 0 | -96 | walk off | 760 |
| roof bar -> awning | 0 | +16 | tap hop; the bounce, holding right | the tank, 448 |
| high: ledge -> 2 tiles -> ledge (x 3) | 32 | 0 | tap hops (the walkway: held jumps, up to 424) | 760, 536, 600, 424 |
| high: 760 -> 728 -> 696 | 32 | +32, +32 | held | 728, 696 |
| high: 600 -> 568 -> 536 | 32 | +32, +32 | held | 568, 536 |
| high: 536 -> 600 | 32 | -64 | held | 600 |
| high: ledge 600 -> chimney pot | 0 | +48 | held and scramble | 552 (golden bone) |
| nest chimney -> sauna hood | 0 | -92 | walk off | 276 |
| copper roof -> terrace | 0 | -96 | Down + A | 376 |

## The puffs

Each puff's apex is 16 px over the floor it serves, so she steers onto it; with no input she drops back on the hood
(or onto the loose tile over it). Each mouth is at least 17 px clear of any solid above it.

| Vent (who) | On | Lift | Serves | Cycle |
| --- | --- | --- | --- | --- |
| KITCHEN FAN (the baker) | T1 952 | 108 | T1b 856 | 3.0 s |
| COURTYARD FAN (boiler room) | well 952 | 108 | T1b 856 | 3.0 s |
| LAUNDRY VENT (the dryer) | T1b 856 | 108 | T2 760 | 4.0 s |
| SWEEP VENT (market heating) | T2 760 | 108 | chimney block 664 | 4.0 s |
| SKYLIGHT FAN (market fan) | dip 856 | 108 | T2 760 | 3.0 s |
| GARDEN VENT (bathroom fans) | T2 760 | 108 | balcony 664 | 4.0 s |
| BALCONY VENT (kitchen hood) | balcony 664 | 108 | T3 568 | 4.0 s |
| TANK VENT (the dishwasher) | tank 448 | 84 | T4 376 | 4.0 s |
| TERRACE FAN (the roof cafe) | T4 376 | 108 | copper roof 280 | 4.0 s |
| SAUNA (a bark) | copper 280 | 108 | nest 184 | bark only |
| ATTIC FAN, LOFT VENT, BAKERY CHIMNEY, BAR FAN (high road) | 856, 696, 600, 424 | 108, 108, 156, 156 | 760, 600, 456, 280 | 3.0, 3.0, 3.5, 3.0 s |

**Readable steam (roofs.lua):** the column is cloud blobs with a crisp blue-grey outline, a shaded underside and a
lit top, behind Pepper. Each vent has a cap on a stem: grey at rest; while it warns it turns orange, hops and
rattles, small outlined wisps and dark specks leak out, and a "!" shows; during the puff it stands open.

## Lamps, secrets, the golden bone, the landmark

- **Lamps (7):** low road: the street (40), T1b after the first puff (1296), T2 after the light well (2064), T3 after
  the balcony's tiles (3336), the roof terrace before the finale (3560). High road: the pigeon loft (1976, 600) after
  the first tiles and ledges, the roof walkway (2992, 456) after the golden bone. On the autopilot's pace the low
  road's lamps come about 10 to 15 s apart: every pressure section (the well, the market hall and balcony, the gull)
  ends at one.
- **Secrets (2):** GOLDEN BONE (the chimney pot) and ROOF WALKWAY (the high road's walkway).
- **The landmark:** the nest chimney (192 px over the terrace) with the gull on its nest. While it is above the
  screen, a faded far copy (chimney, nest, the gull circling, the sauna's thread of steam) stands at the top of the
  sky and slides slower than the world, so the goal is in view from every tier.

## Timing (measured)

- `--auto` (the low road and the finale): **GOOD GIRL! in 54.1 s**, no heart lost, 51 of 76 bones.
- `AUTO_ROUTE=high --auto` (the high road): **51.8 s**, both secrets and the golden bone.
- The autopilot never waits longer than a puff makes it; a child takes two to four times as long. The low road is
  about 6 s under the Morning chapter's 60 to 90 s for perfect play. To close it: one more screen on T2 (a second
  roof garden with a goose and a puff chain), or a second gull over the market hall.
- Suggested par: 100 s.

## Open questions for the owner

- 54 s of perfect play: add the extra screen (above) or accept it as the chapter's shortest climb?
- The high road is slightly faster than the low road (51.8 against 54.1 s). Lion King's high roads often are; if the
  low road should pay more, move a secret onto it.
- Should the sauna's bark need a hint the first time (today: the "?" over its cap and "BARK!" by the nest)?
