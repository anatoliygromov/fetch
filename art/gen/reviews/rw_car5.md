# Review for the pipeline: rw_car5

Reviewer: independent gate 8 reviewer (Claude, session 01XkeHCnH2RKgEVTGUWoSKBw; did not make the asset). Own measurements on riverwalk/art/scene/road_car5.png at commit 46a1dc0 (branch art/rw-traffic2-05nov), compared with road_car1 and road_car4 (unchanged since their PASS). Silver estate, 250x89.

# Round 1

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. 250x89 = 4.55 m x 1.62 m at 55 px/m with the rack (body about 82 px = 1.5 m, 1990s estate); tyre 39 px = 0.71 m (largest of the five, acceptable); rows 0-47 show rack, roof, glass, handles; script lane layer PASS.
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; 19 colours (cap 20).
3. Outline: unbroken 1 px ink: FAIL. 85 exposed edge px are #373737, not ink: the lower roof-rack rail, x129-220 at y6 (2 px rail y6-7, its top edge faces the transparent gap under the upper rail y0-3). Every other exposed edge px (682, incl. borders) is #000000. Fix: ink row at y5 or make the rail's top row #000000.
4. Shapes: round things round, straight lines straight, no lumps or jaggies: PASS. Wheels identical (784/800 px at the 153 px shift; the 16 differences are x57-59,y63-76 where the front wheel meets the door seam, not the wheel), outer radius sd 0.28 px, centres (41.5,69) and (194.5,69); pillars are lines (black outer stair, navy glass); hood glints are stepped lines under the outline like car1.
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: PASS. 46 lone px (2.9 per 1000, car1 10.4), 16 of them lug nuts; the rest are rack and rear-pillar bits ((131,1),(124,3),(91,11),(96,11),(93,14),(92,15),(232,11),(233,11),(234,18),(235,22)) and the side marker (65-68,54-55), small and structural. Light: left/right 121/117, top band 173 against lower 114, top-lit.
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 19 colours, all in riverwalk.gpl; ink #000000; darks #282a36/#373737 neutral; greys neutral.
7. View: side profile as road traffic, no tops/insides: PASS. Side profile; glass is flat navy with a reflection line, no interior; no text or logo; a small fuel flap (x168-172,y52-62) and tail light only.
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. Same ink and pixel size as car1/car4, 2.9 lone px per 1000; board frame rwtraffic2_road_estate_3x.png crisp beside the bench.
9. Read: cute and clear for a 7 year old at 1x: PASS. Silver estate with roof rack, big side glass, round headlamp: clear at 1x.

VERDICT: FAIL (1 item)

# Round 2

Reviewer: same independent gate 8 reviewer as above (did not make the asset). Checked commit f87d747 against d2c2804: road_car5.png differs in exactly 85 px (x129-220, y5), nothing else; road_car3.png is unchanged.

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. Unchanged (250x89).
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; 19 colours, none new.
3. Outline: unbroken 1 px ink: PASS. The 85 px at x129-220,y5 are now #000000 (diff: exactly those 85 px, alpha 0 to opaque), so no exposed edge px is non-ink (0 of all edge px incl. borders). Reading: the rack is the upper rail (y0-3, black/grey/dark/black) and a lower bar (y5-7, black over #373737) with a 1 px see-through slit at y4 between the uprights; it reads as a roof rack with rail and bar, not a solid slab, and matches the stepped rack of car1.
4. Shapes: round things round, straight lines straight, no lumps or jaggies: PASS. Unchanged; rack lines straight and uprights clean; wheels identical.
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: PASS. Unchanged, 46 lone px (2.9 per 1000, 16 are lug nuts).
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 19 colours, all in riverwalk.gpl.
7. View: side profile as road traffic, no tops/insides: PASS. Unchanged; no text or logos.
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. Unchanged apart from the rack row; same ink and density as car1/car4.
9. Read: cute and clear for a 7 year old at 1x: PASS. Silver estate with roof rack, clear at 1x.

VERDICT: PASS
