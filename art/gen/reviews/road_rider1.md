# Gate 8 review: road_rider1

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. New file in fix round 1, first reviewed in round 2.

## Round 2 (re-review of fix round 1, commits 928382c, 8ea91ce)

Lane rider 1 (new), 104x102, 55 px/m, only rows 0-49 show.

Script (--layer lane --level rw): WARN, 2 blotches at (48-51,23-31), no FAIL.



### Measurements and notes (round 2)

- New in fix round 1 (SpriteCook 24 credits). 13 colours, all in riverwalk.gpl; alpha 0/255; bbox x2-101, y0-101.
- Scale in the road frame (board/rwtraffic_road_car1_lanerider1_3x.png): wagon roof y192, rider head top y190; bike lane drawn nearer so the bike wheel bottom is y292 (car y280). Rider head is about 1.2x the promenade rider (Pepper line), matching the 55 px/m cars.
- Lit from the right/top in the art (helmet luma L/R 170/192, torso 76/92). docs/art_hooks_r8.md claims "lit from the upper left": measured, it is not. road.lua draws lane riders unflipped when they go right (flip = not right), so about half of them are lit from the right against the level light.
- Merged #373737: spokes, far leg, far tubes: lighter than the black outline, reads as shade.

### Checklist round 2 (every item answered)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | Wheels stamped on one axle line: rings c(21,83) and c(83,83), r17.1, deviation -0.5..+0.4; outer r 18.4-18.6 on free angles; lower ring identical 283/394 (the rest overlaps); differences at the chain-case overlap x33-41,y86-88 and rear-left arc. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring round, 8 even spokes at 45 degrees, bbox x2-101, no border clip. |
| A3 | One light direction; ramps, no random dark/light dabs | PASS | Lone px 83 (20 per 1000); script WARN 2 blotches at (48-51,23-31) (face/neck, minor, 6 px). Helmet grey 3x3 vent (53-56,2-5), reads as a vent. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | PASS | Outer ink #000000 on 745 edge px; 5 brown/dark-red exposed px at the hand (51,46),(52,47),(55,49),(56,49),(57,50) and #373737 far-side tubes (about 25 px, x58-62,y54-72 etc.): reads as depth, not a second ink. |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | PASS | Face: eye, brow, nose bump, red lip all read at 1x and 9x; hands whole. No frames. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 104x102 = 1.85 m at 55 px/m (hooks: 102 px); wheel outer 37 px = 0.67 m, larger than the car wheels (33 px), as a bike wheel should be; rider top y190 next to car roof y192 with the lane 12 px nearer the viewer: consistent. Against Pepper (46 px/m) the lane is 1.2x, as the cars are. |
| A7 | Mirrored as the game draws it, still reads right | FAIL | Reads right when flipped (basket in front), but the light is from the right (helmet L/R 170/192, torso 76/92), against the hooks line "lit from the upper left" and the level light; road.lua draws it unflipped for the half going right, so those riders are lit from the right. Fix: relight the art from the upper left (or flip lane riders so the lit side is always left). |
| A8 | In game: only the part that shows is clean | PASS | Only rows 0-49 show (y190-240): head, coat or jacket, arms, hands, basket top; clean at 1x in the board frame. Wheels and legs are below the screen. No pedal loop needed. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | 20 lone px per 1000 (bench 16, bin 10); 13-15 colours; ink #000000 like the bench; same pixel size (1 art px). |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 1.85 m at 55 px/m; slot 104x102 as the hooks say. |
| R2 | Layer: values on its ladder row | PASS | Ink #000000 darkest; script lane layer: WARN only for blotches. |
| R3 | Outline: unbroken 1 px ink | PASS | Unbroken 1 px #000000 outline (script outline 100 %%). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round, tubes straight. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | PASS | Coat in 3 shades plus the shaded sleeve; trousers 2; no mottling. |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 13 colours (cap 20), all in riverwalk.gpl; ink pure black; darks neutral. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin basket cap, no tops or insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | Beside the bench at 3x the figure is as crisp; see A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Friendly woman in a red coat and white helmet, reads at 1x. |

VERDICT (round 2): FAIL (1 items)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. The file at 5x beside the bench and bin; in the game on River Walk x 760 at 1x, 2x and a 5x crop (my own still-vehicle hook in a local copy of tests_look.lua), colour and greyscale. Rows measured. Maker's notes read after.

Piece: riverwalk/art/scene/road_rider1.png 105 x 110, the bike lane at 55 px/m (the woman in the red coat); road.lua draws it at y 190, so rows 0-49 show.

Owner's rider checks at 5x on the whole file: seated PASS (hip on the saddle line), hands on the grips PASS (the hand at rows 51-56, x 67-72, closes on the bar end; the basket or bar at rows 55-66), facing the travel PASS (faces right, flipped by road.lua when riding left; checked both ways), limbs connected PASS, no pedal loop (only the top shows), the foot is on the pedal in the still.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1-4 | Repeated parts, wheels, light, outline | PASS | Same geometry as the promenade bike x 55/46, drawn fresh (crisp spokes, no resampling smear at 5x); one ink. |
| 5 | Face | PASS | Eye with a white, brow, nose, mouth; helmet with vents. |
| 6 | Scale | PASS | 110 px = 2.0 m with the helmet at 55 px/m: a grown-up seated; the head is bigger than the promenade riders', as the near lane should be. |
| 7 | Mirrored | PASS | Reads both ways (lane1 right, lane2 left shots). |
| 8 | In game, what shows | PASS, with a judgement | Rows 0-49: helmet, face, shoulders, upper arm. Crisp at 5x. But a bust gliding along the road with no hand and no bar is odd for a child: at 2x (lane1 and lane2 crops) it reads as a head sliding by. |
| 9 | Beside bench, bin, lamp | PASS | As crisp as the bench; script PASS / WARN (17 dirt px, 0.4 %, not visible at 5x). |
| R | Scale, layer, outline, shapes, shading, palette, view, fit, read | PASS | 18-19 colours, flat ramps, profile, reads at 1x. |

On raising the riders 6 px (the open question): no, 6 px is not enough. Rows 0-55 would show the hand's rows 51-55 as 5 px of skin at the very bottom edge and no bar: a hand reaching for nothing. 12 px (RIDER_TOP 178) shows the hand and 7 rows of the bar and basket (rows 55-61), and that is the smallest raise where the hand reads as holding something; 16 px (top 174) shows the whole basket (rows 55-66). Either overlaps Pepper's feet line by 6-10 px, which the 25 Oct rule allows for passing bikes (they ride in front of her). I would take 12 px and check at 1x that the helmet does not cut the kerb awkwardly; the kerb is behind the lane, so it should read as depth.

VERDICT (round 1, 7 Nov): PASS (art); the lane placement is a judgement for the owner, 12 px recommended.

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-chars at 3b69dbf merged into the review worktree. Re-rendered: the changed files at 5x to 8x, River Walk x 1600, 2240, 2880, City Park tall y 144 x 640, 1280, 2560, the lane riders, car 5 and the baker in game (my still-vehicle hook now reads Rd.RIDER_TOP), colour and greyscale.

RIDER_TOP 178: PASS. Rows 0-61 show: helmet, face, shoulders, the arm, the hand on the grip and the basket's top rows at the bottom edge (lane1 shot, 5x crop, colour and grey). She reads as a cyclist passing close, not a bust. The helmet crosses the kerb and Pepper's paws when they line up; the 25 Oct rule allows it for passing bikes. VERDICT (round 2): PASS
