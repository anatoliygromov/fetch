# FETCH! logo track: method notes

Code: `art/source/title/tools/regrid/logo.py` (pipeline), `logo_common.py` (helpers and contour
fitting, copied from the shared drafts and extended), `logo_lines.py` (pixel-perfect line rules),
`logo_qa.py` (gates), `logo_gridfit.py` (local grid check), `logo_run.py` (writes everything in
out/). Run: `python3 art/source/title/tools/regrid/logo_run.py final`.

## What the painting is, here
- Inside the logo the painting's pseudo-pixels are 9.2 to 9.3 px, not 7.5 (edge periodicity,
  as in unfake.js's peak histogram / Perfect Pixel's FFT step). A 320-wide grid cannot sit on
  those blocks (alignment is at chance, 30 to 37 %), so sampling cells (Proper Pixel Art's
  "most common colour per cell") would always produce the clumped checker and notched outline
  the prototype showed. The logo is rebuilt from its geometry instead, then rasterized on the
  standard uniform cells (cell i = x 7.5 i .. 7.5 i + 7.5), which also composites on the grid
  track's grid.json (it deviates by at most 3 px here).
- Only four letter colours exist as flat paint: yellow #febd03, orange #fe6202, light yellow
  #ffe671, red-orange #da3611; every other warm colour is an anti-alias blend. Navy #011135 is
  one colour (outline and depth faces alike). The gaps show four blues.

## Steps
1. Labels: every source pixel is snapped to a painting flat colour. Flat pixels take the nearest
   prototype; edge pixels take the colour of the nearest flat pixel (colour distance plus a
   small spatial term), so a blend never becomes a third colour (dominant-colour voting as in
   unfake.js, palette from flat areas as in Gerstner et al.). Palette colours are the modes of
   the flat pixels, not means.
2. Masks at full resolution: FILL (warm paint), the logo component (fill plus connected navy,
   the tagline plate cut off at its top line y 578 px and left border x 1150 px), holes filled,
   narrow sky inlets closed (25 px); GAP = blue inside.
3. Contours (Kopf and Lischinski's idea: treat the pixel art as a vector shape): each contour is
   split at real corners; every piece that a total-least-squares line fits (RMS <= 3 px, max
   <= 8 px; the painting's own 9 px staircase is ~2.6 px RMS) becomes that exact line, corners
   between two lines move to the lines' intersection, other pieces (the C, the paw) are
   Gaussian-smoothed along arc length with pinned ends. Polygons are filled and rasterized by
   cell coverage >= 0.5, no anti-aliasing, so straight edges become digital straight lines.
4. Letters to the right sit in front: a letter loses cells closer than 3 cells to the letter on
   its right, so two navy cells always separate letters.
5. Paw: toes are axis-aligned pixel ellipses with centres on cell centres (odd widths, mirror
   symmetric in shape and checker), size and centre searched for the best overlap with the
   painted toe among shapes with no one-pixel tips; the main pad is the painted pad mirrored
   about its axis and rasterized symmetric about a cell-centre axis. Pads stay one navy cell
   apart, as in the painting.
6. Navy: a constant 2-cell outline (every cell within Euclidean distance 2 of the fill, in cell
   space) plus the painting's own silhouette where it reaches further (the depth faces, down and
   left), with slivers thinner than 2 cells, one-cell bumps and notches, and 1 to 3 cell lumps
   removed. Gaps: the painting's blue regions minus the 2-cell band, specks under 4 cells and
   inlets narrower than 2 cells or under 10 cells turned navy; each gap cell takes its dominant
   painting blue (4 groups), cleaned by a 3x3 mode filter and island merge.
7. Gradient: the painting's local orange share (orange vs yellow, letter interior only, 12 px
   blur, wider where the interior is far) averaged per cell, smoothed inside the fill, quantized
   to five levels and drawn as a 2x2 ordered dither with one global phase: 0 % yellow, 25 %
   orange dots on the checker lattice, 50 % exact checker, 75 %, 100 % orange. Islands under 8
   cells and one-row bands are merged.
8. Stripes (1 px): light yellow on top-facing edges, red-orange on bottom-facing edges, where the
   painting has them; side faces carry light yellow (yellow half) or red-orange (orange half)
   only as whole chains when the painting marks at least 30 % / 40 % of the chain. Runs are
   completed end to end, one-cell gaps bridged, L-corner joints removed (pixel-perfect rule),
   lone cells dropped. The paw uses the pure rule (light top, yellow, one checker row, orange,
   red bottom) so every pad stays symmetric.

## Output contract
- `logo_rgba.png` 320 x 240 RGBA (owned cells opaque), `logo_mask.png` (owned cells),
  `palette.json` (9 colours), `logo_rgba_x4.png` preview.
- `cmp_*.png` original | result at 10x: FET, CH_paw, paw, depth_F, depth_ET, counters_E_C,
  highlight_FET, highlight_CH. The result side is drawn over a faded copy of the painting so
  the transparent cells read as context.
- `metrics.md` (all gates and iterations), `metrics_*.json` per iteration.

## Research used
unfake.js (edge profiles and peak histogram for the pitch, dominant-colour voting); Proper Pixel
Art and Perfect Pixel (grid fit, why per-cell majority fails when the pitch differs); Gerstner
et al. "Pixelated Image Abstraction" (palette from the image's own flat colours); Kopf and
Lischinski "Depixelizing Pixel Art" (vectorize, smooth, re-rasterize); pixel-perfect line rules
(no L-corner doubles); clean staircases from exact line rasterization.
