# FETCH! logo track: QA gates

Region: the letters F E T C H !, the paw, their navy outline and depth faces and the blue gaps
inside, cells x 125 to 300, y 16 to 86 (the F's foot runs below the plate top at x < 1150 px;
the plate itself, from y 578 px, x 1150 to 2195 px, is excluded). Owned cells: 8311.
All numbers from `art/source/title/tools/regrid/logo_run.py` (out/metrics_final.json).

## Grid
The painting's pseudo-pixels inside the logo are 9.2 to 9.3 px (edge periodicity, logo_gridfit.py),
not 7.5 px. On the standard 320 x 240 grid only 35.5 % (x) and 29.0 % (y) of strong colour changes
lie within 1 px of a cell border; the best sub-cell offset gives 37.2 % / 31.8 %; chance is 40 %.
No 320-wide grid can align with 9.3 px blocks without moving the logo by ~30 cells, so the
alignment gate (90 %) is unreachable here by construction. The logo is therefore rebuilt from
its contours (method principle 3) on the standard uniform cells. The grid track's grid.json
deviates from the uniform cells by mean 1.1 px, max 3 px in this region, so the result composites
on either.

## Gates (final)

### Geometry (result mask re-upscaled vs painting mask; IoU >= 0.92, mean boundary distance < 0.35 block)
| shape | IoU | boundary (blocks) | gate |
|---|---|---|---|
| F | 0.941 | 0.281 | pass |
| E | 0.933 | 0.270 | pass |
| T | 0.937 | 0.293 | pass |
| C | 0.938 | 0.276 | pass |
| H | 0.947 | 0.302 | pass |
| ! | 0.932 | 0.302 | pass |
| paw_toe0 | 0.792 | 0.256 | FAIL |
| paw_toe1 | 0.817 | 0.212 | FAIL |
| paw_toe2 | 0.814 | 0.240 | FAIL |
| paw_toe3 | 0.758 | 0.282 | FAIL |
| paw_pad | 0.844 | 0.413 | FAIL |
| silhouette | 0.966 | 0.456 | FAIL |
| gaps | 0.520 | 4.635 | FAIL |

Reference: rasterizing the painting's own mask with no smoothing at all (jaggy) gives toes
0.76 to 0.83 IoU, pad 0.927, silhouette 0.982 / 0.239. Toes are 5 x 6 cells: one cell of
boundary error is ~20 % IoU, so the 0.92 gate is out of reach for them for any raster.
Silhouette boundary 0.456: the navy outline is forced to a constant 2 cells (15 px) where the
painting's is 13 px, and depth slivers thinner than 2 cells are dropped. Gaps are pushed at least
2 cells from the fill and specks / one-cell inlets removed, by design (constant outline).

### Lines
- L-corner doubles on the 1 px stripes: highlight 0, red 0 (pass)
- gaps on the 1 px stripes: highlight 0, red 0 (pass)
- navy outline: fill cells closer than 2 cells to outside 0, to a blue gap 0 (pass, no gaps or thin spots)
- outline thickness above every top-facing fill cell (cells: count): {'2': 130, '3': 7, '4': 2, '5': 2, '6': 1, '7': 3, '8': 2, '9': 3, '11': 1, '12': 1, '13': 2, '16': 1, '17': 3, '18': 1, '19': 1, '38': 1, '46': 1}
  (2 = the constant outline; larger values are depth faces, letters behind, and gaps between letters)
- staircase regularity (digital-line segments with >= 2 inner runs, inner runs equal +-1 or monotone):
  silhouette 1/2, fill 13/14, total 14/16 = 0.88 (pass >= 0.9; the
  irregular ones: [[3, 3, 3, 2, 4, 4]] [[3, 3, 2, 4, 4]]). Most edges are straight lines with few steps, so few segments qualify.
- lumps / notches (cells a 3x3 opening removes / closing adds, per shape): {"silhouette": [4, 0], "fill": [14, 9]};
  silhouette ones are the acute top-right corner of the "!" and the outline corner under the F foot; fill ones are acute letter corners (E arm ends, slanted stems).

### Colour
- off-palette pixels: 0 (pass); palette: #011135, #febd03, #fe6202, #ffe671, #da3611, #2b86d5, #1676c6, #055aaa, #013a7a (navy, yellow, orange, light yellow, red-orange, four blues); no green, beige or brown: none (pass)
- mixels: 181 by the generic test, all of them the designed stripe orders orange > red-orange > navy and yellow > orange > red-orange (the painting's own edge treatment); 0 anti-alias blends (no colour exists that is not a painting flat colour). Strict reading: FAIL, design reading: pass.

### Pattern
- fill cells following the dither rule: 4636/4636; 50 % band cells out of phase: 0/868 (pass). One global phase everywhere; the 25 % and 75 % levels are subsets of that checker.

### Form (5x5 box blur of luma vs the painting's cell means; mean < 3, p95 < 8)
mean 5.97, p95 17.00: FAIL. The per-cell mode of the painting itself (jaggy, the naive answer) scores 4.67 / 13.3,
so the gate also fails for the painting's own colours: the painting's 9.3 px checker beats against
the 7.5 px cells with a ~5-cell period that a 5x5 box does not remove, and every half-cell edge shift
of navy against yellow moves the blurred luma by ~30.

## Iterations
| it | change | letters IoU min / bd max | silhouette | form mean/p95 | notes |
|---|---|---|---|---|---|
| 1 | contour smoothing (Gaussian, s 12) + 2-cell outline + 5-level dither + stripes | 0.912 / 0.395 | 0.966 / 0.449 | 6.87 / 21.5 | F E ! below gate; stripes red near edges raised the gradient |
| 2 | straight pieces fitted as exact least-squares lines, corners at line intersections | 0.932 / 0.302 | 0.967 / 0.436 | 5.72 / 16.3 | letters pass |
| 3 | toes as pixel ellipses (no one-pixel tips), thin sky inlets to navy, short side stripes dropped | 0.932 / 0.302 | 0.967 / 0.436 | 5.85 / 16.5 | |
| 4-5 | gradient from letter interiors only (edge rows were turning yellow), stripe runs completed end to end, paw coloured by rule | 0.932 / 0.302 | 0.966 / 0.446 | 5.66 / 15.5 | L-corners back to 0 |
| 6-7 | letters on the right sit in front (2 navy cells between letters), side highlights as whole chains (no dashes), one-row bands merged, small inlets to navy | 0.932 / 0.302 | 0.966 / 0.446 | 6.00 / 17.1 | |
| 8-final | odd-width pad and toes so shape AND checker are mirror symmetric, pad axis chosen by toe fit, 1-3 cell outline lumps removed | 0.932 / 0.302 | 0.966 / 0.456 | 5.97 / 17.0 | pad IoU 0.896 -> 0.844 for symmetry |

## Visual check (10x, original | result): out/cmp_*.png
Remaining defects I can see:
1. The 25 % and 75 % bands read as single dotted rows across a letter (E, F, H lower half), where the painting's sparse band is a looser field of dots.
2. The paw's main pad is flatter on top than the painting's dome and sits 0.65 cell left of the painted centre (forced by the symmetric odd-width raster); the pads are one navy cell apart (painting ~1.2), the only place the navy is thinner than 2 cells.
3. The right-facing edges in the orange half carry no light edge (the painting has a faint yellow edge there on F, E, H).
4. Blue gaps are smaller than the painting's (pushed 2 cells from the fill); between H and "!" the blue strip is narrower.
5. Highlight corner cells at the top-left of letters are plain yellow where the pixel-perfect rule removed the L joint.
