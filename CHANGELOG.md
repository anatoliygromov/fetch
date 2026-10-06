# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

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
