# Tagline plate: QA gates

## Round 3 (final): symmetric side frames; every round 2 number unchanged except colours = 4 (sky beside the plate ends), form 2.52 / 7.24

## Round 2

| Gate | Result | Pass |
|---|---|---|
| Grid alignment | 0.902 (x 0.834, y 0.932) | pass |
| Plate outer / filled rim / body IoU, bdist | 0.994/0.049, 0.996/0.026, 0.986/0.088 | pass |
| Rim band IoU, bdist | 0.921 / 0.054 | pass (just) |
| Text ink IoU, bdist | 0.878 / 0.061 | IoU fail, bdist pass |
| Lines: L-corners / gaps / corner staircases regular | 0 / 0 / 4 of 4 (both edges, steps of 1, 2 px per row) | pass |
| Colour: off-palette / mixels | 0 / 0, 3 colours | pass |
| Form (5x5 blurred luma) mean / p95 | 2.52 / 7.23 | pass |
| Glyph centres vs painting | mean 0.26, max 0.53 cell (D, g) | max just over 0.5 |
| Word gaps | 6 / 6 / 6 (painted 6.0 / 5.9 / 6.1) | pass |
| Repeated letters identical (e x3, t x2, r x2) | yes | pass |
| Strokes 1 px | yes except the painted 2 px v point | pass |

Round 1 tables follow.

All numbers from `metrics.json` (final run). Region = the 2725 owned cells (`tagline_mask.png`).
Block = 7.5 px.

## Final gate table (iteration 3)

| Gate | Measure | Target | Result | Pass |
|---|---|---|---|---|
| Grid | strong colour changes within 1 px of a refined cell border | about 0.90 | 0.898 (x 0.820, y 0.932, n 11585) | borderline pass |
| Geometry: plate outer silhouette | IoU / mean boundary distance | 0.92 / 0.35 | 0.991 / 0.071 | pass |
| Geometry: rim, filled | IoU / bdist | 0.92 / 0.35 | 0.994 / 0.046 | pass |
| Geometry: body (inside rim) | IoU / bdist | 0.92 / 0.35 | 0.985 / 0.094 | pass |
| Geometry: rim ring (1 block thin) | IoU / bdist | 0.92 / 0.35 | 0.902 / 0.064 | IoU fail, bdist pass |
| Geometry: text ink (all) | IoU / bdist | 0.92 / 0.35 | 0.878 / 0.061 | IoU fail, bdist pass |
| Geometry: words The / City / Dog / Adventurer | IoU | 0.92 | 0.948 / 0.833 / 0.871 / 0.879 | 1 of 4 |
| Lines | L-corner doubles / gaps on the rim | 0 / 0 | 0 / 0 (1 component, no branches) | pass |
| Lines | staircase regularity (4 chamfers) | 0.9 | 1.0 (runs all 1) | pass |
| Colour | off-palette pixels / mixels | 0 / 0 | 0 / 0 (3 colours; text area 2) | pass |
| Pattern | checker phase | n/a | the plate has no dither | n/a |
| Form | 5x5 blur of luma vs painting, per refined cell | mean < 3, p95 < 8 | mean 2.77, p95 9.23 | mean pass, p95 fail |
| Text | repeated letters identical (e x3, t x2, r x2) | yes | yes | pass |
| Text | no 2x2 ink block (stroke 1 px), letter gap constant | yes | yes, gap 1 | pass |
| Text | only cream on navy, no halo | yes | yes | pass |

Why the thin-shape IoU gates fail: the rim ring and the glyph strokes are 1 block wide, so an average
boundary offset of 0.06 block (0.5 px, the bdist we get) already costs about 10 % IoU. The boundary
distance, which does not depend on thickness, passes everywhere with a wide margin.

Why form p95 fails, by zone: plate middle mean 1.8 / p95 2.5; text mean 2.8 / p95 9.0; plate ends
mean 6.0 / p95 18.1. At the ends the painting draws the chamfer rim with overlapping blocks and
mid-blue steps (about twice the light area of a 1 px diagonal); matching it needs 4-connected
steps, which the line gate forbids. In the text the cells the painting covers half (cut corners,
the A shoulders, the y and g tails, the 9 px arms of v on 6.6 px columns) must go one way or the
other. For reference, the best any 3-colour per-cell choice could do on this grid, ignoring all
shape rules, is mean 1.8 / p95 4.4.

## Iterations

| # | Change | Grid all (x / y) | Outer IoU / bd | Fill IoU / bd | Body IoU / bd | Ring IoU / bd | Text IoU / bd | Lines L / gaps / reg | Off-pal / mixels | Form mean / p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | equal glyph columns, row/col knots at painted edges, symmetric 45 degree chamfer 4, line fitted (RMS, centred: space 6, start 161), outline owned unless the painting shows city/sky there (a navy-only rule left holes at the bottom chamfers in a dry run) | 0.858 (0.777 / 0.894) | 0.987 / 0.115 | 0.988 / 0.092 | 0.973 / 0.175 | 0.824 / 0.124 | 0.809 / 0.098 | 0 / 0 / 1.0 | 0 / 0 | 3.55 / 12.25 |
| 2 | top and bottom chamfers fitted separately (5 / 4); row borders snapped to edges (x-height top 635); glyph borders snapped to the glyph's own edges when its bitmap is unchanged; plate-end columns snapped | 0.898 (0.820 / 0.932) | 0.991 / 0.071 | 0.994 / 0.046 | 0.985 / 0.094 | 0.902 / 0.064 | 0.876 / 0.061 | 0 / 0 / 1.0 | 0 / 0 | 2.83 / 9.87 |
| 3 | rounded corner profiles and left/right-asymmetric corners evaluated and rejected (below); glyph overrides re-audited on the refined grid: g follows the painting (square bowl corner, 0.72), r overrides dropped (the data gives the same r), A and n kept (stroke rule) | 0.898 (0.820 / 0.932) | 0.991 / 0.071 | 0.994 / 0.046 | 0.985 / 0.094 | 0.902 / 0.064 | 0.878 / 0.061 | 0 / 0 / 1.0 | 0 / 0 | 2.77 / 9.23 |

Corner profiles tried in iteration 3 (top-left / bottom-left, right mirrored unless noted):

| Profile | Fill IoU | Ring IoU | Outer IoU | Form p95 (all / ends) |
|---|---|---|---|---|
| 45 degree 5 / 4 (kept) | 0.9938 | 0.9024 | 0.9913 | 9.23 / 18.08 |
| top-left runs 1,1,2, others 45 degree | 0.9953 | 0.9061 | 0.9924 | 9.34 / 18.14 |
| runs 1,1,2 on both top corners | 0.9964 | 0.9075 | 0.9933 | 9.62 / 18.11 |
| top-left runs 2,1,1, others 45 degree | 0.9947 | 0.9062 | 0.9924 | 9.20 / 18.05 |
| top-left 45 degree 4 | 0.9948 | 0.9015 | 0.9920 | 9.41 / 18.49 |

## Visual check (10x, `cmp_*.png`)
Seen and named in notes.md, "Remaining defects": narrower letters and wider word gaps, 3 px t and
5 px T / v, 2 px y and g tails, thin 1 px chamfer rim against the painting's chunky stepped one, the
top-left chamfer half to one cell inside the painting's, top outline owned only where navy is painted.
No specks, no grey pixels, no notches, no doubled corners, no broken rim.
