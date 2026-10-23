# Level 2, tall: Downtown with the roofs of the old town (beat sheet)

Downtown as it plays today, moved down 30 rows, with a second road over the roofs of the old town above it.
`love riverwalk --level downtown_tall`.

> **r8/levels (23 Oct):** this is the game's Downtown now (level 3, D2), with Downtown's art (`art = "town"`, `foot = 424`; the high road's pieces drawn in code until the roof kit lands, docs/art_hooks_r8.md). D1: every tram below is now the baker's cargo bike (the same zones, hit box, speeds and perches; it rides into courtyard gates, the old tram sheds), and a vintage tram rolls by in the back lane as scenery. The hints HOLD: UP ON THE ROOFS and HOLD: BOUNCE UP! are HOLD: CLIMB UP and HOLD: BOUNCE.


- **Size:** 11 screens x 2 screens: 3520 x 480 px (440 x 60 cells). The street (the low road) is at y 424. On the
  street the camera rests at the bottom of the world (camera y 240), so the low road looks exactly as Downtown does
  today; the roofs (y 232 to 280) are above the top of the screen there, and come into view as soon as Pepper is
  up on the bakery sign or the statue's hat.
- **Time of day:** late morning (chapter Morning: 60 to 90 s of perfect play).
- **Manner:** bounce and carry (unchanged), now in two storeys.
- **Story:** unchanged. In town the ball rolled across the plaza and a cat sat on it on the statue's arm. Pepper
  barks it away and carries the ball to Mia at the stairs down to the river. New: the cat can be barked off from
  the loggia right above it, which is how a dog on the roofs gets the ball.
- **Files:** the map `maps/downtown_tall.tmx` (edit it in Tiled; its export `riverwalk/level/tiled/downtown_tall.lua`),
  the loader `riverwalk/level/downtown_tall.lua`, the first draft's generator `tools/make_downtown_tall.py` (it will
  not overwrite the map without `--force`), the checks `riverwalk/tests_downtown_tall.lua`.
- **Paper map:** `/home/claude/out/r3-design/downtown_tall_routes.png` (`python3 tools/draw_routes.py downtown_tall
  <out.png>`): the low road in blue, the high road in orange, the loop for the ball and the middle tier thin.

## The idea, in four beats

The idea of the level is **bounce, then carry**: springy awnings and parasols launch Pepper higher than she can
jump, and once she has the ball she must keep it through water, trams and geese.

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | screen 4, the bakery row | A springy awning in front of a crate wall too high to jump. Land on it and it launches her over (76 px). Below is the street: a miss costs nothing. Holding Down she stands on it. |
| 2 Practise | screen 4 to 5 | The springier awning reaches the bakery sign (gold), and from the sign the first balcony of the roofs (way up A). On the plaza the cat sits on the ball: bark from the street, the pedestal, the arm, or from the loggia right above it. |
| 3 Combine with an earlier mechanic | screens 5 to 9 | Carry meets climbing: with the ball in her mouth she climbs the statue (pedestal, arm, hat) back up to the loggia (way up B), walks up the guild house's roof, hops the gallery's gap over the fountain, the roof ledges over the tram and the geese, and a springy window awning up to the flower roof. Below, the low road carries the ball over the fountain, past the tram and the geese, and bounces over the canal. |
| 4 Twist, then the fetch | screens 10 to 11 | Both roads meet at the flooded square: three springy parasols in the water, bounce from one to the next without stopping (hold Right). Then the faster tram (wait on the shed, then the shelter), and Mia at the river stairs under Riddarholmen's spire, the landmark: give her the ball. GOOD GIRL! |

## Screen by screen

y is the feet line (world px, y grows downwards). The street is y 424 everywhere except the river stairs.

| # | Screen | Low road (y 424) | High road (the roofs, y 232 to 280) | Lamps | Bones (Downtown's + new) |
| --- | --- | --- | --- | --- | --- |
| 1 | Old town lane (0-320) | crate steps (16, 16 px) | none (sky) | | 6 |
| 2 | Cafe terrace (320-640) | tables (crawl or jump), parasols, the shop sign (gold, SHOP SIGN) | none | 636 | 8 |
| 3 | Market (640-968) | stall, awning, crate steps, second awning | none | 960 | 7 |
| 4 | Bakery row (968-1288) | springy awning over the crate wall; the springier one to the bakery sign (gold, BAKERY SIGN) | **way up A:** bakery sign (304) to the BALCONY (1328-1392, 272) | | 6 |
| 5 | The plaza (1288-1608) | the cat on the statue's arm; tub, pedestal, arm, hat (gold, STATUE HAT) | the LOGGIA (1416-1536, 280) right over the cat; **way up B:** the hat (316) to the loggia, 36 px straight up | 1620 | 10 + 5 high |
| 6 | The fountain (1608-1928) | rims and the bowl over the basin (carry the ball); middle tier: Downtown's three balconies and the fountain's top tier (gold, ROOFTOPS) | the GUILD ROOF (one-way steps 4 px high, 272 up to the ridge 244), its CHIMNEY (200, **the golden bone**), the GALLERY in two solid halves (1680-1768 and 1816-1888, y 256) with a 48 px gap over the top tier | 1959 (street); **high: 1830 on the gallery** | 11 + 7 high (THE golden bone) |
| 7 | Tram street (1928-2136) | tram shed, kiosk, shelter: the tram every 6 s | DORMER (264), roof ledge (248), roof ledge (264): no tram up here | | 3 + 4 high |
| 8 | Flower market (2136-2456) | two geese (bark, or the tub, table, springy parasol, balcony) | the springy window AWNING (272, bounce 56) up to the FLOWER ROOF (232), the last ledge (248) | **high: 2420 on the last ledge** | 6 + 7 high |
| 9 | The canal (2456-2784) | the springy awning launches her over the water onto the crates | the FOOTBRIDGE over the canal (2480-2640, 272, solid), off its end onto the crates: the roads meet | 2528, 2764 | 7 + 4 high |
| 10 | Flooded square (2784-3104) | the bounce chain: crate, three parasols, tram shed | (both roads) | | 7 |
| 11 | Tram street, river stairs (3104-3520) | the fast tram every 4 s; shed, shelter; Mia (3460) | (both roads); Riddarholmen spire (3380-3412, up to y 24) | | 4 |

Totals: 102 bones (75 from Downtown, 27 new up high; 5 gold super bones, one of them the golden bone), 5 secrets,
8 lamps (6 on the street as before, 2 up high).

## The two roads

- **The low road** is Downtown as it is: every set piece kept (crates, cafe, market, the springy awnings, the cat
  and the statue climb, the fountain, two tram streets with their sheds, the geese, the canal, the flooded square,
  Mia at the river stairs). Its only change is that a hint for one spot shows only on the street.
- **The high road** is harder: a chain of held jumps over 40 to 48 px gaps, 8 to 16 px up or down, a pitched roof,
  a chimney that needs a held jump straight onto it (44 px), a springy awning that must be ridden with Right held,
  and the cat to be barked off from above. It has no trams and no geese, 27 bones on about 1,300 px of roofs, the
  golden bone and the GOLDEN BONE secret. It is entered twice: way up A (the bakery sign, before the cat) and way
  up B (the statue's hat, after the cat, with the ball). A dog that goes up at the bakery barks the cat off from
  the loggia, drops down for the ball (Down + A onto the arm, a step to the street), and climbs the statue back up.
- **The middle tier:** Downtown's old secret route (the arm, three balconies and the fountain's top tier) stays
  under the roofs. Nothing solid hangs lower than y 262 over it, so its running jumps (heads up to y 272) never
  touch the gallery; the checks prove it.
- **Dropping off the high road lands on the low road, never in water.** Over the fountain and the canal the high
  road is solid (the gallery, the footbridge) with its ends over dry floors; the gallery's gap is right over the
  fountain's top tier and walking off into it lands on the tier. Everywhere else a fall lands on the street, a
  balcony, the statue, a shed or the crates. The checks prove it for every ledge (walk off both ends, a running jump
  off both ends, Down + A through the middle): 63 drops, no heart lost, none in the water.
- **Pressure, then a rest at a lamp:** the roof and the chimney, then the lamp on the gallery; the roof ledges and
  the springy window awning, then the lamp on the last ledge before the footbridge. A lamp lights only for a Pepper
  on its own storey (90 px), so the two roads have their own checkpoints. With the ball in her mouth, a lamp becomes
  the ball's home (`L.ballHomeAtLamps`), up high too.
- **The landmark:** Riddarholmen church's cast-iron spire (x 3380-3412, up to y 24), right over the river stairs
  where Mia waits. From the roofs (screens 6 to 9) it stands above the skyline; the art should also put it in the
  far layer from screen 1 on so it is the goal all the way.

## Every jump, with Pepper's numbers

Pepper: tap hop 24 px, held jump 46 px, ledge scramble up to 58 px, steps of 4 px are walked onto; half width 17,
standing 26 px, crouched 16 px. Every jump below is simulated by `--physics` with her own controller (`pepper.lua`)
from where a player stands: a standing held jump from the edge unless it says otherwise.

| Jump | Gap | Up (+) / down (-) | Needs | Proven |
| --- | --- | --- | --- | --- |
| bakery: springier awning -> bakery sign (way up A) | 0 | +88 | running held jump, bounce 100 | 304 |
| bakery sign -> balcony | 18 | +32 | held | 272 |
| balcony -> loggia | 24 | -8 | held | 280 |
| street -> pedestal from its right side (with the ball) | 0 | +40 | held | 384 |
| pedestal -> arm -> hat | 0 | +36, +32 | held | 348, 316 |
| hat -> loggia (way up B) | 0 | +36 | held, straight up through it | 280 |
| loggia -> guild roof | 24 | +8 to +16 | held | 256 to 264 |
| up the roof's steps to the ridge | 0 | 4 px steps | walk | 244 |
| ridge -> chimney (the golden bone) | 0 | +44 | held | 200 |
| gallery -> gallery | 48 | 0 | held (also running) | 256 |
| gallery -> dormer -> ledge -> ledge | 32, 40, 40 | -8, +16, -16 | held (also running) | 264, 248, 264 |
| ledge -> window awning -> flower roof | 40, 24 | -8, then bounce 56 | held, Right held through the bounce | 232 |
| flower roof -> last ledge -> footbridge | 40, 16 | -16, -24 | held (also running) | 248, 272 |
| Downtown's middle tier: arm -> balcony -> balcony -> tier -> balcony | 34, 48, 56, 24 | small | running held | 344, 336, 344, 344 |

Proven to fail (so the tiers stay apart): the loggia from the street and from the statue's arm (68 px), the
balcony from the springier bakery awning (its apex is 20 px short), the flower roof from the springy parasol.

## The cat, from above

The cat's rules are unchanged (`stage.lua`): a bark scares it when Pepper's middle is within 90 px of the cat's
middle; up to 180 px it only looks up ("?"). The loggia is 68 px above the arm, so from the loggia a bark works
from x 1448 to its end (1536), and from its west end it only makes the cat look up (a hint for a child: "BARK FROM
UP HERE!" shows on the loggia while the cat sits). The ball drops to the street by the pedestal (x 1495); "DOWN + A:
DROP" shows on the loggia once the cat is gone. Down + A off the loggia lands on the arm, a step from the street.

## Timing

- The autopilot plays the high road with the ball (`--auto`): way up A, the cat from the loggia, down for the ball
  and back up the statue, the roofs, the footbridge, the flooded square, the fast tram: GOOD GIRL! in **56.9 s**, no
  heart lost, 66 of 102 bones, 4 of 5 secrets.
- The low road is Downtown's autopilot (51.6 s) plus about 1 s: about **53 s**.
- Both are a little under the Morning chapter's 60 s floor for perfect play, as Downtown is today: the two tram waits
  are the only pauses. To bring it into range without lengthening the map: make the first tram zone start a tram
  on entering only after the shed (a 2 s wait), or add a third springy step on the roofs. Suggested par: **85 s**.

## What the engine must add before this can replace Downtown

1. **The town art at any height.** `Sc.drawPropArt` and the art ground place Downtown's props and street at y 184
   (`scene.lua`, as for City Park). Spec: from each prop's own box and the map's floor. Until then the level has no
   `L.art`; the greybox draws everything. New art pieces: the loggia, the guild house roof (stepped one-way ledges
   drawn as one roof), the chimney, the gallery, the dormer and roof ledges, the window awning, the footbridge,
   Riddarholmen's spire.
2. **The look** (`look.lua`) finds the street by `y0 == 184`; it should use the floor under Pepper (as for
   citypark_tall).
3. Nothing else: the trams use `roadY`, the cat's leap and the ball's home use the tall world's floors already.

## Open questions for the owner

- Replace Downtown with the tall one (after the art), or keep it for a later "Downtown revisited"?
- The high road is a little slower than the low road (56.9 s against about 53 s), because of the loop for the ball.
  Is that the right trade (more bones and the golden bone for a longer road)?
- Should the cat move? It could sit on the loggia instead, so the high road meets it on the way and the low road
  has to climb; today both roads meet at the statue.
