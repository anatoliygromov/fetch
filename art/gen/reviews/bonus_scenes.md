# FETCH FRENZY bonus scenes

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-bonusscene at 8d9d781, worktree review-bonus07. Independent gate 8 reviewer; I did not make the scenes. Every round rendered with its own autopilot run (`love riverwalk --level X --bonus --auto`, fresh XDG_DATA_HOME, xvfb-run -a, three at a time): 726 frames of 640 x 480 per level, mid-round frames picked with Mia throwing and the ball, stick or frisbee in the air (frames 120, 280, 360, 440, 520 of each run), looked at at 2x in colour and greyscale side by side, the front edge and the back-to-floor join at 6x. The three fallback rounds (Rooftops, Söder, Night) are pixel-identical to Downtown's, City Park's and River Walk's (frame 1 diff 0 px), so three scenes are judged and the verdicts carry over. Maker's notes (docs/review/07nov/bonusscene/README.md) read after.

The owner: different scenery per level; no cut ground joins, no stripe stacks; dark foreground clumps are terrible.

## Per scene

### River Walk (rounds 1 and 6)
| Question | Result | Evidence |
| --- | --- | --- |
| 1 Reads as its level at once | PASS | The railing with the river behind it, the far shore's hedge row, the bridge, the spired skyline, the clouds: River Walk in the first frame. |
| 2 Pepper, Mia, items in grey at 2x | PASS | Pepper black on the light paving, Mia's hoodie on the water; the ball reads over the sky and the far shore (a dark dot on mid grey, frame 440); the frisbee edge-on over the hedge row is a 1 px sliver (frame 280), it still reads by its outline. That thinness is the frisbee's own art, not the scene. |
| 3 Bottom front edge | PASS | Paving, a granite coping of 16 px blocks, then the quay wall in four courses to the bottom (6x crop): finished, no stripe stack, no cut; the level's own lower quay rule. |
| 4 Calm | PASS | Nothing moves behind the play but the water. |
| 5 Floating, awkward cuts | PASS | The railing's posts end on the paving's top row; the far bridge is cut by the right edge as in the level; nothing floats. |
| 6 Consistent with the level | PASS, one note | The same pieces as the level. The level's promenade has the road in front; here the quay wall from the level's lower quay stretch. It reads as the quay by the water and avoids the road's dark front band, which the owner would have called a clump. Fine. |

VERDICT: PASS. Optional: the promenade is bare; one of River Walk's approved props behind the line (the lamp post at the far left, the bin at the far right, feet on y 174) would say "the promenade", not "a quay". Decoration only, nothing on the play floor.

### City Park (rounds 2 and 5)
| Question | Result | Evidence |
| --- | --- | --- |
| 1 Reads as its level at once | PASS | Two orange round trees, the far tree line, the autumn haze, the orange path: City Park. |
| 2 Grey at 2x | PASS, one note | Pepper and Mia read. The ball over the tree crown is a dark dot on mid grey (frame 120): reads. The stick in the air reads (frame 520); the stick lying on the path is lost in grey: brown on the orange path, the same luma (frame 520, screen x 295-305, y 187). The item's problem, noted for the items track. |
| 3 Bottom front edge | PASS | A kerb of granite setts with joints every 12 px and grass tufts over its foot, then the lawn to the bottom with tuft rows and ten leaves (6x crop). Finished, no dark clump, no earth stripes, no cut. |
| 4 Calm | PASS | |
| 5 Floating, awkward cuts | PASS | The left tree is cut by the left edge as in the level; nothing floats. |
| 6 Consistent with the level | PASS, one note | The far rows and the path tile are the level's. The back lawn strip (y 162-172) is a flat green band with nothing on it: between the shrub row's hard foot line and the path's dark edge row it is the one stripe left on the screen. In the level the trees and the bench stand in it. |

Notes, 0 credits:
- The front lawn's tufts sit on an exact 8 px grid in offset rows: at 2x it reads as a dot screen. bonusscene.lua has an `rng` helper that is not used; jitter each tuft's x by 0-3 px and drop one tuft in five.
- The back lawn strip: put one approved City Park prop on it behind the line, the bench at x 250-350 or the bin at the far right (feet on y 172), so the band is broken and the round says park, not lawn.

VERDICT: PASS.

### Downtown (rounds 3 and 4)
| Question | Result | Evidence |
| --- | --- | --- |
| 1 Reads as its level at once | PASS, weak | Pastel Old Town houses with spires and dormers: Stockholm's old town, and different from the other two rounds. But it is the level's far backdrop brought near, faded to the mid value; nothing of the level's play line (its full-colour fronts, awnings, stalls, lamps) is here. A child who played Downtown sees "the far houses", not the street she ran on. |
| 2 Grey at 2x | PASS | The best of the three: the ball and the frisbee are dark on the pale walls (frames 120, 360); Pepper and Mia read on the setts. |
| 3 Bottom front edge | PASS | The street's setts, the light kerb band, the granite wall in courses in the file's own greys (6x crop): finished. |
| 4 Calm or busy | PASS | Calm: the window grid is even and faded; the ball flies over it without clutter. |
| 5 Floating, awkward cuts | FAIL | The join between the houses and the floor. The backdrop's foot is hidden under the square's floor, so the houses end on a straight line across the whole screen at y 160 with no doors, no shop fronts, no plinth: a wall of windows standing on a band. The band itself (town_square_floor, rows 0-21, drawn under the mid grade) comes out as a flat pale stripe of about 10 px: its setts are smothered by the fade (6x join crop, screen x 100-260, y 162-172). So the screen stacks: flat wall, flat band, 1 px line, setts. That is the "cut" join the owner names: the houses are cut off at the ground floor and a stripe hides it. The three bollards are the only break in 320 px. |
| 6 Consistent with the level | PASS, note | The pieces are Downtown's. The level's play line is full colour; the round is pale all over. Acceptable while the Downtown redesign is open, if the join is fixed. |

Fixes, 0 credits, in bonusscene.lua:
1. Draw town_square_floor under the back grade (Look.use("back"), the ground plane 2-3 m behind Pepper is the back row, not the mid row) so its setts and kerb show; then the band is a floor, not a stripe.
2. Give the houses a ground floor: stamp the approved town_door (art/gen/reviews/town_door.md) at two or three places on the far wall, its sill on y 160, under the mid grade with the houses; or lower the backdrop so a plinth row of its own sits on the kerb (BS.DT_ROOFS: the file's bottom rows are windows, so the door stamps are the better route).
3. One Downtown prop behind the line to tie the round to the street: the lamp post (town art) at the far left, foot on y 172, and nothing in front of the play.

VERDICT: FAIL (the join; three small fixes).

## Fallbacks
Rooftops = Downtown's round (FAIL with it), Söder = City Park's (PASS), Night = River Walk's (PASS); each frame-identical to its base. When Night Harbour gets a palette, its round should not be a summer morning; noted for later, not a defect now.

## Summary
| Round | Scene | Verdict |
| --- | --- | --- |
| 1 River Walk | promenade | PASS |
| 2 City Park | lawn | PASS (two optional notes) |
| 3 Downtown | square | FAIL: houses cut off at the ground floor on a flat band |
| 4 Rooftops | Downtown fallback | FAIL with 3 |
| 5 Söder | City Park fallback | PASS |
| 6 Night | River Walk fallback | PASS |

Top fixes by impact: (1) Downtown's square floor under the back grade so its setts show; (2) door stamps on Downtown's far wall; (3) one approved prop behind the line in each scene (River Walk lamp, City Park bench, Downtown lamp); (4) jitter City Park's front tufts off the 8 px grid; (5) the stick's read on the orange path in grey (items track).
