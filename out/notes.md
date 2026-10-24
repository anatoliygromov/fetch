# PEPPER track: method notes

Code: `art/source/title/tools/regrid/pepper_seg.py` (labels, masks, parts),
`pepper_render.py` (re-drawing), `pepper_refine.py` (tone refinement and dot
cleanup), `pepper_qa.py` and `pepper_gates.py` (gates), `pepper_final.py` (outputs),
plus additions to `lines.py` (skeleton tracing, arc smoothing, pixel-perfect
rasterization, staircase metric). `shapes.py` is used as is (corner-aware contour
smoothing). Other modules (common, labels, grid) are imported, not changed.

## Why re-draw instead of sample

The local grid fit was done first (grid.py's dynamic programming per band; FFT and
autocorrelation of the edge profiles per 160 px tile). Pepper's pseudo-pixels are
about 9.5 to 10 px, not 7.5 px, so at most 80 % of her strong edges can be brought
within 1 px of a 320 grid line (42 % on the uniform grid). Sampling would alias her
10 px staircases onto 7.5 px cells (the uneven 1-2-1 runs and notches seen in the
prototype). Following Kopf and Lischinski ("Depixelizing Pixel Art"), her shapes are
recovered as curves at full resolution and rasterized again on the output grid with
no anti-aliasing.

## Pipeline

1. Labels (labels.py, Gerstner-style palette from flat areas): k-means in Lab on the
   region's flat pixels (64 clusters, merged under 2.5 dE, 61 colours), each cluster
   represented by its most common exact colour; anti-aliased pixels snapped to a
   nearby flat pixel's colour. Two navy-blacks within 6 dE of a third are merged into
   it. The output uses 27 of these colours.
2. Masks: dog = connected dark, coat, pink and red labels (opened, holes filled);
   bandana = the large pink components; the owned region stops at the bandana's
   upper edge left and right of it and keeps the bandana to its tip (the body below
   belongs to the grid track). Parts (ears by flood fill from a seed, bounded by the
   ear crease and a short cut where the crease fades; eye and nose as the non-coat
   areas around a seed; tongue; bandana) are computed by one function used both on
   the painting and on the re-upscaled result, so the IoU compares like with like.
3. Silhouette: contour of the dog mask, corner-aware smoothing (shapes.py: corners
   kept, near-straight runs made straight, curves Gaussian-smoothed along the arc,
   corner reach 26 px so a narrow notch is not a corner); a cell belongs to Pepper
   when its centre lies inside that polygon. The outline is the shape's own 4-boundary
   ring with L-step joints removed (Aseprite pixel-perfect rule), and those joints
   leave the shape, so no fill shows outside the line.
4. Lines: skeletons of the black line colour (after a light Gaussian so staircases
   give no side branches), split where the stroke gets thick, short spurs dropped,
   strokes inside dark shadows (both sides dark) rejected, smoothed along the arc,
   rasterized 1, 2 or 3 cells thick by measured width, pixel-perfect. Lit rims (brow,
   ear edges, lip) are skeletons of the coat's light tones. The tongue crease and the
   bandana folds are black top-hat ridges (darker than their surroundings), drawn in
   the darkest material colour of their neighbourhood.
5. Fills: every label (or dither class) indicator is Gaussian smoothed (sigma 3 px,
   a multi-label curvature flow that turns 10 px staircases into the curves they
   stand for) and each cell takes the class with the largest mean (Proper Pixel Art's
   per-cell majority, on smoothed classes). Eye, nose, tongue and bandana are filled
   inside their own shapes with their own colours only.
6. Dither: where two tones alternate at block scale in both directions the class
   records the pair and its mix level (1, 2 or 3 quarters) and is rebuilt by an
   ordered 2x2 Bayer rule in global phase, so the coat's checker comes out regular,
   only where the painting has it.
7. Tone refinement: single-cell boundary moves between neighbouring fill classes,
   accepted only when they lower the error of the 5x5 blurred luma against the
   painting and add no mixel, never stranding a cell (unfake.js-style hand cleanup,
   automated). Then anti-aliasing dots (a cell between its two neighbours that does
   not continue along the edge) take the closer neighbour's class.

## Research used

unfake.js (edge profiles, dominant-colour voting, hand cleanup), Proper Pixel Art (most
common colour per cell), Perfect Pixel (per-line grid refinement within a tolerance,
here grid.py), Gerstner et al. (palette from the image), Kopf and Lischinski (vectorize
then re-rasterize), pixel-perfect line rule (no L-corner doubles), clean staircase rule
(monotone run lengths or k, k+1, k alternation).

## Remaining defects (seen at 10x)

- Wink: the thick curve is clean, but the three lashes at its right end merge into
  one dark blob with two ticks; the painting's lashes are thinner than a cell and
  near-black, and drawing them as lines also turned the ear's fur specks into squiggles.
- Fur checker: rebuilt in phase where detected (muzzle, cheek, parts of the forehead
  and ears), but covers less of the forehead and the left ear than in the painting.
- Eye: the brown iris ring is only on the lower left; the painting's thin dark-brown
  upper-right part of the ring is one block, a little heavier than in the painting.
- Brow over the open eye: the dark arc is shorter than the painting's.
- Nose: the highlight starts with a grey and a tan cell at its left end (both in the
  painting's palette and position), so it reads slightly less crisp than the original.
- Knot: its tip is rounder than the painting's point, and two coat cells sit inside
  the outline under the knot where the region is cut.
- Right cheek and jaw: the dark jaw edge is 2 to 3 cells thick (as painted), so the
  1 px outline merges into it there.
- 139 one-pixel ramp bands count as mixels under the strict definition (see metrics).
- 3.7 % of cells use a colour that is not in their own painting cell (99.5 % in the
  cell or a neighbour): the price of moving the 10 px shapes onto 7.5 px cells.

## Round 2 changes

- `pepper_detail.py`: the three wink lashes and the brow arc are traced by hand
  (painting coordinates from ASCII dumps of the near-black labels) and drawn as
  pixel-perfect lines (brow 2 px, as painted); the near-black blob around them is
  cleared from the fill. The knot tip: inside a small box the dog mask is limited to
  the bandana plus one outline block, so the lamp post behind the tip no longer widens
  it; one-cell spurs leave the silhouette (the two coat cells under the knot are gone).
- Jaw: near-black fill cells just inside the outline, in runs of 5 or more, inside the
  jaw box (cells 118-150, 124-166), take the coat's darkest tone `#222231`, so the
  1 px outline reads against the painted dark edge.
- Nose: in the left half of the highlight's bounding box, warm grey and tan gloss
  cells become the nose's own cool tones of similar value (`#5a617d`, `#3a3f5d`);
  turning them navy failed the form gate (-18 luma there).
- Fur checker: dither detection opening 5 px (was 9), pair share 0.025 (was 0.035):
  904 checker cells instead of 542, on the forehead band and the left ear's lower half.
  Wider settings (up to 1005 cells) push form p95 over 8.
- Remaining: the forehead checker is still patchier than painted at its left end; the
  left ear's checker is denser on its lower half than its upper half; form p95 (7.96)
  sits close to its limit.
