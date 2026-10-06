# Level 1: City Park (beat sheet)

The first level. Autumn park: trees, paths, benches, a pond, leaves. Gentle: every move is taught once, in order, with clear ground between the set pieces.

- **Size:** 6 screens, 1920 px (240 x 30 cells of 8 px). Walking line (feet) y 184, like River Walk.
- **Time limit:** 300 s.
- **Story:** a magpie has stolen the girl's ball. It sits on a perch and flies on when Pepper comes near. Pepper sneaks up (walks), barks, the magpie drops the ball, and she carries it to the girl waiting by the swings. GOOD GIRL!
- **Moves taught, in order:** run, tap hop, held jump, crawl, hop over water, ride a moving platform, ledge scramble, dodge a hazard, bark, pick up, give.

## Screens

| # | Screen | Pepper learns / does | Set pieces | Hazards | Bones | Checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The gate (0-320) | Run. Tap A for a hop onto the log. Leaf piles hide bones. | Park gate, leaf pile (bones inside), LOG 40x16 (top y 168) | none | 7 | lamp x 296 |
| 2 | Benches and hedge (320-640) | Hold A to jump higher (bench seat, 28 px up), or crawl under it. Down: crawl through the hedge gap (19 px). Harder route: run and jump from the seat onto the hedge top for a gold bone. | BENCH (seat y 156-165), HEDGE (y 112-165, 64 wide), front-layer trunk | none | 8 (1 gold) | lamp x 656 |
| 3 | The pond (640-960) | Step down onto the first stepping stone, hop to the second (40 px gap), wait for the duck boat and ride it, jump up the far bank (18 px). | Pond (water from y 208, x 704-944), 2 STONES (top y 188), DUCK BOAT (moving, deck y 202) | water: a heart | 7 | lamp x 976 |
| 4 | Leaf cart (960-1280) | Hold A and push to climb the bin (56 px: jump + scramble). Leaf cart zone: get up on the picnic table, or run and jump over the cart. | BIN (top y 128), PICNIC TABLE (top y 156) | the park keeper's LEAF CART (48x26, like River Walk's bikes) | 7 | lamp x 1304 |
| 5 | The big oak (1280-1600) | If the magpie still has the ball it may sit on the low left branch: bark from the path, the ball lands on the branch, climb up for it. Optional: climb the branches (one-way, held jumps) for a gold bone, Down + A drops back through. | OAK trunk and crown, 4 BRANCHES (y 156, 128, 100, low left branch 104), MAGPIE | none | 6 (1 gold) | none |
| 6 | Playground (1600-1920) | Jump up the slide tower (32 px: held jump), run down the slide (slope), hop up the climbing frame, X: give the ball to the girl. | SLIDE (tower top y 152, 45 degree slide, x 1696-1728), CLIMBING FRAME (one-way bars y 160, 136), SWINGS, the girl | none | 5 | lamp x 1616 |

Total: 40 bones, 2 of them gold super bones (hedge top, oak top branch).

Every screen keeps about 100 px of open path. One or two characters per screen at most: the magpie (anywhere along the path), the girl on screen 6, the cart on screen 4.

## The magpie and the ball

1. **Perched:** the magpie (14x10, drawn in code) holds the ball in its beak on a perch: the path past the log, the bench's backrest, the lamp by the hedge, the bin, the oak's low branch, the slide tower's rail, the climbing frame (its last perch). It always faces Pepper.
2. **Wary:** it flies on to the next perch when Pepper comes within 110 px running, or within 40 px walking (hold B). The first time: "TOO FAST! SNEAK UP: HOLD B TO WALK". On its last perch it stays.
3. **Bark:** a bark within 95 px startles it: it drops the ball and flies away for good ("IT DROPPED THE BALL! X: PICK IT UP"). A bark from further off only gets a "?".
4. **The ball falls** with gravity onto whatever is under the perch: the path, the bench seat, the bin top, the oak branch, the slide tower, the frame's top bar. In the pond it comes back by the last lamp.
5. **Fetch:** X picks it up, X near the girl by the swings gives it: GOOD GIRL!, FETCH 2000, then the tally.

## Estimated play time

- A straight run: about 37 s (the autopilot: no hearts lost, 36 of 40 bones, waits once for the duck boat and once for the leaf cart, climbs the oak).
- A first play, with a few falls and reading the hints: 2 to 3 minutes.

## Art needed later (sizes in game px)

Obstacles (Pepper uses them: outlined, mid-tone, never faded)

| Asset | Size | Notes |
| --- | --- | --- |
| Log | 40x16 | lies on the path, a hop up |
| Park bench | about 110x50, seat 96 wide at y 156-165 | crawl gap 19 px under the seat. Could reuse River Walk's bench |
| Hedge with an arch | 64x72 (gap 19 px under it) | autumn colours, the arch must read as a crawl gap |
| Stepping stone | 24x20 above the water (x2) | tops 4 px below the path |
| Duck boat | about 52x20, deck 48 wide | moving platform; a pedal boat shaped like a duck |
| Litter bin | 35x56 | could reuse River Walk's bin |
| Picnic table | 72x28 | solid block, top y 156 |
| Leaf cart (hazard) | 48x26, with the park keeper about 20x40 | drives right to left, like the bikes |
| Oak branches | 64x6, 56x6, 64x6, 48x6 | one-way, part of the oak art |
| Slide | tower 32x32 plus a 32x32 slide | terrain shape is fixed by the map |
| Climbing frame | about 64x56, bars at y 160 and 136 | one-way bars |

Decoration (faded towards the haze, no outline)

| Asset | Size | Notes |
| --- | --- | --- |
| Park gate | 24x64 pillar | at the level's left edge |
| Lamp post | 14x101 | reuse River Walk's lamp (lit = checkpoint) |
| Big oak | trunk 24x132, crown about 200x60 | autumn crown; the branches above are obstacles |
| Leaf pile | 44x12 (x2) | drawn over the bones; it flattens when Pepper runs through |
| Pond water | 240x32 | animated ripples, like the river |
| Path and grass | 320 px loop, about 56 tall | autumn path with leaves |
| Swings and sandpit | about 80x60 | behind the girl |
| Front-layer trunks | 12x180 (x2) | foreground frame, scrolls 1.3x |
| Far city | 320 px wide strip | parallax 0.08 |
| Far trees, near bushes | 320 px wide strips | parallax 0.25 and 0.5, autumn colours |

Characters

| Asset | Size | Notes |
| --- | --- | --- |
| Magpie | 16x12 cell | perch (tail flick), fly (2-frame flap), with and without the ball |
| Girl, ball | existing | real art already |

## Running it

| Command | Does |
| --- | --- |
| `love riverwalk --level citypark` | plays City Park (River Walk stays the default without the flag) |
| `./build_citypark.sh` | builds `CITYPARK_greybox.love`, where City Park is the default (a `default_level.txt` inside the zip) |
| `... --level citypark --physics` | 40 checks: every set piece (heights, gaps, the pond, the cart, the oak, the magpie and the ball, the slide, the girl) |
| `... --level citypark --auto` | the autopilot plays to GOOD GIRL! and saves every 3rd frame to `rec/` |
| `... --level citypark --test` | screenshots: the card, the 6 screens, the magpie (sneak, bark, drop, fly away, on the oak), two debug views, giving the ball, the tally |
| `... --level citypark --qa` | the collision QA sweep (0 problems) |

The greybox look is chosen by the level (`scenery = "greybox"` in `level/citypark.lua`): sky and clouds as in River Walk, then flat misty boxes per parallax layer (far city 0.08, far trees 0.25, near trees 0.5), flat grey ground with a 1 px edge, the pond as a flat box, outlined labelled boxes for everything Pepper uses, flat boxes for decoration. Pepper, the girl and the ball are the real art.
