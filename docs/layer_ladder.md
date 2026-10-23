# The layer ladder (23 Oct 2026)

Owner's rule: the layer furthest from Pepper is the lightest; each nearer layer is darker.
The full spec with every asset measured is the doc "FETCH! Asset Library by Layer" (https://claude.ai/artifact/WyS63nnKxuPnZctTCxMP4Z).

Tools: `python3 -I tools/measure_layers.py out.json` (every asset as drawn: file, fade, look shader; mapping corrected after two QA passes), `tools/layer_shots.sh out/layer_shots` (colour and greyscale frames of the three art levels).

On-screen luma 0-255 after ALL fades and the shader. Fades live in three files: scene.lua (decor 28 %, facades 40 %, roofs 45 %, railing 28 %), setpieces.lua (kiosks 28 %), arthooks.lua (vintage tram 40 %, tall fronts 28 %, spire 45 %). City Park and Downtown are played as their tall versions (levels.lua).

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
- Breaks as drawn: City Park willows lighter than the mid trees behind; winch keeper dark and outlined on the back layer (needs a 35 % fade). Downtown far roofs darker than the facades in front; plaza houses outlined and dark on the back layer; statue tagged back though its arm and hat are ledges; pedestal, stall and shelter under-outlined. River Walk: only the light pavement (owner decision 1). Batch 1: no lightness breaks; scale, layer (spire at 1.0) and slot sizes are the problems.
- Check every new asset with its in-game fade and shader, against its slot in docs/art_hooks_r8.md, at 5x beside bench/bin/lamp, and in an in-game frame in colour AND greyscale.

