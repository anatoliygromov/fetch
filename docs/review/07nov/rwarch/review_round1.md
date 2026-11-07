# RWARCH review, round 1 (7 Nov)

Independent review of `origin/day/07nov-rwarch` (829361f) against `origin/day/07nov-ground`. I did not make this
work. 0 credits, no image service called, no game file changed. My frames and crops: `review1/` (made from a scratch
copy of `riverwalk/` with a patched `tests_look.lua` that puts Pepper in her crawl frames; the branch is untouched).

## Verdict: FAIL (3 small fixes, then PASS)

The rebuild is a big step up from 5 Nov (navy band) and 6 Nov (shallow dark slot): at 3x and at 1x it reads at once
as a stone arch under the bridge with daylight beyond, in the pier's own stone, and the pier no longer sits on a gap.
Three things would still be called "dirty" or "weird" by the owner at a close look.

## Fixes

1. **Blue notch at both outer corners.** World (1939, 191) and (2068, 191): the pier's plinth has a rounded bottom
   corner (its dark bottom line runs 1940-2067), the arch starts at y 192, so one pixel of river shows through the
   bridge's side line on each side (`review1/corner_notch_x1939_y191_16x.png`). Fill those two pixels with the side
   colours the jambs already use (158 left, 109 right), drawn by the arch (one extra row on `rw_arch.png` at y 191,
   transparent except those two pixels, or a 1 px rect in `archFront`). Both pixels are transparent in `pier.png`,
   so the pier's pixels stay as they are.
2. **Drop the hanging keystone (flat crown).** A keystone sits in the ring, flush with the opening. This one hangs
   3 px below it as an 8 x 3 nub under the plinth, and it is 1 px or less above Pepper's back in her crawl loop
   (`review1/keystone_pepper_back_6x.png`). Without it the ring runs cleanly up under the band course
   (`review1/file_now_vs_nokey_lit_base_6x.png`, bottom). In `build_rw_arch.py`, delete step 4.
3. **The far "trees" read as a green railing.** The band is 2 flat rows with a dark tick every 6 px, so it reads as a
   fence or a balustrade, not trees. Give it a tree line with a bumpy top (rounded crowns 2-3 px high in TREE, TREE_D
   on the underside, no regular ticks), like the level's own tree line seen through the opening.

Also correct the README's explanation of the WARN (see question 3).

## The three open questions

1. **Keystone: drop it** (fix 2). It is wrong as stonework and it brushes her back.
2. **Jamb width: keep 18 px.** At 40 px/s crawl she is over a jamb for under half a second at each end, and she reads
   clearly over the light stone (black, outlined, colour and grey: `review1/crawl_x1936-2074_after_4x*.png`).
   12 px legs under a 130 px block would read thin, close to floating, which is a hard reject. 18 px also matches
   the pier's ashlar.
3. **Contrast WARN 134: do not lighten the vault.** The README's cause is wrong. The arch's darkest (p10 100) is the
   same as the approved pier's (pier p10 100, p90 212, contrast 112, PASS). The extra is at the light end: p90 234
   from the daylight (sky 6.2 % of pixels) and the 243 lit rows (5.1 %). Lightening the vault would not move it and
   would lose the "under the bridge" read. Fix 2 plus the base course's top row 243 to 219 measures PASS in my
   scratch build (`asset_qa.py`, back, rw, fade 0). Do that. If the maker wants the base course's top row to stay
   243 to match the pier's plinth, accepting the WARN is fine: this is the foot of an obstacle on Pepper's line.

## What I checked

- **Read (colour and grey, 3x to 16x):** the same 13 stone colours as the pier, 10 px courses at the pier's pitch.
  The phase does not continue through the plinth, but the plinth hides that. The voussoirs are even and mirrored.
  The vault is deeper and darker, and the far opening sits behind Pepper's middle. The plinth's dark bottom line
  reads as the band course's shadow over the arch. Nothing floats: the jambs stand on the paving at Pepper's line,
  with lit quay paving beside them.
- **Joins:** the passage floor is the real paving, so inside the opening the paving and the ground track's shadow
  run through with no seam. Outside the arch's box (x 1939-2068, y 192-215) not one screen pixel changed against
  the base. The far quay's lit strip meets the shaded floor on a straight line. That is the exit in daylight, not a
  cut.
- **Pepper:** crawl frames 3 to 8 at the centre, and frame 4 at x 1926 to 2086 (LOOK_PX 66 to 226), facing both
  ways. She reads clearly everywhere. She is drawn over the jambs at both ends, as the README says.
- **Pier unchanged:** `pier.png`, `stage.lua`, `arthooks.lua`, `setpieces.lua` and `look.lua` have no diff. On screen,
  0 pixels differ in the pier's box (y < 192) between base and branch. The pier and the arch both take the back look.
- **Notes for the owner, not this track:** the bones at about x 1962 and 2046 (level data) now sit on the springing
  stones instead of the dark slot. Their outline still carries them. The ground track's shadow widens toward the
  viewer on both sides, which suggests light from behind more than "sun upper left". It is unchanged from the base.
- **5 / 6 / 7 Nov:** 7 Nov is clearly the best. 5 Nov is a navy band and 6 Nov a low dark slot with the block
  sitting on it. Nothing of either should come back.

## Checks (run by me, each with a fresh XDG_DATA_HOME, `SDL_AUDIODRIVER=dummy xvfb-run -a`)

| Check | Result |
| --- | --- |
| `tools/check_pepper.sh` | PEPPER UNCHANGED (3908 steps identical) |
| `tools/check_flow.sh` | 125 of 125 passed |
| `love riverwalk --physics` | 56 of 56 passed |
| `tools/check_tiled.sh` | TILED CHECK PASSED |
| `tools/check_backdrop.py` | BACKDROP OK |
| `tools/asset_qa.py --file rw_arch.png --layer back --level rw --fade 0` | WARN: contrast 134 (back allows 120) |
| `tools/build_rw_arch.py --check` | CHECK PASS |
