# Gate 8 review: cat (cat_r2 wired in)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. The sheet at 3x; Downtown tall screen 4 (camera x 1240 and the sweep x 1280, y 240 and y 120) at 2x and a 4x crop; scene.lua Sc.cat read. Maker's notes read after.

Piece: riverwalk/art/cat.png, the owner-approved cat_r2 (board 7 Nov), 8 x 3 cells of 48 x 48, 32 px sitting; wired in scene.lua (feet row 47, idle there-and-back sequence 2, 3, 7, 8, 8, 7, 3, 2; leap frames 5-8 by vertical speed; run frames 5-8).

| # | Item | Result | Evidence |
|---|---|---|---|
| Wiring | PASS | Sits on the statue's hand with the ball under its rump, faces Pepper, feet on the hand (row 47 is the paw line in the sheet). The idle sequence skips the ear-pinned frames 4-6 and returns the way it came, so the tail never jumps. Leap uses 5 up, 6 top, 7 down, 8 paws out; run 5-8 is the gallop. The shadow width follows the row. |
| Reads at 1x | PASS | A ginger tabby with big eyes and a striped tail on the statue's arm; a child says cat. |
| Scale, 32 vs 30 px | PASS | 2 px (6 %) does not read next to Pepper: in the 4x crop the sitting cat is 70 % of Pepper's height and about a third of her length, which is a house cat. Keep cat_r2; a 30 px redraw is 100 credits for nothing visible. |
| Crisp | PASS | Script WARN only: one small blotch, two colours missing in leap cells 7 and 8 (the eye white in the stretched frames, a blink), feet move in the leap row (a jump). |
| Layer | PASS | Ink darkest, play row, in front of the statue. |

VERDICT (round 1, 7 Nov): PASS
