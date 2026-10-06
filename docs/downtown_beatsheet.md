# Level 2: Downtown (beat sheet)

The second level. A Stockholm old town street and its plaza: cafe tables with parasols, market stalls, a statue on a pedestal, a fountain, a tram street. A gentle step up from City Park: the moves it taught come back combined (a hop, then a held jump from what she hopped onto), and there are two new twists: carrying the ball over water, and waiting on perches for a long tram.

- **Size:** 6 screens, 1920 px (240 x 30 cells of 8 px). Walking line (feet) y 184, like City Park.
- **Time limit:** 300 s.
- **Story (level 2 of 3):** in town the ball rolled away across the plaza and a cat sat on it. Pepper barks the cat away, picks the ball up and carries it to the girl, who waits at the stairs down to the river. Outro: by the river she throws it again and it lands on a ferry, which is where Level 3, River Walk, starts.
- **Moves used:** run, tap hop, held jump, crawl, ledge scramble, one-way tops (jump up through, Down + A drops through), bark, pick up, carry, dodge a hazard from a perch.

## Screens

| # | Screen | Pepper does | Set pieces | Hazards | Bones | Checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Old town lane (0-320) | Tap A: hop up the crate steps (16 px, then 16 px more). | DOOR, CRATES (low 32x16 top y 168, high 32x32 top y 152) | none | 6 | lamp x 296 |
| 2 | Cafe terrace (320-640) | Crawl under both tables (19 px gap) or jump onto one (26 px). From a table, a held jump onto its parasol (44 px up); a running jump from parasol to parasol; from the second parasol, a running jump onto the shop sign (gold bone). | 2 TABLES (top y 158-165, 48 wide), 2 PARASOLS (one-way, top y 114, 64 wide), SIGN (one-way, y 80) | none | 8 (1 gold) | lamp x 636 |
| 3 | Market (640-960) | Hold A: onto the stall's counter (28 px), up onto its awning (40 px). Down + A drops back through. Hop up the crate stack (16 px, 16 px), a held jump onto the second awning (40 px). The street under it is clear. | STALL (counter 64x28, top y 156), AWNING (one-way, y 116), CRATES (32x16, 32x32), AWNING 2 (one-way, y 112) | none | 7 | lamp x 960 |
| 4 | The plaza (960-1280) | The cat sits on the ball on the statue's arm. Y: bark near it, the cat runs off, the ball drops to the street. X: pick it up. Optional climb: the flower tub is a step (28 px: a tapped hop and a scramble), the pedestal 12 px above it (or 40 px from the street, a held jump), the arm (36 px), the hat (32 px, gold bone, a secret). | TUB 32x28 (top y 156), PEDESTAL 48x40 (top y 144), STATUE, ARM (one-way, y 108), hat (one-way, y 76), CAT | none | 8 (1 gold) | none |
| 5 | The fountain (1280-1600) | Carry the ball over the basin: tap A onto the rim (16 px), hop to the fountain bowl (40 px gap), hop to the far rim. Falling in costs a heart and the ball goes back by the statue. **High route (a secret):** from the statue's arm, running held jumps along the balconies and over the fountain's top tier (gold bone), down to the street by the lamp. | RIM x2 (16x16), basin water x 1416-1528 (from y 192), FOUNTAIN bowl 32 wide (top y 160), 3 HOUSES, 3 BALCONIES (one-way, y 104, 96, 104), TIER (one-way, y 104) | water: a heart | 11 (1 gold) | lamp x 1300 |
| 6 | Tram street (1600-1920) | The tram sets off when she walks into its zone (x 1610-1800): its bell rings and a warning sign shows at the right edge 1 s before it is on screen; then one every 6 s. Get up on the kiosk (36 px, held jump), jump onto the shelter roof (12 px up, 40 px across), wait for the tram to pass, then run to the girl at the stairs down to the river and give her the ball (X). Without it the hint says "GO BACK FOR THE BALL". | KIOSK 40x36 (top y 148), SHELTER roof (one-way, y 136), RIVER sign, the girl (x 1860), stairs (terrain slope, x 1888-1920, down to y 216) | the TRAM (80x26 hit box, every 6 s, 110 px/s) | 5 | lamp x 1600 |

Total: 45 bones, 3 of them gold super bones (the shop sign, the statue's hat, the fountain's top tier).

## Secrets and the second route

Three secrets, counted on the tally (`stats().secrets` of `secretsTotal`; "SECRET! <NAME> n/3" when found):

| Secret | Where | How |
| --- | --- | --- |
| SHOP SIGN | the shop sign over the cafe terrace (gold bone) | table, parasol, parasol, running jump to the sign |
| STATUE HAT | the statue's hat (gold bone) | tub, pedestal, arm, hat |
| ROOFTOPS | the fountain's top tier (gold bone) | the high route below |

**The second route:** the rooftops. With the ball, from the statue's arm along three balconies on the houses at the back of the plaza and over the fountain's top tier, instead of hopping over the basin. It rejoins the street at x 1580, by the lamp before tram street. Every jump is a running held jump (gaps 34 to 56 px).

## Hard mode

Chosen in the menu (`carry.hard`; `--hard` for the checks): 1 heart, the tram 25% faster (137.5 px/s). The autopilot still clears the level without a hit.

Every screen keeps about 100 px of open street (screen 4 and 5 more, around the plaza). One or two characters per screen at most: the cat on screen 4, the tram on screen 6.

## The cat and the ball

1. **Sit:** the cat (greybox 22x16, label CAT) sits on the ball on the statue's arm, 76 px above the street. The ball cannot be picked up. Hint on the plaza: "Y: BARK AT THE CAT!". If she walks on past the plaza: "GO BACK: BARK AT THE CAT".
2. **Bark:** a bark scares the cat when Pepper's middle is within 90 px of the cat's middle. That works from the street right under the arm (x 1144-1232), from the pedestal top, or from the arm itself. A bark from further away (up to 180 px) only makes the cat look up ("?").
3. **Scared:** the cat jumps up with a "!" (0.35 s), leaps off away from Pepper and runs out of the level. The ball is knocked off the arm, falls through it and drops to the street beside the pedestal (x about 1175).
4. **Gone:** "THE CAT RAN OFF! GET THE BALL".
5. **Fetch:** X picks up the ball ("TAKE THE BALL DOWN TO THE RIVER!"). She carries it in her mouth; every move still works (checked: crawl under a table, held jump onto the kiosk with the ball).
6. **Fountain:** if Pepper falls in the fountain with the ball, she loses a heart and the ball goes back by the statue ("THE BALL IS BACK BY THE STATUE"); she restarts at the lamp before the fountain and walks back for it.
7. **Fetch:** X near the girl at the stairs gives her the ball: GOOD GIRL!, FETCH 2000, then the tally (BONES, FETCH 2000, TIME BONUS). Outro: "BY THE RIVER SHE THREW IT / AGAIN. IT LANDED ON A FERRY...".

## Estimated play time

- A straight run: about 30 s (the autopilot: no hearts lost, 39 of 45 bones, 2 of 3 secrets, climbs to the sign and the hat, waits a moment on the shelter roof for the tram, which sets off as it arrives). Hard mode: the same, about 30 s.
- A first play, with a fall in the fountain and reading the hints: 2 to 3 minutes.

## Art needed later (sizes in game px)

Obstacles (Pepper uses them: outlined, mid-tone, never faded)

| Asset | Size | Notes |
| --- | --- | --- |
| Crates | 32x16 and 32x32 (x2 stacks) | wooden fruit crates, stacked as steps |
| Cafe table | 48 wide, top y 158-165, legs to the street | crawl gap 19 px under the top; two chairs could stand beside it as decoration |
| Parasol | 64x4 canopy top, pole 4x40 | one-way top; striped canvas |
| Shop sign | 40x4 bar on a post (post 4x108) | one-way; a hanging old town shop sign (the gold bone) |
| Market stall | counter 64x28, awning 80x4 on two posts (68 tall) | striped awning, fruit boxes on the counter |
| Awning 2 | 64x4 on one post | one-way, over open street |
| Flower tub | 32x28 | a step up to the pedestal |
| Pedestal | 48x40 | stone pedestal |
| Statue arm and hat | arm 40x4, hat 24x4 | one-way, part of the statue art |
| Fountain rims | 16x16 (x2) | stone basin wall |
| Fountain bowl | 32 wide, top y 160, down into the water | stone bowl on a column |
| Balconies | 56x4 (x3) | one-way, wrought iron, on the houses behind the plaza |
| Fountain top tier | 48x4 on a 8x20 column | one-way, the fountain's upper basin rim |
| Kiosk | 40x36 | newspaper kiosk, flat roof |
| Tram stop shelter | roof 72x4, posts 4x44 | one-way roof |
| Tram (hazard) | 80x26 hit box, art about 96x48 | Stockholm tram, drives right to left; bell sound |
| Cat | 22x16 cell | sit (on the ball), startle, leap, run (shared with any later level) |

Decoration (faded towards the haze, no outline)

| Asset | Size | Notes |
| --- | --- | --- |
| Old town doorway | 28x64 | at the level's left edge |
| Statue figure | 28x64 | on the pedestal, behind the arm |
| Plaza houses (x3) | 88x118, 80x126, 68x118 | behind the plaza and the fountain (base y 174), carry the balconies |
| Fountain spout | 12x32 | above the bowl; water jets could animate |
| Basin water | 112x48 (surface y 192) | animated ripples, like the pond |
| RIVER sign | 28x20 on a 4x44 post | points down the stairs |
| River stairs | 32x32 | stone steps going down to the quay (terrain shape fixed by the map) |
| Lamp post | 14x101 | reuse River Walk's lamp (lit = checkpoint) |
| Street and pavement | 320 px loop, about 56 tall | cobbles |
| Near facades | 320 px wide strip, houses 34-58 wide, 44-90 tall | parallax 0.5; old town gables, ochre and red plaster, rows of windows |
| Far roofs and spires | 320 px wide strip | parallax 0.25; roofs and church spires (Storkyrkan, Tyska kyrkan) |
| Far city | 320 px wide strip | parallax 0.08, as City Park |
| Arcade pillars | 12x184 (x2) | foreground frame, scroll 1.3x |

Characters

| Asset | Size | Notes |
| --- | --- | --- |
| Pepper, ball | existing | real art already |

## Running it

| Command | Does |
| --- | --- |
| `love riverwalk --level downtown` | plays Downtown |
| `... --level downtown --physics` | 57 checks: every set piece (heights, gaps, one-way tops, the tub and the statue climb), the cat and the ball, moves while carrying the ball, the fountain, the tram, the rooftops route with the ball, every secret, the tram's start and warning, hard mode, the girl with and without the ball |
| `... --level downtown --auto` | the autopilot plays to GOOD GIRL! and saves every 3rd frame to `rec/` |
| `... --level downtown --test` | screenshots: the card, the 6 screens, the cat beat (sit, bark, leap, run, ball down, pick up), three debug views, the tub, the rooftops, the tram's warning sign, giving the ball, the tally |
| `... --level downtown --auto --hard` | the autopilot in hard mode |
| `... --level downtown --qa` | the collision QA sweep (0 problems) |

The greybox look: `scenery = "greybox"` and `greyStyle = "town"` in `level/downtown.lua`. Sky, clouds and far city as in City Park; layer 4 is far roofs with church spires, layer 5 old town facades with stepped gables and rows of windows. Flat grey street with a 1 px edge, the basin water as a flat box, outlined labelled boxes for everything Pepper uses, flat boxes for decoration. Pepper and the ball are the real art.
