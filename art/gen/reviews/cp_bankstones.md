# Round 1 (reviewer, 6-7 Nov night)

Piece: riverwalk/art/scene/cp_bankstones.png, 24 x 7, 2 cells of 12 x 7, 3 colours, Sc.drawPondKit, bottom row on the shore.
Script: `asset_qa.py --layer back --level cp` PASS.

| Item | Verdict | Evidence |
| --- | --- | --- |
| Scale | PASS | 12 x 7 px = 26 x 15 cm bank pebbles |
| Shapes | PASS | rounded, no jaggies |
| Shading | PASS (thin) | one light row, one dark row, one fill: 3 colours. Reads as stone at 1x but flat beside the 5-shade stepping stones 30 px away |
| Outline / Palette / View | PASS | |
| Fit | PASS | crisp at 5x |
| Read | PASS | |
| floats | PASS | bottom row on the shore row (frame x 640, screen x 80-95 and 275-290, y 183) |
| consistency | PASS with a note | the concept's bank is a ramp of big rounded stones at the near corner; the game puts two small pebbles per end on the far bank. The pond no longer has the "bank slab" of the base review, but the concept's stone ramp is not there either |

Verdict: PASS. Optional: a fourth shade (a mid-light) so the stones match the stepping stones' ramp.
