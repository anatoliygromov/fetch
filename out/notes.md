# Tagline plate: method notes

## Round 2 (producer feedback: letters narrow, word gaps wide, corners light)
- Placement: every glyph sits at its painted position (left column = round(painted centre - width/2),
  then a small DP lets a glyph move one cell so word gaps come out as painted). Glyph centres: mean
  0.26, max 0.53 cell (D and g, the price of 6-cell word gaps). Word gaps 6 / 6 / 6 (painted 6.0 /
  5.9 / 6.1). Letter gaps are 1 or 2 px: the painted letters are 5.44 cells apart and 4.4 wide, so a
  4 px glyph at the painted centre leaves 1 or 2 px (the painted gaps also run 5 to 9 px).
- Widths: t and v are 4 columns (painted 4.0 and 4.4 cells), sampled from the painting on 4 columns;
  T stays 5 (34 px = 4.53 cells, centred stem). The v keeps its painted 2 px point (`.##.` on its last
  two rows, straight from the data): the only 2x2 ink block, where the two arms meet.
- Tails: y and g tails are 3 px `###.`, the painted tail length (3 blocks, starting half a block left).
- Corners: the rim is 2 px per row on the 45 degree corners and on the first and last rows of the
  vertical sides; outer and inner edges are clean staircases (steps of 1, no L-corner joints). With
  the thicker band the fitted chamfers are 4 (top) and 3 (bottom).
- Font: SPACE is now 4 (word gap 6 as painted) for `plate_with_text` and the glyph JSON.
- Round 3 (review: frame line on the right end but not the left): the painted frame outside the
  vertical rim is 9 / 10 px on the two ends, one column each (150 and 290). The right one spills 60 %
  into col 291, which a painting-sampling layer draws navy, so the right end read as a 2 column frame.
  The plate now also owns col 149 and col 291 on the vertical rows (83-90) and paints them with the
  painting's own sky there (#59aade, 4th palette entry), so both ends show the same 1 column frame.
  A 2 column frame on both ends was tried and rejected: it puts navy where the left end is painted
  sky (form p95 8.7).
The sections below describe round 1; where they differ, round 2 above holds.

Track: TAGLINE ("The City Dog Adventurer" plate under the logo).
Code: `art/source/title/tools/regrid/tagline.py` (pipeline), `tagline_font.py` (font table, layout),
`tagline_qa.py` (gates, comparison images, font sheet). Run `python3 tagline.py`; everything in `out/` is rebuilt.

## Region
Plate cells: columns 150 to 290, rows 77 to 96 (320x240 grid). Rim: row 78 (top), row 94 (bottom),
column 151 (left), column 289 (right). Text: cap row 83, baseline row 89, descender rows 90 and 91,
columns 161 to 279. Owned cells: `tagline_mask.png` (2725 cells).

## Palette (3 colours, `palette.json`)
Medians of the painting's own flat pixels of each material: navy body and outline `#012555`
(the painted outline and body are the same navy within 3 levels, so one colour), light rim `#3ea6f2`,
cream text `#fee9c6`. The painting's mid-blue pixels in the chamfer steps are anti-aliasing between
rim and navy and are dropped (they would be mixels).

## Local grid (separable, refined)
Rows: knots at the painting's plate bands (outline top 577, rim 587 to 597, rim 705 to 716, outline
716 to 730) and at the painting's text rows; every row border then snapped (within 3 px) to the
strongest local count of colour edges. Result: text rows 622, 630, 635, 643, 651, 659, 667, 675, 681,
687 (x-height 8 px rows, the painted cap zone is 8 + 5 px). Columns: plate ends at 1125 / 1134 / 1144
and 2166 / 2177 / 2187, and in the text each glyph's own block columns (its painted width split into
its column count, then each border snapped within 2.5 px to that glyph's own vertical edges, kept only
when the glyph's decisive cells do not change). Columns between the text and the plate ends are
interpolated and snapped to the plate's edges. This grid is used for sampling and for every QA
comparison (cells re-upscaled to the painting).

## Glyphs ("the painting's own lowercase pixel font")
1. Cream coverage per source pixel = projection of its colour on the navy to cream axis (so the
   anti-aliased halo counts fractionally, nothing grey survives).
2. Each painted letter is cut out (connected components, the i dot merged), then sampled on its own
   block grid: rows = the text rows above, columns = 3, 4 or 5, whichever makes the coverage most
   decisive (lowest mean min(v, 1 - v)) averaged over all instances of the letter, ties within 5 %
   go to the one with no 2x2 ink block. This is the unfake.js / Perfect Pixel idea (find the real
   pixel size, then vote per cell), done per glyph because the painted font sits on an 8.2 px pitch,
   not 7.5. Result: T and v are 5 columns (the painting centres the T stem and the v point), i and t
   3, all others 4.
3. The cleanest instance of each letter (lowest ambiguity) gives its bitmap at a 0.5 threshold; every
   instance of the letter is then drawn with that one bitmap, so e (3x), t (2x), r (2x) are
   pixel-identical. Agreement: every other instance of e, t, r matches the cleanest one in all cells
   on equal columns except one r cell (34 of 36), and in all cells on the refined grid.
4. Overrides, only where the 1 px stroke rule needs them (listed in `RULES` in tagline.py):
   - A row 1: shoulders sit half a block in, coverage 0.45 to 0.52 in all four cells; `.##.` would put
     a 2x2 block on top of the A, so `#..#`.
   - n row 3, column 1: the painted shoulder thickens the stem (0.70); `##.#` would form a 2x2 block
     with the arch row, so it is dropped, as in h.
   Everything else is the painting's data, including the g's square lower-left bowl corner (0.72) and
   the r's arm (`#.#.` over `##.#`).
5. The extracted table is checked against `tagline_font.RECOVERED` on every run (no mismatches).

Font metrics: 9 rows, cap height 7, x-height 5, descender 2, stroke 1, letter gap 1, word gap 8
(space 6). Letters are 4 px wide, the painting's are 4.4 cells (33 px at 7.5), see defects.

## Layout
Letter gap fixed at 1. Word space and start column fitted: least RMS error of glyph centres against
the painting (x / 7.5), with the line centred on the plate within 1 cell (the painted line is centred
within 0.5). Fit: space 6, start 161, RMS 1.03 cells, mean 0.87, max 2.0 (letters drift inside long
words because each painted letter is 5.44 cells apart and ours are 5). Line centre 220.5 = plate
centre.

## Plate
Measured on the refined grid: rim rows / columns by maximum rim fraction, bottom outline thickness by
navy rows below the rim (2; the top outline is 1 row as painted). Corners: 45 degree chamfers, top and
bottom fitted separately by the mean of filled-shape IoU and rim-ring IoU: top 5 (4 diagonal pixels),
bottom 4 (3), exactly as the painting's top corners are taller than its bottom ones. Rounded profiles
(runs of 2 at one end) were evaluated in iteration 3: IoU moved by under 0.005 and form by under 0.4,
and they would give top and bottom corners different styles, so pure chamfers were kept.
The filled octagon is rasterized with no anti-aliasing; the rim is its 1 px 4-boundary (8-connected,
no L-corner doubles, all runs 1 on the chamfers). The outline is the 4-neighbour ring outside, plus
one more row at the bottom; its cells are owned except where the painting shows the dark city
silhouette or sky there (top-left chamfer, parts of the top row, top-right corner), where the city
touches the rim directly in the painting too.

## Outputs
- `tagline_region.png` RGBA 320x240, plate opaque, rest transparent; `tagline_mask.png` owned cells.
- `tagline_plate_blank.png` the same plate saying nothing (same mask). `tagline.plate_with_text(S, s)`
  draws any other string with the same glyphs, centred on the same rows;
  `tagline_plate_sample_press_start.png` is an example.
- `font_glyphs.png` (cream on transparent, 6x10 cells, 26 per row) + `font_glyphs.json` (position,
  width, top row, bitmap, source painting / drawn) + `font_glyphs_preview8x.png` (painted letters
  cream, drawn letters light blue). 16 letters come from the painting (T h e C i t y D o g A d v n u r),
  the rest of a-z, A-Z, 0-9 and `! ? . , ' - :` are drawn on the same grid and rules.
- `cmp_*.png`: 10x comparisons, painting on top or left, result below or right (the plate shots show
  the result over a dimmed 7.5 px sample of the painting outside the owned cells).
- `metrics.json`, `metrics.md`, `tagline_meta.json` (all fitted parameters, per-letter coverage).

## Research used
- unfake.js: find the true pixel size from edge profiles, then dominant-colour voting per cell; here
  per glyph (column count by decisiveness) and per refined cell for the plate classes.
- Perfect Pixel: global grid, then per-line refinement within a tolerance; here every row / column
  border is snapped within 2.5 to 3 px to the strongest local edge count.
- Proper Pixel Art: most common colour per cell (plate class fractions per refined cell).
- Gerstner et al., Pixelated Image Abstraction: a small palette from the image's own colours.
- Kopf and Lischinski, Depixelizing Pixel Art: shapes as clean vectors, then rasterized; the plate is
  an exact octagon fitted to the painting, rasterized with no anti-aliasing.
- Pixel-perfect line rules: no L-corner doubles; clean staircases with equal runs.

## Remaining defects (seen at 10x)
Round 2 status: items 1 to 4 of round 1 (narrow spacing, 3 px t and 5 px v, 2 px tails, thin corner
rim) are fixed. Still visible: painted strokes are 8 to 9 px (1.1 to 1.2 cells) so the painted letters
look bolder than 1 px strokes; letter gaps alternate 1 and 2 px; the t stem sits left of centre
(painted centred); D and g are 0.53 cell from their painted centres.
5. Top-left chamfer: the painting's rim centre is half to one cell further out on rows 79 to 81 than
   ours (the painted plate is not symmetric; ours is mirrored left/right).
6. The top outline row is owned only where the painting shows navy there; elsewhere the city silhouette
   (another track) touches the rim, so the plate's top edge depends on that track's pixels.
