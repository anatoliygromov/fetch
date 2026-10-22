# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

## Branch `r6/lab`: the playtest lab, recovery v2, whole-game mode, DI v2 and the curve check (22 Oct)
Built on `round1`. The lab only (`riverwalk/playtest.lua`, `riverwalk/pt_bot.lua`, `tools/`); no game file changes,
it still hooks in only through main.lua's `--playtest` flag. Method: `docs/playtest/method.md`.
- **Recovery v2** (pt_bot.lua, playtest.lua, tools/pt_common.py, tools/run_playtest.py): the clean run now records a
  route map (where each autopilot step began: place, floor, mover, buttons, speed, and the world's sig: the ball, the
  magpie's perch, the fox's hideout, the cat; and the x range and lowest floor each step ran over). The persona runs
  get it (`--route`). A persona who leaves the route (more than 72 px beside it or 20 px below it for 0.3 s) fails
  there at once (`offroute`) instead of running on into the water; after any failure the bot settles, fetches a
  loose ball, chases the magpie if it sits where the clean run never saw it, else walks to the nearest step on her
  floor with the same sig and the autopilot goes on from there with the clean run's buttons; nothing on her floor:
  the lab moves her there and charges the walk (`lab_walks`). A step picked up out of sequence that errors counts as
  a stuck. Lost runs on the 22 Oct bot (5 seeds, every level): 127 of 320 (40%); with v2, see the baseline.
- **Whole-game mode** (tools/run_campaign.py, pt_bot.lua `--carry`): a persona plays an order as one playthrough.
  Lives and the tally score carry over as in the real flow; GAME OVER is TRY AGAIN (the level again, 3 lives, the
  score it started with). Controls found stay known for the rest of the playthrough (trying time paid once); a hint
  whose button glyph was on screen halves the trying time of a control not known yet. A level not cleared ends there
  and the playthrough goes on at the next level as LEVEL SELECT starts it. One JSON per level of each playthrough.
- **DI v2 and the acceptance test** (tools/check_curve.py): DI v2 takes the trying time out of the play minutes and
  the clear time and does not count the failure that taught a control; learning seconds are reported on their own;
  DI v1 stays beside it. `check_curve.py --order ...` runs whole-game mode for the eight personas and checks T1
  sawtooth (no level more than 8 DI points above the hardest of the next two; the second half at least as hard as
  the first, the last level at least as hard as the first; kids and parents), T2 no spot over 35% of a level's
  failures, T3 Elsa clears every level in 50% of her playthroughs, T4 under 5% lost runs; exit 0 when all pass.
- **The fox's sig** (pt_bot.lua): whether the fox was sniffed out at its hideout is part of the world sig, so a
  persona who missed the shed roof on Night Harbour goes back to sniff before she barks (it was picked up after the
  sniff, and the bark found no fox).
- **Baseline v2** (docs/playtest/baseline_v2_22oct.md, charts in /home/claude/out/r6-lab/): round1 as it is, three
  orders (current; new: River Walk first, Rooftops 4th; tall: the tall City Park and Downtown) in whole-game mode,
  8 personas x 10 seeds. No order passes; the tall order comes closest (only Downtown (tall) spikes; Elsa clears every
  level in 80% or more). City Park and Downtown are the spikes of the other two, and the last three levels are flat
  and easier than the middle in every order. Lost runs: 41% on 22 Oct, 2.3% now (Downtown 8.8%, City Park (tall)
  7.5%, City Park 5.6% still over 5%). check_pepper: PEPPER UNCHANGED; check_flow: 103 of 103; City Park --auto 44.2 s.

## Branch `r5/bugs`: visual and presentation bugs, scale to the dog (22 Oct)
Built on `round1`. The owner's report ("the bike is too small, the cars get cropped when they pass") and a sweep of
every level, the menus and the cards. The bug list with evidence: `docs/bugs_22oct.md`. Pepper's files are untouched.
- **River Walk's bikes are an adult's bike** (stage.lua, level/riverwalk.lua, maps/riverwalk.tmx and its export): the
  promenade cyclists now use the road cyclists' art (`road_cyclist1-2.png`, 73 x 75, true 1x pixels; the two riders
  take turns) instead of `cyclist1.png` (49 x 50, a child's bike: the wheels were 19 px, smaller than Pepper's
  27 px back). The wheels are now as tall as her back, the rider 1.27x Mia. The hit box follows the drawn bike from
  wheel to wheel: 70 x 28 (was 48 x 26); 28 px keeps the perches (tops y 152-154) safe. The bikes ride behind the
  obstacles on her line (a flower box hides their wheels), so the taller rider no longer rides through Pepper on a
  box. `tests.lua`'s bell timing reads the zone's hit box.
- **Road traffic is never sliced** (road.lua): cars and cyclists only come in and leave at a screen edge. Before, a
  car drove into the end of its stretch of road (where the promenade turns into the quay steps) and was cut in half
  there by the road's scissor, could pop out of the start of a stretch on screen, and was removed on screen when it
  passed the end. Now one is sent only when its stretch reaches far enough past the screen for it to cross at the
  camera's present speed; if Pepper then runs after it so that the end would come into view, it speeds up or drops
  behind; it is removed only once wholly off screen; a cut (respawn) clears the road. Cars drive both ways now (300-
  380 px/s, about 25-30 km/h; were 110-170) so traffic still passes while Pepper runs right; cyclists 190-240 px/s.
  `LOOK_CHECK=1` prints `ROAD CUT` if a vehicle ever meets a road end on screen: none in the autopilot.
  The `--test` tour's traffic shots mark their vehicles `still` (kept through the shot's camera cut, at their world
  x); the planter shot's car starts inside its stretch of road (x 2830; at 2790 it hung over the quay steps).
- **River Walk's far shore ran out** (scene.lua): the shore layer was built for the 3200 px level (1196 px wide); at
  3840 px the camera needs 1376 px, so over the last two screens the trees ended in a hard edge with bare sand-coloured
  sky beside them. The trees now go back and forth to 1600 px. The far skyline's range was fixed at 2880 px too, so
  it stood still over the last 640 px; it now uses the level's own width.
- **LEVEL SELECT fits five levels** (flow.lua): the rows were 46 px, made for three levels; with five, SODER HILL ran
  under the "A PLAY  B BACK" footer, NIGHT HARBOUR hung off the bottom of the panel and the screen, and the SOUND
  pill sat on its text. Rows are now 30 px (the panel 208 px tall), so all five and the footer fit inside it.
- **The bug list** (`docs/bugs_22oct.md`): 16 items, 7 fixed here; the rest need new art (the Downtown tram, its shed
  and stop are toy-sized next to Pepper; the leaf cart keeper and the winch man are Mia's height; doors, the duck
  boat, a treetop lantern) or an owner decision (near-lane cars framed off at the bottom). The art list with target
  sizes goes to the asset plan. Checks: `check_pepper` UNCHANGED, `check_pepper_files` identical, flow 103 of 103,
  `check_tiled` all PASS, `--physics` all levels as before (73, 70, 40, 23, 37, 40, 82, 88, 81), `--auto` 44.2, 51.6,
  66.3, 73.3, 81.3 s unchanged (the wider bike hit box changes no autopilot time), `--qa` 0 problems.

## Branch `r4/playtest`: the playtest lab, ported to today's levels, and the level order checked (22 Oct)
Built on `round1`. The lab from `ml/playtest` (6 Oct, never merged) rebuilt around the levels' own autopilots.
The game is untouched: `main.lua` gains one line (`--playtest`, only with `--auto`); no level, map, stage, world,
camera, lift, roof, critter, set piece, Pepper or art file changes.
- **The persona layer wraps the current autopilot** (`riverwalk/pt_bot.lua`, `playtest.lua`): `tests_<level>.lua
  --auto` still decides what to press from the real game state; the lab sits between its buttons (`I.force`,
  `love.keypressed`) and the game and adds reaction delays, early and late presses, hold errors, controls found by
  trying, failures, recovery (back up on foot or back to the lamp, then on along the route), patience and quits.
  Routes stay current by themselves; Rooftops' high road comes from the autopilot's own `AUTO_ROUTE=high`.
  `pt_json.lua` comes over unchanged; the old copied routes (`pt_routes.lua`) are gone.
- **Runs:** `tools/run_playtest.py` (all personas x levels x seeds, one LOVE process per run, each with its own
  `XDG_DATA_HOME`, `SDL_AUDIODRIVER=dummy`, `xvfb-run -a`). A run takes about a second (no drawing).
- **Analysis and method:** `tools/analyse_playtest.py` (per persona and level: clears, quits and where, hearts,
  lives, game overs, clear times, waits, bones, secrets, controls found, failures per beat-sheet screen; the
  difficulty index per group along each candidate order; charts and stall maps); `docs/playtest/method.md`
  rewritten for the new design (what is exact, what is modelled, the recovery model, lost runs).
- **The order report** (`docs/playtest/report_22oct.md`, `docs/playtest/summary_22oct.json`; 1,280 runs, 20 per
  persona per level): the proposed order is not progressive. River Walk is the easiest level for every group; City
  Park (either version) and Downtown are spikes. City Park and Downtown beat their tall versions as levels 1 and 3;
  the current order (Downtown 2nd) is smoother by the index. Top fixes: City Park's climbing frame, Downtown's cafe
  terrace, the tall City Park's first held jump, the magpie at the gate. Checks: `check_pepper` UNCHANGED, flow 103
  of 103, City Park `--auto` 44.2 s as before.

## Pepper's file check narrowed to what she uses (22 Oct, evening)
- `tools/check_pepper_files.sh` flagged world.lua: engine/round2 gave `Wd:groundAt` an optional `fromY` for carts,
  bikes and the gull on tall levels. Pepper never calls it. The check now proves the rest of world.lua (all her
  collision) byte-identical to aa38be5, with that one function left out, and fails if pepper.lua ever calls it.
  The trace check (`check_pepper.sh`) was identical all along.

## Branch `r3/citypark-art`: the tall City Park gets City Park's art, and a treetop tier dressed to match (22 Oct)
Built on `round1`. Scene and art only; no new generated art (no SpriteCook): the treetops use the approved park art
in `art/scene/` and pieces drawn in code. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The park art at any path height.** The art levels' fixed lines (the path at y 184, decoration's base at y 175,
  the pond's bank and water line, the bench, bin, oak, gate, swings, frame, willows, winch, the duck boat's water,
  Downtown's door, table, fountain, shelter, houses) are now placed from the level's path line: `L.foot` (default
  184; stage.lua sets `Sc.FOOT` before it draws, and scene.lua adds `dy() = FOOT - 184`). The painted path is
  clamped to `foot` (was 184), the pond's water runs to the bottom of the world, the hollow log's art shadow sits
  on its piece's `foot`. `look.lua`'s foreground band finds the flat ground at `foot` and stands on the world's
  bottom row (a flat level: screen y 240 as before). `tools/level_to_tiled.py` keeps a piece's `foot` drag-safe
  (`rely.foot`). Proof: the `--test` tours drawn on `round1` and on this branch, 147 of 153 shots pixel
  identical (River Walk 24 of 26, City Park 21 of 23, Downtown 30 of 31, Night 24 of 25, Soder Hill 22 of 22,
  lab_tall 13 of 13, Rooftops 13 of 13); the 6 others differ only in the debug view's FPS / MS counter
  (x 8-30, y 456-470 of the 640 x 480 shot).
- **The tall City Park has City Park's art.** `maps/citypark_tall.tmx` gets `art = "park"` and `foot = 328`, the
  hollow log's piece back (standing on the path: `rely.foot`) with its prop hidden as in City Park, and the title
  loses "(greybox)"; export regenerated, `tools/make_citypark_tall.py` makes the same (checked with `--force` into
  a scratch copy). On the path the camera rests at the bottom of the world, so the low road now looks as City Park
  does today. `--physics` 82 of 82 as before.
- **The treetop tier, dressed** (`scene.lua`: `Sc.drawTreetops`, called before the back props, and the tier's
  ledges in `Sc.drawPropArt`). Only existing art and code-drawn pieces; no box or test changed. The tier is
  found from the map: ledges 90 px or more over the path (`L.foot`), decoration 100 px or more over it; parts by
  name, an unnamed ledge belongs to the named ledge over it, else to the one before it in the map:
  - branches (the plane tree, the limes, the old oak's crown, twig and stub, the ash, the big oak's boughs): crisp
    and outlined like the old oak's branches: a bough lying across its trunk (thick over it, thin at the tips,
    leafy twigs at both tips), or a branch reaching out from the nearest trunk (`drawBranch`, as in City Park)
  - trunks: the narrow decoration boxes, drawn faded down to the path with flaring roots and bark furrows, up into
    their canopy; the big oak's 32 px trunk with knots. A canopy with no trunk near one end gets one there on dry
    ground (the alders on the creek's far bank): nothing floats
  - canopies: the crowns of `park_tree1`, `park_tree2` and `park_oak` (their trunks masked out, faded as
    decoration), overlapping over each crown box; the big oak's crown is oak crowns over two rows of trees, the old
    oak's top is one oak crown over its art
  - the treetop walk and the alder walk: a plank deck (crisp, outlined), a rope hand-rail on posts behind Pepper,
    timber legs with cross ties down to the path or into the water (seen through it, as the stepping stones are)
  - the rose arbour: white slats (crisp) with a rose along their front, each on two faded posts with a climbing rose
  - the play tower: yellow decks and grey posts, crisp, as the slide tower's art
  - the low bough over the alder walk: a thick crisp bough bending up into the leaves towards its trunk
  - the magpie's nest at the top of the big oak: dark twigs, not faded, a stray twig or two, so it reads from below
- **The sky goes on above the old horizon.** In a tall art level with the look on, the sky rises with the far city
  (factor 0.3, so the warm glow stays behind the skyline) and goes on 120 rows above its old top in five deeper
  blue bands (City Park's script: `above`; a script without them carries its top step on upwards), with a second,
  sparser row of high clouds (`L.cloudsHigh`). A flat level, or the look off, draws its sky as before.
- **Checks.** `tools/tiled/check_tiled.lua`'s drag check knows a piece's `foot` moves with it. The tall tour
  (`--test`) also shoots every screen on the low road (`ct_31`-`ct_39`) and up in the treetops (`ct_41`-`ct_49`).

## Branch `r3/bonus`: FETCH FRENZY, the golden bone bonus round (22 Oct)
Built on `round1`. Gameplay only, no new art, no SpriteCook. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The rule.** A level cleared with at least one of its golden bones found (`super` bones, `bone_gold` art; every
  level has two to four) opens FETCH FRENZY after the tally, before the story card (`Flow.bonusOpen`). No golden
  bone: tally, then the story card as before. Its points go into the tally's and the run's score.
- **The round** (`riverwalk/bonus.lua`). One screen of City Park lawn (City Park's own sky, skyline, tree line,
  near trees and path, drawn by `scene.lua`), 30 seconds. Mia stands on the left and throws every item with a
  throwing animation (her wave clip winds up for 0.36 s with the item in her hand, the cheer clip's open arms let
  go); nothing moves by itself. Balls bounce and roll, sticks spin and drop flat, frisbees glide down slowly.
  Pepper is the levels' Pepper (`pepper.lua`'s controller and numbers): she runs, hops, jumps, crawls; her body box
  catches. In the air: +100, on the lawn: +50, both count as catches; off the screen or 3 s lying still: lost.
  The stick and the frisbee are a few hand-placed pixels in code (12 x 3, 12 x 5); the ball is `art/ball.png`.
- **Three rounds**, so two levels in a row never play the same one: BALL RALLY (levels 1 and 4), STICK TIME (2 and
  5), FRISBEE FLOAT (3). Each starts with a short and a long ball to learn the arc; 14 or 15 throws.
- **Extra life at 11 catches** (`B.LIFE_AT`). Tuned with a model child set before tuning (reacts 0.45-0.9 s late,
  runs to a spot up to 50 px off, jumps up to 0.25 s off time, skips 40% of the jumps): 50% of 120 model rounds
  reach 11 (10 would be 84%). At most 9 lives. Best points saved in `bonus_best.txt`.
- **Screens.** Intro card (FETCH FRENZY!, the goal, PRESS ANY BUTTON), READY... GO!, three signs (catches against
  the goal, the time, points), the last 5 seconds big with a tick, TIME UP!, the result card (catches, in the air,
  points, EXTRA LIFE! or GOOD TRY), then the flow goes on. Cards never cover Pepper (she is drawn over them).
- **Hooks**: `main.lua` (state `bonus`, `--bonus`, `--level X --bonus`, `--bonus --physics`, `--bonus --auto`),
  `flow.lua` (`bonusOpen`, `bonusBest`), `hud.lua` (`U.bonusStatus`).
- **Checks**: `love riverwalk --bonus --physics` (`tests_bonus.lua`) 23 of 23: every throw lands on the lawn under
  the signs and before the time is up; every throw can be caught in the air by the real controller starting
  where the throw before landed (simulated, 44 of 44); Mia winds up before every throw; the timer ends the round;
  the extra life at 11, not 10; the points; the autopilot catches 13-14 of each round; the model child; the flow
  (golden bone: tally, bonus, story; none: tally, story). `--bonus --auto` records the autopilot (rec/).
- **The flow test reaches it** (`tools/check_flow.sh`, 103 of 103, was 94). Three small hooks in
  `tests_flow.lua` (marked `[bonus]`): run level 1 is cleared with a golden bone, so the bonus opens between its
  tally and its story card (no extra life, the points carry into level 2's score); level 2 checks there is no
  bonus without one; the clean clear at the end (every bone) plays it with the extra life before the ending.
  The cases themselves are `tests_bonus.flow`. Screens: `flow_b*.png` (run) and `flow_c*.png` (clean clear).

## Branch `r3/design`: the tall Downtown and the Metro plan (22 Oct)
Built on `round1`. Level design only: no engine files changed, no SpriteCook, music untouched.
- **Downtown, tall** (`downtown_tall`, greybox, not in `levels.lua`: `love riverwalk --level downtown_tall`). A
  Tiled map, `maps/downtown_tall.tmx` (440 x 60 cells, 3520 x 480 px, 11 x 2 screens), exported to
  `level/tiled/downtown_tall.lua`; `level/downtown_tall.lua` loads it. Its first version is drawn by
  `tools/make_downtown_tall.py` from Downtown (moved down 30 rows: the street is at y 424, and on the street the
  camera rests at the bottom of the world, so the low road looks as before), plus the high road over the roofs:
  a balcony from the bakery sign, the loggia over the statue (the cat can be barked off from there), the guild
  house's pitched roof (one-way steps 4 px high) with its chimney (the golden bone), the gallery over the fountain
  in two solid halves (the gap between them drops onto the fountain's top tier), six roof ledges over tram street
  and the flower market with a springy window awning, and the footbridge over the canal. Both roads meet before the
  flooded square. The trams have `roadY = 424`. 2 lamps up high, 27 more bones, the GOLDEN BONE secret (5 in all),
  the landmark (Riddarholmen church's spire over the river stairs). Greybox only: no `L.art` (the town art is
  drawn at y 184). Downtown's old balcony route stays as a middle tier under the roofs.
- **Checks** (`riverwalk/tests_downtown_tall.lua`): `--physics` 81 of 81: the world and camera, the trams on the
  street only (both zones: set off with the warning, hurt on the street, pass under the shelter, never come on the
  roofs), her 46 / 24 px measured, 47 jumps simulated with her own controller (the low road, the two ways up, the
  high road standing and running, the old balcony route under the new roofs), 4 jumps that must fail, the roof's
  steps and the chimney, 63 ways off the high road all land with no heart lost and never in the water, the solid
  walks over water, the cat from the loggia, bones, lamps, secrets, the fetch ends the level. `--auto` plays the
  high road with the ball: GOOD GIRL! in 56.9 s, no heart lost, 4 of 5 secrets. `--qa` 0 problems.
  `tools/check_tiled.sh` covers `downtown_tall` (LEVELS, MAPPED, its export up to date).
- **Paper map with routes:** `python3 tools/draw_routes.py downtown_tall <out.png>`.
- **`docs/downtown_tall_beatsheet.md`**: the four beats of bounce and carry, screen by screen on both roads, every
  jump with Pepper's numbers, the cat from above, timing (par 85 s), what the engine must add (the town art and the
  look at any height), open questions.
- **Metro, the paper map** (level 5 in the plan; not wired into the game): `docs/metro_beatsheet.md` and
  `maps/metro_sketch.tmx` (320 x 90 cells, 2560 x 720 px, drawn by `tools/make_metro_sketch.py`): Sergels torg and
  the ticket hall, the long passage, Stockholm City's platform, the tunnel and Odenplan, three rows in a zig-zag
  joined by switchback escalators. New kinds of objects in the map: `escalators`, `walkways`, `gates`, `doors`,
  `wagon`, `signs`, `hazards`. The beat sheet specifies them for the engine (moving steps riding and walking
  against them, walkways, ticket gates with passengers and the booth, screen doors with chime, light and timer,
  the work wagon's ride with ducking under warned tunnel signs and its camera, the suitcase and the floor
  scrubber), with the checks to write. `tools/draw_routes.py metro_sketch` draws escalators with arrows,
  walkways, gates, doors, the wagon's ride and the signs.

- **Checks on this branch:** `check_pepper` PEPPER UNCHANGED (4591 steps), `check_flow` 94 of 94, `check_tiled`
  passed (downtown_tall in LEVELS and MAPPED, its export up to date), Downtown `--physics` 70 of 70, downtown_tall
  `--physics` 81 of 81, citypark_tall `--physics` 82 of 82. Renders, the screenshot sheet and the autopilot GIF are
  in `/home/claude/out/r3-design/`.

## Branch `r3/rooftops`: Rooftops at full length, readable steam (22 Oct)
Built on `round1`. Level design, the rooftops' own code and checks; greybox, no SpriteCook. Pepper's files are
untouched (`check_pepper` UNCHANGED).
- **Rooftops, full length** (`tools/make_rooftops.py`, now standalone: it no longer starts from the paper map).
  12 x 5 screens, 3840 x 1200 px (was 6 x 4). The skyline climbs to the right in tiers: the street (1144), the
  bakery (T1 952), T1b (856), the market hall and the laundry (T2 760), the roof bar (T3 568), Mia's roof cafe (T4
  376), the copper roof (280), the nest chimney (184). The four beats of the steam puffs and loose tiles: the
  kitchen fan up a wall too tall to jump, with a flat roof under it, and the light well's three loose tiles with a
  fan in the well to climb out (introduce, safe); the market hall (a puff over the sweep's chimneys, the skylight's
  tiles), the laundry vent and the balcony's tiles between two puffs (practise); the roof garden's goose and the roof
  bar's gull and springy awning with puffs (combine); the sauna that only steams on a bark, at the nest (twist). The
  high road floats over it on ledges, 8 loose tiles and 4 puffs, with the golden bone on the bakery's chimney pot
  and the secret ROOF WALKWAY; it meets the low road on the copper roof. 14 vents, 17 loose tiles, 7 lamps, 76
  bones. Story: Mia takes the building's stairs up to the roof cafe; Pepper goes over the roofs.
- **Steam you can read on a light sky** (`roofs.lua`). The column is now cloud blobs with a crisp blue-grey outline,
  a shaded underside and a lit top (`Rf.blob`), still drawn behind Pepper. Every vent has a visible cap on a stem
  over its mouth: at rest grey, while it warns it turns orange, hops 1 to 3 px and rattles sideways, with small
  outlined wisps and dark specks leaking out and the "!" over it; during the puff it stands open. The landmark from
  below (`Rf.drawLandmark`): while the nest chimney is above the screen, a faded far copy of it (the nest, the gull
  circling, the sauna's thread of steam) stands at the top of the sky, sliding slower than the world, behind the
  roofs.
- **Checks** (`tests_rooftops.lua`): `--physics` 88 of 88 (every vent's apex, its landing with no input and when
  steering, the warning, the cycle, one lift per puff, crouching, a bark, the sauna; every vent runs; the loose
  tiles and all six bridges; every jump on both roads with Pepper's controller; the walls too tall to jump without a
  puff; 27 falls off the high road all land safely below; no bone in a solid; the nest; the fetch). `--auto`: the
  low road GOOD GIRL! in 54.1 s, no heart lost; `AUTO_ROUTE=high`: the high road in 51.8 s, both secrets.
  `--qa`: 12446 runs, 0 problems. The low road is about 6 s under the Morning chapter's 60 to 90 s; the beat sheet
  says how to close it (one more screen on T2).
- **Docs and tools:** `docs/rooftops_beatsheet.md` rewritten to match the build (tiers, beats, both roads, every
  jump, every puff, lamps, timing, open questions). `tools/draw_routes.py` has a `rooftops` entry (the routes on the
  new map). No engine file changed (stage, world, vcam, lift, critters, main untouched).

## Branch `engine/round2`: the review's engine fixes and the rooftops mechanics (22 Oct)
Built on `round1`. Engine only, greybox, no SpriteCook. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The lift never waits at her crouched height** (review, SHOULD FIX 2). A lift coming down over a crouched Pepper
  waited 16 px over her paws; when she let go of Down she stood up into the platform (pepper.lua's headroom test
  sees only solids). `lift.lua` now keeps her standing room (26 px) plus 2 px (`Lf.CLEAR`) clear over her whether
  she crouches or not, and a lift that is already lower than that over her (she crawled in under it) is wound back
  up by its operator until she has room. lab_tall `--physics`: 4 new checks (the review's case, crouched then
  standing; a lift too low over her backs up), 34 of 34.
- **Traffic and ground at any height** (the flat levels' y 184 made a level's field). A bike, cart or tram zone in
  `L.bikes` may give `roadY`, the feet line its road is at (default 184: every existing level is unchanged). The
  vehicle drives at `roadY` (and follows the terrain from 34 px above it, as the bikes did from y 150), the
  warning sign sits at its height, and a zone with `roadY` counts Pepper in only while her feet are on that road
  or up to `band` px (default 90) above it, so a cart on the low road says nothing to her up in the trees.
  `world:groundAt(x, fromY)` finds the highest terrain floor (slopes too) at or below any `fromY`; without
  `fromY` it is the old search (below y 150). In a tall world (more than 240 px) the cat's run, the gull's target
  floor (the floor right under her, ledges too) use it; the gull circles at its height on screen (camera y + 86),
  so it swoops to the floor it targets at any height. The kennel and the hollow log stand on `pc.foot` (default
  184). `qa.lua`'s bikes drive at their zone's `roadY`.
- **The leaf carts are back in the tall City Park.** `tools/make_citypark_tall.py` keeps City Park's two cart zones
  as zones (`roadY = 328`, the low road) with their hints ("CART! GET UP HIGH!", on the low road only), not on a
  `#carts` note layer; `maps/citypark_tall.tmx` and its export regenerated (`check_tiled` passes).
  `tests_citypark_tall.lua --physics` 82 of 82: 5 new cart checks (a cart sets off with its warning as she walks
  in on the path, drives at y 328, hurts her there, passes under her on the picnic table, never comes while she is
  on a treetop over the run). The autopilot (the high road) is unchanged: GOOD GIRL! in 38.5 s.
- **QA in tall levels** (review 5). `qa.lua` flagged "below the level" at 4 px under the world, while the fall rule
  (stage.lua) lets her drop 24 px out of the bottom before it takes her out of play: now 24 + 8 px. A QA run also
  clears a pending fall and puts the vertical camera on her when it places her. `--qa` on lab_tall: 4283 runs,
  0 problems (was 18 false ones); on citypark_tall: 11734 runs, 0 problems.
- **The lab pit can be fallen into** (review 4). It was 32 px: Pepper's feet span 26 px, she has coyote time and
  scrambles up 12 px, so she walked or scrambled across and the fall rule was only reached by tests. It is now
  96 px (x 160-256, `tools/make_lab_tall.py`): a running held jump clears it, a running tap hop only just makes it
  with a scramble at the far edge, walking off or running off the edge falls in (a heart, back to the lamp). The
  hint is "RUN, HOLD: BIG JUMP", the bone over it moved onto the jump's arc. For designers (docs/tiled.md is on
  another branch): a gap Pepper must not walk or scramble across is at least 64 px; a running held jump clears
  about 110 px (from her numbers, not measured). lab_tall `--physics` 40 of 40 (6 new pit checks, all played, no
  teleport), `--auto` GOOD GIRL! in 25.9 s, 13/13 bones, `--qa` 0 problems.
- **The ground in chunks** (review 8). The painted ground (terrain, pavement, path) was one canvas as big as the
  world (a 16 x 3 screen level: 15 to 20 MB of video memory, and wider or taller than the handheld's largest
  texture). It is now cut into canvases of 512 x 512 px (`Sc.CHUNK`, the last ones smaller), each drawn only when
  it is on screen, and a chunk with no terrain or water in it (the sky of a tall level) is not made at all
  (lab_tall: 3 chunks, 1.6 MB instead of 2.6 MB). Each chunk is painted by the same code moved to its origin
  (`clip()` is the scissor in world coordinates), drawing only its own columns; each column's terrain runs are
  worked out once per world and shared. Load time as before (Soder Hill 38 ms, City Park 47 ms here).
  `St.ground` is a `Sc.Ground` with `:draw(cam, camY)`, `:release()` and `:bytes()`. Proof: the `--test` tours
  drawn on `round1` and on this branch are pixel identical: River Walk 24 of 26 shots, City Park 21 of 23, Downtown
  28 of 31, Soder Hill 22 of 22; the others differ only in the debug view's FPS / MS counter
  (`/home/claude/out/engine-round2/debug_counter_diff.png`). lab_tall (its pit changed since round1) drawn with one
  big chunk and with 512 px chunks: 140 of 140 shots identical, across both chunk seams.
- **Steam puffs** (`riverwalk/roofs.lua`, data from Tiled: objects of class `steam`, the level's `L.steam`). Fields:
  `name`; the box `x0, x1, y0, y1` is the vent hood, a solid box (keep it 4 px tall so Pepper walks onto it; its
  top `y0` is the mouth); `lift` (px: the puff's apex is `y0 - lift`, exactly); `every` (s, the whole cycle; 0 =
  only on a bark); `warn` (s, default 0.8: the hood's flap rattles, a "!" over it, two wisps rise 8 px); `puff` (s,
  default 0.9: a semi-transparent column of steam up to `y0 - lift - 16`, 3 frames, behind Pepper); `phase` (s into
  the first rest, so neighbours do not puff together); `bark` (true: it never puffs by itself; a "?" shows over it);
  `say` (the line the first time a bark turns it up); `source` (who makes it: a note). Cycle: rest
  (`every - warn - puff`), warn, puff. A bark with Pepper within 80 px across and her feet within 60 px of `y0`
  starts the warning now. While it puffs, Pepper over the mouth (feet x within `x0 - 6 .. x1 + 6`, feet y within
  `y0 - lift .. y0 + 2`), not crouched, is launched once per puff: only her upward speed is set,
  `vy = -sqrt(2 * 560 * (y - apex))`, and her jump base moved so letting go of A does not cut the rise short (as
  the springy awnings' `bounce`); her controller is untouched. Steam never hurts; Down on the hood stays put.
- **Loose tiles** (props with `loose = true`, one-way ledges 24 x 6; Night Harbour's crumbling planks made general,
  for any level; Night's own planks are unchanged). The moment she stands on one it shakes (`Rf.SHAKE` = 0.6 s, 2 px
  every 0.1 s, a clink, grit), then it is no floor: it falls with gravity and breaks on the roof below (it only
  drops while she is on it, so it never falls on her); `Rf.GONE` = 3 s later it is back, once her box is out of its
  place (a faint outline 0.6 s before).
- **The gull's nest**: `L.magpie` with `look = "gull"` draws the magpie as a gull (`Cr.drawBird`); with one perch it
  stays put, a bark within `bark` px (95) across and 110 px up or down makes it let go of the ball.
- **Rooftops, playable greybox** (`rooftops`, not in `levels.lua`: `love riverwalk --level rooftops`).
  `tools/make_rooftops.py` turns the paper map into `maps/rooftops.tmx`, exported to `level/tiled/rooftops.lua`
  (`tools/check_tiled.sh` checks it is up to date); `level/rooftops.lua` loads it. From the sketch: hoods 4 px tall,
  each lift set so its apex is 16 px over the floor it serves (108, the oven's 140), phases, the oven's vent 8 px
  right on a 16 px longer chimney ledge (at x 1516 her body touched the chimney pot, which stopped the lift), the
  nest as the gull's perch, hints (PICK UP, GIVE, BARK!, the kitchen fan's "HOLD: STAY PUT"). The finale: the
  terrace fan lifts her through the copper roof; one bark there makes the gull drop the ball on the chimney and the
  sauna steam up; its puff carries her to the chimney's top; the ball; a step down onto the sauna's hood, Down + A to
  the terrace, the fetch. `tests_rooftops.lua`: `--physics` 42 of 42 (every vent's apex within 1 px, its landing
  with no input and when steering, the 0.8 s warning before a lift, the cycle, one lift per puff, crouching, a bark
  turns a vent up, the sauna only on a bark; a loose tile a floor for 0.6 s, back after 3 s and not while she is in
  its place, the bridge of three crossed with running tap hops; the cafe table (jump on, crawl under), the walk
  from the street to the terrace, the high road's plain jumps and the chimney pot's scramble, the step off the
  chimney, Down + A off the copper roof; the nest; the fetch ends the level). `--auto`: the low road and the
  finale, GOOD GIRL! in 21.8 s, 21/34 bones, no heart lost. `--qa`: 5509 runs, 0 problems. `--test`: a tour and
  frames of a puff and a loose tile.
- **For `docs/tiled.md`** (on another branch, not touched here): new fields to document are a zone's `roadY` and
  `band`, the `steam` objects and their properties, props with `loose = true`, `magpie.look = "gull"`, a piece's
  `foot`, and the minimum gap width (64 px). The loader (`tiled.lua`) needed no change: all of it passes through.

## Branch `polish/round2`: Tiled maps you can drag safely, and the guide brought up to date (22 Oct)
Built on `round1`. Tools and docs only: no engine, level or map files changed.
- **Drag-safe fields.** Positions that belong to an object (a boat's or lift's `from`, `to`, `fromY`, `toY`,
  `winch`, a ferry's `call` and `rope`, a goose's `x0` / `x1`, River Walk's picture anchor `ax` / `ay`, a kiosk's
  `bx0` / `bx1`, the kennel's `door`, a barrel's `trigger` and `rest`, a bike or tram zone's `endX` and `depot`) are
  now stored in the Tiled map as offsets from the object itself: `relx.<field>` (from its x), `rely.<field>` (from
  its y), `relxy.<field>` (points). `riverwalk/tiled.lua` adds the object's position back, so dragging an object
  in Tiled, or adding rows at the top of a map, moves everything that belongs to it. A hint with a height (`minY`,
  `maxY`) is now a box in the map instead of a band above it: its top edge is `minY`, its bottom edge `maxY`.
  Older maps and exports with plain numbers load exactly as before. (A bike zone's `minY` stays a plain number:
  the game does not use it.)
- **`tools/level_to_tiled.py --upgrade maps/*.tmx`** rewrites older maps with the drag-safe fields, in place,
  keeping notes, layers and object ids, and exports them; the levels the game loads stay the same. The maps on this
  branch are not upgraded yet (the engine branch is editing `citypark_tall.tmx`): run it once after merging.
  The converter also reads a level drawn only in Tiled (`citypark_tall`: its table and rows from its export).
- **`tools/check_tiled.sh`** now covers seven levels (the five, `lab_tall`, `citypark_tall`): the round trip (also
  through Tiled 1.8.2's own export) gives identical tables and rows; the committed maps upgraded in a scratch folder
  give the same levels; and every map, fresh and upgraded, dragged by (16, 80) with 10 rows added on top
  (`tools/tiled/move_map.py`) gives the same level with every position moved along. On the old maps that last
  check fails, as it should (night: 12 boat `from` / `to` left behind).
- **`tools/tiled/render_map.py`** reads the drag-safe fields too (a boat's path, a goose's stretch); the old and
  the upgraded Night Harbour map render to the same PNG.
- **`docs/tiled.md` brought up to date** (review item 9): which Tiled (1.8 or later, checks on 1.8.2, newer ones
  call Type "Class"), the numbers that move with their object, lifts (`rely.fromY`, `rely.toY`, `relxy.winch`,
  one-way, waits rather than squash), hints for one floor (a box: `minY`, `maxY`), barrels, tram depots, the
  smallest gap she falls into (64 px), tall levels (the camera, adding rows at the bottom or at the top and what
  moves with them), and a short "make a new level" walkthrough.

## The old title is back (22 Oct, evening)
- The hand-pixeled title (branch `title/redraw`) was rejected by the owner: the 19 Oct title has far more charm.
  Its merge is reverted on `round1`; the branch is kept for reference. The window is now called "FETCH!".

## Music out of the builds (22 Oct, evening)
- The owner takes music on separately, so builds have no music for now: the merge of `audio/music` (title and
  City Park tunes, jingles) is reverted on `round1`, and the old synthesised loop is switched off
  (`S.MUSIC = false` in sfx.lua). Sound effects are unchanged. The tunes stay on branch `audio/music`.

## Branch `design/round2`: the tall City Park and the Rooftops plan (22 Oct)
Built on `round1` (the height engine, Tiled, music). Level design only: no engine files changed, no SpriteCook.
- **City Park, tall** (`citypark_tall`, greybox, not in `levels.lua`: `love riverwalk --level citypark_tall`).
  A Tiled map, `maps/citypark_tall.tmx` (360 x 48 cells, 2880 x 384 px), exported to
  `level/tiled/citypark_tall.lua`; `level/citypark_tall.lua` loads it. Its first version is drawn by
  `tools/make_citypark_tall.py` from City Park (moved down 18 rows: the path is at y 328, and on the path the
  camera rests at the bottom of the world, so the low road looks as before) plus the new treetop tier: the plane
  tree and the treetop walk over the pond, seven lime trees, the old oak's crown and its top twig (the golden
  bone), the ash and the alder walk over the creek (a low bough to crawl under), the rose arbour, the play tower and
  the big oak, the magpie's nest at its top (its 12th and last perch; 3 new high perches on the way). 3 lamps up
  high, 30 more bones (the 3 on the willows went), 4 secrets (TREETOP WALK and GOLDEN BONE are new; WILLOWS went with the willow branches).
  Greybox only: no `L.art`, the hollow log a plain box, and the leaf carts wait on a note layer `#carts` (a cart
  zone starts only while Pepper's feet are above y 184 and the cart drives at y 184: the engine must read a
  zone's y first; see the beat sheet).
- **Checks** (`riverwalk/tests_citypark_tall.lua`): `--physics` 77 of 77: the world and camera, her 46 / 24 px
  measured, 40 jumps simulated with her own controller (the low road's climbs, the 3 ways up, every high-road
  jump standing and some running, the finale), 3 jumps that must fail, the crawl, 124 ways off the high road
  (walk off and run-jump off each end, Down + A through each one-way ledge) all land with no heart lost and never in
  the water, the two walks over water are solid, the magpie's 12 perches (where the ball lands after a bark),
  3 perches that ignore a bark from below, the nest perch stays put, bones (none in a solid, all within a jump),
  the fetch ends the level. `--auto` plays the high road and the finale: GOOD GIRL! in 38.5 s, no heart lost,
  2 of 4 secrets. `--test` a screenshot tour. `tools/check_tiled.sh` also checks its export is up to date.
- **`docs/citypark_tall_beatsheet.md`**: the four beats of the magpie idea, screen by screen on both roads, every
  jump with Pepper's numbers, the 12 perches, secrets and the golden bone, timing (par 75 s), what the engine must
  add (cart zones, the hollow log, the art and the look at any height), open questions.
- **Rooftops, the paper map** (level 3 in the plan; not wired into the game): `docs/rooftops_beatsheet.md` and
  `maps/rooftops_sketch.tmx` (240 x 120 cells, 1920 x 960 px, drawn by `tools/make_rooftops_sketch.py`): the street
  and the cafe, three stairwells, flat roofs T1 and T2, two pitched roofs, the roof terrace (Mia), the copper roof
  and the nest chimney (the landmark, top y 136). The main route takes the stairwells; the high route rides six
  steam puffs and five loose tiles, with the golden bone on a chimney pot. Two new kinds of objects in the map:
  `steam` (vents: lift, every, warn, puff, source, bark) and props with `loose = true`. The beat sheet specifies them
  for the engine: the steam puff (cycle, warning, the lift as `vy = -sqrt(2 * 560 * h)` with the bounce's jumpBase
  trick, one lift per puff, a bark starts a puff) and the loose tile (Night's crumble made general: 0.6 s shake,
  fall, back after 3 s), plus the gull's nest and the checks to write.
- **Paper maps with routes** (`tools/draw_routes.py <map>`): the map rendered by `render_map.py` with the main route
  (blue), the high route (orange), lamps, secrets, the golden bone, steam puffs with their lift, loose tiles and the
  landmark. Renders, the autopilot GIF and a screenshot tour are in `/home/claude/out/design-round2/`.
- **City Park tall, hints:** City Park's hints for one spot show only on the low road (`minY = 290`), so "STOP, THEN
  HOP" no longer shows on the alder walk.
- **Checks on this branch:** `check_pepper` PEPPER UNCHANGED (4591 steps), `check_flow` 94 of 94, `check_tiled`
  passed (and citypark_tall's export up to date), City Park `--physics` 73 of 73, citypark_tall `--physics` 77 of 77,
  its autopilot GOOD GIRL! in 38.5 s.

## Branch `engine/height`: levels that climb and drop (22 Oct)
Built on `main` (v0.5). The engine for the tall levels (rooftops, the building site, the metro); the five levels
play and draw exactly as before. Greybox, no SpriteCook credits.
- **Tall worlds.** A level map may have more than 30 rows: the world is rows x 8 px high (`world.height`). The
  ground canvases are as tall as the world. Everything that assumed 240 (a lost ball, the shadows' floor search,
  Soder Hill's hatch rule) uses the world's height, which is 240 in the five levels.
- **The vertical camera** (`riverwalk/vcam.lua`). `s.cam` is still the camera's x; `s.camY` is new (the world y at
  the top of the screen; always 0 in a world 240 px high). Standing, the camera settles so the floor she stands on
  is at screen y 168 (a "platform snap": eased, at most 300 px/s). In the air there is a dead zone (her feet between
  screen y 64 and 204): hops and jumps do not bob the screen. Falling more than 24 px below the floor she left, it
  leads down (her feet go to screen y 120). Up held while she stands still looks up 64 px, Down held while she is
  crouched and still looks down 64 px, after 0.5 s. What Up and Down do to Pepper is unchanged. `Vc.snap(s)` puts
  the camera on her at once (the start, a respawn; tests use it after moving her).
- **Drawing.** `St:draw` draws the world translated by `-camY` (the HUD, the talk panels and the foreground band
  stay screen space; the night's darkness stamps its light pools at their screen y, `night.lua`). The far layers move down slower than the world as the camera rises
  (sky 0.1, far city 0.3, mid trees / houses 0.6, from the bottom of the world), so climbing rises over the city;
  the sky's top colour fills in above. `Talk.pepperRect` and the cards' Pepper (main.lua) use her screen y.
- **Movers on both axes** (`riverwalk/lift.lua`): an `L.movers` entry with `fromY` (and `toY`) goes to and fro along
  the line from (`from`, `fromY`) to (`to`, `toY`) at `speed` px/s, resting `pause` s at each end. It is one-way (jump
  up through it, Down + A drops off), carries Pepper and a resting ball both ways, and never crushes her: if carrying
  her would push her into a solid, or the platform would come down (or slide) into her, it waits. `winch = { x, y }`
  draws its motor house with the operator who runs it. Movers without `fromY` are moved exactly as before.
- **Hints by height:** a hint in `L.hints` may have `minY` as well as `maxY` (her feet between them), so a tall
  level can say different things on different floors.
- **Falls.** Falling out of the bottom of the world costs a heart and goes back to the last lamp, as the water does
  (`fallT`; not on Soder Hill, whose hatches have their own rule). Landing on a lower floor costs nothing.
- **The test level `lab_tall`** (`level/lab_tall.lua`, `.map` from `tools/make_lab_tall.py`; not in the play order:
  `love riverwalk --level lab_tall`): 3 x 3 screens (960 x 720). The ground floor with a pit, stairs up, three 4 px
  steps, a scaffold of one-way planks, a beam with a 128 px drop onto F2, the goods lift up to the roof, 3 lamps, 13
  bones, Mia on the roof with the ball nearby: pick it up, give it to her.
- **Checks:** `riverwalk/tests_lab_tall.lua`: `--physics` (30 checks: the camera up the stairs, no bob on a jump,
  look up and down, the tall drop and the lead down, the lift up and down, waiting under a ceiling and over her head,
  the pit, the fetch, and the five flat levels at camera y 0), `--auto` (clears it: 25.9 s, 13/13 bones, no heart
  lost), `--test` (a screenshot tour, frames of looking up and down in `rec_lab_tall_look/`).
- **The five levels unchanged:** `check_pepper` (all three) UNCHANGED; `--physics` 73, 70, 40, 23, 37 of the same
  checks pass; the autopilots' runs are identical (44.2, 51.6, 66.3, 73.3, 81.3 s, same bones); `--qa` 0 problems
  with the same run and frame counts; `check_flow` 94 of 94. The `--test` tours of all five levels drawn on `main`
  and on this branch are pixel identical (120 of 127 shots; the other 7 differ only in the debug view's FPS counter).
  (Run the checks with their own `XDG_DATA_HOME` when other copies of the game run at the same time: they share the
  save folder, and `check_flow` fails when two runs write its files at once.)

## Branch `tools/tiled`: levels in Tiled, the map editor (22 Oct)
Built on `main` (v0.5). No SpriteCook credits. See `docs/tiled.md`.
- **Levels as Tiled maps** (`tools/level_to_tiled.py`): a level (`level/<name>.map` and `level/<name>.lua`) becomes
  `maps/<name>.tmx`, a map Tiled 1.8 and later opens: the terrain as a tile layer of 8 x 8 px cells (tileset
  `maps/terrain.png`: solid, water, two slopes, each tile carrying its map character), the rest as objects in the
  layers props, zones, movers, critters, lamps, bones and story, and the level's other fields (time, art, intro...)
  as map properties. Each map remembers its export target, so Tiled's File > Export (Ctrl+E) writes
  `riverwalk/level/tiled/<name>.lua`, the file the game reads; `--export` does the same without Tiled. The level
  table is read by running the level file in Lua (lua5.1, luajit or lua, else LOVE: `tools/tiled/love_runner`).
  All five levels converted.
- **The loader** (`riverwalk/tiled.lua`): `require("tiled").load("level/tiled/<name>.lua")` gives back the terrain
  rows and the table L the game uses today. It is generic: an object goes into the list named by its class (empty:
  the layer's name; "magpie.perches" is a nested list; start, ball, girl, cat, fox and exit are single objects), a
  rectangle gives x0, x1, y0, y1 (or the fields its "box" property names), a point x and y, a polyline its points,
  and every custom property passes through, so new kinds of objects (lifts, vertical movers) need no change. Any
  number of rows: a tall map just works. Text objects and layers named "#..." are notes. The terrain rows go to
  the save folder as `tiled_<name>.map` (as `pepperlab.lua` does) and L.map names that file: no change to
  `world.lua` or `stage.lua`.
- **The check** (`tools/check_tiled.sh`, `tools/tiled/check_tiled.lua`): all five levels go level files -> Tiled
  map -> export -> loader and come back identical (deep compare, lists in order, and every terrain row); the same
  through Tiled's own Lua export (`tiled --export-map`, Tiled 1.8.2 here); the game's exports are up to date with
  `maps/*.tmx`; a tall map (50 rows) with new kinds of objects loads; and which maps were changed in Tiled.
- **City Park loads from Tiled.** `level/citypark.lua` starts with `local USE_TILED = true` and returns the level
  from `level/tiled/citypark.lua`; the rest of the file (and `citypark.map`) stays as the fallback: set it to
  false to play the original. Its physics checks, autopilot (44.2 s, as before), QA and the flow test pass
  unchanged. The other four levels still load from their own files; switching one is the same two lines.
- **Zones with no height** (hints, bike and tram zones, gull stretches) are bands stacked above the map in Tiled,
  the first one on top, so they no longer cover the level. **A preview without Tiled:**
  `tools/tiled/render_map.py maps/<name>.tmx out.png --rows 3` draws a map layer by layer (terrain, props by kind,
  zones, movers with their paths, geese with their stretches, lamps, bones, the magpie's perches numbered, hints).
  The tools find LOVE and Tiled in `/Applications` on a Mac with no Lua installed.
- **`docs/tiled.md`**, a guide for drawing levels: the files, opening a map, the units and Pepper's limits (34 x 26
  px, 16 crouched; hop 24, held jump 46, scramble 58 px), what each layer and object means, adding a prop, a bone
  or a lamp, notes, exporting (Ctrl+E), running the game on a Mac, switching a level to Tiled and back, taller maps.

## Branch `assets/v2`: the tram fix and art for the new pieces (19 Oct)
Built on `levels/v2`.
- **The trams end in tram sheds** (Downtown). Before, the first tram vanished in plain view before the fountain,
  and the second drove on across the flooded square on its rails. Now each line ends in a tram shed (`TRAM SHED`,
  a solid prop) with its door on the right: a zone's `depot` is the door's x; the tram is drawn and hurts only
  right of it (a scissor), so it drives in and is gone. The shed roofs are perches: the first shed stands after
  the fountain (a hop from the rim), the second at the far side of the flooded square, where the last bounce
  lands. The second kiosk is gone; the first kiosk moved 12 px right, so the lamp between shed and kiosk has
  room for Pepper. New checks: tram 2 goes into its shed and never over the water; no bone in any level is
  inside a solid. The test tour shows a tram driving into each shed.
- **Art for the new pieces** (SpriteCook, 250 credits; `tools/build_critters_art.py`, sources in `source_sheets/` and
  `source_scenery/`): the goose (walk, rearing hiss with wings up, take-off and flight: 22 frames), the gull (6 flap
  frames), the rowing boat with its rower (8 rowing frames), the harbour jetty, and the tram shed (70 and 96 px
  wide). Still images were made at about 2-5x game size, reduced with a box filter, snapped to their own colours
  and outlined; the animations were made from those 1x images, so they keep the game's pixel scale. Each was
  pulled out of the browser as a false-colour picture and checked against a hash of its pixels (all exact).
  Code drawings stay as the fallback when a file is missing.
  - The goose's frame follows what it does: walking (by distance, so its feet don't slide), rearing up to hiss,
    flapping as it charges, standing, taking off and flying away when barked at. The "!" sits above its head.
  - The rowing boats' decks are 7 px lower (y 219: the hull sits in the water). The rower rows while the boat
    moves and sits at the end it rows towards, so Pepper, boarding at the other end, never hides him.
  - The gull swoops 2 px higher, so a crawling Pepper on the quay (3 px above a boat's deck) still ducks it.
  - `tools/check_pepper.sh`: the River Walk trace re-recorded (first difference step 2295, the lower decks);
    the lab and file checks are unchanged.

## Branch `level4/soder`: Level 4, Söder Hill, the chase (night of 18-19 Oct)
Built on `levels/v2` (c218a0e). Greybox, no SpriteCook credits. See `docs/soder_beatsheet.md`.
- **A new manner of play, Lion King's Stampede our way** (`riverwalk/chase.lua`, `L.scroll`): the screen moves on by
  itself (50 to 78 px/s by section) and the ball rolls ahead of Pepper down the hill, always on screen. The left
  edge pushes her along; pinned against something she didn't jump or crawl under costs a heart and sends her back
  to the last lamp. On the ground she can't run further than 240 px into the screen while the ball rolls, so the
  chase sets the pace (a jump still flies at full speed). Open cellar hatches are gaps in the street (a heart).
  The ball knocks a barrel off a stack twice: it rolls down the stairs slower than the chase; jump it (a heart on
  touch). At the bottom the ball stops against the quay railing, the scroll stops, and it is a normal fetch: pick
  it up, give it to Mia.
- **The level** (`level/soder.lua`, `level/soder.map` from `tools/make_soder.py`): 16 screens (5120 px), six stair
  flights from y 112 down to the quay at y 208, 7 hatches, 2 barrel stacks, crates, hanging signs and an awning
  and an arch to crawl under, bikes, cafe tables with parasols, a fruit cart, two balconies (gold bones, secrets
  CAFE BALCONY and HIGH STREET), 3 lamps, 45 bones. Time 200 s, par 118 s. Autopilot: 73.3 s, no hit (the other
  levels: 31.4, 29.8, 35.1 s).
- **Flow:** added to `levels.lua` as level 4. River Walk now has an outro leading into it ("UP ON SODER MIA DROPPED
  / THE BALL. IT ROLLED AWAY..."); Söder Hill's outro leads into Level 5 ("IT GOT DARK ON THE WAY / HOME. A FOX TOOK
  THE BALL!").
- **Hooks in `stage.lua`** (one line each, commented): `Ch.init` in `St.new`, `Ch.pre` at the start of `St:update`,
  `Ch.update` after the camera, `Ch.drawBack` and `Ch.draw`, and the rolling ball drawn like a resting one.
- **QA:** `qa.lua`'s fuzz no longer drops a bike into a level without bike zones (it crashed on Söder Hill); the
  random sequence for the other levels is unchanged.
- **Checks:** `riverwalk/tests_soder.lua`: `--physics` (23 checks), `--auto`, `--test` (a 16-screen screenshot
  tour). `--qa` 0 problems. `check_flow` 83/83, `check_pepper` (all three) UNCHANGED, the other levels' physics and
  autopilot unchanged.
## Branch `level5/night`: Level 5, Night Harbour (night of 18-19 Oct)
Built on `levels/v2` (c218a0e). The finale: sniff in the dark. Greybox, no SpriteCook credits. See
`docs/night_beatsheet.md`.
- **The level** (`level/night.lua`, `level/night.map` from `tools/make_night_map.py`): 14 screens (4480 px) along
  the harbour at night. A fox snatched the ball; Pepper sniffs out its three hideouts (a tarp, fish crates, under
  the low jetty), barks it on, picks up the ball it drops and brings it home to Mia at the front door ("HOME AT
  LAST."). Eight water gaps, two rowboats and four small boats (ping-pong movers), eight crumbling planks, a
  mooring post, a net shed to crawl under, a crate tower. 5 checkpoint lamps, 54 bones (3 gold), 2 secrets,
  time 420 s. Autopilot clear 81.3 s; par 135 s.
- **The night rules** (`night.lua`, new): the darkness (a canvas with dithered light pools from the lamps,
  lanterns, boat lights, windows, the porch and Pepper herself; moonlit edges on every floor and the water, so the
  path always reads), sniffing (hold L1 / R1 or Q: Pepper stops and sniffs, a trail of dots points at the hidden
  fox, the dropped ball or Mia, nearby bones glow), the fox (drawn in code; found by sniffing, chased on by a
  bark), crumbling planks (`crumble = true`: 0.5 s, then they fall, back after 3 s).
- **Hooks in `stage.lua`** (each marked `[night hook]`): create `s.night` for a dark level, skip Pepper's
  controller while she sniffs (her movement code is untouched: `check_pepper` UNCHANGED), the bark, the update,
  the fox's hint conditions, bones hidden in the dark, and three draw calls.
- **Controls** (`main.lua`): L1 / R1 now sniff (held); the Lion King look toggles with the L key only
  (`--classic` still starts with it off). `look.lua`'s header says so.
- **`levels.lua`**: the `night` line (number 5, par 135).
- **`qa.lua`**: the fuzz no longer throws bikes at a level without bike zones (it crashed on Night Harbour); the
  random sequence for the other levels is the same.
- **Tests** (`tests_night.lua`): `--physics` 37 checks, `--auto` the scripted clear (rec/ every 3rd frame),
  `--test` a 14-screen screenshot tour plus the fox, sniffing, planks and the tally. `--qa` 0 problems,
  `tools/check_flow.sh` 81 of 81 (unchanged), other levels' physics and autopilot unchanged.

## Branch `levels/v2`: QA, balance and two new levels (night of 18-19 Oct)
Built on `assets/complete`.
- **QA fixes** (an independent QA pass; probes dropped the ball at every x on every surface, 23,216 cases):
  - The ball could be lost forever (it flew out of the level at the edges, or slipped under stairs and the slide)
    or end up inside solid props (flower boxes, grit boxes, the bin, the pier, the stall, the pedestal) where Pepper
    could not pick it up. Now it drops at Pepper's own x when her mouth is inside a wall, never leaves the level
    (kept 14 px from the edges), stops at walls in flight, and any ball that rests out of reach (inside a solid, out
    of the level, or falling for over 2.5 s) goes back to its home spot. Every case now ends with a reachable ball.
  - Mia accepted a ball Pepper never brought (barking the magpie off its last perch while standing by her gave
    FETCH): she now takes a ball only where it lands next to her.
  - A ball resting on the duck boat or the pontoon rides with it (it hovered over the water when the boat left).
  - TIME UP while drowning cost a life and then a heart: the timer waits while Pepper is respawning.
  - The status signs step aside while Pepper is up under them (from the statue's hat, the shop sign, the oak top
    she was hidden behind the HUD).
  - River Walk: "FIND THE BALL ON THE BOAT!" only until Pepper has picked it up; then "GO BACK FOR THE BALL!".
  - Story cards also go on with Start / Enter (kids press it). The volume toast sits at the bottom over menus and
    cards. The old ground canvas (3 MB) is released when a level restarts. Stale comments fixed.
- **Critters** (`riverwalk/critters.lua`, `L.critters`; docs/progression.md): creatures with simple, readable rules.
  Every one warns first, and a bark is always a good answer.
  - Goose: walks to and fro. When Pepper is in front of it within 70 px it hisses (0.5 s, a "!"), then charges.
    Its bite costs a heart, then it struts off the other way (never two bites in a row). A bark within 80 px sends
    it flapping off for good (+200, "SHOO!"). It is 20 px tall: a held jump clears it.
  - Gull (used in River Walk): circles high, squawks and shows its shadow where Pepper is, then swoops down to her
    head height. Crawling ducks under it; a bark while it squawks scares it off for 4 s.
  - `bounce = h` on a prop (used in Downtown): landing on it launches Pepper h px up. Only her upward speed is set,
    so Pepper's own movement is untouched.
  - Hooks in `stage.lua`, one line each: `Cr.init`, `Cr.update`, `Cr.bark`, `Cr.bounce`, `Cr.draw`, and the
    "BARK: SHOO!" hint (`need = "goose"`, only for a goose ahead of Pepper). Two new sounds: hiss, squawk.
- **Level 1, City Park: sneak and bark, 6 to 9 screens** (2880 px; `tools/shift_level.py` opened the gaps and moved
  every x, map column and test literal after them):
  - New screen 4, the goose lawn: a leaf pile with bones, the first goose, and a log (a magpie perch).
  - New screen 7, the creek: three small stepping stones over deep water, 56 px apart. Running across fails (she
    drops past her scramble reach); a jump from standing carries her one stone. Hint: "STOP, THEN HOP". A second
    goose waits on the far bank and hisses as she lands.
  - New screen 8, the rose walk: a second leaf cart run (carts a little faster, every 5.5 s): wait on the bench,
    then the picnic table. A magpie perch on the bench's backrest.
  - 9 magpie perches (was 6), 68 bones, 8 lamps. Autopilot clear 44 s, no hit (was 31 s).
  - QA: lamps moved off the log and the picnic table (a respawn stood inside them); `qa.lua`'s bike sweep tests
    crouch-only spots (under a bench) crouched only. Flow checks use x 1900 for the magpie line.
- **Level 2, Downtown: bounce and carry, 6 to 11 screens** (3520 px):
  - New screen 4, the bakery row: a springy awning launches Pepper over a crate wall 64 px high (more than a jump
    and a scramble); a springier one reaches the bakery sign (gold bone, secret BAKERY SIGN). Holding Down she can
    stand on a springy top. Springy tops have red coil springs on their posts and dip as they launch her.
  - New screen 8, the flower market: two geese on the cobbles. A bite knocks the ball out of Pepper's mouth. Bark
    them off, or go high: the tub, the cafe table, the springy parasol, the balcony.
  - New screen 9, the canal: the awning at the water's edge launches Pepper over it onto a crate wall on the far
    quay. Walking in costs a heart.
  - New screen 10, the flooded square: three springy parasols standing in the water, 88 px apart. From a crate
    at the edge, a held jump onto the first; holding Right she bounces from one to the next and lands on the
    kiosk across the water (our version of Lion King's hippo and rhino bounces). From the street a jump can't
    reach a parasol.
  - New screen 11, tram street again: a faster tram (130 px/s, every 4 s; the first one 110 px/s, every 6 s), so
    Pepper waits for two: on the kiosk, then on the shelter roof. Its zone ends at the shelter, so Mia's spot is
    safe once she is down.
  - `L.ballHomeAtLamps`: a lamp Pepper reaches while carrying the ball becomes its home, so a ball lost in the
    canal comes back by that lamp ("THE BALL IS BACK BY THE LAMP"), not five screens back at the statue.
  - 6 lamps for 11 screens (was 5 for 6), 75 bones, 4 secrets. Autopilot clear 51.5 s, no hit (was 29.8 s);
    hard mode clears too.
- **Level 3, River Walk: water and traffic, 10 to 12 screens** (3840 px):
  - New screens 8 and 9, the harbour, on the quay's level after the bridge: open water with two rowing boats
    (movers with `pause`: a rower in each rows to and fro and rests 1.5 s at each end; drawn in code in
    `setpieces.lua`) and a wooden jetty on piles between them. Hop on, ride, jump onto the jetty, wait for the
    next boat. A gull circles over the water: it squawks and shows its shadow, then swoops at a standing Pepper.
    Crawl to duck ("DUCK!"), or bark while it squawks. Gold high over the jetty (secret JETTY JUMP).
  - Bike zone 2 also has a gull. Bikes a little faster: zone 1 125 px/s every 5.5 s (was 115, 6.5), zone 2
    135 px/s every 5 s (was 115, 6).
  - 5 lamps for 12 screens (was 8 for 10). `L.ballHomeAtLamps` here too.
  - Autopilot clear 66.3 s, no hit (was 35.1 s); hard mode clears too.
  - `tools/check_pepper.sh`: the golden trace re-recorded (the first difference is step 1658, the autopilot
    stopping at the quay to wait for a boat). Pepper herself is unchanged: the lab check (1401 steps) and the
    file check against aa38be5 still pass.
- **Pars** (`levels.lua`, the autopilot's time times about 1.6): City Park 71 s (was 60), Downtown 83 s (was 55),
  River Walk 107 s (was 60). `docs/progression.md` has the measured table: the levels now get longer and harder
  from 1 to 5 (autopilot 44, 52, 66, 73, 81 s).
- **Fixes from an independent review** (a fresh agent played and probed the new sections):
  - Softlock: a lost ball's home by a lamp could be inside a solid (City Park's bin lamp, Downtown's lamp by the
    flooded square's crate), and the ball looped "THE BALL IS BACK" forever. Homes now come from `St:homeNear`
    (24 px past the lamp, 24 px before, or the respawn spot itself, the first that is clear), and a home that
    is still no good falls back to the checkpoint. New checks: every City Park lamp's home is clear; a ball lost
    in the flooded square rests by the lamp, pickable.
  - City Park: the lamp after the creek is now on the far bank (2300), and that goose patrols 2350-2372: a
    respawn no longer lands between a goose and the cart run.
  - "BARK: SHOO!" shows only when a bark would work (80 px, the same as the bark).
  - Gulls: the warning shadow sits on the floor under Pepper even when she is mid-jump (or on the boat under
    her), and is wider than her so it shows; the gull circles below the hint panel and the HUD; a bark resets
    its timer (it came straight back before). River Walk's harbour gull swoops every 4.5 s (was 3.2) and the
    second boat rows faster, so the wait on the jetty is shorter; the second gull is over promenade B before
    the bike zone, not over the bikes.
  - Downtown: "HOLD: STAY ON" (Down) shows above the first springy awning. A springy top's dip counts down by
    time, not frames. The test tour's shots of screens 8-11 now have Pepper on screen.
  - The River Walk golden trace re-recorded again (the harbour timing changed); lab and file checks unchanged.
- **Readability:** the goose is redrawn taller (a long neck when walking; neck stretched out low, beak open and a
  wing up when it hisses), so it reads as a goose, not a duck; its hit box is unchanged. The rower is bigger (red
  cap, face, coat) and leans into each stroke; the oars have a dark outline. Gulls circle a little lower (y 86),
  clear of the hint panel.

## Branch `assets/complete`: the missing assets (18 Oct)
Built on `lk/look` (9c3bcbd). Every placeholder left in the three levels gets real art.
- **The Downtown cat** (`art/cat.png`, `tools/build_cat.py`, `Sc.cat`): modelled on the user's Abyssinian (ruddy
  ticked coat, very large ears, green eyes, pale chin). A hand-pixeled 30 px sitting cat (`source_sheets/
  cat_sit_source.png`, SpriteCook asset 3a0c5b07) animated in SpriteCook (pixel-engine-v1.5, 3 clips, 78 credits):
  idle (tail curl, ear twitch, blink), startle and leap, gallop. Cleaned like Pepper's clips (the animator's grey
  matte removed, 10-colour palette, specks, 1 px outline). It sits on the ball facing Pepper, crouches and arches
  its back when scared, leaps and gallops off. The greybox cat (`Sc.catGrey`) stays for greybox levels.
- **The park keeper pushes the leaf cart** (`art/scene/park_keeper_cart.png`, `tools/build_keeper.py`): City
  Park's cart hazard no longer drives by itself. An older keeper (flat cap, grey beard, green work jacket), styled on
  the River Walk cyclist with the old cart as reference (SpriteCook 14e58436, 36 credits for 3 options) and given an
  8-frame walk cycle (26 credits). Drawn mirrored (the barrow leads, right to left), the barrow's middle on the
  48 x 26 hit box, wheel and boots on the line; the stride follows the distance covered so the boots don't slide.
  Hit box, speed and timing unchanged.
- **A second keeper turns the duck boat's winch** (`art/scene/park_keeper_winch.png`): the rope ferry no longer
  moves by itself. A keeper in the same uniform (grey beanie, ponytail) at a post winch with a rope drum (SpriteCook
  0a12ae1a, 36 credits for 3 options; crank loop 26 credits), drawn mirrored so the winch faces the pond, in place of
  the small `park_winch` drawing. She cranks (10 fps) only while the boat is moving (`Sc.winchFrame`, set in
  St:draw from the rope ferries' `dx`), else she holds the handle.
- **Front-on picnic table** (`art/scene/park_table_front.png`, `tools/make_table_front.py`): the three-quarter
  table becomes the long side seen at Pepper's height: the tabletop's front edge with a thin cap (the top she stands
  on, y 156), the leg posts and the near bench, in the table's own colours, outlined. Same 72 x 28 box.
- **River Walk's code-drawn pieces get art** (`tools/make_riverwalk_pieces.py`, drawn by setpieces.lua at the old
  sizes, the code boxes stay as a fallback): Pepper's kennel in falu red with white corner trim, a flat roof of dark
  boards and a bone sign over the doorway she crawls into (`kennel.png`, 34 x 36); the two kiosks, KAFFE with cups
  and GLASS with ice cream cones, panelled green fronts and a lit window (decoration, faded at load); their awnings
  with a lit top, shaded underside and scalloped hem (`awning_88.png`, `awning_80.png`, outlined obstacles).
- Checks on the branch: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, the autopilot clears all
  three, PEPPER UNCHANGED (trace 2717 steps, lab 1401 steps, files).
- SpriteCook credits for this branch: 238 (1,974 before, 1,736 left).
- **A proper magpie** (`Sc.magpie`): the 14 x 10 placeholder becomes a 24 px magpie pixeled at game size (black
  head and breast, white belly and shoulder patch, long blue-green tail): perched, a tail flick, and two flight
  poses (wings up with white primaries, wings down). The ball hangs at its new beak (`St:beak`). Its perches,
  ranges and behaviour are unchanged (City Park physics 64/64, QA 0 problems).

## Branch `lk/look`, part 2: City Park and Downtown (12 Oct)
- **A colour script per level** (`Look.scripts` in look.lua), as Lion King gives every level its own light:
  River Walk a summer morning (as before), **City Park a golden autumn afternoon** (blue-violet sky to an amber
  horizon, the skyline dusty lilac, the far tree line and near trees hazed warm), **Downtown a bright midday**
  (deep blue sky to a pale horizon, the roofs and facades hazed cool so the street stands out). The art levels' sky,
  clouds, skyline, far and near layers, pond/basin, props and ground go through the same split-tone shader;
  Pepper, Mia, the ball, the bones, the cat and the magpie do not.
- **No foreground band in City Park and Downtown:** their bottom band (the earth, the quay wall) is already dark,
  and dark shapes on it did not read. The foreground now finds the flat ground at Pepper's line itself (River Walk's
  clumps are the same as before), and a script can also use chain fences.
- **More front-on props** (`tools/make_front_view.py`, collision boxes and sizes unchanged, originals kept):
  - `town_crate_front`: the slanted rim corners removed, the apples heaped behind the straight front edge.
  - `town_table_front`: the round top seen from above becomes a 5-row slab at the same top row; the legs reach it.
  - `park_boat_front`: the duck boat's floor and seats no longer show; the near side of the hull rises to the deck
    line Pepper stands on, with the far side's inside as a pale band above it.
- Not changed, for the user to decide: the picnic table (drawn three-quarter, needs a redraw), the hollow log (both
  open ends show, which a side view cannot, but they tell you it can be crawled through). The stone posts, the
  market stall and the log read fine front-on.
- `--lookshots` works on every level (`--level citypark|downtown`).
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three with no
  foreground overlap, PEPPER UNCHANGED (trace, lab and files).

## Branch `lk/look`: the Lion King look (12 Oct)
Built on `fix/console` (8e28369). River Walk only; City Park and Downtown are unchanged. L (keyboard) or L1 / R1
(handheld) switches the look off and on to compare; `--classic` starts with it off. Code in `riverwalk/look.lua`.
- **Colour script:** one key light for the level (summer morning) and a haze colour per distance, instead of one cool
  grey haze for everything.
- **Split toning per layer (a shader, art files untouched):** light colours lean warm, dark ones lean blue-violet,
  colours a little richer. The further back a layer is, the more it turns into its haze: the skyline lavender against
  a warm horizon, the far shore blue-green, the water deeper. Each colour in maps to one colour out. Pepper, Mia, the
  ball, the bones, the warning signs and the HUD are drawn without it.
- **Sky:** 10 painted bands from deep blue to warm cream at the horizon, joined by 3 rows of 2 x 2 ordered dither.
- **The road recedes:** the road rows scroll 1x at the kerb to 1.3x at the bottom of the screen, in 5 bands chosen so
  the lane markings, manhole covers and drains never shear. Near-lane cars and cyclists slide with their row (only the
  camera movement since they appeared counts, so they still drive in from the edge). The pavement Pepper walks on
  stays at 1x.
- **Foreground band:** dark, back-lit grass verges with shrubs and pairs of bollards, 1.4x, only in front of the road.
  Tops at y 218 (y 206 deep inside a stretch of road, where Pepper only walks at y 184). Never over Pepper: checked on
  every frame of the autopilot run with `LOOK_CHECK=1` (0 overlaps).
- **Front-on boxes (user note: the flower box and the grit box were drawn from above, unlike the bench, bin and square
  planter):** `tools/make_front_view.py` makes `flowerbox_front.png` (the slanted rim and the soil removed, the flowers
  on a bed of leaves behind the rim's straight front edge) and `gritbox_front.png` (front face only, the lid a thin
  band, the side face dropped, plain plank columns repeated to keep the 88 px width; 32 rows, so its top is the
  collision top). Collision boxes unchanged. The originals are kept.
- `--lookshots`: before / after shots of the 10 screens without HUD (tests_look.lua).
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three,
  PEPPER UNCHANGED (trace, lab and files); Pepper's pixels identical with the look on and off.

## Branch `fix/console`: after the first RG35XX test (7 Oct)
Built on `preview/art` (884b87e).
- **Sound volume on the handheld:** the game has its own volume (0 = off to 10), saved in `settings.txt`.
  - The volume buttons work in the game if the firmware passes them on as the keys `volumeup` / `volumedown` / `mute`;
    a small SOUND bar shows for 1.6 s. They never count as "any button" on the title or the cards.
  - The pause has a SOUND row: left / right (d-pad or stick) turn it down or up, A steps it up and wraps round to OFF.
    This works whatever the firmware does with the volume buttons.
  - Select only toggles the debug view with `--dev` or a test flag (it showed by accident on the handheld).
  - Every key and button press is printed as `[input] ...` (and joysticks when they connect). PortMaster's launcher
    keeps the output in `ports/fetch/log.txt`, so the next console test shows what the volume buttons really send.
- **Rolling wheels:** the promenade bikes and the road's cyclists turn their wheels as they ride. `tools/make_wheels.py`
  clears each wheel's inside (the old spoke pattern never moved) and redraws a hub and spokes (8 on the small bikes,
  12 on the road's) in 4 steps, keeping legs, shoes and the frame's light tubes in front; output `*_roll.png` next to
  the still art. `Rd.drawBike` picks the step from the distance ridden (wheel radius x spoke gap / 4 per step), so the
  wheels turn at the bike's real speed, forwards in both directions. Riders' legs still do not pedal.
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three,
  PEPPER UNCHANGED (trace, lab and files).

## Branch `ml/ui`: talk panel, nudges, medals, shared play
Built on `ml/fixes` (dad26c3), from the synthetic playtest: kids could not read the long hints and got stuck.
- **Talk panel (talk.lua):** the text banner hints are now short dialogue lines. Pepper (bottom left) says the
  control hints as a drawn button picture plus 1 to 3 words: [B] HOLD: SNEAK, [DOWN] CRAWL, [Y] BARK!, [X] PICK UP,
  [X] GIVE, [A] HOLD: BIG JUMP, [A] HOLD + PUSH: CLIMB, [A] TAP: HOP. The girl (bottom right) says the goal and story
  lines (BRING ME THE BALL!, IT DROPPED THE BALL!). The portraits play their talking loops at 9 fps while the line
  is said, then rest on frame 1. The buttons are drawn in code (RG35XX: A right, B bottom, X top, Y left; the d-pad
  for Down). The panel never covers Pepper: when she is low (the quay, the duck boat) it moves to the top of the
  screen, or is not drawn. Teaching hints win over other messages; a girl's zone line goes away after 4.5 s.
- **Hints that never showed:** the log hop (the magpie hint always matched first: now sneak while running at the
  magpie, the hop once she sneaks, BARK! in range), the magpie line (it started at x 1560, where nobody still lacked
  the ball: now from x 300) and GO BACK: BARK AT THE CAT (it now starts where a bark stops reaching the cat). The
  City Park climb hint starts at x 900. New hint needs: `catnear`, `magpienear`, `magpieahead`.
- **Stuck nudge:** 2 s pushing without getting anywhere, or 3 s idle where a control hint applies: the needed
  button bounces above Pepper's head (Down if she fits through crouching, else A, when no hint applies) until a
  button is pressed. It only reads Pepper's position, speed and the buttons.
- **Tally:** clear time, best time per level (`time_<name>.txt`), medals NO HIT, ALL BONES, PAR TIME (par in
  levels.lua: 60, 55, 60 s), kept in `medals_<name>.txt` and shown on the level select. SECRETS n/m when the stage
  reports `secrets` and `secretsTotal`. The tally sits where it misses Pepper.
- **Shared play:** GAME OVER offers TRY AGAIN (the same level, 3 lives, the score it started with) or MENU. Story
  cards wait 2 s, then only A goes on (a blinking A shows). The pause has GO ON and QUIT, and QUIT asks (NO first);
  B and Esc only go back, never quit. Cards move to miss Pepper, and she is drawn again over the dim.
- **HARD MODE:** a main menu item, saved in `hard.txt`, passed to the stage as `carry.hard` (`self.hard`). A HARD tag
  on the HUD, tally and level select; no hints and no nudges. (The gameplay side is on the sibling branch.)
- Flow test: 67 checks (was 32). Physics 17/40/45, QA 0 problems on all three levels.
- Pepper is unchanged: `tools/check_pepper.sh` still finds all 2,752 steps identical.

## Branch `ml/levels`: kinder spots, no waiting, traffic warnings, secrets, hard mode (level side)
Built on `ml/fixes` (dad26c3), from the persona playtest (kids quit at a few spots and waited too long). The hint
UI, the tally drawing and the menu are on a sibling branch; this branch gives them `stats().secrets`,
`stats().secretsTotal` and `self.hard`.
- **Pepper is frozen, and proven so without a level:**
  - `love riverwalk --pepperlab` builds a small test room in code (28 and 56 px blocks, a low bar, a one-way
    ledge, a moving deck, a water pit, stairs) and plays a fixed 1,401-step script (stand, walk, run, tap and
    held jumps with scrambles, falls and landings, crawl, skid, turn, bark, pick up, up and down through the
    ledge, a ride, a jump over the pit, stairs, a walk into the water), printing her state every step.
    `tools/check_pepper_lab.sh` compares it with `tools/pepper_lab_golden.txt` (recorded before any other change):
    PEPPER UNCHANGED.
  - `tools/check_pepper_files.sh`: pepper.lua, pepper_frames.lua, art/pepper.png, input.lua and world.lua are
    byte-identical to aa38be5.
  - `tools/pepper_golden_trace.txt` (River Walk on autopilot) was recorded again because the level changed: the
    first 459 steps are identical; at step 460 the autopilot, standing on the bin, jumps for the new kiosk awning
    instead of running off the bin. 2,717 steps now (2,752 before).
- **Engine (`setpieces.lua`, called from small hooks in `stage.lua`):**
  - Hard mode: `St.new(def, { hard = true })` (or `--hard` for the checks): 1 heart (also after a lost life),
    bikes, the leaf cart and the tram 25% faster.
  - Rope ferries (a mover with `call`): they wait at their far end, are winched to the near end when Pepper comes
    near and wait there for her, and carry her across when she stands on them. Their rope is drawn.
  - Traffic: a bike, cart or tram is sent so that its front reaches the screen edge 1 s later; its bell rings
    then (new `ding` for the tram, made in code like the other sounds), and a small warning sign (13x13 yellow
    diamond with "!" and an arrow) shows at the right edge at the lane's height until it is on screen, above
    Pepper's head if she stands there. The old gold bars are gone. `start = "enter"`: a zone sends its first
    vehicle as soon as Pepper walks in.
  - Secrets (`L.secrets`): reaching one plays a jingle (`secret`) and says "SECRET! NAME n/N"; `stats()` returns
    `secrets` and `secretsTotal`.
  - Code-drawn pieces (`L.pieces`): Pepper's kennel, the kiosks and their awnings, the hollow log. Their
    collision is an ordinary hidden prop with the same box.
  - The magpie can have a calmer perch (`flee` per perch).
- **City Park:** the first magpie perch flees a running Pepper only at 80 px (bark range 95; the log stops a
  running kid at 81 px). The oak's high left branch is no longer a perch; the magpie sits on the lamp post
  before the oak instead, and every perch now drops the ball on the path or on a top of the main route (checked
  for all seven). Stepping-stone gaps 32 px (were 40). The duck boat is a rope ferry (the park keeper's winch)
  and waits at the stone. The leaf cart sets off when Pepper walks into its zone. New: the high route over the
  pond along three willows' branches (from the hedge top), a hollow log on the path (hop over or crawl through,
  a gold bone hidden inside). Secrets: WILLOWS, HOLLOW LOG, OAK TOP. 44 bones (4 gold).
- **Downtown:** a flower tub (28 px) as a step before the 40 px pedestal. The tram sets off when Pepper walks into
  its zone. New: the rooftop route with the ball, from the statue's arm along three balconies and over the
  fountain's top tier, down by the lamp before tram street. Secrets: SHOP SIGN, STATUE HAT, ROOFTOPS. 45 bones
  (3 gold).
- **River Walk:** a planter as a step before the bin in bike zone 2 (the grit box and the pot moved a little).
  The pontoon is a rope ferry and waits at the quay. New: the high route over bike zone 1 on two kiosks' striped
  awnings (the checkpoint lamp moved from 954 to 1074), Pepper's kennel by the house at the left edge (crawl in
  for a gold bone). Secrets: KENNEL, KIOSK ROOFS. 51 bones (3 gold). See `docs/riverwalk_notes.md`.
- **Checks:** `--physics` River Walk 33/33, City Park 64/64, Downtown 57/57 (each secret reachable, each second
  route completed, the ferries, the traffic start and its 1 s warning, hard mode); a test result of nil now
  counts as a failure. `--qa` 0 problems on all three. `--auto` clears all three, also with `--hard`, and prints
  bones, secrets, hearts and time. `--test` has shots of every new spot. `--flowtest` 32/32.
- **Docs:** `docs/citypark_beatsheet.md` and `docs/downtown_beatsheet.md` updated (secrets, second routes, no
  waiting, hard mode, checks); `docs/riverwalk_notes.md` is new.

## Branch `preview/art`: near-lane traffic at its perspective size
- **Cars and cyclists on the road** (River Walk) are drawn for the near lane, which is closer to the camera than the
  promenade: cars about 180-235 x 70-92 px (a Volvo estate in blue and in silver, a delivery van, a taxi, a red
  hatchback), cyclists 73 x 75. Their tops are at y 192, below Pepper's feet, and the frame crops their wheels.
  The promenade bikes keep their size (their hit box is fixed).
- **Facing:** every moving thing faces the way it moves: cars (right), road cyclists (either way), promenade bikes,
  the tram and the leaf cart (left; the cart is now mirrored, its wheel leading), the duck boat, the magpie.
- 7 SpriteCook renders (84 credits; 288 for the art in all). All checks pass.

## Branch `preview/art`: art for the new set pieces
- **City Park:** the three willows over the pond (faded trees, crisp boughs on their ledges), the keeper's winch on
  the far bank, the hollow log (a fallen trunk with hollow ends; it hides the gold bone inside).
- **Downtown:** the flower tub before the pedestal, the three houses of the rooftop route (crisp and outlined, with
  iron balconies as their ledges), the fountain's top tier with water falling from its rims.
- **Far layers:** Downtown's facades and roofs are faded further (40% and 45%, as River Walk's far shore), so the
  obstacles and the climbable houses stand out.
- **Window titles:** "(greybox)" dropped for City Park and Downtown.
- 2 SpriteCook renders (24 credits; 204 for the art in all). No box moved; all checks pass.

## Branch `ml/art`: City Park and Downtown art (fix 11)
Built on `ml/fixes`. Not merged yet: the before/after sheets are for approval first.
- **Art instead of the greyboxes** in levels 1 and 2, in the River Walk style. A level flag `L.art = "park"` /
  `"town"` turns it on; without it the level is drawn as boxes again. No collision box, map, hint, hazard or flow
  changed: every piece is drawn from its prop's box, so box and art stay together.
- **City Park:** the far city (River Walk's skyline), an autumn tree line, near autumn trees, a sandy path with grass
  and earth, the park gate, the leaf piles (they flatten when Pepper runs through), the log, the bench and the bin
  (River Walk's), the hedge on two stems (the crawl gap reads as a gap), the pond with its far bank, mossy stepping
  stones and the duck boat (it faces the way it paddles, its hull in the water), the picnic table (boarded under its
  top: it is solid), the leaf cart, the big oak with branches drawn on its ledges, the slide, the climbing frame,
  the swings, dark bush tops in the foreground below Pepper's line.
- **Downtown:** the far city, old town roofs and spires, a row of Gamla stan facades, a cobbled pavement and street,
  the doorway, apple crates as steps, cafe tables (two legs, so the crawl gap shows) under market parasols, the
  bakers' sign, the market stall and its awnings on posts, the bronze statue (hat and pointing arm on their ledges)
  on its granite pedestal, the fountain (rims, bowl, water jets, its basin), the kiosk, the tram shelter, the tram,
  the RIVER sign, the stone stairs down to the river, granite bollard tops in the foreground.
- **Rules kept:** obstacles are crisp, mid-tone, with their own 1 px dark outline, on Pepper's line; decoration is
  faded 28% with no outline, its base at y 174; nothing is drawn over Pepper (foreground only from y 221 down). The
  magpie and the cat are still drawn in code (the cat is still its labelled box).
- **Making it:** 13 SpriteCook renders (180 credits) in `source_scenery/`, turned into `art/scene/park_*.png` and
  `town_*.png` by `tools/make_town_art.py` (cuts and repeats of whole rows and columns, exact 2x reductions,
  palettes of 5-12 colours, despeckle). The slide, the climbing frame, the oak's branches, the table legs, the shop
  sign, the fountain and the bollards are drawn by hand.
- Pepper is unchanged (`tools/check_pepper.sh`: 2,752 steps identical); physics 17/17, 40/40, 45/45; QA 0 problems
  in all three levels.

## Branch `multilevel`: three levels, one story
Built on `night/all` (the night's River Walk art, Pepper's extras and the City Park greybox). Not merged yet.
- **Game logic rules:** every level ends with a real fetch: Pepper picks up the ball (X) and gives it to the girl (X),
  who waits at the level's end. The ball only moves when someone moves it (a throw, a fall, an animal).
- **The story over three levels:**
  1. City Park: a magpie has stolen the girl's ball; she waits by the swings.
  2. Downtown: in town the ball rolled across the plaza and a cat sat on it; she waits at the stairs to the river.
  3. River Walk: by the river she throws it again and it lands on a ferry; she waits by the cafe.
- **levels.lua:** the play order.
- **Engine (stage.lua):**
  - Score and lives carry over from level to level; hearts refill.
  - The magpie (`L.magpie`): it sits on a perch with the ball in its beak and flies to the next perch when Pepper comes
    near: at 110 px if she runs, only at 40 px if she walks (hold B). A bark within 95 px startles it: it drops the
    ball, which falls with gravity onto whatever is below (path, bench seat, bin, branch, tower), and flies away. On
    its last perch (the climbing frame) it stays. If the ball falls in the pond it comes back by the last lamp.
  - The magpie is drawn in code (14 x 10 px, black and white, blue tail); it flaps when it flies.
  - `L.exit` (reach a point to clear, optionally with the ball) stays in the engine but no level uses it now.
- **City Park:** the magpie replaces the cat in the oak; the first perch is just past the log, so the level opens with
  the lesson: sneak up, bark. 40 physics checks (new: the magpie flees a running Pepper, lets a walking one come
  close, ignores a far bark, drops the ball on a near bark, the ball falls to the path or onto the oak's branch).
- **Downtown:** the girl waits at the top of the stairs down to the river; giving her the ball clears the level
  (FETCH 2000), the stairs alone do not.
- **Font:** an apostrophe and brackets.
- Pepper is unchanged: `tools/check_pepper.sh` still finds all 2,752 steps identical.

## Branch `multilevel`: game flow
- **Menus:** after the title screen's PRESS ANY KEY a small menu opens over the title picture (dimmed, the logo stays bright): START GAME and LEVEL SELECT. Up and down move, A, Space or Enter chooses, B or Esc goes back.
- **START GAME** plays the levels of `levels.lua` in order: 1 City Park, 2 Downtown, 3 River Walk.
- **Level select:** all three levels. Level 1 is always open; a level opens when the one before it is cleared. Locked levels are dimmed with a padlock. A level whose file is missing says COMING SOON and a run skips it (so Downtown can be added later without other changes). Choosing a level plays from it to the end, with fresh lives and score.
- **One run:** one score for the whole run, lives carry from level to level, hearts refill and the timer starts again in every level.
- **Tally per level:** BONES, the level's bonus (FETCH 2000, or BALL from an exit level), TIME BONUS, then the level's POINTS and the run's SCORE. The points still count up with ticks.
- **Story card:** after the tally, the cleared level's outro lines, then the next level's intro card.
- **Ending:** after the last level, GOOD GIRL! with the final score, the best run, THE END and THANKS FOR PLAYING. A button press after 2 s goes back to the title.
- **GAME OVER** goes back to the title. Unlocked levels stay open.
- **Pause:** shows the level's number and name. Start or Enter goes on; B or Esc quits to the title (no longer quits the game). Esc on the title screen quits the game.
- **Saved:** `progress.txt` (open levels) and `best_run.txt` (best run). The best per level stays in `best.txt` (River Walk) and `best_<level>.txt`, now the level's own points.
- **`default_level.txt` and `build_citypark.sh` are gone:** the level select replaces them. `love riverwalk --level <name>` starts a run at that level without the menus. The test flags still play one level alone, River Walk unless `--level` names another.
- **Font:** a comma.
- **New check:** `love riverwalk --flowtest` (or `tools/check_flow.sh`) drives the real menus with key presses through a whole run and checks the carry-over, the refilled hearts, the saved unlocks, the locks and the skipped missing level: 26 of 26 pass. It saves a screenshot of every screen and one sheet of them, `flow_screens.png`. It uses its own save files.
- **Checks unchanged:** PEPPER UNCHANGED (2752 steps identical), River Walk `--physics` 17/17 and `--qa` 0 problems, City Park `--physics` 36/36 and `--qa` 0 problems.

## Branch `multilevel`: Level 2 Downtown greybox
Built on `ml/downtown` from the multilevel engine (ef6e8b3). Beat sheet in `docs/downtown_beatsheet.md`.
- **Level 2, Downtown (greybox):** a Stockholm old town street and plaza. 6 screens, 1920 px, 300 s, 40 bones (2 gold), 5 lamp checkpoints.
  - Old town lane: hop up the crate steps.
  - Cafe terrace: crawl under the cafe tables or jump on them; their parasols are one-way tops; from the second parasol a jump reaches the shop sign (gold bone).
  - Market: onto the stall's counter and up onto its awning; a crate stack up to a second awning.
  - The plaza: the cat sits on the ball on the statue's arm. Bark near it (90 px): it startles, leaps off and runs away, the ball drops to the street. Pick it up. The pedestal, arm and hat are a climb (gold bone).
  - The fountain: carry the ball over the basin, rim to bowl to rim. Falling in costs a heart, and the ball goes back by the statue.
  - Tram street: the tram drives through like the bikes; wait on the kiosk or the tram stop roof. The girl waits at the stairs down to the river (changed later: see the top section).
- **Story text:** intro "A CAT IS SITTING ON THE BALL!", pickup "BRING THE BALL TO THE GIRL!", outro "BY THE RIVER SHE THREW IT / AGAIN. IT LANDED ON A FERRY...".
- **Greybox town:** `greyStyle = "town"` swaps the park's far trees and bushes for far roofs with church spires and near old town facades (stepped gables, rows of windows, doors). City Park and River Walk draw exactly as before: their `--test` screenshots are pixel-identical to ef6e8b3.
- **Engine (small, generic):** a hazard zone can set its hit box (`w`, `h`) and `rail = true` (it keeps to the street's line, so the tram does not drive down the river stairs); the greybox label is the zone's kind (CART, TRAM); the tally shows the level's own bonus (BALL 1000 here, FETCH 2000 otherwise).
- **Checks:** `love riverwalk --level downtown --physics` 45/45, `--auto` plays to GOOD GIRL! (no hearts lost, 37/40 bones, about 33 s), `--test` screenshot tour, `--qa` 0 problems. Unchanged: River Walk `--physics` 17/17 and `--qa` 0 problems, City Park `--physics` 36/36 and `--qa` 0 problems, PEPPER UNCHANGED.

## Night branch `night/riverwalk-art` (not merged, 6 Oct 2026)
Built on the trial branch `try/scenery-v2`. Every greybox left in River Walk now has art. Pepper is untouched:
`tools/check_pepper.sh` plays the level on autopilot and finds her position, speed, clip and frame identical on
all 2,752 steps. No collision box changed. All art is made by `tools/make_night_art.py` (sources in `source_scenery/`).
- **Bridge on screen 7:** a pale granite bridge abutment with a cornice and a balustrade (SpriteCook, 138 x 162)
  replaces the grey pier. Pepper still crawls under its lintel (y 192). The passage under it is dark at the back
  and the pavement inside is shaded, so it reads as a low way through.
  - Fitted by cutting one brick period out of each side panel, so nothing was rescaled.
- **Pontoon:** a plank deck on two float drums (54 x 12) replaces the PONTOON box. SpriteCook drew it 4x too big and
  a 4x reduction came out muddy, so it is drawn by hand in the render's own colours.
- **Clouds:** eight soft SpriteCook clouds replace the white boxes. They drift as before.
- **Bones:** small hand-drawn bones (11 x 6) with an outline; super bones are gold.
- **Foreground posts:** the two dark bars are now the tops of tarred mooring piles at the bottom edge of the screen
  (three of them). Their tops are below every line Pepper stands on, so they never hide her.
- **Far shore:** the far bridge has 8 arches instead of 40, and the trees continue after it.
- **New check:** `tools/check_pepper.sh` with `love riverwalk --auto --trace` and the golden trace of the approved build.
- **Credits:** 96 SpriteCook credits (4 generations x 2 variations).

## Night branch `night/pepper-extras` (not merged)
- **Visual extras around Pepper** (`riverwalk/extras.lua`), small and pixel-hard, 90s console style. Each has its own switch in `Ex.on`, all on:
  - **Landing dust (`dust_land`):** after a fall of 12 px or more, little puffs roll out from her paws, 1 to 3 each side by fall height. Not on small steps.
  - **Skid dust (`dust_skid`):** while she skids, a small puff kicks off her front paws every few steps and stays behind as she slides.
  - **Run-start kick (`dust_start`):** when she breaks into a gallop from standing, one small puff behind her back paws.
  - **Splash (`splash`):** when she falls in the river: a white burst, a crown of drops, a broken foam line across her that thins out, two ripples sliding away.
  - **Bone pop (`bone_pop`):** a picked-up bone twinkles where it was and a tiny +100 (gold +1000 for a super bone) floats up and blinks out. It is drawn behind her, so it never covers her.
- **Colours:** dust is the pavement's warm greys a step lighter than its lightest stone, so it reads as dust off the paving; the splash uses the river art's light blues. Puffs grow, then break up into a dither and thin out (palette steps, no alpha). Everything scrolls with the level.
- **E key:** all extras off / on in the game, for comparing. `love riverwalk --noextras` starts with them off.
- **Pepper unchanged:** her art, clips, frames, speeds, tuning and physics are untouched (`pepper.lua`, `pepper_frames.lua` and `pepper.png` not edited). The extras only watch her from `stage.lua` and draw. `tools/check_pepper.sh`: PEPPER UNCHANGED (2752 steps identical); 17 physics checks pass; `--qa` 0 problems.

## Night branch `night/citypark` (not merged)
- **Level 1, City Park (greybox):** 6 screens, 1920 px, 300 s. Beat sheet in `docs/citypark_beatsheet.md`.
  - The gate: hop onto the log; a leaf pile hides bones.
  - Benches: jump onto the bench or crawl under it; crawl through the hedge gap. A running jump from the seat reaches the hedge top (gold bone).
  - The pond: stepping stones, then the duck boat (moving platform). Falling in costs a heart.
  - Leaf cart: climb the bin (jump + scramble); the park keeper's cart drives through like the bikes. Get up on the picnic table.
  - The big oak: the cat sits on the girl's ball. Bark near it (90 px): it startles, leaps off and runs away, the ball drops. Branches to climb for a gold bone.
  - Playground: slide tower and slide, climbing frame, the girl. GOOD GIRL!
  - 40 bones (2 gold), 5 lamp checkpoints.
- **Choosing the level:** `love riverwalk --level citypark`. River Walk is still the default. `./build_citypark.sh` builds `CITYPARK_greybox.love`, where City Park is the default (`default_level.txt` in the zip). Best scores are kept per level.
- **Greybox scenery for City Park:** misty boxes per parallax layer, flat grey ground with a 1 px edge, labelled boxes for props, greybox lamp posts and cat. River Walk draws exactly as before (its screenshots are pixel-identical to `night/base`).
- **Engine additions (used by City Park only):** the cat (sit, scared, leap, run, gone), leaf piles drawn over bones that flatten when Pepper runs through, a cart kind for hazard zones, label placement for thin props, the mover's own name as its label.
- **Checks:** City Park `--physics` 38/38, `--auto` plays to GOOD GIRL! (no hearts lost), `--qa` 0 problems. River Walk unchanged: `--physics` 17/17, `--qa` 0 problems, PEPPER UNCHANGED.

## Trial branch `try/scenery-v2` (not merged)
- **Longer level, reworked layout:** River Walk is now 3200 px (10 screens, 420 s).
  - Obstacles stand apart with clear pavement between them and repeat along the level: bench, flower box, bin, grit box, planter.
  - Two bike zones with spaced perches (all above the bikes).
  - The river is wider for the bigger ferry. Lamps every 300-490 px, all checkpoints. 46 bones.
- **Starter composition kept:** the original house and tree, now decoration (faded, base on the pavement's back edge). Their cut left edges sit on the level's left edge, so nothing looks cropped.
- **Decoration rules for houses and trees:** gable, cafe, house and trees are faded like the lamps and have no dark outline. Two more trees along the promenade: the round SpriteCook tree and the original tree completed by SpriteCook.
- **Ferry a little bigger** (252x93): longer decks, taller saloon windows; deck y 206, saloon roof y 184, wheelhouse roof y 154 (ball).
- **The road:** a new asphalt texture (grain, worn tyre tracks, cracks, repair patches, dashed centre line), manhole covers and kerb drains (tools/make_road.py).
- **Traffic:** cars and cyclists pass on the road in the near lane, only where there is road (road.lua). The promenade bikes are drawn as cyclists and ride up and down the stairs instead of floating.
- **QA:** `love riverwalk --qa` (0 problems); 17 physics checks; the autopilot plays to GOOD GIRL!
- **Commuter ferry** (user pick, from their photos of the Djurgården ferry): one image on screen 4 with three hidden boxes: the deck (y 206), the saloon roof (y 188, a hop up) and the wheelhouse roof (y 158, a held jump up), where the ball lies. The old CABIN box and mast are gone.
- **Grit box (SAND)** replaces the low flower box on screen 2 (top y 152, half way up its sloping lid). Halved from a 2x render; the label is repainted.
- **Every lamp is a checkpoint** now, so every lamp lights up when Pepper passes (the one at x 498 never did).
- **Checks:** 16 physics checks (the ferry's two climbs replace the cabin scramble). The autopilot plays to GOOD GIRL!
- **Stockholm bench and bin** (from the user's photos):
  - **Bench (103x51):** green slats, black frame, ball-knob armrests, straight posts. It came out at twice the game scale, so `tools/make_props.py` halves it and lengthens the posts 3 px, keeping the seat at y 156 (crawl gap 19 px). A wider ground shadow fills the pavement under the seat so it no longer looks like it floats (`depth` on the prop, `Sc.shadow`).
  - **Bin (38x59):** the black city bin with gold bands and the shield. Same top (y 128).
- **Obstacles redrawn, bigger and mid-tone (round 2, SpriteCook):** they keep their own 1 px outline, so they no longer look black. `tools/make_props.py` cleans them (16-colour palette, despeckle).
  - **Bench (114x56):** only the seat is solid (y 156-165). Pepper crawls under it (19 px clear) or jumps onto it (28 px up: a held jump or a hop plus a scramble).
  - **Bin (44x60):** top at y 128 (56 px, as high as the cabin roof). A short jump from the bench seat, or a scramble from the pavement.
  - **Screen 2:** the iron fences and grey planters are replaced by a flower box (top y 152), a square planter (y 154) and a low flower box (y 157), all above the bikes. The lamp at x 470 moved to 498.
- **Buildings on screen 6:** a stepped-gable house and a cafe, redrawn in SpriteCook at the screen-1 building's scale (the eight Artlist buildings were about 1.5x too small). The girl stands in front of the cafe. The decorative railing there now stops at the gable; the BIKES box and the top-right foreground box are gone.
- **Checks:** 15 physics checks (new: crawl under the bench, scramble onto the bin, the flower box). The autopilot plays to GOOD GIRL!
- **Skyline, pavement, building and tree** from four 4x images, saved at 1x (exact 4x pixel blocks, nothing lost).
  - **Skyline:** it replaces the grey city. It scrolls at 0.08 and is followed by its own first 128 columns, so only one City Hall tower ever shows.
  - **Pavement:** it is painted along every walkable top, with its back edge 12 px behind Pepper's walking line, then the kerb and road. The bridge pier stays greybox.
  - **Building and tree:** they replace Pepper's home box, the door box and the top-left foreground box. They stand on the pavement's back edge.
- **Title screen:** shown when the game starts, cleaned up and animated. `tools/make_title.py` builds it from `source_title/title_original.png`.
  - **Clean-up:** the painting is brought down to the game's 320x240 (each pixel takes the median colour of its cell), reduced to a 64-colour palette and despeckled.
  - **Layers:** it is cut into layers in `art/title/`, with positions in `title_data.lua`.
  - **Animation (`title.lua`):**
    - the screen fades in
    - the river's sparkles twinkle
    - both lamps glow and flicker
    - Pepper blinks her open eye, sometimes twice
    - the bird flaps, glides and drifts
    - a shine sweeps across the logo
    - PRESS ANY KEY TO START blinks
  - **On a key press:** the text blinks fast and the screen fades out to the level card.
- **New bench and pot:** revised art, same sizes, so nothing else changed.
- **Lamp posts and pot:** they stand on the back edge of the pavement by the water. Their bases are 10 px behind Pepper's walking line.
- **Railings split, preview for review (may be reverted):**
  - **Decoration by the water:** an open tube railing from SpriteCook (asset 7d30bc38). Its shades are mapped onto the lamp post's palette by `tools/make_bg_railing.py`, then faded like the lamps. No outline; Pepper cannot stand on it. It runs along the water on screens 1 to 2 and screen 6.
  - **Obstacles on screen 2:** two short sections of the iron fence on Pepper's line (x 256-344 and 448-536), chained with the two planters for dodging the bikes.
    - They are crisp and outlined, and they block her.
    - Their balusters are longer (a plain baluster row repeated), so the top at y 152 is above the bikes.
  - **Removed:** standing on the long railing, and the Down + A drop-through check (replaced by a fence check).
- **Quay railing:** new SpriteCook railing (asset 2b178488), cleaned to 8 colours by `tools/make_railing.py`.
  - **Tiling:** sections (left post and span) repeat along the railing and a closing post ends it.
  - **Obstacle style:** Pepper uses it, so it is outlined like the bench and bin and never faded. The outline goes round the whole assembled railing, so it has no seams.
  - **Position:** its posts stand on the pavement's back edge.
  - **Height:** the handrail she stands on is now y 152 (was 149), still above the bikes (they reach up to y 158). The railing runs x 256 to 672, and the bones on it moved with it.
- **Obstacles back on Pepper's line:** the bench and bin stand on Pepper's walking line again (seat top y 173, bin top y 158). Set back, they looked like things she could walk past.
- **River:** a new water sprite from SpriteCook (asset d19d28b6) replaces the old river strip.
  - **Clean-up (`tools/make_water.py`):**
    - the haze rows above the waterline are dropped
    - the deepest rows repeat to the bottom of the screen
    - 20 colours, despeckled
  - **Animation:** each row scrolls on its own.
    - The far water moves with the far shore and barely flows; the near water flows faster.
    - Every row wobbles a pixel or two.
    - The glints ride with their rows and twinkle.
- **Shadows:** soft ground shadows under Pepper, the girl, the ball and the props. Pepper's shadow stays on the floor under her and shrinks as she jumps.
- **Checkpoint lamps:** a lit lamp has a warm glow with a slight flicker, and a flash of light when it lights up.
- **Obstacle course vs decoration:**
  - Things Pepper can use (bench, bin) get the characters' 1 px dark outline.
  - Decoration (pot, lamp posts) is faded 28% towards the haze.
  - Both are done in code; the art files are untouched.
- **Checks:**
  - 13 of 13 physics checks pass.
  - The autopilot finishes the level.
  - The checks skip the title.

## v0.3 (5 Oct 2026)
- Scenery art from `riverwalk_scenery_v1`: far shore and bridge, river, bench, bin, pot, lamp post. The files are unaltered.
- **Far shore:** the 320 px strip is extended to the 800 px the layer needs. One of its arches is repeated and the bridge closes with its own left end mirrored.
- **River:** the fallable river on the quay shows the river art instead of a grey box.
- **Lamps:** a passed checkpoint lamp now glows warm (only the glass pixels are recoloured) instead of turning into a gold box.
- **Bench (gameplay):**
  - The bench is its real size (11 px seat), so it is a hop: walk into it and you stop, a hop lands on the seat.
  - The crawl lesson moves to the bridge on screen 5. The screen 1 crawl hint is gone, and the bones under the bench now sit on the seat.
- **Bin (gameplay):** the bin is its real size (17x26), so its top is 11 px lower.
- **Pot:** decoration between the bench and the bin, where the concept has it.
- **Checks:**
  - 13 of 13 physics checks pass; the bench checks now test the hop.
  - The autopilot finishes the level.

## v0.2 (5 Oct 2026)
- Pepper is drawn 1 px lower at all times, so her paws sit in the ground line and she no longer looks like she is floating. The ball in her mouth moves with her. Drawing only: collisions and jump heights are unchanged.

## v0.1 (5 Oct 2026)
- Approved baseline: greybox level, Pepper (14 cleaned SpriteCook clips), the girl (5 standing clips), the ball. All unapproved scenery art removed.
