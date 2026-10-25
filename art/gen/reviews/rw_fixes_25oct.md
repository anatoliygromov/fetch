Reviewer: independent agent (sonnet), 25 Oct

Scope: branch art/rw-fixes, commit 8306f7a, against parent c1c37a4. Method: every asset diffed pixel by pixel against the parent (before/after nearest-neighbour zooms at 7-24x in /tmp, per-pixel dumps), the edit log art/source/rw_fixes/edits.json checked against the real diff, `python3 -I tools/asset_qa.py cloud8 park_log pier skyline gull` run (4 PASS, 1 WARN, 0 FAIL), the five in-game frames in docs/review/25oct/fixes/ looked at at 1x and 3x.

Edit log check: edits.json matches the real diff exactly for all five assets (cloud8 66, park_log 22, pier 766, skyline 86, gull 652 changed pixels; no unlogged change, no wrong colour). The five .aseprite sources exist with layers "before (main v0.6)" and "fixed (game)". No alpha change anywhere except skyline (8 px, the two filled slits) and gull (whole frames moved). Edits are targeted by hand, not a whole-file filter: each file keeps pixels a filter would have caught (see the leftovers below, which are the proof).

One wrong line in CHANGELOG: it says cloud8 had "3 single light pixels made white". The diff has none: all 66 changed pixels became (164,184,205) and no white pixel changed. Correct the line or make the three edits.

## cloud8 (clouds layer, 38x18)

Edit: the 23 Oct flat edge is back to a two-step edge, ring and bottom row now (164,184,205) instead of (174,193,212). Silhouette unchanged (0 alpha changes). The 66 pixels are the ring only; 14 pixels of the old edge shade were left behind.
1. Scale: PASS - 38x18, free-scale cloud; reads as a small distant cloud next to the roofs in screen1 and screen8.
2. Layer: PASS - asset_qa p10 189 (needs 185 or more), contrast 64 (70 allowed), 5 colours (cap 5, so no room for a sixth).
3. Outline: PASS - decoration, no ink: the ring is a darker blue-grey of the cloud itself (luma about 180), not black.
4. Shapes: PASS - silhouette pixel-identical to the parent, no new steps; the edge now runs unbroken round the cap, shoulders and tail.
5. Shading: FAIL - the owner's complaint was the darkest shade. 14 pixels of the near-identical old edge shade (174,193,212) still sit among the new (164,184,205), so the bottom row alternates: row 15 reads E x9, old 19-20, E 21-24, old 25-28, E 29-33, old 34. Same two-near-colour problem the park_log fix removed (a 10-unit difference, invisible at 1x but it is the mottling the checklist forbids and the flat darkest bottom is not flat).
6. Palette: PASS - 5 colours, whites pure (254,254,254). Note: (164,184,205) is a new value, 3 units off the siblings' (161,181,203) in cloud3, 4 and 6. Acceptable because the lift keeps the ladder (the original (161,181,203) gives p10 177, below 185); a one-line note in art_learnings would help.
7. View: PASS - side-on cumulus, a front and a thin cap, no tops or insides.
8. Fit: PASS - screen1 and screen8 at 1x and 3x: crisp, edge slightly stronger than before, consistent with the other clouds.
9. Read: PASS - clear cloud, no text.

Verdict: FIX AGAIN (small, 14 pixels).
Fix list, set to (164,184,205): (21,2); (1,11) (2,11); (32,11) (33,11) (34,11); (35,14); (19,15) (20,15) (25,15) (26,15) (27,15) (28,15) (34,15). I tried it in /tmp: 4 colours left, asset_qa PASS, silhouette unchanged. Minimum if the shoulders are meant to stay lighter: the row 15 and (35,14) pixels only.

## park_log (play-layer obstacle, 40x21)

Edit: 16 orange pixels (166,100,62) merged into (162,110,74) (the 17th became ink); 6 brown pixels made ink (1,8) (38,11) (1,15) (2,17) (3,18) (3,19). Silhouette unchanged.
1. Scale: PASS - 40x21 (about 0.9 m long), sits right beside Pepper, bench and bin in screen1; asset_qa slot clean.
2. Layer: PASS - play row: outline 100 %, full contrast (p10 3, p90 192), 8 colours (cap 20).
3. Outline: PASS - closed: 0 opaque pixels on the 4-neighbour silhouette edge that are not ink (the parent had 1, at (3,19)). 1 px everywhere except five L-corner doubles the edit made: (1,8) (1,15) (2,17) (3,18) and the inward nub (38,11); they thicken the lower-left end cap's arc slightly against the thinner upper-left arc. Cosmetic, not blocking.
4. Shapes: PASS - end-cap ellipse now clean and round, silhouette identical to the parent. Pre-existing and left alone: the black wedge at x30-34, y5-8 and the 2 px stub under the log at (27,19)-(28,20) read as a mouth and a root; fine for a cute log, not part of this fix.
5. Shading: PASS - the two near-identical oranges are one colour, the lit top edge is now one continuous run; dark grain, knot and cut-end ramp kept (8 colours remain). Lone pixels 4.0 % to 2.3 % (asset_qa), noise 0.
6. Palette: PASS - one colour fewer than before, no new colour; ink (9,4,3) near neutral.
7. View: PASS - front-on log on its side with the cut end on the left, no top.
8. Fit: PASS - screen1 at 1x and 3x beside bench and bin: same crispness and density, outline reads solid against the pavement and water.
9. Read: PASS - reads as a log at 1x; the knot looks like an eye, which is cute for a 7 year old.

Verdict: SHIP.
Optional polish (not blocking): turn the L-corner doubles back to the shade colour they replaced where the closing is already done by a neighbour: (1,8), (1,15), (2,17), (3,18), (38,11). Keep (3,19).

## pier (back-layer decoration, 138x162)

Edit: 670 silhouette-edge pixels ink to stone (left edge (158,138,140), right edge (109,95,99), tops and bottoms of ledges stone); 96 interior pixels: the four dotted joints at x67-69 (y48-53, y128-134) and x92-94 (y46-53, y108-113, y130-134) redrawn as solid joints. Silhouette and the 8 baluster gaps (40-41 px each) unchanged. The joints now match the neighbouring ones at 8x; the wall stays a flat fill (11 287 px of one colour, noise 0, blotches 0).
1. Scale: PASS - 138x162 in its hook, a 3.5 m abutment on the back layer, correct beside Pepper in screen7.
2. Layer: PASS - back row: p10 100 (80 allowed), 12 colours (cap 20), the colour set is identical to the parent.
3. Outline: FAIL - decoration has no ink, and 133 ink pixels (24,22,35) are left. Six are orphan black dots at the ledge corners: (8,18) (6,22) (131,22) (3,30) (134,30) (6,147). They were part of the outline; with the outline gone they are specks, and they show at 1x as black dots on the right-hand ledge corners in screen7_1x.png. The other 127 are the foot row y161, x5-131: in game it merges with the dark passage under the pier (screen7), so tolerable, but it is still an ink line on a decoration.
4. Shapes: PASS - straight edges, even steps, balusters and cornice intact, joints straight and continuous. The stone edge is a little soft against the sky but reads as a stone edge.
5. Shading: PASS - ramps of 3-4 stone shades, light from the upper left (lit left edge, darker right edge), no mottling; 1.3 % lone pixels.
6. Palette: PASS - no new colour; stone is a neutral warm grey, the dark is the one blue-black ink.
7. View: PASS - front face with a thin cornice and cap, no tops or insides.
8. Fit: PASS - screen7 at 1x and 3x: crisper and calmer than before, no black fringe on the sky side, same density as lamp and bench.
9. Read: PASS - a bridge abutment, clear at 1x.

Verdict: FIX AGAIN (6 pixels; foot row optional).
Fix list: recolour to the nearest edge stone of the same side: (8,18) and (6,22) and (6,147) to (158,138,140); (3,30) to (109,95,99); (131,22) to (109,95,99); (134,30) to (109,95,99). Foot row y161: either leave (it is the contact line against the passage) or recolour x5-131 to (109,95,99); note it as a decision in the changelog.

## skyline (far city, 320x77)

Edit: 13 hand-picked patches (86 px): near-colour blotches merged into the colour round them, the mauve patch at x169-172, y45-52 (137,125,133 into 130,145,166), the lit patch at x132-134, y16-20 (142,157,178 into 130,145,166) and small 159/161 and 148/152 patches; the two 1x4 slits at x209 and x212, y43-46 filled.
1. Scale: PASS - full 320 px wide silhouettes, true to the layer's slot.
2. Layer: PASS - city row: p10 155 (145 allowed), contrast 19 (35 allowed), 8 colours (cap 8, unchanged set).
3. Outline: PASS - none, no ink, edges are the next haze shade.
4. Shapes: PASS - outer silhouette unchanged (the only alpha change is the 8 slit pixels); spires, domes and the City Hall tower keep their steps. One inconsistency, not a defect: the 1x5 slit in the City Hall tower at (135,10)-(135,14) was kept while the two 1x4 slits at (209,43) and (212,43) were filled; the kept one reads as a window at 1x, so leave it.
5. Shading: PASS - flat silhouettes; asset_qa blotches 0, noise 0.2 %. Candidate patches left are 1-13 px of a 2-unit difference (159/161), invisible, and one 7 px shadow patch at (93,53) that reads as a spire's shade.
6. Palette: PASS - 8 haze blues plus the one warm brick tower, unchanged set.
7. View: PASS - flat silhouettes, no tops or sides.
8. Fit: PASS - screens 1, 6, 7 and 8: no visible change at 1x, cleaner in the 3x zoom, same density as the shore trees in front.
9. Read: PASS - Stockholm skyline reads at 1x, no text.

Verdict: SHIP.

## gull (6-frame flap sheet, 26x26 cells, riverwalk/critters.lua)

Edit: 25 pixels recoloured by hand (5, 7, 4, 3, 2, 4 per frame), eye and beak kept; frames 1 to 6 moved by -2, -1, 0, 0, +1, +2 rows. The red eye pixel (and the beak) now sit on rows 18, 17, 16, 15, 16, 17: an even 1 px bob that loops (17 to 18 at the wrap) instead of 20, 18, 16, 15, 15, 15 (5 px jump at the wrap). Opaque pixel count per frame unchanged (179, 126, 132, 140, 142, 215), nothing clipped. Critter code draws every flap frame at the same anchor and the swoop uses frame 2 only, so the 1-2 px shifts change nothing but the bob.
1. Scale: PASS - 26x26 cells as the hook expects, about 22 px wing span, no slot flag.
2. Layer: PASS - character, never shaded; ink p10 2.
3. Outline: FAIL - 1 px ink (2,2,4) holds on frames 1, 3 and 6. Frame 2 has a new gap at (8,21) in frame (sheet x34,y21): a light (176,183,200) pixel with ink above and below and sky to its left (the parent had a dark grey wing shade there; the edit lightened it). Frame 2 (4,17), frame 4 (8,18) and (19,23), frame 5 (6,24) are dark-grey wingtip pixels on the edge: acceptable.
4. Shapes: FAIL - the size jumps the owner marked are still there and asset_qa still WARNs: frame 1 to 2 179 to 126 px, frame 5 to 6 142 to 215 px (frame 6 is drawn about 50 % bigger than frame 5 and 20 % bigger than frame 1; frame 2 is a flat, thinner bird). The feet jump fell from 5 px to 3 px. A bob fix cannot cure this; frames 2 and 6 need to be redrawn at frame 1's size. The changelog says so honestly.
5. Shading: PASS - lone pixels down (asset_qa 4.7 % to 2.1 %; wings now read as 3-4 flat shades). Cost: frame 2 lost its dark wing shades (59,61,69) and (108,107,110) (4 px), which gives the new asset_qa line "a colour missing in one frame, row 1 col 2". The flat frame hides it at 1x.
6. Palette: PASS - the same 12 colours as before, no new one.
7. View: PASS - side view facing right, as the code expects.
8. Fit: PASS - screen7 and screen8 at 1x and 3x: reads as a gull in flight, bob smooth, heavy ink outline the same as Pepper's.
9. Read: PASS - a bird at 1x; frames 3 to 5 are tucked and read as a dive, which suits the swoop. Beak is only 2 px, small but present (frame 4 has no bright beak pixel, only the dark gold).

Verdict: FIX AGAIN (partial). The stray pixels and the bob are done and sound; the size jumps are not, so the owner's "fix" is half closed. Suggest shipping this state in the meantime and queueing frames 2 and 6 for a redraw.
Fix list: make (34,21) ink (2,2,4) (frame 2, local (8,21)); redraw frame 2 (x26-51) and frame 6 (x130-155) to about 150-180 px, wing span like frame 1, then re-run the bob check (eye rows 18, 17, 16, 15, 16, 17 must hold). Optionally restore two dark wing-shade pixels in frame 2 to clear the new "colour missing" WARN.

## Summary

| Asset | Verdict | Blocking |
| --- | --- | --- |
| cloud8 | fix again | 14 near-colour edge pixels left (list above) |
| park_log | ship | none |
| pier | fix again | 6 orphan black dots (list above) |
| skyline | ship | none |
| gull | fix again (partial) | frame size jumps 179/126 and 142/215 px, one outline gap at (34,21) |
