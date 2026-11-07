# Sky track sweep, the three levels (reviewer, 7 Nov)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at f01b75d, worktree review-sky07. Rendered every screen with the painted sky (`LOOK_SWEEP=1
LOOK_STEP=320`): riverwalk 13 frames, citypark_tall 27 (tiers y 144, 24, 0), downtown_tall 34 (tiers y 240, 120, 0), and
the same 74 with `LOOK_SKY=bands` for before/after. Looked at 2x contact sheets in colour and greyscale, horizons at
4x, the files at 5x, the wrap at 2x and 4x. Pieces: art/gen/reviews/sky_riverwalk.md, sky_citypark.md,
sky_downtown.md, skyline_painted.md, hazes_clean_07nov.md, cp_leaf_front_off.md. The maker's notes
(docs/review/07nov/sky/README.md) were read after; their ladder numbers match mine within 2 luma.

## Per piece

| Piece | Verdict | In one line |
| --- | --- | --- |
| sky_riverwalk.png | FAIL, minor | Painted and right; the stamped row of identical lobes behind the skyline shows between the towers on every screen, plus 1 px scraps in the big bank. |
| sky_citypark.png | FAIL | Horizon zone still technical: a 260 px ruler diagonal, a full-width flat lavender stripe, a row of identical scallops; a cloud sliced flat at the top of the world on 4 screens. |
| sky_downtown.png | FAIL, one defect | The cleanest sky; a cloud bank sliced flat at the top of the world on 7 screens. |
| skyline_riverwalk.png | PASS | Clean, rim on top and left edges only, one step under the glow and above the trees. |
| skyline_citypark.png | PASS | Same; note: only 12 luma under the glow and the most violet thing on screen. |
| skyline_downtown.png | PASS | Clean, rim on tops only, barely there, right for midday. |
| Clean hazes (clean 0.45 to 0.6) | PASS | The old town is no longer dirty and not candy; values unchanged, ladder holds. |
| City Park leaf front off | PASS | The high road reads finished; the trunks, deck and lamp heads carry the bottom edge. No fix. |
| Motion | PASS | Integer offsets, two quads on an integer column; renders 1 px apart are pure shifts with zero residual. A 1 px step every 0.5 s at rest. |
| Family | PASS | Morning cream, autumn amber, midday white; one hand. |

## Screen by screen (camera x, y). PASS unless listed.

River Walk (y 0):

| x | Verdict |
| --- | --- |
| 0 | PASS (the house and tree cover most of the sky; the right bank's lobe row is just visible at screen x 300-320, y 70-76) |
| 320 | PASS |
| 640 | FAIL: identical lobe row between the towers, screen x 170-310, y 67-77 |
| 960 | FAIL: lobe row at screen x 0-40 and 230-320, y 67-77 |
| 1280 | FAIL: lobe row at screen x 0-60 and 170-250, y 67-77; 1 px scraps in the bank at x 110-120, y 25-27 |
| 1600 | FAIL: lobe row at screen x 0-40 and 150-240, y 67-77 |
| 1920 | FAIL: lobe row at screen x 70-170 (right of the bridge tower), y 67-77 |
| 2240 | FAIL: lobe row at screen x 155-250, y 67-77 |
| 2560 | FAIL: lobe row at screen x 120-230, y 67-77 |
| 2880 | FAIL: lobe row at screen x 60-150, y 67-77 (behind the gull) |
| 3200 | FAIL: lobe row at screen x 180-300 (right of the birch), y 67-77 |
| 3520 | FAIL: lobe row at screen x 200-310, y 67-77 |
| 3728 | PASS (the sky is a 110 px slot left of the houses; the row is behind the Stadshuset) |

City Park tall:

| x | y 144 (path) | y 24 | y 0 (top) |
| --- | --- | --- | --- |
| 0 | FAIL: lavender stripe and glow diagonal at y 97-112; scallop row at screen x 165-250, y 96-100 | FAIL: the same horizon, 4x shows the 260 px diagonal at y 97-105 | FAIL: same horizon; cloud sliced flat at the screen top, x 200-320, y 0-6 |
| 320 | FAIL: same horizon, scallop row right of the Stadshuset | FAIL: same horizon | FAIL: same horizon; sliced cloud at x 185-320, y 0-6 |
| 640 | PASS (willow and pond; the sky is a slot at the right) | PASS | PASS |
| 960 | PASS | PASS | PASS |
| 1280 | PASS (the horizon shows only in the trunk gaps; the diagonal is behind the lime) | PASS | PASS |
| 1600 | PASS | PASS | PASS |
| 1920 | FAIL: lavender stripe full width at y 102-112 behind the pond and rope walk | PASS (the oak and willow cover it) | PASS |
| 2240 | FAIL: same stripe and diagonal, y 97-112 | FAIL: same horizon | FAIL: same horizon; sliced cloud at x 90-280, y 0-6 |
| 2560 | FAIL: same horizon at the right half | FAIL: same | FAIL: same; sliced cloud at x 180-250, y 0-6 |

Downtown tall:

| x | y 240 (street) | y 120 | y 0 (roofs) |
| --- | --- | --- | --- |
| 0 | PASS (no sky) | PASS | FAIL: cloud sliced flat at the screen top, x 255-320, y 0-12 |
| 320 | PASS | PASS | FAIL: sliced cloud at x 235-320, y 0-12 |
| 640 | PASS | PASS | FAIL: sliced cloud at x 215-320, y 0-12 |
| 960 | PASS | PASS | FAIL: sliced cloud at x 185-220, y 0-12 |
| 1280 | PASS | PASS (no sky) | PASS (no sky) |
| 1600 | PASS | PASS | PASS |
| 1920 | PASS | PASS | PASS |
| 2240 | PASS | PASS (sky slot at the right, clean) | PASS |
| 2560 | PASS | PASS | FAIL: sliced cloud at x 265-320, y 0-10 |
| 2880 | PASS | PASS | FAIL: sliced cloud at x 100-260, y 0-14, the first thing seen on the roofs |
| 3200 | PASS | PASS | FAIL: sliced cloud at x 85-245, y 0-12 |

## The two owner questions, from the art side

1. Cloud undersides below luma 185: no, keep the clouds row. The cumulus is already the highest-contrast shape in the
   top half of every screen (white 246 on the 120 blue, a step of 126; the old sprites did the same) and the row exists
   to keep that layer the calmest. The undersides at 186-187 already read as shadow at 1x (River Walk x 1280, City
   Park y 24 x 0). What concept a has and ours lacks is volume from shape, not a darker shade: fewer and bigger back
   lobes, a cleaner flat base, no second row of small front lobes. If the owner still wants the concept's weight, the
   one exception I would accept is a single underside tone down to 175 on River Walk only, where the blue behind is
   darkest (120) so a 175 shadow still floats; never on City Park, whose far city fill is 197, so a 175 underside would
   sit under the city and break "furthest lightest".
2. Retiring the cloud sprites, cloud8_v2 included, while the painted sky is on: fine visually. The painted banks and
   the sprites are two styles (lobed cream banks against white puffs); drawn together they would clash and double the
   clouds, and nothing on any of the 74 screens misses them. The files and the bands path stay, so no approved art is
   changed; what changes is what is drawn, and that goes to the owner inside the one yes on the total.

## Top 6 fixes, by impact

1. The top of the tall worlds (11 screens). In build_sky.py move the City Park bank at rows 65-90 (x 200-395) so its
   top is at row 82 or lower, and the Downtown bank at rows 35-62 (x 250-400) so its top is at row 53 or lower; or
   delete each. Add to `--check`: no cloud pixel within 4 rows of row 120 - round(camYMax x 0.3) for a tall level
   (City Park row 77, Downtown row 48).
2. The low bank behind the skyline, all three skies (every River Walk screen, four City Park screens). Stop stamping
   one lobe: radius 3 to 7 px, gaps 2 to 9 px, drop every third lobe, baseline wandering 1-2 rows; or keep a flat
   soft bank with no scallops, as concept b has.
3. City Park horizon (10 screens). Build the glow's top edge from two or three overlapping tongues with the wavy
   stepped joins the blue uses above (runs of 6-20 px), never one 260 px slope; cut the full-width lavender stripe
   at rows 222-232 into three or four streaks of 60-180 px with 1 px tapered ends.
4. Cloud interiors, River Walk and City Park. Remove the 1 px slanted scraps (River Walk x 110-120 rows 145-147, x
   75-80 rows 165-168; City Park x 134-140 rows 156-166, x 76-82 rows 170-172, x 560-600 rows 165-175). Rule for
   `--check`: no cloud stroke narrower than 2 px, no cloud piece under 6 px.
5. City Park cumulus base (rows 178-180, x 40-300): a dead-straight 2 px lavender line under 250 px of lobes reads as
   a shelf; let it wander 1 row or break it under every second lobe. Same for the River Walk left bank's base, which
   is straight for 240 px but less visible on its blue.
6. City Park far city, optional, owner's call: fill from luma 197 to about 186-190 and a quarter less violet, so the
   silhouette separates from the amber glow in greyscale (now 12 luma, concept a about 30) without the purple-on-
   orange clash.

# Round 2 (reviewer, 7 Nov)

Re-rendered all 73 screens at e6b62a4 (riverwalk 13, citypark_tall 27, downtown_tall 33; round 1 counted a map file
as a 34th) with the painted sky, 2x contact sheets in colour and greyscale, the files at 2x and 5x, the wraps at 2x,
the round 1 FAIL screens first, then the rest.

Per piece: sky_riverwalk PASS, sky_citypark PASS, sky_downtown PASS, the three skylines PASS (City Park's fill now
luma 188, a quarter less violet), clean hazes PASS (City Park tree line one step darker, order kept), leaf front off
PASS, motion PASS (unchanged code path), family PASS.

The four questions:
- Stamped repeat, ruled line or scrap left: none. The low banks are flat soft pieces in all three skies; the City
  Park glow edge is stepped tongues and four streaks; the cloud interiors are clean at 5x; 0 lone pixels in each file.
- Top of the world: clean on all 9 City Park and 11 Downtown top-tier screens; the moved banks show whole with sky
  above them (City Park y 0 x 0 and x 2240, Downtown y 0 x 2880 and x 3200 checked at 2x).
- City Park tree line one step darker: reads correctly. Horizon 209, city 188, tree line about 181, mid trees
  darker; in greyscale the three far bands are three clean steps and the tree line is still clearly lighter than
  the mid trees and the lamp.
- The flat low bank: it reads calm and painted and lost nothing. The scalloped row was never in the concepts;
  concept b's low bank is this soft flat shape. The screens are quieter behind the far city, which is what the
  clouds row wants.

Screen by screen: every screen on the round 1 FAIL list now PASS (River Walk x 640 to 3520; City Park y 144 x 0,
320, 1920, 2240, 2560 and y 24 / y 0 x 0, 320, 2240, 2560; Downtown y 0 x 0, 320, 640, 960, 2560, 2880, 3200). All
other screens PASS as in round 1. No new defect on any screen.

Remaining, optional, not blocking the owner: the 2-3 px slanted mid-tone hooks inside the River Walk and City Park
banks at 5x (lobe shading fragments; invisible at 1x). The script gates: build_sky --check OK, asset_qa PASS on
sky_riverwalk and sky_citypark, WARN (lobe-shading blotches) on sky_downtown and the skylines as before.

Verdict: the sky track is ready for the owner's one yes on the total, with the two owner questions from round 1
still open for him (keep the clouds row at 185; retiring the sprite clouds while the painted sky is on is fine).
