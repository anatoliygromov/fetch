# River Walk harbour, night of 6 Nov: water treatment, jetty piles, pontoon, kennel, road, the 208 px shift

# Round 1 (reviewer, 6-7 Nov night)

Branch `night/06nov-rw` at 4709eeb, level `riverwalk`, 13 sweep screens (LOOK_STEP 320, y 0) at 2x colour and
greyscale, suspect spots at 5x to 10x, the base branch (`review/06nov-base`) rendered the same way for comparison.
The boat and rower: `rw_rowboat.md` (PASS) and `rw_rower.md` (FAIL, two small fixes).

## Pieces

| Piece | Result | Evidence and fixes |
| --- | --- | --- |
| Water treatment (setpieces.lua Sp.drawRowboat) | PASS | the hull's own columns under row 48 tinted 70 % deep blue: a wet, darker hull; two ripple rows of white dashes along the waterline, 9 and 13 px periods, moving; the wake trails from the end the boat leaves (checked both directions, ride shots 1-4 and 11-14); the splash is 7 px at the catch and 4 at the finish (code read; too brief to catch in a shot, fine). Nothing sits on the water like a sticker. |
| Jetty piles into the water (x 2496-2544) | PASS | three piles with X bracing, the piles run under the waterline with the tint and a ripple dash either side of each; no longer a table in the river (base review RW2). Deck top is a flat 2-tone cap, fine front-on. |
| Pontoon floats and ropes (pontoon.png 54 x 19, scene.lua hline) | PASS, one fix | floats are 3-shade grey drums, their lower 3 rows tinted under the surface with ripple dashes: they sit in the water. The lines sag 2-6 px at the middle: reads as rope, no longer a wire. Fix: the timber mooring pile by the ferry's bow (world about x 1660) has no tint under row 224; it runs plain brown to the bottom of the screen while the jetty piles next door are tinted. Tint it the same way. |
| Kennel 44 x 44 (kennel.png, build_rw_kennel.py) | PASS | 0.96 m tall, pitched slate roof with shingle rows, red plank walls, cream trim, arched black door with a light arch; unbroken ink; asset_qa PASS; reads as a dog house at 1x; no longer a post box (RW3). Flat lighting (no lit left side) is acceptable at this size. |
| Road band (road.png 640 x 41, make_road.py) | PASS as play ground, FAIL as front row | 5 colours, flat asphalt with grit flecks on a grid, pale dashes, kerb and gutter line; crisp, no dither. asset_qa: WARN as play (32 "blotches" are the deliberate flecks), FAIL as front (drawn median 63 against 40). See the question below. |
| The 208 px wider harbour | PASS | water 2192-2848, two 185 px boats each with a 116 px row, the jetty between; nothing cut, nothing misplaced after the shift: promenade B (railing from 3088, birch, planter, flower box, grit box, planter, bin, cafe, Mia at 3988) all stand on their ground; the far quay end, lamp and step at x 2848-2960 are clean. |

## Screens (camera x, y 0)

| cam x | result | what is wrong |
| --- | --- | --- |
| 0 | PASS | kennel true size, bench, log, pot; road clean |
| 320 | PASS | planter, birch, lamp |
| 640 | PASS | bin, kiosks, grit box (now a chest) |
| 960 | PASS | lime, flower boxes |
| 1280 | PASS, one fix | ramp, quay, pontoon in the water with sagging lines; the mooring pile has no wet tint |
| 1600 | PASS | ferry with Pepper, quay; ferry hull as in base (not this track) |
| 1920 | PASS (not this track) | stone pier with the arch; boat 1 bow at the quay with ripple; the pier itself is the pier band track |
| 2240 | FAIL (rower) | boat 1 rowed with Pepper aboard: hull and water good; the rower's stick arm and the dragging blade at rest; jetty piles good |
| 2560 | FAIL (rower) | boat 2 the same; sweep places Pepper over the rower (test artefact, she is drawn in front) |
| 2880 | PASS | far quay, lamp, step down, railing start, birch crown cut by the top edge |
| 3200 | PASS | planter, flower box, grit box, railing |
| 3520 | PASS | planter, bin, bench |
| 3728 (end) | PASS | bench, gable, cafe, Mia |

Greyscale: the ladder holds on every screen; the road sits between the pavement and the hedge silhouette.

## The maker's questions

1. Pepper on the gunwale (y 212), not 4 px inside the boat: keep it. The Bible says nothing may cover her, and a
   hull in front of her paws would also cut them off and read as floating. On the rail she reads as "on the boat"
   at 1x; the rail is a cream band under her paws, the bow rises beside her. The duck boat does the same. If the
   owner wants her lower, the only clean way is a thwart drawn on the rail row, not a cover.
2. Darker road: yes, one palette step, not to 40. Drawn median 63 now; take it to about 50 (file fill about
   (74, 78, 86)) and keep the flecks, dashes and kerb. The front row's 40 is for the hedge silhouette in front of
   the road; at 40 the road would merge with the hedge and lose the dashes. One step darker makes the kerb and the
   light pavement pop, which is what the owner likes.
