Reviewer: independent gate-8 art reviewer (Claude, did not make these), 7 Nov 2026
Branch day/07nov-ground at fc03880, worktree review-ground07. Judged only against the versions the owner preferred (the files before the 6 Nov fixes, pulled from git), pixel for pixel where a file exists, and in the River Walk and City Park sweeps at 3x and 6x.

# Round 1 (reviewer, 7 Nov)

## road (art/scene/road.png, 640x41)
- Byte-identical to aa38be5 (5 Oct, the textured road the owner liked): grain, tyre tracks, cracks, patches, worn dashes. In game at x 0 to x 1280 and x 2880 to the end it is the same road as before.
- asset_qa FAILs it (noise 3.3 %, blotches 10.9 %, stray 3.9 %). That is the texture the owner asked back; the gate is noted, not applied.
- Kerb: a lit top row and a dark face between the paving and the road on every road screen. PASS.
VERDICT: PASS (the old road, exactly).

## park_ground (art/scene/park_ground.png, 240x68)
- Byte-identical to 63c25de (6 Oct): lawn strip, speckled sand path, grass fringe, earth strata.
- asset_qa FAILs it (noise 0.7 %, ladder darkest 37 on the back row). Same note: the owner's choice.
VERDICT: PASS (the old ground, exactly).

## park_stone (art/scene/park_stone.png, 26x21)
- The pink granite dome with moss, cut at the waterline: the colours of 7bb9d53 and the cut of 7ba7a20. The grey 6 Nov stone is gone. In the pond (x 640, x 1920) with the ripple ring and the dark reflection kept. asset_qa PASS.
VERDICT: PASS.

## pontoon (art/scene/pontoon.png, 54x12)
- Byte-identical to add29a7 (5 Oct): the slab on two floats. In game at x 1280: deck above the water, floats in it with ripple dashes, moored by a line to the quay cleat and to the pile. It sits in the water, not on it. asset_qa PASS.
VERDICT: PASS.

## gritbox_front (art/scene/gritbox_front.png, 88x32)
- The old forest greens (a1108ee / c3d341a: mid green body, darker grooves, lighter lid) on the front-on plank shape of 6 Nov (three planks, side posts, a grey hasp). Not pixel-identical to the old file (the shape is the 6 Nov one, as agreed), but the colour read at 1x and 3x is the old box. Sits on the paving on its dark bottom ink. asset_qa PASS. The old "SAND" lettering is not back (the 6 Nov file had none either): fine, no text on art.
VERDICT: PASS.

## River Walk front band (verges and bollards)
- The scalloped hedge silhouette of 6 Nov is gone. The grass verges with shrubs, bollards and the manhole are back at the same places (x 0 to x 1280, x 2880 on). Dark silhouette, below Pepper's line, never over her.
VERDICT: PASS.
