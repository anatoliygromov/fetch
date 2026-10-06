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
| 3 | The pond (640-960) | Step down onto the first stepping stone, hop to the second (32 px gaps), step onto the duck boat (it is already there, waiting) and ride it, jump up the far bank (18 px). **High route (a secret):** from the hedge top, running held jumps over the three willows' branches, then drop onto the far bank. | Pond (water from y 208, x 704-944), 2 STONES (top y 188), DUCK BOAT (rope ferry, deck y 202), WINCH, 3 WILLOWS (one-way branches y 120, 112, 120) | water: a heart | 10 (1 gold) | lamp x 976 |
| 4 | Leaf cart (960-1280) | Hold A and push to climb the bin (56 px: jump + scramble). Leaf cart zone: the cart sets off as Pepper walks in (a honk and a sign 1 s before it is on screen). Get up on the picnic table, or run and jump over the cart. | BIN (top y 128), PICNIC TABLE (top y 156) | the park keeper's LEAF CART (48x26, like River Walk's bikes) | 7 | lamp x 1304 |
| 5 | The big oak (1280-1600) | The hollow log: hop onto it (26 px) or crawl through it (19 px); crawling through finds the gold bone hidden inside (a secret). If the magpie still has the ball it sits on the lamp post before the oak: bark from the path, the ball drops to the path. Optional: climb the branches (one-way, held jumps) for a gold bone (a secret), Down + A drops back through. | HOLLOW LOG (shell y 158-165, x 1244-1286), OAK trunk and crown, 4 BRANCHES (y 156, 128, 100, low left branch 104), MAGPIE | none | 7 (2 gold) | none |
| 6 | Playground (1600-1920) | Jump up the slide tower (32 px: held jump), run down the slide (slope), hop up the climbing frame, X: give the ball to the girl. | SLIDE (tower top y 152, 45 degree slide, x 1696-1728), CLIMBING FRAME (one-way bars y 160, 136), SWINGS, the girl | none | 5 | lamp x 1616 |

Total: 44 bones, 4 of them gold super bones (hedge top, the middle willow, inside the hollow log, oak top branch).

## Secrets and the second route

Three secrets, counted on the tally (`stats().secrets` of `secretsTotal`; "SECRET! <NAME> n/3" when found):

| Secret | Where | How |
| --- | --- | --- |
| WILLOWS | the middle willow's branch over the pond (gold bone) | the high route: bench seat, running jump to the hedge top, running held jumps from branch to branch |
| HOLLOW LOG | inside the hollow log (gold bone, hidden: the log's dark inside is drawn over it) | Down: crawl through instead of hopping over |
| OAK TOP | the oak's top branch (gold bone) | held jumps up the branches |

**The second route:** over the pond by the willows instead of the stones and the duck boat. It starts at the hedge top and rejoins the path on the far bank (x 944+).

## No waiting

- **The duck boat** is a rope ferry: the park keeper's winch on the far bank pulls it along its rope. It waits by the far bank; when Pepper comes to the pond (x 600-830) it is winched over to the second stone (1.3 s) and waits there for her. When she stands on it, it takes her across (after a 0.3 s pause), and it stays on the far side.
- **The leaf cart** sets off when Pepper walks into its zone (not on a global timer), then one comes every 6 s while she is in it.

## Hard mode

Chosen in the menu (`carry.hard`; `--hard` for the checks): 1 heart, the leaf cart 25% faster (125 px/s). The autopilot still clears the level without a hit.

Every screen keeps about 100 px of open path. One or two characters per screen at most: the magpie (anywhere along the path), the girl on screen 6, the cart on screen 4.

## The magpie and the ball

1. **Perched:** the magpie (14x10, drawn in code) holds the ball in its beak on a perch: the path past the log, the bench's backrest, the lamp by the hedge, the bin, the lamp post before the oak, the slide tower's rail, the climbing frame (its last perch). It always faces Pepper.
2. **Wary:** it flies on to the next perch when Pepper comes within 110 px running, or within 40 px walking (hold B). On the first perch it is calmer: it flees a running Pepper only at 80 px, inside bark range (95 px). A kid who runs straight at it is stopped by the log 81 px away and can still bark it off. The first time it flies: "TOO FAST! SNEAK UP: HOLD B TO WALK". On its last perch it stays.
3. **Bark:** a bark within 95 px startles it: it drops the ball and flies away for good ("IT DROPPED THE BALL! X: PICK IT UP"). A bark from further off only gets a "?".
4. **The ball falls** with gravity onto whatever is under the perch: the path (perches 1, 3, 5), the bench seat (28 px up), the bin top (56 px, on the main route anyway), the slide tower (32 px), the frame's top bar (48 px, two hops). Every drop is somewhere a small child can get to; the oak's high left branch (80 px up, reached only by a jump across from the top branch) made kids quit, so it is no longer a perch. In the pond the ball comes back by the last lamp.
5. **Fetch:** X picks it up, X near the girl by the swings gives it: GOOD GIRL!, FETCH 2000, then the tally.

## Estimated play time

- A straight run: about 31 s (the autopilot: no hearts lost, 38 of 44 bones, 2 of 3 secrets; the duck boat is waiting at the stone, the leaf cart sets off as it arrives at the picnic table; it crawls through the hollow log and climbs the oak). Hard mode: the same, about 31 s.
- A first play, with a few falls and reading the hints: 2 to 3 minutes.

## Art needed later (sizes in game px)

Obstacles (Pepper uses them: outlined, mid-tone, never faded)

| Asset | Size | Notes |
| --- | --- | --- |
| Log | 40x16 | lies on the path, a hop up |
| Park bench | about 110x50, seat 96 wide at y 156-165 | crawl gap 19 px under the seat. Could reuse River Walk's bench |
| Hedge with an arch | 64x72 (gap 19 px under it) | autumn colours, the arch must read as a crawl gap |
| Stepping stone | 24x20 above the water (x2) | tops 4 px below the path, 32 px apart |
| Duck boat | about 52x20, deck 48 wide | rope ferry; a boat shaped like a duck, on a rope across the pond |
| Willow branches | 56x5 (x3) | one-way, hanging over the pond |
| Hollow log | 42x26 | bark shell on top (solid, 7 px), dark inside 19 px high, cut rings at the ends |
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
| Willows (x3) | trunks 8x54, crowns 72x24 | behind the pond (base y 174); their branches are obstacles |
| Winch | 20x14 | the park keeper's rope winch on the far bank |
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
| `... --level citypark --physics` | 64 checks: every set piece (heights, gaps, the pond, the boat coming to Pepper, the cart, the oak, the magpie and the ball on every perch, the slide, the girl), the willows route, every secret, the cart's start and warning, hard mode |
| `... --level citypark --auto` | the autopilot plays to GOOD GIRL! and saves every 3rd frame to `rec/` |
| `... --level citypark --test` | screenshots: the card, the 6 screens, the magpie (sneak, bark, drop, fly away, on the lamp before the oak), two debug views, running at the magpie, the boat waiting, the willows, the hollow log, the cart's warning sign, giving the ball, the tally |
| `... --level citypark --auto --hard` | the autopilot in hard mode |
| `... --level citypark --qa` | the collision QA sweep (0 problems) |

The greybox look is chosen by the level (`scenery = "greybox"` in `level/citypark.lua`): sky and clouds as in River Walk, then flat misty boxes per parallax layer (far city 0.08, far trees 0.25, near trees 0.5), flat grey ground with a 1 px edge, the pond as a flat box, outlined labelled boxes for everything Pepper uses, flat boxes for decoration. Pepper, the girl and the ball are the real art.
