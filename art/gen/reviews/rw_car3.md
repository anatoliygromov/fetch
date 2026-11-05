# Review for the pipeline: rw_car3

Reviewer: independent gate 8 reviewer (Claude, session 01XkeHCnH2RKgEVTGUWoSKBw; did not make the asset). Own measurements on riverwalk/art/scene/road_car3.png at commit 46a1dc0 (branch art/rw-traffic2-05nov), compared with road_car1 and road_car4 (unchanged since their PASS). Yellow taxi, 246x93.

# Round 1

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. 246x93 = 4.47 m x 1.69 m at 55 px/m including the 13 px roof sign (body 80 px = 1.45 m, saloon size); tyre 35 px = 0.63 m; rows 0-47 show the sign, roof, glass, door handles and belt line; script lane layer PASS.
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; 14 colours (cap 20).
3. Outline: unbroken 1 px ink: PASS. All 556 exposed edge px are #000000 (incl. sign row y0 x30 px and the borders).
4. Shapes: round things round, straight lines straight, no lumps or jaggies: PASS. Wheels identical 800/800 px at the 149 px shift, outer radius sd 0.26 px, centres (41,75) and (190,75); pillars read as lines: a black outer stair line with a grey/yellow trim band and one inner black stair (x60-100,y12-42, same trim reading as the accepted car4); sign is a clean trapezoid x93-141,y0-12.
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: PASS. Body in flat yellow bands (#f4cc69 / #d49a54 / #a86e3e); 41 lone px (3.0 per 1000, car1 10.4) of which 12 are the symmetric wheel lug nuts; small brown specks lie just under the hood outline at (51,41),(54,41),(60,40),(61,40),(34,43),(27,44),(13,47),(78,44) and (71,44-47): visible at 9x, not at 1x or 3x, noted not failed. Light: left/right 176/174, top band 182 against lower 156, top-lit.
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 14 colours, all in riverwalk.gpl; ink #000000; darks #282a36/#565864 neutral.
7. View: side profile as road traffic, no tops/insides: PASS. Side profile; the roof sign is a blank pale-yellow box (#f1dbbb), no lettering, no TAXI text, no logo; red tail light only.
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. Same ink, pixel size and clean fills as car1/car4 (3.0 lone px per 1000); board frame rwtraffic2_road_taxi_3x.png shows it crisp beside the bin.
9. Read: cute and clear for a 7 year old at 1x: PASS. Yellow body plus the roof sign reads as a taxi with only the top 48 rows on screen (the sign, roof and glass are all in rows 0-47), cheerful.

VERDICT: PASS
