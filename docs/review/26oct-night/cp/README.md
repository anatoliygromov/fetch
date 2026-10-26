# City Park (tall): the code-only changes from the layer plan, night of 26 Oct

Branch `night/26oct-cp-code` off prod/integrate-b. 0 credits, no image service call, no art file added or changed. Plan: `docs/layer_plans/citypark_tall.md` on `night/25oct-cp-plan`. Every change is one commit with a CHANGELOG entry.

Frames: `*_before_after.png` (left before, right after, each 3x of the game's own 320 x 240 frame, from `tools/layer_frames_tall.py`), at the high camera (camera y 24, the top-of-the-world one at screen 9) and the low camera (y 144): screens 3 (x 640), 4 (x 960), 6 (x 1600), 8 (x 2240), 9 (x 2560). `x2080_camy024_lowbough_after.png` is the low bough, `x0960_camy144_lamp_after.png` the lamp off the winch man. `layers_before.json` and `layers_after.json` are the tool's per-layer numbers.

## What changed

| Plan item | Change | Where |
| --- | --- | --- |
| 3 haze | far city haze b8a0c2 to dccfe0; tree line haze c8a6ae to dcc0c4, its load-time fade 35 to 40 %; mid fade 48 to 38 % | look.lua citypark; the same constants in tools/measure_layers.py |
| 4 sky | the sky's deep blues (top 39579a) become pale blues, luma 192 at the top of the high road's sky to 204 at y 72; warm horizon kept | look.lua citypark `bands`, `above` |
| 5 leaf front | a 22 px bank of dark leaves from code along the bottom of the screen while the camera is up in the trees; gone on the path | look.lua `Look.leaves`, stage.lua; 3 new `--physics` checks |
| 8 a | walk legs: no outline, faded, darker shade of own colour | scene.lua `drawWalkLegs` |
| 8 b | walk rail 1 m (46 px, hand rope and a lower rope) | scene.lua `drawWalk` |
| 8 c | ledge x 1656-1720 y 248 drawn as the old oak's branch (not removed: Pepper stands on it) | scene.lua `Sc.drawPropArt` |
| 8 d | checkpoint lamp 976 moved to x 1028, off the winch man | maps/citypark_tall.tmx, level/tiled/citypark_tall.lua |
| 8 e | low bough's end: gentle rise into a leaf mass, no prow | scene.lua `drawLowBough` |
| 8 f | the big oak's silhouette on the far tree line, from screen 5 (camera x about 1380) | scene.lua `farOakImg`, `Sc.drawFarArt` |

## Luma (Rec.601 as the look shader; median / darkest 10 %)

The ladder, `python3 -I tools/measure_layers.py --ladder` (the art as it shows after fade and shader):

| Layer | Before | After | Target |
| --- | --- | --- | --- |
| far city | 169 / 157 | 191 / 178 | about 191 |
| tree line | 166 / 153 | 181 / 169 | about 181 |
| mid trees | 164 / 145 | 154 / 132 | about 154 |
| back | 134 / 88 | 134 / 88 | 134 |

The game's own frames (`layer_frames_tall.py --ids`):

| Layer | Camera y 0 before | after | Camera y 144 before | after |
| --- | --- | --- | --- | --- |
| sky | 158 / 111 | 202 / 199 | 158 / 130 | 204 / 199 |
| far city | 169 / 157 | 191 / 178 | 169 / 157 | 191 / 178 |
| tree line | 166 / 153 | 181 / 167 | 167 / 153 | 181 / 169 |
| mid | 164 / 145 | 154 / 132 | 164 / 148 | 154 / 135 |
| back | 138 / 108 | 138 / 108 | 134 / 100 | 134 / 105 |
| play | 91 / 20 | 80 / 20 | 87 / 20 | 87 / 20 |
| front | none | 25 / 25, 2 % of the screen | 23 / 15 | 23 / 15 |

The order is now sky 202, far city 191, tree line 181, mid 154, back 138, play 80 to 87, Pepper darkest. The play median at the high camera falls from 91 to 80 because the 1 m rail's dark ropes belong to the walk's play piece. The sky (pale blue, 202) is now close to the clouds' darkest 10 % (201): the clouds read by their warm cream hue and their light tops, not by value; the owner may prefer a slightly deeper sky.

## Checks

On this branch against the base (prod/integrate-b), each with its own data folder: see the commit message of the last commit and the report. The Tiled check needs `PATH=/tmp/v/bin:$PATH` here (the system python3 has no PIL).

## Skipped, and why

- **8 a, the gate's outline:** the dark edge is baked into the approved art file `riverwalk/art/scene/park_gate.png` (96 % of its edge pixels are under luma 60). Changing it touches approved art. Needs the owner's yes and a hand fix in Aseprite.
- **8 g, leaf piles without an outline:** the same: the outline is in the approved files `park_leaves.png` and `park_leaves_flat.png` (every edge pixel under luma 60). Nothing in the code draws it.
- **8 c, removal:** not chosen. The ledge is one Pepper stands on, so removing it changes what she stands on. Drawn as a branch instead.

## Notes for the owner

- The far big oak (8 f) is quiet by design: the mid trees (made at 107 px, 0.5 speed) stand in front of it and hide most of its lower half. Its full size comes with the new mid trees, which are not in scope.
- The haze and sky changes are in the shared `citypark` look script, so the flat City Park (the fallback level) takes them too. The leaf front, the far oak and the other scene changes belong to the tall level only.
- Lamp 1028 sits 68 px short of the goose's patrol; the checkpoint moved 52 px right.
