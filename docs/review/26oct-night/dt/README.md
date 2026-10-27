# Downtown (tall): code-only changes, 26 Oct 2026

Branch `night/26oct-dt-code`, off `prod/integrate-b`. Plan: `night/25oct-dt-plan`, `docs/layer_plans/downtown_tall.md`. 0 credits, no art file touched, no image service call.
Frames are 3x of the game's own frames (`tools/layer_frames_tall.py downtown_tall OUT --ids`), `before_*` is the base, `after_*` the branch.

## Changes (one commit each, each with a CHANGELOG.md entry)

1. **Decision 3, haze re-tune** (`riverwalk/look.lua` downtown script; `tools/measure_layers.py` copy kept in step). Far city a7bad6 to e4eaf0, far roofs b2c3d9 to bcc8da, old town row d6dee8 to b2c3d9. Fade amounts unchanged.
   Median luma in the street frame (camera y 240), from the game's own layer-id frames:

   | Layer | Before | After | Plan target |
   | --- | --- | --- | --- |
   | far city | 163 | 187 | 187 |
   | far roofs | 171 | 176 | 176 |
   | old town row | 180 | 169 | 169 |
   | back (houses behind her) | 154 | 154 | 154 |

   The order is now far city 187 > roofs 176 > row 169 > back 154 > play 92 > Pepper 58. (The far roofs read 176 in the run with the haze change alone; in the final frames they read 172 because the spire, drawn on that layer, now fills part of most frames. The spire is a darker piece than the roofs.)
2. **Decision 6a, spire from screen 1** (`arthooks.lua`, `H.SPIRE_DRIFT` 0.03). It scrolled 0.3 and was on screen only from camera x 2727. It now drifts 0.03 of the camera's way and ends where it did (its box), so it stands at x 274 on screen 1 and stays on screen to the end. `before_y240_x0000` / `after_y240_x0000`.
3. **Decision 6b, balcony railings 46 px** (`scene.lua` `drawBalcony`, was 9 px). Open ironwork (top rail, mid rail, balusters) so pickups and the wall behind show. `before_y120_x1600` / `after_y120_x1600`. Side effect: the old flat `downtown` level, a fallback, draws its balconies through the same function and gets the same railing.
4. **Decision 6c, four more front pieces** (`maps/downtown_tall.tmx` objects 284 to 287 and the regenerated export). x 1260, 2440, 3180, 3440, with the existing 620 and 1900: screens 2, 4, 6, 8, 10, 11. Existing `town_bollard` art, no new file. All at the bottom of the screen (y 221 and down) under Pepper's line (screen y 184) and under every bone (lowest at y 424); x chosen so none is near her where she swims (water x 1736 to 1848, 2560 to 2624, 2816 to 3072). The plan's first idea, x 2540, was moved to 2440 for that. `after_front_y240_x2280`.
5. **Decision 6d, loggia and galleries darker** (`arthooks.lua` `H.STONE_TINT` 0.82, a multiplier at draw time; the three art files are not changed). Median luma of the pieces in the high road frames: galleries 147 to 119, loggia 128 to 119, the front behind them 128. `before_y120_x1280` / `after_y120_x1280`, `..._x1600`.

## Skipped

- **The Downtown sky.** It follows the City Park sky call, which I do not have (no answer in the task, the City Park plan is not on this branch). The bands are a simple parameter (`look.lua`, downtown `bands`), so it is a one-line change once the call is known. Today the sky (135 at y 120 and y 240) is still darker than every far layer.
- Nothing else in decision 6 was skipped. 6d was done as a draw-time tint; had it needed pixel edits of the approved loggia or gallery art it would have been left.

## Checks

Pepper unchanged (4591 steps), flow 125/125, Tiled check passed (needs the venv python on PATH here: the system PIL is broken), `--physics` 102/102, `--qa` 0 problems in 14643 runs, `--auto` GOOD GIRL, `--flowtest` 125/125, `--lookshots` runs, `--test` tour runs, `check_curve` T1 to T4 PASS (order riverwalk, citypark_tall, downtown_tall, rooftops, soder, night, fresh out). `check_backdrop.py` fails on River Walk's old gable (58 of 70 columns), the same as the base and unrelated.
