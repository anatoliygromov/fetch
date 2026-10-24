# Level 4: Rooftops (beat sheet, as built)

Early afternoon over the roofs, sun on copper and tin. The first level that only goes up, then one long run down.
Greybox, level 4: `love riverwalk --level rooftops`, fourth in `levels.lua`. Built in r6/levels, the drying yard
added in r7/curve, the climb to the nest and the long roof down added in r9/rooftops.

- **Files:** the map `maps/rooftops.tmx` (edit it in Tiled; its export `riverwalk/level/tiled/rooftops.lua`), the
  loader `riverwalk/level/rooftops.lua`, the generator of this version `tools/make_rooftops.py` (it will not
  overwrite the map without `--force`; its r7 and r9 blocks at the end build the newer screens), the mechanics
  `riverwalk/roofs.lua`, the checks and the autopilot `riverwalk/tests_rooftops.lua`. The first paper map
  (`maps/rooftops_sketch.tmx`) is kept for reference only.
- **Renders:** `/home/claude/out/r9-rooftops/rooftops_routes_after.png` (the map with both roads, lamps, secrets,
  the golden bone, puffs, loose tiles, the landmark; `python3 tools/draw_routes.py rooftops <out.png>`). The
  render before r9 is `rooftops_routes_before.png` in the same folder (its road lines there are the pre-r7 ones).
- **Size:** 7472 x 1200 px (934 x 150 cells, 23.4 x 5 screens). From the street (feet y 1144, bottom left) to the
  nest chimney's top (y 88): 1056 px of climbing. Then 384 px down the long roof to the roof cafe (472).
- **Story:** Mia and Pepper sit at the street cafe. A gull lands on the table, snatches the ball and flies up to its
  nest on the tallest chimney, high over the roof cafe at the top of the block. Mia: "MEET ME AT THE ROOF CAFE!"
  She goes up the building's own stairs (dogs are not allowed inside); Pepper goes over the roofs. The nest is three
  roofs above the roof bar's terrace; the roof cafe is at the bottom of the long roof on its far side, where Mia
  waits at the table (7312, 472). Pepper barks the gull off its nest, takes the ball, runs down the long roof and
  gives it to Mia: a real fetch ends the level.
- **Manner:** climbing. The idea: **steam puffs lift Pepper**; loose tiles are the pressure. The reward at the top
  (Castle of Illusion's tower): a fast run down four pitched roofs with the ball in her mouth.
- **Dog logic:** no ladders, ropes or walls. Up by the stairwell, pitched roofs, steam puffs (each one has someone
  making it: a baker, a dryer, a dishwasher, a cook, a caretaker, someone in the shower, a sauna guest), springy
  awnings and hops. Every wall between the tiers is 96 px: too tall to jump (58 px with a scramble, checked), so
  the puffs are the way up.

## The tiers (feet y, world px; y grows downwards)

| Tier | y | x | What is there |
| --- | --- | --- | --- |
| Street | 1144 | 0-576 | the street cafe and its table (hop on or crawl under), stairwell A (576-768) |
| T1, the bakery | 952 | 768-1280 | pitched roof R1, the kitchen fan by the wall |
| T1b | 856 | 1280-2048 | the light well (1568-1664, 96 deep) with three loose tiles and a fan in it, pitched roof R2, the laundry vent |
| T2, market hall and laundry | 760 | 2048-3328 | glass roof R3, the sweep's chimney block (top 664), the skylight dip (2528-2624) with three loose tiles and a fan, the roof garden's goose, the garden vent, the balcony (664) with three loose tiles and its vent |
| T3, the drying yard and the roof bar | 568 | 3328-3872 | the drying yard (r7: two loose tiles up to a chimney stack, 472, over a dip 40 deep), the gull, the springy awning (552, bounce 120), the water tank (448) and its vent |
| T4, the roof bar terrace and the hotel roof | 376 | 3872-4800 | the terrace fan up to the copper roof (280, 3776-4032, one-way), then the hotel roof: two skylights (40 deep, three loose tiles each) under the second gull, the hotel's goose, the hotel kitchen's vent over its chimney block (top 280) |
| The light court | 664 | 4800-5200 | its floor, three balconies (568, 472, 376) on four puffs, the balcony's post (40 px) |
| T5, the tall block and the cafe awning's roof | 280 | 5200-5696 | a lamp, the tall block's goose, the scaffold (5424-5568: two loose boards over a gap 40 deep), the cafe awning (264, bounce 120) |
| T6, the stacks and the sauna roof | 184 | 5696-6432 | the chimney stacks (two loose tiles, 152 and 120, up to the stack, 88, over a dip 40 deep), a lamp, the third gull, a skylight (three loose tiles), the sauna (bark) |
| Nest | 88 | 6400-6432 | the gull's nest with the ball on the tallest chimney |
| The long roof | 88 to 472 | 6432-7136 | four pitched roofs falling to the right with flat runs (184, 280, 376) between |
| The roof cafe | 472 | 7136-7472 | Mia at the table, the stairs she came up |

## The idea, in five beats

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | T1 and T1b (screens 3 to 6) | The kitchen fan stands against a wall too tall to jump. It rattles (0.8 s, the cap turns orange and hops, "!"), then puffs: Pepper rides up 108 px onto T1b. A miss leaves her on the flat roof. Then the light well: three loose tiles over a 96 px well, "LOOSE TILES! RUN!". Running, she crosses; walking, she drops into the well (no harm, a bone down there) and its courtyard fan lifts her out. |
| 2 Practise | T2, the market hall and the balcony (screens 7 to 10) | The laundry vent up to T2. The sweep's vent lifts her over a block of chimneys; the skylight is the light well again (tiles, a fan in the dip). The garden vent lifts her onto the balcony: three loose tiles between two ledges, then the balcony vent up to T3. Falls land on T2. |
| 3 Combine with earlier mechanics | the roof garden, the drying yard and the roof bar (screens 9 to 12) | The roof garden's goose (City Park: bark it off or hop it) before the garden vent. The drying yard: held jumps up two loose tiles. On the roof bar the gull circles (River Walk: duck, or bark while it squawks) over the springy awning (Downtown: a tap hop onto it bounces her 120 px onto the water tank) and the tank's vent, which lifts her onto the roof bar's terrace. |
| 4 The climb to the nest (r9) | the hotel roof to the sauna roof (screens 13 to 21) | Everything at once, higher and higher: skylights under a gull, a goose by a vent, the light court (the level's tower: a drop to its floor, then four puffs up three balconies, one of them two loose tiles by the hood), the tall block's goose, the scaffold's loose boards (tap hops), the cafe awning's bounce, the chimney stacks (held jumps up loose tiles), a skylight under the third gull. |
| 5 Twist, the fetch and the reward | the sauna, the nest and the long roof (screens 21 to 24) | The sauna never puffs by itself: one bark makes the gull drop the ball on its chimney and the guest throw water on the stones; the puff carries her onto the nest chimney. The ball, then the long roof: four pitched roofs and three flat runs down to the roof cafe, bones all the way, nothing to fear: GIVE, GOOD GIRL! |

## The new screens (r9), left to right

| Screen | x | Feet y | What is there, and why |
| --- | --- | --- | --- |
| The hotel roof | 4048-4800 | 376 | The roof bar's terrace runs on into the hotel roof. Skylight A (4224-4320) and B (4384-4480): 40 deep, three loose tiles each, run across (a drop: scramble out). The second gull circles from 4160 to 5568. The hotel's goose paces 4496-4600, past the hotel kitchen's vent (4572-4592): bark it off before waiting on the hood. The vent lifts her over the hotel's chimney block (4608-4672, top 280), as the sweep's does; she walks off it and on to the roof's end. |
| The light court | 4800-5200 | 664 to 280 | The tower. She drops 288 px to the court's floor (the hotel lobby's glass roof) and rides four puffs up: the court fan (the caretaker's boiler) onto balcony 568 (4920-5000), the laundry hood onto balcony 472 (two loose tiles, 5008-5056, then a ledge with the next hood: hurry), the kitchen hood onto balcony 376 (5096-5200), the bath fan onto the tall block. 5.0 s cycles: the clean run waits on each hood; the gull swoops on the waiting dog (duck: stays put through the puff, so she waits again; or bark). A fall drops one balcony. The balcony's post (4924-4932, 40 px) stops a knocked ball; a held jump gets her over it. |
| The tall block | 5200-5424 | 280 | A lamp (5224), the tall block's goose (5248-5410). |
| The scaffold | 5424-5568 | 280 | Two loose boards (5456, 5512) over a gap 40 deep: tap hops, as the high road's tiles. A board not hopped: she drops into the gap and scrambles out either side. |
| The cafe awning | 5568-5696 | 280 | A tap hop onto the springy awning (5624-5680, 264, bounce 120) bounces her up onto T6. |
| The chimney stacks | 5696-6104 | 184 to 88 | The drying yard again, higher: a dip 40 deep (5856-6000), loose tiles at 152 and 120, the stack (6000-6104, top 88): three held jumps, no stopping. A miss: into the dip, scramble out left. Off the stack she drops onto the sauna roof. |
| The sauna roof | 6104-6400 | 184 | A lamp (6120), the third gull (5700-6320, over the stacks too), a skylight (6176-6272, three loose tiles), the sauna (6356-6376, bark only). |
| The nest | 6400-6432 | 88 | The tallest chimney, the gull's nest, the ball. |
| The long roof | 6432-7136 | 88 to 472 | The reward: four 45 degree roofs (96 px each) with flat runs of 128, 96 and 96 px between, bones in arcs. Nothing hurts here. |
| The roof cafe | 7136-7472 | 472 | Mia at the table (7312), the railing, the stairs up. GIVE. |

## The two roads

**The low road (main route):** street, table, stairwell A, R1, the kitchen fan, the light well's tiles, R2, the
laundry vent, R3, the sweep's vent, the skylight's tiles, the goose, the garden vent, the balcony's tiles, the
balcony vent, the drying yard, the gull, the awning, the tank vent, then the climb to the nest (beat 4) and the
finale. 15 puffs on the way (the terrace fan up to the copper roof is a side trip), 26 loose tiles, 3 geese,
3 gulls (and the one on the nest).

**The high road (golden bone):** from T1b the attic fan (108) to the attic ledge (760), two loose tiles (tap hops),
ledges 760, 728, 696 (held jumps, gaps 32, +32 each), the loft vent to the pigeon loft (600, lamp), ledges 568
and 536 over the market hall, two loose tiles, down to 600, two more loose tiles, the chimney pot (552, a held jump
and a scramble: **the golden bone**), the bakery chimney's puff (156) to the roof walkway (456, lamp, secret ROOF
WALKWAY), four loose tiles, a held jump up to ledge 424 over the drying yard, the bar fan (156) onto the copper
roof. It skips the goose, the drying yard, the gull, the awning and the terrace fan. **r9:** off the copper roof's
right end it drops onto the roof bar's terrace (376) and takes the climb to the nest with the low road: both roads
share beats 4 and 5.

**Dropping off a ledge lands on a lower roof:** every high ledge is over a roof, a pitched roof, the light well or
the skylight dip (both have a fan out); every balcony of the light court is over a lower balcony or the court's
floor. The checks prove it for every ledge, off each end and with Down + A through it (a balcony end against a
wall, and a spot on a vent hood, are skipped): 46 falls, no heart lost, none out of the map. And every loose tile
(36) drops her onto a floor below with no heart lost.

## Every jump, with Pepper's numbers

Tap hop 24 px, held jump 46 px, scramble to 58 px, a gap she falls into at least 64 px. Each is simulated by
`--physics` with Pepper's own controller from where a player stands.

| Jump | Gap | Up | Needs | Lands |
| --- | --- | --- | --- | --- |
| street -> cafe table | 0 | +24 | running jump (or crawl under) | 1120 |
| a wall between tiers | 0 | +96 | not possible without a puff (checked) | stays below |
| light well, skylights, balcony tiles (and r9: the hotel's and the sauna roof's skylights) | 8 | 0 | run straight across | 856, 760, 664, 376, 184 |
| sweep's chimney block -> market roof | 0 | -96 | walk off | 760 |
| drying yard: T3 -> tile -> tile -> stack (r7) | 32 | +32 each | held (a tap: into the dip) | 536, 504, 472 |
| the stack -> run off: the awning bounces her onto the tank (r7) | 0 | -24, then +120 | run | 448 |
| roof bar -> awning | 0 | +16 | tap hop; the bounce, holding right | the tank, 448 |
| high: ledge -> 2 tiles -> ledge (x 3) | 32 | 0 | tap hops (the walkway: held jumps, up to 424) | 760, 536, 600, 424 |
| high: 760 -> 728 -> 696 | 32 | +32, +32 | held | 728, 696 |
| high: 600 -> 568 -> 536 | 32 | +32, +32 | held | 568, 536 |
| high: 536 -> 600 | 32 | -64 | held | 600 |
| high: ledge 600 -> chimney pot | 0 | +48 | held and scramble | 552 (golden bone) |
| copper roof -> terrace | 0 | -96 | Down + A | 376 |
| (r9) the hotel's chimney block -> the hotel roof | 0 | -96 | walk off | 376 |
| (r9) the hotel roof -> the light court | 0 | -288 | walk off | 664 (or the court fan's hood) |
| (r9) court floor -> the balcony's post -> the floor | 0 | +40, -40 | held; walk off | 624, 664 |
| (r9) the scaffold: edge -> board -> board -> far side | 32 | 0 | tap hops | 280 |
| (r9) a board not hopped; out of the gap, either side | 0 | -40, +40 | walk; held and scramble | 320, 280 |
| (r9) the cafe awning's roof -> awning -> T6 | 0 | +16, then +120 | tap hop, holding right | 184 |
| (r9) the stacks: T6 -> tile -> tile -> stack | 32 | +32 each | held (a tap: into the dip; out: held and scramble, left) | 152, 120, 88 |
| (r9) the stack -> run off onto the sauna roof | 0 | -96 | run | 184 |
| (r9) nest chimney -> the sauna's hood | 0 | -92 | walk off | 180 |
| (r9) nest chimney -> the long roof, all the way down | 0 | -384 | run | 472 |

## The puffs

Each puff's apex is 16 px over the floor it serves, so she steers onto it; with no input she drops back on the hood
(or onto the loose tile over it). Each mouth is at least 17 px clear of any solid above it. In the light court the
next balcony's hood can be where she lands: standing on it is as good as the balcony (checked).

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
| TERRACE FAN (the roof bar) | T4 376 | 108 | copper roof 280 | 4.0 s |
| HOTEL KITCHEN (the cook), r9 | T4 376 | 108 | the hotel's chimney block 280 | 4.0 s |
| COURT FAN (the caretaker's boiler), r9 | court 664 | 108 | balcony 568 | 5.0 s |
| LAUNDRY HOOD (the hotel laundry's dryer), r9 | balcony 568 | 108 | balcony 472 | 5.0 s |
| KITCHEN HOOD (someone frying), r9 | balcony 472 | 108 | balcony 376 | 5.0 s |
| BATH FAN (someone in the shower), r9 | balcony 376 | 108 | T5 280 | 5.0 s |
| SAUNA (a bark), r9: moved | T6 184 | 108 | the nest chimney 88 | bark only |
| ATTIC FAN, LOFT VENT, BAKERY CHIMNEY, BAR FAN (high road) | 856, 696, 600, 424 | 108, 108, 156, 156 | 760, 600, 456, 280 | 3.0, 3.0, 3.5, 3.0 s |

**Readable steam (roofs.lua):** the column is cloud blobs with a crisp blue-grey outline, a shaded underside and a
lit top, behind Pepper. Each vent has a cap on a stem: grey at rest; while it warns it turns orange, hops and
rattles, small outlined wisps and dark specks leak out, and a "!" shows; during the puff it stands open.

## Lamps, secrets, the golden bone, the landmark

- **Lamps (9):** low road and the climb: the street (40), T1b after the first puff (1296), T2 after the light well
  (2064), T3 after the balcony's tiles (3336), the roof bar's terrace (3880), the tall block after the light court
  (5224), the sauna roof after the chimney stacks (6120). High road: the pigeon loft (1976, 600) after the first
  tiles and ledges, the roof walkway (2992, 456) after the golden bone. On the autopilot's pace the climb's lamps
  come about 20 s apart (the court's puffs are slow); a child takes two to four times as long.
- **Secrets (2):** GOLDEN BONE (the chimney pot) and ROOF WALKWAY (the high road's walkway).
- **The landmark:** the nest chimney (now at 6400-6432, top 88) with the gull on its nest. While it is above the
  screen, a faded far copy (chimney, nest, the gull circling, the sauna's thread of steam) stands at the top of the
  sky and slides slower than the world, so the goal is in view from every tier.

## Timing (measured)

- `--auto` (the low road and the finale): **GOOD GIRL! in 92.4 s**, no heart lost, 119 of 158 bones.
- `AUTO_ROUTE=high --auto` (the high road): **92.4 s**, both secrets and the golden bone, 101 of 158 bones.
- The two roads end at the same time: the high road reaches the hotel kitchen's vent a little earlier, and both
  ride the same puff; from there the climb is shared. Before r9: 58.1 s and 54.4 s.
- Par: **148 s** (`levels.lua`, the autopilot's time times about 1.6, as the other levels).

## The playtest lab (r9)

`python3 tools/check_curve.py --order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10` (the
game's order since D2, the r7 method), fresh `--out` on the committed tree
(`/home/claude/out/r9-rooftops/curve_final/`): Rooftops DI v2 kids / parents **23.5 / 26.1** (before r9: 20.0 /
16.5), Elsa clears 78%, lost runs 2.5%, worst spot screen 17 (the tall block's goose, 26%). T1 to T4 pass. With
20 seeds (`curve_final20/`) Rooftops is 21.2 / 22.1, Elsa 84%, lost 1.2%; T4 fails there on City Park (tall), level
2, 9.4% lost, which is played before Rooftops and does not depend on it.

What moved DI: the chimney stacks' loose tiles (held jumps under time pressure; most of the new failures, and two
of Anna's quits in the 10-seed run) and the tall block's goose. The court's puffs cost almost no failures (every
persona rides puffs well), and a longer clean run makes the time term smaller. The stacks are seed-sensitive: a
small change earlier in the level (the balcony's post) moved the 10-seed read from 20.8 / 21.3 to 23.5 / 26.1.
Lessons on the way: a landing pad too short after the awning's bounce threw the bot into the stacks' dip (fixed:
the pad is 160 px); a 96 px pit under the scaffold with a vent out trapped the lab's bot, as r7's well did, so the
scaffold's gap is 40 deep; a ball knocked off the hotel roof's edge flew 161 px into the court (`--qa`), so the
first balcony has a post that stops it.

## Open questions for the owner

- DI sits at the low end of the 22 to 28 asked (21 to 23.5 for kids, depending on the seeds). If it should be
  firmer, the fair lever is one more held jump in a row (the scaffold's boards as held jumps), not more puffs. If
  the chimney stacks feel too hard for Anna, a solid first step there (a chimney pot) took most of their bite off.
- The light court's 5.0 s cycles make the clean run wait. A player who barks at a resting vent starts it at once
  (roofs.lua); a speedrunner can skip most of the wait. Fine, or teach it?
- Should the long roof feel faster (a real slide)? Pepper's movement is frozen, so today it is her gallop downhill.
