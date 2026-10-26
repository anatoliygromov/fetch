# Maker's note after review round 2 (25 Oct): the round-2 fix list, applied

- rw_lime: bark-coloured edge pixels away from the trunk (x 100-165) take the leaf shade (27,82,17) (clean_lime.py step 4); the dangling grey tails under the crown and on its left edge are gone. The .aseprite holds no hand edits: it is the script's PNG (layer "lime (game)") over the cut (layer "cut (render reference)"), re-imported after the fix; its export matches the PNG pixel for pixel.
- rw_home: the two plaster-brown pixels under the door knobs are the door's dark green now; 18 colours.
- rw_rail_bg: the end piece's post sits at x 80 like every unit, so the last span is 80 px; the rails stop at the post's right side (x 84).
- Not changed (pre-existing, scene.lua Sc.railing): a railing is built from whole 84 px units, so it stops up to 83 px short of its prop (5 px on screens 1-4, 67 px on promenade B). Reported, out of this family's scope.
- Not changed (recorded on the card): the lime's clear trunk 84 px (spec 100) and crown 250 px (spec 230).
