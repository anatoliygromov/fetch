# Level 3: Rooftops (beat sheet and paper map)

A new level between Downtown and River Walk. Noon, sun on copper and tin. The first level that only goes up.

- **Paper map:** `maps/rooftops_sketch.tmx` (greybox geometry only, not wired into the game; drawn by
  `tools/make_rooftops_sketch.py`). Renders: `/home/claude/out/design-round2/rooftops_sketch.png` (the map) and
  `rooftops_sketch_routes.png` (the routes, lamps, secrets, the golden bone, steam puffs, loose tiles, the landmark;
  `python3 tools/draw_routes.py rooftops_sketch`).
- **Size:** 6 x 4 screens, 1920 x 960 px (240 x 120 cells). From the street (feet y 904, bottom left) to the nest
  chimney's top (y 136, top right): 768 px of climbing, 3.2 screens.
- **Story:** Mia has a lemonade at a cafe table on the street. A gull lands, snatches the ball off the table and
  flies up to its nest on the tallest chimney. "I'LL TAKE THE LIFT UP TO THE ROOF TERRACE! MEET ME THERE!" (the
  caretaker runs the lift). Pepper climbs. At the top she barks the gull off its nest, takes the ball, and brings it
  to Mia on the roof terrace below the chimney.
- **Manner:** climbing. The idea of the level: **steam puffs lift Pepper**. Loose tiles are the pressure.
- **Dog logic:** no ladders, no drainpipes. Up by stairwells (45 degree stairs, walked), pitched roofs (slopes),
  hops and held jumps, and steam puffs from vents (each one has someone making it: a cook, a dryer, an oven, a sauna).

## The idea, in four beats

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | T1, the first flat roof (y 712) | The cafe's kitchen fan sits in the flat roof. It rattles (0.8 s), then puffs: standing on it, Pepper rides up 112 px onto the dormer ledge (3 bones, secret DORMER). Below is the flat roof: a miss costs nothing. A bark at the vent makes the cook turn the fan up: the next puff comes at once. |
| 2 Practise | T1 to T2 | The dormer's own vent lifts her to the high road; then the laundry room's dryer vent (on a ledge over T2) does the same with a sideways step at the top. Each puff lands her 16 px under its apex, so she steers onto the ledge. |
| 3 Combine with an earlier mechanic | over T2 | Loose tiles (new) between the ledges, and River Walk's gull circling over T2 (crawl to duck, bark to send it off for 4 s). The bakery chimney lifts her 144 px from the last ledge to the copper roof. |
| 4 Twist, then the fetch | the top: copper roof and the nest chimney | The terrace fan (both roads) lifts her through the one-way copper roof. The last vent, the roof sauna's chimney, never puffs on its own: Pepper barks, the guest inside throws water on the stones, one big puff (112 px) carries her to the nest chimney's top. Bark at the gull (it flies off), pick up the ball, step off the chimney onto the terrace, give it to Mia. |

## The routes

y is the feet line, world px (y grows downwards). The street is y 904, the flat roofs T1 712, T2 520, the roof
terrace T3 328, the copper roof 232, the nest chimney's top 136.

**Main route (the low road: the stairwells).** Street, stairwell A (up 192 px of stairs), across T1 and over the
pitched roof R1 (ridge 616), stairwell B, across T2 and over R2 (ridge 456), stairwell C, the roof terrace. Then the
finale, shared: the terrace fan up to the copper roof, the sauna up to the nest. No jump on the low road is more
than a walk until the finale; its pressure is the gull over T2 and the timing of the two last puffs.

**High route (over the roofs).** From T1: the kitchen fan to the dormer (616), the dormer vent to the first ledge
(520), three loose tiles 32 px apart, the gable (lamp), two ledges up (488, 456; gaps 32, 32 px up each), the
laundry vent to the next ledge (360), two loose tiles, the chimney ledge (360), the chimney pot (the golden bone, 48
px up: jump and scramble), the bakery chimney's puff (144 px) to the copper roof (232). It has 12 bones against the
low road's 19 on twice the distance, the golden bone and both secrets.

**Dropping off the high road lands on the low road:** every ledge and loose tile is over a flat roof, a pitched roof
or a stairwell's stairs. There is no hole in the level: every column has a roof or the street under it.

| Jump (plain, with Pepper's numbers) | Gap | Up | Needs |
| --- | --- | --- | --- |
| ledge 520 -> loose tiles -> gable | 32, 32, 32, 32 | 0 | held jump (proven in citypark_tall: gap 48 at 16 up) |
| gable 520 -> ledge 488 -> ledge 456 | 32, 32 | +32, +32 | held (proven: the big oak's boughs, gap 32 at 32 up) |
| ledge 360 -> loose tiles -> chimney ledge 360 | 32, 32, 24 | 0 | held or tap |
| chimney ledge -> chimney pot (golden bone) | 0 | +48 | held jump and scramble (up to 58) |
| copper roof -> nest chimney | 16 | +96 | only the sauna's puff |

Puff landings (each puff's apex is 16 px above the ledge it serves; the vent is at least 17 px, Pepper's half width,
clear of any solid above it, so she never bumps her head on the way up):

| Vent (who) | On | Lift | Lands on | Sideways at the top |
| --- | --- | --- | --- | --- |
| KITCHEN FAN (the cafe's cook) | T1 712 | 112 | dormer 616, right above | 0 |
| DORMER VENT (an attic bathroom fan) | dormer 616 | 112 | ledge 520 | 13 px right |
| LAUNDRY VENT (the dryer) | ledge 456 | 112 | ledge 360 | 12 px right |
| CHIMNEY (the bakery's oven) | chimney ledge 360 | 144 | copper roof 232 | 29 px right |
| TERRACE FAN (the roof restaurant) | terrace 328 | 112 | copper roof 232 (one-way: up through it) | 0 |
| SAUNA (a bark: the guest throws water) | copper roof 232 | 112 | nest chimney top 136 | 17 px right |

## Lamps, secrets, the golden bone, the landmark

- **Lamps (6):** the street by the cafe (40, 904), T1 (512, 712), T2 (1216, 520), the terrace (1648, 328), and up
  high the gable (984, 520, after the first loose tiles) and the copper roof (1600, 232, before the finale). Pressure,
  then a rest: the loose tiles, then the gable's lamp; the bakery puff, then the copper roof's lamp.
- **Secrets (2):** DORMER (the first puff's ledge: a kid finds it by accident, which teaches that puffs go somewhere)
  and GOLDEN BONE (the chimney pot).
- **The golden bone:** on the chimney pot (1500, 312), the hardest spot of the high road: after two loose tiles, a held
  jump and a scramble.
- **The landmark:** the nest chimney (x 1808-1840, 192 px tall above the terrace) with the gull's nest. In the far
  layer the City Hall tower (with its three crowns) stands behind the street on screen 1, so the skyline says
  Stockholm, but the goal is the chimney: draw a thin line of steam from the sauna next to it, visible from every
  screen, and the gull circling it.
- **Mia** waits on the roof terrace (1720, 328) by the lift house; the girl's call ("BRING ME THE BALL!") works as
  in every level.

## Timing (estimate)

The low road: about 2,300 px of walking and stairs (19 s at 120 px/s), plus the gull over T2 (a duck or a bark, 2 s),
plus the finale (two puff waits, up to 3 s each, the bark, the ball, the walk to Mia: 10 s): **about 35 to 40 s**.
The high road: 12 puffs-and-ledges at 2 to 3 s each plus the loose tiles: **about 45 s**. With the puffs' rhythm a
perfect run is about 45 to 50 s, below the Morning chapter's 60 to 90 s; if the owner wants it longer, add a
fourth tier (the level is 4 screens tall; the top screen is mostly sky today) or a second gull over T1.

## New mechanics the engine needs (specs)

### 1. Steam puff (`L.steam`)

Each entry is a vent: `{ name, x0, x1, y0, y1, lift, every, warn, puff, source, bark }`. The box is the vent hood
(drawn, solid like a 4 px step: Pepper walks onto it); its top `y0` is the vent's mouth.

- **Cycle:** `rest` for `every - warn - puff` s, then `warn` for `warn` s (0.8 s: the hood's flap rattles, a "chuff"
  sound, two small wisps rise 8 px), then `puff` for `puff` s (0.9 s: a column of steam from the mouth up to
  `y0 - lift - 16`, drawn behind Pepper, semi-transparent, never over her), then `rest` again. Vents start at
  different phases (`phase` s, optional) so neighbours do not puff together. `every = 0` (with `bark = true`):
  the vent rests until barked.
- **A bark is always useful:** a bark with Pepper's x within 80 px of the vent's middle and her feet within 60 px of
  `y0` skips the rest: `warn` starts now (someone heard her and turned the fan up). For a `bark = true` vent this is
  the only way it puffs. (A short line the first time: "WOOF! THE SAUNA STEAMS UP!")
- **The lift:** while the vent is in `puff`, if Pepper's feet x is within the mouth (x0 - 6 .. x1 + 6) and her feet y
  is between `y0 - lift` and `y0 + 2`, and she is not crouched, and she has not been lifted by this puff yet: set
  `p.vy = -sqrt(2 * 560 * (p.y - (y0 - lift)))`, `p.onGround = false`, `p.ground = nil`, and
  `p.jumpBase = (y0 - lift) + P.minJump` (the same trick as `Cr.bounce`, so letting go of A does not cut the rise).
  Her apex is exactly `y0 - lift`; from there she falls as after any jump and can steer (she drifts at most about
  40 px sideways from the apex to a ledge 16 px below it). One lift per puff: a Pepper who falls back into the column
  is not lifted again until the next puff. A puff that starts while she stands on the hood lifts her too.
- **Never harmful:** steam does not hurt. Crouching on the hood (Down) is the way to stay put through a puff.
- **Sound and look:** warn: a rattle; puff: a soft "pfff"; the column is a 3-frame animation; a lifted Pepper uses her
  jump frames.
- **Checks to write:** each vent's apex equals `y0 - lift` within 1 px; a Pepper on the hood with no input lands on
  the ledge it serves when steering towards it, and lands back on the hood (or the floor below) with no input; a
  bark starts a resting vent within one frame and a bark vent puffs only after a bark; one lift per puff.

### 2. Loose tile (props with `loose = true`)

A one-way ledge (24 x 6 px) on a roof. Generalise Night Harbour's `crumble` (today in `night.lua`, only active in a
dark level) into `setpieces.lua` for any level, and add the loose tile's own look:

- **Warn:** the moment Pepper's feet land on it, it starts to shake (2 px left and right, every 0.1 s) with a tile
  "clink" sound and a puff of grit: **0.6 s** to step or hop off (Night's planks give 0.5 s; 0.6 s for kids 6 to 10).
- **Fall:** then it tips and slides off (it is no longer a floor), falls with gravity and breaks on the roof below
  with a clatter (no damage to anyone: it only drops when Pepper is on it, so it never falls on her).
- **Back:** 3.0 s later it is back in place, but only once Pepper's box does not overlap it (as Night's planks).
- **Rule for designers:** never two loose tiles more than 32 px apart, never a loose tile over a hole; there is a
  solid floor or a stable ledge within one held jump of every loose tile.
- **Checks to write:** a tile under Pepper is a floor for 0.6 s then is not; standing still she falls through at
  0.6 s; hopping on at 0.3 s intervals crosses a three-tile bridge; it comes back after 3 s and not while she is in
  its place.

### 3. Smaller things

- **The gull's nest:** a gull that sits on a perch (like the magpie's last perch) with the ball; a bark within 95 px
  across and 110 px up or down makes it fly off and leave the ball where it sat. (It can reuse the magpie's code with
  one perch and a gull drawing: `L.magpie = { perches = { { x = 1824, y = 136 } }, look = "gull" }`.)
- **Mia moves to the terrace:** the intro card shows the cafe, then L.girl is on the terrace. No engine change if the
  story card tells it; a short cut-scene would be nicer.
- **The lift house:** decoration only (Mia's ride). It could be a real lift (lift.lua) as a third, slow route up for
  a child who is stuck, run by the caretaker.

## Open questions for the owner

- Rooftops as level 3 pushes River Walk to 4 and Soder Hill to 5. Is it right that the first tall level comes so
  early? It teaches the vertical camera before the Metro and the Building site need it.
- The perfect run is short (about 45 to 50 s). Add a fourth tier (the top screen is sky) or keep it short as the
  first climbing level?
- Should the sauna puff need a bark (the twist), or would kids miss it? The hint "BARK!" over the sauna would show
  the first time Pepper stands next to it.
