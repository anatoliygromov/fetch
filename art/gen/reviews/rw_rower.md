# rw_rower (SpriteCook cut, arms and oar built per frame; riverwalk/art/scene/rw_rower.png, 6 frames of 74 x 62)

# Round 1 (reviewer, 6-7 Nov night)

Branch `night/06nov-rw` at 4709eeb. Looked at: every frame at 5x on a blue ground, the frames in the hull in the
game at 5x (sweep x 2240, ride shots 3, 4, 8), the ride at 3x (14 shots, both directions), against concept b.
`asset_qa.py --level rw --frames 74x62`: WARN (3.1 % lone pixels, 0.5 % noise, the lowest pixel moves 14 px). The
lone pixels are the eye, nose, beard and the coat's ribbing; the moving pixel is the blade. Not defects.

The owner's three complaints about the r2 boat, judged hard:
- Arm and oar connect: YES in all 6 frames. The fist sits on the handle end; the oar runs from the fist over the
  rail to the blade.
- The stroke makes sense: YES. The oar is a lever about the rowlock (hull x 97) in every frame: fist and blade on
  opposite sides of it. Frames 1-4: fist goes out then in, blade sweeps stern to bow low in the water (catch,
  drive, drive, finish). Frames 5-6: the blade comes back high, the fist goes out again. Pulling moves the boat
  stern first, which matches him facing the bow. Going left the loop runs backwards (backing water): fine.
- Hull: see rw_rowboat.md (PASS).

| Item | Result | Evidence |
| --- | --- | --- |
| Scale | PASS | cap top 2 px under Pepper's head on the deck; face 12 px; a grandpa, not a child |
| Layer | PASS | play, drawn after the hull; the coat's bottom row sits on the rail row so he reads as seated inside |
| Outline | PASS | 1 px ink round head, cap, coat, arm and oar in every frame |
| Shapes | FAIL | the near arm is a straight 4 px tube from shoulder to fist in frames 1, 2, 4, 5, 6: the two 12 px bones are collinear, no elbow, it reads as a stick at 1x and 5x |
| Shading | PASS on the torso, FAIL on the arm | the sleeve is one flat blue with no highlight row; the torso and face are crisp SpriteCook pixels |
| Palette | PASS | 20 colours on the sheet; the oar is the hull's honey, see fix 3 |
| View | PASS | side view at Pepper's height |
| Faces | PASS | eye, nose, mouth under the beard in every frame; nothing boils (the torso is one stamp) |
| Animation | FAIL (one point) | frames 5 and 6 ("return", and the rest frame 5): the blade sits on rows 45-48, right on the waterline, so it looks like it is still dragging in the water; the lifted blade does not read |
| Fit | PASS | as crisp as Pepper beside him |
| Read | PASS | a child reads an old man rowing |
| "Terrible?" | No | but the stick arm is the one thing left that looks drawn by code |

Verdict: FAIL, two small fixes, both in tools/build_rw_rowboat.py (the arm and oar keys), no credits.

Fixes:
1. Elbow. Key the elbow 3-4 px below the shoulder line and 6-8 px towards the fist, so upper arm and forearm make
   a visible bend in frames 1, 2, 4, 5, 6 (frame 3 is nearly right). Add one row of the lighter sleeve blue along
   the top of each bone. Keep the 1 px ink.
2. Lifted blade. In frames 5 and 6 raise the blade 4-5 px (rows 40-43) by lowering the fist 2 px; the shaft then
   clears the ripple row. Frame 5 is also the rest pose, so the boats at the quays stop looking like they drag an
   oar.
3. Oar against hull. Where the shaft crosses the hull it reads only by its 1 px edge (same honey as the planks).
   Either a grey-brown ash shaft (two shades) or the hull one step red-brown (rw_rowboat.md).
4. Optional: the far fist, 2 px, behind the near fist on the handle (concept b has both hands on the oar); a 3 x 3
   dark iron rowlock on the rail at hull x 97, drawn over the oar.

Note for the producer: the three concept PNGs (`art/gen/concepts/rw_rowboat_concept_a/b/c.png`) are untracked in
the maker's worktree `/home/claude/wt/rw` and are not on the branch. The README points at them. Commit them.

# Round 2 (reviewer, 6-7 Nov night)

Branch `night/06nov-rw` at df396bb. Sheet now 468 x 62 (6 frames of 78). Looked at: every frame at 5x on blue,
the rower in the hull at 5x (ride shots 3 and 9, sweep x 2560), the ride 14 shots both ways with Pepper aboard and
with the boat empty. `asset_qa.py --level rw`: WARN only (3.3 % lone pixels: eye, beard, coat ribbing; 0.5 % noise).

| Fix | Result | Evidence |
| --- | --- | --- |
| 1 Elbow | PASS | the near arm bends at the elbow in all 6 frames, a lighter row along the top of each bone; upper arm and forearm read as two parts at 1x and 5x |
| 2 Lifted blade | PASS | frames 5 and 6 carry the blade on rows 39-41, 7 px clear of the ripple row; the resting boats at the quays and the empty boat (shot 9) show an oar held up, not dragging |
| 3 Oar against hull | PASS | grey-brown ash shaft in two shades, reads across the mahogany hull and the water |
| Stern thwart (rowlock hull x 150) | PASS | he sits at the transom, cut at the rail; the lever geometry still holds about the rowlock in every frame; Pepper rides amidships clear of him in play. The sweep's fixed placement (cam + 140) can still put her over him, which is the harness, not the art: he is behind her, nothing covers her |
| Both directions | PASS | pulling right, loop backwards left; the wake trails from the end it leaves |
| Fist on the handle, faces, outline | PASS | all 6 frames |

Verdict: PASS. Finished. The far fist and a visible rowlock remain optional.
