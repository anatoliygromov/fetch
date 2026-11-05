# Gate 8 review: cyclist_adult1_pedal

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Pedal loop, 8 x 84x87.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

FAIL stray: 3.9 % lone pixels (aim under 3 %) | colours: 21 colours, the play layer allows 20. (--frames 84x87: no frame warnings.)

## Measurements and notes

- Sheet 672x87 = 8 frames of 84x87. 21 colours, none new vs the still (no flicker colours). Outside the leg zone (y<40) every frame is identical to the still.
- WHEEL STROBE: the 8 frames contain only 2 distinct wheel images. Frames 0,2,4,6 are pixel-identical to the still wheel; frames 1,3,5,7 are identical to each other (spokes at 22.5 degrees). Rear wheel spoke/hub pixels: 137 vs 173 (+26 %); front 102 vs 128. Even frames have crisp 45 degree spokes, odd frames stair-stepped ones; played at one frame per 6 px ridden (road.lua, 190-240 px/s) the wheel flips between two patterns 32-40 times a second and does not read as turning (wagon-wheel).
- CADENCE: 8 frames x 6 px = 48 px per pedal turn; at 190-240 px/s that is 4-5 turns a second (240-300 rpm); a wheel turn is 102 px, so the pedals turn about 2.1 times per wheel turn where a real bike turns them about 0.4 times. Legs whirl.
- Leg zone per frame: new lone pixels not in the still: f0 20, f1 30, f2 23, f3 32, f4 40, f5 30, f6 32, f7 24 (e.g. f4: (42,41),(43,42),(46,48),(48,48),(41,49),(48,49),(40,50),(45,51)); near-ink dabs inside the dark bike mass.
- Wheel clip at the border in every frame (rear x0-1,y60-74; front x83,y68-74); frames abut with no gutter, so the front tyre of frame k touches the rear tyre of frame k+1 in the sheet.
- Faces identical in all 8 frames (no boil in the face); hands whole. Near shoe leaves the pedal path unclear in f3-f4 (both feet and both legs overlap in one dark-grey mass at x38-52,y50-70).
- Basket outline and chin/coat brown edges as the still (A4). Rider art is drawn at 46 px/m (87 px = 1.89 m with bike, wheel outer diameter 33 px) and used unchanged in the 55 px/m road lane (road.lua RIDER_TOP 190). Beside the lane cars the rider is 16 % small: a 1.85 m rider at 55 px/m would be about 104 px, wheels about 39 px; here rider top (y190) equals car1 roof (y192) and the bike wheels (33 px) are no bigger than the car wheels (33 px), though a 28 in bike wheel is bigger than a car wheel. Fine on the promenade (Pepper ruler). Either accept in writing (owner) or make a lane-scale copy.
- Pinholes (1-12 px transparent islands) open and close with the legs: e.g. f2 (42,64) 12 px, f5 (41,64) 9 px, f1 (40,65) 8 px; most are gaps between leg and frame tubes but they flicker.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | FAIL | Only 2 distinct wheel images in 8 frames (even frames = still, odd = 22.5 degree pattern); wheels clipped by the border in every frame (rear x0-1,y60-74, front x83,y68-74). |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring round in all frames, 8 spokes at equal steps in both states (6 px/sector in odd frames). Weight differs between states (see A5). |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | 20-40 new lone dabs per frame in the leg zone (f4: (42,41),(43,42),(46,48),(48,48),(41,49),(40,50),(45,51)); 3.9 % lone pixels by the script. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Not one ink: brown #5a2e2a basket outline x73-81,y42 and x78-81,y43-51; brown at chin (49-50,16-17), neck (45,19-20), coat (28,31),(43,40),(45,36),(47,37),(55,39); #21273a on 64 edge px. Basket top and right have no dark line. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | FAIL | Wheel strobes between two patterns (even/odd frames), legs whirl at 4-5 turns/s, leg dabs change frame to frame; both legs merge into one grey mass in f3-f4 at x38-52,y50-70. Face and hands steady. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | FAIL | Slot 84x87 and Pepper scale OK (46 px/m). In the 55 px/m lane the rider is 16 % small: roof-high with car1, wheels (33 px) no bigger than car wheels (33 px). |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, drawn flipped when riding left (road.lua flip=not right; stage.lua flip=true); basket in front, correct in the board frames. Note: light comes from the right, wrong for a road rider going right. |
| A8 | In game: only the part that shows is clean | PASS | Road: only rows 0-49 show, so the loop (changes at y40-86) is almost invisible there; promenade shows the whole loop. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | FAIL | Same density as the still (about 38 lone px per 1000, 21 colours) plus frame-to-frame dabs. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | FAIL | Right for Pepper (1.89 m at 46 px/m), 16 % small for the 55 px/m lane (see A6). Slot 84x87 correct. |
| R2 | Layer: values on its ladder row | PASS | Ink #050a17 is the darkest, play/lane row; lighter than the foreground. (Script has no lane layer.) |
| R3 | Outline: unbroken 1 px ink | FAIL | Outline breaks: see A4 (basket top/right brown, chin/coat brown, 3 inks across the family). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels and tyres round; lines straight. (1 px cut at the border is under A1.) |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Dabs and mottled near-ink blacks in every frame (A3). |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | FAIL | 21 colours (cap 20); script FAIL. Same ink as the still. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile with a thin basket cap; no tops, insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | FAIL | See A9: busier than bench, bin, lamp at 3x. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Reads as a woman pedalling at 1x; speed of the loop is a defect (A5). |

VERDICT: FAIL (11 items)

## Round 2 (re-review of fix round 1, commits 928382c, 8ea91ce)

Pedal loop, 8 x 88x87 (promenade only).

Script (--layer lane --level rw): WARN, 1 blotch at (656-658,51-52); no frame warnings (--frames 88x87).



### Measurements and notes (round 2)

- Fixed round 1 defects: A1 (2-state wheel) fixed, A3 fixed, A4 fixed, A5 (strobe, cadence 4-5 turns/s, dabs, merged legs) fixed, A6 resolved, A9 fixed, R5, R6 fixed.
- Diff vs still per frame: 56 (f0) to 704 (f6) px, all at y40-82 (leg zone and wheels); no changes above y40; 16 colours in every frame.
- Phases: rear-wheel patch groups [0,4],[1,5],[2,6],[3,7]; front-wheel group differs between f3 and f7 only where the foot overlaps it.

### Checklist round 2 (every item answered)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | 4 wheel phases (0, 11.25, 22.5, 33.75 degrees), each used twice (frames 0/4, 1/5, 2/6, 3/7 have identical rear wheel pixels); wheels round and stamped as the still; no border clip. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring r14.05 +/-0.45 on both wheels, outer r 16.2-16.6, 8 spokes at 45 degrees; x2-85 margin, no clip. |
| A3 | One light direction; ramps, no random dark/light dabs | PASS | Lone pixels 60-69 per frame (was 106-124), no new colours in any frame; script WARN 1 blotch at (656-658,51-52) (minor). |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | PASS | Outer silhouette ink #000000 on 661 edge px; basket now inked (was brown). Only exceptions: 5 brown px (47,36),(49,37),(57,39),(45,40),(44,49) at hand/knee, and #373737 far-side frame tubes about 25 px (e.g. (51-54,44-48),(52,52),(56,55)) drawn 1 px grey over the gap: reads as depth, not a second ink on the outline. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | Face and hands identical in all 8 frames; legs read as pedalling in the 8-frame strip (near foot circles, far leg behind); no flicker colours; wheel no longer strobes between 2 images. Note: PEDAL_PX 26 gives one pedal turn per 208 px (about 1 a second at 190-240 px/s); wheel pattern advances 11.25 degrees per frame (about 8 frames/s) while the tyre really travels 91 degrees per 26 px, so the wheel crawls forward slowly: acceptable. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | Frames 88x87 (704x87 sheet), the game cuts by the still width (road.lua quads); same scale as the still. |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, always drawn flipped on the promenade (stage.lua), basket in front, correct in ingame_promenade_rider1; mirrored light comes from the left as the level. |
| A8 | In game: only the part that shows is clean | PASS | Promenade: loop shows. Road: not used (lane riders have no loop; only rows 0-49 show there). |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | 23 lone px per 1000 vs bench 16, bin 10, lamp 0; 16 colours vs 7-16; ink #000000 like the bench; same pixel size, crisp at 3x. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 1.89 m at 46 px/m; slot 88x87. |
| R2 | Layer: values on its ladder row | PASS | Ink #000000 darkest; script lane layer PASS. |
| R3 | Outline: unbroken 1 px ink | PASS | Unbroken 1 px #000000 outline (script outline 100 %); exceptions in A4 are interior tubes. |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round (fit +/-0.45), tubes straight. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | PASS | Coat in 3 shades, trousers 2, no mottling. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 16 colours (cap 20), all in riverwalk.gpl; ink pure black; darks neutral (#373737, #000000). |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin basket cap, no tops or insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | As crisp as the bench at 3x; see A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Red coat, white helmet, friendly face with nose and lip, reads at 1x. |

VERDICT (round 2): PASS
