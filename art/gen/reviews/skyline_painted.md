# skyline_riverwalk.png, skyline_citypark.png, skyline_downtown.png (the far city under the painted sky)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at f01b75d, worktree review-sky07. Each 320 x 77, 3 colours plus alpha, built from the approved
skyline.png (unchanged). Looked at each at 4x beside the approved skyline, in game at 5x (River Walk x 1280, City Park
y 144 x 320), and in greyscale on every screen. asset_qa: WARN each (2 blotches, inherited from the source skyline).
Measured where the rim sits: River Walk and City Park 616 rim pixels, 332 with open sky above, 370 with open sky to
the left, 130 to the right (corners and the tops of right-hand slopes), 9 below; Downtown 332, top only.

## skyline_riverwalk: PASS

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Clean | PASS | Two flat tones (154,174,224 and 142,162,214), the lighter haze band at the base as the approved file has, no noise added. |
| Rim only on lit edges | PASS | Warm rim (232,187,124) on the tops and left sides, light from the upper left as the BIBLE says; right sides plain. At 5x it reads as sunlit edges, not an outline. |
| Between the sky and the far trees in value | PASS | On x 1280: sky horizon median 204, city 174 (darkest 162), far trees 167 (darkest 133). Clouds row floor 185, far city floor 145: both hold. |
| Consistent with the approved skyline and concept a | PASS | Same silhouette; concept a's lavender city with a warm rim over a cream glow. |
| Greyscale | PASS | The city sits one clean step under the glow and one above the trees on every screen. |

## skyline_citypark: PASS, with one note

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Clean | PASS | Two flat tones (196,192,226 and 184,180,216), cream rim (253,230,180), tops and left sides. |
| Between the sky and the far trees in value | PASS | On y 144 x 320: horizon 209, city 197 (darkest 185), far tree line 138. |
| Note | - | The fill is only 12 luma under the glow and is the most violet thing on the screen; in colour it separates from the amber by hue alone, a purple cut-out on orange. Not garish, but close. If the owner says so: fill about luma 186-190 and a quarter less violet (towards the horizon's hue), which keeps it above the 145 floor and makes it read as distance in greyscale too. Concept a has about 30 luma between glow and city. |

## skyline_downtown: PASS

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Clean | PASS | Two tones (204,216,236 and 192,206,230). |
| Rim | PASS | Top only, (238,242,244) on a 215 fill: barely there, right for a sun straight above; it does not read as an outline. |
| Value | PASS | Horizon 239, city 215 (darkest 205), the far roofs under it darker. Only visible above the gables at the roof tier, where it reads as a pale distant town. |

# Round 2 (reviewer, 7 Nov)

skyline_citypark.png at e6b62a4: fill (186,184,210) luma 188 and (178,176,202) luma 180, rim unchanged. On y 144 x 320:
horizon 209, city 188, far tree line about 181 (the shore haze one step darker, look.lua e4c8ae), mid trees darker
again. The city now separates from the glow by 21 luma in greyscale instead of 12 and no longer reads as a purple
cut-out in colour; the order sky, city, tree line, mid holds at 2x in greyscale on every City Park screen with a
horizon (y 144 x 0, 320, 1920, 2240, 2560; y 24 and y 0 x 0, 320, 2240, 2560). The tree line reads correctly: one clean
step under the city, still clearly lighter than the mid trees and the lamp. PASS.

skyline_riverwalk and skyline_downtown: unchanged, PASS.
