# Gate 8 review: cyclist_adult1

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Still, 84x87.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

FAIL stray: 3.8 % lone pixels (aim under 3 %) | colours: 21 colours, the play layer allows 20.

## Measurements and notes

- File 84x87 RGBA, alpha only 0/255. 21 colours, all in art/palettes/riverwalk.gpl. Ink #050a17 (navy-tinted, bench uses #000000, car1 #010102, car4 #020202: three different inks across the family).
- Wheels: ring fits a circle (rear c(16,70) r14.0, front c(68,70) r14.05, deviation +/-0.45); outer silhouette r 16.1-16.5 on every free 10 degrees; 8 spokes on 45 degree steps (6/9 px per sector), so round and even. BUT both wheels touch the frame: rear left edge at x0-1 for y60-74 (flat, about 1 px of tyre cut), front right edge at x83 for y68-74 (about 1 px cut). Rear and front wheel are not stamped identical: 42 of 188 lower-half ring pixels differ (x0-6,y72-82 and x26-31,y75-82).
- Exposed (outer) edge ink: #050a17 607 px, #21273a 64, #5a2e2a (brown) 32, #393847 4, #7d1c24 3 (spoke edges excluded). Brown, not ink: basket top x73-81,y42 and right side x78-81,y43-51; hair/chin (50,16),(49,17),(45,19),(33,20); coat back (28,31),(45,36),(47,37),(43,40),(55,39),(54,32),(64,42),(42,49). Tail reflector #7d1c24 at (1,60),(1,61) sits on the left border.
- Lone pixels 112 (8-neighbour; helmet (35-37,1-5),(43-44,1),(49-50,2-4); coat; face (50,8),(51,8),(50,14),(45,17)). Lone-pixel density (8-neighbour) per 1000 opaque px: this rider 38 (rider 2: 36), bench 16, bin 10, lamp 0; near-ink dark shades in the bike mass (#050a17, #21273a, #2b2a25, #1c1c1c, #282a36, #373737, #393847) where the bench uses #000000 plus 2 greens; 21/20 colours vs bin 14, bench 16, lamp 7. At 3x beside the bench the figure reads but is busier.
- Face (12x enlargement): brow and one eye (white + black pupil, (46-47,10-11)) present; NO nose: the profile edge is a straight line at x51 for y8-15; mouth is one #7d1c24 pixel at about (47,15) plus 2-3 tan (#a86e3e) pixels at (48-50,14-16) that read as a smudge, not lips.
- Rider art is drawn at 46 px/m (87 px = 1.89 m with bike, wheel outer diameter 33 px) and used unchanged in the 55 px/m road lane (road.lua RIDER_TOP 190). Beside the lane cars the rider is 16 % small: a 1.85 m rider at 55 px/m would be about 104 px, wheels about 39 px; here rider top (y190) equals car1 roof (y192) and the bike wheels (33 px) are no bigger than the car wheels (33 px), though a 28 in bike wheel is bigger than a car wheel. Fine on the promenade (Pepper ruler). Either accept in writing (owner) or make a lane-scale copy.
- Light is from the right/top in the art (helmet luma left/right 147/176 rider 1, 109/143 rider 2), so mirrored for the left-riding promenade bikes it is upper-left like the level; a road rider going right (unflipped) is lit from the right against the level.
- In game (docs/review/05nov/rw-traffic/board): promenade rider reads, faces and travels left correctly (basket in front, mirrored); road rider shows only rows 0-49 (y190-240): head, coat, hands, basket top; wheels and legs are below the frame.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | FAIL | Wheels not identical (42/188 ring px differ, x0-6,y72-82 and x26-31,y75-82) and both wheels are clipped by the sheet border (rear x0-1,y60-74; front x83,y68-74). |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring circle fit +/-0.45 px, 8 spokes at 45 degrees. See A1 for the 1 px border clip. |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | Lone dark/light dabs: helmet (35-37,1-5),(43-44,1),(49-50,2-4); coat (40,13),(42,13),(40,15),(39-40,16-17); face (45,17),(49,16); 5 near-ink shades mottle the bike mass. 3.8 % lone pixels by the script. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Not one ink: brown #5a2e2a basket outline x73-81,y42 and x78-81,y43-51; brown at chin (49-50,16-17), neck (45,19-20), coat (28,31),(43,40),(45,36),(47,37),(55,39); #21273a on 64 edge px. Basket top and right have no dark line. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | FAIL | Face has no nose (profile straight at x51,y8-15) and the mouth is a 1 px red + tan smudge at (47-50,14-16). Hands and feet whole. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | FAIL | Slot 84x87 and Pepper scale OK (46 px/m). In the 55 px/m lane the rider is 16 % small: roof-high with car1, wheels (33 px) no bigger than car wheels (33 px). |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, drawn flipped when riding left (road.lua flip=not right; stage.lua flip=true); basket in front, correct in the board frames. Note: light comes from the right, wrong for a road rider going right. |
| A8 | In game: only the part that shows is clean | PASS | Road: rows 0-49 show (head, coat, hands, basket top), clean apart from the face. Promenade: whole bike at 1x reads. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | FAIL | Denser than the approved pieces: 38 lone px per 1000 vs bench 16, bin 10, lamp 0; 21 colours vs 7-16; seven near-black shades. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | FAIL | Right for Pepper (1.89 m at 46 px/m), 16 % small for the 55 px/m lane (see A6). Slot 84x87 correct. |
| R2 | Layer: values on its ladder row | PASS | Ink #050a17 is the darkest, play/lane row; lighter than the foreground. (Script has no lane layer.) |
| R3 | Outline: unbroken 1 px ink | FAIL | Outline breaks: see A4 (basket top/right brown, chin/coat brown, 3 inks across the family). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels and tyres round; lines straight. (1 px cut at the border is under A1.) |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Lone dabs and mottled near-ink blacks (A3); coat is in 3 clean shades, trousers 2. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | FAIL | 21 colours, the lane/play cap is 20 (script FAIL). All colours are in riverwalk.gpl. Ink is navy-tinted, not neutral. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile with a thin basket cap; no tops, insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | FAIL | See A9: busier than bench, bin, lamp at 3x. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Red coat and white helmet read at 1x, friendly. (Face detail under A5.) |

VERDICT: FAIL (11 items)
