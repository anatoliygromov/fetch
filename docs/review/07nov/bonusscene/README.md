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
  (`town_square_floor.png`), then the street's setts, kerb and quay wall (`town_ground.png`). No facades. In the level the roofs stand behind the facade row, faded 70 % to the shore haze; with nothing in front
  they read as a pale wall of houses over the whole screen, so here they stand across the square where the mid row
  would be: faded as the mid layer (25 %) and set 54 px lower, their foot hidden under the square's floor. The
  file is untouched; it is whole-pixel placement and the game's own fade.

## The ground's front edge (the stripes)

Under the City Park path there were 5 flat bands of dark earth (olive, brown, plum, near-black) to the bottom of the
screen. Each scene now ends in a finished front edge:

- **City Park**: a kerb of granite setts in the park stone's greys (`park_stone.png`: lit top, face, shaded foot,
  joints every 12 px), grass tufts with lit tips leaning over its foot so the lawn meets it without a cut, then the
  lawn runs on to the bottom of the screen in the tile's own green: tufts (a lit pair over a dark pair) in offset
  rows that come closer together towards the bottom, and ten single fallen leaves in the leaf piles' colours
  (`park_leaves.png`). No dark foreground shapes, no full-width bands.
- **River Walk**: the quay coping (lit kerb top, granite face, a shadow row) and the quay wall face under it.
- **Downtown**: the setts end at the street's granite kerb with the quay wall under it (the level's own tile). The
  kerb's face and the wall are drawn in the file's own granite greys (see round 2).

Frames: `citypark_before_after_2x.png` (same autopilot frame, before left, after right, colour over greyscale) and
`citypark_ground_before_after_4x.png` (the bottom band, before above, after below).

The ground is now painted under the back layer's grade and drawn under the ground's, as `stage.lua` does in the
levels. Before, the bonus painted it with no grade, so its path was a shade duller than City Park's own (path
233/176/112 before, 255/180/94 now, the same as the level).

**The joins kit**: I read `riverwalk/joins.lua` and `tools/make_ground_kit.py` on `origin/day/07nov-ground` and took
nothing from them. The kit's drawn parts are City Park's mid-row lawn, tufts and tree-root grass, and its geometric
parts are painters inside `scene.lua` that work from a level's kind map. A flat 320 px screen has no joins between
ground kinds. The front edges here are drawn by rule in each level's own colours.

## Round 2 (coordinator's fixes, 7 Nov)

1. **City Park's dark hedges removed.** At 11:27 the owner called exactly these black foreground shapes in City
   Park "terrible". No bonus scene has dark foreground clumps now (`look.lua` is back as on main).
2. **City Park's front edge: no flat olive band.** Two options at 3x in `round2_citypark_options_3x.png`:
   - above: the verge, then a low earth bank, its edge breaking into 2-3 px steps with a dark contact line, stones
     in it, in `park_ground.png`'s earth colours
   - below: the lawn running to the bottom with tufts closer together lower down and a few fallen leaves

   Picked: **the lawn**. Graded as the ground (as in the level), the bank's earth reads as a plum band across the
   screen, the colour and shape the owner disliked in the old earth stripes. The lawn has no band at all.
   Before/after: `round2_citypark_before_after_3x.png` (round 1 above, now below).
3. **Downtown's quay wall: granite, not purple.** The level paints its ground under the back layer's grade and draws
   it under the ground's, and both push dark greys towards violet, so the wall read as a purple brick band (it does
   in the level too: 83/68/95 and 89/75/98 at street level). The bonus now draws the kerb's face and the quay wall
   (`town_ground.png` rows 30-67) ungraded, in the file's own warm granite greys (72/66/64, 78/72/69, joints
   47/43/47). The street's setts and kerb top keep the level's grade. Rooftops falls back to Downtown, so it gets
   the same fix. Before/after: `round2_downtown_before_after_3x.png`, `round2_rooftops_before_after_3x.png`.

## Round 3 (review on review/07nov-bonusscene, 83bf364, art/gen/reviews/bonus_scenes.md)

The review passed River Walk, City Park, Söder and Night, and failed Downtown and Rooftops on the join: the houses
ended on a straight line at y 160 over a flat pale 10 px stripe (the square's floor under the mid grade, its setts
smothered).

- **(a) Downtown's square floor under the back grade, done.** `town_square_floor.png` is now drawn unfaded under
  the back layer's grade (the ground plane a few metres behind Pepper): its kerb and setts show, so the band reads as
  the square's floor. `round3_downtown_join_before_after_4x.png` (and `_grey_4x`): round 2 above, now below.
- **(b) town_door on the far wall: tried, not used.** The approved door is a true-scale play-line piece: a
  140 x 432 opaque brick panel, the door with its arch 60 x 110 px (2.1 m at 46 px/m). The backdrop is at about
  13 px/m (its windows 6 x 8 px, a storey about 39 px), so the door stands 2.5 storeys tall over the houses
  (`round3_downtown_door_trial_3x.png`, a mockup pasted on the frame, which is why it covers Pepper there). Scaling
  it down is not allowed (grid rule), and the scale rule says big things go on a slower layer, not the other way. No
  approved door exists at the backdrop's scale. Options, each needs a yes: a doorway built once by rule in the
  backdrop's own colours at its scale and stamped on two or three ground floors (new art, 0 credits), or wait for
  the Downtown redesign's low rooftop rows and take their ground floor.
- **(c) A lamp post at the far left in Downtown, done.** The levels' lamp, faded as their back decoration, unlit,
  foot on y 172, with its shadow as `stage.lua` draws it.
- **(d) One approved prop behind the line in River Walk and City Park, done.** River Walk: the lamp post at the far
  left, foot on y 174. City Park: the bench at x 250 on the back lawn, feet on y 172, faded to the back haze like the
  back decoration (in River Walk it is an obstacle with its own outline; here Pepper cannot reach it, nothing has a
  collision box). `round3_riverwalk_before_after_2x.png`, `round3_citypark_before_after_2x.png`,
  `round3_downtown_before_after_2x.png` (round 2 left, now right).
- **(e) City Park's front tufts, done.** Each moved 0-3 px off the 8 px grid by the file's rng, one in five left out:
  no dot screen. `round3_citypark_tufts_before_after_3x.png`.

Nothing is on the play floor. Throws, catch rules and timings unchanged.

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
- `round2_*_3x.png`: round 2's fixes and the City Park options
- `round3_*.png`: round 3's fixes and the door trial

## Checks (final commit)

- `love riverwalk --bonus` and `--level X --bonus` for riverwalk, citypark_tall, downtown_tall, rooftops, soder and
  night: no Lua errors; every level's full round played by the autopilot (`--auto`) with the same results as before
  the change (A 14 of 15, B 13 of 15, C 13 of 14).
- Bonus tests (`love riverwalk --bonus --physics`): 23 of 23 passed (rounds 2 and 3 too).
- `tools/check_flow.sh`: 125 of 125 passed (rounds 2 and 3 too).
- `tools/check_pepper.sh`: PEPPER UNCHANGED, 3908 steps identical (rounds 2 and 3 too).
- Rounds 2 and 3: every level's round played again by the autopilot, results unchanged.
- River Walk physics (`--level riverwalk --physics`, as `Sc.paintQuay` got one option): 55 of 55 passed.

Each run with its own `XDG_DATA_HOME=$(mktemp -d)`, under `xvfb-run -a`, `SDL_AUDIODRIVER=dummy`.

## Files

- `riverwalk/bonusscene.lua` (new): the scene table, the three scenes, the front edges, Downtown's ungraded wall.
- `riverwalk/bonus.lua`: the round picks its scene from the level number; the City Park drawing moved out.
- `riverwalk/scene.lua`: `Sc.paintQuay` takes `def.quayFront` (every column the quay's kind, no road);
  `Sc.skyAndClouds` and `Sc.strip` exported. The levels draw exactly as before.
- Not touched: Pepper's files, `world.lua`, `stage.lua`, the throws, catch rules and timings.

## Questions for the owner

1. Night Harbour's round is on River Walk's promenade in morning light until Night gets its own colour script. OK,
   or should it wait for a night look?
2. Söder Hill's round is on the City Park lawn. Would you rather have Downtown's square or the River Walk quay there?
3. Downtown's quay wall is granite grey in the bonus but still violet in the level itself (the same grade). Should
   the level get the same fix?
4. Downtown's far houses have no ground floor. A doorway built by rule at their scale (new art, 0 credits), or wait
   for the redesign's rows?
