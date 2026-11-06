# Round 1 (reviewer, 6-7 Nov night)

Piece: riverwalk/art/goose.png row 3 (the fly row), 8 frames of 34 x 34; this round changed 2 pixels (x 9-10, y 90).
Looked at: the row at 7x, old beside new at 4x, the walking goose in game at x 960 and x 2240 y 144.
Script: `asset_qa.py --frames 34x34 --layer play` FAIL on numbers only: 24 colours (characters are allowed 24 by the BIBLE, the script caps at 20), 3.6 % lone pixels and 9 blotches which are the feather dabs, and the expected size jump at take-off.

| Item | Verdict | Evidence |
| --- | --- | --- |
| Frames clean | PASS | outlines unbroken in all 8, no halo, no blotch left in the row |
| Limbs connect | PASS | wings on the body, feet tucked under the belly in flight |
| Loop makes sense | PASS with a note | stand, crouch, wings up, then flight: down, down, up, up, down. Frames 4 and 5 are near twins (one wasted frame); the crouch (frame 2) turns the head back over the body, so it reads as "looking behind" rather than "about to jump" |
| crisp / reads / scale / owner | PASS | 34 px body, wingspan 60 px, as the gull redraw spec |

Verdict: PASS. Optional polish, 0 credits: make frame 5 a mid-stroke (wings level) and point the crouch's head forward.

# Round 2 (reviewer, 6-7 Nov night)
PASS with a note. Cell 5 is no longer a twin of cell 4: ink closed, feet tucked, the loop is down, tucked, up, up, down. But the wings are folded along the body, not level: it reads as a gliding torpedo between the strokes, a small hiccup in the flap at 1x. If it is touched again, spread the near wing out flat to the side (level stroke) and keep everything else. Script numbers unchanged (24 colours, feather dabs).
