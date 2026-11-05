# Gate 8 review: cyclist_adult2

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Still, 84x87.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

WARN stray: 3.6 % lone pixels (aim under 3 %).

## Measurements and notes

- File 84x87 RGBA, alpha only 0/255. 20 colours (at the cap), all in riverwalk.gpl. Ink #050a17.
- Wheels: rear c(16,70) r14.05, front c(67,70) r14.05, ring deviation +/-0.45; outer r 16.1-16.5 where free; 8 spokes at 45 degrees. Rear wheel touches x0 (rows 66-68 at x0, y60-74 at x<=2 flat) and front wheel x83 (rows 68-74): about 1 px cut. Rear vs front ring: 172/192 lower-half pixels identical, differences at overlap points ((29,72),(32,72),(28,74),(31,74-75),(30,77),(29,80)) and the clipped rear edge ((0,72),(0,73),(5,81),(6,82)).
- Exposed edge ink: #050a17 563 px, #282a36 73, #1c1c1c 8, #393847 8, #5a2e2a 1 (spokes excluded). #282a36 on helmet right edge (49,1),(52,4),(53,6),(53,8), face (36,11), jacket (52,32),(53,33),(46,37), hand/frame (62,39),(41,41),(61,41)...; #1c1c1c on backpack (34,18),(35,18),(26,20),(22,25),(20,27). Subtle but a second and third ink.
- Lone pixels 96 (8-neighbour). Helmet top has a dotted row of alternating #393847/#373737 at (40,3),(42,3),(43,3),(45,3) reading as noise.
- Face (12x): eye is a grey (#9c9ea8/#b5b9bf) pixel group on a dark socket at about (47-49,10-12), no white, reads as a smudge; nose bump at about (50-51,14-15) is mid-grey (#5b5b5b), not skin; beard dark block (45-52,15-20) hides the mouth except one orange pixel (50,17). Forehead brown patch (38-40,9-11).
- Lone-pixel density (8-neighbour) per 1000 opaque px: this rider 36, bench 16, bin 10, lamp 0; near-ink dark shades in the bike mass (#050a17, #21273a, #2b2a25, #1c1c1c, #282a36, #373737, #393847) where the bench uses #000000 plus 2 greens; 21/20 colours vs bin 14, bench 16, lamp 7. At 3x beside the bench the figure reads but is busier.
- Rider art is drawn at 46 px/m (87 px = 1.89 m with bike, wheel outer diameter 33 px) and used unchanged in the 55 px/m road lane (road.lua RIDER_TOP 190). Beside the lane cars the rider is 16 % small: a 1.85 m rider at 55 px/m would be about 104 px, wheels about 39 px; here rider top (y190) equals car1 roof (y192) and the bike wheels (33 px) are no bigger than the car wheels (33 px), though a 28 in bike wheel is bigger than a car wheel. Fine on the promenade (Pepper ruler). Either accept in writing (owner) or make a lane-scale copy.
- Light is from the right/top in the art (helmet luma left/right 147/176 rider 1, 109/143 rider 2), so mirrored for the left-riding promenade bikes it is upper-left like the level; a road rider going right (unflipped) is lit from the right against the level.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | Wheels 172/192 identical on the lower ring, differences only at overlaps and the 1 px border clip (minor, see R4 note). |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring +/-0.45 px, spokes even at 45 degrees. 1 px clip at x0 and x83. |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | Dotted helmet row (40,3),(42,3),(43,3),(45,3); face dabs (45,10),(40,11),(36,10),(47,11); near-ink mottling in frame and trousers; 3.6 % lone pixels (script WARN). |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Second/third ink on the silhouette: #282a36 on 73 edge px (helmet (49,1),(52,4),(53,6),(53,8); jacket (52,32),(53,33); trousers/frame (46,37),(62,39),(41,41),(61,41)), #1c1c1c on backpack (34,18),(35,18),(26,20),(22,25),(20,27); brown (21,26). Otherwise unbroken 1 px. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | FAIL | Eye is a grey blob on a dark socket (47-49,10-12), nose is grey (50-51,14-15), mouth hidden in the beard except 1 px (50,17). Hands and feet whole. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | FAIL | Slot 84x87 and Pepper scale OK (46 px/m); 16 % small in the 55 px/m lane (roof-high with car1, wheels 33 px = car wheels). |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, flipped when riding left; backpack behind, correct in the board frame. Light from the right (see notes) for road riders going right. |
| A8 | In game: only the part that shows is clean | PASS | Road: head, jacket, backpack, hands show; clean. Promenade: whole bike reads. (Promenade rider 2 in the sample sits behind the kiosk awning, a placement matter.) |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | FAIL | 36 lone px per 1000 vs bench 16, bin 10, lamp 0; four near-black shades; busier than the approved pieces. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | FAIL | Right for Pepper, 16 % small for the lane (A6). |
| R2 | Layer: values on its ladder row | PASS | Ink darkest, lane/play row; no lane layer in the script. |
| R3 | Outline: unbroken 1 px ink | FAIL | Outline not one ink (A4). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round, tubes straight; 1 px border clip noted under A2. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Dotted helmet vents, face dabs, mottled near-ink (A3). |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 20 colours (cap 20), all in riverwalk.gpl; ink navy-tinted but nobody else is pure black either. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin cap, no tops/insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | FAIL | See A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Green jacket, backpack, helmet: clear and friendly at 1x (eye/nose under A5). |

VERDICT: FAIL (9 items)

## Round 2 (re-review of fix round 1, commits 928382c, 8ea91ce)

Still, 88x87 (promenade only).

Script (--layer lane --level rw): PASS



### Measurements and notes (round 2)

- Fixed round 1 defects: A3 fixed, A4 fixed (one ink), A5 fixed (nose, dark eye), A6 resolved by road_rider2, A9 fixed.
- Wheels stamped on one axle line: rings c(18,70) and c(69,70), r14.05, deviation -0.45..+0.37; outer radius 16.2-16.6 on every free 15 degrees; 8 spokes at 45 degrees; sprite bbox x2-85, so no tyre touches the border (col 0 and col 87 empty). Lower-half ring+spokes identical rear/front 306/335; the differences sit at x27-36 (chain case and fork overlap) and 1 px at the rear-left arc.
- Lit from the right/top (helmet luma L/R 117/154 (torso 83/101)); stage.lua always draws these mirrored (riding left), so the light arrives from the left like the level. road.lua no longer uses them while road_rider1-2 exist.

### Checklist round 2 (every item answered)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | Lower ring+spokes identical 306/335 px; differences at tube overlaps x27-36 and the rear-left arc 1 px. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring r14.05 +/-0.45 on both wheels, outer r 16.2-16.6, 8 spokes at 45 degrees; x2-85 margin, no clip. |
| A3 | One light direction; ramps, no random dark/light dabs | PASS | Lone pixels 42 (15.7 per 1000, was 96/36): below the bench. Helmet vent row is now 3 dark dashes (36-48,2-4), reads as vents. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | PASS | Outer ink #000000 on 609 edge px, no other colour on the silhouette (#282a36, #1c1c1c gone). Only #373737 exposed 1 px far-side tubes/spokes (e.g. (48,37),(50,45),(52,47),(36-39,53-55)). |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | Face: dark eye pixels, nose bump, sideburn and beard read; no white in the eye but the dark pair reads as an eye at 1x; mouth hidden in the beard (profile beard). Hands and feet whole. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 88x87 (padded 2 px a side, hooks doc updated); 87 px = 1.89 m at 46 px/m beside Pepper; wheel 33 px outer. The 55 px/m lane now uses road_rider1-2, so the old lane-scale defect no longer applies to this file. |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, always drawn flipped on the promenade (stage.lua), basket in front, correct in ingame_promenade_rider1; mirrored light comes from the left as the level. |
| A8 | In game: only the part that shows is clean | PASS | Promenade: whole bike at 1x, clean (docs/review/05nov/rw-traffic/ingame_promenade_rider1_1x.png). Not drawn on the road any more. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | 15.7 lone px per 1000 (bench 16, bin 10); 15 colours; ink #000000. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 1.89 m at 46 px/m; slot 88x87. |
| R2 | Layer: values on its ladder row | PASS | Ink #000000 darkest; script lane layer PASS. |
| R3 | Outline: unbroken 1 px ink | PASS | Unbroken 1 px #000000 outline (script outline 100 %); exceptions in A4 are interior tubes. |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round (fit +/-0.45), tubes straight. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | PASS | Coat in 3 shades, trousers 2, no mottling. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 15 colours (cap 20), all in riverwalk.gpl; ink pure black. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin basket cap, no tops or insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | As crisp as the bench at 3x; see A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Red coat, white helmet, friendly face with nose and lip, reads at 1x. |

VERDICT (round 2): PASS
