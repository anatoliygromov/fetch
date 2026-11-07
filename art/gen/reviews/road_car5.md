# Gate 8 review: road_car5

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. Looked at the file at 5x beside the approved bench and bin, in the game at 1x and 2x (my own shots, a local copy of tests_look.lua with a still-vehicle hook; the branch is untouched), colour and greyscale. `python3 -I tools/asset_qa.py --file` run on every file. The maker's notes (docs/review/07nov/chars/README.md) read after the verdicts were formed.

Piece: riverwalk/art/scene/road_car5.png, 250 x 89 (silver estate), wheels only, near lane (55 px/m), only the top rows show above y 192.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Repeated parts the same (wheels, door handles, glints) | PASS | The family wheel stamped at both axles (23 px tyre columns; the 38 px that differ in the lower 40 rows are the arch surroundings, not the wheel). |
| 2 | Wheels round, spokes even | PASS | Five-spoke rim, round tyre, no lumps at 5x. |
| 3 | One light direction, ramps, no dabs | PASS (note) | The body is the old render: the bonnet edge (about x 10-70, y 36-40) is a stair of single lighter pixels, the rear corner (x 236-248, y 40-60) has a soft two-shade edge. Script noise and stray under the caps. |
| 4 | Outline 1 px, one ink | PASS | One dark ink around the silhouette, unbroken; the pillars and wheel arches are the same ink. |
| 5 | Faces, hands (driver) | PASS (note) | No driver: the glass is a dark tint with glints. The other four cars have a driver. Allowed for one car, but it is the odd one out. |
| 6 | Scale against Pepper, slot | PASS | Slot per tools/asset_qa.py SLOTS; the roof sits under Pepper's feet line in the shot (my car shots, River Walk x 760). |
| 7 | Mirrored as drawn | PASS | Drawn flipped for the right-hand lane; reads the same. |
| 8 | In game, the part that shows | PASS | Top 48 rows show over the road: roof, glass, driver, door tops. Reads as a car passing close at 1x and 2x, colour and grey. |
| 9 | Next to bench, bin, lamp | PASS | As crisp as the bench at 5x; no lone pixels in the fills (script PASS). |
| R | Checklist scale, layer, outline, shapes, shading, palette, view, fit, read | PASS | 20 opaque colours; script PASS on noise, stray, blotches, specks, pinholes, outline, colours, ladder. A child reads it as a car at 1x. |

Notes: The wheels now match cars 1-4 and the owner's note (wheels need some work) is answered. The body is the old render and reads as a different family beside 1-4 at 5x: dark tinted glass without a driver, outlined oval door handles where 1-4 have a 1 px bar, a noisier bonnet edge. In the game at 1x and 2x (only the roof and glass show) it passes as one of the cars.

Fixes: Optional, 0 credits: rebuild car 5 with tools/build_cars_n07.py on its own silhouette (glass ramp, driver, the 1 px bar handles) so the five cars are one family at 5x.

VERDICT (round 1, 7 Nov): PASS
