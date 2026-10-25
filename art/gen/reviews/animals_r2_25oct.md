Reviewer: independent agent (sonnet)

# Review: cat, gull, rowboat, round 2 (25 Oct 2026, branch art/animals-r2)

Method: every frame of riverwalk/art/cat.png (24 cells), gull.png (8) and scene/rowboat.png (8) looked at at 5-12x, plus
pixel maps of the suspect cells, frame-to-frame diffs, bounding boxes against the code anchors (scene.lua Sc.cat,
critters.lua Cr.draw / Cr.drawBird, setpieces.lua Sp.drawRowboat) and the in-game frames. Coordinates are (x, y) inside the
cell, origin top left. No file was edited.

## Checklist (art/gen/rules.json review_checklist), answers after the second pass

1. Scale: PASS. Cat 32 px sitting (ask 30; Pepper sits 38), 46 px running; gull wingspan 33-34 px (ask 32); boat hull 182 px
   (ask about 160, real size at 46 px/m, owner's call, B7). Code anchors match the cells (gull quad 36 x 44, anchor 22/23;
   cat origin 24,47; boat DECK 56 = the gunwale's top ink row over the middle).
2. Layer: PASS. Cat 12 colours, gull 7, boat 15, no semi-transparent pixels, ink is the darkest value in each.
3. Outline: PASS. Cat: no open outline pixel in any of the 24 cells (the open ground row 47 aside), the ink bar under the paw in
   leap 2-4 and the lone pixels in leap 5-6 are gone. Gull: closed in all 8. Boat: the hull outside the man and the oar is now
   pixel-identical in all 8 cells (0 differing pixels at x >= 122, spikes above the gunwale gone). Two single ink pixels remain
   inside the cat's fill (S1), too small to fail the item.
4. Shapes: PASS. Cat poses read, run loop 5-8 is a cycle, the idle frames played now all have up ears. Boat blade in cell 4
   is ragged (no ink on its lower edge, a zigzag) but it is at rows 74-95, under the water cut (the game draws rows 0-67), so it never shows.
5. Shading: FAIL (minor). Boat, cells 4-6 (sheet frame 3): the oar shaft above the water still has dark and grey flecks in the
   wood along its length (x 56-96, y 30-60) and darker mottling where it crosses the hull planks (x 56-78, y 52-66), unlike cells 1, 2, 8
   and cells 3, 7, which are clean enough. See R1.
6. Palette: FAIL (one pixel). The grey-white pixel (214,213,218) at (55,57) is still in cells 1, 2 and 8 (the paint stripe
   colour at the end of the gunwale highlight; cells 3-7 have wood colour there). It was fixed in cells 3-7 only. See R2.
7. View: PASS. Side-on in all three; mirrored as drawn they read right.
8. Fit: PASS. Crisp and as dense as the props. As the code now plays them: cat leap 5, 6, 7, 8 (feet on row 47 for 5, 6, 8; frame 7 only
   for vy 60..90, 0.05 s), run loop 5-8 (8 to 5: 521 px, a gait cycle), idle {1 held, 2, 3, 7, 8, 8, 7, 3, 2}; gull 7 frames;
   Pepper stands on the gunwale in rw_boat_pepper.png and rw_boat2.png with no gap. Remaining notes only (S2, S3).
9. Read: PASS. Cat reads cute in idle (ears up in every played frame), run and leap; gull and rower are clear at 1x.

## Second pass (after the coordinator's fixes)

Verified fixed, on the new files: F1 (no ink bar under the paw, leap frames 2-4: frames 2 and 3 now end x 26-30 at rows 45-47
with nothing at x 31-35), F2, F3 (0 open outline pixels in 24 cells), F4 (frame 8 once vy >= 90, lowest row 47; frame 7 still
shows for 0.05 s at vy 60..90), F5 (loop 5-8), F6 (sequence 1, 2, 3, 7, 8, 8, 7, 3, 2, 1; the 3 to 7 step is 214 px, a tail
change, no ear change), F7 (shadow 26 and 34), G1 (% 7 in both places; frame 8 stays in the file as an unused copy of frame 1),
G2 (no pink in any frame; no detached foot bit), G3 (frame 5 wing tip closed), B1 (hull identical in all 8 cells: 0 differing
pixels at x >= 122 and none in the hull band outside the oar), B2 (the spikes at (42,55), (46,55), (17-19,53), (8,53), (180,54) are gone),
B5 (DECK 56: in both in-game frames Pepper's feet sit on the rim, no float).

Still open (R = needs a fix, S = optional):

R1. Boat cells 4, 5, 6: clean the oar shaft above the water. The wood flecks in the shaft between the hands at about (84,35) and
    the hull edge at (56,56), and the mottle over the planks at x 56-78, y 52-66. Take the shaft colours from cell 1 (same line
    positions), or draw the shaft in 3 px of the two oar browns with ink only where cell 1 has it. The blade (rows 74-95) is under
    the water cut and needs nothing.
R2. Boat cells 1, 2, 8: pixel (55,57) is (214,213,218). Set it to (251,219,170), the colour of x 36-54 on the same row.
    (The note "B3 recoloured" applied to cells 3-7 only; cell 3 and 7 have (169,98,54), cells 4-6 (203,143,89) there, which is
    wood and fine.)
S1. Cat leap frame 4: a single ink pixel inside the fill at (30,42); leap frame 6: at (31,23). Replace each with its neighbouring
    coat colour (or leave: they read as fur lines).
S2. Gull: with the feet removed, frame 4 (swoop, and the perched pose) has no legs at all. Fine for the swoop. If the perch is
    ever used (no level uses `look = "gull"` today), the gull needs its own perched frame with feet under the body.
S3. Gull loop 7 to 1 is 410 px and 3 to 4 is 500 px (wings from up to back-flat): jerky but it is a wingbeat; unchanged since the
    first pass, so only a mid frame would cure it. Boat still plays 3 distinct poses (1 1 2 3 3 3 2 1), kept by decision.
S4. Cards: cat still warns "blotches 1" (the dark tail tip, intended), rowboat warns "blotches 13" (plank grain and the coat),
    both WARN not FAIL. Rowboat rim at the bow end (x 0-18) stands 2-3 px above the deck row 56 and the stern end rises to row 40:
    Pepper stands against it, reads as being inside the boat. Fine.

## First pass fix list (history)

### Cat: riverwalk/art/cat.png (cells 48 x 48, rows 1 idle, 2 leap, 3 run; source art/gen/renders/dt_cat30_*_sheet.png, build tools/build_animals.py)

F1. Leap row (row 2), frames 2, 3, 4: a free-hanging ink bar under and beside the front paw, not part of the paw. Frame 2 and 3:
    pixels (31..35, 45), (32..34 or 32..35, 46) and the lone pixel (35, 47). Frame 4: (33..35, 45), (32..35, 46), (35, 47).
    It reads as a line under the paw. Delete these ink pixels (set alpha 0). Frame 4 also has a lone coat pixel at (32, 45)
    that goes with it. In build_animals.py add a rule: after clean(), drop ink-only components below the paw line with no
    fill neighbour, or hard-clear x 31-35 y 45-47 in leap frames 2-4 before outline_complete.
F2. Leap frames 5 and 6: lone ink pixel at (25, 47) under the hind paw (row 47 is the open ground row, so outline_complete
    left it). Delete.
F3. 1 px breaks in the outline (the pixel listed is the open coat pixel without ink beside it): idle frame 4 (7, 28), idle
    frame 8 (2, 36), leap frame 2 (27, 27), leap frame 4 (35, 22), leap frame 5 (23, 44). Paint the ink pixel on the outside
    of each, or re-run outline_complete with those cells not skipped.
F4. Leap frame 7 (cell x 288..335 of row 2): lowest pixel is row 37, the other leap and run frames stand on row 47. The code
    plays frame 7 while falling (vy > 60), so the whole cat pops down 10 px on touchdown (to run frame 4 on row 47).
    Fix in code (scene.lua line 536): use frame 8 (landing, feet on row 47) once vy > 90, or shift frame 7 down 8-10 px in
    build_animals.py (rows[1][6], dy +10, check x 2..46 stays inside). Also note frame 6 (rearing) has its feet on row 47 but
    is the apex, and frame 8 is never played.
F5. Run loop (scene.lua line 537, frames 4-8): 8 to 4 changes about 520 of 700 pixels, tail from level (8) to hanging curl
    (4), and the hind legs differ (frame 4 is the transition from standing). Loop frames 5 to 8 only
    (`row, fr = 3, 5 + math.floor(t * 12) % 4`): the tail goes up, level, level, then up again, which is a gait cycle.
F6. Idle frames 4, 5, 6 (row 1, x 144-239): head silhouette is a flat wedge and the ears are laid back; reads grumpy and
    differs from every other frame. Cheap option in code (scene.lua line 530): drop 4 and 5 from the sequence, e.g.
    `{ 2, 3, 7, 8, 8, 7, 3, 2 }` (frame 7 has the ears up and the eyes closed, 8 eyes open); check the tail jump 3 to 7 (about
    200 px). Proper option: redraw frames 4 and 5 with one ear back only and the head level (0 credits at gate 3 is not enough,
    this needs a regeneration reason in art/gen/ledger.csv).
F7. Shadow: Sc.shadow(x, y - 1, 16) is 16 px wide under a body 32 px (sitting) to 46 px (running) wide. Use 26 for sit and
    scared, 34 for run.
F8. (info only) The card's blotch warning is the darker tail tip at run frame 6, (2..4, 31..36). It is the coat's dark tip, no change.

### Gull: riverwalk/art/gull.png (cells 36 x 44)

G1. Frame 8 equals frame 1 except one pixel at (10, 18). The loop `1 + floor(t * 10) % 8` holds the same pose for 0.2 s. Either
    play 7 frames (`% 7` in critters.lua line 258 and 279, quads unchanged) or redraw frame 8 as the in-between of 7 (wings
    down, trailing) and 1 (wings up and back). Cheapest is the 7 frame loop.
G2. Feet flicker: pink (200,117,133) is in frames 1-4 and 8 at (9..13, 28..30), absent in frames 5 and 6, and a single detached
    2 px pink foot sits at (9..10, 29) in frame 7 next to the wing (it reads as a stray). Either tuck feet in 5, 6, 7 consistently
    (remove the pink pair in frame 7, ink stays) or add the same feet pair under the body in 5 and 6 at (9..13, 28..30).
G3. Frame 5, wing tip bottom edge (27..29, 35) has dark wing colour (45,50,64) and no ink under it (ink only at (30, 36)): close
    with ink at (27..29, 36).
G4. Pose pop 3 to 4 (517 px) and 4 to 5: frame 4 is flat with the wing laid back along the body and a 16 px long dark line at row 25
    (x 4..21), while 3 is fully up and 5 is down. Acceptable for the dive (frame 4 is used for the swoop and reads as swept
    back), but as the 10 fps loop it jerks. Nice to have: a mid frame between 3 and 5.
G5. Perched use (Cr.drawBird, frame 4, feet at y - 31): the feet are at x 9..13, under the tail, 8-10 px behind the body's
    centre (x 21) while the body lies flat, so a perched gull would lean forward like a seesaw. No level uses the gull perch
    now (no `look = "gull"` in riverwalk/level), so it can wait, but do not ship a perched gull with this frame.

### Rowboat: riverwalk/art/scene/rowboat.png (cells 182 x 96; build tools/build_rowboat.py)

B1. The hull is not identical across frames, as the build comment claims. Cells 3 and 7 (sheet frame 2) and 4-6 (frame 3) differ
    from cells 1, 2, 8 on the stern post outline: (181,47), (180,53), (180,54), (175,66), (174,67), (173,69), (168,74), and in
    cells 4-6 also (176,64), (172,70), plus bow outline (8,53) and (20,54) in cells 4-6 and (17..19,53) in cells 3 and 7.
    Set every pixel of the hull away from the man and the oar to cells 1's value (copy cell 1 for x 120..181, all rows, and for
    x 0..30 outside the blade box), then re-lay the oar. The build's `take` mask is too wide at the stern and the bow.
B2. Spikes above the gunwale: cells 3 and 7: (42, 55) and the three pixels (17..19, 53); cells 4, 5, 6: (46, 55) and (8, 53);
    stern (180, 54) in cells 3 and 7. These are 1 px bumps on the deck line, next to where Pepper's feet are, and they flicker.
    Delete them (they are not in cell 1).
B3. Cells 1, 2, 8: a grey-white pixel (214,213,218) at (55, 57), the paint stripe colour at the end of the gunwale highlight.
    Replace by (251,219,170) like its row neighbours (x 36..54, row 57).
B4. Oar: cells 3-7 shaft and blade are mottled and ragged, cell 1, 2, 8 are clean. Redo the oar of sheet frames 2 and 3 as a
    straight 3 px shaft in the same two or three browns as cell 1 (no (85,67,57) grey-brown dither), with a flat blade outline
    like cell 1's; remove the ragged lower edge of the blade in cell 4 around (3..15, 84..88) and its lone ink pixel at the
    blade's bottom. In build_rowboat.py a simple version: draw the shaft as an ink-bordered line between the hands and the blade
    centre from the cell 1 shapes, rotated by whole pixels, instead of taking the animator's pixels.
B5. Deck line vs Pepper: DECK = 54 (setpieces.lua line 63) but the gunwale's top ink row is 53 at x 0..8, 54 at 12..18, 55 at
    24..30, 56 at x 36..66, 54 at 120, 53 at 126..132, rising to 40 at the stern. Her feet float 2 px over x 36..66 and sit 1 px in
    at the bow end. Level the gunwale at the deck: fill rows 54..55 with ink on top and sand under it for x 24..66 in every
    cell (or lower DECK to 55 and accept 1 px either side). The stern rises 14 px above the deck at x 162..181 and Pepper stands
    in front of it, which reads fine.
B6. Rest and stroke: cells 1, 2, 8 are identical and 3, 7 and 4, 5, 6 pairs, so the boat has 3 poses at 8 fps (1.0 s cycle with
    the rower still for 0.37 s). Good enough for the oar, but if a 4th pose from the sheet (frame 4 broke the blade) is not
    usable, play `ORDER = 1 2 3 3 2 1` at 6 fps instead of holding three equal cells.
B7. Size (owner): hull 182, mover 178, ask was about 160. Keep (real size at 46 px/m) unless the owner wants 160; then the
    whole cut would need regenerating at a smaller size, not a resample.

## Order of work

1. F1, F2, F3, B2, B3, G3 and the single-pixel deletions (no credits, a script on the cells).
2. B1 and B5, then B4 (rebuild with build_rowboat.py).
3. Code: F4, F5, G1, F7.
4. F6 and G2 (owner call: cheap code route or redraw).
5. Re-run asset_qa.py on the three files, regenerate the cards and GIFs (the GIFs play whole rows including the unused run
   frames 1-3, and the gull GIF plays frame 8 twice at the loop end), then send to a second reviewer.

## Maker's follow-up (after the second pass)
- R1: the shaft's middle line (within 1.2 px of the oar's axis, above the waterline) now takes the shaft's own most
  common colour wherever the animator left a dark fleck or the seat grey (tools/build_rowboat.py, oar_core). The
  planks under the source pose's oar (x 56-78) stay as the animator drew them, after the blotch pass.
- R2: (55,57) set to the sand (251,219,170) in cells 1, 2 and 8.
- S1-S3 left as accepted. B7 (hull 182 px against "about 160") goes to the owner on the board.
