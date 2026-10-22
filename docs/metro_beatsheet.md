# Level 5: Metro (beat sheet, paper map and engine specs)

Early afternoon. T-Centralen to Odenplan, under the city. The first level that goes down and then rides.

- **Paper map:** `maps/metro_sketch.tmx` (greybox geometry only, not wired into the game; drawn by
  `tools/make_metro_sketch.py`). Renders: `/home/claude/out/r3-design/metro_sketch.png` (the map) and
  `metro_sketch_routes.png` (`python3 tools/draw_routes.py metro_sketch <out.png>`: routes, lamps, secrets, the
  golden bone, escalators with the way they carry her, walkways, gates, doors, the wagon's ride, the tunnel signs).
- **Size:** 8 x 3 screens, 2560 x 720 px (320 x 90 cells). Three rows joined by escalators, in a zig-zag:
  row 1 (Sergels torg and the ticket hall, feet y 184) runs right, row 2 (the long passage, y 424) runs left,
  row 3 (Stockholm City's platform, the tunnel, Odenplan, y 664) runs right. Rock everywhere else.
- **Chapter:** Midday (90 to 130 s of perfect play). Path length about 5,000 px plus a 13 s ride: an estimated
  95 to 110 s for the autopilot, with one wait at the gates and one at the screen door.
- **Story:** On Sergels torg, by the glass obelisk, Mia is bouncing the ball on the way to the metro. It slips,
  bounces down the escalator into T-Centralen, through the passage, down to the platform and onto the track
  crew's flat wagon, which is about to leave. Mia: "I'LL TAKE THE TRAIN TO ODENPLAN! MEET ME THERE!" Pepper
  follows the ball down, rides the wagon through the tunnel, and brings the ball to Mia at the top of Odenplan's
  escalator.
- **Manner:** descend and ride. **The idea:** moving floors carry Pepper (escalators, walkways, a wagon), and she
  must time getting on and off.
- **Dog logic:** up and down only by escalators (both ways), hops, kiosks, machines and benches; no ladders. Every
  moving thing has someone who moves it: the station runs the escalators and walkways (an attendant in a booth),
  a passenger opens the gates, a traveller lets go of a suitcase, the cleaner drives the floor scrubber, the crew
  drives the wagon and opens the screen door.

## The idea, in four beats

| Beat | Where | What happens |
| --- | --- | --- |
| 1 Introduce, safely | row 1 to 2: escalator A (down, 40 px/s) | The ball bounces down ahead. At the hall's end Pepper hops down onto the moving steps; standing still, they carry her down under the hall to the passage. Walls on both sides, a flat floor at the bottom: nothing can hurt her. Walking up against them works too (she runs 120, they move 40). |
| 2 Practise | row 2: the long passage | Two moving walkways: the first runs with her (fast, bones on it), the second against her (slow going: run, or take the shelves above). The ticket gates: crawl under the flaps, follow a passenger through, or bark at the booth (the attendant opens the wide gate). Then the long escalator B (down, 56 px/s) with a suitcase sliding down it ("OOPS!", hop over it). |
| 3 Combine with an earlier mechanic | row 3: the platform | The screen door opens on a timer (River Walk's ferry: wait for it, then go); a bark asks the crew to open it now. Through it, onto the work wagon, where the ball is: River Walk's boats (ride a moving platform). |
| 4 Twist, then the fetch | row 3: the tunnel and Odenplan | The wagon drives into the tunnel: low signs hang over it, each warned by the wagon's orange lamp and the driver's "DUCK!": crouch (City Park's crawl) and they pass over her. The ball rolls along the deck when the wagon starts and stops: pick it up. At Odenplan the screen door opens; escalator C carries her UP to the exit hall: Mia. GOOD GIRL! |

## The routes

Feet lines: row 1 y 184, row 2 y 424, row 3 y 664.

**Main route (the low road).** Sergels torg (a bench to crawl under or hop on), the entrance, PRESSBYRÅN (a kiosk,
36 px, held jump), the booth and the ticket gates (x 1008-1040), the hall; at its end (x 1600) a hop down onto
escalator A, which turns back under the hall to the passage. Row 2 runs left: the walkway with her (x 1104-1360,
-80 px/s), the walkway against her (x 624-944, +60 px/s, with the floor scrubber), a flower tub, the second gates
(x 400-432), a bench; at the passage's end (x 160) a hop down onto escalator B, which turns back under it to the
platform. Row 3 runs right: the platform (a vending machine), the screen door (x 944-960), the wagon's ride
(x 960 to 2144), Odenplan's platform, escalator C up to the exit hall, Mia (x 2536, y 488).

**High routes (three short ones, where the rows are tall enough):**
- *Over the ticket hall* (row 1): the ticket machine (36 px), the banner over the gates (36 px), two light rails,
  the station CLOCK with **the golden bone** (y 80, 104 px over the floor: the hardest jumps of the level, gaps of
  48 at 16 to 32 px up), down to the hall's end. It skips the gates.
- *The blue cave's shelves* (row 2, the main high road): from the information pillar at the foot of escalator A,
  eight rock shelves and a vent duct (secret VENT DUCT, a jump and a scramble, 56 px) over both walkways, down to
  the flower tub. It skips the walkway against her and the scrubber, and has 9 bones for 8 on the floor.
- *The cave shelf over the platform* (row 3): from the vending machine over three shelves (secret CAVE SHELF),
  down by the screen door.

**Dropping off a high road lands on the low road:** every shelf is over the hall's floor, a walkway or the
platform; nothing is over the track bed (the screen doors keep her off it, and the tunnel's ceiling is y 600).

| Jump (plain, with Pepper's numbers) | Gap | Up | Needs |
| --- | --- | --- | --- |
| hall: floor -> ticket machine -> banner | 0, 8 | +36, +36 | held (proven: Downtown's kiosk 36) |
| banner -> rail -> clock (golden bone) -> rail | 48, 48, 48 | +16, +16, -24 | held (proven: citypark_tall limes, gap 48 at 16 up) |
| passage: floor -> pillar -> shelf | 0, 8 | +32, +40 | held |
| shelf -> shelf (x 7) | 48 | -16 to +16 | held |
| shelf -> vent duct (secret) | 48 | +56 | held and scramble (up to 58) |
| hall end -> escalator A; passage end -> escalator B | 0 | -63 (a drop) | walk off |
| platform: vending machine -> cave shelf -> shelf -> shelf | 48, 48, 48 | +24, +24, -24 | held |

## Lamps, secrets, the golden bone, the landmark

- **Lamps (8):** Sergels torg (400), after the gates (1184), the foot of escalator A (1408), before escalator B
  (480), the foot of escalator B (352), by the screen door (900, before the ride), Odenplan (2264); up high, a
  shelf over the walkway (1208, 336). Pressure, then a rest: the gates, then a lamp; the walkway against her and
  the scrubber, then a lamp; the suitcase, then a lamp; the ride, then Odenplan's lamp.
- **Secrets (3):** GOLDEN BONE (the clock over the ticket hall), VENT DUCT, CAVE SHELF.
- **The landmark:** Odenplan's big round station clock, lit, at the end of the tunnel (x 2264-2440). The far layer
  of row 3 shows it down the tunnel from Stockholm City's platform: a small glowing circle that grows during the
  ride. Row 1's far layer has the Kristallvertikal glass obelisk on Sergels torg, so the start says Stockholm.

## The new engine pieces (specs for the engine agent)

All numbers are px and seconds. Pepper's controller (`pepper.lua`) is not changed: each piece only adds a
velocity to her or moves her with a floor, as the lifts and the springy tops do. `check_pepper` must stay
UNCHANGED.

### 1. Escalators (`L.escalators`)

Fields: the rectangle `x0, x1, y0, y1` (its diagonal is the stairs: `slope = "/"` rises to the right, `"\\"` falls
to the right; always 45 degrees, so `x1 - x0 == y1 - y0`); `way` = `"down"` or `"up"` (where the steps carry
her); `belt` = speed along the stairs (px/s, default 40); `name`; `stopped` (true: it does not run).

- **Collision:** a sloped floor like a terrain slope cell, but bounded to its own rectangle in y as well as x
  (`world.lua` today takes any slope in a column and then ignores the terrain under it; an escalator must not do
  that, because the switchbacks put a floor above and below the same column). Add escalators to `world.slopes`
  with `y0, y1` and make `slopeAt(x, y)` pick only a slope whose band contains the feet (`y0 - 8 .. y1 + 8`).
  Its top is landed on from above (as a one-way: she may drop onto it); its underside is solid only at the top
  and bottom landings (a 4 px lip), so she can walk under the middle of a switchback.
- **Riding:** while she stands on it (her ground is the escalator), each step adds the belt to her position along
  the stairs: `dx = belt / sqrt(2) * sx`, `dy = belt / sqrt(2) * sy` per second, where `(sx, sy)` points the way it
  carries her. Her own walk / run is added on top (her `vx` is untouched): standing still she rides; walking with
  it she goes faster; running against a 40 px/s belt she climbs at 80 (run 120 - 40) along x, walking against it
  (60) she moves at 20, she can stand still against it only by walking. A jump keeps the belt's push for the
  take-off frame only (like a boat's deck: no extra momentum in the air).
- **Landings:** where the belt ends (the low end of a down escalator, the high end of an up one) the floor
  continues flat (the map's floor or a prop); stepping off is automatic. Crouched she rides too (she can duck a
  suitcase only by hopping).
- **The ball** rides it like Pepper (a resting ball is carried; a rolling ball rolls down it with the belt added).
- **Art and sound:** the steps scroll (8 px per step, at the belt's speed), a comb plate at each end, a balustrade
  in the back layer; a soft hum when on screen.
- **Checks:** standing still on A she goes from top to bottom in `340 / 40` = 8.5 s ±0.1; walking down she is
  faster; running up against it she reaches the top; she never sinks into it or floats over it (feet within 0.5 px
  of the line every frame); the floor above a switchback is still a floor; jumping from it lands where a jump on a
  terrain slope lands.

### 2. Moving walkways (`L.walkways`)

A flat escalator: the rectangle's top is the floor (4 px tall, solid), `belt` = vx in px/s (+ right). Standing on
it adds `belt` to her x each step (her `vx` untouched). Running with -80 she goes 200 px/s, against +60 she makes 60.
A resting ball rides it. Art: a rubber belt with grooves scrolling at `belt`, a handrail behind. Checks: the speed
with, against, standing; she walks off its end without a bump; a dropped ball rides to its end and rolls off.

### 3. Ticket gates (`L.gates`)

The rectangle is the gate's glass flaps, a solid box 64 px tall whose bottom is 18 px over the floor: crouched
(16 px) she crawls under, standing she cannot pass, and it is too tall to jump (46 + 12 scramble = 58 < 64).

- **Passengers:** one walks in from off screen every `every` s (default 7; greybox: a 14 x 36 box with a label;
  art: a commuter with a bag, kinds vary). As they reach the gate they tap a card (a beep, a green light), the flaps
  fold away for `open` s (default 1.5): the box is gone, Pepper can follow right behind. A passenger never hurts and
  never blocks (they walk through her, drawn behind).
- **The booth:** a bark with Pepper within 80 px of `booth` (x) makes the attendant wave, say `say` ("GO ON
  THROUGH, DOGGY!") and open the wide gate for `wide` s (default 4): the flaps fold away as above. While open: a
  green light on the gate, a beep when they close (1 s before: the light blinks).
- **Hints:** "CRAWL" (Down) at the gate's left, "BARK: ASK" (Y) near the booth.
- **Checks:** standing she is stopped; crouched she passes; the flaps open for a passenger every 7 s and for 1.5 s;
  a bark at the booth opens them for 4 s; a jump does not clear them.

### 4. Platform screen doors and the train's doors (`L.doors`)

A glass wall (solid) from the platform's floor to its ceiling, `x0..x1` 16 px wide. Cycle while a wagon (or train)
stands at it: **open** for `open` s (default 6), then **warn** for `warn` s (default 1.0: a two-tone chime, the red
light over the door blinks 4 times a second, the door edges glow), then **closed** for `shut` s (default 8, the
crew loads tools), and again. Opening: a single "ding", 0.6 s, then the panels slide apart (0.3 s; solid until
fully open). Closing: they slide shut in 0.3 s and never close on Pepper: if her box is in the doorway the panels
stop and wait open (as the lifts wait), and the warning repeats. `bark = true`: a bark within 80 px while closed
makes the crew open it now (from the next cycle start, 0.6 s ding first). `open = 0`: it opens only when the wagon
arrives (Odenplan) and stays open.

- **Timing for the level:** the door by the wagon opens 6 s, closes for 8 s. A child who misses it waits 8 s at
  most, or barks. Nothing is lost: the wagon does not leave until Pepper is on it (see 5).
- **Checks:** she cannot pass while closed; the warning comes 1.0 s before closing; it never closes on her; a bark
  opens it; the cycle times.

### 5. The ride: the work wagon (`L.wagon`)

The track crew's flat wagon (orange, a driver in a small cab at the front, an orange warning lamp on the cab's
roof). Its deck is a one-way floor `x0..x1` at `y0` (flush with the platform: 664), 96 px long, with end rails
`rails` px tall (48: no jump clears them) at both ends, so she cannot leave the deck during the ride.

- **Start:** it waits at the platform until Pepper's feet are on the deck and the door behind her has closed, then
  `wait` s (1.0: the driver says "ALL ABOARD!"), then accelerates at `accel` (90 px/s per second) to `speed`
  (90 px/s), drives from `from` to `to` (x of its left end) and brakes at the same rate to stop at Odenplan's door,
  which opens (ding). It never leaves without her; the ball alone on it does not start it.
- **Carrying:** like a lift (`lift.lua`): she and a resting ball move with the deck. **The ball rolls** when the
  wagon starts and stops: it is given `vx = -dv` (the change of the wagon's speed) and rolls on the deck until the
  rails stop it (a soft bump). So at the start it rolls to the back rail, at the stop to the front rail: "THE BALL
  ROLLED! GET IT!" Pepper picks it up on the deck (X) any time.
- **The tunnel signs (`L.signs`):** fixed boxes hanging from the tunnel's ceiling (y 600) down to 19 px over the
  deck. Each sign: when its left edge is within `warn` s of the wagon's front at the wagon's speed (1.2 s: about
  108 px), the cab's lamp blinks orange, a "DUCK!" bubble over the driver and a two-tone horn; the sign is lit by
  the wagon's headlight as it comes on screen. Crouched (16 px) she passes under it with 3 px to spare; standing
  (26 px) it touches her: she loses a heart, is pushed into a crouch (no knock-back: she stays on the deck) and is
  invulnerable for 2 s. A sign never touches the ball or the driver. Hint: Down "DUCK!" while the lamp blinks.
- **The camera during the ride:** it follows the wagon, not Pepper's lead: the wagon's middle at screen x 120 so
  the tunnel ahead shows 200 px (2.2 s at 90 px/s: every sign is on screen at least 1 s before its warning ends);
  vertical: fixed with the deck at screen y 168 (the platform snap), no looking up or down. It eases back to the
  usual camera in 0.5 s at Odenplan.
- **Spacing in the map:** five signs at x 1280, 1512, 1720, 1856, 2000: 2.6, 2.3, 1.5, 1.6 s apart at 90 px/s.
  The ride lasts 13.2 s from the start to the stop at Odenplan.
- **Hard mode:** `speed` 110, `warn` 1.0.
- **Checks:** the wagon waits for her and starts 1.0 s after the door closes; she rides it at 90 px/s; the end
  rails hold her (a jump does not clear them); each sign's warning starts 1.2 s ahead; crouched she passes all five,
  standing one costs a heart and she stays on the deck; the ball rolls to the back rail at the start and the front
  rail at the stop; the stop is at Odenplan's door and it opens; the camera keeps the wagon at screen x 120.

### 6. Things someone moves (`L.hazards`)

- **The suitcase** (`kind = "suitcase"`, 20 x 16, on escalator `on`): every `every` s (9) a traveller at the top
  says "OOPS!" with a "!" over them (`warn` 1.0 s), then the suitcase slides down the escalator at `speed` (110 px/s
  along the stairs, belt included) to the bottom, where the traveller's friend catches it (it vanishes behind them).
  Touching it costs a heart; a hop clears it (16 px). A bark at the traveller (within 90 px across and 60 px up or
  down) makes them hold on to it: no suitcase for 6 s.
- **The floor scrubber** (`kind = "scrubber"`, 32 x 20): the cleaner drives it to and fro along `path` (x 600 to
  960, over the walkway against her) at `speed` 50 px/s, beeping, with a yellow flashing light (its warning: always
  on, plus a louder beep when it turns towards her). Touching it costs a heart; a held jump clears it (20 px). A bark
  within 80 px: the cleaner stops for 4 s and waves her past.

### 7. Mia's call and the end

Mia waits at the top of escalator C (`L.girl`, y 488). The fetch is the usual one (X near her: GOOD GIRL!). Her
line at the start (a story line, the talk panel): "I'LL TAKE THE TRAIN TO ODENPLAN! MEET ME THERE!".

## What the paper map does not have yet

- Hints, the passengers' and travellers' start points, the crew's and cleaner's positions are in the specs above,
  not in the map; the engine agent adds them with the objects.
- The terrain under the escalators is drawn as rock steps (cells); in the game the escalator objects are the floor.

## Open questions for the owner

- **Riding outside a train.** For children 6 to 10 a dog riding on the outside of a train is a risky picture. The
  plan uses the track crew's slow flat wagon with a driver and end rails, not a passenger train. Alternative: the
  ride inside a carriage, ducking under swinging hand straps and hanging adverts (no tunnel signs). Which one?
- Should the ball go into a passenger train instead (doors on a timer for boarding, then a ride inside), with the
  work wagon cut?
- Midday target: the estimate (95 to 110 s) relies on the zig-zag; if it is short once built, the row 3 platform
  can grow by one screen without changing the shape.
