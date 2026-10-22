# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

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
