Reviewer: independent (sonnet)

# Round 3

Asset: town_oriel_bay (58x36), new in bca1ab9, decoration: the guild house's bay window, drawn centred on the CHIMNEY box (x1607-1665), its bottom on the box bottom (y244, the portal top's plateau).
Reviewed with 36 fresh frames, numpy, asset_qa at the game fade.

1. Scale: PASS - 58 px wide = the house's windows; 36 tall (0.78 m), sill and three corbel rows; three equal panes of 12 px.
2. Layer: PASS - panes 99.9 on screen (same raw colour as the fronts' panes), frame (140,137,131) and (135,130,120), wall 150.5; asset_qa PASS; the bay region p10 is 99.9 (the darkest is Pepper's, outside the file).
3. Outline: PASS - none (decoration); edges are darker stone shades; 2 px of shade down the right side.
4. Shapes: PASS - three panes equal, straight bars, symmetric apart from the light side; 2 lone pixels (0.10 %) at (51,33) and (48,35), in the stepped corbel.
5. Shading: PASS - light upper left.
6. Palette: PASS - 8 colours, all in downtown.gpl.
7. View: PASS - flat front, a thin sill, no sides or top.
8. Fit: PASS - sits on the plateau under the cap with no gap (cap rows 199 to 207, bay 208 to 244); crisp like the fronts. The solid box mismatch is listed under town_oriel.
9. Read: PASS - a bay window under a copper roof, in the house's own scale. Note: storey 2 (x1552-1700, y141-227) has no other windows, so the bay stands in a wide blank wall at the high road camera.

VERDICT: PASS


# Round 4

Reviewed 229889b against f50160f. town_oriel_bay is now 58x44: the hip roof and two windows, decoration, centred on the CHIMNEY box (x1607-1665), bottom on y244, top (roof apex, 16 px) at y200.
1. Scale: PASS - 58 wide, 44 tall (0.96 m); each window 18 wide, the house's window width scaled to a bay; the apex is level with the pier's top.
2. Layer: PASS - panes 99.9 on screen (the fronts' pane colour), frame 135 to 171, roof 138, wall 150.5; the region's p10 is 99.9, over the back's darkest of 80; behind the pier (104), above Pepper.
3. Outline: PASS - none (decoration); edges are darker shades of their own colour; asset_qa PASS (no decor-ink warning).
4. Shapes: PASS - the two windows are pixel-identical (0 px differ over 18 to 19 columns, rows 10 to 33); symmetric hip roof with even 4 px steps; 2 lone pixels (0.1 %) at (51,41) and (48,43) in the corbel steps.
5. Shading: PASS - light upper left, 2 px shade down the right.
6. Palette: PASS - 11 colours, all in downtown.gpl.
7. View: PASS - flat front, thin sill and corbels, a roof seen as a front profile only.
8. Fit: PASS - the pier (18 px at x1627-1645) covers the 2 px inner frame edge of each window, the sill runs under it; the roof's slopes stay unoutlined and read as backdrop; the 16 px apex sits behind the pier cap and is not a second perch.
9. Read: PASS - a roofed bay window with a stone pier in front; reads right at 1x in colour and greyscale. Storey 2 around it (x1552-1700, y141-227) is still bare wall; noted.

VERDICT: PASS
