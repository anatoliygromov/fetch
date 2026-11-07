# City Park hollow log: Pepper crawls inside (7 Nov, round 2)

Owner, 7 Nov: "isnt hollow wood suppose to make the dog climb inside? it looks like shes just crawling on the side".

Before, the log was one picture drawn before Pepper, so she crawled in front of it. Now she goes into the dark open end on the left, the bark swallows her completely, and her nose comes out from behind the closed right end.

Round 1 (two arched mouths seen front-on) read as a little house with two doorways and is replaced. Round 2 keeps the original 3/4 log as it was and makes it longer.

## The art (no credits, no generator)

`tools/build_cp_hollowlog_layers.py` builds both layers from `riverwalk/art/scene/park_hollowlog.png`. The original file is kept and is not redrawn: the 3/4 view, the open left end (an ellipse showing the dark inside), the bark body running right, and the closed, rounded right end.

- **Longer log.** 30 columns are inserted after column 26: 74 x 27 in all, for the 72 px box plus its 1 px ink on each side.
  - The new columns are the log's own middle bark. The lit top band (rows 0-7, no moss) comes from columns 21-26. The grain and the shaded underside (rows 8-26) come from columns 18-36.
  - Each band runs in its own order, forwards and backwards, so the grain does not repeat at one period.
  - Rows are never moved, so the ink line on top, the shell and the bottom ink stay exactly as before.
  - 12 hand edits, listed with reasons in the script: lone pixels and one short streak that asset_qa flagged in the inserted columns.
  - Review fix (round 1 review): columns 36-51 of the insert mirrored around x 43.5, making a symmetric butterfly of dark strokes. Fixed in the script, so `--check` still holds:
    - the right-hand row 8 stroke is cut to a dash (x 49-51 painted with the row's lit grain);
    - a knot is added in the bark at x 44-47, rows 12-16: a dark core, a darker ring and a lit lower lip.
- **FRONT** (`park_hollowlog_front.png`): the longer log with only the dark inside of the left ellipse taken out (its dark pixels, flood-filled from the middle of the mouth).
- **BACK** (`park_hollowlog_back.png`): that dark inside, the same pixels, plus a slightly darker tunnel tone (35, 20, 16) behind the bark, where her body is while she is in the log.
- Front over back is exactly the longer log. `--check` fails if the files on disk differ from what the script builds.
- `.aseprite` sources are in `art/source/park_hollowlog/`.

## Draw order

- `riverwalk/scene.lua`: the back layer is drawn in the play pass, before Pepper.
- The front layer is drawn after Pepper (`Sc.drawPieceFront`) only while she is crouched under the shell with her sprite over the log. Otherwise it is drawn before her, as before, so nothing covers her when she stands beside the log or on top of it (BIBLE 1). Being hidden inside the log is the owner's 7 Nov ask.
- `riverwalk/stage.lua`: one line, `Sc.drawPieceFront(self, cam)`, right after Pepper and the ball she carries. It comes before the bikes, so bikes still ride in front of everything. This line is in its own commit.
- `riverwalk/setpieces.lua`: passes the stage on to `Sc.drawPieceArt` (one argument).

## Map change (both `maps/citypark_tall.tmx` and `maps/citypark.tmx`, re-exported to `riverwalk/level/tiled/`)

| What | Before | After |
| --- | --- | --- |
| Hollow log box (solid shell and piece) | x 1564-1606 (42 px) | x 1553-1625 (72 px), same y, thickness and crawl gap (19 px) |
| Gold bone (secret) | x 1585 | x 1589, the log's centre |
| HOLLOW LOG secret zone | x 1570-1600 | x 1574-1604, inside the log |
| Checkpoint lamp | x 1624 | x 1642 |
| Magpie perch on that lamp | x 1624 | x 1642 (moved with its lamp) |
| Path bone right of the lamp | x 1648 | x 1656 |
| LEAVES pile in front of the log | x 1516-1560 | x 1505-1549 (11 px left) |

- **Why the lamp moved.** Pepper respawns standing at the lamp. With the lamp at 1624 her box (1607-1641) would be inside the longer log's shell.
- **Why the path bone moved.** The lamp post art now spans 1635-1648, and the bone's art (1643-1653) touched it by 6 px. Nudged 8 px right, the bone (1651-1661) clears the post by 3 px.
- **Why the left end stops at 1553.** The tests' walk and crawl checks start Pepper at 1535 (her box reaches 1552).
- `relx`/`rely` are kept (the piece's `rely.foot` = 26). The objects keep their ids.
- `docs/citypark_tall_beatsheet.md` lists the lamp at 1642. `tools/draw_routes.py` has the bone at 1589.

- **Leaf pile.** The review asked for a 6 px move so the ring has air. At 6 px (1510-1554) the pile's art still touched the ring, so I moved it 11 px instead (1505-1549). That leaves 3 px of air, the same gap the old log had (pile end 1560, log 1563). The two path bones under the pile (1530, 1546) stay covered, as before.
- **Magpie perch (optional review item, not done).** I tried moving the perch 4 px left (1638). Its ball then drops at x 1627 and rests on the log's top end instead of the path, which failed the tall City Park's perch 7 check ("the ball lands on y 328"). The perch stays at 1642.

### Test changes (`riverwalk/tests_citypark_tall.lua`)

- Magpie perch 7 (on the moved lamp): the bark spot was x 1560 on the path, which is now under the shell. It now barks from the log's top (x 1580, y 302), and the ball still lands on the path (x 1631).

### Test changes (`riverwalk/tests_citypark.lua`, flat City Park)

- The gold bone check is now `bn.x == 1589`.
- Magpie perch 6 (on the moved lamp): the test now barks from the log's top (x 1580, 62 px off) instead of the path at 1545, which is now under the shell.
  - In the flat level, a bark from past the log (right side) makes the magpie drop the ball on the oak's low branch, 80 px up.
  - From the left path, the walk stops at 1536, which is 106 px from the perch: out of bark range (95).
  - So in the flat City Park, perch 6 is now barked at from on top of the log. The tall City Park, the game's City Park, passes its perch checks unchanged.

## The gold bone

It lies behind the bark at the log's centre. Both layers hide it from outside. She takes it as she crawls through (her box reaches it at about x 1568), so it is never seen.

## Frames (tall City Park, camera x 1440, look on, no HUD; made with `LOOK_CRAWL` in `riverwalk/tests_look.lua`)

| Frame | Pepper x | 1x | 3x |
| --- | --- | --- | --- |
| approaching | 1520 | `01_approach_1x.png` | `01_approach_3x.png` |
| half inside (her rear in the open end) | 1560 | `02_half_inside_1x.png` | `02_half_inside_3x.png` |
| fully inside (swallowed) | 1596 | `03_inside_1x.png` | `03_inside_3x.png` |
| coming out, nose first, from behind the right end | 1630 | `04_coming_out_1x.png` | `04_coming_out_3x.png` |

- `before_after.png`: the same four moments on main (left) and on this branch (right), at 3x.
- Greyscale:
  - `03_inside_grey_*.png`: the inside frame, where she is fully hidden.
  - `02_half_inside_grey_*.png`: her rear in the mouth. Her body (luma about 58) reads against the inside (34) with her black outline.
- `art_6x.png`: old, back, front, and back plus front.

Her crawl sprite is 59 px. The log hides all of her only between x 1595 and 1597 (a moment at crawl speed). Before that her rear shows in the open end; after it her nose shows past the right end. A longer log needs more room: the left end is held at 1553 by the tests' start spot and the path bone at 1546.

## Checks (each with its own XDG_DATA_HOME, xvfb-run -a, SDL_AUDIODRIVER=dummy)

Rerun after the review fix: both physics runs, both qa runs, check_pepper and check_tiled, with the same results as below. check_flow, the `--test` tour and check_curve are from round 2, before the leaf pile move and the knot.

- `love riverwalk --level citypark --physics`: 85 of 85
  - hollow log: stops a walk (x 1536)
  - a held jump lands on top (y 158)
  - crawl through it (x 1635)
  - secret HOLLOW LOG counted with the gold bone taken
  - magpie perch 6: the ball rests on the path (x 1631)
- `love riverwalk --level citypark_tall --physics`: 97 of 97, including magpie perch 7 from the log's top
- `love riverwalk --level citypark_tall --test`: the screenshot tour ran through, exit 0
- `--qa`: citypark_tall 12780 runs, 0 problems; citypark 7883 runs, 0 problems
- `tools/check_flow.sh`: 125 of 125
- `tools/check_tiled.sh`: TILED CHECK PASSED (exports up to date, drag-safe, round trip)
- `tools/check_pepper.sh`: PEPPER UNCHANGED (3908 steps identical)
- `asset_qa --file ... --layer play --level cp`:
  - back PASS
  - back plus front PASS
  - the original PASS
  - The front alone fails only "outline": the edge of the open end is the original's light ring against the hole. The front is always drawn over the back, which fills that hole with the original's dark pixels.
- `python3 -I tools/build_cp_hollowlog_layers.py --check`: OK

## check_curve (order riverwalk, citypark_tall, downtown_tall, rooftops, soder, night; 10 seeds x 8 personas)

| | main (before) | this branch (after) |
| --- | --- | --- |
| City Park (tall) DI v2, kids | 12.6 | 12.9 |
| City Park (tall) DI v2, parents | 14.6 | 14.8 |
| City Park (tall) retro | 6.4 | 6.4 |
| City Park (tall) worst spot | 2 Bench and hedge (29%) | 2 Bench and hedge (28%) |
| City Park (tall) Elsa clears / lost runs | 100% / 1.2% | 100% / 1.2% |
| City Park (tall) perfect clear (lab) | 39.1 s | 39.1 s |
| T1 sawtooth / T2 spot / T3 Elsa / T4 lost | PASS / PASS / PASS / PASS | PASS / PASS / PASS / PASS |

Every other level is identical before and after.
