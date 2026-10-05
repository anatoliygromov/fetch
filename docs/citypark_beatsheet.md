# Level 1: City Park (beat sheet)

The first level. Autumn park: trees, paths, benches, a pond, leaves. Gentle: every move is taught once, in order, with clear ground between the set pieces.

- **Size:** 6 screens, 1920 px (240 x 30 cells of 8 px). Walking line (feet) y 184, like River Walk.
- **Time limit:** 300 s.
- **Story:** the girl lost her ball in the park. A cat is sitting on it, up in the big oak. Pepper barks the cat off, the ball drops, she carries it to the girl at the playground. GOOD GIRL!
- **Moves taught, in order:** run, tap hop, held jump, crawl, hop over water, ride a moving platform, ledge scramble, dodge a hazard, bark, pick up, give.

## Screens

| # | Screen | Pepper learns / does | Set pieces | Hazards | Bones | Checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The gate (0-320) | Run. Tap A for a hop onto the log. Leaf piles hide bones. | Park gate, leaf pile (bones inside), LOG 40x16 (top y 168) | none | 7 | lamp x 296 |
| 2 | Benches and hedge (320-640) | Hold A to jump higher (bench seat, 28 px up), or crawl under it. Down: crawl through the hedge gap (19 px). Harder route: run and jump from the seat onto the hedge top for a gold bone. | BENCH (seat y 156-165), HEDGE (y 112-165, 64 wide), front-layer trunk | none | 8 (1 gold) | lamp x 656 |
| 3 | The pond (640-960) | Hop from the bank to the stepping stones, then wait for the duck boat and ride it, hop up the far bank (18 px). | Pond (water from y 208, x 704-944), 2 STONES (top y 192), DUCK BOAT (moving, y 202) | water: a heart | 7 | lamp x 976 |
| 4 | Leaf cart (960-1280) | Hold A and push to climb the bin (56 px: jump + scramble). Leaf cart zone: get up on the picnic table, or run and jump over the cart. | BIN (top y 128), PICNIC TABLE (top y 156) | the park keeper's LEAF CART (48x26, like River Walk's bikes) | 7 | lamp x 1304 |
| 5 | The big oak (1280-1600) | The cat sits on the ball on a high branch. Y: bark near it (within 90 px), the cat runs off, the ball drops. X: pick it up. Optional: climb the branches (one-way) for a gold bone. | OAK trunk and crown, 4 BRANCHES (y 156, 128, 100, cat branch 104), CAT | none | 6 (1 gold) | none |
| 6 | Playground (1600-1920) | Jump up the slide tower (32 px), slide down (slope), hop the climbing frame, X: give the ball to the girl. | SLIDE (tower top y 152, 45 degree slide), CLIMBING FRAME (one-way bars y 160, 136), the girl | none | 5 | lamp x 1616 |

Total: 40 bones, 2 of them gold super bones (hedge top, oak top branch).

Every screen keeps about 100 px of open path. One or two characters per screen at most: the cat on screen 5, the girl on screen 6, the cart on screen 4.

## The cat and the ball

1. **Sit:** the cat (greybox 22x16, label CAT) sits on the ball on the cat branch, 80 px above the path. The ball cannot be picked up. Hint near the oak: "Y: BARK AT THE CAT!".
2. **Bark:** a bark scares the cat when Pepper's middle is within 90 px of the cat's middle. That works from the path right under the branch, or from any branch.
3. **Scared:** the cat jumps up with a "!" (0.35 s), leaps off away from Pepper and runs off screen. The ball is knocked off the branch and drops to the path below the oak.
4. **Gone:** the cat is out of the level. "THE CAT RAN OFF! GET THE BALL".
5. **Fetch:** X picks up the ball ("BRING IT TO THE GIRL!"), X near the girl gives it: GOOD GIRL!, 2000 points, then the tally.
6. If Pepper falls in the pond with the ball, it goes back under the oak.

## Estimated play time

- A straight run: about 70 s (the autopilot, which also takes both gold bones).
- A first play, with a few falls and reading the hints: 2 to 3 minutes.

## Art needed later (sizes in game px)

Obstacles (Pepper uses them: outlined, mid-tone, never faded)

| Asset | Size | Notes |
| --- | --- | --- |
| Log | 40x16 | lies on the path, a hop up |
| Park bench | about 110x50, seat 96 wide at y 156-165 | crawl gap 19 px under the seat. Could reuse River Walk's bench |
| Hedge with an arch | 64x72 (gap 19 px under it) | autumn colours, the arch must read as a crawl gap |
| Stepping stone | 24x16 above the water (x2) | |
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
| Cat | 22x16 cell | sit (on the ball), startle, leap, run |
| Girl, ball | existing | real art already |
