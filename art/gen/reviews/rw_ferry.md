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
