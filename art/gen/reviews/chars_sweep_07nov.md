# Track CHARS sweep, round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer. `LOOK_SWEEP=1 LOOK_STEP=320` on riverwalk (13 frames), citypark_tall (27: tiers y 144, 24, 0) and downtown_tall (33: tiers y 240, 120, 0), looked at as 2x contact sheets in colour and greyscale, details at 4x to 8x. The sweep clears the bikes and the road traffic spawns by chance, so the riders, cars and the baker were shot on their own (a local copy of tests_look.lua with a still-vehicle hook; LOOK_BIKE, LOOK_CARGO) and the hint bubbles with --hintshots. Per piece: road_car1-5.md, cyclist_adult1/2(.pedal).md, cargo_bike.md, road_rider1/2.md, rw_ferry.md, gull.md, bones.md, cat.md, hint_pics.md.

Only this track's pieces are judged here (cars, riders, baker, ferry, gull, bones, cat, hint pictures). A screen FAILs when one of them is wrong on it, or a bone sits in level art. The baker's gate clip (x 1938, 3168) is known and not a FAIL here.

## River Walk (y 0)
| x | Result | What |
| --- | --- | --- |
| 0 | PASS | bones chunky and clear on the pavement and the rail |
| 320 | PASS | bones in the planter and on the rail; the gull far over the shore reads |
| 640 | PASS | bones on the kiosk counter and the gold bone over the roof |
| 960 | PASS | |
| 1280 | PASS | bones over the water read against the blue |
| 1600 | FAIL (bone placement) | the bone at screen (47, 172) overlaps the ferry's wheelhouse wall; the ferry itself PASS: in the water, waterline, wet hull, crisp cabin |
| 1920 | PASS | bones under the bridge arch read on the dark |
| 2240 | PASS | gull PASS at 1x, the rower and the pier bones |
| 2560 | PASS | |
| 2880 | PASS | gull |
| 3200 | PASS | three bones on the rail's top; they read, 4 px up would clear it (optional) |
| 3520 | PASS | three bones on the bench back; read as bones on a bench |
| 3728 | PASS | same bench; Mia |

Vehicle shots at x 760 (my LOOK_CAR / LOOK_LANE / LOOK_BIKE): cars 1-5 PASS in the near lane at 1x and 2x; lane riders PASS as art, head-and-shoulders read is the open judgement (12 px, see road_rider1.md); promenade riders 1 and 2 PASS beside Pepper, the chain case reads as a black box at 2x (note).

## City Park tall
| x | y 144 (path) | y 24 | y 0 |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS |
| 320 | PASS (bones on the bench back and in the hedge; read) | PASS | PASS |
| 640 | FAIL (bone placement): a bone at about (235, 185) on the duck boat's neck | PASS | PASS |
| 960 | PASS | PASS | PASS |
| 1280 | FAIL (bone placement): a bone across the lamp post's base at (28, 170); the picnic table bones read | PASS | PASS |
| 1600 | PASS | PASS | PASS |
| 1920 | PASS (bones on the rope bridge's ropes at (118, 39), (178, 39): read, 4 px up optional) | PASS | PASS |
| 2240 | PASS (bench back, arbour) | PASS | PASS |
| 2560 | FAIL (bone placement): bones on the blue climbing frame's bars at (193, 127) and (200, 147) | PASS | PASS |

## Downtown tall
| x | y 240 (street) | y 120 | y 0 |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS |
| 320 | PASS (a bone touches the umbrella table's top; 3 px up optional) | PASS | PASS |
| 640 | PASS | PASS | PASS |
| 960 | PASS | PASS | PASS |
| 1280 | FAIL (bone placement): two bones on the statue's coat at (212, 132), (236, 132), the gold bone on the top hat (224, 64); the cat PASS on the statue's hand, 32 px reads right beside Pepper | PASS (cat and loggia) | PASS |
| 1600 | FAIL (bone placement): bones across the fountain's jets and rim at (126, 157), (226, 152), (256, 157) | PASS | PASS |
| 1920 | PASS; the baker's zone 1: sprite PASS seated, arm, feet, facing left; legs do not read at 1x (cargo_bike.md FAIL); the depot clip at 1938 is the known level item | PASS | PASS |
| 2240 | PASS (bones inside the balcony railings read) | PASS | PASS |
| 2560 | PASS (bones on the balcony top read) | PASS | PASS |
| 2880 | PASS (a bone touches the umbrella top at (66, 124); 3 px up optional) | PASS | PASS |
| 3200 | PASS; zone 2 baker shots the same as zone 1 | PASS | PASS |

Hint bubbles: all 36 control-hint frames of the three levels PASS (hint_pics.md).

## Per piece
| Piece | Verdict | Why |
| --- | --- | --- |
| road_car1-4 | PASS | one family, wheels identical, crisp, read at 1x |
| road_car5 | PASS | wheels fixed as asked; the body is the old render and the odd one out at 5x (optional rebuild) |
| cyclist_adult1 (+pedal) | PASS | seated, hand on the grip, feet on the pedals, a 16 px crank circle, limbs joined |
| cyclist_adult2 (+pedal) | PASS | same, 14 px circle |
| cargo_bike (+pedal) | FAIL | the five reported defects are fixed, but trousers, shoes, frame and chain case are one dark mass: no legs at 1x |
| road_rider1, road_rider2 | PASS | art; raise 12 px, not 6, if the hands are to read |
| ferry | PASS | in the water, crisp, repeated parts stamped |
| gull | FAIL | the still and 24 px are right; frames 4 and 5 twin, 5 to 6 pops: the flap hitches |
| bone, bone_gold | PASS | the piece; 7 placements collide (bones.md) |
| hint pictures | PASS | clean, Pepper at once on the device |
| cat (cat_r2 wired) | PASS | 32 vs 30 px does not read |

## Top 6 fixes by impact
1. cargo_bike and cargo_bike_pedal: trousers (75,79,80) to (118,124,134) with (93,98,108) shadow, shoes (35,41,42) to brown (107,65,40); a 1 px frame-grey rim on the chain case's top and front edge. All 9 frames, 0 credits. The baker gets legs at 1x.
2. gull.png frame 5: redraw as a wings-level-rising frame (the frame 3 body, wing 2 px above the back, tips up) so the flap is up, half, level, down, level, up; the 1 frame removes the hitch.
3. Bone placements, 7 moves in level data: River Walk 1600 wheelhouse bone 6 px left; City Park 640 duck boat bone 10 px up, 1280 lamp bone 6 px right, 2560 climbing frame bones 6 px up; Downtown 1280 statue bones 8 px out and the gold bone 4 px up, 1600 fountain bones 6 px up.
4. Lane riders: RIDER_TOP 190 to 178 in road.lua (12 px) so the hand and the bar's first 7 rows show; 6 px would show only the fingers.
5. gull.png frames 1, 2, 6: 1 px of sky between the head and the far wing; feet pixels in all 6 frames or none.
6. road_car5: optional rebuild of the body on the n07 builder (driver, light glass, 1 px bar handles) so the five cars are one family at 5x; the roof alone passes in the game.

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-chars at 3b69dbf merged into the review worktree. Re-rendered: the changed files at 5x to 8x, River Walk x 1600, 2240, 2880, City Park tall y 144 x 640, 1280, 2560, the lane riders, car 5 and the baker in game (my still-vehicle hook now reads Rd.RIDER_TOP), colour and greyscale.

Per piece after round 2: road_car1-5 PASS; cyclist_adult1/2 PASS; cargo_bike PASS (legs read at 1x); road_rider1/2 PASS (hands and grip show at RIDER_TOP 178); ferry PASS; gull PASS (loop flows, far wing hidden reads); cat PASS; hint pictures PASS; bones PASS as a piece.

Screens after round 2: River Walk 1600 PASS (bone clear of the wheelhouse). City Park tall 640 FAIL (the bone is now in the duck boat's beak), 1280 PASS with a 1 px touch at the lamp base (2 px right), 2560 FAIL (the lower bone still on the blue bar). Downtown tall 1280 and 1600 FAIL as in round 1 (not moved).

Remaining fixes, all level data: City Park id 128 to y 322 or x 1294; id 172 (the lower bone at 2560) 6 px more up; id 138 2 px more right; the stern-seat bone at 640 6 px up; Downtown 1280 statue bones 8 px out each side and the gold bone 4 px up; Downtown 1600 fountain bones 6 px up. Art: nothing remains.

# Round 3 (reviewer, 7 Nov)

Bones only, on origin/day/07nov-integration at 4cf3975 (the merge of day/07nov-bonusdt), worktree review-integ3. City Park tall y 144 at x 640, 1280, 2560 and Downtown tall at y 240, 120, 0 around x 1280 and 1600 (five camera stops), each bone at 6x to 12x in colour and grey, the data's position boxed on the crop (bone drawn centred on x, top at y - 15, bobbing 1-2 px). Screen coordinates below are the bone's centre at the stated camera.

| Bone | Where | Screen (cam) | Result |
| --- | --- | --- | --- |
| CP 128 (866, 308) | duck boat | (226, 153) at cam 640 | PASS: 14 px above the duck's head, over the far shrub row |
| CP 129 (906, 340) | duck boat stern | (266, 185) at cam 640 | PASS, tight: its bottom row is 0-1 px off the blue seat cushion's top; the bob touches it. 3 px up (y 337) to be clean |
| CP 138 (1318, 328) | lamp post base | (38, 173) at cam 1280 | PASS: 2 px clear of the base, 4 px clear of the bin |
| CP 171 (2760, 303) | climbing frame | (200, 148) at cam 2560 | PASS: inside the blue frame's opening, 4 px off the bars above and below |
| CP 172 (2752, 268) | trunk above the frame | (192, 113) at cam 2560 | PASS: on the trunk, clear |
| DT 156 (1424, 396) | bush by the pedestal | (144, 145) at cam 1280 | PASS (unchanged): on the bush |
| DT 157 (1441, 384) | statue, left | (161, 133) at cam 1280 | PASS, tight: 1 px of wall between its right knob and the coat's outline |
| DT 158 (1487, 384) | statue, right | (207, 133) at cam 1280 | PASS, tight: 2 px from the coat's right edge, under the arm |
| DT 159 (1464, 310) gold | above the hat | (184, 59) at cam 1280 | PASS: 12 px above the top hat, under the gallery |
| DT 163 (1728, 408) | shop front left of the fountain | (128, 157) at cam 1600 | PASS |
| DT 164 (1758, 400) and 165 (1772, 400) | left of the fountain's column | (158, 149) and (172, 149) at cam 1600 | FAIL: 14 px apart with a 15 px bone, they share a column (x 1765) and read as one long bone; 165's right knob is 2 px from the column. Move 164 to x 1752 and 165 to x 1770 (3 px between them, 3 px to the column) |
| DT 166 (1826, 400) | right of the column | (226, 149) at cam 1600 | PASS: over the shop, 4 px from the column |
| DT 167 (1856, 408) | by the crates | (256, 157) at cam 1600 | PASS, tight: 1 px from the crates' left edge |
| DT 168 (1884, 388) | over the shop | (284, 137) at cam 1600 | PASS |

The rebuilt fountain's spray is droplets, not jets, so nothing crosses a bone there. Tiers y 120 and y 0 show none of these rows.

Remaining fix: Downtown 164 to x 1752 and 165 to x 1770. Optional: City Park 129 3 px up; Downtown 157 and 158 4 px further out; 167 2 px left.

Note on method: my first Downtown render of this round ran from the wrong directory (main's old Downtown); it was redone from the worktree by absolute path before judging.
