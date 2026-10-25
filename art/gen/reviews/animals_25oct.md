Reviewer: independent agent (sonnet), 25 Oct

# Animals review: gull and cat (branch art/animals, after 9cf95af)

Scope: riverwalk/art/gull.png (8 frames, 48 x 44) and riverwalk/art/cat.png (3 rows x 8 frames, 24 x 24).
Method: read BIBLE section 3, rules.json review_checklist, the CHANGELOG entry and tools/build_animals.py; ran
`python3 -I tools/asset_qa.py gull cat` (2 WARN, 0 FAIL, the WARNs are the expected wingbeat size changes, the leap
and flight leaving the ground, and a missing colour in blink frames); looked at every frame at 7x (gull) and 14x
(cat) on a blue ground; scripted checks per frame (bbox, enclosed transparent pixels, lone pixels, non-ink edge
pixels, palette vs art/palettes/riverwalk.gpl); read the code anchors in riverwalk/critters.lua and scene.lua;
built a fit composite (Pepper cell 0, bench, bin, lamp_post, gull f1 and f4, cat idle 1 and run 6) at 1x and 3x in /tmp/rv/.
The pieces were not made by me. Coordinates below are cell coordinates (x, y) from the cell's top left; sheet
coordinates add (col-1) x 48 for the gull, (col-1) x 24 and (row-1) x 24 for the cat.

Headline: both pieces now clearly read as a gull and a cat (the old complaint is largely met: no big holes, the
outline is closed on all 32 gull and cat frames, the animal is recognisable at 1x). Neither is clean yet: the gull has
one see-through pixel in frame 8, is not on the River Walk palette and is 4 to 6 px wider than the owner's 40; the cat
has an ink clot in idle 2 and 7, a tail that pops at the run loop seam, and four sealed 1 px pinholes.

---------------------------------------------------------------------------------------------------------

## GULL (riverwalk/art/gull.png)

1. Scale: FAIL - Owner's size is a wingspan of about 40 px. Measured widths: f1 to f3 and f8 are 44 px (x 3..46), f8 is 46
   (x 1..46), f4 to f7 are 39 to 40; tallest wings-down frames are 32 to 33 px (f4 y 11..42, f5 y 11..43). That is 4 to
   6 px over, outside the 2 px check. Beak to tail is about 37 px, 71 % of Pepper's 52 px nose to tail (a real gull
   is about 55 %), so the body reads chunky next to her, though it is no longer "massive" (the first one was 58). The
   CHANGELOG itself says 44, so the build did not hit the number it was asked for. No resampling is allowed, so the cure is
   an owner decision on 44, or regenerate the still at 40 x 23.
2. Layer: PASS - Play layer character: darkest value is the ink (0,0,1), full contrast white against the sky and skyline in
   gull_screen8_1x.png; nothing in front is lighter than it.
3. Outline: PASS - Every 4-edge pixel of the silhouette is ink in all 8 frames (script: 0 non-ink edge pixels per frame),
   one ink colour (0,0,1), no break. (The doubled seam in f8 is listed under Shapes.)
4. Shapes: FAIL - Frame 8 has a 1 px see-through hole at (25,6) in the far wing, sealed by ink on all four sides, exactly the
   defect the owner rejected. The same frame carries two parallel 1 px ink lines (x 23..24 and x 26..27, y 3..9) where the
   near and far wing outlines run side by side, so the seam is a 5 px wide ink-and-gap band. Frame 6 has one lone pink foot
   pixel at (14,26) where f5 has a 2 row foot (x 14..17, y 25..26) and f3 none: the foot flickers. Round parts are round
   (head, beak, body), wing edges are even staircases, no jaggies seen elsewhere.
5. Shading: FAIL - Flat fills, a 4 step grey ramp (177,189,201 / 146,160,174 / 111,125,135 / 65,76,94 + 45,47,61 for the wing
   tips) over white, no dithering. But lone specks and mottling remain: f7 has 7 isolated pixels in the near wing
   (16,17) (17,18) (18,16) (19,16) (22,19) (23,19) (30,16) that mottle it; f2 has 5 ((14,15) (18,16) (18,19) (29,12)
   (33,12)), f8 has 5 ((28,2) (13,7) (22,18) (20,19) (30,16)), f4 to f6 3 each. Under 2 % of pixels, but the
   checklist says no lone specks, and f7's wing is visibly noisy at 7x. The two darkest wing colours (45,47,61) and
   (65,76,94) are used for 10 px in total and could merge.
6. Palette: FAIL - 0 of the gull's 9 colours are in art/palettes/riverwalk.gpl (the gull lives in River Walk). Nearest palette
   colour by Lab dE: ink 0.3, white 3.7, greys 3.3 to 4.6, wing dark (65,76,94) 9.2, beak yellow (239,196,67) 13.5, foot
   pink (199,130,148) 26.3 (no pink or saturated yellow of this kind in the palette). build_animals.py snaps to the
   animal's own still, not to the level palette. Whites and darks are neutral enough (white 239,241,247 is a faint blue).
7. View: PASS - Pure side view at flight height, wings seen from the side (up, back, down), no top or underside views, no
   insides.
8. Fit: PASS - In the composite (/tmp/rv/fit3x.png) beside Pepper, the bench, the bin and the lamp the gull is as crisp
   (1 px ink, flat fills) and no sparser than they are; it holds up at 1x and 3x. It is a heavy bird next to Pepper
   (see item 1) but it does not look pasted in.
9. Read: PASS - Reads as a herring gull at 1x (gull_screen8_1x.png): white head, grey wings with black tips, yellow beak,
   pink feet, round friendly head. Cute enough for a 7 year old. The eye is a 2 x 2 black block (37..38, 15..16), a
   little blank but kind.

Animation (looped wingbeat, 8 frames): reads as a flap. Sequence: f1 wings up and open, f2 flattening, f3 swept back and low
(the swoop pose, reads as a dive), f4 and f5 wings down, f6 wings folding on the up stroke, f7 rising, f8 up and open,
back to f1. Wing area jumps (448 / 645 / 604 / 437 / 502 / 679 px) are the wing, not a pop. Weak spot: f6 to f7, the near
wing tip goes from hanging (14,37) to raised (16,16) in one frame, a visible hitch at 10 fps, and f6's feet shrink to one
pixel. The head is anchored: eye at x 37..38 in all 8 frames, y 15..16 (y 14..15 in f4 to f6, a 1 px bob), beak the
same x, never loses the eye or outline.

Code anchors (critters.lua): the cell is drawn at (x - 28, y - 18), so cell point (28,18) is the position; mirrored it
is drawn at x + 28 with scale -1, which keeps (28,18) fixed. Body white centroid x per frame 27.1, 28.0, 28.9, 27.8,
28.5, 29.5, 28.2, 27.1 (within 1.5 px of 28) and y 17.0, 18.3, 19.5, 20.0, 19.2, 17.7, 17.6, 16.8 (a smooth 3 px
bob): it stays centred. The 16 x 8 swoop hit box sits on that point, well inside the 44 px sprite (forgiving, fine).
Problem for the nest gull (Cr.drawBird, Rooftops): it draws frame 1 when not flying, so a perched gull stands on its
nest with wings raised in mid flap and feet dangling. Its feet bottom row (27) lands on m.y - 1 as intended.

Verdict: FIX (small). The bird is good; it is not ship-clean.

Fix list (gull)
- f8 (sheet x 336..383): paint ink (0,0,1) at (25,6), sheet (361,6). Optionally thin the double seam: drop the ink at
  (24,5), (24,6) and (23,7) so the wings share one line.
- f7 (sheet x 288..335): recolour the specks (16,17) (17,18) (18,16) (19,16) (22,19) (23,19) to the colour of their neighbours
  in the near wing, and (30,16) to the wing colour; f2: (14,15) (18,16) (18,19) (29,12) (33,12); f8: (28,2) (13,7)
  (22,18) (20,19) (30,16). Merge (65,76,94) into (45,47,61).
- f6 (sheet x 240..287): give the feet the same 2 row shape as f5 (x 14..17, y 25..26) or remove the stray pixel (14,26).
- Palette: snap ink, white and the greys to riverwalk.gpl (all within dE 5); ask the owner to add the beak yellow
  (239,196,67) and foot pink (199,130,148) to the locked palette, or snap them to the nearest and accept a duller beak.
- Size: owner to accept 44 (46 in f8) or order a regenerate at 40 px wide; f8's wing tip at x 1 should come in with it.
- Optional: add a perched frame (folded wings) for the nest gull, or accept the raised wings.

---------------------------------------------------------------------------------------------------------

## CAT (riverwalk/art/cat.png)

1. Scale: PASS - Idle 1 to 8 are 16 x 16 (x 4..19, y 8..23), the owner's 15 to 16 sitting; run frames 3 to 8 are 23 to 24 x 15 to
   16; leap peaks at 22 x 22. Next to Pepper (26 px withers) the sitting cat is 62 % of her height, true scale. Run frames 4
   to 8 use the full 24 px width (x 0..23); the tail tip and nose are closed in ink, not clipped, but have no margin.
2. Layer: PASS - Character on the play layer: ink (1,0,0), full contrast against the Downtown facades in
   cat_downtown_1x.png, no lighter than what is in front.
3. Outline: PASS - All 24 frames: every 4-edge pixel is ink (bottom row exempt as the ground row, as built); one ink colour
   (1,0,0). It thickens to 2 px in places (see Shapes).
4. Shapes: FAIL - (a) Idle 2 and idle 7: the haunch and hind leg are one black clot, a 7 x 2 ink bar at (6..12, 20..21) with a stray
   orange pixel (6,22); the brown tail root and the hind leg that idle 1 and 3 show are gone, so the frame pops between idle 1 and idle 3.
   (b) Run 3: the tail is a ink loop at (1..5, 16..22), filled with black, a knot instead of a tail. (c) Four sealed
   transparent pixels read as dots of background inside the body: run 3 (5,18), run 4 (12,20), run 6 (9,21), leap 3
   (5,19..21), the old "holes" complaint at small scale. Otherwise round things are round (head, ears, haunch), the
   leap arch's three back spikes in leap 3 (x 7..14, y 12..14) are deliberate fur.
5. Shading: PASS - Flat fills, 4 step coat ramp (229,153,70 / 186,102,39 / 158,85,36 / 131,71,35) plus cream (244,217,168)
   and tan (183,145,104), light on the head and back, stripes below; no mottling. A few single belly pixels (cream (11,20)
   in idle 1/3/4/5/6/8, brown (10,20)) could join their neighbours; eye, ear and nose singles are intended.
6. Palette: PASS - Downtown has no locked palette yet (only riverwalk.gpl exists, 0 of 10 colours match it, which is not this
   level's), 10 colours in total (cap 24), neutral ink, no whites. Revisit when Downtown's palette is made.
7. View: PASS - Side view, the face turned a little to the viewer as a cat's would be, no top or insides.
8. Fit: PASS - In the composite beside Pepper, bench, bin, lamp at 1x and 3x the cat is as crisp as they are, the right size and
   dense enough; the ginger is the only warm saturated colour but that makes it findable on the statue.
9. Read: PASS - A ginger tabby cat at 1x (green eye, pink ears, ringed tail) and cute; sits, crouches, arches, leaps and
   runs as asked. It is a bit foxy in the narrow muzzle but never reads as anything but a cat. Run holds its head as high as
   the sitting cat (top y 8..9 against 8), a trotting look more than a stretched gallop.

Animation and anchors
- Idle (8 frames, bbox identical 4..19 x 8..23, eye (14,13) fixed): sit, tail curl, ear twitch, blink; it loops 8 to 1 cleanly
  (idle 8 and idle 1 match). Pops: idle 2 and 7 (clot, above). Blink in idle 5 and 6 is the ear going flat plus a closed eye, fine.
- Leap (scene uses 2 to 4 scared, 5/6/7 in the air, 8 unused): crouch, arch, spring, up, top, down. Eye path (15,15) (16,17) (16,12)
  (17,7) (17,7) (17,12) is smooth, no pop. It reads as a leap. Frame 6 is the highest (lowest ink y 18), frame 7 y 21.
- Run (frames 3 to 8 loop): reads as a run, head steady (eye x 18, y 13..14). The loop seam pops: f8 to f3 the tail goes from
  horizontal at the back (0..6, 11..13) to a hanging knot (1..5, 16..22); f4's tail also droops (0..5, 12..17) where
  f5 to f8 are level. Fix by redrawing f3 and f4 tails level, or looping 5 to 8 (code change, not mine to make).
- Feet line: every frame of idle and run has ink on row 23 (idle paws at x 13..14 always, hind side x 5..10; run: 2 to 11
  px per frame), so with the origin at (12,23) the feet stay put. Leap frames 6 and 7 leave the ground (intended).
  The bbox is centred on x 12 (4..19 idle, 0..23 run), so mirroring about 12 does not shift it.

Verdict: FIX (small). Recognisable, cute and the right size; three local drawing faults.

Fix list (cat)
- Idle 2 and idle 7 (row 1, cols 2 and 7; sheet x 24..47 and 144..167, y 0..23): redraw the haunch and tail root in coat colour
  as in idle 1 and 3: clear the ink at (7..12, 20..21) down to a 1 px outline under the haunch, redraw the hind leg and haunch in coat
  as in idle 1 (x 6..12, y 17..22), keep the tail at (4..6, 20..22), remove the stray (6,22).
- Run 3 (row 3, col 3; sheet x 48..71, y 48..71): replace the tail loop (1..5, 16..22) with the level tail of run 5 (0..6, 11..13) or at
  least open the loop's ink fill to coat colour; run 4 (col 4): lift the drooping tail (0..5, 12..17) to the level one.
- Pinholes: fill (12,20) in run 4, (9,21) in run 6, (5,18) in run 3 with ink, and (5,19..21) in leap 3 with ink or coat, or
  open them to the edge.
- Optional: merge the single belly pixels (10,20) brown and (11,20) cream in idle frames into the surrounding coat.

---------------------------------------------------------------------------------------------------------

## Summary

| Piece | Verdict | Blocking |
| --- | --- | --- |
| gull | fix | f8 hole (25,6); palette not on riverwalk.gpl; 44 to 46 px against the owner's 40 (needs the owner's call); specks in f2, f7, f8 |
| cat | fix | idle 2 and 7 black clot; run 3 and 4 tail pop at the loop seam; four sealed pinholes |

Neither is ready for the owner's board as is; the fixes are pixel edits of under 40 pixels per piece (plus the palette
snap and the size decision for the gull).
