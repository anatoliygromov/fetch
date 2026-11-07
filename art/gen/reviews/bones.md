# Gate 8 review: bone and bone_gold (15 x 9)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. The two files at 6x beside the bench and bin; every sweep screen of River Walk (13), City Park tall (27) and Downtown tall (33) at 2x, 6x crops where a bone meets art. Maker's notes read after.

Piece: riverwalk/art/scene/bone.png and bone_gold.png, 15 x 9 (was 11 x 6). stage.lua and night.lua centre them on the bone's x with the bottom row at y - 7, bobbing 1-2 px.

| # | Item | Result | Evidence |
|---|---|---|---|
| Shape | PASS | A double-knob bone: two round ends, a waist, one highlight row, one shade row, one ink outline. Reads as a bone at 1x, chunkier than before, cute. |
| Gold | PASS | The same pixels in a gold ramp; reads as the super bone at 1x, not as a coin. |
| Crisp | PASS | 5 colours, flat fills, script PASS. |
| Scale | PASS | 15 px = a 33 cm bone at 46 px/m; big for a dog biscuit, right for a pickup a 7 year old must see. |
| Layer | PASS | Drawn with the look off in front of the play layer; ink darkest. |

Bone placements that collide with level art (level data, not the piece; the bigger bone now touches things the 11 x 6 one cleared). Screen = camera x (sweep tier y), screen x,y at 1x:
- River Walk 1600 (y 0): bone at about (47, 172) overlaps the ferry's wheelhouse left wall by 2-3 px (the one the maker named). Move it 6 px left or 6 px up.
- River Walk 0, 320, 1200, 3200: bones sit on the promenade railing's top rail (for example 3200: (268, 136), (290, 136), (313, 136)). They read, the outline carries them; a 4 px lift clears the rail.
- River Walk 3520 and 3728: three bones on the bench's backrest (3520: (266-311, 139)). Reads as bones on a bench; fine, but they hide the slats.
- River Walk 320, 960, 3200: bones in the planter's flowers; fine.
- City Park tall 640 (y 144): bone at about (235, 185) on the duck boat's neck. Move it 10 px up.
- City Park tall 1280 (y 144): bone at (28, 170) across the lamp post's base; move 6 px right.
- City Park tall 1920 (y 144 and y 24): bones on the rope bridge's ropes at (118, 39) and (178, 39); 4 px up clears them.
- City Park tall 2560 (y 144): bones on the blue climbing frame's bars at (193, 127) and (200, 147); move 6 px up.
- Downtown tall 1280 (y 240): two bones on the statue's coat at (212, 132) and (236, 132); the gold bone touches the top hat at (224, 64). Move the pair 8 px left and right of the statue, the gold one 4 px up.
- Downtown tall 1600 (y 240): bones at (126, 157), (226, 152), (256, 157) across the fountain's jets and rim; 6 px up.
- Downtown tall 2240, 2560 (y 240 and y 120): bones inside the balcony railings (2240: (198, 69), (218, 69); 2560: (28, 17), (65, 17)). They read; optional.
- Downtown tall 320, 2880: bones touching the umbrella tables' tops (2880: (66, 124)); 3 px up.

VERDICT (round 1, 7 Nov): PASS (the piece). The placements above go to the level tracks: 7 real collisions (ferry wheelhouse, duck boat, lamp base, ropes, climbing frame, statue, fountain), the rest overlaps that read.
