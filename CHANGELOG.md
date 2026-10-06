# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

## Branch `multilevel`: three levels, one story
Built on `night/all` (the night's River Walk art, Pepper's extras and the City Park greybox). Not merged yet.
- **The story over three levels:** 1 City Park, the girl throws the ball too far and Pepper chases it out of the
  park. 2 Downtown, a cat sits on it on the plaza; Pepper barks it away and carries the ball to the river. 3 River
  Walk, the ball has bounced onto a ferry; Pepper brings it back to the girl.
- **levels.lua:** the play order.
- **Engine (stage.lua):**
  - Score and lives carry over from level to level; hearts refill.
  - A level can have no girl (Downtown).
  - `L.exit`: reaching it clears the level, with `needBall` only while carrying the ball (+1000 BALL).
  - `L.ballRun`: the runaway ball waits at each point, hops on when Pepper comes within 90 px and finally leaves the level.
- **City Park is now the chase:** the girl stands by the gate, the ball bounces ahead through the park, and the far
  gate ends the level. The cat moved to Downtown. 36 physics checks (new: the runaway ball, the gate).
- Pepper is unchanged: `tools/check_pepper.sh` still finds all 2,752 steps identical.

## Branch `multilevel`: game flow
- **Menus:** after the title screen's PRESS ANY KEY a small menu opens over the title picture (dimmed, the logo stays bright): START GAME and LEVEL SELECT. Up and down move, A, Space or Enter chooses, B or Esc goes back.
- **START GAME** plays the levels of `levels.lua` in order: 1 City Park, 2 Downtown, 3 River Walk.
- **Level select:** all three levels. Level 1 is always open; a level opens when the one before it is cleared. Locked levels are dimmed with a padlock. A level whose file is missing says COMING SOON and a run skips it (so Downtown can be added later without other changes). Choosing a level plays from it to the end, with fresh lives and score.
- **One run:** one score for the whole run, lives carry from level to level, hearts refill and the timer starts again in every level.
- **Tally per level:** BONES, the level's bonus (FETCH 2000, or BALL from an exit level), TIME BONUS, then the level's POINTS and the run's SCORE. The points still count up with ticks.
- **Story card:** after the tally, the cleared level's outro lines (City Park: the ball bounced out into town), then the next level's intro card.
- **Ending:** after the last level, GOOD GIRL! with the final score, the best run, THE END and THANKS FOR PLAYING. A button press after 2 s goes back to the title.
- **GAME OVER** goes back to the title. Unlocked levels stay open.
- **Pause:** shows the level's number and name. Start or Enter goes on; B or Esc quits to the title (no longer quits the game). Esc on the title screen quits the game.
- **Saved:** `progress.txt` (open levels) and `best_run.txt` (best run). The best per level stays in `best.txt` (River Walk) and `best_<level>.txt`, now the level's own points.
- **`default_level.txt` and `build_citypark.sh` are gone:** the level select replaces them. `love riverwalk --level <name>` starts a run at that level without the menus. The test flags still play one level alone, River Walk unless `--level` names another.
- **Font:** a comma (CHASE IT, PEPPER!).
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
  - Tram street: the tram drives through like the bikes; wait on the kiosk or the tram stop roof. The stairs down to the river end the level, only with the ball (BALL bonus 1,000). No girl in this level.
- **Story text:** intro "A CAT IS SITTING ON THE BALL!", pickup "TAKE THE BALL DOWN TO THE RIVER!", outro "THE BALL SLIPPED AND BOUNCED / ONTO A FERRY ON THE RIVER...".
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
