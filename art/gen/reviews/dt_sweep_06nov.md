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
