# FETCH FRENZY: each round in its level's own place (owner, 7 Nov)

Branch `day/07nov-bonusscene`. 0 credits, no image service called, no new art files. Pepper unchanged.

The owner on 7 Nov, looking at a round after River Walk set on the City Park lawn: "these levels should have
different scenery". Every bonus round was built from City Park's art, whatever level it followed. Now each round is
set in the place of the level it follows: one calm, flat, open screen built only from that level's approved art and
its colour script (`look.lua`).

## Which level gets which scene

| Level (number) | Round (throws) | Scene | Light (colour script) | Fallback? |
| --- | --- | --- | --- | --- |
| River Walk (1) | A, ball rally | the riverside promenade: quay paving, the railing by the water, the river, the far shore, bridge and city | summer morning (riverwalk) | no |
| City Park (2) | B, stick time | the park lawn: the path, the round trees, the far tree line and city | autumn afternoon (citypark) | no |
| Downtown (3) | C, frisbee float | an old town square: the far roofs and spires across the square, the square's floor, the street's setts | midday (downtown) | no |
| Rooftops (4) | A | Downtown's square | midday | **yes**: no art key or colour script yet. Rooftops climbs from Downtown's street, so the square under the roofs is its nearest place |
| Söder Hill (5) | B | City Park's lawn | autumn afternoon | **yes**: no art key or colour script yet. A hill park, so the park lawn is its nearest place |
| Night Harbour (6) | C | River Walk's promenade | summer morning | **yes**: no art key or colour script, and no night colour script to keep. A quay by the water, so the promenade is its nearest place. Its darkness is a gameplay overlay (`night.lua`), not a palette, so it is not used here |

The fallbacks are one table, `BS.BY_LEVEL` in `riverwalk/bonusscene.lua`. When a level gets its own art and colour
script, change its line.

## What each scene is made of

The play floor is the same everywhere: flat at y 184, the screen's edges as walls (`B.world`, unchanged). Nothing
stands on it. Decoration is behind Pepper's line (the railing, the far rows) or below it (the front edge).

- **River Walk**: `Sc.drawFar` (sky, clouds, skyline, far shore and bridge, the river, as in the level), the
  decorative railing on the paving's back edge (y 174), and the ground by the level's own rule (`Sc.paintQuay`, the
  lower quay's kind): the paving, its granite coping, then the quay wall in courses to the bottom.
- **City Park**: `Sc.drawFarArt` (sky, skyline, far tree line, round trees, as before), the lawn and path
  (`park_ground.png` rows 0-28), then a new front edge by rule (below).
- **Downtown** (one function, `farDowntown` / `buildDowntown`): only what stays through the redesign on
  `day/07nov-dt`: the sky and clouds, the skyline, the far roofs and spires (`town_roofs.png`) and the square's floor
  (`town_square_floor.png`), then the street's setts, kerb and quay wall (`town_ground.png`, as in the level). No
  facades. In the level the roofs stand behind the facade row, faded 70 % to the shore haze; with nothing in front
  they read as a pale wall of houses over the whole screen, so here they stand across the square where the mid row
  would be: faded as the mid layer (25 %) and set 54 px lower, their foot hidden under the square's floor. The
  file is untouched; it is whole-pixel placement and the game's own fade.

## The ground's front edge (the stripes)

Under the City Park path there were 5 flat bands of dark earth (olive, brown, plum, near-black) to the bottom of the
screen. Each scene now ends in a finished front edge:

- **City Park**: a kerb of granite setts in the park stone's greys (`park_stone.png`: lit top, face, shaded foot,
  joints every 12 px), grass tufts leaning over its foot so the lawn meets it without a cut, a grass verge in the
  tile's own lawn green with tufts on an 8 px grid in offset rows, and in front two clipped hedges in City Park's
  foreground colours (the approved hedge from `look.lua`, tops at y 224 or lower, never over Pepper or an item),
  with a gap where the verge runs on to the bottom.
- **River Walk**: the quay coping (lit kerb top, granite face, a shadow row) and the quay wall face under it.
- **Downtown**: the setts end at the street's granite kerb with the quay wall under it (the level's own tile).

Frames: `citypark_before_after_2x.png` (same autopilot frame, before left, after right, colour over greyscale) and
`citypark_ground_before_after_4x.png` (the bottom band, before above, after below).

The ground is now painted under the back layer's grade and drawn under the ground's, as `stage.lua` does in the
levels. Before, the bonus painted it with no grade, so its path was a shade duller than City Park's own (path
233/176/112 before, 255/180/94 now, the same as the level).

**The joins kit**: I read `riverwalk/joins.lua` and `tools/make_ground_kit.py` on `origin/day/07nov-ground` and took
nothing from them. The kit's drawn parts are City Park's mid-row lawn, tufts and tree-root grass, and its geometric
parts are painters inside `scene.lua` that work from a level's kind map. A flat 320 px screen has no joins between
ground kinds. The front edges here are drawn by rule in each level's own colours.

## Readability (greyscale, 2x)

Background luma where the items fly and Pepper runs (y 40-184, Mia and Pepper masked, READY frame): River Walk p5
135, median 174; City Park p5 135, median 195; Downtown p5 113, median 185. Pepper's body is about 30-50, the items'
ink 35-41, the ball 58, the stick 101, the frisbee 108. All read clearly against every scene in the `*_grey_2x.png`
frames. Downtown's darkest background spots are the square's bollards and window glazing (about 70-80), small and
far behind the play line.

## Frames

Per level, the same moment of each round's autopilot (`love riverwalk --level X --bonus --auto`, its `rec/` frames,
taken from the 2x window as 1x by one pixel per 2x2 block):

- `N_<level>_<scene>_1x.png`, `_3x.png` and `_grey_2x.png` for N = 1-6
- `all_rounds_1x.png`: the six rounds in order (rows of 3, colour over greyscale)

## Checks (final commit)

- `love riverwalk --bonus` and `--level X --bonus` for riverwalk, citypark_tall, downtown_tall, rooftops, soder and
  night: no Lua errors; every level's full round played by the autopilot (`--auto`) with the same results as before
  the change (A 14 of 15, B 13 of 15, C 13 of 14).
- Bonus tests (`love riverwalk --bonus --physics`): 23 of 23 passed.
- `tools/check_flow.sh`: 125 of 125 passed.
- `tools/check_pepper.sh`: PEPPER UNCHANGED (3908 steps identical).
- River Walk physics (`--level riverwalk --physics`, as `Sc.paintQuay` got one option): 55 of 55 passed.

Each run with its own `XDG_DATA_HOME=$(mktemp -d)`, under `xvfb-run -a`, `SDL_AUDIODRIVER=dummy`.

## Files

- `riverwalk/bonusscene.lua` (new): the scene table, the three scenes, the front edges.
- `riverwalk/bonus.lua`: the round picks its scene from the level number; the City Park drawing moved out.
- `riverwalk/scene.lua`: `Sc.paintQuay` takes `def.quayFront` (every column the quay's kind, no road);
  `Sc.skyAndClouds` and `Sc.strip` exported. The levels draw exactly as before.
- `riverwalk/look.lua`: `Look.clump` exported (the hedge). The levels draw exactly as before.
- Not touched: Pepper's files, `world.lua`, `stage.lua`, the throws, catch rules and timings.

## Questions for the owner

1. Night Harbour's round is on River Walk's promenade in morning light until Night gets its own colour script. OK,
   or should it wait for a night look?
2. Söder Hill's round is on the City Park lawn. Would you rather have Downtown's square or the River Walk quay there?
3. City Park's front: clipped hedges with a gap where the verge runs on. OK, or the verge alone to the bottom?
