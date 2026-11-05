Reviewer: independent agent (gate 8), 5 Nov 2026, art/dt-sample-05nov. Judged from the PNG at 5x, numpy, asset_qa and the frames in /tmp/review_dt/frames (tools/dt_sample_frames.sh, 11 screens x camera y 120 and 240). Script PASS not taken as a pass.

Asset: town_crate_leg (16x42), the two stacks of bread crates, end-on, under the board (x p.x0 and p.x1-16 of each SHELTER box: x2048-2063, 2104-2119; 3236-3251, 3292-3307), decoration on the back line.

1. Scale: FAIL - three crates of 14 px each, 42 px in all. The gate crates are 18 px high (same bread crate, other orientation does not change its height), so the shelter's stacks are 22 % smaller than the gates'. Width 16 end-on is fine.
2. Layer: PASS - 169 on screen (S7 y240 legs 138 to 169 depending on the crate face), at or under the plaster; as decoration it sits where back pieces sit, though the same pale value as the play crates.
3. Outline: FAIL - none (asset_qa outline FAIL 0 %, 96 edge px if tested as play). As decoration none is the rule, but the same bread crates at the gates are outlined, so one prop is outlined at one place and not at the next, and the legs carry the board that is outlined.
4. Shapes: PASS - three identical crates, pixel-identical (checked rows), straight. 6 lone pixels = 0.89 % (rivets at x3 and x10, rows 10, 24, 38), under 2 %.
5. Shading: PASS.
6. Palette: PASS - 8 colours, all in downtown.gpl.
7. View: PASS - end-on front view.
8. Fit: FAIL - see 1 and 3; also they are drawn behind the bike while the board is in front of it.
9. Read: PASS - stacks of crates holding a board.

Fix list: build the end-on crate 18 px high (stack 54, board at 48 means three crates would be 54: use two crates of 18 plus a 6 px base, or three crates of 14 with the front crates also 14); outline both or neither.

VERDICT: FAIL (2 items)
