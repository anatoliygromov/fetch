# sky_riverwalk.png (painted sky, River Walk)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at f01b75d, worktree review-sky07. File 960 x 360, 9 colours, built by tools/build_sky.py. Looked at
the file at 2x and 5x, the 13 screens of riverwalk at 2x in colour and greyscale, the horizon strip of x 640, 1280 and
2240 at 4x, the wrap at 4x, and the before (LOOK_SKY=bands) beside the after. asset_qa: WARN (2 blotches), no FAIL.

Verdict: FAIL, minor. The sky itself is the best thing on this branch: it reads as painted 16-bit art, the owner's
"technical gradient" complaint is answered. Two things stop it being finished: a stamped row of identical lobes along
the horizon that shows between the towers on every screen, and a few 1 px scraps inside the big bank.

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Painted, not technical bands | PASS | The blue has three tones joined by wavy stepped tongues (file rows 120-215), the glow is a cream field with long calm streaks, two cumulus banks of stamped lobes. Beside the bands version (x 1280) it is a different game. |
| No visible repeat on one screen | FAIL | The low bank behind the skyline is one lobe stamped in a row: 10 px wide, 4 px tall, every lobe identical, at file rows 187-197, x 0-80, 215-380 and 810-960. On screen it sits at y 67-77 and shows between the towers on x 640 (screen x 170-310), x 1280 (x 0-60 and 170-250), x 2240 (x 155-250) and on every other screen with a gap in the skyline. At 4x it reads as a row of bushes. |
| No seam at the 960 px wrap | PASS | Columns 959 and 0 differ on 0.6 % of rows, the same as any two neighbouring columns; a 320 px window across the wrap shows nothing. |
| No banding stripes | PASS | The only long straight edge (row 211-215, 61 % of columns step there) is the glow's top under the far city's solid base, screen y 91-95, hidden. |
| No lone specks | FAIL | Inside the left bank: a slanted 1 px cream stroke at x 110-120, rows 145-147, and 1 px scraps at x 75-80, rows 165-168 and x 123, row 192. asset_qa counts 10 lone pixels, build_sky --check 0.0 %, because they are 2-4 px strokes, not single pixels. At 5x they read as scratches on the cloud. |
| Lightest, calmest layer; play reads in greyscale | PASS | Greyscale 2x, all 13 screens: Pepper, the bones, the log, the bin and the route are the darkest things; the sky sits at the top, nothing of it crosses y 100. The cumulus tops at luma 246 on the 120 blue are the brightest contrast in the top half, as the old sprites were; acceptable, see the owner answer on undersides. |
| Clouds never compete with play | PASS | Banks at screen y 5-45, play line y 150-236, nothing of the sky behind the kiosks, the bench or the boat. |
| Cloud undersides at luma 185 or more | PASS | acbae2 = 186, c6cfe8 = 207, c3cfd0 = 204. |
| Motion (0.05 of the camera + 2 px/s drift) | PASS | Renders at camera x 1280, 1300 and 1320 (offsets 1 px apart, the same step the drift makes every 0.5 s): each pair is a pure 1 px shift with 0.0000 residual over rows 0-50. The two quads meet on an integer column; nothing tears. At rest the sky steps 1 px every half second, which is how a 16-bit far layer moves. |
| Tall level | n/a | River Walk is flat. |
| Consistency (summer morning, one family) | PASS | Cream-gold glow, blue-grey undersides, white tops. Same lobe and streak language as City Park and Downtown. |
| Would the owner call it technical, dirty, flat? | PASS | No. He may ask what the row of bumps behind the city is. |

Fixes for the FAILs:
1. Low bank (build_sky.py, the River Walk `banks` low entry): do not stamp one radius. Vary the lobe radius 3 to 7 px and the gap 2 to 9 px, drop every third lobe, let the baseline wander 1 to 2 rows, or drop the lobes and keep the flat bank only. Concept b's low bank is a soft flat shape, not scallops.
2. Scraps: no cloud stroke narrower than 2 px and no cloud piece under 6 px; add that to build_sky --check so the lone-pixel number cannot be 0.0 % while 2 px strokes remain.
