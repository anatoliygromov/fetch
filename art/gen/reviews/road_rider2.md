# Gate 8 review: road_rider2

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. New file in fix round 1, first reviewed in round 2.

## Round 2 (re-review of fix round 1, commits 928382c, 8ea91ce)

Lane rider 2 (new), 104x103, 55 px/m, only rows 0-49 show.

Script (--layer lane --level rw): WARN, 1 blotch at (43,56-57).



### Measurements and notes (round 2)

- New in fix round 1 (SpriteCook 24 + 24 credits, family retry). 15 colours, all in riverwalk.gpl; bbox x2-101, y0-102. 103 rows tall against road_rider1 102 and the hooks 102: 1 px over, harmless (anchored by the top row).
- The one-off script dab moves on the backpack: the backpack interior is clean (3 browns, strap) but the skin-colour rim pixels listed under A3 are a leftover of those moves and also run down the sleeve.
- Scale and road frame as road_rider1 (board/rwtraffic_road_car4_lanerider2_3x.png): helmet level with the hatchback roof, bike 12 px nearer.
- Lit from the right/top in the art (helmet luma L/R 118/156, torso 72/96). docs/art_hooks_r8.md claims "lit from the upper left": measured, it is not. road.lua draws lane riders unflipped when they go right (flip = not right), so about half of them are lit from the right against the level light.

### Checklist round 2 (every item answered)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | PASS | Wheels stamped on one axle line: rings c(21,83) and c(83,83), r17.1, deviation -0.5..+0.4; outer r 18.4-18.6 on free angles; lower ring identical 345/417 (the rest overlaps); differences at the chain-case overlap x33-41,y86-88 and rear-left arc. |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring round, 8 even spokes at 45 degrees, bbox x2-101, no border clip. |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | Skin-coloured (#f7a67f) fringe pixels along the top of the backpack (39-42,21),(37-38,22),(36,23),(46-49,22) and along the shoulder and sleeve (51,24),(52,25),(53,26)-(54,29),(55,30)-(57,33),(58,35)-(66,40),(67-71,43-45): about 40 px of orange rim light on a green jacket, from the one-off dab moves; reads as an orange outline halo at 1x. Plus light (right/top) per A7. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | PASS | Outer ink #000000 on 758 edge px; only #373737 far-side tubes (about 16 px) and one #35455f at (44,63). |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | FAIL | Face is messy at 9x: brown patch on forehead and eye socket, grey-blue eye pixels with no white, blue/grey beard speckle; the eye reads as a smudge (compare road_rider1, cyclist_adult2). Nose bump present; at 1x it reads as a bearded man but the eye is weak. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | PASS | 104x103 = 1.85 m at 55 px/m (hooks: 102 px); wheel outer 37 px = 0.67 m, larger than the car wheels (33 px), as a bike wheel should be; rider top y190 next to car roof y192 with the lane 12 px nearer the viewer: consistent. Against Pepper (46 px/m) the lane is 1.2x, as the cars are. |
| A7 | Mirrored as the game draws it, still reads right | FAIL | Light from the right (helmet L/R 118/156, torso 72/96), strongest of the four; against the hooks line "upper left" and the level; unflipped for riders going right (road.lua). |
| A8 | In game: only the part that shows is clean | PASS | Only rows 0-49 show (y190-240): head, coat or jacket, arms, hands, basket top; clean at 1x in the board frame. Wheels and legs are below the screen. No pedal loop needed. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | PASS | 22 lone px per 1000 (bench 16, bin 10); the skin fringe is the only visible dirt; 13-15 colours; ink #000000 like the bench; same pixel size (1 art px). |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | PASS | 1.85 m at 55 px/m; slot 104x103 as the hooks say. |
| R2 | Layer: values on its ladder row | PASS | Ink #000000 darkest; script lane layer: WARN only for blotches. |
| R3 | Outline: unbroken 1 px ink | PASS | Unbroken 1 px #000000 outline (script outline 100 %%). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round, tubes straight. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Orange rim-light dabs on jacket and backpack (A3). |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 15 colours (cap 20), all in riverwalk.gpl; ink pure black; darks neutral. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin basket cap, no tops or insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | PASS | Beside the bench at 3x the figure is as crisp; see A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Bearded cyclist with helmet and backpack reads at 1x (face detail under A5). |

VERDICT (round 2): FAIL (4 items)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. The file at 5x beside the bench and bin; in the game on River Walk x 760 at 1x, 2x and a 5x crop (my own still-vehicle hook in a local copy of tests_look.lua), colour and greyscale. Rows measured. Maker's notes read after.

Piece: riverwalk/art/scene/road_rider2.png 105 x 110, the bike lane at 55 px/m (the bearded man with the backpack); road.lua draws it at y 190, so rows 0-49 show.

Owner's rider checks at 5x on the whole file: seated PASS (hip on the saddle line), hands on the grips PASS (the hand at rows 51-56, x 67-72, closes on the bar end; the basket or bar at rows 55-66), facing the travel PASS (faces right, flipped by road.lua when riding left; checked both ways), limbs connected PASS, no pedal loop (only the top shows), the foot is on the pedal in the still.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1-4 | Repeated parts, wheels, light, outline | PASS | Same geometry as the promenade bike x 55/46, drawn fresh (crisp spokes, no resampling smear at 5x); one ink. |
| 5 | Face | PASS | Eye with a white, brow, nose, mouth, beard; helmet with vents. |
| 6 | Scale | PASS | 110 px = 2.0 m with the helmet at 55 px/m: a grown-up seated; the head is bigger than the promenade riders', as the near lane should be. |
| 7 | Mirrored | PASS | Reads both ways (lane1 right, lane2 left shots). |
| 8 | In game, what shows | PASS, with a judgement | Rows 0-49: helmet, face, shoulders, upper arm. Crisp at 5x. But a bust gliding along the road with no hand and no bar is odd for a child: at 2x (lane1 and lane2 crops) it reads as a head sliding by. |
| 9 | Beside bench, bin, lamp | PASS | As crisp as the bench; script PASS / WARN (17 dirt px, 0.4 %, not visible at 5x). |
| R | Scale, layer, outline, shapes, shading, palette, view, fit, read | PASS | 18-19 colours, flat ramps, profile, reads at 1x. |

On raising the riders 6 px (the open question): no, 6 px is not enough. Rows 0-55 would show the hand's rows 51-55 as 5 px of skin at the very bottom edge and no bar: a hand reaching for nothing. 12 px (RIDER_TOP 178) shows the hand and 7 rows of the bar and basket (rows 55-61), and that is the smallest raise where the hand reads as holding something; 16 px (top 174) shows the whole basket (rows 55-66). Either overlaps Pepper's feet line by 6-10 px, which the 25 Oct rule allows for passing bikes (they ride in front of her). I would take 12 px and check at 1x that the helmet does not cut the kerb awkwardly; the kerb is behind the lane, so it should read as depth.

VERDICT (round 1, 7 Nov): PASS (art); the lane placement is a judgement for the owner, 12 px recommended.

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-chars at 3b69dbf merged into the review worktree. Re-rendered: the changed files at 5x to 8x, River Walk x 1600, 2240, 2880, City Park tall y 144 x 640, 1280, 2560, the lane riders, car 5 and the baker in game (my still-vehicle hook now reads Rd.RIDER_TOP), colour and greyscale.

RIDER_TOP 178: PASS, as road_rider1 round 2: the hand on the grip shows (lane2 shot, riding left). VERDICT (round 2): PASS
