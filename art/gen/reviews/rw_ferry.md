# Gate 6 review: rw_ferry (riverwalk/art/scene/ferry.png, 252 x 79, play layer), 5 Nov 2026

Reviewer: independent (did not make the asset). Method: 5x and 12x nearest enlargements (/tmp/review_water/), numpy
measurements of ink, runs, lone pixels, window components, box lines; asset_qa run; card, board and in-game frames read;
level file diffed; game code read (scene.lua drawProp: image drawn at x = 1560, bottom y = 233, so image row r = world y 154 + r, col c = world x 1560 + c; ferry is not in A.outlined, so no extra 1 px grows around it).

Script: `asset_qa.py --file ferry.png --layer play --level rw` PASS (15 colours, outline 100 %). The script is not the verdict.

## Boxes against the drawn surfaces (measured)
| Surface | Box (level) | Drawn ink top row | Columns of the ink run | Result |
| --- | --- | --- | --- | --- |
| deck | y 206, x 1562-1797 (cols 2-237) | row 52 = y 206 | 2-238 (+ staff 240) | exact on y; 1 px longer than the box at the stern, harmless |
| cabin roof | y 184, x 1620-1740 (cols 60-180) | row 30 = y 184 | 60-180 | exact |
| wheelhouse roof | y 154, x 1657-1705 (cols 97-145) | row 0 = y 154 | 97-145 | exact |

No surface is off by a pixel. `git diff`: riverwalk/level/riverwalk.lua changes only the comment above BOAT (2 insertions, 1 deletion); all box
numbers, FX and the three pile props are unchanged. pepper.png: not in the diff (unchanged).

## asset_qa.md checklist (9)
1. Repeated parts the same: FAIL. The four portholes are pixel-identical (ink + 5 px glint, 11 x 7 interior, stamped at x 71, 93, 115, 137: 22 px apart, rows 41-47): PASS for those. The two wheelhouse windows are NOT the same: left window cols 103-113 x rows 9-19 (105 px of glass, 13 x 13 with ink), right window cols 120-131 x rows 9-17 (96 px, 14 x 11 with ink). Same top row, different heights (bottoms at row 19 and 17) and widths. The build script calls this "windscreen and side window", but at 1x it reads as a drawing mistake. Both fenders (x 36 and 198) and both strake ends are identical.
2. Round things round, symmetric parts symmetric: FAIL. The wheelhouse windows sit left of centre: left margin 3 px of wall (cols 100-102), right margin 12 px (cols 132-143), so the box has an empty right third. Lifebuoy is round and even (13 px, 8 bands), portholes round. Bow rake (18 px over 26 rows) and stern curve (9 px) are even stairs, no jaggies.
3. One light direction, ramps, no dabs: PASS. Upper left: white bow highlight col 3-8, shaded stern; wheelhouse left edge light, right edge grey; cabin left stripe lighter. Ramps: hull fbfbfa / e1e1e1 / b5b9bf / 9c9ea8, wood d49a54 / bf6d36 / a86e3e / 5a2e2a. No dabs.
4. Outline 1 px, one ink colour, no 2 px stretches: FAIL. Ink is #010102 everywhere, no 2x2 ink blocks, hull, cabin, wheelhouse closed (every opaque edge pixel is ink except two). The flagstaff outline is open: its top pixel (row 19, col 239, #f4cc69 yellow tip) has no ink cap above it, and its bottom pixel (row 52, col 239, orange) has transparent below it (the staff hangs 3 px past the hull stern, nothing under it). The script reports 100 % because it counts these as inside; the 12x crop shows both gaps. Fix: cap the tip with ink at (18,239) and root the staff on the deck (see Shapes).
5. Faces: N/A (no characters).
6. Scale against Pepper, slot, anchor: PASS for the slot (252 x 79 OK) and for the route lines (table above). The size itself is a design call (see "Does it read as a Stockholm water taxi" below).
7. Mirrored as the game draws it: PASS (not flipped; Sweden's flag would only be wrong if flipped, it is not).
8. In game: PASS. ingame_ferry_deck/pontoon/wheelhouse frames: Pepper's feet sit on the deck line, hop to cabin roof and held jump to wheelhouse roof coincide with the drawn caps; hull sits in the river, red bottom below the waterline is behind the water as before; lifebuoy reads at 1x as a ring with a hole; portholes read. Pepper's paws on the cabin roof are not hidden by anything.
9. Next to bench, bin, lamp (crisp, clean, same pixel size): FAIL on density. Pixel size and cleanliness match (no semi-alpha, no noise, 15 colours vs bench 16). But the bench has slat bevels, 4-shade ramps on every slat and a shaded seat; the bin has a lid, a coat of arms, gold bands. The ferry is 30 % one flat #e1e1e1 field (3063 of 10342 opaque px) with a 20 x 235 px hull that has no strakes, no rub rail, no cleats, no bollard, no bow detail; the wheelhouse is a 44 x 22 px blank white wall with two windows; the cabin has no door, no handrail. At 3x it looks like a clean vector toy next to the bench. Plainness here reads as unfinished (README review point 1: yes, too plain).

## rules.json review_checklist (9)
- Scale: PASS (boxes exact, slot OK; Pepper unchanged).
- Layer: PASS. On screen darkest 2 (the ink), median 128, light 230: play row (outline, full contrast).
- Outline: FAIL (staff gaps at (19,239) and (52,239), see 4). Everything else unbroken.
- Shapes: FAIL. The flagstaff stands outside the hull: staff cols 238-240, rows 19-52, while the stern wall is at col 237 and rows 53 and below at cols 238-240 are transparent. It is a pole standing in air next to the transom, attached only through the deck-rail row. Move it onto the deck (about cols 230-232, rooted in row 52) or hang it from the transom. Hull curves are otherwise fine.
- Shading: PASS (flat fills, 3-4 shade ramps, no mottling; 63 diagonal lone pixels are the porthole glints at 1 px steps, the lifebuoy checker and the bow stair, all deliberate; no stray specks).
- Palette: PASS (all 15 colours are in art/palettes/riverwalk.gpl; whites neutral, ink neutral; window glass #21273a is a palette navy, chroma 25).
- View: PASS (front-on, a front and a thin cap on each deck; no top view; foredeck planks from the cut are gone).
- Fit: FAIL (item 9).
- Read: PASS at 1x for what it is (a boat, a lifebuoy, a Swedish flag, cute), no text or logos.

## Does it read as a believable Stockholm harbour boat at Pepper's scale?
As a silhouette: a cartoon motor launch (white hull, red bottom, mahogany cabin, Swedish flag), yes, cute and clear. As a believable water taxi: only
loosely. At 46 px/m the cabin side is 22 px = 0.48 m, the wheelhouse 30 px = 0.65 m, the lifebuoy 13 px = 0.28 m (real: about 0.75 m), the windows 0.2 m.
Pepper's back (26 px) is nearly as tall as the cabin. It reads as a toy or model boat, not as a boat people ride in. That is forced by the route's boxes
(the README says so), so it is an owner call, not a pixel defect: either accept the toy reading, or move the boxes. A water taxi also normally has a
forward wheelhouse; here a centred white box on a centred cabin makes a stacked wedding-cake silhouette, which adds to the toy look.

## Must-fix
1. Wheelhouse windows unequal and off-centre: make them identical (both 11 x 11 interior like the left one, or both 12 x 9), stamped 2-3 px in from each wall and mirrored about col 121 (windows at about cols 103-113 and 129-139). Position: left (rows 8-20, cols 102-114), right (rows 8-18, cols 119-132).
2. Flagstaff: open outline at (19,239) and (52,239), and the staff stands outside the hull (cols 238-240).
3. Density: the hull and wheelhouse need the detail the bench has (a rub rail or second strake line, two bollards or cleats, a cabin door with a handle, a handrail or mast on the roofs, panel line on the wheelhouse), while keeping the route lines (rows 0, 30, 52) and one unbroken ink outline.

VERDICT: FAIL (4 items: windows repeated/symmetry, staff outline, staff placement, density next to the bench)

---

# Round 2 (after fix round 1, commit 6c5a228), 5 Nov 2026

Same method (5x and 10x enlargements, numpy, asset_qa, card, board and in-game frames, level diff). asset_qa PASS (16 colours, all in riverwalk.gpl, outline 100 %, no semi-alpha). Level file diff since round 1: none. pepper.png: not in the diff.

## The four round 1 FAILs
1. Wheelhouse windows: FIXED. Both are 11 x 11 glass (107 px each), left cols 103-113, right cols 129-139, rows 9-19, same glint; mirrored about col 121 (left margin 3 px, right margin 3 px). The three portholes (4 before) are identical (47 px glass + 5 px glint, x 69, 89, 109, 20 px apart, rows 41-47).
2. Flagstaff outline: FIXED. Ink cap at (17,231), yellow tip (18,231), shaft cols 230-232, rooted in the deck ink row 52. Zero non-ink edge pixels on the whole sprite.
3. Flagstaff in the air: FIXED. It now stands on the deck at cols 230-232, inside the hull and inside the deck box (box ends col 237).
4. Density: FIXED for the most part (see item 9).

## Checks on what the new detail added
- Route lines still exact: deck ink row 52 = y 206, cols 2-237 (the run now ends at col 237, the box edge); cabin roof ink row 30 = y 184, cols 60-180; wheelhouse roof ink row 0 = y 154, cols 97-145. Cleats stand 3 px above the deck (rows 49-51, cols 19-23 and 207-211) and are decoration, not boxes.
- Dabs: none. The 68 diagonal or single pixels are the porthole and window glints, the lifebuoy octagon corners, the door knob (46,164), cleat edges and the bow stair: deliberate, same ramps.
- Boot top on the water (ingame_ferry_deck_1x, measured): boot line #ce3531 (row 69) on screen luma 97, red bottom luma 54, river behind luma 78, hull grey band luma 160-187, white 229-253. The boot line separates the grey band from the red bottom in colour and in greyscale; the bottom reads darker than the water (54 against 78) and the hull stays readable. PASS.
- New defect: the cabin door's bottom ink row (row 51, cols 153-167) sits directly on the deck ink row 52, so the ink is 2 px thick for 15 px (2 x 2 ink blocks at row 51, cols 153-166). Fix: remove the door's bottom ink row, let the door end on the deck line (the door frame then has ink left, top, right and the deck line below).

## asset_qa.md checklist (9)
1. Repeated parts the same: PASS. Wheelhouse windows identical, portholes identical (20 px apart), fenders (cols 36 and 198) identical, cleats identical (5 px caps), the two hull ends lit/shaded mirror-consistently.
2. Round and symmetric: PASS. Windows mirrored about col 121; lifebuoy is a 15 px octagon with 8 even bands (red, white, dark red, white); bow and stern curves are even stairs.
3. One light direction, ramps, no dabs: PASS. Upper left: white bow highlight, shaded stern, lit left edge of cabin and wheelhouse; hull in lit white (fbfbfa), mid white (e1e1e1), shade grey (b5b9bf, 9c9ea8), orange rub rail (d49a54 / bf6d36 / a86e3e), boot line, red bottom. Lifebuoy is lit top-left and shaded bottom-right.
4. Outline 1 px everywhere, one ink colour, no doubled stretches: FAIL (1 item). Ink #010102 throughout and the staff is closed, but rows 51-52 over cols 153-166 are doubled ink under the cabin door (see above).
5. Faces: PASS (not applicable: no characters).
6. Scale against Pepper, slot, anchor: PASS. Slot 252 x 79 OK; every Pepper surface lands on its box line (table above). The small-boat reading from round 1 stands (cabin 0.48 m, wheelhouse 0.65 m): an owner call, not a pixel defect.
7. Mirrored as the game draws it: PASS (not applicable: the ferry is drawn unflipped).
8. In game: PASS. ingame_ferry_deck, pontoon, wheelhouse frames: Pepper's feet on the deck line, cabin roof and wheelhouse roof; the door, lifebuoy and portholes read at 1x; only the part below the waterline (red bottom) is behind the water as before; cleats and staff never catch her.
9. Next to bench, bin, lamp (crisp, clean, same density): PASS. Same pixel size, 16 colours against the bench's 16, no noise. The hull is now three lit bands, rub rail, boot line, red bottom with two fenders and two cleats; the cabin has a door with a window and knob, three portholes, a lifebuoy and plank seams; the wheelhouse has panel lines. At 1x it matches the bench and bin; at 3x the long white hull is still the plainest area (about 14 % flat e1e1e1 now, 1421 px, down from 30 %) but no longer reads as unfinished.

## rules.json review_checklist (9)
- Scale: PASS (boxes exact, slot OK, Pepper unchanged).
- Layer: PASS (on screen darkest 2, median 128, light 230: play row).
- Outline: FAIL (the 15 px doubled ink under the door; everything else closed).
- Shapes: PASS (staff on the deck, round things round, straight lines straight, even steps).
- Shading: PASS (3-4 shade ramps per material, light upper left, no mottling, no lone specks).
- Palette: PASS (16 colours, all in the level palette; the new lifebuoy red #ce3531 is a palette colour; whites neutral, ink neutral).
- View: PASS (front-on, a front and thin caps, no tops: cleats and door are seen from the front).
- Fit: PASS (see item 9).
- Read: PASS (a cute harbour launch for a 7 year old, lifebuoy and door read at 1x, flag reads as Sweden's, no text or logos).

## Believable Stockholm water taxi?
Better: the door, cleats, rub rail and lifebuoy now give the boat things at human scale to compare with, but the proportions still read as a cartoon launch or toy (cabin knee-high to a person), forced by the route boxes. Same owner call as round 1.

## Must-fix (round 2)
1. Remove the door's bottom ink row at row 51, cols 153-167 (doubled ink with the deck line at row 52).

VERDICT: FAIL (1 item: doubled 2 px ink under the cabin door, row 51, cols 153-166)
