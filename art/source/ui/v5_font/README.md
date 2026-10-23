# FETCH! UI v5: the example font, smaller, with checked geometry (23 Oct 2026)

Owner, 19:14: the v4 font was too big in the top row and the menus; QA its geometry properly.

- Size: glyph body 13 px (was 17 for letters, 19 for digits). With outline and shadow: 18 px. Rows 24 px, menus tighter.
- How: kit A's letterforms (the Artlist font matching the chosen HUD example) redrawn pixel by pixel on a 13-row grid (font/glyphs.py), because shrinking the image by 13/17 is not allowed and would wobble. Rules: stems 3 px, bars 2 px, slab serifs 1 px outward, rounded corners on round letters, 9 = 6 turned round.
- Styling unchanged from v4 (font/restyle.py): highlight row, yellow top, orange bottom, maroon outline, dark shadow. Gold, cream, dim.
- Geometry QA (font/geomqa.py): 0 issues. Every glyph 13 rows on one baseline and cap line; no 1 px or stray 4 px strokes in the body; no lone pixels; A H I M O T U V W X Y 0 8 - + : . ! x mirror-symmetric.
- Checked by eye at 4-5x: font/sheet_5x.png and previews/zoom_*.png (HUD, dialogue, pause, level select, medals).
- font/font_*.png + font_metrics.json: atlases ready for the game.
