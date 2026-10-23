# The layer ladder (23 Oct 2026)

Owner's rule: the layer furthest from Pepper is the lightest; each nearer layer is darker.
The full spec with every asset measured is the doc "FETCH! Asset Library by Layer" (https://claude.ai/artifact/WyS63nnKxuPnZctTCxMP4Z).

Tools: `python3 -I tools/measure_layers.py out.json` (every asset as drawn: file, fade, look shader; mapping corrected after two QA passes), `tools/layer_shots.sh out/layer_shots` (colour and greyscale frames of the three art levels).

On-screen luma 0-255 after ALL fades and the shader. Decision 3 (art/haze, 23 Oct): every load-time fade goes to the level's own haze for the layer (look.lua), never to the old cool grey (200, 210, 222). The amounts per level and layer are look.lua's `fade` (River Walk back 28 %; City Park tree line 35 %, round trees 48 %, back 20 %; Downtown roofs 70 %, facades 10 %, back 28 %); pieces with their own amount keep it (park gate 28 %, winch keeper 35 %, vintage tram 40 %, spire 45 %). Code: scene.lua Sc.haze / Sc.fadeK / Sc.fadeC / Sc.fadeData, used by scene.lua, setpieces.lua and arthooks.lua. City Park and Downtown are played as their tall versions (levels.lua).

Ladder per level, median / darkest (10th pct), pooled over each level's assets (`python3 -I tools/measure_layers.py --ladder`; the horizon is the sky's bands below y 76):

| Level | horizon | clouds | city | shore | mid | back | play |
| --- | --- | --- | --- | --- | --- | --- | --- |
| River Walk | 223/208 | 238/199 | 169/155 | 163/130 | - | 181/119 (was 176/114) | 100/2 |
| City Park | 209/199 | 239/201 | 169/157 | 166/153 (was 160/139) | 164/145 (was 143/118) | 134/88 (was 137/86) | 78/2 |
| Downtown | 237/190 | 236/195 | 175/162 | 173/161 (was 162/139) | 170/124 (was 184/154) | 158/102 (was 151/96) | 96/2 |

River Walk's back decoration has a lighter median than its far shore (light house fronts), as before; its darkest keeps the order. Downtown's far layers sit close together: its look script's shore and city hazes are darker than its mid haze, so the order holds by small steps (the skyline and the roofs are mostly behind the facades).

| Layer | Scroll x / y | Scale | Darkest (10th pct) | Max contrast | Colours | Outline |
| --- | --- | --- | --- | --- | --- | --- |
| clouds | 0.05 + drift / 0.1 (0.3 tall art levels) | free | 185 | 70 | 5 | none |
| far city | capped (max 128 px per level) / 0.1 (0.3 tall) | silhouettes | 145 | 35 | 6-8 | none |
| far shore | 0.25-0.3 / 0.3 | 12-14 px/m (window 8-12) | 125 | 60 | 8-12 | none |
| mid | 0.5 / 0.6 | ~23 px/m (window ~25) | 105 | 85 | 10-14 | none |
| water | river rows 0.3-0.55; ponds with the world | - | 75 | 160 | 20 | none |
| back (behind Pepper) | 1.0 / 1.0 | true scale 46 px/m (door ~95) | 80 | 120 | up to 20 | none |
| play | 1.0 / 1.0 | 46 px/m, near lane 55 | the 1 px outline, 100 % | full | obstacles 20, characters 24 | 1 px dark |
| front | props 1.3, code band 1.4 | ~60 px/m | median <= 40 | 40 | 3-8 | dark silhouette, rim |

- Light local colour is allowed on far layers; dark darks are not. A light obstacle must be fully outlined.
- What Pepper stands on is true scale within her 46 px jump (ledges between storeys); what is big goes on a slower layer. Exceptions: the tram shelter stays a 48 px perch; the swan boat needs mover changes to grow. True-scale buildings replace the 22 Oct "compressed architecture" rule: owner decision 2 pending.
- Dithering: none in sprites; 2x2 ordered only in code (sky band joins, path-end fades).
- Fixed on art/fixes (23 Oct): statue tagged play, winch keeper faded 35 %, plaza houses faded 28 %, pedestal, stall and shelter outlined, clean pass under 5 % lone pixels.
- Fixed on art/haze (23 Oct): City Park willows now darker than the round trees behind; Downtown far roofs now lighter than the facades; the winch keeper takes the park's warm haze, not grey.
- Breaks as drawn (before art/fixes and art/haze): City Park willows lighter than the mid trees behind; winch keeper dark and outlined on the back layer (needs a 35 % fade). Downtown far roofs darker than the facades in front; plaza houses outlined and dark on the back layer; statue tagged back though its arm and hat are ledges; pedestal, stall and shelter under-outlined. River Walk: only the light pavement (owner decision 1). Batch 1: no lightness breaks; scale, layer (spire at 1.0) and slot sizes are the problems.
- Check every new asset with its in-game fade and shader, against its slot in docs/art_hooks_r8.md, at 5x beside bench/bin/lamp, and in an in-game frame in colour AND greyscale.

