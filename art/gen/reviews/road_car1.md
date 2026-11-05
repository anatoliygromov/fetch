# Gate 8 review: road_car1

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Navy estate, 241x88.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

PASS (no flags).

## Measurements and notes

- File 241x88 RGBA, alpha 0/255, 18 colours, all in the palette. Ink #010102 on 708 of 730 edge px; others: #373737 tail-light edge (227,8),(228,9),(229,10),(229,11),(230,13),(231,15); #21273a 14 px scattered ((113,4),(100,7),(73,22),(67,26),(19,36),(2,47),(239,64)...); #1c1c1c (234,24),(235,68). Roof rack touches y0 (ink).
- Scale: 241 px = 4.38 m, 88 px = 1.60 m at 55 px/m (estate, plausible); tyre diameter about 33 px = 0.6 m.
- Tan #c0ac8e (303 px) glint lines on a navy body: shoulder line y35 is broken into 11 dashes x114-206 (gaps at 126-127,131-135,142,144-153,156-159,161-164,168,171,182); roofline y7 x110-190; hood streaks x6-60,y31-43 with stair-step jaggies. Roof rack top strip (x105-190,y0-2) has white/blue/grey dabs. Headlight is a 2-tone beige blob (x4-12,y40-47).
- Wheels round (symmetric about the centre, tyre sides equal). Front and rear rims stamped from one drawing but not pixel-identical: 366/484 pixels within r12.5 match at the exact shift of 149 px; 118 differ in the spoke/hub area (x40-55,y59-63; x41-55,y62-63...). Hubs have a dark/mid speckle in both.
- In game: Rd.CAR_TOP 192, so rows 0-47 show (roof rack, glass, handles, belt line); wheels (rows 54-87) are below y240 and never seen. Car art faces left and is flipped for rightward cars; no text, symmetric enough to mirror. Light is from the top.
- Lone pixels 188 per 15149 opaque = 12 per 1000 (bench 16): comparable.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | FAIL | Front and rear rims not stamped identically: 118 of 484 px differ (x40-55,y59-63 and hub), minor and unseen in game. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Tyres round and symmetric; five rim spokes evenly spaced (5-fold star). |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | Tan glints broken into dashes: shoulder y35 x114-206 (11 dashes), roofline y7 x110-190, hood x6-60,y31-43; rack dabs x105-190,y0-2. Reads as dirt streaks on a navy body. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Minor: tail-light edge (227,8)-(231,15) is #373737 not ink (6 px); 16 scattered #21273a/#1c1c1c edge px. Rest unbroken 1 px #010102. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | No faces or frames. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 241x88 = 4.38 m x 1.60 m at 55 px/m; slot and CAR_TOP 192 as the code uses; script slot PASS. |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces left, flipped when going right; no lettering, rear light and headlight read both ways. |
| A8 | In game: only the part that shows is clean | PASS | Rows 0-47 show: roof rack, glass, mirrors, handles; clean. Wheels never visible. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | At 3x beside bench and bin the car is as crisp: 12 lone px per 1000, 18 colours; same pixel size. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 4.38 m x 1.60 m at 55 px/m. |
| R2 | Layer: values on its ladder row | PASS | Ink #010102 darkest; lane/play row. |
| R3 | Outline: unbroken 1 px ink | FAIL | See A4 (tail-light edge, minor). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Rim and tyre round; panel lines straight; roofline clean. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Glint lines broken and jaggy (A3); body panels in 3 flat shades otherwise. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 18 colours (cap 20), all in riverwalk.gpl; darks neutral. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, no tops; glass is flat blue-grey, no interior. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | Crisp beside bench/bin/lamp at 1x and 3x. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Friendly dark estate, reads at 1x. |

VERDICT: FAIL (5 items)
