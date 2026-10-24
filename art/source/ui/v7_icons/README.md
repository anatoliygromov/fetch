# FETCH! UI v6: one layout system, measured (23 Oct 2026)

Owner, 19:20: QA the top row properly, visually and otherwise; the layout must be concise and organized.

## What the QA found in v5's top row
- Four different centre lines (12.5 to 14.5 px), heights 22 / 26 / 16 / 19 px.
- The clock's bow touched the screen edge (0 px margin); other items 3-7 px down; left margin 3, right 4.
- Groups unbalanced: 24 px and 79 px gaps; the time group 30 px off centre.
- Two outline colours (icons darker, text maroon); icons had no shadow, text did; the bone flat (3 colours).

## The spec (tools/compose6.py, top of file)
- Margin 4 px to every drawn body on all sides (shadows may sit in the margin).
- Top row: health | time | bones, spread with equal gaps (52 / 52 px), all centred on one line (row 4-25).
- Bottom row: lives (Pepper + x3) left, score (paw coin + digits) right, on one line, 4 px from the bottom.
- Icon to its number: 3 px everywhere (also the paw cursor to a row label).
- Menus: panel padding 14 px, rows 24 px with a 4 px gap (pitch 28), labels inset 26 px, every label centred in its row, hints as one centred group.
- One outline colour (64,11,6) and one 1 px shadow (36,8,5) for text and icons.

## Icons (icons/)
- Clock: the bow removed (21 x 20, fits the row). Bone: a shade band and a highlight added. Pepper (lives): 24 rows, with a 1 px cream rim so the black head reads on the dark road.

## Checks (tools/layout_qa.py, previews/layout_qa.txt): ALL PASS
Centre lines within 0.5 px, all margins 4, all icon gaps 3, equal group gaps, even row pitch, shared label edge, labels centred in rows, panels centred, equal side padding, no overlapping text or icons. Eye check at 4x: previews/guides_top.png, guides_bottom.png (green: centre lines, cyan: top/bottom margins, magenta: side margins and screen centre) and previews/zoom_*.png.

## Update 19:30 (owner: the clock went bad; the thing on the top left)
- The clock was cropped through its case when the bow was removed (top outline gone, flat lopsided top, 12 tick lost). The health bar's paw medallion was speckled, lumpy and the empty segment was a recolour with yellow strips left. Both missed because the QA measured layout but did not look at each icon at zoom.
- Redrawn on the pixel grid (tools/icons7.py): one symmetric 19 px disc and one light direction for the watch (with a small crown, 21 px), the paw medallion and the score coin; a 4-toe paw; the health bar as a clean capsule with three rounded segments (full red / orange / yellow, empty drawn, not recoloured): bar_0..bar_3.png. Shapes checked mirror-symmetric; looked at at 8-14x.
- Layout re-run: ALL PASS (top row on one line, equal gaps 57 / 56).
