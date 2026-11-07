# RWARCH review, round 2 (7 Nov)

Independent review of `origin/day/07nov-rwarch` at 4422a55 (round 2) against `origin/day/07nov-ground`. I did not
make this work. 0 credits, no image service called, no game file changed. Frames and crops: `review2/` (from a
scratch copy of `riverwalk/` with a patched `tests_look.lua` for Pepper's crawl frames; the branch is untouched).

## Verdict: PASS

All three round 1 fixes are done and correct. I found nothing new to fix. The arch can go to the Art Review board.

## Round 1 fixes, checked

1. **Corner notches: fixed.** `rw_arch.png` is now 130 x 25, drawn at y 191. Its top row is transparent except
   for column 0 (158) and column 129 (109). On screen, (1939, 191) and (2068, 191) now show the jamb sides' colours,
   175,145,145 left and 125,103,116 right, the same as the plinth's sides above them. The bridge's outer side
   lines are unbroken from the pier down to Pepper's line (`review2/corner_*_16x.png`).
2. **Hanging keystone: gone.** The opening is clear to y 192. The ring runs up under the band course on both sides
   and reads cleanly, with no nub. Pepper's back no longer meets anything in crawl frames 3 to 8 at the centre
   (`review2/crown_pepper_back_6x.png`).
3. **Far trees: fixed.** It is now a line of rounded crowns of uneven widths over a shaded underside row, with no
   regular ticks. At 1x and 3x it reads as trees on the far quay in daylight, not as a railing
   (`review2/far_tree_line_8x.png`).
4. **Contrast:** with the base course's lit row at 219, asset_qa gives PASS. The vault is unchanged, as recommended.
   The README's WARN text is replaced.

## Looked at again (colour and grey, 4x to 16x)

- **The read:** at once a stone bridge underpass with daylight beyond, part of the same pier. It uses the same 13
  stone colours. The plinth reads as the band over the arch. The voussoirs are even and mirrored. Nothing floats,
  and nothing reads as something else.
- **Joins:** the paving, the passage floor and the ground track's shadow run through with no seam. Against the base,
  screen pixels change only inside x 1939-2068, y 191-215. At y 191 only the two corner pixels change.
- **Pepper:** crawl frame 4 at x 1926 to 2086, and frames 3 to 8 at the centre. She reads clearly against the jambs,
  the vault and the daylight, in colour and grey. She is drawn over the 18 px jambs at the ends, which is accepted.
- **Pier unchanged:** `pier.png`, `stage.lua`, `arthooks.lua`, `setpieces.lua` and `look.lua` have no diff against
  the base. On screen, 0 pixels differ in the pier's box above y 191. The `scene.lua` change is only the draw y
  (`p.y0 - 1`) and comments.
- **Still standing as notes, not fixes for this track:** the bones at about x 1962 and 2046 sit on the springing
  stones (level data, and they still read). The ground track's shadow widens toward the viewer on both sides
  (unchanged from the base).

## Checks (rerun by me, each with a fresh XDG_DATA_HOME, `SDL_AUDIODRIVER=dummy xvfb-run -a`)

| Check | Result |
| --- | --- |
| `tools/check_pepper.sh` | PEPPER UNCHANGED (3908 steps identical) |
| `tools/check_flow.sh` | 125 of 125 passed |
| `love riverwalk --physics` | 56 of 56 passed |
| `tools/check_tiled.sh` | TILED CHECK PASSED |
| `tools/check_backdrop.py` | BACKDROP OK |
| `tools/asset_qa.py --file rw_arch.png --layer back --level rw --fade 0` | PASS (130 x 25) |
| `tools/build_rw_arch.py --check` | CHECK PASS |
