# City Park tall sweep, round 1 (reviewer, 6-7 Nov night)

Branch night/06nov-cp at d4f6f7d, worktree review-cp. 27 frames of citypark_tall (`LOOK_SWEEP=1 LOOK_STEP=320`, tiers y 144 / 24 / 0) and 9 of the flat citypark, looked at as 2x contact sheets in colour and greyscale, key screens at 3x, details at 6x to 8x. Compared with art/gen/reviews/base_sweep_06nov.md (review/06nov-base).

Fixed since the base review: CP1 empty sky at x 960 (lime crowns now fill it), CP2 trunk pillars at the mid value (trunks now p10 102 against mid 131 and far city 172), CP3 keeper without a face, the willow crowns (one crisp 10 m willow replaces the soft ones), the pond bank slab (shore rows, reeds, pebbles), the floating log at the alder walk end (it sits on the walk's end post at x 1920 y 24 and y 0).

## Screen-by-screen (camera x, y)
| x | y 144 (path) | y 24 | y 0 |
| --- | --- | --- | --- |
| 0 | PASS: gate, leaf pile, log, stump, magpie on perch 1 | PASS | PASS |
| 320 | PASS: bench, hedge (perch 3), lime at 1004 enters at the right | PASS | PASS |
| 640 | PASS: willow, walkway, pond with reeds, pebbles, lilies, stepping stones, duck boat. Minor: the lawn's left corner meets the water in a 1 px vertical edge at screen x 60, y 180-200 | PASS: willow crown fills the sky, Pepper reads on the gold | PASS |
| 960 | FAIL: the three crotch ledges at 1004, 1112, 1216 read as canoes (screen x 10-85, 125-190, 225-295, y 30-70). Minor: trunk feet sawn flat on the lawn. Keeper face PASS | FAIL: same ledges | FAIL: same ledges |
| 1280 | FAIL: canoe ledge Pepper stands on (screen x 115-180, y 70) and the one at 1420 through the trunk. Low bough and its root PASS, goose PASS | FAIL: same ledges | FAIL: same ledges |
| 1600 | FAIL: the oak's ladder of five canoe ledges (screen x 10-120, y 20-150) | FAIL: same | FAIL: same |
| 1920 | PASS: creek pond, stepping stones, reeds, rope walk | PASS: log on the walk's end post | PASS |
| 2240 | PASS: pergola planks with lights, goose, bench, table | PASS | PASS |
| 2560 | PASS: playground, swing, Mia | FAIL: big oak's crotch ledges, the same canoes (screen x 255-320, y 60-200); nest PASS | FAIL: same |

Flat citypark (quick check, y 0 only): PASS except x 640, where three deck planks float inside the willow crowns with no post or limb under them (screen x 30-60, 160-200, 250-300, y 120-130). Pre-existing, the flat level is the fallback, but it is a "floating platform" by the owner's list.

## Top 5 fixes by impact
1. The crotch ledges (cp_bough_* fork pieces): redraw as two tapered limbs with a bark collar, not a lens deck with upturned tips. Fixes 11 of the 27 frames. See cp_limes_pillars.md.
2. Trunk feet: a 2 px dark base row and a 4 px root flare on each lime and the oak so they stand on the lawn instead of ending on it.
3. Pond left corner (x 640 y 144): round the lawn's corner into the water by 2-3 px so the shore has no vertical cut.
4. Goose fly row: replace the twin frame 5 with a wings-level stroke, point the crouch's head forward.
5. Bank pebbles: a fourth shade so they share the stepping stones' ramp; optional.

Write the 10 m willow into docs/art_hooks_r8.md so the spec matches the file.

# Round 2 (reviewer, 6-7 Nov night)

Re-rendered at e4b9c9e: 27 tall frames and the flat x 640. Fixed since round 1: tree feet (roots and 2 dark base rows, PASS), the pond's left corner (the lawn curves into the water, PASS), pebbles (4 shades, PASS), goose cell 5 (PASS with a note), the flat x 640 (the willow trunks now run up through the crowns to the planks; nothing floats, PASS). The canoe read is gone.

Still failing, all for the fork ledges: x 960, 1280, 1600 at y 144, 24 and 0, and x 2560 at y 24 and 0. The lime stubs are shelf brackets (taper the wrong way, plate and gusset) and every fork has a 1 px line through the trunk between its two halves. See cp_limes_pillars.md round 2 for the exact fix. Everything else PASS.

# Round 3 (reviewer, 6-7 Nov night)

Re-rendered at cf27696, x 960, 1280, 1600, 2560 at every tier. The fork ledges now read as limbs with a stub, nothing is drawn over any trunk, the oaks' limbs stop at the bark. All 27 screens PASS. Open optional notes: bark bands on the oak's long limbs, a 2 px bark saddle where a fork's hit box crosses the trunk, the goose cell 5 wing spread.
