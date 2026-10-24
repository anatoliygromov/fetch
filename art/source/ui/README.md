# FETCH! UI kit, Lion King style (23 Oct 2026)

Direction: the HUD mockup you picked (carved gold frames, paw medallion, chunky gold numbers), extended to the whole UI.
Art: Nano Banana Pro on Artlist (1,960 credits for the UI today). GPT Image 2.5 drew the chosen mockup, but its pixel grid drifts (3.1 to 4.6 px), so it was only used as the style reference.

## How the art was processed
1. Grid: Nano Banana Pro draws on an even 7.5 px grid, so a 2400 px image is exactly 320 game pixels. tools/pitch.py finds the grid.
2. Native pixels: one colour per art pixel (majority of each cell's centre), no resampling of any kind (tools/native.py).
3. Cut: magenta keyed out, pieces cut by connected alpha, fringe pixels removed (tools/cut.py, tools/kit.py).
4. Palette: one shared 32-colour palette, each piece capped to its material ramp (6 colours for letters, up to 11 for the health bar). Pepper's head keeps its own neutral darks (tools/palette.py).
5. Clean pass: lone pixels that are only a shade off take their neighbours' colour; light fringe on edges dropped; 1 to 2 px outline notches filled (tools/palette.py, tools/pinfill.py, tools/fix2.py).
6. Frames rebuilt as true 9-slice / 3-slice: corner ornaments as drawn, each edge one clean repeated column or row, flat fill inside (tools/rebuild9.py). Stretch data in kit/frames/slices.json.
7. Checks on all 73 pieces (kit/qa.json): alpha 0 or 255, at most 11 colours, lone pixels at most 5.5 % (approved art 0.6 to 5.8 %), no specks, no pinholes.

## What is in kit/
- frames/: panel_menu and panel_wide (dark), cream versions, row_normal, row_selected, row_disabled, ribbon, health_full, health_empty (+ slices.json)
- pieces/: cursor_paw, pepper_head (+ pepper_head_rim with a cream rim for the HUD), hearts, icons (clock, bone, golden bone, ball, padlock, speaker), medals won and not won, A and B buttons, d-pad, volume bar, toggles
- font_big/: A to Z, 0 to 9, x / : at 19 to 21 px (headings and HUD numbers)

## Open points
- Body text: the menus use the game's 5x7 letters at 2x with the kit's gold bands and outline, drawn in code. A generated mid-size font did not come out at the asked size (fontA/fontB in sources/, not used).
- HUD numbers are 21 px tall (Lion King proportions). A smaller numeral set needs one more generation if you want it lighter.
- Health bar: 3 segments = 3 hearts; drawn in code from health_full and health_empty.
- toggle_off has red specks on its knob; the panel corner bones are small and busy. Both minor.
- Not wired into the game yet. Nothing touched round1.
