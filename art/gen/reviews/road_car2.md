# Gate 8 review: road_car2

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. Looked at the file at 5x beside the approved bench and bin, in the game at 1x and 2x (my own shots, a local copy of tests_look.lua with a still-vehicle hook; the branch is untouched), colour and greyscale. `python3 -I tools/asset_qa.py --file` run on every file. The maker's notes (docs/review/07nov/chars/README.md) read after the verdicts were formed.

Piece: riverwalk/art/scene/road_car2.png, 244 x 103 (cream van), near lane (55 px/m), only the top rows show above y 192.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Repeated parts the same (wheels, door handles, glints) | PASS | Both wheels pixel-identical: the lower 40 rows of the two wheel columns differ by 0 px (measured). Handles and glints one stamp each. |
| 2 | Wheels round, spokes even | PASS | Five-spoke rim, round tyre, no lumps at 5x. |
| 3 | One light direction, ramps, no dabs | PASS | Roof and bonnet lit from the upper left, body in one flat band plus a shadow band under the sills; no mottling at 5x. |
| 4 | Outline 1 px, one ink | PASS | One dark ink around the silhouette, unbroken; the pillars and wheel arches are the same ink. |
| 5 | Faces, hands (driver) | PASS | A grey driver silhouette with a head in the front window. |
| 6 | Scale against Pepper, slot | PASS | Slot per tools/asset_qa.py SLOTS; the roof sits under Pepper's feet line in the shot (my car shots, River Walk x 760). |
| 7 | Mirrored as drawn | PASS | Drawn flipped for the right-hand lane; reads the same. |
| 8 | In game, the part that shows | PASS | Top 48 rows show over the road: roof, glass, driver, door tops. Reads as a car passing close at 1x and 2x, colour and grey. |
| 9 | Next to bench, bin, lamp | PASS | As crisp as the bench at 5x; no lone pixels in the fills (script PASS). |
| R | Checklist scale, layer, outline, shapes, shading, palette, view, fit, read | PASS | 20 opaque colours; script PASS on noise, stray, blotches, specks, pinholes, outline, colours, ladder. A child reads it as a car at 1x. |

Notes: Clean. The side moulding stops at the sliding door seam (x about 104-164 of 244, y 75-79), which is how a van's moulding looks; fine. The white edge along the roof corner is the body colour against the road, not a halo.

VERDICT (round 1, 7 Nov): PASS
