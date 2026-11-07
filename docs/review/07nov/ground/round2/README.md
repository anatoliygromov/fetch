# GROUND track, round 2 (7 Nov): the independent review's fails, fixed

Review: `origin/review/07nov-ground` (b326389), art/gen/reviews/ground_joins_07nov.md, rw_kennel.md,
riverwalk_sweep_07nov.md, citypark_tall_sweep_07nov.md. 0 credits. Every picture here is round 1 (left or top) |
round 2 (right or bottom), colour over greyscale.

| Review item | Fix | Frames |
| --- | --- | --- |
| RW-j: the quay's paving met the water in one straight cream row (7 screens) | Sc.paintQuay: the paving's back row is now a coping of its darkest stone (#9da0ad, a joint every 16 px). Sc.drawQuayEdge: a 1 px wet row in the quay ends' arris colour on the water above it, the whole length. It is drawn right after the river, so the railing, lamps and trees stand in front of it | `rw_j_quay_edge_x320_3x/8x`, `rw_j_lower_quay_x2880_3x`, `rw_j_x3200_3x` |
| RW-n: the dark lens under the pier's plinth | The segmental arch is gone. The pier's foot is one plain course of its own stone, 24 px blocks like the pier's, with the plinth's shadow row on top. A 1 px dark contact row on the paving, and the slanted shadow stays. Pepper still crawls under the plinth's box (physics unchanged) | `rw_n_pier_course_x1920_3x` |
| RW blob at x 2880 (screen 157-162, y 204-210) | It was a manhole cover. Look.road scrolls the covers with their road row (1.06x), so this one slid past the road's start and the span's scissor cut it into a 6 x 5 blob. Now only a cover wholly on its stretch of road is drawn (look.lua) | `rw_blob_x2880_6x` |
| CP-f: the near banks read as a trapezoid cut into the ground | (1) 2 px of wet earth along each bank's edge under the water line (a dark overlay, so it is darker than every stratum it crosses) and 4 ripple dashes of 3 px on the water against it. (2) One shoulder colour: the old olive lawn wedges (Sc.drawPondShoulders) are no longer drawn, so all four ends have the same sand shoulder. (3) On the lower half of the diagonal a 2 px level step every 8 rows | `cp_f_bank_y144_x0640/1920/2240_3x`, `cp_f_bank_x1920_6x` |
| CP-j: the rope bridge's post cut on the path | A granite footing under every post foot of the built walks: 2 px wider than the post, 2 rows, with a 1 px dark contact row (found from the legs art's bottom row) | `cp_j_post_footing_x1920_6x` |
| CP-c / CP-n: a 16 px battlement of tufts, a dot grid on the mid lawn | tools/make_ground_kit.py: one 48 px pattern of bumps 1-3 px wide and 1-3 px tall with gaps of 1-3 px, from a fixed list in no regular order. The root strip is now 48 x 5, anchored in the world. The tuft row and the mid lawn (3 rows of the pattern, 2-3 px tufts only) use it too. The far tree line now has the tuft row over its feet as well | `cp_c_tree_feet_x1600_5x`, `cp_c_tree_feet_x960_4x`, `cp_n_up_no_leaves_y024_x0960_3x` |
| Kennel: Pepper floated 5-9 px on the peak | A level ridge board on the roof (art x 6-37, rows 0-3). The boards fall 1 in 2 from its ends to the eaves. Eaves box y 145 (was 150). Measured under her paws (`kennel_paw_gaps.txt`): at x 16 hind paws (cols 6-9) 0 px, front paws (27-31) 0 px; at x 22 hind (12-15) 0, front (33-37) 0; at x 30 hind (20-23) 0, front (41-45) 4-5 px. At x 30 her front paws are past the board's end, over the eave and the kennel's edge: the edge of a platform. 0 px there needs a roof flat to x 44, which is a box. The board is 32 px, not the 24 px asked: at 24 px (x 10-33) her paws at x 22 hung 2-4 px | `kennel_pepper_x16_22_30_5x_round1_top_round2_bottom`, `kennel_8x_round1_round2` |
| Kennel: 4 px of lawn to its left | Not done. Moving the kennel 4 px right means moving Pepper's start 4 px right too (her box starts 1 px right of the kennel), and that changes the frozen Pepper golden trace. The left eave stays on x 0. | |

## Checks

PEPPER UNCHANGED; check_flow 125/125; TILED CHECK PASSED; BACKDROP OK. Physics: riverwalk 56/56 (ground joins PASS,
11 changes), citypark_tall 98/98 (ground joins PASS, 4 changes), downtown_tall 102/102. check_curve T1-T4 PASS.
asset_qa: kennel, kit_cp_tufts and kit_cp_roots PASS. kit_cp_midlawn WARN on noise and blotches: tufts on a flat lawn
are seen as noise. Cards: `cards/`.

## Questions for the owner

1. Steps or a smooth ramp down to the quay? The 8 px stone steps stay until he decides. The reviewer passed them;
   the owner has not chosen.
2. The kennel roof now has a level ridge board, so Pepper stands flat on it. It looks a little flatter than a
   classic pitched roof. Keep it, or go back to the pitched peak and accept her paws over the slopes?
3. The front garden runs across the whole house front, with the public bench in it. OK?
