# Gate 8 review: gull (the 24 px gull)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. The sheet at 8x on sky blue; in the game on River Walk screens 6, 8 and 10 (camera x 1600, 2240, 2880) at 2x and 8x crops, colour and greyscale. Frames measured. Maker's notes read after.

Piece: riverwalk/art/gull.png, 6 frames of 26 x 26, the bird 24 px span, 16 rows. The owner picked 24 px. The 25 Oct rejection was "holes, does not look like a bird".

| # | Item | Result | Evidence |
|---|---|---|---|
| Holes | none | PASS | No pinholes in any frame (script PASS); the outline is closed in all 6. |
| Reads as a bird at 1x | PASS | White body, grey wing, black tips, yellow bill, a dark eye in every frame; on screens 6, 8 and 10 at 1x it is a gull over the water, in grey too. |
| Scale | PASS | 24 px span in the sky over the far shore; the owner's number. Against the 46 px Pepper it is a gull in the middle distance, not a toy. |
| Outline | PASS | 1 px black (0,0,0), the same ink as the bench. |
| Crisp | PASS, one note | Flat fills, no lone noise; the colour (73,76,88) is 2 px in frame 1 and 1 px in frame 5 only (x 6-7, y 8 of frame 1): a stray shade, invisible at 1x. |
| Frames, loop | FAIL | Frames 4 and 5 are near twins (33 px differ of about 170) and then 5 to 6 is the biggest jump of the loop (203 px): wings fully down to fully up in one frame. So the downstroke takes 3 frames and the upstroke none: the flap hitches once a cycle. The script's "feet not anchored" warning is only flight. |
| Far wing | note | In the wings-up frames (1, 2, 6) the far wing is a 3 x 4 dark lump right above the head (frame 2: x 17-20, y 9-12). At 8x it reads as a crest on the head, at 1x as a dark cap. Not a fail; a 1 px gap between head and far wing would fix it. |
| Feet | note | Orange feet pixels show in frames 1-3 (x 9-12, y 20-22) and not in 4-6. At 1x a 2 px flicker under the body. Draw them in every frame or none. |

Fixes (0 credits, Aseprite):
1. Frame 5: replace with a wings-level-rising frame (frame 3's body with the wing drawn 2 px above the back, tips up) so the loop is up, half down, level, down, level, up. One frame.
2. Frames 1, 2, 6: 1 px of sky between the head's top row and the far wing's base.
3. Feet: the same 2 orange pixels in all 6 frames, or in none.

VERDICT (round 1, 7 Nov): FAIL (one frame; the still and the size are right)
