# Grid and palette track: metrics

## Round 3 (review fixes), final numbers

| Gate | Result | Pass |
|---|---|---|
| Off-palette / mixels | 0 / 0 | yes |
| Form whole picture / visible background only | 2.49 / 7.83 and 2.39 / 7.48 | yes |
| Checker phase | 1.0 (2225 px; continuous coat bands) | yes |
| Pepper outline L-corners / gaps / staircase | 0 / 0 / 1.0 | yes |
| Strokes L-corners / gaps | 0 / 0 | yes |
| Staircase, all named shapes | 0.96 to 1.0 | yes |
| Boundary distance | 0.19 to 0.32 block | yes |
| IoU | Pepper 0.988, clouds 0.955 / 0.917 / 0.907, bandana 0.943, others 0.63 to 0.83 | partly |
| Colours used by 3 px or fewer, in the visible background | 1 (was 15 in the composite) | yes |
| Single-pixel specks, visible background | 652 (was 1465 in round 1) | see notes |

Round 3 rules: arches rebuilt symmetric from the painting's openings (6 arches) and the deck
as continuous rows; railing balusters as 1 px bars at the painted bar centres (48 bars), only
where the painting has a bar; coat checker zones closed, filled and island-free; spire taper
monotone; bird as a 1 px pixel-perfect polyline; halo rule for sails; 1 px nub rule in sky,
clouds, city, water, pavement, stone, foliage; water, foliage and city reduced to the shades
covering 92 to 93 % of their pixels; straight bodies (bin, left lamp post) column-uniform;
windows on facades, the tower and boats kept as their own cells; stricter specks in pavement,
water, sky and clouds; colours used 3 times or fewer snap to their material ramp.


| Gate | Result | Pass |
|---|---|---|
| Off-palette / mixels | 0 / 0 | yes |
| Form whole picture / my region | 2.42 / 7.75 and 2.35 / 7.09 | yes |
| Checker phase | 1.0 (1569 px) | yes |
| Pepper outline L-corners / gaps / staircase | 0 / 0 / 1.0 | yes |
| Strokes L-corners / gaps | 0 / 0 | yes |
| Boundary distance, named shapes | 0.20 to 0.32 block | yes |
| IoU | Pepper 0.988, cloud 0.954, bandana 0.943, others 0.65 to 0.82 (bounded, see below) | partly |
| Single-pixel specks | 1465 -> 820: 204 foliage or flowers, 580 painted single blocks (windows, sparkles, coat squares: the cell's own top flat colour), 36 checker or line layers; 167 of them sit in the logo, tagline and head boxes | see notes |

Round 2 changes: pinned palette colours (sail shade #d2c9c2, bridge band #a09393, wall mortar
#193059, cloud warm #f1dfc9); stroke ends need two thirds cell coverage (mast starts one cell lower);
dark structure layer for railing, bench and lantern (thin parts one colour, thick parts per-cell);
optimiser never uses neighbour colours except to fix its own mixel and never picks a colour lying
between the cell's two main colours (no grey windows); speck rule (snap to the most common
same-material neighbour colour) followed by a speck-free optimiser pass; rows of small features unify
to their majority colour; mixel repair avoids creating new mixels.

## Round 1 table (kept for the record)


All numbers come from `build_bg.py` (writes `qa_bg.json`) and `grid.py`, measured with `qa.py`.
Result: `result_bg_320.png` (320x240, 128 colours used, every cell owned).

## Final gate table

| Gate | Threshold | Result | Pass |
|---|---|---|---|
| Grid alignment, edge weighted, whole picture | about 0.9 | 0.953 (uniform 7.5 grid: 0.441) | yes |
| Grid alignment per 8x8 cell region (regions with 40+ strong edges) | each about 0.9 | 727 of 860 regions at 0.9 or more, 838 at 0.8 or more, median 0.984, worst 0.629 | partly |
| Off-palette pixels | 0 | 0 | yes |
| Mixels | 0 | 0 | yes |
| Form, 5x5 luma, whole picture (per refined cell) | mean < 3, p95 < 8 | 2.10 / 6.48 | yes |
| Form, my final region (logo, tagline boxes, head box excluded) | mean < 3, p95 < 8 | 2.02 / 6.11 | yes |
| Checker phase (pairs with 8+ checker pixels) | 1.0 | 1.0 (1573 checker pixels; coat 935) | yes |
| Pepper outline (1 px): L-corner doubles / gaps / endpoints | 0 / 0 / 2 (it meets the image border) | 0 / 0 / 2 | yes |
| Pepper outline staircase regularity | 0.9 | 1.000 (67 windows) | yes |
| Masts and thin strokes (1 px): L-corners / gaps | 0 / 0 | 0 / 0 | yes |
| Staircase regularity of named shapes | 0.9 | 0.961 to 1.0 (see below; small shapes have few windows) | yes |
| Geometry boundary distance, every named shape | < 0.35 block | 0.216 to 0.321 | yes |
| Geometry IoU, every named shape | 0.92 | 0.988 Pepper, 0.948 cloud, 0.943 bandana; 0.63 to 0.82 for small or thin shapes | partly |

Informative: 1465 isolated pixels (single specks); the painting itself has many (flowers, windows, sparkles). The form check against the UNIFORM grid (not asked for) gives 3.37 / 10.8, which shows how much the local grid helps.

### Geometry per named shape (uniform re-upscale, as the game shows it)

The IoU gate cannot be met by any binary 320x240 picture for shapes only 4 to 10 cells across: the
best possible rasterisation (coverage of the painting's own mask >= 0.5 per cell, the "oracle") is
given for comparison. The result sits within 0.01 to 0.06 of that bound.

| Shape | IoU | Oracle IoU (uniform cells) | Boundary distance (blocks) | Staircase |
|---|---|---|---|---|
| Pepper silhouette | 0.988 | n/a | 0.321 | 0.961 (51 windows) |
| cloud_left | 0.948 | 0.960 | 0.216 | 1.0 |
| bandana | 0.943 | 0.948 | 0.244 | 1.0 |
| bench | 0.823 | 0.782 | 0.258 | 1.0 |
| lantern_glass | 0.786 | 0.814 | 0.244 | 1.0 |
| sail_right | 0.761 | 0.836 | 0.255 | 1.0 |
| railing | 0.751 | 0.787 | 0.271 | 1.0 |
| lantern_frame | 0.735 | 0.793 | 0.291 | 1.0 |
| sail_left | 0.725 | 0.751 | 0.246 | 1.0 |
| bridge_stone | 0.634 | 0.717 | 0.264 | 1.0 |

Source masks are colour classes of the painting inside a box (cream, glow, dark, stone, pink),
saved with the 320 masks in `qa_masks/`.

### Grid verification regions below 0.9 (133 of 860)

| Area | Regions below 0.9 | All regions with 40+ edges |
|---|---|---|
| Background (city, water, boats, sky, park right, pavement) | 55 | 373 |
| Logo and tagline (other track) | 38 | 223 |
| Pepper body and left park | 25 | 185 |
| "Press any key" box (other track) | 9 | 48 |
| Pepper head (other track) | 6 | 31 |

The 22 regions below 0.8 (row, column of the 8x8 region; score): logo rows 3 to 4 (0.63 to 0.78),
the boats and bridge band rows 17 to 18 (0.73 to 0.80), the press-key box row 25 (0.65 to 0.76),
Pepper's eye (14,13: 0.75), sky and tree corner (0,16: 0.73; 5,11: 0.72), right park (14,38: 0.76),
(20,14: 0.79). Causes: detail thinner than a block (text strokes, masts, rigging, window glints),
half-size blocks, and the logo dither that slips half a block. Line positions move 1.13 px on
average (95 % within 2.5 px, never more than 4 px) from k * 7.5.

## Iterations

| # | Change | Form mean / p95 | Mixels | Checker | Other |
|---|---|---|---|---|---|
| 0 | Uniform grid (reference) | n/a | n/a | n/a | alignment 0.441 |
| 1 | Local grid (DP, +-3 px), 64 colour material palette, weighted vote, stripe based thin features | 2.73 / 8.55 | 2751 | 0.53 | 6438 thin cells, mostly false (anti-aliasing bands) |
| 2 | Palette 96, anti-aliasing bands rejected, mixel repair | 3.00 / 9.35 | 96 | 0.55 | masts still mixed colours |
| 3 | Form-aware coordinate descent over colours present in each cell | 1.97 / 6.32 | 32 | 0.50 | chose blend colours in places (bridge windows grey) |
| 4 | Palette 128 with protected stroke colours; candidates must occur FLAT in the cell; ridge based stroke layer (masts as single colour 1 px lines) | 2.20 / 6.91 | 26 | 0.50 | masts clean |
| 5 | Pepper silhouette shape layer with 1 px pixel-perfect outline; rule checker in coat and logo; boundary length term; bands of 3+ px are not mixels | 2.24 / 7.05 | 16 | 1.00 | hull notches gone |
| 6 | Looser grid (+-4 px, finer levels), border mixels, staircase regulariser, stroke gap joins, no doubled strokes or spurs | 2.10 / 6.48 | 0 | 1.00 | alignment 0.953, outline staircase 1.0 |
