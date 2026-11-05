# Gate 8 review: cyclist_adult2_pedal

Reviewer: independent (did not make the asset). Branch art/rw-traffic-05nov. Pedal loop, 8 x 84x87.

## Script (tools/asset_qa.py --layer play --level rw; the `lane` layer is not known to the script, it crashes on --layer lane)

WARN stray: 3.5 % lone pixels (aim under 3 %) | blotches: 5 blotch(es) of 2-24 px in a near colour. (--frames 84x87: no frame warnings.)

## Measurements and notes

- Sheet 672x87, 8 frames. 20 colours, none new vs the still. Outside the leg zone identical to the still.
- WHEEL STROBE as rider 1: frames 0,2,4,6 are the still wheels, frames 1,3,5,7 an identical 22.5 degree pattern (rear spoke/hub px 133 vs 169, +27 %; front 83 vs 108, +30 %). Flips 32-40 times a second at the game rate; does not read as turning.
- CADENCE: 48 px per pedal turn, 4-5 turns/s at 190-240 px/s (240-300 rpm); wheel turn is 102 px. Near shoe path is a proper circle (centroids f0 (40.7,75.5), f1 (35.8,75.6), f2 (34.1,71.6), f3 (35.1,65.7), f4 (40.1,62.9), f5 (44.9,65.7), f6 (45.3,71.7), f7 (42.2,75.2)) running forward, loop closes f7 to f0.
- Leg zone new lone pixels per frame: f0 9, f1 17, f2 13, f3 23, f4 20, f5 17, f6 13, f7 13 (e.g. f3 (37,40),(33,49),(34,49),(48,49),(42,61),(38,66),(38,68)). Script WARN: 5 blotches of 2-24 px in a near colour.
- Pinholes: an 8-11 px transparent hole opens at (34,53) in f2 and f5, and 3-7 px holes at (51,63) f2,f5, (40,66) f6; they are gaps between thigh and frame but appear in single frames (flicker).
- Wheel clipped by the border as the still (rear x0-1, front x83). Frames abut without a gutter. Face and hands identical in all frames.
- Rider art is drawn at 46 px/m (87 px = 1.89 m with bike, wheel outer diameter 33 px) and used unchanged in the 55 px/m road lane (road.lua RIDER_TOP 190). Beside the lane cars the rider is 16 % small: a 1.85 m rider at 55 px/m would be about 104 px, wheels about 39 px; here rider top (y190) equals car1 roof (y192) and the bike wheels (33 px) are no bigger than the car wheels (33 px), though a 28 in bike wheel is bigger than a car wheel. Fine on the promenade (Pepper ruler). Either accept in writing (owner) or make a lane-scale copy.

## Checklist (docs/asset_qa.md gate 6, items A1-A9; art/gen/rules.json review_checklist, R1-R9)

| # | Item | Result | Position and reason |
|---|---|---|---|
| A1 | Every repeated part the same (wheels, spokes, hubs) | FAIL | Only 2 distinct wheel images in 8 frames; wheels share the border clip (rear x0-1, front x83). |
| A2 | Wheels round, spokes even, symmetric parts symmetric | PASS | Ring round, spokes at equal steps in both states. |
| A3 | One light direction; ramps, no random dark/light dabs | FAIL | 9-23 new lone dabs per frame in the leg zone (f3: (37,40),(33,49),(34,49),(48,49),(42,61),(38,66),(38,68)); script WARN stray 3.5 % and 5 blotches. |
| A4 | Outline 1 px everywhere, one ink colour, no doubled/2 px stretches | FAIL | Same second/third ink as the still (#282a36 on 73 px, #1c1c1c on 8 px) in every frame; leg zone adds #282a36 at (41,41),(36,53),(28,52)... |
| A5 | Faces, hands, feet whole in every frame; nothing boils between frames | FAIL | Wheel strobes between two patterns, legs turn at 4-5 turns/s, holes of 8-11 px open at (34,53) in f2 and f5, dabs change per frame. Foot path itself is a clean forward circle; face and hands steady. |
| A6 | Scale vs Pepper (46 px/m) and the 55 px/m lane; slot and anchor | FAIL | Slot 84x87 and Pepper scale OK (46 px/m); 16 % small in the 55 px/m lane (roof-high with car1, wheels 33 px = car wheels). |
| A7 | Mirrored as the game draws it, still reads right | PASS | Faces right, flipped when riding left; backpack behind, correct in the board frame. Light from the right (see notes) for road riders going right. |
| A8 | In game: only the part that shows is clean | PASS | Road: loop sits below y40 of the sprite (almost all off screen). Promenade: shows. |
| A9 | Next to approved bench, bin, lamp: as crisp, clean, same pixel size | FAIL | About 35 lone px per 1000 plus per-frame dabs vs bench 16, bin 10, lamp 0. |
| R1 | Scale: right size next to Pepper and in its slot (within 2 px) | FAIL | Right for Pepper, 16 % small for the lane (A6). |
| R2 | Layer: values on its ladder row | PASS | Ink darkest, lane/play row; no lane layer in the script. |
| R3 | Outline: unbroken 1 px ink | FAIL | Outline not one ink (A4). |
| R4 | Shapes: round things round, straight lines straight, no lumps or jaggies | PASS | Wheels round, tubes straight; 1 px border clip noted under A2. |
| R5 | Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks | FAIL | Dabs, blotches, mottled near-ink (A3). |
| R6 | Palette: only level-palette colours, whites white, darks neutral, within colour cap | PASS | 20 colours (cap 20), all in riverwalk.gpl; ink navy-tinted but nobody else is pure black either. |
| R7 | View: side profile as road traffic, no tops/insides | PASS | Side profile, thin cap, no tops/insides. |
| R8 | Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense | FAIL | See A9. |
| R9 | Read: cute and clear for a 7 year old at 1x | PASS | Green jacket, backpack, helmet: clear and friendly at 1x (eye/nose under A5). |

VERDICT: FAIL (10 items)
