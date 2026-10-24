# Grid and palette track: method notes

Tools: `art/source/title/tools/regrid/` (`common.py`, `grid.py`, `labels.py`, `build_bg.py`, `qa.py`).
Run from that folder: `python3 grid.py && python3 labels.py && python3 build_bg.py` (about 1.5 minutes;
the cache lives in `/tmp/claude-0/rgg/cache`, outputs go to this `out/` folder). `build_bg.py` imports
`shapes.py` read-only for the smooth contour fill.

## 1. Local grid (`grid.py`, `grid.json`)

The painting's blocks are not on one lattice: within 240 px tiles only 30 to 50 % of strong edges agree
with any single phase, block widths run 7 to 12 px, Pepper's coat uses blocks of about 11 px. The output
must stay 320 x 240 with the painting's geometry, so each grid line may only move a few pixels from
k * 7.5 (x) or k * 7.467 (y), and inside that budget it follows the painting's real block edges.

* Edge strength per border position: max channel difference across the border plus half of the two
  neighbouring differences (one peak for a 2 px anti-aliased edge), clipped at 80 so that many edges
  count more than one strong edge (the Sobel profile idea of unfake.js).
* Coarse to fine (Perfect Pixel: global grid, then per line refinement within a tolerance): bands of 16,
  8, 4, 2 and 1 cell rows (columns for y lines). In each band all 319 x lines (239 y lines) are placed
  together by dynamic programming: score = profile at the line - mu * (distance to the coarser level)^2
  - 3 * (distance to k * pitch beyond 1.5 px)^2, lines ordered, cells at least 4 px, hard limit 4 px.
* `grid.json`: for every cell row j the 321 x borders, for every cell column i the 241 y borders, the
  same as 240 x 320 box arrays (`cells_x0/x1/y0/y1`), and the per region verification.
* Verification: per 8 x 8 cell region, the share of strong edge peaks (non-maximum suppressed,
  strength 48+) within 1 px of a cell border. 0.953 overall against 0.441 for the uniform grid;
  727 of 860 regions reach 0.9. Regions that fail hold detail thinner than a block, half blocks,
  text, or the logo's half-block slip (see metrics.md).

## 2. Palette (`labels.py`, `palette.json`, `palette_ramps.json`)

* Samples: flat pixels (max channel difference to the 4 neighbours under 10) of cell interiors (the
  outer 1 px ring of each cell is skipped), so anti-aliasing never becomes a palette colour.
* Materials: the 320 x 240 masks in `art/source/title/masks` (eroded by one cell for sampling), plus
  "logo" (logo and tagline boxes), "other", and "strokes" (centre lines of long thin strokes such as
  masts, weighted up so a 6 px mast keeps its own brown).
* Per material: k-means in CIE Lab, clusters closer than the material's merge distance merged, each
  cluster represented by its medoid (the most frequent exact colour among its members, the "dominant
  colour" of unfake.js, so every palette colour is a colour the painting uses in a flat area).
* Global: closest pairs merged until 128 colours (distance nudged by support so small accents survive
  longer than ramp neighbours); Pepper's coat keeps at least 8 dark values. 64 and 96 were tried:
  flat pixels further than dE 8 from the palette fell from 6.2 % (64) to 2.0 % (96) and 1.3 % (128);
  128 fixed the mast and sail colours. This is more than a Mega Drive screen (61); a later pass could
  share ramps between materials if the title must fit hardware palettes.
* `palette.json` is the plain list (material by material, dark to light); `palette_ramps.json` gives the
  ramp of every material. Pepper's coat: #000000 #000113 #2a2836 #40363f #514144 #5d494a (six neutral
  values) plus sheen #13274a #3b405e #4b5b7d #a2898c.

## 3. Background build (`build_bg.py`)

Round 2 adds: pinned palette colours (labels.PINS), a dark structure layer (STRUCTURES: railing,
bench, lantern), a speck rule (TEXTURE_MATERIALS kept, other specks snap to the most common
same-material neighbour colour unless the painting paints that block itself), a second optimiser
pass that may not create specks, and unification of rows of small features.


1. Every source pixel snaps to its nearest palette colour (Lab).
2. Cell vote (Proper Pixel Art / Perfect Pixel "most common colour per cell"): flat pixels weigh 1,
   anti-aliased pixels 0.25, the cell ring 0.35, pixels far from the palette 0.3. No mean, no median.
3. Pepper shape layer: Pepper's silhouette is cut out at full resolution (Pepper colours inside the
   rough masks, closed, opened, largest piece), its contour smoothed and filled (shapes.py, after Kopf
   and Lischinski: vectorise, smooth, rasterise without anti-aliasing), rasterised at coverage 0.5,
   slivers 1 to 2 cells wide removed, then a greedy staircase regulariser flips only undecided boundary
   cells (coverage 0.05 to 0.95) when that removes jaggies of the final outline. The outline is the
   8-connected inner boundary made pixel-perfect (no L-corner doubles), 1 px, in the painting's outline
   black. Cells straddling the silhouette re-vote using only the pixels on their own side.
4. Stroke layer: a ridge detector (a pixel that differs from the pixels 3 to 4 px away on both sides and
   is not a blend of them) finds strokes thinner than a cell; long thin components (15+ px, median width
   1.5 to 6 px, 4+ cells) are fitted with a straight line in local cell coordinates and drawn as one
   colour 1 px digital lines (the colour carrying most ridge strength: the core, not the highlight).
   Short gaps are joined, a weaker stroke right beside a longer one is dropped, stray cells removed,
   pixel-perfect applied; the cells beside a stroke re-vote without its pixels and never take its colour.
5. Checker rule: where two neighbouring coat values (or two logo yellows and oranges) interleave in a
   5 x 5 window, the cells become a regular 1-cell checker in global phase ((x + y) even = darker),
   solid where one value holds more than 70 % of the 3 x 3 neighbourhood.
6. Coordinate descent (Gerstner et al. style iterative refinement, constrained): a cell may switch only
   between colours that occur FLAT in it with at least half the winner's vote; objective = form error
   (5 x 5 blurred luma against the painting's per cell mean) + vote deficit + 30 per isolated speck +
   20 per differing 4-neighbour (no new notches) + a hard penalty per mixel. Locked cells (outline,
   strokes, checker) never change.
7. The same staircase regulariser on the named shapes, then a last mixel repair (a pixel between its two
   opposite neighbours across an edge of dE 20+, not part of a 3 px band, takes the better supported of
   them).

Outputs: `result_bg_320.png` (RGB), `result_bg_320_rgba.png` (all opaque), `mask_bg_320.png` (all cells),
`qa_bg.json`, `qa_masks/` (shape and line masks used by the gates), `cmp_*.png` (10x, painting | result).

## 4. QA module (`qa.py`)

`python3 -I qa.py result.png --palette palette.json [--mask m.png] [--src-mask s.png] [--region r.png] [--grid grid.json]`
prints every gate and a pass table; `--compare x0,y0,x1,y1 result.png out.png` writes a 10x comparison.
Definitions: off-palette pixels; mixels (between both opposite neighbours across an edge of dE 20+, a run
of 3+ along the edge is a band, not a mixel); L-corner doubles (Aseprite pixel-perfect rule, one count per
L, square corners kept); gaps (endpoints of different pieces 2 to 3 px apart pointing at each other);
staircase regularity (boundary or line cut into segments of one axis direction plus its diagonal; every
window of 3 run lengths must be equal, monotone, or within 1 of each other: 1,3,1 or 3,1,2 is a jaggy);
geometry (IoU and mean symmetric boundary distance in blocks after uniform re-upscaling); form (5 x 5 box
blur of luma against per cell means of the painting, refined cells with `--grid`); checker phase (per
colour pair with 8+ checker pixels, share on the majority parity). Every gate is also a function.

## 5. Remaining defects I can see (10x comparisons, round 3)

Fixed and checked: the bridge arches are the same size and shape with one continuous deck
line; the balusters stand at the painting's spacing, 1 px each, with no moire; the coat dither
forms continuous bands; the spire tapers without a bump; the bird is a clean 1 px V; the pavement
has fewer blue specks; the lamp post's highlight is one unbroken column; the rare colours are gone.

Still visible:
* Yacht at x135-160, y150-165: still muddled (hull and windows blur into the shore greens).
* The grey block building keeps only part of its window grid; its warm lit windows read as grey.
* The tower windows are fewer and softer than painted.
* sail_right IoU went from 0.76 to 0.71 (halo rule trims its pale edge); the right sail's mast
  top is still pale mauve.
* The bin (x275-290) and its base are darker and flatter than painted.
* Foliage stays mottled in places; the mid-right trees are better clumped than in round 2, but
  not as clean as the painting's leaf clumps.
* Pepper's coat checker is regular 50 % where the painting is sparser.

## Research used

unfake.js (edge profiles, offset search, dominant colour per cell, palette quantisation, cleanup);
Proper Pixel Art (grid from edges, most common colour per cell); Perfect Pixel (global grid, per line
refinement within a tolerance, majority per cell); Gerstner et al., "Pixelated Image Abstraction"
(joint palette and assignment refinement); Kopf and Lischinski, "Depixelizing Pixel Art" (vectorise,
smooth curves); pixel-perfect line rules (no L-corner doubles); clean staircases (run lengths equal or
steadily changing); rasterisation of smooth curves without anti-aliasing.
