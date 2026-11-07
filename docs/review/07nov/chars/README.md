# Track CHARS, 7 Nov 2026: vehicles, animals, bones, hint pictures

Branch `day/07nov-chars`. The owner's board notes of 7 Nov, acted on. SpriteCook 178 credits (track budget about 700):
riders 64, lane riders 64, gull still 24, gull flap 26. Everything else built by rule, 0 credits.

## What changed

| Board id | Owner said | What I did | File(s) | asset_qa |
| --- | --- | --- | --- | --- |
| road_car1_v2, road_car4_v2 | redraw | Built by rule on the old cars' own silhouettes (`tools/build_cars_n07.py`): one body polygon, arches cut out, a 5-step paint ramp, glass with one glint per pane and a driver, black rubber and pillars, one wheel stamped twice, one ink outline | road_car1.png 243 x 89, road_car4.png 187 x 78 | PASS |
| road_car2_v2, road_car3_v2 | needs clean up in details | Same builder (van, taxi with roof sign) | road_car2.png 244 x 103, road_car3.png 248 x 94 | PASS |
| road_car5_v2 | wheels need some work | Only the wheels: the family wheel stamped at the old axles, every pixel in `art/source/road_car5/edits.json` (`tools/fix_car5_n07.py`) | road_car5.png | PASS |
| cyclist_adult1_v2 / 2_v2, road_rider1_v1 / 2_v1, cargo_bike_06n, cargo_bike_pedal_06n | terrible details / redraw / total rework, stray pixels | Split into parts (`tools/build_bikes_n07.py`), like the approved rowing boat: riders cut 1:1 from GPT 2.5 renders (4 px grid, 95-96 % clean cells, Pepper 52 x 38 in the cut), legs keyed per pedal frame (hip on the saddle, feet on the pedals), bikes built by rule, rider + bike one sprite per frame | cyclist_adult1/2 (+ _pedal, 8 frames), road_rider1/2 105 x 110, cargo_bike (+ _pedal, 8 frames) | PASS or WARN (noise 0.3-0.5 %) |
| rw_ferry_v2 | terrible details | Rebuilt by rule on the same lines (`tools/build_ferry_n07.py`): four identical windows, a round 8-band lifebuoy, a panelled door, fenders, anchor, pinstripe, wheelhouse windows and trim | ferry.png 252 x 79 | PASS |
| gull_size_n0607 | 24 | Pixel Engine still at 24 px span (variant c of 4), its flap animated at 1x, cleaned by rule (`tools/build_gull_n07.py`): no holes, the outline closed, the still's bill in every frame | gull.png 6 x 26 x 26 | WARN (flight leaves the ground) |
| cat_size_n0607 | 30 | Wired the approved cat_r2 (board: approve) from `art/animals-r2`, 0 credits | cat.png 8 x 3 x 48 x 48 | WARN |
| bones_06n | chunkier, more distinctive | Built by rule (`tools/build_bones_n07.py`): a double-knob bone 15 x 9 (was 11 x 6), outline, highlight, shade; gold the same shape | bone.png, bone_gold.png | PASS |
| hint_bubbles_06n | design clearer, dog more distinctive, dirty | Pepper's hint poses rebuilt by rule (`art/source/ui/v8/tools/hintdog_n07.py`): a 12 x 8 head with a white eye, her pink bandana as a clear triangle, one ink outline; the cream rim and the drop shadow (made for the old dark bubble) removed | 14 pic_*.png | layout checks PASS on all 53 hint frames |

## Files here
- `cards/`: qa_card for every piece (5x beside bench, bin, lamp; in-game frame in colour and grey), GIFs of the loops.
- `frames/`: before | after in game, colour above, greyscale below, at 1x and 3x; `_after_1x.png` the plain frame.
  - `promenade_rider1_bin`, `promenade_rider2_bin`: a rider passing the bin next to Pepper.
  - `cargo_over_crates_pepper_on_top`, `cargo_street_pepper_near_lane`, `cargo_at_gate_depot_clip`: the baker.
  - `road_*`: the cars and lane riders in the near lane (only their top rows show, as before).
  - `ferry_gull_screen6`, `bones_kiosks`, `cat_statue`.
- `riders_all_frames_5x.png`: every rider-and-bike frame at 5x (the two promenade loops, the cargo loop, the two lane stills).
- `hints/`: before | after hint frames at 4x and all 14 pictures at 5x (before above, after below).

## Numbers
- Cars at the lane's 55 px/m on the old silhouettes; 20 colours each; wheels R 19 (estate, van), 18 (taxi), 15 (hatch).
- Promenade bikes at 46 px/m: wheels 31 px, hubs 51 apart, saddle top 43 px, crank 7 px, a pedal turn in 8 frames, spokes 11.25 degrees a frame. Riders 85-87 px with the helmet.
- Lane riders: the same geometry x 55/46. The render made them 1.98 m with the helmet, so the image is 105 x 110 (was 104 x 102). road.lua still shows rows 0-49: helmet, face, shoulders, the arm; the hands are just below.
- Gull 24 x 16, cells 26 x 26. Cat 32 px sitting (cat_r2). Bones 15 x 9.

## Checks
PEPPER UNCHANGED; check_flow 125/125; check_tiled PASS; check_backdrop OK; --physics River Walk 55/55, City Park tall 97/97, Downtown tall 102/102, Downtown 81/81; check_curve T1-T4 PASS.

## Open for the owner
1. **The cat is 32 px, not 30.** cat_r2 (approved) is 2 px taller than the size pick. Keep it, or a new 30 px cat (about 100 credits: a still and three 1x animations)?
2. **The baker still disappears at the courtyard gate.** His sprite is fixed (seated, arm to the grip, feet on the pedals, facing the way he rides). But each cargo zone ends in a depot: the bike rides into its gate and is clipped at the depot line, x 1938 (zone 1) and x 3168 (zone 2), rule: drawn only right of the depot x (arthooks.lua `H.drawCargo`, scissor at depot - cam), hit box clamped at the depot (stage.lua). In the tall Downtown the GATE crates (town_crates70, x 1868-1938) end exactly on that line and cover the archway's left part (town_gateway opening columns 11-67 of 80), so he reads as riding behind the crates. Riding on is not possible (fountain basin left of zone 1, canal left of zone 2). The fix goes to the Downtown track's round 2: a clear doorway at the depot (crates off the opening, or the depots moved).
3. Bone placement: the bigger bone on screen 6 now touches the ferry's wheelhouse side (level data, unchanged).
4. The lane riders show head and shoulders only (rows 0-49). Show their hands too (draw them 6 px higher, over Pepper's feet line)?
