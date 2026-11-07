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

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. Every frame looked at at 5x and the leg region at 8x, the still at 5x beside the bench and bin, in the game at 1x and 2x (my own LOOK_BIKE shots on River Walk x 760), colour and greyscale. Shoe positions measured per frame (the shoe colour's lowest cluster). Script run on the still and the sheet (--frames). Maker's notes read after.

Piece: riverwalk/art/scene/cyclist_adult2.png 88 x 87; the pedal sheet cyclist_adult2_pedal.png (8 frames, frame 1 is the still pixel for pixel; only the leg region x 6-79, y 44-82 and the spokes change between frames).

Owner's rider checks at 5x, every frame:
- Seated on the saddle: PASS. The hip sits on the saddle line (saddle top row 43); the saddle shows behind the hip in every frame.
- Hands on the grips: PASS. The arm runs shoulder to bar, the hand closes on the grip at the bar end, all 8 frames (the arm does not move).
- Feet on the pedals: PASS. The near shoe sits on its grey pedal in all 8 frames; the far shoe shows at the opposite phase where the near leg does not hide it (frames 3 and 7 show both shoes; the far shoe is hidden by the near leg and the chain case elsewhere, which is right.
- Facing the direction of travel: PASS. Drawn facing right, the game flips her to ride left on the promenade; face, basket and bike agree.
- Limbs connected: PASS. Hip to knee to shoe is one run of pixels in every frame; no gap at the knee or ankle at 8x.
- Loop physically sensible: PASS. See below: a 16 px circle, clockwise seen from the near side, one turn in 8 frames, the knee rises when the foot is at the top.

Pedal loop (near shoe, x,y at 1x): f1 (47,72) front, f2 (45,77), f3 (40,79) bottom, f4 (35,77), f5 (33,72) back, f6 (35,67), f7 (40,65) top, f8 (45,67). A 14 x 14 px circle, clockwise, one turn in 8 frames; no repeats, no pop.

Checklist: scale PASS (85 px with the helmet, 1.85 m seated at 46 px/m, wheels 31 px = 0.7 m; next to Pepper a grown-up on a town bike); layer PASS (ink darkest, play row); outline PASS (one ink, unbroken); shapes PASS (wheels round, spokes even, tubes straight); shading PASS (3 shades per material, light upper left; the script's 0.3-0.4 % noise is the shoe and cuff edges, not visible at 5x); palette PASS (19 colours); view PASS (profile); fit PASS (as crisp as the bench at 5x); read PASS (a cyclist at 1x, cute).

Notes: Same chain case note as cyclist_adult1. The top tube is drawn over the thigh in frames 1-4 (x 44-66, y 60-63): it reads as the tube in front of the leg, which is right for the far side only; at 1x nobody will see it. The jeans (88,124,166) read clearly against the blue frame; good.

VERDICT (round 1, 7 Nov): PASS
