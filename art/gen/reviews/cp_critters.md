Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), 6 Nov 2026, branch art/cp-critters-06nov at 53eb7a6

Frames (own, not the maker's): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/ g_0120.png (magpie perched at bin, 3x), z_perch.png (5x), fly_all.png (4 wing frames, in game), perch_air.png (perch 3), boat_845.png and boat_880.png (Pepper on the boat, 5x), water.png (hull and water, 8x), side3.png (bench, bin, lamp, boat, Pepper, magpie 3x), mag7.png (the 5 cells, 7x). Level citypark_tall, LOOK_SWEEP at camera y 144. The boat and flight frames used a scratch copy of tests_look.lua (Pepper and magpie placed by env); nothing in the repo changed. asset_qa: magpie WARN (size jump cell 2 to 3, expected for wings up), cp_duckboat PASS, goose WARN. check_backdrop OK.

# Review gate 8: magpie.png (5 cells 32x26)

Scale at 46 px/m: 30 px beak to tail = 0.65 m; a real magpie is 0.45 m (21 px). Pepper is 38 px tall, 52 long (1.13 m). Owner question: the maker picked 30 over a true 21 px and says so. Body alone is 14 px long, the tail is the rest.

1. Scale: PASS (owner question: 30 px vs 21 px true; 6 px ball is nearly head size).
2. Layer: PASS. Character, no look shader; inks #000000 and #1f2336, whites #f5f8fc, darkest of its surroundings.
3. Outline: PASS. 1 px #000000 closed, alpha 0/255 only.
4. Shapes: PASS. Wings up (cell 3) is a white and a grey tip, readable. Wings level (cell 4) is a thin white streak laid back over the tail and wings down (cell 5) is nearly the perched body, so the flap reads weakly, mostly a glide. Minor.
5. Shading: PASS. 9 colours, flat ramps, no mottling.
6. Palette: PASS (9 colours, neutral black and blue-grey darks).
7. View: PASS. Side view.
8. Fit: PASS. As crisp as the bin and bench at 1x and 3x (side3.png).
9. Read: PASS. Perched at the bin the ball sits on the beak tip (z_perch.png), in flight too (fly_all.png): clearly a bird carrying the ball.

Note outside the art: perch 3 (map x 656, y 264) has the magpie standing against the lamp post mid-pole (perch_air.png, screen about (115-135, 100-118)); feet on nothing. It was the same spot for the code magpie.

VERDICT: PASS (owner question: scale)

# Review gate 8: cp_duckboat.png (92x60) with the DUCK BOAT mover at 80 px

Scale at 46 px/m: 92 px = 2.0 m long, 60 px = 1.3 m tall (duck head top at 1.3 m); a pedal swan boat is 2 to 2.5 m. Pepper (52 long) fills 56 % of the deck run; the flat deck between neck and seat is 31 px.

1. Scale: PASS (owner question: the boat grew from 48 to 92 px; 2.0 m is on the small side of a real pedal boat but Pepper fits).
2. Layer: PASS. Play layer, whites #f5fdfe and #bbd3e0, ink #000000, darkest on screen is the ink.
3. Outline: PASS. 1 px ink, closed, 19 colours.
4. Shapes: PASS. Hull curve, gunwale at row 41 and duck head are clean at 5x.
5. Shading: PASS. Flat 3-tone whites, red stripe in two reds.
6. Palette: PASS.
7. View: PASS. Front-on, the gunwale is the deck.
8. Fit: FAIL. The code under the boat (scene.lua 2147-2149) draws a hard-edged tint rectangle the full 92 px of the art, but the hull is only cols 8 to 87, so a pale box sticks out 8 px each side of the hull and below it: screen about x 148-156 left of the hull, y 209-221 (water.png, boat_845.png at crop (240-290, 395-430)). It reads as a glass box around the boat, the same defect class as tonight's glass pillars. Fix in code: tint only the hull width (x0 to x0+80) or follow the hull curve.
9. Read: PASS with owner question. Pepper standing on the boat is drawn over the duck: at the front end (x 845) her head and muzzle cover the duck's face and beak (boat_845.png); at the rear (x 880) she hides the neck and seat but the duck's face stays clear (boat_880.png). Cute either way; the owner may want the front half kept clear.

VERDICT: FAIL (1 item: Fit, the tint rectangle)

# Review gate 8: goose.png (272x102, 34x34 cells, kept as is)

Scale: about 28 px tall = 0.6 m, fine for a goose beside Pepper at 46 px/m.

1. Scale: PASS.
2. Layer: PASS (character, 24 colours).
3. Outline: PASS.
4. Shapes: PASS. Walk and hiss rows are clean; fly row cells r3 c4 and r3 c6 are lumpy (wings lying flat, no clear shape) but short-lived.
5. Shading: FAIL. asset_qa lone pixels 3.5 % (yellow flecks on the neck and beak in every walk frame), 13 blotches of 2-24 px (blue patch on the wing in r1 c1-c8 about (14-18, 26) and a 24 px cluster in r3 c2 and r3 c3 about (10-20, 12-22)), a colour missing in r1 c5, feet move 5 px and size jumps in the fly row (cells 1 to 2, 3 to 4).
6. Palette: PASS.
7. View: PASS.
8. Fit: PASS at 1x (it was crisp in the in-game frame); WARN at 5x on the fly row.
9. Read: PASS.

VERDICT: FAIL (1 item: Shading, fly row and flecks). Not blocking at 1x; the maker kept it on triage.
