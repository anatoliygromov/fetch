# Review for the pipeline: rw_car2

Reviewer: independent gate 8 reviewer (Claude, session 01XkeHCnH2RKgEVTGUWoSKBw; did not make the asset). Own measurements on riverwalk/art/scene/road_car2.png at commit 46a1dc0 (branch art/rw-traffic2-05nov), compared with road_car1 and road_car4 (unchanged since their PASS). White panel van, 242x102.

# Round 1

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. 242x102 = 4.40 x 1.85 m at 55 px/m (small panel van, Berlingo/Transit Connect size); tyre diameter 36 px = 0.65 m, car1 33, car4 29; lane top y192, rows 0-47 show (roof, glass, handles, belt); script lane layer WARN only for 2 small blotches.
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; no pixel darker; 17 colours (cap 20).
3. Outline: unbroken 1 px ink: PASS. All 609 exposed edge px are #000000 (also the 169 px roof row y0, 17 px bottom row, columns 0 and 241); no second ink on the silhouette.
4. Shapes: round things round, straight lines straight, no lumps or jaggies: FAIL. Wheels are fine (identical 797/797 px at the 148 px shift, outer radius sd 0.23 px, centres (38.5,83.5) and (186.5,83.5)). The windscreen A-pillar (x33-68, y6-43) is not a line: a black outer line plus a second line of alternating navy, grey and tan dashes inside the cream band, with 14 lone dabs ((66,6),(67,6),(65,7),(58,16),(52,19),(52,20),(47,22),(49,23),(43,29),(50,29),(40,35),(45,35),(36,36),(42,39)); same defect as car4 in round 1. Fix: one black outer line, one flat band.
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: FAIL. Bonnet and nose carry specks: grey/tan dabs at (4,54),(5,52),(7,50),(8,54),(9,52),(10,52),(13,51),(16,50),(25,58),(28,55),(30,55),(47,55) (the producer's bonnet x15-30,y45-52 shows (16,50),(13,51)), and an 8 px orange block at (34-37,53-54) that is neither headlamp nor indicator (the orange at x100-104 and x225-229,y75-76 are the sill lights). Rows 45-47 are on screen, rows 48+ are not, so the pillar dabs are the visible ones. Light: neutral left/right (151/151), top band 225 against lower band 129, i.e. top-lit like car1/car4 (side-on view). 5.9 lone px per 1000 overall, far cleaner than car1 (10.4).
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 17 colours, all in riverwalk.gpl; ink #000000, darks #282a36/#373737 neutral; body is the cream #faf0dc/#faf6f0 with #c2c4ca lower panel.
7. View: side profile as road traffic, no tops/insides: PASS. Side profile, flat dark glass with one 2 px reflection band, no interior, no tops; no text, logos or plates (blank panels, red tail light at x232-236,y46-58 only).
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. Same 1 art px, same ink as the bench and car1/car4; pixel density 5.9 lone px per 1000 (car1 10.4, car4 9.7, bench 16); in the 1x frame ingame_24_traffic_van_1x.png it reads clean beside the bin, the cream body is pale but the black outline holds it against the pavement.
9. Read: cute and clear for a 7 year old at 1x: PASS. Reads as a white delivery van (sliding door, handles, side window, dark bumpers), friendly; the only noise is the pillar (item 4).

VERDICT: FAIL (2 items)

# Round 2

Reviewer: same independent gate 8 reviewer as above (did not make the asset). Checked commit f87d747 against d2c2804: road_car2.png differs in 272 px, all in x4-70, y5-58, alpha unchanged; nothing outside that box changed.

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. Unchanged (242x102, 55 px/m, alpha identical).
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; 17 colours, none new.
3. Outline: unbroken 1 px ink: PASS. Exposed edge px: 0 not #000000 (incl. borders); the roof-corner rows 5-8 edit kept the outer line closed.
4. Shapes: round things round, straight lines straight, no lumps or jaggies: PASS. A-pillar fixed: one black outer stair line and one flat cream band (x33-68,y6-43), the old dashed navy/grey/tan second line is gone; only a single navy 1 px stair line sits inside the black line as the glass frame (x36-60,y10-40), reads as trim not dashes; lone dabs in the pillar zone 14 to 2 ((44,38),(33,43)). Wheels untouched (797/797).
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: PASS. Bonnet specks gone (lone px in x0-60,y40-62: only (33,43)); the orange block at (34-37,53-54) is gone (orange left only in the headlamp x3-5 and the sill lights); lone px 117 to 91 (4.6 per 1000, car1 10.4). Top-lit as before.
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 17 colours, no new colour, all in riverwalk.gpl.
7. View: side profile as road traffic, no tops/insides: PASS. Unchanged; no text or logos.
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. Cleaner than round 1, 4.6 lone px per 1000 against car1 10.4, same ink and pixel size.
9. Read: cute and clear for a 7 year old at 1x: PASS. Reads as a clean white van.

VERDICT: PASS
