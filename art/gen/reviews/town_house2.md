Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), 6 Nov 2026

# Review gate 8: town_house2 - 6 Nov 2026

back, 58x126, plaza house with a bell gable (hand fix).
Own frames (not the maker's; identical to the maker's when re-rendered): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr/sweep_downtown_y{240,120,000}_x{0000,0330,0640,0980,1440,1700,2260,2950,3080}.png, sheets /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/sheet_y240.png sheet_y120.png sheet_y0.png, more spots /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr2/. Scale strips beside bench, bin, lamp and Pepper (cell 0,0,60,52; body 38 px tall with head, back 27 px): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/s5_*.png, door4.png, gate4.png. asset_qa and check_backdrop: PASS.


Scale numbers (houses 1 to 3, owner decision 2a): house1 54x118 px = 1.2x2.6 m at 46 px/m, door and hood 24-26 px = 0.52-0.57 m; house2 58x126 = 1.3x2.7 m, door about 24 px = 0.52 m; house3 52x118 = 1.1x2.6 m, door about 22 px = 0.5 m. True door (town_door) is 97 px = 2.1 m, so the ratio is 0.23-0.27: a quarter. Pepper's head is 38 px, about 1.5-1.7x the door. A true-scale house at these doors would be 4x bigger (about 480-520 px tall, 210-240 px wide), i.e. as tall as the street fronts (storey 140 px).
1. Scale: PASS Owner question (numbers above); slot kept.
2. Layer: PASS Median 157 on screen (fade 28 %); the salmon wall is the brightest of the three beside the grey and sand ones, still at the fronts' value.
3. Outline: FAIL Near-black pixels remain on the silhouette: file (16,10), (17,11), (38,10), (40,11), (41,10) at the gable shoulders, (0,42) and (57,42) at the cornice ends, (2,125) at the foot. 8 edge pixels, luma 1, black against a salmon wall; door jambs are black too (x 22 and 33, y 99-124). Not visible in game (tops covered by the cage), visible at 5x.
4. Shapes: PASS Bell gable curve and cornice even.
5. Shading: FAIL Stray light pixel in the glass of the top window's left pane at file (26,15); the right pane is clean.
6. Palette: PASS 11 colours, all in downtown.gpl v2.
7. View: PASS Front-on.
8. Fit: PASS Crisp in game; at 5x the black dots stop it matching the bench and lamp.
9. Read: PASS Reads as a house, a doll house beside Pepper (Scale).

VERDICT: FAIL (2 items: outline dots, stray pixel)
