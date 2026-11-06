# Downtown tall sweep, branch night/06nov-dt (2852d9c): screen by screen

# Round 1 (reviewer, 6-7 Nov night)

Rendered `LOOK_SWEEP=1 LOOK_STEP=320`, 33 screens at tiers y 240 (street), 120, 0, plus the flat `downtown`
(11 screens). Looked at as 2x contact sheets in colour and greyscale, suspect spots at 4-8x. PASS means I would
show the screen to the owner as finished. Camera x, y are the sweep's.

## The base review's Downtown FAIL list, item by item
| Base item | Now |
| --- | --- |
| mini houses x 0-960, x 2560-3520 (covered: scale-break track) | NOT FIXED. `town_house1-3` (58 x 126, door about 20 px) still stand on the back layer at scroll 1.0 on both sides of the true-scale stretch (x 1100-2740). Decision 2a fixed the doll houses inside the plaza bays only |
| facade lift (covered) | FIXED: 37 styled fronts, crisp, true scale |
| floating high road (covered) | FIXED: consoles, pilasters, French windows, footbridge on piers |
| tram shelter wireframe (covered) | FIXED: green iron shelter |
| fountain basin (covered) | NOT FIXED: granite posts added, the basin is still a pit into deep water |
| DT1 comb ledges on blank plaster (x 1920, 2240) | FIXED: a window door or French window behind each ledge, consoles under |
| DT2 parasols in the flood (x 2880) | NOT FIXED: toy boats (52 px) added, drawn inside the water with no waterline |
| DT3 crate tower below the street (x 2560) | FIXED: the stack stands on a granite quay block |
| DT4 street lamp on the gallery (x 1600) | FIXED: wall lantern on a bracket |
| DT5 kerb end at the right edge (x 3200) | NOT FIXED (maker says so; low priority) |

## Screens
| cam x | y 240 (street) | y 120 | y 0 |
| --- | --- | --- | --- |
| 0 | FAIL: true-scale corner house (door 95 px) beside mini houses (door 45 px) with their roofs and sky on the street screen | FAIL: same seam at x 140 | FAIL: same |
| 320 | FAIL: mini houses, roofs on the street screen | FAIL: mini houses | FAIL: mini roofs (far city and sky behind them are fine) |
| 640 | FAIL: mini houses | FAIL | FAIL |
| 960 | FAIL: mini houses, seam to the true-scale front at x 1100 | FAIL: seam | FAIL |
| 1280 | PASS: statue, loggia on pilasters, balconies on consoles, crates, stall | PASS: arcade, iron balconies, windows crisp | PASS |
| 1600 | FAIL: fountain basin is a pit, jets 1 px dotted; the rest (lantern, balustrade, shop) clean | FAIL (minor): guild pier reads as a chimney stub on the landing; rest PASS | PASS (pier again, small) |
| 1920 | PASS: shelter, shop, planter, awnings, lanterns | PASS: ledges with window doors, cornice awning on irons | PASS |
| 2240 | FAIL: mini house under the footbridge at x 2480-2560; bridge rib 1-2 px reads as a wire at 1x | FAIL: mini house at the right edge beside the pink front | FAIL: mini house roof beside the front at the right edge |
| 2560 | FAIL: boats inside the water, no waterline; mini houses right of x 2830; bridge rib thin | FAIL: mini house at x 2560-2640 one storey tall beside a front whose one window is taller than that storey | FAIL: same seam, the two fronts cut flat at the top beside mini roofs |
| 2880 | FAIL: three toy boats floating in the blue slab | FAIL: mini houses (arch house true scale beside them) | FAIL: mini roofs |
| 3200 | FAIL: mini houses beside the true-scale shelter and Mia; kerb end (DT5) | FAIL: mini houses | FAIL: mini roofs |

The whole true-scale stretch x 1100-2740 passes at every tier except the basin and the pier. Everything outside
it fails on one cause: the quarter-scale houses.

## Flat `downtown` (11 screens, y 0), quick check
Unchanged in kind: the quarter-scale houses carry the plaza balconies (a balcony as wide as its house at x 1600),
the old glass-box shelter at x 1920, the same basin pit. Same FAIL cause as above on every screen with houses
(all but x 1280). The flat level did not get the fronts (PLAZA_FRONTS needs FIRST_FLOOR).

## Layer ladder (greyscale)
PASS on every screen: far city lightest, mini houses and fronts next, Pepper's row darkest. Obstacles outlined,
decoration not. The canal water sits at the mid value; the boats are the same value as the water, which is why
they vanish in grey.

## Top 5 fixes by impact
1. Replace the quarter-scale `town_house1-3` row on x 0-1100 and x 2740-3520 with true-scale fronts (the 37 exist;
   fill the back boxes with them as x 1100-2740 does). Until then every screen outside the middle fails.
2. Boats: true-scale punt (184 px) or a pontoon, cut by a drawn waterline with a wet band; the water as a surface
   band over darker deep water.
3. Basin: a front-on granite kerb at street level with a thin water band behind it; jets 2 px with a splash.
4. Footbridge rib 3 px (dark, mid, light) so the arch reads as iron at 1x.
5. Guild pier: an urn or lion on it, or drop it. Then the kerb end at x 3497.

# Round 2 (reviewer, 6-7 Nov night): fix rounds 1 and 2 (fab6b50)

Re-rendered all 33 screens with the default flag (H.CLOSED_STREET false), the same 33 with LOOK_CLOSED=1, and two
pairs 20 px apart (camera x 400/420 and 3000/3020 at y 240) to measure scroll.

## Scroll, measured
Block-wise best shift between the pairs (20 x 20 blocks, rows 0-200): the small-house row at x 0-1100 and
x 2816-3520 shifts 10 px for 20 px of camera on every block of the row (roofs, storeys, doors): scroll 0.5, the
mid layer. The street, kerb, props and the true-scale fronts shift 20 (scroll 1.0). Round 1's line "quarter-scale
town_house1-3 on the back layer at scroll 1.0" was wrong; the maker is right: it is the mid-layer town row at
scroll 0.5 (23 px/m, a 45 px door is 2 m there). The doll houses of decision 2a stood only on the plaza and are
gone. Correction noted here and in round 1's file.

## Do the open squares read as distance across a square?
No. At the street tier (y 240) the row's feet land on the pavement's far edge with nothing between: no square
floor, no far kerb, no mid-scale thing standing on the square. Its values sit only one small step lighter than
the true-scale fronts (mid 171 median against back 152). The parallax tells the depth only while the camera
moves; on a still screen a 7 year old sees small houses standing on the pavement beside a door twice their
height. x 0-960 and x 2880-3200 at every tier, and the right edge of x 2240 and x 2560, still read as doll houses
at street depth. The quoins fix the seams, not the depth.

## What would fix it with the spire kept (decision 6a)
1. A square floor: a flat paving band in the mid layer's own value (2 shades, no texture), 24-32 px tall, from
   the pavement's back edge to the row's feet, the row raised to stand on its far edge; a far kerb line and a
   bollard or lamp row at 23 px/m along it. That is what Lion King does: the mid layer never touches the play
   floor.
2. One palette step lighter for the row (the mid ladder row: darkest 105, contrast 85), so it sits a clear step
   behind the fronts in greyscale.
3. Or: H.CLOSED_STREET on with two or three alleys or carriage arches of 60-100 px cut in it where the square,
   the row and the spire show through. The LOOK_CLOSED=1 render reads as a real street at every tier (no scale
   break, walls past the top); the spire is lost, which 6a forbids. Alleys keep both.
Recommendation: 3 if the owner will take alleys; else 1 and 2 together.

## Screens still failing (default flag)
| cam x | y 240 | y 120 | y 0 |
| --- | --- | --- | --- |
| 0, 320, 640, 960 | FAIL: row at street depth | FAIL | FAIL |
| 1280, 1600, 1920 | PASS (basin, urn, lanterns, shelter all closed) | PASS | PASS |
| 2240, 2560 | FAIL: row at street depth at the right edge; bridge, canal, crates PASS | FAIL (right edge) | FAIL (right edge) |
| 2880, 3200 | FAIL: row at street depth; canal, poles, stairs PASS | FAIL | FAIL |

With LOOK_CLOSED=1 every screen passes the scale and float checks; the spire is hidden on all of them.

# Round 3 (reviewer, 6-7 Nov night): fix round 3 (e8b1164), the square floor

Re-rendered x 0, 320, 640, 960, 2240, 2560, 2880, 3200 (and the middle three as a control) at y 240, 120, 0 with
the default flag, 2x colour and grey; `town_square_floor.png` at 5x tiled three times beside the bench;
`asset_qa --layer mid --level dt`: PASS.

| Item | Result | Evidence |
| --- | --- | --- |
| strip crisp | PASS | 64 x 51, flat setts in two shades on straight courses, a far kerb row, 3 px bollards with caps, 21 px (0.9 m at 23 px/m); tiles without a seam |
| still-screen read, x 0-960 | PASS | the row stands on a lit paved square behind a kerb and a bollard row, its feet 30 px above the pavement; roofs are off the street screen; the corner house (true scale) reads as near, the row as across the square |
| still-screen read, x 2240, 2560 | PASS | the square shows between the front's quoin and the bridge pier and behind the far quay; the row no longer touches the street |
| still-screen read, x 2880, 3200 | PASS | square behind the arch house, the shelter and Mia; the row across it |
| layer ladder (grey) | PASS | the row and square are now one clear step lighter than the fronts; play row darkest |
| nothing else changed | PASS | x 1280, 1600, 1920 at all three tiers: 0 pixels differ from the round 2 render |

Round 2's open-square FAIL is closed. No screen fails. Two nits for later, not blockers: the square floor also
shows above the far quay behind the canal at x 2560-3056 (right in kind, a square on the far bank, but it meets
the quay coping with no edge row); the row's doors have no step down to the square (one 1 px darker row under each
door would seat them).
