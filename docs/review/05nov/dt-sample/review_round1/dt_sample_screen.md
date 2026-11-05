Reviewer: independent agent (gate 8), 5 Nov 2026, branch art/dt-sample-05nov (Downtown tall, owner picks 1a and 4a).
Method: 22 frames from tools/dt_sample_frames.sh (screens 1 to 11 at camera y 120 and 240, plus x1700, 1840, 2040, 2400, 3000), colour and greyscale, 2x and 5x views, numpy luma (Rec.601) on frame regions, the level lua read by script, asset_qa per file. Builder's README read last; its seven doubts are all confirmed below.

1. Repeated parts identical: FAIL
   - PASS: windows. Storey 2 and storey 3 pixel-identical (0 px differ), identical across town_front_tall1-3, 58x87, 9 equal panes; every window on screen is centred on its house (x1343, 1422, 1496, 1937, 2025, 2115, 2219, 2321 pane starts). Shelter panes 64 and 64 px, posts 4 px; gateway jamb courses identical both sides. Crates identical within each file.
   - FAIL: the string course differs between storeys, rows 136-139 (4 rows, no shade) against rows 280-286 (5 rows plus 2 rows shade), 144 px apart against window pitch 140 (town_front_tall1-3, all houses, seen at camera y under about 112).
   - FAIL: bread crates 35x18 (town_crates70) and 32x18 (town_crates96) and 14 px high end-on (town_crate_leg).
2. Perch against decoration, 1x and greyscale: PASS
   - The board (x2047-2121, y375-381; x3235-3309), the crates (x1867-1938 and x3071-3168, 37 px) and the hood (x1920-1978) read as pieces to use: dark 1 px outline, in colour and in greyscale. The shelter glass and posts, the gateways and the facades read as backdrop: no outline, flat, out of reach.
   - Cautions: the crate and board fills are the wall's value (see 5), so the outline alone carries it; the legs (no outline, 169) are weak; the shelter's flat roof bar (x2014-2154, y299-307, 125 px up) looks like the high road's stone ledges at x2016-2072 and x2112-2168, unreachable from the board (77 px up).
3. Nothing Pepper stands on moved: PASS
   - git diff ops/spritecook-05nov..HEAD is empty for maps/, riverwalk/level/ (so maps/downtown_tall.tmx and riverwalk/level/tiled/downtown_tall.lua are unchanged) and for pepper.png and rw_home.png.
   - Art against boxes: GATE crates drawn at (x0-1, y0-1) 71x37 over the 70x36 box at y388 (street 424); SHELTER board at (x0-1, y0-1) 74x7 over the 72x4 box at y376; legs end at y423, board bottom y381, 42 rows. Pepper's feet land on the first light row of each. Same outline-outside-top-left convention as the other props. DORMER hood at (x0-1, y264-1) 58x19 over 56x6.
4. Scale to Pepper (26 px at the withers, 46 px/m): FAIL
   - PASS: door 93 px body (2.0 m) with lintel 108; storeys 144; shelter 115 (2.5 m); gateways 138 (3.0 m); gate crate 18 px (0.39 m), stack 36 = the old perch height; board 48 up as before.
   - FAIL: the shelter's end-on crates are 14 px high (town_crate_leg) against 18 px at the gates. Not fixed by the plan's numbers: the plaza houses (door 25 px, 0.55 m) are untouched, see 6.
5. Value order far > back > play > Pepper, Rec.601 on the frames: FAIL
   - Far: old town row 168 (S10 y240 x0-130), far roofs 169, far city 187, clouds 236.
   - Back: plaster 179.5 (cream/orange; salmon 154), gateway stone 192 (p90 225), shelter glass 154 with glints at 215. Back is lighter than the far row and roofs: broken (the builder's "back 169-179" table row leaves the far rows out; the plan's target was 154).
   - Play: bread crates 179 (S10 y240), board 179, hood 189: equal to or lighter than the back plaster. The existing play crates and tubs on the same street are 111 (S1 apple crates, S5 tub). New perches 68 lighter than their neighbours.
   - Pepper: p5 about 1 to 25, median 58 to 97 in her box: darkest. 
   - Greyscale 1x at S7 and S10: the gateway slab (S10) is the brightest large shape after the clouds; the crates are pale blocks of the same grey as the wall.
6. Context faults: FAIL (positions below)
7. Crispness against rw_home: PASS
   - Lone pixels: fronts 0.00 %, gateways 0.17 and 0.19 %, shelter 0.12 %, hood and crates 0.00 %, legs 0.89 %; 0 semi-transparent pixels; flat walls; no jaggies beyond the arch's even steps. Weak spot: the shelter glints (dashed 1 px diagonals, white). rw_home has more detail (lantern, curtains, quoins); the fronts are plainer and calmer, which suits the back.

Context faults, screen x (world) and y:
- Screen 10, x3050-3190, y276-414: town_gateway96 stands alone on the flooded square with no house behind it, a free-standing stone slab with a flat cornice top, 192 luma against the far row 168 (frames x2880, x3000; builder doubt 3).
- Screens 6 and 7, x1846-1960, y276-414: town_gateway70 is a rectangular stone block straddling the seam between two houses (x1912), the plaza house x1832-1900 and its balcony (x1840-1896, y344) cover its left half and the street lamp at x1958 stands on its edge. Three overlapping buildings read as clutter.
- Screens 6 and 7, x1920-1978, y263-282: the hood (the dormer's replacement) hangs over the gateway's right shoulder and the shop front with no window beneath it (nearest sill 36 px up): a floating bracket.
- Screen 6, x1552-1700, y282 top: the guild house is still a one-storey stub with the stepped gable (stays cut) and the chimney (about x1628-1645) between two three-storey fronts: a sky notch 148 px wide at both cameras. Owner pick 1a turned the gable into a portal top and the chimney into a bay window's roof; not done here. The flower roof (x2288, y232, screen 8) became window boxes under a window: fine.
- Plaza houses as dollhouses, door 25 px against 108 px next to them (owner decision 2 not picked, builder doubt 2): screen 5, x1536-1624; screen 6, x1644-1724 and x1832-1900; screen 8, x2404-2492. Each is 118 px tall with three storeys of two to three windows, in front of fronts with 87 px windows.
- Cargo-bike rider cut at the waist: shelter board y375-381 is 43 to 49 px above the street on a 77 px rider (56 to 64 % up): x2047-2121 (zone x1930-2120) and x3235-3309 (zone x3120-3300). The bike is drawn in front of the shelter and its legs (back decoration) but behind the board (play), so the board hangs in front of him, in front of his torso, while the legs stand behind him. Also the gate crates (37 px, 48 %) cut him at the hip at x1867-1938 (zone from x1930) and x3071-3168 (zone from x3120); that cut existed before.
- Lamp against a facade: street lamp x1958 (screen 7) on the gateway edge and shop front; high road lamps x1830 (screen 6, post across a window pane) and x2420 (screen 8, post across a window); wall lanterns (decision 5) not done.
- High road ledges x2016-2072 and x2112-2168 (screen 7, y about 248 and 266) and the balcony at x1328 (screen 5) read as stone shelves stuck to the wall (builder doubt 4): decoration-like without windows or brackets to hold them.
- Far layers gone: the full-height fronts hide the spire, far roofs and old town row from x1180 to 2480 (screens 4 to 8); the spire shows on 1-4 and 9-11 (builder doubt 1). Layer depth is lost on the high road camera, where fronts fill 96 % of the frame.
- Street ends: x1180 (first front, hard left edge with the old town row beside it), x2480 (hard right edge, 2 px shade, then a 160 px sky gap to x2640), x2640-2736 (a lone 96 px slab with a flat right edge, screen 9 to 10). Plausible for the canal; low priority.
- Tops: all full-height fronts run to y -18, never on screen (checked at camera y 0 and 120). No front ends in mid-air.

Not mine to fix, noted: the tram stop sign (green disc at x2136 area) is still code-drawn; the shelter's glass lets the door behind show through.

VERDICT: FAIL (4 items)
