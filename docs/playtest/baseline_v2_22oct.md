# FETCH! playtest lab: baseline v2, 22 Oct (round1 as it is)

The baseline the level fixes (r6/levels, r6/engine) will be measured against: three level orders, each played in
**whole-game mode** by all eight personas, **10 seeds** per persona (80 playthroughs per order; 1,360 level runs in
all), on `round1` with no level or engine change. Lab: branch `r6/lab` (recovery v2, whole-game mode, DI v2, the
acceptance test). Method: `docs/playtest/method.md`. Re-run any order with `tools/check_curve.py` (below).

Why 10 seeds and not 20: the machine has 2 cores; a level run takes about 1 s of wall time at 4 parallel jobs, so 20
seeds of the three orders is about 45 minutes. 10 seeds keeps the three orders in about 25 minutes. The check
defaults to 20 (`--seeds 20`); runs on disk are reused, so `--seeds 20` on the same `--out` only adds seeds 11 to 20.

## The answer in short

- **No order passes.** Every order fails T1 (sawtooth) for kids and parents, and T4 (lost runs) on one or two
  levels. The **tall order** (River Walk, City Park tall, Downtown tall, Rooftops, Soder Hill, Night Harbour) is by far
  the closest: Elsa clears every level in 80% or more of her playthroughs (T3 passes), and its only spike is
  Downtown (tall) (kids 23, parents 32, against 14 and 13 for Rooftops after it).
- **City Park and Downtown are the two spikes** of the current and the new order (kids 54 to 56 and 35 to 42,
  parents 41 to 47 and 42 to 52), and everything after them is gentler (Rooftops, Soder Hill and Night Harbour
  9 to 23). Elsa clears City Park in 17 to 29% of her playthroughs.
- **City Park (tall) after River Walk is gentle** (kids 14, parents 22, Elsa 100%): on 22 Oct the tall park was hard
  mainly because nobody had found the held jump yet; played second, River Walk has taught it. The same holds for
  Downtown (tall) against Downtown in the tall order (23 / 32 against 42 / 52).
- **The end of every order is flat**: Rooftops, Soder Hill and Night Harbour sit at 7 to 23 for every group, so no
  order climbs (T1 (b)). The finale is easier than the middle.
- **Spot shares (T2)** fail only where few failures fall: River Walk screen 3 (42% of 40 failures, current order) and
  Rooftops screen 9 (42% of 144). City Park, Downtown and Night Harbour spread their failures (21 to 28%).

## Lost runs: before and after

| level | 22 Oct report (v1, 20 seeds, single level) | v1 re-run today (5 seeds, single level) | v2 baseline (10 seeds, whole-game, all orders) |
|---|---|---|---|
| City Park | 49 of 160 (31%) | 9 of 40 (22%) | 9 of 160 (5.6%) |
| City Park (tall) | 66 of 160 (41%) | 16 of 40 (40%) | 6 of 80 (7.5%) |
| River Walk | 5 of 160 (3%) | 1 of 40 (2%) | 0 of 240 (0%) |
| Downtown | 83 of 160 (52%) | 21 of 40 (52%) | 14 of 160 (8.8%) |
| Downtown (tall) | 101 of 160 (63%) | 27 of 40 (68%) | 0 of 80 (0%) |
| Rooftops | 54 of 160 (34%) | 10 of 40 (25%) | 2 of 160 (1.2%) |
| Soder Hill | 34 of 160 (21%) | 9 of 40 (22%) | 0 of 240 (0%) |
| Night Harbour | 133 of 160 (83%) | 34 of 40 (85%) | 0 of 240 (0%) |
| all | 525 of 1,280 (41%) | 127 of 320 (40%) | 31 of 1,360 (2.3%) |

The target (under 5% on every level) is met on six of eight levels. Still over: **Downtown** (8.8%: the parasol
hop at the cafe terrace, x 576 to 611 y 80, and x 1513 to 1514 at y 108 and 184), **City Park (tall)** (7.5%) and
**City Park** (5.6%: the hedge, x 609, the goose lawn, x 954, and the ball pick-up, x 247). In those runs the clean autopilot, started from
where recovery put Pepper, fails the same precision move again (a standing start where the clean run had speed).
Lost runs are left out of the DI; they are 5 to 12% of one level's runs, so those DIs are a little low.

## Results per order

DI v2 per group (higher is harder), DI v1 beside it, the learning seconds (median trying time per run, by group),
the worst spot and its share of the level's failures (all personas), Elsa's clear rate, the clear rate per group,
and the lost runs. Charts: `/home/claude/out/r6-lab/curve_current.png`, `curve_new.png`, `curve_tall.png` (DI along
the order, v2 solid and v1 dashed; spot shares and Elsa's clears) and `baseline_v2_orders.png` (the three orders side
by side). Raw results: `/home/claude/out/r6-lab/curve_<name>/runs/` and `curve.json`.

### current: City Park > Downtown > River Walk > Soder Hill > Night Harbour

| # | Level | DI v2 kids / parents / retro | DI v1 kids / parents / retro | learning s k / p / r | worst spot (share of failures) | Elsa clears | clear % k / p / r | lost runs |
|---|---|---|---|---|---|---|---|---|
| 1 | City Park | 54 / 47 / 14 | 56 / 47 / 15 | 17 / 0 / 5 | 4 Leaf cart (27%, 415 failures) | 29% | 72 / 70 / 100 | 6.2% (5 of 80) |
| 2 | Downtown | 35 / 42 / 19 | 35 / 42 / 19 | 0 / 0 / 0 | 2 Cafe terrace (27%, 395 failures) | 60% | 87 / 70 / 100 | 12.5% (10 of 80) |
| 3 | River Walk | 5 / 6 / 1 | 5 / 6 / 1 | 0 / 0 / 0 | screen 3 (42%, 40 failures) | 100% | 100 / 100 / 100 | 0.0% (0 of 80) |
| 4 | Soder Hill | 14 / 12 / 8 | 14 / 12 / 8 | 0 / 0 / 0 | 9 Cafe tables (75%, 4 failures) | 100% | 100 / 100 / 100 | 0.0% (0 of 80) |
| 5 | Night Harbour | 15 / 21 / 9 | 15 / 21 / 9 | 11 / 0 / 2 | 13 The slipway (24%, 207 failures) | 90% | 97 / 90 / 100 | 0.0% (0 of 80) |

- sawtooth kids: FAIL: spike: City Park (54) > next two max (35) + 8; spike: Downtown (35) > next two max (14) + 8; does not climb: second half 15 < first half 44; last level (15) easier than the first (54)
- sawtooth parents: FAIL: spike: Downtown (42) > next two max (12) + 8; does not climb: second half 17 < first half 44; last level (21) easier than the first (47)
- sawtooth retro: FAIL: spike: Downtown (19) > next two max (8) + 8; does not climb: second half 9 < first half 16; last level (9) easier than the first (14) (reported, not judged)
- targets: T1 sawtooth FAIL, T2 spot share FAIL, T3 Elsa clears FAIL, T4 lost runs FAIL

### new: River Walk > City Park > Downtown > Rooftops > Soder Hill > Night Harbour

| # | Level | DI v2 kids / parents / retro | DI v1 kids / parents / retro | learning s k / p / r | worst spot (share of failures) | Elsa clears | clear % k / p / r | lost runs |
|---|---|---|---|---|---|---|---|---|
| 1 | River Walk | 9 / 7 / 2 | 10 / 6 / 4 | 13 / 0 / 4 | screen 7 (29%, 77 failures) | 90% | 97 / 100 / 100 | 0.0% (0 of 80) |
| 2 | City Park | 56 / 41 / 12 | 56 / 41 / 12 | 6 / 0 / 2 | 4 Leaf cart (21%, 500 failures) | 17% | 69 / 65 / 100 | 5.0% (4 of 80) |
| 3 | Downtown | 42 / 52 / 16 | 42 / 52 / 16 | 0 / 0 / 0 | 2 Cafe terrace (23%, 506 failures) | 50% | 83 / 60 / 100 | 5.0% (4 of 80) |
| 4 | Rooftops | 14 / 13 / 4 | 14 / 13 / 4 | 0 / 0 / 0 | screen 9 (42%, 144 failures) | 100% | 100 / 100 / 100 | 1.2% (1 of 80) |
| 5 | Soder Hill | 10 / 7 / 7 | 10 / 7 / 7 | 0 / 0 / 0 | 16 The end (100%, 1 failures) | 100% | 100 / 100 / 100 | 0.0% (0 of 80) |
| 6 | Night Harbour | 16 / 23 / 8 | 16 / 23 / 8 | 8 / 0 / 2 | 13 The slipway (26%, 234 failures) | 100% | 100 / 85 / 100 | 0.0% (0 of 80) |

- sawtooth kids: FAIL: spike: City Park (56) > next two max (42) + 8; spike: Downtown (42) > next two max (14) + 8; does not climb: second half 13 < first half 36
- sawtooth parents: FAIL: spike: Downtown (52) > next two max (13) + 8; does not climb: second half 15 < first half 33
- sawtooth retro: FAIL: spike: Downtown (16) > next two max (7) + 8; does not climb: second half 6 < first half 10 (reported, not judged)
- targets: T1 sawtooth FAIL, T2 spot share FAIL, T3 Elsa clears FAIL, T4 lost runs FAIL

### tall: River Walk > City Park (tall) > Downtown (tall) > Rooftops > Soder Hill > Night Harbour

| # | Level | DI v2 kids / parents / retro | DI v1 kids / parents / retro | learning s k / p / r | worst spot (share of failures) | Elsa clears | clear % k / p / r | lost runs |
|---|---|---|---|---|---|---|---|---|
| 1 | River Walk | 9 / 7 / 2 | 10 / 6 / 4 | 13 / 0 / 4 | screen 7 (29%, 77 failures) | 90% | 97 / 100 / 100 | 0.0% (0 of 80) |
| 2 | City Park (tall) | 14 / 22 / 6 | 15 / 22 / 7 | 6 / 0 / 3 | 2 Bench and hedge (28%, 211 failures) | 100% | 100 / 85 / 100 | 7.5% (6 of 80) |
| 3 | Downtown (tall) | 23 / 32 / 9 | 23 / 32 / 9 | 0 / 0 / 0 | 5 The plaza (23%, 511 failures) | 80% | 93 / 70 / 100 | 0.0% (0 of 80) |
| 4 | Rooftops | 14 / 13 / 4 | 14 / 13 / 4 | 0 / 0 / 0 | screen 9 (42%, 144 failures) | 100% | 100 / 100 / 100 | 1.2% (1 of 80) |
| 5 | Soder Hill | 10 / 7 / 7 | 10 / 7 / 7 | 0 / 0 / 0 | 16 The end (100%, 1 failures) | 100% | 100 / 100 / 100 | 0.0% (0 of 80) |
| 6 | Night Harbour | 16 / 23 / 8 | 16 / 23 / 8 | 8 / 0 / 2 | 13 The slipway (28%, 226 failures) | 100% | 100 / 85 / 100 | 0.0% (0 of 80) |

- sawtooth kids: FAIL: spike: Downtown (tall) (23) > next two max (14) + 8; does not climb: second half 13 < first half 15
- sawtooth parents: FAIL: spike: Downtown (tall) (32) > next two max (13) + 8; does not climb: second half 15 < first half 20
- sawtooth retro: PASS (reported, not judged)
- targets: T1 sawtooth FAIL, T2 spot share FAIL, T3 Elsa clears PASS, T4 lost runs FAIL

## Reading the numbers

- **DI v2 against DI v1.** In whole-game mode the two are within 2 points everywhere: a control is found once per
  playthrough, so the learning cost is small after level 1 (kids 6 to 17 s on a level that brings a new
  control, sniff on Night Harbour included; parents 0: they read the hints). DI v2 matters most for comparing a level played first with the same
  level later; the learning seconds column shows where the cost lands.
- **Soder Hill** has almost no failures (1 to 4 per order: the barrels cost hearts, the autopilot jumps on), so its
  "worst spot" share is noise; T2 does not judge levels with fewer than 20 failures. Its DI comes from hearts per
  minute.
- **River Walk is level 1 in the new and tall orders**, so the two tables share the same River Walk runs (same seeds,
  nothing carried in). Rooftops and Soder Hill come out the same in both because the controls known by then are
  the same; lives carried in rarely matter.
- **What a fix should move**: for the new order, City Park (kids 56, Elsa 17%) and Downtown (parents 52) down by
  about 30 points, then the finale up (Night Harbour or Rooftops above the middle); for the tall order, Downtown
  (tall) down by about 10 for kids and 20 for parents.

## How to run the check

```
python3 tools/check_curve.py --name new --order riverwalk,citypark,downtown,rooftops,soder,night --seeds 20
python3 tools/check_curve.py --name tall --order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night
python3 tools/check_curve.py --name current --order citypark,downtown,riverwalk,soder,night
```

Each run writes `/home/claude/out/r6-lab/curve_<name>/` (runs, `curve.json`, `curve_<name>.png`) and prints the table
above; exit code 0 only when T1 to T4 pass. After a level change, use a fresh `--out` (or delete the changed
level's runs and its `perfect/` file): runs on disk are reused. `--analyse-only` re-reads the runs without playing.
The targets: T1 sawtooth on DI v2 for kids and parents (no level more than 8 points above the hardest of the next
two; second half at least as hard as the first, last level at least as hard as the first), T2 no spot over 35% of a
level's failures (levels with 20 failures or more), T3 Elsa clears every level in at least 50% of her playthroughs,
T4 under 5% lost runs per level. The game checks after the lab work: `tools/check_pepper.sh` PEPPER UNCHANGED
(4591 steps), `tools/check_flow.sh` 103 of 103 passed, `--auto` on City Park 44.2 s (unchanged).
