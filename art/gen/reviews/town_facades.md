Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), 6 Nov 2026

# Review gate 8: town_facades - 6 Nov 2026

mid, 806x210, built old town row.
Own frames (not the maker's; identical to the maker's when re-rendered): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr/sweep_downtown_y{240,120,000}_x{0000,0330,0640,0980,1440,1700,2260,2950,3080}.png, sheets /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/sheet_y240.png sheet_y120.png sheet_y0.png, more spots /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/fr2/. Scale strips beside bench, bin, lamp and Pepper (cell 0,0,60,52; body 38 px tall with head, back 27 px): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/rv/s5_*.png, door4.png, gate4.png. asset_qa and check_backdrop: PASS.


Measures at 23 px/m, assuming a Stockholm old town house: window 23x36 px = 1.0x1.55 m, storey 70 px = 3.0 m, door 26x52 = 1.1x2.3 m. All as specified.
1. Scale: PASS Windows, storeys, doors on the 23 px/m grid, correct for a row seen across the square.
2. Layer: PASS On screen (y0 frame x330, rows 150-240): p10 153, median 173, min 124; lighter than the back pieces (houses 154-158, door 146) and darker than the roofs (197). Ladder holds.
3. Outline: PASS No ink: edges are the cream trim and a darker plaster shade; min luma 82, 0 % dark edge.
4. Shapes: PASS Gables (bell, stepped, pediment, mansard) are even; the bell curve steps cleanly. The strip repeats every 806 px (the game tiles it): the seam puts the sand dome gable against a cream one, no visible join (frame y0 x2950, seam at screen x 137).
5. Shading: PASS Flat plaster with one shade band, 13 colours, lone 0.13 %, windows pixel-identical (5x and 3x crops).
6. Palette: PASS All 13 colours in downtown.gpl v2 (the new ramps count only with the owner's approve). Whites cream, darks neutral.
7. View: PASS Front-on, cap roofs only.
8. Fit: PASS As crisp and as dense as the bench, bin and lamp at 1x and 3x.
9. Read: PASS Reads as old town houses across the square. Note: at the street camera (y 240) the gables fill the sky and hide the roofs and spire (maker's note, an owner option).

VERDICT: PASS
