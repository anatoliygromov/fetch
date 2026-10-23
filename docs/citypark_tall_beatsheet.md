# Level 1, tall: City Park with a treetop tier (beat sheet)

City Park as it plays today, moved down 18 rows, with a second road in the treetops above it and a finale that
climbs the play tower into the big oak, with City Park's art: `love riverwalk --level citypark_tall`.

> **r8/levels (23 Oct):** this is the game's City Park now (level 2, D2); the flat City Park is the fallback (levels.lua). Its hints HOLD: UP THE TREE and HOLD: CLIMB THE TOWER are HOLD: CLIMB UP (the panel's three words).


- **Size:** 9 screens x 48 rows: 2880 x 384 px (1.6 screens tall). The path (the low road) is at y 328. On the
  path the camera rests at the bottom of the world (camera y 144), so the low road looks exactly as City Park does
  today, with the treetop tier showing along the top of the screen as a promise.
- **Manner:** sneak and bark (unchanged), now in two storeys.
- **Story:** the magpie has Mia's ball. If Pepper does not get it to drop the ball on the way, it flies to its
  nest at the top of the big oak by the swings. Pepper climbs the play tower into the oak, barks, the ball drops onto
  the nest bough, she picks it up, drops down to Mia: GOOD GIRL!
- **Files:** the map `maps/citypark_tall.tmx` (edit it in Tiled; its export `riverwalk/level/tiled/citypark_tall.lua`),
  the loader `riverwalk/level/citypark_tall.lua`, the first draft's generator `tools/make_citypark_tall.py` (it
  will not overwrite the map without `--force`), the checks `riverwalk/tests_citypark_tall.lua`.
- **Paper maps:** `/home/claude/out/design-round2/citypark_tall_routes.png` (routes drawn on the map).

## The idea, in four beats

The idea of the level is the magpie: **sneak up, then bark**. The tall version teaches it in four beats.

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | screen 1, the gate | The magpie sits on the path past the log. Run at it and it flies ("HOLD: SNEAK"); walk up to the log and bark: it drops the ball on the path. Nothing can hurt Pepper here. |
| 2 Practise | screens 2 to 5 | Perches on the bench's backrest, the lamp by the hedge, the log on the goose lawn, the bin, the lamp before the old oak. Each drop lands where a small child can get it. |
| 3 Combine with an earlier mechanic | screens 3 to 7 | Sneaking meets climbing: three new perches are up in the trees (the treetop walk's rail, the old oak's crown, the alder walk over the creek). A bark only reaches 110 px up, so from the low road the magpie just flies on; from the high road Pepper can sneak along a branch and bark it down. Below, the geese (bark or jump) and the pond and creek (hop) are the low road's pressure. |
| 4 Twist, then the fetch | screen 9, the big oak | The magpie's last perch is its nest at the very top of the big oak, the tallest thing in the park and the landmark seen from the treetops from screen 6 on. Climb the play tower (two decks, 40 px each), four boughs (32 px each), sneak in, bark: the ball lands on the nest bough. Pick it up, Down + A off the bough: Pepper lands by the swings next to Mia. GOOD GIRL! |

A child who barks the ball loose early carries it the rest of the way, as in City Park today, and never needs
the oak. The oak is the catch-all ending, and the treetops are where a skilled player catches the magpie sooner.

## Screen by screen

y is the feet line (world px, y grows downwards). The low road is y 328 everywhere except where noted.

| # | Screen | Low road (y 328) | High road (the treetop tier) | Magpie perch | Lamps | Bones, secrets |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The gate (0-320) | run, hop the log (y 312), leaf pile | none (sky; the tier begins on screen 2) | 1: the path past the log (calm: flees a runner only at 80 px) | 296 | 7 |
| 2 | Bench and hedge (320-640) | bench (seat 300) or crawl under it; crawl through the hedge gap | **Way up 1:** bench seat, running jump to the hedge top (256), held jump up to the plane tree (216) | 2: the bench's backrest (ball on the seat) | 656 | low 7, high 1 (the hedge-top gold) |
| 3 | The pond (640-960) | stones (332), duck boat (deck 346), up the far bank | the plane tree (608-704) then the **treetop walk** (704-944, y 216, solid: no dropping into the pond) | 3: the lamp by the hedge (ball to the path); **4: the walk's rail** (high only) | 976; **high: 864 on the walk** | low 7, high 6 (the walk's gold, secret TREETOP WALK) |
| 4 | Goose lawn (960-1304) | goose (bark or jump), leaf pile, log | the **lime trees**: one-way ledges 48 px apart, 16 to 32 px up or down (y 200, 184, 200, 232) | 5: the log | 1306 | low 7, high 3 |
| 5 | Leaf cart run (1304-1600) | **Way up 2:** the bin (272, jump + scramble), then a held jump to the lime over it (232); picnic table; the carts (see the engine notes) | three more limes (216, 200, 200), the high road skips the cart run | 6: the bin (ball stays on top) | 1624 | low 8, high 3 |
| 6 | The old oak (1600-1920) | hollow log (hop or crawl; gold inside, secret HOLLOW LOG); the oak's branches 300, 272, 244 (gold, secret OAK TOP) | **Way up 3:** from the oak's top branch to the stub (224), then the **crown** (1656-1832, y 192) or the ash. The **golden bone** on the **top twig** (1756-1788, y 152, 40 px above the crown, secret GOLDEN BONE) | 7: the lamp before the oak (ball to the path); **8: the crown** (bark from the branches or the crown) | 1936; **high: 1696 on the crown** | low 5, high 7 (THE golden bone) |
| 7 | The creek (1920-2296) | stop, then hop: three stones 80 px apart; goose on the far bank | the ash (1888-1968, y 200) and the **alder walk** (1968-2312, solid, over the creek) with a **low bough** on it: crawl under (16 px) or hop over (34 px) | **9: the alder walk** (high only) | 2300 | low 7, high 4 |
| 8 | Rose walk (2296-2600) | second cart run: bench, picnic table | the **rose arbour's top**: three slats 48 px apart (216, 200, 216), on to the play tower's top deck | 10: the bench's backrest | 2592 | low 9, high 3 |
| 9 | Playground and the big oak (2600-2880) | slide tower (296), the slide, the climbing frame, the swings, **Mia** (2840) | **The finale** (both roads meet on the play tower's top deck, y 216): bough 184, bough 152, bough 120, the **nest bough** 88 | 11: the frame's top bar; **12: the nest (last perch)** | **high: 2624 on the tower's top deck** | low 6, high 5 (the tower and the boughs) |

Totals: 95 bones (4 gold super bones and the golden bone), 4 secrets, 11 lamps (8 on the path as before, 3 up high).

## The two roads

- **The low road** is City Park as it is: the main route, every set piece kept (geese, carts, pond and duck boat,
  creek, hollow log, the oak's branches, the playground, Mia by the swings). The only additions are the play tower's
  two upper decks and the big oak, which only matter if the magpie still has the ball.
- **The high road** is harder: chains of held jumps between one-way ledges (48 px gaps, 8 to 32 px up or down), no
  geese and no carts, more bones for the distance (30 new ones on about 1,900 px of ledges), the golden bone and two of the four secrets. It is entered three times (the hedge, the bin, the
  old oak) and joins the play tower at the end.
- **Dropping off the high road lands on the low road, never in a pit.** Over the pond and the creek the high road is a
  solid walk with no gaps (the treetop walk, the alder walk), whose ends are over dry land. Everywhere else a fall
  from a ledge lands on the path, a bench, a table, the bin or a lower bough. The checks prove it for every ledge
  (walk off both ends, a running jump off both ends, Down + A through the middle): 124 drops, no heart lost, none in
  the water.
- **Pressure, then a rest at a lamp:** the climb up from the hedge, then the lamp on the treetop walk; the seven limes,
  then the lamp on the old oak's crown; the arbour, then the lamp on the play tower's top deck before the finale.
  The low road keeps its eight lamps. A lamp lights only for a Pepper on its own storey (90 px), so the two roads
  have their own checkpoints.
- **The landmark:** the big oak's crown (x 2600-2880, up to y 8) is the highest thing in the park. From the old oak's
  crown and the alder walk (screens 6 to 8) its top is in view; the art should also put its silhouette in the far
  layer from screen 5 on so it is the goal all the way.

## Every jump, with Pepper's numbers

Pepper: tap hop 24 px, held jump 46 px (about 75 px forward from standing, 92 px running onto the same height),
ledge scramble up to 58 px, steps of 4 px are walked onto; half width 17, standing 26 px, crouched 16 px.
Every jump below is simulated by `--physics` with her own controller (`pepper.lua`) from where a player stands:
a standing held jump from the edge, unless it says running.

| Jump | Gap | Up (+) / down (-) | Needs | Proven |
| --- | --- | --- | --- | --- |
| path -> log | 0 | +16 | tap hop | lands y 312 |
| path -> bench seat | 0 | +28 | held | 300 |
| stone -> stone (pond) | 32 | -4 / 0 | tap hop, running | 332 |
| path -> bin | 0 | +56 | held + scramble | 272 |
| creek stone -> stone | 56 | 0 | stop, then held | 332 |
| oak branches | 0 | +28 x 3 | held, straight up | 300, 272, 244 |
| path -> slide tower | 0 | +32 | held, running | 296 |
| tower top -> deck 2 -> top deck | 0 | +40, +40 | held, straight up through one-way decks | 256, 216 |
| top deck -> bough 1 -> bough 2 | 16, 32 | +32, +32 | held | 184, 152 |
| bough 2 -> bough 3 -> nest bough | 24, 16 | +32, +32 | held (left, then right) | 120, 88 |
| bench seat -> hedge top | 80 | +44 | held, running | 256 |
| hedge -> plane tree | 16 | +40 | held | 216 |
| bin -> lime over it | 0 | +40 | held, up through it | 232 |
| oak top branch -> stub | 48 | +20 | held | 224 |
| stub -> crown / ash | 0 / 16 | +32 / +24 | held | 192 / 200 |
| walk -> lime 1 | 32 | +16 | held (also running) | 200 |
| lime -> lime (x 6) | 48, 40 | +16, -16, -32, +16, +16, 0 | held (also running) | 184, 200, 232, 216, 200, 200 |
| lime 7 -> crown | 16 | +8 | held | 192 |
| crown -> golden twig | 0 | +40 | held, straight up | 152 |
| crown -> ash | 56 | -8 | held | 200 |
| alder walk: the low bough | 0 | +34 (or crawl, 16 px) | held | 166 |
| alder walk -> arbour -> arbour -> arbour -> top deck | 32, 48, 48, 24 | -16, +16, -16, 0 | held (also running) | 216, 200, 216, 216 |

Proven to fail (so the tiers stay apart): the hedge top from the path (72 px), the plane tree from the path
(112 px), the nest bough from bough 2 (64 px).

## The magpie and its perches

Its rules are unchanged (`stage.lua`): it flies on when Pepper comes within 110 px running or 40 px walking (only x
counts), a bark reaches 95 px across and 110 px up or down, the ball falls straight down from its beak. In a tall
level that gives the tiers their meaning: walking under a high perch pushes the magpie on, but only a dog up there
can make it drop the ball.

| # | Perch (x, y) | Bark from | The ball lands on |
| --- | --- | --- | --- |
| 1 | the path past the log (240, 328) | the log | the path |
| 2 | the bench's backrest (400, 282) | the path | the bench seat (28 px up) |
| 3 | the lamp by the hedge (656, 264) | the path | the path |
| 4 | the treetop walk's rail (840, 216) | the walk (not from the pond below) | the walk |
| 5 | the log on the goose lawn (1268, 312) | the path | the log |
| 6 | the bin (1345, 272) | the path or the lime above | the bin top (on the way up anyway) |
| 7 | the lamp before the old oak (1624, 244) | the path | the path |
| 8 | the old oak's crown (1800, 192) | the oak's top branch or the crown | the crown |
| 9 | the alder walk (2160, 200) | the walk (not from the creek's stones) | the walk |
| 10 | the rose bench's backrest (2428, 282) | the path or the arbour | the bench seat |
| 11 | the climbing frame's top bar (2752, 280) | the path | the top bar |
| 12 | **its nest, the top of the big oak (2832, 88)**: the last perch, it stays | bough 2, bough 3 or the nest bough | the nest bough |

The last perch makes sense: magpies build their nests high in a tall tree, and this is the tallest tree in the
park, right over the swings where Mia waits. From the nest bough a Down + A drop lands Pepper next to Mia.

## Secrets and the golden bone

| Secret | Where | How |
| --- | --- | --- |
| TREETOP WALK | the middle of the walk over the pond (gold super bone) | way up 1: the hedge, the plane tree |
| HOLLOW LOG | inside the hollow log (gold) | crawl through instead of hopping over |
| OAK TOP | the old oak's top branch (gold) | up the branches |
| GOLDEN BONE | the old oak's top twig, 40 px above its crown | the high road (or way up 3), then a held jump straight up |

**The golden bone** is new: one per level, at the hardest spot of the high road. Today it is a super bone with
`golden = true` (1,000 points); the engine may later give it its own look and a line on the tally.

## Timing

- The autopilot plays the high road and the finale (`--auto`): GOOD GIRL! in **38.5 s**, no heart lost, 39 of 95
  bones, 2 of 4 secrets (treetop walk, golden bone).
- The low road with the oak finale is about 44 s (City Park's autopilot today) plus the finale (about 9 s): about
  **53 s**. With the carts running again, a wait or two adds 3 to 6 s.
- Suggested par: **75 s** (1.6 x the slower road, rounded up), inside the 60 to 90 s Morning range.

## What the engine must add before this can replace City Park

1. **Cart zones at any height.** `stage.lua` line 318 starts a zone only while `p.y <= 184`, and `Sp.spawn`
   (`setpieces.lua` line 126) puts the cart at `y = 184`; the warning sign (`setpieces.lua` line 150) is placed at
   screen y 184. Spec: a zone may have `y` (its road's feet line, default 184): the zone is entered when
   `p.y > y - 90 and p.y <= y + 2` (the same band as a lamp), the cart drives at `y`, and the sign sits at the
   cart's screen y (`y - s.camY`). The map already holds both zones on the `#carts` layer with `y = 328`: rename the
   layer to `zones` and the class to `bikes`, and add back the two hints `CART! GET UP HIGH!` and
   `ANOTHER CART! UP HIGH!` (`bike = true`).
2. **The hollow log at any height.** Done (engine/round2: `pc.foot`; r3/citypark-art: the map's piece stands on
   `foot = 328`).
3. **The park art at any height.** Done (r3/citypark-art): the art is placed from the level's path line `L.foot`
   (328 here); the level has `L.art = "park"` and the low road looks exactly as City Park does.
4. **The look.** Done (r3/citypark-art): the foreground band finds the flat ground at `L.foot`; the sky is extended
   above the old horizon (see the CHANGELOG).

## Open questions for the owner

- Replace City Park with the tall one (after the engine items 1 to 3), or keep the tall one for a later "City Park
  revisited"?
- The high road is the faster road (38.5 s against about 53 s). Lion King's high roads are often faster too; if the
  low road should feel more rewarding, give it a second secret or the golden bone instead.
- Is a solid boardwalk over the water right for the high road? It obeys "never a pit under the high road" but has
  no gaps; the low bough on the alder walk is its only test.
