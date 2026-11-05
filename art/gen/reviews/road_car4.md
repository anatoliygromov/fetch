# Gate 8 review: road_car4

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Red hatchback, 185x77.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

PASS (no flags).

## Measurements and notes

- File 185x77 RGBA, alpha 0/255, 17 colours, all in the palette. Scale: 3.36 m x 1.40 m at 55 px/m (small hatchback, plausible); tyre about 29 px.
- Outline: only 183 of 437 edge px are ink (#020202). Others: #5a2e2a brown 69, #17181f 44, #282a36 33, #7d1c24 15, #393847 11. The ROOF at y0 is a brown (#5a2e2a) line x85-145 (61 px) on the image edge, continued by brown/salmon at (82-84,1),(146-152,1),(154-161,2); the HOOD edge x4-46,y24-40 alternates brown dashes with exposed salmon (#f78671) pixels, no ink; front-left (1-3,38-56) and rear top corner (172-184,5-40) mixed brown/dark-red.
- Pillar edges: the windscreen A-pillar x47-79,y2-23 and the rear C-pillar x164-179,y4-27 are drawn as a 1 px checker of alternating black and light-grey pixels (dotted line), not a line.
- Strays: orange (#bf6d36) 5 px smudge at (43-45,37-38) on the hood next to the lamp, single (45,24) and (108,28); headlamp is the same orange with a white pixel.
- Wheels round; front vs rear rim 308/377 pixels identical at the best shift (130 px), 69 differ in ring/hub detail; hubs have concentric rings and a speckled centre.
- Door shut-lines are 1 px #5a2e2a/#7d1c24 (decoration lines) with 1 px wobble near the bottom (x52-55,y52-61; x107-109,y49-58); rear quarter glass has a dark wedge (x157-163,y10-26) that reads as interior.
- In game: rows 0-47 show (roof, glass, handles); wheels never visible. Faces left, flipped for rightward cars.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | FAIL | Front and rear rims differ: 69 of 377 px (hub rings and speckle), minor and unseen in game. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Tyres and rims round; hub rings concentric. |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | Orange smudge (43-45,37-38), singles (45,24),(108,28); dotted checker along both pillars (x47-79,y2-23 and x164-179,y4-27); dark wedge in rear glass x157-163,y10-26. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Outline not one unbroken ink: roof y0 x85-145 brown #5a2e2a (61 px), hood x4-46,y24-40 brown dashes with exposed salmon pixels, (82-84,1),(146-161,1-2), front (1-3,38-56), rear top (172-184,5-40); only 183/437 edge px are ink. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | No faces or frames. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 185x77 = 3.36 m x 1.40 m at 55 px/m; CAR_TOP 192 as coded. |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces left, flipped when going right; no text. |
| A8 | In game: only the part that shows is clean | PASS | Rows 0-47 show roof, glass, handles; but the roof and hood edges (the visible silhouette) are the broken-outline parts (A4). |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | FAIL | Next to bench/bin/lamp the silhouette is soft: brown/salmon edges and dotted pillar lines where the approved pieces have a solid ink line. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 3.36 m x 1.40 m at 55 px/m. |
| R2 | Layer: values on its ladder row | PASS | Ink #020202 darkest; lane/play row. |
| R3 | Outline: unbroken 1 px ink | FAIL | See A4: 254 of 437 edge px are not ink. |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | FAIL | Pillars dotted (x47-79,y2-23; x164-179,y4-27); hood edge stair-steps with 1 px dashes (x4-46,y24-40). |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Orange dabs and 1 px brown seam lines on a 3-shade body (A3). |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 17 colours, all in riverwalk.gpl; darks neutral. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, no tops; (dark wedge in the rear glass noted under A3). |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | FAIL | See A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Bright red hatchback, cute, reads at 1x. |

VERDICT: FAIL (8 items)

## Round 2 (re-review of fix round 1, commits 928382c, 8ea91ce)

Red hatchback, 185x77.

Script (--layer lane --level rw): PASS



### Measurements and notes (round 2)

- Fixed round 1 defects: A1, A3, A4, A9, R3, R4, R5, R8 all fixed.
- In game: board frame rwtraffic_road_car4_lanerider2_3x.png: roof and hood now a solid black line; lane rider 2 head sits level with the roof as at car scale.

### Checklist round 2 (every item answered)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | Rims stamped: 596/612 px identical (23,63 centre, shift 130); the 16 differences are bumper/arch overlaps. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Tyres and rims round; hub rings concentric. |
| A3 | One light direction; ramps, no random dark/light dabs | PASS | Orange strays gone: the only #bf6d36 left is the headlamp (x3-10,y37-44); pillars now a black outer line with a grey trim band (x47-79,y2-23); rear glass wedge removed. Lone px 99 (9.7 per 1000). |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | PASS | All exposed edge px #000000 except 2 (#17181f at (173,62),(173,63)); roof y0 x85-145 now ink (was brown). |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | PASS (not applicable: a car has no faces, hands or frames) |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 185x77 = 3.36 m x 1.40 m at 55 px/m; CAR_TOP 192 as coded. |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces left, flipped when going right; no text. |
| A8 | In game: only the part that shows is clean | PASS | Rows 0-47 show roof, glass, handles; but the roof and hood edges (the visible silhouette) are the broken-outline parts (A4). |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | Solid ink silhouette like the bench; 9.7 lone px per 1000; 16 colours. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 3.36 m x 1.40 m at 55 px/m. |
| R2 | Layer: values on its ladder row | PASS | Ink #020202 darkest; lane/play row. |
| R3 | Outline: unbroken 1 px ink | PASS | Outline #000000 around the whole silhouette incl. roof and hood (was 183/437). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Pillar edges are stepped diagonals with a second black trim line (x56-75,y3-22) over a grey band: reads as trim, not dotted; hood edge a clean stair line. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | PASS | Body in flat shades; door seams 1 px brown decoration lines, no dabs. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 16 colours, all in riverwalk.gpl; ink #000000. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, no tops; (dark wedge in the rear glass noted under A3). |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | Crisp beside bench/bin/lamp at 1x and 3x. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Bright red hatchback, cute, reads at 1x. |

VERDICT (round 2): PASS
