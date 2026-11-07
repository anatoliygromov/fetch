# Round 1 (reviewer, 7 Nov)

River Walk, branch day/07nov-ground at fc03880, worktree review-ground07. 13 frames (`LOOK_SWEEP=1 LOOK_STEP=320`, 4048x240), 2x contact sheet in colour and greyscale, every frame at 3x, joins at 6x to 12x. Pieces: art/gen/reviews/rw_kennel.md, rw_ground_reverts_07nov.md, ground_joins_07nov.md (join ids RW-a to RW-t).

## Screen-by-screen (camera x, y 0)
| x | Verdict | What is wrong |
| --- | --- | --- |
| 0 | FAIL | the kennel: Pepper floats 5 to 7 px over the roof slopes when she stands on the peak (rw_kennel 11). The garden, lawn, path and pickets PASS. RW-j: the water meets the paving in a straight row behind the railing (screen x 184-320, y 171). |
| 320 | FAIL | RW-j, the whole width: the paving's top row straight on the water, no coping or wet line. Birch foot and lamp base fine. |
| 640 | FAIL | RW-j between and beside the kiosks (screen x 0-100, 170-250). Kiosk feet weak (a dark row only). Grit box fine. |
| 960 | FAIL | RW-j across the screen. Lime foot and planters fine. |
| 1280 | PASS | stone steps, the quay-end cap, the pontoon in the water, the mooring lines. |
| 1600 | PASS | the tug in the water, the second quay's cap with the ripple. |
| 1920 | FAIL | RW-n: the dark lens under the pier's plinth reads as a hollow (screen x 20-148, y 190-200). The slanted shadow on the paving is right. |
| 2240 | PASS | rowboat, jetty legs in the water. |
| 2560 | PASS | rowboat, quay cap at the right edge. |
| 2880 | FAIL | RW-j on the lower quay (screen x 0-120, y 199). The steps and the kerb return with quoins and shadow PASS. Minor: a 6 x 5 px dark blob on the road by the kerb return (screen x 157-162, y 204-210) reads as dirt. |
| 3200 | FAIL | RW-j across the screen. |
| 3520 | FAIL | RW-j across the screen. |
| 3728 | PASS | the door houses and the cafe on their plinths, Mia on the paving. |

9 of 13 fail, 8 of them for the same join (RW-j). Fix RW-j once in Sc.paintQuay and 7 screens pass.

## Also seen (not failed here)
- road.png fails asset_qa (noise 3.3 %, blotches 10.9 %): it is the texture the owner asked back. If he calls it dirty later, the gate already says why.
- The quay-end reflection is 1 to 2 px and barely reads; fine.
