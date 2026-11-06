# Downtown traffic family (dt_traffic_06nov), 6 Nov 2026

Branch `art/dt-traffic-06nov`. Tier A. Two hazards and set pieces on the tall Downtown's street. Before this, both were drawn in code (arthooks.lua tramCode and cargoCode, still the fallback when the files are missing).
SpriteCook: 134 credits in 4 paid jobs (art/gen/ledger.csv). The NB 2.1 cargo bike probe (24) drew the bike 1.3 to 1.8x too big and was not used.

## Pieces

| File | Size | Layer | Method | Credits | asset_qa | Card |
| --- | --- | --- | --- | --- | --- | --- |
| `riverwalk/art/scene/tram_vintage.png` | 570 x 188 | back lane (faded 40 %) | BUILT by rule at 46 px/m (`tools/build_dt_traffic.py tram`). The NB 2.1 2K render came back at half scale, so it is the design and colour reference only | 36 | PASS | `PASS_tram_vintage.png` |
| `riverwalk/art/scene/tram_vintage_wheel.png` | 4 x 31 x 31 | back lane | built by rule: 8 spokes, turned 11.25 degrees a frame | 0 | PASS | `PASS_tram_vintage_wheel.png`, `tram_vintage_wheel_row1.gif` |
| `riverwalk/art/scene/cargo_bike.png` | 116 x 88 | char (Pepper's line, obstacle) | SpriteCook GPT 2.5 Sunburst 1K on the blockout, `grid4_cut.py` (pitch 4, majority, 96 % clean cells), cut 1:1 and snapped to the Downtown palette, clean pass, wheels redrawn by rule, outline closed, then hand polish by rule (`edits_polish.json`: box planks, specks) | 24 + 48 | WARN (stray 3.0 %, aim under 3 %; the rest are the spokes) | `WARN_cargo_bike.png` |
| `riverwalk/art/scene/cargo_bike_pedal.png` | 8 x 116 x 88 | char | pixel-engine v1.5 at 1x from the polished still. Only the legs are taken (snapped to the still's colours, trousers smoothed). Wheels redrawn by rule each frame. Everything else is the still, pixel-identical | 26 | PASS | `PASS_cargo_bike_pedal.png`, `cargo_bike_pedal_row1.gif` |

## Scale
- Tram: 12.35 m body = 568 px, 3.3 m to the clerestory = 152 px, wheels 0.68 m = 31 px. The brief's 2.3 m (106 px) is the width of a Stockholm tram, not its height. At 106 px the tram would be lower than the 2.5 m (115 px) tram stop shelter. The old code box (300 x 130, `H.TRAM_W`) was too small for true scale. The lane now takes the art's own width and door (`H.tramDims()`: 570, front door middle 60 px in). The stop logic is unchanged: the door stops at the sign.
- Cargo bike: rider 1.85 m with the helmet = 85 px (88 rows with the wheels' ground row), the same as the River Walk riders. The bike is 2.5 m. The hit box (80 x 26, the front wheel and the cargo box) is unchanged.

## Frames (in game, look on, 1x)
- `frame_street_a.png`: screen at camera x 2000. The tram at its stop behind the shelter, the cargo bike beside Pepper.
- `frame_street_b.png`: camera x 2300. The tram's back half; it passes behind the canal-side houses.
- `frame_high_road.png`: the gallery (y 256). The tram's roof under the high road.

## Known
- At its stop the true-scale tram reaches past the street's last house (x 2634). Its back end passes behind the canal-side houses on the far side.
- The trousers in the pedal frames still show two greys, the pixel engine's shading.
