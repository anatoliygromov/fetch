# FETCH! Level 3: River Walk

The approved state of Level 3, River Walk, under git. Every delivered build is a tag; see `CHANGELOG.md`.

## What is in it (approved)

- **Level design:**
  - all six screens; scenery is greybox except the pieces listed below
  - tuned physics
  - tutorial prompts, bikes, the pontoon, the boat and the bridge
- **Pepper:** 14 whole SpriteCook clips, cleaned:
  - idle, panting, tail wag, walk, gallop
  - jump (synced to the physics), skid, crouch, belly crawl
  - hurt, sit, bark, sniff, ball pick-up
- **The girl:** 5 clips made from her standing pose: idle, wave, call, cheer, pet.
- **The ball.**
- **Scenery (from `riverwalk_scenery_v1`):** far shore and bridge, river, bench, bin, pot and lamp post. They are used exactly as delivered, in `riverwalk/art/scene/`. Two things are made from them in code:
  - **far shore:** extended to cover the whole level by repeating one of its own arches and closing the bridge with its own left end mirrored
  - **lit lamp:** a passed checkpoint lamp's glass is recoloured warm
- **Code-made parts:** the HUD, font and sounds.

## What was removed (not approved)

- **Old scenery art:** every piece is gone; scenery without approved art is still plain grey boxes. That covers:
  - the house, bench, bin, lamp posts, railing, canopy and tree band
  - pavement, quay wall, the city across the river and its reflection
  - sky, sun, clouds, skylines and the bone sprite
- **Unreviewed new scenery:** the new SpriteCook scenery tries (bench, bin, lamp, railing, canopy, city) and the house drawn in code.
- **Superseded clips:**
  - older versions of crawl, jump, skid, hurt, crouch and pick-up
  - Pepper's dig
  - the girl's walk, jump and throw
  - the girl clips made from her walking pose
- **A bin collision change:** it only existed to fit the old bin art. The bin is back at its greybox height.

## Level 1: City Park (greybox, branch `night/citypark`)

- `love riverwalk --level citypark` starts a run at City Park (no menus); the test flags work with it too
  (`--physics`, `--auto`, `--test`, `--qa`).
- Beat sheet: `docs/citypark_beatsheet.md`.

## Game flow (branch `ml/flow`)

- **Title screen**, then a menu: START GAME plays the levels in order (1 City Park, 2 Downtown, 3 River Walk);
  LEVEL SELECT plays from the chosen level to the end.
- **Level select:** level 1 is always open, a level opens when the one before it is cleared. Locked levels are
  dimmed with a padlock; a level whose file is missing says COMING SOON and is skipped in a run.
- **One run:** one score for the whole run, lives carry from level to level, hearts refill and the timer starts
  again in every level.
- **Between levels:** the tally (bones, the level's bonus, time bonus, points, score), then a story card, then the
  next level's intro card. After the last level: the ending (GOOD GIRL!, final score, best run, THE END).
- **GAME OVER** goes back to the title; unlocked levels stay open.
- **Saved** in LÖVE's save folder: `progress.txt` (open levels), `best_run.txt` (best run score),
  `best.txt` / `best_<level>.txt` (best points per level).
- The code is in `riverwalk/flow.lua`; `love riverwalk --flowtest` (or `tools/check_flow.sh`) checks it.

## Folders

| Folder | What it is |
| --- | --- |
| `riverwalk/` | The game (LÖVE 11). Run `love riverwalk` |
| `RIVERWALK.love` | The same game as one file (made by `build.sh`, not in git) |
| `source_sheets/` | The 20 SpriteCook spritesheets the character art is built from |
| `source_scenery/` | The manifest that came with the scenery art (SpriteCook source IDs) |
| `tools/` | `build_pepper_clean.py` and `build_girl.py` rebuild `riverwalk/art/pepper.png`, `girl.png` and the frame tables from `source_sheets/`, through `clean.py`. The output matches the shipped art pixel for pixel. `decode.py` is the Chrome download route for new SpriteCook files |
| `build.sh` | Builds `RIVERWALK.love` from `riverwalk/` |
| `CHANGELOG.md` | What changed in each version |

## Checks (all pass on this build)

- **Physics:** `love riverwalk --physics` runs 13 checks, and 13 of 13 pass.
  - jump heights
  - the bench: it stops a walk, a hop lands on the seat
  - crawling under the bridge
  - the scramble onto the cabin
  - stairs
  - drop-through
  - the pontoon
  - falling in the river
- **Autopilot:** `love riverwalk --auto` plays the whole level and reaches GOOD GIRL!
- **Screenshots:** `love riverwalk --test` saves screenshots.
- **Pepper unchanged:** `tools/check_pepper_lab.sh` (a test room built in code, no level: PEPPER UNCHANGED) and
  `tools/check_pepper_files.sh` (her five files against aa38be5, the approved build); `tools/check_pepper.sh`
  compares a River Walk autopilot run with its recorded trace.
- **Hard mode:** add `--hard` to `--auto` (1 heart, traffic 25% faster).
- **Game flow:** `tools/check_flow.sh` runs `love riverwalk --flowtest`: it drives the menus through a whole run
  (26 checks) and puts a screenshot of every screen on one sheet, `flow_screens.png`.

## Controls

| Handheld | Keyboard | Does |
| --- | --- | --- |
| D-pad | Arrows | Run |
| Down | Down | Crouch and crawl |
| A | Space or Up | Jump; hold for higher |
| Down + A | Down + Space | Drop through the railing or a deck |
| B | Shift | Walk |
| X | X | Pick up, drop, give the ball |
| Y | Z | Bark |
| Start | Enter | Pause; in the pause, go on |
| B (in the pause) | Esc (in the pause) | Quit to the title |
| Select | G | Debug view |

In the menus: D-pad or the left stick up and down (arrows) move, A or Start (Space or Enter) chooses,
B (Esc) goes back. Any button moves on from the title, the level cards, the tally, the ending and GAME OVER.
On the title screen Esc quits the game. Tab opens the tuning panel (keyboard only); F fullscreen, M music,
E visual extras.

## Still placeholders

- **Turn:** no turn animation.
- **Jump wind-up:** the crouch frames of the jump clip are not used.
- **Other characters:** no cat, pigeons or gulls.
- **Bikes:** the bike is a box.
