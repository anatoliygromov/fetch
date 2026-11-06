Reviewer: independent gate-8 art reviewer (Claude, did not make these), 6 Nov 2026

# Review gate 8: park_table_front.png (72x28) and park_bush.png (75x34), triage keeps, unchanged - round 1

Own frames: art/gen/reviews/cp_props_06nov_frames/table_x1340_3x.png, bush_x440_6x.png, scale_vs_pepper_4x.png.

## park_table_front (play, picnic table)
asset_qa WARN: noise 0.9 % (11 pixels). Scale (46 px/m): 72x28 = 1.57 m x 0.61 m. A real picnic table is about 1.8 m x 0.75 m: owner question (the maker notes the 0.6 m height is the perch).
1 Scale PASS (owner question). 2 Layer PASS. 3 Outline PASS (1 px ink #030000, unbroken). 4 Shapes PASS (straight planks and legs). 5 Shading PASS (orange plank in 3 tones, lit top, the 11 dirt pixels are the plank nail dots and read as nails). 6 Palette PASS (7 colours). 7 View PASS (front-on, thin top, bench plank). 8 Fit PASS (crisp as the bin and bench at 3x, Pepper stands on it in the frame). 9 Read PASS.
VERDICT: PASS (owner question on height)

## park_bush (front layer, 75x34, only its top 19 rows show at the screen's bottom edge, y 221)
asset_qa WARN: noise 34 px (1.8 %), lone 3.9 %, 6 blotches (1.1 %).
Scale: 75 px at about 60 px/m = 1.25 m wide, 0.57 m tall, but only 0.3 m show.
1 Scale PASS. 2 Layer PASS (6 colours, darkest #13100f, lightest #3d382b, near black on the screen's edge, median luma 32 as the README says). 3 Outline PASS (a front silhouette, the edge is its own dark shade). 4 Shapes PASS (bumpy bush with a few twig spikes). 5 Shading FAIL: at 5x the fill is mottled olive with scattered lone pixels, stray twig dots and 6 dirt patches (the maker's WARN numbers: 1.8 % noise, 3.9 % lone, 1.1 % blotches), unlike the clean ramps of the bench. In the game it is a near black silhouette (frame bush_x440_6x.png) and the mottling cannot be seen. 6 Palette PASS. 7 View PASS. 8 Fit PASS in game (dark silhouette under Pepper's line). 9 Read PASS (a dark bush at the screen edge).
VERDICT: FAIL on file (item 5 only), not visible in game; the owner will not notice it. A hand tidy of the specks is optional, not urgent.


# Round 2 (park_bush only; park_table_front not re-checked)

Reviewer: independent gate-8 art reviewer (Claude, did not make this asset), 6 Nov 2026. Head 33d1a06.

asset_qa: PASS. check_backdrop: OK. Own frames: art/gen/reviews/cp_props_06nov_frames/r2_x420_3x.png (it sits off the bottom of this frame), r2_bush_edge_6x.png (screen bottom edge at 6x), r2_files_5x_beside_bench_bin_lamp.png (file at 5x).
Scale unchanged: 75 x 34 at about 60 px/m = 1.25 m x 0.57 m, 19 rows show.

Round 1 FAIL (item 5, mottled, lone pixels, blotches): fixed. The file is 4 flat shades (#13100f, #211e19, #2e2d1d, #3b3921 family: 1267, 419, 175 and 65 px), a lit upper left with scalloped clumps, no blotches. The only lone-looking pixels are 1 px twig tips on the top edge and one detached twig dot at (7, 8); at 1x on the screen edge they are invisible and read as twigs.

1 Scale PASS. 2 Layer PASS. 3 Outline PASS. 4 Shapes PASS. 5 Shading PASS. 6 Palette PASS. 7 View PASS. 8 Fit PASS. 9 Read PASS (a dark bush at the screen edge).

VERDICT: PASS
