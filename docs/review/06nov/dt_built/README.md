# Downtown (tall): built redraws and hand fixes (art/dt-built-06nov, 6 Nov 2026)

Art track 2 of the 6 Nov run. The board's calls of 25 Oct on Downtown pieces that are drawn in `downtown_tall`:
redraws BUILT from parts (`tools/build_dt_built.py`) and fixes BY HAND, by rule (`tools/fix_dt_06nov.py`, every changed
pixel in `art/source/<name>/edits.json`). 0 credits, no image service. Sources: `art/source/dt_built/*.aseprite`,
`art/source/<name>/<name>.aseprite` (with `<name>_before.png`). Palette: `art/palettes/downtown.gpl` v2 (154 colours;
the new ramps count only with the owner's approve).

Frames: `frames_before/` (preview/05nov-night) and `frames_after/` (this branch), the same camera spots
(`tools/dt_sample_frames.sh`, x 0, 330, 640, 980, 1440, 1700, 2260, 2950, 3080 at camera y 240, 120 and 0).
Each card's in-game frame is `frame_<name>.png` (two spots side by side). Cards: `cards/` (`tools/qa_card.py`).

| Piece | Board call | Layer, size | Method | asset_qa | My 5x look |
| --- | --- | --- | --- | --- | --- |
| town_facades | redraw | mid, 806 x 210 | built: the old town row at 23 px/m (window 1.0 x 1.5 m, storey 3.0 m, ground floor 3.3 m), seven houses in four plasters, stepped, bell and pediment gables, a mansard with dormers, a tiled roof; one window, door, shop and attic part stamped | PASS (on screen 148 / 175 / 216 at the game's 25 %) | crisp, every window identical, reads as houses across the square |
| town_roofs | redraw | shore, 524 x 254 | built: far roofs at 13 px/m (windows 8 x 12), tiled and copper roofs with dormers and chimneys, a copper spire and a lantern tower | PASS (185 / 197 / 200 after the 70 % fade) | clean, quiet, lightest of the town layers |
| town_door | redraw | back, 140 x 432 | built from the street's front parts: Pepper's home at the start, a round-arched oak door 2.1 m (97 px) with a fanlight and a knocker, a window with geraniums, the upper storeys of every front | PASS | matches the sample screen's fronts pixel for pixel above the ground floor |
| town_tramshed96 | redraw ("look at the size in the scene") | back, 160 x 161 | built: screen 10's courtyard gate at 3.5 m, the sample screen's gateway (3 m) in a plastered courtyard wall | PASS | same arch as screen 7's gateway; flat wall, stone coping |
| town_gatestep96 | (new: the GATE's perch) | play, 98 x 37 | built: the gateway's granite doorstep, two courses, outlined, on exactly the 96 x 36 box | PASS (103 median, as the crates) | mid-tone, closed outline |
| town_house3 | redraw | back, 52 x 118 (slot kept) | built in house 1's window and storeys, stepped gable, at the fixed houses' value | PASS | clean; small like houses 1 and 2 (see below) |
| town_bollard | redraw | front, 16 x 54 | built by rule: a cast-iron bollard 0.9 m at 60 px/m, domed cap with a rim light, collar | PASS (median 28, was 41: FAIL) | dark silhouette, simple |
| town_house1 | fix (outline, contrast) | back, 54 x 118 | hand fix by rule: black silhouette outline to the material's own shade; glass +9, frames -21 luma; every colour x 0.66 to the sample screen's back value (on screen 158, was 201) | PASS (was WARN: contrast 137, 100 % dark edge) | no ink edge; sits with the fronts behind |
| town_house2 | fix (outline, contrast) | back, 58 x 126 | hand fix by rule: black and near-black silhouette pixels and the cornice's black lip to the plaster's darker shade | PASS (was WARN: 42 % dark edge) | no ink edge, value already the fronts' (157) |
| town_awning64 | fix | play, 64 x 18 | hand fix by rule: vertical stripes 8 px, red and cream in turn, one stamped tongue per stripe, rail and outline kept | PASS | even stripes and tongues |
| town_awning80 | fix | play, 80 x 18 | the same rule and the same pixels as awning64; its two reds made one | PASS | matches awning64 |
| town_table_front | fix | play, 50 x 26 | hand fix by rule: top and legs mid-tone in their own blue and steel ramps (about 110, was 40: darker than Pepper), the legs' edges and the top's underside the ink outline | PASS | closed outline both sides of each leg |

## Code
- `riverwalk/arthooks.lua`: `H.freeGate`, `drawTownGateways` and `drawTownPerches` draw screen 10's gate and doorstep
  (a GATE with no house front); `townPiece` skips that GATE's old piece. tramCode and cargoCode untouched.
- `riverwalk/scene.lua` `courtyardGate`: the flat Downtown keeps its code gate when `town_tramshed96` is the tall gate.
- `tools/asset_qa.py` SLOTS for the twelve, town_door a building; `tools/measure_layers.py` town_tramshed96 back
  (faded 28 %), town_gatestep96 play; `tools/make_palette.py` downtown v2.

## For the owner (notes, not changed)
- **The plaza houses are still a quarter of true scale** (doors 0.55 m) in front of the true-scale fronts: the layer
  plan's decision 2a (true-scale shop fronts, balconies as canopies) is his open call. Houses 1 and 2 are fixed as
  called (no outline, contrast) and now sit at the fronts' value; house 3 is rebuilt at its slot to match them.
- **The old town row at true scale fills the street camera's sky.** Its gables run past the top of the screen on the
  street, so the far roofs and Riddarholmen's spire show only when the camera is up (the high road, camera y 120 and
  0: frames `frames_after/*_y120_*`, `*_y000_*`). On the tall street (x 1180-2480) the fronts already hid them. Option
  if he wants the spire on the street camera: sink the row 30 px (its doors half hidden behind the pavement).
- Screen 10's gate stands free in a courtyard wall (no house there); its perch is a granite doorstep, not crates (the
  sample screen's one crate size does not fit 96 px).
- The balconies, their railings and the springy awning's coil are code-drawn and belong to the roof route track.

## Review round 1 (gate 8, 146ed3f: 10 of 12 PASS) and what changed

| Finding | Change (tools/fix_dt_06nov.py, tools/build_dt_built.py; every pixel in edits.json) |
| --- | --- |
| town_house1: black dots on both roof slopes and the feet; black door jambs and sill; wall mottle (291 px of 119,121,104) | every black pixel left takes the darker shade of the nearest material within 8 px; the wall's two dirt colours become the one wall colour; the step's two leftover ends the wall shade. No pixel under luma 20 |
| town_house2: near-black pixels at the gable shoulders, cornice ends and foot; a stray pixel in the attic window's left pane (26,15) | the same black rule; (26,15) the lining's colour, so the lining runs one colour down the pane's left |
| town_tramshed96: the beige courtyard wall with a window, seen over the doorstep, read as a hut in the arch | the passage redrawn: dark, its vault and left reveal darker, and at its end a smaller arch of daylight (a sunny wall, a bush, lit cobbles), no window. Opening and sizes unchanged |
