Reviewer: independent (sonnet)

# Round 2

Branch art/dt-sample-05nov at 0c95386 (Downtown tall, owner picks 1a and 4a). Method: 36 fresh frames from tools/dt_sample_frames.sh (camera x 0, 320, 640, 960, 1180, 1280, 1560, 1600, 1700, 1840, 1920, 2040, 2240, 2400, 2560, 2880, 3000, 3200 at y 120 and 240), colour and greyscale views, Rec.601 luma by colour on the frames, the level lua read by script, asset_qa per file, a bike injected into a copy of the repo (x2090, x1905, x3250) to check the rider. Round 1 is in review_round1/.

## Round 1 findings, one by one

| Round 1 FAIL | Now |
| --- | --- |
| Back lighter than far (plaster 179, gateway 192) | FIXED. Houses 145.4 to 156 on screen (red 145.4, stone 147.9, ochre 150.5 to 152.2, cream 156); old town row 168.5, far roofs 169 (far city 187 to 194). |
| Perches as light as the wall (179) | FIXED. Crates, legs 104 to 107, board planks 104 to 128; apple crates 111; plaster 150; Pepper 14 to 24. |
| Crate sizes 35, 32, 14 | FIXED. One crate, 17 px high, 18 px pitch, front 34 wide, end-on 16. |
| Crate legs unoutlined | FIXED. Outlined, two whole crates each. |
| String courses unequal, 144 apart | FIXED. Identical at rows 0, 140, 280, pitch 140. |
| Shelter glints, contrast | FIXED for the glints. NEW: the poster card is 194 (see item 2 of town_shelter_tall). |
| Gateway a slab across a seam; alone on screen 10; palette | FIXED. 80 px arch inside the house x1912-2000; no gateway on screen 10 (the old brick gate stays there); palette complete. |
| Hood floating | FIXED. Removed; the dormer's box x1920-1976, y264 is a plain stone ledge. |
| Guild house a stub, 1a not done | FIXED in structure (full height, own front, portal top, oriel). The oriel itself FAILS (scale, layer, read) and the front's windows are clipped. |
| Rider cut at the waist | FIXED. Checked with a bike at x2090 and x3250: the rider passes in front of board, legs and shelter, uncut. |
| asset_qa fade | FIXED (it prints the fade it used). |
| Dollhouse plaza houses, lamps on facades, shelf-like ledges, far layers hidden, street ends | NOT FIXED (left for the owner, as the builder says). Listed below. |

## The nine items, applied to the screen

1. Scale: FAIL - door 93 px, storeys 140, shelter 115, gateway 138, gate crates 17 px, end-on crates 17 px, board 48 up as before: all fit. Two faults: the oriel's window is a fifth of the house's windows (town_oriel); on screen 10 the GATE (x3072-3168) keeps the old brick gate, 36 px tall (0.78 m), so decision 4a is not carried out there and the 77 px cargo rider (zone x3120-3300) still dwarfs its hiding place.
2. Layer: PASS - far city 187 to 194 > far roofs 169 > old town row 168.5 > houses 145 to 156 > perches 104 to 128 > Pepper 14 to 24 (S10 and S7 frames). Small exceptions: window frames and sills 171, the shelter's poster card 194 (a piece FAIL), the oriel's body 150 (a piece FAIL).
3. Outline: PASS - perches (crates, board, legs, portal top, oriel, ledges) have a 1 px ink outline, in colour and greyscale; shelter, gateway, fronts have none. One notch in the board (town_breadboard, x73,y8) is listed there.
4. Shapes: FAIL - fronts 1 to 3: windows and courses pixel-identical. Front 4 (guild house, x1552-1700): both windows touch the house edges and the right one is clipped by 2 columns (town_front_tall4). Board outline notch.
5. Shading: PASS - one light direction, ramps per material.
6. Palette: PASS - every file colour is in downtown.gpl (built from these pieces, so by construction). Draw-time plasters are not in the files. Note: houses at 145 to 156 with panes at 124 are drab brown and rose next to the lively old town row; owner's eye.
7. View: PASS - fronts, gateway, shelter, portal top, oriel are front-on and flat.
8. Fit (context): FAIL - faults below.
9. Read: FAIL - the oriel reads as a chimney with a window on top of the gable (x1627-1645, y199-243), not as a bay window.

## The seven checks from the brief

1. Repeated parts identical: FAIL (front 4's windows; board notch). Fronts 1 to 3, crates, legs, shelter, gateway pass.
2. Perch against decoration, 1x and greyscale: PASS - board, crates, legs, ledges, portal top, oriel have outlines and sit darker than the wall (oriel excepted); shelter, gateway, fronts are flat backdrop. Cautions: the oriel's body equals the wall; the shelter's roof bar (x2014-2154, y299-307) still looks like a ledge but is out of reach.
3. Nothing Pepper stands on moved: PASS - git diff ops/spritecook-05nov..0c95386 is empty for maps/, riverwalk/level/ and pepper.png. Portal top: all 11 steps' art tops equal the box tops minus the outline row (x1560 y271 to the plateau x1616-1656 y243). Oriel at (1627,199) on the box x1628-1644, y200-244; the golden bone box x1628-1644, y188-200 is where it was, 12 px above the roof. Crates and board at the old boxes (x0-1, y0-1); legs under the board's last row.
4. Scale: FAIL (oriel; screen 10 gate), see item 1.
5. Value order: PASS - numbers in item 2 (far 168 to 194 > back 145 to 156 > play 104 to 128 > Pepper).
6. Context faults: FAIL, list below.
7. Crispness against rw_home: PASS - lone pixels 0.00 % (fronts, crates, legs, portal top, oriel), 0.10 % (shelter), 0.11 % (board), 0.34 % (gateway); no semi-transparent pixels; flat walls.

## Context faults that remain (screen x, y)

- Guild house, screen 6, x1552-1700: the oriel (x1627-1645, y199-243) is a small turret on the gable; the portal top (x1559-1681, y243-293) is a 122 px pediment over a gate that the iron balcony (x1552-1608, y344) and the plaza houses (x1536-1624, x1644-1724) cover; the front's windows touch both seams (x1552, x1700).
- Street lamp at x1958 stands in the middle of the new archway (x1916-1996), on screen 7. High road lamps x1830 (screen 6) and x2420 (screen 8) still stand across window panes.
- Plaza houses as dollhouses (door 25 px beside a 93 px door storey): x1536-1624 (screen 5), x1644-1724 and x1832-1900 (screen 6), x2404-2492 (screen 8). Owner decision 2 was not picked.
- Screen 10, x3072-3168, y388-424: the old brick gate, 36 px, in front of the old town row; no gateway, no 4a scale; the cargo rider is twice its height. At least it no longer stands alone as a slab.
- The DORMER ledge, x1920-1976, y264: a plain ledge 12 px above the arch's keystone (y270 to 276): reads as a lintel. High road ledges x2016-2072 and x2112-2168 (and the balcony x1328, y272) still read as stone shelves stuck to the facade.
- The cargo bike is clipped at its depot (x1938 for zone 1, x3168 for zone 2): now drawn in front of the crates, it pops out at that vertical line, not behind anything (checked at x1905). Minor.
- Far layers (spire, far roofs, old town row) are hidden by the fronts from x1180 to 2480 (screens 4 to 8); the street ends are hard: x1180, x2480 (then a 160 px sky gap), x2640-2736.
- No front's top shows: all run to y -18 (checked at camera y 0 and 120). No front ends in mid-air.

VERDICT: FAIL (4 items)


# Round 3

Reviewed bca1ab9 with 36 fresh frames (camera x 0 to 3200, y 120 and 240). Round 2's open FAILs: front 4's windows (FIXED: whole, margins 14 and 12), the poster card (FIXED: 150 on screen), the board's outline notch (FIXED), the oriel (CHANGED: a 58x36 bay window of the house's scale plus a copper roof cap; the bay passes, the cap fails on its hit box). Pass pieces unchanged (crates, legs, portal top: 0 px differ; the fronts, gateway and shelter: pane or poster colours only). maps/, riverwalk/level/ and pepper.png still unchanged against the base. Darker panes: 99.9 on screen against plaster 145 to 156 (contrast 46 to 56, back range 100 to 171, within 120); 0 lone pixels in the fronts; the grid is crisp.

1. Scale: FAIL - screen 10's GATE (x3072-3168) is still the old 36 px brick gate, decision 4a is not carried out there and the 77 px rider (zone x3120-3300) is twice its height. Everything else fits (the bay window is 58 wide like the house's windows).
2. Layer: PASS - far city 187 to 194 > far roofs 169 > old town row 168.5 > houses 145 to 156 > perches 104 to 128 and the copper cap 88 to 113 > Pepper 14 to 24; the poster and bay are no longer above their neighbours.
3. Outline: PASS - perches outlined, decoration not; the board's outline is closed.
4. Shapes: PASS - every window equal across all four fronts (0 px differ), courses identical, 0 to 0.34 % lone pixels.
5. Shading: PASS.
6. Palette: PASS - 0 colours outside downtown.gpl (built from these pieces). Houses stay a calm brown and rose; owner's eye.
7. View: PASS - flat front-on pieces.
8. Fit (context): FAIL - (a) the CHIMNEY's 16 px solid box in the middle of a 58 px bay and a 60 px roof (town_oriel item 8): invisible wall on the plateau at x1628 and x1644, a passable roof slope; (b) the remaining faults below.
9. Read: PASS - the guild house reads as a house with a portal and a bay. The street lamp at x1958 in the middle of the archway reads as a lamp in front of a gateway to a child's eye, and the bike passes in front of it: an owner note, not a defect.

Context faults that remain (screen x, y): the plaza houses as dollhouses, door 25 px (x1536-1624, x1644-1724, x1832-1900, x2404-2492; decision 2); high road lamps across window panes (x1830, x2420); ledges as shelves (x2016-2072, x2112-2168; the dormer ledge x1920-1976, y264 reads as a lintel 12 px over the keystone); the old brick gate on screen 10 (x3072-3168); the bike clipped at its depot (x1938, x3168); far layers hidden from x1180 to 2480; hard street ends at x1180, x2480, x2640-2736; guild house storey 2 bare wall around the bay (x1552-1700, y141-227). No front's top shows.

VERDICT: FAIL (2 items)
