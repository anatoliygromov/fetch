Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), 6 Nov 2026

# Review gate 8: town_house1 - 6 Nov 2026

back, 54x118, plaza house with a plain gable (hand fix).
Own frames (not the maker's; identical to the maker's when re-rendered): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr/sweep_downtown_y{240,120,000}_x{0000,0330,0640,0980,1440,1700,2260,2950,3080}.png, sheets /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/sheet_y240.png sheet_y120.png sheet_y0.png, more spots /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr2/. Scale strips beside bench, bin, lamp and Pepper (cell 0,0,60,52; body 38 px tall with head, back 27 px): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/s5_*.png, door4.png, gate4.png. asset_qa and check_backdrop: PASS.


Scale numbers (houses 1 to 3, owner decision 2a): house1 54x118 px = 1.2x2.6 m at 46 px/m, door and hood 24-26 px = 0.52-0.57 m; house2 58x126 = 1.3x2.7 m, door about 24 px = 0.52 m; house3 52x118 = 1.1x2.6 m, door about 22 px = 0.5 m. True door (town_door) is 97 px = 2.1 m, so the ratio is 0.23-0.27: a quarter. Pepper's head is 38 px, about 1.5-1.7x the door. A true-scale house at these doors would be 4x bigger (about 480-520 px tall, 210-240 px wide), i.e. as tall as the street fronts (storey 140 px).
1. Scale: PASS Owner question (numbers above); slot kept.
2. Layer: PASS Median 158 on screen (fade 28 %, was 201), at the fronts' value.
3. Outline: FAIL Black ink dots remain on the roof edge: luma 1 at file (2,31), (7,25), (12,19), (15,15), (19,10), (23,5), (32,7), (39,16), (44,22), (47,26), (51,31) (a dotted black line along both slopes, 5x crop h_top8.png), and at the eaves feet (1,117) and (52,117). Door jambs are black (x 21 and 32, y 92-117) with a black sill (x 19-34, y 114-117). Decoration takes a darker shade of its own colour, not black. 13 edge pixels; not visible in game (the tops are covered by the balcony cages) but visible on the card at 5x.
4. Shapes: PASS Gable straight, windows and storeys even.
5. Shading: FAIL Wall is mottled: 291 pixels of (119,121,104) scattered over rows 5-113, x 2-51 inside the main wall (117,121,108), 4.6 % of the art; visible as grain on the 8x crop. Lone pixels 3.0 % (the diagonal roof line counts for most).
6. Palette: PASS 10 colours, all in downtown.gpl v2.
7. View: PASS Front-on, cap gable.
8. Fit: PASS In game (frames y240 x1440, x1790) it is crisp; the file at 5x is not as clean as the bench and lamp because of the dots.
9. Read: PASS Reads as a house, a doll house beside Pepper (Scale).

VERDICT: FAIL (2 items: outline dots, wall mottle)

# Round 2

Frames: the game would not render under the machine load (love sweep never wrote a frame in 4 tries), so the in-game check is a composite at 1x, 3x colour and 3x grey beside Pepper (cell 0,0,60,52), /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/r2/comp1x.png, comp3x.png, comp3x_grey.png, plus the file at 5x beside bench and lamp /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/r2/town_house1_5x.png; the maker's frames_after (docs/review/06nov/dt_built/frames_after) were looked at only as a cross-check. asset_qa and check_backdrop: PASS.
3. Outline: PASS Darkest pixel luma 41 (38,41,49); no black on the roof slopes (dotted line gone), the feet or the jambs.
5. Shading: PASS Wall is one flat colour (117,121,108), 7 colours in all, no grain at 5x; lone pixels 103 (1.9 %), nearly all the stepped roof diagonal.
Other items unchanged: PASS.

VERDICT: PASS (9 of 9)
