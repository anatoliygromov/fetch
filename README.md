# River Walk: handoff build (5 Oct 2026)

The approved state of Level 3, River Walk. Use it as the starting point in a new chat: attach this zip and ask Claude to read the project doc `claude/riverwalk-handoff.md`.

## What is in it (approved)

- **Level design:**
  - all six screens as a greybox
  - tuned physics
  - tutorial prompts, bikes, the pontoon, the boat and the bridge
- **Pepper:** 14 whole SpriteCook clips, cleaned:
  - idle, panting, tail wag, walk, gallop
  - jump (synced to the physics), skid, crouch, belly crawl
  - hurt, sit, bark, sniff, ball pick-up
- **The girl:** 5 clips made from her standing pose: idle, wave, call, cheer, pet.
- **The ball.**
- **Code-made parts:** the HUD, font and sounds.

## What was removed (not approved)

- **Scenery art:** every piece is gone and the level draws plain grey boxes again. That covers:
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

## Folders

| Folder | What it is |
| --- | --- |
| `riverwalk/` | The game (LÖVE 11). Run `love riverwalk` |
| `RIVERWALK.love` | The same game as one file |
| `source_sheets/` | The 20 SpriteCook spritesheets the character art is built from |
| `tools/` | `build_pepper_clean.py` and `build_girl.py` rebuild `riverwalk/art/pepper.png`, `girl.png` and the frame tables from `source_sheets/`, through `clean.py`. The output matches the shipped art pixel for pixel. `decode.py` is the Chrome download route for new SpriteCook files |
| `riverwalk_girl_standing.gif` | A playthrough of this build |

## Checks (all pass on this build)

- **Physics:** `love riverwalk --physics` runs 13 checks, and 13 of 13 pass.
  - jump heights
  - crawling under the bench and the bridge
  - the scramble onto the cabin
  - stairs
  - drop-through
  - the pontoon
  - falling in the river
- **Autopilot:** `love riverwalk --auto` plays the whole level and reaches GOOD GIRL!
- **Screenshots:** `love riverwalk --test` saves screenshots.

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
| Start | Enter | Pause |
| Select | G | Debug view |

Tab opens the tuning panel (keyboard only).

## Still placeholders

- **Turn:** no turn animation.
- **Jump wind-up:** the crouch frames of the jump clip are not used.
- **Other characters:** no cat, pigeons or gulls.
- **Bikes:** the bike is a box.
