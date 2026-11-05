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
