# Visual and presentation bugs, 22 Oct (branch `r5/bugs`)

The owner's report: "the bike is too small, the cars get cropped when they pass etc, we need to make sure to fix all
that". Swept with the `--test` tours and the `--auto` runs of all nine levels (frames read at 1x and in 3x crops),
the `--flowtest` screens (title, menu, level select, intro, story, tally, ending, pause, game over, bonus round).

Scale reference, measured from the art: Pepper's back 27 px, her head 38 px; Mia 59 px (an 8-year-old: about 46 px a
metre). An adult is then about 80 px, a bicycle wheel about 30 px, a door about 95 px, a tram about 160 px.
See `scale_lineup.png` (every person and vehicle next to Pepper and Mia, 3x).

Evidence images are in `/home/claude/out/r5-bugs/` (before / after pairs at 3x for the fixed bugs, `ev_*.png` for
the open ones). Art to make: `/home/claude/out/r5-bugs/NEEDS_ART.md`.

| # | Bug | Where | Evidence | Status |
|---|-----|-------|----------|--------|
| 1 | Road cars sliced in half: a car drove into the end of its stretch of road (where the promenade turns into the quay steps) and the road's scissor cut it off vertically; one could also pop out of the start of a stretch on screen, and was removed on screen when it passed the end | River Walk, near lane (road.lua) | `01_road_car_sliced.png` | **Fixed**: vehicles enter and leave only at screen edges; sent only when the road reaches far enough for the camera's speed, speed up or drop behind if Pepper chases them, removed only when wholly off screen. `LOOK_CHECK=1` counts `ROAD CUT`: 0 in the autopilot. Cars now drive both ways, 300-380 px/s |
| 2 | The promenade bike is a child's bike: `cyclist1.png` 49 x 50, wheels 19 px, smaller than Pepper's back | River Walk bike zones 1 and 2 | `02_bike_scale.png`, `scale_lineup.png` | **Fixed**: the adult cyclist art (`road_cyclist1-2.png`, 73 x 75, true 1x pixels, wheels 29 px = Pepper's back); hit box 70 x 28 (the drawn bike, was 48 x 26); the riders take turns |
| 3 | The taller rider rode through Pepper standing on a flower box (bike drawn in front of the box, behind her) | River Walk bike zones | `02_bike_scale.png` (after), `ev_rider_over_pepper.png` (after: the head overlap left) | **Fixed**: bikes ride behind the obstacles on her line; the box hides the wheels. (The rider's head still passes behind Pepper's: she is always drawn on top, by rule) |
| 4 | The far shore ran out: the tree band ended in a hard edge with bare sky beside it (built for the old 3200 px level) | River Walk, last two screens | `03_far_shore_gap.png` | **Fixed** (scene.lua: 1600 px of shore) |
| 5 | The far skyline stood still over the last 640 px (its range fixed at 2880 px) | River Walk, end | (same frames as 4) | **Fixed** (uses the level's width) |
| 6 | LEVEL SELECT overflow: SODER HILL under the footer, NIGHT HARBOUR off the panel and the screen, the SOUND pill on top of the text | Menus | `04_level_select_overflow.png` | **Fixed** (30 px rows, 208 px panel) |
| 7 | The `--test` tour's traffic shot put a car over the quay steps (outside its road) | River Walk tour shot 21 | `ev_rw_test2_21_traffic_planter.png` (after) | **Fixed** (test only) |
| 8 | The leaf cart keeper is 61 px tall: an adult as tall as Mia | City Park, tall City Park (cart zones) | `ev_keeper_cart.png`, `scale_lineup.png` | **Needs art**: 2x would be 122 px (too big), 1.33x is not clean. Interim: unchanged |
| 9 | The winch man by the duck boat is 57 px: shorter than Mia | City Park screen 3, tall City Park | `ev_winch_man.png` | **Needs art** (same reason) |
| 10 | The tram is 34 px tall (Pepper's height), its shed 41 px, the tram stop shelter 48 px: a toy tram and a shelter shorter than Mia | Downtown tram zones | `ev_tram_shelter.png`, `scale_lineup.png` | **Needs art and a level change**: Pepper escapes the tram on the shelter and shed roofs (41-48 px, within her 46 px jump); a tram at scale (about 150 px) changes the puzzle. Won't fix in code |
| 11 | Downtown doors are 58 px (shorter than Mia) and the houses dollhouse-sized beside Pepper | Downtown, the houses at the back of the square | `ev_town_door.png` | **Needs art** (or accept: they stand at the back of the square, so smaller by distance) |
| 12 | The duck boat is 54 x 33: a pedal boat smaller than Pepper's length | City Park pond | `ev_duck_boat.png` | **Needs art** (its deck is the mover's box: a bigger hull must keep the deck at the same height) |
| 13 | Near-lane cars and road cyclists are cut by the bottom of the screen (wheels below y 240) | River Walk road | `ev_near_lane_bottom_crop.png` | **Won't fix, owner to confirm**: the near lane is closer than the frame; whole cars at Pepper's scale (70-90 px) in the 41 px road band would have to cover her line. Not the "cropped when they pass" bug (that was #1) |
| 14 | Street lamps standing in the tree canopies on the high road | Tall City Park, treetop tier | `ev_treetop_lamp.png` | **Needs art** (a treetop lantern on a branch for the high road's checkpoints) |
| 15 | Greybox labels under the HUD bars and cut at screen edges | Soder Hill, Night, the greybox tall levels | tour shots | **Won't fix**: greybox, replaced by art |
| 16 | Only one cyclist size: the near-lane cyclists (closer to the camera) now use the same art as the promenade bikes | River Walk | `19_traffic_home` shot | **Won't fix** for now (reads fine; a bigger near-lane rider is on the art list as optional) |

Checked and found right: Pepper, Mia, the ball and bones; the goose (about 30 px: a goose's height), the gull and the
magpie; the bench, bin, flower box, grit box, planter, picnic table; the HUD on every level; the intro, story, tally,
ending, pause and GAME OVER cards; the bonus round's cards. No pixel-scale mixing (every asset is drawn at 1x and at
whole pixels; the 2x upscale of `cyclist1` was rejected for that reason in favour of the 1x adult art).

Checks on this branch: `check_pepper` PEPPER UNCHANGED (4591 steps), `check_pepper_files` 5 files identical,
`check_flow` 103 of 103, `check_tiled` all PASS, `--physics` citypark 73, downtown 70, riverwalk 40, soder 23,
night 37, lab_tall 40, citypark_tall 82, rooftops 88, downtown_tall 81 (all pass), `--auto` 44.2, 51.6, 66.3, 73.3,
81.3 s (the five real levels, unchanged) and lab_tall 25.9, citypark_tall 38.5, rooftops 54.1, downtown_tall 56.9 s,
`--qa` 0 problems on City Park, Downtown and River Walk.
