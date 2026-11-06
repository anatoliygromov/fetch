# Downtown (tall) street props, 6 Nov (branch `art/dt-props-06nov`)

Family `dt_props_06nov`: the four board redraws (town_kiosk, town_parasol, town_pedestal, town_stall) and the triage of
town_tub, town_shopsign, town_sign (the RIVER sign) and town_crate_front. Play pieces have one 1 px ink outline
(18, 18, 26, the sample screen's ink); the RIVER sign is back decoration (no outline, faded by the game).

Built pieces: `python3 -I tools/build_dt_props.py` (parts drawn once and stamped, the sample screen's colours from
`tools/build_dt_street.py`, 0 credits). The tub's shrub: SpriteCook, see below. No box in
`riverwalk/level/tiled/downtown_tall.lua` was moved.

## Pieces

| Piece | File, size | Layer | Method | Credits | asset_qa | Card |
| --- | --- | --- | --- | --- | --- | --- |
| kiosk | town_kiosk.png 42 x 37 | play, solid 40 x 36 | built | 0 | PASS | cards/PASS_town_kiosk.png |
| parasol | town_parasol40/48/64/96.png, 14 rows; town_parasol.png = 64 | play, one-way | built | 0 | PASS (all 4) | cards/PASS_town_parasol*.png |
| pedestal | town_pedestal.png 50 x 41 | play, solid 48 x 40 | built | 0 | PASS | cards/PASS_town_pedestal.png |
| stall | town_stall.png 66 x 43 | play, solid 64 x 28 | built | 0 | PASS | cards/PASS_town_stall.png |
| tub | town_tub.png 32 x 51 (was 32 x 46) | play, solid 32 x 28 | old tub kept, new shrub from SpriteCook | 36 | PASS | cards/PASS_town_tub.png |
| apple crates | town_crate_front28/32/36.png, 21 rows; town_crate_front.png = 32 | play, solid | built (remade) | 0 | PASS (all 3) | cards/PASS_town_crate_front*.png |
| RIVER sign | town_sign.png 28 x 106 (was 19 x 38) | back, decor | built (remade) | 0 | PASS | cards/PASS_town_sign.png |
| shop sign | town_shopsign.png 47 x 112 | play, one-way arm | kept as is | 0 | PASS | cards/PASS_town_shopsign.png |

## Sizes: true scale against the boxes (46 px a metre)

- **Kiosk, KIOSK 40 x 36 (0.87 x 0.78 m).** A newspaper kiosk is about 2.6 m (120 px) and cannot be a 36 px perch; the
  gateway and the shelter fill the back line there, so no true-scale kiosk fits behind it either. The piece is the
  kiosk's ice cream chest freezer at true size (0.87 x 0.8 m): white lid with a handle, blue enamel, a pale blue card
  with three ice creams (a cone, an orange lolly, a choc ice; no text), a rubber bumper, two castors.
- **Parasols, 7 boxes 40, 48, 64, 96 wide (0.87 to 2.09 m), canopies at y 354 to 404.** A real cafe parasol is 2.0 to
  3.0 m across (92 to 138 px) with its canopy edge about 2.1 m up (97 px). The boxes are narrower and lower (the two
  terrace ones 62 px up, 1.35 m; the springy one at x 1512 only 20 px). Not moved: Pepper's jumps. Each canopy is now
  exactly its box's width (before: one 64 px file for every box, so the 96 px box was a third invisible and the 40 and
  48 px boxes had canopy hanging past their ends). 8 px panels, a scalloped valance, rounded shoulders.
- **Pedestal, 48 x 40 (1.04 x 0.87 m):** true scale for a plinth. Red granite (Stockholm's statues stand on it): a
  moulded cap, the die with a sunk panel and a bronze plaque with a dog's paw in relief, a base course.
- **Stall, counter 64 x 28 (1.39 x 0.61 m).** A market stall's counter is 0.8 to 0.9 m (37 to 41 px). The box is 9 to
  13 px low; not moved (the beat sheet's 28 px hop up to the awning). A pine top board on a green planked front, three
  crates of apples, carrots and lettuces behind her on the counter's back (14 rows, 0.3 m).
- **Tub, 32 x 28 (0.70 x 0.61 m):** true scale. Its sprig was 17 px (0.37 m) and thin. Now a clipped round box shrub
  31 x 23 px (0.67 x 0.5 m) over the old tub, which is kept pixel for pixel.
- **Apple crates, 16 px pitch (0.35 m), 28 to 36 wide (0.6 to 0.78 m):** true scale for a produce crate. Remade in the
  bread crates' build (town_crates70): the same pine, rails, hand slot and openings, apples (5 px, one drawn once) in
  the openings and their tops 3 rows over the rim. One file per box width (the 36 px box had a 32 px crate, the 28 px
  box a crate 4 px too wide).
- **RIVER sign:** was 38 px (0.83 m) with a 19 px plate and an ink outline (decoration must not have one). Now a
  pedestrian sign post 2.3 m (106 px) with a blue plate 0.61 x 0.28 m (28 x 13): a white wave and an arrow, no text.
  It reads over Mia's head at the river stairs.
- **Shop sign (kept):** arm 96 px up (2.1 m), plate 26 x 12 (0.57 x 0.26 m): true scale, crisp, 1 px outline, asset_qa
  PASS. The pretzel is drawn as two thin gold rings; a candidate for a later hand fix, not a fail.

## The tub's shrub (SpriteCook, 36 credits, 2 paid jobs on town_tub, 1 retry in the family)

1. `town_tub@1106-185500`, Nano Banana 2.1 1K on the 256 blockout with Pepper at 1x, 24 credits: both variants came
   back with Pepper at 1x but the tub 78 px and 59 px wide for a 32 px box (2.4x and 1.8x, not integer).
   Rejected on size (never scaled). Renders: `art/gen/renders/town_tub_n6a.png`, `_n6b.png`.
2. Retry 1, one input changed (the model): `town_tub@1106-185640`, Pixel Engine Image at exactly 32 x 51, 12 credits.
   Variant a: a crisp round shrub on a tub seen a little from above. Its rows 0-22 (the shrub only) are cut 1:1 onto
   the old tub (`art/source/town_tub/build_tub.py`: its pure black ink made the tub's ink, three rare greens merged into
   their ramp; every changed pixel in `edits.json`, source `town_tub.aseprite`). Variant b was a three-quarter view.

## Code (scene.lua Sc.drawPropArt, stage.lua)

- PARASOL and CRATES pick the file of the box's width and draw it at x0 - 1 (the old files stay as the fallback).
- A parasol with no table under it stops its pole at the street when it stands on the pavement (the springy one at
  x 1512 ran through the pavement to the bottom of the screen); over water it still runs down into it. `Sc.world` is set
  in stage.lua for this. The pole has a lit left column.
- PEDESTAL draws at x0 - 1, y0 - 1 when the art is the box + its ink. TUB stands the art's bottom on the box's bottom.

## Frames

`frames_before/` (base dff15cf) and `frames_after/`: the street camera (y 240) at x 280, 560, 1060, 1260, 1880, 2200,
2560, 2760, 3260 (`tools/dt_sample_frames.sh`). Not touched here: the tables, awnings, houses, door, gate and bollards
(another track).
