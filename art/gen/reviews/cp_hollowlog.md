Reviewer: independent gate-8 art reviewer (Claude, did not make this), 7 Nov 2026
Branch day/07nov-cplog at a032b17, worktree review-cplog07. Frames: crawl series (LOOK_CRAWL x 1500 to 1668 every 8 px, LOOK_CRAWLY 328 tall / 184 flat, LOOK_CAM 1450) at 1x and 3x for both City Parks; the switch frames x 1518-1530 and 1650-1658 pixel-diffed against a clean frame; citypark_tall sweep at x 1280, 1440, 1600, 1760, 1920 on all three tiers (15 frames) at 2x and 3x; the flat City Park at x 1280-1760 and with the magpie on perch 6 (LOOK_MAGPIE=6); the tall level with the magpie on its lamp perch (LOOK_MAGPIE=7); Pepper standing at the mouth (LOOK_PX 88 at cam 1450); the layer files at 6x and 10x. Own view formed from the pictures before reading the maker's before_after.png.

# Round 1 (reviewer, 7 Nov)

Owner: "isnt hollow wood suppose to make the dog climb inside? it looks like shes just crawling on the side".

## The piece (park_hollowlog_back.png and park_hollowlog_front.png, 74 x 27, play; box 1553-1625, y 302-309 tall / 158-165 flat, foot +26)

Numbers: log 74 px (1.6 m) long, 27 px (0.6 m) high; the opening's ring 25 px, its hole 17 x 13 px; Pepper crawling is about 20 px high. The lamp is 17 px right of the log's end, the path bone 14 px right of the lamp.

### 1. Crawl frames, does she go IN and come out the far end: PASS
- 1x and 3x, both levels: at x 1540 her nose meets the ring; 1548 her head is in the hole, body outside; 1556-1572 her rear goes in, her black back shows in the dark hole; 1580-1596 nothing of her shows (24 px of travel, about 0.4 s); 1604 her nose comes out from behind the closed right end at the bottom of the log; 1612-1644 she crawls out; 1652 clear. A child sees her go into the log and out the other end. The 3/4 view makes the exit read right: the far end's hole is hidden, so she comes out from behind it.
- Pops: none seen, none measured. The front layer switches to in front of her at x 1523 and back at x 1656. Pixel diff of the log box against a clean frame: 0 pixels differ at 1518, 1520, 1522, 1523, 1524 and at 1658; the only differences at 1526-1530 and 1650-1656 are her nose over the leaf pile and her tail over the path in the log art's transparent corners, which is the same in both draw orders. So the switch happens while nothing of her overlaps a log pixel.
- Hurt inside: Pp:hurt keeps her crouched when there is no headroom (the shell is solid above her), so inLog stays true and the bark stays over her. Standing up inside: impossible, the crouch is held while the shell is over her box.
- One thing to know, not a fail: standing at the mouth (x about 1535-1545) her chest and the top of her head are drawn over the ring's left edge; pressing down there puts the ring in front of her at once. It reads as her ducking into the hole, so it is fine. If it ever shows as a flicker (tapping down at the mouth), make inLog sticky: once true, keep it until her sprite no longer overlaps the log's x range, crouched or not.

### 2. Lengthened bark, seamless at 3x and 6x: FAIL (weak)
- At 3x in game: bark lines run the whole length, no seam row, no step in the outline, the knot at the right and the leaf at the left are once each. PASS at 3x.
- At 6x and in the file: columns 36-51 are a mirror of each other around x 43.5 (36=51, 39=48, 40=47, 41=46 pixel for pixel, 37/50 and 42/45 within 3 rows). It shows as a symmetric pair of dark bark strokes in the middle of the log at rows 8-9 and 15-16, a butterfly. Columns 24-25 also recur at 33-34 and 53-54 (plain bark, not visible). Fix: in columns 44-51 move the two dark strokes 2 to 3 rows (one up, one down) and break the lower one into two dashes; or draw one more knot at x 44-47 in the knot's own ramp. A 10 minute Aseprite edit.

### 3. Still reads as a log: PASS
The old 3/4 log's ring, bark ramp, leaf and rounded far end are kept; longer, it reads as a fallen trunk rather than a stub, which suits "crawl through". Outline 1 px, one ink, unbroken. Light from the upper left (lit top band, dark underside). Shadow on the path under it.

### 4. The moved lamp, the perch and the path bone: PASS
- Lamp at 1642: its post is 17 px clear of the log's rounded end at 1625, base on the lawn behind the path with its plate, nothing touching the log in either level (tall y 144 x 1440; flat x 1440).
- Path bone at 1656: 14 px right of the post, on the path, clear.
- Magpie on the lamp (flat perch 6, tall perch 7): sits on the lamp head. Its tail tip ends 3 to 5 px above and over the left end of the branch ledge to the right (flat ledge at about x 1653, y 108; tall at about x 1653, y 250). Not touching, but close enough that at 1x the tail can read as resting on the ledge. Note only; 4 px further left for the perch (1638) or the ledge's end would clear it.
- Gold bone at 1589 under the shell: hidden by the bark from outside, taken as she crawls through. Right for a secret.

### 5. Flat City Park, perch 6 barked at from the log's top: PASS (fair, obvious)
- Range check from the code: bark reaches 95 px in x and 110 in y; the magpie flees at 40 px when she walks or crawls and at 110 when she runs. From the path left of the log the only legal spot is x 1547-1552 (a 6 px window at the mouth); crawling through brings her within 40 px at x 1602 and flushes it; coming out at 1626 is 16 px away. So the log's top (x 1553-1625, 58 px below the bird, 17-89 px in x) is the spot, and the path window a bonus.
- Reads: on the frame with the magpie on perch 6 and Pepper on the log, she stands level with the lamp head and the bird with the ball is right in front of her nose. A child who climbs the log (she has to, or crawl) is looking at the bird. Fair and obvious. The sneak lesson ("HOLD: SNEAK") already covers the run-up.
- Note: a first-timer who crawls through the log flushes the bird once, then learns the top. That is a fair cost.

### 6. Every screen of citypark_tall around x 1280-1920, all tiers: PASS (15 of 15)
| x | y 144 | y 24 | y 0 |
| --- | --- | --- | --- |
| 1280 | PASS: bin, picnic table, the leaf pile and the log's left half at the right edge | PASS | PASS |
| 1440 | PASS: log, lamp, bone, Pepper standing on the log's flat top (no float, her paws on the top band) | PASS | PASS |
| 1600 | PASS: the log's end leaves the left edge; lamp, bone, the poplar | PASS | PASS |
| 1760 | PASS | PASS: the alder walk | PASS |
| 1920 | PASS: creek and stones | PASS | PASS |
Nothing new floats, nothing touches, the ledges above the log are unchanged.

## Also seen (not failed)
- The leaf pile at x about 1520-1553 now ends against the ring's lower left (the log grew 11 px to the left). It reads as leaves banked at the opening and the hole stays clear; a 6 px shift of the pile to the left would give the ring air.
- While she is fully inside (x 1580-1596) nothing of her shows for about 0.4 s. Fine for a hollow log; two eye pixels in the hole would be a cute touch, not needed.

## Checklist
1. Scale: PASS (1.6 m log, the hole fits her crawl height). 2. Layer: PASS (play values, inside dark, the front in the play look). 3. Outline: PASS. 4. Shapes: FAIL weak (the mirrored bark stretch, item 2). 5. Shading: PASS. 6. Palette: PASS (the old log's colours only). 7. View: PASS (3/4 as the owner's original). 8. Fit: PASS (beside the bench and bin at 3x, same crispness). 9. Read: PASS (she goes into the log).

VERDICT: FAIL on one item (the bark mirror at 6x), everything the owner asked for PASSES. Fix the 16 px mirror and it is finished.
