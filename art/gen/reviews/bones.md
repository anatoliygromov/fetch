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

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-chars at 3b69dbf merged into the review worktree. Re-rendered: the changed files at 5x to 8x, River Walk x 1600, 2240, 2880, City Park tall y 144 x 640, 1280, 2560, the lane riders, car 5 and the baker in game (my still-vehicle hook now reads Rd.RIDER_TOP), colour and greyscale.

Moves checked in game (6x to 10x crops):
- River Walk 1600, bone 1650 to 1644: PASS, clear of the wheelhouse wall by 4 px.
- City Park 1280, id 138 x 1310 to 1316: nearly. The bone's left end still touches the lamp base's foot by 1 px at screen (31-32, 171). 2 px more right clears it. Minor.
- City Park 2560, ids 171 and 172 up 6: the upper bone is clear on the trunk (PASS); the lower bone at screen (200, 141) still sits across the blue climbing frame's top bar. FAIL: 6 px more up (y 268) or 8 px down below the bar.
- City Park 640, id 128 y 346 to 336: FAIL. The bone moved from the duck boat's neck into its beak: at screen (233, 174) it lies on the beak under the eye (8x crop). Funny by accident, but it is a collision and it bobs. Move it 14 px up (y 322, above the head) or 16 px left (x 1294, over the water). The other bone on the boat's stern seat at (268, 180) also overlaps the blue cushion; 6 px up.
- Downtown tall 1280 (statue coat, gold bone on the hat) and 1600 (fountain jets and rim): not moved in round 2; the round 1 collisions stand.

VERDICT (round 2): the piece PASS; placements still FAIL at City Park 640 and 2560 and the two Downtown screens.
